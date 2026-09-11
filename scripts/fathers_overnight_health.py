#!/usr/bin/env python3
"""Idle / healthy / hung for the Mini Fathers overnight burn.

  python3 scripts/fathers_overnight_health.py
  python3 scripts/fathers_overnight_health.py --kill   # only if hung

Hung = a burn child is alive and the overnight log has not grown for --stale-s
(default 900s, longer than NVIDIA urlopen 180s × retries).
Does not bootout the LaunchAgent. Does not free claims.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PATTERNS = ("overnight_quota.py", "draft_claim.py", "ai_promote.py", "fathers_run_lock.py")
LOG = Path.home() / "Library/Logs/SaneApps/fathers-overnight.out.log"
HEARTBEAT = Path.home() / "SaneApps/outputs/fathers-overnight/heartbeat"


def pgrep() -> list[tuple[int, str]]:
    raw = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
    out: list[tuple[int, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_s, _, cmd = line.partition(" ")
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        if any(p in cmd for p in PATTERNS) and "fathers_overnight_health" not in cmd:
            out.append((pid, cmd.strip()))
    return out


def log_age_s() -> float | None:
    ages = []
    for path in (LOG, HEARTBEAT):
        if path.is_file():
            ages.append(max(0.0, time.time() - path.stat().st_mtime))
    if not ages:
        return None
    return min(ages)


def last_log_line() -> str:
    if not LOG.is_file():
        return ""
    try:
        return LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-1][:200]
    except OSError:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-s", type=int, default=900)
    ap.add_argument("--kill", action="store_true")
    args = ap.parse_args()
    procs = pgrep()
    age = log_age_s()
    if not procs:
        print("IDLE no overnight/draft/promote process")
        return 0
    if age is None:
        print("HUNG process live, no overnight log")
        hung = True
    elif age > args.stale_s:
        print(f"HUNG log silent {int(age)}s (stale>{args.stale_s}s) procs={len(procs)}")
        hung = True
    else:
        print(f"HEALTHY log {int(age)}s ago procs={len(procs)}")
        hung = False
    print("last:", last_log_line())
    for pid, cmd in procs:
        print(f"  {pid} {cmd[:140]}")
    if hung and args.kill:
        for pid, _cmd in procs:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"SIGTERM {pid}")
            except ProcessLookupError:
                pass
        time.sleep(2)
        for pid, _cmd in pgrep():
            try:
                os.kill(pid, signal.SIGKILL)
                print(f"SIGKILL {pid}")
            except ProcessLookupError:
                pass
        print("killed hung children; LaunchAgent stays calendar-only")
        return 1
    return 1 if hung else 0


if __name__ == "__main__":
    raise SystemExit(main())
