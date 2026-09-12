#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a36..a39 (entries 141–156)."""
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
    if n <= 144:
        return "cyril-matt-frag-a36"
    if n <= 148:
        return "cyril-matt-frag-a37"
    if n <= 152:
        return "cyril-matt-frag-a38"
    return "cyril-matt-frag-a39"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(141, 157)}

PASS_A = {141: 'And very reasonably; for whenever once someone having-been-freed of the evils not may-be-made-prudent, by-much harder things he-will-suffer of the former; for through this he-said: not he-finds rest, in-order-that he-may-show, that wholly and from necessity will-take the such the of the demons plot; for also from two these the such to-be-made-prudent it-was-necessary, both from the to-suffer before, and from the to-be-released. Rather also third is-present the of the worse to-suffer threat, but yet by none of these they-became better. There-was on-the-one-hand to them dwelling the wicked spirit also when in Egypt they-were-serving and with the Egyptians living customs and laws full they-were of every uncleanness. Since through Moses they-have-been-ransomed and law they-have-had pedagogue toward the of the true God-knowledge calling light, has-been-driven-out the profane and unclean spirit. But since not they-have-believed into Christ, again to them has-settled the demon; for it-found of them the heart bare and idle from every piety and as-if having-been-swept and it-dwelt in them; for just-as the spirit the holy whenever it-may-see heart of human idle from every uncleanness both it-lodges and dwells and rests in him, thus also the spirit the unclean in souls of lawless to-dwell loves.', 142: "Through this in parables speaks the Christ, in-order-that also through these he-may-show, that himself he-is the having-been-prophesied, about whom said David: 'I-will-open in parables the mouth of me' and again: 'and will-be the human hiding the words of him and he-will-be-hidden as from water being-borne'.", 143: 'To the gentle and learning-loving having knowledge will-be-settled the divine light more-richly than formerly, but to those having-had spark of light intelligible, but into senseless having-turned knowledge will-be-quenched also itself the small which they-have brightness, which have-suffered Jews into Christ not having-believed; for they-had small light-leading from the law guiding them upon the into God knowledge. But since into Christ they-have-acted-impiously, also of it they-have-been-deprived. The however Lord more-clearly showing what is what he-said, that to the having will-be-given, but from the not having also what he-has will-be-taken from him, he-adds: through this in parables to them I-speak, that seeing not they-see and hearing not they-hear nor understand. To the teachable humans and well being-disposed toward reception of divine words will-be-settled the spirit the holy increasing in them the gifts, but to those spark of light having-possessed and of this having-neglected will-be-quenched wholly and will-be-taken from them also the smallest, which formerly they-had. But this Jews have-suffered having-taken light from the law and not having-multiplied, but also of the truth having-come being-dull-sighted toward it they-have-been-deprived, what they-had-possessed.', 144: 'The to-say lest ever they-may-turn and I-will-heal them intensified shows stubbornness, yet also of drawing and stirring-up it-is; for he-shows, that if they-may-turn, he-heals them; for through the to-be-saved them thus he-speaks, since it-was-necessary him wholly not-even anything to-speak, but to-be-silent, yet not through the own glory, but through the of them salvation all he-does.', 145: 'He-blesses therefore them as having-heard of the of the Son voice and having-been-deemed-worthy of the of him vision, through whom and in whom the of the Father and God they-were-seeing nature intelligibly, of which have-been-deemed-worthy the of-old holy and most-full they-had the upon goods gladness.', 146: "Let-us-see as in thick matters, what is the upon the road to-be. Hard and somehow useless is every road through the to the of all to-lie feet and nothing to it is-heaped of the seeds, but lies rather upon-surface and to the wanting of the birds ready into plunder. Therefore who the mind have in themselves hard and as-if compressed, these the divine not they-receive seed, but to the unclean spirits having-been-trampled they-have-become road; for these are 'the birds of the heaven'. But heaven here the air we-understand, in which the of the wickedness spirits turn, by which also the good seed is-plundered and is-destroyed. But who also those upon the rock? There-are some without-investigation having the faith in themselves, but the mind not letting-down into the of the mystery test. These light and rootless have the into God piety. And if on-the-one-hand from fair-wind may-be-borne the of Christians affairs of nothing them storming of trial, they-preserve then scarcely in themselves those the faith, but of persecution having-disturbed warless they-have the soul.", 147: "Matthew wrote wicked, but Mark 'satan', but Luke 'devil'. Not the-same is beside the road and in the road, but we-need of the difference through the 'I am the road'; yet the three wrote beside the road. Most-gracefully but Matthew and Mark 'upon the rocky', not upon rock he-says to-have-been-sown the word. Upon on-the-one-hand of all of the beside the road has-been-said the not understanding. But upon the good earth, this is the the word hearing and understanding; lest then those upon the rocky and those into the thorns between are of not-understanding and understanding. But hortatory into the of understanding to-care; for if not of the understanding is-plundered the seed, understanding must-be-taken-up and must-be-covered the seed in the earth, the memory, in-order-that it-may-take-root and not bare being-found may-be-plundered by the of the wickedness spirits.", 148: 'But that ecumenical has-become the through Christ call, himself will-confirm saying clearly, that of the gospel preachings the net from every gathers race. And just-as those of the of the fishes hunt skilled and sea-working having craft let-down the net not distinguishing, but what ever to the meshes may-be-caught, this wholly and altogether they-draw into land, thus also the power of the preaching and the marvelous and many-folded of the sacred lessons teaching, which the good fishermen apostles wove, from every draws race and gathers toward God. But it-gathers until time, which will-be-fulfilled according to the time of the consummation, according to which those having-been-netted outside of the life having-drawn the upon this having-been-appointed angels of the God the of all distinction will-make separating the wicked from midst of the righteous.', 149: "Scribe is the through the persistent reading of the scriptures of both the old and the new treasure of knowledge to himself having-stored. Wherefore he-blesses those having-brought-together in themselves legal training and gospel, so-as to-bring-out from the treasure new and old. These also to scribe he-likens just-as also elsewhere he-says: 'I-send' to you 'wise and scribes'. Did-you-see how not he-casts-out the old—through which is-adorned the soul.", 150: "But now also baskets he-filled and that rather to one each of the disciples was-given into wage of the service, through which is-signified, that those serving much will-have the wage. Since also the other evangelist 'of-barley' says the breads, the of the contemplation aim into this looks; the barley beastlike is food, which is the through Moses contemplation to the more-irrational having-been-brought; through this but also five the breads we-say through the five-part of the of Moses writing, but two the fishes, through which is-shown the double of the fishermen writing, both apostolic and gospel.", 151: 'What the dismiss is, let-us-examine carefully. Some on-the-one-hand of those following the Christ of wicked spirits holding them to-be-released were-asking, but others also of other illnesses were-seeking putting-away. As therefore knowing the disciples that having-nodded only he-accomplishes to the suffering the desired, dismiss them they-say, not themselves rather being-weary as of having-passed the time, but of the into the crowds love holding and as-if practicing already the pastoral skill and of the to-care of peoples beginning.', 152: 'The of the economy mystery fulfilling the savior into the heaven looks-up; for also of slave form he-took God being according to nature and through the hands of the disciples he-gives the foods to the crowds the of the holy hinting toward God nearness. Wherefore those not such outside have-stood of him.', 153: 'In-order-that through manner every God being by-nature he-may-be-recognized, he-multiplies the little, and looks into heaven as-if the from-above blessing asking. But he-was-doing also this economically through us. For he-is on-the-one-hand himself the all filling, the from-above and from Father blessing. But in-order-that we-may-learn we, that of table beginning and about-to breads to-break to God to-bring we-ought with-upturned as-if having-placed hands and the from-above blessing upon them to-bring-down, beginning and type and way of the deed he-has-become to us economically.', 154: 'The of the breads to-have-abounded the fragments of multitude of men not small having-been-satisfied clear assurance would become, if of the hospitality the matter rich has from God the repayment. But it-is-possible to-see to the more-ancient wonders the new agreeing and of one being and of the same power workings. He-rained in desert the manna to those from Israel, but look indeed again in desert to those in need of food he-has-supplied abundantly as-if from heaven sending-down it; for the to-multiply the little and as-if from the nothing the thus much to-have-fed multitude not unlike would be to the first sign.', 155: "Chosen always to God the male as most-combatant and into youth to-come that-is into fitness spiritual and to-sow-seed and the others to-teach being-able and to-measure 'into measure of stature of the fullness of the Christ' being-strong.", 156: 'But he-prays not as needing, but as high-priest the on-behalf of us petitions making. And after a-little; until evening, in-order-that he-may-show, that not it-is-necessary fickly to-have about this, but endurance and eagerness. But he-teaches also this, so-that in what need, we-ought the common-beneficial to-speak to those encountering and after the such conversation and teaching upon the prayer to-proceed. He-prays not as needing something the God, but as high-priest the on-behalf of us petitions making, and-yet according to what he-is-understood and is God by-nature himself supplying to the holy the requests. But he-prays until evening, in-order-that he-may-show, that not it-is-necessary fickly to-have about it, but endurance and long-suffering to-show. He on-the-one-hand therefore was-going-up there and was-praying.'}

