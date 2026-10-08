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
import traceback
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
# A model's flusher that has not come round its loop for this long, while
# items wait, is wedged; a queued item this old means nothing drains it (its
# caller gave up long ago and dropped it). One flusher pass takes at most
# rate_acquire's 900 s wait + a 120 s submit, well under this. The watchdog
# first restarts dead threads; if a queue is still stuck, the process exits
# non-zero and launchd (KeepAlive) starts a fresh broker. 2026-10-06: both
# flushers died in the full-disk crash and 139 Kimi items sat queued for 11
# hours while /stats still answered.
STUCK_S = DEADLINE_S + 120
WATCH_S = 30.0         # watchdog interval

lock = threading.Lock()
queues: dict[str, list] = {}        # model -> [item]
pending: list[dict] = []            # submitted batches awaiting results
workers: dict[str, threading.Event] = {}  # model -> flusher wake event
threads: dict[str, list] = {}       # model -> [flusher thread, poller thread]
beats: dict[str, float] = {}        # model -> last time its flusher came round its loop
metered_polls: set[str] = set()     # models whose polls drew a 429: poll under the limiter
stats = {"submitted_batches": 0, "submitted_items": 0, "done_items": 0, "errors": 0,
         "polls": 0, "poll_429s": 0, "thread_restarts": 0, "loop_errors": 0}


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


