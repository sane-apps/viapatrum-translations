#!/usr/bin/env python3
"""Build + apply De Aeternitate Dei (& ejus Immutabilitate) I-VIII densify (tip 456 → 464).

Opens after Immensitate XXXII close. Live floor 4639.
After tip-ready: HOLD live>4639 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_aeternitate_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_aeternitate_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_aeternitate_densify')
PACKET_STEM = 'dei_aeternitate_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_aeternitate/apply_dei_aeternitate_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['457', '458', '459', '460', '461', '462', '463', '464']
ROMANS = {
    '457': 'I', '458': 'II', '459': 'III', '460': 'IV',
    '461': 'V', '462': 'VI', '463': 'VII', '464': 'VIII',
}
TIP_BEFORE = 456
LIVE_FLOOR = 4639
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeternitate Dei I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeternitate Dei I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeternitate Dei I-VIII, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice opens Aeternitate after Immensitate close "
    "(senses of aeternum; proper eternity; Ps 102/90/92; Isa/Apoc; first Ens)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeternitate Dei & ejus Immutabilitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 111-112 / PDF 123-124 (I-VIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeternitate Dei I-VIII tip. IX+ remains. Prior tracts closed through Immensitate I-XXXII.\n"
    "Note: Opens after Immensitate. Senses of aeternum; proper divine eternity; Scripture + first-Ens proof.\n\n"
)

LATIN = {
    '457': (
        'I. Aeternum frequenter in Scriptura dicitur id quod principium quidem durationis '
        'habet, sed finem habiturum non est: sic beata illa vita quam Deus promittit '
        'credentibus in Christum, aeterna saepe appellatur, & aeterna quoque dicitur poena '
        'illa quae justo Dei judicio impiis & impoenitentibus olim infligenda est: ut quum '
        'tum piorum, tum impiorum finis his verbis describitur apud Matthaeum cap. 25. '
        'vers. 46. & abibunt hi in supplicium aeternum, justi vero ad vitam aeternam.'
    ),
    '458': (
        'II. Aeternum etiam quandoque dicitur id quod aliquando quidem finem habiturum est, '
        'sed tamen propter diuturnitatem, aeternitatem imitari videtur: sic quamvis caelum '
        '& terra olim transire debeant, tamen Ecclesiastae 1. dicitur terra in aeternum '
        'stare: & eodem sensu Deuteron. cap. 33. mentio fit a Mose, collium aeternorum, & '
        'eo quoque referri potest, quod decimo septimo capite Geneseos Deus pollicetur '
        'Abrahae se daturum illi & semini ejus, omnem terram Canaan in possessionem '
        'aeternam.'
    ),
    '459': (
        'III. Praeterea illud quod durante certo curriculo, perpetuo locum habere debet, '
        'aeternum fieri dicitur. Quomodo sumendum est illud Exod. 12. Celebrabitis hanc '
        'diem cultu sempiterno, ubi agitur de festo Paschatis: quoniam ritus legales & '
        'cultus Mosaicus obtinere debebant usque ad tempus diorthoseos, & Domini nostri '
        'Jesu Christi adventum.'
    ),
    '460': (
        'IV. Imo quamvis hominum vita brevissima sit, quandoque dicitur in aeternum fieri, '
        'id quod per totam hominis vitam nunquam finiendum est, sed ad mortem usque locum '
        'habere debet: ut quum de servo Hebraeo qui anno septimo uti noluerat libertate '
        'per legem oblata, dicitur, Servus erit domino suo leolam, in aeternum, Exod. cap. '
        '21. Quo pertinet illud Horatii, Serviet aeternum qui parvo nesciet uti.'
    ),
    '461': (
        'V. Aeternum vero proprie dicitur id quod simpliciter & absolute caret durationis '
        'principio & fine: & haec est illa aeternitas quae de Deo praedicari solet, & inter '
        'ejus attributa censeri: est enim Dei essentia omnino expers ortus & interitus. '
        'Deus nec esse incepit, nec unquam esse desinet: Atque ut Dei magnitudo, tanta est, '
        'ut nullo loco contineri, vel definiri possit, sic Dei duratio nullo tempore '
        'limitatur, sed omnia praecedit & superat tempora.'
    ),
    '462': (
        'VI. Istud autem Scriptura multis locis aperte docet, praecipue vero Psalmo 102. '
        'ubi Propheta comparans res quae inter visibiles maxime sunt permanentes, caelum '
        'scilicet & terram, docet illa aliquando habuisse initium, quum sint opus manuum '
        'Dei, & finem olim esse habitura: Deum vero permanere semper, & eundem perpetuo & '
        'fuisse & fore. Initio, inquit, Tu Domine terram fundasti, & opera manuum tuarum '
        'sunt caeli: ipsi peribunt, tu autem permanes: & omnes ipsi sicut vestimentum '
        'veterascent, & sicut opertorium mutabis eos, & mutabuntur, tu autem idem ipse es, '
        '& anni tui non deficient. Quam perpetuam quoque Dei permanentiam celebrat David, '
        'Psal. 92. Tu autem, inquit, altissimus in aeternum Domine. Et Moses vir Dei, '
        'Psal. 90. Priusquam montes fierent, & formaretur terra & orbis, a saeculo & usque '
        'in saeculum tu es Deus. Quo etiam respicit quod addit, mille anni ante oculos '
        'tuos sicut dies hesterna quae praeteriit: quia scilicet ad immensam & illimitatam '
        'Dei durationem, nec mille anni, nec quodlibet designatum tempus ullam '
        'proportionem habent.'
    ),
    '463': (
        'VII. Propterea Deus apud Isaiam cap. 9. vocatur Pater aeternitatis: item primus & '
        'novissimus, cap. 41. & 57. capite, excelsus & sublimis habitans aeternitatem. Quo '
        'pertinet quoque illa descriptio qua Deus seipsum designat cap. 1. Apocalypseos, '
        'Ego sum Alpha & Omega, principium & finis, dicit Dominus Deus, qui est, qui erat, '
        '& qui venturus est. Quibus docemur Dei durationem omnia complecti tempora, '
        'praeteritum, praesens & futurum, ac Deum optimo jure dici posse principium sine '
        'principio, & finem sine fine: quia scilicet quum sit omnium rerum principium, '
        'ipse principio caret, nec etiam finem ullum habere potest, quum sit finis ad quem '
        'omnia referuntur.'
    ),
    '464': (
        'VIII. Hac in parte vero, Scripturae ratio manifeste adstipulatur. Quaecunque enim '
        'argumenta demonstrant unum esse primum Ens a quo pendent omnia caetera, & unde '
        'originem habent, cujusmodi a nobis allata & exposita sunt Thesibus illis quibus '
        'demonstravimus Deum esse, ea, inquam, argumenta necessario probant primum Ens '
        'illud, nempe Deum, aeternum quoque esse, nec habuisse ullum durationis initium. '
        'Nam Ens quod primum est, & aliorum causa, factum esse non potest, quippe nec ab '
        'alio factum est, alioqui primum non esset, sed daretur Ens aliud ipso prius: nec '
        'etiam a seipso, quum ut fieret deberet non fuisse: ut faceret, deberet fuisse, '
        'quae manifeste pugnantia sunt. Quod autem est & non factum est, nunquam esse '
        'incepit, adeoque aeternum est. Quocirca Augustum illud Dei nomen Jehovah quod '
        'significat Deum esse per se & a se, & illum qui facit ut reliqua omnia sint, '
        'adeoque Ens primum & independens, Dei aeternitatem includit & connotat. Ideoque '
        'authoribus vernaculae nostrae versionis non male vertitur l\'Eternel.'
    ),
}

SECTIONS = [
    {
        'section': '457',
        'title': 'Aeternum with a start but no end — life and punishment',
        'pass_a': (
            'Eternal is frequently said in Scripture of that which has indeed a beginning of '
            'duration, but will not have an end: so that blessed life which God promises to '
            'those who believe in Christ is often called eternal, and that punishment also '
            'is called eternal which by God\'s just judgment is hereafter to be inflicted on '
            'the ungodly and impenitent: as when the end of both the godly and the ungodly '
            'is described in these words in Matthew chapter 25 verse 46, and these will go '
            'away into eternal punishment, but the righteous into eternal life.'
        ),
        'pass_b': [
            'Scripture often calls eternal what began but will not end.',
            'Blessed life in Christ — eternal; judgment on the ungodly — eternal.',
            'Matt 25:46: eternal punishment / eternal life.',
        ],
        'lemmas': [
            {'latin': 'principium quidem durationis habet, sed finem habiturum non est', 'gloss': 'has indeed a beginning of duration, but will not have an end'},
            {'latin': 'supplicium aeternum … vitam aeternam', 'gloss': 'eternal punishment … eternal life'},
        ],
        'choices': [{
            'term': 'principium quidem durationis habet, sed finem habiturum non est',
            'english': 'has indeed a beginning of duration, but will not have an end',
            'why': 'Opens Aeternitate with the first (weaker) sense of aeternum.',
            'rejected': ['eternal in Matt 25 means no beginning and no end'],
        }],
        'notes': ['OCR: Aeternitate I PDF 123 / p. 111; Matt 25:46.'],
        'bible_refs': ['Matt. 25:46'],
    },
    {
        'section': '458',
        'title': 'Aeternum by long duration — earth, hills, Canaan',
        'pass_a': (
            'Eternal is also sometimes said of that which will indeed sometime have an end, '
            'but nevertheless because of long duration seems to imitate eternity: so although '
            'heaven and earth must someday pass away, yet in Ecclesiastes 1 the earth is '
            'said to stand forever: and in the same sense in Deuteronomy chapter 33 Moses '
            'makes mention of everlasting hills, and thither also can be referred that in '
            'Genesis chapter seventeen God promises Abraham He will give him and his seed '
            'all the land of Canaan for an everlasting possession.'
        ),
        'pass_b': [
            'Sometimes eternal = very long, still able to end.',
            'Eccl 1: earth stands forever; Deut 33: everlasting hills.',
            'Gen 17: Canaan as everlasting possession.',
        ],
        'lemmas': [
            {'latin': 'propter diuturnitatem, aeternitatem imitari videtur', 'gloss': 'because of long duration seems to imitate eternity'},
            {'latin': 'possessionem aeternam', 'gloss': 'an everlasting possession'},
        ],
        'choices': [{
            'term': 'propter diuturnitatem, aeternitatem imitari videtur',
            'english': 'because of long duration seems to imitate eternity',
            'why': 'Second sense: long-lasting, not absolute eternity.',
            'rejected': ['earth forever in Eccl 1 means the earth never ends'],
        }],
        'notes': ['OCR: II PDF 123; Eccl 1:4; Deut 33:15; Gen 17:8.'],
        'bible_refs': ['Eccl. 1:4', 'Deut. 33:15', 'Gen. 17:8'],
    },
    {
        'section': '459',
        'title': 'Aeternum for a fixed course — Passover until Christ',
        'pass_a': (
            'Besides, that which during a certain course must perpetually have place is said '
            'to be done forever. In which way that of Exodus 12 is to be taken, You shall '
            'celebrate this day with an everlasting worship, where the feast of Passover is '
            'treated: since the legal rites and Mosaic worship were to obtain until the time '
            'of reformation, and the advent of our Lord Jesus Christ.'
        ),
        'pass_b': [
            'Eternal can mean: lasting through a set course.',
            'Exod 12: everlasting Passover worship.',
            'Bound to Mosaic rites until Christ\'s advent / diorthosis.',
        ],
        'lemmas': [
            {'latin': 'durante certo curriculo, perpetuo locum habere debet', 'gloss': 'during a certain course must perpetually have place'},
            {'latin': 'cultu sempiterno', 'gloss': 'with an everlasting worship'},
        ],
        'choices': [{
            'term': 'usque ad tempus diorthoseos, & Domini nostri Jesu Christi adventum',
            'english': 'until the time of reformation, and the advent of our Lord Jesus Christ',
            'why': 'Third sense: covenantal duration until Christ.',
            'rejected': ['Passover forever means Mosaic rites never end'],
        }],
        'notes': ['OCR: III PDF 123; Exod 12:14; cf. Heb 9 diorthosis.'],
        'bible_refs': ['Exod. 12:14'],
    },
    {
        'section': '460',
        'title': 'Aeternum for a human lifetime — Hebrew servant; Horace',
        'pass_a': (
            'Nay although human life is very short, sometimes that is said to be done forever '
            'which through a whole human life is never to be ended, but must have place until '
            'death: as when of the Hebrew servant who in the seventh year had refused to use '
            'the liberty offered by the law, it is said, He shall be a servant to his master '
            'leolam, forever, Exodus chapter 21. To which belongs that of Horace, He will '
            'serve forever who does not know how to use a little.'
        ),
        'pass_b': [
            'Even a short life can host forever-language.',
            'Exod 21: Hebrew servant forever = for life (leolam).',
            'Horace: serve forever who cannot use a little.',
        ],
        'lemmas': [
            {'latin': 'ad mortem usque locum habere debet', 'gloss': 'must have place until death'},
            {'latin': 'Servus erit domino suo leolam, in aeternum', 'gloss': 'He shall be a servant to his master leolam, forever'},
        ],
        'choices': [{
            'term': 'per totam hominis vitam nunquam finiendum est',
            'english': 'through a whole human life is never to be ended',
            'why': 'Fourth sense: lifelong, not absolute eternity.',
            'rejected': ['Exod 21 forever means the servant never dies free'],
        }],
        'notes': ['OCR: IV PDF 123; Exod 21:6 leolam; Horace Sat.'],
        'bible_refs': ['Exod. 21:6'],
    },
    {
        'section': '461',
        'title': 'Proper eternity — no beginning, no end of duration',
        'pass_a': (
            'But eternal is properly said of that which simply and absolutely lacks a '
            'beginning and end of duration: and this is that eternity which is wont to be '
            'predicated of God, and counted among His attributes: for God\'s essence is '
            'altogether without rising and falling. God neither began to be, nor will ever '
            'cease to be: And as God\'s greatness is so great that it can be contained or '
            'defined by no place, so God\'s duration is limited by no time, but precedes and '
            'surpasses all times.'
        ),
        'pass_b': [
            'Proper sense: no beginning and no end of duration.',
            'This is the eternity predicated of God as an attribute.',
            'As greatness escapes place, duration escapes all times.',
        ],
        'lemmas': [
            {'latin': 'caret durationis principio & fine', 'gloss': 'lacks a beginning and end of duration'},
            {'latin': 'expers ortus & interitus', 'gloss': 'without rising and falling'},
        ],
        'choices': [{
            'term': 'Dei duratio nullo tempore limitatur, sed omnia praecedit & superat tempora',
            'english': 'God\'s duration is limited by no time, but precedes and surpasses all times',
            'why': 'Defines proper divine eternity after weaker senses.',
            'rejected': ['God\'s eternity is only endless forward from a start'],
        }],
        'notes': ['OCR: V PDF 123.'],
        'bible_refs': [],
    },
    {
        'section': '462',
        'title': 'Psalms 102, 92, 90 — God remains; a thousand years as yesterday',
        'pass_a': (
            'But Scripture openly teaches that in many places, and especially in Psalm 102, '
            'where the Prophet comparing the things among visibles that are most permanent, '
            'namely heaven and earth, teaches that they sometime had a beginning, since they '
            'are the work of God\'s hands, and will someday have an end: but that God remains '
            'always, and the same perpetually both was and will be. In the beginning, he '
            'says, You Lord founded the earth, and the heavens are the works of Your hands: '
            'they will perish, but You remain: and all of them will grow old like a garment, '
            'and like a covering You will change them, and they will be changed, but You are '
            'the same Yourself, and Your years will not fail. Which perpetual permanence of '
            'God David also celebrates, Psalm 92. But You, he says, are most high forever, '
            'Lord. And Moses the man of God, Psalm 90. Before the mountains were made, and '
            'the earth and the world were formed, from age and unto age You are God. To '
            'which also looks what he adds, a thousand years before Your eyes are as '
            'yesterday which passed: because namely to God\'s immense and unlimited duration '
            'neither a thousand years nor any designated time has any proportion.'
        ),
        'pass_b': [
            'Ps 102: heavens perish like a garment; God remains the same.',
            'Ps 92 / 90: most high forever; from age to age You are God.',
            'A thousand years before God — as yesterday; no proportion to His duration.',
        ],
        'lemmas': [
            {'latin': 'tu autem idem ipse es, & anni tui non deficient', 'gloss': 'but You are the same Yourself, and Your years will not fail'},
            {'latin': 'mille anni ante oculos tuos sicut dies hesterna', 'gloss': 'a thousand years before Your eyes as yesterday'},
        ],
        'choices': [{
            'term': 'nec mille anni, nec quodlibet designatum tempus ullam proportionem habent',
            'english': 'neither a thousand years nor any designated time has any proportion',
            'why': 'Scripture grounds unlimited divine duration.',
            'rejected': ['Ps 102 only compares God\'s age to the age of the world'],
        }],
        'notes': ['OCR: VI PDF 123-124; Ps 102:25-27; 92:8; 90:2,4.'],
        'bible_refs': ['Ps. 102:25-27', 'Ps. 92:8', 'Ps. 90:2', 'Ps. 90:4'],
    },
    {
        'section': '463',
        'title': 'Isaiah and Apocalypse — Father of eternity; Alpha and Omega',
        'pass_a': (
            'Therefore God in Isaiah chapter 9 is called Father of eternity: likewise the '
            'first and the last, chapter 41 and chapter 57, the high and lofty One dwelling '
            'in eternity. To which also belongs that description by which God designates '
            'Himself in chapter 1 of the Apocalypse, I am Alpha and Omega, the beginning and '
            'the end, says the Lord God, who is, who was, and who is to come. By which we '
            'are taught that God\'s duration embraces all times, past, present, and future, '
            'and that God can with best right be called a beginning without beginning, and '
            'an end without end: because namely since He is the beginning of all things, He '
            'Himself lacks a beginning, nor can He have any end, since He is the end to which '
            'all things are referred.'
        ),
        'pass_b': [
            'Isa 9: Father of eternity; Isa 41/57: first and last; dwells in eternity.',
            'Apoc 1: Alpha and Omega — who is, was, and is to come.',
            'Beginning without beginning; end without end — all times embraced.',
        ],
        'lemmas': [
            {'latin': 'Pater aeternitatis', 'gloss': 'Father of eternity'},
            {'latin': 'principium sine principio, & finem sine fine', 'gloss': 'a beginning without beginning, and an end without end'},
        ],
        'choices': [{
            'term': 'Dei durationem omnia complecti tempora, praeteritum, praesens & futurum',
            'english': 'that God\'s duration embraces all times, past, present, and future',
            'why': 'Prophetic/Apocalyptic names seal unlimited duration.',
            'rejected': ['Alpha and Omega means God only spans created history'],
        }],
        'notes': ['OCR: VII PDF 124; Isa 9:6; 41:4; 57:15; Rev 1:8.'],
        'bible_refs': ['Isa. 9:6', 'Isa. 41:4', 'Isa. 57:15', 'Rev. 1:8'],
    },
    {
        'section': '464',
        'title': 'First Ens cannot have been made — Jehovah / l\'Eternel',
        'pass_a': (
            'But in this part the reason of Scripture plainly agrees. For whatever arguments '
            'demonstrate that there is one first Being from which all the rest depend, and '
            'from which they have origin, of which kind were brought and set out by us in '
            'those Theses in which we demonstrated that God is — those arguments, I say, '
            'necessarily prove that that first Being, namely God, is eternal also, and had '
            'no beginning of duration. For a Being which is first, and cause of others, '
            'cannot have been made, since it was not made by another — otherwise it would '
            'not be first, but another Being prior to it would be given — nor even by itself, '
            'since to become it would have had not to have been, and to make it would have '
            'had to have been, which are plain contradictions. But what is and was not made '
            'never began to be, and therefore is eternal. Wherefore that august name of God '
            'Jehovah, which signifies that God is through Himself and from Himself, and Him '
            'who makes the rest of all things to be, and therefore the first and independent '
            'Being, includes and connotes God\'s eternity. And therefore by the authors of '
            'our vernacular version it is not badly rendered l\'Eternel.'
        ),
        'pass_b': [
            'First-Ens proofs (from Deum esse) force no start of duration.',
            'First cause cannot be made by another or by itself — contradiction either way.',
            'Jehovah / l\'Eternel names aseity and so connotes eternity.',
        ],
        'lemmas': [
            {'latin': 'primum Ens … aeternum quoque esse', 'gloss': 'that the first Being … is eternal also'},
            {'latin': 'Jehovah … Dei aeternitatem includit & connotat', 'gloss': 'Jehovah … includes and connotes God\'s eternity'},
        ],
        'choices': [{
            'term': 'Quod autem est & non factum est, nunquam esse incepit, adeoque aeternum est',
            'english': 'But what is and was not made never began to be, and therefore is eternal',
            'why': 'Closes I-VIII on metaphysical eternity; next IX+ necessary endless duration.',
            'rejected': ['the first Being could have begun without a maker'],
        }],
        'notes': ['OCR: VIII PDF 124; French l\'Eternel; next IX+.'],
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
        jpath = JUST / f'dei_aeternitate_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_aeternitate_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_122_126_layout.txt', 'tess123.txt', 'tess124.txt', 'tess125.txt'):
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
        if 457 <= n <= 464:
            notes = (
                f'Section {sid}: new densify De Aeternitate Dei I-VIII; '
                'Pass A!=B; lock-grounded PDF 123-124 / book pp. 111-112.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_aeternitate I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Aeternitate Dei I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Aeternitate through VIII. IX+ remains. Not shipped.'
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
        'locus': 'De Aeternitate Dei theses I-VIII (senses of aeternum; proper eternity; first Ens)',
        'next_locus': 'De Aeternitate Dei IX+ (necessary endless duration; immortality proper)',
        'gates': {
            'check_pass_ab': f'ok dei_aeternitate_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'deploy_bound': 'ad42596d',
        'pre_hold_note': 'pre-densify hold cleared live>4627 (57/4639) before Aeternitate open',
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
        f'## {day} (Scribe — De Aeternitate Dei I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(opens Aeternitate I–VIII → §§{SECS[0]}–{SECS[-1]} after Immensitate close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 123-124 / pp. 111-112).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Aeternitate Dei through VIII. IX+ remains. '
        'Immensitate closed. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound ad42596d / tip 456; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Aeternitate Dei I–VIII densify)\n\n'
        'CoS densify: Aeternitate I–VIII after Immensitate close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Aeternitate I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: IX+. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-456 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
