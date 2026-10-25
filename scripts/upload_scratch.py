#!/usr/bin/env python3
"""Dedicated scratch dir for files staged for upload or transfer (2026-10-25).

Why: tar parts (<work>-ptN-parts.tar, <work>-part-aa...) and sy_part_* slices
piled up in /private/tmp (18 GB, Mini disk down to 10 GB free). Producers now
stage into one folder, remove each file once its upload is verified, and the
first use of the folder sweeps anything older than 24 h.

  from upload_scratch import ensure_scratch, staged, remove_after_verified
  d = ensure_scratch()                       # creates the dir, sweeps >24 h files
  with staged("book-1-pt1-parts.tar", verify=lambda p: remote_size(p) == p.stat().st_size) as p:
      write_tar(p); upload(p)                # removed on exit only if verify() is True
  python3 scripts/upload_scratch.py sweep    # manual sweep, prints what it removed
  python3 scripts/upload_scratch.py path

Rules: a file is deleted only after its remote size (or sha256) matches; a failed
or unverified upload keeps the file for a retry; the sweep skips anything newer
than 24 h, anything not a plain file, and anything outside the scratch dir.
Override the dir with TRANSLATIONS_UPLOAD_SCRATCH.
"""
import contextlib
import hashlib
import os
import sys
import time
from pathlib import Path

DEFAULT_DIR = Path.home() / "SaneApps" / "scratch" / "translations-upload"
MAX_AGE_S = 24 * 3600


def scratch_dir() -> Path:
    return Path(os.environ.get("TRANSLATIONS_UPLOAD_SCRATCH") or DEFAULT_DIR)


def sweep_stale(d: Path | None = None, max_age_s: int = MAX_AGE_S, now: float | None = None) -> list[Path]:
    """Remove plain files directly in the scratch dir not modified for max_age_s."""
    d = Path(d) if d else scratch_dir()
    now = time.time() if now is None else now
    removed = []
    if not d.is_dir():
        return removed
    for p in d.iterdir():
        try:
            st = p.lstat()
            if not p.is_file() or p.is_symlink() or now - st.st_mtime < max_age_s:
                continue
            p.unlink()
            removed.append(p)
        except FileNotFoundError:
            continue
    return removed


def ensure_scratch() -> Path:
    """Create the scratch dir and sweep old files (the startup sweep)."""
    d = scratch_dir()
    d.mkdir(parents=True, exist_ok=True)
    sweep_stale(d)
    return d


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def remove_after_verified(path, remote_size: int | None = None, remote_sha256: str | None = None) -> bool:
    """Delete path only when the remote copy's size (and sha256 if given) match.

    Idempotent: a path that is already gone returns True. Without any remote
    evidence nothing is deleted."""
    p = Path(path)
    if remote_size is None and remote_sha256 is None:
        return False
    if not p.exists():
        return True
    if not p.is_file() or p.is_symlink():
        return False
    if remote_size is not None and p.stat().st_size != remote_size:
        return False
    if remote_sha256 is not None and _sha256(p) != remote_sha256.lower():
        return False
    p.unlink(missing_ok=True)
    return True


@contextlib.contextmanager
def staged(name: str, verify):
    """Yield a path in the scratch dir; on exit delete it only if verify(path) is True.

    verify(path) -> bool is the caller's check against the remote object (size
    or hash). An exception inside the block, a False result, or a verify error
    all keep the file for a retry (the 24 h sweep clears it later)."""
    p = ensure_scratch() / os.path.basename(name)
    completed = False
    try:
        yield p
        completed = True
    finally:
        # Only a block that finished may delete; an error keeps the file.
        if completed:
            try:
                ok = p.exists() and bool(verify(p))
            except Exception:
                ok = False
            if ok:
                p.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "path"
    if cmd == "path":
        print(scratch_dir())
    elif cmd == "sweep":
        for p in sweep_stale():
            print("removed", p)
    else:
        print("usage: upload_scratch.py [path|sweep]", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
