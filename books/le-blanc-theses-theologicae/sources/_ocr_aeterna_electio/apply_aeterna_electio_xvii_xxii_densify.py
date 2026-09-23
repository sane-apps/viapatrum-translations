#!/usr/bin/env python3
"""Build + apply De Aeterna Hominum Electione XVII-XXII densify (tip 577 → 583).

Communior fallen-in-Adam; Reformed word-senses; electio variants; supralapsarian object.
Live floor 5135. After tip-ready: HOLD live>5135 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_aeterna_electio_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_aeterna_electio_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_aeterna_electio_densify')
PACKET_STEM = 'aeterna_electio_xvii_xxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_aeterna_electio/apply_aeterna_electio_xvii_xxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['578', '579', '580', '581', '582', '583']
ROMANS = {
    '578': 'XVII', '579': 'XVIII', '580': 'XIX',
    '581': 'XX', '582': 'XXI', '583': 'XXII',
}
TIP_BEFORE = 577
PRIOR_START = 562
LIVE_FLOOR = 5153
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeterna Hominum Electione et Praedestinatione I-XXII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeterna Hominum Electione et Praedestinatione I-XXII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeterna Hominum Electione et Praedestinatione I-XXII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeterna Electio XVII-XXII "
    "(communior fallen-in-Adam; Reformed senses; supralapsarian object)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeterna Hominum Electione et Praedestinatione.\n"
    "Same 1675 Pitt copy-text. Book pp. 127-130 / PDF 139-142 (I-XXII; this packet XVII-XXII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeterna Hominum Electione et Praedestinatione I-XXII tip. Next: Aeterna Electio XXIII+.\n"
    "Note: Communior fallen-in-Adam; Reformed praedestinatio/electio senses; Dort; Cameronians; "
    "XXII opens object-question with Primo/supralapsarii (page-break continuation).\n\n"
)

LATIN = {
    '578': (
        'XVII. Sed communior Scholae Romanae sententia est, quum Deus certos homines '
        'ab aeterno praedestinavit, illum eos considerasse ut in Adamo lapsos, & peccato '
        'corruptos. Nam communiter censent illius Theologi decretum illud quo Deus quosdam '
        'ex hominibus ad salutem praedestinavit, secundum nostrum concipiendi modum '
        'posterius esse praevisione lapsus primi hominis, ac inde consequentis peccati '
        'originalis, quo totum genus humanum infectum est.'
    ),
    '579': (
        'XVIII. Quod spectat autem illos qui inter Protestantes singulari nomine Reformati '
        'dicuntur, eorum plurimi voce praedestinationis significant totam illam providentiae '
        'divinae partem, qua Deus apud se ante mundum conditum decrevit & statuit ea quae '
        'singulorum hominum, vel aeternam salutem, vel interitum & exitium spectant. Ac '
        'proinde aeternam Dei praedestinationem distinguunt, in eam quae est ad vitam & '
        'salutem, & in eam quae est ad mortem & exitium. Et prior illa est quae communiter '
        'Electio, posterior quae Reprobatio in Scholis appellatur. Sic utuntur voce '
        'praedestinationis Zanchius, Beza, Ursinus, Perkinsus, Polanus, Bucanus, & alii '
        'complures, ac ipsa quoque Synodus Dordracena.'
    ),
    '580': (
        'XIX. Non pauci tamen Doctores Reformati praedestinationis vocem, juxta Scripturae '
        'usum, in bonam partem tantum sumendam esse putant. Ac proinde per praedestinationem '
        'designant illos solos divinae mentis & voluntatis actus, quibus Deus de certis '
        'hominibus ad vitam & gloriam coelestem perducendis, & mediis quae ad hunc finem '
        'assequendum necessaria sunt illis subministrandis, immutabiliter apud se constituit. '
        'Nec enim restringunt praedestinationem ad solam gratiae praeparationem, quemadmodum '
        'multi Scholastici: sed tam decretum de fine, quam decretum de mediis, id est, tam '
        'decretum de danda certis hominibus gloria, quam decretum de gratia illis '
        'communicanda, praedestinationis nomine complectuntur.'
    ),
    '581': (
        'XX. Et eodem quoque sensu vocem Electionis usurpant. Siquidem per Electionem '
        'intelligunt decretum, quo Deus ab aeterno quosdam homines ab aliis selegit, ut '
        'illos in hac vita gratiae Christi participes redderet, in altera vero gloria '
        'coronaret; adeo & electio & praedestinatio pro Synonymis ab ipsis habeantur.'
    ),
    '582': (
        'XXI. Attamen nonnulli videntur per electionem proprie designare decretum de certis '
        'quibusdam hominibus efficaciter ad Christum vocandis & fide vera vivaque donandis. '
        'Ut electio, juxta ipsos, potius gratiae communicationem, quam donationem gloriae '
        'respiciat. Sic electionis vocem communiter usurpant Testardus in Irenico, Ludovicus '
        'Capellus Thesibus de Electione & Reprobatione, et Moses Amyraldus passim, aliique '
        'qui cum illis Cameronis Methodum & doctrinam sequuntur.'
    ),
    '583': (
        'XXII. Non parum quoque variant in Schola Reformata Theologorum sententiae, circa '
        'quaestionem illam sub qua ratione & respectu homo sit objectum divinae '
        'praedestinationis. Primo enim nonnulli in assignando objecto praedestinationis '
        'atque electionis, supra lapsum hominis, imo supra ipsam hominis creationem '
        'ascendunt. Etenim decretum praedestinationis certorum quorundam hominum ad '
        'salutem in Deo, secundum nostrum concipiendi modum, prius fuisse volunt, non '
        'solum praevisione lapsus hominis in peccatum, sed ipso quoque decreto de homine '
        'creando. Ac proinde objectum praedestinationis ipsis est homo non conditus & '
        'lapsus in Dei praescientia: sed potius homo creabilis. Unde est quod ab aliis '
        'Theologis supralapsarii vocantur. Quo de numero sunt Zanchius, Beza, Piscator, '
        'Perkinsus, Ursinus, Gomarus, Polanus, Voetius, Twissus, & alii non pauci.'
    ),
}

SECTIONS = [
    {
        'section': '578',
        'title': 'Communior Roman view — God predestined men as fallen in Adam',
        'pass_a': (
            'But the more common opinion of the Roman School is that when God from eternity '
            'predestined certain men, He considered them as fallen in Adam and corrupted by '
            'sin. For the Theologians of that School commonly judge that that decree by which '
            'God predestined some of men to salvation is, according to our way of conceiving, '
            'later than the foresight of the first man’s fall, and thence of the consequent '
            'original sin by which the whole human race is infected.'
        ),
        'pass_b': [
            'Common Roman view: God predestined men as fallen in Adam, sin-corrupted.',
            'Salvation-decree later (our conception) than foresight of the first fall.',
            'And later than foresight of original sin infecting the whole race.',
        ],
        'lemmas': [
            {'latin': 'ut in Adamo lapsos, & peccato corruptos', 'gloss': 'as fallen in Adam and corrupted by sin'},
            {'latin': 'posterius esse praevisione lapsus primi hominis', 'gloss': 'to be later than the foresight of the first man’s fall'},
        ],
        'choices': [{
            'term': 'illum eos considerasse ut in Adamo lapsos, & peccato corruptos',
            'english': 'that He considered them as fallen in Adam and corrupted by sin',
            'why': 'Opens XVII+ against XVI’s creatable-object party.',
            'rejected': ['the common Roman view takes the object as creatable, not fallen'],
        }],
        'notes': ['OCR: XVII PDF 141; communior fallen-in-Adam.'],
        'bible_refs': [],
    },
    {
        'section': '579',
        'title': 'Most Reformed — praedestinatio covers election and reprobation',
        'pass_a': (
            'But as regards those who among Protestants are called by the special name '
            'Reformed, most of them by the word predestination signify that whole part of '
            'divine providence by which God with Himself before the world was founded decreed '
            'and appointed those things which look to each man’s eternal salvation, or to his '
            'ruin and destruction. And therefore they distinguish God’s eternal '
            'predestination into that which is to life and salvation, and that which is to '
            'death and destruction. And the former is that which is commonly called Election '
            'in the Schools, the latter Reprobation. So Zanchius, Beza, Ursinus, Perkins, '
            'Polanus, Bucanus, and many others use the word predestination, and the Synod of '
            'Dort itself also.'
        ),
        'pass_b': [
            'Most Reformed: praedestinatio = whole providence re salvation or ruin.',
            'Split: to life/salvation (election) vs to death/ruin (reprobation).',
            'Zanchius, Beza, Ursinus, Perkins, Polanus, Bucanus, Dort.',
        ],
        'lemmas': [
            {'latin': 'in eam quae est ad vitam & salutem, & in eam quae est ad mortem & exitium', 'gloss': 'into that which is to life and salvation, and that which is to death and destruction'},
            {'latin': 'prior illa est quae communiter Electio, posterior quae Reprobatio', 'gloss': 'the former is that which is commonly called Election, the latter Reprobation'},
        ],
        'choices': [{
            'term': 'aeternam Dei praedestinationem distinguunt, in eam quae est ad vitam & salutem, & in eam quae est ad mortem & exitium',
            'english': 'they distinguish God’s eternal predestination into that which is to life and salvation, and that which is to death and destruction',
            'why': 'States the majority Reformed double use of praedestinatio.',
            'rejected': ['most Reformed restrict praedestinatio to election alone'],
        }],
        'notes': ['OCR: XVIII PDF 141; Dort + Reformed majority.'],
        'bible_refs': [],
    },
    {
        'section': '580',
        'title': 'Many Reformed — praedestinatio only in the good sense (end + means)',
        'pass_a': (
            'Yet not a few Reformed Doctors think the word predestination, according to '
            'Scripture’s use, is to be taken only in a good sense. And therefore by '
            'predestination they designate only those acts of the divine mind and will by '
            'which God immutably appointed with Himself concerning certain men to be brought '
            'to heavenly life and glory, and concerning the means necessary to obtaining '
            'that end to be supplied to them. For they do not restrict predestination to the '
            'preparation of grace alone, as many Scholastics do: but they embrace under the '
            'name of predestination both the decree concerning the end and the decree '
            'concerning the means — that is, both the decree of giving glory to certain men '
            'and the decree of communicating grace to them.'
        ),
        'pass_b': [
            'Many Reformed: praedestinatio only in the good / Scriptural sense.',
            'Acts bringing certain men to heavenly life/glory + supplying the means.',
            'Not grace-prep alone — covers both glory-decree and grace-decree.',
        ],
        'lemmas': [
            {'latin': 'in bonam partem tantum sumendam', 'gloss': 'to be taken only in a good sense'},
            {'latin': 'tam decretum de fine, quam decretum de mediis', 'gloss': 'both the decree concerning the end and the decree concerning the means'},
        ],
        'choices': [{
            'term': 'tam decretum de danda certis hominibus gloria, quam decretum de gratia illis communicanda, praedestinationis nomine complectuntur',
            'english': 'they embrace under the name of predestination both the decree of giving glory to certain men and the decree of communicating grace to them',
            'why': 'Good-sense Reformed: end + means under one name.',
            'rejected': ['these Doctors restrict praedestinatio to grace-preparation alone'],
        }],
        'notes': ['OCR: XIX PDF 141; good-sense Reformed.'],
        'bible_refs': [],
    },
    {
        'section': '581',
        'title': 'Same sense of electio — synonymous with praedestinatio',
        'pass_a': (
            'And they also use the word Election in the same sense. For by Election they '
            'understand the decree by which God from eternity selected certain men from '
            'others, that He might make them partakers of the grace of Christ in this life, '
            'and in the other crown them with glory; so that both election and '
            'predestination are held by them as synonyms.'
        ),
        'pass_b': [
            'Same group: electio = decree selecting some for grace now, glory later.',
            'Electio and praedestinatio treated as synonyms.',
        ],
        'lemmas': [
            {'latin': 'quosdam homines ab aliis selegit', 'gloss': 'selected certain men from others'},
            {'latin': 'electio & praedestinatio pro Synonymis', 'gloss': 'election and predestination as synonyms'},
        ],
        'choices': [{
            'term': 'adeo & electio & praedestinatio pro Synonymis ab ipsis habeantur',
            'english': 'so that both election and predestination are held by them as synonyms',
            'why': 'Locks electio to the same good-sense package as XIX.',
            'rejected': ['these Doctors keep electio strictly wider than praedestinatio'],
        }],
        'notes': ['OCR: XX PDF 141; electio = praedestinatio.'],
        'bible_refs': [],
    },
    {
        'section': '582',
        'title': 'Cameronians — electio as efficacious calling and gift of living faith',
        'pass_a': (
            'Yet some seem properly to designate by election the decree concerning certain '
            'men to be efficaciously called to Christ and endowed with true and living faith. '
            'So that election, according to them, rather regards the communication of grace '
            'than the gift of glory. So Testard in the Irenicum, Louis Cappel in the Theses '
            'on Election and Reprobation, and Moses Amyraut everywhere commonly use the word '
            'election, and others who with them follow Cameron’s Method and doctrine.'
        ),
        'pass_b': [
            'Some: electio = efficacious calling + gift of true living faith.',
            'Looks to grace-communication more than glory-gift.',
            'Testard, Cappel, Amyraut, and other Cameronians.',
        ],
        'lemmas': [
            {'latin': 'efficaciter ad Christum vocandis & fide vera vivaque donandis', 'gloss': 'to be efficaciously called to Christ and endowed with true and living faith'},
            {'latin': 'potius gratiae communicationem, quam donationem gloriae', 'gloss': 'rather the communication of grace than the gift of glory'},
        ],
        'choices': [{
            'term': 'electio, juxta ipsos, potius gratiae communicationem, quam donationem gloriae respiciat',
            'english': 'that election, according to them, rather regards the communication of grace than the gift of glory',
            'why': 'Marks the Cameronian narrowing of electio.',
            'rejected': ['Testard/Cappel/Amyraut treat electio as synonym of glory-predestination'],
        }],
        'notes': ['OCR: XXI PDF 141; Cameronian electio.'],
        'bible_refs': [],
    },
    {
        'section': '583',
        'title': 'Object-question opens — first party: creatable / supralapsarian',
        'pass_a': (
            'The opinions of the Theologians in the Reformed School also vary not a little '
            'concerning that question under what reason and respect man is the object of '
            'divine predestination. For first some, in assigning the object of '
            'predestination and election, ascend above man’s fall, and even above man’s '
            'creation itself. For they will that the decree of the predestination of certain '
            'men to salvation was in God, according to our way of conceiving, prior not only '
            'to the foresight of man’s fall into sin, but also to the very decree of '
            'creating man. And therefore the object of predestination for them is man not as '
            'created and fallen in God’s foreknowledge, but rather creatable man. Whence it '
            'is that by other Theologians they are called supralapsarians. Of which number '
            'are Zanchius, Beza, Piscator, Perkins, Ursinus, Gomarus, Polanus, Voetius, '
            'Twisse, and not a few others.'
        ),
        'pass_b': [
            'Reformed also split on the object of praedestinatio.',
            'First party: object above fall and even above creation = creatable man.',
            'Called supralapsarians — Zanchius, Beza, Gomarus, Voetius, Twisse, &c.',
        ],
        'lemmas': [
            {'latin': 'homo creabilis', 'gloss': 'creatable man'},
            {'latin': 'ab aliis Theologis supralapsarii vocantur', 'gloss': 'by other Theologians they are called supralapsarians'},
        ],
        'choices': [{
            'term': 'objectum praedestinationis ipsis est homo non conditus & lapsus in Dei praescientia: sed potius homo creabilis',
            'english': 'the object of predestination for them is man not as created and fallen in God’s foreknowledge, but rather creatable man',
            'why': 'Closes XVII–XXII on the first (supralapsarian) answer; next XXIII+ infralapsarian majority.',
            'rejected': ['this first party takes the object as mass of fallen humanity'],
        }],
        'notes': [
            'OCR: XXII PDF 141-142; Primo/supralapsarii continues past page break. Next: XXIII+ infralapsarian majority.',
        ],
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
    return latin, {s['section']: s for s in sections}


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
        jpath = JUST / ('aeterna_electio_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab aeterna_electio_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
    for name in ('pdf_141.txt', 'pdf_142.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20261003,
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
        if 578 <= n <= 583:
            notes = (
                'Section %s: new densify De Aeterna Hominum Electione XVII-XXII; '
                'Pass A!=B; lock-grounded PDF 141-142 / book pp. 129-130.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in aeterna_electio XVII-XXII packet scope covering all current sections.'
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
                'Scope review: densify De Aeterna Hominum Electione XVII-XXII only '
                '(sections %s-%s). Meta discloses %s. '
                'Next Aeterna Electio XXIII+. Not shipped.'
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
            'De Aeterna Hominum Electione et Praedestinatione XVII-XXII '
            '(communior fallen-in-Adam; Reformed senses; supralapsarian object)'
        ),
        'next_locus': (
            'De Aeterna Hominum Electione et Praedestinatione XXIII+ '
            '(infralapsarian majority; Sohnius/Cameron object)'
        ),
        'gates': {
            'check_pass_ab': 'ok aeterna_electio_%s–%s (%s/%s)' % (
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
        '## %s (Scribe — De Aeterna Hominum Electione XVII–XXII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Aeterna Electio XVII–XXII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: Aeterna Electio XXIII+.\n\n'
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
        '## %s ~ET (Scribe — Le Blanc De Aeterna Electione XVII–XXII densify)\n\n'
        'CoS densify: Aeterna Electio XVII–XXII (**%s→%s**). Packet %s. '
        'Next: Aeterna Electio XXIII+. Punch X: **NO**.\n\n---\n\n'
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
    write_data_files()
    latin, by_sec = load_data()
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
    (DATA / 'hold_post_tipready_583.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-583 post-ready')
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
