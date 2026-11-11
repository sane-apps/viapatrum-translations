#!/usr/bin/env python3
import json
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
os.environ["PLAN_METER_PUSH"] = "0"  # never copy test meters to the other Mac
os.environ["PLAN_METER_REFRESH"] = "0"  # never run the real muse or agy usage commands from a test
os.environ["PLAN_SPILL"] = "0"  # second doors off unless a test turns them on: an older test that pauses a plan must never reach a real CLI
os.environ["PLAN_METER_DIR"] = str(Path(TMP) / "no-meters")  # never read this Mac's real plan meters
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

    def test_grok_limit_with_iso_reset(self):
        got = pc.grok_reset("Error: usage limit reached for your plan; resets at 2026-10-20T04:00:00Z", NOW)
        self.assertEqual(got, datetime(2026, 10, 20, 4, 0, tzinfo=timezone.utc))

    def test_grok_spent_pool_pauses(self):
        # 2026-10-19: the X plan's Grok pool ran dry with a 402, no reset time given.
        msg = 'API error (status 402 Payment Required): Grok Build usage balance exhausted'
        self.assertEqual(pc.grok_reset(msg, NOW), NOW + pc.timedelta(hours=1))

    def test_grok_ordinary_error_is_not_a_limit(self):
        self.assertIsNone(pc.grok_reset("grok timeout after 900s", NOW))

    def test_agy_ids_route_to_agy_plan(self):
        self.assertEqual(pc.plan_of("agy/claude-opus-4-6-thinking"), "agy")
        self.assertEqual(pc.plan_of("agy/gemini-3.8-flash-high"), "agy")
        self.assertIsNone(pc.plan_of("agy/not-a-model"))
        self.assertEqual(pc.plan_of("claude-opus-5-5"), "claude")

    def test_agy_limit_pauses_one_hour_or_until_iso(self):
        self.assertEqual(pc.agy_reset("RESOURCE_EXHAUSTED: quota exceeded", NOW), NOW + pc.timedelta(hours=1))
        got = pc.agy_reset("quota exhausted; resets at 2026-10-24T22:00:00Z", NOW)
        self.assertEqual(got.isoformat(), "2026-10-24T22:00:00+00:00")

    def test_agy_ordinary_error_is_not_a_limit(self):
        self.assertIsNone(pc.agy_reset("agy timeout after 900s", NOW))

    def test_new_agy_models_route_to_agy(self):
        for m in ("gemini-4-argon-high", "claude-sonnet-5-5-medium", "claude-opus-5-5-low"):
            self.assertEqual(pc.plan_of("agy/" + m), "agy")

    def test_cursor_ids_route_to_cursor_plan(self):
        self.assertEqual(pc.plan_of("cursor/composer-2.5"), "cursor")
        # Models the plan does not include (2026-11-11) are not plan models: they would need bought credits.
        self.assertIsNone(pc.plan_of("cursor/gpt-5.5-low"))
        self.assertIsNone(pc.plan_of("cursor/claude-sonnet-5-5-low"))
        self.assertIn("cursor", pc.PLANS)

    def test_cursor_limit_pauses_one_hour_or_until_iso(self):
        msg = ("ActionRequiredError: GPT-5.5 is not included in your weekly usage Buy credits or switch to a "
               "Grok model to continue.")
        self.assertEqual(pc.cursor_reset(msg, NOW), NOW + pc.timedelta(hours=1))
        got = pc.cursor_reset("usage limit reached; resets at 2026-10-20T00:00:00Z", NOW)
        self.assertEqual(got, datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc))
        self.assertIsNone(pc.cursor_reset("cursor timeout after 900s", NOW))

    def test_grok_ids_route_to_the_grok_plan(self):
        self.assertEqual(pc.plan_of("grok-4.7-build-fast"), "grok")
        self.assertIsNone(pc.plan_of("@cf/zai-org/glm-5.2"))

    def test_budgets_file_is_the_one_live_setting(self):
        f = pc.STATE.with_name("budgets.json")
        try:
            f.write_text('{"claude": [7, 70]}')
            self.assertEqual(pc.budgets("claude"), (7, 70))
            self.assertEqual(pc.budgets("muse"), pc.BUDGETS["muse"])  # plans not in the file keep defaults
        finally:
            f.unlink(missing_ok=True)
        self.assertEqual(pc.budgets("claude"), pc.BUDGETS["claude"])

    def test_night_block_applies_in_its_hours(self):
        f = pc.STATE.with_name("budgets.json")
        h = NOW.astimezone().hour
        try:
            f.write_text(json.dumps({"claude": [15, 300], "night": {"hours": [h, (h + 1) % 24], "claude": [100, 900]}}))
            self.assertEqual(pc.budgets("claude", NOW), (100, 900))
            self.assertEqual(pc.budgets("claude", NOW + pc.timedelta(hours=2)), (15, 300))
            self.assertEqual(pc.budgets("muse", NOW), pc.BUDGETS["muse"])
        finally:
            f.unlink(missing_ok=True)

    def test_grok_report_splits_windows_at_limits(self):
        f = pc._ledger_path()
        rows = [{"at": "t1", "ok": True, "limit": False, "tokens": 100, "uncached": 60},
                {"at": "t2", "ok": True, "limit": False, "tokens": 50, "uncached": 50},
                {"at": "t3", "ok": False, "limit": True, "tokens": 0, "uncached": 0},
                {"at": "t4", "ok": False, "limit": True, "tokens": 0, "uncached": 0},
                {"at": "t5", "ok": True, "limit": False, "tokens": 30, "uncached": 30}]
        try:
            f.write_text("".join(json.dumps(r) + "\n" for r in rows))
            rep = pc.grok_report()
        finally:
            f.unlink(missing_ok=True)
        self.assertEqual(rep["windows"], [{"start": "t1", "tokens": 150, "uncached": 110, "calls": 2,
                                           "limit_at": "t3", "back_at": "t5"}])
        self.assertEqual(rep["since_reset"], {"start": "t5", "tokens": 30, "uncached": 30, "calls": 1})
        self.assertFalse(rep["limited_now"])

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

    def test_auth_failure_pauses_briefly_and_spends_no_budget(self):
        # 2026-11-07: OAuth failures in the launchd lanes were counted against Claude's hourly budget.
        replies = iter([("Failed to authenticate: OAuth session expired and could not be refreshed", True),
                        ("checked", False)])
        with mock.patch.object(pc, "_run_claude", lambda *a: next(replies)):
            r = pc.chat("claude-sonnet-5-5", [{"role": "user", "content": "x"}])
        self.assertEqual(r["content"], "checked")
        self.assertEqual(json.loads(pc.STATE.read_text())["claude"]["calls_total"], 1)  # only the real call
        self.assertGreaterEqual(self.clock.t - NOW.timestamp(), pc.AUTH_PAUSE_S)
        self.assertLess(self.clock.t - NOW.timestamp(), pc.AUTH_PAUSE_S + 60)

    def test_cursor_limit_pauses_cursor_only_then_retries(self):
        replies = iter([("ActionRequiredError: Composer 2.5 is not included in your weekly usage Buy credits", True),
                        ('{"ok": true}', False)])
        with mock.patch.object(pc, "_run_cursor", lambda *a: next(replies)):
            r = pc.chat("cursor/composer-2.5", [{"role": "user", "content": "x"}])
        self.assertEqual(r["content"], '{"ok": true}')
        self.assertGreaterEqual(self.clock.t - NOW.timestamp(), 3600)
        self.assertIsNone(pc.paused_until("agy"))

    def test_agy_quota_pauses_only_that_model_family(self):
        # 2026-11-11: the 4 Nov "Individual quota reached" stop was Gemini alone; a spent Gemini
        # referee must not stop an agy Claude checker, while the plan budget stays shared.
        self.assertEqual(pc.pause_key("agy/gemini-3.8-flash-high"), "agy/gemini")
        self.assertEqual(pc.pause_key("agy/claude-opus-5-5-medium"), "agy/claude")
        self.assertEqual(pc.pause_key("claude-sonnet-5-5"), "claude")
        replies = iter([("Individual quota reached. Please upgrade your subscription. Resets in 167h35m32s.", True)])
        with mock.patch.object(pc, "_run_agy", lambda *a: next(replies)), mock.patch.object(pc, "MAX_WAIT_S", 60):
            r = pc.chat("agy/gemini-3.8-flash-high", [{"role": "user", "content": "x"}])
        self.assertIn(pc.PAUSED, r["error"])
        self.assertIsNotNone(pc.paused_until("agy/gemini"))
        self.assertIsNone(pc.paused_until("agy/claude"))
        self.assertIn("agy/gemini", pc.status()["agy"]["model_pauses"])
        with mock.patch.object(pc, "_run_agy", lambda *a: ("ruled", False)):
            self.assertEqual(pc.chat("agy/claude-opus-5-5-medium", [{"role": "user", "content": "x"}])["content"], "ruled")
        pc.pause("agy", NOW + pc.timedelta(days=2), "whole plan")  # a whole-plan pause still covers every family
        self.assertIsNotNone(pc.paused_until("agy/claude"))

    @mock.patch.object(pc, "SPILL", True)
    def test_second_door_when_own_plan_would_wait(self):
        # Owner 2026-11-11: own subscription first; the same model on another plan only when the own
        # plan would wait and the other has room.
        msg = [{"role": "user", "content": "x"}]
        with mock.patch.object(pc, "_run_claude", lambda *a: ("own", False)), mock.patch.object(pc, "_run_agy", lambda *a: ("second", False)):
            r = pc.chat("claude-opus-5-5", msg)
            self.assertEqual((r["content"], r.get("door")), ("own", None))          # room on its own plan: no second door
            pc.pause("claude", NOW + pc.timedelta(hours=3), "weekly limit")
            self.assertEqual(pc.route("claude-opus-5-5")[0], "agy/claude-opus-5-5-medium")
            r = pc.chat("claude-opus-5-5", msg)
            self.assertEqual((r["content"], r["door"]), ("second", "agy/claude-opus-5-5-medium"))
            self.assertEqual(pc.status()["second_door_calls"], {"claude-opus-5-5 -> agy/claude-opus-5-5-medium": 1})
            self.assertEqual(pc.chat("claude-haiku-5-5", msg, _max_wait=60).get("door"), None)   # no door listed: it waits
            pc.pause("agy/claude", NOW + pc.timedelta(hours=4), "quota")            # both doors shut: wait on the own plan
            self.assertEqual(pc.route("claude-opus-5-5")[0], "claude-opus-5-5")
            r = pc.chat("claude-opus-5-5", msg)
            self.assertEqual((r["content"], r.get("door")), ("own", None))
            self.assertGreaterEqual(self.clock.t - NOW.timestamp(), 3 * 3600)

    @mock.patch.object(pc, "SPILL", True)
    def test_second_door_short_wait_and_switch_off(self):
        msg = [{"role": "user", "content": "x"}]
        with mock.patch.object(pc, "_run_claude", lambda *a: ("own", False)), mock.patch.object(pc, "_run_agy", lambda *a: ("second", False)):
            pc.pause("claude", NOW + pc.timedelta(seconds=120), "short")           # under 5 min: wait, do not switch
            self.assertEqual(pc.chat("claude-sonnet-5-5", msg).get("door"), None)
            pc.pause("claude", self.clock.now() + pc.timedelta(hours=2), "long")
            with mock.patch.object(pc, "SPILL", False):
                self.assertEqual(pc.route("claude-sonnet-5-5")[0], "claude-sonnet-5-5")
                self.assertEqual(pc.chat("claude-sonnet-5-5", msg).get("door"), None)

    @mock.patch.object(pc, "SPILL", True)
    def test_second_door_failure_falls_back_to_waiting(self):
        msg = [{"role": "user", "content": "x"}]
        with mock.patch.object(pc, "_run_claude", lambda *a: ("own", False)), mock.patch.object(pc, "_run_agy", lambda *a: ("agy crashed", True)):
            pc.pause("agy/claude", NOW + pc.timedelta(hours=1), "quota")
            r = pc.chat("agy/claude-opus-5-5-medium", msg)                          # the reverse door: the Claude plan
            self.assertEqual((r["content"], r["door"]), ("own", "claude-opus-5-5"))
            pc.pause("claude", self.clock.now() + pc.timedelta(hours=1), "limit")
        with mock.patch.object(pc, "_run_claude", lambda *a: ("own", False)), mock.patch.object(pc, "_run_agy", lambda *a: ("agy crashed", True)):
            fresh()
            pc.pause("claude", self.clock.now() + pc.timedelta(hours=1), "limit")
            r = pc.chat("claude-opus-5-5", msg)                                     # second door errors: own plan after the wait
            self.assertEqual((r["content"], r.get("door")), ("own", None))

    @mock.patch.object(pc, "SPILL", True)
    def test_meter_high_sends_background_calls_to_the_second_door(self):
        msg = [{"role": "user", "content": "x"}]
        mdir = Path(TMP) / "meters"
        mdir.mkdir(exist_ok=True)
        with mock.patch.object(pc, "METER_DIR", mdir), mock.patch.object(pc, "_run_claude", lambda *a: ("own", False)), \
                mock.patch.object(pc, "_run_agy", lambda *a: ("second", False)):
            t = self.clock.t
            (mdir / "claude.json").write_text(json.dumps({"at": t, "windows": {"five_hour": {"used_percentage": 40, "resets_at": t + 3600},
                                                                                "seven_day": {"used_percentage": 91, "resets_at": t + 86400}}}))
            self.assertTrue(pc.tight("claude"))
            self.assertEqual(pc.chat("claude-opus-5-5", msg)["door"], "agy/claude-opus-5-5-medium")
            pc.pause("agy/claude", self.clock.now() + pc.timedelta(hours=1), "quota")
            self.assertEqual(pc.route("agy/claude-opus-5-5-medium")[0], "agy/claude-opus-5-5-medium")   # never onto a plan whose meter is high
            (mdir / "claude.json").write_text(json.dumps({"at": t, "windows": {"seven_day": {"used_percentage": 91, "resets_at": t - 5}}}))
            self.assertFalse(pc.tight("claude"))                                    # the window has reset: the reading is dead
            (mdir / "claude.json").write_text("not json")
            self.assertEqual(pc.meter("claude"), {})
            self.assertIn("no meter", pc.table())

    def test_meter_well_under_pace_raises_the_background_budget(self):
        mdir = Path(TMP) / "meters2"
        mdir.mkdir(exist_ok=True)
        t = self.clock.t
        week = 7 * 86400

        def put(used, days_left, at=t):
            (mdir / "claude.json").write_text(json.dumps({"at": at, "windows": {"seven_day": {"used_percentage": used, "resets_at": t + days_left * 86400}}}))
        with mock.patch.object(pc, "METER_DIR", mdir):
            base = pc.budgets("claude")
            put(20, 3)                                   # 4 of 7 days gone (57%), 20% used: 37 points under pace
            self.assertTrue(pc.spare("claude"))
            self.assertEqual(pc.budgets("claude"), (base[0], int(base[1] * 1.5)))
            put(50, 3)                                   # 7 points under pace: not enough
            self.assertFalse(pc.spare("claude"))
            self.assertEqual(pc.budgets("claude"), base)
            put(5, 6.9)                                  # the window has only just begun
            self.assertFalse(pc.spare("claude"))
            put(62, 0.5)                                 # under pace but over 60% used
            self.assertFalse(pc.spare("claude"))
            put(20, 3, at=t - 7 * 3600)                  # a reading 7 hours old is not trusted
            self.assertFalse(pc.spare("claude"))
            self.assertFalse(pc.spare("grok"))           # no meter, no extra

    def test_muse_and_agy_usage_are_parsed_into_meters(self):
        # Real outputs, 2026-11-11 (Mini).
        muse = ('{"schemaVersion":1,"allowance":{"tier":"Muse Code High Usage","window":{"usedPercent":0,"resetsAtMs":1794426654000},'
                '"weekly":{"usedPercent":1,"resetsAtMs":1794787200000},"asOfMs":1794424826858,"source":"mint"},"reason":null,"hint":null}')
        self.assertEqual(pc.parse_muse_usage(muse), {"muse": {"five_hour": {"used_percentage": 0.0, "resets_at": 1794426654.0},
                                                              "seven_day": {"used_percentage": 1.0, "resets_at": 1794787200.0}}})
        self.assertEqual(pc.parse_muse_usage("muse usage: not logged in: run `muse login` first"), {})
        self.assertEqual(pc.parse_muse_usage('{"allowance": null, "reason": "locked"}'), {})
        agy = ("Gemini Models\tWeekly Limit Remaining\t97%\t2026-11-17T21:30:57Z\n"
               "Gemini Models\tFive Hour Limit Remaining\t100%\t2026-11-12T00:21:31Z\n"
               "Claude and GPT models\tWeekly Limit Remaining\t18%\t2026-11-17T21:41:20Z\n"
               "Claude and GPT models\tFive Hour Limit Remaining\t0%\t2026-11-11T20:12:32Z\n"
               "Gemini 4 Argon\tGemini 4 Argon Weekly Limit\t24%\t2026-11-17T21:30:51Z\n")
        got = pc.parse_agy_usage(agy)
        self.assertEqual(sorted(got), ["agy-argon", "agy-claude", "agy-gemini", "agy-gpt-oss"])
        self.assertEqual(got["agy-claude"]["seven_day"]["used_percentage"], 82.0)
        self.assertEqual(got["agy-claude"]["five_hour"]["used_percentage"], 100.0)
        self.assertEqual(got["agy-gpt-oss"], got["agy-claude"])
        self.assertEqual(got["agy-gemini"]["seven_day"]["used_percentage"], 3.0)
        self.assertEqual(got["agy-argon"], {"seven_day": {"used_percentage": 76.0, "resets_at": 1794951051.0}})
        self.assertEqual(pc.parse_agy_usage("I cannot show usage.\nSome\ttext\twithout\tnumbers"), {})

    @mock.patch.object(pc, "SPILL", True)
    def test_group_meters_steer_only_their_own_models(self):
        mdir = Path(TMP) / "meters3"
        mdir.mkdir(exist_ok=True)
        t = self.clock.t
        with mock.patch.object(pc, "_grok_usage_note", lambda: "no meter yet"), mock.patch.object(pc, "METER_DIR", mdir), mock.patch.object(pc, "_read_muse_usage", lambda: ""), \
                mock.patch.object(pc, "_read_agy_usage", lambda: "Claude and GPT models\tWeekly Limit Remaining\t8%\t2030-01-01T00:00:00Z\n"
                                                                 "Gemini Models\tWeekly Limit Remaining\t97%\t2030-01-01T00:00:00Z\n"
                                                                 "Gemini 4 Argon\tGemini 4 Argon Weekly Limit\t5%\t2030-01-01T00:00:00Z\n"):
            self.assertEqual(pc.refresh_meters(force=True), {"muse": [], "agy": ["agy-argon", "agy-claude", "agy-gemini", "agy-gpt-oss"], "grok": "no meter yet"})
            self.assertEqual(pc.meter_keys("agy/gemini-4-argon-high"), ["agy-argon", "agy-gemini"])
            self.assertTrue(pc.tight("agy/claude-opus-5-5-medium"))        # 92% of its week used
            self.assertTrue(pc.tight("agy/gemini-4-argon-high"))           # Argon's own weekly limit
            self.assertFalse(pc.tight("agy/gemini-3.8-flash-high"))
            self.assertFalse(pc.tight("claude-opus-5-5"))
            self.assertEqual(pc.route("agy/claude-opus-5-5-medium")[0], "claude-opus-5-5")   # nearly spent there: the Claude plan
            self.assertEqual(pc.route("claude-opus-5-5")[0], "claude-opus-5-5")
            pc.pause("claude", self.clock.now() + pc.timedelta(hours=2), "limit")
            self.assertEqual(pc.route("claude-opus-5-5")[0], "claude-opus-5-5")              # never onto a door whose meter is high
            self.assertIn("agy-claude", pc.status()["agy"]["group_meters"])
            self.assertIn("HIGH", pc.table())
            self.assertEqual(pc.refresh_meters(), {})                       # off in tests unless forced
        with mock.patch.object(pc, "_grok_usage_note", lambda: "no meter yet"), mock.patch.object(pc, "METER_DIR", mdir), mock.patch.object(pc, "_read_muse_usage", side_effect=OSError("no muse")), \
                mock.patch.object(pc, "_read_agy_usage", lambda: ""):
            got = pc.refresh_meters(force=True)                             # a failing reader is not an error
            self.assertIn("muse_error", got)
            self.assertTrue((mdir / "agy-claude.json").exists())            # and the last good reading stays

    def test_meter_read_never_starts_an_agy_sign_in(self):
        # 2026-11-11: a meter read on a Mac with no lane sign-in opened a Google sign-in window. No token, no call.
        home = Path(tempfile.mkdtemp())
        ran = []
        with mock.patch.object(pc, "AGY_HOME", home / "lane"), mock.patch.object(pc, "AGY_CWD", home / "lane" / "work"), \
                mock.patch.object(pc.subprocess, "run", lambda *a, **k: ran.append(a) or mock.Mock(stdout="{}")):
            self.assertFalse(pc.agy_signed_in())
            self.assertEqual(pc._read_agy_usage(), "")
            self.assertEqual(ran, [])                                   # agy was not started
            self.assertFalse((home / "lane").exists())                  # and the lane home was not created
            tok = home / "lane" / ".gemini" / "antigravity-cli"
            tok.mkdir(parents=True)
            (tok / "antigravity-oauth-token").write_text("x")
            self.assertFalse(pc.agy_signed_in())                        # no work folder yet: still not a lane
            (home / "lane" / "work").mkdir()
            self.assertTrue(pc.agy_signed_in())

    def test_lane_refusal_spends_no_budget(self):
        with mock.patch.object(pc, "_run_cursor", lambda *a: ("cursor lane folder /x is not private to this user; refusing", True)):
            r = pc.chat("cursor/composer-2.5", [{"role": "user", "content": "x"}])
        self.assertIn("call failed", r["error"])
        self.assertEqual(json.loads(pc.STATE.read_text()).get("cursor", {}).get("calls_total", 0), 0)

    def test_non_limit_error_is_returned_not_waited(self):
        with mock.patch.object(pc, "_run_claude", lambda *a: ("overloaded", True)):
            r = pc.chat("claude-haiku-5-5", [{"role": "user", "content": "x"}])
        self.assertIn("call failed", r["error"])
        self.assertLess(self.clock.t - NOW.timestamp(), 5)


