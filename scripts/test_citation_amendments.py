#!/usr/bin/env python3
"""Known-answer tests for citation-only amendments (Nov 8, 2026). Run: python3 -m unittest scripts/test_citation_amendments.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_amendments as CA  # noqa: E402

BEFORE = ["John said no; he was called Elijah by the Lord (Luke 1:17).",
          "The law is a lamp (Ps 118:106); and 'Remember not our former iniquities' (Ps 103:12)."]
AFTER = ["John said no; he was called Elijah by the Lord (Matthew 11:14).",
         "The law is a lamp (Psalm 119:105); and 'Remember not our former iniquities' (Psalm 79:8)."]


class CitationOnly(unittest.TestCase):
    def test_placeholder_tags_count_as_references(self):
        self.assertTrue(CA.citation_only(["came to be' (prophetic allusion); therefore"], ["came to be' (Isaiah 43:10); therefore"]))
        self.assertTrue(CA.citation_only(["humbled.' (Isaiah 5:30 (cf.) And the"], ["humbled.' (Luke 14:11) And the"]))
        self.assertTrue(CA.citation_only(["me.' (Lamentations 1:16 (echo)) I take"], ["me.' (Jeremiah 15:7) I take"]))

    def test_dual_psalm_numbering_and_deuterocanon(self):
        self.assertTrue(CA.citation_only(["a support in the land (Ps 71:16a)."], ["a support in the land (Psalm 72:16; LXX 71:16a)."]))
        self.assertTrue(CA.citation_only(["'Put your feet into its feet' (Proverbs 4:26)."], ["'Put your feet into its feet' (Sirach 6:24)."]))
        self.assertTrue(CA.citation_only(["did not endure (Daniel 9:7)."], ["did not endure (Susanna 1:56)."]))

    def test_psalm_line_numbers(self):
        self.assertTrue(CA.citation_only(["the face of evil (Psalm 18:39.41). For"], ["the face of evil (Psalm 18:39-40). For"]))
        self.assertTrue(CA.citation_only(["the bad-minded (Psalm 49:10.12ab); and"], ["the bad-minded (Psalm 49:10-11); and"]))

    def test_slash_alternatives(self):
        self.assertTrue(CA.citation_only(["works the good' (cf. Rom 12:10/1 Pet 5:10), if"], ["works the good' (Romans 2:10), if"]))

    def test_ordinary_parenthesis_with_tag_word_is_text(self):
        self.assertFalse(CA.citation_only(["the echo (of a voice) came"], ["the echo came"]))
        self.assertFalse(CA.citation_only(["an echo (echo of Christ) here"], ["an echo here"]))

    def test_reference_swap_is_citation_only(self):
        self.assertTrue(CA.citation_only(BEFORE, AFTER))

    def test_reference_removal_is_citation_only(self):
        self.assertTrue(CA.citation_only(["He said it (Luke 1:17; cf. Matt 11:14)."], ["He said it."]))

    def test_word_change_is_not(self):
        self.assertFalse(CA.citation_only(BEFORE, [AFTER[0].replace("Lord", "angel"), AFTER[1]]))

    def test_non_reference_parenthesis_is_not(self):
        self.assertFalse(CA.citation_only(["He came (as he said) at once."], ["He came at once."]))

    def test_lemma_heading_reference(self):
        self.assertTrue(CA.citation_only(["Ps 9:18–19: 'Let the sinners be turned away.'"],
                                         ["Psalm 9:17: 'Let the sinners be turned away.'"]))
        self.assertTrue(CA.citation_only(["Regarding Psalm 104:12a, 'brief' instead of 'few.'"],
                                         ["Regarding Psalm 105:12, 'brief' instead of 'few.'"]))

    def test_book_name_in_prose_is_not_a_reference(self):
        self.assertFalse(CA.citation_only(["As John says in his Gospel."], ["As Mark says in his Gospel."]))

    def test_multi_ref_paren(self):
        self.assertTrue(CA.citation_only(["Words (Isaiah 43:26; Luke 6:28) here."], ["Words (Isaiah 66:5) here."]))


class Chain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.book = Path(self.tmp.name) / "bk"
        (self.book / "reviews").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def h(self, paras):
        return CA.sha("\n".join(paras))

    def test_recorded_chain_certifies(self):
        CA.record(self.book, "1", BEFORE, AFTER, tool="t", why="w")
        rows = CA.load(self.book)
        self.assertTrue(CA.chain_ok(rows, "1", self.h(BEFORE), self.h(AFTER)))

    def test_two_step_chain(self):
        mid = [BEFORE[0].replace("Luke 1:17", "Matthew 11:14"), BEFORE[1]]
        CA.record(self.book, "1", BEFORE, mid, tool="t", why="w")
        CA.record(self.book, "1", mid, AFTER, tool="t", why="w")
        self.assertTrue(CA.chain_ok(CA.load(self.book), "1", self.h(BEFORE), self.h(AFTER)))

    def test_record_refuses_text_change(self):
        with self.assertRaises(ValueError):
            CA.record(self.book, "1", BEFORE, ["Changed words."], tool="t", why="w")

    def test_tampered_row_fails(self):
        CA.record(self.book, "1", BEFORE, AFTER, tool="t", why="w")
        path = self.book / "reviews" / CA.FILE
        row = json.loads(path.read_text())
        row["after"] = ["John said yes."] + AFTER[1:]
        row["after_sha256"] = self.h(row["after"])
        path.write_text(json.dumps(row) + "\n")
        self.assertFalse(CA.chain_ok(CA.load(self.book), "1", self.h(BEFORE), row["after_sha256"]))

    def test_other_section_or_wrong_start_fails(self):
        CA.record(self.book, "2", BEFORE, AFTER, tool="t", why="w")
        self.assertFalse(CA.chain_ok(CA.load(self.book), "1", self.h(BEFORE), self.h(AFTER)))
        self.assertFalse(CA.chain_ok(CA.load(self.book), "2", CA.sha("other"), self.h(AFTER)))

    def test_no_change_needs_no_rows(self):
        self.assertTrue(CA.chain_ok([], "1", "abc", "abc"))


class DuplicateSections(unittest.TestCase):
    PAIRS = [{"id": "u01-open", "source": ["Title. First half of the homily.", "Second half."]}]

    def test_contained_section_may_go(self):
        rows = [{"kind": CA.REMOVE, "section": "u01-rem-mid", "contained_in": "u01-open", "source": ["First half of the homily."]}]
        self.assertTrue(CA.removal_ok(rows, {"u01-rem-mid"}, self.PAIRS))

    def test_unrecorded_or_new_text_may_not(self):
        self.assertFalse(CA.removal_ok([], {"u01-rem-mid"}, self.PAIRS))
        rows = [{"kind": CA.REMOVE, "section": "u01-rem-mid", "contained_in": "u01-open", "source": ["Text found nowhere else."]}]
        self.assertFalse(CA.removal_ok(rows, {"u01-rem-mid"}, self.PAIRS))
        rows = [{"kind": CA.REMOVE, "section": "u01-rem-mid", "contained_in": "u09", "source": ["Second half."]}]
        self.assertFalse(CA.removal_ok(rows, {"u01-rem-mid"}, self.PAIRS))

    def test_record_refuses_uncontained(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                CA.record_removal(Path(t), "x", ["Other text."], [], "u01-open", ["Title."], tool="t", why="w")


if __name__ == "__main__":
    unittest.main()
