#!/usr/bin/env python3
"""Offline regressions for the Jev citation checker. Never calls the API."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jev_cite_check as jc


class CiteCheckTests(unittest.TestCase):
    def test_display_ref(self):
        self.assertEqual(jc.display_ref(("john", 3, 5)), "John 3:5")
        self.assertEqual(jc.display_ref(("ps", 23, None)), "Psalms 23")
        self.assertEqual(jc.display_ref(("2cor", 3, 14)), "2 Corinthians 3:14")
        self.assertEqual(jc.display_ref(("zzz", 1, 1)), "zzz 1:1")

    def test_pairs_prepend_previous_sentence(self):
        paras = ["For unless one is born of water and spirit. (John 3:5) The Jews lack goods."]
        pairs = jc.cite_pairs(paras)
        self.assertEqual(len(pairs), 1)
        clause, _ref, display, cf = pairs[0]
        self.assertEqual(display, "John 3:5")
        self.assertIn("born of water", clause)
        self.assertFalse(cf)

    def test_pairs_keep_long_head(self):
        paras = ["For it is written, 'Man shall not live by bread alone.' (Deuteronomy 8:3)"]
        pairs = jc.cite_pairs(paras)
        self.assertEqual(len(pairs), 1)
        self.assertIn("bread alone", pairs[0][0])

    def test_pairs_cf_flag(self):
        paras = ["Bread alone. (Deuteronomy 8:3; cf. Matthew 4:4)"]
        pairs = jc.cite_pairs(paras)
        self.assertEqual(len(pairs), 2)
        by_display = {d: cf for _, _, d, cf in pairs}
        self.assertFalse(by_display["Deuteronomy 8:3"])
        self.assertTrue(by_display["Matthew 4:4"])

    def test_sanitize_strips_filed_answer(self):
        self.assertEqual(jc.sanitize_clause("Born of water. (John 3:5)"), "Born of water.")
        self.assertEqual(jc.sanitize_clause("[[Let us sing >> Bible:Exodus 15:1]]"), "Let us sing")
        self.assertEqual(jc.sanitize_clause("Plain (note) words."), "Plain (note) words.")

    def test_pairs_dedupe(self):
        paras = ["Bread. (John 3:5)", "Bread. (John 3:5)"]
        self.assertEqual(len(jc.cite_pairs(paras)), 1)

    def test_build_questions_shape(self):
        pairs = [("clause words", ("john", 3, 5), "John 3:5", False)]
        qs = jc.build_questions(pairs)
        self.assertEqual(set(qs), {"cite0"})
        q = qs["cite0"]
        self.assertEqual(q["type"], "choice")
        self.assertIn("John 3:5", q["instructions"])
        self.assertIn("clause words", q["instructions"])
        self.assertEqual(set(q["criteria"]), {"supports", "contradicts", "says_nothing"})

    def test_check_section_maps_verdicts(self):
        texts = ("g1", ["Born of water and spirit. (John 3:5)"])
        body = {"model": "jev-1.13.0", "usage": {"input_tokens": 1, "output_tokens": 1},
                "answers": {"cite0": {"choice": "supports", "confidence": 0.95,
                                      "probabilities": {"supports": 0.95}}}}
        with patch.object(jc, "load_section_texts", return_value=texts), \
             patch.object(jc, "jev", return_value=body):
            result = jc.check_section("b", "s")
        self.assertEqual(len(result["cites"]), 1)
        cite = result["cites"][0]
        self.assertEqual(cite["verdict"], "verified")
        self.assertTrue(cite["auto"])
        self.assertFalse(cite["cf"])

    def test_load_section_texts_direct(self):
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp) / "books" / "b" / "translations"
            tdir.mkdir(parents=True)
            (tdir / "x_english.json").write_text(
                json.dumps([{"section": "s1", "english": ["Body (John 3:5)."]}]))
            (tdir / "x_source.json").write_text(
                json.dumps([{"section": "s1", "greek": "g"}]))
            with patch.object(jc.promote, "ROOT", Path(tmp)):
                greek, paras = jc.load_section_texts("b", "s1")
        self.assertEqual(greek, "g")
        self.assertEqual(paras, ["Body (John 3:5)."])

    def test_check_section_no_cites(self):
        texts = ("g1", ["No cites here."])
        with patch.object(jc, "load_section_texts", return_value=texts):
            result = jc.check_section("b", "s")
        self.assertEqual(result["cites"], [])


if __name__ == "__main__":
    unittest.main()
