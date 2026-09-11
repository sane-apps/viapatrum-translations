"""Extract Book 1 Greek witnesses from GCS Koetschau scans (archive.org).

Downloads the two full OCR texts as witnesses, slices the treatise spans,
and writes sources/manifest.json (URLs + SHA256 + edition lock + bounds).

Bounds (verified 2026-09-10 by running-head/index anchors):
- Exhortatio ad martyrium (GCS 2 = Bd 1): from the
  "EIS MAPTYPION" title to just before the Celsus title block
  ("EIHTETPAMMENON KEAZOY" + "PREFACE/PROOIMION"). Edition cites:
  Bd I 3,1 - 47,16.
- De oratione (GCS 3 = Bd 2): from the "UEPIEYXH2" title
  (after Celsus VIII.76 close) to just before "VORBEMERKUNGEN."
  Edition cites: Bd II 297,1 - 403,10.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"

ITEMS = {
    "gcs2_bd1_full_ocr.txt": (
        "https://archive.org/download/origenes-werke.-bd-1-1899/"
        "Origenes%20Werke.%20Bd%201%2C%201899_djvu.txt",
        "Bd 1: Schrift vom Martyrium + Celsus I-IV (GCS 2, Koetschau 1899)",
    ),
    "gcs3_bd2_full_ocr.txt": (
        "https://archive.org/download/origenes-werke.-bd-2-1899/"
        "Origenes%20Werke.%20Bd%202%2C%201899_djvu.txt",
        "Bd 2: Celsus V-VIII + Schrift vom Gebet (GCS 3, Koetschau 1899)",
    ),
}

START_MART = "EIS MAPTYPION"
END_MART = "EIHTETPAMMENON"
START_GEBET = "UEPIEYXH2"
END_GEBET = "VORBEMERKUNGEN."


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name: str, url: str) -> Path:
    path = SOURCES / name
    if not path.exists():
        print(f"download {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "saneapps-translations/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def main() -> int:
    SOURCES.mkdir(parents=True, exist_ok=True)
    manifest = {"edition_lock": {}, "files": {}}

    bd1 = fetch("gcs2_bd1_full_ocr.txt", ITEMS["gcs2_bd1_full_ocr.txt"][0])
    bd2 = fetch("gcs3_bd2_full_ocr.txt", ITEMS["gcs3_bd2_full_ocr.txt"][0])

    t1 = bd1.read_text(encoding="utf-8", errors="replace")
    t2 = bd2.read_text(encoding="utf-8", errors="replace")

    s = t1.index(START_MART)
    e = t1.index(END_MART)
    mart = t1[s:e]
    (SOURCES / "gcs2_martyrium_slice.txt").write_text(mart, encoding="utf-8")

    s2 = t2.index(START_GEBET)
    e2 = t2.index(END_GEBET)
    gebet = t2[s2:e2]
    (SOURCES / "gcs3_gebet_slice.txt").write_text(gebet, encoding="utf-8")

    import json

    manifest = {
        "edition_lock": {
            "martyrium": {
                "edition": "Paul Koetschau (ed.), Origenes Werke Bd 1, GCS 2 (Leipzig: Hinrichs, 1899)",
                "language": "grc",
                "locus_scheme": "Bd I 3,1-47,16; chapters 1-51 (LI) per Koetschau numbering",
                "url": ITEMS["gcs2_bd1_full_ocr.txt"][0],
            },
            "gebet": {
                "edition": "Paul Koetschau (ed.), Origenes Werke Bd 2, GCS 3 (Leipzig: Hinrichs, 1899)",
                "language": "grc",
                "locus_scheme": "Bd II 297,1-403,10; chapters 1-33/34 per Koetschau numbering",
                "url": ITEMS["gcs3_bd2_full_ocr.txt"][0],
            },
        },
        "files": {},
    }
    for p in sorted(SOURCES.glob("*.txt")):
        manifest["files"][p.name] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    (SOURCES / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"martyrium slice: {len(mart)} chars")
    print(f"gebet slice: {len(gebet)} chars")
    print("wrote sources/manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