def _log(msg: str) -> None:
    """Write one log line. The log sits on the same disk as everything else:
    on a full disk the write raises, and that must never kill the thread that
    is logging (2026-10-06 review: a failed print in the error handler killed
    the flusher it was meant to save)."""
    try:
        print(msg, file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass


# Batch body shape per model. The live schema (GET ai/models/schema, 2026-10-07)
# for @cf/openai/gpt-oss-120b and -20b accepts a direct call as Prompt or
# Messages, but its async form is "Responses_Async": {"requests": [{"input",
# "reasoning"}]}. A batch of Messages items fails with 400 "oneOf at '/' not
# met ... 'prompt' ... 'messages'" (fathers-beliefs.log, 51 lines on 10-06), so
# every gpt-oss overflow call fell back to a direct call. Other models take
# the Messages item as is. Results come back in the Responses shape, which
# llm_bakeoff._cf_pick_content already reads.
RESPONSES_BATCH = ("gpt-oss-",)
REASONING_EFFORTS = ("low", "medium", "high")  # gpt-oss: reasoning cannot be disabled


def batch_item(model: str, payload: dict) -> dict:
    """One request of a ?queueRequest=true batch, in the shape this model's
    async schema takes."""
    if not any(k in model for k in RESPONSES_BATCH) or "messages" not in payload:
        return payload
    item = {"input": payload["messages"]}
    effort = payload.get("reasoning_effort")
    if effort in REASONING_EFFORTS:
        item["reasoning"] = {"effort": effort}
    return item


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


def ensure_threads(model: str) -> list[str]:
    """Start the model's flusher and poller if missing or dead. Caller holds
    lock. Returns the names of dead threads it replaced."""
    if model not in workers:
        workers[model] = threading.Event()
    cur = threads.get(model) or [None, None]
    started = []
    for k, (target, kind) in enumerate(((flusher, "flush"), (poller, "poll"))):
        if cur[k] is not None and cur[k].is_alive():
            continue
        if cur[k] is not None:
            stats["thread_restarts"] += 1
            started.append(cur[k].name)
        if kind == "flush":
            beats[model] = time.time()  # a fresh flusher is not wedged
        cur[k] = threading.Thread(target=target, args=(model,), daemon=True, name=f"{kind}:{model}")
        cur[k].start()
    threads[model] = cur
    return started


def dead_threads() -> list[str]:
    """Names of flusher/poller threads that have stopped. Caller holds lock."""
    return [t.name for ts in threads.values() for t in ts if t is not None and not t.is_alive()]


def enqueue(model: str, item: dict) -> None:
    item.setdefault("t", time.time())
    with lock:
        q = queues.setdefault(model, [])
        q.append(item)
        restarted = ensure_threads(model)  # a dead flusher is replaced on the next call
        wake = workers[model]
        early = len(q) >= FLUSH_EARLY
    if restarted:
        _log(f"restarted dead {', '.join(restarted)}")
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
    try:
        # rate_acquire writes /tmp/vendor-rate: it raises on a full disk. No
        # free slot in its wait: do not send; requeue as a failed submit.
        if L.rate_acquire(model) is False:
            code, res = -1, {"errors": [{"message": L.RATE_WAIT_ERR}]}
        else:
            code, res = _post(model, {"requests": [batch_item(model, i["payload"]) for i in batch]})
    except Exception as e:  # noqa: BLE001
        # The batch is already off the queue: answer its callers now so their
        # own direct-call fallback runs, instead of leaving them to time out.
        for it in batch:
            _finish(it, error=f"broker flush failed: {type(e).__name__}: {e}"[:200])
        raise
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
        try:
            L.rate_throttled(model)  # writes /tmp/vendor-rate too: may raise on a full disk
        except Exception as e:  # noqa: BLE001  the batch below is still requeued or answered
            _log(f"flush:{model}: rate_throttled failed: {type(e).__name__}: {e}")
    full = json.dumps(res.get("errors") or res)
    msg = full[:200]
    # The callers' error text is cut to 200 characters, which hid the schema
    # path of the gpt-oss 400 for two days. Log the whole reply once per failed
    # submit (first 2,000 characters) so the cause can be read.
    _log(f"flush:{model}: batch submit {code} for {len(batch)} items: {full[:2000]}")
    for it in batch:  # requeue once, then fail so the caller's own retry runs
        if it.get("tries", 0) < 2:
            with lock:  # same lock as do_POST's give-up, so the check cannot race it
                if it.get("abandoned"):
                    continue  # its caller already got a 504; a requeue would sit forever
                it["tries"] = it.get("tries", 0) + 1
                queues.setdefault(model, []).append(it)
        else:
            _finish(it, error=f"batch submit {code}: {msg}")
    time.sleep(SUBMIT_RETRY_S)  # requeued items keep their old t, so without this they resubmit at once
    return True


def _loop_error(name: str) -> None:
    """Log a loop exception and pause; the thread keeps running."""
    with lock:
        stats["loop_errors"] += 1
    _log(f"{name}: error, continuing\n{traceback.format_exc()}")
    time.sleep(SUBMIT_RETRY_S)


def flusher(model: str) -> None:
    wake = workers[model]
    while True:
        beats[model] = time.time()
        try:
            wake.clear()
            with lock:
                wait = flush_wait(queues.get(model) or [], time.time())
            if wait > 0:
                wake.wait(wait)
                continue
            flush_once(model)
        except Exception:  # noqa: BLE001  one bad flush must not kill the model's queue
            _loop_error(f"flush:{model}")


def poll_once(b: dict) -> None:
    model = b["model"]
    if model in metered_polls and L.rate_acquire(model) is False:
        b["next_poll"] = time.time() + POLL_EVERY_S  # no slot: poll later, never over the cap
        return
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
        try:
            time.sleep(POLL_TICK_S)
            now = time.time()
            with lock:
                due = [b for b in pending if b["model"] == model and b.get("next_poll", 0) <= now]
            for b in due:
                poll_once(b)
        except Exception:  # noqa: BLE001
            _loop_error(f"poll:{model}")


def watchdog_once(now: float) -> str:
    """Restart dead threads; return a reason to exit if a queue is still stuck."""
    with lock:
        restarted = [n for m in list(threads) for n in ensure_threads(m)]
        if restarted:
            _log(f"watchdog restarted dead {', '.join(restarted)}")
        for m, q in queues.items():
            if q and now - min(i.get("t", now) for i in q) > STUCK_S:
                return f"{m}: {len(q)} queued, oldest {int(now - min(i.get('t', now) for i in q))}s"
            if q and now - beats.get(m, now) > STUCK_S:
                return f"{m}: {len(q)} queued, flusher wedged {int(now - beats[m])}s"
    return ""


def watchdog() -> None:
    while True:
        time.sleep(WATCH_S)
        try:
            why = watchdog_once(time.time())
        except Exception:  # noqa: BLE001
            why = "watchdog error: " + traceback.format_exc()
        if why:
            # Exit non-zero so launchd KeepAlive starts a fresh broker; callers
            # see a dropped connection and fall back to a direct call. The exit
            # sits in finally so nothing in the log write can skip it.
            try:
                _log(f"broker stuck, exiting for launchd restart: {why}")
            finally:
                os._exit(3)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            # Client hung up mid-response (common under KeepAlive load); not fatal.
            return

    def do_GET(self):
        if self.path == "/stats":
            with lock:
                body = dict(stats, queued={m: len(q) for m, q in queues.items() if q},
                            pending_batches=len(pending), models=model_stats(time.time()),
                            metered_polls=sorted(metered_polls), dead_threads=dead_threads())
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
            with lock:  # the caller gives up: drop the item so it is never sent
                item["abandoned"] = True
                q = queues.get(model) or []
                q[:] = [x for x in q if x is not item]
            return self._send(504, {"error": "broker timeout"})
        self._send(200, {"result": item["result"]} if not item["error"] else {"error": item["error"]})


def main() -> int:
    if not TOKEN:
        print("no CLOUDFLARE_API_TOKEN", file=sys.stderr)
        return 2
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    srv.daemon_threads = True
    print(f"cf batch broker on 127.0.0.1:{PORT}", flush=True)
    threading.Thread(target=watchdog, daemon=True, name="watchdog").start()
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
