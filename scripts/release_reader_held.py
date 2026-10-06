#!/usr/bin/env python3
"""Release held works that are stuck only on the reader score (P15, 2026-10-06).

Reader edits are off (WP_READ_EDITS=0), so nothing in the pipeline can raise a
work's reader score any more. Works whose sections ALL pass the blind
two-family source check and whose intro is clean can still sit 'held' forever
on readers [3,3] because FOLLOW_AVG = 3.5.

This script makes no model calls. It reuses the scores already stored in each
work's read.json; work_pipeline.read_scores rejects a read whose text_sha256
does not match the current text, so a stale score never counts.

Dry run (default) writes a receipt and changes nothing:
    python3 scripts/release_reader_held.py
Apply (only after the owner approves the bar AND work_pipeline.follow_ok has
the reader-bar change; until then follow_ok refuses and nothing is applied):
    python3 scripts/release_reader_held.py --apply --books a,b,c

Queue rows are written only under the lanes' own queue.json lock, read and
merged inside that lock, and replaced atomically (tmp + rename), the same way
work_pipeline.update_log / claim do.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as wp  # noqa: E402

# Owner decision (memory fathers-state-2026-10-04): parked on the reader bar on purpose.
OWNER_PARKED = {"ignatius-letters", "hermas-shepherd"}
OUT = wp.STAGE / "reader-bar-release-20261006"


def nums(scores) -> list:
    return [s for s in scores or [] if isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s)]


def proposed_ok(scores) -> bool:
    """The bar P15 proposes while reader edits are off: two readers, none below FOLLOW_MIN."""
    n = nums(scores)
    return len(n) >= 2 and min(n) >= wp.FOLLOW_MIN


def quiet_status(slug: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return wp.status(slug)


def words_of(slug: str) -> int:
    return sum(len(" ".join(p["source"]).split()) for p in wp.load_pairs(slug))


def survey() -> dict:
    rows = json.loads(wp.QUEUE_LOG.read_text())
    out = {"release": [], "has_a_2": [], "intro_or_sections": [], "stale_or_no_read": [], "owner_parked": [], "other": []}
    for slug, row in sorted(rows.items()):
        if row.get("result") != "held":
            continue
        try:
            st = quiet_status(slug)
        except Exception as e:  # one broken work must not stop the survey
            out["other"].append({"slug": slug, "why": f"status failed: {type(e).__name__}: {e}"})
            continue
        secs = st.get("sections") or {}
        scores = st.get("followability")
        item = {"slug": slug, "words": words_of(slug), "scores": scores, "sections": secs,
                "intro_ok": st.get("intro_ok"), "attempts": row.get("attempts"),
                "queue_scores": (row.get("status") or {}).get("followability")}
        if st.get("read_note"):
            item["read_note"] = st["read_note"]
        if slug in OWNER_PARKED:
            out["owner_parked"].append(item)
        elif set(secs) != {"pass"}:
            continue  # sections still held or stale: not a reader-bar case
        elif not st.get("intro_ok"):
            out["intro_or_sections"].append(item)
        elif st.get("read_note") or len(nums(scores)) < 2:
            out["stale_or_no_read"].append(item)
        elif not proposed_ok(scores):
            out["has_a_2"].append(item)
        elif wp.certified(slug):
            out["other"].append({**item, "why": "already certified"})
        else:
            item["follow_ok_now"] = bool(wp.follow_ok(scores, item["words"]))
            out["release"].append(item)
    return out


def set_row(book: str, update) -> dict:
    """Read-merge-write one queue row under the lanes' lock; atomic replace."""
    import fcntl
    with open(str(wp.QUEUE_LOG) + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        rows = json.loads(wp.QUEUE_LOG.read_text())
        rows[book] = update(rows.get(book) or {})
        tmp = wp.QUEUE_LOG.with_suffix(".release.tmp")
        tmp.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
        os.replace(tmp, wp.QUEUE_LOG)
        return rows[book]


def release(book: str) -> dict:
    st = quiet_status(book)
    words = words_of(book)
    if set(st.get("sections") or {}) != {"pass"} or not st.get("intro_ok") or st.get("read_note"):
        return {"slug": book, "result": "skipped", "why": "sections, intro or read not clean now"}
    if not wp.follow_ok(st.get("followability"), words):
        return {"slug": book, "result": "skipped",
                "why": "work_pipeline.follow_ok still refuses (reader-bar change not in the pipeline)"}
    prev = wp.claim(book)  # marks it running for this pid; lanes skip it
    if prev is None:
        return {"slug": book, "result": "skipped", "why": "a live lane holds it"}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = wp.apply(book)
    except Exception as e:
        rc = 99
        print(f"{book}: apply crashed: {type(e).__name__}: {e}", file=sys.stderr)
    ok = rc == 0 and wp.certified(book)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    if ok:
        row = set_row(book, lambda r: {**r, "result": "certified", "status": st, "at": now, "pid": None,
                                       "why": "reader bar waived (P15): all sections pass, intro clean, readers "
                                              f"{st.get('followability')}"})
    else:
        row = set_row(book, lambda r: {**prev, "at": now})  # put the held row back as it was
    check = json.loads(wp.QUEUE_LOG.read_text()).get(book, {})
    return {"slug": book, "result": "certified" if ok else "failed", "rc": rc, "row_after": check.get("result"),
            "row_written": row.get("result")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="certify the named books (default: dry run)")
    ap.add_argument("--books", default="", help="comma list; required with --apply")
    ap.add_argument("--out", default=str(OUT / "dry-run.json"))
    a = ap.parse_args()
    if not a.apply:
        s = survey()
        rec = {"made": time.strftime("%Y-%m-%dT%H:%M:%S"), "mode": "dry-run", "model_calls": 0,
               "bar_now": {"FOLLOW_MIN": wp.FOLLOW_MIN, "FOLLOW_AVG": wp.FOLLOW_AVG, "READ_EDITS": wp.READ_EDITS},
               "bar_proposed": "while reader edits are off: two readers, none below FOLLOW_MIN; no average check",
               "counts": {k: len(v) for k, v in s.items()},
               "release_words": sum(i["words"] for i in s["release"]),
               # Every all-pass work with a reader at 2, whatever else holds it
               # (review 2026-10-06: john-damascus-de-animato [2,4] also fails its intro).
               "any_reader_2": sorted(i["slug"] for k in ("has_a_2", "intro_or_sections", "stale_or_no_read")
                                      for i in s[k] if any(n < wp.FOLLOW_MIN for n in nums(i["scores"] or i["queue_scores"]))),
               **s}
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(a.out).with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
        os.replace(tmp, a.out)
        print(json.dumps(rec["counts"]), f"-> {a.out}")
        return 0
    books = [b.strip() for b in a.books.split(",") if b.strip()]
    if not books:
        ap.error("--apply needs --books")
    bad = [b for b in books if b in OWNER_PARKED]
    if bad:
        ap.error(f"owner parked these on purpose: {', '.join(bad)}")
    results = [release(b) for b in books]
    path = OUT / f"apply-{time.strftime('%Y%m%dT%H%M%S')}.json"
    path.write_text(json.dumps({"mode": "apply", "results": results}, indent=1) + "\n")
    print(json.dumps(results, indent=1), f"-> {path}")
    return 0 if all(r["result"] == "certified" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
