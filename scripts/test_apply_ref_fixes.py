#!/usr/bin/env python3
"""Known-answer tests for apply_ref_fixes placement (Nov 8, 2026).
Run: python3 -m unittest discover -s scripts -p test_apply_ref_fixes.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_ref_fixes as A  # noqa: E402


class Placement(unittest.TestCase):
    def test_single_replace(self):
        p = "He was called Elijah by the Lord (Luke 1:17). Next."
        s = "He was called Elijah by the Lord (Luke 1:17)."
        self.assertEqual(A.new_para(p, s, "Luke 1:17", "replace", "Matthew 11:14"),
                         "He was called Elijah by the Lord (Matthew 11:14). Next.")

    def test_twice_needs_times(self):
        s = "'Save me' (Ps 30:3) and again 'save me' (Ps 30:3)."
        self.assertIsNone(A.new_para(s, s, "Ps 30:3", "replace", "Psalm 31:1"))
        self.assertEqual(A.new_para(s, s, "Ps 30:3", "replace", "Psalm 31:1", 2),
                         "'Save me' (Psalm 31:1) and again 'save me' (Psalm 31:1).")

    def test_times_does_not_touch_longer_reference(self):
        s = "(Ps 30:3) and (Ps 30:31)."
        self.assertIsNone(A.new_para(s, s, "Ps 30:3", "replace", "Psalm 31:1", 2))

    def test_remove_cleans_parenthesis(self):
        s = "the earth is a tent (Ps 103:29), and"
        self.assertEqual(A.new_para(s, s, "Ps 103:29", "remove", None), "the earth is a tent, and")

    def test_dump_like_keeps_style(self):
        for text in ('[\n {\n  "a": "é"\n }\n]', '[\n  {\n    "a": "\\u00e9"\n  }\n]\n'):
            data = json.loads(text)
            self.assertEqual(A.dump_like(text, data), text)


class ShipLock(unittest.TestCase):
    def test_held_lock_means_ship_running(self):
        import fcntl
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            lock = Path(t) / "ship.lock"
            self.assertFalse(A.ship_running(lock))
            lock.write_text("")
            self.assertFalse(A.ship_running(lock))
            fd = os.open(lock, os.O_WRONLY)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                self.assertTrue(A.ship_running(lock))
            finally:
                os.close(fd)
            self.assertFalse(A.ship_running(lock))


if __name__ == "__main__":
    unittest.main()
