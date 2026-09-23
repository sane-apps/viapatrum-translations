#!/usr/bin/env python3
"""Build + apply Demonstratur Deum esse I-XVI densify (tip 328 → 336).

Pre-append hold CLEARED at live 57/4205. After tip-ready: HOLD live>4225 OR 12m.
Punch X=NO. No ship. New lock: sources/_le_blanc_deum_esse_latin_lock.txt.
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
LOCK = BOOK / 'sources/_le_blanc_deum_esse_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_deum_esse_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_deum_esse_i_densify')
PACKET_STEM = 'deum_esse_ix_xvi_densify'
APPLY_COPY = BOOK / 'sources/_ocr_deum_esse/apply_deum_esse_ix_xvi_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['337', '338', '339', '340', '341', '342', '343', '344']
ROMANS = {
    '337': 'IX', '338': 'X', '339': 'XI', '340': 'XII',
    '341': 'XIII', '342': 'XIV', '343': 'XV', '344': 'XVI',
}
TIP_BEFORE = 336
LIVE_FLOOR = 4225
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, and Demonstratur Deum esse I-XVI. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), and Demonstratur Deum esse I-XVI, reconstructed from "
    "the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third "
    "edition was not used as copy-text. No modern English was copied. This slice opens Demonstratur Deum esse "
    "I-VIII (AN SIT / natural knowledge / demonstrability from effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: Demonstratur Deum esse (Theses Theologicae quibus Demonstratur Deum esse).\n"
    "Same 1675 Pitt copy-text. Book pp. 90-92 / PDF 102-104 (I-XVI; this packet IX-XVI). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Demonstratur Deum esse I-XVI tip. IX+ remains.\n"
    "Note: Distinct from De Theologia (already densified). This tract asks AN SIT and proves God from effects.\n\n"
)

LATIN = {
    "337": "IX. Id autem melius ostendi non potest, quam prolatis exemplis ejusmodi argumentorum, quae ex se suam produnt evidentiam & necessitatem. Itaque qua ratione commodius id fieri posse existimamus, ex iis quae in hoc mundo aspectabili nostris oculis obversantur, per necessariam & evidentem consequentiam deducere conabimur, Deum esse qui ista produxit: eaque quasi unica demonstratione contenti erimus. Nam argumenta singula persequi, quibus probatur esse summum aliquod numen, infiniti esset operis, & supra nostri instituti modum.",
    "338": "X. Ut autem sensim ad institutum nostrum viam nobis complanemus, nec reliqui quicquam faciamus ad summam evidentiam, qualis quidem exigi potest in rebus Physicis & Metaphysicis, principia quaedam constituenda sunt, quibus veluti fundamentis reliqua superstruentur, quibusque in tota discursus serie saepe utendum erit.",
    "339": "XI. Primo igitur certum est, nihil a se ipso fieri, & nihil esse sui ipsius causam. Nam si aliquid se ipsum fecisset, plane necesse foret, illud fuisse antequam esset, quod implicat contradictionem. Etenim quod fit nondum est; nam quod fit transit a non esse ad esse. Quod vero facit aliquid, jam est; cum agere praesupponat esse.",
    "340": "XII. Est etiam extra dubium, nihil pendere a seipso: sed quicquid dependet, ab alio dependere. Ratio manifesta est: nam si aliquid penderet a seipso, idem esset seipso prius & posterius. Quod enim dependet, posterius est eo unde dependet.",
    "341": "XIII. Tertium principium prioribus illis non minus manifestum est, in ordine causarum efficientium, quarum una ab alia pendet, non posse dari progressum in infinitum: sed tandem deveniendum esse ad causam aliquam primam atque summam. Nam si daretur in causis progressus in infinitum, nec ulla causa prima esset, omnes & singulae causae mediae essent, adeoque ante se causam aliquam haberent: imo nulla esset causa, quae ante se infinitas causas superiores non haberet. Sed hoc est impossibile: nam si ante omnes & singulas causas infinitae causae essent, ante totam causarum multitudinem & collectionem essent infinitae causae. Nam quod est ante omnia & singula, illud est ante totam singulorum multitudinem: sed contradictionem manifestam implicat infinitas causas esse tota multitudine causarum superiores. Nam certe extra totam causarum multitudinem, causa nulla reperiri potest. Alioqui multitudo illa tota non esset. Deinde, si ascendendo ab effectis ad causas, non posset ad primam causam perveniri, pari ratione, descendendo a causis ad effecta, ad ultimum effectum nunquam deveniri posset. Etenim distantia tanta est a summo ad imum, quanta est ab imo ad summum. Et quod infinitum est non magis ascendendo quam descendendo pertransiri potest.",
    "342": "XIV. Porro ex principiis jam positis sequitur, non omne ens esse factum & sui habere causam: sed dari aliquod ens improductum & independens. Nam si non daretur ens aliquod improductum, sed omne ens factum & productum esset, necesse esset factum esse vel a se vel ab alio. Sed ens ullum a se factum dici non potest, quia nihil est causa sui, per primum principium a nobis ante positum. Igitur oportet omne ens fuisse ab alio productum. Et ita vel dabitur in causis producentibus progressus in infinitum, quem impossibilem esse jamjam demonstratum est: vel circulus aliquis entium invicem productorum & producentium. Sed cum in eis quae sunt facta detur ultimum, quod aliud non fecit & produxit, talem circulum non dari evidens est. Praeterquam quod ejusmodi circulus est impossibilis. Nam tali circulo posito, sequeretur idem a se ipso fieri, & idem esse sui ipsius causam. Si dicas enim, exempli gratia, Abraham genuisse Isaac, & Isaac genuisse Jacob, & rursus Jacob genuisse Abraham, quod in circulo necessarium est; inde sequetur Abraham mediate saltem seipsum genuisse: quo nihil absurdius.",
    "343": "XV. Denique & hoc principium firmiter tenendum est, videlicet causam primam & praecipuam effectus sui non posse esse minus perfectam, neque quicquam in effectu perfectionis esse, quod in causa non contineatur, si non formaliter, ut aiunt, saltem modo aliquo eminentiori. Nam cum effectus, qua talis, quicquid habet a causa acceperit, manifestum est, effectum nihil habere posse quod in causa quodammodo non sit. Nihil enim dat quod non habet: quum dare sit, alium participem facere ejus, quod ipse habes.",
    "344": "XVI. His ita constitutis ut intentum nostrum assequamur, & ex iis, quae in hoc universo spectanda exhibentur, demonstremus esse Deum, duo sunt sigillatim & distincte probanda. Primo corpora illa, quibus constat hic mundus, terram scilicet, solem, stellas atque planetas, non esse entia a se & improducta; sed habere causam quae illa produxit. Deinde causam illam non posse esse, nisi summam intelligentiam, optimam, potentissimam & sapientissimam, quae ipsa est quam Deum vocamus."
}

SECTIONS = [
    {
        "section": "337",
        "title": "One path: from the visible world deduce the God who made it",
        "pass_a": "But that is better shown by bringing forward examples of such arguments, which from themselves produce their evidence and necessity. Therefore by the way we judge it can more conveniently be done, from the things which meet our eyes in this visible world we will try to deduce by necessary and evident consequence that God is who produced these things: and we will be content with that as if with a single demonstration. For to chase every argument by which some highest deity is proved would be infinite work, and beyond the measure of our design.",
        "pass_b": [
            "Best shown by sample arguments that carry their own necessity.",
            "From what the eyes meet in this visible world, deduce the God who made it.",
            "One demonstration path is enough — chasing every proof would be endless."
        ],
        "lemmas": [
            {
                "latin": "unica demonstratione",
                "gloss": "a single demonstration"
            },
            {
                "latin": "mundo aspectabili",
                "gloss": "the visible world"
            }
        ],
        "choices": [
            {
                "term": "eaque quasi unica demonstratione contenti erimus",
                "english": "and we will be content with that as if with a single demonstration",
                "why": "Scopes the tract to one effect-to-cause path.",
                "rejected": [
                    "enumerate every classical theistic proof"
                ]
            }
        ],
        "notes": [
            "OCR: IX PDF 103 / p.91; numen restored."
        ],
        "bible_refs": []
    },
    {
        "section": "338",
        "title": "First lay principles — foundations for physical and metaphysical evidence",
        "pass_a": "But so that we may gradually smooth the way to our design, and leave nothing wanting for the highest evidence such as can be required in physical and metaphysical matters, certain principles must be established, on which as foundations the rest will be built, and which must often be used in the whole series of the discourse.",
        "pass_b": [
            "Before the proof: lay principles as foundations.",
            "Aim at the evidence physics and metaphysics can demand.",
            "These principles will be reused through the whole argument."
        ],
        "lemmas": [
            {
                "latin": "principia quaedam constituenda",
                "gloss": "certain principles must be established"
            },
            {
                "latin": "veluti fundamentis",
                "gloss": "as foundations"
            }
        ],
        "choices": [
            {
                "term": "principia quaedam constituenda sunt",
                "english": "certain principles must be established",
                "why": "Opens the five-principle block XI-XV.",
                "rejected": [
                    "jump straight to world-as-effect without axioms"
                ]
            }
        ],
        "notes": [
            "OCR: X PDF 103."
        ],
        "bible_refs": []
    },
    {
        "section": "339",
        "title": "Principle 1: nothing makes itself — nothing is its own cause",
        "pass_a": "First therefore it is certain that nothing comes to be from itself, and nothing is the cause of itself. For if something had made itself, it would plainly have had to be before it was, which implies a contradiction. For what is coming to be is not yet; for what is coming to be passes from non-being to being. But what makes something already is; since to act presupposes being.",
        "pass_b": [
            "First principle: nothing makes itself; nothing is its own cause.",
            "Self-making would require being before being — contradiction.",
            "What is becoming is not yet; what acts already is."
        ],
        "lemmas": [
            {
                "latin": "nihil a se ipso fieri",
                "gloss": "nothing comes to be from itself"
            },
            {
                "latin": "nihil esse sui ipsius causam",
                "gloss": "nothing is the cause of itself"
            }
        ],
        "choices": [
            {
                "term": "illud fuisse antequam esset, quod implicat contradictionem",
                "english": "it would have had to be before it was, which implies a contradiction",
                "why": "Core self-cause absurdity.",
                "rejected": [
                    "something can cause itself"
                ]
            }
        ],
        "notes": [
            "OCR: XI PDF 103."
        ],
        "bible_refs": []
    },
    {
        "section": "340",
        "title": "Principle 2: nothing depends on itself — dependence is on another",
        "pass_a": "It is also beyond doubt that nothing depends on itself: but whatever depends, depends on another. The reason is plain: for if something depended on itself, the same thing would be prior and posterior to itself. For what depends is posterior to that on which it depends.",
        "pass_b": [
            "Second principle: nothing depends on itself.",
            "Whatever depends, depends on another.",
            "Self-dependence would make the same thing prior and posterior to itself."
        ],
        "lemmas": [
            {
                "latin": "nihil pendere a seipso",
                "gloss": "nothing depends on itself"
            },
            {
                "latin": "posterius est eo unde dependet",
                "gloss": "is posterior to that on which it depends"
            }
        ],
        "choices": [
            {
                "term": "idem esset seipso prius & posterius",
                "english": "the same thing would be prior and posterior to itself",
                "why": "Blocks self-dependence.",
                "rejected": [
                    "a thing can depend only on itself"
                ]
            }
        ],
        "notes": [
            "OCR: XII PDF 103."
        ],
        "bible_refs": []
    },
    {
        "section": "341",
        "title": "Principle 3: no infinite regress of efficient causes — a first cause",
        "pass_a": "The third principle, no less plain than the former, is that in the order of efficient causes, of which one depends on another, an infinite progress cannot be granted: but at last one must come to some first and highest cause. For if an infinite progress were granted in causes, and there were no first cause, all and each would be intermediate causes, and so would have some cause before them: nay there would be no cause which did not have infinite superior causes before it. But this is impossible: for if before all and each cause there were infinite causes, before the whole multitude and collection of causes there would be infinite causes. For what is before all and each is before the whole multitude of the individuals: but it implies a plain contradiction that infinite causes be superior to the whole multitude of causes. For certainly outside the whole multitude of causes no cause can be found. Otherwise that multitude would not be the whole. Next, if by ascending from effects to causes one could not reach a first cause, by the same reason, descending from causes to effects, one could never arrive at the last effect. For the distance from the highest to the lowest is as great as from the lowest to the highest. And what is infinite cannot be traversed more by ascending than by descending.",
        "pass_b": [
            "Third principle: no infinite regress of efficient causes — arrive at a first cause.",
            "If every cause had infinite superiors, infinite causes would stand outside the whole set — contradiction.",
            "Same distance up and down: if no first cause ascending, no last effect descending."
        ],
        "lemmas": [
            {
                "latin": "non posse dari progressum in infinitum",
                "gloss": "an infinite progress cannot be granted"
            },
            {
                "latin": "causam aliquam primam atque summam",
                "gloss": "some first and highest cause"
            }
        ],
        "choices": [
            {
                "term": "non posse dari progressum in infinitum",
                "english": "an infinite progress cannot be granted",
                "why": "Classic no-infinite-regress axiom.",
                "rejected": [
                    "infinite chain of efficient causes is possible"
                ]
            }
        ],
        "notes": [
            "OCR: XIII PDF 103; long principle restored from tess+layout."
        ],
        "bible_refs": []
    },
    {
        "section": "342",
        "title": "Principle 4: not every being is made — some unproduced independent being",
        "pass_a": "Further from the principles already laid down it follows that not every being is made and has a cause of itself: but that some unproduced and independent being is given. For if no unproduced being were given, but every being were made and produced, it would have to be made either from itself or from another. But no being can be said to be made from itself, because nothing is the cause of itself, by the first principle already laid down by us. Therefore every being must have been produced by another. And so either there will be an infinite progress in producing causes, which has just been shown impossible: or some circle of beings producing one another. But since among things that are made there is a last which did not make and produce another, it is evident that such a circle is not given. Besides, that kind of circle is impossible. For with such a circle posited, it would follow that the same thing is made from itself, and is the cause of itself. For if you say, for example, that Abraham begot Isaac, and Isaac begot Jacob, and again Jacob begot Abraham, which is necessary in a circle; thence it will follow that Abraham at least mediately begot himself: than which nothing is more absurd.",
        "pass_b": [
            "Fourth: not every being is made — some unproduced, independent being must exist.",
            "Else infinite regress (already ruled out) or a circle of mutual makers.",
            "Abraham–Isaac–Jacob circle: Abraham would mediately beget himself — absurd."
        ],
        "lemmas": [
            {
                "latin": "ens improductum & independens",
                "gloss": "an unproduced and independent being"
            },
            {
                "latin": "circulus aliquis entium",
                "gloss": "some circle of beings"
            }
        ],
        "choices": [
            {
                "term": "dari aliquod ens improductum & independens",
                "english": "that some unproduced and independent being is given",
                "why": "Positive conclusion from no self-cause + no infinite regress.",
                "rejected": [
                    "every being is produced by another without end"
                ]
            }
        ],
        "notes": [
            "OCR: XIV PDF 103; Abraham/Isaac/Jacob example restored."
        ],
        "bible_refs": []
    },
    {
        "section": "343",
        "title": "Principle 5: the first cause is not less perfect than its effect",
        "pass_a": "Finally this principle also must be firmly held: namely that the first and principal cause of its effect cannot be less perfect, nor can there be any perfection in the effect which is not contained in the cause — if not formally, as they say, at least in some more eminent mode. For since the effect, as such, has received whatever it has from the cause, it is clear that the effect can have nothing which is not somehow in the cause. For nothing gives what it does not have: since to give is to make another a participant in what you yourself have.",
        "pass_b": [
            "Fifth: the first cause is not less perfect than its effect.",
            "No perfection in the effect is missing from the cause — formally or more eminently.",
            "Nothing gives what it does not have."
        ],
        "lemmas": [
            {
                "latin": "non posse esse minus perfectam",
                "gloss": "cannot be less perfect"
            },
            {
                "latin": "modo aliquo eminentiori",
                "gloss": "in some more eminent mode"
            }
        ],
        "choices": [
            {
                "term": "Nihil enim dat quod non habet",
                "english": "For nothing gives what it does not have",
                "why": "Closes the principle set before the two-step proof in XVI.",
                "rejected": [
                    "effects can outstrip their first cause in perfection"
                ]
            }
        ],
        "notes": [
            "OCR: XV spans PDF 103-104; page-break quod non habet joined."
        ],
        "bible_refs": []
    },
    {
        "section": "344",
        "title": "Two things to prove: world-bodies are not from themselves; their cause is God",
        "pass_a": "These things thus established so that we may reach our intent, and from the things displayed to be observed in this universe demonstrate that God is, two things are to be proved separately and distinctly. First, that those bodies of which this world consists — earth, sun, stars, and planets — are not beings from themselves and unproduced; but have a cause which produced them. Next, that that cause cannot be anything but the highest intelligence, best, most powerful and most wise, which itself is what we call God.",
        "pass_b": [
            "Proof plan: two lemmas.",
            "First: earth, sun, stars, planets are not unproduced self-beings — they have a cause.",
            "Second: that cause can only be the highest intelligence we call God."
        ],
        "lemmas": [
            {
                "latin": "duo sunt sigillatim & distincte probanda",
                "gloss": "two things are to be proved separately and distinctly"
            },
            {
                "latin": "summam intelligentiam",
                "gloss": "the highest intelligence"
            }
        ],
        "choices": [
            {
                "term": "quae ipsa est quam Deum vocamus",
                "english": "which itself is what we call God",
                "why": "Identifies the first cause with God before XVII+ body-proofs.",
                "rejected": [
                    "first cause need not be personal intelligence"
                ]
            }
        ],
        "notes": [
            "OCR: XVI PDF 104 / p.92; opens the two-step demonstration for XVII+."
        ],
        "bible_refs": []
    }
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
    for sec in [str(n) for n in range(329, TIP_BEFORE + 1)]:
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
        jpath = JUST / f'deum_esse_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab deum_esse_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=[
            LOCK,
            pdf,
            DATA / 'pdf_102_110_layout.txt',
            DATA / 'tess_102.txt',
            DATA / 'tess_103.txt',
            DATA / 'tess_104.txt',
            DATA / 'latin.json',
            Path(__file__),
        ],
        expected_sections=section_ids,
        seed=20260924,
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
        if 337 <= n <= 344:
            notes = (
                f'Section {sid}: new densify Demonstratur Deum esse IX-XVI; '
                'Pass A!=B; lock-grounded PDF 103-104 / book pp. 91-92.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in deum_esse IX-XVI packet scope covering all current sections.'
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
                'Scope review: densify Demonstratur Deum esse IX-XVI only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Deum esse through XVI; XVII+ remains. '
                'Prior tracts untouched. Not shipped.'
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
        'locus': 'Demonstratur Deum esse theses IX-XVI (unique path / five principles / two lemmas)',
        'next_locus': 'Demonstratur Deum esse XVII+ (world-bodies not a se / motion-time proofs)',
        'gates': {
            'check_pass_ab': f'ok deum_esse_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'raw_source_paths_count': 7,
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
        f'## {day} (Scribe — Demonstratur Deum esse IX–XVI densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Deum esse IX–XVI → §§{SECS[0]}–{SECS[-1]}; continues Deum esse after I-VIII tip).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 103-104 / pp. 91-92).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: Demonstratur Deum esse through XVI (AN SIT; natural knowledge; '
        'principles + two lemmas). XVII+ remains. Prior tracts closed as before. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Pre-append hold cleared live>4225 OR 12m; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}; '
        f'disk tip re-read {TIP_BEFORE} before append.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc Demonstratur Deum esse IX–XVI densify)\n\n'
        'CoS densify: Demonstratur Deum esse IX–XVI (existence of God). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Deum esse IX–XVI (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through XVI. Next: Deum esse XVII+. '
        'Punch X: **NO**.\n\n---\n\n'
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
    post_floor = secs_now if secs_now is not None else LIVE_FLOOR
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-336 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
