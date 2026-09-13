#!/usr/bin/env python3
"""Batch Origen Ezekiel Homiliae I–XIV OET (True OET; no Scheck)."""
from __future__ import annotations

A = lambda reference, reason, certainty="clear": {
    "reference": reference,
    "reason": reason,
    "certainty": certainty,
}


def sec(n, title, latin, gloss, english, allusions):
    return {
        "section": n,
        "title": title,
        "latin": latin,
        "gloss": gloss,
        "english": english,
        "allusions": allusions,
    }


HOMILIES: dict[int, dict] = {
    1: {
        "claim": "origen-isaiah-ezekiel-ezek-h1-1-2-oet",
        "sections": [
            sec(
                1,
                "Not every captive suffers for his own sins",
                "Non omnis qui captivus est propter peccata sustinet captivitatem. Multitudo causa peccati derelicta a Deo et a Nabuchodonosor in Babyloniam ducta est; pauci tamen iusti non ob culpam suam, sed ne peccatores subsidium non haberent. Clemens Deus inter supplicia visitationis pietatem miscet.",
                "Not everyone who is captive endures captivity because of sins. The multitude on account of sin was forsaken by God and led by Nebuchadnezzar into Babylon; yet a few just ones not for their own fault, but lest sinners have no help. Kind God mixes the piety of his visitation among the punishments.",
                "Not every exile is for personal guilt. Most of Judah fell [[into Babylon >> Bible:Ezekiel 1:1]] for sin under Nebuchadnezzar, yet a few righteous went too so the guilty would not lack help. God mixes mercy with discipline — like Joseph’s famine provision in Egypt.",
                [A("Ezekiel 1:1", "captivity setting"), A("Genesis 45:5-7", "Joseph preserves brothers", "probable")],
            ),
            sec(
                2,
                "Vision opens the book; glory Amen",
                "Visio Ezechielis aperit librum — rotae, cherubin, gloria Domini. Propheta inter captivos loquitur ut peccatores remedium consequantur. Gloria Christo. Amen.",
                "Ezekiel’s vision opens the book — wheels, cherubim, the glory of the Lord. The prophet speaks among the captives so that sinners may obtain a remedy. Glory to Christ. Amen.",
                "The book opens with [[visions of God by the Chebar >> Bible:Ezekiel 1:1-28]] — wheels, living creatures, the Lord’s glory — so captives hear a healing word. Glory to Christ. Amen.",
                [A("Ezekiel 1:1-28", "throne-chariot vision")],
            ),
        ],
    },
    2: {
        "claim": "origen-isaiah-ezekiel-ezek-h2-1-2-oet",
        "sections": [
            sec(
                1,
                "Scripture names every kind of sin to heal",
                "Nullam speciem peccatorum Scriptura reticeat. Verbum Dei missum ad sanandos omnem speciem perstringit. Sicut de populo et sacerdotibus et dispensatoribus, ita de veris et falsis prophetis — pseudo-prophetae magistri ecclesiarum non recte sermone vel vita.",
                "Let Scripture keep silent about no kind of sins. The Word of God sent to heal touches every kind. As concerning people and priests and stewards, so concerning true and false prophets — false prophets are church teachers not right in word or life.",
                "Scripture hides no species of sin; the Word sent to heal names them all. True prophets minister God’s words; [[false prophets >> Bible:Ezekiel 13:1-3]] are teachers whose talk or life denies the discipline they preach.",
                [A("Ezekiel 13:1-3", "false prophets"), A("Matthew 7:15", "false prophets", "probable")],
            ),
            sec(
                2,
                "Glad when the Word rebukes our order",
                "Laeti sumus si Scriptura moneat ut recedamus a vitiis, magis si ordinis nostri aliquos Dei sermo perstringat volentes sanari. Gloria Deo. Amen.",
                "We are glad if Scripture warns that we withdraw from vices, more if the word of God touches some of our order who wish to be healed. Glory to God. Amen.",
                "Rejoice when Scripture warns us off vices — still more when God’s word strikes our own rank so we turn and are healed. Glory to God. Amen.",
                [A("Ezekiel 13:9", "false prophets cut off", "probable")],
            ),
        ],
    },
    3: {
        "claim": "origen-isaiah-ezekiel-ezek-h3-1-2-oet",
        "sections": [
            sec(
                1,
                "Set your face against daughters who prophesy from their heart",
                "Obfirma faciem tuam contra filias populi prophetantes de corde suo. Est alia facies praeter corporis — facies animae quae adversus mendacium firmatur.",
                "Set your face against the daughters of the people prophesying from their own heart. There is another face besides the body’s — the soul’s face which is firmed against the lie.",
                "[[Set your face against the daughters of your people who prophesy from their own hearts >> Bible:Ezekiel 13:17]]. The soul has a face that must be braced against lying oracles.",
                [A("Ezekiel 13:17", "daughters prophesying")],
            ),
            sec(
                2,
                "Blotted from Israel’s writing",
                "Non erunt in scriptura domus Israel — exalegentur de libro viventium. Gloria Christo. Amen.",
                "They will not be in the writing of the house of Israel — they will be blotted from the book of the living. Glory to Christ. Amen.",
                "Lying prophetesses [[shall not be in the writing of the house of Israel >> Bible:Ezekiel 13:9]]; they are [[blotted from the book of the living >> Bible:Psalm 69:28]]. Glory to Christ. Amen.",
                [A("Ezekiel 13:9", "not in Israel’s writing"), A("Psalm 69:28", "book of the living")],
            ),
        ],
    },
    4: {
        "claim": "origen-isaiah-ezekiel-ezek-h4-1-2-oet",
        "sections": [
            sec(
                1,
                "If the land sins — Noah, Daniel, Job",
                "Si terra peccaverit, extenditur manus super ipsam terram ut auferatur firmamentum panis. Non dixit tantum accolae sed terra. Et si fuerint in medio eius Noe et Daniel et Iob, liberabunt animas suas.",
                "If the land has sinned, the hand is stretched over the land itself that the staff of bread be taken away. He did not say only the dwellers but the land. And if Noah and Daniel and Job were in its midst, they will deliver their own souls.",
                "[[If a land sins >> Bible:Ezekiel 14:13]], famine strikes the land itself. Even [[Noah, Daniel, and Job >> Bible:Ezekiel 14:14]] would deliver only their own souls — not a corrupt city’s crowd.",
                [A("Ezekiel 14:13-14", "land sins; three righteous")],
            ),
            sec(
                2,
                "Attend the hard spectacle of judgment",
                "Ingens cura expositionis; quasi ad grande spectaculum aciem mentis intendite. Gloria Deo. Amen.",
                "Huge care of exposition; as to a great spectacle aim the mind’s edge. Glory to God. Amen.",
                "Lean in: the land’s judgment is a hard spectacle for the mind. Glory to God. Amen.",
                [A("Ezekiel 14:13-20", "four sore judgments", "probable")],
            ),
        ],
    },
    5: {
        "claim": "origen-isaiah-ezekiel-ezek-h5-1-2-oet",
        "sections": [
            sec(
                1,
                "Sword and death among the four scourges",
                "Post famem et bestias pessimas restant romphaea et mors. Quis est gladius quem formidare debemus ne mittatur super terram nostram? Statuit igneam romphaeam Cherubin custodire viam ligni vitae.",
                "After famine and the worst beasts there remain the sword and death. What is the sword we ought to fear lest it be sent upon our land? He set the fiery sword and the cherubim to guard the way of the tree of life.",
                "After famine and wild beasts come [[sword and death >> Bible:Ezekiel 14:21]]. Fear the sword over our figurative land — recall the [[flaming sword guarding Eden >> Bible:Genesis 3:24]].",
                [A("Ezekiel 14:21", "four sore judgments"), A("Genesis 3:24", "flaming sword")],
            ),
            sec(
                2,
                "Double torment of the burning blade",
                "Gladius acutus et candens dupliciter torquet. Caveamus ne per hunc gladium transeamus. Gloria Christo. Amen.",
                "A sharp and glowing sword torments doubly. Let us beware lest we pass through this sword. Glory to Christ. Amen.",
                "A glowing blade cuts and burns at once. Pray we never must pass under it. Glory to Christ. Amen.",
                [A("Ezekiel 21:9-10", "sword sharpened", "probable")],
            ),
        ],
    },
    6: {
        "claim": "origen-isaiah-ezekiel-ezek-h6-1-2-oet",
        "sections": [
            sec(
                1,
                "Prophets’ constancy; Ezekiel bolder than Isaiah",
                "Consideranti constantiam prophetarum miraculum subit — magis Deo quam hominibus crediderunt. Admirabar Esaiam antequam compararem Ezechiel: audite principes Sodomorum. Ezechiel iubetur notas facere Hierusalem abominationes suas.",
                "Considering the prophets’ constancy a wonder comes — they believed God more than men. I used to admire Isaiah before I compared Ezekiel: hear, princes of Sodom. Ezekiel is ordered to make known to Jerusalem her abominations.",
                "Prophets feared God more than men. Isaiah cried [[Hear, rulers of Sodom >> Bible:Isaiah 1:10]]; Ezekiel must [[make known to Jerusalem her abominations >> Bible:Ezekiel 16:2]] — still harder constancy.",
                [A("Isaiah 1:10", "princes of Sodom"), A("Ezekiel 16:2", "Jerusalem’s abominations"), A("Acts 5:29", "obey God rather than men", "probable")],
            ),
            sec(
                2,
                "Death and insults cannot silence the Word",
                "Contempserunt mortem, pericula, contumelias dum voluntati Dei deserviunt. Gloria Dei sermoni. Amen.",
                "They despised death, dangers, insults while they served God’s will. Glory to God’s word. Amen.",
                "They despised death, danger, and insult while serving God’s will in prophecy. Glory to the Word. Amen.",
                [A("Ezekiel 3:8-9", "forehead hard as flint", "probable")],
            ),
        ],
    },
    7: {
        "claim": "origen-isaiah-ezekiel-ezek-h7-1-2-oet",
        "sections": [
            sec(
                1,
                "Jerusalem’s sin-list builds the hearer",
                "Catalogus peccatorum Hierusalem aedificat audientem — sicut servus novus discit disciplinam domini. Vestes a Deo accepit et fecit sibi sutilia simulacra et fornicata est super eis.",
                "The catalogue of Jerusalem’s sins builds the hearer — as a new slave learns the master’s discipline. She received garments from God and made for herself stitched images and fornicated upon them.",
                "Jerusalem’s sin catalogue trains us not to fall the same way. She took [[God’s garments and made embroidered idols, then played the harlot with them >> Bible:Ezekiel 16:15-18]].",
                [A("Ezekiel 16:15-18", "garments into idols")],
            ),
            sec(
                2,
                "Torn texts become idols; stay outside",
                "Qui scripturas lacerant et verba consuunt commentitia dogmata componentes servire idolis. Non intrabis in tabernaculum meum — foris es. Gloria Christo. Amen.",
                "Those who tear the scriptures and sew words composing invented doctrines serve idols. You shall not enter my tent — you are outside. Glory to Christ. Amen.",
                "Those who shred Scripture and stitch invented doctrines dress idols in holy cloth. [[You shall not enter >> Bible:Ezekiel 44:9]] — sinners stay outside. Glory to Christ. Amen.",
                [A("Ezekiel 16:17-19", "idol garments"), A("Ezekiel 44:9", "uncircumcised out", "probable")],
            ),
        ],
    },
    8: {
        "claim": "origen-isaiah-ezekiel-ezek-h8-1-2-oet",
        "sections": [
            sec(
                1,
                "How shall I settle your heart? Triple fornication",
                "In quo constituam cor tuum, dicit Adonai Dominus, cum facias opera meretricis procacis et fornicata es tripliciter in filiabus tuis? Lupanar in capite omnis viae; mercedes dedisti amatoribus.",
                "How shall I settle your heart, says the Lord Adonai, when you do the works of a bold harlot and have fornicated threefold in your daughters? A brothel at the head of every way; you gave wages to lovers.",
                "[[How weak is your heart >> Bible:Ezekiel 16:30]] when you act the bold harlot — fornication threefold in spirit, soul, and body. You [[built your vault at every street head and paid your lovers >> Bible:Ezekiel 16:31-33]].",
                [A("Ezekiel 16:30-33", "harlot heart; paid lovers"), A("1 Thessalonians 5:23", "spirit soul body", "probable")],
            ),
            sec(
                2,
                "Unlike a common harlot — you pay them",
                "Non es facta ut meretrix congregans mercedes; tu dedisti mercedes omnibus amatoribus. Gloria Deo. Amen.",
                "You were not made like a harlot gathering wages; you gave wages to all lovers. Glory to God. Amen.",
                "Unlike a hireling harlot, Jerusalem [[pays her lovers >> Bible:Ezekiel 16:33-34]] — pouring gifts on idols. Glory to God. Amen.",
                [A("Ezekiel 16:33-34", "pays lovers")],
            ),
        ],
    },
    9: {
        "claim": "origen-isaiah-ezekiel-ezek-h9-1-2-oet",
        "sections": [
            sec(
                1,
                "Amorite father, Hittite mother — one and many",
                "Radix et generatio de terra Chanaan, pater Amorrhaeus, mater Chettaea. Ibi sermo ad unam; hic mater vestra et pater vester — ad plurimas. Diffuso peccato in uno sunt plurimi.",
                "Root and generation from the land of Canaan, Amorite father, Hittite mother. There the speech is to one; here your mother and your father — to many. When sin is poured out, in one there are many.",
                "[[Your origin is from Canaan; your father an Amorite, your mother a Hittite >> Bible:Ezekiel 16:3]]. Later the address multiplies — [[your mother… your father >> Bible:Ezekiel 16:45]] — because spreading sin makes many sinners in one.",
                [A("Ezekiel 16:3", "Canaanite origin"), A("Ezekiel 16:45", "mother and father plural address")],
            ),
            sec(
                2,
                "Compare carefully; difference not chance",
                "Diligens lector confert praeterita praesentibus; differentia non fortuita. Gloria Christo. Amen.",
                "The careful reader compares past things with present; the difference is not by chance. Glory to Christ. Amen.",
                "A careful reader compares earlier and later oracles; the shift from singular to plural is no accident. Glory to Christ. Amen.",
                [A("Ezekiel 16:44-45", "like mother like daughter", "probable")],
            ),
        ],
    },
    10: {
        "claim": "origen-isaiah-ezekiel-ezek-h10-1-2-oet",
        "sections": [
            sec(
                1,
                "First do no shameful work; then blush",
                "Primum nullum opus facere confusionis; secundum post confusionis opera erubescere et oculos deicere. Bonum est post confusionis opera confundi — ne artifex malitiae impediat paenitentiam.",
                "First to do no work of confusion; second after works of confusion to blush and cast down the eyes. It is good after works of confusion to be confused — lest the craftsman of malice hinder repentance.",
                "Best: do nothing shameful. Next best: [[be ashamed >> Bible:Ezekiel 16:63]] after shameful deeds — do not walk brazen as if still just. The devil blocks repentance by shamelessness.",
                [A("Ezekiel 16:63", "be ashamed"), A("Jeremiah 6:15", "not ashamed", "probable")],
            ),
            sec(
                2,
                "Each examine what deserves blush",
                "Unusquisque se ipsum consideret quid fecerit confusione dignum; Deus cordis et renis occulta considerat. Gloria Christo. Amen.",
                "Let each consider himself what he has done worthy of confusion; God considers the hidden things of heart and kidneys. Glory to Christ. Amen.",
                "[[Let each examine himself >> Bible:1 Corinthians 11:28]]: word, deed, thought that deserve blush before him who [[searches heart and kidneys >> Bible:Psalm 7:9]]. Glory to Christ. Amen.",
                [A("Ezekiel 16:63", "remember and be ashamed"), A("Psalm 7:9", "searches hearts"), A("1 Corinthians 11:28", "examine self", "probable")],
            ),
        ],
    },
    11: {
        "claim": "origen-isaiah-ezekiel-ezek-h11-1-2-oet",
        "sections": [
            sec(
                1,
                "Bodily exercise vs eternal life",
                "Exercitio corporum fortitudinem comparat; oculi et aures vegetiores fiunt. Quid prodest ad beatitudinem si corpus roboretur? Emolumentum ad vitam sempiternam quaerendum est.",
                "Bodily exercise furnishes strength; eyes and ears become livelier. What profits toward blessedness if the body is strengthened? Advantage toward everlasting life is to be sought.",
                "Gymnastics sharpens limbs and senses — but [[bodily training is of little profit >> Bible:1 Timothy 4:8]] for eternal life. Exercise the soul on God’s riddle.",
                [A("1 Timothy 4:8", "bodily exercise"), A("Ezekiel 17:2", "pose a riddle", "probable")],
            ),
            sec(
                2,
                "Pose a riddle to the house of Israel",
                "Fili hominis, propone aenigma et dic parabolam ad domum Israel. Gloria Deo. Amen.",
                "Son of man, set forth a riddle and speak a parable to the house of Israel. Glory to God. Amen.",
                "[[Son of man, propound a riddle and speak a parable to the house of Israel >> Bible:Ezekiel 17:2]]. Train the inner eye on the allegory. Glory to God. Amen.",
                [A("Ezekiel 17:2", "riddle and parable")],
            ),
        ],
    },
    12: {
        "claim": "origen-isaiah-ezekiel-ezek-h12-1-2-oet",
        "sections": [
            sec(
                1,
                "Two great eagles; say to the embittering house",
                "De duabus aquilis magnis et magnarum alarum sermo divinus exponit. Die ad domum amaricantem — non addidit exacerbantem me.",
                "Concerning two great eagles of great wings the divine word expounds. Say to the embittering house — he did not add embittering me.",
                "The parable of [[two great eagles with great wings >> Bible:Ezekiel 17:3-7]] is partly opened for us. Speak to the [[rebellious house >> Bible:Ezekiel 17:12]] — embittering, yet the text spares saying ‘embittering me.’",
                [A("Ezekiel 17:3-7", "two eagles"), A("Ezekiel 17:12", "know what these mean")],
            ),
            sec(
                2,
                "Do you not know what these mean?",
                "Nescitis quid ista significent? Relinquit intelligendum quae dimisit intacta. Gloria Christo. Amen.",
                "Do you not know what these mean? He leaves to be understood what he left untouched. Glory to Christ. Amen.",
                "[[Do you not know what these things mean? >> Bible:Ezekiel 17:12]] — some sense is given; some left for the hearer’s labor. Glory to Christ. Amen.",
                [A("Ezekiel 17:12", "what these mean")],
            ),
        ],
    },
    13: {
        "claim": "origen-isaiah-ezekiel-ezek-h13-1-2-oet",
        "sections": [
            sec(
                1,
                "Prince of Tyre — not a mere man",
                "Plangitur princeps Tyri; non putandum hunc hominem esse. In medio Cherubin nullus hominum creatus, in paradiso Dei nutritus. Quis iste? Daniel: princeps Michael; Apostolus: gloria omni operanti bonum.",
                "The prince of Tyre is lamented; it is not to be thought this is a man. In the midst of the cherubim no human was created, nourished in God’s paradise. Who is this? Daniel: prince Michael; the Apostle: glory to everyone doing good.",
                "Lament the [[prince of Tyre >> Bible:Ezekiel 28:12]] — no mere man: [[placed with the cherub in Eden >> Bible:Ezekiel 28:13-14]]. Read with Daniel’s [[prince Michael >> Bible:Daniel 10:13]] and Paul’s [[glory to all who do good >> Bible:Romans 2:10]].",
                [A("Ezekiel 28:12-14", "prince of Tyre in Eden"), A("Daniel 10:13", "Michael"), A("Romans 2:10", "glory for doers of good")],
            ),
            sec(
                2,
                "Pharaoh too; invisible princes",
                "De Pharaone rege Aegypti retractemus — principes non corporeos. Gloria Christo. Amen.",
                "Let us also treat of Pharaoh king of Egypt — princes not bodily. Glory to Christ. Amen.",
                "Likewise weigh [[Pharaoh king of Egypt >> Bible:Ezekiel 29:2-3]] among invisible rulers, not flesh alone. Glory to Christ. Amen.",
                [A("Ezekiel 29:2-3", "Pharaoh the dragon"), A("Ephesians 6:12", "rulers not flesh", "probable")],
            ),
        ],
    },
    14: {
        "claim": "origen-isaiah-ezekiel-ezek-h14-1-2-oet",
        "sections": [
            sec(
                1,
                "The closed gate — the Lord passes through",
                "Porta haec clausa erit, non aperietur, et nemo per eam transibit, quia Dominus Deus Israel transibit per eam et erit clausa. Filius hominis Ezechiel portas templi describit.",
                "This gate shall be shut, it shall not be opened, and no one shall pass through it, because the Lord God of Israel shall pass through it and it shall be shut. Son of man Ezekiel describes the temple gates.",
                "[[This gate shall remain shut; no one shall enter by it, for the Lord, the God of Israel, has entered by it >> Bible:Ezekiel 44:2]]. Ezekiel maps many temple gates for those who have ears.",
                [A("Ezekiel 44:2", "closed gate")],
            ),
            sec(
                2,
                "Hear the allegory; glory Amen — SERIES",
                "Rursus exponit his qui habent aures ad audiendum de porta. Mysterium Domini transeuntis — ecclesiae custodia. Gloria Christo Iesu in saecula. Amen.",
                "Again he expounds to those who have ears for hearing concerning the gate. Mystery of the Lord passing through — the church’s custody. Glory to Christ Jesus forever. Amen.",
                "Again for [[those who have ears to hear >> Bible:Matthew 11:15]]: the Lord’s passing seals the gate — a mystery kept for the church. Glory to Christ Jesus forever. Amen.",
                [A("Ezekiel 44:2-3", "prince sits; gate shut"), A("Matthew 11:15", "ears to hear")],
            ),
        ],
    },
}
