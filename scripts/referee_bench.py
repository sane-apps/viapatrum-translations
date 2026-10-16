#!/usr/bin/env python3
"""Referee bench (owner 2026-10-16: "do benchmarks, have 5 model fallbacks so
stalls on work is unlikely").

The referee (work_pipeline.referee) rules whether a reported problem in an
English section is a real major error. The answer key is the Claude held
review: every finding it judged "real" or "noise" (outputs/held-review/*/
verdicts.jsonl; "unsure" is left out). Each candidate gets the production
prompt (ADJ_SYS) with one reported problem, through the production call().

  python3 scripts/referee_bench.py build [--n 160] [--per-book 4]
  python3 scripts/referee_bench.py run --models a,b,... [--workers 2]
  python3 scripts/referee_bench.py score

Out: outputs/referee-bench/{sample.jsonl, runs/<model>.jsonl, REPORT.md}.
What matters most is real_kept: a referee that clears a real error lets it
publish. noise_cleared is throughput (false alarms released).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as W  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HR = ROOT / "outputs" / "held-review"
OUT = ROOT / "outputs" / "referee-bench"
SAMPLE = OUT / "sample.jsonl"


def load_key() -> list[dict]:
    rows = []
    for d in sorted(HR.iterdir()):
        f, v = d / "findings.jsonl", d / "verdicts.jsonl"
        if not (f.exists() and v.exists()):
            continue
        finds = {}
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                finds[r["id"]] = r
        for line in v.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("verdict") in ("real", "noise") and r["id"] in finds:
                rows.append({**finds[r["id"]], "key": r["verdict"], "key_note": r.get("note", ""), "set": d.name})
    return rows


def build(n: int, per_book: int, seed: int = 16) -> None:
    rows = load_key()
    seen, uniq = set(), []
    for r in rows:  # the same finding can appear in two reviews; keep the latest
        k = (r["book"], r["section"], r.get("quote", ""))
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    rnd = random.Random(seed)
    rnd.shuffle(uniq)
    out, per = [], {}
    for want in ("real", "noise"):
        got = 0
        for r in uniq:
            if got >= n // 2:
                break
            if r["key"] != want or per.get((want, r["book"]), 0) >= per_book:
                continue
            per[(want, r["book"])] = per.get((want, r["book"]), 0) + 1
            out.append(r)
            got += 1
    rnd.shuffle(out)
    OUT.mkdir(parents=True, exist_ok=True)
    SAMPLE.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    books = {r["book"] for r in out}
    print(f"sample: {len(out)} findings ({sum(r['key'] == 'real' for r in out)} real), {len(books)} books -> {SAMPLE}")


def langname(src: str) -> str:
    return "Greek" if re.search(r"[Ͱ-Ͽἀ-῿]", src or "") else "Latin"


def user_for(r: dict) -> str:
    listing = f"1. [{r.get('class', '')}] English: \"{r.get('quote', '')}\" | source: \"{r.get('source_quote', '')}\" | claim: {r.get('why', '')}"
    return ("SOURCE:\n" + (r.get("source") or "") + "\n\nENGLISH:\n" + (r.get("english") or "")
            + f"\n\nREPORTED PROBLEMS:\n{listing}\n\nReturn the JSON now.")


def run(models: list[str], workers: int) -> None:
    W.TOKENS["cf"], W.TOKENS["nv"] = W.secret("CLOUDFLARE_API_TOKEN"), W.secret("NV_API_KEY")
    W.receipts_ok(models, "translation-qa")
    sample = [json.loads(l) for l in SAMPLE.read_text().splitlines() if l.strip()]
    (OUT / "runs").mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()

    def one_model(model: str) -> None:
        path = OUT / "runs" / (model.replace("/", "__") + ".jsonl")
        done = set()
        if path.exists():
            done = {json.loads(l)["id"] for l in path.read_text().splitlines() if l.strip()}
        todo = [r for r in sample if r["id"] not in done]

        def ask(r: dict) -> None:
            t0 = time.time()
            try:
                obj = W.call(model, W.ADJ_SYS.format(langname=langname(r.get("source", ""))), user_for(r),
                             max_tokens=3000, expect=("rulings",))
                err = None
            except Exception as e:  # noqa: BLE001  a bench row records the failure
                obj, err = None, f"{type(e).__name__}: {e}"[:200]
            real = None
            for x in (obj or {}).get("rulings") or []:
                if isinstance(x, dict) and str(x.get("n", "")) == "1" and isinstance(x.get("real"), bool):
                    real = x["real"]
            row = {"id": r["id"], "key": r["key"], "real": real, "secs": round(time.time() - t0, 1),
                   "why": next((str(x.get("why", ""))[:200] for x in (obj or {}).get("rulings") or [] if isinstance(x, dict)), ""),
                   "error": err if obj is None else None}
            with lock:
                with path.open("a") as fh:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")

        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(ask, todo))
        print(f"{time.strftime('%T')} STAGE done {model}: {len(todo)} asked", flush=True)

    with ThreadPoolExecutor(len(models)) as ex:
        list(ex.map(one_model, models))
    print(f"{time.strftime('%T')} EXIT ok run", flush=True)


def score() -> list[dict]:
    sample = {json.loads(l)["id"]: json.loads(l) for l in SAMPLE.read_text().splitlines() if l.strip()}
    res = []
    for path in sorted((OUT / "runs").glob("*.jsonl")):
        rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        rows = [r for r in rows if r["id"] in sample]
        ans = [r for r in rows if r["real"] is not None]
        real = [r for r in ans if r["key"] == "real"]
        noise = [r for r in ans if r["key"] == "noise"]
        kept = sum(r["real"] for r in real) / len(real) if real else 0
        cleared = sum(not r["real"] for r in noise) / len(noise) if noise else 0
        res.append({"model": path.stem.replace("__", "/"), "asked": len(rows), "answered": len(ans),
                    "answered_pct": round(100 * len(ans) / max(len(sample), 1), 1),
                    "real_kept_pct": round(100 * kept, 1), "noise_cleared_pct": round(100 * cleared, 1),
                    "balanced_pct": round(50 * (kept + cleared), 1),
                    "median_secs": statistics.median([r["secs"] for r in ans]) if ans else None})
    # Rank: answering at all comes first (a referee that stalls is the problem
    # being fixed), then balanced accuracy, then catching real errors.
    res.sort(key=lambda r: (r["answered_pct"] >= 90, r["balanced_pct"], r["real_kept_pct"]), reverse=True)
    lines = ["# Referee bench", "", f"Answer key: Claude held review, {len(sample)} findings "
             f"({sum(s['key'] == 'real' for s in sample.values())} real). Prompt and call: production ADJ_SYS + work_pipeline.call.",
             "", "| model | answered | real kept | noise cleared | balanced | median s |", "|---|---|---|---|---|---|"]
    for r in res:
        lines.append(f"| {r['model']} | {r['answered']}/{len(sample)} | {r['real_kept_pct']}% | {r['noise_cleared_pct']}% | "
                     f"{r['balanced_pct']}% | {r['median_secs']} |")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    (OUT / "scores.json").write_text(json.dumps(res, indent=1))
    print("\n".join(lines))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "run", "score"])
    ap.add_argument("--n", type=int, default=160)
    ap.add_argument("--per-book", type=int, default=4)
    ap.add_argument("--models", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.n, a.per_book)
    elif a.cmd == "run":
        run([m for m in a.models.split(",") if m], a.workers)
    else:
        score()
    return 0


if __name__ == "__main__":
    sys.exit(main())
