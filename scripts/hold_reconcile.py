#!/usr/bin/env python3
"""Clear stale HOLD rows for claims that are verifiably done.

Fail-closed: a row clears ONLY when docs/CLAIMS.md marks the claim done AND
its newest promote receipt says promoted+ok. Everything else is left byte-
identical. Cleared rows keep their fail history plus an audit trail.

Usage:
  hold_reconcile.py [--claim ID]   # dry run (default)
  hold_reconcile.py --apply        # write cleared rows
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOLD_PATH = os.path.join(ROOT, "outputs", "overnight-quota", "HOLD.jsonl")
CLAIMS_MD = os.path.join(ROOT, "docs", "CLAIMS.md")
RECEIPTS = os.path.join(ROOT, "outputs", "ai-promote")


def claim_status() -> dict:
    status = {}
    with open(CLAIMS_MD, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            cid = cells[0]
            if not cid or cid.lower().startswith("claim") or set(cid) <= {"-", " "}:
                continue
            status[cid] = cells[1].lower()
    return status


def newest_receipt(claim: str):
    cands = sorted(
        glob.glob(os.path.join(RECEIPTS, f"*-{claim}")), key=os.path.getmtime
    )
    if not cands:
        return None, "no receipt dir"
    summ = os.path.join(cands[-1], "summary.json")
    try:
        with open(summ, encoding="utf-8") as f:
            s = json.load(f)
    except (OSError, ValueError) as exc:
        return None, f"unreadable summary: {exc}"
    if s.get("ok") is True and s.get("verdict") == "promoted":
        return os.path.basename(cands[-1]), None
    return None, "receipt %s: %s/%s" % (os.path.basename(cands[-1]), s.get("verdict"), s.get("ok"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--claim", default=None)
    args = ap.parse_args()

    with open(HOLD_PATH, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f.read().splitlines() if l.strip()]
    status = claim_status()
    stamp = datetime.now(timezone.utc).isoformat()
    cleared, kept = [], []
    for row in rows:
        c = row.get("claim", "")
        if args.claim and c != args.claim:
            kept.append((c, "filtered out"))
            continue
        if not row.get("held"):
            kept.append((c, "not held"))
            continue
        if status.get(c) != "done":
            kept.append((c, f"board status={status.get(c, 'MISSING')}"))
            continue
        ev, why = newest_receipt(c)
        if not ev:
            kept.append((c, why))
            continue
        row["held"] = False
        row["cleared"] = stamp
        row["cleared_by"] = "hold_reconcile"
        row["clear_evidence"] = ev
        cleared.append(c)
    for c in cleared:
        print(f"CLEAR {c}")
    if args.apply:
        with open(HOLD_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r) for r in sorted(rows, key=lambda r: r.get("claim", ""))) + "\n")
        print(f"wrote {HOLD_PATH}: {len(cleared)} cleared, {len(kept)} kept")
    else:
        print(f"dry run: {len(cleared)} would clear, {len(kept)} kept")
        for c, why in kept:
            if why not in ("not held", "filtered out"):
                print(f"KEEP {c}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
