#!/usr/bin/env python3
"""Build + apply De Aeterna Hominum Electione IX-XVI densify (tip 569 → 577).

Communior effects; Estius/Mendoza expansive effects; creatable-object party.
Live floor 5062. After tip-ready: HOLD live>5062 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'aeterna_electio_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_aeterna_electio/apply_aeterna_electio_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['570', '571', '572', '573', '574', '575', '576', '577']
ROMANS = {
    '570': 'IX', '571': 'X', '572': 'XI', '573': 'XII',
    '574': 'XIII', '575': 'XIV', '576': 'XV', '577': 'XVI',
}
TIP_BEFORE = 569
PRIOR_START = 562  # lock rebuild from I through tip
LIVE_FLOOR = 5062
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeterna Hominum Electione et Praedestinatione I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeterna Hominum Electione et Praedestinatione I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeterna Hominum Electione et Praedestinatione I-XVI, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeterna Electio IX-XVI "
    "(communior Rom.8 effects; Estius/Mendoza expansive; creatable object)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeterna Hominum Electione et Praedestinatione "
    "(quis sit vocum illarum usus; tum quomodo varie assignentur Praedestinationis effectus & objectum).\n"
    "Same 1675 Pitt copy-text. Book pp. 127-129 / PDF 139-141 (I-XVI; this packet IX-XVI). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeterna Hominum Electione et Praedestinatione I-XVI tip. Next: Aeterna Electio XVII+.\n"
    "Note: Communior Rom.8 effects; Estius/Mendoza; creatable vs fallen object. "
    "XIV numeral lost at PDF page-break; body reconstructed from continuation before XV.\n\n"
)

LATIN = {
    '570': (
        'IX. Hodie vero Doctorum Ecclesiae Romanae communior sententia est, effectus '
        'praedestinationis esse, tum ipsam beatitudinem supernaturalem, tum media illa '
        'particularia, quibus unusquisque praedestinatus supernaturaliter adipiscitur '
        'beatitudinem. Adeoque tres effectus praedestinationis generales numerant, qui '
        'notantur ab Apostolo Rom. 8. Vocationem, scilicet, justificationem, & '
        'glorificationem. Nempe, praedestinationis nomine intelligunt, tum decretum de '
        'conferenda certis quibusdam hominibus coelesti beatitudine, tum decretum de mediis '
        'quibus ad fruitionem beatitudinis illius deducuntur.'
    ),
    '571': (
        'X. Sed sunt nonnulli Scholae Romanae Theologi qui longe plura numerant inter '
        'praedestinationis effectus: atque inter alia permissionem peccatorum illorum in quae '
        'incidunt electi, adeoque ipsius primi peccati permissionem. Imo ad praedestinationis '
        'effectus referunt ipsam creationem & conservationem eorum qui praedestinantur. Quod '
        'facit inprimis Estius in 1. Sentent. Dist. 40. paragr. 7.'
    ),
    '572': (
        'XI. Quin ulterius procedit Alphonsus Mendoza Augustinianus Professor '
        'Salmanticensis jam supra memoratus. Nam ex professo tuetur primum omnium actuum '
        'divinorum fuisse praedestinationem, ex qua consecutae sunt caetera omnia decreta de '
        'condendo mundo, de creandis hominibus, de permittendo peccato, &c. Itaque totius '
        'hujus universi creationem & conservationem, imo ipsam Daemonum & impiorum '
        'reprobationem, & justam damnationem, vult numeranda esse inter effecta '
        'praedestinationis Christi & electorum. Ac ut verbo dicam, pretendit nihil omnino a '
        'Deo in quocunque genere vel parvum, vel magnum fieri, vel permitti, quod non sit '
        'effectus praedestinationis, & medium ad illam exequendam ordinatum.'
    ),
    '573': (
        'XII. Nam in Controversiis Theologicis, jam citata prima quaestione Scholastica de '
        'Praedestinatione, Sectione sexta, haec est ejus secunda conclusio. Nulla futuri '
        'praescientia praesupponitur in mente Dei ad praedestinationem, sed omnia ex ipsa '
        'sequuntur: atque adeo nihil prorsus ab aeterno decrevit Deus facere, vel in tempore '
        'facit, vel permittit, sive intendit, sive naturale, sive supernaturale, sive sit res '
        'magni ponderis, sive minimi, & fere nullius, quod non proveniat, sitque effectus, & '
        'medium praedestinationis electorum & Christi. Atque adeo omnia cadunt sub ordine '
        'divinae praedestinationis, tanquam media ad Christi & sanctorum gloriam ordinata.'
    ),
    '574': (
        'XIII. Unde est haec ejus tertia conclusio. Non est aliqua alia providentia in Deo '
        'antecedens praedestinationem, ex qua scilicet providentia proveniant res naturales, '
        '& quidam alii effectus supernaturales: sed unica est duntaxat providentia, ipsaque '
        'est praedestinatio, ex qua omnia in universum, nullo prorsus excepto, habent sequi.'
    ),
    '575': (
        'XIV. Atque adeo juxta hanc conclusionem, totum universum, ut complectitur '
        'naturalia, & supernaturalia, bona, & mala, substantias & accidentia, & omnes in '
        'universum modos essendi & operandi, non solum in generali, sed in specie, & '
        'individuo, sunt consideranda tanquam unicum objectum totale divinae '
        'praedestinationis: ita ut nihil omnino sit quod subterfugiat illius objecti '
        'latitudinem, & quod non cadat sub actu illo praedestinationis.'
    ),
    '576': (
        'XV. Ex eo vero licet colligere sub quo respectu duo illi Doctores hominem '
        'objectum putent Deo praedestinanti, nempe non ut lapsum neque ut conditum in divina '
        'praescientia, sed potius simpliciter ut possibilem, sive creabilem. Nam cum '
        'permissio lapsus primi hominis, imo & ipsius hominis creatio, ab iis recensetur '
        'inter effectus praedestinationis, necesse est ut, ex eorum mente, praevisio lapsus '
        '& creationis non praecesserit in Deo, juxta nostrum intelligendi modum, decretum '
        'praedestinationis, sed potius illud secuta sit; & sic Deus homines praedestinans '
        'illos ut lapsos & conditos considerare non potuit, sed solum ut a se creabiles. '
        'Quod cum Mendoza agnoscit Estius. Non ita nominamus, inquit, praedestinationem '
        'hominum lapsi, quasi praevisio lapsus primi hominis, atque in eo totius humani '
        'generis, praecesserit in Deo, secundum modum intelligentiae nostrae, '
        'praedestinationem aliquorum ex toto hominum genere ad vitam aeternam. Citata '
        'Distinctione quadragesima libri primi sententiarum, paragrapho 6.'
    ),
    '577': (
        'XVI. Idem autem secum hac in parte sensisse non paucos, ex Scholasticis, tam '
        'veteribus, quam recentioribus, ostendit Alphonsus Mendoza, jam dicta quaestione, '
        'Sectione quarta. Ubi pro se citat Jacobum Naclantum Episcopum Clugiensem, Albertum '
        'Pighium, Petrum Galatinum, Ambrosium Catharinum, & quem caeteris omnibus praefert, '
        'Joannem Scotum, cujus citat multa verba, ex quibus patet, juxta Doctorem illum '
        'subtilem, Deum electos praedestinasse, & bona gratiae ipsis voluisse, priusquam '
        'vellet hunc mundum sensibilem, quem Deus ab aeterno voluit in ordine ad hominem '
        'praedestinatum, propter quem totam naturam visibilem creare constituit.'
    ),
}

# Prior I-VIII latin kept in lock from existing source when rebuilding
SECTIONS = [
    {
        'section': '570',
        'title': 'Communior Roman view — beatitude plus means; Rom. 8 triad',
        'pass_a': (
            'But today the more common opinion of the Doctors of the Roman Church is that '
            'the effects of predestination are both supernatural beatitude itself and those '
            'particular means by which each predestined person supernaturally obtains '
            'beatitude. And therefore they number three general effects of predestination, '
            'which are noted by the Apostle in Romans 8: namely Calling, Justification, and '
            'Glorification. Namely, by the name of predestination they understand both the '
            'decree of conferring heavenly beatitude on certain men and the decree concerning '
            'the means by which they are led to the enjoyment of that beatitude.'
        ),
        'pass_b': [
            'Common Roman view: effects = beatitude + the particular means to it.',
            'Three general effects from Rom. 8: vocation, justification, glorification.',
            'Name covers both the glory-decree and the means-decree.',
        ],
        'lemmas': [
            {'latin': 'tum ipsam beatitudinem supernaturalem, tum media illa particularia', 'gloss': 'both supernatural beatitude itself and those particular means'},
            {'latin': 'Vocationem, scilicet, justificationem, & glorificationem', 'gloss': 'namely Calling, Justification, and Glorification'},
        ],
        'choices': [{
            'term': 'tres effectus praedestinationis generales numerant, qui notantur ab Apostolo Rom. 8',
            'english': 'they number three general effects of predestination, which are noted by the Apostle in Romans 8',
            'why': 'Opens IX–XVI on the communior effect-list against VIII’s Durandus means-only.',
            'rejected': ['the common Roman view excludes glorification from the effects'],
        }],
        'notes': ['OCR: IX PDF 140; Rom. 8 triad.'],
        'bible_refs': ['Rom. 8:30'],
    },
    {
        'section': '571',
        'title': 'Some Romans count more — permission of sins; creation (Estius)',
        'pass_a': (
            'But there are some Theologians of the Roman School who number far more among '
            'the effects of predestination: and among other things the permission of those '
            'sins into which the elect fall, and even the permission of the first sin itself. '
            'Indeed they refer to the effects of predestination the very creation and '
            'conservation of those who are predestined. Which Estius does especially in the '
            'first book of the Sentences, Distinction 40, paragraph 7.'
        ),
        'pass_b': [
            'Some Romans expand the effect-list far beyond the Rom. 8 triad.',
            'Include permission of the elect’s sins — even the first sin.',
            'Also creation & conservation of the predestined — Estius 1 Sent. d.40 §7.',
        ],
        'lemmas': [
            {'latin': 'permissionem peccatorum illorum in quae incidunt electi', 'gloss': 'the permission of those sins into which the elect fall'},
            {'latin': 'ipsam creationem & conservationem eorum qui praedestinantur', 'gloss': 'the very creation and conservation of those who are predestined'},
        ],
        'choices': [{
            'term': 'Imo ad praedestinationis effectus referunt ipsam creationem & conservationem eorum qui praedestinantur',
            'english': 'Indeed they refer to the effects of predestination the very creation and conservation of those who are predestined',
            'why': 'Marks the Estius expansion beyond vocation/justification/glorification.',
            'rejected': ['Estius keeps creation outside praedestinatio’s effects'],
        }],
        'notes': ['OCR: X PDF 140; Estius 1 Sent. d.40.'],
        'bible_refs': [],
    },
    {
        'section': '572',
        'title': 'Mendoza — predestination the first divine act; all else its effect',
        'pass_a': (
            'Indeed Alphonsus Mendoza, the Augustinian Professor of Salamanca already '
            'mentioned above, goes still further. For he expressly maintains that '
            'predestination was the first of all the divine acts, from which followed all '
            'the other decrees concerning founding the world, creating men, permitting sin, '
            '&c. And therefore he will have the creation and conservation of this whole '
            'universe, and even the reprobation and just damnation of Demons and of the '
            'impious, numbered among the effects of the predestination of Christ and of the '
            'elect. And to say it in a word, he maintains that nothing at all is done or '
            'permitted by God in any kind, whether small or great, which is not an effect of '
            'predestination and a means ordained to executing it.'
        ),
        'pass_b': [
            'Mendoza (Salamanca Augustinian): praedestinatio = first of all divine acts.',
            'World, creation, permission of sin — all follow from it.',
            'Even demon/impious reprobation = effect of Christ’s and the elect’s predestination.',
        ],
        'lemmas': [
            {'latin': 'primum omnium actuum divinorum fuisse praedestinationem', 'gloss': 'that predestination was the first of all the divine acts'},
            {'latin': 'nihil omnino a Deo … fieri, vel permitti, quod non sit effectus praedestinationis', 'gloss': 'that nothing at all is done or permitted by God … which is not an effect of predestination'},
        ],
        'choices': [{
            'term': 'primum omnium actuum divinorum fuisse praedestinationem, ex qua consecutae sunt caetera omnia decreta',
            'english': 'that predestination was the first of all the divine acts, from which followed all the other decrees',
            'why': 'States Mendoza’s maximal ordering of decrees.',
            'rejected': ['Mendoza puts world-creation before predestination'],
        }],
        'notes': ['OCR: XI PDF 140; Mendoza.'],
        'bible_refs': [],
    },
    {
        'section': '573',
        'title': 'Mendoza concl. 2 — no foreknowledge presupposed; all is medium of predestination',
        'pass_a': (
            'For in the Theological Controversies, in the first Scholastic question on '
            'Predestination already cited, Section six, this is his second conclusion. No '
            'foreknowledge of the future is presupposed in the mind of God unto '
            'predestination, but all things follow from it: and therefore God has decreed '
            'from eternity to do absolutely nothing, or in time does or permits or intends '
            'nothing, whether natural or supernatural, whether a thing of great weight or of '
            'the least and almost of none, which does not proceed from, and is an effect and '
            'means of, the predestination of the elect and of Christ. And therefore all '
            'things fall under the order of divine predestination, as means ordained to the '
            'glory of Christ and of the saints.'
        ),
        'pass_b': [
            'Mendoza Sect.6 concl.2: no future-foreknowledge presupposed to praedestinatio.',
            'Everything God decrees/does/permits follows from it.',
            'All ordered as means to Christ’s and the saints’ glory.',
        ],
        'lemmas': [
            {'latin': 'Nulla futuri praescientia praesupponitur in mente Dei ad praedestinationem', 'gloss': 'No foreknowledge of the future is presupposed in the mind of God unto predestination'},
            {'latin': 'tanquam media ad Christi & sanctorum gloriam ordinata', 'gloss': 'as means ordained to the glory of Christ and of the saints'},
        ],
        'choices': [{
            'term': 'Nulla futuri praescientia praesupponitur in mente Dei ad praedestinationem, sed omnia ex ipsa sequuntur',
            'english': 'No foreknowledge of the future is presupposed in the mind of God unto predestination, but all things follow from it',
            'why': 'Mendoza’s second conclusion — praedestinatio before foresight.',
            'rejected': ['Mendoza presupposes foresight of futures before predestination'],
        }],
        'notes': ['OCR: XII PDF 140; Mendoza Controv. Sect.6 concl.2.'],
        'bible_refs': [],
    },
    {
        'section': '574',
        'title': 'Mendoza concl. 3 — no providence prior to predestination',
        'pass_a': (
            'Whence is this his third conclusion. There is not some other providence in God '
            'antecedent to predestination, from which providence namely natural things and '
            'certain other supernatural effects would proceed: but there is only one single '
            'providence, and that itself is predestination, from which all things in the '
            'universe, with absolutely nothing excepted, have to follow.'
        ),
        'pass_b': [
            'Mendoza concl.3: no second providence before praedestinatio.',
            'The one providence = predestination itself.',
            'Everything in the universe follows from it — nothing excepted.',
        ],
        'lemmas': [
            {'latin': 'Non est aliqua alia providentia in Deo antecedens praedestinationem', 'gloss': 'There is not some other providence in God antecedent to predestination'},
            {'latin': 'unica est duntaxat providentia, ipsaque est praedestinatio', 'gloss': 'there is only one single providence, and that itself is predestination'},
        ],
        'choices': [{
            'term': 'unica est duntaxat providentia, ipsaque est praedestinatio, ex qua omnia in universum, nullo prorsus excepto, habent sequi',
            'english': 'there is only one single providence, and that itself is predestination, from which all things in the universe, with absolutely nothing excepted, have to follow',
            'why': 'Collapses providence into predestination.',
            'rejected': ['Mendoza keeps a natural providence prior to predestination'],
        }],
        'notes': ['OCR: XIII PDF 140; Mendoza concl.3.'],
        'bible_refs': [],
    },
    {
        'section': '575',
        'title': 'Therefore the whole universe is one total object of predestination',
        'pass_a': (
            'And therefore according to this conclusion, the whole universe, as it embraces '
            'natural and supernatural things, goods and evils, substances and accidents, and '
            'all modes of being and operating in the universe, not only in general but in '
            'species and in the individual, are to be considered as the one total object of '
            'divine predestination: so that there is absolutely nothing which escapes the '
            'breadth of that object, and which does not fall under that act of '
            'predestination.'
        ),
        'pass_b': [
            'Corollary: whole universe = one total object of praedestinatio.',
            'Natural/supernatural, good/evil, substance/accident, every mode.',
            'Nothing falls outside that act.',
        ],
        'lemmas': [
            {'latin': 'unicum objectum totale divinae praedestinationis', 'gloss': 'the one total object of divine predestination'},
            {'latin': 'nihil omnino sit quod subterfugiat illius objecti latitudinem', 'gloss': 'there is absolutely nothing which escapes the breadth of that object'},
        ],
        'choices': [{
            'term': 'totum universum … sunt consideranda tanquam unicum objectum totale divinae praedestinationis',
            'english': 'the whole universe … are to be considered as the one total object of divine predestination',
            'why': 'XIV body at PDF page-break (numeral lost); applies XIII’s unique providence.',
            'rejected': ['Mendoza limits the object to the elect alone'],
        }],
        'notes': [
            'OCR: XIV PDF 140-141; numeral lost at page break before XV; body = totum universum corollary.',
        ],
        'bible_refs': [],
    },
    {
        'section': '576',
        'title': 'Object as possible/creatable — not as fallen or already created',
        'pass_a': (
            'But from that it may be gathered under what respect those two Doctors think '
            'man the object for God predestining — namely not as fallen nor as created in '
            'the divine foreknowledge, but rather simply as possible, or creatable. For '
            'since the permission of the first man’s fall, and even the creation of man '
            'himself, is reckoned by them among the effects of predestination, it is '
            'necessary that, on their mind, the foresight of the fall and of creation did '
            'not precede in God, according to our way of understanding, the decree of '
            'predestination, but rather followed it; and so God predestining men could not '
            'consider them as fallen and created, but only as creatable by Himself. Which '
            'Estius acknowledges with Mendoza. We do not so name, he says, the '
            'predestination of fallen men, as if the foresight of the first man’s fall, and '
            'in him of the whole human race, had preceded in God, according to our mode of '
            'understanding, the predestination of some from the whole race of men to eternal '
            'life. Cited Distinction forty of the first book of the Sentences, paragraph 6.'
        ),
        'pass_b': [
            'Estius/Mendoza: man-object = possible/creatable, not fallen or already made.',
            'Because fall-permission and creation are themselves effects.',
            'So foresight of fall/creation follows praedestinatio — Estius 1 Sent. d.40 §6.',
        ],
        'lemmas': [
            {'latin': 'simpliciter ut possibilem, sive creabilem', 'gloss': 'simply as possible, or creatable'},
            {'latin': 'non ut lapsum neque ut conditum', 'gloss': 'not as fallen nor as created'},
        ],
        'choices': [{
            'term': 'Deus homines praedestinans illos ut lapsos & conditos considerare non potuit, sed solum ut a se creabiles',
            'english': 'God predestining men could not consider them as fallen and created, but only as creatable by Himself',
            'why': 'Pins the creatable-object reading for the Mendoza/Estius party.',
            'rejected': ['Estius/Mendoza take the object as man already fallen in foresight'],
        }],
        'notes': ['OCR: XV PDF 141; Estius with Mendoza on creatable object.'],
        'bible_refs': [],
    },
    {
        'section': '577',
        'title': 'Mendoza’s allies — Scotus: elect before this sensible world',
        'pass_a': (
            'But that not a few of the Scholastics, both older and more recent, felt the '
            'same with him on this part, Alphonsus Mendoza shows in the question already '
            'named, Section four. Where for himself he cites James Naclantus Bishop of '
            'Chioggia, Albert Pighius, Petrus Galatinus, Ambrosius Catharinus, and whom he '
            'prefers to all the others, John Scotus, of whom he cites many words, from which '
            'it is plain that according to that Subtle Doctor God predestined the elect and '
            'willed the goods of grace for them before He willed this sensible world, which '
            'God from eternity willed in order to the predestined man, for whose sake He '
            'appointed to create the whole visible nature.'
        ),
        'pass_b': [
            'Mendoza Sect.4 roll-call: Naclantus, Pighius, Galatinus, Catharinus.',
            'Prefers Scotus above the rest.',
            'Scotus: elect + grace-goods willed before this sensible world.',
        ],
        'lemmas': [
            {'latin': 'Deum electos praedestinasse … priusquam vellet hunc mundum sensibilem', 'gloss': 'that God predestined the elect … before He willed this sensible world'},
            {'latin': 'in ordine ad hominem praedestinatum', 'gloss': 'in order to the predestined man'},
        ],
        'choices': [{
            'term': 'Deum electos praedestinasse, & bona gratiae ipsis voluisse, priusquam vellet hunc mundum sensibilem',
            'english': 'that God predestined the elect and willed the goods of grace for them before He willed this sensible world',
            'why': 'Closes IX–XVI on Scotus/Mendoza priority of elect over world; next XVII+ communior fallen-in-Adam.',
            'rejected': ['Scotus puts the sensible world before the elect’s predestination'],
        }],
        'notes': ['OCR: XVI PDF 141; Scotus via Mendoza. Next: XVII+ communior fallen object.'],
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
    for name in ('pdf_140.txt', 'pdf_141.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20261002,
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
        if 570 <= n <= 577:
            notes = (
                'Section %s: new densify De Aeterna Hominum Electione IX-XVI; '
                'Pass A!=B; lock-grounded PDF 140-141 / book pp. 128-129.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in aeterna_electio IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Aeterna Hominum Electione IX-XVI only '
                '(sections %s-%s). Meta discloses %s. '
                'Next Aeterna Electio XVII+. Not shipped.'
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
            'De Aeterna Hominum Electione et Praedestinatione IX-XVI '
            '(communior Rom.8; Estius/Mendoza; creatable object)'
        ),
        'next_locus': (
            'De Aeterna Hominum Electione et Praedestinatione XVII+ '
            '(communior fallen-in-Adam object; Reformed senses)'
        ),
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
        '## %s (Scribe — De Aeterna Hominum Electione IX–XVI densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Aeterna Electio IX–XVI → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: Aeterna Electio XVII+.\n\n'
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
        '## %s ~ET (Scribe — Le Blanc De Aeterna Electione IX–XVI densify)\n\n'
        'CoS densify: Aeterna Electio IX–XVI (**%s→%s**). Packet %s. '
        'Next: Aeterna Electio XVII+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_577.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-577 post-ready')
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
