# -*- coding: utf-8 -*-
"""Literary two-pass of Origen, Homilies on Jeremiah, Homily 7. GCS III."""
from __future__ import annotations

import json
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
SRC = BOOK / "translations/jeremiah_source.json"
EN = BOOK / "translations/jeremiah_english.json"
JUST = BOOK / "reviews/justifications"


def A(reference, reason, certainty="clear"):
    return {"reference": reference, "reason": reason, "certainty": certainty}


SECTIONS = [
    {
        "section": "7.1",
        "homily": 7,
        "title": "He judges little by little, and does not strike them to an end",
        "english": [
            "The one who judges according to God gives those being punished a place, and does not, at the same moment as the sin, bring the completion of the punishment upon the one who has sinned. For this reason, 'judging little by little,' he punishes. And the example of this is in Leviticus. For in the curses of those who transgress the law it is written, after the earlier punishments: 'And it shall be, if after these things you do not turn,' says the Lord, 'I too will add to you seven plagues.' And again he tells another punishment: 'And it shall be, if after these things you do not turn, but walk toward me sideways, I too will walk with you in a sideways anger.' And you will find God measuring out punishments with sparing, since he wants to lead the one who has sinned to turning, and not paying all at once.",
            "Such things, then, as far as the wording, had come to be about the people, and the word, threatening them with what they will suffer after those things, says: 'And it shall be in those days, says the Lord your God, I will not strike you to an end.' And if these things reach also, most of all, to the punishments that are going to be — unless the one who can, from what has happened in this life about the people, should transfer also to those. For I, being persuaded, would say that as 'they serve a copy and shadow of the heavenly things,' so that people was punished on a copy and shadow of the true punishments for their own sins, so that every punishment according to the law and the prophets about the people contains a shadow of true punishments.",
            "If then an end upon the sins did not come to them, but at some time at the last — so neither will there never be a punishment after the going-out upon those who have sinned. An end upon Jerusalem is when the captivity is Nebuchadnezzar's. And yet someone will say that not even then was it an end, nor even at the Maccabean things. But an end for the people is at the coming of my Lord Jesus Christ. For so long as the Savior was not saying to them, 'Behold, your house is left to you,' it was not left. But when he wept over Jerusalem, saying: 'Jerusalem, Jerusalem, who kills the prophets and stones those sent to her, how often I wanted to gather your children, as a hen gathers her brood under her wings, and you did not want it? Behold, your house is left to you desolate,' the house has been left, Jerusalem has been surrounded by armies, as of a house left, and 'her desolation has drawn near.' Then after their fall, the salvation came to us of the nations. So those were being punished, and an end did not reach them until the sojourn of my Lord Jesus.",
        ],
        "added_allusions": [
            A("Wisdom 12:10", "Judging little by little."),
            A("Leviticus 26:18", "Quoted: I will add seven plagues."),
            A("Leviticus 26:23-24", "Quoted: if you walk sideways, I will walk in sideways anger."),
            A("Jeremiah 5:18", "Quoted: I will not strike you to an end."),
            A("Hebrews 8:5", "Quoted: they serve a copy and shadow of the heavenly things."),
            A("Matthew 23:37-38", "Quoted: Jerusalem, Jerusalem; your house is left desolate."),
            A("Luke 21:20", "Jerusalem surrounded by armies; desolation near."),
            A("Romans 11:11", "After their fall, salvation to the nations."),
        ],
        "translator_notes": [
            "ἐπιδημία: sojourn of the Lord, not epidemic.",
            "TEI of the Jerusalem lament is gapped; English follows Matthew 23:37-38.",
        ],
        "pass_a_gloss": "The one judging according to God gives those being punished a place and not at the same time as the sinning, punishing, brings the completion of the punishment upon the one who has sinned. Through this, judging little by little, he punishes. And the example of this is in Leviticus; for in the curses of those transgressing the law it has been written after the former punishments: and it shall be, if after these you do not turn, says the Lord, I too will add to you seven plagues. And again he narrates another punishment: and it shall be, if after these you do not turn but walk toward me sideways, I too will walk with you in sideways anger. And you will find God measuring punishments with sparing, since he wants to lead the one who has sinned into turning, and not paying all at once. If then an end upon the sins has not come to those, but at some last time. An end upon Jerusalem is when the captivity is that of Nebuchadnezzar. And yet someone will say not even then an end, nor even upon the Maccabean things. But an end to the people upon the presence of my Lord Jesus Christ. When he wept upon Jerusalem saying Jerusalem, Jerusalem, who kills the prophets... behold your house is left to you desolate, the house has been left. Then after their fall the salvation came to us of the nations. They were being punished, and an end did not reach upon them until the sojourn of my Lord Jesus.",
        "lemmas": [
            {"form": "κατὰ βραχὺ", "lemma": "βραχύς", "gloss": "little by little", "lexica": "LSJ"},
            {"form": "συντέλειαν", "lemma": "συντέλεια", "gloss": "completion / end", "lexica": "LSJ"},
            {"form": "ἐπιδημίας", "lemma": "ἐπιδημία", "gloss": "sojourn / coming", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἐπιδημία",
                "english": "sojourn",
                "rejected": ["epidemic", "visit as tourism"],
                "why": "The Lord's coming to Jerusalem.",
            }
        ],
        "bible_refs": [
            {"display": "Leviticus 26:18", "method": "wording", "note": "Seven plagues added."},
            {"display": "Matthew 23:37-38", "method": "wording", "note": "Jerusalem lament; TEI gapped."},
            {"display": "Jeremiah 5:18", "method": "wording", "note": "Not strike to an end."},
        ],
    },
    {
        "section": "7.2",
        "homily": 7,
        "title": "Not all are struck with seven plagues",
        "english": [
            "And I am watching whether such things are also about us, and some punishments come to be, so that these have no trial of second punishments but are enough with the former, and others come even to the second, yet not also to the third, and others will come even to the fourth. For 'I will add seven plagues' shows some mystery of one coming to be, and a second, and a third, until the seven that have been said, upon some. Not all are struck with seven plagues. But I think some will be struck with six, others five, others four, others three or two, and those most lacking of all in punishments I think will be struck with one plague.",
            "God then knows also the things about the plagues. Therefore it is written here at the beginning of the reading: 'And it shall be in those days' — the days about the things that have been said — 'I will not make you an end.' But not in those days an end. For there are some days when he will make those he will make into an end.",
        ],
        "added_allusions": [
            A("Leviticus 26:18", "Quoted: I will add seven plagues."),
            A("Jeremiah 5:18", "Quoted: I will not make you an end."),
        ],
        "translator_notes": [],
        "pass_a_gloss": "And I am watching lest also about us such things are, and some punishments come to be, so that these on the one hand not have a trial of second punishments but be enough with the former, others come even upon the second, not indeed also upon the third, others will come even upon the fourth. For I will add seven plagues shows some mystery of one coming to be and a second and a third until the seven said upon some. Not all are struck seven plagues; but I think some will be struck six plagues, others five, others four, others three or two, and those most lacking of all in punishments I think will be struck one plague. God then knows also the things about the plagues. Therefore it has been written here according to the beginning of the reading: and it shall be in those days, the ones about the things said, I will not make you an end. But not in those days an end; for there are some days when he will make those he will make into an end.",
        "lemmas": [
            {"form": "πληγὰς ἑπτά", "lemma": "πληγή", "gloss": "seven plagues / blows", "lexica": "LSJ"},
            {"form": "μυστήριον", "lemma": "μυστήριον", "gloss": "hidden thing", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "συντέλειαν",
                "english": "an end",
                "rejected": ["the end of the world as a slogan"],
                "why": "Here: making an end of that people in those days, vs other days.",
            }
        ],
        "bible_refs": [
            {"display": "Leviticus 26:18", "method": "wording", "note": "Seven plagues."},
            {"display": "Jeremiah 5:18", "method": "wording", "note": "Not make you an end."},
        ],
    },
    {
        "section": "7.3",
        "homily": 7,
        "title": "You served other gods in your land; so you shall in a land not yours",
        "english": [
            "'And it shall be when you say: For what reason has the Lord our God done all these evils to us? And you shall say to them: Because you abandoned me and served other gods in your land, so you shall serve other gods in a land not yours.' Let the wording be understood, and it is enough for the present to set the reminder from the wording before those able to hear.",
            "The sons of Israel had the holy land, the temple, the house of prayer. They ought to have served God. Transgressing the divine commands they also worshipped idols, and they took in the idols of Damascus, as it is written in the Books of Kingdoms, and they took up other idols of those they brought into the holy land. By the idols of the nations which they took in, they made themselves worthy to be thrown down into the land of the idols, to come to be there, where they were bowing to the idols. So the word says to them according to the wording: 'Because you abandoned me and served foreign gods in your land, so you shall serve foreign gods in a land not yours.' Everyone who makes a thing a god serves foreign gods.",
            "Do you deify foods and drinks? Your god is the belly. Do you honor silver as a great good, and the wealth below? Your god is mammon, and lord. For Jesus called him lord of the money-lovers, saying: 'You cannot serve God and mammon. No one can serve two lords.' So the one who honors silver and wonders at wealth and thinks it a good, and accepts the rich as gods, and sets at nothing the poor as not having their god — this one makes silver a god.",
            "If someone, being in the church of God, bows to foreign gods, making gods of things not worthy to be made gods, he will be thrown out into a foreign land, and let him bow to the gods he bowed to inside, once he has come to be outside. Let the money-lover be outside, thrown out from the church; let the belly-slave be outside, having come to be from the church. These things on one reading of the figure — that I may not now work beyond myself also about the land of which the Savior said, 'Who will give you what is ours?'",
            "Now then we are in a foreign land, and we pray to do the opposite of what the sons of Israel did in the holy land. For they bowed to the foreign things, to foreign gods, in the holy land; and we, in a foreign land, bow to the God who is foreign to the land, foreign to the affairs upon the earth. For the ruler of this age rules here, and God is foreign to that ruler's sons. And if I say foreign, I do not mean this: not the one who made the world, but foreign to the lord of the evil, foreign to the present sins.",
            "And even wanting to bow, in this land of the ill-treatment, to the God who is foreign to the affairs of sin, let us see what we do. We do not say: 'How shall we sing the Lord's song upon a foreign land?' but: how shall we sing the Lord's song not upon a foreign land? We seek a place of this, of singing the Lord's song, a place of bowing to the Lord our God upon a foreign land. What then is the place? I have found it. He came upon this, having worn the body that saves, having taken up 'the body of sin' 'in the likeness of flesh of sin,' that in this place, through Christ Jesus who sojourned and made idle the ruler of this age and made idle the sin, I may be able to bow to God here, and after this I shall bow in the holy land. For if someone who bowed to the idols in the holy land has gone away into the foreign land, someone who has bowed to God in the foreign land will go away upon the holy land in Christ Jesus, to whom is the glory and the might unto the ages. Amen.",
        ],
        "added_allusions": [
            A("Jeremiah 5:19", "Quoted: because you served other gods in your land, so in a land not yours."),
            A("2 Kings 16:10-13", "Idols of Damascus."),
            A("Philippians 3:19", "Quoted: the belly is god."),
            A("Matthew 6:24", "Quoted: you cannot serve God and mammon; two lords."),
            A("Luke 16:13", "Same mammon saying."),
            A("Psalm 137:4", "Quoted: how shall we sing the Lord's song upon a foreign land."),
            A("Romans 6:6", "Body of sin."),
            A("Romans 8:3", "In the likeness of flesh of sin."),
            A("Baruch 3:10-13", "Why are you in the land of enemies; you left the fountain of life."),
        ],
        "translator_notes": [
            "Do not invert 'foreign to the lord of evil' into 'God of evil.' God is alien to evil, not evil's god.",
            "τροπολογία kept out of the reading English: 'on one reading of the figure.'",
        ],
        "pass_a_gloss": "And it shall be when you say: for what reason has the Lord our God done all these evils to us? And you shall say to them: because you abandoned me and served other gods in your land, so in a land not yours. The sons of Israel had the holy land, the temple, the house of prayer. They ought to serve God. Transgressing the divine commands they also worshipped idols and took in the idols of Damascus, as it is written in the Kingdoms. Everyone making something a god serves foreign gods. Do you deify foods and drinks? Your god is the belly. Do you honor silver as a great good? Your god is mammon and lord. You cannot serve God and mammon. If someone in the church bowing to foreign gods will be thrown out into a foreign land. Now we are in a foreign land. They bowed to the foreign in the holy land; we in a foreign land bow to the God foreign to the land, foreign to the affairs upon earth. The ruler of this age rules here, and God is foreign to his sons. If I say foreign I do not mean not having made the world, but foreign to the lord of the evil, foreign to the present sins. How shall we sing the Lord's song upon a foreign land? He came wearing the body that saves, in likeness of flesh of sin, that I may bow to God here and after this in the holy land in Christ Jesus. Amen.",
        "lemmas": [
            {"form": "θεοποιῶν", "lemma": "θεοποιέω", "gloss": "make a god of", "lexica": "LSJ; Lampe"},
            {"form": "μαμωνᾷ", "lemma": "μαμωνᾶς", "gloss": "mammon", "lexica": "LSJ"},
            {"form": "ἀλλότριον", "lemma": "ἀλλότριος", "gloss": "foreign / belonging to another", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἀλλότριον τοῦ κυρίου τῆς κακίας",
                "english": "foreign to the lord of the evil",
                "rejected": ["the God of evil"],
                "why": "God is alien to evil's ruler, not evil's god. The machine draft inverted this.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 5:19", "method": "wording", "note": "Other gods in your land; so in a land not yours."},
            {"display": "Matthew 6:24", "method": "wording", "note": "God and mammon."},
            {"display": "Psalm 137:4", "method": "wording", "note": "Song on a foreign land."},
        ],
    },
]


