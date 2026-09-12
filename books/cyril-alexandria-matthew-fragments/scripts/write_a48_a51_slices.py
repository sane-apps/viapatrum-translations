#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a48..a51 (entries 189–204)."""
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
    if n <= 192:
        return "cyril-matt-frag-a48"
    if n <= 196:
        return "cyril-matt-frag-a49"
    if n <= 200:
        return "cyril-matt-frag-a50"
    return "cyril-matt-frag-a51"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(189, 205)}

PASS_A = {
189: "Since some much and hard-to-number of demons multitude this the all wanders with-many-turned deceits the according to us overturning, from-heaven to us he-set-over the Christ the tutors not as of the of human nature the lesser carrying-off—far indeed also it-needs; for far of the according to us those and clear the word—but as to the of the demonic excesses the own strength opposing and of the our life to-contend-for being-able; he-has-set-right but also this with the other all to the our souls the Christ. Long-ago on-the-one-hand of us having-been-ruined had-been-shut the heaven and none of the according to us they-were-making account the angels as-if with the of all master jointly-indignant as having-been-insulted. But since it-pleased the God 'to-sum-up the all in the Christ', he-brought-down having-come upon earth also the holy angels and of the our life guardians he-appointed. Wherefore also he-was-saying: 'you-will-see the heaven having-been-opened and the angels of the God going-up and going-down upon the son of the human'. 'Of the human', this is through the human; for having-been-shut according to the already having-passed times he-opened to us the heaven, in-order-that through us upward and downward running servants some they-may-be of the into us being-accomplished economy through Christ. This therefore also the Paul says: 'not all are liturgical spirits' and following. This has the indication also of the dreams <of the> forefather of us Jacob the power; he-has-seen, as he-said, 'the ladder' reaching from earth 'into the heaven', nothing I-think signifying <of the dream> other than that according to times ascent and descent will-be to the holy angels through the human shining in world with flesh of the only-begotten. Most-dreadful therefore then those of such care having-been-deemed-worthy beside God as overseers and tutors angels to-obtain in the in nothing to-have-been-ranked account and this beside us the fellow-slaves and brothers.",
190: "Since he-gives to those the to-teach having-obtained authority of the to-loose and to-bind the Christ not of migrating of those once having-turned toward desire of virtue, it-is-necessary to-fear the of the holy voices, even-if not many some they-may-be those defining; for he-has-assured also this us the Christ, not indeed wholly that what from many will-be firm having-said, but if also two the number concordantly and carefully they-may-define, into end to-come having-promised; for I-will-be-with he-says and I-will-define-with, if alone two may-be-gathered through me; for not <the> of those being-with number, but the of the piety and God-loving power effective to-become he-says.",
191: "Of being-forgiven to us of the of all God the hard of the faults, through the many is-shown talents, if not to the fellow-slaves we-may-remit ourselves the 100 denarii, this-is the few worldly slips from the being-in them hatred-of-evil, the of the according to us standing-over angels and under the same to us being of the mastery yoke the beside God they-make accusation not as to not-knowing signifying—for all he-knows as God—requesting but rather according to the likely usefully to-be-disciplined those having-chosen to-despise and the of the mutual-love to-dishonor laws. But if indeed we-may-suffer the upon these payment, either we-are-disciplined according to the present life as-if by some torturers by-trials and illnesses being-sent or at-least into age the coming being-punished. But that disciplines God convertibly the disobedient and hard-to-lead transforming upon the better, not-toilsome to-see; for full of the such the divine scripture, of-which-sort is the wisely having-been-said 'whom loves Lord he-disciplines, he-scourges but every son, whom he-accepts' and again 'into discipline you-endure' and following.",
192: "Through the sale of the wife and of the rest is-signified of the beside God pleasant-things the into all removal and falling-away complete. But the sale shows the alienation clearly the from God; for alien of God toward whom ever may-become word the bitter that and unsmiling: 'depart from me workers' of the lawlessness; for 'not-yet' 'I-knew you'.",
193: "Of having-said of the Christ if you-wish into the life to-enter, or 'straightway the keep the commands nothing other that one having-expected to-say him mine' he-says; which? But much of the hope he-was-erring; for not, what he-thought, toward him answered the Christ, but upon the law he-leads-up him, not that perfection the law (for 'is-justified' 'no-one in law' according to the having-been-written), but that entrance some as-if of the into age life the according to law practice according to little habituating to the higher of those being-tutored the mind. For 'has-become' to us 'the law tutor into Christ'; beginning therefore of bodily polity the law, perfection but the Christ; for beginning, he-says, of the goods the to-do just-things. Shows on-the-one-hand the just the law, but the good the Christ. The on-the-one-hand therefore was-teaching to the equals to-ward-off those to-wrong wanting (for 'tooth' 'instead of tooth' and 'eye instead of eye'), but the the equal-balancing having-released us upon the greater ... for to the striking you 'into the right, turn to him also the other; and to the wanting with you to-go-to-law', he-says, 'and the tunic of you to-take, leave to him also the cloak'.",
194: "Camel but here he-says not the animal the burden-bearing, but the thick rope, in which they-bind the anchors the sailors. Not impossible wholly this he-shows being, but by the very difficult already somehow near and next-door of the impossible the matter placing. Whence is-shown not the ordinary—need of the grace to the about this to-accomplish.",
195: "Not would become someone of passions free into all having soul even if very someone may-be of the that most most-industrious; for 'who clean from filth' according to the having-been-written or 'who will-boast pure to-have the heart'? But if also the 'having-stumbled in one, has-become of all liable' according to the of the to-be-condemned word, who would not be-held-liable the remaining the upon one transgression not-even having-fled? For not even would he-escape the according to mind to-sin also the very sober. As-much therefore it-came into human weakness, no-one the being-saved; as-much at-least into the of the saving gentleness, not despairable the salvation; for not every sin toward death.",
196: "In-order-that not someone may-think upon only of the disciples to-fit the having-been-said, he-widened upon all the word those the like doing; for if also not of the same to the disciples will-obtain the rest, but nevertheless they-will-have instead on-the-one-hand of the according to flesh kin the toward God intimacy and the brotherhood the toward the holy (or the elders and elder-women of the church he-says, whom they-had through love as kin, the according to disposition beloved, the by-much more of the according to flesh kin loving, from whom also moneys they-received, in-order-that they-may-manage them as they-wish, being-laid-up to them also of the about-to-be goods), instead but of the fields the paradise and instead of houses of the from stones the above Jerusalem, the of the firstborns mother. To-be-noted, that even-if not of the same to the disciples the rest may-obtain, but nevertheless they-will-have instead on-the-one-hand of the according to flesh kin toward God intimacy and the brotherhood the toward holy city the of the firstborns mother.",
197: "Not many therefore instead of one fathers or many instead of one mother or fields instead of few many to-receive he-says, but that of the earthly all with-incomparable excellences will-surpass the heavenly and of the being-lost will-be more-preferred the being-saved.",
198: "Has-added but the Luke also about wife; this but according to the Paul commanding to-honor 'elder-women on-the-one-hand as mothers, younger but as sisters in all purity'; just-as therefore brothers he-gives the not brothers and parents the not parents and children the not children, thus also wife the not wife by other manner clearly spiritual the intimacies fulfilling, not bodily. But to-leave the according to flesh race good it-is through the spiritual life; for then he-says to-be-separated from parents and from wife, whenever toward impiety they-may-drag; for just-as it-is-necessary of soul and of body to-despise through piety, thus it-is-necessary also of all this to-prefer.",
199: "Fleeing the glory-loving the Lord as about other he-says householder himself being householder and of the of the heavens kingdom distributor. Day but he-says the all age, according to which in different times after the of the Adam transgression he-calls some righteous into work God-reverent wage to them having-set upon the works. Are therefore about the first hour those about the Adam and the Enoch, but those about the third those about Noah and Shem and those from them righteous; for second the time and the call second, when also different the ordinances. But those about the sixth having-been-called workers those according to the Abraham are times, upon whom again the of the circumcision legislation, the eleventh those according to the of Christ presence, upon whom also alone is-said the what here you-do whole the day idle, that of Lord hope not having and godless in the world and idle in every work good resembling those in marketplace standing and nothing wholly handling, but vainly and idly the of themselves running-through life. Whom also he-exhorts the Lord saying: what you-stand (thus saying) idle? Toward whom they-answer-back saying: no-one us hired; for neither Moses nor someone of the holy preached to the nations, but only to the Israel. Nevertheless the Lord sends-in also them into the vineyard. Five but calls <he-says> to-have-become, in-order-that he-may-show, that in each time there-were succeeding and missing as the 'five virgins prudent and the foolish five' show according to the same being times, and that some virtuous were-found, but some despised through folly of the coming age. Upon end but of the life, which is evening (for the from the advent of the Christ time until the consummation is the after the eleventh hour just-as the John says: 'last hour it-is'), in which the householder, he-says, from the last <commands> to-be-given the wage. Householder but may-be-understood <as> the father using the son as distributor not as servant, but as <co-worker> that through him he-administers and works all, what ever he-wishes. He-gives but to all the each denarius, which is the of the spirit grace conforming making the holy to God and the above characters in the of those souls engraving and into life leading-up and incorruption. In these but the first seem more of the last to-have-toiled as the of the devil burning upon more having-endured not-yet of the sin having-been-abolished and of the corruption and of the death; for the matter, if according to equality it-may-be-examined, more something to the former owed suggests, that of death and of devil ruling they-were-living; for this is the burden of the day and the heat, when not-even the of the spirit dew was-present helping toward righteousness to humans. But the last instead of toils the of the master having generosity first the wage receive, since all those after the advent through the baptism and the toward the spirit union 'of divine' have-become 'sharers nature' and sons of God they-were-named of those before the advent all born of women being-named, about-to but also themselves toward this to-be-called; for if also they-have-become partakers of spirit the prophets, but nevertheless not as the faithful, manner some of the holy spirit to the of the faithful souls as-if of leaven having-become and whole the human transforming into other of life state. Wherefore also 'of divine' we-become 'sharers nature' and from boldness we-cry 'abba the father'. But the more-ancient not of the same obtained grace. Wherefore also the Paul says: 'for not you-received spirit of slavery again into fear, but you-received spirit of adoption' as that the ancient 'spirit of slavery' were-receiving not having the of the adoption dignity. First therefore having-received the intelligible denarius necessarily of the others to-have-been-preferred we-are-said.",
200: "You-ask, if remaining some are-about to-sit; learn, that no-one; for of alone of the first substance the such is and not of human; for not having-understood the apostles what is the to-sit 'upon twelve thrones' and that the to-be-glorified then shows such they-were-seeking seat.",
201: "Before five days of the saving of him passion to-fulfill wanting also the voices of the prophets the about him having-been-said he-commands to the two disciples to-go-away into the village the opposite Bethphage and Bethany and to-bring the unbroken colt of him. But that on-the-one-hand the Matthew donkey and colt to-have-brought to the Lord says, but Luke and Mark of one only beast they-recalled, not of conflict the having-been-said; for of the colt being-led according to the having-been-commanded by the disciples sprang-upon also the donkey to the of her child following as affectionate mother.",
202: "Two but he-says to-be the disciples, which is apostles and evangelists, who have-become co-workers and servants of Christ toward this. Or also angels he-says those serving to Christ toward our ransom 'going-up and going-down upon the son of the human'. But if may-ask the having-bound them with the cords of the sins 'what you-do', but nevertheless not being-able to-withstand to the of the savior words he-will-be-silent not willing through the exceeding of the power; but divine the call in this has-been-shown.",
203: "Coming is-said the Christ as from-above having-come, that God being by-nature and son of the father he-became human and he-came in name of Lord the Lord being-called. This therefore as by-nature God blessed is-said, this-is being-glorified. He-was-sitting on-the-one-hand therefore upon the colt Christ, was-following but the having-borne. And sign to us of most-necessary matter the being-done was; for he-rested the Christ upon the new people the idol-worshiping once, will-follow but according to times also the of the Jews synagogue, although in time the according to the call the older having; for it-had-been-called-before through Moses and prophets. But since it-has-struck-against the saving God, through this justly of the colt behind it-comes scarcely and has-become into tail, this-is attendant and behind of those from nations also the first has-become last. Observe but, how into last irrationality having-been-carried he-showed the of human nature the 'kidneys' knowing 'and hearts'; for to donkey is-likened to the very most-irrational also the of the Jews synagogue and itself but of the nations the multitude; for those on-the-one-hand 'having-served to the creation beside the having-created' God, but those the tutor dishonoring law outside mind and of understanding having-become good and toward every form of baseness having-turned 'were-compared to the cattle the senseless and have-been-likened to them' according to the of the psalmist voice. Donkey but also otherwise of uncleanness symbol; for unholy the animal and the from law condemnation having. Such but all those wandering and sin-loving.",
204: "Is-led the colt of two disciples having-been-sent from Christ; for they-serve toward this to him two orders, prophets and apostles, through whom are-netted into faith the nations. And it-is-led from some village, in-order-that also from this the rustic of the nations he-may-show mind not in law having-been-raised, having-lived but rather carelessly and wildly, yet it-changed upon the gentler; for it-has-become under Christ these teaching. And children but 'palms of palms' having-raised were-running-before him and together with the disciples the doxology they-were-composing, in-order-that also through them the new and from nations as-if in tablet having-been-written we-may-see people; for it-has-been-written: 'and people the being-created will-praise the Lord'.",
}

