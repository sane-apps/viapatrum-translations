#!/usr/bin/env python3
"""Search the whole library, in the original language and in English.

Built for the Timeline question dossiers (owner 2026-10-13: "a clear list of
source quotes that really capture the authors' views"). The belief search
(doctrine_map.py) only sees passages that already have English and asks a
model to grade them; this tool reads every locked Greek or Latin section,
translated or not, so a reader can find the classic witnesses (Tertullian,
On Baptism 18, untranslated) and decide by reading.

Matching ignores Greek accents and breathings, final sigma, Latin u/v and i/j,
and case. Patterns are Python regular expressions over that normalised text.

  python3 scripts/corpus_search.py build                 # (re)index, ~1 min
  python3 scripts/corpus_search.py find 'paruul' 'baptiz|tingu' --author Origen
  python3 scripts/corpus_search.py find 'νηπι' 'βαπτισ' --near 300
  python3 scripts/corpus_search.py show tertullian-on-baptism 18

`find` takes one or more patterns; every pattern must match within --near
characters of the first one. Each hit prints the book, section, author, year,
whether English exists and whether the work is live, then the source context.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
INDEX = ROOT / "outputs" / "corpus-index" / "sections.jsonl"
RAW_INDEX = ROOT / "outputs" / "corpus-index" / "raw.jsonl"
RAW_CHUNK = 3000
SRC_KEYS = ("greek", "latin", "source", "text", "syriac", "coptic")


def norm(s: str) -> str:
    """Lower case, no Greek diacritics, one sigma, Latin u for v and i for j."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("ς", "σ").replace("ϲ", "σ").replace("v", "u").replace("j", "i")
    return re.sub(r"\s+", " ", s)


def joined(v) -> str:
    if isinstance(v, list):
        return " ".join(str(x) for x in v if x)
    return str(v or "")


def book_info(slug: str) -> dict:
    f = ROOT / "books" / slug / "book.yml"
    out = {"slug": slug, "author": "", "title": "", "year": None, "language": ""}
    if not f.is_file():
        return out
    t = f.read_text(encoding="utf-8", errors="replace")
    for k in ("author", "title", "language"):
        m = re.search(rf"^{k}:\s*\"?([^\"\n]+)\"?", t, re.M)
        if m:
            out[k] = m.group(1).strip()
    m = re.search(r"^year:\s*(\d{2,4})", t, re.M)
    if m:
        out["year"] = int(m.group(1))
    return out


def live_works() -> set[str]:
    d = SITE / "dist" / "works"
    return {p.name for p in d.iterdir() if p.is_dir()} if d.is_dir() else set()


