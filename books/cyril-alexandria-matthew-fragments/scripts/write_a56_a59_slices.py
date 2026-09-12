#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a56..a59 (entries 221–236)."""
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
    if n <= 224:
        return "cyril-matt-frag-a56"
    if n <= 228:
        return "cyril-matt-frag-a57"
    if n <= 232:
        return "cyril-matt-frag-a58"
    return "cyril-matt-frag-a59"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(221, 237)}

PASS_A = {
221: "Since for they-saw, that those about Theudas and Judas—through the words these into such suspicion to-cast.",
222: "Was-willing on-the-one-hand the of the all God of human dominion free to-be the Israel. But since the divine they-have-trampled laws, they-have-become under hand of those then having-ruled and tributes they-laid upon them. And of tax thereafter—of Romans having-fallen-over rule.",
223: "From measureless shamelessness being-envious the Pharisees, since of having-been-shamed of the Sadducees he-was-being-praised by the crowds, with hypocrisy again they-ask testing him, if also he-adds again to the command the first as correcting the law, in-order-that they-may-find against him a-handle. And on-the-one-hand Matthew and Luke 'lawyer' to-be was-saying the having-asked, but Mark 'scribe'. Not is this disagreement; for some on-the-one-hand law-learned this they-show, but others scribe-leader, which is of the law interpreter to the people. But the Lord publishes of them the wickedness, that not through this they-came to-ask, so-as to-be-benefited, but from the not to-have and by the envy to-be-held, and he-teaches, that not it-is-necessary in part on-the-one-hand to-love the God, in part but to the earthly to-be-attached. Through which but the Lord said this the command more-summary being of all, seemed the lawyer to-cast him into danger as making-god himself. Whence also not having-said this praised the lawyer as the Mark says. The on-the-one-hand therefore first command every form of piety teaches; for the from whole heart the God to-love cause is of every good, but the second the toward humans just things contains; and the on-the-one-hand makes-way for the second, but the from this is-held-together; for the the toward God love having-accomplished clearly also the toward the neighbor into all as himself loves. Of all of the commands the such fulfiller happens-to-be.",
224: "Since of having-been-shamed of the Sadducees and having-withdrawn he-was-being-praised the Lord, upon this being-envious to these the Pharisees came into midst and law-learned someone very beside them being-thought asks which command great in the law, having-thought that he-is-about on-the-one-hand the of Moses to-cross-out, to-set-beside but the of himself teaching or <to-say> that you-will-love Lord the God of you and me, yoking of himself the glory to the glory of the father and thus he-finds place of the to-cast into danger as making-god himself or, if this he-may-pass-in-silence, to-say: therefore not I-accept you as God. But the Lord nothing new having-said but the of the law and by-this having-muzzled the Pharisees asks also himself them of-whom son they-think the Christ.",
225: "How therefore David in spirit Lord him calls? For it-is-necessary he-says the fathers of the sons lords to-be-named through the to-have them under the of them authority the sons, the-opposite the David the from seed of himself Lord of him calls.",
226: "Woe therefore to you, O lawyers, that burdensome admittedly being the law to the on-the-one-hand others trampling it of death penalty you-bring, yourselves but of the law not-even you-touch.",
227: "Since those new doctrines teaching as upon-all to-see it-is of empty-glory and boastfulness love into the of the teaching dignity having-arrived, removes the Lord this the suspicion and the road he-cuts as upon destruction leading. If therefore, he-says, of glory both and of first-places you-love, the of the servants and later order seek and humility practice.",
228: "Son of Gehenna he-says the being-destroyed from unbelief as of impiety into this to-slide and into this of lawlessness to-arrive measure as unmediated to-have toward flame the intimacy and all-but kinship the toward <the the> torments unambiguously to-bear.",
229: "Through this but 'throne of God' the heaven name the scriptures, that to the above powers God rests-upon; for in heaven are those doing the will of him angels and always glorifying him; for this to him rest. 'But the earth footstool of the feet of him'; for in it through flesh with the humans he-associated. But foot of God the holy of him flesh and variously is-named.",
230: "You-exact, he-says? O Pharisees, the tenths perhaps somewhere also of herbs fine having-left the commands, upon which is greater the transgression. And what-sort these are the injunctions? The judgment, this-is the to-judge right and blameless, and the mercy, this-is the into God genuineness; for better judgment and mercy and faith the into God of tenth and firstfruits. Wherefore also through the prophet says the of the all God: and now, Israel, 'what Lord' the God 'seeks from you but or of the to-do judgment and to-love' and to-seek 'mercy and ready to-be of the to-walk with Lord' of the 'God of you'. For in the very ready toward following the into faith genuine is-seen being-saved. See the rebuke; you-exact, he-says, O Pharisees, the tenths perhaps somewhere also of herbs fine having-left the commands, upon which is greater the transgression. But what-sort these the commands? The judgment, this-is the to-judge right and the mercy and the faith into God; for these better of tenth and firstfruits. Wherefore also through the prophet says the of the all God: and now, Israel, 'what Lord' the God 'seeks from you but or of the to-do judgment and to-love' and to-seek 'mercy and ready to-be of the to-walk with Lord' of the 'God of you'.",
231: "Through these the of the Pharisees he-describes life advising not to the outside fashionings to-be-molded only, but to-have also the inside clean the into mind and heart.",
232: "What then therefore says the savior, carefully we-will-search. The on-the-one-hand of the Jews fathers killed according to times the holy prophets the divine to them ferrying word; those at-least from them having-been confessing, that the prophets have-been august and honorable, fitted-around to them the crowns that-is the tombs honor having-assigned the to the holy most-fitting, themselves but prophets to-be having-believed and men holy judges have-become of those having-killed them; for through which to-honor they-have-known those having-been-killed, through these of them they-accuse as having-acted-impiously. But those of the own fathers upon the thus terrible bloodsheds having-condemned by the equal were-about to-be-caught evils, rather but by the still worse. 'They-killed' on-the-one-hand 'the of the life author', they-have-added but to the against him impieties bloodsheds other against the marvelous of him disciples; for until on-the-one-hand someone the of others injustices may-examine by natural reasoning judging, he-sees the base and blames, himself but into the equal passions being-led as-if blind upon these is-borne.",
233: "According to what manner upon the last of the murderers generation the of every blood will-come justice, although through the prophet saying the God 'not will-die fathers on-behalf of children' and indeed also the reverse 'each but by the own sin will-die'? What therefore then do-we-say? How of the of others bloodshed will-they-be-made accounts those, toward whom these has-spoken the Christ? For either not will-be-punished on-the-one-hand on-behalf of Abel the Cain; Lamech but saying: 'man' I-have-killed 'into wound to me and youth into bruise'; of each therefore by the own having-been-weighed-down evils how the wretched the on-behalf of all will-they-undergo justice? For 'not unjust the God', but is judge just and strong and long-suffering according to the having-been-written. We-say therefore, that such-sort some to the having-been-said it-befits to-fit meaning. Let-there-be-set therefore such something perhaps: robbers have-become say in this the country. These the in circle were-plundering villages and those in them were-killing; but the of the rule leader not straightway the ruling to them bare sword, by-threats but rather to-be-reformed these he-was-eager. But they were nothing less cruel; but in-order-that thereafter may-be-turned-back the terrible, of having-been-caught some not he-spared, most-cruel but tortures having-subjected the upon the last he-was-placing danger not indeed only upon those being-indignant, but by-much more, since him being-long-suffering also the of the first deceived wildness. But I-think someone will-say of the last harshly having-been-punished, that the of all sins they-received themselves through the into them to-end of the judging the anger? Such something you-will-think also about God; for having-been-long-suffering in the previous times until these he-was-reasoning it-is-necessary the of the long-suffering to-define measure; for also it-was-necessary upon these the divine to-strike anger; for those on-the-one-hand against humans and fellow-slaves were-sinning, but those the of the all have-killed Lord. Not that therefore he-punishes the last through this harsh, but that he-endured into the present most-worthy-of-wonder.",
234: "If someone may-wish through the to-say the Lord this the generation not only those to-be-indicated, toward whom was the word, but of whole as-if of the murderers the race, of the rightly having he-departs; for we-find the holy scripture the like-manners as-if somehow also same-counsels naming as race. And indeed the blessed said David 'generation of upright will-be-blessed' and 'this the generation of those seeking' the Lord. Therefore the this, if also it-may-be-said demonstratively, not only perhaps somewhere to-have-indicated we-say those then present and hearing, but every the murderer and under the same of the impiety falling race; for will-be-ranked with the like the like as brother and same-kin.",
235: "Having-said this he-shows of himself the God-befitting also in human form being; for also about the God said Moses: 'spreading the wings of him he-received them'; and again David: 'but the sons of the humans in shelter of the wings of you will-hope'.",
236: "The having-been-said intelligible has the through faith sight; for whenever 'may-enter the fullness of the nations' and they-may-believe to the Christ, then those after these having-believed Jews see the of the divinity beauty of the Christ in son beholding to-be the father and him saying to-be the redeemer the through the prophets having-been-proclaimed, about whom has-foretold the prophet as coming in name of Lord; for the other prophets not in name of Lord came; for they-were-saying: 'thus Lord' and 'slave of Lord I am, and the God of the heaven I worship'.",
}

