#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a44..a47 (entries 173–188)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from reader_titles import reader_title, scholar_label

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def claim_for(n: int) -> str:
    if n <= 176:
        return "cyril-matt-frag-a44"
    if n <= 180:
        return "cyril-matt-frag-a45"
    if n <= 184:
        return "cyril-matt-frag-a46"
    return "cyril-matt-frag-a47"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(173, 189)}

PASS_A = {
173: "To-have-been-done but we-say the transfiguration not indeed the form the human having-changed of the body, but of glory some light-like enveloping it; for of remaining of the body upon the form upon the more-glorious the features through light-like color were-being-tinged.",
174: "Through which they-converse-together is-shown, that the same things to the Christ also the of-old prophets uttered, even-if through riddles. But by the extreme cowardice fall the disciples and raises them the savior showing, that if not he-became-incarnate and mediated God and humans and strengthened the of him nature, not would he-have-borne voice of God to-hear.",
175: "Not he-knew what he-was-saying; for before the passion and the resurrection of the savior and the dissolution of the death and the corruption of the bodies of us impossible it-was the Peter to-be-with Christ and of the tents to-desire the in heaven; for these it-is-necessary to-happen after the of the savior resurrection and into heaven ascent.",
176: "Of him he-has-commanded to-hear, since not to legal still to-obey writings us willed to the God and father, but not-even to the in type shadow-drawings, to-follow but rather to the through the savior to us having-been-enjoined not of being-thrust-out of Moses and of the prophets; for they-were-standing-alongside and were-conversing with him, in-order-that on-the-one-hand the presence the servant-like to us may-signify service, but the to-converse-together the into Christ intimacy and as-if the same-speaking.",
177: "The on-the-one-hand of the God and father voice good and admirable, but by unmixed already being-held fear fall the disciples, in-order-that indeed again also through this we-may-learn, that most-necessary to those upon earth the of the savior of us has-appeared mediation being-understood clearly according to the of the incarnation manner; for if not he-became according to us, who of us would-have-borne upward approaching God and the ineffable of him glory to none perhaps of the generated bearable showing; for 'light to-dwell' him 'unapproachable' also the blessed said Paul; and before this was-borne voice upon the Jordan such and crowd was-present.",
178: "Shows the Christ the Jews exceedingly not-knowing the scriptures, from which the John not they-knew, this-is the first Elijah the 'the way having-prepared of the Lord', whom not-knowing and having-killed the of the Christ forerunner also himself they-ignored the Lord and they-killed him.",
179: "If also it-was-necessary the of the demon-possessed father grieving to-depart not having-obtained of the favor, as not blameless having-made the approach, but of the choir of the apostles having-cried-out-against and having-said, not to-have-been-able them to-rebuke the demon, rather but him accusing the of the powers Lord; for the saying to-have-been-weak toward working the against spirits unclean those from Christ authority having-received to-cast-out them, of the grace rather he-accuses, not of those having-received it. Through these therefore the unbelieving that father and through this distorted it-was-necessary empty to-be-sent-away. But in-order-that not someone may-think also him to-have-been-powerless the Christ toward the of the marvel accomplishment, 'he-rebuked the unclean spirit' and immediately of the being-ill the child was-being-freed 'and he-gave him to the father of him'; for before the to-be-healed not he-was of the father, but of the holding spirit.",
180: "If through natural of it law the moon was-able to-produce in-someone passion, through what not to all it-sends this to the humans just-as to all it-sends-in the of itself light? Again that clear, that into shining was-made the moon, not into the to-beget demons. But if from the working the natural of the moon was-made this, it-was-necessary of the demon having-been-crushed also the moon to-be-harmed, the cause of the passion. But not is this, but the demons to-deceive wanting the humans the of the elements to themselves were-putting-around names, in-order-that as wicked the elements may-be-accused, which not is; for by-nature <the> elements good only serving to the having-been-given to them laws and not having the from choice authoritative.",
181: "The unbelieving will-be somewhere also distorted and according to no manner to-walk-straight knowing. But to the such not he-deems-worthy to-be-with Christ, but if it-is-necessary something of the human to-say, he-is-indifferent and is-weary. Yet not into the of this person—also the not befitting to-think about them.",
182: "Whenever but he-may-say, that until when I-dwell-with you the thus insulting and unbelieving he-shows, that the of the incarnate presence time was-demanding him to-dwell-with with God-befitting gentleness the not good, in-order-that them through which he-does he-may-correct. Until when, he-says, I-dwell-with you the thus insolent and unbelieving showing, that the with flesh presence of him compelled him to-associate with the not good, in-order-that he-may-correct them.",
183: "If you-have faith as grain of mustard this-is hot and boiling or the to the small grain having-been-likened through the in word smallness. For 'we-have' 'in earthen vessels the' of the faith 'treasure'.",
184: "Therefore he-brought-up on-the-one-hand into the mountain the chief and he-showed to them the glory, with which he-will-shine-upon the world according to times, then having-come-down from the mountain of wicked and harsh spirit he-freed someone. But it-was-necessary wholly him the saving on-behalf of us to-endure passion and of the of Jews to-bear perversity. Of which indeed having-happened not unreasonable in tumults to-be the disciples and that somewhere perhaps by themselves to-think and to-say: the so-many dead having-raised in authority God-befitting, the also to seas rebuking and to spirits, the by-word crushing the satan, how was-he-caught now and into the of the murderous he-has-fallen snares? Were we-deceived God to-be thinking him? In-order-that therefore they-may-know the wholly and altogether about-to-be, he-foretells to them of the passion the mystery.",
185: "Having-mixed-together the about the resurrection word he-weaves-together with the weakness the power, with the ingloriousness the glory, with the cheapness of the humanity the of the divinity high; for he-died as human, he-lived-again as God. Are-grieved but the disciples through the toward the Christ love although indeed having-been-foreannounced of the resurrection after not much, since more-hotly the humans are-grieved hearing of the grievous and more of these they-perceive than of the sweetest.",
186: "And cunningly they-ask the Peter. Since, he-says, custom he-has to the of Moses to-oppose laws, not-even the didrachma he-pays, knowing that also the Christ was having-said 'not I-came to-destroy the law, but to fulfill', and that of the economy the manner this demands. To these on-the-one-hand therefore said the Peter—perhaps blushing about these to-converse.",
187: "Being-able also from the earth to-bring-forth the stater not he-did this, but from the sea the sign he-made, in-order-that mystery us he-may-teach of contemplation full; for fishes we-were from the bitter of the life turmoils having-been-drawn-up as from sea through the apostolic hooks having in the of ourselves mouths the Christ the stater the royal, who was-given on-behalf of two as-ransom, on-behalf of soul and body of us or on-behalf of two peoples, of Jews and of gentiles, likewise ransoming poor and rich since also the old law unreservedly from equal was-demanding the tax of the drachma from both rich and poor. Was-able the savior also from the earth to-bring-forth the stater, not he-did but this, but from the sea the sign he-worked, in-order-that he-may-show mystery to us of contemplation full; for we are the fishes having-been-caught from the of the life turmoils through the apostolic teachings. We-have but in the mouths of us the stater, this-is the Christ.",
188: "Of heavens both kingdom in both the present especially we-reckon and to-be we-say either the in sanctification calling or the in faith and holiness measure; for he-hints something such also the savior saying: 'the kingdom' of the heavens 'within you is'.",
}

