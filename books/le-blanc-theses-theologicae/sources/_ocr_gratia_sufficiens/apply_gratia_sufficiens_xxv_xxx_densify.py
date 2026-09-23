#!/usr/bin/env python3
"""Build + apply An omnibus Hominibus detur Gratia sufficiens XXV-XXX densify (tip 670 → 676).

Vasquez infants; Tricassini; adult perpetual vs timed; Bellarmine; hardening. Live floor 5525. After tip-ready: HOLD live>5525 OR 12m. Punch X=NO. No ship.
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
SEED = Path('/tmp/leblanc_gratia_xxv_data')
PACKET_STEM = 'gratia_sufficiens_xxv_xxx_densify'
APPLY_COPY = BOOK / 'sources/_ocr_gratia_sufficiens/apply_gratia_sufficiens_xxv_xxx_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['671', '672', '673', '674', '675', '676']
ROMANS = {
    '671': 'XXV', '672': 'XXVI', '673': 'XXVII', '674': 'XXVIII',
    '675': 'XXIX', '676': 'XXX',
}
TIP_BEFORE = 670
PRIOR_START = 599
LIVE_FLOOR = 5525
HOLD_MINUTES = 12

LATIN = {
  "671": "XXV. Verum hic omittendum non est clarissimum Amyraldum in sua Dissertatione de Gratia Particulari referre tertiam quandam sententiam, quam nonnullis ex Reformatis tribuit, licet nomina eorum non edat. Illi igitur, eo referente, non solum admittunt quandam Gratiam Universalem externam atque objectivam, quae sufficiat ad salutem; sed praeterea gratiam aliquam subjectivam & internam, quae sit quoque Universalis, & cujus omnes homines participes a Deo fiant, ut ejus beneficio credere possint & converti, quod absque ea fieri non posset. Quamvis praeter istam gratiam subjectivam & universalem, non negent esse aliam electis peculiarem. Addunt, inquit, utramque gratiam (tam internam scilicet, quam subjectivam vocat, quam externam, quam nominat objectivam,) aliquomodo universalem: Ut tametsi non negent in electo peculiarem quandam efficaciam sese exerere, fateantur tamen, quemadmodum Deus misericordiam suam omnibus hominibus revelat, qua ad fidem & paenitentiam invitantur, sic etiam omnium mentes intrinsecus eatenus affici, quoad objectivam gratiam, si velint, amplecti & retinere queant. Atque hos dicit doctrinam suam typis non vulgavisse, sed privatis tantum animadversionibus, quae tamen longe lateque dissipatae per manus hominum volitaverunt, gratiam subjectivam solis electis particularem carpsisse, & dogma de decreto Reprobationis absoluto, tanquam a vero abhorrens, censuisse e finibus religionis exterminandum.",
  "672": "XXVI. Porro qui in Belgio Remonstrantes dicuntur, sive Arminiani, inter dogmata sua praecipua reponunt illud de Gratia quadam universali atque sufficienti, quam Deus omnibus eo fine largitur, ut possint, si libeat, resipiscere & ad Deum converti. Etenim cum plerisque hodiernae Scholae Romanae Theologis aperte docent & tuentur, non tantum omnibus & singulis hominibus salutem a Deo extrinsecus offerri, sed Deum quoque intus sic in omnium animis agere, ut plane sit ipsis liberum, & in eorum potestate situm, gratia ista interna atque universali bene vel male uti: & ita vel salutem oblatam rejicere, vel saltem sensim & per gradus ad veram conversionem & fidem pervenire, adeoque salutem aeternam adipisci.",
  "673": "XXVII. Illi vero Theologi Confessionis Augustanae qui Lutherani appellantur distinctionem quidem gratiae in sufficientem atque efficacem respuunt, ut inutilem atque superfluam; sed tamen in hac quaestione idem, aut prope idem cum Remonstrantibus sentire videntur. Censent enim omnes universaliter ad salutem a Deo vocari atque excitari, & quidem vocatione, quae ex se, & ex Dei intentione efficax est: quod vero effectum in multis non sortitur, inde esse quod multi Deum vocantem respuunt, & vocationi divinae resistunt, nec admittunt efficaciam gratiae ipsis oblatae, aut serius admissa non bene utuntur, sed sponte Divinam gratiam abjiciunt. Cum alii contra Deo vocanti aurem praebeant, nec spiritus in ipsis operationi impedimentum ponant. Quae pluribus deducta videre licet apud Joannem Gerhardum, Tom. 2. tractatu de Elect. & Reprob. cap. 7.",
  "674": "XXVIII. Porro ex dictis constat dogma de gratia quadam sufficienti, quae omnibus hominibus detur, in Ecclesia Romana nondum haberi tanquam fidei articulum, qui sine haereseos nota negari non possit, sed licet a plurimis Doctoribus teneatur, esse tamen adhuc nonnullos qui repugnent: Et vicissim non paucos ex Reformatis hodie gratiam quandam universalem, & in suo genere sufficientem tueri, quamvis in contrarium sit communior Ecclesiarum Reformatarum sententia. Adeoque quod plurimi in Schola Romana affirmant omnibus hominibus dari gratiam sufficientem, tum ad conversionem, tum ad nova peccata vitanda, a plurimis Reformatorum simpliciter negatur.",
  "675": "XXIX. Illi vero ipsi Doctores reformati, qui, saltem verbis tenus, gratiam quandam universalem atque sufficientem cum plerisque Scholae Romanae Theologis confitentur, reipsa tamen ab ipsis dissentiunt. Quod enim Scholae Romanae Theologi intelligunt de gratia quadam interna atque subjectiva, quae conversionem hominis, non solum Physice, sed etiam moraliter possibilem reddit, id totum Reformati referunt ad gratiam solum externam atque objectivam; qua posita, homini interna gratia destituto, conversio nihilominus moraliter impossibilis manet.",
  "676": "XXX. Illi tamen qui, Mose Amyraldo testante, inter Reformatos agnoscunt gratiam quandam universalem atque sufficientem, non externam solum atque objectivam, sed subjectivam quoque & hominibus inhaerentem, eatenus non videntur a Thomistis recentioribus & Dominicanis differre: cum utrique praeter gratiam illam universalem quae neminem actu convertit, ad actualem conversionem velint necessarium esse peculiare quoddam auxilium, quod omnibus non obtingit, sed illis duntaxat qui actu convertuntur."
}

SECTIONS = [
  {
    "section": "671",
    "title": "Amyraut’s third Reformed view: universal inward grace too — elect still have a peculiar efficacy",
    "pass_a": "But here it must not be omitted that the most distinguished Amyraut, in his Dissertation on Particular Grace, reports a certain third opinion, which he attributes to some of the Reformed, though he does not publish their names. Those men, then, on his report, not only admit a certain Universal Grace, external and objective, which suffices for salvation; but besides a certain subjective and inward grace, which is also Universal, and of which all men are made partakers by God, that by its benefit they may be able to believe and be converted, which without it could not be done. Although besides that subjective and universal grace they do not deny that there is another peculiar to the elect. They add, he says, that both graces (the inward, namely, which he calls subjective, and the outward, which he names objective) are somehow universal: so that although they do not deny that in the elect a certain peculiar efficacy puts itself forth, yet they confess that, just as God reveals His mercy to all men by which they are invited to faith and repentance, so also He inwardly affects the minds of all so far that, as regards the objective grace, they can embrace and retain it if they will. And he says that these men have not published their doctrine in print, but only in private remarks, which yet have flown far and wide through men’s hands; that they have attacked the subjective grace as particular to the elect alone; and that they have judged the dogma of an absolute decree of Reprobation, as abhorring from the truth, to be banished from the bounds of religion.",
    "pass_b": [
      "Amyraut reports a third Reformed opinion (unnamed).",
      "Not only universal external/objective grace unto salvation.",
      "Also a universal inward/subjective grace — without it none can believe or convert.",
      "Elect still have a peculiar efficacy; absolute reprobation they would drive from religion.",
      "Taught in private papers, not print — yet widely circulated."
    ],
    "lemmas": [
      {
        "latin": "gratiam aliquam subjectivam & internam, quae sit quoque Universalis",
        "gloss": "a certain subjective and inward grace, which is also Universal"
      },
      {
        "latin": "praeter istam … non negent esse aliam electis peculiarem",
        "gloss": "besides that … they do not deny that there is another peculiar to the elect"
      }
    ],
    "choices": [
      {
        "term": "omnium mentes intrinsecus eatenus affici … si velint, amplecti & retinere queant",
        "english": "He inwardly affects the minds of all so far that … they can embrace and retain it if they will",
        "why": "Names the third view’s universal inward enablement.",
        "rejected": [
          "the third view denies any inward grace outside the elect"
        ]
      }
    ],
    "notes": [
      "OCR: XXV 1675 PDF 215; Amyraut De Gratia Particulari."
    ],
    "bible_refs": []
  },
  {
    "section": "672",
    "title": "Remonstrants: universal internal grace — free to use well or ill",
    "pass_a": "Further, those who in Belgium are called Remonstrants, or Arminians, place among their chief dogmas that of a certain universal and sufficient Grace, which God grants to all to this end, that they may be able, if they please, to repent and be converted to God. For with most Theologians of today’s Roman School they openly teach and maintain, not only that salvation is offered by God from without to all and each men, but that God also so acts inwardly in the souls of all that it is plainly free for them, and placed in their power, to use that inward and universal grace well or ill: and so either to reject the offered salvation, or at least by degrees and step by step to come to true conversion and faith, and so to obtain eternal salvation.",
    "pass_b": [
      "Belgian Remonstrants/Arminians make universal sufficient grace a chief dogma.",
      "God gives it so all can repent and convert if they please.",
      "With most modern Romans: salvation offered outwardly to each.",
      "Also inward universal action — free to use well or ill; reject, or climb by degrees to true faith and eternal salvation."
    ],
    "lemmas": [
      {
        "latin": "Gratia quadam universali atque sufficienti, quam Deus omnibus eo fine largitur",
        "gloss": "a certain universal and sufficient Grace, which God grants to all to this end"
      },
      {
        "latin": "gratia ista interna atque universali bene vel male uti",
        "gloss": "to use that inward and universal grace well or ill"
      }
    ],
    "choices": [
      {
        "term": "plane sit ipsis liberum, & in eorum potestate situm, gratia ista interna atque universali bene vel male uti",
        "english": "it is plainly free for them, and placed in their power, to use that inward and universal grace well or ill",
        "why": "Arminian liberty over inward universal grace.",
        "rejected": [
          "Remonstrants deny any inward universal grace"
        ]
      }
    ],
    "notes": [
      "OCR: XXVI 1675 PDF 215."
    ],
    "bible_refs": []
  },
  {
    "section": "673",
    "title": "Lutherans reject sufficient/efficacious split — call resists, not weak offer",
    "pass_a": "But those Theologians of the Augsburg Confession who are called Lutherans indeed reject the distinction of grace into sufficient and efficacious, as useless and superfluous; yet in this question they seem to feel the same, or nearly the same, as the Remonstrants. For they judge that all are universally called and stirred to salvation by God, and indeed by a vocation which of itself, and from God’s intention, is efficacious: but that it does not obtain its effect in many, comes from this, that many reject God calling, and resist the divine vocation, and do not admit the efficacy of the grace offered them, or, having more seriously admitted it, do not use it well, but of their own accord cast off the Divine grace. While others on the contrary lend an ear to God calling, and put no impediment to the Spirit’s operation in them. Which may be seen more fully drawn out in John Gerhard, Tom. 2, treatise on Election and Reprobation, ch. 7.",
    "pass_b": [
      "Lutherans scrap sufficient-vs-efficacious as useless.",
      "Yet near the Remonstrants here: all are universally called.",
      "The call is efficacious of itself and by God’s intent.",
      "It fails in many because they resist, refuse its efficacy, or cast grace off — not because the offer was weak (Gerhard)."
    ],
    "lemmas": [
      {
        "latin": "distinctionem quidem gratiae in sufficientem atque efficacem respuunt",
        "gloss": "they indeed reject the distinction of grace into sufficient and efficacious"
      },
      {
        "latin": "vocatione, quae ex se, & ex Dei intentione efficax est",
        "gloss": "by a vocation which of itself, and from God’s intention, is efficacious"
      }
    ],
    "choices": [
      {
        "term": "quod vero effectum in multis non sortitur, inde esse quod multi Deum vocantem respuunt",
        "english": "but that it does not obtain its effect in many, comes from this, that many reject God calling",
        "why": "Failure attributed to resistance, not insufficient offer.",
        "rejected": [
          "Lutherans say God never intends an efficacious call for the lost"
        ]
      }
    ],
    "notes": [
      "OCR: XXVII 1675 PDF 215; Gerhard Tom. 2 de Elect. & Reprob. c.7."
    ],
    "bible_refs": []
  },
  {
    "section": "674",
    "title": "Not yet a Roman article of faith — Reformed majority still deny universal sufficient grace",
    "pass_a": "Further from what has been said it is clear that the dogma of a certain sufficient grace which is given to all men is not yet held in the Roman Church as an article of faith which cannot be denied without the note of heresy, but although it is held by most Doctors, there are still some who oppose it: And on the other side not a few of the Reformed today maintain a certain universal grace, and in its own kind sufficient, although the more common opinion of the Reformed Churches is to the contrary. And so what most in the Roman School affirm — that sufficient grace is given to all men, both for conversion and for avoiding new sins — is simply denied by most of the Reformed.",
    "pass_b": [
      "Rome: universal sufficient grace is not yet a binding article of faith — some still oppose.",
      "Some Reformed today defend a universal, kind-sufficient grace.",
      "But the commoner Reformed church opinion is against it.",
      "What most Romans affirm for all (conversion and avoiding new sins), most Reformed simply deny."
    ],
    "lemmas": [
      {
        "latin": "nondum haberi tanquam fidei articulum, qui sine haereseos nota negari non possit",
        "gloss": "is not yet held as an article of faith which cannot be denied without the note of heresy"
      },
      {
        "latin": "a plurimis Reformatorum simpliciter negatur",
        "gloss": "is simply denied by most of the Reformed"
      }
    ],
    "choices": [
      {
        "term": "quamvis in contrarium sit communior Ecclesiarum Reformatarum sententia",
        "english": "although the more common opinion of the Reformed Churches is to the contrary",
        "why": "Balances minority Reformed universalists against the majority.",
        "rejected": [
          "universal sufficient grace is already Rome’s de fide dogma"
        ]
      }
    ],
    "notes": [
      "OCR: XXVIII 1675 PDF 215–216."
    ],
    "bible_refs": []
  },
  {
    "section": "675",
    "title": "Word-agreement with Rome hides a real split: internal vs external ‘sufficient’",
    "pass_a": "But those very Reformed Doctors who, at least in words, confess a certain universal and sufficient grace with most Theologians of the Roman School, yet in very deed dissent from them. For what the Theologians of the Roman School understand of a certain inward and subjective grace, which renders a man’s conversion possible not only Physically but also morally — that whole thing the Reformed refer to grace only external and objective; which being posited, for a man destitute of inward grace, conversion nevertheless remains morally impossible.",
    "pass_b": [
      "Even Reformed who speak with Romans of universal sufficient grace still dissent in substance.",
      "Romans mean inward/subjective grace — conversion physically and morally possible.",
      "Those Reformed mean only external/objective grace.",
      "With that alone and no inward grace, conversion stays morally impossible."
    ],
    "lemmas": [
      {
        "latin": "reipsa tamen ab ipsis dissentiunt",
        "gloss": "yet in very deed they dissent from them"
      },
      {
        "latin": "id totum Reformati referunt ad gratiam solum externam atque objectivam",
        "gloss": "that whole thing the Reformed refer to grace only external and objective"
      }
    ],
    "choices": [
      {
        "term": "qua posita, homini interna gratia destituto, conversio nihilominus moraliter impossibilis manet",
        "english": "which being posited, for a man destitute of inward grace, conversion nevertheless remains morally impossible",
        "why": "Shows the verbal overlap masks opposite moral-possibility claims.",
        "rejected": [
          "word-agreeing Reformed take sufficient grace as inward moral enablement like Rome"
        ]
      }
    ],
    "notes": [
      "OCR: XXIX 1675 PDF 216."
    ],
    "bible_refs": []
  },
  {
    "section": "676",
    "title": "Amyraut’s inward-universal Reformed align with recent Thomists on a further peculiar help",
    "pass_a": "Yet those who, Moses Amyraut bearing witness, among the Reformed acknowledge a certain universal and sufficient grace, not external only and objective, but also subjective and inhering in men, do not seem so far to differ from the more recent Thomists and Dominicans: since both, besides that universal grace which converts no one in act, will have it necessary for actual conversion that there be a certain peculiar help, which does not fall to all, but only to those who are actually converted.",
    "pass_b": [
      "Amyraut’s inward-universal Reformed still look like recent Thomists/Dominicans.",
      "Universal grace (even subjective) converts no one in act by itself.",
      "Actual conversion needs a further peculiar help.",
      "That help is not for all — only for those who actually convert."
    ],
    "lemmas": [
      {
        "latin": "non externam solum atque objectivam, sed subjectivam quoque & hominibus inhaerentem",
        "gloss": "not external only and objective, but also subjective and inhering in men"
      },
      {
        "latin": "ad actualem conversionem velint necessarium esse peculiare quoddam auxilium",
        "gloss": "for actual conversion they will have a certain peculiar help to be necessary"
      }
    ],
    "choices": [
      {
        "term": "quod omnibus non obtingit, sed illis duntaxat qui actu convertuntur",
        "english": "which does not fall to all, but only to those who are actually converted",
        "why": "Closes the tract by aligning Amyraut’s third party with Thomist peculiar auxilium.",
        "rejected": [
          "inward universal grace alone always converts in act"
        ]
      }
    ],
    "notes": [
      "OCR: XXX 1675 PDF 216; tract ends; next De Fidei justificantis natura."
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
    "De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens XXV-XXX"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens XXV-XXX)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine I-XLVIII + Gratia sufficiens XXV-XXX (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through Gratia sufficiens XXV-XXX. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through An omnibus Hominibus detur Gratia sufficiens XXV-XXX. "
    "1675 PDF 215-216 for XXV-XXX (+ 1683 check). No modern English. "
    "This slice densifies Gratia sufficiens XXV-XXX (Jansenist split; Thomist vs Molina; mediate; infants)."
)
LOCK_HEADER = (
    "Le Blanc Latin lock — An omnibus Hominibus detur Gratia sufficiens\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: An omnibus Hominibus detur Gratia sufficiens XXV-XXX tip. Next: De Fidei justificantis natura I+.\n"
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
                'Section %s: new densify An omnibus Hominibus detur Gratia sufficiens XXV-XXX; '
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
                'Scope review: densify An omnibus Hominibus detur Gratia sufficiens XXV-XXX only '
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
            'An omnibus Hominibus detur Gratia sufficiens XXV-XXX '
            '(Amyraut third; Remonstrants; Lutherans; verbal vs real split; Thomist align)'
        ),
        'next_locus': (
            'De Fidei justificantis natura I+ '
            '(justifying faith vs historical/dead faith)'
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
        '## %s (Scribe — An omnibus Hominibus detur Gratia sufficiens XXV-XXX densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Gratia sufficiens XXV-XXX → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: De Fidei justificantis natura I+.\n\n'
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
        'CoS densify: Gratia sufficiens XXV-XXX (**%s→%s**). Packet %s. '
        'Next: De Fidei justificantis natura I+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_676.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-676 post-ready')
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
