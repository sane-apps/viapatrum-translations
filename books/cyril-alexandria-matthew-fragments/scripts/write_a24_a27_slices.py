#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a24..a27 (entries 93–108)."""
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
    if n <= 96:
        return "cyril-matt-frag-a24"
    if n <= 100:
        return "cyril-matt-frag-a25"
    if n <= 104:
        return "cyril-matt-frag-a26"
    return "cyril-matt-frag-a27"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(93, 109)}

PASS_A = {93: 'Custom to the humans the unmarried maidens, whenever they are toward hour of marriage, having-died to-mourn through the symbolic marriages; wherefore also flute-players were inside, if also against the command the Jewish then they-were-doing this the Jews.', 94: 'The disciples he-calls workers, whom few being he-sent into all the under heaven.', 95: "These the twelve disciples also the law was-prefiguring and the prophets were-proclaiming-beforehand. It-has-been-written at-least in Mosaic book: 'and you-will-take fine-flour and you-will-make it twelve loaves, and you-will-set them upon the table the pure before Lord, and you-will-set frankincense and salt'; for bread on-the-one-hand the from heaven having-come-down 'and life giving to the world' himself is the Christ, according to imitation but the toward him breads have-been-called also the blessed disciples; for partakers having-become of the nourishing us into life eternal they-nourish also themselves through the own writings those 'hungering and thirsting the righteousness'. Just-as but 'light' being 'the true' the savior light he-named them ('you' for, he-says, 'are the light of the world'); thus himself being 'the bread of the life' he-granted also to the disciples the in rank to-be-understood of the breads. And to-me see of the law the skillfulness. 'You-will-set' for, he-says, upon the breads 'frankincense and salt'. And the on-the-one-hand frankincense of fragrance is symbol, but the salts of minds and understanding. But there-were-in extremely both to the holy apostles; for fragrant was the life of them and at-least they-were-saying: 'of Christ fragrance we-are' to the Christ. But they-were toward this also all-understanding. Wherefore also they-heard: 'you are the salt of the earth'. But I-hear of the prophet David singing about them: 'there Benjamin younger in ecstasy, rulers of Judah leaders of them, rulers of Zebulun, rulers of Naphtali'; for almost from every tribe the from Israel chosen have-become the divine disciples and luminaries have-become ecumenical word having of life, humans hand-craftsmen having-become and sea-workers and fish-hunters, not of words having abundance of approved, but 'unlearned' on-the-one-hand 'in the word', rich but 'in the knowledge'. These the God was-showing also through voice of Jeremiah saying about the satan: 'woe the multiplying to him the not being of him, that suddenly will-arise the biting him and will-wake the plotters of you, and you-will-be into plunder to them'; for all on-the-one-hand the upon earth humans not being of him he-gathered the satan and own he-showed worshipers, but were-raised the plundering of him the vessels; for hunted of the apostolic teaching the net all the having-been-led-astray and they-brought-near to the God the under heaven.", 96: 'That it-is-necessary first to the Jews to-preach; for toward them had-been the promises, that from them was-about the Christ the according to flesh to-appear and whenever they-disobeyed, then into the nations to-go. But Samaritans he-joins to those from nations, since also from nations they-were according to race Babylonians being and having-settled the Judea. For just is toward Jews first to-be-preached the word, since also toward those the promises first, and that from them the Christ the according to flesh appeared. But when they-disobeyed, necessary was into the nations to-go. But he-joins to those from nations the Samaritans as from nations being also themselves and the Judea having-settled.', 97: 'But kingdom of heavens he-calls the through faith grace, the through spirit adoption the uniting to God the human.', 98: 'According to excess the word every forbids possession from gold until staff as greatest being hindrance toward virtue and piety; but the necessary food not he-forbids, so-that if it-was possible also without food to-live to us also this would he-have-forbidden.', 99: 'Not he-wishes place from place and house from house to-change them, in order that not grief may-happen to the first having-received nor suspicion they-may-receive of gluttony and easiness. But the dust being-shaken from the feet of them proof is of the useless toward them journey and of the toils, which they-endured through them. But equal to the Sodomites they-will-be-punished if-indeed those on-the-one-hand dishonored the angels, but these the apostles.', 100: 'Prudent to-be he-wishes them, in order that they-may-teach on-the-one-hand the of the piety dogmas unveiledly and through the not to-be-ignorant of the of the base malices, but if some may-come-upon not to-resist, but to-depart from them and not unreflectingly to-turn toward the to-suffer. But to serpents he-likens teaching, that it-is-necessary them sharp to-be toward flight if somehow some may-come-upon to-kill wanting, but to doves, since unremembering-of-evil the bird and loving-to-dwell always toward which it-was-accustomed places and turning-back upon the same, whenever the driving-out may-cease. He-teaches therefore the word, that not it-is-necessary wholly of the persecuting to-depart, but having-yielded toward a-little again upon the to-admonish them to-return, whenever the of the anger may-cease. Thus also to them the Christ did being-persecuted on-the-one-hand and withdrawing from the Judea and again returning.', 101: 'But the is-given, he-says, to some word, when it-is-beneficial to-defend, in order that through the confession they-may-be-benefited some and may-be-strengthened the church.', 102: 'But in itself the hour he-promised the dialectical to-give grace, in order that may-be-shown the of the spirit gift; for if before time he-had-given by the experience, it-was-being-thought to-be the matter of nature human and dexterity, not by all but they-were-about to-be-hated, but by many especially according to that time. Wherefore from the more he-said the by all, since those having-received the word were-loving them.', 103: 'For not to-fear them he-wishes, but the opposite, not by desire of the being-hoped ready to-hand-over themselves into death and to-harm those about-to from the preaching to-be-benefited. He-exhorts to the disciples from this to-flee of the city into the other and from that into another. But this he-says not teaching them to-fear, but not to-throw themselves into dangers and to-die easily and to-harm those about-to to-be-benefited through the preaching.', 104: 'But cities of the Israel he-says also of the faithful the assemblies, which until the consummation of the age are and not cease the teaching and the being-taught until the second appearing of the Lord. And they-seem to-live until then the disciples and evangelists since from the writings of them all teach.', 105: 'He-teaches patiently every kind to-bear of abuse and not above the master to-think.', 106: 'In time of the judgment all are-made-manifest; for not to abuses he-attends, but to the hearts.', 107: "About the in the to-preach boldness of the apostles also the marvelous Habakkuk foretold; 'they-will-open' for, he-says, 'bridles of them as' the 'eating poor secretly', that-is those formerly scarcely to-some and secretly speaking apostles and by the of the believing faith being-nourished these after these having-broken-through the having-been-set-upon them of the fear bridle of the of themselves voice they-will-fill the under heaven. But for-a-while since—what for he-says.", 108: 'The confessing, that God is the Christ, having-humbled himself is-about to-have the Christ confessing about him to the Father, that genuine he-is servant.'}

