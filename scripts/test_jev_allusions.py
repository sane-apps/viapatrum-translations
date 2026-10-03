#!/usr/bin/env python3
"""Offline regressions for Jev excerpt windowing and certainty normalization."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_review import (  # noqa: E402
    WINDOW_EDGE,
    WINDOW_FULL,
    WINDOW_SNIP,
    excerpt_window,
    normalize_certainty,
)


class WindowTests(unittest.TestCase):
    def test_short_passthrough(self):
        self.assertEqual(excerpt_window("abc"), "abc")
        self.assertEqual(excerpt_window(""), "")

    def test_boundary_passthrough(self):
        text = "x" * WINDOW_FULL
        self.assertEqual(excerpt_window(text), text)

    def test_long_snip_keeps_head_and_tail(self):
        text = "H" * WINDOW_EDGE + "M" * 5000 + "T" * WINDOW_EDGE
        out = excerpt_window(text)
        self.assertIn(WINDOW_SNIP.strip(), out)
        self.assertTrue(out.startswith("H" * WINDOW_EDGE))
        self.assertTrue(out.endswith("T" * WINDOW_EDGE))
        self.assertNotIn("M" * 100, out)
        self.assertLess(len(out), len(text))

    def test_quoted_verse_late_in_excerpt_stays_visible(self):
        head = "preface method talk. " * 60
        quote = "I gave my back to whips and my cheeks to palms."
        text = head + quote
        self.assertLess(len(text), WINDOW_FULL)
        self.assertIn(quote, excerpt_window(text))


class NormalizeTests(unittest.TestCase):
    def test_strong_band(self):
        self.assertEqual(normalize_certainty("clear"), "clear")
        self.assertEqual(normalize_certainty("quotation"), "clear")
        self.assertEqual(normalize_certainty(" Clear "), "clear")

    def test_weak_band(self):
        for raw in ("possible", "probable", "allusion", "allusive"):
            self.assertEqual(normalize_certainty(raw), "possible")

    def test_none_band(self):
        self.assertEqual(normalize_certainty("none"), "none")

    def test_unknown_passes_through(self):
        self.assertEqual(normalize_certainty("echoic"), "echoic")
        self.assertEqual(normalize_certainty(""), "")


if __name__ == "__main__":
    unittest.main()
