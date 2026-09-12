#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a5 (17–20), a6 (21–24), a7 (25–28)."""
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
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


CLEAN = {n: clean_join(BY_ORD[n]["greek"][0]) for n in range(17, 29)}
CLAIMS = {n: f"cyril-matt-frag-a{5 if n <= 20 else 6 if n <= 24 else 7}" for n in range(17, 29)}

PASS_A = {
    17: (
        "The of John baptism was not giving forgiveness of sins, but was teaching the humans "
        "to run toward the baptism because of the sins."
    ),
    18: (
        "As more law-learned than the others later they came toward John whom he calls offspring "
        "of vipers because of the like-manner; for just as those, when about to go out into light, "
        "burst the of the mother belly and dead her leaving go away, the same way also these "
        "dead as it were being their own mother, the Jerusalem, they left and were being saved "
        "out of the Christ-killing, through which they endured the incurable evils for a while "
        "under Romans, which he calls coming wrath."
    ),
    19: (
        "And someone might say fruits of repentance to be chiefly the into Christ faith, and "
        "beside this also the evangelical way-of-life the 'in newness' being 'of life' and "
        "having been freed of the of the letter thickness. Do not therefore, he says, put "
        "forward the customary excuses that God is able out of these stones to raise children "
        "of Abraham — he added."
    ),
    20: (
        "For just as the wife of Lot he turned-to-stone, so possible for him also out of stones "
        "humans to make, just as also the Adam out of earth earlier."
    ),
    21: (
        "Axe he says the Christ the 'sharper than two-mouthed sword' the about-to cut-out the "
        "unbelieving Jews and alienate from the of the patriarchs honor and fellowship, whom "
        "also root he said, who also remained the of old to-God pleasing fathers those about "
        "Abraham and as many as formerly holy; for the out of them unbelievers were cut out as "
        "fruitless branches, but the root remained, upon which the out of nations were grafted. "
        "And Irenaeus axe says the word of God just as also Jeremiah: the word of the Lord "
        "'as an axe cutting rock'. For why do I say, he says, that you are about to fall away — "
        "for this reason indeed it had not even stood away from the root."
    ),
    22: (
        "And to an axe he likens the word of God; for Jeremiah also thus says: the word of the "
        "Lord 'as an axe cutting rock'. Thus upon the root it lies, in order that by the fear "
        "it may make you better and prepare fruit to bring."
    ),
    23: (
        "What does he call axe? Nothing other than the about-to cut from the patriarchs those "
        "vainly boasting and nothing any good having worked; for it is necessary the from such "
        "having become fruitless both to cut out and into fire to throw."
    ),
    24: (
        "And the blessed Baptist bound together with the of the spirit signification the of "
        "the fire energy and signification, not in fire altogether to-be-baptized saying us "
        "through Christ, but the of the spirit life-giving energy through the of the fire "
        "signification signifying."
    ),
    25: (
        "The righteous he snatches into the above city, but the sinners into the to-be-burned."
    ),
    26: (
        "The on-the-one-hand ancients and before the Christ those by them being baptized they "
        "were holding in the water until they their own confessed sins, but the Christ "
        "sinless being immediately went up; for not as repenting was he baptized, but as "
        "cleansing sins and sanctifying the waters."
    ),
    27: ("By the devil he was being led according to permission."),
    28: (
        "The Christ did not obey the devil so as to make the stones breads, because not toward "
        "benefit of him it was; for not in order that he believe and become as formerly he was "
        "angel this he was asking; for unrepentant, but in order that into vain-glory he drag "
        "the Christ. Which knowing the savior did not obey him."
    ),
}

