#!/usr/bin/env python3
"""Jev cross-check for topics-excerpt Bible allusions (advisory only).

Mirrors jev_review.py for ante-nicene-topics/translations/topics/*.json,
whose excerpt records carry added_allusions the book reviewer never sees.
Reports agreement with filed certainty; mismatches go to an editor.

Sends the full excerpt (head+tail snip past 6000 chars) so quoted verses
living late in long excerpts are visible. Filed certainty is normalized
to Jev's {clear, possible, none} bands for the verdict; receipts keep
both the raw filed value and the normalized band.

Usage: python3 scripts/jev_topics_allusions.py [--max N] [--start N] [--out PATH]
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_review import (  # noqa: E402
    CERTAINTY_Q,
    excerpt_window,
    jev,
    normalize_certainty,
)

ROOT = Path(__file__).resolve().parents[1]


def iter_allusions():
    tdir = ROOT / "books" / "ante-nicene-topics" / "translations" / "topics"
    for path in sorted(tdir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("excerpts", [])
        for x in rows:
            if not isinstance(x, dict):
                continue
            eng = x.get("english") or []
            eng = " ".join(eng) if isinstance(eng, list) else str(eng)
            for al in x.get("added_allusions") or []:
                if isinstance(al, dict) and al.get("reference"):
                    yield path.name, x, eng, al


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    items = list(iter_allusions())
    if args.start:
        items = items[args.start:]
    if args.max:
        items = items[:args.max]
    print(f"allusions: {len(items)}", flush=True)
    receipts = []
    mismatches = checked = 0
    for n, (fname, x, eng, al) in enumerate(items, 1):
        ref = al.get("reference") or ""
        state = {"source_excerpt": excerpt_window(eng),
                 "candidate_verse": ref,
                 "filed_certainty": al.get("certainty"),
                 "filed_reason": al.get("reason")}
        try:
            body = jev(state, {"certainty": CERTAINTY_Q})
        except Exception as e:  # noqa: BLE001 - report lane failure plainly
            print(f"LANE-ERROR {x.get('id')}: {type(e).__name__}: {e}")
            return 3
        ans = body["answers"]["certainty"]
        filed = (al.get("certainty") or "").strip().lower()
        fnorm = normalize_certainty(filed)
        verdict = "AGREE" if ans["choice"] == fnorm else "MISMATCH"
        if verdict == "MISMATCH":
            mismatches += 1
        checked += 1
        receipts.append({"file": fname, "id": x.get("id"), "reference": ref,
                         "filed": filed, "filed_norm": fnorm,
                         "jev": ans["choice"],
                         "confidence": round(ans["confidence"], 3)})
        print(f"[{n}/{len(items)}] {verdict} {x.get('id')} {ref}: "
              f"filed={filed} jev={ans['choice']} "
              f"conf={ans['confidence']:.2f}", flush=True)
        time.sleep(0.2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for rec in receipts:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {args.out}", flush=True)
    print(f"MISMATCHES: {mismatches} of {checked} checked", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
