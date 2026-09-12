#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a16..a19 (entries 61–76)."""
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
    if n <= 64:
        return "cyril-matt-frag-a16"
    if n <= 68:
        return "cyril-matt-frag-a17"
    if n <= 72:
        return "cyril-matt-frag-a18"
    return "cyril-matt-frag-a19"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(61, 77)}

PASS_A = {
    61: (
        "From a metaphor this has been said of the in the camps trumpet; for those whenever "
        "they wish together to gather the army, sound the recall-signal, but the hypocrites do "
        "not wish to gather, but to be-theatrical to the many."
    ),
    62: (
        "Through this the Christ exhorts through brief the prayers to be-made, since he knows "
        "the mind being easily-carried-aside and through thoughts and cares empty being-led-"
        "astray, especially in the of prayer time. And he commands soberly and quickly to ask "
        "the God what he seeks not all whatever he wishes announcing; for this of extreme "
        "mind-harm is; for knows the God also before the us to ask of what we have-need. And "
        "battology is called the many-speaking from Battus some Greek long and many-lined hymns "
        "having-made unto the idols and tautology having. Battology is the outside of the good. "
        "The many-speaking call the ancients battology from someone thus being-named many-lined "
        "prayers having-made unto the idols and the same words saying through other and other "
        "expressions."
    ),
    63: (
        "Economically as human the Christ king is called although being by-nature God. Pray "
        "therefore the faithful to-be-present also to the unbelievers, in order that into the "
        "Christ having-believed own they may-call-upon, through whom they will-partake of the "
        "perfect goods now only having the earnest and the from part good; for not would be-"
        "active then the passions of the passionlessness being-present, gone the death, "
        "invisible the corruption, when in us the life will-reign and incorruption the power "
        "will-have. By-nature God the Christ being and by-nature human economically is-called "
        "king, that-is as human. Through this the righteous pray for themselves this to-be, "
        "still also for the unbelievers, in order that seeing and believing into him own of "
        "themselves they may-have king. Jesus is-able also as God to forgive sins, but as still "
        "imperfect to the disciples not-yet the about of the own divinity he handed-over word "
        "purely."
    ),
    64: (
        "It-is-necessary therefore not gloomy to appear nor having something of the love-of-"
        "glory charge, but as dirt being of the soul to wash-off."
    ),
    65: (
        "It-is-necessary the ruling-faculty — to the humans when-fasting."
    ),
    66: (
        "What someone has-set-before, this also he thinks and works most-readily and to set-"
        "right he strives; which of the heart is-found more-clearly from the intelligible onto "
        "the sensible leading-out the word and saying."
    ),
    67: (
        "Good master the un-money-loving manner, base but the loving of money. Wherefore to the "
        "one it-must-be-attached; for not possible to the two to please of different and "
        "opposite being habit."
    ),
    68: (
        "Since the soul and the body more-honorable are than the foods and the garments, also "
        "of the lesser it-must-be-despised, but it-must-be-cared also of the more-honorable, of "
        "soul I say and of body."
    ),
    69: (
        "The soul of the of the body essence more-honorable is as image of God and inbreathing, "
        "but the body instrument is of it and co-worker toward the finest. It-is-necessary "
        "therefore us of both to take-thought of the body together and of the soul and of the "
        "body unto so-much, as-far-as sufficient to it and not to be-hindered the soul; but to "
        "it it-must-be-given always the own and it-must-be-cared in-every-way and it-must-be-"
        "drawn-up through the virtues toward the cause of it the creative."
    ),
    70: (
        "To those the of the soul seeking gives the God also the to the bodies suitable, in "
        "order that not caring we about the such more than the necessary we will-be-hindered "
        "toward the finest."
    ),
    71: (
        "Those toward piety being-trained the from good thought bridle they put-upon the tongue "
        "those-things only to speak permitting, as-many-as do not harm. This teaching someone "
        "of us of the wise was-saying: child, 'if' on-the-one-hand 'there-is to you' word 'of "
        "understanding, answer; and if not, hand let-be upon mouth of you'. 'Death' for 'and "
        "life in hand of tongue', that-is in authority, 'and those mastering of it will-eat the "
        "fruits of it'. And since the of tongue to master not very easy is, from-above also this "
        "us the psalmist teaches saying: 'set, Lord, a guard to the mouth of me'. Let-us-not "
        "speak-against therefore of one-another nor let-us-condemn the brothers; for the on-the-"
        "one-hand by understanding being-steered not unto the of others sins looks, but to the "
        "own gazing evils good upon them drips tear, in order that he may-carry the forgiveness "
        "from God; for impossible humans being and thus weak not altogether to few to fall "
        "absurdities. And the not-at-all to fall only is-present by nature to the God. And us "
        "necessary those being in sins, not with the others' to delight evils, but to take-"
        "thought, how we ourselves of the base outside may-become."
    ),
    72: (
        "Cast-out first the beam from the eye of you, that-is yourself show clean of the great "
        "sins and then counselor you-will-be to the erring little. And if you do not cast-out "
        "the beam, but condemn the having the speck, reasonably you will-hear the apostolic: "
        "'the saying not to commit-adultery you commit-adultery', the saying 'not to steal, you "
        "steal'. Therefore for himself on-the-one-hand will-be teacher the wise, but another he "
        "will not condemn. For this also the law through Moses commands saying: 'attend to "
        "yourself'. 'To yourself' he says, not to another. And the 'attend' instead of the to "
        "look-aside the according to yourself. The indeed understanding thus himself will-train "
        "not unto the of others looking faults, but the own examining and about them repenting. "
        "And there are some who the on-the-one-hand of themselves do not see slips, but upon "
        "the of others stumbles laugh broad, who on-ground lying the standing mock, who from "
        "feet until head with mire having-been-smeared those little having dirt condemn; for "
        "they say sometimes about someone: so-and-so hard, inhuman, shameful-gaining, money-"
        "loving, raw, senseless, then these attaching to others they do not perceive the of "
        "themselves painting manner. And how-much damage has the to condemn others, through the "
        "despising the tax-collector Pharisee we have-learned. These therefore all having-"
        "removed through the good this legislation, he added again another command saying."
    ),
    73: (
        "Beginning of the virtue the to pray to be-made-known to someone the way of the truth; "
        "second step the to seek how it-is-necessary to journey the way; third the having-"
        "touched of the virtue to knock to the Christ, in order that he may-open to him the door "
        "and he may-be-freed of the narrow way and compressed and may-lead him into the spacious "
        "gnostic working, which all through the from God and toward God petition someone "
        "receives. And perhaps also the with practice to ask he hinted through the to say: "
        "knock. For knocks someone with the right hand. And of good practice symbol the right "
        "hand. And if not immediately you receive, not thus despair; for through this he said "
        "knock."
    ),
    74: (
        "And gifts good he calls the spiritual gifts, but Luke 'holy spirit' said instead of to "
        "say goods. And nothing the difference; for the 'holy spirit' itself is the by-nature "
        "good. Wherefore also to the partakers it gives goods. But to the very wicked through "
        "the unyieldingly to sin in a way nature to them the badness becomes, such-as is the "
        "satan and the demons; for someone is-able also these by-nature bad to say, although "
        "not by-nature bad having-been-created, but from self-chosen badness having-hardened."
    ),
    75: (
        "The word against those in beginning having-believed rightly and carefully having-"
        "worked the virtue so-as also signs to do and demons to cast-out and to prophesy, later "
        "but having-turned into baseness and from willing choice and wicked and eagerness; for "
        "if he says, that I did not know you never, in equal to those not-at-all having-been-"
        "known he places the in beginnings virtuously having-lived, but at end having-been-"
        "condemned. And to know says the God, whom he loves; and he loves those wholly into him "
        "believing and doing the pleasing to him."
    ),
    76: (
        "The hearer of law of the spiritually being-understood not indeed also doer to a house "
        "is-compared upon the sand having-been-built, which in time of trial falls and is-buried "
        "of the spirits of the wickedness having-blown, of the being-troubled waters until soul "
        "having-entered and of the muddy torrent of the lawlessness of them having-disturbed and "
        "the about the last having-shaken danger. And well upon on-the-one-hand the prudent I-"
        "will-liken him he said, but upon the foolish he will-be-likened; for the on-the-one-"
        "hand of the virtue worker altogether 'is-strong in the empowering' him Christ, from "
        "whom every to humans the being-set-right, from whom wisdom and understanding and toward "
        "the good likeness. But the base not God has of the of himself badness and folly cause, "
        "but himself is-likened to the senseless of the according to nature having-stood-away "
        "and in the against nature having-become."
    ),
}

