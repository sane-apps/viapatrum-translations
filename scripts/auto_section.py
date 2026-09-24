#!/usr/bin/env python3
"""Autonomous section pipeline: draft → promote → revise → mark-done.

One claim in, one of three outcomes out:
  0 promoted (marked done, receipt written)
  1 hold (content dispute after N revise rounds; parked, never published)
  2 api failure (retryable; nothing written as done)

Each round runs the real CLIs (draft_claim, ai_promote) so receipts and
locks behave exactly as in manual runs. A Gemini accuracy grade runs after
a pass as an advisory audit only; it never gates promotion.

Usage:
  CF_TOKEN=... NV_API_KEY=... SANE_LLM_API_RECEIPT=... \\
    python3 scripts/auto_section.py --claim cyr-isa-x --agent overnight [--rounds 2]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIM_WALL_DEFAULT = 5400


def run(cmd: list[str], timeout: int) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def latest_receipt(claim: str) -> Path | None:
    cands = sorted(glob.glob(str(ROOT / "outputs/ai-promote" / f"*{claim}")))
    if not cands:
        return None
    summary = Path(cands[-1]) / "summary.json"
    return summary if summary.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--model", default="")
    ap.add_argument("--chunk-chars", type=int, default=0)
    ap.add_argument("--grade", action="store_true",
                    help="Run advisory Gemini grade after a pass")
    args = ap.parse_args()

    draft_cmd = [sys.executable, "scripts/draft_claim.py",
                 "--claim", args.claim, "--agent", args.agent]
    if args.model:
        draft_cmd += ["--model", args.model]
    if args.chunk_chars:
        draft_cmd += ["--chunk-chars", str(args.chunk_chars)]
    print(f"[auto] draft {' '.join(draft_cmd[2:])}", flush=True)
    rc, out = run(draft_cmd, CLAIM_WALL_DEFAULT)
    print(out[-1500:], flush=True)
    if rc != 0:
        print("[auto] HOLD: draft failed", flush=True)
        return 1

    api_retried = False
    for round_no in range(args.rounds + 1):
        promote_cmd = [sys.executable, "scripts/ai_promote.py",
                       "--claim", args.claim, "--agent", args.agent,
                       "--no-mark-done"]
        print(f"[auto] promote round {round_no}", flush=True)
        rc, out = run(promote_cmd, CLAIM_WALL_DEFAULT)
        print(out[-1500:], flush=True)
        if rc == 0:
            break
        if rc == 2 and not api_retried:
            print("[auto] promote API failure; one same-round retry", flush=True)
            api_retried = True
            rc, out = run(promote_cmd, CLAIM_WALL_DEFAULT)
            print(out[-1500:], flush=True)
        if rc == 0:
            break
        if rc == 2:
            print("[auto] API failure; retryable", flush=True)
            return 2
        if round_no >= args.rounds:
            print("[auto] HOLD: revise rounds exhausted", flush=True)
            return 1
        receipt = latest_receipt(args.claim)
        if receipt is None:
            print("[auto] HOLD: no receipt to revise from", flush=True)
            return 1
        revise_cmd = [sys.executable, "scripts/draft_claim.py",
                      "--claim", args.claim, "--agent", args.agent,
                      "--revise-from", str(receipt)]
        if args.model:
            revise_cmd += ["--model", args.model]
        print(f"[auto] revise from {receipt.name}", flush=True)
        rc, out = run(revise_cmd, CLAIM_WALL_DEFAULT)
        print(out[-1500:], flush=True)
        if rc != 0:
            print("[auto] revise failed; trying constrained redraft", flush=True)
            redraft_cmd = [sys.executable, "scripts/redraft_b.py",
                           "--claim", args.claim, "--agent", args.agent]
            if args.model:
                redraft_cmd += ["--model", args.model]
            rc, out = run(redraft_cmd, CLAIM_WALL_DEFAULT)
            print(out[-1500:], flush=True)
            if rc != 0:
                print("[auto] HOLD: revise failed", flush=True)
                return 1

    mark_cmd = [sys.executable, "scripts/ai_promote.py",
                "--claim", args.claim, "--agent", args.agent]
    print("[auto] mark done", flush=True)
    rc, out = run(mark_cmd, CLAIM_WALL_DEFAULT)
    print(out[-800:], flush=True)
    if rc != 0:
        print("[auto] HOLD: final mark failed", flush=True)
        return 1
    if args.grade:
        grade_cmd = [sys.executable, "scripts/accuracy_grade.py",
                     "--packet", os.environ.get("AUTO_GRADE_PACKET", ""),
                     "--out", str(ROOT / "outputs" / f"grade-{args.claim}.json"),
                     "--batch", "5", "--sleep", "5"]
        if grade_cmd[3]:
            print("[auto] advisory grade", flush=True)
            rc, out = run(grade_cmd, 900)
            print(out[-500:], flush=True)
    print("[auto] PROMOTED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
