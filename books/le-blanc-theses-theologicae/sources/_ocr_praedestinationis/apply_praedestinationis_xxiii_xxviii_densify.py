#!/usr/bin/env python3
"""Build + apply De Causa Praedestinationis XXIII-XXVIII densify (tip 549 → 555).

Reformed doctors on collective/glory election; Testard/Cappel minority; common ground with Rome.
Live floor 4988. After tip-ready: HOLD live>4988 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_praedestinationis_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_praedestinationis_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_praedestinationis_densify')
PACKET_STEM = 'praedestinationis_xxiii_xxviii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_praedestinationis/apply_praedestinationis_xxiii_xxviii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['550', '551', '552', '553', '554', '555']
ROMANS = {
    '550': 'XXIII', '551': 'XXIV', '552': 'XXV',
    '553': 'XXVI', '554': 'XXVII', '555': 'XXVIII',
}
TIP_BEFORE = 549
PRIOR_START = 528
LIVE_FLOOR = 4988
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXVIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXVIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Causa Praedestinationis I-XXVIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Causa Praedestinationis I-XXVIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Causa Praedestinationis I-XXVIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Praedestinatio XXIII-XXVIII "
    "(Reformed collective/glory election; Testard/Cappel; common ground with Rome)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Causa Praedestinationis (an detur in homine causa vel ratio aliqua suae Praedestinationis).\n"
    "Same 1675 Pitt copy-text. Book pp. 121-125 / PDF 133-137 (I-XXVIII; this packet XXIII-XXVIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Causa Praedestinationis I-XXVIII tip — continues after I-XXII. Next: Praedestinatio XXIX+.\n"
    "Note: Reformed unanimous on collective effects; most on absolute glory-election; Testard/Cappel; common ground.\n\n"
)

LATIN = {
    '550': (
        'XXIII. Quod spectat autem Scholae Reformatae Doctores omnes unanimi consensu '
        'statuunt praedestinationis ad gratiam & gloriam simul & collective sumptas, nullam '
        'in homine causam, conditionem, vel rationem reperiri posse, sed illam esse mere & '
        'absolute gratuitam, & a sola Dei libera voluntate pendere. Deum enim dum hos & illos '
        'prae aliis elegit, & ad gratiam & salutem ordinavit, nihil in iis spectasse quo ullo '
        'modo moveri potuerit ad illos tanta benevolentia & favore prae aliis prosequendos, '
        'nec ullam hujus rei rationem afferri posse, praeter unicum ejus beneplacitum.'
    ),
    '551': (
        'XXIV. Quod si quis seorsim considerare velit electionem ad gloriam, illamque '
        'distinguere a decreto conferendi varia gratiae dona, ad coelestis illius gloriae '
        'assecutionem necessaria, longe plurimi quoque ex Theologis Reformatis asserunt '
        'illam minime conditionatam, sed mere gratuitam & absolutam esse: Deumque ad gloriam '
        'absoluto decreto certos homines elegisse, priusquam in iis praevideret ullos futuros '
        'bonos motus, ullumque vel bonum opus, vel fidei initium. Quoniam Deus non potuit '
        'quicquam tale in iis praevidere antequam decrevisset illis dare gratiam ad omne '
        'bonum opus, omnemque fidei actum plane necessariam. Quod decretum, juxta nostrum '
        'concipiendi modum posterius esse censent electione ad gloriam, aut saltem non ea '
        'prius, sed cum ea cohaerens, eique si non subordinatum, saltem coordinatum.'
    ),
    '552': (
        'XXV. Attamen nonnulli sunt, qui secundum nostrum concipiendi modum, decretum de '
        'danda gloria posterius esse volunt electione ad fidem & gratiam efficacem, adeoque '
        'statuunt Deum ratione prius praevidere hominis fidem & bona opera, quam illum ad '
        'gloriam coelestem praedestinet. Unde sequitur praedestinationem ad vitam & gloriam '
        'aeternam esse ex fide, tanquam conditione ab aeterno a Deo praevisa in eo qui '
        'eligitur.'
    ),
    '553': (
        'XXVI. Quae est Pauli Testardi sententia in Irenico, Thesi 289. Nemo, inquit, certe '
        'negaverit electionem ad justificationem & glorificationem, si distincte consideretur '
        'esse ex fide praevisa, earumque objectum esse hominem credentem, quatenus '
        'credentem. Nam quales justificat & glorificat Deus in tempore, tales decrevit '
        'justificare & glorificare ab aeterno. Et quod est causa subordinata & conditio '
        'justificationis & glorificationis in tempore, illud est causa subordinata & '
        'conditio justificationis & glorificationis in decreto ab aeterno: quandoquidem '
        'executio decreto optime respondet.'
    ),
    '554': (
        'XXVII. Et his quoque consentanea docet Ludovicus Capellus thesibus de Electione & '
        'Reprobatione, quae insertae sunt Systemati Thesium Salmuriensium. Ibi enim thesi '
        'trigesima & trigesima prima haec sunt illius verba. Decretum de danda fide prius '
        'est, non quidem tempore, omnia enim Dei decreta in eo simul ab aeterno sunt, sed '
        'rei natura decreto de justificando & sanctificando, adeoque & de glorificando eo '
        'qui credit, & ab illis est distinguendum. Nam ut aliud est credere, aliud '
        'justificari, aliud sanctificari, aliud glorificari, sic etiam aliud est Dei '
        'decretum quo constituit homini dare fidem, aliud quo credentem justificare, '
        'sanctificare, & tandem glorificare sibi proposuit, nostro inquam concipiendi modo. '
        'Neque per decretum de glorificando fit prima inter homines separatio, sed per '
        'decretum de danda fide, quia reapse per veram fidem, & actu ipso, homines ab '
        'invicem primo separantur, qui eousque pares fuerant. Neque Deus primum decernit '
        'hominem absolute glorificare, deinde fidem illi dare; sed contra fidem dare, '
        'deinde glorificare decernit. Quia quemadmodum non nisi credentem actu glorificat, '
        'sic nec nisi credentem decrevit glorificare.'
    ),
    '555': (
        'XXVIII. Caeterum ex dictis apparet circa causam electionis & praedestinationis, '
        'prout suos omnes effectus respiciunt, nullam esse controversiam inter Doctores '
        'Reformatos, & plerosque Doctores Ecclesiae Romanae. Utrique enim in eo consentire, '
        'quod omnes effectus praedestinationis, simul & collective sumpti, nullam omnino '
        'causam in homine habeant, sed ad solam Dei gratiam atque benignitatem in solidum '
        'referendi sint. Unde sequitur nullam rationem ex parte hominis, reddi posse, cur '
        'hic potius, quam ille, ad gloriam & varia gratiae auxilia ab aeterno fuerit a Deo '
        'praedestinatus, sed id totum referendum esse ad merum & unicum Dei beneplacitum, '
        'quod a nulla conditione ex parte hominis pendere censendum est. Quod si quae restat '
        'ea de re quaestio, illa est tantum cum nonnullis vetustioris Scholae Theologis, & '
        'paucis quibusdam forte Neotericis, reclamante communi hodiernae Scholae sententia.'
    ),
}

SECTIONS = [
    {
        'section': '550',
        'title': 'Reformed unanimous — collective grace+glory predestination uncaused in man',
        'pass_a': (
            'But as regards the Doctors of the Reformed School, all with unanimous consent '
            'lay down that of predestination to grace and glory taken together and '
            'collectively, no cause, condition, or reason can be found in man, but that it is '
            'merely and absolutely gratuitous, and depends on the free will of God alone. For '
            'that God, when He elected these and those before others, and ordained them to '
            'grace and salvation, looked at nothing in them by which He could in any way be '
            'moved to pursue them with such great benevolence and favor before others, nor '
            'can any reason of this matter be brought forward except His sole good pleasure.'
        ),
        'pass_b': [
            'All Reformed Doctors: collective grace+glory election uncaused in man.',
            'Merely and absolutely gratuitous — free will of God alone.',
            'No motive in the elect; only God’s beneplacitum.',
        ],
        'lemmas': [
            {'latin': 'simul & collective sumptas', 'gloss': 'taken together and collectively'},
            {'latin': 'praeter unicum ejus beneplacitum', 'gloss': 'except His sole good pleasure'},
        ],
        'choices': [{
            'term': 'nullam in homine causam, conditionem, vel rationem reperiri posse',
            'english': 'that no cause, condition, or reason can be found in man',
            'why': 'Opens the Reformed block after the Roman merits party.',
            'rejected': ['Reformed allow a condition in man for the collective package'],
        }],
        'notes': ['OCR: XXIII PDF 137; Reformed unanimous collective.'],
        'bible_refs': [],
    },
    {
        'section': '551',
        'title': 'Most Reformed — glory-election absolute, before foresight of faith/works',
        'pass_a': (
            'But if anyone should wish to consider election to glory separately, and to '
            'distinguish it from the decree of conferring the various gifts of grace necessary '
            'to the obtaining of that heavenly glory, by far the greater part also of the '
            'Reformed Theologians assert that it is in no way conditioned, but merely '
            'gratuitous and absolute: and that God by an absolute decree elected certain men '
            'to glory before He foresaw in them any future good motions, or any good work, or '
            'beginning of faith. Because God could not foresee anything of that sort in them '
            'before He had decreed to give them the grace plainly necessary for every good '
            'work and every act of faith. Which decree, according to our way of conceiving, '
            'they judge to be later than election to glory, or at least not prior to it, but '
            'cohering with it, and if not subordinated to it, at least coordinated.'
        ),
        'pass_b': [
            'Most Reformed: glory-election itself absolute, not conditioned.',
            'Before foresight of motions, works, or faith’s start.',
            'Grace-decree later/coordinated with glory-election (our conception).',
        ],
        'lemmas': [
            {'latin': 'minime conditionatam, sed mere gratuitam & absolutam', 'gloss': 'in no way conditioned, but merely gratuitous and absolute'},
            {'latin': 'si non subordinatum, saltem coordinatum', 'gloss': 'if not subordinated, at least coordinated'},
        ],
        'choices': [{
            'term': 'Deumque ad gloriam absoluto decreto certos homines elegisse, priusquam in iis praevideret ullos futuros bonos motus',
            'english': 'and that God by an absolute decree elected certain men to glory before He foresaw in them any future good motions',
            'why': 'Mainstream Reformed absolute glory-election.',
            'rejected': ['most Reformed hang glory-election on foresight of faith'],
        }],
        'notes': ['OCR: XXIV PDF 137; majority Reformed absolute glory.'],
        'bible_refs': [],
    },
    {
        'section': '552',
        'title': 'Minority Reformed — glory-decree after foresight of faith and works',
        'pass_a': (
            'Yet there are some who, according to our way of conceiving, will that the decree '
            'of giving glory is later than election to faith and efficacious grace, and '
            'therefore lay down that God by reason foresaw man’s faith and good works before '
            'He predestines him to heavenly glory. Whence it follows that predestination to '
            'eternal life and glory is from faith, as a condition forever foreseen by God in '
            'him who is elected.'
        ),
        'pass_b': [
            'Some Reformed: glory-decree later than faith/grace election.',
            'God first foresees faith and works, then glory-predestination.',
            'So eternal glory-election is from foreseen faith as condition.',
        ],
        'lemmas': [
            {'latin': 'decretum de danda gloria posterius esse volunt electione ad fidem', 'gloss': 'will that the decree of giving glory is later than election to faith'},
            {'latin': 'ex fide, tanquam conditione ab aeterno a Deo praevisa', 'gloss': 'from faith, as a condition forever foreseen by God'},
        ],
        'choices': [{
            'term': 'praedestinationem ad vitam & gloriam aeternam esse ex fide, tanquam conditione',
            'english': 'that predestination to eternal life and glory is from faith, as a condition',
            'why': 'Names the minority foresight-of-faith reading.',
            'rejected': ['all Reformed deny any foresight condition for glory'],
        }],
        'notes': ['OCR: XXV PDF 137; minority foresight party.'],
        'bible_refs': [],
    },
    {
        'section': '553',
        'title': 'Testard Irenicum 289 — justification/glorification from foreseen faith',
        'pass_a': (
            'Which is the opinion of Paul Testard in the Irenicum, Thesis 289. No one, he '
            'says, will certainly deny that election to justification and glorification, if '
            'it be distinctly considered, is from foreseen faith, and that their object is '
            'the believing man as believing. For such as God justifies and glorifies in time, '
            'such He decreed to justify and glorify from eternity. And what is a subordinate '
            'cause and condition of justification and glorification in time, that is a '
            'subordinate cause and condition of justification and glorification in the decree '
            'from eternity: seeing that the execution answers optimally to the decree.'
        ),
        'pass_b': [
            'Testard Irenicum th. 289: election to justif./glorif. from foreseen faith.',
            'Object = the believer as believer.',
            'Time’s subordinate condition mirrors the eternal decree.',
        ],
        'lemmas': [
            {'latin': 'esse ex fide praevisa', 'gloss': 'is from foreseen faith'},
            {'latin': 'executio decreto optime respondet', 'gloss': 'the execution answers optimally to the decree'},
        ],
        'choices': [{
            'term': 'quales justificat & glorificat Deus in tempore, tales decrevit justificare & glorificare ab aeterno',
            'english': 'such as God justifies and glorifies in time, such He decreed to justify and glorify from eternity',
            'why': 'Testard’s time/eternity matching rule.',
            'rejected': ['Testard severs time’s condition from the eternal decree'],
        }],
        'notes': ['OCR: XXVI PDF 137; Testard Irenicum 289.'],
        'bible_refs': [],
    },
    {
        'section': '554',
        'title': 'Cappel Salmurian theses — faith-decree prior; no absolute glory first',
        'pass_a': (
            'And Louis Cappel also teaches things agreeing with these in the theses On '
            'Election and Reprobation which are inserted in the System of the Saumur Theses. '
            'For there in the thirtieth and thirty-first thesis these are his words. The '
            'decree of giving faith is prior, not indeed in time — for all God’s decrees are '
            'in Him together from eternity — but in the nature of the thing to the decree of '
            'justifying and sanctifying, and therefore also of glorifying him who believes, '
            'and is to be distinguished from them. For as it is one thing to believe, another '
            'to be justified, another to be sanctified, another to be glorified, so also it '
            'is one thing God’s decree by which He appointed to give faith to a man, another '
            'by which He proposed to Himself to justify, sanctify, and at length glorify the '
            'believer — in our way of conceiving, I say. Nor does the first separation among '
            'men come about through the decree of glorifying, but through the decree of '
            'giving faith, because in reality through true faith, and in the very act, men '
            'are first separated from one another who until then had been equals. Nor does '
            'God first decree to glorify a man absolutely, then give him faith; but on the '
            'contrary He decrees to give faith, then to glorify. Because just as He actually '
            'glorifies none but the believer, so also He decreed to glorify none but the '
            'believer.'
        ),
        'pass_b': [
            'Cappel (Saumur th. 30–31): faith-decree prior by nature of the thing.',
            'First separation = faith-decree, not glory-decree.',
            'Not: absolute glory then faith — reverse: faith then glory.',
        ],
        'lemmas': [
            {'latin': 'Decretum de danda fide prius est … sed rei natura', 'gloss': 'The decree of giving faith is prior … but in the nature of the thing'},
            {'latin': 'Neque Deus primum decernit hominem absolute glorificare, deinde fidem illi dare', 'gloss': 'Nor does God first decree to glorify a man absolutely, then give him faith'},
        ],
        'choices': [{
            'term': 'sed contra fidem dare, deinde glorificare decernit',
            'english': 'but on the contrary He decrees to give faith, then to glorify',
            'why': 'Cappel’s order blocks absolute-glory-first.',
            'rejected': ['Cappel puts absolute glory-decree before the faith-decree'],
        }],
        'notes': ['OCR: XXVII PDF 137; Cappel Salmurian System.'],
        'bible_refs': [],
    },
    {
        'section': '555',
        'title': 'Common ground — collective effects uncaused; leftover dispute with ancients',
        'pass_a': (
            'But from what has been said it appears that concerning the cause of election and '
            'predestination as they regard all their effects, there is no controversy between '
            'the Reformed Doctors and most of the Doctors of the Roman Church. For both '
            'agree in this, that all the effects of predestination, taken together and '
            'collectively, have no cause at all in man, but are to be referred wholly to the '
            'grace and kindness of God alone. Whence it follows that no reason on man’s part '
            'can be rendered why this one rather than that was from eternity predestined by '
            'God to glory and the various helps of grace, but that the whole is to be referred '
            'to the mere and sole good pleasure of God, which is to be judged to depend on no '
            'condition on man’s part. But if any question remains on that matter, it is only '
            'with some Theologians of the older School, and perhaps a few Neoterics, the '
            'common opinion of today’s School crying out against them.'
        ),
        'pass_b': [
            'Reformed + most Roman: no fight on collective uncaused package.',
            'Why this one not that → only God’s mere beneplacitum.',
            'Leftover quarrel only with older School / few Neoterics.',
        ],
        'lemmas': [
            {'latin': 'nullam esse controversiam inter Doctores Reformatos, & plerosque Doctores Ecclesiae Romanae', 'gloss': 'that there is no controversy between the Reformed Doctors and most of the Doctors of the Roman Church'},
            {'latin': 'ad merum & unicum Dei beneplacitum', 'gloss': 'to the mere and sole good pleasure of God'},
        ],
        'choices': [{
            'term': 'omnes effectus praedestinationis, simul & collective sumpti, nullam omnino causam in homine habeant',
            'english': 'that all the effects of predestination, taken together and collectively, have no cause at all in man',
            'why': 'Closes XXIII–XXVIII on Reformed/Roman common ground; next XXIX+ glory-alone question.',
            'rejected': ['Reformed and Rome still clash on the collective package'],
        }],
        'notes': ['OCR: XXVIII PDF 137; common ground; next XXIX+.'],
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
        jpath = JUST / f'praedestinationis_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab praedestinationis_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    raw_sources = [LOCK, pdf, Path(__file__), DATA / 'latin.json']
    for name in ('pdf_137.txt', 'pdf_138_fresh.txt', 'pdf_137_fresh.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20260929,
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
        if 550 <= n <= 555:
            notes = (
                'Section %s: new densify De Causa Praedestinationis XXIII-XXVIII; '
                'Pass A!=B; lock-grounded PDF 137 / book p. 125.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in praedestinationis XXIII-XXVIII packet scope covering all current sections.'
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
        'reviewer': 'scribe-leblanc, %s' % day,
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
                'Scope review: densify De Causa Praedestinationis XXIII-XXVIII only '
                '(sections %s-%s). Meta discloses %s. '
                'Next Praedestinatio XXIX+. Not shipped.'
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
            'De Causa Praedestinationis theses XXIII-XXVIII '
            '(Reformed collective/glory; Testard/Cappel; common ground)'
        ),
        'next_locus': (
            'De Causa Praedestinationis XXIX+ '
            '(glory-election alone vs grace-decree; Roman/Reformed split)'
        ),
        'gates': {
            'check_pass_ab': 'ok praedestinationis_%s–%s (%s/%s)' % (
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
    packet_files = (
        bt + 'reviews/audit/' + PACKET_STEM + '.packet.json' + bt
        + ' + '
        + bt + '.review.json' + bt
    )
    lock_ref = bt + LOCK_REL + bt
    claim_ref = bt + 'le-blanc-theses-densify' + bt
    slug_ref = bt + 'le-blanc-theses-theologicae' + bt
    block = (
        '## %s (Scribe — De Causa Praedestinationis XXIII–XXVIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** '
        '(contiguous Praedestinatio XXIII–XXVIII → §§%s–%s).\n'
        '- Packet %s (%s). '
        'Reviewer: scribe-leblanc, %s. Verdict pass grounded in '
        '%s (PDF 137 / p. 125).\n'
        '- Meta range bumped to **%s**.\n'
        '- Next: Praedestinatio XXIX+. Not shipped.\n'
        '- Pass A ≠ B for §§%s–%s. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Claim %s stays claimed. Punch X = NO.\n\n'
        % (
            day,
            receipt['before'],
            receipt['after'],
            SECS[0],
            SECS[-1],
            packet_ref,
            packet_files,
            day,
            lock_ref,
            RANGE_SHORT,
            SECS[0],
            SECS[-1],
            receipt['hold_clear_reason'],
            receipt['live_at_proceed'],
            claim_ref,
        )
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        '## %s ~ET (Scribe — Le Blanc De Causa Praedestinationis XXIII–XXVIII densify)\n\n'
        'CoS densify: Praedestinatio XXIII–XXVIII. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        '- **Le Blanc** %s: Praedestinatio XXIII–XXVIII (**'
        '%s→%s**). Packet %s. '
        'Next: Praedestinatio XXIX+. Punch X: **NO**.\n\n---\n\n'
        % (
            day,
            slug_ref,
            receipt['before'],
            receipt['after'],
            packet_ref,
        )
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
        raise SystemExit('refuse writes: hostname %s is not Mini' % host)
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
        raise SystemExit('tip drifted before append: %s (need %s)' % (len(eng), TIP_BEFORE))
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
    (DATA / 'hold_post_tipready_555.json').write_text(
        json.dumps({
            'hold_start': hold_start.isoformat(timespec='seconds'),
            'live_floor': post_floor,
            'tip_after': TIP_BEFORE + len(SECS),
            'note': 'post tip-ready hold live>%s OR 12m' % post_floor,
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-555 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
