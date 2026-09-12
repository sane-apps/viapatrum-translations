#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a72..a73 (entries 285–290). Reader titles: On Matthew only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    t = re.sub(r"^(\d{1,2})\s+", "", t)
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def reader_title(matthew: str) -> str:
    """Reader H1/TOC: plain English + Mt ch/v. No CPG/fr."""
    m = (matthew or "").strip().replace("-", "–")
    return f"On Matthew {m}" if m else "On Matthew"


def claim_for(n: int) -> str:
    if n <= 288:
        return "cyril-matt-frag-a72"
    return "cyril-matt-frag-a73"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(285, 291)}

PASS_A = {
285: "And the crowds but the having-come-to into the spectacle striking of-them the breasts, were-returning, perhaps somewhere of the against Christ impiety freeing themselves through of the of the crucifiers crying-out-against, if also not openly through the of the leaders unholiness. So-great of the being-crucified the power–of the centurion this having-manfully-acted after these in the faith. True was saying the lord, whenever I-may-be-lifted from the earth, all I-will-draw toward myself; behold for in the precious cross being-lifted he-began of the to-net many into knowledge of truth; he-drew at-least the centurion, he-drew but also of the Jews some, who also the breasts were-striking being-pricked somewhere wholly and with the of the mind eyes looking-up toward lord.",
286: "Since the upon the cross through us he-has-endured suffering the lord and of the of-all life exchange the of-himself he-has-given flesh and was in tomb just-as someone helpless among dead free according-to the in psalms being-hymned, ran the women the toward the of the body tending bringing and of spices being full; they-were-thinking for, that he-will-lie with the others together and will-remain dead in tomb. And not-yet you-may-marvel, if women were-ignorant, that God being and life the of the corruption will-dissolve power and will-run-back toward life, where also to the apostles themselves the about of the resurrection of him word seemed to-be nonsense some simply and thing having-been-falsified through the not-even themselves to-know the God-breathed scripture. Therefore they-arrived on-the-one-hand the women upon the tomb, not having-found at-least the body of the Christ of the into him love for-the-sake-of they-see holy angel. And indeed he-has-become to-them evangelist and herald of the resurrection; not for you-may-seek, he-says, the always living according-to nature being life with of the dead; not he-is for here, this-is in death and tomb, but he-was-raised way of the into incorruption running-back not to-himself rather, but to-us having-become; through this for he-let-down himself into emptying and the toward us he-underwent likeness, in-order-that by-grace of God, as says the blessed Paul, on-behalf of every he-may-taste of death and may-become this of the death death and dissolution of curse the having-been-brought-upon to the first-formed once; of-such for hope he-prepared inside to-become the lord saying; amen I-say to-you; the believing into me even-if he-may-die he-will-live; to-know for it-is-necessary as angels to the shepherds in Bethlehem the birth were-evangelizing, and now rational powers proclaim the resurrection. Has-ministered therefore the heaven to the about him proclamations and they-surround the son the of the above spirits armies as of the all master and lord also when he-became flesh, this-is human.",
287: "Has-gained the female race both loosing of reproach and of curse overturning; the for having-said formerly toward them in pains you-will-bear children pause to-them he-has-given having-met them in the garden and having-said rejoice. With exceeding gladness the women to-him–and into good hopes and the having-toiled healing.",
288: "You-see but how some things they-run-past some of the evangelists; the for they-doubted has-been-unfolded clearly beside the John of the doubting being-shown, who was the Thomas; so-that also the to-mention of the in the Judea appearance second having-become how it-had the matter. He-said but, that to-them he-appeared in the Galilee, which alone seems to-me John to-omit as would lying-before to-him the remaining to-say how-often both he-appeared and where, but indeed also how clearly narrating.",
289: "Other says the John visions, <which> but says here the Matthew not only [which] saw the eleven, but also the many as likely.",
290: "Economically still and more-humanly he-said the was-given to-me; yet he-wants to-be-understood, that the against of all he-has authority as God and having-left the of the emptying measure into the innate and always being-present to-him glory he-ran-back and with flesh God of the all and lord being-confessed. Remaining therefore he-says was-given to-me not as first having-received, when he-became human, but what he-was-having always through the to-exist from father and by-nature God as in of-human rank receiving.",
}