PASS_B = {
    61: [
        (
            "This is said by a metaphor from the trumpet in the camps. When they want to gather "
            "the army together, they sound the recall. The hypocrites do not want to gather "
            "anyone; they want to put on a show for the crowd."
        ),
    ],
    62: [
        (
            "That is why Christ urges that prayers be made briefly. He knows the mind is easily "
            "pulled aside and led astray by empty thoughts and cares, especially at the time of "
            "prayer. He commands us to ask God soberly and quickly for what we seek — not by "
            "announcing everything we happen to want. That is extreme mind-harm. God knows what "
            "we need even before we ask."
        ),
        (
            "“Battology” means many words. It is named from a certain Greek, Battus, who made "
            "long, many-lined hymns to the idols, full of the same thing said over again. "
            "Battology is speech outside the good. The ancients call many-speaking battology "
            "from someone so named who made many-lined prayers to the idols and said the same "
            "words through one set of expressions after another."
        ),
    ],
    63: [
        (
            "Economically, as man, Christ is called king, though he is God by nature. So the "
            "faithful pray that this may hold also for unbelievers: that, believing in Christ, "
            "they may call him their own, and through him share the perfect goods — now having "
            "only the earnest and the partial good."
        ),
        (
            "Then the passions will not be at work when passionlessness is present; death will "
            "be gone and corruption unseen, when life reigns in us and incorruption holds the "
            "power. Christ is God by nature and man by nature, and is called king economically — "
            "that is, as man. That is why the righteous pray for this for themselves, and also "
            "for unbelievers: that seeing and believing in him they may have him as their own king."
        ),
        (
            "Jesus can also forgive sins as God, but while the disciples were still imperfect he "
            "had not yet handed over the word about his own divinity clearly."
        ),
    ],
    64: [
        (
            "So one must not look gloomy, nor carry any charge of love of glory, but wash off "
            "what is dirt of the soul."
        ),
    ],
    65: [
        ("When fasting before people, one must [guard] the ruling faculty."),
    ],
    66: [
        (
            "What a person has set before himself, that he also thinks and works at most readily, "
            "and strives to set it right. This is found more clearly of the heart when he leads "
            "the saying from intelligible things out to sensible ones."
        ),
    ],
    67: [
        (
            "The un-money-loving manner is a good master; the one who loves money is a base one. "
            "So one must cling to the one. It is not possible to please both, for they are "
            "different and opposite habits."
        ),
    ],
    68: [
        (
            "Since soul and body are more honorable than foods and garments, one must also "
            "despise the lesser things and care for the more honorable — I mean soul and body."
        ),
    ],
    69: [
        (
            "The soul is more honorable than the body’s essence, as God’s image and inbreathing. "
            "The body is its instrument and co-worker toward what is finest. So we must take "
            "thought for both body and soul together — for the body only so far as is enough for "
            "it and does not hinder the soul."
        ),
        (
            "To the soul one must always give what is its own, care for it in every way, and "
            "draw it up through the virtues toward its creative cause."
        ),
    ],
    70: [
        (
            "To those who seek the things of the soul God also gives what suits the bodies, so "
            "that we, not caring about such things more than we must, will not be hindered toward "
            "what is finest."
        ),
    ],
    71: [
        (
            "Those being trained toward piety put the bridle of good thought on the tongue, "
            "allowing it to speak only what does no harm. Teaching us this, one of the wise said: "
            "“Child, if you have a word of understanding, answer; if not, let a hand be on your "
            "mouth.” For “death and life are in the hand of the tongue” — that is, in its power — "
            "“and those who master it will eat its fruits.”"
        ),
        (
            "And since mastering the tongue is not very easy, the psalmist also teaches us from "
            "above: “Set a guard, Lord, on my mouth.” So let us not speak against one another or "
            "condemn the brothers. The one steered by understanding does not look at others’ "
            "sins, but gazing at his own evils drops a good tear over them, that he may receive "
            "forgiveness from God."
        ),
        (
            "It is impossible for humans, weak as we are, not to fall into a few absurdities at "
            "all. Not falling at all belongs by nature to God alone. We who are in sins must not "
            "delight in others’ evils, but take thought how we ourselves may get outside what is "
            "base."
        ),
    ],
    72: [
        (
            "“First cast the beam out of your eye” — that is, show yourself clean of the great "
            "sins, and then you will be a counselor to the one who errs a little. If you do not "
            "cast out the beam, yet condemn the one who has the speck, you will reasonably hear "
            "the apostolic word: “You who say not to commit adultery, commit adultery”; “you who "
            "say not to steal, steal.”"
        ),
        (
            "So the wise will be a teacher for himself and will not condemn another. The law "
            "through Moses also commands this: “Attend to yourself.” “To yourself,” he says, not "
            "to another. “Attend” means look carefully at what concerns you. The understanding "
            "person will thus train himself, not looking at others’ faults but examining his own "
            "and repenting over them."
        ),
        (
            "But some do not see their own slips, and laugh broadly at others’ stumbles — lying "
            "on the ground while mocking those who stand, smeared with mire from feet to head "
            "while condemning those who have little dirt. They sometimes say of someone, “So-and-"
            "so is hard, inhuman, greedy for shameful gain, money-loving, raw, senseless,” and "
            "while hanging these titles on others they do not notice they are painting their own "
            "manner. How much damage it is to condemn others we have learned through the Pharisee "
            "who despised the tax collector. Having removed all this through this good "
            "legislation, he added another command again."
        ),
    ],
    73: [
        (
            "The beginning of virtue is to pray that the way of truth be made known to someone. "
            "The second step is to seek how one must travel that way. The third is, having taken "
            "hold of virtue, to knock to Christ, that he may open the door, free him from the "
            "narrow and compressed way, and lead him into the spacious work of knowledge. All "
            "this one receives through petition from God and toward God."
        ),
        (
            "Perhaps he also hinted at asking with practice when he said “knock.” One knocks with "
            "the right hand, and the right hand is a symbol of good practice. And if you do not "
            "receive at once, do not despair even so — that is why he said “knock.”"
        ),
    ],
    74: [
        (
            "He calls “good gifts” the spiritual gifts. Luke said “Holy Spirit” instead of "
            "“goods,” and there is no difference: the Holy Spirit is what is good by nature. That "
            "is why he also gives goods to those who share in him."
        ),
        (
            "But for those who are very wicked, because they sin without yielding, badness becomes "
            "in a way a nature for them — as with Satan and the demons. One may even call these "
            "bad by nature, though they were not created bad by nature, but hardened from "
            "self-chosen badness."
        ),
    ],
    75: [
        (
            "The word is against those who at the beginning believed rightly and carefully worked "
            "virtue — so as even to do signs, cast out demons, and prophesy — but later turned to "
            "baseness by willing choice and wicked eagerness."
        ),
        (
            "When he says, “I never knew you,” he places the one who lived virtuously at the "
            "start but was condemned at the end on a level with those never known at all. God "
            "says he knows those he loves, and he loves those who believe in him wholly and do "
            "what is pleasing to him."
        ),
    ],
    76: [
        (
            "The hearer of the law understood spiritually, who is not also a doer, is compared to "
            "a house built on sand. In a time of trial it falls and is buried when the spirits of "
            "wickedness blow, when troubled waters enter as far as the soul, and when the muddy "
            "torrent of their lawlessness disturbs it and shakes the danger concerning the last "
            "things."
        ),
        (
            "He well said “I will liken him” of the prudent man, but “he will be likened” of the "
            "foolish. The worker of virtue is altogether “strong in the Christ who empowers him,” "
            "from whom comes every setting-right for humans, from whom come wisdom and "
            "understanding and likeness toward the good. The base person does not have God as "
            "cause of his badness and folly; he likens himself to the senseless, having stood "
            "away from what is according to nature and come to be in what is against nature."
        ),
    ],
}

