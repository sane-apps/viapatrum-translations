"""Build the Origen Heraclides + On Pascha Logos Personal Book DOCX."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.bible_links import BibleLinker, REF, _expand_comma_verses, link_heading_verses
from pipeline.docx_helpers import (
    BookmarkStore,
    add_heading_with_headword,
    assert_internal_links,
    setup_document,
)

BOOK_DIR = Path(__file__).resolve().parent
OUT_DOCX = BOOK_DIR / "origen-heraclides-pascha.docx"
RECEIPT = BOOK_DIR / "build_receipt.json"

WORKS = [
    (
        "heraclides_english.json",
        "Dialogue with Heraclides",
        "her",
        "Dialogus cum Heraclide, Scherer tradition (Toura papyrus) via DCO Greek.",
    ),
    (
        "pascha_english.json",
        "On Pascha",
        "pascha",
        "Peri Pascha, Witte 1993 from the Toura papyrus (Guéraud–Nautin 1979 critical base).",
    ),
]

FRONT_MATTER = [
    "New English rendering for private study, prepared with AI assistance from the Greek text. No modern copyrighted translation has been copied. A modern version may have been consulted only as a sense or style check.",
    "Scope: Dialogue with Heraclides and On Pascha — Toura-papyrus recoveries that lack a public-domain English version. Prayer and Martyrdom are in a separate book. Contra Celsum and De Principiis are out of scope here.",
    "Bible quotations and clear allusions are linked inline in the reading text. Possible or lacuna-tied connections stay as short captions. Translator notes use numbered Headword marks (hover/click opens the matching note) — Logos Personal Books do not compile Word footnotes.",
    "Damaged papyrus is marked [lacuna]. Editorial fillings are not treated as Origen’s text.",
]

# Logos-visible superscripts for TN headword links (not Word footnotes).
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_STOP = {
    "about", "after", "against", "almost", "already", "among", "because", "before",
    "being", "between", "chapter", "clear", "could", "echo", "echoes", "every",
    "first", "from", "further", "here", "into", "same", "saying", "shall", "should",
    "their", "there", "these", "those", "through", "under", "where", "which", "while",
    "with", "would", "origen", "greek", "latin", "lxx", "also", "than", "then", "that",
    "this", "they", "them", "have", "been", "were", "when", "what", "your", "unto",
}


def tn_mark(n: int) -> str:
    return "".join(_SUP[int(ch)] for ch in str(n))


def section_label(work_title: str, section, title: str | None = None) -> str:
    if section == "proem":
        base = f"{work_title}, proem"
    else:
        base = f"{work_title} {section}"
    titled = (title or "").strip()
    if titled:
        return f"{base} — {titled}"
    return base


def _allusion_ref(raw) -> tuple[str, str, str]:
    if isinstance(raw, dict):
        return (
            (raw.get("reference") or "").strip(),
            (raw.get("certainty") or "clear").strip(),
            (raw.get("reason") or "").strip(),
        )
    return (str(raw).strip(), "clear", "")


def _ref_already_in(text: str, reference: str) -> bool:
    """True if this allusion's book+loc already appears as a detectable Bible ref."""
    for m in REF.finditer(reference):
        book = "Psalm" if m["book"] == "Psalms" else m["book"]
        for loc in _expand_comma_verses(book, m["loc"].replace("–", "-")):
            needle = f"{book} {loc}"
            if needle in text:
                return True
            # loose: book + chapter present as linked-style prose
            if re.search(rf"\b{re.escape(book)}\s+{re.escape(loc.split(':')[0])}\b", text):
                return True
    return False


def _reason_words(reason: str) -> list[str]:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-z']{5,}", reason)
        if w.lower() not in _STOP
    ]
    # Quoted snippets in the reason are strong anchors into the English.
    for q in re.findall(r"'([^']{6,80})'|\"([^\"]{6,80})\"", reason):
        snippet = (q[0] or q[1]).lower()
        words.extend(w for w in re.findall(r"[A-Za-z']{5,}", snippet) if w not in _STOP)
    return words


def _insert_cite_before_punct(text: str, end: int, cite: str) -> str:
    """Insert cite immediately before punctuation at end (inclusive index of punct)."""
    return text[:end] + cite + text[end:]


