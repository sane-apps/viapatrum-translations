# -*- coding: utf-8 -*-
"""English of Origen, Homilies on Jeremiah, Homily 1 (Jer 1:2–10). From GCS III Greek."""

SECTIONS = []


def S(section, title, english, allusions, notes=None):
    SECTIONS.append(
        {
            "section": section,
            "homily": 1,
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
    "1.1",
    "God is ready to do good, and slow to punish",
    [
        "God is ready to do good, and slow to punish those who deserve punishment. He could bring the penalty on those he has condemned in silence, without first bearing witness against them. He never does that. Even when he condemns, he speaks, and he speaks so that the one about to be condemned may turn from the sentence.",
        "There are many examples of this in the Scriptures. A few that come up at once will be enough, so that we may reach the aim of the readings set before us.",
        "The Ninevites had become sinners, and they were condemned by God. Yet three days, and Nineveh was about to be overthrown. God did not wish to condemn the city in silence. He gave them room for repentance and turning, and sent a Hebrew prophet, so that when the prophet said, 'Yet three days, and Nineveh shall be overthrown,' those already condemned might not be condemned, but might repent and meet with the mercy of God.",
        "Those in Sodom and Gomorrah had been condemned, as is clear from God's words to Abraham. Even so the angels did their part, wanting to save those who did not want to be saved. They said to Lot, 'Have you anyone here, sons-in-law or sons or daughters?' They were not ignorant that those others would not follow Lot. They were doing the work of their own kindness, and of the kindness of the one who sent them.",
    ],
    [
        A("Jonah 3:4", "Narrative of the sentence, then Jonah's quoted word: yet three days and Nineveh shall be overthrown."),
        A("Wisdom 12:10", "Room for repentance.", "possible"),
        A("Genesis 18:20-21", "God's words to Abraham on Sodom.", "possible"),
        A("Genesis 19:12", "Quoted: have you anyone here, sons-in-law or sons or daughters."),
    ],
    [
        "μελλητής: slow, delaying — not unwilling.",
        "Klostermann: a Hebrew prophet (Jonah), not an unnamed prophet.",
    ],
)

S(
    "1.2",
    "Why the dates of Jeremiah's prophecy are written",
    [
        "You will find the same thing in what is written about Jeremiah. The time of his prophecy is recorded: when he began, and how far he prophesied. Then the reader, if he does not attend to the reading and examine the intent of the passages set down, will say: this is history, and it is written when Jeremiah began to prophesy, and after how long a time he stopped. What is this history to me?",
        "I read, and I learned that he began to prophesy 'in the days of Josiah son of Amos, king of Judah, in the thirteenth year of his reign.' Then 'it came to pass in the days of Jehoiakim son of Josiah, king of Judah,' and he prophesied 'until the end of the eleventh year of Zedekiah son of Josiah, king of Judah.' And I learned that his prophecy stretched through three kings, 'until the captivity of Jerusalem in the fifth month.' What then are we taught through these things, if we attend to the reading?",
    ],
    [
        A("Jeremiah 1:2", "Quoted: in the days of Josiah, thirteenth year."),
        A("Jeremiah 1:3", "Quoted: Jehoiakim; until the eleventh year of Zedekiah; captivity in the fifth month."),
    ],
)

S(
    "1.3",
    "God sent the prophet before the captivity, and even in it",
    [
        "God condemned Jerusalem for her sins, and they had been judged to be left to captivity. Even so the God who loves mankind, when the time had come, sends this prophet also, starting two reigns before the captivity, so that those who were willing, taking it in, might repent through the prophetic words. He sent a prophet to prophesy under the second king after the first, and under the third, up to the very times of the captivity.",
        "For the long-suffering God was giving a delay even, so to speak, one day before the captivity, urging those who heard to repent, so that the grim things of the captivity might cease. That is why it is written that Jeremiah prophesied 'until the captivity of Jerusalem, until the fifth month.' He had begun, and he was still prophesying, as if to say: you have become captives; even so, repent. If you repent, the captivity will not go on, but the mercy of God will stand over you.",
        "So we have something useful from the record that gives the times of the prophecy: that God, according to his own love of mankind, urges those who hear not to suffer the things of the captivity. It is like this with us too. If we sin, we also are about to become captives. For 'to hand such a one over to Satan' differs in nothing from handing those from Jerusalem over to Nebuchadnezzar. As they were handed over to him because of sins, so we are handed over to Satan because of sins — Satan who is a Nebuchadnezzar. And 'those I handed over to Satan, that they may be taught not to blaspheme,' the apostle says of other sinners.",
    ],
    [
        A("Jeremiah 1:3", "Quoted: until the captivity of Jerusalem, until the fifth month."),
        A("1 Corinthians 5:5", "Quoted sense: hand such a one over to Satan."),
        A("1 Timothy 1:20", "Quoted: those I handed over to Satan, that they may be taught not to blaspheme."),
    ],
)

S(
    "1.4",
    "Sin hands the soul to a spiritual Babylon",
    [
        "See then how great an evil it is to sin, so that people are handed over to Satan, who takes captive the souls of those left by God. God does not leave without cause, and not without judgment, those he has left. For when he sends the rain on the vineyard, and the vineyard bears thorns instead of grapes, what will God do but 'command the clouds not to rain' on the vineyard?",
        "Because of our sins a captivity hangs over us too, and we are about to be handed over, if we do not repent, to Nebuchadnezzar and the Babylonians, so that the spiritual Babylonians may tear us. With these things hanging over us, the words of the prophets, the words of the Law, the words of the apostles, the words of our Lord and Savior Jesus Christ, speak to us about repentance and call us to a turning. If we hear, let us believe the one who said, 'I also will repent of all the evils which I spoke of doing to them.' So much for the preface.",
    ],
    [
        A("Isaiah 5:6", "Quoted: command the clouds not to rain on the vineyard."),
        A("Jeremiah 18:8", "Quoted: I will repent of the evils I spoke of doing to them."),
        A("Jeremiah 26:3", "Same repent-of-evil formula.", "possible"),
    ],
)

S(
    "1.5",
    "Before I formed you in the womb I knew you",
    [
        "After the preface it is written that 'the word of the Lord came to him' — clearly, to Jeremiah. And what does the word of the Lord say to him? Something set apart from what was said to the other prophets. For we have found this said to none of the prophets.",
        "Abraham was called a prophet in the word, 'He is a prophet, and he will pray for you,' and God did not say to him, 'Before I formed you in the womb I know you, and before you came out of the womb I have sanctified you.' Abraham was sanctified later, when he went out from his land and from his kindred and from his father's house. Isaac was born of promise, and we have not found this word said even to him. Why should I go through the rest? Jeremiah received a gift set apart: 'Before I formed you in the womb I know you, and before you came out of the womb I have sanctified you.'",
    ],
    [
        A("Jeremiah 1:4", "The word of the Lord came to him."),
        A("Jeremiah 1:5", "Quoted twice: before I formed you; I have sanctified you."),
        A("Genesis 20:7", "Quoted of Abraham: he is a prophet and will pray for you."),
        A("Genesis 12:1", "Abraham left his land, kindred, and father's house."),
        A("Galatians 4:23", "Isaac born of promise.", "possible"),
    ],
    ["Klostermann prints Ἰσαάκ: Isaac was born of promise; the word 'I know you from the womb' is not said to him either."],
)

S(
    "1.6",
    "Some refer the words to the Savior; the whole sequence must be kept",
    [
        "We are not unaware that some refer these words, as greater than Jeremiah, to our Savior and Lord. And one must know that much of it agrees with him and can be referred to the Savior — I will set that out. But a few of the things said to Jeremiah press the argument, and cannot, as most people take them, be fitted to the Savior.",
        "What then fits the Savior? 'To all to whom I send you, you shall go, and according to all that I command you, you shall speak. Do not be afraid of their face, because I am with you to deliver you, says the Lord.' These would not yet clearly seem to be referred to the Savior. But what follows puts the reading about Jeremiah in a tight place: 'And the Lord stretched out his hand toward me and touched my mouth, and the Lord said to me, Behold, I have given my words into your mouth. Behold, I have set you today over nations and kingdoms, to uproot and to pull down.' What nations did Jeremiah uproot? What kingdoms did he overthrow? For it is written, 'Behold, I have set you today over nations and kingdoms, to uproot and to pull down.' And what authority did Jeremiah have 'to destroy'? And whom did he build in such numbers that it should be said 'and to build'? Jeremiah says, 'I have not profited, and no one has profited me.' How then is 'to build and to plant' given to him? How will 'to plant' fit Jeremiah?",
        "These things, referred to the Savior, do not press the interpreter, because in them Jeremiah is a symbol of the Savior. But what I am about to set down presses even the most intelligent person who wants to show how these too can fit the Savior: 'And I said, You who are, Master, Lord, behold, I do not know how to speak.' He who is Wisdom, he who is the Power of God, who brought us 'the fullness of the deity, which dwelt in him bodily' — how then can 'I do not know how to speak' fit the Savior? And 'I am younger' is forbidden to the Savior, as if he were saying it wrongly. For if the Lord says to him, Do not say this, it is clear that he forbids what is not well said. So these do not fit the Savior. Those other words do not seem to put the Savior to shame.",
        "To say that these belong to Jeremiah and those to the Savior is not hard. But a fair-minded person will be much pressed here. To cut a connected run of words, and to say, 'These, being lesser, fit Jeremiah and not Christ, and these, being greater than Jeremiah, fit Christ and not Jeremiah' — that is the work of people without judgment. Let the whole, then, be referred to Jeremiah, and let even the things that seem greater than Jeremiah be interpreted.",
    ],
    [
        A("Jeremiah 1:7-8", "Quoted: to all I send you; do not be afraid; I am with you to deliver you."),
        A("Jeremiah 1:9-10", "Quoted: stretched out his hand; words in the mouth; over nations to uproot and pull down."),
        A("Jeremiah 15:10", "Jeremiah: I have not profited, nor has anyone profited me.", "possible"),
        A("Jeremiah 1:6", "Quoted: I do not know how to speak."),
        A("Colossians 2:9", "Quoted: the fullness of the deity dwelt bodily."),
        A("1 Corinthians 1:24", "Christ the power of God and the wisdom of God.", "possible"),
    ],
)

S(
    "1.7",
    "Nations and kingdoms in the soul; the child who chooses the good",
    [
        "Everyone who has received words from God and has the grace of the heavenly words has received them in order 'to uproot nations and kingdoms and to pull them down.' But if it is said that everyone who has received words from God 'uproots nations and kingdoms,' do not take the nations and the kingdoms for me in a bodily way. Look at human souls, ruled by sin, as the apostle said: 'Do not let sin reign in our mortal body.' And seeing the many kinds of sins, take the nations and the kingdoms as a figure: the bad things in the souls of men, which are uprooted and pulled down by the words of God given either to Jeremiah or to anyone at all.",
        "The first things, which press us as regards the Savior, can also fit Jeremiah; and the second things can fit Jeremiah for the one who knows how to read them as a figure. Someone among the hearers will say to me: Work the other reading too, and try to show that all that is written fits the Savior. Do not be anxious about the second things. It is clear that the Savior uprooted the kingdoms of the devil and pulled down the nations, taking away the life of the nations. Here, at what seems ill-sounding as regards the Savior, work the word somehow: how can the Savior say, 'I do not know how to speak, because I am younger,' and the rest? You see that the argument is in a tight place.",
        "We know the Savior is Lord. We are seeking, according to the dignity of the Word and according to the truth, to refer these things to the Savior. Witnesses must be taken from the Scriptures. For our guesses, if they have no witness, and our interpretations, are not to be trusted. And 'every word shall be established at the mouth of two or three witnesses' fits interpretations more than it fits men, so that I may establish the words of the interpretation by taking two witnesses from the New and the Old Covenant, taking three from gospel, from prophet, from apostle. For so every word will stand.",
        "How then can we refer these things to the Savior? Bring the Old Covenant as a witness: 'Before the child knows good or evil, he refuses evil to choose the good.' And these things are said outright about the Savior in Isaiah: 'Behold, the virgin shall conceive in the womb and bear a son, and they shall call his name Emmanuel.' And there it is added: 'before the child knows.' And if an example must also be taken from the gospel: Jesus, not yet become a man but still a child, since 'he emptied himself,' was advancing. For no one who is already perfected advances; he advances who still needs advance. So he 'advanced in stature, advanced in wisdom, advanced in grace with God and men.' If he emptied himself coming down here, and emptying himself was taking again from what he had emptied himself of, having emptied himself willingly, what is strange if he also advanced 'in wisdom and stature and grace with God and men,' and if what I set down from Isaiah is true of him: before he knows good or evil he will choose the good and refuse evil?",
    ],
    [
        A("Jeremiah 1:10", "Uproot nations and kingdoms."),
        A("Romans 6:12", "Quoted: do not let sin reign in our mortal body."),
        A("Jeremiah 1:6", "Quoted: I do not know how to speak, because I am younger."),
        A("Deuteronomy 19:15", "Every word established at two or three witnesses."),
        A("Matthew 18:16", "Same two-or-three-witness rule in the gospel.", "possible"),
        A("Isaiah 7:15-16", "Quoted: before the child knows good or evil he refuses evil."),
        A("Isaiah 7:14", "Quoted: the virgin shall conceive; Emmanuel."),
        A("Philippians 2:7", "Quoted: he emptied himself."),
        A("Luke 2:52", "Quoted: advanced in wisdom and stature and grace with God and men."),
        A("Luke 2:40", "The child grew and became strong, filled with wisdom.", "possible"),
    ],
)

S(
    "1.8",
    "Not knowing how to speak is greater than human speech",
    [
        "But someone will say: Even if you can refer 'he does not know' to the Savior, does it not offend you to say these things about the Only-begotten, about the firstborn of all creation, about the one announced before the conception according to the word, 'The Holy Spirit will come upon you, and the power of the Most High will overshadow you'? And you say he does not know how to speak?",
        "See whether you can see something worth saying, and great, about the Savior in this place: that not knowing certain things, he is greater in not knowing them than in knowing them. And I use his own voice as a witness that he does not know certain things. He says to those who tell him, 'Did we not eat in your name, and drink in your name, and cast out demons in your name, and do many mighty works?' 'Depart from me; I never knew you.' Does that 'I never knew you' present his power as lesser, or as greater and more wonderful, because he did not know the worse and those who are perishing? For he knew the things that matter, the better things, and 'the Lord knew those who are his,' and 'if anyone is ignorant, he is not known.' So the sinner is not known by God.",
        "Someone among the hearers will say to me: You have shown that he does not know the sinners; you have shown that he does not know those who work lawlessness, for they are not worthy of his knowledge. How will you show that it is a great and glorious thing for the Savior to say, 'I do not know how to speak'? Speaking is a human thing. To speak is to use a dialect: the speech of the Hebrews, say, or of the Greeks, or of some others. If you go up to the Savior and see him as Word 'in the beginning with God,' you will see that he does not know how to speak, because speaking is human. He does not know it, because what he knows is greater than speaking. And if you compare the tongues of angels with the tongues of men, and see that he is greater even than angels, as the apostle bore witness in the letter to the Hebrews, you will say that he was greater even than the tongue of angels when he was God, the Word with the Father.",
        "So he learns, and as it were takes on, a knowledge not of great things but of lesser and smaller ones. Just as I force myself to lisp when I talk with little children (for not knowing how to speak in baby-talk, being full-grown I force myself to talk with children), in the same way the Savior, being 'in the Father' and in the greatness of the glory of God, does not speak human things and does not know how to utter speech to those below. But when he comes into a human body he says at the beginning, 'I do not know how to speak, because I am younger.' Younger because of the bodily birth; older according to 'firstborn of all creation'; younger because he came at the completion of the ages and visited this life later. So he says, 'I do not know how to speak': I know things greater than speaking, I know things greater than this human sound. You want me to speak to men? I have not yet taken up a human dialect. I have your dialect, O God. I am your Word, O God. I know how to speak with you. I do not know how to speak to men. I am younger.",
    ],
    [
        A("Colossians 1:15", "Firstborn of all creation."),
        A("Luke 1:35", "Quoted: the Holy Spirit will come upon you; power of the Most High."),
        A("Matthew 7:22-23", "Quoted: did we not eat and drink and cast out demons in your name; I never knew you."),
        A("Luke 13:26-27", "Ate and drank in your name; I do not know you.", "possible"),
        A("2 Timothy 2:19", "Quoted: the Lord knew those who are his."),
        A("1 Corinthians 14:38", "Quoted: if anyone is ignorant, he is not known."),
        A("John 1:1", "Quoted: the Word in the beginning with God."),
        A("Hebrews 1:4", "Greater than the angels."),
        A("John 14:10-11", "Being in the Father.", "possible"),
        A("Jeremiah 1:6", "Quoted: I do not know how to speak, because I am younger."),
        A("Colossians 1:15", "Quoted: firstborn of all creation."),
        A("Hebrews 9:26", "At the completion of the ages.", "possible"),
    ],
)

S(
    "1.9",
    "Do not say, I am younger",
    [
        "'Do not say, I am younger, because to all to whom I send you, you shall go.' So he stretches out the hand, touches his mouth, and gives him words, and gives him words because of the kingdoms, that he may uproot. When he was 'in the Father' he had no need of words that uproot. He had no words that pull down and take apart the worse things. For nothing there was worthy of being pulled down, nothing worthy of being uprooted.",
        "It is a great thing, as 'I do not know you, because you are workers of lawlessness' is a great thing, said by the Savior because of the surpassing greatness of his glory. Equal in force to 'I do not know how to speak human things' is this 'I do not know how to speak.'",
    ],
    [
        A("Jeremiah 1:7", "Quoted: do not say I am younger; to all I send you, you shall go."),
        A("Matthew 7:23", "Quoted sense: I do not know you, workers of lawlessness."),
        A("John 14:10", "In the Father.", "possible"),
    ],
)

S(
    "1.10",
    "Formed in the womb, not made: God knows those who are his",
    [
        "Whether it is said to Jeremiah or to the Savior, 'Before I formed you in the womb I know you': if you read Genesis and watch what is said about the making of the world, you will find that the Scripture, with a very fine distinction, did not say, 'Before I made you in the womb I know you.' For when the one according to the image was being created, 'God said, Let us make man according to our image and likeness.' He did not say, Let us form. But when he took 'dust from the earth,' he did not make the man; he 'formed the man,' and 'placed in the garden the man whom he had formed, to work it and to keep it.'",
        "If you can, see the difference between making and forming. The Lord, whether to Jeremiah or to the Savior, did not say, 'Before I made you in the womb I know you.' For what is made does not come about in the womb; what is formed from the dust of the earth is created in the womb. 'Before I formed you in the womb I know you.' If the Lord knew all, he would not have said to Jeremiah as something set apart, 'I know you.' So God knows those who matter, God knows those worthy of his knowledge, and 'the Lord knew those who are his.' Those unworthy God does not know, as the Savior also does not: 'I never knew you.'",
        "We, being men, as we advance, judge some things worthy of our knowing them. Some things we do not even want to hear, so that we may not know them. Some things we want to know. What of the God of all? Does he want to know Pharaoh? Does he want to know the Egyptians? They are not worthy of the knowledge of God. Moses is worthy, and each of the prophets of that rank. You must set many things right before God begins to know you. Jeremiah he knew before forming him in the womb. Another he begins to know at thirty years of age, another at forty. There are secret words here, not in question as regards the Savior, but as regards Jeremiah needing attention from those who have ears.",
    ],
    [
        A("Jeremiah 1:5", "Quoted: before I formed you in the womb I know you."),
        A("Genesis 1:26", "Quoted: let us make man according to our image and likeness."),
        A("Genesis 2:7", "Quoted: formed the man from dust of the earth."),
        A("Genesis 2:15", "Placed in the garden the man he had formed, to work and keep it."),
        A("2 Timothy 2:19", "Quoted: the Lord knew those who are his."),
        A("Matthew 7:23", "Quoted: I never knew you."),
    ],
    ["Klostermann: what is made does not come about in the womb; what is formed from dust is created in the womb. ποιέω vs πλάσσω kept as make vs form."],
)

S(
    "1.11",
    "Sanctified before coming out of the womb",
    [
        "How does he say, 'Before I formed you in the womb I know you, and before you came out of the womb I have sanctified you'? God sanctifies some for himself. He did not wait for this one to come into birth in order to sanctify him; he had already sanctified him before he came out of the womb. If you refer it to the Savior, it is not hard to say that he has been sanctified before coming out of the womb. If you refer it to the Savior, he has been sanctified not only before coming out, but still earlier. This Jeremiah was sanctified before coming out of the womb.",
    ],
    [
        A("Jeremiah 1:5", "Quoted: before I formed you; before you came out I have sanctified you."),
    ],
    ["ἡγίακά σε: I have sanctified you. Present knowledge, past sanctifying."],
)

S(
    "1.12",
    "A prophet to the nations",
    [
        "'I have set you as a prophet to the nations.' If you look for this in Jeremiah — 'I have set you as a prophet to the nations' — watch later on: he is commanded to prophesy 'against all the nations,' and there is a heading, 'What Jeremiah prophesied against all the nations,' against Elam, against Damascus, against Moab. And we have it that he 'prophesied against all the nations,' as regards the letter of 'I have set you as a prophet to the nations,' said to him.",
        "If it is a matter of the higher sense: if of Jeremiah, we have already spoken; if of the Savior, what need is there even to say it? He truly prophesied to all the nations. For he is, as he is ten thousand other things, also a prophet. As he is high priest, as he is savior, as he is physician, so he is also prophet. Moses, prophesying about him, did not say only 'a prophet,' but said it with a special force: 'The Lord your God will raise up for you a prophet from your brothers, like me; him you shall hear, and it shall be that whoever does not hear that prophet shall be destroyed from his people.'",
        "This one, then, is also the prophet set 'to the nations,' and he received grace from God poured out on his lips, so that not only when he was present in the body, but also now, when he is present in power and in the Spirit, he may prophesy 'to all the nations,' so that from all the nations his prophecy may reach its end and draw men to salvation.",
    ],
    [
        A("Jeremiah 1:5", "Quoted: I have set you as a prophet to the nations."),
        A("Jeremiah 25:13", "What Jeremiah prophesied against all the nations.", "possible"),
        A("Jeremiah 49:34", "Against Elam.", "possible"),
        A("Jeremiah 49:23", "Against Damascus.", "possible"),
        A("Jeremiah 48:1", "Against Moab.", "possible"),
        A("Deuteronomy 18:15", "Quoted: a prophet from your brothers, like me."),
        A("Deuteronomy 18:19", "Whoever will not hear that prophet."),
        A("Acts 3:22-23", "Peter cites the same Deuteronomy prophet-like-Moses word.", "possible"),
        A("Psalm 45:2", "Grace poured out on his lips.", "possible"),
    ],
)

S(
    "1.13",
    "A child in body, a grown man within; do not fear their face",
    [
        "'And I said, You who are, Master, Lord, behold, I do not know how to speak, because I am younger. And the Lord said to me, Do not say that I am younger, because to all to whom I send you...' We have often said that it is possible, according to the inner man, to be a child, even if someone is in an old age of body. And it is possible at times, according to the outer man, to be a child, and according to the inner, a man. Such was Jeremiah, already having the grace from God while he was still in the age of a child according to the body. That is why the Lord says to him, 'Do not say that I am younger.' And a sign that he is not younger, but 'a grown man,' is this: 'To all to whom I send you, you shall go, and according to all that I command you, you shall speak. Do not be afraid of their face.'",
        "The Word of God knows that those who serve as ambassadors of the word are in danger among the hearers. For when they are exposed they hate them; when they are rebuked they persecute them. The prophets suffer every kind of thing. 'A prophet is not without honor except in his own country and in his house' — which we also recalled earlier. So God, sending the prophet, knows how many dangers he will take on, and he says to him, 'Do not be afraid of their face, because I am with you to deliver you, says the Lord.'",
        "What Jeremiah suffered is written down. He was thrown into a pit of mire; he remained there eating one loaf a day and drinking water only; and ten thousand other things which his prophecy has made clear. 'Which of the prophets did your fathers not persecute?' it is said to the Jews. And it is necessary that 'those who want to live in a godly way in Christ Jesus be persecuted in every case by opposing powers, through the vessels they find.' Therefore those who are persecuted must not be surprised, but must do everything, only praying that they be persecuted unjustly and not justly — not for injustice, not for sin, not for greed. And if someone is ever persecuted for righteousness, let him also hear, 'Blessed are you when they reproach you and persecute you and say every evil word against you, lying, for my sake. Rejoice and be glad, because your reward is great in the heavens; for so they persecuted the prophets who were before you.'",
    ],
    [
        A("Jeremiah 1:6-8", "Quoted: I do not know how to speak; do not say I am younger; do not fear their face."),
        A("Ephesians 4:13", "A grown man / mature man.", "possible"),
        A("2 Corinthians 4:16", "Inner man and outer man.", "possible"),
        A("Matthew 13:57", "Quoted: a prophet is not without honor except in his own country and house."),
        A("Jeremiah 38:6-9", "Thrown into the pit of mire."),
        A("Jeremiah 37:21", "One loaf a day."),
        A("Acts 7:52", "Quoted: which of the prophets did your fathers not persecute."),
        A("2 Timothy 3:12", "Quoted: those who want to live in a godly way in Christ Jesus will be persecuted."),
        A("Matthew 5:10-12", "Quoted: blessed when they persecute you; so they persecuted the prophets."),
    ],
)

S(
    "1.14",
    "The Lord's own hand, not Isaiah's coal; kingdoms of the vices",
    [
        "'Because I am with you to deliver you, says the Lord. And the Lord stretched out his hand toward me, and touched my mouth, and the Lord said to me.' Watch the difference between Jeremiah and Isaiah. Isaiah says, 'I have unclean lips, and I dwell in the midst of a people having unclean lips, and I have seen the King, the Lord of hosts, with my eyes.' And since he confessed that he did not have unclean works, but only small words (for to that point he was a sinner), the Lord did not stretch out his hand. One of the seraphim touched his lips with his hand, and said, 'Behold, I have taken away your iniquities.' But because this one was sanctified 'from the womb,' no tongs are sent to him, and no coal 'from the altar' (he had nothing worthy of the fire). The Lord's own hand touched him. That is why he says, 'The Lord stretched out his hand toward me and touched my mouth, and the Lord said to me, Behold, I have given my words into your mouth. Behold, I have set you today over nations and kingdoms, to uproot.'",
        "Who is so blessed as to uproot, by the words given by God, the many kingdoms which 'the devil shows,' kingdoms of opposing powers, kingdoms according to the sins? For it is written, 'Behold, I have given my words into your mouth. Behold, I have set you today over nations and kingdoms, to uproot.' And as there are kingdoms, so there are nations. A kingdom cannot even be called a kingdom unless it has nations under it. For example: there is a kingdom of fornication, and the nations of fornication are each several fornication. There is one kingdom, the general sin of greed and of robbery, and there are many kingdoms in those who have many kinds of sins. Then, in each of the sinners, think of the nations under the kingdom: this man has many nations of the kingdom according to fornication, that man has many nations of the kingdom according to robbery, according to slander, according to anger.",
        "It is the work of the words of God, sent out over 'nations and kingdoms,' 'to uproot and to pull down.' To uproot what? The Savior taught, saying, 'Every plant which my heavenly Father did not plant will be uprooted.' There are some things inside in the souls which 'the heavenly Father did not plant.' For all 'the evil reasonings, murders, adulteries, fornications, thefts, false witnesses, blasphemies' are plants planted not by the heavenly Father. And if you want to see whose plants such reasonings are, hear that 'an enemy man did this,' the one who sowed 'the tares in the midst of the wheat.' So God stands by, having the seeds, and the devil. If we give 'place to the devil,' 'the enemy' sows a plant 'which the Father did not plant,' which will certainly be uprooted. If we do not give 'place to the devil,' but give place to God, God rejoices and sows his seeds on our governing mind.",
        "Do not think, then, that Jeremiah received some grim gift from God, because he is set 'over nations and over kingdoms, to uproot.' God is good, uprooting through the words the bad things, the kingdoms hostile to the kingdom of the heavens, the warring nations against the nation of God. 'To uproot and to pull down.'",
    ],
    [
        A("Jeremiah 1:8-10", "Quoted: I am with you; stretched out his hand; words in the mouth; over nations to uproot."),
        A("Isaiah 6:5", "Quoted: unclean lips; I have seen the King, the Lord of hosts."),
        A("Isaiah 6:6-7", "A seraph touched his lips; I have taken away your iniquities."),
        A("Jeremiah 1:5", "Sanctified from the womb."),
        A("Matthew 4:8", "The devil shows the kingdoms.", "possible"),
        A("Luke 4:5", "The devil shows the kingdoms of the world.", "possible"),
        A("Matthew 15:13", "Quoted: every plant my heavenly Father did not plant will be uprooted."),
        A("Matthew 15:19", "Quoted: evil reasonings, murders, adulteries, fornications, thefts, false witness, blasphemies."),
        A("Matthew 13:28", "Quoted: an enemy man did this."),
        A("Matthew 13:25", "Quoted: sowed tares in the midst of the wheat."),
        A("Ephesians 4:27", "Quoted: do not give place to the devil."),
    ],
)

S(
    "1.15",
    "What is pulled down must also be destroyed",
    [
        "There is a building of the devil, and there is a building of God. The building 'on the sand' is the devil's, for it stands on nothing firm and sure and united. The building 'on the rock' is God's. See what is said to those of God: 'You are God's field, God's building.' So the words of God are over 'nations and kingdoms, to uproot and to pull down and to destroy.' If something is uprooted, and what was uprooted is not destroyed, it is still there. If something is pulled down, and the stones of the demolition are not destroyed, it is still there.",
        "It is a work of the goodness of God, after the uprooting, to destroy what has been uprooted, and after the taking-down, to destroy what has been taken down. Read carefully how such things are destroyed: 'Burn the chaff with unquenchable fire,' and 'Bind the tares in bundles and hand them over to fire.' So after being uprooted they are destroyed. And if you want to see also the things destroyed after demolition, of the building of poor stuff: that house which was taken down because of leprosy becomes dust, and being dust it is thrown 'outside the city,' so that not even a stone remains, like 'I will grind them as the mud of the streets.' For the worse things must in no way still stand. Something has been pulled down: let the stones not be useful for another building which the evil one can build. Something has been uprooted: let him not again find seeds from the uprooted things, so as to sow the tares once more. For having the seeds of the tares he certainly sowed them. That is why 'bind the tares and burn them with fire,' so that after being uprooted they may be destroyed, and after being pulled down the devil's building may be destroyed.",
    ],
    [
        A("Matthew 7:24-27", "House on rock and house on sand."),
        A("1 Corinthians 3:9", "Quoted: you are God's field, God's building."),
        A("Jeremiah 1:10", "Uproot, pull down, destroy."),
        A("Matthew 3:12", "Chaff burned with unquenchable fire."),
        A("Luke 3:17", "Same chaff and unquenchable fire.", "possible"),
        A("Matthew 13:30", "Quoted: bind the tares in bundles and hand them to fire."),
        A("Leviticus 14:40-45", "Leprous house taken down; dust thrown outside the city."),
        A("Psalm 18:42", "Quoted: I will grind them as the mud of the streets."),
    ],
)

S(
    "1.16",
    "Then build and plant; I will kill and I will make alive",
    [
        "But the words of God do not stop at 'to uproot and to pull down and to destroy.' Suppose the bad things have been uprooted from me, the worse things pulled down: what good is it to me if, in place of what was uprooted, the better things are not planted? What good is it to me if, in place of these, the things that matter are not built up? That is why the words of God first, of necessity, do the 'uproot and pull down and destroy,' and after that the 'build and plant.' And we have always watched in Scripture that the things which look grim, if I may call them so, are named first, then the things that seem cheerful are said second. 'I will kill and I will make alive.' He did not say, 'I will make alive,' and after that, 'I will kill.' For it is impossible that what God has made alive should be taken away by him or by anyone else. But 'I will kill and I will make alive.' Whom will I kill? Paul the betrayer, Paul the persecutor. 'And I will make alive,' so that he may become 'Paul, an apostle of Jesus Christ.'",
        "If the wretched people from the heresies had understood these things, they would not keep putting them forward to us, saying, Do you see how fierce and inhuman the God of the Law is, when he says, 'I will kill, and I will make alive'? Do you not see in the Scriptures a promise of the resurrection of the dead? Or do you not see the resurrection of the dead already making its beginning in each person? 'We were buried' with Christ 'through baptism' and we were raised with him.",
        "So he begins from the grimmer voices, which are necessary — as 'I will kill' — then, having killed, 'and I will make alive. I will strike, and I will heal.' 'For whom the Lord loves he disciplines, and he scourges every son whom he receives.' First he strikes, and after that he heals. 'For he makes one feel pain and again restores.' So also here: 'I have set you today over nations and kingdoms, to uproot and to pull down and to destroy and to build and to plant.' Only, first those bad things must be taken from us. God cannot build on the place of the bad building. 'For what partnership has righteousness with lawlessness? What fellowship has light with darkness?' Vice must be uprooted from the foundations. The building of vice must be consumed from our soul, so that after these things the words of God may build and plant.",
        "I cannot understand what is written in any other way: 'Behold, I have given my words into your mouth.' What do the words do? 'To uproot and to pull down and to destroy.' Words uproot 'nations'; words pull down kingdoms — not these worldly ones. Think, in a way worthy of words that pull down, worthy of words that uproot, the things uprooted by words, the things pulled down by words. Is there not, in what is being said right now, a power — if God gives it (according to 'the Lord will give a word to those who preach good news with great power') — a power that uproots, if there is any unbelief, any hypocrisy, any vice, any incontinence? Is there not a power that pulls down, if somewhere an idol-shrine has been built in the heart, so that when that is pulled down a temple of God may be built, and the glory of God may be found in the temple built up, and there may be not a grove but a planting, a garden of God, where the temple of God is, in Christ Jesus, to whom is the glory and the power to the ages of the ages. Amen.",
    ],
    [
        A("Jeremiah 1:10", "Quoted throughout: uproot, pull down, destroy, build, plant."),
        A("Deuteronomy 32:39", "Quoted: I will kill and I will make alive."),
        A("1 Timothy 1:13", "Paul the persecutor.", "possible"),
        A("1 Corinthians 1:1", "Paul an apostle of Jesus Christ.", "possible"),
        A("Romans 6:4", "Quoted: we were buried with him through baptism."),
        A("Colossians 2:12", "Buried and raised with him in baptism.", "possible"),
        A("Deuteronomy 32:39", "I will strike and I will heal — same song.", "possible"),
        A("Hosea 6:1", "He has torn, and he will heal.", "possible"),
        A("Hebrews 12:6", "Quoted: whom the Lord loves he disciplines; he scourges every son he receives."),
        A("Job 5:18", "Quoted sense: he makes one feel pain and again restores."),
        A("2 Corinthians 6:14", "Quoted: what partnership has righteousness with lawlessness; light with darkness."),
        A("Jeremiah 1:9", "Quoted: I have given my words into your mouth."),
        A("Psalm 68:11", "Quoted: the Lord will give a word to those who preach good news with great power."),
        A("1 Corinthians 3:16", "Temple of God.", "possible"),
        A("2 Corinthians 6:16", "We are the temple of the living God.", "possible"),
    ],
    [
        "προδότην: Klostermann prints 'betrayer' of Paul, then 'persecutor.' Kept; not softened to 'persecutor' only.",
    ],
)
