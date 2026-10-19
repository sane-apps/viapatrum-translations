#!/usr/bin/env python3
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

TMP = tempfile.mkdtemp()
os.environ["PLAN_STATE"] = str(Path(TMP) / "state.json")
os.environ["PLAN_SLOTS"] = str(Path(TMP) / "slots")
os.environ["PLAN_CLAUDE_CALLS_PER_HOUR"] = "2"
os.environ["PLAN_MUSE_CALLS_PER_HOUR"] = "50"
os.environ["PLAN_MUSE_CALLS_PER_DAY"] = "3"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_calls as pc  # noqa: E402

NOW = datetime(2026, 10, 19, 16, 0, tzinfo=timezone.utc)  # 12:00 in New York


class Clock:
    """Fake time: _sleep advances _now and time.time together."""

    def __init__(self):
        self.t = NOW.timestamp()

    def now(self):
        return datetime.fromtimestamp(self.t, timezone.utc)

    def sleep(self, s):
        self.t += s

    def time(self):
        return self.t


def fresh():
    for f in Path(TMP).glob("state*"):
        f.unlink()


class ResetParsing(unittest.TestCase):
    def test_claude_weekly_with_date_and_zone(self):
        got = pc.claude_reset("You've hit your weekly limit · resets Oct 12 at 9pm (America/New_York)",
                              datetime(2026, 10, 10, 12, tzinfo=timezone.utc))
        self.assertEqual(got, datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc))  # 9 pm EDT

    def test_claude_session_limit_rolls_to_next_day_when_past(self):
        got = pc.claude_reset("You've hit your session limit · resets 3am (America/New_York)", NOW)
        self.assertEqual(got, datetime(2026, 10, 20, 7, 0, tzinfo=timezone.utc))

    def test_claude_ordinary_error_is_not_a_limit(self):
        self.assertIsNone(pc.claude_reset("API Error: overloaded", NOW))

    def test_muse_iso_reset(self):
        got = pc.muse_reset("API error 429: Subscription quota exhausted. Your usage window resets at "
                            "2026-10-19T00:28:23Z. (rate_limit_error)", NOW)
        self.assertEqual(got, datetime(2026, 10, 19, 0, 28, 23, tzinfo=timezone.utc))

    def test_unreadable_reset_waits_an_hour(self):
        self.assertEqual(pc.claude_reset("Claude AI usage limit reached", NOW), NOW + pc.timedelta(hours=1))


class Waiting(unittest.TestCase):
    def setUp(self):
        fresh()
        self.clock = Clock()
        self.patches = [mock.patch.object(pc, "_now", self.clock.now), mock.patch.object(pc, "_sleep", self.clock.sleep),
                        mock.patch.object(pc.time, "time", self.clock.time)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_spent_window_waits_for_reset_then_retries_same_call(self):
        replies = iter([("You've hit your session limit · resets 2pm (America/New_York)", True), ('{"ok": true}', False)])
        with mock.patch.object(pc, "_run_claude", lambda *a: next(replies)):
            r = pc.chat("claude-haiku-5-5", [{"role": "user", "content": "x"}])
        self.assertEqual(r["content"], '{"ok": true}')
        self.assertGreaterEqual(self.clock.t, datetime(2026, 10, 19, 18, 0, tzinfo=timezone.utc).timestamp())

    def test_other_processes_see_the_pause(self):
        pc.pause("muse", NOW + pc.timedelta(minutes=30), "quota")
        self.assertEqual(pc.paused_until("muse", NOW), NOW + pc.timedelta(minutes=30))
        self.assertIsNone(pc.paused_until("claude", NOW))

    def test_hourly_budget_spaces_calls(self):
        with mock.patch.object(pc, "_run_claude", lambda *a: ("fine", False)):
            for _ in range(3):
                pc.chat("claude-sonnet-5-5", [{"role": "user", "content": "x"}])
        self.assertGreaterEqual(self.clock.t - NOW.timestamp(), 3600)  # third call waited for the hour

    def test_daily_budget_holds_until_the_oldest_call_ages_out(self):
        with mock.patch.object(pc, "_run_muse", lambda *a: ("fine", False)):
            for _ in range(3):
                pc.chat("muse", [{"role": "user", "content": "x"}])
            r = pc.chat("muse", [{"role": "user", "content": "x"}])  # 4th in a day: waits ~24 h > max wait
        self.assertIn(pc.PAUSED, r["error"])

    def test_gives_up_after_max_wait(self):
        pc.pause("claude", NOW + pc.timedelta(days=5), "weekly")
        with mock.patch.object(pc, "_run_claude", lambda *a: self.fail("must not call while paused")):
            r = pc.chat("claude-opus-5-5", [{"role": "user", "content": "x"}])
        self.assertIn(pc.PAUSED, r["error"])

    def test_muse_quota_message_pauses_muse_only(self):
        replies = iter([("Subscription quota exhausted. Your usage window resets at 2026-10-19T17:00:00Z.", True),
                        ("done", False)])
        with mock.patch.object(pc, "_run_muse", lambda *a: next(replies)):
            r = pc.chat("muse", [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}])
        self.assertEqual(r["content"], "done")
        self.assertIsNone(pc.paused_until("claude"))

    def test_muse_runner_down_waits_instead_of_failing(self):
        replies = iter([(f"{pc.RUNNER_DOWN}: heartbeat silent over 600s", True), ("drafted", False)])
        with mock.patch.object(pc, "_run_muse", lambda *a: next(replies)):
            r = pc.chat("muse", [{"role": "user", "content": "x"}])
        self.assertEqual(r["content"], "drafted")
        self.assertGreaterEqual(self.clock.t - NOW.timestamp(), 600)

    def test_non_limit_error_is_returned_not_waited(self):
        with mock.patch.object(pc, "_run_claude", lambda *a: ("overloaded", True)):
            r = pc.chat("claude-haiku-5-5", [{"role": "user", "content": "x"}])
        self.assertIn("call failed", r["error"])
        self.assertLess(self.clock.t - NOW.timestamp(), 5)


if __name__ == "__main__":
    unittest.main()
