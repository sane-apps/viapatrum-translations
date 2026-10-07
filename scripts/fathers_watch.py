#!/usr/bin/env python3
"""Fathers Watch: one periodic health pass over the translation pipeline.

Runs every 15 min on the Mini via launchd (com.saneapps.fathers-watch).
Reads state, writes outputs/fathers-watch/status.json + alerts.log.
Self-heal is bounded and logged: kill a twice-confirmed hung burn child,
remove a PID-dead logos lock older than 30 min. Never touches gates,
never edits books, never ships.

Alerting is state-change based: an alert id appears once when a check
goes bad and disappears on recovery; alerts.log gets one line when an
alert appears and one when it clears. The Air notifier
(com.saneapps.fathers-watch-notify -> scripts/fathers_watch_notify.py)
reads status.json over ssh and turns transitions into notifications; it
also alerts when status.json is older than STALE_MIN, because a watch that
is unloaded or stuck cannot report itself. The first pass after such a gap
raises watch:gap once.

The only Fathers monitor (2026-10-06): it absorbed scripts/health_watch.py
(lanes, queue progress, 429s, batch broker, audio drain, ship, held review)
and watches every live com.saneapps.fathers-* LaunchAgent.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

HOME = Path.home()
REPO = HOME / "SaneApps/clients/translations"
SITE = HOME / "SaneApps/websites/fathers.saneapps.com"
LA = HOME / "Library/LaunchAgents"
LOGS = HOME / "Library/Logs/SaneApps"
WP = REPO / "outputs/work-pipeline"
OUT = REPO / "outputs/fathers-watch"
STATUS = OUT / "status.json"
ALERTS_LOG = OUT / "alerts.log"
RUN_LOCK = OUT / "watch.lock"

sys.path.insert(0, str(REPO / "scripts"))
import fathers_overnight_health as burnmod  # noqa: E402
import ship_if_changed as autoship  # noqa: E402  (one disk floor, one ship fingerprint)

WATCH_LABEL = "com.saneapps.fathers-watch"
STALE_MIN = 30  # status.json older than this = the watch is not running (it runs every 15 min)
WATCH_HARD_LIMIT_S = STALE_MIN * 60  # a watch.lock older than this is a stuck or dead pass
DRAIN_SILENT_S = 2 * 900  # audio drain log silent this long = two missed 15-min runs
BROKER_STUCK_S = 1800  # a queued broker item this old with no batch in flight = its flusher is dead
# A lock line written by a busy tick; it must not count as the job making progress.
BUSY_RE = re.compile(r"\S+ BUSY: ")
LOCK_NOTE = ""  # set by main() when it took over a watch lock left by a dead pass
HELD_REVIEW = "com.saneapps.fathers-held-review"
OVERNIGHT = "com.saneapps.fathers-overnight-quota"
# Not named fathers-* but serves the lanes (KeepAlive).
EXTRA_JOBS = ["com.saneapps.cf-batch-broker"]
CERT_WINDOW_H = 6
CERT_FLOOR = 1  # works certified per CERT_WINDOW_H while lanes run
REDRAFT_LIMIT = 3  # same section redrafted this often in one run = a loop

PRIOR: dict = {}  # last status.json, set by main()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_prior() -> dict:
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def prior_info(name: str) -> dict:
    return ((PRIOR.get("checks") or {}).get(name) or {}).get("info") or {}


def live_jobs() -> list[str]:
    """One plist per live job; retired ones are *.plist.disabled or *.bak-*,
    which this glob skips, so a retirement never leaves a stale entry."""
    jobs = sorted(p.stem for p in LA.glob("com.saneapps.fathers-*.plist") if p.stem != WATCH_LABEL)
    return jobs + [j for j in EXTRA_JOBS if (LA / f"{j}.plist").exists()]


def overnight_retired() -> bool:
    """The overnight-quota burn was retired 2026-10-03 (plist renamed .disabled)."""
    return not (LA / f"{OVERNIGHT}.plist").exists() and (LA / f"{OVERNIGHT}.plist.disabled").exists()


@lru_cache(maxsize=1)
def launchctl_states() -> dict | None:
    """label -> (pid, last exit) from `launchctl list`, or None."""
    try:
        raw = subprocess.check_output(["launchctl", "list"], text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    out = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) == 3:
            out[parts[2]] = (parts[0], parts[1])
    return out


def load_queue() -> dict:
    try:
        return json.loads((WP / "queue.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def lanes_paused() -> bool:
    return (WP / "lanes.paused").exists()


def local_ts(s: str) -> float:
    try:
        return datetime.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S").timestamp()
    except ValueError:
        return 0.0


def timed_lines(path: Path, n: int = 400) -> list[tuple[float, str]]:
    """Last n lines of a log whose lines start HH:MM:SS (no date), with an
    absolute time: the newest line is dated by the file mtime and the day
    steps back whenever the clock runs backwards."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
        day = datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return []
    out, last = [], None
    for line in reversed(lines):
        m = re.match(r"(\d\d):(\d\d):(\d\d) ", line)
        if not m:
            continue
        t = day.replace(hour=int(m[1]), minute=int(m[2]), second=int(m[3]), microsecond=0)
        if last is not None and t > last:
            day -= timedelta(days=1)
            t -= timedelta(days=1)
        last = t
        out.append((t.timestamp(), line))
    return list(reversed(out))


