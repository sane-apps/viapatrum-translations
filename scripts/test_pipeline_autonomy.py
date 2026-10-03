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


class JsonBookTests(unittest.TestCase):
    def test_severianus_fragment_and_earliest_queue(self):
        import overnight_quota as quota

        adapter = adapters.get_adapter("severianus-fragmentum-philemonem")
        fix = adapter.load_source_row("u01-open")
        greek = " ".join(fix["greek"])
        self.assertGreater(len(greek), 40)
        self.assertTrue(any("\u0370" <= ch <= "\u03ff" or "\u1f00" <= ch <= "\u1fff" for ch in greek))
        self.assertFalse(autonomy.source_is_betacode(greek))
        self.assertEqual(adapter.justification_path("u01-open").name, "u01_open.json")
        self.assertIsNone(adapter.manifest_path())
        claim = "severianus-fragmentum-philemonem--u01-open"
        self.assertTrue(__import__("re").fullmatch(adapter.claim_re, claim))
        rows = quota.earliest_scaffold_candidates(4)
        ids = [row[0] for row in rows]
        self.assertEqual(ids[0], claim)
        self.assertEqual(sum(item.startswith("severianus-fragmentum-philemonem--") for item in ids), 1)
        self.assertEqual([row[3] for row in rows], sorted(row[3] for row in rows))
        self.assertLessEqual(len(rows), 4)
        for _claim, slug, _section, _year in rows:
            self.assertNotIn("melito", slug)
            self.assertNotIn(slug, ("cyril-alexandria-isaiah", "origen-jeremiah-samuel"))


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



class ClauseRepairTests(unittest.TestCase):
    def test_omission_already_in_reading_is_refuted(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["Pass A omitted the clause 'since He was about to rebuke Israel' from the reading."],
            "Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ ποιεῖσθαι μομφάς",
            "since He was about to rebuke Israel and make the charge known",
            "since He was about to rebuke Israel and make the charge known",
        )
        self.assertTrue(result["override"], result)
        self.assertEqual(result["refuted"][0]["basis"], "omission-already-in-draft")
        self.assertEqual(result["actionable"], [])

    def test_greek_absent_from_source_is_refuted(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["Pass B omits the clause 'τοιούτον τί φασιν οἱ ἡ προκειμένην' from the source."],
            "ὁ λόγος ἦν πρὸς τὸν θεόν καὶ ἐσκήνωσεν ἐν ἡμῖν",
            "The word was with God.",
            "The word was with God.",
        )
        self.assertTrue(result["override"], result)
        self.assertEqual(result["refuted"][0]["basis"], "greek-not-in-source")

    def test_real_omission_stays_actionable(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["Pass B omits 'since He was about to rebuke Israel' (Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραήλ)."],
            "Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ ποιεῖσθαι μομφάς",
            "The prophet speaks.",
            "The prophet speaks.",
        )
        self.assertFalse(result["override"], result)
        self.assertEqual(len(result["actionable"]), 1)

    def test_addition_of_translated_source_is_refuted(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["Pass B added the phrase 'despite their noble birth which was and is becoming to their fathers' (εὐγένειαν)."],
            "τὴν τοῖς πατράσι πρέπουσάν τε καὶ ἐνοῦσαν εὐγένειαν εἶχον",
            "The elements had toiled.",
            "He had pity on them despite their noble birth which was and is becoming to their fathers.",
        )
        self.assertTrue(result["override"], result)
        self.assertEqual(result["refuted"][0]["basis"], "addition-is-translated-source")

    def test_unsupported_pass_b_stays_actionable(self):
        from pipeline_autonomy import refute_confabulated_clauses

        quote = "As they ascend, they will experience the perfection and blamelessness that come from being in Christ"
        result = refute_confabulated_clauses(
            ["Pass B adds the sentence '%s' which the gloss does not say." % quote],
            "ἣ καὶ ἀληθῶς ἐστι τελεία καὶ ἄμωμος",
            "The intelligible Jerusalem, which is truly perfect and blameless, is the Church.",
            quote + ".",
        )
        self.assertFalse(result["override"], result)
        self.assertTrue(result["actionable"])

    def test_mistranslation_blocks_override(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            [
                "Pass A omitted the clause 'since He was about to rebuke Israel' from the reading.",
                "Mistranslated 'πεπονηκότων' as 'those involved in the labor' rather than those who had toiled.",
            ],
            "Ἐπειδὴ γὰρ ἔμελλε πεπονηκότων εὐγένειαν",
            "since He was about to rebuke Israel",
            "since He was about to rebuke Israel and all those involved in the labor",
        )
        self.assertFalse(result["override"], result)
        self.assertTrue(any("Mistranslated" in item for item in result["actionable"]))

    def test_garbled_betacode_is_refuted(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["Pass A omits the clause 'Ou) ga/r toi fasi par- aitios' from the Greek."],
            "Toiou=to/n ti fasin oi thn prokeimenhn lithn anaferontej",
            "Toiou=to/n ti fasin oi thn prokeimenhn lithn anaferontej",
            "Thus they speak.",
        )
        self.assertTrue(result["override"], result)
        self.assertEqual(result["refuted"][0]["basis"], "garbled-not-in-source")

    def test_boilerplate_without_a_quote_is_ignored(self):
        from pipeline_autonomy import refute_confabulated_clauses

        result = refute_confabulated_clauses(
            ["The draft dropped a clause and the completeness check failed."],
            "ὁ λόγος",
            "The word.",
            "The word.",
        )
        self.assertFalse(result["override"], result)
        self.assertEqual(result["actionable"], [])
        self.assertEqual(result["refuted"], [])


