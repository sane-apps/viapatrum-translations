#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a2 (entries 5–8) and a3 (9–12)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from reader_titles import reader_title, scholar_label

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY_ORD = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean_join(text: str) -> str:
    t = " ".join(text.split())
    t = re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)
    return t


CLEAN = {n: clean_join(BY_ORD[n]["greek"][0]) for n in range(5, 13)}

PASS_A = {
    5: (
        "But the not saying 'through whom he was born' perhaps, but 'out of whom', "
        "overturns the heresy of Apollinaris saying that through a tube of the virgin "
        "the Christ passed and nothing from her he took. For the evangelist does not say "
        "the Jesus was born through her, but out of her, that is out of her all-holy bloods; "
        "such also is the [word] of the apostle: for 'he sent', he says, 'God his son, "
        "becoming out of woman', but not through woman."
    ),
    6: (
        "Woman her the angel called, in order that of every suspicion toward another "
        "person he might free the virgin; for if of Joseph woman her he calls — of the one "
        "having without union toward her — then neither toward another someone has "
        "suspicion's thought the virgin."
    ),
    7: (
        "If a people he has even before being born out of Mary and he saves, clear that as God."
    ),
    8: (
        "After the betrothal she conceived, in order that she might seem out of him to have "
        "been pregnant and in order that out of him she might be genealogized and might have "
        "also a guardian in the plots."
    ),
    9: (
        "Not the of the magi voice disturbed him, but the being noised about beside all the "
        "law-learned and those believing the prophets' words; for the magi a king were seeking, "
        "but the Jews Christ were publishing to have been born. Wherefore leaving the magi, "
        "and calling the Jews he was asking where the Christ is born, whom now you, he says, "
        "publish having heard the magi. And the of the truth enemies even unwilling say the "
        "truth and the prophecy interpret in vain wholly; for they did not add the next. And "
        "ambassadors he calls the magi, since in a way they came toward the king of Israel, "
        "in order that they might embassage and peace come about between them and the "
        "Israelites and come about of the nations and Jews 'one flock, one shepherd' of both. "
        "And what was this, that the exits of him from beginning — from the limits of the "
        "inhabited world they come about to see the manger."
    ),
    10: (
        "Israel first the Jacob was called, when he had seen the ladder and the angels going "
        "up and going down upon him through it and he wrestled with the one appeared to him "
        "and from him heard: 'no longer the name of you Jacob, but Israel'. And with this name "
        "all the of the Jews people was called as with an exceptional and divine [name] and "
        "from the other nations distinguishing them. And Israel is mind seeing the God. "
        "Wherefore also the out-of-nations church Israel was named not according to flesh, "
        "but according to divine grace."
    ),
    11: (
        "But whether together with the being born they arrived and in swaddling-clothes "
        "beheld the Christ the magi, or in a house with the mother sitting? More truly I "
        "think the in swaddling-clothes. Wherefore also, as above we said, the star before "
        "the of the Lord birth appeared. And from this clear, that it preceded also the of "
        "the magi arrival."
    ),
    12: (
        "Stood the star a fixture one unmoved, in order that the magi no longer go forward; "
        "not indeed having come down out of heaven it stood upon earth, nor above the house "
        "did it fix itself — having a custom not according to the of the others motion to "
        "make the journey, but a strange some course making and at other times in other "
        "appearing climates then only it stood unmoved. Unmoved was the star and standing, "
        "but not the heaven having left near the earth it was going nor upon the house was "
        "it fixed; for not the same motion with the remaining stars it was making, but a "
        "strange some and outlandish."
    ),
}

