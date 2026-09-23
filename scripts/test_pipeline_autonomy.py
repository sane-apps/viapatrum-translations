#!/usr/bin/env python3
"""Offline regressions for autonomy helpers and book adapters. No network."""
import copy
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import book_adapter as adapters
import pipeline_autonomy as autonomy
from pipeline_autonomy import (
    SplitRefused,
    arbiter_needed,
    arbiter_rule,
    chunk_paragraphs,
    merge_chunk_drafts,
    parse_or_repair,
    split_guard,
)


def fake_call_factory(script):
    """script: list of content strings or {'error': ...}; records calls."""
    calls = []
    state = {"n": 0}

    def call(model, messages, max_tokens):
        calls.append((model, messages, max_tokens))
        item = script[min(state["n"], len(script) - 1)]
        state["n"] += 1
        if isinstance(item, dict) and "error" in item:
            return {"error": item["error"], "ms": 1}
        return {"content": item, "ms": 1, "pt": 10, "ct": 20, "neurons": 3}

    call.calls = calls
    return call


GOOD = '{"pass_a_gloss": "literal sense here, long enough to count", "lemmas": []}'
BROKEN = '{"pass_a_gloss": "oops, unclosed'


class RepairTests(unittest.TestCase):
    def test_clean_parse_no_repair(self):
        call = fake_call_factory([GOOD])
        obj, info = parse_or_repair(
            call, "m", [], need=["pass_a_gloss"], shape_desc="D",
            max_tokens=10,
        )
        self.assertEqual(obj["lemmas"], [])
        self.assertFalse(info["repaired"])
        self.assertIsNone(info["error"])
        self.assertEqual(len(call.calls), 1)

    def test_broken_then_repaired(self):
        call = fake_call_factory([BROKEN, GOOD])
        obj, info = parse_or_repair(
            call, "m", [], need=["pass_a_gloss"], shape_desc="D",
            max_tokens=10, attempts=1, repairs=1,
        )
        self.assertIsNotNone(obj)
        self.assertTrue(info["repaired"])
        self.assertIsNone(info["error"])
        # Repair prompt carries the breakage back to the same model.
        self.assertIn("failed to parse", call.calls[1][1][1]["content"])

    def test_unrepairable_reports_parse_fail(self):
        call = fake_call_factory([BROKEN, BROKEN, BROKEN, BROKEN])
        obj, info = parse_or_repair(
            call, "m", [], need=["pass_a_gloss"], shape_desc="D",
            max_tokens=10, attempts=2, repairs=1,
        )
        self.assertIsNone(obj)
        self.assertEqual(info["error"], "parse_fail")

    def test_api_error_retries_next_attempt(self):
        call = fake_call_factory([{"error": "boom 500"}, GOOD])
        obj, info = parse_or_repair(
            call, "m", [], need=["pass_a_gloss"], shape_desc="D",
            max_tokens=10, attempts=2, repairs=0,
        )
        self.assertIsNotNone(obj)
        self.assertIsNone(info["error"])

    def test_exception_never_raises(self):
        def raiser(model, messages, max_tokens):
            raise RuntimeError("network down")

        obj, info = parse_or_repair(
            raiser, "m", [], need=["pass_a_gloss"], shape_desc="D",
            max_tokens=10, attempts=2,
        )
        self.assertIsNone(obj)
        self.assertIn("call_exception", info["error"])


