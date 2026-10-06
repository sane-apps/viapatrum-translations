#!/usr/bin/env python3
"""Tests for scripts/fathers_watch.py (the one Fathers monitor). Offline:
launchctl, the broker, ps and lsof are mocked; all paths live in a temp dir."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fathers_watch as W  # noqa: E402

HELD = "com.saneapps.fathers-held-review"
BROKER = "com.saneapps.cf-batch-broker"


def hhmmss(ago_s: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(time.time() - ago_s))


class WatchTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.la, self.logs, self.wp = root / "LaunchAgents", root / "Logs", root / "repo/outputs/work-pipeline"
        self.site, self.out = root / "site", root / "repo/outputs/fathers-watch"
        for d in (self.la, self.logs, self.wp, self.site / "outputs/e2e", self.out, root / "repo/scripts"):
            d.mkdir(parents=True)
        for name in ("fathers-recert", "fathers-beliefs", "fathers-held-review", "fathers-watch"):
            (self.la / f"com.saneapps.{name}.plist").write_text("x")
        (self.la / f"{BROKER}.plist").write_text("x")
        (self.la / "com.saneapps.fathers-overnight-quota.plist.disabled").write_text("x")
        (self.la / "com.saneapps.fathers-e2e.plist.bak-20260928").write_text("x")
        (root / "repo/scripts/run-recert-lanes.sh").write_text(
            "for n in 1 2; do lane C$n --x; done\nfor n in 1; do lane E$n --y; done\n")
        (self.site / "outputs/e2e/LATEST.json").write_text(json.dumps({"rc": 0, "live_works": 3}))
        self.states = {"com.saneapps.fathers-recert": ("-", "0"), "com.saneapps.fathers-beliefs": ("-", "0"),
                       HELD: ("-", "0"), BROKER: ("4242", "-15")}
        self.launchctl = mock.MagicMock(side_effect=lambda: self.states)
        patches = {"LA": self.la, "LOGS": self.logs, "WP": self.wp, "SITE": self.site, "REPO": root / "repo",
                   "OUT": self.out, "STATUS": self.out / "status.json", "ALERTS_LOG": self.out / "alerts.log",
                   "RUN_LOCK": self.out / "watch.lock", "launchctl_states": self.launchctl,
                   "broker_stats": lambda: {"errors": 0}, "ship_ps": lambda: "", "ship_lock_holders": lambda: []}
        for k, v in patches.items():
            p = mock.patch.object(W, k, v)
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)
        W.PRIOR = {}

    def write_queue(self, rows: dict):
        (self.wp / "queue.json").write_text(json.dumps(rows))


class JobsTests(WatchTestBase):
    def test_live_jobs_from_plists_skip_retired_backup_and_self(self):
        self.assertEqual(W.live_jobs(), ["com.saneapps.fathers-beliefs", HELD,
                                         "com.saneapps.fathers-recert", BROKER])

    def test_retired_overnight_checks_are_skipped(self):
        self.assertTrue(W.overnight_retired())
        for fn in (W.check_burn, W.check_quota, W.check_holds):
            self.assertEqual(fn()[0], "ok", fn.__name__)

    def test_held_review_exit_3_is_its_own_fail(self):
        self.states[HELD] = ("-", "3")
        self.assertEqual(W.check_jobs()[0], "ok")  # running broker's old -15 and exit 3 not double-counted
        state, detail, _ = W.check_held_review()
        self.assertEqual(state, "fail")
        self.assertIn("Claude not signed in", detail)

    def test_missing_and_failed_jobs(self):
        del self.states["com.saneapps.fathers-recert"]
        self.assertEqual(W.check_jobs()[0], "fail")
        self.states["com.saneapps.fathers-recert"] = ("-", "1")
        self.assertEqual(W.check_jobs()[:2], ("warn", "nonzero last exit: fathers-recert=1"))


class LogCheckTests(WatchTestBase):
    def test_beliefs_failed_step_in_last_run_only(self):
        log = self.logs / "fathers-beliefs.log"
        log.write_text("03:30:00 index\n03:35:33 grade\nBLOCKED: receipt expired\n03:35:34 grade FAILED\n03:35:34 report\n")
        state, detail, _ = W.check_beliefs()
        self.assertEqual(state, "warn")
        self.assertIn("grade FAILED", detail)
        with log.open("a") as fh:
            fh.write("03:30:01 receipt refreshed kimi\n03:30:02 index\n03:31:00 grade\n03:32:00 report\n")
        self.assertEqual(W.check_beliefs()[0], "ok")
        with log.open("a") as fh:
            fh.write("03:30:01 receipt FAILED kimi\n03:30:02 index\n03:31:00 grade FAILED: receipt refresh failed\n")
        self.assertEqual(W.check_beliefs()[0], "warn")

    def test_recert_receipt_needs_two_failures_in_a_row(self):
        log = self.logs / "fathers-recert.out.log"
        log.write_text(f"{hhmmss(3600)} receipt FAILED kimi\n{hhmmss(1800)} receipt refreshed kimi\n"
                       f"{hhmmss(60)} status site unchanged, skip deploy\n")
        self.assertEqual(W.check_recert()[0], "ok")
        log.write_text(f"{hhmmss(3600)} receipt FAILED kimi\n{hhmmss(1800)} receipt FAILED kimi\n"
                       f"{hhmmss(60)} status site deploy FAILED\n")
        state, detail, _ = W.check_recert()
        self.assertEqual(state, "warn")
        self.assertIn("receipt FAILED twice in a row: kimi", detail)
        self.assertIn("status site deploy FAILED", detail)

    def test_redraft_loop_in_latest_run(self):
        d = self.wp / "book-a"
        d.mkdir()
        loop = "".join(f"10:0{i}:00 1: source changed since it passed; redrafting\n" for i in range(3))
        (d / "run.log").write_text("09:00:00 start: 4 sections\n" + loop + "11:00:00 start: 4 sections\n")
        self.assertEqual(W.check_redraft()[0], "ok")  # loop was in an older run
        with (d / "run.log").open("a") as fh:
            fh.write(loop)
        state, detail, _ = W.check_redraft()
        self.assertEqual(state, "warn")
        self.assertIn("book-a (1 sections, up to x3)", detail)


class QueueTests(WatchTestBase):
    def test_certified_floor_and_pause(self):
        old = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 8 * 3600))
        new = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 600))
        self.write_queue({"a": {"result": "certified", "at": old}})
        self.assertEqual(W.check_certified()[0], "warn")
        self.assertEqual(W.check_progress()[0], "warn")
        (self.wp / "lanes.paused").write_text("owner")
        self.assertEqual(W.check_certified()[0], "ok")
        self.assertEqual(W.check_lanes()[0], "ok")
        (self.wp / "lanes.paused").unlink()
        self.write_queue({"a": {"result": "certified", "at": new}})
        self.assertEqual(W.check_certified()[0], "ok")
        self.assertEqual(W.check_progress()[0], "ok")

    def test_lanes_count_from_runner(self):
        self.assertEqual(W.expected_lanes(), 3)
        (self.wp / "lane-C1.pid").write_text(str(os.getpid()))
        self.assertEqual(W.check_lanes()[:2], ("warn", "only 1/3 lanes alive"))


class AlertLogTests(WatchTestBase):
    def run_main(self):
        W.PRIOR = {}
        with mock.patch("builtins.print"):
            self.assertEqual(W.main(), 0)
        return json.loads((self.out / "status.json").read_text())

    def test_alerts_log_only_on_state_change_and_schema_kept(self):
        self.states[HELD] = ("-", "3")
        st = self.run_main()
        self.assertEqual(set(st), {"checked_at", "overall", "checks", "alerts", "heals", "healed_burn_hung"})
        self.assertEqual(st["overall"], "fail")
        ids = {a["id"] for a in st["alerts"]}
        self.assertIn("held-review:claude", ids)
        self.assertNotIn("quota:stale", ids)
        first = (self.out / "alerts.log").read_text()
        self.assertIn("fail held-review:claude", first)
        self.run_main()
        self.assertEqual((self.out / "alerts.log").read_text(), first)  # same state: no new lines
        self.states[HELD] = ("-", "0")
        self.run_main()
        self.assertIn("cleared held-review:claude", (self.out / "alerts.log").read_text())


if __name__ == "__main__":
    unittest.main()
