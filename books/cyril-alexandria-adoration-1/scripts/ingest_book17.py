#!/usr/bin/env python3
"""Ingest PG 68 Book 17 Greek into adoration17_source.json from the locked PDF text."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
RAW = BOOK / "sources" / "pg68_de_adoratione_pdftotext.txt"
CLEAN = BOOK / "sources" / "adoration_book17_greek_clean.txt"
OUT = BOOK / "translations" / "adoration17_source.json"

SPEAKER_RE = re.compile(r"\{([^}]+)\}")
COL_RE = re.compile(r"68\.\d+")
FOOTER_RE = re.compile(
    r"Ερευνητικό έργο:.*?προέλευσής του\.|"
    r"Ερευνητικ[oό] έργο:.*?προέλευσής του\.|"
    r"www\.aegean\.gr/culturaltec/chmlab\.|"
    r"Χρηματοδότηση:.*?(?:\n|$)|"
    r"Χρηµατοδότηση:.*?(?:\n|$)|"
    r"Πανεπιστήμιο Αιγαίου.*?(?:\n|$)|"
    r"Πανεπιστήµιο Αιγαίου.*?(?:\n|$)|"
    r"Εργαστήριο.*?(?:\n|$)|"
    r"Εργαστήριο.*?(?:\n|$)|"
    r"Digital Patrology.*?(?:\n|$)|"
    r"Interreg.*?(?:\n|$)|"
    r"© 2006\.",
    re.S,
)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def collapse_ws(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[\t\n]+", " ", s)
    s = re.sub(r" +", " ", s)
    return s.strip()


def strip_footers(text: str) -> str:
    t = FOOTER_RE.sub(" ", text)
    t = re.sub(r"\n\s*\d+\s*\n", "\n", t)
    t = t.replace("\x0c", "\n")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = t.replace("Ω", "Ω").replace("∆", "Δ").replace("µ", "μ")
    return t


def slice_book17(raw: str) -> str:
    raw = nfc(raw)
    m = re.search(r"ΛΟΓΟΣ ΕΠΤΑΚΑΙ[∆Δ]ΕΚΑΤΟΣ", raw)
    if not m:
        raise SystemExit("Book 17 start not found")
    start = m.start()
    head = raw.rfind("ΠΕΡΙ ΤΗΣ ΕΝ ΠΝΕΥΜΑΤΙ", 0, start)
    if head >= 0 and start - head < 300:
        start = head
    # Last book in PG 68 De adoratione — take through EOF; strip_footers removes page footers
    return raw[start:]


def split_speakers(chunk: str) -> list[str]:
    parts: list[str] = []
    matches = list(SPEAKER_RE.finditer(chunk))
    if not matches:
        text = collapse_ws(chunk)
        return [text] if text else []
    if matches[0].start() > 0:
        pre = collapse_ws(chunk[: matches[0].start()])
        if pre:
            parts.append(pre)
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(chunk)
        body = collapse_ws(chunk[m.end() : end])
        label = "{" + m.group(1).strip() + "}"
        para = f"{label} {body}".strip()
        if para:
            parts.append(para)
    return [re.sub(r" +", " ", p).strip() for p in parts if p.strip()]


def apply_hyphen_joins(text: str, notes: list[str]) -> str:
    t = re.sub(r"([Α-Ωα-ωἈ-Ὧἀ-ὧά-ώΆ-Ώ]+)[\-‐‑]\s*", r"\1", text)

    def join_split(m: re.Match) -> str:
        a, b = m.group(1), m.group(2)
        notes.append(f"joined column-split {a}+{b}")
        return a + b

    t2 = re.sub(
        r"([Α-Ωα-ωἈ-Ὧἀ-ὧά-ώΆ-Ώ]{2,})\s+68\.\d+\s+([α-ωἀ-ὧά-ώ]{2,})",
        join_split,
        t,
    )
    if t2 != t:
        t = t2
    if "Ω" in t or "∆" in t:
        t = t.replace("Ω", "Ω").replace("∆", "Δ")
        notes.append("Ω/Δ for lookalike Ω/∆ glyphs")
    return t


def parse(clean: str) -> list[dict]:
    cols = [(m.start(), m.end(), m.group()) for m in COL_RE.finditer(clean)]
    # Book 17 opens ~PG 68.1009 (first inline marker often soon after)
    spans = [(0, cols[0][0] if cols else len(clean), "68.1061")]
    for i, (start, end, col) in enumerate(cols):
        nxt = cols[i + 1][0] if i + 1 < len(cols) else len(clean)
        spans.append((end, nxt, col))
    records = []
    for a, b, col in spans:
        notes: list[str] = []
        piece = apply_hyphen_joins(clean[a:b], notes).strip()
        paras = [p for p in split_speakers(piece) if p]
        if not paras:
            continue
        if len(paras) == 1 and re.fullmatch(r"\d+", paras[0]):
            continue
        nchars = sum(len(p) for p in paras)
        if nchars < 20:
            continue
        records.append(
            {
                "section": len(records) + 1,
                "pg_column": col,
                "head": f"PG {col}",
                "greek": paras,
                "ocr_normalizations": notes,
            }
        )
    return records


def main() -> None:
    raw = RAW.read_text(encoding="utf-8", errors="replace")
    sliced = slice_book17(raw)
    clean = strip_footers(sliced)
    clean = re.sub(
        r"(?m)^(Ερευνητικό|Εργαστήριο|Χρηματοδότηση|Πανεπιστήμιο|Επιτρέπεται|Digital|Interreg|www\.).*$\n?",
        "",
        clean,
    )
    CLEAN.write_text(clean, encoding="utf-8")
    recs = parse(nfc(clean))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(recs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {CLEAN} chars={len(clean)}")
    print(f"wrote {OUT} sections={len(recs)}")
    for r in recs:
        nchars = sum(len(p) for p in r["greek"])
        print(
            f"  {r['section']:02d} {r['pg_column']} paras={len(r['greek']):2d} "
            f"chars={nchars:5d} notes={len(r['ocr_normalizations'])}"
        )


if __name__ == "__main__":
    main()
