#!/usr/bin/env python3
"""Offline tests for cf_batch_broker: flush timing, per-model stats, per-model
threads, unmetered polls with a 429 fallback. No network: _post and the rate
limiter are stubbed.

2026-10-03: the broker sent ~1.5 items per batch (FLUSH_S 2 s) and polled every
pending batch every 4 s through the 18/min limiter, so polls ate the paid cap.
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cf_batch_broker as B  # noqa: E402


def _reset() -> None:
    B.queues.clear()
    B.pending.clear()
    B.workers.clear()
    B.metered_polls.clear()
    for k in B.stats:
        B.stats[k] = 0


def _item(t: float, payload=None) -> dict:
    return {"payload": payload or {"messages": []}, "event": threading.Event(), "t": t}


def test_flush_wait() -> None:
    now = 1000.0
    assert B.flush_wait([], now) == B.FLUSH_S
    assert B.flush_wait([_item(now - 1)], now) == B.FLUSH_S - 1
    assert B.flush_wait([_item(now - B.FLUSH_S - 1)], now) == 0
    assert B.flush_wait([_item(now) for _ in range(B.FLUSH_EARLY)], now) == 0
    assert 0 < B.flush_wait([_item(now) for _ in range(B.FLUSH_EARLY - 1)], now) <= B.FLUSH_S
    # a requeued (old) item at the back still makes the queue due
    assert B.flush_wait([_item(now), _item(now - B.FLUSH_S - 1)], now) == 0
    assert B.FLUSH_S == 8.0 and B.FLUSH_EARLY == 10


def test_take_batch_caps() -> None:
    q = [_item(0) for _ in range(B.MAX_ITEMS + 5)]
    assert len(B.take_batch(q)) == B.MAX_ITEMS and len(q) == 5


def test_model_stats() -> None:
    _reset()
    now = 2000.0
    B.queues["a"] = [_item(now - 3), _item(now - 1)]
    B.queues["b"] = []
    B.pending.append({"model": "a", "rid": "r1", "items": [1, 2, 3], "t": now - 20})
    B.pending.append({"model": "c", "rid": "r2", "items": [1], "t": now - 5})
    B.pending.append({"model": "c", "rid": "r3", "items": [1, 2], "t": now - 50})
    s = B.model_stats(now)
    assert s["a"] == {"queued": 2, "oldest_queued_s": 3.0, "pending_batches": 1,
                      "pending_items": 3, "oldest_pending_s": 20.0}, s["a"]
    assert "b" not in s
    assert s["c"]["queued"] == 0 and s["c"]["pending_batches"] == 2
    assert s["c"]["pending_items"] == 3 and s["c"]["oldest_pending_s"] == 50.0


def test_per_model_threads_and_unmetered_polls() -> None:
    """A slow model's polls must not hold up another model; polls skip the limiter."""
    _reset()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S)
    acquired: list[tuple[str, str]] = []
    calls: list[tuple[str, str]] = []

    def fake_post(model, body, timeout=120):
        kind = "poll" if "request_id" in body else "submit"
        calls.append((model, kind))
        if kind == "submit":
            return 202, {"result": {"request_id": f"{model}-rid"}}
        if model == "slow":
            time.sleep(1.5)  # a slow poll for one model
            return 200, {"result": {"status": "running"}}
        return 200, {"result": {"results": [{"index": 0, "success": True, "result": {"ok": model}}]}}

    try:
        B._post = fake_post
        B.L.rate_acquire = lambda m, *a, **k: acquired.append((m, "x"))
        B.L.rate_throttled = lambda m: None
        B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S = 0.1, 0.05, 0.1
        slow, fast = _item(time.time()), _item(time.time())
        B.enqueue("slow", slow)
        time.sleep(0.4)  # slow model is now mid-poll
        t0 = time.time()
        B.enqueue("fast", fast)
        assert fast["event"].wait(1.0), "fast model waited behind slow model's poll"
        assert fast["result"] == {"ok": "fast"} and time.time() - t0 < 1.0
        assert not slow["event"].is_set()
        # only submits went through the limiter
        n_submits = sum(1 for _, k in calls if k == "submit")
        assert len(acquired) == n_submits == 2, (acquired, calls)
        assert set(B.workers) == {"slow", "fast"}
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S = old
        B.pending.clear()


def test_early_flush_and_poll_429_fallback() -> None:
    _reset()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S)
    acquired, throttled, sizes = [], [], []
    state = {"polls": 0}

    def fake_post(model, body, timeout=120):
        if "requests" in body:
            sizes.append(len(body["requests"]))
            return 202, {"result": {"request_id": "rid"}}
        state["polls"] += 1
        if state["polls"] == 1:
            return 429, {"errors": [{"message": "rate"}]}
        return 200, {"result": {"results": [{"index": k, "result": {"k": k}} for k in range(10)]}}

    try:
        B._post = fake_post
        B.L.rate_acquire = lambda m, *a, **k: acquired.append(m)
        B.L.rate_throttled = lambda m: throttled.append(m)
        B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S = 30.0, 0.05, 0.1  # only the early rule can flush
        items = [_item(time.time()) for _ in range(B.FLUSH_EARLY)]
        for it in items:
            B.enqueue("m", it)
        assert all(it["event"].wait(3.0) for it in items), "early flush did not fire"
        assert sizes == [B.FLUSH_EARLY]
        assert [it["result"] for it in items] == [{"k": k} for k in range(10)]
        assert throttled == ["m"] and "m" in B.metered_polls and B.stats["poll_429s"] == 1
        # 1 submit + the poll after the 429 went through the limiter
        assert acquired == ["m", "m"], acquired
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S = old
        B.pending.clear()


def main() -> int:
    for fn in (test_flush_wait, test_take_batch_caps, test_model_stats,
               test_per_model_threads_and_unmetered_polls, test_early_flush_and_poll_429_fallback, test_submit_failure_spacing):
        fn()
        print("ok", fn.__name__)
    print("ALL PASS")
    return 0


def test_submit_failure_spacing() -> None:
    calls = []

    def post(model, body, timeout=120):
        calls.append(time.time())
        return 503, {"errors": [{"message": "busy"}]}
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S)
    B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = post, (lambda m, *a, **k: None), (lambda m: None), 0.3
    try:
        it = {"payload": {"x": 1}, "event": threading.Event(), "t": time.time() - 100}
        B.enqueue("fail-model", it)
        assert it["event"].wait(10)
        assert len(calls) == 3 and it["error"].startswith("batch submit 503")
        assert calls[1] - calls[0] >= 0.25 and calls[2] - calls[1] >= 0.25, calls
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = old


if __name__ == "__main__":
    raise SystemExit(main())
