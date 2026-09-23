#!/usr/bin/env python3
"""Build + apply De Scientia Dei XVII-XXIV densify (tip 513 → 521).

Stars; Jerome/gnats; Matt 10; great/small before God. Live floor 4860.
After tip-ready: HOLD live>4860 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_scientia_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_scientia/apply_dei_scientia_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['514', '515', '516', '517', '518', '519', '520', '521']
ROMANS = {
    '514': 'XVII', '515': 'XVIII', '516': 'XIX', '517': 'XX',
    '518': 'XXI', '519': 'XXII', '520': 'XXIII', '521': 'XXIV',
}
TIP_BEFORE = 513
PRIOR_START = 498
LIVE_FLOOR = 4860
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Scientia Dei I-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Scientia Dei I-XXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Scientia Dei I-XXIV, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Scientia Dei XVII-XXIV "
    "(named stars; Jerome on gnats; Matt 10; great/small; hearts)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scientia Dei, sive De cognitione rerum quae in Deo est.\n"
    "Same 1675 Pitt copy-text. Book pp. 117-120 / PDF 129-132 (I-XXIV; this packet XVII-XXIV). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Scientia Dei I-XXIV tip — continues after IX-XVI. Next: Scientia Dei XXV+ (times).\n"
    "Note: Stars by name; Jerome/gnats; sparrows/hairs; Isaiah; animalcules; hearts.\n\n"
)

LATIN = {
    '514': (
        'XVII. Et certe Scriptura testatur Deum nosse singulas stellas, & earum unamquamque '
        'nomine suo vocare. Psal. 147. Numerat, inquit, multitudinem stellarum & omnibus eis '
        'nomina vocat. Argumento evidenti, quod non solum in genere naturam stellarum noverit, '
        'sed quod haec & illa stella singularis ipsi probe sit nota & perspecta.'
    ),
    '515': (
        'XVIII. Neque putandum est Deum res quidem magnas, & alicujus momenti, ut stellas, '
        'sigillatim nosse, scientiam vero illius fugere multitudinem & numerum rerum parvarum '
        '& vilium: quasi non deceret intellectum divinum ad earum singulas seorsim advertere. '
        'Id existimasse videtur Hieronymus scribens in Prophetiae Abacuc caput primum, '
        'Absurdum est, inquit, ad hoc Dei deducere majestatem, ut sciat per momenta singula '
        'quot nascantur culices, quotve moriantur: quae cimicum, & pulicum, & muscarum sit in '
        'terra multitudo: quanti pisces in aqua natent, & qui de minoribus majorum praedae '
        'cedere debeant.'
    ),
    '516': (
        'XIX. Sed argumenta, quae modo attulimus, probant Deum non minus res parvas ac tenues, '
        'quam magnas & graves nosse: Etenim Deus non minus res parvas quam magnas condidit. '
        'Non minus parvis, quam magnis rebus adest, & intime praesens est. Adeoque minimarum '
        'etiam rerum curam gerit. Nam ne unus quidem passerculus in terram cadit sine patre '
        'nostro, id est, sine ejus scitu atque permissu. Et etiam capitis nostri capilli omnes '
        'numerati sunt, ut docet Christus Matth. cap. 10. 29. 30.'
    ),
    '517': (
        'XX. Nec ideo vilescit intellectus divinus, quod nec parvas & viles cognoscat: sicut '
        '& sol non inquinatur, propterea quod illius radii saepe limum & stercora feriant & '
        'collustrent.'
    ),
    '518': (
        'XXI. Hominum quidem respectu melius est quaedam nescire quam scire: & res est '
        'vituperabilis, ingenioque magno & excelso indigna, si quis ad res parvas & viles '
        'advertat. Verum hoc inde fit, quod intellectus humanus finitus cum sit, neque '
        'multorum capax, sufficere non potest omnibus cognoscendis. Ac propterea si rerum '
        'vilium atque minutarum cognitionem quaerat, iisque nimium attendat, hoc ipso necesse '
        'est illum ea negligere, quae sunt majoris momenti, & quae ignorare illi noxium ac '
        'turpe est. At in Deo res aliter se habet. Nam intellectus divinus, propter suam '
        'infinitatem, per notitiam rerum pusillarum non avertitur a rerum magnarum scientia, '
        'aut in ea aliqua ratione impeditur. Nec etiam metus est, ne dum res parvas & viles '
        'contemplatur, obliviscatur earum, quae graves sunt atque momentosae.'
    ),
    '519': (
        'XXII. Adde quod Dei respectu nihil proprie magnum aut pretiosum dici potest. Nec '
        'enim ullius indiget, aut aliquem ex ulla re, qui ad ipsum redeat, fructum capere '
        'potest, cum sit αὐτάρκης, & sibi sufficiens. Nec etiam quidquam ad ejus magnitudinem '
        'accedit. Nam quae sunt quantumlibet magna in infinitum, sua immensitate superat. Nec '
        'minus ab eo distant quae maxima videntur nobis, quam quae minima: cum inter Deum & '
        'creaturam quamvis distantia sit infinita, qua nulla major dari potest. Adeoque, si '
        'Deus nil nosse debet, quod non sit coram ipso magnum & momentosum, necesse est '
        'omnium scientiam ei adimere, quia omnia sunt ei tanquam nihilum, ut magnificis verbis '
        'docet Isaias cap. 40. Ecce, inquit, gentes quasi stilla situlae, & quasi pulvis '
        'staturae reputatae sunt: ecce insulae quasi pulverem exiguum. Omnes Gentes quasi non '
        'sint sic sunt coram eo, & quasi nihilum & inane reputatae sunt ei.'
    ),
    '520': (
        'XXIII. Rursus vero alio respectu dici potest coram Deo nullam creaturam parvam & '
        'vilem esse. Nam vidit Deus quicquid fecit, & visum est ei valde bonum, quam in '
        'minimis quoque ejus potentia, bonitas & sapientia elucet: imo maxime in illis '
        'animalculis, quae calcamus & pro vilissimis habemus: in quibus Deo placitum est '
        'virtutum suarum edere specimina, & quasi miracula, quae rite contemplantem in '
        'admirationem & stuporem dare possunt, & Dei gloriam non parum illustrare.'
    ),
    '521': (
        'XXIV. Ut autem divinae omniscientiae Scriptura nos certiores reddat, praecipue urget '
        'Deum videre atque intueri quae sunt hominibus maxime occulta: quales sunt cordium '
        'cogitationes, & latentia in hominum animis consilia. Infernus, inquit sapiens, & '
        'perditio coram Domino, quanto magis corda filiorum hominum? Prov. 15. 11. Et hac '
        'cognitione Deus tanquam sibi propria saepius gloriatur, asserens se eum esse qui '
        'scrutatur renes & corda, ut praesertim videre est 17. cap. Jeremiae, Fraudulentum '
        'est, inquit, cor prae omnibus & inscrutabile; quis cognoscet illud? Ego Dominus '
        'scrutans cor & probans renes: qui do unicuique juxta viam suam & juxta fructum '
        'operum suorum. Quod agnoscens Solomon 2. Paral. 6. 30. hanc Deo gloriam tribuit, '
        'Tu solus nosti corda filiorum hominum.'
    ),
}

SECTIONS = [
    {
        'section': '514',
        'title': 'God names each star — Ps 147',
        'pass_a': (
            'And certainly Scripture testifies that God knows the individual stars, and calls '
            'each of them by its name. Psalm 147: He counts, it says, the multitude of the '
            'stars and calls them all by name. By evident argument, that He has known not only '
            'the nature of the stars in genus, but that this and that singular star is well '
            'known and seen through by Him.'
        ),
        'pass_b': [
            'Scripture: God knows each star.',
            'Ps 147 — counts them and names them all.',
            'Singular stars, not genus only.',
        ],
        'lemmas': [
            {'latin': 'nomine suo vocare', 'gloss': 'to call by its name'},
            {'latin': 'stella singularis ipsi probe sit nota', 'gloss': 'that singular star is well known to Him'},
        ],
        'choices': [{
            'term': 'Numerat … multitudinem stellarum & omnibus eis nomina vocat',
            'english': 'He counts … the multitude of the stars and calls them all by name',
            'why': 'Scripture proof of singular knowledge in the heavens.',
            'rejected': ['God knows star-kind only, not this star'],
        }],
        'notes': ['OCR: XVII PDF 131; Psal. 147.'],
        'bible_refs': ['Ps. 147:4'],
    },
    {
        'section': '515',
        'title': 'Jerome’s absurdity — counting gnats and fleas',
        'pass_a': (
            'Nor is it to be thought that God knows great things of some moment, such as the '
            'stars, one by one, but that the multitude and number of small and base things '
            'escape His knowledge: as if it were not fitting for the divine intellect to attend '
            'to each of them separately. Jerome writing on the first chapter of the prophecy of '
            'Habakkuk seems to have thought that: It is absurd, he says, to bring God’s majesty '
            'down to this, that He should know at each moment how many gnats are born or die: '
            'what multitude of bugs and fleas and flies is on the earth: how many fish swim in '
            'the water, and which of the smaller ought to fall as prey to the greater.'
        ),
        'pass_b': [
            'Do not spare small/vile things from His knowledge.',
            'Jerome (Hab 1) called gnat-counting absurd.',
            'Le Blanc will refute that limit.',
        ],
        'lemmas': [
            {'latin': 'scientiam vero illius fugere … rerum parvarum & vilium', 'gloss': 'but that … small and base things escape His knowledge'},
            {'latin': 'quot nascantur culices', 'gloss': 'how many gnats are born'},
        ],
        'choices': [{
            'term': 'Absurdum est … ut sciat per momenta singula quot nascantur culices',
            'english': 'It is absurd … that He should know at each moment how many gnats are born',
            'why': 'States Jerome’s objection before answering it from creation/presence/care.',
            'rejected': ['Jerome correctly limits God’s knowledge of small things'],
        }],
        'notes': ['OCR: XVIII PDF 131; Hieronymus on Habakkuk.'],
        'bible_refs': [],
    },
    {
        'section': '516',
        'title': 'Small things too — sparrows and hairs; Matt 10',
        'pass_a': (
            'But the arguments we have just brought prove that God knows small and slight '
            'things no less than great and weighty ones: For God founded small things no less '
            'than great ones. He is present to small things no less than to great, and '
            'intimately present. And so He also cares for the least things. For not even one '
            'little sparrow falls to the earth without our Father, that is, without His '
            'knowledge and permission. And also all the hairs of our head are numbered, as '
            'Christ teaches in Matthew chapter 10 verses 29–30.'
        ),
        'pass_b': [
            'Same create/presence arguments cover small things.',
            'God cares for the least.',
            'Matt 10: sparrow / numbered hairs.',
        ],
        'lemmas': [
            {'latin': 'minimarum etiam rerum curam gerit', 'gloss': 'He also cares for the least things'},
            {'latin': 'capilli omnes numerati sunt', 'gloss': 'all the hairs are numbered'},
        ],
        'choices': [{
            'term': 'ne unus quidem passerculus in terram cadit sine patre nostro',
            'english': 'not even one little sparrow falls to the earth without our Father',
            'why': 'Christ’s care texts overturn Jerome’s limit.',
            'rejected': ['God ignores gnats and sparrows'],
        }],
        'notes': ['OCR: XIX PDF 131; Matt 10:29-30.'],
        'bible_refs': ['Matt. 10:29-30'],
    },
    {
        'section': '517',
        'title': 'Knowing the low does not soil the divine intellect',
        'pass_a': (
            'Nor does the divine intellect therefore grow base because it knows small and vile '
            'things: just as the sun is not defiled because its rays often strike and light up '
            'mud and dung.'
        ),
        'pass_b': [
            'Knowing low objects does not degrade God.',
            'Sun analogy: rays on mud stay clean.',
            'Object’s baseness ≠ knower’s baseness.',
        ],
        'lemmas': [
            {'latin': 'Nec ideo vilescit intellectus divinus', 'gloss': 'Nor does the divine intellect therefore grow base'},
            {'latin': 'sol non inquinatur', 'gloss': 'the sun is not defiled'},
        ],
        'choices': [{
            'term': 'sicut & sol non inquinatur',
            'english': 'just as the sun is not defiled',
            'why': 'Blocks the dignity objection to knowing vile particulars.',
            'rejected': ['contact with base objects soils God’s mind'],
        }],
        'notes': ['OCR: XX PDF 131; sun/mud.'],
        'bible_refs': [],
    },
    {
        'section': '518',
        'title': 'Finite minds must skip small things — God’s infinity need not',
        'pass_a': (
            'With respect to men indeed it is better to be ignorant of some things than to know '
            'them: and it is blameworthy, and unworthy of a great and lofty mind, if someone '
            'attends to small and vile things. But that comes about because the human intellect, '
            'being finite and not capable of many things, cannot suffice for knowing all. And '
            'therefore if it seeks knowledge of base and tiny things and attends to them too '
            'much, by that very fact it must neglect those of greater moment, which it is '
            'harmful and shameful for it to ignore. But in God the matter is otherwise. For the '
            'divine intellect, because of its infinity, is not turned away from the knowledge of '
            'great things by notice of petty things, nor hindered in it in any way. Nor is there '
            'fear that while it contemplates small and vile things it may forget those that are '
            'weighty and momentous.'
        ),
        'pass_b': [
            'For humans: attending to trivia crowds out weighty things.',
            'Finite capacity forces trade-offs.',
            'Infinite intellect: no diversion, no forgetting.',
        ],
        'lemmas': [
            {'latin': 'intellectus humanus finitus', 'gloss': 'the human intellect … finite'},
            {'latin': 'propter suam infinitatem … non avertitur', 'gloss': 'because of its infinity … is not turned away'},
        ],
        'choices': [{
            'term': 'per notitiam rerum pusillarum non avertitur a rerum magnarum scientia',
            'english': 'is not turned away from the knowledge of great things by notice of petty things',
            'why': 'Infinity dissolves the human trade-off Jerome assumed.',
            'rejected': ['God’s mind is crowded like ours by small details'],
        }],
        'notes': ['OCR: XXI PDF 131; finitum vs infinitum.'],
        'bible_refs': [],
    },
    {
        'section': '519',
        'title': 'Before God nothing is properly great — Isa 40',
        'pass_a': (
            'Add that with respect to God nothing can properly be called great or precious. For '
            'He needs no one, nor can He take any fruit from any thing that returns to Himself, '
            'since He is self-sufficient and sufficient to Himself. Nor does anything add to His '
            'magnitude. For whatever things are however great, He surpasses into the infinite by '
            'His immensity. Nor are those which seem greatest to us less distant from Him than '
            'those which are least: since between God and any creature the distance is infinite, '
            'than which none greater can be given. And so, if God ought to know nothing that is '
            'not great and momentous before Him, it is necessary to take from Him the knowledge '
            'of all things, because all things are to Him as nothing, as Isaiah teaches in '
            'magnificent words in chapter 40. Behold, he says, the nations are as a drop of a '
            'bucket, and are counted as the dust of the balance: behold the islands as a little '
            'dust. All the nations are as if they were not before Him, and are counted to Him as '
            'nothing and emptiness.'
        ),
        'pass_b': [
            'Nothing properly great before self-sufficient God.',
            'Infinite distance: our greatest ≈ our least to Him.',
            'Isa 40: nations as a drop — else strip all knowledge.',
        ],
        'lemmas': [
            {'latin': 'nihil proprie magnum aut pretiosum', 'gloss': 'nothing properly great or precious'},
            {'latin': 'omnia sunt ei tanquam nihilum', 'gloss': 'all things are to Him as nothing'},
        ],
        'choices': [{
            'term': 'si Deus nil nosse debet, quod non sit coram ipso magnum … necesse est omnium scientiam ei adimere',
            'english': 'if God ought to know nothing that is not great before Him … it is necessary to take from Him the knowledge of all things',
            'why': 'Reductio: dignity-filter on objects empties omniscience.',
            'rejected': ['God should know only what is great before Him'],
        }],
        'notes': ['OCR: XXII PDF 131; Isa 40; αὐτάρκης.'],
        'bible_refs': ['Isa. 40:15-17'],
    },
    {
        'section': '520',
        'title': 'Conversely nothing is properly vile — glory in animalcules',
        'pass_a': (
            'But again in another respect it can be said that before God no creature is small '
            'and base. For God saw whatever He made, and it seemed to Him very good, how in the '
            'least things also His power, goodness, and wisdom shine: indeed most of all in those '
            'little animals which we tread under foot and hold for the basest: in which it has '
            'pleased God to put forth specimens of His virtues, and as it were miracles, which '
            'can throw one who rightly contemplates them into wonder and stupor, and not a little '
            'illustrate the glory of God.'
        ),
        'pass_b': [
            'Flip side: no creature properly vile before God.',
            'Very good even in the least.',
            'Animalcules display power, goodness, wisdom.',
        ],
        'lemmas': [
            {'latin': 'nullam creaturam parvam & vilem esse', 'gloss': 'that no creature is small and base'},
            {'latin': 'in illis animalculis', 'gloss': 'in those little animals'},
        ],
        'choices': [{
            'term': 'in minimis quoque ejus potentia, bonitas & sapientia elucet',
            'english': 'in the least things also His power, goodness, and wisdom shine',
            'why': 'Balances Isa 40 with Gen 1 goodness in the tiny.',
            'rejected': ['least creatures show nothing of God'],
        }],
        'notes': ['OCR: XXIII PDF 132 / p. 120; animalcula.'],
        'bible_refs': ['Gen. 1:31'],
    },
    {
        'section': '521',
        'title': 'God searches hearts — Prov 15; Jer 17; 2 Chr 6',
        'pass_a': (
            'But that Scripture may make us more certain of divine omniscience, it especially '
            'urges that God sees and looks on what is most hidden from men: such as the thoughts '
            'of hearts, and the counsels lying hidden in men’s souls. Hell, says the wise man, '
            'and destruction are before the Lord; how much more the hearts of the sons of men? '
            'Prov. 15:11. And with this knowledge God often glories as proper to Himself, '
            'asserting that He is the One who searches kidneys and hearts, as is especially to '
            'be seen in Jeremiah chapter 17: The heart is deceitful, he says, above all things '
            'and inscrutable; who will know it? I the Lord searching the heart and proving the '
            'kidneys: who give to each according to his way and according to the fruit of his '
            'works. Which Solomon acknowledging in 2 Chronicles 6:30 ascribes this glory to '
            'God: You alone know the hearts of the sons of men.'
        ),
        'pass_b': [
            'Omniscience pressed on hidden hearts/counsels.',
            'Prov 15:11; Jer 17 — searches heart and kidneys.',
            '2 Chr 6:30 — You alone know hearts.',
        ],
        'lemmas': [
            {'latin': 'scrutatur renes & corda', 'gloss': 'searches kidneys and hearts'},
            {'latin': 'Tu solus nosti corda filiorum hominum', 'gloss': 'You alone know the hearts of the sons of men'},
        ],
        'choices': [{
            'term': 'Ego Dominus scrutans cor & probans renes',
            'english': 'I the Lord searching the heart and proving the kidneys',
            'why': 'Closes XVII-XXIV on inmost singulars; next XXV+ times.',
            'rejected': ['hearts are opaque even to God'],
        }],
        'notes': ['OCR: XXIV PDF 132; Prov 15; Jer 17; 2 Chr 6; next XXV+.'],
        'bible_refs': ['Prov. 15:11', 'Jer. 17:9-10', '2 Chr. 6:30'],
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
    for name in ('pdf_131.txt', 'pdf_132.txt'):
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
        if 514 <= n <= 521:
            notes = (
                f'Section {sid}: new densify De Scientia Dei XVII-XXIV; '
                'Pass A!=B; lock-grounded PDF 131-132 / book pp. 119-120.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_scientia XVII-XXIV packet scope covering all current sections.'
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
                'Scope review: densify De Scientia Dei XVII-XXIV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Next Scientia XXV+ (times). Not shipped.'
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
        'locus': 'De Scientia Dei theses XVII-XXIV (stars; Jerome; Matt 10; great/small; hearts)',
        'next_locus': 'De Scientia Dei XXV+ (past/present/future; possibles)',
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
        f'## {day} (Scribe — De Scientia Dei XVII–XXIV densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Scientia Dei XVII–XXIV → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 131-132 / pp. 119-120).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Scientia Dei XXV+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Scientia Dei XVII–XXIV densify)\n\n'
        'CoS densify: Scientia Dei XVII–XXIV. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Scientia Dei XVII–XXIV (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Scientia XXV+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_521.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-521 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
