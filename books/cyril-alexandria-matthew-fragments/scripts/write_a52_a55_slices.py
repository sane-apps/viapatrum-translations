#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a52..a55 (entries 205–220)."""
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
    if n <= 208:
        return "cyril-matt-frag-a52"
    if n <= 212:
        return "cyril-matt-frag-a53"
    if n <= 216:
        return "cyril-matt-frag-a54"
    return "cyril-matt-frag-a55"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(205, 221)}

PASS_A = {
205: "Hosanna to the son of David blessed; the Hebrew thus has in the 117th psalm: ANNA ADONAI OSIANNA, ADONAI ASLIANNA, BAROUCH ABBA BSAIM.",
206: "There-was on-the-one-hand in the temple multitude of merchants, money-changers or small-coin-dealers and with those of oxen and of sheep merchants turtledoves both selling and pigeons. These but useful to the sacrifices of the according to law worship. But it-was already the time of the to-cease the shadow and to-shine-up the in Christ truth; in-this-way indeed Christ fittingly the truth as-indeed with the own father in the beside him being temple being-honored, to-be-curtailed on-the-one-hand the in law he-has-commanded sacrifices and the smokes, house but of prayer to-be-shown the temple; for the to-rebuke the merchants and from the sacred precincts to-scare them the into sacrifice useful selling to some this wholly is and other nothing. But other of the evangelists 'also whip from cords to-make' says the Jesus and to-threaten blows and to-raise-against them; for it-was-necessary to-know those the legal honoring worship after the of the truth showing, that 'spirit of slavery' having and the to-be-freed refusing under scourges they-will-be and will-be-subject to punishment slave-like. He-sets-against them also the Isaiah as-accuser—for says the evangelist.",
207: "Also of the worship but the change he-foretells casting-out the being-slaughtered animals and the legal traditions. He-raises-against but the scourge signifying, that if again the same they-may-do, they-will-experience blows, and in-order-that he-may-show the slave-like of those under law, to-household-slaves befitting he-brings scourge.",
208: "Riddle was the having-happened, that of the Jews having-been-cast-out from the temple with the typic sacrifices the blind and lame are-healed who type having of the nations. Let-them-learn however also those selling also the of the spirit gifts and the priesthood, that those selling the pigeons he-cast-out from the temple having-scourged the Lord and let-them-cease profits for-themselves from ordinations gathering.",
209: "Through the unloving-of-God of the Jews he-withdraws.",
210: "If the 'God-breathed' you-knew 'scriptures', O senseless Pharisee, and the of the holy prophets voices, you-would-have-remembered saying of the blessed David toward the of the all savior Christ: 'swore Lord and not he-will-repent; you priest into the age according to the order of Melchizedek'. Tell then therefore, who from the scribes or Pharisees has-served to the God 'according to the order of Melchizedek'? Or wholly no-one. But also the forefather Abraham, the root of the generation of those from Israel, under the of Melchizedek priesthood has-been-blessed; but type was the Melchizedek and the according to him priesthood of the of all savior Christ, who has-become of us high-priest bringing-near to the God and father all those having-believed into him through the beyond law worship perfecting into sanctification. What therefore you-are-vexed, O Pharisee? You-accuse, tell me, the lawgiver of the law the loosing, and that not to the own he-followed commands? But of law wholly beyond God; for the the laws not for-himself rather, but for us having-defined transfers according to time upon what ever he-may-choose the having-been-arranged and raises into better. There-was therefore time of the to-cease the in types, to-be-shown but the better; wherefore he-said somewhere through voice of Isaiah: 'will-be-abolished ordinances of people'; for it-has-become-idle of the new command having-been-shown, which through himself has-spoken to us the son.",
211: "Asked the Christ, what-sort about the baptist the opinion they-have-had, since custom it-was to the Jews false-speakers to-call the holy and to-say, that from judgment own the prophecy they-fabricate not having-been-sent from God. But the Pharisees fear on-the-one-hand to-say the true, in-order-that not they-may-hear: through what not you-believed?",
212: "And is vineyard on-the-one-hand the Israel, as says the psalmist: 'vine from Egypt you-removed' and the Isaiah: 'vineyard', he-says, 'was-made for the beloved'. He-planted but it the God and went-abroad time long that-is he-was-long-suffering. Yet he-is-seen having-cared of the place and into mind having it; for no-one has-become through middle time, according to which not were-being-sent from the God prophets and righteous admonishing. But they have-become disobedient and having-dishonored those having-been-sent they-sent empty, this-is nothing having to-say about them good to the having-sent God.",
213: "Then also you sons of the God and father? Then by-nature the lot into you descends, if from midst you-may-make the heir? How will-you-become lords of things you-desire? And that how not of laughter worthy? For on-the-one-hand the Christ as son and of the of the God and father dignities essentially heir having-become human into sharing of the of himself kingdom was-calling those believing into him, but the Hebrews alone the kingdom to-have were-wishing, which was both impossible and ignorant. Observe but in these, that after the household-servants the son is-sent as not being-counted in household-servants, but as son true and through this Lord; for even-if he-wore of slave form economically, but he-was also thus God and son true of the God and father and natural having the lordship.",
214: "And who ever would-be these? Of the holy apostles the choir, through whom of the new covenant priests and teachers.",
215: "Stone here the Christ he-says, but corner the joining both and intimacy of the two peoples these, of the from Israel having-been-saved and of the from nations. Through this will-be-taken from you the kingdom of the heavens, this-is the of the salvation knowledge and the toward every what ever of the praised way and the toward the spirit sharing, through which someone acquires the of the heavens kingdom.",
216: "This has-marvelled the corner that-is of the two peoples the into same-ness meeting the blessed David saying: 'from Lord was-made this, and is marvelous in eyes of us'. Therefore saving on-the-one-hand the stone to the corner the from him having-been-made, crushing but and destruction to those outside having-remained of the intelligible and spiritual this concurrence; to some on-the-one-hand is the Christ 'rock of stumbling and stone of scandal'.",
217: "Marriage he-says the toward the son of the faithful joining, calling into this Jews, long-ago on-the-one-hand through prophets, later but through the disciples before the passion and the resurrection.",
218: "Have-refused the arrival those through the first household-servants having-been-called, who the through Moses having-thrust-aside law turned toward teachings of humans. Likewise but also those after those second having-been-called through second this-is of the holy apostles the beneficial having-left as farthest they-have-withdrawn upon the to-themselves seeming; for some on-the-one-hand upon the own field, through which is-signified of the earthly the possession and the about these zeal; toward commerce but others, through which again to us the money-loving is-shown passion and the about this spasm; for flesh-lovings us and pleasure-lovings worldly and vain distractions and the of the to-make-money care deprive us of the into age luxury and of the toward God intimacy.",
219: "Clearly of the Roman army the irresistible hand. Of God but we-say the Roman campaign, according as he-is master and of all creator.",
220: "And otherwise to-have-been-bound hands and feet he-is-said as of nothing remaining good to-do there being-able; for the of the good working until the present extends.",
}

