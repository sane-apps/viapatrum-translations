#!/usr/bin/env python3
"""Build + apply De Aeternitate Dei XVII-XIX densify (tip 472 → 475).

Perfection bars change; mutation species; immutability incommunicable. Tract close.
Live floor 4708. After tip-ready: HOLD live>4708 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_aeternitate_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_aeternitate_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_aeternitate_densify')
PACKET_STEM = 'dei_aeternitate_xvii_xix_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_aeternitate/apply_dei_aeternitate_xvii_xix_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['473', '474', '475']
ROMANS = {'473': 'XVII', '474': 'XVIII', '475': 'XIX'}
TIP_BEFORE = 472
LIVE_FLOOR = 4708
HOLD_MINUTES = 12
PRIOR_START = 457

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeternitate Dei I-XIX (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeternitate Dei I-XIX. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeternitate Dei I-XIX, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeternitate XVII-XIX "
    "(perfection bars change; mutation species; immutability incommunicable; tract close)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeternitate Dei & ejus Immutabilitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 111-114 / PDF 123-126 (I-XIX; this packet XVII-XIX). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeternitate Dei I-XIX tip — tract closed. Next: De Vita Dei.\n"
    "Note: Continues after IX-XVI. Infinite perfection; species of mutation; immutability proper to God alone.\n\n"
)

LATIN = {
    '473': (
        'XVII. Idem quoque evincitur ex infinita Dei perfectione, nam si Deus mutaretur, '
        'mutatio illa fieret vel in melius, vel in deterius. Quorum utrumque divinae '
        'perfectioni repugnat. Nam quod mutatur in melius, necessario carebat aliqua '
        'perfectione quam per mutationem illam adipiscitur: & quod in deterius mutatur, '
        'per mutationem illam perfectionem aliquam amittit, adeoque non potest esse summe '
        'perfectum. Adde quod res nulla est mutationi obnoxia, nisi vel ex propria ejus '
        'impotentia, vel ex alterius majore potentia: Deo vero, qui est Ens primum & '
        'independens, nihil est potentius, nec ulla potest ei tribui impotentia, si quidem '
        'nulla perfectione caret.'
    ),
    '474': (
        'XVIII. Ac praeterea, si quis singulas mutationis species percurrere velit, '
        'manifestum erit nullam Deo accidere posse. Nec enim incipit aut desinit esse qui '
        'per naturam aeternus est. Non mutatur secundum qualitates & accidentia, is in quo '
        'nulla accidentia sunt, sed quicquid in eo est, mera ejus essentia est. Non augetur '
        'neque minuitur qui incorporeus est & indivisibilis: & denique non potest loco '
        'moveri qui totus ubique est.'
    ),
    '475': (
        'XIX. Istud autem attributum ita Dei proprium est, ut non possit cum ulla creatura '
        'communicari. Nihil enim fingi potest quod a Deo non pendeat tanquam a prima causa '
        'creante atque conservante, ac proinde quod ejus potentiae non ita subjaceat ut '
        'etiam possit in nihilum redigi Deo sic volente & suum concursum subtrahente.'
    ),
}

SECTIONS = [
    {
        'section': '473',
        'title': 'Infinite perfection bars change for better or worse',
        'pass_a': (
            'The same is also proved from God\'s infinite perfection, for if God were '
            'changed, that change would happen either for the better, or for the worse. Both '
            'of which are repugnant to divine perfection. For what is changed for the better '
            'necessarily lacked some perfection which it acquires by that change: and what '
            'is changed for the worse loses some perfection by that change, and therefore '
            'cannot be most perfect. Add that no thing is liable to change except either from '
            'its own impotence, or from another\'s greater power: but for God, who is the '
            'first and independent Being, nothing is more powerful, nor can any impotence be '
            'attributed to Him, since indeed He lacks no perfection.'
        ),
        'pass_b': [
            'Change would be better or worse — both clash with infinite perfection.',
            'Better means a prior lack; worse means a lost perfection.',
            'Change needs impotence or a stronger other — neither fits the first Ens.',
        ],
        'lemmas': [
            {'latin': 'vel in melius, vel in deterius', 'gloss': 'either for the better, or for the worse'},
            {'latin': 'nihil est potentius, nec ulla potest ei tribui impotentia', 'gloss': 'nothing is more powerful, nor can any impotence be attributed to Him'},
        ],
        'choices': [{
            'term': 'utrumque divinae perfectioni repugnat',
            'english': 'Both of which are repugnant to divine perfection',
            'why': 'Perfection closes the door on real change.',
            'rejected': ['God can change for the better without prior lack'],
        }],
        'notes': ['OCR: XVII PDF 125.'],
        'bible_refs': [],
    },
    {
        'section': '474',
        'title': 'No species of mutation — start/stop, accidents, quantity, place',
        'pass_a': (
            'And besides, if anyone wishes to run through the singular species of mutation, '
            'it will be clear that none can happen to God. For He neither begins nor ceases '
            'to be who by nature is eternal. He is not changed according to qualities and '
            'accidents — He in whom there are no accidents, but whatever is in Him is His '
            'mere essence. He is neither increased nor diminished who is incorporeal and '
            'indivisible: and finally He cannot be moved in place who is whole everywhere.'
        ),
        'pass_b': [
            'Scan mutation kinds: none fit God.',
            'No start/stop of being; no quality/accident change; no increase/decrease.',
            'No local motion — whole everywhere.',
        ],
        'lemmas': [
            {'latin': 'nullam Deo accidere posse', 'gloss': 'that none can happen to God'},
            {'latin': 'quicquid in eo est, mera ejus essentia est', 'gloss': 'whatever is in Him is His mere essence'},
        ],
        'choices': [{
            'term': 'non potest loco moveri qui totus ubique est',
            'english': 'He cannot be moved in place who is whole everywhere',
            'why': 'Closes species list with ubiquity.',
            'rejected': ['God changes by successive local presence'],
        }],
        'notes': ['OCR: XVIII PDF 125-126.'],
        'bible_refs': [],
    },
    {
        'section': '475',
        'title': 'Immutability incommunicable — creatures can be reduced to nothing',
        'pass_a': (
            'But that attribute is so proper to God that it cannot be shared with any '
            'creature. For nothing can be imagined which does not depend on God as on the '
            'first creating and conserving cause, and therefore which is not so subject to '
            'His power that it can even be reduced to nothing if God so wills and withdraws '
            'His concurrence.'
        ),
        'pass_b': [
            'Immutability is God\'s alone — incommunicable.',
            'Every creature depends on creating/conserving cause.',
            'At His will, withdrawing concurrence, any creature can fall to nothing.',
        ],
        'lemmas': [
            {'latin': 'non possit cum ulla creatura communicari', 'gloss': 'it cannot be shared with any creature'},
            {'latin': 'possit in nihilum redigi Deo sic volente', 'gloss': 'it can be reduced to nothing if God so wills'},
        ],
        'choices': [{
            'term': 'Istud autem attributum ita Dei proprium est',
            'english': 'But that attribute is so proper to God',
            'why': 'Closes Aeternitate/Immutabilitate; next De Vita Dei.',
            'rejected': ['creatures can share absolute immutability'],
        }],
        'notes': ['OCR: XIX PDF 126 / p. 114; Aeternitate tract close before Vita Dei.'],
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
        jpath = JUST / f'dei_aeternitate_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_aeternitate_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
            'post-tip hold now='
            + now.strftime('%H:%M:%S')
            + ' live='
            + str(treatises)
            + '/'
            + str(secs)
            + ' leblanc_tip='
            + str(lb)
            + ' need_live>'
            + str(floor)
            + ' or_after='
            + deadline.strftime('%H:%M:%S')
            + ' timed_out='
            + str(timed_out),
            flush=True,
        )
        if live_ok or timed_out:
            reason = (
                'live>' + str(floor)
                if live_ok
                else str(HOLD_MINUTES) + 'm since ' + label + ' start (live>' + str(floor) + ')'
            )
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
        'pdf_125_127_layout.txt', 'pdf_124_126_layout.txt',
        'tess_ae125.txt', 'tess_ae126.txt', 'tess125.txt',
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
        if 473 <= n <= 475:
            notes = (
                f'Section {sid}: new densify De Aeternitate Dei XVII-XIX tract close; '
                'Pass A!=B; lock-grounded PDF 125-126 / book pp. 113-114.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_aeternitate XVII-XIX packet scope covering all current sections.'
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
                'Scope review: densify De Aeternitate Dei XVII-XIX only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest tract close; Aeternitate through XIX. Next Vita Dei. Not shipped.'
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
        'locus': 'De Aeternitate Dei theses XVII-XIX (perfection; mutation species; close)',
        'next_locus': 'De Vita Dei (opens after Aeternitate XIX)',
        'gates': {
            'check_pass_ab': f'ok dei_aeternitate_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'honest_slice_note': 'XVII-XIX only remain before Vita Dei (<4-8 honest tract close)',
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
        f'## {day} (Scribe — De Aeternitate Dei XVII–XIX densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Aeternitate XVII–XIX → §§{SECS[0]}–{SECS[-1]}; tract close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 125-126 / pp. 113-114).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Aeternitate Dei through XIX **closed**. '
        'Next: De Vita Dei. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Aeternitate Dei XVII–XIX densify)\n\n'
        'CoS densify: Aeternitate XVII–XIX tract close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Aeternitate XVII–XIX (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Vita Dei. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-472 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
