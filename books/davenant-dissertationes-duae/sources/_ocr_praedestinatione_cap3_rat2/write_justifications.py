#!/usr/bin/env python3
"""Write morte_278..282 justifications; check_pass_ab after each."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
JUST = BOOK / "reviews/justifications"
OCR = BOOK / "sources/_ocr_praedestinatione_cap3_rat2"
CHECK = Path.home() / "SaneApps/clients/translations/pipeline/check_pass_ab.py"
PACKET = "praedestinatione_cap3_rat2_densify"

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
                f"Densify De praedestinatione Cap. III Rat. 2 section {n}. "
                f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+DjVu+lock. "
                f"Packet {PACKET}. Honest partial."
            ),
            "lemmas": sec["lemmas"],
            "choices": [
                {
                    "issue": "Copy-text",
                    "choice": (
                        "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng + DjVu) "
                        "with sense normalize; lock: sources/_davenant_praedestinatione_cap3_rat2_latin_lock.txt."
                    ),
                },
                {
                    "issue": "Scope",
                    "choice": (
                        "Cap. III adversariorum rationes Rat. 2 (Vasquez physical vs moral media) and Resp. "
                        "(after Cap. III Rat. 1 Rej. close; before Cap. III Rat. 3 king/prize analogy)."
                    ),
                },
            ],
        }
        path = JUST / f"morte_{n}.json"
        path.write_text(json.dumps(jx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        print(f"check {n}: {out}")
        if r.returncode != 0 or "fail=0" not in out:
            raise SystemExit(f"FAIL section {n}: {out}")
    print("all justifications ok")

if __name__ == "__main__":
    main()
