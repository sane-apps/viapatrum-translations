#!/usr/bin/env python3
"""Offline tests for the work_pipeline efficiency changes (2026-10-03).

No network and no LLM: every model call is replaced by a stub.
Run: python3 scripts/test_work_pipeline_efficiency.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import llm_bakeoff as LB  # noqa: E402
import work_pipeline as W  # noqa: E402
import work_read as R  # noqa: E402


def gate_only(j, brief):
    with mock.patch.object(W, "check_record", return_value=[]), \
            mock.patch.object(W, "output_guard_errors", return_value=[]):
        return W.section_gate(j, brief)


class FallbackPassTests(unittest.TestCase):
    def test_checker_fallback_does_not_certify(self):
        out = W.block_fallback_pass({
            "_status": "pass", "confidence": "source_verified",
            "checks": {"fallback": [{"model": W.FALLBACK}]},
        })
        self.assertEqual(out["_status"], "hold")
        self.assertEqual(out["confidence"], "held")
        self.assertIn(W.FALLBACK, out["_why"])

    def test_referee_fallback_does_not_certify(self):
        out = W.block_fallback_pass({"_status": "pass", "checks": {"referee": W.FALLBACK}})
        self.assertEqual(out["_status"], "hold")
        self.assertTrue(W.used_fallback(out))

    def test_two_real_checkers_still_pass(self):
        j = {"_status": "pass", "confidence": "source_verified",
             "checks": {"referee": "nvidia/nemotron-3-ultra-550b-a55b"}}
        self.assertEqual(W.block_fallback_pass(j)["_status"], "pass")
        self.assertFalse(W.used_fallback({"_status": "pass"}))


class NamesGateTests(unittest.TestCase):
    BRIEF = {"names": {"Sion": "Zion"}, "glossary": []}

    def rec(self, text):
        return {"section": "1", "source_text": "x.", "pass_b_english": [text]}

    def test_substring_no_longer_holds(self):
        self.assertEqual(gate_only(self.rec("He saw a vision of the city."), self.BRIEF), [])

    def test_whole_word_still_held_by_lint(self):
        errs = gate_only(self.rec("He went up to Sion."), self.BRIEF)
        self.assertTrue(any("Zion" in e for e in errs), errs)

    def test_modern_form_present_passes(self):
        self.assertEqual(gate_only(self.rec("Zion, that is Sion, rejoiced."), self.BRIEF), [])


class ParseObjTests(unittest.TestCase):
    def test_first_block_default_unchanged(self):
        self.assertEqual(R.parse_obj('x {"a": 1} y {"b": 2}'), {"a": 1})

    def test_last_block_with_expected_key(self):
        raw = 'thinking {"n": 1} more {"draft": 2} answer {"findings": [], "verdict": "pass"}'
        self.assertEqual(R.parse_obj(raw, expected_keys=("findings",)), {"findings": [], "verdict": "pass"})

    def test_no_expected_block_keeps_first(self):
        self.assertEqual(R.parse_obj('{"n": 1} {"m": 2}', expected_keys=("findings",)), {"n": 1})

    def test_first_block_with_key_wins(self):
        self.assertEqual(R.parse_obj('{"findings": [1]} {"findings": [2]}', expected_keys=("findings",)), {"findings": [1]})

    def test_braces_in_strings(self):
        self.assertEqual(R.parse_obj('{"x": "a } b"} {"rulings": []}', expected_keys=("rulings",)), {"rulings": []})


class PickContentTests(unittest.TestCase):
    def test_reasoning_only_is_not_content(self):
        res = {"choices": [{"message": {"content": "", "reasoning_content": '{"half": 1'}}]}
        self.assertIsNone(LB._cf_pick_content(res))
        self.assertTrue(LB._cf_reasoning_only(res))

    def test_content_kept(self):
        res = {"choices": [{"message": {"content": '{"a":1}', "reasoning_content": "hmm"}}]}
        self.assertEqual(LB._cf_pick_content(res), '{"a":1}')
        self.assertFalse(LB._cf_reasoning_only(res))

    def test_responses_shape_skips_reasoning_and_does_not_double(self):
        res = {"output": [{"type": "reasoning", "content": [{"type": "reasoning_text", "text": "{think}"}]},
                          {"type": "message", "content": [{"type": "output_text", "text": '{"a":1}'}]}]}
        self.assertEqual(LB._cf_pick_content(res), '{"a":1}')

    def test_responses_reasoning_only(self):
        res = {"output": [{"type": "reasoning", "content": [{"type": "reasoning_text", "text": "..."}]}]}
        self.assertIsNone(LB._cf_pick_content(res))
        self.assertTrue(LB._cf_reasoning_only(res))


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class CfCallTests(unittest.TestCase):
    def test_rate_error_returns_at_once(self):
        calls = []

        def fake(req, timeout=0):
            calls.append(1)
            return FakeResp(json.dumps({"success": False, "errors": [{"code": 429, "message": "rate limited"}]}).encode())
        with mock.patch.object(LB.urllib.request, "urlopen", fake), mock.patch.object(LB.time, "sleep") as sl:
            r = LB.cf_call("@cf/zai-org/glm-5.2", [], "t", "a")
        self.assertEqual(len(calls), 1)
        self.assertIn("429", r["error"])
        sl.assert_not_called()

    def test_http_429_returns_at_once(self):
        calls = []

        def fake(req, timeout=0):
            calls.append(1)
            raise urllib.error.HTTPError("u", 429, "Too Many Requests", {}, io.BytesIO(b"slow down"))
        with mock.patch.object(LB.urllib.request, "urlopen", fake), mock.patch.object(LB.time, "sleep"):
            r = LB.cf_call("@cf/zai-org/glm-5.2", [], "t", "a")
        self.assertEqual(len(calls), 1)
        self.assertIn("429", r["error"])

    def test_truncated_reasoning_error(self):
        body = {"success": True, "result": {"choices": [{"message": {"content": None, "reasoning_content": "{"}}]}}
        with mock.patch.object(LB.urllib.request, "urlopen", lambda req, timeout=0: FakeResp(json.dumps(body).encode())):
            r = LB.cf_call("@cf/zai-org/glm-5.3", [], "t", "a")
        self.assertTrue(r["error"].startswith("truncated"))

    def test_vendor_call_throttles_on_429(self):
        with mock.patch.object(LB, "_vendor_call_raw", return_value={"error": "HTTP 429 rate limited"}), \
                mock.patch.object(LB, "batch_route", return_value=False), \
                mock.patch.object(LB, "rate_acquire"), mock.patch.object(LB, "rate_throttled") as th:
            LB.vendor_call("@cf/zai-org/glm-5.2", [], cf_token="t")
        th.assert_called_once()


class TokenFloorTests(unittest.TestCase):
    def tok(self, model, asked):
        with mock.patch.object(LB, "cf_call", return_value={"content": "{}"}) as cc:
            LB._vendor_call_raw(model, [], cf_token="t", max_tokens=asked)
        return cc.call_args.kwargs["max_tokens"]

    def test_floor_for_thinking_models(self):
        self.assertEqual(self.tok("@cf/zai-org/glm-5.3", 3000), 16000)
        self.assertEqual(self.tok("@cf/openai/gpt-oss-120b", 3000), 12000)
        self.assertEqual(self.tok("@cf/openai/gpt-oss-120b", 20000), 20000)

    def test_other_models_keep_caller_budget(self):
        self.assertEqual(self.tok("@cf/zai-org/glm-5.2", 3000), 3000)
        self.assertEqual(self.tok("@cf/openai/gpt-oss-20b", 3000), 3000)


class CallRetryTests(unittest.TestCase):
    def run_call(self, replies, max_tokens=8000):
        seq = iter(replies)
        seen = []
        self.budgets = []

        def fake(model, msgs, **kw):
            seen.append(msgs[-1]["content"])
            self.budgets.append(kw.get("max_tokens"))
            return next(seq)
        with mock.patch.object(W, "vendor_call", fake), mock.patch.object(W.time, "sleep") as sl:
            out = W.call("m", "sys", "user", max_tokens=max_tokens, expect=("a",))
        return out, seen, [c.args[0] for c in sl.call_args_list]

    def test_unparseable_one_nudged_retry_no_sleep(self):
        out, seen, sleeps = self.run_call([{"content": "no json"}, {"content": '{"a": 1}'}])
        self.assertEqual(out, {"a": 1})
        self.assertEqual(len(seen), 2)
        self.assertTrue(seen[1].endswith("Return only the JSON object."))
        self.assertEqual(sleeps, [])

    def test_unparseable_twice_gives_none(self):
        out, seen, sleeps = self.run_call([{"content": "x"}, {"content": "y"}, {"content": '{"a": 1}'}])
        self.assertIsNone(out)
        self.assertEqual(len(seen), 2)
        self.assertEqual(sleeps, [])

    def test_truncated_retries_once_with_doubled_budget(self):
        # 2026-10-06: a cut-off reply re-sent at the same budget was cut off again.
        out, seen, sleeps = self.run_call([{"error": LB.TRUNCATED_LENGTH}, {"content": '{"a": 2}'}], max_tokens=6000)
        self.assertEqual(out, {"a": 2})
        self.assertEqual(self.budgets, [6000, 12000])
        self.assertEqual(seen, ["user", "user"], "no nudge: the budget was the problem")
        self.assertEqual(sleeps, [])
        out, seen, _ = self.run_call([{"error": LB.TRUNCATED_REASONING}, {"error": LB.TRUNCATED_LENGTH},
                                      {"content": '{"a": 3}'}], max_tokens=12000)
        self.assertIsNone(out)
        self.assertEqual(self.budgets, [12000, W.MAX_TOKENS_CAP])

    def test_cut_off_reply_whose_json_closed_is_used(self):
        out, seen, _ = self.run_call([{"error": LB.TRUNCATED_LENGTH, "content": '{"a": 5} and then rambling'}])
        self.assertEqual((out, len(seen)), ({"a": 5}, 1))

    def test_unparseable_logs_completion_tokens(self):
        err = io.StringIO()
        with mock.patch.object(W.sys, "stderr", err):
            self.run_call([{"content": "{\"a\": [", "ct": 6000}, {"content": "{\"a\": [", "ct": 6000}], max_tokens=6000)
        self.assertIn("unparseable (6000 of 6000 tokens)", err.getvalue())

    def test_rate_error_backs_off(self):
        out, seen, sleeps = self.run_call([{"error": "HTTP 429 rate limited"}, {"error": '[{"code": 3040, "message": "Capacity temporarily exceeded"}]'},
                                           {"content": '{"a": 3}'}])
        self.assertEqual(out, {"a": 3})
        self.assertEqual(sleeps, [15, 30])

    def test_rate_backoff_is_bounded(self):
        out, seen, sleeps = self.run_call([{"error": "429"}] * 6)
        self.assertIsNone(out)
        self.assertEqual(sleeps, [15, 30, 60, 90, 120])

    def test_other_error_one_retry(self):
        out, seen, sleeps = self.run_call([{"error": "fetch failed: boom"}, {"error": "fetch failed: boom"}, {"content": '{"a": 1}'}])
        self.assertIsNone(out)
        self.assertEqual(len(seen), 2)


class BriefTests(unittest.TestCase):
    BRIEF = {"title_en": "T", "author": "A", "addressee": "X", "genre": "letter", "occasion": "O", "argument": "Arg",
             "outline": [{"sections": ["1"], "move": "m"}], "cast": [], "voices": [], "names": {"Sion": "Zion"},
             "scripture": "LXX", "key_terms": [],
             "glossary": [{"source_term": "logos", "english": "Word", "sense": "s", "banned": ["Reason"],
                           "votes": {"drafter": "Word", "kimi": "Word"}, "decided_by": "auto-centroid", "decision_note": "n"}]}

    def test_section_brief_fields(self):
        d = json.loads(W.section_brief_text(self.BRIEF))
        self.assertEqual(set(d), set(W.SECTION_BRIEF_KEYS))
        self.assertNotIn("occasion", d)
        self.assertNotIn("addressee", d)
        self.assertEqual(d["glossary"], [{"source_term": "logos", "english": "Word", "sense": "s", "banned": ["Reason"]}])

    def test_full_brief_text_unchanged(self):
        d = json.loads(W.brief_text(self.BRIEF))
        self.assertIn("occasion", d)
        self.assertIn("votes", d["glossary"][0])

    def test_brief_validates(self):
        self.assertTrue(W.brief_validates(self.BRIEF, []))
        self.assertTrue(W.brief_validates(self.BRIEF, [{"field": "outline"}]))
        self.assertFalse(W.brief_validates(self.BRIEF, [{"field": "outline"}, {"field": "occasion"}]))
        self.assertFalse(W.brief_validates(self.BRIEF, [{"field": "cast"}]))
        self.assertFalse(W.brief_validates(self.BRIEF, [{"field": "other"}]))
        self.assertFalse(W.brief_validates({**self.BRIEF, "key_terms": None}, []))

    def test_make_brief_one_attempt_when_valid(self):
        n = {"draft": 0}

        def fake_call(model, system, user, max_tokens=0, expect=()):
            if "general editor" in system:
                n["draft"] += 1
                return dict(self.BRIEF)
            if "verify a work brief" in system:
                return {"problems": [{"field": "outline", "claim": "c", "verdict": "wrong"}]}
            return {"votes": []}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "STAGE", Path(d)), \
                mock.patch.object(W, "call", fake_call), mock.patch.object(W, "vote_glossary", return_value=([], [])):
            b = W.make_brief("s", [{"id": "1", "source": ["x"]}], "grc", {})
        self.assertEqual(n["draft"], 1)
        self.assertEqual(len(b["_unresolved_facts"]), 1)


class PassBRedoTests(unittest.TestCase):
    def test_redraft_pass_b_keeps_pass_a(self):
        j = {"section": "1", "pass_a_gloss": "LIT", "lemmas": [{"form": "a"}], "choices": [{"term": "t"}],
             "_part_notes": [{"lemmas": [{"form": "a"}], "choices": [{"term": "t"}], "bible_refs": []}],
             "pass_b_english": ["old"], "_gate": ["near-copies"]}
        seen = []

        def fake_call(model, system, user, max_tokens=0, expect=()):
            seen.append((system, user))
            return {"pass_b_english": ["New English."]}
        with mock.patch.object(W, "call", fake_call), mock.patch.object(W, "log"):
            out = W.redraft_pass_b("s", j, {"id": "1", "source": ["src words."]}, "", {}, "Greek", "- HOW TO FIX: x")
        self.assertEqual(out["pass_a_gloss"], "LIT")
        self.assertEqual(out["pass_b_english"], ["New English."])
        self.assertNotIn("_gate", out)
        self.assertEqual(len(seen), 1)
        self.assertIn("reading English", seen[0][0])
        self.assertIn("HOW TO FIX", seen[0][1])
        self.assertIn('"term": "t"', seen[0][1])

    def test_redraft_needs_matching_parts(self):
        j = {"pass_a_gloss": "LIT", "_part_notes": [{}, {}]}
        with mock.patch.object(W, "call") as c:
            self.assertIsNone(W.redraft_pass_b("s", j, {"id": "1", "source": ["x."]}, "", {}, "Greek", ""))
        c.assert_not_called()


class SectionLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patches = [mock.patch.object(W, "STAGE", Path(self.tmp.name)), mock.patch.object(W, "log")]
        for p in self.patches:
            p.start()
        self.pairs = [{"id": "1", "source": ["src."], "english": [], "lang": "grc", "src_file": None}]

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_near_copy_redoes_pass_a_and_keeps_pass_b(self):
        # 2026-10-06: Pass A (the gloss) was the fluent side; Pass B stays.
        gates = iter([["Pass A and Pass B are near-copies"], [], []])
        drafts, redos = [], []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}

        def fake_redo(slug, j, *a, **k):
            redos.append(1)
            return {**{k2: v for k2, v in j.items() if k2 != "_gate"}, "pass_a_gloss": "A2 [the]"}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_a", fake_redo), \
                mock.patch.object(W, "redraft_pass_b") as rb, \
                mock.patch.object(W, "section_gate", lambda j, b: next(gates, [])), \
                mock.patch.object(W, "check_section", return_value={"confirmed": [], "rejected": []}):
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual((len(drafts), len(redos)), (1, 1))
        rb.assert_not_called()
        self.assertEqual(j["_status"], "pass")
        self.assertEqual((j["pass_a_gloss"], j["pass_b_english"]), ("A2 [the]", ["B."]))

    def test_still_near_copy_after_pass_a_redo_holds_at_once(self):
        drafts, redos = [], []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}

        def fake_redo(slug, j, *a, **k):
            redos.append(1)
            return {k2: v for k2, v in j.items() if k2 != "_gate"}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_a", fake_redo), \
                mock.patch.object(W, "section_gate", lambda j, b: ["Pass A and Pass B are near-copies"]), \
                mock.patch.object(W, "check_section") as cs:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual((len(drafts), len(redos)), (1, 1), "no full redrafts for a near-copy")
        self.assertEqual(j["_status"], "hold")
        self.assertIn("near-copies", j["_why"])
        cs.assert_not_called()

    def test_failed_pass_a_redo_falls_back_to_one_full_redraft(self):
        drafts = []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_a", return_value=None), \
                mock.patch.object(W, "section_gate", lambda j, b: ["Pass A and Pass B are near-copies"]), \
                mock.patch.object(W, "check_section") as cs:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual(len(drafts), 2)
        self.assertEqual(j["_status"], "hold")
        cs.assert_not_called()

    def test_other_structural_failures_still_capped(self):
        drafts = []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_a") as ra, \
                mock.patch.object(W, "section_gate", lambda j, b: ["Pass A is too short to constrain Pass B"]), \
                mock.patch.object(W, "check_section") as cs:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        ra.assert_not_called()
        self.assertEqual(len(drafts), 1 + W.MAX_FULL_REDRAFTS)
        self.assertEqual(j["_status"], "hold")
        cs.assert_not_called()

    def test_redraft_pass_a_keeps_pass_b(self):
        j = {"section": "1", "pass_a_gloss": "fluent", "pass_b_english": ["Keep me."], "_gate": ["near-copies"]}
        seen = []

        def fake_call(model, system, user, max_tokens=0, expect=()):
            seen.append((system, user))
            return {"pass_a_gloss": "word [by] word"}
        with mock.patch.object(W, "call", fake_call), mock.patch.object(W, "log"):
            out = W.redraft_pass_a("s", j, {"id": "1", "source": ["src words."]}, "Greek")
        self.assertEqual((out["pass_a_gloss"], out["pass_b_english"]), ("word [by] word", ["Keep me."]))
        self.assertNotIn("_gate", out)
        self.assertEqual(len(seen), 1)
        self.assertIn("square brackets", seen[0][0])
        self.assertNotIn("Keep me", seen[0][1], "the redo never sees Pass B")

    def run_repair_fail(self, confirmed, referee_out):
        rep = []

        def fake_repair(*a, **k):
            rep.append(1)
            return None, "call"
        with mock.patch.object(W, "draft_section", return_value={"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}), \
                mock.patch.object(W, "section_gate", return_value=[]), \
                mock.patch.object(W, "check_section", return_value={"confirmed": confirmed, "rejected": []}), \
                mock.patch.object(W, "repair_attempt", fake_repair), \
                mock.patch.object(W, "referee", return_value=referee_out) as rf:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        return j, len(rep), rf

    def test_repair_call_failure_retried_then_holds_without_referee(self):
        # A failed repair never certifies early, even when a referee would clear it.
        j, n, rf = self.run_repair_fail([{"class": "omission", "quote": "B", "upheld_by": "x"}], [])
        self.assertEqual(n, 2)
        rf.assert_not_called()
        self.assertEqual(j["_status"], "hold")
        self.assertEqual(j["_why"], "repair failed")

    def test_both_checker_finding_holds_without_referee(self):
        j, n, rf = self.run_repair_fail([{"class": "omission", "quote": "B", "agreed_by": ["a", "b"]}], [])
        rf.assert_not_called()
        self.assertEqual(j["_status"], "hold")
        self.assertEqual(j["_why"], "repair failed")

    def run_no_edits(self, referee_out):
        conf = [{"class": "omission", "quote": "B", "upheld_by": "x"}]
        with mock.patch.object(W, "draft_section", return_value={"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}), \
                mock.patch.object(W, "section_gate", return_value=[]), \
                mock.patch.object(W, "check_section", return_value={"confirmed": conf, "rejected": []}), \
                mock.patch.object(W, "repair_attempt", return_value=(None, "no-edits")) as ra, \
                mock.patch.object(W, "referee", return_value=referee_out) as rf:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual(ra.call_count, 1, "no-edits is an answer, not a transient failure")
        rf.assert_called_once()
        self.assertEqual(rf.call_args.args[2], conf)
        return j

    def test_no_edit_repair_goes_to_referee_and_passes(self):
        # 2026-10-06: declining to edit correct English held 33 sections.
        j = self.run_no_edits([])
        self.assertEqual(j["_status"], "pass")
        self.assertEqual(j["checks"]["repair"], "no edits")

    def test_no_edit_repair_holds_on_referee_findings(self):
        f = {"class": "omission", "quote": "B", "referee": "r"}
        j = self.run_no_edits([f])
        self.assertEqual(j["_status"], "hold")
        self.assertIn("confirmed problems", j["_why"], "held_review picks these up")
        self.assertEqual(j["open_findings"], [f])


class CheckCacheTests(unittest.TestCase):
    def test_baseline_cached_by_text(self):
        W._CHECK_CACHE.clear()
        sec = {"id": "1", "source": ["s"]}
        with mock.patch.object(W, "check_section", return_value={"confirmed": [], "rejected": []}) as cs:
            W.baseline_check(sec, ["a"], {}, "Greek")
            W.baseline_check(sec, ["a"], {}, "Greek")
            W.baseline_check(sec, ["b"], {}, "Greek")
        self.assertEqual(cs.call_count, 2)

    def test_errors_not_cached(self):
        W._CHECK_CACHE.clear()
        sec = {"id": "1", "source": ["s"]}
        with mock.patch.object(W, "check_section", return_value={"error": "x", "confirmed": []}) as cs:
            W.baseline_check(sec, ["a"], {}, "Greek")
            W.baseline_check(sec, ["a"], {}, "Greek")
        self.assertEqual(cs.call_count, 2)

    def test_remembered_new_side_is_reused(self):
        W._CHECK_CACHE.clear()
        sec = {"id": "1", "source": ["s"]}
        W.remember_check(sec, ["new"], {}, {"confirmed": [], "rejected": []})
        with mock.patch.object(W, "check_section") as cs:
            W.baseline_check(sec, ["new"], {}, "Greek")
        cs.assert_not_called()


class ReadSkipTests(unittest.TestCase):
    def run_with(self, attempt, held):
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            secdir = stage / "s" / "sections"
            secdir.mkdir(parents=True)
            (secdir / "1.json").write_text(json.dumps({"_status": "hold" if held else "pass"}))
            if held == "spent":
                (secdir / "1.retries").write_text("2")
            pairs = [{"id": "1", "title": "", "source": ["x"], "english": [], "lang": "grc", "src_file": None}]
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "load_pairs", return_value=pairs), \
                    mock.patch.object(W, "book_meta", return_value={}), mock.patch.object(W, "rebalance", return_value=[]), \
                    mock.patch.object(W, "make_brief", return_value={}), mock.patch.object(W, "process_section"), \
                    mock.patch.object(W, "make_intro", return_value={}) as mi, \
                    mock.patch.object(W, "read_and_fix") as rf, mock.patch.object(W, "status"), \
                    mock.patch.object(W, "log") as lg:
                W.run("s", attempt=attempt)
            return rf.called, mi.called, [c.args[1] for c in lg.call_args_list]

    def test_first_attempt_with_held_skips_read(self):
        read, intro, logs = self.run_with(1, True)
        self.assertFalse(read)
        self.assertTrue(intro)
        self.assertIn("read skipped: 1 held", logs)

    # 2026-10-06: any section not passed skips the read on every attempt; a
    # read of a work that cannot certify is thrown away.
    def test_later_attempt_with_held_skips_read(self):
        self.assertFalse(self.run_with(2, True)[0])

    def test_no_held_reads(self):
        self.assertTrue(self.run_with(1, False)[0])

    def test_held_without_retries_left_skips_read(self):
        self.assertFalse(self.run_with(1, "spent")[0])

    def test_cli_run_with_held_skips_read(self):
        self.assertFalse(self.run_with(None, True)[0])


class RegateTests(unittest.TestCase):
    def test_regate_reopens_passing_gate_holds(self):
        import regate_held as RG
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            sec = stage / "bk" / "sections"
            sec.mkdir(parents=True)
            (stage / "bk" / "brief.json").write_text(json.dumps({"names": {"Sion": "Zion"}, "glossary": []}))
            ok = {"section": "1", "source_text": "x.", "pass_b_english": ["A vision came."], "_status": "hold",
                  "_why": "gate: names: 'Sion' left unexplained (modern: 'Zion')"}
            bad = {"section": "2", "source_text": "x.", "pass_b_english": ["Up to Sion."], "_status": "hold",
                   "_why": "gate: names: 'Sion' left unexplained (modern: 'Zion')"}
            dispute = {"section": "3", "pass_b_english": ["Fine."], "_status": "hold", "_why": "2 confirmed problems after 3 repairs"}
            for name, j in (("1", ok), ("2", bad), ("3", dispute)):
                (sec / f"{name}.json").write_text(json.dumps(j))
            (sec / "1.retries").write_text("2")
            (sec / "9.gatehold.json").write_text(json.dumps({**ok, "section": "9"}))
            q = stage / "queue.json"
            q.write_text(json.dumps({"bk": {"result": "held", "attempts": 2, "words": 10}}))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "QUEUE_LOG", q), \
                    mock.patch.object(W, "check_record", return_value=[]), \
                    mock.patch.object(W, "output_guard_errors", return_value=[]):
                dry = RG.regate(True)
                self.assertEqual((dry["held_by_gate"], dry["reopened"], dry["still_fail"]), (2, 1, 1))
                self.assertTrue((sec / "1.json").exists())
                real = RG.regate(False)
            self.assertEqual(real["reopened"], 1)
            self.assertFalse((sec / "1.json").exists())
            self.assertTrue((sec / "1.gatehold.json").exists())
            self.assertFalse((sec / "1.retries").exists())
            self.assertTrue((sec / "2.json").exists() and (sec / "3.json").exists())
            row = json.loads(q.read_text())["bk"]
            self.assertEqual((row["result"], row["attempts"], row["words"]), ("reopened", 0, 10))


# ---------------------------------------------------------------- stall fixes (2026-10-03)

JER = {"source_term": "Ἱερουσαλήμ", "english": "Jerusalem", "banned": ["the Church", "the soul"]}
CHURCH = {"source_term": "ἐκκλησία", "english": "church", "banned": ["assembly"]}
WAY = {"source_term": "ὁδὸς τοῦ φωτός / ὁδὸς τοῦ σκότους", "english": "way of light",
       "banned": ["path of light", "two ways"]}


def rec(src, text):
    return {"section": "1", "source_text": src, "pass_b_english": [text]}


class BannedSourcePresenceTests(unittest.TestCase):
    def test_ban_skipped_when_term_not_in_section_source(self):
        errs = gate_only(rec("καὶ εἶπεν ὁ θεὸς πρὸς αὐτόν.", "Then the soul rejoiced."), {"glossary": [JER]})
        self.assertEqual(errs, [])

    def test_ban_holds_when_term_in_source_any_accent_or_case(self):
        for src in ("ἀνέβη εἰς Ἰερουσαλὴμ ἡ πόλις.", "ΙΕΡΟΥΣΑΛΗΜ ΠΟΛΙΣ.", "τῆς Ἱερουσαλὴμ λέγει."):
            errs = gate_only(rec(src, "He went up to the soul."), {"glossary": [JER]})
            self.assertTrue(any("banned rendering 'the soul'" in e for e in errs), (src, errs))

    def test_ban_dropped_where_common_source_word_present(self):
        src = "ἡ Ἱερουσαλὴμ καὶ ἡ ψυχὴ αὐτοῦ."
        self.assertEqual(gate_only(rec(src, "Jerusalem and the soul."), {"glossary": [JER]}), [])

    def test_ban_equal_to_other_entry_english_dropped(self):
        src = "ἡ Ἱερουσαλὴμ καὶ ἡ ἐκκλησία."
        brief = {"glossary": [JER, CHURCH]}
        self.assertEqual(gate_only(rec(src, "Jerusalem, that is, the Church."), brief), [])
        # without the church entry the ban still stands where Jerusalem is named
        errs = gate_only(rec("ἡ Ἱερουσαλὴμ πόλις.", "the Church."), {"glossary": [JER]})
        self.assertTrue(any("the Church" in e for e in errs), errs)

    def test_multiword_source_term_any_content_word(self):
        errs = gate_only(rec("ἡ τοῦ φωτὸς ἐστίν.", "This is the path of light."), {"glossary": [WAY]})
        self.assertTrue(any("path of light" in e for e in errs), errs)
        self.assertEqual(gate_only(rec("καὶ εἶπεν ὁ θεός.", "This is the path of light."), {"glossary": [WAY]}), [])

    def test_two_ways_allowed_where_source_says_two_ways(self):
        src = "Ὁδοὶ δύο εἰσὶν διδαχῆς, ἥ τε τοῦ φωτὸς καὶ ἡ τοῦ σκότους."
        self.assertEqual(gate_only(rec(src, "There are two ways of teaching."), {"glossary": [WAY]}), [])

    def test_lint_rule_glossary_uses_section_source(self):
        from pipeline import work_lint as wl
        brief = {"glossary": [JER]}
        with_src = wl.lint_work([{"id": "1", "text": "The soul is glad.", "source": "ὁ θεὸς λέγει."}], brief)
        self.assertFalse([f for f in with_src if f["rule"] == "glossary"])
        no_src = wl.lint_work([{"id": "1", "text": "The soul is glad."}], brief)
        self.assertTrue([f for f in no_src if f["rule"] == "glossary"])  # whole-work CLI: old rule

    def test_stems(self):
        from pipeline import work_lint as wl
        self.assertTrue(wl.term_in_source("μετάνοια", "εἰς μετανοίας ἦλθεν"))
        self.assertFalse(wl.term_in_source("μετάνοια", "εἰς τὴν πόλιν"))
        self.assertIsNone(wl.term_in_source("μετάνοια", ""))
        self.assertEqual(wl.phrase_key("The Churches"), "church")

    def test_short_headword_stem_finds_inflected_forms(self):
        # review 2026-10-03: σάρξ missed σαρκός, so 'human nature' was not gated
        from pipeline import work_lint as wl
        for term, src in (("σάρξ", "ἐν τῇ σαρκὶ αὐτοῦ"), ("πατήρ", "τοῦ πατρὸς"), ("εἰκών", "κατ' εἰκόνα")):
            self.assertTrue(wl.term_in_source(term, src), term)
        flesh = {"source_term": "σάρξ", "english": "flesh", "banned": ["human nature"]}
        errs = gate_only(rec("ὁ λόγος σὰρξ ἐγένετο καὶ τῆς σαρκὸς αὐτοῦ.", "the lowliness of human nature"),
                         {"glossary": [flesh]})
        self.assertTrue(any("human nature" in e for e in errs), errs)
        errs = gate_only(rec("διὰ τῆς σαρκὸς αὐτοῦ.", "the lowliness of human nature"), {"glossary": [flesh]})
        self.assertTrue(any("human nature" in e for e in errs), errs)

    def test_common_phrase_words_must_stand_together(self):
        # θεοῦ elsewhere in the section is not βασιλεία τοῦ θεοῦ
        heaven = {"source_term": "βασιλεία τῶν οὐρανῶν", "english": "kingdom of heaven", "banned": ["kingdom of God"]}
        apart = "ἡ βασιλεία τῶν οὐρανῶν ἐστιν ὡς κόκκος σινάπεως, καὶ πολλοὶ ἐδόξαζον τὸν θεόν."
        errs = gate_only(rec(apart, "The kingdom of God is like a mustard seed."), {"glossary": [heaven]})
        self.assertTrue(any("kingdom of God" in e for e in errs), errs)
        both = "ἡ βασιλεία τῶν οὐρανῶν, ἣν καὶ βασιλείαν τοῦ θεοῦ καλεῖ."
        self.assertEqual(gate_only(rec(both, "The kingdom of God is near."), {"glossary": [heaven]}), [])

    def test_regate_dry_run_picks_up_false_ban_holds(self):
        import regate_held as RG
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            sec = stage / "bk" / "sections"
            sec.mkdir(parents=True)
            (stage / "bk" / "brief.json").write_text(json.dumps({"glossary": [JER]}, ensure_ascii=False))
            why = "gate: glossary: banned rendering 'the soul' (use 'Jerusalem')"
            (sec / "1.json").write_text(json.dumps({**rec("ὁ θεὸς λέγει.", "The soul is glad."),
                                                    "_status": "hold", "_why": why}, ensure_ascii=False))
            (sec / "2.json").write_text(json.dumps({**rec("εἰς Ἰερουσαλήμ.", "The soul is glad."), "section": "2",
                                                    "_status": "hold", "_why": why}, ensure_ascii=False))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "QUEUE_LOG", stage / "queue.json"), \
                    mock.patch.object(W, "check_record", return_value=[]), \
                    mock.patch.object(W, "output_guard_errors", return_value=[]):
                st = RG.regate(True)
            self.assertEqual((st["held_by_gate"], st["reopened"], st["still_fail"]), (2, 1, 1))


class TwoReaderTests(unittest.TestCase):
    def test_follow_ok_needs_two_scores(self):
        self.assertFalse(W.follow_ok([5]))
        self.assertFalse(W.follow_ok([5, None]))
        self.assertFalse(W.follow_ok([True, 5]))
        self.assertTrue(W.follow_ok([4, 4]))
        self.assertFalse(W.follow_ok([5], words=100))

    def test_mean_bar_only_while_reader_edits_on(self):
        """P15 (owner 2026-10-06): with reader edits off, [3, 3] certifies; a 2 never does."""
        with mock.patch.object(W, "READ_EDITS", False):
            self.assertTrue(W.follow_ok([3, 3], words=5000))
            self.assertFalse(W.follow_ok([2, 4], words=5000))
            self.assertIn("mean waived", W.reader_bar())
        with mock.patch.object(W, "READ_EDITS", True):
            self.assertFalse(W.follow_ok([3, 3], words=5000))
            self.assertTrue(W.follow_ok([3, 4], words=5000))

    def reads(self, script):
        calls = []

        def fake(m, title, light, tokens):
            calls.append(m)
            seq = script[m]
            return seq.pop(0) if seq else {"_error": "down"}
        with mock.patch.object(W.work_read, "read_with", side_effect=fake):
            out = W.read_two("t", [])
        return out, calls

    def test_failed_read_retried_once(self):
        a, b = W.JUDGES
        out, calls = self.reads({a: [{"_error": "x"}, {"followability": 4}], b: [{"followability": 5}], W.FALLBACK: []})
        self.assertEqual(calls.count(a), 2)
        self.assertNotIn(W.FALLBACK, calls)
        self.assertEqual({m: W.reader_score(o) for m, o in out.items()}, {a: 4, b: 5})

    def test_no_score_counts_as_failure_then_fallback(self):
        a, b = W.JUDGES
        out, calls = self.reads({a: [{"summary": "x"}, {"followability": "n/a"}], b: [{"followability": 4}],
                                 W.FALLBACK: [{"followability": 3}]})
        self.assertEqual(calls.count(a), 2)
        self.assertEqual(out[W.FALLBACK]["_replaces"], a)
        self.assertEqual(sorted(W.reader_score(o) for o in out.values()), [3, 4])

    def test_both_fail_one_fallback_only(self):
        a, b = W.JUDGES
        out, calls = self.reads({a: [], b: [], W.FALLBACK: [{"followability": 5}]})
        self.assertEqual(calls.count(W.FALLBACK), 1)
        scored = [o for o in out.values() if W.reader_score(o) is not None]
        self.assertEqual(len(scored), 1)


class ReadBindingTests(unittest.TestCase):
    """B1 + B2 + B5: certification uses two scores of the text that ships."""

    def setup(self, d):
        stage = Path(d)
        (stage / "s" / "sections").mkdir(parents=True)
        (stage / "s" / "sections" / "1.json").write_text(json.dumps({"_status": "pass", "pass_b_english": ["Old text."]}))
        pairs = [{"id": "1", "title": "", "source": ["x"], "english": [], "lang": "grc", "src_file": None}]
        return stage, pairs

    def patches(self, stage, pairs):
        return [mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "load_pairs", return_value=pairs),
                mock.patch.object(W, "rebalance", return_value=[]), mock.patch.object(W, "intro_problems", return_value=[]),
                mock.patch.object(W.work_read, "verify", return_value=([], []))]

    def run_read(self, stage, pairs, rounds, polish=None, extra=(), read_edits=True):
        # These tests cover the read-fix + polish loop, which is off by default
        # since the 2026-10-05 audit (WP_READ_EDITS); test it switched on.
        seq = iter(rounds)
        from contextlib import ExitStack
        with ExitStack() as es:
            es.enter_context(mock.patch.object(W, "READ_EDITS", read_edits))
            for p in [*self.patches(stage, pairs), *extra]:
                es.enter_context(p)
            es.enter_context(mock.patch.object(W, "read_two", side_effect=lambda t, l: next(seq)))
            es.enter_context(mock.patch.object(W, "polish_section", side_effect=polish or (lambda *a: None)))
            res = W.read_and_fix("s", pairs, {}, "Greek", None)
            st = W.status("s")
        return res, st

    def test_default_readers_score_but_never_edit(self):
        """2026-10-05: with WP_READ_EDITS off, one read; no fix or polish edits the text."""
        a, b = W.JUDGES
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            rounds = [{a: {"followability": 3, "findings": []}, b: {"followability": 2, "findings": []}}] * 3
            calls = []
            with mock.patch.object(W, "repair_section", side_effect=lambda *a: calls.append("fix")):
                res, st = self.run_read(stage, pairs, rounds, polish=lambda *a: calls.append("polish"), read_edits=False)
            text = json.loads((stage / "s" / "sections" / "1.json").read_text())["pass_b_english"]
        self.assertEqual(res["round"], 0, "one read when the intro is unchanged")
        self.assertEqual(calls, [], "readers never edit the translation")
        self.assertEqual(text, ["Old text."])
        self.assertEqual(res["followability"], [3, 2])

    def test_last_round_scores_not_best(self):
        a, b = W.JUDGES
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            rounds = [{a: {"followability": 2}, b: {"followability": 5}},
                      {a: {"followability": 2}, b: {"followability": 2}},
                      {a: {"followability": 3}, b: {"followability": 2}}]
            res, st = self.run_read(stage, pairs, rounds)
        self.assertEqual(res["best_followability"], [2, 5])
        self.assertEqual(res["followability"], [3, 2])
        self.assertEqual(st["followability"], [3, 2])

    def test_passing_text_restored_when_later_round_falls(self):
        a, b = W.JUDGES
        finding = {"class": "garbled", "section": "1", "quote": "Old", "why": "w", "fix": "f"}
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            rounds = [{a: {"followability": 3}, b: {"followability": 4}},
                      {a: {"followability": 2}, b: {"followability": 3}},
                      {a: {"followability": 2}, b: {"followability": 3}}]
            clean = {"confirmed": [], "rejected": []}
            extra = [mock.patch.object(W.work_read, "verify", return_value=([finding], [])),
                     mock.patch.object(W, "repair_section", return_value={"_status": "pass", "pass_b_english": ["Fixed text."]}),
                     mock.patch.object(W, "section_gate", return_value=[]),
                     mock.patch.object(W, "check_section", return_value=clean),
                     mock.patch.object(W, "baseline_check", return_value=clean),
                     mock.patch.object(W, "remember_check")]
            res, st = self.run_read(stage, pairs, rounds, extra=extra)
            text = json.loads((stage / "s" / "sections" / "1.json").read_text())["pass_b_english"]
        self.assertEqual(text, ["Old text."])
        self.assertEqual(res["restored_from_round"], 0)
        self.assertEqual(res["all_rounds"], [[3, 4], [2, 3], [2, 3]])
        self.assertEqual(st["followability"], [3, 4])

    def test_unexplained_terms_redraft_intro_before_next_read(self):
        a, b = W.JUDGES
        term = {"class": "unexplained", "section": "1", "quote": "intelligent natures", "why": "w"}
        old = {"paragraphs": ["P1.", "P2.", "P3."], "unsupported": []}
        new = {"paragraphs": ["P1.", "P2.", "P3 explains intelligent natures."], "unsupported": []}
        seen = []
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            (stage / "s" / "intro.json").write_text(json.dumps(old))

            def mk(slug, brief, prs, terms=None):
                seen.append([t["quote"] for t in terms or []])
                (stage / "s" / "intro.json").write_text(json.dumps(new))
                return new
            views = []

            def read(t, light):
                views.append(light[0]["text"])
                return {a: {"followability": 2}, b: {"followability": 3}}
            from contextlib import ExitStack
            with ExitStack() as es:
                for p in [*self.patches(stage, pairs),
                          mock.patch.object(W.work_read, "verify", return_value=([term], [])),
                          mock.patch.object(W, "make_intro", side_effect=mk),
                          mock.patch.object(W, "read_two", side_effect=read),
                          mock.patch.object(W, "polish_section", return_value=None),
                          mock.patch.object(W, "READ_EDITS", True)]:
                    es.enter_context(p)
                res = W.read_and_fix("s", pairs, {}, "Greek", old)
        self.assertEqual(seen, [["intelligent natures"]])  # once per run
        self.assertEqual(views, ["P1.\n\nP2.\n\nP3.", "P1.\n\nP2.\n\nP3 explains intelligent natures.",
                                 "P1.\n\nP2.\n\nP3 explains intelligent natures."])
        self.assertEqual(res["round"], 2)

    def test_failed_intro_redraft_keeps_old(self):
        old = {"paragraphs": ["P1.", "P2.", "P3."], "unsupported": []}
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            (stage / "s").mkdir()
            (stage / "s" / "intro.json").write_text(json.dumps(old))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "intro_problems", return_value=[]), \
                    mock.patch.object(W, "author_dates", return_value=("A", "")), \
                    mock.patch.object(W, "research", return_value={}), mock.patch.object(W, "research_text", return_value=""), \
                    mock.patch.object(W, "call", return_value=None):
                got = W.make_intro("s", {}, [], terms=[{"quote": "x", "why": "w"}])
            self.assertEqual(got["paragraphs"], old["paragraphs"])
            self.assertEqual(json.loads((stage / "s" / "intro.json").read_text()), old)

    def test_polish_skips_low_reads_and_unflagged(self):
        a, b = W.JUDGES
        flagged = {"class": "garbled", "section": "1", "quote": "Old", "why": "w", "fix": "f"}
        for scores, findings, want in (([2, 3], [flagged], 0), ([2.5, 4], [], 0), ([2.5, 4], [flagged], 2)):
            calls = []
            with tempfile.TemporaryDirectory() as d:
                stage, pairs = self.setup(d)
                rounds = [{a: {"followability": scores[0]}, b: {"followability": scores[1]}}] * 3
                extra = [mock.patch.object(W.work_read, "verify", return_value=(findings, [])),
                         mock.patch.object(W, "repair_section", return_value=None)]
                self.run_read(stage, pairs, rounds, polish=lambda *x: calls.append(1), extra=extra)
            self.assertEqual(len(calls), want, (scores, findings))

    def test_one_reader_cannot_certify(self):
        a, b = W.JUDGES
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            res, st = self.run_read(stage, pairs, [{a: {"followability": 5}, b: {"_error": "down"}}] * 3)
        self.assertTrue(res["reader_unavailable"])
        self.assertEqual(st["read_note"], "held: reader unavailable")
        self.assertFalse(W.follow_ok(st["followability"]))

    def test_text_changed_after_read_drops_scores(self):
        a, b = W.JUDGES
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            res, st = self.run_read(stage, pairs, [{a: {"followability": 5}, b: {"followability": 5}}])
            self.assertEqual(st["followability"], [5, 5])
            (stage / "s" / "sections" / "1.json").write_text(json.dumps({"_status": "pass", "pass_b_english": ["New."]}))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "load_pairs", return_value=pairs), \
                    mock.patch.object(W, "rebalance", return_value=[]), mock.patch.object(W, "intro_problems", return_value=[]):
                st2 = W.status("s")
        self.assertIsNone(st2["followability"])
        self.assertIn("text changed", st2["read_note"])

    def test_unbound_old_read_not_used(self):
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            (stage / "s" / "read.json").write_text(json.dumps({"followability": [5, 5]}))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "load_pairs", return_value=pairs), \
                    mock.patch.object(W, "rebalance", return_value=[]), mock.patch.object(W, "intro_problems", return_value=[]):
                st = W.status("s")
        self.assertIsNone(st["followability"])

    def test_skipped_read_clears_stale_scores(self):
        with tempfile.TemporaryDirectory() as d:
            stage, pairs = self.setup(d)
            (stage / "s" / "sections" / "1.json").write_text(json.dumps({"_status": "hold"}))
            (stage / "s" / "read.json").write_text(json.dumps({"followability": [5, 5], "text_sha256": "x"}))
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "load_pairs", return_value=pairs), \
                    mock.patch.object(W, "book_meta", return_value={}), mock.patch.object(W, "rebalance", return_value=[]), \
                    mock.patch.object(W, "make_brief", return_value={}), mock.patch.object(W, "process_section"), \
                    mock.patch.object(W, "make_intro", return_value={}), mock.patch.object(W, "read_and_fix") as rf, \
                    mock.patch.object(W, "intro_problems", return_value=[]), mock.patch.object(W, "log"):
                W.run("s", attempt=1)
                st = W.status("s")
            read = json.loads((stage / "s" / "read.json").read_text())
        rf.assert_not_called()
        self.assertIsNone(st["followability"])
        self.assertIn("read skipped", st["read_note"])
        self.assertEqual(read["previous_followability"], [5, 5])


class ReviewAccuracyTests(unittest.TestCase):
    """Accuracy review 2026-10-03: paths where the new rules let text through."""

    def test_other_entry_english_drops_ban_only_where_its_word_is(self):
        brief = {"glossary": [JER, CHURCH]}
        errs = gate_only(rec("ἀνέβη εἰς Ἱερουσαλὴμ ἡ πόλις.", "He went up to the Church."), brief)
        self.assertTrue(any("the Church" in e for e in errs), errs)
        self.assertEqual(gate_only(rec("ἡ Ἱερουσαλὴμ καὶ ἡ ἐκκλησία.", "Jerusalem, the Church."), brief), [])

    def test_greek_term_over_latin_source_is_unknown_not_absent(self):
        from pipeline import work_lint as wl
        src = "Et ascendit in civitatem sanctam, et dixit ad eos verbum Domini."
        self.assertIsNone(wl.term_in_source("Ἱερουσαλήμ", src))
        errs = gate_only(rec(src, "He went up to the soul."), {"glossary": [JER]})
        self.assertTrue(any("the soul" in e for e in errs), errs)

    def test_forms_a_prefix_cannot_reach(self):
        from pipeline import work_lint as wl
        for term, src in (("θεός", "τῷ θεῷ δόξα"), ("υἱός", "τῷ υἱῷ αὐτοῦ"), ("ἀνήρ", "τοῦ ἀνδρὸς αὐτῆς"),
                          ("rex", "ad regem venit"), ("lux", "in lucem mundi"), ("deus", "verbum dei manet"),
                          ("caro", "verbum carnem factum")):
            self.assertTrue(wl.term_in_source(term, src), term)

    def test_nan_or_inf_score_cannot_certify(self):
        self.assertIsNone(W.reader_score({"followability": "nan"}))
        self.assertIsNone(W.reader_score({"followability": float("inf")}))
        self.assertFalse(W.follow_ok([float("nan"), 5], words=10))
        self.assertFalse(W.follow_ok([float("nan"), float("nan")], words=10))



class SweepTests(unittest.TestCase):
    """Held-section sweep 2026-10-03."""

    def test_glossary_findings_do_not_hold(self):
        a, b = W.CHECKERS
        gl = {"class": "glossary", "severity": "major", "quote": "Church", "source_quote": "x", "why": "w", "fix": "church"}
        real = {"class": "negation", "severity": "major", "quote": "not", "source_quote": "x", "why": "w", "fix": "f"}
        with mock.patch.object(W, "check_one", side_effect=lambda m, *r: [gl, real] if m == a else [real]), \
                mock.patch.object(W, "call", return_value={"rulings": []}):
            chk = W.check_section({"id": "1", "source": ["x"]}, ["not Church"], {}, "Greek")
        self.assertEqual([f["class"] for f in chk["confirmed"]], ["negation"])
        self.assertIn(gl, chk["minor"])

    def test_repair_prompt_allows_no_edit(self):
        src = Path(W.__file__).read_text()
        self.assertIn("leave correct English alone", src)
        self.assertNotIn("Every problem needs an edit", src)
        self.assertIn("Checkers are often wrong", W.REPAIR_SYS)



class ClaimTests(unittest.TestCase):
    """One book, one lane (spend audit 2026-10-03)."""

    def test_claim_refuses_a_book_a_live_lane_holds(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "queue.json"
            q.write_text(json.dumps({"bk": {"result": "running", "pid": os.getppid(), "attempts": 1}}))
            with mock.patch.object(W, "QUEUE_LOG", q):
                self.assertIsNone(W.claim("bk"))
                self.assertEqual(json.loads(q.read_text())["bk"]["pid"], os.getppid())

    def test_claim_takes_a_free_or_dead_book_and_keeps_its_row(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "queue.json"
            q.write_text(json.dumps({"bk": {"result": "running", "pid": 999999, "attempts": 2}}))
            with mock.patch.object(W, "QUEUE_LOG", q):
                prev = W.claim("bk")
                self.assertEqual(prev["attempts"], 2)
                row = json.loads(q.read_text())["bk"]
                self.assertEqual((row["result"], row["pid"], row["attempts"]), ("running", os.getpid(), 2))
                self.assertEqual(W.claim("new"), {})



class SourceChangeTests(unittest.TestCase):
    """2026-10-04: a repaired source must reach the lanes and void old passes."""

    def test_stale_pass(self):
        sec = {"id": "12", "source": ["Confido enim vos"]}
        good = {"_status": "pass", "source_sha256": W.sha("Confido enim vos")}
        self.assertFalse(W.is_stale(good, sec))
        self.assertTrue(W.is_stale({**good, "source_sha256": W.sha("ξονφιδο ενιμ ϝος")}, sec))
        self.assertFalse(W.is_stale({**good, "_status": "hold", "source_sha256": "x"}, sec))
        self.assertFalse(W.is_stale({"_status": "pass"}, sec), "old records without a hash are left alone")

    def test_segments_cache_refresh(self):
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            (stage / "bk").mkdir()
            seg = stage / "bk" / "segments.json"
            seg.write_text(json.dumps({"moves": [{"from": "1", "to": "2", "moved_chars": 3, "moved_start": "x"}],
                                       "sections": {"1": ["a"], "2": ["x b"], "3": ["old"]}}))
            pairs = [{"id": "1", "source": ["a"]}, {"id": "2", "source": ["changed"]}, {"id": "3", "source": ["new"]}]
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "log"):
                W.rebalance("bk", pairs)
            self.assertEqual(pairs[2]["source"], ["new"], "unmoved section takes the repaired source")
            self.assertEqual(pairs[1]["source"], ["x b"], "moved section keeps its cached cut")
            self.assertEqual(json.loads(seg.read_text())["sections"]["3"], ["new"])


# ---------------------------------------------------------------- certifier gates (audit 2026-10-06)

NOTE = "(Jerome Latin working note; lemma Luke 2:21-24. Full Rauer GCS 35 text to be locked locally.)"


class SourceGateTests(unittest.TestCase):
    """A placeholder source holds before any model call and never certifies."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.stage = Path(self.tmp.name)
        self.patches = [mock.patch.object(W, "STAGE", self.stage), mock.patch.object(W, "log")]
        for p in self.patches:
            p.start()
        self.pairs = [{"id": "20", "sid": "20", "title": "", "source": [NOTE], "english": [], "lang": "lat", "src_file": None}]

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_placeholder_holds_with_no_model_call(self):
        with mock.patch.object(W, "call") as c, mock.patch.object(W, "draft_section") as d:
            j = W.process_section("bk", 0, self.pairs, {}, "Latin")
        c.assert_not_called()
        d.assert_not_called()
        self.assertEqual((j["_status"], j["_why"], j["_permanent"]), ("hold", "no locked source", True))
        on_disk = json.loads((self.stage / "bk" / "sections" / "20.json").read_text())
        self.assertEqual(on_disk["_status"], "hold")

    def test_passed_placeholder_section_is_demoted(self):
        secdir = self.stage / "bk" / "sections"
        secdir.mkdir(parents=True)
        staged = {"section": "20", "_status": "pass", "pass_b_english": ["Luke from memory."], "source_text": NOTE,
                  "source_sha256": W.sha(NOTE), "confidence": "source_verified"}
        (secdir / "20.json").write_text(json.dumps(staged))
        with mock.patch.object(W, "call") as c:
            j = W.process_section("bk", 0, self.pairs, {}, "Latin")
        c.assert_not_called()
        self.assertEqual((j["_status"], j["confidence"]), ("hold", "held"))
        self.assertEqual(j["pass_b_english"], ["Luke from memory."], "kept for the record")
        self.assertEqual(W.staged_sections("bk", self.pairs)[0]["_j"]["_status"], "hold")

    def test_origen_luke_section_20_holds(self):
        # The staged record that passed with Luke written from memory (archived
        # 2026-10-06): both the source check and check_record now refuse it.
        real = W.ROOT / "outputs/work-pipeline/origen-luke-homilies/sections/20.json"
        archived = sorted(W.ROOT.glob("outputs/_held/*/work-pipeline/origen-luke-homilies/sections/20.json"))
        path = real if real.exists() else (archived[-1] if archived else None)
        if path is None:
            self.skipTest("origen-luke 20.json not on this machine")
        j = json.loads(path.read_text())
        sec = {"id": "20", "source": j["source_text"].split("\n")}
        self.assertTrue(W.source_problems(sec))
        self.assertTrue(any("not locked source" in e for e in W.check_record(j)))

    def test_apply_refuses_placeholder_even_from_staged_passes(self):
        st = {"sections": {"pass": 1}, "intro_ok": True, "followability": [4, 4]}
        with mock.patch.object(W, "status", return_value=st), mock.patch.object(W, "load_pairs", return_value=self.pairs), \
                mock.patch.object(W, "rebalance", return_value=[]), \
                mock.patch.object(W, "staged_sections", return_value=[{"_j": {"_status": "pass"}}]), \
                mock.patch("builtins.print") as pr:
            self.assertEqual(W.apply("bk"), 1)
        self.assertIn("no locked source", pr.call_args.args[0])


