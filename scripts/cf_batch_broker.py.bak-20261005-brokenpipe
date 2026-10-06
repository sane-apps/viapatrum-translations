#!/usr/bin/env python3
"""Workers AI batch broker: many calls in, few batched requests out.

Owner 2026-10-03: use the Cloudflare grant at full speed. Paid-access models
are capped near 20 direct requests a minute, but the documented batch path
(?queueRequest=true) took 40 Kimi K2.6 requests in one submission and
returned all 40 in ~33 s. Every job on the Mini (translation lanes, doctrine
grading, narration) sends batch-capable model calls here through
llm_bakeoff.cf_call; the broker groups them per model and hands each caller
its own result. Each model gets its own flusher and poller thread, so one
model's submits and polls never wait behind another's. A model's queue is
flushed once its oldest item has waited FLUSH_S, or at once when FLUSH_EARLY
items wait. Submits go through llm_bakeoff.rate_acquire, so the broker itself
never draws a 429 on a submit.

Polls run outside the limiter, at most one per batch every POLL_EVERY_S.
Probe 2026-10-03 (outputs/broker-poll-probe-20261003T151717.json): 231 Kimi
K2.6 polls at ~58/min for 240 s, while live traffic held the 18/min limiter
full, drew zero 429s, so Cloudflare does not charge a poll against the
per-model cap. If a poll ever 429s, that model's polls go back under the
limiter for the life of the process. launchd: com.saneapps.cf-batch-broker
(KeepAlive), 127.0.0.1:8799.

  POST /run   {"model": "@cf/...", "payload": {...}}  -> {"result": {...}} | {"error": "..."}
  GET  /stats                                          -> queue and batch counts, per model
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
FLUSH_S = 8.0          # submit once the oldest queued item has waited this long
FLUSH_EARLY = 10       # ...or at once when this many items wait
MAX_ITEMS = 64         # requests per batch
MAX_BYTES = 9_000_000  # Cloudflare caps a batch payload at 10 MB
POLL_TICK_S = 1.0      # poller wake-up interval
POLL_EVERY_S = 10.0    # at most one poll per batch this often
SUBMIT_RETRY_S = 2.0   # pause after a failed submit before the requeued items go again
DEADLINE_S = 1500      # a caller waits at most this long

lock = threading.Lock()
queues: dict[str, list] = {}        # model -> [item]
pending: list[dict] = []            # submitted batches awaiting results
workers: dict[str, threading.Event] = {}  # model -> flusher wake event
metered_polls: set[str] = set()     # models whose polls drew a 429: poll under the limiter
stats = {"submitted_batches": 0, "submitted_items": 0, "done_items": 0, "errors": 0,
         "polls": 0, "poll_429s": 0}


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


def flush_wait(q: list, now: float) -> float:
    """Seconds until this queue should be flushed; 0 means flush now."""
    if not q:
        return FLUSH_S
    if len(q) >= FLUSH_EARLY:
        return 0.0
    oldest = min(i.get("t", now) for i in q)  # requeued items sit at the back with an old t
    return max(0.0, FLUSH_S - (now - oldest))


def take_batch(q: list) -> list:
    """Pop up to MAX_ITEMS / MAX_BYTES from the front of q. Caller holds lock."""
    batch, size = [], 0
    while q and len(batch) < MAX_ITEMS:
        n = len(json.dumps(q[0]["payload"]))
        if batch and size + n > MAX_BYTES:
            break
        batch.append(q.pop(0))
        size += n
    return batch


def model_stats(now: float) -> dict:
    """Per model: queued items, oldest queued age, pending batches/items, oldest pending age.
    Caller holds lock."""
    out: dict[str, dict] = {}
    for m, q in queues.items():
        if q:
            out.setdefault(m, {})
            out[m]["queued"] = len(q)
            out[m]["oldest_queued_s"] = round(now - min(i.get("t", now) for i in q), 1)
    for b in pending:
        s = out.setdefault(b["model"], {})
        s["pending_batches"] = s.get("pending_batches", 0) + 1
        s["pending_items"] = s.get("pending_items", 0) + len(b["items"])
        s["oldest_pending_s"] = round(max(s.get("oldest_pending_s", 0.0), now - b["t"]), 1)
    for s in out.values():
        for k in ("queued", "pending_batches", "pending_items"):
            s.setdefault(k, 0)
    return out


def enqueue(model: str, item: dict) -> None:
    item.setdefault("t", time.time())
    with lock:
        q = queues.setdefault(model, [])
        q.append(item)
        wake = workers.get(model)
        start = wake is None
        if start:
            wake = workers[model] = threading.Event()
        early = len(q) >= FLUSH_EARLY
    if start:
        threading.Thread(target=flusher, args=(model,), daemon=True, name=f"flush:{model}").start()
        threading.Thread(target=poller, args=(model,), daemon=True, name=f"poll:{model}").start()
    if early:
        wake.set()


def flush_once(model: str) -> bool:
    """Submit one batch for model if one is due. Returns True if it submitted or failed a batch."""
    with lock:
        q = queues.get(model) or []
        if not q or flush_wait(q, time.time()) > 0:
            return False
        batch = take_batch(q)
    if not batch:
        return False
    L.rate_acquire(model)
    code, res = _post(model, {"requests": [i["payload"] for i in batch]})
    rid = (res.get("result") or {}).get("request_id")
    if code in (200, 202) and rid:
        now = time.time()
        with lock:
            pending.append({"model": model, "rid": rid, "items": batch, "t": now,
                            "next_poll": now + POLL_EVERY_S})
            stats["submitted_batches"] += 1
            stats["submitted_items"] += len(batch)
        return True
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
    time.sleep(SUBMIT_RETRY_S)  # requeued items keep their old t, so without this they resubmit at once
    return True


def flusher(model: str) -> None:
    wake = workers[model]
    while True:
        wake.clear()
        with lock:
            wait = flush_wait(queues.get(model) or [], time.time())
        if wait > 0:
            wake.wait(wait)
            continue
        flush_once(model)


def poll_once(b: dict) -> None:
    model = b["model"]
    if model in metered_polls:
        L.rate_acquire(model)
    b["next_poll"] = time.time() + POLL_EVERY_S
    code, res = _post(model, {"request_id": b["rid"]}, timeout=60)
    with lock:
        stats["polls"] += 1
    if code == 429:
        L.rate_throttled(model)
        with lock:
            stats["poll_429s"] += 1
            metered_polls.add(model)
        return
    r = res.get("result") or {}
    results = r.get("results") if isinstance(r, dict) else None
    if results is None:
        if time.time() - b["t"] > DEADLINE_S:
            with lock:
                if b in pending:
                    pending.remove(b)
            for it in b["items"]:
                _finish(it, error="batch timed out")
        return
    with lock:
        if b in pending:
            pending.remove(b)
    by_index = {x.get("index"): x for x in results}
    for k, it in enumerate(b["items"]):
        x = by_index.get(k)
        if x and x.get("success", True) and x.get("result") is not None:
            _finish(it, result=x["result"])
        else:
            _finish(it, error="batch item failed: " + json.dumps(x)[:200] if x else "batch item missing")


def poller(model: str) -> None:
    while True:
        time.sleep(POLL_TICK_S)
        now = time.time()
        with lock:
            due = [b for b in pending if b["model"] == model and b.get("next_poll", 0) <= now]
        for b in due:
            poll_once(b)


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
                body = dict(stats, queued={m: len(q) for m, q in queues.items() if q},
                            pending_batches=len(pending), models=model_stats(time.time()),
                            metered_polls=sorted(metered_polls))
            self._send(200, body)
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
        item = {"payload": payload, "event": threading.Event(), "t": time.time()}
        enqueue(model, item)
        if not item["event"].wait(DEADLINE_S + 60):
            return self._send(504, {"error": "broker timeout"})
        self._send(200, {"result": item["result"]} if not item["error"] else {"error": item["error"]})


def main() -> int:
    if not TOKEN:
        print("no CLOUDFLARE_API_TOKEN", file=sys.stderr)
        return 2
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    srv.daemon_threads = True
    print(f"cf batch broker on 127.0.0.1:{PORT}", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
