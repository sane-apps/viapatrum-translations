#!/usr/bin/env python3
"""Workers AI batch broker: many calls in, few batched requests out.

Owner 2026-10-03: use the Cloudflare grant at full speed. Paid-access models
are capped near 20 direct requests a minute, but the documented batch path
(?queueRequest=true) took 40 Kimi K2.6 requests in one submission and
returned all 40 in ~33 s. Every job on the Mini (translation lanes, doctrine
grading, narration) sends batch-capable model calls here through
llm_bakeoff.cf_call; the broker groups them per model, submits one batch every
FLUSH_S seconds, polls, and hands each caller its own result. Submits and
polls go through llm_bakeoff.rate_acquire, so the broker itself never draws a
429. launchd: com.saneapps.cf-batch-broker (KeepAlive), 127.0.0.1:8799.

  POST /run   {"model": "@cf/...", "payload": {...}}  -> {"result": {...}} | {"error": "..."}
  GET  /stats                                          -> queue and batch counts
"""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_bakeoff as L  # noqa: E402

PORT = int(os.environ.get("CF_BATCH_PORT", "8799"))
ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", L.DEFAULT_ACCOUNT)
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
FLUSH_S = 2.0          # collect for this long, then submit
MAX_ITEMS = 64         # requests per batch
MAX_BYTES = 9_000_000  # Cloudflare caps a batch payload at 10 MB
POLL_S = 4.0
DEADLINE_S = 1500      # a caller waits at most this long

lock = threading.Lock()
queues: dict[str, list] = {}        # model -> [item]
pending: list[dict] = []            # submitted batches awaiting results
stats = {"submitted_batches": 0, "submitted_items": 0, "done_items": 0, "errors": 0}


def _post(model: str, body: dict, timeout: int = 120) -> tuple[int, dict]:
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai/run/{model}?queueRequest=true"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}
    except Exception as e:  # noqa: BLE001
        return -1, {"errors": [{"message": str(e)}]}


def _finish(item: dict, result=None, error: str = "") -> None:
    item["result"], item["error"] = result, error
    item["event"].set()
    with lock:
        stats["done_items" if not error else "errors"] += 1


def flusher() -> None:
    while True:
        time.sleep(FLUSH_S)
        with lock:
            work = {m: q for m, q in queues.items() if q}
        for model, q in work.items():
            with lock:
                batch, size = [], 0
                while q and len(batch) < MAX_ITEMS:
                    n = len(json.dumps(q[0]["payload"]))
                    if batch and size + n > MAX_BYTES:
                        break
                    batch.append(q.pop(0))
                    size += n
            if not batch:
                continue
            L.rate_acquire(model)
            code, res = _post(model, {"requests": [i["payload"] for i in batch]})
            rid = (res.get("result") or {}).get("request_id")
            if code in (200, 202) and rid:
                with lock:
                    pending.append({"model": model, "rid": rid, "items": batch, "t": time.time()})
                    stats["submitted_batches"] += 1
                    stats["submitted_items"] += len(batch)
                continue
            if code == 429:
                L.rate_throttled(model)
            msg = json.dumps(res.get("errors") or res)[:200]
            for it in batch:  # requeue once, then fail so the caller's own retry runs
                if it.get("tries", 0) < 2:
                    it["tries"] = it.get("tries", 0) + 1
                    with lock:
                        queues.setdefault(model, []).append(it)
                else:
                    _finish(it, error=f"batch submit {code}: {msg}")


def poller() -> None:
    while True:
        time.sleep(POLL_S)
        with lock:
            todo = list(pending)
        for b in todo:
            L.rate_acquire(b["model"])
            code, res = _post(b["model"], {"request_id": b["rid"]}, timeout=60)
            r = res.get("result") or {}
            results = r.get("results") if isinstance(r, dict) else None
            if code == 429:
                L.rate_throttled(b["model"])
                continue
            if results is None:
                if time.time() - b["t"] > DEADLINE_S:
                    with lock:
                        pending.remove(b)
                    for it in b["items"]:
                        _finish(it, error="batch timed out")
                continue
            with lock:
                pending.remove(b)
            by_index = {x.get("index"): x for x in results}
            for k, it in enumerate(b["items"]):
                x = by_index.get(k)
                if x and x.get("success", True) and x.get("result") is not None:
                    _finish(it, result=x["result"])
                else:
                    _finish(it, error="batch item failed: " + json.dumps(x)[:200] if x else "batch item missing")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/stats":
            with lock:
                self._send(200, dict(stats, queued={m: len(q) for m, q in queues.items() if q},
                                     pending_batches=len(pending)))
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/run":
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            model, payload = req["model"], req["payload"]
        except (ValueError, KeyError):
            return self._send(400, {"error": "bad request"})
        item = {"payload": payload, "event": threading.Event()}
        with lock:
            queues.setdefault(model, []).append(item)
        if not item["event"].wait(DEADLINE_S + 60):
            return self._send(504, {"error": "broker timeout"})
        self._send(200, {"result": item["result"]} if not item["error"] else {"error": item["error"]})


def main() -> int:
    if not TOKEN:
        print("no CLOUDFLARE_API_TOKEN", file=sys.stderr)
        return 2
    threading.Thread(target=flusher, daemon=True).start()
    threading.Thread(target=poller, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    srv.daemon_threads = True
    print(f"cf batch broker on 127.0.0.1:{PORT}", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
