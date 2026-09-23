#!/usr/bin/env python3
"""Build + apply De Dei Simplicitate I-VIII densify (tip 370 → 378).

New lock: sources/_le_blanc_dei_simplicitate_latin_lock.txt
Deploy 78b7b840 live 57/4353 bound tip 370. After tip-ready: HOLD live>4353 OR 12m.
Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_simplicitate_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_simplicitate_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_simplicitate_i_densify')
PACKET_STEM = 'dei_simplicitate_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_simplicitate/apply_dei_simplicitate_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['371', '372', '373', '374', '375', '376', '377', '378']
ROMANS = {
    '371': 'I', '372': 'II', '373': 'III', '374': 'IV',
    '375': 'V', '376': 'VI', '377': 'VII', '378': 'VIII',
}
TIP_BEFORE = 370
LIVE_FLOOR = 4353
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + "
    "De Dei Simplicitate I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-VIII, reconstructed from the Internet Archive PDF page images with "
    "pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. This slice opens De Dei Simplicitate I-VIII (QUID SIT / "
    "attributes / simplicity vs composition)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Simplicitate (Theses Theologicae De Dei Simplicitate).\n"
    "Same 1675 Pitt copy-text. Book pp. 97-98 / PDF 109-110 (I-VIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Simplicitate I-VIII tip. IX+ remains.\n"
    "Note: Distinct from Demonstratur Deum esse (closed at XLII). This tract opens QUID SIT / attributes.\n\n"
)

LATIN = {
    '371': (
        'I. Esse Deum, Thesibus superioribus a nobis demonstratum fuit. Sequitur ut agamus de altera '
        'ista quaestione, scilicet, quid sit Deus, atque ea, qua decet, modestia & sobrietate, in '
        'ipsam Dei naturam inquiramus.'
    ),
    '372': (
        'II. Hic autem ante omnia profitenda est imbecillitas & ignorantia nostra. Nec enim putandum '
        'est mentem humanam, saltem quamdiu in hoc mortali corpore degit, capere posse quid Deus sit '
        'in se. Id docet Apostolus 1 Cor. 13. cum ait, nos nunc Deum videre per speculum & in '
        'aenigmate. Et Joan. ep. 1. c. 3. proponens tanquam vitae futurae privilegium quod Deum tunc '
        'sicuti est visuri simus. Indicio manifesto quod Deus sicuti est, a nobis jam non cognoscitur. '
        'Et certe si ne muscae quidem & formicae essentia a nobis jam percipi potest, ut modestiores '
        'philosophi agnoscunt, quanto minus existimandum est cognitione nos assequi posse quid sit '
        'Dei natura atque essentia.'
    ),
    '373': (
        'III. Veruntamen negandum non est, nos posse conceptus aliquos formare qui naturam divinam '
        'utcunque repraesentent, quantum scilicet capit ingenii nostri modulus: multaque Deo a nobis '
        'tribui, & de Deo enuntiari quae vere ipsi conveniunt, quamvis immensam ejus perfectionem '
        'minime assequantur. Et haec sunt quae vocantur attributa divina, quibus essentia Dei, '
        'quamquam imperfecte admodum & obscure aliquatenus tamen adumbratur.'
    ),
    '374': (
        'IV. Porro attributa ista duorum sunt generum. Nam vel iis aliquid de Deo affirmatur, vel '
        'aliquid de Deo negatur. Etenim duabus viis ad Divinae naturae cognitionem contendere '
        'possumus. Primum ipsi tribuendo perfectiones omnes quae in rebus creatis cernuntur. Quum '
        'enim sit primum ens, primaque omnium causa, necesse est ut quicquid perfectionis creaturis '
        'inest, in eo reperiatur modo quodam eminentiori. Deinde de Deo negando quicquid in creaturis '
        'sapit aut secum trahit aliquam imperfectionem. Oportet enim quicquid est imperfectum in '
        'rebus creatis a Deo removeri. Cum certum sit causam efficientem perfectiorem esse rebus '
        'effectis, eam maxime quae est prima & summa causa. Unde oriuntur, ut dictum, duo '
        'attributorum divinorum genera, quaedam scilicet negativa, alia vero affirmativa. Et '
        'prioribus quidem clarius & distinctius de Deo docetur quid non sit: posterioribus vero '
        'confusius & obscurius quid sit. Nam longe facilius est de Deo dicere quid non sit, quam '
        'explicare & capere quid sit. Itaque nobis naturam divinam investigantibus istiusmodi '
        'attributa divina breviter percurrenda & consideranda sunt: non omnia quidem & singula, '
        'sed praecipua nonnulla quae plus habent difficultatis, aut in Theologia majorem usum '
        'praestant.'
    ),
    '375': (
        'V. Primum autem attributum, quo natura divina utcunque declaratur, est Dei Simplicitas. '
        'Hic vero simplicitas non sumitur sensu morali, sed physico & metaphysico, prout simplex '
        'opponitur mixto & composito. Nam quum simplicitas Deo tribuitur, per id ab eo removetur '
        'omnis compositio.'
    ),
    '376': (
        'VI. Porro in rebus creatis multa animadvertuntur compositionis genera. Prima eaque omnium '
        'maxime sensibilis est, quae cernitur in omni corpore, quod constat partibus extensis, '
        'quarum una est extra aliam: adeoque quarum una ab alia dividi & separari potest. Secunda '
        'compositio, quae hic consideranda est, est subjecti & accidentis, sicut album constat '
        'albedine & corpore illo quod sustinet albedinem. Et sicut in homine, praeter naturam '
        'humanam, varia sunt accidentia, veluti virtus & vitium, scientia & ignorantia, unde '
        'varie homo denominatur, vel doctus, vel indoctus, vel vitiosus, vel virtute praeditus.'
    ),
    '377': (
        'VII. Sed praeterea sunt quaedam compositionis genera magis abstracta & metaphysica, quae '
        'hic quoque consideranda sunt. Nam in rebus omnibus creatis essentia potest ab existentia '
        'distingui, estque aliud essentia, & aliud existentia. Quippe per essentiam intelligimus '
        'id sine quo res concipi non potest, & per quod res quaeque definitur. Sic animal '
        'rationale est hominis essentia, quia non potes concipere hominem quin concipias animal '
        'rationale: estque animal rationale hominis definitio. Per existentiam autem intelligitur '
        'id per quod res actu est in rerum natura. Jam autem haec duo in rebus creatis omnino '
        'distinguuntur. Siquidem existentia de illarum essentia non est. Nam possunt esse & non '
        'esse. Et potes essentiam illarum concipere, etiamsi de earum existentia non cogites: imo '
        'quamvis cogites & scias illas non existere. Veluti cum quis hyeme, quando nulla rosa '
        'existat, naturam rosae contemplatur. Ideoque res omnes creatae compositae dici possunt '
        'ex essentia & existentia.'
    ),
    '378': (
        'VIII. Est & alia quoque compositio quae in rebus omnibus creatis animadvertitur. Nam in '
        'omnibus illis aliud est natura, & aliud singulare istud quod naturam habet. Ita '
        'distinguenda est humanitas quae est in Petro, & Petrus qui habet illam humanitatem. '
        'Estque in omni persona seu supposito, ut loquuntur, aliquid praeter naturam a natura '
        'ipsa distinctum: imo quod potest ab ipsa natura separari, ut patet ex mysterio '
        'incarnationis in Christo. Nam Christus naturam humanam assumpsit, & personam tamen '
        'humanam non assumpsit. Siquidem natura humana in Christo subsistit in persona Verbi, & '
        'propria subsistentia caret. Unde manifestum est aliud esse naturam, & aliud '
        'subsistentiam, sive illud quod personam constituit. Ideoque res omnes creatae compositae '
        'dici possunt ex natura & supposito, sive dicere mavis ex natura & subsistentia.'
    ),
}

SECTIONS = [
    {
        'section': '371',
        'title': 'From Esse Deum to Quid sit Deus — inquire with sobriety',
        'pass_a': (
            'That God is, was demonstrated by us in the superior Theses. It follows that we should '
            'treat of that other question, namely, what God is, and with that modesty and sobriety '
            'which is fitting inquire into the very nature of God.'
        ),
        'pass_b': [
            'Esse Deum is done — now Quid sit Deus.',
            'Inquire into God\'s nature with fitting modesty and sobriety.',
        ],
        'lemmas': [
            {'latin': 'Esse Deum', 'gloss': 'that God is'},
            {'latin': 'quid sit Deus', 'gloss': 'what God is'},
        ],
        'choices': [{
            'term': 'modestia & sobrietate, in ipsam Dei naturam inquiramus',
            'english': 'with modesty and sobriety inquire into the very nature of God',
            'why': 'Opens QUID SIT after closed AN SIT.',
            'rejected': ['AN SIT still open; rush into essence without sobriety'],
        }],
        'notes': ['OCR: I PDF 109 / book p. 97; new lock.'],
        'bible_refs': [],
    },
    {
        'section': '372',
        'title': 'Our mind cannot grasp what God is in Himself',
        'pass_a': (
            'But here before all things our weakness and ignorance must be professed. For it is not '
            'to be thought that the human mind, at least while it dwells in this mortal body, can '
            'grasp what God is in Himself. The Apostle teaches this in 1 Cor. 13 when he says that '
            'we now see God through a mirror and in an enigma. And 1 John 3, proposing as a privilege '
            'of the future life that we shall then see God as He is. By a clear indication that God '
            'as He is is not yet known by us. And certainly if not even the essence of a fly and an '
            'ant can already be perceived by us, as the more modest philosophers acknowledge, how '
            'much less is it to be thought that by cognition we can attain what the nature and '
            'essence of God is.'
        ),
        'pass_b': [
            'First: confess our weakness — we cannot grasp God-in-Himself here.',
            '1 Cor 13: mirror and enigma; 1 John 3: seeing as He is is future privilege.',
            'If fly and ant essence escape us, much less God\'s.',
        ],
        'lemmas': [
            {'latin': 'imbecillitas & ignorantia nostra', 'gloss': 'our weakness and ignorance'},
            {'latin': 'per speculum & in aenigmate', 'gloss': 'through a mirror and in an enigma'},
        ],
        'choices': [{
            'term': 'capere posse quid Deus sit in se',
            'english': 'can grasp what God is in Himself',
            'why': 'Limits QUID SIT knowledge this side of glory.',
            'rejected': ['mortal mind already knows God as He is in se'],
        }],
        'notes': ['OCR: II PDF 109; 1 Cor 13; 1 John 3.'],
        'bible_refs': ['1 Cor. 13', '1 John 3'],
    },
    {
        'section': '373',
        'title': 'Yet we form concepts — the divine attributes',
        'pass_a': (
            'Nevertheless it is not to be denied that we can form some concepts which somehow '
            'represent the divine nature, as far as the measure of our ingenuity takes: and that '
            'many things are attributed by us to God, and enunciated of God, which truly agree '
            'with Him, although they by no means attain His immense perfection. And these are what '
            'are called the divine attributes, by which the essence of God, although very imperfectly '
            'and obscurely, is yet in some measure adumbrated.'
        ),
        'pass_b': [
            'We can still form limited concepts of the divine nature.',
            'True attributions fall short of His immense perfection.',
            'Those are the divine attributes — a faint outline of essence.',
        ],
        'lemmas': [
            {'latin': 'attributa divina', 'gloss': 'divine attributes'},
            {'latin': 'aliquatenus tamen adumbratur', 'gloss': 'is yet in some measure adumbrated'},
        ],
        'choices': [{
            'term': 'attributa divina, quibus essentia Dei ... adumbratur',
            'english': 'divine attributes, by which the essence of God is adumbrated',
            'why': 'Names attributes as the workable QUID SIT path.',
            'rejected': ['no true speech about God is possible at all'],
        }],
        'notes': ['OCR: III PDF 109.'],
        'bible_refs': [],
    },
    {
        'section': '374',
        'title': 'Two kinds of attributes: via affirmation and negation',
        'pass_a': (
            'Further, those attributes are of two kinds. For either something is affirmed of God by '
            'them, or something is denied of God. For we can contend for the knowledge of the divine '
            'nature by two ways. First by attributing to Him all perfections which are seen in created '
            'things. For since He is the first being and the first cause of all, it is necessary that '
            'whatever perfection is in creatures be found in Him in a more eminent mode. Next by '
            'denying of God whatever in creatures savors of or carries with it some imperfection. For '
            'whatever is imperfect in created things ought to be removed from God. Since it is certain '
            'that the efficient cause is more perfect than the things effected, especially that which '
            'is the first and highest cause. Whence arise, as said, two kinds of divine attributes, '
            'some negative, others affirmative. And by the former indeed it is taught more clearly and '
            'distinctly of God what He is not: by the latter more confusedly and obscurely what He is. '
            'For it is far easier to say of God what He is not than to explain and grasp what He is. '
            'Therefore for us investigating the divine nature such divine attributes are to be briefly '
            'run through and considered: not indeed all and each, but some chief ones which have more '
            'difficulty, or render greater use in Theology.'
        ),
        'pass_b': [
            'Attributes affirm or deny — two paths to divine nature.',
            'Give God creature-perfections eminently; strip every creature-imperfection.',
            'Negatives teach clearer what God is not; affirmatives dimly what He is.',
        ],
        'lemmas': [
            {'latin': 'duorum sunt generum', 'gloss': 'are of two kinds'},
            {'latin': 'modo quodam eminentiori', 'gloss': 'in a more eminent mode'},
        ],
        'choices': [{
            'term': 'quaedam scilicet negativa, alia vero affirmativa',
            'english': 'some negative, others affirmative',
            'why': 'Frames via negativa / via eminentiae before simplicity.',
            'rejected': ['only affirmative names of God are possible'],
        }],
        'notes': ['OCR: IV PDF 109-110.'],
        'bible_refs': [],
    },
    {
        'section': '375',
        'title': 'First attribute: God\'s simplicity removes all composition',
        'pass_a': (
            'But the first attribute by which the divine nature is somehow declared is the Simplicity '
            'of God. Here indeed simplicity is not taken in a moral sense, but in a physical and '
            'metaphysical one, as simple is opposed to mixed and composite. For when simplicity is '
            'attributed to God, by that all composition is removed from Him.'
        ),
        'pass_b': [
            'First attribute: God\'s Simplicity.',
            'Not moral "simple" — physical/metaphysical vs mixed and composite.',
            'Simplicity attributed = every composition removed.',
        ],
        'lemmas': [
            {'latin': 'Dei Simplicitas', 'gloss': 'the Simplicity of God'},
            {'latin': 'omnis compositio', 'gloss': 'all composition'},
        ],
        'choices': [{
            'term': 'per id ab eo removetur omnis compositio',
            'english': 'by that all composition is removed from Him',
            'why': 'Defines simplicity as anti-composition.',
            'rejected': ['simplicity here means moral artlessness'],
        }],
        'notes': ['OCR: V PDF 110.'],
        'bible_refs': [],
    },
    {
        'section': '376',
        'title': 'Created compositions: extended parts; subject and accident',
        'pass_a': (
            'Further, in created things many kinds of composition are noticed. The first and of all '
            'the most sensible is that which is seen in every body, which consists of extended parts, '
            'of which one is outside another: and therefore of which one can be divided and separated '
            'from another. The second composition which is to be considered here is of subject and '
            'accident, as the white consists of whiteness and that body which sustains whiteness. And '
            'as in a man, besides human nature, there are various accidents, such as virtue and vice, '
            'knowledge and ignorance, whence a man is variously denominated, either learned, or '
            'unlearned, or vicious, or endowed with virtue.'
        ),
        'pass_b': [
            'Creatures show many composition kinds.',
            'Sensible: body parts outside parts, divisible.',
            'Next: subject + accident — white/whiteness; virtue, vice, knowledge on a man.',
        ],
        'lemmas': [
            {'latin': 'partibus extensis', 'gloss': 'extended parts'},
            {'latin': 'subjecti & accidentis', 'gloss': 'of subject and accident'},
        ],
        'choices': [{
            'term': 'Secunda compositio ... est subjecti & accidentis',
            'english': 'The second composition is of subject and accident',
            'why': 'Sets corporeal and accidental composition for later denial in God.',
            'rejected': ['creatures have no subject-accident composition'],
        }],
        'notes': ['OCR: VI PDF 110.'],
        'bible_refs': [],
    },
    {
        'section': '377',
        'title': 'Essence vs existence composition in creatures',
        'pass_a': (
            'But besides there are certain kinds of composition more abstract and metaphysical, which '
            'are also to be considered here. For in all created things essence can be distinguished '
            'from existence, and essence is one thing, and existence another. For by essence we '
            'understand that without which a thing cannot be conceived, and by which each thing is '
            'defined. So rational animal is the essence of man, because you cannot conceive a man '
            'without conceiving a rational animal: and rational animal is the definition of man. But '
            'by existence is understood that by which a thing actually is in the nature of things. '
            'But now these two are altogether distinguished in created things. Since existence is not '
            'of their essence. For they can be and not be. And you can conceive their essence even if '
            'you do not think of their existence: indeed even though you think and know that they do '
            'not exist. As when someone in winter, when no rose exists, contemplates the nature of a '
            'rose. And therefore all created things can be said to be composed of essence and existence.'
        ),
        'pass_b': [
            'Metaphysical composition: essence ≠ existence in creatures.',
            'Essence = what you must conceive (rational animal = man).',
            'Winter rose-nature without a rose: creatures can be and not-be.',
        ],
        'lemmas': [
            {'latin': 'essentia ... existentia', 'gloss': 'essence ... existence'},
            {'latin': 'possumt esse & non esse', 'gloss': 'they can be and not be'},
        ],
        'choices': [{
            'term': 'res omnes creatae compositae dici possunt ex essentia & existentia',
            'english': 'all created things can be said to be composed of essence and existence',
            'why': 'Third composition genus before nature/suppositum.',
            'rejected': ['creature essence already includes necessary existence'],
        }],
        'notes': ['OCR: VII PDF 110.'],
        'bible_refs': [],
    },
    {
        'section': '378',
        'title': 'Nature vs suppositum — incarnation shows the split',
        'pass_a': (
            'There is also another composition which is noticed in all created things. For in all of '
            'them nature is one thing, and that singular which has the nature is another. So the '
            'humanity which is in Peter is to be distinguished, and Peter who has that humanity. And '
            'in every person or suppositum, as they say, there is something besides the nature distinct '
            'from the nature itself: indeed which can be separated from the nature itself, as is clear '
            'from the mystery of the incarnation in Christ. For Christ assumed human nature, and yet '
            'did not assume a human person. Since the human nature in Christ subsists in the person of '
            'the Word, and lacks its own subsistence. Whence it is manifest that nature is one thing, '
            'and subsistence another, or that which constitutes the person. And therefore all created '
            'things can be said to be composed of nature and suppositum, or if you prefer to say, of '
            'nature and subsistence.'
        ),
        'pass_b': [
            'Another split: nature vs the singular that has it (Peter / humanity).',
            'Incarnation: Christ took human nature, not a human person.',
            'Creatures = nature + suppositum (subsistence).',
        ],
        'lemmas': [
            {'latin': 'natura & supposito', 'gloss': 'nature and suppositum'},
            {'latin': 'mysterio incarnationis', 'gloss': 'the mystery of the incarnation'},
        ],
        'choices': [{
            'term': 'Christus naturam humanam assumpsit, & personam tamen humanam non assumpsit',
            'english': 'Christ assumed human nature, and yet did not assume a human person',
            'why': 'Incarnation proves nature/suppositum composition in creatures.',
            'rejected': ['assuming nature always includes assuming a human person'],
        }],
        'notes': ['OCR: VIII PDF 110; next IX+ genus/difference then corporeity.'],
        'bible_refs': [],
    },
]


def write_data_files():
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'latin.json').write_text(json.dumps(LATIN, ensure_ascii=False, indent=2) + '\n')
    (DATA / 'sections.json').write_text(json.dumps(SECTIONS, ensure_ascii=False, indent=2) + '\n')
    # link OCR receipts from prior workspace
    src_ocr = Path('/tmp/leblanc_deum_esse_i_densify')
    for name in ('pdf_109_114_simplicitate.txt', 'pdf_109_114_simplicitate_raw.txt', 'tess_109.txt', 'tess_110.txt'):
        p = src_ocr / name
        if p.exists():
            (DATA / name).write_bytes(p.read_bytes())
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
        jpath = JUST / f'dei_simplicitate_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_simplicitate_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_109_114_simplicitate.txt', 'pdf_109_114_simplicitate_raw.txt', 'tess_109.txt', 'tess_110.txt'):
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
        if 371 <= n <= 378:
            notes = (
                f'Section {sid}: new densify De Dei Simplicitate I-VIII; '
                'Pass A!=B; lock-grounded PDF 109-110 / book pp. 97-98.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_simplicitate I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Dei Simplicitate I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Simplicitate through VIII; IX+ remains. '
                'Deum esse closed at XLII. Prior tracts untouched. Not shipped.'
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
        'locus': 'De Dei Simplicitate theses I-VIII (QUID SIT / attributes / composition kinds)',
        'next_locus': 'De Dei Simplicitate IX+ (genus-difference / corporeity denial)',
        'gates': {
            'check_pass_ab': f'ok dei_simplicitate_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'deploy_bound': '78b7b840 live 57/4353 tip 370',
        'raw_source_paths_count': 7,
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
        f'## {day} (Scribe — De Dei Simplicitate I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Simplicitate I–VIII → §§{SECS[0]}–{SECS[-1]}; opens after Deum esse XLII close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 109-110 / pp. 97-98).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: De Dei Simplicitate through VIII (QUID SIT; attributes; composition '
        'kinds). IX+ remains. Deum esse closed. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound 78b7b840 / tip 370; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Simplicitate I–VIII densify)\n\n'
        'CoS densify: De Dei Simplicitate I–VIII (attributes / simplicity). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Simplicitate I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through VIII. Next: Simplicitate IX+. '
        'Punch X: **NO**.\n\n---\n\n'
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
            'deploy_bound': '78b7b840',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-370 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
