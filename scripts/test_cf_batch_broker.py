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
    B.threads.clear()
    B.beats.clear()
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
               test_per_model_threads_and_unmetered_polls, test_early_flush_and_poll_429_fallback, test_submit_failure_spacing,
               test_flusher_survives_full_disk, test_dead_flusher_is_restarted, test_watchdog_exits_when_stuck,
               test_watchdog_restart_is_not_a_wedge, test_abandoned_item_is_not_requeued,
               test_batch_stuck_counts_a_queue_that_does_not_drain, test_full_disk_log_does_not_kill_threads,
               test_throttle_write_failure_still_requeues, test_abandon_between_check_and_requeue,
               test_rate_acquire_gives_up_without_a_slot, test_gpt_oss_batch_uses_responses_shape):
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


def test_flusher_survives_full_disk() -> None:
    """2026-10-06: rate_acquire hit ENOSPC on /tmp/vendor-rate and killed both
    flushers; their batch was lost and later items queued for 11 hours."""
    _reset()
    old = (B._post, B.L.rate_acquire, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S)
    state = {"acq": 0}

    def acquire(m, *a, **k):
        state["acq"] += 1
        if state["acq"] == 1:
            raise OSError(28, "No space left on device")

    def post(model, body, timeout=120):
        if "requests" in body:
            return 202, {"result": {"request_id": "rid"}}
        return 200, {"result": {"results": [{"index": 0, "result": {"ok": 1}}]}}
    try:
        B._post, B.L.rate_acquire = post, acquire
        B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S = 0.05, 0.05, 0.05, 0.05
        first = _item(time.time())
        B.enqueue("disk", first)
        assert first["event"].wait(3), "the lost batch's caller was never answered"
        assert first["error"].startswith("broker flush failed: OSError"), first["error"]
        second = _item(time.time())
        B.enqueue("disk", second)
        assert second["event"].wait(3) and second["result"] == {"ok": 1}, second
        assert B.threads["disk"][0].is_alive() and B.stats["loop_errors"] == 1
        assert B.dead_threads() == []
    finally:
        B._post, B.L.rate_acquire, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S = old
        B.pending.clear()


def test_dead_flusher_is_restarted() -> None:
    _reset()
    dead = threading.Thread(target=lambda: None, name="flush:x")
    dead.start()
    dead.join()
    live = threading.Thread(target=time.sleep, args=(1,), name="poll:x", daemon=True)
    live.start()
    B.workers["x"] = threading.Event()
    B.threads["x"] = [dead, live]
    B.FLUSH_S, old = 30.0, B.FLUSH_S  # the new flusher just waits
    try:
        assert B.dead_threads() == ["flush:x"]
        B.enqueue("x", _item(time.time()))
        assert B.threads["x"][0] is not dead and B.threads["x"][0].is_alive()
        assert B.threads["x"][1] is live and B.stats["thread_restarts"] == 1
        assert B.dead_threads() == []
    finally:
        B.FLUSH_S = old


def test_watchdog_exits_when_stuck() -> None:
    _reset()
    now = time.time()
    B.queues["k"] = [_item(now - 5)]
    assert B.watchdog_once(now) == ""
    B.queues["k"] = [_item(now - B.STUCK_S - 1)]
    assert B.watchdog_once(now).startswith("k: 1 queued")
    # A live flusher that has not come round its loop (wedged in a lock) also exits.
    B.queues["k"] = [_item(now - 5)]
    B.beats["k"] = now - B.STUCK_S - 1
    assert "flusher wedged" in B.watchdog_once(now)
    B.queues.clear()
    B.beats.clear()


def test_watchdog_restart_is_not_a_wedge() -> None:
    """A flusher the watchdog just restarted must not trip the wedge check in
    the same pass (its old heartbeat is stale)."""
    _reset()
    dead = threading.Thread(target=lambda: None, name="flush:y")
    dead.start()
    dead.join()
    now = time.time()
    B.workers["y"] = threading.Event()
    B.threads["y"] = [dead, None]
    B.beats["y"] = now - B.STUCK_S - 100
    B.queues["y"] = [_item(now - 5)]
    B.FLUSH_S, old = 30.0, B.FLUSH_S
    try:
        assert B.watchdog_once(now) == ""
        assert B.threads["y"][0].is_alive() and B.stats["thread_restarts"] == 1
    finally:
        B.FLUSH_S = old
        B.queues.clear()


def test_abandoned_item_is_not_requeued() -> None:
    """A batch in flight when its caller timed out must not be put back on the
    queue: nobody waits for it, and its old age would trip the watchdog."""
    _reset()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S)
    try:
        B._post = lambda model, body, timeout=120: (500, {"errors": [{"message": "x"}]})
        B.L.rate_acquire = B.L.rate_throttled = lambda *a, **k: None
        B.SUBMIT_RETRY_S = 0
        gone, live = _item(time.time() - 100), _item(time.time() - 100)
        gone["abandoned"] = True
        B.queues["z"] = [gone, live]
        assert B.flush_once("z")
        assert B.queues["z"] == [live], B.queues["z"]
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = old
        B.queues.clear()


