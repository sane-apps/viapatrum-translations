# -*- coding: utf-8 -*-
"""English of De adoratione Book 2, sections 1–8 (PG 68.212–225). From locked Greek."""

SECTIONS = []


def S(section, title, english, allusions, notes=None):
    SECTIONS.append(
        {
            "section": section,
            "title": title,
            "english": english,
            "notes_covered": [],
            "added_allusions": allusions,
            "translator_notes": notes or [],
        }
    )


def A(reference, reason, certainty="clear"):
    return {"reference": reference, "reason": reason, "certainty": certainty}


S(
    1,
    "Justification is not in the Law but in Christ",
    [
        "Book 2. That it is impossible to escape the death that comes from sin, and the devil's greed, except through the sanctification that is according to Christ; and that justification is not in the Law but in Christ.",
        "Cyril said: So then, Palladius, a not ignoble argument has shown us that it is a thing to love to keep clear of what is naturally hurtful, and that we must desire the slavery under God, as both honorable and profitable.",
        "Palladius said: Indeed it has.",
        "Cyril: And we were quite sure that, leaving the more shameful things entirely, we ought to seek the better.",
        "Palladius: Very much so.",
        "Cyril: And so it seemed we must, putting as far away as we can the love of pleasure in this world's life and the bustle that goes with it, be eager to sacrifice to God, and — as if we had come into a desert by a disposition of mind — practice for him a worship that is unhurried and most clean, not to be entered by defilements, beautiful and acceptable.",
        "Palladius: It did seem so.",
        "Cyril: And that, when Satan from greed was shutting us up under himself and wanting to hold us, a divine law was calling us into a free dignity, setting the teaching about the best things against his abominations, and tutoring us toward the better — was this not made white-clear from ten thousand examples?",
        "Palladius: True.",
        "Cyril: God, then, is the giver of salvation, and the steward of all our well-being, showing the road of kinship with himself, Christ mediating. Or would not Moses' mediation be a type, and a very clear one, of the mediation through Christ?",
    ],
    [
        A("Galatians 3:19-20", "Mediator; Law and promise.", "possible"),
        A("1 Timothy 2:5", "One mediator between God and men, the man Christ Jesus.", "possible"),
        A("Hebrews 8:6", "A better covenant, a better mediation.", "possible"),
    ],
    ["θάνα τον: split θάνατον at the heading."],
)

S(
    2,
    "Moses led from brick-making; Christ from the intelligible slavery",
    [
        "Palladius said: In what way?",
        "Cyril: Divine Moses was bringing Israel out of a bodily slavery and taking them off the labors of brick-making and the works around the earth, and, lying as it were in the middle between God and men, he was carrying down to them the words from above. But our Lord Jesus Christ, recarving into truth the things that were in type and shadows, draws us out of the intelligible slavery, putting out the sin that long tyrannized over us, shaking down the devil's power, and persuading those who think they must follow him to leave an earthly mind and the eager business about the flesh, reshaping them as it were into a desire for virtue, and announcing to us most clearly the will of God and Father. That is why he also said, 'The words that I speak are not mine, but of the one who sent me.' And again, 'I do not speak from myself, but the Father who sent me has himself given me a commandment, what I should say and what I should speak.'",
        "And Moses made his own affairs an image and stamp of the mediation in Christ, saying to those from Israel, 'The Lord your God will raise up for you a prophet from your brothers, like me. You shall hear him, according to all that you asked from the Lord your God at Horeb, on the day of the assembly.' So the things through Moses, and the force of the mediation according to him, are in type and image. The manner of the mediation in Christ is more unspeakable. For Moses was a servant of law and shadow, and a carrier of the tutoring from above. Christ, as master of law and prophets, lays down what seems good to him, and he was mediator, deity and humanity running together in him and coming as it were into one. For Christ is understood as both at once. 'And Moses was faithful in all his house as a servant; but Christ as a son over his house, whose house we are' — we who have been led through faith in him into the true freedom.",
        "It is settled, then, that the hierophant Moses was mediator of a bodily freedom, of letter and shadow; but our Lord Jesus Christ is the one who brings in the things above the Law, and who gives the incomparably better freedom, that is, the one according to the Spirit. That is why he also said, even to those from Israel who had been freed in a bodily way, 'If you remain in my word, you are truly my disciples, and you will know the truth, and the truth will free you.' And again, 'Everyone who does sin is a slave of sin. The slave does not remain in the house forever; the son remains forever. If then the Son frees you, you are free indeed.'",
        "Palladius: You have spoken very well.",
        "Cyril: We will boast, then, not in the bright things according to the flesh, but in those in the Spirit and in the righteousness",
    ],
    [
        A("John 14:24", "Quoted: the words I speak are not mine, but of the one who sent me."),
        A("John 12:49", "Quoted: I do not speak from myself; the Father has given me a commandment what to say."),
        A("Deuteronomy 18:15-16", "Quoted: a prophet from your brothers, like me; you asked this at Horeb."),
        A("Hebrews 3:5-6", "Quoted: Moses faithful as a servant; Christ as a son over his house."),
        A("John 8:31-32", "Quoted: if you remain in my word; the truth will free you."),
        A("John 8:34-36", "Quoted: slave of sin; the son remains forever; if the Son frees you."),
        A("Exodus 1:14", "Brick-making in Egypt.", "possible"),
    ],
)