PASS_B = {
205: [
    "“Hosanna to the Son of David; blessed…” The Hebrew stands thus in Psalm 117: ANNA ADONAI OSIANNA, ADONAI ASLIANNA, BAROUCH ABBA BSAIM."
],
206: [
    "There was in the temple a crowd of merchants — money-changers, or small-coin dealers — and with them sellers of oxen and sheep, and people selling turtledoves and pigeons. These things were useful for the sacrifices of worship under the law. But it was already time for the shadow to cease and for the truth in Christ to shine. So Christ, the Truth, rightly honored with his own Father in the temple that is his, commanded the sacrifices and smoke under the law to be curtailed, and showed the temple to be a house of prayer. For to rebuke the merchants and drive from the sacred precincts those selling what is useful for sacrifice is exactly that and nothing else.",
    "Another evangelist says Jesus also “made a whip of cords,” threatened blows, and raised it against them. Those who honor legal worship needed to know, after the truth was shown, that having a “spirit of slavery” and refusing to be freed, they will be under scourges and subject to slavish punishment. He also sets Isaiah against them as accuser — for so the evangelist says."
],
207: [
    "He also foretells the change of worship by casting out the animals being slaughtered and the legal traditions. He raises the scourge to show that if they do the same again they will taste blows, and to show the slavish state of those under the law he brings a scourge fitting for household slaves."
],
208: [
    "What happened was a riddle: when the Jews were cast out of the temple with the typological sacrifices, the blind and lame are healed — a type of the nations. And let those who sell the Spirit’s gifts and the priesthood also learn that the Lord cast the sellers of pigeons out of the temple with a scourge, and let them stop gathering profits for themselves from ordinations."
],
209: [
    "Because of the Jews’ lack of love for God, he withdraws."
],
210: [
    "If you knew the “God-breathed scriptures,” senseless Pharisee, and the holy prophets’ voices, you would have remembered blessed David saying to Christ the Savior of all: “The Lord has sworn and will not repent: You are a priest forever according to the order of Melchizedek.” Tell me, then: which of the scribes or Pharisees has served God “according to the order of Melchizedek”? None at all. Even Abraham our forefather, root of Israel’s line, was blessed under Melchizedek’s priesthood. Melchizedek and his priesthood were a type of Christ the Savior of all, who has become our high priest, bringing near to God the Father all who have believed in him and perfecting them into sanctification through worship beyond the law.",
    "Why then are you vexed, Pharisee? Do you accuse the Lawgiver, tell me, of loosing the law, and of not following his own commands? But God is wholly beyond the law. For the one who set the laws not chiefly for himself but for us transfers what was arranged, in due time, to whatever he chooses, and raises it to what is better. So there was a time for the things in types to cease and for the better to be shown. That is why he said somewhere through Isaiah’s voice, “The people’s ordinances will be abolished”; for they grew idle once the new command was shown, which the Son has spoken to us through himself."
],
211: [
    "Christ asked what opinion they held about the Baptist, because the Jews were accustomed to call the holy ones liars and to say they invent prophecy from their own judgment, not sent from God. The Pharisees fear to say the truth, lest they hear: “Why did you not believe?”"
],
212: [
    "The vineyard is Israel, as the psalmist says, “You brought a vine out of Egypt,” and Isaiah, “A vineyard was made for the beloved.” God planted it and went abroad a long time — that is, he was long-suffering. Yet he is seen caring for the place and holding it in mind; for there was no intervening time when prophets and righteous men were not being sent from God to admonish. But they became disobedient, and having dishonored those sent, they sent them away empty — that is, with nothing good to say about them to the God who sent them."
],
213: [
    "Are you too sons of God the Father? Does the lot descend to you by nature if you put the heir out of the way? How will you become lords of what you desire? And how is that not worth laughing at? For Christ, as Son and essential heir of God the Father’s dignities, became man and was calling those who believe in him into share of his own kingdom; but the Hebrews wanted to have the kingdom alone — which was both impossible and ignorant. Notice here that after the household servants the Son is sent, not as one counted among servants, but as true Son and therefore Lord. Even if he wore a slave’s form economically, he was still God and true Son of God the Father, and had lordship by nature."
],
214: [
    "And who would these be? The choir of the holy apostles, through whom come the priests and teachers of the new covenant."
],
215: [
    "By “stone” here he means Christ, and by “corner” the joining and fellowship of these two peoples — the remnant saved from Israel and those from the nations. For this reason “the kingdom of the heavens will be taken from you” — that is, the knowledge of salvation, the way toward everything praiseworthy, and sharing in the Spirit, through which one acquires the kingdom of the heavens."
],
216: [
    "Blessed David marveled at this corner — that is, the meeting of the two peoples into one — saying, “This was from the Lord, and it is marvelous in our eyes.” So the stone is saving for the corner made by him, but crushing and ruin for those who remained outside this intelligible and spiritual concurrence. For some, Christ is “a rock of stumbling and a stone of scandal.”"
],
217: [
    "By “marriage” he means the joining of the faithful to the Son, calling Jews into it — long ago through the prophets, later through the disciples before the passion and resurrection."
],
218: [
    "Those called through the first household servants refused to come: thrusting aside the law through Moses, they turned to human teachings. Likewise those called second after them through second messengers — that is, the holy apostles — left what was beneficial and withdrew as far as possible to what seemed good to themselves. Some went to their own field, which signifies possession of earthly things and zeal about them; others to commerce, which again shows us love of money and the spasm around it. For love of flesh and worldly love of pleasure, empty distractions, and care for making money deprive us of eternal enjoyment and intimacy with God."
],
219: [
    "Clearly the irresistible hand of the Roman army. We call the Roman campaign God’s, inasmuch as he is Master and Creator of all."
],
220: [
    "Otherwise he is said to have hands and feet bound as no longer able to do anything good there; for the working of the good extends only as far as the present."
],
}

