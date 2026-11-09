#!/usr/bin/env python3
"""No live default names a model Cloudflare retires on 2026-11-20, and no new default sends a kwarg
its live schema rejects or turns into its opposite. No network, no spend."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
for key in ("WP_DRAFTER", "WP_CHECKERS", "WP_JUDGES", "WP_FALLBACK", "DM_CHECKERS"):
    os.environ.pop(key, None)

import dual_family_review as DF  # noqa: E402
import llm_bakeoff as LB  # noqa: E402
import work_pipeline as W  # noqa: E402
import work_read as WR  # noqa: E402

# https://developers.cloudflare.com/changelog/post/2026-11-05-planned-model-deprecations/
RETIRED = {
    "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b", "@cf/nvidia/nemotron-3-120b-a12b",
    "@cf/deepseek-ai/deepseek-v4-pro-0813", "@cf/deepseek-ai/deepseek-v4-flash-0731", "@cf/qwen/qwq-32b",
    "@cf/qwen/qwen3-30b-a3b-fp8", "@cf/moonshotai/kimi-k2.6", "@cf/moonshotai/kimi-k2.7-code",
    "@cf/zai-org/glm-5.2", "@cf/zai-org/glm-5.3-flash", "@cf/meta-llama/llama-2-7b-chat-hf-lora",
    "@cf/google/gemma-2b-it-lora", "@cf/google/gemma-7b-it-lora", "@cf/meta/llama-3.1-8b-instruct-fp8",
    "@cf/meta/llama-3.2-1b-instruct", "@cf/meta/llama-3.2-3b-instruct",
}


class Retirement(unittest.TestCase):
    def test_pipeline_defaults_are_live_and_two_families(self):
        self.assertEqual(W.family_problems(), [])
        for model in [W._DEFAULT_DRAFTER, W.FALLBACK, *W.CHECKERS, *W.JUDGES, *WR.DEFAULT_MODELS,
                      *(DF.LANES[lane]["model"] for lane in DF.PROFILES["aligned"]["lanes"]), *LB.TIER_A]:
            self.assertNotIn(model, RETIRED)
        self.assertNotEqual(W.FAMILY[W.FALLBACK], W.FAMILY[W.CHECKERS[0]])
        self.assertNotEqual(W.FAMILY[W.FALLBACK], W.FAMILY[W.CHECKERS[1]])

    def test_new_family_names_are_real(self):
        self.assertEqual({W.FAMILY[m] for m in W.CHECKERS}, {"qwen", "gemma"})
        self.assertEqual(W.FAMILY[W.FALLBACK], "gpt-oss")

    def test_grader_defaults_are_live_and_can_batch(self):
        try:
            import doctrine_map as DM
        except (ImportError, unittest.SkipTest):
            self.skipTest("doctrine_map needs numpy; run with ~/Models/kokoro/.venv/bin/python")
        for model in DM.CHECKERS:
            self.assertNotIn(model, RETIRED)
            self.assertTrue(any(k in model for k in LB.BATCH_MODELS), model)

    def test_kwargs_match_live_schemas(self):
        qwen = LB.cf_profile("@cf/qwen/qwen3.8-27b")
        self.assertIs(qwen["enable_thinking"], False)
        self.assertIsNone(qwen["reasoning_effort"])
        gemma = LB.cf_profile("@cf/google/gemma-4-26b-a4b-it")
        self.assertIs(gemma["enable_thinking"], False)
        self.assertIsNone(gemma["reasoning_effort"])
        flash = LB.cf_profile("@cf/deepseek-ai/deepseek-v4.1-flash-1017")
        self.assertIs(flash["enable_thinking"], False)
        self.assertEqual(flash["reasoning_effort"], "none")
        glm = LB.cf_profile("@cf/zai-org/glm-5.3")
        self.assertEqual(glm["reasoning_effort"], "low")  # "none" maps to "max" on this model
        self.assertNotIn("enable_thinking", glm)

    def test_two_family_review_body_matches_schema(self):
        sent = {}

        def fake_post(url, body, headers, timeout):
            sent[url.rsplit("/", 1)[-1]] = body
            return 200, {}, {"result": {"choices": [{"message": {"content": "x"}}]}}

        real_post, real_allow = DF._post, DF.spend_allow
        DF._post, DF.spend_allow = fake_post, (lambda m: (True, "ok"))
        try:
            DF.call_cf("@cf/qwen/qwen3.8-27b", [{"role": "user", "content": "x"}], "k")
            DF.call_cf("@cf/google/gemma-4-26b-a4b-it", [{"role": "user", "content": "x"}], "k")
        finally:
            DF._post, DF.spend_allow = real_post, real_allow
        for body in sent.values():
            self.assertNotIn("reasoning_effort", body)
            self.assertIs(body["chat_template_kwargs"]["enable_thinking"], False)
        self.assertEqual(len(sent), 2)


if __name__ == "__main__":
    unittest.main()
