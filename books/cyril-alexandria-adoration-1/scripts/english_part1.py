# -*- coding: utf-8 -*-
"""English of De adoratione Book 1, sections 1–13 (PG 68.134–157). From locked Greek."""

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
    "The tablet of Matthew and John",
    [
        "Book 1. On man's turning aside into worthlessness, and his captivity into sin, and together on the calling and the return that come by a change of mind, and the climb back toward what is better.",
        "Cyril said: To ask where you are going, and from where you have come, is superfluous, I think. You would say at once, I am quite sure, that you have come from home and to us.",
        "Palladius said: True.",
        "Cyril said: And this tablet here in your hands — what is it?",
        "Palladius. A gospel book, the writing of Matthew and of John.",
        "Cyril. And do you think it ought to be carried about anywhere, and to anyone? You would hardly go practicing it in the streets, Palladius. The labor spent on this is sweeter at home and in study.",
        "Palladius. You speak well. I have come to confer with you. And I bring the holy tablet; for after toiling over a vast amount I still cannot see what our Lord Jesus Christ means when he says, in Matthew, 'Do not think that I came to destroy the Law or the prophets. I did not come to destroy, but to fulfill. For amen I say to you, until heaven and earth pass away, one iota or one stroke'",
    ],
    [
        A("Matthew 5:17-18", "Palladius quotes the opening of the fulfill-not-destroy saying."),
    ],
)

S(
    2,
    "Fulfill the Law; worship in spirit and truth",
    [
        "'shall by no means pass from the Law until all things come to be.' And in the writing according to John, to the woman from Samaria: 'Believe me, woman, that an hour is coming when you will worship the Father neither on this mountain nor in Jerusalem. You worship what you do not know; we worship what we know, because salvation is from the Jews. But an hour is coming, and now is, when the true worshipers will worship the Father in spirit and truth. For the Father also seeks such to worship him. God is spirit, and those who worship him must worship in spirit and in truth.'",
        "Cyril. Then what in these things seems to you the steep place? What is the deep and hard to reach? Tell me, since I ask.",
        "Palladius. A holy word commands us to leave the more ancient customs and to put an end to the righteousness that is in the Law. And Paul said to those who still desired that righteousness even after the faith: 'You have been severed from Christ, you who are being justified in the Law; you have fallen away from grace. For we by the Spirit, from faith, wait for the hope of righteousness.' And of the way of life according to the Law, though he could show on himself bright and great boasts, he says again: 'Whatever was gain to me, these I have counted loss because of Christ. Indeed I count all things loss because of the surpassing knowledge of our Lord Jesus Christ, for whom I suffered the loss of all things, and count them refuse, that I may gain Christ and be found in him, not having my own righteousness, the one from the Law, but the one from faith in Christ, the righteousness from God.' He also affirmed plainly that the ancient commandment was not without fault. That is why, he says, the new one through Christ — that is, the gospel one — has been brought in for us usefully in its place. He writes thus: 'For there is a setting-aside of the foregoing commandment because of its weakness and uselessness. For the Law perfected nothing, but the bringing in of a better hope, through which we draw near to God.' And again: 'For if that first one had been faultless, no place would have been sought for a second.' For finding fault with them he says: 'Behold, days are coming, says the Lord, and I will complete upon the house of Israel and upon the house of Judah a new covenant, not according to the covenant which I made with their fathers on the day when I took them by the hand to lead them out of the land of Egypt, because they did not remain in my covenant, and I neglected them, says the Lord. Because this is the covenant which I will covenant with the house of Israel after those days, says the Lord, giving my laws into their mind, and on their heart I will write them.' And understanding and interpreting the name of newness with special care: 'In saying \"new,\"' he says, 'he has made the first old; and what is growing old and aging is near disappearance.' If then the Law perfected nothing, and there has been a setting-aside of the ancient commandment and the bringing in of the second, which knits us to",
    ],
    [
        A("Matthew 5:18", "Continuation of the iota-and-stroke saying across the column cut."),
        A("John 4:21-24", "Quoted in full to the Samaritan woman: worship in spirit and truth."),
        A("Galatians 5:4-5", "Quoted: severed from Christ; fallen from grace; hope of righteousness."),
        A("Philippians 3:7-9", "Quoted: gains as loss; refuse; righteousness from faith, not from Law."),
        A("Hebrews 7:18-19", "Quoted: setting-aside of the foregoing commandment; Law perfected nothing."),
        A("Hebrews 8:7", "Quoted: if the first had been faultless."),
        A("Hebrews 8:8-10", "Quoted from Jeremiah via Hebrews: new covenant written on the heart."),
        A("Jeremiah 31:31-33", "The new-covenant oracle under the Hebrews citation (LXX 38:31-33).", "possible"),
        A("Hebrews 8:13", "Quoted: in saying new he has made the first old."),
    ],
)

