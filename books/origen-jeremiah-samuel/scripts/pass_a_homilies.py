# -*- coding: utf-8 -*-
"""Pass A: literal sense gloss + lemmas. Pass B is the reading English.

Glosses follow Klostermann GCS III. Where First1KGreek TEI drops a printed
word, the gloss follows the PDF (noted in lemmas/why).
"""

def L(form, lemma, gloss, lexica="LSJ"):
    return {"form": form, "lemma": lemma, "gloss": gloss, "lexica": lexica}


PASS_A = {
    "1.1": {
        "gloss": (
            "God is ready toward well-doing, but a delayer toward punishing those worthy of punishment. "
            "Able therefore to bring the punishment upon those condemned by him with silence, with not first-bearing-witness, "
            "he by no means does this; but even if he condemns, he speaks, the speaking being set before him for the turning-back "
            "from the sentence of the one about to be condemned. Of these there are many examples to take from the Scriptures; "
            "a few of the things presently falling-to-hand suffice, so that we may come also to the aim of the readings lying before us. "
            "For the Ninevites had become sinners and were condemned by God; still three days and Nineveh was about to be overthrown. "
            "God did not wish, being silent, to condemn it, but giving them a place of repentance and turning he sent a Hebrew prophet, "
            "so that when he said 'still three days and Nineveh shall be overturned,' the already-condemned might not be condemned, "
            "but having repented might obtain the mercy of God. Those in Sodom and Gomorrah were condemned, as is clear from the words "
            "of God toward Abraham; but nevertheless the angels did their own things, wanting those not wanting to be saved to be saved, "
            "saying to Lot: 'are there some to you here, sons-in-law or sons or daughters?' not being ignorant that those do not follow Lot, "
            "but doing the things of their own kindness and of the one who sent them."
        ),
        "lemmas": [
            L("μελλητής", "μελλητής", "delayer, one who postpones"),
            L("προδιαμαρτύρασθαι", "προδιαμαρτύρομαι", "to bear witness beforehand"),
            L("Ἑβραῖον προφήτην", "Ἑβραῖος", "a Hebrew prophet — printed in Klostermann; TEI omits Ἑβραῖον"),
            L("τόπον μετανοίας", "μετάνοια", "place/room for a change of mind"),
        ],
    },
    "1.2": {
        "gloss": (
            "You will find the like also upon the things according to Jeremiah. The time of his prophecy has been written, "
            "when he began and until when he prophesied. Then the one reading, if he does not attend to the reading and examine "
            "the purpose of the things set down, will say: a history is this, and it has been written when Jeremiah began to prophesy "
            "and after how much time he ceased. What is this history to me? I read, and I learned that he began to prophesy "
            "in the days of Josiah son of Amos king of Judah, in the thirteenth year of his reign. Then it came to pass in the days "
            "of Jehoiakim son of Josiah, and he prophesied until the eleventh year of Zedekiah son of Josiah king of Judah. "
            "And I learned that his prophecy was stretched through three kings, until the captivity of Jerusalem in the fifth month. "
            "What then are we taught through these, if we attend to the reading?"
        ),
        "lemmas": [
            L("ἱστορία", "ἱστορία", "narrative/history as mere chronicle"),
            L("σκοπός", "σκοπός", "aim, intent of the passage"),
        ],
    },
    "1.3": {
        "gloss": (
            "God condemned Jerusalem for sins, and they had been judged to be handed over to captivity. "
            "Nevertheless the mankind-loving God, the time having come, sends also this prophet — from before the third kingship, "
            "the one of the captivity — so that those willing, receiving, might repent through the prophetic words. "
            "He sent a prophet to prophesy under the second king after the first and under the third, up to the times of the captivity. "
            "For the long-suffering God was giving delay even, so to speak, one day before the captivity, calling the hearers to repent, "
            "so that the things of the captivity might cease. Therefore it is written that he prophesied until the captivity of Jerusalem, "
            "until the fifth month. He had begun and was still prophesying, as if saying: you have become captives — even so, repent. "
            "If you repent, the things of the captivity will not advance, but the mercy of God will stand over you. "
            "So we have something useful from the writing that gives the times of the prophecy: that God, according to his own love of mankind, "
            "calls the hearers not to suffer the things of the captivity. And it is thus also with us. If we sin, we too are about to become captives. "
            "For to hand over such a one to Satan differs in nothing from handing those from Jerusalem over to Nebuchadnezzar. "
            "As they were handed over to him because of sins, so we are handed over to Satan because of sins — Satan being a Nebuchadnezzar. "
            "And 'those I handed over to Satan, that they may be taught not to blaspheme,' the apostle says of other sinners."
        ),
        "lemmas": [
            L("φιλάνθρωπος", "φιλάνθρωπος", "loving mankind"),
            L("μακρόθυμος", "μακρόθυμος", "long-suffering"),
            L("προκόψει", "προκόπτω", "advance, go further (of the captivity)"),
        ],
    },
    "1.4": {
        "gloss": (
            "See then how great an evil it is to sin, so as to be handed over to Satan, who takes captive the souls of those left by God — "
            "God not leaving without cause and not without judgment those he has left. For when he sends the rain upon the vineyard, "
            "and the vineyard bears thorns instead of grapes, what will God do except command the clouds not to rain rain upon the vineyard? "
            "Because of our sins a captivity hangs over us too, and we are about to be handed over, if we do not repent, to Nebuchadnezzar "
            "and the Babylonians, so that the intelligible Babylonians may tear us. These hanging over us, the words of the prophets, "
            "of the Law, of the apostles, of our Lord and Savior Jesus Christ speak to us concerning repentance and call to turning. "
            "If we hear, let us believe the one who said, 'I also will repent of all the evils which I spoke of doing to them.' "
            "These things as a preface."
        ),
        "lemmas": [
            L("νοητοί", "νοητός", "intelligible; of the mind — Pass B: spiritual Babylonians"),
            L("μετανοήσω", "μετανοέω", "I will change my mind / repent (said of God)"),
        ],
    },
    "1.5": {
        "gloss": (
            "After the preface it is written that the word of the Lord came to him — clearly, to Jeremiah. "
            "And what does the word of the Lord say to him? A thing set-apart from the things said to the other prophets. "
            "For we have found this said toward none of the prophets. Abraham was called a prophet in the word 'he is a prophet and he will pray for you,' "
            "and God did not say to him 'before I formed you in the belly I know you, and before you came out of the womb I have sanctified you.' "
            "Abraham was sanctified later, when he went out from his land and from his kindred and from his father's house. "
            "Isaac has been born from promise, and we have not found even toward this one this word said. And why must I catalogue the rest? "
            "Jeremiah obtained an exceptional gift: 'before I formed you in the belly I know you, and before you came out of the womb I have sanctified you.'"
        ),
        "lemmas": [
            L("ἐξαιρέτου δωρεᾶς", "ἐξαίρετος", "exceptional / set-apart gift"),
            L("πλάσαι", "πλάσσω", "form, mould (not ποιέω make)"),
            L("ἡγίακα", "ἁγιάζω", "I have sanctified"),
            L("Ἰσαάκ", "Ἰσαάκ", "Isaac — printed in Klostermann; TEI dropped the name"),
        ],
    },
    "1.6": {
        "gloss": (
            "We are not ignorant that some refer these things, as greater than Jeremiah, upon the Savior and our Lord; "
            "and one must know that the many things agree with him and can be referred upon the Savior, which I will set beside; "
            "but a few of the things said toward Jeremiah squeeze the argument, not being able, as toward the many, to fit the Savior. "
            "What then are the things fitting the Savior? 'Toward all to whom I send you you shall go...' These would not yet clearly seem "
            "to be referred toward the Savior; but the things following squeeze the reading about Jeremiah. What nations did he uproot? "
            "What kingdoms did he overthrow? And what authority did Jeremiah have to destroy? And whom did Jeremiah build so as to be said 'and to build'? "
            "Jeremiah says 'I did not profit, and no one profited me.' How then is 'to build and to plant' given to him? "
            "These things, referred upon the Savior, do not squeeze the interpreter, because in them Jeremiah is a symbol of the Savior. "
            "But what I am about to set down squeezes even the most intelligent wanting to show how these too can fit the Savior: "
            "'I do not know how to speak.' He who is Wisdom, who is Power of God, who brought us the fullness of the deity which dwelt in him bodily — "
            "how then can 'I do not know how to speak' fit the Savior? And 'I am younger' is forbidden toward the Savior as saying it not well. "
            "To say these belong to Jeremiah and those to the Savior is not hard. But a fair-minded person will be much squeezed here, "
            "seeing that to cut, in a connected run of words, and to say 'these lesser fit Jeremiah and not Christ, these greater than Jeremiah fit Christ and not Jeremiah' "
            "is of those without judgment. Let the whole therefore be referred upon Jeremiah, and let even the things seeming greater than Jeremiah be interpreted."
        ),
        "lemmas": [
            L("θλίβει τὸν λόγον", "θλίβω", "squeezes/puts the argument in a tight place"),
            L("σύμβολον", "σύμβολον", "symbol, type"),
            L("ἀναγωγή", "ἀναγωγή", "leading-up; higher sense (used later in 1.12)"),
        ],
    },
    "1.7": {
        "gloss": (
            "Everyone who has taken words from God and has the grace of the heavenly words has taken them for the 'uprooting nations and kingdoms and pulling down.' "
            "But if it is said that everyone who has taken words from God uproots nations and kingdoms, do not think the nations and kingdoms for me bodily. "
            "Having observed human souls being ruled by sin according to the apostle's 'let not sin reign in our mortal body,' and seeing the many kinds of sins, "
            "tropologize also the nations and the kingdoms, the cheap things being in the souls of men, which are uprooted and pulled down by the words of God given either to Jeremiah or to anyone. "
            "And the first things, which squeeze as toward the Savior, can also fit Jeremiah, and the second things can fit Jeremiah for the one knowing how to tropologize. "
            "Someone of the hearers will say to me: exercise also the other argument and try to present all the things written as fitting the Savior. "
            "Do not be anxious about the second things; for it appears that the Savior uprooted the kingdoms of the devil and pulled down the nations, taking down the ethnic life. "
            "Here, according to the seeming ill-sounding as toward the Savior, exercise somehow the argument: how can the Savior say 'I do not know how to speak, because I am younger'? "
            "You see that the argument is in a narrow place. We know the Savior is Lord. We seek according to the worth of the Word and according to the truth to lead these up upon the Savior. "
            "Witnesses must be taken from the Scriptures; for our guesses without witness and our interpretations are untrustworthy. "
            "And 'every word shall be established at the mouth of two or three witnesses' fits interpretations more than men. "
            "How then can we refer these upon the Savior? Bring the Old Covenant as witness: 'before the child knows good or evil he refuses evil to choose the good.' "
            "And these are said outright about the Savior in Isaiah: 'behold the virgin shall conceive...' and there is added 'before the child knows.' "
            "And if one must take an example also from the gospel: Jesus, not having become a man but still being a child, since he emptied himself, was advancing "
            "(for no one already perfected advances, but he advances who still needs advance). Therefore he advanced in stature, advanced in wisdom, advanced in grace with God and men."
        ),
        "lemmas": [
            L("τροπολόγει", "τροπολογέω", "read tropologically; take as a figure — Pass B: as a figure"),
            L("ἐθνικὸν βίον", "ἐθνικός", "life of the nations / gentile way of life"),
            L("προέκοπτεν", "προκόπτω", "was advancing (threefold: stature, wisdom, grace)"),
            L("ἐκένωσεν ἑαυτόν", "κενόω", "he emptied himself"),
        ],
    },
    "1.8": {
        "gloss": (
            "But someone will say: even if you can lead up 'he does not know' upon the Savior, does it not cause you to stumble to say these things about the Only-begotten, "
            "about the firstborn of all creation, about the one announced before conception according to 'the Holy Spirit will come upon you'? And you say he does not know how to speak? "
            "See whether you can see something worth-saying and great about the Savior in the place: that not-knowing certain things, he is greater not-knowing than knowing them. "
            "And I use his own voice witnessing that he does not know certain things. He says to those saying 'did we not eat in your name...' 'depart from me; I never knew you.' "
            "Does the 'I never knew you' present his power as lesser, or greater and more wonderful, because he did not know the worse and those being destroyed? "
            "For he knew the things that differ, the better things, and 'the Lord knew those who are his,' and 'if anyone is ignorant, he is not known.' So the sinner is not known by God. "
            "Someone of the hearers will say: you have shown that he does not know the sinners; how will you show that it is a great and glorious thing for the Savior to say 'I do not know how to speak'? "
            "To speak is a human thing. To speak is to use a dialect — of Hebrews or of Greeks or of some others. If you go up to the Savior and see him as Word in the beginning with God, "
            "you will see that he does not know how to speak, because speaking is human; he does not know it, because the things he knows are greater than speaking. "
            "And if you compare tongues of angels with tongues of men, and see that he is greater even than angels, as the apostle witnessed in Hebrews, "
            "you will say he was greater even than the tongue of angels when he was God, the Word with the Father. "
            "So he learns and as-it-were takes up a knowledge not of great things but of lesser and smaller. And just as I, forcing myself, lisp when I converse with little children "
            "(for not knowing how to speak child-wise, being perfect/grown I force myself to converse with children), in the same way the Savior, being in the Father and in the greatness of the glory of God, "
            "does not speak human things, does not know how to utter to those below. But when he comes into a human body he says according to the beginnings: 'I do not know how to speak, because I am younger' — "
            "younger because of the bodily birth, older according to firstborn of all creation; younger because he came at the completion of the ages and later visited the life."
        ),
        "lemmas": [
            L("προσκόπτει", "προσκόπτω", "causes to stumble / gives offense"),
            L("ψελλίζειν", "ψελλίζω", "to lisp, speak as a small child"),
            L("παιδιστί", "παιδιστί", "in child-speech / baby-talk"),
            L("διαφέροντα", "διαφέρω", "things that differ / that matter"),
            L("συντελείᾳ τῶν αἰώνων", "συντέλεια", "completion of the ages"),
        ],
    },
    "1.9": {
        "gloss": (
            "'Do not say I am younger, because to all to whom I send you, you shall go.' So he stretches out the hand, touches his mouth, gives him words, "
            "and gives him words because of the kingdoms, that he may uproot. He had no need of uprooting words when he was in the Father; "
            "he had no words pulling-down and taking-apart the worse things. For nothing there was worthy of being pulled down, nothing worthy of being uprooted. "
            "It is a great thing, as 'I do not know you, because you are workers of lawlessness' is a great thing, said by the Savior because of the surpassing greatness of his glory — "
            "equal in force to 'I do not know how to speak human things,' this 'I do not know how to speak.'"
        ),
        "lemmas": [
            L("ἐκριζοῦν", "ἐκριζόω", "to uproot"),
            L("κατασκάπτειν", "κατασκάπτω", "to pull down, raze"),
        ],
    },
    "1.10": {
        "gloss": (
            "Whether toward Jeremiah or toward the Savior it is said 'before I formed you in the belly I know you,' having read Genesis and watched the things said about the creation of the world "
            "you will find that the Scripture very dialectically did not say that 'before I made you in the belly I know you.' "
            "For when the one according to the image was being created, 'God said, let us make man according to our image and likeness'; he did not say 'let us form.' "
            "But when he took dust from the earth, he did not make the man, but formed the man, and placed in the garden the man whom he formed, to work it and to keep it. "
            "If you can, see the difference of making and of forming: the Lord speaking, whether toward Jeremiah or toward the Savior, did not say 'before I made you in the belly I know you'; "
            "for the thing being-made does not come-to-be in a belly, but the thing being-formed from the dust of the earth, this is created in a belly. "
            "'Before I formed you in the belly I know you.' If the Lord knew all, he would not have said toward Jeremiah as something set-apart 'I know you.' "
            "So God knows those who differ, God knows those worthy of his knowledge, and 'the Lord knew those who are his.' Those unworthy God does not know, as the Savior also does not: 'I never knew you.' "
            "We, being men, as we advance, judge some things worthy of our knowing them; and some we do not even want to hear, so as not to know them; and some we want to know. "
            "What of the God of all? Does he want to know Pharaoh? Does he want to know the Egyptians? They are not worthy of the knowledge of God. Moses is worthy, and each of the prophets of that rank. "
            "You must set many things right before God begins to know you. Jeremiah he knew before forming him in the belly. Another he begins to know at thirty years, another at forty. "
            "There are secret words here — not in question as toward the Savior, but as toward Jeremiah needing attention from those having ears."
        ),
        "lemmas": [
            L("ποιήσωμεν", "ποιέω", "let us make (Gen 1:26)"),
            L("πλάσωμεν / ἔπλασε", "πλάσσω", "form/mould (Gen 2:7)"),
            L("διαλεκτικώτατα", "διαλεκτικός", "with a very fine distinction"),
            L("ἐπίσταμαί σε", "ἐπίσταμαι", "I know you (present, not 'knew')"),
        ],
    },
    "1.11": {
        "gloss": (
            "How does he say 'before I formed you in the belly I know you, and before you came out of the womb I have sanctified you'? "
            "God sanctifies some for himself. He did not wait for this one to come into birth in order to sanctify him; he had already sanctified him before he came out of the womb. "
            "If you refer it upon the Savior, it is not hard to say that he has been sanctified before coming out of the womb. "
            "If you refer it upon the Savior, he has been sanctified not only before coming out but still earlier. This Jeremiah was sanctified before coming out of the womb."
        ),
        "lemmas": [
            L("ἡγίακα σε", "ἁγιάζω", "I have sanctified you"),
        ],
    },
    "1.12": {
        "gloss": (
            "'I have set you as a prophet unto nations.' If you search this upon Jeremiah, watch in the things following that he is commanded to prophesy upon all the nations, "
            "and there is a heading 'what Jeremiah prophesied upon all the nations,' upon Elam, upon Damascus, upon Moab. "
            "And we have that he prophesied upon all the nations, as toward the letter of 'I have set you as a prophet unto nations' toward that one. "
            "If toward anagogy: if upon Jeremiah, we have already spoken; if upon the Savior, what need even to say? He truly prophesied upon all the nations. "
            "For he is, as he is ten-thousand other things, also a prophet. As he is high priest, as he is savior, as he is physician, so also prophet. "
            "Moses prophesying about him did not say only 'a prophet' but said it exceptionally: 'the Lord your God will raise up for you a prophet from your brothers, like me...' "
            "This one therefore is also the prophet set unto nations, and he received grace from God poured out on his lips, so that not only when he was present in the body, "
            "but also now, when he is present in power and in the spirit, he may prophesy upon all the nations, so as from all the nations to accomplish his prophecy and draw men unto salvation."
        ),
        "lemmas": [
            L("ἀναγωγήν", "ἀναγωγή", "leading-up; higher sense — Pass B: higher sense"),
            L("ἐξαιρέτως", "ἐξαιρέτως", "in a set-apart / special way"),
        ],
    },
    "1.13": {
        "gloss": (
            "'And I said, You who are, Master Lord, behold I do not know how to speak, because I am younger. And the Lord said to me, Do not say that I am younger...' "
            "We have often said that it is possible, according to the inner man, to be a child even if someone is in an old age of body. "
            "And it is possible at times, according to the outer man, to be a child, and according to the inner, a man. Such was Jeremiah, already having the grace from God "
            "while still in the age of a child according to the body. Therefore the Lord says to him 'do not say that I am younger.' "
            "And a sign that he is not younger but a complete man is this: 'to all to whom I send you, you shall go... Do not be afraid of their face.' "
            "The Word of God knows that those serving-as-ambassadors of the word are in danger among the hearers. For when they are exposed they hate them; when rebuked they persecute them. "
            "The prophets suffer every kind of thing. 'A prophet is not without honor except in his own country and in his house.' "
            "What Jeremiah suffered is written: he was thrown into a pit of mire; he remained there eating one loaf a day and drinking water only. "
            "'Which of the prophets did your fathers not persecute?' And it is necessary that those wanting to live in a godly way in Christ Jesus be persecuted in every case by opposing powers, through the vessels they find. "
            "Therefore those persecuted must not be surprised, but must do everything, only praying that they be persecuted unjustly and not justly."
        ),
        "lemmas": [
            L("ἔσω ἄνθρωπον", "ἄνθρωπος", "inner man"),
            L("τέλειος ἀνήρ", "τέλειος", "complete / grown man"),
            L("πρεσβεύοντες τὸν λόγον", "πρεσβεύω", "serving as ambassadors of the word"),
        ],
    },
    "1.14": {
        "gloss": (
            "Watch the difference of Jeremiah and of Isaiah. Isaiah says 'I have unclean lips...' and since he confessed that he did not have unclean works but only little-words "
            "(for to that point he was a sinner), the Lord did not stretch out his hand. One of the seraphim touched his lips and said 'behold I have taken away your iniquities.' "
            "But because this one was sanctified from the womb, tongs are not sent to him, nor coal from the altar (he had nothing worthy of the fire). The Lord's own hand touched him. "
            "Who is so blessed as to uproot, by the words given by God, the many kingdoms which the devil shows, kingdoms of opposing powers, kingdoms according to the sins? "
            "And as there are kingdoms, so there are nations. A kingdom cannot even be called a kingdom unless it has nations under it. "
            "For example: there is a kingdom of fornication, and the nations of fornication are each several fornication. There is one kingdom, the generic sin of greed and of robbery. "
            "It is the work of the words of God sent out over nations and kingdoms to uproot and to pull down. To uproot what? The Savior taught: 'every plant which my heavenly Father did not plant will be uprooted.' "
            "If we give place to the devil, the enemy sows a plant which the Father did not plant. If we give place to God, God rejoices and sows his seeds upon our governing part."
        ),
        "lemmas": [
            L("ῥημάτια", "ῥημάτιον", "little words / small utterances"),
            L("γενικὸν ἁμάρτημα", "γενικός", "generic / general sin"),
            L("ἡγεμονικόν", "ἡγεμονικόν", "governing part (Stoic) — Pass B: governing mind"),
        ],
    },
    "1.15": {
        "gloss": (
            "There is a building of the devil and a building of God. The building on the sand is the devil's, for it is supported on nothing firm and sure and united. "
            "The building on the rock is God's. 'You are God's field, God's building.' So the words of God are over nations and kingdoms to uproot and to pull down and to destroy. "
            "If something is uprooted and the uprooted is not destroyed, the uprooted still is. If something is pulled down and the stones of the demolition are not destroyed, the pulled-down still is. "
            "It is a work of the goodness of God, after the uprooting, to destroy the uprooted, and after the taking-down, to destroy the taken-down. "
            "The leprous house taken down becomes dust and is thrown outside the city, so that not even a stone remains. "
            "Something has been pulled down — let the stones not be useful for another building which the evil one can build. Something has been uprooted — let him not again find seeds so as to sow the tares once more."
        ),
        "lemmas": [
            L("οἰκοδομή", "οἰκοδομή", "building"),
            L("φαύλης ὕλης", "φαῦλος", "cheap/poor matter"),
        ],
    },
    "1.16": {
        "gloss": (
            "But the words of God do not stop at 'to uproot and to pull down and to destroy.' Suppose the cheap things have been uprooted from me, the worse pulled down — "
            "what benefit to me if in place of the uprooted the better things are not planted? That is why the words of God first of necessity do the uproot and pull down and destroy, and after that the build and plant. "
            "And we have always watched in Scripture that the things seeming grim — if I may call them so — are named first, then the things seeming cheerful second. "
            "'I will kill and I will make alive.' He did not say 'I will make alive' and after that 'I will kill.' For it is impossible that what God has made to live should be taken-away by him or by anyone else. "
            "But 'I will kill and I will make alive.' Whom will I kill? Paul the betrayer, Paul the persecutor. 'And I will make alive,' so that he may become Paul apostle of Jesus Christ. "
            "If the wretched ones from the heresies had understood these things, they would not keep putting them forward to us, saying 'do you see how fierce and inhuman the God of the Law is?' "
            "Do you not see in the Scriptures a promise of resurrection of the dead? Or do you not see the resurrection of the dead already making a beginning in each? "
            "'We were buried' with Christ through baptism and we were raised with him. First he strikes, and after that he heals. "
            "God cannot build upon the place of the cheap building. 'What partnership has righteousness with lawlessness?' Vice must be uprooted from the foundations. "
            "Words uproot nations; words pull down kingdoms — not these worldly ones. Is there not, in the things being said now, a power — if God gives it — uprooting unbelief, hypocrisy, vice, incontinence? "
            "Is there not a power pulling down, if somewhere an idol-shrine has been built in the heart, so that when that is pulled down a temple of God may be built, "
            "and there may be not a grove but a planting, a garden of God, where the temple of God is, in Christ Jesus, to whom is the glory and the power unto the ages of the ages. Amen."
        ),
        "lemmas": [
            L("προδότην", "προδότης", "betrayer, traitor — printed of Paul, then διώκτην persecutor"),
            L("ἀναιρεθῆναι", "ἀναιρέω", "to be taken away / destroyed (not merely 'killed')"),
            L("εἰδωλεῖον", "εἰδωλεῖον", "idol-shrine"),
            L("ἄλσος / παράδεισος", "παράδεισος", "grove vs garden of God"),
        ],
    },
    "2.1": {
        "gloss": (
            "'God did not make death, nor does he delight upon destruction of living ones. For he created all things unto being, and saving are the generations of the world, "
            "and there is not in them a drug of ruin, nor a kingdom of Hades upon earth.' Then, having gone a little beyond the wording, I will say from where death entered: "
            "'by envy of the devil death entered into the world.' If therefore anything is best about us, God has made it; but we created for ourselves the evil and the sins. "
            "Therefore here too the beginning of the reading in the prophet was speaking as-if questioningly toward those who have had bitterness in the soul, opposite to the sweetness which God constructed for it: "
            "'how have you been turned into bitterness, the alien vine?' As if he were saying: God did not make lameness, but he has made all sound-of-foot — what cause has come-to-be of those lamed? "
            "In the same way the soul has come-to-be according to the image not of the first only but of every man. For 'let us make man according to our image and according to our likeness' reaches upon all men. "
            "And as in Adam that which the many understand as according-to-the-image is older than what was taken-on when, because of sin, he wore the image of the dusty one, "
            "so in all the according-to-image of God is older than the worse image. We have worn, being sinners, the image of the dusty one; let us wear, repenting, the image of the heavenly one. "
            "Yet the creation came-to-be in the image of the heavenly one. So here he is at a loss toward those sinning: 'how have you been turned into bitterness, the alien vine? For I planted you a fruit-bearing vine, all true.'"
        ),
        "lemmas": [
            L("μελλητής", "μελλητής", "unused here"),
            L("φθόνῳ διαβόλου", "φθόνος", "envy of the devil"),
            L("ἀλλοτρία ἄμπελος", "ἀλλότριος", "alien / foreign vine"),
            L("χοϊκοῦ", "χοϊκός", "dusty, of earth"),
        ],
    },
    "2.2": {
        "gloss": (
            "After this let us look at 'if you wash yourself with nitre and multiply soap-plant for yourself, you are stained in your injustices before me, says the Lord.' "
            "Did some sinning soul suppose that, taking nitre and washing with sense-perceptible nitre, it ceases from the stain and ceases from the sin? "
            "Did someone assume that, taking this herb springing from the earth and washing and scouring, the soul is cleansed? "
            "But one must know that the Word has all power. And as he has the power of all Scripture, so the Word has the power of every medicine and is the power of everything that cleanses, and is most-scouring. "
            "'For the word of God is living and active and sharper than any two-edged sword.' So there is a word that is nitre, and there is a word that is soap-plant, which when spoken cleanses such filth. "
            "But since not every sin is healed from such a word as is nitre and from such a word as is soap-plant — there are sins not needing nitre or soap-plant — "
            "it is said to the one thinking she has sins of a kind able to fly-off in nitre and soap-plant: 'if you wash yourself with nitre... you are stained.' "
            "And as of wounds some are healed with a poultice, others with oil, others need a bandage, and there are other wounds of which it is said 'there is no poultice to put on, nor oil nor bandages' — "
            "so there are some sins which soil the soul, and for these the man needs a word that is nitre, a word that is soap-plant. And there are some sins not healed this way, for they are not even compared to soil. "
            "Therefore the Lord in Isaiah, knowing the differences of sins: 'the Lord will wash the soil of the sons and of the daughters of Zion, and he will cleanse the blood from their midst with a spirit of judgment and a spirit of burning.' "
            "Soil with a spirit of judgment; blood with a spirit of burning. If you have sinned, yet not unto death, you have been soiled. And most of us, if we have sinned the worse things, do not need nitre nor the multiplying of soap-plant, but the spirit of burning."
        ),
        "lemmas": [
            L("νίτρον", "νίτρον", "nitre, washing-soda"),
            L("πόαν", "πόα", "soap-plant / herb used as soap — Pass B: soap"),
            L("ῥύπον", "ῥύπος", "dirt, soil, filth"),
            L("πνεῦμα καύσεως", "καῦσις", "spirit of burning"),
        ],
    },
    "2.3": {
        "gloss": (
            "Therefore Jesus baptizes (perhaps I now find the meaning) in Holy Spirit and fire. Not that he baptizes the same person in Holy Spirit and fire, "
            "but the holy one in Holy Spirit, and the one who after believing, after being counted worthy of the Holy Spirit, has sinned again, he washes in fire — "
            "so that it is not the same person being baptized by Jesus in Holy Spirit and fire. Blessed therefore is the one baptized in Holy Spirit and not needing the baptism from fire. "
            "Thrice-wretched is that one who has need to be baptized with the fire. Yet Jesus has both. 'For a rod will come out of the root of Jesse, and a flower will go up from the root.' "
            "A rod upon those being punished; a flower upon the righteous. So God is a consuming fire, and God is light: consuming fire to sinners, light to the righteous and holy. "
            "And blessed is the one having a part in the first resurrection, who has kept the baptism of the Holy Spirit. Who is the one saved in another resurrection? "
            "The one needing the baptism from fire, when he comes upon that fire, and the fire tests him, and that fire finds wood, hay, and stubble, so as to burn them. "
            "Therefore, these things being said, gathering as we are able the words of the Scriptures, let us store them into the heart and try to live according to them, "
            "if perhaps we may be able to become clean before the departure, and having prepared our works for the departure, going out may be taken up in those good things and be saved in Christ Jesus, "
            "to whom is the glory and the power unto the ages of the ages. Amen."
        ),
        "lemmas": [
            L("τάχα", "τάχα", "perhaps — hedge kept"),
            L("τρισάθλιος", "τρισάθλιος", "thrice-wretched"),
            L("ῥάβδος / ἄνθος", "ῥάβδος", "rod (punishment) vs flower (the righteous)"),
            L("καλάμην", "καλάμη", "stubble — Klostermann with wood and hay"),
        ],
    },
}

# drop dummy lemma in 2.1
PASS_A["2.1"]["lemmas"] = [
    L("φθόνῳ διαβόλου", "φθόνος", "envy of the devil"),
    L("ἀλλοτρία ἄμπελος", "ἀλλότριος", "alien / foreign vine"),
    L("χοϊκοῦ", "χοϊκός", "dusty, of earth"),
    L("κατ' εἰκόνα", "εἰκών", "according to the image"),
]
