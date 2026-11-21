#!/usr/bin/env python3
"""Known-answer tests: a book corrected after the pipeline applied it is never overwritten by the old
staged English (2026-11-20: 38 sections in 15 works, e.g. Basil Hexaemeron 21 and 43 of 11 Nov).

No network and no model call. Run: python3 scripts/test_book_edit.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _testenv  # noqa: E402,F401  finds llm_vendor_gate under any HOME
import citation_amendments as CA  # noqa: E402
import work_pipeline as W  # noqa: E402

SLUG = "test-work"
SRC = ["Ἐν ἀρχῇ ἐποίησεν ὁ θεός."]
OLD = ["Basil says that in the beginning God made it (Genesis 1:1)."]
NEW = ["In the beginning God made it (Genesis 1:1)."]
DRAFT = ["A newer staged draft, not yet applied (Genesis 1:1)."]


class BookEditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.books, self.stage = root / "books", root / "stage"
        for p in (mock.patch.object(W, "BOOKS", self.books), mock.patch.object(W, "STAGE", self.stage)):
            p.start()
            self.addCleanup(p.stop)
        (self.books / SLUG / "reviews" / "justifications").mkdir(parents=True)
        (self.stage / SLUG / "sections").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def staged(self, english, status="pass"):
        j = {"section": "1", "_status": status, "source_sha256": W.sha("\n".join(SRC)), "pass_b_english": english,
             "pass_a_gloss": "old gloss", "checks": {"checkers": ["a", "b"]}}
        (self.stage / SLUG / "sections" / "1.json").write_text(json.dumps(j))
        return j

    def receipt(self, english):
        rec = {"sections": [{"section": "1", "source_sha256": W.sha("\n".join(SRC)),
                             "english_sha256": W.sha("\n".join(english))}]}
        (self.books / SLUG / "reviews" / "work_receipt.json").write_text(json.dumps(rec))

    def sec(self, english):
        return {"id": "1", "source": SRC, "english": english}

    # book_edit ---------------------------------------------------------------------------------
    def test_never_applied_is_not_an_edit(self):
        j = self.staged(DRAFT)
        self.assertEqual(W.book_edit(SLUG, self.sec(OLD), j), "")

    def test_newer_staged_draft_is_not_an_edit(self):
        self.receipt(OLD)
        j = self.staged(DRAFT)
        self.assertEqual(W.book_edit(SLUG, self.sec(OLD), j), "")

    def test_same_english_is_not_an_edit(self):
        self.receipt(OLD)
        self.assertEqual(W.book_edit(SLUG, self.sec(OLD), self.staged(OLD)), "")

    def test_correction_after_apply_is_an_edit(self):
        self.receipt(OLD)
        self.assertEqual(W.book_edit(SLUG, self.sec(NEW), self.staged(OLD)), "edited")

    def test_held_section_is_not_reconciled(self):
        self.receipt(OLD)
        self.assertEqual(W.book_edit(SLUG, self.sec(NEW), self.staged(OLD, status="hold")), "")

    def test_proved_citation_fix_is_amended(self):
        self.receipt(OLD)
        fixed = ["Basil says that in the beginning God made it (Genesis 1:2)."]
        CA.record(self.books / SLUG, "1", OLD, fixed, tool="test", why="test")
        self.assertEqual(W.book_edit(SLUG, self.sec(fixed), self.staged(OLD)), "amended")

    # staged_sections (what apply and finish_ready read) ---------------------------------------
    def test_staged_sections_marks_correction_stale(self):
        self.receipt(OLD)
        self.staged(OLD)
        s = W.staged_sections(SLUG, [self.sec(NEW)])[0]
        self.assertEqual(s["_j"]["_status"], "stale")
        self.assertIn("corrected", s["_j"]["_why"])

    def test_staged_sections_carries_citation_fix(self):
        self.receipt(OLD)
        fixed = ["Basil says that in the beginning God made it (Genesis 1:2)."]
        CA.record(self.books / SLUG, "1", OLD, fixed, tool="test", why="test")
        self.staged(OLD)
        s = W.staged_sections(SLUG, [self.sec(fixed)])[0]
        self.assertEqual(s["_j"]["_status"], "pass")
        self.assertEqual(s["_j"]["pass_b_english"], fixed)

    def test_finish_ready_false_after_correction(self):
        self.receipt(OLD)
        self.staged(OLD)
        self.assertFalse(W.finish_ready(SLUG, [self.sec(NEW)]))

    # process_section ---------------------------------------------------------------------------
    def run_section(self, verdict):
        seen = {}

        def fake_check(slug, sec, j, brief, langname, jpath):
            seen["j"] = dict(j)
            out = {**j, **verdict}
            jpath.write_text(json.dumps(out))
            return out

        with mock.patch.object(W, "source_problems", return_value=[]), \
                mock.patch.object(W, "check_rounds", side_effect=fake_check), \
                mock.patch.object(W, "log", lambda *a, **k: None):
            out = W.process_section(SLUG, 0, [self.sec(NEW)], {}, "Greek")
        return seen, out

    def test_process_section_checks_the_corrected_english(self):
        self.receipt(OLD)
        self.staged(OLD)
        bj = {"section": "1", "pass_b_english": NEW, "pass_a_gloss": "new gloss"}
        (self.books / SLUG / "reviews" / "justifications" / "1.json").write_text(json.dumps(bj))
        seen, out = self.run_section({"_status": "pass", "checks": {"checkers": ["c", "d"]}})
        self.assertEqual(seen["j"]["pass_b_english"], NEW)
        self.assertEqual(seen["j"]["pass_a_gloss"], "new gloss")
        self.assertEqual(seen["j"]["_status"], "recheck")
        self.assertNotIn("checks", seen["j"])
        self.assertEqual(out["_status"], "pass")
        self.assertEqual(out["pass_b_english"], NEW)

    def test_process_section_no_verdict_keeps_file_and_blocks_apply(self):
        self.receipt(OLD)
        before = json.dumps(self.staged(OLD))
        _, out = self.run_section({"_status": "hold", "_why": "checker unavailable: plan budget",
                                   "check_history": [{}]})
        self.assertEqual((self.stage / SLUG / "sections" / "1.json").read_text(), before)
        self.assertEqual(out["_status"], "stale")
        self.assertEqual(W.staged_sections(SLUG, [self.sec(NEW)])[0]["_j"]["_status"], "stale")


if __name__ == "__main__":
    unittest.main(verbosity=1)