S(
    3,
    "The Law is type and shadow",
    [
        "Palladius. God, what then does the Savior mean, 'I did not come to destroy the Law, but to fulfill'? And that 'it is fitting that we worship God and Father in spirit and truth'? For this, I think, shows that we must cease from the habits and the worship that are according to the Law.",
        "Cyril. How you have gone out into a wide sea of questions! For what mind would be enough to look brightly into theorems so fine as to show us the new Scripture as sister and neighbor to what was of old decreed through all-wise Moses, going through the same things, and the life in Christ not far removed from the legal way of life, if the things marked out for the ancients are led to a spiritual contemplation? For the Law is type and shadow, and the shaping of piety is still as if in birth-pangs, and has the beauty of the truth hidden in itself. Or will you say it is not as I have said?",
        "Palladius. Very much so. But what would the clarification of this be? Or what is the manner of living according to the Gospel and yet seeming still to cling to the ancient commandment, and thinking to fulfill the things through Moses?",
        "Cyril. The account is not simple, as one might guess. Virtue is, I think, a thing both many-branched and many-formed; and the boasts of the life in Christ are varied for us through a very great deal of well-doing. And so divine David, in the forty-fourth psalm, sets beside Christ a pure virgin, the Church, as in the rank of a queen, and puts on her a gold-inwoven and embroidered robe, saying thus: 'The queen stood at your right hand, in gold-shot clothing, wrapped about and embroidered.' The gold-shot, as I judge, marks well what is honorable and conspicuous, and the embroidered, the many kinds of virtue. For the Church is exceedingly fair, having the intelligible adornment, not seen with the eyes of the flesh, but into the mind within and the heart — the Jew understood in secret — showing him, with a fine grace, well-formed and choice through a very great many beauties. For as the blessed Paul writes: 'For he is not a Jew who is one in the open, nor is circumcision that which is in the open in the flesh, but he who is a Jew in secret, and circumcision of heart, in spirit not in letter, whose praise is not from men but from God.'",
        "Palladius. Tell me, then: when the circumcision in spirit has been brought in, and the sacrifices according to the Law have been overthrown, and that way of life has no place among us, does it not seem somehow unconvincing to say that Christ said, 'I did not come to destroy the Law, but to fulfill'? Or if it is not so, nothing, I think, would stop us from honoring the God of all with cattle-sacrifices and frankincense, bringing him turtledoves and pigeons, and being eager ourselves to fulfill whatever else was customary for the more ancient people.",
    ],
    [
        A("Matthew 5:17", "Palladius restates the Savior's fulfill-not-destroy word."),
        A("John 4:23-24", "Palladius restates worship in spirit and truth."),
        A("Hebrews 10:1", "Law as type and shadow of the coming goods.", "possible"),
        A("Colossians 2:16-17", "Shadow of the things to come.", "possible"),
        A("Psalm 45:9", "Quoted as the forty-fourth psalm (LXX 44): the queen in gold-shot clothing."),
        A("Romans 2:28-29", "Quoted: the Jew in secret; circumcision of heart in spirit."),
        A("Leviticus 1:14", "Turtledoves and pigeons as legal offerings.", "possible"),
    ],
    [
        "Psalm numbering: Cyril cites 'the forty-fourth psalm' (LXX 44); linked as Psalm 45:9.",
    ],
)

S(
    4,
    "We do not abolish the Law; we establish it",
    [
        "Cyril. And yet, my friend, you are carried a long way from what is fitting. For you think the Law has been overthrown, as if we had no profit from what is his, and as if it were wholly useless for showing anything of the things we need — not rather that it has been turned toward a showing of the truth, though the blessed Paul writes: 'Do we then abolish the Law through faith? By no means! Rather we establish the Law.' For the Law tutors, and carries us well toward the mystery that is in Christ. And we say that the things of old decreed through Moses to the more ancient people are the first elements of the oracles of God. And if we push aside the tutor, who will still convey us to the mystery of Christ? And if we refuse to learn the first elements of the oracles of God, how, or from where, shall we still arrive at the end? Or is Christ not, according to the Scriptures, the fullness of Law and prophets?",
        "Palladius. Yes.",
        "Cyril. For it is written so. And the fullness of Law and prophets would be this: that every prophetic and legal decree looks, I think, and is turned toward him. That is why, putting the Jews' unbelief to shame, he said: 'Do not think that I will accuse you to the Father; there is one who accuses you, Moses, in whom you have hoped. For if you believed Moses, you would have believed me; for he wrote about me. But if you do not believe his writings, how will you believe my words?' If then he should say he has come not at all to destroy the Law, but rather to bring it to its end, do not think he has worked a total overturning of what was decreed of old; rather a kind of recasting, and, so to speak, a recarving of the things in types toward the true.",
        "Palladius. You have spoken rightly.",
        "Cyril. And this is the sort of thing that had to be done by Christ. Those who have practiced the skill in tablets and paintings do not, as soon as they begin to paint, bring upon the pictures the form that lacks nothing and is finished in every part. First they sketch well in a form and in a less beautiful color, and they show beforehand the types of whatever they may have chosen, still rather dim; then, laying over the shadows the shape that is fitting and most suitable to each, they transfer the types into the form that is manifest, and incomparably better than what was at the start. Or is it not so?",
        "Palladius. I say so.",
        "Cyril. And those who practice the bronze-worker's craft, if they should wish to cast a statue, first bring it in wax into a weak form; then, melting it with fire, they pour on the bronze, and so they bring the thing being crafted to a form that is complete and to a beauty that is very fine. And when the many kinds of colors have been thrown upon the shadows, and the bronze also has melted the things of wax,",
    ],
    [
        A("Romans 3:31", "Quoted: do we abolish the Law through faith? We establish it."),
        A("Galatians 3:24", "The Law as tutor unto Christ."),
        A("Hebrews 5:12", "First elements of the oracles of God."),
        A("Romans 10:4", "Christ the end/fullness of the Law.", "possible"),
        A("Matthew 5:17", "Cyril restates: he came not to destroy but to bring the Law to its end."),
        A("John 5:45-47", "Quoted: Moses accuses; he wrote about me."),
    ],
)