LEMMAS = {
    61: [{"form": "σάλπιγγος", "lemma": "σάλπιγξ", "gloss": "trumpet", "lexica": "LSJ"}, {"form": "θεατρίζεσθαι", "lemma": "θεατρίζω", "gloss": "be made a spectacle", "lexica": "LSJ"}],
    62: [{"form": "βαττολογία", "lemma": "βαττολογία", "gloss": "battology / many words", "lexica": "Mt 6:7"}, {"form": "εὐπαράφορον", "lemma": "εὐπαράφορος", "gloss": "easily carried aside", "lexica": "LSJ"}],
    63: [{"form": "οἰκονομικῶς", "lemma": "οἰκονομικῶς", "gloss": "economically / in the economy", "lexica": "patristic"}, {"form": "ἀρραβῶνα", "lemma": "ἀρραβών", "gloss": "earnest / pledge", "lexica": "NT"}],
    64: [{"form": "φιλοδοξίας", "lemma": "φιλοδοξία", "gloss": "love of glory", "lexica": "LSJ"}],
    65: [{"form": "ἡγεμονικόν", "lemma": "ἡγεμονικόν", "gloss": "ruling faculty", "lexica": "Stoic/patristic"}],
    66: [{"form": "προέθετο", "lemma": "προτίθημι", "gloss": "set before oneself", "lexica": "LSJ"}],
    67: [{"form": "ἀφιλάργυρος", "lemma": "ἀφιλάργυρος", "gloss": "not money-loving", "lexica": "NT"}, {"form": "μαμωνᾷ", "lemma": "μαμωνᾶς", "gloss": "mammon (implied dual service)", "lexica": "Mt 6:24"}],
    68: [{"form": "τιμιώτερα", "lemma": "τίμιος", "gloss": "more honorable", "lexica": "LSJ"}],
    69: [{"form": "ἐμφύσημα", "lemma": "ἐμφύσημα", "gloss": "inbreathing", "lexica": "Gen 2:7 patristic"}, {"form": "δημιουργικήν", "lemma": "δημιουργικός", "gloss": "creative", "lexica": "patristic"}],
    70: [{"form": "ἐπιτήδεια", "lemma": "ἐπιτήδειος", "gloss": "what is suitable / needful", "lexica": "LSJ"}],
    71: [{"form": "χαλινόν", "lemma": "χαλινός", "gloss": "bridle", "lexica": "LSJ"}, {"form": "καταλαλῶμεν", "lemma": "καταλαλέω", "gloss": "speak against", "lexica": "NT"}],
    72: [{"form": "δοκόν / κάρφος", "lemma": "δοκός / κάρφος", "gloss": "beam / speck", "lexica": "Mt 7:3-5"}, {"form": "πρόσεχε σεαυτῷ", "lemma": "προσέχω", "gloss": "attend to yourself", "lexica": "Deut / pastoral"}],
    73: [{"form": "κρούετε", "lemma": "κρούω", "gloss": "knock", "lexica": "Mt 7:7"}, {"form": "γνωστικὴν ἐργασίαν", "lemma": "γνωστικός", "gloss": "work of knowledge", "lexica": "patristic"}],
    74: [{"form": "δόματα ἀγαθά", "lemma": "δόμα", "gloss": "good gifts", "lexica": "Mt 7:11"}, {"form": "αὐτοπροαιρέτου", "lemma": "αὐτοπροαίρετος", "gloss": "self-chosen", "lexica": "patristic"}],
    75: [{"form": "οὐκ ἔγνων ὑμᾶς", "lemma": "γινώσκω", "gloss": "I never knew you", "lexica": "Mt 7:23"}, {"form": "σημεῖα", "lemma": "σημεῖον", "gloss": "signs", "lexica": "Mt 7:22"}],
    76: [{"form": "ἐπὶ τῆς ψάμμου", "lemma": "ψάμμος", "gloss": "on the sand", "lexica": "Mt 7:26"}, {"form": "ἐνδυναμοῦντι", "lemma": "ἐνδυναμόω", "gloss": "empowering", "lexica": "Phil 4:13"}],
}

