# -*- coding: utf-8 -*-
"""English of De adoratione Book 1, sections 14–26 (PG 68.160–184). From locked Greek."""

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
    14,
    "We love the goods in hand too late",
    [
        "Cyril. For it is always somehow slack and fallen back toward desire of the goods in hand, and it does not much long for the things of which it would have the power. But if there should be a calling-over to the other side, and it is allowed to be overcome in the bright things it would have, then at last it barely perceives, after suffering, what it ought to have beaten off with every strength, and not to have let the assault come through trial, cutting it off beforehand.",
        "Palladius. True.",
        "Cyril. It is necessary, then, and wise, and of the things most profitable of all, to cut off well beforehand the wretched things and the assault of the unwilling hired service, and to try to turn away swiftly from the things which, if we should come to a trial of them, we shall lie in every evil.",
        "Palladius. It is so.",
        "Cyril. And if the yoke of necessary slavery should be brought upon us from divine anger, and also the need to come down into a reprobate mind, it is not easy to stand against it. But I would say it is useful, at least, only to keep remembering from what things into what we have been turned, and to lament bitterly the overlooking, and the scarcity of the help from above; 'for the grief according to God works a repentance unto salvation not to be regretted.' And when divine anger is not hung over us, but it is possible, in our power, to choose and to do what seems good, and to possess still somehow loose and wholly unforced the swing both ways — I mean the one toward the worthless and the one toward the good — we must refuse in a manly way the softness as in worthlessness, and I think we must love to shake off the pleasures at the enemies' hands, and the doing of things under enemies' power, who are said to rule this age. And even if something should come near that is not without worldly good days — I mean the good days honored in the world — it turns in every way to a shameful and unbeautiful end.",
        "Palladius. How have you said?",
        "Cyril. Do you wish us to speak, taking from ancient examples?",
        "Palladius. Very much so.",
        "Cyril. When a famine was wasting those throughout almost the whole land, those from Jacob thought it good to come to the Egyptians; and they were young men, some ten in number, and the aim of the journey abroad was to buy foods, and there was nothing else. And when they had come to this and were at last recognized as brothers, Joseph then giving grain and ruling the Egyptians, Pharaoh received what had been done toward them, 'And Pharaoh said,' it says, 'to Joseph: Say to your brothers: Do this: Fill your wagons, and go away into the land of Canaan, and taking your father and your belongings, come to me, and I will give you of all the goods of Egypt, and you shall eat the marrow of the land. And you, command these things, that they take wagons from the land of Egypt for your children and your wives, and taking",
    ],
    [
        A("2 Corinthians 7:10", "Quoted: the grief according to God works repentance unto salvation."),
        A("Romans 1:28", "Coming down into a reprobate mind."),
        A("John 12:31", "The ruler of this age.", "possible"),
        A("Ephesians 6:12", "Rulers of this age.", "possible"),
        A("Genesis 42:1-3", "Ten brothers go down to Egypt for grain."),
        A("Genesis 45:17-19", "Quoted: fill your wagons; take your father; eat the marrow of the land."),
    ],
)

S(
    15,
    "Egypt's marrow; Rabshakeh's vines",
    [
        "your father, come, and do not spare with your eyes your vessels; for all the goods of Egypt shall be yours.' So the ruler of the Egyptians promised them rest, and to fatten them well with luxury, and he even granted wagons, smoothing, I think, the descent for those who hesitated. But they went down at once with their whole house, having somehow preferred the temporary enjoyment of eatables to land and country given by God; for it was far better and finer, I suppose, to inhabit that, even if the thing was accomplished with a little labor. And when they had come into Egypt, they thought perhaps they had also escaped thereafter the labors at home, to whom the sense of the delights at hand was somehow sweet. But as time crept on, the crowd noble and free from above and from the fathers runs under the inglorious yoke of slavery. So if falling into the more shameful things should come with worldly good days, it must be refused, my good man, if freedom is of any account with us, and the slavish thing and mind is abominable and hated.",
        "Palladius. You have spoken best.",
        "Cyril. And what? Do we not also say that other thing, which, as it seems to me, is in no moderate labor together with what we have just said, toward profit?",
        "Palladius. What do you mean?",
        "Cyril. Rabshakeh the Babylonian, general of the Assyrians, once dragged a crowd of spear-bearers beyond number, and came to besiege, or rather, having supposed that he would take the holy city from the foundations with very little toil. Then, before the weapons, he put forward the unpracticed — no, the very customary — tongue-sickness against God. And saying a thousand things of ill omen, he called out at last to those who lived in the holy city: 'Thus says the king of the Assyrians: If you wish to be blessed, come over to me, and each of you shall eat his vine and his fig-trees, and you shall drink water of your cistern, until I come and take you into a land like your land, a land of grain and wine and breads and vineyards.' See then that he too promises the luxury and delight upon vine and fig, and he added that 'And you shall drink water of your cistern.'",
        "Palladius. But what would these things wish to show, if they were led to a spiritual contemplation?",
        "Cyril. In a double manner, I think, the power of worthlessness is brought to its end in us. For either by the pleasures from outside, or by those inborn and in us, being persuaded by ourselves and also by others to revel, those easy toward sin would be caught, having slipped toward anything most unseemly. And the Savior's disciple would also show us that this is true, saying in this way, 'that all that is in the world, the desire of the flesh, and the desire",
    ],
    [
        A("Genesis 45:20", "Quoted: do not spare your vessels; all Egypt's goods shall be yours."),
        A("Exodus 1:8-14", "The free people later under the yoke of slavery in Egypt."),
        A("2 Kings 18:31-32", "Quoted: Rabshakeh's offer of vine, fig, cistern, and a land like their land."),
        A("Isaiah 36:16-17", "Parallel Rabshakeh speech."),
        A("1 John 2:16", "Quoted opening: all that is in the world, the desire of the flesh."),
    ],
)

