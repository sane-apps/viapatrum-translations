#!/usr/bin/env python3
"""Tests for scripts/ocr_historical.py (hyphen cleanup + live Kraken OCR on 1636 Crocius scan)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ocr_historical as OH

CROCIUS_PDF = Path.home() / "SaneApps/clients/translations/books/crocius-syntagma/sources/slub_phys_cap2/phys_0304.pdf"


class TestOcrHistorical(unittest.TestCase):
    def test_clean_ocr_text_joins_early_modern_hyphens(self):
        raw = "sola scriptura ducuntur: il¬\nlustrantia vero, quibus ju-\nvamur, præsertim.\n"
        cleaned = OH.clean_ocr_text(raw, join_hyphens=True)
        self.assertIn("illustrantia", cleaned)
        self.assertIn("juvamur", cleaned)
        self.assertNotIn("¬", cleaned)

    def test_clean_ocr_text_preserves_hyphens_when_disabled(self):
        raw = "il¬\nlustrantia\n"
        self.assertIn("il¬\nlustrantia", OH.clean_ocr_text(raw, join_hyphens=False))

    def test_kraken_available_and_reads_1636_crocius(self):
        if not CROCIUS_PDF.is_file():
            self.skipTest("Crocius 1636 PDF not present on this host")
        self.assertIsNotNone(OH.find_kraken_bin(), "Kraken CLI should be found")
        self.assertIsNotNone(OH.find_kraken_model(), "CATMuS-Print model should be found")
        text, used = OH.ocr_file(CROCIUS_PDF, engine="auto", first=1, last=1)
        self.assertEqual(used, "kraken")
        self.assertIn("sola scriptura", text.lower())
        self.assertIn("juvamur", text.lower())
        self.assertIn("hæreseon", text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
