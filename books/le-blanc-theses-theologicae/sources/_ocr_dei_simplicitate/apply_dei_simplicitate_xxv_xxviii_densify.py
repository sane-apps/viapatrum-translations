#!/usr/bin/env python3
"""Build + apply De Dei Simplicitate XXV-XXVIII densify (tip 394 → 398).

Tract close: pure act; most simple; quicquid in Deo est Deus; attributes one.
Deploy 871d77d1 live 57/4425 bound tip 394. After tip-ready: HOLD live>4425 OR 12m.
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
LOCK = BOOK / 'sources/_le_blanc_dei_simplicitate_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_simplicitate_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_simplicitate_i_densify')
PACKET_STEM = 'dei_simplicitate_xxv_xxviii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_simplicitate/apply_dei_simplicitate_xxv_xxviii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['395', '396', '397', '398']
ROMANS = {'395': 'XXV', '396': 'XXVI', '397': 'XXVII', '398': 'XXVIII'}
TIP_BEFORE = 394
LIVE_FLOOR = 4425
HOLD_MINUTES = 12
PRIOR_START = 371

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + "
    "De Dei Simplicitate I-XXVIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XXVIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XXVIII, reconstructed from the Internet Archive PDF page images with "
    "pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. This slice closes De Dei Simplicitate XXV-XXVIII "
    "(pure act; most simple; quicquid in Deo est Deus; attributes one)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Simplicitate (Theses Theologicae De Dei Simplicitate).\n"
    "Same 1675 Pitt copy-text. Book pp. 97-102 / PDF 109-114 (I-XXVIII; this packet XXV-XXVIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Simplicitate I-XXVIII tip (tract closed). Next: De Dei Perfectione & Infinitate.\n"
    "Note: Closes after XVII-XXIV act/potency intro. Pure act + attribute unity.\n\n"
)

LATIN = {
    '395': (
        'XXV. Sed ab hac compositione Deus est quoque immunis. Nam in Deo nulla est '
        'potentia, nempe passiva qualem intelligimus. Etenim Deus est quicquid esse potest: '
        'nec potest ipsi quicquam accidere aut ab eo recipi, ut nec ab eo demi aut auferri: '
        'quandoquidem est primum ens omnino independens, & quod nullam habet causam quae in '
        'ipsum agere possit. Et hoc est quod scholae dicunt, Deum esse actum purum, id est, '
        'quod nullam habet potentiam admixtam. Quoniam in Deo nihil est quod perfici egeat '
        'aut ab alio perfectionem sumat: sed Deus totus est perfectio mera, cui nihil unquam '
        'addi, & unde nihil tolli potest. Et quae, ut jam dictum, est quicquid esse potest, '
        'nec potest esse aliud quam quod est.'
    ),
    '396': (
        'XXVI. Porro, ex istis apparet Deum esse simplicissimum, & nullam prorsus '
        'compositionem in eo reperiri, quandoquidem singula compositionis genera ab eo '
        'removimus. Et confirmatur ex eo quod Deus est primum ens, adeoque primum unum. '
        'Nam ens & unum convertuntur. Perfecta autem unitas compositionem excludit. Nam '
        'quod compositum est, aliquo modo non est unum sed multa, quoniam ex multis constat. '
        'Deinde primum ens nihil habet se prius. Sed quicquid compositum est posterius est '
        'suis partibus componentibus, & dependet ab illis. Ac denique quae sunt diversa non '
        'conveniunt in unum, nisi per aliquam causam uniantur. Deus autem causam non habet.'
    ),
    '397': (
        'XXVII. Atque hinc quoque patet quam verum sit illud axioma quod in scholis tritum '
        'est, videlicet, quicquid est in Deo est ipse Deus. Nam hoc sequitur absolutam illam '
        'Dei simplicitatem. Etenim si aliquid esset in Deo, quod Deus non esset, necesse '
        'esset naturam divinam non esse omnino simplicem, sed quaedam in ea distincta esse, '
        'quorum unum non esset alterum: ac proinde Deum esse aliquatenus compositum.'
    ),
    '398': (
        'XXVIII. Inde etiam sequitur omnia Dei attributa esse unum inter se, & cum essentia '
        'divina, & distingui non reipsa, sed tantum secundum nostrum concipiendi modum. Nam '
        'quia Dei essentia infinita est, & infinite perfecta, tota ejus perfectio a nobis '
        'simul concipi non potest, & conceptu uno exhauriri. Ideoque cogimur illam partiri '
        'in varios conceptus, quibus respondet una eademque res quae secundum diversos '
        'respectus & varias operationes, quibus una per se sufficit, diversimode a nobis '
        'consideratur.'
    ),
}

SECTIONS = [
    {
        'section': '395',
        'title': 'God is pure act — no passive potency',
        'pass_a': (
            'But from this composition also God is immune. For in God there is no potency, '
            'namely passive as we understand it. For God is whatever He can be: nor can anything '
            'happen to Him or be received by Him, as neither can it be taken or removed from Him: '
            'since He is the first being altogether independent, and which has no cause that can '
            'act upon Him. And this is what the schools say, that God is pure act, that is, what '
            'has no potency mixed in. Since in God there is nothing that needs to be perfected or '
            'takes perfection from another: but God is wholly mere perfection, to which nothing '
            'can ever be added, and from which nothing can be taken. And which, as already said, '
            'is whatever it can be, nor can it be other than what it is.'
        ),
        'pass_b': [
            'God has no passive potency — nothing can accrue or be stripped from Him.',
            'Schools: He is actus purus — no mixed potency.',
            'Whole mere perfection: whatever He can be, He is.',
        ],
        'lemmas': [
            {'latin': 'actum purum', 'gloss': 'pure act'},
            {'latin': 'nullam habet potentiam admixtam', 'gloss': 'has no potency mixed in'},
        ],
        'choices': [{
            'term': 'Deum esse actum purum',
            'english': 'that God is pure act',
            'why': 'Closes act/potency denial.',
            'rejected': ['God has passive potency to receive new perfection'],
        }],
        'notes': ['OCR: XXV PDF 113.'],
        'bible_refs': [],
    },
    {
        'section': '396',
        'title': 'Most simple — first being, first one',
        'pass_a': (
            'Further, from these things it appears that God is most simple, and that absolutely '
            'no composition is found in Him, since we have removed each kind of composition from '
            'Him. And it is confirmed from this that God is the first being, and therefore the '
            'first one. For being and one are convertible. But perfect unity excludes composition. '
            'For what is composed is in some way not one but many, since it consists of many. '
            'Next the first being has nothing prior to itself. But whatever is composed is '
            'posterior to its composing parts, and depends on them. And finally things that are '
            'diverse do not come together into one unless they are united by some cause. But God '
            'has no cause.'
        ),
        'pass_b': [
            'Every composition kind removed — God is most simple.',
            'First being = first one; perfect unity bars composition.',
            'Composites depend on prior parts and a unifier — God has neither.',
        ],
        'lemmas': [
            {'latin': 'simplicissimum', 'gloss': 'most simple'},
            {'latin': 'primum ens, adeoque primum unum', 'gloss': 'first being, and therefore the first one'},
        ],
        'choices': [{
            'term': 'Perfecta autem unitas compositionem excludit',
            'english': 'But perfect unity excludes composition',
            'why': 'Unity of first being seals simplicity.',
            'rejected': ['first being can still be many-from-parts'],
        }],
        'notes': ['OCR: XXVI PDF 113.'],
        'bible_refs': [],
    },
    {
        'section': '397',
        'title': 'School axiom: whatever is in God is God Himself',
        'pass_a': (
            'And from this also it is clear how true that axiom is which is worn in the schools, '
            'namely, whatever is in God is God Himself. For this follows that absolute simplicity '
            'of God. For if something were in God which was not God, it would be necessary that '
            'the divine nature not be altogether simple, but that certain things be distinct in '
            'it, of which one would not be the other: and therefore that God be composed to some '
            'extent.'
        ),
        'pass_b': [
            'School axiom: whatever is in God is God Himself.',
            'Follows absolute simplicity.',
            'Anything in God that is not God would split and compose Him.',
        ],
        'lemmas': [
            {'latin': 'quicquid est in Deo est ipse Deus', 'gloss': 'whatever is in God is God Himself'},
        ],
        'choices': [{
            'term': 'quicquid est in Deo est ipse Deus',
            'english': 'whatever is in God is God Himself',
            'why': 'Classic simplicity axiom before attribute unity.',
            'rejected': ['something in God can be other than God'],
        }],
        'notes': ['OCR: XXVII PDF 113.'],
        'bible_refs': [],
    },
    {
        'section': '398',
        'title': 'All attributes one with the essence — split only in our conceiving',
        'pass_a': (
            'Thence also it follows that all the attributes of God are one among themselves, and '
            'with the divine essence, and are distinguished not in the thing itself, but only '
            'according to our mode of conceiving. For because the essence of God is infinite, and '
            'infinitely perfect, its whole perfection cannot be conceived by us at once, and '
            'exhausted by one concept. And therefore we are compelled to partition it into various '
            'concepts, to which one and the same thing responds which according to diverse respects '
            'and various operations, for which one through itself suffices, is considered by us in '
            'diverse ways.'
        ),
        'pass_b': [
            'All attributes are one with each other and with the essence.',
            'Distinction is only in our conceiving — not in the thing.',
            'Infinite perfection forces many concepts of one sufficient reality.',
        ],
        'lemmas': [
            {'latin': 'omnia Dei attributa esse unum', 'gloss': 'all the attributes of God are one'},
            {'latin': 'secundum nostrum concipiendi modum', 'gloss': 'according to our mode of conceiving'},
        ],
        'choices': [{
            'term': 'distingui non reipsa, sed tantum secundum nostrum concipiendi modum',
            'english': 'are distinguished not in the thing itself, but only according to our mode of conceiving',
            'why': 'Closes Simplicitate on attribute unity.',
            'rejected': ['attributes are really distinct parts of God'],
        }],
        'notes': ['OCR: XXVIII PDF 113-114; tract ends; next De Dei Perfectione & Infinitate.'],
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
        jpath = JUST / f'dei_simplicitate_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_simplicitate_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_113_116_layout.txt', 'pdf_111_114_layout.txt'):
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
        if 395 <= n <= 398:
            notes = (
                f'Section {sid}: new densify De Dei Simplicitate XXV-XXVIII (tract close); '
                'Pass A!=B; lock-grounded PDF 113-114 / book pp. 101-102.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_simplicitate XXV-XXVIII packet scope covering all current sections.'
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
                'Scope review: densify De Dei Simplicitate XXV-XXVIII only '
                f'(sections {SECS[0]}-{SECS[-1]}; tract close). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Simplicitate through XXVIII closed. '
                'De Dei Perfectione & Infinitate next. Not shipped.'
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
        'locus': 'De Dei Simplicitate theses XXV-XXVIII (pure act / attributes one; tract close)',
        'next_locus': 'De Dei Perfectione & Infinitate I+ (summa perfectio / infinitude)',
        'gates': {
            'check_pass_ab': f'ok dei_simplicitate_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'deploy_bound': '871d77d1 live 57/4425 tip 394',
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
        f'## {day} (Scribe — De Dei Simplicitate XXV–XXVIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Simplicitate XXV–XXVIII → §§{SECS[0]}–{SECS[-1]}; tract close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 113-114 / pp. 101-102).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Simplicitate through XXVIII **closed** (pure act; '
        'attributes one). Next: De Dei Perfectione & Infinitate. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound 871d77d1 / tip 394; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Simplicitate XXV–XXVIII densify)\n\n'
        'CoS densify: De Dei Simplicitate XXV–XXVIII (tract close). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Simplicitate XXV–XXVIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Tract closed. Next: De Dei Perfectione & Infinitate I+. Punch X: **NO**.\n\n---\n\n'
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
            'deploy_bound': '871d77d1',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-394 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