S(
    16,
    "Desire of the flesh, of the eyes, and pride of life",
    [
        "of the eyes, and the pride of life.' For the desire of the flesh is inborn and rooted in us ourselves and remaining, and the divine Paul also named it a law of sin, dwelling in the members of the flesh. And the delights and pleasures from outside and brought in are the things through the eyes. For the things from wealth are wondered at through eyes, and also fine clothing, and the things to which some would cling, that they may have the sweetest enjoyment, giving them no mean vote. So then vine and fig would be toward a type of the delight and luxury from outside and brought in, showing with a fine grace together the temporary and easily withered character of the things in the world, and with this the sweet together with what is accustomed to darken. For every worldly luxury has a sweet sharing at the moment, but it darkens very much and makes terribly drunk the one who has received it. And the cistern is an image of the inborn motions in us. For these have not been brought in as those have, but they spring as it were in us, bubbling up from the flesh itself. Of all these then, natural and brought on, the evil powers say that the sharing will be free for us, and the enjoyment wholly broad, if, having left self-control as a holy and unshaken city, we go over to the king of Babylon, who was in type of Satan. But Rabshakeh promised that the delight at the moment would be let go to them and given besides, if they went over to the Babylonians. But they were not persuaded, thinking rightly; for there will follow in every way, upon wishing to choose the worldly things, the need to fall into an unwanted slavery, and to come into the rank of those taken by the spear.",
        "Palladius. The word is exact. And what would be the loosing of these things? Tell me, since I would hear it most gladly.",
        "Cyril. What else than the one that stands opposite to the first and at the beginning? For turning aside by swings of our own wishes toward wishing to live shamefully, and pushing away the fineness of the blameless way of life, we have fallen toward a low-born and slavish mind, thinking only the things on the earth, and lying wholly in the pleasures of the flesh. That is why God thereafter also let us slip down into a reprobate mind.",
        "Palladius. So then it is necessary to run back toward virtue?",
        "Cyril. Without neglect, my good man, no longer longing for the life in the world, according surely to that word spoken rightly through Paul's voice: 'For you died, and your life is hidden with Christ in God.' But rather thirsting for the enrollment in heaven, and having made the city above as it were fatherland and city, and crying out well to God: 'Let me go, because I am a sojourner on the earth, and a stranger, as all my fathers were.' For the one who walks on the earth, and has a bright",
    ],
    [
        A("1 John 2:16", "Quoted in full: desire of the flesh, of the eyes, and the pride of life."),
        A("Romans 7:23", "The law of sin in the members."),
        A("Romans 7:18", "Desire dwelling in the flesh.", "possible"),
        A("Isaiah 28:1-7", "Luxury that darkens and makes drunk.", "possible"),
        A("Colossians 3:2", "Thinking the things on the earth."),
        A("Romans 1:28", "Let slip into a reprobate mind."),
        A("Colossians 3:3", "Quoted: you died, and your life is hidden with Christ in God."),
        A("Hebrews 12:23", "Enrollment in heaven.", "possible"),
        A("Galatians 4:26", "The city above.", "possible"),
        A("Psalm 39:12", "Quoted: I am a sojourner and a stranger, as all my fathers (LXX 38:13)."),
        A("Philippians 3:20", "Walks on earth; citizenship in heaven."),
    ],
)