S(
    5,
    "Painters, bronze, and Moses' veil",
    [
        "Cyril. The first shapes, the ones at the beginning, might seem for a little to have been set aside and overthrown. But the thing is not so by nature. For bronze-worker and painter, if they told the truth, would say: We have not destroyed the shadows; we have not sent the types into utter uselessness; we have rather fulfilled them. For what could still be seen more dimly and less beautifully, as in shadows and types, this has gone forward toward what is better and more manifest.",
        "Palladius. You speak well.",
        "Cyril. And if anyone should choose to search the holy and God-breathed Scripture truly, he will know that what I say is wholly true. For Moses used to put a veil on his own face, because the sons of Israel could not gaze into his face, according to what is written.",
        "Palladius. And what does this hint?",
        "Cyril. For minds of the Jews that were still rather thick, the outward things of the Law were somehow bearable — I mean again the things through the letter alone — but the things hidden inside were wholly unbearable and not to be approached, and, so to speak, the true face of the meanings. That is why divine Paul also writes to us: 'For until this day the same veil remains on the reading of the Old Covenant, not being unveiled, because it is abolished in Christ. But to this day, whenever Moses is read, a veil lies on their heart.' But let the things of the Jews stand here. 'And we all,' he says, 'with unveiled face, mirroring the glory of the Lord, are being transformed into the same image from glory to glory, as from the Lord, the Spirit; and the Lord is the Spirit.' For just as those who look in a mirror would gaze at an image and type of the true, and not at the true itself, in the same way, I think, those who desire to see the beauty of the life in Christ would succeed at the thing longed for in the best way by using the Law as a mirror. For recasting the same image of the things into truth, they will know purely what seems most of all good and well-pleasing to God.",
        "Palladius. Then what would be the reason that the new gospel oracle was not given to the people of old at the start, and types and shadows were legislated instead?",
        "Cyril. The exact account of the economy, and how these things would stand, in what is truer, must be referred piously to God who knows all. But reasonings that do not know how to go without good thoughts do carry us somehow, at least to a moderate knowledge, or perhaps even to seeming to know the occasion of the economy. We say, then, that those redeemed from Egypt needed much tutoring, and a kind of upbringing suited to infants. For they were still thick-minded, and very easily carried toward anything most unseemly.",
    ],
    [
        A("Matthew 5:17", "Fulfillment of types, not their destruction: the painters' and bronze-workers' analogy."),
        A("2 Timothy 3:16", "Holy and God-breathed Scripture.", "possible"),
        A("Exodus 34:33-35", "Moses put a veil on his face."),
        A("2 Corinthians 3:14-15", "Quoted: the veil on the reading of the Old Covenant."),
        A("2 Corinthians 3:18", "Quoted: we all with unveiled face mirroring the glory of the Lord."),
        A("2 Corinthians 3:17", "Quoted: the Lord is the Spirit."),
        A("1 Corinthians 13:12", "Seeing in a mirror, not the thing itself.", "possible"),
        A("Hebrews 5:12-13", "Infant upbringing and first teaching.", "possible"),
    ],
)