class HoldRepairTests(unittest.TestCase):
    def test_one_repair_then_park(self):
        import overnight_quota as quota

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", path):
                first = quota.record_claim_fail("c1", "hold")
                self.assertFalse(first.get("held"))
                self.assertFalse(quota._hold_blocks(first))
                second = quota.record_claim_fail("c1", "hold")
                self.assertTrue(second.get("held"))
                self.assertFalse(second.get("repair_spent"))
                self.assertFalse(quota._hold_blocks(second))
                third = quota.record_claim_fail("c1", "hold")
                self.assertTrue(third.get("repair_spent"))
                self.assertTrue(quota._hold_blocks(third))


class StructuralReceiptTests(unittest.TestCase):
    def test_structural_only_receipt(self):
        self.assertTrue(autonomy.receipt_structural_only(
            {"results": [{"structural": {"ok": False}}]}
        ))
        self.assertFalse(autonomy.receipt_structural_only(
            {"results": [{"structural": {"ok": True}}]}
        ))
        self.assertFalse(autonomy.receipt_structural_only({"results": []}))
        self.assertFalse(autonomy.receipt_structural_only({"results": [
            {"structural": {"ok": False}},
            {"structural": {"ok": True}},
        ]}))

    def test_clear_hold_after_promote(self):
        import overnight_quota as quota

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", path):
                quota.record_claim_fail("c1", "hold")
                quota.record_claim_fail("c1", "hold")
                self.assertTrue(quota.load_hold()["c1"].get("held"))
                quota.clear_claim_hold("c1")
                self.assertNotIn("c1", quota.load_hold())


class LemmaSenseTests(unittest.TestCase):
    def test_missing_lemma_sense(self):
        gaps = autonomy.missing_lemma_senses(
            [{"form": "εὐγένειαν", "gloss": "noble birth"}],
            ["He had pity on them as those being wronged."],
        )
        self.assertEqual(len(gaps), 1)
        self.assertIn("noble birth", gaps[0])
        self.assertFalse(autonomy.missing_lemma_senses(
            [{"form": "εὐγένειαν", "gloss": "noble birth"}],
            ["despite their noble birth"],
        ))
        self.assertFalse(autonomy.missing_lemma_senses(
            [{"form": "εὐγένειαν", "gloss": "noble birth"}],
            ["a noble family"],
        ))
        self.assertFalse(autonomy.missing_lemma_senses(
            [{"form": "x", "gloss": "pity"}],
            ["no pity here"],
        ))