class DuplicateIdTests(unittest.TestCase):
    """Books whose files each number from 1 (audit 2026-10-06: 42 books)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.books, self.stage = root / "books", root / "stage"
        tr = self.books / "bk" / "translations"
        tr.mkdir(parents=True)
        for hom in ("hom1", "hom2"):
            (tr / f"{hom}_english.json").write_text(json.dumps(
                [{"section": "1", "title": "t", "english": ["old"]}, {"section": "2", "title": "t", "english": ["old"]}]))
            # Each homily ends mid-sentence: a move must not cross into the next file.
            (tr / f"{hom}_source.json").write_text(json.dumps(
                [{"section": "1", "latin": [f"{hom} prima pars."]},
                 {"section": "2", "latin": [f"{hom} secunda pars. et sequitur sine fine"]}]))
        self.patches = [mock.patch.object(W, "BOOKS", self.books), mock.patch.object(W, "STAGE", self.stage),
                        mock.patch.object(W, "log")]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_unique_ids_separate_files_and_certified_round_trip(self):
        pairs = W.load_pairs("bk")
        self.assertEqual([p["id"] for p in pairs], ["hom1_english:1", "hom1_english:2", "hom2_english:1", "hom2_english:2"])
        self.assertEqual([p["sid"] for p in pairs], ["1", "2", "1", "2"])
        self.assertFalse(W.duplicate_ids(pairs))
        moves = W.rebalance("bk", pairs)
        self.assertEqual(moves, [], "no move from one homily into the next")
        secdir = self.stage / "bk" / "sections"
        secdir.mkdir(parents=True)
        for p in pairs:
            (secdir / (p["id"].replace(":", "_") + ".json")).write_text(json.dumps(
                {"section": p["id"], "_status": "pass", "pass_b_english": [f"New {p['id']}."], "thought_title": "T"}))
        names = sorted(f.name for f in secdir.glob("*.json"))
        self.assertEqual(len(names), 4)
        (self.stage / "bk" / "brief.json").write_text(json.dumps({"title_en": "T"}))
        (self.stage / "bk" / "intro.json").write_text(json.dumps({"paragraphs": ["a", "b", "c"]}))
        st = {"sections": {"pass": 4}, "intro_ok": True, "followability": [4, 4]}
        with mock.patch.object(W, "status", return_value=st), mock.patch.object(W, "intro_problems", return_value=[]), \
                mock.patch("builtins.print"):
            self.assertEqual(W.apply("bk"), 0)
        h1 = json.loads((self.books / "bk" / "translations" / "hom1_english.json").read_text())
        h2 = json.loads((self.books / "bk" / "translations" / "hom2_english.json").read_text())
        self.assertEqual(h1[0]["english"], ["New hom1_english:1."])
        self.assertEqual(h2[0]["english"], ["New hom2_english:1."])
        self.assertTrue(W.certified("bk"))

    def test_old_bare_id_segments_cache_is_rebuilt(self):
        (self.stage / "bk").mkdir(parents=True)
        (self.stage / "bk" / "segments.json").write_text(json.dumps(
            {"moves": [{"from": "1", "to": "2", "moved_chars": 1, "moved_start": "x"}], "sections": {"1": ["a"], "2": ["b"]}}))
        pairs = W.load_pairs("bk")
        self.assertEqual(W.rebalance("bk", pairs), [])
        self.assertIn("hom2_english:1", json.loads((self.stage / "bk" / "segments.json").read_text())["sections"])
        # The old cache is kept beside, not overwritten (reversible data rule).
        baks = list((self.stage / "bk").glob("segments.*.bak.json"))
        self.assertEqual(len(baks), 1)
        self.assertIn("1", json.loads(baks[0].read_text())["sections"])

    def test_single_file_books_keep_bare_ids(self):
        (self.books / "bk" / "translations" / "hom2_english.json").unlink()
        self.assertEqual([p["id"] for p in W.load_pairs("bk")], ["1", "2"])

    def test_repeat_inside_one_file_still_collides(self):
        pairs = [{"id": "f:1"}, {"id": "f:1"}]
        self.assertTrue(W.duplicate_ids(pairs))


class GlossaryBanTests(unittest.TestCase):
    """Bans that hold the chosen English forbid the right word (2026-10-06)."""

    def test_ban_containing_choice_does_not_fire(self):
        brief = {"glossary": [{"source_term": "παρθένος", "english": "virgin", "banned": ["the Virgin", "Virgin"]}]}
        errs = gate_only(rec("παρθένος ἐστίν.", "She was the virgin of the prophecy."), brief)
        self.assertEqual(errs, [])

    def test_real_calque_ban_still_fires(self):
        brief = {"glossary": [{"source_term": "πνεῦμα", "english": "Holy Spirit", "banned": ["Spirit of God"]}]}
        errs = gate_only(rec("τὸ πνεῦμα λέγει.", "The Spirit of God speaks."), brief)
        self.assertTrue(any("banned rendering 'Spirit of God'" in e for e in errs), errs)

    def test_choice_inside_another_word_still_bans(self):
        # Whole words only: 'man' in 'human', 'sin' in 'missing' are not the choice.
        self.assertFalse(W.ban_contains_choice("human of God", "man of God"))
        self.assertFalse(W.ban_contains_choice("missing the mark", "sin"))
        self.assertTrue(W.ban_contains_choice("Law of Moses", "law"))
        brief = {"glossary": [{"source_term": "ἄνθρωπος", "english": "man of God", "banned": ["human of God"]}]}
        errs = gate_only(rec("ὁ ἄνθρωπος τοῦ θεοῦ λέγει.", "The human of God speaks."), brief)
        self.assertTrue(any("banned rendering 'human of God'" in e for e in errs), errs)
        brief = {"glossary": [{"source_term": "ἁμαρτία", "english": "sin", "banned": ["missing the mark"]}]}
        errs = gate_only(rec("ἡ ἁμαρτία ἐστίν.", "It is missing the mark."), brief)
        self.assertTrue(any("banned rendering 'missing the mark'" in e for e in errs), errs)

    def test_vote_glossary_drops_bans_holding_the_choice(self):
        votes = {"votes": [{"source_term": "παρθένος", "choice": "virgin", "banned": ["the Virgin", "maiden"]}]}
        with mock.patch.object(W, "call", return_value=votes):
            gl, _ = W.vote_glossary("s", [{"source_term": "παρθένος", "sense": "s", "candidates": ["virgin"]}], "", "Greek")
        self.assertEqual(gl[0]["english"], "virgin")
        self.assertEqual(gl[0]["banned"], ["maiden"])


class RetryContextTests(unittest.TestCase):
    """A retried hold starts from its findings, labelled as notes (2026-10-06)."""

    def test_retry_feedback_labels_notes_and_skips_noise(self):
        with tempfile.TemporaryDirectory() as d:
            hr = Path(d) / "held-review" / "2026-10-04"
            hr.mkdir(parents=True)
            (hr / "findings.jsonl").write_text(
                json.dumps({"id": "bk/3#0", "quote": "noisy words"}) + "\n" + json.dumps({"id": "bk/3#1", "quote": "real words"}) + "\n")
            (hr / "verdicts.jsonl").write_text(
                json.dumps({"id": "bk/3#0", "verdict": "noise"}) + "\n" + json.dumps({"id": "bk/3#1", "verdict": "real"}) + "\n")
            held = {"section": "3", "_status": "hold", "_why": "2 confirmed problems after 3 repairs",
                    "open_findings": [{"class": "omission", "quote": "noisy words", "why": "w"},
                                      {"class": "negation", "quote": "real words", "source_quote": "οὐ", "why": "not dropped"}]}
            with mock.patch.object(W, "HELD_REVIEW", Path(d) / "held-review"):
                fb = W.retry_feedback("bk", held)
        self.assertIn("checker notes, may be wrong; verify against the source", fb)
        self.assertIn("held because: 2 confirmed problems", fb)
        self.assertIn("real words", fb)
        self.assertNotIn("noisy words", fb)

    def test_retry_feedback_skips_unruled_findings(self):
        """Review 2026-10-06 (P3): a finding nobody ruled on must not steer the redraft."""
        held = {"section": "3", "_why": "1 confirmed problems after 3 repairs (+2 without a ruling)",
                "open_findings": [{"class": "negation", "quote": "ruled words", "referee": "r", "why": "w"},
                                  {"class": "omission", "quote": "referee gave none", "no_ruling": True, "referee": "r"},
                                  {"class": "omission", "quote": "checker gave none", "unruled_by": "c"}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "HELD_REVIEW", Path(d)):
            fb = W.retry_feedback("bk", held)
        self.assertIn("ruled words", fb)
        self.assertNotIn("referee gave none", fb)
        self.assertNotIn("checker gave none", fb)

    def test_process_section_passes_notes_to_the_redraft(self):
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d)
            secdir = stage / "bk" / "sections"
            secdir.mkdir(parents=True)
            (secdir / "1.json").write_text(json.dumps({"section": "1", "_status": "hold", "_why": "repair failed",
                                                      "open_findings": [{"class": "omission", "quote": "q1", "why": "gap"}]}))
            pairs = [{"id": "1", "title": "", "source": ["src."], "english": [], "lang": "grc", "src_file": None}]
            seen = []

            def fake_draft(slug, p, prev, nxt, brief, langname, feedback=""):
                seen.append(feedback)
                return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}
            with mock.patch.object(W, "STAGE", stage), mock.patch.object(W, "log"), \
                    mock.patch.object(W, "HELD_REVIEW", stage / "none"), \
                    mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "section_gate", return_value=[]), \
                    mock.patch.object(W, "check_section", return_value={"confirmed": [], "rejected": []}):
                j = W.process_section("bk", 0, pairs, {}, "Greek")
            self.assertEqual(j["_status"], "pass")
            self.assertTrue((secdir / "1.hold1.json").exists())
        self.assertIn("may be wrong", seen[0])
        self.assertIn("q1", seen[0])
        # Notes keep their own heading; they are not framed as problems to fix.
        self.assertTrue(seen[0].startswith(W.RETRY_NOTES_HEAD))
        self.assertNotIn("FIX THESE PROBLEMS", W.feedback_block(seen[0]))
        self.assertIn("FIX THESE PROBLEMS", W.feedback_block("- gate: x"))

    def test_draft_prompt_frames_retry_notes_as_notes(self):
        users = []

        def fake_call(model, system, user, **k):
            users.append(user)
            return {"pass_a_gloss": "A", "pass_b_english": ["B."]}
        notes = W.RETRY_NOTES_HEAD + " (checker notes, may be wrong; verify against the source):\n- [omission] \"q1\""
        p = {"id": "1", "source": ["src."], "lang": "grc", "src_file": None}
        with mock.patch.object(W, "call", fake_call):
            W.draft_section("bk", p, "", "", {}, "Greek", notes)
        self.assertEqual(len(users), 2, "Pass A and Pass B calls")
        for u in users:
            self.assertIn(W.RETRY_NOTES_HEAD, u)
            self.assertNotIn("FIX THESE PROBLEMS", u)


class ParkAndQueueTests(unittest.TestCase):
    def test_parked_only_when_last_attempt_changed_nothing(self):
        self.assertFalse(W.parked({"result": "held", "attempts": 1, "stalled": True}))
        self.assertTrue(W.parked({"result": "held", "attempts": 2}), "old rows stay parked")
        self.assertTrue(W.parked({"result": "held", "attempts": 2, "stalled": True}))
        self.assertFalse(W.parked({"result": "held", "attempts": 2, "stalled": False}))
        self.assertTrue(W.parked({"result": "held", "attempts": W.PARK_MAX, "stalled": False}), "bounded")
        self.assertFalse(W.parked({"result": "reopened", "attempts": 0}))

    def test_old_row_stays_parked_and_can_move_is_ready(self):
        """Red team 2026-10-06 (P3): releasing old-format parked rows waits for
        the owner, so they stay parked; can_move() is the ready-made test for
        that release (a held section with a retry left can move)."""
        row = {"result": "held", "attempts": 2}
        pairs = [{"id": "1"}, {"id": "2 a"}]
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "STAGE", Path(d)):
            sd = Path(d) / "bk" / "sections"
            sd.mkdir(parents=True)
            put = lambda name, j: (sd / name).write_text(json.dumps(j))  # noqa: E731
            put("1.json", {"_status": "pass"})
            self.assertTrue(W.parked(row, "bk", pairs), "old rows stay parked until the owner decides")
            self.assertTrue(W.can_move("bk", pairs), "a section never staged can move")
            put("2_a.json", {"_status": "pass"})
            self.assertFalse(W.can_move("bk", pairs), "all pass: stays parked")
            put("2_a.json", {"_status": "hold", "_why": "1 confirmed problems after 3 repairs"})
            (sd / "2_a.retries").write_text("1")
            self.assertTrue(W.can_move("bk", pairs), "a hold with a retry left runs again")
            (sd / "2_a.retries").write_text("2")
            self.assertFalse(W.can_move("bk", pairs), "out of retries")
            (sd / "2_a.retries").unlink()
            put("2_a.json", {"_status": "hold", "_why": "no locked source", "_permanent": True})
            self.assertFalse(W.can_move("bk", pairs), "a source hold waits for a person")
            put("2_a.json", {"_status": "hold"})
            self.assertTrue(W.parked({**row, "stalled": True}, "bk", pairs), "a recorded stall still parks")
            self.assertTrue(W.parked({**row, "attempts": W.PARK_MAX}, "bk", pairs), "bounded")
            self.assertTrue(W.parked(row), "no book given: as before")

    def run_queue(self, pairs, rows=None, status=None):
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "queue.json"
            q.write_text(json.dumps(rows or {}))
            with mock.patch.object(W, "QUEUE_LOG", q), mock.patch.object(W, "STAGE", Path(d)), \
                    mock.patch.object(W, "site_books", return_value=[(10, "bk")]), \
                    mock.patch.object(W, "certified", return_value=False), \
                    mock.patch.object(W, "load_pairs", return_value=pairs), \
                    mock.patch.object(W, "run", return_value=0) as run, \
                    mock.patch.object(W, "status", return_value=status or {"sections": {"hold": 1}}), \
                    mock.patch.object(W, "log"), mock.patch("builtins.print"), \
                    mock.patch.dict(sys.modules, {"audit_log": mock.MagicMock()}):
                W.queue(5, 0)
            return run.called, json.loads(q.read_text()).get("bk")

    def test_missing_site_dist_does_not_list_books(self):
        with tempfile.TemporaryDirectory() as d:
            scripts = Path(d) / "scripts"
            scripts.mkdir()
            with mock.patch.object(W, "SITE_SCRIPTS", scripts):
                with self.assertRaises(W.CatalogueUnavailable):
                    W.site_books(False)
                with self.assertRaises(W.CatalogueUnavailable):
                    W.site_books(True)

    def test_queue_exits_when_the_site_dist_is_missing(self):
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "queue.json"
            q.write_text("{}")
            with mock.patch.object(W, "QUEUE_LOG", q), \
                    mock.patch.object(W, "site_books", side_effect=W.CatalogueUnavailable("dist/works")), \
                    mock.patch.object(W, "run") as run, \
                    mock.patch("builtins.print"):
                self.assertEqual(W.queue(5, 0), 0)
            self.assertFalse(run.called)

    def test_duplicate_ids_skip_without_a_run(self):
        ran, row = self.run_queue([{"id": "1", "source": ["x."]}, {"id": "1", "source": ["y."]}])
        self.assertFalse(ran)

    def test_placeholder_source_marks_needs_source_without_a_run(self):
        ran, row = self.run_queue([{"id": "20", "source": [NOTE]}], rows={"bk": {"result": "held", "attempts": 1}})
        self.assertFalse(ran)
        self.assertEqual(row["result"], "needs-source")
        self.assertIn("20", row["why"])

    def test_row_records_whether_the_attempt_moved(self):
        ok = [{"id": "1", "source": ["Verba sunt."]}]
        prev = {"bk": {"result": "held", "attempts": 1, "status": {"sections": {"hold": 1}}}}
        ran, row = self.run_queue(ok, rows=prev, status={"sections": {"hold": 1}})
        self.assertTrue(ran)
        self.assertEqual((row["attempts"], row["stalled"]), (2, True))
        self.assertTrue(W.parked(row))
        ran, row = self.run_queue(ok, rows=prev, status={"sections": {"pass": 1}, "intro_ok": False})
        self.assertEqual((row["attempts"], row["stalled"]), (2, False))
        self.assertFalse(W.parked(row))


class CheckerBudgetTests(unittest.TestCase):
    """Kimi replies were cut off; glossary findings were never used (2026-10-06)."""

    def test_check_prompt_drops_glossary_and_caps_findings(self):
        self.assertNotIn("- glossary:", W.CHECK_SYS)
        self.assertIn("at most 12 findings, majors first", W.CHECK_SYS)

    def test_cf_call_length_finish_is_truncated(self):
        body = {"success": True, "result": {"choices": [{"message": {"content": '{"findings": ['}, "finish_reason": "length"}],
                                            "usage": {"completion_tokens": 6000}}}
        with mock.patch.object(LB.urllib.request, "urlopen", lambda req, timeout=0: FakeResp(json.dumps(body).encode())):
            r = LB.cf_call("@cf/moonshotai/kimi-k2.6", [], "t", "a")
        self.assertEqual((r["error"], r["ct"], r["content"]), (LB.TRUNCATED_LENGTH, 6000, '{"findings": ['))
        body["result"]["choices"][0]["finish_reason"] = "stop"
        with mock.patch.object(LB.urllib.request, "urlopen", lambda req, timeout=0: FakeResp(json.dumps(body).encode())):
            self.assertEqual(LB.cf_call("@cf/moonshotai/kimi-k2.6", [], "t", "a")["content"], '{"findings": [')

    def test_cf_chat_api_length_finish_is_truncated(self):
        body = {"choices": [{"message": {"content": "{"}, "finish_reason": "length"}], "usage": {"completion_tokens": 9}}
        with mock.patch.object(LB.urllib.request, "urlopen", lambda req, timeout=0: FakeResp(json.dumps(body).encode())):
            r = LB.cf_call("m", [], "t", "a", api="chat")
        self.assertEqual(r["error"], LB.TRUNCATED_LENGTH)

    def test_fallback_round_is_tagged(self):
        a, b = W.CHECKERS
        with mock.patch.object(W, "check_one", side_effect=lambda m, *r: None if m == a else []):
            chk = W.check_section({"id": "1", "source": ["x"]}, ["y"], {}, "Greek")
        self.assertEqual(chk["fallback"], [a])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "STAGE", Path(d)), mock.patch.object(W, "log"), \
                mock.patch.object(W, "draft_section", return_value={"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}), \
                mock.patch.object(W, "section_gate", return_value=[]), \
                mock.patch.object(W, "check_section", return_value={"confirmed": [], "rejected": [], "fallback": [a]}):
            j = W.process_section("s", 0, [{"id": "1", "source": ["src."], "english": [], "lang": "grc", "src_file": None}], {}, "Greek")
        self.assertEqual(j["checks"]["fallback"][0]["checker"], "fallback")
        self.assertEqual(j["checks"]["fallback"][0]["replaced"], [a])

    def test_majority_term_hyphen_needs_both_judges(self):
        self.assertEqual(W.majority_term({"drafter": "chastity", "kimi": "chastity", "glm": "purity"}), "chastity")
        self.assertEqual(W.majority_term({"drafter": "belly-dancer", "kimi": "belly-dancer", "glm": "medium"}), "")
        self.assertEqual(W.majority_term({"drafter": "life-bringing", "kimi": "life-giving", "glm": "life-giving"}), "life-giving")
        self.assertEqual(W.majority_term({"drafter": "a", "kimi": "b", "glm": "c"}), "")

    def test_only_a_final_round_or_referee_fallback_blocks(self):
        hist = [{"round": 0, "fallback": ["x"]}, {"round": 1}]
        early = {"_status": "pass", "check_history": hist,
                 "checks": {"referee": W.REFEREE, "fallback": [{"round": 0, "checker": "fallback"}]}}
        self.assertFalse(W.used_fallback(early))
        self.assertEqual(W.block_fallback_pass(dict(early))["_status"], "pass")
        final = {**early, "checks": {"referee": W.REFEREE, "fallback": [{"round": 1, "checker": "fallback"}]}}
        self.assertTrue(W.used_fallback(final))
        self.assertTrue(W.used_fallback({"checks": {"referee": W.FALLBACK}}))
        self.assertTrue(W.used_fallback({"checks": {"fallback": [{"round": 0}]}}))  # rounds unknown: hold

    def run_referee_pass(self, nim_up):
        """No-edits path with the real referee(); only call() is mocked."""
        conf = [{"class": "omission", "quote": "B", "upheld_by": "x"}]

        def fake_call(model, system, user, **k):
            if model == W.REFEREE and not nim_up:
                return None
            return {"rulings": [{"n": 1, "real": False, "why": "fine"}]}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "STAGE", Path(d)), mock.patch.object(W, "log"), \
                mock.patch.object(W, "draft_section", return_value={"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}), \
                mock.patch.object(W, "section_gate", return_value=[]), \
                mock.patch.object(W, "check_section", return_value={"confirmed": conf, "rejected": []}), \
                mock.patch.object(W, "repair_attempt", return_value=(None, "no-edits")), \
                mock.patch.object(W, "call", fake_call):
            return W.process_section("s", 0, [{"id": "1", "source": ["src."], "english": [], "lang": "grc", "src_file": None}], {}, "Greek")

    def test_referee_pass_names_the_model_that_ruled(self):
        j = self.run_referee_pass(nim_up=True)
        self.assertEqual((j["_status"], j["checks"]["referee"]), ("pass", W.REFEREE))
        self.assertNotIn("fallback", j["checks"])
        j = self.run_referee_pass(nim_up=False)
        # The fallback referee is named, and its ruling does not certify (Wave A, 2026-10-07).
        self.assertEqual((j["_status"], j["checks"]["referee"]), ("hold", W.FALLBACK))
        self.assertEqual(j["checks"]["fallback"][-1]["checker"], "referee")
        self.assertEqual(j["checks"]["fallback"][-1]["model"], W.FALLBACK)


class ReadWithTruncationTests(unittest.TestCase):
    """cf_call now flags a cut-off reply as an error but keeps its text (2026-10-06)."""

    def run_read(self, replies):
        seen = []

        def fake(model, msgs, cf_token="", nv_token="", max_tokens=0):
            seen.append(max_tokens)
            return replies[len(seen) - 1]
        with mock.patch.object(R, "vendor_call", fake), mock.patch.object(R.time, "sleep") as sl:
            out = R.read_with("m", "T", [{"id": "1", "title": "t", "text": "x"}], {"cf": "", "nv": ""})
        return out, seen, sl

    def test_cut_off_reply_whose_json_closed_is_used(self):
        out, seen, sl = self.run_read([{"error": LB.TRUNCATED_LENGTH, "content": '{"followability": 4, "findings": []}'}])
        self.assertEqual(out["followability"], 4)
        self.assertEqual(seen, [8000])
        sl.assert_not_called()

    def test_cut_off_unparseable_grows_budget_once(self):
        cut = {"error": LB.TRUNCATED_LENGTH, "content": '{"findings": ['}
        out, seen, sl = self.run_read([cut, {"content": '{"followability": 3, "findings": []}'}])
        self.assertEqual(out["followability"], 3)
        self.assertEqual(seen, [8000, 16000])
        sl.assert_not_called()
        out, seen, _ = self.run_read([cut, cut, cut])
        self.assertEqual(seen, [8000, 16000, 16000], "bounded: 3 tries, one growth")
        self.assertIn("cut off", out["_error"])

    def test_other_errors_still_back_off(self):
        out, seen, sl = self.run_read([{"error": "503"}] * 3)
        self.assertEqual(out["_error"], "503")
        self.assertEqual(sl.call_count, 3)


class NoRulingTests(unittest.TestCase):
    """Red team 2026-10-06 (P3): a missing ruling neither confirms a finding
    nor lets a repair edit the English; a dead lane's running row is cleared."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patches = [mock.patch.object(W, "STAGE", Path(self.tmp.name)), mock.patch.object(W, "log")]
        for p in self.patches:
            p.start()
        self.pairs = [{"id": "1", "source": ["src."], "english": [], "lang": "grc", "src_file": None}]

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_check_section_without_ruling_is_unruled_not_confirmed(self):
        a, b = W.CHECKERS
        f = {"class": "omission", "severity": "major", "quote": "x", "source_quote": "y", "why": "w", "fix": "f"}
        for reply in (None, {"rulings": []}, {"rulings": [{"n": 1, "why": "?"}]}, {"rulings": [{"n": 1, "real": "yes"}]}):
            with mock.patch.object(W, "check_one", side_effect=lambda m, *r: [f] if m == a else []), \
                    mock.patch.object(W, "call", return_value=reply):
                chk = W.check_section({"id": "1", "source": ["x"]}, ["y"], {}, "Greek")
            self.assertEqual(chk["confirmed"], [], reply)
            self.assertEqual(chk["rejected"], [], reply)
            self.assertEqual(len(chk["unruled"]), 1, reply)
        with mock.patch.object(W, "check_one", side_effect=lambda m, *r: [f] if m == a else []), \
                mock.patch.object(W, "call", return_value={"rulings": [{"n": 1, "real": True, "why": "r"}]}):
            self.assertEqual(len(W.check_section({"id": "1", "source": ["x"]}, ["y"], {}, "Greek")["confirmed"]), 1)

    def run_section(self, chk, referee_out, repair=(None, "no-edits")):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(W, "STAGE", Path(d)), \
                mock.patch.object(W, "draft_section", return_value={"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}), \
                mock.patch.object(W, "section_gate", return_value=[]), \
                mock.patch.object(W, "check_section", return_value=chk), \
                mock.patch.object(W, "repair_attempt", return_value=repair) as ra, \
                mock.patch.object(W, "referee", return_value=referee_out) as rf:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        return j, ra, rf

    def test_unruled_only_applies_no_edit_and_referee_rules(self):
        u = {"class": "omission", "quote": "B", "unruled_by": "x"}
        j, ra, rf = self.run_section({"confirmed": [], "rejected": [], "unruled": [u]}, [])
        ra.assert_not_called()
        self.assertEqual(rf.call_args.args[2], [u])
        self.assertEqual(j["_status"], "pass")
        # The referee gives no ruling either: hold, no edit, not "confirmed".
        j, ra, rf = self.run_section({"confirmed": [], "rejected": [], "unruled": [u]}, [{**u, "no_ruling": True}])
        ra.assert_not_called()
        self.assertEqual(j["_status"], "hold")
        self.assertEqual(j["_why"], "1 problems without a ruling after 0 repairs")
        self.assertNotIn("confirmed problems", j["_why"])

    def test_early_referee_upholds_an_unruled_finding(self):
        """Review 2026-10-06 (P3): at an early round with only unruled findings
        the referee rules; repair gets only what it upheld, and both the
        no-edits and repair-failed branches reuse that ruling with no second
        referee call."""
        u1 = {"class": "omission", "quote": "A", "unruled_by": "x"}
        u2 = {"class": "omission", "quote": "B", "unruled_by": "y"}
        upheld, none = {**u1, "referee": "r", "referee_why": "real"}, {**u2, "referee": "r", "no_ruling": True}
        chk = {"confirmed": [], "rejected": [], "unruled": [u1, u2]}
        for repair, why in (((None, "no-edits"), "1 confirmed problems after 0 repairs (+1 without a ruling); repair made no edit"),
                            ((None, "bad"), "repair failed")):
            j, ra, rf = self.run_section(chk, [upheld, none], repair)
            self.assertEqual(rf.call_count, 1, repair)
            self.assertEqual(rf.call_args.args[2], [u1, u2], repair)
            self.assertEqual(ra.call_count, 1, repair)
            self.assertEqual(ra.call_args.args[2], [upheld], "only the upheld finding is repaired")
            self.assertEqual((j["_status"], j["_why"]), ("hold", why))
            self.assertEqual(j["open_findings"], [upheld, none])

    def test_repair_gets_only_ruled_findings(self):
        c = {"class": "negation", "quote": "A", "upheld_by": "x"}
        u = {"class": "omission", "quote": "B", "unruled_by": "y"}
        j, ra, rf = self.run_section({"confirmed": [c], "rejected": [], "unruled": [u]}, [c])
        self.assertEqual(ra.call_args.args[2], [c], "the unruled finding is never sent to repair")
        self.assertEqual(rf.call_args.args[2], [c, u], "the referee rules on both")
        self.assertEqual(j["_why"], "1 confirmed problems after 0 repairs; repair made no edit")

    def test_referee_without_ruling_keeps_finding_as_unruled(self):
        f = {"class": "omission", "quote": "B", "upheld_by": "x"}
        for reply in (None, {"rulings": []}, {"rulings": [{"n": 1, "real": "maybe"}]}):
            with mock.patch.object(W, "call", return_value=reply):
                out = W.referee({"source": ["s"]}, ["e"], [f], "Greek")
            self.assertEqual(len(out), 1, reply)
            self.assertTrue(out[0]["no_ruling"], reply)
        with mock.patch.object(W, "call", return_value={"rulings": [{"n": 1, "real": False}]}):
            self.assertEqual(W.referee({"source": ["s"]}, ["e"], [f], "Greek"), [])

    def test_open_count_includes_unruled(self):
        self.assertEqual(W.open_count({"confirmed": [1], "unruled": [2, 3]}), 3)

    def test_dead_lane_running_row_is_cleared(self):
        import subprocess
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()  # reaped, so its pid is gone
        q = Path(self.tmp.name) / "queue.json"
        q.write_text(json.dumps({
            "dead": {"result": "running", "pid": p.pid, "at": "2026-10-06T04:08:06", "attempts": 1},
            "live": {"result": "running", "pid": os.getppid(), "at": "x"},
            "held": {"result": "held", "attempts": 2}}))
        with mock.patch.object(W, "QUEUE_LOG", q):
            self.assertEqual(W.reap_dead_rows(), ["dead"])
            self.assertEqual(W.reap_dead_rows(), [])
        rows = json.loads(q.read_text())
        self.assertEqual((rows["dead"]["result"], rows["dead"]["attempts"]), ("crash", 2))
        self.assertIn(str(p.pid), rows["dead"]["why"])
        self.assertEqual(rows["live"]["result"], "running")
        self.assertEqual(rows["held"], {"result": "held", "attempts": 2})


if __name__ == "__main__":
    unittest.main()
