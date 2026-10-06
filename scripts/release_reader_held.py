#!/usr/bin/env python3
"""Release held works that pass every check except the old reader mean (P15).

Owner 2026-10-06: with reader edits off, nothing can raise a reader score, so
works whose sections all pass the blind source check, whose intro is clean and
whose readers all scored 3 or more certify on their STORED scores. No model
calls: status() reuses the last read and drops it when the text changed since.
Ignatius and Hermas stay parked (owner decision 2026-10-04). Books a lane is
running are skipped.

Usage: release_reader_held.py [--apply] [--only SLUG]
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.chdir(Path(__file__).resolve().parent.parent)
import work_pipeline as wp  # noqa: E402

APPLY = "--apply" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
PARKED_BY_OWNER = ("ignatius", "hermas", "shepherd")


def alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


rows = json.loads(wp.QUEUE_LOG.read_text())
out = {"apply": APPLY, "bar": wp.reader_bar(), "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
       "release": [], "kept": [], "skipped": []}
for book, row in sorted(rows.items()):
    if row.get("result") not in ("held", "running") or (ONLY and book != ONLY):
        continue
    if row.get("result") == "running" and alive(row.get("pid", 0)):
        out["skipped"].append({"book": book, "why": "lane running"})
        continue
    if any(k in book for k in PARKED_BY_OWNER):
        out["skipped"].append({"book": book, "why": "parked by owner"})
        continue
    st = wp.status(book)
    words = sum(len(" ".join(p["source"]).split()) for p in wp.load_pairs(book))
    secs = st.get("sections", {})
    if set(secs) != {"pass"} or not st.get("intro_ok"):
        continue  # held for real section or intro problems; not this script's job
    entry = {"book": book, "words": words, "followability": st.get("followability")}
    if not wp.follow_ok(st.get("followability"), words):
        out["kept"].append({**entry, "why": "reader below bar or no current read"})
        continue
    if APPLY:
        rc = wp.apply(book)
        entry["apply_rc"] = rc
        if rc == 0:
            wp.update_log(book, {**row, "result": "certified", "status": st,
                                 "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "released_by": "release_reader_held P15"})
    out["release"].append(entry)

dest = Path("outputs/work-pipeline") / f"release-reader-held-{time.strftime('%Y%m%d-%H%M%S')}{'' if APPLY else '-dry'}.json"
dest.write_text(json.dumps(out, indent=1))
print(json.dumps({"release": len(out["release"]), "kept": len(out["kept"]), "skipped": len(out["skipped"]),
                  "words": sum(e["words"] for e in out["release"]), "receipt": str(dest)}))
