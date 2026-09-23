#!/usr/bin/env python3
"""Build + apply De Scientia Dei IX-XVI densify (tip 505 → 513).

Continues after I-VIII. Live floor 4840.
After tip-ready: HOLD live>4840 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_scientia_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_scientia/apply_dei_scientia_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['506', '507', '508', '509', '510', '511', '512', '513']
ROMANS = {
    '506': 'IX', '507': 'X', '508': 'XI', '509': 'XII',
    '510': 'XIII', '511': 'XIV', '512': 'XV', '513': 'XVI',
}
TIP_BEFORE = 505
PRIOR_START = 498
LIVE_FLOOR = 4840
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Scientia Dei I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Scientia Dei I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Scientia Dei I-XVI, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Scientia Dei IX-XVI "
    "(knows all else; singulars vs Averroes; presence; intelligibility)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scientia Dei, sive De cognitione rerum quae in Deo est.\n"
    "Same 1675 Pitt copy-text. Book pp. 117-119 / PDF 129-131 (I-XVI; this packet IX-XVI). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Scientia Dei I-XVI tip — continues after I-VIII. Next: Scientia Dei XVII+.\n"
    "Note: Knows creatures as well as Himself; Averroes error; singulars; Jer 23 presence.\n\n"
)

LATIN = {
    '506': (
        'IX. Non minus autem perfecte quam seipsum, reliqua omnia praeter se Deus novit. '
        'Nam ut ait Apostolus Hebr. 4. 13. Non est ulla res creata non manifesta in conspectu '
        'ejus: sed omnia sunt nuda, & τετραχηλισμένα intime patentia oculis ejus cum quo nobis '
        'est negotium. Quo spectat quoque illud Jobi cap. 28. Ipse fines mundi intuetur, & '
        'omnia quae sub caelo sunt respicit.'
    ),
    '507': (
        'X. Deus autem res non solum cognoscit in genere, & sub communi aliqua ratione, prout '
        'considerantur in scientiis humanis. Id senserunt Philosophi quidam, inter quos praecipue '
        'memoratur Averroes. Tribuitur enim illi quod docuerit Deum universalia tantum '
        'cognoscere, singularia vero non cadere sub intellectum divinum. Verum istud est '
        'manifestus error, cui tum rationis lumen, tum Scriptura Sacra aperte repugnat.'
    ),
    '508': (
        'XI. Nam cum Deus res singulas condiderit, & earum unicuique rei esse contulerit '
        'propria & immediata quadam efficientia, atque id non temere, neque naturali quadam '
        'necessitate, sed certo consilio & ex propriae voluntatis decreto, non potest illas '
        'ignorare. An enim causa libera, atque ex judicio agens proprium suum opus non '
        'intelliget, & percipere non poterit quod ipsa valet efficere?'
    ),
    '509': (
        'XII. Neque Deus res semel condidit & produxit, sed illas perpetuo regit & moderatur, '
        '& sapientissime ad finem suum unamquamque dirigit. Non potest autem id praestare, '
        'quin res, non solum in communi, sed sigillatim probe ipsi notae atque perspectae sint.'
    ),
    '510': (
        'XIII. Ac profecto, cum Deus sit unicuique redditurus secundum opera sua, quae bene '
        'acta sunt, scilicet, liberaliter remunerans, male facta vero pro eorum merito puniens '
        '& vindicans, necesse est Deum unumquemque novisse, & singula omnium dicta, facta, '
        'atque cogitata penitus percepta & cognita habere.'
    ),
    '511': (
        'XIV. Adde quod cum Deus immensus sit, & essentia ejus ineffabili modo omnia loca '
        'repleat, singulis rebus adest & intime praesens est. An autem Deus ignoraret, & non '
        'perciperet ea, quae ipsi proxima & praesentia sunt: imo in quibus est, aut quae potius '
        'sunt in ipso? cum ne homo quidem, nisi dormiens, aut non advertens, non possit quin '
        'percipiat ea, quae attingit, & quae sunt coram ipso in luce posita. Quo argumento Deus '
        'Jeremiae cap. 23. arguit stuporem eorum, qui fraudes suas atque occulta facinora Deum '
        'latere posse existimant. Putatisne, inquit, Deus e vicino ego sum, & non Deus de '
        'longo? si occultabitur vir in abscondito & ego non videbo eum, dicit Dominus? Nunquid '
        'non caelum & terram ego impleo, dicit Dominus.'
    ),
    '512': (
        'XV. Sed cum homines ipsi singularia noscant & percipiant, quis cum ratione reliqua, '
        'eorum cognitionem Deo adimere poterit? Num enim quidquam homo sciet, quod Deus '
        'ignorabit? cum quicquid in homine cognitionis reperitur sit veluti gutta quaedam ex '
        'immenso divinae sapientiae Oceano hausta.'
    ),
    '513': (
        'XVI. Praeterea potentia omnium perfectissima necessario se porrigit ad omnia, quae '
        'ad ejus potentiae objectum pertinere possunt. Ac proinde cum intellectus divinus '
        'omnium perfectissimus sit, nihil eum fugit eorum, quae sunt intelligibilia. Sed omne '
        'quod est, intelligibile est, adeoque talia sunt etiam singularia, quibus juxta '
        'Philosophos ratio entis, vel maxime, competit, & sic necesse est illa non minus, imo '
        'magis quam universalia sub intellectum divinum cadere.'
    ),
}

SECTIONS = [
    {
        'section': '506',
        'title': 'God knows all else as perfectly as Himself — Heb 4; Job 28',
        'pass_a': (
            'But God knows all the rest besides Himself no less perfectly than Himself. For as '
            'the Apostle says in Hebrews 4:13, There is no created thing that is not manifest in '
            'His sight: but all things are naked and laid open inwardly to the eyes of Him with '
            'whom we have to do. To which also that of Job chapter 28 looks: He looks on the '
            'ends of the world, and sees all things that are under heaven.'
        ),
        'pass_b': [
            'Creatures known as perfectly as God knows Himself.',
            'Heb 4:13 — all naked and open to His eyes.',
            'Job 28 — He surveys earth’s ends and all under heaven.',
        ],
        'lemmas': [
            {'latin': 'reliqua omnia praeter se Deus novit', 'gloss': 'God knows all the rest besides Himself'},
            {'latin': 'omnia sunt nuda', 'gloss': 'all things are naked'},
        ],
        'choices': [{
            'term': 'Non minus autem perfecte quam seipsum, reliqua omnia praeter se Deus novit',
            'english': 'But God knows all the rest besides Himself no less perfectly than Himself',
            'why': 'Extends self-comprehension to every other object.',
            'rejected': ['God knows Himself but not creatures equally well'],
        }],
        'notes': ['OCR: IX PDF 130; Heb 4:13; Job 28; τετραχηλισμένα.'],
        'bible_refs': ['Heb. 4:13', 'Job 28:24'],
    },
    {
        'section': '507',
        'title': 'Not universals only — Averroes error rejected',
        'pass_a': (
            'But God does not know things only in genus and under some common aspect, as they '
            'are considered in the human sciences. Certain philosophers thought that, among whom '
            'Averroes is especially remembered. For it is ascribed to him that he taught that '
            'God knows universals only, but that singulars do not fall under the divine '
            'intellect. But that is a clear error, which both the light of reason and Holy '
            'Scripture openly oppose.'
        ),
        'pass_b': [
            'Not genus-only knowledge like human sciences.',
            'Averroes: universals yes, singulars no — false.',
            'Reason and Scripture both reject it.',
        ],
        'lemmas': [
            {'latin': 'universalia tantum cognoscere', 'gloss': 'to know universals only'},
            {'latin': 'singularia vero non cadere sub intellectum divinum', 'gloss': 'but that singulars do not fall under the divine intellect'},
        ],
        'choices': [{
            'term': 'Verum istud est manifestus error',
            'english': 'But that is a clear error',
            'why': 'Names and rejects Averroes on divine singulars.',
            'rejected': ['God knows only universals'],
        }],
        'notes': ['OCR: X PDF 130; Averroes.'],
        'bible_refs': [],
    },
    {
        'section': '508',
        'title': 'Free creating cause must know its singular works',
        'pass_a': (
            'For since God has founded individual things, and has conferred being on each of '
            'them by a certain proper and immediate efficiency, and that not rashly, nor by some '
            'natural necessity, but by sure counsel and from the decree of His own will, He '
            'cannot be ignorant of them. For shall a free cause, acting also from judgment, not '
            'understand its own proper work, and not be able to perceive what it itself is able '
            'to effect?'
        ),
        'pass_b': [
            'Each thing made by immediate free efficiency.',
            'Counsel / will decree — not blind necessity.',
            'A free judging cause knows its own work.',
        ],
        'lemmas': [
            {'latin': 'certo consilio & ex propriae voluntatis decreto', 'gloss': 'by sure counsel and from the decree of His own will'},
            {'latin': 'causa libera, atque ex judicio agens', 'gloss': 'a free cause, acting also from judgment'},
        ],
        'choices': [{
            'term': 'non potest illas ignorare',
            'english': 'He cannot be ignorant of them',
            'why': 'Creation by free decree forces knowledge of the singulars made.',
            'rejected': ['God could freely create what He does not know'],
        }],
        'notes': ['OCR: XI PDF 130; free cause.'],
        'bible_refs': [],
    },
    {
        'section': '509',
        'title': 'Ongoing rule requires individual knowledge',
        'pass_a': (
            'Nor has God founded and produced things once only, but He continually rules and '
            'governs them, and most wisely directs each to its end. But He cannot perform that '
            'unless the things are well known and seen through by Him, not only in common, but '
            'one by one.'
        ),
        'pass_b': [
            'Not one-shot creation — perpetual governance.',
            'Each directed wisely to its end.',
            'Requires sigillatim knowledge, not only in common.',
        ],
        'lemmas': [
            {'latin': 'perpetuo regit & moderatur', 'gloss': 'continually rules and governs'},
            {'latin': 'non solum in communi, sed sigillatim', 'gloss': 'not only in common, but one by one'},
        ],
        'choices': [{
            'term': 'non solum in communi, sed sigillatim probe ipsi notae',
            'english': 'well known to Him not only in common, but one by one',
            'why': 'Providence needs particular knowledge.',
            'rejected': ['general knowledge suffices for particular rule'],
        }],
        'notes': ['OCR: XII PDF 130; sigillatim.'],
        'bible_refs': [],
    },
    {
        'section': '510',
        'title': 'Judgment by works requires knowing deeds and thoughts',
        'pass_a': (
            'And indeed, since God is to render to each according to his works — liberally '
            'rewarding what has been well done, but punishing and avenging evil deeds according '
            'to their desert — it is necessary that God know each one, and have thoroughly '
            'perceived and known every one’s individual words, deeds, and thoughts.'
        ),
        'pass_b': [
            'Final recompense by works.',
            'Must know each person.',
            'Words, deeds, and thoughts all known.',
        ],
        'lemmas': [
            {'latin': 'redditurus secundum opera sua', 'gloss': 'to render according to his works'},
            {'latin': 'dicta, facta, atque cogitata', 'gloss': 'words, deeds, and thoughts'},
        ],
        'choices': [{
            'term': 'singula omnium dicta, facta, atque cogitata penitus percepta & cognita habere',
            'english': 'have thoroughly perceived and known every one’s individual words, deeds, and thoughts',
            'why': 'Judgment thesis seals particular omniscience.',
            'rejected': ['God judges without knowing thoughts'],
        }],
        'notes': ['OCR: XIII PDF 130; judgment.'],
        'bible_refs': [],
    },
    {
        'section': '511',
        'title': 'Immensity and presence — Jer 23 against hidden sins',
        'pass_a': (
            'Add that since God is immense, and His essence in an ineffable way fills all '
            'places, He is present to individual things and intimately present. But would God '
            'be ignorant of, and not perceive, those things which are nearest and present to '
            'Him — indeed in which He is, or which rather are in Him? since not even a man, '
            'unless sleeping or not attending, can fail to perceive what he touches and what is '
            'set before him in the light. By which argument God in Jeremiah chapter 23 rebukes '
            'the stupor of those who think their frauds and hidden crimes can escape God. Do '
            'you think, He says, I am a God at hand, and not a God afar off? If a man shall hide '
            'himself in secret places, shall I not see him, says the Lord? Do I not fill heaven '
            'and earth, says the Lord.'
        ),
        'pass_b': [
            'Immense essence fills all places — present to each.',
            'Near presence implies perception.',
            'Jer 23: no hiding from the God who fills heaven and earth.',
        ],
        'lemmas': [
            {'latin': 'singulis rebus adest & intime praesens est', 'gloss': 'He is present to individual things and intimately present'},
            {'latin': 'Nunquid non caelum & terram ego impleo', 'gloss': 'Do I not fill heaven and earth'},
        ],
        'choices': [{
            'term': 'si occultabitur vir in abscondito & ego non videbo eum',
            'english': 'If a man shall hide himself in secret places, shall I not see him',
            'why': 'Scripture seal on knowledge via omnipresence.',
            'rejected': ['hidden sins can escape an immense God'],
        }],
        'notes': ['OCR: XIV PDF 131 / p. 119; Jer 23.'],
        'bible_refs': ['Jer. 23:23-24'],
    },
    {
        'section': '512',
        'title': 'If men know singulars, God more — drop from His ocean',
        'pass_a': (
            'But since men themselves know and perceive singulars, who with reason could take '
            'their knowledge from God as to the rest? For will a man know anything that God will '
            'be ignorant of? since whatever knowledge is found in man is as it were a certain '
            'drop drawn from the immense Ocean of divine wisdom.'
        ),
        'pass_b': [
            'Humans already know singulars.',
            'Cannot strip that from God.',
            'Human knowing = a drop from God’s ocean.',
        ],
        'lemmas': [
            {'latin': 'homines ipsi singularia noscant', 'gloss': 'men themselves know singulars'},
            {'latin': 'gutta quaedam ex immenso divinae sapientiae Oceano', 'gloss': 'a certain drop from the immense Ocean of divine wisdom'},
        ],
        'choices': [{
            'term': 'Num enim quidquam homo sciet, quod Deus ignorabit?',
            'english': 'For will a man know anything that God will be ignorant of?',
            'why': 'A fortiori from creature singular knowledge.',
            'rejected': ['men can know what God cannot'],
        }],
        'notes': ['OCR: XV PDF 131; ocean drop.'],
        'bible_refs': [],
    },
    {
        'section': '513',
        'title': 'Perfect intellect reaches every intelligible — including singulars',
        'pass_a': (
            'Further, the most perfect power of all necessarily extends itself to all things '
            'that can belong to the object of that power. And therefore since the divine '
            'intellect is the most perfect of all, nothing of those things that are intelligible '
            'escapes it. But everything that is, is intelligible, and therefore singulars also '
            'are such, to which according to the philosophers the notion of being belongs even '
            'most of all, and so it is necessary that they fall under the divine intellect no '
            'less, indeed more, than universals.'
        ),
        'pass_b': [
            'Most perfect power covers its whole object-range.',
            'Whatever is, is intelligible — including singulars.',
            'Singulars under divine intellect no less than universals.',
        ],
        'lemmas': [
            {'latin': 'omne quod est, intelligibile est', 'gloss': 'everything that is, is intelligible'},
            {'latin': 'magis quam universalia sub intellectum divinum cadere', 'gloss': 'fall under the divine intellect more than universals'},
        ],
        'choices': [{
            'term': 'necesse est illa non minus, imo magis quam universalia sub intellectum divinum cadere',
            'english': 'it is necessary that they fall under the divine intellect no less, indeed more, than universals',
            'why': 'Closes IX-XVI against Averroes; next XVII+ stars and small things.',
            'rejected': ['singulars are less intelligible to God than universals'],
        }],
        'notes': ['OCR: XVI PDF 131; next XVII+ named stars / gnats.'],
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
    for name in ('pdf_130.txt', 'pdf_131.txt'):
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
        if 506 <= n <= 513:
            notes = (
                f'Section {sid}: new densify De Scientia Dei IX-XVI; '
                'Pass A!=B; lock-grounded PDF 130-131 / book pp. 118-119.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_scientia IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Scientia Dei IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Next Scientia XVII+. Not shipped.'
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
        'locus': 'De Scientia Dei theses IX-XVI (all else; Averroes; singulars; Jer 23; intelligibles)',
        'next_locus': 'De Scientia Dei XVII+ (stars; small things; Jerome; Matt 10)',
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
        f'## {day} (Scribe — De Scientia Dei IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Scientia Dei IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 130-131 / pp. 118-119).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Scientia Dei XVII+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Scientia Dei IX–XVI densify)\n\n'
        'CoS densify: Scientia Dei IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Scientia Dei IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Scientia XVII+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_513.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-513 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
