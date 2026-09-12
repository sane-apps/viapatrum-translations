#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a64..a67 (entries 253–268)."""
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
    t = re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)
    return t



def reader_title(matthew: str) -> str:
    m = (matthew or "").strip().replace("-", "–")
    if not m:
        return "On Matthew"
    return f"On Matthew {m}"

def claim_for(n: int) -> str:
    if n <= 256:
        return "cyril-matt-frag-a64"
    if n <= 260:
        return "cyril-matt-frag-a65"
    if n <= 264:
        return "cyril-matt-frag-a66"
    return "cyril-matt-frag-a67"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(253, 269)}

PASS_A = {
253: "Through therefore the boldness of the virginity they-ask to-be-opened to-them. And not he-opens, because according-to time not they-cared-for of-themselves. And this is the 'not I-know you'; for these he-knows, who not only faith they-show, but also works they-have; but those by the-one-or-the-other having-lived not-even in knowledge ever have-become of the bridegroom.",
254: "Man on-the-one-hand householder the of-this of the all creator both and lord. But to-journeying likens of the parable the word either the into heavens ascent of the Christ or-at-least the unseen both and out-of-sight of the divine nature. But belongings is-to-be-understood of God the in each country both and city having-believed into him. But slaves of him he-calls whom according-to times the Christ crowns with the of the priesthood boast; for the inspired writes Paul: 'not to-himself someone takes the honor, but the being-called by the God'. To-these he-hands-over those under him having-become spiritual gift to-each giving, as he-may-have of mind and fitness. This to-be we-say the of the talents distribution not in equal measure to the household-servants being-supplied through the of the understanding differing. Straightway but having-gone they-worked, he-says, of the straightway to-us here signifying, that of delay some without it-would-be-fitting to-work the of God. Those at-least by hesitation and idleness having-been-held in last will-be evils. For he-buried, he-says, the having-been-given to-him talent in the earth, this-is idle both and to-others useless in himself he-kept the gift. Is-taken-away therefore from him the talent and to the being-rich will-be-given; for will-depart from the such the spirit and of the divine gifts the giving, but to those having-worked-lovingly richer some will-be of gifts increase. Householder here is the master Christ as creator of all and lord. But journeying of him the into heavens ascent. It-is but also otherwise to-say; for as unseen to the creation existing and by us sinning not being-seen journeying he-is-said beside the scripture. But belongings of him are the in each country faithful.",
255: "In-order-that not 'before the feast of the passover' to the killers him the betrayer may-hand-over, not has-disclosed the savior either the house or the man, beside whom the passover he-has-fulfilled.",
256: "Having-said the so-and-so not he-makes-clear name specifically, but obliquely he-makes-clear someone of the holy; for it-fits also upon every holy the word, who first on-the-one-hand receives the disciples of the lord, evangelists, apostles leveling-before of him the soul, then thus also himself the Christ, who not having-been-called but spontaneous will-come with the holy spirit dwelling beside that-one, beside whom he-sees the holy baptism; for this makes-clear the man the the 'jar bearing of the water', as says Mark and Luke.",
257: "Not surely we-will-understand from this of the on-the-one-hand others none of disciples, only but the Judas to-have-dipped the morsel in the bowl with him. But I-think I such to-have sense the having-been-said; for he-wants to-say according at-least the likely, that betrayer will-be the having-dipped with me the hand in the bowl, this-is the fellow-diner and table-mate and of table and of salts sharer both and participant; for thus him also through voice of the blessed David he-was-accusing saying: 'but you, man equal-souled, who upon the same you-sweetened to-me foods'. And again: 'the eating breads of me, he-magnified upon me heel-lift'. But itself this more-clearly the John made; for he-said to-have-said the lord, that 'that-one is, to-whom I having-dipped will-give the morsel'.",
258: "Not as of being some either good or base perhaps to those not-yet having-been outside sensation being (still utterly silly the thus to-think), but that to those about-to of misery all inside to-fall, if toward the to-be they-may-be-brought-in by God, much surely and incomparably better the non-existence.",
259: "Gives-thanks the lord having-taken the cup, this-is in shape of prayer he-converses to the God and father sharer as-it-were him and co-approver declaring of the going-to-be-given life-giving blessing to-us, together but also to-us type giving first to-give-thanks and thus to-break the bread and to-distribute. Wherefore also we upon faces of God the having-been-said setting we-beg intently into blessing to-us to-be-remolded the spiritual, in-order-that having-partaken of them we-may-be-sanctified bodily and spiritually. But demonstratively he-said this of-me is body and this of-me is the blood, in-order-that not you-may-think type to-be the appearing, but through some ineffable energy of the all being-able God to-be-changed into body and blood of Christ according-to the true the having-been-brought-forward, of which having-partaken the life-giving and sanctifying power of the Christ we-receive-in; for it-was-necessary him through the holy spirit in us God-befittingly to-be-mingled as-it-were to the our bodies through the holy flesh of him and of the precious blood. Which indeed also we-have-had into blessing life-giving as in bread both and wine, in-order-that not we-may-shrink flesh both and blood lying-before seeing in holy tables of churches; for co-adjusting the God to the our weaknesses he-sends-into the lying-before power of life and transfers them toward energy of the of-himself life. And not you-may-doubt, that this is true of him saying clearly this of-me is the body and this of-me is the blood, receive but rather by-faith of the savior the word; for truth being not he-lies.",
260: "After the to-go-out the Judas he-hands-over the savior to the eleven the saving mystery; since for little later was-about the Christ having-risen with the own flesh to-go-up toward the father, in-order-that the of the body of him presence we-may-have– for without of the presence of the Christ impossible to-be-saved human and to-be-freed of death and of sin not being-with to-us of the life–he-gave therefore to-us the own body both and blood, in-order-that through them also the of the corruption may-be-destroyed power, may-be-indwelt but to the our souls through the holy spirit, and we-may-become of sanctification sharers and heavenly humans and spiritual we-may-be-called. Since after the resurrection was-about the Christ to-be-taken-up toward the father with body, through this he-has-given to-us the own body both and blood, in-order-that being-indwelt in us the of him flesh and the blood may-make us holy and of the immortality sharers.",
261: "Until it I-drink new in the kingdom; of the wine drinking not need fulfills only, but also all-various pleasure to the sense brings. But after the from dead resurrection of having-been-shaken-off of the corruption of the human bodies also itself of the things the nature toward newness will-be-transferred, so-as also itself of us the gladness to-be new. But of temperance symbol the from wine mixture, which also will-become he-says new; and not-at-all entirely the drink he-says will-be new, but the from it resulting, this-is the gladness; for will-withdraw after the resurrection the of-human nature of the of-itself customary and earthly enjoyment, will-transfer but toward newness of luxury of him clearly of the of-all savior of us Christ. The innate and own gladness to the of those worshipping him sending-into souls and proportionally to the of each measures distributing; that but in gladnesses we-will-be intelligible, the divine us David will-assure saying: 'as you-multiplied the mercy of you, the God; but the sons of the humans in shelter of the wings of you will-hope. They-will-be-drunk from fatness and the torrent of the luxury you-will-give-to-drink them'. But the wisdom again 'the of herself wine into bowl having-mixed' and having-set-forth the breads; 'come', she-says, 'eat of the of me breads and drink wine, which I-have-mixed to-you'.",
262: "Were-troubled the disciples not as light some, but that of much was-full of perplexity the matter and hard-to-grasp was the knowledge of the mystery this, how the the dead having-raised and countless having-done signs beyond human into thus dishonorable was-handed-over death. But this was the through the prophet having-said 'I-will-strike the shepherd'. Wherefore also the David says toward the father, 'that whom you struck, themselves they-pursued'. Yet not entirely this and wholly has-happened by-will of the father, but he-was-wanting on-the-one-hand not to-suffer him, if-indeed they-accepted the Jews; but since they not received, he-consented the father to the son this to-suffer having-chosen. Wherefore also it-is-said, that the father struck 'the shepherd', since he-allowed him to-suffer being-able to-prevent not to-suffer. Thus but is-to-be-understood also the having-been-said toward Pilate by Christ, that 'not you-had authority none against me, if not it-was to-you having-been-given from-above', instead-of not consented the father to-me having-chosen to-suffer.",
263: "Not he-left the disciples until of the gloomy to-remain, he-foretells but the resurrection loosing of them the grief and he-promises to-go-before them into the Galilee, through which he-signifies, that he-is-about to-depart of the Jews and into the nations to-transfer. Not from heaven he-appears immediately–wherefore also there he-appeared.",
264: "Is-grieved but as human and the of the soul and the of the body own he-makes the impassible. Since the of the humanity common is to-him, just-as also the only to the divinity befitting common somehow have-become to the flesh through the ineffable and inexpressible union, and not let-scandalize someone the having-happened; for the toward flesh coming-together of the word having-suffered the of-itself will-confirm well in us of the incarnation the mystery.",
265: "Cup in these the through of the death stupefaction he-calls and the as-it-were toward sleep putting-to-sleep drunkenness. The at-least to-decline to-drink it, this-is the not very according-to pleasure to-make the to-suffer, of the of the crucifiers impiety accuses; for not surely they-may-say as since he-chose to-suffer helpers rather we of the will; for will-convict them to-speak-falsely having-chosen the declining.",
266: "He-intensifies the prayer and through the same he-weaves words outline and pattern the according-to himself to-us setting-beside; for I-think it-is-necessary not one us the according-to eagerness <prayer to-offer>, to-approach but rather frequently and repeating-the-same not to-blush until to-us into end may-depart the requests; for through this also third prayer about the same he-was-making Christ although very clearly the of the God and father knowing will; rather but through the third he-was-confirming, that human he-has-become.",
267: "Perhaps somewhere thought the Judas to-be-able to-escape-notice kiss on-the-one-hand holding-forth into type of love, of unholy but plans full having the heart. Therefore as from drunkenness he-approaches to the Christ of deceit and of love instrument the exceptional virtue to-declare expecting, he-was-adding but also the 'rejoice rabbi'. Rejoice you-say to the having-been-ensnared toward death through you? Not-even the shape of the betrayal you-are-ashamed? But it-was from-here to-see, that the liar having in himself, this-is the satan and 'rejoice' saying he-was-lying. And the to-be-kissed he-accepted the Christ–and of the gentleness of beast every harsher he-has-become.",
268: "Twelve he-said legions; instead of-you saying of the twelve disciples, so-that not of the of-you help I-need; for not I-have-used the authority, but I-give-over myself to the Jews, since this going-to-be foretold the scriptures, that these are-about the Jews to-do.",
}

