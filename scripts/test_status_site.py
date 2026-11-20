#!/usr/bin/env python3
"""Known-answer checks for the owner status page sections fixed 20 Nov 2026.

Run from the translations repo: python3 scripts/test_status_site.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_site as ss  # noqa: E402

FAILS = []


def check(name: str, ok: bool) -> None:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAILS.append(name)


def write(dirpath: Path, name: str, obj) -> Path:
    p = dirpath / name
    p.write_text(json.dumps(obj))
    return p


with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    scan = write(d, "latest.json", {"run": "2026-10-23 06:15", "drafter": "@cf/old/model-pick"})
    jobs_off = write(d, "jobs_off.json", {"mini": {"cf-scout": {"state": "off"}}})
    jobs_on = write(d, "jobs_on.json", {"mini": {"cf-scout": {"state": "on"}}})
    now = time.time()

    # 1. Job off: no "nightly" claim, old drafter pick hidden, real drafter shown.
    html_off = ss.scout_section(scan, drafter="@cf/real/drafter", jobs_path=jobs_off, now=now)
    check("job off: says the scan job is off", "the scan job is off" in html_off)
    check("job off: no 'nightly' claim", "nightly" not in html_off)
    check("job off: old scan drafter hidden", "model-pick" not in html_off)
    check("job off: real drafter shown", "@cf/real/drafter" in html_off)

    # 2. Job on but scan file three days old: treated as stale.
    os.utime(scan, (now - 72 * 3600, now - 72 * 3600))
    html_stale = ss.scout_section(scan, drafter="@cf/real/drafter", jobs_path=jobs_on, now=now)
    check("stale scan: says it has not run", "has not run in over two days" in html_stale)
    check("stale scan: old drafter hidden", "model-pick" not in html_stale)

    # 3. Job on, fresh scan: normal section, and still the real drafter, never the scan's pick.
    os.utime(scan, (now - 3600, now - 3600))
    html_fresh = ss.scout_section(scan, drafter="@cf/real/drafter", jobs_path=jobs_on, now=now)
    check("fresh scan: nightly line shown", "nightly at 06:15" in html_fresh)
    check("fresh scan: scan's drafter pick not shown as current", "model-pick" not in html_fresh)
    check("fresh scan: real drafter shown", "@cf/real/drafter" in html_fresh)

    # 4. Audio: the waiting counts appear beside the backlog counts.
    drain = write(d, "drain.json", {"counts": {"works_without_audio": 0, "stale_current_voice": 0, "failures": 12},
                                    "waiting": {"sentence_drift": 2379, "stale_old_voice": 2, "page_not_english": 3}})
    html_audio = ss.drain_section(drain)
    check("audio: 2,379 waiting sections shown", "2,379" in html_audio and "re-read" in html_audio)
    check("audio: failures still shown", "<b>12</b>" in html_audio)

print(f"{len(FAILS)} failed" if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
