#!/usr/bin/env python3
"""One promotion point for certified English (2026-10-07).

Translation lanes write into this working tree all day. The site build and the
audio drain do not read it: they read a clean checkout of the committed
`main` (the site's scripts/published_books.py keeps it at
~/SaneApps/.worktrees/translations-published). So text reaches readers only
once it is committed, and nobody has to move uncommitted files aside before a
ship again.

Two ways in:
  - A lane certifies a book: work_pipeline.apply() calls commit_book() with the
    files it just wrote, and only when certified(slug) holds for them.
  - A person or agent commits a reviewed edit as usual.

  python3 scripts/promote.py pending            dirty books, and which of them
                                               are certified (would publish if
                                               committed)
  python3 scripts/promote.py commit <slug>...  commit the dirty files of a
                                               certified book (refuses one
                                               that is not certified)

A failed commit never undoes a certification: the book stays certified in this
tree, `pending` lists it, and fathers_watch warns (promote:pending).
"""
from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "main"
LOCK_WAIT_S = 120     # another lane's commit holds the promote lock
INDEX_RETRY_S = 60    # a person's git command holds .git/index.lock


def git(*args: str, root: Path = ROOT, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)


def _blocker(root: Path) -> str | None:
    """Why lanes must not commit here now, or None."""
    head = git("symbolic-ref", "-q", "HEAD", root=root)
    if head.returncode != 0:
        return "HEAD is detached"
    if head.stdout.strip() != f"refs/heads/{BRANCH}":
        return f"on {head.stdout.strip()}, not {BRANCH}"
    for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        p = git("rev-parse", "--git-path", name, root=root).stdout.strip()
        if p and (root / p if not os.path.isabs(p) else Path(p)).exists():
            return f"a {name} is in progress"
    return None


def commit_book(slug: str, paths: list[Path | str], message: str, root: Path = ROOT) -> tuple[bool, str]:
    """Commit exactly `paths` (all inside books/<slug>/) on main. Other staged or
    dirty files are left as they are (`git commit --only`). Never raises."""
    try:
        book = (root / "books" / slug).resolve()
        rel = []
        for p in paths:
            p = Path(p)
            p = (p if p.is_absolute() else root / p).resolve()
            if book not in p.parents:
                return False, f"refusing: {p} is outside books/{slug}/"
            rel.append(str(p.relative_to(root.resolve())))
        if not rel:
            return False, "nothing to commit"
        why = _blocker(root)
        if why:
            return False, f"not committed: {why}"
        common = git("rev-parse", "--git-common-dir", root=root).stdout.strip()
        lock_path = (root / common if not os.path.isabs(common) else Path(common)) / "fathers-promote.lock"
        with open(lock_path, "a") as fh:
            deadline = time.monotonic() + LOCK_WAIT_S
            while True:
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        return False, f"not committed: the promote lock stayed busy for {LOCK_WAIT_S} s"
                    time.sleep(1)
            return _commit_locked(rel, message, root)
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"not committed: {type(e).__name__}: {e}"


def _commit_locked(rel: list[str], message: str, root: Path) -> tuple[bool, str]:
    deadline = time.monotonic() + INDEX_RETRY_S
    while True:
        add = git("add", "-A", "--", *rel, root=root)
        if add.returncode == 0:
            if git("diff", "--cached", "--quiet", "--", *rel, root=root).returncode == 0:
                return True, "already committed (no change)"
            c = git("commit", "-q", "--no-verify", "-m", message, "--only", "--", *rel, root=root)
            if c.returncode == 0:
                sha = git("rev-parse", "--short", "HEAD", root=root).stdout.strip()
                return True, f"committed {sha}"
            err = (c.stderr or c.stdout).strip()
        else:
            err = (add.stderr or add.stdout).strip()
        if "index.lock" not in err or time.monotonic() >= deadline:
            return False, f"not committed: {err[:200]}"
        time.sleep(2)


def dirty_books(root: Path = ROOT) -> dict[str, list[str]]:
    """books/<slug>/ -> dirty paths (modified, added, deleted, untracked)."""
    r = git("status", "--porcelain", "-z", "--untracked-files=all", "--", "books", root=root, timeout=600)
    out: dict[str, list[str]] = {}
    if r.returncode != 0:
        raise RuntimeError(f"git status failed: {r.stderr.strip()[:200]}")
    entries = r.stdout.split("\0")
    i = 0
    while i < len(entries):
        e = entries[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":
            i += 1  # the rename's source path follows
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "books":
            out.setdefault(parts[1], []).append(path)
    return out


def _certified(slug: str) -> bool:
    sys.path.insert(0, str(ROOT / "scripts"))
    import work_pipeline  # noqa: E402  (heavy; only for the CLI)
    return work_pipeline.certified(slug)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("pending", "commit"):
        print(__doc__.strip())
        return 2
    dirty = dirty_books()
    if argv[0] == "pending":
        for slug in sorted(dirty):
            try:
                state = "certified, not committed" if _certified(slug) else "not certified"
            except Exception as e:  # noqa: BLE001
                state = f"unknown ({type(e).__name__})"
            print(f"{slug}\t{len(dirty[slug])} paths\t{state}")
        return 0
    rc = 0
    for slug in argv[1:]:
        if slug not in dirty:
            print(f"{slug}: nothing to commit")
            continue
        if not _certified(slug):
            print(f"{slug}: refusing: not certified (its receipt does not match the English)")
            rc = 1
            continue
        ok, msg = commit_book(slug, dirty[slug], f"Promote certified {slug}")
        print(f"{slug}: {msg}")
        rc = rc or (0 if ok else 1)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
