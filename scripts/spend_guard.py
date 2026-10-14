#!/usr/bin/env python3
"""Daily Workers AI spending cap for every Via Patrum job (owner 2026-10-14:
"make sure theres no chance of credits burning. only useful work").

Spend is read from Cloudflare's GraphQL usage (aiInferenceAdaptiveGroups),
the same number the invoice uses, for the current UTC day (it resets at
8 PM ET). It counts the whole account, so lanes, narration and the beliefs
job share one cap. The read is free; it makes no inference call.

  spend_guard.py check       exit 0 under the cap, 10 over, 2 when usage is unknown
  spend_guard.py gate-lanes  for run-recert-lanes.sh: pauses lanes when over the
                             cap, lifts its own pause the next UTC day; exit 0 =
                             lanes may start, 1 = they may not
  spend_guard.py status      one line for people and fathers-watch

Cap: outputs/spend/cap.json {"usd": N}, else FATHERS_DAILY_CAP_USD, else 150.
On 2026-10-14 the real burn was about $388/day and the grant had about
$5,500 left, enough for two weeks; at $150/day it lasts about five.
Unknown usage counts as over for starting new work (fail closed), but does
not pause lanes that are already running.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SPEND = ROOT / "outputs" / "spend"
TODAY = SPEND / "today.json"
CAP_FILE = SPEND / "cap.json"
LANES = ROOT / "outputs" / "work-pipeline"
PAUSED = LANES / "lanes.paused"
RESTART = LANES / "lanes.restart"
DEFAULT_CAP_USD = 150.0
FREE_NEURONS = 10_000  # per day, free
USD_PER_1K_NEURONS = 0.011
LANE_SHARE = 0.8  # lanes stop at 80% of the cap so narration and beliefs keep the rest
BUDGET_TAG = "budget:"  # first word of a pause this script wrote; an owner pause has none

OVER, UNKNOWN, OK = 10, 2, 0


def cap_usd() -> float:
    try:
        return float(json.loads(CAP_FILE.read_text())["usd"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    try:
        return float(os.environ.get("FATHERS_DAILY_CAP_USD") or DEFAULT_CAP_USD)
    except ValueError:
        return DEFAULT_CAP_USD


def usd_of(neurons: int) -> float:
    return max(0, neurons - FREE_NEURONS) * USD_PER_1K_NEURONS / 1000


def read_usage() -> dict:
    """Today's spend, or {'error': ...}. Never raises."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_TOKEN")
    if not token:
        return {"error": "no Cloudflare token in the environment"}
    try:
        from overnight_quota import DEFAULT_ACCOUNT, neurons_today
        neurons = neurons_today(token, os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT)
    except (Exception, SystemExit) as e:  # noqa: BLE001 - a failed read is data, not a crash
        return {"error": f"{type(e).__name__}: {e}"[:300]}
    return {"neurons": neurons, "usd": round(usd_of(neurons), 2)}


def evaluate(usage: dict, cap: float, day: str) -> dict:
    row = {"date": day, "cap_usd": cap, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **usage}
    row["state"] = "unknown" if "error" in usage else ("over" if usage["usd"] >= cap else "ok")
    return row


def record(row: dict) -> None:
    SPEND.mkdir(parents=True, exist_ok=True)
    tmp = TODAY.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, indent=1))
    tmp.replace(TODAY)


def gate_lanes(row: dict) -> int:
    """Pause or un-pause the lanes for this row. Returns 0 when lanes may start."""
    pause = PAUSED.read_text().strip() if PAUSED.exists() else ""
    ours = pause.startswith(BUDGET_TAG)
    if row["state"] == "ok" and row["usd"] >= row["cap_usd"] * LANE_SHARE:
        row = {**row, "state": "over"}
    if row["state"] == "over":
        if not pause:
            PAUSED.write_text(f"{BUDGET_TAG} ${row['usd']:.0f} spent on {row['date']} (UTC), past the lanes' "
                              f"{LANE_SHARE:.0%} share of the ${row['cap_usd']:.0f} daily cap; "
                              "lanes resume after 00:00 UTC (8 PM ET)\n")
            RESTART.touch()  # running lanes exit between works
            print(f"spend: ${row['usd']:.2f} is past the lanes' share of ${row['cap_usd']:.0f}; lanes paused")
        return 1
    if ours and row["state"] == "ok":
        PAUSED.unlink(missing_ok=True)
        print(f"spend: ${row['usd']:.2f} of ${row['cap_usd']:.0f} today; budget pause lifted")
    if row["state"] == "unknown":
        print(f"spend: usage unknown ({row['error']}); no new lanes this tick")
        return 1
    return 1 if PAUSED.exists() else 0


def line(row: dict) -> str:
    if row.get("state") == "unknown":
        return f"spend unknown at {row.get('at')}: {row.get('error')}"
    return f"spend {row.get('date')}: ${row.get('usd', 0):.2f} of ${row.get('cap_usd', 0):.0f} cap ({row.get('state')})"


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "status":
        try:
            print(line(json.loads(TODAY.read_text())))
        except (OSError, ValueError):
            print("spend: no reading yet")
        return 0
    if cmd not in ("check", "gate-lanes"):
        print(__doc__)
        return 64
    row = evaluate(read_usage(), cap_usd(), datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    record(row)
    if cmd == "gate-lanes":
        return gate_lanes(row)
    print(line(row))
    return {"ok": OK, "over": OVER}.get(row["state"], UNKNOWN)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