PASS_B = {
221: [
    "For they saw that those around Theudas and Judas — through these words to cast into such suspicion."
],
222: [
    "The God of all wanted Israel free of human domination. But because they trampled the divine laws, they came under the hand of those then in power, who laid tributes on them. And tax thereafter — when rule passed over to the Romans."
],
223: [
    "From measureless shamelessness the Pharisees, envious because he was being praised by the crowds after the Sadducees were put to shame, ask again with hypocrisy, testing him — whether he will also add again to the first command as if correcting the law — so that they may find a handle against him. Matthew and Luke said the one who asked was a “lawyer,” Mark a “scribe.” That is no disagreement: some show him learned in the law, others a leading scribe, that is, an interpreter of the law to the people.",
    "The Lord exposes their wickedness: they did not come to ask so as to be helped, but from having nothing and being held by envy. He also teaches that one must not love God in part and cling to earthly things in part. Because the Lord said this command is more summary than all, the lawyer seemed to be thrusting him into danger as making himself God. Hence, though he had not said that, the lawyer praised him, as Mark says. The first command teaches every form of piety; for loving God from the whole heart is the cause of every good. The second contains what is just toward humans. The first opens the way for the second, and the second is held together from it; for the one who has accomplished love toward God clearly also loves the neighbor in all things as himself. Such a person happens to be the fulfiller of all the commands."
],
224: [
    "Since the Lord was being praised after the Sadducees were shamed and withdrew, the Pharisees, envious at this, came forward, and someone thought very learned in the law among them asks which commandment is great in the law. He supposed Christ was about to cross out Moses’ teaching and set his own beside it, or <to say>, “You shall love the Lord your God — and me,” yoking his own glory to the Father’s glory, and so find a place to cast him into danger as making himself God — or, if he passed over that in silence, to say, “Then I do not accept you as God.”",
    "But the Lord said nothing new, only what is of the law, and having muzzled the Pharisees by this, he himself asks them whose son they think the Christ is."
],
225: [
    "How then does David in the Spirit call him Lord? For one ought, he says, to name fathers lords of their sons, because they have the sons under their authority; yet David, on the contrary, calls the one from his own seed his Lord."
],
226: [
    "Woe to you, then, lawyers: while the law is admittedly burdensome, on others who trample it you bring the penalty of death, but you yourselves do not even touch the law."
],
227: [
    "Since one generally sees those who teach new doctrines arriving at the dignity of teaching from love of empty glory and boastfulness, the Lord removes this suspicion and cuts off the road as leading to ruin. So if, he says, you love glory and first places, seek the order of servants and of those later, and practice humility."
],
228: [
    "By “son of Gehenna” he means the one being destroyed from unbelief — as having slid into this through impiety and reached such a measure of lawlessness as to have unmediated intimacy with the flame, and all but kinship toward <bearing> the torments without dispute."
],
229: [
    "That is why the scriptures name heaven “God’s throne”: God rests upon the powers above. For in heaven are the angels who do his will and always glorify him; that is rest for him. “But the earth is the footstool of his feet”: for in it he associated with humans through flesh. And God’s “foot” is his holy flesh, and it is named in various ways."
],
230: [
    "You exact tithes, he says, Pharisees — perhaps even of fine herbs — while leaving aside the commands whose transgression is greater. And what are those injunctions? Judgment — that is, judging what is right and blameless — and mercy — that is, genuineness toward God. For judgment and mercy and faith toward God are better than tithe and firstfruits. That is why through the prophet the God of all says: And now, Israel, “what does the Lord God seek from you but to do judgment and to love” and to seek “mercy, and to be ready to walk with the Lord your God”? For in being very ready to follow, what is saved into genuine faith is seen.",
    "See the rebuke: you exact tithes, Pharisees — perhaps even of fine herbs — leaving aside the commands whose transgression is greater. And what are those commands? Judgment — judging rightly — and mercy and faith toward God; for these are better than tithe and firstfruits. That is why through the prophet the God of all says: And now, Israel, “what does the Lord God seek from you but to do judgment and to love” and to seek “mercy, and to be ready to walk with the Lord your God”?"
],
231: [
    "Through these he describes the Pharisees’ life, advising not to be molded only by outward fashionings, but also to have the inside clean — what belongs to mind and heart."
],
232: [
    "Let us search carefully what the Savior says. The Jews’ fathers killed the holy prophets in their times, who were ferrying the divine word to them. Those born from them, confessing that the prophets were august and honorable, fitted crowns around them — that is, tombs — assigning the honor most fitting to the holy, and by believing them prophets and holy men they became judges of those who killed them. For by the very means they chose to honor the slain, through those means they accuse their fathers as having acted impiously.",
    "But those who condemned their own fathers for such terrible bloodshed were about to be caught by equal evils — rather, by still worse. They “killed the Author of life,” and added to the impieties against him other bloodsheds against his marvelous disciples. For as long as someone examines others’ injustices judging by natural reasoning, he sees what is base and blames it; but when he himself is led into the same passions, he is carried upon them as if blind."
],
233: [
    "In what manner will the justice for every blood come upon the last generation of the murderers — though God says through the prophet, “Fathers shall not die for children,” and again the reverse, “each shall die by his own sin”? What then do we say? How will those to whom Christ spoke these things be made to give account for others’ bloodshed? Will Cain not be punished for Abel? And Lamech saying, “I have killed a man for my wound and a youth for my bruise”? So if each is weighed down by his own evils, how will the wretched undergo justice on behalf of all? For “God is not unjust,” but is a just and strong and long-suffering judge, according to what is written.",
    "We say, then, that some such sense fits what was said. Suppose something like this: robbers arise in a certain country. They plunder the villages round about and kill those in them. The ruler of the province does not at once bare the ruling sword against them, but is eager rather to reform them by threats. They are no less cruel. So that the horror may at last be turned back, when some are caught he does not spare them, but subjecting them to most cruel tortures he sets the final danger upon them — not indignant only at those last crimes, but much more because the wildness of the first ones also deceived him while he was long-suffering. I think one of those last who were harshly punished will say that they themselves received everyone’s sins, because the judge’s anger ended upon them.",
    "You will think something like this also about God. Having been long-suffering in the previous times, he was reasoning up to these that the measure of long-suffering must be defined; for the divine anger also had to strike upon these. The earlier ones were sinning against humans and fellow-slaves; but these have killed the Lord of all. He is not harsh because he punishes the last, but marvelous because he endured until the present."
],
234: [
    "If someone wants, because the Lord said “this generation,” not only those to whom the word was addressed to be indicated, but as it were the whole race of the murderers, he leaves what is right. For we find holy scripture naming like manners and, as it were, same counsels as a “generation.” Blessed David said, “A generation of the upright will be blessed,” and “This is the generation of those seeking the Lord.” So “this,” even if said demonstratively, we say does not indicate only those then present and hearing, but every murderer and the whole race falling under the same impiety; for like will be ranked with like as brother and same-kin."
],
235: [
    "Having said this he shows what is God-befitting in himself even while in human form. For Moses also said about God, “Spreading his wings he received them”; and again David, “But the sons of humans will hope in the shelter of your wings.”"
],
236: [
    "What was said has an intelligible sight through faith. For when “the fullness of the nations enters” and they believe in Christ, then the Jews who believe after that see the beauty of Christ’s divinity, beholding the Father to be in the Son, and saying that he is the redeemer proclaimed through the prophets, of whom the prophet foretold as coming in the Lord’s name. For the other prophets did not come in the Lord’s name; they were saying, “Thus says the Lord,” and “I am a slave of the Lord, and I worship the God of heaven.”"
],
}

