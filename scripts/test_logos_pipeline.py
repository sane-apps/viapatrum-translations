#!/usr/bin/env python3
"""Logos pipeline regressions from the 2026-10-06 red team (package P10). Offline.

- worksheet notes never reach a Word file, and every gate refuses one that has them
- a Word file is rebuilt when its English or the note filter is newer, even shorter
- intro.md goes into the Word file
- the Logos row is keyed by resource id, and a shared title still opens the right book
- the Logos description links to the work page when it is published
"""
import json
import os
import sqlite3
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import build_logos_pack  # noqa: E402
import build_pbb_docx as B  # noqa: E402
import logos_build as L  # noqa: E402
import pb_sync  # noqa: E402
from pipeline.verify_docx import docx_text, verify_docx, worksheet_hits  # noqa: E402

SHOP = "True OET; Pass A ≠ Pass B. Melito skipped; never Cyril Matthew densify."
INTRO = ("Fixture Author (c. 300) wrote this test homily.\n\n"
         "It was preached at Easter.\n\n"
         "A reader will meet one quotation of John.")


def write_book(root: Path, slug: str, english: list[str], notes: list[str]) -> Path:
    book = root / "books" / slug
    (book / "translations").mkdir(parents=True, exist_ok=True)
    (book / "book.yml").write_text(
        f"slug: {slug}\n"
        "title: \"Fragment on 'Rejoice in that day'\"\n"
        "author: Fixture Author\n"
        f'docx: "{slug}.docx"\n'
        "notes: |\n  True OET; Pass A ≠ Pass B.\n",
        encoding="utf-8")
    (book / "intro.md").write_text(INTRO, encoding="utf-8")
    (book / "translations" / "fx_u01_source.json").write_text(
        json.dumps([{"section": "u01", "head": "Opening"}]), encoding="utf-8")
    (book / "translations" / "fx_u01_english.json").write_text(json.dumps([{
        "section": "u01", "title": "The spring of the newly baptized",
        "english": english, "translator_notes": notes,
    }]), encoding="utf-8")
    return book