LEMMAS = {
205: [{"form": "Ὡσαννά", "lemma": "ὡσαννά", "gloss": "hosanna", "lexica": "NT"}],
206: [{"form": "κολλυβισταί", "lemma": "κολλυβιστής", "gloss": "small-coin changer", "lexica": "NT"}],
207: [],
208: [{"form": "χειροτονιῶν", "lemma": "χειροτονία", "gloss": "ordination / appointment", "lexica": "patristic"}],
209: [],
210: [{"form": "Μελχισεδέκ", "lemma": "Μελχισεδέκ", "gloss": "Melchizedek", "lexica": "NT"}],
211: [],
212: [],
213: [{"form": "κληρονόμον", "lemma": "κληρονόμος", "gloss": "heir", "lexica": "NT"}],
214: [],
215: [],
216: [{"form": "γωνίαν", "lemma": "γωνία", "gloss": "corner / angle", "lexica": "NT"}],
217: [],
218: [{"form": "φιλοσαρκίαι", "lemma": "φιλοσαρκία", "gloss": "love of flesh", "lexica": "patristic"}],
219: [],
220: [],
}

CHOICES = {
205: [{"term": "Hebrew transliteration", "english": "keep Hebrew strings as in extract", "rejected": ["normalize / invent pointing"], "why": "Copy-text preserves the Aegean extract’s Hebrew line."}],
206: [],
207: [],
208: [{"term": "stray ‘29’", "english": "digit stripped in clean", "rejected": ["keep as marker"], "why": "OCR/page digit; not Greek text."}],
209: [],
210: [],
211: [],
212: [],
213: [],
214: [],
215: [{"term": "stray ‘30’", "english": "digit stripped in clean", "rejected": ["keep as marker"], "why": "OCR/page digit; not Greek text."}],
216: [],
217: [],
218: [],
219: [{"term": "Ῥωμαϊκῆς στρατιᾶς", "english": "Roman army as God’s hand", "rejected": ["mere politics"], "why": "Fragment reads the army as instrument under God’s mastery."}],
220: [],
}