PASS_B = {93: ['It is a custom among people to mourn unmarried girls who die when they are at the age for marriage, with symbolic wedding rites. That is why flute-players were inside — even if the Jews were then doing this against the Jewish command.'], 94: ['He calls the disciples workers — few though they were — whom he sent into all the world under heaven.'], 95: ['The law also prefigured these twelve disciples, and the prophets proclaimed them beforehand. It is written in the Mosaic book: “Take fine flour and make it into twelve loaves, and set them on the pure table before the Lord, and set frankincense and salt on them.” For the bread that came down from heaven “and gives life to the world” is Christ himself; and by imitation of him the blessed disciples too are called breads. Having become sharers in the one who nourishes us unto eternal life, they also nourish, through their own writings, those who “hunger and thirst for righteousness.”', 'Just as the Savior, being “the true light,” named them light (“You are the light of the world”), so he himself, being “the bread of life,” also granted the disciples to be understood in the rank of the breads. See the skill of the law: “You shall set frankincense and salt on the breads.” Frankincense is a symbol of fragrance; salt, of mind and understanding. Both were present in the highest degree in the holy apostles. Their life was fragrant — they even said, “We are the fragrance of Christ” to Christ — and they were also all-understanding. That is why they also heard, “You are the salt of the earth.”', 'I hear the prophet David singing about them: “There Benjamin the younger in ecstasy, rulers of Judah their leaders, rulers of Zebulun, rulers of Naphtali.” For the divine disciples were chosen from almost every tribe of Israel and became worldwide luminaries holding a word of life — men who had been craftsmen, seafarers, and fishers, without a stock of polished words, “unlearned in speech” yet rich “in knowledge.”', 'God also showed these through Jeremiah’s voice, saying about Satan: “Woe to him who multiplies for himself what is not his, for suddenly those who bite him will rise, and your plotters will wake, and you will be plunder for them.” For Satan gathered all people on earth who were not his and made them his own worshipers; but those who plunder his vessels rose up. The net of the apostolic teaching caught all who had gone astray, and they brought the world under heaven near to God.'], 96: ['First one must preach to the Jews. The promises had been made to them, that from them Christ was going to appear according to the flesh; and when they disobeyed, then one must go to the nations. He joins the Samaritans to those from the nations, since they too were from the nations by race — Babylonians who settled Judea.', 'It is just that the word be preached to the Jews first, since the promises were first toward them, and since from them Christ appeared according to the flesh. But when they disobeyed, it was necessary to go to the nations. He joins the Samaritans to those from the nations as themselves also being from the nations and having settled Judea.'], 97: ['By “kingdom of heaven” he means the grace that comes through faith — the adoption through the Spirit that unites the human being to God.'], 98: ['The saying forbids every possession to excess — from gold down to a staff — as the greatest hindrance to virtue and piety. It does not forbid necessary food. If it were possible for us to live without food, he would have forbidden that too.'], 99: ['He does not want them to change from place to place and house to house, lest grief come to the first host, and lest they take on a suspicion of gluttony and easiness. The dust shaken from their feet is proof of a journey toward them that gained nothing, and of the toils they endured for them. They will be punished equally with the people of Sodom: those dishonored the angels; these, the apostles.'], 100: ['He wants them to be prudent: to teach the doctrines of piety openly, and, knowing the malice of the base, not to resist if some come against them, but to leave and not rush thoughtlessly toward suffering.', 'He likens them to serpents, teaching that they must be quick to flee if some come wanting to kill them; and to doves, since that bird does not remember evil, loves to stay in the places it is used to, and turns back to the same spot when the one driving it out stops.', 'So the word teaches that one must not leave the persecutors altogether, but yield for a little and return again to admonish them when the anger ceases. Christ himself did this with them: being persecuted, withdrawing from Judea, and returning again.'], 101: ['“It is given,” he says — a word is given to some when it is useful to make a defense, so that through the confession some may be helped and the church strengthened.'], 102: ['In that very hour he promised to give the grace of debate, so that the Spirit’s gift might be shown. If he had given it before the time of trial, the matter would have been thought a thing of human nature and skill. They were not going to be hated by absolutely everyone, but by many — especially at that time. So from the greater part he said “by all,” since those who received the word loved them.'], 103: ['He does not want them to be cowardly — rather the opposite: not, out of longing for the things hoped for, to hand themselves over ready to death and so harm those who are about to be helped by the preaching.', 'He urges the disciples to flee from this city to another, and from that to another. He says this not teaching them to fear, but not to throw themselves into dangers, die lightly, and harm those who are about to be helped through the preaching.'], 104: ['By “cities of Israel” he also means the assemblies of the faithful, which last until the consummation of the age. Teachers and learners do not cease until the Lord’s second appearing. And the disciples and evangelists seem to live until then, since from their writings all teach.'], 105: ['He teaches them to bear every kind of abuse patiently, and not to think themselves above the Master.'], 106: ['In the time of judgment everything is made plain. He does not attend to abuses, but to the hearts.'], 107: ['About the apostles’ boldness in preaching, marvelous Habakkuk also foretold: “They will open their bridles like a poor man eating in secret” — that is, the apostles who at first scarcely spoke to a few, and in secret, fed by the faith of believers, later broke the bridle of fear set on them and will fill the world under heaven with their own voice. For now — since — what does he say?'], 108: ['The one who confesses that Christ is God, having humbled himself, will have Christ confessing about him to the Father that he is a genuine servant.']}