PASS_B = {
253: [
    "So because of the frankness that belongs to virginity they ask that it be opened to them. And he does not open, because in due time they did not care for themselves. And this is “I do not know you”: for he knows those who not only show faith but also have works; but those who have lived by only one of the two have never even come into knowledge of the bridegroom."
],
254: [
    "The “man” who is a householder is the creator and Lord of this whole world. The word of the parable likens his journey either to Christ’s ascent into the heavens or to the unseen and out-of-sight character of the divine nature. By God’s “belongings” understand those in each country and city who have believed in him. He calls “his slaves” those whom Christ in due times crowns with the boast of priesthood; for the inspired Paul writes, “No one takes the honor for himself, but the one called by God.” To these he hands over those who have come under him, giving a spiritual gift to each according to the mind and fitness he has. We say this is the distribution of the talents, not supplied to the household servants in equal measure because of the difference of understanding. “Straightway” they went and worked, he says — the “straightway” here signifying to us that it would be fitting to work the things of God without any delay. Those held by hesitation and idleness will be in the worst evils. For he buried, he says, the talent given to him in the earth — that is, he kept the gift idle in himself and useless to others. So the talent is taken from him and will be given to the one who is rich; for the Spirit and the giving of the divine gifts will depart from such people, while for those who have worked lovingly there will be a richer increase of gifts.",
    "The householder here is the Master Christ as creator of all and Lord. His journeying is the ascent into the heavens. One may also say it otherwise: as existing unseen to creation and not seen by us when we sin, he is said in scripture to be journeying. His belongings are the faithful in each country."
],
255: [
    "So that the betrayer might not hand him over to his killers “before the feast of the Passover,” the Savior disclosed neither the house nor the man with whom he fulfilled the Passover."
],
256: [
    "By saying “so-and-so” he does not make a name clear specifically, but obliquely indicates one of the holy. For the word also fits every holy person, who first receives the Lord’s disciples — evangelists and apostles leveling his soul beforehand — and then Christ himself, who will come not as one called but of his own accord, dwelling with the Holy Spirit beside the one with whom he sees the holy baptism. For that is what “the man carrying the jar of water” makes clear, as Mark and Luke say."
],
257: [
    "We will not surely understand from this that none of the other disciples, but only Judas, dipped the morsel in the bowl with him. I think what was said has some such sense: he wants to say, as is likely, that the betrayer will be the one who dipped his hand with me in the bowl — that is, the fellow diner and table-mate, sharer and participant of table and of salt. For thus he also was accusing him through the voice of blessed David, saying, “But you, man of equal soul, who sweetened foods for me at the same table.” And again, “He who eats my bread has lifted up his heel against me.” John made this very point more clearly; for he said the Lord had said, “It is that one to whom I will give the morsel when I have dipped it.”"
],
258: [
    "Not as if some good or base thing somehow belonged to those not yet born, who are outside sensation (it is still utterly silly to think thus), but that for those about to fall into all misery, if they should be brought into being by God, non-existence is surely much and incomparably better."
],
259: [
    "The Lord gives thanks when he takes the cup — that is, in the form of prayer he converses with God the Father, declaring him as it were sharer and co-approver of the life-giving blessing that will be given to us, and at the same time giving us a pattern first to give thanks and thus to break the bread and distribute it. That is why we too, setting what was said before God’s face, beg intently that it be remolded for us into the spiritual blessing, so that by partaking of them we may be sanctified bodily and spiritually. He said demonstratively, “This is my body” and “This is my blood,” so that you may not think what appears is a mere type, but that through some ineffable energy of the God who can do all things what has been brought forward is truly changed into the body and blood of Christ — of which, when we partake, we take in Christ’s life-giving and sanctifying power. For it was necessary that he be mingled in us in a God-befitting way through the Holy Spirit, as it were with our bodies through his holy flesh and precious blood. And these we have also received as a life-giving blessing in bread and wine, so that we may not shrink when we see flesh and blood lying before us on the holy tables of the churches. For God, adjusting himself to our weaknesses, sends into what lies before us a power of life and transfers them toward the energy of his own life. And do not doubt that this is true when he says clearly, “This is my body” and “This is my blood”; rather receive the Savior’s word by faith, for being truth he does not lie."
],
260: [
    "After Judas went out, the Savior handed over to the eleven the saving mystery. For a little later Christ was about, having risen with his own flesh, to go up to the Father, so that we might have the presence of his body — for without Christ’s presence it is impossible for a human to be saved and freed from death and sin if the Life is not with us. So he gave us his own body and blood, so that through them the power of corruption might also be destroyed, and that it might dwell in our souls through the Holy Spirit, and we might become sharers of sanctification and be called heavenly and spiritual humans.",
    "Since after the resurrection Christ was about to be taken up to the Father with a body, for this reason he has given us his own body and blood, so that his flesh and blood, dwelling in us, may make us holy and sharers of immortality."
],
261: [
    "“Until I drink it new in the kingdom”: drinking wine does not fulfill need only, but also brings all-various pleasure to the sense. After the resurrection from the dead, when corruption has been shaken off from human bodies, the nature of things itself will also be transferred toward newness, so that our gladness itself may also be new. The mixture from wine is a symbol of temperance, which he also says will become new; and he does not at all say the drink itself will be new, but what results from it — that is, the gladness. For after the resurrection human nature will withdraw from its customary and earthly enjoyment, and will transfer toward a newness of delight that is clearly that of Christ our Savior of all, who sends his innate and own gladness into the souls of those who worship him and distributes it in proportion to each one’s measures. That we will be in intelligible gladnesses, divine David will assure us, saying, “How you multiplied your mercy, O God; and the sons of humans will hope in the shelter of your wings. They will be drunk from fatness, and you will give them the torrent of luxury to drink.” And wisdom again, “having mixed her own wine into a bowl” and set forth the breads, says, “Come, eat of my breads and drink wine which I have mixed for you.”"
],
262: [
    "The disciples were troubled not as light people, but because the matter was full of much perplexity and the knowledge of this mystery was hard to grasp — how the one who raised the dead and did countless signs beyond human measure was handed over to so dishonorable a death. This was the one who had said through the prophet, “I will strike the shepherd.” That is why David also says to the Father, “For the one whom you struck, they themselves pursued.” Yet this did not happen entirely and wholly by the Father’s will; he wanted him not to suffer, if the Jews had accepted him. But since they did not receive him, the Father consented to the Son who chose to suffer this. That is why it is also said that the Father struck “the shepherd,” since he allowed him to suffer though able to prevent his suffering. The word said to Pilate by Christ is also to be understood thus: “You would have no authority at all against me unless it had been given you from above” — instead of “the Father did not consent to me who chose to suffer.”"
],
263: [
    "He did not leave the disciples to remain only as far as the gloomy things; he foretells the resurrection, loosing their grief, and promises to go before them into Galilee, by which he signifies that he is about to depart from the Jews and transfer to the nations. He does not appear from heaven immediately — which is also why he appeared there."
],
264: [
    "He is grieved as a human, and the impassible one makes his own what belongs to the soul and what belongs to the body. Since what belongs to humanity is common to him, just as what befits divinity alone has somehow also become common to the flesh through the ineffable and inexpressible union, let what happened scandalize no one; for the Word’s coming together with flesh, having suffered what is its own, will confirm well in us the mystery of the incarnation."
],
265: [
    "By “cup” in these things he calls the stupefaction through death and the drunkenness that as it were puts one to sleep toward sleep. Declining to drink it — that is, not making suffering very much according to pleasure — accuses the impiety of those who crucified him. For they may not surely say, “Since he chose to suffer, we are rather helpers of the will”; for the declining will convict them of choosing to speak falsely."
],
266: [
    "He intensifies the prayer and weaves through the same words, setting what concerns himself beside us as outline and pattern. For I think we must not offer <a prayer> only once according to eagerness, but rather approach frequently and not blush at repeating the same until our requests depart to an end for us. For this reason Christ also made a third prayer about the same things, though he knew the will of God the Father very clearly; rather, through the third he was confirming that he had become human."
],
267: [
    "Perhaps Judas thought he could escape notice, holding forth a kiss as a type of love while having a heart full of unholy plans. So he approaches Christ as from drunkenness, expecting to declare the exceptional virtue an instrument of deceit and of love, and he was also adding, “Rejoice, Rabbi.” Do you say “rejoice” to the one ensnared toward death through you? Are you not even ashamed of the shape of the betrayal? But from here one could see that, having the liar in himself — that is, Satan — he was also lying when he said “rejoice.” And Christ accepted being kissed — and he became harsher than every beast of gentleness."
],
268: [
    "He said “twelve legions,” saying it instead of “you twelve disciples,” so that “I do not need your help; for I have not used the authority, but I give myself over to the Jews, since the scriptures foretold that this would be, that the Jews are about to do these things.”"
],
}