PASS_B = {
173: [
    "We say the transfiguration took place not by the body’s human form being changed, but by a light-like glory wrapping it around. The body remained in its form, while the features were colored more gloriously by a light-like hue."
],
174: [
    "What they speak together shows that the prophets of old uttered the same things as Christ, even if in riddles. The disciples fall from extreme fear, and the Savior raises them, showing that unless he had become flesh, mediated between God and humans, and strengthened our nature, it could not have borne to hear God’s voice."
],
175: [
    "He did not know what he was saying. Before the Savior’s passion and resurrection, and before the dissolution of death and the corruption of our bodies, it was impossible for Peter to dwell with Christ and to long for the tents in heaven. Those things must come after the Savior’s resurrection and ascent into heaven."
],
176: [
    "He has commanded that we hear him, because God the Father no longer wills us to obey legal writings, nor even the shadow-sketches in type, but rather to follow what has been enjoined on us through the Savior — without thrusting out Moses and the prophets. For they were standing beside him and speaking with him, so that their presence might signify servant-like service to us, while their conversing might signify intimacy with Christ and, as it were, speaking the same things."
],
177: [
    "The voice of God the Father is good and worthy of wonder; yet the disciples fall, already held by unmixed fear, so that through this too we may learn how necessary the Savior’s mediation has appeared for those on earth — understood according to the manner of the incarnation. For if he had not become as we are, who of us could have borne God approaching from above and displaying his ineffable glory, scarcely bearable for any generated being? For the blessed Paul also said that he “dwells in unapproachable light.” And before this such a voice was borne at the Jordan, and a crowd was present."
],
178: [
    "Christ shows that the Jews are greatly ignorant of the scriptures, from which they did not recognize John — that is, the first Elijah, “who prepared the way of the Lord.” Not knowing him and killing the forerunner of Christ, they also failed to recognize the Lord himself and killed him."
],
179: [
    "Even if the father of the demon-possessed boy, grieving, ought to have gone away without obtaining the favor — because he did not make a blameless approach, but cried out against the apostolic band and said they could not rebuke the demon, rather accusing the Lord of the powers himself (for the one who says those who received authority from Christ to cast out unclean spirits were weak for the work rather accuses the grace, not those who received it) — therefore that unbelieving and so distorted father ought to have been sent away empty.",
    "Yet so that no one might think Christ himself powerless to accomplish the marvel, “he rebuked the unclean spirit,” and at once the child was freed from illness, “and he gave him to his father.” For before he was healed he was not the father’s, but the spirit’s that held him."
],
180: [
    "If the moon could produce a passion in someone by its natural law, why does it not send this on all humans, just as it pours its light on all? Again it is clear that the moon was made for shining, not for begetting demons. And if this came from the moon’s natural working, then when the demon was crushed the moon too — the cause of the passion — ought to have been harmed. But that is not so. Demons, wanting to deceive humans, put the names of the elements around themselves so that the elements might be accused as wicked — which they are not. By nature <the> elements are good, serving only the laws given them and having no authority from choice."
],
181: [
    "The unbeliever will somehow also be distorted and know no way to walk straight. Christ does not deem such people worthy of his company; if one may say something human, he grows weary and is distressed. Yet this is not aimed at this person’s face — and one must not think what is unfitting about them."
],
182: [
    "When he says, “How long shall I dwell with you who insult and are unbelieving?” he shows that the time of the incarnate presence required him to dwell with the not-good in God-befitting gentleness, so that through what he does he might correct them. “How long,” he says, “shall I dwell with you so insolent and unbelieving?” — showing that his presence with flesh compelled him to associate with the not-good in order to correct them."
],
183: [
    "“If you have faith as a mustard seed” — that is, hot and boiling, or faith likened to the tiny grain because of smallness in word. For “we have the treasure” of faith “in earthen vessels.”"
],
184: [
    "So he brought the chief disciples up the mountain and showed them the glory with which he will shine upon the world in due times; then, coming down from the mountain, he freed someone from a wicked and harsh spirit. Yet he had wholly to endure the saving passion for us and bear the Jews’ perversity. When that happened it would not be strange for the disciples to be in tumult and perhaps to think and say among themselves: He who raised so many dead by God-befitting authority, who rebukes seas and spirits, who crushes Satan by a word — how has he now been caught and fallen into murderers’ snares? Were we deceived in thinking him God? So that they may know what will wholly and altogether come, he foretells to them the mystery of the passion."
],
185: [
    "Mixing in the word about the resurrection, he weaves power together with weakness, glory with ingloriousness, the height of divinity with the cheapness of humanity. For he died as man and lived again as God. The disciples are grieved from love toward Christ, even though the resurrection was announced to come soon — because humans grieve more hotly when they hear grievous things and feel those more than the sweetest."
],
186: [
    "And they ask Peter craftily. Since, they say, he is accustomed to oppose Moses’ laws, he does not even pay the didrachma — knowing that Christ had also said, “I came not to destroy the law but to fulfill,” and that the manner of the economy requires this. To these Peter said — perhaps blushing to converse about these things."
],
187: [
    "Though able to bring forth the stater from the earth, he did not do that, but made the sign from the sea, to teach us a mystery full of contemplation. For we were fishes drawn up from life’s bitter turmoils as from a sea through the apostolic hooks, having in our mouths Christ the royal stater, given as ransom for two — for our soul and body, or for two peoples, Jews and gentiles — likewise ransoming poor and rich, since the old law also unreservedly demanded the drachma’s tax equally from rich and poor.",
    "The Savior could have brought forth the stater from the earth, but he did not; he worked the sign from the sea to show us a mystery full of contemplation. For we are the fishes caught from life’s turmoils through the apostolic teachings, and we have in our mouths the stater — that is, Christ."
],
188: [
    "We especially reckon the kingdom of the heavens even in the present, and we say it is either the calling in sanctification or the measure in faith and holiness. For the Savior also hints at something of the sort when he says, “The kingdom of the heavens is within you.”"
],
}

