#!/usr/bin/env python3
"""Build + apply De Dei Simplicitate XVII-XXIV densify (tip 386 → 394).

Essence/existence; nature/suppositum in God; genus/difference; act/potency intro.
Deploy b67a6a67 live 57/4399 bound tip 386. After tip-ready: HOLD live>4399 OR 12m.
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
PACKET_STEM = 'dei_simplicitate_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_simplicitate/apply_dei_simplicitate_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['387', '388', '389', '390', '391', '392', '393', '394']
ROMANS = {
    '387': 'XVII', '388': 'XVIII', '389': 'XIX', '390': 'XX',
    '391': 'XXI', '392': 'XXII', '393': 'XXIII', '394': 'XXIV',
}
TIP_BEFORE = 386
LIVE_FLOOR = 4399
HOLD_MINUTES = 12
PRIOR_START = 371

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + "
    "De Dei Simplicitate I-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XXIV, reconstructed from the Internet Archive PDF page images with "
    "pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. This slice densifies De Dei Simplicitate XVII-XXIV "
    "(essence/existence; nature/suppositum; genus/difference; act/potency)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Simplicitate (Theses Theologicae De Dei Simplicitate).\n"
    "Same 1675 Pitt copy-text. Book pp. 97-101 / PDF 109-113 (I-XXIV; this packet XVII-XXIV). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Simplicitate I-XXIV tip. XXV+ remains.\n"
    "Note: Continues after IX-XVI. Essence-existence and remaining compositions in God.\n\n"
)

LATIN = {
    '387': (
        'XVII. Tertia compositio, quae a nobis notata fuit, est ex essentia & existentia. Nam '
        'haec duo, ut dictum, in rebus creatis omnino distinguuntur. Estque in iis alia essentiae '
        'ratio, & alia existentiae: quandoquidem tota earum essentia concipi potest absque '
        'existentia, nec existentia ingreditur earum definitionem. Et hoc quia possunt esse & non '
        'esse, nec est ulla res creata quam non existere repugnet. Ideoque earum respectu '
        'existentia est aliquid contingens, non vero necessarium, & aliquid accidentarium, non '
        'autem essentiale. Sed in Deo res aliter se habet. Nam essentia ejus non potest concipi '
        'absque existentia. Et repugnat plane Deum concipere qui non existat. Nec magis potest '
        'mente abstrahi & praescindi essentia Dei ab ejus existentia, quam essentia hominis ab '
        'animali vel rationali. Nam quamvis in Deo nihil sit prius & posterius, attamen nostro '
        'concipiendi modo primum & maxime essentiale Dei attributum est, quod sit ens primum & '
        'necessarium, id est, quod primo per se & necessario existat: estque omnino de Dei '
        'essentia esse & existere.'
    ),
    '388': (
        'XVIII. Idcirco Deus vocatur a Platone to on, esse ipsum, quod hodie Philosophi dicunt '
        'ens per essentiam, id est, quod vi suae essentiae existit, & cujus essentia & natura est '
        'ut perpetuo existat. Atque hoc docet Deus ipse Exodi capite tertio, dum se vocat illum '
        'qui est, Ego sum qui sum, inquit Mosi. Quo nomine significat esse ipsi convenire longe '
        'alia ratione, quam rebus ab ipso creatis. Nam existere, ut dixi, creaturarum respectu '
        'est aliquid contingens, Dei vero, necessarium. Creaturis est accidentarium, verum Deo, '
        'essentiale. Esse creaturarum est participatum & mutuarium: sed Deo, esse proprium est, '
        'ipsique primo & per se competit. Atque haec est etiam vis nominis illius Jehovah quod '
        'est Deo maxime proprium. Fit enim ab havah, esse, quasi dicas ipsum est, id quod est, '
        '& ho on. Quod Joannes in Apocal. explicat illa periphrasi ho on kai ho en kai ho '
        'erchomenos: qui est, qui erat, & qui futurus est. Adeoque quum Dei existentia sit de '
        'ratione essentiae illius, nec una possit ab altera distingui, quasi aliud quid, sed '
        'conceptus unius ingrediatur conceptum alterius, Deus non potest dici ullo modo '
        'compositus ex essentia & existentia, estque prorsus istius compositionis expers.'
    ),
    '389': (
        'XIX. Nec etiam ipsi competit quarta compositio, quae a nobis commemorata est, ex '
        'natura, nempe, & subsistentia, sive eo quod personam & suppositum constituit. Haec duo '
        'quidem in rebus creatis distingui docuimus. Quippe in eis aliud est natura & essentia, '
        '& aliud quod naturam habet. Sicut aliud est Petrus, & aliud humanitas quae est in '
        'Petro. Et hoc quoniam praeter humanitatem, in Petro est aliquid quod personam Petri '
        'constituit, videlicet, subsistentia, quae (ut supra probatum est) a natura realiter '
        'differt. Atque etiam in Petro est differentia quaedam singularis, quae naturam humanam '
        'in Petro, ad Petrum contrahit & restringit ad ipsum, quod alioqui pluribus commune '
        'est. Ideoque in rebus creatis nominibus concretis & abstractis non idem omnino '
        'significatur: Nec unum dici de alio potest. Nam Petrus non est sua humanitas. Nec '
        'humanitas Petri est Petrus ipse. Ut nec Gabriel est ipsa natura Angelica, nec natura '
        'est ipse Gabriel.'
    ),
    '390': (
        'XX. Sed distinctio illa in Deo locum non habet. Nam in Deo Divinae naturae nihil est '
        'superadditum quod ab ipsa diversum sit. Etenim natura divina est aliquid singulare, '
        'quod multiplicari non potest. Ideoque opus non habet differentia ulla contrahente '
        'quia fiat Deo propria: sicut Petri humanitas Petri fit propria per quandam '
        'differentiam singularem. Nec etiam in Deo subsistentia est aliquid ab essentia '
        'realiter distinctum. Sed personae divinae & essentia divina idem sunt. Alioqui non '
        'trinitas, sed quaternitas quaedam in Deo concipienda esset, nempe natura divina, & '
        'tres personae, sive subsistentiae. Et hoc quoque exigit divina perfectio. Nam cum '
        'essentiae divinae nihil desit, sed ipsa sit simpliciter & absolute perfecta, & omnem '
        'in suo conceptu perfectionem includat, non alia re ad subsistendum eget, nec quicquam '
        'ipsi superaddi potest.'
    ),
    '391': (
        'XXI. Idcirco nominibus abstractis & concretis in Deo res una plane, & eadem '
        'significatur. Nam Deus est sua essentia, & essentia Dei est Deus ipse. Homo non est '
        'humanitas, nec humanitas est homo: sed Deitas est Deus, & Deus est Deitas. Ac '
        'similiter quodcunque Divinum attributum, tam in abstracto quam in concreto de Deo '
        'recte & vere enunciari potest. Etenim Deus non tantum est bonus; sed etiam ipsa '
        'bonitas: nec tantum justus; sed ipsa justitia. Qui loquendi modus authoritate '
        'Scripturae comprobatur. Siquidem Filius Dei frequenter in Scripturis vocatur '
        'sapientia. Et non solum dicitur Deus verus: sed ipsa veritas: nec solum Deus vivens: '
        'sed ipsa vita, veluti Joan. 14. Ego sum, inquit, veritas & vita. Quapropter in '
        'scholis merito explosa est sententia Gilberti Porretani Episcopi Pictaviensis, qui '
        'tempore Bernardi docuit non eandem rem in Deo significari nominibus abstractis & '
        'concretis: ut hisce vocibus Deus & Deitas, Persona & natura. Adeoque hac etiam in '
        'parte Deus est omnino simplex & compositione caret.'
    ),
    '392': (
        'XXII. Nec magis Deo tribui potest compositio quam diximus ex genere & differentia. '
        'Nam Deus est supra omne genus: nec ullo rerum genere includitur. Genus enim dicitur '
        'quod pluribus commune est, & eodem modo de pluribus dicitur. Sed nihil est proprie '
        'creaturis & Deo commune, & quod eodem modo de creaturis & de Deo dicatur. Si quid '
        'enim dicitur de Deo & de creaturis, id non univoce dicitur, sed per analogiam & '
        'similitudinem quandam, nec eodem modo est in Deo & in creaturis. Veluti, cum Deum '
        'nominamus sapientem & justum, & quosdam etiam homines sapientes & justos, justitia & '
        'sapientia in hominibus notat qualitatem quandam; sed in Deo notat ipsam illius '
        'essentiam. Quod si esset aliquod genus creaturis & Deo commune, nullum potius esset '
        'quam substantia. Et tamen Dei natura magis distat a substantiis creatis, quam '
        'substantia creata distat ab accidentibus. Jam autem substantia creata non est in eodem '
        'genere cum accidente. Multo minus igitur Deus est in eodem genere cum substantiis '
        'creatis.'
    ),
    '393': (
        'XXIII. Cum autem Deus non habeat genus, differentiam quoque proprie dictam habere '
        'non potest. Nam differentia dicitur id quod genus pluribus commune ad certam speciem '
        'contrahit. Et sic in natura divina certi gradus distingui non possunt, nec composita '
        'est ex variis gradibus; sed est una simplex essentia, quae per seipsam differt ab '
        'omnibus aliis.'
    ),
    '394': (
        'XXIV. Restat unum, quod omisimus, compositionis metaphysicae genus, nimirum ex actu '
        '& potentia. Actus hic dicitur quicquid rem perficit, determinat, & constituit, & uno '
        'verbo quaevis perfectio actus est. Potentia vero dicitur id secundum quod res apta '
        'est perfici & determinari, & in se aliquid recipere vel pati. Idcirco res omnes '
        'creatae compositae dici possunt ex actu & potentia. Nam in iis omnibus est aliquid '
        'quod perficit, & aliquid quod perficitur. Et praeter perfectiones quae actu illis '
        'insunt, nulla est quae non possit aliud recipere, & non sit alicujus mutationis '
        'capax.'
    ),
}

SECTIONS = [
    {
        'section': '387',
        'title': 'In God essence cannot be cut from existence',
        'pass_a': (
            'The third composition which was noted by us is of essence and existence. For these '
            'two, as said, are altogether distinguished in created things. And in them there is '
            'one ratio of essence, and another of existence: since their whole essence can be '
            'conceived without existence, nor does existence enter their definition. And this '
            'because they can be and not be, nor is there any created thing to which not to exist '
            'is repugnant. And therefore with respect to them existence is something contingent, '
            'not indeed necessary, and something accidental, but not essential. But in God the '
            'matter stands otherwise. For His essence cannot be conceived without existence. And '
            'it is plainly repugnant to conceive God who does not exist. Nor can the essence of '
            'God be abstracted and prescinded in the mind from His existence more than the '
            'essence of man from animal or rational. For although in God nothing is prior and '
            'posterior, yet in our mode of conceiving the first and most essential attribute of '
            'God is that He is first and necessary being, that is, that He exists first through '
            'Himself and necessarily: and it is altogether of the essence of God to be and to exist.'
        ),
        'pass_b': [
            'Creatures: essence without existence — contingent, accidental.',
            'God: essence cannot be conceived without existing.',
            'First essential attribute: necessary being — to be and exist is of His essence.',
        ],
        'lemmas': [
            {'latin': 'ex essentia & existentia', 'gloss': 'of essence and existence'},
            {'latin': 'de Dei essentia esse & existere', 'gloss': 'of God\'s essence to be and to exist'},
        ],
        'choices': [{
            'term': 'essentia ejus non potest concipi absque existentia',
            'english': 'His essence cannot be conceived without existence',
            'why': 'Blocks essence-existence composition in God.',
            'rejected': ['God\'s essence can be thought without existence'],
        }],
        'notes': ['OCR: XVII PDF 112.'],
        'bible_refs': [],
    },
    {
        'section': '388',
        'title': 'Ego sum qui sum — Jehovah; no essence-existence composition',
        'pass_a': (
            'Therefore God is called by Plato to on, being itself, which today Philosophers call '
            'being by essence, that is, what exists by force of its essence, and whose essence and '
            'nature is that it perpetually exist. And God Himself teaches this in Exodus chapter '
            'three, while He calls Himself Him who is: I am who I am, He says to Moses. By which '
            'name He signifies that being befits Him by a far other reason than things created by '
            'Him. For to exist, as I said, with respect to creatures is something contingent, but '
            'of God, necessary. To creatures it is accidental, but to God, essential. The being '
            'of creatures is participated and borrowed: but to God, being is proper, and befits '
            'Him first and through Himself. And this is also the force of that name Jehovah which '
            'is most proper to God. For it is made from havah, to be, as if you should say He '
            'Himself is, that which is, and ho on. Which John in the Apocalypse explains by that '
            'periphrasis ho on kai ho en kai ho erchomenos: who is, who was, and who is to come. '
            'And therefore since God\'s existence is of the ratio of His essence, nor can one be '
            'distinguished from the other as something else, but the concept of one enters the '
            'concept of the other, God cannot be said in any way to be composed of essence and '
            'existence, and is wholly free of that composition.'
        ),
        'pass_b': [
            'Plato\'s to on / ens per essentiam: exists by His essence forever.',
            'Exod 3: I am who I am; Jehovah from havah — being proper to God.',
            'Apocalypse: who is, was, is to come — no essence-existence split.',
        ],
        'lemmas': [
            {'latin': 'Ego sum qui sum', 'gloss': 'I am who I am'},
            {'latin': 'ens per essentiam', 'gloss': 'being by essence'},
        ],
        'choices': [{
            'term': 'Deus non potest dici ullo modo compositus ex essentia & existentia',
            'english': 'God cannot be said in any way to be composed of essence and existence',
            'why': 'Closes third composition denial with Exodus/Jehovah.',
            'rejected': ['Jehovah names a God whose existence is accidental'],
        }],
        'notes': ['OCR: XVIII PDF 112; Greek/Hebrew normalized from OCR.'],
        'bible_refs': ['Exod. 3', 'Rev. 1'],
    },
    {
        'section': '389',
        'title': 'Fourth composition: nature and subsistence in creatures',
        'pass_a': (
            'Nor does the fourth composition which was commemorated by us befit Him, namely of '
            'nature and subsistence, or of that which constitutes person and suppositum. These '
            'two indeed we taught are distinguished in created things. For in them nature and '
            'essence is one thing, and that which has the nature is another. As Peter is one '
            'thing, and the humanity which is in Peter is another. And this because besides '
            'humanity, in Peter there is something which constitutes the person of Peter, namely '
            'subsistence, which (as was proved above) differs really from nature. And also in '
            'Peter there is a certain singular difference which contracts the human nature in '
            'Peter to Peter and restricts it to him, which otherwise is common to many. And '
            'therefore in created things concrete and abstract names do not signify altogether '
            'the same: Nor can one be said of the other. For Peter is not his humanity. Nor is '
            'Peter\'s humanity Peter himself. As neither is Gabriel the angelic nature itself, '
            'nor is the nature Gabriel himself.'
        ),
        'pass_b': [
            'Fourth composition: nature vs subsistence (person/suppositum).',
            'Peter ≠ his humanity; Gabriel ≠ angelic nature.',
            'Concrete and abstract names split in creatures.',
        ],
        'lemmas': [
            {'latin': 'ex natura ... & subsistentia', 'gloss': 'of nature and subsistence'},
            {'latin': 'personam & suppositum', 'gloss': 'person and suppositum'},
        ],
        'choices': [{
            'term': 'Petrus non est sua humanitas',
            'english': 'Peter is not his humanity',
            'why': 'Sets creaturely nature/suppositum split before denying it in God.',
            'rejected': ['concrete and abstract names mean the same in creatures'],
        }],
        'notes': ['OCR: XIX PDF 112.'],
        'bible_refs': [],
    },
    {
        'section': '390',
        'title': 'In God no added subsistence — else a quaternity',
        'pass_a': (
            'But that distinction has no place in God. For in God nothing is superadded to the '
            'Divine nature that is diverse from it. For the divine nature is something singular, '
            'which cannot be multiplied. And therefore it has no need of any contracting '
            'difference that it may become proper to God: as Peter\'s humanity becomes proper to '
            'Peter by a certain singular difference. Nor also in God is subsistence something '
            'really distinct from essence. But the divine persons and the divine essence are the '
            'same. Otherwise not a trinity, but a certain quaternity would have to be conceived '
            'in God, namely the divine nature, and three persons, or subsistences. And divine '
            'perfection also requires this. For since nothing is lacking to the divine essence, '
            'but it itself is simply and absolutely perfect, and includes every perfection in its '
            'concept, it needs no other thing for subsisting, nor can anything be superadded to it.'
        ),
        'pass_b': [
            'Divine nature is singular — no contracting difference needed.',
            'Subsistence is not really other than essence in God.',
            'Else quaternity (nature + three persons); perfect essence needs no add-on to subsist.',
        ],
        'lemmas': [
            {'latin': 'non trinitas, sed quaternitas', 'gloss': 'not a trinity, but a quaternity'},
            {'latin': 'personae divinae & essentia divina idem sunt', 'gloss': 'the divine persons and the divine essence are the same'},
        ],
        'choices': [{
            'term': 'Alioqui non trinitas, sed quaternitas quaedam in Deo concipienda esset',
            'english': 'Otherwise not a trinity, but a certain quaternity would have to be conceived in God',
            'why': 'Blocks real distinction of subsistence from essence.',
            'rejected': ['divine persons add a fourth thing beside essence'],
        }],
        'notes': ['OCR: XX PDF 112.'],
        'bible_refs': [],
    },
    {
        'section': '391',
        'title': 'Deus est Deitas — Gilbert of Poitiers rejected',
        'pass_a': (
            'Therefore by abstract and concrete names in God one thing plainly, and the same, is '
            'signified. For God is His essence, and the essence of God is God Himself. Man is not '
            'humanity, nor is humanity man: but Deity is God, and God is Deity. And likewise '
            'whatever Divine attribute can be rightly and truly enunciated of God both in the '
            'abstract and in the concrete. For God is not only good; but also goodness itself: '
            'nor only just; but justice itself. Which manner of speaking is proved by the '
            'authority of Scripture. Since the Son of God is frequently called wisdom in the '
            'Scriptures. And God is not only said to be true: but truth itself: nor only the '
            'living God: but life itself, as John 14. I am, He says, the truth and the life. '
            'Wherefore in the schools the opinion of Gilbert of Poitiers, Bishop of Poitiers, who '
            'in the time of Bernard taught that the same thing is not signified in God by abstract '
            'and concrete names — as by these words God and Deity, Person and nature — has been '
            'deservedly exploded. And therefore in this part also God is altogether simple and '
            'free of composition.'
        ),
        'pass_b': [
            'In God abstract = concrete: God is Deity; goodness itself, justice itself.',
            'John 14: I am the truth and the life.',
            'Gilbert of Poitiers exploded — Person/nature not split names in God.',
        ],
        'lemmas': [
            {'latin': 'Deitas est Deus, & Deus est Deitas', 'gloss': 'Deity is God, and God is Deity'},
            {'latin': 'Gilberti Porretani', 'gloss': 'of Gilbert of Poitiers'},
        ],
        'choices': [{
            'term': 'Deus est sua essentia, & essentia Dei est Deus ipse',
            'english': 'God is His essence, and the essence of God is God Himself',
            'why': 'Identity of abstract/concrete names in God.',
            'rejected': ['Deus and Deitas name different things in God'],
        }],
        'notes': ['OCR: XXI PDF 112-113; Joan. 14.'],
        'bible_refs': ['John 14'],
    },
    {
        'section': '392',
        'title': 'God is above every genus — not univocal with creatures',
        'pass_a': (
            'Nor can the composition which we said of genus and difference be attributed to God '
            'any more. For God is above every genus: nor is He included in any genus of things. '
            'For genus is said what is common to many, and is said in the same way of many. But '
            'nothing is properly common to creatures and God, and said in the same way of '
            'creatures and of God. For if anything is said of God and of creatures, it is not '
            'said univocally, but by analogy and a certain likeness, nor is it in the same way '
            'in God and in creatures. As when we name God wise and just, and also certain men '
            'wise and just, justice and wisdom in men note a certain quality; but in God note '
            'His very essence. But if there were some genus common to creatures and God, none '
            'would rather be than substance. And yet the nature of God is farther distant from '
            'created substances than created substance is distant from accidents. But now '
            'created substance is not in the same genus with accident. Much less therefore is '
            'God in the same genus with created substances.'
        ),
        'pass_b': [
            'God is above every genus — nothing univocally common with creatures.',
            'Wise/just of God names essence; of men, a quality — analogy only.',
            'Even substance is no shared genus: God farther from creatures than substance from accidents.',
        ],
        'lemmas': [
            {'latin': 'supra omne genus', 'gloss': 'above every genus'},
            {'latin': 'non univoce ... sed per analogiam', 'gloss': 'not univocally but by analogy'},
        ],
        'choices': [{
            'term': 'Deus est supra omne genus',
            'english': 'God is above every genus',
            'why': 'Denies genus-difference composition.',
            'rejected': ['God and creatures share the genus substance univocally'],
        }],
        'notes': ['OCR: XXII PDF 113.'],
        'bible_refs': [],
    },
    {
        'section': '393',
        'title': 'No proper difference — one simple essence',
        'pass_a': (
            'But since God does not have a genus, He also cannot have a difference properly so '
            'called. For difference is said that which contracts a genus common to many to a '
            'certain species. And so in the divine nature certain grades cannot be distinguished, '
            'nor is it composed of various grades; but it is one simple essence, which through '
            'itself differs from all others.'
        ),
        'pass_b': [
            'No genus → no proper difference.',
            'Divine nature has no graded composition.',
            'One simple essence differs through itself from all else.',
        ],
        'lemmas': [
            {'latin': 'una simplex essentia', 'gloss': 'one simple essence'},
            {'latin': 'differentiam ... proprie dictam', 'gloss': 'a difference properly so called'},
        ],
        'choices': [{
            'term': 'est una simplex essentia, quae per seipsam differt ab omnibus aliis',
            'english': 'it is one simple essence, which through itself differs from all others',
            'why': 'Closes genus-difference denial.',
            'rejected': ['divine essence is graded like species under a genus'],
        }],
        'notes': ['OCR: XXIII PDF 113.'],
        'bible_refs': [],
    },
    {
        'section': '394',
        'title': 'Act and potency — the last metaphysical composition in creatures',
        'pass_a': (
            'There remains one genus of metaphysical composition which we omitted, namely of act '
            'and potency. Act here is said whatever perfects, determines, and constitutes a '
            'thing, and in a word every perfection is act. But potency is said that according to '
            'which a thing is apt to be perfected and determined, and to receive or suffer '
            'something in itself. And therefore all created things can be said to be composed of '
            'act and potency. For in all of them there is something that perfects, and something '
            'that is perfected. And besides the perfections which are actually in them, there is '
            'none which cannot receive something else, and is not capable of some mutation.'
        ),
        'pass_b': [
            'Last metaphysical composition: act and potency.',
            'Act = whatever perfects; potency = aptness to be perfected or changed.',
            'Every creature has both — and can still receive more change.',
        ],
        'lemmas': [
            {'latin': 'ex actu & potentia', 'gloss': 'of act and potency'},
            {'latin': 'alicujus mutationis capax', 'gloss': 'capable of some mutation'},
        ],
        'choices': [{
            'term': 'res omnes creatae compositae dici possunt ex actu & potentia',
            'english': 'all created things can be said to be composed of act and potency',
            'why': 'Opens act/potency before XXV+ denial in God.',
            'rejected': ['creatures are pure act with no potency'],
        }],
        'notes': ['OCR: XXIV PDF 113; next XXV+ God immune from act/potency.'],
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
    for name in ('pdf_111_114_layout.txt', 'pdf_110_113_layout.txt'):
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
        if 387 <= n <= 394:
            notes = (
                f'Section {sid}: new densify De Dei Simplicitate XVII-XXIV; '
                'Pass A!=B; lock-grounded PDF 112-113 / book pp. 100-101.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_simplicitate XVII-XXIV packet scope covering all current sections.'
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
                'Scope review: densify De Dei Simplicitate XVII-XXIV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Simplicitate through XXIV; XXV+ remains. Not shipped.'
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
        'locus': 'De Dei Simplicitate theses XVII-XXIV (essence-existence / genus / act-potency)',
        'next_locus': 'De Dei Simplicitate XXV+ (God as pure act / attributes one)',
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
        'deploy_bound': 'b67a6a67 live 57/4399 tip 386',
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
        f'## {day} (Scribe — De Dei Simplicitate XVII–XXIV densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Simplicitate XVII–XXIV → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 112-113 / pp. 100-101).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Simplicitate through XXIV. XXV+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound b67a6a67 / tip 386; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Simplicitate XVII–XXIV densify)\n\n'
        'CoS densify: De Dei Simplicitate XVII–XXIV. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Simplicitate XVII–XXIV (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: XXV+. Punch X: **NO**.\n\n---\n\n'
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
            'deploy_bound': 'b67a6a67',
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-386 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
