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


# main() tries --accept-current before anything else (since 2026-10-03). These scripts open with its refusal.
REFUSED = (1, "nothing to accept")


class DriverTests(unittest.TestCase):
    def run_driver(self, argv, scripts, fresh_draft=True, source_not_greek=False):
        """fresh_draft and source_not_greek replace the checks that read the real claim board and book."""
        with patch.object(sys, "argv", ["auto_section.py"] + argv), \
             patch.object(driver.subprocess, "run",
                          side_effect=[FakeProc(*s) for s in scripts]) as run, \
             patch.object(driver, "_source_not_greek", return_value=source_not_greek), \
             patch.object(driver, "_needs_fresh_draft", return_value=fresh_draft), \
             patch.object(driver, "latest_receipt",
                          return_value=Path("/tmp/fake/summary.json")):
            return driver.main(), run

    def test_accepts_current_without_drafting(self):
        rc, run = self.run_driver(["--claim", "c", "--agent", "a"], [(0, "accepted")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 1)
        self.assertIn("--accept-current", run.call_args_list[0][0][0])

    def test_source_not_greek_skips_without_a_call(self):
        rc, run = self.run_driver(["--claim", "c", "--agent", "a"], [], source_not_greek=True)
        self.assertEqual(rc, 5)
        self.assertEqual(run.call_count, 0)

    def test_failing_receipt_is_revised_not_redrafted(self):
        with patch.object(driver, "receipt_needs_repair", return_value=Path("/tmp/fake/summary.json")):
            rc, run = self.run_driver(
                ["--claim", "c", "--agent", "a"],
                [REFUSED, (0, "revised"), (0, "promote ok"), (0, "marked")], fresh_draft=False)
        self.assertEqual(rc, 0)
        self.assertIn("--revise-from", run.call_args_list[1][0][0])

    def test_promote_first_try(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [REFUSED, (0, "draft ok"), (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 4)
        self.assertIn("draft_claim.py", run.call_args_list[1][0][0][1])
        self.assertIn("--no-mark-done", run.call_args_list[2][0][0])
        self.assertNotIn("--no-mark-done", run.call_args_list[3][0][0])

    def test_revise_then_promote(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a", "--rounds", "2"],
            [REFUSED, (0, "draft"), (1, "hold"), (0, "revised"),
             (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 6)
        self.assertIn("--revise-from", run.call_args_list[3][0][0])

    def test_hold_after_rounds(self):
        rc, _run = self.run_driver(
            ["--claim", "c", "--agent", "a", "--rounds", "1"],
            [REFUSED, (0, "draft"), (1, "hold"), (0, "revised"), (1, "hold")])
        self.assertEqual(rc, 1)

    def test_draft_fail_holds(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"], [REFUSED, (1, "draft fail")])
        self.assertEqual(rc, 1)
        self.assertEqual(run.call_count, 2)

    def test_api_fail_exits_2(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [REFUSED, (0, "draft"), (2, "api down"), (2, "still down")])
        self.assertEqual(rc, 2)
        self.assertEqual(run.call_count, 4)

    def test_api_retry_recovers(self):
        rc, run = self.run_driver(
            ["--claim", "c", "--agent", "a"],
            [REFUSED, (0, "draft"), (2, "api down"), (0, "promote ok"), (0, "marked")])
        self.assertEqual(rc, 0)
        self.assertEqual(run.call_count, 5)


if __name__ == "__main__":
    unittest.main()