PASS_B = {
    5: [
        (
            "Matthew does not say “through whom” he was born, but “out of whom.” That "
            "overthrows Apollinaris, who claimed Christ passed through the virgin as through "
            "a tube and took nothing from her."
        ),
        (
            "The evangelist says Jesus was born not through her but out of her — that is, "
            "from her all-holy blood. The apostle speaks the same way: “God sent his Son, "
            "born of a woman,” not through a woman."
        ),
    ],
    6: [
        (
            "The angel called her Joseph’s wife so no one would suspect another man. If she "
            "is named the wife of Joseph, who had not known her, the virgin is free of any "
            "thought of suspicion toward someone else."
        ),
    ],
    7: [
        (
            "If he already has a people and saves them before he is born of Mary, it is clear "
            "he does so as God."
        ),
    ],
    8: [
        (
            "She conceived after the betrothal so she would seem to have carried a child by "
            "Joseph, so the genealogy could run through him, and so she would have a guardian "
            "when plots rose against them."
        ),
    ],
    9: [
        (
            "It was not the magi’s voice that disturbed Herod, but the rumor among all who "
            "knew the law and trusted the prophets’ words. The magi were seeking a king; the "
            "Jews were publishing that the Christ had been born."
        ),
        (
            "So he left the magi, called the Jews, and asked where the Christ is born — “the "
            "one you are now publishing,” he says, “after hearing the magi.” Even unwilling, "
            "the enemies of the truth speak the truth and interpret the whole prophecy — yet "
            "in vain, for they did not add what follows."
        ),
        (
            "He calls the magi ambassadors because in a way they came to the king of Israel "
            "to make peace between themselves and Israel, so that of the nations and the Jews "
            "there might be “one flock, one shepherd.”"
        ),
        (
            "And what did that mean — that “his goings forth are from the beginning”? People "
            "come from the ends of the inhabited world to see the manger."
        ),
    ],
    10: [
        (
            "Jacob was first called Israel when he saw the ladder and the angels going up and "
            "down on it through him, wrestled with the one who appeared to him, and heard from "
            "him, “Your name shall no longer be Jacob, but Israel.”"
        ),
        (
            "The whole Jewish people received that name as something exceptional and divine, "
            "setting them apart from the other nations. Israel means a mind that sees God. "
            "That is why the church from the nations was also named Israel — not according to "
            "flesh, but according to divine grace."
        ),
    ],
    11: [
        (
            "Did the magi arrive at the birth itself and see Christ in swaddling clothes, or "
            "find him later sitting in a house with his mother? I think the truer reading is "
            "the swaddling clothes."
        ),
        (
            "That is also why, as we said above, the star appeared before the Lord’s birth. "
            "From this it is clear that the star also preceded the magi’s arrival."
        ),
    ],
    12: [
        (
            "The star stood as a single unmoved fixture so the magi would go no farther. It "
            "did not come down from heaven and stand on the earth, nor lodge itself above the "
            "house. Its custom was not to travel like the other stars, but to run a strange "
            "course, appearing at different times in different regions — and only then did it "
            "stand still."
        ),
        (
            "The star was unmoved and standing, yet it had not left heaven to travel near the "
            "earth, nor was it fixed on the house. It did not share the other stars’ motion, "
            "but a strange and outlandish one."
        ),
    ],
}

