"""Build Cyril of Alexandria Commentary on Isaiah Logos Personal Book DOCX."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent
REPO = BOOK_DIR.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from build_pbb_docx import collect_sections  # noqa: E402
from pipeline.bible_links import BibleLinker  # noqa: E402
from pipeline.book_frontmatter import add_docx_frontmatter, load_frontmatter  # noqa: E402
from pipeline.docx_helpers import setup_document  # noqa: E402
from pipeline.verify_docx import verify_docx  # noqa: E402

OUT_DOCX = BOOK_DIR / "cyril-isaiah.docx"
RECEIPT = BOOK_DIR / "build_receipt.json"

# Front matter (title page, license, Introduction) comes from the shared
# pipeline.book_frontmatter module reading book.yml + intro.md.

_SUPER = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

_ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
_REM_PART = {"early": 1, "mid": 2, "close": 3}
_REM_TITLE = re.compile(r"^Book (I{1,3}|IV|V) (.+?) rem (early|mid|close)( CLOSEOUT)?$")


def clean_slice_title(stem: str) -> str:
    """Slice stem (isaiah_book2-tomos2_open) -> clean English H1."""
    short = stem[7:] if stem.startswith("isaiah_") else stem
    if short == "prol":
        return "Prologue"
    m = re.fullmatch(r"book(\d+)-tomos(\d+)_(open|rem)", short)
    if m:
        tail = "opening" if m.group(3) == "open" else "continued"
        return "Book %s, Tomos %s %s" % (m.group(1), m.group(2), tail)
    m = re.fullmatch(r"book(\d+)-logos(\d+)_(open|rem)", short)
    if m:
        tail = "opening" if m.group(3) == "open" else "continued"
        return "Book %s, Logos %s %s" % (m.group(1), m.group(2), tail)
    m = re.fullmatch(r"book(\d+)-part(\d+)_(open|rem)", short)
    if m:
        tail = "opening" if m.group(3) == "open" else "continued"
        return "Book %s, Part %s %s" % (m.group(1), m.group(2), tail)
    m = re.fullmatch(r"book(\d+)_(open|rem)", short)
    if m:
        tail = "opening" if m.group(2) == "open" else "continued"
        return "Book %s %s" % (m.group(1), tail)
    m = re.fullmatch(r"logos(\d+)_(open|rem)", short)
    if m:
        tail = "opening" if m.group(2) == "open" else "continued"
        return "Book 1, Logos %s %s" % (m.group(1), tail)
    raise ValueError("unknown isaiah slice stem: %s" % stem)


def clean_section_title(title: str) -> str:
    """'Book II Tomos 2 rem early' -> 'Book 2, Tomos 2, continued (1 of 3)'.

    Only rem/CLOSEOUT jargon is touched; already-English titles pass through.
    """
    m = _REM_TITLE.match(title.strip())
    if not m:
        return title
    book = _ROMAN[m.group(1)]
    rest = m.group(2).strip()
    part = _REM_PART[m.group(3)]
    if rest == "opening":
        return "Book %d opening, continued (%d of 3)" % (book, part)
    if rest.lower().startswith("part "):
        rest = "Part " + rest[5:]
    return "Book %d, %s, continued (%d of 3)" % (book, rest, part)


def main() -> None:
    fm = load_frontmatter(str(BOOK_DIR))
    sections = collect_sections(BOOK_DIR, None)
    linker = BibleLinker()
    doc = setup_document(
        title=fm["title"],
        author=fm["author"],
        subject="New English translation for Logos",
        keywords="Cyril of Alexandria, Commentary on Isaiah, Isaiah",
    )
    add_docx_frontmatter(doc, str(BOOK_DIR))

    tn_counter = 0
    tn_articles: list[tuple[int, str]] = []
    records: list[dict] = []
    last_slice = None
    for item in sections:
        if item["slice"] != last_slice:
            doc.add_heading(clean_slice_title(item["slice"]), level=1)
            last_slice = item["slice"]
        title = clean_section_title(item["title"])
        headword = f"{title} ({item['section']})"
        doc.add_heading(title, level=2)
        doc.add_paragraph(f"[[@Headword:{headword}]]")
        paras = item["english"] or ["[English pending.]"]
        n_paras = 0
        for para in paras:
            linked = linker.bible_text(str(para), key=item["section"], label=title)
            doc.add_paragraph(linked)
            n_paras += 1
        for note in item["translator_notes"]:
            tn_counter += 1
            mark = str(tn_counter).translate(_SUPER)
            doc.add_paragraph(f"[[{mark} >> Headword:TN {tn_counter}]]")
            tn_articles.append((tn_counter, str(note)))
        records.append(
            {"key": item["section"], "label": title, "paragraphs": n_paras,
             "slice": item["slice"]}
        )
    if tn_articles:
        doc.add_heading("Translator Notes", level=1)
        for num, text in tn_articles:
            doc.add_heading(f"TN {num}", level=3)
            doc.add_paragraph(f"[[@Headword:TN {num}]]")
            doc.add_paragraph(text)

    tmp = OUT_DOCX.with_name(OUT_DOCX.name + ".tmp")
    doc.save(str(tmp))
    errors = verify_docx(tmp)
    if errors:
        tmp.unlink(missing_ok=True)
        raise SystemExit("verify_docx refused the build:\n- " + "\n- ".join(errors))
    tmp.replace(OUT_DOCX)

    receipt = {
        "title": fm["title"],
        "section_count": len(records),
        "paragraph_count": sum(r["paragraphs"] for r in records),
        "bookmark_count": 0,
        "footnote_count": 0,
        "tn_note_count": len(tn_articles),
        "bible_links": linker.link_receipts,
        "scripture_index_entries": sum(len(v) for v in linker.index.values()),
        "records": records,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(
        f"wrote {OUT_DOCX.name}: {len(records)} sections, "
        f"{len(linker.link_receipts)} bible links, {len(tn_articles)} TN notes"
    )


if __name__ == "__main__":
    main()
