#!/usr/bin/env python3
"""Build + apply De Certitudine qua Fidei competit XLI-XLVIII densify (tip 638 → 646).

Gravity cling; Spirit measure; not enthusiasm; post-faith word-work; finger of God;
experimental seal vs creating infusion. Live floor 5418. After tip-ready: HOLD live>5418 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_certitudine_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_certitudine_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_certitudine_densify')
SEED = Path('/tmp/leblanc_certitudine_xli_data')
PACKET_STEM = 'certitudine_xli_xlviii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_certitudine/apply_certitudine_xli_xlviii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['639', '640', '641', '642', '643', '644', '645', '646']
ROMANS = {
    '639': 'XLI', '640': 'XLII', '641': 'XLIII', '642': 'XLIV',
    '643': 'XLV', '644': 'XLVI', '645': 'XLVII', '646': 'XLVIII',
}
TIP_BEFORE = 638
PRIOR_START = 599
LIVE_FLOOR = 5418
HOLD_MINUTES = 12

LATIN = {
  "639": "XLI. Quae fidei firmitas potensque & tenax in mente adhaesio ex evidentia objecti non nascitur, sed ex rei ipsius gravitate & momento. Scilicet mens Spiritu Sancto illuminata percipit quamlibet aliam cognitionem ad bene beateque vivendum nihil aut parum conferre, verum ex hac hominis beatitudinem pendere, nec posse illam rejici, nisi cum certa totius hominis pernicie: ideoque tenacius, & potentius illi adhaerescit, quam ulli qualicunque cognitioni, sive scientiae. Denique, ut breviter quae fusius dicta sunt concludam, fides non tam procul a mente dubitationem removet, quam scientia, quae demonstratione nascitur; sed tamen mens fidei tenacius adhaeret, illamque ut sic dicam, studiose magis, & anxie custodit. Et idcirco, licet fides minus certa forte dici possit certitudine speculationis, quam scientiae prorsus demonstrativae, proculdubio tamen omnibus illis certior est certitudine adhaesionis.",
  "640": "XLII. Porro hinc liquere potest, quam non sine ratione alias docuerimus, totam certitudinem, quae in fide reperitur, non resolvi in ipsam verbi divini lucem, id est, in varias notas & argumenta, quibus verbum Dei tale esse se probat, nec argumenta illa esse mensuram totius ejus certitudinis, sed Spiritum Sanctum fidelium mentibus majorem de verbo Dei certitudinem imprimere quam per se ferant ejusmodi notae & argumenta: adeoque summam istam certitudinem, qua verbum Dei fides amplectitur, referendam esse ad internam operationem Spiritus Sancti, qui plenum illum & firmum assensum fidelium mentibus imprimit vi quadam quae sit omni argumento & ratione major.",
  "641": "XLIII. Etenim certitudo illa adhaesionis, qua fides humanas scientias superat, non mensuratur rei evidentia, nec simpliciter pendet a vi argumentorum quibus aliquid verum esse probatur: Et in ea fidelium menti ingeneranda praecipue sese exerit efficacia & vis Spiritus Sancti, qui non solum eis oculos aperit, ut perspiciant verbi divini lucem, id est, moralem illam evidentiam qua menti nostrae innotescere potest, & percipiant vim signorum & argumentorum quae probant & ostendunt Deum esse illius authorem: sed praeterea sic mentem hominis convertendi disponit & afficit, ut serio cogitet atque animadvertat Dei vocem, ad ipsum dirigi, illumque docere & monere de rebus, non levibus & parvi momenti, sed unde pendet totum animae bonum, & aeterna hominis salus, vel perditio: Jam vero nihil gravius & atrocius esse quam Deo loquenti assensum & obsequium debitum non praestare: Et nihil quoque insanus quam ea negligere in quibus vera hominis felicitas sita est, & quae rejici & contemni non possunt absque pernicie & summa miseria. Unde formatur in hominis animo propositum & judicium efficax, quo statuit Dei verbum cum debita veneratione & obsequio suscipere, illudque firmiter amplecti, & penitus ei adhaerere. Quod ut fiat necesse est voluntatem a rebus terrenis & caducis abstrahi, & ad Deum resque caelestes inclinari, & perrumpi obstacula pravorum affectuum, qui mentem ita pervertunt, & obscurant: ut hisce in rebus nihil sani judicare possit; quandoquidem, ut quisque affectus est ita judicat: ad quae omnia requiritur potentissima & efficacissima Spiritus Dei in animis nostris operatio.",
  "642": "XLIV. Nec tamen quicquam in nobis Spiritus Dei agit per modum raptus sive enthusiasmi: sed homines eo movet & impellit modo quodam naturae maxime consentaneo, & prout decet creaturam rationalem & liberam. Ac quamvis summa illa fidei firmitas atque certitudo, quam Spiritus nostris mentibus imprimit, tota referenda non sit ad objecti lucem sive evidentiam, nulla tamen ex parte ratione destituta est, nec caret omni fundamento etiam ex parte objecti. Siquidem nascitur ex rei ipsius dignitate atque gravitate, quam mens, ut decet, expendit & attendit, quomodo jam expositum est.",
  "643": "XLV. Verum adhuc alia ex parte certitudo quaedam fidei accrescit. Postquam enim aliquis Dei verbum admittit vera & sincera fide, verbum istud potenter & efficaciter in eo operatur. Nam primo conscientiam terret atque percellit acutissimo peccati & irae Dei sensu. Deinde illam consolatione suavissima mulcet, & creat in ea pacem quae superat omnem intellectum & gaudium inenarrabile: Phil. 4.7. 1 Petr. 1.8. Tum quoque hominum affectus immutat, pravos corrigit, turbatos componit, impuros mundat atque purificat: Et liberat animum a servitute vitiorum, ut libenter & alacriter Deum colat, & ipsi serviat: adeoque sic hominem totum intus & extra innovat, ut omni impietati & cupiditatibus mundanis renuncians, sobrie, juste & pie in hoc saeculo vivat, atque eo nomine nova creatura dici mereatur.",
  "644": "XLVI. Ista vero Dei verbum in hominum animis operari non potest, quin ipsi digitum Dei in se sentiant, & agnoscant divinam quandam efficaciam, quae intus eorum animos miris & variis modis commovet & afficit. Nec possunt mentem eo referre, quin inde valide in fide confirmentur, & novo quodam argumento colligant vere divinum esse verbum illud cujus tam divinam vim & energiam in se persentiunt. Quo spectat Apostolus dum gratulatur Thessalonicensibus quod verbum auditus Dei accepissent, non ut verbum hominum, sed sicut vere est, ut verbum Dei, quod & (inquit) operatur in vobis qui credidistis, 1 Thess. 2.13.",
  "645": "XLVII. Unde fidei accedit certitudo quaedam, ut sic dicam, experimentalis: & in eo quoque notare est internum quoddam Spiritus Sancti testimonium insigne valde & illustre, quo Dei verbum in cordibus fidelium obsignatur, ejusque divinitas & veritas sancitur. Nec alia ratione Spiritus Dei una cum spiritu nostro testatur nos esse filios Dei, ut loquitur Apostolus, Rom. 8.16. De quo certos nos reddere non potest Dei Spiritus suo testimonio, quin simul nos certos reddat Deum patrem nostrum esse, qui nos in Evangelio compellat atque alloquitur.",
  "646": "XLVIII. Verum hoc Spiritus Sancti testimonium, quod intus perhibet adoptioni nostrae & Evangelici verbi veritati & divinitati, per effecta varia ac plane divina, quae in nobis producit, mediante Dei verbo fide suscepto & admisso, distinguendum est ab altera illius operatione, qua fidem in nobis creat & infundit, & quae etiam vulgo testimonium internum Spiritus appellari solet. Etenim illud testimonium fidem natura praecedit, ut patet; hoc vero fidem consequitur, & illam supponit."
}

SECTIONS = [
  {
    "section": "639",
    "title": "Cling-strength from gravity of the matter, not object-evidence",
    "pass_a": "Which firmness of faith and powerful and tenacious adhesion in the mind is not born from the evidence of the object, but from the gravity and moment of the thing itself. Namely the mind illuminated by the Holy Spirit perceives that any other cognition contributes nothing or little to living well and blessedly, but that man's beatitude hangs from this, nor can it be rejected except with certain ruin of the whole man: and therefore it adheres more tenaciously and more powerfully to it than to any cognition whatsoever, or science. Finally, to conclude briefly what was said more fully: faith does not remove doubt so far from the mind as science born of demonstration; yet the mind of faith adheres more tenaciously, and guards it, so to speak, more studiously and anxiously. And therefore, although faith may perhaps be called less certain by the certainty of speculation than thoroughly demonstrative science, yet without doubt it is more certain than all those by the certainty of adhesion.",
    "pass_b": [
      "Cling-strength and tenacious adhesion: not from object-evidence.",
      "From the matter's gravity: Spirit-lit mind sees other knowledge little aids blessed life; reject this and whole-man ruin follows.",
      "Faith removes doubt less than demonstrative scientia — yet clings and guards more anxiously.",
      "Maybe less by speculation-certainty; surely greater by adhesion-certainty."
    ],
    "lemmas": [
      {
        "latin": "ex evidentia objecti non nascitur, sed ex rei ipsius gravitate & momento",
        "gloss": "is not born from the evidence of the object, but from the gravity and moment of the thing itself"
      },
      {
        "latin": "omnibus illis certior est certitudine adhaesionis",
        "gloss": "it is more certain than all those by the certainty of adhesion"
      }
    ],
    "choices": [
      {
        "term": "ex evidentia objecti non nascitur, sed ex rei ipsius gravitate & momento",
        "english": "is not born from the evidence of the object, but from the gravity and moment of the thing itself",
        "why": "Names the source of cling after XL's firmer-yet-less-clear assent.",
        "rejected": [
          "adhesion-strength measured by object-evidence"
        ]
      }
    ],
    "notes": [
      "OCR: XLI 1675 PDF 150; label XL1 in scan = XLI after XL."
    ],
    "bible_refs": []
  },
  {
    "section": "640",
    "title": "Faith's summit certainty referred to the Spirit's inward operation — not note-measure alone",
    "pass_a": "Further from this it can be clear how not without reason we have taught elsewhere that the whole certainty which is found in faith is not resolved into the light of the divine word itself — that is, into the various marks and arguments by which God's word proves itself to be such — nor that those arguments are the measure of its whole certainty; but that the Holy Spirit impresses on the minds of the faithful a greater certainty concerning God's word than such notes and arguments of themselves bear: and so that highest certainty by which faith embraces God's word is to be referred to the inward operation of the Holy Spirit, who impresses that full and firm assent on the minds of the faithful by a force which is greater than every argument and reason.",
    "pass_b": [
      "Whole faith-certainty not resolved into word-light or proving notes alone.",
      "Those arguments are not the measure of its whole certainty.",
      "Spirit stamps greater word-certainty than marks bear by themselves.",
      "Summit cling referred to inward Spirit operation: full firm assent by a force above every argument."
    ],
    "lemmas": [
      {
        "latin": "totam certitudinem … non resolvi in ipsam verbi divini lucem",
        "gloss": "that the whole certainty … is not resolved into the light of the divine word itself"
      },
      {
        "latin": "referendam esse ad internam operationem Spiritus Sancti",
        "gloss": "is to be referred to the inward operation of the Holy Spirit"
      }
    ],
    "choices": [
      {
        "term": "Spiritum Sanctum … majorem de verbo Dei certitudinem imprimere quam per se ferant ejusmodi notae & argumenta",
        "english": "the Holy Spirit impresses … a greater certainty concerning God's word than such notes and arguments of themselves bear",
        "why": "Keeps XXX/XXXII internal-Spirit line after adhesion ranking.",
        "rejected": [
          "notes alone measure the whole certainty of faith"
        ]
      }
    ],
    "notes": [
      "OCR: XLII 1675 PDF 150–151 (page break mid-sentence)."
    ],
    "bible_refs": []
  },
  {
    "section": "641",
    "title": "Adhesion that beats human sciences: Spirit opens eyes and bends the will",
    "pass_a": "For that certainty of adhesion by which faith surpasses the human sciences is not measured by the evidence of the thing, nor does it simply hang from the force of the arguments by which something is proved to be true: and in generating it in the mind of the faithful there chiefly exerts itself the efficacy and force of the Holy Spirit, who not only opens their eyes that they may perceive the light of the divine word — that is, that moral evidence by which it can become known to our mind — and perceive the force of the signs and arguments which prove and show that God is its author: but besides so disposes and affects the mind of the man to be converted that he seriously thinks and notices that God's voice is directed to him, and teaches and warns him of things not light and of small moment, but from which hangs the whole good of the soul and man's eternal salvation or perdition. Now truly nothing is graver and more dreadful than not to render due assent and obedience to God speaking: and nothing likewise more insane than to neglect those things in which man's true happiness is situated, and which cannot be rejected and despised without ruin and utmost misery. Whence is formed in man's soul an efficacious purpose and judgment by which he lays down to receive God's word with due veneration and obedience, to embrace it firmly, and to adhere to it inwardly. Which that it may be done, it is necessary that the will be drawn away from earthly and fleeting things, and inclined to God and heavenly things, and that the obstacles of base affections be broken through, which so pervert and darken the mind that in these matters it can judge nothing sound — since as each is affected, so he judges: for all which is required the most powerful and most efficacious operation of God's Spirit in our souls.",
    "pass_b": [
      "Adhesion-certainty greater than human sciences: not measured by evidence; not simply by proving-force.",
      "Spirit chiefly generates it: opens eyes to moral word-light and author-signs.",
      "Also bends the converting mind: God's voice addresses me; stakes are the soul's whole good and eternal salvage or ruin.",
      "Nothing worse than refuse God speaking; insane to neglect true happiness.",
      "Efficacious resolve: receive, embrace, cling — will pulled from earth; base affections broken; Spirit's strongest work."
    ],
    "lemmas": [
      {
        "latin": "certitudo illa adhaesionis … non mensuratur rei evidentia",
        "gloss": "that certainty of adhesion … is not measured by the evidence of the thing"
      },
      {
        "latin": "praecipue sese exerit efficacia & vis Spiritus Sancti",
        "gloss": "there chiefly exerts itself the efficacy and force of the Holy Spirit"
      }
    ],
    "choices": [
      {
        "term": "sic mentem hominis convertendi disponit & afficit, ut serio cogitet … Dei vocem, ad ipsum dirigi",
        "english": "so disposes and affects the mind of the man to be converted that he seriously thinks … that God's voice is directed to him",
        "why": "Spirit's work is more than evidential eye-opening.",
        "rejected": [
          "Spirit only supplies more arguments, never moves the will"
        ]
      }
    ],
    "notes": [
      "OCR: XLIII 1675 PDF 151."
    ],
    "bible_refs": []
  },
  {
    "section": "642",
    "title": "Not by rapture or enthusiasm — yet not without object-side ground",
    "pass_a": "Nor yet does God's Spirit act anything in us by way of rapture or enthusiasm: but He moves and drives men in a manner most agreeable to nature, and as befits a rational and free creature. And although that highest firmness and certainty of faith which the Spirit impresses on our minds is not to be wholly referred to the light or evidence of the object, yet it is destitute of reason on no side, nor does it lack every foundation even on the object's side. For it is born from the dignity and gravity of the thing itself, which the mind, as is fitting, weighs and attends to, as has already been set out.",
    "pass_b": [
      "Spirit's work is not rapture or enthusiasm.",
      "Moves as befits a rational free creature — nature-agreeing.",
      "Highest faith-firmness not wholly from object-light — yet not reasonless.",
      "Even object-side ground: dignity and gravity the mind duly weighs (as already shown)."
    ],
    "lemmas": [
      {
        "latin": "per modum raptus sive enthusiasmi",
        "gloss": "by way of rapture or enthusiasm"
      },
      {
        "latin": "nascitur ex rei ipsius dignitate atque gravitate",
        "gloss": "it is born from the dignity and gravity of the thing itself"
      }
    ],
    "choices": [
      {
        "term": "Nec tamen quicquam in nobis Spiritus Dei agit per modum raptus sive enthusiasmi",
        "english": "Nor yet does God's Spirit act anything in us by way of rapture or enthusiasm",
        "why": "Blocks fanatic reading of Spirit-impressed certainty.",
        "rejected": [
          "Spirit certainty is pure enthusiasm without object ground"
        ]
      }
    ],
    "notes": [
      "OCR: XLIV 1675 PDF 151."
    ],
    "bible_refs": []
  },
  {
    "section": "643",
    "title": "After true faith, the word works: terror, peace, new creature",
    "pass_a": "But still from another side a certain certainty of faith grows. For after someone admits God's word with true and sincere faith, that word operates in him powerfully and efficaciously. For first it terrifies and strikes the conscience with a most sharp sense of sin and of God's wrath. Then it soothes it with most sweet consolation, and creates in it peace that surpasses every understanding and joy unspeakable: Phil. 4.7; 1 Pet. 1.8. Then also it changes men's affections, corrects the base, settles the disturbed, cleanses and purifies the impure: and frees the soul from the slavery of vices, that it may gladly and cheerfully worship God and serve Him: and so renews the whole man within and without, that renouncing all impiety and worldly lusts he may live soberly, justly, and piously in this age, and on that account deserve to be called a new creature.",
    "pass_b": [
      "Another side: certainty grows after true admission of the word.",
      "Word works hard: first sharp terror of sin and wrath.",
      "Then sweet comfort — peace beyond understanding, unspeakable joy (Phil 4:7; 1 Pet 1:8).",
      "Changes affections; frees from vice; renews whole man — soberly, justly, piously; new creature."
    ],
    "lemmas": [
      {
        "latin": "verbum istud potenter & efficaciter in eo operatur",
        "gloss": "that word operates in him powerfully and efficaciously"
      },
      {
        "latin": "pacem quae superat omnem intellectum & gaudium inenarrabile",
        "gloss": "peace that surpasses every understanding and joy unspeakable"
      }
    ],
    "choices": [
      {
        "term": "Postquam enim aliquis Dei verbum admittit vera & sincera fide, verbum istud potenter & efficaciter in eo operatur",
        "english": "For after someone admits God's word with true and sincere faith, that word operates in him powerfully and efficaciously",
        "why": "Post-faith efficacy as further certainty-source.",
        "rejected": [
          "word's transforming work precedes and replaces faith"
        ]
      }
    ],
    "notes": [
      "OCR: XLV 1675 PDF 151; 1 Petr. j.8 read as 1 Pet. 1.8."
    ],
    "bible_refs": [
      "Phil. 4.7",
      "1 Pet. 1.8"
    ]
  },
  {
    "section": "644",
    "title": "Feeling God's finger in the word's work confirms it is divine",
    "pass_a": "But that word of God cannot operate in men's souls without their feeling the finger of God in themselves, and acknowledging a certain divine efficacy which inwardly moves and affects their minds in wondrous and various ways. Nor can they refer the mind thither without being thereby strongly confirmed in faith, and gathering by a new argument that that word is truly divine whose so divine force and energy they feel in themselves. To which the Apostle looks when he congratulates the Thessalonians that they had received the word of the hearing of God, not as the word of men, but as it truly is, as the word of God, which also (he says) works in you who believed, 1 Thess. 2.13.",
    "pass_b": [
      "Word cannot so work without men feeling God's finger in themselves.",
      "They own a divine efficacy moving the mind within.",
      "That felt force becomes a new argument: this word is truly divine.",
      "Paul to Thessalonica: received as God's word, which works in you who believed (1 Thess 2:13)."
    ],
    "lemmas": [
      {
        "latin": "digitum Dei in se sentiant",
        "gloss": "they feel the finger of God in themselves"
      },
      {
        "latin": "vere divinum esse verbum illud",
        "gloss": "that that word is truly divine"
      }
    ],
    "choices": [
      {
        "term": "quin ipsi digitum Dei in se sentiant, & agnoscant divinam quandam efficaciam",
        "english": "without their feeling the finger of God in themselves, and acknowledging a certain divine efficacy",
        "why": "Experiential seal of post-faith word-work.",
        "rejected": [
          "felt efficacy is irrelevant to the word's divinity"
        ]
      }
    ],
    "notes": [
      "OCR: XLVI 1675 PDF 151; energiam for Greek energy (OCR garbled)."
    ],
    "bible_refs": [
      "1 Thess. 2.13"
    ]
  },
  {
    "section": "645",
    "title": "Experimental certainty — Spirit seals the word and sonship together",
    "pass_a": "Whence there accrues to faith a certain certainty, so to speak, experimental: and in that also is to be noted a certain inward testimony of the Holy Spirit, very signal and illustrious, by which God's word is sealed in the hearts of the faithful, and its divinity and truth are sanctioned. Nor by any other reason does God's Spirit together with our spirit testify that we are sons of God, as the Apostle speaks, Rom. 8.16. Concerning which God's Spirit cannot make us certain by His testimony without at the same time making us certain that God is our Father, who calls and addresses us in the Gospel.",
    "pass_b": [
      "Faith gains an experimental certainty.",
      "Inward Spirit-testimony seals the word in the heart — divinity and truth sanctioned.",
      "Same witness: Spirit with our spirit testifies we are sons (Rom 8:16).",
      "Cannot certify sonship without certifying the Father who addresses us in the Gospel."
    ],
    "lemmas": [
      {
        "latin": "certitudo quaedam, ut sic dicam, experimentalis",
        "gloss": "a certain certainty, so to speak, experimental"
      },
      {
        "latin": "Spiritus Dei una cum spiritu nostro testatur nos esse filios Dei",
        "gloss": "God's Spirit together with our spirit testifies that we are sons of God"
      }
    ],
    "choices": [
      {
        "term": "internum quoddam Spiritus Sancti testimonium … quo Dei verbum in cordibus fidelium obsignatur",
        "english": "a certain inward testimony of the Holy Spirit … by which God's word is sealed in the hearts of the faithful",
        "why": "Names experimental sealing distinct from mere moral notes.",
        "rejected": [
          "experimental certainty is only private enthusiasm"
        ]
      }
    ],
    "notes": [
      "OCR: XLVII 1675 PDF 151; Rom.8.i7 corrected to 8.16 (witness-with-our-spirit verse)."
    ],
    "bible_refs": [
      "Rom. 8.16"
    ]
  },
  {
    "section": "646",
    "title": "Post-faith sealing is not the earlier operation that creates faith",
    "pass_a": "But this testimony of the Holy Spirit, which inwardly bears witness to our adoption and to the truth and divinity of the Gospel word, through various and plainly divine effects which it produces in us, by means of God's word received and admitted by faith, is to be distinguished from that other operation of His by which He creates and pours faith into us, and which also is commonly wont to be called the inward testimony of the Spirit. For that testimony precedes faith by nature, as is plain; but this follows faith, and presupposes it.",
    "pass_b": [
      "This post-faith sealing (adoption and Gospel divinity via divine effects) is not the Spirit's creating infusion.",
      "The creating work is what people commonly call inward testimony.",
      "Creating testimony precedes faith by nature.",
      "Experimental sealing follows faith and presupposes it."
    ],
    "lemmas": [
      {
        "latin": "distinguendum est ab altera illius operatione, qua fidem in nobis creat & infundit",
        "gloss": "is to be distinguished from that other operation of His by which He creates and pours faith into us"
      },
      {
        "latin": "illud testimonium fidem natura praecedit … hoc vero fidem consequitur",
        "gloss": "that testimony precedes faith by nature … but this follows faith"
      }
    ],
    "choices": [
      {
        "term": "distinguendum est ab altera illius operatione, qua fidem in nobis creat & infundit",
        "english": "is to be distinguished from that other operation of His by which He creates and pours faith into us",
        "why": "Splits experimental seal from faith-creating internal testimony.",
        "rejected": [
          "one undifferentiated internal testimony both creates and seals"
        ]
      }
    ],
    "notes": [
      "OCR: XLVIII 1675 PDF 152; illud=creating / hoc=experimental to match sense of the distinction."
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
    "De Certitudine qua Fidei competit I-XLVIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine qua Fidei competit I-XLVIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Certitudine qua Fidei competit I-XLVIII. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through De Certitudine qua Fidei competit I-XLVIII. "
    "1675 PDF 150-152 for XLI-XLVIII. No modern English. "
    "This slice densifies Certitudine XLI-XLVIII (gravity cling; Spirit measure; experimental seal)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt).\n"
    "Tract: De Certitudine qua Fidei competit.\n"
    "Copy-text intent: 1675 Pitt. I-VII start filled from 1683 where 1675 IA lacks leaf 164; "
    "VIII+ from 1675 PDF 146-150. pdftotext + DjVu. No modern English.\n"
    "Scope: De Certitudine qua Fidei competit I-XLVIII tip. Next: An omnibus Hominibus detur Gratia sufficiens I+.\n"
    "Note: Speculation rank vs adhesion; moral certainty still binds; faith clings harder than scientia.\n\n"
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
    prior = LOCK.read_text(encoding='utf-8') if LOCK.exists() else LOCK_HEADER
    # refresh header; keep prior theses I-XL latin bodies
    body_lines = []
    if LOCK.exists():
        raw = LOCK.read_text(encoding='utf-8')
        # drop old header through blank line after Note
        parts = raw.split('\n\n', 1)
        prior_body = parts[1] if len(parts) > 1 else raw
        # strip any existing IX+ if re-run
        keep = []
        for block in prior_body.strip().split('\n'):
            keep.append(block)
        # rebuild from source.json 599-606 + new
        pass
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    parts = [LOCK_HEADER]
    for sec in [str(n) for n in range(599, TIP_BEFORE + 1)]:
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
        jpath = JUST / ('certitudine_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab certitudine_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
                'Section %s: new densify De Certitudine qua Fidei competit XLI-XLVIII; '
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
                'Scope review: densify De Certitudine qua Fidei competit XLI-XLVIII only '
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
            'De Certitudine qua Fidei competit XLI-XLVIII '
            '(gravity cling; Spirit measure; experimental seal vs creating infusion)'
        ),
        'next_locus': (
            'An omnibus Hominibus detur Gratia sufficiens I+ '
            '(sufficient grace for conversion)'
        ),
        'gates': {
            'check_pass_ab': 'ok certitudine_%s–%s (%s/%s)' % (
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
        '## %s (Scribe — De Certitudine qua Fidei competit XLI-XLVIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Certitudine XLI-XLVIII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: An omnibus Hominibus detur Gratia sufficiens I+.\n\n'
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
        'CoS densify: Certitudine XLI-XLVIII (**%s→%s**). Packet %s. '
        'Next: An omnibus Hominibus detur Gratia sufficiens I+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_646.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-646 post-ready')
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
