#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a32..a35 (entries 125–140)."""
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
    if n <= 128:
        return "cyril-matt-frag-a32"
    if n <= 132:
        return "cyril-matt-frag-a33"
    if n <= 136:
        return "cyril-matt-frag-a34"
    return "cyril-matt-frag-a35"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(125, 141)}

PASS_A = {125: 'According to different conceptions the of God knowledge; of creator, by-which he-created, of judge <by-which he-judged and the others. But these all clear, to-whom ever the Son> may-reveal, not otherwise being Son of God. <Therefore> who having-taken authority child to-become when on-the-one-hand he-has not he-knew, not he-has the Father; but when he-becomes of Jesus having-revealed as to-brother he-will-know.', 126: 'Just-as therefore the Father is-said to-have-made the all, although through the Son all making, thus also he-is-said to the Son all to-hand-over him having power and through him ruling of the all and being-with to him. Yet even if as human authority to-receive economically he-is-said as not having-been-by-nature of human nature to-master, not even this outside of the reasonable.', 127: "The seeing the Son the of the Father image having in himself him sees the Father. But he-reveals the Father as in prototype himself to the Father appearing, showing-under but again in own form the archetype. But these in-a-God-befitting-way one-must-think. But since he-said all to me were-handed-over, in-order-that not he-may-seem of other tribe to-be and beside the Father lesser, he-added this, in-order-that he-may-show the of himself nature ineffable and incomprehensible being as the of the Father; for only the divine nature of the Trinity itself recognizes. Alone the Father knows the Son the own the of the of himself nature fruit, alone the divine offspring recognizes the from whom he-was-born alone the holy Spirit knows 'the depths of the God', which is the thoughts of the Father and of the Son.", 128: "The therefore having-heard of the call and having-drawn-near and having-been-joined to the having-commanded, this one rests. Having-stood-away, he-says, of the sin-loving mind and of the flesh-loving and being-turned upon the of praise worthy deeds draw-near to me, in-order-that you-may-become 'of divine sharers nature' and of holy Spirit partakers. But all he-calls and not only those from Israel as of all creator and Lord and laboring on-the-one-hand he-says the Jews the not being-able to-bear the legal yoke, having-been-burdened the idolaters the through the devil having-been-loaded-down and by the multitude of the sins being-weighed-down. You therefore, he-says, O Jews, nod toward the truth and recognize me the your guardian and master and from-near of the approach the gain receiving. For I-release you of the under the law slavery, in which much you-endure labor, neither easily to-accomplish it being-able and greatest of the sins 'the burden' to yourselves preparing, by-as-much more to-keep it-was-fitting you consistent with the law practicing.", 129: 'Light is the yoke of the Christ, since not he-punishes us just-as the law the sinless demanding and passionless, but in simple words he-has the promise and the of the virtue outline.', 130: 'Where on-the-one-hand nothing happens great and noble, they-are-quiet, but where they-see some being-saved, also of all they-are more-burdensome; thus enemies of the of the humans they-are salvation and of the sacred writings unknowledgeable. For if other beside the first covenant is the new the through Jeremiah having-been-proclaimed, it-is-necessary wholly also laws not the ancient to-use, but the new. But the Pharisees this to-understand not having-wished lie-in-wait to the holy apostles and they-say about them to the Christ: look, to the legal commands opposing we-see those by you being-trained; for of the law commanding to-rest on Sabbath and of nothing at-all to-touch of labor they-rub with the hands ears-of-grain the disciples. But you yourself say to me, O Pharisee, the Sabbath to yourself table having-set not you-break the bread? Why therefore others you-blame? But how also the savior about them apologizes?', 131: 'Impious being the Pharisees were-pretending the piety, in-order-that the pious they-may-destroy. Wherefore also the Christ to-slander they-were-attempting and the of him disciples seeing them being-made-bright by the wonders.', 132: 'Since, he-says, not in the ruler of the demons I-cast-out the demons as he-showed having-said, that every kingdom against itself having-been-divided is-dissolved and is-destroyed, in the power of the Spirit then I-cast-out them and through this has-drawn-near the of the God kingdom.', 133: 'But strong he-calls the devil not as by-nature this being, but the of him tyranny he-shows, which from the our slackness he-acquired; but I-plunder him, not allowing to-have worshipers the humans, but into knowledge of the God persuading to-come. How therefore ally to me will-he-become against himself?', 134: 'Whenever someone against human was-sinning, possible was on-behalf of him to-beseech the God, but whenever against God the humans were-blaspheming, not it-was-allowed on-behalf of them to-beseech. Yet since as human being-seen the of the God Son, even if by-nature God he-was, not very-much to the senseless he-was-recognized, he-gives sometimes to those from ignorance sinning against him forgiveness, but to those against the Spirit perpetual he-says the punishment to-be-brought.', 135: "Spirit saying whole the of the Trinity divinity; yet is-given to those repenting through the of the Spirit grace forgiveness. But the greatness wanting to-show the Christ of the sin, thus he-said, since not there-is sin unforgivable beside God in those genuinely and according to worth repenting. Spirit saying whole the of the Trinity divinity he-says; yet is-given to those repenting through the of the Spirit grace being-baptized forgiveness. But the greatness wanting to-show the Christ of the sin he-said this; for if also custom to the God often either here only to-demand accounts the having-sinned not indeed also there according to the 'not will-avenge Lord twice upon the same', or to-forbear on-the-one-hand in the now age, not indeed also from-there to-give forgiveness, but upon of such indelible and unforgivable and here and there he-says the punishment.", 136: 'Whenever he-says treasure, the multitude he-indicates of the in the soul lying. But in-order-that not they-may-say some that by-nature they-have-been-born wicked the humans, upon of the Pharisees this he-showed, that possible the same and one human sometimes on-the-one-hand good to-become, but sometimes wicked, saying: the good human from the overflow of the heart of him speaks, likewise also the wicked.', 137: 'Even if he-said the Lord, that wicked being not they-are-able not wicked to-speak, not as by-nature being of them wicked this he-said, but as from much of the senselessness having-been-overcome by the evil. But if also he-said the Lord, that wicked being not they-are-able good to-speak, not as by-nature being wicked this he-said, but from of them voluntary movement.', 138: "Since the having-happened signs, they-say, of demons were, which upon only of the earth he-makes the appearances, make also you from the your power sign from heaven; for another evangelist clearly said, that 'from heaven' they-were-asking him sign to-make, which to the divine power it-was-fitting to-make. But this they-were-saying as not being-able of him to-make something of the God-befitting being-blind in the mind; for the to-open eyes of blind and dead to-raise and to-sea and winds to-rebuke of only authority God-befitting.", 139: "But wicked as the excellent of the mind spending not about love-of-God, but about the to-do something and to-say against God. But adulteress he-called also the former and the present unbelief showing; for neither to the Father they-believed and of him of the Christ they-stood-away of the having-wedded the humanity and having-betrothed according to the humanity through the having-been-said: 'and I-will-betroth you to myself into the age', but they-were-glued to the satan the of the intelligible fornication manner calling. He-shows himself again to the Father—the sign of Jonah the prophet.", 140: 'So-that <if> as type of Christ Jonah is-taken, not according to all he-is-taken, for-example he-was-sent to the Ninevites to-preach, but he-sought to-flee from face of the God and hesitating he-is-seen toward mission. Has-been-sent also from the God and Father the Son preaching to the nations, but not unwilling he-was into service. He-was-urging the sailing-with the prophet to-throw him into the sea, but he-was-swallowed also by whale, then also he-was-given-out three-day and after this he-went into Nineveh and he-has-fulfilled the service, but he-has-been-grieved not moderately of God having-pitied the Ninevites. He-endured also the Christ willingly the death, he-remained in the heart of the earth, he-rose-again and after this he-went into the Galilee and of the toward the nations preaching he-was-commanding to-make the beginning, yet not he-has-been-grieved being-saved seeing those having-been-called into knowledge. Therefore just-as the bees meadows and flowers flying-around the useful always they-gather toward the of the honeycombs construction, thus it-is-necessary also us the God-inspired searching scripture the accomplishing into clarification of the of Christ mysteries always to-collect and to-compose and the word to-accomplish unreproved.'}

