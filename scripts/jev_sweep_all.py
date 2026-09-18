#!/usr/bin/env python3
"""Full-corpus Jev certainty sweep. Every filed added_allusion gets an
independent verdict; results append as JSONL. Advisory only: nothing is
changed. Usage: python3 scripts/jev_sweep_all.py [--out PATH] [--glob PATTERN]
--glob filters book slugs by fnmatch (e.g. '[k-z]*' for a remainder sweep)
so a resumed run cannot duplicate already-swept slugs.
Needs TYPESAFE_API_KEY in the environment."""
from __future__ import annotations

import fnmatch
import glob
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.jev_review import CERTAINTY_Q, jev  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def window(text, needle, radius=1200, fallback=1500):
    idx = text.find(needle)
    if idx < 0:
        short = needle.split("\u2013")[0].split("-")[0].strip()
        idx = text.find(short) if len(short) > 3 else -1
    if idx >= 0:
        return text[max(0, idx - radius):idx + radius]
    return text[:fallback]


def iter_english_files(root, pattern=None):
    """Yield (path, slug) for each book English JSON, optionally fnmatch-filtered."""
    for ef in sorted(glob.glob(str(Path(root) / "books/*/translations/*_english.json"))):
        slug = ef.split("/books/")[1].split("/")[0]
        if pattern and not fnmatch.fnmatch(slug, pattern):
            continue
        yield ef, slug


def main(argv):
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else (
        ROOT / "outputs" / f"jev-sweep-{datetime.now().strftime('%Y%m%d')}.jsonl"
    )
    pattern = argv[argv.index("--glob") + 1] if "--glob" in argv else None
    total_in = total_out = checked = mismatches = errors = 0
    with open(out, "a", encoding="utf-8") as fh:
        for ef, slug in iter_english_files(ROOT, pattern):
            try:
                data = json.load(open(ef, encoding="utf-8"))
            except Exception:
                continue
            rows = data if isinstance(data, list) else data.get("sections", [])
            src_path = ef.replace("_english.json", "_source.json")
            src_map = {}
            try:
                sdata = json.load(open(src_path, encoding="utf-8"))
                srows = sdata if isinstance(sdata, list) else sdata.get("sections", [])
                src_map = {str(s.get("section")): s for s in srows if isinstance(s, dict)}
            except Exception:
                pass
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for al in row.get("added_allusions") or []:
                    if not isinstance(al, dict) or not al.get("reference"):
                        continue
                    sec = str(row.get("section"))
                    src = src_map.get(sec, {})
                    state = {
                        "source_excerpt": str(src.get("latin") or src.get("greek") or "")[:3000],
                        "english_excerpt": window(" ".join(row.get("english") or []), al["reference"]),
                        "candidate_verse": al["reference"],
                        "filed_certainty": al.get("certainty"),
                        "filed_reason": al.get("reason"),
                    }
                    try:
                        body = jev(state, {"certainty": CERTAINTY_Q})
                    except Exception as e:  # noqa: BLE001 - record and continue
                        errors += 1
                        fh.write(json.dumps({"book": slug, "section": sec, "error": f"{type(e).__name__}: {e}"}) + "\n")
                        fh.flush()
                        time.sleep(2)
                        continue
                    ans = body["answers"]["certainty"]
                    filed = (al.get("certainty") or "").strip().lower()
                    verdict = "AGREE" if ans["choice"] == filed else "MISMATCH"
                    if verdict == "MISMATCH":
                        mismatches += 1
                    checked += 1
                    u = body.get("usage", {})
                    total_in += u.get("input_tokens", 0)
                    total_out += u.get("output_tokens", 0)
                    fh.write(json.dumps({
                        "book": slug, "section": sec, "reference": al["reference"],
                        "filed": filed, "jev": ans["choice"],
                        "confidence": ans["confidence"],
                        "probabilities": ans.get("probabilities"),
                        "verdict": verdict, "usage": u,
                    }) + "\n")
                    fh.flush()
                    if checked % 100 == 0:
                        print(f"...{checked} checked, {mismatches} mismatches, {errors} errors", flush=True)
                    time.sleep(0.2)
    print(f"DONE checked={checked} mismatches={mismatches} errors={errors}", flush=True)
    print(f"TOKENS in={total_in} out={total_out}", flush=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