S(
    3,
    "The Law shows sin; it does not perfect",
    [
        "Palladius went on with Cyril: '...that is according to Christ, not that according to the Law.' For if what is under sin is still a slave, and the Law justifies least of all — it condemns rather, and writes down those who transgress — how would it not be clear to everyone that all justification is in Christ, and the perfecting in the Spirit through sanctification, through him and in him? And so the all-wise Paul writes, 'For I am not ashamed of the gospel, for it is the power of God for salvation to everyone who believes, to the Jew first and to the Greek. For in it the righteousness of God is revealed from faith to faith, as it is written, The righteous shall live from faith.' And he writes down the uselessness and weakness of the old Law in this, saying, 'That no one is justified in the Law before God is clear, because the righteous shall live from faith. And the Law is not from faith, but the one who has done them shall live in them.' So in Christ we are justified through faith, and we have been redeemed from the intelligible slavery.",
        "Palladius: Is the Law useless, then?",
        "Cyril: I do not say that. For it was not oracled in vain. It was given rather 'for help,' according to what is written. As far as tutoring goes, and knowing what is a fault, and needing to take first principles and elements of the oracles of God, how would it not be thought useful? But it is slower toward the washing-off of sin, and toward being able to perfect into sanctification. And so divine Paul said to us, 'We know that whatever the Law says, it speaks to those in the Law, so that every mouth may be stopped and all the world may become accountable to God, because from works of Law no flesh will be justified before him; for through Law is knowledge of sins.' So the Law is a shower of sin, not a bringer of boasts toward virtue. For to say, You shall not fornicate, you shall not commit adultery, you shall not steal, you shall not swear falsely, and whatever is fitted to such things, belonged to one marking the kinds of worthlessness and putting people out of uncleanness — not bringing in a knowledge of virtue, nor making the knowledge of the unadulterated life most clear to the hearers. That one must not do the more shameful things is, I think, a dull thing to enroll among the ways of the exceptional life. I think we must, and very reasonably, only then barely bind on ourselves the vote for all the things that are praised, if, having let go of the evil and pushed it away and left it to stay down somewhere — the thing not yet rid of the reputation of worthlessness and profane abomination — we leap up onto the very boasts of virtue. And so our Lord Jesus Christ says, 'Amen, amen I say to you, unless your righteousness exceeds that of the scribes and Pharisees, you will by no means enter the kingdom of the heavens.' You understand, then, that the Savior has commanded us to choose the righteousness beyond that according to the Law. And knowing the thing to be best, the wise Paul writes, 'If anyone else thinks to have confidence in the flesh, I more. Circumcised the eighth day, of the race of Israel, of the tribe of Benjamin,'",
    ],
    [
        A("Romans 1:16-17", "Quoted: I am not ashamed of the gospel; the righteous shall live from faith."),
        A("Habakkuk 2:4", "The righteous shall live from faith, under the Romans citation."),
        A("Galatians 3:11-12", "Quoted: no one is justified in the Law; the one who has done them shall live in them."),
        A("Leviticus 18:5", "The one who has done them shall live in them.", "possible"),
        A("Isaiah 8:20", "For help — εἰς βοήθειαν.", "possible"),
        A("Romans 3:19-20", "Quoted: every mouth stopped; from works of Law no flesh justified; knowledge of sins."),
        A("Exodus 20:14-16", "You shall not commit adultery, steal; false witness.", "possible"),
        A("Matthew 5:20", "Quoted: unless your righteousness exceeds that of the scribes and Pharisees."),
        A("Philippians 3:4-5", "Quoted: confidence in the flesh; eighth-day circumcision; tribe of Benjamin."),
    ],
)

