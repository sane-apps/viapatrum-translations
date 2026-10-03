#!/usr/bin/env python3
"""Offline regressions for overnight stall fixes. Never calls an inference endpoint."""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ai_promote as promote
import draft_claim as draft
import hold_reconcile as recon
import overnight_quota as quota
import redraft_b as redraft


GREEK1 = ["\u1f41\u03b8\u03b5\u03bf\u03c2\u03bf\u03c5\u03ba\u1f00\u03b4\u03b9\u03ba\u03b5\u03b9"]
GREEK2 = GREEK1 + ["\u0394\u03b9\u03b1\u03c4\u03bf\u03c5\u03c4\u03bf\u1f14\u03c0\u03b1\u03b9\u03bd\u03bf\u03c2"]


def bundle(n=1):
    greek = GREEK1 if n == 1 else GREEK2
    english = ["God does no wrong.", "Praise is just."][:n]
    return {"section": "t.1", "greek": greek,
            "english_row": {"section": "t.1", "title": "Thought", "english": english},
            "justification": {"draft_model": "m", "source_text": " ".join(greek),
                "pass_a_gloss": "gloss", "lemmas": [], "choices": [],
                "edition": {"id": "t"}}}


def good_verdict(n=1):
    return {"verdict": "pass", "reviewer": "model",
            "notes": "covers every clause with concrete evidence quoted here",
            "checks": {k: True for k in ("source_identity", "completeness", "negation",
                                         "agency", "modality", "doctrine", "scripture")},
            "pass_a_fidelity": True, "title_is_thought": True,
            "covered_source_paragraphs": list(range(1, n + 1)),
            "uncertainties": [], "reasons": []}


class HardeningTests(unittest.TestCase):
    def test_gptoss_banned_from_draft_fallbacks(self):
        self.assertNotIn("gpt-oss", draft.DRAFT_FALLBACK_DEFAULTS)
        self.assertNotIn("gpt-oss", redraft.DRAFT_FALLBACK_DEFAULTS)

    def test_reconcile_keep_path_reports_without_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            rdir = Path(tmp) / "20260101T000000Z-c"
            rdir.mkdir()
            (rdir / "summary.json").write_text(json.dumps({"ok": False, "verdict": "hold"}))
            with patch.object(recon, "RECEIPTS", tmp):
                ev, why = recon.newest_receipt("c")
            self.assertIsNone(ev)
            self.assertIn("hold", why)

    def test_effective_shares_normalize(self):
        shares = {"rank1": 40.0, "reformed": 35.0, "densify": 15.0, "topics": 10.0}
        eff = quota.effective_lane_shares({"rank1"}, shares.get)
        self.assertEqual(eff, {"rank1": 1.0})
        eff2 = quota.effective_lane_shares(set(shares), lambda l: shares[l] / 100.0)
        self.assertAlmostEqual(sum(eff2.values()), 1.0)
        self.assertAlmostEqual(eff2["rank1"], 0.4)

    def test_checker_prompt_states_exact_count(self):
        p1 = promote.checker_prompt(bundle(1))
        self.assertIn("exactly 1", p1[1]["content"])
        p2 = promote.checker_prompt(bundle(2))
        self.assertIn("exactly 2", p2[1]["content"])

    def test_malformed_pass_gets_same_model_retry(self):
        bad = good_verdict(1)
        bad["covered_source_paragraphs"] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        good = good_verdict(1)
        calls = []

        def fake_call(*a, **k):
            obj = bad if not calls else good
            calls.append(1)
            return {"content": json.dumps(obj), "ms": 1}

        with patch.object(promote, "vendor_call", side_effect=fake_call):
            with patch("time.sleep", return_value=None):
                out = promote.run_checker("m", bundle(1), retries=2)
        self.assertTrue(out["ok"])
        self.assertEqual(len(calls), 2)

    def test_eligible_arbiter_models_collapse(self):
        draft_model = ("@cf/meta/llama-3.3-70b-instruct-fp8-fast"
                       "+rev:@cf/qwen/qwen3-30b-a3b-fp8")
        elig = promote.eligible_arbiter_models(
            promote.ARBITER_DEFAULTS, draft_model,
            ("@cf/google/gemma-4-26b-a4b-it", "nvidia/nemotron-3-super-120b-a12b"))
        self.assertEqual(elig, ["@cf/zai-org/glm-4.7-flash"])

    def test_judged_snapshot(self):
        snap = promote.judged_snapshot(bundle(1))
        self.assertEqual(snap["greek"], GREEK1)
        self.assertEqual(len(snap["english"]), 1)

    def test_hold_lock_no_lost_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            hp = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", hp):
                threads = [threading.Thread(target=quota.record_claim_fail,
                                            args=("c", "hold"))
                           for _ in range(20)]
                [t.start() for t in threads]
                [t.join() for t in threads]
                row = quota.load_hold()["c"]
            self.assertEqual(row["fails"], 20)

    def test_revise_sys_verify_first(self):
        self.assertIn("VERIFY FIRST", draft.REVISE_SYS)

    def test_check_sys_citation_practice(self):
        self.assertIn("Added identifications are REQUIRED", promote.CHECK_SYS)


if __name__ == "__main__":
    unittest.main()
