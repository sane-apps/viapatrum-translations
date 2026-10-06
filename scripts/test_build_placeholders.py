#!/usr/bin/env python3
"""Regressions: scaffold rows never ship as translation. Offline."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_pbb_docx import (
    PENDING_ENGLISH,
    _plain_heading,
    _reader_note,
    collect_sections,
    is_scaffold_english,
)
from pipeline.verify_docx import verify_docx


def make_docx(path, texts):
    paras = "".join(
        f"<w:p><w:r><w:t>{t}</w:t></w:r></w:p>" for t in texts)
    xml = (f'<w:document xmlns:w="u"><w:body>{paras}</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)


CLEAN_PARAS = ["[[xx &gt;&gt; Bible:John 3:16]]", "[[@Headword:TN 1]]", "Plain text."]


class ScaffoldTests(unittest.TestCase):
    def test_detects_leads(self):
        self.assertTrue(is_scaffold_english(["Rem early: Unit 1; lemma text."]))
        self.assertTrue(is_scaffold_english(["Rem mid: historia held."]))
        self.assertTrue(is_scaffold_english(["Rem CLOSEOUT: Unit 1 CLOSEOUT."]))
        self.assertTrue(is_scaffold_english(["Lemma-led open — foo"]))
        self.assertTrue(is_scaffold_english(["ZU LK 24, 51."]))
        self.assertTrue(is_scaffold_english(["", "  ", "Rem early: x"]))

    def test_ignores_content(self):
        self.assertFalse(is_scaffold_english(["For God so loved the world."]))
        self.assertFalse(is_scaffold_english([]))
        self.assertFalse(is_scaffold_english([""]))
        self.assertFalse(is_scaffold_english(["Unit 1 rem early"]))
        self.assertFalse(is_scaffold_english(["[English pending.]"]))

    def test_collector_maps_scaffold_to_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            trans = Path(tmp) / "translations"
            trans.mkdir()
            src = [{"section": "a", "greek": "g"}, {"section": "b", "greek": "g"}]
            eng = [{"section": "a", "title": "Ta", "english": ["Rem early: Unit 1."]},
                   {"section": "b", "title": "Tb", "english": ["Real translation."]}]
            (trans / "x_source.json").write_text(json.dumps(src))
            (trans / "x_english.json").write_text(json.dumps(eng))
            sections = collect_sections(Path(tmp), None)
        self.assertEqual(sections[0]["english"], [PENDING_ENGLISH])
        self.assertEqual(sections[1]["english"], ["Real translation."])

    def test_collector_skips_tip_that_repeats_the_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            trans = Path(tmp) / "translations"
            trans.mkdir()
            whole = [{"section": "1", "title": "Song", "english": ["Horse and rider."]}]
            (trans / "hom6_source.json").write_text(json.dumps([{"section": "1"}]))
            (trans / "hom6_english.json").write_text(json.dumps(whole))
            (trans / "hom6_1_1_source.json").write_text(json.dumps([{"section": "1"}]))
            (trans / "hom6_1_1_english.json").write_text(json.dumps(whole))
            sections = collect_sections(Path(tmp), None)
        self.assertEqual([s["slice"] for s in sections], ["hom6"])

    def test_reader_note_drops_shop_talk(self):
        self.assertEqual(_reader_note("True OET; Pass A ≠ Pass B."), "")
        self.assertEqual(_reader_note("The Greek text may be fragmented."), "")
        self.assertEqual(_reader_note("SERIES CLOSEOUT."), "")
        self.assertEqual(_reader_note("Lacunae marked [...]. Machine draft tip-checked."), "")
        self.assertEqual(_reader_note("Corpus-wide Rank-1 Evagrius PG 40; densify-lane."), "")
        kept = _reader_note("The quotation is from Proverbs 19:3.")
        self.assertIn("Proverbs 19:3", kept)

    def test_plain_heading_strips_a_nested_bible_marker(self):
        raw = "Virgin birth and [[God with us >> Bible:Matthew 1:23]]; dove"
        self.assertEqual(_plain_heading(raw), "Virgin birth and God with us; dove")

    def test_english_tail_is_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp)
            trans = book / "translations"
            trans.mkdir()
            (trans / "ep_source.json").write_text(json.dumps([{"section": "1"}]))
            (trans / "ep_english.json").write_text(json.dumps([
                {"section": "1", "title": "Open", "english": ["One."]},
                {"section": "2", "title": "Close", "english": ["Two."]},
            ]))
            self.assertEqual(len(collect_sections(book, None)), 1)
            (book / "book.yml").write_text('logos_english_tail: "true"\n')
            self.assertEqual(
                [s["title"] for s in collect_sections(book, None)],
                ["Open", "Close"],
            )

    def test_verifier_refuses_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.docx"
            make_docx(bad, CLEAN_PARAS + ["Rem early: Unit 1; lemma text."])
            errors = verify_docx(bad)
        self.assertTrue(any("scaffold" in e for e in errors), errors)

    def test_verifier_passes_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.docx"
            make_docx(good, CLEAN_PARAS + [PENDING_ENGLISH])
            self.assertEqual(verify_docx(good), [])


if __name__ == "__main__":
    unittest.main()
