#!/usr/bin/env python3
"""Offline tests for spend_guard.py. No network.
Run: python3 scripts/test_spend_guard.py
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spend_guard as G  # noqa: E402


class SpendGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.patches = [mock.patch.object(G, name, d / leaf) for name, leaf in
                        (("SPEND", "spend"), ("TODAY", "spend/today.json"), ("CAP_FILE", "spend/cap.json"),
                         ("PAUSED", "lanes.paused"), ("RESTART", "lanes.restart"))]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def row(self, usd=None, error=None):
        usage = {"error": error} if error else {"neurons": 0, "usd": usd}
        return G.evaluate(usage, 150.0, "2026-10-14")

    def test_free_tier_is_not_billed(self):
        self.assertEqual(G.usd_of(10_000), 0)
        self.assertAlmostEqual(G.usd_of(1_010_000), 11.0)

    def test_over_cap_pauses_lanes_and_asks_them_to_exit(self):
        self.assertEqual(G.gate_lanes(self.row(151)), 1)
        self.assertTrue(G.PAUSED.read_text().startswith(G.BUDGET_TAG))
        self.assertTrue(G.RESTART.exists())

    def test_next_day_lifts_only_its_own_pause(self):
        G.gate_lanes(self.row(200))
        self.assertEqual(G.gate_lanes(self.row(3)), 0)
        self.assertFalse(G.PAUSED.exists())
        self.assertEqual(G.gate_lanes(self.row(100)), 0)
        G.PAUSED.write_text("owner: quality audit\n")
        self.assertEqual(G.gate_lanes(self.row(3)), 1)
        self.assertTrue(G.PAUSED.exists(), "an owner pause is never lifted by the budget")

    def test_lanes_stop_at_their_share_leaving_room_for_narration(self):
        self.assertEqual(G.gate_lanes(self.row(125)), 1)  # 125 >= 0.8 * 150
        self.assertTrue(G.PAUSED.exists())

    def test_unknown_usage_starts_nothing_but_pauses_nothing(self):
        self.assertEqual(G.gate_lanes(self.row(error="HTTP 500")), 1)
        self.assertFalse(G.PAUSED.exists())

    def test_cap_file_wins(self):
        G.SPEND.mkdir(parents=True, exist_ok=True)
        G.CAP_FILE.write_text('{"usd": 80}')
        self.assertEqual(G.cap_usd(), 80.0)

    def test_check_exit_codes(self):
        with mock.patch.object(G, "read_usage", return_value={"neurons": 0, "usd": 500.0}):
            self.assertEqual(G.main(["x", "check"]), G.OVER)
        with mock.patch.object(G, "read_usage", return_value={"error": "x"}):
            self.assertEqual(G.main(["x", "check"]), G.UNKNOWN)
        with mock.patch.object(G, "read_usage", return_value={"neurons": 0, "usd": 1.0}):
            self.assertEqual(G.main(["x", "check"]), G.OK)


if __name__ == "__main__":
    unittest.main()
