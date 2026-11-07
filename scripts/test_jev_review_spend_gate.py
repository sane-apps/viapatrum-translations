#!/usr/bin/env python3
"""jev_review must ask spend_guard before every Workers AI call, and a refusal must not reach another paid path.
No network: _post is faked, and each test sets its own spend_guard answer. python3 scripts/test_jev_review_spend_gate.py"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev_review as J  # noqa: E402
import spend_guard  # noqa: E402

ANSWER = {"answers": {"certainty": "clear"}}


class Gate(unittest.TestCase):
    def setUp(self):
        env = {"CF_TOKEN": "fake", "CLOUDFLARE_ACCOUNT_ID": "fake"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("TYPESAFE_API_KEY", None)
        post = mock.patch.object(J, "_post", return_value=ANSWER)
        self.post = post.start()
        self.addCleanup(post.stop)

    def urls(self):
        return [call.args[0] for call in self.post.call_args_list]

    def test_allowed_call_is_reserved_then_sent(self):
        with mock.patch.object(spend_guard, "reserve", return_value=(True, "ok")) as reserve:
            self.assertEqual(J.jev("state", {"q": 1}), ANSWER)
        self.assertEqual(reserve.call_args.args[0], "jev_review")
        self.assertGreater(reserve.call_args.args[1], 0)
        self.assertEqual(len(self.urls()), 1)
        self.assertIn("api.cloudflare.com", self.urls()[0])

    def test_refusal_sends_nothing_and_skips_the_paid_fallback(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "fake"}), \
                mock.patch.object(spend_guard, "reserve", return_value=(False, "owner hold")):
            with self.assertRaisesRegex(J.JevSpendRefused, "owner hold"):
                J.jev("state", {"q": 1})
        self.assertEqual(self.urls(), [])

    def test_direct_cf_callers_are_gated_too(self):  # referee_bench calls _cf_jev itself
        with mock.patch.object(spend_guard, "reserve", return_value=(False, "over cap")):
            with self.assertRaises(J.JevSpendRefused):
                J._cf_jev("state", {"q": 1})
        self.assertEqual(self.urls(), [])

    def test_a_broken_guard_fails_closed(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "fake"}), \
                mock.patch.object(spend_guard, "reserve", side_effect=OSError("bad state file")):
            with self.assertRaisesRegex(J.JevSpendRefused, "unavailable"):
                J.jev("state", {"q": 1})
        self.assertEqual(self.urls(), [])

    def test_cf_failure_without_a_key_is_a_normal_error(self):
        self.post.side_effect = OSError("network down")
        with mock.patch.object(spend_guard, "reserve", return_value=(True, "ok")):
            with self.assertRaises(RuntimeError) as caught:
                J.jev("state", {"q": 1})
        self.assertNotIsInstance(caught.exception, J.JevSpendRefused)

    def test_cf_failure_still_uses_the_fallback_when_a_key_is_set(self):
        self.post.side_effect = [OSError("network down"), ANSWER]
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "fake"}), \
                mock.patch.object(spend_guard, "reserve", return_value=(True, "ok")), \
                mock.patch.object(J, "_fallback_noted", True):
            self.assertEqual(J.jev("state", {"q": 1}), ANSWER)
        self.assertIn("typesafe", self.urls()[1])


class PromoteSurvives(unittest.TestCase):
    def check(self, error):
        import ai_promote
        import jev_cite_check
        entry = {}
        env = {"CF_TOKEN": "fake"}
        with mock.patch.dict(os.environ, env), mock.patch.object(jev_cite_check, "check_section", side_effect=error):
            hold = ai_promote.jev_citation_gate(entry, {"book": "x", "section": "1"})
        return hold, entry

    def test_jev_failure_is_recorded_and_promote_goes_on(self):
        hold, entry = self.check(RuntimeError("CF Jev failed"))
        self.assertIsNone(hold)
        self.assertIn("CF Jev failed", entry["jev_cites"]["error"])

    def test_refusal_is_recorded_and_promote_goes_on(self):
        hold, entry = self.check(J.JevSpendRefused("cf spend guard refused: owner hold"))
        self.assertIsNone(hold)
        self.assertIn("owner hold", entry["jev_cites"]["error"])

    def test_the_hard_stop_still_stops(self):  # fathers_run_lock's wall deadline raises SystemExit
        with self.assertRaises(SystemExit):
            self.check(SystemExit("wall deadline"))


if __name__ == "__main__":
    unittest.main()
