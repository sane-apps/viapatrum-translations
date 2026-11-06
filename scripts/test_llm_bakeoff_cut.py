#!/usr/bin/env python3
"""Offline tests for llm_bakeoff.cf_call: cut-off / reasoning-only replies with n > 1 keep every choice ("raw"),
billed tokens are returned on those replies too, and the spend reservation covers n samples. No network: urlopen
and spend_guard.reserve are stubbed. Run: python3 scripts/test_llm_bakeoff_cut.py"""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_bakeoff as B  # noqa: E402
import spend_guard as G  # noqa: E402

CUT = {"message": {"content": "{\"quote\":\"abc"}, "finish_reason": "length"}
OK = {"message": {"content": "{\"verdict\":\"major\"}"}, "finish_reason": "stop"}
THINK = {"message": {"content": None, "reasoning_content": "thinking..."}, "finish_reason": "length"}
USAGE = {"prompt_tokens": 100, "completion_tokens": 3000, "neurons": 42}


class Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def reply(choices):
    body = {"success": True, "result": {"choices": choices, "usage": USAGE}}
    return Resp(json.dumps(body).encode())


class CutOff(unittest.TestCase):
    def setUp(self):
        self.reserved = []
        self.p = [mock.patch.object(G, "reserve", lambda caller, usd, now=None: (self.reserved.append(usd) or (True, ""))),
                  mock.patch.object(B, "batch_route", lambda *a, **k: False)]
        for p in self.p:
            p.start()

    def tearDown(self):
        for p in self.p:
            p.stop()

    def call(self, choices, extra):
        with mock.patch.object(B.urllib.request, "urlopen", lambda req, timeout=None: reply(choices)):
            return B.cf_call("@cf/x/y", [{"role": "user", "content": "hi"}], "tok", "acct", 2000, extra=extra)

    def test_n3_choice0_cut_keeps_all_choices(self):
        r = self.call([CUT, OK, OK], {"n": 3})
        self.assertEqual(r["error"], B.TRUNCATED_LENGTH)
        self.assertEqual(len(r["raw"]["choices"]), 3)
        self.assertEqual([c["finish_reason"] for c in r["raw"]["choices"]], ["length", "stop", "stop"])
        self.assertEqual((r["pt"], r["ct"], r["neurons"]), (100, 3000, 42))

    def test_n3_choice0_reasoning_only_keeps_all_choices(self):
        r = self.call([THINK, OK, OK], {"n": 3})
        self.assertEqual(r["error"], B.TRUNCATED_REASONING)
        self.assertEqual(len(r["raw"]["choices"]), 3)
        self.assertEqual(r["neurons"], 42)

    def test_no_extra_keeps_old_contract(self):
        r = self.call([CUT], None)
        self.assertEqual(r["error"], B.TRUNCATED_LENGTH)
        self.assertNotIn("raw", r)
        self.assertEqual(r["ct"], 3000)

    def test_reservation_covers_n_samples(self):
        self.call([OK], {"n": 1})
        self.call([OK, OK, OK], {"n": 3})
        self.call([OK], None)
        one, three, none = self.reserved
        self.assertAlmostEqual(none, one)
        self.assertAlmostEqual(three - G.estimate_usd(2, 0), 3 * (one - G.estimate_usd(2, 0)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
