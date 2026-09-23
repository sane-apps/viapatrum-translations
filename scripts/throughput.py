#!/usr/bin/env python3
"""Throughput accounting: nightly spend vs progress + site/tip velocity.

Reads outputs/overnight-quota/*-dual.json (14 days), ship commits from the
fathers repo, and tip landings from this repo. Writes docs/THROUGHPUT.md.
Re-run any time; the 10am digest reads the result.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
DAYS = 14


def git_log(repo: Path, since_days: int, fmt: str, *args: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", f"--since={since_days} days ago", f"--format={fmt}", *args],
            cwd=repo, capture_output=True, text=True, timeout=60, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return []
    return [line for line in out.splitlines() if line.strip()]


def nightly() -> dict:
    per_night: dict[str, dict] = defaultdict(
        lambda: {"runs": 0, "cf_spent": 0, "cf_done": 0, "cf_held": 0,
                 "cf_skips": 0, "nv_done": 0, "stops": defaultdict(int),
                 "lane_spent": defaultdict(int)})
    for path in sorted((ROOT / "outputs/overnight-quota").glob("*-dual.json")):
        day = path.name[:8]
        try:
            data = json.loads(path.read_text())
        except ValueError:
            continue
        night = per_night[day]
        night["runs"] += 1
        for lane in ("cf", "nv"):
            entry = (data.get("lanes") or {}).get(lane) or {}
            if entry.get("stop_reason") == "dry_run":
                continue
            if not entry.get("stop_reason") and not entry.get("claims") \
                    and not entry.get("neurons_spent"):
                continue
            night["stops"][f"{lane}:{entry.get('stop_reason', '?')}"] += 1
            night["cf_spent"] += int(entry.get("neurons_spent") or 0)
            night["cf_done"] += sum(1 for c in entry.get("claims", []) if c.get("ok"))
            night["cf_held"] += int(entry.get("held_count") or 0)
            night["cf_skips"] += int(entry.get("content_skips") or 0)
            for lname, spent in (entry.get("lane_spent") or {}).items():
                night["lane_spent"][lname] += int(spent or 0)
    return per_night


def site_velocity() -> dict:
    """day -> max live-sections from Ship commits (message: live 57/NNNN)."""
    vel: dict[str, int] = {}
    for line in git_log(SITE, DAYS, "%ci %s"):
        match = re.search(r"live \d+/(\d+)", line)
        if match:
            day = line[:10].replace("-", "")
            vel[day] = max(vel.get(day, 0), int(match.group(1)))
    return vel


def tip_velocity() -> dict:
    counts: dict[str, int] = defaultdict(int)
    for line in git_log(ROOT, DAYS, "%ci %s"):
        if "tip-ready" in line:
            counts[line[:10].replace("-", "")] += 1
    return counts


def main() -> int:
    nights = nightly()
    site = site_velocity()
    tips = tip_velocity()
    days = sorted(set(nights) | set(site) | set(tips))[-DAYS:]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_spent = sum(nights[d]["cf_spent"] for d in days if d in nights)
    total_done = sum(nights[d]["cf_done"] for d in days if d in nights)
    total_tips = sum(tips.get(d, 0) for d in days)
    site_days = sorted(site)
    site_growth = site[site_days[-1]] - site[site_days[0]] if len(site_days) >= 2 else 0

    md = ["# Throughput\n",
          f"Generated {now} by scripts/throughput.py (last {DAYS} days).\n",
          "## Overnight queue (CF neurons vs claims)\n",
          "| Night (UTC) | Runs | CF spent | Done | Held | Skips | N/done | Top stop |",
          "|---|---|---|---|---|---|---|---|"]
    for day in days:
        n = nights.get(day)
        if not n:
            md.append(f"| {day} | - | - | - | - | - | - | no runs |")
            continue
        per = f"{n['cf_spent'] // n['cf_done']:,}" if n["cf_done"] and n["cf_spent"] else "-"
        top = max(n["stops"].items(), key=lambda kv: kv[1])[0] if n["stops"] else "-"
        md.append(f"| {day} | {n['runs']} | {n['cf_spent']:,} | {n['cf_done']} | "
                  f"{n['cf_held']} | {n['cf_skips']} | {per} | {top} |")
    per_all = f"{total_spent // total_done:,}" if total_done else "-"
    md.append(f"\nTotals: {total_spent:,} neurons, {total_done} done "
              f"({per_all} N/done), {total_tips} tip landings, "
              f"+{site_growth} live site sections.\n")
    lane_totals: dict[str, int] = defaultdict(int)
    for day in days:
        for lname, spent in (nights.get(day) or {}).get("lane_spent", {}).items():
            lane_totals[lname] += spent
    if lane_totals:
        md.append("Work-lane spend (newer runs only): "
                  + ", ".join(f"{k}={v:,}" for k, v in sorted(lane_totals.items())))
    md.append("\n## Site + tip velocity\n")
    md.append("| Day | Live sections | Tips landed |")
    md.append("|---|---|---|")
    for day in days:
        md.append(f"| {day} | {site.get(day, '-')} | {tips.get(day, 0)} |")
    md.append("")
    (ROOT / "docs/THROUGHPUT.md").write_text("\n".join(md), encoding="utf-8")
    print(f"nights={len([d for d in days if d in nights])} spent={total_spent} "
          f"done={total_done} tips={total_tips} site_growth={site_growth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
