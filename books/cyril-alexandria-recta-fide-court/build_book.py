"""Stub builder for Cyril of Alexandria: On the True Faith to the Imperial Women. Replace with book-specific assembly; use pipeline helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from pipeline.bible_links import BibleLinker  # noqa: E402
from pipeline.docx_helpers import (  # noqa: E402
    add_heading_with_headword,
    assert_internal_links,
    setup_document,
)


def main():
    doc = setup_document(
        title="Cyril of Alexandria: On the True Faith to the Imperial Women",
        author="Cyril of Alexandria",
        subject="English translation with Scripture links",
        comments="Private study edition. AI-assisted translation.",
    )
    linker = BibleLinker()
    # Example section — replace with real records from translations/
    from pipeline.docx_helpers import BookmarkStore

    bookmarks = BookmarkStore()
    add_heading_with_headword(doc, bookmarks, "Sample section", 1, "sample")
    p = doc.add_paragraph()
    p.add_run(linker.bible_text("See Romans 5:12.", key="sample", label="Sample section"))
    assert_internal_links(doc, bookmarks.ids)
    out = ROOT / "cyril-alexandria-recta-fide-court English.docx"
    doc.save(out)
    receipt = {
        "section_count": 1,
        "bible_links": linker.link_receipts,
        "bookmark_count": len(bookmarks.ids),
        "scripture_index_entries": len(linker.index),
        "records": [{"key": "sample", "label": "Sample section"}],
    }
    (ROOT / "build_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(out), "sections": 1, "bible_links": len(linker.link_receipts)}))


if __name__ == "__main__":
    main()