LEMMAS = {93: [{'form': 'αὐληταί', 'lemma': 'αὐλητής', 'gloss': 'flute-player', 'lexica': 'LSJ'}], 94: [], 95: [{'form': 'σεμίδαλιν', 'lemma': 'σεμίδαλις', 'gloss': 'fine flour', 'lexica': 'LSJ'}], 96: [], 97: [{'form': 'υἱοθεσίαν', 'lemma': 'υἱοθεσία', 'gloss': 'adoption as son', 'lexica': 'NT'}], 98: [], 99: [], 100: [{'form': 'ἀμνησίκακον', 'lemma': 'ἀμνησίκακος', 'gloss': 'not remembering evil', 'lexica': 'LSJ'}], 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [{'form': 'παρρησίας', 'lemma': 'παρρησία', 'gloss': 'boldness of speech', 'lexica': 'NT'}], 108: []}

CHOICES = {93: [], 94: [], 95: [{'term': 'ἄρτοι', 'english': 'breads / loaves', 'rejected': ['cakes'], 'why': 'Twelve-loaf typology for the apostles.'}], 96: [], 97: [], 98: [], 99: [], 100: [], 101: [], 102: [], 103: [], 104: [], 105: [], 106: [], 107: [{'term': 'ἐπειδή–τί', 'english': 'since — what (breaks off)', 'rejected': ['smooth invented continuation'], 'why': 'Copy-text breaks mid-phrase; disclose the break, do not invent Greek.'}], 108: []}

