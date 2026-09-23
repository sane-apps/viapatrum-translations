#!/usr/bin/env python3
"""Write morte_229..235 justifications; check_pass_ab after each."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
JUST = BOOK / "reviews/justifications"
OCR = BOOK / "sources/_ocr_praedestinatione_cap2_scholastici"
CHECK = Path.home() / "SaneApps/clients/translations/pipeline/check_pass_ab.py"
PACKET = "praedestinatione_cap2_scholastici_densify"

SECTIONS = json.loads((OCR / "sections_all.json").read_text(encoding="utf-8"))

def main() -> None:
    JUST.mkdir(parents=True, exist_ok=True)
    for sec in SECTIONS:
        n = sec["section"]
        jx = {
            "section": str(n),
            "title": sec["title"],
            "pass_a_gloss": sec["pass_a"],
            "pass_b_english": [sec["pass_b"]],
            "source_text": sec["latin"],
            "pass_a_ne_b": True,
            "bible_refs": [],
            "notes": (
                f"Densify De praedestinatione Cap. II Scholastici section {n}. "
                f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+DjVu+lock. "
                f"Packet {PACKET}. Honest partial."
            ),
            "lemmas": sec["lemmas"],
            "choices": [
                {
                    "issue": "Copy-text",
                    "choice": (
                        "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng + DjVu) "
                        "with sense normalize; lock: sources/_davenant_praedestinatione_cap2_scholastici_latin_lock.txt."
                    ),
                },
                {
                    "issue": "Scope",
                    "choice": (
                        "Cap. II Scholastici (causes of election error; then Pontificii / Vasquez Arg. 1 + Sol.) "
                        "(after Cap. II Variae Semipelagian close; before Cap. II Arg. 2 praescientia loci)."
                    ),
                },
            ],
        }
        path = JUST / f"morte_{n}.json"
        path.write_text(json.dumps(jx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECK), str(path)],
            capture_output=True,
            text=True,
        )
        out = (r.stdout + r.stderr).strip()
        print(f"check {n}: {out}")
        if r.returncode != 0 or "fail=0" not in out:
            raise SystemExit(f"FAIL section {n}: {out}")
    print("all justifications ok")

if __name__ == "__main__":
    main()
