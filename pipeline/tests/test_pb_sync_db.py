import importlib.util
import os
import sqlite3
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_pb_sync():
    spec = importlib.util.spec_from_file_location(
        "pb_sync", os.path.join(REPO, "scripts", "pb_sync.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_db(home, profile):
    p = os.path.join(
        home, "Library/Application Support/Logos4/Documents",
        profile, "PersonalBooks", "PersonalBookManager.db",
    )
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b"db")
    return p


def test_resolve_pb_db_prefers_newest():
    pb_sync = _load_pb_sync()
    with tempfile.TemporaryDirectory() as tmp:
        old = _make_db(tmp, "aaa111.old")
        time.sleep(0.02)
        new = _make_db(tmp, "zzz999.new")
        prev = os.environ.get("HOME")
        os.environ["HOME"] = tmp
        try:
            assert pb_sync.resolve_pb_db() == new
        finally:
            if prev is None:
                del os.environ["HOME"]
            else:
                os.environ["HOME"] = prev
        assert old != new


def _books_schema(cur):
    cur.execute(
        "CREATE TABLE Books (Id integer primary key autoincrement,"
        "ResourceId text not null,SourceFilePaths text,Title text,"
        "Authors text,Description text,Language text,Copyright text,"
        "ResourceType text,CoverImage blob,LastCompiled text,"
        "ModifiedDate text not null,SyncRevision integer,"
        "SyncState int not null,IsDeleted bool not null)"
    )


def _sample_row(cover):
    return {
        "src": "/tmp/x.docx", "title": "T", "authors": "A",
        "description": "D", "language": "en", "copyright": "C",
        "resource_type": "text.monograph", "cover": cover,
        "now": "2026-09-18T00:00:00-04:00",
    }


def test_insert_book_row_writes_cover():
    pb_sync = _load_pb_sync()
    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    _books_schema(cur)
    pb_sync.insert_book_row(cur, "PBB:cover", _sample_row(b"JPEGDATA"))
    got = cur.execute(
        "SELECT Title,length(CoverImage),ResourceType FROM Books"
    ).fetchone()
    assert got == ("T", 8, "text.monograph")
    con.close()


def test_update_book_row_writes_cover():
    pb_sync = _load_pb_sync()
    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    _books_schema(cur)
    pb_sync.insert_book_row(cur, "PBB:cover", _sample_row(None))
    bid = cur.lastrowid
    pb_sync.update_book_row(cur, bid, _sample_row(b"NEWDATA!"))
    got = cur.execute(
        "SELECT Title,length(CoverImage),ResourceType FROM Books WHERE Id=?",
        (bid,),
    ).fetchone()
    assert got == ("T", 8, "text.monograph")
    con.close()


def test_resolve_pb_db_missing_exits():
    pb_sync = _load_pb_sync()
    with tempfile.TemporaryDirectory() as tmp:
        prev = os.environ.get("HOME")
        os.environ["HOME"] = os.path.join(tmp, "empty-home")
        try:
            try:
                pb_sync.resolve_pb_db()
            except SystemExit:
                pass
            else:
                raise AssertionError("expected SystemExit")
        finally:
            if prev is None:
                del os.environ["HOME"]
            else:
                os.environ["HOME"] = prev
