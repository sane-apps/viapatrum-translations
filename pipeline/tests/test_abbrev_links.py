"""Explicit Bible abbreviations become Logos links. Bare allusions do not."""
from __future__ import annotations

import unittest

from pipeline.bible_links import BibleLinker


class AbbrevLinkTest(unittest.TestCase):
    def test_numbered_epistle_abbreviation_links(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text(
            "you are joined to us in the Lord (1 Cor 1:10).", key="k", label="L"
        )
        self.assertIn(">> Bible:1 Corinthians 1:10", out)
        self.assertIn("1 Cor 1:10", out)
        self.assertEqual(len(linker.link_receipts), 1)

    def test_period_and_psalm_and_matthew(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("See Matt. 5:3 and Ps. 50:1.", key="k", label="L")
        self.assertIn(">> Bible:Matthew 5:3", out)
        self.assertIn(">> Bible:Psalm 50:1", out)
        self.assertEqual(len(linker.link_receipts), 2)

    def test_full_name_is_not_linked_twice(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("as it is written (1 Corinthians 1:10).", key="k", label="L")
        self.assertEqual(out.count(">> Bible:"), 1)
        self.assertIn(">> Bible:1 Corinthians 1:10", out)

    def test_words_after_a_citation_do_not_block_it(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("See Matt. 5:3 and then Rom 8:28.", key="k", label="L")
        self.assertIn(">> Bible:Matthew 5:3", out)
        self.assertIn(">> Bible:Romans 8:28", out)
        self.assertEqual(len(linker.link_receipts), 2)

    def test_second_book_after_a_semicolon_stays_its_own_link(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("See 1 Cor 1:10; 2 Cor 5:1.", key="k", label="L")
        self.assertIn(">> Bible:1 Corinthians 1:10", out)
        self.assertIn(">> Bible:2 Corinthians 5:1", out)
        self.assertNotIn("Bible:1 Corinthians 1:10; 2", out)
        self.assertEqual(len(linker.link_receipts), 2)

    def test_range_and_exodus_abbreviation(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("Paul says (1 Cor 15:1-2) what the bush said (Exod 3:2).", key="k", label="L")
        self.assertIn(">> Bible:1 Corinthians 15:1-2", out)
        self.assertIn(">> Bible:Exodus 3:2", out)
        kor = BibleLinker()
        self.assertIn(
            ">> Bible:1 Corinthians 16:10",
            kor.bible_text("so that Timothy may dare to come (1 Kor 16:10-11).", key="k", label="L"),
        )

    def test_bare_allusion_and_lxx_abbreviation_stay_plain(self) -> None:
        linker = BibleLinker()
        plain = linker.bible_text("the Apostle says the Lord is near.", key="k", label="L")
        self.assertEqual(plain, "the Apostle says the Lord is near.")
        self.assertEqual(linker.link_receipts, [])
        lxx = linker.bible_text("as the Greek has it (LXX Ps 50:1).", key="k", label="L")
        self.assertNotIn(">> Bible:", lxx)

    def test_note_caption_still_does_not_link_an_abbreviation(self) -> None:
        linker = BibleLinker()
        line = "Possible allusion: 1 Cor 1:10"
        out = linker.bible_text(line, key="k", label="L", note=True)
        self.assertEqual(out, line)
        self.assertEqual(linker.link_receipts, [])


if __name__ == "__main__":
    unittest.main()
