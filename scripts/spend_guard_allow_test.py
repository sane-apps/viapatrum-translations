#!/usr/bin/env python3
"""Tests for the owner allow list on the Cloudflare AI switch (spend_guard.CF_AI_ALLOW). No network, no spend.

  python3 scripts/spend_guard_allow_test.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spend_guard as G  # noqa: E402


class Allow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.saved = (G.CF_AI_OFF, G.CF_AI_ALLOW, G.HOLD)
        G.CF_AI_OFF, G.CF_AI_ALLOW, G.HOLD = d / "OFF", d / "ALLOW", d / "hold"
        G.CF_AI_OFF.write_text("off")

    def tearDown(self):
        G.CF_AI_OFF, G.CF_AI_ALLOW, G.HOLD = self.saved
        self.tmp.cleanup()

    def test_switch_refuses_everyone_without_an_allow_file(self):
        self.assertIn("switched off", G.hold_reason("search_sync.ai"))
        self.assertIn("switched off", G.hold_reason())

    def test_named_caller_passes_the_switch_others_do_not(self):
        G.CF_AI_ALLOW.write_text("search_sync.ai\tYes it's Pennys\t2026-11-04\n")
        self.assertEqual(G.hold_reason("search_sync.ai"), "")
        self.assertIn("switched off", G.hold_reason("cf_tts"))
        self.assertIn("switched off", G.hold_reason(""))

    def test_line_without_owner_words_does_not_count(self):
        G.CF_AI_ALLOW.write_text("search_sync.ai\n# search_sync.ai\tcomment\nsearch_sync.ai\t\t2026-11-04\n")
        self.assertIn("switched off", G.hold_reason("search_sync.ai"))

    def test_owner_hold_still_applies_to_an_allowed_caller(self):
        G.CF_AI_ALLOW.write_text("search_sync.ai\tYes it's Pennys\t2026-11-04\n")
        G.HOLD.write_text("owner says stop")
        self.assertIn("owner hold", G.hold_reason("search_sync.ai"))

    def test_allow_and_reserve_pass_the_caller(self):
        ok, why = G.allow("cf_tts")
        self.assertFalse(ok)
        self.assertIn("switched off", why)
        ok, why = G.reserve("cf_tts", 0.001)
        self.assertFalse(ok)
        self.assertIn("switched off", why)


if __name__ == "__main__":
    unittest.main()
