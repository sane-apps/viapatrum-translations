#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a60..a63 (entries 237–252)."""
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
    if n <= 240:
        return "cyril-matt-frag-a60"
    if n <= 244:
        return "cyril-matt-frag-a61"
    if n <= 248:
        return "cyril-matt-frag-a62"
    return "cyril-matt-frag-a63"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(237, 253)}

PASS_A = {
237: "Having-said 'is-left to-you the house of-you' following this he-does having-gone-out from the temple and going and through this showing the from the race of the Jews departure of the divine grace, upon others transferring. Hyperbolically but he-used these, nevertheless also in-deed it-came-out having-been-ruined completely the sanctuary.",
238: "Were-showing some to the Christ the in the temple great-works and the of the offerings adornment; for they-thought, that he-will-marvel with them the being-seen although God being and having throne the heaven. But he leaves-aside on-the-one-hand the about them word, has-foretold but, that from foundations it-will-fall according-to times bringing-down into this it of the of-Romans army and all the Jerusalem the of the Lord-killing penalties demanding from the Israel; for after at-any-rate the of the savior cross these happened to-suffer them, but they not were-understanding of the being-said the power. But they-thought the about completion of the age words to-be-weaving him. They-asked then therefore when these will-be, and what the sign, whenever it-is-about to-happen.",
239: "Follows the aim of those bringing-near the inquiry the Lord and about completion for-now he-says of the present age; for before the from heavens to-happen of him descent forerunners some will-appear, false-christs and false-prophets the of him face to themselves molding-around, but not you-may-follow he-says to them.",
240: "Perhaps also riddle has the word, so-as to-pray us not to-depart from the body neither in idleness being of work good, which indicates the sabbath, neither in unfruitfulness, which makes-clear winter; for it-is-to-be-noted that winter of evils the God not made, in winter but we-are, whenever the passions of the flesh dominate in us. This hints the Christ the to-pray us not to-become in departure of the body neither in idleness being of the of virtue works, which indicates the sabbath, neither being-troubled in the worldly tumults both and disturbances, which makes-clear the winter.",
241: "Just-as of body lying dead the flesh-eating of the birds upon it run-together, thus, whenever the son of the human may-arrive, then indeed all the eagles this is those into the heights flying and uppermost and of the earthly and worldly having-been-lifted upon him will-run-together.",
242: "How not will-they-shudder? Of being-re-elemented for of heaven and earth toward the seeming to the God (precise for something to-say in the such not it-is-possible) the on-the-one-hand sun and the moon will-be-darkened, but the stars as flowers will-fall of the having-created them again re-elementing, as he-wills, will-be-disturbed also themselves the elements; of being-renewed for of the humanity is-recapitulated and is-co-created also the through the human having-been-created creation.",
243: "Since the beyond themselves they-were-wanting to-learn the disciples, opportunity he-finds of the to-hinder them of the such the not to-know insofar-as human and he-says not-even the according-to heaven holy angels to-be-able these to-know.",
244: "Custom to the savior Christ such something to-do upon the holy especially disciples, if on-the-one-hand they-may-inquire something of the as-many-as is of love-of-learning on-the-one-hand having reputation of higher at-least search having-been-freed, to-grant the narration and to-exact that especially to-try finely. But if indeed something they-may-wish of the beyond measure the according-to themselves them superfluously to-learn-again, to-check quietly and to-persuade-otherwise well very to-be-busybodies to-choose the more-fitting and to-do upon these the through which they-may-become conspicuous and most-splendid having the from works good brightness beside God. Having-chosen therefore not I-know how the beyond measure household-slave to-ask both and to-learn, to-be-quiet he-persuades with-reasonings necessary putting-to-shame, that not-even to-angels has-revealed the father nor to-him the son he-makes known, if-indeed someone may-be bare and according-to them human upon earth and not having by-nature the to-be God. Custom it-was to the savior Christ such something to-do upon the holy especially disciples, if they-may-inquire something of the as-many-as was of love-of-learning on-the-one-hand having reputation, of higher at-least search having-been-freed, to-grant the narration and to-exact that especially to-try finely. But if indeed something they-may-wish of the beyond measure the according-to themselves them superfluously to-learn-again, to-wrap quietly and to-persuade-otherwise well very to-be-busybodies to-choose the more-fitting. Since therefore the beyond them they-were-wanting to-learn the disciples, he-pretends usefully the not to-know insofar-as human and he-says not-even themselves to-know the according-to the heaven holy angels, in-order-that not they-may-be-grieved as not having-been-trusted the moderate. And see how to-be-quiet he-persuades with-reasonings own and puts-to-shame, that not-even to-angels has-revealed the father nor to-him the son was-made known.",
245: "If also the completion clear was, what not would they-have-done? If the son wisdom is of the father and if, what things he-knows himself, not knows the wisdom, he-is-found again himself not-knowing or that the nature of him better is of the wisdom of him, and he-is-found composite and unlike to-himself the simple God; yet not the not-to-know and to-know makes of the essence difference just-as not-even upon humans, but passion is the of the ignorance, which not has the son, but God he-is by-nature and according-to the heretics of passions unreceptive. But if all the of the son of the father is and all the of the father of the son, either both not-know or knows the father and the son knows as having of the father all according-to nature to-him being; for not about the lordship of the creatures this he-says; yet whenever names the scripture father, the whole of the in holy trinity being-thought and being-worshipped divinity it-signifies.",
246: "See, that into two ranks divides the word the humans, into both of the being-saved and of the being-destroyed. And the on-the-one-hand being-saved he-says to-be-taken-along, but the being-destroyed to-be-left that-is to-be-rejected. But field is-to-be-understood here the world, where 'the' on-the-one-hand 'into the spirit sowing harvests life eternal, the' but 'into the flesh, corruption'. But to the grinding-women he-likens the teachers, who manner some thinning-out the scriptural thoughts easily-acceptable and easily-understood to the humans the divine oracles they-set-forth; for also law commanding not to-be-taken into pledge millstone or upper-millstone, in-order-that not the of the food tools having-taken someone may-hinder the being-fed through them, riddlingly the teachers he-indicates. Into two ranks divides the humans the Lord, into both the of the being-saved and into the of the being-destroyed; and the on-the-one-hand of the being-saved to-be-taken-along he-says, but the impious to-be-left, which is to-be-rejected. But to the grinding-women the teachers he-likens as thinning the scriptures and easily-acceptable and easily-understood to the humans making; for also the law not to-be-taken into pledge millstone forbids or upper-millstone, so-that not the of the food tools having-taken someone obstacle may-become to the being-fed. Wherefore also riddlingly the savior the teachers indicates.",
247: "Faithful on-the-one-hand into teachings, prudent but into work and of the fellow-slaves steward most-reasonable; for will-be the such of the of the master kingdom whole sharer; for this makes-clear the upon all the belongings of him he-will-set him. Not he-says who is this, but indefinitely, in-order-that he-may-show the scarcity and the high-value of the right teachers. Well but both to-require—but if the-one-or-the-other may-be-absent, the other limps.",
248: "That but the word against the leaders the in luxuries spending-time; for bad and wicked slave he-named the careless teacher, who through the to-be-absent the judge and not to-be-seen through the long-suffering strikes bitterly those under hand and mixes-with the flesh-lovers; for those sinning as not being-present of the judge they-sin and as not reckoning judgment. But through the to-be-struck some from them he-shows those according-to soul being-harmed from the of the leaders luxury, as says the apostle: 'thus but sinning into the brothers and striking of them the conscience being-weak'. He-threatens therefore to the living-luxuriously the last things to-undergo; for he-splits him and divides from him with pains by the living of himself word of the having-been-united to-him in the age spirit that-is of the divine gift; those pretending for the right things to-think not thinking but as it-is-necessary, but the virtue on-the-one-hand outside by-shape only wearing in-two will-be-cut according-to the fearful day of the judgment, which is from the spirit into the continuous alienation; now on-the-one-hand for if also not it-has-been-mixed to the unworthy, but therefore to-be-present somehow it-seems to those once having-been-sealed the from the turning of them salvation awaiting. Then but from whole of the having-profaned of him the gift soul it-will-be-cut-off and with the hypocrites the part of him will-be-set. But hypocrites he-says those the right on-the-one-hand to-teach attempting, through which but they-do harming more the being-discipled. Upon therefore, he-says, of those not according-to the necessary going-to-use in the present life the having-been-entrusted to them ministry from Lord not only not he-will-add other, but also the already participation to them having-come-to-be of the spirit, of which they-obtained toward church ministry having-been-appointed, having-taken-away, thus them he-will-hand-over to the punishment; for not possible with the spirit to-be-handed-over someone into punishment; for not bodily he-hints cut, but the of the adoption of the spirit stripping. They-are-punished therefore instead-of which they-were-laughing, they-will-gnash but 'the teeth' reckoning the end of the pain and the excess of the",
249: "What is the to-be-cut-in-two, let-us-examine. When he-has-become in of-punishment. beginnings the Adam, the most-complete beauty giving-back to the nature the God sharer him he-makes of the own spirit; for 'he-breathed-into' 'into the face of him breath of life'; for the truly life-giving the spirit is of the life, this is of Christ. But since he-slipped from deceit into sin, was-removed the spirit. But of having-been-pleased of the God and father 'to-recapitulate the all in the Christ' and into the ancient to-bring-up beauty the of the humans nature, we-received-back through the grace, what the of the sin intrusion us damaged; for breathed-into Christ to us after the resurrection and into the ancient us renewing beauty; 'receive' he-says 'spirit holy'. Is-united therefore to us the spirit; for 'the one-cleaving to the Lord one spirit is'. Therefore in the according-to piety efforts having-been-caught upon the end the full we-receive-back, as in pledge order the spirit now having, but being-accused in sins also itself we-are-damaged the pledge of the spirit; for it-is-cut-off and departs as-it-were according-to the of the judgment time. And this to-be we-say, which here he-says cutting-in-two; for not possible with the spirit to-be-given someone into punishment.",
250: "In the time of the completion is-taken-away the spirit the holy; for not possible with the spirit to-be-given someone into punishment.",
251: "To virgins he-likens the of the peoples leaders; spotless it-is-necessary to-be the priest soul both and body as also the Paul says, 'in-order-that she-may-be holy both body and the spirit'. But since the all life custom to the scripture into five to-divide, to-each time he-assigns both holy and foolish souls as of each time having wise and simple, just and unjust. But in which all went-out with the lamps, he-shows, that all the souls were-illumined by the God by natural both and innate laws, but indeed also by the through Moses written laws. And all went-out into meeting to the bridegroom instead-of all set-before to-please to the God and to-be-joined spiritually to the bridegroom the sowing in the hearts of the faithful every form of virtue, wherefore also bridegroom he-is-called. Yet indiscriminately some although having the from God illumination not endured reasonably to-live, which did the prudent souls, through works good upon more making to-shine-out the from-within having-been-given to them from God illuminating grace and benefiting both themselves and others into glory of God. Oil is-to-be-understood the love-of-work the good, which not have the idle, of which not being upon the more-unbeautiful transfers the in us divine illumination. But to sleep he-likens and drowsiness he-calls the of the flesh death, which from necessity comes-upon to prudent both and senseless, whom raises the of the angels trumpet according-to the of the presence of the Christ time; for all are-raised of having-been-abolished of the death, good both and bad, and all are-prepared into defense of the judge, which is to-arrange the lamps of each the own reckoning life. But of the base nothing bringing-along begins to-be-gloomy the soul and as-if to-be-quenched and into madness to-go, so-as to-think them through the of others virtue to-be-mercied. Wherefore they-are-rejected of those saying never not may-suffice to-us and to-you; for scarcely will-suffice toward salvation of soul the of each virtue through the many to-stumble also the very reasonable. But go toward the selling, who are prophets, apostles, evangelists, through whom someone learns the virtue to-work, and right teachers of the right doctrines. But of those readily having-gone-away not allowed the time of the having-been-lived making examination not beginning giving of working. Since the all life custom to the scripture into five to-divide, to-each time he-assigns both holy and foolish souls. But in which all went-out with the lamps, he-shows, that all the souls were-illumined by God by the natural and the written law. Yet some the from God illumination not endured reasonably to-live, but some through works good upon more make to-shine-out the from God having-been-given to them illuminating grace and benefit both themselves and others into glory of God. But oil is-to-be-understood the good love-of-work, of which not being upon the more-unbeautiful transfers the in us divine illumination. But to sleep and drowsiness he-likens the of the flesh death, which from necessity to-all comes, whom raises the of the angels trumpet of having-been-abolished of the death, and all are-prepared into defense; for this is the to-arrange the lamps of each the own reckoning life. But of the base begins to-be-gloomy the soul and as-if into madness to-go, so-as to-think them through the of others virtue to-be-mercied. Wherefore they-are-rejected; for scarcely will-suffice toward salvation the of each virtue through the many to-stumble also the very reasonable. But the selling are the of the right doctrines teachers, through whom someone learns the virtue. But to-buy that-is to-be-taught the time not allowed of the having-been-lived making examination not beginning giving of working; of working the present time, but the coming of recompense.",
252: "The souls neglecting of the virtue wither both and as-if are-quenched and into madness they-go having-thought in the second presence of the savior to-be-able to-be-saved without of the of the virtues working. Wherefore also they-are-rejected by the prudent saying toward them: never not may-suffice to-us both and to-you; for this indicates here the scarcely ever to-be-able to-be-saved someone through the own virtue, not indeed through the of the others; for foolish the not working someone wage to-have-received of the working.",
}

