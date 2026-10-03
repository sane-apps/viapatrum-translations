#!/usr/bin/env python3
"""Mark done claims whose newest receipt already says promoted+ok.

Replays the sanctioned stamp+mark path (stamp_justifications, mark_claim_done
imported from ai_promote) WITHOUT re-burning models. Fail-closed: aborts a
claim unless its newest receipt is promoted+ok AND review_is_current passes
for every result entry (inputs unchanged since the receipt).

Usage:
  mark_verified_done.py --claim ID        # dry run (default)
  mark_verified_done.py --claim ID --apply
  mark_verified_done.py --batch SUBSTR --apply   # e.g. cyr-isa-book4
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ai_promote import (  # noqa: E402
    load_section_bundle,
    mark_claim_done,
    review_is_current,
    stamp_justifications,
)

RECEIPTS = ROOT / "outputs" / "ai-promote"


def newest_ok_receipt(claim: str):
    cands = sorted(glob.glob(str(RECEIPTS / f"*-{claim}")), key=os.path.getmtime)
    for d in reversed(cands):
        try:
            with open(os.path.join(d, "summary.json"), encoding="utf-8") as f:
                s = json.load(f)
        except (OSError, ValueError):
            continue
        if s.get("ok") is True and s.get("verdict") == "promoted":
            return Path(d), s
    return None, None


def claims_in_hold(batch: str | None):
    rows = [
        json.loads(line)
        for line in (
            ROOT / "outputs" / "overnight-quota" / "HOLD.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = [r["claim"] for r in rows if r.get("claim")]
    if batch:
        out = [c for c in out if batch in c]
    return sorted(set(out))


def process(claim: str, apply: bool) -> str:
    rdir, s = newest_ok_receipt(claim)
    if not rdir:
        return f"SKIP {claim}: no promoted+ok receipt"
    results = s.get("results") or []
    if not results:
        return f"SKIP {claim}: receipt has no results"
    try:
        for entry in results:
            bundle = load_section_bundle(entry["section"], entry.get("book"))
            if not review_is_current(bundle, entry, entry["draft_model"]):
                return f"SKIP {claim}: inputs drifted since {rdir.name}"
    except SystemExit as exc:
        return f"SKIP {claim}: {exc}"
    except (KeyError, OSError, ValueError) as exc:
        return f"SKIP {claim}: check error {exc!r}"
    models = []
    for entry in results:
        pair = f"{entry['checker_a']['model']}+{entry['checker_b']['model']}"
        if entry.get("arbiter"):
            pair += f"+arb:{entry['arbiter']['model']}"
        models.append(pair)
    grounded = "+grounded" if any(
        (e.get("grounding_override") or {}).get("overridden") for e in results
    ) else ""
    agent = s.get("agent") or "mark-verified"
    note = f"{models[0]}{grounded}; receipt {rdir.name} (verified-mark, no re-burn)"
    if not apply:
        return f"WOULD-MARK {claim} via {rdir.name}"
    stamp_justifications(results, rdir / "summary.json")
    mark_claim_done(claim, agent, note)
    return f"MARKED {claim} via {rdir.name}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", default=None)
    ap.add_argument("--batch", default=None)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    claims = [args.claim] if args.claim else claims_in_hold(args.batch)
    for claim in claims:
        print(process(claim, args.apply), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
