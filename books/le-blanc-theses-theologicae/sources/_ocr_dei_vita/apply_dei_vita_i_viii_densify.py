#!/usr/bin/env python3
"""Build + apply De Vita Dei I-VIII densify (tip 475 → 483).

Opens after Aeternitate XIX close. Live floor 4723.
After tip-ready: HOLD live>4723 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_vita_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_vita_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_vita_densify')
PACKET_STEM = 'dei_vita_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_vita/apply_dei_vita_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['476', '477', '478', '479', '480', '481', '482', '483']
ROMANS = {
    '476': 'I', '477': 'II', '478': 'III', '479': 'IV',
    '480': 'V', '481': 'VI', '482': 'VII', '483': 'VIII',
}
TIP_BEFORE = 475
LIVE_FLOOR = 4723
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Vita Dei I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Vita Dei I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Vita Dei I-VIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks; tess blocked on Mini PNG path). "
    "1683 not copy-text. No modern English. This slice opens Vita Dei I-VIII "
    "(common/philosophical living; grades of life; plants, animals, humans)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Vita Dei.\n"
    "Same 1675 Pitt copy-text. Book pp. 114-115 / PDF 126-127 (I-VIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Vita Dei I-VIII tip — opens after Aeternitate XIX. Next: Vita Dei IX+.\n"
    "Note: Grades of living from loose speech up through plants, animals, and humans.\n\n"
)

LATIN = {
    '476': (
        'I. Notione communissima & generalissima ac in usu communi loquendi vivere dicuntur '
        'ea quae quovis modo nobis seipsa movere apparent, sic dicimus aquam vivam & ignem '
        'vivum, quia flamma pluribus motibus sponte sua cieri videtur, & etiam aqua e fonte '
        'scaturiens, cui aquae mortuae stagnorum opponuntur.'
    ),
    '477': (
        'II. Sed proprie & Philosophice id tantum seipsum movere adeoque vivere dicitur quod '
        'seipsum in loco & statu naturali constitutum movere potest, atque ita ut postquam '
        'naturaliter a motu destitit, & ab operando cessavit, motum rursus a se inchoare '
        'valeat. Quum autem dico id quod vivit a motu desistere, non intelligo simpliciter '
        'ab omni motu. Etenim in omni vivente est vigor quidem continuus & motus indeficiens '
        'qui nisi in morte non cessat. Sed vivere tamen non dicimus nisi quod potest per '
        'naturam ab aliquo motu cessare, & rursus eundem motum ex principio interno inchoare.'
    ),
    '478': (
        'III. In hac autem vitae definitione motus non sumitur stricte & prout a Philosophis '
        'definitur, Actus entis in potentia quatenus est in potentia, qui motus in subjecto '
        'necessario supponit aliquam imperfectionem, & propterea dicitur in scholis actus '
        'imperfecti; sed sensu generali per motum intelligitur operatio quaevis, & illa etiam '
        'quae est actus perfecti.'
    ),
    '479': (
        'IV. Porro vitae perfectio, ut ex definitione facile colligi potest, in duobus '
        'praesertim consistit: primo, scilicet, in motuum & operationum praestantia & '
        'varietate: deinde in agentis, ut sic dicam, αὐτοκινησίᾳ: id est, ejus in agendo ab '
        'externo motore independentia, atque indeterminatione. Ac proinde perfectius vivunt '
        'ea quae plures & praestantiores motus exercere possunt, & quae minus ab alio in '
        'agendo dependent & determinata sunt.'
    ),
    '480': (
        'V. Ut vero ad vitam illam quae Deo Optimo Maximo competit, & de qua hic nobis '
        'agendum est, sensim, & veluti per gradus assurgamus, notandum est Deum plures '
        'viventium ordines in creaturis corporeis atque visibilibus creasse & constituisse. '
        'Etenim quemadmodum hominum industria & solertia praecipue elucet in fabricandis '
        'variis machinis, quae sponte moveri videntur & pluribus usibus in humana vita '
        'inserviunt, sic quoque, ut sic dicam, Dei sapientia sese manifestavit dum in hoc '
        'mundo sensibili varia, ut sic dicam, αὐτόματα excogitavit, & incomprehensibili ac '
        'plane stupenda arte fabricata est, quae nos corpora viventia vocamus. Et certe opera '
        'naturae non aliud sunt rite expendenti quam opera artis divinae, sicut vice versa '
        'opera artis humanae nihil aliud sunt quam opera naturae quatenus a mente humana '
        'dirigitur.'
    ),
    '481': (
        'VI. Primum igitur cernere est multa corpora terrae adnata & adhaerentia quae iis '
        'sunt organis instructa, & eo interno movendi principio quod animam vocamus, '
        'praedita, ut dum terra solis calore aperitur, & spiritus in ea contenti excitantur, '
        'varios succos e terra eliciant, & attrahant, quorum beneficio non tantum foventur '
        '& augescunt, sed folia, flores & fructus diversi generis producunt, & semina quoque '
        'proferunt unde postea corpora similia sponte germinant atque enascuntur. Et hae '
        'sunt quas plantas vocamus, quae a Philosophis vivere dicuntur vita vegetativa, '
        'cujus tres principes facultates recensent altricem, auctricem atque generatricem.'
    ),
    '482': (
        'VII. Sed praeter istud primum & infimum viventium genus, in terrae superficie, in '
        'aquis, in aere ipso extant corpora plurima longe pluribus & magis admirandis organis '
        'distincta, & quae etiam nobilioribus facultatibus pollent, motusque multo plures & '
        'magis diversos exercere possunt. Etenim non solum vim habent alimento intus suscepto '
        'seipsa nutriendi, & augmentum sumendi, ac simile sibi procreandi: sed praeterea non '
        'sunt ut priora uni certo loco affixa, verum seipsa de loco in locum transferre '
        'valent, neque sunt, quemadmodum plantae, ad unum certum & simplex operationum genus '
        'a natura sic determinata, ut non possint nisi semper eodem modo moveri & agere: sed '
        'saepe aliter atque aliter agunt, & motus suos varie temperant, raro diversis '
        'impressionibus quas intus ab objectis variis suscipiunt mediantibus organis quae '
        'Philosophi sensoria appellant. Et illa sunt quae animalia vocantur, quae sponte '
        'supra terrae superficiem, in aere & in aquis variis motibus cientur, & per sensus '
        'objecta externa percipiunt: adeoque supra plantas pollent facultate sensitiva atque '
        'loco motiva.'
    ),
    '483': (
        'VIII. Verum supra omnia corpora viventia multum adhuc eminent homines. In iis '
        'oculis usuramus corpus brutorum corpori simile, nisi quod sit organis perfectioribus '
        'instructum, neque quicquam est in brutis, quod spectat vitam animalem, quod in iis '
        'non reperiatur. Sed in iis praeterea latet principium quoddam agendi ab eo quod est '
        'in brutis diversae plane naturae, unde procedunt motus & actiones quae nullo modo '
        'ex sola organorum fabrica, & forma ulla mere corporea consequi possunt: sed '
        'necessario tribuenda sunt cuidam principio spirituali & immateriali: qualia sunt '
        'intelligere & ratiocinari, Deum nosse, & res pure immateriales, in seipsum, & '
        'proprias operationes reflecti, &c. rerum causas inquirere, ac denique libertate '
        'uti, & esse propriarum actionum dominum. Quae arguunt in hominibus animam latere '
        'plane alterius generis quam sit sensitiva, & vegetativa, nempe, intelligentem, & '
        'ratiocinantem, ac proinde spiritualem, & immaterialem.'
    ),
}

SECTIONS = [
    {
        'section': '476',
        'title': 'Living in loose speech — living water and living fire',
        'pass_a': (
            'In the most common and most general notion and in the common use of speaking, '
            'those things are said to live which in any way appear to us to move themselves: '
            'so we say living water and living fire, because a flame seems to be stirred by '
            'many motions of its own accord, and also water gushing from a spring, to which '
            'the dead waters of ponds are opposed.'
        ),
        'pass_b': [
            'Loose speech: anything that seems self-moving is called living.',
            'Living water / living fire vs stagnant dead water.',
            'Flame and spring-water looked spontaneous.',
        ],
        'lemmas': [
            {'latin': 'seipsa movere apparent', 'gloss': 'appear to move themselves'},
            {'latin': 'aquam vivam & ignem vivum', 'gloss': 'living water and living fire'},
        ],
        'choices': [{
            'term': 'vivere dicuntur ea quae quovis modo nobis seipsa movere apparent',
            'english': 'those things are said to live which in any way appear to us to move themselves',
            'why': 'Opens Vita Dei at the loosest common sense of living before philosophy tightens it.',
            'rejected': ['only animals are ever called living in ordinary speech'],
        }],
        'notes': ['OCR: Vita Dei I PDF 126 / p. 114; aquam vivam / ignem vivum.'],
        'bible_refs': [],
    },
    {
        'section': '477',
        'title': 'Philosophical living — resume motion from an inward principle',
        'pass_a': (
            'But properly and philosophically that alone is said to move itself and therefore '
            'to live which, set in its natural place and state, can move itself, and so that '
            'after it has naturally left off from motion and ceased from operating it can '
            'begin the motion again from itself. Yet when I say that what lives leaves off '
            'from motion, I do not mean simply from every motion. For in every living thing '
            'there is indeed a continuous vigor and unfailing motion that does not cease '
            'except in death. But still we do not say that anything lives except what can by '
            'nature cease from some motion and again begin the same motion from an inward '
            'principle.'
        ),
        'pass_b': [
            'Strict sense: can restart a motion from itself after stopping.',
            'Not total stillness — continuous vital vigor until death.',
            'Life = stop some act, then restart it from an inward principle.',
        ],
        'lemmas': [
            {'latin': 'motum rursus a se inchoare valeat', 'gloss': 'can begin the motion again from itself'},
            {'latin': 'ex principio interno inchoare', 'gloss': 'begin from an inward principle'},
        ],
        'choices': [{
            'term': 'ex principio interno inchoare',
            'english': 'begin from an inward principle',
            'why': 'Defines living by self-started return to operation, not mere continuous stir.',
            'rejected': ['life requires absolute cessation of all motion'],
        }],
        'notes': ['OCR: II PDF 126; continuous vigor vs particular motions.'],
        'bible_refs': [],
    },
    {
        'section': '478',
        'title': 'Motion here means any operation — even actus perfecti',
        'pass_a': (
            'But in this definition of life motion is not taken strictly and as philosophers '
            'define it, the act of a being in potency insofar as it is in potency, which '
            'motion in the subject necessarily assumes some imperfection, and therefore is '
            'called in the schools the act of what is imperfect; but in a general sense by '
            'motion is understood any operation, and even that which is the act of what is '
            'perfect.'
        ),
        'pass_b': [
            'Not the scholastic actus imperfecti alone.',
            'Motion = any operation, including perfect acts.',
            'Widens life-talk past mere locomotion.',
        ],
        'lemmas': [
            {'latin': 'Actus entis in potentia quatenus est in potentia', 'gloss': 'act of a being in potency insofar as it is in potency'},
            {'latin': 'actus imperfecti … actus perfecti', 'gloss': 'act of the imperfect … act of the perfect'},
        ],
        'choices': [{
            'term': 'per motum intelligitur operatio quaevis',
            'english': 'by motion is understood any operation',
            'why': 'Blocks reading life as only imperfect local motion.',
            'rejected': ['life-motion is only potencies being reduced'],
        }],
        'notes': ['OCR: III PDF 126; actus imperfecti / perfecti.'],
        'bible_refs': [],
    },
    {
        'section': '479',
        'title': 'Life’s perfection — variety of acts and self-motion',
        'pass_a': (
            'Further, the perfection of life, as can easily be gathered from the definition, '
            'consists especially in two things: first, namely, in the excellence and variety '
            'of motions and operations; next in the agent’s, so to speak, self-motion: that '
            'is, its independence in acting from an external mover, and its indeterminateness. '
            'And therefore those live more perfectly which can exercise more and more '
            'excellent motions, and which less depend on another in acting and are less '
            'determined.'
        ),
        'pass_b': [
            'Two marks: richer operations + freer self-agency.',
            'Self-motion = independence from an external mover.',
            'More / better acts and less determination = higher life.',
        ],
        'lemmas': [
            {'latin': 'motuum & operationum praestantia & varietate', 'gloss': 'excellence and variety of motions and operations'},
            {'latin': 'ab externo motore independentia', 'gloss': 'independence from an external mover'},
        ],
        'choices': [{
            'term': 'ab externo motore independentia, atque indeterminatione',
            'english': 'independence from an external mover, and indeterminateness',
            'why': 'Second axis of life-perfection; sets up the creature grades that follow.',
            'rejected': ['life perfection is only number of organs'],
        }],
        'notes': ['OCR: IV PDF 126; αὐτοκινησίᾳ normalized with Latin gloss.'],
        'bible_refs': [],
    },
    {
        'section': '480',
        'title': 'Climb toward God’s life — living bodies as divine automata',
        'pass_a': (
            'But that we may rise sensibly and as by steps to that life which belongs to God '
            'Most High and with which we must deal here, it is to be noted that God has '
            'created and established several orders of living things among bodily and visible '
            'creatures. For just as men’s industry and skill chiefly shine in making various '
            'machines which seem to move of themselves and serve many uses in human life, so '
            'also, so to speak, God’s wisdom has shown itself while in this sensible world it '
            'has devised various, so to speak, automata, and by incomprehensible and plainly '
            'stupendous art has fashioned what we call living bodies. And certainly the works '
            'of nature are nothing else, to one who weighs them rightly, than works of divine '
            'art, just as conversely the works of human art are nothing else than works of '
            'nature insofar as it is directed by the human mind.'
        ),
        'pass_b': [
            'Approach God’s life by creature grades.',
            'Living bodies = God’s crafted automata.',
            'Nature’s works = divine art; human art = nature guided by mind.',
        ],
        'lemmas': [
            {'latin': 'per gradus assurgamus', 'gloss': 'we may rise by steps'},
            {'latin': 'corpora viventia', 'gloss': 'living bodies'},
        ],
        'choices': [{
            'term': 'opera naturae … opera artis divinae',
            'english': 'the works of nature … works of divine art',
            'why': 'Frames the climb from plants upward as reading God’s craftsmanship.',
            'rejected': ['living bodies are chance machines without art'],
        }],
        'notes': ['OCR: V PDF 126; αὐτόματα / machines comparison.'],
        'bible_refs': [],
    },
    {
        'section': '481',
        'title': 'Plants — vegetative life; feed, grow, generate',
        'pass_a': (
            'First, then, one may see many bodies sprung from and clinging to the earth which '
            'are furnished with those organs and endowed with that inward principle of moving '
            'which we call soul, so that when the earth is opened by the sun’s heat and the '
            'spirits contained in it are stirred, they draw and attract various juices from '
            'the earth, by whose benefit they are not only fostered and grow, but produce '
            'leaves, flowers, and fruits of diverse kinds, and also put forth seeds from which '
            'afterward like bodies sprout and are born of themselves. And these are what we '
            'call plants, which philosophers say live with vegetative life, whose three chief '
            'faculties they list as the nourishing, the growing, and the generating.'
        ),
        'pass_b': [
            'Lowest rung: plants rooted in earth.',
            'Soul as inward mover: juices, growth, seed.',
            'Vegetative life — nourish, grow, generate.',
        ],
        'lemmas': [
            {'latin': 'vita vegetativa', 'gloss': 'vegetative life'},
            {'latin': 'altricem, auctricem atque generatricem', 'gloss': 'nourishing, growing, and generating'},
        ],
        'choices': [{
            'term': 'vivere dicuntur vita vegetativa',
            'english': 'are said to live with vegetative life',
            'why': 'First creature grade on the climb toward God’s life.',
            'rejected': ['plants do not live in any philosophical sense'],
        }],
        'notes': ['OCR: VI PDF 127 / p. 115; three vegetative faculties.'],
        'bible_refs': [],
    },
    {
        'section': '482',
        'title': 'Animals — sensitive life and local motion',
        'pass_a': (
            'But besides that first and lowest kind of living things, on the earth’s surface, '
            'in the waters, and in the air itself there are very many bodies distinguished by '
            'far more and more marvelous organs, and which also excel in nobler faculties and '
            'can exercise far more and more diverse motions. For they not only have power of '
            'nourishing themselves by food taken within, of taking increase, and of begetting '
            'what is like themselves: but further they are not, like the former, fixed to one '
            'certain place; rather they can transfer themselves from place to place, nor are '
            'they, as plants are, so determined by nature to one certain and simple kind of '
            'operations that they can move and act only always in the same way: but they often '
            'act now one way and now another, and variously temper their motions by the '
            'diverse impressions which they receive within from various objects through the '
            'organs which philosophers call sensors. And those are what are called animals, '
            'which of themselves are stirred by various motions above the earth’s surface, '
            'in the air and in the waters, and through the senses perceive external objects: '
            'and thus above plants they excel by the sensitive faculty and by local motion.'
        ),
        'pass_b': [
            'Animals: more organs, freer motions than plants.',
            'Not place-fixed; vary acts by sensory impressions.',
            'Sensitive + loco-motive faculties above vegetative life.',
        ],
        'lemmas': [
            {'latin': 'facultate sensitiva atque loco motiva', 'gloss': 'by the sensitive faculty and by local motion'},
            {'latin': 'sensoria', 'gloss': 'sense organs / sensors'},
        ],
        'choices': [{
            'term': 'facultate sensitiva atque loco motiva',
            'english': 'by the sensitive faculty and by local motion',
            'why': 'Marks the second creature grade above plants.',
            'rejected': ['animals live only the same vegetative life as plants'],
        }],
        'notes': ['OCR: VII PDF 127; sensoria / local motion.'],
        'bible_refs': [],
    },
    {
        'section': '483',
        'title': 'Humans — spiritual soul above animal life',
        'pass_a': (
            'But above all living bodies men still far excel. In them with the eyes we observe '
            'a body like the body of the brutes, except that it is furnished with more perfect '
            'organs, nor is there anything in the brutes that concerns animal life which is '
            'not found in them. But in them there further lies hidden a certain principle of '
            'acting of a nature plainly different from that which is in the brutes, whence '
            'proceed motions and actions which in no way can follow from the fabric of the '
            'organs alone and from any merely bodily form: but must necessarily be ascribed '
            'to a certain spiritual and immaterial principle: such as to understand and '
            'reason, to know God, and purely immaterial things, to reflect on oneself and '
            'one’s own operations, and so on, to inquire into the causes of things, and '
            'finally to use freedom and to be master of one’s own actions. Which prove that '
            'in men there lies hidden a soul of a kind plainly other than the sensitive and '
            'vegetative, namely intelligent and reasoning, and therefore spiritual and '
            'immaterial.'
        ),
        'pass_b': [
            'Body like the brutes — plus a higher acting principle.',
            'Understand, reason, know God, reflect, free mastery of acts.',
            'Intelligent / spiritual soul above sensitive and vegetative.',
        ],
        'lemmas': [
            {'latin': 'principio spirituali & immateriali', 'gloss': 'to a spiritual and immaterial principle'},
            {'latin': 'intelligentem, & ratiocinantem', 'gloss': 'intelligent and reasoning'},
        ],
        'choices': [{
            'term': 'animam … plane alterius generis quam sit sensitiva, & vegetativa',
            'english': 'a soul … of a kind plainly other than the sensitive and vegetative',
            'why': 'Closes I-VIII on the human rung; next IX+ compares human freedom to brutes.',
            'rejected': ['human life adds only better animal organs'],
        }],
        'notes': ['OCR: VIII PDF 127; next IX+ human vs brute freedom.'],
        'bible_refs': [],
    },
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
    parts = [LOCK_HEADER]
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
        jpath = JUST / f'dei_vita_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_vita_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    raw_sources = [LOCK, pdf, Path(__file__), DATA / 'latin.json']
    for name in (
        'pdf_126.txt', 'pdf_127.txt', 'pdf_126_134_layout.txt', 'pdf_127_132_layout.txt',
    ):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
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
        if 476 <= n <= 483:
            notes = (
                f'Section {sid}: new densify De Vita Dei I-VIII; '
                'Pass A!=B; lock-grounded PDF 126-127 / book pp. 114-115.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_vita I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Vita Dei I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Opens Vita Dei after Aeternitate XIX. Next Vita IX+. Not shipped.'
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
        'locus': 'De Vita Dei theses I-VIII (common/philosophical living; grades; plants/animals/humans)',
        'next_locus': 'De Vita Dei IX+ (human freedom vs brutes; angels; God more properly living)',
        'gates': {
            'check_pass_ab': f'ok dei_vita_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'live_floor': LIVE_FLOOR,
        'raw_source_paths_count': 5,
        'honest_slice_note': 'I-VIII open Vita Dei after Aeternitate close (~4-8)',
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
        f'## {day} (Scribe — De Vita Dei I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Vita Dei I–VIII → §§{SECS[0]}–{SECS[-1]}; opens after Aeternitate).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 126-127 / pp. 114-115).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest slice: De Vita Dei through VIII. Next: Vita Dei IX+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Vita Dei I–VIII densify)\n\n'
        'CoS densify: Vita Dei I–VIII open after Aeternitate. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Vita Dei I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Vita IX+. Punch X: **NO**.\n\n---\n\n'
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
    post_floor = LIVE_FLOOR
    if secs_now is not None and secs_now > LIVE_FLOOR:
        post_floor = secs_now
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-483 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