PASS_B = {
    17: [
        (
            "John’s baptism did not give forgiveness of sins. It taught people to run to baptism "
            "because of their sins."
        ),
    ],
    18: [
        (
            "As men more learned in the law than the rest, they came to John later. He calls them "
            "offspring of vipers because of their likeness: when vipers are about to come into "
            "the light, they burst their mother’s belly and leave her dead."
        ),
        (
            "In the same way these men left their own mother, Jerusalem, as if she were dead, and "
            "were being saved from the killing of Christ — the crime for which they endured "
            "incurable evils for a time under the Romans, which he calls the coming wrath."
        ),
    ],
    19: [
        (
            "Someone might say the fruits of repentance are chiefly faith in Christ, and with it "
            "the gospel way of life that is “in newness of life,” freed from the thickness of the "
            "letter."
        ),
        (
            "So do not, he says, put forward the usual excuses — that God can raise children for "
            "Abraham from these stones. That is what he added."
        ),
    ],
    20: [
        (
            "Just as he turned Lot’s wife to stone, so he can also make humans from stones, as he "
            "earlier made Adam from earth."
        ),
    ],
    21: [
        (
            "By “axe” he means Christ, “sharper than any two-edged sword,” who is about to cut "
            "away the unbelieving Jews and estrange them from the patriarchs’ honor and "
            "fellowship. He also called those patriarchs the root — the fathers of old who "
            "pleased God, those around Abraham, and as many as were holy before."
        ),
        (
            "Their unbelieving descendants were cut off as fruitless branches, but the root "
            "remained, and onto it those from the nations were grafted. Irenaeus says the axe is "
            "the word of God, as Jeremiah also does: the word of the Lord is “like an axe "
            "cutting rock.” Why do I say you are about to fall away? For this very reason it had "
            "not even stood clear of the root."
        ),
    ],
    22: [
        (
            "He likens the word of God to an axe. Jeremiah says the same: the word of the Lord is "
            "“like an axe cutting rock.” So it lies against the root, that by fear it may make "
            "you better and prepare you to bear fruit."
        ),
    ],
    23: [
        (
            "What does he mean by axe? Nothing but what is about to cut from the patriarchs those "
            "who boast in vain and have done no good. Those who come from such lines and prove "
            "fruitless must be cut out and thrown into the fire."
        ),
    ],
    24: [
        (
            "The blessed Baptist joins the Spirit’s meaning with fire’s energy and meaning. He is "
            "not saying we will be baptized in fire itself through Christ, but marking the "
            "Spirit’s life-giving energy by the figure of fire."
        ),
    ],
    25: [
        (
            "He snatches the righteous into the city above, and the sinners into what is to be "
            "burned."
        ),
    ],
    26: [
        (
            "The ancients before Christ used to hold those they baptized in the water until they "
            "confessed their own sins. Christ, being sinless, came up at once. He was not baptized "
            "as one repenting, but as one who cleanses sins and sanctifies the waters."
        ),
    ],
    27: [("He was led by the devil by permission.")],
    28: [
        (
            "Christ did not obey the devil so as to turn the stones into loaves, because that "
            "request was not for the devil’s benefit. He was not asking so that he might believe "
            "and become again the angel he once was — for he is unrepentant — but so that he "
            "might drag Christ into vain glory. Knowing this, the Savior did not obey him."
        ),
    ],
}

