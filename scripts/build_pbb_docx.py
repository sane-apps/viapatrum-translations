#!/usr/bin/env python3
"""Build one Logos Personal-Book DOCX from a book's english JSON.

Covers the per-slice layout (sorted translations/*_source.json with
*_english.json siblings, e.g. cyril-alexandria-isaiah). Other layouts
refuse; extend the reader when the next book needs it.

Markup follows docs/LOGOS_MARKUP.md:
  Title/Subtitle cover from book.yml (never hardcoded strings)
  Heading 1 per slice file, Heading 2 per section
  [[@Headword:...]] milestones as standalone paragraphs
  english paragraphs with [[... >> Bible:...]] via BibleLinker receipts
  translator notes as Headword TN marks + TN articles (no Word footnotes)

The verify_docx gate runs before the final path is written: a failing
build never lands. Zero Bible links is the honest hold, not an error
to pad around.

Usage:
  python3 scripts/build_pbb_docx.py --book cyril-alexandria-isaiah \\
      --out books/cyril-alexandria-isaiah/cyril-isaiah.docx [--sections a,b]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from pipeline.bible_links import BibleLinker  # noqa: E402
from pipeline.book_meta import load_book_meta  # noqa: E402
from pipeline.docx_helpers import setup_document  # noqa: E402
from pipeline.verify_docx import verify_docx  # noqa: E402

_SUPER = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _slice_title(stem: str) -> str:
    short = stem[7:] if stem.startswith("isaiah_") else stem
    return short.replace("_", " ").replace("-", " ").strip().title() or stem


def collect_sections(book_dir: Path, only: set[str] | None) -> list[dict]:
    trans = book_dir / "translations"
    sources = sorted(trans.glob("*_source.json"))
    if not sources:
        raise SystemExit(f"No per-slice source layout under {trans}; refusing")
    sections = []
    for src in sources:
        eng_path = src.with_name(src.name.replace("_source.json", "_english.json"))
        if not eng_path.is_file():
            raise SystemExit(f"Missing english sibling for {src.name}; refusing")
        src_rows = json.loads(src.read_text(encoding="utf-8"))
        eng_rows = json.loads(eng_path.read_text(encoding="utf-8"))
        src_rows = src_rows if isinstance(src_rows, list) else [src_rows]
        eng_rows = eng_rows if isinstance(eng_rows, list) else [eng_rows]
        for i, srow in enumerate(src_rows):
            section = str(srow.get("section") or "")
            if only is not None and section not in only:
                continue
            erow = eng_rows[i] if i < len(eng_rows) else {}
            sections.append({
                "slice": src.stem.replace("_source", ""),
                "section": section,
                "title": str(erow.get("title") or srow.get("head") or section),
                "english": list(erow.get("english") or []),
                "translator_notes": list(erow.get("translator_notes") or []),
            })
    if only:
        missing = only - {s["section"] for s in sections}
        if missing:
            raise SystemExit(f"Unknown sections: {sorted(missing)}")
    if not sections:
        raise SystemExit("No sections collected; refusing to build an empty book")
    return sections


def build_docx(book: str, out: Path, only: set[str] | None) -> dict:
    book_dir = ROOT / "books" / book
    meta = load_book_meta(book_dir)
    sections = collect_sections(book_dir, only)
    linker = BibleLinker()
    doc = setup_document(
        title=meta["title"],
        author=meta["author"],
        subject=meta.get("edition", ""),
        keywords=meta.get("slug", book),
        comments=meta.get("blurb", meta.get("description", "")),
    )
    doc.add_paragraph(meta["title"], style="Title")
    doc.add_paragraph(meta["author"], style="Subtitle")
    if meta.get("edition"):
        doc.add_paragraph(str(meta["edition"]), style="Subtitle")

    tn_counter = 0
    tn_articles: list[tuple[int, str]] = []
    last_slice = None
    for item in sections:
        if item["slice"] != last_slice:
            doc.add_heading(_slice_title(item["slice"]), level=1)
            last_slice = item["slice"]
        headword = f"{item['title']} ({item['section']})"
        doc.add_heading(item["title"], level=2)
        doc.add_paragraph(f"[[@Headword:{headword}]]")
        paras = item["english"] or ["[English pending.]"]
        for para in paras:
            linked = linker.bible_text(str(para), key=item["section"], label=item["title"])
            doc.add_paragraph(linked)
        for note in item["translator_notes"]:
            tn_counter += 1
            mark = str(tn_counter).translate(_SUPER)
            doc.add_paragraph(f"[[{mark} >> Headword:TN {tn_counter}]]")
            tn_articles.append((tn_counter, str(note)))
    if tn_articles:
        doc.add_heading("Translator Notes", level=1)
        for num, text in tn_articles:
            doc.add_heading(f"TN {num}", level=3)
            doc.add_paragraph(f"[[@Headword:TN {num}]]")
            doc.add_paragraph(text)

    tmp = out.with_name(out.name + ".tmp")
    doc.save(str(tmp))
    errors = verify_docx(tmp)
    if errors:
        tmp.unlink(missing_ok=True)
        raise SystemExit("verify_docx refused the build:\n- " + "\n- ".join(errors))
    tmp.replace(out)
    return {
        "out": str(out),
        "sections": len(sections),
        "bible_links": len(linker.link_receipts),
        "tn_notes": len(tn_articles),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sections", default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.sections.split(",") if s.strip()} or None
    try:
        receipt = build_docx(args.book, Path(args.out), only)
    except (SystemExit, ValueError) as exc:
        print(f"build_pbb_docx: {exc}", flush=True)
        return 1
    print(f"Built {receipt['out']}: "
          f"{receipt['sections']} sections, "
          f"{receipt['bible_links']} Bible links, "
          f"{receipt['tn_notes']} TN notes", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
