#!/usr/bin/env python3
"""Append-only audit log: what was done to each work, when, and the receipt.

Every tool that changes a work's text, checks it, records audio for it, or
ships it calls record(). One JSON line per event in
outputs/audit/events.jsonl, locked so parallel lanes never interleave.
The owner's status dashboard (scripts/status_site.py) is built from this log.

Event kinds (keep this list short and stable):
  certified   work passed the blind source check, intro and readers; applied
  held        work checked; some part still disputed (current text stays live)
  recheck     re-certification started for a work
  translated  new English drafted and certified for a work not yet live
  citation    Bible reference corrected in the text
  repair      damaged English repaired (fused words, stutter, lost text)
  title       public title changed
  audio       audio recorded or re-recorded
  shipped     site deployed (book "*" = whole library)
  note        anything else worth a line
"""
from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "outputs" / "audit" / "events.jsonl"
KINDS = {"certified", "held", "recheck", "translated", "citation", "repair", "title", "audio", "shipped", "note"}


def book_of(path: str) -> str:
    """Book slug from a books/<slug>/... path ('' when not a book file)."""
    parts = Path(path).parts
    return parts[parts.index("books") + 1] if "books" in parts and parts.index("books") + 1 < len(parts) else ""


def record(book: str, kind: str, summary: str, ref: str = "", when: str = "", **detail) -> dict:
    """Append one event. when defaults to now (local time, ISO)."""
    if kind not in KINDS:
        kind = "note"
    ev = {"at": when or time.strftime("%Y-%m-%dT%H:%M:%S"), "book": book, "kind": kind,
          "summary": summary[:400], "ref": ref, "by": os.environ.get("AUDIT_BY", "pipeline")}
    if detail:
        ev["detail"] = detail
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def events() -> list[dict]:
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out
