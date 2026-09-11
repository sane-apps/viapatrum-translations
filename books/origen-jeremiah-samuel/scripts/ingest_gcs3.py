#!/usr/bin/env python3
"""Ingest First1KGreek TEI of GCS Orig. III (Klostermann 1901).

Source XML is a transcription of the same 1901 edition locked in
sources/origeneswerke03orig.pdf. Apparatus <note> is kept out of the
reading Greek.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

BOOK = Path(__file__).resolve().parents[1]
SRC = BOOK / "sources" / "first1k"
TRANS = BOOK / "translations"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

FILES = {
    "jer1_11": SRC / "tlg2042.tlg009.opp-grc1.xml",
    "jer12_20": SRC / "tlg2042.tlg021.opp-grc1.xml",
    "samuel": SRC / "tlg2042.tlg013.opp-grc1.xml",
    "lamentations": SRC / "tlg2042.tlg011.opp-grc1.xml",
}

QUOTE_FIX = str.maketrans({
    "»": "«",
    "«": "«",
    "‹": "'",
    "›": "'",
})


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def local_tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def element_text(el: ET.Element) -> str:
    """Visible Greek; skip footnotes/apparatus notes."""
    if local_tag(el) in {"note", "bibl", "ref"}:
        return ""
    parts: list[str] = [el.text or ""]
    for child in list(el):
        if local_tag(child) in {"note", "bibl"}:
            parts.append(child.tail or "")
            continue
        parts.append(element_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def clean_greek(raw: str, notes: list[str]) -> str:
    t = nfc(raw)
    t = t.replace("\xa0", " ")
    t = t.replace("&gt;", "").replace("&lt;", "")
    t = t.translate(QUOTE_FIX)
    # leftover encoding junk from diplomatic quote marks
    t = t.replace(">.", ".").replace("«.", ".")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s+\n", "\n", t)
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r" +", " ", t).strip()
    # common DDD encoding slips seen in Hom. 1.1
    fixes = [
        ("λέrει", "λέγει"),
        ("καταδίδκης", "καταδίκης"),
        ("καταδικάσθησαν κάσθησαν", "καταδικάσθησαν"),
        ("προόιαμαρτύρασθαι", "προδιαμαρτύρασθαι"),
        ("ὑποπίπτοντα", "ὑποπίπτοντος"),
    ]
    for a, b in fixes:
        if a in t:
            t = t.replace(a, b)
            notes.append(f"{b} for TEI '{a}'")
    t = t.replace("««", "«").replace("»»", "»")
    return t


def paragraphs(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    # GCS sections are usually one running block; split on strong stops
    # only when the block is very long, keep as 1–3 readable paras.
    if len(text) < 900:
        return [text]
    chunks = re.split(r"(?<=[·.])\s+(?=[Α-ΩἈ-ὯA-Z])", text)
    out: list[str] = []
    buf = ""
    for ch in chunks:
        if not buf:
            buf = ch
        elif len(buf) + len(ch) < 700:
            buf = buf + " " + ch
        else:
            out.append(buf.strip())
            buf = ch
    if buf.strip():
        out.append(buf.strip())
    return out or [text]


def ingest_homilies() -> list[dict]:
    records: list[dict] = []
    for key in ("jer1_11", "jer12_20"):
        root = ET.parse(FILES[key]).getroot()
        for hom in root.findall(".//tei:div[@subtype='homilia']", NS):
            hn = int(hom.get("n") or "0")
            for sec in hom.findall("./tei:div[@subtype='section']", NS):
                sn = sec.get("n") or "?"
                notes: list[str] = []
                greek = clean_greek(element_text(sec), notes)
                records.append(
                    {
                        "section": f"{hn}.{sn}",
                        "homily": hn,
                        "klostermann": f"GCS Orig. III Hom. {hn} §{sn}",
                        "head": f"Homily {hn}.{sn}",
                        "greek": paragraphs(greek),
                        "ocr_normalizations": notes,
                        "source_xml": FILES[key].name,
                    }
                )
    records.sort(key=lambda r: (int(str(r["homily"])), float(str(r["section"]).split(".")[-1] or 0)))
    return records


def ingest_samuel() -> list[dict]:
    root = ET.parse(FILES["samuel"]).getroot()
    records: list[dict] = []
    for sec in root.findall(".//tei:div[@subtype='section']", NS):
        sn = sec.get("n") or "?"
        notes: list[str] = []
        greek = clean_greek(element_text(sec), notes)
        records.append(
            {
                "section": str(sn),
                "homily": "1sam28",
                "klostermann": f"GCS Orig. III Hom. in 1 Reg. 28 §{sn}",
                "head": f"Homily on 1 Samuel 28.{sn}",
                "greek": paragraphs(greek),
                "ocr_normalizations": notes,
                "source_xml": FILES["samuel"].name,
            }
        )
    records.sort(key=lambda r: int(r["section"]) if str(r["section"]).isdigit() else 0)
    return records


def ingest_lamentations() -> list[dict]:
    root = ET.parse(FILES["lamentations"]).getroot()
    records: list[dict] = []
    for frag in root.findall(".//tei:div[@subtype='fragment']", NS):
        n = frag.get("n") or "?"
        notes: list[str] = []
        greek = clean_greek(element_text(frag), notes)
        if not greek:
            continue
        records.append(
            {
                "section": str(n),
                "homily": "lamentations",
                "klostermann": f"GCS Orig. III Lam. fr. {n}",
                "head": f"Lamentations fragment {n}",
                "greek": paragraphs(greek),
                "ocr_normalizations": notes,
                "source_xml": FILES["lamentations"].name,
            }
        )
    return records


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    jer = ingest_homilies()
    sam = ingest_samuel()
    lam = ingest_lamentations()
    write_json(TRANS / "jeremiah_source.json", jer)
    write_json(TRANS / "samuel_source.json", sam)
    write_json(TRANS / "lamentations_source.json", lam)

    files = {}
    for p in [
        BOOK / "sources" / "origeneswerke03orig.pdf",
        BOOK / "sources" / "origeneswerke03orig_djvu.txt",
        *FILES.values(),
    ]:
        if p.exists():
            files[str(p.relative_to(BOOK / "sources"))] = {
                "sha256": sha256(p),
                "bytes": p.stat().st_size,
            }

    manifest = {
        "edition_lock": {
            "jeremiah_homilies": {
                "edition": "Erich Klostermann (ed.), Origenes Werke Bd 3, GCS 6 (Leipzig: Hinrichs, 1901)",
                "language": "grc",
                "locus_scheme": "Homily.section as in Klostermann",
                "url": "https://archive.org/details/origeneswerke03orig",
                "working_file": "first1k/tlg2042.tlg009.opp-grc1.xml + tlg2042.tlg021.opp-grc1.xml",
                "notes": "First1KGreek TEI is a transcription of the 1901 GCS. PDF + djvu.txt retained as witnesses. Do not copy FOTC 97 (Smith).",
            },
            "samuel_28": {
                "edition": "same GCS Orig. III, Homily on 1 Kingdoms 28 (Witch of Endor)",
                "language": "grc",
                "working_file": "first1k/tlg2042.tlg013.opp-grc1.xml",
            },
            "lamentations": {
                "edition": "same GCS Orig. III, catena fragments on Lamentations",
                "language": "grc",
                "working_file": "first1k/tlg2042.tlg011.opp-grc1.xml",
            },
        },
        "files": files,
    }
    write_json(BOOK / "sources" / "manifest.json", manifest)

    def brief(rows, label):
        chars = sum(len(" ".join(r["greek"])) for r in rows)
        print(f"{label}: {len(rows)} sections, {chars} greek chars")

    brief(jer, "Jeremiah homilies")
    brief(sam, "1 Samuel 28")
    brief(lam, "Lamentations fragments")
    by_h = {}
    for r in jer:
        by_h.setdefault(r["homily"], 0)
        by_h[r["homily"]] += 1
    print("per homily:", by_h)


if __name__ == "__main__":
    main()
