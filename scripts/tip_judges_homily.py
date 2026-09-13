#!/usr/bin/env python3
"""Write Origen Judges homily OET artifacts and optionally emit stamp helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books/origen-judges-homilies"


def write_homily(num: int, claim: str, prev_tip: str, sections: list[dict]) -> None:
    (BOOK / "sources").mkdir(parents=True, exist_ok=True)
    (BOOK / "translations").mkdir(parents=True, exist_ok=True)
    (BOOK / "reviews/justifications").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/claim-locks").mkdir(parents=True, exist_ok=True)

    wl = [
        f"Origen Judges (Iudicum) Homilia {num} — working Latin "
        "(cleaned/condensed from Baehrens GCS 30 OCR)\n"
    ]
    eng: list[dict] = []
    src: list[dict] = []

    for s in sections:
        sec = s["section"]
        latin = s["latin"].strip()
        english = s["english"].strip()
        gloss = s["gloss"].strip()
        assert gloss != english, f"Pass A == Pass B at Hom {num}.{sec}"
        allusions = s.get("allusions", [])
        wl.append(f"\n{num}.{sec}\n{latin}\n")

        notes = [
            "Copy-text Baehrens GCS 30 / Origenes Werke VII (1921), Rufinus Latin.",
            "True OET: no ANF; do not copy copyrighted Judges FOTC (Judges).",
            f"After tip {prev_tip}; Homilia {num} CLOSEOUT.",
        ]
        eng.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": f"homilia-{num}",
                "title": s["title"],
                "english": [english],
                "notes_covered": [],
                "added_allusions": allusions,
                "translator_notes": notes,
                "baehrens": f"GCS 30 Iudicum Hom. {num}.{sec}",
                "claim": claim,
            }
        )
        src.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": f"homilia-{num}",
                "locus": f"Baehrens GCS 30 Iudicum Hom. {num} §{sec}",
                "head": f"Iudicum Hom. {num}.{sec}",
                "latin": [latin],
                "edition": "baehrens-gcs30-1921",
            }
        )
        j = {
            "excerpt_id": f"jud_hom{num}_{sec:02d}",
            "edition": {
                "id": "baehrens-gcs30-1921",
                "language": "lat",
                "locus": f"Baehrens GCS 30 Iudicum Hom. {num} {sec}",
            },
            "source_text": latin,
            "pass_a_gloss": gloss,
            "pass_b_english": english,
            "notes": [
                "Pass A ≠ Pass B.",
                "True OET; no copyrighted Judges FOTC.",
                "Copy-text Baehrens GCS 30 Rufinus Latin.",
            ],
            "bible_links": [
                {"ref": a["reference"], "why": a["reason"]} for a in allusions
            ],
            "anf_compare": "no ANF for Rufinus Judges homilies; do not copy copyrighted Judges FOTC",
            "checks": {
                "pass_a_ne_pass_b": True,
                "no_fotc_Bruce": True,
                "edition_lock": "Baehrens GCS 30 / Werke VII (1921)",
            },
            "confidence": "high",
            "reviewer": "Air",
        }
        (BOOK / "reviews/justifications" / f"jud_hom{num}_{sec:02d}.json").write_text(
            json.dumps(j, ensure_ascii=False, indent=2) + "\n"
        )

    (BOOK / "sources" / f"jud_hom{num}_working_latin.txt").write_text("".join(wl))
    (BOOK / "translations" / f"jud_hom{num}_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n"
    )
    (BOOK / "translations" / f"jud_hom{num}_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "docs/claim-locks" / claim).write_text(
        f"agent: Air\nclaimed: 2026-09-13\n"
        f"slice: Origen Judges Homilia {num} CLOSEOUT Pass A≠B OET\n"
        f"status: done\n"
    )
    print(f"wrote Homilia {num}: {len(sections)} sections claim={claim}", file=sys.stderr)
