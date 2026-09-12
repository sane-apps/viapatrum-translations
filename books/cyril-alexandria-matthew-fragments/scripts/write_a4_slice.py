#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a4 (entries 13–16)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY_ORD = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean_join(text: str) -> str:
    t = " ".join(text.split())
    t = re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)
    return t


CLEAN = {n: clean_join(BY_ORD[n]["greek"][0]) for n in range(13, 17)}
CLAIM = "cyril-matt-frag-a4"

PASS_A = {
    13: (
        "No longer he says, flee, but go, hinting at relief after the trial; and saying "
        "the soul of the child he overturns the glory of Apollinaris saying the Lord took "
        "flesh without mind and without soul. And in the economic descent of the Christ into "
        "Egypt and the from-there again into Judea return God recapitulates the captivity of "
        "the people and redeems him from plot leading again onto his own."
    ),
    14: (
        "Yet it is worth noting that Nazareth lay in the extremities of Judea, into which "
        "having settled Christ shows that because of the Jews' murderousness he was about to "
        "leave Judea and go over onto the nations for the sake of having given to the "
        "learning-loving an occasion of the into Christ faith. In the last [parts] of Judea "
        "lay Nazareth. And having left Judea and gone away into Nazareth Christ clearly "
        "showed that he will leave Jews and will transfer onto the nations the worship. And "
        "at the same time also to the learning-loving he will give a cause of believing into him."
    ),
    15: (
        "And if the Nazorean is interpreted holy or according to some flower, this name is "
        "found beside many; for 'holy of holies' Daniel names him. And Isaiah: 'a rod out of "
        "the root of Jesse and a flower out of it' and the Lord himself about himself says in "
        "the song of songs: 'I [am] a flower of a field, a lily of the valleys'."
    ),
    16: (
        "Kingdom of the heavens [is] the through faith justification and the through spirit "
        "sanctification; wherefore also elsewhere: 'the kingdom' of the heavens 'is within you'."
    ),
}

PASS_B = {
    13: [
        (
            "He no longer says “flee,” but “go,” hinting at relief after the trial. By speaking "
            "of the child’s soul he overturns Apollinaris’s claim that the Lord took flesh "
            "without mind and without soul."
        ),
        (
            "In Christ’s economic descent into Egypt and his return from there into Judea, God "
            "recapitulates the people’s captivity and redeems them from the plot, leading them "
            "home again."
        ),
    ],
    14: [
        (
            "It is worth noting that Nazareth lay at the edges of Judea. By settling there, "
            "Christ shows that because of the Jews’ murderousness he was about to leave Judea "
            "and go over to the nations, giving lovers of learning an occasion for faith in Christ."
        ),
        (
            "Nazareth lay in the last parts of Judea. Leaving Judea for Nazareth, Christ showed "
            "clearly that he would leave the Jews and transfer worship to the nations — and at "
            "the same time give lovers of learning a reason to believe in him."
        ),
    ],
    15: [
        (
            "If “Nazorean” is interpreted “holy,” or according to some “flower,” the name shows "
            "up in many places. Daniel calls him “holy of holies.” Isaiah says, “a rod from the "
            "root of Jesse and a flower from it.” And the Lord says of himself in the Song of "
            "Songs, “I am a flower of the field, a lily of the valleys.”"
        ),
    ],
    16: [
        (
            "The kingdom of the heavens is justification through faith and sanctification "
            "through the Spirit. That is why he also says elsewhere, “The kingdom of the "
            "heavens is within you.”"
        ),
    ],
}

LEMMAS = {
    13: [
        {"form": "ἄνεσιν", "lemma": "ἄνεσις", "gloss": "relief / easing", "lexica": "LSJ"},
        {"form": "ἄνουν καὶ ἄψυχον", "lemma": "ἄνους / ἄψυχος", "gloss": "mindless and soulless", "lexica": "Apollinaris polemic"},
        {"form": "ἀνακεφαλαιοῦται", "lemma": "ἀνακεφαλαιόω", "gloss": "recapitulates", "lexica": "patristic"},
    ],
    14: [
        {"form": "μιαιφόνον", "lemma": "μιαιφόνος", "gloss": "murderous / bloodstained", "lexica": "LSJ"},
        {"form": "φιλομαθέσιν", "lemma": "φιλομαθής", "gloss": "lovers of learning", "lexica": "LSJ"},
    ],
    15: [
        {"form": "Ναζωραῖος", "lemma": "Ναζωραῖος", "gloss": "Nazorean", "lexica": "biblical"},
        {"form": "ἄνθος", "lemma": "ἄνθος", "gloss": "flower", "lexica": "Isa 11:1 / Song"},
    ],
    16: [
        {"form": "δικαίωσις", "lemma": "δικαίωσις", "gloss": "justification", "lexica": "NT"},
        {"form": "ἁγιασμός", "lemma": "ἁγιασμός", "gloss": "sanctification", "lexica": "NT"},
    ],
}

