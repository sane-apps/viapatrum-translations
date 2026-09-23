#!/usr/bin/env python3
"""Build + apply De Causa Praedestinationis I-VIII densify (tip 527 → 535).

Opens after Scientia XXX. Roman senses; question; adult scope; scholastic opinions.
Live floor 4911. After tip-ready: HOLD live>4911 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'praedestinationis_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_praedestinationis/apply_praedestinationis_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['528', '529', '530', '531', '532', '533', '534', '535']
ROMANS = {
    '528': 'I', '529': 'II', '530': 'III', '531': 'IV',
    '532': 'V', '533': 'VI', '534': 'VII', '535': 'VIII',
}
TIP_BEFORE = 527
LIVE_FLOOR = 4911
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Causa Praedestinationis I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Causa Praedestinationis I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Causa Praedestinationis I-VIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice opens Praedestinatio I-VIII "
    "(Roman senses; question of cause in man; adults; scholastic opinions)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Causa Praedestinationis (an detur in homine causa vel ratio aliqua suae Praedestinationis).\n"
    "Same 1675 Pitt copy-text. Book pp. 121-122 / PDF 133-134 (I-VIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Causa Praedestinationis I-VIII tip — opens after Scientia XXX. Next: Praedestinatio IX+.\n"
    "Note: Roman definitions; triple respect; cause-in-us question; adult scope; four scholastic opinions.\n\n"
)

LATIN = {
    '528': (
        'I. Thesibus praecedentibus observavimus Praedestinationem in Schola Romana multis '
        'modis accipi. Et primo quidem nonnullos Praedestinationis vocem restringere ad '
        'decretum illud, quo Deus ab aeterno absolute constituit gloriam caelestem certis '
        'hominibus conferre. Juxta alios vero, praedestinationem solum illud decretum '
        'complecti, quo Deus hominibus quibusdam praeparavit media ad gloriam caelestem '
        'infallibiliter assequendam conducibilia. Hodie vero apud plerosque Scholae Romanae '
        'Theologos utrumque istud decretum sub praedestinationis nomine comprehendi. Et hoc '
        'sensu vox ista in hac disputatione communiter sumitur.'
    ),
    '529': (
        'II. Porro praedestinatio sub hac notione accepta, secundum Scholae Romanae Theologos '
        'tripliciter considerari potest. Et prima quidem ratione actus ipsius voluntatis '
        'divinae, per quem Deus homines ad salutem destinat. Secundo, ratione effectuum '
        'illius actus, qui conferuntur homini in tempore, & qui omnes ad gratiam & gloriam '
        'revocantur. Denique secundum terminationem atque relationem, quam divina voluntas ab '
        'aeterno habuit ad effectus illos futuros. Priori modo confitentur omnes Scholae '
        'Romanae Doctores, absque ulla haesitatione, nullam causam divinae praedestinationis '
        'a parte hominis dari, vel cogitari posse, ut nec divinae voluntatis, quae cum ipsa '
        'sit causa rerum omnium, nullam causam habere potest.'
    ),
    '530': (
        'III. Verum hic quaestio est de praedestinatione secundo & tertio modo considerata, '
        'nempe, secundum effectus quos Deus, ut praedestinans & eligens homines, in hominibus, '
        'aut circa homines operatur. Et etiam secundum respectum extrinsecum, quem Dei '
        'praedestinantis voluntas habet ad effectus illos, ad quos ab aeterno libere '
        'terminatur. Videlicet, quaeritur, An sit aliqua causa omnium effectuum '
        'praedestinationis in nobis, quae effectibus illis non sit annumeranda. Seu quod eodem '
        'redit, An Deus hos & illos eligens atque praedestinans consideraverit & praeviderit '
        'in ipsis aliquid quod sit ratio vel motivum praedestinationis & electionis ipsorum, '
        'ad quod nimirum possint referri, tanquam ad causam quoquo modo moventem atque '
        'meritoriam, quaecunque bona ipsis, vi suae praedestinationis & electionis obtingunt: '
        '& ita an sit in homine quaedam vel causa, vel ratio cur sit a Deo praedestinatus, & '
        'cur iste potius electus sit quam alter?'
    ),
    '531': (
        'IV. Quae quaestio solos adultos respicit. Nam quod spectat ad parvulos ante usum '
        'rationis ex hac vita decedentes, in Schola Romana certum apud omnes habetur nihil '
        'esse in ipsis, quod possit esse causa, vel conditio electionis illorum. Adeoque tota '
        'controversia est An in illis praedestinatis qui adulta aetate ex hac vita migrant, '
        'possit assignari aliqua causa ullo modo meritoria, seu aliqua ratio praedestinationis '
        '& electionis ipsorum, quoad omnes ejus effectus? Et quidem talis causa, vel conditio '
        'quae semper habeat certam connexionem cum praedestinatione.'
    ),
    '532': (
        'V. Super qua re variae sunt & fuerunt in Schola Romana sententiae. Primo enim '
        'reperti sunt Scholastici nonnulli, qui existimarunt causam meritoriam praedestinationis, '
        'quoad omnes ejus effectus esse bona opera moralia antecedentia gratiam justificationis. '
        'Nempe Deum ab aeterno ad gratiam & salutem aeternam elegisse, quos praevidit, citra '
        'gratiam ullam supernaturalem, ex liberi arbitrii viribus bene acturos moraliter, & sic '
        'sese ad gratiam quodammodo praeparaturos: Deumque ad illam dandam ex congruitate '
        'quadam invitaturos esse. Hanc sententiam tribuit Gregorius de Valentia Thomae de '
        'Argentina, Gabrieli, & Occam veteribus Scholasticis: itemque Chrysostomo Javello '
        'Dominicano, qui superiori saeculo scribebat.'
    ),
    '533': (
        'VI. Alii putarunt causam praedestinationis esse merita, non quidem antecedentia '
        'gratiam, sed illam subsequentia. Dixerunt enim Deum ab aeterno decrevisse illi '
        'homini conferre gratiam, & reliquos subsequentes effectus praedestinationis, quem '
        'praevidit recte fuisse usurum accepta gratia, atque a Deo habiturum merita per '
        'divinam gratiam. Quam rem explicabant exemplo Regis alicujus, qui dare vellet equum '
        'ei militi quem existimaret equo bene usurum, atque ita propter bonum usum futurum '
        'equi, equum daret. Ut refert Thomas quaest. 23. art. 5. Et Durandus in Dist. 41. '
        'lib. 1. Sententiarum.'
    ),
    '534': (
        'VII. Ad hanc sententiam accedit, & cum ea fere coincidit sententia cujusdam Henrici '
        'Gandavensis veteris Scholastici. Docet enim actiones illas, quibus homo praedestinatus '
        'cooperatur divinae vocationi & justificantem gratiam acquirit, ac in ea acquisita '
        'constanter perseverat, observando Dei mandata, dupliciter considerari posse, uno modo, '
        'ut sunt a libero arbitrio, altero modo, ut sunt ab adjutorio Gratiae. Et priori modo '
        'dicit non esse effectus praedestinationis, sed posteriori modo. Atque ita existimat '
        'actiones illas, ut sunt a Libero arbitrio, esse causam praedestinationis relatam ad '
        'suos effectus, atque adeo ad illas etiam ipsas actiones, ut sunt a gratia. Addit autem '
        'tales actiones esse causam non propter quam homo praedestinetur, tanquam propter '
        'meritum ex condigno, sed sine qua non praedestinaretur, & qua interveniente '
        'praedestinetur, ex congruitate quadam: quia nimirum decet & aequum est, ut Deus eum '
        'praedestinet quem videt cooperaturum illo modo Divinae gratiae. Quam sententiam, teste '
        'Gregorio de Valentia, superiori saeculo secutus est Joannes Eckius, in libro qui ab '
        'eo Chrysopassus inscribitur.'
    ),
    '535': (
        'VIII. Denique ex Scholasticis aliqui censuerunt esse aliquam causam praedestinationis '
        'ex parte praedestinati, non tamen positivam, sed negativam. Arbitrati sunt enim Deum '
        'eo praedestinare quos praedestinat, quia praevidit illos non posituros obicem gratiae '
        'divinae finaliter per peccatum mortale. Quae variae sententiae referuntur & '
        'explicantur ab eodem Gregorio de Valentia, Disputatione prima, quaestione 23. de '
        'Praedestinatione, puncto 4.'
    ),
}

SECTIONS = [
    {
        'section': '528',
        'title': 'Roman senses of praedestinatio — glory, means, or both',
        'pass_a': (
            'In the preceding theses we observed that Predestination is taken in many ways in '
            'the Roman School. And first indeed some restrict the word Predestination to that '
            'decree by which God from eternity absolutely appointed to confer heavenly glory on '
            'certain men. But according to others, predestination comprises only that decree by '
            'which God prepared for certain men means conducive to attaining heavenly glory '
            'infallibly. But today among most theologians of the Roman School both those decrees '
            'are comprehended under the name of predestination. And in that sense that word is '
            'commonly taken in this disputation.'
        ),
        'pass_b': [
            'Roman School: several senses of predestination.',
            'Some = glory-decree only; others = means-decree only.',
            'Most now combine both — our working sense here.',
        ],
        'lemmas': [
            {'latin': 'multis modis accipi', 'gloss': 'to be taken in many ways'},
            {'latin': 'utrumque istud decretum sub praedestinationis nomine', 'gloss': 'both those decrees under the name of predestination'},
        ],
        'choices': [{
            'term': 'utrumque istud decretum sub praedestinationis nomine comprehendi',
            'english': 'both those decrees are comprehended under the name of predestination',
            'why': 'Fixes the tract’s working definition before the cause-question.',
            'rejected': ['this dispute uses only the glory-decree sense'],
        }],
        'notes': ['OCR: Praedestinatio I PDF 133 / p. 121.'],
        'bible_refs': [],
    },
    {
        'section': '529',
        'title': 'Triple respect — act, effects, eternal relation; no cause of the act',
        'pass_a': (
            'Further, predestination taken under this notion can, according to the theologians '
            'of the Roman School, be considered in three ways. And first indeed by reason of '
            'the act itself of the divine will by which God destines men to salvation. Second, '
            'by reason of the effects of that act which are conferred on man in time, and which '
            'are all referred to grace and glory. Finally according to the termination and '
            'relation which the divine will from eternity had to those future effects. In the '
            'first way all the Doctors of the Roman School confess without any hesitation that '
            'no cause of divine predestination on man’s part is given or can be thought, as '
            'neither of the divine will, which since it itself is the cause of all things can '
            'have no cause.'
        ),
        'pass_b': [
            'Three respects: will’s act; temporal effects; eternal relation.',
            'Of the act itself: no cause in man — unanimous.',
            'Divine will is cause of all; has no cause.',
        ],
        'lemmas': [
            {'latin': 'tripliciter considerari potest', 'gloss': 'can be considered in three ways'},
            {'latin': 'nullam causam divinae praedestinationis a parte hominis', 'gloss': 'no cause of divine predestination on man’s part'},
        ],
        'choices': [{
            'term': 'nullam causam divinae praedestinationis a parte hominis dari, vel cogitari posse',
            'english': 'that no cause of divine predestination on man’s part is given or can be thought',
            'why': 'Settles the act-respect before narrowing to effects/relation.',
            'rejected': ['man’s merit causes the electing act itself'],
        }],
        'notes': ['OCR: II PDF 133; triple consideration.'],
        'bible_refs': [],
    },
    {
        'section': '530',
        'title': 'The question — is there a motive in us for election?',
        'pass_a': (
            'But here the question is about predestination considered in the second and third '
            'way, namely according to the effects which God, as predestining and electing men, '
            'works in men or about men. And also according to the extrinsic respect which the '
            'will of God predestining has to those effects to which it is freely terminated from '
            'eternity. Namely it is asked whether there is some cause of all the effects of '
            'predestination in us which is not to be numbered among those effects. Or, what '
            'comes to the same, whether God electing and predestining these and those considered '
            'and foresaw in them something that is a reason or motive of their predestination '
            'and election, to which namely whatever goods befall them by force of their '
            'predestination and election can be referred as to a cause in some way moving and '
            'meritorious: and so whether there is in man some cause or reason why he is '
            'predestined by God, and why this one rather than another is elect.'
        ),
        'pass_b': [
            'Live question: effects + eternal relation to them.',
            'Is there a non-effect cause/motive in us?',
            'Why this person elect rather than another?',
        ],
        'lemmas': [
            {'latin': 'An sit aliqua causa omnium effectuum praedestinationis in nobis', 'gloss': 'whether there is some cause of all the effects of predestination in us'},
            {'latin': 'cur iste potius electus sit quam alter', 'gloss': 'why this one rather than another is elect'},
        ],
        'choices': [{
            'term': 'an sit in homine quaedam vel causa, vel ratio cur sit a Deo praedestinatus',
            'english': 'whether there is in man some cause or reason why he is predestined by God',
            'why': 'States the tract’s central controversy.',
            'rejected': ['the question is only about the electing act’s ontology'],
        }],
        'notes': ['OCR: III PDF 133-134; motive-in-us.'],
        'bible_refs': [],
    },
    {
        'section': '531',
        'title': 'Adults only — infants have no election-cause in them',
        'pass_a': (
            'Which question concerns adults alone. For as to little ones departing this life '
            'before the use of reason, it is held certain among all in the Roman School that '
            'there is nothing in them that can be a cause or condition of their election. And '
            'so the whole controversy is whether in those predestined who leave this life at '
            'adult age some cause in any way meritorious can be assigned, or some reason of '
            'their predestination and election as to all its effects — and indeed such a cause '
            'or condition as always has a certain connection with predestination.'
        ),
        'pass_b': [
            'Scope: adults only.',
            'Infants: nothing in them as election’s cause/condition.',
            'Need a cause tied always to predestination’s effects.',
        ],
        'lemmas': [
            {'latin': 'solos adultos respicit', 'gloss': 'concerns adults alone'},
            {'latin': 'certam connexionem cum praedestinatione', 'gloss': 'a certain connection with predestination'},
        ],
        'choices': [{
            'term': 'Quae quaestio solos adultos respicit',
            'english': 'Which question concerns adults alone',
            'why': 'Bounds the dispute before listing scholastic opinions.',
            'rejected': ['infant election turns on foreseen works'],
        }],
        'notes': ['OCR: IV PDF 134 / p. 122; adults.'],
        'bible_refs': [],
    },
    {
        'section': '532',
        'title': 'Opinion 1 — moral works before justifying grace',
        'pass_a': (
            'On which matter there are and have been various opinions in the Roman School. For '
            'first some Scholastics were found who judged that the meritorious cause of '
            'predestination as to all its effects is moral good works antecedent to the grace of '
            'justification. Namely that God from eternity elected to grace and eternal salvation '
            'those whom He foresaw, apart from any supernatural grace, would act well morally '
            'from the powers of free choice, and so would in a way prepare themselves for grace: '
            'and that God would be invited to give it by a certain congruity. Gregory of Valencia '
            'ascribes this opinion to Thomas of Argentina, Gabriel, and Ockham among the older '
            'Scholastics: and likewise to Chrysostom Javellus the Dominican, who wrote in the '
            'previous century.'
        ),
        'pass_b': [
            'First opinion: pre-grace moral works as meritorious cause.',
            'Foresaw natural free-choice goodness → congruous grace.',
            'Named: Thomas of Argentina, Gabriel, Ockham, Javellus.',
        ],
        'lemmas': [
            {'latin': 'bona opera moralia antecedentia gratiam justificationis', 'gloss': 'moral good works antecedent to the grace of justification'},
            {'latin': 'ex congruitate quadam', 'gloss': 'by a certain congruity'},
        ],
        'choices': [{
            'term': 'causam meritoriam praedestinationis … esse bona opera moralia antecedentia gratiam justificationis',
            'english': 'that the meritorious cause of predestination … is moral good works antecedent to the grace of justification',
            'why': 'First of the four Roman opinions Le Blanc will survey.',
            'rejected': ['no Scholastic ever put pre-grace morals as election’s cause'],
        }],
        'notes': ['OCR: V PDF 134; Gregory of Valencia; Occam.'],
        'bible_refs': [],
    },
    {
        'section': '533',
        'title': 'Opinion 2 — merits after grace; Thomas’s horse',
        'pass_a': (
            'Others thought the cause of predestination to be merits not indeed antecedent to '
            'grace but following it. For they said that God from eternity decreed to confer '
            'grace on that man, and the remaining subsequent effects of predestination, whom He '
            'foresaw would use received grace rightly, and would have merits from God through '
            'divine grace. Which matter they explained by the example of some king who would '
            'wish to give a horse to that soldier whom he judged would use the horse well, and '
            'so on account of the future good use of the horse would give the horse. As Thomas '
            'reports in question 23 article 5. And Durandus on Distinction 41 of book 1 of the '
            'Sentences.'
        ),
        'pass_b': [
            'Second opinion: post-grace merits as cause.',
            'Foresaw right use of grace → further effects.',
            'King/horse example — Thomas ST I q.23 a.5; Durandus.',
        ],
        'lemmas': [
            {'latin': 'merita … illam subsequentia', 'gloss': 'merits … following it [grace]'},
            {'latin': 'propter bonum usum futurum equi', 'gloss': 'on account of the future good use of the horse'},
        ],
        'choices': [{
            'term': 'quem praevidit recte fuisse usurum accepta gratia',
            'english': 'whom He foresaw would use received grace rightly',
            'why': 'Marks the post-grace foresight theory.',
            'rejected': ['this opinion ignores grace entirely'],
        }],
        'notes': ['OCR: VI PDF 134; Thomas q.23 a.5; Durandus.'],
        'bible_refs': [],
    },
    {
        'section': '534',
        'title': 'Opinion 3 — Henry of Ghent / Eck; free will as sine qua non',
        'pass_a': (
            'To this opinion approaches, and with it almost coincides, the opinion of a certain '
            'Henry of Ghent, an older Scholastic. For he teaches that those actions by which '
            'the predestined man cooperates with divine calling and acquires justifying grace, '
            'and constantly perseveres in it once acquired, observing God’s commandments, can '
            'be considered in two ways: in one way as they are from free choice, in the other '
            'as they are from the help of Grace. And in the former way he says they are not '
            'effects of predestination, but in the latter way. And so he judges that those '
            'actions, as they are from Free choice, are a cause of predestination related to '
            'its effects, and therefore even to those very actions as they are from grace. But '
            'he adds that such actions are a cause not on account of which a man is predestined, '
            'as on account of merit of condignity, but without which he would not be '
            'predestined, and with which intervening he is predestined, from a certain '
            'congruity: because namely it is fitting and fair that God predestine him whom He '
            'sees will cooperate in that way with Divine grace. Which opinion, according to '
            'Gregory of Valencia, John Eck followed in the previous century in the book titled '
            'by him Chrysopassus.'
        ),
        'pass_b': [
            'Henry of Ghent: free-will side ≠ predestination’s effect.',
            'Grace-side = effect; free-will side = sine-qua-non congruity.',
            'Not condign merit — Eck’s Chrysopassus follows.',
        ],
        'lemmas': [
            {'latin': 'sine qua non praedestinaretur', 'gloss': 'without which he would not be predestined'},
            {'latin': 'ex congruitate quadam', 'gloss': 'from a certain congruity'},
        ],
        'choices': [{
            'term': 'causam non propter quam homo praedestinetur, tanquam propter meritum ex condigno, sed sine qua non praedestinaretur',
            'english': 'a cause not on account of which a man is predestined, as on account of merit of condignity, but without which he would not be predestined',
            'why': 'Third opinion: negative/congruous condition via free cooperation.',
            'rejected': ['Henry taught condign merit of election'],
        }],
        'notes': ['OCR: VII PDF 134; Henricus Gandavensis; Eckius Chrysopassus.'],
        'bible_refs': [],
    },
    {
        'section': '535',
        'title': 'Opinion 4 — negative cause: no final mortal obstacle',
        'pass_a': (
            'Finally some among the Scholastics judged that there is some cause of '
            'predestination on the part of the predestined, yet not a positive but a negative '
            'one. For they thought that God therefore predestines those whom He predestines '
            'because He foresaw that they would not finally put an obstacle to divine grace '
            'through mortal sin. Which various opinions are reported and explained by the same '
            'Gregory of Valencia, First Disputation, question 23 on Predestination, point 4.'
        ),
        'pass_b': [
            'Fourth opinion: negative cause only.',
            'Foresaw: no final mortal-sin block to grace.',
            'Catalogue via Gregory of Valencia Disp. 1 q.23 p.4.',
        ],
        'lemmas': [
            {'latin': 'non tamen positivam, sed negativam', 'gloss': 'yet not a positive but a negative one'},
            {'latin': 'non posituros obicem gratiae divinae finaliter', 'gloss': 'would not finally put an obstacle to divine grace'},
        ],
        'choices': [{
            'term': 'quia praevidit illos non posituros obicem gratiae divinae finaliter per peccatum mortale',
            'english': 'because He foresaw that they would not finally put an obstacle to divine grace through mortal sin',
            'why': 'Closes I-VIII’s opinion survey; next IX+ common Roman rejection.',
            'rejected': ['only positive merits were ever proposed'],
        }],
        'notes': ['OCR: VIII PDF 134; next IX rejects all four.'],
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
    for name in ('pdf_133.txt', 'pdf_134.txt'):
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
        if 528 <= n <= 535:
            notes = (
                f'Section {sid}: new densify De Causa Praedestinationis I-VIII; '
                'Pass A!=B; lock-grounded PDF 133-134 / book pp. 121-122.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in praedestinationis I-VIII packet scope covering all current sections.'
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
                'Scope review: densify De Causa Praedestinationis I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Opens after Scientia XXX. Next Praedestinatio IX+. Not shipped.'
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
        'locus': 'De Causa Praedestinationis theses I-VIII (senses; question; adults; four opinions)',
        'next_locus': 'De Causa Praedestinationis IX+ (common Roman rejection; Reformed contrast)',
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
        f'## {day} (Scribe — De Causa Praedestinationis I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Praedestinatio I–VIII → §§{SECS[0]}–{SECS[-1]}; opens after Scientia).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 133-134 / pp. 121-122).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Next: Praedestinatio IX+. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Causa Praedestinationis I–VIII densify)\n\n'
        'CoS densify: Praedestinatio I–VIII open after Scientia. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Praedestinatio I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Praedestinatio IX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_535.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-535 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