LEMMAS = {
173: [{"form": "μεταμόρφωσιν", "lemma": "μεταμόρφωσις", "gloss": "transfiguration", "lexica": "NT"}],
174: [],
175: [],
176: [{"form": "σκιαγραφίαις", "lemma": "σκιαγραφία", "gloss": "shadow-sketch / outline", "lexica": "LSJ"}],
177: [{"form": "μεσιτεία", "lemma": "μεσιτεία", "gloss": "mediation", "lexica": "NT"}],
178: [],
179: [],
180: [{"form": "<τὰ>", "lemma": "ὁ", "gloss": "the (supplied)", "lexica": "editorial"}],
181: [{"form": "ὀλιγωρεῖ", "lemma": "ὀλιγωρέω", "gloss": "make light of / grow weary", "lexica": "LSJ"}],
182: [],
183: [],
184: [],
185: [],
186: [{"form": "δίδραχμον", "lemma": "δίδραχμον", "gloss": "two-drachma temple tax", "lexica": "NT"}],
187: [{"form": "στατῆρα", "lemma": "στατήρ", "gloss": "stater coin", "lexica": "NT"}],
188: [],
}

CHOICES = {
173: [],
174: [],
175: [],
176: [{"term": "source fr.1 after fr.200", "english": "keep source label fr.1", "rejected": ["silently renumber to 201"], "why": "Array order is section id; disclose source numbering restart."}],
177: [],
178: [],
179: [{"term": "stray ‘23’", "english": "digit stripped in clean", "rejected": ["keep as verse marker"], "why": "OCR/page digit; not Greek text."}],
180: [{"term": "<τὰ>", "english": "supplied article", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}],
181: [],
182: [],
183: [],
184: [],
185: [{"term": "stray ‘24’", "english": "digit stripped in clean", "rejected": ["keep as marker"], "why": "OCR/page digit; not Greek text."}],
186: [],
187: [{"term": "στατήρ / ἀντίλυτρον", "english": "stater as ransom for two", "rejected": ["mere coin miracle only"], "why": "Fragment reads the sign as ransom for soul/body or two peoples."}],
188: [],
}