PASS_B = {
285: [
    "And the crowds who had come to the spectacle were returning, striking their breasts — freeing themselves, perhaps, from impiety against Christ by crying out against the crucifiers, even if not openly, because of the leaders’ unholiness. So great was the power of the one being crucified — this centurion afterward proving steadfast in the faith. The Lord was speaking truly when he said, “When I am lifted up from the earth, I will draw all to myself.” For look: lifted on the precious cross, he began to net many into knowledge of the truth. He drew the centurion, and he also drew some of the Jews, who were striking their breasts, pricked in mind and looking up toward the Lord with the eyes of understanding."
],
286: [
    "Since the Lord endured the suffering on the cross for us and gave his own flesh as the exchange for the life of all, and was in the tomb like one “helpless among the dead, free,” as the psalm sings, the women ran bringing what was needed for the care of the body, full of spices. For they thought he would lie with the others and remain dead in the tomb. And do not marvel if women did not know that, being God and life, he would dissolve corruption’s power and run back to life — when even to the apostles themselves the word about his resurrection seemed mere nonsense and a fabricated thing, because they too did not know the God-breathed Scripture.",
    "So the women came to the tomb; and though they did not find Christ’s body, for love of him they see a holy angel. He became for them an evangelist and herald of the resurrection: “Do not seek,” he says, “the one who is always living, who is life by nature, among the dead; for he is not here” — that is, in death and the tomb — “but he has been raised,” becoming for us rather than for himself the way of the run back into incorruption. For that is why he let himself down into emptying and underwent likeness toward us: so that “by the grace of God,” as blessed Paul says, “he might taste death for everyone,” and this might become death’s death and the dissolution of the curse once brought upon the first-formed. For the Lord prepared us to enter such hope when he said, “Amen, I say to you: the one who believes in me, even if he dies, will live.”",
    "Know that angels evangelized the birth to the shepherds in Bethlehem, and now rational powers proclaim the resurrection. Heaven has therefore ministered to the proclamations about him, and the armies of the spirits above surround the Son as Master and Lord of all — even when he became flesh, that is, a human."
],
287: [
    "The female race has gained both the loosing of reproach and the overturning of the curse. For the one who once said to them, “In pains you will bear children,” gave them a pause when he met them in the garden and said, “Rejoice.” With exceeding gladness the women [came] to him — and he was healing what had suffered, and leading them into good hopes."
],
288: [
    "You see how some of the evangelists run past certain things. For “they doubted” is clearly unfolded in John, where the one who doubted is shown — and he was Thomas. So mentioning the appearance in Judea that happened second also shows how the matter stood. But he said that he appeared to them in Galilee — which alone John seems to me to omit, since it lay before him to say the rest: how often he appeared, and where, and indeed how, narrating clearly."
],
289: [
    "John speaks of other visions; <the one> Matthew speaks of here the eleven saw, and not only they, but also the many, as is likely."
],
290: [
    "Still economically, and in a more human way, he said “it was given to me.” Yet he wants it understood that he has authority over all as God, and that, leaving the measure of the emptying, he ran back into the glory innate and always present to him, and is confessed God and Lord of all even with the flesh. So when he says “it was given to me,” it is not as if he first received it when he became human, but as receiving, in the rank of a human, what he always had because he exists from the Father and is God by nature."
],
}

LEMMAS = {n: [] for n in range(285, 291)}
LEMMAS[289] = [
    {"form": "<ἣν>", "lemma": "ὅς", "gloss": "supplied relative ‘which’", "lexica": "editorial"},
    {"form": "[ἣν]", "lemma": "ὅς", "gloss": "bracketed relative in extract", "lexica": "editorial"},
]