def plain(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        return docx_text(zf.read("word/document.xml").decode("utf-8"))


class WorksheetGate(unittest.TestCase):
    def test_marks_found_and_ordinary_english_passes(self):
        self.assertEqual(worksheet_hits(SHOP)[:3], ["True OET", "Pass A ≠", "Pass B"])
        for clean in ("He will pass away.", "to pass a law", "They surpass all.",
                      "Pass on the bread.", "Copy-text PG 39 (Greek)"):
            self.assertEqual(worksheet_hits(clean), [], clean)

    def test_reader_note_drops_shop_talk_keeps_reader_note(self):
        self.assertEqual(B._reader_note(SHOP), "")
        self.assertEqual(B._reader_note("Pass A was a summary; not globbed."), "")
        self.assertEqual(B._reader_note("The Greek word also means light."),
                         "The Greek word also means light.")

    def test_verify_refuses_notes_split_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.docx"
            xml = ('<w:document xmlns:w="u"><w:body>'
                   '<w:p><w:r><w:t>[[@Headword:A]]</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t>[[John 3:16 &gt;&gt; Bible:John 3:16]]</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t xml:space="preserve">True </w:t></w:r>'
                   '<w:r><w:t>OET; Pass A.</w:t></w:r></w:p>'
                   '</w:body></w:document>')
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("word/document.xml", xml)
            errs = verify_docx(path)
            self.assertTrue(any("worksheet note" in e for e in errs), errs)


class FixtureBuild(unittest.TestCase):
    """Build a fixture book end to end with the real builder."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        patcher = mock.patch.object(B, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_build_has_intro_reader_note_and_no_worksheet(self):
        book = write_book(self.root, "fx", [
            "When the season of spring succeeds the gloom of winter, as John 3:16 says, God loved the world."],
            [SHOP, "Copy-text: PG 39 (Khazarzar). PD.", "The Greek word also means light."])
        out = book / "fx.docx"
        receipt = B.build_docx("fx", out, None)
        text = plain(out)
        self.assertEqual(verify_docx(out), [])
        self.assertEqual(worksheet_hits(text), [])
        self.assertIn("\nIntroduction\n", text)
        self.assertIn("It was preached at Easter.", text)
        self.assertIn("The Greek word also means light.", text)
        self.assertEqual(receipt["tn_notes"], 1)
        # The closing quote of the title survives (book_meta fix).
        self.assertTrue(text.startswith("Fragment on 'Rejoice in that day'\n"), text[:60])
        self.assertEqual(B._docx_stamp(out), B.NOTE_FILTER_STAMP)
        self.assertEqual(B.rebuild_reason(book, out), "")

    def test_rebuild_reasons_and_shorter_rebuild(self):
        long_para = "As John 3:16 says, God loved the world. " + "Spring follows winter. " * 450
        book = write_book(self.root, "fx", [long_para], [])
        out = book / "fx.docx"
        B.build_docx("fx", out, None)
        self.assertGreater(B._docx_chars(out), 8000)
        # Newer English, and shorter than half the old file.
        old = time.time() - 100
        os.utime(out, (old, old))
        write_book(self.root, "fx", ["As John 3:16 says, God loved the world."], [])
        self.assertIn("English newer", B.rebuild_reason(book, out))
        with self.assertRaises(SystemExit):
            B.build_docx("fx", out, None)  # the guard still holds by default
        B.build_docx("fx", out, None, allow_shrink=True)
        self.assertLess(B._docx_chars(out), 2000)
        self.assertEqual(B.rebuild_reason(book, out), "")
        # A file made before the current note filter is out of date.
        with mock.patch.object(B, "NOTE_FILTER_STAMP", "pbb-notes-newer"):
            self.assertEqual(B.rebuild_reason(book, out), "built before the current note filter")

    def test_catchup_rebuilds_stale_certified_book(self):
        book = write_book(self.root, "fx", ["As John 3:16 says, God loved the world."], [])
        out = book / "fx.docx"
        B.build_docx("fx", out, None)
        old, edited = time.time() - 100, time.time() - 50
        os.utime(out, (old, old))
        os.utime(book / "intro.md", (edited, edited))
        queue = self.root / "outputs" / "work-pipeline"
        queue.mkdir(parents=True)
        (queue / "queue.json").write_text(json.dumps({"fx": {"result": "certified"}}))
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "check_research.py").write_text(
            "ERRORS = []\n", encoding="utf-8")
        self.assertEqual(B.catchup(dry_run=True), 0)
        self.assertEqual(out.stat().st_mtime, old)  # dry run wrote nothing
        self.assertEqual(B.catchup(), 0)
        self.assertGreater(out.stat().st_mtime, edited)
        self.assertEqual(B.rebuild_reason(book, out), "")
        report = json.loads((self.root / "outputs/logos-catchup/latest.json").read_text())
        self.assertEqual([r["slug"] for r in report["rebuilt"]], ["fx"])


class LogosRows(unittest.TestCase):
    TITLES = ["Fragments on John", "Fragments on John", "Fragments on Romans",
              "Fragments", "On the Newly Baptized", "On the Newly Enlightened Ones"]

    def test_unique_needle_goes_below_five_words(self):
        others = [t for t in self.TITLES if t != "On the Newly Baptized"]
        self.assertEqual(L.unique_needle("On the Newly Baptized", others), "On the Newly Baptized")
        self.assertEqual(L.unique_needle("Octavius", self.TITLES), "Octavius")
        # A shared title has no unique prefix: the whole title comes back, and
        # "Fragments" never matches "Fragments on John" as a whole-word needle.
        self.assertEqual(L.unique_needle("Fragments on John", self.TITLES[1:]), "Fragments on John")
        self.assertTrue(L.title_has("Fragments on\nJohn", "Fragments on John"))
        self.assertFalse(L.title_has("Fragments on Johnathan", "Fragments on John"))

    def test_shared_title_opens_the_right_book(self):
        rows = [(10, 100, "ammonius.docx"), (10, 140, "didymus.docx")]
        state = {"open": "", "clicks": []}

        def fake_run(cmd, timeout=120):
            if cmd and cmd[0] == L.CLICLICK and cmd[1].startswith("c:"):
                x, y = (int(v) for v in cmd[1][2:].split(","))
                state["clicks"].append(y)
                for _rx, ry, docx in rows:
                    if ry <= y <= ry + 20:
                        state["open"] = docx
            return 0, ""

        fakes = {
            "run": fake_run,
            "scroll_geom": lambda: (50, 50, 400, 60),
            "drag_thumb": lambda a, b: True,
            "list_quiet": lambda timeout=45: True,
            "ax_texts": lambda: [(1, "Fragments on John")],
            "find_title_hits": lambda needle: [(x, y) for x, y, _d in rows],
            "scroll_area_count": lambda: 3 if state["open"] else 2,
            "body_file": lambda: state["open"],
            "click_edit_if_present": lambda: False,
            "log": lambda msg: None,
        }
        with mock.patch.multiple(L, **fakes), mock.patch.object(L.time, "sleep", lambda s: None):
            opened, matched = L.open_edit("Fragments on John", "didymus.docx",
                                          ["Fragments on John", "Fragments on Romans"])
        self.assertEqual((opened, matched), (True, True))
        self.assertEqual(state["open"], "didymus.docx")
        self.assertEqual(state["clicks"], [110, 150])  # first row was the other book

    def test_inventory_keys_by_resource_id_not_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            db = repo / "pb.db"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE Books (Id INTEGER PRIMARY KEY, ResourceId TEXT, Title TEXT,"
                        " Authors TEXT, LastCompiled TEXT, IsDeleted INT)")
            con.executemany("INSERT INTO Books VALUES (?,?,?,?,?,0)", [
                (1, "PBB:aaa", "Fragments on John", "Ammonius", "2026-10-01T00:00:00"),
                (2, "PBB:bbb", "Fragments on John", "Didymus", None),
                (3, "PBB:ccc", "On the Imputation of Adam's First Sin", "Placeus", "2026-10-02T00:00:00"),
            ])
            con.commit()
            con.close()
            books = [("ammonius-fj", '"Fragments on John"', "Ammonius", 'resource_id: "PBB:aaa"\n'),
                     ("didymus-fj", '"Fragments on John"', "Didymus", ""),
                     ("placeus", "'On the Imputation of Adam''s First Sin'", "Placeus",
                      'resource_id: "PBB:ccc"\n')]
            for slug, title, author, rid in books:
                d = repo / "books" / slug
                d.mkdir(parents=True)
                (d / f"{slug}.docx").write_bytes(b"x")
                (d / "book.yml").write_text(f"title: {title}\nauthor: {author}\n"
                                            f'docx: "{slug}.docx"\n{rid}', encoding="utf-8")
            with mock.patch.object(L, "REPO", str(repo)), \
                    mock.patch.object(L, "resolve_pb_db", lambda: str(db)):
                inv = L.inventory()
        self.assertEqual(inv["ammonius-fj"]["bid"], 1)
        self.assertEqual(inv["didymus-fj"]["bid"], 2)  # title and author, not title alone
        self.assertEqual(inv["placeus"]["bid"], 3)
        self.assertIsNone(inv["didymus-fj"]["last_compiled"])


class Descriptions(unittest.TestCase):
    def test_work_url_only_when_published(self):
        self.assertEqual(
            pb_sync.with_work_url("Amphilochius, On the Newly Baptized.", "amph", {"amph"}),
            "Amphilochius, On the Newly Baptized. The same English is free to read at "
            "https://viapatrum.org/works/amph/")
        self.assertEqual(pb_sync.with_work_url("D.", "unpublished", {"amph"}), "D.")
        self.assertEqual(pb_sync.with_work_url("D.", "amph", None), "D.")
        once = pb_sync.with_work_url("D.", "amph", {"amph"})
        self.assertEqual(pb_sync.with_work_url(once, "amph", {"amph"}), once)

    def test_pb_sync_adds_no_row_for_a_failing_word_file(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(B, "ROOT", Path(tmp)):
            root = Path(tmp)
            good = write_book(root, "good", ["As John 3:16 says, God loved the world."], [])
            B.build_docx("good", good / "good.docx", None)
            bad = write_book(root, "bad", ["As John 3:16 says, God loved the world."], [])
            xml = ('<w:document xmlns:w="u"><w:body><w:p><w:r><w:t>[[@Headword:A]]</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t>[[John 3:16 &gt;&gt; Bible:John 3:16]] True OET.</w:t></w:r></w:p>'
                   '</w:body></w:document>')
            with zipfile.ZipFile(bad / "bad.docx", "w") as zf:
                zf.writestr("word/document.xml", xml)
            db = root / "home/Library/Application Support/Logos4/Documents/p/PersonalBooks"
            db.mkdir(parents=True)
            sqlite3.connect(db / "PersonalBookManager.db").execute(
                "CREATE TABLE Books (Id INTEGER PRIMARY KEY, ResourceId TEXT, Title TEXT,"
                " Authors TEXT, Description TEXT, IsDeleted INT)").connection.commit()
            out = []
            with mock.patch.object(pb_sync, "REPO", str(root)), \
                    mock.patch.dict(os.environ, {"HOME": str(root / "home")}), \
                    mock.patch.object(sys, "argv", ["pb_sync.py"]), \
                    mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(map(str, a)))):
                pb_sync.main()
        lines = "\n".join(out)
        self.assertIn("good: INSERT new row", lines)
        self.assertIn("bad: SKIP (Word file held", lines)

    def test_pack_refuses_worksheet_and_missing_intro(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(B, "ROOT", Path(tmp)):
            book = write_book(Path(tmp), "fx", ["As John 3:16 says, God loved the world."], [])
            out = book / "fx.docx"
            B.build_docx("fx", out, None)
            self.assertEqual(build_logos_pack.word_file_problems(book, out), [])
            yml = (book / "book.yml").read_text()
            (book / "book.yml").write_text(yml + "logos_intro: false\n", encoding="utf-8")
            B.build_docx("fx", out, None)
            # An explicit opt-out is honoured by the one shared rule.
            self.assertEqual(build_logos_pack.word_file_problems(book, out), [])
            (book / "book.yml").write_text(yml, encoding="utf-8")
            self.assertIn("Word file leaves out intro.md",
                          build_logos_pack.word_file_problems(book, out))
            self.assertIn("leaves out intro.md", B.rebuild_reason(book, out))


def stale_and_introless(root: Path) -> None:
    """Three built books: good (current), stale (older than its English),
    nointro (intro.md exists, the Word file has no Introduction)."""
    for slug in ("good", "stale", "nointro"):
        book = write_book(root, slug, ["As John 3:16 says, God loved the world."], [])
        yml = (book / "book.yml").read_text()
        if slug == "nointro":
            (book / "book.yml").write_text(yml + "logos_intro: false\n", encoding="utf-8")
        B.build_docx(slug, book / f"{slug}.docx", None)
        (book / "book.yml").write_text(yml, encoding="utf-8")
    old = time.time() - 100
    os.utime(root / "books/stale/stale.docx", (old, old))


class OneRuleEverywhere(unittest.TestCase):
    """The driver, pb_sync and the pack refuse the same out-of-date files."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        patcher = mock.patch.object(B, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        stale_and_introless(self.root)

    def test_driver_dry_run_holds_stale_and_introless(self):
        db = self.root / "pb.db"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE Books (Id INTEGER PRIMARY KEY, ResourceId TEXT, Title TEXT,"
                    " Authors TEXT, LastCompiled TEXT, IsDeleted INT)")
        con.commit()
        con.close()
        out = []
        with mock.patch.object(L, "REPO", str(self.root)), \
                mock.patch.object(L, "resolve_pb_db", lambda: str(db)), \
                mock.patch.object(L, "LOCK_PATH", str(self.root / "no.lock")), \
                mock.patch.object(L, "load_uploads", lambda: {}), \
                mock.patch.object(L, "run", lambda cmd, timeout=120: (0, "research ok")), \
                mock.patch.object(sys, "argv", ["logos_build.py", "--dry-run"]), \
                mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(map(str, a)))):
            L.main()
        lines = {ln.split(":", 1)[0]: ln.split(":", 1)[1].split() for ln in out
                 if ln.split(":", 1)[0] in ("NEED_BUILD", "HELD")}
        self.assertEqual(lines["NEED_BUILD"], ["good"])
        self.assertEqual(lines["HELD"], ["nointro", "stale"])
        self.assertFalse((self.root / "no.lock").exists())

    def test_pb_sync_inserts_no_row_for_stale_or_introless(self):
        db = self.root / "home/Library/Application Support/Logos4/Documents/p/PersonalBooks"
        db.mkdir(parents=True)
        sqlite3.connect(db / "PersonalBookManager.db").execute(
            "CREATE TABLE Books (Id INTEGER PRIMARY KEY, ResourceId TEXT, Title TEXT,"
            " Authors TEXT, Description TEXT, IsDeleted INT)").connection.commit()
        out = []
        with mock.patch.object(pb_sync, "REPO", str(self.root)), \
                mock.patch.dict(os.environ, {"HOME": str(self.root / "home")}), \
                mock.patch.object(sys, "argv", ["pb_sync.py"]), \
                mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(map(str, a)))):
            pb_sync.main()
        lines = "\n".join(out)
        self.assertIn("good: INSERT new row", lines)
        self.assertIn("stale: SKIP (Word file held: English newer", lines)
        self.assertIn("nointro: SKIP (Word file held: Word file leaves out intro.md", lines)

    def test_pack_and_catchup_agree(self):
        for slug, want in (("good", ""), ("stale", "English newer"),
                           ("nointro", "leaves out intro.md")):
            book = self.root / "books" / slug
            docx = book / f"{slug}.docx"
            problems = "; ".join(build_logos_pack.word_file_problems(book, docx))
            reason = B.rebuild_reason(book, docx)
            if want:
                self.assertIn(want, problems)
                self.assertIn(want, reason)
            else:
                self.assertEqual((problems, reason), ("", ""))


