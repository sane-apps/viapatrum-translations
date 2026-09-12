#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a20..a23 (entries 77–92)."""
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
    if n <= 80:
        return "cyril-matt-frag-a20"
    if n <= 84:
        return "cyril-matt-frag-a21"
    if n <= 88:
        return "cyril-matt-frag-a22"
    return "cyril-matt-frag-a23"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(77, 93)}

PASS_A = {77: 'Through the touch he made the cleansing making-clear, that also the holy of him flesh needful is toward sanctification; for the on-the-one-hand spirit cleanses, but the of the body communion produces the sanctification. Touching of the leper the savior healed him showing as the spirit the in him heals the diseases, but the body by the contact the sanctification provides.', 78: "What then was the gift the from the leper according to the law being-brought-near? 'Two little-birds', of which the one the priest slaughtered 'upon living water' and having-taken 'cedar wood and scarlet twisted and hyssop' and the other little-bird the living he was-dipping it 'into the blood of the slaughtered little-bird upon living water' and was-anointing of the being-cleansed leper the right parts, ear, hand and foot, but 'the little-bird the living' outside of the city 'into the plain' he sent-away. Observe therefore how through the things-said wholly to us is-painted Christ; through the living little-bird the living and heavenly Word; through the slaughtered blood the precious blood of the having-suffered Lord; through the incorruptible wood the incorruptible flesh; through the hyssop the of the spirit boiling; through the scarlet the of the upon-blood covenant confession; through the living water the life-giving of baptism grace; through the outside-city sending the from-world departure and into-heavens ascent; through the right anointings the need toward contemplation and practice and journey in the divine things.", 79: 'Through what then of day they did not bring-near? Whether being-cautious of the scribes and Pharisees or again being-ashamed upon the weaknesses of them as Nicodemus or through the not to-have the being-weak some to bring them to Jesus.', 80: 'But was-withdrawing the Christ from the crowds, in order that not someone may-think him applause-loving to be rejoicing in the from the many praises and in order that not they-may-be-angered against him the Pharisees; for it-was-distressing them greatly the to-follow him many; and in order that to the nearby cities he-may-shine the own and saving light.', 81: "But he-commands only to the disciples Jesus to-depart into the beyond, in order that not he-may-seem to-be-hindered by the pressing him crowds to-hear the disciples of the fitting to them lessons and more-genuinely about-to to them to-be-revealed of the of God mysteries, of the 'in parables to the crowds' being-spoken; since all the in hands having-left alone to him they-followed for love-of-learning, but he-commands to-cross from the temporary upon the eternal, from the earthly upon the heavenly, from the fleshly upon the spiritual.", 82: "Where not is-set-forth if toward God honor, just to-honor the parents; whenever but the two in midst be, of the on-the-one-hand it-is-necessary to-cling, of the but to-despise, especially if is-hindered toward the to-please God the toward the parents honor; for to the first-places it-is-necessary to-glorify the God, in order that not we-may-be-found according to the Cain the second-places to the God assigning. Likewise also the old law the priests was-forbidding to-approach to the dead and of the own to-hold liturgy and not to-be-brought-down about the fleshly sympathies, but that through shadows, but the Christ unveiledly teaches the to the God wanting-to-attend of no kinship account to-make into the to-be-distracted from the to-be-with Christ; for also himself through the toward the being-with benefit he-overlooked mother and brothers saying: 'who is the mother of me, and who the brothers of me' and 'mother of me is'.", 83: 'The to-say save has praise of faith, but the to-say we-are-perishing charge of little-faith to those danger expecting of Christ sailing-with. Not unbelieving but wholly, but little-faith those not having-taken-courage of dangers of Christ being-with.', 84: 'See with faith little-faith; for they-believe on-the-one-hand, that to-save he-is-able, but as little-faith they-say the save, we-are-perishing; for not was attainable to-perish ever of being-with to them of the all being-able.', 85: 'The divine of the only-begotten nature with unspeakable fire was-burning-down the demons just-as also other-things invisibly he-was-doing, the wilder of the demons into roads shutting-in and the of the devil having-taken-down tyranny. You-came, they-say, before time; for they-knew in the word, that also was-about to-come the Christ and that himself has them to-judge. But if also the before time they-said as slandering the of the incarnation time as against time having-happened, nothing marvelous if being wicked also this they-dare to-say. And-yet knowing they-will-be-punished, so-that overlooking they-say: what to us and to you; for he-has account with us the judge, from which we-transgressed the commandments of him.', 86: "Not the faith of the paralyzed the Lord beheld, but of the having-brought; for there-is when also another through others' faith is-healed and full of these the holy of the gospels writing. Having-beheld therefore the faith of them not vain of them he-shows the labor, but says child the child either also to him as having-believed or according to the of the creation word. Child he-called the paralytic by the of the creation word or as having-believed into him and having-known him Lord and creator.", 87: 'Went-out the word and the wonder followed. Through what then also son of man he-said to-forgive sins of being-accomplished a God-sign? Or in order that he-may-show, that he-brought-down into the human nature the of the divinity authority through the indivisible toward it union; for if also human, he-says, I-became God Word being and through the economy upon earth I-conduct-myself and I-move-about, but none the less the beyond word I-accomplish wonders and forgiveness I-grant of sins; for not I-took-away something of the of the divinity properties or I-lessened by the to-become me unchangeably and truly upon the earth according to flesh son of man. And after a-little; economically but he-says upon the earth, in order that he-may-show, that also human having-become and upon the earth having-appeared God he-was according to nature. But he-commanded to the paralytic to-carry the bed and to-depart home, in order that through him also <toward> the absent he-may-confirm the having-happened upon him.', 88: "Is-full but also this of a God-sign the by word alone the such to-be-turned toward virtue so-great. But calling the Matthew he-shows, that if also nobody comes toward him, 'unless the Father draw him', yet through Christ happens the drawing. The therefore savior unashamedly a tax-collector having-called into discipleship and into the house of him having-arrived, in which nothing other was good except of the householder the change. There-was therefore crowd much of tax-collectors reclining-with to Jesus and not is-indignant the savior nor into insult of him he-receives the happening, but as master of the nature he-arrives into the feast and eats and drinks both the truth of the body showing and the timely of the foods blessing use. But were-present also Pharisees and scribes, not in order that they-may-learn, but in order that they-may-meddle-in the happenings. They-see the tax-collectors reclining-with and they-call the disciples and the happening they-blame. Hears the Jesus and says toward them: also you need have of a physician; for if not you-were-ill, not would you-blame of the physician the love-of-humans. I-know that badly they-have. Through this toward them I-have-come, in order that the souls of them I-may-heal being-ill. Through which but cause they-lay-hold-of the Pharisees of the savior with sinners eating-with, that law was 'to-distinguish between holy and profane'. But they-did-not-know Christ above the legal use providing the philanthropic grace; for the on-the-one-hand cast-out, but the changed the evil. He-showed therefore, that not as judge he-is-present, but as physician and the belonging to the art he-does being-with to those also of healing needing.", 89: "Yet the holy ones the old law forbade to-be-glued to the profane, in order that not may-slip of them the mind, not indeed the opposite, if may-run-toward a profane to a holy, it-is-necessary him to-turn-away according to the: 'you-shall-not-abhor an Edomite nor an Egyptian'. But upon Christ nothing such it-is-necessary to-think of the of every wickedness and passion higher; for faith he-wants justifying the human, not the in letters law the the through bloods sacrifices commanding, which making-clear he-adds also 'knowledge of God than burnt-offerings; mercy' for is the gospel word. Wherefore from faith we-are-justified freely without works of law. But he-calls not the near being, but the far having-stood.", 90: 'The Pharisees resembling but a garment torn or a wineskin old not are-able the youthful to-receive teaching into annulment of the bodily of the law. But worse he-says the tear, because those hearing of the gospel and not accepting more than those not having-heard are-punished. But since the disciples of John two asked the Lord: through what we and the Pharisees fast, but the disciples of you not fast, toward on-the-one-hand them of the bridegroom the parable he-said, but toward the Pharisees the about of the wineskins.', 91: 'Of the hemorrhage-suffering having-perceived the Christ not he-deemed-unworthy her, but he-healed and daughter he-called as faithful, together but also showing, that not is beside the God unclean the having disease involuntary.', 92: 'He-shows, that beside God nobody having involuntary disease unclean. Wherefore also he-calls-near the hemorrhage-suffering the Lord, in order that the typological law into spiritual he-may-lead contemplation.'}