def check_watch() -> tuple[str, str, dict]:
    """The watch cannot report while it is unloaded or stuck, so the first pass
    after a gap says how long it was silent (and the Air notifier alerts on a
    stale status.json while the gap lasts)."""
    info: dict = {}
    problems = []
    try:
        prev = datetime.fromisoformat(str(PRIOR.get("checked_at"))).timestamp()
        info["gap_min"] = round((time.time() - prev) / 60)
        if info["gap_min"] > STALE_MIN:
            problems.append(f"watch was silent {info['gap_min']} min before this pass (unloaded or stuck)")
    except (TypeError, ValueError):
        pass
    if LOCK_NOTE:
        problems.append(LOCK_NOTE)
    code = (launchctl_states() or {}).get(WATCH_LABEL, ("-", None))[1]
    info["last_exit"] = code
    if code not in (None, "0", "-"):
        problems.append(f"previous watch pass exited {code}")
    if problems:
        return "warn", "; ".join(problems), info
    return "ok", "watch ran on time", info


def check_burn() -> tuple[str, str, dict]:
    """IDLE / HEALTHY / HUNG via the existing burn module (no kill here)."""
    if overnight_retired():
        return "ok", "skipped: overnight burn retired 2026-10-03", {"retired": True}
    procs = burnmod.pgrep()
    age = burnmod.log_age_s()
    info = {"procs": len(procs), "log_age_s": None if age is None else int(age)}
    if not procs:
        return "ok", "idle, no burn process", info
    if age is None:
        return "fail", f"HUNG: {len(procs)} live procs, no overnight log", info
    if age > 900:
        last = burnmod.last_log_line()
        return "fail", f"HUNG: log silent {int(age)}s, {len(procs)} procs; tail: {last}", info
    return "ok", f"healthy: log {int(age)}s ago, {len(procs)} procs", info


def check_quota() -> tuple[str, str, dict]:
    if overnight_retired():
        return "ok", "skipped: overnight-quota retired 2026-10-03", {"retired": True}
    files = sorted((REPO / "outputs/overnight-quota").glob("*-dual.json"))
    if not files:
        return "warn", "no quota receipts at all", {}
    latest = files[-1]
    age_h = (time.time() - latest.stat().st_mtime) / 3600
    info = {"latest": latest.name, "age_h": round(age_h, 1)}
    try:
        d = json.loads(latest.read_text(encoding="utf-8"))
        lanes = d.get("lanes", {})
        summ = {k: (v.get("done_count"), v.get("held_count"), v.get("stop_reason"))
                for k, v in lanes.items() if isinstance(v, dict)}
        info["lanes"] = summ
    except (OSError, ValueError):
        pass
    # Nightly 21:10 local; allow a missed night + margin before calling stall.
    if age_h > 50:
        return "fail", f"STALE: latest quota receipt {latest.name} is {age_h:.0f}h old", info
    if age_h > 26:
        return "warn", f"latest quota receipt {age_h:.0f}h old (nightly job may have missed)", info
    return "ok", f"latest {latest.name} ({age_h:.1f}h ago)", info


def check_jobs() -> tuple[str, str, dict]:
    jobs = live_jobs()
    states = launchctl_states()
    if states is None:
        return "warn", "launchctl list unavailable", {}
    info = {"exit": {j: states[j][1] for j in jobs if j in states},
            "running": [j for j in jobs if j in states and states[j][0] != "-"]}
    missing = [j for j in jobs if j not in states]
    # A running job's exit column is its previous run; held-review exit 3 has
    # its own alert (check_held_review).
    bad = {j: states[j][1] for j in jobs if j in states and states[j][0] == "-"
           and states[j][1] not in ("0", "-") and not (j == HELD_REVIEW and states[j][1] == "3")}
    if missing:
        return "fail", f"jobs not loaded: {', '.join(missing)}", info
    if bad:
        detail = ", ".join(f"{j.split('.')[-1]}={c}" for j, c in bad.items())
        return "warn", f"nonzero last exit: {detail}", info
    return "ok", f"all {len(jobs)} fathers jobs loaded, last exit 0", info


def check_held_review() -> tuple[str, str, dict]:
    """run-held-review.sh exits 3 when headless Claude is not signed in on
    the Mini, so held sections pile up unreviewed until someone notices."""
    pid, code = (launchctl_states() or {}).get(HELD_REVIEW, ("-", None))
    info = {"last_exit": code}
    # launchctl keeps the scheduled run's exit; a later manual run (logged as
    # "held review exit N" or "manual run exit N") is the newer truth. But a
    # launchd exit other than 0 or 3 (75 busy, 1 early cd failure, a kill
    # before the wrapper's echo) comes from a run that wrote no exit line, so
    # it is newer than the log and wins.
    try:
        text = (LOGS / "fathers-held-review.out.log").read_text(encoding="utf-8", errors="replace")
        logged = re.findall(r"^(?:.*held review|manual run) exit (\d+)\s*$", text, re.M)
    except OSError:
        logged = []
    if logged:
        info["log_last_exit"] = logged[-1]
        if code in (None, "-", "0", "3"):
            code = logged[-1]
    if code == "3":
        return "fail", "weekly held review could not run: Claude not signed in on Mini (last exit 3)", info
    if code not in (None, "0", "-"):
        return "warn", f"held review last exit {code}", info
    return "ok", f"held review last exit {code}", info