S(
    17,
    "Sojourners; leave your land",
    [
        "citizenship in heaven would reasonably appear, from the things themselves, a sojourner and a stranger in truth. And so the Savior's disciple commands that we ourselves also make this a conspicuous and fair boast, saying in this way: 'Beloved, I exhort you as sojourners and strangers to abstain from the fleshly desires which war against the soul.'",
        "Palladius. Would such a disposition then be enough toward the accomplishment of virtue — I mean, putting an end to the fleshly desires?",
        "Cyril. If there should also be added, wisely, the things from the other fairness, clearly the spiritual. For it is written: 'Your commandment is very broad.' Or is not the stain in us double, of soul and of body? I would think that the things accustomed to wash must follow, and with much reason, equal in force and equal in work to the things accustomed to defile.",
        "Palladius. You have spoken rightly.",
        "Cyril. As then, of course, the dirt is double, of soul and of body, so the thorough cleansing would reasonably be of soul and of body. Yet that thinking it a sojourning, to love the life in the world, is not without profit for those so disposed, to see without toil, if someone should choose to make Abraham an image of the thing, to whom it was said by God: 'Go out from your land and from your kindred and from the house of your father. And come into a land which I will show you, and I will make you into a great nation, and I will bless you, and I will make your name great, and you shall be blessed, and I will bless those who bless you, and those who curse you I will curse, and in you all the tribes of the earth shall be blessed.' You understand how he commanded him to set out not from land and house only, but also from the kindred, and also from the house of the father, and to come into a land which the one who calls would himself show?",
        "Palladius. But what is this?",
        "Cyril. Then is it not somehow clear that, when God calls into a following — clearly the spiritual — and wishes those he would choose to honor to creep out of the life in the world, I mean again the one in pleasures and loves of flesh, it is wholly struck-minded to think anything better than such a thing? For let a man count fatherland and race and father's house and the possession of earthly things as nothing. That is why the Savior himself also called us toward the equal manliness, saying: 'He who loves father or mother above me is not worthy of me, and he who loves son or daughter above me is not worthy of me; and whoever does not take his cross and follow after me is not worthy of me.' And he added: 'And everyone who has left brothers or sisters or father or mother or wife or children or fields or houses for the sake of my name shall receive many times more, and shall inherit eternal life.' Or do you not say that it is the work of the utmost strength understood in Christ, the so bright and",
    ],
    [
        A("Philippians 3:20", "Citizenship in heaven while walking on earth."),
        A("1 Peter 2:11", "Quoted: as sojourners and strangers abstain from fleshly desires."),
        A("Psalm 119:96", "Quoted: your commandment is very broad (LXX 118:96)."),
        A("2 Corinthians 7:1", "Cleansing from defilement of flesh and spirit.", "possible"),
        A("Genesis 12:1-3", "Quoted: go out from your land; I will make you a great nation."),
        A("Matthew 10:37-38", "Quoted: who loves father or mother above me; take the cross."),
        A("Matthew 19:29", "Quoted: who has left brothers, fields, houses for my name."),
        A("Luke 18:29-30", "Parallel leaving family for the kingdom.", "possible"),
    ],
)

S(
    18,
    "Follow Christ; Abraham leaves Haran",
    [
        "conspicuous manliness, which counts these things as nothing? And it makes much of the need to follow Christ.",
        "Palladius. Very much so, since those called to the wedding and refusing the coming have also slipped away from the best hope and from the gladness in Christ. Of whom one said: 'I have married a wife, and I cannot come.' And another, saying he had bought a field, made the temporary things better than the calling.",
        "Cyril. Well done, Palladius; for you gladden us, saying what is likely, and from a very great aptitude leaping up well beforehand toward understanding warmly the end of the word. See then that for those who follow God wholly and in every way, and have made the things of the flesh and worldly love of pleasure second to the hope in him, there will follow in every way a rich sharing in the blessing from above. For what does he say to Abraham? 'And I will make you into a great nation, and I will bless you,' and the things joined to these. You see, then, how great a crowd of spiritual goods he heaped on him? And in what manner Abraham sets out from the land that bore him — how is it not worth seeing? 'For he took,' it says, 'Sarah his wife, and Lot the son of his brother, and all their belongings which they had acquired, and every soul which they had acquired in Haran. And they went out to go into the land of Canaan, and Abraham passed through the land into its length, as far as the place Shechem, to the high oak.' For he went out from Haran, leaving no remnant of himself in it, and as with his whole race and whole house, most eagerly running over into the land of Canaan, which God showed. Then he goes through the land into its length, and comes into the high land. For the one who has wished to follow the divine decrees very well, and to count the calling from above worthy of the best care, let him go out of the life in worldly pleasures wholly through and through, and as with his whole race, having left no remnant of his own mind in the things in which he once was. For so he sets out rightly, and he will go through the land, for he has been called by God, so that, as the blessed Paul writes, he may be strong to grasp with all the saints what is the breadth and length and height and depth of the mystery of Christ. For then he will go up well toward the high land, that is, toward the habit housed in virtues, and having no longer from any side what is thrown down into love of flesh. And what again of the goods there will be for the one who has already come to this, we shall know from the holy Writings themselves. 'For the Lord appeared,' it says, 'to Abraham, and said to him: To your seed I will give this land. And Abraham built there an altar to the Lord who had appeared to him.' For while he lingered in the land of his fatherland, and had not yet gone over toward the holy land, only an oracle was given of the need to go over into another, having slighted the land that bore him. But when he came into the land of Canaan with his whole house and with all his gear, and toward the holy",
    ],
    [
        A("Luke 14:18-20", "The called who refuse: I have married a wife; I have bought a field."),
        A("Matthew 22:2-5", "The wedding call refused.", "possible"),
        A("Genesis 12:2", "Quoted: I will make you a great nation, and I will bless you."),
        A("Genesis 12:5-6", "Quoted: he took Sarah and Lot; passed through to Shechem, to the high oak."),
        A("Ephesians 3:18", "Quoted sense: breadth and length and height and depth."),
        A("Colossians 2:2-3", "The mystery of Christ.", "possible"),
        A("Genesis 12:7", "Quoted: the Lord appeared; to your seed I will give this land; Abraham built an altar."),
    ],
)

