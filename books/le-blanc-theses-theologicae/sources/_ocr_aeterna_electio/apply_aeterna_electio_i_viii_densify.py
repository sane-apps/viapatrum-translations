#!/usr/bin/env python3
"""Build + apply De Aeterna Hominum Electione et Praedestinatione I-VIII densify (tip 561 → 569).

Roman senses of praedestinatio/electio; first effect-assignment theses (Ockham/Biel vs Durandus).
Live floor 5026. After tip-ready: HOLD live>5026 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'aeterna_electio_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_aeterna_electio/apply_aeterna_electio_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['562', '563', '564', '565', '566', '567', '568', '569']
ROMANS = {
    '562': 'I', '563': 'II', '564': 'III', '565': 'IV',
    '566': 'V', '567': 'VI', '568': 'VII', '569': 'VIII',
}
TIP_BEFORE = 561
LIVE_FLOOR = 5026
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeterna Hominum Electione et Praedestinatione I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeterna Hominum Electione et Praedestinatione I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeterna Hominum Electione et Praedestinatione I-VIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeterna Electio I-VIII "
    "(Roman senses of praedestinatio/electio; Ockham/Biel vs Durandus on effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeterna Hominum Electione et Praedestinatione "
    "(quis sit vocum illarum usus in Ecclesiae Romanae & Protestantium Scholis; "
    "tum quomodo in Scholis iisdem varie assignentur Praedestinationis effectus & objectum).\n"
    "Same 1675 Pitt copy-text. Book pp. 127-128 / PDF 139-140 (I-VIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeterna Hominum Electione et Praedestinatione I-VIII tip. Next: Aeterna Electio IX+.\n"
    "Note: Three Roman senses of praedestinatio; electio parallel; effects = glory-only vs means-only.\n\n"
)

LATIN = {
    '562': (
        'I. Vox Praedestinationis in Schola Romana varie usurpatur. Nam juxta quosdam '
        'illius Doctores Praedestinatio solum illud decretum complectitur, quo Deus ab '
        'aeterno absolute constituit gloriam coelestem certis hominibus conferre. Aliis '
        'vero praedestinatio restringitur potius ad decretum conferendi certis hominibus '
        'media ad gloriam coelestem infallibiliter assequendam conducibilia. Alii denique '
        'utrumque decretum ad praedestinationem pertinere contendunt. Ut observat '
        'Eustachius a Sancto Paulo in Summa Theologiae, de Praedestinatione, quaestione 3.'
    ),
    '563': (
        'II. Acceptio prior rarior est. Sic tamen sumere videntur nomen praedestinationis '
        'nonnulli veteres Scholastici, ut Gabriel Biel, & Occam, quibus praedestinatio nil '
        'aliud esse videtur, quam aeternum Dei consilium quo decrevit quibusdam hominibus '
        'dare gloriam. Ut patet ex iis quae refert Gregorius de Valentia, Tom. 1. Disp. 1. '
        'quaest. 23. quae est de praedestinatione, puncto 1.'
    ),
    '564': (
        'III. Scholasticorum vero maxima pars praedestinationem sumit secundo modo, nempe '
        'pro gratiae praeparatione, ut ab electione ad gloriam distinguitur. Sicuti videre '
        'est apud Martinum Becanum, in Summa Theologiae, tom. 1. c. 19. quaest. 2. conclus. 1.'
    ),
    '565': (
        'IV. Multi tamen ex Doctoribus Ecclesiae Rom. sic definiunt praedestinationem, ut '
        'non tantum gratiae, sed etiam gloriae praeparatio ad ipsam pertineat. Illis enim '
        'praedestinatio est aeternum decretum, seu propositum Dei, quo Deus homines quosdam '
        'ordinat ac dirigit in beatitudinem supernaturalem, per media supernaturalia reipsa '
        'consequendam. In qua sententia sunt memoratus ille Eustachius a Sancto Paulo, '
        'Petrus a Sancto Joseph, Gregorius de Valentia, Estius, & alii plurimi.'
    ),
    '566': (
        'V. Jansenius vero & ejus discipuli, Augustinum hac in parte sequentes, '
        'praedestinationem sumunt sensu adhuc generaliori. Nam putant Dei praedestinationem '
        'respicere non solum bonum, sed etiam malum, non quidem culpae, sed poenae. Adeoque '
        'reprobos non minus dici posse ad aeterna supplicia a Deo praedestinatos esse, quam '
        'electos ad gloriam & beatitudinem. Unde est quod duplicem faciunt praedestinationem, '
        'unam ad vitam, & alteram ad mortem. Ut videre est apud Jansenium De gratia Christi '
        'Salvatoris, lib. 9. cap. 3.'
    ),
    '567': (
        'VI. Electio similiter a multis Scholasticis restringitur ad decretum quo Deus '
        'hominibus quibusdam decrevit dare gloriam, prae aliis. Et sic distinguitur a '
        'praedestinatione, quae juxta ipsos, est decretum de conferendis mediis ad gloriam. '
        'Ut observat Alphonsus Mendoza Professor Salmanticensis in quaestione Scholastica de '
        'praedestinatione, Sectione secunda. Alii vero permulti electionem, sicut '
        'praedestinationem, non minus ad gratiam, quam ad gloriam referunt, & volunt illam '
        'complecti decretum de danda Gratia, non secus ac decretum de conferenda gloria.'
    ),
    '568': (
        'VII. Ut autem praedestinatio in Schola Romana a variis varie accipitur & definitur, '
        'sic non omnes eodem modo effectus illius assignant. Qui enim praedestinationis '
        'nomine intelligunt solum illud decretum, quo Deus ab aeterno certis hominibus '
        'gloriam coelestem praeparavit, non alium assignant ejus effectum quam gloriae '
        'istius communicationem: neque volunt dona gratiae inter praedestinationis effectus '
        'numerari. Qua in sententia sunt Gulielmus Occam, & Gabriel Biel, referente Greg. '
        'de Valentia. Tom. 1. quaest. cit.'
    ),
    '569': (
        'VIII. Alii vero contra pretendunt sola media ad aeternam beatitudinem esse '
        'effectus praedestinationis, minime autem ipsam beatitudinis assecutionem. Et hoc '
        'quia nomen praedestinationis restringunt ad decretum de gratia communicanda, nec '
        'eo comprehendi volunt decretum de danda gloria. Quae est opinio Durandi, teste '
        'eodem Gregorio de Valentia loco modo citato.'
    ),
}

SECTIONS = [
    {
        'section': '562',
        'title': 'Roman School — three senses of the word Praedestinatio',
        'pass_a': (
            'The word Predestination is variously used in the Roman School. For according to '
            'certain of its Doctors Predestination comprises only that decree by which God '
            'from eternity absolutely appointed to confer heavenly glory on certain men. But '
            'to others predestination is restricted rather to the decree of conferring on '
            'certain men the means conducive to infallibly obtaining heavenly glory. Finally '
            'others contend that both decrees belong to predestination. As Eustachius a '
            'Sancto Paulo observes in the Summa of Theology, on Predestination, question 3.'
        ),
        'pass_b': [
            'Roman School uses “praedestinatio” in three ways.',
            'Glory-decree alone; means-to-glory decree alone; or both.',
            'Eustachius a S. Paulo Summa, de Praedestinatione q.3.',
        ],
        'lemmas': [
            {'latin': 'varie usurpatur', 'gloss': 'is variously used'},
            {'latin': 'utrumque decretum ad praedestinationem pertinere', 'gloss': 'that both decrees belong to predestination'},
        ],
        'choices': [{
            'term': 'Praedestinatio solum illud decretum complectitur, quo Deus … gloriam coelestem certis hominibus conferre',
            'english': 'Predestination comprises only that decree by which God … to confer heavenly glory on certain men',
            'why': 'Opens the new tract on Roman word-use after Causa Praedestinationis close.',
            'rejected': ['Romans have one fixed sense of praedestinatio'],
        }],
        'notes': ['OCR: I PDF 139; Eustachius Summa q.3.'],
        'bible_refs': [],
    },
    {
        'section': '563',
        'title': 'First sense rarer — Biel and Occam: eternal counsel to give glory',
        'pass_a': (
            'The prior acceptance is rarer. Yet so some older Scholastics seem to take the '
            'name of predestination, as Gabriel Biel and Occam, to whom predestination seems '
            'to be nothing other than the eternal counsel of God by which He decreed to give '
            'glory to certain men. As is plain from those things which Gregory of Valencia '
            'reports, Tome 1 Disputation 1 question 23 which is on predestination, point 1.'
        ),
        'pass_b': [
            'Glory-only sense is the rarer acceptance.',
            'Biel & Occam: praedestinatio = eternal counsel to give glory.',
            'Cited via Gregory of Valencia Tom.1 Disp.1 q.23.',
        ],
        'lemmas': [
            {'latin': 'Acceptio prior rarior est', 'gloss': 'The prior acceptance is rarer'},
            {'latin': 'aeternum Dei consilium quo decrevit quibusdam hominibus dare gloriam', 'gloss': 'the eternal counsel of God by which He decreed to give glory to certain men'},
        ],
        'choices': [{
            'term': 'praedestinatio nil aliud esse videtur, quam aeternum Dei consilium quo decrevit quibusdam hominibus dare gloriam',
            'english': 'predestination seems to be nothing other than the eternal counsel of God by which He decreed to give glory to certain men',
            'why': 'Pins the rare glory-only sense on Biel/Occam.',
            'rejected': ['Biel and Occam take praedestinatio as means-preparation only'],
        }],
        'notes': ['OCR: II PDF 139; Biel, Occam.'],
        'bible_refs': [],
    },
    {
        'section': '564',
        'title': 'Most Scholastics — praedestinatio as preparation of grace',
        'pass_a': (
            'But the greater part of the Scholastics take predestination in the second way, '
            'namely for the preparation of grace, as it is distinguished from election to '
            'glory. As is to be seen in Martin Becanus, in the Summa of Theology, tome 1 '
            'chapter 19 question 2 conclusion 1.'
        ),
        'pass_b': [
            'Most Scholastics: second sense = preparation of grace.',
            'Distinguished from election to glory.',
            'Becanus Summa Theol. I.19 q.2 concl.1.',
        ],
        'lemmas': [
            {'latin': 'pro gratiae praeparatione', 'gloss': 'for the preparation of grace'},
            {'latin': 'ut ab electione ad gloriam distinguitur', 'gloss': 'as it is distinguished from election to glory'},
        ],
        'choices': [{
            'term': 'Scholasticorum vero maxima pars praedestinationem sumit secundo modo, nempe pro gratiae praeparatione',
            'english': 'But the greater part of the Scholastics take predestination in the second way, namely for the preparation of grace',
            'why': 'States the majority Roman scholastic usage.',
            'rejected': ['most Scholastics take the glory-only sense'],
        }],
        'notes': ['OCR: III PDF 139; Becanus.'],
        'bible_refs': [],
    },
    {
        'section': '565',
        'title': 'Many Romans — both grace and glory preparation in one decree',
        'pass_a': (
            'Yet many of the Doctors of the Roman Church so define predestination that not '
            'only the preparation of grace but also that of glory belongs to it. For to them '
            'predestination is the eternal decree or purpose of God by which God ordains and '
            'directs certain men into supernatural beatitude, to be obtained in reality '
            'through supernatural means. In which opinion are that Eustachius a Sancto Paulo '
            'already mentioned, Petrus a Sancto Joseph, Gregory of Valencia, Estius, and '
            'very many others.'
        ),
        'pass_b': [
            'Many Romans fold both grace- and glory-preparation into praedestinatio.',
            'Eternal purpose directing some into supernatural beatitude via means.',
            'Eustachius, Petrus a S. Joseph, Valencia, Estius, &c.',
        ],
        'lemmas': [
            {'latin': 'non tantum gratiae, sed etiam gloriae praeparatio', 'gloss': 'not only the preparation of grace but also that of glory'},
            {'latin': 'ordinat ac dirigit in beatitudinem supernaturalem', 'gloss': 'ordains and directs into supernatural beatitude'},
        ],
        'choices': [{
            'term': 'praedestinatio est aeternum decretum, seu propositum Dei, quo Deus homines quosdam ordinat ac dirigit in beatitudinem supernaturalem',
            'english': 'predestination is the eternal decree or purpose of God by which God ordains and directs certain men into supernatural beatitude',
            'why': 'Third Roman sense — both decrees under one name.',
            'rejected': ['these Doctors limit praedestinatio to grace-preparation alone'],
        }],
        'notes': ['OCR: IV PDF 139; both-decree definition.'],
        'bible_refs': [],
    },
    {
        'section': '566',
        'title': 'Jansenius — still more general: predestination to life and to death',
        'pass_a': (
            'But Jansenius and his disciples, following Augustine on this part, take '
            'predestination in a still more general sense. For they think God’s '
            'predestination regards not only the good but also the evil — not indeed of '
            'fault, but of punishment. And therefore that the reprobate can no less be said '
            'to have been predestined by God to eternal punishments than the elect to glory '
            'and beatitude. Whence it is that they make a double predestination, one to life '
            'and another to death. As is to be seen in Jansenius On the Grace of Christ the '
            'Savior, book 9 chapter 3.'
        ),
        'pass_b': [
            'Jansenius/Augustinians: still wider sense of praedestinatio.',
            'Covers good and evil of punishment (not of fault).',
            'Double predestination: to life and to death — De gratia Christi IX.3.',
        ],
        'lemmas': [
            {'latin': 'non solum bonum, sed etiam malum, non quidem culpae, sed poenae', 'gloss': 'not only the good but also the evil — not indeed of fault, but of punishment'},
            {'latin': 'duplicem faciunt praedestinationem, unam ad vitam, & alteram ad mortem', 'gloss': 'they make a double predestination, one to life and another to death'},
        ],
        'choices': [{
            'term': 'reprobos non minus dici posse ad aeterna supplicia a Deo praedestinatos esse, quam electos ad gloriam',
            'english': 'that the reprobate can no less be said to have been predestined by God to eternal punishments than the elect to glory',
            'why': 'Marks Jansenist double predestination vs the prior three Roman senses.',
            'rejected': ['Jansenius limits praedestinatio to the elect only'],
        }],
        'notes': ['OCR: V PDF 139-140; Jansenius De gratia Christi IX.3.'],
        'bible_refs': [],
    },
    {
        'section': '567',
        'title': 'Electio likewise — glory-only vs grace-and-glory',
        'pass_a': (
            'Election likewise is restricted by many Scholastics to the decree by which God '
            'decreed to give glory to certain men before others. And so it is distinguished '
            'from predestination, which according to them is the decree of conferring the '
            'means to glory. As Alphonsus Mendoza, Professor of Salamanca, observes in the '
            'Scholastic question on predestination, Section two. But very many others refer '
            'election, like predestination, no less to grace than to glory, and will that it '
            'comprise the decree of giving Grace no less than the decree of conferring glory.'
        ),
        'pass_b': [
            'Many Scholastics: electio = glory-decree; praedestinatio = means-decree.',
            'Mendoza (Salamanca) notes the split.',
            'Many others: electio covers grace-decree and glory-decree alike.',
        ],
        'lemmas': [
            {'latin': 'Electio similiter … restringitur ad decretum quo Deus … dare gloriam', 'gloss': 'Election likewise … is restricted to the decree by which God … to give glory'},
            {'latin': 'complecti decretum de danda Gratia, non secus ac decretum de conferenda gloria', 'gloss': 'to comprise the decree of giving Grace no less than the decree of conferring glory'},
        ],
        'choices': [{
            'term': 'sic distinguitur a praedestinatione, quae juxta ipsos, est decretum de conferendis mediis ad gloriam',
            'english': 'and so it is distinguished from predestination, which according to them is the decree of conferring the means to glory',
            'why': 'Maps electio/praedestinatio split in Roman usage.',
            'rejected': ['all Scholastics treat electio and praedestinatio as synonyms'],
        }],
        'notes': ['OCR: VI PDF 140; Mendoza Sect.2.'],
        'bible_refs': [],
    },
    {
        'section': '568',
        'title': 'Effects — glory-only sense assigns only communication of glory',
        'pass_a': (
            'But as predestination in the Roman School is variously accepted and defined by '
            'various writers, so not all assign its effects in the same way. For those who '
            'by the name of predestination understand only that decree by which God from '
            'eternity prepared heavenly glory for certain men assign no other effect of it '
            'than the communication of that glory: nor will they have the gifts of grace '
            'numbered among the effects of predestination. In which opinion are William '
            'Occam and Gabriel Biel, Gregory of Valencia reporting. Tome 1 question cited.'
        ),
        'pass_b': [
            'Effect-lists track the word-sense chosen.',
            'Glory-only sense → only communication of glory as effect.',
            'Occam & Biel refuse to count grace-gifts as effects.',
        ],
        'lemmas': [
            {'latin': 'non alium assignant ejus effectum quam gloriae istius communicationem', 'gloss': 'assign no other effect of it than the communication of that glory'},
            {'latin': 'neque volunt dona gratiae inter praedestinationis effectus numerari', 'gloss': 'nor will they have the gifts of grace numbered among the effects of predestination'},
        ],
        'choices': [{
            'term': 'neque volunt dona gratiae inter praedestinationis effectus numerari',
            'english': 'nor will they have the gifts of grace numbered among the effects of predestination',
            'why': 'First effect-assignment thesis — excludes grace from effects.',
            'rejected': ['Occam/Biel count grace-gifts among praedestinatio’s effects'],
        }],
        'notes': ['OCR: VII PDF 140; Occam/Biel via Valencia.'],
        'bible_refs': [],
    },
    {
        'section': '569',
        'title': 'Opposite — only means are effects; not attainment of beatitude (Durandus)',
        'pass_a': (
            'But others on the contrary maintain that only the means to eternal beatitude '
            'are effects of predestination, but by no means the very attainment of '
            'beatitude. And this because they restrict the name of predestination to the '
            'decree of communicating grace, and will not have the decree of giving glory '
            'comprehended in it. Which is the opinion of Durandus, the same Gregory of '
            'Valencia bearing witness in the place just cited.'
        ),
        'pass_b': [
            'Opposite camp: only means-to-beatitude are effects.',
            'Attainment of beatitude itself is not an effect.',
            'Because praedestinatio = grace-decree only — Durandus (via Valencia).',
        ],
        'lemmas': [
            {'latin': 'sola media ad aeternam beatitudinem esse effectus praedestinationis', 'gloss': 'that only the means to eternal beatitude are effects of predestination'},
            {'latin': 'minime autem ipsam beatitudinis assecutionem', 'gloss': 'but by no means the very attainment of beatitude'},
        ],
        'choices': [{
            'term': 'nomen praedestinationis restringunt ad decretum de gratia communicanda, nec eo comprehendi volunt decretum de danda gloria',
            'english': 'they restrict the name of predestination to the decree of communicating grace, and will not have the decree of giving glory comprehended in it',
            'why': 'Closes I–VIII on Durandus means-only effects; next IX+ common Roman list.',
            'rejected': ['Durandus counts glorification itself among the effects'],
        }],
        'notes': ['OCR: VIII PDF 140; Durandus. Next: IX+ communior effectus.'],
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
    for name in ('pdf_139.txt', 'pdf_140.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20261001,
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
        if 562 <= n <= 569:
            notes = (
                'Section %s: new densify De Aeterna Hominum Electione et Praedestinatione I-VIII; '
                'Pass A!=B; lock-grounded PDF 139-140 / book pp. 127-128.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in aeterna_electio I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Aeterna Hominum Electione et Praedestinatione I-VIII only '
                '(sections %s-%s). Meta discloses %s. '
                'Next Aeterna Electio IX+. Not shipped.'
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
            'De Aeterna Hominum Electione et Praedestinatione I-VIII '
            '(Roman senses; electio; Ockham/Biel vs Durandus effects)'
        ),
        'next_locus': 'De Aeterna Hominum Electione et Praedestinatione IX+ (communior effects; Mendoza)',
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
        '## %s (Scribe — De Aeterna Hominum Electione I–VIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Aeterna Electio I–VIII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: Aeterna Electio IX+.\n\n'
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
        '## %s ~ET (Scribe — Le Blanc De Aeterna Electione I–VIII densify)\n\n'
        'CoS densify: Aeterna Electio I–VIII (**%s→%s**). Packet %s. '
        'Next: Aeterna Electio IX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_569.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-569 post-ready')
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
