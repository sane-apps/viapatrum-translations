"""Shared front matter for Logos DOCX and the website: one source.

Every book renders the same brief opening from its own data:
  Title / Author ("A new English translation" implied, never shouted)
  small print: license (1 sentence) + status (1 sentence) + source (1 line)
  Introduction (Heading 1): author / context / contents from intro.md
  ...then the text. Nothing else before the meat.

Reads books/<slug>/book.yml + intro.md. Optional book.yml key
review_status: when "independently reviewed" the status line says so;
anything else (or absent) honestly says not yet. Builders call
add_docx_frontmatter; the site builder calls render_intro_html.
"""
from __future__ import annotations

import html
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from pb_sync import load_yml  # noqa: E402

LICENSE_LINE = (
    "© 2026 SaneApps. This translation is free to share and adapt, "
    "even commercially, as long as you credit SaneApps."
)


def load_frontmatter(book_dir: str) -> dict:
    """Return title/author/edition/intro paras/copyright lines/reviewed."""
    yml = load_yml(os.path.join(book_dir, "book.yml"))
    with open(os.path.join(book_dir, "intro.md"), encoding="utf-8") as f:
        paras = [p.strip() for p in re.split(r"\n\s*\n", f.read().strip())
                 if p.strip()]
    if len(paras) != 3:
        raise ValueError("intro.md must hold 3 paragraphs: %s" % book_dir)
    reviewed = (yml.get("review_status") or "").strip().lower() \
        == "independently reviewed"
    status = ("Draft translation, prepared with AI assistance and "
              "independently reviewed."
              if reviewed else
              "Draft translation, prepared with AI assistance and not "
              "yet independently reviewed. "
              "Verify against the original before citing.")
    edition = (yml.get("edition") or "").strip()
    copyright_lines = [LICENSE_LINE, status]
    if edition:
        copyright_lines.append("Translated from %s." % edition)
    return {"title": yml.get("title", ""),
            "author": yml.get("author", ""),
            "edition": edition,
            "intro": paras,
            "copyright_lines": copyright_lines,
            "reviewed": reviewed}


def add_docx_frontmatter(doc, book_dir: str) -> dict:
    """Append Title/Author/small-print/Introduction to a fresh Document.

    Returns the frontmatter dict (builders reuse title/author for
    setup_document so covers always match book.yml).
    """
    from docx.shared import Pt

    fm = load_frontmatter(book_dir)
    doc.add_paragraph(fm["title"], style="Title")
    doc.add_paragraph(fm["author"], style="Subtitle")
    for line in fm["copyright_lines"]:
        para = doc.add_paragraph(style="Normal")
        run = para.add_run(line)
        run.font.size = Pt(9)
    doc.add_paragraph("Introduction", style="Heading 1")
    for para_text in fm["intro"]:
        doc.add_paragraph(para_text, style="Normal")
    return fm


def render_intro_html(book_dir: str) -> str:
    """Intro block for the website work page (same words as Logos)."""
    fm = load_frontmatter(book_dir)
    parts = ['<section class="work-intro">']
    for para_text in fm["intro"]:
        parts.append("<p>%s</p>" % html.escape(para_text))
    parts.append('<p class="translation-note">%s</p>'
                 % html.escape(" ".join(fm["copyright_lines"])))
    parts.append("</section>")
    return "\n".join(parts)
