#!/usr/bin/env python3
"""Regressions for local KJV lookup. Skips cleanly without data/en_kjv.json."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import kjv_lookup as kjv

HAS_DATA = kjv.KJV_PATH.is_file()


@unittest.skipUnless(HAS_DATA, "needs data/en_kjv.json")
class KjvLookupTests(unittest.TestCase):
    def test_genesis(self):
        self.assertTrue(kjv.verse_text("gen", 1, 1).startswith("In the beginning"))

    def test_index_mapping(self):
        self.assertIn("God so loved the world", kjv.verse_text("john", 3, 16))
        self.assertIn("valley of the shadow", kjv.verse_text("ps", 23, 4))

    def test_window(self):
        text = kjv.verse_window("ps", 23, 1)
        self.assertIn("LORD is my shepherd", text)
        self.assertIn("green pastures", text)

    def test_unknown_is_empty(self):
        self.assertEqual(kjv.verse_text("wis", 2, 24), "")
        self.assertEqual(kjv.verse_text("john", 99, 1), "")
        self.assertEqual(kjv.verse_text("nope", 1, 1), "")


if __name__ == "__main__":
    unittest.main()
