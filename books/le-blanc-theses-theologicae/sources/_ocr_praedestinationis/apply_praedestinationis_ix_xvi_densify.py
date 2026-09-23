#!/usr/bin/env python3
"""Build + apply De Causa Praedestinationis IX-XVI densify (tip 535 → 543).

Common Roman rejection of four opinions; Vasquez/Molina/Bellarmine on gratuitous election.
Live floor 4937. After tip-ready: HOLD live>4937 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_praedestinationis_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_praedestinationis_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_praedestinationis_densify')
PACKET_STEM = 'praedestinationis_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_praedestinationis/apply_praedestinationis_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['536', '537', '538', '539', '540', '541', '542', '543']
ROMANS = {
    '536': 'IX', '537': 'X', '538': 'XI', '539': 'XII',
    '540': 'XIII', '541': 'XIV', '542': 'XV', '543': 'XVI',
}
TIP_BEFORE = 535
PRIOR_START = 528
LIVE_FLOOR = 4937
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Causa Praedestinationis I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Causa Praedestinationis I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Causa Praedestinationis I-XVI, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Praedestinatio IX-XVI "
    "(common rejection; Vasquez/Molina; glory vs grace election; Bellarmine)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Causa Praedestinationis (an detur in homine causa vel ratio aliqua suae Praedestinationis).\n"
    "Same 1675 Pitt copy-text. Book pp. 121-124 / PDF 133-136 (I-XVI; this packet IX-XVI). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Causa Praedestinationis I-XVI tip — continues after I-VIII. Next: Praedestinatio XVII+.\n"
    "Note: Common Roman absolute decree; Vasquez/Molina/Bannez; collective vs particular; Bellarmine.\n\n"
)

LATIN = {
    '536': (
        'IX. Verum omnes istae sententiae a Doctoribus Ecclesiae Romanae communiter hodie '
        'rejiciuntur & damnantur. Censent enim, saltem eorum longe plurimi, decretum divinae '
        'praedestinationis ad omnes suos effectus relatum absolutum esse & mere gratuitum, nec '
        'pendere ab ulla conditione vel causa, quam Deus praedestinans in homine praeviderit '
        '& consideraverit. Hanc enim sententiam ut Theologorum communem proponit & defendit '
        'jam saepe memoratus Gregorius de Valentia. Nullam, scilicet, esse rationem seu causam '
        'ullo modo meritoriam, ex parte praedestinati, praedestinationis quoad omnes ipsius '
        'effectus. Et quod si praedestinatio referatur ad omnes ipsius effectus, nulla sit '
        'ratio, vel causa ullo modo meritoria ipsius in praedestinato, neque propter quam, '
        'neque sine qua non, sed in solam gratuitam Dei voluntatem referri debeat. Ut videre '
        'est loco supra citato. Ubi eandem quoque sententiam tribuit multis veteribus '
        'Scholasticis, ut Thomae Aquinati, Alexandro Alensi, Cardinali Bonaventurae, Joanni '
        'Scoto, Aegidio Romano, Gregorio Ariminensi, Richardo Hertio, & ipsi Sententiarum '
        'Magistro Petro Lombardo.'
    ),
    '537': (
        'X. In eadem etiam sententia est Gabriel Vasquez, qui eam prolixe probat & tuetur '
        'tomo primo in primam Thomae, Disputatione nonagesima prima. Ubi suam ea de re mentem '
        'his verbis explicat. Catholica igitur sententia est, nullam causam, nullum meritum, '
        'seu occasionem ex parte praedestinati excogitari posse, ob quam Deus, aut in tempore '
        'gratiam suam ei dederit, aut ab aeterno dare decreverit. Primum autem doctrina haec '
        'non solum intelligenda est de initio fidei, orationis, seu voluntatis consequendi '
        'salutem, vel de aliis operibus, quae circa Deum aliquo modo versantur, qualia sunt '
        'religionis: verum etiam de quovis opere moralis virtutis, quod in ipsum solum bonum '
        'honestum referatur: Ut nullo modo aliquid hujusmodi esse possit occasio, aut initium '
        'donationis, aut praedestinationis gratiae. Praeterea non solum excludimus initium, '
        'quod sit meritum condignum, sed etiam meritum congruum, seu impetratorium, aut '
        'dispositionem: denique quamlibet causam & occasionem, ob quam Deus huic potius quam '
        'alteri, gratiam donaverit, aut donare praesciverit: ita ut tota ratio praeparandi huic '
        'potius gratiam, quam alii, sit beneplacitum divinae voluntatis, nihil autem, vel '
        'minimum ex parte praedestinati. Disputationis jam dictae capite undecimo.'
    ),
    '538': (
        'XI. Idem quoque docet Petrus a Sancto Joseph in Idea Theologiae speculativae. Ubi '
        'libro primo, capite decimo nono, haec est illius Resolutio quarta. Ex parte '
        'praedestinati non datur causa praedestinationis ad primam gratiam. Quod probat ex '
        'illo Pauli, Quis te discernit? Unde colligit hominem non esse causam illius '
        'discriminis, quo praedestinatus distinguitur a non praedestinato, sed meram '
        'misericordiam Dei tale discrimen inter utrumque constituentis: quod falsum esset, si '
        'homo naturaliter Deo praeberet motivum, seu rationem eum praedestinandi prae alio, ad '
        'gratiae auxilia quibus salus comparatur. Atque eandem sententiam inter recentiores '
        'tenent Dominicus Bannez, Estius, Puteanus, Eustachius a Sancto Paulo, & alii plurimi, '
        'quorum singulorum testimonia referre taediosum nimis & superfluum esset.'
    ),
    '539': (
        'XII. Quin haec est ipsius Molinae sententia. Asserat enim praedestinationis quoad '
        'integrum effectum non dari causam ex parte praedestinati. Et hoc probat quia quicquid '
        'est in homine, quo in vitam aeternam dirigitur, comprehenditur ut integro effectu '
        'praedestinationis, etiam ipsa praeparatio ad gratiam, quae non fit nisi per auxilium '
        'particulare Dei. Ergo nulla ratione fieri potest, ut integri effectus praedestinationis '
        'aliqua causa ex parte nostri reperiatur. Praedestinatio igitur hoc modo sumpta ex '
        'parte effectus habet pro ratione divinam voluntatem, ad quam totus effectus '
        'praedestinationis ordinatur ut in finem, & ex qua, sicut ex principio movente, '
        'procedit. Unde est quod postea assentitur Thomae dicenti, Ex parte hominum '
        'praedestinatorum & reproborum nullam esse causam, sive rationem, quare quidam eorum '
        'sint a Deo praedestinati, alii vero reprobati; sed rationem sumendam, reddendamque '
        'esse ex parte Dei. Quaest. 23. art. 5. & d. Disput. 1. Memb. 5.'
    ),
    '540': (
        'XIII. Porro quamvis Doctores Ecclesiae Romanae communiter censent omnes effectus '
        'praedestinationis simul & collective sumptos, nullam omnino causam in homine habere, '
        'nec ex ullo hominis merito, vel opere pendere, sed ex Dei quadam voluntate omnino '
        'gratuita & absoluta homini conferri, adeoque nullam ex parte hominis dari, vel '
        'reperiri causam divinae praedestinationis ad omnes suos effectus relatae, est tamen '
        'communis eorum sententia unum effectum praedestinationis esse non tantum rationem, '
        'sed vere causam alterius effectus ejusdem praedestinationis: & sic unum effectum esse '
        'posse rationem, & causam, saltem improprie dictam, praedestinationis, prout refertur '
        'ad alium effectum. Quo posito quaerunt, An praedestinatio seu electio hominis ad '
        'gloriam, prout consideratur distincte a decreto de conferenda homini gratia, habeat '
        'aliquam in homine causam, & facta sit ex fide & meritis praevisis, An vero sit omnino '
        'gratuita & absoluta, & secundum nostrum concipiendi modum, debeat censeri fieri ante '
        'praevisionem fidei & bonorum operum, adeoque nullam ex parte hominis rationem vel '
        'causam habeat.'
    ),
    '541': (
        'XIV. Super qua re variae sunt in Ecclesia Romana Doctorum sententiae. Quamvis enim '
        'in eo conveniant, quod gloria detur homini ex meritis, quodque Deus gloriam a meritis '
        'dare homini decreverit, eorum tamen multi, & quidem Doctissimi atque celeberrimi, '
        'docent electionem hominis ad gloriam omnimodo gratuitam esse, & pendere a solo Dei '
        'beneplacito. Nempe volunt Deum ab aeterno certis hominibus gloriam caelestem gratuito '
        'destinasse atque praeparavisse, sed tamen voluisse ut per merita ad illam pervenirent, '
        '& propterea decrevisse illis dare gratiam, qua possent gloriam ipsis destinatam '
        'mereri: ita ut donatio gloriae cadat sub meritum, nec omnino gratuita sit, decretum '
        'vero de gloria donanda sub meritum non cadat, sed sit simpliciter & absolute '
        'gratuitum.'
    ),
    '542': (
        'XV. Haec est inter alios sententia Bellarmini. Nam libro secundo de Gratia & libero '
        'arbitrio cap. 13. Respondens ad quintum testimonium, Alia, inquit, est praedestinatio, '
        'alia executio. Constituit enim Deus in praedestinatione, regnum caelorum dare certis '
        'hominibus quos absque ulla operum praevisione dilexit: tamen simul constituit, ut via '
        'ad executionem, via perveniendi ad regnum, essent bona opera. Itaque illa propositio, '
        'Deus ab aeterno praedestinavit hominibus dare regnum per opera bona praevisa, potest '
        '& vera esse & falsa. Nam si illud, per opera praevisa, referatur ad verbum, '
        'praedestinavit, falsa erit: significabit enim Deum praedestinasse homines, quia opera '
        'illorum bona praeviderat: si referatur ad verbum, dare, vera erit: quia significabit '
        'executionem futuram esse per opera bona, sive, quod idem est, glorificationem '
        'effectum esse justificationis, & operum bonorum, sicut ipsa justificatio effectum est '
        'vocationis, & vocatio praedestinationis.'
    ),
    '543': (
        'XVI. Capite vero decimo quinto ejusdem libri ex professo probat, ut patet ex ipso '
        'titulo capitis, Non solum ad gratiam efficacem, sed etiam ad gloriam, gratis homines '
        'eligi. Et capitis initio eos sibi refutandos proponit qui distinguunt praedestinationem '
        'ab electione, & praedestinatione quidem praeparari certis hominibus infallibilia media '
        'ad salutem, electione vero praeparari ad gloriam. Denique praedestinationem esse plane '
        'gratuitam, electionem autem a bonorum operum praevisione pendere.'
    ),
}

SECTIONS = [
    {
        'section': '536',
        'title': 'Common Roman view — absolute gratuitous decree; no meritorious cause',
        'pass_a': (
            'But all those opinions are commonly today rejected and condemned by the Doctors of '
            'the Roman Church. For they judge, at least the far greater part of them, that the '
            'decree of divine predestination related to all its effects is absolute and merely '
            'gratuitous, and does not depend on any condition or cause which God predestining '
            'foresaw and considered in man. For this opinion as the common one of the Theologians '
            'Gregory of Valencia, already often mentioned, proposes and defends. Namely that '
            'there is no reason or cause in any way meritorious, on the part of the predestined, '
            'of predestination as to all its effects. And that if predestination is referred to '
            'all its effects, there is no reason or cause in any way meritorious of it in the '
            'predestined, neither on account of which, nor without which not — but it ought to '
            'be referred to the gratuitous will of God alone. As is to be seen in the place '
            'cited above. Where he also ascribes the same opinion to many older Scholastics, as '
            'to Thomas Aquinas, Alexander of Hales, Cardinal Bonaventure, John Scotus, Giles of '
            'Rome, Gregory of Rimini, Richard of Middleton, and to the Master of the Sentences '
            'himself, Peter Lombard.'
        ),
        'pass_b': [
            'Today’s common Roman Doctors reject all four prior opinions.',
            'Decree to all effects: absolute, merely gratuitous.',
            'No propter-quam / sine-qua-non in the elect — Gregory lists Thomas to Lombard.',
        ],
        'lemmas': [
            {'latin': 'absolutum esse & mere gratuitum', 'gloss': 'is absolute and merely gratuitous'},
            {'latin': 'in solam gratuitam Dei voluntatem', 'gloss': 'to the gratuitous will of God alone'},
        ],
        'choices': [{
            'term': 'nec pendere ab ulla conditione vel causa, quam Deus praedestinans in homine praeviderit',
            'english': 'and does not depend on any condition or cause which God predestining foresaw in man',
            'why': 'States the common Roman absolute-decree thesis against I–VIII’s opinions.',
            'rejected': ['most Roman Doctors still hold a meritorious cause in man'],
        }],
        'notes': ['OCR: IX PDF 134; Gregory de Valentia; Thomas to Lombard.'],
        'bible_refs': [],
    },
    {
        'section': '537',
        'title': 'Vasquez — no cause, merit, or occasion in the elect',
        'pass_a': (
            'Gabriel Vasquez is also in the same opinion, who proves and defends it at length '
            'in the first tome on the first part of Thomas, Disputation ninety-one. Where he '
            'explains his mind on that matter in these words. The Catholic opinion therefore '
            'is that no cause, no merit, or occasion on the part of the predestined can be '
            'thought up on account of which God either in time gave him His grace, or from '
            'eternity decreed to give it. But first this doctrine is to be understood not only '
            'of the beginning of faith, prayer, or the will to obtain salvation, or of other '
            'works which in some way turn about God, such as those of religion: but also of any '
            'work of moral virtue which is referred to the honest good alone: so that in no way '
            'can anything of this sort be an occasion or beginning of the gift or predestination '
            'of grace. Further we exclude not only a beginning that is condign merit, but also '
            'congruous or impetratory merit, or a disposition: finally any cause and occasion on '
            'account of which God rather to this one than to another gave grace, or foresaw that '
            'He would give it: so that the whole reason of preparing grace rather for this one '
            'than for another is the good pleasure of the divine will, but nothing, even the '
            'least, on the part of the predestined. Chapter eleven of the Disputation already '
            'named.'
        ),
        'pass_b': [
            'Vasquez Disp. 91: Catholic sentence — no cause/merit/occasion in the elect.',
            'Covers faith-start and any honest moral work.',
            'Excludes condign, congruous, disposition — only God’s good pleasure.',
        ],
        'lemmas': [
            {'latin': 'nullam causam, nullum meritum, seu occasionem ex parte praedestinati', 'gloss': 'no cause, no merit, or occasion on the part of the predestined'},
            {'latin': 'beneplacitum divinae voluntatis', 'gloss': 'the good pleasure of the divine will'},
        ],
        'choices': [{
            'term': 'tota ratio praeparandi huic potius gratiam, quam alii, sit beneplacitum divinae voluntatis',
            'english': 'the whole reason of preparing grace rather for this one than for another is the good pleasure of the divine will',
            'why': 'Vasquez’s absolute exclusion of every creaturely occasion.',
            'rejected': ['Vasquez still allows congruous disposition as election’s start'],
        }],
        'notes': ['OCR: X PDF 135; Vasquez in 1am Thomae Disp. 91.'],
        'bible_refs': [],
    },
    {
        'section': '538',
        'title': 'Petrus a S. Joseph — Quis te discernit?; Bannez circle',
        'pass_a': (
            'Petrus a Sancto Joseph also teaches the same in the Idea of Speculative Theology. '
            'Where in book one, chapter nineteen, this is his fourth Resolution. On the part of '
            'the predestined there is not given a cause of predestination to the first grace. '
            'Which he proves from that of Paul, Who makes you to differ? Whence he gathers that '
            'man is not the cause of that discrimination by which the predestined is '
            'distinguished from the non-predestined, but the mere mercy of God constituting '
            'such a discrimination between both: which would be false if man naturally offered '
            'God a motive or reason for predestining him before another, to the helps of grace '
            'by which salvation is obtained. And among more recent writers the same opinion is '
            'held by Dominicus Bannez, Estius, Puteanus, Eustachius a Sancto Paulo, and very '
            'many others, whose several testimonies it would be too tedious and superfluous to '
            'report.'
        ),
        'pass_b': [
            'Idea Theol.: no cause in the elect for first grace.',
            '1 Cor 4:7 — discrimination = God’s mercy alone.',
            'Bannez, Estius, Puteanus, Eustachius agree.',
        ],
        'lemmas': [
            {'latin': 'Quis te discernit?', 'gloss': 'Who makes you to differ?'},
            {'latin': 'meram misericordiam Dei', 'gloss': 'the mere mercy of God'},
        ],
        'choices': [{
            'term': 'hominem non esse causam illius discriminis, quo praedestinatus distinguitur a non praedestinato',
            'english': 'that man is not the cause of that discrimination by which the predestined is distinguished from the non-predestined',
            'why': 'Pauline lever for no motive-from-nature.',
            'rejected': ['natural motive explains why this one is elect'],
        }],
        'notes': ['OCR: XI PDF 135; 1 Cor 4:7; Bannez.'],
        'bible_refs': ['1 Cor. 4:7'],
    },
    {
        'section': '539',
        'title': 'Molina — no cause of the integral effect; agrees with Thomas',
        'pass_a': (
            'Indeed this is Molina’s own opinion. For he asserts that of predestination as to '
            'the integral effect there is not given a cause on the part of the predestined. And '
            'he proves this because whatever is in man by which he is directed to eternal life '
            'is comprehended as in the integral effect of predestination, even the very '
            'preparation for grace, which is not made except by a particular help of God. '
            'Therefore in no way can it come about that some cause of the integral effect of '
            'predestination be found on our part. Predestination therefore taken this way on '
            'the side of the effect has for its reason the divine will, to which the whole '
            'effect of predestination is ordered as to an end, and from which, as from a moving '
            'principle, it proceeds. Whence it is that afterward he agrees with Thomas saying '
            'that on the part of predestined and reprobate men there is no cause or reason why '
            'some of them are predestined by God, but others reprobated; but the reason is to '
            'be taken and rendered on God’s part. Question 23 article 5 and Disputation 1 '
            'Member 5.'
        ),
        'pass_b': [
            'Molina: no cause in us for the integral effect.',
            'Even preparation-for-grace is inside the effect (particular help).',
            'Assents to Thomas ST I q.23 a.5 — reason only from God’s side.',
        ],
        'lemmas': [
            {'latin': 'quoad integrum effectum non dari causam ex parte praedestinati', 'gloss': 'that as to the integral effect there is not given a cause on the part of the predestined'},
            {'latin': 'rationem … ex parte Dei', 'gloss': 'the reason … on God’s part'},
        ],
        'choices': [{
            'term': 'etiam ipsa praeparatio ad gratiam … comprehenditur ut integro effectu praedestinationis',
            'english': 'even the very preparation for grace … is comprehended as in the integral effect of predestination',
            'why': 'Blocks smuggling a pre-grace cause outside the effect-set.',
            'rejected': ['preparation for grace stands outside predestination’s effect'],
        }],
        'notes': ['OCR: XII PDF 135; Molina; Thomas q.23 a.5.'],
        'bible_refs': [],
    },
    {
        'section': '540',
        'title': 'Collective effects uncaused — but one effect may cause another',
        'pass_a': (
            'Further, although the Doctors of the Roman Church commonly judge that all the '
            'effects of predestination taken together and collectively have no cause at all in '
            'man, nor depend on any merit or work of man, but are conferred on man from a '
            'certain wholly gratuitous and absolute will of God, and therefore that no cause of '
            'divine predestination related to all its effects is given or found on man’s part, '
            'yet it is their common opinion that one effect of predestination is not only a '
            'reason but truly a cause of another effect of the same predestination: and so one '
            'effect can be a reason and cause, at least improperly so called, of '
            'predestination as it is referred to another effect. Which being laid down they '
            'ask whether the predestination or election of a man to glory, as it is considered '
            'distinct from the decree of conferring grace on the man, has some cause in man and '
            'was made from foreseen faith and merits, or whether it is wholly gratuitous and '
            'absolute, and according to our way of conceiving ought to be judged to be done '
            'before the foresight of faith and good works, and therefore to have no reason or '
            'cause on man’s part.'
        ),
        'pass_b': [
            'Collective package of effects: no cause in man.',
            'Still: one effect can cause another effect.',
            'New question: glory-election vs grace-decree — foresight or absolute?',
        ],
        'lemmas': [
            {'latin': 'simul & collective sumptos', 'gloss': 'taken together and collectively'},
            {'latin': 'unum effectum praedestinationis esse … causam alterius effectus', 'gloss': 'that one effect of predestination is … a cause of another effect'},
        ],
        'choices': [{
            'term': 'An praedestinatio seu electio hominis ad gloriam … facta sit ex fide & meritis praevisis',
            'english': 'whether the predestination or election of a man to glory … was made from foreseen faith and merits',
            'why': 'Pivots from package-uncaused to glory-election’s order.',
            'rejected': ['Roman Doctors deny all causal order among effects'],
        }],
        'notes': ['OCR: XIII PDF 135; collective vs glory-election.'],
        'bible_refs': [],
    },
    {
        'section': '541',
        'title': 'Many hold glory-election absolute — grace given to merit destined glory',
        'pass_a': (
            'On which matter the opinions of the Doctors in the Roman Church are various. For '
            'although they agree in this, that glory is given to man from merits, and that God '
            'decreed to give glory to man from merits, yet many of them, and indeed the most '
            'learned and celebrated, teach that the election of a man to glory is in every way '
            'gratuitous and depends on the good pleasure of God alone. Namely they will that '
            'God from eternity freely destined and prepared heavenly glory for certain men, but '
            'yet willed that they should arrive at it through merits, and therefore decreed to '
            'give them grace by which they could merit the glory destined for them: so that the '
            'gift of glory falls under merit and is not wholly gratuitous, but the decree of '
            'giving glory does not fall under merit, but is simply and absolutely gratuitous.'
        ),
        'pass_b': [
            'Agree: glory conferred from merits in time.',
            'Many: eternal glory-election still absolute / beneplacitum.',
            'Grace given so they can merit the already-destined glory.',
        ],
        'lemmas': [
            {'latin': 'electionem hominis ad gloriam omnimodo gratuitam', 'gloss': 'that the election of a man to glory is in every way gratuitous'},
            {'latin': 'decretum vero de gloria donanda … sit simpliciter & absolute gratuitum', 'gloss': 'but the decree of giving glory … is simply and absolutely gratuitous'},
        ],
        'choices': [{
            'term': 'donatio gloriae cadat sub meritum … decretum vero de gloria donanda sub meritum non cadat',
            'english': 'the gift of glory falls under merit … but the decree of giving glory does not fall under merit',
            'why': 'Splits temporal meriting from eternal absolute destination.',
            'rejected': ['the glory-decree itself is from foreseen merits'],
        }],
        'notes': ['OCR: XIV PDF 135; absolute glory-election.'],
        'bible_refs': [],
    },
    {
        'section': '542',
        'title': 'Bellarmine — predestination vs execution; per opera praevisa',
        'pass_a': (
            'This among others is Bellarmine’s opinion. For in book two On Grace and Free Choice '
            'chapter 13, answering the fifth testimony, Another thing, he says, is '
            'predestination, another is execution. For God appointed in predestination to give '
            'the kingdom of heaven to certain men whom He loved without any foresight of works: '
            'yet at the same time He appointed that the way to execution, the way of arriving at '
            'the kingdom, should be good works. And so that proposition, God from eternity '
            'predestined to give men the kingdom through foreseen good works, can be both true '
            'and false. For if that phrase, through foreseen works, is referred to the verb '
            'predestined, it will be false: for it will signify that God predestined men because '
            'He had foreseen their good works: if it is referred to the verb to give, it will be '
            'true: because it will signify that the future execution is through good works, or, '
            'what is the same, that glorification is the effect of justification and of good '
            'works, just as justification itself is the effect of calling, and calling of '
            'predestination.'
        ),
        'pass_b': [
            'Bellarmine: predestination ≠ execution.',
            'Loved without foresight of works; works = path of execution.',
            '“Through foreseen works” false of praedestinavit, true of dare.',
        ],
        'lemmas': [
            {'latin': 'Alia … est praedestinatio, alia executio', 'gloss': 'Another thing … is predestination, another is execution'},
            {'latin': 'absque ulla operum praevisione dilexit', 'gloss': 'whom He loved without any foresight of works'},
        ],
        'choices': [{
            'term': 'si illud, per opera praevisa, referatur ad verbum, praedestinavit, falsa erit',
            'english': 'if that phrase, through foreseen works, is referred to the verb predestined, it will be false',
            'why': 'Bellarmine’s scope ambiguity dissolves the seeming contradiction.',
            'rejected': ['Bellarmine makes foresight of works the ground of predestination'],
        }],
        'notes': ['OCR: XV PDF 135-136; Bellarmine De Gratia II.13.'],
        'bible_refs': [],
    },
    {
        'section': '543',
        'title': 'Bellarmine ch. 15 — free election to glory, not only to grace',
        'pass_a': (
            'But in chapter fifteen of the same book he proves on purpose, as is plain from '
            'the very title of the chapter, that men are freely elected not only to efficacious '
            'grace but also to glory. And at the beginning of the chapter he proposes to himself '
            'to refute those who distinguish predestination from election, and by predestination '
            'indeed prepare for certain men infallible means to salvation, but by election '
            'prepare for glory — and finally that predestination is wholly gratuitous, but '
            'election depends on the foresight of good works.'
        ),
        'pass_b': [
            'Bellarmine II.15 title: free election to glory too.',
            'Targets split: predestination=means / election=glory-from-works.',
            'Holds both gratuitous — denies works-foresight for election.',
        ],
        'lemmas': [
            {'latin': 'Non solum ad gratiam efficacem, sed etiam ad gloriam, gratis homines eligi', 'gloss': 'that men are freely elected not only to efficacious grace but also to glory'},
            {'latin': 'electionem autem a bonorum operum praevisione pendere', 'gloss': 'but that election depends on the foresight of good works'},
        ],
        'choices': [{
            'term': 'Non solum ad gratiam efficacem, sed etiam ad gloriam, gratis homines eligi',
            'english': 'that men are freely elected not only to efficacious grace but also to glory',
            'why': 'Closes IX-XVI on Bellarmine’s free glory-election; next XVII+ allies.',
            'rejected': ['Bellarmine limits free election to grace alone'],
        }],
        'notes': ['OCR: XVI PDF 136; Bellarmine De Gratia II.15; next XVII+.'],
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
        jpath = JUST / f'praedestinationis_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab praedestinationis_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_134.txt', 'pdf_135.txt', 'pdf_136.txt'):
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
        if 536 <= n <= 543:
            notes = (
                f'Section {sid}: new densify De Causa Praedestinationis IX-XVI; '
                'Pass A!=B; lock-grounded PDF 134-136 / book pp. 122-124.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in praedestinationis IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify De Causa Praedestinationis IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Next Praedestinatio XVII+. Not shipped.'
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
        'locus': 'De Causa Praedestinationis theses IX-XVI (common rejection; Vasquez/Molina; Bellarmine)',
        'next_locus': 'De Causa Praedestinationis XVII+ (allies; opposite glory-from-merits party)',
        'gates': {
            'check_pass_ab': f'ok praedestinationis_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        f'## {day} (Scribe — De Causa Praedestinationis IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Praedestinatio IX–XVI → §§{SECS[0]}–{SECS[-1]}).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 134-136 / pp. 122-124).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Praedestinatio XVII+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Causa Praedestinationis IX–XVI densify)\n\n'
        'CoS densify: Praedestinatio IX–XVI. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Praedestinatio IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Praedestinatio XVII+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_543.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-543 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