LEMMAS = {
    5: [
        {"form": "δι' ἧς / ἐξ ἧς", "lemma": "διά / ἐκ", "gloss": "through vs out of", "lexica": "LSJ"},
        {"form": "σωλῆνος", "lemma": "σωλήν", "gloss": "tube / pipe", "lexica": "LSJ"},
        {"form": "πανάγνων … αἱμάτων", "lemma": "παναγνος / αἷμα", "gloss": "all-holy bloods", "lexica": "patristic"},
    ],
    6: [
        {"form": "ἀμυήτως", "lemma": "ἀμύητος", "gloss": "without marital union", "lexica": "LSJ"},
        {"form": "ὑποψίας", "lemma": "ὑποψία", "gloss": "suspicion", "lexica": "LSJ"},
    ],
    7: [
        {"form": "λαὸν ἔχει", "lemma": "λαός", "gloss": "has a people", "lexica": "biblical"},
        {"form": "ὡς θεός", "lemma": "θεός", "gloss": "as God", "lexica": "patristic"},
    ],
    8: [
        {"form": "μνηστείαν", "lemma": "μνηστεία", "gloss": "betrothal", "lexica": "LSJ"},
        {"form": "κηδεμόνα", "lemma": "κηδεμών", "gloss": "guardian", "lexica": "LSJ"},
    ],
    9: [
        {"form": "θρυλεῖσθαι", "lemma": "θρυλέω", "gloss": "be noised abroad", "lexica": "LSJ"},
        {"form": "πρέσβεις", "lemma": "πρέσβυς", "gloss": "ambassadors", "lexica": "LSJ"},
        {"form": "μία ποίμνη", "lemma": "ποίμνη", "gloss": "one flock", "lexica": "John 10:16"},
    ],
    10: [
        {"form": "κλίμακα", "lemma": "κλίμαξ", "gloss": "ladder", "lexica": "Gen 28"},
        {"form": "νοῦς ὁρῶν τὸν θεόν", "lemma": "νοῦς / ὁράω", "gloss": "mind seeing God", "lexica": "etymology"},
    ],
    11: [
        {"form": "σπαργάνοις", "lemma": "σπάργανον", "gloss": "swaddling clothes", "lexica": "LSJ"},
        {"form": "προέλαβε", "lemma": "προλαμβάνω", "gloss": "precede", "lexica": "LSJ"},
    ],
    12: [
        {"form": "πῆγμα", "lemma": "πῆγμα", "gloss": "fixture", "lexica": "LSJ"},
        {"form": "ἀκίνητον", "lemma": "ἀκίνητος", "gloss": "unmoved", "lexica": "LSJ"},
        {"form": "ἀλλόκοτον", "lemma": "ἀλλόκοτος", "gloss": "outlandish", "lexica": "LSJ"},
    ],
}

CHOICES = {
    5: [{
        "term": "δι' ἧς vs ἐξ ἧς",
        "english": "through whom vs out of whom",
        "rejected": ["by whom (ambiguous)"],
        "why": "The διά/ἐκ contrast is the anti-Apollinarian point.",
    }],
    6: [{
        "term": "ἀμυήτως",
        "english": "who had not known her",
        "rejected": ["uninitiated (cult tone)"],
        "why": "Joseph’s chastity toward Mary.",
    }],
    7: [{
        "term": "ὡς θεός",
        "english": "as God",
        "rejected": ["like a god"],
        "why": "Deity claim, not simile.",
    }],
    8: [{
        "term": "κηδεμόνα",
        "english": "guardian",
        "rejected": ["husband (over-reads)"],
        "why": "Protective role in the plots.",
    }],
    9: [{
        "term": "πρέσβεις",
        "english": "ambassadors",
        "rejected": ["elders"],
        "why": "Diplomatic embassy; fits one flock.",
    }],
    10: [{
        "term": "νοῦς ὁρῶν τὸν θεόν",
        "english": "a mind that sees God",
        "rejected": ["man who sees God"],
        "why": "Traditional etymological gloss.",
    }],
    11: [{
        "term": "ἐν σπαργάνοις",
        "english": "in swaddling clothes",
        "rejected": ["in a crib only"],
        "why": "Chronology hinges on newborn swaddling.",
    }],
    12: [{
        "term": "πῆγμα … ἀκίνητον",
        "english": "unmoved fixture",
        "rejected": ["frozen statue"],
        "why": "Astral pause, not a landed roof object.",
    }],
}

