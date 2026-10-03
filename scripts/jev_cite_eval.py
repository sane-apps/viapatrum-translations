#!/usr/bin/env python3
"""Wide Jev citation eval: filed cites vs certain-negative swaps, corpus-wide.

Positives are filed Pass B citations (presumed true); negatives swap in a
real verse from a different book, cross- or same-testament. One Jev call per
section, mirroring production. Answers cache by (clause, display) so reruns
are free. Prints a calibration summary; writes JSONL details.

Usage: python3 scripts/jev_cite_eval.py [--positives N] [--per-book N]
  [--seed N] [--out PATH] [--cache PATH] [--no-cache] [--max-per-call N]
  [--all] [--glob PATTERN]
--all sweeps every filed citation corpus-wide (site + Logos books share the
same English JSON). --glob filters book slugs by fnmatch so a big sweep can
run in resumable chunks (answers cache, reruns are free).
Needs TYPESAFE_API_KEY unless every answer is cached.
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import hashlib
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_review import jev  # noqa: E402
import jev_cite_check as cite  # noqa: E402
import ai_promote as promote  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

OT = {"gen", "exod", "lev", "num", "deut", "josh", "judg", "ruth", "1sam",
      "2sam", "1kgs", "2kgs", "1chr", "2chr", "ezra", "neh", "esth", "job",
      "ps", "prov", "eccl", "song", "isa", "jer", "lam", "ezek", "dan",
      "hos", "joel", "amos", "obad", "jonah", "mic", "nah", "hab", "zeph",
      "hag", "zech", "mal", "wis", "sir", "bar", "tob", "jdt", "1macc",
      "2macc"}


def testament(book_id: str) -> str:
    return "OT" if book_id in OT else "NT"


def cache_key(clause: str, display: str) -> str:
    return hashlib.sha1(f"{clause}\0{display}".encode()).hexdigest()[:16]


def collect_positives(per_book: int | None, seed: int, pattern: str | None = None):
    """Stratified filed cites: [(book, section, clause, ref, display, cf)]."""
    rng = random.Random(seed)
    out = []
    for ef in sorted(glob.glob(str(ROOT / "books/*/translations/*_english.json"))):
        slug = ef.split("books/")[1].split("/")[0]
        if pattern and not fnmatch.fnmatch(slug, pattern):
            continue
        try:
            data = json.load(open(ef, encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        found = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            eng = row.get("english") or []
            paras = eng if isinstance(eng, list) else [eng]
            for clause, ref, display, cf in cite.cite_pairs(paras, max_n=50):
                found.append((slug, str(row.get("section")), clause, ref, display, cf))
        if per_book is None:
            out.extend(found)
        else:
            rng.shuffle(found)
            out.extend(found[:per_book])
    return out


def assign_swaps(positives, rng):
    """Certain-negative displays: real verses from other books.

    Cross-testament first (nearly immune to parallel passages), then
    same-testament. A supports verdict on a negative gets manual review:
    it is either a Jev error or a genuine parallel/quotation overlap.
    """
    by_test = {"OT": [], "NT": []}
    for i, pos in enumerate(positives):
        by_test[testament(pos[3][0])].append((i, pos[4], pos[3][0]))
    negs = []
    for i, pos in enumerate(positives):
        _slug, _sec, _cl, ref, _disp, _cf = pos
        own_test = testament(ref[0])
        own_book = ref[0]
        other = [d for j, d, b in by_test["NT" if own_test == "OT" else "OT"]
                 if j != i and b != own_book]
        same = [d for j, d, b in by_test[own_test] if j != i and b != own_book]
        if other:
            negs.append((i, rng.choice(other), "NEG_XTEST"))
        if same:
            negs.append((i, rng.choice(same), "NEG_STEST"))
    return negs


def evaluate(positives, max_per_call=12, cache=None, no_cache=False, cache_path=None):
    """Run Jev over positives + swaps. Returns (records, stats)."""
    cache = {} if cache is None else cache
    rng = random.Random(1234)
    swaps = assign_swaps(positives, rng)
    # Group questions by section: one call per section like production.
    groups = {}
    for i, pos in enumerate(positives):
        slug, sec = pos[0], pos[1]
        stratum = "POS_CF" if pos[5] else "POS_DIRECT"
        groups.setdefault((slug, sec), []).append((stratum, i, pos[2], pos[4]))
    for i, display, stratum in swaps:
        pos = positives[i]
        groups.setdefault((pos[0], pos[1]), []).append((stratum, i, pos[2], display))
    records = []
    stats = {"calls": 0, "cached": 0, "in_tokens": 0, "out_tokens": 0,
             "seconds": 0.0, "errors": 0}
    # Load each section's texts once for state (direct JSON, all books).
    texts = {}
    for (slug, sec) in groups:
        try:
            texts[(slug, sec)] = cite.load_section_texts(slug, sec)
        except Exception as e:  # noqa: BLE001 - record and skip section
            stats["errors"] += 1
            for stratum, i, clause, display in groups[(slug, sec)]:
                records.append({"stratum": stratum, "book": slug, "section": sec,
                                "display": display, "error": f"texts: {e}"[:120]})
            del groups[(slug, sec)]
    for (slug, sec), items in sorted(groups.items()):
        greek, paras = texts[(slug, sec)]
        state = {"greek": greek[:4000],
                 "english": "\n".join(paras)[:4000]}
        todo = []
        for stratum, i, clause, display in items:
            key = cache_key(clause, display)
            if not no_cache and key in cache:
                stats["cached"] += 1
                records.append(_record(cache[key], stratum, slug, sec, clause, display, True))
            else:
                todo.append((stratum, i, clause, display, key))
        for start in range(0, len(todo), max_per_call):
            chunk = todo[start:start + max_per_call]
            pairs = [(c, ("", 0, 0), d, False) for _, _, c, d, _k in chunk]
            t0 = time.time()
            try:
                body = jev(state, cite.build_questions(pairs))
            except Exception as e:  # noqa: BLE001 - record and continue
                stats["errors"] += 1
                for stratum, _i, clause, display, _k in chunk:
                    records.append({"stratum": stratum, "book": slug, "section": sec,
                                    "display": display, "error": f"{type(e).__name__}: {e}"[:120]})
                time.sleep(2)
                continue
            stats["calls"] += 1
            if stats["calls"] % 100 == 0:
                print(f"...{stats['calls']} calls, {len(records)} items, "
                      f"in={stats['in_tokens']} tok", flush=True)
                if cache_path and not no_cache:
                    Path(cache_path).write_text(json.dumps(cache), encoding="utf-8")
            stats["seconds"] += time.time() - t0
            use = body.get("usage") or {}
            stats["in_tokens"] += use.get("input_tokens", 0)
            stats["out_tokens"] += use.get("output_tokens", 0)
            for n, (stratum, _i, clause, display, key) in enumerate(chunk):
                ans = body["answers"][f"cite{n}"]
                cache[key] = {"choice": ans["choice"],
                              "confidence": ans.get("confidence", 0.0),
                              "probabilities": ans.get("probabilities"),
                              "model": body.get("model")}
                records.append(_record(cache[key], stratum, slug, sec, clause, display, False))
            time.sleep(0.2)
    return records, stats


def _record(ans, stratum, slug, sec, clause, display, cached):
    return {"stratum": stratum, "book": slug, "section": sec,
            "display": display, "clause": clause[:300],
            "choice": ans["choice"], "confidence": round(ans.get("confidence", 0.0), 3),
            "model": ans.get("model"), "cached": cached}


def summarize(records, stats):
    lines = []
    ok = [r for r in records if "error" not in r]
    lines.append(f"items={len(ok)} errors={len(records) - len(ok)} "
                 f"calls={stats['calls']} cached={stats['cached']}")
    lines.append(f"tokens in={stats['in_tokens']} out={stats['out_tokens']} "
                 f"seconds={stats['seconds']:.1f}")
    for stratum in ("POS_DIRECT", "POS_CF", "NEG_XTEST", "NEG_STEST"):
        rows = [r for r in ok if r["stratum"] == stratum]
        if not rows:
            continue
        want = "supports" if stratum.startswith("POS") else "contradicts"
        right = [r for r in rows if r["choice"] == want]
        high_wrong = [r for r in rows if r["choice"] != want
                      and r["choice"] != "says_nothing" and r["confidence"] >= 0.9]
        fuzzy = [r for r in rows if r["choice"] == "says_nothing"]
        mean_right = (sum(r["confidence"] for r in right) / len(right)) if right else 0
        lines.append(f"{stratum:10s} n={len(rows):3d} {want}={len(right):3d} "
                     f"({100 * len(right) / len(rows):.0f}%) fuzzy={len(fuzzy)} "
                     f"highconf_wrong={len(high_wrong)} meanconf_right={mean_right:.2f}")
        for r in high_wrong[:5]:
            lines.append(f"  HIGHCONF_WRONG {r['book']}/{r['section']} {r['display']} "
                         f"{r['choice']}@{r['confidence']} :: {r['clause'][:120]}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--positives", type=int, default=120)
    ap.add_argument("--per-book", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="")
    ap.add_argument("--cache", default=str(ROOT / "outputs/jev-eval-cache.json"))
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--max-per-call", type=int, default=12)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--glob", default="")
    args = ap.parse_args(argv)
    if args.all:
        positives = collect_positives(None, args.seed, args.glob or None)
    else:
        positives = collect_positives(args.per_book, args.seed, args.glob or None)
        rng = random.Random(args.seed)
        rng.shuffle(positives)
        positives = positives[:args.positives]
    print(f"sampled {len(positives)} positives across "
          f"{len({p[0] for p in positives})} books", flush=True)
    cache = {}
    if not args.no_cache and Path(args.cache).is_file():
        cache = json.loads(Path(args.cache).read_text(encoding="utf-8"))
        print(f"loaded {len(cache)} cached answers", flush=True)
    records, stats = evaluate(positives, args.max_per_call, cache, args.no_cache,
                              None if args.no_cache else args.cache)
    if not args.no_cache:
        Path(args.cache).write_text(json.dumps(cache, indent=1), encoding="utf-8")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {args.out}", flush=True)
    print(summarize(records, stats), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