CHOICES = {
    61: [{"term": "θεατρίζεσθαι", "english": "put on a show / be theatrical", "rejected": ["act on stage only"], "why": "Hypocrites seek spectacle, not assembly."}],
    62: [{"term": "βαττολογία", "english": "battology", "rejected": ["babble only"], "why": "Keep the technical Gospel word + Battus etiology."}],
    63: [{"term": "οἰκονομικῶς", "english": "economically / in the economy", "rejected": ["practically"], "why": "Christ as king as man in the incarnation economy."}],
    64: [{"term": "φιλοδοξίας ἔγκλημα", "english": "charge of love of glory", "rejected": ["vanity charge"], "why": "Fasting face must not advertise glory."}],
    65: [{"term": "ἡγεμονικόν", "english": "ruling faculty", "rejected": ["willpower"], "why": "Inner ruling part while fasting before people."}],
    66: [{"term": "προέθετο", "english": "has set before himself", "rejected": ["intended vaguely"], "why": "Treasure/heart link via deliberate aim."}],
    67: [{"term": "ἀφιλάργυρος τρόπος", "english": "un-money-loving manner", "rejected": ["generous mood"], "why": "Two masters as two habits of life."}],
    68: [{"term": "τιμιώτερα", "english": "more honorable", "rejected": ["more valuable (market)"], "why": "Soul/body outrank food/clothing."}],
    69: [{"term": "ἐμφύσημα", "english": "inbreathing", "rejected": ["breath only"], "why": "Genesis-patristic soul dignity."}],
    70: [{"term": "τὰ τῆς ψυχῆς", "english": "the things of the soul", "rejected": ["spiritualities"], "why": "Seek first; bodily needs added."}],
    71: [{"term": "χαλινὸν τῇ γλώσσῃ", "english": "bridle on the tongue", "rejected": ["muzzle"], "why": "Piety trains speech; do not condemn brothers."}],
    72: [{"term": "δοκόν / κάρφος", "english": "beam / speck", "rejected": ["log / splinter only"], "why": "Standard Mt 7 pair; self first."}],
    73: [{"term": "κρούετε", "english": "knock", "rejected": ["rap casually"], "why": "Third step; right hand = practice."}],
    74: [{"term": "αὐτοπροαιρέτου κακίας", "english": "self-chosen badness", "rejected": ["free-will evil (jargon)"], "why": "Demons not created evil by nature."}],
    75: [{"term": "οὐκ ἔγνων ὑμᾶς οὐδέποτε", "english": "I never knew you", "rejected": ["I do not recognize you"], "why": "Gospel lemma; end-state cancels early signs."}],
    76: [{"term": "ἐπὶ τῆς ψάμμου", "english": "on the sand", "rejected": ["on gravel"], "why": "Hearer-not-doer house."}],
}