S(
    19,
    "Theophany and altar; Lot at Sodom's gate",
    [
        "land he sprang up, the grace of the seeing of God has been given, and the firmness of the hope in the security of freedom, and the being permitted thereafter to raise an altar. And so for us too, according to the equal figure of the word, while we remain with the world and with the most abominable pleasures according to it, there will be no grace from God; but when we have been called and yield to the divine laws, springing up from the desire and eagerness toward anything of the goods as toward a high land, God puts in the knowledge of his own glory, and promises the firmness of the hope; and so he makes the mind in us strong, as already somehow to be able to bring spiritual sacrifices, and to become a sweet smell of Christ to God and Father, according to what is written; and to present also to him the body, a living sacrifice well-pleasing to God, the reasonable and in-spirit worship acceptable with God. For he receives gladly the manners of the worship in spirit, and counts the thing a spiritual sacrifice.",
        "Palladius. So then it is fitting to shift toward the better, setting out from the more shameful; and to receive as most gladly the calling from above, and to love to linger as much as possible in the things honored from the Law and that have obtained the best vote with God. As for seeking to go backward and to return upon something of the things accustomed to do wrong, we shall not be free of blame.",
        "Cyril. No indeed, my friend. For it is wholly hard to choose to be sick again with the things from which one would go out; so that for those once taken out by the power of God from a worldly way of life, it is very perilous even only to look toward it, and as it were to go toward a remembrance of faults, sending the mind into the love of them. And so the divine Singer pleaded, saying: 'Turn away my eyes from seeing vanity.' For vanity in truth is the distraction of this life, and the empty delight of the temporary things, from which that it is fitting to stand apart and to leave, and for the one who has chosen in truth to walk straight to refuse even the mere looking as still in thoughts and with pleasure, one may learn easily from here too.",
        "Palladius. From what do you say?",
        "Cyril. The inhabitants of Sodom, being wildly stung into the pleasures against nature, and dishonoring the law of intercourse which nature set for the begetting of children, and being whetted by male seasons, and accomplishing everything most out of place, provoked to angers, and as it were forced the Creator, though he is a lover of men, to go toward the penalty upon them. And when the time of the need to suffer was at the doors, the long-suffering toward them having as it were been spent, those who would fulfill this broke in at Sodom. And it is written thus: 'And two angels came to Sodom at evening. And Lot was sitting",
    ],
    [
        A("2 Corinthians 2:15", "A sweet smell of Christ to God."),
        A("Romans 12:1", "Present the body a living sacrifice; reasonable worship."),
        A("1 Peter 2:5", "Spiritual sacrifices.", "possible"),
        A("John 4:23-24", "Worship in spirit."),
        A("Luke 9:62", "Looking back after being taken out.", "possible"),
        A("Psalm 119:37", "Quoted: turn away my eyes from seeing vanity (LXX 118:37)."),
        A("Romans 1:26-27", "Pleasures against nature."),
        A("Genesis 19:1", "Quoted: two angels came to Sodom at evening; Lot sat at the gate."),
    ],
)

S(
    20,
    "Lot receives the angels",
    [
        "at the gate of Sodom. And Lot, seeing, rose up to meet them, and bowed with his face to the earth, and said: Behold, lords, turn aside into the house of your servant, and lodge, and wash your feet, and rising early you shall go away on your way. And they said: No. But we will lodge in the street. And he forced them, and they turned aside toward him, and they went into his house, and he made a drink for them. And he baked unleavened cakes for them, and they ate before they lay down.' For Lot, inasmuch as he was also of Abraham's blood, and had been reared in the laws of rightness, and had taken care of piety toward God in no small account, was sojourning at Sodom. And he was on them an incomer and a stranger both in race and in manner. 'For what fellowship has light with darkness? Or what portion has a believer with an unbeliever,' according to what is written? And having been stronger than the evils of the place, and going the road of life customary to him, he held to holy pursuits, and, honoring the law of hospitality as much as possible, sitting at the inlets of the town, he receives kindly those who run in at them, knowing the thing is dear to God. And when those who would bring the penalty on those who had run wild unbridled into wantonness had come (and it was a pair of angels), he meets them swiftly, and shows beforehand, as a clear sign of the kindness in him, the greeting. For he bowed with his face to the earth, and urges them to go home, and to revel in the laws of love. And they say: No, but we will lodge in the street; marking by this that they are strangers and without a hearth, and whetting, I think, the one who had chosen to show hospitality toward a more intense eagerness, and all but hinting with a fine grace that he would not fittingly let them go, being empty of a hearth and thrown out in the very crossroads; which the righteous man also understood, and forced them the more, and did not take the refusal as a prize, as from a weak and rather watery mind. So he houses them, and set unleavened breads, and made a drink. But these things the righteous man. And the Sodomites, sick with a naked and shapeless pleasure, going round the righteous man's chamber unholy, and having fallen beyond the shamelessness that comes to the utmost, thought it right that the customary things be let go for them to do; then, when they ought to have chosen hospitality, they wished to harm with the wantonness against nature. And they wished to disable Lot, who was turning them away from attempts so wild and most abominable, and he would perhaps have been caught even into the suffering itself, if those who save had not been there. 'For the men,' it says, 'stretching out their hands, drew Lot in toward themselves into the house, and they shut the door of the house. And the men who were at the door of the house they struck with sightlessness from small to great, and they were disabled seeking the door.' And the things of the help for him have not been measured in these only. For it is written again: 'And when dawn came, the angels were urgent",
    ],
    [
        A("Genesis 19:1-3", "Quoted: Lot at the gate; hospitality; unleavened cakes."),
        A("2 Corinthians 6:14-15", "Quoted: what fellowship has light with darkness; believer with unbeliever."),
        A("Hebrews 13:2", "Hospitality to strangers; some have entertained angels.", "possible"),
        A("Genesis 19:4-5", "The Sodomites demand the guests."),
        A("Genesis 19:10-11", "Quoted: the men draw Lot in; strike the others with sightlessness."),
        A("Genesis 19:15", "Quoted opening: at dawn the angels were urgent with Lot."),
    ],
)

