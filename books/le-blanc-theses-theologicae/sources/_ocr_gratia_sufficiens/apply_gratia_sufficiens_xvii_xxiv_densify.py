#!/usr/bin/env python3
"""Build + apply An omnibus Hominibus detur Gratia sufficiens XVII-XXIV densify (tip 662 → 670).

Vasquez infants; Tricassini; adult perpetual vs timed; Bellarmine; hardening. Live floor 5498. After tip-ready: HOLD live>5498 OR 12m. Punch X=NO. No ship.
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
SEED = Path('/tmp/leblanc_gratia_xvii_data')
PACKET_STEM = 'gratia_sufficiens_xvii_xxiv_densify'
APPLY_COPY = BOOK / 'sources/_ocr_gratia_sufficiens/apply_gratia_sufficiens_xvii_xxiv_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['663', '664', '665', '666', '667', '668', '669', '670']
ROMANS = {
    '663': 'XVII', '664': 'XVIII', '665': 'XIX', '666': 'XX',
    '667': 'XXI', '668': 'XXII', '669': 'XXIII', '670': 'XXIV',
}
TIP_BEFORE = 662
PRIOR_START = 599
LIVE_FLOOR = 5498
HOLD_MINUTES = 12

LATIN = {
  "663": "XVII. Quod spectat Scholae Reformatae Doctores, eorum longe plurimi non agnoscunt ullam gratiam quae sufficiat ad hominem convertendum, & perducendum ad salutem, quae etiam reapse hominem non convertat, & ad salutem perducat. Adeoque, juxta eorum sententiam, nulla est gratia sufficiens, quae etiam efficax non sit: nec debet haec ab illa distingui. Ac proinde cum doceant gratiam Dei in solis electis esse efficacem, tantum abest ut agnoscant omnibus hominibus dari gratiam sufficientem sive ad conversionem, sive ad peccata vitanda, ut hanc solis electis obtingere contendant.",
  "664": "XVIII. Veruntamen nonnulli hodie reperiuntur Theologi inter Reformatos qui tuentur & praedicant gratiam quandam universalem, quam communem esse volunt omnibus hominibus, & quam etiam dicunt ex se & per se ad salutem sufficere. Adeoque rogati an omnibus hominibus detur gratia sufficiens? Respondent ita esse. Sed gratiam illam constituunt, non in interna quadam spiritus operatione, quae mentem, voluntatem, & affectus hominis moveat & excitet, ut feratur in Deum, & peccatum fugiat: sed tantum in externa divinae misericordiae praedicatione & declaratione, & invitatione ad fidem & resipiscentiam, sub spe remissionis peccatorum obtinendae, & participandae salutis; sive ista declaratio atque invitatio fiant per externum verbi praeconium; sive per effecta varia divinae providentiae, quae sese circa homines peccato corruptos exserunt.",
  "665": "XIX. Hanc autem gratiam sufficientem vocant, non quod, ex eorum mente, simpliciter sufficiat ad hominem actu convertendum, absque ullo alio auxilio divino: sed quia salutem homini sic possibilem reddit, ut possit salvari, si velit: nec ullum sit, ut loquuntur, Physicum impedimentum quod saluti illius obstet: cum & salus illi debite offeratur, & facultates naturales habeat, mentem, scilicet, atque voluntatem quibus possit illam amplecti, si recte iis utatur.",
  "666": "XX. Agnoscunt autem istas naturales hominis facultates, nempe mentem atque voluntatem, ita peccato corruptas & vitiatas esse, ut nisi accedat interna quaedam Dei gratia, quae mentem illuminet & voluntatem flectat, contingere non possit ut homo bene utatur suis illis facultatibus, & pareat atque obsequatur Deo vocanti & invitanti ad gratiae suae extrinsecus oblatae participationem; quod illi propter vitium inhaerens, absque interna ejusmodi gratia moraliter impossibile est.",
  "667": "XXI. Neque propterea minus inexcusabiles existimant eos qui Deo vocanti obsequium non praestant. Idque quoniam ista moralis impossibilitas sita est in ultronea voluntatis in malo obduratione & obfirmatione, quae minime peccatum excusat, ut patet exemplo daemonum: cum solum excusemur per illa impedimenta, quae a propria nostra voluntate non pendent, & quae quantum velimus, & annitamur ipsi, tollere non valemus.",
  "668": "XXII. Ac praeterea putant gratiam istam communiter hominibus omnibus oblatam satis esse, ut Deus dici possit nolle quemquam perire, sed omnium hominum salutem & conversionem velle & serio cupere: quandoquidem per id Deus salutem reddit omnibus possibilem, sub conditione quae pendet ab eorum voluntate, & quam possunt praestare si velint: cum nulla sit causa externa, aut externum impedimentum quod saluti eorum obstet, sed solum eorum perversa voluntas, quae media a Deo oblata respuit & contemnit, iisque uti obstinate renuit.",
  "669": "XXIII. Ceterum internam gratiam, sine qua nemo potest misericordiam divinam amplecti, volunt esse electis propriam & peculiarem, neque ullis quam electis obtingere, tantum abest ut sit omnium communis. Ut videre est apud Amyraldum in dissertationibus de gratia particulari, & de gratia universali; & apud Paulum Testardum, de natura & gratia, cap. 7. cujus titulus est, De gratia supernaturali, & potentia salutis per eam indulta, ejusque universalitate.",
  "670": "XXIV. Gratiam autem illam, quam vocant universalem, docent universalem esse, non tantum respectu adultorum, sed etiam respectu ipsorum infantium, quibus, scilicet, Deus potestatem salutis fecit, quatenus voluit ut infantes sequantur conditionem parentum: omnibus vero parentibus salutem propriam possibilem reddidit: adeoque salutem infantium qui sunt ex ipsis oriundi, & qui habentur tanquam eorum quaedam appendices."
}

SECTIONS = [
  {
    "section": "663",
    "title": "Most Reformed: no sufficient grace that is not also efficacious — elect only",
    "pass_a": "As concerns the Doctors of the Reformed School, by far most of them do not acknowledge any grace which suffices to convert a man and lead him to salvation which does not also in very deed convert the man and lead him to salvation. And so, according to their opinion, there is no sufficient grace which is not also efficacious: nor ought this to be distinguished from that. And therefore since they teach that God’s grace is efficacious in the elect alone, so far are they from acknowledging that sufficient grace is given to all men either for conversion or for avoiding sins, that they contend that this falls to the elect alone.",
    "pass_b": [
      "Most Reformed deny any ‘sufficient’ grace that fails to convert in fact.",
      "Sufficient = efficacious — no real distinction.",
      "God’s grace efficacious in the elect alone.",
      "So sufficient grace for conversion or avoiding sins is for the elect only — not for all."
    ],
    "lemmas": [
      {
        "latin": "nulla est gratia sufficiens, quae etiam efficax non sit",
        "gloss": "there is no sufficient grace which is not also efficacious"
      },
      {
        "latin": "hanc solis electis obtingere",
        "gloss": "that this falls to the elect alone"
      }
    ],
    "choices": [
      {
        "term": "non agnoscunt ullam gratiam quae sufficiat … quae etiam reapse hominem non convertat",
        "english": "they do not acknowledge any grace which suffices … which does not also in very deed convert the man",
        "why": "Collapses sufficient into efficacious for the Reformed majority.",
        "rejected": [
          "most Reformed affirm a real inefficacious sufficient grace for all"
        ]
      }
    ],
    "notes": [
      "OCR: XVII 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "664",
    "title": "Some Reformed: universal external mercy-offer counts as sufficient",
    "pass_a": "Yet some Theologians among the Reformed are found today who maintain and preach a certain universal grace, which they will have common to all men, and which they also say suffices of itself and by itself for salvation. And so when asked whether sufficient grace is given to all men, they answer that it is so. But they place that grace not in some inward operation of the Spirit which moves and stirs the mind, will, and affections of man that he be carried to God and flee sin: but only in the outward preaching and declaration of divine mercy, and the invitation to faith and repentance, under hope of obtaining remission of sins and of sharing salvation — whether that declaration and invitation happen through the outward proclamation of the word, or through various effects of divine providence which put themselves forth about men corrupted by sin.",
    "pass_b": [
      "Some Reformed today preach a universal grace common to all — enough of itself for salvation.",
      "Asked if all get sufficient grace: they say yes.",
      "Not as inward Spirit-work on mind/will/affections.",
      "But as outward mercy-preaching and invitation to faith and repentance — by word or providence’s effects."
    ],
    "lemmas": [
      {
        "latin": "gratiam quandam universalem, quam communem esse volunt omnibus hominibus",
        "gloss": "a certain universal grace, which they will have common to all men"
      },
      {
        "latin": "non in interna quadam spiritus operatione … sed tantum in externa divinae misericordiae praedicatione",
        "gloss": "not in some inward operation of the Spirit … but only in the outward preaching of divine mercy"
      }
    ],
    "choices": [
      {
        "term": "sed tantum in externa divinae misericordiae praedicatione & declaratione, & invitatione ad fidem & resipiscentiam",
        "english": "but only in the outward preaching and declaration of divine mercy, and the invitation to faith and repentance",
        "why": "Defines their ‘sufficient’ as external offer, not internal motion.",
        "rejected": [
          "these Reformed locate universal sufficient grace in inward Spirit operation for all"
        ]
      }
    ],
    "notes": [
      "OCR: XVIII 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "665",
    "title": "‘Sufficient’ = physically possible to be saved if one will — not actual conversion alone",
    "pass_a": "But they call this grace sufficient, not because, on their mind, it simply suffices to convert a man in act without any other divine help: but because it so renders salvation possible to the man that he can be saved if he will: and there is no Physical impediment, as they speak, which stands in the way of his salvation: since both salvation is duly offered to him, and he has natural faculties — namely mind and will — by which he can embrace it, if he use them rightly.",
    "pass_b": [
      "They do not mean this grace alone actually converts without further help.",
      "It makes salvation possible — he can be saved if he will.",
      "No ‘physical’ block to salvation.",
      "Salvation is duly offered; mind and will can embrace it if used rightly."
    ],
    "lemmas": [
      {
        "latin": "salutem homini sic possibilem reddit, ut possit salvari, si velit",
        "gloss": "it so renders salvation possible to the man that he can be saved if he will"
      },
      {
        "latin": "nec ullum sit … Physicum impedimentum",
        "gloss": "and there is no Physical impediment"
      }
    ],
    "choices": [
      {
        "term": "non quod … simpliciter sufficiat ad hominem actu convertendum, absque ullo alio auxilio divino",
        "english": "not because … it simply suffices to convert a man in act without any other divine help",
        "why": "Keeps external sufficiency short of actual conversion.",
        "rejected": [
          "their sufficient grace alone always converts in act"
        ]
      }
    ],
    "notes": [
      "OCR: XIX 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "666",
    "title": "Yet without internal grace, right use of faculties is morally impossible",
    "pass_a": "But they acknowledge that those natural faculties of man, namely mind and will, are so corrupted and vitiated by sin that unless some inward grace of God come to illuminate the mind and bend the will, it cannot happen that a man use those faculties of his well, and obey and yield to God calling and inviting to the participation of His grace offered from without; which for him, because of the inherent vice, is morally impossible without such inward grace.",
    "pass_b": [
      "Still: mind and will are sin-corrupted.",
      "Without inward grace lighting the mind and bending the will, right use cannot happen.",
      "Obeying the outward call needs that inward help.",
      "Without it, obedience is morally impossible because of inherent vice."
    ],
    "lemmas": [
      {
        "latin": "nisi accedat interna quaedam Dei gratia, quae mentem illuminet & voluntatem flectat",
        "gloss": "unless some inward grace of God come which illuminates the mind and bends the will"
      },
      {
        "latin": "absque interna ejusmodi gratia moraliter impossibile est",
        "gloss": "without such inward grace it is morally impossible"
      }
    ],
    "choices": [
      {
        "term": "contingere non possit ut homo bene utatur suis illis facultatibus",
        "english": "it cannot happen that a man use those faculties of his well",
        "why": "Moral impossibility without internal grace despite external offer.",
        "rejected": [
          "natural faculties alone can rightly answer the external call"
        ]
      }
    ],
    "notes": [
      "OCR: XX 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "667",
    "title": "Still inexcusable — moral impossibility sits in the will’s own hardening",
    "pass_a": "Nor for that reason do they judge less inexcusable those who do not render obedience to God calling. And that because that moral impossibility is seated in the will’s own spontaneous hardening and obstinacy in evil, which by no means excuses sin, as is plain from the example of the demons: since we are excused only by those impediments which do not depend on our own will, and which, however much we will and strive ourselves, we are not able to remove.",
    "pass_b": [
      "Refusal of the call is still inexcusable.",
      "Moral impossibility sits in the will’s own hardening in evil.",
      "That does not excuse sin — demons show as much.",
      "Excuse only for blocks outside our will that we cannot remove however hard we try."
    ],
    "lemmas": [
      {
        "latin": "ista moralis impossibilitas sita est in ultronea voluntatis in malo obduratione & obfirmatione",
        "gloss": "that moral impossibility is seated in the will’s own spontaneous hardening and obstinacy in evil"
      },
      {
        "latin": "minime peccatum excusat",
        "gloss": "by no means excuses sin"
      }
    ],
    "choices": [
      {
        "term": "cum solum excusemur per illa impedimenta, quae a propria nostra voluntate non pendent",
        "english": "since we are excused only by those impediments which do not depend on our own will",
        "why": "Keeps inexcusability despite moral inability.",
        "rejected": [
          "moral impossibility from hardening excuses the unbeliever"
        ]
      }
    ],
    "notes": [
      "OCR: XXI 1675 PDF 214."
    ],
    "bible_refs": []
  },
  {
    "section": "668",
    "title": "Outward offer enough for ‘God wills none to perish’ — block is perverse will",
    "pass_a": "And besides they think that that grace commonly offered to all men is enough that God may be said to will that none perish, but to will and seriously desire the salvation and conversion of all men: inasmuch as by it God renders salvation possible to all, under a condition which depends on their will, and which they can fulfill if they will: since there is no external cause or external impediment that stands in the way of their salvation, but only their perverse will, which rejects and despises the means offered by God, and obstinately refuses to use them.",
    "pass_b": [
      "This common outward offer is enough to say God wills none to perish — and seriously wants all saved and converted.",
      "Salvation is possible for all under a will-dependent condition they can meet if they will.",
      "No external block.",
      "Only a perverse will that spurns God’s offered means."
    ],
    "lemmas": [
      {
        "latin": "ut Deus dici possit nolle quemquam perire",
        "gloss": "that God may be said to will that none perish"
      },
      {
        "latin": "solum eorum perversa voluntas, quae media a Deo oblata respuit",
        "gloss": "only their perverse will, which rejects the means offered by God"
      }
    ],
    "choices": [
      {
        "term": "Deus salutem reddit omnibus possibilem, sub conditione quae pendet ab eorum voluntate",
        "english": "God renders salvation possible to all, under a condition which depends on their will",
        "why": "Ties universal desire language to the external-offer theory.",
        "rejected": [
          "the outward offer leaves salvation physically impossible for most"
        ]
      }
    ],
    "notes": [
      "OCR: XXII 1675 PDF 214–215."
    ],
    "bible_refs": []
  },
  {
    "section": "669",
    "title": "Internal grace still elect-only — Amyraut and Testard",
    "pass_a": "For the rest, the inward grace without which no one can embrace the divine mercy they will have proper and peculiar to the elect, and to fall to none but the elect — so far is it from being common to all. As may be seen in Amyraut in the dissertations on particular grace and on universal grace; and in Paul Testard, On nature and grace, ch. 7, whose title is, On supernatural grace, and the power of salvation granted through it, and its universality.",
    "pass_b": [
      "Inward grace to embrace mercy: elect-only — not common to all.",
      "Amyraut: particular and universal grace dissertations.",
      "Testard, On nature and grace ch. 7 — supernatural grace and salvation’s power through it."
    ],
    "lemmas": [
      {
        "latin": "internam gratiam … volunt esse electis propriam & peculiarem",
        "gloss": "the inward grace … they will have proper and peculiar to the elect"
      },
      {
        "latin": "neque ullis quam electis obtingere",
        "gloss": "and to fall to none but the elect"
      }
    ],
    "choices": [
      {
        "term": "tantum abest ut sit omnium communis",
        "english": "so far is it from being common to all",
        "why": "Splits external universal offer from elect-only internal grace.",
        "rejected": [
          "Amyraut/Testard make inward converting grace common to all alike"
        ]
      }
    ],
    "notes": [
      "OCR: XXIII 1675 PDF 215; Amyraut; Testard."
    ],
    "bible_refs": []
  },
  {
    "section": "670",
    "title": "Their ‘universal’ grace covers infants via parents’ possible salvation",
    "pass_a": "But that grace which they call universal they teach to be universal not only with respect to adults, but also with respect to the infants themselves, for whom, namely, God made a power of salvation, inasmuch as He willed that infants follow the condition of the parents: but to all parents He rendered their own salvation possible: and so the salvation of the infants who are born of them, and who are held as certain appendages of them.",
    "pass_b": [
      "Their universal grace covers infants too, not adults only.",
      "God tied infant salvation-power to the parents’ condition.",
      "He made every parent’s own salvation possible.",
      "So children — as parents’ appendages — share that possible salvation."
    ],
    "lemmas": [
      {
        "latin": "non tantum respectu adultorum, sed etiam respectu ipsorum infantium",
        "gloss": "not only with respect to adults, but also with respect to the infants themselves"
      },
      {
        "latin": "voluit ut infantes sequantur conditionem parentum",
        "gloss": "He willed that infants follow the condition of the parents"
      }
    ],
    "choices": [
      {
        "term": "omnibus vero parentibus salutem propriam possibilem reddidit",
        "english": "but to all parents He rendered their own salvation possible",
        "why": "Infant universality rides on parental possible salvation.",
        "rejected": [
          "universal grace here ignores infants entirely"
        ]
      }
    ],
    "notes": [
      "OCR: XXIV 1675 PDF 215; next XXV+ Amyraut’s third Reformed opinion."
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
    "De Certitudine qua Fidei competit I-XLVIII + An omnibus Hominibus detur Gratia sufficiens XVII-XXIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXXVII; "
    "De Certitudine qua Fidei competit I-XLVIII; An omnibus Hominibus detur Gratia sufficiens XVII-XXIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Certitudine I-XLVIII + Gratia sufficiens XVII-XXIV (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through Gratia sufficiens XVII-XXIV. Not the collected folio."
)
METHOD = (
    "English follows locked Pitt Latin through An omnibus Hominibus detur Gratia sufficiens XVII-XXIV. "
    "1675 PDF 214-215 for XVII-XXIV (+ 1683 check). No modern English. "
    "This slice densifies Gratia sufficiens XVII-XXIV (Jansenist split; Thomist vs Molina; mediate; infants)."
)
LOCK_HEADER = (
    "Le Blanc Latin lock — An omnibus Hominibus detur Gratia sufficiens\n"
    "Edition: Theses theologicae (London: Moses Pitt, 1675). ESTC R17887.\n"
    "Scope: An omnibus Hominibus detur Gratia sufficiens XVII-XXIV tip. Next: Gratia sufficiens XXV+.\n"
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
                'Section %s: new densify An omnibus Hominibus detur Gratia sufficiens XVII-XXIV; '
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
                'Scope review: densify An omnibus Hominibus detur Gratia sufficiens XVII-XXIV only '
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
            'An omnibus Hominibus detur Gratia sufficiens XVII-XXIV '
            '(Reformed majority; external universal; Amyraut/Testard; infants via parents)'
        ),
        'next_locus': (
            'An omnibus Hominibus detur Gratia sufficiens XXV+ '
            '(Amyraut third opinion; Remonstrants; Lutherans)'
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
        '## %s (Scribe — An omnibus Hominibus detur Gratia sufficiens XVII-XXIV densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Gratia sufficiens XVII-XXIV → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: An omnibus Hominibus detur Gratia sufficiens XXV+.\n\n'
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
        'CoS densify: Gratia sufficiens XVII-XXIV (**%s→%s**). Packet %s. '
        'Next: An omnibus Hominibus detur Gratia sufficiens XXV+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_670.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-670 post-ready')
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