PASS_B = {141: ['And it is quite fitting. Once someone has been freed from evils and is not made prudent, he will suffer things much harder than before. That is why he said the spirit “finds no rest”: to show that the demons’ plot will certainly and of necessity seize such a person. Two things ought to have made them prudent — having suffered earlier, and having been released. There is even a third: the threat of suffering worse. Yet by none of these did they become better.', 'The wicked spirit lived in them even when they were slaves in Egypt and, living by Egyptian customs and laws, were full of every uncleanness. When they were ransomed through Moses and received the law as a guide calling them toward the light of true knowledge of God, the profane and unclean spirit was driven out. But because they have not believed in Christ, the demon settled in them again. It found their heart bare and idle of every piety, as if swept clean, and dwelt in them. Just as the Holy Spirit, when it sees a human heart idle of every uncleanness, lodges and dwells and rests in it, so the unclean spirit loves to inhabit the souls of the lawless.'], 142: ['Christ speaks in parables also to show through them that he himself is the one prophesied, of whom David said, “I will open my mouth in parables,” and again, “And the man will be one who hides his words and will be hidden as from rushing water.”'], 143: ['In the gentle and eager to learn who already have knowledge, the divine light will settle even more richly than before. But in those who had a spark of intelligible light and turned it into senseless “knowledge,” even the small brightness they have will be quenched — which is what the Jews suffered by not believing in Christ. They had a small leading light from the law guiding them toward knowledge of God; but because they acted impiously toward Christ, they were deprived of that too.', 'The Lord makes clearer what he meant by “to the one who has it will be given, and from the one who does not have, even what he has will be taken,” by adding: “For this reason I speak to them in parables, because seeing they do not see, and hearing they do not hear, nor understand.”', 'In teachable people well disposed to receive divine words, the Holy Spirit will settle, increasing the gifts in them. But in those who possessed a spark of light and neglected it, even the least they once had will wholly be quenched and taken from them. That is what the Jews suffered: they received light from the law and did not multiply it; and when the truth came, growing dull-eyed toward it, they were stripped of what they had possessed.'], 144: ['Saying “lest they turn and I heal them” shows intensified stubbornness — yet it is also the speech of one drawing and stirring them. He shows that if they turn, he heals them. He speaks this way for their salvation. He could have said nothing at all and kept silent; yet he does everything not for his own glory, but for their salvation.'], 145: ['So he calls them blessed as ones who have heard the Son’s voice and been counted worthy of his sight — through whom and in whom they were seeing the Father and God’s nature intelligibly — the very things the saints of old were counted worthy of, and in which they had the fullest joy in goods.'], 146: ['Let us see, in concrete terms, what it is to be “on the road.” Every road is somehow hard and useless, because it lies under everyone’s feet; none of the seed is heaped into it, but lies on the surface, ready for any birds that want to snatch it. So those who have a hard, packed mind in themselves do not receive the divine seed, but have become a road trampled by unclean spirits — for these are “the birds of the heaven.” By heaven here we mean the air, in which the spirits of wickedness move, by whom the good seed is also snatched and destroyed.', 'And who are those on the rock? Some hold the faith in themselves without investigation and do not let the mind down into testing the mystery. These have a light, rootless piety toward God. If Christian affairs are carried with a fair wind and no trial storms them, they scarcely keep the faith in themselves then; but when persecution disturbs them, they have a soul unwilling to fight.'], 147: ['Matthew wrote “the evil one,” Mark “Satan,” Luke “the devil.” “Beside the road” is not the same as “in the road,” and we need the difference because of “I am the road”; yet all three wrote “beside the road.” Most aptly Matthew and Mark say the word was sown “on the rocky places,” not on rock. Of all that is beside the road it is said that they do not understand; but of the good soil, “this is the one who hears the word and understands.” Perhaps, then, those on the rocky places and those among the thorns stand between the non-understanding and the understanding.', 'And it urges care for understanding. If the seed of the one who understands is not snatched, one must take up understanding and cover the seed in the earth — memory — so that it may take root and, not being found bare, may not be snatched by the spirits of wickedness.'], 148: ['That the call through Christ has become worldwide, he himself will confirm by saying clearly that the net of the gospel preachings gathers from every race. Just as those skilled in fishing, whose craft is the sea’s work, let down the net without distinguishing, and whatever is caught in the meshes they wholly and altogether draw to land, so also the power of the preaching and the marvelous, intricate teaching of the sacred lessons — which the good fishermen, the apostles, wove — draws from every race and gathers toward God.', 'It gathers until a time that will be fulfilled at the consummation, when the angels of God appointed for this, having drawn those netted out of this life, will make the distinction of all, separating the wicked from the midst of the righteous.'], 149: ['A “scribe” is the one who, through persistent reading of the scriptures of both the old and the new, has stored up a treasure of knowledge for himself. That is why he blesses those who have brought together in themselves both legal and gospel training, so as to bring out from the treasure things new and old. He also likens these to a scribe, just as elsewhere he says, “I send you wise men and scribes.” See how he does not cast out the old — through which the soul is adorned.'], 150: ['And now he also filled baskets, and that rather each of the disciples was given one as the wage of service — which signifies that those who serve will have a great wage. Since another evangelist also calls the loaves “of barley,” the aim of contemplation looks to this: barley is beastlike food, which is the contemplation through Moses brought to the more irrational. That is also why we say five loaves, because of the fivefold writing of Moses, and two fish, through which is shown the double writing of the fishermen — both apostolic and evangelical.'], 151: ['Let us examine carefully what “dismiss them” means. Some of those following Christ were asking to be released from the wicked spirits holding them; others were seeking the putting away of other illnesses. So the disciples, knowing that with a mere nod he accomplishes what the suffering desire, say “dismiss them” — not themselves growing weary as if the time had passed, but holding to love for the crowds, already practicing pastoral skill, as it were, and beginning to care for peoples.'], 152: ['Fulfilling the mystery of the economy, the Savior looks up to heaven. For though God by nature, he took a slave’s form, and through the disciples’ hands he gives the foods to the crowds, hinting at the holy ones’ nearness to God. That is why those who are not such stand outside him.'], 153: ['So that by every manner he may be recognized as God by nature, he multiplies the little, and looks into heaven as if asking the blessing from above. He was also doing this economically for our sake. For he himself is the one who fills all things — the blessing from above and from the Father. But so that we may learn, when beginning a table and about to break bread, that we ought to set them in upturned hands, as it were, and bring down the blessing from above upon them, he has become for us economically the beginning and type and way of the deed.'], 154: ['That fragments of the loaves abounded after a not small multitude of men had been satisfied would be clear assurance that hospitality’s work has rich repayment from God. One can see the new wonders agreeing with the more ancient, workings of one and the same power. He rained the manna in the desert for those from Israel; and look — again in the desert he has supplied abundantly to those in need of food, as if sending it down from heaven. For multiplying the little and, as from nothing, feeding so great a multitude would not be unlike the first sign.'], 155: ['What is male is always chosen by God as most ready for combat, able to come into youth — that is, into spiritual fitness — to sow seed, to teach others, and strong enough to measure “to the measure of the stature of the fullness of Christ.”'], 156: ['He prays not as one in need, but as high priest making petitions on our behalf. And a little later: until evening, to show that one must not be fickle about this, but have endurance and eagerness. He also teaches this: that when there is need, we ought to speak what benefits the common good to those we meet, and after such conversation and teaching proceed to prayer.', 'He prays not as God needing something, but as high priest making petitions on our behalf — and yet, according to what he is understood to be and is, God by nature, himself supplying the holy ones’ requests. He prays until evening to show that one must not be fickle about it, but show endurance and long-suffering. So he was going up there and praying.']}