PASS_B = {
189: [
    "Because a great and hard-to-count host of demons wanders this whole world, overturning our affairs by many kinds of deceit, Christ has set tutors over us from heaven — not as if human nature were inferior (far from it; they are far above what is ours, and the point is clear), but as ones who oppose demonic greed with their own strength and are able to contend for our life. With everything else, Christ has also set this right for our souls.",
    "Long ago, when we were ruined, heaven was shut, and the angels took no account of any of us, as if sharing the Master of all’s indignation at the insult. But when God was pleased “to sum up all things in Christ,” he came to earth, brought the holy angels down, and appointed them guardians of our life. That is why he also said, “You will see heaven opened, and the angels of God ascending and descending on the Son of Man” — “of Man,” that is, for the sake of the human. Heaven, shut in the times already past, he opened for us, so that running up and down for our sake they might be servants of the economy accomplished for us through Christ.",
    "Paul too says this: “Are they not all ministering spirits,” and what follows. Jacob our forefather’s dreams have the same force: he saw, as he said, “the ladder” reaching from earth “to heaven,” and <the dream> signifies nothing else, I think, than that in due times there will be ascent and descent for the holy angels because the Only-Begotten shines in the world with flesh for the human. It is most dreadful, then, that those deemed worthy of such care from God — allotted angels as overseers and tutors — should be ranked as of no account, and that by us, their fellow-servants and brothers."
],
190: [
    "Since Christ gives those appointed to teach authority to loose and to bind — once people have turned toward desire for virtue and do not wander off again — one must fear the holy ones’ voices, even if those who decide are not many. Christ has also assured us of this: he did not say a decision is firm only when it comes from many, but promised that if even two should decide in concord and with care, it will come to pass. “For I will be with them,” he says, “and join in the decision, if only two are gathered because of me.” It is not <the> number of those present, he says, but the power of piety and love of God that will be effective."
],
191: [
    "When the God of all forgives us the hard faults — shown by the many talents — if we ourselves do not remit to fellow-servants the hundred denarii, that is, the few worldly slips, then from the hatred of evil in them the angels set over us, who share the same yoke of mastery with us, make accusation before God — not as informing one who does not know (for he knows all as God), but rather, as is fitting, asking that those who choose to despise and dishonor the laws of mutual love be usefully disciplined.",
    "And if we suffer the repayment for these things, either we are disciplined in the present life, as if handed over to torturers by trials and illnesses, or at least we are punished in the age to come. That God disciplines convertibly, transforming the disobedient and hard to lead toward what is better, is easy to see; for divine scripture is full of such things — as in the wise saying, “Whom the Lord loves he disciplines, and he scourges every son he accepts,” and again, “Endure for discipline,” and what follows."
],
192: [
    "Through the sale of the wife and the rest is signified the total removal and complete falling away of the pleasant things from God. The sale shows alienation from God; for those to whom that bitter, unsmiling word comes are alien to God: “Depart from me, workers of lawlessness; for I never knew you.”"
],
193: [
    "When Christ said, “If you want to enter into life,” or “keep the commandments,” that man, expecting him to say nothing other than “mine,” asks, “Which?” But he was much mistaken in his hope. Christ did not answer him as he thought, but leads him up to the law — not because the law is perfection (“no one is justified in the law,” according to what is written), but because practice according to the law is a kind of entrance to eternal life, little by little habituating the mind of those being tutored toward what is higher. For “the law has become our tutor unto Christ.” So the law is the beginning of bodily conduct, and Christ is perfection; for the beginning of goods, he says, is to do what is just. The law shows the just; Christ shows the good.",
    "The law taught us to ward off with equals those who want to wrong us (“tooth for tooth” and “eye for eye”); but Christ, releasing us from that balance, leads us to the greater … “To the one who strikes you on the right cheek, turn the other also; and to the one who wants to go to law with you and take your tunic,” he says, “leave him the cloak as well.”"
],
194: [
    "By “camel” here he does not mean the burden-bearing animal, but the thick rope with which sailors bind the anchors. He does not show this as wholly impossible, but by the extreme difficulty places the matter somehow near and next door to the impossible. From this it is clear that the one about to accomplish it is no ordinary person — he needs grace."
],
195: [
    "No one would have a soul free of passions in every respect, even if he were among the most industrious. For “who is clean from filth,” according to what is written, or “who will boast of having a pure heart?” And if “the one who stumbles in one thing has become liable for all,” as far as the word of condemnation goes, who would not then be held for the remaining single transgression, not even having escaped? For even the very sober would not escape sinning in the mind. So as far as human weakness goes, no one is saved; but as far as the Savior’s gentleness goes, salvation is not to be despaired of — for not every sin is unto death."
],
196: [
    "So that no one may think what was said fits only the disciples, he widened the word to all who do the like. Even if the rest will not obtain the same things as the disciples, they will still have, instead of kin according to the flesh, intimacy with God and brotherhood with the holy — he means the elders and elder women of the church, whom they had through love as kin, beloved by disposition, loving far more than fleshly kin, from whom they also received money to manage as they wish, with the goods to come also stored up for them — and instead of fields, paradise, and instead of houses of stone, the Jerusalem above, mother of the firstborn.",
    "Note that even if the rest do not obtain the same as the disciples, they will nonetheless have, instead of fleshly kin, intimacy with God and brotherhood toward the holy city, mother of the firstborn."
],
197: [
    "He does not say they will receive many fathers instead of one, or many mothers instead of one, or many fields instead of few, but that the heavenly will surpass all earthly things with incomparable excellences, and what is being saved will be preferred to what is being lost."
],
198: [
    "Luke has also added concerning a wife — according to Paul, who commands to honor “elder women as mothers, younger as sisters in all purity.” Just as he gives brothers who are not brothers, parents who are not parents, and children who are not children, so also a wife who is not a wife, fulfilling the intimacies in another, clearly spiritual manner, not bodily. Leaving the race according to the flesh is good for the spiritual life; for he says to separate from parents and from a wife when they drag toward impiety. Just as one must despise soul and body for piety, so one must also prefer this to all things."
],
199: [
    "Fleeing love of glory, the Lord speaks as about another householder, though he himself is householder and distributor of the kingdom of the heavens. By “day” he means the whole age, in which at different times after Adam’s transgression he calls some righteous into God-reverent work, setting them a wage for the works.",
    "Those about the first hour are those around Adam and Enoch; those about the third, around Noah and Shem and the righteous from them — for the time is second and the call second, when the ordinances also differ. The workers called about the sixth are those in Abraham’s times, when again came the legislation of circumcision; those of the eleventh, those at Christ’s presence, of whom alone it is said, “Why do you stand here idle all day?” — having no hope of the Lord, godless in the world, idle in every good work, like those standing in the marketplace handling nothing at all, but running through their life vainly and to no purpose. The Lord also exhorts them, saying, “Why do you stand idle?” They answer, “No one hired us” — for neither Moses nor any of the holy ones preached to the nations, but only to Israel. Still the Lord sends them too into the vineyard.",
    "He <says> five calls happened, to show that in each time some succeeded and some missed — as the “five prudent virgins and the five foolish” show, being in the same times — and that some were found virtuous, while some despised the coming age through folly. At the end of life, which is evening (for the time from Christ’s advent until the consummation is the time after the eleventh hour, as John says, “It is the last hour”), the householder, he says, <commands> the wage to be given beginning from the last. The householder may be understood <as> the Father, using the Son as distributor not as a mere servant but as <co-worker>, because through him he administers and works whatever he wills.",
    "He gives each a denarius — the Spirit’s grace, conforming the holy to God, engraving the heavenly characters in their souls, and leading them up into life and incorruption. In this the first seem to have toiled more than the last, having endured the devil’s burning longer while sin, corruption, and death were not yet abolished. If the matter is weighed by equality, something more seems owed to the former, because they lived while death and the devil ruled — that is the burden of the day and the heat, when not even the Spirit’s dew was present helping humans toward righteousness. But the last, having the Master’s generosity instead of toils, receive the wage first, since all after the advent, through baptism and union with the Spirit, have become “sharers of the divine nature” and were named sons of God, while all before the advent were named born of women — though they too are to be called to this. For even if the prophets became partakers of the Spirit, it was not as the faithful: somehow the Holy Spirit becomes like leaven in the faithful’s souls and transforms the whole human into another state of life. That is why we become “sharers of the divine nature” and cry out boldly, “Abba, Father.” The more ancient did not obtain the same grace. So Paul says, “You did not receive a spirit of slavery again unto fear, but you received a spirit of adoption” — meaning the ancients received a “spirit of slavery,” not having the dignity of adoption. Having received the intelligible denarius first, we are necessarily said to have been preferred above the others."
],
200: [
    "You ask whether some are still going to sit. Learn that no one will. Such a thing belongs to the first substance alone, not to what is human. For the apostles, not understanding what it is to sit “on twelve thrones” and what being glorified then means, were seeking that sort of seat."
],
201: [
    "Five days before his saving passion, wanting also to fulfill the prophets’ voices spoken about him, he commands the two disciples to go away into the village opposite Bethphage and Bethany and bring him the unbroken colt. That Matthew says a donkey and a colt were brought to the Lord, while Luke and Mark recalled only one beast, is no conflict: when the colt was being led as the disciples were commanded, the donkey also sprang along, following her child as an affectionate mother."
],
202: [
    "He says the disciples are two — that is, apostles and evangelists — who became Christ’s co-workers and servants for this. Or he also means angels who serve Christ for our ransom, “ascending and descending on the Son of Man.” And if the one who bound them with the cords of sins asks, “What are you doing?” still, unable to withstand the Savior’s words, he will fall silent — not willingly, because of the excess of power. In this the call is shown to be divine."
],
203: [
    "Christ is said to be “coming” as one who came from above: being God by nature and Son of the Father, he became man and came in the Lord’s name, being called Lord. So as God by nature he is called blessed — that is, glorified. Christ was sitting on the colt, and the mother followed. What was done was a sign for us of a most necessary matter: Christ rested on the new people that once worshiped idols, and in due times the Jews’ synagogue will also follow — though in the time of the call it had the older place, having been called first through Moses and the prophets. But because it struck against the saving God, it justly comes behind the colt only with difficulty and has become a tail — that is, an attendant behind those from the nations — and the first has become last.",
    "See how he who knows “kidneys and hearts” showed human nature carried into the last irrationality: both the Jews’ synagogue and the multitude of the nations are likened to a donkey, the most irrational of all. For some “served the creation rather than the Creator” God, and others, dishonoring the tutoring law, went outside good mind and understanding and turned toward every form of baseness; “they were compared to senseless cattle and made like them,” according to the psalmist’s voice. A donkey is also otherwise a symbol of uncleanness; for the animal is unholy and has condemnation from the law. Such are all who wander and love sin."
],
204: [
    "The colt is led when two disciples have been sent from Christ; for two orders serve him for this — prophets and apostles — through whom the nations are netted into faith. And it is led from a village, so that from this too he may show the rustic mind of the nations, not raised in the law, but living rather carelessly and wildly — yet it changed toward the gentler, for it came under Christ teaching these things. And children, raising “palm branches,” were running before him and composing the doxology together with the disciples, so that through them too we may see the new people from the nations as if written on a tablet. For it is written: “And a people being created will praise the Lord.”"
],
}

