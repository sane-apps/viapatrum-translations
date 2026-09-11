# -*- coding: utf-8 -*-
"""English of De adoratione Book 1, sections 27–39 (PG 68.185–209). From locked Greek."""

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
    27,
    "Call on the Lord; brick and mortar",
    [
        "and silver and gold, and he went where he had gone out into the wilderness as far as Bethel, as far as the place where his tent was formerly, between Bethel and between Ai, to the place of the altar which he had made there at the beginning. And Abraham called there on the name of the Lord.' You understand, then, that with those who run up out of worldly incontinence into another holy life, all that is theirs must as it were set out together? For the forefather Abraham ran away from the Egyptians' land with his whole house and whole race, and I would add, with all his gear. For we must leave wholly, and love to shift as with a whole house into the wilderness, that is, into an undisturbed and clean condition of mind, from which also at the beginning man's nature went out, turning aside toward the worse by want of the goods from above. For the descent to strangers would mark this riddlingly, from a land as it were and tent of the things at the beginning and most dear, in which there is also an altar. For running back thus, until we come to be in the place and country of the altar at the beginning, that is, of the sanctification long grown with us, we too call on the God of all, saying that prophetic address: 'Lord, besides you we know no other. We name your name.'",
        "Palladius. You have spoken most finely.",
        "Cyril. And you may see the thing standing for us in no other way, if you also look well through the things that came to be upon the sons of Israel in their times; whom, when the Egyptians had taken them, a famine having pushed them down at the start, even those holy from above and from the root, and free, yoking them into a hired service unexpected and unpracticed for them, they forced wildly, having composed some such occasion of the cruelty upon them. 'For another king arose,' it says, 'over Egypt, who did not know Joseph. And he said to his race: Behold, the race of the sons of Israel, a great crowd, and it is strong beyond us; come, let us deal wisely with them, lest they multiply, and, whenever war happens, these too will be added to the opponents, and having warred us out, they will go out from the land.' For it pained, I think, the ruler of the Egyptians' land, that those under a necessary bond, yoked not according to judgment, should even choose at some time to look toward freedom. 'And he set over them,' it says, 'taskmasters of the works, that they might maltreat them from the works, and they built fortified cities for Pharaoh, Pithom and Rameses, and On, which is Heliopolis.' For the fruits of the unbearable greed were the continual endurance of suffering upon clay and brickmaking, and cities towered with walls, and raisings of mounds in the fields, and these were accomplished unpaid and with long sweat for those who labored. For the world-rulers of this age, having taken under hand the wretched souls of men, wear them out in clay and brickmakings and in the things done toward earth and about earth,",
    ],
    [
        A("Genesis 13:2-4", "Quoted: silver and gold; to Bethel, to the altar at the beginning; he called on the name of the Lord."),
        A("Isaiah 26:13", "Quoted: Lord, besides you we know no other; we name your name."),
        A("Exodus 1:8-10", "Quoted: a king who did not know Joseph; come, let us deal wisely with them."),
        A("Exodus 1:11", "Quoted: taskmasters; they built Pithom and Rameses and On."),
        A("Ephesians 6:12", "The world-rulers of this age."),
    ],
)

S(
    28,
    "Let my people go, that they may feast",
    [
        "and having bound them to an evil and profitless trial (for such the works of the flesh and about it appear), they force them to receive a bitter and wholly toilsome life, which will in no manner bring in what helps for those forced to practice it. For what would the works and passions of the flesh profit our wretched soul? And as it were a gain will be laid up from us for the devil and the demons, and it will be wealth and a boast of the opposing kingdom, just as, of course, Pharaoh also thought it of no small glory for himself that those from Israel should raise cities for him, having been forced to come to this unpaid and without food.",
        "Palladius. It is so. For the word is very clear.",
        "Cyril. So then the labor of the Israelites writes down a shaping and as it were a clear image of our vain and unholy pursuits on earth, Satan himself lying on them and leaping on them, and the evil powers with him, whom the divine Scripture marks with the names of the taskmasters; and I for my part would say that this is the evil distraction, full of sweat and labor, and filled as it were with clay and uncleanness and a mud-like pleasure. But God even then pitied those maltreated most unholy and most wildly by the Egyptians' greeds, and serving beside what was due. For he at once made the all-best Moses a servant of the gentleness toward them. Or shall we not also find God doing this toward us ourselves? For to us who have slipped into sins he grants the mercy, and at once puts his own law into the hearts of all as a mediator, carrying them toward a free life.",
        "Palladius. I understand what you say.",
        "Cyril. Do you wish, then, cutting the breadth of the history, that we say what is likely as we can?",
        "Palladius. Very much so.",
        "Cyril. It is written then thus: 'And after these things Moses and Aaron went in to Pharaoh, and said to him: Thus says the Lord, the God of Israel: Send out my people, that they may feast to me in the wilderness. And Pharaoh said: Who is he, whose voice I shall hear, so as to send out the sons of Israel? I do not know the Lord, and I will not send Israel out.' For those around Moses and Aaron affirmed that Israel must be let go from the Egyptians' country and land, God calling to a feast; for it is a true feast in truth to loose oneself from the yoke of the unwanted slavery, and to come thereafter under God, and to fulfill the things dear to him, no one standing against, or forcing one to choose instead and to",
    ],
    [
        A("Galatians 5:19-21", "Works of the flesh.", "possible"),
        A("Romans 6:21", "What fruit from the things of which you are now ashamed.", "possible"),
        A("Hebrews 8:10", "The law put into the hearts.", "possible"),
        A("Jeremiah 31:33", "Law written on the heart.", "possible"),
        A("Exodus 5:1-2", "Quoted: send out my people, that they may feast; I do not know the Lord."),
    ],
)