LEMMAS = {141: [{'form': 'σεσαρωμένην', 'lemma': 'σαρόω', 'gloss': 'swept clean', 'lexica': 'NT'}], 142: [], 143: [], 144: [], 145: [], 146: [{'form': 'πεπιλημένον', 'lemma': 'πιλέω', 'gloss': 'compressed / packed', 'lexica': 'LSJ'}], 147: [], 148: [{'form': 'σαγηνευθέντας', 'lemma': 'σαγηνεύω', 'gloss': 'caught in a net', 'lexica': 'LSJ'}], 149: [], 150: [{'form': 'κριθίνους', 'lemma': 'κρίθινος', 'gloss': 'of barley', 'lexica': 'NT'}], 151: [], 152: [], 153: [], 154: [], 155: [], 156: [{'form': 'ἁψικόρως', 'lemma': 'ἁψίκορος', 'gloss': 'fickle / soon tired', 'lexica': 'patristic'}]}

CHOICES = {141: [], 142: [], 143: [], 144: [], 145: [], 146: [], 147: [{'term': 'παρὰ τὴν ὁδόν vs ἐν τῇ ὁδῷ', 'english': 'beside the road vs in the road', 'rejected': ['collapse the distinction'], 'why': 'Fragment needs the difference because of ‘I am the road’.'}], 148: [], 149: [], 150: [{'term': 'κριθίνους ἄρτους', 'english': 'barley loaves → Mosaic / ‘beastlike’ food', 'rejected': ['mere menu detail'], 'why': 'Contemplative reading ties barley to Moses’ fivefold writing.'}], 151: [], 152: [], 153: [], 154: [], 155: [], 156: [{'term': 'οὐχ ὡς δεόμενος', 'english': 'not as needing', 'rejected': ['prays from lack as God'], 'why': 'High-priestly petition for us; as God he supplies requests.'}]}