def build() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import book_era
        year_of = book_era.book_year
    except Exception:  # noqa: BLE001
        year_of = lambda b: None  # noqa: E731
    live = live_works()
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    tmp = INDEX.with_suffix(".tmp")
    n = 0
    with open(tmp, "w", encoding="utf-8") as out:
        for book in sorted(os.listdir(ROOT / "books")):
            tdir = ROOT / "books" / book / "translations"
            if not tdir.is_dir():
                continue
            info = book_info(book)
            info["year"] = info["year"] or year_of(book)
            for src in sorted(glob.glob(str(tdir / "*_source.json"))):
                unit = Path(src).name[: -len("_source.json")]
                try:
                    S = json.loads(Path(src).read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                engf = Path(src[: -len("_source.json")] + "_english.json")
                E = {}
                if engf.is_file():
                    try:
                        E = {str(s.get("section")): s for s in json.loads(engf.read_text(encoding="utf-8")) if isinstance(s, dict)}
                    except (OSError, ValueError):
                        E = {}
                if not isinstance(S, list):
                    continue
                for s in S:
                    if not isinstance(s, dict):
                        continue
                    text = next((joined(s[k]) for k in SRC_KEYS if s.get(k)), "")
                    if not text.strip():
                        continue
                    sec = str(s.get("section"))
                    e = E.get(sec) or {}
                    rec = {"book": book, "unit": unit, "section": sec, "author": info["author"], "title": info["title"],
                           "year": info["year"], "lang": "greek" if s.get("greek") else "latin" if s.get("latin") else "other",
                           "head": s.get("title") or s.get("head") or s.get("locus") or "",
                           "source": text, "english": joined(e.get("english")), "live": book in live}
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n += 1
    tmp.rename(INDEX)
    print(f"indexed {n} sections -> {INDEX}")
    return 0


def build_raw() -> int:
    """Every raw source file (OCR text, TEI XML) in overlapping chunks. The
    section JSON is not always the text: some books hold one-line summaries
    there (Origen, Homilies on Leviticus, 2026-10-13), while the scan's OCR
    sits under sources/. Chunks overlap so a sentence is never cut in two."""
    n = 0
    tmp = RAW_INDEX.with_suffix(".tmp")
    RAW_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as out:
        for book in sorted(os.listdir(ROOT / "books")):
            sdir = ROOT / "books" / book / "sources"
            if not sdir.is_dir():
                continue
            info = book_info(book)
            for path in sorted(sdir.rglob("*")):
                if path.suffix.lower() not in (".txt", ".xml") or not path.is_file() or path.stat().st_size > 60_000_000:
                    continue
                try:
                    t = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if path.suffix.lower() == ".xml":
                    t = re.sub(r"<teiHeader.*?</teiHeader>", " ", t, flags=re.S)
                    t = re.sub(r"<[^>]+>", " ", t)
                t = re.sub(r"\s+", " ", t).strip()
                rel = str(path.relative_to(ROOT))
                for i in range(0, max(1, len(t)), RAW_CHUNK - 400):
                    chunk = t[i:i + RAW_CHUNK]
                    if len(chunk) < 40:
                        continue
                    out.write(json.dumps({"book": book, "file": rel, "offset": i, "author": info["author"],
                                          "year": info["year"], "text": chunk}, ensure_ascii=False) + "\n")
                    n += 1
    tmp.rename(RAW_INDEX)
    print(f"indexed {n} raw chunks -> {RAW_INDEX}")
    return 0


def find_raw(patterns: list[str], near: int, author: str, book: str, limit: int, width: int) -> int:
    if not RAW_INDEX.is_file():
        sys.exit("no raw index: run `corpus_search.py build --raw` first")
    rx = [re.compile(norm(p)) for p in patterns]
    a_rx = re.compile(author, re.I) if author else None
    b_rx = re.compile(book) if book else None
    shown, seen = 0, set()
    with open(RAW_INDEX, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if (a_rx and not a_rx.search(r["author"])) or (b_rx and not b_rx.search(r["book"])):
                continue
            n = norm(r["text"])
            for m in rx[0].finditer(n):
                lo, hi = max(0, m.start() - near), m.end() + near
                if all(x.search(n, lo, hi) for x in rx[1:]):
                    key = (r["file"], r["offset"] + m.start() // 500)
                    if key in seen:
                        break
                    seen.add(key)
                    c0, c1 = max(0, m.start() - width), min(len(n), m.end() + width)
                    print(f"\n[RAW {r['file']} @{r['offset'] + m.start()}] {r['author']} c.{r['year']}")
                    print("   …" + n[c0:c1] + "…")
                    shown += 1
                    break
            if shown >= limit:
                print(f"\n(limit {limit} reached)")
                break
    print(f"\n{shown} hit(s)")
    return 0


def records():
    if not INDEX.is_file():
        sys.exit("no index: run `corpus_search.py build` first")
    with open(INDEX, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def find(patterns: list[str], near: int, author: str, book: str, max_year: int, english: bool,
         limit: int, width: int) -> int:
    rx = [re.compile(norm(p)) for p in patterns]
    a_rx = re.compile(author, re.I) if author else None
    b_rx = re.compile(book) if book else None
    shown = 0
    for r in records():
        if a_rx and not a_rx.search(r["author"]):
            continue
        if b_rx and not b_rx.search(r["book"]):
            continue
        if max_year and (r["year"] or 9999) > max_year:
            continue
        hay = r["english"] if english else r["source"]
        if not hay:
            continue
        n = norm(hay)
        for m in rx[0].finditer(n):
            lo, hi = max(0, m.start() - near), m.end() + near
            if all(x.search(n, lo, hi) for x in rx[1:]):
                # Context from the same span of the normalised text, so offsets agree.
                c0, c1 = max(0, m.start() - width), min(len(n), m.end() + width)
                flag = ("EN" if r["english"] else "--") + ("/LIVE" if r["live"] else "")
                print(f"\n[{r['book']} §{r['section']}] {r['author']} c.{r['year']} {flag} :: {r['head'][:60]}")
                print("   …" + n[c0:c1] + "…")
                shown += 1
                break
        if shown >= limit:
            print(f"\n(limit {limit} reached)")
            break
    print(f"\n{shown} hit(s)")
    return 0


def show(book: str, section: str) -> int:
    for r in records():
        if r["book"] == book and r["section"] == section:
            print(f"[{book} §{section}] {r['author']} c.{r['year']} live={r['live']} unit={r['unit']} head={r['head']}")
            print("\nSOURCE:\n" + r["source"])
            print("\nENGLISH:\n" + (r["english"] or "(none)"))
            return 0
    print("not found")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    bp = sub.add_parser("build")
    bp.add_argument("--raw", action="store_true", help="also index raw OCR/TEI files under sources/")
    f = sub.add_parser("find")
    f.add_argument("patterns", nargs="+")
    f.add_argument("--near", type=int, default=400)
    f.add_argument("--author", default="")
    f.add_argument("--book", default="")
    f.add_argument("--max-year", type=int, default=0)
    f.add_argument("--english", action="store_true", help="search the English instead of the source")
    f.add_argument("--raw", action="store_true", help="search raw OCR/TEI source files instead of sections")
    f.add_argument("--limit", type=int, default=25)
    f.add_argument("--width", type=int, default=220)
    s = sub.add_parser("show")
    s.add_argument("book")
    s.add_argument("section")
    a = ap.parse_args()
    if a.cmd == "build":
        rc = build()
        return build_raw() if a.raw else rc
    if a.cmd == "find" and a.raw:
        return find_raw(a.patterns, a.near, a.author, a.book, a.limit, a.width)
    if a.cmd == "find":
        return find(a.patterns, a.near, a.author, a.book, a.max_year, a.english, a.limit, a.width)
    return show(a.book, a.section)


if __name__ == "__main__":
    sys.exit(main())
