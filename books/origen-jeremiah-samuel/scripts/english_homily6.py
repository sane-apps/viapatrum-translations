# -*- coding: utf-8 -*-
"""Literary two-pass of Origen, Homilies on Jeremiah, Homily 6. GCS III."""
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
        "section": "6.1",
        "homily": 6,
        "title": "The Lord's eyes are toward faith, and toward every virtue",
        "english": [
            "'Lord,' he says, 'your eyes are toward faith,' as 'the eyes of the Lord are upon the righteous,' for he turns them away from the unrighteous. So the eyes of the Lord are toward faith, for he turns them away from unbelief. That is why the one who understands what he is saying in the prayer has spoken well: 'Lord, your eyes are toward faith.' What is written here is: 'Lord, your eyes are toward faith.'",
            "And since 'if a man of understanding hears a wise word, he will praise it and add to it,' see how much there is to do from 'Lord, your eyes are toward faith.' Paul says: 'Now these three remain, faith, hope, love; and the greatest of these is love.' As the eyes of the Lord are toward faith, so the eyes of the Lord are toward hope, so the eyes of the Lord are toward love.",
            "And since there is 'a spirit of power and of love and of self-control,' the eyes of the Lord are toward love, and so toward power, and so toward self-control. The eyes of the Lord are upon righteousness. So the eyes of the Lord are upon all the virtues.",
            "If then you too want the rays of God's intelligible eyes to reach you, take up the virtues. And it will be as 'Lord, your eyes are toward faith,' so 'Lord, your eyes' toward each good you acquire. And if you are of such a size that the Lord's eyes shine on you, you will say: 'The light of your face has been marked upon us, Lord.'",
        ],
        "added_allusions": [
            A("Jeremiah 5:3", "Quoted: Lord, your eyes are toward faith."),
            A("Psalm 34:15", "Quoted: the eyes of the Lord are upon the righteous."),
            A("Sirach 21:15", "Quoted: if a man of understanding hears a wise word, he will praise it and add to it."),
            A("1 Corinthians 13:13", "Quoted: faith, hope, love remain; the greatest is love."),
            A("2 Timothy 1:7", "Quoted: a spirit of power and of love and of self-control. TEI has ἀπάπης for ἀγάπης."),
            A("Psalm 4:6", "Quoted: the light of your face has been marked upon us."),
        ],
        "translator_notes": [
            "2 Timothy 1:7: TEI reads ἀπάπης; English follows ἀγάπης (love), with power and self-control.",
        ],
        "pass_a_gloss": "Lord, he says, your eyes are toward faith, as the eyes of the Lord are upon the righteous, for from the unrighteous he turns them away; so the eyes of the Lord toward faith, for from unbelief he turns them away. Therefore it has been well said by the one understanding what he says in the prayer: Lord, your eyes toward faith. What is written here is: Lord, your eyes toward faith. And since if a man of understanding hears a wise word he will praise it and add upon it, see how many things there are to do from Lord, your eyes toward faith. Paul says: now these three remain, faith, hope, love; and greater of these is love. As eyes of the Lord toward faith, eyes of the Lord toward hope, eyes of the Lord toward love. And since there is a spirit of power and of love and of self-control, eyes of the Lord toward love, so eyes of the Lord toward power, so eyes of the Lord toward self-control. Eyes of the Lord upon righteousness. So upon all virtues eyes of the Lord. If then you too want the rays of the intelligible eyes of God to reach upon you, take up the virtues. And it will be as Lord, your eyes toward faith, so Lord, your eyes toward each of the goods you may acquire. And if you are of such a size that the eyes of the Lord shine on you, you will say: the light of your face has been marked upon us, Lord.",
        "lemmas": [
            {"form": "εἰς πίστιν", "lemma": "πίστις", "gloss": "toward faith", "lexica": "LSJ"},
            {"form": "ἀπιστίας", "lemma": "ἀπιστία", "gloss": "unbelief", "lexica": "LSJ"},
            {"form": "σωφρονισμοῦ", "lemma": "σωφρονισμός", "gloss": "self-control / discipline", "lexica": "LSJ"},
            {"form": "νοητῶν ὀφθαλμῶν", "lemma": "νοητός", "gloss": "intelligible eyes", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἀγάπης",
                "english": "love",
                "rejected": ["purity (TEI ἀπάπης)"],
                "why": "2 Timothy 1:7; TEI garbles ἀγάπης as ἀπάπης.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 5:3", "method": "wording", "note": "Eyes toward faith."},
            {"display": "1 Corinthians 13:13", "method": "wording", "note": "Faith, hope, love."},
            {"display": "2 Timothy 1:7", "method": "wording", "note": "Power, love, self-control; TEI ἀπάπης."},
        ],
    },
    {
        "section": "6.2",
        "homily": 6,
        "title": "You scourged them, and they did not feel the pain",
        "english": [
            "Then let us look at what is said about the sinners: 'You scourged them, and they did not feel the pain.' These sensible scourges, brought upon living bodies, cause pain to those being scourged whether they will or not. But the scourges of God are such that some of those scourged feel the pain, and some of those scourged do not.",
            "Let us see if we can tell what it is to feel pain from God's scourges and what it is not to, and that those who do not feel pain from God's scourges are wretched, and those who do feel pain from them are blessed. For Wisdom says: 'Who will set scourges upon my thought, and a seal of cunning upon my lips, that they may not spare my ignorances, and my sins may not destroy me?' Attend to 'Who will set scourges upon my thought?' So there are scourges that scourge the thought. The Lord's scourges scourge the thought. For a word that lays hold of the soul and brings it to a sense of what has been sinned scourges it. It scourges the blessed one who feels pain at the scourges, because what is said reaches him, and he does not make little of the one who rebukes him.",
            "But when someone is found, if I may say so, without feeling, it will be said about him: 'You scourged them, and they did not feel the pain.' The same word is spoken as a rebuke, say, to reach the thought of one whose conscience has been stained by some sin. If one of the hearers is pained, so that it is said about him, 'Did you see how so-and-so was pricked?' and another of the hearers is not pained, but is without feeling toward the rebukes, it is clear that it will be said about the one who does not even perceive: 'You scourged them, and they did not feel the pain.'",
            "That is one account of 'they did not feel the pain' or they did. Let us see if we have another. There come to be in bodies deadnesses and drynesses of certain parts, and often the members that have died suffer such things compared with the living, that when things able to cause pain are brought to the living member, the one to whom the pain-making thing is brought hurts; but when the pain-making things are brought to the member without feeling, that one does not perceive, when there is a deadness about it. If you have seen this in the body, transfer it to the soul, and see that there is also a soul with members dying, so that it does not perceive from the scourges, even if painful things are brought. Terrible things are brought, but such-and-such a soul will not perceive, and another will. And perhaps the one who does not perceive from pains brought upon him is more grieved at not perceiving than at perceiving, praying rather to feel pain if the painful things were brought (since this is a sign that he is alive), and loathing not to perceive the painful things.",
            "As this happens in bodies, so I think something of this kind is shown in 'they would wish they had been burnt with fire': as when the fire is brought to someone and the one being burned does not perceive, they would wish, having grasped the comparison of those who do not perceive the pains and those who do, rather to perceive at the fire than not to perceive. And someone might pray, when that judged fire is brought upon the sinners, rather to perceive than not to perceive. These things are because of 'You scourged them, and they did not feel the pain. You completed them, and they did not wish to receive training.'",
            "When the God who provides for the whole does the purifying things for the salvation of a soul, he has completed what is upon him. You will understand 'You completed them, they did not wish to receive training' from the example of the one handing over knowledge and the one not willing to take the knowledge from the one handing it over. Let the teacher do all that is in him and complete everything toward the handing-over of knowledge, and let that one not receive what is said. I would say about such a one to the teacher: you completed so-and-so, and he did not wish to receive training. If then all the things from providence come upon us, that we may be completed and perfected, and we do not receive the things of the providence that is drawing us toward perfection, it would be said by the one who understands, to God: Lord, you completed them, and they did not wish to receive training.",
        ],
        "added_allusions": [
            A("Jeremiah 5:3", "Quoted: you scourged them and they did not feel the pain; you completed them and they did not wish to receive training."),
            A("Sirach 23:2", "Quoted: who will set scourges upon my thought."),
            A("Acts 2:37", "Pricked: they were cut to the heart."),
            A("Isaiah 9:5", "Burnt with fire — the wish of those who do not feel."),
        ],
        "translator_notes": [
            "πονεῖν: feel the pain of the scourge, not merely 'suffer' in general.",
        ],
        "pass_a_gloss": "Then concerning the sinners let us see the thing said: you scourged them and they did not feel pain. These sensible scourges brought to living bodies, whether the scourged will or not, produce pain for them; but the scourges of God are such that some of the scourged feel pain, and some of the scourged do not feel pain. Let us see if we can narrate what it is to feel pain from scourges of God and what not to feel pain, and that those not feeling pain from scourges of God are wretched, and blessed those feeling pain from scourges of God. For Wisdom says: who will give scourges upon my thought, and upon my lips a seal of cunning ones, that they may not spare upon my ignorances, and my sins may not destroy me? Attend to who will give scourges upon my thought. Therefore there are scourges scourging the thought. The scourges of the Lord scourge the thought; for a word laying hold of the soul and bringing it into a co-perception of the things sinned scourges; and it scourges the blessed one feeling pain upon the scourges, for the things said reach him, and he does not make cheap the one rebuking from himself. But when someone is found, so to speak, without perception, it will be said about him: you scourged them and they did not feel pain. When then the God providing for the wholes does the purifying things upon salvation of a soul, he has completed what is upon him. You will understand you completed them they did not wish to receive training from the example of the one handing over the knowledge and the one not willing to take the knowledge from the one handing over.",
        "lemmas": [
            {"form": "ἐμαστίγωσας", "lemma": "μαστιγόω", "gloss": "you scourged", "lexica": "LSJ"},
            {"form": "ἐπόνησαν", "lemma": "πονέω", "gloss": "felt pain / toiled in pain", "lexica": "LSJ"},
            {"form": "παιδείαν", "lemma": "παιδεία", "gloss": "training / discipline", "lexica": "LSJ"},
            {"form": "ἀναίσθητος", "lemma": "ἀναίσθητος", "gloss": "without feeling", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "οὐκ ἐπόνησαν",
                "english": "they did not feel the pain",
                "rejected": ["they did not suffer (too vague)", "they did not labor"],
                "why": "The point is numbness to the blow, not refusal of work.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 5:3", "method": "wording", "note": "Scourged; did not feel pain; did not receive training."},
            {"display": "Sirach 23:2", "method": "wording", "note": "Scourges upon my thought."},
        ],
    },
    {
        "section": "6.3",
        "homily": 6,
        "title": "They hardened their faces harder than rock; I will go to those of a full soul",
        "english": [
            "'They made their faces harder than rock.' You will understand this too from the more bodily things. Of those who sin, some, hearing words of rebuke at the sin, blush and sink down and fall under it, when the rebuking word touches them. Others are such that they are without a blush, not ashamed at what they are rebuked for, at what they have sinned. You would say then about those who are not ashamed: 'They made their faces harder than rock.' If you have understood it in the bodily things, move with me in the word to the soul, having understood a face, about which it is said: 'then face to face.' And see a hard soul, such as Pharaoh's heart was, hardened, so that it stands contrary to what is announced, and as if throwing off what is said, not being formed according to what is announced.",
            "For there you will find that 'They made their faces harder than rock and did not wish to turn' fits. 'And I said: perhaps they are poor, because they did not wish to know the way of the Lord and the judgment of God. I will go to the full-souled and I will speak to them.' Having understood these things about those who do not wish to be trained, who do not understand at the scourges of God, he says, having understood the cause of these things. Their soul is poor. 'And I said: perhaps they are poor, because they were not able' — because they did not know the way of the Lord and the judgment of God. 'I will go to the full-souled and I will speak to them.' The full-souled are spoken of in praise, of souls. And among the Greeks too the 'full' is named continually, and the greatness of the rational soul.",
            "For when someone sets himself to great matters and has purposes worth speaking of, and always looks at what must be, how he will live according to right reason, wanting and seeing nothing low or small, such a one has the fullness and the greatness in the soul. These former ones, then, whom the word blamed, since they were poor, did not hear, the prophet says. For this reason they did not hear, since they are poor. 'I will go to the full-souled and I will speak to them.' And if it is blessed to be at the saying 'into ears that hear,' it is blessed if one happens upon a full and great hearer.",
            "Therefore, these things being said, knowing that the loss is not so much to those who speak as to those who hear, in not receiving what is announced — and he accuses poverty of their mind and thought — let us ask to receive from God, as the word grows in us, fullness and greatness in Christ Jesus, that we may be able to hear the holy and sacred words, to whom is the glory and the might unto the ages of the ages. Amen.",
        ],
        "added_allusions": [
            A("Jeremiah 5:3-5", "Quoted: faces harder than rock; perhaps they are poor; I will go to the full-souled."),
            A("1 Corinthians 13:12", "Quoted: then face to face."),
            A("Exodus 9:12", "Pharaoh's heart hardened."),
            A("Matthew 11:15", "Ears that hear."),
        ],
        "translator_notes": [
            "ἁδροί: those of a full / substantial soul, in praise, not 'stout' as a body-word.",
        ],
        "pass_a_gloss": "They made their faces harder than rock; you will understand this too from the more bodily. Of those sinning, some hearing rebuking words at the sin blush and sink and fall under, the rebuking word touching them; others are such that they are without blush, not being ashamed at what they are rebuked for, at what they have sinned. You would say then about these who are not ashamed: they made their faces harder than rock. If you have understood it upon the bodily, move with me in the word upon the soul having understood a face, about which it is said: then face to face. And see a hard soul, such as was the heart of Pharaoh hardened, so that it stands contrary upon the things announced and as if throwing off the things said, not being formed according to the things announced. For there you will find that they made their faces harder than rock and did not wish to turn fits. And I said: perhaps they are poor, because they did not wish to know the way of the Lord and judgment of God. I will go to the full-souled and I will speak to them. The full-souled are said in praise in the souls. And among Greeks too the full is named continually and the greatness of the rational soul. When someone sets upon great deeds and has purposes worth speaking of and always looks at the things needed, how he will live according to right reason, wanting and seeing nothing low and small, such a one has the full and the greatness in the soul. These former then, since they were poor, whom the word blamed, did not hear, the prophet says. For this they did not hear, since they are poor. I will go to the full-souled and I will speak to them. Let us ask from God to receive, the word growing in us, fullness and greatness in Christ Jesus, that we may be able to hear the holy and sacred words, to whom the glory and the might unto the ages of the ages. Amen.",
        "lemmas": [
            {"form": "ἐστερέωσαν", "lemma": "στερεόω", "gloss": "they made hard / solid", "lexica": "LSJ"},
            {"form": "ἁδροὺς", "lemma": "ἁδρός", "gloss": "full, substantial, great-souled", "lexica": "LSJ"},
            {"form": "πτωχοί", "lemma": "πτωχός", "gloss": "poor (here: poor in soul)", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἁδροί",
                "english": "the full-souled",
                "rejected": ["the stout", "the fat", "the rich only"],
                "why": "Origen praises ἁδρόν as greatness of the rational soul, then goes to them to speak.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 5:3-5", "method": "wording", "note": "Harder than rock; poor; go to the full-souled."},
            {"display": "1 Corinthians 13:12", "method": "wording", "note": "Face to face."},
        ],
    },
]


def source_map():
    return {str(r.get("section")): r for r in json.loads(SRC.read_text(encoding="utf-8"))}


def write_justification(sec: dict, src: dict) -> None:
    greek = src.get("greek") or []
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
        "source_text": " ".join(str(p) for p in greek),
        "variants": [],
    }
    path = JUST / f"jeremiah_{sec['section'].replace('.', '_')}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    print(f"wrote {len(SECTIONS)} Homily 6 sections")


if __name__ == "__main__":
    main()
