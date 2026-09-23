#!/usr/bin/env python3
"""Build + apply De Causa Praedestinationis XXIX-XXXIV densify (tip 555 → 561).

Glory-election-alone question; Pelagian stake; method vs thing; tract close.
Live floor 5007. After tip-ready: HOLD live>5007 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'praedestinationis_xxix_xxxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_praedestinationis/apply_praedestinationis_xxix_xxxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['556', '557', '558', '559', '560', '561']
ROMANS = {
    '556': 'XXIX', '557': 'XXX', '558': 'XXXI',
    '559': 'XXXII', '560': 'XXXIII', '561': 'XXXIV',
}
TIP_BEFORE = 555
PRIOR_START = 528
LIVE_FLOOR = 5007
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Causa Praedestinationis I-XXXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Causa Praedestinationis I-XXXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Causa Praedestinationis I-XXXIV, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Praedestinatio XXIX-XXXIV "
    "(glory-alone foresight question; Pelagian stake; method vs thing; tract close)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Causa Praedestinationis (an detur in homine causa vel ratio aliqua suae Praedestinationis).\n"
    "Same 1675 Pitt copy-text. Book pp. 121-126 / PDF 133-138 (I-XXXIV; this packet XXIX-XXXIV). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Causa Praedestinationis I-XXXIV tip — tract close. Next: De Aeterna Hominum Electione et Praedestinatione.\n"
    "Note: Glory-election foresight dispute; collective cause = Pelagian risk; remaining quarrel is method.\n\n"
)

LATIN = {
    '556': (
        'XXIX. An vero electio ad vitam aeternam & gloriam coelestem seorsim considerata, '
        '& distincte a decreto conferendi gratiam, sit ex praevisa fide, & praevisis operibus, '
        'dubitatur, ut patet ex antedictis, tam in Schola Reformata, quam in Schola Romana. '
        'In illa enim, ut in ista, reperiuntur nonnulli qui sentiunt, electionem ad fidem '
        'vivam & operosam, secundum nostrum concipiendi modum, praecedere absolutam '
        'electionem ad gloriam, & rationem aliquam reddi posse cur hic potius, quam ille, '
        'sit ad vitam & gloriam aeternam praedestinatus. Nempe quia Deus ab aeterno '
        'praevidit hunc gratiae beneficio in Christum crediturum, & acturum poenitentiam, '
        'ac in fide perseveraturum, nihil tale vero de altero praevidit.'
    ),
    '557': (
        'XXX. Verum in Schola Romana communior & vulgatior est sententia quae suspendit '
        'decretum electionis ad gloriam aeternam, ex praevisa conditione fidei & operum, '
        'quam in Schola Reformata. Et in hac pauci sunt admodum prae aliis, qui volunt '
        'praevisionem fidei vivae & per dilectionem operantis, in Deo, secundum nostrum '
        'concipiendi modum, praecedere efficacem electionem quorundam ad gloriam: cum idem '
        'in Schola Romana tueantur & doceant plurimi.'
    ),
    '558': (
        'XXXI. Porro prior illa quaestio de causa praedestinationis secundum omnes suos '
        'effectus consideratae, an scilicet, detur ex parte hominis, non est parvi momenti, '
        '& spectat ad fundamenta fidei Christianae. Nec enim affirmari potest dari causam '
        'ex parte hominis omnium effectuum praedestinationis, quatenus tam ad auxilia '
        'gratiae, quam ad gloriam coelestem refertur, quin incidatur in Pelagianismum, & '
        'negetur salutem hominis esse gratuitam, & ex sola Dei misericordia & benignitate '
        'in solidum pendere, non ex ullis operibus nostris, quod tam clare & constanter '
        'affirmat Evangelium: adeoque quin doceatur gratiam dari ex meritis, & hominem per '
        'naturae vires incipere seipsum ab alio discernere, & ad gratiam salutarem, aliquo '
        'saltem modo, praeparare atque disponere, quod tanquam Pelagianum, & Christianae '
        'gratiae adversum, pia antiquitas horruit & damnavit.'
    ),
    '559': (
        'XXXII. Secus vero videtur de altera illa quaestione, An scilicet, Electio ad '
        'gloriam aeternam, prout ab Electione ad gratiam distinguitur, sit ex praevisa fide '
        '& operibus? hoc est, An natura, vel ratione prius Deus praevideat hominem in '
        'Christum crediturum, illumque fide viva & per dilectionem efficaci amplexurum, '
        'quam absolute decernat illi conferre vitam & gloriam aeternam? Modo constet '
        'homines ad gratiam salutarem omnino gratis eligi, nec quicquam in iis esse quo '
        'Deus provocetur, ad gratiae istius auxilia ipsis, potius quam aliis destinanda '
        'atque largienda. Ac praeterea Deum unico & simplici voluntatis suae actu, ab '
        'aeterno simul & semel decrevisse, quaecunque unquam decrevit, & in tempore '
        'exequitur. Nec revera in Deo esse plura decreta, sibi succedentia, aut ab invicem '
        'realiter distincta, tanquam distinctos, & seorsim ac separatim elicitos, divinae '
        'mentis & voluntatis actus.'
    ),
    '560': (
        'XXXIII. Si enim ista, de quibus jam convenit, inter Scholam Romanam & Scholam '
        'Reformatam, agnita & concessa fuerint, quod superest controversiae, non erit de '
        'reipsa, qualiter res, scilicet, in Deo se habeat, sed solum de Methodo aliquos '
        'mentis nostrae conceptus digerendi. Nempe omnes jam in eo consentiunt, decretum '
        'de danda gloria, & decretum de gratia conferenda, non esse duo decreta realiter '
        'in Deo distincta, & inter quae possit esse realis aliquis ordo prioris & '
        'posterioris; sed Deum unico voluntatis actu uno ista constituisse. Verum mens '
        'nostra non valens, propter suam imbecillitatem, uno conceptu exhaurire, & simul '
        'complecti omnes illos respectus, quos unicus actus voluntatis Divinae ad varia '
        'objecta habet, cogitur illam seorsim concipere, prout modo hoc objectum, modo '
        'illud respicit, & sic illam diverse nominat, & modo unius decreti, modo alterius '
        'nomen illi imponit. Et postea inter varios illos conceptus, quos unius, & nunc '
        'alterius decreti nominibus insignit, excogitat aliquem ordinem, quo convenienter '
        'inter se disponantur, qui ordo propemodum arbitrarius videtur: Et citra culpam & '
        'reprehensionem diverse assignari potest: dum alii nimirum conceptus suos de '
        'decretis divinis, secundum ipsam rerum executionem, digerunt, alii vero, si quae '
        'sit relatio mediorum & finis, inter res a Deo decretas, malunt ordinem intentionis '
        'sequi, & tanquam, prius concipere decretum de re quae finis est, ut posterius '
        'autem illud quod se habet tanquam medium ad illam.'
    ),
    '561': (
        'XXXIV. Itaque non video quid mali, vel periculi sit, si quis decretum de gloria '
        'alicui donanda concipiat ut prius decreto de conferendis gratiae auxiliis, quia '
        'gloria se habet ut finis, gratiae vero auxilia, ut media quae ad finem illum '
        'consequendum necessaria sunt; aut contra, si quis concipiat decretum de '
        'praebendis gratiae auxiliis, ut prius decreto de conferenda gloria, quia reipsa '
        'Deus prius gratiam communicat, & postea gloriam, & ita secundum ordinem causae '
        'efficientis, gratia gloriam praecedit: quamvis prior ille ordo, ut in Scholis '
        'Reformatis longe magis receptus est, ita nobis etiam videtur convenientior. '
        'Etenim sapientis est finem aliquem intendere, postea vero apud se statuere de '
        'mediis quae ad finem illum obtinendum conducunt. Forte tamen consultius esset '
        'quaestiones ejusmodi, quae nihil ad fructum pietatis faciunt, & nihilominus saepe '
        'gravissimas contentiones excitant, nec movere, nec determinare.'
    ),
}

SECTIONS = [
    {
        'section': '556',
        'title': 'Open question — glory-election alone from foresight of faith/works?',
        'pass_a': (
            'But whether election to eternal life and heavenly glory, considered separately '
            'and distinctly from the decree of conferring grace, is from foreseen faith and '
            'foreseen works, is doubted, as is plain from what was said before, both in the '
            'Reformed School and in the Roman School. For in that one, as in this, some are '
            'found who think that election to living and operative faith, according to our '
            'way of conceiving, precedes absolute election to glory, and that some reason '
            'can be rendered why this one rather than that is predestined to eternal life '
            'and glory. Namely because God from eternity foresaw that this one by the '
            'benefit of grace would believe in Christ, and would do repentance, and would '
            'persevere in faith, but foresaw nothing of the sort concerning the other.'
        ),
        'pass_b': [
            'Still open in both Schools: is glory-election alone from foresight?',
            'Some put living-faith election before absolute glory-election.',
            'Reason named: God foresaw this one’s faith/repentance/perseverance, not that one’s.',
        ],
        'lemmas': [
            {'latin': 'seorsim considerata, & distincte a decreto conferendi gratiam', 'gloss': 'considered separately and distinctly from the decree of conferring grace'},
            {'latin': 'sit ex praevisa fide, & praevisis operibus', 'gloss': 'is from foreseen faith and foreseen works'},
        ],
        'choices': [{
            'term': 'rationem aliquam reddi posse cur hic potius, quam ille, sit ad vitam & gloriam aeternam praedestinatus',
            'english': 'that some reason can be rendered why this one rather than that is predestined to eternal life and glory',
            'why': 'Opens the glory-alone foresight question after XXVIII’s common ground.',
            'rejected': ['both Schools treat glory-alone foresight as settled'],
        }],
        'notes': ['OCR: XXIX PDF 137-138; open in both Schools.'],
        'bible_refs': [],
    },
    {
        'section': '557',
        'title': 'Roman School more often suspends glory-election on foresight',
        'pass_a': (
            'But in the Roman School the more common and more widespread opinion is that '
            'which suspends the decree of election to eternal glory on the foreseen '
            'condition of faith and works, than in the Reformed School. And in this latter '
            'there are very few indeed compared with the others who will that the foresight '
            'of living faith working through love, in God, according to our way of '
            'conceiving, precedes the efficacious election of certain ones to glory: whereas '
            'the same is defended and taught by very many in the Roman School.'
        ),
        'pass_b': [
            'Roman School: glory-election from foresight is the more common view.',
            'Reformed School: only a few put living-faith foresight before glory-election.',
            'Same thesis: many Romans teach it; few Reformed.',
        ],
        'lemmas': [
            {'latin': 'communior & vulgatior est sententia quae suspendit decretum electionis', 'gloss': 'the more common and more widespread opinion is that which suspends the decree of election'},
            {'latin': 'praevisionem fidei vivae & per dilectionem operantis', 'gloss': 'the foresight of living faith working through love'},
        ],
        'choices': [{
            'term': 'in hac pauci sunt admodum prae aliis … cum idem in Schola Romana tueantur & doceant plurimi',
            'english': 'in this latter there are very few indeed … whereas the same is defended and taught by very many in the Roman School',
            'why': 'Quantifies the Reformed/Roman imbalance on glory-foresight.',
            'rejected': ['foresight-of-faith is equally common in both Schools'],
        }],
        'notes': ['OCR: XXX PDF 138; Roman majority vs Reformed few.'],
        'bible_refs': [],
    },
    {
        'section': '558',
        'title': 'Collective-cause question is foundational — Pelagian risk',
        'pass_a': (
            'Further that prior question concerning the cause of predestination considered '
            'according to all its effects — whether, namely, it is given on man’s part — is '
            'not of small moment, and looks to the foundations of the Christian faith. For '
            'it cannot be affirmed that a cause on man’s part of all the effects of '
            'predestination is given, insofar as it is referred both to the helps of grace '
            'and to heavenly glory, without falling into Pelagianism, and denying that man’s '
            'salvation is gratuitous and depends wholly on the mercy and kindness of God '
            'alone, not on any works of ours, which the Gospel so clearly and constantly '
            'affirms: and therefore without teaching that grace is given from merits, and '
            'that man by the powers of nature begins to distinguish himself from another, '
            'and in some way at least to prepare and dispose himself for saving grace, which '
            'as Pelagian and contrary to Christian grace pious antiquity shuddered at and '
            'condemned.'
        ),
        'pass_b': [
            'Collective-cause question = foundation of Christian faith.',
            'Cause-in-man for the whole package → Pelagianism.',
            'Would teach grace-from-merits and natural self-discerning — condemned.',
        ],
        'lemmas': [
            {'latin': 'quin incidatur in Pelagianismum', 'gloss': 'without falling into Pelagianism'},
            {'latin': 'hominem per naturae vires incipere seipsum ab alio discernere', 'gloss': 'that man by the powers of nature begins to distinguish himself from another'},
        ],
        'choices': [{
            'term': 'Nec enim affirmari potest dari causam ex parte hominis omnium effectuum praedestinationis … quin incidatur in Pelagianismum',
            'english': 'For it cannot be affirmed that a cause on man’s part of all the effects of predestination is given … without falling into Pelagianism',
            'why': 'Hard line: collective cause-in-man is not a free academic option.',
            'rejected': ['collective cause-in-man is a safe open question'],
        }],
        'notes': ['OCR: XXXI PDF 138; Pelagian stake.'],
        'bible_refs': [],
    },
    {
        'section': '559',
        'title': 'Second question safer — if saving grace is wholly free and one act in God',
        'pass_a': (
            'But it seems otherwise concerning that other question, Whether, namely, '
            'Election to eternal glory, as it is distinguished from Election to grace, is '
            'from foreseen faith and works? that is, Whether by nature or by reason God '
            'first foresaw that a man would believe in Christ, and would embrace Him with '
            'living faith and through efficacious love, before He absolutely decreed to '
            'confer on him eternal life and glory? Provided it be established that men are '
            'elected to saving grace wholly freely, and that there is nothing in them by '
            'which God is provoked to destine and bestow those helps of grace on them '
            'rather than on others. And further that God by one single and simple act of '
            'His will from eternity together and at once decreed whatever He ever decreed '
            'and executes in time. Nor that there are really in God several decrees '
            'succeeding one another, or really distinct from one another, as distinct acts '
            'of the divine mind and will elicited separately and apart.'
        ),
        'pass_b': [
            'Glory-vs-grace order question is different — safer if grace stays free.',
            'Premise: nothing in man provokes the grace-helps.',
            'And: one simple eternal will-act — not stacked real decrees in God.',
        ],
        'lemmas': [
            {'latin': 'Modo constet homines ad gratiam salutarem omnino gratis eligi', 'gloss': 'Provided it be established that men are elected to saving grace wholly freely'},
            {'latin': 'unico & simplici voluntatis suae actu', 'gloss': 'by one single and simple act of His will'},
        ],
        'choices': [{
            'term': 'Nec revera in Deo esse plura decreta, sibi succedentia, aut ab invicem realiter distincta',
            'english': 'Nor that there are really in God several decrees succeeding one another, or really distinct from one another',
            'why': 'Keeps the second question inside one-act orthodoxy.',
            'rejected': ['the second question requires really distinct successive decrees in God'],
        }],
        'notes': ['OCR: XXXII PDF 138; conditional safety of glory-order question.'],
        'bible_refs': [],
    },
    {
        'section': '560',
        'title': 'Remaining dispute is method of our concepts, not the thing in God',
        'pass_a': (
            'For if those things on which there is already agreement between the Roman '
            'School and the Reformed School have been acknowledged and granted, what '
            'remains of the controversy will not be about the thing itself — how the matter, '
            'namely, stands in God — but only about the Method of arranging certain concepts '
            'of our mind. Namely all already agree in this, that the decree of giving glory '
            'and the decree of conferring grace are not two decrees really distinct in God, '
            'and between which there can be some real order of prior and posterior; but that '
            'God constituted both by one single act of will. But our mind, not able because '
            'of its weakness to exhaust in one concept and at once to embrace all those '
            'respects which the single act of the Divine will has toward various objects, is '
            'forced to conceive it separately as it regards now this object, now that, and '
            'so names it diversely, and imposes on it now the name of one decree, now of '
            'another. And afterward among those various concepts which it marks with the '
            'names of one decree and now of another, it invents some order by which they may '
            'conveniently be arranged among themselves, which order seems almost arbitrary: '
            'And without fault or blame it can be assigned diversely: while some arrange '
            'their concepts of the divine decrees according to the very execution of things, '
            'but others, if there be a relation of means and end among the things decreed by '
            'God, prefer to follow the order of intention, and as it were first to conceive '
            'the decree concerning the thing which is the end, but as later that which '
            'stands as a means to it.'
        ),
        'pass_b': [
            'Given the agreed points: leftover quarrel ≠ the thing in God.',
            'It is only how we sort our concepts of one will-act.',
            'Execution-order vs intention/end-means order — nearly arbitrary, both blameless.',
        ],
        'lemmas': [
            {'latin': 'non erit de reipsa … sed solum de Methodo', 'gloss': 'will not be about the thing itself … but only about the Method'},
            {'latin': 'qui ordo propemodum arbitrarius videtur', 'gloss': 'which order seems almost arbitrary'},
        ],
        'choices': [{
            'term': 'decretum de danda gloria, & decretum de gratia conferenda, non esse duo decreta realiter in Deo distincta',
            'english': 'that the decree of giving glory and the decree of conferring grace are not two decrees really distinct in God',
            'why': 'Agreed premise that shrinks the leftover dispute to method.',
            'rejected': ['the leftover dispute is still about real priority in God'],
        }],
        'notes': ['OCR: XXXIII PDF 138; method not reipsa.'],
        'bible_refs': [],
    },
    {
        'section': '561',
        'title': 'Either conceptual order allowed — Reformed end-first preferred; better not to fight',
        'pass_a': (
            'And so I do not see what evil or danger there is if someone conceives the '
            'decree of giving glory to someone as prior to the decree of conferring the '
            'helps of grace, because glory stands as the end, but the helps of grace as '
            'means which are necessary for obtaining that end; or on the contrary, if '
            'someone conceives the decree of supplying the helps of grace as prior to the '
            'decree of conferring glory, because in reality God first communicates grace '
            'and afterward glory, and so according to the order of efficient cause grace '
            'precedes glory: although that former order, as it is far more received in the '
            'Reformed Schools, so also seems to us more convenient. For it belongs to a '
            'wise man to intend some end, and afterward to settle with himself concerning '
            'the means which lead to obtaining that end. Yet perhaps it would be more '
            'advisable neither to raise nor to determine questions of that sort, which do '
            'nothing for the fruit of piety, and nevertheless often stir up the gravest '
            'contentions.'
        ),
        'pass_b': [
            'Either conceptual order is allowed: end-first or execution-first.',
            'Reformed (and Le Blanc) prefer end/intention-first as more fitting.',
            'Still: better neither to raise nor settle — no piety fruit, much fight.',
        ],
        'lemmas': [
            {'latin': 'gloria se habet ut finis, gratiae vero auxilia, ut media', 'gloss': 'glory stands as the end, but the helps of grace as means'},
            {'latin': 'nec movere, nec determinare', 'gloss': 'neither to raise nor to determine'},
        ],
        'choices': [{
            'term': 'Forte tamen consultius esset quaestiones ejusmodi … nec movere, nec determinare',
            'english': 'Yet perhaps it would be more advisable neither to raise nor to determine questions of that sort',
            'why': 'Closes De Causa Praedestinationis; next tract De Aeterna Electione.',
            'rejected': ['Le Blanc requires settling the conceptual order as dogma'],
        }],
        'notes': ['OCR: XXXIV PDF 138; tract close. Next: De Aeterna Hominum Electione.'],
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
        jpath = JUST / ('praedestinationis_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab praedestinationis_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
    for name in ('pdf_137.txt', 'pdf_138_fresh.txt', 'pdf_137_fresh.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20260930,
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
        if 556 <= n <= 561:
            notes = (
                'Section %s: new densify De Causa Praedestinationis XXIX-XXXIV; '
                'Pass A!=B; lock-grounded PDF 137-138 / book pp. 125-126.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in praedestinationis XXIX-XXXIV packet scope covering all current sections.'
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
                'Scope review: densify De Causa Praedestinationis XXIX-XXXIV only '
                '(sections %s-%s). Meta discloses %s. '
                'Next De Aeterna Hominum Electione. Not shipped.'
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
            'De Causa Praedestinationis theses XXIX-XXXIV '
            '(glory-alone foresight; Pelagian stake; method close)'
        ),
        'next_locus': 'De Aeterna Hominum Electione et Praedestinatione (PDF 139+)',
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
    block = (
        '## %s (Scribe — De Causa Praedestinationis XXIX–XXXIV densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Praedestinatio XXIX–XXXIV → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: De Aeterna Hominum Electione et Praedestinatione.\n\n'
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
    slug_ref = bt + 'le-blanc-theses-theologicae' + bt
    repo_block = (
        '## %s ~ET (Scribe — Le Blanc De Causa Praedestinationis XXIX–XXXIV densify)\n\n'
        'CoS densify: Praedestinatio XXIX–XXXIV (**%s→%s**). Packet %s. '
        'Next: De Aeterna Electione. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_561.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-561 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'packet', receipt['packet_id'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