S(
    29,
    "A three days' journey; death or murder",
    [
        "love what seems good to him. And Pharaoh is very unbridled in tongue, and grows bold against the glory of God, saying he neither knows who the Lord is, nor will let Israel go. And divine Moses does not stop at all, and he strongly affirms that what seems good to God must be brought to its end. For when Satan blocks those who would have come under him from going into freedom, they must play the man, and become better than everything, I think, without any hindrance, and be seen least cowardly, but lie on it, saying: 'The God of the Hebrews has called us. We will go then a way of three days into the wilderness, that we may sacrifice to our God, lest death or murder meet us.' For these things the wise Moses also cried out to us then. For it is not, he says, after the likeness toward you, O Egyptians, that a calf is worship for us Hebrews, nor a pig, or a goat, or a man's statue, and a shadow of birds, and images of creeping things, the things set in shrines. The God and Master who crafted this whole has called us. Great then, and unranked with the Egyptians' gods, and above all the creation, is the God of the Hebrews, who calls us into the wilderness, to bring there the sacrifice well-pleasing to him. Egypt then is named a darkening, and I think those of us who are spiritually must apply ourselves to the things in shadow and types. For we must leave very well every thing, I think, that is accustomed to darken, and, having gone out as from a country lying under the tyrant, I mean Satan, the easiness in sins, be eager in a youthful way to go over into a loosed and cleaner life, and to step through a road of a lawful way of life, not laid under demons; for then we shall be able well to sacrifice to God the fruits of righteousness. And he affirmed that those from Israel must be sent a way of three days according to the wilderness, showing by this that they are not near the bounds of worthlessness and of the life being tyrannized. And divine Moses also uses a wise pretext, and says with a very ready occasion that those called by God must be separated from Egypt: 'Lest somehow death meet us,' he says, 'or murder.'",
        "Palladius. And what is this? For it is not ready for those who wish to understand.",
        "Cyril. I will tell: it was a custom for Egyptians, and it has been kept even until now among the worshipers of the idols, that those going in at temples must refuse to meet a dead body. For they say it is the highest defilement not only if someone should choose to touch, but even if it should fall in upon the mere sights. So from the customs among themselves he persuades them to think that the sacrificing would not be clean for them, if, when they had begun to do this from some unforeseen place, a dead man or a murder should happen upon them — that is, either one who has ended by a law of nature, or one forced out by the",
    ],
    [
        A("Exodus 5:3", "Quoted: the God of the Hebrews has called us; three days; lest death or murder meet us."),
        A("Romans 1:23", "Images of men, birds, and creeping things."),
        A("Exodus 8:26", "Sacrifice of the abomination of the Egyptians.", "possible"),
        A("Philippians 1:11", "Fruits of righteousness.", "possible"),
        A("Numbers 19:11-13", "Defilement from a dead body.", "possible"),
    ],
)

