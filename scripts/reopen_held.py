#!/usr/bin/env python3
"""Reopen held sections of one finish-list book so a lane redoes them (2026-10-18).

Stephan, 2026-10-18 via Chief of Staff: work the held books on finish_only.json
through their section fixes the normal way so the lanes have work again. A
section held after its two retries stays held for a person (work_pipeline
process_section). This is that person's re-queue, done the way
regate_held.py reopens a section: <id>.json -> <id>.gatehold.json (kept for
audit), its .retries deleted, the book's queue row set to 'reopened' with
attempts 0. The lane then redrafts the section and runs the full blind source
check, repairs, referee, whole-work read and certification. Nothing here
passes a section or writes English.

Kinds reopened (choose with --kinds):
  gate      held by section_gate ("gate: ...") after its retries
  fallback  passed only with the uncertified fallback model ("not a certified pass")
Never reopened: confirmed or unruled findings (held_review.py judges those),
"no locked source" and other permanent holds, and sections a held review kept.

Usage (Mini, translations root):
  python3 scripts/reopen_held.py --book SLUG [--kinds gate,fallback] [--dry-run]
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as W  # noqa: E402
from regate_held import ARCHIVED, archive_path  # noqa: E402

KINDS = {
    "gate": lambda j: str(j.get("_why", "")).startswith("gate:"),
    "fallback": lambda j: "not a certified pass" in str(j.get("_why", "")),
}


def kept_by_review(book: str) -> set[str]:
    """Section ids a held review judged and kept held (real without a usable fix, or unsure)."""
    out = set()
    for p in glob.glob(str(W.ROOT / "outputs/held-review/*/kept_held.json")):
        try:
            for k in json.loads(Path(p).read_text()):
                key, why = (k[0], k[1]) if isinstance(k, list) else (str(k), "")
                if key.startswith(book + "/") and why != "unjudged finding":
                    out.add(key.split("/", 1)[1])
        except (OSError, ValueError, IndexError):
            continue
    return out


def reopen(book: str, kinds: list[str], dry_run: bool) -> dict:
    allow = W.finish_only()
    if allow is not None and book not in allow:
        raise SystemExit(f"{book} is not on finish_only.json; lanes would not take it")
    if W._withheld(book):
        raise SystemExit(f"{book} is withheld by the site (FORCED_WITHHOLD); reopening cannot certify it")
    rows = W.update_log("", {}) if W.QUEUE_LOG.exists() else {}
    if W.prev_running(rows, book):
        raise SystemExit(f"{book}: a lane is running it; try later")
    kept = kept_by_review(book)
    pairs = W.load_pairs(book)
    opened, skipped_kept = [], []
    for p in pairs:
        f = W.STAGE / book / "sections" / f"{W.re.sub(r'[^A-Za-z0-9_.-]', '_', p['id'])}.json"
        if not f.exists() or ARCHIVED.search(f.name):
            continue
        try:
            j = json.loads(f.read_text())
        except ValueError:
            continue
        if j.get("_status") != "hold" or j.get("_permanent"):
            continue
        if not any(KINDS[k](j) for k in kinds):
            continue
        if p["id"] in kept or f.stem in kept:
            skipped_kept.append(f.stem)
            continue
        opened.append(f.stem)
        if not dry_run:
            f.rename(archive_path(f))
            tries = f.with_suffix(".retries")
            if tries.exists():
                tries.unlink()
    if opened and not dry_run:
        row = W.update_log(book, {}).get(book) or {}
        W.update_log(book, {**row, "result": "reopened", "attempts": 0,
                            "why": f"reopened {len(opened)} held sections ({','.join(kinds)}) for a lane redo"})
    return {"book": book, "reopened": opened, "skipped_kept": skipped_kept, "dry_run": dry_run}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--book", required=True)
    ap.add_argument("--kinds", default="gate,fallback")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    kinds = [k for k in a.kinds.split(",") if k]
    bad = [k for k in kinds if k not in KINDS]
    if bad:
        raise SystemExit(f"unknown kinds: {bad}")
    r = reopen(a.book, kinds, a.dry_run)
    print(json.dumps({**r, "reopened_n": len(r["reopened"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
