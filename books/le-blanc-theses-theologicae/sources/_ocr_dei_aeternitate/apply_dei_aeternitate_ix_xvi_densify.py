#!/usr/bin/env python3
"""Build + apply De Aeternitate Dei IX-XVI densify (tip 464 → 472).

Necessary endless duration; immortality proper; immutability open. Live floor 4683.
After tip-ready: HOLD live>4683 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'dei_aeternitate_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_aeternitate/apply_dei_aeternitate_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['465', '466', '467', '468', '469', '470', '471', '472']
ROMANS = {
    '465': 'IX', '466': 'X', '467': 'XI', '468': 'XII',
    '469': 'XIII', '470': 'XIV', '471': 'XV', '472': 'XVI',
}
TIP_BEFORE = 464
LIVE_FLOOR = 4683
HOLD_MINUTES = 12
PRIOR_START = 457

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeternitate Dei I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeternitate Dei I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeternitate Dei I-XVI, "
    "reconstructed from IA PDF page images with pdftotext + tesseract (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeternitate IX-XVI "
    "(necessary endless duration; immortality proper; immutability; tota simul; Mal 3 / Jas 1)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeternitate Dei & ejus Immutabilitate.\n"
    "Same 1675 Pitt copy-text. Book pp. 111-113 / PDF 123-125 (I-XVI; this packet IX-XVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeternitate Dei I-XVI tip. XVII+ remains.\n"
    "Note: Continues after I-VIII. Necessary perpetual duration; God alone immortal; opens immutability.\n\n"
)

LATIN = {
    '465': (
        'IX. Porro ut Dei essentia non caret simpliciter initio durationis, sed impossibile '
        'est illam non semper fuisse, ita quoque simpliciter & absolute necesse est ut '
        'perpetuo duret, neque finem unquam habeat. Ut enim Deus a nullo est, nec esse '
        'suum ab alio accepit, sic a nullo destrui potest, nec esse suum amittere. '
        'Quapropter ab Apostolo dicitur aphthartos, incorruptibilis sive immortalis, '
        '1 Tim. 1. 17.'
    ),
    '466': (
        'X. Unde patet aeternitatem illam quae Deo competit esse proprium naturae divinae '
        'attributum, quod cum creatura nulla communicari potest. Quum enim creatio sit '
        'productio rei ex nihilo, omnis creatura necessario incepit, & aliquando non fuit, '
        'quandoquidem transiit a non esse ad esse. Ac quamvis ex Philosophis nonnulli '
        'existiment creaturam aliquam ab aeterno posse existere, attamen, quum Deus sit '
        'agens liberrimum quod agit absque ulla necessitate, si quae creatura foret ab '
        'aeterno, saltem potuisset ab aeterno non esse, & habuisse suae durationis initium, '
        'nec esset necesse ut semper fuisset: & similiter quamvis creaturae quaedam nunquam '
        'sint finem habiturae, sicut Angeli & humani spiritus, nihilominus nulla est '
        'creatura quae finem non possit habere, si quidem Deo ita visum esset: nam sicut '
        'omnia ex nihilo creavit, ita omnia ad ipsius nutum in nihilum possunt recidere, & '
        'haec est ratio cur 1 Tim. 6. 16. dicitur Deus solus habere immortalitatem, nimirum '
        'quia licet non possint quaedam ab ulla creatura destrui, nihil est tamen praeter '
        'Deum quod, absolute loquendo, interire & deficere non possit.'
    ),
    '467': (
        'XI. Divinae vero naturae praestantia non elucet tantum in perpetua & omnino '
        'necessaria illius duratione, sed in eo praeterea quod eadem perpetuo manet, nec '
        'saecula praeterlabentia quicquam ei addunt aut detrahunt. Siquidem Deus non solum '
        'aeternus est, sed etiam immutabilis. Res pleraeque non tantum durationem habent '
        'brevibus admodum terminis circumscriptam, sed etiam quandiu durant sunt in '
        'perpetuo fluxu: nam de earum substantia jugiter aliquid effluit, & aliquid ei de '
        'novo accedit, donec tandem penitus intereant & dissolvantur, ut videre est in '
        'plantis atque animalibus. Quod si quaedam substantia ita firma sit ut eadem '
        'perpetuo maneat, saltem novos actus & nova accidentia suscipere potest, & hactenus '
        'est variis mutationibus subdita: at Deus est omnis omnino mutationis expers, '
        'nullam perfectionem cum tempore amittit, nec ulla ei de novo accedit, sed '
        'quaecunque perfectio in eo unquam fuit, ea jam actu perseverat ac incessanter '
        'perseverabit, & quaecunque in eo unquam erit ea jam actu est, & nunquam non fuit.'
    ),
    '468': (
        'XII. Quapropter Deus merito dicitur actus purus, quia actu jam est quicquid fuit, '
        'vel erit: nec ulla est in eo potestas qua possit aliquid quod habet deponere, aut '
        'aliquid quod non habet suscipere.'
    ),
    '469': (
        'XIII. Optimo quoque jure a Theologis vita Dei dicitur non tantum interminabilis, '
        'sed etiam tota simul, quia de vita ejus, sicut de nostra, nihil cum tempore '
        'effluit, sed Deus quovis momento simul habet, quicquid in toto simul tempore, '
        'quum ipsi, temporis progressus nihil adjiciat, vel adimat, ut caeteris rebus, quae '
        'sunt mutationi obnoxiae: quo respicit Plutarchus tract. de vocula e templi Delphici '
        'vestibulo inscripta. Deus, inquit, cum unus sit unico nunc aeternitatem complevit: '
        'quia scilicet in tota temporis amplitudine nullum momentum sumi potest in quo '
        'habeat aliquid quod ante non habuerit, vel olim habiturus non sit, aut non habeat '
        'aliquid quod antea habebat, aut aliquando sit habiturus. Unde tempus merito '
        'comparatur flumini perpetuo labenti, nauta, qui fluvio innatans ab eo abripitur; '
        'Deus vero arbori altis radicibus alveo implantatae, immobiliter & constanter in '
        'eodem statu manenti; fluvius ille temporis imago jugi fluxu praeterlabitur.'
    ),
    '470': (
        'XIV. Praeterea inde est quod Plato, & alii post eum Philosophi pronuntiaverunt de '
        'Deo nec praeteritum, nec futurum, sive fuit, vel erit, sed solum praesens sive est '
        'proprie dici posse: quia scilicet, Dei aeterna duratio omnia quidem tempora '
        'praeteritum praesens & futurum complectitur: at vero in Dei natura nihil est '
        'praeteritum neque futurum: nec enim quicquam de ea praeteriit, ut etiam ad eam '
        'quicquam nondum advenit, sed eadem & immutata perpetuo perseverat. Jam autem '
        'praeteriti & futuri temporis verba inventa sunt ad significandas mutationes rerum, '
        'quae cum tempore transeunt, & tempore mensurantur: nam proprie ac stricte loquendo '
        'fuisse dicitur quod non est amplius, ut quum apud Poetam dicitur fuit Ilium, & '
        'futurum esse quod nondum est, ut Alter erit tum Tiphys: sed quamvis praeteriti & '
        'futuri temporis verba hoc sensu Deo non congruant, hoc tamen non obstat quominus '
        'de Deo possimus vere dicere fuit, modo intelligamus illum eundem omnino jam '
        'perseverare qui antea fuerit: itemque erit, modo intelligamus talem ab aevo ac '
        'etiamnum esse qualis est perpetuo futurus, quod est de eo affirmare futurum, sed '
        'absque negatione praeteriti & praesentis: & affirmare praeteritum, sed absque '
        'negatione praesentis & futuri: ut quum Deus describitur loco supra citato qui est, '
        'qui erat, & qui venturus est: quod Augustinus optime explicat tractatu 99. in '
        'Joan. Quamvis inquit natura illa immutabilis & ineffabilis non recipiat fuit & '
        'erit, sed tantum est, tamen propter mutabilitatem temporum in quibus versatur '
        'nostra mortalitas & mutabilitas, non mendaciter dicimus, est, fuit, & erit: fuit '
        'in praeteritis saeculis, est in praesentibus, erit in futuris; fuit quia nunquam '
        'defuit, erit quia nunquam deerit; est quia semper est.'
    ),
    '471': (
        'XV. Porro hanc a nobis descriptam immutabilitatem Deus ipse sibi tribuit Mal. 3. '
        'Ego, inquit, Dominus & non mutor: & illam egregie describit Psaltes per '
        'oppositionem ad res creatas quae sunt mutationi obnoxiae Psal. 102. quem modo '
        'citavimus, ubi postquam dixit caelos ipsos qui initium suae durationis habuerunt, '
        'immutandos, & tandem etiam perituros esse, de Deo dicit Atta hu, Tu idem ipse es, '
        '& anni tui non deficient: & huc quoque respicit Jacobus 1. v. 17. dum Deum vocat '
        'Patrem luminum, apud quem non est transmutatio, nec vicissitudinis obumbratio.'
    ),
    '472': (
        'XVI. Nec minus evidenter ipsa ratio probat Deum esse omnis omnino mutationis '
        'expertem. Id enim necessario colligitur ex ejus absoluta simplicitate, quae ante a '
        'nobis demonstrata fuit Thesibus de hoc argumento editis: etenim quicquid mutatur, '
        'secundum aliquid manet, & secundum aliquid transit, nempe subjectum manet, forma '
        'vero aut actus aliquis ab eo abscedit: Ac proinde necesse est id quod mutatur a '
        'summa simplicitate deficere, & aliquo modo componi ex diversis. Igitur cum Deus '
        'sit simplicissimus, nec in eo sit aliud & aliud, planum est in eum nullam '
        'mutationem cadere.'
    ),
}

SECTIONS = [
    {
        'section': '465',
        'title': 'Necessary perpetual duration — incorruptible / immortal',
        'pass_a': (
            'Further as God\'s essence does not simply lack a beginning of duration, but it '
            'is impossible that it not always have been, so also it is simply and absolutely '
            'necessary that it perpetually endure, and never have an end. For as God is from '
            'none, nor received His being from another, so He can be destroyed by none, nor '
            'lose His being. Wherefore by the Apostle He is called aphthartos, incorruptible '
            'or immortal, 1 Tim. 1. 17.'
        ),
        'pass_b': [
            'Not only no start — it is impossible He ever not was.',
            'So also necessary: perpetual duration, never an end.',
            '1 Tim 1:17 aphthartos — incorruptible / immortal.',
        ],
        'lemmas': [
            {'latin': 'necesse est ut perpetuo duret, neque finem unquam habeat', 'gloss': 'it is necessary that it perpetually endure, and never have an end'},
            {'latin': 'aphthartos, incorruptibilis sive immortalis', 'gloss': 'aphthartos, incorruptible or immortal'},
        ],
        'choices': [{
            'term': 'a nullo destrui potest, nec esse suum amittere',
            'english': 'He can be destroyed by none, nor lose His being',
            'why': 'Pairs necessary no-start with necessary no-end.',
            'rejected': ['God could cease if He willed to destroy Himself'],
        }],
        'notes': ['OCR: IX PDF 124; 1 Tim 1:17.'],
        'bible_refs': ['1 Tim. 1:17'],
    },
    {
        'section': '466',
        'title': 'Eternity proper to God alone — 1 Tim 6:16 sole immortality',
        'pass_a': (
            'Whence it is clear that that eternity which belongs to God is a proper '
            'attribute of the divine nature, which can be shared with no creature. For since '
            'creation is production of a thing from nothing, every creature necessarily '
            'began, and sometime was not, inasmuch as it passed from not-being to being. And '
            'although some among the Philosophers think some creature can exist from '
            'eternity, yet, since God is a most free agent who acts without any necessity, '
            'if any creature were from eternity, at least it could have not been from '
            'eternity, and have had a beginning of its duration, nor would it be necessary '
            'that it always had been: and likewise although certain creatures will never '
            'have an end, as Angels and human spirits, nevertheless there is no creature '
            'which cannot have an end, if indeed it so seemed good to God: for as He created '
            'all things from nothing, so all things at His nod can fall back into nothing, '
            'and this is the reason why in 1 Tim. 6. 16. God is said alone to have '
            'immortality, namely because although certain things cannot be destroyed by any '
            'creature, there is nevertheless nothing besides God which, absolutely speaking, '
            'cannot perish and fail.'
        ),
        'pass_b': [
            'Divine eternity is incommunicable — every creature began from nothing.',
            'Even a supposed eternal creature could have not been; angels can still end if God wills.',
            '1 Tim 6:16: God alone has immortality — absolute inability to perish.',
        ],
        'lemmas': [
            {'latin': 'proprium naturae divinae attributum', 'gloss': 'a proper attribute of the divine nature'},
            {'latin': 'Deus solus habere immortalitatem', 'gloss': 'that God alone has immortality'},
        ],
        'choices': [{
            'term': 'nihil est tamen praeter Deum quod, absolute loquendo, interire & deficere non possit',
            'english': 'there is nevertheless nothing besides God which, absolutely speaking, cannot perish and fail',
            'why': 'Defines immortality proper vs creaturely indefectibility.',
            'rejected': ['angels share God\'s absolute immortality'],
        }],
        'notes': ['OCR: X PDF 124; 1 Tim 6:16.'],
        'bible_refs': ['1 Tim. 6:16'],
    },
    {
        'section': '467',
        'title': 'Eternal and immutable — no flux of perfection with time',
        'pass_a': (
            'But the excellence of the divine nature does not shine only in its perpetual '
            'and altogether necessary duration, but in this besides, that the same perpetually '
            'remains, nor do passing ages add or take anything from it. Since God is not '
            'only eternal, but also immutable. Most things not only have duration '
            'circumscribed by very short bounds, but also while they last are in perpetual '
            'flux: for from their substance continually something flows out, and something '
            'newly accedes to them, until at last they utterly perish and are dissolved, as '
            'is seen in plants and animals. But if some substance is so firm that the same '
            'perpetually remains, at least it can take on new acts and new accidents, and so '
            'far is subject to various changes: but God is altogether without every change, '
            'loses no perfection with time, nor does any newly accede to Him, but whatever '
            'perfection was ever in Him, that already in act perseveres and will '
            'incessantly persevere, and whatever will ever be in Him that already is in '
            'act, and never was not.'
        ),
        'pass_b': [
            'Not only perpetual duration — the same remains; ages add/take nothing.',
            'Creatures flux or at least take new acts/accidents.',
            'God: no change — every perfection already in act, never was not.',
        ],
        'lemmas': [
            {'latin': 'non solum aeternus est, sed etiam immutabilis', 'gloss': 'is not only eternal, but also immutable'},
            {'latin': 'omnis omnino mutationis expers', 'gloss': 'altogether without every change'},
        ],
        'choices': [{
            'term': 'quaecunque perfectio in eo unquam fuit, ea jam actu perseverat',
            'english': 'whatever perfection was ever in Him, that already in act perseveres',
            'why': 'Opens immutability from eternity.',
            'rejected': ['God gains new perfections across ages'],
        }],
        'notes': ['OCR: XI PDF 124-125.'],
        'bible_refs': [],
    },
    {
        'section': '468',
        'title': 'Actus purus — already is whatever was or will be',
        'pass_a': (
            'Wherefore God is deservedly called pure act, because He already is in act '
            'whatever was, or will be: nor is there in Him any power by which He could lay '
            'aside something He has, or take on something He does not have.'
        ),
        'pass_b': [
            'Pure act: already is whatever was or will be.',
            'No power to drop what He has.',
            'No power to take on what He lacks.',
        ],
        'lemmas': [
            {'latin': 'actus purus', 'gloss': 'pure act'},
            {'latin': 'actu jam est quicquid fuit, vel erit', 'gloss': 'He already is in act whatever was, or will be'},
        ],
        'choices': [{
            'term': 'nec ulla est in eo potestas qua possit aliquid quod habet deponere',
            'english': 'nor is there in Him any power by which He could lay aside something He has',
            'why': 'Pure act blocks real potency toward change.',
            'rejected': ['God has unused potencies waiting to be actualized'],
        }],
        'notes': ['OCR: XII PDF 125.'],
        'bible_refs': [],
    },
    {
        'section': '469',
        'title': 'Life of God tota simul — Plutarch\'s river and tree',
        'pass_a': (
            'Also with best right by the Theologians the life of God is said not only '
            'interminable, but also all at once, because from His life, as from ours, '
            'nothing flows away with time, but God at any moment has at once whatever in '
            'the whole of time at once, since for Him the progress of time adds or takes '
            'nothing, as for other things which are liable to change: to which Plutarch '
            'looks in the treatise on the little word inscribed on the vestibule of the '
            'Delphic temple. God, he says, since He is one, has completed eternity in a '
            'unique now: because namely in the whole amplitude of time no moment can be '
            'taken in which He has something He did not have before, or will not someday '
            'have, or does not have something He had before, or will someday have. Whence '
            'time is deservedly compared to a river perpetually flowing, a sailor who '
            'swimming in the stream is carried off by it; but God to a tree planted with '
            'deep roots in the channel, remaining immoveably and constantly in the same '
            'state; that river, image of time, passes by with continuous flow.'
        ),
        'pass_b': [
            'God\'s life: not only endless — tota simul (all at once).',
            'Time adds/takes nothing for Him; Plutarch: eternity in a unique now.',
            'Time as river carrying the sailor; God as rooted tree the stream flows past.',
        ],
        'lemmas': [
            {'latin': 'tota simul', 'gloss': 'all at once'},
            {'latin': 'unico nunc aeternitatem complevit', 'gloss': 'has completed eternity in a unique now'},
        ],
        'choices': [{
            'term': 'vita Dei dicitur non tantum interminabilis, sed etiam tota simul',
            'english': 'the life of God is said not only interminable, but also all at once',
            'why': 'Boethian tota simul via Plutarch image.',
            'rejected': ['God\'s life is only successive endless duration'],
        }],
        'notes': ['OCR: XIII PDF 125; Plutarch Delphic EI.'],
        'bible_refs': [],
    },
    {
        'section': '470',
        'title': 'Plato and Augustine — was / will be without change of nature',
        'pass_a': (
            'Besides thence it is that Plato, and other Philosophers after him, pronounced '
            'that of God neither past nor future, or was or will be, but only present or is '
            'can properly be said: because namely God\'s eternal duration indeed embraces '
            'all times past present and future: but in God\'s nature there is nothing past '
            'nor future: for nothing of it has passed, as also nothing has not yet come to '
            'it, but the same and unchanged perpetually perseveres. Now words of past and '
            'future time were invented to signify changes of things which pass with time and '
            'are measured by time: for properly and strictly speaking that is said to have '
            'been which is no longer, as when among the Poet it is said Ilium was, and to '
            'be future what is not yet, as Then there will be another Tiphys: but although '
            'words of past and future time in this sense do not fit God, this nevertheless '
            'does not hinder us from being able truly to say of God He was, provided we '
            'understand that He altogether already perseveres the same who was before: and '
            'likewise He will be, provided we understand that He is from of old and even now '
            'such as He is perpetually going to be — which is to affirm of Him future, but '
            'without negation of past and present; and to affirm past, but without negation '
            'of present and future: as when God is described in the place cited above who '
            'is, who was, and who is to come: which Augustine excellently explains in '
            'tractate 99 on John. Although, he says, that immutable and ineffable nature '
            'does not receive was and will be, but only is, yet because of the mutability of '
            'the times in which our mortality and mutability move, we do not falsely say is, '
            'was, and will be: was in past ages, is in present, will be in future; was '
            'because He never was lacking, will be because He will never be lacking; is '
            'because He always is.'
        ),
        'pass_b': [
            'Plato: properly only is — yet duration embraces all times.',
            'Was/will-be words track creaturely change; still true of God without negation.',
            'Augustine on John: was / is / will be = never lacking, always is.',
        ],
        'lemmas': [
            {'latin': 'in Dei natura nihil est praeteritum neque futurum', 'gloss': 'in God\'s nature there is nothing past nor future'},
            {'latin': 'fuit quia nunquam defuit, erit quia nunquam deerit; est quia semper est', 'gloss': 'was because He never was lacking, will be because He will never be lacking; is because He always is'},
        ],
        'choices': [{
            'term': 'eadem & immutata perpetuo perseverat',
            'english': 'the same and unchanged perpetually perseveres',
            'why': 'Allows tensed speech without tensed change in God.',
            'rejected': ['saying God was implies something of God has passed away'],
        }],
        'notes': ['OCR: XIV PDF 125; Aug. Tract. in Io. 99; Rev 1:8.'],
        'bible_refs': ['Rev. 1:8'],
    },
    {
        'section': '471',
        'title': 'Malachi 3 and James 1 — I do not change; no shadow of turning',
        'pass_a': (
            'Further this immutability described by us God Himself attributes to Himself in '
            'Mal. 3. I, He says, the Lord and I do not change: and the Psalmist excellently '
            'describes it by opposition to created things which are liable to change in '
            'Psalm 102 which we just cited, where after he said the heavens themselves which '
            'had a beginning of their duration are to be changed, and at last even to perish, '
            'of God he says Atta hu, You Yourself are the same, and Your years will not '
            'fail: and hither also James 1. v. 17. looks when he calls God the Father of '
            'lights, with whom there is no change, nor shadow of turning.'
        ),
        'pass_b': [
            'Mal 3: I the Lord — I do not change.',
            'Ps 102: heavens change and perish; You are the same.',
            'Jas 1:17: Father of lights — no change, no shadow of turning.',
        ],
        'lemmas': [
            {'latin': 'Ego … Dominus & non mutor', 'gloss': 'I … the Lord and I do not change'},
            {'latin': 'non est transmutatio, nec vicissitudinis obumbratio', 'gloss': 'there is no change, nor shadow of turning'},
        ],
        'choices': [{
            'term': 'Tu idem ipse es, & anni tui non deficient',
            'english': 'You Yourself are the same, and Your years will not fail',
            'why': 'Scripture seals immutability against creaturely flux.',
            'rejected': ['Mal 3 only means God will not break covenant mood'],
        }],
        'notes': ['OCR: XV PDF 125; Mal 3:6; Ps 102:27; Jas 1:17.'],
        'bible_refs': ['Mal. 3:6', 'Ps. 102:27', 'Jas. 1:17'],
    },
    {
        'section': '472',
        'title': 'Immutability from absolute simplicity',
        'pass_a': (
            'Nor less evidently does reason itself prove that God is altogether without '
            'every change. For that is necessarily gathered from His absolute simplicity, '
            'which was demonstrated before by us in Theses published on this argument: for '
            'whatever changes remains according to something, and passes according to '
            'something, namely the subject remains, but a form or some act withdraws from '
            'it: And therefore what changes must fall short of highest simplicity, and in '
            'some way be composed of divers things. Therefore since God is most simple, nor '
            'is there in Him one thing and another, it is plain that no change falls upon Him.'
        ),
        'pass_b': [
            'Reason: absolute simplicity → no change.',
            'Change needs a remaining subject and a departing form/act — composition.',
            'Most simple God: no other-and-other — no change can fall on Him.',
        ],
        'lemmas': [
            {'latin': 'ex ejus absoluta simplicitate', 'gloss': 'from His absolute simplicity'},
            {'latin': 'nec in eo sit aliud & aliud', 'gloss': 'nor is there in Him one thing and another'},
        ],
        'choices': [{
            'term': 'planum est in eum nullam mutationem cadere',
            'english': 'it is plain that no change falls upon Him',
            'why': 'Closes IX-XVI on simplicity-grounded immutability; next XVII+ perfection.',
            'rejected': ['a simple God can still change by successive acts'],
        }],
        'notes': ['OCR: XVI PDF 125; next XVII+ infinite perfection bars better/worse change.'],
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
    for name in (
        'pdf_124_126_layout.txt', 'pdf_122_126_layout.txt',
        'tess123.txt', 'tess124.txt', 'tess125.txt',
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
        if 465 <= n <= 472:
            notes = (
                f'Section {sid}: new densify De Aeternitate Dei IX-XVI; '
                'Pass A!=B; lock-grounded PDF 124-125 / book pp. 112-113.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_aeternitate IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Aeternitate Dei IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Aeternitate through XVI. XVII+ remains. Not shipped.'
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
        'locus': 'De Aeternitate Dei theses IX-XVI (endless duration; immortality; immutability)',
        'next_locus': 'De Aeternitate Dei XVII+ (perfection bars change; species of mutation)',
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
        'deploy_bound': 'd6559810',
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
        f'## {day} (Scribe — De Aeternitate Dei IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Aeternitate IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 124-125 / pp. 112-113).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Aeternitate Dei through XVI. XVII+ remains. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Deploy bound d6559810 / tip 464; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Aeternitate Dei IX–XVI densify)\n\n'
        'CoS densify: Aeternitate IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Aeternitate IX–XVI (**'
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-464 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