PASS_B = {125: ['Knowledge of God comes under different aspects: as Creator, by which he created; as Judge, <by which he judged — and the rest. All these become clear to anyone to whom the Son> reveals them, and only if that person is God’s Son in no other sense. <So> the one who has received authority to become a child, when he has it and has not yet come to know, does not yet have the Father; but when he becomes such, once Jesus has revealed it, he will know as a brother.'], 126: ['Just as the Father is said to have made all things, though he makes all things through the Son, so he is also said to hand all things over to the Son while himself having power, ruling the universe through him, and being with him. And even if, as man, he is said economically to receive authority — since human nature is not of itself master — that too is not unreasonable.'], 127: ['The one who sees the Son, who has the Father’s image in himself, sees the Father himself. He reveals the Father as himself appearing to the Father in the prototype, while again showing the archetype under his own form. These things must be thought of in a way worthy of God.', 'Since he said, “All things have been handed over to me,” so that he would not seem to be of another kind and lesser beside the Father, he added this to show that his own nature is ineffable and incomprehensible, like the Father’s. For only the divine nature of the Trinity knows itself. The Father alone knows the Son, his own fruit of his nature; the divine Offspring alone knows the One from whom he was born; the Holy Spirit alone knows “the depths of God,” that is, the thoughts of the Father and of the Son.'], 128: ['So the one who has heard the call, drawn near, and clung to the One who commanded rests. “Stand away,” he says, “from a sin-loving mind and love of the flesh, turn to deeds worthy of praise, and draw near to me, so that you may become ‘sharers in the divine nature’ and partakers of the Holy Spirit.” He calls all, not only those from Israel, as Creator and Lord of all.', 'By “those who labor” he means the Jews, who cannot bear the yoke of the law; by “those who are burdened,” the idolaters, weighed down by the devil and heavy with a mass of sins. “So you, Jews,” he says, “lean toward the truth, recognize me as your guardian and master, and take the gain of approaching near. For I release you from slavery under the law, in which you endure much toil — unable to finish it easily, and preparing for yourselves the greatest ‘burden’ of sins, the more you must keep when living in line with the law.”'], 129: ['Christ’s yoke is light, because he does not punish us as the law does, demanding what is sinless and free of passion. In simple words he holds out the promise and the pattern of virtue.'], 130: ['Where nothing great or noble is happening, they keep quiet; but where they see some being saved, they are more burdensome than anyone. So they are enemies of human salvation and ignorant of the sacred writings. For if the new covenant proclaimed through Jeremiah is other than the first, one must certainly use not the old laws but the new.', 'But the Pharisees, unwilling to see this, lie in wait for the holy apostles and say about them to Christ: “Look, we see those you train opposing the legal commands. The law orders rest on the Sabbath and touching no labor at all, yet the disciples rub ears of grain with their hands.” But tell me yourself, Pharisee: when you set your own Sabbath table, do you not break the bread? Why then blame others? And how does the Savior defend them?'], 131: ['Being impious, the Pharisees were pretending piety in order to destroy the pious. That is why they also tried to slander Christ and his disciples when they saw them shining with wonders.'], 132: ['“Since,” he says, “I do not cast out the demons by the ruler of the demons — as he showed by saying that every kingdom divided against itself is dissolved and destroyed — then I cast them out by the power of the Spirit, and for that reason the kingdom of God has drawn near.”'], 133: ['He calls the devil “strong” not as if he were this by nature, but to show the tyranny he gained from our slackness. “I plunder him,” not letting him keep humans as worshipers, but persuading them to come to the knowledge of God. How then will he become my ally against himself?'], 134: ['When someone sinned against a human being, it was possible to beseech God for him; but when humans blasphemed against God, it was not allowed to beseech for them. Yet since the Son of God was seen as man — even though he was God by nature — and was not very clearly recognized by the senseless, he sometimes grants forgiveness to those who sin against him from ignorance; but to those who sin against the Spirit he says perpetual punishment is brought.'], 135: ['By “Spirit” he means the whole divinity of the Trinity. Still, forgiveness is given through the Spirit’s grace to those who repent. Wanting to show the greatness of the sin, Christ spoke this way — for with God there is no unforgivable sin among those who repent genuinely and as they ought.', 'By “Spirit” he means the whole divinity of the Trinity. Still, forgiveness is given through the Spirit’s grace to those who repent and are baptized. Wanting to show the greatness of the sin, Christ said this. For though God often either exacts accounts from sinners only here and not also there — according to “the Lord will not avenge twice for the same” — or forbears in the present age without also granting forgiveness from there, of such people he says the punishment is indelible and without pardon both here and there.'], 136: ['When he says “treasure,” he points to the mass of what lies in the soul. And so that some may not say humans are wicked by nature, he showed this in the Pharisees’ case: that the same one person can sometimes become good and sometimes wicked, saying, “The good person speaks from the overflow of his heart,” and likewise the wicked.'], 137: ['Even if the Lord said that being wicked they cannot help speaking wicked things, he did not say this as if they were wicked by nature, but as overcome by evil from much senselessness. And even if he said that being wicked they cannot speak good things, he did not say this as if they were wicked by nature, but from their own voluntary movement.'], 138: ['“Since the signs that have happened,” they say, “were of demons, who produce appearances only on earth, you too make a sign from heaven by your own power.” Another evangelist said clearly that they were asking him to make a sign “from heaven,” which it was fitting for divine power to do. They said this as if he could not do anything God-befitting, blind in mind — for opening blind eyes, raising the dead, and rebuking sea and winds belong to God-befitting authority alone.'], 139: ['They are “wicked” as spending the excellence of the mind not on love of God, but on doing and saying something against God. He called them an “adulteress,” showing both the earlier and the present unbelief. For they neither believed the Father nor stood with Christ himself, who wedded humanity and betrothed it according to humanity through what was said: “And I will betroth you to myself forever.” They glued themselves to Satan, naming the manner of intelligible fornication. He shows himself again to the Father — the sign of Jonah the prophet.'], 140: ['So <if> Jonah is taken as a type of Christ, he is not taken in every respect. For example, he was sent to preach to the Ninevites, but sought to flee from God’s face and is seen hesitating toward the mission. The Son too was sent from God the Father preaching to the nations, but he was not unwilling for the service.', 'The prophet urged those sailing with him to throw him into the sea; he was also swallowed by a whale, then given up after three days, and after that went to Nineveh and fulfilled the service — yet he was not moderately grieved when God pitied the Ninevites. Christ also endured death willingly, remained in the heart of the earth, rose again, and after that went into Galilee and commanded that the preaching to the nations begin — yet he was not grieved when he saw those called into knowledge being saved.', 'Therefore, just as bees, flying around meadows and flowers, always gather what is useful for building the honeycombs, so we too, searching the God-inspired scripture, must always collect and arrange what serves to clarify Christ’s mysteries, and finish the word without blame.']}

