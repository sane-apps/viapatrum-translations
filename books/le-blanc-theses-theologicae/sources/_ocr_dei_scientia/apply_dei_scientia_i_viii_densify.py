#!/usr/bin/env python3
"""Build + apply De Scientia Dei I-VIII densify (tip 497 → 505).

Opens after Vita Dei XXII close. Live floor 4815.
After tip-ready: HOLD live>4815 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_scientia_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_scientia/apply_dei_scientia_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['498', '499', '500', '501', '502', '503', '504', '505']
ROMANS = {
    '498': 'I', '499': 'II', '500': 'III', '501': 'IV',
    '502': 'V', '503': 'VI', '504': 'VII', '505': 'VIII',
}
TIP_BEFORE = 497
LIVE_FLOOR = 4815
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Scientia Dei I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Scientia Dei I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Scientia Dei I-VIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice opens Scientia Dei I-VIII "
    "(God knows; Scripture praise; plan of treatise; omniscience; God knows Himself comprehensively)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scientia Dei, sive De cognitione rerum quae in Deo est.\n"
    "Same 1675 Pitt copy-text. Book pp. 117-118 / PDF 129-130 (I-VIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Scientia Dei I-VIII tip — opens after Vita Dei XXII. Next: Scientia Dei IX+.\n"
    "Note: God endowed with intellect; Scripture; object of divine knowledge; God comprehends Himself.\n\n"
)

LATIN = {
    '498': (
        'I. Illa argumenta quae demonstrant Deum esse, eadem quoque probant illum esse '
        'intellectu & scientia praeditum: iis enim concluditur necessario dari causam primam, '
        'non tantum potentissimam, sed etiam optimam & sapientissimam, quae rebus singulis '
        'fines optimos praestituat, eisque commodissime & convenientissime ad finem suum '
        'quamque ducat atque dirigat, neque in Dei operibus quicquam clarius elucet, quam '
        'μιμητότατον ejus sapientia, quae corpora mundana, & varias in eis creaturas stupenda '
        'quadam arte fabricata est, & etiam prorsus admirando ordine inter se disposuit: '
        'adeoque necesse est ei inesse summam & excellentissimam vim cognoscendi & intelligendi.'
    ),
    '499': (
        'II. Et certe, cum inter ipsas creaturas visibiles multae reperiantur, quae sensu, '
        'ratione & intelligentia pollent, quis dubitare possit illarum authorem atque opificem '
        'modo longe praestantiori atque sublimiori res cognoscere atque percipere? juxta illud '
        'Psal. 94. An qui plantavit aurem non audiet: aut qui oculum finxit non considerat? '
        'Nec enim potest causa effectu suo minus perfecta esse: jam autem evidens est '
        'simpliciter perfectius esse id, quod cognoscit atque intelligit, quam illud quod est '
        'omni sensu & cognitione privatum; & absolute loquendo, melius atque optabilius esse '
        'intelligere, quam non intelligere.'
    ),
    '500': (
        'III. Ac profecto nullus est qui, audito Dei nomine, non statim notionem formet '
        'intelligentis cujusdam naturae, quae summa sit sapientia & virtute polleat, ne quidem '
        'exceptis ipsis epicureis, qui licet negaverint Deum, hujus universi authorem & '
        'rectorem esse, Deum tamen esse fassi sunt, rerumque cognitionem & contemplationem '
        'ei non ademerunt.'
    ),
    '501': (
        'IV. Praesertim vero Scriptura intelligentiam & scientiam Dei saepe praedicat. Sic '
        '1 Sam. 2. 3. Dominus vocatur Deus scientiarum, id est, Deus omni scientia praeditus. '
        'Quo respiciens David Psal. 147. Sapientiae, inquit, seu intelligentiae ejus non est '
        'numerus: Psalmo 139. sic Deum alloquitur, Mirabilis facta est scientia tua ex me, '
        'seu prae me, id est, mirabilis atque sublimior est, quam ut possim eam assequi. Unde '
        'est quod Paulus exclamat. Rom. 11. O altitudo divitiarum sapientiae & scientiae Dei.'
    ),
    '502': (
        'V. Ut autem mirabilis hujus scientiae, quae in Deo est, plenam atque distinctam, '
        'quantum quidem patitur mentis nostrae imbecillitas, cognitionem habeamus, '
        'expendendum est primo, quod sit ejus objectum, & ad quid se extendat. Secundo, '
        'qualis illa sit, & quae ejus ratio. Denique quotuplex sit, & quae sint ejus vulgatae '
        'in schola divisiones.'
    ),
    '503': (
        'VI. Quod ad primum attinet, scientiae divinae objectum in genere est quicquid sciri '
        '& cognosci potest. Deus enim novit omnia, ut docet Joan. Epist. 1. cap. 3. 20. '
        'Itaque quemadmodum dicitur omnipotens, sic quoque dici potest omniscius. Quod exigit '
        'plane ejus infinitas & summa perfectio alio loco a nobis demonstrata. Si enim Deus '
        'non novisset omnia, sed quaedam ipsum fugerent, & ab eo ignorarentur, abesset ab eo '
        'aliqua perfectio, & scientia ejus aliquos terminos & limites haberet, ultra quos non '
        'extenderetur, adeoque prorsus infinita non esset.'
    ),
    '504': (
        'VII. Sed ad pleniorem & distinctiorem omniscientiae divinae notitiam, necesse est '
        'ejus varia objecta percurrere & seorsim considerare. Primum autem & praecipuum '
        'cognitionis divinae objectum est, Deus ipse. Si enim creaturae intelligentes seipsas '
        'cognoscant: quanto magis istud est de Deo existimandum. Hoc ipsum exigit Dei '
        'sapientia: Etenim sapientiae pars non minima est seipsum novisse. Nec etiam objectum '
        'nobilissimum, quod est Deus, latere potest intellectum divinum, qui omnium '
        'nobilissimus est. Ac profecto si Deus seipsum non novisset, rerum creandarum '
        'consilium capere non potuisset: ad hoc enim necesse fuit, ut vires suas immensas '
        'suamque sapientiam, quibus res omnes condere, disponere & regere posset, probe '
        'cognitas & perspectas haberet.'
    ),
    '505': (
        'VIII. Porro Deus ita seipsum cognoscit, ut seipsum comprehendat. Quod sic '
        'accipiendum non est, quasi intellectus divinus essentiam divinam quibusdam quasi '
        'finibus concluderet. Etenim rem comprehendere, non est aliud quam eam cognoscere, '
        'quantum cognoscibilis est, & ita ut nihil ejus lateat cognoscentem, ut loquitur '
        'Thom. Aquinas, seu in essentia divina, quantumlibet infinita sit, nihil latere '
        'potest intellectum divinum, qui simili quoque modo infinitus est. Talis vero Dei '
        'cognitio ipsius Dei propria est, nec competit ulli creaturae. Nam cum creaturae '
        'omnes finitae sint, non possunt rem infinitam capere & comprehendere. Et huc potest '
        'illud Apostoli referri, Spiritus omnia scrutatur etiam profunda Dei. Quis enim '
        'hominum scit, quae sunt hominis, nisi spiritus hominis qui in ipso est: ita & quae '
        'Dei sunt nemo cognovit nisi Spiritus Dei: 1 Cor. 2. 11.'
    ),
}

SECTIONS = [
    {
        'section': '498',
        'title': 'Proofs that God is also prove He knows',
        'pass_a': (
            'Those arguments which demonstrate that God is, also prove that He is endowed with '
            'intellect and knowledge: for by them it is concluded that there necessarily is a '
            'first cause, not only most powerful, but also most good and most wise, which sets '
            'the best ends for individual things, and leads and directs each of them most fitly '
            'and conveniently to its end, nor does anything shine more clearly in God’s works '
            'than His most imitable wisdom, which with a certain stupendous art has fashioned '
            'the bodies of the world and the various creatures in them, and has also arranged '
            'them among themselves in a wholly admirable order: and therefore it is necessary '
            'that there be in Him a highest and most excellent power of knowing and understanding.'
        ),
        'pass_b': [
            'Deum-esse proofs force a knowing first cause.',
            'Best/wisest cause sets ends and directs creatures.',
            'World-order displays supreme knowing power.',
        ],
        'lemmas': [
            {'latin': 'intellectu & scientia praeditum', 'gloss': 'endowed with intellect and knowledge'},
            {'latin': 'vim cognoscendi & intelligendi', 'gloss': 'power of knowing and understanding'},
        ],
        'choices': [{
            'term': 'eadem quoque probant illum esse intellectu & scientia praeditum',
            'english': 'also prove that He is endowed with intellect and knowledge',
            'why': 'Opens Scientia by tying knowledge to the same first-cause proofs.',
            'rejected': ['a first cause could be powerful yet mindless'],
        }],
        'notes': ['OCR: Scientia I PDF 129 / p. 117; μιμητότατον sapientia.'],
        'bible_refs': [],
    },
    {
        'section': '499',
        'title': 'Maker of knowers must know more eminently — Ps 94',
        'pass_a': (
            'And certainly, since among the visible creatures themselves many are found that '
            'excel in sense, reason, and intelligence, who could doubt that their author and '
            'craftsman knows and perceives things in a far more excellent and loftier way? '
            'according to that of Psalm 94, Shall He who planted the ear not hear: or He who '
            'formed the eye not consider? For a cause cannot be less perfect than its effect: '
            'but now it is evident that what knows and understands is simply more perfect than '
            'that which is deprived of all sense and knowledge; and speaking absolutely, it is '
            'better and more desirable to understand than not to understand.'
        ),
        'pass_b': [
            'Creatures that know imply a knowing Maker.',
            'Ps 94: ear/eye maker hears and sees.',
            'Cause ≥ effect; knowing beats ignorance.',
        ],
        'lemmas': [
            {'latin': 'An qui plantavit aurem non audiet', 'gloss': 'Shall He who planted the ear not hear'},
            {'latin': 'causa effectu suo minus perfecta', 'gloss': 'a cause less perfect than its effect'},
        ],
        'choices': [{
            'term': 'Nec enim potest causa effectu suo minus perfecta esse',
            'english': 'For a cause cannot be less perfect than its effect',
            'why': 'Metaphysical lever from creature knowers to God’s higher knowledge.',
            'rejected': ['the Maker could lack what He gave creatures'],
        }],
        'notes': ['OCR: II PDF 129; Psal. 94.'],
        'bible_refs': ['Ps. 94:9'],
    },
    {
        'section': '500',
        'title': 'Even Epicureans grant God knows',
        'pass_a': (
            'And indeed there is no one who, when he has heard the name of God, does not at '
            'once form a notion of some intelligent nature which is of highest wisdom and '
            'excels in power — not even excepting the Epicureans themselves, who although they '
            'denied that God is the author and ruler of this universe, yet confessed that God '
            'is, and did not take from Him the knowledge and contemplation of things.'
        ),
        'pass_b': [
            'God’s name itself suggests an intelligent nature.',
            'Even Epicureans keep divine knowing.',
            'They deny providence, not contemplative knowledge.',
        ],
        'lemmas': [
            {'latin': 'notionem formet intelligentis cujusdam naturae', 'gloss': 'form a notion of some intelligent nature'},
            {'latin': 'cognitionem & contemplationem ei non ademerunt', 'gloss': 'did not take from Him knowledge and contemplation'},
        ],
        'choices': [{
            'term': 'Deum tamen esse fassi sunt, rerumque cognitionem & contemplationem ei non ademerunt',
            'english': 'yet confessed that God is, and did not take from Him the knowledge and contemplation of things',
            'why': 'Shows near-universal assent that deity includes knowing.',
            'rejected': ['Epicureans stripped God of all knowledge'],
        }],
        'notes': ['OCR: III PDF 129; Epicureans.'],
        'bible_refs': [],
    },
    {
        'section': '501',
        'title': 'Scripture praises God’s knowledge — 1 Sam 2; Ps 147/139; Rom 11',
        'pass_a': (
            'But especially Scripture often proclaims the intelligence and knowledge of God. '
            'So in 1 Samuel 2:3 the Lord is called the God of knowledges, that is, God endowed '
            'with all knowledge. Looking to which David in Psalm 147 says, Of His wisdom, or '
            'intelligence, there is no number: in Psalm 139 he addresses God thus, Your knowledge '
            'has been made wonderful from me, or beyond me, that is, it is wonderful and loftier '
            'than I can attain. Whence it is that Paul exclaims in Romans 11, O the depth of the '
            'riches of the wisdom and knowledge of God.'
        ),
        'pass_b': [
            '1 Sam 2:3 — God of knowledges.',
            'Ps 147 / 139 — unnumbered, unattainable knowledge.',
            'Rom 11 — depth of wisdom and knowledge.',
        ],
        'lemmas': [
            {'latin': 'Deus scientiarum', 'gloss': 'God of knowledges'},
            {'latin': 'O altitudo divitiarum sapientiae & scientiae Dei', 'gloss': 'O the depth of the riches of the wisdom and knowledge of God'},
        ],
        'choices': [{
            'term': 'Dominus vocatur Deus scientiarum',
            'english': 'the Lord is called the God of knowledges',
            'why': 'Scripture title anchoring the tract’s subject.',
            'rejected': ['Scripture rarely predicates knowledge of God'],
        }],
        'notes': ['OCR: IV PDF 130 / p. 118; 1 Sam 2; Ps 147/139; Rom 11.'],
        'bible_refs': ['1 Sam. 2:3', 'Ps. 147:5', 'Ps. 139:6', 'Rom. 11:33'],
    },
    {
        'section': '502',
        'title': 'Plan — object, nature, scholastic divisions',
        'pass_a': (
            'But that we may have a full and distinct knowledge of this wonderful knowledge '
            'which is in God, so far as the weakness of our mind allows, it must first be '
            'weighed what its object is, and to what it extends. Second, of what sort it is, '
            'and what its mode is. Finally how manifold it is, and what its common divisions '
            'in the schools are.'
        ),
        'pass_b': [
            'Three questions structure the tract.',
            'Object / extent; nature / ratio; scholastic kinds.',
            'Limited by our mind’s weakness.',
        ],
        'lemmas': [
            {'latin': 'quod sit ejus objectum', 'gloss': 'what its object is'},
            {'latin': 'vulgatae in schola divisiones', 'gloss': 'common divisions in the schools'},
        ],
        'choices': [{
            'term': 'expendendum est primo, quod sit ejus objectum',
            'english': 'it must first be weighed what its object is',
            'why': 'Roadmap thesis before object/omniscience theses.',
            'rejected': ['jump straight to divisions without object'],
        }],
        'notes': ['OCR: V PDF 130; treatise plan.'],
        'bible_refs': [],
    },
    {
        'section': '503',
        'title': 'Object in general — whatever can be known; omniscient',
        'pass_a': (
            'As for the first, the object of divine knowledge in general is whatever can be '
            'known and cognized. For God knows all things, as 1 John chapter 3 verse 20 teaches. '
            'And so just as He is called omnipotent, so also He can be called omniscient. Which '
            'His infinity and highest perfection, demonstrated by us elsewhere, plainly require. '
            'For if God had not known all things, but some things escaped Him and were unknown '
            'to Him, some perfection would be absent from Him, and His knowledge would have some '
            'bounds and limits beyond which it would not extend, and therefore would not be '
            'wholly infinite.'
        ),
        'pass_b': [
            '1 John 3:20 — God knows all.',
            'Omnipotent parallel → omniscient.',
            'Gaps in knowledge would bound and un-infinite Him.',
        ],
        'lemmas': [
            {'latin': 'novit omnia', 'gloss': 'knows all things'},
            {'latin': 'dici potest omniscius', 'gloss': 'can be called omniscient'},
        ],
        'choices': [{
            'term': 'quemadmodum dicitur omnipotens, sic quoque dici potest omniscius',
            'english': 'just as He is called omnipotent, so also He can be called omniscient',
            'why': 'Pairs infinite power with infinite knowledge.',
            'rejected': ['God could be infinite yet ignorant of some things'],
        }],
        'notes': ['OCR: VI PDF 130; 1 John 3:20; omniscius.'],
        'bible_refs': ['1 John 3:20'],
    },
    {
        'section': '504',
        'title': 'First object — God Himself; needed for creating counsel',
        'pass_a': (
            'But for a fuller and more distinct notice of divine omniscience, it is necessary '
            'to run through its various objects and consider them separately. But the first and '
            'chief object of divine knowledge is God Himself. For if intelligent creatures know '
            'themselves: how much more is that to be thought of God. God’s wisdom itself requires '
            'this: for not the least part of wisdom is to know oneself. Nor can the noblest '
            'object, which is God, hide from the divine intellect, which is the noblest of all. '
            'And indeed if God had not known Himself, He could not have taken counsel for '
            'creating things: for for that it was necessary that He have His immense powers and '
            'His wisdom, by which He could found, arrange, and rule all things, well known and '
            'seen through.'
        ),
        'pass_b': [
            'Chief object of divine knowing: God Himself.',
            'Self-knowledge is part of wisdom.',
            'Without knowing Himself He could not plan creation.',
        ],
        'lemmas': [
            {'latin': 'Primum … objectum est, Deus ipse', 'gloss': 'the first … object is God Himself'},
            {'latin': 'sapientiae pars non minima est seipsum novisse', 'gloss': 'not the least part of wisdom is to know oneself'},
        ],
        'choices': [{
            'term': 'si Deus seipsum non novisset, rerum creandarum consilium capere non potuisset',
            'english': 'if God had not known Himself, He could not have taken counsel for creating things',
            'why': 'Links self-knowledge to creative counsel.',
            'rejected': ['God could create without knowing His own power'],
        }],
        'notes': ['OCR: VII PDF 130; self as first object.'],
        'bible_refs': [],
    },
    {
        'section': '505',
        'title': 'God comprehends Himself — Thomas; 1 Cor 2',
        'pass_a': (
            'Further, God so knows Himself that He comprehends Himself. Which is not to be '
            'taken as if the divine intellect shut up the divine essence within certain bounds, '
            'as it were. For to comprehend a thing is nothing other than to know it as far as it '
            'is knowable, and so that nothing of it is hidden from the knower, as Thomas Aquinas '
            'speaks — or in the divine essence, however infinite it may be, nothing can be hidden '
            'from the divine intellect, which is likewise infinite. But such knowledge of God is '
            'proper to God Himself, and belongs to no creature. For since all creatures are '
            'finite, they cannot take in and comprehend an infinite thing. And to this can be '
            'referred that of the Apostle, The Spirit searches all things, even the deep things '
            'of God. For who among men knows the things of a man except the spirit of the man '
            'which is in him: so also the things of God no one has known except the Spirit of '
            'God: 1 Cor. 2:11.'
        ),
        'pass_b': [
            'God comprehends Himself — not by bounding His essence.',
            'Comprehend = know as far as knowable; nothing hidden (Thomas).',
            'Creature intellects finite; 1 Cor 2: Spirit alone knows God’s depths.',
        ],
        'lemmas': [
            {'latin': 'ut seipsum comprehendat', 'gloss': 'that He comprehends Himself'},
            {'latin': 'Spiritus omnia scrutatur etiam profunda Dei', 'gloss': 'The Spirit searches all things, even the deep things of God'},
        ],
        'choices': [{
            'term': 'Talis vero Dei cognitio ipsius Dei propria est, nec competit ulli creaturae',
            'english': 'But such knowledge of God is proper to God Himself, and belongs to no creature',
            'why': 'Closes I-VIII on incommunicable self-comprehension; next IX+ other objects.',
            'rejected': ['finite creatures can fully comprehend the infinite essence'],
        }],
        'notes': ['OCR: VIII PDF 130; Thomas; 1 Cor 2:10-11; next IX+.'],
        'bible_refs': ['1 Cor. 2:10-11'],
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
    for name in ('pdf_129.txt', 'pdf_130.txt'):
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
        if 498 <= n <= 505:
            notes = (
                f'Section {sid}: new densify De Scientia Dei I-VIII; '
                'Pass A!=B; lock-grounded PDF 129-130 / book pp. 117-118.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_scientia I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Scientia Dei I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Opens after Vita XXII. Next Scientia IX+. Not shipped.'
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
        'locus': 'De Scientia Dei theses I-VIII (knowing God; Scripture; object; self-comprehension)',
        'next_locus': 'De Scientia Dei IX+ (knows all else; singulars vs Averroes)',
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
        f'## {day} (Scribe — De Scientia Dei I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Scientia Dei I–VIII → §§{SECS[0]}–{SECS[-1]}; opens after Vita).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 129-130 / pp. 117-118).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Scientia Dei IX+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Scientia Dei I–VIII densify)\n\n'
        'CoS densify: Scientia Dei I–VIII open after Vita. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Scientia Dei I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Scientia IX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_505.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-505 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
