#!/usr/bin/env python3
"""Slice Pusey 1877 De recta fide (CPG 5219–5220) into *_source.json.

Source lock only — no English. Reads the locked Internet Archive DjVu text.
Skips ad Theodosium. Stops before Quod unus sit Christus.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
RAW = BOOK / "sources" / "pusey1877_de_recta_fide_djvu.txt"
OUT_DIR = BOOK / "translations"

ARCADIA_START = re.compile(
    r"^DE RECTA FIDE AD ARCADIAM MARINAMQUE\.?\s+(\d+)\s*$"
)
# OCR variants: F. / FIDE / ΕΞ / RECTE / LET
PULCHERIA_HEAD = re.compile(
    r"^DE RECT[AE]\s+F\.?\s*AD PULCHERIAM(?:\s+ET|\s+LET)?\s+EUDOCIAM\.?"
    r"(?:\s+[\d.,]+)?\s+(\d+)\s*$",
    re.I,
)
QUOD_UNUS = re.compile(r"^QUOD UNUS", re.I)
PAGE_FOOTER = re.compile(
    r"^\d+\s+B\.\s*CYRILLI|^B\.\s*CYRILLI ARCHIEPISC|^B\.\s*CYR\.\s*ALEX",
    re.I,
)
APPARATUS_LINE = re.compile(
    r"("
    r"^\s*\d+\.\s|"  # numbered app notes
    r"Cod\.|Comm\.|Edd\.|Aub\.|om\.|add\.|sic\)|emend|"
    r"exhibet|signavi|fol\.|sec\.|mg\.|"
    r"Πετ\.|Pet\.|"
    r"^\s*[IVXLC]+\.\s*$"
    r")",
    re.I,
)
GREEK_CHAR = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def greek_ratio(s: str) -> float:
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    g = sum(1 for c in letters if GREEK_CHAR.match(c))
    return g / len(letters)


def clean_para(lines: list[str]) -> str:
    text = " ".join(l.strip() for l in lines if l.strip())
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" ;", ";").replace(" ,", ",")
    return nfc(text.strip())


def is_keep_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if ARCADIA_START.match(s) or PULCHERIA_HEAD.match(s) or QUOD_UNUS.match(s):
        return False
    if PAGE_FOOTER.match(s):
        return False
    if re.match(r"^\d+\s*$", s):
        return False
    if APPARATUS_LINE.search(s) and greek_ratio(s) < 0.45:
        return False
    # Syriac / Latin apparatus blocks
    if greek_ratio(s) < 0.25 and not re.search(r"[Α-Ωα-ω]", s):
        return False
    return greek_ratio(s) >= 0.35 or (
        greek_ratio(s) >= 0.2 and len(GREEK_CHAR.findall(s)) >= 12
    )


def flush_page(
    records: list[dict],
    page: int | None,
    buf: list[str],
    treatise: str,
) -> list[str]:
    if page is None:
        return []
    kept: list[str] = []
    para: list[str] = []
    for line in buf:
        if not line.strip():
            if para:
                p = clean_para(para)
                if p and greek_ratio(p) >= 0.4:
                    kept.append(p)
                para = []
            continue
        if is_keep_line(line):
            para.append(line)
        else:
            if para:
                p = clean_para(para)
                if p and greek_ratio(p) >= 0.4:
                    kept.append(p)
                para = []
    if para:
        p = clean_para(para)
        if p and greek_ratio(p) >= 0.4:
            kept.append(p)
    if kept:
        records.append(
            {
                "section": len(records) + 1,
                "pusey_page": page,
                "head": f"Pusey 1877 p.{page}",
                "treatise": treatise,
                "greek": kept,
            }
        )
    return []


def slice_treatise(
    lines: list[str],
    start_idx: int,
    end_idx: int,
    treatise: str,
    head_re: re.Pattern[str],
) -> list[dict]:
    records: list[dict] = []
    page: int | None = None
    buf: list[str] = []
    for i in range(start_idx, end_idx):
        line = lines[i]
        m = head_re.match(line.strip())
        if m:
            buf = flush_page(records, page, buf, treatise)
            try:
                page = int(m.group(1))
            except ValueError:
                page = page or 0
            continue
        # also catch plain page footers that carry print page numbers
        fm = re.match(
            r"^(\d{3})\s+B\.\s*CYRILLI",
            line.strip(),
            re.I,
        )
        if fm and page is not None:
            # verso page start — flush prior and advance if sequential
            nxt = int(fm.group(1))
            if nxt != page:
                buf = flush_page(records, page, buf, treatise)
                page = nxt
            continue
        buf.append(line)
    flush_page(records, page, buf, treatise)
    return records


def main() -> None:
    raw = nfc(RAW.read_text(encoding="utf-8", errors="replace"))
    lines = raw.splitlines()

    arcadia_start = next(
        i for i, l in enumerate(lines) if ARCADIA_START.match(l.strip())
    )
    pulcheria_start = next(
        i for i, l in enumerate(lines) if PULCHERIA_HEAD.match(l.strip())
    )
    quod_start = next(
        i
        for i, l in enumerate(lines)
        if i > pulcheria_start and QUOD_UNUS.match(l.strip())
    )

    arcadia = slice_treatise(
        lines,
        arcadia_start,
        pulcheria_start,
        "cpg5219_ad_arcadiam_marinamque",
        ARCADIA_START,
    )
    pulcheria = slice_treatise(
        lines,
        pulcheria_start,
        quod_start,
        "cpg5220_ad_pulcheriam_eudociamque",
        PULCHERIA_HEAD,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "edition": "Pusey 1877 (IA SPNCyrilli7)",
        "source_file": "sources/pusey1877_de_recta_fide_djvu.txt",
        "pdf": "sources/pusey1877_de_recta_fide.pdf",
        "note": "OCR source lock from DjVu text; apparatus stripped by heuristic; no English.",
        "skipped": "CPG 5218 ad Theodosium (opens volume; King FC 129 has modern English)",
    }

    arcadia_path = OUT_DIR / "ad_arcadiam_marinamque_source.json"
    pulcheria_path = OUT_DIR / "ad_pulcheriam_eudociamque_source.json"
    arcadia_path.write_text(
        json.dumps({"meta": {**meta, "cpg": 5219}, "sections": arcadia}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    pulcheria_path.write_text(
        json.dumps(
            {"meta": {**meta, "cpg": 5220}, "sections": pulcheria},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    def stats(recs: list[dict]) -> str:
        pages = [r["pusey_page"] for r in recs]
        paras = sum(len(r["greek"]) for r in recs)
        chars = sum(sum(len(g) for g in r["greek"]) for r in recs)
        return f"sections={len(recs)} pages={min(pages) if pages else '-'}–{max(pages) if pages else '-'} paras={paras} chars={chars}"

    print(f"wrote {arcadia_path.name}: {stats(arcadia)}")
    print(f"wrote {pulcheria_path.name}: {stats(pulcheria)}")
    if len(arcadia) < 20 or len(pulcheria) < 20:
        raise SystemExit("slice too thin — check header regex / bounds")


if __name__ == "__main__":
    main()
