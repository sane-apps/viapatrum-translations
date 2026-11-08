#!/usr/bin/env python3
"""Reference ratchet: the count of impossible Bible references may only go down (Nov 8, 2026).

Why: Larry Sanger found wrong references in our published texts; a corpus sweep found about one in four pointer
references wrong and 667 citing verses that do not exist (594 of them Psalms in Greek numbering). The sweep fixes
what two independent judges agree on, and ref_gate checks every reference in new work. This check makes sure the
count of the plainly impossible ones (no such chapter or verse in the English Bible, or a translator placeholder
such as "(prophetic allusion)") never grows again.

Counts per book over books/*/translations/*_english.json, using ref_gate's parser (the same one the gate uses).
  check (default): exit 1 when a book has more than its baseline, or a book not in the baseline that holds a
                   current work receipt (it went through ref_gate) has any.
  --update:        write the current counts as the baseline (run after a fix lowers them; never to excuse a rise).
Baseline: data/reference_ratchet.json. Run: python3 -I scripts/ref_ratchet.py [--update]
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOKS = ROOT / "books"
BASELINE = ROOT / "data" / "reference_ratchet.json"
sys.path.insert(0, str(HERE))
import ref_gate as G  # noqa: E402

TAG = re.compile(r"\((?:prophetic allusion|allusion|echo|cf\.)\)")


def greek_addition(book: str, ch: int, v: int | None) -> bool:
    """Real verses of the Greek (and Catholic) Bible: Daniel's Song of the Three (3:24-90), Susanna (13), Bel (14);
    the additions to Esther (Vulgate 10:4-16:24)."""
    return ((book == "Daniel" and ((ch == 3 and v is not None and 31 <= v <= 100) or ch in (13, 14)))
            or (book == "Esther" and 11 <= ch <= 16))


def english_rows(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = data if isinstance(data, list) else data.get("sections", []) if isinstance(data, dict) else []
    out = []
    for row in rows:
        if isinstance(row, dict):
            eng = row.get("english") or []
            out.append([str(p) for p in eng] if isinstance(eng, list) else [str(eng)])
    return out


def count_book(book_dir: Path) -> tuple[int, list[str]]:
    n, examples = 0, []
    for ef in sorted((book_dir / "translations").glob("*_english.json")):
        for paras in english_rows(ef):
            for _pi, _s, _e, printed, book, ch, v, _ve in G.refs_in(paras):
                if not G.exists(book, ch, v) and not greek_addition(book, ch, v):
                    n += 1
                    if len(examples) < 3:
                        examples.append(printed)
            for para in paras:
                for m in TAG.finditer(para):
                    n += 1
                    if len(examples) < 3:
                        examples.append(m.group(0))
    return n, examples


def current() -> dict[str, tuple[int, list[str]]]:
    out = {}
    for b in sorted(p for p in BOOKS.iterdir() if (p / "translations").is_dir()):
        n, ex = count_book(b)
        if n:
            out[b.name] = (n, ex)
    return out


def main(argv: list[str]) -> int:
    now = current()
    total = sum(n for n, _ in now.values())
    if "--update" in argv:
        BASELINE.write_text(json.dumps({"updated": time.strftime("%Y-%m-%d"), "total": total,
                                        "books": {b: n for b, (n, _) in now.items()}}, indent=1) + "\n")
        print(f"reference ratchet: baseline written, {total} impossible references in {len(now)} books")
        return 0
    if not BASELINE.is_file():
        print("reference ratchet: no baseline (run with --update once)")
        return 1
    base = json.loads(BASELINE.read_text())["books"]
    certified = None
    bad = []
    for b, (n, ex) in now.items():
        if b in base:
            if n > base[b]:
                bad.append(f"{b}: {n} > baseline {base[b]} (e.g. {', '.join(ex)})")
            continue
        if (BOOKS / b / "reviews" / "work_receipt.json").is_file():
            if certified is None:
                import work_pipeline as W
                certified = W.certified
            try:
                ok = certified(b)
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                bad.append(f"{b}: {n} impossible references in a certified work (e.g. {', '.join(ex)})")
    if bad:
        print("reference ratchet: FAIL")
        for x in bad[:20]:
            print("  ", x)
        return 1
    print(f"reference ratchet: ok ({total} impossible references; baseline {sum(base.values())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