def test_batch_stuck_counts_a_queue_that_does_not_drain() -> None:
    """2026-10-06: a dead flusher left oldest_pending_s at 0 while items sat
    queued for hours, so overflow calls kept going to the broker."""
    L = B.L
    saved = dict(L._broker_seen)
    try:
        m = "@cf/moonshotai/kimi-k2.6"
        L._broker_seen["stats"] = {"models": {m: {"queued": 106, "oldest_queued_s": 36000.0}}}
        assert L._batch_stuck(m)
        L._broker_seen["stats"] = {"models": {m: {"queued": 3, "oldest_queued_s": 5.0}}}
        assert not L._batch_stuck(m)
        L._broker_seen["stats"] = {"models": {m: {"oldest_pending_s": L.BATCH_STUCK_S + 1}}}
        assert L._batch_stuck(m)
    finally:
        L._broker_seen.clear()
        L._broker_seen.update(saved)


class _FullDisk:
    """A stderr whose every write fails as on a full disk."""
    def write(self, *_a):
        raise OSError(28, "No space left on device")

    def flush(self):
        raise OSError(28, "No space left on device")


def test_full_disk_log_does_not_kill_threads() -> None:
    """Review 2026-10-06: with the log on the full disk, the print in the error
    handler raised and killed the flusher anyway, and the watchdog's print
    raised before os._exit, so a stuck broker never exited."""
    _reset()
    old = (B._post, B.L.rate_acquire, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S,
           B.WATCH_S, sys.stderr, B.os._exit)
    exits = []

    def fake_exit(code):
        exits.append(code)
        raise SystemExit(code)  # ends the watchdog thread quietly

    def acquire(m, *a, **k):
        raise OSError(28, "No space left on device")
    try:
        B._post, B.L.rate_acquire = (lambda *a, **k: (500, {})), acquire
        B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S = 0.05, 0.05, 0.05, 0.05
        sys.stderr = _FullDisk()
        it = _item(time.time())
        B.enqueue("m", it)
        assert it["event"].wait(3) and it["error"].startswith("broker flush failed: OSError")
        time.sleep(0.2)  # let the flusher come round its error handler
        assert B.stats["loop_errors"] >= 1
        assert B.dead_threads() == [], B.dead_threads()
        # A stuck queue still reaches os._exit even though the log write fails.
        B.os._exit, B.WATCH_S = fake_exit, 0.05
        B.queues["stuck"] = [_item(time.time() - B.STUCK_S - 10)]
        w = threading.Thread(target=B.watchdog, daemon=True)
        w.start()
        w.join(3)
        assert exits == [3], exits
    finally:
        (B._post, B.L.rate_acquire, B.FLUSH_S, B.POLL_TICK_S, B.POLL_EVERY_S, B.SUBMIT_RETRY_S,
         B.WATCH_S, sys.stderr, B.os._exit) = old
        B.queues.clear()
        B.pending.clear()


def test_throttle_write_failure_still_requeues() -> None:
    """Review 2026-10-06: on a 429, rate_throttled (it writes /tmp/vendor-rate)
    raised on a full disk after the batch left the queue, so its callers hung."""
    _reset()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S, sys.stderr)

    def throttled(m):
        raise OSError(28, "No space left on device")
    try:
        B._post = lambda model, body, timeout=120: (429, {"errors": [{"message": "rate"}]})
        B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = (lambda *a, **k: None), throttled, 0
        sys.stderr = _FullDisk()
        fresh, spent = _item(time.time() - 100), _item(time.time() - 100)
        spent["tries"] = 2
        B.queues["t"] = [fresh, spent]
        assert B.flush_once("t")
        assert B.queues["t"] == [fresh] and fresh["tries"] == 1
        assert spent["event"].is_set() and spent["error"].startswith("batch submit 429")
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S, sys.stderr = old
        B.queues.clear()


def test_abandon_between_check_and_requeue() -> None:
    """Review 2026-10-06: the abandoned check ran outside the lock, so a caller
    giving up just after it could still get its item requeued and paid for.
    Here the caller gives up the moment the flusher takes the lock to requeue
    (the first lock is take_batch, the second the requeue)."""
    _reset()
    real = B.lock
    gone = _item(time.time() - 100)

    class GiveUpOnSecond:
        n = 0

        def __enter__(self):
            real.acquire()
            GiveUpOnSecond.n += 1
            if GiveUpOnSecond.n == 2:
                gone["abandoned"] = True  # do_POST's give-up runs under this lock
            return self

        def __exit__(self, *a):
            real.release()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S)
    try:
        B._post = lambda model, body, timeout=120: (500, {"errors": [{"message": "x"}]})
        B.L.rate_acquire = B.L.rate_throttled = lambda *a, **k: None
        B.SUBMIT_RETRY_S = 0
        B.queues["r"] = [gone]
        B.lock = GiveUpOnSecond()
        assert B.flush_once("r") is True
        assert GiveUpOnSecond.n == 2 and B.queues["r"] == [], B.queues["r"]
    finally:
        B.lock = real
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = old
        B.queues.clear()

