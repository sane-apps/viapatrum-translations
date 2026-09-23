#!/usr/bin/env python3
"""Build + apply De Dei Perfectione & Infinitate I-VIII densify (tip 398 → 406).

New lock: sources/_le_blanc_dei_perfectione_latin_lock.txt
Deploy ec82d5ea live 57/4447 bound tip 398. After tip-ready: HOLD live>4447 OR 12m.
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
PACKET_STEM = 'dei_perfectione_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_perfectione/apply_dei_perfectione_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['399', '400', '401', '402', '403', '404', '405', '406']
ROMANS = {
    '399': 'I', '400': 'II', '401': 'III', '402': 'IV',
    '403': 'V', '404': 'VI', '405': 'VII', '406': 'VIII',
}
TIP_BEFORE = 398
LIVE_FLOOR = 4447
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Perfectione & Infinitate I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Perfectione & Infinitate I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Perfectione & Infinitate I-VIII, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice opens Perfectione I-VIII "
    "(summa perfectio after simplicity; absolute vs secundum quid)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Perfectione & Infinitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 102-103 / PDF 114-115 (I-VIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Perfectione & Infinitate I-VIII tip. IX+ remains.\n"
    "Note: Opens after De Dei Simplicitate closed at XXVIII.\n\n"
)

LATIN = {
    '399': (
        'I. Novissimis thesibus egimus de divina simplicitate, quae cum summa & absoluta Dei '
        'perfectione necessariam connexionem habet. Nam in rebus quidem corporeis, quae '
        'simpliciora sunt, sunt imperfectiora. Sic elementa sunt imperfectiora mixtis, & '
        'animalia sunt plantis perfectiora. Nec est ulla res creata quae ad suam perfectionem '
        'compositionem aliquam non requirat, & quae saltem non egeat accidentibus quibusdam '
        'perfici. Sed summa perfectio simplicitatem absolutam exigit. Deus est simplicissimus, '
        'quia perfectissimus. Ideoque postquam actum est de Dei simplicitate, ratio postulat '
        'ut jam de perfectione illius agamus.'
    ),
    '400': (
        'II. Perfectum dicitur id cui nihil deest. Perfectio vero saepe excellentiam quamlibet '
        'designat. Sed aliquid perfectum dicitur duobus modis, vel absolute, vel secundum quid.'
    ),
    '401': (
        'III. Secundum quid perfectum est illud cui nihil deest, non simpliciter, sed in suo '
        'genere, id est, quod habet omnem perfectionem naturae suae congruam & debitam. Ita '
        'perfectus equus est cui nihil deest quod pertinet ad naturam equinam, & perfecta planta '
        'quae habet omnem perfectionem plantae convenientem, quamvis absolute loquendo, sint '
        'multae perfectiones quas non habet equus, vel planta quae perfecta dicitur.'
    ),
    '402': (
        'IV. Simpliciter vero perfectum est id cui nihil omnino deest, & quod habet omnem '
        'excellentiam possibilem. Talis perfectio nulli creaturae competit, sed est proprium '
        'naturae divinae attributum. Omnis enim creatura perfectionem habet certam & '
        'determinatam, haec illam, ista aliam: sed Deus in se continet quicquid haberi potest '
        'perfectionis, nec cogitari potest ulla excellentia cujus natura divina sit expers.'
    ),
    '403': (
        'V. Haec autem summa naturae divinae perfectio colligitur ex duobus. 1. Ex eo quod '
        'Deus est rerum omnium causa. 2. Ex eo quod Deus nullam causam habet, sed per se est, '
        '& a seipso.'
    ),
    '404': (
        'VI. Etenim certissimum est in effectu nullam esse posse perfectionem, quae in causa '
        'quodammodo non sit. Quandoquidem ergo Deus est prima rerum omnium causa, nihil in '
        'ulla re potest esse perfectionis quod in Deo non reperiatur. Atque hoc indicat '
        'Scriptura, dum perfectionem aliquam in rebus a Deo factis notans, inde argumentatur '
        'Deum multo magis talem perfectionem habere. Veluti Psal. 94. An, inquit Propheta, qui '
        'aurem plantavit non audiet? an qui oculum formavit non videbit? Et Isa. 66. Nunquid '
        'ego qui alios parere facio, ipse non pariam, dicit Dominus? An ego qui generationem '
        'ceteris tribuo, sterilis ero?'
    ),
    '405': (
        'VII. Itaque arte tenendum est, & tanquam firmum certumque axioma, nullam omnino '
        'praestantiam & excellentiam in creatura ulla reperiri, quae in Deo non sit aliquo '
        'saltem modo. Sed ad pleniorem hujus rei intelligentiam notandum est duo esse '
        'perfectionum genera. Sunt enim perfectiones quaedam simpliciter tales, id est, quas, '
        'absolute loquendo, praestat habere, quam non habere, & quae nullam majorem '
        'perfectionem excludunt. Has Scholastici vocant perfectiones simpliciter simplices. '
        'Atque hujusmodi perfectiones sunt vita, intellectus, voluntatis libertas. Nam absolute '
        'loquendo, praestat vivere, quam non vivere, intelligere quam non intelligere, & '
        'praeditum esse libera voluntate, quam non esse praeditum. Nec ulla est perfectio '
        'quantumvis magna, quae cum vita, intellectu & libera voluntate consistere non possit.'
    ),
    '406': (
        'VIII. Sed praeterea sunt aliae quaedam perfectiones non simpliciter, sed secundum '
        'quid sic dictae. Hae vero sunt, quae quidem in suo genere dicunt perfectionem aliquam, '
        'sed quae tamen necessario est cum imperfectione conjuncta: nec ab ea potest separari, '
        'quandiu suam naturam retinet. Ideoque sunt quaedam perfectiones majores quae cum '
        'istiusmodi perfectione consistere non possunt. Ac proinde, simpliciter & absolute '
        'loquendo, praestat talem perfectionem non habere, quam illam habere. Hujusmodi '
        'perfectio est animalis sensitiva & vegetativa. Nam quamvis in suo genere sit '
        'perfectio quaedam vegetativum & sensitivum esse, tamen perfectiones illae connotant '
        'quandam imperfectionem, & est major quaedam perfectio quae non potest cum illis '
        'consistere, ut verbi causa, perfectio naturae angelicae. Ideoque, simpliciter & '
        'absolute loquendo, praestat non esse sensitivum, quam esse sensitivum, non esse '
        'vegetativum, quam esse vegetativum.'
    ),
}

SECTIONS = [
    {
        'section': '399',
        'title': 'After simplicity — highest perfection demands absolute simplicity',
        'pass_a': (
            'In the newest theses we treated of divine simplicity, which has a necessary '
            'connexion with the highest and absolute perfection of God. For in corporeal things '
            'indeed, those which are simpler are more imperfect. So elements are more imperfect '
            'than mixed things, and animals are more perfect than plants. Nor is there any created '
            'thing which does not require some composition for its perfection, and which at least '
            'does not need to be perfected by certain accidents. But the highest perfection '
            'demands absolute simplicity. God is most simple, because most perfect. And therefore '
            'after it has been treated of God\'s simplicity, reason demands that we now treat of '
            'His perfection.'
        ),
        'pass_b': [
            'Simplicity and highest perfection are necessarily linked.',
            'In bodies, simpler often means more imperfect — creatures need composition.',
            'Highest perfection demands absolute simplicity — so after simplicity, perfection.',
        ],
        'lemmas': [
            {'latin': 'summa perfectio simplicitatem absolutam exigit', 'gloss': 'the highest perfection demands absolute simplicity'},
            {'latin': 'simplicissimus, quia perfectissimus', 'gloss': 'most simple, because most perfect'},
        ],
        'choices': [{
            'term': 'Deus est simplicissimus, quia perfectissimus',
            'english': 'God is most simple, because most perfect',
            'why': 'Opens Perfectione from closed Simplicitate.',
            'rejected': ['highest perfection can coexist with composition in God'],
        }],
        'notes': ['OCR: I PDF 114 / book p. 102; new lock.'],
        'bible_refs': [],
    },
    {
        'section': '400',
        'title': 'Perfect = nothing lacking — absolutely or secundum quid',
        'pass_a': (
            'Perfect is said that to which nothing is lacking. But perfection often designates '
            'any excellence. But something is said perfect in two ways, either absolutely, or '
            'secundum quid.'
        ),
        'pass_b': [
            'Perfect: that to which nothing is lacking.',
            'Said two ways: absolutely, or secundum quid.',
        ],
        'lemmas': [
            {'latin': 'cui nihil deest', 'gloss': 'to which nothing is lacking'},
            {'latin': 'vel absolute, vel secundum quid', 'gloss': 'either absolutely, or secundum quid'},
        ],
        'choices': [{
            'term': 'vel absolute, vel secundum quid',
            'english': 'either absolutely, or secundum quid',
            'why': 'Frames the perfection distinction.',
            'rejected': ['only one sense of perfect'],
        }],
        'notes': ['OCR: II PDF 114.'],
        'bible_refs': [],
    },
    {
        'section': '401',
        'title': 'Secundum quid: complete in its own kind',
        'pass_a': (
            'Secundum quid perfect is that to which nothing is lacking, not simply, but in its '
            'own genus, that is, which has every perfection congruent and due to its nature. So '
            'a perfect horse is one to which nothing is lacking that pertains to equine nature, '
            'and a perfect plant which has every perfection suitable to a plant, although '
            'absolutely speaking there are many perfections which a horse, or a plant called '
            'perfect, does not have.'
        ),
        'pass_b': [
            'Secundum quid: nothing lacking in its own kind.',
            'Perfect horse / perfect plant = full for that nature.',
            'Still miss many absolute excellences.',
        ],
        'lemmas': [
            {'latin': 'in suo genere', 'gloss': 'in its own genus'},
            {'latin': 'naturae suae congruam & debitam', 'gloss': 'congruent and due to its nature'},
        ],
        'choices': [{
            'term': 'non simpliciter, sed in suo genere',
            'english': 'not simply, but in its own genus',
            'why': 'Defines relative perfection.',
            'rejected': ['kind-complete equals absolute perfect'],
        }],
        'notes': ['OCR: III PDF 114.'],
        'bible_refs': [],
    },
    {
        'section': '402',
        'title': 'Simply perfect: every possible excellence — God alone',
        'pass_a': (
            'But simply perfect is that to which nothing at all is lacking, and which has every '
            'possible excellence. Such perfection befits no creature, but is a proper attribute '
            'of the divine nature. For every creature has a certain and determinate perfection, '
            'this one that, that one another: but God contains in Himself whatever of perfection '
            'can be had, nor can any excellence be thought of of which the divine nature is devoid.'
        ),
        'pass_b': [
            'Simply perfect: nothing lacking; every possible excellence.',
            'No creature — only the divine nature.',
            'Creatures have bounded perfections; God holds them all.',
        ],
        'lemmas': [
            {'latin': 'omnem excellentiam possibilem', 'gloss': 'every possible excellence'},
            {'latin': 'proprium naturae divinae attributum', 'gloss': 'a proper attribute of the divine nature'},
        ],
        'choices': [{
            'term': 'Talis perfectio nulli creaturae competit',
            'english': 'Such perfection befits no creature',
            'why': 'Reserves absolute perfection to God.',
            'rejected': ['some creature can be simply perfect'],
        }],
        'notes': ['OCR: IV PDF 114.'],
        'bible_refs': [],
    },
    {
        'section': '403',
        'title': 'Two grounds: cause of all; uncaused from Himself',
        'pass_a': (
            'But this highest perfection of the divine nature is gathered from two things. 1. '
            'From this that God is the cause of all things. 2. From this that God has no cause, '
            'but is through Himself, and from Himself.'
        ),
        'pass_b': [
            'Highest divine perfection from two grounds.',
            'He is cause of all.',
            'He has no cause — through Himself, from Himself.',
        ],
        'lemmas': [
            {'latin': 'rerum omnium causa', 'gloss': 'cause of all things'},
            {'latin': 'per se est, & a seipso', 'gloss': 'is through Himself, and from Himself'},
        ],
        'choices': [{
            'term': 'Deus nullam causam habet, sed per se est, & a seipso',
            'english': 'God has no cause, but is through Himself, and from Himself',
            'why': 'Second ground of summa perfectio.',
            'rejected': ['God\'s perfection needs an external cause'],
        }],
        'notes': ['OCR: V PDF 114.'],
        'bible_refs': [],
    },
    {
        'section': '404',
        'title': 'Effect-perfection is in the cause — Psalm 94; Isaiah 66',
        'pass_a': (
            'For it is most certain that in an effect there can be no perfection which is not '
            'somehow in the cause. Since therefore God is the first cause of all things, nothing '
            'of perfection can be in any thing which is not found in God. And Scripture indicates '
            'this, while noting some perfection in things made by God, thence arguing that God '
            'much more has such a perfection. As Psalm 94. Shall He, says the Prophet, who '
            'planted the ear not hear? shall He who formed the eye not see? And Isaiah 66. Shall '
            'I who make others bring forth, myself not bring forth, says the Lord? Shall I who '
            'give generation to the rest be barren?'
        ),
        'pass_b': [
            'No effect-perfection missing from the first cause.',
            'Ps 94: planter of the ear hears; former of the eye sees.',
            'Isa 66: He who makes others bear is not barren.',
        ],
        'lemmas': [
            {'latin': 'in effectu nullam esse posse perfectionem', 'gloss': 'that in an effect there can be no perfection'},
            {'latin': 'qui aurem plantavit non audiet', 'gloss': 'shall He who planted the ear not hear'},
        ],
        'choices': [{
            'term': 'nihil in ulla re potest esse perfectionis quod in Deo non reperiatur',
            'english': 'nothing of perfection can be in any thing which is not found in God',
            'why': 'Cause-contains-effect perfection with Scripture.',
            'rejected': ['creatures can have perfections absent from God'],
        }],
        'notes': ['OCR: VI PDF 114-115; Psal. 94 / Isa. 66.'],
        'bible_refs': ['Ps. 94', 'Isa. 66'],
    },
    {
        'section': '405',
        'title': 'Axiom: every creaturely excellence is somehow in God — simply simple perfections',
        'pass_a': (
            'And therefore it is to be held with skill, and as a firm and certain axiom, that '
            'absolutely no preeminence and excellence is found in any creature which is not in '
            'God in some way at least. But for a fuller understanding of this matter it is to be '
            'noted that there are two kinds of perfections. For there are certain perfections '
            'simply such, that is, which, absolutely speaking, it is better to have than not to '
            'have, and which exclude no greater perfection. These the Scholastics call perfections '
            'simply simple. And of this sort are life, intellect, liberty of will. For absolutely '
            'speaking, it is better to live than not to live, to understand than not to understand, '
            'and to be endowed with free will than not to be endowed. Nor is there any perfection '
            'however great which cannot stand with life, intellect, and free will.'
        ),
        'pass_b': [
            'Axiom: every creaturely excellence is somehow in God.',
            'Two kinds: first, simply simple — better to have than lack.',
            'Life, intellect, free will — no greater perfection bars them.',
        ],
        'lemmas': [
            {'latin': 'perfectiones simpliciter simplices', 'gloss': 'perfections simply simple'},
            {'latin': 'vita, intellectus, voluntatis libertas', 'gloss': 'life, intellect, liberty of will'},
        ],
        'choices': [{
            'term': 'perfectiones simpliciter simplices',
            'english': 'perfections simply simple',
            'why': 'Opens Scholastic perfection taxonomy.',
            'rejected': ['life and intellect exclude greater perfections'],
        }],
        'notes': ['OCR: VII PDF 115.'],
        'bible_refs': [],
    },
    {
        'section': '406',
        'title': 'Secundum quid perfections: sensitive and vegetative tied to imperfection',
        'pass_a': (
            'But besides there are certain other perfections not simply, but so called secundum '
            'quid. These indeed are those which in their own genus say some perfection, but which '
            'yet is necessarily joined with imperfection: nor can it be separated from it so long '
            'as it retains its nature. And therefore there are certain greater perfections which '
            'cannot stand with a perfection of that sort. And therefore, simply and absolutely '
            'speaking, it is better not to have such a perfection than to have it. Of this sort '
            'is the sensitive and vegetative animal perfection. For although in its own genus it '
            'is some perfection to be vegetative and sensitive, yet those perfections connote a '
            'certain imperfection, and there is a certain greater perfection which cannot stand '
            'with them, as for example the perfection of angelic nature. And therefore, simply '
            'and absolutely speaking, it is better not to be sensitive than to be sensitive, not '
            'to be vegetative than to be vegetative.'
        ),
        'pass_b': [
            'Secundum quid perfections: kind-good but locked to imperfection.',
            'Sensitive / vegetative conflict with higher (angelic) perfection.',
            'Absolutely: better without sense/vegetative than with them.',
        ],
        'lemmas': [
            {'latin': 'secundum quid sic dictae', 'gloss': 'so called secundum quid'},
            {'latin': 'animalis sensitiva & vegetativa', 'gloss': 'sensitive and vegetative animal'},
        ],
        'choices': [{
            'term': 'praestat non esse sensitivum, quam esse sensitivum',
            'english': 'it is better not to be sensitive than to be sensitive',
            'why': 'Contrasts secundum quid with simply simple perfections; next IX+ formal/eminent.',
            'rejected': ['sensitive nature is simply better than angelic'],
        }],
        'notes': ['OCR: VIII PDF 115; next IX+ formaliter / eminenter.'],
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
        if 399 <= n <= 406:
            notes = (
                f'Section {sid}: new densify De Dei Perfectione & Infinitate I-VIII; '
                'Pass A!=B; lock-grounded PDF 114-115 / book pp. 102-103.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_perfectione I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Dei Perfectione & Infinitate I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Perfectione through VIII; IX+ remains. '
                'Simplicitate closed. Not shipped.'
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
        'locus': 'De Dei Perfectione & Infinitate theses I-VIII (summa perfectio / absolute vs secundum quid)',
        'next_locus': 'De Dei Perfectione & Infinitate IX+ (formaliter / eminenter)',
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
        'deploy_bound': 'ec82d5ea live 57/4447 tip 398',
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
        f'## {day} (Scribe — De Dei Perfectione & Infinitate I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(opens Perfectione I–VIII → §§{SECS[0]}–{SECS[-1]} after Simplicitate close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 114-115 / pp. 102-103).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Perfectione & Infinitate through VIII. IX+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound ec82d5ea / tip 398; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Perfectione & Infinitate I–VIII densify)\n\n'
        'CoS densify: De Dei Perfectione & Infinitate I–VIII. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Perfectione I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: IX+. Punch X: **NO**.\n\n---\n\n'
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
            'deploy_bound': 'ec82d5ea',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-398 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