S(
    30,
    "Sacrifice in the wilderness; idle, you are idle",
    [
        "murderers. For you, he said, have temples and precincts, bolts and gates, inside which, having perhaps run in, it will be possible to sacrifice purely, as you yourselves think according to yourselves; but we, sacrificing of necessity in the middle of a city, in crossroads and in fields, are defiled by the sights of the dead. For there is wholly nothing to keep it off by bounds. And the word of the history would have for us the persuasive in the customs of the Egyptians, and what was said by all-wise Moses would be rightly said, even if it should be understood spiritually. For we must sacrifice as in a wilderness, and complete a holy feast to God, setting out from the Egyptians', and also refuse the sight of death. For with a leisured mind, and one that has come to stand far from being darkened in a worldly way, and setting the eye free from the things that carry it down into deadness and corruption, we shall sacrifice purely to the God who rules all. And dead works would be the things of the flesh. And worldly darkening is the muddying from evil and vain distractions, defiling the clean and clear ether of the mind. That it is fitting for those who wish to worship purely to be separated from these, the word of the history also persuades us.",
        "Palladius. And this at least is not unhidden; so complete for me what follows.",
        "Cyril. So then a hard-to-bear and sharp longing for the ancient freedom ran in, I think, upon those from Israel; and already having turned aside toward this, they provoked terribly to angers the one who binds them in the yokes of slavery. And saying that the desires upon such things are a work of leisure, he commands that the sweat upon the works be stretched tight for them, the accustomed quota being demanded without delay, and the distribution of the straw being cut off from them contrary to custom; for he said that 'You are idle, you are idlers; because of this you say, Let us go and sacrifice to our God. Now then go and work; for the straw shall not be given, and you yourselves shall give the quota of the brickmaking. So the scribes of the sons of Israel saw themselves in evils, saying: You shall not fall short of the brickmaking, the due for the day. And they met Moses and Aaron coming to meet them, as they were going out from Pharaoh, and they said to them: May God look upon you, and judge, because you have made our smell abominable before Pharaoh and before his servants, to give a sword into his hands to kill us.' For, my friend, do you not say it is exact, that whenever someone should choose to loose himself from the yoke of the devil's greed, and to take up instead the bright and free boast of the worship toward God, and to be still and to know the true Master, according to what is sung in the Psalms: 'Be still and know that I am the Lord God,' he will accuse us of the leisure and",
    ],
    [
        A("Hebrews 9:14", "Dead works.", "possible"),
        A("Hebrews 6:1", "Repentance from dead works.", "possible"),
        A("Exodus 5:8-9", "The quota of bricks without straw."),
        A("Exodus 5:17-21", "Quoted: you are idle; straw shall not be given; you have made our smell abominable."),
        A("Psalm 46:10", "Quoted: be still and know that I am the Lord God (LXX 45:11)."),
    ],
)

S(
    31,
    "Be still and know; I will redeem you",
    [
        "will upon this as an unholy thing, and the enemy of all rises up together with the other evil and unclean spirits, forcing them wildly to hold without stopping to fleshly and earthly uncleanness and to the things in the world, according to what is customary for each, and least allowing them to hold off from the well-worn worthlessness, and making even this hard to get, so that the evil may not, by being too ready, be spat out and come to a glut? For this, I think, is what the demanding the quota of the brickmaking strongly, and depriving them of the things through which it would come easily — that is, the straw — shows. And we are somehow of a nature, then most of all, to seek the customary things most eagerly and most strongly, and to be burned toward them with hotter desires, when something in between should appear that of necessity carries us toward not being able to obtain them. And when a divine law is retraining the human mind from the more shameful things, a long longing then most of all slips in, calling toward the same things, and all but persuading us to cry out against the lawgiver; and of this again the scribes of the sons of Israel are a proof as in shadows, worn out in the works, and not seeing the easy road upon them; for they were in want of straw, and they accused Moses and Aaron very much of the cause brought upon them, saying they had become an occasion, and that they had endured a more grievous assault of the greed, for no other reason than that a longing for freedom had slipped into them, having been persuaded by their words.",
        "Palladius. Do you not think you are saying what is likely and true?",
        "Cyril. Wholly, Palladius; for as soon as a useful desire and a good reasoning has perhaps stirred us toward the need to choose the things that seem good to God, and we have remembered a law toward piety, the enemy of all presses down more badly upon what is of a nature to harm, yet God draws out and saves. And so he said to Moses: 'Go, say to the sons of Israel, saying, I am the Lord, and I will lead you out from the domination of the Egyptians, and I will rescue you from their slavery, and I will redeem you with a high arm and a great judgment, and I will take you to myself for a people. And I will be your God, and you shall know that I am the Lord your God, who led you out from the land of Egypt, from the domination of the Egyptians.' For when Satan turns us away, and raises us out of every good desire, and pushes aside the turnings toward this by whatever manners he can, the law of God urges toward a good will, showing the one who helps as unbroken, and whetting into good daring by the richest hope, and sinewing by faith, and assigning us to God, in truth savior and redeemer.",
        "Palladius. How all-best a thing and saving is the faith, and the need to thirst to follow God!",
        "Cyril. You have spoken rightly. And that the faith creeps toward the good as its end, you will know well,",
    ],
    [
        A("Exodus 5:18-21", "Straw withheld; the scribes accuse Moses and Aaron."),
        A("Exodus 6:6-7", "Quoted: I am the Lord; I will lead you out; I will redeem you with a high arm; I will take you for a people."),
        A("Exodus 6:2-8", "The promise of redemption.", "possible"),
    ],
)

