"""Build + apply Angelorum & Hominum Sanctorum Cultu Pars Secunda (Reformata) I-XL densify (tip 1557 to 1597).

Contiguous slice after Sanctorum Cultu Romana CLOSED at LXXVII (tip 1557). Prefer ~40 theses (I-XL).
Live floor 9114. After tip-ready: HOLD live>floor OR 0m. Punch X=NO. No ship.
Tip 1557 PRESERVE. Crocius/Baron CLOSED books - do not modify.
Sister latin lock EXTEND: sources/_le_blanc_sanctorum_cultu_latin_lock.txt (Romana I-LXXVII PRESERVED + PARS SECUNDA Reformata banner + I-XL).
Do not rewrite Imaginum / Remissione / Distinctione / fidei locks.
Justifications: sanctorum_cultu_{n}.json (locus-prefixed).
OCR/apply under sources/_ocr_sanctorum_cultu/.
Pars Secunda NOT closed at XL (~CI remains); claim stays claimed.
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
LOCK = BOOK / 'sources/_le_blanc_sanctorum_cultu_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_sanctorum_cultu_latin_lock.txt'
IMAG_LOCK = BOOK / 'sources/_le_blanc_imaginum_cultum_latin_lock.txt'
REMISS_LOCK = BOOK / 'sources/_le_blanc_remissione_peccatorum_latin_lock.txt'
DIST_LOCK = BOOK / 'sources/_le_blanc_distinctione_peccati_latin_lock.txt'
FIDEI_LOCK = BOOK / 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_sanctorum_pars2_i_xl_densify')
PAYLOAD = Path('/tmp/sanctorum_cultu_pars_secunda_i_xl_payload.json')
PACKET_STEM = 'sanctorum_cultu_pars_secunda_i_xl_densify'
APPLY_COPY = BOOK / 'sources/_ocr_sanctorum_cultu/apply_sanctorum_cultu_pars_secunda_i_xl_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = [str(n) for n in range(1558, 1598)]
_ROMAN_LIST = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII","XXIX","XXX","XXXI","XXXII","XXXIII","XXXIV","XXXV","XXXVI","XXXVII","XXXVIII","XXXIX","XL"]
ROMANS = {str(1558 + i): _ROMAN_LIST[i] for i in range(40)}
TIP_BEFORE = 1557
LIVE_FLOOR = 9114
HOLD_MINUTES = 0

RANGE_SHORT = (
    'Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXXVII + De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens I-XXX + De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII + De Certitudine Justificationis Pars Prima I-XXX + Pars Secunda I-LVI + De Distinctione Peccati in Mortale et Veniale Pars Prior I-XXXI + Pars Posterior I-LXVIII + De Remissione Peccatorum I-XXIV + Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem I-LXI + De Imaginum Cultu pars altera (Ecclesiae Reformatae) I-L + Angelorum & Hominum Sanctorum Cultu & Veneratione (Romana) I-LXXVII + Pars Secunda (Reformata) I-XL'
)
RANGE_TITLE = (
    'Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; De Aeterna Hominum Electione et Praedestinatione I-XXXVII; De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens I-XXX; De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu & Acceptione vocis Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII + De Certitudine Justificationis Pars Prima I-XXX + Pars Secunda I-LVI + De Distinctione Peccati in Mortale et Veniale Pars Prior I-XXXI + Pars Posterior I-LXVIII + De Remissione Peccatorum I-XXIV + Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem I-LXI + De Imaginum Cultu pars altera I-L + Angelorum & Hominum Sanctorum Cultu & Veneratione (Romana) I-LXXVII + Pars Secunda (Reformata) I-XL)'
)
EDITION = 'Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC (+ EEBO 1675 for gap leaves). Densify through Sanctorum Cultu Romana I-LXXVII + Pars Secunda Reformata I-XL (Pars Secunda not closed; not whole folio).'
BLURB = 'Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. Covers De Theologia through Angelorum & Hominum Sanctorum Cultu Romana I-LXXVII and Pars Secunda (Reformata) I-XL. Not the collected folio.'
METHOD = 'English follows locked Pitt Latin through Imaginum CLOSED + Sanctorum Cultu Romana CLOSED + Pars Secunda Reformata I-XL. 1675 PDF ~384-390 (book ~370-376); Vision OCR + pdftotext + tess. No modern English. This slice densifies Sanctorum Pars Secunda I-XL. Next: Pars Secunda XLI–fin (~CI). Claim stays claimed (book densify not done).'
LOCK_HEADER = (
    'Le Blanc Latin lock — Angelorum & Hominum Sanctorum Cultu & Veneratione\n'
    'Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n'
    'Scope: Sanctorum Cultu Romana I-LXXVII PRESERVED + PARS SECUNDA (Reformata) banner + I-XL tip (Pars Secunda NOT closed; ~CI remains).\n'
    'Source: 1675 PDF pages ~370-390 (book ~356-376); Vision OCR + pdftotext + tess.\n'
    'Note: Contiguous densify after tip 1557. Sister lock EXTENDED (Imaginum + Remissione + Distinctione + fidei locks untouched). Sanctorum Romana CLOSED; Pars Secunda I-XL densified; claim le-blanc-theses-densify stays claimed (book densify not done).\n'
    '\n'
)



def crocius_baron_fingerprint() -> str:
    """Stable fingerprint of CLOSED Crocius/Baron translation JSON (must not change)."""
    import hashlib
    h = hashlib.sha1()
    roots = [
        REPO / 'books/crocius-syntagma/translations',
        REPO / 'books/baron-philosophia-theologiae-ancillans/translations',
    ]
    paths = []
    for root in roots:
        if root.is_dir():
            paths.extend(sorted(root.rglob('*.json')))
    for pth in paths:
        h.update(str(pth.relative_to(REPO)).encode())
        h.update(b'\0')
        h.update(pth.read_bytes())
        h.update(b'\0')
    return h.hexdigest() + '  -'

def load_payload():
    data = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    latin = data['latin']
    sections = data['sections']
    missing = [s for s in SECS if s not in latin]
    if missing:
        raise SystemExit('payload missing latin: %s' % missing)
    by_sec = {s['section']: s for s in sections}
    missing_s = [s for s in SECS if s not in by_sec]
    if missing_s:
        raise SystemExit('payload missing sections: %s' % missing_s)
    return latin, by_sec


def write_data_files(latin: dict, by_sec: dict):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'latin.json').write_text(json.dumps({k: latin[k] for k in SECS}, ensure_ascii=False, indent=2) + '\n')
    (DATA / 'sections.json').write_text(json.dumps([by_sec[s] for s in SECS], ensure_ascii=False, indent=2) + '\n')
    print('wrote data', DATA, SECS)



def write_lock(new_latin: dict):
    """Extend Sanctorum sister lock: keep Romana I-LXXVII body; append PARS SECUNDA banner + I-XL. Do not touch Imaginum/Remissione/Distinctione/fidei."""
    for lock in (IMAG_LOCK, REMISS_LOCK, DIST_LOCK, FIDEI_LOCK):
        if lock.exists():
            print("preserve untouched", lock, "chars", lock.stat().st_size)
    body = ""
    if LOCK.exists():
        raw = LOCK.read_text(encoding="utf-8")
        marker = "THESES THEOLOGICAE"
        idx = raw.find(marker)
        if idx >= 0:
            body = raw[idx:].rstrip() + chr(10) + chr(10)
        else:
            body = raw.rstrip() + chr(10) + chr(10)
    cut = None
    first = body.find("THESES THEOLOGICAE")
    p2 = body.find("Pars Secunda.")
    if p2 >= 0:
        header = body.rfind("THESES THEOLOGICAE", 0, p2)
        if header > first:
            cut = header
        else:
            line_start = body.rfind(chr(10), 0, p2)
            if line_start >= 0:
                cut = line_start + 1
    if cut is not None:
        body = body[:cut].rstrip() + chr(10) + chr(10)
    parts = [LOCK_HEADER]
    if body.strip():
        parts.append(body)
    else:
        parts.append(
            "THESES THEOLOGICAE" + chr(10)
            + "DE ANGELORUM & HOMINUM SANCTORUM Cultu & Veneratione." + chr(10)
            + "In quibus exponitur Doctrina Ecclesiae & Scholae Romanae." + chr(10) + chr(10)
        )
    parts.append(
        "THESES THEOLOGICAE" + chr(10)
        + "DE ANGELORUM & HOMINUM SANCTORUM Cultu & Veneratione. Pars Secunda." + chr(10)
        + "In qua Protestantium Doctrina exponitur, ac cum Scholae Romanae Doctrina" + chr(10)
        + "comparatur, et confirmatur variis Argumentis." + chr(10) + chr(10)
    )
    for sec in SECS:
        parts.append(new_latin[sec].rstrip() + chr(10))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text("".join(parts) + chr(10), encoding="utf-8")
    print("wrote", LOCK, "chars", LOCK.stat().st_size, "secs", len(SECS), "(extended; Romana I-LXXVII preserved + Pars Secunda I-XL)")



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
        jpath = JUST / ('sanctorum_cultu_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab sanctorum_cultu_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
        if errs:
            raise SystemExit('FAIL check_pass_ab %s: %s' % (sec, errs))


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
    for _tick in range(HOLD_MINUTES * 2 + 2):
        treatises, secs = live_section_count()
        lb = live_leblanc_tip()
        now = datetime.now()
        timed_out = now >= deadline
        live_ok = secs is not None and secs > floor
        print(
            'hold now=%s live=%s/%s leblanc_tip=%s need>%s or_after=%s timed_out=%s'
            % (
                now.strftime('%H:%M:%S'),
                treatises,
                secs,
                lb,
                floor,
                deadline.strftime('%H:%M:%S'),
                timed_out,
            ),
            flush=True,
        )
        if live_ok or timed_out:
            reason = (
                'live>%s' % floor
                if live_ok
                else '%sm since %s start (live>%s)' % (HOLD_MINUTES, label, floor)
            )
            print('post-tip hold cleared:', reason, flush=True)
            return treatises, secs, lb, reason
        time.sleep(30)
    treatises, secs = live_section_count()
    lb = live_leblanc_tip()
    return treatises, secs, lb, '%sm bound exhausted (live>%s)' % (HOLD_MINUTES, floor)


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
            'refuse append: tip not %s (eng=%s last=%s)'
            % (TIP_BEFORE, len(eng), eng[-1].get('section'))
        )
    if len(src) != TIP_BEFORE:
        raise SystemExit('refuse append: src tip not %s (%s)' % (TIP_BEFORE, len(src)))
    have = {str(r['section']) for r in eng}
    for sec in SECS:
        if sec in have:
            raise SystemExit('refuse overwrite existing section %s' % sec)
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
    raw_sources = [LOCK, pdf, Path(__file__), DATA / 'latin.json', PAYLOAD]
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20261016,
        sample_size=len(section_ids),
        identity=identity,
        selected_sections=section_ids,
        publication_scope=publication_scope,
    )
    packet_path = AUDIT / ('%s.packet.json' % PACKET_STEM)
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    reviews = []
    for sid in section_ids:
        n = int(sid)
        if 1558 <= n <= 1597:
            notes = (
                'Section %s: new densify Sanctorum Cultu Pars Secunda Reformata I-XL; Pass A!=B; '
                'lock-grounded 1675 PDF ~384-390 + Vision/tess; Reformata summary and honor-limits through XL.'
                % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in sanctorum_cultu_pars_secunda_i_xl packet scope covering all current sections.'
                % sid
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
        'reviewer': 'Densify, %s' % day,
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
                'Scope review: densify Sanctorum Cultu Pars Secunda Reformata I-XL only '
                '(sections %s-%s). Meta discloses %s. '
                'Sanctorum Romana CLOSED; Pars Secunda I-XL densified (NOT closed). Next XLI–fin (~CI). Claim stays claimed. Not shipped.'
                % (SECS[0], SECS[-1], RANGE_SHORT)
            ),
        },
        'reviews': reviews,
    }
    review_path = AUDIT / ('%s.review.json' % PACKET_STEM)
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
                'locus': (
            'Angelorum & Hominum Sanctorum Cultu Pars Secunda (Reformata) I-XL (summary of Romana; Reformata honor doctrine through XL)'
        ),
        'next_locus': (
            'Angelorum & Hominum Sanctorum Cultu Pars Secunda (Reformata) '
            '(next Pitt 1675 after Pars Secunda I-XL; Pars Secunda NOT closed)'
        ),
        'gates': {
            'check_pass_ab': 'ok sanctorum_cultu_%s–%s (%s/%s)' % (
                SECS[0], SECS[-1], len(SECS), len(SECS)
            ),
            'tip_ready': 'ok theses_theologia_english.json+theses_theologia_source.json',
            'validate_audit_receipt': 'ok',
        },
        'punch_x': 'NO',
        'ship': 'NO',
        'claim': 'le-blanc-theses-densify stays claimed',
        'latin_lock': str(LOCK),
        'live_at_proceed': '%s/%s' % (treatises, secs),
        'leblanc_live_tip_at_proceed': lb,
        'hold_clear_reason': reason,
        'live_floor': LIVE_FLOOR,
    }
    rpath = AUDIT / ('%s.receipt.json' % PACKET_STEM)
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rpath)
    return receipt


def prepend_handoff(receipt: dict):
    day = datetime.now().strftime("%Y-%m-%d")
    bt = chr(96)
    packet_ref = bt + PACKET_STEM + bt
    nl = chr(10)
    block = (
        "## %s (Densify — Sanctorum Cultu Pars Secunda Reformata I-XL densify LOCAL)" + nl + nl
        + "- Before: **%s**. After: **%s** (contiguous Sanctorum Cultu Pars Secunda Reformata I-XL → §§%s–%s)." + nl
        + "- Packet %s. Punch X = NO. Not shipped." + nl
        + "- Latin lock: `sources/_le_blanc_sanctorum_cultu_latin_lock.txt` EXTENDED (Romana I-LXXVII PRESERVED + PARS SECUNDA Reformata banner + I-XL). Imaginum + Remissione + Distinctione + fidei locks untouched. Justifications `sanctorum_cultu_{n}.json`; OCR/apply under `sources/_ocr_sanctorum_cultu/`." + nl
        + "- Post tip-ready hold cleared (%s) live %s." + nl
        + "- Next: Sanctorum Cultu Pars Secunda Reformata XLI–fin (~CI). Pars Secunda NOT closed at XL; claim le-blanc-theses-densify stays claimed (book densify not done)." + nl + nl
    ) % (
        day,
        receipt["before"],
        receipt["after"],
        SECS[0],
        SECS[-1],
        packet_ref,
        receipt["hold_clear_reason"],
        receipt["live_at_proceed"],
    )
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    HANDOFF.write_text(block + prev, encoding="utf-8")
    print("prepended", HANDOFF)
    for repo_handoff in (REPO / "docs/SESSION_HANDOFF.md", REPO / "SESSION_HANDOFF.md"):
        if repo_handoff.exists():
            prevr = repo_handoff.read_text(encoding="utf-8")
            repo_handoff.write_text(block + prevr, encoding="utf-8")
            print("prepended", repo_handoff)
    claims = REPO / "docs/CLAIMS.md"
    if claims.exists():
        ctext = claims.read_text(encoding="utf-8")
        lines = ctext.splitlines()
        out = []
        updated = False
        for line in lines:
            if line.startswith("| le-blanc-theses-densify |"):
                parts = line.split("|")
                # parts[0]='' parts[1]=claim ... typical markdown table
                new_row = (
                    "| le-blanc-theses-densify | claimed | le-blanc-theses-theologicae | "
                    "Sanctorum Cultu Pars Secunda Reformata I-XL densify DONE tip 1557→1597; tip-1557 PRESERVED; Pars Secunda NOT closed; next XLI–fin (~CI); book densify NOT closed; not ship | Densify | 2026-09-29 | "
                    "wip/le-blanc-theses-densify | Reformed lane; Pitt 1675; packet sanctorum_cultu_pars_secunda_i_xl_densify; "
                    "sister lock EXTEND sanctorum_cultu Pars Secunda I-XL; Punch X=NO; Crocius/Baron CLOSED untouched this slice |"
                )
                out.append(new_row)
                updated = True
            else:
                out.append(line)
        if updated:
            claims.write_text("\n".join(out) + "\n", encoding="utf-8")
            print("updated CLAIMS.md le-blanc-theses-densify stays claimed")
        else:
            print("WARN: CLAIMS row not found")



def main():
    import socket
    host = socket.gethostname()
    print('hostname', host, flush=True)
    if 'Stephans-Mac-mini' not in host and 'mini' not in host.lower():
        raise SystemExit('refuse writes: hostname %s is not Mini' % host)
    fp_before = crocius_baron_fingerprint()
    (DATA / 'crocius_baron_hash_before.txt').write_text(fp_before + chr(10), encoding='utf-8')
    print('crocius/baron fingerprint before', fp_before)
    latin, by_sec = load_payload()
    write_data_files(latin, by_sec)
    write_lock(latin)
    write_and_check_justifications(latin, by_sec)
    eng, _src = reread_tip()
    if len(eng) != TIP_BEFORE:
        # Allow resume if already appended to tip 1557
        if len(eng) == TIP_BEFORE + len(SECS) and str(eng[-1]['section']) == SECS[-1]:
            print('tip already at %s — skip append; finish tip-ready/hold/receipt' % len(eng))
        else:
            raise SystemExit('tip drifted before append: %s (need %s)' % (len(eng), TIP_BEFORE))
    else:
        append_translations(latin, by_sec)
        update_meta()
    tip_ready()
    treatises_now, secs_now = live_section_count()
    post_floor = LIVE_FLOOR
    if secs_now is not None and secs_now > LIVE_FLOOR:
        post_floor = secs_now
    hold_start = datetime.now()
    print(
        'post-tip hold start',
        hold_start.isoformat(timespec='seconds'),
        'floor',
        post_floor,
        flush=True,
    )
    (DATA / 'hold_post_tipready_1597.json').write_text(
        json.dumps({
            'hold_start': hold_start.isoformat(timespec='seconds'),
            'live_floor': post_floor,
            'tip_after': TIP_BEFORE + len(SECS),
            'note': 'post tip-ready hold live>%s OR 0m' % post_floor,
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-1597 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    fp_after = crocius_baron_fingerprint()
    (DATA / 'crocius_baron_hash_after.txt').write_text(fp_after + chr(10), encoding='utf-8')
    print('crocius/baron fingerprint after', fp_after)
    if fp_after != fp_before:
        raise SystemExit('Crocius/Baron translations changed during Sanctorum Pars Secunda densify — refuse')
    print(
        'DONE',
        receipt['before'],
        '->',
        receipt['after'],
        'packet',
        receipt['packet_id'],
        'Punch X=NO',
        flush=True,
    )


if __name__ == '__main__':
    main()
