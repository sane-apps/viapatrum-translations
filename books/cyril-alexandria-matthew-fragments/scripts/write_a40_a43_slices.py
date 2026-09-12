#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a40..a43 (entries 157–172)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def claim_for(n: int) -> str:
    if n <= 160:
        return "cyril-matt-frag-a40"
    if n <= 164:
        return "cyril-matt-frag-a41"
    if n <= 168:
        return "cyril-matt-frag-a42"
    return "cyril-matt-frag-a43"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(157, 173)}

PASS_A = {
157: "Having-said take-courage the faith he-demands, through which each of those sincerely into Christ believing is-saved; but having-added I am he-looses every fear; for I, he-says, am the all being-able to-do.",
158: "Were-approaching some of the Jews and to-consecrate they-were-eager to the God the of themselves souls, as in type on-the-one-hand still and shadow yet according to the law the from beside themselves confessing honors to those to-serve-as-priests having-obtained and to the divine attending altar, but there-were some longing on-the-one-hand of the such glory, of the to-have-been-sanctified I-mean and holy and divine offering, but by-lack of money cutting-short the desire. But of urging them upon the to-be-necessary to-be toward this of the Pharisees and scribes — for money-loving these exceedingly — the toward parents reverence they-were-putting-forward and speaking-truth they-were-saying, scarcely to-be-able for themselves and for those the life-sustaining to-provide. But they to-persuade they-were-daring as nothing to-regard the matter through the God, and-if may-approach those having-begotten the customary from them seeking aid, it-is-necessary to-say they-were-teaching to the father or to the mother, that gift it-is, what ever from me you-may-be-benefited, this-is what ever from me you-may-take, know the divine harming offering and to sacred moneys the hands laying-on; for I-have-dedicated myself and as gift I-have-promised to the God. But the parents the from the temple-robbery fearing harm and the upon this laws having-shuddered they-were-enduring wailing and the toward God piety pretext to them to-have-become of famine they-were-maintaining having-cried-out perhaps somewhere also of the divine command wronging them into the most-vital. Through what therefore, he-says, you-made-void the command of the God through the tradition of you? For it-was-necessary, it-was-necessary to-honor the having-begotten, not of the toward God piety for-the-sake-of the upon them to-destroy law. Therefore neither of the to the God befitting must-one-neglect through the human things nor indeed wholly of the humans through the God must-one-neglect, apportioning but rather the of the love exceptional to the of all beginning, this-is to God, just-as in order second and neighboring to-convey straightway also into the of the birth helpers the to them that most befitting honors.",
159: "Of the God commanding to-honor the parents and danger having-hung to those transgressing you command to the children not to-honor the parents, unless-perhaps the children from ambition this they-may-wish to-do, but if you they-may-ask something, to-say toward them, what ever from me you-may-take, know this depriving of the God; for into sacrifice for it I-promised to-give. And it-is-necessary on-the-one-hand the God to-be-preferred of the parents, it-is-necessary but <I-say> also the toward parents honor to-be-kept to-require; for not through the to-seem to-pretext gift-bringing to God they-ought to-err into the of themselves parents.",
160: "Planting is the not from God every the outside God, which also will-be-uprooted; the to this having-been-made-like blind is.",
161: "Also them senseless the Lord says about the body being-turned, just-as the Pharisees, and not-yet passing-over upon the inner human. Foods therefore, he-says, of body has filling, but of heart not it-touches. But the of heart not touching not is-able to-make-common the human the true or not clean to-render.",
162: "But having-said let-it-become to you as you-wish royally he-spoke not through prayer the matter having-accomplished, but through the God-befitting to him authority.",
163: "Having-been-said of the word the work not delays; for God the saying and the word working and the power everywhere.",
164: "Not-yet the of the Lord they-have-learned dignity, that God he-is, but human they-were-thinking him bare; wherefore also to the God of Israel the glory they-were-sending-up.",
165: "From many but the Christ shows, that God he-is; nothing less also from the to-feed in desert the crowd this he-presents as-if somehow also unwilling through the necessity and the of the food hard-to-procure doing the of the breads sign, which not he-would-have-done in city, where of the marketables the abundance; yet being-able by-word to-strengthen them through the invisible this not he-does; but the of the breads as clearly showing the of him God-befitting glory he-did. Not he-said the Peter: you are Christ or son of the God, but the Christ the son of the God; for many on-the-one-hand christs according to grace and of adoption dignity having, but alone one the by-nature son of the God. Wherefore with the article he-said the Christ the son of the God. But having-said him son of the God the living he-shows, that himself life he-was and death of him not lords. For even-if toward a-little the flesh weakened having-died, but it-rose not being-able of the in it word under bonds of death to-be-held.",
166: "Just-as those by the addition of the matter the being-burned upon the greater raising the flame, thus also those to-destroy the of the Christ church having-hastened through the persecution it into greater of glory they-led-forward and of power. But if of the church, he-says, not they-prevail — then also another he-says honor.",
167: "Observe, how Lord himself he-shows summarily of heaven and of earth; for he-promises the beyond the nature the according to us, rather also of order of the angelic and as-many-as to alone it-befits to-grant to the highest of all nature and glory; for first on-the-one-hand he-says of himself to-be the church although of the sacred writings to God rather and to none of the others dedicating 'not having spot or wrinkle', which indeed also to-found he-promises the unshakeable to it assigning as himself being of the powers Lord and of this shepherd the Peter he-sets-over. Then he-said: and I-will-give to you the keys of the kingdom of the heavens. But this the voice not angel, not other some rational power to-utter is-able, it-befits but rather to the of all ruling God and authority having of earth and of heaven.",
168: "The of the gift time into the of resurrection looking according to which he-said: 'take spirit holy; if of some you-may-forgive the sins, they-have-been-forgiven; if of some you-may-retain, they-have-been-retained'. But the gift of the faith the having-been-given to all fits; wherefore common of all we-understand of the apostles the faith and not of alone of the Peter.",
169: "That Jesus Christ he-is, is-shown through this; for he-says the of the economy about-to which it-was-necessary to-be-proclaimed completely after this to-be *** in-order-that Christ having-been-crucified by those to-witness being-able *** since but not it-was-receiving 'prophet <to-perish> outside Jerusalem' destruction analogy having toward the 'having-lost the soul of him, he-will-find it', through this into Jerusalem he-departs.",
170: "Since not-yet the 'from height power' having-had the disciples likely it-was perhaps somewhere also to human to-fall weaknesses and something such having-thought to-say: how will-deny someone himself? Or how having-lost the of himself soul he-will-find it? But what to those this having-suffered the equal-honoring prize? Through this, in-order-that of such them he-may-stand-away reasonings and as-if he-may-reforge toward manliness of the about-to-be to them fair-fame desire having-instilled, he-says: there-are some of those here having-stood and the following, Peter hinting and the sons of Zebedee; for these in the transfiguration were-taken-along, which he-calls kingdom as having-shown of the authority the ineffable and of the toward the father genuineness the unvarying; but in it also of the second coming the dignity and the frightful he-indicated prelude this of that and as-if confirmation having-shown. For he-will-come in glory of the God and Father, not in smallness the according to us.",
171: "Glory he-says the transformation and change of the our nature beside the now being-seen form into glorious and incomparable glory; but of whom also glory one, by-much more also substance. But glory otherwise the transformation and remodeling of the our nature the glorious and incomparable having the glory beside the now being-seen form.",
172: "Into the mountain he-goes-up showing, that the lowly mind not would become toward contemplation suitable, but the according to own having-become and outside of cares of life in quiet.",
}