S(
    32,
    "Signs, plagues, and 'sacrifice in the land'",
    [
        "when our word has come to its own aim. For when those around Moses came again to Pharaoh to speak, and to persuade him to let Israel go from the Egyptians' land and to loose them from the old bonds, they wished to put him to shame with signs beyond word, and they showed a recasting of a rod into a serpent, and they promised most readily that they could still accomplish the greater and more lifted-up things, clearly through God. But he commanded his own magicians to do equal work, all but crying by this: We are not ignorant of such works. There are very many among the Egyptians, or of your kind; and wonder-working is a practice for the magicians, among whom you too are numbered. And when he grew very hard, and would not let Israel go, four terrible plagues, each worse than the last, are brought on; for a change of water into blood was accomplished beyond expectation, and frogs and gnats, and last a dog-fly, already made Pharaoh somehow softer, as from a necessity not to be borne. Calling in then those around Moses, he says: 'Go in and sacrifice to the Lord your God in the land. And Moses said, It is not possible for it to be so; for we shall sacrifice the abominations of the Egyptians to the Lord our God. For if we sacrifice the abominations of the Egyptians to the Lord our God before them, we shall be stoned. We will go a way of three days into the wilderness, and we will sacrifice to the Lord our God, as he said to us. And Pharaoh said: I will send you out, and you shall sacrifice to the Lord your God in the wilderness, but you shall not stretch far in going.' For when Satan stands against, and has known in a youthful way to set his own hatred of the good against our eagernesses toward the good, God sets himself against him, and presses him down when he grows bold, and tames him with plagues. And then he barely permits, not willingly; yet he tries all the same to persuade us to make the worship toward God not exact, and not yet to leave wholly the slavery to him. For he commanded the Jews that they must sacrifice not outside his own land, but in it. And Moses most wisely says, 'It is not possible for it to be so.' For the inventor of sin is always an introducer of the worthless things; and the divine law sends them out, and forbids the doing of whatever would seem good to that one. Those who wish to live rightly must therefore attend not to whatever the Evil One would say, deceiving, but to what the divine oracle cries out to us. 'For a lamp,' he says, 'to my feet is your law, and a light to my paths.'",
        "Palladius. True.",
        "Cyril. So then, when the Evil One holds us, or wishes to shut us in and to make us under him, we must worship the only God who is so by nature, and going as far as possible from double-mindedness, let us say, 'It is not possible for it to be so.' For no one can serve two masters; for either he will hate the one and love the other; or he will hold to the one, and despise the other.",
    ],
    [
        A("Exodus 7:10-12", "Rod into a serpent; the magicians do the same."),
        A("Exodus 7:20-21", "Water into blood."),
        A("Exodus 8:6", "Frogs."),
        A("Exodus 8:17", "Gnats."),
        A("Exodus 8:24", "The dog-fly."),
        A("Exodus 8:25-28", "Quoted: sacrifice in the land; Moses refuses; three days; not far."),
        A("Psalm 119:105", "Quoted: a lamp to my feet is your law, and a light to my paths (LXX 118:105)."),
        A("Matthew 6:24", "Quoted: no one can serve two masters."),
        A("Luke 16:13", "Parallel two-masters saying.", "possible"),
        A("James 1:8", "Double-mindedness.", "possible"),
    ],
)

S(
    33,
    "Two paths; the abominations of Egypt",
    [
        "And it is written again, 'Woe to fearful hearts, and slack hands, and to a sinner treading upon two paths!' For I for my part say we must make a clean and blameless worship to the God who rules all, having left wholly the worship under that one; and so seek to go toward the better in a manly way; and otherwise, 'We shall sacrifice the abominations of the Egyptians,' he says, 'to the Lord our God. For if we sacrifice the abominations of the Egyptians before them, we shall be stoned.' And as far as it belongs to the word of the history, the refusal has a ready occasion. For abominations here he says are the objects of worship; and calves were worship for the Egyptians. These, he says, if we sacrifice to the God of the Hebrews, we shall in every way and wholly whet the Egyptians to angers, who make the thing hard to bear. And sometimes the word is also persuasive. But as far as it belongs to a spiritual contemplation, it has no moderate profit. For what the crowd of the demons knows most of all to honor, and makes much of, and counts worthy of every account, we, putting it to death, complete a worship most sweet to God.",
        "Palladius. How have you said?",
        "Cyril. Or are not the passions of the flesh honorable among themselves? And not wholly through themselves, but since through them we perish, and are bound tight toward the slavery under them?",
        "Palladius. True.",
        "Cyril. These then, putting to death and as it were slaughtering, we shall be a smell of sweet fragrance to God. And Paul writes thus: 'Present your bodies a living sacrifice, well-pleasing to God, your reasonable worship.' And someone would do such a thing rightly, putting to death the members on the earth, fornication, uncleanness, passion, evil desire, and the greed. Each then of the passions in us is an abomination of the intelligible Egyptians, that is, most worshipful. For that it is a custom for the divine Scripture to call an abomination what is in the rank of an idol, and as it were a worship, God persuades, saying through Jeremiah's voice, about the Jews' Synagogue: 'What has the beloved done in my house, an abomination?' And if someone should wish to say that an abomination of the Egyptians is as it were a hated thing and a refusal, he would not go out from the fitting mind; for the things the unclean spirits are always accustomed to hate and to abominate, these will be laid up from us as a smell of sweet fragrance to God, and a spiritual sacrifice: faith, meekness, self-control, soundness of mind, love of one another, and the boasts of genuineness toward God.",
        "Palladius. And who would be those who sacrifice in the land of the Evil One? And who would be understood as those outside the land?",
        "Cyril. For those who have not yet gone out from the Egyptians', and who sacrifice to God in it, are very many, and perhaps beyond number; and those outside and in",
    ],
    [
        A("Sirach 2:12", "Quoted: woe to fearful hearts, slack hands, and a sinner treading two paths."),
        A("Exodus 8:26", "Quoted: we shall sacrifice the abominations of the Egyptians."),
        A("Romans 12:1", "Quoted: present your bodies a living sacrifice; reasonable worship."),
        A("Colossians 3:5", "Put to death the members on the earth: fornication, uncleanness, passion, evil desire, greed."),
        A("Jeremiah 11:15", "Quoted: what has the beloved done in my house, an abomination."),
        A("Ephesians 5:2", "A smell of sweet fragrance.", "possible"),
        A("Galatians 5:22-23", "Faith, meekness, self-control as spiritual sacrifice.", "possible"),
    ],
)

