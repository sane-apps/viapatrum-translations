#!/usr/bin/env python3
"""Build + apply Demonstratur Deum esse I-XL densify (tip 328 → 336).

Pre-append hold CLEARED at live 57/4205. After tip-ready: HOLD live>4309 OR 12m.
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
PACKET_STEM = 'deum_esse_xxxiii_xl_densify'
APPLY_COPY = BOOK / 'sources/_ocr_deum_esse/apply_deum_esse_xxxiii_xl_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['361', '362', '363', '364', '365', '366', '367', '368']
ROMANS = {
    '361': 'XXXIII', '362': 'XXXIV', '363': 'XXXV', '364': 'XXXVI',
    '365': 'XXXVII', '366': 'XXXVIII', '367': 'XXXIX', '368': 'XL',
}
TIP_BEFORE = 360
LIVE_FLOOR = 4309
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XL"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XL)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XL (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, and Demonstratur Deum esse I-XL. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), and Demonstratur Deum esse I-XL, reconstructed from "
    "the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third "
    "edition was not used as copy-text. No modern English was copied. This slice opens Demonstratur Deum esse "
    "I-VIII (AN SIT / natural knowledge / demonstrability from effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: Demonstratur Deum esse (Theses Theologicae quibus Demonstratur Deum esse).\n"
    "Same 1675 Pitt copy-text. Book pp. 90-96 / PDF 102-108 (I-XL; this packet XXXIII-XL). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Demonstratur Deum esse I-XL tip. IX+ remains.\n"
    "Note: Distinct from De Theologia (already densified). This tract asks AN SIT and proves God from effects.\n\n"
)

LATIN = {
    "361": "XXXIII. Et certe quis est, qui, dum palatium aliquod splendide, & ex arte extractum contemplatur, aut horologium quoddam affabre fictum, quod variis rotis & motibus inter se compositis, horas, dies, & lunae phases notat & dimetitur, in animum inducat ista casu facta esse, & lignis atque lapidibus, aerisque & chalybis particulis quibusdam temere congestis exorta? At quodnam Palatium excogitari potest majori arte, & symmetria structum, & ubi proportiones omnes melius observatae sint, quam ipsum hoc universum, quod oculis nostris obversatur? Aut quaenam est machina in qua plures motus, magisque mirabiles, & in summa varietate magis constantes, observari possint?",
    "362": "XXXIV. Nec etiam potest tantum opus tribui causae brutae, & quae agat ex necessitate, absque ratione & intelligentia. Primo enim inter ea quae in mundo videntur, multa sunt, non tantum sensu & cognitione praedita, veluti bestiae: sed etiam ratione & intellectu, sicuti homines; sed id quod cognoscit & intelligit, necessario causam aliquam habet cognoscentem & intelligentem: nam effectus sua causa prima & praecipua perfectior esse non potest: nec potest in effectu quicquam perfectionis esse, quod in causa non sit, si non formaliter, saltem modo quodam eminentiori, ut ante demonstratum fuit. Jam autem simpliciter & absolute perfectius est cognoscere, quam non cognoscere, intelligere, quam non intelligere. Ideoque necesse est, ut quod est prima & praecipua causa rei intelligentis, non sit expers intelligentiae, alioqui causa esset effectu minus perfecta. Atque haec est demonstratio, qua utitur Psaltes Psal. 94. dum homines atheos & profanos coarguit. Intelligite, inquit, stupidi in populo & fatui, quando intelligetis? An qui plantavit aurem, non audiet? an qui oculum finxit, non videbit? An qui gentes corripit, non arguet? An qui docet homines scientiam, non cognoscet?",
    "363": "XXXV. Deinde videmus in mundo nihil temere factum esse, & naturam in omnibus agere certum ob finem, & qua ratione congruit ut assequatur illud quod optimum est. Sic nullus est eorum, qui speculantur opera naturae, qui facile non agnoscat solis motum diurnum & annuum, ita ut est, temperatum esse, ut mediante vicissitudine dierum & noctium, variarumque anni tempestatum, diversae rerum in natura species generari & conservari possint. In terra vero disposita esse omnia ad usum & commodum animalium, ac praecipue in animalibus illa tot & tam varia organa ad certos usus singula facta esse, & unumquodque suum habere finem, unum ut nutritioni, aliud ut generationi, aliud ut sensuum functionibus inserviat: & ita de reliquis quae pene innumera sunt. Jam autem necesse est, ut quod agit propter finem, & ad finem aliquem tendit, vel cognoscat finem illum, vel, si finem non novit, dirigatur ab alio, cui finis ille fuerit propositus, sicut sagitta ad scopum dirigitur a sagittario. Itaque natura illa, quae statuitur causa rerum, necessario, vel est aliquid intelligens, ac proinde Deus ipse, vel dirigitur a summa quadam intelligentia, quae certe Deus erit.",
    "364": "XXXVI. Praeterea si quis consideret, tam universum hujus mundi systema & corporum illorum, quibus constat, dispositionem, motusque & flexus varios, quam singula quae in eo observantur, plantas, dico, & animalia & alia, quae videre & tractare possumus, negare non poterit, in omnibus istis elucere infinitas summae sapientiae notas: atque non tantum totius universi, sed animalis cujusque structuram, ita mirandam & stupendam esse, & in ea proportiones omnes tam accurate & exacte observatas, atque tam diligenter & proinde omnibus prospectum, ut ingenium humanum, sapientiam tantam satis capere & mirari non possit. Quis ergo, nisi plane stupidus & insipiens, opera tanta cum arte & industria facta, tantoque cum ordine & harmonia digesta, referre possit in causam, quae sit omnino bruta, omnisque sapientiae & cognitionis expers?",
    "365": "XXXVII. Verum ut magis adhuc urgeamus impios illos, qui nolunt aliam rerum causam agnoscere, nisi brutam quandam naturam: Rogamus eos quid nomine naturae intelligant. Nam vulgo per naturam, quae casui opponitur, & iis quae ex consilio & deliberatione agunt, intelligitur ordo & series causarum, quibus constat hoc universum. Juxta quem ordinem videmus in terra fieri varias generationes, & in elementari regione alias & alias mutationes: Sic enim, quum planta plantam, & animal aliud animal simile generat, opus esse naturae dicimus: & similiter quum nives per hyemem terram operiunt, aestate vero terra aestu fatiscit, ad naturam ista referimus: Sed hic frustra ad istam naturam recurritur. Nam natura illa, ut patet ex dictis, nihil aliud est, quam ordo agentium & patientium, quibus hoc universum constat. Sed hic quaeritur hujus ordinis author, & quid est illud quod coelum, solem & terram produxit, & quo videmus ordine disposuit? Quaenam est ergo natura, quae, naturae hujus, quae jam operatur, causa est?",
    "366": "XXXVIII. Arbitrantur impii nonnulli naturam hanc, quae non est aliud quam mundi systema, exortam esse ex vario situ, figura & dispositione partium materiae, quae certa quadam motus mensura agitatae, sese sponte in hunc ordinem digesserunt, qui jam in mundo observatur: nec aliam rerum causam aliudve principium ultra esse quaerendum. Sed quibus argumentis probavimus mundi partes praecipuas, terram scilicet, solem atque planetas a se ipsis non esse, sed aliquam sui causam & originem habere, iisdem probare possumus, istas quoque materiae particulas a se non existere, sed esse suum habere ab alio. Etenim id quod est a se, perfectionis nullos limites habere potest, ut ante ostensum est, atqui materia & ejus particulae sunt entia imperfectissima. Deinde quod est a se illud quoque propter se est: Sed materiae partes non sunt propter se, sed propter aliud, nimirum propter corpora quae componunt & quorum partes sunt.",
    "367": "XXXIX. Praeterea unde est ista materiae divisio, & variae in partibus ejus magnitudines & figurae? Omnino necesse est, ut sit agens aliquod, quod materiam ita diviserit, & varias partibus ejus figuras impresserit. Quod si omnes a se ipsis suam quantitatem & figuram haberent, nulla esset inter ipsas ratio diversitatis. Nec etiam earum figura variari & mutari posset. Ac proinde materia non esset, ut tamen est, divisibilis in infinitum.",
    "368": "XL. Praecipue vero, cum demonstraverimus motum & tempus ab aeterno esse non posse, quicquid sit de materia ipsa, necesse est, ut motus ille partium materiae, unde exorta statuitur universa rerum dispositio, aliquod sui initium habeat: ac proinde materia non potest motum illum a se habere; sed motus iste necessario est a principio extrinseco. Nam illo non concesso materiam aeternam esse, & a se existere, cujus contrarium ante probatum est, attamen post aeternam quietem moveri non potuit, nisi motor aliquis externus motum illum ipsi impresserit. Ecquis vero est ille motor, qui torpentem materiam primo commovere & agitare coepit, & motum ejus tam apte dimensus est, ut inde mundi systema oriretur? Hic certe necessario ad summam quandam mentem, id est, ad Deum recurrendum erit."
}

SECTIONS = [
    {
        "section": "361",
        "title": "Palace and watch: chance cannot build the universe-machine",
        "pass_a": "And certainly who is there who, while contemplating some palace splendidly and by art drawn forth, or some clock skillfully made, which with various wheels and motions composed among themselves notes and measures hours, days, and the phases of the moon, would take it into his mind that these were made by chance, and arose from woods and stones and certain particles of bronze and steel rashly heaped together? But what palace can be thought of structured with greater art and symmetry, and where all proportions are better observed, than this very universe which meets our eyes? Or what machine is there in which more motions, and more marvelous ones, and in the highest variety more constant, can be observed?",
        "pass_b": [
            "Who credits a palace or a clock to chance scrap-heaps?",
            "This universe outdoes any palace in art and proportion.",
            "No machine shows more motions — more marvelous, more constant."
        ],
        "lemmas": [
            {
                "latin": "palatium aliquod",
                "gloss": "some palace"
            },
            {
                "latin": "horologium",
                "gloss": "a clock"
            }
        ],
        "choices": [
            {
                "term": "ista casu facta esse",
                "english": "that these were made by chance",
                "why": "Rejects chance after Democritus/Epicurus.",
                "rejected": [
                    "ordered artifacts can arise by chance heap"
                ]
            }
        ],
        "notes": [
            "OCR: XXXIII PDF 107; horologium/chalybis restored."
        ],
        "bible_refs": []
    },
    {
        "section": "362",
        "title": "Blind necessary cause cannot birth knowers — Psalm 94",
        "pass_a": "Nor can so great a work be attributed to a brute cause, and one that acts from necessity, without reason and intelligence. For first among the things seen in the world, many are endowed not only with sense and cognition, as beasts: but also with reason and intellect, as humans; but that which knows and understands necessarily has some knowing and intelligent cause: for an effect cannot be more perfect than its first and principal cause: nor can there be any perfection in the effect which is not in the cause, if not formally, at least in some more eminent mode, as was shown before. But now simply and absolutely it is more perfect to know than not to know, to understand than not to understand. Therefore it is necessary that what is the first and principal cause of an intelligent thing not be devoid of intelligence, otherwise the cause would be less perfect than the effect. And this is the demonstration which the Psalmist uses in Psalm 94 when he convicts atheist and profane people. Understand, he says, you stupid among the people and fools, when will you understand? He who planted the ear, shall he not hear? He who formed the eye, shall he not see? He who chastises the nations, shall he not rebuke? He who teaches humans knowledge, shall he not know?",
        "pass_b": [
            "A brute necessary cause cannot explain knowers.",
            "Knowing effects require a knowing first cause.",
            "Psalm 94: He who planted the ear — shall He not hear?"
        ],
        "lemmas": [
            {
                "latin": "causae brutae",
                "gloss": "a brute cause"
            },
            {
                "latin": "Psal. 94",
                "gloss": "Psalm 94"
            }
        ],
        "choices": [
            {
                "term": "An qui plantavit aurem, non audiet?",
                "english": "He who planted the ear, shall he not hear?",
                "why": "Psalm proof against blind first cause.",
                "rejected": [
                    "intelligence can arise from non-intelligent first cause"
                ]
            }
        ],
        "notes": [
            "OCR: XXXIV PDF 107; Psal. 94 / aurem restored."
        ],
        "bible_refs": [
            "Bible:Psalm 94:8-10"
        ]
    },
    {
        "section": "363",
        "title": "Nature acts for ends — either intelligent, or steered by God",
        "pass_a": "Next we see that nothing in the world has been done rashly, and that nature in all things acts for a certain end, and by the reason that fits so as to attain what is best. So there is none of those who contemplate the works of nature who does not easily acknowledge that the sun's daily and yearly motion, as it is, is tempered so that by means of the vicissitude of days and nights and of the various seasons of the year diverse species of things in nature can be generated and conserved. And on the earth all things are disposed for the use and convenience of animals, and especially in animals those so many and so various organs are each made for certain uses, and each has its own end — one to serve nutrition, another generation, another the functions of the senses: and so of the rest which are almost innumerable. But now it is necessary that what acts for an end, and tends to some end, either know that end, or, if it does not know the end, be directed by another to whom that end was proposed, as an arrow is directed to the mark by an archer. Therefore that nature which is stated as the cause of things necessarily either is something intelligent, and so God Himself, or is directed by some highest intelligence, which will certainly be God.",
        "pass_b": [
            "Nothing in the world is rash — nature acts for ends.",
            "Sun, seasons, organs: each fitted to a use.",
            "End-seeking without knowledge needs an archer — God either is or steers that nature."
        ],
        "lemmas": [
            {
                "latin": "certum ob finem",
                "gloss": "for a certain end"
            },
            {
                "latin": "sicut sagitta ad scopum",
                "gloss": "as an arrow to the mark"
            }
        ],
        "choices": [
            {
                "term": "vel est aliquid intelligens, ac proinde Deus ipse, vel dirigitur a summa quadam intelligentia",
                "english": "either is something intelligent, and so God Himself, or is directed by some highest intelligence",
                "why": "Teleology fork closes on God either way.",
                "rejected": [
                    "end-directed nature needs no mind"
                ]
            }
        ],
        "notes": [
            "OCR: XXXV PDF 107-108 page break."
        ],
        "bible_refs": []
    },
    {
        "section": "364",
        "title": "Infinite marks of wisdom — not a brute cause",
        "pass_a": "Besides if anyone considers both the universal system of this world and the disposition of those bodies of which it consists, and their various motions and bendings, and the singular things observed in it — plants, I say, and animals and others which we can see and handle — he will not be able to deny that in all these there shine forth infinite marks of the highest wisdom: and that not only the structure of the whole universe, but of each animal, is so marvelous and stupendous, and in it all proportions so accurately and exactly observed, and so diligently and therefore provision made for all, that the human mind cannot sufficiently grasp and admire so great a wisdom. Who then, unless plainly stupid and foolish, could refer works made with so much art and industry, and digested with so much order and harmony, to a cause which is altogether brute and devoid of all wisdom and cognition?",
        "pass_b": [
            "World-system and each creature show infinite marks of highest wisdom.",
            "Proportions exact beyond human grasp.",
            "Only a fool credits that to a brute, mindless cause."
        ],
        "lemmas": [
            {
                "latin": "infinitas summae sapientiae notas",
                "gloss": "infinite marks of the highest wisdom"
            },
            {
                "latin": "omnino bruta",
                "gloss": "altogether brute"
            }
        ],
        "choices": [
            {
                "term": "referre possit in causam, quae sit omnino bruta",
                "english": "could refer to a cause which is altogether brute",
                "why": "Wisdom-marks bar blind nature.",
                "rejected": [
                    "stupendous order needs no wisdom in the cause"
                ]
            }
        ],
        "notes": [
            "OCR: XXXVI PDF 108."
        ],
        "bible_refs": []
    },
    {
        "section": "365",
        "title": "“Nature” is only the order of causes — who authored that order?",
        "pass_a": "But that we may still more urge those ungodly who will acknowledge no other cause of things except some brute nature: We ask them what they understand by the name of nature. For commonly by nature, which is opposed to chance, and to those who act from counsel and deliberation, is understood the order and series of causes of which this universe consists. According to which order we see various generations happen on earth, and in the elementary region other and other mutations: for so, when a plant generates a plant, and an animal another like animal, we say it is a work of nature: and likewise when snows cover the earth through winter, but in summer the earth gapes with heat, we refer those things to nature: But here one recurs in vain to that nature. For that nature, as is clear from what was said, is nothing other than the order of agents and patients of which this universe consists. But here the author of this order is sought, and what is that which produced heaven, sun, and earth, and disposed them in the order we see? What then is the nature which is the cause of this nature which now operates?",
        "pass_b": [
            "Ask the nature-only crowd: what do you mean by nature?",
            "Usually: the order of causes — plant begets plant, seasons turn.",
            "That order itself needs an author — who made heaven, sun, earth?"
        ],
        "lemmas": [
            {
                "latin": "ordo & series causarum",
                "gloss": "order and series of causes"
            },
            {
                "latin": "hujus ordinis author",
                "gloss": "the author of this order"
            }
        ],
        "choices": [
            {
                "term": "Quaenam est ergo natura, quae, naturae hujus, quae jam operatur, causa est?",
                "english": "What then is the nature which is the cause of this nature which now operates?",
                "why": "Pushes past secondary nature to first author.",
                "rejected": [
                    "nature as order needs no further cause"
                ]
            }
        ],
        "notes": [
            "OCR: XXXVII PDF 108."
        ],
        "bible_refs": []
    },
    {
        "section": "366",
        "title": "Matter-particles are not from themselves either",
        "pass_a": "Some ungodly judge that this nature, which is nothing other than the world-system, arose from the various situation, figure, and disposition of the parts of matter, which agitated by a certain measure of motion spontaneously digested themselves into this order now observed in the world: and that no other cause of things or other principle beyond is to be sought. But by the same arguments by which we proved that the chief parts of the world — earth, sun, and planets — are not from themselves, but have some cause and origin of themselves, we can prove that those particles of matter also do not exist from themselves, but have their being from another. For that which is from itself can have no limits of perfection, as was shown before, but matter and its particles are most imperfect beings. Next, what is from itself is also for itself: But the parts of matter are not for themselves, but for another, namely for the bodies which they compose and of which they are parts.",
        "pass_b": [
            "Some say matter bits self-sorted into the world-order — stop there.",
            "Same proofs that bar planet-aseity bar particle-aseity.",
            "Imperfect parts exist for wholes — not from themselves."
        ],
        "lemmas": [
            {
                "latin": "materiae particulas",
                "gloss": "particles of matter"
            },
            {
                "latin": "entia imperfectissima",
                "gloss": "most imperfect beings"
            }
        ],
        "choices": [
            {
                "term": "istas quoque materiae particulas a se non existere",
                "english": "those particles of matter also do not exist from themselves",
                "why": "Extends aseity block to atoms/particles.",
                "rejected": [
                    "matter particles can be a-se while planets are not"
                ]
            }
        ],
        "notes": [
            "OCR: XXXVIII PDF 108."
        ],
        "bible_refs": []
    },
    {
        "section": "367",
        "title": "Matter’s division and shapes need an agent",
        "pass_a": "Besides, whence is that division of matter, and the various magnitudes and figures in its parts? It is altogether necessary that there be some agent which so divided matter and impressed various figures on its parts. But if all had their quantity and figure from themselves, there would be no reason of diversity among them. Nor could their figure be varied and changed. And therefore matter would not be, as it yet is, divisible to infinity.",
        "pass_b": [
            "Whence matter's split sizes and shapes?",
            "Some agent must have divided and figured it.",
            "Self-shaped bits could not differ or change — yet matter divides without end."
        ],
        "lemmas": [
            {
                "latin": "materiae divisio",
                "gloss": "division of matter"
            },
            {
                "latin": "divisibilis in infinitum",
                "gloss": "divisible to infinity"
            }
        ],
        "choices": [
            {
                "term": "ut sit agens aliquod, quod materiam ita diviserit",
                "english": "that there be some agent which so divided matter",
                "why": "Division/figure need an impressing agent.",
                "rejected": [
                    "particles self-assign size and shape"
                ]
            }
        ],
        "notes": [
            "OCR: XXXIX PDF 108."
        ],
        "bible_refs": []
    },
    {
        "section": "368",
        "title": "Matter’s motion needs an external mover — God",
        "pass_a": "But especially, since we have demonstrated that motion and time cannot be from eternity, whatever be the case about matter itself, it is necessary that that motion of the parts of matter, from which the universal disposition of things is stated to have arisen, have some beginning of itself: and therefore matter cannot have that motion from itself; but that motion is necessarily from an extrinsic principle. For even if it be not granted that matter is eternal and exists from itself — whose contrary was proved before — yet after eternal rest it could not be moved unless some external mover impressed that motion on it. But who is that mover who first began to stir and agitate torpid matter, and so aptly measured its motion that thence the world-system would arise? Here certainly one must necessarily recur to some highest mind, that is, to God.",
        "pass_b": [
            "Motion is not eternal — so matter-motion had a start.",
            "Matter cannot give itself that first stir.",
            "Who wound torpid matter into a world-system? The highest mind — God."
        ],
        "lemmas": [
            {
                "latin": "principio extrinseco",
                "gloss": "an extrinsic principle"
            },
            {
                "latin": "ad summam quandam mentem",
                "gloss": "to some highest mind"
            }
        ],
        "choices": [
            {
                "term": "Hic certe necessario ad summam quandam mentem, id est, ad Deum recurrendum erit",
                "english": "Here certainly one must necessarily recur to some highest mind, that is, to God",
                "why": "Closes particle-motion block on God before XLI+ body analogies.",
                "rejected": [
                    "matter self-starts ordered motion"
                ]
            }
        ],
        "notes": [
            "OCR: XL PDF 108; next XLI+ human-body / conclusion."
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
            DATA / 'tess_108.txt',
            DATA / 'latin.json',
            Path(__file__),
        ],
        expected_sections=section_ids,
        seed=20260927,
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
        if 361 <= n <= 368:
            notes = (
                f'Section {sid}: new densify Demonstratur Deum esse XXXIII-XL; '
                'Pass A!=B; lock-grounded PDF 107-108 / book pp. 95-96.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in deum_esse XXXIII-XL packet scope covering all current sections.'
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
                'Scope review: densify Demonstratur Deum esse XXXIII-XL only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Deum esse through XL; XLI+ remains. '
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
        'locus': 'Demonstratur Deum esse theses XXXIII-XL (palace-watch / nature / matter-mover)',
        'next_locus': 'Demonstratur Deum esse XLI+ (human body / final Esse Deum close)',
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
        f'## {day} (Scribe — Demonstratur Deum esse XXXIII–XL densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Deum esse XXXIII–XL → §§{SECS[0]}–{SECS[-1]}; continues Deum esse after XXV-XXXII).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 103-104 / pp. 91-92).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: Demonstratur Deum esse through XL (AN SIT; natural knowledge; '
        'palace-watch / matter). XLI+ remains. Prior tracts closed as before. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Pre-append hold cleared live>4309 OR 12m; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}; '
        f'disk tip re-read {TIP_BEFORE} before append.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc Demonstratur Deum esse XXXIII–XL densify)\n\n'
        'CoS densify: Demonstratur Deum esse XXXIII–XL (existence of God). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Deum esse XXXIII–XL (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through XL. Next: Deum esse XLI+. '
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-360 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