def check_holds() -> tuple[str, str, dict]:
    if overnight_retired():
        # Holds now live in the recert queue (held_review.py releases them).
        held = sum(1 for v in load_queue().values() if v.get("result") == "held")
        return "ok", f"{held} works held in the recert queue", {"queue_held": held}
    p = REPO / "outputs/overnight-quota/HOLD.jsonl"
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "warn", "HOLD.jsonl unreadable", {}
    open_holds = []
    fresh_cutoff = time.time() - 48 * 3600
    for line in lines[-200:]:
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("cleared", False):
            continue
        try:
            upd = datetime.fromisoformat(str(o.get("updated", ""))).timestamp()
        except ValueError:
            upd = 0
        open_holds.append((o.get("claim", "?"), upd))
    fresh = [c for c, u in open_holds if u >= fresh_cutoff]
    info = {"open_total": len(open_holds), "open_fresh_48h": fresh}
    if len(fresh) > 5:
        return "warn", f"{len(fresh)} fresh holds in 48h (newest: {fresh[-1]})", info
    return "ok", f"{len(open_holds)} uncleared ({len(fresh)} fresh)", info


def expected_lanes() -> int:
    """Lane count from run-recert-lanes.sh (`for n in 1 2; do lane C$n ...`)."""
    try:
        src = (REPO / "scripts/run-recert-lanes.sh").read_text(encoding="utf-8")
    except OSError:
        return 6
    n = sum(len(m.split()) for m in re.findall(r"^for n in ([0-9 ]+); do lane ", src, re.M))
    return n or 6


def check_lanes() -> tuple[str, str, dict]:
    alive = []
    for f in sorted(WP.glob("lane-*.pid")):
        try:
            os.kill(int(f.read_text().strip()), 0)
            alive.append(f.stem.removeprefix("lane-"))
        except (OSError, ValueError):
            pass
    want = expected_lanes()
    info = {"alive": alive, "expected": want, "paused": lanes_paused()}
    if info["paused"]:
        return "ok", f"lanes paused by owner; {len(alive)} finishing current work", info
    if not alive:
        return "fail", f"no recert lane running (expected {want})", info
    if len(alive) < want - 1:
        return "warn", f"only {len(alive)}/{want} lanes alive", info
    return "ok", f"{len(alive)}/{want} lanes alive", info


def check_progress() -> tuple[str, str, dict]:
    """Some lane finished a work (any result) in the last 3 h."""
    q = load_queue()
    ends = [local_ts(v.get("at", "")) for v in q.values() if v.get("result") not in (None, "running")]
    last = max(ends, default=0.0)
    age_h = (time.time() - last) / 3600 if last else None
    info = {"last_finish_h": None if age_h is None else round(age_h, 1),
            "results": dict(Counter(v.get("result") for v in q.values()))}
    if lanes_paused() or age_h is None:
        return "ok", "lanes paused" if lanes_paused() else "queue empty", info
    if age_h > 3:
        return "warn", f"no lane finished a work in {age_h:.0f} h", info
    return "ok", f"last work finished {age_h:.1f} h ago", info


def check_certified() -> tuple[str, str, dict]:
    """Works certified in the last CERT_WINDOW_H hours vs CERT_FLOOR."""
    cutoff = time.time() - CERT_WINDOW_H * 3600
    q = load_queue()
    n = sum(1 for v in q.values() if v.get("result") == "certified" and local_ts(v.get("at", "")) >= cutoff)
    info = {"certified_window": n, "window_h": CERT_WINDOW_H, "floor": CERT_FLOOR}
    if lanes_paused() or not q:
        return "ok", f"{n} certified in {CERT_WINDOW_H} h (lanes paused)", info
    if n < CERT_FLOOR:
        return "warn", f"{n} works certified in the last {CERT_WINDOW_H} h (floor {CERT_FLOOR})", info
    return "ok", f"{n} works certified in the last {CERT_WINDOW_H} h", info


def check_throttles() -> tuple[str, str, dict]:
    """429s counted by llm_bakeoff.rate_acquire in /tmp/vendor-rate."""
    total = 0
    for f in Path("/tmp/vendor-rate").glob("*.json"):
        try:
            total += int(json.loads(f.read_text() or "{}").get("throttles", 0))
        except (OSError, ValueError, TypeError):
            pass
    prev = prior_info("throttles").get("total")
    info = {"total": total}
    if isinstance(prev, int) and total - prev > 25:
        return "warn", f"429 throttles rose by {total - prev} since the last check", info
    return "ok", f"{total} throttles counted", info


def broker_stats() -> dict:
    with urllib.request.urlopen("http://127.0.0.1:8799/stats", timeout=5) as r:
        return json.loads(r.read())


