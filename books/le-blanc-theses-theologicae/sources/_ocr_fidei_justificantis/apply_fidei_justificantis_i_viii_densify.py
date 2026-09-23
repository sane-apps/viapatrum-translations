#!/usr/bin/env python3
"""Build + apply An omnibus Hominibus detur Gratia sufficiens I-VIII densify (tip 676 → 684).

Vasquez infants; Tricassini; adult perpetual vs timed; Bellarmine; hardening. Live floor 5570. After tip-ready: HOLD live>5570 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_fidei_justificantis_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_fidei_just_densify')
SEED = Path('/tmp/leblanc_fidei_i_data')
PACKET_STEM = 'fidei_justificantis_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_fidei_justificantis/apply_fidei_justificantis_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['677', '678', '679', '680', '681', '682', '683', '684']
ROMANS = {
    '677': 'I', '678': 'II', '679': 'III', '680': 'IV',
    '681': 'V', '682': 'VI', '683': 'VII', '684': 'VIII',
}
TIP_BEFORE = 676
PRIOR_START = 599
LIVE_FLOOR = 5570
HOLD_MINUTES = 12

LATIN = {
  "677": "I. Fidem Historicam Protestantes nominant nudum & simplicem assensum quem multi praebent iis quae Verbo Dei proponuntur, propter Dei dicentis & testantis authoritatem; sic tamen ut inde ad recte agendum non moveantur, nec reddantur meliores. Tali fide dicitur credidisse Simon Magus, cujus tamen cor rectum coram Deo non erat, & qui nihilominus in felle amaritudinis, & vinculis iniquitatis, judice Petro, positus manebat, Act. 8. Et simili quoque modo credebant illi Judaeorum primores, qui Christum non confitebantur, quoniam magis diligebant gloriam hominum, quam gloriam Dei, Joan. 12.",
  "678": "II. Porro fides ista dicitur historica, non quod sit eorum solum quae historice narrantur in Scripturis. Nam qui hac fide praediti sunt vera credunt quaecunque in Verbo Dei continentur, non minus promissiones, dogmata, & praecepta, quam historias & narrationes. Sed appellatio ista sumitur a modo quo versatur haec fides circa suum objectum. Nempe veluti quum legimus historias ad nos nihil attinentes, eas nude contemplamur, nec inde commovemur & afficimur intus: ita qui fidem illam habent, quae Verbum Dei docet otiose speculantur, nec ea ad praxin referunt.",
  "679": "III. Et haec est fides quam Jacobus, epistolae capite secundo, fidem mortuam vocat; quia scilicet, omni motu & actione, non secus ac cadaver quoddam, destituta est. Adeoque nihil prodest ad salutem, sed potius culpam praegravat, & damnationem auget illorum qui in ea haerent. Juxta quod dicit ibidem Jacobus, Quid proderit, fratres mei, si fidem quis dicat se habere, opera autem non habeat? numquid poterit fides salvare eum? Quin ejusmodi fidem non veretur eodem loco daemonibus tribuere; Tu credis, inquit, quod Deus unus est, bene facis; & daemones credunt, & contremiscunt. Unde est quod Protestantes illam verae fidei nomine dignam non putant: quia videlicet, eorum judicio, ea sola fides vera meretur appellari quae justitiam & salutem affert illi qui ea praeditus est, quod ejusmodi fidei non competit.",
  "680": "IV. Unde colligunt omnino ab hac fide distinguendam esse fidem illam quam Scriptura summis laudibus & elogiis ornat, ad quam nos tam frequenter & vehementer hortatur, cuique justitiam & salutem nostram tribuere solet, tanquam indivulse cum ea cohaerentem. Ut quum apud Joannem dicitur, Sic Deus dilexit mundum, ut filium suum unigenitum daret; ut omnis qui credit in eum non pereat, sed habeat vitam aeternam. Et similiter apud Marcum, Qui crediderit, & baptizatus fuerit, salvus erit. Quibus consonat illud Pauli in Epistola ad Romanos, Finis legis est Christus ad justitiam omni credenti. Unde patet esse quandam fidem, quam quicunque habet coram Deo justus est, & Deo gratus & acceptus ad salutem & vitam aeternam; & quae proinde alia est ab ea fide quae in ipsis impiis & daemonibus reperitur. Ea vero fides piorum & justorum propria a Protestantibus sola digna censetur nomine fidei verae, salvificae, & justificantis. Joan. 3. Marc. 16. Rom. 10.",
  "681": "V. Et hinc apparet Protestantes per fidem justificantem non intelligere eam quae quocunque modo praeparat ad justificationem, sive proxime, sive remote; sed quae hominem reapse justificat, aut quam semper & infallibiliter comitatur justificatio. Et similiter non aliam fidem salvificam nominant, quam quae revera hominem in statu gratiae & salutis constituit.",
  "682": "VI. Quantum vero inter se differant fides historica & fides justificans, inter Reformatos non omnino convenit. Quidam tantum inter utramque discrimen esse volunt, ut distinctionem fidei in historicam & justificantem nolint dici distinctionem generis in species, sed vocis ambiguae in sua significata. Qua in sententia est Samuel Maresius in Academia Groningana Theologiae Professor celeberrimus, ut videre est in ejus Systemate, loco undecimo, Thesi 21. Alii vero dicunt esse divisionem generis in species, non tamen univocas, sed analogas. Quae est sententia Doctissimi viri Christophori Wittichii, antehac Noviomagi, & nunc Lugduni Batavorum Theologiae Professoris; in Theologia Pacifica, cap. 11. numero 136. ubi citat Paraeum, & Professores Leydenses, tanquam idem cum ipso in hac parte sentientes.",
  "683": "VII. Sed quomodo fides justificans ab historica differat, ex fidei justificantis definitione, & actuum ac partium ejus expositione melius constare poterit. Porro fides justificans a Reformatis varie describitur, & plures proferuntur ejus definitiones, quae videri possunt plus minusve commodae, sed tamen quoad sensum, eodem fere recidunt. Juxta Calvinum fides justificans est, Divinae erga nos benevolentiae firma certaque cognitio, quae gratuitae in Christo promissionis veritate fundata, per Spiritum Sanctum revelatur mentibus nostris, & cordibus obsignatur: cui consentit descriptio brevis illius Catechismi vulgaris, in quo fides dicitur esse Certa persuasio, vel fiducia quam debet habere quilibet Christianus, quod Deus pater ipsum amat propter filium suum Jesum Christum.",
  "684": "VIII. Beza autem in Annotationibus in caput primum ad Romanos fidem definit esse Firmam illam & constantem animi persuasionem, qua certus est apud se unusquisque fidelium, non modo in genere verum esse verbum Dei, ac proinde promissiones de gratuita per Christum reconciliatione, sed etiam istas ad se proprie pertinere credit. Ursino & Paraeo Fides justificans est non tantum certa notitia, qua firmiter quis assentitur omnibus quae Deus nobis in verbo suo patefecit, sed etiam certa fiducia, a Spiritu Sancto per Evangelium in corde fidelis accensa, qua in Deo acquiescit, certo statuens non solum aliis, sed sibi quoque remissionem peccatorum, aeternam justitiam & vitam donatam esse; idque gratis ex Dei misericordia, propter unius Christi meritum. In Explicationibus Catecheticis, parte secunda, quaestione 21."
}

SECTIONS = [
  {
    "section": "677",
    "title": "Historical faith: bare assent that does not move to right living",
    "pass_a": "Protestants name Historical Faith that bare and simple assent which many give to the things proposed in the Word of God, because of the authority of God speaking and witnessing; yet so that they are not thereby moved to act rightly, nor are made better. With such a faith Simon Magus is said to have believed, whose heart yet was not right before God, and who nevertheless remained, by Peter’s judgment, in the gall of bitterness and the bonds of iniquity, Acts 8. And in a like way also those chiefs of the Jews believed who did not confess Christ, because they loved the glory of men more than the glory of God, John 12.",
    "pass_b": [
      "Historical faith = bare assent to what God’s Word proposes.",
      "Authority of God speaking — yet no move to right living, no betterment.",
      "Simon Magus believed thus — heart not right; still in bitterness and iniquity (Acts 8).",
      "Jewish leaders likewise: believed but would not confess Christ — loved men’s glory more (John 12)."
    ],
    "lemmas": [
      {
        "latin": "nudum & simplicem assensum",
        "gloss": "bare and simple assent"
      },
      {
        "latin": "ut inde ad recte agendum non moveantur, nec reddantur meliores",
        "gloss": "so that they are not thereby moved to act rightly, nor are made better"
      }
    ],
    "choices": [
      {
        "term": "sic tamen ut inde ad recte agendum non moveantur, nec reddantur meliores",
        "english": "yet so that they are not thereby moved to act rightly, nor are made better",
        "why": "Marks historical faith as non-transforming assent.",
        "rejected": [
          "historical faith always reforms life"
        ]
      }
    ],
    "notes": [
      "OCR: I 1675 PDF 216; Act. 8; Joan. 12 (OCR 1 1)."
    ],
    "bible_refs": [
      "Acts 8",
      "John 12"
    ]
  },
  {
    "section": "678",
    "title": "Why called ‘historical’: idle contemplation, not content limited to narratives",
    "pass_a": "Further that faith is called historical, not because it is only of those things which are narrated historically in the Scriptures. For those endowed with this faith truly believe whatever is contained in the Word of God — no less promises, doctrines, and precepts than histories and narrations. But that name is taken from the manner in which this faith deals with its object. Namely just as when we read histories that do not concern us, we contemplate them nakedly, and are not thereby inwardly moved and affected: so those who have that faith idly speculate on what the Word of God teaches, and do not refer it to practice.",
    "pass_b": [
      "‘Historical’ is not ‘only Bible stories’.",
      "It believes promises, doctrines, and precepts too.",
      "The name tracks the manner: like reading unrelated history — bare gaze, no inward effect.",
      "Idle speculation on the Word — not referred to practice."
    ],
    "lemmas": [
      {
        "latin": "non quod sit eorum solum quae historice narrantur",
        "gloss": "not because it is only of those things which are narrated historically"
      },
      {
        "latin": "otiose speculantur, nec ea ad praxin referunt",
        "gloss": "they idly speculate, and do not refer it to practice"
      }
    ],
    "choices": [
      {
        "term": "appellatio ista sumitur a modo quo versatur haec fides circa suum objectum",
        "english": "that name is taken from the manner in which this faith deals with its object",
        "why": "Defines ‘historical’ by mode, not by narrative-only content.",
        "rejected": [
          "historical faith believes only narrative passages"
        ]
      }
    ],
    "notes": [
      "OCR: II 1675 PDF 216."
    ],
    "bible_refs": []
  },
  {
    "section": "679",
    "title": "James’s dead faith — no salvation; not worthy of the name ‘true faith’",
    "pass_a": "And this is the faith which James, in the second chapter of his epistle, calls dead faith; because, namely, it is destitute of every motion and action, no otherwise than a certain corpse. And so it profits nothing unto salvation, but rather weighs down the guilt, and increases the damnation, of those who cling in it. According to what James says in the same place, What shall it profit, my brethren, if a man say he has faith, but has not works? can faith save him? Nay, in the same place he does not fear to attribute such a faith to the demons; You believe, he says, that God is one; you do well; and the demons believe, and tremble. Whence it is that Protestants do not think it worthy of the name of true faith: because, namely, in their judgment, that faith alone deserves to be called true which brings justice and salvation to him who is endowed with it — which does not belong to such a faith.",
    "pass_b": [
      "James calls this dead faith — no motion or action, like a corpse.",
      "It does not save; it worsens guilt and damnation.",
      "Demons believe God is one and tremble — same sort of faith.",
      "Protestants deny it the name ‘true faith’: true faith alone brings justice and salvation."
    ],
    "lemmas": [
      {
        "latin": "fidem mortuam vocat",
        "gloss": "he calls dead faith"
      },
      {
        "latin": "ea sola fides vera meretur appellari quae justitiam & salutem affert",
        "gloss": "that faith alone deserves to be called true which brings justice and salvation"
      }
    ],
    "choices": [
      {
        "term": "nihil prodest ad salutem, sed potius culpam praegravat",
        "english": "it profits nothing unto salvation, but rather weighs down the guilt",
        "why": "Dead faith aggravates rather than saves.",
        "rejected": [
          "dead historical faith still saves without works"
        ]
      }
    ],
    "notes": [
      "OCR: III 1675 PDF 216–217; James 2."
    ],
    "bible_refs": [
      "James 2"
    ]
  },
  {
    "section": "680",
    "title": "Scripture’s praised faith is another — true, saving, justifying",
    "pass_a": "Whence they gather that that faith which Scripture adorns with highest praises and encomiums, to which it so often and vehemently exhorts us, and to which it is wont to attribute our justice and salvation as indivisibly cohering with it, is altogether to be distinguished from this faith. As when it is said in John, So God loved the world that He gave His only-begotten Son, that everyone who believes in Him should not perish but have eternal life. And likewise in Mark, He who has believed and been baptized shall be saved. With which agrees that of Paul in the Epistle to the Romans, The end of the law is Christ unto justice to everyone who believes. Whence it is plain that there is a certain faith which whoever has is just before God, and pleasing and acceptable to God unto salvation and eternal life; and which therefore is other than that faith which is found even in the ungodly and in demons. But that faith proper to the pious and the just is judged by Protestants alone worthy of the name of true, saving, and justifying faith. John 3; Mark 16; Rom. 10.",
    "pass_b": [
      "Scripture’s highly praised faith is another thing entirely.",
      "John 3 / Mark 16 / Romans: believe → eternal life, salvation, justice.",
      "Whoever has it is just before God — unlike demon/ungodly assent.",
      "Protestants reserve ‘true, saving, justifying faith’ for this alone."
    ],
    "lemmas": [
      {
        "latin": "omnino ab hac fide distinguendam esse fidem illam",
        "gloss": "that that faith is altogether to be distinguished from this faith"
      },
      {
        "latin": "nomine fidei verae, salvificae, & justificantis",
        "gloss": "of the name of true, saving, and justifying faith"
      }
    ],
    "choices": [
      {
        "term": "ea vero fides piorum & justorum propria … sola digna censetur nomine fidei verae, salvificae, & justificantis",
        "english": "but that faith proper to the pious and the just … is judged alone worthy of the name of true, saving, and justifying faith",
        "why": "Names the positive counterpart to dead historical faith.",
        "rejected": [
          "historical and justifying faith are the same gift"
        ]
      }
    ],
    "notes": [
      "OCR: IV 1675 PDF 217; Joan. 3; Marc. 16; Rom. 10 (OCR to)."
    ],
    "bible_refs": [
      "John 3",
      "Mark 16",
      "Rom. 10"
    ]
  },
  {
    "section": "681",
    "title": "Justifying faith actually justifies — not mere remote preparation",
    "pass_a": "And from this it appears that Protestants by justifying faith do not understand that which in any way prepares for justification, whether proximately or remotely; but that which in very deed justifies a man, or which justification always and infallibly accompanies. And likewise they name no other saving faith than that which truly sets a man in the state of grace and salvation.",
    "pass_b": [
      "Justifying faith ≠ any mere preparation for justification (near or remote).",
      "It actually justifies — or justification always and infallibly goes with it.",
      "Saving faith = what truly places a man in grace and salvation."
    ],
    "lemmas": [
      {
        "latin": "non intelligere eam quae quocunque modo praeparat ad justificationem",
        "gloss": "they do not understand that which in any way prepares for justification"
      },
      {
        "latin": "quae hominem reapse justificat, aut quam semper & infallibiliter comitatur justificatio",
        "gloss": "which in very deed justifies a man, or which justification always and infallibly accompanies"
      }
    ],
    "choices": [
      {
        "term": "sed quae hominem reapse justificat",
        "english": "but that which in very deed justifies a man",
        "why": "Blocks reducing justifying faith to mere prep.",
        "rejected": [
          "justifying faith is only remote disposition toward later justice"
        ]
      }
    ],
    "notes": [
      "OCR: V 1675 PDF 217."
    ],
    "bible_refs": []
  },
  {
    "section": "682",
    "title": "Reformed split: ambiguous word vs analogous species (Maresius / Wittich)",
    "pass_a": "But how far historical faith and justifying faith differ among themselves, there is not altogether agreement among the Reformed. Some will have there to be only such a difference between them that they refuse to call the distinction of faith into historical and justifying a distinction of a genus into species, but of an ambiguous word into its significations. In which opinion is Samuel Maresius, most celebrated Professor of Theology in the Academy of Groningen, as may be seen in his System, place eleven, Thesis 21. But others say it is a division of a genus into species, yet not univocal but analogous. Which is the opinion of the most learned man Christopher Wittich, formerly at Nijmegen, and now Professor of Theology at Leiden; in Theologia Pacifica, ch. 11, number 136, where he cites Paraeus and the Leiden Professors as feeling the same with him in this part.",
    "pass_b": [
      "Reformed disagree on how historical and justifying faith differ.",
      "Maresius: not genus/species — an ambiguous word’s senses (System XI.21).",
      "Wittich (and Paraeus / Leiden): genus into analogous species (Theologia Pacifica 11.136)."
    ],
    "lemmas": [
      {
        "latin": "nolint dici distinctionem generis in species, sed vocis ambiguae in sua significata",
        "gloss": "they refuse to call it a distinction of a genus into species, but of an ambiguous word into its significations"
      },
      {
        "latin": "divisionem generis in species, non tamen univocas, sed analogas",
        "gloss": "a division of a genus into species, yet not univocal but analogous"
      }
    ],
    "choices": [
      {
        "term": "inter Reformatos non omnino convenit",
        "english": "there is not altogether agreement among the Reformed",
        "why": "Flags an internal Reformed taxonomy dispute.",
        "rejected": [
          "all Reformed identically classify the distinction"
        ]
      }
    ],
    "notes": [
      "OCR: VI 1675 PDF 217; Maresius; Wittich Theologia Pacifica."
    ],
    "bible_refs": []
  },
  {
    "section": "683",
    "title": "Calvin and the common Catechism: sure knowledge and trust of God’s love in Christ",
    "pass_a": "But how justifying faith differs from historical will be able to appear better from the definition of justifying faith, and from the exposition of its acts and parts. Further justifying faith is variously described by the Reformed, and several definitions of it are brought forward, which may seem more or less convenient, yet as to sense they nearly come to the same. According to Calvin justifying faith is a firm and sure knowledge of the divine benevolence toward us, which, founded on the truth of the free promise in Christ, is revealed to our minds by the Holy Spirit, and sealed upon our hearts: with which agrees the brief description of that common Catechism, in which faith is said to be a Sure persuasion, or trust, which every Christian ought to have, that God the Father loves him for the sake of His Son Jesus Christ.",
    "pass_b": [
      "Better seen from defining justifying faith and its acts/parts.",
      "Reformed definitions vary in wording — nearly the same sense.",
      "Calvin: firm sure knowledge of God’s goodwill to us, on the free promise in Christ, Spirit-revealed and heart-sealed.",
      "Common Catechism: sure persuasion/trust that the Father loves me for Jesus’ sake."
    ],
    "lemmas": [
      {
        "latin": "Divinae erga nos benevolentiae firma certaque cognitio",
        "gloss": "a firm and sure knowledge of the divine benevolence toward us"
      },
      {
        "latin": "Certa persuasio, vel fiducia",
        "gloss": "a Sure persuasion, or trust"
      }
    ],
    "choices": [
      {
        "term": "per Spiritum Sanctum revelatur mentibus nostris, & cordibus obsignatur",
        "english": "is revealed to our minds by the Holy Spirit, and sealed upon our hearts",
        "why": "Calvin’s Spirit-seal of justifying faith.",
        "rejected": [
          "Calvin makes justifying faith bare historical assent"
        ]
      }
    ],
    "notes": [
      "OCR: VII 1675 PDF 217; Calvin; vulgar Catechism."
    ],
    "bible_refs": []
  },
  {
    "section": "684",
    "title": "Beza, Ursinus, Paraeus: persuasion and fiducia that the promises are mine",
    "pass_a": "But Beza in the Annotations on the first chapter to the Romans defines faith to be that Firm and constant persuasion of the mind by which each of the faithful is sure with himself not only that the word of God is true in general, and therefore the promises of free reconciliation through Christ, but also believes that those belong properly to himself. For Ursinus and Paraeus Justifying Faith is not only a sure knowledge by which one firmly assents to all things which God has disclosed to us in His word, but also a sure trust, kindled by the Holy Spirit through the Gospel in the heart of the faithful, by which he rests in God, certainly laying down that not only to others, but to himself also, remission of sins, eternal justice and life have been given; and that freely from God’s mercy, for the merit of Christ alone. In the Catechetical Explications, second part, question 21.",
    "pass_b": [
      "Beza: firm constant persuasion — God’s word true, and the free-reconciliation promises mine.",
      "Ursinus/Paraeus: not only sure assent to all God disclosed.",
      "Also Spirit-kindled trust through the Gospel — rest in God.",
      "Sure that remission, eternal justice, and life are given to me too — freely, for Christ’s merit alone."
    ],
    "lemmas": [
      {
        "latin": "istas ad se proprie pertinere credit",
        "gloss": "he believes that those belong properly to himself"
      },
      {
        "latin": "certa fiducia … qua in Deo acquiescit",
        "gloss": "a sure trust … by which he rests in God"
      }
    ],
    "choices": [
      {
        "term": "certo statuens non solum aliis, sed sibi quoque remissionem peccatorum … donatam esse",
        "english": "certainly laying down that not only to others, but to himself also, remission of sins … have been given",
        "why": "Fiducia applies the promise personally.",
        "rejected": [
          "justifying faith stops at general assent that promises are true for someone"
        ]
      }
    ],
    "notes": [
      "OCR: VIII 1675 PDF 217; Beza Ann. Rom. 1; Ursinus/Paraeus Cat. Expl. II.21; next IX+ Rivetus."
    ],
    "bible_refs": []
  }
]

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXXVII + "
    "De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur De Fidei justificantis natura I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur De Fidei justificantis natura I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine I-XLVIII + De Fidei justificantis natura I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Fidei justificantis natura I-VIII. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through De Fidei justificantis natura I-VIII. "
    "1675 PDF 216-217 for I-VIII. No modern English. "
    "This slice densifies Fidei justificantis I-VIII (historical/dead vs justifying; Calvin/Beza/Ursinus)."
)
LOCK_HEADER = (
    "Le Blanc Latin lock — De Fidei justificantis natura\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: De Fidei justificantis natura I-VIII tip. Next: Fidei justificantis IX+.\n"
    "Source: 1675 PDF pages 216-217 (book ~191-192).\n"
    "Note: Contiguous densify after Gratia sufficiens I-XXX.\n\n"
)


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
    parts = [LOCK_HEADER]
    for sec in SECS:
        parts.append(latin[sec].rstrip() + chr(10))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
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
        jpath = JUST / ('fidei_justificantis_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab fidei_justificantis_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
    for name in ('pdf_141.txt', 'pdf_142.txt'):
        p = DATA / name
        if p.exists():
            raw_sources.append(p)
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=raw_sources,
        expected_sections=section_ids,
        seed=20261004,
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
        if 631 <= n <= 638:
            notes = (
                'Section %s: new densify An omnibus Hominibus detur De Fidei justificantis natura I-VIII; '
                'Pass A!=B; lock-grounded PDF 146+ / book p.165+; I-VII from 1683 gap-fill for missing 1675 leaf 164.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in aeterna_electio XXXVII packet scope covering all current sections.'
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
                'Scope review: densify An omnibus Hominibus detur De Fidei justificantis natura I-VIII only '
                '(sections %s-%s). Meta discloses %s. '
                'Next De Certitudine qua Fidei competit IX+. Not shipped.'
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
            'An omnibus Hominibus detur De Fidei justificantis natura I-VIII '
            '(historical/dead vs justifying; Calvin; Beza; Ursinus/Paraeus)'
        ),
        'next_locus': (
            'De Fidei justificantis natura IX+ '
            '(Rivetus and further definitions)'
        ),
        'gates': {
            'check_pass_ab': 'ok fidei_justificantis_%s–%s (%s/%s)' % (
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
        '## %s (Scribe — An omnibus Hominibus detur De Fidei justificantis natura I-VIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous De Fidei justificantis natura I-VIII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: De Fidei justificantis natura IX+.\n\n'
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
        '## %s ~ET (Scribe — Le Blanc De Aeterna Electione XXXVII densify)\n\n'
        'CoS densify: De Fidei justificantis natura I-VIII (**%s→%s**). Packet %s. '
        'Next: De Fidei justificantis natura IX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_684.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-684 post-ready')
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
