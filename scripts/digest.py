#!/usr/bin/env python3
"""Render a 10am digest DRAFT from machine sources (agent verifies + sends).

Reads: newest dual summary, HOLD.jsonl, runner.log tail, THROUGHPUT.md,
ui-review status, latest independent-review report, corrections snapshot,
fathers HEAD. Prints <=15 lines. Never sends anything itself.
"""
from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
OUT = Path.home() / "SaneApps/outputs/fathers-overnight"


def newest_dual() -> dict:
    files = sorted(glob.glob(str(ROOT / "outputs/overnight-quota/*-dual.json")))
    if not files:
        return {}
    try:
        return json.loads(Path(files[-1]).read_text())
    except ValueError:
        return {"_file": files[-1], "_unparseable": True}


def holds() -> list:
    path = ROOT / "outputs/overnight-quota/HOLD.jsonl"
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def runner_tail() -> list[str]:
    log = OUT / "runner.log"
    if not log.is_file():
        return ["runner.log missing"]
    return log.read_text().splitlines()[-6:]


def ui_pending() -> str:
    try:
        proc = subprocess.run(["python3", str(SITE / "scripts/ui_review.py"), "status"],
                              capture_output=True, text=True, timeout=120)
        first = (proc.stdout or "").splitlines()
        return first[0].replace("build: ", "") if first else "unknown"
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def latest_indep() -> dict:
    files = sorted((ROOT / "outputs/independent-review").glob("*.json")) if (
        ROOT / "outputs/independent-review").is_dir() else []
    if not files:
        return {}
    try:
        return json.loads(files[-1].read_text())
    except ValueError:
        return {}


def corrections_count() -> int:
    path = ROOT / "outputs/corrections-open.json"
    if not path.is_file():
        return -1
    try:
        return len(json.loads(path.read_text()).get("open", []))
    except ValueError:
        return -1


def fathers_head() -> str:
    try:
        return subprocess.run(["git", "log", "--oneline", "-1"], cwd=SITE,
                              capture_output=True, text=True,
                              timeout=30, check=True).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def main() -> int:
    dual = newest_dual()
    lines = ["Fathers 10am digest (DRAFT - agent verifies before sending)"]
    for lane in ("cf", "nv"):
        entry = (dual.get("lanes") or {}).get(lane) or {}
        if not entry:
            continue
        done = sum(1 for c in entry.get("claims", []) if c.get("ok"))
        lines.append(
            f"- {lane}: stop={entry.get('stop_reason')} done={done} "
            f"held={entry.get('held_count', 0)} skips={entry.get('content_skips', 0)} "
            f"spent={entry.get('neurons_spent', '-')}/{entry.get('fathers_cf_budget', '-')}")
    lane_spent: dict = {}
    for lane in ("cf", "nv"):
        lane_entry = (dual.get("lanes") or {}).get(lane) or {}
        lane_spent.update(lane_entry.get("lane_spent") or {})
    if lane_spent:
        lines.append("- lane spend: " + ", ".join(f"{k}={v:,}" for k, v in sorted(lane_spent.items())))
    skipped = [c for lane in ("cf", "nv")
               for c in (((dual.get("lanes") or {}).get(lane) or {}).get("lane_skipped") or [])]
    if skipped:
        lines.append(f"- lane skips: {len(skipped)} paused-lane rows skipped")
    held = [h for h in holds() if h.get("held")]
    if held:
        lines.append(f"- holds: {len(held)} claims held "
                     f"({', '.join(sorted({str(h.get('claim', '?')) for h in held})[:6])})")
    tail = " | ".join(runner_tail()[-2:])
    lines.append(f"- runner: {tail[:160]}")
    indep = latest_indep()
    if indep:
        lines.append(f"- indep review {indep.get('week')}: "
                     f"{len(indep.get('mismatches', []))} confirmed, "
                     f"{len(indep.get('unconfirmed', []))} unconfirmed, "
                     f"{len(indep.get('escalated', []))} escalated")
    corr = corrections_count()
    if corr >= 0:
        lines.append(f"- corrections open: {corr}")
    lines.append(f"- site review gate: {ui_pending()}")
    lines.append(f"- fathers HEAD: {fathers_head()[:110]}")
    print("\n".join(lines[:15]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
