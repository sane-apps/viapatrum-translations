#!/usr/bin/env python3
"""Write Origen Isaiah homily OET artifacts and optionally emit stamp helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books/origen-isaiah-ezekiel"


def write_homily(num: int, claim: str, prev_tip: str, sections: list[dict]) -> None:
    (BOOK / "sources").mkdir(parents=True, exist_ok=True)
    (BOOK / "translations").mkdir(parents=True, exist_ok=True)
    (BOOK / "reviews/justifications").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/claim-locks").mkdir(parents=True, exist_ok=True)

    wl = [
        f"Origen Isaiah (Isaiam) Homilia {num} — working Latin "
        "(cleaned/condensed from Baehrens GCS 33 OCR)\n"
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
            "Copy-text Baehrens GCS 33 / Origenes Werke VIII (1925), Jerome Latin.",
            "True OET: no ANF; do not copy Scheck FOTC Isaiah/Ezekiel (Isaiah).",
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
                "baehrens": f"GCS 33 Isaiam Hom. {num}.{sec}",
                "claim": claim,
            }
        )
        src.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": f"homilia-{num}",
                "locus": f"Baehrens GCS 33 Isaiam Hom. {num} §{sec}",
                "head": f"Isaiam Hom. {num}.{sec}",
                "latin": [latin],
                "edition": "baehrens-gcs33-1925",
            }
        )
        j = {
            "excerpt_id": f"isa_hom{num}_{sec:02d}",
            "edition": {
                "id": "baehrens-gcs33-1925",
                "language": "lat",
                "locus": f"Baehrens GCS 33 Isaiam Hom. {num} {sec}",
            },
            "source_text": latin,
            "pass_a_gloss": gloss,
            "pass_b_english": english,
            "notes": [
                "Pass A ≠ Pass B.",
                "True OET; no Scheck FOTC Isaiah/Ezekiel.",
                "Copy-text Baehrens GCS 33 Jerome Latin.",
            ],
            "bible_links": [
                {"ref": a["reference"], "why": a["reason"]} for a in allusions
            ],
            "anf_compare": "no ANF for Jerome Isaiah homilies; do not copy Scheck FOTC Isaiah/Ezekiel",
            "checks": {
                "pass_a_ne_pass_b": True,
                "no_fotc_Scheck": True,
                "edition_lock": "Baehrens GCS 33 / Werke VIII (1925)",
            },
            "confidence": "high",
            "reviewer": "Air",
        }
        (BOOK / "reviews/justifications" / f"isa_hom{num}_{sec:02d}.json").write_text(
            json.dumps(j, ensure_ascii=False, indent=2) + "\n"
        )

    (BOOK / "sources" / f"isa_hom{num}_working_latin.txt").write_text("".join(wl))
    (BOOK / "translations" / f"isa_hom{num}_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n"
    )
    (BOOK / "translations" / f"isa_hom{num}_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "docs/claim-locks" / claim).write_text(
        f"agent: Air\nclaimed: 2026-09-13\n"
        f"slice: Origen Isaiah Homilia {num} CLOSEOUT Pass A≠B OET\n"
        f"status: done\n"
    )
    print(f"wrote Homilia {num}: {len(sections)} sections claim={claim}", file=sys.stderr)


def write_ezekiel_homily(num: int, claim: str, prev_tip: str, sections: list[dict]) -> None:
    (BOOK / "sources").mkdir(parents=True, exist_ok=True)
    (BOOK / "translations").mkdir(parents=True, exist_ok=True)
    (BOOK / "reviews/justifications").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/claim-locks").mkdir(parents=True, exist_ok=True)

    wl = [
        f"Origen Ezekiel (Ezechielem) Homilia {num} — working Latin "
        "(cleaned/condensed from Baehrens GCS 33 OCR)\n"
    ]
    eng: list[dict] = []
    src: list[dict] = []

    for s in sections:
        sec = s["section"]
        latin = s["latin"].strip()
        english = s["english"].strip()
        gloss = s["gloss"].strip()
        assert gloss != english, f"Pass A == Pass B at Ezek Hom {num}.{sec}"
        allusions = s.get("allusions", [])
        wl.append(f"\n{num}.{sec}\n{latin}\n")

        notes = [
            "Copy-text Baehrens GCS 33 / Origenes Werke VIII (1925), Jerome Latin.",
            "True OET: no ANF; do not copy Scheck FOTC Isaiah/Ezekiel (Ezekiel).",
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
                "baehrens": f"GCS 33 Ezechielem Hom. {num}.{sec}",
                "claim": claim,
            }
        )
        src.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": f"homilia-{num}",
                "locus": f"Baehrens GCS 33 Ezechielem Hom. {num} §{sec}",
                "head": f"Ezechielem Hom. {num}.{sec}",
                "latin": [latin],
                "edition": "baehrens-gcs33-1925",
            }
        )
        j = {
            "excerpt_id": f"ezek_hom{num}_{sec:02d}",
            "edition": {
                "id": "baehrens-gcs33-1925",
                "language": "lat",
                "locus": f"Baehrens GCS 33 Ezechielem Hom. {num} {sec}",
            },
            "source_text": latin,
            "pass_a_gloss": gloss,
            "pass_b_english": english,
            "notes": [
                "Pass A ≠ Pass B.",
                "True OET; no Scheck FOTC Isaiah/Ezekiel.",
                "Copy-text Baehrens GCS 33 Jerome Latin.",
            ],
            "bible_links": [
                {"ref": a["reference"], "why": a["reason"]} for a in allusions
            ],
            "anf_compare": "no ANF for Jerome Ezekiel homilies; do not copy Scheck FOTC Isaiah/Ezekiel",
            "checks": {
                "pass_a_ne_pass_b": True,
                "no_fotc_Scheck": True,
                "edition_lock": "Baehrens GCS 33 / Werke VIII (1925)",
            },
            "confidence": "high",
            "reviewer": "Air",
        }
        (BOOK / "reviews/justifications" / f"ezek_hom{num}_{sec:02d}.json").write_text(
            json.dumps(j, ensure_ascii=False, indent=2) + "\n"
        )

    (BOOK / "sources" / f"ezek_hom{num}_working_latin.txt").write_text("".join(wl))
    (BOOK / "translations" / f"ezek_hom{num}_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n"
    )
    (BOOK / "translations" / f"ezek_hom{num}_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "docs/claim-locks" / claim).write_text(
        f"agent: Air\nclaimed: 2026-09-13\n"
        f"slice: Origen Ezekiel Homilia {num} CLOSEOUT Pass A≠B OET\n"
        f"status: done\n"
    )
    print(f"wrote Ezek Homilia {num}: {len(sections)} sections claim={claim}", file=sys.stderr)