def check_broker() -> tuple[str, str, dict]:
    try:
        st = broker_stats()
    except Exception:  # noqa: BLE001 - any failure means not answering
        return "warn", "batch broker not answering on 127.0.0.1:8799", {}
    errors = int(st.get("errors", 0) or 0)
    info = {"errors": errors, "pending_batches": st.get("pending_batches")}
    problems = []
    # A dead flusher still answers /stats: items sit queued with no batch in
    # flight (2026-10-06: 321 Kimi items queued 15 h, pending_batches 0).
    stuck = []
    for model, m in (st.get("models") or {}).items():
        if not isinstance(m, dict):
            continue
        age = m.get("oldest_queued_s") or 0
        if m.get("queued") and age > BROKER_STUCK_S and not m.get("pending_batches"):
            stuck.append(f"{model.split('/')[-1]} {m['queued']} queued {age / 3600:.1f} h")
    if stuck:
        info["stuck"] = stuck
        problems.append("batch broker queue not draining, no batch in flight (dead flusher?): " + ", ".join(stuck))
    if st.get("dead_threads"):
        problems.append("batch broker threads dead: " + ", ".join(map(str, st["dead_threads"])))
    prev = prior_info("broker").get("errors")
    if isinstance(prev, int) and errors - prev > 10:
        problems.append(f"batch broker errors rose by {errors - prev}")
    if problems:
        return "warn", "; ".join(problems)[:300], info
    return "ok", f"broker up, {errors} errors total", info


def check_audio() -> tuple[str, str, dict]:
    """Narration drain (com.saneapps.fathers-audio-next, every 15 min)."""
    now = time.time()
    log = LOGS / "fathers-audio-next.out.log"
    try:
        text = log.read_text(encoding="utf-8", errors="replace")
        age_h = (now - log.stat().st_mtime) / 3600
    except OSError:
        return "warn", "no audio drain log", {}
    rendered = sum(1 for line in text.splitlines() if line.startswith("rendered"))
    prev = prior_info("audio")
    audio_t = now if rendered != prev.get("rendered") else prev.get("audio_t", now)
    info: dict = {"rendered": rendered, "audio_t": audio_t, "log_age_h": round(age_h, 1)}
    problems = []
    # The drain writes at least one line every run (every 900 s, about 17 min
    # apart in practice), so two missed runs means it is unloaded or hung.
    if age_h * 3600 > DRAIN_SILENT_S:
        problems.append(f"audio drain log silent {age_h * 60:.0f} min (it runs every 15 min)")
    err = LOGS / "fathers-audio-next.err.log"
    try:
        if now - err.stat().st_mtime < 3600:
            tail = err.read_text(encoding="utf-8", errors="replace")[-4000:]
            # Since 2026-10-06 the drain logs item failures as timestamped
            # lines (counted from drain-status.json below). Only a traceback
            # after the last timestamped line is a crash; older ones are history.
            lines = tail.strip().splitlines()
            last_ts = max((i for i, ln in enumerate(lines) if re.match(r"\d{4}-\d\d-\d\dT", ln)), default=-1)
            if any(ln.startswith("Traceback") for ln in lines[last_ts + 1:]):
                problems.append("audio drain error: " + lines[-1][:160])
    except OSError:
        pass
    # Backlog by reason, written by build_audio.py --drain at the end of a run.
    # "backlog" is what the drain can render now; "waiting" (old voice, page not
    # English, drift, unmapped, retrying) never drains alone, so it does not
    # alarm here. Sentence drift alarms on its own id in check_audio_drift.
    try:
        d = json.loads((SITE / "outputs/audio/drain-status.json").read_text(encoding="utf-8"))
        counts = d.get("counts") if isinstance(d.get("counts"), dict) else d
        counts = {k: v for k, v in counts.items() if isinstance(v, int) and not isinstance(v, bool)}
        info["drain"] = counts
        if isinstance(d.get("waiting"), dict):
            info["drain_waiting"] = {k: v for k, v in d["waiting"].items() if isinstance(v, int)}
        backlog = d.get("backlog")
        if not isinstance(backlog, int) or isinstance(backlog, bool):
            backlog = sum(v for k, v in counts.items() if "fail" not in k)
        info["backlog"] = backlog
        if backlog and now - audio_t > 5400:
            problems.append(f"narration rendered nothing for 90 min with {backlog} items waiting")
        failed = sum(v for k, v in counts.items() if "fail" in k)
        if failed:
            problems.append(f"{failed} audio items failing")
    except (OSError, ValueError, AttributeError):
        pass
    if problems:
        return "warn", "; ".join(problems), info
    return "ok", f"drain ran {age_h:.1f} h ago, {rendered} renders logged", info


MISMATCH_RE = re.compile(r"^skip (\S+) (\S+): (?:audio does not match the page|sentence drift)", re.M)


