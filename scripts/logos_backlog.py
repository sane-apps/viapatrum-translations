#!/usr/bin/env python3
"""Regenerate docs/LOGOS_BACKLOG.md from live state (Logos DB + repo + receipts).

Read-only: never writes the Logos DB (safe to run while Logos is open).
Run: python3 scripts/logos_backlog.py
Also run automatically at the end of every scripts/logos_build.py run.
"""

import datetime
import glob
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pb_sync import resolve_pb_db, load_yml  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DOC = os.path.join(REPO, "docs", "LOGOS_BACKLOG.md")
UPLOAD_RECEIPTS = os.path.join(REPO, "outputs", "logos_uploads.json")


def load_uploads():
    try:
        with open(UPLOAD_RECEIPTS, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    db = resolve_pb_db()
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT Id,ResourceId,Title,LastCompiled,ModifiedDate,SyncState"
        " FROM Books WHERE IsDeleted=0 ORDER BY Id"
    ).fetchall()
    con.close()
    by_title = {}
    for r in rows:
        by_title.setdefault(r["Title"], []).append(r)

    uploads = load_uploads()
    compiled, pending_build, no_row, no_docx = [], [], [], []
    pattern = os.path.join(REPO, "books", "*", "book.yml")
    for yml_path in sorted(glob.glob(pattern)):
        slug = os.path.basename(os.path.dirname(yml_path))
        yml = load_yml(yml_path)
        title = yml.get("title", "")
        docx_name = yml.get("docx") or ""
        docx_path = os.path.join(REPO, "books", slug, docx_name)
        if not docx_name or not os.path.exists(docx_path):
            no_docx.append((slug, title))
            continue
        matches = by_title.get(title, [])
        if not matches:
            no_row.append((slug, title))
            continue
        for m in matches:
            rec = (slug, title, m["Id"], m["LastCompiled"] or "",
                   uploads.get(slug, ""))
            if m["LastCompiled"]:
                compiled.append(rec)
            else:
                pending_build.append(rec)

    stamp = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    L = []
    L.append("# Logos Personal Books backlog (generated - do not hand-edit)")
    L.append("")
    L.append("Regenerated: %s by scripts/logos_backlog.py from the live" % stamp)
    L.append("Mini PersonalBookManager.db + repo books/*/book.yml + upload receipts.")
    L.append("Pipeline: docs/LOGOS_PIPELINE.md. Driver: scripts/logos_build.py.")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("- Compiled in Logos: **%d**" % len(compiled))
    L.append("- Metadata row exists, never compiled: **%d**" % len(pending_build))
    L.append("- DOCX exists, no Logos row yet: **%d**" % len(no_row))
    L.append("- No DOCX (needs build_book.py or per-slice builder): **%d**"
             % len(no_docx))
    L.append("")
    L.append("## Compiled (title | book Id | LastCompiled | uploaded)")
    L.append("")
    for slug, title, bid, lc, up in sorted(compiled, key=lambda r: r[1]):
        L.append("- %s | Id %s | %s | %s" % (title, bid, lc, up or "NO RECEIPT"))
    L.append("")
    L.append("## Pending build (row exists, LastCompiled NULL)")
    L.append("")
    if pending_build:
        for slug, title, bid, _lc, _up in sorted(pending_build,
                                                key=lambda r: r[1]):
            L.append("- %s | %s | Id %s" % (slug, title, bid))
    else:
        L.append("- (none)")
    L.append("")
    L.append("## DOCX exists, no Logos row (pb_sync will INSERT on next build run)")
    L.append("")
    if no_row:
        for slug, title in sorted(no_row):
            L.append("- %s | %s" % (slug, title))
    else:
        L.append("- (none)")
    L.append("")
    L.append("## No DOCX (Logos-blocked until a builder exists)")
    L.append("")
    for slug, title in sorted(no_docx):
        L.append("- %s | %s" % (slug, title))
    L.append("")
    with open(OUT_DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("wrote %s: compiled=%d pending=%d no_row=%d no_docx=%d"
          % (OUT_DOC, len(compiled), len(pending_build), len(no_row),
             len(no_docx)))


if __name__ == "__main__":
    main()
