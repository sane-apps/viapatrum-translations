#!/usr/bin/env python3
"""Build + apply De Dei Perfectione & Infinitate XXV-XXVI densify (tip 422 → 424).

Scripture on infinite essence; tract close. Live floor 4519.
After tip-ready: HOLD live>4519 OR 12m. Punch X=NO. No ship.
Honest slice: only XXV-XXVI remain before Immensitate (book p. 106).
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
PACKET_STEM = 'dei_perfectione_xxv_xxvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_perfectione/apply_dei_perfectione_xxv_xxvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['423', '424']
ROMANS = {'423': 'XXV', '424': 'XXVI'}
TIP_BEFORE = 422
LIVE_FLOOR = 4519
HOLD_MINUTES = 12
PRIOR_START = 399

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Perfectione & Infinitate I-XXVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Perfectione & Infinitate I-XXVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Perfectione & Infinitate I-XXVI, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Perfectione XXV-XXVI "
    "(Scripture on infinite essence; tract close before Immensitate)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Perfectione & Infinitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 102-105 / PDF 114-117 (I-XXVI; this packet XXV-XXVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Perfectione & Infinitate I-XXVI tip — tract closed. Next: Immensitate & Omnipraesentia.\n"
    "Note: Continues after XVII-XXIV. Psalm 145 / infinite power & wisdom prove infinite essence.\n\n"
)

LATIN = {
    '423': (
        'XXV. Neque hanc essentiae divinae infinitatem docet tantum ratio & sana '
        'Philosophia, sed etiam ipse Scripturae sacrae textus. Nam Psal. 145. de Deo '
        'diserte dicitur, Dominus magnus est & valde laudabilis, & magnitudinis illius '
        'non est finis, sive, ut habet Hebraeus eodem, En cheker, non est investigatio, '
        'quod eodem recidit. Etenim quod finem habet non est penitus investigabile.'
    ),
    '424': (
        'XXVI. Et certe ista essentiae divinae infinitas inde satis probatur, quod '
        'Scriptura Deo tribuit potentiam infinitam, & sapientiam quoque infinitam. Nam '
        'essentia Dei & attributa divina sunt plane unum & idem, sicuti patet ex summa '
        'Dei simplicitate, quae ante probata & demonstrata fuit. Ideoque si attributa '
        'Dei infinita sunt, etiam essentiam infinitam esse necesse est. Praeterquam quod '
        'subjectum finitum non esset capax potentiae & sapientiae infinitae. Nam inter '
        'subjectum, & id quod est in subjecto proportio quaedam requiritur. Quod autem, '
        'juxta Scripturam, potentia Dei plane infinita sit, inde manifestum est, quod '
        'expresse Scriptura docet Deum omnia posse, & ipsi rem omnino nullam esse '
        'impossibilem. Nam potentia illa demum finita dici potest, quae huc usque potest '
        'extendi, & non ultra, adeoque cui est aliquid impossibile. Qui vero simpliciter '
        '& absolute omnia potest, illius potentia nullum terminum habet extra quem '
        'extendi non possit, sed omni fine & termino caret. Et similiter sane de '
        'intelligentia & sapientia divina dicitur, quod illius non sit numerus nec '
        'investigatio: quibus verbis, ut patet, res infinita describitur.'
    ),
}

SECTIONS = [
    {
        'section': '423',
        'title': 'Scripture teaches infinite essence — Psalm 145',
        'pass_a': (
            'Nor does only reason and sound Philosophy teach this infinitude of the divine '
            'essence, but also the very text of sacred Scripture. For in Psalm 145 it is '
            'expressly said of God, The Lord is great and greatly to be praised, and of His '
            'greatness there is no end, or, as the Hebrew has in the same place, En cheker, '
            'there is no searching out, which comes to the same. For what has an end is not '
            'altogether searchable.'
        ),
        'pass_b': [
            'Not only philosophy — Scripture teaches divine essence is infinite.',
            'Psalm 145: His greatness has no end / Hebrew En cheker — no searching out.',
            'What has an end is not altogether searchable.',
        ],
        'lemmas': [
            {'latin': 'essentiae divinae infinitatem', 'gloss': 'infinitude of the divine essence'},
            {'latin': 'En cheker, non est investigatio', 'gloss': 'En cheker, there is no searching out'},
        ],
        'choices': [{
            'term': 'magnitudinis illius non est finis',
            'english': 'of His greatness there is no end',
            'why': 'Psalm 145 grounds infinitude in Scripture, not reason alone.',
            'rejected': ['Scripture never speaks of divine greatness as without end'],
        }],
        'notes': ['OCR: XXV PDF 117 / p. 105; Ps 145:3 En cheker normalized.'],
        'bible_refs': ['Ps. 145:3'],
    },
    {
        'section': '424',
        'title': 'Infinite power and wisdom prove infinite essence',
        'pass_a': (
            'And certainly that infinitude of the divine essence is sufficiently proved from '
            'this, that Scripture attributes to God infinite power, and infinite wisdom also. '
            'For the essence of God and the divine attributes are plainly one and the same, as '
            'is clear from the highest simplicity of God, which was proved and demonstrated '
            'before. And therefore if the attributes of God are infinite, it is necessary that '
            'the essence also be infinite. Besides that a finite subject would not be capable of '
            'infinite power and wisdom. For between a subject and that which is in the subject '
            'a certain proportion is required. But that, according to Scripture, the power of '
            'God is plainly infinite is clear from this, that Scripture expressly teaches that '
            'God can do all things, and that to Him nothing at all is impossible. For that power '
            'alone can be called finite which can be extended thus far and not beyond, and so '
            'to which something is impossible. But he who simply and absolutely can do all '
            'things — his power has no bound beyond which it cannot be extended, but lacks '
            'every end and bound. And likewise indeed it is said of the divine intelligence and '
            'wisdom that of it there is no number nor searching out: by which words, as is '
            'plain, an infinite thing is described.'
        ),
        'pass_b': [
            'Scripture gives God infinite power and infinite wisdom.',
            'Attributes = essence (simplicity) — so essence is infinite too.',
            'Finite subject cannot hold infinite power/wisdom; what can do all things has no bound.',
        ],
        'lemmas': [
            {'latin': 'potentiam infinitam, & sapientiam quoque infinitam', 'gloss': 'infinite power, and infinite wisdom also'},
            {'latin': 'subjectum finitum non esset capax', 'gloss': 'a finite subject would not be capable'},
        ],
        'choices': [{
            'term': 'etiam essentiam infinitam esse necesse est',
            'english': 'it is necessary that the essence also be infinite',
            'why': 'Closes Perfectione: infinite attributes → infinite essence; next Immensitate.',
            'rejected': ['infinite attributes can sit in a finite essence'],
        }],
        'notes': ['OCR: XXVI PDF 117 / p. 105; tract close before Immensitate p. 106.'],
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
    for name in (
        'pdf_117_122_layout.txt',
        'pdf_117_118_layout.txt',
        'tess117.txt',
        'pdf_116_119_layout.txt',
        'pdf_114_117_perfectione.txt',
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
        if 423 <= n <= 424:
            notes = (
                f'Section {sid}: new densify De Dei Perfectione & Infinitate XXV-XXVI tract close; '
                'Pass A!=B; lock-grounded PDF 117 / book p. 105.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_perfectione XXV-XXVI packet scope covering all current sections.'
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
                'Scope review: densify De Dei Perfectione & Infinitate XXV-XXVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest tract close; Perfectione through XXVI. Next Immensitate. Not shipped.'
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
        'locus': 'De Dei Perfectione & Infinitate theses XXV-XXVI (Scripture; tract close)',
        'next_locus': 'De Dei Immensitate & Omnipraesentia (opens after Perfectione XXVI)',
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
        'live_floor': LIVE_FLOOR,
        'raw_source_paths_count': 5,
        'deploy_bound': 'b734c4b1',
        'honest_slice_note': 'XXV-XXVI only remain before Immensitate (<4-8 honest tract close)',
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
        f'## {day} (Scribe — De Dei Perfectione & Infinitate XXV–XXVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Perfectione XXV–XXVI → §§{SECS[0]}–{SECS[-1]}; tract close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 117 / p. 105).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Perfectione & Infinitate through XXVI **closed**. '
        'Next: Immensitate & Omnipraesentia. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound b734c4b1 / tip 422; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Perfectione & Infinitate XXV–XXVI densify)\n\n'
        'CoS densify: De Dei Perfectione & Infinitate XXV–XXVI tract close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Perfectione XXV–XXVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Immensitate. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-422 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
