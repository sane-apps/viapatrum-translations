"""Mutation checks for the known false-pass failure modes; no model calls."""
import json
from pathlib import Path
import tempfile
import unittest

from pipeline.check_pass_ab import check_file, check_record, main as pass_main
from pipeline.verify_translation_qa import (
    SEMANTIC_CHECKS, check_excerpts, check_justifications, digest, file_digest,
    make_audit_packet, validate_audit_receipt, validate_semantic_review, reviewed_section_errors,
)


class TranslationQATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.english = self.root / "english.json"
        self.source = self.root / "source.json"
        self.raw = self.root / "print.txt"
        self.raw.write_text("Latin printed witness. Verified passage at page 20.")
        self.identity = {"author": "Test author", "work": "Test work", "edition": "Test edition",
                         "locus_scheme": "section", "source_url": "https://example.test/source"}
        self.write(self.source, [{"section": str(i), "locus": f"Work {i}",
                                 "latin": [f"Non necessitate sed voluntate {i}."]}
                                for i in range(1, 9)])
        self.write(self.english, [{"section": str(i), "english": [
            f"Choice is voluntary, never forced by necessity. Passage {i}."]}
                                 for i in range(1, 9)])

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def justification(self):
        return {"excerpt_id": "x", "source_text": "Non necessitate sed voluntate.",
                "pass_a_gloss": "The act comes about by willing, with necessity denied.",
                "pass_b_english": ["We choose freely; no one forces this decision upon us."],
                "lemmas": [{"form": "voluntate", "gloss": "by willing"}],
                "choices": [{"term": "necessitate", "why": "negated in source"}],
                "edition": {"path": str(self.raw), "sha256": file_digest(self.raw), "locus": "20"},
                "confidence": "source_verified"}

    def packet(self):
        return make_audit_packet(self.english, self.source, raw_sources=[self.raw],
                                 seed=42, sample_size=5, identity=self.identity)

    def receipt(self, packet):
        return {"packet_id": packet["packet_id"], "reviewer": "test-reviewer",
                "verdict": "pass", "reviews": [{
                    "section": s["section"], "verdict": "pass",
                    "checks": {key: True for key in SEMANTIC_CHECKS},
                    "uncertainties": [], "notes": "Synthetic fixture evidence only.",
                    "covered_source_paragraphs": list(range(1, len(s["source_text"]) + 1)),
                } for s in packet["sections"]]}

    def test_scaffold_empty_and_invalid_files_fail(self):
        self.write(self.english, [])
        self.assertTrue(check_excerpts(self.english))
        with self.assertRaises(ValueError):
            self.packet()
        self.english.write_text("{broken")
        self.assertTrue(check_file(self.english))
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(pass_main([str(empty)]), 1)
        for text in ("Rem early: Unit 1; lemma and argument toward the thesis.",
                     "Lemma-led open — ΑΓΑΘΙΟΥ", "(Rufinus; see working file)", ""):
            j = self.justification()
            j["pass_b_english"] = [text]
            self.assertTrue(check_record(j))

    def test_disguised_copy_and_greek_are_flagged(self):
        j = self.justification()
        self.assertEqual(check_record(j), [])
        j["pass_a_gloss"] = "WE choose freely — no one forces this decision upon us!"
        self.assertTrue(any("copies" in e for e in check_record(j)))
        j["pass_a_gloss"] = "Literal gloss: We choose freely; no one forces this decision upon us."
        self.assertTrue(any("near-copies" in e for e in check_record(j)))
        j["pass_b_english"] = ["Καὶ οὐχὶ ἀνάγκῃ ἀλλὰ προαιρέσει πράττομεν."]
        self.assertTrue(any("Greek" in e for e in check_record(j)))
        j["source_text"] = "Melito skipped; never Cyril Matthew densify."
        self.assertTrue(any("operational" in e for e in check_record(j)))

    def test_snapshot_and_coverage_mutations_fail(self):
        packet = self.packet()
        self.assertEqual(packet, self.packet())
        self.assertIn("1", [s["section"] for s in packet["sections"]])
        self.assertIn("8", [s["section"] for s in packet["sections"]])
        receipt = self.receipt(packet)
        self.assertEqual(validate_audit_receipt(packet, receipt), [])
        self.raw.write_text("Changed print")
        self.assertTrue(any("stale" in e for e in validate_audit_receipt(packet, receipt)))
        self.assertNotEqual(packet["packet_id"], self.packet()["packet_id"])
        rows = json.loads(self.english.read_text())
        self.write(self.english, rows[:-1])
        self.assertTrue(any("missing expected" in e for e in self.packet()["structural_errors"]))
        self.write(self.english, rows + [rows[0]])
        with self.assertRaises(ValueError):
            self.packet()

    def test_receipt_cannot_approve_other_or_partial_packet(self):
        packet = self.packet()
        receipt = self.receipt(packet)
        receipt["reviews"][0]["checks"]["negation"] = "true"
        self.assertTrue(validate_audit_receipt(packet, receipt))
        receipt = self.receipt(packet)
        receipt["reviews"][0]["uncertainties"] = ["Unclear"]
        self.assertTrue(validate_audit_receipt(packet, receipt))
        receipt = self.receipt(packet)
        receipt["reviews"].pop()
        self.assertTrue(validate_audit_receipt(packet, receipt))
        receipt = self.receipt(packet)
        packet["sections"][0]["english"] = ["Silently changed"]
        self.assertTrue(any("packet contents" in e for e in validate_audit_receipt(packet, receipt)))
        self.assertTrue(validate_semantic_review({}, 1))
        review = self.receipt(self.packet())["reviews"][0]
        review["covered_source_paragraphs"] = [True]
        self.assertTrue(validate_semantic_review(review, 1))
        self.assertTrue(validate_audit_receipt({"schema": "translation-audit-v1",
                                              "raw_source_paths": ["x"], "files": []}, {}))

    def test_current_english_and_raw_hash_required(self):
        j = self.justification()
        self.write(self.english, [{"id": "x", "confidence": "source_verified",
                                  "english": j["pass_b_english"]}])
        just_dir = self.root / "reviews/justifications"
        self.write(just_dir / "x.json", j)
        self.assertEqual(check_justifications(self.english, just_dir), [])
        self.write(self.english, [{"id": "x", "confidence": "source_verified",
                                  "english": ["Changed English."]}])
        self.assertTrue(any("snapshot" in e for e in check_justifications(self.english, just_dir)))
        self.raw.write_text("new raw print")
        self.assertTrue(any("hash" in e for e in check_justifications(self.english, just_dir)))

    def test_consumer_must_match_selected_current_passage(self):
        packet = self.packet()
        receipt = self.receipt(packet)
        item = packet["sections"][0]
        self.assertEqual(reviewed_section_errors(packet, receipt, item["section"],
                                                 item["source_text"], item["english"], expected_identity=self.identity), [])
        self.assertTrue(reviewed_section_errors(packet, receipt, "999",
                                                item["source_text"], item["english"], expected_identity=self.identity))
        self.assertTrue(reviewed_section_errors(packet, receipt, item["section"],
                                                ["Different source"], item["english"], expected_identity=self.identity))
        self.assertTrue(reviewed_section_errors(packet, receipt, item["section"],
                                                item["source_text"], ["Edited English"], expected_identity=self.identity))
        packet["sections"][0]["english"] = ["Counterfeit packet"]
        packet["packet_id"] = digest({k: v for k, v in packet.items() if k != "packet_id"})
        receipt = self.receipt(packet)
        self.assertTrue(any("regenerated" in e for e in validate_audit_receipt(packet, receipt)))

    def test_identity_targeted_selection_and_scope_review_are_bound(self):
        packet = make_audit_packet(self.english, self.source, raw_sources=[self.raw],
                                  identity=self.identity, selected_sections=["3"])
        self.assertEqual([s["section"] for s in packet["sections"]], ["3"])
        receipt = self.receipt(packet)
        item = packet["sections"][0]
        self.assertEqual(validate_audit_receipt(packet, receipt), [])
        wrong = {**self.identity, "author": "Wrong author"}
        self.assertTrue(reviewed_section_errors(packet, receipt, "3",
                        item["source_text"], item["english"], expected_identity=wrong))
        scoped = make_audit_packet(self.english, self.source, raw_sources=[self.raw],
                                  identity=self.identity, publication_scope={"section_ids": ["1", "2"]})
        receipt = self.receipt(scoped)
        self.assertTrue(any("scope review" in e for e in validate_audit_receipt(scoped, receipt)))
        receipt["scope_review"] = receipt["reviews"][0]
        self.assertEqual(validate_audit_receipt(scoped, receipt), [])

    def test_jeremiah_6_1_source_checked_correction(self):
        book = Path(__file__).resolve().parents[2] / "books/origen-jeremiah-samuel"
        en = next(r for r in json.loads((book / "translations/jeremiah_english.json").read_text())
                  if r["section"] == "6.1")
        source = next(r for r in json.loads((book / "translations/jeremiah_source.json").read_text())
                      if r["section"] == "6.1")
        just = json.loads((book / "reviews/justifications/jeremiah_6_1.json").read_text())
        self.assertEqual(just["pass_b_english"], en["english"])
        self.assertEqual(just["source_text"], " ".join(source["greek"]))
        self.assertNotIn("purity", " ".join(en["english"]))
        self.assertIn("power and love and self-control", en["english"][1])
        self.assertIn("ἀγάπης", source["greek"][1])
        self.assertNotIn("ἀπάπης", source["greek"][1])
        self.assertIn("see how much can be drawn", en["english"][0])
        self.assertIn("Sirach 21:15", en["english"][0])
        for ref in ("Jeremiah 5:3", "Psalm 34:15", "Sirach 21:15",
                    "1 Corinthians 13:13", "2 Timothy 1:7", "Psalm 4:6"):
            self.assertIn(f">> Bible:{ref}]]", " ".join(en["english"]))
        self.assertEqual(just["edition"]["sha256"], file_digest(book / just["edition"]["path"]))
        self.assertIn("missing", en["english"][1])
        self.assertNotEqual(just["checks"].get("fidelity"), "pass")

    def test_julian_1_27_reference_alignment_and_current_review(self):
        book = Path(__file__).resolve().parents[2] / "books/julian-of-eclanum"
        packet = json.loads((book / "reviews/audit/ad-florum-1-27.packet.json").read_text())
        receipt = json.loads((book / "reviews/audit/ad-florum-1-27.review.json").read_text())
        self.assertEqual(validate_audit_receipt(packet, receipt), [])
        self.assertEqual([s["section"] for s in packet["sections"]], ["27"])
        self.assertEqual(packet["sections"][0]["locus"], "1.27")
        row = next(r for r in json.loads((book / "translations/ad_florum_1_english.json").read_text())
                   if r["section"] == 27)
        text = " ".join(row["english"])
        self.assertIn("just and holy' (Deuteronomy 32:4). And again:", text)
        self.assertIn("upon fairness' (Psalm 11:7; LXX Psalm 10:8). And again:", text)
        self.assertIn("judgments are fairness' (Psalm 119:172; LXX Psalm 118:172)", text)
        self.assertNotIn(" (Psalm 11:7;)", text)
        self.assertNotIn(" (Psalm 119:172;)", text)
        self.assertIn("no injustice", text)
        self.assertIn("except the Manichaeans", text)
        source = next(r for r in json.loads((book / "sources/ad_florum_1.json").read_text())
                      if r["section"] == 27)
        self.assertEqual(packet["sections"][0]["source_text"], source["julian"])
        self.assertNotIn(source["augustine"][0], " ".join(packet["sections"][0]["source_text"]))

    def test_malformed_content_cannot_be_stringified_into_valid_text(self):
        for bad in ([None], [{"text": "hidden"}], 42, {}):
            j = self.justification()
            j["source_text"] = bad
            self.assertTrue(check_record(j))
        j = self.justification()
        self.write(self.english, [{"id": "x", "confidence": "source_verified",
                                  "english": j["pass_b_english"]}])
        j["edition"] = "not an object"
        just_dir = self.root / "reviews/justifications"
        self.write(just_dir / "x.json", j)
        self.assertTrue(check_justifications(self.english, just_dir))
        rows = json.loads(self.source.read_text())
        rows[0]["latin"] = [None]
        self.write(self.english, [{"section": str(i), "english": ["A valid English sentence."]}
                                  for i in range(1, 9)])
        self.write(self.source, rows)
        with self.assertRaises(ValueError):
            self.packet()

    def test_codex_rows_and_single_row_source_file(self):
        codex_en = self.root / "codex_1_english.json"
        codex_src = self.root / "codex_1_source.json"
        self.write(codex_en, [{"codex": 1, "english": ["I read the discourse of Theodore."]}])
        self.write(codex_src, {"codex": 1, "greek": "Ἀνέγνων τὸν τοῦ Θεοδώρου λόγον."})
        packet = make_audit_packet(codex_en, codex_src, raw_sources=[self.raw],
                                   identity=self.identity, selected_sections=["1"])
        self.assertEqual([s["section"] for s in packet["sections"]], ["1"])
        self.assertEqual(packet["sections"][0]["source_text"],
                         ["Ἀνέγνων τὸν τοῦ Θεοδώρου λόγον."])
        self.assertEqual(validate_audit_receipt(packet, self.receipt(packet)), [])
        self.write(codex_src, {"codex": 1, "greek": "Different Greek."})
        self.assertTrue(validate_audit_receipt(packet, self.receipt(packet)))
        # A dict with no id-like key is still malformed, not a single row.
        self.write(codex_src, {"greek": "No codex key."})
        with self.assertRaises(ValueError):
            make_audit_packet(codex_en, codex_src, raw_sources=[self.raw],
                              identity=self.identity, selected_sections=["1"])

    def test_raw_witness_and_source_contamination_fail_closed(self):
        packet = make_audit_packet(self.english, self.source, identity=self.identity)
        self.assertTrue(packet["structural_errors"])
        rows = json.loads(self.source.read_text())
        rows[0]["latin"] = ["Profanus qui pro cibo temporary primatum spiritus vendit."]
        self.write(self.source, rows)
        packet = self.packet()
        self.assertTrue(any("operational" in e for e in packet["structural_errors"]))
        self.assertTrue(validate_audit_receipt(packet, self.receipt(packet)))


if __name__ == "__main__":
    unittest.main()
