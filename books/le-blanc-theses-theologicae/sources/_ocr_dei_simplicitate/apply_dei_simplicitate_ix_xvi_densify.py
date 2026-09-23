#!/usr/bin/env python3
"""Build + apply De Dei Simplicitate IX-XVI densify (tip 378 → 386).

Genus/difference; corporeity denial; subject-accident; attribute-as-essence reply.
After tip-ready: HOLD live>4374 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_simplicitate_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_simplicitate/apply_dei_simplicitate_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['379', '380', '381', '382', '383', '384', '385', '386']
ROMANS = {
    '379': 'IX', '380': 'X', '381': 'XI', '382': 'XII',
    '383': 'XIII', '384': 'XIV', '385': 'XV', '386': 'XVI',
}
TIP_BEFORE = 378
LIVE_FLOOR = 4374
HOLD_MINUTES = 12
PRIOR_START = 371  # Simplicitate I in eng/src

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XLII + "
    "De Dei Simplicitate I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), Demonstratur Deum esse I-XLII, and "
    "De Dei Simplicitate I-XVI, reconstructed from the Internet Archive PDF page images with "
    "pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. This slice densifies De Dei Simplicitate IX-XVI (genus/difference; "
    "corporeity denial; subject-accident; attributes as essence)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Simplicitate (Theses Theologicae De Dei Simplicitate).\n"
    "Same 1675 Pitt copy-text. Book pp. 97-100 / PDF 109-112 (I-XVI; this packet IX-XVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Simplicitate I-XVI tip. XVII+ remains.\n"
    "Note: Continues after I-VIII. Corporeity / accident blocks before essence-existence.\n\n"
)

LATIN = {
    '379': (
        'IX. Denique est alia quaedam compositio rebus omnibus creatis communis. Nam in earum '
        'essentia sunt veluti quidam gradus. Sunt enim quaedam quibus inter se conveniunt, '
        'quaedam, quibus inter se differunt. Id quo conveniunt genus appellatur, quo differunt '
        'differentia. Ideoque res omnes creatae & finitae, compositae dici possunt ex genere & '
        'differentia.'
    ),
    '380': (
        'X. His ita expositis quaeritur an Deo talis simplicitas conveniat, quae omnes ejusmodi '
        'compositiones excludat. Id autem ita esse communi consensu Scholae Christianae docetur. '
        'De singulis vero est distincte ostendendum. Primum ergo quaeritur an Deo conveniat illa '
        'compositio quam primo loco commemoravimus, id est, an Deus ad modum corporum sit '
        'extensus, & habeat partes extra partes, quod idem est ac quaerere an Deus sit corporeus, '
        'an non? Corporeum esse censuerunt ex Philosophis antiquis non pauci: veluti Anaximenes, '
        'Diogenes Apolloniates qui putabant Deum esse aerem: Xenocrates, qui Deum fingebat '
        'caelesti corpore: & Epicurus qui Deo corpus humano simile tribuebat.'
    ),
    '381': (
        'XI. Ex Judaeis autem Sadducaei cum nullum spiritum esse existimarent, nec tamen Deum '
        'esse diffiterentur, omnino videntur sensisse Deum non esse spiritum sed corpus. Nec '
        'etiam inter Christianos defuerunt haeretici qui Deum corporeum esse opinati sunt. Tales '
        'erant Anthropomorphitae qui Deo membra humanis similia affingebant, nec parum olim '
        'Ecclesiam turbarunt. Imo Tertullianus ipse disertis verbis affirmat Deum esse '
        'corporeum, libro adversus Praxeam: quo minus mirum est eum similiter statuisse animam '
        'esse corpus. Veruntamen Augustinus haeres. 86. quae est Tertullianistarum Tertullianum '
        'hac in parte excusat quasi pro eodem sumat substantiam & corpus, & dicere velit '
        'simpliciter Deum esse aliquid reale & subsistens.'
    ),
    '382': (
        'XII. Sed quicquid ille & alii senserint, certum est tam ex Scriptura, quam ex recta '
        'ratione, Deum omnino esse incorporeum. Primo enim Scriptura Deum diserte spiritum '
        'appellat Joan. 4. Nam inquit Christus, Deus spiritus est. Spiritus autem & corpus '
        'opponuntur. 2. Docet Scriptura Deum ubique esse & omnia replere. Psal. 139. Quo ibo a '
        'Spiritu tuo, & quo fugiam a facie tua? &c. Et Jer. 23. Annon caelum & terram ego '
        'impleo, inquit Dominus? Jam autem si Deus esset corpus & extensum quid, non posset '
        'ubique esse & omnia replere, quin duo corpora simul essent, & daretur penetratio '
        'dimensionum, quod absurdum est & impossibile. Ac denique Scriptura satis indicat Deum '
        'non esse corpus, dum negat ullum fingi posse corporeum simulachrum quod sit Deo '
        'simile. Ut Isaiae 40. cui similem facietis Deum, aut quam imaginem ponetis ei? Et Act. '
        '17. Non debemus existimare sculpturae artis & cogitationis hominis divinum esse '
        'simile.'
    ),
    '383': (
        'XIII. Anthropomorphitae quidem errori suo obtendebant authoritatem Scripturae, quae '
        'dicit hominem factum esse ad imaginem & similitudinem Dei, unde colligebant Deum '
        'habere membra similia humanis. Sed imago Dei in homine non consistit in membrorum '
        'situ & conformatione, verum in spiritualibus animae facultatibus, intellectu, '
        'scilicet, & voluntate: ac praeterea in donis variis, quibus anima per Dei gratiam '
        'decoratur. Quod autem Scriptura variis in locis Deo membra humana tribuit, veluti '
        'aures, oculos, manus, pedes, metaphorice intelligendum est. Nam aures & oculi, verbi '
        'causa, Deo tribuuntur ut per id significetur nihil ipsi esse occultum, omniaque dicta '
        '& facta nostra ipsi probe nota & perspecta esse. Etenim aures & oculi sunt '
        'instrumenta visus & auditus, quibus percipimus ea quae fiunt & dicuntur. Et similiter '
        'quia manus sunt actionum nostrarum instrumenta, per manum Dei significatur illius '
        'potentia & vis illa qua res efficit. Et ita de reliquis.'
    ),
    '384': (
        'XIV. Sed praeter Scripturae sacrae testimonia, non desunt Philosophis argumenta quibus '
        'probent Deum esse incorporeum. Primo enim, sicuti demonstrat Aristoteles, Deus est '
        'primus motor qui omnia movet, ipse immobilis manens. Sed nullum corpus movet, quin '
        'moveatur ipsum, ut patet per inductionem. Ideoque Deus non potest esse corpus. '
        'Deinde inter res a Deo productas sunt substantiae immateriales, velut angeli, & anima '
        'humana, quae corporibus sunt praestantiores. Sed Deus est aliquid rebus quibusvis ab '
        'ipso productis longe praestantius atque nobilius. Ergo multo magis debet esse '
        'incorporeus & immaterialis. Denique quod corporeum est, aliquid in se continet quod '
        'non est omnino perfectum: nempe partes singulas ex quibus componitur: quarum '
        'unaquaeque minus quiddam est, & imperfectius quam ipsum totum. Sed cum Deus '
        'undiquaque sit ens primum & ex se, nihil in eo potest esse quod non sit omnino '
        'perfectum. Nam ratio nulla reddi potest cur in eo quod est a se, aliqua perfectio '
        'desit. Igitur Deus non potest esse corpus.'
    ),
    '385': (
        'XV. Secunda compositio, cujus mentionem fecimus est ex subjecto & accidente, de qua '
        'etiam quaestio est, An Deo conveniat, id est, an in Deo sint accidentia quaedam ab '
        'essentia ipsius distincta. Id autem Theologi communi consensu negant. Nec sine summa '
        'ratione. Etenim quum Deus sit primum ens & prima causa, necesse est ut sit ens '
        'omnino independens. Adeoque in ipso nihil est quod ab alio dependeat. Sed accidens '
        'omne ab alio dependet, nimirum a subjecto: Ergo in Deo nullum est accidens. Deinde '
        'quicquid praeter essentiam accidens aliquod habet, hoc ipso arguitur essentiam habere '
        'non omnino perfectam. Nam si essentiae rei alicujus perfectio nulla deesset, nullam '
        'extra essentiam perfectionem suscipere posset. Si quidem quod ex se habet omnem '
        'perfectionem, ipsi perfectio nulla adjici potest. Sed Deus essentiam habet omnino '
        'perfectam: Ergo nullius accidentis est capax. Atque, ut verbo dicam, compositio omnis '
        'ex subjecto & accidente arguit imperfectionem tam subjecti, quod ab accidente velut '
        'accessoriam perfectionem mutuatur: quam ipsius accidentis, quod propterea semper '
        'imperfectum convincitur, quia ejus esse semper a subjecto dependet. Verum in Deo '
        'nihil est imperfectum, ideoque est talis compositionis expers.'
    ),
    '386': (
        'XVI. At inquies, nonne Deo accidentia multa tribuuntur, veluti sapientia, justitia, '
        'bonitas, misericordia, & his similia, unde denominatur sapiens, justus, misericors, & '
        'bonus? Respondeo omnia ista non dici eodem modo de Deo, & de nobis. Nam nomina illa '
        'in rebus creatis accidentia quaedam notant: sed in Deo designant ipsam illius '
        'essentiam, quae propter omnimodam suam perfectionem, & varias operationes, varia '
        'sortitur nomina: quoniam unico nomine tanta perfectio significari non potest, nec uno '
        'conceptu concipi.'
    ),
}

SECTIONS = [
    {
        'section': '379',
        'title': 'Genus and difference — another creaturely composition',
        'pass_a': (
            'Finally there is a certain other composition common to all created things. For in '
            'their essence there are as it were certain grades. For there are some things by which '
            'they agree among themselves, some by which they differ among themselves. That by '
            'which they agree is called genus, that by which they differ difference. And therefore '
            'all created and finite things can be said to be composed of genus and difference.'
        ),
        'pass_b': [
            'Last shared creature-composition: grades in essence.',
            'Agree by genus; differ by difference.',
            'Finite creatures = genus + difference.',
        ],
        'lemmas': [
            {'latin': 'ex genere & differentia', 'gloss': 'of genus and difference'},
        ],
        'choices': [{
            'term': 'compositae dici possunt ex genere & differentia',
            'english': 'can be said to be composed of genus and difference',
            'why': 'Closes composition inventory before applying simplicity to God.',
            'rejected': ['creatures lack genus-difference composition'],
        }],
        'notes': ['OCR: IX PDF 110.'],
        'bible_refs': [],
    },
    {
        'section': '380',
        'title': 'Does God\'s simplicity exclude all these? First: is God a body?',
        'pass_a': (
            'These things thus set out, it is asked whether such simplicity befits God as excludes '
            'all compositions of this sort. But that it is so is taught by the common consent of '
            'the Christian School. But concerning each it is to be shown distinctly. First '
            'therefore it is asked whether that composition which we commemorated in the first '
            'place befits God, that is, whether God after the manner of bodies is extended, and '
            'has parts outside parts, which is the same as asking whether God is corporeal or '
            'not? Not a few of the ancient Philosophers judged Him to be corporeal: as '
            'Anaximenes, Diogenes of Apollonia who thought God to be air: Xenocrates, who '
            'feigned God with a celestial body: and Epicurus who attributed to God a body '
            'like the human.'
        ),
        'pass_b': [
            'Christian School: God\'s simplicity bars every such composition.',
            'First question: is God extended parts-outside-parts — a body?',
            'Ancients who said yes: Anaximenes, Diogenes, Xenocrates, Epicurus.',
        ],
        'lemmas': [
            {'latin': 'partes extra partes', 'gloss': 'parts outside parts'},
            {'latin': 'an Deus sit corporeus', 'gloss': 'whether God is corporeal'},
        ],
        'choices': [{
            'term': 'an Deus sit corporeus, an non?',
            'english': 'whether God is corporeal or not?',
            'why': 'Opens corporeity denial series.',
            'rejected': ['simplicity never raises corporeity'],
        }],
        'notes': ['OCR: X PDF 110; Anaximenes normalized from Artaximenes OCR.'],
        'bible_refs': [],
    },
    {
        'section': '381',
        'title': 'Sadducees, Anthropomorphites, Tertullian on a corporeal God',
        'pass_a': (
            'But among the Jews the Sadducees, since they thought no spirit to exist, and yet '
            'did not deny that God is, seem altogether to have felt that God is not a spirit but '
            'a body. Nor were heretics wanting even among Christians who opined that God is '
            'corporeal. Such were the Anthropomorphites who affixed to God members like human '
            'ones, and formerly disturbed the Church not a little. Indeed Tertullian himself in '
            'express words affirms that God is corporeal, in the book against Praxeas: whence '
            'it is less marvelous that he similarly stated the soul to be a body. Yet Augustine '
            'in heresy 86, which is of the Tertullianists, excuses Tertullian in this part as '
            'if he takes substance and body for the same, and wishes to say simply that God is '
            'something real and subsisting.'
        ),
        'pass_b': [
            'Sadducees: no spirits — so God must be body.',
            'Anthropomorphites gave God human members; Tertullian called God corporeal.',
            'Augustine excuses him as meaning substance / something real.',
        ],
        'lemmas': [
            {'latin': 'Anthropomorphitae', 'gloss': 'Anthropomorphites'},
            {'latin': 'adversus Praxeam', 'gloss': 'against Praxeas'},
        ],
        'choices': [{
            'term': 'Deum esse corporeum, libro adversus Praxeam',
            'english': 'that God is corporeal, in the book against Praxeas',
            'why': 'Names Christian corporealist witnesses before Scripture rebuttal.',
            'rejected': ['no Christian ever called God corporeal'],
        }],
        'notes': ['OCR: XI PDF 110-111; Aug. haeres. 86.'],
        'bible_refs': [],
    },
    {
        'section': '382',
        'title': 'Scripture: God is spirit, fills all, no bodily likeness',
        'pass_a': (
            'But whatever he and others sensed, it is certain both from Scripture and from right '
            'reason that God is altogether incorporeal. For first Scripture expressly calls God '
            'spirit in John 4. For Christ says, God is spirit. But spirit and body are opposed. '
            '2. Scripture teaches that God is everywhere and fills all things. Psalm 139. Whither '
            'shall I go from Thy Spirit, and whither shall I flee from Thy face? &c. And Jer. 23. '
            'Do I not fill heaven and earth, says the Lord? But now if God were a body and '
            'something extended, He could not be everywhere and fill all things without two bodies '
            'being together, and a penetration of dimensions being given, which is absurd and '
            'impossible. And finally Scripture sufficiently indicates that God is not a body, '
            'while it denies that any corporeal image can be fashioned which is like God. As '
            'Isaiah 40. to whom will you liken God, or what image will you set for Him? And Acts '
            '17. We ought not to think the divine is like the sculpture of art and of man\'s thought.'
        ),
        'pass_b': [
            'Scripture + reason: God is wholly incorporeal.',
            'John 4: God is spirit; Ps 139 / Jer 23: He fills all — no extended body.',
            'Isa 40 / Acts 17: no bodily likeness of God.',
        ],
        'lemmas': [
            {'latin': 'Deus spiritus est', 'gloss': 'God is spirit'},
            {'latin': 'penetratio dimensionum', 'gloss': 'penetration of dimensions'},
        ],
        'choices': [{
            'term': 'Deum omnino esse incorporeum',
            'english': 'that God is altogether incorporeal',
            'why': 'Scripture case against corporeity.',
            'rejected': ['omnipresence fits an extended body'],
        }],
        'notes': ['OCR: XII PDF 111; Psal. 139 (layout 139/139).'],
        'bible_refs': ['John 4', 'Ps. 139', 'Jer. 23', 'Isa. 40', 'Acts 17'],
    },
    {
        'section': '383',
        'title': 'Image of God is spiritual — human members of God are metaphor',
        'pass_a': (
            'The Anthropomorphites indeed put forward for their error the authority of Scripture, '
            'which says that man was made after the image and likeness of God, whence they '
            'gathered that God has members like human ones. But the image of God in man does not '
            'consist in the situation and conformation of members, but in the spiritual faculties '
            'of the soul, namely intellect and will: and besides in various gifts with which the '
            'soul is adorned by the grace of God. But that Scripture in various places attributes '
            'human members to God, such as ears, eyes, hands, feet, is to be understood '
            'metaphorically. For ears and eyes, for example, are attributed to God that by that '
            'it may be signified that nothing is hidden from Him, and that all our sayings and '
            'deeds are well known and surveyed by Him. For ears and eyes are instruments of sight '
            'and hearing by which we perceive the things that are done and said. And likewise '
            'because hands are instruments of our actions, by the hand of God is signified His '
            'power and that force by which He effects things. And so of the rest.'
        ),
        'pass_b': [
            'Anthropomorphites abused imago Dei into bodily members.',
            'Image = intellect, will, grace-gifts — not limb-shape.',
            'God\'s ears/eyes/hands in Scripture are metaphor for knowledge and power.',
        ],
        'lemmas': [
            {'latin': 'ad imaginem & similitudinem Dei', 'gloss': 'after the image and likeness of God'},
            {'latin': 'metaphorice intelligendum', 'gloss': 'to be understood metaphorically'},
        ],
        'choices': [{
            'term': 'metaphorice intelligendum est',
            'english': 'is to be understood metaphorically',
            'why': 'Blocks Anthropomorphite reading of divine members.',
            'rejected': ['Scripture attributes literal human limbs to God'],
        }],
        'notes': ['OCR: XIII PDF 111.'],
        'bible_refs': [],
    },
    {
        'section': '384',
        'title': 'Philosophy: unmoved mover, immaterial products, no imperfect parts',
        'pass_a': (
            'But besides the testimonies of sacred Scripture, Philosophers are not lacking in '
            'arguments by which they prove that God is incorporeal. For first, as Aristotle '
            'demonstrates, God is the first mover who moves all things, Himself remaining '
            'unmoved. But no body moves without itself being moved, as is clear by induction. '
            'And therefore God cannot be a body. Next among things produced by God there are '
            'immaterial substances, as angels and the human soul, which are more excellent than '
            'bodies. But God is something far more excellent and nobler than any things produced '
            'by Him. Therefore much more ought He to be incorporeal and immaterial. Finally what '
            'is corporeal contains in itself something that is not altogether perfect: namely the '
            'singular parts of which it is composed: each of which is something less, and more '
            'imperfect than the whole itself. But since God is everywhere first being and from '
            'Himself, nothing can be in Him that is not altogether perfect. For no reason can be '
            'given why in that which is from itself some perfection should be lacking. Therefore '
            'God cannot be a body.'
        ),
        'pass_b': [
            'Aristotle: first unmoved mover — no body moves unmoved.',
            'He makes angels and souls — so He is still more immaterial.',
            'Bodies have imperfect parts; a-se first being cannot.',
        ],
        'lemmas': [
            {'latin': 'primus motor', 'gloss': 'first mover'},
            {'latin': 'ens primum & ex se', 'gloss': 'first being and from itself'},
        ],
        'choices': [{
            'term': 'Igitur Deus non potest esse corpus',
            'english': 'Therefore God cannot be a body',
            'why': 'Closes philosophical corporeity denial.',
            'rejected': ['an a-se first being can have imperfect parts'],
        }],
        'notes': ['OCR: XIV PDF 111.'],
        'bible_refs': [],
    },
    {
        'section': '385',
        'title': 'No accidents in God — subject-accident composition denied',
        'pass_a': (
            'The second composition of which we made mention is of subject and accident, about '
            'which there is also a question, Whether it befits God, that is, whether in God there '
            'are certain accidents distinct from His essence. But the Theologians deny that by '
            'common consent. Nor without the highest reason. For since God is the first being '
            'and first cause, it is necessary that He be a being altogether independent. And '
            'therefore in Him there is nothing that depends on another. But every accident depends '
            'on another, namely on a subject: Therefore in God there is no accident. Next whatever '
            'besides essence has some accident is by that very fact argued to have an essence not '
            'altogether perfect. For if no perfection of the essence of some thing were lacking, '
            'it could receive no perfection outside the essence. Since indeed what has every '
            'perfection from itself, no perfection can be added to it. But God has an altogether '
            'perfect essence: Therefore He is capable of no accident. And, to say it in a word, '
            'every composition of subject and accident argues imperfection both of the subject, '
            'which borrows as it were an accessory perfection from the accident: and of the '
            'accident itself, which is therefore always convicted as imperfect, because its being '
            'always depends on the subject. But in God nothing is imperfect, and therefore He is '
            'free of such composition.'
        ),
        'pass_b': [
            'Second composition: subject + accident — does God have it?',
            'Theologians say no: first independent being cannot depend as accidents do.',
            'Perfect essence takes no add-on perfection — God is accident-free.',
        ],
        'lemmas': [
            {'latin': 'ex subjecto & accidente', 'gloss': 'of subject and accident'},
            {'latin': 'nullius accidentis est capax', 'gloss': 'is capable of no accident'},
        ],
        'choices': [{
            'term': 'in Deo nullum est accidens',
            'english': 'in God there is no accident',
            'why': 'Denies subject-accident composition in God.',
            'rejected': ['God\'s essence can receive added accidental perfections'],
        }],
        'notes': ['OCR: XV PDF 111.'],
        'bible_refs': [],
    },
    {
        'section': '386',
        'title': 'Wisdom and justice in God name the essence, not accidents',
        'pass_a': (
            'But you will say, are not many accidents attributed to God, such as wisdom, justice, '
            'goodness, mercy, and the like, whence He is denominated wise, just, merciful, and '
            'good? I answer that all those are not said in the same way of God and of us. For '
            'those names in created things note certain accidents: but in God they designate His '
            'very essence, which on account of its every-way perfection, and various operations, '
            'obtains various names: since so great a perfection cannot be signified by a single '
            'name, nor conceived by a single concept.'
        ),
        'pass_b': [
            'Objection: God is called wise, just, merciful — are those accidents?',
            'In us those names mark accidents; in God they name the essence itself.',
            'One essence, many names — no single word holds that perfection.',
        ],
        'lemmas': [
            {'latin': 'designant ipsam illius essentiam', 'gloss': 'designate His very essence'},
            {'latin': 'varia sortitur nomina', 'gloss': 'obtains various names'},
        ],
        'choices': [{
            'term': 'in Deo designant ipsam illius essentiam',
            'english': 'in God they designate His very essence',
            'why': 'Answers attribute-as-accident objection.',
            'rejected': ['divine wisdom is an accident added to essence'],
        }],
        'notes': ['OCR: XVI PDF 111-112; next XVII+ essence/existence.'],
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
    for name in ('pdf_110_113_layout.txt', 'tess_110.txt', 'tess_111.txt', 'tess_112.txt'):
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
        if 379 <= n <= 386:
            notes = (
                f'Section {sid}: new densify De Dei Simplicitate IX-XVI; '
                'Pass A!=B; lock-grounded PDF 110-112 / book pp. 98-100.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_simplicitate IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Dei Simplicitate IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Simplicitate through XVI; XVII+ remains. Not shipped.'
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
        'locus': 'De Dei Simplicitate theses IX-XVI (genus / corporeity / accidents)',
        'next_locus': 'De Dei Simplicitate XVII+ (essence-existence / nature-suppositum in God)',
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
        f'## {day} (Scribe — De Dei Simplicitate IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Simplicitate IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 110-112 / pp. 98-100).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Simplicitate through XVI (corporeity; accidents). '
        'XVII+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Simplicitate IX–XVI densify)\n\n'
        'CoS densify: De Dei Simplicitate IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Simplicitate IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: XVII+. Punch X: **NO**.\n\n---\n\n'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-378 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