LEMMAS = {
189: [{"form": "<τοῦ ὀνείρου>", "lemma": "ὄνειρος", "gloss": "dream (supplied)", "lexica": "editorial"}],
190: [{"form": "<τὸν>", "lemma": "ὁ", "gloss": "the (supplied)", "lexica": "editorial"}],
191: [],
192: [],
193: [{"form": "…", "lemma": "lacuna", "gloss": "mid-phrase break in copy-text", "lexica": "editorial"}],
194: [{"form": "κάμηλον", "lemma": "κάμηλος", "gloss": "camel / thick rope", "lexica": "patristic"}],
195: [],
196: [],
197: [],
198: [],
199: [{"form": "<συνεργῷ>", "lemma": "συνεργός", "gloss": "co-worker (supplied)", "lexica": "editorial"}],
200: [],
201: [],
202: [],
203: [],
204: [{"form": "βάϊα", "lemma": "βάϊον", "gloss": "palm branch", "lexica": "NT"}],
}

CHOICES = {
189: [{"term": "<τοῦ> / <τοῦ ὀνείρου>", "english": "supplied articles/phrase", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}],
190: [{"term": "<τὸν>", "english": "supplied article", "rejected": ["silent omit"], "why": "Disclose editor-supplied text."}],
191: [],
192: [],
193: [{"term": "… mid-phrase break", "english": "preserve break; no invented Greek", "rejected": ["smooth over gap"], "why": "Copy-text trails mid-thought; Pass B keeps the break."}],
194: [{"term": "κάμηλος", "english": "thick rope (not the animal)", "rejected": ["literal beast only"], "why": "Fragment defines the nautical rope sense."}],
195: [],
196: [],
197: [],
198: [],
199: [{"term": "<λέγει>/<κελεύει>/<η>/<συνεργῷ>", "english": "supplied stretches", "rejected": ["silent omit / invent Greek"], "why": "Disclose all angle-bracket supplies; invent no Greek."}],
200: [],
201: [],
202: [],
203: [],
204: [],
}