class ChunkTests(unittest.TestCase):
    def test_greedy_pack(self):
        chunks = chunk_paragraphs(["a" * 100, "b" * 100, "c" * 100], 210)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], ["a" * 100, "b" * 100])

    def test_single_huge_para_splits_on_sentences(self):
        para = ("Alpha beta gamma. " * 40).strip()
        chunks = chunk_paragraphs([para], 200)
        self.assertTrue(len(chunks) > 1)
        self.assertEqual(" ".join(" ".join(c) for c in chunks), para)

    def test_single_huge_sentence_refuses_with_plan(self):
        with self.assertRaises(SplitRefused) as ctx:
            chunk_paragraphs(["x" * 5000], 1000)
        self.assertIn("paragraph 1", str(ctx.exception))
        self.assertTrue(ctx.exception.plan)

    def test_merge_concatenates_and_clears_title(self):
        merged = merge_chunk_drafts([
            {"section": "s", "title": "T1", "pass_a_gloss": "g1",
             "english": ["e1"], "lemmas": [{"a": 1}]},
            {"section": "s", "title": "T2", "pass_a_gloss": "g2",
             "english": ["e2"], "lemmas": []},
        ])
        self.assertEqual(merged["section"], "s")
        self.assertEqual(merged["title"], "")
        self.assertEqual(merged["english"], ["e1", "e2"])
        self.assertIn("g1", merged["pass_a_gloss"])
        self.assertIn("g2", merged["pass_a_gloss"])

    def test_guard_thresholds(self):
        self.assertEqual(split_guard(100), "single")
        self.assertEqual(split_guard(1501), "chunk")
        self.assertEqual(split_guard(12001), "refuse")