ALLUSIONS = {
    61: [{"reference": "Matthew 6:2", "reason": "Trumpet almsgiving / hypocrites.", "certainty": "clear"}],
    62: [{"reference": "Matthew 6:7-8", "reason": "Battology; Father knows needs.", "certainty": "clear"}],
    63: [
        {"reference": "Matthew 6:10", "reason": "Your kingdom come.", "certainty": "clear"},
        {"reference": "Matthew 6:14", "reason": "Forgive / forgiven (appended note).", "certainty": "possible"},
    ],
    64: [{"reference": "Matthew 6:16", "reason": "Fasting not gloomy for show.", "certainty": "clear"}],
    65: [{"reference": "Matthew 6:16-17", "reason": "Anoint head when fasting.", "certainty": "clear"}],
    66: [{"reference": "Matthew 6:21", "reason": "Where treasure is, heart is.", "certainty": "clear"}],
    67: [{"reference": "Matthew 6:24", "reason": "Cannot serve God and mammon.", "certainty": "clear"}],
    68: [{"reference": "Matthew 6:25", "reason": "Do not worry about food/clothing.", "certainty": "clear"}],
    69: [{"reference": "Matthew 6:25", "reason": "Soul/body more than food/clothing.", "certainty": "clear"}],
    70: [{"reference": "Matthew 6:33", "reason": "Seek first the kingdom.", "certainty": "clear"}],
    71: [
        {"reference": "Matthew 7:1-2", "reason": "Judge not; measure.", "certainty": "clear"},
        {"reference": "Sirach 5:12", "reason": "If you have understanding, answer.", "certainty": "possible"},
        {"reference": "Proverbs 18:21", "reason": "Death and life in tongue’s power.", "certainty": "possible"},
        {"reference": "Psalm 141:3", "reason": "Set a guard on my mouth.", "certainty": "clear"},
    ],
    72: [
        {"reference": "Matthew 7:3-5", "reason": "Beam and speck.", "certainty": "clear"},
        {"reference": "Romans 2:21-22", "reason": "You who say not to steal/adultery.", "certainty": "clear"},
        {"reference": "Luke 18:9-14", "reason": "Pharisee and tax collector.", "certainty": "clear"},
    ],
    73: [{"reference": "Matthew 7:7", "reason": "Ask, seek, knock.", "certainty": "clear"}],
    74: [
        {"reference": "Matthew 7:11", "reason": "Good gifts to children.", "certainty": "clear"},
        {"reference": "Luke 11:13", "reason": "Holy Spirit instead of good gifts.", "certainty": "clear"},
    ],
    75: [{"reference": "Matthew 7:22-23", "reason": "Lord, Lord; I never knew you.", "certainty": "clear"}],
    76: [
        {"reference": "Matthew 7:24-27", "reason": "House on rock / sand.", "certainty": "clear"},
        {"reference": "Philippians 4:13", "reason": "Strong in the one who empowers.", "certainty": "clear"},
    ],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(61, 77):
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a16a19.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a16a19.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a16",
                        "cyril-matt-frag-a17",
                        "cyril-matt-frag-a18",
                        "cyril-matt-frag-a19",
                    ],
                    "sections": "61-76",
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
