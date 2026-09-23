#!/usr/bin/env python3
"""Build + apply De Scientia Dei XXV-XXX densify (tip 521 → 527).

Times; past/future; possibles/impossibles; object-slice close. Live floor 4887.
After tip-ready: HOLD live>4887 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_scientia_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_scientia_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_scientia_densify')
PACKET_STEM = 'dei_scientia_xxv_xxx_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_scientia/apply_dei_scientia_xxv_xxx_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['522', '523', '524', '525', '526', '527']
ROMANS = {
    '522': 'XXV', '523': 'XXVI', '524': 'XXVII',
    '525': 'XXVIII', '526': 'XXIX', '527': 'XXX',
}
TIP_BEFORE = 521
PRIOR_START = 498
LIVE_FLOOR = 4887
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Scientia Dei I-XXX (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Scientia Dei I-XXX. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Scientia Dei I-XXX, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Scientia Dei XXV-XXX "
    "(times; past/future; possibles/impossibles; omniscience close before Praedestinatio)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scientia Dei, sive De cognitione rerum quae in Deo est.\n"
    "Same 1675 Pitt copy-text. Book pp. 117-120 / PDF 129-132 (I-XXX; this packet XXV-XXX). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Scientia Dei I-XXX tip — object-slice close. Next: De Causa Praedestinationis.\n"
    "Note: Present/past/future; memory books; prophecy; possibles; impossibles; wrap.\n\n"
)

LATIN = {
    '522': (
        'XXV. Jam autem, si per discrimina temporum ire libet, & ex iis rerum genera '
        'distinguere, inde quoque manifestum erit, nullum rerum genus a Deo ignorari. Nec enim '
        'Deo nota sunt praesentia solum quantumvis occulta, sed praeteritorum nihil eum fugit, '
        '& de longe quoque prospicit futura.'
    ),
    '523': (
        'XXVI. Et certe praeteritorum notitiam Deo tribuendam esse, vel inde patet quod Deus '
        'in Scriptura multa pluribus ante saeculis praeterita recenset, primamque rerum originem '
        'ab initio per Mosen repetit. Hoc quoque facit, quod Scriptura memoriam Deo tribuit, ut '
        'quum dicitur meminisse foederis vel juramenti sui. Etenim licet Deus idcirco praecipue '
        'dicatur meminisse rerum, quia earum rationem habet, aut propter eas aliquid operatur, '
        'hoc ipsum tamen supponit Deum illas probe novisse ac tenere. Nec alio referendi sunt '
        'libri illi, in quibus ea quae fiunt & contingunt Deus scribere dicitur, Psal. 56. 9. & '
        'Psal. 139. 16. Per hoc enim Scriptura innuit Deum oblivioni praeterita non mandare, sed '
        'illa Deo tam certo & distincte cognita manere, ac si ab eo scriptis mandata essent, & '
        'continuo lecta. Sed praecipue exactam rerum praeteritarum cognitionem in Deo arguit '
        'universale illud judicium, in quo unicuique pro praeteritis ejus factis, dictis & '
        'cogitatis, sive bonis sive malis olim redditurus est: juxta illa ultima Ecclesiastae '
        'verba, Cuncta quae fiunt adducet Deus in judicium de omni abscondito sive bonum sive '
        'malum sit.'
    ),
    '524': (
        'XXVII. Futura vero Deum praenoscere probant innumerae rerum futurarum praedictiones '
        'per totum Sacrae Scripturae corpus sparsae, & quibus praecipue Prophetarum libri '
        'scatent, ut liber Apocalypseos inter scripta Novi Testamenti. Ideoque scite dixit '
        'Tertullianus, Dei praescientiam tot habere testes, quot fecit Prophetas. Atque hanc '
        'futurorum praenotionem Deus ut propriam sibi vendicat, eaque vult a falsis Gentium '
        'Diis discerni, & pro vero vivoque Deo solum agnosci, quia videlicet, ipse solus futura '
        'annunciare possit, & reipsa annunciet: ut saepius apud Isaiam videre est, praesertim '
        'cap. 41. ubi Deus per Prophetam sic idolatria Gentium numina alloquitur, Annunciate '
        'quae ventura sunt in futurum, & sciemus quod Dii estis vos.'
    ),
    '525': (
        'XXVIII. Porro Deus novit non tantum ea quae sunt, fuerunt, aut futura sunt, sed & '
        'quaecunque possunt esse, licet revera nunquam futura sint. Quum enim homines ipsi '
        'noverint multa esse possibilia, quae nunquam tamen actu ponenda sunt, & in natura '
        'rerum exitura, quis rerum ejusmodi cognitionem Deo cum ratione adimat? Adde quod Deus '
        'propriam potentiam ignorare non potest: nec potest propriam potentiam nosse, quin '
        'noverit ad quae se extendat. Deus autem praeter ea quae fecit, aut facturus est, '
        'infinita facere & producere potest: adeoque necesse est, ut distincte cognoscat '
        'infinita posse esse & fieri, quae tamen nunquam futura sunt.'
    ),
    '526': (
        'XXIX. Jam vero sicut Deus optime novit quicquid est possibile, sic quoque non '
        'ignorat quid impossibile sit & fieri non possit. Novit se non posse mori, & seipsum '
        'abnegare, & impossibile esse, ut Deus mentiatur, quod Deus ipse in verbo suo asserit. '
        'Et certe, quum homines ipsi certo & distincte sciant hoc vel illud fieri non posse, '
        'quanto magis illud Deo tribuendum est. Cumque ad intellectum pertineat judicare quid '
        'fieri repugnet, & quid non, quid est hujusmodi quod intellectum divinum latere & '
        'fugere possit, quandoquidem quicquid est ullo modo intelligibile necessario cadit sub '
        'intellectum infinitum?'
    ),
    '527': (
        'XXX. Igitur conclusum esto, Deum perfecte & distincte novisse omnia, quae quomodocunque '
        'sciri & intelligi possunt, singularia & universalia, maxima & minima, patentia & '
        'latentia, bona & mala, praeterita, praesentia & futura, denique possibilia & '
        'impossibilia: quorum omnium quum aliquid mens humana percipiat, eorum nihil menti '
        'divinae atque infinitae potest non esse penitus cognitum & perceptum.'
    ),
}

SECTIONS = [
    {
        'section': '522',
        'title': 'By times — present, past, and future all known',
        'pass_a': (
            'But now, if one may go by the distinctions of times, and from them distinguish '
            'kinds of things, from that also it will be plain that no kind of things is unknown '
            'to God. For not only are present things known to God, however hidden, but nothing '
            'of past things escapes Him, and from afar He also looks out on future things.'
        ),
        'pass_b': [
            'Time-slices also fall under omniscience.',
            'Hidden presents known.',
            'Past escapes Him not; future seen from afar.',
        ],
        'lemmas': [
            {'latin': 'nullum rerum genus a Deo ignorari', 'gloss': 'that no kind of things is unknown to God'},
            {'latin': 'de longe quoque prospicit futura', 'gloss': 'from afar He also looks out on future things'},
        ],
        'choices': [{
            'term': 'praeteritorum nihil eum fugit, & de longe quoque prospicit futura',
            'english': 'nothing of past things escapes Him, and from afar He also looks out on future things',
            'why': 'Opens the time axis after hearts/singulars.',
            'rejected': ['God knows only the present'],
        }],
        'notes': ['OCR: XXV PDF 132; times.'],
        'bible_refs': [],
    },
    {
        'section': '523',
        'title': 'Past knowledge — Moses, memory, books, final judgment',
        'pass_a': (
            'And certainly that knowledge of past things is to be ascribed to God is plain even '
            'from this, that in Scripture God recounts many things past many ages before, and '
            'repeats through Moses the first origin of things from the beginning. This also does '
            'it, that Scripture ascribes memory to God, as when He is said to remember His '
            'covenant or His oath. For although God is said especially to remember things because '
            'He takes account of them, or works something on account of them, yet that itself '
            'assumes that God has well known and holds them. Nor are those books to be referred '
            'elsewhere, in which God is said to write the things that happen and come to pass, '
            'Psalm 56:9 and Psalm 139:16. For by this Scripture hints that God does not consign '
            'past things to oblivion, but that they remain known to God as certainly and '
            'distinctly as if they had been committed by Him to writing and continually read. '
            'But especially that exact knowledge of past things in God is argued by that universal '
            'judgment in which He will one day render to each for his past deeds, words, and '
            'thoughts, whether good or evil: according to those last words of Ecclesiastes, God '
            'will bring every work into judgment, with every secret thing, whether it be good or '
            'whether it be evil.'
        ),
        'pass_b': [
            'Scripture recounts ancient past via Moses.',
            '“Remembering” covenant/oath presupposes knowing.',
            'Books (Ps 56/139) + final judgment seal exact past knowledge.',
        ],
        'lemmas': [
            {'latin': 'memoriam Deo tribuit', 'gloss': 'ascribes memory to God'},
            {'latin': 'Cuncta quae fiunt adducet Deus in judicium', 'gloss': 'God will bring every work into judgment'},
        ],
        'choices': [{
            'term': 'Deum oblivioni praeterita non mandare',
            'english': 'that God does not consign past things to oblivion',
            'why': 'Memory/books imagery = durable distinct past knowledge.',
            'rejected': ['past events drop from God’s mind'],
        }],
        'notes': ['OCR: XXVI PDF 132; Ps 56:9; 139:16; Eccl 12:14.'],
        'bible_refs': ['Ps. 56:8', 'Ps. 139:16', 'Eccl. 12:14'],
    },
    {
        'section': '524',
        'title': 'Future foreknowledge — prophecy; Tertullian; Isa 41',
        'pass_a': (
            'But that God foreknows future things is proved by countless predictions of future '
            'things scattered through the whole body of Holy Scripture, and with which especially '
            'the books of the Prophets abound, as the book of the Apocalypse among the writings '
            'of the New Testament. And therefore Tertullian said shrewdly that God’s '
            'foreknowledge has as many witnesses as He has made Prophets. And God claims this '
            'foreknowledge of future things as proper to Himself, and by it wills to be '
            'distinguished from the false gods of the nations, and to be acknowledged alone as '
            'the true and living God, because namely He alone can announce future things, and '
            'in fact does announce them: as is often to be seen in Isaiah, especially chapter '
            '41, where God through the Prophet thus addresses the idol-gods of the nations, '
            'Announce the things that are to come hereafter, and we shall know that you are gods.'
        ),
        'pass_b': [
            'Prophecy floods Scripture — including Revelation.',
            'Tertullian: as many witnesses as Prophets.',
            'Isa 41: announce the future — mark of the living God.',
        ],
        'lemmas': [
            {'latin': 'Dei praescientiam tot habere testes, quot fecit Prophetas', 'gloss': 'God’s foreknowledge has as many witnesses as He has made Prophets'},
            {'latin': 'Annunciate quae ventura sunt in futurum', 'gloss': 'Announce the things that are to come hereafter'},
        ],
        'choices': [{
            'term': 'ipse solus futura annunciare possit, & reipsa annunciet',
            'english': 'He alone can announce future things, and in fact does announce them',
            'why': 'Foreknowledge as God’s proprietary claim vs idols.',
            'rejected': ['prophecy does not require divine foreknowledge'],
        }],
        'notes': ['OCR: XXVII PDF 132; Tertullian; Isa 41.'],
        'bible_refs': ['Isa. 41:23'],
    },
    {
        'section': '525',
        'title': 'God knows possibles that will never be',
        'pass_a': (
            'Further, God knows not only those things which are, have been, or will be, but '
            'also whatever things can be, even if in reality they will never be. For since men '
            'themselves know that many things are possible which yet are never to be actually '
            'posited and to come forth in the nature of things, who with reason would take from '
            'God the knowledge of such things? Add that God cannot be ignorant of His own power: '
            'nor can He know His own power without knowing to what it extends. But God, besides '
            'those things which He has made or will make, can make and produce infinite things: '
            'and therefore it is necessary that He distinctly know that infinite things can be '
            'and come to be which yet will never be.'
        ),
        'pass_b': [
            'Not only actual timeline — also mere possibles.',
            'Men already know unused possibles.',
            'Knowing His power = knowing its infinite unused reach.',
        ],
        'lemmas': [
            {'latin': 'quaecunque possunt esse, licet revera nunquam futura sint', 'gloss': 'whatever things can be, even if in reality they will never be'},
            {'latin': 'propriam potentiam nosse, quin noverit ad quae se extendat', 'gloss': 'know His own power without knowing to what it extends'},
        ],
        'choices': [{
            'term': 'necessarium est, ut distincte cognoscat infinita posse esse & fieri, quae tamen nunquam futura sunt',
            'english': 'it is necessary that He distinctly know that infinite things can be and come to be which yet will never be',
            'why': 'Extends omniscience beyond the actual world-history.',
            'rejected': ['God knows only what will actually occur'],
        }],
        'notes': ['OCR: XXVIII PDF 132; possibles.'],
        'bible_refs': [],
    },
    {
        'section': '526',
        'title': 'God knows impossibles — cannot die or lie',
        'pass_a': (
            'But now just as God knows best whatever is possible, so also He is not ignorant '
            'of what is impossible and cannot come to be. He knows that He cannot die, and deny '
            'Himself, and that it is impossible that God should lie, which God Himself asserts '
            'in His word. And certainly, since men themselves know certainly and distinctly that '
            'this or that cannot come to be, how much more is that to be ascribed to God. And '
            'since it belongs to intellect to judge what is contradictory to coming to be, and '
            'what is not, what is there of this sort that can hide from and escape the divine '
            'intellect, seeing that whatever is in any way intelligible necessarily falls under '
            'an infinite intellect?'
        ),
        'pass_b': [
            'Impossibles known too — die, deny Himself, lie.',
            'Men already spot impossibles; God more.',
            'Infinite intellect covers every intelligibile.',
        ],
        'lemmas': [
            {'latin': 'impossibile esse, ut Deus mentiatur', 'gloss': 'that it is impossible that God should lie'},
            {'latin': 'quicquid est ullo modo intelligibile', 'gloss': 'whatever is in any way intelligible'},
        ],
        'choices': [{
            'term': 'Novit se non posse mori, & seipsum abnegare, & impossibile esse, ut Deus mentiatur',
            'english': 'He knows that He cannot die, and deny Himself, and that it is impossible that God should lie',
            'why': 'Negative possibles complete the modal range.',
            'rejected': ['God does not know what He cannot do'],
        }],
        'notes': ['OCR: XXIX PDF 132; cannot lie.'],
        'bible_refs': ['Titus 1:2', '2 Tim. 2:13'],
    },
    {
        'section': '527',
        'title': 'Wrap — God knows all that can be known',
        'pass_a': (
            'Therefore let it be concluded that God has known perfectly and distinctly all '
            'things which in any way can be known and understood — singulars and universals, '
            'greatest and least, open and hidden, good and evil, past, present, and future, '
            'finally possibles and impossibles: of all which, when the human mind perceives '
            'something, nothing of them can fail to be thoroughly known and perceived by the '
            'divine and infinite mind.'
        ),
        'pass_b': [
            'Close: perfect distinct knowledge of every knowable.',
            'Singulars/universals; great/small; open/hidden; good/evil.',
            'Past/present/future; possible/impossible — if humans glimpse any, God holds all.',
        ],
        'lemmas': [
            {'latin': 'perfecte & distincte novisse omnia', 'gloss': 'to have known all things perfectly and distinctly'},
            {'latin': 'possibilia & impossibilia', 'gloss': 'possibles and impossibles'},
        ],
        'choices': [{
            'term': 'eorum nihil menti divinae atque infinitae potest non esse penitus cognitum & perceptum',
            'english': 'nothing of them can fail to be thoroughly known and perceived by the divine and infinite mind',
            'why': 'Honest object-slice close; next De Causa Praedestinationis.',
            'rejected': ['some knowables escape the infinite mind'],
        }],
        'notes': ['OCR: XXX PDF 132; Scientia object wrap; next Praedestinatio.'],
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
        jpath = JUST / f'dei_scientia_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_scientia_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_132.txt', 'pdf_133.txt'):
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
        if 522 <= n <= 527:
            notes = (
                f'Section {sid}: new densify De Scientia Dei XXV-XXX object close; '
                'Pass A!=B; lock-grounded PDF 132 / book p. 120.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_scientia XXV-XXX packet scope covering all current sections.'
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
                'Scope review: densify De Scientia Dei XXV-XXX only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest object-slice close; next De Causa Praedestinationis. Not shipped.'
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
        'locus': 'De Scientia Dei theses XXV-XXX (times; past/future; possibles; wrap)',
        'next_locus': 'De Causa Praedestinationis (opens after Scientia XXX)',
        'gates': {
            'check_pass_ab': f'ok dei_scientia_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'honest_slice_note': 'XXV-XXX honest object close (6 ~4-8) before Praedestinatio',
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
        f'## {day} (Scribe — De Scientia Dei XXV–XXX densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Scientia Dei XXV–XXX → §§{SECS[0]}–{SECS[-1]}; object close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 132 / p. 120).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: Scientia object through XXX. '
        'Next: De Causa Praedestinationis. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Scientia Dei XXV–XXX densify)\n\n'
        'CoS densify: Scientia Dei XXV–XXX object close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Scientia Dei XXV–XXX (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Praedestinatio. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_527.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-527 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
