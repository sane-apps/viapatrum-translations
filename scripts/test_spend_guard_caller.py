#!/usr/bin/env python3
"""spend_guard check --caller NAME: the owner's CLOUDFLARE_AI_ALLOW lines can lift the switch for a named job."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

D = Path(tempfile.mkdtemp())
(D / "OFF").write_text("off for test")
(D / "ALLOW").write_text("*\tuse cf as needed (owner)\t2026-11-04\n")
os.environ["SANE_CF_AI_OFF_FILE"], os.environ["SANE_CF_AI_ALLOW_FILE"] = str(D / "OFF"), str(D / "ALLOW")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import spend_guard as S  # noqa: E402


class Caller(unittest.TestCase):
    def test_unnamed_check_is_refused_by_the_switch(self):
        self.assertIn("switched off", S.hold_reason(""))

    def test_named_caller_passes_the_switch(self):
        self.assertNotIn("switched off", S.hold_reason("fathers-audio-next"))

    def test_cli_passes_the_caller_through(self):
        seen = []
        real = S.hold_reason
        S.hold_reason = lambda caller="": seen.append(caller) or "held for test"
        try:
            S.main(["spend_guard.py", "check", "--caller", "fathers-audio-next"])
        finally:
            S.hold_reason = real
        self.assertEqual(seen[0], "fathers-audio-next")


if __name__ == "__main__":
    unittest.main()