S(
    34,
    "Many called, few chosen",
    [
        "a wilderness, very few and choice; 'for many are called,' he says, 'but few chosen.' We have all then been called into freedom through the faith in Christ, and we have been redeemed from diabolic tyranny, Christ carrying us toward this, being well prefigured for the people of old in Moses and Aaron, so that in the same you may understand Emmanuel, being lawgiver and high priest and apostle, in the manner of the economy. But the most of those called still linger in the old evils, and having not yet gone out with a whole mind from worldly deceit, they worship God as in a naked and mere faith. These we say are those who sacrifice in Egypt, or who have come a little outside. 'For you shall not stretch far,' says the hard-hearted Pharaoh, even if you run out from the Egyptians' land. Those, however, who wish to please God with a whole transfer toward the good, and who have been set free even wholly from worldly confusion, are carried outside the Egyptians', and they run away from the tyrant's hand, and, as in a wilderness, in the leisured and loosed life, they sacrifice cleanly, being clean, to God. And I for my part would also say, in another manner, that those running from the worshiping of the creation beside the one who created, toward truth, and called into knowledge of the God who is so by nature, must be carried farthest from the Egyptians' land. For those who have not yet rubbed off the remnants of the ancient deceit from their own mind have not yet gone out perfectly. For some observe days and months and seasons and years. These, called toward the free dignity through Christ, still living in the Egyptians', sacrifice to God, keeping a life that would not be unwanted by Satan. And if someone should go out wholly, having said farewell to the more ancient customs, he sacrifices in a wilderness, and practices the life worthy of every praise.",
        "Palladius. I agree; for you think rightly. And let the word go for us again with the stream.",
        "Cyril. So then Pharaoh lies, and denies the promise, and does not yet let those from Israel go. Then he was maltreated with three other plagues, and he barely nods, saying he will let them go; and he was caught having lied again. 'For he is a liar, and has not stood in the truth,' according to the Savior's voice. And God, threatening, and also putting it in, sends the most violent hail upon the Egyptians, and also the locust, the field-destroyer, if one must also take a voice from the Greeks and say it. Then, then, the spear-bearers of Pharaoh's abomination, once terrible and unbroken, barely make a very great outcry against him, saying: 'How long shall this be a snare for us? Send out the men, that they may worship the Lord their God. Or do you wish to know that Egypt has perished?' And from here again it comes to me to think that Satan is perhaps somehow better than the powers under him, in the things in which winning would be fitting for him. For they, as",
    ],
    [
        A("Matthew 22:14", "Quoted: many are called, but few chosen."),
        A("Galatians 5:1", "Called into freedom through Christ.", "possible"),
        A("Hebrews 3:1", "Apostle and high priest.", "possible"),
        A("James 4:12", "One lawgiver.", "possible"),
        A("Exodus 8:28", "You shall not stretch far."),
        A("Romans 1:25", "Worshiping the creation beside the Creator."),
        A("Galatians 4:10", "You observe days and months and seasons and years."),
        A("John 8:44", "Quoted: he is a liar, and has not stood in the truth."),
        A("Exodus 9:23-25", "The hail."),
        A("Exodus 10:12-15", "The locust."),
        A("Exodus 10:7", "Quoted: how long shall this be a snare; send out the men; Egypt has perished."),
    ],
    [
        "Cyril names the locust agroleteira, 'field-destroyer,' and notes the word as taken from Greek poets; the epithet is kept in the English as 'field-destroyer.'",
    ],
)