ALLUSIONS = {
205: [{"reference": "Matthew 21:9", "reason": "Hosanna to the Son of David.", "certainty": "clear"}, {"reference": "Psalm 118:25-26", "reason": "Hebrew hosanna / blessed line.", "certainty": "clear"}],
206: [{"reference": "Matthew 21:12-13", "reason": "Cleansing the temple; house of prayer.", "certainty": "clear"}, {"reference": "John 2:15", "reason": "Whip of cords.", "certainty": "clear"}, {"reference": "Romans 8:15", "reason": "Spirit of slavery.", "certainty": "clear"}],
207: [{"reference": "Matthew 21:12", "reason": "Drove out sellers.", "certainty": "clear"}],
208: [{"reference": "Matthew 21:14", "reason": "Blind and lame healed in the temple.", "certainty": "clear"}],
209: [{"reference": "Matthew 21:17", "reason": "Left them and went out to Bethany.", "certainty": "clear"}],
210: [{"reference": "Matthew 21:23", "reason": "By what authority?", "certainty": "clear"}, {"reference": "Psalm 110:4", "reason": "Priest forever after Melchizedek.", "certainty": "clear"}, {"reference": "Isaiah 24:5", "reason": "Ordinances abolished (LXX echo).", "certainty": "possible"}],
211: [{"reference": "Matthew 21:25", "reason": "Baptism of John — from heaven or from men?", "certainty": "clear"}],
212: [{"reference": "Matthew 21:33-41", "reason": "Parable of the vineyard.", "certainty": "clear"}, {"reference": "Psalm 80:8", "reason": "Vine out of Egypt.", "certainty": "clear"}, {"reference": "Isaiah 5:1", "reason": "Beloved’s vineyard.", "certainty": "clear"}],
213: [{"reference": "Matthew 21:37", "reason": "He sent his son.", "certainty": "clear"}, {"reference": "Philippians 2:7", "reason": "Form of a slave.", "certainty": "clear"}],
214: [{"reference": "Matthew 21:41", "reason": "Lease vineyard to other farmers.", "certainty": "clear"}],
215: [{"reference": "Matthew 21:42-43", "reason": "Stone the builders rejected; kingdom taken.", "certainty": "clear"}],
216: [{"reference": "Matthew 21:42", "reason": "Cornerstone; marvelous in our eyes.", "certainty": "clear"}, {"reference": "Psalm 118:22-23", "reason": "From the Lord; marvelous.", "certainty": "clear"}, {"reference": "1 Peter 2:8", "reason": "Rock of stumbling.", "certainty": "clear"}],
217: [{"reference": "Matthew 22:2", "reason": "Wedding feast for the son.", "certainty": "clear"}],
218: [{"reference": "Matthew 22:2-5", "reason": "Invited refuse; field and business.", "certainty": "clear"}],
219: [{"reference": "Matthew 22:7", "reason": "King sent troops; burned their city.", "certainty": "clear"}],
220: [{"reference": "Matthew 22:13", "reason": "Bind him hand and foot.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(205, 221):
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
        if n == 205:
            notes.append("Hebrew transliteration kept as in extract.")
        if n in (208, 215):
            notes.append("Stray page/verse digits stripped in clean Greek.")
        if n in (213, 214):
            notes.append("Edition fr.240 absent from source array (skip).")
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a52a55.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a52a55.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a52",
                        "cyril-matt-frag-a53",
                        "cyril-matt-frag-a54",
                        "cyril-matt-frag-a55",
                    ],
                    "sections": "205-220",
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
    print("english max", english[-1]["section"], english[-1]["claim"], "count", len(english))


if __name__ == "__main__":
    main()
