#!/usr/bin/env python3
"""Regression: tip closeout cannot outrun catalogue scaffold/contamination gates."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.check_pass_ab import (
    _failed_greek_scan,
    PLACEHOLDER,
    check_record,
    check_translation_files,
    content_errors,
    repeated_paragraph,
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

    def test_julian_shaped_source_rows_pass(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "en.json"
            src = Path(tmp) / "src.json"
            eng.write_text(
                json.dumps(
                    [
                        {
                            "section": "50",
                            "english": ["The judge will stir all things."],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            src.write_text(
                json.dumps(
                    [
                        {
                            "book": 1,
                            "section": 50,
                            "julian": ["examinator cunctorum in ultimo die."],
                            "augustine": ["Respondit Augustinus ita."],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(check_translation_files(eng, src), [])

    def test_photius_shaped_source_dict_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "en.json"
            src = Path(tmp) / "src.json"
            eng.write_text(
                json.dumps(
                    [
                        {
                            "codex": 8,
                            "title": "Origen, De Principiis",
                            "english": ["I read the four books On First Principles."],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            src.write_text(
                json.dumps(
                    {
                        "codex": 8,
                        "title_greek": "\u1f08\u03bd\u03ad\u03b3\u03bd\u03c9\u03bd \u03c4\u1f70 \u03c4\u1f73\u03c3\u03c3\u03b1\u03c1\u03b1 \u03b2\u03b9\u03b2\u03bb\u03af\u03b1 \u1f68\u03c1\u03b9\u03b3\u1f73\u03bd\u03bf\u03c5\u03c2 \u03a0\u03b5\u03c1\u1f76",
                        "greek": "\u1f08\u03bd\u03ad\u03b3\u03bd\u03c9\u03bd \u03c4\u1f70 \u03c4\u1f73\u03c3\u03c3\u03b1\u03c1\u03b1 \u03b2\u03b9\u03b2\u03bb\u03af\u03b1 \u1f68\u03c1\u03b9\u03b3\u1f73\u03bd\u03bf\u03c5\u03c2 \u03a0\u03b5\u03c1\u1f76 \u1f08\u03c1\u03c7\u1ff6\u03bd.",
                        "bekker_page": "8",
                        "notes": "test",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(check_translation_files(eng, src), [])

    def test_photius_codex_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "en.json"
            src = Path(tmp) / "src.json"
            eng.write_text(
                json.dumps([{"codex": 8, "english": ["I read the four books."]}]),
                encoding="utf-8",
            )
            src.write_text(
                json.dumps({"codex": 9, "greek": "test"}),
                encoding="utf-8",
            )
            errors = check_translation_files(eng, src)
            self.assertTrue(any("section set mismatch" in e for e in errors))

    def test_dropped_section_and_repeated_paragraph_fail_the_draft_gate(self) -> None:
        para = "The opening line about the soul and the body is copied again below in full."
        self.assertTrue(repeated_paragraph([para, para]))
        self.assertEqual(repeated_paragraph([para, "A second paragraph about grace and the law of the Spirit."]), "")
        self.assertEqual(repeated_paragraph(["Amen.", "Amen."]), "")
        # The site build calls content_errors, not this draft check.
        self.assertEqual(content_errors([para, para]), [])
        gloss = "A full gloss that is not the reading text and covers each clause in its own words."
        notes = {"lemmas": [{"form": "λόγος", "gloss": "word"}], "choices": [{"term": "λόγος", "english": "word"}]}
        short = check_record({
            "pass_a_gloss": gloss,
            "pass_b_english": [" ".join(["word"] * 30)],
            "source_text": " ".join(["λόγος"] * 100),
            **notes,
        })
        self.assertTrue(any("far shorter than the source" in e for e in short), short)
        self.assertTrue(any("paragraph is repeated" in e for e in check_record({
            "pass_a_gloss": gloss,
            "pass_b_english": [para, para],
            "source_text": " ".join(["λόγος"] * 40),
            **notes,
        })))
        covered = check_record({
            "pass_a_gloss": " ".join(["gloss"] * 80),
            "pass_b_english": [" ".join(["word"] * 100)],
            "source_text": " ".join(["λόγος"] * 100),
            **notes,
        })
        self.assertFalse(any("far shorter" in e or "far longer" in e for e in covered), covered)
        added = check_record({
            "pass_a_gloss": " ".join(["gloss"] * 80),
            "pass_b_english": [" ".join(["word"] * 400)],
            "source_text": " ".join(["λόγος"] * 100),
            **notes,
        })
        self.assertTrue(any("far longer than the source" in e for e in added), added)

    def test_placeholder_regex_matches_catalogue_smells(self) -> None:
        self.assertTrue(PLACEHOLDER.search("Lemma-led open — X"))
        self.assertTrue(PLACEHOLDER.search("Rem mid: Unit 2"))
        self.assertTrue(content_errors(["clean English sentence."]) == [])
        self.assertTrue(check_record({"pass_a_gloss": "x", "pass_b_english": ["Lemma-led open — y"], "source_text": "z", "lemmas": [], "choices": []}))



    def test_folio_debris_and_stuck_phrase_fail(self) -> None:
        loop = (
            "grace abounded to many grace abounded to many grace abounded to many "
            "and the sentence then continues in ordinary English."
        )
        self.assertTrue(any("repeated phrase" in e for e in content_errors(loop)))
        citation = (
            "neither sin nor eternal death is transmitted through Adam "
            "(compare Romans 5:15; Revelation 20:14) (Romans 5:15) "
            "(Revelation 20:14) (Romans 5:15; Revelation 20:14)."
        )
        self.assertEqual(content_errors(citation), [])
        latin = (
            "The margin then runs et quod cum enim autem sunt sed est quo quae "
            "before the English resumes its course."
        )
        self.assertTrue(any("Latin left" in e for e in content_errors(latin)))
        self.assertEqual(
            content_errors("He answers sed contra and moves on to the next question about grace."),
            [],
        )
        self.assertTrue(any("debris" in e for e in content_errors(
            "The note reads desperate32 28 is a plague upon the page.")))
        self.assertTrue(any("debris" in e for e in content_errors(
            "The quire mark Aij was read as a word in the sentence about grace.")))
        self.assertEqual(
            content_errors("Plural Dii on the calves tracks Hebrew idiom, not a pantheon."),
            [],
        )
        self.assertTrue(any("debris" in e for e in content_errors(
            "Cap. 10 complete. Next begins PHYS 323.")))
        self.assertTrue(any("debris" in e for e in content_errors("Densify COMPLETE for this chapter.")))
        self.assertTrue(any("debris" in e for e in content_errors(["The prayer ends here.", "28"])))
        self.assertTrue(any("debris" in e for e in content_errors(["The prayer ends here.", "Ciiij"])))
        self.assertEqual(
            content_errors("There is one Physician, both flesh and spirit, born and unborn."),
            [],
        )
        self.assertTrue(any("reuse footer" in e for e in content_errors(["The free use is permitted."])))
        self.assertTrue(any("reuse footer" in e for e in content_errors(
            ["[Source too fragmentary to translate; likely a footer.]"])))
        self.assertTrue(any("reuse footer" in e for e in content_errors(
            "Επιτρέπεται η ελεύθερη χρήση του υλικού", "source", source=True)))
        self.assertTrue(any("reuse footer" in e for e in content_errors(
            "ην πηγή προέλευσής του.", "source", source=True)))
        self.assertEqual(content_errors("He permits the free use of reason in this question."), [])
        greek = (
            "Ἴσως μὲν ἂν ἔδοξέ σοι τὸν περὶ τῆς Σαμαρείτιδος λόγον μὴ διακοπῆναι "
            "ἐν τῷ μέσῳ τῆς ἐξηγήσεως ταύτης καὶ πάλιν ὁ αὐτὸς λόγος πρόεισιν."
        )
        self.assertEqual(content_errors(greek, "source", source=True), [])
        latin_source = (
            "Sicut mysteria paschae, quae in testamento ueteri celebrabantur, "
            "et quod cum enim autem sunt figurae noui testamenti, non est dubium."
        )
        self.assertEqual(content_errors(latin_source, "source", source=True), [])
        gloss = (
            "Tertiam prophetiam Balaam tractamus. Balac putat locum defuisse maledictioni; "
            "ducit eum in verticem Phogor, et populus manet in campis."
        )
        self.assertEqual(content_errors(gloss, "source", source=True), [])
        betacode = (
            r"kainou\j de\ ou)ranou\j kai\ kainh\n gh=n kai\ ta\ e)pagge/lmata "
            r"au)tou= prosdokw\men katallagh\n kai\ th\n a)polutrwsin"
        )
        self.assertTrue(any("broken Greek scan" in e for e in content_errors(
            betacode, "source", source=True)))

    def test_source_placeholder_and_escaped_quotes(self) -> None:
        # Audit 2026-10-06: Origen on Luke stored an editor's note as the source.
        note = "(Jerome Latin working note; lemma Luke 2:21-24. Full Rauer GCS 35 text to be locked locally.)"
        self.assertTrue(any("not locked source" in e for e in content_errors([note], "source_text", source=True)))
        self.assertTrue(content_errors("(Jerome Latin note; lemma Luke 4:1-13.)", "s", source=True))
        self.assertTrue(content_errors("Rufinus text to be locked from GCS.", "s", source=True))
        # English reading text keeps the old gate (live pages are not newly blocked).
        self.assertEqual(content_errors("He kept a working note of the lemma Luke 2:21."), [])
        # Escaped quotes in a Latin lock (tap_source entry 12) are not a broken scan.
        latin = (
            r"et hic enim dicendo \'deus in te\' et (tu deus\' duos proponit: qui erat in Christo et [spiritum] "
            r"ipsum. plus est, quod (et) in euangelio totidem inuenies: in principio erat sermo, et sermo erat apud "
            r"deum, et deus erat sermo: unus, qui erat, et alius, penes quem erat. sed et nomen domini in duobus "
            r"lego: dixit dominus domino meo: sede ad dexteram meam. et Esaias haec dicit: domine, quis credidit "
            r"auditui nostro, et brachium domini cui reuelatum est? \'brachium\' enim \'tuum\', non \'domini\' "
            r"dixisset, si non dominum patrem et dominum filium intellegi"
        )
        self.assertGreaterEqual(latin.count("\\"), 8)
        self.assertFalse(_failed_greek_scan(latin))
        self.assertEqual(content_errors(latin, "source", source=True), [])
        # A real betacode scan (cyril-alexandria-isaiah book 5) still fails.
        beta = (r"hj, kainou\j de\ ou)- ranou\ j, kai\ kainh\n gh=n, kai\ ta\ e)pagge/lmata au) tou= "
                r"prosdokw\men, kata\ to\ gegramme/non. Efh de/ ti toiou=- ton kai\ au)to\j o(")
        self.assertTrue(_failed_greek_scan(beta))


if __name__ == "__main__":
    unittest.main()