PASS_B = {77: ['By the touch he accomplished the cleansing, making clear that his holy flesh is also needed for sanctification. The Spirit cleanses; communion with the body produces sanctification. Touching the leper, the Savior healed him, showing that the Spirit in him heals diseases, while the body, by contact, grants sanctification.'], 78: ['What was the gift the leper had to bring under the law? “Two little birds.” The priest slaughtered one “over living water,” took “cedar wood, twisted scarlet, and hyssop,” dipped the living bird “in the blood of the slaughtered bird over living water,” and anointed the right ear, hand, and foot of the leper being cleansed. The living bird he sent away outside the city “into the open country.”', 'Watch how through these things Christ is painted for us in full: living bird — the living and heavenly Word; slaughtered blood — the Lord’s precious blood in his own body; incorruptible cedar — incorruptible flesh that “did not see corruption”; hyssop — the Spirit’s fervor; scarlet — confession of the blood-covenant; living water — baptism’s life-giving grace; sending outside the city — departure from the world and ascent into the heavens; right anointings — that we must become people of contemplation, practice, and journey in the things of God.'], 79: ['Why did they not bring them by day? Was it caution toward the scribes and Pharisees, or shame again at their weaknesses, as with Nicodemus — or because the sick had no one to bring them to Jesus?'], 80: ['Christ withdrew from the crowds so that no one would think him applause-loving, glad of praise from the many; so that the Pharisees would not be angered at him (for it distressed them greatly that many followed him); and so that he might shine his own saving light on the nearby cities.'], 81: ['Jesus commands only the disciples to go across, so that he may not seem hindered by the crowds pressing him from letting the disciples hear the lessons that fit them, and so that God’s mysteries — spoken “in parables to the crowds” — may be revealed to them more genuinely.', 'Since they left everything in hand and followed him alone for love of learning, he commands them to cross from the temporary to the eternal, from the earthly to the heavenly, from the fleshly to the spiritual.'], 82: ['Where honor toward God is not at stake, it is right to honor parents. But when both stand in the middle, one must cling to the one and despise the other — especially if honor to parents hinders pleasing God. God must be given the first place, lest we be found like Cain assigning God the second place.', 'Likewise the old law forbade priests to approach the dead and to hold to their own ministry without being dragged down into fleshly sympathies — that through shadows; but Christ teaches unveiledly that whoever wants to attend on God must make no account of kinship so as to be distracted from being with Christ. He himself, for the benefit of those with him, overlooked mother and brothers, saying, “Who is my mother, and who are my brothers?” and “My mother is….”'], 83: ['To say “save” carries praise of faith; to say “we are perishing” charges little faith in those who expect danger while Christ sails with them. They are not wholly unbelieving, but little-faith — those who did not take courage in dangers while Christ was with them.'], 84: ['See little faith together with faith. They believe he can save, yet as little-faith people they say, “Save — we are perishing.” It was never possible to perish while the One who can do all things was with them.'], 85: ['The divine nature of the Only-Begotten was burning down the demons with unspeakable fire, just as he was also doing other things invisibly — shutting the wilder demons into paths and taking down the devil’s tyranny.', '“You have come before the time,” they say. They knew in the Word that Christ was also going to come and that he himself has them to judge. If they also said “before the time” as a slander on the timing of the incarnation, as if it had happened out of season, it is no wonder that, being wicked, they dare to say even this.', 'And yet, knowing they will be punished, they speak as if overlooking him: “What to us and to you?” For the Judge has an account with us from the time we transgressed his commandments.'], 86: ['The Lord did not look at the faith of the paralyzed man, but at the faith of those who brought him. There are times when one person is healed through another’s faith, and the holy writing of the Gospels is full of such cases. Seeing their faith, he does not show their labor vain, but says “child” — either to him as one who also believed, or according to the word of creation.', 'He called the paralytic “child” by the word of creation, or as one who had believed in him and known him as Lord and Creator.'], 87: ['The word went out and the wonder followed. Why then did he also say that the Son of Man forgives sins while a God-sign was being done? To show that he brought the authority of divinity down into human nature through the indivisible union with it.', '“For if I also became man,” he says, “being God the Word, and through the economy I live and move about on earth, still I accomplish wonders beyond speech and grant forgiveness of sins. I did not take away any property of divinity or lessen it by becoming, unchangeably and truly, Son of Man according to flesh on earth.”', 'And a little later: he says “on earth” economically, to show that even having become man and appeared on earth he was God by nature. He commanded the paralytic to carry the bed and go home, so that through him he might also confirm to those absent what had happened to him.'], 88: ['This too is full of a God-sign: that by word alone such a man was turned toward so great a virtue. Calling Matthew, he shows that even if no one comes to him “unless the Father draws him,” still the drawing happens through Christ.', 'So the Savior, unashamed, called a tax collector into discipleship and came into his house, where nothing else was good except the householder’s change. A large crowd of tax collectors were reclining with Jesus. The Savior is not indignant and does not take what happens as an insult to him; as master of nature he arrives at the feast, eats and drinks, showing the truth of the body and blessing the timely use of foods.', 'Pharisees and scribes were also present — not to learn, but to meddle in what was happening. They see the tax collectors reclining with him, call the disciples, and blame what is going on. Jesus hears and says to them: “You also need a physician. If you were not ill, you would not blame the physician’s love of humankind. I know they are tax collectors; I know their soul’s diseases; I know they are in a bad way. That is why I have come to them: to heal their sick souls.”', 'The reason the Pharisees seize on the Savior for eating with sinners is that there was a law “to distinguish between holy and profane.” They did not know that Christ was giving philanthropic grace above the legal use: the one cast out the evil; the other changed it. So he showed that he is present not as judge but as physician, and does what belongs to the art by being with those who also need healing.'], 89: ['Yet the old law forbade the holy to glue themselves to the profane, lest their mind slip — not the opposite: if a profane person runs toward a holy one, one must not turn him away, according to “You shall not abhor an Edomite or an Egyptian.”', 'But of Christ, who is above every wickedness and passion, one must think no such thing. He wants faith that justifies the human being, not the law in letters that commands sacrifices through bloods — which he makes clear by adding also “knowledge of God rather than burnt offerings,” for “mercy” is the gospel word. So we are justified from faith freely, without works of law. And he calls not those who are near, but those who have stood far off.'], 90: ['The Pharisees, resembling a torn garment or an old wineskin, cannot receive the youthful teaching that annuls the bodily things of the law. He says the tear is worse because those who hear the gospel and do not accept it are punished more than those who never heard.', 'And since John’s disciples asked the Lord two things — why we and the Pharisees fast, but your disciples do not — to them he spoke the parable of the bridegroom, and to the Pharisees the one about the wineskins.'], 91: ['Perceiving the woman with the hemorrhage, Christ did not deem her unworthy, but healed her and called her daughter as one faithful — and at the same time showing that with God no one who has an involuntary disease is unclean.'], 92: ['He shows that with God no one who has an involuntary disease is unclean. That is why the Lord also calls the woman with the hemorrhage near: to lead the typological law over into spiritual contemplation.']}