S(
    4,
    "Abraham was justified by faith before circumcision",
    [
        "'a Hebrew from Hebrews, according to the Law a Pharisee, according to zeal persecuting the Church, according to righteousness in the Law becoming blameless. Whatever was gain to me, these I have counted loss because of Christ. Indeed I count all things loss because of the surpassing knowledge of Jesus Christ our Lord, for whom I suffered the loss of all things, and count them rubbish, that I may gain Christ and be found in him, not having my own righteousness, the one from the Law, but the one through faith in Christ.'",
        "Palladius: I understand; the argument is clear. But tell me this. Why was the righteousness through faith, and the sanctification according to it, not decreed for us at the beginning, if the old Law is not enough for perfecting?",
        "Cyril: Because, my friend, I would say, what is dirty is reasonably washed, what is defiled is wiped, and what is darkened is made bright. And it would be fitting, I think, according to the Savior's voice, that the sick be healed, and that not the sanctified but those loaded with sins be called to a change of mind. For must not those who are called to forgiveness first be found guilty, and be seen as redeemed after having been in danger from the weakness in them? So the Law that shows sin had to appear first, as a kind of proof and an exact accuser of everyone's weakness, so that the greatness of the divine gentleness through Christ might not be unknown to us. For where, or how, is the grace of forgiveness, if the charges do not lie underneath?",
        "And if, speaking briefly, we must also leap to certain ancient narratives, I will say again that God was promising to Abraham the grace through faith, and, as in a firstfruits of those shown mercy, he was making in him the forgiveness from gentleness older than the Law. For it is written that 'Abraham believed God, and it was counted to him for righteousness.' And Paul adds his witness, saying, 'How then was it counted? In circumcision or in uncircumcision? Not in circumcision, he says, but in uncircumcision; and he received a sign, circumcision, a seal of the righteousness of the faith which was in uncircumcision.' And he heard God saying plainly that 'in you all the nations shall be blessed.' And the 'in you' would mean, according to your likeness. So Paul, understanding it this way, says, 'The Scripture, foreseeing that God justifies the nations from faith, preached the gospel beforehand to Abraham, that in you all the nations shall be blessed. So those from faith are blessed with faithful Abraham.' Circumcision, then, is a sign of the faith in uncircumcision, and he has been justified not from works of Law, and the boasts through faith appear older than the circumcision in the flesh. For he was called friend of God.",
    ],
    [
        A("Philippians 3:5-9", "Quoted: Hebrew of Hebrews; Pharisee; gains as loss; righteousness through faith."),
        A("Matthew 9:12-13", "The sick need a physician; sinners called, not the righteous.", "possible"),
        A("Luke 5:31-32", "Same call of the loaded with sin.", "possible"),
        A("Genesis 15:6", "Quoted: Abraham believed God, and it was counted for righteousness."),
        A("Romans 4:10-11", "Quoted: counted in uncircumcision; circumcision a seal of the faith."),
        A("Genesis 12:3", "Quoted: in you all the nations shall be blessed."),
        A("Galatians 3:8-9", "Quoted: Scripture preached the gospel beforehand to Abraham."),
        A("James 2:23", "Abraham was called friend of God.", "possible"),
        A("Isaiah 41:8", "Abraham my friend.", "possible"),
    ],
)