def _word_hit(word: str, haystack: str) -> bool:
    if word in haystack:
        return True
    # persecutors ↔ persecute, heavenly ↔ heaven, etc.
    if len(word) >= 6 and word[:6] in haystack:
        return True
    return False


def _inject_cite_in_paragraph(paragraph: str, reference: str, reason: str) -> str:
    """Place (Book ch:v) immediately before the best-matching clause's terminal punct."""
    cite = f" ({reference})"
    if f"({reference})" in paragraph:
        return paragraph
    words = _reason_words(reason)
    # Score on text without prior cites so earlier marks do not steal matches.
    score_base = re.sub(r"\s*\([^)]*\d[^)]*\)", "", paragraph)
    best_clause = None
    best_score = -1.0
    for m in re.finditer(r"[^.;!?]+[.;!]?", score_base):
        s = m.group()
        if len(s.strip()) < 12:
            continue
        sl = s.lower()
        score = float(sum(1 for w in words if _word_hit(w, sl)))
        if "'" in s or "‘" in s or "“" in s:
            score += 0.5
        score += min(len(s), 120) / 2000.0
        if score > best_score:
            best_score = score
            best_clause = s

    if best_clause is None or best_score < 1.0:
        end = len(paragraph)
        while end > 0 and paragraph[end - 1].isspace():
            end -= 1
        if end > 0 and paragraph[end - 1] in ".!?;:":
            return _insert_cite_before_punct(paragraph, end - 1, cite)
        return paragraph + cite

    # Locate the clause's leading text in the live paragraph (cites may already sit
    # after earlier clauses). Use a punct-free core for the search.
    core = re.sub(r"[.;!?]+$", "", best_clause.strip())
    core = re.sub(r"\s+", " ", core)
    # Prefer the last 50 chars of the core — unique enough within a paragraph.
    needle = core[-50:] if len(core) > 50 else core
    pos = paragraph.find(needle)
    if pos < 0:
        pos = paragraph.lower().find(needle.lower())
    if pos < 0:
        end = len(paragraph)
        while end > 0 and paragraph[end - 1].isspace():
            end -= 1
        if end > 0 and paragraph[end - 1] in ".!?;:":
            return _insert_cite_before_punct(paragraph, end - 1, cite)
        return paragraph + cite

    # Walk from end of needle to the clause terminal punct, skipping existing cites.
    end = pos + len(needle)
    while end < len(paragraph):
        ch = paragraph[end]
        if ch in ".!?;:":
            return _insert_cite_before_punct(paragraph, end, cite)
        if ch.isspace():
            end += 1
            continue
        if paragraph.startswith(" (", end):
            close = paragraph.find(")", end)
            if close < 0:
                break
            end = close + 1
            continue
        break
    return _insert_cite_before_punct(paragraph, end, cite)


def inject_refs_into_paragraphs(paragraphs: list[str], allusions: list) -> tuple[list[str], list[dict]]:
    """
    Put clear Bible refs inline beside the matching clause, not as a caption dump.
    Possible/uncertain allusions are returned for short captions.
    """
    original = list(paragraphs)
    paras = list(paragraphs)
    if not paras:
        return paras, []
    leftovers: list[dict] = []

    for raw in allusions or []:
        reference, certainty, reason = _allusion_ref(raw)
        if not reference:
            continue
        if certainty == "possible":
            leftovers.append({"reference": reference, "certainty": certainty, "reason": reason})
            continue
        body = "\n".join(paras)
        if _ref_already_in(body, reference):
            continue

        words = _reason_words(reason)
        best_i, best_score = len(paras) - 1, -1.0
        for i, p in enumerate(original):
            pl = p.lower()
            score = float(sum(1 for w in words if _word_hit(w, pl)))
            if "'" in p or "‘" in p or "“" in p:
                score += 0.5
            if score > best_score:
                best_score, best_i = score, i

        paras[best_i] = _inject_cite_in_paragraph(paras[best_i], reference, reason)

    return paras, leftovers


