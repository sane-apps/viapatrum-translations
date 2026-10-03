#!/usr/bin/env python3
"""regen_declared_packet must refuse ephemeral (/tmp) witnesses.

Regression test for the 2026-09-28 le-blanc incident, where a packet bound
/private/tmp scratch that was later wiped, holding the work out of the
site build. No model calls.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import regen_declared_packet as regen


class RegenEphemeralGuardTests(unittest.TestCase):
    def test_tmp_witnesses_rejected(self):
        self.assertTrue(regen._is_ephemeral("/private/tmp/apply_x.py"))
        self.assertTrue(regen._is_ephemeral("/tmp/latin.json"))
        self.assertTrue(regen._is_ephemeral("/var/folders/zz/T/work.txt"))

    def test_repo_witnesses_accepted(self):
        self.assertFalse(regen._is_ephemeral(
            "/Users/stephansmac/SaneApps/clients/translations/books/x/sources/print.txt"))
        self.assertFalse(regen._is_ephemeral(
            "/Users/stephansmac/SaneApps/clients/translations/books/x/translations/e.json"))

    def test_tmp_substring_in_name_is_fine(self):
        # "tmp" appearing inside a durable filename must not trip the guard.
        self.assertFalse(regen._is_ephemeral(
            "/Users/stephansmac/SaneApps/clients/translations/books/x/sources/attempt.txt"))


if __name__ == "__main__":
    unittest.main()