class LostClick(unittest.TestCase):
    def test_lost_click_after_wrong_book_is_retried(self):
        """Row 0 opens the other book with the same title; the first click on
        row 1 is lost, so the wrong edit view is still open. That is a miss,
        not "other": the row is clicked again and opens the right book."""
        rows = [(10, 100, "ammonius.docx"), (10, 140, "didymus.docx")]
        state = {"open": "", "clicks": [], "drop": 1}

        def fake_run(cmd, timeout=120):
            if cmd and cmd[0] == L.CLICLICK and cmd[1].startswith("c:"):
                _x, y = (int(v) for v in cmd[1][2:].split(","))
                state["clicks"].append(y)
                for _rx, ry, docx in rows:
                    if ry <= y <= ry + 20:
                        if docx == "didymus.docx" and state["drop"]:
                            state["drop"] -= 1  # the list ate this click
                        else:
                            state["open"] = docx
            return 0, ""

        fakes = {
            "run": fake_run,
            "scroll_geom": lambda: (50, 50, 400, 60),
            "drag_thumb": lambda a, b: True,
            "list_quiet": lambda timeout=45: True,
            "ax_texts": lambda: [(1, "Fragments on John")],
            "find_title_hits": lambda needle: [(x, y) for x, y, _d in rows],
            "scroll_area_count": lambda: 3 if state["open"] else 2,
            "body_file": lambda: state["open"],
            "click_edit_if_present": lambda: False,
            "log": lambda msg: None,
        }
        with mock.patch.multiple(L, **fakes), mock.patch.object(L.time, "sleep", lambda s: None):
            self.assertEqual(L.click_row(10, 140, 1, "Fragments on John", "didymus.docx",
                                         50, 400, "test"), "open")
            state.update(open="", clicks=[], drop=1)
            opened, matched = L.open_edit("Fragments on John", "didymus.docx",
                                          ["Fragments on John", "Fragments on Romans"])
        self.assertEqual((opened, matched), (True, True))
        self.assertEqual(state["open"], "didymus.docx")
        self.assertEqual(state["clicks"], [110, 150, 150])


