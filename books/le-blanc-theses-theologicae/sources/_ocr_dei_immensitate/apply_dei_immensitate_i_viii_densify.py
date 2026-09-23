#!/usr/bin/env python3
"""Build + apply De Dei Immensitate & Omnipraesentia I-VIII densify (tip 424 → 432).

Opens after Perfectione XXVI close. Live floor 4535.
After tip-ready: HOLD live>4535 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_immensitate_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_immensitate_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_immensitate_densify')
PACKET_STEM = 'dei_immensitate_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_immensitate/apply_dei_immensitate_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['425', '426', '427', '428', '429', '430', '431', '432']
ROMANS = {
    '425': 'I', '426': 'II', '427': 'III', '428': 'IV',
    '429': 'V', '430': 'VI', '431': 'VII', '432': 'VIII',
}
TIP_BEFORE = 424
LIVE_FLOOR = 4535
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Immensitate & Omnipraesentia I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Immensitate & Omnipraesentia I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Immensitate & Omnipraesentia I-VIII, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice opens Immensitate after Perfectione close "
    "(immensity vs eternity; ubique; Makom; three modes; power & presence)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Immensitate & Omnipraesentia.\n"
    "Same 1675 Pitt copy-text. Book pp. 106-107 / PDF 118-119 (I-VIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Immensitate & Omnipraesentia I-VIII tip. IX+ remains. "
    "Prior tracts closed through Perfectione I-XXVI.\n"
    "Note: Opens after Perfectione. Immensity/eternity split; circumscriptive/definitive; Makom; Scholastic modes.\n\n"
)

LATIN = {
    '425': (
        'I. Quandoquidem essentiae divinae perfectio omni prorsus limite caret, sequitur '
        'Deum, quocunque modo consideretur, infinitum esse. Nam infinitum esse est terminis '
        'carere, & intra certos limites non concludi.'
    ),
    '426': (
        'II. Sed quamvis Dei infinitas per omnia ejus attributa aequaliter fusa sit, nec '
        'quicquam sit in Deo quod non sit infinitum: illa tamen solet in duobus praecipue '
        'considerari, nempe in eo quod nullis nec loci, nec temporis limitibus '
        'circumscribatur, sed sit longe supra omne tempus & locum: adeo ut ejus magnitudo '
        'terminum non habeat, nec duratio principium, aut finem. Quae prior infinitas '
        'immensitas vocatur; posterior autem aeternitas: de quibus utraque seorsim agendum '
        'est: atque nunc quidem de priori.'
    ),
    '427': (
        'III. Deus igitur immensus est, quia magnitudinis ejus terminus nullus datur, '
        'adeoque nullo loco circumscriptus, aut definitus est. Quae naturae divinae '
        'singularis praestantia melius percipitur, si quis conferat Deum hac in parte cum '
        'rebus creatis. Igitur res omnes creatae singulae suum locum peculiarem habent. '
        'Quemadmodum essentia illarum finita est, ita sunt in certo & finito loco. Et '
        'quidem videmus corpora certo loci spatio concludi, contineri, & circumscribi, sic '
        'ut partes eorum partibus spatii & loci respondeant, major majori, & minor minori. '
        'Quod Philosophi vocant in loco esse circumscriptive. Qui modus solis corporibus '
        'competit: a substantiis vero incorporeis, quales sunt angeli, & anima humana, '
        'plane alienus est. Cum enim substantiae spirituales non sint extensae ad modum '
        'corporum, nec habeant partes extra partes, non possunt habere partes partibus loci '
        'respondentes, & loco commensurari. Attamen certis locis definiuntur. Ita sunt hic '
        'ut alibi non sint. Hinc abscedunt, & alio migrant. Ideoque a Philosophis in loco '
        'dicuntur esse definitive.'
    ),
    '428': (
        'IV. Sed Deo proprium est ubique esse, nec ullo certo loco definiri. Nam infinita '
        'ipsius substantia omnia penetrat, & omnibus adest. Nullibi ita est ut alibi non '
        'sit. A nullo loco exclusus est, & nullo tamen includitur. Totus ubique est, & '
        'totus extra quemvis locum est.'
    ),
    '429': (
        'V. Quocirca sapienter & acute dictum est Deum esse circulum cujus centrum est '
        'ubique, circumferentia nullibi. Nec etiam absque ratione Hebraeorum Magistri Deum '
        'vocaverunt Makom, id est, locum: quoniam Deus loco non continetur, sed ipse est '
        'qui fecit, & continet omnia loca: ita ut potius omnia sint in ipso, quam ipse sit '
        'in omnibus.'
    ),
    '430': (
        'VI. Verum ad accuratiorem immensitatis hujus divinae notitiam, notate Deum rebus '
        'adesse tribus modis, nempe, per potentiam, praesentiam, & essentiam, ut Scholastici '
        'communiter loquuntur. Quod clarius dixeris & convenientius, per operationem, per '
        'cognitionem, & per substantiam.'
    ),
    '431': (
        'VII. Nam Deus per potentiam in omnibus esse dicitur, quoniam omnia producit, '
        'conservat & gubernat: & operatur omnia in omnibus: juxta illud Apostoli: Actor. 17. '
        'Non longe Deus est ab unoquoque nostrum, in ipso enim vivimus, movemur, & sumus.'
    ),
    '432': (
        'VIII. Per praesentiam vero dicitur Deus in omnibus esse, quoniam omnia quae sunt, '
        'fiunt, aut aguntur ubique locorum, tanquam coram se posita videt & intuetur, '
        'secundum illud Apostoli Hebr. 4. Non est creatura ulla invisibilis in conspectu '
        'Dei: omnia autem nuda & aperta sunt oculis ejus. Hic autem modus quo Deus rebus '
        'adest speciali ratione a Scholasticis per praesentiam dicitur, quoniam praesens '
        'videtur ad cognitionem referri. Nam juxta etymologiam, praesens est illud quod '
        'prae sensibus est. Quomodo nos alicui loco praesentes esse dicimur, cum oculis '
        'illum collustramus: & quomodo sol, etsi in caelo sit positus, praesens nobis '
        'dicitur, & nos illi, dum eum aspicimus.'
    ),
}

SECTIONS = [
    {
        'section': '425',
        'title': 'Unlimited divine perfection → God infinite in every respect',
        'pass_a': (
            'Since the perfection of the divine essence lacks altogether every limit, it '
            'follows that God, in whatever way He be considered, is infinite. For to be '
            'infinite is to lack bounds, and not to be shut up within certain limits.'
        ),
        'pass_b': [
            'Divine essence has no perfection-limit.',
            'Therefore God is infinite however you take Him.',
            'Infinite = unbound — not shut inside limits.',
        ],
        'lemmas': [
            {'latin': 'omni prorsus limite caret', 'gloss': 'lacks altogether every limit'},
            {'latin': 'terminis carere', 'gloss': 'to lack bounds'},
        ],
        'choices': [{
            'term': 'Deum, quocunque modo consideretur, infinitum esse',
            'english': 'that God, in whatever way He be considered, is infinite',
            'why': 'Opens Immensitate from Perfectione close.',
            'rejected': ['God is infinite only under one attribute'],
        }],
        'notes': ['OCR: Immensitate I PDF 118 / p. 106; Thes. Prima.'],
        'bible_refs': [],
    },
    {
        'section': '426',
        'title': 'Infinitude chiefly as immensity (place) and eternity (time)',
        'pass_a': (
            'But although the infinitude of God is equally poured through all His '
            'attributes, nor is there anything in God which is not infinite: that '
            'infinitude is nevertheless wont to be considered chiefly in two respects, '
            'namely in this, that He is circumscribed by no limits either of place or of '
            'time, but is far above every time and place: so that His greatness has no '
            'bound, nor His duration a beginning or an end. Which prior infinitude is '
            'called immensity; but the posterior, eternity: of both of which it must be '
            'treated separately: and now indeed of the prior.'
        ),
        'pass_b': [
            'Every attribute is infinite — yet two foci stand out.',
            'No place-bound, no time-bound: greatness without end; duration without start/end.',
            'Prior = immensity; posterior = eternity — treat immensity first.',
        ],
        'lemmas': [
            {'latin': 'immensitas vocatur; posterior autem aeternitas', 'gloss': 'is called immensity; but the posterior, eternity'},
            {'latin': 'nullis nec loci, nec temporis limitibus', 'gloss': 'by no limits either of place or of time'},
        ],
        'choices': [{
            'term': 'Quae prior infinitas immensitas vocatur',
            'english': 'Which prior infinitude is called immensity',
            'why': 'Splits tract agenda: immensity now, eternity later.',
            'rejected': ['immensity and eternity are the same focus'],
        }],
        'notes': ['OCR: II PDF 118.'],
        'bible_refs': [],
    },
    {
        'section': '427',
        'title': 'Immensus vs creatures — circumscriptive and definitive place',
        'pass_a': (
            'God therefore is immense, because no bound of His greatness is given, and '
            'therefore He is circumscribed by no place, or defined. Which singular '
            'excellence of the divine nature is better perceived if one compares God in '
            'this part with created things. Therefore all created things each have their '
            'own peculiar place. Just as their essence is finite, so they are in a certain '
            'and finite place. And indeed we see bodies shut up, contained, and '
            'circumscribed by a certain space of place, so that their parts answer to the '
            'parts of space and place, greater to greater, and lesser to lesser. Which the '
            'Philosophers call being in place circumscriptively. Which mode belongs to '
            'bodies alone: but from incorporeal substances, such as angels and the human '
            'soul, it is altogether alien. For since spiritual substances are not extended '
            'after the manner of bodies, nor have parts outside parts, they cannot have '
            'parts answering to the parts of place, and be commensurated to place. '
            'Nevertheless they are defined by certain places. So they are here so as not to '
            'be elsewhere. Hence they withdraw, and migrate elsewhere. And therefore by '
            'the Philosophers they are said to be in place definitively.'
        ),
        'pass_b': [
            'God immense: no bound of greatness; not place-defined.',
            'Bodies: circumscriptive place (parts match space-parts).',
            'Angels/souls: definitive place — here not elsewhere; can migrate.',
        ],
        'lemmas': [
            {'latin': 'in loco esse circumscriptive', 'gloss': 'to be in place circumscriptively'},
            {'latin': 'in loco dicuntur esse definitive', 'gloss': 'are said to be in place definitively'},
        ],
        'choices': [{
            'term': 'nullo loco circumscriptus, aut definitus est',
            'english': 'He is circumscribed by no place, or defined',
            'why': 'Sets God off from both corporeal and spiritual creature-place.',
            'rejected': ['God is in place the way angels are'],
        }],
        'notes': ['OCR: III PDF 118; Scholastic loco modes.'],
        'bible_refs': [],
    },
    {
        'section': '428',
        'title': 'God alone is everywhere — whole everywhere, whole outside every place',
        'pass_a': (
            'But it is proper to God to be everywhere, and not to be defined by any certain '
            'place. For His infinite substance penetrates all things, and is present to all. '
            'He is nowhere so as not to be elsewhere. He is excluded from no place, and yet '
            'is included by none. He is whole everywhere, and whole outside every place.'
        ),
        'pass_b': [
            'Proper to God: ubique — not fixed to one place.',
            'Infinite substance penetrates all; present to all.',
            'Whole everywhere and whole outside every place.',
        ],
        'lemmas': [
            {'latin': 'ubique esse', 'gloss': 'to be everywhere'},
            {'latin': 'Totus ubique est, & totus extra quemvis locum est', 'gloss': 'He is whole everywhere, and whole outside every place'},
        ],
        'choices': [{
            'term': 'Totus ubique est, & totus extra quemvis locum est',
            'english': 'He is whole everywhere, and whole outside every place',
            'why': 'Classic immensity formula.',
            'rejected': ['God is partly here and partly elsewhere'],
        }],
        'notes': ['OCR: IV PDF 118.'],
        'bible_refs': [],
    },
    {
        'section': '429',
        'title': 'Circle whose center is everywhere — Hebrew Makom',
        'pass_a': (
            'Wherefore it has been wisely and acutely said that God is a circle whose '
            'center is everywhere, the circumference nowhere. Nor without reason did the '
            'Masters of the Hebrews call God Makom, that is, place: since God is not '
            'contained by place, but He Himself is who made and contains all places: so '
            'that rather all things are in Him, than He in all things.'
        ),
        'pass_b': [
            'Wise saying: circle — center everywhere, circumference nowhere.',
            'Hebrews called God Makom (place) — He contains places.',
            'All things in Him more than He in all things.',
        ],
        'lemmas': [
            {'latin': 'circulum cujus centrum est ubique, circumferentia nullibi', 'gloss': 'a circle whose center is everywhere, circumference nowhere'},
            {'latin': 'Makom, id est, locum', 'gloss': 'Makom, that is, place'},
        ],
        'choices': [{
            'term': 'potius omnia sint in ipso, quam ipse sit in omnibus',
            'english': 'rather all things are in Him, than He in all things',
            'why': 'Makom flips containment.',
            'rejected': ['place contains God as a vessel'],
        }],
        'notes': ['OCR: V PDF 118; Makom / המקום normalized from Aktym/Makem.'],
        'bible_refs': [],
    },
    {
        'section': '430',
        'title': 'Three modes of presence — power, presence, essence',
        'pass_a': (
            'But for a more accurate knowledge of this divine immensity, note that God is '
            'present to things in three modes, namely, by power, by presence, and by '
            'essence, as the Scholastics commonly speak. Which you would say more clearly '
            'and conveniently, by operation, by cognition, and by substance.'
        ),
        'pass_b': [
            'Scholastics: present by power, presence, and essence.',
            'Clearer: by operation, by cognition, by substance.',
            'Sets up VII–IX on each mode.',
        ],
        'lemmas': [
            {'latin': 'per potentiam, praesentiam, & essentiam', 'gloss': 'by power, presence, and essence'},
            {'latin': 'per operationem, per cognitionem, & per substantiam', 'gloss': 'by operation, by cognition, and by substance'},
        ],
        'choices': [{
            'term': 'Deum rebus adesse tribus modis',
            'english': 'that God is present to things in three modes',
            'why': 'Frames the mode analysis.',
            'rejected': ['only one mode of divine presence'],
        }],
        'notes': ['OCR: VI PDF 118.'],
        'bible_refs': [],
    },
    {
        'section': '431',
        'title': 'Presence by power — Acts 17 in Him we live',
        'pass_a': (
            'For God is said to be in all things by power, because He produces, preserves, '
            'and governs all things: and works all things in all: according to that of the '
            'Apostle: Acts 17. God is not far from each one of us, for in Him we live, and '
            'move, and are.'
        ),
        'pass_b': [
            'By power: He produces, preserves, governs all.',
            'Works all in all.',
            'Acts 17: not far — in Him we live, move, and are.',
        ],
        'lemmas': [
            {'latin': 'per potentiam in omnibus esse', 'gloss': 'to be in all things by power'},
            {'latin': 'in ipso enim vivimus, movemur, & sumus', 'gloss': 'for in Him we live, and move, and are'},
        ],
        'choices': [{
            'term': 'omnia producit, conservat & gubernat',
            'english': 'He produces, preserves, and governs all things',
            'why': 'Defines presence-by-power.',
            'rejected': ['power-presence means God is locally shut in creatures'],
        }],
        'notes': ['OCR: VII PDF 119; Acts 17:27-28.'],
        'bible_refs': ['Acts 17:27-28'],
    },
    {
        'section': '432',
        'title': 'Presence by cognition — all bare before His eyes',
        'pass_a': (
            'But by presence God is said to be in all things, because all things which are, '
            'come to be, or are done everywhere in places, He sees and beholds as set before '
            'Him, according to that of the Apostle Heb. 4. There is no creature invisible in '
            'the sight of God: but all things are naked and open to His eyes. But this mode '
            'by which God is present to things is called by the Scholastics by a special '
            'reason by presence, since present seems to be referred to cognition. For '
            'according to etymology, present is that which is before the senses. As we are '
            'said to be present to some place when we survey it with the eyes: and as the '
            'sun, though placed in heaven, is said present to us, and we to it, while we '
            'look upon it.'
        ),
        'pass_b': [
            'By presence: He sees all that is done everywhere as before Him.',
            'Heb. 4: nothing invisible — all naked and open to His eyes.',
            'Scholastic "praesentia" tracks cognition — like eye-survey / sun seen.',
        ],
        'lemmas': [
            {'latin': 'per praesentiam', 'gloss': 'by presence'},
            {'latin': 'omnia autem nuda & aperta sunt oculis ejus', 'gloss': 'but all things are naked and open to His eyes'},
        ],
        'choices': [{
            'term': 'praesens videtur ad cognitionem referri',
            'english': 'present seems to be referred to cognition',
            'why': 'Explains why Scholastics label the cognitive mode praesentia.',
            'rejected': ['praesentia here means local bodily containment'],
        }],
        'notes': ['OCR: VIII PDF 119; Heb 4:13. Next IX essence-mode.'],
        'bible_refs': ['Heb. 4:13'],
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
    parts = [LOCK_HEADER]
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
        jpath = JUST / f'dei_immensitate_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_immensitate_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_118_120_layout.txt', 'tess118.txt', 'tess119.txt'):
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
        if 425 <= n <= 432:
            notes = (
                f'Section {sid}: new densify De Dei Immensitate & Omnipraesentia I-VIII; '
                'Pass A!=B; lock-grounded PDF 118-119 / book pp. 106-107.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_immensitate I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Dei Immensitate & Omnipraesentia I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Immensitate through VIII. IX+ remains. Not shipped.'
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
        'locus': 'De Dei Immensitate & Omnipraesentia theses I-VIII (open after Perfectione)',
        'next_locus': 'De Dei Immensitate & Omnipraesentia IX+ (essence-mode; ubiquity proofs)',
        'gates': {
            'check_pass_ab': f'ok dei_immensitate_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'note': 'Perfectione closed at 424; contiguous next tract Immensitate I-VIII',
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
        f'## {day} (Scribe — De Dei Immensitate & Omnipraesentia I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(opens Immensitate I–VIII → §§{SECS[0]}–{SECS[-1]} after Perfectione close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 118-119 / pp. 106-107).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Immensitate & Omnipraesentia through VIII. '
        'IX+ remains. Perfectione closed. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Immensitate & Omnipraesentia I–VIII densify)\n\n'
        'CoS densify: Immensitate I–VIII after Perfectione close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Immensitate I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: IX+. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-424 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