class BetacodeSourceTests(unittest.TestCase):
    def test_source_is_betacode(self):
        self.assertTrue(autonomy.source_is_betacode("lisqhko/taj"))
        self.assertFalse(autonomy.source_is_betacode("εὐγένειαν καὶ τοῖς πατράσι"))
        self.assertFalse(autonomy.source_is_betacode(
            "Fragmentum (in catenis)\n"
            "Ἐν πολλαῖς ἐπιστολαῖς ξένον τίθησι ῥῆμα"))




class QuoteCoverageTests(unittest.TestCase):
    def test_near_quote_already_in_reading_is_refuted(self):
        result = autonomy.refute_confabulated_clauses(
            ["Pass B omits 'since he was about to rebuke Israel and make the charge known to the angels'."],
            "Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ ποιεῖσθαι μομφάς",
            "since he was about to rebuke Israel",
            "because he was about to rebuke Israel and make the charge known to the angels today",
        )
        self.assertTrue(result["override"], result)
        self.assertEqual(result["actionable"], [])

    def test_scattered_words_stay_a_real_omission(self):
        result = autonomy.refute_confabulated_clauses(
            ["Pass B omits 'since he was about to rebuke Israel and make the charge known to the angels'."],
            "Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ ποιεῖσθαι μομφάς",
            "The prophet speaks.",
            "The angels sang. Much later Israel heard a rebuke. The charge was known to nobody in particular today.",
        )
        self.assertTrue(result["actionable"], result)

    def test_meta_pass_fragment_is_not_a_quote(self):
        quotes = autonomy._english_quotes(
            "Pass A omits the clause 'the water was turned into blood and the air was darkened' (Pass B includes it)."
        )
        self.assertFalse(any("pass b" in q for q in quotes))

    def test_pass_a_complaint_does_not_rewrite_pass_b(self):
        result = autonomy.refute_confabulated_clauses(
            ["Pass A omits the clause 'purple elephants danced on the shore at dusk' (Pass B includes it)."],
            "ὁ λόγος",
            "The word.",
            "The reading says something else entirely about the prophet.",
        )
        self.assertEqual(result["actionable"], [])
        self.assertEqual(result["refuted"][0]["basis"], "complaint-targets-pass-a")

    def test_real_pass_b_omission_stays(self):
        result = autonomy.refute_confabulated_clauses(
            ["Pass B omits the clause 'purple elephants danced on the shore at dusk'."],
            "ὁ λόγος",
            "The word.",
            "The reading says something else entirely about the prophet.",
        )
        self.assertTrue(result["actionable"], result)


class RepairNoteTests(unittest.TestCase):
    def test_word_still_present(self):
        notes = [{"until_absent": "involved", "note": "Rewrite this sentence so it no longer says involved."}]
        self.assertEqual(len(autonomy.unsatisfied_repair_notes(notes, ["all those involved"])), 1)
        self.assertEqual(autonomy.unsatisfied_repair_notes(notes, ["on all bodies"]), [])
        kept = [{"until_absent": "involved", "sentence_has": "sores and blisters", "note": notes[0]["note"]}]
        self.assertEqual(len(autonomy.unsatisfied_repair_notes(kept, ["the elements had toiled"])), 1)
        self.assertEqual(
            autonomy.unsatisfied_repair_notes(kept, ["sores and blisters rose on all bodies"]),
            [],
        )

    def test_omission_note_names_the_greek(self):
        note = "Pass B omits the clause 'πᾶσάν τε αὐτῶν καταδῃώσας τὴν γῆν' from the reading."
        out = autonomy.concrete_omission_note(note)
        self.assertIn("καταδῃώσας", out)
        self.assertTrue(out.startswith("Add this missing clause"))
        lied = "Pass A omits the clause 'πᾶσάν τε αὐτῶν καταδῃώσας τὴν γῆν' (Pass B includes it)."
        self.assertEqual(autonomy.concrete_omission_note(lied), "")

    def test_defect_key_is_stable(self):
        note = "Pass B omits 'πᾶσάν τε αὐτῶν καταδῃώσας τὴν γῆν' from the reading."
        self.assertEqual(autonomy.stable_defect_key([note]), autonomy.stable_defect_key([note]))
        self.assertTrue(autonomy.stable_defect_key([note]).startswith("g:"))
        self.assertEqual(autonomy.stable_defect_key(["Rewrite this sentence and leave it."]), "")


