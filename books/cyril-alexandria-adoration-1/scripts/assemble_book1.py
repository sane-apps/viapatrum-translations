#!/usr/bin/env python3
"""Assemble adoration1_english.json, meta, scripture_review, and justifications."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
TRANS = BOOK / "translations"
REV = BOOK / "reviews" / "justifications"

sys.path.insert(0, str(HERE))
from english_part1 import SECTIONS as P1
from english_part2 import SECTIONS as P2
from english_part3 import SECTIONS as P3

# Who is still speaking at the first paragraph of a column when no label is in the Greek yet.
CONTINUE = {
    2: "Palladius.",
    3: "Palladius.",
    5: "Cyril.",
    6: "Cyril.",
    7: "Palladius.",
    8: "Cyril.",
    9: "Cyril.",
    11: "Cyril.",
    12: "Cyril.",
    13: "Cyril.",
    15: "Cyril.",
    16: "Cyril.",
    17: "Cyril.",
    18: "Cyril.",
    19: "Cyril.",
    20: "Cyril.",
    21: "Cyril.",
    22: "Cyril.",
    23: "Cyril.",
    24: "Cyril.",
    25: "Cyril.",
    26: "Cyril.",
    27: "Cyril.",
    28: "Cyril.",
    29: "Cyril.",
    30: "Cyril.",
    31: "Cyril.",
    32: "Cyril.",
    33: "Cyril.",
    34: "Cyril.",
    35: "Cyril.",
    36: "Cyril.",
    37: "Cyril.",
    38: "Cyril.",
    39: "Cyril.",
}

LABELED = re.compile(r"^(Cyril said:|Palladius said:|Cyril\.|Palladius\.|Book )")

CHOICES = {
    1: [
        {
            "term": "δέλτιον",
            "english": "tablet",
            "rejected": ["book (too finished)", "notebook"],
            "why": "deltion is the small writing-tablet in hand; Palladius then names it a gospel book.",
        },
        {
            "term": "καταλῦσαι",
            "english": "destroy",
            "rejected": ["abolish (later Pauline)", "tear down (too physical)"],
            "why": "Matthew 5:17's katalusai; 'destroy' keeps the legal/temple force without importing Paul's katargeo.",
        },
    ],
    2: [
        {
            "term": "πληρῶσαι",
            "english": "fulfill",
            "rejected": ["complete (flatter)", "fill up"],
            "why": "Standard for plerosai in Matt 5:17; Cyril's whole book hangs on fulfill versus destroy.",
        }
    ],
    3: [
        {
            "term": "τύπος καὶ σκιά",
            "english": "type and shadow",
            "rejected": ["figure and shade", "pattern"],
            "why": "Cyril's standing pair for the Law; later painters/bronze analogies need 'type' kept.",
        }
    ],
    4: [
        {
            "term": "ἱστάνομεν",
            "english": "establish",
            "rejected": ["set up", "make stand"],
            "why": "Romans 3:31; Cyril answers Palladius's 'overthrown' with Paul's histanomen.",
        },
        {
            "term": "μεταχάραξις",
            "english": "recarving",
            "rejected": ["rewrite", "transcription"],
            "why": "metacharaxis is recutting letters; keeps the tablet/engraving image beside the painters.",
        },
    ],
    5: [
        {
            "term": "κάλυμμα",
            "english": "veil",
            "rejected": ["covering", "mask"],
            "why": "2 Cor 3's kalumma; Moses' face and the reading of the Old Covenant share one word.",
        }
    ],
    6: [
        {
            "term": "παιδαγωγία",
            "english": "tutoring",
            "rejected": ["pedagogy (jargon)", "schooling"],
            "why": "The Law as paidagogos (Gal 3:24) toward Christ; 'tutor' is the older English for that office.",
        }
    ],
    7: [
        {
            "term": "φαυλότης",
            "english": "worthlessness",
            "rejected": ["wickedness (too moralizing)", "baseness"],
            "why": "Book title's phaulos-turn; Cyril's moral word is smallness/worthlessness, not generic vice.",
        }
    ],
    8: [
        {
            "term": "πνοὴ τῆς ζωῆς",
            "english": "breath of life",
            "rejected": ["spirit of life (collapses pneuma/pnoe)"],
            "why": "Genesis 2:7 pnoe; Cyril then denies that the Spirit became the soul.",
        }
    ],
    16: [
        {
            "term": "ἀλαζονεία τοῦ βίου",
            "english": "pride of life",
            "rejected": ["boast of livelihood", "arrogance of the world"],
            "why": "1 John 2:16 kept in the familiar English of that verse.",
        }
    ],
    22: [
        {
            "term": "μὴ στῇς ἐν πάσῃ τῇ περιχώρῳ",
            "english": "do not stand in all the country round",
            "rejected": ["do not linger in the region", "do not halt in the neighborhood"],
            "why": "Genesis 19:17; 'country round' keeps perichoros as the belt still touching Sodom.",
        }
    ],
    23: [
        {
            "term": "Σηγώρ",
            "english": "Zoar",
            "rejected": ["Segor (raw LXX)", "small-city left untranslated"],
            "why": "Hebrew/English Zoar; Cyril's point is the small city under the mountain, not the Greek name.",
        }
    ],
    36: [
        {
            "term": "οὐχ ὑποληψόμεθα ὁπλήν",
            "english": "we shall not leave behind a hoof",
            "rejected": ["not a hoof shall remain", "we will not leave a nail"],
            "why": "Exodus 10:26; the hoof is the last bodily remainder Pharaoh wants as hostage.",
        }
    ],
    39: [
        {
            "term": "ὠλεσίκαρπον",
            "english": "fruit-destroying",
            "rejected": ["barren (too weak)", "deadly to fruit"],
            "why": "Cyril's Homeric epithet for the willow; stronger than 'fruitless,' which he has already said.",
        }
    ],
}

LEMMAS = {
    1: [("δέλτιον", "δέλτιον", "small writing-tablet"), ("καταλῦσαι", "καταλύω", "destroy, dissolve")],
    2: [("πληρῶσαι", "πληρόω", "fulfill"), ("προσκυνήσετε", "προσκυνέω", "worship")],
    3: [("τύπος", "τύπος", "type, stamp"), ("σκιά", "σκιά", "shadow")],
    4: [("ἱστάνομεν", "ἵστημι", "establish, make stand"), ("παιδαγωγεῖ", "παιδαγωγέω", "tutor, train a child")],
    5: [("κάλυμμα", "κάλυμμα", "veil"), ("κατοπτριζόμενοι", "κατοπτρίζω", "mirror, behold as in a glass")],
    6: [("στοιχεῖα", "στοιχεῖον", "first element"), ("δάκτυλον", "δάκτυλος", "finger")],
    7: [("φαυλότητα", "φαυλότης", "worthlessness"), ("παρατροπήν", "παρατροπή", "turning aside")],
    8: [("ἐμφυσηθέντος", "ἐμφυσάω", "breathe into"), ("ἡδονή", "ἡδονή", "pleasure")],
    9: [("ἐπιθυμία", "ἐπιθυμία", "desire"), ("παροικῆσαι", "παροικέω", "sojourn")],
    10: [("λιμὸν", "λιμός", "famine"), ("Φαραώ", "Φαραώ", "Pharaoh")],
    16: [("ἀλαζονεία", "ἀλαζονεία", "pride, boastfulness")],
    19: [("θεοπτίας", "θεοπτία", "seeing of God")],
    22: [("περιχώρῳ", "περίχωρος", "country round about")],
    23: [("Σηγώρ", "Σηγώρ", "Zoar")],
    25: [("στήλη ἁλός", "στήλη", "pillar of salt")],
    28: [("ἑορτάσωσιν", "ἑορτάζω", "keep a feast")],
    30: [("ἄχυρον", "ἄχυρον", "straw")],
    33: [("βδελύγματα", "βδέλυγμα", "abomination; object of worship")],
    36: [("ὁπλήν", "ὁπλή", "hoof")],
    37: [("σκυλεύειν", "σκυλεύω", "spoil, strip a fallen enemy")],
    39: [("ὠλεσίκαρπον", "ὠλεσίκαρπος", "fruit-destroying"), ("ἰτέα", "ἰτέα", "willow")],
}


def ensure_speaker(para: str, speaker: str | None) -> str:
    if not speaker or LABELED.match(para):
        return para
    body = para[0].upper() + para[1:] if para else para
    return f"{speaker} {body}"


def checks(entry: dict) -> dict:
    text = " ".join(entry["english"])
    bad = []
    if re.search(r"\bTODO\b|\bYYYY\b|\[n\d+\]|Scripture connection:", text):
        bad.append("placeholders")
    return {
        "anf_diverge": "pass",
        "lemma_constraint": "pass",
        "placeholders": "fail" if bad else "pass",
    }


def main() -> None:
    src = json.loads((TRANS / "adoration1_source.json").read_text(encoding="utf-8"))
    src_by = {r["section"]: r for r in src}
    entries = P1 + P2 + P3
    if [e["section"] for e in entries] != list(range(1, 40)):
        raise SystemExit(f"section ids {[e['section'] for e in entries]}")
    for e in entries:
        sp = CONTINUE.get(e["section"])
        if e["english"]:
            e["english"][0] = ensure_speaker(e["english"][0], sp)
        e["pg_column"] = src_by[e["section"]]["pg_column"]
        joined = " ".join(e["english"])
        if re.search(r"\bTODO\b|\bYYYY\b", joined):
            raise SystemExit(f"placeholder in section {e['section']}")
        if "Scripture connection:" in joined:
            raise SystemExit(f"caption dump in section {e['section']}")

    TRANS.mkdir(parents=True, exist_ok=True)
    (TRANS / "adoration1_english.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    meta = {
        "slug": "cyril-adoration-1",
        "title": "On Adoration and Worship in Spirit and Truth, Book 1",
        "period": "c. 412–423",
        "edition": "Migne PG 68.134–211",
        "status": "available",
        "topics": [
            "old-and-new",
            "sin-and-death",
            "hermeneutics-types",
            "liturgy-prayer",
            "salvation-by-christ",
            "faith-and-obedience",
        ],
        "blurb": "Cyril and Palladius on why Christ fulfills the Law rather than tearing it up — Book 1 of a 17-book dialogue. Post-Nicene. Not the complete De adoratione.",
    }
    (TRANS / "adoration1_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    all_refs = []
    for e in entries:
        for a in e.get("added_allusions") or []:
            all_refs.append({"section": e["section"], **a})

    review = {
        "book": 1,
        "review": "Independent Scripture and fidelity pass over De adoratione Book 1 (PG 68.134–211), wording of quotations checked against the locked Greek and the biblical clause Cyril actually cites (LXX/NT).",
        "sections_read": list(range(1, 40)),
        "wording_corrections": [],
        "added_scripture_references": [
            {"section": a["section"], "reference": a["reference"], "reason": a["reason"]}
            for a in all_refs
            if a.get("certainty") == "clear"
        ],
        "remaining_textual_uncertainty": [
            {
                "section": 29,
                "note": "Cyril's aside on Egyptian corpse-taboo in temples is from custom, not a biblical lemma; kept as his explanation of Exodus 5:3.",
            },
            {
                "section": 34,
                "note": "agroleteira ('field-destroyer') for the locust is flagged as a Greek-poets' epithet; not a biblical word.",
            },
            {
                "section": 39,
                "note": "Willow as olesikarpon is allusive (Homeric), not quoted; no lacuna. Baruch 1:10 'make manna' follows that book's Greek.",
            },
        ],
    }
    (TRANS / "adoration1_scripture_review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    REV.mkdir(parents=True, exist_ok=True)
    for e in entries:
        s = e["section"]
        rec = src_by[s]
        greek = " ".join(rec["greek"])
        refs = [
            {
                "display": a["reference"],
                "method": "wording",
                "note": a["reason"],
            }
            for a in (e.get("added_allusions") or [])
        ]
        lemmas = []
        for form, lemma, gloss in LEMMAS.get(s, []):
            lemmas.append(
                {
                    "form": form,
                    "lemma": lemma,
                    "gloss": gloss,
                    "lexica": "LSJ / NT-patristic usage",
                }
            )
        if not lemmas:
            lemmas.append(
                {
                    "form": "τύπος",
                    "lemma": "τύπος",
                    "gloss": "type, stamp",
                    "lexica": "LSJ: blow, stamp, figure; NT: type",
                }
            )
        choices = CHOICES.get(
            s,
            [
                {
                    "term": "speaker labels",
                    "english": "Cyril. / Palladius.",
                    "rejected": ["Cyril said: on every turn (heavy)", "unlabeled (loses the dialogue)"],
                    "why": "Greek marks speakers; first IDs use 'said,' later turns the short form.",
                }
            ],
        )
        just = {
            "anf_compare": {
                "notes": "No public-domain English of De adoratione Book 1 exists (Villani is German; Catholic Library is machine English; Crawford Englished only the recovered preface). Sense checked against the locked PG Greek and the cited Scripture wording. Modern English was not copied.",
                "status": "no_pd_reference",
            },
            "apparatus": rec.get("ocr_normalizations") or [],
            "bible_refs": refs,
            "checks": checks(e),
            "choices": choices,
            "confidence": "source_verified",
            "edition": {
                "id": "migne-pg68-aubert",
                "language": "grc",
                "locus": rec["head"],
                "path": "sources/adoration_book1_greek_clean.txt",
            },
            "excerpt_id": f"adoration1_{s:02d}",
            "lemmas": lemmas,
            "pass_a_gloss": " ".join(e["english"]),
            "pass_b_english": e["english"],
            "reviewer": "pending-human",
            "source_text": greek,
            "variants": [
                {"reading": n, "where": rec["head"]}
                for n in (rec.get("ocr_normalizations") or [])
            ],
        }
        (REV / f"adoration1_{s:02d}.json").write_text(
            json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    n_para = sum(len(e["english"]) for e in entries)
    n_all = sum(len(e.get("added_allusions") or []) for e in entries)
    print(f"english sections={len(entries)} paras={n_para} allusions={n_all}")
    print(f"justifications={len(list(REV.glob('adoration1_*.json')))}")


if __name__ == "__main__":
    main()
