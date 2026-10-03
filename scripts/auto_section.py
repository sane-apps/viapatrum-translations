#!/usr/bin/env python3
"""Autonomous section pipeline: repair or draft, then promote, then mark done.

One claim in, one of three outcomes out:
  0 promoted (marked done, receipt written)
  1 hold (content dispute after the repair rounds; parked, never published)
  2 api or unreadable draft (retryable; nothing written as done)
  5 source is still betacode (skipped; not a failed translation)

A receipt that already passes is accepted without a second jury. A receipt
with a real defect is revised before any fresh draft, so a parked slice is
repaired instead of rewritten from scratch. Confabulated notes are dropped
inside draft_claim and do not churn the text.

Usage:
  CF_TOKEN=... NV_API_KEY=... SANE_LLM_API_RECEIPT=... \\
    python3 scripts/auto_section.py --claim cyr-isa-x --agent overnight [--rounds 2]
"""
from __future__ import annotations

import argparse
import glob
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


def receipt_needs_repair(claim: str) -> Path | None:
    path = latest_receipt(claim)
    if path is None:
        return None
    sys.path.insert(0, str(ROOT / "scripts"))
    from draft_claim import load_receipt_failures

    if load_receipt_failures(str(path)):
        return path
    return None


def _needs_fresh_draft(args) -> bool:
    """Scaffold English, betacode gloss, or missing lemmas cannot be revised."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from ai_promote import parse_claim_row, sections_from_slice
        from draft_claim import section_needs_fresh_draft

        row = parse_claim_row(args.claim)
        book = row.get("Book slug") or ""
        sections = sections_from_slice(row.get("Slice (sections)") or "", book)
        if not sections:
            return False
        return any(section_needs_fresh_draft(section, book) for section in sections)
    except (Exception, SystemExit) as exc:
        print("[auto] draft check failed: %s" % type(exc).__name__, flush=True)
        return False


def _unreadable_draft(out: str) -> bool:
    return (
        "chunk_draft_failed" in out
        or "parse_fail" in out
        or "chunk_tail_cut" in out
    )


def _draft(args) -> int:
    cmd = [sys.executable, "scripts/draft_claim.py",
           "--claim", args.claim, "--agent", args.agent]
    if args.model:
        cmd += ["--model", args.model]
    if args.chunk_chars:
        cmd += ["--chunk-chars", str(args.chunk_chars)]
    print("[auto] draft %s" % " ".join(cmd[2:]), flush=True)
    rc, out = run(cmd, CLAIM_WALL_DEFAULT)
    print(out[-1500:], flush=True)
    if rc == 0:
        return 0
    if _unreadable_draft(out):
        print("[auto] draft parse failed; retryable", flush=True)
        return 2
    return 1


def _revise(args, receipt: Path) -> int:
    cmd = [sys.executable, "scripts/draft_claim.py",
           "--claim", args.claim, "--agent", args.agent,
           "--revise-from", str(receipt)]
    if args.model:
        cmd += ["--model", args.model]
    print("[auto] revise from %s" % receipt.name, flush=True)
    rc, out = run(cmd, CLAIM_WALL_DEFAULT)
    print(out[-1500:], flush=True)
    if rc == 0:
        return 0
    if _unreadable_draft(out):
        print("[auto] revise parse failed; retryable", flush=True)
        return 2
    if ("Structural fail has no checker notes" in out
            or "missing_evidence_for_revision" in out):
        print("[auto] revise cannot repair this bundle; drafting", flush=True)
        return _draft(args)
    print("[auto] revise failed; trying constrained redraft", flush=True)
    redraft = [sys.executable, "scripts/redraft_b.py",
               "--claim", args.claim, "--agent", args.agent]
    if args.model:
        redraft += ["--model", args.model]
    rc, out = run(redraft, CLAIM_WALL_DEFAULT)
    print(out[-1500:], flush=True)
    if rc == 0:
        return 0
    if _unreadable_draft(out):
        print("[auto] redraft parse failed; retryable", flush=True)
        return 2
    return 1


def _hold_or_retry(code: int, label: str) -> int:
    if code == 2:
        return 2
    print(label, flush=True)
    return 1


def _grade(args) -> None:
    if not args.grade:
        return
    grade_cmd = [sys.executable, "scripts/accuracy_grade.py",
                 "--packet", os.environ.get("AUTO_GRADE_PACKET", ""),
                 "--out", str(ROOT / "outputs" / ("grade-%s.json" % args.claim)),
                 "--batch", "5", "--sleep", "5"]
    if not grade_cmd[3]:
        return
    print("[auto] advisory grade", flush=True)
    rc, out = run(grade_cmd, 900)
    print(out[-500:], flush=True)


def _source_not_greek(args) -> bool:
    """True when the locked slice is still betacode. Drafting it invents English."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from ai_promote import load_section_bundle, parse_claim_row, sections_from_slice
        from pipeline_autonomy import source_is_betacode

        row = parse_claim_row(args.claim)
        book = row.get("Book slug") or ""
        sections = sections_from_slice(row.get("Slice (sections)") or "", book)
        for section in sections:
            bundle = load_section_bundle(section, book)
            greek = bundle.get("greek") or ""
            if isinstance(greek, list):
                greek = " ".join(str(part) for part in greek)
            if source_is_betacode(greek):
                return True
    except (Exception, SystemExit) as exc:
        print("[auto] source check failed: %s" % type(exc).__name__, flush=True)
    return False


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

    def promote(no_mark: bool = False, accept: bool = False) -> tuple[int, str]:
        cmd = [sys.executable, "scripts/ai_promote.py",
               "--claim", args.claim, "--agent", args.agent]
        if no_mark:
            cmd.append("--no-mark-done")
        if accept:
            cmd.append("--accept-current")
        return run(cmd, CLAIM_WALL_DEFAULT)

    if _source_not_greek(args):
        print("[auto] source is not Unicode Greek; skipped", flush=True)
        return 5

    print("[auto] accept current", flush=True)
    rc, out = promote(accept=True)
    print(out[-800:], flush=True)
    if rc == 0:
        _grade(args)
        print("[auto] PROMOTED", flush=True)
        return 0

    if _needs_fresh_draft(args):
        print("[auto] bundle cannot be revised; drafting", flush=True)
        code = _draft(args)
        if code != 0:
            return _hold_or_retry(code, "[auto] HOLD: draft failed")
    else:
        repair = receipt_needs_repair(args.claim)
        if repair is not None:
            code = _revise(args, repair)
            if code != 0:
                return _hold_or_retry(code, "[auto] HOLD: revise failed")
        elif latest_receipt(args.claim) is None:
            code = _draft(args)
            if code != 0:
                return _hold_or_retry(code, "[auto] HOLD: draft failed")

    api_retried = False
    for round_no in range(args.rounds + 1):
        print("[auto] promote round %d" % round_no, flush=True)
        rc, out = promote(no_mark=True)
        print(out[-1500:], flush=True)
        if rc == 0:
            break
        if rc == 2 and not api_retried:
            print("[auto] promote API failure; one same-round retry", flush=True)
            api_retried = True
            rc, out = promote(no_mark=True)
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
        code = _revise(args, receipt)
        if code != 0:
            return _hold_or_retry(code, "[auto] HOLD: revise failed")

    print("[auto] accept current", flush=True)
    rc, out = promote(accept=True)
    print(out[-800:], flush=True)
    if rc != 0:
        print("[auto] mark done", flush=True)
        rc, out = promote()
        print(out[-800:], flush=True)
    if rc != 0:
        print("[auto] HOLD: final mark failed", flush=True)
        return 1
    _grade(args)
    print("[auto] PROMOTED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
