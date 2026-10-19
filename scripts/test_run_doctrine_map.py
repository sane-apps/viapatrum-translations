#!/usr/bin/env python3
"""run-doctrine-map.sh: a failed or skipped grade must not rewrite the site map.

2026-10-07: the 03:30 run skipped grading (a referee receipt failed), then the
report step rewrote doctrine_map.json anyway, dropping graded passages and
stamping today's date. The runner runs here under a fake HOME: receipt
refreshes and doctrine_map.py are stubs that only record which steps ran.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "run-doctrine-map.sh"
REFRESH_STUB = """KW='{}'
refresh() { case "$1" in *nemotron*) [ -n "${FAIL_REFEREE:-}" ] && { echo "receipt FAILED $1"; return 1; } ;; esac; return 0; }
"""
PY_STUB = """#!/bin/bash
echo "$2" >> "$STEPS"
[ "$2" = grade ] && [ -n "${FAIL_GRADE:-}" ] && exit 1
[ "$2" = grade ] && [ -n "${PARTIAL_GRADE:-}" ] && exit 3
exit 0
"""

SPEND_STUB = """import os, sys
sys.exit(10 if os.environ.get("SPEND_OVER") and sys.argv[1:] == ["check"] else 0)
"""


class RunnerTests(unittest.TestCase):
    def run_job(self, **env):
        with tempfile.TemporaryDirectory() as home:
            h = Path(home)
            scripts = h / "SaneApps/clients/translations/scripts"
            scripts.mkdir(parents=True)
            (scripts / "receipt_refresh.sh").write_text(REFRESH_STUB)
            (scripts / "spend_guard.py").write_text(SPEND_STUB)
            (h / ".config/nv").mkdir(parents=True)
            (h / ".config/nv/env").write_text("")
            py = h / "Models/kokoro/.venv/bin/python"
            py.parent.mkdir(parents=True)
            py.write_text(PY_STUB)
            py.chmod(0o755)
            steps = h / "steps.txt"
            e = dict(os.environ, HOME=home, STEPS=str(steps), BELIEFS_LOCK=str(h / "lock"), **env)
            p = subprocess.run(["bash", str(SCRIPT)], env=e, capture_output=True, text=True, timeout=60)
            ran = steps.read_text().split() if steps.exists() else []
            return p.returncode, ran, p.stdout

    def test_all_good_runs_report(self):
        rc, ran, _ = self.run_job()
        self.assertEqual((rc, ran), (0, ["index", "search", "grade", "report"]))

    def test_skipped_grade_keeps_last_map(self):
        rc, ran, out = self.run_job(FAIL_REFEREE="1")
        self.assertEqual((rc, ran), (1, ["index", "search"]))
        self.assertIn("report SKIPPED", out)

    def test_failed_grade_keeps_last_map(self):
        rc, ran, out = self.run_job(FAIL_GRADE="1")
        self.assertEqual((rc, ran), (1, ["index", "search", "grade"]))
        self.assertIn("report SKIPPED", out)

    def test_grade_out_of_time_is_progress_and_keeps_last_map(self):
        # 2026-10-19: doctrine_map.py grade exits 3 when its time budget ran
        # out after saving some grades; the rest wait for the next run.
        rc, ran, out = self.run_job(PARTIAL_GRADE="1")
        self.assertEqual((rc, ran), (0, ["index", "search", "grade"]))
        self.assertIn("grade INCOMPLETE", out)
        self.assertIn("report SKIPPED: grading is not finished yet", out)

    def test_over_the_spending_cap_runs_nothing_and_keeps_the_map(self):
        rc, ran, out = self.run_job(SPEND_OVER="1")
        self.assertEqual((rc, ran), (0, []))
        self.assertIn("skipped for today", out)


if __name__ == "__main__":
    unittest.main()
