#!/usr/bin/env python3
"""inline_scripture_refs.expand_ref: English refs expand; Greek-numbered (LXX) refs are left out, never copied."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inline_scripture_refs as I  # noqa: E402


class ExpandRef(unittest.TestCase):
    def test_english_ref_expands(self):
        self.assertEqual(I.expand_ref("Matt 11:14"), "Matthew 11:14")

    def test_lxx_ref_is_left_out(self):
        self.assertIsNone(I.expand_ref("Ps 22:1 LXX"))


if __name__ == "__main__":
    unittest.main()