LEMMAS = {125: [{'form': 'ἐπινοίας', 'lemma': 'ἐπίνοια', 'gloss': 'aspect / conception', 'lexica': 'patristic'}], 126: [], 127: [{'form': 'ἀρχέτυπον', 'lemma': 'ἀρχέτυπον', 'gloss': 'archetype', 'lexica': 'LSJ'}], 128: [], 129: [], 130: [], 131: [], 132: [], 133: [{'form': 'διαρπάζω', 'lemma': 'διαρπάζω', 'gloss': 'plunder', 'lexica': 'LSJ'}], 134: [], 135: [], 136: [], 137: [], 138: [], 139: [], 140: [{'form': 'τύπος', 'lemma': 'τύπος', 'gloss': 'type / figure', 'lexica': 'patristic'}]}

CHOICES = {125: [{'term': '<ᾗ…υἱὸς> / <τοιγαροῦν>', 'english': 'supplied stretches', 'rejected': ['silent omit / invent Greek'], 'why': 'Angle brackets mark editor-supplied text; disclose, invent no Greek.'}], 126: [], 127: [], 128: [], 129: [], 130: [], 131: [], 132: [], 133: [], 134: [], 135: [{'term': 'πνεῦμα', 'english': 'Spirit = whole Trinity divinity', 'rejected': ['third person only'], 'why': 'Fragment equates Spirit with the Trinity’s whole Godhead here.'}], 136: [], 137: [], 138: [], 139: [], 140: [{'term': '<εἰ>', 'english': 'if', 'rejected': ['silent omit'], 'why': 'Editor-supplied particle; disclose.'}]}

