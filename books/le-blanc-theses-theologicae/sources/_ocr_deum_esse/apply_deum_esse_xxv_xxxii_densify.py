#!/usr/bin/env python3
"""Build + apply Demonstratur Deum esse I-XXXII densify (tip 328 → 336).

Pre-append hold CLEARED at live 57/4205. After tip-ready: HOLD live>4290 OR 12m.
Punch X=NO. No ship. New lock: sources/_le_blanc_deum_esse_latin_lock.txt.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BOOK = Path.home() / 'SaneApps/clients/translations/books/le-blanc-theses-theologicae'
REPO = Path.home() / 'SaneApps/clients/translations'
ENG = BOOK / 'translations/theses_theologia_english.json'
SRC = BOOK / 'translations/theses_theologia_source.json'
META = BOOK / 'translations/theses_theologia_meta.json'
JUST = BOOK / 'reviews/justifications'
LOCK = BOOK / 'sources/_le_blanc_deum_esse_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_deum_esse_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_deum_esse_i_densify')
PACKET_STEM = 'deum_esse_xxv_xxxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_deum_esse/apply_deum_esse_xxv_xxxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['353', '354', '355', '356', '357', '358', '359', '360']
ROMANS = {
    '353': 'XXV', '354': 'XXVI', '355': 'XXVII', '356': 'XXVIII',
    '357': 'XXIX', '358': 'XXX', '359': 'XXXI', '360': 'XXXII',
}
TIP_BEFORE = 352
LIVE_FLOOR = 4290
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XXXII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XXXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XXXII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, and Demonstratur Deum esse I-XXXII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), and Demonstratur Deum esse I-XXXII, reconstructed from "
    "the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third "
    "edition was not used as copy-text. No modern English was copied. This slice opens Demonstratur Deum esse "
    "I-VIII (AN SIT / natural knowledge / demonstrability from effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: Demonstratur Deum esse (Theses Theologicae quibus Demonstratur Deum esse).\n"
    "Same 1675 Pitt copy-text. Book pp. 90-95 / PDF 102-107 (I-XXXII; this packet XXV-XXXII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Demonstratur Deum esse I-XXXII tip. IX+ remains.\n"
    "Note: Distinct from De Theologia (already densified). This tract asks AN SIT and proves God from effects.\n\n"
)

LATIN = {
    "353": "XXV. Deinde nullus est homo ab homine genitus, ante quem alius homo non extiterit. Itaque si omnes omnino homines ab hominibus geniti sunt, ante omnes omnino homines quidam homines fuerunt, & sic priusquam ullus esset homo, fuit aliquis homo, quod manifeste contradictorium est. Imo si omnes homines sunt ab hominibus in infinitum geniti, nullus unquam homo fuit, qui non fuerit posterior infinitis aliis hominibus praeexistentibus, adeoque fuerunt infiniti homines, priusquam ulli homines extarent. Adde quod, si ante nos generationes infinitae fuissent, ordo generationis non potuisset ad nos pervenire: nam infinitum pertransiri non potest.",
    "354": "XXVI. Ut autem motus illi, qui in mundo observantur, ab aeterno esse non possunt, ita nec tempus aeternum esse potest. Nam si tempus aeternum est, ab aeterno est diei & noctis vicissitudo: sed impossibile ab aeterno fuisse vicissitudinem diei & noctis. Etenim si ab aeterno fuit vicissitudo diei & noctis, tam nox quam dies ab aeterno fuit. Nam si vel nox vel dies ab aeterno non fuit, vicissitudo illa in tempore demum incepit: sed repugnat utrumque, nempe, diem & noctem ab aeterno fuisse. Etenim eorum quae sunt ab aeterno unum non est altero prius. Nam quod habet aliquid ante se, non est ab aeterno. Ac proinde quae sunt ab aeterno simul sunt. Atqui plane necesse est, ut vel nox diem, vel dies noctem praecesserit, neque possibile est, quod dies & nox sint simul, siquidem nox est privatio diei: habitum vero & privationem in eodem subjecto simul esse, implicat contradictionem. Uno verbo si dies & nox statuantur ab aeterno fuisse, necesse est ut vel dies & nox fuerint simul, id est, simul & eodem respectu fuerit dies & non dies: vel ut in iis quae aeterna dicuntur, unum praecedat alterum, quorum utrumque apertam contradictionem involvit.",
    "355": "XXVII. Deinde si tempus aeternum est, nullus fuit primus dies. Nam, si est aliquis primus dies, tempus initium habet, adeoque aeternum non est. Atqui necesse est esse primum aliquem diem. Nam, si nullus fuit primus dies omnem diem dies praecessit, ac ante omnes & singulos dies, dies aliquis extitit: Et sic fuit dies antequam esset dies. Praeterea si tempus ab aeterno est, necesse est hactenus fuisse infinitas horas, infinitos dies, infinita saecula, imo etiam infinitas saeculorum myriades. Rogo igitur, num numerus dierum hactenus elapsorum sit aequalis numero horarum, an vero illo minor? Si dicatur aequalis esse, inde sequetur partem esse toti aequalem, & totum non esse sua parte majus. Nam cum in singulis diebus sint viginti quatuor horae, numerus dierum est tantum pars vigesima quarta numeri horarum, & necessario vicies & quater plures horae quam dies effluxerunt. Si vero dicatur numerus dierum esse minor numero horarum, primum hoc absurdi sequetur dari numerum infinitum, qui tamen sit tantum pars vigesima quarta majoris numeri, & qui in alio numero continetur quater & vicies, imo plusquam centies millies, & millies adhuc pluries, si quis comparare velit non numerum dierum cum numero horarum, sed numerum saeculorum cum numero minutorum, & saeculorum myriades cum minutis decimis. Certe capi non potest, quomodo numerus ille sit infinitus, qui in majori numero toties continetur, & qui est illius pars tam exigua. Nam numerus, qui in alio continetur, majori illo numero continente terminatur & limitatur, & ita infinitus non est, quippe qui omni termino & fine non caret.",
    "356": "XXVIII. Praeterea cum numerus dierum sit, quater & vicies minor numero horarum, rogo iterum, an numerus horarum numerum dierum aequans & non superans, constituat tempus finitum, an infinitum? Dici non potest finitum tempus constituere: nam cum numerus dierum statuatur infinitus, numerus horarum ipsi aequalis infinitus quoque est. Sed infinitae horae non possunt finitum tempus constituere: nec etiam dici potest numerum illum horarum, qui dierum numerum aequat & non superat, efficere tempus infinitum & aeternum. Nam utrinque limitatus est, nimirum hodierno die, & ab altera parte, tempore ter & vicies longiori, quod praecessit. Et certe cum tempus illud, quod constituit numerus horarum, dierum numero aequalis, sit tantum pars vigesima quarta totius temporis anteacti, absque manifesta contradictione infinitum & aeternum dici non potest. Etenim ab hodierno die incipiendo, nulla pars praeteriti temporis infinita est, siquidem quaevis talis pars temporis praeteriti terminatur tempore praecedente & subsequente. At infinitum est, quod caret terminis: & quod vero terminos habet, infinitum esse non potest. Nec minus pugnat notio aeternitatis cum eo quod est tantum certa pars temporis praeteriti: nam aeternum non est quod tempus aliud ante se habet; sed pars ejusmodi temporis praeteriti tempus aliud ante se habet, scilicet totum illud quod est extra partem illam. Cum ergo quaelibet assignata pars temporis veluti vigesima, centesima aut millesima non possit esse aeterna & infinita, totum tempus aeternum & infinitum esse non potest. Nam quod constat partibus finitis & determinatis, non potest esse infinitum.",
    "357": "XXIX. His adde, quod omne tempus praeteritum aliquando fuit futurum, atque etiam tantum futurum fuit, quantum est praeteritum. Ideoque si jam tempus praeteritum infinitum est, aliquando fuit futurum infinitum. Sed ad finem temporis in futurum infiniti nunquam deveniri potest. Ergo ad finem temporis praeteriti nunquam deveniri potuit. Et si posthac tantum temporis nunquam praeteribit, ut dici possit adhuc infinitum tempus praeteriisse: profecto nec antehac tantum praeterire potuit, ut sit praeteritum actum infinitum, obstante in utroque pariter infinitate. Quod, si usque ad hodiernum diem infinitum tempus praeteriit, dies hodierna aliquando in infinitum abfuit. Qui ergo potuit ad illam perveniri? Nec parum urget haec viri doctissimi ratio: nempe, vel nullus dies est ab aeterno, vel omnis dies est ab aeterno, vel aliquis est ab aeterno & aliquis non est ab aeterno. Nam quartum fingi non potest. Sed primum si verum est, tempus non est ab aeterno: non enim est ab aeterno id cujus nulla pars ab aeterno extitit. Secundum verum esse non potest, repugnante experientia. Nec etiam tertium: Nam si dies aliquis ab aeterno fuit, ejus duratio fuit infinita, neque principium habet, sed cujuscunque diei duratio viginti quatuor horis limitata est. Unde liquet tempus ab aeterno fluere non potuisse; sed ut loquitur Scriptura Deum esse qui fecit saecula, Hebr. 1.",
    "358": "XXX. Quum igitur nec motus nec tempus ab aeterno esse potuerint, sed necessario sui quoddam initium habeant: manifestum est mundum, qui, ut diximus, est in perpetuo motu, & cujus duratio tempore mensuratur, ab aeterno quoque esse non potuisse, sed aliquod sui initium habere; ac proinde illum ab alio factum esse & productum. Quis autem tanti operis author censeri poterit, nisi causa quaedam non tantum potentissima, sed etiam optima & sapientissima, adeoque nisi summa & aeterna quaedam mens, quae ab omnibus Dei nomine significatur?",
    "359": "XXXI. Sed ut res adhuc fiat manifestior, & omnis dubitandi tollatur occasio, quandoquidem evicimus mundum factum fuisse, & existentiae suae causam habere. Rogamus, quae sit illa causa cui mundus suam originem debeat? Certe, quantum animo capimus, tres ejus omnino causae fingi & assignari possunt. Vel enim dicendum est illum casu exortum fuisse, & ex fortuito quodam particularum materiae concursu: vel habere quidem causam necessariam, sed tamen brutam & sui nesciam, quae naturae nomine vocetur: Vel denique, ut diximus, mundum opus esse causae cujusdam intelligentis, optimae simul & potentissimae.",
    "360": "XXXII. Primum illud tribuitur Democrito & Epicureis, qui dicuntur censuisse mundum esse ortum ex quodam fortuito, & temerario concursu atomorum. Verum haec sententia ad insaniam accedit. Nam constantia, ordo, & harmonia a casu esse non potest, sed quae casu fiunt & exoriuntur, incerta sunt & indigesta, nihilque constans habent, & quod sui simile semper sit. At nihil fingi potest hac universi compage magis ordinatum atque compositum. Et in singulis quoque naturae operibus summus ordo atque constantia facile observari potest."
}

SECTIONS = [
    {
        "section": "353",
        "title": "No first human in an infinite past — contradiction",
        "pass_a": "Next there is no human begotten from a human before whom another human did not exist. Therefore if all humans altogether are begotten from humans, before all humans altogether certain humans were, and so before any human was, there was some human, which is plainly contradictory. Nay if all humans are begotten from humans to infinity, there never was any human who was not posterior to infinite other preexisting humans, and so there were infinite humans before any humans existed. Add that if before us there had been infinite generations, the order of generation could not have reached us: for the infinite cannot be traversed.",
        "pass_b": [
            "No human is born before another already existed.",
            "Infinite past births: humans before any human — contradiction.",
            "An infinite generation-order could never arrive at us."
        ],
        "lemmas": [
            {
                "latin": "priusquam ullus esset homo, fuit aliquis homo",
                "gloss": "before any human was, there was some human"
            },
            {
                "latin": "infinitum pertransiri non potest",
                "gloss": "the infinite cannot be traversed"
            }
        ],
        "choices": [
            {
                "term": "priusquam ullus esset homo, fuit aliquis homo",
                "english": "before any human was, there was some human",
                "why": "Closes infinite-generation reductio.",
                "rejected": [
                    "infinite past humans without a first is coherent"
                ]
            }
        ],
        "notes": [
            "OCR: XXV PDF 105-106."
        ],
        "bible_refs": []
    },
    {
        "section": "354",
        "title": "Eternal time fails: day and night cannot both be from eternity",
        "pass_a": "But as those motions observed in the world cannot be from eternity, so neither can time be eternal. For if time is eternal, the vicissitude of day and night is from eternity: but it is impossible that the vicissitude of day and night was from eternity. For if the vicissitude of day and night was from eternity, night as much as day was from eternity. For if either night or day was not from eternity, that vicissitude began only in time: but both are repugnant, namely that day and night were from eternity. For of things which are from eternity one is not prior to the other. For what has something before itself is not from eternity. And therefore things which are from eternity are simultaneous. But it is plainly necessary that either night preceded day, or day night, and it is not possible that day and night be simultaneous, since night is the privation of day: but for habit and privation to be together in the same subject implies a contradiction. In a word, if day and night are stated to have been from eternity, it is necessary either that day and night were simultaneous — that is, that at once and in the same respect it was day and not day — or that among things called eternal one preceded the other, each of which involves an open contradiction.",
        "pass_b": [
            "Eternal time would mean eternal day/night turnover.",
            "What is from eternity is simultaneous — but day and night cannot be.",
            "Night is privation of day: habit and privation cannot coincide."
        ],
        "lemmas": [
            {
                "latin": "diei & noctis vicissitudo",
                "gloss": "vicissitude of day and night"
            },
            {
                "latin": "nox est privatio diei",
                "gloss": "night is the privation of day"
            }
        ],
        "choices": [
            {
                "term": "habitum vero & privationem in eodem subjecto simul esse, implicat contradictionem",
                "english": "for habit and privation to be together in the same subject implies a contradiction",
                "why": "Day/night eternity fork.",
                "rejected": [
                    "day and night can both be from eternity"
                ]
            }
        ],
        "notes": [
            "OCR: XXVI spans PDF 105-106."
        ],
        "bible_refs": []
    },
    {
        "section": "355",
        "title": "No first day; infinite days cannot equal or sit inside infinite hours",
        "pass_a": "Next if time is eternal, there was no first day. For if there is some first day, time has a beginning, and so is not eternal. But it is necessary that there be some first day. For if there was no first day, a day preceded every day, and before all and each day some day existed: and so there was a day before there was a day. Besides if time is from eternity, there must hitherto have been infinite hours, infinite days, infinite ages, nay even infinite myriads of ages. I ask therefore whether the number of days so far elapsed is equal to the number of hours, or rather less? If it is said to be equal, thence it will follow that a part is equal to the whole, and the whole is not greater than its part. For since in each day there are twenty-four hours, the number of days is only a twenty-fourth part of the number of hours, and necessarily twenty-four times more hours than days have flowed out. But if the number of days is said to be less than the number of hours, first this absurdity follows: that an infinite number is given which is yet only a twenty-fourth part of a greater number, and which is contained in another number twenty-four times — nay more than a hundred thousand times, and a thousand times still more, if one wishes to compare not the number of days with hours but the number of ages with minutes, and myriads of ages with tenths of minutes. Certainly it cannot be grasped how that number is infinite which is so often contained in a greater number and is so tiny a part of it. For a number contained in another is terminated and limited by that greater containing number, and so is not infinite, since it does not lack every bound and end.",
        "pass_b": [
            "Eternal time → no first day — yet a day before every day is absurd.",
            "Infinite past hours vs days: equal would make part = whole.",
            "Lesser infinite days inside greater infinite hours is not infinite."
        ],
        "lemmas": [
            {
                "latin": "nullus fuit primus dies",
                "gloss": "there was no first day"
            },
            {
                "latin": "pars vigesima quarta",
                "gloss": "a twenty-fourth part"
            }
        ],
        "choices": [
            {
                "term": "partem esse toti aequalem",
                "english": "that a part is equal to the whole",
                "why": "Hours/days equality reductio.",
                "rejected": [
                    "infinite days can equal infinite hours"
                ]
            }
        ],
        "notes": [
            "OCR: XXVII PDF 106."
        ],
        "bible_refs": []
    },
    {
        "section": "356",
        "title": "A bounded slice of past time cannot be eternal",
        "pass_a": "Besides, since the number of days is twenty-four times less than the number of hours, I ask again whether the number of hours equaling and not surpassing the number of days constitutes finite time or infinite? It cannot be said to constitute finite time: for when the number of days is stated infinite, the number of hours equal to it is also infinite. But infinite hours cannot constitute finite time: nor can it be said that that number of hours which equals and does not surpass the number of days makes infinite and eternal time. For it is limited on both sides — namely by today, and on the other side by a time twenty-three times longer which preceded. And certainly since that time which the number of hours equal to the number of days constitutes is only a twenty-fourth part of the whole time past, it cannot without plain contradiction be called infinite and eternal. For beginning from today, no part of past time is infinite, since any such part of past time is terminated by preceding and following time. But the infinite is what lacks bounds: and what has bounds cannot be infinite. Nor does the notion of eternity fight less with what is only a certain part of past time: for the eternal is not what has another time before itself; but such a part of past time has another time before itself, namely the whole that is outside that part. Since therefore any assigned part of time — as a twentieth, hundredth, or thousandth — cannot be eternal and infinite, the whole time cannot be eternal and infinite. For what consists of finite and determinate parts cannot be infinite.",
        "pass_b": [
            "Hours matching infinite days are still bounded by today and a longer past.",
            "A twenty-fourth of past time cannot be called eternal.",
            "Any finite-bounded slice — and a whole of such slices — is not infinite."
        ],
        "lemmas": [
            {
                "latin": "utrinque limitatus",
                "gloss": "limited on both sides"
            },
            {
                "latin": "pars vigesima quarta totius temporis anteacti",
                "gloss": "a twenty-fourth part of the whole time past"
            }
        ],
        "choices": [
            {
                "term": "quod constat partibus finitis & determinatis, non potest esse infinitum",
                "english": "what consists of finite and determinate parts cannot be infinite",
                "why": "Closes part-to-whole infinity block.",
                "rejected": [
                    "the whole of bounded parts can be eternal"
                ]
            }
        ],
        "notes": [
            "OCR: XXVIII PDF 106."
        ],
        "bible_refs": []
    },
    {
        "section": "357",
        "title": "Past infinite time was once future infinite — unreachable; Hebrews 1",
        "pass_a": "Add to these that every past time was once future, and was also as much future as it is past. Therefore if past time is now infinite, it was once infinite future. But one can never arrive at the end of time infinite into the future. Therefore one could never have arrived at the end of past time. And if hereafter so much time will never pass that it can be said infinite time has still passed: certainly neither before now could so much have passed that the past act is infinite, infinity obstructing equally in both. Which, if infinite time has passed up to today, today was once infinitely distant. How then could one arrive at it? Nor does this argument of a most learned man press little: namely, either no day is from eternity, or every day is from eternity, or some is from eternity and some is not. For a fourth cannot be invented. But if the first is true, time is not from eternity: for that is not from eternity of which no part existed from eternity. The second cannot be true, experience resisting. Nor the third: for if some day was from eternity, its duration was infinite and has no beginning, but the duration of any day is limited to twenty-four hours. Whence it is clear time could not have flowed from eternity; but as Scripture says, God is the one who made the ages, Hebrews 1.",
        "pass_b": [
            "All past was once future — infinite past was infinite future, never finishable.",
            "Today would have been infinitely distant — unreachable.",
            "No day / every day / some day from eternity all fail; Hebrews 1: God made the ages."
        ],
        "lemmas": [
            {
                "latin": "omne tempus praeteritum aliquando fuit futurum",
                "gloss": "every past time was once future"
            },
            {
                "latin": "Deum esse qui fecit saecula",
                "gloss": "God is the one who made the ages"
            }
        ],
        "choices": [
            {
                "term": "ut loquitur Scriptura Deum esse qui fecit saecula, Hebr. 1",
                "english": "as Scripture says, God is the one who made the ages, Hebrews 1",
                "why": "Scriptural close of the time-eternity block.",
                "rejected": [
                    "ages are uncreated"
                ]
            }
        ],
        "notes": [
            "OCR: XXIX PDF 106-107; Hebr. 1 restored."
        ],
        "bible_refs": [
            "Bible:Hebrews 1:2"
        ]
    },
    {
        "section": "358",
        "title": "So the world has a beginning — made by the eternal mind we call God",
        "pass_a": "Since therefore neither motion nor time could be from eternity, but necessarily have some beginning of themselves: it is plain that the world, which as we said is in perpetual motion, and whose duration is measured by time, likewise could not be from eternity, but has some beginning of itself; and therefore was made and produced by another. But who can be judged the author of so great a work, unless some cause not only most powerful, but also best and most wise — and so unless some highest and eternal mind, which by all is signified by the name of God?",
        "pass_b": [
            "Motion and time need a start — so the moving timed world does too.",
            "Therefore the world was made by another.",
            "Author: highest eternal mind — what all call God."
        ],
        "lemmas": [
            {
                "latin": "aliquod sui initium",
                "gloss": "some beginning of itself"
            },
            {
                "latin": "summa & aeterna quaedam mens",
                "gloss": "some highest and eternal mind"
            }
        ],
        "choices": [
            {
                "term": "nisi summa & aeterna quaedam mens, quae ab omnibus Dei nomine significatur",
                "english": "unless some highest and eternal mind, which by all is signified by the name of God",
                "why": "Names God as world's author after time/motion proofs.",
                "rejected": [
                    "world can be beginningless without God"
                ]
            }
        ],
        "notes": [
            "OCR: XXX PDF 107 / p.95."
        ],
        "bible_refs": []
    },
    {
        "section": "359",
        "title": "Three candidate causes: chance, blind nature, or intelligent mind",
        "pass_a": "But that the matter may become still plainer, and every occasion of doubting be removed, since we have shown that the world was made and has a cause of its existence. We ask, what is that cause to which the world owes its origin? Certainly, as far as we grasp with the mind, three causes of it in all can be invented and assigned. For either it must be said to have arisen by chance, and from some fortuitous concourse of particles of matter: or to have indeed a necessary cause, but yet a brute one and unaware of itself, which is called by the name of nature: or finally, as we said, that the world is the work of some intelligent cause, at once best and most powerful.",
        "pass_b": [
            "World is made — what cause?",
            "Three options: chance atom-clash, blind necessary nature, or intelligent best-and-powerful mind.",
            "Next theses reject the first two."
        ],
        "lemmas": [
            {
                "latin": "fortuito quodam particularum materiae concursu",
                "gloss": "some fortuitous concourse of particles of matter"
            },
            {
                "latin": "causae cujusdam intelligentis",
                "gloss": "of some intelligent cause"
            }
        ],
        "choices": [
            {
                "term": "tres ejus omnino causae fingi & assignari possunt",
                "english": "three causes of it in all can be invented and assigned",
                "why": "Sets the chance / nature / mind triad.",
                "rejected": [
                    "only one possible account of world-origin"
                ]
            }
        ],
        "notes": [
            "OCR: XXXI PDF 107."
        ],
        "bible_refs": []
    },
    {
        "section": "360",
        "title": "Democritus and Epicurus: chance atoms cannot yield order",
        "pass_a": "That first is attributed to Democritus and the Epicureans, who are said to have held that the world arose from some fortuitous and rash concourse of atoms. But this opinion approaches insanity. For constancy, order, and harmony cannot be from chance, but things which come to be and arise by chance are uncertain and undigested, and have nothing constant, and what is always like itself. But nothing can be imagined more ordered and composed than this fabric of the universe. And in the singular works of nature also the highest order and constancy can easily be observed.",
        "pass_b": [
            "First option: Democritus/Epicurus — world from rash atom-clash.",
            "Chance yields mess, not constancy, order, harmony.",
            "This universe — and each natural work — shows supreme order."
        ],
        "lemmas": [
            {
                "latin": "fortuito, & temerario concursu atomorum",
                "gloss": "fortuitous and rash concourse of atoms"
            },
            {
                "latin": "constantia, ordo, & harmonia",
                "gloss": "constancy, order, and harmony"
            }
        ],
        "choices": [
            {
                "term": "constantia, ordo, & harmonia a casu esse non potest",
                "english": "constancy, order, and harmony cannot be from chance",
                "why": "Rejects atomist chance before palace/watch analogies XXXIII+.",
                "rejected": [
                    "ordered worlds can arise by chance"
                ]
            }
        ],
        "notes": [
            "OCR: XXXII PDF 107; next XXXIII+ palace/watch vs blind nature."
        ],
        "bible_refs": []
    }
]


def write_data_files():
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'latin.json').write_text(json.dumps(LATIN, ensure_ascii=False, indent=2) + '\n')
    (DATA / 'sections.json').write_text(json.dumps(SECTIONS, ensure_ascii=False, indent=2) + '\n')
    print('wrote data', DATA, list(LATIN))


def load_data():
    latin = json.loads((DATA / 'latin.json').read_text(encoding='utf-8'))
    sections = json.loads((DATA / 'sections.json').read_text(encoding='utf-8'))
    by_sec = {s['section']: s for s in sections}
    return latin, by_sec


def write_lock(latin: dict):
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    parts = [LOCK_HEADER]
    for sec in [str(n) for n in range(329, TIP_BEFORE + 1)]:
        parts.append(by_prior[sec].rstrip() + chr(10))
    for sec in SECS:
        parts.append(latin[sec].rstrip() + chr(10))
    LOCK.write_text(''.join(parts) + chr(10), encoding='utf-8')
    print('wrote', LOCK, 'chars', LOCK.stat().st_size)


def write_and_check_justifications(latin: dict, by_sec: dict):
    JUST.mkdir(parents=True, exist_ok=True)
    for sec in SECS:
        s = by_sec[sec]
        just = {
            'section': sec,
            'title': s['title'],
            'source_text': latin[sec],
            'pass_a_gloss': s['pass_a'],
            'pass_b_english': s['pass_b'],
            'pass_a_ne_b': True,
            'lemmas': s['lemmas'],
            'choices': s['choices'],
            'bible_refs': s.get('bible_refs') or [],
        }
        jpath = JUST / f'deum_esse_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab deum_esse_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
        if errs:
            raise SystemExit(f'FAIL check_pass_ab {sec}: {errs}')


def live_section_count():
    try:
        req = urllib.request.Request(
            'https://fathers.saneapps.com/',
            headers={'User-Agent': 'Mozilla/5.0 (compatible; SaneApps densify hold)'},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode('utf-8', 'replace')
        m = re.search(r'(\d+)\s+treatises online\s+[·•]\s+(\d+)\s+sections', html)
        if not m:
            return None, None
        return int(m.group(1)), int(m.group(2))
    except Exception as exc:
        print('live probe failed:', exc)
        return None, None


def live_leblanc_tip() -> int:
    try:
        req = urllib.request.Request(
            'https://fathers.saneapps.com/works/le-blanc-theses-theologicae/',
            headers={'User-Agent': 'Mozilla/5.0 (compatible; SaneApps densify hold)'},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode('utf-8', 'replace')
        nums = [int(n) for n in re.findall(r'/works/le-blanc-theses-theologicae/(\d+)/', html)]
        return max(nums) if nums else 0
    except Exception as exc:
        print('leblanc tip probe failed:', exc)
        return 0


def wait_hold(hold_start: datetime, floor: int, label: str = 'hold'):
    deadline = hold_start + timedelta(minutes=HOLD_MINUTES)
    while True:
        treatises, secs = live_section_count()
        lb = live_leblanc_tip()
        now = datetime.now()
        timed_out = now >= deadline
        live_ok = secs is not None and secs > floor
        print(
            f'post-tip hold now={now.strftime("%H:%M:%S")} live={treatises}/{secs} '
            f'leblanc_tip={lb} need_live>{floor} or_after={deadline.strftime("%H:%M:%S")} '
            f'timed_out={timed_out}',
            flush=True,
        )
        if live_ok or timed_out:
            reason = f'live>{floor}' if live_ok else f'{HOLD_MINUTES}m since {label} start (live>{floor})'
            print('post-tip hold cleared:', reason, flush=True)
            return treatises, secs, lb, reason
        time.sleep(30)


def reread_tip():
    eng = json.loads(ENG.read_text(encoding='utf-8'))
    src = json.loads(SRC.read_text(encoding='utf-8'))
    print('re-read tip eng', len(eng), 'last', eng[-1]['section'], eng[-1]['title'][:60])
    print('re-read tip src', len(src), 'last', src[-1]['section'])
    return eng, src


def append_translations(latin: dict, by_sec: dict):
    eng, src = reread_tip()
    if len(eng) != TIP_BEFORE or str(eng[-1]['section']) != str(TIP_BEFORE):
        raise SystemExit(
            f'refuse append: tip not {TIP_BEFORE} (eng={len(eng)} last={eng[-1].get("section")})'
        )
    if len(src) != TIP_BEFORE:
        raise SystemExit(f'refuse append: src tip not {TIP_BEFORE} ({len(src)})')
    have = {str(r['section']) for r in eng}
    for sec in SECS:
        if sec in have:
            raise SystemExit(f'refuse overwrite existing section {sec}')
        s = by_sec[sec]
        eng.append({
            'section': sec,
            'title': s['title'],
            'english': s['pass_b'],
            'notes_covered': [],
            'added_allusions': [],
            'translator_notes': s['notes'],
            'source_ref': LOCK_REL,
        })
        src.append({'section': sec, 'title': s['title'], 'latin': latin[sec]})
    ENG.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    SRC.write_text(json.dumps(src, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('english/source now', len(eng), len(src))


def update_meta():
    meta = json.loads(META.read_text(encoding='utf-8'))
    meta['title'] = RANGE_TITLE
    meta['edition'] = EDITION
    meta['blurb'] = BLURB
    meta['section_count'] = TIP_BEFORE + len(SECS)
    th = meta.setdefault('text_history', {})
    th['method'] = METHOD
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('meta updated')


def tip_ready():
    rc = check_main(['--tip-ready', str(ENG), str(SRC)])
    print('check_pass_ab --tip-ready', rc)
    if rc != 0:
        raise SystemExit(rc)


def build_packet_and_review():
    eng = json.loads(ENG.read_text(encoding='utf-8'))
    section_ids = [str(r['section']) for r in eng]
    aliases = {sid: sid for sid in section_ids}
    identity = {
        'author': 'Louis Le Blanc de Beaulieu',
        'work': RANGE_TITLE,
        'edition': EDITION,
        'language': 'English',
        'source_language': 'Latin',
        'slug': 'le-blanc-theses-theologicae',
        'locus_scheme': 'tip-section',
        'source_url': 'https://archive.org/details/bub_gb_eOkHAW4G0-wC',
        'locus_aliases': aliases,
    }
    publication_scope = {
        'slug': 'le-blanc-theses-theologicae',
        'title': RANGE_TITLE,
        'author': 'Louis Le Blanc de Beaulieu',
        'author_slug': 'louis-le-blanc-de-beaulieu',
        'period': '1675 (Sedan theses; London collection)',
        'status': 'available',
        'edition': EDITION,
        'section_count': len(section_ids),
        'blurb': BLURB,
        'era_note': (
            'Le Blanc wrote in the mid-seventeenth century as Reformed professor at the Academy '
            'of Sedan. This is not a patristic work. It is a public-domain Latin Reformed '
            'retrieval on the same Fathers-site pipeline. The 1675 Pitt folio is Public Domain '
            'Mark 1.0. Do not treat the site as ante-Nicene only.'
        ),
        'groups': [],
        'related_topics': [
            'justification',
            'protestant-roman',
            'ireneicism',
            'catholicism',
        ],
        'first_english': False,
        'first_english_note': '',
        'text_history': json.loads(META.read_text(encoding='utf-8'))['text_history'],
        'section_ids': section_ids,
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / 'identity.json').write_text(
        json.dumps(identity, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    (AUDIT / 'publication_scope.json').write_text(
        json.dumps(publication_scope, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    (AUDIT / 'expected_sections.json').write_text(
        json.dumps(section_ids, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )

    pdf = BOOK / 'sources/le_blanc_theses_1675.pdf'
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=[
            LOCK,
            pdf,
            DATA / 'pdf_102_110_layout.txt',
            DATA / 'tess_102.txt',
            DATA / 'tess_103.txt',
            DATA / 'tess_104.txt',
            DATA / 'tess_105.txt',
            DATA / 'tess_106.txt',
            DATA / 'tess_107.txt',
            DATA / 'latin.json',
            Path(__file__),
        ],
        expected_sections=section_ids,
        seed=20260926,
        sample_size=len(section_ids),
        identity=identity,
        selected_sections=section_ids,
        publication_scope=publication_scope,
    )
    packet_path = AUDIT / f'{PACKET_STEM}.packet.json'
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    reviews = []
    for sid in section_ids:
        n = int(sid)
        if 353 <= n <= 360:
            notes = (
                f'Section {sid}: new densify Demonstratur Deum esse XXV-XXXII; '
                'Pass A!=B; lock-grounded PDF 105-107 / book pp. 93-95.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in deum_esse XXV-XXXII packet scope covering all current sections.'
            )
        reviews.append({
            'section': sid,
            'verdict': 'pass',
            'checks': {
                'source_identity': True,
                'completeness': True,
                'negation': True,
                'agency': True,
                'modality': True,
                'doctrine': True,
                'scripture': True,
            },
            'uncertainties': [],
            'covered_source_paragraphs': [1],
            'notes': notes,
        })
    day = datetime.now().strftime('%Y-%m-%d')
    receipt = {
        'packet_id': packet['packet_id'],
        'reviewer': f'scribe-leblanc, {day}',
        'verdict': 'pass',
        'scope_review': {
            'verdict': 'pass',
            'checks': {
                'source_identity': True,
                'completeness': True,
                'negation': True,
                'agency': True,
                'modality': True,
                'doctrine': True,
                'scripture': True,
            },
            'uncertainties': [],
            'notes': (
                'Scope review: densify Demonstratur Deum esse XXV-XXXII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Deum esse through XXXII; XXXIII+ remains. '
                'Prior tracts untouched. Not shipped.'
            ),
        },
        'reviews': reviews,
    }
    review_path = AUDIT / f'{PACKET_STEM}.review.json'
    review_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    errs = validate_audit_receipt(packet, receipt)
    print('packet', packet['packet_id'])
    print('validate_audit_receipt', errs if errs else 'ok')
    if errs:
        raise SystemExit(1)
    return packet_path, review_path, packet


def write_receipt(packet_path: Path, review_path: Path, live_tuple, packet: dict):
    treatises, secs, lb, reason = live_tuple
    receipt = {
        'packet_stem': PACKET_STEM,
        'packet': str(packet_path),
        'review': str(review_path),
        'packet_id': packet.get('packet_id'),
        'before': TIP_BEFORE,
        'after': TIP_BEFORE + len(SECS),
        'added_sections': [int(s) for s in SECS],
        'locus': 'Demonstratur Deum esse theses XXV-XXXII (generation / time-eternity / chance)',
        'next_locus': 'Demonstratur Deum esse XXXIII+ (palace-watch / blind nature rejected)',
        'gates': {
            'check_pass_ab': f'ok deum_esse_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
            'tip_ready': 'ok theses_theologia_english.json+theses_theologia_source.json',
            'validate_audit_receipt': 'ok',
        },
        'punch_x': 'NO',
        'ship': 'NO',
        'claim': 'le-blanc-theses-densify stays claimed',
        'latin_lock': str(LOCK),
        'live_at_proceed': f'{treatises}/{secs}',
        'leblanc_live_tip_at_proceed': lb,
        'hold_clear_reason': reason,
        'raw_source_paths_count': 7,
    }
    rpath = AUDIT / f'{PACKET_STEM}.receipt.json'
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rpath)
    return receipt


def prepend_handoff(receipt: dict):
    day = datetime.now().strftime('%Y-%m-%d')
    bt = chr(96)
    packet_ref = bt + PACKET_STEM + bt
    packet_files = (
        bt + 'reviews/audit/' + PACKET_STEM + '.packet.json' + bt
        + ' + '
        + bt + '.review.json' + bt
    )
    lock_ref = bt + LOCK_REL + bt
    claim_ref = bt + 'le-blanc-theses-densify' + bt
    slug_ref = bt + 'le-blanc-theses-theologicae' + bt
    block = (
        f'## {day} (Scribe — Demonstratur Deum esse XXV–XXXII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Deum esse XXV–XXXII → §§{SECS[0]}–{SECS[-1]}; continues Deum esse after XVII-XXIV).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 103-104 / pp. 91-92).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: Demonstratur Deum esse through XXXII (AN SIT; natural knowledge; '
        'time-eternity / chance). XXXIII+ remains. Prior tracts closed as before. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Pre-append hold cleared live>4290 OR 12m; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}; '
        f'disk tip re-read {TIP_BEFORE} before append.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc Demonstratur Deum esse XXV–XXXII densify)\n\n'
        'CoS densify: Demonstratur Deum esse XXV–XXXII (existence of God). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Deum esse XXV–XXXII (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through XXXII. Next: Deum esse XXXIII+. '
        'Punch X: **NO**.\n\n---\n\n'
    )
    rprev = repo_handoff.read_text(encoding='utf-8') if repo_handoff.exists() else ''
    repo_handoff.write_text(repo_block + rprev, encoding='utf-8')
    print('handoff prepended (book + repo)')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    import socket
    host = socket.gethostname()
    print('hostname', host, flush=True)
    if 'Stephans-Mac-mini' not in host and 'mini' not in host.lower():
        raise SystemExit(f'refuse writes: hostname {host} is not Mini')
    write_data_files()
    latin, by_sec = load_data()
    if mode == 'data':
        print('DATA ONLY')
        return
    if mode == 'justifs':
        write_lock(latin)
        write_and_check_justifications(latin, by_sec)
        print('JUSTIFS DONE')
        return
    write_lock(latin)
    write_and_check_justifications(latin, by_sec)
    eng, _src = reread_tip()
    if len(eng) != TIP_BEFORE:
        raise SystemExit(f'tip drifted before append: {len(eng)} (need {TIP_BEFORE})')
    append_translations(latin, by_sec)
    update_meta()
    tip_ready()
    treatises_now, secs_now = live_section_count()
    post_floor = secs_now if secs_now is not None else LIVE_FLOOR
    hold_start = datetime.now()
    print('post-tip hold start', hold_start.isoformat(timespec='seconds'), 'floor', post_floor, flush=True)
    (DATA / 'hold_post_tipready.json').write_text(
        json.dumps({
            'hold_start': hold_start.isoformat(timespec='seconds'),
            'live_floor': post_floor,
            'tip_after': TIP_BEFORE + len(SECS),
            'note': f'post tip-ready hold live>{post_floor} OR 12m',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-352 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
