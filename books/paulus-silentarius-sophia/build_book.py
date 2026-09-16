"""Build Paulus Silentarius: Descriptio Sanctae Sophiae Logos Personal Book DOCX."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.bible_links import BibleLinker, REF, _expand_comma_verses
from pipeline.docx_helpers import (
    BookmarkStore,
    add_heading_with_headword,
    assert_internal_links,
    setup_document,
)

BOOK_DIR = Path(__file__).resolve().parent
OUT_DOCX = BOOK_DIR / "paulus-silentarius-sophia English.docx"
RECEIPT = BOOK_DIR / "build_receipt.json"

CODEX_FILES = [
    "sophia_part1_english.json",
    "sophia_part2_english.json",
    "sophia_part3_english.json",
]

FRONT_MATTER = [
    "New English rendering for private study, prepared with AI assistance from locked Greek (PG 86b / Friedländer 1912). No modern copyrighted translation has been copied. Lethaby & Swainson 1894 (Hakluyt Society) used as PD English reference only.",
    "Scope: Paul the Silentiary's Ekphrasis of Hagia Sophia (1046 hexameter verses), recited at the rededication of Hagia Sophia, 24 December 563 AD. Three parts: (1) The Dome and Nave, (2) The Exedras and Piers, (3) The Ambo and Conclusion.",
    "Bible quotations and clear allusions are linked inline in the reading text. Possible connections stay as short captions. Translator notes use numbered Headword marks — Logos Personal Books do not compile Word footnotes.",
    "Pass A ≠ Pass B. First English from Greek for this ekphrasis. True OET.",
]

# Logos-visible superscripts for TN headword links (not Word footnotes).
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_STOP = {
    "about", "after", "against", "almost", "already", "among", "because", "before",
    "being", "between", "chapter", "clear", "could", "echo", "echoes", "every",
    "first", "from", "further", "here", "into", "same", "saying", "shall", "should",
    "their", "there", "these", "those", "through", "under", "where", "which", "while",
    "with", "would", "paul", "silentiary", "hagia", "sophia", "greek", "latin",
    "also", "than", "then", "that", "this", "they", "them", "have", "been", "were",
    "when", "what", "your", "unto",
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
    for m in REF.finditer(reference):
        book = "Psalm" if m["book"] == "Psalms" else m["book"]
        for loc in _expand_comma_verses(book, m["loc"].replace("–", "-")):
            needle = f"{book} {loc}"
            if needle in text:
                return True
            if re.search(rf"\b{re.escape(book)}\s+{re.escape(loc.split(':')[0])}\b", text):
                return True
    return False


def _reason_words(reason: str) -> list[str]:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-z']{5,}", reason)
        if w.lower() not in _STOP
    ]
    for q in re.findall(r"'([^']{6,80})'|\"([^\"]{6,80})\"", reason):
        snippet = (q[0] or q[1]).lower()
        words.extend(w for w in re.findall(r"[A-Za-z']{5,}", snippet) if w not in _STOP)
    return words


def _insert_cite_before_punct(text: str, end: int, cite: str) -> str:
    return text[:end] + cite + text[end:]


def _word_hit(word: str, haystack: str) -> bool:
    if word in haystack:
        return True
    if len(word) >= 6 and word[:6] in haystack:
        return True
    return False


def _inject_cite_in_paragraph(paragraph: str, reference: str, reason: str) -> str:
    cite = f" ({reference})"
    if f"({reference})" in paragraph:
        return paragraph
    words = _reason_words(reason)
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

    core = re.sub(r"[.;!?]+$", "", best_clause.strip())
    core = re.sub(r"\s+", " ", core)
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
        title="Paulus Silentarius: Descriptio Sanctae Sophiae (New English)",
        author="Paulus Silentarius",
        subject="New English rendering for private Logos study",
        keywords="Paulus Silentarius, Hagia Sophia, Ekphrasis, 6th century",
    )
    doc.add_paragraph("Paulus Silentarius: Descriptio Sanctae Sophiae", style="Title")
    doc.add_paragraph("A new English rendering for private study", style="Subtitle")
    for para in FRONT_MATTER:
        doc.add_paragraph(para)

    linker = BibleLinker()
    bookmarks = BookmarkStore()
    tn_records: list[dict] = []
    records: list[dict] = []

    work_heading_added = False
    for fname in CODEX_FILES:
        path = BOOK_DIR / "translations" / fname
        if not path.exists():
            continue
        entries = json.loads(path.read_text())
        if not entries:
            continue
        if not work_heading_added:
            add_heading_with_headword(doc, bookmarks, "Descriptio Sanctae Sophiae", 1, "sophia-work")
            doc.add_paragraph("Paul the Silentiary, Ekphrasis of Hagia Sophia (563 AD). Greek locked from PG 86b / Friedländer 1912.", style="Caption")
            work_heading_added = True

        for entry in entries:
            part = entry.get("part")
            section = entry.get("section")
            label = section_label(f"Part {part}", section, entry.get("title"))
            key = f"sophia-p{part}-{section}"
            add_heading_with_headword(doc, bookmarks, label, 2, key)

            enriched, possible = inject_refs_into_paragraphs(
                list(entry.get("english") or []),
                entry.get("added_allusions") or [],
            )
            n_paras = 0
            for para in enriched:
                linked = linker.bible_text(para, key=key, label=label)
                doc.add_paragraph(linked)
                n_paras += 1

            notes = [n.strip() for n in (entry.get("translator_notes") or []) if (n or "").strip()]
            if notes and n_paras:
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
            "wording choices, and rough passages — not Paul's text."
        )
        for rec in tn_records:
            hw = rec["headword"]
            add_heading_with_headword(doc, bookmarks, hw, 3, f"tn_{rec['n']}")
            doc.add_paragraph(rec["note"])
            doc.add_paragraph(rec["citation"], style="Caption")

    assert_internal_links(doc, bookmarks.ids)
    doc.save(OUT_DOCX)

    if not records:
        raise SystemExit("no English JSON yet — translate first")

    receipt = {
        "title": "Paulus Silentarius: Descriptio Sanctae Sophiae (New English)",
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