PASS_B = {
157: [
    "Having said “Take courage,” he requires the faith through which each of those who believe sincerely in Christ is saved. And by adding “I am,” he dissolves every fear; for “I,” he says, “am the one who can do all things.”"
],
158: [
    "Some of the Jews were coming forward and were eager to consecrate their own souls to God — still in type and shadow, yet according to the law — confessing as their own the honors owed to those allotted to priestly service and attending the divine altar. But some longed for that sort of glory (I mean being sanctified, holy, and a divine offering) while lack of money cut short the desire.",
    "When Pharisees and scribes urged them that they must pursue this — for those men are exceedingly fond of money — the people put forward reverence toward parents and, speaking truthfully, said they could scarcely provide the means of life for themselves and for their parents. The Pharisees dared to persuade them to count the matter as nothing for God’s sake: even if those who begot them approached seeking the customary help from them, they taught that one must say to father or mother, “It is a gift — whatever you would be helped with from me,” that is, “Whatever you would take from me, know that you are harming the divine offering and laying hands on sacred funds; for I have dedicated myself and promised myself to God as a gift.”",
    "But the parents, fearing the harm that comes from temple-robbery and shuddering at the laws about it, kept enduring while they wailed, and insisted that piety toward God had become a pretext of famine for them — crying out, perhaps, that the divine command itself was wronging them in what mattered most. “Why then,” he says, “did you make void the command of God through your tradition?” For it was necessary — necessary — to honor those who begot them, not to destroy the law concerning them for the sake of piety toward God. Therefore one must neither neglect what befits God because of human affairs, nor wholly neglect humans because of God; rather, assigning love’s exceptional share to the beginning of all — that is, to God — one should next, as in a second and neighboring rank, also convey to the helpers of one’s birth the honors most fitting to them."
],
159: [
    "Though God commands that parents be honored and has hung danger over those who transgress, you command the children not to honor their parents — unless perhaps the children should wish to do this from ambition — but if they ask you for something, to say to them: “Whatever you take from me, know that you are stripping this from God; for I promised to give it as a sacrifice.” God must indeed be preferred to parents; yet <I say> one must also require that honor toward parents be kept. For they ought not, by seeming to pretext gift-bringing to God, to wrong their own parents."
],
160: [
    "Every planting that is not from God — everything outside God — will also be uprooted. The one conformed to that planting is blind."
],
161: [
    "The Lord also calls them senseless for turning about the body, like the Pharisees, and not yet crossing over to the inner human. Foods, then, he says, fill the body; they do not touch the heart. And what does not touch the heart cannot make the true human common or render him unclean."
],
162: [
    "When he said, “Let it be for you as you wish,” he spoke royally — not accomplishing the matter through prayer, but through the authority that befits God in him."
],
163: [
    "Once the word is spoken, the deed does not delay. For God is the one speaking, the word is at work, and the power is everywhere."
],
164: [
    "They had not yet learned the Lord’s dignity — that he is God — but were thinking him a mere human. That is why they were also sending up the glory to the God of Israel."
],
165: [
    "From many things Christ shows that he is God. Not least, he also presents this by feeding the crowd in the desert — doing the sign of the loaves, as if somehow unwillingly, because of necessity and how hard food was to get — which he would not have done in a city, where market goods are abundant. Yet though he could have strengthened them by a word through what is unseen, he does not do that; he did the sign of the loaves as clearly showing his God-befitting glory.",
    "Peter did not say, “You are Christ,” or “a son of God,” but “the Christ, the Son of God.” For there are many christs by grace and who hold the dignity of adoption, but only one is Son of God by nature. That is why, with the article, he said “the Christ, the Son of God.” And by calling him Son of the living God he shows that he himself was life, and death does not lord it over him. For even if for a little the flesh weakened in dying, it rose, since the Word in it could not be held under death’s bonds."
],
166: [
    "Just as those who, by adding fuel to what is already burning, raise the flame higher, so also those who hastened to destroy Christ’s church, through the persecution, led it forward into greater glory and power. And if, he says, they do not prevail over the church — then he also names another honor."
],
167: [
    "See how he shows himself Lord of heaven and earth in summary. For he promises what is beyond our nature — rather, even beyond the angelic order — and whatever it befits to grant only to the nature and glory highest of all. First he says the church is his own, although the sacred writings dedicate it rather to God and to none of the others — “having no spot or wrinkle” — and he also promises to found it, assigning it what cannot be shaken, as himself Lord of the powers, and he sets Peter over it as shepherd.",
    "Then he said, “And I will give you the keys of the kingdom of the heavens.” This voice no angel, nor any other rational power, can utter; it befits rather the God who rules all and has authority over earth and heaven."
],
168: [
    "The time of the gift looks to the resurrection, when he said, “Receive the Holy Spirit; if you forgive the sins of any, they have been forgiven; if you retain those of any, they have been retained.” But the gift of the faith given fits all; that is why we understand the faith as common to all the apostles, and not Peter’s alone."
],
169: [
    "That he is Jesus Christ is shown through this. For he says the things of the economy that were about to be — which had to be proclaimed completely after this — *** so that Christ crucified, by those able to bear witness *** But since it was not accepted that a “prophet <perish> outside Jerusalem” — a destruction that has an analogy to “the one who has lost his soul will find it” — for that reason he goes away into Jerusalem."
],
170: [
    "Since the disciples did not yet have “power from on high,” it was likely they might somehow also fall into human weaknesses and, having thought something of the sort, say: How will someone deny himself? Or how, having lost his own soul, will he find it? And what equal-honoring prize is there for those who have suffered this?",
    "Therefore, so that he might stand them away from such reasonings and, as it were, reforge them toward courage by instilling desire for the fair fame about to be theirs, he says, “There are some of those standing here,” and what follows — hinting at Peter and the sons of Zebedee. For these were taken along at the transfiguration, which he calls a kingdom as having shown the ineffable of his authority and the unvarying genuineness of his relation to the Father. In it he also indicated the dignity of the second coming and a frightful prelude — showing this as confirmation, as it were, of that. For he will come in the glory of God the Father, not in the smallness that is ours."
],
171: [
    "By “glory” he means the transformation and change of our nature from the form now seen into a glorious and incomparable glory. And of those who also have one glory, much more is the substance one.",
    "Otherwise by “glory” he means the transformation and remodeling of our nature that has the glorious and incomparable glory beside the form now seen."
],
172: [
    "He goes up onto the mountain to show that a lowly mind would not become fit for contemplation, but the one who has become his own, outside life’s cares, in quiet."
],
}