def main() -> None:
    doc = setup_document(
        title="Origen: Dialogue with Heraclides and On Pascha (New English)",
        author="Origen of Alexandria",
        subject="New English rendering for private Logos study",
        keywords="Origen, Heraclides, Pascha, Toura, ante-nicene",
    )
    doc.add_paragraph("Origen: Dialogue with Heraclides and On Pascha", style="Title")
    doc.add_paragraph("A new English rendering for private study", style="Subtitle")
    for para in FRONT_MATTER:
        doc.add_paragraph(para)

    linker = BibleLinker()
    bookmarks = BookmarkStore()
    tn_records: list[dict] = []
    records: list[dict] = []

    for fname, work_title, key_prefix, edition_line in WORKS:
        path = BOOK_DIR / "translations" / fname
        if not path.exists():
            continue
        entries = json.loads(path.read_text())
        if not entries:
            continue
        add_heading_with_headword(doc, bookmarks, work_title, 1, f"{key_prefix}-work")
        doc.add_paragraph(edition_line, style="Caption")
        for entry in entries:
            section = entry["section"]
            label = section_label(work_title, section, entry.get("title"))
            key = f"{key_prefix}-{section}"
            add_heading_with_headword(
                doc,
                bookmarks,
                link_heading_verses(label, linker, key=key, label=label),
                2,
                key,
                headword_source=label,
            )

            enriched, possible = inject_refs_into_paragraphs(
                list(entry.get("english") or []),
                entry.get("added_allusions") or [],
            )
            n_paras = 0
            last_linked = ""
            for para in enriched:
                linked = linker.bible_text(para, key=key, label=label)
                doc.add_paragraph(linked)
                last_linked = linked
                n_paras += 1

            # Translator notes → Headword TN marks (Logos compiles these; Word footnotes do not).
            notes = [n.strip() for n in (entry.get("translator_notes") or []) if (n or "").strip()]
            if notes and n_paras:
                # Re-write last paragraph with trailing TN marks.
                # python-docx: easiest path — append marks as a new short paragraph after body.
                marks = []
                for note in notes:
                    n = len(tn_records) + 1
                    hw = f"TN {n}"
                    mark = tn_mark(n)
                    marks.append(f"[[{mark} >> Headword:{hw}]]")
                    tn_records.append(
                        {
                            "n": n,
                            "headword": hw,
                            "note": note,
                            "citation": label,
                            "excerpt_id": key,
                        }
                    )
                doc.add_paragraph(" ".join(marks))

            for a in possible:
                reason = a.get("reason") or ""
                line = f"Possible allusion: {a['reference']}"
                if reason:
                    line += f" — {reason}"
                doc.add_paragraph(
                    linker.bible_text(line, key=key, label=label, note=True),
                    style="Caption",
                )

            records.append(
                {"key": key, "label": label, "paragraphs": n_paras, "source": fname}
            )

    if tn_records:
        add_heading_with_headword(doc, bookmarks, "Translator notes", 1, "translation_notes")
        doc.add_paragraph(
            "Numbered marks in the chapters open these notes. They flag lacunae, "
            "wording choices, and rough passages — not Origen's text."
        )
        for rec in tn_records:
            hw = rec["headword"]
            add_heading_with_headword(doc, bookmarks, hw, 3, f"tn_{rec['n']}")
            doc.add_paragraph(rec["note"])
            doc.add_paragraph(rec["citation"], style="Caption")

    assert_internal_links(doc, bookmarks.ids)
    doc.save(OUT_DOCX)

    if not records:
        raise SystemExit("no English JSON yet — translate Heraclides/Pascha first")

    receipt = {
        "title": "Origen: Dialogue with Heraclides and On Pascha (New English)",
        "section_count": len(records),
        "paragraph_count": sum(r["paragraphs"] for r in records),
        "bookmark_count": len(bookmarks.ids),
        "footnote_count": 0,
        "tn_note_count": len(tn_records),
        "bible_links": linker.link_receipts,
        "scripture_index_entries": sum(len(v) for v in linker.index.values()),
        "records": records,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(
        f"wrote {OUT_DOCX.name}: {len(records)} sections, "
        f"{len(linker.link_receipts)} bible links, {len(tn_records)} TN notes"
    )


if __name__ == "__main__":
    main()
