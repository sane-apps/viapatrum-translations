#!/usr/bin/env python3
"""Re-run section_gate offline on held sections; reopen the ones that pass now.

Why (efficiency sweep 2026-10-03): section_gate's old substring names test
held sections for 'Sion' inside 'vision' and similar. work_lint's whole-word,
case-sensitive names rule now does that job, so some gate holds were false.
Likewise the glossary banned-rendering gate (2026-10-03) now applies a ban only
where the section's source has the glossary's source term, and never to a phrase
another entry fixes or that renders a common source word present there ("the
soul" for Ἱερουσαλήμ, "two ways" in Barnabas); those holds reopen here too.
This re-gates every section held BY THE GATE (_why "gate: ...") with today's
section_gate and the work's resolved brief. No LLM call is made.

A section that now passes is reopened the way earlier reopen scripts did:
<id>.json -> <id>.gatehold.json (kept for audit), its .retries file deleted,
and the book's queue row set to result 'reopened' with attempts 0, so a lane
redoes it. Sections held for confirmed source problems, failed repairs or a
missing checker stay held: the gate is not what holds them.

Books a live lane is running right now are left alone.

Usage (Mini):
  python3 scripts/regate_held.py --dry-run
  python3 scripts/regate_held.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as W  # noqa: E402

ARCHIVED = re.compile(r"\.(?:gate)?hold\d*\.json$")


def held_by_gate(j: dict) -> bool:
    return j.get("_status") == "hold" and str(j.get("_why", "")).startswith("gate:")


def load_brief(book: str) -> dict | None:
    path = W.STAGE / book / "brief.json"
    if not path.exists():
        return None
    try:
        brief = json.loads(path.read_text())
    except ValueError:
        return None
    if W.resolve_terms(book, brief, quiet=True):
        return None  # open terms: the work cannot run yet; leave it
    return brief


def archive_path(p: Path) -> Path:
    dest = p.with_suffix(".gatehold.json")
    n = 2
    while dest.exists():
        dest = p.with_suffix(f".gatehold{n}.json")
        n += 1
    return dest


def regate(dry_run: bool, only: str = "") -> dict:
    rows = W.update_log("", {}) if W.QUEUE_LOG.exists() else {}
    stats = {"held_by_gate": 0, "still_fail": 0, "reopened": 0, "skipped_running": 0, "skipped_no_brief": 0,
             "books": []}
    for bdir in sorted(d for d in W.STAGE.iterdir() if (d / "sections").is_dir()):
        book = bdir.name
        if only and book != only:
            continue
        cands = []
        for f in sorted((bdir / "sections").glob("*.json")):
            if ARCHIVED.search(f.name):
                continue
            try:
                j = json.loads(f.read_text())
            except ValueError:
                continue
            if held_by_gate(j):
                cands.append((f, j))
        if not cands:
            continue
        stats["held_by_gate"] += len(cands)
        if W.prev_running(rows, book):
            stats["skipped_running"] += len(cands)
            continue
        brief = load_brief(book)
        if brief is None:
            stats["skipped_no_brief"] += len(cands)
            continue
        opened = []
        for f, j in cands:
            errs = W.section_gate(j, brief)
            if errs:
                stats["still_fail"] += 1
                continue
            opened.append(f)
            if not dry_run:
                f.rename(archive_path(f))
                tries = f.with_suffix(".retries")
                if tries.exists():
                    tries.unlink()
        if not opened:
            continue
        stats["reopened"] += len(opened)
        stats["books"].append({"book": book, "sections": [f.stem for f in opened]})
        if not dry_run:
            row = W.update_log(book, {}).get(book) or {}
            W.update_log(book, {**row, "result": "reopened", "attempts": 0})
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="report only; rename nothing, leave queue.json alone")
    ap.add_argument("--book", default="", help="only this book")
    a = ap.parse_args()
    st = regate(a.dry_run, a.book)
    for b in st["books"]:
        print(f"{'would reopen' if a.dry_run else 'reopened'} {b['book']}: {', '.join(b['sections'])}")
    print(json.dumps({k: v if k != "books" else len(v) for k, v in st.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