def check_audio_drift() -> tuple[str, str, dict]:
    """Narration that no longer matches its page. Two current sources:
    drain-status.json "waiting.sentence_drift" (the last drain run), and the
    sections the last auto ship skipped with "audio does not match the page"
    in fathers-ship-auto.log. Kept apart from audio:drain so an open drift
    warning never hides a drain that stopped. Nothing re-renders these alone;
    the warning stays until someone re-reads them."""
    info: dict = {}
    try:
        d = json.loads((SITE / "outputs/audio/drain-status.json").read_text(encoding="utf-8"))
        n = (d.get("waiting") or {}).get("sentence_drift")
        if isinstance(n, int) and not isinstance(n, bool):
            info["drain_sentence_drift"] = n
            info["drain_generated"] = d.get("generated", "")
    except (OSError, ValueError, AttributeError):
        pass
    try:
        text = (LOGS / "fathers-ship-auto.log").read_text(encoding="utf-8", errors="replace")
        start = text.rfind("+ scripts/ship.sh")
        if start >= 0:
            info["ship_mismatch"] = len(set(MISMATCH_RE.findall(text[start:])))
    except OSError:
        pass
    problems = []
    if info.get("drain_sentence_drift"):
        problems.append(
            f"{info['drain_sentence_drift']} sections wait because the recording does not match the page (drain)")
    if info.get("ship_mismatch"):
        problems.append(f"last auto ship skipped {info['ship_mismatch']} sections: audio does not match the page")
    if problems:
        return "warn", "; ".join(problems) + "; they need a re-read", info
    if not info:
        return "ok", "no drain status or auto ship log to read", info
    return "ok", "narration matches the pages", info


SHELF_STEPS = ("build_ebooks.py", "build_audiobooks.py", "library_sync.py")