LEMMAS = {
253: [], 254: [], 255: [], 256: [],
257: [], 258: [], 259: [],
260: [{"form": "stray ‘28’", "lemma": "—", "gloss": "leading verse digit stripped", "lexica": "editorial"}],
261: [{"form": "stray ‘39’", "lemma": "—", "gloss": "mid-text digit stripped", "lexica": "editorial"}],
262: [], 263: [], 264: [], 265: [],
266: [{"form": "<προσευχὴν προσάγειν>", "lemma": "προσεύχομαι", "gloss": "supplied ‘to offer a prayer’", "lexica": "editorial"}],
267: [],
268: [{"form": "stray ‘40’", "lemma": "—", "gloss": "leading page/verse digit stripped", "lexica": "editorial"}],
}

CHOICES = {
253: [],
254: [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two witness forms in the extract."}],
255: [], 256: [],
257: [{"term": "ed.fr.286 skip", "english": "source jumps 285→287", "rejected": ["invent fr.286"], "why": "Edition fragment numbers skip; disclose, do not renumber."}],
258: [],
259: [],
260: [{"term": "parallel catena blocks", "english": "keep both wordings", "rejected": ["merge into one"], "why": "Two witness forms in the extract."}, {"term": "stray ‘28’", "english": "leading digit stripped", "rejected": ["keep as text"], "why": "Verse digit, not Greek."}, {"term": "locus 26:26-", "english": "keep incomplete locus as source", "rejected": ["invent end verse"], "why": "Source locus trails; invent nothing."}],
261: [{"term": "stray digits", "english": "digits stripped in clean Greek", "rejected": ["keep as text"], "why": "Page/verse digits, not Greek."}],
262: [], 263: [], 264: [], 265: [],
266: [{"term": "<προσευχὴν προσάγειν>", "english": "supplied ‘to offer a prayer’", "rejected": ["silent omit"], "why": "Angle brackets mark editor-supplied text; disclose."}],
267: [],
268: [{"term": "stray ‘40’", "english": "leading digit stripped", "rejected": ["keep as text"], "why": "Page/verse digit, not Greek."}],
}

ALLUSIONS = {
253: [{"reference": "Matthew 25:11-12", "reason": "Lord, lord, open; I do not know you.", "certainty": "clear"}],
254: [{"reference": "Matthew 25:14-30", "reason": "Parable of the talents.", "certainty": "clear"}, {"reference": "Hebrews 5:4", "reason": "No one takes the honor for himself.", "certainty": "clear"}],
255: [{"reference": "Matthew 26:18", "reason": "Go into the city to so-and-so; Passover.", "certainty": "clear"}, {"reference": "John 13:1", "reason": "Before the feast of the Passover.", "certainty": "clear"}],
256: [{"reference": "Matthew 26:18", "reason": "So-and-so; keep the Passover.", "certainty": "clear"}, {"reference": "Mark 14:13", "reason": "Man carrying a jar of water.", "certainty": "clear"}, {"reference": "Luke 22:10", "reason": "Man carrying a jar of water.", "certainty": "clear"}],
257: [{"reference": "Matthew 26:23", "reason": "He who dipped his hand in the bowl.", "certainty": "clear"}, {"reference": "Psalm 55:13", "reason": "Man of equal soul; sweet foods.", "certainty": "clear"}, {"reference": "Psalm 41:9", "reason": "Ate my bread; lifted heel.", "certainty": "clear"}, {"reference": "John 13:26", "reason": "The one to whom I give the dipped morsel.", "certainty": "clear"}],
258: [{"reference": "Matthew 26:24", "reason": "Better if that man had not been born.", "certainty": "clear"}],
259: [{"reference": "Matthew 26:26-28", "reason": "This is my body; this is my blood.", "certainty": "clear"}],
260: [{"reference": "Matthew 26:26-28", "reason": "Institution after Judas goes out.", "certainty": "clear"}],
261: [{"reference": "Matthew 26:29", "reason": "Drink it new in the Father’s kingdom.", "certainty": "clear"}, {"reference": "Psalm 36:7-8", "reason": "Shelter of wings; drunk from fatness.", "certainty": "clear"}, {"reference": "Proverbs 9:5", "reason": "Eat of my bread; drink wine I mixed.", "certainty": "clear"}],
262: [{"reference": "Matthew 26:31", "reason": "I will strike the shepherd.", "certainty": "clear"}, {"reference": "Zechariah 13:7", "reason": "Strike the shepherd.", "certainty": "clear"}, {"reference": "Psalm 69:26", "reason": "Whom you struck, they pursued.", "certainty": "clear"}, {"reference": "John 19:11", "reason": "No authority unless given from above.", "certainty": "clear"}],
263: [{"reference": "Matthew 26:32", "reason": "After I am raised I will go before you to Galilee.", "certainty": "clear"}],
264: [{"reference": "Matthew 26:37-38", "reason": "My soul is very sorrowful.", "certainty": "clear"}],
265: [{"reference": "Matthew 26:39", "reason": "Let this cup pass; yet your will.", "certainty": "clear"}],
266: [{"reference": "Matthew 26:42-44", "reason": "Prayed a third time, saying the same.", "certainty": "clear"}],
267: [{"reference": "Matthew 26:47-50", "reason": "Judas’s kiss; Friend, why are you here?", "certainty": "clear"}],
268: [{"reference": "Matthew 26:53", "reason": "Twelve legions of angels.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(253, 269):
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
        if n == 257:
            notes.append("Edition fragment numbers skip 286 after 285; disclose, do not renumber.")
        if n in (254, 260):
            notes.append("Parallel catena witness blocks both translated; not silently merged.")
        if n in (260, 261, 268):
            notes.append("Stray page/verse digits stripped in clean Greek.")
        if n == 260:
            notes.append("Source Matthew locus trails as 26:26-; invent no end verse.")
        if n == 266:
            notes.append("Supplied <προσευχὴν προσάγειν> disclosed.")
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a64a67.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a64a67.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a64",
                        "cyril-matt-frag-a65",
                        "cyril-matt-frag-a66",
                        "cyril-matt-frag-a67",
                    ],
                    "sections": "253-268",
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