LEMMAS = {
    17: [
        {"form": "ἄφεσιν ἁμαρτιῶν", "lemma": "ἄφεσις", "gloss": "forgiveness of sins", "lexica": "NT"},
        {"form": "προστρέχειν", "lemma": "προστρέχω", "gloss": "run toward", "lexica": "LSJ"},
    ],
    18: [
        {"form": "γεννήματα ἐχιδνῶν", "lemma": "ἔχιδνα", "gloss": "offspring of vipers", "lexica": "Mt 3:7"},
        {"form": "χριστοκτονίας", "lemma": "χριστοκτονία", "gloss": "Christ-killing", "lexica": "patristic"},
        {"form": "μέλλουσαν ὀργήν", "lemma": "ὀργή", "gloss": "coming wrath", "lexica": "Mt 3:7"},
    ],
    19: [
        {"form": "καρποὺς μετανοίας", "lemma": "καρπός / μετάνοια", "gloss": "fruits of repentance", "lexica": "Mt 3:8"},
        {"form": "ἐν καινότητι ζωῆς", "lemma": "καινότης", "gloss": "newness of life", "lexica": "Rom 6:4"},
    ],
    20: [
        {"form": "ἀπελίθωσεν", "lemma": "ἀπολιθόω", "gloss": "turn to stone", "lexica": "LSJ"},
        {"form": "ἐκ λίθων", "lemma": "λίθος", "gloss": "from stones", "lexica": "Mt 3:9"},
    ],
    21: [
        {"form": "ἀξίνην", "lemma": "ἀξίνη", "gloss": "axe", "lexica": "Mt 3:10"},
        {"form": "ἐνεκεντρίσθησαν", "lemma": "ἐγκεντρίζω", "gloss": "were grafted in", "lexica": "Rom 11"},
        {"form": "πέλυξ", "lemma": "πέλεκυς", "gloss": "axe / hatchet", "lexica": "Jeremiah citation"},
    ],
    22: [
        {"form": "παρεικάζει", "lemma": "παρεικάζω", "gloss": "likens", "lexica": "LSJ"},
        {"form": "τῇ ῥίζῃ ἐπίκειται", "lemma": "ἐπίκειμαι", "gloss": "lies against the root", "lexica": "LSJ"},
    ],
    23: [
        {"form": "καυχησαμένους", "lemma": "καυχάομαι", "gloss": "those who boasted", "lexica": "LSJ"},
        {"form": "ἀκάρπους", "lemma": "ἄκαρπος", "gloss": "fruitless", "lexica": "NT"},
    ],
    24: [
        {"form": "συνέδησε", "lemma": "συνδέω", "gloss": "bound together", "lexica": "LSJ"},
        {"form": "ζωοποιόν", "lemma": "ζωοποιός", "gloss": "life-giving", "lexica": "patristic"},
    ],
    25: [
        {"form": "ἁρπάζει", "lemma": "ἁρπάζω", "gloss": "snatches", "lexica": "LSJ"},
        {"form": "ἄνω πόλιν", "lemma": "πόλις", "gloss": "city above", "lexica": "patristic"},
    ],
    26: [
        {"form": "ἐξωμολογήσαντο", "lemma": "ἐξομολογέομαι", "gloss": "confessed", "lexica": "LSJ"},
        {"form": "ἀναμάρτητος", "lemma": "ἀναμάρτητος", "gloss": "sinless", "lexica": "patristic"},
    ],
    27: [
        {"form": "κατὰ συγχώρησιν", "lemma": "συγχώρησις", "gloss": "by permission / concession", "lexica": "patristic"},
    ],
    28: [
        {"form": "κενοδοξίαν", "lemma": "κενοδοξία", "gloss": "vain glory", "lexica": "LSJ"},
        {"form": "ἀμετανόητος", "lemma": "ἀμετανόητος", "gloss": "unrepentant", "lexica": "NT"},
    ],
}

CHOICES = {
    17: [{"term": "οὐ παρεῖχε ἄφεσιν", "english": "did not give forgiveness", "rejected": ["was not offering pardon (softer)"], "why": "Hard denial of remission in John’s baptism."}],
    18: [{"term": "χριστοκτονίας", "english": "killing of Christ", "rejected": ["deicide (Latinizing)"], "why": "Keep Cyril’s compound concrete."}],
    19: [{"term": "παχύτητος", "english": "thickness (of the letter)", "rejected": ["crudeness"], "why": "Letter vs Spirit density image."}],
    20: [{"term": "ἀπελίθωσεν", "english": "turned to stone", "rejected": ["petrified (modern)"], "why": "Matches Lot’s wife typology plainly."}],
    21: [{"term": "ἐνεκεντρίσθησαν", "english": "were grafted in", "rejected": ["were inserted"], "why": "Romans 11 technical verb."}],
    22: [{"term": "ἐπίκειται", "english": "lies against / upon", "rejected": ["threatens only"], "why": "Axe set to the root, not mere mood."}],
    23: [{"term": "μάτην καυχησαμένους", "english": "who boast in vain", "rejected": ["who brag emptily"], "why": "Patriarchal boast without fruit."}],
    24: [{"term": "σημασίᾳ", "english": "signification / figure", "rejected": ["symbol only"], "why": "Fire figures Spirit’s energy, not literal fire-baptism."}],
    25: [{"term": "ἄνω πόλιν", "english": "city above", "rejected": ["upper city (municipal)"], "why": "Heavenly city, not topography."}],
    26: [{"term": "ἀναμάρτητος", "english": "sinless", "rejected": ["innocent"], "why": "Christological claim for rising at once."}],
    27: [{"term": "κατὰ συγχώρησιν", "english": "by permission", "rejected": ["by agreement"], "why": "Divine permission, not devil’s deal."}],
    28: [{"term": "κενοδοξίαν", "english": "vain glory", "rejected": ["pride (generic)"], "why": "Exact bait Cyril names."}],
}

