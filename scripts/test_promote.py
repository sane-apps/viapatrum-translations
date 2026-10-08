#!/usr/bin/env python3
"""One promotion point: a book that certifies is committed with exactly the
files apply() wrote; nothing else in the tree is swept in; a commit problem
never fails the certification. Offline, in temp git repos.
Run: python3 -m unittest scripts/test_promote.py  (from the repo root)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import promote as P  # noqa: E402
import work_pipeline as W  # noqa: E402


def sh(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def make_repo(root: Path) -> None:
    sh(root, "init", "-q", "-b", "main")
    sh(root, "config", "user.name", "t")
    sh(root, "config", "user.email", "t@t")
    (root / "books" / "bk" / "translations").mkdir(parents=True)
    (root / "books" / "bk" / "translations" / "a_english.json").write_text("[]\n")
    (root / "books" / "bk" / "book.yml").write_text("title: x\n")
    (root / "books" / "other").mkdir(parents=True)
    (root / "books" / "other" / "book.yml").write_text("title: y\n")
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", "init")


class CommitBookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_repo(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_commits_only_the_named_files(self):
        b = self.root / "books" / "bk"
        (b / "translations" / "a_english.json").write_text('[{"english": ["new"]}]\n')
        (b / "reviews" / "justifications").mkdir(parents=True)
        (b / "reviews" / "justifications" / "1.json").write_text("{}\n")
        (b / "book.yml").write_text("title: half-edited by hand\n")         # not written by apply
        (self.root / "books" / "other" / "book.yml").write_text("title: z\n")  # another book
        sh(self.root, "add", "books/other/book.yml")                          # even when staged
        ok, msg = P.commit_book("bk", [b / "translations" / "a_english.json",
                                       b / "reviews" / "justifications" / "1.json"], "Certify bk", root=self.root)
        self.assertTrue(ok, msg)
        files = sh(self.root, "show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(sorted(files), ["books/bk/reviews/justifications/1.json", "books/bk/translations/a_english.json"])
        dirty = sh(self.root, "status", "--porcelain")
        self.assertIn(" M books/bk/book.yml", dirty)
        self.assertIn("M  books/other/book.yml", dirty, "a staged change elsewhere stays staged, not committed")

    def test_refuses_a_path_outside_the_book(self):
        ok, msg = P.commit_book("bk", [self.root / "books" / "other" / "book.yml"], "x", root=self.root)
        self.assertFalse(ok)
        self.assertIn("outside books/bk/", msg)

    def test_no_change_is_ok(self):
        ok, msg = P.commit_book("bk", [self.root / "books" / "bk" / "book.yml"], "x", root=self.root)
        self.assertTrue(ok)
        self.assertIn("no change", msg)

    def test_not_on_main_is_left_uncommitted(self):
        sh(self.root, "checkout", "-q", "-b", "side")
        (self.root / "books" / "bk" / "book.yml").write_text("title: q\n")
        ok, msg = P.commit_book("bk", [self.root / "books" / "bk" / "book.yml"], "x", root=self.root)
        self.assertFalse(ok)
        self.assertIn("not main", msg)

    def test_dirty_books_lists_untracked_and_modified(self):
        (self.root / "books" / "bk" / "book.yml").write_text("title: q\n")
        (self.root / "books" / "new").mkdir()
        (self.root / "books" / "new" / "x.json").write_text("{}")
        self.assertEqual(P.dirty_books(self.root), {"bk": ["books/bk/book.yml"], "new": ["books/new/x.json"]})


class ApplyPromotesTests(unittest.TestCase):
    """work_pipeline.apply() commits a certified book in its own repo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sh(self.root, "init", "-q", "-b", "main")
        sh(self.root, "config", "user.name", "t")
        sh(self.root, "config", "user.email", "t@t")
        self.books, self.stage = self.root / "books", self.root / "stage"
        tr = self.books / "bk" / "translations"
        tr.mkdir(parents=True)
        (tr / "w_english.json").write_text(json.dumps([{"section": "1", "title": "t", "english": ["old"]}]))
        (tr / "w_source.json").write_text(json.dumps([{"section": "1", "latin": ["Prima pars."]}]))
        (self.books / "bk" / "notes.txt").write_text("hand notes\n")
        sh(self.root, "add", "-A")
        sh(self.root, "commit", "-q", "-m", "init")
        (self.books / "bk" / "notes.txt").write_text("hand notes, edited\n")
        secdir = self.stage / "bk" / "sections"
        secdir.mkdir(parents=True)
        (secdir / "1.json").write_text(json.dumps({"section": "1", "_status": "pass",
                                                   "pass_b_english": ["New."], "thought_title": "T"}))
        (self.stage / "bk" / "brief.json").write_text(json.dumps({"title_en": "T"}))
        (self.stage / "bk" / "intro.json").write_text(json.dumps({"paragraphs": ["a", "b", "c"]}))
        self.patches = [mock.patch.object(W, "BOOKS", self.books), mock.patch.object(W, "STAGE", self.stage),
                        mock.patch.object(W, "log")]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def apply(self):
        st = {"sections": {"pass": 1}, "intro_ok": True, "followability": [4, 4]}
        with mock.patch.object(W, "status", return_value=st), mock.patch.object(W, "intro_problems", return_value=[]), \
                mock.patch("builtins.print"):
            return W.apply("bk")

    def test_certified_book_is_committed_without_hand_edits(self):
        self.assertEqual(self.apply(), 0)
        self.assertTrue(W.certified("bk"))
        files = sh(self.root, "show", "--name-only", "--format=", "HEAD").split()
        self.assertIn("books/bk/translations/w_english.json", files)
        self.assertIn("books/bk/reviews/work_receipt.json", files)
        self.assertIn("books/bk/intro.md", files)
        self.assertNotIn("books/bk/notes.txt", files)
        self.assertEqual(sh(self.root, "log", "-1", "--format=%s"), "Certify bk (work_pipeline apply)\n")
        self.assertEqual(sh(self.root, "status", "--porcelain", "--", "books").split(), ["M", "books/bk/notes.txt"])
        W.log.assert_any_call("bk", mock.ANY)

    def test_commit_failure_keeps_the_certification(self):
        sh(self.root, "checkout", "-q", "-b", "side")
        self.assertEqual(self.apply(), 0)
        self.assertTrue(W.certified("bk"))
        self.assertEqual(sh(self.root, "log", "--format=%s"), "init\n")
        msgs = " ".join(str(c.args[1]) for c in W.log.call_args_list)
        self.assertIn("promote: not committed: on refs/heads/side", msgs)

    def test_uncertified_apply_is_not_committed(self):
        with mock.patch.object(W, "certified", return_value=False):
            self.assertEqual(self.apply(), 0)
        self.assertEqual(sh(self.root, "log", "--format=%s"), "init\n")


if __name__ == "__main__":
    unittest.main()
