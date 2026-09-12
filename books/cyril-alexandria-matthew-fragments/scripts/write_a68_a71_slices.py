#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a68..a71 (entries 269–284). Reader titles: On Matthew only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    t = re.sub(r"^(\d{1,2})\s+", "", t)
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def reader_title(matthew: str) -> str:
    """Reader H1/TOC: plain English + Mt ch/v. No CPG/fr."""
    m = (matthew or "").strip().replace("-", "–")
    return f"On Matthew {m}" if m else "On Matthew"


def claim_for(n: int) -> str:
    if n <= 272:
        return "cyril-matt-frag-a68"
    if n <= 276:
        return "cyril-matt-frag-a69"
    if n <= 280:
        return "cyril-matt-frag-a70"
    return "cyril-matt-frag-a71"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(269, 285)}

PASS_A = {
269: "Then therefore does Christ accuse the of the Jews leaders, that not early to-him the of the death snare they-were-preparing? Not this he-wants to-make-clear, but that being-possible to-you day by day in the temple teaching to-seize, not you-seized; for I-was-reserving rather the to-be-necessary to-suffer at-time the fitting. Not therefore of Jews' madness accusing these the Christ said, nor indeed he-rebukes the slowness of them toward bloodshed, that indeed present and being-seen not in beginnings they-seized; he-convicts but rather as not of the in-them power work the arrest, but of his will of the the unwanted suffering economically having-accepted and having-made willed. Not since was the to-suffer good, but that the from it resulting the of-human nature were-about to-restore into the from beginning showing, that of his permission work was the to-take.",
270: "Said somewhere through Moses the of the all God: 'if a soul may-sin and may-hear voice of adjuration, and this one witness or has-seen or has-known, if not he-may-report', he-says, 'he-will-receive the sin'. Was-being-inscribed therefore of lawlessness charge to-some, if nothing they-may-answer, voice hearing of adjuration. Through this craftily adjures the Lord the Caiaphas, in-order-that if he-may-wish also after this to-be-silent, as having-transgressed he-may-condemn, knowing, that having-been-adjured and having-been-silent liable he-became to-penalty the from the law; but if he-may-say the true, as false-christ him they-may-kill as saying himself God nothing more having of the other humans according-to the flesh and the being-seen. Wherefore the Christ said: you said instead-of the your confessed mouth henceforth. But in-order-that more-burdensome to-them the judgment he-may-work, the upon at-least I-mean the not to-believe into him to-wish, again to-them clear the of him he-makes glory saying: you-will-see from now the son of the human sitting from right of the power of the God. In form, he-says, the according-to you having-become me the son by nature and truly of the God and father in the nothing you-have-made account, and since of ignorance into this you-have-descended, so-as the of him both and the my you-not-know mystery, although law-learned being, necessarily that I-say, that of the against me impiety short to-you and delimited was-given time until of the precious cross; after this for immediately into the of himself I-will-run-back honor, I-will-ascend toward glory the in beginnings, co-sitter I-will-be to the God and father also with the flesh. These of saying of the Christ the Caiaphas tore the garments of him saying: he-blasphemed. This but he-did more-vehement the accusation making and the having-been-said raising through the act. And-yet what blasphemy this—this especially both shone and conquered by force.",
271: "It-would-befit to-say what said one of the holy prophets: 'was-amazed the heaven upon this and shuddered upon more exceedingly, says' the 'Lord' the of the all God, the king of those-being-kinged and lord of those-being-lorded; as one from us he-is-dishonored and endures being-struck and the from the impious he-undergoes laugh type to-us of the into extreme forbearance of him setting-beside; for the 'examining hearts and kidneys' the of prophecy all giver how would he-have-not-known who is the having-struck him?",
272: "They-brought to Pilate the Jesus; were-handed-over also themselves to the of-Romans armies. And has-been-fulfilled the through the holy prophets upon them having-been-foretold; the on-the-one-hand says: 'woe to the lawless; evil things according-to the works of him will-happen to him'. But the: as 'you-did, thus will-be to-you; the recompense of you will-be-repaid into the head of you'.",
273: "Great proof these of the Jews robber and murderer having-chosen rather than the Christ; so-much to-them it-cared of the just and thus through the piety they-were-accusing of Christ; and of the to-judge having-obtained freeing him of death verdict to-undergo they-exhort the of all piety leader and teacher, <and> in-order-that still more-burdensome they-may-undergo the punishment, they-cried-out saying: 'take this one, release to-us the Barabbas'. See indeed clearly 'the holy and just they-denied' as says the blessed Peter 'and they-asked a man murderer to-be-granted' to-them, in-order-that of that one's portion they-will-be sharers.",
274: "Having-neglected of the right and just judgment the Pilate not-even reasoned to-give-over guiltless into death although master being of the to-deliver him; and he-washes the hands having-supposed himself through this of the sin free, which is foolish to-think. Perhaps but as gentile he-was-thinking, that suffices itself toward cleansing of sins the water.",
275: "This of them the unholy outcry was-blaming saying the Lord through voice of Jeremiah: 'I-have-abandoned the house of me, I-left the inheritance of me <I-gave the beloved soul of me into hands of enemies of her. Became the inheritance of me> to-me as lion in thicket; he-gave upon me the voice of her, through this I-hated her'. Said somewhere about of the of Jews unholiness also the prophet Hosea: 'woe to them, that they-leaped-away from me; wretched they-are, that they-acted-impiously into me; but I redeemed them, but they spoke-against against me false. Will-fall in sword the rulers of them through lack-of-education of tongue of them'.",
276: "Is-led on-the-one-hand the savior upon the saving suffering. But to Simon Cyrenean they-placed the cross of him. But another of the holy evangelists also himself said the Jesus 'to-bear' the wood. True but wholly both; for bore on-the-one-hand the cross the savior, according-to middle somehow the road having-met the Cyrenean they-seized and they-transferred upon him <the> cross. For it-has-been-said about him through voice of Isaiah, that 'child was-born to-us, son also was-given to-us, of whom the rule upon of the shoulder of him'; for rule of him became the cross, through which he-has-reigned of the under heaven, if-indeed is true, that 'until death' he-became 'obedient, of death but of cross, wherefore also the God him highly-exalted'.",
277: "About of the skull place it-came to us, that Hebrews hand-down the body of the Adam there to-have-been-buried and since 'in the Adam all' die, rose also the Adam and 'in Christ all will-be-made-alive'.",
278: "You-saw how the of the all creator and lord the of him nature corrects; for this into the in beginnings bringing-back through the to-become according-to us through us the of us on-behalf of us he-underwent sufferings. But to having-been-hung of the cross were-hung-with to-him two robbers and insult on-the-one-hand admittedly the at-least reaching into the of the Jews aim yet reminder of prophecy saying: 'and with lawless he-was-reckoned'. But through the of him sufferings into us runs the goods; for true, that 'by the bruise of him we were-healed'. The two these robbers the two were-outlining peoples, of whom the on-the-one-hand until end the senselessness displayed and not-even the last captivity, which under Romans he-underwent, into defense of the against Christ outrages he-confessed to-undergo, but the toward itself the end not despaired of the forgiveness, but the raw of the evils by theology corrected. Both indeed middle of the robbers cross to-undergo the lord the voluntary of him <death the> toward the two peoples revealed presence. Toward whom willingly he-was-coming, both by the of himself incarnation having-willed to-renew, even-if the former as the one of the robbers refused, 'not we-have' saying 'king except Caesar' and the blood the guiltless upon the of himself head demanding and as just to the murder exulting, from which also these and that-one commonly of the kingdom fell-out.",
279: "The on-the-one-hand one of the robbers to the of the Jews godlessness co-dwelling the same as those was-belching words; for if 'you are', he-says, 'the Christ, save yourself and us'. But at-least the other the opposite to that-one walking road fittingly is-marvelled; for he-has-believed into him although of punishment having-been-hung thus bitter, he-rebukes the of the Jews loose-mouthedness and the of the co-hung voices, he-confessed the sin, in-order-that more-just he-may-appear; for he-has-witnessed to Christ the blameless wholly and of the of the crucifiers madness accuser he-was, thus indeed the of the holy he-seized lot, the above and in heavens enrollment. For being-crucified seeing king he-was-calling; the in dishonor and suffering he-expected to-come in glory God-befitting, he-seized the faith, although nobly not having-been-raised, benefits but also us <opening to-us the> heavens.",
280: "The darkness upon whole the earth became from hour sixth until hour ninth of the sun failing, in-order-that they-may-know, that himself is that-one the having-been-hung of the wood the ally on-behalf of them the creation having-taken, when to the Egyptians he-has-warred through them. The solar failed light and of all of their country was-scattered the darkness of sun the ray having-drawn-in and as-if not enduring to-send it still to the having-become lord-killers. And according-to other but manner to-have-been-darkened we-say the of Jews country or-at-least the inhabiting it, that not received the sun of the righteousness and 'the light the true'.",
281: "Said the lord the voice this as human, in-order-that he-may-set-right to the our of the humans nature the with boldness to-say toward the God, for what me you-abandoned; for only to the pure and of sin outside is fearless this to-say. But saying my God toward the father nothing he-undergoes harm about the own divinity and glory by-nature God being, whenever as human he-may-say these the to the humanity befitting, since also we, if we-may-call the God father, not beside this we-threw-off the to-be humans by-nature and creatures of God, even-if according-to grace us the God into sonship may-call through the into Christ faith.",
282: "Great and exceptional was-accomplished through Christ to the our souls; since for we-have-been-justified through the into God faith and in him the faultlessness the of-human nature was-found having-become-rich, he-has-innovated to-us the no-longer on-the-one-hand into Hades to-run the of the bodies being-released souls as also formerly, to-be-sent but rather into hands of God living. And this having-known the holy said Stephen: 'Lord Jesus, receive the spirit of me'. And another but writes of the apostles: 'so-that also those suffering according-to the will of the God to faithful creator let-them-entrust the' of themselves 'souls'.",
283: "Was-shaken but also the earth the upon the better transfer signifying or also shows the against of those into him having-outraged indignation. But the to-be-split the rocks sign is of the the 'stony' of the nations 'heart' to-be-opened toward reception of the gospel seed. But the having-risen holy and having-appeared to the many not premature received alone those the of the resurrection gift, but into sign it-became, that was-abolished the death through of the death of the Christ. Into this I-think also the law was-looking commanding the unwillingly having-killed having-fled again to-run-back into the fatherland after the death of the high-priest; for the of the Christ death the into the above Jerusalem ascent to the liable us gave-back. Was-shaken the earth signifying the upon the better transfer of the things even-if the indignation it-may-show of the God against of those having-outraged into him. But the to-be-split the rocks the of the gentile souls to-be-opened makes-clear into the to-receive the of the Christ faith. But the having-risen of the holy and having-appeared to-many signify, that was-abolished the death through of the death of the Christ.",
284: "The to-be-torn the veil sign was not unclear of the also itself all-but to-mourn the temple and those into ruin and destruction having-been-brought-down, who the of itself of the temple master they-crucified; perhaps but also upon impiety the against Christ through of the beside them custom convicting them of the having-happened; for custom was to Jews the clothing to-be-torn-around of having-been-blasphemed of God. But it-seems also something other of the necessary into benefit to-hint to-us the having-happened; for the veil hiding within the holies of the holies of having-arrived of time, according-to which it-was-necessary to-be-drawn-together the of the law shadow and the in types to-cease worship, to-be-opened but the holies of the holies to those through faith the into Christ having-been-justified, is-torn-around showing as-it-were them of the God to the worthy, in-order-that henceforth of restraining nothing into the inner they-may-run tent those according-to track going of Christ.",
}