class CursorLane(unittest.TestCase):
    """The lane folder: outside HOME, private, every tool denied (tested against the real CLI 2026-11-11)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=os.confstr(65537))  # per-user temp, outside HOME like the real lane
        self.dir = Path(self.tmp) / "lane"
        self.p = mock.patch.object(pc, "CURSOR_DIR", self.dir)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_first_use_writes_deny_all_settings(self):
        self.assertEqual(pc._cursor_lane(), "")
        cfg = json.loads((self.dir / ".cursor" / "cli.json").read_text())
        self.assertEqual(cfg["permissions"]["allow"], [])
        self.assertTrue(set(pc.CURSOR_DENY_ALL) <= set(cfg["permissions"]["deny"]))
        self.assertEqual(self.dir.stat().st_mode & 0o077, 0)

    def test_refuses_a_folder_under_home(self):
        with mock.patch.object(pc, "CURSOR_DIR", Path.home() / ".cache" / "never-made-cursor-lane"):
            self.assertIn("under HOME", pc._cursor_lane())
        self.assertFalse((Path.home() / ".cache" / "never-made-cursor-lane").exists())

    def test_refuses_weakened_settings_or_extra_files(self):
        pc._cursor_lane()
        cfg = self.dir / ".cursor" / "cli.json"
        cfg.write_text(json.dumps({"permissions": {"allow": ["Read(**)"], "deny": pc.CURSOR_DENY_ALL}}))
        self.assertIn("deny every tool", pc._cursor_lane())
        cfg.write_text(json.dumps({"permissions": {"allow": [], "deny": ["Shell(*)"]}}))
        self.assertIn("deny every tool", pc._cursor_lane())
        cfg.write_text(json.dumps({"permissions": {"allow": [], "deny": pc.CURSOR_DENY_ALL}}))
        (self.dir / "AGENTS.md").write_text("do things")
        self.assertIn("must hold only", pc._cursor_lane())

    def test_refuses_a_shared_folder(self):
        pc._cursor_lane()
        os.chmod(self.dir, 0o755)
        self.assertIn("not private", pc._cursor_lane())

    def test_run_reads_result_and_passes_no_tool_flags(self):
        seen = {}

        def fake_run(cmd, **kw):
            seen["cmd"], seen["input"] = cmd, kw.get("input")
            return mock.Mock(stdout=json.dumps({"type": "result", "is_error": False, "result": '{"ok": true}'}),
                             stderr="", returncode=0)
        with mock.patch.object(pc.subprocess, "run", fake_run):
            text, err = pc._run_cursor("cursor/composer-2.5", "SYS", "USER")
        self.assertEqual((text, err), ('{"ok": true}', False))
        cmd = seen["cmd"]
        self.assertEqual(cmd[cmd.index("--mode") + 1], "ask")
        self.assertEqual(cmd[cmd.index("--model") + 1], "composer-2.5")
        for flag in ("--force", "--yolo", "-f", "--approve-mcps"):
            self.assertNotIn(flag, cmd)
        self.assertIn("SYS", seen["input"])
        self.assertIn("USER", seen["input"])

    def test_run_plain_text_error_is_an_error(self):
        out = mock.Mock(stdout="ActionRequiredError: GPT-5.5 is not included in your weekly usage", stderr="", returncode=1)
        with mock.patch.object(pc.subprocess, "run", lambda *a, **k: out):
            text, err = pc._run_cursor("cursor/composer-2.5", "", "x")
        self.assertTrue(err)
        self.assertIsNotNone(pc.cursor_reset(text, NOW))


if __name__ == "__main__":
    unittest.main()


class AgyKeychainSandboxTest(unittest.TestCase):
    """11 Nov 2026: agy's hourly login save raised a "Keychain Not Found" box on the owner's screen."""

    def test_sandbox_blocks_security_tool_only(self):
        import subprocess as sp
        ok = sp.run([pc.SANDBOX_EXEC, "-p", pc.AGY_SANDBOX, "/bin/echo", "hi"], capture_output=True, text=True)
        self.assertEqual(ok.stdout.strip(), "hi")
        blocked = sp.run([pc.SANDBOX_EXEC, "-p", pc.AGY_SANDBOX, "/usr/bin/security", "help"],
                         capture_output=True, text=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("Operation not permitted", blocked.stderr)

    def test_every_agy_call_runs_in_the_sandbox(self):
        import tempfile
        from pathlib import Path
        seen = {}

        class R:
            returncode, stdout, stderr = 0, '{"status": "SUCCESS", "response": "ok"}', ""

        def fake_run(cmd, **kw):
            seen["cmd"] = cmd
            return R()

        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"
            cfg = home / ".gemini" / "antigravity-cli"
            cfg.mkdir(parents=True)
            (cfg / "settings.json").write_text(json.dumps({"permissions": {"deny": sorted(pc.AGY_DENY_ALL)}}))
            with mock.patch.object(pc, "AGY_HOME", home), mock.patch.object(pc, "AGY_CWD", home / "work"), \
                    mock.patch.object(pc.subprocess, "run", fake_run):
                text, err = pc._run_agy("agy/gemini-4-argon-low", "", "hello")
        self.assertEqual((text, err), ("ok", False))
        self.assertEqual(seen["cmd"][:3], [pc.SANDBOX_EXEC, "-p", pc.AGY_SANDBOX])
        self.assertEqual(seen["cmd"][3], pc.AGY)
