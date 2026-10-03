#!/usr/bin/env python3
"""Fathers Watch: one periodic health pass over the translation pipeline.

Runs every 15 min on the Mini via launchd (com.saneapps.fathers-watch).
Reads state, writes outputs/fathers-watch/status.json + alerts.log.
Self-heal is bounded and logged: kill a twice-confirmed hung burn child,
remove a PID-dead logos lock older than 30 min. Never touches gates,
never edits books, never ships.

Alerting is state-change based: an alert id appears once when a check
goes bad and disappears on recovery. The Air notifier turns transitions
into user notifications.
"""
from __future__ import annotations

import json
import os
import plistlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path.home() / "SaneApps/clients/translations"
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
OUT = REPO / "outputs/fathers-watch"
STATUS = OUT / "status.json"
ALERTS_LOG = OUT / "alerts.log"
RUN_LOCK = OUT / "watch.lock"

sys.path.insert(0, str(REPO / "scripts"))
import fathers_overnight_health as burnmod  # noqa: E402

JOBS = [
    "com.saneapps.fathers-overnight-quota",
    "com.saneapps.fathers-overnight-catchup",
    "com.saneapps.fathers-logos-build",
    "com.saneapps.fathers-independent-review",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_prior() -> dict:
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def check_burn() -> tuple[str, str, dict]:
    """IDLE / HEALTHY / HUNG via the existing burn module (no kill here)."""
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
    try:
        raw = subprocess.check_output(["launchctl", "list"], text=True,
                                      timeout=20)
    except (OSError, subprocess.SubprocessError):
        return "warn", "launchctl list unavailable", {}
    states = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] in JOBS:
            states[parts[2]] = parts[1]
    info = {"exit": states}
    bad = {j: c for j, c in states.items() if c != "0" and c != "-"}
    missing = [j for j in JOBS if j not in states]
    if missing:
        return "fail", f"jobs not loaded: {', '.join(missing)}", info
    if bad:
        detail = ", ".join(f"{j.split('.')[-1]}={c}" for j, c in bad.items())
        return "warn", f"nonzero last exit: {detail}", info
    return "ok", "all 4 fathers jobs loaded, last exit 0", info


def check_holds() -> tuple[str, str, dict]:
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
    "holds": check_holds,
    "e2e": check_e2e,
    "logos_lock": check_logos_lock,
    "disk": check_disk,
    "queue": check_queue_depth,
}

# check -> (alert id, severity) when state != ok
ALERTS = {
    "burn": ("burn:hung", "fail"),
    "quota": ("quota:stale", "fail"),
    "jobs": ("jobs:exit", "warn"),
    "holds": ("holds:pileup", "warn"),
    "e2e": ("e2e:red", "fail"),
    "logos_lock": ("logos:stale-lock", "fail"),
    "disk": ("disk:low", "fail"),
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
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        RUN_LOCK.mkdir(exist_ok=False)
    except FileExistsError:
        print("watch already running, skip")
        return 0
    try:
        prior = load_prior()
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
        for name, (aid, sev) in ALERTS.items():
            if results[name]["state"] != "ok":
                first = (prior_alerts.get(aid) or {}).get("first_seen", now)
                alerts.append({"id": aid, "severity": sev,
                               "text": results[name]["detail"],
                               "first_seen": first})
        overall = "ok"
        if any(a["severity"] == "fail" for a in alerts):
            overall = "fail"
        elif alerts:
            overall = "warn"
        STATUS.write_text(json.dumps({
            "checked_at": now, "overall": overall, "checks": results,
            "alerts": alerts, "heals": heals,
            "healed_burn_hung": results["burn"]["state"] != "ok" and (
                bool(prior.get("healed_burn_hung"))
                or any("kill hung burn" in h for h in heals)),
        }, indent=2) + "\n", encoding="utf-8")
        if alerts or heals:
            with ALERTS_LOG.open("a", encoding="utf-8") as fh:
                for a in alerts:
                    fh.write(f"{now} {a['severity']} {a['id']} {a['text']}\n")
                for h in heals:
                    fh.write(f"{now} heal {h}\n")
        print(f"watch: {overall} ({len(alerts)} alerts, {len(heals)} heals)")
        return 0
    finally:
        try:
            RUN_LOCK.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