ALLUSIONS = {141: [{'reference': 'Matthew 12:43-45', 'reason': 'Unclean spirit returns with seven others.', 'certainty': 'clear'}], 142: [{'reference': 'Matthew 13:3', 'reason': 'He spoke many things in parables.', 'certainty': 'clear'}, {'reference': 'Psalm 78:2', 'reason': 'I will open my mouth in parables.', 'certainty': 'clear'}], 143: [{'reference': 'Matthew 13:12-13', 'reason': 'To the one who has; speaking in parables.', 'certainty': 'clear'}], 144: [{'reference': 'Matthew 13:15', 'reason': 'Lest they turn and I heal them.', 'certainty': 'clear'}], 145: [{'reference': 'Matthew 13:16', 'reason': 'Blessed are your eyes and ears.', 'certainty': 'clear'}], 146: [{'reference': 'Matthew 13:19-22', 'reason': 'Path, rocky, thorns.', 'certainty': 'clear'}], 147: [{'reference': 'Matthew 13:19-23', 'reason': 'Evil one / Satan / devil; good soil.', 'certainty': 'clear'}, {'reference': 'John 14:6', 'reason': 'I am the way.', 'certainty': 'clear'}], 148: [{'reference': 'Matthew 13:49-50', 'reason': 'Angels separate wicked from righteous.', 'certainty': 'clear'}], 149: [{'reference': 'Matthew 13:52', 'reason': 'Scribe trained for the kingdom; new and old.', 'certainty': 'clear'}], 150: [{'reference': 'Matthew 14:13-21', 'reason': 'Feeding of the five thousand.', 'certainty': 'clear'}, {'reference': 'John 6:9', 'reason': 'Barley loaves.', 'certainty': 'clear'}], 151: [{'reference': 'Matthew 14:15', 'reason': 'Send the crowds away.', 'certainty': 'clear'}], 152: [{'reference': 'Matthew 14:19', 'reason': 'Looking up to heaven; gave to disciples.', 'certainty': 'clear'}, {'reference': 'Philippians 2:7', 'reason': 'Form of a slave.', 'certainty': 'clear'}], 153: [{'reference': 'Matthew 14:19', 'reason': 'Looked up to heaven and blessed.', 'certainty': 'clear'}], 154: [{'reference': 'Matthew 14:20', 'reason': 'Twelve baskets of fragments.', 'certainty': 'clear'}, {'reference': 'Exodus 16', 'reason': 'Manna in the desert.', 'certainty': 'clear'}], 155: [{'reference': 'Matthew 14:21', 'reason': 'Five thousand men, besides women and children.', 'certainty': 'clear'}, {'reference': 'Ephesians 4:13', 'reason': 'Measure of the stature of Christ’s fullness.', 'certainty': 'clear'}], 156: [{'reference': 'Matthew 14:23', 'reason': 'Went up the mountain by himself to pray.', 'certainty': 'clear'}]}

def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(141, 157):
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a36a39.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a36a39.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a36",
                        "cyril-matt-frag-a37",
                        "cyril-matt-frag-a38",
                        "cyril-matt-frag-a39",
                    ],
                    "sections": "141-156",
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
