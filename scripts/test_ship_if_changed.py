#!/usr/bin/env python3
"""Tests for scripts/ship_if_changed.py (the change-gated auto ship). Offline:
ship.sh, the shelf steps, git, the disk and the build lock are faked; every
path lives in a temp dir. Run: python3 scripts/test_ship_if_changed.py"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ship_if_changed as S  # noqa: E402

REAL_RUN = subprocess.run  # the base class patches subprocess.run per test


class AutoShipTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.site, self.out = root / "site", root / "repo/outputs/ship-auto"
        (self.site / "outputs/ship-last/dist/app/v1").mkdir(parents=True)
        (self.site / "outputs/ship-last/dist/app/v1/catalog.json").write_text("{}")
        self.receipt = self.site / "outputs/ship-last/receipt.json"
        self.receipt.write_text(json.dumps({"shipped_at": "old", "verified": True}))
        os.utime(self.receipt, (1, 1))
        self.now = {"text": "t2", "audio": "a1", "library": "l1"}
        self.git = subprocess.CompletedProcess([], 0, "", "")
        self.cmds: list[str] = []
        self.fail_step = None  # shelf step name that returns rc 1
        self.ship_verifies = True
        patches = {"SITE": self.site, "OUT": self.out, "STATE": self.out / "state.json",
                   "RUN_LOCK": self.out / "run.lock", "BUILD_LOCK": self.site / "outputs/build.lock",
                   "DRY": False, "LOCK_WAIT_S": 0, "inputs": lambda: dict(self.now),
                   "free_gb": lambda: 100, "take_build_lock": lambda: True,
                   "run": self.fake_run, "with_token": self.fake_run}
        for k, v in patches.items():
            p = mock.patch.object(S, k, v)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(S.subprocess, "run", lambda *a, **k: self.git)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(S, "log", lambda msg: None)
        p.start()
        self.addCleanup(p.stop)
        self.out.mkdir(parents=True)
        self.write_state({"shipped": {"text": "t1", "audio": "a1", "library": "l1"}})

    def write_state(self, st: dict):
        (self.out / "state.json").write_text(json.dumps(st))

    def state(self) -> dict:
        return json.loads((self.out / "state.json").read_text())

    def fake_run(self, cmd, timeout, cwd=None):
        text = cmd if isinstance(cmd, str) else " ".join(cmd)
        self.cmds.append(text)
        if "ship.sh" in text:
            if self.ship_verifies:
                self.receipt.write_text(json.dumps({"shipped_at": "new", "verified": True}))
            return 0 if self.ship_verifies else 1
        for name, needle in (("ebooks", "build_ebooks"), ("audiobooks", "build_audiobooks"),
                             ("word", " word "), ("assemble", " assemble"),
                             ("upload-direct", "--direct"), ("upload-large", "--base")):
            if needle in text:
                return 1 if self.fail_step == name else 0
        return 0


class ExitCodeTests(AutoShipTestBase):
    def test_failed_shelf_keeps_pending_and_exits_3(self):
        self.fail_step = "audiobooks"
        self.assertEqual(S.main(), S.EXIT_SHELF)
        st = self.state()
        self.assertEqual(st["shipped"], self.now)  # the site ship itself verified
        self.assertEqual(st["shelf_pending"]["done"], ["ebooks"])
        self.assertEqual(st["shelf_pending"]["error"], "audiobooks rc=1")
        self.assertEqual(st["last_run"]["exit"], S.EXIT_SHELF)
        self.assertFalse((self.out / "run.lock").exists())

    def test_next_run_resumes_shelf_at_failed_step(self):
        self.fail_step = "audiobooks"
        S.main()
        self.fail_step, self.cmds = None, []
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertFalse(any("build_ebooks" in c for c in self.cmds))
        self.assertTrue(any("build_audiobooks" in c for c in self.cmds))
        self.assertFalse(any("ship.sh" in c for c in self.cmds))  # nothing changed, nothing shipped
        st = self.state()
        self.assertNotIn("shelf_pending", st)
        self.assertTrue(st["last_shelf"]["ok"])

    def test_failed_upload_after_assemble_blocks_the_next_ship(self):
        self.fail_step = "upload-direct"
        S.main()
        self.now = {"text": "t3", "audio": "a1", "library": "l2"}
        self.cmds = []
        self.assertEqual(S.main(), S.EXIT_SHELF)
        self.assertFalse(any("ship.sh" in c for c in self.cmds))
        self.assertEqual(self.state()["pending"], ["text", "library"])

    def test_library_only_ship_starts_no_new_shelf(self):
        self.write_state({"shipped": {"text": "t2", "audio": "a1", "library": "l0"}})
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertTrue(any("ship.sh" in c for c in self.cmds))
        self.assertFalse(any("build_ebooks" in c for c in self.cmds))
        self.assertNotIn("shelf_pending", self.state())

    def test_unverified_ship_exits_1_and_keeps_pending(self):
        self.ship_verifies = False
        self.assertEqual(S.main(), S.EXIT_FAILED)
        st = self.state()
        self.assertEqual(st["pending"], ["text"])
        self.assertIn("pending_since", st)
        self.assertNotIn("ships", st)

    def test_skips_exit_2(self):
        self.git = subprocess.CompletedProcess([], 0, " M scripts/ship.sh\n", "")
        self.assertEqual(S.main(), S.EXIT_SKIPPED)
        self.assertIn("uncommitted site code", self.state()["last_skip"]["why"])
        self.git = subprocess.CompletedProcess([], 128, "", "fatal: not a git repository")
        self.assertEqual(S.main(), S.EXIT_SKIPPED)
        self.assertIn("git status failed", self.state()["last_run"]["why"])
        self.git = subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(S, "free_gb", lambda: 14):
            self.assertEqual(S.main(), S.EXIT_SKIPPED)
        with mock.patch.object(S, "take_build_lock", lambda: False):
            self.assertEqual(S.main(), S.EXIT_SKIPPED)
        self.assertIn("build.lock", self.state()["last_skip"]["why"])
        self.assertFalse(any("ship.sh" in c for c in self.cmds))

    def test_site_code_ship_does_not_rebuild_the_shelf(self):
        self.now = {"text": "t1", "audio": "a1", "library": "l1", "site": "new"}
        self.write_state({"shipped": {"text": "t1", "audio": "a1", "library": "l1", "site": "old"}})
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertTrue(any("ship.sh" in c for c in self.cmds))
        self.assertFalse(any("build_ebooks" in c for c in self.cmds))
        self.assertNotIn("shelf_pending", self.state())

    def test_a_prior_ship_count_does_not_block_the_next(self):
        today = S.time.strftime("%Y-%m-%d")
        self.write_state({"shipped": {"text": "t1", "audio": "a1", "library": "l1"}, "ships": {today: 2}})
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertTrue(any("ship.sh" in c for c in self.cmds))
        self.assertNotIn("ships", self.state())

    def test_no_change_exits_0(self):
        self.now = {"text": "t1", "audio": "a1", "library": "l1"}
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertEqual(self.cmds, [])


class LockTests(AutoShipTestBase):
    def test_live_run_lock_exits_75_and_dead_one_is_taken(self):
        (self.out / "run.lock").mkdir()
        (self.out / "run.lock/pid").write_text(f"{os.getpid()} {int(S.time.time())}\n")
        with mock.patch.object(S, "pid_command", lambda pid: "python ship_if_changed.py"):
            self.assertEqual(S.main(), S.EXIT_BUSY)
        self.assertTrue((self.out / "run.lock").exists())  # not ours to remove
        dead = subprocess.Popen(["true"])
        dead.wait()
        (self.out / "run.lock/pid").write_text(f"{dead.pid} 0\n")
        self.assertEqual(S.main(), S.EXIT_OK)
        self.assertFalse((self.out / "run.lock").exists())

    def test_lock_pid_reused_by_another_program_is_taken(self):
        # After a reboot the old pid can be any live process: not ours to wait on.
        (self.out / "run.lock").mkdir()
        (self.out / "run.lock/pid").write_text(f"{os.getpid()} {int(S.time.time())}\n")
        with mock.patch.object(S, "pid_command", lambda pid: "/usr/sbin/cfprefsd agent"):
            self.assertEqual(S.main(), S.EXIT_OK)
        self.assertFalse((self.out / "run.lock").exists())

    def test_lock_older_than_hard_limit_is_taken(self):
        (self.out / "run.lock").mkdir()
        old = int(S.time.time()) - S.RUN_HARD_LIMIT_S - 60
        (self.out / "run.lock/pid").write_text(f"{os.getpid()} {old}\n")
        with mock.patch.object(S, "pid_command", lambda pid: "python ship_if_changed.py"):
            self.assertEqual(S.main(), S.EXIT_OK)

    def test_ps_failure_keeps_a_young_live_lock(self):
        (self.out / "run.lock").mkdir()
        (self.out / "run.lock/pid").write_text(f"{os.getpid()} {int(S.time.time())}\n")
        with mock.patch.object(S, "pid_command", lambda pid: None):
            self.assertEqual(S.main(), S.EXIT_BUSY)

    def test_pid_command_reads_this_process(self):
        with mock.patch.object(S.subprocess, "run", REAL_RUN):
            self.assertIn("python", S.pid_command(os.getpid()).lower())

    def test_sigterm_clears_run_lock_and_keeps_shelf_pending(self):
        def killed_in_audiobooks(cmd, timeout, cwd=None):
            if "build_audiobooks" in (cmd if isinstance(cmd, str) else " ".join(cmd)):
                S.on_term(signal.SIGTERM, None)
            return self.fake_run(cmd, timeout, cwd)
        with mock.patch.object(S, "run", killed_in_audiobooks):
            with self.assertRaises(SystemExit) as cm:
                S.main()
        self.assertEqual(cm.exception.code, S.EXIT_TERM)
        self.assertFalse((self.out / "run.lock").exists())
        st = self.state()
        self.assertEqual(st["shelf_pending"]["done"], ["ebooks"])
        self.assertIn("killed (SIGTERM) during audiobooks", st["shelf_pending"]["error"])
        self.assertEqual(st["last_run"]["exit"], S.EXIT_TERM)


class SiteCodeGateTests(unittest.TestCase):
    """Real git: regenerated share cards do not block a ship; code does."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name)
        for rel in ("scripts/build.py", "assets/og/a.png", "assets/site.css"):
            (self.site / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.site / rel).write_text("v1")
        git = lambda *a: REAL_RUN(["git", "-C", str(self.site), *a], capture_output=True, check=True)  # noqa: E731
        git("init", "-q")
        git("add", ".")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        for k, v in {"SITE": self.site, "free_gb": lambda: 100}.items():
            p = mock.patch.object(S, k, v)
            p.start()
            self.addCleanup(p.stop)

    def test_share_cards_alone_do_not_block(self):
        (self.site / "assets/og/a.png").write_text("v2")
        (self.site / "assets/og/new.png").write_text("v1")
        self.assertIsNone(S.site_code_gate())

    def test_code_still_blocks(self):
        (self.site / "assets/og/a.png").write_text("v2")
        (self.site / "assets/site.css").write_text("v2")
        self.assertEqual(S.site_code_gate(), "uncommitted site code (1 paths: assets/site.css)")


if __name__ == "__main__":
    unittest.main()