S(
    6,
    "Milk for infants; the calf; tablets of stone",
    [
        "Cyril. And for those sick with a love of flesh that is wholly hard to wash off, and caught in passions hard to escape, it was still somehow out of reach, and not ready to hand, to be able to spring up at once toward what is exceedingly fine, so as to take up a manner of life perhaps so bright and beyond nature as to walk on the earth and have their citizenship in heaven, according to what is written. For is not solid food for the mature, and milk the more fitting thing for those still infants?",
        "Palladius. Very much so.",
        "Cyril. So then those still infants needed the tutoring that is in types, and, so to speak, a more tender upbringing, not the word that orders toward perfection and is able to carry them to what is complete. And the people from Israel would be found so light and small-minded, and easy toward any of the passions, that if there had been in them an exact testing of habits and attempts, they would not, I think, even have been counted worthy of a shadow. And Moses has shown this. For when God commanded, he himself sprang up the mountain to receive the Law. But they at once slipped down into apostasy. For they have made a calf, and the wretches have dared to say: 'These are your gods, Israel, who brought you up from the land of Egypt.' So at such terrible lightness Moses was distressed, and he broke the tablets on which the Law was, thinking those whose mind was so struck as to forget the wonders worked for them by the divine power, and to assign worship again to a calf, and to come to a remembrance of the worship in Egypt, were not worthy even of a shadow or of types, or of any tutoring from above at all. But then the Law was sketched for the more ancient people on stone tablets by the finger of God, as it is written. And those things were a type of what we believe has come to be in us in Christ. For the Master God of all writes, as it were, in us the knowledge of his own will, using the Son in the Spirit as a pen. For he named him so through David, saying: 'My tongue is a pen of a swift-writing scribe.' For the Father's pen — that is, the Son — engraved on the hearts of all the knowledge of every good, using the Spirit of the Father and his own as a kind of finger of God. For he named the Spirit the finger of God, saying at one time, 'But if I by the Spirit of God cast out the demons,' and at another, 'But if I by the finger of God cast out the demons.' And Paul also called us the spiritual letter, saying: 'You are our letter, written in our hearts, known and read by all men, being manifested that you are a letter of God ministered by us, written not with ink but with the Spirit of the living God, not on stone tablets but on tablets of hearts of flesh.'",
        "Palladius. But that the things according to the Law are types and shadows, I too would say, know it well. Come then, putting a fine and exact mind to what was oracled in type,",
    ],
    [
        A("Philippians 3:20", "Citizenship in heaven while walking on the earth."),
        A("Hebrews 5:12-14", "Solid food for the mature; milk for infants."),
        A("1 Corinthians 3:1-2", "Milk, not solid food, for infants.", "possible"),
        A("Exodus 32:1-4", "They made a calf: these are your gods, Israel."),
        A("Exodus 32:19", "Moses broke the tablets."),
        A("Exodus 31:18", "Tablets of stone written by the finger of God."),
        A("Exodus 34:1", "Stone tablets.", "possible"),
        A("Psalm 45:1", "Quoted as David: my tongue is a pen of a swift-writing scribe (LXX 44:2)."),
        A("Matthew 12:28", "Quoted: if I by the Spirit of God cast out the demons."),
        A("Luke 11:20", "Quoted: if I by the finger of God cast out the demons."),
        A("2 Corinthians 3:2-3", "Quoted: you are our letter, written not with ink but with the Spirit, on hearts of flesh."),
    ],
    [
        "Psalm 45:1 is LXX Psalm 44:2, which Cyril cites as spoken through David.",
    ],
)

S(
    7,
    "Ask, seek, knock; man turned aside",
    [
        "Palladius. Let us search very well the beauty of the truth. For so at last the mystery of the worship in spirit would be unhidden to no one of those who are.",
        "Cyril. And yet, noble friend, I have shuddered at this greatly, and with reason, and I am very reluctant toward it. For I think the things that have obtained a contemplation so removed and stretched high would be ungraspable for those of our time. And I think a man looking into the depth of the theorems in the Law must say: 'Who is wise and will understand these things? And understanding, and will know them?'",
        "Palladius. The thing is not without roughness, my good man. Yet 'Ask,' says Christ, 'and it will be given you; seek and you will find; knock and it will be opened to you.'",
        "Cyril. We must go on, then, to the need of hunting what makes for profit; and let us also stretch out a petition beforehand, saying: 'Uncover my eyes, and I will perceive your wonders from your Law.' And we must, as it seems, speak before the rest both of man's turning aside into worthlessness, and about slavery, and the captivity under the enemy of all, and how and in what manner these things are worked by us and in us. And then, next, also in what manner we must turn away from the evil, and shake off the yoke of the slavery to it, and spring up again toward what was at the beginning, God saving and helping. For if the word goes for us on this fitting road, the rest also would, I think, belong.",
        "Palladius. You think most rightly.",
        "Cyril. For being able to bear fruit to God and to bring spiritual sacrifices, or to play the man and to be well thought of, when we wish to accomplish virtue, would not, I suppose, be fitting for those still so bound in slavery and in the necessity of passions, but for those whose mind is already somehow sobering toward the free, and who have not left unpracticed the shaking-off of the yoke of the devil's greed.",
        "Palladius. I agree, for you think rightly.",
        "Cyril. Come then, let us say that man was made at the beginning with his mind still somehow above sin and passions, yet not wholly incapable of the turning aside toward whatever he might choose. For it seemed right to God, the best craftsman of all, to fasten to him the reins of his own wishes, and to assign him to do what seemed good by self-commanded impulses. For virtue had to be seen as of choice, and not as from necessity, and not as set unfailingly on laws of nature; for that would be proper to the highest of all beings and to the supremacy. And when the living creature had been finished according to the reasons of its own nature, God crafting it, it was at once rich in the likeness toward him. For the image of the divine nature was engraved on it, when the Holy Spirit had been breathed in.",
    ],
    [
        A("Hosea 14:9", "Quoted: who is wise and will understand these things."),
        A("Matthew 7:7", "Quoted: ask, seek, knock."),
        A("Psalm 119:18", "Quoted: uncover my eyes, and I will perceive your wonders from your Law (LXX 118:18)."),
        A("1 Peter 2:5", "Spiritual sacrifices.", "possible"),
        A("Romans 12:1", "Spiritual/reasonable worship.", "possible"),
        A("Genesis 1:26-27", "Man made in the image and likeness."),
        A("Genesis 2:7", "The inbreathing; the living creature finished."),
    ],
    [
        "Psalm 119:18 is LXX 118:18, which Cyril quotes as from the Law-psalm.",
    ],
)

