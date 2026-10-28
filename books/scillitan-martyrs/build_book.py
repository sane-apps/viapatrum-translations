"""Build Acts of the Scillitan Martyrs Logos Personal Book DOCX."""
from __future__ import annotations

import json
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

OUT_DOCX = BOOK_DIR / "scillitan-martyrs.docx"
RECEIPT = BOOK_DIR / "build_receipt.json"

_SUPER = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def main() -> None:
    fm = load_frontmatter(str(BOOK_DIR))
    sections = collect_sections(BOOK_DIR, None)
    linker = BibleLinker()
    doc = setup_document(
        title=fm["title"],
        author=fm["author"],
        subject="New English translation for Logos",
        keywords="Scillitan Martyrs, Speratus, Carthage, martyr acts, Saturninus",
    )
    add_docx_frontmatter(doc, str(BOOK_DIR))

    tn_counter = 0
    tn_articles: list[tuple[int, str]] = []
    records: list[dict] = []
    doc.add_heading("The Hearing at Carthage", level=1)
    for item in sections:
        title = item["title"]
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
        records.append({"key": item["section"], "label": title, "paragraphs": n_paras,
                        "slice": item["slice"]})
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
    print(f"wrote {OUT_DOCX.name}: {len(records)} sections, "
          f"{len(linker.link_receipts)} bible links, {len(tn_articles)} TN notes")


if __name__ == "__main__":
    main()
