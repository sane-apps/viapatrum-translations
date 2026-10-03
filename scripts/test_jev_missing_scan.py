#!/usr/bin/env python3
"""Offline regressions for the missing-citation queue producer."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jev_missing_scan as ms


VERSES = [
    ("matt", 7, 15, "Beware of false prophets, which come to you in "
                    "sheep's clothing, but inwardly they are ravening wolves."),
    ("john", 3, 16, "For God so loved the world, that he gave his only "
                    "begotten Son, that whosoever believeth in him should "
                    "not perish, but have everlasting life."),
    ("gen", 1, 1, "In the beginning God created the heaven and the earth."),
]


class MissingScanTests(unittest.TestCase):
    def test_quoted_segments(self):
        segs = list(ms.quoted_segments(
            "He said, \u2018Take heed from the deceivers of old,\u2019 and left."))
        self.assertEqual(len(segs), 1)
        self.assertIn("Take heed", segs[0])
        self.assertEqual(list(ms.quoted_segments("No quotes here.")), [])
        self.assertEqual(list(ms.quoted_segments("Too short \u2018be glad\u2019.")), [])

    def test_uncited_quotes_skips_cited(self):
        paras = ["Wolves in sheep\u2019s (Matthew 7:15) clothing, beware all. "
                 "He said \u2018take heed from the deceivers of old\u2019 daily."]
        got = list(ms.uncited_quotes(paras))
        self.assertEqual(len(got), 1)
        self.assertIn("take heed", got[0][1])

    def test_uncited_quotes_skips_pending(self):
        paras = ["[English pending.] He said \u2018take heed from deceivers\u2019."]
        self.assertEqual(list(ms.uncited_quotes(paras)), [])

    def test_best_match_finds_verse(self):
        index = ms.build_index(VERSES)
        ref, shared = ms.best_match(
            "Take heed from those who come toward you in sheep\u2019s "
            "clothing, but inwardly they are rapacious wolves", index)
        self.assertEqual(ref, ("matt", 7, 15))
        self.assertGreaterEqual(shared, 4)

    def test_quoted_segments_ignores_possessive(self):
        # Live 2026-09-25: "Christ’s ..." seeded a phantom quote that
        # double-cited an already-cited sentence.
        segs = list(ms.quoted_segments(
            "We must all appear before Christ\u2019s judgment seat, so that "
            "each may receive what belongs to his own body, according to "
            "what he has done, whether good or evil."))
        self.assertEqual(segs, [])

    def test_quoted_segments_keeps_apostrophe_in_quote(self):
        segs = list(ms.quoted_segments(
            "He said \u2018take heed, don't fear the wolves of old\u2019 daily."))
        self.assertEqual(len(segs), 1)
        self.assertIn("don't fear", segs[0])

    def test_quoted_segments_catches_unclosed(self):
        segs = list(ms.quoted_segments(
            "It is written thus: \u2018and after these things Moses and Aaron "
            "went in to Pharaoh, and said words unto him"))
        self.assertEqual(len(segs), 1)
        self.assertIn("Moses and Aaron", segs[0])

    def test_quoted_segments_closes_before_emdash(self):
        segs = list(ms.quoted_segments(
            "\u2018lacking, afflicted, mistreated, wandering upon deserts'"
            "\u2014when there were many synagogues."))
        self.assertEqual(len(segs), 1)
        self.assertTrue(segs[0].endswith("deserts"))
        self.assertNotIn("synagogues", segs[0])

    def test_best_match_no_match(self):
        index = ms.build_index(VERSES)
        ref, shared = ms.best_match("xyzzy plugh frobnicate wobble", index)
        self.assertIsNone(ref)
        self.assertEqual(shared, 0)


if __name__ == "__main__":
    unittest.main()
