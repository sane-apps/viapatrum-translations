#!/usr/bin/env python3
"""Report corpus chunk edges: rows ending mid-sentence/mid-word.

Cyril slices are size-cut, not sentence-cut, so most rows have chunk edges.
Draft and checker prompts tolerate honest edge fragments (see chunked_source
adapters); this report exists to size the backlog, not to demand rewrites.

Usage: python3 scripts/boundary_audit.py [--book SLUG]
Exit 0 + VIOLATIONS count line; one line per suspect boundary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from book_adapter import get_adapter  # noqa: E402

TERMINAL = set(".:;·…?!»”’'’\")]}")


def strip_markers(text: str) -> str:
    """Drop trailing footnote/page markers (6, 70.1) and closers before judging."""
    import re

    stripped = text.rstrip()
    stripped = re.sub(r"[\d.\s]+$", "", stripped).rstrip()
    return stripped


def terminal_ok(text: str) -> bool:
    stripped = strip_markers(text)
    return bool(stripped) and stripped[-1] in TERMINAL


def audit_cyril() -> list[str]:
    """Flag rows whose own tail lacks terminal punctuation (order-free).

    A flagged tail means the slice bleeds into whatever follows: no draft
    can satisfy completeness until a curator rejoins or trims the sentence.
    """
    adapter = get_adapter("cyril-alexandria-isaiah")
    index = adapter._source_index()
    problems = []
    for section in sorted(index):
        greek = index[section][2].get("greek") or ""
        tail = strip_markers(greek)
        if not tail or tail[-1] not in TERMINAL:
            kind = "ENDS_HYPHEN" if tail.endswith("-") else "ENDS_MID_SENTENCE"
            problems.append(f"{section} {kind} tail={' '.join(greek.split())[-80:]!r}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="cyril-alexandria-isaiah")
    args = ap.parse_args()
    if args.book != "cyril-alexandria-isaiah":
        print(f"boundary_audit supports only cyril-alexandria-isaiah, not {args.book}")
        return 2
    problems = audit_cyril()
    for line in problems:
        print(line, flush=True)
    print(f"CHUNK_EDGES {len(problems)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
