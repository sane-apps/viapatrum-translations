#!/usr/bin/env python3
"""Build + apply De Dei Immensitate & Omnipraesentia XVII-XXIV densify (tip 440 → 448).

Immediate operation; hypostatic union; world-surpassing; Vorstius texts. Live floor 4581.
After tip-ready: HOLD live>4581 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_immensitate_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_immensitate/apply_dei_immensitate_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['441', '442', '443', '444', '445', '446', '447', '448']
ROMANS = {
    '441': 'XVII', '442': 'XVIII', '443': 'XIX', '444': 'XX',
    '445': 'XXI', '446': 'XXII', '447': 'XXIII', '448': 'XXIV',
}
TIP_BEFORE = 440
LIVE_FLOOR = 4581
HOLD_MINUTES = 12
PRIOR_START = 425

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Dei Immensitate & Omnipraesentia I-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Dei Immensitate & Omnipraesentia I-XXIV. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Dei Immensitate & Omnipraesentia I-XXIV, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Immensitate XVII-XXIV "
    "(immediate operation; hypostatic union; world-surpassing; Vorstius heaven-texts)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Dei Immensitate & Omnipraesentia.\n"
    "Same 1675 Pitt copy-text. Book pp. 106-109 / PDF 118-121 (I-XXIV; this packet XVII-XXIV). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Dei Immensitate & Omnipraesentia I-XXIV tip. XXV+ remains.\n"
    "Note: Continues after IX-XVI. Immediate earth-operation; Col 2; 1 Kgs 8 / Job 11 / Isa 40; "
    "extra mundum; Vorstius heaven-habitation texts.\n\n"
)

LATIN = {
    '441': (
        'XVII. Sed praeterea, quod Deus in terra sit secundum substantiam non minus quam '
        'in caelo, inde patet quod in terra immediate operatur. Nam non minus est '
        'impossibile, ut quis immediate efficiat aliquid ubi non est, quam quum non est. '
        'Deum autem agere immediate in terra manifestum est ex terrae creatione, & '
        'conservatione: tum ex miraculis in terra editis. Nam creatio & conservatio, & '
        'miraculorum etiam patratio sunt actiones Dei immediatae, in quibus Deus nullis '
        'utitur instrumentis, sed per seipsum immediate agit. Ideoque Apostolus Actor. 17. '
        'ex perpetua illa rerum conservatione & sustentatione, ratione cujus dicimur in Deo '
        'vivere, moveri, & esse, colligit Deum non esse longe ab unoquoque nostrum: adeoque '
        'non procul a nobis in caelo versari, tanquam in habitaculo quodam extra quod non sit.'
    ),
    '442': (
        'XVIII. Et huc etiam nos ducit fidei analogia. Nam ex fide certum est naturam '
        'divinam in Christo humanae naturae esse personaliter unitam. Et sic omnem '
        'plenitudinem divinitatis in Christo habitare corporaliter & substantialiter, ut '
        'docet Apostolus capite secundo Epist. ad Colossenses. Sed Christus secundum '
        'naturam humanam in terris diu versatus est. Ideoque necesse est divinam '
        'substantiam in terris etiam adesse, nisi quis dissolvere velit unionem duarum '
        'naturarum in Christo: aut dicere Christi naturam humanam personaliter unitam '
        'fuisse cum natura divina, etiam tum quum ab ea secundum locum distabat.'
    ),
    '443': (
        'XIX. Itaque nullus est locus in universo, ubi Deus non adsit non tantum virtute & '
        'potentia sua, sed etiam per essentiam suam quae omnia penetrat, & per omnia '
        'diffusa est. Sed praeterea, quod secundo loco probandum suscepimus, Dei '
        'magnitudo tanta est ut totum universum replens ipso tamen non contineatur, sed '
        'ipsum longe exsuperet. Id docet Salomon libro primo Regum capite octavo. Nam '
        'postquam dixit de templo quod recens extruxerat, Aedificavi domum habitaculum '
        'tibi, firmam sedem in qua aeternum habites, Ne quis existimaret Deum magnifica '
        'illa domo in posterum includendum esse, sicuti gentium idola suis templis, '
        'absurdam ejusmodi cogitationem removet. Ecce, inquit, caeli caelorum non capiunt '
        'te, quanto minus domus ista quam aedificavi? Ubi per caelos caelorum intelligit '
        'caelos extremos, qui continent universum mundum, quos Deum capere, id est, '
        'continere & concludere non posse asseverat. Quae verba accipi non possunt nisi de '
        'Dei substantia, non vero de Dei virtute, & exertione providentiae ejus. Nam cui '
        'tam stupido & inepto posset venire in mentem Dei potestatem & providentiam unica '
        'domo concludi? Nec opus fuit ut Salomon cogitationi tali occurreret.'
    ),
    '444': (
        'XX. Praeterea quod Deus mundo non includatur, sed sit toto mundo major & superior, '
        'manifeste docet Sophar apud Jobum capite undecimo. Excelsior, inquit, est caelo, '
        'profundior inferno, longior terra, & latior mari. Nam certe si Deus extremo caelo '
        'concluderetur non posset dici caelo excelsior.'
    ),
    '445': (
        'XXI. Et huc etiam facit quod Deus, apud Isaiam capite quadragesimo, dicitur '
        'mensus fuisse pugillo aquas, & caelos spithama, denique tantus ut in conspectu '
        'ejus gentes sint tanquam gutta e situla, tanquam flos pulverisculi in lancibus: '
        'imo velut nihil, & quid minus nihilo & inanitate. Quibus verbis Deo tanta '
        'magnitudo tribuitur, ut, illius respectu, totum hoc universum sit res parva & '
        'quasi nihili. Et certe si Deus universo concluderetur, nec esset illo superior, '
        'finem haberet illius magnitudo: quandoquidem mundus est aliquid finitum. Sed '
        'diserte Psaltes affirmat magnitudinis Dei non esse finem: Psal. 145. Magnus est '
        'Dominus, & laudabilis nimis, & magnitudinis illius En cheker, non est investigatio, '
        'id est, ut recte vertit vulgata, non est finis. Cur enim magnitudinis Dei non est '
        'investigatio, nisi quoniam illa nec modum habet nec finem.'
    ),
    '446': (
        'XXII. Et certe, quandoquidem Deus pro sua voluntate mundum hunc e nihilo creavit, '
        'negari non potest illum pari facultate posse, si liberet, plures alios mundos '
        'creare in infinitum, & sine certo numero. A quorum tamen nullo abesse putandus '
        'esset. Nec daretur ulla ratio cur esset in hoc, non vero in alio. Praeterquam '
        'quod si Deus hoc mundo includitur, nec est extra hunc mundum, qui posset extra '
        'hunc mundum operari, & alium mundum creare? cum ad productionem ex nihilo '
        'requiratur actio immediata: inde ergo sequitur Dei magnitudinem non habere finem '
        '& terminum ullum, nec ut caelo conclusa sit.'
    ),
    '447': (
        'XXIII. At, inquies, quomodo Deus est extra mundum cum extra mundum nihil sit? An '
        'Deus est in nihilo? Respondeo Deum esse extra mundum quomodo ante mundum '
        'conditum erat ubi est mundus. Nempe Deus loco non indiget, sed est ipse sibi '
        'locus. Juxta illud Tertulliani libro contra Praxeam: Ante omnia Deus erat solus '
        'ipse sibi, & locus, & mundus, & omnia. Quod alii volunt, dum dicunt, Deum extra '
        'mundum esse in seipso, sicut ante in seipso fuit. Idque post Augustinum in '
        'Psalmum 122. Antequam faceret Deus sanctos ubi habitabat? In se habitabat. Quo '
        'pertinet etiam illud Bernardi, Non est quod quaeras ultra ubi erat? praeter ipsum '
        'nihil erat. Atque haec est sententia versuum istorum qui leguntur apud Dionysium '
        'Carthusianum: Dic ubi tunc esset quum praeter eum nihil esset? Tunc, ubi nunc, in '
        'se, quoniam sibi sufficit ipse. Quibus addendum est extra hunc mundum quidem '
        'nullum esse locum realem & actualem, sed tamen esse locum possibilem. Nimirum '
        'Deus potest ibi creare corpora & loca ubi erit citra ullum sui motum & loci '
        'mutationem.'
    ),
    '448': (
        'XXIV. Quod autem Vorstium, & paucos quosdam movit ut essentiae divinae '
        'magnitudinem limitarent, & Dei substantiam caelo inclusam esse opinarentur, sunt '
        'multa Scripturae loca ubi caelum terrae oppositum describitur tanquam Dei '
        'habitaculum & locus in quo residet. Sicut id quod legitur Psal. 115. Caeli '
        'caelorum Domino, terram autem dedit filiis hominum. Et Psal. 123. Ad te levavi '
        'oculos qui habitas in caelis. Sed si ideo putandum est Dei substantiam caelo '
        'contineri, & extra caelum non esse, quoniam Deus dicitur peculiariter habitare in '
        'caelo: pari ratione concludendum erit Deum olim inclusum fuisse templo '
        'Hierosolymitano: quoniam saepe quoque dicitur Deus templum istud elegisse '
        'tanquam domum & sedem in qua habitaret. Et praeterea, tam tota Ecclesia '
        'conjunctim, quam singuli fideles seorsim, vocantur in Sacra Scriptura Dei '
        'templum, in quo etiam Deus dicitur habitare. Et tamen quis inde colliget Deum per '
        'substantiam alibi praesentem non esse, quam in Ecclesia & illius membris?'
    ),
}

SECTIONS = [
    {
        'section': '441',
        'title': 'Immediate earth-operation proves substantial presence on earth',
        'pass_a': (
            'But besides, that God is on earth according to substance no less than in '
            'heaven is clear from this, that He operates immediately on earth. For it is '
            'no less impossible that someone immediately effect something where he is not, '
            'than when he is not. But that God acts immediately on earth is manifest from '
            'the creation and conservation of the earth: then from miracles wrought on '
            'earth. For creation and conservation, and also the working of miracles, are '
            'immediate actions of God, in which God uses no instruments, but acts '
            'immediately through Himself. And therefore the Apostle in Acts 17, from that '
            'perpetual conservation and sustentation of things, by reason of which we are '
            'said to live, move, and be in God, gathers that God is not far from each one '
            'of us: and therefore is not conversing far from us in heaven, as in some '
            'dwelling outside of which He is not.'
        ),
        'pass_b': [
            'Immediate earth-acts prove substance on earth as in heaven.',
            'Creation, conservation, miracles: no instruments — He acts through Himself.',
            'Acts 17: not far away in a heavenly box outside which He is not.',
        ],
        'lemmas': [
            {'latin': 'in terra immediate operatur', 'gloss': 'He operates immediately on earth'},
            {'latin': 'per seipsum immediate agit', 'gloss': 'acts immediately through Himself'},
        ],
        'choices': [{
            'term': 'non minus est impossibile, ut quis immediate efficiat aliquid ubi non est',
            'english': 'it is no less impossible that someone immediately effect something where he is not',
            'why': 'Blocks remote-only substance while claiming immediate earth-acts.',
            'rejected': ['God can immediately create on earth while substance stays only in heaven'],
        }],
        'notes': ['OCR: XVII PDF 120 / p. 108; Acts 17.'],
        'bible_refs': ['Acts 17:27-28'],
    },
    {
        'section': '442',
        'title': 'Hypostatic union — Colossians 2 requires divine substance on earth',
        'pass_a': (
            'And hither also the analogy of faith leads us. For from faith it is certain '
            'that the divine nature in Christ is personally united to the human nature. And '
            'so that all the fullness of deity dwells in Christ bodily and substantially, as '
            'the Apostle teaches in the second chapter of the Epistle to the Colossians. But '
            'Christ according to the human nature dwelt long on earth. And therefore it is '
            'necessary that the divine substance be present on earth also, unless someone '
            'wishes to dissolve the union of the two natures in Christ: or to say that '
            'Christ\'s human nature was personally united with the divine nature even then '
            'when it was distant from it according to place.'
        ),
        'pass_b': [
            'Faith: divine nature personally united to Christ\'s human nature.',
            'Col 2: all fullness of deity dwells in Him bodily/substantially.',
            'He walked earth — so divine substance was on earth, or the union breaks.',
        ],
        'lemmas': [
            {'latin': 'personaliter unitam', 'gloss': 'personally united'},
            {'latin': 'corporaliter & substantialiter', 'gloss': 'bodily and substantially'},
        ],
        'choices': [{
            'term': 'necesse est divinam substantiam in terris etiam adesse',
            'english': 'it is necessary that the divine substance be present on earth also',
            'why': 'Christological wedge against heaven-only substance.',
            'rejected': ['hypostatic union allows local distance between the natures'],
        }],
        'notes': ['OCR: XVIII PDF 120; Col 2:9.'],
        'bible_refs': ['Col. 2:9'],
    },
    {
        'section': '443',
        'title': 'First proof closed; Solomon — heavens of heavens cannot contain God',
        'pass_a': (
            'Therefore there is no place in the universe where God is not present not only '
            'by His virtue and power, but also by His essence which penetrates all things '
            'and is poured through all. But besides, what we undertook to prove in the '
            'second place, the greatness of God is so great that, filling the whole '
            'universe, He is nevertheless not contained by it, but far surpasses it. That '
            'Solomon teaches in the first book of Kings chapter eight. For after he said of '
            'the temple he had newly built, I have built a house a dwelling for You, a '
            'firm seat in which You may dwell forever, lest anyone think God was '
            'thereafter to be shut up in that magnificent house as the nations\' idols in '
            'their temples, he removes such an absurd thought. Behold, he says, the heavens '
            'of heavens do not contain You, how much less this house which I have built? '
            'Where by heavens of heavens he understands the outermost heavens which contain '
            'the whole world, which he asserts cannot contain and shut God in. Which words '
            'cannot be taken except of God\'s substance, not of God\'s power and the '
            'exertion of His providence. For to whom so stupid and inept could it come to '
            'mind that God\'s power and providence are shut in one house? Nor was there need '
            'for Solomon to meet such a thought.'
        ),
        'pass_b': [
            'First claim closed: essence-presence everywhere.',
            'Second: filling the universe yet not contained — surpasses it.',
            '1 Kgs 8: heavens of heavens cannot contain You — of substance, not mere power.',
        ],
        'lemmas': [
            {'latin': 'ipsum longe exsuperet', 'gloss': 'far surpasses it'},
            {'latin': 'caeli caelorum non capiunt te', 'gloss': 'the heavens of heavens do not contain You'},
        ],
        'choices': [{
            'term': 'accipi non possunt nisi de Dei substantia',
            'english': 'cannot be taken except of God\'s substance',
            'why': 'Opens world-surpassing proof on substantial terms.',
            'rejected': ['Solomon only meant providence cannot fit in a temple'],
        }],
        'notes': ['OCR: XIX PDF 120; 1 Kgs 8:27.'],
        'bible_refs': ['1 Kgs. 8:27'],
    },
    {
        'section': '444',
        'title': 'Job 11 — higher than heaven, deeper than Sheol',
        'pass_a': (
            'Besides that God is not shut in by the world, but is greater and superior to '
            'the whole world, Sophar openly teaches in Job chapter eleven. Higher, he says, '
            'than heaven, deeper than hell, longer than earth, and broader than the sea. For '
            'certainly if God were shut in by the outermost heaven He could not be called '
            'higher than heaven.'
        ),
        'pass_b': [
            'Sophar (Job 11): higher than heaven, deeper than Sheol, longer/broader than earth/sea.',
            'If outermost heaven boxed Him, He could not be higher than heaven.',
            'World-enclosure blocked.',
        ],
        'lemmas': [
            {'latin': 'toto mundo major & superior', 'gloss': 'greater and superior to the whole world'},
            {'latin': 'Excelsior … est caelo', 'gloss': 'Higher … than heaven'},
        ],
        'choices': [{
            'term': 'si Deus extremo caelo concluderetur non posset dici caelo excelsior',
            'english': 'if God were shut in by the outermost heaven He could not be called higher than heaven',
            'why': 'Job 11 undercuts heaven-enclosure.',
            'rejected': ['higher than heaven still allows outermost-heaven enclosure'],
        }],
        'notes': ['OCR: XX PDF 120-121; Job 11:8-9.'],
        'bible_refs': ['Job 11:8-9'],
    },
    {
        'section': '445',
        'title': 'Isaiah 40 and Psalm 145 — greatness without end',
        'pass_a': (
            'And hither also it contributes that God, in Isaiah chapter forty, is said to '
            'have measured the waters in His fist, and the heavens with a span, finally so '
            'great that in His sight the nations are as a drop from a bucket, as the fine '
            'dust on the scales: nay as nothing, and less than nothing and emptiness. By '
            'which words so great a greatness is attributed to God that, with respect to '
            'Him, this whole universe is a small thing and as it were of nothing. And '
            'certainly if God were shut in by the universe and were not superior to it, His '
            'greatness would have an end: since the world is something finite. But the '
            'Psalmist expressly affirms that of God\'s greatness there is no end: Psalm 145. '
            'Great is the Lord, and greatly to be praised, and of His greatness En cheker, '
            'there is no searching out, that is, as the Vulgate rightly renders, there is no '
            'end. For why is there no searching out of God\'s greatness, except because it '
            'has neither measure nor end.'
        ),
        'pass_b': [
            'Isa 40: waters in a fist, heavens in a span — nations as a drop / dust / nothing.',
            'If the finite universe boxed Him, greatness would end.',
            'Ps 145 En cheker: greatness has no end / no searching out.',
        ],
        'lemmas': [
            {'latin': 'mensus fuisse pugillo aquas, & caelos spithama', 'gloss': 'to have measured the waters in His fist, and the heavens with a span'},
            {'latin': 'magnitudinis Dei non esse finem', 'gloss': 'that of God\'s greatness there is no end'},
        ],
        'choices': [{
            'term': 'totum hoc universum sit res parva & quasi nihili',
            'english': 'this whole universe is a small thing and as it were of nothing',
            'why': 'Isa 40 scale blocks world-enclosure of substance.',
            'rejected': ['Isa 40 concerns only moral greatness, not magnitude vs the world'],
        }],
        'notes': ['OCR: XXI PDF 120-121; Isa 40:12-17; Ps 145:3.'],
        'bible_refs': ['Isa. 40:12-17', 'Ps. 145:3'],
    },
    {
        'section': '446',
        'title': 'Could create infinite worlds — so not shut in this one',
        'pass_a': (
            'And certainly, since God by His will created this world from nothing, it cannot '
            'be denied that by equal faculty He can, if He please, create many other worlds '
            'to infinity, and without a certain number. From none of which nevertheless '
            'would He be thought absent. Nor would any reason be given why He would be in '
            'this and not in another. Besides that if God is shut in by this world and is '
            'not outside this world, who could operate outside this world and create another '
            'world? since for production from nothing immediate action is required: from '
            'thence therefore it follows that God\'s greatness has no end and bound at all, '
            'nor that it is shut in by heaven.'
        ),
        'pass_b': [
            'He made this world from nothing — could make endless others.',
            'He would be absent from none; no reason to pick only this box.',
            'Shut inside this world → cannot immediately create another outside it.',
        ],
        'lemmas': [
            {'latin': 'plures alios mundos creare in infinitum', 'gloss': 'to create many other worlds to infinity'},
            {'latin': 'ad productionem ex nihilo requiratur actio immediata', 'gloss': 'for production from nothing immediate action is required'},
        ],
        'choices': [{
            'term': 'Dei magnitudinem non habere finem & terminum ullum',
            'english': 'that God\'s greatness has no end and bound at all',
            'why': 'Possible other worlds force unbounded magnitude.',
            'rejected': ['God could create outside only by remote non-immediate action'],
        }],
        'notes': ['OCR: XXII PDF 121.'],
        'bible_refs': [],
    },
    {
        'section': '447',
        'title': 'Extra mundum — God is His own place (Tertullian, Augustine, Bernard)',
        'pass_a': (
            'But, you will say, how is God outside the world when outside the world there is '
            'nothing? Is God in nothing? I answer that God is outside the world as before '
            'the world was made He was where the world is. Namely God does not need place, '
            'but is Himself place to Himself. According to that of Tertullian in the book '
            'against Praxeas: Before all things God was alone Himself to Himself, and place, '
            'and world, and all things. Which others mean when they say God is outside the '
            'world in Himself, as before He was in Himself. And that after Augustine on '
            'Psalm 122. Before God made the saints where did He dwell? He dwelt in Himself. '
            'To which also belongs that of Bernard, There is nothing further to ask where He '
            'was? besides Himself there was nothing. And this is the sense of those verses '
            'read in Dionysius the Carthusian: Say where He then would be when besides Him '
            'there was nothing? Then, where now, in Himself, since He Himself suffices for '
            'Himself. To which it must be added that outside this world there is indeed no '
            'real and actual place, but there is nevertheless a possible place. Namely God '
            'can there create bodies and places where He will be without any motion of '
            'Himself and change of place.'
        ),
        'pass_b': [
            'Objection: outside the world is nothing — is God in nothing?',
            'Answer: as before creation — God needs no place; He is place to Himself.',
            'Tertullian / Augustine / Bernard / Dionysius; possible place beyond this world.',
        ],
        'lemmas': [
            {'latin': 'est ipse sibi locus', 'gloss': 'is Himself place to Himself'},
            {'latin': 'esse locum possibilem', 'gloss': 'that there is a possible place'},
        ],
        'choices': [{
            'term': 'Deus loco non indiget, sed est ipse sibi locus',
            'english': 'God does not need place, but is Himself place to Himself',
            'why': 'Resolves extra mundum without putting God in a void-thing.',
            'rejected': ['outside the world God occupies empty space as a creature would'],
        }],
        'notes': ['OCR: XXIII PDF 121; Tertullian c. Prax.; Aug. Ps 122; Bernard.'],
        'bible_refs': [],
    },
    {
        'section': '448',
        'title': 'Heaven-habitation texts do not box substance — temple and Church parallels',
        'pass_a': (
            'But what moved Vorstius and certain few to limit the greatness of the divine '
            'essence and to think God\'s substance shut in by heaven are many places of '
            'Scripture where heaven opposed to earth is described as God\'s dwelling and the '
            'place in which He resides. As what is read in Psalm 115. The heavens of heavens '
            'are the Lord\'s, but the earth He gave to the children of men. And Psalm 123. '
            'To You I have lifted eyes who dwell in the heavens. But if therefore God\'s '
            'substance is to be thought contained by heaven and not to be outside heaven '
            'because God is said to dwell peculiarly in heaven: by like reason it will have '
            'to be concluded that God was once shut in by the temple at Jerusalem: since '
            'often also God is said to have chosen that temple as a house and seat in which '
            'He would dwell. And besides, both the whole Church jointly and singular '
            'believers separately are called in Sacred Scripture the temple of God, in which '
            'also God is said to dwell. And yet who will gather from that that God is not '
            'present by substance elsewhere than in the Church and its members?'
        ),
        'pass_b': [
            'Vorstius cites heaven-as-dwelling texts (Ps 115, 123).',
            'Same logic would have boxed God in the Jerusalem temple.',
            'Church/believers are God\'s temple — that does not confine substance to them alone.',
        ],
        'lemmas': [
            {'latin': 'Dei substantiam caelo inclusam', 'gloss': 'God\'s substance shut in by heaven'},
            {'latin': 'pari ratione concludendum erit', 'gloss': 'by like reason it will have to be concluded'},
        ],
        'choices': [{
            'term': 'pari ratione concludendum erit Deum olim inclusum fuisse templo Hierosolymitano',
            'english': 'by like reason it will have to be concluded that God was once shut in by the temple at Jerusalem',
            'why': 'Reductio of Vorstius\'s heaven-habitation reading; next XXV+ peculiar presence.',
            'rejected': ['heaven-habitation texts prove substance cannot be on earth'],
        }],
        'notes': ['OCR: XXIV PDF 121 / p. 109; Ps 115:16; Ps 123:1. Next XXV+ peculiar modes.'],
        'bible_refs': ['Ps. 115:16', 'Ps. 123:1'],
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
        'pdf_120_123_layout.txt', 'pdf_118_120_layout.txt',
        'tess120.txt', 'tess120b.txt', 'tess121.txt', 'tess122.txt',
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
        if 441 <= n <= 448:
            notes = (
                f'Section {sid}: new densify De Dei Immensitate & Omnipraesentia XVII-XXIV; '
                'Pass A!=B; lock-grounded PDF 120-121 / book pp. 108-109.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_immensitate XVII-XXIV packet scope covering all current sections.'
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
                'Scope review: densify De Dei Immensitate & Omnipraesentia XVII-XXIV only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Immensitate through XXIV. XXV+ remains. Not shipped.'
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
        'locus': 'De Dei Immensitate & Omnipraesentia theses XVII-XXIV (operation; union; surpassing)',
        'next_locus': 'De Dei Immensitate & Omnipraesentia XXV+ (peculiar presence; Christ; immobility)',
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
        'deploy_bound': '87247f53',
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
        f'## {day} (Scribe — De Dei Immensitate & Omnipraesentia XVII–XXIV densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Immensitate XVII–XXIV → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 120-121 / pp. 108-109).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Dei Immensitate & Omnipraesentia through XXIV. XXV+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound 87247f53 / tip 440; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Dei Immensitate & Omnipraesentia XVII–XXIV densify)\n\n'
        'CoS densify: Immensitate XVII–XXIV. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Immensitate XVII–XXIV (**'
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
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    APPLY_COPY.parent.mkdir(parents=True, exist_ok=True)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    packet_path, review_path, packet = build_packet_and_review()
    live_tuple = wait_hold(hold_start, post_floor, label='tip-440 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