class DegenerateVerdictTests(unittest.TestCase):
    def test_chain_falls_past_reasonless_verdict(self):
        import ai_promote as promote

        degenerate = {"ok": False, "api_error": False, "model": "m1",
                      "parsed": {"verdict": "fail"}}
        passing = {"ok": True, "api_error": False,
                   "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                   "parsed": {"verdict": "pass", "notes": "checked all"}}
        with patch.object(promote, "run_checker",
                          side_effect=[degenerate, passing]) as run:
            result = promote.run_checker_chain(
                ["@cf/google/gemma-4-26b-a4b-it",
                 "@cf/meta/llama-3.3-70b-instruct-fp8-fast"],
                {}, draft_model="@cf/qwen/qwen3-30b-a3b-fp8")
            self.assertTrue(result["ok"])
            self.assertEqual(run.call_count, 2)

    def test_unparseable_verdict_falls_through(self):
        import ai_promote as promote

        self.assertTrue(promote.verdict_degenerate({}))
        self.assertFalse(promote.verdict_degenerate(None))
        self.assertFalse(promote.verdict_degenerate(
            {"verdict": "fail", "notes": "agency dropped"}))

    def test_genuine_fail_still_stops_chain(self):
        import ai_promote as promote

        genuine = {"ok": False, "api_error": False, "model": "m1",
                   "parsed": {"verdict": "fail", "notes": "agency dropped"}}
        with patch.object(promote, "run_checker",
                          return_value=genuine) as run:
            result = promote.run_checker_chain(
                ["@cf/google/gemma-4-26b-a4b-it",
                 "@cf/meta/llama-3.3-70b-instruct-fp8-fast"],
                {}, draft_model="@cf/qwen/qwen3-30b-a3b-fp8")
            self.assertFalse(result["ok"])
            self.assertEqual(run.call_count, 1)


class ArbiterTests(unittest.TestCase):
    def test_split_needs_arbiter(self):
        self.assertTrue(arbiter_needed(True, False))
        self.assertTrue(arbiter_needed(False, True))

    def test_agreement_needs_none(self):
        self.assertFalse(arbiter_needed(True, True))
        self.assertFalse(arbiter_needed(False, False))

    def test_api_failure_never_arbitrates(self):
        self.assertFalse(arbiter_needed(True, False, api_b=True))
        self.assertFalse(arbiter_needed(False, True, api_a=True))

    def test_rule(self):
        verdict, _ = arbiter_rule(True)
        self.assertEqual(verdict, "PROMOTE")
        verdict, _ = arbiter_rule(False)
        self.assertEqual(verdict, "HOLD")


class CheckerPromptTests(unittest.TestCase):
    def test_checker_prompt_demands_json_first(self):
        import ai_promote as promote

        self.assertIn("Begin your response with {", promote.CHECK_SYS)


class ChunkedSourceTests(unittest.TestCase):
    def test_user_prompt_chunk_note(self):
        from llm_bakeoff import user_prompt

        chunked = user_prompt({"section": "s", "greek": ["x"],
                               "chunked_source": True})
        self.assertIn("Chunked source", chunked)
        plain = user_prompt({"section": "s", "greek": ["x"]})
        self.assertNotIn("Chunked source", plain)

    def test_checker_prompt_chunk_tolerance(self):
        import ai_promote as promote

        bundle = {"section": "s", "book": "cyril-alexandria-isaiah",
                  "greek": ["x"],
                  "english_row": {"title": "t", "english": ["y"]},
                  "justification": {"edition": {}, "pass_a_gloss": "g",
                                    "lemmas": [], "choices": []}}
        cyril = promote.checker_prompt(bundle)[1]["content"]
        self.assertIn("SOURCE CHUNKING", cyril)
        bundle["book"] = "origen-jeremiah-samuel"
        jer = promote.checker_prompt(bundle)[1]["content"]
        self.assertNotIn("SOURCE CHUNKING", jer)

    def test_ellipsis_end_counts_complete(self):
        from llm_bakeoff import score

        obj = {"section": "s", "title": "Thoughts on mercy",
               "pass_a_gloss": "A full literal gloss of every clause here.",
               "english": ["A complete sentence.", "A cut fragment…"],
               "lemmas": [{"form": "x", "lemma": "x", "gloss": "x"}]}
        self.assertTrue(score(obj, "{}", "s")["checks"]["english_complete"])

    def test_trailing_citation_counts_complete(self):
        from llm_bakeoff import score

        obj = {"section": "s", "title": "Thoughts on mercy",
               "pass_a_gloss": "A full literal gloss of every clause here.",
               "english": ["He said, 'Draw near to me.' (Isaiah 29:13)"],
               "lemmas": [{"form": "x", "lemma": "x", "gloss": "x"}]}
        self.assertTrue(score(obj, "{}", "s")["checks"]["english_complete"])
        obj["english"] = ["(Isaiah 29:13)"]
        self.assertFalse(score(obj, "{}", "s")["checks"]["english_complete"])


class AdapterTests(unittest.TestCase):
    def test_unknown_book_refuses(self):
        with self.assertRaises(SystemExit):
            adapters.get_adapter("augustine-confessions")

    def test_jeremiah_parity(self):
        j = adapters.get_adapter("origen-jeremiah-samuel")
        self.assertEqual(j.excerpt_id("6.1"), "jeremiah_6_1")
        self.assertTrue(str(j.justification_path("6.1")).endswith(
            "reviews/justifications/jeremiah_6_1.json"))
        self.assertTrue(str(j.english_path()).endswith(
            "translations/jeremiah_english.json"))
        self.assertEqual(
            j.sections_from_slice("Homily 6 §§6.1–6.3"),
            ["6.1", "6.2", "6.3"],
        )
        with self.assertRaises(SystemExit):
            j.sections_from_slice("§§6.3–6.1")

    def test_cyril_slice_and_excerpt(self):
        c = adapters.get_adapter("cyril-alexandria-isaiah")
        self.assertEqual(
            c.sections_from_slice("book2-open, prologue"),
            ["book2-open", "prologue"],
        )
        self.assertEqual(c.excerpt_id("book2-open"), "book2-open")
        with self.assertRaises(SystemExit):
            c.sections_from_slice("book2-open, nope-nothing")
        with self.assertRaises(SystemExit):
            c.sections_from_slice("   ")

    def test_cyril_justification_mapping_matches_repo(self):
        c = adapters.get_adapter("cyril-alexandria-isaiah")
        names = {p.name for p in c.just_dir.glob("*.json")}
        count = 0
        for path in sorted(c.trans_dir.glob("*_source.json")):
            import json

            rows = json.loads(path.read_text(encoding="utf-8"))
            for row in rows if isinstance(rows, list) else [rows]:
                self.assertIn(
                    c.justification_path(row["section"]).name, names,
                    row["section"],
                )
                count += 1
        self.assertEqual(count, 89)

    def test_cyril_source_row_shape(self):
        c = adapters.get_adapter("cyril-alexandria-isaiah")
        fix = c.load_source_row("prologue")
        self.assertEqual(fix["section"], "prologue")
        self.assertIsInstance(fix["greek"], list)
        self.assertTrue(all(isinstance(p, str) for p in fix["greek"]))
        self.assertEqual(fix["locus"], "Prologue")
        with self.assertRaises(SystemExit):
            c.load_source_row("nope-nothing")


class CompletionTests(unittest.TestCase):
    def test_cut_off_english_is_finished_not_redrafted(self):
        import draft_claim as draft

        greek = ["Ὁ θεὸς οὐκ ἀδικεῖ.", "Ἀγαπᾷ τοὺς δικαίους."]
        truncated = {
            "section": "6.1", "title": "No wrong, only love",
            "pass_a_gloss": "God does no wrong to anyone at all in any way here.",
            "english": ["God does no wrong.", "God loves the righteo"],
            "lemmas": [{"form": "ἀδικεῖ", "lemma": "ἀδικέω", "gloss": "wrongs"}],
            "choices": [{"term": "ἀδικεῖ", "english": "does no wrong",
                         "why": "Negation preserved."}],
            "translator_notes": [],
        }
        tail = {"english_tail": ["God loves the righteous fully."]}
        fix = {"section": "6.1", "homily": 6, "greek": greek,
               "klostermann": "Hom.6.1"}
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            book = root / "books/origen-jeremiah-samuel"
            raw = book / "sources/first1k/tlg2042.tlg009.opp-grc1.xml"
            raw.parent.mkdir(parents=True)
            raw.write_text(" ".join(greek))
            manifest = raw.parent.parent / "manifest.json"
            from pipeline.verify_translation_qa import file_digest

            manifest.write_text(json.dumps({"files": {
                "first1k/tlg2042.tlg009.opp-grc1.xml":
                    {"sha256": file_digest(raw)}}}))
            english = book / "translations/jeremiah_english.json"
            english.parent.mkdir()
            english.write_text("[]")
            just_dir = book / "reviews/justifications"
            just_dir.mkdir(parents=True)
            for name, value in (("ENG", english), ("JUST_DIR", just_dir),
                                ("RAW_SOURCE", raw), ("XML_SOURCE", raw),
                                ("SOURCE_MANIFEST", manifest)):
                stack.enter_context(patch.object(draft, name, value))
            stack.enter_context(patch.object(
                draft, "load_fixture",
                side_effect=lambda _s: copy.deepcopy(fix)))
            call = stack.enter_context(patch.object(
                draft, "vendor_call", side_effect=[
                    {"content": json.dumps(truncated)},
                    {"content": json.dumps(tail)},
                ]))
            result = draft.draft_section("6.1", "m", "", "", "", "t")
            self.assertTrue(result["ok"], result)
            self.assertEqual(call.call_count, 2)
            current = json.loads(english.read_text())[0]
            self.assertEqual(current["english"][-1],
                             "God loves the righteous fully.")


class ReviseTests(unittest.TestCase):
    def _tree(self, root):
        import draft_claim as draft
        from pipeline.verify_translation_qa import file_digest

        greek = ["Ὁ θεὸς οὐκ ἀδικεῖ τὸν ἄνθρωπον.",
                 "Ἀγαπᾷ τοὺς δικαίους ὁ θεός."]
        book = root / "books/origen-jeremiah-samuel"
        raw = book / "sources/first1k/tlg2042.tlg009.opp-grc1.xml"
        raw.parent.mkdir(parents=True)
        raw.write_text(" ".join(greek))
        english = book / "translations/jeremiah_english.json"
        english.parent.mkdir()
        english.write_text(json.dumps([{
            "section": "6.1", "homily": 6, "title": "Rough cut",
            "english": ["God does no wrong, more or less.", "Something about love."]}]))
        just_dir = book / "reviews/justifications"
        just_dir.mkdir(parents=True)
        (just_dir / "jeremiah_6_1.json").write_text(json.dumps({
            "excerpt_id": "jeremiah_6_1",
            "edition": {"id": "gcs6-klostermann-1901", "language": "grc",
                        "locus": "Hom.6.1",
                        "path": "sources/first1k/tlg2042.tlg009.opp-grc1.xml",
                        "sha256": file_digest(raw), "checks": []},
            "source_text": " ".join(greek),
            "pass_a_gloss": "God commits no injustice toward a human being at all. God loves the righteous ones.",
            "pass_b_english": ["God does no wrong, more or less.", "Something about love."],
            "lemmas": [{"form": "ἀδικεῖ", "lemma": "ἀδικέω", "gloss": "wrongs"}],
            "choices": [{"term": "ἀδικεῖ", "english": "does no wrong",
                         "why": "Negation preserved."}],
            "bible_refs": [], "variants": [], "source_normalizations": [],
            "anf_compare": {"status": "not_checked", "notes": "x"},
            "apparatus": [], "checks": {}, "confidence": "machine_draft",
            "reviewer": "pending-ai-crosscheck:m", "draft_agent": "t",
            "draft_model": "m0", "drafted_at": "2026-01-01T00:00:00+00:00",
        }))
        fix = {"section": "6.1", "homily": 6, "greek": greek,
               "klostermann": "Hom.6.1"}
        return draft, fix

    def _receipt(self, root, checks):
        receipt = root / "summary.json"
        receipt.write_text(json.dumps({"results": [{
            "section": "6.1", "structural": {"ok": True},
            "checker_a": {"model": "a", "ok": checks[0], "api_error": False,
                          "parsed": {"verdict": "fail", "notes": "B drops agency",
                                     "reasons": ["agency"]}},
            "checker_b": {"model": "b", "ok": checks[1], "api_error": False,
                          "parsed": {"verdict": "pass", "notes": "fine",
                                     "reasons": []}},
        }]}))
        return str(receipt)

    def test_revise_replaces_b_and_records_round(self):
        import draft_claim as draft

        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            mod, fix = self._tree(root)
            book = root / "books/origen-jeremiah-samuel"
            for name, value in (
                    ("ENG", book / "translations/jeremiah_english.json"),
                    ("JUST_DIR", book / "reviews/justifications")):
                stack.enter_context(patch.object(mod, name, value))
            stack.enter_context(patch.object(
                mod, "load_fixture",
                side_effect=lambda _s: copy.deepcopy(fix)))
            stack.enter_context(patch.object(
                mod, "vendor_call", return_value={"content": json.dumps({
                    "title": "No wrong, only love",
                    "english": ["God does no person any wrong at all.",
                                "God loves the righteous."],
                    "pass_a_gloss": "God commits no injustice toward a human being at all. God loves the righteous ones. Extra topped-up gloss line.",
                    "translator_notes": []})}))
            receipt = self._receipt(root, (False, True))
            failures = draft.load_receipt_failures(receipt)
            self.assertEqual(list(failures), ["6.1"])
            self.assertEqual(len(failures["6.1"]), 1)
            result = mod.revise_section("6.1", "m1", "", "", "", "t",
                                        failures["6.1"], receipt)
            self.assertTrue(result["ok"], result)
            just = json.loads(
                (book / "reviews/justifications/jeremiah_6_1.json").read_text())
            self.assertEqual(just["pass_b_english"],
                             ["God does no person any wrong at all.",
                              "God loves the righteous."])
            self.assertEqual(len(just["revisions"]), 1)
            self.assertEqual(just["revisions"][0]["model"], "m1")
            self.assertEqual(just["draft_model"], "m0+rev:m1")
            self.assertEqual(just["edition"]["locus"], "Hom.6.1")
            current = json.loads(
                (book / "translations/jeremiah_english.json").read_text())[0]
            self.assertEqual(current["title"], "No wrong, only love")

    def test_greek_span_extraction(self):
        import draft_claim as draft

        notes = ["checker_a: omits 'Ἐφη γοῦν· Ἐγγίζει μοι' and short ὁ δὲ",
                 "no greek here", "also 'Βδέλυγμα δὲ τὸ εἴδωλον ὀνομάζει ok'"]
        spans = draft.greek_spans_in(notes)
        self.assertEqual(len(spans), 2)
        self.assertTrue(all(" " in s for s in spans))

    def test_revise_skips_api_only_and_refuses_thin_prior(self):
        import draft_claim as draft

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = root / "summary.json"
            receipt.write_text(json.dumps({"results": [{
                "section": "6.1", "structural": {"ok": True},
                "checker_a": {"model": "a", "ok": False, "api_error": True},
                "checker_b": {"model": "b", "ok": True}}]}))
            self.assertEqual(draft.load_receipt_failures(str(receipt)), {})


if __name__ == "__main__":
    unittest.main()