ALLUSIONS = {125: [{'reference': 'Matthew 11:27', 'reason': 'No one knows the Father except the Son.', 'certainty': 'clear'}], 126: [{'reference': 'Matthew 11:27', 'reason': 'All things handed over to the Son.', 'certainty': 'clear'}], 127: [{'reference': 'Matthew 11:27', 'reason': 'Son reveals the Father.', 'certainty': 'clear'}, {'reference': '1 Corinthians 2:10', 'reason': 'Spirit searches the depths of God.', 'certainty': 'clear'}], 128: [{'reference': 'Matthew 11:28', 'reason': 'Come to me, all who labor.', 'certainty': 'clear'}, {'reference': '2 Peter 1:4', 'reason': 'Sharers in divine nature.', 'certainty': 'clear'}], 129: [{'reference': 'Matthew 11:30', 'reason': 'Yoke is easy / light.', 'certainty': 'clear'}], 130: [{'reference': 'Matthew 12:1-2', 'reason': 'Disciples pluck grain on Sabbath.', 'certainty': 'clear'}, {'reference': 'Jeremiah 31:31', 'reason': 'New covenant.', 'certainty': 'clear'}], 131: [{'reference': 'Matthew 12:9-14', 'reason': 'Healing; plot against him.', 'certainty': 'clear'}], 132: [{'reference': 'Matthew 12:24-28', 'reason': 'By Beelzebul / by Spirit of God.', 'certainty': 'clear'}], 133: [{'reference': 'Matthew 12:29', 'reason': 'Bind the strong man.', 'certainty': 'clear'}], 134: [{'reference': 'Matthew 12:31-32', 'reason': 'Blasphemy against the Spirit.', 'certainty': 'clear'}], 135: [{'reference': 'Matthew 12:31-32', 'reason': 'Unforgivable blasphemy.', 'certainty': 'clear'}, {'reference': 'Nahum 1:9', 'reason': 'Not avenge twice (LXX).', 'certainty': 'possible'}], 136: [{'reference': 'Matthew 12:34-35', 'reason': 'Treasure of heart.', 'certainty': 'clear'}], 137: [{'reference': 'Matthew 12:35', 'reason': 'Cannot speak good while wicked.', 'certainty': 'clear'}], 138: [{'reference': 'Matthew 12:38', 'reason': 'We want a sign.', 'certainty': 'clear'}, {'reference': 'Mark 8:11', 'reason': 'Sign from heaven.', 'certainty': 'clear'}], 139: [{'reference': 'Matthew 12:39', 'reason': 'Evil and adulterous generation.', 'certainty': 'clear'}, {'reference': 'Hosea 2:19', 'reason': 'I will betroth you forever.', 'certainty': 'clear'}], 140: [{'reference': 'Matthew 12:41', 'reason': 'Men of Nineveh; sign of Jonah.', 'certainty': 'clear'}, {'reference': 'Jonah 1-3', 'reason': 'Flight, whale, Nineveh.', 'certainty': 'clear'}]}

def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(125, 141):
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
                "title": src["head"],
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a32a35.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a32a35.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a32",
                        "cyril-matt-frag-a33",
                        "cyril-matt-frag-a34",
                        "cyril-matt-frag-a35",
                    ],
                    "sections": "125-140",
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