ALLUSIONS = {
173: [{"reference": "Matthew 17:2", "reason": "He was transfigured before them.", "certainty": "clear"}],
174: [{"reference": "Matthew 17:3-7", "reason": "Moses and Elijah; disciples fall; Jesus raises them.", "certainty": "clear"}],
175: [{"reference": "Matthew 17:4", "reason": "Peter’s three tents.", "certainty": "clear"}],
176: [{"reference": "Matthew 17:5", "reason": "This is my beloved Son; listen to him.", "certainty": "clear"}],
177: [{"reference": "Matthew 17:6", "reason": "Disciples fell on their faces.", "certainty": "clear"}, {"reference": "1 Timothy 6:16", "reason": "Dwells in unapproachable light.", "certainty": "clear"}],
178: [{"reference": "Matthew 17:11-12", "reason": "Elijah is coming; already came (John).", "certainty": "clear"}],
179: [{"reference": "Matthew 17:14-18", "reason": "Epileptic boy; rebuke of unclean spirit.", "certainty": "clear"}],
180: [{"reference": "Matthew 17:15", "reason": "Moon-struck / lunatic boy.", "certainty": "clear"}],
181: [{"reference": "Matthew 17:17", "reason": "Faithless and twisted generation.", "certainty": "clear"}],
182: [{"reference": "Matthew 17:17", "reason": "How long shall I be with you?", "certainty": "clear"}],
183: [{"reference": "Matthew 17:20", "reason": "Faith as a mustard seed.", "certainty": "clear"}, {"reference": "2 Corinthians 4:7", "reason": "Treasure in earthen vessels.", "certainty": "clear"}],
184: [{"reference": "Matthew 17:22-23", "reason": "Son of Man will be delivered up.", "certainty": "clear"}],
185: [{"reference": "Matthew 17:22-23", "reason": "Killed and raised on the third day.", "certainty": "clear"}],
186: [{"reference": "Matthew 17:24", "reason": "Does your teacher not pay the didrachma?", "certainty": "clear"}, {"reference": "Matthew 5:17", "reason": "Not to abolish but to fulfill.", "certainty": "clear"}],
187: [{"reference": "Matthew 17:27", "reason": "Fish with stater in mouth.", "certainty": "clear"}],
188: [{"reference": "Matthew 18:1", "reason": "Who is greatest in the kingdom?", "certainty": "clear"}, {"reference": "Luke 17:21", "reason": "Kingdom of God within you.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(173, 189):
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
        if 176 <= n <= 184:
            notes.append("Source edition labels restart fr.1–9 after fr.200; section id keeps array order.")
        if n == 180:
            notes.append("Supplied <τὰ> disclosed.")
        if n in (179, 185):
            notes.append("Stray page/verse digits stripped in clean Greek.")
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
                "title": reader_title(src.get("matthew")),
                "scholar_label": scholar_label(fragment=src.get("fragment"), matthew=src.get("matthew"), existing=src.get("head")),
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a44a47.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a44a47.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a44",
                        "cyril-matt-frag-a45",
                        "cyril-matt-frag-a46",
                        "cyril-matt-frag-a47",
                    ],
                    "sections": "173-188",
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
    print("english", [e["section"] for e in english[-20:]])


if __name__ == "__main__":
    main()
