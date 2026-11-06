#!/usr/bin/env python3
"""Offline tests for strong_check.py. Model calls are stubbed; nothing leaves this machine.
Run: python3 scripts/test_strong_check.py
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strong_check as S  # noqa: E402


FINDING = {"quote": "the Lord said", "problem": "wrong speaker"}


def judged(refuted):
    return [{**FINDING, "verdict": {"refuted": refuted, "correction_ok": False, "reason": ""}}]


class QuoteIn(unittest.TestCase):
    def test_exact_case_and_curly_quotes(self):
        self.assertTrue(S.quote_in("The Lord’s word", "and the lord's word stood"))

    def test_absent_quote_fails(self):
        self.assertFalse(S.quote_in("a sentence not there", "something else entirely"))

    def test_very_short_quote_fails(self):
        self.assertFalse(S.quote_in("a", "a b c"))

    def test_ellipsis_needs_every_piece(self):
        text = "first long clause here and later second long clause here"
        self.assertTrue(S.quote_in("first long clause ... second long clause", text))
        self.assertFalse(S.quote_in("first long clause ... missing long clause", text))


class CheckText(unittest.TestCase):
    def run_check(self, found, skeptic):
        with mock.patch.object(S, "find", return_value=found), mock.patch.object(S, "skeptic", return_value=skeptic):
            return S.check_text("s1", "source", "english")

    def test_finder_down_fails_closed(self):
        res = self.run_check(None, [])
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "finder unavailable")

    def test_skeptic_down_fails_closed(self):
        res = self.run_check([FINDING], None)
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "skeptic unavailable")

    def test_unrefuted_finding_stands(self):
        res = self.run_check([FINDING], judged(False))
        self.assertFalse(res["ok"])
        self.assertEqual(len(res["standing"]), 1)

    def test_refuted_finding_clears(self):
        res = self.run_check([FINDING], judged(True))
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["refuted"]), 1)


class Skeptic(unittest.TestCase):
    def test_missing_ruling_never_clears_a_finding(self):
        with mock.patch.object(S, "claude", return_value='{"verdicts": [{"n": 2, "refuted": true}]}'):
            out = S.skeptic("s1", "source", "english", [FINDING])
        self.assertFalse(out[0]["verdict"]["refuted"])


if __name__ == "__main__":
    unittest.main()