def ship_ps() -> str:
    """etime + command of a running scripts/ship.sh, or ''."""
    try:
        raw = subprocess.check_output(["ps", "-Ao", "etime,command"], text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return next((line.strip() for line in raw.splitlines() if "scripts/ship.sh" in line), "")


def shelf_ps() -> str:
    """etime + command of a running paid-shelf step (ebooks, audiobooks,
    Word/assemble/upload), or ''. The auto ship runs these after a ship."""
    try:
        raw = subprocess.check_output(["ps", "-Ao", "etime,command"], text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return next((line.strip() for line in raw.splitlines()
                 if any(f"scripts/{s}" in line for s in SHELF_STEPS) and "bash -c" not in line), "")


def etime_secs(ps_line: str) -> int:
    """ps etime ([[dd-]hh:]mm:ss, the first field) in seconds."""
    parts = [int(x) for x in re.split(r"[-:]", ps_line.split()[0]) if x.isdigit()]
    return sum(v * m for v, m in zip(reversed(parts), (1, 60, 3600, 86400)))


def ship_lock_holders() -> list[str]:
    try:
        r = subprocess.run(["lsof", "-t", str(SITE / "outputs/ship.lock")],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return []
    return r.stdout.split()


def check_ship() -> tuple[str, str, dict]:
    problems, info = [], {}
    ship = ship_ps()
    if ship:
        secs = etime_secs(ship)
        info["ship_secs"] = secs
        if secs > 4 * 3600:
            problems.append(f"a ship has run {secs // 3600} h (slow upload?)")
    shelf = shelf_ps()
    if shelf:
        info["shelf"] = next((s for s in SHELF_STEPS if s in shelf), "?")
        info["shelf_secs"] = etime_secs(shelf)
    # A process left holding the ship lock with no ship running blocks every
    # later ship (2026-10-03: an orphaned check_links.py from a stopped ship).
    holders = ship_lock_holders()
    if holders and not ship:
        problems.append("ship lock held with no ship running (orphan pid " + ",".join(holders) + ")")
    # Hand-run ships log to outputs/ship-*.log; the auto ship's result is in
    # its state.json (check_ship_auto), not in these files.
    logs = sorted((SITE / "outputs").glob("ship-*.log"), key=lambda f: f.stat().st_mtime)[-1:]
    for lg in logs:
        if time.time() - lg.stat().st_mtime < 1800 and not ship:
            tail = lg.read_text(encoding="utf-8", errors="replace")[-4000:]
            hits = re.findall(r"(BLOCKED[^\n]*|AssertionError[^\n]*|FAILED[^\n]*)", tail)
            if hits and "SHIP OK" not in tail:
                problems.append(f"ship problem in {lg.name}: {hits[-1][:160]}")
    if problems:
        return "warn", "; ".join(problems), info
    if ship:
        return "ok", "ship running", info
    if shelf:
        return "ok", f"paid shelf running: {info['shelf']} for {info['shelf_secs'] // 60} min", info
    return "ok", "no ship running", info


def check_beliefs() -> tuple[str, str, dict]:
    """Nightly beliefs map (run-doctrine-map.sh, 03:30): any FAILED step in
    its last run. It exited 0 through two nights of BLOCKED grading."""
    log = LOGS / "fathers-beliefs.log"
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
    except OSError:
        return "warn", "no beliefs log", {}
    # Age from the last real line, not the file time: a BUSY line from a tick
    # that found the lock held is not a run.
    real = [ts for ts, line in timed_lines(log) if not BUSY_RE.match(line)]
    age_h = (time.time() - (real[-1] if real else log.stat().st_mtime)) / 3600
    starts = [i for i, line in enumerate(lines) if re.match(r"\d\d:\d\d:\d\d index$", line)]
    start = starts[-1] if starts else 0
    while start > 0 and re.match(r"\d\d:\d\d:\d\d receipt ", lines[start - 1]):
        start -= 1  # receipt refresh lines belong to the same run
    failed = [line[9:] for line in lines[start:] if re.match(r"\d\d:\d\d:\d\d (receipt FAILED|\w+ FAILED)", line)]
    # A step killed mid-run (2026-10-06: disk full) leaves a traceback and no
    # FAILED line; name the step it died in.
    if not failed and any(line.startswith("Traceback") for line in lines[start:]):
        steps = [line[9:] for line in lines[start:] if re.match(r"\d\d:\d\d:\d\d (index|search|grade|report)$", line)]
        failed = [f"{steps[-1] if steps else 'a step'} crashed (traceback, no exit line)"]
    info = {"log_age_h": round(age_h, 1), "failed": failed}
    if failed:
        return "warn", "beliefs map last run: " + "; ".join(failed)[:200], info
    if age_h > 26:
        return "warn", f"beliefs job has not run in {age_h:.0f} h", info
    return "ok", f"last run clean ({age_h:.0f} h ago)", info


def check_recert() -> tuple[str, str, dict]:
    """Recert tick log: ticking, receipts refreshing, status site deploying."""
    log = LOGS / "fathers-recert.out.log"
    tl = timed_lines(log)
    if not tl:
        return "warn", "no recert tick log", {}
    now = time.time()
    problems = []
    real = [ts for ts, line in tl if not BUSY_RE.match(line)]  # a BUSY tick did no work
    age_min = (now - (real[-1] if real else tl[0][0])) / 60
    if age_min > 75:
        problems.append(f"recert tick log silent {age_min:.0f} min")
    # A refresh is retried every tick; one failure is noise, two in a row
    # within the last 4 h means lanes lose that model when its receipt expires.
    last2: dict[str, list[str]] = {}
    for ts, line in tl:
        m = re.match(r"\S+ receipt (refreshed|FAILED) (\S+)", line)
        if m and now - ts < 4 * 3600:
            last2.setdefault(m[2], []).append(m[1])
    stuck = [k for k, v in last2.items() if v[-2:] == ["FAILED", "FAILED"]]
    if stuck:
        problems.append("receipt FAILED twice in a row: " + ", ".join(stuck))
    deploys = [(ts, line) for ts, line in tl if " status site " in line]
    if deploys and now - deploys[-1][0] < 2 * 3600 and "deploy FAILED" in deploys[-1][1]:
        problems.append("status site deploy FAILED")
    info = {"last_tick_min": round(age_min), "receipts": {k: v[-1] for k, v in last2.items()}}
    if problems:
        return "warn", "; ".join(problems), info
    return "ok", f"last tick {age_min:.0f} min ago", info


def check_redraft() -> tuple[str, str, dict]:
    """Same section redrafted REDRAFT_LIMIT+ times in one run ('source changed
    since it passed'): a lane looping on its own output, spending calls."""
    cutoff = time.time() - 24 * 3600
    loops = []
    for runlog in WP.glob("*/run.log"):
        try:
            if runlog.stat().st_mtime < cutoff:
                continue
            lines = runlog.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        starts = [i for i, line in enumerate(lines) if " start: " in line]
        c = Counter(m[1] for line in lines[starts[-1] if starts else 0:]
                    if (m := re.match(r"\S+ (.+): source changed since it passed", line)))
        hits = {sec: n for sec, n in c.items() if n >= REDRAFT_LIMIT}
        if hits:
            loops.append({"book": runlog.parent.name, "sections": hits})
    loops.sort(key=lambda x: x["book"])
    info = {"loops": loops}
    if loops:
        books = ", ".join(f"{x['book']} ({len(x['sections'])} sections, up to x{max(x['sections'].values())})"
                          for x in loops)
        return "warn", f"same section redrafted {REDRAFT_LIMIT}+ times in one run: {books}"[:300], info
    return "ok", "no redraft loops in the last 24 h", info


def check_e2e() -> tuple[str, str, dict]:
    p = SITE / "outputs/e2e/LATEST.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "fail", "no e2e receipt yet (no e2e proof exists)", {}
    age_h = (time.time() - p.stat().st_mtime) / 3600
    info = {"rc": d.get("rc"), "live_works": d.get("live_works"),
            "age_h": round(age_h, 1)}
    if age_h > 50:
        return "fail", f"STALE: e2e receipt {age_h:.0f}h old", info
    if d.get("rc") != 0:
        # fathers_e2e.sh names the failing gate line and keeps the full log.
        what = d.get("failed") or d.get("tail", "")
        where = f" (log {d['log']})" if d.get("log") else ""
        return "fail", f"e2e RED rc {d.get('rc')}: {str(what)[:200]}{where}", info
    return "ok", f"e2e green, {d.get('live_works')} works ({age_h:.1f}h ago)", info


def check_logos_lock() -> tuple[str, str, dict]:
    p = REPO / "outputs/logos_build.lock"
    if not p.exists():
        return "ok", "no logos lock held", {}
    try:
        pid = int(p.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return "warn", "logos lock unreadable", {}
    age_min = (time.time() - p.stat().st_mtime) / 60
    try:
        os.kill(pid, 0)
        alive = True
    except (OSError, ValueError):
        alive = False
    info = {"pid": pid, "alive": alive, "age_min": round(age_min, 1)}
    if alive:
        return "ok", f"logos build running (pid {pid})", info
    if age_min > 30:
        return "fail", f"STALE logos lock: pid {pid} dead, {age_min:.0f} min old", info
    return "warn", f"logos lock pid {pid} dead, {age_min:.0f} min old (watching)", info


def check_disk() -> tuple[str, str, dict]:
    # Absolute GB, not percent: APFS snapshot/purgeable accounting makes
    # percentages meaningless. One floor, measured the way the auto ship
    # measures it: under MIN_FREE_GB ships, site builds and e2e stop.
    free_g = autoship.free_gb()
    floor = autoship.MIN_FREE_GB
    info = {"free_gb": free_g, "floor_gb": floor}
    if free_g < 4:
        return "fail", f"disk free {free_g} GB (<4 GB; jobs will die)", info
    if free_g < floor:
        return "warn", f"disk free {free_g} GB (<{floor} GB: ships, site builds and e2e skip)", info
    return "ok", f"disk free {free_g} GB", info


def check_queue_depth() -> tuple[str, str, dict]:
    """Informational backlogs (never alert alone)."""
    info: dict = {}
    try:
        d = json.loads((REPO / "outputs/corrections-open.json").read_text())
        info["jev_open"] = len(d.get("open", []))
    except (OSError, ValueError):
        info["jev_open"] = "?"
    return "ok", f"jev corrections open: {info['jev_open']}", info


def check_ship_auto() -> tuple[str, str, dict]:
    """P16 (2026-10-06): certified text, audio or library changes waiting for
    the change-gated auto ship longer than 6 h."""
    path = REPO / "outputs/ship-auto/state.json"
    try:
        st = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return "ok", "auto ship has not run yet", {}
    since = st.get("pending_since")
    last_run = st.get("last_run") or {}
    shelf = st.get("shelf_pending") or {}
    # Recompute what the auto ship would see now, so edits made since its
    # last run are not reported as "site matches".
    now = autoship.inputs()
    waiting = [k for k in now if now[k] != (st.get("shipped") or {}).get(k)]
    info = {"pending_since": since, "pending": st.get("pending"), "waiting_now": waiting,
            "last_skip": st.get("last_skip"), "last_ship": st.get("last_ship"),
            "last_run": last_run, "shelf_pending": shelf or None}
    problems = []
    if since and (time.time() - local_ts(since)) / 3600 > autoship.ALERT_HOURS:
        hours = (time.time() - local_ts(since)) / 3600
        why = last_run.get("why") or (st.get("last_skip") or {}).get("why") or "last ship did not verify"
        problems.append(f"{', '.join(st.get('pending') or [])} changes not shipped for {hours:.0f} h ({why})")
    elif last_run.get("exit") not in (None, 0, 75):
        problems.append(f"last auto ship exit {last_run.get('exit')} at {last_run.get('at')}: {last_run.get('why')}")
    if shelf.get("error"):
        problems.append(f"paid shelf refresh failed ({shelf['error']}); the next auto ship resumes it")
    elif shelf and (time.time() - local_ts(shelf.get("since", ""))) / 3600 > autoship.ALERT_HOURS \
            and not shelf_ps():
        problems.append(f"paid shelf pending since {shelf.get('since')} and not running")
    if last_run.get("at") and (time.time() - local_ts(last_run["at"])) / 3600 > 18:
        problems.append(f"auto ship has not run since {last_run['at']} (job unloaded?)")
    if problems:
        return "warn", "; ".join(problems)[:300], info
    if shelf:
        return "ok", f"paid shelf in progress (done: {', '.join(shelf.get('done') or []) or 'nothing yet'})", info
    if waiting:
        return "ok", f"{', '.join(waiting)} changed since the last auto ship; the next run ships it", info
    return "ok", "site matches certified work", info


CHECKS = {
    "watch": check_watch,
    "burn": check_burn,
    "quota": check_quota,
    "jobs": check_jobs,
    "held_review": check_held_review,
    "holds": check_holds,
    "lanes": check_lanes,
    "progress": check_progress,
    "certified": check_certified,
    "throttles": check_throttles,
    "broker": check_broker,
    "audio": check_audio,
    "audio_drift": check_audio_drift,
    "ship": check_ship,
    "ship_auto": check_ship_auto,
    "beliefs": check_beliefs,
    "recert": check_recert,
    "redraft": check_redraft,
    "e2e": check_e2e,
    "logos_lock": check_logos_lock,
    "disk": check_disk,
    "queue": check_queue_depth,
}

# check -> alert id when state != ok; severity is the check's state.
ALERTS = {
    "watch": "watch:gap",
    "burn": "burn:hung",
    "quota": "quota:stale",
    "jobs": "jobs:exit",
    "held_review": "held-review:claude",
    "holds": "holds:pileup",
    "lanes": "lanes:down",
    "progress": "pipeline:no-finish",
    "certified": "pipeline:few-certified",
    "throttles": "vendor:429",
    "broker": "broker:down",
    "audio": "audio:drain",
    "audio_drift": "audio:drift",
    "ship": "ship:problem",
    "ship_auto": "ship:pending",
    "beliefs": "beliefs:failed",
    "recert": "recert:tick",
    "redraft": "pipeline:redraft-loop",
    "e2e": "e2e:red",
    "logos_lock": "logos:stale-lock",
    "disk": "disk:low",
}


def self_heal(results: dict, prior: dict, heals: list[str]) -> None:
    prior_checks = (prior.get("checks") or {})
    # Hung burn twice in a row -> kill once via the sanctioned path.
    if (results["burn"]["state"] == "fail"
            and (prior_checks.get("burn") or {}).get("state") == "fail"):
        if not prior.get("healed_burn_hung"):
            rc = subprocess.run(
                [sys.executable, str(REPO / "scripts/fathers_overnight_health.py"),
                 "--kill"], capture_output=True, text=True, timeout=60).returncode
            heals.append(f"kill hung burn (rc={rc})")
    # PID-dead logos lock -> remove (logos_build.py has no stale detection).
    if results["logos_lock"]["state"] == "fail":
        p = REPO / "outputs/logos_build.lock"
        try:
            pid = int(p.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
        except (OSError, ValueError):
            try:
                p.unlink()
                heals.append(f"removed stale logos lock (pid {pid} dead)")
                results["logos_lock"] = {
                    "state": "ok", "detail": "stale lock cleared by watch",
                    "info": {"healed": True}}
            except OSError:
                pass


def take_lock() -> bool:
    """watch.lock is a directory holding "pid" = "<pid> <start epoch>". A lock
    whose holder is no longer a watch pass (pid gone, pid reused by another
    program after a reboot, old empty lock, or older than WATCH_HARD_LIMIT_S)
    is taken over and noted in watch:gap. A live one means another pass is
    running: exit 75, and if it is stuck the Air notifier sees status.json go
    stale."""
    global LOCK_NOTE
    LOCK_NOTE = ""
    try:
        RUN_LOCK.mkdir()
    except FileExistsError:
        try:
            pid_s, start_s = (RUN_LOCK / "pid").read_text().split()[:2]
            pid, start = int(pid_s), int(start_s)
        except (OSError, ValueError):
            pid, start = 0, int(RUN_LOCK.stat().st_mtime)
        age_min = int((time.time() - start) // 60)
        if autoship.lock_holder_live(pid, start, "fathers_watch.py", WATCH_HARD_LIMIT_S):
            print(f"BUSY: watch pass pid {pid} has run {age_min} min; exit 75")
            return False
        LOCK_NOTE = (f"took over a watch lock left by pid {pid or '?'} ({age_min} min old; "
                     "gone, another program, or past the 30 min limit)")
        for f in RUN_LOCK.iterdir():
            f.unlink()
        RUN_LOCK.rmdir()
        try:
            RUN_LOCK.mkdir()
        except FileExistsError:
            return False
    (RUN_LOCK / "pid").write_text(f"{os.getpid()} {int(time.time())}\n")
    return True


def main() -> int:
    global PRIOR
    OUT.mkdir(parents=True, exist_ok=True)
    if not take_lock():
        return 75
    try:
        prior = PRIOR = load_prior()
        launchctl_states.cache_clear()
        prior_alerts = {a["id"]: a for a in (prior.get("alerts") or [])}
        results: dict = {}
        for name, fn in CHECKS.items():
            try:
                state, detail, info = fn()
            except Exception as exc:  # noqa: BLE001 - one bad check must not kill the pass
                state, detail, info = "warn", f"check error: {exc}", {}
            results[name] = {"state": state, "detail": detail, "info": info}
        heals: list[str] = []
        try:
            self_heal(results, prior, heals)
        except Exception as exc:  # noqa: BLE001 - heal failure is itself data
            heals.append(f"heal error: {exc}")
        now = now_iso()
        alerts = []
        for name, aid in ALERTS.items():
            if results[name]["state"] != "ok":
                first = (prior_alerts.get(aid) or {}).get("first_seen", now)
                alerts.append({"id": aid, "severity": results[name]["state"],
                               "text": results[name]["detail"],
                               "first_seen": first})
        overall = "ok"
        if any(a["severity"] == "fail" for a in alerts):
            overall = "fail"
        elif alerts:
            overall = "warn"
        tmp = STATUS.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({
            "checked_at": now, "overall": overall, "checks": results,
            "alerts": alerts, "heals": heals,
            "healed_burn_hung": results["burn"]["state"] != "ok" and (
                bool(prior.get("healed_burn_hung"))
                or any("kill hung burn" in h for h in heals)),
        }, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, STATUS)  # the Air notifier never reads a half file
        # alerts.log records transitions only (it grew to 209 KB by
        # re-logging the same two alerts every pass until 2026-10-06).
        current = {a["id"] for a in alerts}
        lines = [f"{now} {a['severity']} {a['id']} {a['text']}" for a in alerts if a["id"] not in prior_alerts]
        lines += [f"{now} cleared {aid}" for aid in prior_alerts if aid not in current]
        lines += [f"{now} heal {h}" for h in heals]
        if lines:
            with ALERTS_LOG.open("a", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
        print(f"watch: {overall} ({len(alerts)} alerts, {len(heals)} heals)")
        return 0
    finally:
        try:
            (RUN_LOCK / "pid").unlink()
            RUN_LOCK.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