LEMMAS = {
221: [{"form": "Θευδᾶν", "lemma": "Θευδᾶς", "gloss": "Theudas", "lexica": "NT"}],
222: [],
223: [],
224: [{"form": "<εἰπεῖν>", "lemma": "λέγω", "gloss": "to say (supplied)", "lexica": "editorial"}],
225: [],
226: [],
227: [],
228: [{"form": "<τὸ τὰς>", "lemma": "ὁ", "gloss": "supplied article phrase", "lexica": "editorial"}],
229: [],
230: [],
231: [],
232: [{"form": "μιαιφονίαις", "lemma": "μιαιφονία", "gloss": "bloodshed / murder", "lexica": "LSJ"}],
233: [],
234: [],
235: [],
236: [{"form": "πλήρωμα", "lemma": "πλήρωμα", "gloss": "fullness", "lexica": "NT"}],
}

CHOICES = {
221: [{"term": "mid-phrase break", "english": "preserve trailing break; invent no Greek", "rejected": ["complete the sentence"], "why": "Copy-text trails mid-thought after Theudas/Judas."}],
222: [{"term": "mid-phrase break", "english": "preserve dash break; invent no Greek", "rejected": ["smooth completion"], "why": "Fragment ends mid-clause on Roman rule."}],
223: [],
224: [{"term": "<εἰπεῖν>", "english": "supplied ‘to say’", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}],
225: [],
226: [],
227: [],
228: [{"term": "<τὸ τὰς>", "english": "supplied article phrase", "rejected": ["silent omit / invent"], "why": "Disclose editor supply; invent no Greek."}],
229: [],
230: [],
231: [],
232: [{"term": "stray ‘32’", "english": "digit stripped in clean", "rejected": ["keep as marker"], "why": "OCR/page digit; not Greek text."}],
233: [],
234: [],
235: [],
236: [{"term": "stray ‘33’", "english": "digit stripped in clean", "rejected": ["keep as marker"], "why": "OCR/page digit; not Greek text."}],
}

