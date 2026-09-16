#!/usr/bin/env python3
"""Unit tests for pipeline.book_meta (single source of book identity)."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pipeline.book_meta import load_book_meta


class BookMetaTest(unittest.TestCase):
    def test_loads_flat_yml(self) -> None:
        with TemporaryDirectory() as tmp:
            (Path(tmp) / "book.yml").write_text(
                'title: "Philosophia theologiae ancillans (tip)"\n'
                'author: "Robert Baron"\n'
                'slug: "baron-philosophia-theologiae-ancillans"\n',
                encoding="utf-8",
            )
            meta = load_book_meta(tmp)
            self.assertEqual(meta["author"], "Robert Baron")
            self.assertIn("Philosophia", meta["title"])

    def test_missing_key_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            (Path(tmp) / "book.yml").write_text('title: "X"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_book_meta(tmp)

    def test_real_books_parse(self) -> None:
        root = Path(__file__).resolve().parents[2] / "books"
        n = 0
        for yml in sorted(root.glob("*/book.yml")):
            meta = load_book_meta(yml.parent)
            self.assertTrue(meta["title"] and meta["author"])
            n += 1
        self.assertGreater(n, 100)


if __name__ == "__main__":
    unittest.main()