S(
    5,
    "The Law was put in until the seed should come",
    [
        "Palladius said: I would reasonably ask, then, what the delay of the sanctification according to faith was — why you say the sign is in the older place and the thing that surpasses it in the second.",
        "Cyril: Did we not just say that it was the work of an admirable and unspeakable skill, that the Law which condemns should leap up in time before the faith that justifies? Or does not the light shine in the darkness? And is not power perfected in weakness, according to what is written?",
        "Palladius: You speak well.",
        "Cyril: So the Law came in besides, so that the trespass might increase. For where there is no Law, there is no transgression either. And how would anyone see the forgiveness of transgression and of the ease toward it, if the Law had not first condemned us? That what I say is true, and that the argument on this is not some faded or ugly thing, Paul will help, saying, 'So the Law was added for the sake of transgressions, until the seed should come to whom it has been promised, ordained through angels.' And being very wise, he tries to cut off in advance the inventions and questions that will sometimes be found by some. For it was likely that some would blame the delay of the righteousness in faith, and say that the coming-in of the Law in between became a setting-aside of that ancient promise. That is why he says, 'Is the Law then against the promises of God? Let it not be. For if a Law had been given that was able to make alive, righteousness would truly have been in Law. But Scripture shut up all things under sin, so that the promise from faith in Jesus Christ might be given to those who believe. Before the faith came, we were guarded under Law, being shut up into the faith about to be revealed to us. So the Law became our tutor unto Christ, so that we might be justified from faith. But when the faith has come we are no longer under a tutor, for you are all sons of God through the faith in Christ Jesus.'",
        "And he makes the question white-clear, as it were, by adding, 'This I say: a covenant previously ratified by God, the Law that came after four hundred and thirty years does not annul, so as to make the promise void. For if the inheritance is from Law, it is no longer from promise. But God has granted it to Abraham through a promise.' So the Law, having shut us up into sin, tutored us unto Christ, for the end of Law and prophets is Christ. That is why he also said to the peoples of the Jews who had not believed him, 'If you believed Moses, you would believe me. For he wrote about me.' We are justified, then, not from works of Law, but rather by the faith in Christ. 'For as many as are from works of Law are under a curse. For it is written, Cursed is everyone who does not remain in all the things written in the book of the Law, to do them. But from the curse of the Law Christ bought all, having become'",
    ],
    [
        A("John 1:5", "The light shines in the darkness."),
        A("2 Corinthians 12:9", "Power perfected in weakness."),
        A("Romans 5:20", "The Law came in besides so that the trespass might increase."),
        A("Romans 4:15", "Where there is no Law, no transgression."),
        A("Galatians 3:19", "Quoted: the Law was added for transgressions until the seed should come."),
        A("Galatians 3:21-26", "Quoted: not against the promises; shut up under sin; tutor unto Christ; sons of God through faith."),
        A("Galatians 3:17-18", "Quoted: the Law after 430 years does not annul the promise."),
        A("Romans 10:4", "Christ is the end of the Law.", "possible"),
        A("John 5:46", "Quoted: if you believed Moses you would believe me; he wrote about me."),
        A("Galatians 3:10", "Quoted: as many as are from works of Law are under a curse."),
        A("Deuteronomy 27:26", "Cursed is everyone who does not remain in all things written."),
        A("Galatians 3:13", "Christ became a curse for us — continued in the next column."),
    ],
)