S(
    21,
    "The angels take Lot by the hand",
    [
        "with Lot, saying: Rising, take your wife and your two daughters whom you have, and go out, that you too may not perish with the lawlessnesses of the city. And they were troubled, and the angels took hold of his hand, and of the hand of his wife, and of his two daughters, in the Lord's sparing them.' This is a sign for you, and a very clear one, that we are not whetted by words only, and leave sin by exhortations into the mind, but that the Savior God of all has come even to this gentleness toward us, as to make the help active, according at least to the, 'You took hold of my right hand, and in your counsel you guided me.' For since man's nature is not very strong, nor sufficiently able to swim out of the evil, God somehow contends along with it toward this. And he is seen assigning a double grace: persuading with admonitions and having found help, and setting it better than the evil at the feet and tyrannizing. And you may see that also true, that the caretakers of righteousness are very few, and the scarcity of good men in life is great; for a faithful man is a labor to find, according to what is written. Yet such a one is choice, and has been counted worthy of the care from above not as a side-work. For if he is in the world mixed with the others, he undergoes no harm from there, as a lily is snatched from thorns, and a righteous man would not perish with the ungodly, according to the voices of the holy ones.",
        "Palladius. It is fixed, then, that by the sparing from God, and by the running-together of holy angels, we shall both wash off the greed from worthlessness, and shall find without dispute that we are caught nowhere and in no way by the penalties of the evil, believing God who has cried clearly through one of the prophets, that 'I am the Lord your God, who holds your right hand, who says to you, Do not fear, Jacob, little Israel, I have helped you, says the Lord, who redeems you, Israel.'",
        "Cyril. Or would not Lot's having been hung from the angels' hand show the God who can do all as a fellow-worker to the holy ones? For these would be a type of God. Three at the start coming upon Abraham at the oak of Mamre, and two visiting Sodom. 'For the Father judges no one,' according to the Savior's own voice, 'but he has given all the judgment to the Son'; the Holy Spirit, clearly, being with him and existing in him by nature also.",
        "Palladius. You understand very well. And let us look round at what follows, if it seems good.",
        "Cyril. Most unreluctant, and I will speak. 'And it came to pass,' it says, 'when they had led him out outside, they said: Save your own soul; do not look round behind, and do not stand in all the country round; save yourself to the mountain, lest",
    ],
    [
        A("Genesis 19:15-16", "Quoted: take wife and daughters; the angels took hold of their hands."),
        A("Psalm 73:23-24", "Quoted: you took hold of my right hand; in your counsel you guided me (LXX 72:23-24)."),
        A("Proverbs 20:6", "A faithful man is a labor to find."),
        A("Song of Solomon 2:2", "A lily among thorns.", "possible"),
        A("Genesis 18:23-25", "The righteous not destroyed with the ungodly."),
        A("Isaiah 41:13-14", "Quoted: I hold your right hand; do not fear, Jacob, little Israel."),
        A("Genesis 18:1-2", "Three at Mamre."),
        A("Genesis 19:1", "Two at Sodom."),
        A("John 5:22", "Quoted: the Father judges no one; he has given all judgment to the Son."),
        A("Genesis 19:17", "Quoted: save your soul; do not look behind; to the mountain."),
    ],
)

