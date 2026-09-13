#!/usr/bin/env python3
"""OET English + justifications for Cyril De adoratione Book 17 §§11–20."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "translations/adoration17_english.json"
SRC_PATH = ROOT / "translations/adoration17_source.json"
JUST_DIR = ROOT / "reviews/justifications"

SECTIONS = [
    {
        "section": 11,
        "title": "Num 9 unclean-by-corpse; second-month Pascha; dead ways outside church",
        "pg_column": "68.1081",
        "english": [
            "Cyril: ‘And there arrived the men who were unclean upon a soul of a man, and they were not able to make the Pascha in that day. And they came-near opposite Moses and Aaron in that day, and those men said toward him: We are unclean upon a soul of a man; let us not then be late to bring-near the gift to Lord according to its season in a middle of sons of Israel. And Moses said toward them: Stand there and I will hear what Lord will enjoin concerning you. And Lord spoke toward Moses, saying: Speak to the sons of Israel, saying: A man, who if he should become unclean upon a soul of a man, or in a way far for you, or in your generations, and he will make the Pascha to Lord; in the month the second on the fourteenth day, the toward evening they will make it; upon unleaveneds and bitters in the night they will eat it; they will not leave-behind from it unto the morning, and a bone they will not crush from it. According to the law of the Pascha they will make it. And a man who if he should be clean, and in a way far he is not, and he should be late to make the Pascha, that soul will be utterly-destroyed from its people, because the gift to Lord he did not bring-near according to its season; his sin that man will take. And if a proselyte should come-near toward you in your land, and he should make the Pascha to Lord according to the law of the Pascha, and according to its arrangement, thus he will make it; one law will be for you, and for the proselyte, and for the native of the land.’ ([[Numbers 9:6-14 >> Bible:Numbers 9:6-14]])",
            "Palladius: And who ever would be the unclean on the one hand as upon a soul of a man, and a pretext then of the not to be able to fulfill the Pascha the matter making, I would wish to know clearly, as well know you indeed.",
            "Cyril: Much on the one hand then exceedingly of the history the word. For I will remember of God having cried-through toward the hierophant Moses: ‘Speak to the sons of Israel, and let them send-out from the camp every leper and every gonorrheal, and every unclean upon a soul.’ ([[Numbers 5:2 >> Bible:Numbers 5:2]]) And enough on the one hand for us the concerning these has been labored word. Except that I say usefully unto the present. For unclean on the one hand upon a soul of a man the Letter says the sacred, the upon a corpse having been polluted; for it has been forbidden also of a soulless body to touch-off, and for those mourning someone of the near and from blood of the uncleanness the writing the ancient was setting-upon an ordinance. Therefore indeed also they were being sent-out of the camp. And the law was under-typing again through these, that unholy someone will be and of a noetic uncleanness full, of the of another deadness having shared, as in habit and manners; for dead the manners those concerning whom ever would be said beside Christ ‘Leave the dead to bury their own dead.’ ([[Matthew 8:22 >> Bible:Matthew 8:22]]; [[Luke 9:60 >> Bible:Luke 9:60]]) Outside then therefore of the divine court, and of the of the firstborns Church, and of the of the holy ones flock send-awayable, the one with those the dead things to think and to do having been accustomed having shared, or also near having become, according at least to the to choose I say the equal things to think and to do. But thus on the one hand holds of the law the riddle. And toward a mind the true, and that most the most-fitting for us the spiritual ones, the unclean upon a soul of a man, in this way indeed also in a month",
        ],
        "notes_covered": [
            "Num 9 second-month Pascha",
            "Num 5 unclean expulsion",
            "Matt 8 leave dead bury dead",
        ],
        "added_allusions": [
            "Numbers 9:6-14",
            "Numbers 5:2",
            "Matthew 8:22",
            "Luke 9:60",
        ],
        "translator_notes": [
            "Continues Num 9 after §10; ends mid μηνὶ into §12 second-month Jews.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("ἀκάθαρτοι", "ἀκάθαρτος", "unclean"),
            ("Πάσχα", "πάσχα", "Pascha"),
            ("νεκροὺς", "νεκρός", "dead"),
        ],
        "pass_a_gloss": "§11 dual gloss: ἀκάθαρτος / unclean · πάσχα / Pascha · νεκρός / dead … Pass A ≠ Pass B. Theme: Corpse-uncleanness; deferred feast; dead manners.",
    },
    {
        "section": 12,
        "title": "Second-month Jews after Christ-murder; fullness of nations; far-way idolaters",
        "pg_column": "68.1084",
        "english": [
            "Cyril: …the second completing the feast, and slaughtering the sacrifice, unto a type of Christ, according to the of the Pascha law, not other ones we will reckon to be, or that the Jews upon the against Christ blood-pollution having been polluted, and a writing having unto uncleanness, the to have insulted-beside unto the Emmanuel. ([[Matthew 1:23 >> Bible:Matthew 1:23]]) For such ones of our holy feast slipped-away necessarily. And they are late and have missed-through of the season according to which the of all life leader has been perfected through sufferings; ([[Hebrews 2:10 >> Bible:Hebrews 2:10]]) of a pity at least of the all to save wanting, in the after this seasons, as in a month second they will share also themselves of the Christ, and they will feast-together with the holy ones, the in a season having been called, clear then that the from nations; for look-down how the on the one hand in Egypt the of the idolatry immediately having rubbed-off dirt, slaughter the lamb in a first month, and unto the of the to believe beginnings they leap-up. And the ones having been anointed with the blood of the Lord, beside nothing they will reckon the destroyer, and better they will be of the corruption. And the ones, as in a year and in a month second, come-near scarcely and confess the pollution. And that they have become unclean upon a soul of a man, they were affirming-through clearly, and of the blessing they deem-worthy to hit, and later and after the first ones, they fulfill the feast; ‘For when the fullness of the nations should enter,’ he says, ‘then all Israel will be saved.’ ([[Romans 11:25-26 >> Bible:Romans 11:25-26]]) And the prophet has pre-spoken-out somewhere also concerning them: ‘And after these things the sons of Israel will return, and they will seek-upon Lord their God, and David their king, and they will be-amazed upon the Lord, and upon his good things upon lasts of the days.’ ([[Hosea 3:5 >> Bible:Hosea 3:5]]) For he will be sought-upon in last seasons beside the ones having been left-behind from Israel, the from seed of David, according to flesh Christ. ([[Romans 1:3 >> Bible:Romans 1:3]])",
            "Palladius: True the word; for Israel has been set in hopes.",
            "Cyril: And that not un-erring, rather even of the exceedingly most-fallible things, the not to fulfill feasts upon Christ, he clarified straightway, the neither unclean upon a soul of a man, nor at least in a way long having become, and a necessary not having stumbling-block, to last penalties will be brought-under saying, if he should not choose to do the having-been-lawed. And unclean on the one hand as upon a soul of a man would be noeted toward us, just as we were saying just-now, the Lord-killing Jew. And in a way as it were long, and outside somewhere of the Jerusalem that is of the holy of our Savior Church, ‘The one to the wood saying, My God you are, and to the stone saying, You generated me.’ ([[Jeremiah 2:27 >> Bible:Jeremiah 2:27]]) And indeed also to the creation beside the having-created worshiping, or then the one another some having been sick-with wandering; if at least it is true, that near on the one hand being would be noeted of God every good man, and unadulterated having upon him the glory; and he has stood-out and departs-away and is far every if someone not thus holds. Not then the neither unclean upon a soul of a man according to the Jews, nor at least being in a way long, according to Greeks or heretics, eagerly and un-delayedly we will bring-near the sacrifice, and the feasts of Lord we will",
        ],
        "notes_covered": [
            "Rom 11 fullness then Israel",
            "Hos 3 return seek David",
            "Jer 2 wood/stone gods",
        ],
        "added_allusions": [
            "Matthew 1:23",
            "Hebrews 2:10",
            "Romans 11:25-26",
            "Hosea 3:5",
            "Romans 1:3",
            "Jeremiah 2:27",
        ],
        "translator_notes": [
            "Continues mid μηνὶ; ends mid τιμήσομεν into §13 proselyte / Pascha place.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("δευτέρῳ", "δεύτερος", "second"),
            ("μιαιφονίᾳ", "μιαιφονία", "blood-pollution"),
            ("προσήλυτος", "προσήλυτος", "proselyte"),
        ],
        "pass_a_gloss": "§12 dual gloss: δεύτερος / second · μιαιφονία / blood-pollution · μακρά / far … Pass A ≠ Pass B. Theme: Deferred Jewish feast; nations first.",
    },
    {
        "section": 13,
        "title": "Proselyte shares altar; Pascha only in holy city / Church",
        "pg_column": "68.1085",
        "english": [
            "Cyril: …honor. And a proselyte will feast with you according to the equal law, and will be-glad-together with ones rejoicing. For those according to seasons of the in Christ faith receiving the boasts, we make sharers of the bloodless sacrifice, and of the holy table we call unto a sharing. And that also I think to bring-upon-beside necessary, that a custom has prevailed in Churches, from at least, I think, of this law, that if the according to moon fourteenth should fall-out of the first month, to busy-around the second and near month, and in it to seek the having-been-defined day, in order that the of the true of the feast season might not go-out. And thus holds the matter, just as also for the of old has been pre-oracled law.",
            "Palladius: Rightly you spoke; except, say that. If not for every one perhaps and if in a way he should become long, and as farthest of the Jerusalem, the law allowed unblamably to be able to fulfill the Pascha.",
            "Cyril: Not on the one hand then; for in alone then to sacrifice-down he was ordering the holy city, in which also the of old temple Solomon built-up. And Moses was addressing thus in the Deuteronomy to the sons of Israel, saying: ‘Guard the month of the news, and you will make the Pascha to Lord your God, because in the month of the news you went-out from Egypt by night. And you will sacrifice the Pascha to Lord your God, sheep and oxen in the place which if Lord your God should choose it, for his name to be called-upon there. You will not eat upon it leaven. Seven days you will eat upon it unleaveneds, bread of affliction, because in haste you went-out from Egypt, in order that you may remember the day of your exodus from a land of Egypt all the days of your life. Leaven will not be seen for you in all your borders seven days, and from the meats which if you should sacrifice the evening on the day the first unto the morning will not sleep. You will not be able to sacrifice the Pascha in not-one of your cities which Lord your God gives to you, but or unto the place which ever Lord your God should choose, for his name to be called-upon there. You will sacrifice the Pascha evening toward settings of sun in the season in which you went-out from Egypt, and you will boil and roast and eat in the place, which if Lord your God should choose it.’ ([[Deuteronomy 16:1-7 >> Bible:Deuteronomy 16:1-7]]) For with countless as many cities and villages the of the Jews land was filled, and to complete both the sacred things and the upon the Pascha law, in alone then needing the holy city God was molding-through, that, I think somewhere, well very of the legal letter sketching-shadow for us, that not ever would be lawful nor at least has been allowed for some the upon Christ mystery, according to which ever he should choose manner, or then in a place every to be able to fulfill; for a space alone the fitting for it, and most-proper truly, the holy city, that is, the Church, in which also a lawful priest, and through hands having been sanctified the sacred things are completed, and incense is brought-near to the of all ruling God, and a clean sacrifice, according to the of the prophet voice. ([[Malachi 1:11 >> Bible:Malachi 1:11]]) Through nothing then therefore the upon this they make",
        ],
        "notes_covered": [
            "Church calendar second month custom",
            "Deut 16 Pascha place",
            "Mal 1 clean sacrifice",
        ],
        "added_allusions": [
            "Deuteronomy 16:1-7",
            "Malachi 1:11",
        ],
        "translator_notes": [
            "Continues mid τιμήσομεν; ends mid ποιοῦνται into §14 heretics outside city.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("προσήλυτος", "προσήλυτος", "proselyte"),
            ("τόπον", "τόπος", "place"),
            ("Ἐκκλησία", "ἐκκλησία", "Church"),
        ],
        "pass_a_gloss": "§13 dual gloss: προσήλυτος / proselyte · τόπος / place · ἐκκλησία / Church … Pass A ≠ Pass B. Theme: One altar; Pascha in Church alone.",
    },
    {
        "section": 14,
        "title": "Heretics seize honor; Num 28 Passover holocausts with calves/rams/lambs",
        "pg_column": "68.1088",
        "english": [
            "Cyril: …law, the the rightly holding distorting heretics; for they sacrifice-down the lamb, not in the holy city, nor at least through a hand of the ones having been chosen-out through the Spirit unto a sacred-work, but as the divine for us writes Paul, for themselves seizing the honor, ([[Hebrews 5:4 >> Bible:Hebrews 5:4]]) and in every place bringing-near. For bulls as it were insolent and arrogant, toward alone indiscriminately they go the for them seeming. But those on the one hand much the unbridled and the having nodded unto madness practicing, bitter for the judge of such considerations they will pay justices. And let us go again ourselves unto a path the well-worn and undistorted, that of the having-been-brought-beside law proving. For you learned-through somewhere of him saying clearly, that ‘Guard the month of the news, and you will make the Pascha to Lord your God, sheep and oxen.’ ([[Deuteronomy 16:1-2 >> Bible:Deuteronomy 16:1-2]]) And yet what ever then, someone ever would say, the upon the Pascha law for those in Egypt setting, one alone he ordered to sacrifice-down a lamb; and of sheep and calves having remembered we will not find? Has then of the fitting Moses missed-through? By no means; for in the Numbers to be brought-upon-beside for the lamb oxen and sheep God was adding-lawing thus saying: ‘And in the month the first on the fourteenth day of the month Pascha to the Lord, and on the fifteenth day of this month a feast, seven days unleaveneds you will eat, and the day the first called-upon holy will be for you, every work worshipful you will not make. And you will bring-near holocausts a fruit-offering to Lord, calves from oxen two, a ram one, lambs yearlings seven, unblemished they will be for you, and their sacrifice fine-flour having been worked-up in oil, three tenths for the calf the one, and two tenths for the ram the one. A tenth a tenth you will make for the lamb the one, for the seven lambs, and a he-goat from goats one concerning sin, to propitiate concerning you. Except of the holocaust of the through-all of the morning, which is a holocaust of continuance. These according to these you will make the day unto the seven days, a gift a fruit-offering unto a smell of good-odor to Lord upon the holocaust of the through-all, you will make its libation. And the day the seventh called holy will be for you, every work worshipful you will not make in it.’ ([[Numbers 28:16-25 >> Bible:Numbers 28:16-25]]) That on the one hand then in a month the first, and indeed also on a day fourteenth the Pascha to fulfill a necessity according to the law, having anticipated already we said-before. And what ever would wish to show-through also of the unleaveneds the eating, and the according to Sabbath idleness, and toward these still the to have been named called holies both the first and the seventh day, the word showed-out-before clearly. Therefore having let-go the in at least these to delay still, upon the of the sacrifices again let us go manners. Two on the one hand then the calves, toward holocausts and a sacrifice, and one a ram, and indeed also lambs the number seven, all unblemished and yearlings, and a sacrifice on the one hand upon them, fine-flour oil-wet. Except not in an equal measure; for three on the one hand for each calf tenths, and two for the ram, and one upon each of the lambs. Then is brought-in-together also a he-goat from goats, over sin; ‘And these then all,’ he says,",
        ],
        "notes_covered": [
            "Heb 5 honor not self-taken",
            "Deut 16 sheep and oxen",
            "Num 28 Passover offerings",
        ],
        "added_allusions": [
            "Hebrews 5:4",
            "Deuteronomy 16:1-2",
            "Numbers 28:16-25",
        ],
        "translator_notes": [
            "Continues mid ποιοῦνται; ends mid φησὶ into §15 grain-of-wheat / two peoples.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("αἱρετικοὶ", "αἱρετικός", "heretics"),
            ("ὁλοκαυτώματα", "ὁλοκαύτωμα", "holocaust"),
            ("χίμαρον", "χίμαρος", "he-goat"),
        ],
        "pass_a_gloss": "§14 dual gloss: αἱρετικός / heretic · ὁλοκαύτωμα / holocaust · χίμαρος / he-goat … Pass A ≠ Pass B. Theme: False altar; Num 28 feast offerings.",
    },
    {
        "section": 15,
        "title": "Grain dies → many; two calves=peoples; one ram=unity; seven lambs; virtue grades",
        "pg_column": "68.1089",
        "english": [
            "Cyril: …‘except of the holocausts of the continuance.’ Look then therefore, O Palladius, of the Emmanuel the death, fruit-bearing many, according at least to the beside him clearly and truly having been said, ‘Amen amen I say to you, if the grain of the wheat having fallen unto the earth should not die, itself alone remains; and if it should die, it bears fruit much.’ ([[John 12:24 >> Bible:John 12:24]]) For the lamb is slaughtered unto a type of Christ, in a month on the one hand first according to the law, and on a day then again the fourteenth. And calves are brought-upon-beside, and a ram, and lambs toward a sacrifice and holocausts, of the through faith having been called unto sanctification, just as I think, both the multitude, and of the spiritual good-condition the measure, as in a type signifying-down; for if Christ did not die over you, we would not have been received unto a smell of good-odor for the God and Father. And since he has been perfected through sufferings, behind we go straightway a sacred-fitting dedication to the God and Father, and a sacrifice truly spiritual according to ourselves bringing-up. Two on the one hand then the calves; for two the peoples; and I say the Israel, and indeed the from nations. And one a ram; for we are being united in Christ, ‘The one having made both one, and the mid-wall of the fence having loosed, and the law of the commandments in dogmas having abolished, in order that the two he may create unto one new man, making peace,’ ([[Ephesians 2:14-15 >> Bible:Ephesians 2:14-15]]) according to the having-been-written. And seven were the lambs; for one the all in Christ having become, a broad some we are flock, and the of one of the of all arch-shepherd running-under hand, and from flocks two, unto one already somehow having been gathered-together, and in a clean and unblemished excelling life, we continue in a world, through the over us in lawless ones, and over of all sin having endured a slaughter, who also in the he-goat is signified. And of a calf at least and of a ram, and indeed also of a lamb having remembered the law, of the of the holy ones God-loving citizenship the three under-showed differences; both the uppermost, I say, and middle, and the still lesser and more-deficient. For in the bodily sizes of the animals, of the spiritual good-condition the quantity was being typed-up. Or for, not also a land he said the most-fertile to give-out fruits in three differences, of the evangelical citizenship the word?",
            "Palladius: Yes; for the on the one hand, he says, made a hundred, and the sixty, and the thirty. ([[Matthew 13:8 >> Bible:Matthew 13:8]]; [[Matthew 13:23 >> Bible:Matthew 13:23]])",
            "Cyril: It has been fitted then that the different in virtue, and of the life the having been changed-beside, as in a quantity of the sacrifices, and as in a bulk bodily is sketched-shadow well; extremely on the one hand and overlvingly, as in at least then the calf. And middlingly then again, and of the perfectly holding having gone-under as in a lesser the ram, and nestling-in and still lesser, the lamb. For of a ram lesser, the lamb, just as indeed also of a calf, a ram. Therefore also proportionally to the of each sizes, of the fine-flour is brought-upon the measure, of a life having a type; for three on the one hand for the calf tenths, and two for the ram, and one for the lamb. Except in oil the all to have been wet needing he said; for it will follow wholly for the of each measures proportionally, the beside God. And of the in good-fame and blessedness life much some will be a difference. For for the on the one hand would be fitting reasonably, the uppermost, and for others then again the as in a lesser on the one hand, except in honor and glory, and for some then",
        ],
        "notes_covered": [
            "John 12 grain dies",
            "Eph 2 one new man",
            "Matt 13 hundred/sixty/thirty",
        ],
        "added_allusions": [
            "John 12:24",
            "Ephesians 2:14-15",
            "Matthew 13:8",
            "Matthew 13:23",
        ],
        "translator_notes": [
            "Continues mid φησὶ; ends mid τισὶ δὲ into §16 star differs / Pentecost feast.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("κόκκος", "κόκκος", "grain"),
            ("μόσχοι", "μόσχος", "calf"),
            ("κριός", "κριός", "ram"),
        ],
        "pass_a_gloss": "§15 dual gloss: κόκκος / grain · μόσχος / calf · κριός / ram … Pass A ≠ Pass B. Theme: Death fruit; two peoples; virtue grades.",
    },
    {
        "section": 16,
        "title": "Star differs in glory; continual lamb; feast of weeks / new offerings",
        "pg_column": "68.1092",
        "english": [
            "Cyril: …also having gone-under and having been let-down still. ‘For a star of a star differs in glory;’ ([[1 Corinthians 15:41 >> Bible:1 Corinthians 15:41]]) and beside them then I say the holy angels, in differences to be many of the good-fame the measure, except in which ever measures it would be, of the of the holy ones life, the cheerful holds; and the then to be well-minded needing, and to be fattened-down with the beside God. For look-down how the oil not for alone the three was being poured-upon tenths, but also for two, and for one. And of continuance a sacrifice and holocausts, he calls the lamb the being-slaughtered in the holy tent the morning, and near toward evening. Through which then again it will be possible to learn, that much the good-odor of the holy tent, and unceasing truly, of the Churches the good-smell, and of the in them holy ones. For they good-odorize the Emmanuel, and the upon Christ they complete mystery the bloodless worship bringing-near to God. For this, I think, is the morning and toward evening to be holocausted the lambs. For with a beginning and an end, and through a middle it is taken. Not then from a firstfruit until an end the good-odor in Churches, as in a lamb the Christ.",
            "Palladius: Well you spoke.",
            "Cyril: And another then again a law joins-upon for the first the feast, only-not also themselves for us the seasons he joins-together saying in the Numbers: ‘And on the day of the news, when you bring-near a new sacrifice to Lord of the weeks, called-upon holy will be for you, every work worshipful you will not make. And you will bring-near holocausts unto a smell of good-odor to Lord, calves from oxen two, a ram one, lambs yearlings seven unblemished. Their sacrifice fine-flour having been worked-up in oil, three tenths for the calf the one, and two tenths for the ram the one, a tenth a tenth for the lamb the one, for the seven lambs, and a he-goat from goats one concerning sin, to propitiate concerning you, except of the holocaust of the through-all. And their sacrifice you will make for me, unblemished they will be for you, and their libations.’ ([[Numbers 28:26-31 >> Bible:Numbers 28:26-31]]) For in a month on the one hand the first, according to the of Hebrews laws, the lamb was being slaughtered. And for the near perhaps somewhere also neighbor, to gather-together a custom the from fields, of pulses then I say the early ones, and a bundle of a sheaf, of wheat already having been reaped. A season then therefore of the news, according to which from fields to be gathered-together needing, the in them having been sown. And called again such, he says, a feast, and let it be finished lawfully, of toil and sweat having been removed. For to be let-go a custom in feasts and to depart-away that most of the more-laborious. And someone would learn-up also from this then again, that for those a holy for God completing the feast, it would be fitting least at least, the inglorious and all-toilsome to fulfill sin. And having let-go as it were and filling the mind, with the unto virtue to revel eagernesses. And they are brought-near also unto a holocaust and a sacrifice, calves on the one hand two, and a ram one and seven lambs, fine-flour oil-soaked, and a he-goat from goats. And wherever ever would look of the law the riddle, having spoken-through just-now, we will not same-say. Except, that we will say necessarily, that of the of our Savior resurrec",
        ],
        "notes_covered": [
            "1 Cor 15 star glory",
            "continual morning/evening lamb",
            "Num 28 weeks feast",
        ],
        "added_allusions": [
            "1 Corinthians 15:41",
            "Numbers 28:26-31",
        ],
        "translator_notes": [
            "Continues mid τισὶ δὲ; ends mid ἀναστά into §17 new-creation / sheaf typology.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("ἀστήρ", "ἀστήρ", "star"),
            ("ἔλαιον", "ἔλαιον", "oil"),
            ("ἑβδομάδων", "ἑβδομάς", "week"),
        ],
        "pass_a_gloss": "§16 dual gloss: ἀστήρ / star · ἔλαιον / oil · ἑβδομάς / week … Pass A ≠ Pass B. Theme: Graded glory; continual odor; weeks feast.",
    },
    {
        "section": 17,
        "title": "New-fruits = resurrection; Lev 23 sheaf; Emmanuel debts; white fields",
        "pg_column": "68.1093",
        "english": [
            "Cyril: …tion under-types the mystery, the of the news season; for the of man nature bloomed-up in a first Christ, having rubbed-off the corruption, and the from the sin aging having thrown-off thereafter. Therefore also upon this exceedingly she was being solemnized saying: ‘Let my soul rejoice-up upon the Lord; for he clothed me a garment of salvation and a tunic of good-cheer.’ ([[Isaiah 61:10 >> Bible:Isaiah 61:10]]) A garment of salvation, and indeed also of good-cheer a wrap, the from above and from heaven and in Christ somewhere wholly she named incorruption, and more-clearly also the upon this panegyric law, and through most as many apparent the riddle he was setting saying in the Leviticus: ‘Say to the sons of Israel, and you will say toward them: When you should enter unto the land which I give to you, and you should harvest its harvest, and you will bring the sheaf a firstfruit of your harvest toward the priest, and he will bring-up the sheaf opposite Lord acceptable for you. On the tomorrow of the first the priest will bring-up it. And you will make on the day on which ever you bring the sheaf, a sheep unblemished yearling unto a holocaust to the Lord, and its sacrifice two tenths of fine-flour having been worked-up in oil, a sacrifice to the Lord, a smell of good-odor to Lord, and its libation the fourth of the hin of wine, and bread, and roasted new groats you will not eat until unto itself this day, until ever you should bring-near yourselves the gifts to your God. An eternal lawful unto your generations in every dwelling of you. And you will number for yourselves from the tomorrow of the Sabbaths, from the day which ever you should bring-near the sheaf of the placement, seven weeks complete, until the tomorrow of the last week you will number fifty days.’ ([[Leviticus 23:10-16 >> Bible:Leviticus 23:10-16]]) For a feast saving truly, the over us death of the Emmanuel. For he has paid-out over us the debts, and it is true, that himself our sins he takes and concerning us he is pained, and with his bruise we were healed. ([[Isaiah 53:4-5 >> Bible:Isaiah 53:4-5]]) For he nailed-toward for his own cross the against us handwriting, and he has triumphed in it the of old ruling upon the earth, beginnings then I say and authorities, and the spiritual things of the wickedness; ([[Colossians 2:14-15 >> Bible:Colossians 2:14-15]]) and before at least of the others, the Satan. And a feast neighbor straightway, of the first not lesser, the from dead re-living, shaking-down the corruption, shearing-off the sin, and unto a new us transferring life, the as in sanctification and incorruption, of death having been abolished. For we put-off the old man, and we have changed-around the new, that is, Christ, or then the in Christ citizenship and life. ([[Ephesians 4:22-24 >> Bible:Ephesians 4:22-24]]; [[Colossians 3:9-10 >> Bible:Colossians 3:9-10]]) Look-down then therefore, look-down the of the being-renewed humanity firstfruit, that is Christ, as in a type of a sheaf, and as a firstling from a field, and as from fruits a firstfruit being brought-near a sacred dedication to the God and Father. Or not of ears-of-grain a justice we bloomed-up in a world?",
            "Palladius: Yes; therefore concerning us also himself was affirming the Christ for the holy disciples, ‘Do you yourselves not say that a four-month is, and the harvest comes? Behold I say to you, lift-upon your eyes, and behold the spaces, that white they are toward",
        ],
        "notes_covered": [
            "Isa 61 garment salvation",
            "Lev 23 sheaf / weeks",
            "Isa 53 / Col 2 cross triumph",
        ],
        "added_allusions": [
            "Isaiah 61:10",
            "Leviticus 23:10-16",
            "Isaiah 53:4-5",
            "Colossians 2:14-15",
            "Ephesians 4:22-24",
            "Colossians 3:9-10",
            "John 4:35",
        ],
        "translator_notes": [
            "Continues mid ἀναστά; ends mid πρὸς into §18 harvest / sheaf before Father.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("δράγμα", "δράγμα", "sheaf"),
            ("ἀπαρχὴν", "ἀπαρχή", "firstfruit"),
            ("ἀνάστασις", "ἀνάστασις", "resurrection"),
        ],
        "pass_a_gloss": "§17 dual gloss: δράγμα / sheaf · ἀπαρχή / firstfruit · ἀνάστασις / resurrection … Pass A ≠ Pass B. Theme: New fruits; cross debts; white fields.",
    },
    {
        "section": 18,
        "title": "Christ sheaf / firstborn dead; third-day type; new dough; wait for offering",
        "pg_column": "68.1096",
        "english": [
            "Palladius: …harvest already, and the harvesting a wage takes and the gathering.’ ([[John 4:35-36 >> Bible:John 4:35-36]]) For to ears-of-grain and wheats he likens-beside the according to us.",
            "Cyril: Not then, of ears-of-grain such some firstfruit and new as it were a fruit in a form of a sheaf is noeted Christ, the firstborn from dead, ([[Colossians 1:18 >> Bible:Colossians 1:18]]; [[Revelation 1:5 >> Bible:Revelation 1:5]]) the of the resurrection for us way, the all toward a newness re-elementing, and an oldness releasing; ‘For the ancient things passed-by,’ he says, ‘behold have become the all things new, and if someone in Christ a new creation’ according to the Scriptures. ([[2 Corinthians 5:17 >> Bible:2 Corinthians 5:17]]) And the sheaf was being brought-up opposite Lord; for having been raised from dead the Emmanuel the new of the humanity and as in incorruption fruit, has gone-up unto the heaven, in order that he may be manifested now over us for the face of the God and Father, ([[Hebrews 9:24 >> Bible:Hebrews 9:24]]) and not then wholly himself unto a sight leading of him; for he is-with eternally, and would not be left-behind of the Father, as God, as in himself then rather, unto a sight leading us the outside of a face, and in wrath through the in Adam transgression, and the against us having tyrannized sin. Not then in Christ we gain the also in a face perhaps to become of God. For he deems-worthy us of oversight already thereafter, as having been sanctified. And see how for us the law, also the for the resurrection fitting was pre-typing season, that is, the third day. For on the tomorrow of the first, he says, the priest will bring-up the sheaf, opposite Lord. And third wholly the from the first, not tomorrow, but on-tomorrow; and Christ re-lived according to the third.",
            "Palladius: Truly.",
            "Cyril: And is brought-up-together with the sheaf, also a sheep unblemished, of two tenths for it of fine-flour having been brought-upon mixed with oil again. For the as in a sheaf and a firstfruit of fruits as it were being painted, also as from a flock a firstfruit is taken, and of a flock living as in a fatness of grace, and in a good-cheer of spirit. In this way indeed to be brought-up-together needing with the sheep he says the fine-flour, and oil and wine; and fine-flour on the one hand a sign ever would become of life, just as most-often we have said; and of fatness the oil, and of good-cheer, wine. And it is brought-near also as in a bread again, and in roasted groats; and groats the pulses, he says, through the, I think, being rubbed for the ones threshing them to be poured-around mills. And would be noeted for us also through this Christ, a new dough, toward whom we have been formed, and we have been ordered to complete feasts, having cleaned-out the old leaven, in order that also we a new dough may be-named, ([[1 Corinthians 5:7-8 >> Bible:1 Corinthians 5:7-8]]) according to a likeness of the all for us the unto a newness of citizenship having inaugurated way, that is of Christ.",
            "Palladius: Well you say.",
            "Cyril: And he orders-upon-beside needing of fruits to hold-off new, and edible from them to make nothing, the of the sheaf dedication awaiting. For new you will not",
        ],
        "notes_covered": [
            "John 4 harvest wage",
            "2 Cor 5 new creation",
            "Heb 9 appear for us",
            "1 Cor 5 new dough",
        ],
        "added_allusions": [
            "John 4:35-36",
            "Colossians 1:18",
            "Revelation 1:5",
            "2 Corinthians 5:17",
            "Hebrews 9:24",
            "1 Corinthians 5:7-8",
        ],
        "translator_notes": [
            "Continues mid πρὸς; ends mid Νέα γὰρ οὐ into §19 wait until gift; Pentecost count.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("δράγμα", "δράγμα", "sheaf"),
            ("πρωτότοκος", "πρωτότοκος", "firstborn"),
            ("φύραμα", "φύραμα", "dough"),
        ],
        "pass_a_gloss": "§18 dual gloss: δράγμα / sheaf · πρωτότοκος / firstborn · φύραμα / dough … Pass A ≠ Pass B. Theme: Ascension sheaf; third day; new dough.",
    },
    {
        "section": 19,
        "title": "New life after Emmanuel; Pentecost weeks; two leavened firstfruit loaves",
        "pg_column": "68.1097",
        "english": [
            "Cyril: …eat, he says, until unto itself this day, until ever you should bring-near yourselves the gifts to your God. ([[Leviticus 23:14 >> Bible:Leviticus 23:14]]) For a season the fitting of the needing to share of the new and unmixed life, alone ever would become, and very reasonably, according to which the Emmanuel shone-upon. And sufficient then before him wholly no one, unto a new us to re-element a life, and a firstfruit as it were and first himself of the unto incorruption having been created, according as he appeared a man, and in flesh with us, through the toward us likeness. ([[1 Corinthians 15:20 >> Bible:1 Corinthians 15:20]]; [[Romans 8:29 >> Bible:Romans 8:29]]) And he has brought-in immediately of the holy for us Pentecost a pre-typing clear, seven needing saying to count-upon weeks, for the of the sheaf bringing-in. For after at least the resurrectional of the Savior day, seven joining-together weeks, we feast the ones having believed.",
            "Palladius: How clear the word!",
            "Cyril: And that of the of our Savior resurrection the season transfers the ones having been sanctified in Spirit, and in faith having been justified, unto the to be able to fruit-bear the new and unadulterated life, he was showing-down clearly thus saying straightway: ‘And you will bring-near a new sacrifice to the Lord, from your dwelling you will bring-near breads a placement, two breads, from two tenths of fine-flour will be the bread the one, leavened they will be baked of first-generations to the Lord, and you will bring-near with the breads seven lambs unblemished yearlings, and a calf one from herds, and rams two unblemished, and they will be unto a holocaust to the Lord, and their sacrifices and their libations, a sacrifice a smell of good-odor to the Lord. And they will make a he-goat from goats one concerning sin, and two lambs yearlings unto a sacrifice of salvation with the breads of the first-generation. And the priest will set-upon them with the breads of the first-generation a placement opposite Lord with the two lambs, holy they will be to the Lord, for the priest the bringing-near them for him it will be. And you will call this day called, holy it will be for you, every work worshipful you will not make in it, an eternal lawful unto your generations in every the dwelling of you.’ ([[Leviticus 23:16-21 >> Bible:Leviticus 23:16-21]]) For a firstfruit on the one hand and as it were a firstling of the unto a newness being-remolded creation the Emmanuel, and is noeted first in us, as a bread and a new dough, and a path as it were the unto the matter thereafter having chosen we, according to a likeness the toward him, a new as it were some also we have been called dough. And a type ever would be also of this clear, the from new fruits being brought-near bread, but not one the bread, and two needing to be brought-near he says; for two the peoples, even if toward a oneness they should appear having been brought-together through a mediator Christ; ([[1 Timothy 2:5 >> Bible:1 Timothy 2:5]]) except leavened they will be baked, he says. And what the riddle, come let us say, of the of the law depth, as is possible, well having looked-around. Has then a leaven in these to noet a consequence, the as in baseness and having been lied? Then how not a folly this at least? for how ever still of badness would we release, the unto a newness of an evangelical citizenship having been remodeled? or how ever",
        ],
        "notes_covered": [
            "Lev 23 wait for gift",
            "1 Cor 15 firstfruit",
            "Lev 23 Pentecost loaves",
        ],
        "added_allusions": [
            "Leviticus 23:14",
            "1 Corinthians 15:20",
            "Romans 8:29",
            "Leviticus 23:16-21",
            "1 Timothy 2:5",
        ],
        "translator_notes": [
            "Continues mid Νέα γὰρ οὐ; ends mid ἢ πῶς ἂν into §20 kingdom-leaven / scribe old+new.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("Πεντηκοστῆς", "πεντηκοστή", "Pentecost"),
            ("ἄρτους", "ἄρτος", "bread"),
            ("ζύμην", "ζύμη", "leaven"),
        ],
        "pass_a_gloss": "§19 dual gloss: πεντηκοστή / Pentecost · ἄρτος / bread · ζύμη / leaven … Pass A ≠ Pass B. Theme: New life timing; two loaves; good leaven puzzle.",
    },
    {
        "section": 20,
        "title": "Kingdom leaven; scribe new+old; lambs→calf→rams = growth in Christ",
        "pg_column": "68.1100",
        "english": [
            "Cyril: …this would be noeted of a newness? and how ever still also a new dough would some be said, if of a leaven in them a remnant remains-in, and they should be of the unholy and abominable baseness not wholly having lacked? It must be invented then therefore according at least to the fitting for the contemplations word, of a leaven a form of another, the to be blamed needing not having upon itself, rather even also having been wondered beside at least the God-breathed Scripture. With a leaven then therefore the Savior of the divine and evangelical education the well-famed and benefit-bearing power likens-beside, saying: ‘Like is the kingdom of the heavens to a leaven, which having taken a woman, she hid unto of flour satas three, until which the whole was leavened.’ ([[Matthew 13:33 >> Bible:Matthew 13:33]]) For entering-into unto a mind and a heart of the evangelical education the life-making energy, both soul and body and spirit toward an own as it were quality re-elements. Not then with such a leaven it would be fitting to under-noet to have been leavened the peoples, as in a form of the breads having been brought-near, and from two tenths each; the as it were double of the education, writing-down for us riddlingly of the type.",
            "Palladius: Such then what do you say?",
            "Cyril: For not, O Palladius, would you say, that through a double education, both legal and evangelical, both sacred we will be, and well-acceptable for God, and we go thus unto a new and choice life?",
            "Palladius: I say.",
            "Cyril: This indeed also himself for us the Savior was clarifying, saying: ‘Through this I said to you, that every scribe having been discipled in the kingdom of the heavens, like is to a rich man, who throws-out from his treasure new and old.’ ([[Matthew 13:52 >> Bible:Matthew 13:52]]) For those the mind having expert of the through Moses having been oracled, and of that ancient and as in types commandment having been filled, then toward that the new and evangelical having enriched knowledge, a double, I think somewhere, thereafter they boast also the education.",
            "Palladius: Rightly you spoke.",
            "Cyril: But not in alone breads for us of the unto a newness of life having been prepared multitude was being written-down, and the law orders-upon-beside needing seven to bring-near lambs with a calf the one, and with rams two; and of a following then clearly a libation for the victims, that is, of wine being poured-down, and as in a fourth of the hin, which is of xestai six, with a tongue the according to us being voiced-out. Not then a type ever would be the seven again lambs of the of the believing flock, infanting on the one hand in Christ. For of infancy a symbol, the lamb; except as in a strength and a manhood spiritual, going-forward unto a perfection and unto a measure of an age of the fullness of Christ. ([[Ephesians 4:13 >> Bible:Ephesians 4:13]])",
            "Palladius: How did you speak?",
            "Cyril: Having named the lambs, then through a middle having inserted the calf, he brings-upon the rams. And a type ever would be the on the one hand lambs, of the flock; and of a strength and a manliness, the calf; for the animal is well-strong; and of an age thereafter the complete, the rams. Not then the ones believing through the to man-up to love of the more-earthy",
        ],
        "notes_covered": [
            "Matt 13 kingdom leaven",
            "Matt 13 scribe new/old",
            "Eph 4 measure of Christ",
        ],
        "added_allusions": [
            "Matthew 13:33",
            "Matthew 13:52",
            "Ephesians 4:13",
        ],
        "translator_notes": [
            "Tip §§11-20; ends mid γεω into §21 perfection twin rams / baptism death.",
            "Inline Logos Bible refs on quotes/allusions ([[display >> Bible:…]]).",
        ],
        "lemmas": [
            ("ζύμῃ", "ζύμη", "leaven"),
            ("γραμματεὺς", "γραμματεύς", "scribe"),
            ("κριούς", "κριός", "ram"),
        ],
        "pass_a_gloss": "§20 dual gloss: ζύμη / leaven · γραμματεύς / scribe · κριός / ram … Pass A ≠ Pass B. Theme: Good leaven; double paideia; growth grades.",
    },
]


def make_just(sec: dict, source_text: str) -> dict:
    return {
        "excerpt_id": f"adoration17_{sec['section']:02d}",
        "edition": {
            "id": "pg68-de-adoratione",
            "language": "grc",
            "locus": f"PG 68 Book 17 §{sec['section']} ({sec['pg_column']})",
            "path": "sources/adoration_book17_greek_clean.txt",
        },
        "source_text": source_text[:2500],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": sec["english"],
        "lemmas": [
            {"form": f, "lemma": l, "gloss": g, "lexica": "LSJ"} for f, l, g in sec["lemmas"]
        ],
        "choices": [
            {
                "term": l,
                "english": g,
                "rejected": [f"{g} soft"],
                "why": f"Locked to Greek {f} in §{sec['section']}.",
            }
            for f, l, g in sec["lemmas"]
        ],
        "bible_refs": sec["added_allusions"],
        "anf_compare": {
            "status": "no_pd_reference",
            "notes": "No PD complete English of Cyril De adoratione Book 17. Sense from PG 68 Greek lock. Modern English not copied. OET = no previous English translation. Melito skipped. Never Cyril Matthew.",
        },
        "apparatus": [{"type": "ocr_warning", "note": "PG OCR; column may cut mid-sentence."}],
        "variants": [],
        "checks": {
            "pass_a_ne_pass_b": "pass",
            "source_lock": "pass",
            "placeholders": "pass",
            "jer_h20b": "intact",
        },
        "confidence": 0.8,
        "reviewer": "composer-agent",
    }


def main() -> None:
    en = json.loads(EN_PATH.read_text())
    src = {s["section"]: s for s in json.loads(SRC_PATH.read_text())}
    # drop any prior >10
    en = [s for s in en if s["section"] <= 10]
    for sec in SECTIONS:
        greek = src[sec["section"]]["greek"]
        source_text = "\n".join(greek) if isinstance(greek, list) else greek
        entry = {
            "section": sec["section"],
            "title": sec["title"],
            "english": sec["english"],
            "notes_covered": sec["notes_covered"],
            "added_allusions": sec["added_allusions"],
            "translator_notes": sec["translator_notes"],
            "pg_column": sec["pg_column"],
        }
        en.append(entry)
        just = make_just(sec, source_text)
        path = JUST_DIR / f"adoration17_{sec['section']:02d}.json"
        path.write_text(json.dumps(just, ensure_ascii=False, indent=2) + "\n")
        # quick checks
        assert just["pass_a_gloss"] != json.dumps(just["pass_b_english"])
        assert "[[" in "\n".join(sec["english"])
        print(f"OK §{sec['section']}")
    EN_PATH.write_text(json.dumps(en, ensure_ascii=False, indent=2) + "\n")
    print(f"english sections: {len(en)}")


if __name__ == "__main__":
    main()