ALLUSIONS = {
    17: [{"reference": "Matthew 3:6", "reason": "Baptism in the Jordan lemma.", "certainty": "clear"}],
    18: [
        {"reference": "Matthew 3:7", "reason": "Brood of vipers / coming wrath.", "certainty": "clear"},
    ],
    19: [
        {"reference": "Matthew 3:8-9", "reason": "Fruits of repentance; stones / Abraham.", "certainty": "clear"},
        {"reference": "Romans 6:4", "reason": "Newness of life.", "certainty": "clear"},
    ],
    20: [
        {"reference": "Matthew 3:9", "reason": "Children from stones.", "certainty": "clear"},
        {"reference": "Genesis 19:26", "reason": "Lot’s wife.", "certainty": "clear"},
        {"reference": "Genesis 2:7", "reason": "Adam from earth.", "certainty": "clear"},
    ],
    21: [
        {"reference": "Matthew 3:10", "reason": "Axe at the root.", "certainty": "clear"},
        {"reference": "Hebrews 4:12", "reason": "Sharper than two-edged sword.", "certainty": "possible"},
        {"reference": "Romans 11:17-24", "reason": "Grafting of the nations.", "certainty": "clear"},
        {"reference": "Jeremiah 23:29", "reason": "Word like an axe/hammer on rock (via Irenaeus).", "certainty": "possible"},
    ],
    22: [
        {"reference": "Matthew 3:10", "reason": "Axe / root.", "certainty": "clear"},
        {"reference": "Jeremiah 23:29", "reason": "Word as axe cutting rock.", "certainty": "possible"},
    ],
    23: [{"reference": "Matthew 3:10", "reason": "Cut down and thrown into fire.", "certainty": "clear"}],
    24: [{"reference": "Matthew 3:11", "reason": "Baptize with Spirit and fire.", "certainty": "clear"}],
    25: [{"reference": "Matthew 3:12", "reason": "Wheat to barn; chaff burned.", "certainty": "clear"}],
    26: [{"reference": "Matthew 3:16", "reason": "Jesus comes up from the water.", "certainty": "clear"}],
    27: [{"reference": "Matthew 4:1", "reason": "Led into the wilderness by the Spirit / devil temptation frame.", "certainty": "clear"}],
    28: [{"reference": "Matthew 4:3", "reason": "Stones to bread temptation.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    clean_sections = []
    for ord_ in range(17, 29):
        src = BY_ORD[ord_]
        a = PASS_A[ord_]
        b = " ".join(PASS_B[ord_])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {ord_}")
        claim = CLAIMS[ord_]
        ed = src["fragment"]
        clean_sections.append(
            {
                "section": ord_,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "locus": src["locus"],
                "head": src["head"],
                "greek": [CLEAN[ord_]],
                "claim": claim,
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "whitespace + stray digits; no IA merge",
            }
        )
        english.append(
            {
                "section": ord_,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "title": reader_title(src.get("matthew")),
                "scholar_label": scholar_label(fragment=src.get("fragment"), matthew=src.get("matthew"), existing=src.get("head")),
                "english": PASS_B[ord_],
                "notes_covered": [],
                "added_allusions": ALLUSIONS[ord_],
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract.",
                    "Section id = source array order (1-based).",
                    "IA OCR not reading text.",
                ],
                "claim": claim,
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{ord_:02d}",
            "section": ord_,
            "edition_fragment": ed,
            "matthew": src["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": claim,
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": src["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a5a7.json",
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
        print("wrote", out.name, claim, "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a5a7.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": ["cyril-matt-frag-a5", "cyril-matt-frag-a6", "cyril-matt-frag-a7"],
                    "sections": "17-28",
                },
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
    print("english", [e["section"] for e in english])


if __name__ == "__main__":
    main()