CHOICES = {n: [] for n in range(285, 291)}
CHOICES[286] = [{"term": "stray digit 44", "english": "drop OCR/page digit from clean Greek", "rejected": ["keep ‘44’ in reading text"], "why": "Stray numeral amid Greek; disclose cleanup."}]
CHOICES[287] = [{"term": "mid-phrase break", "english": "translate broken ending; mark lacuna sense", "rejected": ["invent missing clause"], "why": "Extract ends mid-thought after αὐτῷ–; disclose."}]
CHOICES[289] = [{"term": "<ἣν> / [ἣν]", "english": "disclose editor supply/brackets", "rejected": ["silent omit"], "why": "Angle/square brackets mark editorial text."}]

ALLUSIONS = {
285: [
    {"reference": "Matthew 27:54", "reason": "Centurion and those watching; truly God’s Son.", "certainty": "clear"},
    {"reference": "John 12:32", "reason": "When I am lifted up, I will draw all.", "certainty": "clear"},
    {"reference": "Luke 23:48", "reason": "Crowds return beating their breasts.", "certainty": "clear"},
],
286: [
    {"reference": "Matthew 28:1-7", "reason": "Women at the tomb; angel’s resurrection message.", "certainty": "clear"},
    {"reference": "Psalm 88:5", "reason": "Helpless among the dead / free among the dead.", "certainty": "possible"},
    {"reference": "Hebrews 2:9", "reason": "By God’s grace he tasted death for everyone.", "certainty": "clear"},
    {"reference": "John 11:25", "reason": "Believer lives even if he dies.", "certainty": "clear"},
    {"reference": "Luke 2:8-14", "reason": "Angels evangelize the birth to shepherds.", "certainty": "clear"},
],
287: [
    {"reference": "Matthew 28:9-10", "reason": "Jesus meets the women; rejoice / greetings.", "certainty": "clear"},
    {"reference": "Genesis 3:16", "reason": "In pains you will bear children.", "certainty": "clear"},
],
288: [
    {"reference": "Matthew 28:16-17", "reason": "Galilee; some doubted.", "certainty": "clear"},
    {"reference": "John 20:24-29", "reason": "Thomas the doubter shown in John.", "certainty": "clear"},
],
289: [{"reference": "Matthew 28:17", "reason": "They saw him; some doubted / the eleven.", "certainty": "clear"}],
290: [{"reference": "Matthew 28:18", "reason": "All authority has been given to me.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(285, 291):
        src = BY[n]
        a, b = PASS_A[n], " ".join(PASS_B[n])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {n}")
        claim = claim_for(n)
        ed = src["fragment"]
        notes = [
            "Copy-text khazarzar Aegean PG 72 extract.",
            f"CPG 5206 fr.{ed} (apparatus/meta only; not reader title).",
            "Section id = source array order (1-based).",
            "IA OCR not reading text.",
        ]
        if n == 286:
            notes.append("Stray digit in extract cleaned from reading Greek; disclosed.")
        if n == 287:
            notes.append("Source breaks mid-phrase after the women toward him; ending not invented.")
        if n == 289:
            notes.append("Editor-supplied <ἣν> and bracketed [ἣν] disclosed.")
        cleans.append(
            {
                "section": n,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "locus": src["locus"],
                "head": src["head"],
                "greek": [CLEAN[n]],
                "claim": claim,
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "whitespace + stray digits; no IA merge",
            }
        )
        english.append(
            {
                "section": n,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "title": reader_title(src["matthew"]),
                "english": PASS_B[n],
                "notes_covered": [],
                "added_allusions": ALLUSIONS[n],
                "translator_notes": notes,
                "claim": claim,
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{n:02d}",
            "section": n,
            "edition_fragment": ed,
            "matthew": src["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": claim,
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": src["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a72a73.json",
            },
            "source_text": CLEAN[n],
            "pass_a_gloss": PASS_A[n],
            "pass_b_english": PASS_B[n],
            "lemmas": LEMMAS[n],
            "choices": CHOICES[n],
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
        out = ROOT / f"reviews/justifications/matt_frag_{n}.json"
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name, claim, reader_title(src["matthew"]), "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a72a73.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": ["cyril-matt-frag-a72", "cyril-matt-frag-a73"],
                    "sections": "285-290",
                },
                "sections": cleans,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    english.sort(key=lambda e: e["section"])
    eng_path.write_text(json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english updated through", max(CLEAN), "count", len(english))


if __name__ == "__main__":
    main()
