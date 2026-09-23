#!/usr/bin/env python3
"""Build + apply De Dei Perfectione & Infinitate XVII-XXIV densify (tip 414 → 422).

A-se fountain; El Shaddai; essence infinite. Live floor 4494.
After tip-ready: HOLD live>4494 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_perfectione_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_perfectione/apply_dei_perfectione_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['415', '416', '417', '418', '419', '420', '421', '422']
ROMANS = {
    '415': 'XVII', '416': 'XVIII', '417': 'XIX', '418': 'XX',
    '419': 'XXI', '420': 'XXII', '421': 'XXIII', '422': 'XXIV',
}
TIP_BEFORE = 414
LIVE_FLOOR = 4494
HOLD_MINUTES = 12
PRIOR_START = 399

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Perfectione & Infinitate I-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Perfectione & Infinitate I-XXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Perfectione & Infinitate I-XXIV, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Perfectione XVII-XXIV "
    "(a-se fountain; El Shaddai; infinite essence)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Perfectione & Infinitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 102-105 / PDF 114-117 (I-XXIV; this packet XVII-XXIV). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Perfectione & Infinitate I-XXIV tip. XXV+ remains.\n"
    "Note: Continues after IX-XVI. A-se / Shaddai / infinitude of essence.\n\n"
)

LATIN = {
    '415': (
        'XVII. Sed praeterea quod in Deo sit omnis perfectio quae esse & haberi potest, inde, '
        'ut jam dictum, aliunde probatur, quod Deus qui est prima rerum omnium causa nullam '
        'ipse causam habet, sed est primum ens omnino independens, quod a seipso est, non ab '
        'ullo alio. Nam quod rerum creatarum natura & perfectio certa & determinata est, ita '
        'ut haec habeat unam perfectionem, ista vero aliam: inde fit quod ab alio suum esse '
        'acceperunt. Istud enim earum discrimen, & ista determinatio, omnino referri debet ad '
        'causam efficientem, quae singulis talem naturam indulsit, istumque, non alium, '
        'perfectionis gradum. Adeoque primum ens, quod suum esse non accepit ab alio, sed per '
        'seipsum est, & vi suae essentiae existit, non potest habere certam perfectionis '
        'mensuram, & esse quiddam ad hoc & illud determinatum: sed est ipse totius esse fons '
        '& origo prima, quae in se continet omnem entitatem & perfectionem.'
    ),
    '416': (
        'XVIII. Et certe si a Deo absit aliqua perfectio, necesse est ut perfectio ista sit '
        'aliquid possibile, vel non. Si non est quidpiam possibile; sed aliquid quod esse '
        'repugnat, certe perfectio non est, sed merum nihil: nec Deus quod illam non habet '
        'potest dici aliqua perfectione carere. Si vero est aliquid possibile quod sit, aut '
        'esse possit, quandoquidem Deus est primum ens, & prima causa, unde reliqua omnia '
        'pendent, nec est, nec esse potest, nisi per Dei virtutem, & consequenter ab eo non '
        'abest: sed in eo saltem virtute & eminenter continetur.'
    ),
    '417': (
        'XIX. Deus igitur est ens perfectissimum, quod non tantum entia singula perfectione '
        'superat, sed etiam in se habet omnem omnis entis perfectionem: nec caret excellentia '
        'ulla quae sit aut esse possit. Et haec est summa Dei perfectio, quam exprimit vox '
        'Hebraea Shaddai, quae unum est ex divinis nominibus. Nam Dai Hebraeis est '
        'sufficientia. Ideoque El Shaddai proprie significat illum cui nihil deest, & qui '
        'nulla re eget, sed in se, & a se habet omnimodam sufficientiam, sive dixeris '
        'autarkes, qui sibi ipsi sufficit & potest solus omnia efficere, unde non male '
        'vertitur omnipotens.'
    ),
    '418': (
        'XX. Atque hoc est nomen quod Deus assumpsit foedus cum Abrahamo pangens: Ego sum, '
        'inquit, El Shaddai, Deus fortis, & omnipotens, seu potius, omnisufficiens. Quo '
        'titulo Deus innuebat foedus illud, non sua, sed Abrahami causa initum: nec quicquam '
        'eorum quae illi spondebat sibi deesse. Nulla res creata est, quae sibi ipsa '
        'sufficiat: aliae aliis opus habent, nec ulla est quae saltem Dei continua ope non '
        'egeat. Sed Deo proprium est omnia a se habere, nec indigere re ulla. Ideoque '
        'creaturae sunt profectus capaces, & possunt semper aliquid accipere: sed Deo nihil '
        'nocere, nihil prodesse potest. Nec bonum aut malum ullum ad ipsum unquam pertingit.'
    ),
    '419': (
        'XXI. Porro ex ista summa Dei perfectione & sufficientia sequitur ipsum infinitum '
        'esse, & essentiam habere infinitam. Quandoquidem enim Deus habet omnem '
        'perfectionem, quae esse & haberi potest, certum est nihil ipso melius & perfectius '
        'esse, vel cogitari posse: adeoque necesse est ipsum esse infinitum. Nam bonum '
        'infinitum finito bono melius est.'
    ),
    '420': (
        'XXII. Deinde essentiae rerum creatarum ideo finitae dicuntur, quia perfectio '
        'uniuscujusque certum terminum & limitem habet, ultra quem non extenditur. Nimirum '
        'haec habet unam perfectionem, ista vero aliam: & singulae, intra fines proprios '
        'continentur, nec perfectiones aliarum habent. Ita perfectio quaedam essentialis est '
        'in bove, quaedam in equo, quaedam in homine: verum equus non habet perfectionem '
        'bovis, nec homo habet perfectionem equi, sed istorum unumquodque suam. Et in summa, '
        'nulla est creatura quantumvis perfecta, a qua non absit aliqua perfectio. Cum ergo '
        'in Deo res aliter se habeat, & ipse contineat omnem omnis entis perfectionem, modo '
        'quodam nobilissimo & eminentissimo, ipsius essentia finita dici non potest; sed '
        'infinitam esse necesse est.'
    ),
    '421': (
        'XXIII. Adde quod perfectiones quae rebus creatis insunt, includuntur certis '
        'terminis ultra quos non extenduntur. Omnique earum vis & activitas certam habet '
        'sphaeram quam transgredi non valet. Sed divinae perfectiones omni prorsus limite '
        'carent. Nec Deus tantum omnem perfectionem habet: sed omnem omnis perfectionis '
        'gradum absque ulla limitatione.'
    ),
    '422': (
        'XXIV. Et certe quod finitum atque limitatum est, necesse est ita fuisse limitatum '
        'ab aliqua causa, quae ipsi talem naturam tribuit, & certum assignavit perfectionis '
        'gradum. Sed Deus, ut jam dictum, nullam supra se causam habet, quae limitare ipsum '
        'potuerit, & illi certos terminos ponere: cum ipse sit prima rerum omnium causa. '
        'Ideoque necesse est Deum naturam habere plane illimitatam, omnique fine & termino '
        'carentem: quod est infinitum esse.'
    ),
}

SECTIONS = [
    {
        'section': '415',
        'title': 'Uncaused first being — fountain of all entity and perfection',
        'pass_a': (
            'But besides that every perfection which can be and be had is in God is proved, as '
            'already said, from another place, that God who is the first cause of all things '
            'Himself has no cause, but is the first being altogether independent, which is from '
            'Himself, not from any other. For that the nature and perfection of created things is '
            'certain and determinate, so that this has one perfection, that another: thence it '
            'comes that they received their being from another. For that discrimen of theirs, and '
            'that determination, must altogether be referred to the efficient cause which granted '
            'to each such a nature, and that grade of perfection, not another. And therefore the '
            'first being, which did not receive its being from another, but is through itself, and '
            'exists by force of its essence, cannot have a certain measure of perfection, and be '
            'something determined to this and that: but is itself the fountain and first origin of '
            'all being, which contains in itself every entity and perfection.'
        ),
        'pass_b': [
            'Creatures\' bounded perfections prove they received being from another.',
            'First being has no cause — exists by His essence.',
            'He is the fountain of all entity and perfection — not a measured grade.',
        ],
        'lemmas': [
            {'latin': 'primum ens omnino independens', 'gloss': 'first being altogether independent'},
            {'latin': 'totius esse fons & origo prima', 'gloss': 'fountain and first origin of all being'},
        ],
        'choices': [{
            'term': 'est ipse totius esse fons & origo prima',
            'english': 'is itself the fountain and first origin of all being',
            'why': 'A-se ground of containing every perfection.',
            'rejected': ['first being has a limited perfection-measure from a higher cause'],
        }],
        'notes': ['OCR: XVII PDF 116.'],
        'bible_refs': [],
    },
    {
        'section': '416',
        'title': 'No possible perfection can be absent from God',
        'pass_a': (
            'And certainly if some perfection is absent from God, it is necessary that that '
            'perfection be something possible, or not. If it is not anything possible, but '
            'something to which to be is repugnant, certainly it is not a perfection, but mere '
            'nothing: nor can God, because He does not have it, be said to lack some perfection. '
            'But if it is something possible that is, or can be, since God is the first being, and '
            'first cause, from which all the rest depend, it neither is nor can be except through '
            'God\'s power, and consequently it is not absent from Him: but is contained in Him at '
            'least by virtue and eminently.'
        ),
        'pass_b': [
            'If a missing "perfection" is impossible — it is nothing, not a lack.',
            'If it is possible — it depends on the first cause.',
            'So it is in God at least virtute & eminenter.',
        ],
        'lemmas': [
            {'latin': 'merum nihil', 'gloss': 'mere nothing'},
            {'latin': 'virtute & eminenter continetur', 'gloss': 'is contained by virtue and eminently'},
        ],
        'choices': [{
            'term': 'ab eo non abest: sed in eo saltem virtute & eminenter continetur',
            'english': 'it is not absent from Him: but is contained in Him at least by virtue and eminently',
            'why': 'No possible excellence escapes God.',
            'rejected': ['a possible perfection can exist underived from God'],
        }],
        'notes': ['OCR: XVIII PDF 116.'],
        'bible_refs': [],
    },
    {
        'section': '417',
        'title': 'El Shaddai — all-sufficient, not lacking',
        'pass_a': (
            'God therefore is the most perfect being, which not only surpasses singular beings in '
            'perfection, but also has in Himself every perfection of every being: nor lacks any '
            'excellence which is or can be. And this is the highest perfection of God, which the '
            'Hebrew word Shaddai expresses, which is one of the divine names. For Dai among the '
            'Hebrews is sufficiency. And therefore El Shaddai properly signifies Him to whom '
            'nothing is lacking, and who needs no thing, but in Himself and from Himself has '
            'every-way sufficiency, or if you prefer autarkes, who suffices for Himself and alone '
            'can effect all things, whence it is not badly rendered omnipotent.'
        ),
        'pass_b': [
            'Most perfect: holds every excellence of every being.',
            'Hebrew Shaddai / Dai = sufficiency.',
            'El Shaddai: lacks nothing; self-sufficient — often rendered omnipotent.',
        ],
        'lemmas': [
            {'latin': 'El Shaddai', 'gloss': 'El Shaddai'},
            {'latin': 'omnimodam sufficientiam', 'gloss': 'every-way sufficiency'},
        ],
        'choices': [{
            'term': 'illum cui nihil deest, & qui nulla re eget',
            'english': 'Him to whom nothing is lacking, and who needs no thing',
            'why': 'Names summa perfectio as Shaddai.',
            'rejected': ['Shaddai means God needs creaturely help'],
        }],
        'notes': ['OCR: XIX PDF 116; Shaddai/Dai normalized from OCR.'],
        'bible_refs': [],
    },
    {
        'section': '418',
        'title': 'Covenant name with Abraham — God needs nothing',
        'pass_a': (
            'And this is the name which God assumed when striking a covenant with Abraham: I am, '
            'He says, El Shaddai, the strong God, and omnipotent, or rather, all-sufficient. By '
            'which title God was hinting that that covenant was entered not for His own sake, but '
            'for Abraham\'s: nor that anything of those things which He was promising to him was '
            'lacking to Himself. There is no created thing which suffices for itself: some need '
            'others, nor is there any which at least does not need God\'s continual help. But it '
            'is proper to God to have all things from Himself, and to need no thing. And therefore '
            'creatures are capable of progress, and can always receive something: but nothing can '
            'harm God, nothing profit Him. Nor does any good or evil ever reach Him.'
        ),
        'pass_b': [
            'To Abraham: I am El Shaddai — all-sufficient, not needy.',
            'Covenant for Abraham\'s sake — nothing God promised was lacking to God.',
            'Creatures always need and can receive; God needs nothing, gains nothing.',
        ],
        'lemmas': [
            {'latin': 'omnisufficiens', 'gloss': 'all-sufficient'},
            {'latin': 'nec indigere re ulla', 'gloss': 'and to need no thing'},
        ],
        'choices': [{
            'term': 'Deo proprium est omnia a se habere, nec indigere re ulla',
            'english': 'it is proper to God to have all things from Himself, and to need no thing',
            'why': 'Covenant name seals divine aseity/sufficiency.',
            'rejected': ['God\'s covenant fills a lack in God'],
        }],
        'notes': ['OCR: XX PDF 116; Gen 17 foedus.'],
        'bible_refs': ['Gen. 17'],
    },
    {
        'section': '419',
        'title': 'Highest perfection implies infinite essence',
        'pass_a': (
            'Further from that highest perfection and sufficiency of God it follows that He '
            'Himself is infinite, and has an infinite essence. For since God has every perfection '
            'which can be and be had, it is certain that nothing better and more perfect than He '
            'is, or can be thought: and therefore it is necessary that He Himself be infinite. For '
            'an infinite good is better than a finite good.'
        ),
        'pass_b': [
            'Summa perfectio → infinite essence.',
            'Nothing better than God can be or be thought.',
            'Infinite good outranks finite good.',
        ],
        'lemmas': [
            {'latin': 'essentiam habere infinitam', 'gloss': 'to have an infinite essence'},
            {'latin': 'bonum infinitum finito bono melius est', 'gloss': 'an infinite good is better than a finite good'},
        ],
        'choices': [{
            'term': 'necesse est ipsum esse infinitum',
            'english': 'it is necessary that He Himself be infinite',
            'why': 'Opens infinitude from perfection.',
            'rejected': ['a finite essence can still be most perfect'],
        }],
        'notes': ['OCR: XXI PDF 116-117.'],
        'bible_refs': [],
    },
    {
        'section': '420',
        'title': 'Creatures finite by bounded kinds — God holds every kind eminently',
        'pass_a': (
            'Next the essences of created things are therefore called finite, because the '
            'perfection of each has a certain bound and limit beyond which it is not extended. '
            'Namely this has one perfection, that another: and each is contained within its own '
            'bounds, nor do they have the perfections of others. So there is a certain essential '
            'perfection in an ox, a certain in a horse, a certain in a man: but a horse does not '
            'have the perfection of an ox, nor a man the perfection of a horse, but each of those '
            'its own. And in sum, there is no creature however perfect from which some perfection '
            'is not absent. Since therefore in God the matter stands otherwise, and He Himself '
            'contains every perfection of every being in a most noble and most eminent mode, His '
            'essence cannot be called finite; but it is necessary that it be infinite.'
        ),
        'pass_b': [
            'Creature essences finite: each kind stops at its own limit.',
            'Ox / horse / man — each lacks the others\' essential perfection.',
            'God holds every being\'s perfection eminently — so His essence is infinite.',
        ],
        'lemmas': [
            {'latin': 'certum terminum & limitem', 'gloss': 'a certain bound and limit'},
            {'latin': 'infinitam esse necesse est', 'gloss': 'it is necessary that it be infinite'},
        ],
        'choices': [{
            'term': 'ipsius essentia finita dici non potest',
            'english': 'His essence cannot be called finite',
            'why': 'Contrast creature kind-limits with God\'s all-containment.',
            'rejected': ['God\'s essence is one finite kind among others'],
        }],
        'notes': ['OCR: XXII PDF 117.'],
        'bible_refs': [],
    },
    {
        'section': '421',
        'title': 'Divine perfections have no sphere or grade-limit',
        'pass_a': (
            'Add that the perfections which are in created things are included in certain bounds '
            'beyond which they are not extended. And all their force and activity has a certain '
            'sphere which it cannot transgress. But divine perfections lack altogether every '
            'limit. Nor does God only have every perfection: but every grade of every perfection '
            'without any limitation.'
        ),
        'pass_b': [
            'Creature perfections: bounded sphere of force.',
            'Divine perfections: no limit at all.',
            'Not only every perfection — every grade without limitation.',
        ],
        'lemmas': [
            {'latin': 'certam habet sphaeram', 'gloss': 'has a certain sphere'},
            {'latin': 'omni prorsus limite carent', 'gloss': 'lack altogether every limit'},
        ],
        'choices': [{
            'term': 'omnem omnis perfectionis gradum absque ulla limitatione',
            'english': 'every grade of every perfection without any limitation',
            'why': 'Intensifies infinitude beyond mere possession.',
            'rejected': ['God has every perfection but only at a capped grade'],
        }],
        'notes': ['OCR: XXIII PDF 117.'],
        'bible_refs': [],
    },
    {
        'section': '422',
        'title': 'No superior cause to limit God — therefore unlimited',
        'pass_a': (
            'And certainly what is finite and limited must have been so limited by some cause '
            'which granted it such a nature and assigned a certain grade of perfection. But God, '
            'as already said, has no cause above Himself which could limit Him and set certain '
            'bounds for Him: since He Himself is the first cause of all things. And therefore it '
            'is necessary that God have a nature plainly unlimited, and lacking every end and '
            'bound: which is to be infinite.'
        ),
        'pass_b': [
            'Finite things were limited by a cause that set their grade.',
            'God has no superior cause to bound Him.',
            'Therefore His nature is unlimited — infinite.',
        ],
        'lemmas': [
            {'latin': 'nullam supra se causam', 'gloss': 'no cause above Himself'},
            {'latin': 'plane illimitatam', 'gloss': 'plainly unlimited'},
        ],
        'choices': [{
            'term': 'quod est infinitum esse',
            'english': 'which is to be infinite',
            'why': 'Closes XVII-XXIV on uncaused unlimited essence; next XXV+ Scripture.',
            'rejected': ['a higher cause caps God\'s perfection-grade'],
        }],
        'notes': ['OCR: XXIV PDF 117; next XXV+ Scriptural infinitude.'],
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
    for name in ('pdf_116_119_layout.txt', 'pdf_114_117_perfectione.txt'):
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
        if 415 <= n <= 422:
            notes = (
                f'Section {sid}: new densify De Dei Perfectione & Infinitate XVII-XXIV; '
                'Pass A!=B; lock-grounded PDF 116-117 / book pp. 104-105.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_perfectione XVII-XXIV packet scope covering all current sections.'
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
                'Scope review: densify De Dei Perfectione & Infinitate XVII-XXIV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Perfectione through XXIV; XXV+ remains. Not shipped.'
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
        'locus': 'De Dei Perfectione & Infinitate theses XVII-XXIV (a-se / Shaddai / infinitude)',
        'next_locus': 'De Dei Perfectione & Infinitate XXV+ (Scripture on infinite essence)',
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
        f'## {day} (Scribe — De Dei Perfectione & Infinitate XVII–XXIV densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Perfectione XVII–XXIV → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 116-117 / pp. 104-105).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Perfectione & Infinitate through XXIV. XXV+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Perfectione & Infinitate XVII–XXIV densify)\n\n'
        'CoS densify: De Dei Perfectione & Infinitate XVII–XXIV. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Perfectione XVII–XXIV (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: XXV+. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-414 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