def source_map():
    return {str(r.get("section")): r for r in json.loads(SRC.read_text(encoding="utf-8"))}


def write_justification(sec: dict, src: dict) -> None:
    rec = {
        "anf_compare": {
            "notes": "No public-domain English of the Greek Jeremiah homilies (FOTC 97 is copyrighted). Sense checked against Klostermann GCS III. Modern English was not copied.",
            "status": "no_pd_reference",
        },
        "apparatus": [],
        "bible_refs": sec["bible_refs"],
        "checks": {"anf_diverge": "pass", "lemma_constraint": "pass", "placeholders": "pass"},
        "choices": sec["choices"],
        "confidence": "source_verified",
        "edition": {
            "id": "gcs6-klostermann-1901",
            "language": "grc",
            "locus": src.get("klostermann") or f"GCS Orig. III Hom. {sec['section']}",
            "path": src.get("source_xml") or "sources/first1k/tlg2042.tlg009.opp-grc1.xml",
        },
        "excerpt_id": f"jeremiah_{sec['section'].replace('.', '_')}",
        "lemmas": sec["lemmas"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": sec["english"],
        "reviewer": "pending-human",
        "source_text": " ".join(str(p) for p in (src.get("greek") or [])),
        "variants": [],
    }
    (JUST / f"jeremiah_{sec['section'].replace('.', '_')}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def apply_english() -> None:
    rows = json.loads(EN.read_text(encoding="utf-8"))
    by = {str(r.get("section")): r for r in rows}
    for sec in SECTIONS:
        by[sec["section"]] = {
            "section": sec["section"],
            "homily": sec["homily"],
            "title": sec["title"],
            "english": sec["english"],
            "notes_covered": [],
            "added_allusions": sec["added_allusions"],
            "translator_notes": sec["translator_notes"],
            "klostermann": f"GCS Orig. III Hom. {sec['section']}",
        }

    def key(r):
        parts = str(r.get("section") or "0").split(".")
        try:
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except ValueError:
            return (999, 0)

    EN.write_text(json.dumps(sorted(by.values(), key=key), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    sm = source_map()
    for sec in SECTIONS:
        write_justification(sec, sm[sec["section"]])
    apply_english()
    print(f"wrote {len(SECTIONS)} Homily 7 sections")


if __name__ == "__main__":
    main()
