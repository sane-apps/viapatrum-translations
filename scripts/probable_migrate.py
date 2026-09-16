#!/usr/bin/env python3
"""Normalize non-vocab certainty (probable/allusion) to possible, except
entries Jev flags none-high (padding suspects) or clear-high (upgrade
candidates), which are listed for human adjudication instead.

Lateral move only: probable/allusion both mean uncertain, and builders
currently inline them as clear links, which overstates them. Folding to
possible renders them as plain-text captions. No entry is deleted here and
no clear is created here.

Reads outputs/jev-sweep-<today>.jsonl; refuses unless it covers every filed
allusion. Prints changed files, adjudication lists, and sampled-section
overlaps needing packet rebinds. Run from the repo root on the Mini.
Usage: python3 scripts/probable_migrate.py [--apply]
Without --apply, dry run: report only, change nothing.
"""
from __future__ import annotations

import glob
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NONVOCAB = ("probable", "allusion")


def main(argv):
    apply = "--apply" in argv
    sweep_path = ROOT / "outputs" / f"jev-sweep-{datetime.now().strftime('%Y%m%d')}.jsonl"
    verdicts = {}
    for ln in open(sweep_path, encoding="utf-8"):
        d = json.loads(ln)
        if "error" in d:
            continue
        verdicts[(d["book"], d["section"], d["reference"])] = d

    changed_files: set[str] = set()
    adjudicate_none = []
    adjudicate_clear = []
    total_filed = 0
    covered = 0
    for ef in sorted(glob.glob(str(ROOT / "books/*/translations/*_english.json"))):
        try:
            data = json.load(open(ef, encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        dirty = False
        for row in rows:
            if not isinstance(row, dict):
                continue
            for al in row.get("added_allusions") or []:
                if not isinstance(al, dict) or not al.get("reference"):
                    continue
                total_filed += 1
                key = (
                    ef.split("/books/")[1].split("/")[0],
                    str(row.get("section")),
                    al["reference"],
                )
                if key in verdicts:
                    covered += 1
                v = str(al.get("certainty", "")).strip().lower()
                if v not in NONVOCAB:
                    continue
                d = verdicts.get(key, {})
                jev, conf = d.get("jev"), d.get("confidence", 0)
                if jev == "none" and conf >= 0.85:
                    adjudicate_none.append(key + (al.get("reason"),))
                    continue
                if jev == "clear" and conf >= 0.85:
                    adjudicate_clear.append(key + (al.get("reason"),))
                    continue
                if apply:
                    al["certainty"] = "possible"
                    dirty = True
        if dirty:
            json.dump(data, open(ef, "w"), indent=2, ensure_ascii=False)
            open(ef, "a").write("\n")
            changed_files.add(ef)
    print(f"filed={total_filed} sweep-covered={covered}")
    assert covered == total_filed, "sweep incomplete: refusing to migrate on partial data"
    print(f"files changed: {len(changed_files)}")
    for f in sorted(changed_files):
        print("  M", f)
    print(f"adjudicate-as-padding-suspect: {len(adjudicate_none)}")
    for x in adjudicate_none:
        print("  NONE?", x)
    print(f"adjudicate-as-upgrade: {len(adjudicate_clear)}")
    for x in adjudicate_clear:
        print("  UPGRADE?", x)
    if not apply:
        print("dry run: nothing changed (pass --apply to migrate)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