ALLUSIONS = {
    5: [
        {"reference": "Matthew 1:16", "reason": "Lemma: out of whom Jesus was born.", "certainty": "clear"},
        {"reference": "Galatians 4:4", "reason": "Quoted: born of a woman.", "certainty": "clear"},
    ],
    6: [{"reference": "Matthew 1:20", "reason": "Angel calls Mary Joseph’s wife.", "certainty": "clear"}],
    7: [{"reference": "Matthew 1:21", "reason": "He will save his people.", "certainty": "clear"}],
    8: [{"reference": "Matthew 1:24", "reason": "Joseph takes Mary after the annunciation.", "certainty": "clear"}],
    9: [
        {"reference": "Matthew 2:3-6", "reason": "Herod, priests, Bethlehem prophecy.", "certainty": "clear"},
        {"reference": "John 10:16", "reason": "One flock, one shepherd.", "certainty": "clear"},
        {"reference": "Micah 5:2", "reason": "Goings forth from the beginning.", "certainty": "possible"},
    ],
    10: [
        {"reference": "Matthew 2:6", "reason": "Israel in the Bethlehem citation.", "certainty": "clear"},
        {"reference": "Genesis 28:12", "reason": "Jacob’s ladder.", "certainty": "clear"},
        {"reference": "Genesis 32:28", "reason": "Rename to Israel.", "certainty": "clear"},
    ],
    11: [
        {"reference": "Matthew 2:7-11", "reason": "Magi find the child.", "certainty": "clear"},
        {"reference": "Luke 2:7", "reason": "Swaddling clothes.", "certainty": "possible"},
    ],
    12: [{"reference": "Matthew 2:9", "reason": "Star stops over the place.", "certainty": "clear"}],
}

CLAIMS = {n: ("cyril-matt-frag-a2" if n <= 8 else "cyril-matt-frag-a3") for n in range(5, 13)}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8")) if eng_path.exists() else []
    english = [e for e in english if e.get("section") not in CLEAN]

    clean_sections = []
    for ord_ in range(5, 13):
        src = BY_ORD[ord_]
        a = PASS_A[ord_]
        b = " ".join(PASS_B[ord_])
        if a.strip() == b.strip():
            raise SystemExit(f"Pass A == Pass B at ord {ord_}")
        claim = CLAIMS[ord_]
        ed_frag = src["fragment"]
        clean_sections.append(
            {
                "section": ord_,
                "edition_fragment": ed_frag,
                "matthew": src["matthew"],
                "locus": src["locus"],
                "head": src["head"],
                "greek": [CLEAN[ord_]],
                "claim": claim,
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "whitespace + stray mid-phrase digits; no IA merge",
            }
        )
        english.append(
            {
                "section": ord_,
                "edition_fragment": ed_frag,
                "matthew": src["matthew"],
                "title": reader_title(src.get("matthew")),
                "scholar_label": scholar_label(fragment=src.get("fragment"), matthew=src.get("matthew"), existing=src.get("head")),
                "english": PASS_B[ord_],
                "notes_covered": [],
                "added_allusions": ALLUSIONS[ord_],
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract.",
                    "Section id = source array order (1-based) to avoid duplicate catena numbers.",
                    "IA PG72 OCR not used as reading text.",
                ],
                "claim": claim,
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{ord_:02d}",
            "section": ord_,
            "edition_fragment": ed_frag,
            "matthew": src["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": claim,
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": src["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a2a3.json",
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
                    "note": "PDFs byte-identical; no textual disagreement.",
                },
                {
                    "witnesses": ["ia-bim-pg72-djvu-ocr"],
                    "note": "IA OCR not used as copy-text; no merge.",
                },
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
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name, claim, "ed_fr", ed_frag)

    (ROOT / "translations/matthew_fragments_greek_clean_a2a3.json").write_text(
        json.dumps(
            {
                "meta": {"claims": ["cyril-matt-frag-a2", "cyril-matt-frag-a3"], "sections": "5-12"},
                "sections": clean_sections,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    english.sort(key=lambda e: e["section"])
    eng_path.write_text(json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", [e["section"] for e in english])


if __name__ == "__main__":
    main()
