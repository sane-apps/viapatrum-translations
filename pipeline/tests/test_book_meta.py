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

    def test_keeps_inner_and_closing_quotes(self) -> None:
        with TemporaryDirectory() as tmp:
            (Path(tmp) / "book.yml").write_text(
                'title: "Fragment on \'Rejoice in that day\'"\n'
                "author: 'Josué de la Place'\n"
                "slug: x\n"
                "description: 'On \"The Lord created me\": created means appointed.'\n"
                'edition: "PG \\"39\\""\n',
                encoding="utf-8",
            )
            meta = load_book_meta(tmp)
            self.assertEqual(meta["title"], "Fragment on 'Rejoice in that day'")
            self.assertEqual(meta["description"], 'On "The Lord created me": created means appointed.')
            self.assertEqual(meta["edition"], 'PG "39"')

    def test_real_books_agree_with_yaml(self) -> None:
        """Every book.yml parses as YAML, and book_meta reads the same strings."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        root = Path(__file__).resolve().parents[2] / "books"
        for path in sorted(root.glob("*/book.yml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            meta = load_book_meta(path.parent)
            for key, value in data.items():
                if isinstance(value, str) and "\n" not in value:
                    self.assertEqual(meta.get(key), value, f"{path.parent.name}: {key}")

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
