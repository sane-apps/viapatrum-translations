#!/usr/bin/env python3
"""Known-answer tests for the reference ratchet (Nov 8, 2026). Run: python3 -m unittest discover -s scripts -p test_ref_ratchet.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_ratchet as R  # noqa: E402


class Ratchet(unittest.TestCase):
    def book(self, root, name, paras):
        d = root / name / "translations"
        d.mkdir(parents=True)
        (d / "x_english.json").write_text(json.dumps([{"section": "1", "english": paras}]))
        return root / name

    def test_counts_impossible_and_placeholders_only(self):
        with tempfile.TemporaryDirectory() as t:
            b = self.book(Path(t), "w", ["Loved the world (John 3:16).", "Sing (Psalm 151:2) and (Ps 183:4).",
                                         "Bless the Lord, O angels (Daniel 3:58); seed of Canaan (Daniel 13:56).",
                                         "As the prophet said (prophetic allusion); the echo (of a voice)."])
            n, ex = R.count_book(b)
            self.assertEqual(n, 3)
            self.assertIn("(prophetic allusion)", ex)

    def test_rise_fails_and_fall_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self.book(root / "books", "w", ["(Psalm 151:2)", "(Ps 183:4)"])
            old = (R.BOOKS, R.BASELINE)
            R.BOOKS, R.BASELINE = root / "books", root / "base.json"
            try:
                R.BASELINE.write_text(json.dumps({"books": {"w": 1}}))
                self.assertEqual(R.main([]), 1)
                R.BASELINE.write_text(json.dumps({"books": {"w": 3}}))
                self.assertEqual(R.main([]), 0)
            finally:
                R.BOOKS, R.BASELINE = old


if __name__ == "__main__":
    unittest.main()
