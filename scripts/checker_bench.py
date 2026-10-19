#!/usr/bin/env python3
"""Checker bench (owner 2026-10-19: "do a larger test, has to be statistically significant").

Which models should check translations, judged on three groups of sections, all with
the production checker (work_pipeline.check_one, CHECK_SYS) through the production call
path, so plan models (muse, claude-*, grok-*) and Workers AI ids compare like for like:

  A  real errors     sections holding a finding the Claude held review judged REAL
                     (outputs/referee-bench/sample.jsonl answer key). Caught when a finding
                     quotes the same English or source words (>=3-word overlap).
  B  planted errors  one meaning error planted (defect_bench injectors: negation, agency,
                     omission, addition, wrong Scripture, malapropism, speaker) into a
                     section of a certified book. Caught when a finding quotes the planted span.
  C  clean controls  untouched sections of certified books. Any finding is a flag.

  python3 scripts/checker_bench.py build [--planted 70 --clean 50]
  python3 scripts/checker_bench.py run --models a,b,... [--workers 2]
  python3 scripts/checker_bench.py score

Out: outputs/checker-bench-plans/{items.jsonl, runs/<model>.jsonl, REPORT.md, scores.json}.
Scores carry Wilson 95% intervals; models are compared pairwise with McNemar's exact test
on the same items.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import defect_bench as DB  # noqa: E402
import work_pipeline as W  # noqa: E402

OUT = ROOT / "outputs" / "checker-bench-plans"
ITEMS = OUT / "items.jsonl"
KEY = ROOT / "outputs" / "referee-bench" / "sample.jsonl"
PLANT_TYPES = ["negation_flip", "agency_swap", "omission", "addition", "wrong_scripture", "malapropism", "speaker_strip"]
SEED = 20261019


def _lang(src: str) -> str:
    return "Greek" if any("Ͱ" <= c <= "Ͽ" or "ἀ" <= c <= "῿" for c in src[:400]) else "Latin"


def build(planted: int, clean: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    items = []
    # A: one item per section that holds at least one REAL finding in the answer key.
    by_sec: dict[str, dict] = {}
    for line in KEY.read_text().splitlines():
        r = json.loads(line)
        if r["key"] != "real":
            continue
        k = f"{r['book']}|{r['section']}"
        it = by_sec.setdefault(k, {"id": "A:" + k, "group": "A", "book": r["book"], "section": r["section"],
                                   "source": r["source"], "english": r["english"], "truth": []})
        it["truth"].append({"class": r.get("class"), "quote": r.get("quote", ""), "source_quote": r.get("source_quote", "")})
    items += list(by_sec.values())
    # B and C: sections of certified books, 60-450 words, one section per book where possible.
    books = sorted(b.name for b in (ROOT / "books").iterdir() if (b / "reviews" / "work_receipt.json").exists() and W.certified(b.name))
    rng.shuffle(books)
    pool = []
    for b in books:
        try:
            secs = [s for s in DB.load_base(b) if s["source"].strip() and 60 <= len(s["text"].split()) <= 450]
        except (OSError, ValueError):
            continue
        rng.shuffle(secs)
        pool += [(b, s) for s in secs[:6]]
    rng.shuffle(pool)
    used = set()
    type_cycle = PLANT_TYPES * (planted // len(PLANT_TYPES) + 1)
    for ty in type_cycle:
        if sum(i["group"] == "B" for i in items) >= planted:
            break
        for n, (b, s) in enumerate(pool):
            if n in used:
                continue
            res = DB.INJECTORS[ty]([dict(s)], [0], random.Random(f"{SEED}{b}{s['id']}{ty}"))
            if res is None:
                continue
            truth, new = res
            used.add(n)
            sp = truth["spans"][0]
            items.append({"id": f"B:{b}|{s['id']}|{ty}", "group": "B", "book": b, "section": s["id"], "type": ty,
                          "source": s["source"], "english": new[0],
                          "truth": [{"class": ty, "quote": sp.get("injected") or sp.get("context", ""),
                                     "source_quote": ""}]})
            break
    for n, (b, s) in enumerate(pool):
        if sum(i["group"] == "C" for i in items) >= clean:
            break
        if n in used:
            continue
        used.add(n)
        items.append({"id": f"C:{b}|{s['id']}", "group": "C", "book": b, "section": s["id"],
                      "source": s["source"], "english": s["text"], "truth": []})
    ITEMS.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
    from collections import Counter
    print(f"items: {Counter(i['group'] for i in items)}; planted types: {Counter(i.get('type') for i in items if i['group'] == 'B')}")


def caught(findings: list[dict], item: dict) -> bool:
    for t in item["truth"]:
        for f in findings:
            q, sq = str(f.get("quote", "")), str(f.get("source_quote", ""))
            if t["quote"] and (DB.overlap(q, t["quote"]) or DB.overlap(t["quote"], q)):
                return True
            if t["source_quote"] and sq and DB.overlap(sq, t["source_quote"]):
                return True
    return False


def run(models: list[str], workers: int) -> None:
    W.TOKENS["cf"], W.TOKENS["nv"] = W.secret("CLOUDFLARE_API_TOKEN"), W.secret("NV_API_KEY")
    W.receipts_ok(models, "translation-qa")
    items = [json.loads(line) for line in ITEMS.read_text().splitlines()]
    (OUT / "runs").mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()

    def one_model(model: str) -> None:
        path = OUT / "runs" / (model.replace("/", "__") + ".jsonl")
        done = {json.loads(line)["id"] for line in path.read_text().splitlines()} if path.exists() else set()
        todo = [i for i in items if i["id"] not in done]

        def ask(it: dict) -> None:
            t0 = time.time()
            sec = {"id": it["section"], "source": it["source"].split("\n")}
            try:
                fs = W.check_one(model, sec, it["english"].split("\n"), {}, _lang(it["source"]))
                err = None if fs is not None else "no answer"
            except Exception as e:  # noqa: BLE001  a bench row records the failure
                fs, err = None, f"{type(e).__name__}: {e}"[:200]
            row = {"id": it["id"], "group": it["group"], "answered": fs is not None,
                   "findings": [{k: f.get(k) for k in ("class", "quote", "source_quote", "why", "severity")} for f in fs or []],
                   "caught": caught(fs or [], it) if it["truth"] else None, "secs": round(time.time() - t0, 1), "error": err}
            with lock, path.open("a") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(ask, todo))
        print(f"{time.strftime('%T')} STAGE done {model}: {len(todo)} asked", flush=True)

    with ThreadPoolExecutor(len(models)) as ex:
        list(ex.map(one_model, models))
    print(f"{time.strftime('%T')} EXIT ok run", flush=True)


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return 0.0, 0.0
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar p for discordant counts b, c."""
    n = b + c
    if not n:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def score() -> None:
    items = {json.loads(line)["id"]: json.loads(line) for line in ITEMS.read_text().splitlines()}
    runs = {}
    for path in sorted((OUT / "runs").glob("*.jsonl")):
        rows = {}
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r["id"] in items:
                rows[r["id"]] = r
        runs[path.stem.replace("__", "/")] = rows
    lines = ["# Checker bench", "", f"Items: {sum(i['group'] == 'A' for i in items.values())} real-error sections (A), "
             f"{sum(i['group'] == 'B' for i in items.values())} planted errors (B), "
             f"{sum(i['group'] == 'C' for i in items.values())} clean controls (C). Production check_one / CHECK_SYS.",
             "", "| model | answered | A real caught | B planted caught | C clean flagged | median s |",
             "|---|---|---|---|---|---|"]
    res = []
    for m, rows in runs.items():
        out = {"model": m, "answered": sum(r["answered"] for r in rows.values()), "n": len(rows)}
        for g in ("A", "B"):
            rs = [r for r in rows.values() if r["group"] == g and r["answered"]]
            k = sum(bool(r["caught"]) for r in rs)
            lo, hi = wilson(k, len(rs))
            out[g] = (k, len(rs), lo, hi)
        cs = [r for r in rows.values() if r["group"] == "C" and r["answered"]]
        k = sum(bool(r["findings"]) for r in cs)
        lo, hi = wilson(k, len(cs))
        out["C"] = (k, len(cs), lo, hi)
        secs = sorted(r["secs"] for r in rows.values() if r["answered"])
        out["median_s"] = secs[len(secs) // 2] if secs else None
        res.append(out)

        def cell(t):
            return f"{t[0]}/{t[1]} = {100 * t[0] / max(t[1], 1):.0f}% [{100 * t[2]:.0f}-{100 * t[3]:.0f}]"
        lines.append(f"| {m} | {out['answered']}/{len(items)} | {cell(out['A'])} | {cell(out['B'])} | {cell(out['C'])} | {out['median_s']} |")
    lines += ["", "Brackets: Wilson 95% interval.", "", "## Pairwise (A+B errors caught, McNemar exact)", "",
              "| model 1 | model 2 | only 1 caught | only 2 caught | p |", "|---|---|---|---|---|"]
    pos = [i for i, it in items.items() if it["group"] in ("A", "B")]
    names = list(runs)
    for x in range(len(names)):
        for y in range(x + 1, len(names)):
            a, b = runs[names[x]], runs[names[y]]
            both = [i for i in pos if i in a and i in b and a[i]["answered"] and b[i]["answered"]]
            only1 = sum(bool(a[i]["caught"]) and not b[i]["caught"] for i in both)
            only2 = sum(bool(b[i]["caught"]) and not a[i]["caught"] for i in both)
            lines.append(f"| {names[x]} | {names[y]} | {only1} | {only2} | {mcnemar_p(only1, only2):.3f} |")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    (OUT / "scores.json").write_text(json.dumps(res, indent=1))
    print("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "run", "score"])
    ap.add_argument("--planted", type=int, default=70)
    ap.add_argument("--clean", type=int, default=50)
    ap.add_argument("--models", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.planted, a.clean)
    elif a.cmd == "run":
        run([m for m in a.models.split(",") if m], a.workers)
    else:
        score()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
