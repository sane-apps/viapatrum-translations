#!/usr/bin/env python3
"""Regression: tip closeout cannot outrun catalogue scaffold/contamination gates."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.check_pass_ab import (
    PLACEHOLDER,
    check_record,
    check_translation_files,
    content_errors,
)
from llm_bakeoff import score


class TipReadyGateTest(unittest.TestCase):
    def test_score_refuses_lemma_led_and_rem_scaffold(self) -> None:
        for bad in (
            "Lemma-led open — Greek unit 1 toward the thesis.",
            "Rem early: Unit 1; lemma and argument toward the thesis.",
            "Rem CLOSEOUT: Unit 1 CLOSEOUT for series stamp.",
        ):
            result = score(
                {
                    "section": "1",
                    "title": "A real thought title for the section",
                    "pass_a_gloss": "A long enough independent gloss that is not the reading text at all.",
                    "english": [bad + " Finished sentence."],
                    "lemmas": [{"form": "λόγος", "gloss": "word"}],
                },
                "{}",
                "1",
                source=["Ἱκανὸν ἑλληνικὸν κείμενον εἰς ἔλεγχον."],
            )
            self.assertFalse(result["ok"], bad)
            self.assertFalse(result["checks"].get("no_placeholders"), bad)

    def test_score_accepts_clean_pair(self) -> None:
        result = score(
            {
                "section": "1",
                "title": "On the Samaritan woman’s well",
                "pass_a_gloss": "Independent gloss covering the Greek clauses without copying Pass B wording here.",
                "english": [
                    "Perhaps you would have preferred that the discourse not be broken between books."
                ],
                "lemmas": [{"form": "φρέαρ", "gloss": "well"}],
            },
            "{}",
            "1",
            source=[
                "Ἴσως μὲν ἂν ἔδοξέ σοι τὸν περὶ τῆς Σαμαρείτιδος λόγον μὴ διακοπῆναι."
            ],
        )
        self.assertTrue(result["ok"], result)

    def test_translation_files_refuse_scaffold_and_source_ops(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            eng = root / "x_english.json"
            src = root / "x_source.json"
            eng.write_text(
                json.dumps(
                    [
                        {
                            "section": 1,
                            "english": ["Lemma-led open — fake finished work."],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            src.write_text(
                json.dumps(
                    [
                        {
                            "section": 1,
                            "latin": [
                                "Melito skipped; never Cyril Matthew densify."
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            errors = check_translation_files(eng, src)
            self.assertTrue(any("placeholder or operational" in e for e in errors))

    def test_translation_files_refuse_temporary_in_latin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            eng = root / "x_english.json"
            src = root / "x_source.json"
            eng.write_text(
                json.dumps(
                    [
                        {
                            "section": 4,
                            "english": [
                                "Esau sells the birthright for a meal, and despises what is holy."
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            src.write_text(
                json.dumps(
                    [
                        {
                            "section": 4,
                            "latin": [
                                "Profanus qui pro cibo temporary primatum spiritus vendit."
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            errors = check_translation_files(eng, src)
            self.assertTrue(errors)
            self.assertTrue(
                any("operational" in e or "temporary" in e.lower() or "English/operational" in e for e in errors)
            )

    def test_placeholder_regex_matches_catalogue_smells(self) -> None:
        self.assertTrue(PLACEHOLDER.search("Lemma-led open — X"))
        self.assertTrue(PLACEHOLDER.search("Rem mid: Unit 2"))
        self.assertTrue(content_errors(["clean English sentence."]) == [])
        self.assertTrue(check_record({"pass_a_gloss": "x", "pass_b_english": ["Lemma-led open — y"], "source_text": "z", "lemmas": [], "choices": []}))


if __name__ == "__main__":
    unittest.main()