ALLUSIONS = {
221: [{"reference": "Matthew 22:15", "reason": "Pharisees plot to entangle him in speech.", "certainty": "clear"}, {"reference": "Acts 5:36-37", "reason": "Theudas and Judas the Galilean.", "certainty": "clear"}],
222: [{"reference": "Matthew 22:17", "reason": "Is it lawful to pay tax to Caesar?", "certainty": "clear"}],
223: [{"reference": "Matthew 22:34-40", "reason": "Greatest commandment; love God and neighbor.", "certainty": "clear"}],
224: [{"reference": "Matthew 22:34-42", "reason": "Lawyer’s test; whose son is the Christ?", "certainty": "clear"}],
225: [{"reference": "Matthew 22:43-46", "reason": "David calls him Lord.", "certainty": "clear"}, {"reference": "Psalm 110:1", "reason": "The Lord said to my Lord.", "certainty": "clear"}],
226: [{"reference": "Matthew 23:4", "reason": "Heavy burdens; they will not move them.", "certainty": "clear"}],
227: [{"reference": "Matthew 23:11-12", "reason": "Greatest shall be your servant; humble exalted.", "certainty": "clear"}],
228: [{"reference": "Matthew 23:15", "reason": "Son of Gehenna twice as much.", "certainty": "clear"}],
229: [{"reference": "Matthew 23:22", "reason": "Swears by heaven, throne of God.", "certainty": "clear"}, {"reference": "Isaiah 66:1", "reason": "Heaven my throne; earth my footstool.", "certainty": "clear"}],
230: [{"reference": "Matthew 23:23", "reason": "Tithe mint; neglected justice, mercy, faith.", "certainty": "clear"}, {"reference": "Deuteronomy 10:12", "reason": "What the Lord requires: justice, love, walk.", "certainty": "clear"}],
231: [{"reference": "Matthew 23:25", "reason": "Clean outside of cup; inside full of greed.", "certainty": "clear"}],
232: [{"reference": "Matthew 23:29-36", "reason": "Tombs of the prophets; fill up fathers’ measure.", "certainty": "clear"}, {"reference": "Acts 3:15", "reason": "Killed the Author of life.", "certainty": "clear"}],
233: [{"reference": "Matthew 23:35-36", "reason": "Blood of Abel to Zechariah; this generation.", "certainty": "clear"}, {"reference": "Deuteronomy 24:16", "reason": "Fathers not die for children.", "certainty": "clear"}, {"reference": "Genesis 4:23", "reason": "Lamech’s boast of killing.", "certainty": "clear"}],
234: [{"reference": "Matthew 23:36", "reason": "All this will come on this generation.", "certainty": "clear"}, {"reference": "Psalm 112:2", "reason": "Generation of the upright blessed.", "certainty": "clear"}, {"reference": "Psalm 24:6", "reason": "Generation of those seeking the Lord.", "certainty": "clear"}],
235: [{"reference": "Matthew 23:37", "reason": "Hen gathering chicks under wings.", "certainty": "clear"}, {"reference": "Deuteronomy 32:11", "reason": "Spreading wings (LXX echo).", "certainty": "possible"}, {"reference": "Psalm 36:7", "reason": "Shelter of your wings.", "certainty": "clear"}],
236: [{"reference": "Matthew 23:39", "reason": "Blessed is he who comes in the Lord’s name.", "certainty": "clear"}, {"reference": "Romans 11:25", "reason": "Fullness of the nations.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(221, 237):
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
        if n in (221, 222):
            notes.append("Mid-phrase break preserved; invent no Greek.")
        if n == 224:
            notes.append("Supplied <εἰπεῖν> disclosed.")
        if n == 228:
            notes.append("Supplied <τὸ τὰς> disclosed.")
        if n in (232, 236):
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a56a59.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a56a59.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a56",
                        "cyril-matt-frag-a57",
                        "cyril-matt-frag-a58",
                        "cyril-matt-frag-a59",
                    ],
                    "sections": "221-236",
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