LEMMAS = {
157: [],
158: [{"form": "ἐρασιχρήματοι", "lemma": "ἐρασιχρήματος", "gloss": "money-loving", "lexica": "LSJ"}],
159: [{"form": "<λέγω>", "lemma": "λέγω", "gloss": "I say (supplied)", "lexica": "editorial"}],
160: [],
161: [{"form": "κοινῶσαι", "lemma": "κοινόω", "gloss": "make common / defile", "lexica": "NT"}],
162: [],
163: [],
164: [{"form": "ψιλόν", "lemma": "ψιλός", "gloss": "mere / bare", "lexica": "patristic"}],
165: [],
166: [],
167: [],
168: [],
169: [{"form": "***", "lemma": "lacuna", "gloss": "gaps in copy-text", "lexica": "editorial"}],
170: [],
171: [{"form": "μετασχηματισμόν", "lemma": "μετασχηματισμός", "gloss": "transformation", "lexica": "NT"}],
172: [],
}

CHOICES = {
157: [],
158: [{"term": "δῶρόν ἐστιν / Corban", "english": "It is a gift (Corban vow)", "rejected": ["ordinary present"], "why": "Pharisaic vow voids parental support."}],
159: [{"term": "<λέγω>", "english": "supplied ‘I say’", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}],
160: [],
161: [],
162: [{"term": "βασιλικῶς", "english": "royally / as king", "rejected": ["merely firmly"], "why": "Authority is God-befitting, not prayer-petition."}],
163: [],
164: [],
165: [{"term": "ὁ Χριστὸς ὁ υἱὸς", "english": "the Christ, the Son (with articles)", "rejected": ["a christ / a son"], "why": "Articles mark the unique natural Son vs many by grace."}],
166: [],
167: [],
168: [{"term": "κοινὴν … πίστιν", "english": "faith common to all apostles", "rejected": ["Peter alone"], "why": "Gift timing and scope are shared."}],
169: [{"term": "*** lacunae / <ἀπολέσθαι>", "english": "gaps + supplied ‘to perish’", "rejected": ["invent continuous Greek"], "why": "Copy-text breaks; disclose; invent no Greek."}],
170: [],
171: [],
172: [],
}