S(
    35,
    "Young and old, flocks and herds",
    [
        "it seems, are very hard and wholly unsoftened, and late and barely would they still go, at least into a moderate sense of the divine anger; but he is lifted above in a wildness beyond word, and hardened to the utmost. For it is written that 'His heart has been fixed like a stone, and he has stood like an unhammered anvil.' So when a very great outcry had come to be upon him, he barely said to those around Moses: 'Go and worship the Lord your God. But who also are those who go?' And Moses says: 'With our young men and our elders we will go, with our sons and our daughters, and our sheep, and our oxen; for it is the feast of the Lord our God. And he said to them: Let the Lord be with you, in that I send you out — not also your household stuff? See, that evil is set before you. Not so; but let the men go, and worship God, for this you yourselves seek.' Understand then, my friend, that Moses said the breaking-up must be made in the best way; but he says, not so; and that he will let them go in part, and that what is left must as it were be a hostage for the returns of those who set out, the household stuff itself also remaining in Egypt. For let every young man of yours go, he says; and every race in its primes. But the divine Moses strongly affirms that it is fitting to set out very well, nothing having been overlooked; but together with those in youth and in the settings of age, with sons and daughters, and herds of oxen, and other flocks. For it is fitting for those who are eager to take for themselves the true freedom to love to be set free from the evils in the world, and to go a path upon virtues, leaving no remnant at all of their own soul and mind, through which they would again be carried under the greeds of the evil one. And the divine law calls to this young men and virgins, elders with younger, according to the Singer's voice, and every kind of the age understood in Christ. To whom the divine John also called, saying: 'I have written to you, children, because you have known the Father; I have written to you, fathers, because you have known him from the beginning; I have written to you, young men, because you are strong, and the word of God remains in you, and you have conquered the evil one.' And they would also be, in another way, young men a type of manliness, and elders of prudence, and sons and daughters of the infancy understood in Christ; for with manliness, and prudence, and the simplicity according to God, we shall set out from sin into sanctification. 'Play the man,' he says, 'and let your heart be strengthened.' And again: 'Become prudent as the serpents, and simple as the doves.' And having said that sheep and oxen run off together, he would mark, I think, that it is fitting not even to let go to Satan the bodily and less reasonable motions in us. And so the divine Paul writes: 'For as you presented your members slaves to uncleanness and to lawlessness unto lawlessness, so now present",
    ],
    [
        A("Job 41:24", "Quoted: his heart has been fixed like a stone; he has stood like an unhammered anvil (LXX 41:15/24)."),
        A("Exodus 10:8-11", "Quoted: who are those who go; with young and old, sons and daughters, flocks; only the men may go."),
        A("Psalm 148:12", "Young men and virgins, elders with younger."),
        A("1 John 2:13-14", "Quoted: I have written to children, fathers, young men; you have conquered the evil one."),
        A("Psalm 31:24", "Quoted: play the man, and let your heart be strengthened (LXX 30:25)."),
        A("Matthew 10:16", "Quoted: prudent as serpents, simple as doves."),
        A("Romans 6:19", "Quoted: you presented your members slaves to uncleanness; so now present them to righteousness."),
    ],
)

S(
    36,
    "Not a hoof left behind",
    [
        "your members slaves to righteousness unto sanctification.'",
        "Palladius. Why then does Pharaoh let those in youth and in their primes go, and take for himself the others?",
        "Cyril. For whom do you say is the one who remains in Egypt?",
        "Palladius. There were, I think, women in every way, children not yet in youth, and weak elders, and unreasonable possession.",
        "Cyril. Then, my good man, how do you not think that other thing at once?",
        "Palladius. What do you say?",
        "Cyril. For those swelling and young, and having a more prime habit toward piety, he counts burdensome; for he longs, I think, even unwilling, to be rid of those who have stood against, who are also able to act against him, and to help themselves when they are wronged, according at least to the, 'Stand against the devil, and he will flee from you.' And he takes much for himself of what is not of a nature to play the man, and as a weak and unwarlike race, and he loves a mind sick in itself with the female and soft, and such as has left youth and is without strength, and still boyish, and the thick and less reasonable, as in type with oxen and sheep.",
        "Palladius. You have spoken well.",
        "Cyril. And the hard-minded and unbending Pharaoh lies again. Then, when their whole country, so to speak, is being spent by the assaults of the locust, he makes Moses sent-for, Aaron running in with him, and says: 'Go and worship the Lord your God, only leave the sheep and the oxen, and let your household stuff run off with you.' And Moses said: 'But you too shall give us whole burnt-offerings, and sacrifices which we shall make to the Lord our God; and our cattle shall go with us, and we shall not leave behind a hoof; for from them we shall take to worship the Lord our God.'",
        "Palladius. And what mind would we fit to what was said by all-wise Moses? Or how would one take the things from Egypt and Pharaoh, and assign them to God?",
        "Cyril. And yet, my friend, the word is clear. For the one who has stood against and fights those who wish to be pious, if it should not be wholly possible that some lie under him, desires at least to have this in part; but the law of God teaches that the leaving must be made very cutting, allowing nothing whatever to lie and remain under him — not of soul, not a portion of mind, not an occasion of a bodily motion. And besides, we must also bring to God the finest and exceptional things of the life in the world. For this, I think, is what taking from Egypt, and sacrificing to God, shows. Or would not",
    ],
    [
        A("Romans 6:19", "Quoted completion: present your members slaves to righteousness unto sanctification."),
        A("James 4:7", "Quoted: stand against the devil, and he will flee from you."),
        A("Exodus 10:24-26", "Quoted: leave the sheep and oxen; Moses: we shall not leave behind a hoof."),
    ],
)

