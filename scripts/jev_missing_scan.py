#!/usr/bin/env python3
"""Missing-citation queue producer (offline; feeds jev_cite_correct --mode backfill).

Scans book English for quoted-but-uncited sentences, scores each quote
against the local KJV by shared distinctive tokens, and emits flags:
{book, section, sentence, quote, best, shared, noul}.
noul is the shared-token count (float); backfill --min-conf filters on it.
Precision gates live downstream (proposer + Jev verifier + KJV overlap);
this scan favors recall.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_promote as promote  # noqa: E402
import jev_cite_check as cite  # noqa: E402
import jev_cite_correct as cc  # noqa: E402
import kjv_lookup  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QUOTE_CHARS = "'\u2018\u2019\u201c\u201d\""
_OPENER_PRECEDERS = set(" \t\n([{\"'\"‘“;—–-:")
_CLOSER_FOLLOWERS = set(" \t\n.,;:!?)]}'\"’”—–")


def quoted_segments(sentence: str, min_words: int = 6):
    """Text between quote-char pairs.

    A quote char opens only after whitespace/opening punctuation, so
    possessives ("Christ’s") never seed phantom quotes (live 2026-09-25).
    """
    segs = []
    i, n, opener = 0, len(sentence), -1
    while i < n:
        if sentence[i] in QUOTE_CHARS:
            if opener < 0:
                if i == 0 or sentence[i - 1] in _OPENER_PRECEDERS:
                    opener = i
            else:
                if i + 1 >= n or sentence[i + 1] in _CLOSER_FOLLOWERS:
                    segs.append(sentence[opener + 1:i])
                    opener = -1
        i += 1
    if opener >= 0:
        segs.append(sentence[opener + 1:])  # unclosed run-on quote
    for seg in segs:
        if len(re.findall(r"[A-Za-z]+", seg)) >= min_words:
            yield seg.strip()


def uncited_quotes(paras):
    """(sentence, quote) for quoted sentences carrying no citation."""
    for para in paras:
        for sent in promote.split_sentences(para):
            if not sent or "[English pending" in sent:
                continue
            if cc.ref_spans(sent):
                continue
            for quote in quoted_segments(sent):
                yield sent, quote
                break


def build_index(verses):
    """token -> [(book_id, chapter, verse)] over (id, ch, v, text) rows."""
    index: dict = {}
    for book_id, ch, v, text in verses:
        for tok in cc._overlap_tokens(text):
            index.setdefault(tok, []).append((book_id, ch, v))
    return index


def kjv_verses():
    for book_id, chapters in kjv_lookup._load().items():
        for ci, ch in enumerate(chapters, 1):
            for vi, text in enumerate(ch, 1):
                yield book_id, ci, vi, text


def best_match(quote: str, index):
    """((book_id, chapter, verse), shared) for the quote's top verse."""
    votes: Counter = Counter()
    for tok in cc._overlap_tokens(quote):
        for ref in index.get(tok, ()):
            votes[ref] += 1
    if not votes:
        return None, 0
    ref, shared = votes.most_common(1)[0]
    return ref, shared


def scan_book(book: str, index, min_shared: int):
    tdir = ROOT / "books" / book / "translations"
    if not tdir.is_dir():
        return []
    out = []
    for ef in sorted(tdir.glob("*_english.json")):
        try:
            data = json.loads(ef.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            section = str(row.get("section"))
            for sent, quote in uncited_quotes(row.get("english") or []):
                ref, shared = best_match(quote, index)
                if ref is None or shared < min_shared:
                    continue
                out.append({"book": book, "section": section,
                            "sentence": sent, "quote": quote,
                            "best": cite.display_ref(ref),
                            "shared": shared, "noul": float(shared)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default="")
    ap.add_argument("--min-shared", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    if args.books:
        books = [b.strip() for b in args.books.split(",") if b.strip()]
    else:
        books = sorted(json.loads(
            (ROOT / "outputs/logos_uploads.json").read_text(encoding="utf-8")))
    print("indexing KJV...", flush=True)
    index = build_index(kjv_verses())
    flags = []
    for book in books:
        found = scan_book(book, index, args.min_shared)
        flags.extend(found)
        print(f"{book}: {len(found)}", flush=True)
    flags.sort(key=lambda r: -r["shared"])
    if args.limit:
        flags = flags[:args.limit]
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for flag in flags:
                fh.write(json.dumps(flag, ensure_ascii=False) + "\n")
    print(f"done: {len(flags)} missing-cite candidates", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
