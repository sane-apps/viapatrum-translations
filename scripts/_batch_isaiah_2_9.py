#!/usr/bin/env python3
"""Batch write Isaiah Homiliae II–IX OET artifacts (True OET; no Scheck)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tip_isaiah_ezekiel_homily import write_homily  # noqa: E402

A = lambda reference, reason, certainty="clear": {
    "reference": reference,
    "reason": reason,
    "certainty": certainty,
}

# prev_tip chain starts after Homilia I tip 19a2e1e6
PREV = "19a2e1e6"

HOMILIES: dict[int, dict] = {
    2: {
        "claim": "origen-isaiah-ezekiel-isa-h2-1-2-oet",
        "sections": [
            {
                "section": 1,
                "title": "Ahaz will not ask; the Lord gives Immanuel",
                "latin": (
                    "Quantum ad dictum, verecunde fecit Achaz cum iuberetur "
                    "petere signum in profundum aut in excelsum; ait: non petam "
                    "neque tentabo Dominum. Tamen culpatur: audite, domus David. "
                    "Ideo Dominus ipse dabit signum: ecce virgo in utero accipiet "
                    "et pariet filium, et vocabis nomen eius Emmanuel. Signum "
                    "propositum Dominus Iesus — in profundum quia qui descendit, "
                    "in excelsum quia qui ascendit super omnes caelos."
                ),
                "gloss": (
                    "As to the saying, Achaz acted shyly when ordered to seek a "
                    "sign in the deep or the height; he said I will not seek nor "
                    "test the Lord. Yet he is blamed: hear, house of David. "
                    "Therefore the Lord himself will give a sign: behold a virgin "
                    "will take in the womb and bear a son, and you will call his "
                    "name Emmanuel. The proposed sign is the Lord Jesus — in the "
                    "deep because he who descended, in the height because he who "
                    "ascended above all the heavens."
                ),
                "english": (
                    "Ahaz’s refusal looked modest when he was told to [[ask a sign "
                    "in the deep or in the height >> Bible:Isaiah 7:11]]; he answered "
                    "[[I will not ask, nor will I test the Lord >> Bible:Isaiah 7:12]]. "
                    "Yet the house of David is rebuked, and the Lord himself gives "
                    "the sign: [[behold, the virgin shall conceive and bear a son, "
                    "and you shall call his name Immanuel >> Bible:Isaiah 7:14]]. "
                    "That sign is Jesus — [[he who descended is also he who ascended "
                    "far above all the heavens >> Bible:Ephesians 4:9-10]]."
                ),
                "allusions": [
                    A("Isaiah 7:11", "ask a sign"),
                    A("Isaiah 7:12", "Ahaz refuses"),
                    A("Isaiah 7:14", "Immanuel"),
                    A("Ephesians 4:9-10", "descent and ascent"),
                ],
            },
            {
                "section": 2,
                "title": "Butter and honey; Christ among us",
                "latin": (
                    "Butyrum et mel manducabit. Quomodo Christus prophetatur "
                    "comedens butyrum et mel — antequam sciat reprobare malum "
                    "et eligere bonum. Signum in nobis nascitur cum Emmanuel "
                    "nobiscum Deus; qui aperit et introit cenat nobiscum. Gloria "
                    "Christo. Amen."
                ),
                "gloss": (
                    "Butter and honey he will eat. How Christ is prophesied eating "
                    "butter and honey — before he knows to refuse evil and choose "
                    "good. The sign is born in us when Emmanuel is God with us; "
                    "he who opens and enters dines with us. Glory to Christ. Amen."
                ),
                "english": (
                    "[[Butter and honey he shall eat >> Bible:Isaiah 7:15]] — before "
                    "he knows to refuse the evil and choose the good. Immanuel is "
                    "[[God with us >> Bible:Matthew 1:23]]; the risen Lord "
                    "[[stands at the door and knocks >> Bible:Revelation 3:20]] so "
                    "that we may dine with him. Glory to Christ. Amen."
                ),
                "allusions": [
                    A("Isaiah 7:15", "butter and honey"),
                    A("Matthew 1:23", "God with us"),
                    A("Revelation 3:20", "door and supper"),
                ],
            },
        ],
    },
    3: {
        "claim": "origen-isaiah-ezekiel-isa-h3-1-3-oet",
        "sections": [
            {
                "section": 1,
                "title": "Seven women seek one who takes away reproach",
                "latin": (
                    "Septem mulieres patiuntur opprobrium et quaerunt eum qui "
                    "possit auferre opprobrium earum. Promittunt suum panem "
                    "manducare et vestimentis suis operiri. Septem mulieres una "
                    "sunt — Spiritus Dei: spiritus sapientiae et intellectus, "
                    "consilii et virtutis, scientiae et pietatis, timoris Domini. "
                    "Singulae patiuntur opprobrium a falsis sapientiis saeculi."
                ),
                "gloss": (
                    "Seven women suffer reproach and seek him who can take away "
                    "their reproach. They promise to eat their own bread and be "
                    "covered with their own clothes. The seven women are one — "
                    "the Spirit of God: spirit of wisdom and understanding, counsel "
                    "and might, knowledge and piety, fear of the Lord. Each suffers "
                    "reproach from the false wisdoms of the age."
                ),
                "english": (
                    "[[Seven women >> Bible:Isaiah 4:1]] suffer reproach and seek "
                    "the one who can take it away; they will eat their own bread "
                    "and wear their own clothes. They are one Spirit — the "
                    "[[spirit of wisdom and understanding, counsel and might, "
                    "knowledge and the fear of the Lord >> Bible:Isaiah 11:2-3]]. "
                    "Worldly wisdom heaps shame on Christ’s wisdom."
                ),
                "allusions": [
                    A("Isaiah 4:1", "seven women"),
                    A("Isaiah 11:2-3", "sevenfold Spirit"),
                    A("1 Corinthians 2:6-8", "wisdom of this age", "probable"),
                ],
            },
            {
                "section": 2,
                "title": "Not blasphemy to honor the Spirit’s gifts",
                "latin": (
                    "Nec quasi blasphemantem me lapidetis dum velim glorificare "
                    "Spiritum. Mulieres quaerentes quem adsumant apprehendent "
                    "virum — Christum — ut nomen eius invocetur super eas."
                ),
                "gloss": (
                    "Do not stone me as if blaspheming while I wish to glorify "
                    "the Spirit. The women seeking whom they may take will seize "
                    "a man — Christ — so that his name may be invoked over them."
                ),
                "english": (
                    "Do not stone the preacher for glorifying the Spirit. The "
                    "seven seek a man to take away their shame — and that man is "
                    "Jesus, whose name is invoked over every gift of the Spirit."
                ),
                "allusions": [
                    A("Isaiah 4:1", "take away our reproach"),
                    A("Acts 4:12", "name invoked", "probable"),
                ],
            },
            {
                "section": 3,
                "title": "Jesus’ name on the seven; Amen",
                "latin": (
                    "Panem nostrum manducabimus et vestimentis nostris operiemur. "
                    "Nomen sapientiae Iesus; invocetur nomen tuum super nos, "
                    "aufer opprobrium nostrum. Abstulit opprobrium Iesus. Oremus "
                    "ut septem spiritus in eo requiescant et nobis communio "
                    "harum virtutum detur in Christo Iesu, cui gloria. Amen."
                ),
                "gloss": (
                    "We will eat our bread and be covered with our clothes. The "
                    "name of wisdom is Jesus; let your name be invoked over us, "
                    "take away our reproach. Jesus took away the reproach. Let us "
                    "pray that the seven spirits rest in him and that we share "
                    "these virtues in Christ Jesus, to whom be glory. Amen."
                ),
                "english": (
                    "[[We will eat our own bread and wear our own clothes; only "
                    "let your name be called over us — take away our reproach "
                    ">> Bible:Isaiah 4:1]]. Wisdom’s name is Jesus; he truly "
                    "removed the shame. Pray that the sevenfold Spirit rest on "
                    "him and on us [[in Christ Jesus, to whom be glory "
                    ">> Bible:1 Peter 4:11]]. Amen."
                ),
                "allusions": [
                    A("Isaiah 4:1", "name over us"),
                    A("Isaiah 11:2", "Spirit rests"),
                    A("1 Peter 4:11", "glory Amen"),
                ],
            },
        ],
    },
    4: {
        "claim": "origen-isaiah-ezekiel-isa-h4-1-4-oet",
        "sections": [
            {
                "section": 1,
                "title": "God’s beginning cannot be found",
                "latin": (
                    "Impossibile est invenire principium Dei. Nusquam "
                    "comprehendis — non tu, neque aliud quidquam eorum quae "
                    "subsistunt. Solus Salvator et Spiritus sanctus, qui semper "
                    "fuerunt cum Deo, vident faciem eius; angeli vident faciem "
                    "Patris in caelis."
                ),
                "gloss": (
                    "It is impossible to find the beginning of God. Nowhere do "
                    "you comprehend — not you, nor any other of the things that "
                    "subsist. Only the Savior and the Holy Spirit, who always "
                    "were with God, see his face; the angels see the face of the "
                    "Father in the heavens."
                ),
                "english": (
                    "God’s beginning cannot be found. Creatures never grasp it. "
                    "Only the Savior and the Holy Spirit, forever with God, see "
                    "his face; and [[angels always behold the face of the Father "
                    "in heaven >> Bible:Matthew 18:10]]."
                ),
                "allusions": [
                    A("Matthew 18:10", "angels see the Father’s face"),
                    A("Isaiah 6:1-2", "throne vision context", "probable"),
                ],
            },
            {
                "section": 2,
                "title": "The whole earth full of his glory",
                "latin": (
                    "Plena omnis terra gloria eius. Olim domus plena erat gloria; "
                    "nunc omnis terra. Elevatum est superliminare a voce clamantium; "
                    "domus impleta est fumo."
                ),
                "gloss": (
                    "The whole earth is full of his glory. Once the house was full "
                    "of glory; now the whole earth. The lintel was raised by the "
                    "voice of those crying; the house was filled with smoke."
                ),
                "english": (
                    "[[The whole earth is full of his glory >> Bible:Isaiah 6:3]] — "
                    "not only the temple house. [[The thresholds shook at the voice "
                    "of those who called, and the house was filled with smoke "
                    ">> Bible:Isaiah 6:4]]."
                ),
                "allusions": [
                    A("Isaiah 6:3", "earth full of glory"),
                    A("Isaiah 6:4", "thresholds and smoke"),
                ],
            },
            {
                "section": 3,
                "title": "I saw the King, the Lord of hosts",
                "latin": (
                    "Et regem Dominum Sabaoth vidi oculis meis. Si quando de "
                    "Deo loquimur, regem videmus. Post visionem propheta dicit: "
                    "vae mihi, quia homo pollutus labiis sum."
                ),
                "gloss": (
                    "And the King, the Lord of hosts, I saw with my eyes. Whenever "
                    "we speak of God we see the King. After the vision the prophet "
                    "says: woe is me, for I am a man of unclean lips."
                ),
                "english": (
                    "[[My eyes have seen the King, the Lord of hosts "
                    ">> Bible:Isaiah 6:5]]. Vision drives confession: [[Woe is me, "
                    "for I am a man of unclean lips >> Bible:Isaiah 6:5]]."
                ),
                "allusions": [
                    A("Isaiah 6:5", "King; unclean lips"),
                ],
            },
            {
                "section": 4,
                "title": "Seraphim coal cleanses the lips",
                "latin": (
                    "Missus est ad me unus de Seraphim, et in manu eius carbo. "
                    "Tetigit labia mea et abstulit iniquitates meas. Purgatus "
                    "propheta paratus est ad ministerium. Gloria Deo. Amen."
                ),
                "gloss": (
                    "One of the Seraphim was sent to me, and in his hand a coal. "
                    "He touched my lips and took away my iniquities. The cleansed "
                    "prophet is ready for ministry. Glory to God. Amen."
                ),
                "english": (
                    "[[One of the Seraphim flew to me with a live coal "
                    ">> Bible:Isaiah 6:6]]; [[it touched my mouth; your guilt is "
                    "taken away >> Bible:Isaiah 6:7]]. Cleansed lips can preach. "
                    "Glory to God. Amen."
                ),
                "allusions": [
                    A("Isaiah 6:6-7", "coal; guilt removed"),
                ],
            },
        ],
    },
    5: {
        "claim": "origen-isaiah-ezekiel-isa-h5-1-2-oet",
        "sections": [
            {
                "section": 1,
                "title": "Who raised justice from the east?",
                "latin": (
                    "Ait prophetes esse viventem iustitiam; Apostolus dicit "
                    "Christum iustitiam et sanctificationem et redemptionem. "
                    "Quis surgere fecit ab oriente iustitiam, vocavit eam ad "
                    "pedes suos? Pater vocavit Filium — incarnationem — de "
                    "oriente lucis verae. Adoramus scabellum pedum eius."
                ),
                "gloss": (
                    "The prophet says there is living justice; the Apostle says "
                    "Christ is justice and sanctification and redemption. Who made "
                    "justice rise from the east, called it to his feet? The Father "
                    "called the Son — the incarnation — from the east of true light. "
                    "We adore the footstool of his feet."
                ),
                "english": (
                    "Isaiah already knows living Justice, not Paul alone: Christ is "
                    "[[our righteousness, sanctification, and redemption "
                    ">> Bible:1 Corinthians 1:30]]. [[Who raised up justice from "
                    "the east and called it to his feet? >> Bible:Isaiah 41:2]] — "
                    "the Father calling the Son from the true dawn. [[Worship at "
                    "his footstool, for it is holy >> Bible:Psalm 99:5]]."
                ),
                "allusions": [
                    A("Isaiah 41:2", "justice from the east"),
                    A("1 Corinthians 1:30", "Christ our righteousness"),
                    A("Psalm 99:5", "holy footstool"),
                    A("John 3:13", "descended from heaven", "probable"),
                ],
            },
            {
                "section": 2,
                "title": "Vision of the Lord after Uzziah again",
                "latin": (
                    "Et factum est anno quo mortuus est Ozias rex, vidi Dominum "
                    "sedentem supra thronum excelsum; et plena domus gloria eius. "
                    "Visio iterum aliter exponitur. Gloria Christo. Amen."
                ),
                "gloss": (
                    "And it happened in the year King Uzziah died, I saw the Lord "
                    "sitting upon a high throne; and the house was full of his "
                    "glory. The vision is expounded again otherwise. Glory to "
                    "Christ. Amen."
                ),
                "english": (
                    "Again: [[In the year King Uzziah died I saw the Lord seated "
                    "on a high throne; the house was full of his glory "
                    ">> Bible:Isaiah 6:1]]. The same vision yields fresh sense "
                    "beside Isaiah 41. Glory to Christ. Amen."
                ),
                "allusions": [
                    A("Isaiah 6:1", "Uzziah; throne vision"),
                ],
            },
        ],
    },
    6: {
        "claim": "origen-isaiah-ezekiel-isa-h6-1-3-oet",
        "sections": [
            {
                "section": 1,
                "title": "Here am I; send me — bolder than Moses",
                "latin": (
                    "Videns Isaias Dominum Sabaoth sedentem super thronum "
                    "audivit: quem mittam? Ecce sum ego, mitte me. Verecundius "
                    "Moyses: provide alium quem mittas. Isaias non exspectans "
                    "quid iuberetur ait ecce ego; ideo iubetur dicere aure "
                    "audietis et non intelligetis."
                ),
                "gloss": (
                    "Seeing the Lord of hosts seated on the throne Isaiah heard: "
                    "whom shall I send? Behold I am here, send me. Moses was more "
                    "shy: provide another whom you may send. Isaiah without waiting "
                    "what would be commanded said behold I; therefore he is ordered "
                    "to say you will hear with the ear and not understand."
                ),
                "english": (
                    "After the throne vision Isaiah answers [[Whom shall I send? "
                    "— Here am I; send me >> Bible:Isaiah 6:8]]. Moses had pleaded "
                    "[[send someone else >> Bible:Exodus 4:13]]; Isaiah volunteers "
                    "before he knows the hard word: [[hear and hear, but do not "
                    "understand >> Bible:Isaiah 6:9]]."
                ),
                "allusions": [
                    A("Isaiah 6:8", "send me"),
                    A("Exodus 4:13", "Moses declines"),
                    A("Isaiah 6:9", "hear without understanding"),
                ],
            },
            {
                "section": 2,
                "title": "Why hearing without understanding",
                "latin": (
                    "Quae causa est audientem non intelligere et videntem non "
                    "videre? Incrassatum cor, aures graves, oculi clausi — "
                    "iudicium et misericordia Dei circa populum."
                ),
                "gloss": (
                    "What is the cause that the hearer does not understand and "
                    "the seer does not see? A thickened heart, heavy ears, closed "
                    "eyes — God’s judgment and mercy concerning the people."
                ),
                "english": (
                    "Why [[see and not perceive; hear and not understand "
                    ">> Bible:Isaiah 6:9-10]]? A fat heart, dull ears, shut eyes — "
                    "judgment that still aims at healing when they turn."
                ),
                "allusions": [
                    A("Isaiah 6:9-10", "harden; heal"),
                    A("Matthew 13:14-15", "Isaiah fulfilled", "probable"),
                ],
            },
            {
                "section": 3,
                "title": "Shut eyes from harm; the Word heals",
                "latin": (
                    "Si futurum est ut aperiens oculos animae audiam turpiloquia, "
                    "melius est claudere aditus. Quando videnda sunt eloquia Dei, "
                    "convertimur et sanat nos Deus mittens verbum. Gloria Christo. "
                    "Amen."
                ),
                "gloss": (
                    "If opening the soul’s eyes I would hear foul speech, better "
                    "to shut the entrances. When God’s oracles are to be seen, we "
                    "are turned and God heals us sending the word. Glory to "
                    "Christ. Amen."
                ),
                "english": (
                    "Better to [[close the eyes lest we look on evil "
                    ">> Bible:Isaiah 33:15]] than to drink harmful talk. When we "
                    "turn to God’s words, he [[sends his word and heals "
                    ">> Bible:Psalm 107:20]] in Christ Jesus. Amen."
                ),
                "allusions": [
                    A("Isaiah 33:15", "shut eyes from evil"),
                    A("Psalm 107:20", "word heals"),
                    A("Isaiah 6:10", "turn and be healed"),
                ],
            },
        ],
    },
    7: {
        "claim": "origen-isaiah-ezekiel-isa-h7-1-3-oet",
        "sections": [
            {
                "section": 1,
                "title": "Behold I and the children God gave me",
                "latin": (
                    "Da sapienti occasionem et sapientior erit. Apostolus "
                    "recordans: ecce ego et pueri quos Deus dedit mihi — quia "
                    "pueri communicaverunt sanguini atque carni, et ipse "
                    "proximo factus est, ut per mortem destruat eum qui "
                    "imperium habet mortis."
                ),
                "gloss": (
                    "Give occasion to the wise and he will be wiser. The Apostle "
                    "recalling: behold I and the children God gave me — because "
                    "the children shared in blood and flesh, and he himself became "
                    "near, that through death he might destroy him who has the "
                    "empire of death."
                ),
                "english": (
                    "[[Give a wise man occasion and he will be wiser "
                    ">> Bible:Proverbs 9:9]]. Paul reads [[Behold, I and the "
                    "children God has given me >> Bible:Isaiah 8:18]] as "
                    "[[Hebrews 2:13-14 >> Bible:Hebrews 2:13-14]]: the children "
                    "shared flesh and blood, so the Savior shared them to destroy "
                    "the one who holds death’s power."
                ),
                "allusions": [
                    A("Proverbs 9:9", "occasion for the wise"),
                    A("Isaiah 8:18", "I and the children"),
                    A("Hebrews 2:13-14", "apostolic reading"),
                ],
            },
            {
                "section": 2,
                "title": "He shared flesh to make us his own",
                "latin": (
                    "Alienus erat a natura divina sanguinem et carnem suscipere; "
                    "propter nos ea suscepit ut domesticos nos faceret qui "
                    "alieni eramus per peccatum."
                ),
                "gloss": (
                    "It was foreign to the divine nature to take up blood and "
                    "flesh; for us he took them up to make us household members "
                    "who had become foreign through sin."
                ),
                "english": (
                    "Flesh and blood were alien to his divinity; he took what was "
                    "not his so that we who were estranged by sin might become "
                    "his household."
                ),
                "allusions": [
                    A("Hebrews 2:14", "shared flesh and blood"),
                    A("Ephesians 2:19", "household of God", "probable"),
                ],
            },
            {
                "section": 3,
                "title": "Not mediums; the Word made flesh",
                "latin": (
                    "Si dixerint quaerite ventriloquos — non est ut verbum "
                    "istud. Ecclesia dicit: verbum caro factum habitavit in "
                    "nobis; vidimus gloriam unigeniti. Verbum in principio erat "
                    "apud Deum; cui gloria. Amen."
                ),
                "gloss": (
                    "If they say seek mediums — it is not like this word. The "
                    "church says: the word became flesh and dwelt among us; we "
                    "saw the glory of the only-begotten. The word in the beginning "
                    "was with God; to whom be glory. Amen."
                ),
                "english": (
                    "If they say [[seek mediums and wizards >> Bible:Isaiah 8:19]], "
                    "answer: [[this word is not like that >> Bible:Isaiah 8:20]]. "
                    "The church holds [[the Word became flesh and dwelt among us; "
                    "we have seen his glory >> Bible:John 1:14]] — glory as of the "
                    "only Son, not Moses’ veiled face. Amen."
                ),
                "allusions": [
                    A("Isaiah 8:19-20", "mediums vs the word"),
                    A("John 1:14", "Word made flesh"),
                    A("2 Corinthians 3:13", "Moses’ veil", "probable"),
                ],
            },
        ],
    },
    8: {
        "claim": "origen-isaiah-ezekiel-isa-h8-1-2-oet",
        "sections": [
            {
                "section": 1,
                "title": "Wail, idols of Jerusalem and Samaria",
                "latin": (
                    "Olim quando peccavit populus prior, excidit a religione et "
                    "sculptilia fabricatus est Iudas in Hierusalem et Israel in "
                    "Samaria. Ululate sculptilia — iudicium super idola et "
                    "civitates habitatas."
                ),
                "gloss": (
                    "Once when the former people sinned, it fell from religion and "
                    "Judah fashioned idols in Jerusalem and Israel in Samaria. "
                    "Wail, idols — judgment upon the idols and the inhabited cities."
                ),
                "english": (
                    "When the old people fell, Judah carved idols [[in Jerusalem "
                    "and Samaria >> Bible:Isaiah 10:10-11]]. [[Wail, you idols "
                    ">> Bible:Isaiah 10:10]] — judgment shakes inhabited cities."
                ),
                "allusions": [
                    A("Isaiah 10:10-11", "idols Jerusalem/Samaria"),
                    A("Isaiah 10:14", "cities shaken", "probable"),
                ],
            },
            {
                "section": 2,
                "title": "Pride’s inflation; house on the rock",
                "latin": (
                    "Videamus inflationem eius ut eam caveamus. Stabiles "
                    "perseveremus habentes aedificium super petram Iesum "
                    "Christum, cui gloria. Amen."
                ),
                "gloss": (
                    "Let us see its inflation so that we may beware of it. Let us "
                    "persevere stable having a building upon the rock Jesus Christ, "
                    "to whom be glory. Amen."
                ),
                "english": (
                    "Beware pride’s swelling. Stand firm with a house [[built on "
                    "the rock >> Bible:Matthew 7:24]] — Jesus Christ, to whom be "
                    "glory. Amen."
                ),
                "allusions": [
                    A("Matthew 7:24-25", "house on rock"),
                    A("1 Corinthians 10:4", "rock was Christ", "probable"),
                ],
            },
        ],
    },
    9: {
        "claim": "origen-isaiah-ezekiel-isa-h9-1-2-oet",
        "sections": [
            {
                "section": 1,
                "title": "Whom shall I send? — ready, then slow",
                "latin": (
                    "Et audivi vocem Domini: quem mittam? Et dixi: ecce ego sum; "
                    "mitte me. Postquam purgatus est labiis, paratus suscepit "
                    "ministerium. Hebraeus quidam: libenter suscepit ignorans "
                    "tristia nuntianda; deinde pigrior fit cum audit aure "
                    "audietis et non intelligetis. Haec etiam de Salvatore — "
                    "audientes non audirent."
                ),
                "gloss": (
                    "And I heard the Lord’s voice: whom shall I send? And I said: "
                    "behold I am; send me. After his lips were cleansed he readily "
                    "took the ministry. A certain Hebrew: he gladly took it not "
                    "knowing the sad things to announce; then he grows slower when "
                    "he hears you will hear with the ear and not understand. These "
                    "things also of the Savior — hearers would not hear."
                ),
                "english": (
                    "[[Whom shall I send? — Here am I; send me >> Bible:Isaiah 6:8]]. "
                    "Cleansed lips volunteer; then the hard commission "
                    "[[hear and not understand >> Bible:Isaiah 6:9]] makes the "
                    "messenger slower — and foreshadows hearers who would not hear "
                    "the Savior. (Baehrens: Homilia IX conclusion lacunate in "
                    "witnesses; no invented Amen.)"
                ),
                "allusions": [
                    A("Isaiah 6:8-9", "send me; harden"),
                    A("Matthew 13:13", "hearing not hearing", "probable"),
                ],
            },
            {
                "section": 2,
                "title": "Thick heart; thin heart sees God",
                "latin": (
                    "Incrassatum est cor populi huius. Omnis in curis vitae "
                    "praesentis cor incrassatum habet; spinis enecatur. Fugiamus "
                    "terrena negotia ut attenuatum cor Deo acceptabile fiat. "
                    "Mundo corde Deum videbunt. Tria: cor incrassatum, aures "
                    "graves, oculi clausi. Soli iusti rationes creaturarum "
                    "comprehendunt — quoniam videbo caelos tuos. [Schluss fehlt "
                    "in Baehrens; non fingimus Amen.]"
                ),
                "gloss": (
                    "The heart of this people has grown thick. Everyone in present "
                    "life’s cares has a thick heart; it is choked by thorns. Let us "
                    "flee earthly business so a thinned heart may be acceptable to "
                    "God. The pure in heart will see God. Three things: thick heart, "
                    "heavy ears, closed eyes. Only the just grasp the reasons of "
                    "creatures — for I will see your heavens. [Ending lacking in "
                    "Baehrens; we do not invent Amen.]"
                ),
                "english": (
                    "[[This people’s heart has grown dull >> Bible:Isaiah 6:10]] — "
                    "cares and thorns fatten it. Flee earthly business so the heart "
                    "thins for God; [[the pure in heart shall see God "
                    ">> Bible:Matthew 5:8]]. Dull heart, heavy ears, shut eyes: "
                    "only the holy grasp creation’s reasons, saying with David "
                    "[[I will see your heavens, the work of your fingers "
                    ">> Bible:Psalm 8:3]]. Baehrens notes the ending is missing "
                    "(Jeremiah Homilia VI’s Amen wrongly appended in ABD) — we do "
                    "not invent a close."
                ),
                "allusions": [
                    A("Isaiah 6:10", "dull heart"),
                    A("Matthew 5:8", "pure in heart"),
                    A("Psalm 8:3", "I will see your heavens"),
                    A("Matthew 13:22", "cares choke", "probable"),
                ],
            },
        ],
    },
}


def main() -> None:
    prev = PREV
    which = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else sorted(HOMILIES)
    for num in which:
        h = HOMILIES[num]
        write_homily(num, h["claim"], prev, h["sections"])
        # next prev is unknown until commit; caller chains tips
        print(f"READY tip Homilia {num} claim={h['claim']} after={prev}")


if __name__ == "__main__":
    main()