S(
    37,
    "Gold from Egypt; the Passover lamb",
    [
        "those who contend for our holy and divine doctrines through worldly wisdom, and hunt the brightness in diction and the sharpness in knowledge, and complete the reasonable worship to God, do this? 'For all wisdom is from the Lord,' according to what is written. But we say that the poets and prose-writers among the Greeks came to this brightness according to fine speech in a worldly spirit. And so the divine Paul: 'We have not received,' he says, 'the spirit of this world, but the Spirit from God, that we may see the things freely given us by God; which we also speak, not in words taught of human wisdom, but in a demonstration of spirit.' And that Moses was still in shadows in truth, when he said the exceptional things of the life in the world would not become rejectable to the God who is so by nature, he shows at once clearly, yet as in type and shadow. For when God commanded them to spoil the Egyptians, he said they must borrow gold and silver vessels, from tent-companion and neighbor, which is also brought to its end through women. For the thing is always somehow whispering and most talkative, and well-devised toward deceit. And gold and silver vessels from the Egyptians would be, I think, as I said just now, the things with which it was likely some of those in the world would be made solemn, even if they knew the true God. And what I say is something of this kind again. For the motions of mind and soul are common to all men, and the aptitude toward anything of good and of evil. But those who have used the advantages of nature well accomplish the glorious and exceptional life. Those, however, who turn them aside most mindlessly upon what is not fitting, somehow counterfeit the goods of nature and go the path upon the most shameful things. For manliness and prudence are fine for those who have used them best, and damaging for those who do not have them rightly; for it is possible to play the man and to be prudent with praise and applause; and it is possible again to possess these with much outcry. These then are common and in all, both in those still wandering and in those who know God. When then the manliness that was of old a worker of worthlessness, and the sharpness in understanding, are turned by us toward what seems good to God, they will all but, having been taken from Egyptians and from the life in the world, become holy and well-receivable to God; for they are recast into a need of virtue, and a service of sanctification, just as, of course, the gold and silver vessels from Egypt were shown useful toward the construction and completion of the holy tent. And after the spoiling of the Egyptians, and the death of the firstborn, those from Israel are barely redeemed, having sacrificed the lamb toward a type of Christ; for there was no other way to be able to obtain such a thing, since all redemption is in Christ, and through him every good giving. And they are sent out from the Egyptians' land in the middle of the night, all but being set free from darkness and from slavery together. For in the intelligible dark, and not in the divine light, the being a slave into sin always somehow loves to be. 'For everyone who practices the worthless things hates the",
    ],
    [
        A("Sirach 1:1", "Quoted: all wisdom is from the Lord."),
        A("1 Corinthians 2:12-13", "Quoted: not the spirit of this world, but the Spirit from God; not in words of human wisdom."),
        A("1 Corinthians 2:4", "In a demonstration of spirit."),
        A("Exodus 3:21-22", "Spoil the Egyptians; gold and silver vessels."),
        A("Exodus 11:2", "Borrow gold and silver from neighbor."),
        A("Exodus 12:35-36", "They spoiled the Egyptians."),
        A("Exodus 25:1-8", "Gold and silver for the holy tent."),
        A("Exodus 12:29", "Death of the firstborn."),
        A("Exodus 12:3-7", "The Passover lamb, type of Christ."),
        A("1 Corinthians 5:7", "Christ our Passover.", "possible"),
        A("John 1:29", "The lamb of God.", "possible"),
        A("James 1:17", "Every good giving."),
        A("Exodus 12:29-33", "Sent out at midnight."),
        A("John 3:20", "Quoted: everyone who practices the worthless things hates the light."),
        A("Romans 6:16-18", "Slave to sin.", "possible"),
    ],
)