ALLUSIONS = {
157: [{"reference": "Matthew 14:27", "reason": "Take courage; I am.", "certainty": "clear"}],
158: [{"reference": "Matthew 15:1-6", "reason": "Corban; tradition vs command.", "certainty": "clear"}],
159: [{"reference": "Matthew 15:4-6", "reason": "Honor parents; gift vow.", "certainty": "clear"}],
160: [{"reference": "Matthew 15:13-14", "reason": "Every plant not planted by Father; blind guides.", "certainty": "clear"}],
161: [{"reference": "Matthew 15:17-18", "reason": "What enters mouth; what comes from heart.", "certainty": "clear"}],
162: [{"reference": "Matthew 15:28", "reason": "Let it be for you as you wish.", "certainty": "clear"}],
163: [{"reference": "Matthew 15:28", "reason": "Word and healing coincide.", "certainty": "clear"}],
164: [{"reference": "Matthew 15:31", "reason": "They glorified the God of Israel.", "certainty": "clear"}],
165: [{"reference": "Matthew 15:34-39", "reason": "Feeding of the four thousand.", "certainty": "clear"}, {"reference": "Matthew 16:16", "reason": "You are the Christ, the Son of the living God.", "certainty": "clear"}],
166: [{"reference": "Matthew 16:18", "reason": "Gates of Hades will not prevail.", "certainty": "clear"}],
167: [{"reference": "Matthew 16:18-19", "reason": "Church; keys of the kingdom.", "certainty": "clear"}, {"reference": "Ephesians 5:27", "reason": "No spot or wrinkle.", "certainty": "clear"}],
168: [{"reference": "Matthew 16:19", "reason": "Bind and loose.", "certainty": "clear"}, {"reference": "John 20:22-23", "reason": "Receive the Holy Spirit; forgive/retain.", "certainty": "clear"}],
169: [{"reference": "Matthew 16:20-21", "reason": "Tell no one; must go to Jerusalem.", "certainty": "clear"}, {"reference": "Luke 13:33", "reason": "Prophet must not perish outside Jerusalem.", "certainty": "clear"}],
170: [{"reference": "Matthew 16:24-28", "reason": "Deny self; some standing here.", "certainty": "clear"}, {"reference": "Luke 24:49", "reason": "Power from on high.", "certainty": "clear"}],
171: [{"reference": "Matthew 16:27-28", "reason": "Come in glory of Father.", "certainty": "clear"}],
172: [{"reference": "Matthew 17:1", "reason": "Up a high mountain.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(157, 173):
        src = BY[n]
        a, b = PASS_A[n], " ".join(PASS_B[n])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {n}")
        claim = claim_for(n)
        ed = src["fragment"]
        notes = [
            "Copy-text khazarzar Aegean PG 72 extract.",
            "Section id = source array order (1-based).",
            "IA OCR not reading text.",
        ]
        if n == 159:
            notes.append("Supplied <λέγω> disclosed.")
        if n == 165:
            notes.append("Source joins feeding sign with Peter’s confession; both kept.")
        if n == 169:
            notes.append("Lacunae (***) and supplied <ἀπολέσθαι> disclosed; invent no Greek.")
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
                "title": src["head"],
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a40a43.json",
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
        out = ROOT / f"reviews/justifications/matt_frag_{n:02d}.json"
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name, claim, "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a40a43.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a40",
                        "cyril-matt-frag-a41",
                        "cyril-matt-frag-a42",
                        "cyril-matt-frag-a43",
                    ],
                    "sections": "157-172",
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
    print("english", [e["section"] for e in english])


if __name__ == "__main__":
    main()
