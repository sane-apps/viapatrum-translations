#!/usr/bin/env python3
"""Offline tests for the work_pipeline efficiency changes (2026-10-03).

No network and no LLM: every model call is replaced by a stub.
Run: python3 scripts/test_work_pipeline_efficiency.py
"""
from __future__ import annotations

import io
import json
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
    def run_call(self, replies):
        seq = iter(replies)
        seen = []

        def fake(model, msgs, **kw):
            seen.append(msgs[-1]["content"])
            return next(seq)
        with mock.patch.object(W, "vendor_call", fake), mock.patch.object(W.time, "sleep") as sl:
            out = W.call("m", "sys", "user", expect=("a",))
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

    def test_truncated_is_nudged_not_slept(self):
        out, seen, sleeps = self.run_call([{"error": LB.TRUNCATED_REASONING}, {"content": '{"a": 2}'}])
        self.assertEqual(out, {"a": 2})
        self.assertEqual(sleeps, [])

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

    def test_near_copy_redoes_pass_b_first(self):
        gates = iter([["Pass A and Pass B are near-copies"], [], []])
        drafts, redos = [], []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}

        def fake_redo(slug, j, *a, **k):
            redos.append(1)
            return {**{k2: v for k2, v in j.items() if k2 != "_gate"}, "pass_b_english": ["B2."]}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_b", fake_redo), \
                mock.patch.object(W, "section_gate", lambda j, b: next(gates, [])), \
                mock.patch.object(W, "check_section", return_value={"confirmed": [], "rejected": []}):
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual((len(drafts), len(redos)), (1, 1))
        self.assertEqual(j["_status"], "pass")
        self.assertEqual(j["pass_b_english"], ["B2."])

    def test_full_redrafts_capped(self):
        drafts, redos = [], []

        def fake_draft(*a, **k):
            drafts.append(1)
            return {"section": "1", "pass_a_gloss": "A", "pass_b_english": ["B."]}

        def fake_redo(slug, j, *a, **k):
            redos.append(1)
            return {k2: v for k2, v in j.items() if k2 != "_gate"}
        with mock.patch.object(W, "draft_section", fake_draft), mock.patch.object(W, "redraft_pass_b", fake_redo), \
                mock.patch.object(W, "section_gate", lambda j, b: ["Pass A and Pass B are near-copies"]), \
                mock.patch.object(W, "check_section") as cs:
            j = W.process_section("s", 0, self.pairs, {}, "Greek")
        self.assertEqual(len(redos), 1)
        self.assertEqual(len(drafts), 1 + W.MAX_FULL_REDRAFTS)
        self.assertEqual(j["_status"], "hold")
        cs.assert_not_called()

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
            pairs = [{"id": "1", "source": ["x"], "english": [], "lang": "grc", "src_file": None}]
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

    def test_final_attempt_reads(self):
        self.assertTrue(self.run_with(2, True)[0])

    def test_no_held_reads(self):
        self.assertTrue(self.run_with(1, False)[0])

    def test_held_without_retries_left_reads(self):
        self.assertTrue(self.run_with(1, "spent")[0])

    def test_cli_run_reads(self):
        self.assertTrue(self.run_with(None, True)[0])


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

    def run_read(self, stage, pairs, rounds, polish=None):
        seq = iter(rounds)
        from contextlib import ExitStack
        with ExitStack() as es:
            for p in self.patches(stage, pairs):
                es.enter_context(p)
            es.enter_context(mock.patch.object(W, "read_two", side_effect=lambda t, l: next(seq)))
            es.enter_context(mock.patch.object(W, "polish_section", side_effect=polish or (lambda *a: None)))
            res = W.read_and_fix("s", pairs, {}, "Greek", None)
            st = W.status("s")
        return res, st

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


if __name__ == "__main__":
    unittest.main()