def test_rate_acquire_gives_up_without_a_slot() -> None:
    """Red team 2026-10-06 (translation-caps-and-429s): after its wait,
    rate_acquire took a slot over the cap anyway, and each such call drew a
    429. Now it returns False, takes no slot, and nothing is sent."""
    import json
    import tempfile
    from unittest import mock
    L = B.L
    with tempfile.TemporaryDirectory() as d, mock.patch.object(L, "RATE_DIR", Path(d)):
        m = "@cf/test/model"
        now = time.time()
        L._rate_file(m).write_text(json.dumps({"hits": [now, now], "limit": 2, "cut_at": now}))
        t0 = time.time()
        assert L.rate_acquire(m, max_wait=0.3) is False
        assert time.time() - t0 < 2
        assert len(json.loads(L._rate_file(m).read_text())["hits"]) == 2, "no slot taken"
        L._rate_file(m).write_text(json.dumps({"hits": [now], "limit": 2, "cut_at": now}))
        assert L.rate_acquire(m, max_wait=0.3) is True
        assert len(json.loads(L._rate_file(m).read_text())["hits"]) == 2
        # vendor_call sends nothing, and does not count a throttle, when no slot came free.
        with mock.patch.object(L, "batch_route", return_value=False), \
                mock.patch.object(L, "rate_acquire", return_value=False), \
                mock.patch.object(L, "_vendor_call_raw") as raw, mock.patch.object(L, "rate_throttled") as th:
            r = L.vendor_call(m, [{"role": "user", "content": "x"}])
        raw.assert_not_called()
        th.assert_not_called()
        assert r["error"] == L.RATE_WAIT_ERR and "429" not in r["error"]
    # The broker does not submit a batch without a slot; it requeues it.
    _reset()
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S)
    sent = []
    try:
        B._post = lambda model, body, timeout=120: sent.append(body) or (202, {"result": {"request_id": "r"}})
        B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = (lambda *a, **k: False), (lambda m: None), 0
        it = _item(time.time() - 100)
        B.queues["s"] = [it]
        assert B.flush_once("s")
        assert sent == [] and B.queues["s"] == [it] and it["tries"] == 1
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = old
        B.queues.clear()


def test_gpt_oss_batch_uses_responses_shape() -> None:
    """2026-10-06: every gpt-oss batch drew 400 'oneOf ... prompt/messages':
    its async schema takes Responses items ({"input"}), not Messages items."""
    _reset()
    sent, logged = [], []
    old = (B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S, B._log)
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    try:
        B._post = lambda model, body, timeout=120: sent.append(body) or (202, {"result": {"request_id": "r"}})
        B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S = (lambda *a, **k: None), (lambda m: None), 0
        B.queues["@cf/openai/gpt-oss-120b"] = [_item(time.time() - 100, {"messages": msgs, "temperature": 0.6,
                                                                          "max_tokens": 12000})]
        B.queues["@cf/moonshotai/kimi-k2.6"] = [_item(time.time() - 100, {"messages": msgs, "max_tokens": 9})]
        assert B.flush_once("@cf/openai/gpt-oss-120b") and B.flush_once("@cf/moonshotai/kimi-k2.6")
        assert sent[0] == {"requests": [{"input": msgs}]}, sent[0]
        assert sent[1] == {"requests": [{"messages": msgs, "max_tokens": 9}]}, sent[1]
        assert B.batch_item("@cf/openai/gpt-oss-20b", {"messages": msgs, "reasoning_effort": "low"}) == \
            {"input": msgs, "reasoning": {"effort": "low"}}
        assert B.batch_item("@cf/openai/gpt-oss-20b", {"messages": msgs, "reasoning_effort": "none"}) == {"input": msgs}
        # A failed submit logs the whole reply, not the 200-character cut the caller sees.
        long = "x" * 600
        B._post = lambda model, body, timeout=120: (400, {"errors": [{"message": long}]})
        B._log = logged.append
        B.queues["m400"] = [_item(time.time() - 100)]
        assert B.flush_once("m400")
        assert any(long in line and "batch submit 400 for 1 items" in line for line in logged), logged
    finally:
        B._post, B.L.rate_acquire, B.L.rate_throttled, B.SUBMIT_RETRY_S, B._log = old
        B.queues.clear()
        B.pending.clear()


if __name__ == "__main__":
    raise SystemExit(main())