PASS_B = {
269: [
    "Does Christ then blame the Jewish leaders because they were not already laying an early snare of death for him? That is not what he means. Rather: though you could seize me day by day while I taught in the temple, you did not — for I was saving the need to suffer for the fitting time. So Christ did not say this as accusing Jewish madness, nor as rebuking their slowness toward bloodshed because they did not seize him at the outset when he was present and seen. He convicts them rather that the arrest was not the work of power in them, but of his will, who economically accepted the unwanted suffering and made it willed — not because suffering was good in itself, but because what would follow from it was about to restore human nature to what it was from the beginning, showing that taking him was the work of his permission."
],
270: [
    "God of all said somewhere through Moses: “If a soul sins and hears a voice of adjuration, and he is a witness or has seen or known, if he does not report it, he will receive the sin.” So a charge of lawlessness was written against people if they answered nothing when they heard an adjuring voice. That is why Caiaphas craftily adjures the Lord: so that if he still wished to be silent after this, Caiaphas might condemn him as a transgressor — knowing that one adjured who stays silent becomes liable to the law’s penalty — but if he spoke the truth, they might kill him as a false christ for calling himself God while, in the flesh and what is seen, having nothing more than other humans. That is why Christ said, “You have said it” — instead of “your own mouth has now confessed it.”",
    "And so that he might make the judgment against them heavier — I mean the judgment on their unwillingness to believe in him — he again sets his glory plainly before them, saying, “From now on you will see the Son of Man sitting at the right hand of the power of God.” “Me, who have become in the form that is yours, the Son by nature and truly of God the Father, you have made of no account; and since you have sunk to such ignorance that you do not know his mystery and mine, though you are learned in the law, I necessarily say this: that only a short and bounded time was given you for impiety against me, as far as the precious cross; for after this I will at once run back into my own honor, ascend to the glory that was in the beginning, and sit with God the Father even with the flesh.” While Christ said this, Caiaphas tore his garments, saying, “He has blasphemed.” He did this to make the accusation fiercer and to raise what was said by the act. And yet what blasphemy was this? This especially both shone and conquered by force."
],
271: [
    "One might fittingly say what one of the holy prophets said: “Heaven was amazed at this and shuddered still more exceedingly, says the Lord,” the God of all, the King of those who reign and Lord of those who lord it. He is dishonored as one of us, endures being struck, and undergoes the laugh of the impious, setting beside us a pattern of his extreme forbearance. For how could the one who “examines hearts and kidneys,” the giver of all prophecy, not have known who it was that struck him?"
],
272: [
    "They brought Jesus to Pilate — and they themselves were handed over to the Roman armies. And what was foretold about them through the holy prophets has been fulfilled. One says, “Woe to the lawless; evils will come upon him according to his works.” Another: “As you did, so it will be to you; your recompense will be repaid on your head.”"
],
273: [
    "These things are a great proof against the Jews, who chose a robber and murderer rather than Christ. So little did justice matter to them, and thus, for “piety,” they were accusing Christ. And though the one appointed to judge was freeing him, they urge a death verdict against the leader and teacher of all piety, <and>, so that they might undergo a still heavier punishment, they cried out, “Take this one; release Barabbas to us.” See clearly: they “denied the Holy and Righteous One,” as blessed Peter says, “and asked that a murderer be granted them,” so that they would be sharers of that man’s portion."
],
274: [
    "Pilate, neglecting right and just judgment, did not even reason that he was giving an innocent man over to death, though he was master of delivering him. And he washes his hands, having supposed that through this he was free of the sin — which is foolish to think. Perhaps, as a gentile, he imagined that the water itself sufficed for cleansing of sins."
],
275: [
    "The Lord was blaming this unholy outcry of theirs through Jeremiah’s voice: “I have abandoned my house; I have left my inheritance; <I have given my beloved soul into the hands of her enemies. My inheritance has become> to me like a lion in a thicket; she raised her voice against me; therefore I hated her.” Somewhere Hosea also spoke about the Jews’ unholiness: “Woe to them, for they leaped away from me; they are wretched, for they acted impiously against me. I redeemed them, but they spoke false things against me. Their rulers will fall by the sword through the lack of training of their tongue.”"
],
276: [
    "The Savior is led to the saving suffering. They laid his cross on Simon of Cyrene. Another of the holy evangelists also said that Jesus himself “bore” the wood. Both are wholly true: the Savior bore the cross, and somewhere in the middle of the road they met the Cyrenean, seized him, and transferred <the> cross onto him. For it was said about him through Isaiah’s voice: “A child was born to us, a son also was given to us, whose rule is upon his shoulder.” For his rule became the cross, through which he has reigned over what is under heaven — if it is true that he “became obedient unto death, even death of a cross; therefore God also highly exalted him.”"
],
277: [
    "About the Place of the Skull it has come down to us that the Hebrews hand on that Adam’s body was buried there; and since “in Adam all die,” Adam also rose, and “in Christ all will be made alive.”"
],
278: [
    "You saw how the Creator and Lord of all corrects his nature: bringing it back to what was in the beginning by becoming as we are, he underwent our sufferings for us, through us. Two robbers were hung with him when he hung on the cross — an insult, admittedly, as far as the Jews’ aim went, yet also a reminder of the prophecy that says, “And he was reckoned with the lawless.” But through his sufferings the goods run to us; for it is true that “by his bruise we were healed.”",
    "These two robbers were outlining the two peoples. One displayed senselessness to the end and would not even confess that the last captivity he underwent under the Romans was being borne as requital for the outrages against Christ. The other, at the very end, did not despair of forgiveness, but corrected the rawness of evils by theology. And the Lord’s undergoing the cross in the middle of the robbers revealed <his voluntary death as> his presence toward the two peoples — toward whom he was coming willingly, having willed to renew both by his own incarnation — even if the former people refused like the one robber, saying, “We have no king except Caesar,” demanding the guiltless blood on their own head and exulting in the murder as just, from which both they and that robber alike fell out of the kingdom."
],
279: [
    "One of the robbers, sharing the Jews’ lovelessness toward God, belched out the same words as they: “If you are the Christ, save yourself and us.” But the other, walking the opposite road, is fittingly marvelled at. He has believed in him though hung in so bitter a punishment; he rebukes the Jews’ loose-mouthedness and the co-hung man’s voices; he confessed the sin so that he might appear more just. For he bore witness that Christ was wholly without blame and was an accuser of the crucifiers’ madness; and so he seized the lot of the holy — the enrollment above and in the heavens. Seeing him crucified, he was calling him king; he expected the one in dishonor and suffering to come in God-befitting glory; he seized the faith though not raised in nobility — and he also benefits us, <opening the> heavens <to us>."
],
280: [
    "Darkness came upon the whole earth from the sixth hour until the ninth, the sun failing, so that they might know that the one hung on the wood is that very one who took creation as ally for them when he warred against the Egyptians for their sake. The sun’s light failed, and darkness was scattered over their whole country, the sun drawing in its ray and as if no longer enduring to send it to those who had become killers of the Lord. And in another way we say the Jews’ country — or those who inhabit it — was darkened, because it did not receive the sun of righteousness and “the true light.”"
],
281: [
    "The Lord spoke this cry as a human, so that he might set right for our human nature the freedom to say boldly to God, “Why have you abandoned me?” — for only the pure and those outside sin may say this without fear. And when he says “my God” to the Father, he undergoes no harm regarding his own divinity and glory, being God by nature, whenever as a human he says what befits humanity — since we too, if we call God Father, do not thereby cast off being humans by nature and creatures of God, even if by grace God calls us into sonship through faith in Christ."
],
282: [
    "Something great and exceptional was accomplished for our souls through Christ. Since we have been justified through faith in God, and in him human nature was found enriched with faultlessness, he has opened something new for us: that souls released from bodies no longer run into Hades as before, but are rather sent into the hands of the living God. Knowing this, holy Stephen said, “Lord Jesus, receive my spirit.” And another of the apostles writes, “So that those who suffer according to God’s will should also entrust their souls to a faithful Creator.”"
],
283: [
    "The earth was also shaken, signifying the transfer toward what is better — or also showing indignation against those who had outraged him. The splitting of the rocks is a sign that the nations’ “stony heart” was opened to receive the gospel seed. The holy who rose and appeared to many did not alone receive the gift of resurrection ahead of time; it became a sign that death was abolished through Christ’s death. I think the law was also looking toward this when it commanded that one who killed unwillingly and fled should run back again to the homeland after the high priest’s death; for Christ’s death gave us who were liable the ascent into the Jerusalem above.",
    "The earth was shaken, signifying the transfer of things toward what is better, even if it shows God’s indignation against those who outraged him. The splitting of the rocks makes clear that gentile souls were opened to receive the faith of Christ. The holy who rose and appeared to many signify that death was abolished through Christ’s death."
],
284: [
    "The tearing of the veil was no unclear sign that the temple itself all but mourned, and those brought down into ruin and destruction who crucified the Master of that very temple — perhaps also convicting them, through the custom among them, of impiety against Christ. For it was a Jewish custom to tear clothing around when God was blasphemed. But what happened also seems to hint something else needful for our benefit: the veil that hid the holies of holies within, when the time arrived in which the law’s shadow had to be drawn together and the worship in types to cease, and the holies of holies to be opened to those justified through faith in Christ, is torn around, God as it were showing them to the worthy, so that henceforth, with nothing restraining, those who go in Christ’s track may run into the inner tent."
],
}

