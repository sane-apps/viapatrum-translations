#!/usr/bin/env python3
"""Regression: possible/thematic allusions must never become Bible links.

A "possible" allusion with no quotation or echo in the locked source is
padding. Honest labeling (certainty/reason fields) does not legitimize it:
caption lines stay plain text, never satisfy the >=1-link gate, and a DOCX
whose links come only from Possible-allusion captions fails verify.
"""
from __future__ import annotations

import io
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from pipeline.bible_links import BibleLinker
from pipeline.verify_docx import verify_docx


def make_docx(path: Path, paragraphs: list[str]) -> Path:
    runs = "".join(
        f"<w:p><w:r><w:t xml:space=\"preserve\">{t}</w:t></w:r></w:p>"
        for t in paragraphs
    )
    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{runs}</w:body></w:document>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", xml)
    path.write_bytes(buf.getvalue())
    return path


HEADWORD = "[[@Headword:ente-1]]"
POSSIBLE_CAPTION = (
    "Possible allusion: [[Exodus 3:14 &gt;&gt; Bible:Exodus 3:14]] "
    "&#8212; Thematic affinity; no explicit quotation in text"
)
GENUINE_INLINE = (
    "Until the law, sin was in the world "
    "([[Romans 5:13 &gt;&gt; Bible:Romans 5:13]])."
)


class AllusionPaddingTest(unittest.TestCase):
    def test_note_caption_emits_no_link_and_records_nothing(self) -> None:
        linker = BibleLinker()
        line = "Possible allusion: Exodus 3:14 \u2014 no explicit quotation in text"
        out = linker.bible_text(line, key="ente-1", label="Ente 1", note=True)
        self.assertEqual(out, line)
        self.assertNotIn(">> Bible:", out)
        self.assertEqual(linker.link_receipts, [])

    def test_inline_prose_still_links(self) -> None:
        linker = BibleLinker()
        out = linker.bible_text("sin was in the world (Romans 5:13).", key="k", label="L")
        self.assertIn(">> Bible:Romans 5:13", out)
        self.assertEqual(len(linker.link_receipts), 1)
        self.assertFalse(linker.link_receipts[0]["editorial"])

    def test_verify_rejects_only_possible_caption_links(self) -> None:
        with TemporaryDirectory() as tmp:
            docx = make_docx(Path(tmp) / "padded.docx", [HEADWORD, POSSIBLE_CAPTION])
            errs = verify_docx(docx)
            self.assertTrue(any("Possible allusion" in e for e in errs), errs)

    def test_verify_accepts_genuine_inline_link(self) -> None:
        with TemporaryDirectory() as tmp:
            docx = make_docx(Path(tmp) / "good.docx", [HEADWORD, GENUINE_INLINE])
            self.assertEqual(verify_docx(docx), [])

    def test_verify_caption_check_is_paragraph_scoped(self) -> None:
        # A plain caption in one paragraph must not span forward into the next
        # paragraph's legitimate inline cite (julian-of-eclanum false positive:
        # 20 hits over whole-document text, zero clickable captions present).
        plain_caption = (
            "Possible allusion: Exodus 3:14 \u2014 Thematic affinity; "
            "no explicit quotation in text"
        )
        with TemporaryDirectory() as tmp:
            docx = make_docx(
                Path(tmp) / "scoped.docx", [HEADWORD, plain_caption, GENUINE_INLINE]
            )
            errs = verify_docx(docx)
            self.assertFalse(
                [e for e in errs if "Possible allusion" in e], errs
            )

    def test_verify_zero_links_still_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            docx = make_docx(Path(tmp) / "bare.docx", [HEADWORD, "Plain metaphysics."])
            errs = verify_docx(docx)
            self.assertTrue(any("no Bible datatype links" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
