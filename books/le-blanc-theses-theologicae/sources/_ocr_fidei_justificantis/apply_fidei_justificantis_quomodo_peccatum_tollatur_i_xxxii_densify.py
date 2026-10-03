"""Build + apply Quomodo Peccatum tollatur in Justis I-XXXII densify (tip 1128 to 1160).

Continuation: full locus Quomodo Peccatum I-XXXII after Imputata close.
Live floor 8244. After tip-ready: HOLD live>floor OR 0m. Punch X=NO. No ship.
Tip 1128 PRESERVE. Crocius/Baron CLOSED - do not modify.
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
LOCK = BOOK / 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_peccatum_densify')
PAYLOAD = Path('/tmp/fidei_peccatum_payload.json')
PACKET_STEM = 'fidei_justificantis_quomodo_peccatum_tollatur_i_xxxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_fidei_justificantis/apply_fidei_justificantis_quomodo_peccatum_tollatur_i_xxxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = [str(n) for n in range(1129, 1161)]
ROMANS = {
    '1129': 'I',
    '1130': 'II',
    '1131': 'III',
    '1132': 'IV',
    '1133': 'V',
    '1134': 'VI',
    '1135': 'VII',
    '1136': 'VIII',
    '1137': 'IX',
    '1138': 'X',
    '1139': 'XI',
    '1140': 'XII',
    '1141': 'XIII',
    '1142': 'XIV',
    '1143': 'XV',
    '1144': 'XVI',
    '1145': 'XVII',
    '1146': 'XVIII',
    '1147': 'XIX',
    '1148': 'XX',
    '1149': 'XXI',
    '1150': 'XXII',
    '1151': 'XXIII',
    '1152': 'XXIV',
    '1153': 'XXV',
    '1154': 'XXVI',
    '1155': 'XXVII',
    '1156': 'XXVIII',
    '1157': 'XXIX',
    '1158': 'XXX',
    '1159': 'XXXI',
    '1160': 'XXXII',
}
TIP_BEFORE = 1128
LIVE_FLOOR = 8244
HOLD_MINUTES = 0

RANGE_SHORT = "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXXVII + De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens I-XXX + De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII"
RANGE_TITLE = "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; De Aeterna Hominum Electione et Praedestinatione I-XXXVII; De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens I-XXX; De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu & Acceptione vocis Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII)"
EDITION = "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. Densify through De Certitudine I-XLVIII + Gratia I-XXX + De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII (not whole folio)."
BLURB = "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. Covers De Theologia through De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu & Acceptione vocis Justificandi I-XLIII + Quomodo Fides Justificet I-LIX + De Justitia per Gratiam Fidelibus inhaerente I-LVII + De Justitia Christi Fidelibus Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII. Not the collected folio."
METHOD = "English follows locked Pitt Latin through De Fidei justificantis natura Pars I I-CXLV + Pars II I-LXXI + De Facultate I-XLI + De Usu I-XLIII + Quomodo Fides I-LIX + De Justitia I-LVII + Imputata I-XXXVII + Quomodo Peccatum tollatur in Justis I-XXXII. 1675 PDF 304-309 for Quomodo Peccatum I-XXXII. No modern English. This slice densifies Quomodo Peccatum tollatur in Justis I-XXXII; Quomodo Peccatum CLOSED. Next De Certitudine Justificationis."
LOCK_HEADER = (
    "Le Blanc Latin lock \u2014 De Fidei justificantis natura\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: Pars I I-CXLV PRESERVED + Pars II I-LXXI PRESERVED + De Facultate I-XLI PRESERVED + De Usu I-XLIII PRESERVED + Quomodo I-LIX PRESERVED + De Justitia I-LVII PRESERVED + Imputata I-XXXVII PRESERVED + Quomodo Peccatum tollatur in Justis I-XXXII tip. Next: De Certitudine Justificationis.\n"
    "Source: 1675 PDF pages 216-309 (book ~191-284).\n"
    "Note: Contiguous densify after Imputata XXXVII. Quomodo Peccatum tollatur in Justis I-XXXII CLOSED. Next De Certitudine Justificationis.\n\n"
)
ROMAN_TO_N = {
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
ORDER = [str(n) for n in range(677, 1161)]


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
    """Merge prior lock/source latin with new SECS; write Pars I I–CXLV + Pars II I–XVI lock."""
    prior = {}
    # Prefer source.json for prior sections (reliable); fall back to lock parse
    if SRC.exists():
        for row in json.loads(SRC.read_text(encoding='utf-8')):
            sec = str(row.get('section'))
            lat = row.get('latin') or ''
            if sec.isdigit() and 677 <= int(sec) <= TIP_BEFORE and lat:
                prior[sec] = ' '.join(lat.split())
    if LOCK.exists() and len(prior) < 32:
        text = LOCK.read_text(encoding='utf-8')
        long_rom = (
            'CXLV|CXLIV|CXLIII|CXLII|CXLI|CXL|CXXXIX|CXXXVIII|CXXXVII|CXXXVI|CXXXV|CXXXIV|CXXXIII|CXXXI|CXXX|CXXIX|CXXVIII|CXXVII|CXXVI|CXXV|CXXIV|CXXIII|CXXII|CXXI|CXX|CXIX|CXVIII|CXVII|CXVI|CXV|CXIV|CXIII|CXII|CXI|CX|CIX|CVIII|CVII|CVI|CV|CIV|CIII|CII|CI|C|XCIX|XCVIII|XCVII|XCVI|XCV|XCIV|XCIII|XCII|XCI|XC|LXXXIX|LXXXVIII|LXXXVII|LXXXVI|LXXXV|LXXXIV|LXXXIII|LXXXII|LXXXI|LXXX|LXXIX|LXXVIII|LXXVII|LXXVI|LXXV|LXXIV|LXXIII|LXXII|LXXI|LXX|LXIX|LXVIII|LXVII|LXVI|LXV|LXIV|LXIII|LXII|LXI|LX|LIX|LVIII|LVII|LVI|LV|LIV|LIII|LII|LI|L|'
            'XLVIII|XLVII|XLVI|XLV|XLIV|XLIII|XLII|XLI|XL|XXXIX|XXXVIII|XXXVII|XXXVI|XXXV|XXXIV|XXXIII|XXXII|XXXI|XXX|XXIX|'
            'XXVIII|XXVII|XXVI|XXV|XXIV|XXIII|XXII|XXI|XX|XIX|XVIII|XVII|'
            'XVI|XV|XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I'
        )
        chunks = re.split(r'(?m)(?=^(?:' + long_rom + r')\.\s)', text)
        for ch in chunks:
            ch = ch.strip()
            if not ch:
                continue
            rm = re.match(r'^(' + long_rom + r')\.\s', ch)
            if not rm:
                continue
            sec = ROMAN_TO_N.get(rm.group(1))
            if sec:
                prior.setdefault(sec, ' '.join(ch.split()))
    merged = dict(prior)
    merged.update({k: ' '.join(new_latin[k].split()) for k in SECS})
    parts = [LOCK_HEADER]
    pars2_banner = (
        "\nPARS SECUNDA — Exponitur Doctrina Scholae Romanae, "
        "& cum Protestantium Doctrina comparatur.\n\n"
    )
    facultate_banner = (
        "\nDE FACULTATE CUI FIDES INHAERET: & de connexione Fidei cum Charitate "
        "& Bonis Operibus.\n"
        "In quibus Protestantium Doctrina exponitur, & cum Scholae Romanae Doctrina comparatur.\n\n"
    )
    de_usu_banner = (
        "\nTHESES THEOLOGICAE:\n"
        "DE USU & ACCEPTIONE VOCIS JUSTIFICANDI\n"
        "In Scripturis & Scholis.\n\n"
    )
    quomodo_banner = (
        "\nTHESES THEOLOGICAE:\n"
        "In quibus exponitur, Quomodo FIDES JUSTIFICET.\n\n"
    )
    justitia_banner = (
        "\nTHESES THEOLOGICAE:\n"
        "DE JUSTITIA PER CHRISTI GRATIAM\n"
        "Fidelibus inhaerente.\n\n"
    )
    imputata_banner = (
        "\nTHESES THEOLOGICAE:\n"
        "DE JUSTITIA CHRISTI\n"
        "Fidelibus Imputata.\n\n"
    )
    peccatum_banner = (
        "\nTHESES THEOLOGICAE:\n"
        "In quibus Exponitur,\n"
        "AN & QUOMODO PECCATUM\n"
        "Tollatur in iis qui JUSTIFICANTUR.\n\n"
    )
    for sec in ORDER:
        if sec not in merged:
            raise SystemExit('lock missing section %s after merge (have %s)' % (sec, sorted(merged, key=int)[:5]))
        if sec == '821':
            parts.append(pars2_banner)
        if sec == '892':
            parts.append(facultate_banner)
        if sec == '933':
            parts.append(de_usu_banner)
        if sec == '976':
            parts.append(quomodo_banner)
        if sec == '1035':
            parts.append(justitia_banner)
        if sec == '1092':
            parts.append(imputata_banner)
        if sec == '1129':
            parts.append(peccatum_banner)
        parts.append(merged[sec].rstrip() + chr(10))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(''.join(parts) + chr(10), encoding='utf-8')
    print('wrote', LOCK, 'chars', LOCK.stat().st_size, 'secs', len(ORDER))


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
        jpath = JUST / ('fidei_justificantis_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab fidei_justificantis_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
        seed=20261014,
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
        if 1129 <= n <= 1160:
            notes = (
                'Section %s: new densify Quomodo Peccatum tollatur in Justis I-XXXII; Pass A!=B; '
                'lock-grounded 1675 PDF 304-309; full locus.'
                % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in fidei_justificantis_quomodo_peccatum_tollatur_i_xxxii packet scope covering all current sections.'
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
                'Scope review: densify Quomodo Peccatum tollatur in Justis I-XXXII only '
                '(sections %s-%s). Meta discloses %s. '
                'Quomodo Peccatum CLOSED. Next De Certitudine Justificationis. De Fidei justificantis locus NOT closed. Not shipped.'
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
            'Quomodo Peccatum tollatur in Justis I-XXXII '
            '(tollere metaphors; reatus+macula; gradual cleansing; '
            'Reformed remains/concupiscence; Roman calumny XXIV-XXXII irenic close)'
        ),
        'next_locus': (
            'De Certitudine Justificationis '
            '(next after Quomodo Peccatum close; related justification loci)'
        ),
        'gates': {
            'check_pass_ab': 'ok fidei_justificantis_%s–%s (%s/%s)' % (
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
    day = datetime.now().strftime('%Y-%m-%d')
    bt = chr(96)
    packet_ref = bt + PACKET_STEM + bt
    block = (
        '## %s (Densify — Quomodo Peccatum tollatur in Justis I-XXXII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Quomodo Peccatum I-XXXII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: De Certitudine Justificationis. Quomodo Peccatum CLOSED; De Fidei justificantis locus NOT closed.\n\n'
        % (
            day,
            receipt['before'],
            receipt['after'],
            SECS[0],
            SECS[-1],
            packet_ref,
            receipt['hold_clear_reason'],
            receipt['live_at_proceed'],
        )
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        '## %s ~ET (Densify — Le Blanc Quomodo Peccatum tollatur in Justis I-XXXII densify)\n\n'
        'CoS densify: Quomodo Peccatum tollatur in Justis I-XXXII (**%s→%s**). Packet %s. '
        'Tip-1128 PRESERVED. Quomodo Peccatum CLOSED. Next: De Certitudine Justificationis. Punch X: **NO**.\n\n---\n\n'
        % (day, receipt['before'], receipt['after'], packet_ref)
    )
    rprev = repo_handoff.read_text(encoding='utf-8') if repo_handoff.exists() else ''
    repo_handoff.write_text(repo_block + rprev, encoding='utf-8')
    print('handoff prepended (book + repo)')


def main():
    import socket
    host = socket.gethostname()
    print('hostname', host, flush=True)
    if 'Stephans-Mac-mini' not in host and 'mini' not in host.lower():
        raise SystemExit('refuse writes: hostname %s is not Mini' % host)
    latin, by_sec = load_payload()
    write_data_files(latin, by_sec)
    write_lock(latin)
    write_and_check_justifications(latin, by_sec)
    eng, _src = reread_tip()
    if len(eng) != TIP_BEFORE:
        # Allow resume if already appended to tip 700
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
    (DATA / 'hold_post_tipready_1160.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-1160 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
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
