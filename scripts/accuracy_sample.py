#!/usr/bin/env python3
"""Accuracy-audit sampler: seeded-random sample of passages where a unit has
BOTH locked source text and our English rendering.

Conventions (inspect, don't assume): books/<slug>/translations/<base>_source.json
(list of {section, greek|latin, ...}) pairs with <base>_english.json
(list of {section, english:[...], ...}). book.yml carries title/author/language.

Emits outputs/accuracy_packet.json entries:
  {book, tip_id, source_lang, source_text, our_english, context}
Deterministic under --seed. Validates the packet schema on write.

Usage:
  python3 scripts/accuracy_sample.py --n 40 --seed 20260916
  python3 scripts/accuracy_sample.py --n 40 --seed 20260916 --out outputs/accuracy_packet.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "books"
OUT_DEFAULT = ROOT / "outputs" / "accuracy_packet.json"

GREEK = re.compile("[\u0370-\u03ff\u1f00-\u1fff]")
SCAFFOLD = re.compile(
    r"\b(?:TODO|TBD|FIXME|YYYY|placeholder|scaffold|translation pending"
    r"|lemma-led open|lemma and argument toward the thesis"
    r"|\[n\d+\]|rem early|rem closeout)\b",
    re.I,
)


def visible(text: str) -> str:
    text = re.sub(r"\[\[([^\[\]]+?)\s*>>\s*[^\]]+\]\]", r"\1", text)
    return re.sub(r"\[\[@[^\]]+\]\]", "", text)


def source_text_of(entry: dict) -> tuple[str, str]:
    greek = entry.get("greek") or ""
    latin = entry.get("latin") or ""
    if isinstance(greek, list):
        greek = "\n".join(str(x) for x in greek)
    if isinstance(latin, list):
        latin = "\n".join(str(x) for x in latin)
    greek, latin = str(greek).strip(), str(latin).strip()
    if greek and latin:
        return "Greek+Latin", (greek + "\n" + latin).strip()
    if greek:
        return "Greek", greek
    if latin:
        return "Latin", latin
    return "", ""


def english_of(entry: dict) -> str:
    eng = entry.get("english") or []
    if isinstance(eng, str):
        eng = [eng]
    return visible(" ".join(str(x) for x in eng)).strip()


def book_meta(slug: str) -> dict:
    yml = BOOKS / slug / "book.yml"
    meta = {"title": "", "author": "", "language": ""}
    try:
        for line in yml.read_text(encoding="utf-8").splitlines():
            for key in ("title", "author", "language"):
                if line.startswith(key + ":"):
                    meta[key] = line.split(":", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return meta


def is_genuine_rendering(english: str, source: str) -> bool:
    if len(english) < 200 or len(source) < 100:
        return False
    if SCAFFOLD.search(english):
        return False
    greek_chars = len(GREEK.findall(english))
    if greek_chars / max(len(english), 1) > 0.15:
        return False
    return True


def collect_candidates() -> dict[str, list[dict]]:
    by_book: dict[str, list[dict]] = {}
    for eng_path in sorted((BOOKS).glob("*/translations/*_english.json")):
        slug = eng_path.parent.parent.name
        src_path = eng_path.with_name(eng_path.name[: -len("_english.json")] + "_source.json")
        if not src_path.is_file():
            continue
        try:
            eng = json.loads(eng_path.read_text(encoding="utf-8"))
            src = json.loads(src_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(eng, list) or not isinstance(src, list):
            continue
        src_by_sec = {str(e.get("section")): e for e in src if isinstance(e, dict)}
        meta = book_meta(slug)
        base = eng_path.name[: -len("_english.json")]
        for entry in eng:
            if not isinstance(entry, dict):
                continue
            sec = str(entry.get("section"))
            s = src_by_sec.get(sec)
            if not s:
                continue
            lang, stext = source_text_of(s)
            our = english_of(entry)
            if not lang or not is_genuine_rendering(our, stext):
                continue
            title_bits = [str(entry.get("title") or s.get("title") or "")]
            for k in ("locus", "head", "work", "part"):
                v = entry.get(k) or s.get(k)
                if v:
                    title_bits.append(f"{k}={v}")
            ctx = f"{meta['author']} — {meta['title']} [{', '.join(title_bits)}]"
            by_book.setdefault(slug, []).append(
                {
                    "book": slug,
                    "tip_id": f"{base}#{sec}",
                    "source_lang": lang,
                    "source_text": stext[:2500],
                    "our_english": our[:2500],
                    "context": ctx[:600],
                }
            )
    return by_book


PACKET_SCHEMA_KEYS = {
    "book": str,
    "tip_id": str,
    "source_lang": str,
    "source_text": str,
    "our_english": str,
    "context": str,
}


def validate_packet(items: list[dict]) -> None:
    assert isinstance(items, list) and items, "packet must be a non-empty list"
    seen = set()
    for e in items:
        assert isinstance(e, dict), f"entry not an object: {e!r:.80}"
        assert set(e.keys()) == set(PACKET_SCHEMA_KEYS), f"bad keys: {sorted(e.keys())}"
        for k, t in PACKET_SCHEMA_KEYS.items():
            assert isinstance(e[k], t) and e[k].strip(), f"bad {k} in {e.get('tip_id')}"
        assert e["source_lang"] in ("Greek", "Latin", "Greek+Latin"), e["source_lang"]
        assert e["tip_id"] not in seen, f"duplicate tip_id {e['tip_id']}"
        seen.add(e["tip_id"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260916)
    ap.add_argument("--per-book", type=int, default=2)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()

    by_book = collect_candidates()
    print(f"candidate books: {len(by_book)}, passages: {sum(len(v) for v in by_book.values())}", flush=True)
    rng = random.Random(args.seed)
    slugs = sorted(by_book)
    rng.shuffle(slugs)
    for v in by_book.values():
        rng.shuffle(v)
    picked: list[dict] = []
    idx = {s: 0 for s in slugs}
    while len(picked) < args.n:
        progressed = False
        for s in slugs:
            if idx[s] >= min(len(by_book[s]), args.per_book):
                continue
            picked.append(by_book[s][idx[s]])
            idx[s] += 1
            progressed = True
            if len(picked) >= args.n:
                break
        if not progressed:
            break
    if len(picked) < args.n:
        print(f"WARNING: only {len(picked)} genuine passages found", flush=True)
    validate_packet(picked)
    packet = {
        "audit": "accuracy",
        "seed": args.seed,
        "count": len(picked),
        "books_covered": len({e["book"] for e in picked}),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fidelity_standard": "docs/CHARTER.md: rendering must be new, made from the locked source; if a passage cannot be honestly rendered, say so openly rather than inventing it.",
        "items": picked,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(packet, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({len(picked)} items, {packet['books_covered']} books)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