class ChangedDefectTests(unittest.TestCase):
    def test_changed_defect_does_not_park(self):
        import overnight_quota as quota

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", path):
                first = quota.record_claim_fail("c2", "hold", "alpha")
                self.assertFalse(first.get("repair_spent"))
                second = quota.record_claim_fail("c2", "hold", "beta")
                self.assertFalse(second.get("repair_spent"))
                self.assertTrue(second.get("held"))
                third = quota.record_claim_fail("c2", "hold", "gamma")
                self.assertFalse(third.get("repair_spent"))
                self.assertFalse(quota._hold_blocks(third))

    def test_same_defect_parks_on_the_third(self):
        import overnight_quota as quota

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", path):
                quota.record_claim_fail("c3", "hold", "same-span")
                quota.record_claim_fail("c3", "hold", "same-span")
                third = quota.record_claim_fail("c3", "hold", "same-span")
                self.assertTrue(third.get("repair_spent"))
                self.assertTrue(quota._hold_blocks(third))

    def test_open_repair_is_not_parked(self):
        import overnight_quota as quota

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", path):
                row = quota.record_claim_fail("c4", "hold", "")
                self.assertTrue(row.get("held"))
                self.assertFalse(row.get("repair_spent"))
                again = quota.record_claim_fail("c4", "hold", "")
                self.assertFalse(again.get("repair_spent"))
                self.assertFalse(quota._hold_blocks(again))


    def test_torn_receipt_does_not_park(self):
        import overnight_quota as quota

        note = (
            "Pass B omits '\u03c0\u1fb6\u03c3\u03ac\u03bd \u03c4\u03b5 "
            "\u03b1\u1f50\u03c4\u1ff6\u03bd \u03ba\u03b1\u03c4\u03b1\u03b4"
            "\u1fc3\u03ce\u03c3\u03b1\u03c2 \u03c4\u1f74\u03bd \u03b3\u1fc6\u03bd' "
            "from the reading."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            promote = root / "outputs" / "ai-promote"
            good = promote / "20260929T010000Z-c9"
            good.mkdir(parents=True)
            (good / "summary.json").write_text(
                json.dumps({"results": [{"clause_defect": {"actionable": [note]}}]}),
                encoding="utf-8",
            )
            torn = promote / "20260929T020000Z-c9"
            torn.mkdir()
            with patch.object(quota, "ROOT", root):
                key = quota._concrete_defect_key("c9")
            self.assertTrue(key.startswith("g:"))
            hold = root / "HOLD.jsonl"
            with patch.object(quota, "HOLD_PATH", hold):
                first = quota.record_claim_fail("c9", "hold", key)
                self.assertFalse(first.get("repair_spent"))
                second = quota.record_claim_fail("c9", "hold", key)
                self.assertEqual(second.get("same_fails"), 2)
                self.assertFalse(second.get("repair_spent"))
            empty = Path(tmp) / "empty-root"
            (empty / "outputs" / "ai-promote").mkdir(parents=True)
            with patch.object(quota, "ROOT", empty):
                self.assertEqual(quota._concrete_defect_key("c9"), "")


if __name__ == "__main__":
    unittest.main()
