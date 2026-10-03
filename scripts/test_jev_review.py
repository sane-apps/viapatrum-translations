#!/usr/bin/env python3
"""Offline regressions for Jev routing (Cloudflare first, direct fallback)."""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jev_review as jr


ANSWERS = {"answers": {"v": {"type": "choice", "choice": "a", "confidence": 0.9}}}


class FakeResp:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.payload


class JevRoutingTests(unittest.TestCase):
    def test_cf_first_unwraps_result(self):
        seen = {}

        def fake_open(req, timeout=None):
            seen["url"] = req.full_url
            seen["body"] = json.loads(req.data.decode())
            return FakeResp({"result": dict(ANSWERS, model="jev-1.13.0"), "success": True})

        env = {"CF_TOKEN": "cf", "CLOUDFLARE_ACCOUNT_ID": "acct",
               "TYPESAFE_API_KEY": "ts"}
        with patch.object(jr.urllib.request, "urlopen", fake_open), \
             patch.dict("os.environ", env, clear=False):
            out = jr.jev({"s": 1}, {"v": {}})
        self.assertIn("/ai/run", seen["url"])
        self.assertEqual(seen["body"]["model"], "typesafe/jev")
        self.assertEqual(seen["body"]["input"]["state"], {"s": 1})
        self.assertEqual(out["answers"], ANSWERS["answers"])

    def test_cf_failure_falls_back_to_direct(self):
        calls = []

        def fake_open(req, timeout=None):
            calls.append(req.full_url)
            if "cloudflare" in req.full_url:
                raise RuntimeError("boom-2021")
            return FakeResp(ANSWERS)

        env = {"CF_TOKEN": "cf", "CLOUDFLARE_ACCOUNT_ID": "acct",
               "TYPESAFE_API_KEY": "ts"}
        with patch.object(jr.urllib.request, "urlopen", fake_open), \
             patch.dict("os.environ", env, clear=False):
            jr._fallback_noted = True
            try:
                out = jr.jev({"s": 1}, {"v": {}})
            finally:
                jr._fallback_noted = False
        self.assertEqual(len(calls), 2)
        self.assertIn("api.typesafe.ai", calls[1])
        self.assertEqual(out, ANSWERS)

    def test_cf_gateway_double_wrap_unwraps(self):
        gateway = {"state": "Completed",
                   "result": dict(ANSWERS, model="jev-1.13.0"),
                   "gatewayMetadata": {"keySource": "Unified"}}

        def fake_open(req, timeout=None):
            return FakeResp({"result": gateway, "success": True,
                             "errors": [], "messages": []})

        env = {"CF_TOKEN": "cf", "CLOUDFLARE_ACCOUNT_ID": "acct",
               "TYPESAFE_API_KEY": "ts"}
        with patch.object(jr.urllib.request, "urlopen", fake_open), \
             patch.dict("os.environ", env, clear=False):
            out = jr.jev({"s": 1}, {"v": {}})
        self.assertEqual(out["answers"], ANSWERS["answers"])

    def test_no_creds_raises(self):
        env = {"CF_TOKEN": "", "CLOUDFLARE_API_TOKEN": "",
               "TYPESAFE_API_KEY": ""}
        with patch.dict("os.environ", env, clear=False):
            with self.assertRaises(SystemExit):
                jr.jev({"s": 1}, {"v": {}})


if __name__ == "__main__":
    unittest.main()