ALLUSIONS = {93: [{'reference': 'Matthew 9:23', 'reason': 'Flute-players at the girl’s death.', 'certainty': 'clear'}], 94: [{'reference': 'Matthew 9:38', 'reason': 'Ask the Lord of the harvest for workers.', 'certainty': 'clear'}], 95: [{'reference': 'Matthew 10:2', 'reason': 'The twelve named.', 'certainty': 'clear'}, {'reference': 'Leviticus 24:5-7', 'reason': 'Twelve loaves; frankincense.', 'certainty': 'clear'}, {'reference': 'John 6:33-35', 'reason': 'Bread from heaven; bread of life.', 'certainty': 'clear'}, {'reference': 'Matthew 5:6', 'reason': 'Hunger and thirst for righteousness.', 'certainty': 'clear'}, {'reference': 'Matthew 5:13-14', 'reason': 'Salt of the earth; light of the world.', 'certainty': 'clear'}, {'reference': '2 Corinthians 2:15', 'reason': 'Fragrance of Christ.', 'certainty': 'clear'}, {'reference': 'Psalm 68:27', 'reason': 'Benjamin, Judah, Zebulun, Naphtali.', 'certainty': 'clear'}, {'reference': 'Acts 4:13', 'reason': 'Unlearned in speech.', 'certainty': 'possible'}, {'reference': 'Habakkuk 2:6', 'reason': 'Woe to him who multiplies what is not his.', 'certainty': 'possible'}], 96: [{'reference': 'Matthew 10:5-6', 'reason': 'Go not to Gentiles or Samaritans first.', 'certainty': 'clear'}], 97: [{'reference': 'Matthew 10:7', 'reason': 'Kingdom of heaven has drawn near.', 'certainty': 'clear'}], 98: [{'reference': 'Matthew 10:9-10', 'reason': 'No gold, silver, staff.', 'certainty': 'clear'}], 99: [{'reference': 'Matthew 10:11-15', 'reason': 'Stay in one house; shake dust.', 'certainty': 'clear'}, {'reference': 'Genesis 19', 'reason': 'Sodom and the angels.', 'certainty': 'clear'}], 100: [{'reference': 'Matthew 10:16', 'reason': 'Wise as serpents, innocent as doves.', 'certainty': 'clear'}], 101: [{'reference': 'Matthew 10:19', 'reason': 'It will be given what to speak.', 'certainty': 'clear'}], 102: [{'reference': 'Matthew 10:19-22', 'reason': 'Spirit speaks; hated by all.', 'certainty': 'clear'}], 103: [{'reference': 'Matthew 10:23', 'reason': 'Flee to another city.', 'certainty': 'clear'}], 104: [{'reference': 'Matthew 10:23', 'reason': 'Cities of Israel until the Son of Man comes.', 'certainty': 'clear'}], 105: [{'reference': 'Matthew 10:25', 'reason': 'If they called the master Beelzebul.', 'certainty': 'clear'}], 106: [{'reference': 'Matthew 10:26', 'reason': 'Nothing covered that will not be revealed.', 'certainty': 'clear'}], 107: [{'reference': 'Matthew 10:27', 'reason': 'Proclaim on the housetops.', 'certainty': 'clear'}, {'reference': 'Habakkuk 3:14', 'reason': 'Poor eating in secret / bridles.', 'certainty': 'possible'}], 108: [{'reference': 'Matthew 10:32', 'reason': 'Confess me before people.', 'certainty': 'clear'}]}

def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(93, 109):
        src = BY[n]
        a, b = PASS_A[n], " ".join(PASS_B[n])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {n}")
        claim = claim_for(n)
        ed = src["fragment"]
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
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract.",
                    "Section id = source array order (1-based).",
                    "IA OCR not reading text.",
                ],
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a24a27.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a24a27.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a24",
                        "cyril-matt-frag-a25",
                        "cyril-matt-frag-a26",
                        "cyril-matt-frag-a27",
                    ],
                    "sections": "93-108",
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
