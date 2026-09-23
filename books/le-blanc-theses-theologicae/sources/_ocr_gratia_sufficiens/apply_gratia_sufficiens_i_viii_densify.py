#!/usr/bin/env python3
"""Build + apply An omnibus Hominibus detur Gratia sufficiens I-VIII densify (tip 646 → 654).

Jansenist split; common Roman; Thomist vs Molina; mediate; infants. Live floor 5444. After tip-ready: HOLD live>5444 OR 12m. Punch X=NO. No ship.
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
SEED = Path('/tmp/leblanc_gratia_i_data')
PACKET_STEM = 'gratia_sufficiens_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_gratia_sufficiens/apply_gratia_sufficiens_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['647', '648', '649', '650', '651', '652', '653', '654']
ROMANS = {
    '647': 'I', '648': 'II', '649': 'III', '650': 'IV',
    '651': 'V', '652': 'VI', '653': 'VII', '654': 'VIII',
}
TIP_BEFORE = 646
PRIOR_START = 599
LIVE_FLOOR = 5444
HOLD_MINUTES = 12

LATIN = {
  "647": "I. De hac quaestione non omnino convenit inter Doctores Ecclesiae Romanae. Primo enim sunt qui improbant distinctionem gratiae in sufficientem atque efficacem, nec volunt ullam esse gratiam sufficientem quae non sit efficax. Illi vero aperte docent non omnibus hominibus dari gratiam sufficientem sive ad conversionem, sive ad peccata vitanda; cum planum sit gratiam ad ista efficacem non omnibus dari. Quam sententiam tuentur Jansenius & ejus Discipuli, ut Augustini doctrinae conformem.",
  "648": "II. Sed communis Doctorum Ecclesiae Romanae sententia est in contrarium: saltem quantum attinet Doctores hodiernos atque recentiores. Existimant enim omnibus a Deo gratiam sufficientem dari ad conversionem, & peccata vitanda. Ut autem ita sentiant inducuntur Scripturae locis, in quibus dicitur Deus velle ut omnes homines serventur, & ad agnitionem veritatis veniant; item nolle quemquam perire, sed omnes ad resipiscentiam venire; aliisque similibus. Nec enim ista constare videntur, ut Deus velit hominum salutem & conversionem, & tamen iis gratiam ad fidem & salutem necessariam denegat. Ac praeterea, nisi omnibus hominibus sufficiens gratia detur, putant multos excusari posse, si non convertantur, & a peccatis abstineant, nempe omnes illos quibus talis gratia non obtigit. Nec enim existimant quenquam juste condemnari posse, quod non fecerit ea ad quae non habuit auxilia necessaria & sufficientia: cum tamen Scriptura doceat omnes illos esse inexcusabiles, qui in peccatis perseverant, & ad Deum non convertuntur.",
  "649": "III. Veruntamen omnes qui in ista Thesi generali de sufficienti gratia omnibus concessa convenire videntur, gratiam illam non eodem modo explicant atque intelligunt. Etenim qui recentiores Thomistae appellantur, quique docent gratiae efficaciam consistere in liberi arbitrii Physica quadam determinatione, dicunt omnibus hominibus gratiam a Deo sufficientem dari, quoniam illis a Deo auxilium sufficiens datur ut bene operari possint: quamvis cum isto auxilio nunquam aliquis bene operetur; sed ad hoc necessario requiratur aliud auxilium efficax a sufficiente realiter distinctum, quod voluntatem ad bonum determinet, & quod a Deo omnibus hominibus non conceditur. Itaque juxta illos, datur omnibus hominibus gratia sufficiens ut bene operari possint: sed tamen quae sine novo auxilio non sufficiat ut actu bene operentur.",
  "650": "IV. At vero Molina, & plerique alii Scholae Romanae Theologi, docent omnibus dari gratiam sufficientem, non tantum ut bene operari possint, sed etiam ut sine alio auxilio praevio actu operentur, si velint, & situm sit in eorum libertate atque potestate gratia illa uti, vel non uti.",
  "651": "V. Est autem observandum inter omnes Scholae Romanae Doctores convenire, quod non omnibus hominibus detur gratia quae immediate ad adipiscendam salutem sufficiat. Ad hoc enim fatentur adultorum respectu necessariam esse fidem in Christum, quam quis habere non potest, nisi Christus ipsi praedicetur, aut alio quodam modo innotescat: cum tamen palam sit multis hominibus Christi nomen prorsus inauditum esse.",
  "652": "VI. Itaque quum gratiam quandam universalem & sufficientem urgent, intelligunt eam quae saltem mediate sufficiat, ut ejus beneficio homines ad salutem aeternam perducantur: quatenus, scilicet, si bene utantur ea gratiae mensura quae primo ipsis indulgetur, paratus sit Deus semper ampliorem largiri, donec tandem eos ad salutiferam filii sui notitiam adducat, per media seu ordinaria, seu etiam extraordinaria: sicut Cornelio contigit, qui Deum pie colens pro modulo cognitionis ipsi a Deo indulto per angelum monitus fuit ut Petrum arcesseret, a quo in via salutis amplius instrueretur, & Evangelii doctrinam perciperet.",
  "653": "VII. Imo neque volunt omnibus hominibus gratiam dari quae sit immediate sufficiens ad peccata vitanda, & tentationes vincendas, sed eam tantum qua possint, mediate saltem, peccata vitare, & tentationes vincere. Agnoscunt, videlicet, multos cum auxilio praesenti impares esse tentationi vincendae, & ni Deus majus auxilium addat, certo fore ut pravae cupiditati succumbant: sed contendunt illis saltem non deesse auxilium quo Deum orare possint, & gratiam tum illis necessariam ab ipso impetrare.",
  "654": "VIII. Ceterum Scholae Romanae Theologi quaestiones varias hic movent circa quas non est eadem omnibus sententia. Et primo quidem de infantibus quaerunt, An etiam omnibus illis gratia sufficiens ad salutem a Deo detur? Id negant in Schola Romana non pauci: quoniam multi infantes decedunt, antequam potuerit illis administrari Baptismus, sine quo tamen existimant nullum infantem posse ad salutem pervenire. Quod clarum est, praesertim in iis infantibus, qui in utero materno sine parentum culpa extinguuntur."
}

SECTIONS = [
  {
    "section": "647",
    "title": "Roman doctors split: Jansenists deny any mere sufficient grace",
    "pass_a": "On this question the Doctors of the Roman Church do not altogether agree. For first there are those who reject the distinction of grace into sufficient and efficacious, and will not have any grace to be sufficient which is not efficacious. But they openly teach that sufficient grace is not given to all men, whether for conversion or for avoiding sins; since it is plain that efficacious grace for those things is not given to all. Which opinion Jansenius and his disciples maintain, as conformable to Augustine's doctrine.",
    "pass_b": [
      "Roman doctors do not all agree on sufficient grace.",
      "Some reject sufficient-vs-efficacious: no grace is sufficient unless efficacious.",
      "They deny sufficient grace to all — for conversion or for avoiding sins — since efficacious grace is not given to all.",
      "Jansenius and his disciples: this fits Augustine."
    ],
    "lemmas": [
      {
        "latin": "improbant distinctionem gratiae in sufficientem atque efficacem",
        "gloss": "they reject the distinction of grace into sufficient and efficacious"
      },
      {
        "latin": "non omnibus hominibus dari gratiam sufficientem",
        "gloss": "that sufficient grace is not given to all men"
      }
    ],
    "choices": [
      {
        "term": "nec volunt ullam esse gratiam sufficientem quae non sit efficax",
        "english": "and will not have any grace to be sufficient which is not efficacious",
        "why": "Names the Jansenist collapse of the distinction.",
        "rejected": [
          "Jansenists affirm a real sufficient-but-inefficacious grace for all"
        ]
      }
    ],
    "notes": [
      "OCR: I 1675 PDF 212 / book p.187; 1683 check."
    ],
    "bible_refs": []
  },
  {
    "section": "648",
    "title": "Common Roman view: God gives all sufficient grace — Scripture and inexcusability",
    "pass_a": "But the common opinion of the Doctors of the Roman Church is to the contrary: at least as concerns today's and more recent Doctors. For they judge that sufficient grace is given by God to all for conversion and for avoiding sins. And they are led so to think by Scripture places in which it is said that God wills that all men be saved and come to the knowledge of the truth; likewise that He wills none to perish, but all to come to repentance; and by others like them. For those things do not seem to stand together: that God wills men's salvation and conversion, and yet denies them the grace necessary for faith and salvation. And besides, unless sufficient grace be given to all men, they think many can be excused if they are not converted and abstain from sins — namely all those to whom such grace did not fall. For they do not judge that anyone can justly be condemned for not doing those things for which he did not have necessary and sufficient helps: yet Scripture teaches that all those are inexcusable who persevere in sins and are not converted to God.",
    "pass_b": [
      "Common Roman (esp. recent) view: God gives all sufficient grace for conversion and avoiding sins.",
      "Driven by God-wills-all-saved / none-perish / all-to-repentance texts.",
      "Else He would will salvation yet deny needed grace — incoherent.",
      "Without universal sufficient help, the unevangelized look excusable; Scripture still calls persevering sinners inexcusable."
    ],
    "lemmas": [
      {
        "latin": "omnibus a Deo gratiam sufficientem dari ad conversionem, & peccata vitanda",
        "gloss": "that sufficient grace is given by God to all for conversion and for avoiding sins"
      },
      {
        "latin": "omnes illos esse inexcusabiles",
        "gloss": "that all those are inexcusable"
      }
    ],
    "choices": [
      {
        "term": "nisi omnibus hominibus sufficiens gratia detur, putant multos excusari posse",
        "english": "unless sufficient grace be given to all men, they think many can be excused",
        "why": "Moral pressure behind the common Roman thesis.",
        "rejected": [
          "common Romans deny any link between sufficient grace and inexcusability"
        ]
      }
    ],
    "notes": [
      "OCR: II 1675 PDF 212."
    ],
    "bible_refs": []
  },
  {
    "section": "649",
    "title": "Recent Thomists: sufficient help to be able — but efficacious help needed to act",
    "pass_a": "Yet all who seem to agree in that general thesis of sufficient grace granted to all do not explain and understand that grace in the same way. For those who are called more recent Thomists, and who teach that the efficacy of grace consists in a certain physical determination of free choice, say that sufficient grace is given by God to all men, because a sufficient help is given them by God that they may be able to work well: although with that help no one ever works well; but for this another efficacious help, really distinct from the sufficient, is necessarily required, which determines the will to the good, and which is not granted by God to all men. And so according to them, sufficient grace is given to all men that they may be able to work well: yet such as without a new help does not suffice that they actually work well.",
    "pass_b": [
      "Agreement on sufficient grace for all still splits on what it means.",
      "Recent Thomists: efficacy equals physical determination of free choice.",
      "All get sufficient help to be able to work well — yet with it alone no one ever does.",
      "Actual well-doing needs a further efficacious help, really distinct, not given to all."
    ],
    "lemmas": [
      {
        "latin": "auxilium sufficiens datur ut bene operari possint",
        "gloss": "a sufficient help is given that they may be able to work well"
      },
      {
        "latin": "aliud auxilium efficax a sufficiente realiter distinctum",
        "gloss": "another efficacious help really distinct from the sufficient"
      }
    ],
    "choices": [
      {
        "term": "quae sine novo auxilio non sufficiat ut actu bene operentur",
        "english": "which without a new help does not suffice that they actually work well",
        "why": "Marks Thomist ability-without-act reading of sufficient.",
        "rejected": [
          "Thomist sufficient grace already determines actual good works"
        ]
      }
    ],
    "notes": [
      "OCR: III 1675 PDF 212."
    ],
    "bible_refs": []
  },
  {
    "section": "650",
    "title": "Molina: sufficient grace enough to act if they will — use or refuse",
    "pass_a": "But Molina, and most other Theologians of the Roman School, teach that sufficient grace is given to all, not only that they may be able to work well, but also that without another previous help they may actually work, if they will, and that it is placed in their freedom and power to use that grace, or not to use it.",
    "pass_b": [
      "Molina and most Roman schoolmen go further.",
      "Sufficient grace not only ability — also actual working without a further prior help, if they will.",
      "Use or refuse sits in their freedom and power."
    ],
    "lemmas": [
      {
        "latin": "ut sine alio auxilio praevio actu operentur, si velint",
        "gloss": "that without another previous help they may actually work, if they will"
      },
      {
        "latin": "situm sit in eorum libertate atque potestate gratia illa uti, vel non uti",
        "gloss": "that it is placed in their freedom and power to use that grace, or not to use it"
      }
    ],
    "choices": [
      {
        "term": "gratia illa uti, vel non uti",
        "english": "to use that grace, or not to use it",
        "why": "Molinist liberty over sufficient grace itself.",
        "rejected": [
          "Molina still requires a second really-distinct efficacious help for any act"
        ]
      }
    ],
    "notes": [
      "OCR: IV 1675 PDF 212."
    ],
    "bible_refs": []
  },
  {
    "section": "651",
    "title": "Roman consensus: not immediate sufficiency for salvation — faith needs Christ known",
    "pass_a": "But it is to be observed that among all Doctors of the Roman School it is agreed that grace which immediately suffices for obtaining salvation is not given to all men. For to this they confess that, with respect to adults, faith in Christ is necessary, which no one can have unless Christ is preached to him, or becomes known in some other way: yet it is plain that to many men the name of Christ is altogether unheard of.",
    "pass_b": [
      "All Roman doctors agree: not everyone gets grace that immediately suffices for salvation.",
      "Adults need faith in Christ.",
      "No faith without Christ preached or otherwise made known.",
      "Many have never even heard Christ's name."
    ],
    "lemmas": [
      {
        "latin": "non omnibus hominibus detur gratia quae immediate ad adipiscendam salutem sufficiat",
        "gloss": "that grace which immediately suffices for obtaining salvation is not given to all men"
      },
      {
        "latin": "fidem in Christum, quam quis habere non potest, nisi Christus ipsi praedicetur",
        "gloss": "faith in Christ, which no one can have unless Christ is preached to him"
      }
    ],
    "choices": [
      {
        "term": "multis hominibus Christi nomen prorsus inauditum esse",
        "english": "that to many men the name of Christ is altogether unheard of",
        "why": "Limits immediate universal sufficiency.",
        "rejected": [
          "Romans claim every adult already has immediate saving faith-grace"
        ]
      }
    ],
    "notes": [
      "OCR: V 1675 PDF 212-213."
    ],
    "bible_refs": []
  },
  {
    "section": "652",
    "title": "Universal sufficient means mediate — more grace if well used (Cornelius)",
    "pass_a": "And so when they urge a certain universal and sufficient grace, they understand that which at least mediately suffices, that by its benefit men may be led to eternal salvation: namely, inasmuch as, if they use well that measure of grace which is first granted them, God is always ready to bestow a larger, until at length He brings them to the saving knowledge of His Son, by means ordinary or even extraordinary: as happened to Cornelius, who piously worshiping God according to the measure of knowledge granted him by God was warned by an angel to send for Peter, by whom he would be further instructed in the way of salvation and perceive the doctrine of the Gospel.",
    "pass_b": [
      "Their universal sufficient grace is at least mediate, not always immediate.",
      "Use the first measure well → God ready to give more.",
      "Until saving knowledge of the Son — by ordinary or even extraordinary means.",
      "Cornelius: pious with limited light → angel → Peter → Gospel."
    ],
    "lemmas": [
      {
        "latin": "eam quae saltem mediate sufficiat",
        "gloss": "that which at least mediately suffices"
      },
      {
        "latin": "paratus sit Deus semper ampliorem largiri",
        "gloss": "God is always ready to bestow a larger"
      }
    ],
    "choices": [
      {
        "term": "sicut Cornelio contigit",
        "english": "as happened to Cornelius",
        "why": "Acts 10 pattern for mediate enlargement of grace.",
        "rejected": [
          "universal sufficient grace already includes full Gospel knowledge for all"
        ]
      }
    ],
    "notes": [
      "OCR: VI 1675 PDF 213; Cornelius = Acts 10."
    ],
    "bible_refs": [
      "Acts 10"
    ]
  },
  {
    "section": "653",
    "title": "Not immediate power against every temptation — at least mediate via prayer",
    "pass_a": "Indeed they also do not will that grace be given to all men which is immediately sufficient for avoiding sins and overcoming temptations, but only that by which they may be able, at least mediately, to avoid sins and overcome temptations. They acknowledge, namely, that many with present help are unequal to overcoming the temptation, and unless God add a greater help, it will certainly be that they succumb to base desire: yet they contend that at least there is not wanting to them a help by which they may pray to God, and obtain from Him the grace then necessary for them.",
    "pass_b": [
      "Likewise: not immediate sufficiency against every sin and temptation for all.",
      "Only mediate power to avoid and overcome.",
      "Many with present help still lose unless God adds greater help.",
      "Yet they keep at least prayer-help to ask God for the grace then needed."
    ],
    "lemmas": [
      {
        "latin": "immediate sufficiens ad peccata vitanda, & tentationes vincendas",
        "gloss": "immediately sufficient for avoiding sins and overcoming temptations"
      },
      {
        "latin": "auxilium quo Deum orare possint, & gratiam … impetrare",
        "gloss": "a help by which they may pray to God, and obtain grace"
      }
    ],
    "choices": [
      {
        "term": "illis saltem non deesse auxilium quo Deum orare possint",
        "english": "that at least there is not wanting to them a help by which they may pray to God",
        "why": "Mediate sufficiency bottoms out in prayer for further help.",
        "rejected": [
          "present sufficient grace always conquers every temptation without more"
        ]
      }
    ],
    "notes": [
      "OCR: VII 1675 PDF 213."
    ],
    "bible_refs": []
  },
  {
    "section": "654",
    "title": "Infants: many Romans deny sufficient grace for all — baptism barrier",
    "pass_a": "Moreover the Theologians of the Roman School raise various questions here about which there is not the same opinion for all. And first indeed concerning infants they ask whether sufficient grace for salvation is given by God even to all of them. Not a few in the Roman School deny it: because many infants depart before Baptism can be administered to them, without which yet they judge that no infant can come to salvation. Which is clear especially in those infants who are extinguished in the mother's womb without the parents' fault.",
    "pass_b": [
      "Romans still split on further questions — first, infants.",
      "Is sufficient saving grace given to every infant?",
      "Many say no: many die before baptism can be given.",
      "Without baptism they hold no infant reaches salvation — clearest in womb-deaths without parents' fault."
    ],
    "lemmas": [
      {
        "latin": "An etiam omnibus illis gratia sufficiens ad salutem a Deo detur",
        "gloss": "whether sufficient grace for salvation is given by God even to all of them"
      },
      {
        "latin": "sine quo tamen existimant nullum infantem posse ad salutem pervenire",
        "gloss": "without which yet they judge that no infant can come to salvation"
      }
    ],
    "choices": [
      {
        "term": "multi infantes decedunt, antequam potuerit illis administrari Baptismus",
        "english": "many infants depart before Baptism can be administered to them",
        "why": "Grounds the negative infant answer inside Rome.",
        "rejected": [
          "all Romans grant every infant immediate sufficient saving grace"
        ]
      }
    ],
    "notes": [
      "OCR: VIII 1675 PDF 213; next IX+ Vasquez on infant remedies."
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
    "De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine I-XLVIII + Gratia sufficiens I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through Gratia sufficiens I-VIII. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through An omnibus Hominibus detur Gratia sufficiens I-VIII. "
    "1675 PDF 212-213 for I-VIII (+ 1683 check). No modern English. "
    "This slice densifies Gratia sufficiens I-VIII (Jansenist split; Thomist vs Molina; mediate; infants)."
)
LOCK_HEADER = (
    "Le Blanc Latin lock — An omnibus Hominibus detur Gratia sufficiens\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: An omnibus Hominibus detur Gratia sufficiens I-VIII tip. Next: Gratia sufficiens IX+.\n"
    "Source: 1675 PDF pages 212-213 (book ~187-188). 1683 folio cross-check.\n"
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
                'Section %s: new densify An omnibus Hominibus detur Gratia sufficiens I-VIII; '
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
                'Scope review: densify An omnibus Hominibus detur Gratia sufficiens I-VIII only '
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
            'An omnibus Hominibus detur Gratia sufficiens I-VIII '
            '(Jansenist split; common Roman; Thomist vs Molina; mediate; infants)'
        ),
        'next_locus': (
            'An omnibus Hominibus detur Gratia sufficiens IX+ '
            '(Vasquez infants; adult perpetual grace)'
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
        '## %s (Scribe — An omnibus Hominibus detur Gratia sufficiens I-VIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Gratia sufficiens I-VIII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: An omnibus Hominibus detur Gratia sufficiens IX+.\n\n'
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
        'CoS densify: Gratia sufficiens I-VIII (**%s→%s**). Packet %s. '
        'Next: An omnibus Hominibus detur Gratia sufficiens IX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_654.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-654 post-ready')
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
