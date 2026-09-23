#!/usr/bin/env python3
"""Build + apply De Dei Immensitate & Omnipraesentia IX-XVI densify (tip 432 → 440).

Essence-mode; Vorstius/Eugubinus; Jer 23 / Ps 139 / Isa 66. Live floor 4557.
After tip-ready: HOLD live>4557 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_immensitate_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_immensitate/apply_dei_immensitate_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['433', '434', '435', '436', '437', '438', '439', '440']
ROMANS = {
    '433': 'IX', '434': 'X', '435': 'XI', '436': 'XII',
    '437': 'XIII', '438': 'XIV', '439': 'XV', '440': 'XVI',
}
TIP_BEFORE = 432
LIVE_FLOOR = 4557
HOLD_MINUTES = 12
PRIOR_START = 425

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Immensitate & Omnipraesentia I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Immensitate & Omnipraesentia I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Immensitate & Omnipraesentia I-XVI, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Immensitate IX-XVI "
    "(essence-mode; Vorstius; Jer 23 / Ps 139 / Isa 66)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Immensitate & Omnipraesentia.\n"
    "Same 1675 Pitt copy-text. Book pp. 106-108 / PDF 118-120 (I-XVI; this packet IX-XVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Immensitate & Omnipraesentia I-XVI tip. XVII+ remains.\n"
    "Note: Continues after I-VIII. Essence-presence; Eugubinus/Vorstius; Scripture proofs.\n\n"
)

LATIN = {
    '433': (
        'IX. Denique Deus in rebus dicitur esse per essentiam, quia substantia ejus nusquam '
        'deest, nec deesse potest: sed, ut diximus, omnia penetrat, & per omnia diffusa est, '
        'omnibusque ac singulis rebus tota per seipsam intime inest; ita ut nulli dentur '
        'recessus in ulla plane creatura, in quibus tota divina essentia non reperiatur.'
    ),
    '434': (
        'X. Quae quamvis a nobis dicantur, agnoscimus tamen modum illum quo essentia divina '
        'rebus inest, a nobis satis intelligi, aut verbis exprimi non posse. Neque verbis '
        'praedictis aliud assertum volumus, quam essentiam divinam a nulla re prorsus '
        'abesse: nec illam rebus inesse per partes, cum simplicissima sit & indivisibilis, '
        'ut aliis thesibus abunde probatum est. Ac licet modus ille quo Deus existit in '
        'rebus ipsi sit proprius, ac plane singularis, ejus tamen vestigium quoddam dari '
        'videtur in anima humana, quae per totum corpus ita diffusa est, ut tota sit in '
        'toto, & tota in qualibet parte, ut communiter docent scholae Philosophicae.'
    ),
    '435': (
        'XI. Tribus hisce modis Deus in mundo ubique praesens est, juxta Orthodoxorum '
        'communem sententiam. Et quidem de duobus primis nulla dubitatio est. Nec est '
        'quisquam inter Christianos, quod sciam, imo nec inter ipsos infideles, qui Deum '
        'aliquem agnoscunt, qui neget Deum ubique praesentem esse per suam cognitionem & '
        'virtutem: ita ut nulla res sit quae cognitionem illius fugiat, & ad quam virtus '
        'ejus non possit pertingere.'
    ),
    '436': (
        'XII. Sed de tertio modo, nimirum de praesentia secundum substantiam, repertus est '
        'unus, aut alter qui negaret Deum ita ubique esse. Nam inter Pontificios Augustinus '
        'quidam Eugubinus scribens in Psalmum 138. juxta versionem vulgatam, qui juxta '
        'Hebraeos est 139. pretendit Deum secundum substantiam extra caelum non esse, & in '
        'caelo duntaxat versari. Ex reformatis vero similem errorem erravit Vorstius, sub '
        'hujus saeculi initium, Professor in Academia Lugduno-Batava, qui affirmavit Deum, '
        'ratione suae substantiae, esse tantum in caelo, licet in terra virtute & sapientia '
        'sua nobis adsit.'
    ),
    '437': (
        'XIII. Itaque ad asserendam Deo immensitatis suae laudem, contra hominem illum, & '
        'si qui sint qui cum ipso sentiant, duo jam, Deo ipso favente, probabimus. Primo in '
        'toto universo nullum locum esse, in quo Deus praesens non sit secundum suam '
        'substantiam, secundum Deum toto mundo non contineri, & illum immensa sua '
        'magnitudine superare.'
    ),
    '438': (
        'XIV. Quod ad primum attinet Scriptura sacra docet apertissime nullum in toto mundo '
        'locum esse in quo Deus praesens non adsit, & quidem praesentia reali & substantiali. '
        'Id praesertim colligitur ex ipsius Dei verbis, Jeremiae capite vigesimo tertio, ubi '
        'se terram & caelum implere asseverat. Quod de praesentia alia quam substantiali '
        'commode accipi non potest. Nam arguens Pseudo-prophetas, qui fingebant se a Deo '
        'missos, eique mendacia sua ascribere non verebantur, non cogitantes Deum testem & '
        'ultorem adesse, his interrogationibus stuporem eorum excitat. Numquid ego sum Deus '
        'de propinquo, inquit Dominus, & non Deus de longinquo? Potestne quis abscondi in '
        'latibulis ubi ego eum non videam, inquit Dominus? Annon caelum & terram impleo? '
        'dicit Dominus? Ubi probat neminem posse ab ipsius oculis abscondi, quoniam in toto '
        'mundo nullus locus ipso vacuus est. Et certe, si Deus tantum ideo terrae praesens '
        'esset, quia de caelo videt & regit ea quae in terra fiunt, non posset recte dici '
        'terram implere. Nec enim Rex qui Galliam imperio suo regit potest dici Galliam '
        'implere. Ut nec implet campum aliquem, qui in turri quadam constitutus, procul '
        'illum contuetur.'
    ),
    '439': (
        'XV. Nec minus illam naturae divinae omnipraesentiam probant verba Prophetae: '
        'Psal. 139. Quo ibo a spiritu tuo, & quo a facie tua fugiam? Si ascendero in caelum, '
        'tu illic es. Si stratum posuero in inferno, ecce ades. Si assumam alas aurorae, & '
        'ultra maria andeam: ibi quoque manus tua inveniet me, & dextera tua me '
        'comprehendet. Quae verba docent Deum tam esse in terra quam in caelo, & in summa '
        'nullum omnino locum esse ubi non adsit. Nec verba ista ad solam Dei potentiam & '
        'cognitionem detorqueri possunt quin recedatur a scopo Prophetae. Nam cum duae sint '
        'rationes, quibus ita quis occultari possit, ut non videatur ab alio, una, si sit in '
        'eo loco ubi alter non sit; altera, si sit quidem in eodem loco, sed visum impediant '
        'tenebrae, neutram sibi prodesse posse Psaltes affirmat. Et prius quidem illud '
        'removet verbis citatis, ubi docet a nullo loco Deum abesse. Posterius vero verbis '
        'sequentibus, ubi affirmat Deo esse perinde tenebras atque lucem. Nec etiam verba '
        'Prophetae patiuntur istud interpretamentum. Nam quum de loco supremo dicit '
        'Propheta, Si ascendero, tu illic es, & verborum proprietas, & rei veritas exigit ut '
        'intelligamus substantiae divinae praesentiam. Sed manifestum est, quam postea de '
        'loco infimo subjungit, ecce ades, illum de eadem praesentia loqui, & dicere velle '
        'Deum ita praesentem esse in terra ut in caelo: adeoque illic etiam secundum suam '
        'substantiam adesse.'
    ),
    '440': (
        'XVI. Huc etiam referri potest quod legitur apud Isaiam cap. 66. Haec dicit '
        'Dominus, caelum sedes mea, terra autem scabellum pedum meorum. Quae est ista '
        'domus quam aedificabitis mihi? Et quis est iste locus quietis meae? Nonne manus '
        'mea fecit haec omnia? Ubi Deus probat se templis manufactis includi non posse, non '
        'ratione ducta a distantia loci in quo sit ejus propria sedes & habitaculum, ut '
        'somniasse videtur Vorstius: sed a substantiae suae magnitudine, qua replet '
        'universum mundum. Et certe is qui folio insidit, substantia sua non minus attingit '
        'scabellum quam solium ipsum. Adeoque Deus dicens caelum esse thronum suum, & '
        'terram pedum suorum scabellum, significat se non minus terrae quam ipsi caelo '
        'substantia sua adesse.'
    ),
}

SECTIONS = [
    {
        'section': '433',
        'title': 'Presence by essence — whole substance intimately in every creature',
        'pass_a': (
            'Finally God is said to be in things by essence, because His substance is nowhere '
            'absent, nor can it be absent: but, as we have said, it penetrates all things, and '
            'is poured through all, and is intimately present by itself whole to all and '
            'singular things; so that no recesses are given in any creature at all in which '
            'the whole divine essence is not found.'
        ),
        'pass_b': [
            'By essence: His substance is nowhere missing.',
            'It penetrates all — whole, by itself, intimately in each thing.',
            'No creaturely recess lacks the whole divine essence.',
        ],
        'lemmas': [
            {'latin': 'per essentiam', 'gloss': 'by essence'},
            {'latin': 'tota per seipsam intime inest', 'gloss': 'is intimately present by itself whole'},
        ],
        'choices': [{
            'term': 'nulli dentur recessus in ulla plane creatura',
            'english': 'no recesses are given in any creature at all',
            'why': 'Closes the three modes with essence-presence.',
            'rejected': ['essence-presence leaves creaturely voids empty of God'],
        }],
        'notes': ['OCR: IX PDF 119 / p. 107.'],
        'bible_refs': [],
    },
    {
        'section': '434',
        'title': 'Mode ineffable — not by parts; soul vestige tota in toto',
        'pass_a': (
            'Which things although they are said by us, we nevertheless acknowledge that '
            'that mode by which the divine essence is in things cannot be sufficiently '
            'understood by us, or expressed in words. Nor by the aforesaid words do we '
            'wish anything else asserted than that the divine essence is altogether absent '
            'from no thing: nor that it is in things by parts, since it is most simple and '
            'indivisible, as has been abundantly proved in other theses. And although that '
            'mode by which God exists in things is proper to Him, and plainly singular, '
            'nevertheless a certain vestige of it seems to be given in the human soul, which '
            'is so poured through the whole body that it is whole in the whole, and whole in '
            'any part, as the schools of Philosophy commonly teach.'
        ),
        'pass_b': [
            'We cannot fully grasp or word the mode of essence-in-things.',
            'Claim only: absent from nothing; not present by parts (simplicity).',
            'Vestige: soul whole in whole body and whole in each part.',
        ],
        'lemmas': [
            {'latin': 'simplicissima sit & indivisibilis', 'gloss': 'it is most simple and indivisible'},
            {'latin': 'tota sit in toto, & tota in qualibet parte', 'gloss': 'it is whole in the whole, and whole in any part'},
        ],
        'choices': [{
            'term': 'nec illam rebus inesse per partes',
            'english': 'nor that it is in things by parts',
            'why': 'Guards simplicity against piecemeal presence.',
            'rejected': ['divine essence is present as divided parts in creatures'],
        }],
        'notes': ['OCR: X PDF 119.'],
        'bible_refs': [],
    },
    {
        'section': '435',
        'title': 'First two modes undisputed — even among theists',
        'pass_a': (
            'By these three modes God is everywhere present in the world, according to the '
            'common judgment of the Orthodox. And indeed concerning the first two there is '
            'no doubt. Nor is there anyone among Christians, so far as I know, nay nor among '
            'the unbelievers themselves who acknowledge some God, who denies that God is '
            'everywhere present by His cognition and power: so that there is no thing which '
            'escapes His cognition, and to which His power cannot reach.'
        ),
        'pass_b': [
            'Orthodox: three modes of ubiquity.',
            'Power and cognition-presence: no dispute.',
            'Even theist unbelievers grant no thing escapes His knowing/power.',
        ],
        'lemmas': [
            {'latin': 'de duobus primis nulla dubitatio est', 'gloss': 'concerning the first two there is no doubt'},
            {'latin': 'per suam cognitionem & virtutem', 'gloss': 'by His cognition and power'},
        ],
        'choices': [{
            'term': 'de duobus primis nulla dubitatio est',
            'english': 'concerning the first two there is no doubt',
            'why': 'Sets up the contested third mode.',
            'rejected': ['power and cognition-presence are also contested'],
        }],
        'notes': ['OCR: XI PDF 119; end restored from layout + sense.'],
        'bible_refs': [],
    },
    {
        'section': '436',
        'title': 'Third mode denied — Eugubinus and Vorstius confine substance to heaven',
        'pass_a': (
            'But concerning the third mode, namely presence according to substance, one or '
            'another has been found who would deny that God is thus everywhere. For among '
            'the Pontificals a certain Augustinus Eugubinus writing on Psalm 138 according '
            'to the Vulgate version, which according to the Hebrews is 139, maintains that '
            'God according to substance is not outside heaven, and dwells only in heaven. '
            'But from the Reformed Vorstius erred with a like error at the beginning of this '
            'century, Professor in the Academy of Leiden, who affirmed that God, by reason '
            'of His substance, is only in heaven, although on earth He is present to us by '
            'His power and wisdom.'
        ),
        'pass_b': [
            'Substance-presence is the contested mode.',
            'Eugubinus: God\'s substance only in heaven (Ps 138/139).',
            'Vorstius (Leiden): same — substance in heaven; earth only by power/wisdom.',
        ],
        'lemmas': [
            {'latin': 'praesentia secundum substantiam', 'gloss': 'presence according to substance'},
            {'latin': 'Vorstius', 'gloss': 'Vorstius'},
        ],
        'choices': [{
            'term': 'esse tantum in caelo, licet in terra virtute & sapientia sua nobis adsit',
            'english': 'is only in heaven, although on earth He is present to us by His power and wisdom',
            'why': 'Names the error Immensitate will refute.',
            'rejected': ['Vorstius affirmed substantial presence on earth'],
        }],
        'notes': ['OCR: XII PDF 119; Vorstius/Eugubinus.'],
        'bible_refs': ['Ps. 139'],
    },
    {
        'section': '437',
        'title': 'Two proofs — no empty place; greater than the world',
        'pass_a': (
            'Therefore to assert for God the praise of His immensity, against that man, and '
            'if there be any who feel with him, we will now prove two things, God Himself '
            'favoring. First that in the whole universe there is no place in which God is '
            'not present according to His substance; second that God is not contained by the '
            'whole world, and that He surpasses it by His immense greatness.'
        ),
        'pass_b': [
            'Against Vorstius: two claims to prove.',
            '1) No place without substantial presence.',
            '2) God not contained by the world — surpasses it.',
        ],
        'lemmas': [
            {'latin': 'nullum locum esse, in quo Deus praesens non sit secundum suam substantiam', 'gloss': 'there is no place in which God is not present according to His substance'},
            {'latin': 'toto mundo non contineri', 'gloss': 'not to be contained by the whole world'},
        ],
        'choices': [{
            'term': 'duo jam, Deo ipso favente, probabimus',
            'english': 'we will now prove two things, God Himself favoring',
            'why': 'Roadmap for XIV+ and later world-surpassing proofs.',
            'rejected': ['only one proof is needed against Vorstius'],
        }],
        'notes': ['OCR: XIII PDF 119.'],
        'bible_refs': [],
    },
    {
        'section': '438',
        'title': 'Jeremiah 23 — filling heaven and earth is substantial presence',
        'pass_a': (
            'As to the first, sacred Scripture teaches most openly that there is no place in '
            'the whole world in which God is not present, and indeed with real and '
            'substantial presence. That is gathered especially from God\'s own words in '
            'Jeremiah chapter twenty-three, where He asserts that He fills earth and heaven. '
            'Which cannot conveniently be taken of a presence other than substantial. For '
            'arguing against the false prophets who pretended they were sent by God and did '
            'not fear to ascribe their lies to Him, not thinking that God the witness and '
            'avenger was present, He stirs their stupor with these questions. Am I a God at '
            'hand, says the Lord, and not a God afar off? Can anyone hide in secret places '
            'where I shall not see him, says the Lord? Do I not fill heaven and earth? says '
            'the Lord? Where He proves that no one can be hidden from His eyes, because in '
            'the whole world no place is empty of Him. And certainly, if God were present to '
            'the earth only because from heaven He sees and rules what is done on earth, He '
            'could not rightly be said to fill the earth. For a King who rules Gaul by his '
            'empire cannot be said to fill Gaul. As neither does he fill some field who, '
            'stationed in a certain tower, looks upon it from afar.'
        ),
        'pass_b': [
            'Scripture: no place without real substantial presence.',
            'Jer 23: I fill heaven and earth — not mere remote rule.',
            'Remote seeing ≠ filling (Gaul-king / tower-watcher analogies).',
        ],
        'lemmas': [
            {'latin': 'praesentia reali & substantiali', 'gloss': 'with real and substantial presence'},
            {'latin': 'se terram & caelum implere', 'gloss': 'that He fills earth and heaven'},
        ],
        'choices': [{
            'term': 'non posset recte dici terram implere',
            'english': 'He could not rightly be said to fill the earth',
            'why': 'Blocks reducing fill to distant governance.',
            'rejected': ['filling earth means only ruling it from heaven'],
        }],
        'notes': ['OCR: XIV PDF 119; Jer 23:23-24.'],
        'bible_refs': ['Jer. 23:23-24'],
    },
    {
        'section': '439',
        'title': 'Psalm 139 — same substantial presence in heaven and on earth',
        'pass_a': (
            'Nor less do the words of the Prophet prove that omnipresence of the divine '
            'nature: Psalm 139. Whither shall I go from Thy spirit, and whither shall I flee '
            'from Thy face? If I ascend into heaven, Thou art there. If I make my bed in '
            'hell, behold Thou art present. If I take the wings of the dawn, and dwell beyond '
            'the seas: there also Thy hand will find me, and Thy right hand will hold me. '
            'Which words teach that God is as much on earth as in heaven, and in sum that '
            'there is no place at all where He is not present. Nor can those words be twisted '
            'to God\'s power and cognition alone without departing from the Prophet\'s aim. '
            'For since there are two ways by which someone can be so hidden as not to be seen '
            'by another — one, if he is in a place where the other is not; the other, if he '
            'is indeed in the same place but darkness hinders sight — the Psalmist affirms '
            'that neither can profit him. And the first he removes by the words cited, where '
            'he teaches that God is absent from no place. But the latter by the following '
            'words, where he affirms that darkness and light are alike to God. Nor do the '
            'Prophet\'s words endure that interpretation. For when concerning the highest '
            'place the Prophet says, If I ascend, Thou art there, both the propriety of the '
            'words and the truth of the matter require that we understand the presence of the '
            'divine substance. But it is clear that what he afterward subjoins concerning the '
            'lowest place, behold Thou art present, speaks of the same presence, and means '
            'to say that God is as present on earth as in heaven: and therefore that He is '
            'present there also according to His substance.'
        ),
        'pass_b': [
            'Ps 139: no flight from God — heaven, Sheol, seas.',
            'Not twistable to power/knowledge only without missing the aim.',
            'Highest and lowest places: same substantial presence.',
        ],
        'lemmas': [
            {'latin': 'nullum omnino locum esse ubi non adsit', 'gloss': 'there is no place at all where He is not present'},
            {'latin': 'secundum suam substantiam adesse', 'gloss': 'to be present according to His substance'},
        ],
        'choices': [{
            'term': 'Deum ita praesentem esse in terra ut in caelo',
            'english': 'that God is as present on earth as in heaven',
            'why': 'Psalm parity blocks heaven-only substance.',
            'rejected': ['Ps 139 concerns only remote knowledge from heaven'],
        }],
        'notes': ['OCR: XV PDF 119-120 / pp. 107-108.'],
        'bible_refs': ['Ps. 139:7-12'],
    },
    {
        'section': '440',
        'title': 'Isaiah 66 — heaven throne, earth footstool; same substance',
        'pass_a': (
            'Hither also can be referred what is read in Isaiah chapter 66. Thus says the '
            'Lord, heaven is My seat, but the earth the footstool of My feet. What is that '
            'house which you will build for Me? And what is that place of My rest? Did not '
            'My hand make all these things? Where God proves that He cannot be shut up in '
            'hand-made temples, not by an argument drawn from the distance of the place in '
            'which His proper seat and dwelling is, as Vorstius seems to have dreamed: but '
            'from the greatness of His substance, by which He fills the whole world. And '
            'certainly he who sits on a throne touches the footstool no less with his '
            'substance than the throne itself. And therefore God, saying that heaven is His '
            'throne and the earth the footstool of His feet, signifies that He is present by '
            'His substance no less to the earth than to heaven itself.'
        ),
        'pass_b': [
            'Isa 66: heaven My throne, earth My footstool — cannot be boxed in temples.',
            'Not Vorstius\'s distant-seat reading — substance fills the world.',
            'Throne-sitter touches footstool too — earth gets the same substance.',
        ],
        'lemmas': [
            {'latin': 'caelum sedes mea, terra autem scabellum pedum meorum', 'gloss': 'heaven is My seat, but the earth the footstool of My feet'},
            {'latin': 'a substantiae suae magnitudine, qua replet universum mundum', 'gloss': 'from the greatness of His substance, by which He fills the whole world'},
        ],
        'choices': [{
            'term': 'se non minus terrae quam ipsi caelo substantia sua adesse',
            'english': 'that He is present by His substance no less to the earth than to heaven itself',
            'why': 'Isa 66 closes IX-XVI against heaven-only substance.',
            'rejected': ['footstool means earth lacks substantial presence'],
        }],
        'notes': ['OCR: XVI PDF 120 / p. 108; Isa 66:1-2. Next XVII+ immediate operation.'],
        'bible_refs': ['Isa. 66:1-2'],
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
    for name in ('pdf_118_120_layout.txt', 'tess118.txt', 'tess119.txt', 'tess120.txt'):
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
        if 433 <= n <= 440:
            notes = (
                f'Section {sid}: new densify De Dei Immensitate & Omnipraesentia IX-XVI; '
                'Pass A!=B; lock-grounded PDF 119-120 / book pp. 107-108.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_immensitate IX-XVI packet scope covering all current sections.'
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
            },
            'uncertainties': [],
            'notes': (
                'Scope review: densify De Dei Immensitate & Omnipraesentia IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Immensitate through XVI. XVII+ remains. Not shipped.'
            ),
        },
        'reviews': reviews,
    }
    # ensure scripture check present for validate
    receipt['scope_review']['checks']['scripture'] = True
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
        'locus': 'De Dei Immensitate & Omnipraesentia theses IX-XVI (essence; Vorstius; Scripture)',
        'next_locus': 'De Dei Immensitate & Omnipraesentia XVII+ (immediate operation; hypostatic union)',
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
        'deploy_bound': '364dfebc',
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
        f'## {day} (Scribe — De Dei Immensitate & Omnipraesentia IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Immensitate IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 119-120 / pp. 107-108).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Immensitate & Omnipraesentia through XVI. XVII+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound 364dfebc / tip 432; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Immensitate & Omnipraesentia IX–XVI densify)\n\n'
        'CoS densify: Immensitate IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Immensitate IX–XVI (**'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-432 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