class CatalogueMissing(unittest.TestCase):
    def test_missing_catalogue_keeps_existing_link(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(B, "ROOT", Path(tmp)):
            root = Path(tmp)
            book = write_book(root, "amph", ["As John 3:16 says, God loved the world."], [])
            with open(book / "book.yml", "a", encoding="utf-8") as f:
                f.write('description: "Amphilochius, On the Newly Baptized."\n'
                        'resource_id: "PBB:aaa"\n')
            B.build_docx("amph", book / "amph.docx", None)
            linked = ("Amphilochius, On the Newly Baptized. The same English is free "
                      "to read at https://viapatrum.org/works/amph/")
            dbdir = root / "home/Library/Application Support/Logos4/Documents/p/PersonalBooks"
            dbdir.mkdir(parents=True)
            db = dbdir / "PersonalBookManager.db"
            con = sqlite3.connect(db)
            con.execute(
                "CREATE TABLE Books (Id INTEGER PRIMARY KEY, ResourceId TEXT, SourceFilePaths TEXT,"
                " Title TEXT, Authors TEXT, Description TEXT, Language TEXT, Copyright TEXT,"
                " ResourceType TEXT, CoverImage BLOB, LastCompiled TEXT, ModifiedDate TEXT,"
                " SyncRevision INT, SyncState INT, IsDeleted INT)")
            con.execute("INSERT INTO Books (Id,ResourceId,Title,Authors,Description,IsDeleted)"
                        " VALUES (1,'PBB:aaa','t','a',?,0)", (linked,))
            con.commit()
            con.close()

            def sync(published):
                with mock.patch.object(pb_sync, "REPO", str(root)), \
                        mock.patch.object(pb_sync, "BACKUP_DIR", str(root / "bk")), \
                        mock.patch.object(pb_sync, "logos_running", lambda: False), \
                        mock.patch.object(pb_sync, "published_slugs", lambda: published), \
                        mock.patch.dict(os.environ, {"HOME": str(root / "home")}), \
                        mock.patch.object(sys, "argv", ["pb_sync.py", "--apply"]), \
                        mock.patch("builtins.print", lambda *a, **k: None):
                    pb_sync.main()
                c = sqlite3.connect(db)
                try:
                    return c.execute("SELECT Description FROM Books WHERE Id=1").fetchone()[0]
                finally:
                    c.close()

            self.assertEqual(sync(None), linked)       # unreadable catalogue: kept
            self.assertEqual(sync(set()), "Amphilochius, On the Newly Baptized.")  # unpublished
            self.assertEqual(sync({"amph"}), linked)   # published: link written


if __name__ == "__main__":
    unittest.main()