S(
    6,
    "A curse on the tree; honor God from righteous labors",
    [
        "'a curse for us. For it is written, Cursed is everyone who hangs on a tree, so that the blessing of Abraham might come to the nations in Christ Jesus, so that we might receive the promise of the Spirit through the faith.'",
        "Palladius: But, my good man, if it seems good, I would rather we go on to something else learned from Christ. This is enough about the Law and the economy according to it.",
        "Cyril: Say then whatever is dear to you; and for me too it is not among the things too hard to reach.",
        "Palladius: The question is not very steep, or trackless. What is sought could be caught, I think, even without much labor, if Christ puts the divine light into us. Will we not, then, honor God with the bloodless offerings — we who have received the justification in faith and push out the worship in shadows and types?",
        "Cyril: You speak well. For it is written, 'Honor the Lord from your righteous labors, and offer him firstfruits from your fruits of righteousness.' 'For with such sacrifices God is well pleased,' according to the voices of the saints.",
        "Palladius: So it is idle, then, to be eager to sacrifice cattle and to fulfill the things brought in for us through the ancient commandment. For sheep-slaughters and frankincense, and besides these cakes, and oil-soaked fine flour, turtledoves and pigeons, were in that time the dedicated things of those who worshiped. But tell me why he did not from the beginning make these things dismissed, and is now seen laying down as law the things he delights in, and uncovering for us the ways of the spiritual sacrifice.",
        "Cyril: Do you think, then, and dare to say, that the divine did not plan rightly at the beginning, and, as if it had missed the perfectly good, was only barely able to find the greater? Or that it chose then the things in shadows as adequately having what seemed good to it, and then suffered some love of novelty in our case, giving the preference to others, and making new for us a worship not long since decided?",
        "Palladius: No indeed. That, I think, is nonsense. I would not even suppose that being able to miss in anything at all would follow him. I would learn with the greatest pleasure what it was that persuaded him to lay down as law, for those on the earth, those things then, and these things now.",
        "Cyril: Your argument forces us to go back, as it were. Or did I not say that the Law was a tutor — that is, the trainer of those still infants? And to those not yet able to understand what the truly good is? And what the will of God would be, the perfect and well-pleasing, hinting it through a riddle? And as in",
    ],
    [
        A("Galatians 3:13-14", "Quoted: a curse for us; cursed is everyone who hangs on a tree; blessing of Abraham to the nations."),
        A("Deuteronomy 21:23", "Cursed is everyone who hangs on a tree."),
        A("Proverbs 3:9", "Quoted: honor the Lord from your righteous labors."),
        A("Hebrews 13:16", "Quoted: with such sacrifices God is well pleased."),
        A("Leviticus 2:1", "Fine flour and oil as offering.", "possible"),
        A("Leviticus 1:14", "Turtledoves and pigeons.", "possible"),
        A("Galatians 3:24", "The Law a tutor.", "possible"),
        A("Romans 12:2", "The perfect and well-pleasing will of God.", "possible"),
    ],
)

S(
    7,
    "I hate your feasts; do justice and love mercy",
    [
        "thick types still marking it. You will know, you will know, and not with long sweat, the manner of the spiritual worship — how it was always, and from the beginning, thrice-desired by God, but still hard to enter and untouchable for the souls of the Jews. That is why they needed an infant-fitting word, and simple lessons, and an economic child-nursing that had nothing steep or rough. For God legislated even of old the things in types. And he showed beforehand again the things from the true worship as coming and about to be present in their times. And he made the approach through blood, and the shadow, a thing to be thrown away. He shook it off through the prophet, saying in Amos, 'I have hated, I have rejected your feasts, and I will not smell in your assemblies. Because if you bring me whole burnt offerings and your sacrifices, I will not look. Take away from me the noise of your songs, and I will not hear the psalm of your instruments.'",
        "And through Micah he has brought in the person of a man, wanting to learn how he might accomplish the good without blame: 'With what shall I take hold of the Lord, shall I lay hold of God most high? Shall I take hold of him with whole burnt offerings, with yearling calves? Will the Lord receive thousands of rams, or ten thousands of fat goats? Shall I give my firstborn, fruit of my belly for ungodliness, for the sin of my soul?' Then, joined and in order: 'Has it been told you, O man, what is good, or what the Lord seeks from you, but to do judgment and to love mercy, and to be ready to walk with the Lord your God?' Is this not clearly what Christ said: 'If anyone wants to come after me, let him deny himself, and take up his cross, and follow me'? And again, 'Let the one who loves me follow me, and where I am, there let my servant also be.' Not in the legal worship, the one according to Christ, but in a holy and spiritual one.",
        "Palladius: You have spoken most rightly.",
        "Cyril: And through Isaiah's voice he rebukes those from Israel more hotly, saying, 'Hear the words of the Lord, rulers of Sodom; attend to the Law of God, people of Gomorrah. What to me is the multitude of your sacrifices, says the Lord? I am full of whole burnt offerings of rams, and I do not want the fat of lambs and goats. Even if you come to appear to me, who sought these things from your hands? You shall not go on treading my court. If you bring fine flour, it is vain. Incense is an abomination to me; I cannot endure your new moons and sabbaths and great day. Fasting and idleness and your feasts my soul has hated; you have become a surfeit to me.' And through the prophet Malachi he says the same still to people greatly hated. And he remembers times in which those throughout all the earth would offer him the incomparable",
    ],
    [
        A("Amos 5:21-23", "Quoted: I have hated your feasts; I will not look on your sacrifices; take away the noise of your songs."),
        A("Micah 6:6-8", "Quoted: with what shall I take hold of the Lord; do judgment, love mercy, walk with God."),
        A("Matthew 16:24", "Quoted: if anyone wants to come after me, let him deny himself and take up his cross."),
        A("John 12:26", "Quoted: where I am, there let my servant be."),
        A("Isaiah 1:10-14", "Quoted: rulers of Sodom; I am full of burnt offerings; incense an abomination."),
        A("Malachi 1:11", "The pure sacrifice from the nations — continued in the next column."),
    ],
)

