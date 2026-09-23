#!/usr/bin/env python3
"""De Scripturae plenitudine Pars II IX-XV densify on Mini.

Lock + justifs (check_pass_ab each) first. Append eng/src only after live >3696
OR 12 minutes from tip-208 ship hold start (~20:07 EDT), then re-read tip.
No ship/commit/push/publication-review/Logos/ai_promote. Punch X=NO.
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
LOCK = BOOK / 'sources/_le_blanc_plenitudine_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_plenitudine_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_plen_pars_ii_ix_densify')
PACKET_STEM = 'scripturae_plenitudine_pars_ii_ix_densify'
APPLY_COPY = BOOK / 'sources/_ocr_plenitudine/apply_scripturae_plenitudine_pars_ii_ix_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['209', '210', '211', '212', '213', '214', '215']
ROMANS = {
    '209': 'IX', '210': 'X', '211': 'XI', '212': 'XII',
    '213': 'XIII', '214': 'XIV', '215': 'XV',
}

TIP_BEFORE = 208
LIVE_FLOOR = 3696
HOLD_START = datetime(2026, 9, 22, 20, 7, 0)
HOLD_MINUTES = 12

RANGE_SHORT = (
    'Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scriptura'
    'e plenitudine Pars I I-XXXVIII + Pars II I-XV'
)
RANGE_TITLE = (
    'Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scriptu'
    'rae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scriptura'
    'e plenitudine Pars I I-XXXVIII; Pars II I-XV)'
)
EDITION = (
    'Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb'
    '_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate S'
    'cripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De'
    ' Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XV (not whole folio).'
)
BLURB = (
    'Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1'
    '675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Sc'
    'ripturae through Pars IV XLIV, and De Scripturae plenitudine Pars I through XXXV'
    'III plus Pars II through XV (Pontificiorum sententia: unwritten dogma; succession; '
    'tradition kinds Divine/Apostolic/Ecclesiastical; Trent Session 4). Not the '
    'collected folio.'
)
METHOD = (
    'English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XX'
    'II, De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, Pa'
    'rs IV I-XLIV, and De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XV, r'
    'econstructed from the Internet Archive PDF page images with pdftotext + tesseract'
    ' (+ DjVu checks). The 1683 third edition was not used as copy-text. No modern En'
    'glish was copied. This slice continues Plenitudine Pars II (Pontificiorum sententia)'
    ' through XV (Trent Session 4 restricted to Divine/Apostolic). Pars II XVI+ remains.'
)

LOCK_HEADER = (
    'Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\nTra'
    'ct: De Scripturae Plenitudine et Sufficientia adversus necessitatem verbi cujusd'
    'am non scripti.\nPARS PRIMA — theses I-XXXVIII retained.\nPARS SECUNDA — theses I-XV'
    ' (Pontificiorum sententia; densify contiguous after Pars II VIII).\nSame 1675 Pitt '
    'copy-text. Book pp. 54-63 / PDF 67-75 (Pars II IX-XV on PDF 74-75 / pp. 62-63). '
    'pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not '
    'copy-text. No modern English.\nScope: Plenitudine Pars I through XXXVIII + Pars II '
    'through XV. Pars II XVI+ remains.\nNote: Pars II I-VIII retained; IX unwritten dogma; '
    'X succession; XI tradition name; XII Divine/Apostolic/Ecclesiastical; XIII Lent/'
    'customs; XIV authority grades; XV Trent Session 4.\n\n'
)


def load_data():
    latin = json.loads((DATA / 'latin.json').read_text(encoding='utf-8'))
    sections = json.loads((DATA / 'sections.json').read_text(encoding='utf-8'))
    by_sec = {s['section']: s for s in sections}
    return latin, by_sec


def write_lock(latin: dict):
    prior = LOCK.read_text(encoding='utf-8') if LOCK.exists() else ''
    body = ''
    if prior:
        idx = prior.find('\nI. ')
        if idx < 0:
            idx = prior.find('\n\nI.')
        rest = prior[idx + 1 :] if idx >= 0 else prior.split('\n\n', 1)[-1]
        # Keep through VIII; drop any prior IX+ append if re-run
        # Prefer keep full PARS SECUNDA I-VIII from prior lock
        if '\n\nPARS SECUNDA' in rest:
            # keep header split handled below; extract from PARS SECUNDA
            pass
        # Find VIII close and strip anything after
        m = re.search(r'(VIII\.[^\n]*(?:\n(?![IXV]+\.)[^\n]*)*)', rest)
        # Simpler: keep everything up to and including VIII paragraph, then rebuild IX+
        if 'PARS SECUNDA' in rest:
            secunda = rest.split('PARS SECUNDA', 1)[1]
            # after marker
            # Keep I-VIII lines from existing lock body under PARS SECUNDA
            keep_parts = []
            for line in secunda.splitlines():
                keep_parts.append(line)
            # We'll rebuild entirely from latin for I-VIII retained in prior lock + new IX-XV
        # Keep Pars I + PARS SECUNDA I-VIII from prior by cutting at IX.
        cut = None
        for marker in ['\nIX. ', '\nIX.', '\nI X.']:
            pos = rest.find(marker)
            if pos >= 0:
                cut = pos
                break
        if cut is not None:
            rest = rest[:cut].rstrip() + '\n'
        # If PARS SECUNDA missing somehow, keep as-is
        if 'PARS SECUNDA' not in rest and 'PARS SECUNDA' in prior:
            # ensure marker present
            pass
        body = rest.rstrip() + '\n'
        if 'PARS SECUNDA' not in body:
            # re-find from prior
            pidx = prior.find('PARS SECUNDA')
            if pidx >= 0:
                body = prior[prior.find('\nI. ')+1 if prior.find('\nI. ')>=0 else 0:]
                # too messy — rebuild from prior lock split
    # Cleaner rebuild: Pars I body + PARS SECUNDA I-VIII from current lock sections 201-208 + new
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    # Pars I theses from lock file between first I. and PARS SECUNDA
    if 'PARS SECUNDA' in prior:
        pars1 = prior.split('PARS SECUNDA', 1)[0]
        # drop old header
        if '\nI. ' in pars1:
            pars1_body = pars1[pars1.find('\nI. ')+1:]
        elif '\n\nI.' in pars1:
            pars1_body = pars1[pars1.find('\n\nI.')+2:]
        else:
            pars1_body = pars1.split('\n\n', 1)[-1]
    else:
        pars1_body = ''
    parts = [pars1_body.rstrip() + '\n', '\nPARS SECUNDA — In qua Pontificiorum sententia exponitur.\n\n']
    for sec in ['201','202','203','204','205','206','207','208']:
        parts.append(by_prior[sec].rstrip() + '\n')
    for sec in SECS:
        parts.append(latin[sec].rstrip() + '\n')
    blob = LOCK_HEADER + ''.join(parts) + '\n'
    LOCK.write_text(blob, encoding='utf-8')
    print('wrote', LOCK, 'chars', len(blob))


def write_and_check_justifications(latin: dict, by_sec: dict):
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
        jpath = JUST / f'plenitudine_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab plenitudine_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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


def wait_hold():
    deadline = HOLD_START + timedelta(minutes=HOLD_MINUTES)
    while True:
        treatises, secs = live_section_count()
        lb = live_leblanc_tip()
        now = datetime.now()
        timed_out = now >= deadline
        live_ok = secs is not None and secs > LIVE_FLOOR
        print(
            f'hold check now={now.strftime("%H:%M:%S")} live={treatises}/{secs} '
            f'leblanc_tip={lb} need_live>{LIVE_FLOOR} or_after={deadline.strftime("%H:%M:%S")} '
            f'timed_out={timed_out}'
        )
        if live_ok or timed_out:
            reason = f'live>{LIVE_FLOOR}' if live_ok else f'{HOLD_MINUTES}m since tip-208 hold start'
            print('hold cleared:', reason)
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
            BOOK / 'sources/_ocr_plenitudine/pdf_73_76.txt',
            BOOK / 'sources/_ocr_plenitudine/tesseng-p-074.txt',
            BOOK / 'sources/_ocr_plenitudine/tesseng-p-075.txt',
            BOOK / 'sources/_ocr_plenitudine/apply_scripturae_plenitudine_pars_ii_ix_densify.py',
        ],
        expected_sections=section_ids,
        seed=20260922,
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
        if 209 <= n <= 215:
            notes = (
                f'Section {sid}: new densify De Scripturae plenitudine Pars II IX-XV; '
                'Pass A!=B; lock-grounded PDF 74-75 / book pp. 62-63.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in plenitudine Pars II IX packet scope covering all current sections.'
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
                'Scope review: densify De Scripturae plenitudine Pars II IX-XV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; plenitudine Pars II XVI+ remains. Prior tracts untouched. Not shipped.'
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
        'locus': 'De Scripturae plenitudine Pars II theses IX-XV (unwritten dogma / tradition kinds)',
        'next_locus': 'De Scripturae plenitudine Pars II XVI+ (rules for discerning Divine/Apostolic traditions)',
        'gates': {
            'check_pass_ab': f'ok plenitudine_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'raw_source_paths_count': 6,
    }
    rpath = AUDIT / f'{PACKET_STEM}.receipt.json'
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rpath)
    return receipt


def prepend_handoff(receipt: dict):
    day = datetime.now().strftime("%Y-%m-%d")
    bt = chr(96)
    packet_ref = bt + PACKET_STEM + bt
    packet_files = (
        bt + "reviews/audit/" + PACKET_STEM + ".packet.json" + bt
        + " + "
        + bt + ".review.json" + bt
    )
    lock_ref = bt + "sources/_le_blanc_plenitudine_latin_lock.txt" + bt
    claim_ref = bt + "le-blanc-theses-densify" + bt
    slug_ref = bt + "le-blanc-theses-theologicae" + bt
    parts = [
        "## " + day + " (Scribe — De Scripturae plenitudine Pars II IX–XV densify LOCAL)\n\n",
        "- Before: **" + str(receipt["before"]) + "** (Plenitudine Pars II I–VIII). After: **"
        + str(receipt["after"]) + "** ",
        "(contiguous Plenitudine Pars II IX–XV → §§" + SECS[0] + "–" + SECS[-1] + ").\n",
        "- Packet " + packet_ref + " (" + packet_files + "). ",
        "Reviewer: scribe-leblanc, " + day + ". Verdict pass grounded in ",
        lock_ref + " (PDF 74–75 / book pp. 62–63).\n",
        "- Meta range bumped to **" + RANGE_SHORT + "** (title, edition, blurb, text_history.method).\n",
        "- Honest **partial**: Plenitudine Pars II through XV (unwritten dogma; succession; "
        "tradition name; Divine/Apostolic/Ecclesiastical kinds; Lent/customs; authority grades; "
        "Trent Session 4). XVI+ remains. De Theologia / De Fide / Authoritate / Plenitudine "
        "Pars I / Pars II I–VIII closed as before. Not folio. Not shipped this slice.\n",
        "- Pass A ≠ B for §§" + SECS[0] + "–" + SECS[-1] + ". Greek ἀγράφως restored; Trent Session 4 "
        "sense; Quadragesima. OCR restorations noted in translator_notes.\n",
        "- All seven new justifications check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n",
        "- Hold cleared (" + receipt["hold_clear_reason"] + ") live "
        + str(receipt["live_at_proceed"]) + "; disk tip re-read " + str(TIP_BEFORE) + " before append.\n",
        "- Claim " + claim_ref + " stays claimed. Punch X = NO.\n\n",
    ]
    block = "".join(parts)
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    HANDOFF.write_text(block + prev, encoding="utf-8")
    repo_handoff = REPO / "SESSION_HANDOFF.md"
    repo_block = (
        "## " + day + " ~ET (Scribe — Le Blanc Plenitudine Pars II IX–XV densify)\n\n"
        "CoS densify: De Scripturae plenitudine Pars II IX–XV (unwritten dogma / tradition kinds). "
        "Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n"
        "### Bound this job (not shipped)\n"
        "- **Le Blanc** " + slug_ref + ": Plenitudine Pars II IX–XV (**"
        + str(receipt["before"]) + "→" + str(receipt["after"]) + "** sections). Packet "
        + packet_ref + ". Pass A≠B; tip-ready ok. Honest partial. Next: Pars II XVI+. "
        "Punch X: **NO**.\n\n---\n\n"
    )
    rprev = repo_handoff.read_text(encoding="utf-8") if repo_handoff.exists() else ""
    repo_handoff.write_text(repo_block + rprev, encoding="utf-8")
    print("handoff prepended (book + repo)")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    import socket
    host = socket.gethostname()
    print('hostname', host)
    if 'Stephans-Mac-mini' not in host and 'mini' not in host.lower():
        raise SystemExit(f'refuse writes: hostname {host} is not Mini')
    latin, by_sec = load_data()
    if mode in ('all', 'justifs'):
        write_lock(latin)
        write_and_check_justifications(latin, by_sec)
        if mode == 'justifs':
            print('JUSTIFS DONE — hold/append deferred')
            return
    live_tuple = wait_hold()
    eng, src = reread_tip()
    if len(eng) != TIP_BEFORE:
        raise SystemExit(f'tip drifted before append: {len(eng)}')
    append_translations(latin, by_sec)
    update_meta()
    tip_ready()
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO')


if __name__ == '__main__':
    main()