S(
    8,
    "Breath of life; the woman as type of pleasure",
    [
        "Cyril. For that is the breath of life, since God is life by nature.",
        "Palladius. Did the divine Spirit then become soul for the man?",
        "Cyril. And how is it not wholly absurd to think this way? For the soul would itself also have remained unchangeable; but as it is, it is changeable. And the Spirit is not changeable at all. Or if it suffers change, will the blame run up upon the divine nature itself — if the Spirit is of God and Father, and also of the Son, the one essentially from both, or rather from the Father through the Son, poured out? It is ignorant, then, to think the Spirit has been recast into a soul and has passed over into a man's nature. But what was molded was ensouled by an unspeakable power; and it was at once made beautiful by the gift of the Spirit. For there was no other way for us to be rich in the divine image.",
        "Palladius. You speak well.",
        "Cyril. So then, having adorned the craft-work, God granted the dwelling in paradise. And since the one so made splendid, and crowned with the plenty of the goods from above, had to be kept from being easily carried toward arrogance, not knowing the slavery, and that there is a measure of things proper to servants (for what is too wide toward glory, and freedom without measure, carries toward the proud and accursed passion), a law of self-control was given him as an occasion of not being ignorant of the Master, so that through it he might always be called to a remembrance of the one who had commanded with authority, and might know clearly that he is yoked under the statutes of the one who rules. But that unholy and God-hated beast was not still.",
        "Palladius. You would mean, I think, Satan, who was hurled down from the heavenly vaults like lightning; for it seemed to him, in a boyish sickness, to wish to be God, and he imagined things beyond his own nature.",
        "Cyril. You guess well. For being inventor and father of envy and of sin, he did not wish to be idle about the living creature on earth, that is, the man. Then, coming under him by craft and deceits, he carried him aside into disobedience, using the woman as an instrument of villainy. For the pleasures with us and in us always somehow shake us toward the unbeautiful, that is, into sin; and the woman is a type of pleasure; and the mind is often run down by the flatteries from pleasures toward what it did not wish. What then is seen to have happened in Adam as in a narrative of events and perceptibly, this one may see fulfilled in each of us also, intelligibly and hiddenly. For pleasure, rising beforehand, bewitches the mind, and little by little draws it under toward thinking at last that a transgression of the divine law is nothing at all. And",
    ],
    [
        A("Genesis 2:7", "The breath of life; God is life by nature."),
        A("John 4:24", "God as spirit/life by nature.", "possible"),
        A("John 15:26", "Spirit from the Father.", "possible"),
        A("Genesis 2:8-15", "Dwelling in paradise."),
        A("Genesis 2:16-17", "The law of self-control: the command not to eat."),
        A("Luke 10:18", "Satan hurled like lightning from heaven."),
        A("Isaiah 14:12-14", "The wish to be God; fall from heaven.", "possible"),
        A("John 8:44", "Father of sin; the devil as inventor of evil."),
        A("Wisdom 2:24", "By the envy of the devil death entered the world.", "possible"),
        A("Genesis 3:1-6", "The woman as instrument; the deceit into disobedience."),
        A("1 Timothy 2:14", "The woman deceived.", "possible"),
        A("James 1:14-15", "Desire draws and entices; the next column completes the quote."),
    ],
)

