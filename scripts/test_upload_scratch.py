import hashlib
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import upload_scratch as us


class UploadScratchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "scratch"
        os.environ["TRANSLATIONS_UPLOAD_SCRATCH"] = str(self.dir)

    def tearDown(self):
        os.environ.pop("TRANSLATIONS_UPLOAD_SCRATCH", None)
        self.tmp.cleanup()

    def test_sweep_removes_only_old_plain_files(self):
        d = us.ensure_scratch()
        old, new = d / "old.tar", d / "new.tar"
        old.write_bytes(b"x"); new.write_bytes(b"y")
        past = time.time() - 25 * 3600
        os.utime(old, (past, past))
        (d / "sub").mkdir()
        os.utime(d / "sub", (past, past))
        gone = us.sweep_stale()
        self.assertEqual(gone, [old])
        self.assertTrue(new.exists() and (d / "sub").is_dir())

    def test_sweep_ignores_other_dirs(self):
        other = Path(self.tmp.name) / "other.tar"
        other.write_bytes(b"x")
        past = time.time() - 48 * 3600
        os.utime(other, (past, past))
        us.ensure_scratch()
        self.assertTrue(other.exists())

    def test_remove_needs_matching_evidence(self):
        p = Path(self.tmp.name) / "a.tar"
        p.write_bytes(b"hello")
        self.assertFalse(us.remove_after_verified(p))
        self.assertFalse(us.remove_after_verified(p, remote_size=4))
        self.assertFalse(us.remove_after_verified(p, remote_size=5, remote_sha256="0" * 64))
        self.assertTrue(p.exists())
        self.assertTrue(us.remove_after_verified(p, 5, hashlib.sha256(b"hello").hexdigest()))
        self.assertFalse(p.exists())
        self.assertTrue(us.remove_after_verified(p, remote_size=5))  # idempotent

    def test_staged_deletes_only_when_verified(self):
        with us.staged("ok.tar", verify=lambda p: p.stat().st_size == 3) as p:
            p.write_bytes(b"abc")
        self.assertFalse(p.exists())
        with us.staged("bad.tar", verify=lambda p: False) as p:
            p.write_bytes(b"abc")
        self.assertTrue(p.exists())

    def test_staged_keeps_file_on_error_or_verify_crash(self):
        with self.assertRaises(RuntimeError):
            with us.staged("e.tar", verify=lambda p: True) as p:
                p.write_bytes(b"abc")
                raise RuntimeError("upload failed")
        self.assertTrue((self.dir / "e.tar").exists())  # error in the block keeps the file
        def boom(p):
            raise OSError("net down")
        with us.staged("v.tar", verify=boom) as q:
            q.write_bytes(b"abc")
        self.assertTrue(q.exists())


if __name__ == "__main__":
    unittest.main()