LEMMAS = {n: [] for n in range(269, 285)}
LEMMAS[273] = [{"form": "<καὶ>", "lemma": "καί", "gloss": "supplied ‘and’", "lexica": "editorial"}]
LEMMAS[275] = [{"form": "<ἔδωκα…ἐμοὶ>", "lemma": "—", "gloss": "supplied stretch in Jeremiah citation", "lexica": "editorial"}]
LEMMAS[276] = [{"form": "<τὸν>", "lemma": "ὁ", "gloss": "supplied article", "lexica": "editorial"}]
LEMMAS[278] = [{"form": "<θάνατον τὴν>", "lemma": "θάνατος", "gloss": "supplied ‘death the’", "lexica": "editorial"}]
LEMMAS[279] = [{"form": "<ἀνοίγων ἡμῖν τοὺς>", "lemma": "ἀνοίγω", "gloss": "supplied ‘opening to us the’", "lexica": "editorial"}]

CHOICES = {n: [] for n in range(269, 285)}
CHOICES[280] = [{"term": "ed.fr.310 skip", "english": "source jumps 309→311", "rejected": ["invent fr.310"], "why": "Edition fragment numbers skip; disclose, do not renumber."}]
CHOICES[283] = [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two witness forms in the extract."}]
for n, forms in ((273, "<καὶ>"), (275, "supplied Jeremiah stretch"), (276, "<τὸν>"), (278, "<θάνατον τὴν>"), (279, "<ἀνοίγων ἡμῖν τοὺς>")):
    CHOICES[n] = [{"term": forms, "english": "disclose editor supply", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}]

ALLUSIONS = {
269: [{"reference": "Matthew 26:55", "reason": "Day by day in the temple; you did not seize me.", "certainty": "clear"}],
270: [{"reference": "Matthew 26:63-65", "reason": "Caiaphas adjures; you have said; blasphemy.", "certainty": "clear"}, {"reference": "Leviticus 5:1", "reason": "Hearing adjuration and not reporting.", "certainty": "clear"}],
271: [{"reference": "Matthew 26:67-68", "reason": "Struck; prophesy who hit you.", "certainty": "clear"}, {"reference": "Jeremiah 2:12", "reason": "Heaven amazed; shuddered.", "certainty": "clear"}],
272: [{"reference": "Matthew 27:11", "reason": "Jesus before Pilate.", "certainty": "clear"}],
273: [{"reference": "Matthew 27:21-26", "reason": "Barabbas preferred to Jesus.", "certainty": "clear"}, {"reference": "Acts 3:14", "reason": "Denied the Holy and Righteous; asked a murderer.", "certainty": "clear"}],
274: [{"reference": "Matthew 27:24", "reason": "Pilate washes hands.", "certainty": "clear"}],
275: [{"reference": "Matthew 27:25", "reason": "His blood be on us.", "certainty": "clear"}, {"reference": "Jeremiah 12:7-8", "reason": "Abandoned house; inheritance as lion.", "certainty": "clear"}, {"reference": "Hosea 7:13-16", "reason": "Woe; leaped away; rulers fall by sword.", "certainty": "clear"}],
276: [{"reference": "Matthew 27:32", "reason": "Simon of Cyrene bears the cross.", "certainty": "clear"}, {"reference": "Isaiah 9:6", "reason": "Rule upon his shoulder.", "certainty": "clear"}, {"reference": "Philippians 2:8-9", "reason": "Obedient unto cross; God exalted him.", "certainty": "clear"}],
277: [{"reference": "Matthew 27:33", "reason": "Golgotha, Place of a Skull.", "certainty": "clear"}, {"reference": "1 Corinthians 15:22", "reason": "In Adam all die; in Christ all made alive.", "certainty": "clear"}],
278: [{"reference": "Matthew 27:38", "reason": "Two robbers crucified with him.", "certainty": "clear"}, {"reference": "Isaiah 53:12", "reason": "Reckoned with the lawless.", "certainty": "clear"}, {"reference": "Isaiah 53:5", "reason": "By his bruise we were healed.", "certainty": "clear"}, {"reference": "John 19:15", "reason": "No king but Caesar.", "certainty": "clear"}],
279: [{"reference": "Matthew 27:44", "reason": "Robbers also reviled him.", "certainty": "clear"}],
280: [{"reference": "Matthew 27:45", "reason": "Darkness from sixth to ninth hour.", "certainty": "clear"}, {"reference": "Malachi 4:2", "reason": "Sun of righteousness.", "certainty": "possible"}, {"reference": "John 1:9", "reason": "True light.", "certainty": "clear"}],
281: [{"reference": "Matthew 27:46", "reason": "My God, my God, why have you forsaken me?", "certainty": "clear"}],
282: [{"reference": "Matthew 27:50", "reason": "Jesus yielded up his spirit.", "certainty": "clear"}, {"reference": "Acts 7:59", "reason": "Lord Jesus, receive my spirit.", "certainty": "clear"}, {"reference": "1 Peter 4:19", "reason": "Entrust souls to a faithful Creator.", "certainty": "clear"}],
283: [{"reference": "Matthew 27:51-54", "reason": "Earthquake; rocks split; saints raised.", "certainty": "clear"}],
284: [{"reference": "Matthew 27:51", "reason": "Veil of the temple torn.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(269, 285):
        src = BY[n]
        a, b = PASS_A[n], " ".join(PASS_B[n])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {n}")
        claim = claim_for(n)
        ed = src["fragment"]
        notes = [
            "Copy-text khazarzar Aegean PG 72 extract.",
            f"CPG 5206 fr.{ed} (apparatus/meta only; not reader title).",
            "Section id = source array order (1-based).",
            "IA OCR not reading text.",
        ]
        if n == 280:
            notes.append("Edition fragment numbers skip 310 after 309; disclose, do not renumber.")
        if n == 283:
            notes.append("Parallel catena witness blocks both translated; not silently merged.")
        if n in (273, 275, 276, 278, 279):
            notes.append("Editor-supplied text in angle brackets disclosed.")
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
                "title": reader_title(src["matthew"]),
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a68a71.json",
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
        out = ROOT / f"reviews/justifications/matt_frag_{n}.json"
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name, claim, reader_title(src["matthew"]), "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a68a71.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a68",
                        "cyril-matt-frag-a69",
                        "cyril-matt-frag-a70",
                        "cyril-matt-frag-a71",
                    ],
                    "sections": "269-284",
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
    print("english updated through", max(CLEAN))


if __name__ == "__main__":
    main()