S(
    9,
    "Desire conceives sin; Abraham goes down to Egypt",
    [
        "the disciple of Christ will confirm it, saying: 'Let no one being tempted say, I am tempted from God. For God is untempted of evils, and he himself tempts no one. But each is tempted, being drawn out and baited by his own desire. Then desire, having conceived, bears sin; and sin, when it is finished, gives birth to death.'",
        "Palladius. The word is exact.",
        "Cyril. So then, having sold away the grace from God, and already stripped of the goods that were at the beginning, human nature was sent out of the paradise of delight, and was at once recast toward the unbeautiful, and having fallen inside corruption was thereafter shown to be so.",
        "Palladius. Necessarily. For want of the gifts from God is nothing else, I think, than a falling-away from every good. And man's nature would very easily sicken into a carrying-aside toward anything out of place, if the grace of the one who saves did not hold it up toward virtue, enriching it with the goods from above and from herself.",
        "Cyril. You speak well. For I would agree, and with much reason; for the living bread, that is, the Word of God, feeds toward the spiritual strength. For it is written that 'and bread strengthens a man's heart.' And it sets free from slavery and from passions, and gilds well with the boasts that belong to freedom. But when God has as it were drawn in his hand, and does not distribute to us the supply in these things, there is every necessity that we fall into evils we did not wish, and slip away from all virtue, and come as it were under another's yoke, and come to such evils and greed as to be near at last even to losing the understanding that serves us toward any of the goods and is housed with us, and for the heart of the one who has suffered to be shown wholly empty of the wisdom according to God, as if it had gone whoring to Satan, and had been easily carried down into the insolences and wantonnesses under him.",
        "Palladius. Would you show how, or will you leave me floating on bare reasonings?",
        "Cyril. Not at all. For I would show as well as I can the things that happened to the ancients, shaping them with skill into a type of the intelligible things. For the things in sense and in a telling sight would become for us clear and most evident images of the things in a fine contemplation. It is written, then, about the forefather Abraham: 'And there was a famine on the land, and Abraham went down into Egypt to sojourn there, because the famine prevailed on the land.' For leaving the land dear to him and that had borne him, he shifted toward another, which God had shown. For 'Go out,' he says, 'from your land and from your kindred, and come into a land which I will show you.' But when the famine was weighing down, and bringing a loss wholly hard to escape, he was forced, and not willingly, to see Egypt. And he did not settle, but rather sojourned in it.",
        "Palladius. What then is this?",
    ],
    [
        A("James 1:13-15", "Quoted: God tempts no one; desire conceives sin; sin gives birth to death."),
        A("Genesis 3:23-24", "Sent out of the paradise of delight."),
        A("Wisdom 2:23-24", "Corruption after the fall.", "possible"),
        A("John 6:51", "The living bread, the Word of God."),
        A("Psalm 104:15", "Quoted: bread strengthens a man's heart (LXX 103:15)."),
        A("Hosea 4:12", "The heart gone whoring.", "possible"),
        A("Genesis 12:10", "Quoted: famine; Abraham went down into Egypt to sojourn."),
        A("Genesis 12:1", "Quoted: go out from your land and from your kindred."),
    ],
)

S(
    10,
    "A famine of hearing; Sarah is taken",
    [
        "Cyril. It shapes for us a very fine contemplation of the things less apparent.",
        "Palladius. In what manner?",
        "Cyril. Rebuking the Jews' unbelief, God said somewhere: 'Behold, I bring a famine on the land, not a famine of bread, nor a thirst of water, but a famine of hearing the word of the Lord. And they will run from east to west seeking the word of the Lord, and they shall not find it.' Would not then, my friend, those pressed by such a famine, and fallen out of the supply that holds them toward virtue, and not having the foods from heaven and from above, of every necessity make the mind as it were a migrant and a fugitive, chasing thereafter after the more shameful things, and, as if pushed out of a land of its own — the strength toward virtue — go down into another habit and will, no longer the one under God, but rather one laid under diabolic scepters? For the father, I think, and king of sin is the first who brought it into the world, whose image and type one might also receive, I think, and with much reason, as Pharaoh, ruling the Egyptians. Among whom the darkness of having wandered was very deep, and no manner of vice was wholly unpracticed.",
        "Palladius. And what was it that pained blessed Abraham from having come, perhaps, into the Egyptians' land?",
        "Cyril. A very great deal. For he was carried a little beyond every evil. And you may learn this easily too, when the holy Writing speaks: 'And it came to pass when Abraham entered into Egypt, the Egyptians saw the woman, that she was very beautiful, and the rulers of Pharaoh saw her, and they praised her to Pharaoh, and they led her into Pharaoh's house.' See then that the woman almost perished for him, my good man.",
        "Palladius. How sharp the thing is, and enough to grieve.",
        "Cyril. And this will happen about us ourselves, intelligibly. For those who might slip away from a fatherland, as it were, of their own — the accustomed and most dear good order and virtue — and come toward the worse, and come under diabolic scepters, the evil and opposing powers grow upon them and plot terribly in every way and wholly; and if they should see one of those who have come under them able to have an understanding not unbeautiful, they are eager to procure him for their own leader, and they carry him under that one's sowings, so that he may no longer bear fruit to God, but rather to Satan. 'For his foods,' according to what is written, 'are choice'; and they soothe, as it were, the mind that has been caught and has slipped, so that, not looking much toward the free, it may not leave the hired service under them. They sometimes procure the pleasures in earthly things, and as it were enrich them with delights toward nothing, just as, of course, the rulers of the Egyptians, when blessed Abraham was losing the woman who lived with him,",
    ],
    [
        A("Amos 8:11-12", "Quoted: a famine of hearing the word of the Lord."),
        A("John 8:44", "The devil as father of sin; first to bring it into the world.", "possible"),
        A("Wisdom 2:24", "Death entered by the devil.", "possible"),
        A("Genesis 12:14-15", "Quoted: Sarah seen, praised, and taken into Pharaoh's house."),
        A("Habakkuk 1:16", "His foods are choice (LXX)."),
        A("Romans 6:13", "Bearing fruit to God rather than to sin.", "possible"),
    ],
)

