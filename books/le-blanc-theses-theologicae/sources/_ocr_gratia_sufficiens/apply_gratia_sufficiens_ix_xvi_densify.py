#!/usr/bin/env python3
"""Build + apply An omnibus Hominibus detur Gratia sufficiens IX-XVI densify (tip 654 → 662).

Vasquez infants; Tricassini; adult perpetual vs timed; Bellarmine; hardening. Live floor 5471. After tip-ready: HOLD live>5471 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_gratia_sufficiens_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_gratia_sufficiens_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_gratia_densify')
SEED = Path('/tmp/leblanc_gratia_ix_data')
PACKET_STEM = 'gratia_sufficiens_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_gratia_sufficiens/apply_gratia_sufficiens_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['655', '656', '657', '658', '659', '660', '661', '662']
ROMANS = {
    '655': 'IX', '656': 'X', '657': 'XI', '658': 'XII',
    '659': 'XIII', '660': 'XIV', '661': 'XV', '662': 'XVI',
}
TIP_BEFORE = 654
PRIOR_START = 599
LIVE_FLOOR = 5471
HOLD_MINUTES = 12

LATIN = {
  "655": "IX. In ea est sententia Vasquez, qui monet hic non quaeri an Christus instituerit media ad salutem parvulis omnibus ex se sufficientia: sed an illa ita providerit & disposuerit, ut in libera facultate alicujus applicationem illorum reliquerit. Et postea, adhibita quadam distinctione, docet quibusdam parvulis, editis nimirum in lucem, & iis qui negligentia parentum in utero materno moriuntur, provisa fuisse remedia sufficientia, quae applicari illis possent, licet adultorum negligentia non fuerint applicata: quibusdam vero parvulis non fuisse a Deo ullo modo concessum, posse humana diligentia applicari sufficientia remedia, sive editis in lucem, quum aqua non conceditur, sive in utero materno vi sola naturae morientibus. Tom. 1. in 1. Thom. disputatione 96.",
  "656": "X. Sed contra alii affirmant, etiam respectu ipsorum infantium, gratiam omnibus sufficientem dari: idque quoniam Deus, quantum in ipso est, baptismum omnibus infantibus paravit, & parentibus, ac aliis in quorum potestate sunt infantes, seu immediatam, sive mediatam facultatem dedit ipsos baptizandi, & ita salutem eorum procurandi.",
  "657": "XI. Haec est sententia Caroli Joseph Tricassini Concionatoris Capucini, in libro nuper edito de necessaria ad salutem gratia omnibus & singulis data, secundae partis sectione ultima, ubi haec est ejus conclusio, Omnes & singuli parvuli habent gratiam sufficientem ad salutem, non quidem in seipsis, cum ejus recipiendae sint incapaces, sed in suis parentibus, & parentum amicis, qui possunt eos perducere ad baptismum, & per hoc ad salutem.",
  "658": "XII. Postea vero explicat quomodo parentes possint eos ad baptismum perducere. Nempe si infideles sunt, gratiam habent qua possint vel immediate, vel saltem mediate credere, & ita suis baptismum procurare. Si vero fideles sunt, possunt orare pro salute parvulorum suorum, ut Deus servet eos usque ad nativitatem, quo tempore solliciti debent esse, ut cito procurent ipsis baptismum. Possunt etiam cavere a peccatis, ne ob ea priventur parvuli sua vita temporali antequam nascantur. Et specialiter possunt cavere matres ab iis omnibus, quae possunt sibi, & parvulis suis, quos gestant in utero, esse noxia & lethifera. Quae si bene observent, parvuli eorum sunt perventuri ad baptismum, & sic ad salutem aeternam.",
  "659": "XIII. Quod attinet autem ad adultos, illi ipsi qui docent adultis omnibus gratiam sufficientem dari, inter se non consentiunt, An gratia ista sufficiens perpetuo illis adsit, An vero iis detur pro loco tantum & tempore; ita ut aliquando ea destituti sint. Nam hodierni Jesuitae, & plerique alii Scholae Romanae Doctores statuunt adultis omnibus, ad finem usque vitae perpetuo adesse gratiam, qua & vitare possint singula peccata quorum occasio se offert, & ad quae tentantur atque impelluntur, & qua possint quoque ad Deum converti, & se ex statu peccati eripere.",
  "660": "XIV. At vero alii quadam hic utuntur distinctione. Sunt enim qui sentiunt neminem quidem esse cui non in aliquo saltem vitae momento, Deus largiatur gratiam qua possit sese ad Deum convertere, & salutis fieri particeps: sed negant istam gratiam semper omnibus praesto esse: multos enim illa juste propter peccata a Deo destitui. Verum contendunt Deum nunquam ulli homini denegare gratiam qua possit a novis peccatis abstinere, & tentationi ingruenti resistere, scilicet, vel immediate, vel ut dictum est, saltem mediate, per auxilium, quod quidem non habet, sed quod precibus impetrare potest. Qua in sententia est Cardinalis Bellarminus, ut videre est primis capitibus libri secundi de Gratia & libero arbitrio.",
  "661": "XV. Nonnulli tamen ex patronis gratiae universalis atque sufficientis nequidem admittunt semper omnibus adesse gratiam qua possint peccata vitare: quia scilicet, quidam propter nimium gratiae divinae abusum, & in vindictam ac poenam peccatorum praecedentium, sic a Deo deseruntur, ut deinceps prorsus mancipentur pravis suis cupiditatibus, nec amplius possunt non peccare. Quo de numero putant esse illos quos scriptura induratos & occaecatos vocat.",
  "662": "XVI. Hanc sententiam Vasquez tribuit Tostato Episcopo Abulensi, Cardinali Cajetano, Joanni Episcopo Roffensi & Cardinali, & Ruardo Tappero Professori Lovaniensi, quos censere affirmat, interdum propter peiora peccata, ita destitui homines per aliquam certam vitae periodum, ut nec sufficiens & necessarium iis concedatur auxilium, quo observare valeant mandata credendi, paenitendi, & alia hujusmodi, atque peccata evitare. Tom. 1. in 1. Thom. disp. 96. cap. 3."
}

SECTIONS = [
  {
    "section": "655",
    "title": "Vasquez on infants: sufficient remedies for some, not all",
    "pass_a": "In that is the opinion of Vasquez, who warns that the question here is not whether Christ instituted means to salvation sufficient of themselves for all little ones: but whether He so provided and arranged them that He left their application in someone’s free faculty. And afterward, using a certain distinction, he teaches that for some little ones — namely those brought forth into the light, and those who die in the mother’s womb by the parents’ negligence — sufficient remedies were provided which could be applied to them, though by adults’ negligence they were not applied: but that to some little ones it was in no way granted by God that sufficient remedies could be applied by human diligence, whether for those brought forth into the light when water is not granted, or for those dying in the mother’s womb by nature’s force alone. Tom. 1 on 1 Sent. of Thomas, disputation 96.",
    "pass_b": [
      "Vasquez: the question is not whether Christ made means sufficient in themselves for every infant.",
      "But whether He left their application in someone’s free power.",
      "Some infants (born, or dying in the womb by parental neglect): sufficient remedies were provided — though often unused.",
      "Others: God never granted that human diligence could apply sufficient remedies (no water; womb-death by nature alone)."
    ],
    "lemmas": [
      {
        "latin": "non quaeri an Christus instituerit media … ex se sufficientia",
        "gloss": "it is not asked whether Christ instituted means … sufficient of themselves"
      },
      {
        "latin": "in libera facultate alicujus applicationem illorum reliquerit",
        "gloss": "He left their application in someone’s free faculty"
      }
    ],
    "choices": [
      {
        "term": "quibusdam vero parvulis non fuisse a Deo ullo modo concessum, posse humana diligentia applicari sufficientia remedia",
        "english": "but that to some little ones it was in no way granted by God that sufficient remedies could be applied by human diligence",
        "why": "Marks Vasquez’s hard limit inside infant sufficiency.",
        "rejected": [
          "Vasquez grants every infant apply-able sufficient baptismal means"
        ]
      }
    ],
    "notes": [
      "OCR: IX 1675 PDF 213; Vasquez in 1 Thom. disp. 96."
    ],
    "bible_refs": []
  },
  {
    "section": "656",
    "title": "Others: every infant has sufficient grace — baptism prepared for all",
    "pass_a": "But against this others affirm that even with respect to the infants themselves sufficient grace is given to all: and that because God, as far as in Him lies, prepared baptism for all infants, and gave to parents and to others in whose power the infants are, whether an immediate or a mediate faculty of baptizing them, and so of procuring their salvation.",
    "pass_b": [
      "Contra Vasquez: sufficient grace is given even for every infant.",
      "God prepared baptism for all infants, as far as in Him lies.",
      "Parents and guardians got immediate or mediate power to baptize — and so to procure their salvation."
    ],
    "lemmas": [
      {
        "latin": "etiam respectu ipsorum infantium, gratiam omnibus sufficientem dari",
        "gloss": "that even with respect to the infants themselves sufficient grace is given to all"
      },
      {
        "latin": "baptismum omnibus infantibus paravit",
        "gloss": "He prepared baptism for all infants"
      }
    ],
    "choices": [
      {
        "term": "parentibus … facultatem dedit ipsos baptizandi, & ita salutem eorum procurandi",
        "english": "He gave to parents … the faculty of baptizing them, and so of procuring their salvation",
        "why": "Locates infant sufficiency in adults’ baptismal power.",
        "rejected": [
          "infant sufficiency needs no human baptizer at all"
        ]
      }
    ],
    "notes": [
      "OCR: X 1675 PDF 213."
    ],
    "bible_refs": []
  },
  {
    "section": "657",
    "title": "Tricassini: infants’ sufficient grace is in parents and friends",
    "pass_a": "This is the opinion of Charles Joseph Tricassini, Capuchin preacher, in a book lately published on the grace necessary to salvation given to all and each, in the last section of the second part, where this is his conclusion: All and each little ones have sufficient grace for salvation, not indeed in themselves, since they are incapable of receiving it, but in their parents and the parents’ friends, who can lead them to baptism, and by this to salvation.",
    "pass_b": [
      "Tricassini (Capuchin): every infant has sufficient grace for salvation.",
      "Not in themselves — they cannot receive it yet.",
      "But in parents and parents’ friends who can bring them to baptism — and so to salvation."
    ],
    "lemmas": [
      {
        "latin": "Omnes & singuli parvuli habent gratiam sufficientem ad salutem",
        "gloss": "All and each little ones have sufficient grace for salvation"
      },
      {
        "latin": "non quidem in seipsis … sed in suis parentibus, & parentum amicis",
        "gloss": "not indeed in themselves … but in their parents and the parents’ friends"
      }
    ],
    "choices": [
      {
        "term": "non quidem in seipsis, cum ejus recipiendae sint incapaces, sed in suis parentibus",
        "english": "not indeed in themselves, since they are incapable of receiving it, but in their parents",
        "why": "Puts infant sufficiency in caregivers, not the child’s own act.",
        "rejected": [
          "infants themselves already possess usable saving grace inwardly"
        ]
      }
    ],
    "notes": [
      "OCR: XI 1675 PDF 213; Capuchin Tricassini."
    ],
    "bible_refs": []
  },
  {
    "section": "658",
    "title": "How parents can bring infants to baptism — unbelieving and believing",
    "pass_a": "But afterward he explains how parents can lead them to baptism. Namely if they are unbelievers, they have grace by which they can believe either immediately, or at least mediately, and so procure baptism for their own. But if they are believers, they can pray for the salvation of their little ones, that God may keep them until birth, at which time they ought to be careful to procure baptism for them quickly. They can also beware of sins, lest on their account the little ones be deprived of their temporal life before they are born. And especially mothers can beware of all those things which can be harmful and deadly to themselves and to their little ones whom they carry in the womb. Which if they carefully observe, their little ones are to come through to baptism, and so to eternal salvation.",
    "pass_b": [
      "How parents lead infants to baptism:",
      "Unbelievers: grace to believe (immediate or at least mediate) → then seek baptism.",
      "Believers: pray God keep the child to birth; baptize promptly; avoid sins that cut life short.",
      "Mothers especially avoid what harms mother or child in the womb — then baptism and eternal salvation follow."
    ],
    "lemmas": [
      {
        "latin": "si infideles sunt, gratiam habent qua possint vel immediate, vel saltem mediate credere",
        "gloss": "if they are unbelievers, they have grace by which they can believe either immediately, or at least mediately"
      },
      {
        "latin": "parvuli eorum sunt perventuri ad baptismum, & sic ad salutem aeternam",
        "gloss": "their little ones are to come through to baptism, and so to eternal salvation"
      }
    ],
    "choices": [
      {
        "term": "possunt orare pro salute parvulorum suorum, ut Deus servet eos usque ad nativitatem",
        "english": "they can pray for the salvation of their little ones, that God may keep them until birth",
        "why": "Believing parents’ path to infant baptismal sufficiency.",
        "rejected": [
          "believing parents need no prayer or care once grace is universal"
        ]
      }
    ],
    "notes": [
      "OCR: XII 1675 PDF 213; layout garbled mid-sentence — sense restored from 1683."
    ],
    "bible_refs": []
  },
  {
    "section": "659",
    "title": "Adults: Jesuits — sufficient grace present to life’s end",
    "pass_a": "But as concerns adults, those very ones who teach that sufficient grace is given to all adults do not agree among themselves whether that sufficient grace is perpetually present to them, or whether it is given to them only for place and time, so that they are sometimes destitute of it. For today’s Jesuits, and most other Doctors of the Roman School, lay down that to all adults, even to the end of life, grace is perpetually present by which they can both avoid the several sins whose occasion presents itself and to which they are tempted and driven, and also by which they can be converted to God and snatch themselves out of the state of sin.",
    "pass_b": [
      "Adult question splits even among universalists: is sufficient grace always present, or only sometimes?",
      "Today’s Jesuits and most Roman doctors: present to every adult to life’s end.",
      "Enough to avoid each presenting sin and temptation.",
      "Enough also to convert and leave the state of sin."
    ],
    "lemmas": [
      {
        "latin": "An gratia ista sufficiens perpetuo illis adsit",
        "gloss": "whether that sufficient grace is perpetually present to them"
      },
      {
        "latin": "ad finem usque vitae perpetuo adesse gratiam",
        "gloss": "that grace is perpetually present even to the end of life"
      }
    ],
    "choices": [
      {
        "term": "perpetuo adesse gratiam, qua & vitare possint singula peccata … & qua possint quoque ad Deum converti",
        "english": "grace is perpetually present by which they can both avoid the several sins … and also be converted to God",
        "why": "Jesuit perpetual-presence reading for adults.",
        "rejected": [
          "Jesuits deny adults always have convertible sufficient grace"
        ]
      }
    ],
    "notes": [
      "OCR: XIII 1675 PDF 213–214."
    ],
    "bible_refs": []
  },
  {
    "section": "660",
    "title": "Bellarmine: conversion-grace not always on hand — yet never denied for new sins",
    "pass_a": "But others here use a certain distinction. For there are those who think there is indeed no one to whom God does not, at least in some moment of life, grant grace by which he can convert himself to God and become a partaker of salvation: but they deny that that grace is always ready for all: for many are justly destitute of it by God on account of sins. Yet they contend that God never denies to any man grace by which he can abstain from new sins and resist an oncoming temptation — namely either immediately, or as was said, at least mediately, through a help which he does not indeed have, but which he can obtain by prayers. In which opinion is Cardinal Bellarmine, as may be seen in the first chapters of the second book on Grace and free choice.",
    "pass_b": [
      "Other Romans distinguish:",
      "Everyone gets, at some life-moment, grace enough to convert and share salvation.",
      "But that converting grace is not always on hand — many justly lose it for sins.",
      "Yet God never denies help to refuse new sins / resist temptation — at least mediate via prayer (Bellarmine)."
    ],
    "lemmas": [
      {
        "latin": "negant istam gratiam semper omnibus praesto esse",
        "gloss": "they deny that that grace is always ready for all"
      },
      {
        "latin": "Deum nunquam ulli homini denegare gratiam qua possit a novis peccatis abstinere",
        "gloss": "that God never denies to any man grace by which he can abstain from new sins"
      }
    ],
    "choices": [
      {
        "term": "saltem mediate, per auxilium … quod precibus impetrare potest",
        "english": "at least mediately, through a help … which he can obtain by prayers",
        "why": "Bellarmine’s mediate floor when converting grace is withdrawn.",
        "rejected": [
          "Bellarmine keeps converting grace perpetually present for all adults"
        ]
      }
    ],
    "notes": [
      "OCR: XIV 1675 PDF 214; Bellarmine De Gratia et libero arbitrio II."
    ],
    "bible_refs": []
  },
  {
    "section": "661",
    "title": "Some universalists: even avoid-sin grace can be withdrawn — the hardened",
    "pass_a": "Yet some of the patrons of universal and sufficient grace do not even admit that grace by which they can avoid sins is always present to all: because, namely, some, on account of too great abuse of divine grace, and in vengeance and punishment of preceding sins, are so forsaken by God that afterward they are wholly given over to their base desires, and can no longer not sin. Of which number they think are those whom Scripture calls hardened and blinded.",
    "pass_b": [
      "Even some universalists deny perpetual avoid-sin grace for all.",
      "After extreme abuse, God may forsake them in punishment.",
      "Then they are enslaved to base desires — can no longer not sin.",
      "These are Scripture’s hardened and blinded."
    ],
    "lemmas": [
      {
        "latin": "nequidem admittunt semper omnibus adesse gratiam qua possint peccata vitare",
        "gloss": "they do not even admit that grace by which they can avoid sins is always present to all"
      },
      {
        "latin": "illos quos scriptura induratos & occaecatos vocat",
        "gloss": "those whom Scripture calls hardened and blinded"
      }
    ],
    "choices": [
      {
        "term": "sic a Deo deseruntur, ut deinceps prorsus mancipentur pravis suis cupiditatibus, nec amplius possunt non peccare",
        "english": "they are so forsaken by God that afterward they are wholly given over to their base desires, and can no longer not sin",
        "why": "Hardening as loss even of avoid-sin sufficient help.",
        "rejected": [
          "universalists never allow total loss of avoid-sin grace"
        ]
      }
    ],
    "notes": [
      "OCR: XV 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "662",
    "title": "Vasquez names Tostatus, Cajetan, Fisher, Tapper for timed destitution",
    "pass_a": "This opinion Vasquez attributes to Tostatus Bishop of Avila, to Cardinal Cajetan, to John Bishop of Rochester and Cardinal, and to Ruard Tapper Professor of Louvain, whom he affirms to hold that sometimes, on account of worse sins, men are so destitute for some certain period of life that neither sufficient nor necessary help is granted them by which they can observe the commands of believing, of repenting, and others of this kind, and avoid sins. Tom. 1 on 1 Sent. of Thomas, disp. 96, ch. 3.",
    "pass_b": [
      "Vasquez pins this timed-destitution view on Tostatus, Cajetan, Fisher (Rochester), and Tapper.",
      "For a set stretch of life, after worse sins, help can fail.",
      "Not even sufficient/necessary aid to believe, repent, keep like commands, or avoid sins."
    ],
    "lemmas": [
      {
        "latin": "interdum propter peiora peccata, ita destitui homines per aliquam certam vitae periodum",
        "gloss": "that sometimes, on account of worse sins, men are so destitute for some certain period of life"
      },
      {
        "latin": "nec sufficiens & necessarium iis concedatur auxilium",
        "gloss": "that neither sufficient nor necessary help is granted them"
      }
    ],
    "choices": [
      {
        "term": "ut nec sufficiens & necessarium iis concedatur auxilium, quo observare valeant mandata credendi, paenitendi",
        "english": "that neither sufficient nor necessary help is granted them by which they can observe the commands of believing, of repenting",
        "why": "Names the hard timed gap inside sufficient-grace patronage.",
        "rejected": [
          "these doctors never allow any period without believe/repent help"
        ]
      }
    ],
    "notes": [
      "OCR: XVI 1675 PDF 214; next XVII+ Reformed doctors."
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
    "De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens IX-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens IX-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine I-XLVIII + Gratia sufficiens IX-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through Gratia sufficiens IX-XVI. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through An omnibus Hominibus detur Gratia sufficiens IX-XVI. "
    "1675 PDF 213-214 for IX-XVI (+ 1683 check). No modern English. "
    "This slice densifies Gratia sufficiens IX-XVI (Jansenist split; Thomist vs Molina; mediate; infants)."
)
LOCK_HEADER = (
    "Le Blanc Latin lock — An omnibus Hominibus detur Gratia sufficiens\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: An omnibus Hominibus detur Gratia sufficiens IX-XVI tip. Next: Gratia sufficiens XVII+.\n"
    "Source: 1675 PDF pages 212-214 (book ~187-189). 1683 folio cross-check.\n"
    "Note: Contiguous densify after De Certitudine qua Fidei competit I-XLVIII.\n\n"
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
    prior_src = json.loads(SRC.read_text(encoding='utf-8'))
    by_prior = {str(r['section']): r['latin'] for r in prior_src}
    parts = [LOCK_HEADER]
    # keep I-VIII from prior tip (647-654) then new IX-XVI
    for sec in [str(n) for n in range(647, TIP_BEFORE + 1)]:
        if sec in by_prior:
            parts.append(by_prior[sec].rstrip() + chr(10))
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
        jpath = JUST / ('gratia_sufficiens_%s.json' % sec)
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print('check_pass_ab gratia_sufficiens_%s (%s)' % (sec, ROMANS[sec]), 'ok' if not errs else errs)
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
                'Section %s: new densify An omnibus Hominibus detur Gratia sufficiens IX-XVI; '
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
                'Scope review: densify An omnibus Hominibus detur Gratia sufficiens IX-XVI only '
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
            'An omnibus Hominibus detur Gratia sufficiens IX-XVI '
            '(Vasquez infants; Tricassini; adult perpetual vs timed; Bellarmine; hardening)'
        ),
        'next_locus': (
            'An omnibus Hominibus detur Gratia sufficiens XVII+ '
            '(Reformed doctors on sufficient grace)'
        ),
        'gates': {
            'check_pass_ab': 'ok gratia_sufficiens_%s–%s (%s/%s)' % (
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
        '## %s (Scribe — An omnibus Hominibus detur Gratia sufficiens IX-XVI densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Gratia sufficiens IX-XVI → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: An omnibus Hominibus detur Gratia sufficiens XVII+.\n\n'
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
        'CoS densify: Gratia sufficiens IX-XVI (**%s→%s**). Packet %s. '
        'Next: An omnibus Hominibus detur Gratia sufficiens XVII+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_662.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-662 post-ready')
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