S(
    38,
    "Unleavened dough; songs by the willows",
    [
        "light,' according to the Savior's voice. And the dough is carried out unleavened, and they flee without a provision of food. 'For the Egyptians,' it says, 'forced the people, to throw them out from the land in haste. For they said that we all are dying. And the people took up also their dough before the lumps were leavened, their kneadings bound in their garments upon their shoulders.' For I do not think that those who are about to cling to God, and have chosen a kinship toward him, must bring along a remnant of worldly vice, nor provision themselves with others' and unholy foods, clearly the intelligible ones; but they must love to be unleavened breads, the longing thereafter for the one who gives life to the world; for such would feast purely, and, completing the worship worth taking up to God, they remain under him through all.",
        "Palladius. It is fixed, then, that those who would be both lovers of God and good must as it were reach some holy and sacred land, of the life under Christ and not under a tyrant; and be eager to sacrifice not in the enemies', that is, not being in the sin-loving habit, and not very blameless, but rather in eagernesses toward virtue, and in a condition of habits housed outside the devil's tyranny.",
        "Cyril. Do not suppose it stands in another way than this, my good man; for the word has been made rightly for us. And it is possible, if it seems good, to look at these things also through another image. For when those who lived in the holy city, I mean Jerusalem, dared through the running-away toward anything out of place to grieve the Savior God of all, they came under the hand of the Babylonians, who, having taken them as spear-taken, commanded them to serve. For it was a necessity to yield to those who ruled, even them not willing. And they, being very much at a loss, and wailing over the unexpected disasters, sought at times at least to find a small consolation of the labor. And this was, to blunt the sharpness of the grief in them by the hymn-singings toward God; 'For I remembered God and was glad,' the divine David said, showing the hymn-singing toward God as a spiritual feast. But it seemed somehow shameful to those who wished to strike up and to fulfill the customary things, to love to put so sweet a sound into the ears of the foreigners, and already as it were to throw into the air the melody most sweet and most clear to themselves, the Babylonians sometimes smiling down, and being wholly burdened at the songs through instruments. That is why they also said: 'By the rivers of Babylon there we sat and wept, when we remembered Zion'; in which, according to the laws and customs of the Jews, the sacrifice of praise was brought with strings and instruments being completed, and charming with the songs those who came to the divine temple. And when they were bound tight in a stranger's yoke of slavery,",
    ],
    [
        A("John 3:20", "Quoted: everyone who practices the worthless things hates the light."),
        A("Exodus 12:33-34", "Quoted: the Egyptians forced them out; dough before it was leavened, bound in garments."),
        A("1 Corinthians 5:7-8", "Unleavened bread; keep the feast.", "possible"),
        A("John 6:33", "The one who gives life to the world.", "possible"),
        A("2 Kings 25:1-11", "Jerusalem taken; captivity to Babylon."),
        A("Psalm 77:3", "Quoted: I remembered God and was glad (LXX 76:4)."),
        A("Psalm 137:1", "Quoted: by the rivers of Babylon we sat and wept (LXX 136:1)."),
        A("Hebrews 13:15", "The sacrifice of praise.", "possible"),
    ],
)

S(
    39,
    "How shall we sing in a strange land",
    [
        "lamenting they say: 'On the willows in the midst of it we hung our instruments'; marking by this very thing that they were idle in songs. For the willow is a fruitless plant, or rather a fruit-destroying one; for it is said so by the poets among the Greeks. The instruments of song were then laid up toward idleness and fruitlessness; and crying out the occasion of this ease they say: 'How shall we sing the Lord's song on a foreign land?' And when Baruch had carried them Jeremiah's words, 'They all wept,' it says, 'and they fasted and prayed a prayer before the Lord; and they gathered silver, as each one's hand was able; and they sent it to Jerusalem to Joakim son of Hilkiah, son of Shallum the priest, and to the priests and to all the people found with him in Jerusalem.' And after other things: 'And they said: Behold, we have sent silver to you; buy with the silver whole burnt-offerings and for sin, and frankincense, and make manna, and offer it upon the altar of the Lord our God.' For they thought it fitting for themselves no longer to sacrifice, being housed outside a holy land, and acting for the time no longer under God, but yoked as it were to another and having fallen under the tyrannical hand; yet to those who still lived in the holy city, and had obtained the glory of the holy liturgy, they assign the worship, using, clearly, a right reasoning toward the examination of what is fitting and needed. And the most wise Daniel himself also, though he held to holy pursuits, and was a captive together with the others, outwitted the thing of necessity. And in what manner, I will say: for he prayed three times of the day. But the windows in the upper rooms were looking and opened toward Jerusalem for him. For it is written so. For he thought his own prayer would then barely be well-receivable with God, if, from a foreign and hated land, he could, if not perhaps in flesh, at least in thoughts be separated, and with the eyes of the mind, looking toward the land most dear to God, and as if having slipped into the temple itself, he might bring the petition for whatever he would choose.",
        "Palladius. Well indeed, in truth, the whole word has been fitted together for us.",
    ],
    [
        A("Psalm 137:2", "Quoted: on the willows in the midst of it we hung our instruments (LXX 136:2)."),
        A("Psalm 137:4", "Quoted: how shall we sing the Lord's song on a foreign land (LXX 136:4)."),
        A("Baruch 1:5-7", "Quoted: they wept and fasted and prayed; they gathered silver and sent it to Joakim the priest."),
        A("Baruch 1:10", "Quoted: buy whole burnt-offerings and for sin, and frankincense, and make manna."),
        A("Daniel 6:10", "Daniel prayed three times a day, windows opened toward Jerusalem."),
        A("1 Kings 8:48", "Pray toward the city and the house.", "possible"),
    ],
    [
        "Cyril cites Greek poets for the willow as fruit-destroying (olesikarpon); the epithet is Homeric (Odyssey 10.510), but he does not quote the line. No lacuna is marked; the verse is simply not given.",
        "Baruch 1:10 'make manna' follows the Greek of that book (manna as a cereal offering), not Exodus manna.",
    ],
)
