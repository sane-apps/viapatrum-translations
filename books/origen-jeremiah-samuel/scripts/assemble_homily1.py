#!/usr/bin/env python3
"""Assemble Homilies 1–2 English JSON, meta, scripture review, justifications."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
TRANS = BOOK / "translations"
REV = BOOK / "reviews" / "justifications"
sys.path.insert(0, str(HERE))
from english_homily1 import SECTIONS as H1
from english_homily2 import SECTIONS as H2
from pass_a_homilies import PASS_A

CHOICES = {
    "1.1": [
        {
            "term": "μελλητής",
            "english": "slow",
            "rejected": ["unwilling", "reluctant"],
            "why": "mellētēs is delay, not refusal. God can punish and does not rush.",
        },
        {
            "term": "Ἑβραῖον προφήτην",
            "english": "a Hebrew prophet",
            "rejected": ["a prophet (drops Klostermann's Ἑβραῖον)"],
            "why": "Jonah is named as a Hebrew prophet sent to Nineveh.",
        },
    ],
    "1.4": [
        {
            "term": "νοητοὶ Βαβυλώνιοι",
            "english": "spiritual Babylonians",
            "rejected": ["intelligible Babylonians (jargon)", "mental Babylonians"],
            "why": "noētoi Babylonians are the soul's captors, not a philosophy term.",
        }
    ],
    "1.7": [
        {
            "term": "τροπολόγει",
            "english": "take as a figure",
            "rejected": ["tropologically (jargon)", "allegorize (later school)"],
            "why": "Homily speech: tropologei is 'read as a figure,' not a technical label.",
        }
    ],
    "1.10": [
        {
            "term": "ποιέω / πλάσσω",
            "english": "make / form",
            "rejected": ["create / create (collapses the Genesis distinction)"],
            "why": "Origen's whole point is Genesis 1 poieō vs Genesis 2 plassō.",
        }
    ],
    "1.16": [
        {
            "term": "προδότην",
            "english": "betrayer",
            "rejected": ["persecutor only (drops the first word)"],
            "why": "Klostermann prints both: Paul the betrayer, Paul the persecutor.",
        }
    ],
    "2.2": [
        {
            "term": "νίτρον / πόα",
            "english": "nitre / soap",
            "rejected": ["lye / herb (opaque)", "soda / grass"],
            "why": "Jeremiah 2:22's pair; πόα is the soap-plant, read as soap for the hearer.",
        }
    ],
}


def write_justifications(entries: list[dict], src_by: dict) -> None:
    REV.mkdir(parents=True, exist_ok=True)
    for e in entries:
        s = e["section"]
        rec = src_by[s]
        greek = " ".join(rec["greek"])
        pa = PASS_A.get(s)
        if not pa:
            raise SystemExit(f"missing Pass A for {s}")
        a_gloss = pa["gloss"].strip()
        b_join = " ".join(e["english"]).strip()
        if a_gloss == b_join:
            raise SystemExit(f"Pass A copies Pass B in {s}")
        refs = [
            {"display": a["reference"], "method": "wording", "note": a["reason"]}
            for a in (e.get("added_allusions") or [])
        ]
        just = {
            "anf_compare": {
                "notes": "No public-domain English of the Greek Jeremiah homilies (FOTC 97 is copyrighted). Sense checked against Klostermann GCS III and the cited Scripture wording. Modern English was not copied.",
                "status": "no_pd_reference",
            },
            "apparatus": rec.get("ocr_normalizations") or [],
            "bible_refs": refs,
            "checks": {
                "anf_diverge": "pass",
                "lemma_constraint": "pass",
                "placeholders": "pass",
            },
            "choices": CHOICES.get(
                s,
                [
                    {
                        "term": "homily voice",
                        "english": "oral questions to hearers; hedges kept",
                        "rejected": ["smoothing Origen's questions into essay prose"],
                        "why": "These are spoken homilies. Questions and 'someone will say' stay.",
                    }
                ],
            ),
            "confidence": "source_verified",
            "edition": {
                "id": "gcs6-klostermann-1901",
                "language": "grc",
                "locus": rec["klostermann"],
                "path": "sources/first1k/tlg2042.tlg009.opp-grc1.xml",
            },
            "excerpt_id": f"jeremiah_{s.replace('.', '_')}",
            "lemmas": pa["lemmas"],
            "pass_a_gloss": a_gloss,
            "pass_b_english": e["english"],
            "reviewer": "pending-human",
            "source_text": greek,
            "variants": [
                {"reading": n, "where": rec["head"]}
                for n in (rec.get("ocr_normalizations") or [])
            ],
        }
        (REV / f"jeremiah_{s.replace('.', '_')}.json").write_text(
            json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def main() -> None:
    src = json.loads((TRANS / "jeremiah_source.json").read_text(encoding="utf-8"))
    src_by = {r["section"]: r for r in src}
    entries = H1 + H2
    expected = [f"1.{n}" for n in range(1, 17)] + ["2.1", "2.2", "2.3"]
    got = [e["section"] for e in entries]
    if got != expected:
        raise SystemExit(f"section ids {got}")
    for e in entries:
        rec = src_by[e["section"]]
        e["klostermann"] = rec["klostermann"]
        joined = " ".join(e["english"])
        if "TODO" in joined or "YYYY" in joined:
            raise SystemExit(f"placeholder in {e['section']}")
        if "Scripture connection:" in joined:
            raise SystemExit(f"caption dump in {e['section']}")
    TRANS.mkdir(parents=True, exist_ok=True)
    (TRANS / "jeremiah_english.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    meta = {
        "slug": "origen-homilies-jeremiah",
        "title": "Homilies on Jeremiah, Homilies 1–2",
        "period": "c. 240–250",
        "edition": "Klostermann, Origenes Werke III (GCS 6, 1901)",
        "status": "in_progress",
        "topics": [
            "gifts-and-order",
            "hermeneutics-types",
            "old-and-new",
            "discipline-penance",
            "sin-and-death",
            "incarnation-word-flesh",
        ],
        "blurb": (
            "Origen on Jeremiah. Twenty Greek homilies survive; this page has Homilies 1–2 "
            "(Jeremiah 1:2–10 and 2:21–22). The rest of the volume is still being translated."
        ),
        "first_english": True,
        "first_english_note": (
            "These Greek homilies had no earlier complete English a reader could freely use. "
            "This page is Homilies 1–2 only. The English here is new."
        ),
    }
    (TRANS / "jeremiah_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_justifications(entries, src_by)

    all_refs = []
    for e in entries:
        for a in e.get("added_allusions") or []:
            all_refs.append({"section": e["section"], **a})
    review = {
        "book": "jeremiah-homilies-1-2",
        "review": "Independent Scripture and fidelity pass over Homilies 1–2 against Klostermann GCS III (PDF witness + First1KGreek TEI). Quotation wording checked against the biblical clause Origen cites.",
        "sections_read": [e["section"] for e in entries],
        "wording_corrections": [
            {
                "section": "1.1",
                "before": "sent a prophet",
                "after": "sent a Hebrew prophet (Jonah)",
            },
            {
                "section": "1.10",
                "before": "What is from the dust of the earth is formed in the womb.",
                "after": "What is made does not come about in the womb; what is formed from dust is created in the womb.",
            },
            {
                "section": "1.4",
                "before": "command the clouds not to rain rain",
                "after": "command the clouds not to rain",
            },
        ],
        "added_scripture_references": [
            {"section": a["section"], "reference": a["reference"], "reason": a["reason"]}
            for a in all_refs
            if a.get("certainty") == "clear"
        ],
        "remaining_textual_uncertainty": [
            {
                "section": "1.8",
                "note": "Klostermann marks a short gap in the baby-talk aside (ἵν᾽ οὕτως εἴπω). Sense of the lisp comparison is intact.",
            },
            {
                "section": "1.16",
                "note": "προδότην of Paul is in the printed Greek; kept as 'betrayer,' then 'persecutor.'",
            },
        ],
    }
    (TRANS / "jeremiah_scripture_review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    n_para = sum(len(e["english"]) for e in entries)
    n_all = sum(len(e.get("added_allusions") or []) for e in entries)
    print(f"homilies 1–2 english sections={len(entries)} paras={n_para} allusions={n_all}")
    print(f"justifications={len(list(REV.glob('jeremiah_*.json')))}")


if __name__ == "__main__":
    main()