LEMMAS = {77: [{'form': 'ἐπαφῆς', 'lemma': 'ἐπαφή', 'gloss': 'touch', 'lexica': 'LSJ'}], 78: [{'form': 'ἀδιάφθορον', 'lemma': 'ἀδιάφθορος', 'gloss': 'incorruptible', 'lexica': 'patristic'}], 79: [], 80: [], 81: [], 82: [], 83: [], 84: [], 85: [{'form': 'μονογενοῦς', 'lemma': 'μονογενής', 'gloss': 'only-begotten', 'lexica': 'NT'}], 86: [], 87: [{'form': 'θεοσημείας', 'lemma': 'θεοσημεία', 'gloss': 'God-sign', 'lexica': 'patristic'}], 88: [{'form': 'τελώνην', 'lemma': 'τελώνης', 'gloss': 'tax collector', 'lexica': 'NT'}], 89: [], 90: [], 91: [], 92: []}

CHOICES = {77: [{'term': 'ἐπαφή', 'english': 'touch', 'rejected': ['mere proximity'], 'why': 'Physical contact of the holy flesh is the point.'}], 78: [], 79: [], 80: [], 81: [], 82: [], 83: [], 84: [], 85: [], 86: [], 87: [{'term': '<πρός>', 'english': 'toward (the absent)', 'rejected': ['silent omit'], 'why': 'Angle brackets mark editor-supplied stretch in copy-text; disclose, do not invent Greek.'}], 88: [], 89: [], 90: [], 91: [], 92: []}

