#!/usr/bin/env python3
"""Change-gated automatic ship for viapatrum.org (P16, owner approved 2026-10-06).

Run by com.saneapps.fathers-ship-auto every 30 minutes. Ships only when what
readers see changed since the last good auto ship:
  text     certified English, book.yml, work receipts, topic records
  audio    narration manifests (audio-only changes use ship.sh --audio-only)
  library  outputs/downloads/library.json (the paid shelf)
  site     the site repo's committed revision (a code-only change does not
           rebuild the shelf)

Never ships when:
  - the site repo has uncommitted code in scripts/, assets/ or functions/
    (unreviewed work, e.g. an agent mid-change), or git status fails,
  - another ship, build, e2e or Logos compile holds outputs/build.lock for
    more than LOCK_WAIT_S (this job waits that long, then skips),
  - the disk has under MIN_FREE_GB free.
ship.sh's own gates still decide whether a deploy goes out.

After a good full ship (not --audio-only) of new text it refreshes the paid
shelf from the shipped build (EPUB/PDF, audiobooks, Word, assemble, upload:
direct, then the admin route for files over 280 MB); the changed library.json
then ships on the next run, and that library-only ship does not start another
shelf. An audio-only ship starts no shelf, so new narration reaches the paid
audiobooks only with the next text change (an open owner call, 2026-10-06).

The shelf is marked done only when both uploads return 0. Until then
state.json keeps "shelf_pending" (the steps done, and "error" when a step
failed or the job was killed). The next run resumes it from the first step
not done. Once assemble has rewritten library.json, nothing ships until the
uploads finish, so a catalogue that lists files not yet uploaded never goes
live.

Exit codes, so launchd and fathers_watch see what happened:
  0  nothing changed, or the ship verified and the shelf finished
  1  ship.sh ran and did not verify (inputs stay pending)
  2  skipped: uncommitted site code, git status failed, disk under
     MIN_FREE_GB, or another build held outputs/build.lock too long
  3  shelf refresh failed (shelf_pending stays set; the next run resumes it)
  75 another auto ship is still running (its pid is alive, runs this script,
     and is younger than RUN_HARD_LIMIT_S)
  143 killed by SIGTERM (launchd timeout); pending and shelf_pending stay set

state: outputs/ship-auto/state.json ("last_run" is every run's exit and why).
fathers_watch reads it. Usage: ship_if_changed.py [--dry-run]
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

T = Path(__file__).resolve().parents[1]
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
OUT = T / "outputs/ship-auto"
STATE = OUT / "state.json"
RUN_LOCK = OUT / "run.lock"  # a directory; its "pid" file holds "<pid> <start epoch>"
BUILD_LOCK = SITE / "outputs/build.lock"
# The one disk floor for Fathers builds, ships and the shelf. fathers_watch
# imports it, so the watch warns at the same number this job skips at.
MIN_FREE_GB = 15
ALERT_HOURS = 6  # fathers_watch.check_ship_auto uses the same 6 h
LOCK_WAIT_S = 1800  # wait this long for outputs/build.lock, then skip
# launchd runs this job under `timeout --kill-after=300 27000`, so no real run
# lives longer than this; an older run.lock was left by a kill or a reboot.
RUN_HARD_LIMIT_S = 27300
DRY = "--dry-run" in sys.argv
EXIT_OK, EXIT_FAILED, EXIT_SKIPPED, EXIT_SHELF, EXIT_BUSY, EXIT_TERM = 0, 1, 2, 3, 75, 143


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
    try:
        rev = subprocess.run(["git", "-C", str(SITE), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        site = rev.stdout.strip() if rev.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        site = ""
    return {"text": fingerprint(text),
            "audio": fingerprint(SITE.glob("outputs/audio/*/manifest.json")),
            "library": fingerprint([SITE / "outputs/downloads/library.json"]),
            "site": site}


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


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def pid_command(pid: int) -> str | None:
    """The command line of a running pid ("" when it is gone), or None when ps
    itself could not run."""
    try:
        r = subprocess.run(["ps", "-ww", "-o", "command=", "-p", str(pid)],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip()


def lock_holder_live(pid: int, start: int, script: str, max_age_s: int) -> bool:
    """True when the pid in a run lock is still that job. A lock under outputs/
    survives a SIGKILL, a crash and a reboot, and after a reboot its pid can
    belong to some unrelated process. So the pid must be alive, younger than
    the job's hard time limit, and running `script`. When ps cannot run, a live
    young pid counts as the job (two runs at once is the worse mistake)."""
    if not pid or not alive(pid):
        return False
    if start and time.time() - start > max_age_s:
        return False
    cmd = pid_command(pid)
    return cmd is None or script in cmd


def run(cmd: list[str], timeout: int, cwd: Path = SITE) -> int:
    log("+ " + " ".join(cmd))
    # FATHERS_BUILD_LOCK_HELD tells ship.sh and build_site.py that this job
    # already holds outputs/build.lock, so they must not wait on it themselves.
    env = {**os.environ, "FATHERS_BUILD_LOCK_HELD": str(os.getpid())}
    try:
        return subprocess.run(["nice", "-n", "10", *cmd], cwd=cwd, timeout=timeout, env=env).returncode
    except subprocess.TimeoutExpired:
        log(f"timeout after {timeout}s")
        return 124


def with_token(py_args: str, timeout: int) -> int:
    """library_sync upload needs CLOUDFLARE_API_TOKEN; load it the way ship.sh does."""
    return run(["bash", "-c", f'source "$HOME/.config/nv/env" >/dev/null 2>&1; {py_args}'], timeout)


def take_run_lock() -> bool:
    """One auto ship at a time. A lock whose holder is no longer this job
    (pid gone, pid reused by another program after a reboot, or older than
    RUN_HARD_LIMIT_S) is taken over at once; a live one makes this run exit 75."""
    try:
        RUN_LOCK.mkdir()
    except FileExistsError:
        try:
            pid_s, start_s = (RUN_LOCK / "pid").read_text().split()[:2]
            pid, start = int(pid_s), int(start_s)
        except (OSError, ValueError):
            pid, start = 0, 0
        if lock_holder_live(pid, start, "ship_if_changed.py", RUN_HARD_LIMIT_S):
            log(f"another auto ship (pid {pid}) has run {int((time.time() - start) // 60)} min; exit {EXIT_BUSY}")
            return False
        log(f"run lock left by pid {pid or '?'}, which is no longer an auto ship "
            f"(gone, another program, or over {RUN_HARD_LIMIT_S // 3600} h old); taking it")
        shutil.rmtree(RUN_LOCK, ignore_errors=True)
        try:
            RUN_LOCK.mkdir()
        except FileExistsError:
            log("another auto ship took the lock first; exit")
            return False
    (RUN_LOCK / "pid").write_text(f"{os.getpid()} {int(time.time())}\n")
    return True


def take_build_lock() -> bool:
    """Hold outputs/build.lock (via the site's ship_lock.py) until this process
    exits. Waits up to LOCK_WAIT_S for a build, e2e or Logos compile to finish."""
    deadline = time.monotonic() + LOCK_WAIT_S
    said = False
    while True:
        r = subprocess.run(["python3", str(SITE / "scripts/ship_lock.py"), str(BUILD_LOCK), str(os.getpid())],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            log(f"holding outputs/build.lock ({r.stdout.strip()})")
            return True
        if time.monotonic() >= deadline:
            return False
        if not said:
            log(f"outputs/build.lock is held ({(r.stderr or r.stdout).strip()}); waiting up to {LOCK_WAIT_S // 60} min")
            said = True
        time.sleep(30)


def site_code_gate() -> str | None:
    """Why the site repo is not safe to ship from, or None. assets/og is left
    out: ship.sh itself rewrites those share cards on every ship, so they
    were dirty after each ship and kept auto-ship off (2026-10-07 re-audit)."""
    try:
        r = subprocess.run(["git", "-C", str(SITE), "status", "--porcelain", "--", "scripts", "assets", "functions",
                            ":(exclude)assets/og"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return f"git status failed ({type(e).__name__})"
    if r.returncode != 0:
        return f"git status failed (rc {r.returncode}): {r.stderr.strip()[:120]}"
    dirty = r.stdout.strip()
    if dirty:
        lines = dirty.splitlines()
        names = ", ".join((line.split(None, 1)[1] if " " in line else line) for line in lines[:3])
        more = f" +{len(lines) - 3}" if len(lines) > 3 else ""
        return f"uncommitted site code ({len(lines)} paths: {names}{more})"
    if free_gb() < MIN_FREE_GB:
        return f"disk low ({free_gb()} GB free, floor {MIN_FREE_GB} GB)"
    return None


def finish(st: dict, code: int, why: str) -> int:
    st["last_run"] = {"at": now_ts(), "exit": code, "why": why}
    save_state(st)
    return code


def skip(st: dict, changed: list[str], why: str) -> int:
    st["last_skip"] = {"at": now_ts(), "why": why, "changed": changed}
    log(f"changed {changed}; not shipping: {why}")
    return finish(st, EXIT_SKIPPED, why)


def shipped_at() -> str:
    try:
        return json.loads((SITE / "outputs/ship-last/receipt.json").read_text()).get("shipped_at", "")
    except (OSError, ValueError):
        return ""


def shelf_steps(py: str, app: Path) -> list[tuple[str, list[str] | str, int]]:
    """(name, command, time limit). A str command needs the Cloudflare token."""
    return [
        ("ebooks", [py, "scripts/build_ebooks.py", "--app-dir", str(app), "--jobs", "2"], 7200),
        ("audiobooks", [py, "scripts/build_audiobooks.py", "--app-dir", str(app), "--jobs", "1"], 7200),
        ("word", [py, "scripts/library_sync.py", "word", "--app-dir", str(app), "--jobs", "2"], 3600),
        ("assemble", [py, "scripts/library_sync.py", "assemble", "--app-dir", str(app)], 1800),
        ("upload-direct", f'"{py}" scripts/library_sync.py upload --direct --jobs 4', 3600),
        # Files over 280 MB (era audiobook zips, the largest audiobooks) go through
        # the just-verified site's admin route; already-uploaded files are skipped.
        ("upload-large", f'"{py}" scripts/library_sync.py upload --base https://viapatrum.org --jobs 2', 4 * 3600),
    ]


def refresh_library(st: dict) -> int:
    """Build and upload the paid shelf from the shipped build, resuming from
    st["shelf_pending"]["done"]. Returns 0 only when every step returned 0."""
    shelf = st.setdefault("shelf_pending", {"since": now_ts(), "for_ship": shipped_at(), "done": []})
    if shelf.get("for_ship") != shipped_at():
        log("library: a newer ship replaced the build this shelf was for; starting the shelf over")
        shelf.update(since=now_ts(), for_ship=shipped_at(), done=[])
    shelf.pop("error", None)
    app = SITE / "outputs/ship-last/dist/app/v1"
    if not (app / "catalog.json").is_file():
        shelf["error"] = "no shipped app export in outputs/ship-last"
        save_state(st)
        log(f"library: {shelf['error']}; shelf left pending")
        return 1
    py = str(T / ".venv/bin/python")
    for name, cmd, limit in shelf_steps(py, app):
        if name in shelf["done"]:
            continue
        shelf["step"] = name
        save_state(st)  # a kill from here on is recorded against this step
        rc = with_token(cmd, limit) if isinstance(cmd, str) else run(cmd, limit)
        if rc != 0:
            shelf["error"] = f"{name} rc={rc}"
            save_state(st)
            log(f"library: {name} failed rc={rc}; shelf left pending, the next run resumes at {name}")
            return rc
        shelf["done"].append(name)
        log(f"library: {name} done")
    st.pop("shelf_pending", None)
    st["last_shelf"] = {"at": now_ts(), "for_ship": shipped_at(), "ok": True}
    save_state(st)
    log("library: shelf refreshed and uploaded")
    return 0


def ship(st: dict, now: dict, changed: list[str]) -> int:
    audio_only = changed == ["audio"] and (SITE / "outputs/ship-last/receipt.json").is_file()
    cmd = ["scripts/ship.sh"] + (["--audio-only"] if audio_only else [])
    receipt = SITE / "outputs/ship-last/receipt.json"
    before = receipt.stat().st_mtime if receipt.is_file() else 0
    save_state(st)  # pending is on disk before a kill can land
    rc = run(cmd, 4 * 3600)
    # ship.sh rewrites the receipt only when a deploy went out.
    deployed = receipt.is_file() and receipt.stat().st_mtime > before
    verified = deployed and json.loads(receipt.read_text()).get("verified")
    st["last_ship"] = {"at": now_ts(), "rc": rc, "mode": "audio-only" if audio_only else "full",
                       "verified": bool(verified), "changed": changed}
    if not (rc == 0 and verified):
        save_state(st)
        log(f"ship did not verify (rc={rc}); inputs stay pending")
        return EXIT_FAILED
    st["shipped"] = now  # inputs as read before the ship; later edits ship next run
    st.pop("pending_since", None)
    st.pop("pending", None)
    # New text needs a new shelf. Audio alone waits for the next text ship
    # (owner 2026-10-06). The shelf's own library.json, and a committed site
    # revision, do not: rebuilding on those would ship and rebuild forever.
    if "text" in changed or ("audio" in changed and not audio_only):
        st["shelf_pending"] = {"since": now_ts(), "for_ship": shipped_at(), "done": []}
    save_state(st)
    log("ship verified")
    return EXIT_OK


def on_term(_signum, _frame) -> None:
    raise SystemExit(EXIT_TERM)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not take_run_lock():
        return EXIT_BUSY
    signal.signal(signal.SIGTERM, on_term)
    try:
        return _main()
    except SystemExit as e:
        if e.code == EXIT_TERM:
            st = load_state()  # every long step saved state before it started
            if st.get("shelf_pending"):
                st["shelf_pending"]["error"] = f"killed (SIGTERM) during {st['shelf_pending'].get('step', '?')}"
            log("SIGTERM (launchd timeout or stop); pending changes and the shelf stay pending")
            finish(st, EXIT_TERM, "killed by SIGTERM")
        raise
    finally:
        shutil.rmtree(RUN_LOCK, ignore_errors=True)


def _main() -> int:
    st = load_state()
    st.pop("ships", None)  # the old daily count is not a gate
    now = inputs()
    last = st.get("shipped", {})
    changed = [k for k in now if now[k] != last.get(k)]
    shelf = st.get("shelf_pending")
    if not changed and not shelf:
        log("no change since the last auto ship")
        st.pop("pending_since", None)
        st.pop("pending", None)
        return finish(st, EXIT_OK, "no change")
    if changed:
        st.setdefault("pending_since", now_ts())
        st["pending"] = changed
    if shelf:
        log(f"paid shelf still pending since {shelf.get('since')} (done: {', '.join(shelf.get('done', [])) or 'nothing'}"
            f"{'; last error: ' + shelf['error'] if shelf.get('error') else ''})")

    why = site_code_gate()
    if why:
        return skip(st, changed, why)
    if DRY:
        log(f"changed {changed}; would {'finish the shelf, then ' if shelf else ''}run scripts/ship.sh (dry run)")
        save_state(st)
        return EXIT_OK
    if not take_build_lock():
        return skip(st, changed, f"outputs/build.lock held for over {LOCK_WAIT_S // 60} min")

    # assemble already rewrote library.json: finish the uploads before any
    # ship, or the live downloads page would list files that are not uploaded.
    if shelf and "assemble" in shelf.get("done", []):
        rc = refresh_library(st)
        if rc != 0:
            return finish(st, EXIT_SHELF, f"paid shelf: {st['shelf_pending'].get('error')}; nothing shipped")
        shelf = None
        now = inputs()
        changed = [k for k in now if now[k] != last.get(k)]
        if changed:
            st["pending"] = changed

    if changed:
        code = ship(st, now, changed)
        if code != EXIT_OK:
            return finish(st, code, f"ship did not verify ({', '.join(changed)} still pending)")
        shelf = st.get("shelf_pending")

    if shelf:
        rc = refresh_library(st)
        if rc != 0:
            return finish(st, EXIT_SHELF, f"paid shelf: {st['shelf_pending'].get('error')}")
    return finish(st, EXIT_OK, "shipped" if changed else "shelf finished")


if __name__ == "__main__":
    sys.exit(main())