S(
    8,
    "From the rising of the sun a pure sacrifice",
    [
        "fragrance of the bloodless and intelligible sacrifice. For he said again, 'I have no will in you, says the Lord Almighty, and I will not receive a sacrifice from your hands, because from the rising of the sun even to its setting my name has been glorified among the nations, and in every place incense is offered to my name and a pure sacrifice, because my name is great among the nations, says the Lord Almighty.' You understand that he says incense and a pure sacrifice will be brought up to him from every nation. And just as, naming the new covenant in Christ 'new,' he has made the first old — for divine Paul writes to us this way — so here too, having said that the sacrifice from every nation will be pure in its times, he condemns the ancient one as not being so. For how is something pure in a way, which neither cleanses nor even has the power to perfect toward virtue? That is why the blessed Paul says that it was not without fault, and that the things through Christ had to be brought in, and that a place for the second was sought.",
        "Palladius: Was the worship in shadows wholly unwanted, then, by the all-holy God?",
        "Cyril: Entirely so. And you can hear him saying plainly to those from Israel, through Jeremiah's voice, 'Thus says the Lord: Gather your whole burnt offerings with your sacrifices, and eat meat. Because I did not speak to your fathers, and I did not command them, on the day I brought them up from the land of Egypt, about whole burnt offerings and sacrifices. But this word I commanded them, saying, Hear my voice.' As far as the legislator's exact intent went, the Law still in shadows would not have been oracled at all at the beginning, with the worship in spirit left silent. But because the thing was burdensome, and being able to fulfill the perfectly good was not, at that time, passable for them — I would say it was hard and not without roughness — a kind of infant-fitting practice, having the shaping of the truth, the Law in letters, was decreed economically. Yet the one who marked out the laws for us showed clearly that those things were not most to his heart; the things through Christ were thrice-desired. And so he said again, 'Therefore I have mowed down your prophets, I have killed them with the words of my mouth, and my judgment will go out as light; because I want mercy and not sacrifice, and knowledge of God rather than whole burnt offerings.' For much better before God than a falling calf and the slaughter of a sheep is love toward brothers, unto the fulfilling of the Law, and the surpassing of the knowledge of Christ, through whom the Father himself would become known to us. And that the thing is a bringer of eternal life, no one would doubt, when Christ says to the Father in the heavens, 'And this is eternal life, that they may know you, the only true God, and Jesus Christ whom you sent.' He will not",
    ],
    [
        A("Malachi 1:10-11", "Quoted: I have no will in you; from the rising of the sun a pure sacrifice among the nations."),
        A("Hebrews 8:13", "In saying new he has made the first old."),
        A("Hebrews 8:7", "If the first had been faultless, no place for a second."),
        A("Jeremiah 7:21-23", "Quoted: I did not command them about burnt offerings; hear my voice."),
        A("Hosea 6:5-6", "Quoted: I have killed them with the words of my mouth; I want mercy and not sacrifice."),
        A("Matthew 9:13", "I want mercy and not sacrifice.", "possible"),
        A("Romans 13:10", "Love is the fulfilling of the Law.", "possible"),
        A("Philippians 3:8", "The surpassing of the knowledge of Christ."),
        A("John 17:3", "Quoted: this is eternal life, that they may know you, the only true God."),
    ],
)
