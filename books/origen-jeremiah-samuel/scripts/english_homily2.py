# -*- coding: utf-8 -*-
"""English of Origen, Homilies on Jeremiah, Homily 2 (Jer 2:21–22). From GCS III Greek."""

SECTIONS = []


def S(section, title, english, allusions, notes=None):
    SECTIONS.append(
        {
            "section": section,
            "homily": 2,
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
    "2.1",
    "God did not make death; how did the true vine turn bitter",
    [
        "'God did not make death, nor does he delight in the destruction of the living. For he created all things that they might be, and the generations of the world are saving, and there is no poison of ruin in them, nor a kingdom of Hades upon the earth.' Then, going a little past the wording, I will say from where death entered: 'By the envy of the devil death entered into the world.' So whatever is best about us, God has made; but we have created evil and sins for ourselves.",
        "That is why here too the beginning of the reading in the prophet was speaking, as it were questioningly, to those who have had bitterness in the soul, opposite to the sweetness which God prepared for it: 'How have you turned into bitterness, the alien vine?' As if he were saying: God did not make lameness, but he made all sound of foot — what then has become the cause of those who have been lamed? And God made all the members healthy in the first place — what has become a cause of someone suffering something?",
        "In the same way the soul has come to be 'according to the image' not of the first man only, but of every man. For 'let us make man according to our image and according to our likeness' reaches to all men. And as in Adam that which most people understand as 'according to the image' is older than what was added to him when, because of sin, he wore 'the image of the dusty one,' so in all the 'according to the image of God' is older than the worse image. 'We have worn,' being sinners, 'the image of the dusty one; let us wear,' repenting, 'the image of the heavenly one.' Yet the creation came to be in the image of the heavenly one.",
        "So here the Word is at a loss toward those who sin, speaking as a reproof: 'How have you turned into bitterness, the alien vine? For I planted you a fruit-bearing vine, all true.' In what was said before this it has been spoken, and taking up a little I will persuade you that God planted a good vine, the soul of man, and each, having turned, has become opposite to the will of the one who created him. 'And I planted you a fruit-bearing vine, all' — not in part — 'true,' not one true and one false, but 'I planted you a fruit-bearing vine, all true. How have you turned' — I planted you an all-true vine; you, how have you turned into bitterness and become an alien vine?",
    ],
    [
        A("Wisdom 1:13-14", "Quoted: God did not make death; he created all things that they might be."),
        A("Wisdom 2:24", "Quoted: by the envy of the devil death entered into the world."),
        A("Jeremiah 2:21", "Quoted throughout: how have you turned into bitterness, the alien vine; I planted you a fruit-bearing vine, all true."),
        A("Genesis 1:26", "Quoted: let us make man according to our image and likeness."),
        A("1 Corinthians 15:49", "Quoted: we have worn the image of the dusty one; let us wear the image of the heavenly one."),
    ],
)

S(
    "2.2",
    "Nitre and soap cannot wash every stain",
    [
        "After this let us look at: 'If you wash yourself with nitre and multiply soap for yourself, you are stained in your injustices before me, says the Lord.' Did some sinning soul suppose that, taking nitre and washing with ordinary nitre, it ceases from the stain and ceases from the sin? Did someone assume that, taking this herb that springs from the earth and washing and scouring, the soul is cleansed, because the Word says here to the one who has turned into bitterness and become an alien vine, 'If you wash yourself with nitre and multiply soap for yourself, you are stained in your injustices before me, says the Lord'?",
        "But one must know that the Word has all power. And as he has the power of all Scripture, so the Word has the power of every medicine, and is the power of everything that cleanses, and is most scouring. 'For the word of God is living and active and sharper than any two-edged sword.' And whatever you name, of which there is need, that is in the power of the Word. So there is a word that is nitre, and there is a word that is soap, which, when spoken, cleanses such filth. But since not every sin is healed from such a word as is nitre, and from such a word as is soap — there are sins that do not need nitre or soap — it is said to the one who thinks it has sins of a kind that can be washed off in nitre and soap: 'If you wash yourself with nitre and multiply soap for yourself, you are stained before me in your injustices, says the Lord.'",
        "And as of wounds some are healed with a poultice, and others with oil, and others need a bandage and so are made well, and there are other wounds of which it is said, 'There is no poultice to put on, nor oil nor bandages; but your land is desolate, your cities burned with fire' — so there are some sins which soil the soul, and for these sins the man needs a word that is nitre, a word that is soap. And there are some sins which are not healed this way, for they are not even compared to soil. That is why the Lord in Isaiah, knowing the differences of sins, see how he says, 'The Lord will wash the soil of the sons and of the daughters of Zion, and he will cleanse the blood from their midst with a spirit of judgment and a spirit of burning.' Soil and blood: soil with a spirit of judgment, blood with a spirit of burning. If you have sinned, yet not 'unto death,' you have been soiled. So 'the Lord will wash the soil of the sons and of the daughters of Zion, and he will cleanse the blood from their midst.' Then the matching: toward 'the soil,' 'with a spirit of judgment'; toward 'the blood,' 'with a spirit of burning.' And most of us, if we have sinned the worse things, do not need nitre, nor the multiplying of soap, but the spirit of burning.",
    ],
    [
        A("Jeremiah 2:22", "Quoted throughout: if you wash with nitre and multiply soap, you are stained."),
        A("Hebrews 4:12", "Quoted: the word of God is living and active and sharper than any two-edged sword."),
        A("Isaiah 1:6-7", "Quoted: no poultice, oil, or bandages; land desolate, cities burned."),
        A("Isaiah 4:4", "Quoted: the Lord will wash the soil of Zion's children; blood with a spirit of burning."),
        A("1 John 5:16", "Sin not unto death."),
    ],
)

S(
    "2.3",
    "Baptism in the Holy Spirit, and baptism in fire",
    [
        "That is why Jesus baptizes (perhaps I find the meaning now) 'in the Holy Spirit and fire.' Not that he baptizes the same person 'in the Holy Spirit and fire,' but the holy one 'in the Holy Spirit,' and the one who, after believing, after being counted worthy of the Holy Spirit, has sinned again, he washes in 'fire' — so that it is not the same person being baptized by Jesus 'in the Holy Spirit and fire.' Blessed, then, is the one baptized in the Holy Spirit and not needing the baptism from fire. Thrice-wretched is that one who has need to be baptized with the fire. Yet Jesus has both. 'For a rod will come out of the root of Jesse, and a flower will go up from the root.' A 'rod' upon those being punished; a 'flower' upon the righteous. So 'God is a consuming fire,' and 'God is light': a consuming fire to sinners, light to the righteous and holy.",
        "And blessed is the one who has a part in the first resurrection, who has kept the baptism of the Holy Spirit. Who is the one saved in another resurrection? The one who needs the baptism from fire, when he comes to that fire, and the fire tests him, and that fire finds wood, hay, and stubble, so as to burn them. Therefore, these things being said, gathering as far as we can the words of the Scriptures, let us store them in the heart and try to live according to them, if perhaps we may be able to become clean before the departure, and, having prepared our works for the departure, going out may be taken up in those good things and be saved in Christ Jesus, to whom is the glory and the power to the ages of the ages. Amen.",
    ],
    [
        A("Matthew 3:11", "Quoted: he will baptize you in the Holy Spirit and fire."),
        A("Luke 3:16", "Same Spirit-and-fire baptism.", "possible"),
        A("Isaiah 11:1", "Quoted: a rod from the root of Jesse, and a flower from the root."),
        A("Hebrews 12:29", "Quoted: God is a consuming fire."),
        A("Deuteronomy 4:24", "The Lord your God is a consuming fire.", "possible"),
        A("1 John 1:5", "Quoted: God is light."),
        A("Revelation 20:6", "Blessed is the one who has part in the first resurrection."),
        A("1 Corinthians 3:12-13", "Fire tests; wood, hay, stubble."),
    ],
    ["Klostermann: wood, hay, and stubble (καλάμην). Fire-baptism is for the one who sins again after the Spirit."],
)