PASS_B = {
237: [
    "Having said, “Your house is left to you,” he does the matching act: he goes out from the temple and walks on, and by this shows the departure of divine grace from the Jewish race as it transfers to others. He used strong language; yet it also came about in deed when the sanctuary was utterly ruined."
],
238: [
    "Some were showing Christ the great works in the temple and the adornment of the offerings; for they supposed he would marvel with them at what was seen — though he is God and has heaven as his throne. He sets aside talk about those things, but has foretold that it will fall from its foundations in due times, when the Roman army brings it to that end and all Jerusalem exacts from Israel the penalties for killing the Lord. For after the Savior’s cross these things happened to them to suffer, yet they did not understand the force of what was said. They supposed he was weaving words about the completion of the age. So they asked when these things would be, and what the sign would be when it was about to happen."
],
239: [
    "The Lord follows the aim of those who bring the question, and for now speaks about the completion of the present age. For before his descent from the heavens takes place, some forerunners will appear — false christs and false prophets molding his face around themselves — but do not follow them, he says."
],
240: [
    "Perhaps the word also has a riddle, so that we should pray not to depart from the body either while idle of good work — which the sabbath hints — or in unfruitfulness — which winter makes clear. For it should be noted that God did not make a winter of evils; yet we are in winter whenever the passions of the flesh dominate in us.",
    "This is what Christ hints: that we should pray not to be in departure from the body, nor idle of the works of virtue — which the sabbath indicates — nor troubled in the worldly tumults and disturbances, which winter makes clear."
],
241: [
    "Just as when a dead body lies there the flesh-eating birds run together upon it, so, when the Son of Man arrives, then all the eagles — that is, those who fly into the heights and highest places and have been lifted above earthly and worldly things — will run together to him."
],
242: [
    "How will they not shudder? For as heaven and earth are re-elemented toward what seems good to God (it is not possible to say something precise in such matters), the sun and the moon will be darkened, and the stars will fall like flowers, while the one who created them re-elements them again as he wills; the elements themselves will also be disturbed. For as humanity is renewed, the creation made because of the human is also recapitulated and co-created."
],
243: [
    "Since the disciples wanted to learn things beyond themselves, he finds an opening to check them from such inquiries in not knowing insofar as he is human, and he says that not even the holy angels in heaven can know these things."
],
244: [
    "It is the Savior Christ’s custom to do something like this with his holy disciples especially: if they inquire into things that have a reputation for love of learning yet are free of higher searching, he grants the account and tries to make it exact with fine care. But if they want to learn over-again things beyond the measure that fits them, he checks them quietly and strongly persuades them to choose busying themselves with what is more fitting, and to do in those things what will make them conspicuous, having the brightest radiance from good works before God. So when they somehow chose to ask and learn things beyond a household slave’s measure, he persuades them to be quiet with necessary reasonings that put them to shame: that the Father has not revealed it even to angels, nor makes it known to the Son himself — if one were a bare human on earth like them and did not have it by nature to be God.",
    "It was the Savior Christ’s custom to do something like this with his holy disciples especially: if they inquired into things that had a reputation for love of learning yet were free of higher searching, he would grant the account and try to make it exact with fine care. But if they wanted to learn over-again things beyond the measure that fits them, he would wrap the matter quietly and strongly persuade them to choose busying themselves with what is more fitting. So since the disciples wanted to learn things beyond them, he usefully pretends not to know insofar as he is human, and says that not even the holy angels in heaven know, so that they may not be grieved as if not trusted with what is moderate. And see how he persuades them to be quiet with his own reasonings and puts them to shame: that the Father has not revealed it even to angels, nor was it made known to the Son himself."
],
245: [
    "Even if the completion was clear, what would they not have done? If the Son is the wisdom of the Father, and if what he himself knows wisdom does not know, he is found again not knowing — or else his nature is better than his wisdom, and the simple God is found composite and unlike himself. Yet not-knowing and knowing do not make a difference of essence, any more than they do among humans; ignorance is a passion, which the Son does not have, but he is God by nature and, even on the heretics’ terms, unreceptive of passions. But if all that is the Son’s is the Father’s and all that is the Father’s is the Son’s, either both do not know, or the Father knows and the Son knows as having by nature all that is the Father’s. For he does not say this about lordship over creatures; yet whenever scripture names “Father,” it signifies the whole of the divinity thought and worshipped in the holy Trinity."
],
246: [
    "See that the word divides humans into two ranks — the saved and the destroyed. He says the saved are taken along, and the destroyed are left, that is, rejected. By “field” here understand the world, where “the one sowing to the Spirit harvests eternal life, and the one sowing to the flesh, corruption.” He likens teachers to the women grinding, who in a way thin out the scriptural thoughts and set the divine oracles before humans as easily accepted and easily understood. For the law also, commanding that a millstone or upper millstone not be taken in pledge so that someone who takes the tools of food may not hinder those fed through them, indicates teachers in a riddle.",
    "The Lord divides humans into two ranks — the saved and the destroyed. He says the saved are taken along, and the impious are left, which is to be rejected. He likens teachers to the women grinding as thinning the scriptures and making them easily accepted and easily understood by humans. For the law also forbids taking a millstone or upper millstone in pledge, so that someone who takes the tools of food may not become an obstacle to those being fed. That is why the Savior also indicates teachers in a riddle."
],
247: [
    "Faithful in teachings, prudent in work, and a most reasonable steward of fellow-slaves: for such a one will share in the master’s whole kingdom. That is what “he will set him over all his belongings” makes clear. He does not say who this is, but speaks indefinitely, to show how scarce and precious right teachers are. He rightly requires both; if either is missing, the other limps."
],
248: [
    "The word is against leaders who spend their time in luxuries. For he named the careless teacher a bad and wicked slave, who, because the judge is absent and not seen through long-suffering, strikes those under his hand bitterly and mixes with flesh-lovers. For those who sin sin as if the judge were not present and as if they were not reckoning on judgment. By some of them being struck he shows those harmed in soul by the leaders’ luxury, as the apostle says: “Thus sinning against the brothers and striking their weak conscience.” So he threatens those living in luxury with undergoing the last things. For he splits him and divides him from himself with pains by his living word — from the Spirit united to him in the age, that is, the divine gift. Those who pretend to think right things but do not think as they ought, wearing virtue only by outward shape, will be cut in two on the fearful day of judgment, which is lasting alienation from the Spirit. For now, even if it has not been mixed into the unworthy, it somehow seems present to those once sealed, awaiting the salvation that comes from their turning. Then it will be cut off from the whole soul that profaned its gift, and his portion will be set with the hypocrites. By “hypocrites” he means those who try to teach what is right, yet through what they do harm the disciples more. So, he says, for those who will not use in the present life as they ought the ministry entrusted to them by the Lord, he will not only add nothing further, but taking away the participation in the Spirit already come to be in them — which they obtained when appointed to church ministry — he will thus hand them over to punishment. For it is not possible for someone to be handed over to punishment together with the Spirit; he does not hint a bodily cut, but the stripping of the Spirit’s adoption. So they are punished for what they were laughing at, and they will “gnash their teeth,” reckoning the end of the pain and the excess of the"
],
249: [
    "Let us examine what it is to be cut in two. When Adam came to be in the beginnings of punishment — God, giving nature its most complete beauty, makes him sharer of his own Spirit. For “he breathed into his face a breath of life”; for what truly gives life is the Spirit of life, that is, of Christ. But since he slipped from deceit into sin, the Spirit was removed. When God and Father was pleased “to recapitulate all things in Christ” and to bring human nature back up into its ancient beauty, we received back through grace what the intrusion of sin had damaged in us. For Christ breathed into us after the resurrection, renewing us into the ancient beauty: “Receive,” he says, “holy Spirit.” So the Spirit is united to us; for “the one cleaving to the Lord is one spirit.” Therefore, if we are found at the end in efforts according to piety, we receive back the fullness — now having the Spirit as in the order of a pledge — but if we are accused in sins we are damaged even of the Spirit’s pledge itself; for it is cut off and departs, as it were, at the time of judgment. And this, we say, is the cutting in two of which he speaks here; for it is not possible for someone to be given over to punishment together with the Spirit."
],
250: [
    "In the time of the completion the Holy Spirit is taken away; for it is not possible for someone to be given over to punishment together with the Spirit."
],
251: [
    "He likens the leaders of the peoples to virgins. The one who serves as priest must be spotless in soul and body, as Paul also says, “that she may be holy in body and in spirit.” Since scripture customarily divides all of life into five, he assigns to each time both holy and foolish souls, as each time has wise and simple, just and unjust. In that they all went out with the lamps, he shows that all souls were illumined by God with natural and innate laws, and also with the written laws through Moses. And all went out to meet the bridegroom — that is, all set themselves to please God and to be joined spiritually to the bridegroom who sows in the hearts of the faithful every form of virtue, which is why he is also called bridegroom. Yet some, though having the illumination from God, did not endure to live reasonably — which the prudent souls did, through good works making the illuminating grace given them from within by God shine out still more, and benefiting both themselves and others to the glory of God. By oil understand good love of work, which the idle do not have; when it is absent, the divine illumination in us passes over toward what is less beautiful. He likens to sleep, and calls drowsiness, the death of the flesh, which of necessity comes upon both the prudent and the senseless, whom the angels’ trumpet raises at the time of Christ’s presence. For all are raised when death is abolished, good and bad, and all are prepared for defense before the judge — that is, to arrange the lamps as each reckons his own life. When the base bring nothing along, the soul begins to be gloomy and as if quenched and to go into madness, so that they think they will be mercied through others’ virtue. That is why they are rejected when those say, “Perhaps it will not suffice for us and for you.” For each person’s virtue will scarcely suffice for the soul’s salvation, because even the very reasonable stumble in many things. “But go to those who sell” — who are prophets, apostles, evangelists, through whom one learns to work virtue, and right teachers of right doctrines. When they went away readily, the time did not allow it, making examination of what had been lived and not giving a beginning of working.",
    "Since scripture customarily divides all of life into five, he assigns to each time both holy and foolish souls. In that they all went out with the lamps, he shows that all souls were illumined by God with the natural and the written law. Yet some did not endure to live reasonably with the illumination from God, while some through good works make the illuminating grace given them from God shine out still more and benefit both themselves and others to the glory of God. By oil understand good love of work; when it is absent, the divine illumination in us passes over toward what is less beautiful. He likens the death of the flesh to sleep and drowsiness, which of necessity comes upon all, whom the angels’ trumpet raises when death is abolished, and all are prepared for defense; for this is to arrange the lamps as each reckons his own life. For the base the soul begins to be gloomy and as if to go into madness, so that they think they will be mercied through others’ virtue. That is why they are rejected; for each person’s virtue will scarcely suffice for salvation, because even the very reasonable stumble in many things. Those who sell are the teachers of right doctrines, through whom one learns virtue. But to buy — that is, to be taught — the time did not allow, making examination of what had been lived and not giving a beginning of working. The present time is for working; the coming one is for recompense."
],
252: [
    "Souls that neglect virtue wither and are as if quenched, and they go into madness, having thought that at the Savior’s second presence they can be saved without the working of the virtues. That is why they are also rejected by the prudent who say to them, “Perhaps it will not suffice for us and for you.” For this indicates here that someone can scarcely ever be saved through his own virtue, and certainly not through that of others; for it is foolish that someone who does not work should have received the wage of the working."
],
}

