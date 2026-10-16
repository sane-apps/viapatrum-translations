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
        with mock.patch.object(G, "read_usage", return_value={"neurons": 0, "usd": 1.0}), \
                mock.patch.object(G, "read_hour_usage", return_value={"neurons": 0, "usd": 0.5}):
            self.assertEqual(G.main(["x", "check"]), G.OK)
        # under the daily cap but past the hourly ceiling (cap/12): check refuses too
        with mock.patch.object(G, "read_usage", return_value={"neurons": 0, "usd": 20.0}), \
                mock.patch.object(G, "read_hour_usage", return_value={"neurons": 0, "usd": 13.0}):
            self.assertEqual(G.main(["x", "check"]), G.OVER)



class PerCallGate(unittest.TestCase):
    """Broker batches and review calls are refused over the daily cap, over the
    hourly ceiling (cap/12) or with usage unknown, and allowed under them."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.patches = [mock.patch.object(G, "SPEND", d / "spend"),
                        mock.patch.object(G, "ALLOW_CACHE", d / "spend/allow.json"),
                        mock.patch.object(G, "CAP_FILE", d / "spend/cap.json"),
                        mock.patch.dict("os.environ", {"FATHERS_DAILY_CAP_USD": "150"})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def usage(self, day, hour):
        def u(x):
            return {"error": "no token"} if x is None else {"neurons": 0, "usd": x}
        return [mock.patch.object(G, "read_usage", return_value=u(day)),
                mock.patch.object(G, "read_hour_usage", return_value=u(hour))]

    def gate(self, day, hour):
        ps = self.usage(day, hour)
        for p in ps:
            p.start()
        try:
            G.ALLOW_CACHE.unlink(missing_ok=True)
            return G.allow("test")
        finally:
            for p in ps:
                p.stop()

    def test_decide(self):
        self.assertTrue(self.gate(100, 5)[0])
        self.assertIn("daily cap", self.gate(182.42, 0)[1])
        self.assertFalse(self.gate(182.42, 0)[0])
        self.assertAlmostEqual(G.hourly_ceiling_usd(150), 12.5)
        ok, why = self.gate(40, 12.5)
        self.assertFalse(ok)
        self.assertIn("hourly ceiling", why)
        self.assertFalse(self.gate(None, 1)[0])
        self.assertFalse(self.gate(10, None)[0])

    def test_cache_is_reused_within_ttl(self):
        self.assertFalse(self.gate(200, 0)[0])
        with mock.patch.object(G, "read_usage", side_effect=AssertionError("queried")):
            self.assertFalse(G.allow("again")[0])

    def _broker_flush(self, day, hour):
        import cf_batch_broker as B
        ps = self.usage(day, hour) + [
            mock.patch.object(B, "_post", return_value=(200, {"result": {"request_id": "r1"}})),
            mock.patch.object(B.L, "rate_acquire", return_value=True),
            mock.patch.object(B, "_finish")]
        mocks = [p.start() for p in ps]
        try:
            B.queues.clear(); B.pending.clear()
            G.ALLOW_CACHE.unlink(missing_ok=True)
            B.queues["@cf/zai-org/glm-5.2"] = [{"payload": {"messages": []}, "t": 0}]
            self.assertTrue(B.flush_once("@cf/zai-org/glm-5.2"))
            return mocks[2], mocks[4]
        finally:
            for p in ps:
                p.stop()
            B.queues.clear(); B.pending.clear()

    def test_broker_refuses_over_cap(self):
        post, finish = self._broker_flush(182.42, 0)
        post.assert_not_called()
        self.assertIn("spend guard refused", finish.call_args.kwargs["error"])

    def test_broker_refuses_over_hourly_ceiling(self):
        post, finish = self._broker_flush(20, 13)
        post.assert_not_called()
        self.assertIn("hourly ceiling", finish.call_args.kwargs["error"])

    def test_broker_refuses_unknown_usage(self):
        post, _ = self._broker_flush(None, None)
        post.assert_not_called()

    def test_broker_allows_under(self):
        post, finish = self._broker_flush(20, 1)
        post.assert_called_once()
        finish.assert_not_called()

    def _review_call(self, day, hour):
        import dual_family_review as D
        ps = self.usage(day, hour) + [mock.patch.object(
            D, "_post", return_value=(200, {}, {"result": {"choices": [{"message": {"content": "ok"}}]}}))]
        mocks = [p.start() for p in ps]
        try:
            G.ALLOW_CACHE.unlink(missing_ok=True)
            try:
                res = D.call_cf("@cf/zai-org/glm-5.2", [{"role": "user", "content": "x"}], "k")
            except D.QuotaPause as e:
                res = e
            return res, mocks[2]
        finally:
            for p in ps:
                p.stop()

    def test_review_call_refused_over_cap_and_hourly(self):
        import dual_family_review as D
        for day, hour in ((182.42, 0), (20, 13), (None, None)):
            res, post = self._review_call(day, hour)
            self.assertIsInstance(res, D.QuotaPause)
            post.assert_not_called()

    def test_review_call_allowed_under(self):
        res, post = self._review_call(20, 1)
        self.assertEqual(res["text"], "ok")
        post.assert_called_once()


class HoldAndReservation(unittest.TestCase):
    """2026-10-16: owner hold, pre-call reservation (15 s cache), and every
    Workers AI path in this repo refusing without a request."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.patches = [mock.patch.object(G, "SPEND", d / "spend"),
                        mock.patch.object(G, "ALLOW_CACHE", d / "spend/allow.json"),
                        mock.patch.object(G, "CAP_FILE", d / "spend/cap.json"),
                        mock.patch.object(G, "HOLD", d / "spend/hold"),
                        mock.patch.dict("os.environ", {"FATHERS_DAILY_CAP_USD": "150"}),
                        mock.patch.object(G, "_reserved", [])]
        for p in self.patches:
            p.start()
        (d / "spend").mkdir()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def usage(self, day, hour):
        return [mock.patch.object(G, "read_usage", return_value={"neurons": 0, "usd": day}),
                mock.patch.object(G, "read_hour_usage", return_value={"neurons": 0, "usd": hour})]

    def hold(self):
        G.HOLD.write_text("owner pause test")

    def test_cache_is_15_s(self):
        self.assertEqual(G.ALLOW_TTL_S, 15)

    def test_hold_refuses_everything_without_reading_usage(self):
        self.hold()
        with mock.patch.object(G, "read_usage", side_effect=AssertionError("read")):
            self.assertFalse(G.allow("t")[0])
            ok, why = G.reserve("t", 0.0)
            self.assertFalse(ok)
            self.assertIn("owner hold", why)
            with self.assertRaises(G.SpendRefused) as cm:
                G.gate("t", 0.0)
            self.assertTrue(str(cm.exception).startswith(G.REFUSED_TAG))
            with mock.patch("builtins.print"):
                self.assertEqual(G.main(["x", "check"]), G.OVER)
                self.assertEqual(G.main(["x", "allow"]), G.OVER)
                self.assertEqual(G.main(["x", "gate-lanes"]), 1)

    def test_reservations_add_up_against_the_hourly_ceiling_and_expire(self):
        ps = self.usage(100.0, 10.0)
        for p in ps:
            p.start()
        try:
            self.assertTrue(G.reserve("a", 1.0, now=1000.0)[0])
            self.assertTrue(G.reserve("b", 1.0, now=1001.0)[0])
            ok, why = G.reserve("c", 1.0, now=1002.0)   # 10 + 2 reserved + 1 >= 12.50
            self.assertFalse(ok)
            self.assertIn("hourly ceiling", why)
            self.assertTrue(G.reserve("d", 1.0, now=1000.0 + G.RESERVE_WINDOW_S + 1)[0])
        finally:
            for p in ps:
                p.stop()

    def test_reservations_add_up_against_the_daily_cap(self):
        ps = self.usage(149.0, 0.0)
        for p in ps:
            p.start()
        try:
            self.assertTrue(G.reserve("a", 0.5, now=1.0)[0])
            ok, why = G.reserve("b", 0.6, now=2.0)
            self.assertFalse(ok)
            self.assertIn("daily cap", why)
        finally:
            for p in ps:
                p.stop()

    def test_estimate(self):
        self.assertAlmostEqual(G.estimate_usd(4000, 1000), 0.001 + 0.004)
        self.assertAlmostEqual(G.estimate_usd(tts_chars=1000), 0.03)

    def test_llm_bakeoff_cf_call_refuses_without_a_request(self):
        import llm_bakeoff as LB
        self.hold()
        with mock.patch.object(LB.urllib.request, "urlopen", side_effect=AssertionError("network")):
            r = LB.cf_call("@cf/zai-org/glm-5.2", [{"role": "user", "content": "x"}], "tok", "acct")
        self.assertTrue(r["spend_refused"])
        self.assertIn(G.REFUSED_TAG, r["error"])

    def test_llm_bakeoff_broker_refusal_never_goes_direct(self):
        import llm_bakeoff as LB
        ps = self.usage(1.0, 0.0)
        for p in ps:
            p.start()
        try:
            LB._use_batch.on = True
            with mock.patch.object(LB, "batch_route", return_value=True), \
                    mock.patch.object(LB, "_broker_run", return_value={"error": "spend guard refused: over"}), \
                    mock.patch.object(LB.urllib.request, "urlopen", side_effect=AssertionError("direct")):
                r = LB.cf_call("@cf/moonshotai/kimi-k2.6", [{"role": "user", "content": "x"}], "tok", "acct")
        finally:
            LB._use_batch.on = False
            for p in ps:
                p.stop()
        self.assertTrue(r["spend_refused"])

    def test_work_pipeline_call_stops_at_the_first_refusal(self):
        import work_pipeline as WP
        calls = []
        def fake(*a, **k):
            calls.append(1)
            return {"error": "spend guard refused (x): owner hold", "spend_refused": True}
        with mock.patch.object(WP, "vendor_call", fake), mock.patch.object(WP.time, "sleep"), \
                mock.patch("sys.stderr"):
            self.assertIsNone(WP.call("@cf/zai-org/glm-5.2", "s", "u"))
        self.assertEqual(len(calls), 1)

    def test_dual_family_review_reserves_and_refuses_under_hold(self):
        import dual_family_review as D
        self.hold()
        with mock.patch.object(D, "_post", side_effect=AssertionError("network")):
            with self.assertRaises(D.QuotaPause):
                D.call_cf("@cf/zai-org/glm-5.2", [{"role": "user", "content": "x"}], "k")

    def test_broker_refuses_under_hold(self):
        import cf_batch_broker as B
        self.hold()
        with mock.patch.object(B, "_post", side_effect=AssertionError("network")), \
                mock.patch.object(B, "_finish") as fin, mock.patch.object(B, "_log"):
            B.queues["@cf/zai-org/glm-5.2"] = [{"payload": {"messages": []}, "t": 0}]
            try:
                self.assertTrue(B.flush_once("@cf/zai-org/glm-5.2"))
            finally:
                B.queues.clear()
        self.assertTrue(fin.call_args.kwargs["error"].startswith(G.REFUSED_TAG))

if __name__ == "__main__":
    unittest.main()