CHOICES = {
    13: [{
        "term": "ἄνουν καὶ ἄψυχον",
        "english": "without mind and without soul",
        "rejected": ["foolish and lifeless (weak)"],
        "why": "Technical anti-Apollinarian pairing.",
    }],
    14: [{
        "term": "μιαιφόνον",
        "english": "murderousness",
        "rejected": ["pollution only"],
        "why": "Blood-guilt toward Christ, not generic uncleanness.",
    }],
    15: [{
        "term": "ἄνθος",
        "english": "flower",
        "rejected": ["blossom (too soft)"],
        "why": "Matches Isaiah / Song lemma Cyril stacks.",
    }],
    16: [{
        "term": "δικαίωσις … ἁγιασμός",
        "english": "justification … sanctification",
        "rejected": ["making righteous … making holy (wordy)"],
        "why": "Keep Pauline twin terms Cyril pairs with the kingdom.",
    }],
}

ALLUSIONS = {
    13: [
        {"reference": "Matthew 2:20", "reason": "Go into the land of Israel.", "certainty": "clear"},
        {"reference": "Hosea 11:1", "reason": "Out of Egypt recapitulated.", "certainty": "possible"},
    ],
    14: [{"reference": "Matthew 2:23", "reason": "He shall be called a Nazorean / Nazareth dwelling.", "certainty": "clear"}],
    15: [
        {"reference": "Matthew 2:23", "reason": "Nazorean name.", "certainty": "clear"},
        {"reference": "Daniel 9:24", "reason": "Holy of holies.", "certainty": "possible"},
        {"reference": "Isaiah 11:1", "reason": "Rod/flower from Jesse.", "certainty": "clear"},
        {"reference": "Song of Songs 2:1", "reason": "Flower of the field / lily.", "certainty": "clear"},
    ],
    16: [
        {"reference": "Matthew 3:2", "reason": "Kingdom of heaven lemma.", "certainty": "clear"},
        {"reference": "Luke 17:21", "reason": "Kingdom within you.", "certainty": "clear"},
    ],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    clean_sections = []
    for ord_ in range(13, 17):
        src = BY_ORD[ord_]
        a, b = PASS_A[ord_], " ".join(PASS_B[ord_])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {ord_}")
        ed = src["fragment"]
        clean_sections.append(
            {
                "section": ord_,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "locus": src["locus"],
                "head": src["head"],
                "greek": [CLEAN[ord_]],
                "claim": CLAIM,
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "whitespace; no IA merge",
            }
        )
        english.append(
            {
                "section": ord_,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "title": src["head"],
                "english": PASS_B[ord_],
                "notes_covered": [],
                "added_allusions": ALLUSIONS[ord_],
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract.",
                    "Section id = source array order (1-based).",
                    "IA OCR not reading text.",
                ],
                "claim": CLAIM,
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{ord_:02d}",
            "section": ord_,
            "edition_fragment": ed,
            "matthew": src["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": CLAIM,
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": src["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a4.json",
            },
            "source_text": CLEAN[ord_],
            "pass_a_gloss": PASS_A[ord_],
            "pass_b_english": PASS_B[ord_],
            "lemmas": LEMMAS[ord_],
            "choices": CHOICES[ord_],
            "variants": [
                {
                    "witnesses": [
                        "khazarzar-aegean-pg72-extract",
                        "matia-aegean-pg72-extract-mirror",
                    ],
                    "note": "PDFs byte-identical.",
                },
                {"witnesses": ["ia-bim-pg72-djvu-ocr"], "note": "Not copy-text; no merge."},
            ],
            "guards": {
                "pass_a_ne_pass_b": True,
                "cpg_5219_5220_closed": True,
                "melito_skipped": True,
                "no_css": True,
                "jer_h20b_preserved": True,
            },
        }
        out = ROOT / f"reviews/justifications/matt_frag_{ord_:02d}.json"
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name, "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a4.json").write_text(
        json.dumps(
            {"meta": {"claim": CLAIM, "sections": "13-16"}, "sections": clean_sections},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    english.sort(key=lambda e: e["section"])
    eng_path.write_text(json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english", [e["section"] for e in english])


if __name__ == "__main__":
    main()
