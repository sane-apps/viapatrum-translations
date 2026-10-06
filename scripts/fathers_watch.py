#!/usr/bin/env python3
"""Fathers Watch: one periodic health pass over the translation pipeline.

Runs every 15 min on the Mini via launchd (com.saneapps.fathers-watch).
Reads state, writes outputs/fathers-watch/status.json + alerts.log.
Self-heal is bounded and logged: kill a twice-confirmed hung burn child,
remove a PID-dead logos lock older than 30 min. Never touches gates,
never edits books, never ships.

Alerting is state-change based: an alert id appears once when a check
goes bad and disappears on recovery; alerts.log gets one line when an
alert appears and one when it clears. The Air notifier turns transitions
into user notifications.

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

WATCH_LABEL = "com.saneapps.fathers-watch"
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
    if code == "3":
        return "fail", "weekly held review could not run: Claude not signed in on Mini (last exit 3)", info
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
    prev = prior_info("broker").get("errors")
    if isinstance(prev, int) and errors - prev > 10:
        return "warn", f"batch broker errors rose by {errors - prev}", info
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
    if age_h > 4:
        problems.append(f"audio drain log silent {age_h:.0f} h")
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
    # English, drift, unmapped, retrying) never drains alone, so it never alarms.
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


def ship_ps() -> str:
    """etime + command of a running scripts/ship.sh, or ''."""
    try:
        raw = subprocess.check_output(["ps", "-Ao", "etime,command"], text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return next((line.strip() for line in raw.splitlines() if "scripts/ship.sh" in line), "")


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
        parts = [int(x) for x in re.split(r"[-:]", ship.split()[0]) if x.isdigit()]
        secs = sum(v * m for v, m in zip(reversed(parts), (1, 60, 3600, 86400)))
        info["ship_secs"] = secs
        if secs > 4 * 3600:
            problems.append(f"a ship has run {secs // 3600} h (slow upload?)")
    # A process left holding the ship lock with no ship running blocks every
    # later ship (2026-10-03: an orphaned check_links.py from a stopped ship).
    holders = ship_lock_holders()
    if holders and not ship:
        problems.append("ship lock held with no ship running (orphan pid " + ",".join(holders) + ")")
    logs = sorted((SITE / "outputs").glob("ship-*.log"), key=lambda f: f.stat().st_mtime)[-1:]
    for lg in logs:
        if time.time() - lg.stat().st_mtime < 1800:
            tail = lg.read_text(encoding="utf-8", errors="replace")[-4000:]
            hits = re.findall(r"(BLOCKED[^\n]*|AssertionError[^\n]*|FAILED[^\n]*)", tail)
            if hits and "SHIP OK" not in tail:
                problems.append(f"ship problem in {lg.name}: {hits[-1][:160]}")
    if problems:
        return "warn", "; ".join(problems), info
    return "ok", "ship running" if ship else "no ship running", info


def check_beliefs() -> tuple[str, str, dict]:
    """Nightly beliefs map (run-doctrine-map.sh, 03:30): any FAILED step in
    its last run. It exited 0 through two nights of BLOCKED grading."""
    log = LOGS / "fathers-beliefs.log"
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
        age_h = (time.time() - log.stat().st_mtime) / 3600
    except OSError:
        return "warn", "no beliefs log", {}
    starts = [i for i, line in enumerate(lines) if re.match(r"\d\d:\d\d:\d\d index$", line)]
    start = starts[-1] if starts else 0
    while start > 0 and re.match(r"\d\d:\d\d:\d\d receipt ", lines[start - 1]):
        start -= 1  # receipt refresh lines belong to the same run
    failed = [line[9:] for line in lines[start:] if re.match(r"\d\d:\d\d:\d\d (receipt FAILED|\w+ FAILED)", line)]
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
    age_min = (now - tl[-1][0]) / 60
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
        return "fail", f"e2e RED: {str(d.get('tail', ''))[:200]}", info
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
    # percentages meaningless. Pipeline jobs need ~2G headroom.
    st = os.statvfs(str(Path.home()))
    free_g = st.f_bavail * st.f_frsize / 1e9
    info = {"free_gb": round(free_g, 1)}
    if free_g < 4:
        return "fail", f"disk free {free_g:.1f}G (<4G)", info
    if free_g < 8:
        return "warn", f"disk free {free_g:.1f}G (<8G)", info
    return "ok", f"disk free {free_g:.1f}G", info


def check_queue_depth() -> tuple[str, str, dict]:
    """Informational backlogs (never alert alone)."""
    info: dict = {}
    try:
        d = json.loads((REPO / "outputs/corrections-open.json").read_text())
        info["jev_open"] = len(d.get("open", []))
    except (OSError, ValueError):
        info["jev_open"] = "?"
    return "ok", f"jev corrections open: {info['jev_open']}", info


CHECKS = {
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
    "ship": check_ship,
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
    "ship": "ship:problem",
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


def main() -> int:
    global PRIOR
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        RUN_LOCK.mkdir(exist_ok=False)
    except FileExistsError:
        print("watch already running, skip")
        return 0
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
            RUN_LOCK.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
