#!/usr/bin/env python3
"""Offline regressions for the Jev citation eval harness. Never calls the API."""
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jev_cite_eval as ev


def pos(slug, display, book="john"):
    return (slug, "s1", "clause words", (book, 3, 5), display, False)


class EvalHarnessTests(unittest.TestCase):
    def test_testament_split(self):
        self.assertEqual(ev.testament("ps"), "OT")
        self.assertEqual(ev.testament("john"), "NT")
        self.assertEqual(ev.testament("wis"), "OT")
        self.assertEqual(ev.testament("rev"), "NT")

    def test_cache_key_stable_and_distinct(self):
        self.assertEqual(ev.cache_key("a", "b"), ev.cache_key("a", "b"))
        self.assertNotEqual(ev.cache_key("a", "b"), ev.cache_key("a", "c"))
        self.assertNotEqual(ev.cache_key("a", "b"), ev.cache_key("a b", ""))

    def test_swaps_come_from_other_books(self):
        positives = [pos("slug-a", "John 3:5", "john"),
                     pos("slug-b", "Psalms 23:1", "ps"),
                     pos("slug-c", "Romans 8:28", "rom")]
        negs = ev.assign_swaps(positives, random.Random(0))
        by_idx = {}
        for i, display, stratum in negs:
            by_idx.setdefault(i, []).append((display, stratum))
        for i, p in enumerate(positives):
            for display, _s in by_idx[i]:
                self.assertNotIn(display, [p[4]])
        strata = {s for _, _, s in negs}
        self.assertIn("NEG_XTEST", strata)
        self.assertIn("NEG_STEST", strata)

    def test_swaps_exclude_same_book(self):
        positives = [pos("a", "John 3:5", "john"), pos("b", "John 3:16", "john"),
                     pos("c", "Psalms 23:1", "ps")]
        negs = ev.assign_swaps(positives, random.Random(2))
        by_idx = {}
        for i, display, _s in negs:
            by_idx.setdefault(i, []).append(display)
        self.assertEqual(by_idx[0], ["Psalms 23:1"])
        self.assertEqual(by_idx[1], ["Psalms 23:1"])

    def test_swaps_cross_testament(self):
        positives = [pos("a", "John 3:5", "john"), pos("b", "Psalms 23:1", "ps")]
        negs = ev.assign_swaps(positives, random.Random(1))
        x = [(i, d) for i, d, s in negs if s == "NEG_XTEST"]
        self.assertTrue(x)
        for i, d in x:
            own_test = ev.testament(positives[i][3][0])
            swap_test = "NT" if "John" in d or "Romans" in d else "OT"
            self.assertNotEqual(own_test, swap_test)

    def test_summarize_counts(self):
        records = [
            {"stratum": "POS_DIRECT", "book": "b", "section": "s",
             "display": "John 3:5", "clause": "c", "choice": "supports",
             "confidence": 0.9, "cached": False},
            {"stratum": "POS_DIRECT", "book": "b", "section": "s",
             "display": "John 3:6", "clause": "c", "choice": "contradicts",
             "confidence": 0.95, "cached": False},
            {"stratum": "NEG_XTEST", "book": "b", "section": "s",
             "display": "Psalms 1:1", "clause": "c", "choice": "contradicts",
             "confidence": 0.99, "cached": False},
        ]
        stats = {"calls": 1, "cached": 0, "in_tokens": 10, "out_tokens": 2,
                 "seconds": 1.0, "errors": 0}
        text = ev.summarize(records, stats)
        flat = " ".join(text.split())
        self.assertIn("POS_DIRECT n= 2 supports= 1 (50%)", flat)
        self.assertIn("highconf_wrong=1", text)
        self.assertIn("NEG_XTEST", text)

    def test_evaluate_uses_cache_without_api(self):
        positives = [pos("slug-a", "John 3:5")]
        key = ev.cache_key("clause words", "John 3:5")
        cache = {key: {"choice": "supports", "confidence": 0.9,
                       "probabilities": {}, "model": "jev-x"}}
        with patch.object(ev.cite, "load_section_texts", return_value=("g", ["e"])), \
             patch.object(ev, "jev", side_effect=AssertionError("must not call")):
            records, stats = ev.evaluate(positives, cache=cache)
        self.assertEqual(stats["calls"], 0)
        self.assertEqual(records[0]["choice"], "supports")
        self.assertTrue(records[0]["cached"])


if __name__ == "__main__":
    unittest.main()