S(
    22,
    "Save your soul; do not stand in the country round",
    [
        "you be taken along.' In the, 'Save your own soul,' I say it is clearly spoken: 'Keep yourself pure; and do not share in others' sins.' And be better than the hindrances in the world; for there is no exchange at all for a soul. 'For what will a man be profited, when he gains the whole world, and loses his soul?' And the need to say that the walking must be made without turning back signifies, I think, perhaps this: not to choose, by turnings-about into worthlessness, to think again the equal things with those brought under the penalty of fire from incontinence ('For no one,' he says, 'having put his hand to a plow and turned back is fit for the kingdom of the heavens'); but that we must hold the road toward salvation, not being distracted this way and that, and keeping in ourselves a mind light and easy to scatter by stale fantasies of worldly desires, but complete and sleepless, and having practiced always to look toward the straight. And I will say the still greater thing; for the angel says not only that he must already make the walking without turning back; he also added usefully, 'Do not stand in all the country round. Save yourself to the mountain, lest you be taken along.'",
        "Palladius. And what would 'Do not stand in all the country round' wish to show?",
        "Cyril. The sluggish, I think, and weak toward the need to fly out of the evil, which is perilous and damaging.",
        "Palladius. Tell how.",
        "Cyril. A prophetic word said: 'Woe, those who do the work of the Lord carelessly. — And run that you may grasp,' the divine Paul himself also says somewhere. For not wishing to do most strongly and in eagerness the running-away from the more shameful things, the mind having itself hard to tear away toward the ancient things, and as it were setting out sullenly from each of the worthless, and shifting most reluctantly toward what is of a nature to help — this would be nothing else than to stand at last in a country round of vice, though one ought to go out at a run. For it would be of the things possible, before coming outside the bounds of evil, always delaying and drawing back, to be caught by the penalty, before the stain is thoroughly cleansed, before the defilement melted into the soul from the ancient slackness is washed off, before the charges are unloaded, and one runs under the saving yoke, to rest through Christ. Best then of exhortations is, 'Do not stand in all the country round,' that is: Be not caught having delayed in any manner of worthlessness, but go up rather, as to a mountain, into some exceptional and conspicuous life, having nothing thrown on the ground, but shining in a high and lifted-up virtue, and set free from the lowest mind, that is, the earthly and fleshly. For it is written that 'The strong ones of God of the earth have been lifted up very much.' For the mind proper to holy things is highest of the earthly things.",
    ],
    [
        A("Genesis 19:17", "Quoted: save your soul; do not look behind; do not stand in the country round."),
        A("1 Timothy 5:22", "Quoted: keep yourself pure; do not share in others' sins."),
        A("Matthew 16:26", "Quoted: what will a man be profited if he gains the world and loses his soul."),
        A("Mark 8:36", "Parallel saying.", "possible"),
        A("Luke 9:62", "Quoted: no one putting his hand to a plow and turning back is fit for the kingdom."),
        A("Jeremiah 48:10", "Quoted: woe to those who do the work of the Lord carelessly."),
        A("1 Corinthians 9:24", "Quoted: run that you may grasp."),
        A("Matthew 11:29", "The saving yoke; rest through Christ.", "possible"),
        A("Psalm 47:9", "Quoted: the strong ones of God of the earth have been lifted up (LXX 46:10)."),
    ],
)

S(
    23,
    "The mountain, and Zoar the smaller city",
    [
        "Cyril. 'And the vulture's young fly the high things,' according to what is written, if they have their citizenship as on a mountain in heaven, and take for themselves the fatherland above. And Paul also writes somewhere: 'Seek the things above, not the things on the earth.'",
        "Palladius. So then the intelligible mountain is the life in sanctification, and the stretched-high character of the exceptional way of life, the one in uncleannesses and sin-loving, and melted into earthly things, being understood as below.",
        "Cyril. You have spoken well; for the word shows us this very well, and you might still wonder at this also.",
        "Palladius. At what?",
        "Cyril. For the blessed angel said that divine Lot, running through without neglect and without turning back, must spring up to the mountain. He pleaded, saying: 'I ask, Lord, since your servant has found mercy before you, and you have magnified your righteousness, which you do upon my soul's living; but I shall not be able to be saved through to the mountain, lest the evils overtake me, and I die. Behold, this city is near for me to flee there, which is small; there I shall be saved. Is it not small, and my soul shall live? And he said to him,' it says: 'Behold, I have admired your face also in this word, of not overthrowing the city about which you spoke. Hurry then to be saved there, for I shall not be able to do a thing until you enter there. Therefore he called the name of that city Zoar. The sun came out upon the land, and Lot entered into Zoar.'",
        "Palladius. And what profit would there be for us through these things also? I would wish, as you well know, to learn it through.",
        "Cyril. Or do you not understand, though you have leaned much toward a very great aptitude, that for those who have just run out of worthlessness, and think they must go upon the path of salvation, virtue is not at once, nor from first attempts, graspable, nor is the thing that seems good easy to walk? But neither would one easily be brought up into an exceptional way of life, nor would he become far from the passions as it were reared with him, but he will be outside of such things gently, at least as far as eagerness toward better things and beginnings of attempts; yet not very high, or far; and he would all but go over into a land as into another, into a life that is praised, but has not yet obtained a high and conspicuous glory, such as was the tutoring according to the Law, carrying toward beginnings of a best and good life. For it is written: 'The beginning of a good road is to do the just things.' For in the way that, for those who have been eager about knowledge and long for the mystical contemplation, the word of catechesis would be suitable at the start and most fitting of all; but when they dart through toward a man already mature, and into the measure of stature of the fullness of Christ,",
    ],
    [
        A("Job 5:7", "The vulture's young fly the high things (LXX)."),
        A("Philippians 3:20", "Citizenship in heaven."),
        A("Colossians 3:1-2", "Quoted: seek the things above, not the things on the earth."),
        A("Genesis 19:18-23", "Quoted: Lot pleads for the small city; Zoar; the sun came out."),
        A("Proverbs 16:7", "Quoted: the beginning of a good road is to do the just things (LXX 16:7)."),
        A("Ephesians 4:13", "Quoted: a mature man; measure of stature of the fullness of Christ."),
        A("Hebrews 5:12-14", "Catechesis first; then solid food.", "possible"),
    ],
)

