#!/usr/bin/env python3
"""Jev cross-check for filed Bible-allusion certainty (TypeSafe reviewer lane).

For each added_allusion in a book's English JSON, asks Jev whether the locked
source quotes, echoes, or merely resembles the verse, and reports agreement
with the filed certainty. Advisory only: mismatches go to a stronger reviewer,
never auto-decide. Needs TYPESAFE_API_KEY in the environment.

Usage: python3 scripts/jev_review.py <book-slug> [--all] [--max N]
Exit 0 with a MISMATCHES count line; prints one verdict line per allusion.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.typesafe.ai/v1/systemone"
TIMEOUT = 25


def jev(state, questions):
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        raise SystemExit("TYPESAFE_API_KEY not set")
    req = urllib.request.Request(
        API,
        data=json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode())


CERTAINTY_Q = {
    "type": "choice",
    "instructions": (
        "Does the source text quote or echo the candidate verse, "
        "or merely resemble it in theme?"
    ),
    "criteria": {
        "clear": "The source quotes the verse or unmistakably echoes its wording.",
        "possible": "No quotation or clear echo, but a plausible thematic connection.",
        "none": "Neither quotation, echo, nor meaningful connection.",
    },
}


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        print("usage: jev_review.py <book-slug> [--all] [--max N]", file=sys.stderr)
        return 2
    slug = argv[1]
    check_all = "--all" in argv
    max_n = 5
    if "--max" in argv:
        max_n = int(argv[argv.index("--max") + 1])
    book = ROOT / "books" / slug
    eng_files = sorted((book / "translations").glob("*_english.json"))
    if not eng_files:
        print(f"no English JSON under {book}/translations")
        return 2
    mismatches = 0
    checked = 0
    for ef in eng_files:
        data = json.loads(ef.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("sections", [])
        src_path = ef.with_name(ef.name.replace("_english.json", "_source.json"))
        src_map = {}
        if src_path.exists():
            sdata = json.loads(src_path.read_text(encoding="utf-8"))
            srows = sdata if isinstance(sdata, list) else sdata.get("sections", [])
            src_map = {str(s.get("section")): s for s in srows if isinstance(s, dict)}
        for row in rows:
            if not isinstance(row, dict):
                continue
            for al in row.get("added_allusions") or []:
                if not isinstance(al, dict) or not al.get("reference"):
                    continue
                if checked >= max_n and not check_all:
                    print(f"cap reached ({max_n}); rerun with --all for the rest")
                    print(f"MISMATCHES: {mismatches} of {checked} checked")
                    return 0
                sec = str(row.get("section"))
                src = src_map.get(sec, {})
                full_en = " ".join(row.get("english") or [])
                ref = al.get("reference") or ""
                # Center the English window on the citation itself: a blind
                # head-clip once cut off the very clause under review.
                idx = full_en.find(ref)
                if idx < 0:
                    short = ref.split("\u2013")[0].split("-")[0].strip()
                    idx = full_en.find(short) if len(short) > 3 else -1
                if idx >= 0:
                    english_excerpt = full_en[max(0, idx - 1200):idx + 1200]
                else:
                    english_excerpt = full_en[:1500]
                state = {
                    "source_excerpt": str(src.get("latin") or src.get("greek") or "")[:3000],
                    "english_excerpt": english_excerpt,
                    "candidate_verse": al.get("reference"),
                    "filed_certainty": al.get("certainty"),
                    "filed_reason": al.get("reason"),
                }
                try:
                    body = jev(state, {"certainty": CERTAINTY_Q})
                except Exception as e:  # noqa: BLE001 - report lane failure plainly
                    print(f"LANE-ERROR sec {sec}: {type(e).__name__}: {e}")
                    return 3
                ans = body["answers"]["certainty"]
                filed = (al.get("certainty") or "").strip().lower()
                verdict = "AGREE" if ans["choice"] == filed else "MISMATCH"
                if verdict == "MISMATCH":
                    mismatches += 1
                checked += 1
                print(
                    f"{verdict} sec {sec} {al.get('reference')}: filed={filed} "
                    f"jev={ans['choice']} conf={ans['confidence']:.2f}"
                )
    if checked == 0:
        print("no added_allusions filed in this book")
    print(f"MISMATCHES: {mismatches} of {checked} checked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
