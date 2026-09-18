import importlib.util
import os
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