S(
    24,
    "Solid food, marriage, and unequal gifts",
    [
        "the more solid food would already somehow be fitting, that is, the word about the highest things, and every path thereafter of dogmatic search; so here too I say, that is, in the corrections of habits and manners, it would not be of the things possible for some to be able to spring up at once upon what has itself blamelessly, or into a beyond-nature and high-ridged way of life. It would be fitting, I think, little by little toward the habit that has itself completely, having begun from small and measured things, and all but running in beforehand as into a small city, neighbor to a high mountain, the way of life that sits under the exceptional and housed life and is in lesser things. That is why the righteous Lot also would be a type of those so disposed, thinking it right to lodge not at once on the mountain, but in the small city Zoar. Or shall we not also in the gospel preachings often find such economies having come to be in those who believe? And so the blessed Paul sends a letter, saying: 'It is good for a man not to touch a woman; but because of the fornications let each have his own wife, and each woman her own husband. And this I say by way of concession, not by command. For I wish all men to be as I myself also am. But each has his own gift from God, one thus, one thus.' You see how he showed us the exceedingly lifted-up character of self-control as a mountain, saying: 'It is good for a man not to touch a woman'; and he permitted us to lodge in Zoar, that is, in the training that still sits under what has itself perfectly — I mean the being permitted to be joined only with one's own wife? And the Savior said the best land would give back fruits, one a hundred, one sixty, one thirty. And he also distributed the talent, not in equal measure, but to one five, to one two, to one one; showing, I think, through these the unequal strength of the habits, and assigning to each as he would have aptitude and judgment. For as we said just now, 'Each has his own gift from God, one thus, one thus.'",
        "Palladius. You speak well.",
        "Cyril. The blessed angel permits him to lodge in Zoar. 'For behold,' he says, 'I have admired your face also in this word of not overthrowing the city about which you spoke. Hurry then to be saved there.' Then he says that 'The sun came out upon the land, and Lot entered into Zoar.' And you might wonder, my friend, what the mind of these things also would be, when you have learned: 'For I have admired your face,' he says, 'of not",
    ],
    [
        A("Hebrews 5:14", "Solid food for the mature."),
        A("Genesis 19:18-23", "Lot lodges in Zoar, not at once on the mountain."),
        A("1 Corinthians 7:1-2", "Quoted: good not to touch a woman; let each have his own wife."),
        A("1 Corinthians 7:6-7", "Quoted: by concession, not command; each has his own gift."),
        A("Matthew 13:23", "Fruit a hundred, sixty, thirty."),
        A("Matthew 13:8", "The good land giving varied fruit.", "possible"),
        A("Matthew 25:15", "Talents: five, two, and one."),
        A("Genesis 19:21-23", "Quoted: I have admired your face; the sun came out; Lot entered Zoar."),
    ],
)