S(
    11,
    "Pharaoh's gifts; God rescues Sarah",
    [
        "fawning as it were with honors and with offerings of gifts, wished to carry him far from grieving too much. For it is written that 'And they used Abraham well because of her' — clearly Sarah — 'and there came to be for him sheep and calves and donkeys and servants and maidservants and mules and camels.' For Satan, defrauding us in the things that matter most, and as it were stripping us of free offspring and good fruit, and carrying the well-born mind under his own insolences and wantonnesses out of greed, binds it down with the delight of earthly things. And he has at times driven his madness to this, as to let the trial down even upon Christ himself. 'For leading him up,' it says, 'he showed him all the kingdoms of the inhabited world in a moment of time, and the devil said to him: I will give you this authority, all of it, and their glory, because they have been handed over to me, and I give them to whomever I wish. You then, if you worship before me, it will all be yours.'",
        "Palladius. It stands rightly. Yet tell me, since I ask: what would be the profit for those who have suffered, or the help?",
        "Cyril. God, noble friend, and the grace from him, which does not allow the weakened mind to be under diabolic feet to the end, but shields and takes out the one who can help himself in nothing. And you may see, if you wish, this also having happened in the case of the forefather Abraham. For when the righteous man had given up, and was able to do nothing at all, God came in the middle, and set the woman free from the Egyptians' wantonness. 'For the Lord tested Pharaoh with great and evil testings, and his house, concerning Sarah, Abraham's wife.' And so he barely let go the one who lived with the righteous man, free of insolence. God alone, then, would take the mind that has been caught out of the devil's hand, and would turn it back into the good order that was at the beginning.",
        "Palladius. So then, pushed down by want of the goods from above, we sometimes go down toward the shameful and abominable.",
        "Cyril. So I say.",
        "Palladius. But it is surely in every way fitting for the God who loves the good, not to let us fall into any of such things.",
        "Cyril. This is most of all fitting for God, and willed, my good man; for he would be least good, and not much a lover of virtue, if he did not have this aim toward us. But we ourselves are causes of the suffering to ourselves, whetting the Master of all into angers; for so he lets a man go toward a weak and unmanly mind. Or do you not hear him crying through one of the holy prophets: 'Behold, I give weakness upon this people, and they shall be weak in it, fathers and sons; neighbor and his neighbor shall perish'? And the most wise Paul also writes about some: 'And as they did not approve to have God in knowledge, God gave them over to a reprobate mind, to do the things that are not fitting.' And more clearly the divine",
    ],
    [
        A("Genesis 12:16", "Quoted: they used Abraham well because of Sarah; flocks and servants given."),
        A("Luke 4:5-7", "Quoted: the devil shows the kingdoms and offers them for worship."),
        A("Matthew 4:8-9", "Parallel temptation narrative.", "possible"),
        A("Genesis 12:17", "Quoted: the Lord tested Pharaoh with great testings concerning Sarah."),
        A("Jeremiah 6:21", "Quoted: I give weakness upon this people (LXX)."),
        A("Romans 1:28", "Quoted: God gave them over to a reprobate mind."),
    ],
)

