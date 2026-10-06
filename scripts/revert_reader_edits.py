#!/usr/bin/env python3
"""Undo reader-fix edits in certified works (2026-10-05).

Reader-fix edits came from readers who never saw the source. A blind sample of
100 live reader edits, judged against the source, found 38 made the English
less faithful, 23 more faithful, 39 no different (25 in the first mixed sample
of 75 and 75 more; scratchpad edit-sample, docs/QUALITY_AUDIT_20261005.md).
The step is off since 02903843e; this removes what it left behind.

Per section: undo the reader edits newest first (only where the edited words
are present exactly once and the original words are not), then run the blind
two-family source check on the reverted and the current English. Keep the
revert when it has no more confirmed problems than the current text (the same
rule the reader-fix step used to accept its edits). Then update the book's
English file, the staged section, its justification, and the receipt hashes.

  python3 scripts/revert_reader_edits.py            # dry run: what would revert
  python3 scripts/revert_reader_edits.py --apply [--book slug]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import threading
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as W  # noqa: E402


def is_reader_repair(r: dict) -> bool:
    return any(isinstance(p, dict) and "variants" in p for p in r.get("problems") or [])


def undo(english: list[str], repairs: list[dict]) -> tuple[list[str], int]:
    text = "\n\n".join(english)
    n = 0
    for r in reversed(repairs or []):
        if not is_reader_repair(r):
            continue
        for e in reversed(r.get("edits") or []):
            if not isinstance(e, dict):
                continue
            old, new = str(e.get("old", "")), str(e.get("new", ""))
            if old and new and old != new and text.count(new) == 1 and old not in text:
                text = text.replace(new, old)
                n += 1
    return [x for x in text.split("\n\n") if x.strip()], n


def plan(book: str) -> list[dict]:
    pairs = W.load_pairs(book)
    secs = W.staged_sections(book, pairs)
    out = []
    for p, s in zip(pairs, secs):
        j = s["_j"]
        cur = j.get("pass_b_english") or []
        if cur != p["english"]:
            continue  # stage and book disagree: leave it alone
        rev, n = undo(cur, j.get("repairs") or [])
        if n and rev != cur:
            out.append({"pair": p, "sec": s, "current": cur, "reverted": rev, "undone": n})
    return out


def judge(book: str, item: dict, brief: dict) -> dict:
    p = item["pair"]
    book_lang = W.LANGNAME.get(W.detect_lang(W.load_pairs(book), W.book_meta(book)), "Greek")
    lang = W.LANGNAME.get(p.get("lang") or "", book_lang)
    with ThreadPoolExecutor(2) as ex:
        f_rev = ex.submit(W.baseline_check, p, item["reverted"], brief, lang)
        f_cur = ex.submit(W.baseline_check, p, item["current"], brief, lang)
        rev, cur = f_rev.result(), f_cur.result()
    if rev.get("error") or cur.get("error"):
        return {**item, "keep_revert": False, "why": "checker unavailable"}
    n_rev, n_cur = len(rev.get("confirmed", [])), len(cur.get("confirmed", []))
    return {**item, "keep_revert": n_rev <= n_cur, "n_rev": n_rev, "n_cur": n_cur}


def write_back(book: str, done: list[dict]) -> None:
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    by_file: dict[str, list] = {}
    for d in done:
        by_file.setdefault(d["pair"]["eng_file"], []).append(d)
    for ef, items in by_file.items():
        data = json.load(open(ef))
        lst = data if isinstance(data, list) else data.get("sections", [])
        by = {str(r.get("section")): r for r in lst if isinstance(r, dict)}
        for d in items:
            by[d["pair"]["id"]]["english"] = d["reverted"]
        Path(ef).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    jdir = W.BOOKS / book / "reviews" / "justifications"
    for d in done:
        j = d["sec"]["_j"]
        j["pass_b_english"] = d["reverted"]
        j.setdefault("reverted_reader_edits", []).append(
            {"at": stamp, "undone": d["undone"], "confirmed_before": d["n_cur"], "confirmed_after": d["n_rev"]})
        d["sec"]["_file"].write_text(json.dumps(j, indent=1, ensure_ascii=False))
        jf = jdir / (re.sub(r"[^A-Za-z0-9_.-]", "_", d["pair"]["id"]) + ".json")
        if jf.exists():
            jj = json.loads(jf.read_text())
            jj["pass_b_english"] = d["reverted"]
            jj["reverted_reader_edits"] = j["reverted_reader_edits"]
            jf.write_text(json.dumps(jj, indent=1, ensure_ascii=False))
    rpath = W.BOOKS / book / "reviews" / "work_receipt.json"
    rec = json.loads(rpath.read_text())
    new_sha = {d["pair"]["id"]: W.sha("\n".join(d["reverted"])) for d in done}
    for s in rec["sections"]:
        if s["section"] in new_sha:
            s["english_sha256"] = new_sha[s["section"]]
    rec.setdefault("revisions", []).append({
        "at": stamp, "kind": "reverted_reader_edits", "sections": sorted(new_sha),
        "edits_undone": sum(d["undone"] for d in done),
        "rule": "blind two-family source check: reverted text has no more confirmed problems than the edited text",
        "evidence": "docs/QUALITY_AUDIT_20261005.md (reader edits: 38 worse, 23 better, 39 equal of 100)"})
    rpath.write_text(json.dumps(rec, indent=1, ensure_ascii=False))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--book", default="")
    a = ap.parse_args(argv)
    books = [a.book] if a.book else sorted(p.name for p in W.BOOKS.iterdir() if p.is_dir() and W.certified(p.name))
    plans = {b: plan(b) for b in books}
    plans = {b: v for b, v in plans.items() if v}
    print(f"{len(plans)} certified works, {sum(len(v) for v in plans.values())} sections, "
          f"{sum(i['undone'] for v in plans.values() for i in v)} reader edits to undo", flush=True)
    if not a.apply:
        return 0
    W.TOKENS["cf"], W.TOKENS["nv"] = W.secret("CLOUDFLARE_API_TOKEN"), W.secret("NV_API_KEY")
    totals = {"kept": 0, "refused": 0, "books_ok": 0, "books_bad": []}
    lock = threading.Lock()

    def one_book(b: str) -> None:
        items = plans[b]
        brief = json.loads((W.STAGE / b / "brief.json").read_text())
        with ThreadPoolExecutor(W.WORKERS) as ex:
            res = list(ex.map(lambda it: judge(b, it, brief), items))
        done = [r for r in res if r["keep_revert"]]
        with lock:  # one book's files at a time; the checks run in parallel
            if done:
                write_back(b, done)
            ok = W.certified(b)
            totals["kept"] += len(done)
            totals["refused"] += len(res) - len(done)
            totals["books_ok"] += ok
            if not ok:
                totals["books_bad"].append(b)
            print(f"{b}: reverted {len(done)}/{len(res)} sections "
                  f"({sum(d['undone'] for d in done)} edits); certified {ok}" + ("" if ok else " !!"), flush=True)

    # 2026-10-05: one book at a time took ~7 min each beside the running lanes.
    with ThreadPoolExecutor(int(os.environ.get("REVERT_BOOKS", "8"))) as ex:
        list(ex.map(one_book, list(plans)))
    print(json.dumps(totals), flush=True)
    return 2 if totals["books_bad"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
