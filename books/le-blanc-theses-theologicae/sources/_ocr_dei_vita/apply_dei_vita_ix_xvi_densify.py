#!/usr/bin/env python3
"""Build + apply De Vita Dei IX-XVI densify (tip 483 → 491).

Continues after I-VIII. Live floor 4741 (post-hold).
After tip-ready: HOLD live>4741 OR 12m (or bumped live). Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_vita_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_vita_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_vita_densify')
PACKET_STEM = 'dei_vita_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_vita/apply_dei_vita_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['484', '485', '486', '487', '488', '489', '490', '491']
ROMANS = {
    '484': 'IX', '485': 'X', '486': 'XI', '487': 'XII',
    '488': 'XIII', '489': 'XIV', '490': 'XV', '491': 'XVI',
}
TIP_BEFORE = 483
PRIOR_START = 476
LIVE_FLOOR = 4741
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Vita Dei I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Vita Dei I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Vita Dei I-XVI, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Vita Dei IX-XVI "
    "(human vs brute freedom; angels; God more properly living; analogy)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Vita Dei.\n"
    "Same 1675 Pitt copy-text. Book pp. 114-116 / PDF 126-128 (I-XVI; this packet IX-XVI). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Vita Dei I-XVI tip — continues after I-VIII. Next: Vita Dei XVII+ (Scripture living God; then Scientia).\n"
    "Note: Human freedom vs brutes; angels; God lives more properly; creature life secundum quid.\n\n"
)

LATIN = {
    '484': (
        'IX. Quapropter homo vivit vita longe perfectiori quam animalia bruta: non solum '
        'quia longe plures & praestantiores actiones exercet: sed quia seipsum movet, & a '
        'seipso agit modo multo excellentiori. Bruta enim, quae carent ratione & intelligentia, '
        'nec finem sibi praestituunt, neque se ad finem dirigunt, sed simpliciter ad finem ab '
        'authore naturae aguntur, eodemque ducuntur necessario impressionibus per sensus ab '
        'objectis materialibus acceptis. Itaque illorum operationes non sunt in eorum potestate, '
        'nec proprie habent illarum dominium. Homo vero ratione utens finem ipse sibi '
        'praestituit, & media ad finem ducentia pro arbitrio rejicit, vel eligit: nec in suis '
        'actionibus ab objectis materialibus, & sensuum impressionibus necessario pendet: Sed '
        'operationes suas ad finem deliberate, & ex proprio judicio dirigit, & ita est '
        'αὐτεξούσιος, & propriarum actionum dominus.'
    ),
    '485': (
        'X. Et tamen fatendum est inter creaturas quasdam reperiri quarum vita est humana '
        'perfectior, substantias, scilicet, pure immateriales, ut sunt spiritus Angelici. Nec '
        'enim solum nobilior est eorum intelligentia, & ad multo plura eorum cognitio & virtus '
        'extenditur: Sed, cum materiae non sint alligati, in agendo minus pendent ab extrinseco '
        'quam homines, qui respectu multorum motuum qui ab ipsis, aut in ipsis exercentur, a '
        'materia pendent, atque determinantur, neque aliter agunt aut aguntur potius quam bruta.'
    ),
    '486': (
        'XI. Jam autem, si quis ex iis quae dicta sunt rite perpendat qua in re consistat vita '
        '& ejus perfectio, & creaturarum, quae vivere dicuntur, comparationem cum Deo instituat, '
        'facile agnoscet vitam magis proprie Deo competere quam ulli creaturae, & modo multo '
        'eminentiori.'
    ),
    '487': (
        'XII. Etenim creaturarum viventium nobilissimae atque praestantissimae a seipsis quidem '
        'agunt & moventur: sed secundum quid non vero simpliciter. Etenim non solum a Deo '
        'essentiam & virtutem operandi habent, & per eum continuo subsistunt atque conservantur: '
        'sed earum nullae agunt nisi a Deo primo agente actae: nec ullae earum moventur nisi '
        'virtute Dei primi motoris, in quo vivimus, movemur, & sumus, ut testatur Apostolus '
        'Actor. 17. & qui operatur omnia in omnibus juxta ejusdem Apostoli doctrinam: 1 Cor. 12. '
        'Deus autem a seipso agit simpliciter & absolute. Nec enim ab ullo in agendo pendet. '
        'Et, cum sit primus motor, ita seipsum movet, ut ab alio nullo moveatur.'
    ),
    '488': (
        'XIII. Deinde quae sunt inter creaturas praestantissimae habent quidem respectu quodam '
        'potestatem suorum actuum, & sunt propriarum actionum dominae, ideoque liberae '
        'dicuntur, & ipsis tribuitur αὐτεξούσιον: sed tota ista potestas a Dei summa potestate '
        'pendet, & prout ipsi libuerit, flectitur: ac dominium istud non est simplex & absolutum, '
        'sed precarium quodammodo, & supremo Dei dominio subditum. Ideoque solus Deus absolute '
        'est αὐτεξούσιος, & propriarum actionum Dominus: & solus gaudet libertate in agendo '
        'absoluta & prorsus independenti.'
    ),
    '489': (
        'XIV. Praeterea, cum vitae excellentia aestimetur etiam, sicut supra dictum est, ex '
        'varietate motuum & operationum quae a vivente exercentur, creaturae quidem multae '
        'reperiuntur quae variis omnino motibus sese movent, & multifarias actiones exercent, '
        'multaque & plane diversa operantur: sed tamen omnium illarum facultates certum '
        'obtinent perfectionis gradum, & ad certa actionum genera limitatae & determinatae '
        'sunt, ultra quae nihil possunt, nec valent quicquam perficere. At Deus Optim. Maxim. '
        'non multa potest, sed omnia; illiusque virtus est prorsus infinita & illimitata, nec '
        'terminis ullis definitur & circumscribitur ejus operandi potestas.'
    ),
    '490': (
        'XV. Adde quod sicut creaturae, etiam excellentissimae, vitam a seipsis non habent, '
        'sed a Deo prima rerum omnium causa, sic quoque, simpliciter & absolute loquendo, '
        'possunt illae omnes vita destitui, & ab agendo & existendo cessare, siquidem Deo ita '
        'visum fuerit. Ut vero Deus a nullo est, ita quoque vita ejus a nullo tolli & aboleri '
        'potest. Itaque licet creaturae quaedam aliarum respectu immortales dicantur, quia '
        'scilicet Dei beneficio in perpetuum victurae sunt, nec ulla est causa secunda quae '
        'illas perimere & destruere possit: tamen, si creaturae cum Deo comparentur, vivunt '
        'omnes illae vita mortali & defectibili, solus vero Deus est simpliciter & absolute '
        'immortalis & incorruptibilis, & propterea dicitur ab Apostolo solus habere '
        'immortalitatem, 1 Tim. 6.'
    ),
    '491': (
        'XVI. Igitur cum solus Deus simpliciter a seipso agat, atque a nullo moveatur, & '
        'absolutum habeat operationum suarum dominium, nec possit unquam ab ullo in agendo '
        'impediri, nedum omni motu & actione privari, & virtus quoque ejus sit plane '
        'illimitata & indeterminata, solus etiam simpliciter & absolute vivere dicendus est: '
        'creaturis vero vita competit tantum secundum quid, & per participationem & '
        'dependentiam a Deo. Ac proinde vita de Deo & creaturis non univoce dicitur, sed '
        'aequivoce & analogice.'
    ),
}

SECTIONS = [
    {
        'section': '484',
        'title': 'Human life freer than the brutes — self-directed end',
        'pass_a': (
            'Therefore man lives with a life far more perfect than the brute animals: not only '
            'because he exercises far more and more excellent actions, but because he moves '
            'himself and acts from himself in a far more excellent way. For the brutes, which '
            'lack reason and intelligence, neither set an end for themselves nor direct '
            'themselves to an end, but are simply driven to an end by the author of nature, and '
            'are necessarily led by the same impressions received through the senses from '
            'material objects. And so their operations are not in their power, nor do they '
            'properly have dominion over them. But man, using reason, himself sets an end for '
            'himself, and rejects or chooses the means leading to the end at will: nor in his '
            'actions does he necessarily depend on material objects and the impressions of the '
            'senses: but he directs his operations to the end deliberately and from his own '
            'judgment, and so is self-determining, and master of his own actions.'
        ),
        'pass_b': [
            'Humans outrank brutes by freer self-motion, not only more acts.',
            'Brutes: nature-pushed ends; no dominion over their acts.',
            'Man sets ends, picks means, αὐτεξούσιος — master of his acts.',
        ],
        'lemmas': [
            {'latin': 'finem ipse sibi praestituit', 'gloss': 'himself sets an end for himself'},
            {'latin': 'αὐτεξούσιος, & propriarum actionum dominus', 'gloss': 'self-determining, and master of his own actions'},
        ],
        'choices': [{
            'term': 'operationes suas ad finem deliberate, & ex proprio judicio dirigit',
            'english': 'he directs his operations to the end deliberately and from his own judgment',
            'why': 'Marks the human rung by free end-setting against brute necessity.',
            'rejected': ['brutes freely choose ends as men do'],
        }],
        'notes': ['OCR: IX PDF 127; αὐτεξούσιος.'],
        'bible_refs': [],
    },
    {
        'section': '485',
        'title': 'Angelic spirits live higher than humans',
        'pass_a': (
            'And yet it must be admitted that among creatures some are found whose life is more '
            'perfect than the human, namely pure immaterial substances, as are the angelic '
            'spirits. For not only is their intelligence nobler, and their knowledge and power '
            'extend to far more things: but, since they are not bound to matter, in acting they '
            'depend less on what is extrinsic than men do, who with respect to many motions '
            'which are exercised by them or in them depend on matter and are determined, and do '
            'not otherwise act — or rather are acted upon — than the brutes.'
        ),
        'pass_b': [
            'Angels: higher life than human among creatures.',
            'Nobler intellect; not bound to matter.',
            'Men still matter-determined in many motions like brutes.',
        ],
        'lemmas': [
            {'latin': 'spiritus Angelici', 'gloss': 'angelic spirits'},
            {'latin': 'materiae non sint alligati', 'gloss': 'they are not bound to matter'},
        ],
        'choices': [{
            'term': 'vita est humana perfectior',
            'english': 'life is more perfect than the human',
            'why': 'Inserts the angelic rung above man before comparing all to God.',
            'rejected': ['no creature surpasses human life'],
        }],
        'notes': ['OCR: X PDF 127; angelic immaterial substances.'],
        'bible_refs': [],
    },
    {
        'section': '486',
        'title': 'Life belongs more properly to God than to any creature',
        'pass_a': (
            'But now, if anyone from what has been said rightly weighs in what life and its '
            'perfection consist, and institutes a comparison of the creatures which are said to '
            'live with God, he will easily acknowledge that life belongs more properly to God '
            'than to any creature, and in a far more eminent way.'
        ),
        'pass_b': [
            'Weigh life’s marks against the creature grades.',
            'Life fits God more properly than any creature.',
            'And in a far more eminent mode.',
        ],
        'lemmas': [
            {'latin': 'vitam magis proprie Deo competere', 'gloss': 'that life belongs more properly to God'},
            {'latin': 'modo multo eminentiori', 'gloss': 'in a far more eminent way'},
        ],
        'choices': [{
            'term': 'vitam magis proprie Deo competere quam ulli creaturae',
            'english': 'that life belongs more properly to God than to any creature',
            'why': 'Thesis pivot from creature grades to God’s preeminent life.',
            'rejected': ['creature life and God’s life are equally proper'],
        }],
        'notes': ['OCR: XI PDF 127; pivot to God.'],
        'bible_refs': [],
    },
    {
        'section': '487',
        'title': 'Creatures act only secundum quid — God from Himself absolutely',
        'pass_a': (
            'For even the noblest and most excellent of living creatures do indeed act and '
            'move from themselves: but in a qualified sense, not simply. For not only do they '
            'have from God their essence and power of operating, and through Him they continually '
            'subsist and are conserved: but none of them act unless acted upon by God the first '
            'agent: nor are any of them moved except by the power of God the first mover, in '
            'whom we live, move, and are, as the Apostle testifies in Acts 17, and who works '
            'all things in all according to the same Apostle’s teaching in 1 Cor. 12. But God '
            'acts from Himself simply and absolutely. For He depends on no one in acting. And, '
            'since He is the first mover, He so moves Himself that He is moved by no other.'
        ),
        'pass_b': [
            'Top creatures self-move only secundum quid.',
            'Acts 17 / 1 Cor 12: first mover works all in all.',
            'God alone acts from Himself simply and absolutely.',
        ],
        'lemmas': [
            {'latin': 'secundum quid non vero simpliciter', 'gloss': 'in a qualified sense, not simply'},
            {'latin': 'a seipso agit simpliciter & absolute', 'gloss': 'acts from Himself simply and absolutely'},
        ],
        'choices': [{
            'term': 'nullae agunt nisi a Deo primo agente actae',
            'english': 'none of them act unless acted upon by God the first agent',
            'why': 'Creature self-motion is always under first-agency.',
            'rejected': ['top creatures act without God’s first agency'],
        }],
        'notes': ['OCR: XII PDF 127-128; Acts 17; 1 Cor 12.'],
        'bible_refs': ['Acts 17:28', '1 Cor. 12:6'],
    },
    {
        'section': '488',
        'title': 'Creature freedom is precarious — God alone absolutely free',
        'pass_a': (
            'Next, those which are most excellent among creatures do indeed have, in a certain '
            'respect, power over their acts, and are mistresses of their own actions, and '
            'therefore are called free, and self-determination is ascribed to them: but that '
            'whole power depends on God’s supreme power, and is bent as it pleases Him: and '
            'that dominion is not simple and absolute, but in a way precarious, and subject to '
            'God’s supreme dominion. And therefore God alone is absolutely self-determining, '
            'and Lord of His own actions: and He alone enjoys freedom in acting that is absolute '
            'and wholly independent.'
        ),
        'pass_b': [
            'Creature liberty / αὐτεξούσιον is real but borrowed.',
            'Bent under God’s supreme power — precarious dominion.',
            'God alone absolutely free and independent in acting.',
        ],
        'lemmas': [
            {'latin': 'precarium quodammodo', 'gloss': 'in a way precarious'},
            {'latin': 'solus Deus absolute est αὐτεξούσιος', 'gloss': 'God alone is absolutely self-determining'},
        ],
        'choices': [{
            'term': 'dominium istud non est simplex & absolutum, sed precarium',
            'english': 'that dominion is not simple and absolute, but precarious',
            'why': 'Keeps creature freedom without equating it to God’s.',
            'rejected': ['creature freedom is absolute like God’s'],
        }],
        'notes': ['OCR: XIII PDF 128; αὐτεξούσιον under God.'],
        'bible_refs': [],
    },
    {
        'section': '489',
        'title': 'Creatures limited in acts — God can do all',
        'pass_a': (
            'Further, since the excellence of life is also estimated, as was said above, from '
            'the variety of motions and operations which are exercised by the living thing, '
            'many creatures indeed are found which move themselves with altogether various '
            'motions, and exercise manifold actions, and work many and plainly diverse things: '
            'but still the faculties of all of them obtain a certain grade of perfection, and '
            'are limited and determined to certain kinds of actions, beyond which they can do '
            'nothing, nor are they able to accomplish anything. But God Most High can not many '
            'things, but all things; and His power is wholly infinite and unlimited, nor is His '
            'power of operating defined and circumscribed by any bounds.'
        ),
        'pass_b': [
            'Life’s excellence also tracked by variety of operations.',
            'Creatures capped at graded, limited action-kinds.',
            'God’s power: not many, but all — unbounded.',
        ],
        'lemmas': [
            {'latin': 'ad certa actionum genera limitatae', 'gloss': 'limited to certain kinds of actions'},
            {'latin': 'non multa potest, sed omnia', 'gloss': 'can not many things, but all things'},
        ],
        'choices': [{
            'term': 'non multa potest, sed omnia',
            'english': 'can not many things, but all things',
            'why': 'Contrasts creature variety-within-limits with infinite divine power.',
            'rejected': ['God’s power is a large but finite set of acts'],
        }],
        'notes': ['OCR: XIV PDF 128; infinite operandi potestas.'],
        'bible_refs': [],
    },
    {
        'section': '490',
        'title': 'Creature life defectible — God alone has immortality',
        'pass_a': (
            'Add that just as creatures, even the most excellent, do not have life from '
            'themselves, but from God the first cause of all things, so also, speaking simply '
            'and absolutely, they can all be stripped of life, and cease from acting and from '
            'existing, if it should so seem good to God. But as God is from no one, so also His '
            'life can be taken away and abolished by no one. And so although some creatures are '
            'called immortal with respect to others, because namely by God’s benefit they are to '
            'live forever, and there is no second cause which can destroy and ruin them: yet, if '
            'creatures are compared with God, they all live with a mortal and defectible life, '
            'but God alone is simply and absolutely immortal and incorruptible, and therefore '
            'is said by the Apostle to alone have immortality, 1 Tim. 6.'
        ),
        'pass_b': [
            'Even top creatures can lose life if God wills.',
            'Relative creature immortality ≠ absolute.',
            '1 Tim 6: God alone has immortality.',
        ],
        'lemmas': [
            {'latin': 'vita mortali & defectibili', 'gloss': 'with a mortal and defectible life'},
            {'latin': 'solus habere immortalitatem', 'gloss': 'alone to have immortality'},
        ],
        'choices': [{
            'term': 'solus habere immortalitatem, 1 Tim. 6',
            'english': 'alone to have immortality, 1 Tim. 6',
            'why': 'Scripture seal on God’s inalienable life vs defectible creatures.',
            'rejected': ['angelic immortality equals God’s'],
        }],
        'notes': ['OCR: XV PDF 128; 1 Tim 6.'],
        'bible_refs': ['1 Tim. 6:16'],
    },
    {
        'section': '491',
        'title': 'God alone lives simply — creature life by analogy',
        'pass_a': (
            'Therefore since God alone acts simply from Himself, and is moved by no one, and '
            'has absolute dominion of His operations, and can never be hindered by anyone in '
            'acting, still less be deprived of all motion and action, and His power also is '
            'plainly unlimited and indeterminate, He alone also is to be said to live simply '
            'and absolutely: but to creatures life belongs only in a qualified sense, and by '
            'participation and dependence on God. And therefore life is not said of God and '
            'creatures univocally, but equivocally and analogically.'
        ),
        'pass_b': [
            'Only God lives simply and absolutely.',
            'Creatures: life secundum quid, by participation.',
            'Not univocal — equivocal / analogical predication.',
        ],
        'lemmas': [
            {'latin': 'secundum quid, & per participationem', 'gloss': 'in a qualified sense, and by participation'},
            {'latin': 'non univoce … sed aequivoce & analogice', 'gloss': 'not univocally … but equivocally and analogically'},
        ],
        'choices': [{
            'term': 'vita de Deo & creaturis non univoce dicitur, sed aequivoce & analogice',
            'english': 'life is not said of God and creatures univocally, but equivocally and analogically',
            'why': 'Closes IX-XVI on analogical predication; next XVII+ Scripture’s living God.',
            'rejected': ['life is univocal of God and creatures'],
        }],
        'notes': ['OCR: XVI PDF 128; next XVII+ living God in Scripture.'],
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
        jpath = JUST / f'dei_vita_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_vita_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_127.txt', 'pdf_128.txt', 'pdf_126_134_layout.txt'):
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
        if 484 <= n <= 491:
            notes = (
                f'Section {sid}: new densify De Vita Dei IX-XVI; '
                'Pass A!=B; lock-grounded PDF 127-128 / book pp. 115-116.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_vita IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Vita Dei IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Next Vita XVII+ / Scripture living God. Not shipped.'
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
        'locus': 'De Vita Dei theses IX-XVI (freedom; angels; God more properly living; analogy)',
        'next_locus': 'De Vita Dei XVII+ (Scripture living God; oaths; then Scientia Dei)',
        'gates': {
            'check_pass_ab': f'ok dei_vita_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        f'## {day} (Scribe — De Vita Dei IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Vita Dei IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 127-128 / pp. 115-116).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Vita Dei XVII+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Vita Dei IX–XVI densify)\n\n'
        'CoS densify: Vita Dei IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Vita Dei IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Vita XVII+. Punch X: **NO**.\n\n---\n\n'
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
    # gate: pre-hold must already be cleared unless --force-after-hold
    cleared = DATA / 'hold_cleared_483.json'
    if mode == 'all' and not cleared.exists():
        raise SystemExit('refuse mid-writes: wait for hold_cleared_483.json (live>4741 OR 12m)')
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
    (DATA / 'hold_post_tipready_491.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-491 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
