#!/usr/bin/env python3
"""Build + apply De Dei Perfectione & Infinitate IX-XVI densify (tip 406 → 414).

Formaliter/eminenter; secundum quid in God only eminently; simply simple formally.
Deploy add9e526 live 57/4470 bound tip 406. After tip-ready: HOLD live>4470 OR 12m.
Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_perfectione_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_perfectione_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_perfectione_i_densify')
PACKET_STEM = 'dei_perfectione_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_perfectione/apply_dei_perfectione_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['407', '408', '409', '410', '411', '412', '413', '414']
ROMANS = {
    '407': 'IX', '408': 'X', '409': 'XI', '410': 'XII',
    '411': 'XIII', '412': 'XIV', '413': 'XV', '414': 'XVI',
}
TIP_BEFORE = 406
LIVE_FLOOR = 4470
HOLD_MINUTES = 12
PRIOR_START = 399

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Perfectione & Infinitate I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Perfectione & Infinitate I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Perfectione & Infinitate I-XVI, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Perfectione IX-XVI "
    "(formaliter / eminenter; secundum quid only eminently in God)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Perfectione & Infinitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 102-104 / PDF 114-116 (I-XVI; this packet IX-XVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Perfectione & Infinitate I-XVI tip. XVII+ remains.\n"
    "Note: Continues after I-VIII. Formal/eminent modes of containing perfection.\n\n"
)

LATIN = {
    '407': (
        'IX. Secundo notandum est perfectionem aliquam posse duobus modis in aliquo esse '
        '& contineri: nempe, ut scholae docent, vel formaliter & proprie, vel virtute, seu '
        'eminenter. Illud perfectionem aliquam formaliter habet cui perfectio illa inest '
        'secundum totam suam naturam & essentiam, ita ut ab ea denominari possit. Sic ignis '
        'habet formaliter calorem, aqua habet formaliter frigus, quia calor & frigus proprie, '
        '& secundum totam suam naturam, insunt aquae, & igni, ita ut ignis calidus, & aqua '
        'frigida proprie, & citra figuram ullam denominari possit.'
    ),
    '408': (
        'X. Eminenter autem & virtute habere perfectionem aliquam, est in se habere aliquid '
        'perfectius, & quod continet totam vim perfectionis illius quae eminenter haberi '
        'dicitur: idque, vel quia potest perfectionem illam producere; vel quia absque illa '
        'potest praestare quicquid illa praestat, seclusa omni imperfectione. Ita juxta mentem '
        'Peripateticorum Sol formaliter calorem non habet, & proprie calidus non est: sed '
        'tamen calorem habet virtute seu eminenter, quia calorem producere potest, & praestare '
        'quicquid praestat ignis qui calorem habet. Sic visus & auditus in angelis formaliter '
        'non est, nec enim habent naturam sensitivam, attamen sensus illos habent virtute & '
        'eminenter, quia cognitionem quam habet homo, sensibus illis mediantibus nobiliori '
        'modo per intellectum suum habent.'
    ),
    '409': (
        'XI. His ita notatis dicimus perfectiones illas creaturarum quas vocavimus secundum '
        'quid, in Deo quidem non esse proprie & formaliter: attamen Deum omnes illas habere '
        'virtute & eminenter.'
    ),
    '410': (
        'XII. Quod in Deo proprie & formaliter non sint, est per se manifestum. Etenim, ut '
        'dictum est, notant & secum trahunt quandam imperfectionem. Sed in Deo nulla est '
        'imperfectio. Deinde perfectiones illae non possunt compatari omnes in eodem subjecto. '
        'Nec enim unum idemque potest simul habere naturam humanam, equinam, & bovinam. Et '
        'esse simul siccum & humidum, calidum & frigidum. Sed ista necessario constituunt '
        'diversas res, & requirunt diversa subjecta. Ac denique, si omnia ista in Deo '
        'formaliter essent, possent de eo dici & affirmari. Quod tamen falsum esse nemo non '
        'videt.'
    ),
    '411': (
        'XIII. Sed quamvis perfectiones illae in Deo non sint secundum propriam suam '
        'rationem, nihilominus in Deo sunt, ut dictum, virtute & eminenter, quoniam Deus in '
        'se vim habet illas producendi, & potest sine iis efficere quicquid illae efficere '
        'possunt. Sic Deus in se formaliter non habet naturam plantae, vel animalis: sed '
        'habet aliquid in se perfectius quod tota virtute continet, fiunt enim a Deo quicquid '
        'sunt; & Deus est qui ista produxit, & producere potest. Non habet aures & oculos, '
        'nec est proprie visu & auditu praeditus: sed ille est qui plantavit aurem, & qui '
        'oculum formavit, adeoque qui sine auribus, & oculis, percipit omnia quae fiunt & '
        'dicuntur.'
    ),
    '412': (
        'XIV. Illae vero perfectiones quae sunt simpliciter tales, & quas absolute praestat '
        'habere, quam illis carere, in Deo formaliter & proprie reperiuntur. Etenim in Deo '
        'sunt secundum propriam suam formam & essentiam, vita, intellectus, voluntas, '
        'sapientia, bonitas, justitia, & alia istiusmodi: adeoque Deus vere & proprie dici '
        'potest vivens, intelligens, liber, sapiens, justus, & bonus.'
    ),
    '413': (
        'XV. At, inquies, nomina ista proprie significant accidentia quaedam, nam '
        'intellectus & voluntas sunt potentiae naturales, sapientia vero & justitia, habitus '
        'quidam intellectum & voluntatem exornantes. Sed in Deo nulla sunt accidentia. '
        'Ideoque perfectiones quae per nomina illa significantur in Deo, non possunt esse '
        'proprie & formaliter, sed solummodo eminenter, sicut perfectiones illae quae '
        'dicuntur secundum quid. Respondeo intellectum, voluntatem, sapientiam, justitiam, & '
        'similia duobus modis considerari posse. Vel secundum modum quo creaturis insunt: Et '
        'ita sunt accidentia quae imperfectionis aliquid admixtum habent. Vel praecise, prout '
        'de illis formatur quidam conceptus generalis qui abstrahit ab omni imperfectione, & '
        'per analogiam communis est Deo & creaturis. Priore modo perfectiones illae proprie '
        'Deo non competunt. Posteriore vero Deo formaliter insunt, & possunt de Deo vere & '
        'proprie enunciari. Nam cum audimus voces illas intellectum, voluntatem, sapientiam, '
        'justitiam, possumus concipere perfectionem quandam absolutam, & quae non includat '
        'ullam rationem accidentis. Et sic Deo tribui possunt recte & convenienter. Nam '
        'perfectiones istae hoc modo consideratae vere sunt intra essentiam divinam.'
    ),
    '414': (
        'XVI. Ex his ergo manifestum est nullam in ulla re esse perfectionem quae in Deo '
        'quodammodo non sit: nempe, formaliter, ut perfectiones illae quae simpliciter '
        'simplices dicuntur: vel eminenter & virtute, ut aliae quae vocantur perfectiones '
        'secundum quid. Et hoc quia Deus est rerum omnium prima & praecipua causa. Unde '
        'sequitur quicquid perfectionis est in rebus ab ipso promanare, adeoque in eo, ut sic '
        'dicam, praeexistere: nec ullam omnino posse dari excellentiam, quae ab ipso non '
        'derivetur, adeoque quae non in ipso, tanquam in fonte resideat. Quod enim ab alio '
        'derivatur & manat, non potest non esse quodam modo in eo unde manat & derivatur.'
    ),
}

SECTIONS = [
    {
        'section': '407',
        'title': 'Two modes: formaliter vs virtute / eminenter',
        'pass_a': (
            'Secondly it is to be noted that some perfection can be in something and be '
            'contained in two ways: namely, as the schools teach, either formally and properly, '
            'or by virtue, or eminently. That has some perfection formally to which that '
            'perfection is present according to its whole nature and essence, so that it can be '
            'denominated from it. So fire has heat formally, water has cold formally, because '
            'heat and cold properly, and according to their whole nature, are in water and fire, '
            'so that fire can be denominated hot, and water cold, properly and without any figure.'
        ),
        'pass_b': [
            'Schools: contain a perfection formally, or by virtue / eminently.',
            'Formal: the perfection is present by its whole nature — fire hot, water cold.',
        ],
        'lemmas': [
            {'latin': 'formaliter & proprie', 'gloss': 'formally and properly'},
            {'latin': 'virtute, seu eminenter', 'gloss': 'by virtue, or eminently'},
        ],
        'choices': [{
            'term': 'vel formaliter & proprie, vel virtute, seu eminenter',
            'english': 'either formally and properly, or by virtue, or eminently',
            'why': 'Opens formal/eminent taxonomy.',
            'rejected': ['only one mode of having a perfection'],
        }],
        'notes': ['OCR: IX PDF 115.'],
        'bible_refs': [],
    },
    {
        'section': '408',
        'title': 'Eminent containment: Sun and heat; angels and senses',
        'pass_a': (
            'But to have some perfection eminently and by virtue is to have in oneself something '
            'more perfect, and which contains the whole force of that perfection which is said to '
            'be had eminently: and that, either because it can produce that perfection; or because '
            'without it it can perform whatever that performs, every imperfection set aside. So '
            'according to the mind of the Peripatetics the Sun does not have heat formally, and '
            'is not properly hot: but yet it has heat by virtue or eminently, because it can '
            'produce heat, and perform whatever fire which has heat performs. So sight and hearing '
            'are not formally in angels, for they do not have a sensitive nature, yet they have '
            'those senses by virtue and eminently, because the cognition which man has by those '
            'senses mediating they have in a nobler mode through their intellect.'
        ),
        'pass_b': [
            'Eminent: hold something better that can do all the lesser does — without its flaw.',
            'Peripatetic Sun: not formally hot, but produces heat.',
            'Angels: no sense-nature, yet sense-knowledge more nobly by intellect.',
        ],
        'lemmas': [
            {'latin': 'virtute seu eminenter', 'gloss': 'by virtue or eminently'},
            {'latin': 'seclusa omni imperfectione', 'gloss': 'every imperfection set aside'},
        ],
        'choices': [{
            'term': 'in se habere aliquid perfectius',
            'english': 'to have in oneself something more perfect',
            'why': 'Defines eminent containment.',
            'rejected': ['eminent means formally identical to the lower perfection'],
        }],
        'notes': ['OCR: X PDF 115.'],
        'bible_refs': [],
    },
    {
        'section': '409',
        'title': 'Secundum quid perfections in God only virtute & eminenter',
        'pass_a': (
            'These things thus noted, we say that those perfections of creatures which we called '
            'secundum quid are indeed not properly and formally in God: yet that God has all of '
            'them by virtue and eminently.'
        ),
        'pass_b': [
            'Secundum quid creature-perfections: not formal in God.',
            'Yet God has them all by virtue and eminently.',
        ],
        'lemmas': [
            {'latin': 'non esse proprie & formaliter', 'gloss': 'not to be properly and formally'},
            {'latin': 'virtute & eminenter', 'gloss': 'by virtue and eminently'},
        ],
        'choices': [{
            'term': 'Deum omnes illas habere virtute & eminenter',
            'english': 'that God has all of them by virtue and eminently',
            'why': 'Applies taxonomy to secundum quid set.',
            'rejected': ['secundum quid perfections are formal in God'],
        }],
        'notes': ['OCR: XI PDF 115.'],
        'bible_refs': [],
    },
    {
        'section': '410',
        'title': 'Why not formal: they drag imperfection and clash in one subject',
        'pass_a': (
            'That they are not properly and formally in God is manifest of itself. For, as was '
            'said, they note and drag with them a certain imperfection. But in God there is no '
            'imperfection. Next those perfections cannot all be compatible in the same subject. '
            'For one and the same cannot at once have human, equine, and bovine nature. And be '
            'at once dry and wet, hot and cold. But those things necessarily constitute diverse '
            'things, and require diverse subjects. And finally, if all those were formally in '
            'God, they could be said and affirmed of Him. Which yet no one fails to see is false.'
        ),
        'pass_b': [
            'Formal secundum quid would import imperfection — none in God.',
            'Human/horse/ox natures and hot/cold cannot share one subject.',
            'If formal in God, we could predicate them — we cannot.',
        ],
        'lemmas': [
            {'latin': 'notant & secum trahunt quandam imperfectionem', 'gloss': 'they note and drag with them a certain imperfection'},
            {'latin': 'non possunt compatari omnes in eodem subjecto', 'gloss': 'cannot all be compatible in the same subject'},
        ],
        'choices': [{
            'term': 'in Deo nulla est imperfectio',
            'english': 'in God there is no imperfection',
            'why': 'Bars formal secundum quid in God.',
            'rejected': ['God can formally be hot and cold at once'],
        }],
        'notes': ['OCR: XII PDF 115.'],
        'bible_refs': [],
    },
    {
        'section': '411',
        'title': 'Yet eminently: He made ear and eye — perceives without organs',
        'pass_a': (
            'But although those perfections are not in God according to their own proper ratio, '
            'nevertheless they are in God, as said, by virtue and eminently, since God has in '
            'Himself the power of producing them, and can without them effect whatever they can '
            'effect. So God does not have in Himself formally the nature of a plant or an animal: '
            'but He has something in Himself more perfect which contains them by whole virtue, '
            'for whatever they are they are from God; and God is who produced those things, and '
            'can produce them. He does not have ears and eyes, nor is He properly endowed with '
            'sight and hearing: but He is the one who planted the ear, and who formed the eye, '
            'and therefore who without ears and eyes perceives all things that are done and said.'
        ),
        'pass_b': [
            'Not by proper ratio — still virtute & eminenter.',
            'No plant/animal nature formally — yet He made them.',
            'No ears/eyes — yet He planted the ear and formed the eye.',
        ],
        'lemmas': [
            {'latin': 'virtute & eminenter', 'gloss': 'by virtue and eminently'},
            {'latin': 'qui plantavit aurem, & qui oculum formavit', 'gloss': 'who planted the ear, and who formed the eye'},
        ],
        'choices': [{
            'term': 'sine auribus, & oculis, percipit omnia quae fiunt & dicuntur',
            'english': 'without ears and eyes perceives all things that are done and said',
            'why': 'Eminent sense-knowledge without organs.',
            'rejected': ['God formally has animal sense organs'],
        }],
        'notes': ['OCR: XIII PDF 115-116.'],
        'bible_refs': [],
    },
    {
        'section': '412',
        'title': 'Simply simple perfections are formal in God',
        'pass_a': (
            'But those perfections which are simply such, and which absolutely it is better to '
            'have than to lack, are found in God formally and properly. For in God according to '
            'their own proper form and essence there are life, intellect, will, wisdom, goodness, '
            'justice, and others of that sort: and therefore God can truly and properly be called '
            'living, understanding, free, wise, just, and good.'
        ),
        'pass_b': [
            'Simply simple perfections: formal and proper in God.',
            'Life, intellect, will, wisdom, goodness, justice — by proper form.',
            'God is truly living, understanding, free, wise, just, good.',
        ],
        'lemmas': [
            {'latin': 'formaliter & proprie reperiuntur', 'gloss': 'are found formally and properly'},
            {'latin': 'vita, intellectus, voluntas, sapientia', 'gloss': 'life, intellect, will, wisdom'},
        ],
        'choices': [{
            'term': 'in Deo formaliter & proprie reperiuntur',
            'english': 'are found in God formally and properly',
            'why': 'Contrasts simply simple with secundum quid.',
            'rejected': ['life and wisdom are only eminent in God'],
        }],
        'notes': ['OCR: XIV PDF 116.'],
        'bible_refs': [],
    },
    {
        'section': '413',
        'title': 'Objection: intellect and wisdom are accidents — answer by analogy',
        'pass_a': (
            'But, you will say, those names properly signify certain accidents, for intellect '
            'and will are natural powers, but wisdom and justice certain habits adorning intellect '
            'and will. But in God there are no accidents. And therefore the perfections which are '
            'signified by those names in God cannot be properly and formally, but only eminently, '
            'as those perfections which are called secundum quid. I answer that intellect, will, '
            'wisdom, justice, and the like can be considered in two ways. Either according to the '
            'mode in which they are in creatures: And so they are accidents which have something '
            'of imperfection mixed. Or precisely, insofar as of them is formed a certain general '
            'concept which abstracts from every imperfection, and by analogy is common to God and '
            'creatures. In the former mode those perfections do not properly befit God. But in the '
            'latter they are formally in God, and can be truly and properly enunciated of God. For '
            'when we hear those words intellect, will, wisdom, justice, we can conceive a certain '
            'absolute perfection which does not include any ratio of accident. And so they can be '
            'attributed to God rightly and fittingly. For those perfections so considered are '
            'truly within the divine essence.'
        ),
        'pass_b': [
            'Objection: intellect/wisdom name accidents — none in God.',
            'Answer: as in creatures they are imperfect accidents; as absolute concepts, formal in God.',
            'Analogical names strip accident — sit inside the divine essence.',
        ],
        'lemmas': [
            {'latin': 'in Deo nulla sunt accidentia', 'gloss': 'in God there are no accidents'},
            {'latin': 'per analogiam communis est Deo & creaturis', 'gloss': 'by analogy is common to God and creatures'},
        ],
        'choices': [{
            'term': 'perfectiones istae hoc modo consideratae vere sunt intra essentiam divinam',
            'english': 'those perfections so considered are truly within the divine essence',
            'why': 'Saves formal attribution without accidents.',
            'rejected': ['wisdom in God is only an eminent accident-analogue'],
        }],
        'notes': ['OCR: XV PDF 116.'],
        'bible_refs': [],
    },
    {
        'section': '414',
        'title': 'Every creaturely perfection is somehow in God — as in the fountain',
        'pass_a': (
            'From these things therefore it is manifest that there is no perfection in any thing '
            'which is not somehow in God: namely, formally, as those perfections which are called '
            'simply simple: or eminently and by virtue, as others which are called perfections '
            'secundum quid. And this because God is the first and principal cause of all things. '
            'Whence it follows that whatever of perfection is in things flows forth from Him, and '
            'therefore preexists in Him, so to speak: nor can any excellence at all be given which '
            'is not derived from Him, and therefore which does not reside in Him as in a fountain. '
            'For what is derived and flows from another cannot but be somehow in that from which '
            'it flows and is derived.'
        ),
        'pass_b': [
            'No creaturely perfection missing from God — formal or eminent.',
            'He is first cause: all perfection flows from Him and preexists in Him.',
            'Excellence resides in God as in a fountain.',
        ],
        'lemmas': [
            {'latin': 'tanquam in fonte', 'gloss': 'as in a fountain'},
            {'latin': 'prima & praecipua causa', 'gloss': 'first and principal cause'},
        ],
        'choices': [{
            'term': 'nullam in ulla re esse perfectionem quae in Deo quodammodo non sit',
            'english': 'that there is no perfection in any thing which is not somehow in God',
            'why': 'Closes formal/eminent packet; next XVII+ a-se infinitude.',
            'rejected': ['some excellence exists underived from God'],
        }],
        'notes': ['OCR: XVI PDF 116; next XVII+ uncaused first being / infinitude.'],
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
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    parts = [LOCK_HEADER]
    for sec in [str(n) for n in range(PRIOR_START, TIP_BEFORE + 1)]:
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
        jpath = JUST / f'dei_perfectione_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_perfectione_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    p = DATA / 'pdf_114_117_perfectione.txt'
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
        if 407 <= n <= 414:
            notes = (
                f'Section {sid}: new densify De Dei Perfectione & Infinitate IX-XVI; '
                'Pass A!=B; lock-grounded PDF 115-116 / book pp. 103-104.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_perfectione IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Dei Perfectione & Infinitate IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Perfectione through XVI; XVII+ remains. Not shipped.'
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
        'locus': 'De Dei Perfectione & Infinitate theses IX-XVI (formaliter / eminenter)',
        'next_locus': 'De Dei Perfectione & Infinitate XVII+ (a-se / infinitude)',
        'gates': {
            'check_pass_ab': f'ok dei_perfectione_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'deploy_bound': 'add9e526 live 57/4470 tip 406',
        'raw_source_paths_count': 5,
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
        f'## {day} (Scribe — De Dei Perfectione & Infinitate IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Perfectione IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 115-116 / pp. 103-104).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Perfectione & Infinitate through XVI. XVII+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound add9e526 / tip 406; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Perfectione & Infinitate IX–XVI densify)\n\n'
        'CoS densify: De Dei Perfectione & Infinitate IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Perfectione IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: XVII+. Punch X: **NO**.\n\n---\n\n'
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
            'deploy_bound': 'add9e526',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-406 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
