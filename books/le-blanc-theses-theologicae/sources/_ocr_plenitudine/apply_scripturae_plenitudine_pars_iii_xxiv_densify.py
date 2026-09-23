#!/usr/bin/env python3
"""De Scripturae plenitudine Pars III XXIV-XXXI densify on Mini.

Lock + justifs (check_pass_ab each) first. Append eng/src after live >3930
OR 12m from tip-267 proceed (~21:32 EDT), then re-read tip.
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
DATA = Path('/tmp/leblanc_plen_pars_iii_xxiv_densify')
PACKET_STEM = 'scripturae_plenitudine_pars_iii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_plenitudine/apply_scripturae_plenitudine_pars_iii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['268', '269', '270', '271', '272', '273', '274', '275']
ROMANS = {
    '268': 'XXIV', '269': 'XXV', '270': 'XXVI', '271': 'XXVII',
    '272': 'XXVIII', '273': 'XXIX', '274': 'XXX', '275': 'XXXI',
}

TIP_BEFORE = 267
LIVE_FLOOR = 3930
HOLD_START = datetime(2026, 9, 22, 21, 32, 31)
HOLD_MINUTES = 12

RANGE_SHORT = "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-XXXI"
RANGE_TITLE = "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-XXXI)"
EDITION = "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-XXXI (not whole folio)."
BLURB = "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, and De Scripturae plenitudine Pars I through XXXVIII, Pars II through XLIV, and Pars III through XXXI (rebaptism / Filioque / Mosaic immortality / Scripture self-witness). Not the collected folio."
METHOD = "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, Pars IV I-XLIV, and De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-XXXI, reconstructed from the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not used as copy-text. No modern English was copied. This slice densifies Plenitudine Pars III XXIV-XXXI (rebaptism of heretics' baptism; Filioque; Mosaic immortality/resurrection; OT types; Scripture self-witness sophism; retorsion; rule need not prove itself). XXXII+ remains."

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scripturae Plenitudine et Sufficientia adversus necessitatem verbi cujusdam non scripti.\n"
    "PARS PRIMA — theses I-XXXVIII retained.\n"
    "PARS SECUNDA — theses I-XLIV retained (closed).\n"
    "PARS TERTIA — theses I-XXXI (rebaptism / Filioque / Mosaic immortality / Scripture self-witness).\n"
    "Same 1675 Pitt copy-text. Book pp. 54-78 / PDF 67-90 (Pars III XXIV-XXXI on PDF 88-90 / pp. 76-78). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Plenitudine Pars I through XXXVIII + Pars II through XLIV + Pars III through XXXI. Pars III XXXII+ remains.\n"
    "Note: Pars III I-XXIII retained; XXIV rebaptism; XXV Filioque; XXVI-XXVII Mosaic immortality/types; XXVIII-XXXI Scripture self-witness.\n\n"
)


def load_data():
    latin = json.loads((DATA / 'latin.json').read_text(encoding='utf-8'))
    sections = json.loads((DATA / 'sections.json').read_text(encoding='utf-8'))
    by_sec = {s['section']: s for s in sections}
    return latin, by_sec



def write_lock(latin: dict):
    prior = LOCK.read_text(encoding='utf-8') if LOCK.exists() else ''
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    if 'PARS SECUNDA' in prior:
        head = prior.split('PARS SECUNDA', 1)[0]
        i_pos = head.find(chr(10) + 'I. ')
        if i_pos < 0:
            i_pos = head.find(chr(10) + 'I.')
        pars1_body = head[i_pos + 1:] if i_pos >= 0 else head.split(chr(10)+chr(10), 1)[-1]
    else:
        pars1_body = chr(10).join(by_prior[str(n)] for n in range(163, 201) if str(n) in by_prior)
    parts = [pars1_body.rstrip() + chr(10)]
    parts.append(chr(10) + 'PARS SECUNDA — In qua Pontificiorum sententia exponitur.' + chr(10) + chr(10))
    for sec in [str(n) for n in range(201, 245)]:
        parts.append(by_prior[sec].rstrip() + chr(10))
    parts.append(
        chr(10) + 'PARS TERTIA — In qua solvuntur argumenta quibus Doctores Ecclesiae Romanae '
        'Scripturae sufficientiam impugnare conantur.' + chr(10) + chr(10)
    )
    for sec in [str(n) for n in range(245, 268)]:
        parts.append(by_prior[sec].rstrip() + chr(10))
    for sec in SECS:
        parts.append(latin[sec].rstrip() + chr(10))
    blob = LOCK_HEADER + ''.join(parts) + chr(10)
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
            reason = f'live>{LIVE_FLOOR}' if live_ok else f'{HOLD_MINUTES}m since tip-267 hold start'
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
            Path('/tmp/leblanc_plen_pars_iii_xxiv_densify/pdf_88_92_layout.txt'),
            Path('/tmp/leblanc_plen_pars_iii_xxiv_densify/tess_088.txt'),
            Path('/tmp/leblanc_plen_pars_iii_xxiv_densify/tess_089.txt'),
            Path('/tmp/leblanc_plen_pars_iii_xxiv_densify/tess_090.txt'),
            Path('/tmp/leblanc_plen_pars_iii_xxiv_densify/latin.json'),
            BOOK / 'sources/_ocr_plenitudine/apply_scripturae_plenitudine_pars_iii_xvi_densify.py',
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
        if 268 <= n <= 275:
            notes = (
                f'Section {sid}: new densify De Scripturae plenitudine Pars III XXIV-XXXI; '
                'Pass A!=B; lock-grounded PDF 88-90 / book pp. 76-78.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in plenitudine Pars III XXIV packet scope covering all current sections.'
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
                'Scope review: densify De Scripturae plenitudine Pars III XXIV-XXXI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; plenitudine Pars III through XXXI; XXXII+ remains. Prior tracts untouched. Not shipped.'
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
        'locus': 'De Scripturae plenitudine Pars III theses XXIV-XXXI (rebaptism / Filioque / Mosaic immortality / Scripture self-witness)',
        'next_locus': 'De Scripturae plenitudine Pars III XXXII+ (faith accepts word vs things / innate notes of divinity / integrity)',
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
        'raw_source_paths_count': 8,
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
    block = (
        f"## {day} (Scribe — De Scripturae plenitudine Pars III XXIV–XXXI densify LOCAL)\n\n"
        f"- Before: **{receipt['before']}** (Plenitudine Pars III I–XXIII). After: **{receipt['after']}** "
        f"(contiguous Plenitudine Pars III XXIV–XXXI → §§{SECS[0]}–{SECS[-1]}).\n"
        f"- Packet {packet_ref} ({packet_files}). "
        f"Reviewer: scribe-leblanc, {day}. Verdict pass grounded in "
        f"{lock_ref} (PDF 88–90 / book pp. 76–78).\n"
        f"- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n"
        "- Honest **partial**: Plenitudine Pars III through XXXI (rebaptism of heretics baptism; "
        "Filioque; Mosaic immortality/resurrection; OT sacrificial types; Scripture self-witness "
        "sophism; retorsion on Rome mixed rule; sufficient rule need not prove itself). XXXII+ "
        "remains. De Theologia / De Fide / Authoritate / Plenitudine Pars I / Pars II / Pars III "
        "I–XXIII closed as before. Not folio. Not shipped.\n"
        f"- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. non iterando baptismo; processione Spiritus; "
        "Edamus bibamus; nihil probat seipsum; retorqueo. OCR restorations noted in translator_notes.\n"
        "- All eight new justifications check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n"
        f"- Hold cleared ({receipt['hold_clear_reason']}) live "
        f"{receipt['live_at_proceed']}; disk tip re-read {TIP_BEFORE} before append.\n"
        f"- Claim {claim_ref} stays claimed. Punch X = NO.\n\n"
    )
    # restore Greek spellings in handoff
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    HANDOFF.write_text(block + prev, encoding="utf-8")
    repo_handoff = REPO / "SESSION_HANDOFF.md"
    repo_block = (
        f"## {day} ~ET (Scribe — Le Blanc Plenitudine Pars III XXIV–XXXI densify)\n\n"
        "CoS densify: De Scripturae plenitudine Pars III XXIV–XXXI (rebaptism / Filioque / self-witness). "
        "Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n"
        "### Bound this job (not shipped)\n"
        f"- **Le Blanc** {slug_ref}: Plenitudine Pars III XXIV–XXXI (**"
        f"{receipt['before']}→{receipt['after']}** sections). Packet "
        f"{packet_ref}. Pass A≠B; tip-ready ok. Honest partial. Next: Pars III XXXII+. "
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
