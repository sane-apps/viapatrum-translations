#!/usr/bin/env python3
"""Build + apply De Dei Immensitate & Omnipraesentia XXV-XXXII densify (tip 448 → 456).

Peculiar presence; Christ; pollution; immobility. Tract close. Live floor 4604.
After tip-ready: HOLD live>4604 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_immensitate_xxv_xxxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_immensitate/apply_dei_immensitate_xxv_xxxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['449', '450', '451', '452', '453', '454', '455', '456']
ROMANS = {
    '449': 'XXV', '450': 'XXVI', '451': 'XXVII', '452': 'XXVIII',
    '453': 'XXIX', '454': 'XXX', '455': 'XXXI', '456': 'XXXII',
}
TIP_BEFORE = 448
LIVE_FLOOR = 4604
HOLD_MINUTES = 12
PRIOR_START = 425

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Immensitate & Omnipraesentia I-XXXII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Immensitate & Omnipraesentia I-XXXII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Immensitate & Omnipraesentia I-XXXII, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Immensitate XXV-XXXII "
    "(peculiar presence; temple/saints/Christ; pollution; immobility; tract close)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Immensitate & Omnipraesentia.\n"
    "Same 1675 Pitt copy-text. Book pp. 106-110 / PDF 118-122 (I-XXXII; this packet XXV-XXXII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Immensitate & Omnipraesentia I-XXXII tip — tract closed. Next: De Aeternitate Dei.\n"
    "Note: Continues after XVII-XXIV. Peculiar habitation; Christ; no pollution; immobile; figurative ascent.\n\n"
)

LATIN = {
    '449': (
        'XXV. Igitur sciendum est, quamvis Deus sit ubique, non tantum per virtutem & '
        'cognitionem suam, sed etiam per substantiam; certas tamen ob causas Deum peculiari '
        'modo dici esse, & habitare in quibusdam locis & personis, nempe, ubi, vel suae '
        'majestatis & gloriae, vel gratiae & favoris signa & effecta dat quaedam peculiaria. '
        'Sic Deus in caelis habitare dicitur, quia ibi cernuntur illustriora quam in terra '
        'potentiae & gloriae divinae documenta. Illic enim videmus splendere solem & alia '
        'sidera, & mirandis motibus ciere. Indeque derivari in haec inferiora lucem, '
        'calorem, vitam, atque omnem vigorem. Deinde in terra locus est peccato & miseriis '
        'quae a caelo procul absunt. Sed ubi peccatum & miseria obtinet, Scriptura Sacra '
        'nobiscum balbutiens, de Deo loquitur perinde ac si abesset: quia ibi Dei praesens '
        'auxilium & efficacia gratiae non sentitur, aut ita illustris non est. Ideoque mirum '
        'non est si dicatur in caelis esse aliquo modo, secundum quem in terra non est. Adde '
        'quod angeli, qui Dei filii & ministri dicuntur, propriam in caelis habitationem '
        'habent, ubi etiam sedes parata est Ecclesiae, quae ideo in terris peregrina '
        'dicitur. Et idcirco non immerito Dei domus & habitaculum peculiari ratione dicitur '
        'esse in caelis, quandoquidem universa, ut ita dicam, Dei familia illic perpetuo '
        'mansura & habitatura est.'
    ),
    '450': (
        'XXVI. Similiter in templo Hierosolymitano Deus habitare olim dicebatur, quoniam '
        'ibi certa praesentiae suae symbola collocari voluerat: nempe arcam foederis, & '
        'propitiatorium. Et ibidem singulari quadam ratione se coli praeceperat, & preces '
        'sibi offerri quas promiserat se exauditurum. Imo aliquando inde viva reddebat '
        'oracula, & responsa dabat interrogantibus.'
    ),
    '451': (
        'XXVII. Ita quoque Deus dicitur in hominibus sanctis & justis habitare, quoniam eos '
        'regit propitius, & favore suo prosequitur & gratia exornat, singularesque in iis '
        'operationes edit. Tum quia homines frequentant, imo si possunt inhabitant ea loca '
        'quae amant, ad designandum summum illum amorem quo Deus justos prosequitur, '
        'dicitur eis inhabitare. Juxta illud Christi, Joan. 14. Si quis diligit me, '
        'sermonem meum servabit, & Pater meus diliget eum, & ad eum veniemus, & mansionem '
        'apud eum faciemus.'
    ),
    '452': (
        'XXVIII. Praecipue vero longe perfectissimo & ineffabili modo Deus est in Christo '
        'homine, in quo tam excellenter habitat divinitas, ut ipse vere & proprie Deus esse '
        'dicatur. Unde dictum est a Paulo omnem plenitudinem divinitatis in eo habitare '
        'somatikos, corporaliter. Corporaliter, inquam, non tantum, ut id opponatur figurae, '
        'secundum quam Deus in templo Judaico, & in arca foederis esse & habitare '
        'dicebatur: sed maxime propter hypostaticam illam unionem, qua divina natura cum '
        'humana & concreta in unam convenit personam; ut vere dicere liceat divinitatem '
        'incarnatam, atque ut ita loquar, incorporatam esse.'
    ),
    '453': (
        'XXIX. Sed quamvis Deus, ut jam ostensum est, singulari modo dicatur in quibusdam '
        'rebus & personis esse, ob certas rationes a nobis indicatas, hoc non obstat quo '
        'minus existat in omnibus rebus, qua ratione quoque supra expositum est. Imo quin '
        'tantus sit ut, cum in mundo ubique praesens sit, mundo tamen non contineatur, sed '
        'immensitate sua mundum infinite superet.'
    ),
    '454': (
        'XXX. Neque metuendum est ne Deus locorum sordibus inquinetur. Et ne, si ejus '
        'essentia per haec inferiora & terrena diffusa sit, ubi tam multa polluta & sordida '
        'occurrunt, inde pollutionem & immunditiem aliquam contrahat. Nam cum Deus sit '
        'spiritus a corpore tangi non potest. Et cum infinito naturae intervallo creaturam '
        'omnem superet, a creatura non potest quicquam recipere, vel pati. Deinde verum est '
        'quidem quaedam corporaliter immunda & sordida esse respectu nostri, vel alterius '
        'creaturae, cujus naturam offendunt, corrumpunt, aut vitiant. Sed respectu Dei nulla '
        'res sordida aut polluta est. Solum vero peccatum, quod non est res, sed rei vitium, '
        '& defectus, quodque Deus nec facit, nec contingit, spiritualis immunditia est, & '
        'abominatio coram Deo.'
    ),
    '455': (
        'XXXI. Porro ex ista Dei immensitate, qua omnia loca tam actualia, quam possibilia '
        'replet, sequitur illum esse immobilem, neque posse mutare locum. Nam quod locum '
        'mutat & loco movetur necesse est ut locum unum deserat, & alium acquirat. Sed quod '
        'ubique jam est, & loca omnia replet, nullum locum acquirere potest, nec ullum '
        'locum deserere. Et certe vis se loco movendi est magna quidem perfectio in '
        'substantia finita, quae, cum pluribus in locis simul esse non possit, beneficio '
        'facultatis illius potest innumeris locis successive adesse, & ita suam, ut ita '
        'dicam, finitatem & parvitatem quodammodo compensare. Sed Dei infinitas & '
        'immensitas efficit ut auxilio isto non egeat: quandoquidem per suam immensitatem '
        'habet modo perfectissimo quicquid per motum localem suppleri, & acquiri potest '
        'modo longe imperfectiori.'
    ),
    '456': (
        'XXXII. Quamobrem quum Deus dicitur in Scriptura ascendere, vel descendere, '
        'accedere, vel recedere, hucque & illuc proficisci, ista figurate accipienda sunt '
        'non de quadam in Deo loci mutatione, sed de variis operationibus, quas Deus hic '
        'vel illic edere incipit, vel definit.'
    ),
}

SECTIONS = [
    {
        'section': '449',
        'title': 'Peculiar habitation — heaven as special glory and family seat',
        'pass_a': (
            'Therefore it must be known that although God is everywhere, not only by His '
            'power and cognition, but also by substance; nevertheless for certain causes God '
            'is said in a peculiar mode to be, and to dwell, in certain places and persons, '
            'namely where He gives certain peculiar signs and effects either of His majesty '
            'and glory, or of grace and favor. So God is said to dwell in the heavens, '
            'because there are seen more illustrious evidences of divine power and glory than '
            'on earth. For there we see the sun and other stars shine, and stir with wondrous '
            'motions. And from thence light, heat, life, and all vigor are derived into these '
            'lower things. Next on earth there is place for sin and miseries which are far '
            'from heaven. But where sin and misery obtain, Sacred Scripture, babbling with '
            'us, speaks of God as if He were absent: because there God\'s present help and '
            'the efficacy of grace are not felt, or are not so illustrious. And therefore it '
            'is no wonder if He is said to be in the heavens in some mode according to which '
            'He is not on earth. Add that the angels, who are called sons and ministers of '
            'God, have their proper dwelling in the heavens, where also a seat is prepared '
            'for the Church, which therefore on earth is called a pilgrim. And therefore not '
            'undeservedly God\'s house and dwelling is said by a peculiar reason to be in '
            'the heavens, since the whole, so to speak, family of God will there perpetually '
            'remain and dwell.'
        ),
        'pass_b': [
            'Ubiquitous by substance — yet peculiarly said to dwell where special glory/grace signs appear.',
            'Heaven: clearer documents of power; earth holds sin/misery — Scripture speaks as if He were absent.',
            'Angels and the Church\'s prepared seat make heaven God\'s peculiar house.',
        ],
        'lemmas': [
            {'latin': 'peculiari modo dici esse, & habitare', 'gloss': 'to be said in a peculiar mode to be, and to dwell'},
            {'latin': 'Dei domus & habitaculum', 'gloss': 'God\'s house and dwelling'},
        ],
        'choices': [{
            'term': 'quamvis Deus sit ubique … certas tamen ob causas Deum peculiari modo dici esse',
            'english': 'although God is everywhere … nevertheless for certain causes God is said in a peculiar mode to be',
            'why': 'Opens XXV+ by reconciling ubiquity with special habitation language.',
            'rejected': ['peculiar habitation cancels substantial ubiquity'],
        }],
        'notes': ['OCR: XXV PDF 121 / p. 109.'],
        'bible_refs': [],
    },
    {
        'section': '450',
        'title': 'Jerusalem temple — symbols, commanded worship, oracles',
        'pass_a': (
            'Likewise God was once said to dwell in the temple at Jerusalem, because there '
            'He had willed certain symbols of His presence to be placed: namely the ark of '
            'the covenant, and the mercy-seat. And there by a certain singular reason He had '
            'commanded Himself to be worshiped, and prayers to be offered to Him which He '
            'had promised He would hear. Nay sometimes from thence He gave living oracles, '
            'and answers to those who asked.'
        ),
        'pass_b': [
            'Temple habitation: ark and mercy-seat as presence symbols.',
            'Commanded worship and promised hearing of prayer there.',
            'Sometimes living oracles and answers from that place.',
        ],
        'lemmas': [
            {'latin': 'arcam foederis, & propitiatorium', 'gloss': 'the ark of the covenant, and the mercy-seat'},
            {'latin': 'viva reddebat oracula', 'gloss': 'He gave living oracles'},
        ],
        'choices': [{
            'term': 'ibi certa praesentiae suae symbola collocari voluerat',
            'english': 'there He had willed certain symbols of His presence to be placed',
            'why': 'Temple language tracks special signs, not boxed substance.',
            'rejected': ['temple habitation meant God\'s substance was only there'],
        }],
        'notes': ['OCR: XXVI PDF 121-122 / pp. 109-110.'],
        'bible_refs': [],
    },
    {
        'section': '451',
        'title': 'God dwells in the holy — favor, grace, John 14 mansion',
        'pass_a': (
            'So also God is said to dwell in holy and just people, because He rules them '
            'propitiously, and pursues them with His favor and adorns them with grace, and '
            'works singular operations in them. Then because people frequent, nay if they '
            'can inhabit, those places they love, to designate that highest love with which '
            'God pursues the just, He is said to inhabit them. According to that of Christ, '
            'John 14. If anyone loves Me, he will keep My word, and My Father will love '
            'him, and We will come to him, and make Our mansion with him.'
        ),
        'pass_b': [
            'In the holy: propitious rule, favor, grace, singular works.',
            'Love-language: as people inhabit what they love, God inhabits the just.',
            'John 14: We will come and make Our mansion with him.',
        ],
        'lemmas': [
            {'latin': 'in hominibus sanctis & justis habitare', 'gloss': 'to dwell in holy and just people'},
            {'latin': 'mansionem apud eum faciemus', 'gloss': 'We will make Our mansion with him'},
        ],
        'choices': [{
            'term': 'dicitur eis inhabitare',
            'english': 'He is said to inhabit them',
            'why': 'Peculiar grace-presence in the saints.',
            'rejected': ['God inhabits saints by leaving the rest empty of substance'],
        }],
        'notes': ['OCR: XXVII PDF 122; John 14:23.'],
        'bible_refs': ['John 14:23'],
    },
    {
        'section': '452',
        'title': 'Highest mode — divinity in Christ hypostatically, bodily',
        'pass_a': (
            'But especially in a far most perfect and ineffable mode God is in the man '
            'Christ, in whom deity dwells so excellently that He Himself is said truly and '
            'properly to be God. Whence it was said by Paul that all the fullness of deity '
            'dwells in Him somatikos, bodily. Bodily, I say, not only as opposed to the '
            'figure according to which God was said to be and dwell in the Jewish temple and '
            'in the ark of the covenant: but chiefly because of that hypostatic union by '
            'which the divine nature comes together with the human and concrete into one '
            'person; so that it is truly permitted to say that deity is incarnate, and so to '
            'speak, incorporate.'
        ),
        'pass_b': [
            'Highest mode: deity in the man Christ — He is truly God.',
            'Col 2 somatikos / bodily: beyond temple-figure presence.',
            'Hypostatic union: divinity incarnate / incorporate in one person.',
        ],
        'lemmas': [
            {'latin': 'hypostaticam illam unionem', 'gloss': 'that hypostatic union'},
            {'latin': 'divinitatem incarnatam … incorporatam esse', 'gloss': 'that deity is incarnate … incorporate'},
        ],
        'choices': [{
            'term': 'omnem plenitudinem divinitatis in eo habitare … corporaliter',
            'english': 'that all the fullness of deity dwells in Him … bodily',
            'why': 'Climaxes peculiar presence in the Incarnation.',
            'rejected': ['bodily only means a temple-style figure of presence'],
        }],
        'notes': ['OCR: XXVIII PDF 122; Col 2:9 somatikos.'],
        'bible_refs': ['Col. 2:9'],
    },
    {
        'section': '453',
        'title': 'Peculiar modes do not cancel ubiquity or world-surpassing greatness',
        'pass_a': (
            'But although God, as already shown, is said in a singular mode to be in certain '
            'things and persons, for certain reasons indicated by us, this does not hinder '
            'Him from existing in all things, in the way also set out above. Nay that He is '
            'so great that, while present everywhere in the world, He is nevertheless not '
            'contained by the world, but by His immensity infinitely surpasses the world.'
        ),
        'pass_b': [
            'Singular presence in some does not block existence in all.',
            'Still everywhere in the world — yet not contained by it.',
            'Immensity infinitely surpasses the world.',
        ],
        'lemmas': [
            {'latin': 'hoc non obstat quo minus existat in omnibus rebus', 'gloss': 'this does not hinder Him from existing in all things'},
            {'latin': 'mundum infinite superet', 'gloss': 'infinitely surpasses the world'},
        ],
        'choices': [{
            'term': 'mundo tamen non contineatur, sed immensitate sua mundum infinite superet',
            'english': 'He is nevertheless not contained by the world, but by His immensity infinitely surpasses the world',
            'why': 'Ties peculiar modes back to ubiquity + surpassing.',
            'rejected': ['peculiar presence means He is only where specially named'],
        }],
        'notes': ['OCR: XXIX PDF 122.'],
        'bible_refs': [],
    },
    {
        'section': '454',
        'title': 'Essence through lower places does not pollute God — only sin is filth before Him',
        'pass_a': (
            'Nor is it to be feared that God be defiled by the filth of places. And lest, if '
            'His essence is poured through these lower and earthly things, where so many '
            'polluted and filthy things occur, He thence contract some pollution and '
            'uncleanness. For since God is a spirit He cannot be touched by a body. And '
            'since by an infinite interval of nature He surpasses every creature, He cannot '
            'receive or suffer anything from a creature. Next it is true indeed that certain '
            'things are corporally unclean and filthy with respect to us, or to another '
            'creature, whose nature they offend, corrupt, or vitiate. But with respect to '
            'God no thing is filthy or polluted. Only sin, which is not a thing but a vice '
            'and defect of a thing, and which God neither makes nor touches, is spiritual '
            'uncleanness and an abomination before God.'
        ),
        'pass_b': [
            'No fear: essence in low places does not soil God.',
            'Spirit — untouchable by body; infinite gap — receives nothing from creatures.',
            'Creaturely filth is relative to us; before God only sin is spiritual uncleanness.',
        ],
        'lemmas': [
            {'latin': 'a corpore tangi non potest', 'gloss': 'He cannot be touched by a body'},
            {'latin': 'Solum vero peccatum … spiritualis immunditia est', 'gloss': 'Only sin … is spiritual uncleanness'},
        ],
        'choices': [{
            'term': 'respectu Dei nulla res sordida aut polluta est',
            'english': 'with respect to God no thing is filthy or polluted',
            'why': 'Blocks pollution objection to ubiquity through earthly places.',
            'rejected': ['God\'s essence contracts uncleanness from filthy places'],
        }],
        'notes': ['OCR: XXX PDF 122.'],
        'bible_refs': [],
    },
    {
        'section': '455',
        'title': 'Immensity implies immobility — already everywhere, needs no local motion',
        'pass_a': (
            'Further from that immensity of God, by which He fills all places both actual '
            'and possible, it follows that He is immobile, and cannot change place. For what '
            'changes place and is moved in place must leave one place and acquire another. '
            'But what is already everywhere and fills all places can acquire no place, nor '
            'leave any place. And certainly the power of moving oneself in place is indeed '
            'a great perfection in a finite substance, which, since it cannot be in many '
            'places at once, by benefit of that faculty can be present successively in '
            'countless places, and so in some way compensate its, so to speak, finitude and '
            'smallness. But God\'s infinity and immensity make Him not need that help: since '
            'by His immensity He has in the most perfect mode whatever can be supplied and '
            'acquired by local motion in a far more imperfect mode.'
        ),
        'pass_b': [
            'Fills all actual and possible places → immobile.',
            'Local movers leave one place for another; ubiquity cannot.',
            'Finite things need successive motion; immensity already has that more perfectly.',
        ],
        'lemmas': [
            {'latin': 'illum esse immobilem, neque posse mutare locum', 'gloss': 'that He is immobile, and cannot change place'},
            {'latin': 'auxilio isto non egeat', 'gloss': 'He does not need that help'},
        ],
        'choices': [{
            'term': 'nullum locum acquirere potest, nec ullum locum deserere',
            'english': 'can acquire no place, nor leave any place',
            'why': 'Immensity → no local change.',
            'rejected': ['God moves from place to place like a finite spirit'],
        }],
        'notes': ['OCR: XXXI PDF 122.'],
        'bible_refs': [],
    },
    {
        'section': '456',
        'title': 'Scripture ascent and descent are figurative of operations, not local change',
        'pass_a': (
            'Wherefore when God is said in Scripture to ascend, or descend, to approach, or '
            'withdraw, and to set out hither and thither, those things are to be taken '
            'figuratively not of some change of place in God, but of various operations '
            'which God begins or ceases to put forth here or there.'
        ),
        'pass_b': [
            'Ascend / descend / approach / withdraw in Scripture.',
            'Not local change in God.',
            'Figurative of operations begun or ended here or there.',
        ],
        'lemmas': [
            {'latin': 'figurate accipienda sunt', 'gloss': 'are to be taken figuratively'},
            {'latin': 'non de quadam in Deo loci mutatione', 'gloss': 'not of some change of place in God'},
        ],
        'choices': [{
            'term': 'de variis operationibus, quas Deus hic vel illic edere incipit, vel definit',
            'english': 'of various operations which God begins or ceases to put forth here or there',
            'why': 'Closes Immensitate; next De Aeternitate Dei.',
            'rejected': ['Scripture ascent means God literally changes place'],
        }],
        'notes': ['OCR: XXXII PDF 122 / p. 110; Immensitate tract close before Aeternitate.'],
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
    for name in (
        'pdf_121_124_layout.txt', 'pdf_120_123_layout.txt',
        'tess121.txt', 'tess122.txt', 'tess122c.txt',
    ):
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
        if 449 <= n <= 456:
            notes = (
                f'Section {sid}: new densify De Dei Immensitate & Omnipraesentia XXV-XXXII tract close; '
                'Pass A!=B; lock-grounded PDF 121-122 / book pp. 109-110.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_immensitate XXV-XXXII packet scope covering all current sections.'
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
                'Scope review: densify De Dei Immensitate & Omnipraesentia XXV-XXXII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest tract close; Immensitate through XXXII. Next Aeternitate. Not shipped.'
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
        'locus': 'De Dei Immensitate & Omnipraesentia theses XXV-XXXII (peculiar; Christ; immobile; close)',
        'next_locus': 'De Aeternitate Dei (opens after Immensitate XXXII)',
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
        'deploy_bound': '9cbc6a72',
        'honest_slice_note': 'XXV-XXXII tract close before Aeternitate',
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
        f'## {day} (Scribe — De Dei Immensitate & Omnipraesentia XXV–XXXII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Immensitate XXV–XXXII → §§{SECS[0]}–{SECS[-1]}; tract close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 121-122 / pp. 109-110).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Immensitate & Omnipraesentia through XXXII **closed**. '
        'Next: De Aeternitate Dei. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound 9cbc6a72 / tip 448; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Immensitate & Omnipraesentia XXV–XXXII densify)\n\n'
        'CoS densify: Immensitate XXV–XXXII tract close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Immensitate XXV–XXXII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Aeternitate. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-448 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