S(
    25,
    "Lot's wife; the cave in the rock",
    [
        "overthrowing the city about which you spoke.' For the way of life that does not have itself perfectly toward virtue is in truth unwanted by God, and being overcome by the passions in anything at all is rejectable to him and not far from condemnation. Yet from love of men he permits, and having measured to the nature what is reachable at the start, he commands that they be saved, even those still practicing the good, and not yet wholly stepping through the blameable training. But even for those who have come to these measures, and drive into this condition, the running-in would not come without the divine light and the torch-bearing from above. 'For the sun rose,' it says, 'and Lot entered into Zoar.'",
        "Palladius. How very much you have said what is likely!",
        "Cyril. So then divine Lot ran in into the city still small, God permitting him; but the woman who followed him and ran out with him was also convicted as weak toward this. 'For she looked,' it says, 'behind, and she became a pillar of salt.' And see that the manly mind and the youthful spirit, even if it should not arrive perfectly, perhaps, at what pleases God, having begun to accomplish virtue, still makes habits of passions little by little toward what has itself better. But the weak and unmanly, whose sign is the woman, is wholly made useless by the turnings-about into worthlessness. For this, I think, is what becoming a pillar of salt shows; which would be a symbol of a mind withered, and of a mind laid to go over toward silliness, and having already somehow driven on into a last insensibility. And salt that has been made foolish will no longer be strong for anything, the Savior himself also said; and it will be made wholly useless, sent outside, and thrown under men's feet. So the woman was turned to stone, and not long after Lot added what was lacking. For it is written that 'Lot went up from Zoar, and sat in the mountain, he and his two daughters with him. For they feared to live in Zoar, and they lived in the cave, he and his two daughters with him.' For the mind goes forward as by steps upon what has itself completely, and springs up little by little toward what was at the beginning, not being suitably able, nor very sufficiently. And it goes forward and goes up toward the better, being tented by prudence and spiritual manliness as by some daughters of its own, and having left below the pleasure-loving and unmanly, of which the woman is toward a type. And it lives thereafter as on a mountain and in a cave; the mountain showing us well the high and lifted-up toward the spiritual good condition, and the cave the fixed and seated character of the remaining in virtue. For it is written thus about good men: 'He who walks in righteousness, speaking a straight road, hating lawlessness and injustice, and shaking his hands from gifts, making his ears heavy that he may not hear a judgment of blood, shutting his eyes that he may not see injustice, this one shall live in a high cave of a strong rock.' And the word upon this would also be for us not unconvincing in another way. For the rock is Christ, because of the strength and unwoundedness of the highest of all beings. And the cave in Christ would be understood as the Church, the lodging of the holy ones, the shelter of those who are pious, which the righteous inhabit,",
    ],
    [
        A("Genesis 19:21-23", "Zoar spared; the sun rose as Lot entered."),
        A("Genesis 19:26", "Quoted: she looked behind and became a pillar of salt."),
        A("Matthew 5:13", "Salt made foolish is good for nothing; thrown underfoot."),
        A("Luke 17:32", "Remember Lot's wife.", "possible"),
        A("Genesis 19:30", "Quoted: Lot went up from Zoar and lived in the cave with his daughters."),
        A("Isaiah 33:15-16", "Quoted: who walks in righteousness shall live in a high cave of a strong rock."),
        A("1 Corinthians 10:4", "The rock was Christ."),
        A("Matthew 16:18", "The Church as shelter.", "possible"),
    ],
)

S(
    26,
    "Abraham goes up from Egypt",
    [
        "and also as many as refuse the penalty through fire.",
        "Palladius. How well the word stands for us, my good man! And I for my part would wish the exercise to go for us also through as many other proofs as you will. For to love to know richly what makes for profit, I would think worth everything.",
        "Cyril. And yet, Palladius, you say what is likely. For the thing would be a fruit of a mind in us most loving of learning, and the word from us will be better than reluctance, not seeming to me the same as practicing an untimely silence running in upon narratives so bright and worth loving. So then, that we must fence ourselves off wholly and in every way, as far as it is possible, from the disposition and sharing toward the worthless; and also that being able to look up toward virtue would be added in no other way than according to this same manner, we shall see without toil, putting the eye of the mind in well, both to the things according to divine Abraham, and to the things accomplished beyond word at the going-out of those from Israel, which they made in the times of the Egyptians' greed, having broken the bonds.",
        "Palladius. Speak then in parts. For know well that you gladden us richly, if you should choose to do these things.",
        "Cyril. We were saying, then, that divine Abraham, once pressed out by an unbearable famine and by wants of the needed things, made the descent into Egypt not wished, and gave the necessities the rule. And being a stranger and an incomer, Pharaoh maltreated him with griefs and greeds. For he wished to disable the woman who lived with him, burned with unmixed pleasures into a longing for shameful work. But God did not allow this to be accomplished. 'For he tested,' it says, 'Pharaoh with great testings concerning Sarah, Abraham's wife.' And Pharaoh is an image and type of diabolic incontinence. For that one's aim, and of the things most eagerly pursued, is to love to put into the understandings of the holy ones also the seeds of the uncleanness in him, so that they may choose to bear fruit the things dear to him and according to pleasure. And these would be, I think, the charges into a many-formed sin. And everyone then would be caught, and will lie unwilling under that one's greeds. For the nature is sick with the lack of strength, yet God does not allow it, drawing back as it were the attempts against the holy ones, and the plots of the evil one. And it has happened that divine Abraham escaped the harms in no other way, except, having left the Egyptians' land, he went up again toward the place at the beginning and given by God, where, having also arrived, he was a leisured caretaker of good pursuits. And it is written thus: 'And Abraham went up from Egypt, he and his wife, and all that was his, and Lot with him, into the wilderness. And Abraham was very rich, with cattle",
    ],
    [
        A("Genesis 19:24-25", "The penalty through fire on Sodom.", "possible"),
        A("Genesis 12:10", "Abraham's unwilling descent into Egypt."),
        A("Genesis 12:17", "Quoted: he tested Pharaoh with great testings concerning Sarah."),
        A("Genesis 13:1-4", "Quoted opening: Abraham went up from Egypt with wife and Lot into the wilderness, very rich."),
    ],
)
