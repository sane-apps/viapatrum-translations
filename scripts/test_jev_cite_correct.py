#!/usr/bin/env python3
"""Offline regressions for the Jev citation correction loop. Mocks API calls."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jev_cite_correct as cc


SENT = "Bind the tares (Leviticus 14:40) and burn them."


class CorrectorTests(unittest.TestCase):
    def setUp(self):
        # Older cases exercise the CF proposer alone; search has its own tests.
        for name, fake in (("search_verses", lambda clause, top=3: []),
                           ("overlap_any", lambda c, p: cc.overlap_with_kjv(c, p)),
                           ("second_opinion", lambda clause, greek, display: ("contradicts", 0.9))):
            patcher = patch.object(cc, name, side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_ref_spans(self):
        spans = cc.ref_spans("See (John 3:5) and Romans 8 about grace.")
        self.assertIn(("john", 3, 5), [(b, c, v) for b, c, v, _s, _e in spans])
        self.assertIn(("rom", 8, None), [(b, c, v) for b, c, v, _s, _e in spans])
        for _b, _c, _v, s, e in spans:
            self.assertLess(s, e)

    def test_same_ref(self):
        self.assertTrue(cc.same_ref(("john", 3, 5), ("john", 3, 5)))
        self.assertTrue(cc.same_ref(("john", 3, None), ("john", 3, 5)))
        self.assertFalse(cc.same_ref(("john", 3, 5), ("john", 3, 6)))
        self.assertFalse(cc.same_ref(("john", 3, 5), ("1jn", 3, 5)))
        self.assertFalse(cc.same_ref(None, ("john", 3, 5)))

    def test_replace_citation(self):
        out = cc.replace_citation(SENT, ("lev", 14, 40), "Matthew 13:30")
        self.assertEqual(out, "Bind the tares (Matthew 13:30) and burn them.")
        self.assertIsNone(cc.replace_citation(SENT, ("john", 3, 5), "X 1:1"))
        cf = cc.replace_citation("(Deuteronomy 8:3; cf. Matthew 4:4) Next.",
                                 ("matt", 4, 4), "Luke 4:4")
        self.assertEqual(cf, "(Deuteronomy 8:3; cf. Luke 4:4) Next.")

    def test_append_citation(self):
        self.assertEqual(cc.append_citation("Come to me.", "Matthew 11:28"),
                         "Come to me. (Matthew 11:28)")

    def test_verse_overlap_accepts_close_quote(self):
        clause = ("after the second veil a tent, the one called Holies of holies, "
                  "having a golden censer, and the ark of the covenant")
        kjv = ("And after the second veil, the tabernacle which is called the "
               "Holiest of all; Which had the golden censer, and the ark of the "
               "covenant overlaid round about with gold")
        self.assertGreaterEqual(cc.verse_overlap(clause, kjv), 2)

    def test_verse_overlap_rejects_theme_match(self):
        # Caught live 2026-09-25: proposer said Exodus 12:46, Jev verified
        # supports@0.9, but the words are Leviticus 17:10-11. Overlap blocks it.
        clause = ("who should eat every blood, I will set my face upon the soul "
                  "eating the blood, and I will destroy it from its people. "
                  "For the soul of every flesh is its blood")
        kjv_wrong = ("In one house shall it be eaten; thou shalt carry nothing "
                     "of the flesh abroad out of the house; neither shall ye "
                     "break a bone thereof")
        self.assertLess(cc.verse_overlap(clause, kjv_wrong), 2)

    def test_section_claimed_boundaries(self):
        active = "| c1 | claimed | b | logos2-rem-close | ag | 2026-09-24 | w |\n"
        self.assertTrue(cc.section_claimed("logos2-rem-close", active))
        self.assertFalse(cc.section_claimed("2", active))
        self.assertFalse(cc.section_claimed("22", active))
        self.assertFalse(cc.section_claimed("", active))
        self.assertFalse(cc.section_claimed("logos2-rem-mid", active))

    def test_correct_item_filed_cite_not_in_text(self):
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40", "sentence": SENT, "flag_conf": 0.98}
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [SENT])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, [{"section": "s"}], 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec.get("ok"))
        self.assertEqual(rec.get("reason"), "filed-cite-not-in-text")

    def test_correct_item_backfill_sentence_not_found(self):
        item = {"kind": "backfill", "book": "b", "section": "s",
                "display": "", "sentence": "Unrelated words here.", "flag_conf": 0.95}
        rows = [{"section": "s", "english": ["Entirely different text."]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", rows[0]["english"])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.9)
        self.assertFalse(rec.get("ok"))
        self.assertEqual(rec.get("reason"), "sentence-not-found")

    def test_correct_item_disambiguates_files(self):
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40", "sentence": SENT, "flag_conf": 0.98}
        wrong = [{"section": "s", "english": ["Other slice text without cites."]}]
        right = [{"section": "s", "english": [SENT]}]
        cands = [(Path("a.json"), None, wrong, 0), (Path("b.json"), None, right, 0)]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [SENT])), \
             patch.object(cc, "english_candidates", return_value=cands), \
             patch.object(cc, "greek_for_file", return_value="g"), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["path"], "b.json")

    def test_correct_item_full_flow(self):
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40", "sentence": SENT, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [SENT]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [SENT])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["op"], "replace")
        self.assertEqual(rec["proposed"], "Matthew 13:30")
        self.assertIn("(Matthew 13:30)", rec["new_sentence"])

    def test_correct_item_matches_sanitized_clause(self):
        raw = "Bind the tares (Leviticus 14:40) and burn them."
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40",
                "sentence": "Bind the tares and burn them.", "flag_conf": 0.98}
        rows = [{"section": "s", "english": [raw]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertIn("(Matthew 13:30)", rec["new_sentence"])

    def test_correct_item_prefers_filed_sentence(self):
        prev = "Previous words here about context."
        raw = "Quote words (Leviticus 14:40) tail."
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40",
                "sentence": prev + " Quote words tail.", "flag_conf": 0.98}
        rows = [{"section": "s", "english": [prev + " " + raw]}]
        with patch.object(cc.cite, "load_section_texts",
                          return_value=("g", [prev + " " + raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertIn("Quote words (Matthew 13:30) tail.", rec["new_sentence"])

    def test_correct_item_rejects_unverified(self):
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40", "sentence": SENT, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [SENT]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [SENT])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.5, {})):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec["ok"])
        self.assertIn("unverified", rec["reason"])

    def test_correct_item_rejects_clause_mismatch(self):
        blood = ("who should eat every blood, I will set my face upon the soul "
                 "eating the blood (Deuteronomy 12:13)")
        pone = "In one house it will be eaten (Deuteronomy 12:13) from Egypt."
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Deuteronomy 12:13", "sentence": blood, "flag_conf": 0.99}
        rows = [{"section": "s", "english": [pone]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [pone])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse") as p, \
             patch.object(cc, "verify_proposal") as v:
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec.get("ok"))
        self.assertEqual(rec.get("reason"), "clause-mismatch")
        p.assert_not_called()
        v.assert_not_called()

    def test_dedupe_removes_filed_span(self):
        sent = "impossible to take away (Psalm 19:4) (Romans 10:18) (Hebrews 10:4)"
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Romans 10:18", "sentence": sent, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [sent]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [sent])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("heb", 10, 4)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.98, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=5):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["op"], "dedupe")
        self.assertNotIn("Romans 10:18", rec["new_sentence"])
        self.assertIn("(Hebrews 10:4)", rec["new_sentence"])

    def test_replace_repairs_split_possessive(self):
        out = cc.replace_citation("Aaron’ (1 Peter 2:9)s rod that sprouted.",
                                  ("1pet", 2, 9), "Hebrews 9:3")
        self.assertEqual(out, "Aaron’s (Hebrews 9:3) rod that sprouted.")

    def test_correct_item_rejects_low_overlap(self):
        sent = "Take heed (Deuteronomy 12:13) in the place."
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Deuteronomy 12:13", "sentence": sent, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [sent]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [sent])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("exod", 12, 46)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.9, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=0):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec["ok"])
        self.assertIn("overlap-too-low", rec["reason"])

    def test_correct_item_rejects_filed_agreement(self):
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40", "sentence": SENT, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [SENT]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [SENT])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("lev", 14, 40)), \
             patch.object(cc, "verify_proposal") as v:
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec["ok"])
        v.assert_not_called()

    def test_apply_correction_and_justification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "books/origen-jeremiah-samuel/reviews/justifications").mkdir(parents=True)
            eng = root / "eng.json"
            eng.write_text(json.dumps([{"section": "1.15", "english": [SENT]}]))
            just = root / "books/origen-jeremiah-samuel/reviews/justifications/jeremiah_1_15.json"
            just.write_text(json.dumps({"bible_refs": [
                {"display": "Leviticus 14:40", "method": "wording", "note": "n"}]}))
            rec = {"book": "origen-jeremiah-samuel", "section": "1.15",
                   "display": "Leviticus 14:40", "proposed": "Matthew 13:30",
                   "sentence": SENT,
                   "new_sentence": "Bind the tares (Matthew 13:30) and burn them.",
                   "path": str(eng)}
            with patch.object(cc, "ROOT", root):
                self.assertTrue(cc.apply_correction(rec))
            eng_rows = json.loads(eng.read_text())
            self.assertIn("(Matthew 13:30)", eng_rows[0]["english"][0])
            just_rows = json.loads(just.read_text())
            self.assertEqual(just_rows["bible_refs"][0]["display"], "Matthew 13:30")

    def test_receipt_sentence_is_located_target(self):
        # Live 2026-09-25: **item spread after "sentence": target let the
        # sanitized flag clause clobber the located target, so apply spliced
        # the short clause and duplicated the original citation tail.
        raw = SENT
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Leviticus 14:40",
                "sentence": "Bind the tares and burn them.", "flag_conf": 0.98}
        rows = [{"section": "s", "english": [raw]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 13, 30)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["sentence"], raw)
        self.assertNotEqual(rec["sentence"], item["sentence"])

    def test_apply_end_cite_splice_is_exact(self):
        # End-of-sentence filed cite: the old span must be replaced in place,
        # never kept alongside the new cite.
        raw = "Christ will benefit us nothing. (Leviticus 19:5)"
        new = "Christ will benefit us nothing. (Galatians 5:2)"
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "eng.json"
            eng.write_text(json.dumps([{"section": "s", "english": [raw]}]))
            rec = {"book": "b", "section": "s", "display": "Leviticus 19:5",
                   "proposed": "Galatians 5:2", "sentence": raw,
                   "new_sentence": new, "path": str(eng)}
            self.assertTrue(cc.apply_correction(rec))
            got = json.loads(eng.read_text())[0]["english"][0]
        self.assertEqual(got, new)
        self.assertEqual(got.count("(Galatians 5:2)"), 1)
        self.assertNotIn("Leviticus", got)

    def test_apply_reports_write_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "eng.json"
            eng.write_text(json.dumps([{"section": "s", "english": ["Other."]}]))
            rec = {"book": "b", "section": "s", "sentence": "Absent.",
                   "new_sentence": "Absent. (John 1:1)", "path": str(eng)}
            self.assertFalse(cc.apply_correction(rec))
            self.assertEqual(
                json.loads(eng.read_text())[0]["english"][0], "Other.")

    def test_paren_extra_text(self):
        clean, _, _, s, e = cc.ref_spans("See (John 3:5) now.")[0]
        _ = clean
        self.assertEqual(cc.paren_extra_text("See (John 3:5) now.", s, e), "")
        rng = "Bind (Leviticus 14:40-45) them."
        _, _, _, s, e = cc.ref_spans(rng)[0]
        self.assertEqual(cc.paren_extra_text(rng, s, e), "")
        either = "Light (Mark 1:1 or John 1:34) shines."
        _, _, _, s, e = cc.ref_spans(either)[0]
        self.assertNotEqual(cc.paren_extra_text(either, s, e), "")
        macro = "See ([[Philippians 2:1-4 >> Bible:Philippians 2:1-4]])."
        _, _, _, s, e = cc.ref_spans(macro)[0]
        self.assertNotEqual(cc.paren_extra_text(macro, s, e), "")

    def test_compound_span_holds_replace(self):
        raw = "Jerusalem lament (Isaiah 1:8 (watchtower)) ends."
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Isaiah 1:8", "sentence": raw, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [raw]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("matt", 23, 37)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=8):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["reason"], "compound-span")

    def test_compound_span_holds_dedupe(self):
        raw = ("Light came into the world (Mark 1:1 or John 1:34) "
               "and (John 1:9) shines upon all people.")
        item = {"kind": "correct", "book": "b", "section": "s",
                "display": "Mark 1:1", "sentence": raw, "flag_conf": 0.98}
        rows = [{"section": "s", "english": [raw]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("john", 1, 9)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=3):
            rec = cc.correct_item(item, "tok", 0.85)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["reason"], "compound-span")

    def test_dedupe_rejoins_split_possessive(self):
        sent = "Through one man\u2019 (Romans 3:20)s disobedience (Romans 5:19)."
        out = cc.remove_citation(sent, ("rom", 3, 20))
        self.assertIn("man\u2019s disobedience", out)
        self.assertNotIn("(Romans 3:20)", out)

    def test_backfill_skips_already_cited(self):
        raw = ("He said let there be light over the firmament, and it was "
               "so immediately (Genesis 1:3).")
        item = {"kind": "backfill", "book": "b", "section": "s",
                "display": "", "sentence": raw, "flag_conf": 6.0}
        rows = [{"section": "s", "english": [raw]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [raw])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("gen", 1, 3)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=5):
            rec = cc.correct_item(item, "tok", 0.9)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["reason"], "already-cited")

    def test_insert_citation_at_quote_close(self):
        sent = ("Messengers came and spoke many words about the long journey "
                "through the wilderness, from Kadesh onward to Edom.")
        quote = ("spoke many words about the long journey through the "
                 "wilderness, from Kadesh onward to Edom")
        out = cc.insert_citation_at_quote(sent, quote, "Numbers 20:14")
        self.assertTrue(out.endswith("to Edom (Numbers 20:14)."))
        cont = sent + " And the people listened carefully."
        out2 = cc.insert_citation_at_quote(cont, quote, "Numbers 20:14")
        self.assertIn("to Edom (Numbers 20:14). And the people", out2)

    def test_insert_citation_falls_back_to_end(self):
        sent = "A wholly different sentence about nothing quoted."
        out = cc.insert_citation_at_quote(sent, "absent quote tail", "John 1:1")
        self.assertEqual(out, sent + " (John 1:1)")

    def test_main_skips_active_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/CLAIMS.md").write_text(
                "| c1 | claimed | b | s1 | ag | 2026 | wip | x |\n")
            flags = root / "flags.jsonl"
            flags.write_text(
                '{"book": "b", "section": "s1", "display": "John 3:5", "stratum": "POS_DIRECT", '
                '"clause": "c1", "choice": "contradicts", "confidence": 0.99, "cf": false}\n'
                '{"book": "b", "section": "s2", "display": "John 3:6", "stratum": "POS_DIRECT", '
                '"clause": "c2", "choice": "contradicts", "confidence": 0.99, "cf": false}\n'
                '{"book": "b", "section": "s3", "display": "John 3:7", "stratum": "NEG_XTEST", '
                '"clause": "c3", "choice": "contradicts", "confidence": 0.99, "cf": false}\n')
            with patch.object(cc, "ROOT", root), \
                 patch.dict("os.environ", {"CF_TOKEN": "t", "TYPESAFE_API_KEY": "k"}), \
                 patch.object(cc, "correct_item",
                              return_value={"ok": True, "book": "b", "section": "s2",
                                            "proposed": "P", "confidence": 1}) as m:
                self.assertEqual(cc.main(["--flags", str(flags), "--min-conf", "0.9"]), 0)
            m.assert_called_once()
            called_section = m.call_args[0][0]["section"]
            self.assertEqual(called_section, "s2")


    def test_backfill_skips_para_level_duplicate(self):
        # Live 2026-09-25: "sentence. (cite)" splits; the bare fragment
        # must not earn a second copy of the neighboring cite.
        para = ("Words about light over the firmament spoken plainly. "
                "(Genesis 1:3)")
        item = {"kind": "backfill", "book": "b", "section": "s",
                "display": "",
                "sentence": "Words about light over the firmament spoken plainly.",
                "flag_conf": 6.0}
        rows = [{"section": "s", "english": [para]}]
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [para])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x"), None, rows, 0)]), \
             patch.object(cc, "propose_verse", return_value=("gen", 1, 3)), \
             patch.object(cc, "verify_proposal", return_value=("supports", 0.95, {})), \
             patch.object(cc, "overlap_with_kjv", return_value=5):
            rec = cc.correct_item(item, "tok", 0.9)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["reason"], "already-cited")

    def test_main_backfill_passes_quote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/CLAIMS.md").write_text("")
            flags = root / "flags.jsonl"
            flags.write_text(
                '{"book": "b", "section": "s", "sentence": "He said light be.", '
                '"quote": "light be", "noul": 8.0}\n')
            with patch.object(cc, "ROOT", root), \
                 patch.dict("os.environ", {"CF_TOKEN": "t", "TYPESAFE_API_KEY": "k"}), \
                 patch.object(cc, "correct_item",
                              return_value={"ok": False, "reason": "x"}) as m:
                self.assertEqual(cc.main(["--flags", str(flags), "--mode", "backfill",
                                          "--min-conf", "7", "--books", "b"]), 0)
            m.assert_called_once()
            self.assertEqual(m.call_args[0][0]["quote"], "light be")



class SearchProposerTests(unittest.TestCase):
    def test_search_finds_quoted_verse(self):
        found = cc.search_verses("he says: 'what is left of the meat of the sacrifice "
                                 "on the third day shall be burned with fire'")
        self.assertIn(("lev", 7, 17), found)
        found = cc.search_verses("‘My grace is sufficient for you, for my power is "
                                 "made perfect in weakness’")
        self.assertEqual(found[0], ("2cor", 12, 9))

    def test_clause_before_targets_filed_quote(self):
        sent = ("as the Savior taught, 'The servant does not know what his master does' "
                "(Matthew 13:52), and as Peter wrote, 'into which angels desire to stoop' (1 Peter 1:12).")
        seg = cc.clause_before(sent, ("matt", 13, 52))
        self.assertIn("servant", seg)
        self.assertNotIn("angels", seg)
        seg = cc.clause_before(sent, ("1pet", 1, 12))
        self.assertIn("angels", seg)
        self.assertNotIn("servant", seg)
        self.assertIn(("john", 15, 15),
                      cc.search_verses(cc.clause_before(sent, ("matt", 13, 52))))

    def test_remove_citation_keeps_punctuation_tight(self):
        out = cc.remove_citation("he says, 'I am the vine' (Romans 2:1), and adds more (John 15:1).",
                                 ("rom", 2, 1))
        self.assertEqual(out, "he says, 'I am the vine', and adds more (John 15:1).")

    def test_span_covers_range(self):
        sent = "burned in fire (Leviticus 7:16\u201317) (1 Corinthians 5:7)."
        spans = cc.ref_spans(sent)
        lev = [sp for sp in spans if sp[0] == "lev"][0]
        self.assertTrue(cc.span_covers(sent, lev, ("lev", 7, 17)))
        self.assertTrue(cc.span_covers(sent, lev, ("lev", 7, 16)))
        self.assertFalse(cc.span_covers(sent, lev, ("lev", 7, 18)))

    def test_nested_gloss_is_compound(self):
        sent = ("says 'stewards of the mysteries' (Jeremiah 5:3 (LXX) Micah 3:11 "
                "('they lean upon the Lord, saying...')) next.")
        mic = [sp for sp in cc.ref_spans(sent) if sp[0] == "mic"][0]
        self.assertTrue(cc.paren_extra_text(sent, mic[3], mic[4]))
        clean = "word (John 3:5) more."
        john = cc.ref_spans(clean)[0]
        self.assertEqual(cc.paren_extra_text(clean, john[3], john[4]), "")

    def test_two_verifiers_agreeing_accept(self):
        sent = "He said: 'what is left of the sacrifice on the third day shall be burned' (Leviticus 17:11)."
        rows = [{"section": "1", "english": [sent]}]
        def run(second):
            with patch.object(cc.cite, "load_section_texts", return_value=("g", [sent])), \
                 patch.object(cc, "english_candidates", return_value=[(Path("x_english.json"), rows, rows, 0)]), \
                 patch.object(cc, "greek_for_file", return_value="g"), \
                 patch.object(cc, "search_verses", return_value=[("lev", 7, 17)]), \
                 patch.object(cc, "propose_verse", return_value=None), \
                 patch.object(cc, "overlap_any", return_value=2), \
                 patch.object(cc, "verify_proposal", return_value=("supports", 0.6, {})), \
                 patch.object(cc, "second_opinion", return_value=second):
                return cc.correct_item({"book": "b", "section": "1", "display": "Leviticus 17:11",
                                        "sentence": sent}, "tok", 0.85)
        rec = run(("supports", 0.7))
        self.assertTrue(rec["ok"], rec)
        self.assertEqual(rec["basis"], "jev+clef")
        self.assertFalse(run(("contradicts", 0.9))["ok"])
        self.assertFalse(run(("supports", 0.3))["ok"])

    def test_correct_item_tries_next_candidate(self):
        sent = "He said: 'what is left of the sacrifice on the third day shall be burned' (Leviticus 17:11)."
        rows = [{"section": "1", "english": [sent]}]
        verdicts = iter([("contradicts", 0.9, {}), ("supports", 0.95, {})])
        with patch.object(cc.cite, "load_section_texts", return_value=("g", [sent])), \
             patch.object(cc, "english_candidates",
                          return_value=[(Path("x_english.json"), rows, rows, 0)]), \
             patch.object(cc, "greek_for_file", return_value="g"), \
             patch.object(cc, "search_verses", return_value=[("lev", 7, 15), ("lev", 7, 17)]), \
             patch.object(cc, "propose_verse", return_value=("lev", 17, 11)), \
             patch.object(cc, "overlap_any", return_value=3), \
             patch.object(cc, "verify_proposal", side_effect=lambda *a: next(verdicts)):
            rec = cc.correct_item({"book": "b", "section": "1", "display": "Leviticus 17:11",
                                   "sentence": sent}, "tok", 0.85)
        self.assertTrue(rec["ok"], rec)
        self.assertEqual(rec["proposed"], "Leviticus 7:17")
        self.assertIn("(Leviticus 7:17)", rec["new_sentence"])
        self.assertEqual(len(rec["tried"]), 2)


if __name__ == "__main__":
    unittest.main()
