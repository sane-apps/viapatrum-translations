#!/usr/bin/env python3
"""Ingest locked PG 68 Book 1 Greek into adoration1_source.json."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
SRC = BOOK / "sources" / "adoration_book1_greek_clean.txt"
OUT = BOOK / "translations" / "adoration1_source.json"

SPEAKER_RE = re.compile(r"\{([^}]+)\}")
COL_RE = re.compile(r"68\.\d+")
BOOK2_RE = re.compile(r"ΠΕΡΙ ΤΗΣ ΕΝ ΠΝΕΥΜΑΤΙ")

# Mid-word joins at column cuts (first-half + second-half after the marker).
KNOWN_JOINS = {
    ("Δυσαπό", "νιπτον"): "Δυσαπόνιπτον",
    ("Δυσαπό", "νιπτον"): "Δυσαπόνιπτον",
    ("θεσπέ", "σιος"): "θεσπέσιος",
    ("θεσπέ", "σιος"): "θεσπέσιος",
    ("πολεμου", "μένοις"): "πολεμουμένοις",
    ("πολεμου", "μένοις"): "πολεμουμένοις",
    ("ἀναλα", "βόντες"): "ἀναλαβόντες",
    ("ἀναλα", "βόντες"): "ἀναλαβόντες",
    ("ἀνέ", "θορε"): "ἀνέθορε",
    ("ἀνέ", "θορε"): "ἀνέθορε",
    ("φρό", "νημα"): "φρόνημα",
    ("φρό", "νημα"): "φρόνημα",
    ("ἐγκα", "τατρύχουσι"): "ἐγκατατρύχουσι",
    ("ἐγκα", "τατρύχουσι"): "ἐγκατατρύχουσι",
    ("ἐκβεβιασμέ", "νος"): "ἐκβεβιασμένος",
    ("ἐκβεβιασμέ", "νος"): "ἐκβεβιασμένος",
}

HYPHEN_FIXES = [
    ("προσ-κυνεῖτε", "προσκυνεῖτε"),
    ("ἀνεῖ-ναί", "ἀνεῖναι"),
    ("ἀνεῖ-ναί", "ἀνεῖναι"),
    ("Ἐξαπό-στειλον", "Ἐξαπόστειλον"),
    ("Ἐξαπό-στειλον", "Ἐξαπόστειλον"),
    ("Πορευ-σόμεθα", "Πορευσόμεθα"),
    ("Πορευ-σόμεθα", "Πορευσόμεθα"),
    ("Συναγω-γῆς", "Συναγωγῆς"),
]

SPACE_FIXES = [
    ("περιβεβλημ μένη", "περιβεβλημένη"),
    ("περιβεβλημ μένη", "περιβεβλημένη"),
    ("Ἡμεῖςδὲ", "Ἡμεῖς δὲ"),
    ("Ταύτῃτοί", "Ταύτῃ τοι"),
    ("Ταύτῃτοί", "Ταύτῃ τοι"),
    ("Ταύτῃτοι", "Ταύτῃ τοι"),
    ("Καρποὶγὰρ", "Καρποὶ γὰρ"),
    ("ὡδίπη", "ὡδί που"),
    ("ὡδίπη", "ὡδί που"),
    ("διαπήγσθαι", "διαπήγνυσθαι"),
    ("διαπήγσθαι", "διαπήγνυσθαι"),
]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def collapse_ws(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[\t\n]+", " ", s)
    s = re.sub(r" +", " ", s)
    return s.strip()


def apply_fixes(text: str, notes: list[str]) -> str:
    t = text
    for a, b in HYPHEN_FIXES + SPACE_FIXES:
        if a in t:
            t = t.replace(a, b)
            notes.append(f"{b} for scan '{a}'")
    # editorial brackets kept readable
    t2 = t.replace("ταυτ[αισ]ὶ", "ταυταισὶ").replace("Ἐπίδοι[τ]ο", "Ἐπίδοιτο").replace("Ἐπίδοι[τ]ο", "Ἐπίδοιτο")
    t2 = t2.replace("εἶεν [ἂν] οὗτοι", "εἶεν ἂν οὗτοι")
    if t2 != t:
        notes.append("expanded editor restorations in square brackets (ταυταισὶ / Ἐπίδοιτο / ἂν)")
        t = t2
    # capital lookalikes
    if "Ω" in t or "∆" in t:
        t = t.replace("Ω", "Ω").replace("∆", "Δ")
        notes.append("Ω/Δ for lookalike Ω/∆ glyphs")
    return t


def split_speakers(chunk: str) -> list[str]:
    """Keep speaker labels in the Greek paragraphs."""
    parts: list[str] = []
    idx = 0
    matches = list(SPEAKER_RE.finditer(chunk))
    if not matches:
        text = collapse_ws(chunk)
        return [text] if text else []
    if matches[0].start() > 0:
        pre_raw = chunk[: matches[0].start()]
        pre = collapse_ws(pre_raw)
        if pre:
            # Book heading stays its own paragraph; unlabeled opening is Cyril.
            m_open = re.search(r"(ΛΟΓΟΣ\s+ΠΡΩΤΟΣ.*?ἀναδρομῆς\.)\s*(.*)$", pre)
            if m_open:
                parts.append(m_open.group(1).strip())
                if m_open.group(2).strip():
                    parts.append(m_open.group(2).strip())
            else:
                parts.append(pre)
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(chunk)
        body = collapse_ws(chunk[m.end() : end]).replace("\n", " ")
        body = re.sub(r" +", " ", body).strip()
        label = "{" + m.group(1).strip() + "}"
        para = f"{label} {body}".strip()
        if para:
            parts.append(para)
    return [re.sub(r" +", " ", p).strip() for p in parts if p.strip()]


def parse() -> list[dict]:
    raw = nfc(SRC.read_text(encoding="utf-8"))
    raw = BOOK2_RE.split(raw)[0].rstrip()
    cols = [(m.start(), m.end(), m.group()) for m in COL_RE.finditer(raw)]
    # First block is 68.134 (no marker).
    spans = [(0, cols[0][0] if cols else len(raw), "68.134")]
    for i, (start, end, col) in enumerate(cols):
        nxt = cols[i + 1][0] if i + 1 < len(cols) else len(raw)
        spans.append((end, nxt, col))

    records = []
    pending_join: tuple[str, str] | None = None  # (joined, second_half)
    for i, (a, b, col) in enumerate(spans):
        notes: list[str] = []
        piece = raw[a:b]
        if pending_join:
            joined, second = pending_join
            stripped = piece.lstrip()
            if stripped.startswith(second):
                piece = joined + stripped[len(second) :]
            else:
                piece = joined + " " + piece
            notes.append(f"rejoined column-split → {joined}")
            pending_join = None
        chunk = apply_fixes(piece, notes).strip()
        if i + 1 < len(spans):
            nxt_raw = apply_fixes(nfc(raw[spans[i + 1][0] : spans[i + 1][0] + 80]).lstrip(), [])
            m_next = re.match(r"[\u0370-\u03ff\u1f00-\u1fff]+", nxt_raw)
            tail_m = re.search(r"([\u0370-\u03ff\u1f00-\u1fff]+)\s*$", chunk)
            if m_next and tail_m:
                first, second = tail_m.group(1), m_next.group(0)
                joined = KNOWN_JOINS.get((first, second))
                if joined:
                    pending_join = (joined, second)
                    chunk = chunk[: tail_m.start()].rstrip()
        paras = split_speakers(chunk)
        # drop empty
        paras = [p for p in paras if p]
        records.append(
            {
                "section": i + 1,
                "pg_column": col,
                "head": f"PG {col}",
                "greek": paras,
                "ocr_normalizations": notes,
            }
        )
    return records


def main() -> None:
    recs = parse()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(recs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} sections={len(recs)}")
    for r in recs:
        nchars = sum(len(p) for p in r["greek"])
        print(f"  {r['section']:02d} {r['pg_column']} paras={len(r['greek']):2d} chars={nchars:5d} notes={len(r['ocr_normalizations'])}")


if __name__ == "__main__":
    main()
