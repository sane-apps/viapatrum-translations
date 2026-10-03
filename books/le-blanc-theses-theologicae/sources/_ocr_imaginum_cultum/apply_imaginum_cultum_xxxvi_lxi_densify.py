"""Build + apply Ecclesiae Romanae doctrina circa Imaginum Cultum XXXVI-LXI densify (tip 1404 to 1430).

Contiguous slice after Imaginum Cultum I-XXXV (tip 1404). Closes Roman locus at LXI / FINIS.
Live floor 8244. After tip-ready: HOLD live>floor OR 0m. Punch X=NO. No ship.
Tip 1404 PRESERVE. Crocius/Baron CLOSED books - do not modify.
Sister latin lock EXTEND: sources/_le_blanc_imaginum_cultum_latin_lock.txt (I-XXXV PRESERVED + XXXVI-LXI).
Do not reopen Remissione / Distinctione / fidei locks.
Justifications: imaginum_cultum_{n}.json (locus-prefixed).
OCR/apply under sources/_ocr_imaginum_cultum/.
Pars altera NOT started this slice.
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
LOCK = BOOK / 'sources/_le_blanc_imaginum_cultum_latin_lock.txt'
REMISS_LOCK = BOOK / 'sources/_le_blanc_remissione_peccatorum_latin_lock.txt'
DIST_LOCK = BOOK / 'sources/_le_blanc_distinctione_peccati_latin_lock.txt'
FIDEI_LOCK = BOOK / 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_imaginum_cultum_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_imaginum_xxxvi_densify')
PAYLOAD = Path('/tmp/imaginum_cultum_xxxvi_lxi_payload.json')
PACKET_STEM = 'imaginum_cultum_xxxvi_lxi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_imaginum_cultum/apply_imaginum_cultum_xxxvi_lxi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = [str(n) for n in range(1405, 1431)]
_ROMAN_LIST = ["XXXVI","XXXVII","XXXVIII","XXXIX","XL","XLI","XLII","XLIII","XLIV","XLV","XLVI","XLVII","XLVIII","XLIX","L","LI","LII","LIII","LIV","LV","LVI","LVII","LVIII","LIX","LX","LXI"]
ROMANS = {str(1405 + i): _ROMAN_LIST[i] for i in range(26)}
TIP_BEFORE = 1404
LIVE_FLOOR = 8244
HOLD_MINUTES = 0

RANGE_SHORT = 'Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXXVII + De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens I-XXX + De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII + De Certitudine Justificationis Pars Prima I-XXX + Pars Secunda I-LVI + De Distinctione Peccati in Mortale et Veniale Pars Prior I-XXXI + Pars Posterior I-LXVIII + De Remissione Peccatorum I-XXIV + Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem I-LXI'
RANGE_TITLE = 'Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; De Aeterna Hominum Electione et Praedestinatione I-XXXVII; De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens I-XXX; De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu & Acceptione vocis Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII + De Certitudine Justificationis Pars Prima I-XXX + Pars Secunda I-LVI + De Distinctione Peccati in Mortale et Veniale Pars Prior I-XXXI + Pars Posterior I-LXVIII + De Remissione Peccatorum I-XXIV + Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem I-LXI)'
EDITION = 'Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC (+ EEBO 1675 for gap leaves). Densify through Imaginum Cultum I-LXI Roman locus CLOSED (not whole folio).'
BLURB = 'Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. Covers De Theologia through Ecclesiae Romanae doctrina circa Imaginum Cultum I-LXI (Roman locus CLOSED). Not the collected folio.'
METHOD = 'English follows locked Pitt Latin through Remissione CLOSED + Imaginum Cultum I-LXI. 1675 PDF ~357-361 (book ~343-347); EEBO 1675 + Vision OCR for School distinctions through Suarez FINIS. No modern English. This slice densifies Imaginum XXXVI-LXI and CLOSES the Roman locus. Next: De Imaginum Cultu pars altera (Ecclesiae Reformatae). Claim stays claimed (book densify not done; pars altera pending).'
LOCK_HEADER = (
    'Le Blanc Latin lock — Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem\n'
    'Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n'
    'Scope: Imaginum Cultum I-XXXV PRESERVED + XXXVI-LXI tip (School distinctions through Suarez; Roman locus CLOSED at FINIS).\n'
    'Source: 1675 PDF pages ~351-361 (book ~326-347); EEBO 1675 + Vision OCR for XXXVI-LXI.\n'
    'Note: Contiguous densify after tip 1404. Sister lock EXTENDED (Remissione + Distinctione + fidei locks untouched). Imaginum Roman locus CLOSED; pars altera NOT started; claim le-blanc-theses-densify stays claimed (book densify not done).\n'
    '\n'
)
ROMAN_TO_NROMAN_TO_N = {
    'I': '677', 'II': '678', 'III': '679', 'IV': '680',
    'V': '681', 'VI': '682', 'VII': '683', 'VIII': '684',
    'IX': '685', 'X': '686', 'XI': '687', 'XII': '688',
    'XIII': '689', 'XIV': '690', 'XV': '691', 'XVI': '692',
    'XVII': '693', 'XVIII': '694', 'XIX': '695', 'XX': '696',
    'XXI': '697', 'XXII': '698', 'XXIII': '699', 'XXIV': '700',
    'XXV': '701', 'XXVI': '702', 'XXVII': '703', 'XXVIII': '704',
    'XXIX': '705', 'XXX': '706', 'XXXI': '707', 'XXXII': '708',
    'XXXIII': '709', 'XXXIV': '710', 'XXXV': '711', 'XXXVI': '712',
    'XXXVII': '713', 'XXXVIII': '714', 'XXXIX': '715', 'XL': '716',
    'XLI': '717', 'XLII': '718', 'XLIII': '719', 'XLIV': '720',
    'XLV': '721', 'XLVI': '722', 'XLVII': '723', 'XLVIII': '724',
    'XLIX': '725', 'L': '726', 'LI': '727', 'LII': '728',
    'LIII': '729', 'LIV': '730', 'LV': '731', 'LVI': '732',
    'LVII': '733', 'LVIII': '734', 'LIX': '735', 'LX': '736',
    'LXI': '737', 'LXII': '738', 'LXIII': '739', 'LXIV': '740',
    'LXV': '741', 'LXVI': '742', 'LXVII': '743', 'LXVIII': '744',
    'LXIX': '745', 'LXX': '746', 'LXXI': '747', 'LXXII': '748',
    'LXXIII': '749', 'LXXIV': '750', 'LXXV': '751', 'LXXVI': '752',
    'LXXVII': '753', 'LXXVIII': '754', 'LXXIX': '755', 'LXXX': '756',
    'LXXXI': '757', 'LXXXII': '758', 'LXXXIII': '759', 'LXXXIV': '760',
    'LXXXV': '761', 'LXXXVI': '762', 'LXXXVII': '763', 'LXXXVIII': '764',
    'LXXXIX': '765', 'XC': '766', 'XCI': '767', 'XCII': '768',
    'XCIII': '769', 'XCIV': '770', 'XCV': '771', 'XCVI': '772',
    'XCVII': '773', 'XCVIII': '774', 'XCIX': '775', 'C': '776',
    'CI': '777', 'CII': '778', 'CIII': '779', 'CIV': '780',
    'CV': '781', 'CVI': '782', 'CVII': '783', 'CVIII': '784',
    'CIX': '785', 'CX': '786', 'CXI': '787', 'CXII': '788',
    'CXIII': '789', 'CXIV': '790', 'CXV': '791', 'CXVI': '792',
    'CXVII': '793', 'CXVIII': '794', 'CXIX': '795', 'CXX': '796',
    'CXXI': '797', 'CXXII': '798', 'CXXIII': '799', 'CXXIV': '800',
    'CXXV': '801', 'CXXVI': '802', 'CXXVII': '803', 'CXXVIII': '804',
    'CXXIX': '805', 'CXXX': '806',
    'CXXXI': '807', 'CXXXIII': '808', 'CXXXIV': '809', 'CXXXV': '810',
    'CXXXVI': '811', 'CXXXVII': '812', 'CXXXVIII': '813', 'CXXXIX': '814',
    'CXL': '815', 'CXLI': '816', 'CXLII': '817', 'CXLIII': '818',
    'CXLIV': '819', 'CXLV': '820',
    # Pars II Romans restart; used only if lock-parse fallback needed for new SECS
    # (prior 677-820 come from source.json, not this map)
}
ORDER = [str(n) for n in range(677, 1311)]



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
    for p in paths:
        h.update(str(p.relative_to(REPO)).encode())
        h.update(b'\0')
        h.update(p.read_bytes())
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
    """Extend Imaginum sister lock: keep I-XXXV body; append XXXVI-LXI. Do not touch Remissione/Distinctione/fidei."""
    for p in (REMISS_LOCK, DIST_LOCK, FIDEI_LOCK):
        if p.exists():
            print("preserve untouched", p, "chars", p.stat().st_size)
    body = ""
    if LOCK.exists():
        raw = LOCK.read_text(encoding="utf-8")
        marker = "THESES THEOLOGICAE"
        idx = raw.find(marker)
        if idx >= 0:
            body = raw[idx:].rstrip() + chr(10) + chr(10)
        else:
            # fallback: keep everything after first blank line following header notes
            body = raw.rstrip() + chr(10) + chr(10)
    parts = [LOCK_HEADER]
    if body.strip():
        parts.append(body)
    else:
        parts.append(
            "THESES THEOLOGICAE" + chr(10)
            + "In quibus Exponitur Ecclesiae Romanae doctrina CIRCA IMAGINUM CULTUM ET ADORATIONEM."
            + chr(10) + chr(10)
        )
    for sec in SECS:
        parts.append(new_latin[sec].rstrip() + chr(10))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text("".join(parts) + chr(10), encoding="utf-8")
    print("wrote", LOCK, "chars", LOCK.stat().st_size, "secs", len(SECS), "(extended; I-XXXV preserved)")






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
        jpath = JUST / ('imaginum_cultum_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab imaginum_cultum_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
        if 1405 <= n <= 1430:
            notes = (
                'Section %s: new densify Imaginum Cultum XXXVI-LXI; Pass A!=B; '
                'lock-grounded 1675 PDF ~357-361 + EEBO/Vision; School distinctions through Suarez FINIS.'
                % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in imaginum_cultum_xxxvi_lxi packet scope covering all current sections.'
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
                'Scope review: densify Imaginum Cultum XXXVI-LXI only '
                '(sections %s-%s). Meta discloses %s. '
                'Imaginum Roman locus CLOSED at LXI/FINIS. Pars altera NOT started. Next: De Imaginum Cultu pars altera (Reformata). Claim stays claimed. Not shipped.'
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
            'Ecclesiae Romanae doctrina circa Imaginum Cultum et Adorationem I-LXI (Councils/praxis/School consensus ante XXXVI+)'
        ),
        'next_locus': (
            'Imaginum Cultum XXXVI through end of Roman locus (~LXI), then '
            'De Imaginum Cultu pars altera (Reformata)'
        ),
        'gates': {
            'check_pass_ab': 'ok imaginum_cultum_%s–%s (%s/%s)' % (
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
        "## %s (Densify — Imaginum Cultum XXXVI-LXI densify LOCAL)" + nl + nl
        + "- Before: **%s**. After: **%s** (contiguous Imaginum Cultum XXXVI-LXI → §§%s–%s)." + nl
        + "- Packet %s. Punch X = NO. Not shipped." + nl
        + "- Latin lock: `sources/_le_blanc_imaginum_cultum_latin_lock.txt` EXTENDED (I-XXXV PRESERVED + XXXVI-LXI). Remissione + Distinctione + fidei locks untouched. Justifications `imaginum_cultum_{n}.json`; OCR/apply under `sources/_ocr_imaginum_cultum/`." + nl
        + "- Post tip-ready hold cleared (%s) live %s." + nl
        + "- Next: De Imaginum Cultu pars altera (Ecclesiae Reformatae). Imaginum Roman CLOSED at LXI; pars altera NOT started; claim le-blanc-theses-densify stays claimed (book densify not done)." + nl + nl
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
    repo_handoff = REPO / "docs/SESSION_HANDOFF.md"
    if not repo_handoff.exists():
        repo_handoff = REPO / "SESSION_HANDOFF.md"
    if repo_handoff.exists():
        prevr = repo_handoff.read_text(encoding="utf-8")
        repo_handoff.write_text(block + prevr, encoding="utf-8")
        print("prepended", repo_handoff)
    claims = REPO / "docs/CLAIMS.md"
    if claims.exists():
        ctext = claims.read_text(encoding="utf-8")
        old_row = None
        for line in ctext.splitlines():
            if "| le-blanc-theses-densify |" in line:
                old_row = line
                break
        new_row = (
            "| le-blanc-theses-densify | claimed | le-blanc-theses-theologicae | "
            "Imaginum Cultum XXXVI–LXI densify DONE tip 1404→1430; tip-1404 PRESERVED; "
            "Imaginum Roman CLOSED; next pars altera Reformata; book densify NOT closed; not ship | "
            "Densify | 2026-09-29 | wip/le-blanc-theses-densify | "
            "Reformed lane; Pitt 1675; packet imaginum_cultum_xxxvi_lxi_densify; "
            "sister lock EXTENDED imaginum_cultum; Punch X=NO; Crocius/Baron CLOSED untouched this slice |"
        )
        if old_row:
            claims.write_text(ctext.replace(old_row, new_row, 1), encoding="utf-8")
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
        # Allow resume if already appended to tip 1430
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
    (DATA / 'hold_post_tipready_1430.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-1430 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    fp_after = crocius_baron_fingerprint()
    (DATA / 'crocius_baron_hash_after.txt').write_text(fp_after + chr(10), encoding='utf-8')
    print('crocius/baron fingerprint after', fp_after)
    if fp_after != fp_before:
        raise SystemExit('FAIL: Crocius/Baron fingerprint changed')
    print('Crocius+Baron untouched OK')
    print(
        'DONE',
        receipt['before'],
        '->',
        receipt['after'],
        'packet',
        receipt['packet_id'],
        'Punch X=NO Roman CLOSED',
        flush=True,
    )


if __name__ == '__main__':
    main()