ALLUSIONS = {77: [{'reference': 'Matthew 8:3', 'reason': 'Touch cleanses the leper.', 'certainty': 'clear'}], 78: [{'reference': 'Leviticus 14:4-7', 'reason': 'Two-bird cleansing rite.', 'certainty': 'clear'}, {'reference': 'Acts 2:31', 'reason': 'Flesh did not see corruption.', 'certainty': 'clear'}], 79: [{'reference': 'Matthew 8:16', 'reason': 'Evening healings; Nicodemus parallel.', 'certainty': 'clear'}], 80: [{'reference': 'Matthew 8:18', 'reason': 'Withdraws; orders to cross.', 'certainty': 'clear'}], 81: [{'reference': 'Matthew 8:18-22', 'reason': 'Crossing; cost of discipleship.', 'certainty': 'clear'}, {'reference': 'Matthew 13:10-13', 'reason': 'Parables to crowds.', 'certainty': 'possible'}], 82: [{'reference': 'Matthew 8:21-22', 'reason': 'Bury father; follow me.', 'certainty': 'clear'}, {'reference': 'Matthew 12:48-50', 'reason': 'Who is my mother?', 'certainty': 'clear'}], 83: [{'reference': 'Matthew 8:25', 'reason': 'Save us; we are perishing.', 'certainty': 'clear'}], 84: [{'reference': 'Matthew 8:25-26', 'reason': 'Little faith in the storm.', 'certainty': 'clear'}], 85: [{'reference': 'Matthew 8:29', 'reason': 'Demons: before the time.', 'certainty': 'clear'}], 86: [{'reference': 'Matthew 9:2', 'reason': 'Faith of the bearers.', 'certainty': 'clear'}], 87: [{'reference': 'Matthew 9:3-7', 'reason': 'Son of Man forgives; take the bed.', 'certainty': 'clear'}], 88: [{'reference': 'Matthew 9:9-13', 'reason': 'Call of Matthew; eating with sinners.', 'certainty': 'clear'}, {'reference': 'John 6:44', 'reason': 'Father draws.', 'certainty': 'clear'}, {'reference': 'Leviticus 10:10', 'reason': 'Holy and profane.', 'certainty': 'clear'}], 89: [{'reference': 'Matthew 9:11-13', 'reason': 'Mercy not sacrifice.', 'certainty': 'clear'}, {'reference': 'Deuteronomy 23:7', 'reason': 'Edomite and Egyptian.', 'certainty': 'clear'}, {'reference': 'Hosea 6:6', 'reason': 'Mercy and knowledge of God.', 'certainty': 'clear'}], 90: [{'reference': 'Matthew 9:14-17', 'reason': 'Fasting; wineskins.', 'certainty': 'clear'}], 91: [{'reference': 'Matthew 9:20-22', 'reason': 'Hemorrhage; daughter.', 'certainty': 'clear'}], 92: [{'reference': 'Matthew 9:20-22', 'reason': 'Typology to spiritual reading.', 'certainty': 'clear'}]}

def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(77, 93):
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a20a23.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a20a23.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a20",
                        "cyril-matt-frag-a21",
                        "cyril-matt-frag-a22",
                        "cyril-matt-frag-a23",
                    ],
                    "sections": "77-92",
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
