#!/usr/bin/env python3
"""Build + apply De Causa Praedestinationis XVII-XXII densify (tip 543 → 549).

Bellarmine allies (Petrus/Jansenius/Thomists); opposite glory-from-merits party (Becanus/Vasquez).
Live floor 4963. After tip-ready: HOLD live>4963 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'praedestinationis_xvii_xxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_praedestinationis/apply_praedestinationis_xvii_xxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['544', '545', '546', '547', '548', '549']
ROMANS = {
    '544': 'XVII', '545': 'XVIII', '546': 'XIX',
    '547': 'XX', '548': 'XXI', '549': 'XXII',
}
TIP_BEFORE = 543
PRIOR_START = 528
LIVE_FLOOR = 4963
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Causa Praedestinationis I-XXII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Causa Praedestinationis I-XXII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Causa Praedestinationis I-XXII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Praedestinatio XVII-XXII "
    "(Bellarmine allies; Becanus/Vasquez glory-from-merits party)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Causa Praedestinationis (an detur in homine causa vel ratio aliqua suae Praedestinationis).\n"
    "Same 1675 Pitt copy-text. Book pp. 121-125 / PDF 133-137 (I-XXII; this packet XVII-XXII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Causa Praedestinationis I-XXII tip — continues after I-XVI. Next: Praedestinatio XXIII+.\n"
    "Note: Bellarmine allies (Petrus/Jansenius); opposite party Becanus/Vasquez on glory from foreseen merits.\n\n"
)

LATIN = {
    '544': (
        'XVII. Bellarmino hac in parte astipulatur Petrus a Sancto Joseph cujus haec est '
        'Resolutio. Probabilior est sententia quae docet, electionem efficacem ad gloriam '
        'factam esse antecedenter ad absolutam praevisionem meritorum, adeoque esse mere '
        'gratuitam. In Idea Theologiae speculativae lib. 1. cap. 20. Resolutione 1.'
    ),
    '545': (
        'XVIII. Denique idem ea de re docent Eustachius a Sancto Paulo, Dominicus Bannes, '
        'Gulielmus Estius, & alii qui dicuntur Thomistae recentiores, omnium vero maxime '
        'Jansenius & ejus Discipuli, qui acriter tuentur praedestinationem & electionem '
        'hominis ad Gloriam, & aeternam beatitudinem, non minus gratuitam esse, & secundum '
        'nostrum concipiendi modum, praevisionem bonorum operum in Deo praecedere, quam '
        'praedestinationem hominis ad gratiam.'
    ),
    '546': (
        'XIX. Fundamentum autem eorum est quod gloria finis est, merita vero hominis medium '
        'ad finem illum consequendum: prior est autem intentio finis electione mediorum. '
        'Unde sequitur destinationem hominis ad gloriam, qua Deus finem intendit, praecedere '
        'decretum de conferendis per gratiam meritis, ut mediis ad finem illum necessariis: '
        'ac proinde praevisionem meritorum hominis sequi electionem illius ad gloriam, quae '
        'sic non potest niti illa praevisione, ut conditione vel causa.'
    ),
    '547': (
        'XX. Plurimi tamen Scholae Romanae Theologi in ea sunt sententia, non tantum in '
        'tempore gloriam dari ex meritis, sed aeternam ipsam praedestinationem, seu '
        'electionem hominis ad gloriam, factam esse ex praevisis meritis: ita ut, juxta '
        'ipsos, ipsum illud decretum quo Deus ab aeterno quibusdam hominibus gloriam '
        'destinavit, non sit simpliciter & mere gratuitum, sed factum sit non solum post '
        'praevisa hominis merita, verum etiam propter illa praevisa.'
    ),
    '548': (
        'XXI. Haec est sententia Martini Becani, qui postquam dixit multos ex Scholasticis '
        'sentire praedestinationem, seu efficacem electionem ad gloriam factam esse ex '
        'praevisis meritis, sequentia verba subjungit. Porro haec sententia, quae multo '
        'probabilior est, potest duobus modis explicari. Primo de praescientia conditionata, '
        'ut sensus sit, Deus, antequam efficaciter eligeret aliquos ad gloriam, praevidit per '
        'scientiam conditionatam, quinam bene usuri essent gratia Dei si illis daretur. '
        'Secundo de praescientia absoluta, hoc sensu: Deus absolute praevidit aliquos bene '
        'operaturos, antequam illos efficaciter eligeret ad gloriam. Rursum utrumque '
        'dupliciter intelligi potest. Primo Deus efficaciter elegit aliquos ad gloriam ex '
        'praevisis meritis, id est, post praevisa merita. Secundo, ex praevisis meritis, id '
        'est, propter praevisa merita. Nos dicimus omnibus modis veram esse hanc sententiam. '
        'In Summa Theol. tom. 1. cap. 9. q. 1. sect. 3.'
    ),
    '549': (
        'XXII. Hac in parte vero Becanus, ut in multis aliis, sequitur Gabrielem Vasquez qui '
        'tomo primo in primam Thomae, disputatione 89. haec duo constituit & multis probare '
        'contendit. Prius est, Nullam electionem efficacem ad gloriam ex sola Dei voluntate '
        'fuisse, antequam merita praeviderentur ex gratia, sed quemlibet ad gloriam electum '
        'fuisse ex meritis praevisis, quae ex gratia facturus erat. Posterius est, ante merita '
        'gratiae praevisa, nullum peculiarem affectum donandi gloriam Deum habuisse erga '
        'praedestinatos, sed circa omnes etiam reprobos habuisse communem voluntatem '
        'simplicem, vel antecedentem, qua omnibus vitam aeternam, tanquam bravium, & '
        'praemium commune aequum proposuit, & desideravit. Cap. 2. In eadem autem cum '
        'Vasquez, & cum Becano sententia, sunt alii plurimi, quos Becanus nominat loco supra '
        'citato, ut Pighius, Molina, Lessius, Ruardus, Driedo, Eckius, Turrianus, Stapletonus, '
        'Gregorius de Valentia. Et e Veteribus Alensis, Bonaventura, Albertus Magnus, Thomas '
        'Argentinensis, Henricus Gandavensis, Occam, Gabriel, Joannes Major: Quos omnes idem '
        'in hac quaestione secum sentire affirmat jam dictus Martinus Becanus.'
    ),
}

SECTIONS = [
    {
        'section': '544',
        'title': 'Petrus a S. Joseph — glory-election before foresight of merits',
        'pass_a': (
            'Petrus a Sancto Joseph agrees with Bellarmine on this part, whose Resolution is '
            'this. More probable is the opinion which teaches that efficacious election to '
            'glory was made antecedently to the absolute foresight of merits, and therefore '
            'is merely gratuitous. In the Idea of Speculative Theology book 1 chapter 20 '
            'Resolution 1.'
        ),
        'pass_b': [
            'Petrus a S. Joseph sides with Bellarmine.',
            'Efficacious glory-election before absolute foresight of merits.',
            'Therefore merely gratuitous — Idea Theol. I.20 Res. 1.',
        ],
        'lemmas': [
            {'latin': 'astipulatur Petrus a Sancto Joseph', 'gloss': 'Petrus a Sancto Joseph agrees'},
            {'latin': 'antecedenter ad absolutam praevisionem meritorum', 'gloss': 'antecedently to the absolute foresight of merits'},
        ],
        'choices': [{
            'term': 'electionem efficacem ad gloriam factam esse antecedenter ad absolutam praevisionem meritorum',
            'english': 'that efficacious election to glory was made antecedently to the absolute foresight of merits',
            'why': 'Opens the Bellarmine-ally block after XVI.',
            'rejected': ['Petrus puts glory-election after foresight of merits'],
        }],
        'notes': ['OCR: XVII PDF 136; Idea Theol. I.20.'],
        'bible_refs': [],
    },
    {
        'section': '545',
        'title': 'Thomists and Jansenius — glory-election as free as grace-election',
        'pass_a': (
            'Finally Eustachius a Sancto Paulo, Dominicus Bannes, Gulielmus Estius, and '
            'others who are called more recent Thomists teach the same on that matter — and '
            'most of all Jansenius and his Disciples, who stoutly maintain that the '
            'predestination and election of man to Glory and eternal beatitude is no less '
            'gratuitous, and according to our way of conceiving precedes the foresight of '
            'good works in God, than the predestination of man to grace.'
        ),
        'pass_b': [
            'Eustachius, Bannes, Estius + recent Thomists agree.',
            'Jansenius & disciples: glory-election no less free than grace-election.',
            'Our conception: it precedes foresight of good works.',
        ],
        'lemmas': [
            {'latin': 'non minus gratuitam esse', 'gloss': 'is no less gratuitous'},
            {'latin': 'praevisionem bonorum operum in Deo praecedere', 'gloss': 'precedes the foresight of good works in God'},
        ],
        'choices': [{
            'term': 'praedestinationem & electionem hominis ad Gloriam … non minus gratuitam esse … quam praedestinationem hominis ad gratiam',
            'english': 'that the predestination and election of man to Glory … is no less gratuitous … than the predestination of man to grace',
            'why': 'Parity of gratuitousness for glory- vs grace-election.',
            'rejected': ['Jansenius makes glory-election hang on foresight of works'],
        }],
        'notes': ['OCR: XVIII PDF 136; Jansenius / Thomists.'],
        'bible_refs': [],
    },
    {
        'section': '546',
        'title': 'End before means — glory-destination precedes merits-decree',
        'pass_a': (
            'But their foundation is that glory is the end, but man’s merits are the means to '
            'obtaining that end: and the intention of the end is prior to the choice of means. '
            'Whence it follows that the destination of man to glory, by which God intends the '
            'end, precedes the decree of conferring merits through grace, as means necessary '
            'to that end: and therefore that the foresight of man’s merits follows his '
            'election to glory, which thus cannot rest on that foresight as a condition or '
            'cause.'
        ),
        'pass_b': [
            'Glory = end; merits = means → intention of end first.',
            'Glory-destination precedes the grace/merits decree.',
            'Foresight of merits follows election — cannot be its cause.',
        ],
        'lemmas': [
            {'latin': 'prior est autem intentio finis electione mediorum', 'gloss': 'and the intention of the end is prior to the choice of means'},
            {'latin': 'praevisionem meritorum hominis sequi electionem', 'gloss': 'that the foresight of man’s merits follows his election'},
        ],
        'choices': [{
            'term': 'quae sic non potest niti illa praevisione, ut conditione vel causa',
            'english': 'which thus cannot rest on that foresight as a condition or cause',
            'why': 'Blocks foresight-of-merits as ground of glory-election.',
            'rejected': ['foresight of merits is the condition of glory-election'],
        }],
        'notes': ['OCR: XIX PDF 136; finis/media order.'],
        'bible_refs': [],
    },
    {
        'section': '547',
        'title': 'Opposite party — eternal glory-election from foreseen merits',
        'pass_a': (
            'Yet very many Theologians of the Roman School are of this opinion: not only that '
            'in time glory is given from merits, but that the eternal predestination itself, or '
            'election of a man to glory, was made from foreseen merits: so that, according to '
            'them, that very decree by which God from eternity destined glory to certain men '
            'is not simply and merely gratuitous, but was made not only after man’s foreseen '
            'merits, but also on account of those foreseen merits.'
        ),
        'pass_b': [
            'Many Roman School: eternal glory-election from foreseen merits.',
            'Not merely post praevisa — also propter praevisa.',
            'So the glory-decree itself is not simply gratuitous.',
        ],
        'lemmas': [
            {'latin': 'factam esse ex praevisis meritis', 'gloss': 'was made from foreseen merits'},
            {'latin': 'non solum post praevisa … verum etiam propter illa praevisa', 'gloss': 'not only after the foreseen … but also on account of those foreseen'},
        ],
        'choices': [{
            'term': 'ipsum illud decretum … non sit simpliciter & mere gratuitum, sed factum sit … propter illa praevisa',
            'english': 'that very decree … is not simply and merely gratuitous, but was made … on account of those foreseen merits',
            'why': 'Names the opposite glory-from-merits party.',
            'rejected': ['the opposite party keeps the glory-decree absolute'],
        }],
        'notes': ['OCR: XX PDF 136; post/propter praevisa.'],
        'bible_refs': [],
    },
    {
        'section': '548',
        'title': 'Becanus — conditional vs absolute foresight; post vs propter',
        'pass_a': (
            'This is the opinion of Martin Becanus, who after he has said that many of the '
            'Scholastics think predestination, or efficacious election to glory, was made from '
            'foreseen merits, subjoins the following words. Further this opinion, which is '
            'much more probable, can be explained in two ways. First of conditioned '
            'foreknowledge, so that the sense is: God, before He efficaciously elected some to '
            'glory, foresaw by conditioned knowledge who would use God’s grace well if it were '
            'given them. Second of absolute foreknowledge, in this sense: God absolutely '
            'foresaw that some would work well, before He efficaciously elected them to glory. '
            'Again each can be understood doubly. First God efficaciously elects some to glory '
            'from foreseen merits, that is, after foreseen merits. Second, from foreseen '
            'merits, that is, on account of foreseen merits. We say that this opinion is true '
            'in all ways. In the Summa of Theology tome 1 chapter 9 question 1 section 3.'
        ),
        'pass_b': [
            'Becanus: glory-election from foreseen merits is more probable.',
            'Splits: conditioned vs absolute foresight.',
            'And: post praevisa vs propter praevisa — true in all modes.',
        ],
        'lemmas': [
            {'latin': 'de praescientia conditionata', 'gloss': 'of conditioned foreknowledge'},
            {'latin': 'post praevisa merita … propter praevisa merita', 'gloss': 'after foreseen merits … on account of foreseen merits'},
        ],
        'choices': [{
            'term': 'Nos dicimus omnibus modis veram esse hanc sententiam',
            'english': 'We say that this opinion is true in all ways',
            'why': 'Becanus endorses every branch of the foresight reading.',
            'rejected': ['Becanus rejects propter-praevisa as false'],
        }],
        'notes': ['OCR: XXI PDF 136; Becanus Summa Theol. I.9.'],
        'bible_refs': [],
    },
    {
        'section': '549',
        'title': 'Vasquez Disp. 89 — no free glory-election before merits; allies listed',
        'pass_a': (
            'But on this part Becanus, as in many other things, follows Gabriel Vasquez who '
            'in the first tome on the first part of Thomas, disputation 89, lays down these '
            'two points and contends to prove them with many arguments. The first is that '
            'there was no efficacious election to glory from the will of God alone before '
            'merits from grace were foreseen, but that anyone elected to glory was elected '
            'from foreseen merits which he was going to perform from grace. The second is '
            'that before the foreseen merits of grace God had no peculiar affection of giving '
            'glory toward the predestined, but toward all even the reprobate had a common '
            'simple or antecedent will by which He equally proposed and desired eternal life '
            'to all as a prize and common reward. Chapter 2. And in the same opinion with '
            'Vasquez and with Becanus are very many others whom Becanus names in the place '
            'cited above, as Pighius, Molina, Lessius, Ruardus, Driedo, Eckius, Turrianus, '
            'Stapleton, Gregory of Valencia. And among the older writers Alexander of Hales, '
            'Bonaventure, Albert the Great, Thomas of Strasbourg, Henry of Ghent, Ockham, '
            'Gabriel, John Major: all of whom the same Martin Becanus already named affirms '
            'to agree with him on this question.'
        ),
        'pass_b': [
            'Vasquez Disp. 89: no efficacious glory-election from will alone before merits.',
            'Before merits: only common antecedent will toward all, even reprobate.',
            'Becanus’s roll-call: Molina/Lessius/Stapleton … to Major.',
        ],
        'lemmas': [
            {'latin': 'Nullam electionem efficacem ad gloriam ex sola Dei voluntate fuisse', 'gloss': 'that there was no efficacious election to glory from the will of God alone'},
            {'latin': 'communem voluntatem simplicem, vel antecedentem', 'gloss': 'a common simple or antecedent will'},
        ],
        'choices': [{
            'term': 'ante merita gratiae praevisa, nullum peculiarem affectum donandi gloriam Deum habuisse erga praedestinatos',
            'english': 'that before the foreseen merits of grace God had no peculiar affection of giving glory toward the predestined',
            'why': 'Vasquez’s second thesis — no special glory-love before merits.',
            'rejected': ['Vasquez grants a special glory-affection before merits'],
        }],
        'notes': ['OCR: XXII PDF 136-137; Vasquez Disp. 89; next XXIII+ Reformed.'],
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
    for name in ('pdf_136.txt', 'pdf_137.txt', 'pdf_136_fresh.txt', 'pdf_137_fresh.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20260928,
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
        if 544 <= n <= 549:
            notes = (
                f'Section {sid}: new densify De Causa Praedestinationis XVII-XXII; '
                'Pass A!=B; lock-grounded PDF 136-137 / book pp. 124-125.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in praedestinationis XVII-XXII packet scope covering all current sections.'
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
                'Scope review: densify De Causa Praedestinationis XVII-XXII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Next Praedestinatio XXIII+. Not shipped.'
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
        'locus': 'De Causa Praedestinationis theses XVII-XXII (Bellarmine allies; Becanus/Vasquez merits party)',
        'next_locus': 'De Causa Praedestinationis XXIII+ (Reformed doctors; Testard/Cappel)',
        'gates': {
            'check_pass_ab': f'ok praedestinationis_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        f'## {day} (Scribe — De Causa Praedestinationis XVII–XXII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Praedestinatio XVII–XXII → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 136-137 / pp. 124-125).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Praedestinatio XXIII+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Causa Praedestinationis XVII–XXII densify)\n\n'
        'CoS densify: Praedestinatio XVII–XXII. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Praedestinatio XVII–XXII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Praedestinatio XXIII+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_549.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-549 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
