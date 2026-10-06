#!/usr/bin/env python3
"""Change-gated automatic ship for viapatrum.org (P16, owner approved 2026-10-06).

Run by com.saneapps.fathers-ship-auto at 13:30 and 05:30. Ships only when what
readers see changed since the last good auto ship:
  text     certified English, book.yml, work receipts, topic records
  audio    narration manifests (audio-only changes use ship.sh --audio-only)
  library  outputs/downloads/library.json (the paid shelf)

Never ships when:
  - the site repo has uncommitted code in scripts/, assets/ or functions/
    (unreviewed work, e.g. an agent mid-change),
  - another ship or a package build holds outputs/build.lock,
  - MAX_PER_DAY ships already ran today, or the disk has under 15 GB free.
ship.sh's own gates still decide whether a deploy goes out.

After a good full ship it refreshes the paid shelf from the shipped build
(EPUB/PDF, audiobooks, Word, assemble, upload: direct, then the admin route for files over 280 MB); a changed
library.json then ships on the next run.

state: outputs/ship-auto/state.json. fathers_watch alerts when changes have
waited over ALERT_HOURS. Usage: ship_if_changed.py [--dry-run]
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

T = Path(__file__).resolve().parents[1]
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
OUT = T / "outputs/ship-auto"
STATE = OUT / "state.json"
RUN_LOCK = OUT / "run.lock"
MAX_PER_DAY = 2
MIN_FREE_GB = 15
ALERT_HOURS = 6  # fathers_watch.check_ship_auto uses the same 6 h
DRY = "--dry-run" in sys.argv


def log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def fingerprint(paths) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        try:
            st = p.stat()
        except FileNotFoundError:
            continue
        h.update(f"{p}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


def inputs() -> dict:
    books = T / "books"
    text = (list(books.glob("*/translations/*.json")) + list(books.glob("*/book.yml"))
            + list(books.glob("*/reviews/work_receipt.json"))
            + list(books.glob("ante-nicene-topics/translations/topics/*.json"))
            + [books / "ante-nicene-topics/topics.yml"])
    return {"text": fingerprint(text),
            "audio": fingerprint(SITE.glob("outputs/audio/*/manifest.json")),
            "library": fingerprint([SITE / "outputs/downloads/library.json"])}


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(st: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    tmp.rename(STATE)


def free_gb() -> int:
    return shutil.disk_usage("/System/Volumes/Data").free // 2**30


def run(cmd: list[str], timeout: int, cwd: Path = SITE) -> int:
    log("+ " + " ".join(cmd))
    try:
        return subprocess.run(["nice", "-n", "10", *cmd], cwd=cwd, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        log(f"timeout after {timeout}s")
        return 124


def with_token(py_args: str, timeout: int) -> int:
    """library_sync upload needs CLOUDFLARE_API_TOKEN; load it the way ship.sh does."""
    return run(["bash", "-c", f'source "$HOME/.config/nv/env" >/dev/null 2>&1; {py_args}'], timeout)


def refresh_library() -> None:
    app = SITE / "outputs/ship-last/dist/app/v1"
    if not (app / "catalog.json").is_file():
        log("library: no shipped app export; skipped")
        return
    py = str(T / ".venv/bin/python")
    steps = [
        ([py, "scripts/build_ebooks.py", "--app-dir", str(app), "--jobs", "2"], 7200),
        ([py, "scripts/build_audiobooks.py", "--app-dir", str(app), "--jobs", "1"], 7200),
        ([py, "scripts/library_sync.py", "word", "--app-dir", str(app), "--jobs", "2"], 3600),
        ([py, "scripts/library_sync.py", "assemble", "--app-dir", str(app)], 1800),
    ]
    for cmd, limit in steps:
        rc = run(cmd, limit)
        if rc != 0:
            log(f"library: step failed rc={rc}; upload skipped, shelf unchanged")
            return
    rc = with_token(f'"{py}" scripts/library_sync.py upload --direct --jobs 4', 3600)
    log(f"library: direct upload rc={rc}")
    # Files over 280 MB (era audiobook zips, the largest audiobooks) go through
    # the just-verified site's admin route; already-uploaded files are skipped.
    rc = with_token(f'"{py}" scripts/library_sync.py upload --base https://viapatrum.org --jobs 2', 4 * 3600)
    log(f"library: large-file upload rc={rc}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        RUN_LOCK.mkdir()
    except FileExistsError:
        age = time.time() - RUN_LOCK.stat().st_mtime
        if age < 6 * 3600:
            log(f"another auto ship started {int(age // 60)} min ago; exit")
            return 0
        log("stale run lock (over 6 h); taking it")
    try:
        return _main()
    finally:
        shutil.rmtree(RUN_LOCK, ignore_errors=True)


def _main() -> int:
    st = load_state()
    now = inputs()
    last = st.get("shipped", {})
    changed = [k for k in now if now[k] != last.get(k)]
    if not changed:
        log("no change since the last auto ship")
        st.pop("pending_since", None)
        save_state(st)
        return 0
    st.setdefault("pending_since", time.strftime("%Y-%m-%dT%H:%M:%S"))
    st["pending"] = changed
    today = time.strftime("%Y-%m-%d")
    done_today = st.get("ships", {}).get(today, 0)

    why = None
    dirty = subprocess.run(["git", "-C", str(SITE), "status", "--porcelain", "--", "scripts", "assets", "functions"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        why = f"uncommitted site code ({len(dirty.splitlines())} paths)"
    elif done_today >= MAX_PER_DAY:
        why = f"daily cap reached ({done_today}/{MAX_PER_DAY})"
    elif free_gb() < MIN_FREE_GB:
        why = f"disk low ({free_gb()} GB free)"
    if why:
        st["last_skip"] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "why": why, "changed": changed}
        save_state(st)
        log(f"changed {changed}; not shipping: {why}")
        return 0

    audio_only = changed == ["audio"] and (SITE / "outputs/ship-last/receipt.json").is_file()
    cmd = ["scripts/ship.sh"] + (["--audio-only"] if audio_only else [])
    if DRY:
        log(f"changed {changed}; would run {' '.join(cmd)} (dry run)")
        save_state(st)
        return 0

    # Hold the package-build lock for the whole ship: builds and ships share the Mini's RAM.
    lock = subprocess.run(["python3", str(SITE / "scripts/ship_lock.py"), str(SITE / "outputs/build.lock"), str(os.getpid())],
                          capture_output=True, text=True)
    if lock.returncode != 0:
        st["last_skip"] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "why": "build lock held", "changed": changed}
        save_state(st)
        log("a build or ship holds outputs/build.lock; next run")
        return 0

    receipt = SITE / "outputs/ship-last/receipt.json"
    before = receipt.stat().st_mtime if receipt.is_file() else 0
    rc = run(cmd, 4 * 3600)
    # Count only runs that deployed (ship.sh rewrites ship-last at deploy); a
    # run blocked by a gate must not use up the day's cap.
    if receipt.is_file() and receipt.stat().st_mtime > before:
        st.setdefault("ships", {})[today] = done_today + 1
    st["ships"] = {d: n for d, n in st.get("ships", {}).items() if d >= time.strftime("%Y-%m-%d", time.localtime(time.time() - 7 * 86400))}
    verified = receipt.is_file() and receipt.stat().st_mtime > before and json.loads(receipt.read_text()).get("verified")
    st["last_ship"] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "rc": rc, "mode": "audio-only" if audio_only else "full",
                       "verified": bool(verified), "changed": changed}
    if rc == 0 and verified:
        st["shipped"] = now  # inputs as read before the ship; later edits ship next run
        st.pop("pending_since", None)
        st.pop("pending", None)
        save_state(st)
        log("ship verified")
        if not audio_only:
            refresh_library()
    else:
        save_state(st)
        log(f"ship did not verify (rc={rc}); inputs stay pending")
    return 0


if __name__ == "__main__":
    sys.exit(main())