S(
    12,
    "You were angry, and we sinned",
    [
        "Isaiah sets it down, saying, as from the person of the sons of Israel, or of those who have slipped into sins: 'Behold, you were angry, and we sinned.'",
        "Palladius. Tell me, then: when we grow slack about what is fitting and are caught by sins, shall we throw the cause upon God, and accuse him of the anger, as if we had sinned because of this?",
        "Cyril. We will not bring a charge — for that is madness — but when we say, 'You were angry, and we sinned,' we mean something like this: that if we do not have your goodwill, Master, there is nothing to keep us from being tyrannized by sin, because of the weakness of our nature, and from being liable thereafter to every evil.",
        "Palladius. I understand what you say.",
        "Cyril. So then, stripped of the care from above and of the sparing, and paying the penalties of extreme fading and of the unchecked turnings-aside toward the worthless, we are shown weak and easy to catch, and sick with everything of that kind. And you may look at these things brightly, if you meet Jeremiah's words. For the wild crowd of the Jews, though they were reveling very richly and going wide in the honors from God, and had already mastered all their enemies, and had driven on perhaps to the very highest of glory among men, practiced a hard and unbroken unbelief. And having all but said farewell to the commandments through Moses, and counting what was decreed worth little account at all, they were carried by unhindered impulses into ruin and destruction. For under an oak, and a white poplar, and a shading tree, according to the prophet's voice, they built altars, and in the groves densest with trees, having fixed precincts for the demons, they thought it right to honor them with cattle-sacrifices and frankincense and all the rest, not blushing to call the things crafted by their own hands gods and saviors and everything of that kind. And they came at times to this folly, as thereafter to make unholy child-slaughters a matter of boasts, and to think they were kindling in this way a very rich sacrifice for them. And the things of impiety were not practiced by those from Israel only up to this. Always bringing as it were an addition to the daring deeds, the unbridled departure toward anything out of place, they provoked him not moderately to angers against themselves, though the lawgiver is kind. And when they shook off the slavery to him in a youthful way, he thereafter let them also be defrauded even by enemies, and be carried already toward a necessary hired service, I mean the one under Chaldeans and Babylonians. For these came, leaving their own homes, enslaved them, and burned the holy and famous city, and it seemed the people being warred on barely asked",
    ],
    [
        A("Isaiah 64:5", "Quoted: behold, you were angry, and we sinned (LXX 64:4/5)."),
        A("Hosea 4:13", "Under oak and white poplar and shading tree they sacrificed."),
        A("Jeremiah 2:20", "Upon every high hill and under every green tree.", "possible"),
        A("Jeremiah 7:31", "Child-sacrifice in the valley.", "possible"),
        A("Psalm 106:37-38", "They sacrificed their sons and daughters to demons.", "possible"),
        A("2 Kings 25:8-10", "The holy city burned; captivity to Babylon."),
        A("Jeremiah 21:2", "They asked the prophet where the evil would end.", "possible"),
    ],
)

S(
    13,
    "The way of life and the way of death",
    [
        "the prophet Jeremiah where the evil would end for them. 'And Jeremiah said,' it says: 'Thus you shall say to Zedekiah: Thus says the Lord: Behold, I turn back the war-weapons with which you are fighting in them against the Chaldeans who have shut you up outside the wall, into the middle of this city. And I will war on you with a hand stretched out and with a strong arm, with fury and great anger. And I will strike all who live in this city, the men and the cattle, with a great death, and they shall die.' Then after other things: 'And to this people,' he says, 'you shall say, Thus says the Lord: Behold, I have given before your face the way of life and the way of death. He who sits in this city shall die by sword and by famine, and he who goes out to go over to the Chaldeans who have shut you up shall live. And his soul shall be for spoils, and he shall live. Because I have set my face on this city for evils and not for goods, and it shall be given into the hands of the king of Babylon, and he shall burn it with fire.' You understand, then, that when we grieve God by the honors given once for all, we wretches will not be able to stand against the strengths of the enemies, and when the divine anger is as it were lying on us and leaping down on us, we shall be slaves instead of free, and we shall live an inglorious and pitiable life.",
        "Palladius. You speak well.",
        "Cyril. For the law of God carries the tender and well-reined man toward a blameless way of life, and becomes as it were a lamp for each toward the showing of what is useful and needed, and one who is overcome by reverence toward it would live, I think, not without wonder, and would inhabit as it were a holy city — what is set firm toward virtue and has come to stand in piety. But if someone should choose, as if into a thicket and a wood fair with flowers and good timber, to rush readily into the worldly pleasures, and to linger in the delights according to this life, and as it were to receive into mind and heart a swarm of idols — the many-formed pleasure — and to burn to the demons the fruits of his own eagerness, then, then, and with much reason, he would slip away from the sparing from above, and would lie a very ready hunt for those who wish to take him. And being pushed out, as from a holy city, of the good order that was at the beginning, he will thereafter go, as from a necessary yoke, toward what seems good to those who rule, and he will be far from God, at least in the manner of disposition, undergoing the migration into Babylon, that is, the things beyond the bounds of a holy land, in which God is known, and his name is great. That is why those who undergo so hard a labor, and have fallen into enemies' hands, and cannot bear the way of life with them as slavish and servile, have cried out: 'By the rivers of Babylon, there we sat and wept, when we remembered Zion.' For the human mind, I think, is sick with something of this kind.",
        "Palladius. What do you mean?",
    ],
    [
        A("Jeremiah 21:3-6", "Quoted: weapons turned back; I will war on you; a great death."),
        A("Jeremiah 21:8-10", "Quoted: the way of life and the way of death; go over to the Chaldeans and live."),
        A("Psalm 119:105", "The law as a lamp.", "possible"),
        A("Psalm 76:1", "In Judah God is known; his name is great (LXX 75:2)."),
        A("Psalm 137:1", "Quoted: by the rivers of Babylon we sat and wept (LXX 136:1)."),
    ],
)