ALLUSIONS = {
189: [{"reference": "Matthew 18:10", "reason": "Their angels always behold the Father’s face.", "certainty": "clear"}, {"reference": "John 1:51", "reason": "Angels ascending and descending on the Son of Man.", "certainty": "clear"}, {"reference": "Hebrews 1:14", "reason": "Ministering spirits.", "certainty": "clear"}, {"reference": "Genesis 28:12", "reason": "Jacob’s ladder.", "certainty": "clear"}],
190: [{"reference": "Matthew 18:18-20", "reason": "Bind and loose; two or three gathered.", "certainty": "clear"}],
191: [{"reference": "Matthew 18:24-35", "reason": "Unforgiving servant; talents and denarii.", "certainty": "clear"}, {"reference": "Hebrews 12:6-7", "reason": "Whom the Lord loves he disciplines.", "certainty": "clear"}],
192: [{"reference": "Matthew 18:25", "reason": "Sold, and wife and children.", "certainty": "clear"}, {"reference": "Matthew 7:23", "reason": "I never knew you; depart.", "certainty": "clear"}],
193: [{"reference": "Matthew 19:17-18", "reason": "Keep the commandments; which?", "certainty": "clear"}, {"reference": "Galatians 3:24", "reason": "Law as tutor unto Christ.", "certainty": "clear"}, {"reference": "Matthew 5:38-40", "reason": "Tooth for tooth; turn the other cheek.", "certainty": "clear"}],
194: [{"reference": "Matthew 19:24", "reason": "Camel through the eye of a needle.", "certainty": "clear"}],
195: [{"reference": "Matthew 19:26", "reason": "With God all things possible.", "certainty": "clear"}, {"reference": "1 John 5:16-17", "reason": "Sin not unto death.", "certainty": "clear"}],
196: [{"reference": "Matthew 19:29", "reason": "Left houses or brothers… will receive a hundredfold.", "certainty": "clear"}],
197: [{"reference": "Matthew 19:29", "reason": "Hundredfold and eternal life.", "certainty": "clear"}],
198: [{"reference": "Matthew 19:29", "reason": "Left… wife (Luke parallel).", "certainty": "clear"}, {"reference": "1 Timothy 5:2", "reason": "Older women as mothers; younger as sisters.", "certainty": "clear"}],
199: [{"reference": "Matthew 20:1-16", "reason": "Laborers in the vineyard.", "certainty": "clear"}, {"reference": "Matthew 25:1-13", "reason": "Five wise and five foolish virgins.", "certainty": "clear"}, {"reference": "2 Peter 1:4", "reason": "Sharers of divine nature.", "certainty": "clear"}, {"reference": "Romans 8:15", "reason": "Spirit of adoption; Abba Father.", "certainty": "clear"}],
200: [{"reference": "Matthew 20:23", "reason": "To sit at my right and left.", "certainty": "clear"}, {"reference": "Matthew 19:28", "reason": "Sit on twelve thrones.", "certainty": "clear"}],
201: [{"reference": "Matthew 21:1-7", "reason": "Colt and donkey; Bethphage.", "certainty": "clear"}],
202: [{"reference": "Matthew 21:1-3", "reason": "Two disciples sent; the Lord has need.", "certainty": "clear"}, {"reference": "John 1:51", "reason": "Angels ascending and descending.", "certainty": "clear"}],
203: [{"reference": "Matthew 21:7-9", "reason": "Sat on the colt; Hosanna.", "certainty": "clear"}, {"reference": "Romans 1:25", "reason": "Served the creature rather than the Creator.", "certainty": "clear"}, {"reference": "Psalm 49:12", "reason": "Compared to senseless beasts.", "certainty": "clear"}],
204: [{"reference": "Matthew 21:7-9", "reason": "Palm branches; children crying Hosanna.", "certainty": "clear"}, {"reference": "Psalm 102:18", "reason": "A people created will praise the Lord.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(189, 205):
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
        if n == 189:
            notes.append("Supplied <τοῦ> / <τοῦ ὀνείρου> disclosed.")
        if n == 190:
            notes.append("Supplied <τὸν> disclosed.")
        if n == 193:
            notes.append("Mid-phrase break (…) preserved; invent no Greek.")
        if n == 199:
            notes.append("Supplied <λέγει>/<κελεύει>/<η>/<συνεργῷ> disclosed.")
        if n in (198, 199):
            notes.append("Edition fr.223–224 absent from source array (skip).")
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a48a51.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a48a51.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a48",
                        "cyril-matt-frag-a49",
                        "cyril-matt-frag-a50",
                        "cyril-matt-frag-a51",
                    ],
                    "sections": "189-204",
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