LEMMAS = {
237: [], 238: [], 239: [], 240: [], 241: [], 242: [], 243: [],
244: [], 245: [], 246: [], 247: [],
248: [{"form": "mid-phrase end", "lemma": "—", "gloss": "extract breaks after τῆς", "lexica": "editorial"}],
249: [{"form": "mid-phrase start", "lemma": "—", "gloss": "ἐν κολάσεως. ἀρχαῖς break", "lexica": "editorial"}],
250: [], 251: [], 252: [],
}

CHOICES = {
237: [], 238: [{"term": "ed.fr.267 skip", "english": "source jumps 266→268", "rejected": ["invent fr.267"], "why": "Edition fragment numbers skip; disclose, do not renumber."}],
239: [], 240: [{"term": "double witness block", "english": "translate both parallel notes", "rejected": ["collapse silently"], "why": "Extract carries two close catena notes."}],
241: [], 242: [], 243: [],
244: [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two witness forms in the extract."}],
245: [],
246: [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two witness forms in the extract."}],
247: [{"term": "stray ‘35’", "english": "digit stripped in clean Greek", "rejected": ["keep as text"], "why": "Page/verse digit, not Greek."}],
248: [{"term": "mid-phrase break", "english": "stop after ‘excess of the’", "rejected": ["invent completion"], "why": "Copy-text ends mid-phrase after τῆς."}],
249: [{"term": "mid-phrase break", "english": "preserve κολάσεως. ἀρχαῖς seam", "rejected": ["smooth lacuna"], "why": "Extract opens with broken seam; invent no Greek."}],
250: [],
251: [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two long witness forms; stray ‘37’ stripped."}, {"term": "stray ‘37’", "english": "digit stripped in clean Greek", "rejected": ["keep as text"], "why": "Page/verse digit, not Greek."}],
252: [],
}

ALLUSIONS = {
237: [{"reference": "Matthew 23:38-24:1", "reason": "House left; departure from temple.", "certainty": "clear"}],
238: [{"reference": "Matthew 24:1-3", "reason": "Temple buildings; when will these be?", "certainty": "clear"}],
239: [{"reference": "Matthew 24:4-5", "reason": "False christs; do not follow.", "certainty": "clear"}],
240: [{"reference": "Matthew 24:20", "reason": "Pray flight not in winter or sabbath.", "certainty": "clear"}],
241: [{"reference": "Matthew 24:28", "reason": "Wherever the corpse is, eagles gather.", "certainty": "clear"}],
242: [{"reference": "Matthew 24:29", "reason": "Sun darkened; stars fall.", "certainty": "clear"}],
243: [{"reference": "Matthew 24:36", "reason": "Day and hour unknown; not even angels.", "certainty": "clear"}],
244: [{"reference": "Matthew 24:36", "reason": "Unknown to angels; pedagogical not-knowing.", "certainty": "clear"}],
245: [{"reference": "Matthew 24:36", "reason": "Son’s knowledge; anti-Arian argument.", "certainty": "clear"}],
246: [{"reference": "Matthew 24:40-41", "reason": "One taken, one left; women grinding.", "certainty": "clear"}, {"reference": "Galatians 6:8", "reason": "Sowing to Spirit / flesh.", "certainty": "clear"}, {"reference": "Deuteronomy 24:6", "reason": "Millstone not taken in pledge.", "certainty": "clear"}],
247: [{"reference": "Matthew 24:45-47", "reason": "Faithful and wise servant set over all.", "certainty": "clear"}],
248: [{"reference": "Matthew 24:48-51", "reason": "Wicked servant; cut in two; gnash teeth.", "certainty": "clear"}, {"reference": "1 Corinthians 8:12", "reason": "Sinning against brothers; weak conscience.", "certainty": "clear"}],
249: [{"reference": "Matthew 24:51", "reason": "Dichotomēthēnai / cut in two.", "certainty": "clear"}, {"reference": "Genesis 2:7", "reason": "Breathed breath of life.", "certainty": "clear"}, {"reference": "Ephesians 1:10", "reason": "Recapitulate all in Christ.", "certainty": "clear"}, {"reference": "John 20:22", "reason": "Receive holy Spirit.", "certainty": "clear"}, {"reference": "1 Corinthians 6:17", "reason": "One spirit with the Lord.", "certainty": "clear"}],
250: [{"reference": "Matthew 24:51", "reason": "Spirit removed at consummation.", "certainty": "clear"}],
251: [{"reference": "Matthew 25:1-13", "reason": "Ten virgins; oil; sellers.", "certainty": "clear"}, {"reference": "1 Corinthians 7:34", "reason": "Holy in body and spirit.", "certainty": "clear"}],
252: [{"reference": "Matthew 25:8-9", "reason": "Give us of your oil; not enough for us and you.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(237, 253):
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
        if n == 238:
            notes.append("Edition fragment numbers skip 267 after 266; disclose, do not renumber.")
        if n in (240, 244, 246, 251):
            notes.append("Parallel catena witness blocks both translated; not silently merged.")
        if n in (247, 251):
            notes.append("Stray page/verse digits stripped in clean Greek.")
        if n == 248:
            notes.append("Source extract ends mid-phrase after τῆς; invent no Greek.")
        if n == 249:
            notes.append("Source extract opens with mid-phrase seam (κολάσεως. ἀρχαῖς); invent no Greek.")
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a60a63.json",
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
        print("wrote", out.name, claim, "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a60a63.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a60",
                        "cyril-matt-frag-a61",
                        "cyril-matt-frag-a62",
                        "cyril-matt-frag-a63",
                    ],
                    "sections": "237-252",
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
