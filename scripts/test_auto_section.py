"""Offline driver-logic tests: auto_section with mocked CLIs."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import auto_section as driver


class FakeProc:
    def __init__(self, rc, out=""):
        self.returncode = rc
        self.stdout = out
        self.stderr = ""


def summary(path, ok=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"results": [], "ok": ok}))


class DriverTests(unittest.TestCase):
    def run_driver(self, argv, scripts):
        with patch.object(sys, "argv", ["auto_section.py"] + argv), \
             patch.object(driver.subprocess, "run",
                          side_effect=[FakeProc(*s) for s in scripts]) as run, \
             patch.object(driver, "latest_receipt",
                          return_value=Path("/tmp/fake/summary.json")):
            return driver.main(), run

    def test_promote_first_try(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [(0, "draft ok"), (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 3)
        self.assertIn("draft_claim.py", run.call_args_list[0][0][0][1])
        self.assertIn("--no-mark-done", run.call_args_list[1][0][0])
        self.assertNotIn("--no-mark-done", run.call_args_list[2][0][0])

    def test_revise_then_promote(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a", "--rounds", "2"],
            [(0, "draft"), (1, "hold"), (0, "revised"),
             (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 5)
        self.assertIn("--revise-from", run.call_args_list[2][0][0])

    def test_hold_after_rounds(self):
        rc, _run = self.run_driver(
            ["--claim", "c", "--agent", "a", "--rounds", "1"],
            [(0, "draft"), (1, "hold"), (0, "revised"), (1, "hold")])
        self.assertEqual(rc, 1)

    def test_draft_fail_holds(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"], [(1, "draft fail")])
        self.assertEqual(rc, 1)
        self.assertEqual(run.call_count, 1)

    def test_api_fail_exits_2(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [(0, "draft"), (2, "api down"), (2, "still down")])
        self.assertEqual(rc, 2)
        self.assertEqual(run.call_count, 3)

    def test_api_retry_recovers(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [(0, "draft"), (2, "api down"), (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 4)


if __name__ == "__main__":
    unittest.main()
