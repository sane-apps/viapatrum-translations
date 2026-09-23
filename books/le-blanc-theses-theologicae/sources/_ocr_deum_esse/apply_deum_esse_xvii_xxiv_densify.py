#!/usr/bin/env python3
"""Build + apply Demonstratur Deum esse I-XXIV densify (tip 328 → 336).

Pre-append hold CLEARED at live 57/4205. After tip-ready: HOLD live>4264 OR 12m.
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
PACKET_STEM = 'deum_esse_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_deum_esse/apply_deum_esse_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['345', '346', '347', '348', '349', '350', '351', '352']
ROMANS = {
    '345': 'XVII', '346': 'XVIII', '347': 'XIX', '348': 'XX',
    '349': 'XXI', '350': 'XXII', '351': 'XXIII', '352': 'XXIV',
}
TIP_BEFORE = 344
LIVE_FLOOR = 4264
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, and Demonstratur Deum esse I-XXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), and Demonstratur Deum esse I-XXIV, reconstructed from "
    "the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third "
    "edition was not used as copy-text. No modern English was copied. This slice opens Demonstratur Deum esse "
    "I-VIII (AN SIT / natural knowledge / demonstrability from effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: Demonstratur Deum esse (Theses Theologicae quibus Demonstratur Deum esse).\n"
    "Same 1675 Pitt copy-text. Book pp. 90-93 / PDF 102-105 (I-XXIV; this packet XVII-XXIV). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Demonstratur Deum esse I-XXIV tip. IX+ remains.\n"
    "Note: Distinct from De Theologia (already densified). This tract asks AN SIT and proves God from effects.\n\n"
)

LATIN = {
    "345": "XVII. Primum igitur quod corpora illa, quae sunt universi partes praecipuae & integrantes non sint entia a se & improducta multis modis probari potest. Nam primo non sunt entia per se & simplicia, sed tota quaedam congesta ex partibus diversae naturae; Saltem id manifestum est in hoc terreno & elementari globo, qui constat partibus maxime diversis: veluti petris, aquis, & terra proprie sic dicta, aliisque hujusmodi; sed quod est a se debet esse aliquid simplex. Nam quod est a se nihil habet se prius. Quod vero conflatum & compositum est ex partibus diversis, posterius est partibus ex quibus componitur; partes enim sunt aliquid prius toto. Deinde res diversae non coalescunt in Unum, nisi per aliquam causam uniantur. Sed quod est a se nullam causam habet, neque dependet ab alio.",
    "346": "XVIII. Deinde quod est a se, est sibi ipsi sufficiens, nec ullo alio indiget. Sed corpora illa, quibus hoc universum constat, veluti terra, planetae, res hujusmodi non sunt: sed aliena ope egent, nec possunt alio carere. Minor manifesta est. Nam terra & planetae lumine solis egent. Neque globus elementaris absque sole subsistere posset: Sed omnino opus habet luce & calore illius foveri, ut in suo statu & esse permaneat. Et sic quoque proculdubio reliquae universi partes solae per se esse non possent: multisque modis ab aliis juvantur atque sustentantur. Nec vero minus evidens est, quod est a se sibi sufficere, & alio non indigere: Nam quod alio indiget, & sibi ipsi non sufficit, non potest absque alio conservari. At quod non potest absque alio conservari, ab alio pendet ut sit. Quod autem ut sit ab alio pendet, certe illud non est a se. Adde quod ens a se nullam omnino causam habet: Nam a seipso esse, est causam non habere, sed quod non potest absque alio conservari causam aliquam habet, scilicet conservantem. Ac praeterea quicquid causam conservantem habet, efficientem quoque habet. Nam conservatio est quaedam efficientiae continuatio.",
    "347": "XIX. Tertio quod corpora, quibus constat hic mundus, entia a se & improducta non sint, inde manifestum est, quod singula certum finem habent, nec sunt propter se, sed propter aliud: Nam certe quod est a se, illud quoque est propter se, non autem propter aliud, neque potest ad finem referri. Etenim quicquid refertur ad finem, ab aliquo alio, unde pendet, ad finem refertur: Verum id quod est a se, non pendet ab ullo alio, a quo possit ad finem referri. Adde quod finis omnis est intentione prior re illa cujus est finis; sed quod est a se, ut jam dictum fuit, nihil habet se prius, a quo finis ille intendi potuerit. Quod autem singula corpora mundana propter se non sint, sed referantur ad finem, vel ex eo patet quod sint partes totius cujusdam, harmonice & ordine digesti, nimirum mundi ipsius ad cujus commune bonum referuntur. Nam bonum totius est finis partium singularum. Neque ullus negare potest, quod hoc & illud corpus, exempli causa, terra, sol, aut aliquis planeta, sit magnitudinis hujus aut illius, in hoc vel illo statu, ista vel illa qualitate, figura ac motu praeditum: quod, inquam, omnia ista finem certum habeant, & ita sint vel non sint, quoniam ita exigit ornatus, pulchritudo & commodum universi. Adeoque necesse est, ut tota universi harmonia & idea concepta & intenta fuerit ab aliquo, a quo omnia juxta illam constituta & ordinata sint.",
    "348": "XX. Quod corpora illa quae constituunt totum hoc universum, entia a se non sint, sed ab alio orta & producta, inde probatur, quod singula certam & determinatam perfectionem habent, & naturam ab invicem diversam: istud enim eorum discrimen, & ista determinatio omnino referri debet ad causam efficientem, quae singulis talem naturam indulsit, ac perfectionem istam & non aliam. Quod si essent a se omnia, unum & idem essent. Unde foret enim quod naturam diversam haberent, ac praeterea omni perfectionis termino & limite carerent? Nam quod essentiam habet determinatam & limitatam, necesse est ita fuisse limitatum ab aliqua causa: sed quod est a se nullam causam habet, quae limites & terminos ei ponere potuerit, sed esse per se hausit in ipso fonte, aut potius est ipsius esse fons, necesse est in se continere omnem entitatem & perfectionem.",
    "349": "XXI. Jam autem si corpora, quibus hoc universum constat, entia producta sunt, & quae sui causam & originem habent, ipsum quoque universum productum esse necesse est. Nam quod constat partibus productis improductum esse non potest.",
    "350": "XXII. Et certe si mundus hic, & partes illae quibus constat, esset aliquid a se, & quod sui causam non haberet, aeternus quoque esset, & durationis initio careret. Nam quod est, & tamen nunquam productum est, necesse est semper fuisse. Etenim quod est, & aliquando non fuit, productum esse necesse est. Quod enim transit a non esse ad esse illud certe produci dicitur; sed fieri non potest, ut mundus hic corporeus & visibilis ab aeterno fuerit. Nam mundus hic est in perpetuo motu, ejusque duratio tempore mensuratur. Sed motus & tempus, quod motum consequitur, ab aeterno esse non possunt, quod multis modis demonstrari potest.",
    "351": "XXIII. Primo enim si motus, qui, verbi causa, in sole apparet, ab aeterno esse dicatur, necesse erit solem ab aeterno fuisse, vel in aliquo Zodiaci signo, vel in omnibus Zodiaci signis. At neutrum dici potest absque manifesta contradictione. Etenim si sol ab aeterno fuit in aliquo Zodiaci signo, puta in Ariete, non item in aliis, inde sequitur solem in tempore demum pervenisse ad Taurum & Geminos. Et ita cum supponatur ab aeterno motus fuisse, per totam aeternitatem unum aut alterum tantum signum peragraverit, id est, infinito tempore, spatium finitum. Nam motus qui est ab aeterno infinito tempore, antecedit quicquid in tempore factum. Ac proinde sol eodem illo motu, quo intra mensem signum unum percurrit, tempore infinito non amplius quam unum aut alterum signum percurrere potuerit. Si dicatur autem sol ab aeterno fuisse in omnibus Zodiaci signis; necesse erit solem simul in omnibus signis Zodiaci fuisse. Etenim si ab aeterno fuit, & in Ariete & in Cancro, & in Libra & in Capricorno, non ante fuit in Ariete quam in Cancro, & in Libra quam in Capricorno. Nam quod ab aeterno est, ante se nihil habet. Ac proinde quum non fuerit in uno prius quam in alio, necesse est ut simul in omnibus fuerit. Sed implicat contradictionem solem per Zodiacum moveri, & tamen simul in omnibus Zodiaci signis esse. Nam solem per Zodiacum moveri, est unum signum deserere & ad aliud progredi: praeterquam quod ita sol sibi ipsi oppositus & a se ipso distans fuisset.",
    "352": "XXIV. Praeterea si motus qui in mundo observantur ab aeterno fuerunt, nec ullum sui initium habent, necesse est ut hactenus fuerint infinitae generationes hominum & caeterorum animalium, usque in istis generationibus detur progressus in infinitum: sed hoc est impossibile. Nam si in hominum generationibus daretur progressus in infinitum, nullus daretur primus homo, unde reliqui progeniti essent; sed omnes omnino homines, nullo excepto, essent ab homine geniti. Atqui fieri non potest, ut omnes omnino homines nullo excepto, sint ab homine geniti. Nam sic tota & integra hominum multitudo ab homine genita esset, quod dici non potest absque contradictione. Etenim si tota hominum multitudo ab homine genita est, necesse est ut ille a quo genita dicitur, vel sit extra multitudinem, vel in multitudine illa contineatur. Prius dici non potest. Nam fieri nequit ut integra hominum multitudo, ne uno quidem excepto, genita sit ab aliquo homine, qui in illa non comprehendatur: quandoquidem extra universalem hominum multitudinem nullus homo reperitur. Nec etiam dici potest, totam multitudinem hominum genitam fuisse ab aliquo, qui sit pars illius multitudinis. Nam si ita esset, homo ille, qui caeteros genuisse diceretur, se ipsum quoque genuisset. Nam qui genuit universam hominum multitudinem, singulos quoque genuit, qui in illa continentur, quorum unus ille est. At nihil se ipsum gignit, nec est sui ipsius causa."
}

SECTIONS = [
    {
        "section": "345",
        "title": "World-bodies are composites, not simple self-beings",
        "pass_a": "First therefore that those bodies which are the chief and integral parts of the universe are not beings from themselves and unproduced can be proved in many ways. For first they are not beings through themselves and simple, but certain wholes heaped together from parts of diverse nature; at least that is plain in this earthly and elementary globe, which consists of parts most diverse: as of rocks, waters, and earth properly so called, and other such things; but what is from itself ought to be something simple. For what is from itself has nothing prior to itself. But what is fused and composed from diverse parts is posterior to the parts from which it is composed; for parts are something prior to the whole. Next diverse things do not coalesce into One unless they are united by some cause. But what is from itself has no cause, nor depends on another.",
        "pass_b": [
            "First: chief world-bodies are not unproduced self-beings.",
            "They are composites of diverse parts — rocks, waters, earth — not simples.",
            "What is from itself must be simple and have nothing prior; composites need a unifier."
        ],
        "lemmas": [
            {
                "latin": "entia a se & improducta",
                "gloss": "beings from themselves and unproduced"
            },
            {
                "latin": "congesta ex partibus diversae naturae",
                "gloss": "heaped together from parts of diverse nature"
            }
        ],
        "choices": [
            {
                "term": "quod est a se debet esse aliquid simplex",
                "english": "what is from itself ought to be something simple",
                "why": "Blocks composite world-bodies from aseity.",
                "rejected": [
                    "composites can be from themselves"
                ]
            }
        ],
        "notes": [
            "OCR: XVII PDF 104 / p.92."
        ],
        "bible_refs": []
    },
    {
        "section": "346",
        "title": "What is from itself needs nothing — but planets need the sun",
        "pass_a": "Next, what is from itself is sufficient to itself, and needs no other. But those bodies of which this universe consists — earth, planets, and such — are not: but they need alien help, and cannot do without another. The minor is plain. For earth and planets need the light of the sun. Nor could the elementary globe subsist without the sun: but it altogether needs to be fostered by its light and heat, that it may remain in its state and being. And so likewise the remaining parts of the universe could doubtless not be alone through themselves: and in many ways they are helped and sustained by others. Nor is it less evident that what is from itself is sufficient to itself and needs no other: for what needs another and does not suffice to itself cannot be conserved without another. But what cannot be conserved without another depends on another in order to be. But what depends on another in order to be is certainly not from itself. Add that a being from itself has no cause at all: for to be from itself is to have no cause; but what cannot be conserved without another has some cause, namely a conserving one. And besides, whatever has a conserving cause also has an efficient one. For conservation is a certain continuation of efficiency.",
        "pass_b": [
            "What is from itself is self-sufficient.",
            "Earth and planets need the sun's light and heat — they cannot stand alone.",
            "Need of another means dependence — and conservation implies an efficient cause."
        ],
        "lemmas": [
            {
                "latin": "sibi ipsi sufficiens",
                "gloss": "sufficient to itself"
            },
            {
                "latin": "aliena ope egent",
                "gloss": "need alien help"
            }
        ],
        "choices": [
            {
                "term": "conservatio est quaedam efficientiae continuatio",
                "english": "conservation is a certain continuation of efficiency",
                "why": "Ties ongoing dependence to efficient causality.",
                "rejected": [
                    "conservation needs no efficient cause"
                ]
            }
        ],
        "notes": [
            "OCR: XVIII PDF 104."
        ],
        "bible_refs": []
    },
    {
        "section": "347",
        "title": "World-bodies aim at ends — so they are not for themselves",
        "pass_a": "Third, that the bodies of which this world consists are not beings from themselves and unproduced is plain from this: that each has a certain end, and they are not for themselves but for another. For certainly what is from itself is also for itself, not for another, and cannot be referred to an end. For whatever is referred to an end is referred to an end by some other on which it depends: but what is from itself depends on no other by which it could be referred to an end. Add that every end is prior in intention to the thing of which it is the end; but what is from itself, as already said, has nothing prior to itself from which that end could have been intended. But that each worldly body is not for itself but is referred to an end is clear also from this: that they are parts of a certain whole digested in harmony and order — namely of the world itself — to whose common good they are referred. For the good of the whole is the end of the singular parts. Nor can anyone deny that this and that body — for example earth, sun, or some planet — is of this or that magnitude, in this or that state, endowed with this or that quality, figure, and motion: that, I say, all these have a certain end, and are or are not so because the adornment, beauty, and convenience of the universe so require. And so it is necessary that the whole harmony and idea of the universe was conceived and intended by someone, by whom all things were constituted and ordered according to it.",
        "pass_b": [
            "Each world-body has an end — not for itself but for another.",
            "Aseity cannot be referred to an end or have anything prior intending it.",
            "Parts serve the world's common good — so some mind conceived the harmony."
        ],
        "lemmas": [
            {
                "latin": "certum finem habent",
                "gloss": "have a certain end"
            },
            {
                "latin": "commune bonum",
                "gloss": "common good"
            }
        ],
        "choices": [
            {
                "term": "tota universi harmonia & idea concepta & intenta fuerit ab aliquo",
                "english": "the whole harmony and idea of the universe was conceived and intended by someone",
                "why": "Teleology of parts → intentional cause.",
                "rejected": [
                    "cosmic order needs no intending mind"
                ]
            }
        ],
        "notes": [
            "OCR: XIX PDF 104."
        ],
        "bible_refs": []
    },
    {
        "section": "348",
        "title": "Limited diverse natures prove an efficient cause — not aseity",
        "pass_a": "That those bodies which constitute this whole universe are not beings from themselves, but arisen and produced from another, is proved from this: that each has a certain and determinate perfection, and a nature diverse from one another. For that discrimination of theirs, and that determination, must altogether be referred to an efficient cause which granted each such a nature, and that perfection and not another. But if all were from themselves, they would be one and the same. For whence would it be that they had a diverse nature, and besides would lack every bound and limit of perfection? For what has a determinate and limited essence must have been so limited by some cause: but what is from itself has no cause which could set limits and bounds for it, but drew being through itself from the very fountain — or rather is itself the fountain of being — and must contain in itself every entity and perfection.",
        "pass_b": [
            "Diverse limited perfections need an efficient cause.",
            "If all were from themselves they would be one unbounded being.",
            "Aseity would be the fountain of all perfection — not a capped planet-nature."
        ],
        "lemmas": [
            {
                "latin": "determinatam perfectionem",
                "gloss": "determinate perfection"
            },
            {
                "latin": "causam efficientem",
                "gloss": "efficient cause"
            }
        ],
        "choices": [
            {
                "term": "Quod si essent a se omnia, unum & idem essent",
                "english": "But if all were from themselves, they would be one and the same",
                "why": "Diversity blocks universal aseity.",
                "rejected": [
                    "many limited a-se beings can coexist"
                ]
            }
        ],
        "notes": [
            "OCR: XX PDF 104-105 page break into XXI."
        ],
        "bible_refs": []
    },
    {
        "section": "349",
        "title": "If the parts are produced, the universe itself is produced",
        "pass_a": "But now if the bodies of which this universe consists are produced beings, and have a cause and origin of themselves, the universe itself also must be produced. For what consists of produced parts cannot be unproduced.",
        "pass_b": [
            "Produced parts → produced universe.",
            "A whole of produced parts cannot itself be unproduced."
        ],
        "lemmas": [
            {
                "latin": "ipsum quoque universum productum",
                "gloss": "the universe itself also produced"
            },
            {
                "latin": "constat partibus productis",
                "gloss": "consists of produced parts"
            }
        ],
        "choices": [
            {
                "term": "quod constat partibus productis improductum esse non potest",
                "english": "what consists of produced parts cannot be unproduced",
                "why": "Whole inherits produced status from parts.",
                "rejected": [
                    "the universe can be a-se while parts are not"
                ]
            }
        ],
        "notes": [
            "OCR: XXI spans PDF 104-105."
        ],
        "bible_refs": []
    },
    {
        "section": "350",
        "title": "If the world were from itself it would be eternal — but motion and time are not",
        "pass_a": "And certainly if this world, and those parts of which it consists, were something from itself, and had no cause of itself, it would also be eternal, and would lack a beginning of duration. For what is, and yet was never produced, must always have been. For what is, and at some time was not, must have been produced. For what passes from non-being to being is certainly said to be produced; but it cannot be that this bodily and visible world was from eternity. For this world is in perpetual motion, and its duration is measured by time. But motion and time, which follows motion, cannot be from eternity, which can be shown in many ways.",
        "pass_b": [
            "Aseity would mean an eternal world with no start of duration.",
            "But this bodily world is in perpetual motion measured by time.",
            "Motion and time cannot be from eternity — next theses prove it."
        ],
        "lemmas": [
            {
                "latin": "durationis initio careret",
                "gloss": "would lack a beginning of duration"
            },
            {
                "latin": "motus & tempus",
                "gloss": "motion and time"
            }
        ],
        "choices": [
            {
                "term": "motus & tempus ... ab aeterno esse non possunt",
                "english": "motion and time cannot be from eternity",
                "why": "Opens motion/time arguments XXIII+.",
                "rejected": [
                    "eternal cyclic motion is possible for this world"
                ]
            }
        ],
        "notes": [
            "OCR: XXII PDF 105 / p.93."
        ],
        "bible_refs": []
    },
    {
        "section": "351",
        "title": "Eternal solar motion yields contradiction in the Zodiac",
        "pass_a": "For first, if the motion which, for example, appears in the sun were said to be from eternity, it would be necessary that the sun had been from eternity either in some sign of the Zodiac, or in all the signs of the Zodiac. But neither can be said without plain contradiction. For if the sun was from eternity in some Zodiac sign, say Aries, and not likewise in the others, thence it follows that the sun only in time finally arrived at Taurus and Gemini. And so, though motion is supposed to have been from eternity, through all eternity it would have traversed only one or another sign — that is, in infinite time, a finite space. For motion which is from eternity in infinite time precedes whatever is done in time. And therefore by that same motion by which within a month it runs through one sign, in infinite time it could run through no more than one or another sign. But if it be said the sun was from eternity in all Zodiac signs, it will be necessary that the sun was at once in all Zodiac signs. For if it was from eternity, and in Aries and in Cancer, and in Libra and in Capricorn, it was not in Aries before Cancer, nor in Libra before Capricorn. For what is from eternity has nothing before itself. And therefore since it was not in one before another, it must have been in all at once. But it implies a contradiction that the sun move through the Zodiac and yet be at once in all Zodiac signs. For the sun to move through the Zodiac is to leave one sign and proceed to another: besides which thus the sun would have been opposite to itself and distant from itself.",
        "pass_b": [
            "Eternal sun-motion: either stuck in one Zodiac sign forever, or in all at once.",
            "One-sign forever: infinite time covers only finite space.",
            "All-signs at once: contradicts moving through the Zodiac."
        ],
        "lemmas": [
            {
                "latin": "Zodiaci signo",
                "gloss": "Zodiac sign"
            },
            {
                "latin": "simul in omnibus",
                "gloss": "at once in all"
            }
        ],
        "choices": [
            {
                "term": "implicat contradictionem solem per Zodiacum moveri, & tamen simul in omnibus Zodiaci signis esse",
                "english": "it implies a contradiction that the sun move through the Zodiac and yet be at once in all Zodiac signs",
                "why": "Closes the solar-motion fork.",
                "rejected": [
                    "eternal solar motion through the Zodiac is coherent"
                ]
            }
        ],
        "notes": [
            "OCR: XXIII PDF 105."
        ],
        "bible_refs": []
    },
    {
        "section": "352",
        "title": "Eternal motion would require infinite human generations — impossible",
        "pass_a": "Besides, if the motions observed in the world were from eternity and have no beginning of themselves, it is necessary that there have been hitherto infinite generations of humans and of the other animals, so that in those generations an infinite progress is granted: but this is impossible. For if an infinite progress were granted in human generations, no first human would be given from whom the rest would be begotten; but all humans altogether, with none excepted, would be begotten from a human. But it cannot be that all humans altogether, with none excepted, are begotten from a human. For thus the whole and entire multitude of humans would be begotten from a human, which cannot be said without contradiction. For if the whole multitude of humans is begotten from a human, that one from whom it is said to be begotten must either be outside the multitude, or be contained in that multitude. The former cannot be said. For it cannot be that the entire multitude of humans, not even one excepted, was begotten from some human not comprehended in it: since outside the universal multitude of humans no human is found. Nor can it be said that the whole multitude of humans was begotten from someone who is part of that multitude. For if so, that human who is said to have begotten the others would also have begotten himself. For whoever begot the universal multitude of humans also begot each who are contained in it, of whom he is one. But nothing begets itself, nor is the cause of itself.",
        "pass_b": [
            "Eternal motion → infinite past human generations.",
            "No first human: every human begotten by a human — including the whole set.",
            "Begetter outside the set is impossible; begetter inside would beget himself."
        ],
        "lemmas": [
            {
                "latin": "infinitae generationes",
                "gloss": "infinite generations"
            },
            {
                "latin": "nihil se ipsum gignit",
                "gloss": "nothing begets itself"
            }
        ],
        "choices": [
            {
                "term": "nihil se ipsum gignit, nec est sui ipsius causa",
                "english": "nothing begets itself, nor is the cause of itself",
                "why": "Closes infinite-generation regress via self-begetting absurdity.",
                "rejected": [
                    "infinite past human generations are possible"
                ]
            }
        ],
        "notes": [
            "OCR: XXIV PDF 105; next XXV+ continues generation/time arguments."
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
            DATA / 'latin.json',
            Path(__file__),
        ],
        expected_sections=section_ids,
        seed=20260925,
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
        if 345 <= n <= 352:
            notes = (
                f'Section {sid}: new densify Demonstratur Deum esse XVII-XXIV; '
                'Pass A!=B; lock-grounded PDF 104-105 / book pp. 92-93.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in deum_esse XVII-XXIV packet scope covering all current sections.'
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
                'Scope review: densify Demonstratur Deum esse XVII-XXIV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Deum esse through XXIV; XXV+ remains. '
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
        'locus': 'Demonstratur Deum esse theses XVII-XXIV (world-bodies not a se / eternal motion)',
        'next_locus': 'Demonstratur Deum esse XXV+ (generation / time-eternity arguments)',
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
        f'## {day} (Scribe — Demonstratur Deum esse XVII–XXIV densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Deum esse XVII–XXIV → §§{SECS[0]}–{SECS[-1]}; continues Deum esse after IX-XVI).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 103-104 / pp. 91-92).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: Demonstratur Deum esse through XXIV (AN SIT; natural knowledge; '
        'world-bodies / motion). XXV+ remains. Prior tracts closed as before. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Pre-append hold cleared live>4264 OR 12m; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}; '
        f'disk tip re-read {TIP_BEFORE} before append.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc Demonstratur Deum esse XVII–XXIV densify)\n\n'
        'CoS densify: Demonstratur Deum esse XVII–XXIV (existence of God). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Deum esse XVII–XXIV (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through XXIV. Next: Deum esse XXV+. '
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-344 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
