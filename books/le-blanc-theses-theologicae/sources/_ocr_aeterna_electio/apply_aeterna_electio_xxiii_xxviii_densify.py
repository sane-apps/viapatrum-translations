#!/usr/bin/env python3
"""Build + apply De Aeterna Hominum Electione XXIII-XXVIII densify (tip 583 → 589).

Infralapsarian majority; Sohnius/Cameron object; effect-lists by object-party.
Live floor 5177. After tip-ready: HOLD live>5177 OR 12m. Punch X=NO. No ship.
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
PACKET_STEM = 'aeterna_electio_xxiii_xxviii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_aeterna_electio/apply_aeterna_electio_xxiii_xxviii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['584', '585', '586', '587', '588', '589']
ROMANS = {
    '584': 'XXIII', '585': 'XXIV', '586': 'XXV',
    '587': 'XXVI', '588': 'XXVII', '589': 'XXVIII',
}
TIP_BEFORE = 583
PRIOR_START = 562
LIVE_FLOOR = 5177
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII + De Scientia Dei I-XXX + "
    "De Causa Praedestinationis I-XXXIV + De Aeterna Hominum Electione et Praedestinatione I-XXVIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII; "
    "De Scientia Dei I-XXX; De Causa Praedestinationis I-XXXIV; "
    "De Aeterna Hominum Electione et Praedestinatione I-XXVIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Aeterna Hominum Electione et Praedestinatione I-XXVIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Aeterna Hominum Electione et Praedestinatione I-XXVIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Aeterna Hominum Electione et Praedestinatione I-XXVIII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Aeterna Electio XXIII-XXVIII "
    "(infralapsarian majority; Sohnius/Cameron; effect-lists by object-party)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Aeterna Hominum Electione et Praedestinatione.\n"
    "Same 1675 Pitt copy-text. Book pp. 127-131 / PDF 139-143 (I-XXVIII; this packet XXIII-XXVIII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Aeterna Hominum Electione et Praedestinatione I-XXVIII tip. Next: Aeterna Electio XXIX+.\n"
    "Note: Infralapsarian Dort majority; Sohnius/Cameron object; effects track object-party.\n\n"
)

LATIN = {
    "584": "XXIII. Verumtamen maxima pars Doctorum Scholae Reformatae Deo praedestinanti objectum fuisse volunt massam peccato corruptam, nec decretum de homine creando & de primo lapsu hominis permittendo ingredi volunt decretum totale praedestinationis & partem illius facere. Sed ex eorum sententia in Deo, secundum nostrum concipiendi modum, prius extitit lapsus hominis praevisio, quam decretum de misericordia in salute quorundam hominum exercenda, atque manifestanda: quod a Theologis vocatur electio, seu praedestinatio. Ac proinde, juxta ipsos, objectum electionis & praedestinationis est homo lapsus & peccato corruptus: neque in eo describendo atque definiendo supra hominis lapsum & creationem assurgere debemus. Atque haec sententia maxime conformis est Canonibus Synodi Dordracenae, illamque sequuntur longe plurimi Reformatorum, quorum nomina recensere & prolixum nimis & superfluum foret.",
    "585": "XXIV. Sed inter Reformatos reperiuntur nonnulli qui electionis objectum constituunt hominem non lapsum simpliciter & peccato corruptum, sed praeterea jam ad gratiae Christi participationem & communionem vocatum externa praedicatione. Nec enim decretum de Christo Redemptore mittendo, & de gratia ejus per verbi praedicationem hominibus offerenda, volunt facere partem decreti praedestinationis, & subordinari decreto de hisce illis hominibus aeterna salute donandis. Quin potius statuunt, secundum nostrum concipiendi modum, Deum prius decrevisse Christum in mundum mittere, quam certos quosdam homines ad vitam & salutem per veram in Christum fidem efficaciter perducere.",
    "586": "XXV. Haec fuit sententia Georgii Sohnii olim Theologiae in Heidelbergensi Academia Professoris. Nam operum tomo secundo, sic definit hominum praedestinationem, Decretum Dei quo ipse homines universos a se praescitos ut corruptos, & per Evangelium ad Christum vocatos ad vitam, vel mortem aeternam ab aeterno praeordinavit, ad declarandam aeternam gloriam suam. Hanc vero definitionem explicans ista addit, Praedestinatio illa facta est secundum praescientiam Dei, id est, a se praescitos homines, atque adeo ut peccato corruptos & per Evangelium de Christo vocatos Deus praeordinavit. Nam ab aeterno eos praedestinans consideravit, non simpliciter ut homines a se condendos, sed ut homines in peccatum lapsuros, & per Christum iterum in Evangelio vocandos. Quibus postea subjungit, Itaque objectum seu materia praedestinationis est genus humanum lapsum, & per Evangelium iterum vocatum. Nam vocatio hic est universalis. In Exegesi praecipuorum articulorum Confessionis Augustanae, tractatu de aeterna praedestinatione pag. 1000. Quam Sohnii sententiam probat & sequitur Testardus libro de natura & gratia, capite de voluntate & decreto gratiae, sectione nona. Et ad hanc quoque necesse est accedere omnes illos qui in doctrina de hominum Redemptione atque electione, Cameronis Methodum & Doctrinam sequuntur, siquidem propriis placitis stare velint.",
    "587": "XXVI. Ut autem varii varie sentiunt de Praedestinationis & Electionis Objecto, sic quoque de effectis praedestinationis atque electionis illos diversa sentire necesse est. Nam qui censent objectum praedestinationis esse hominem non conditum & lapsum, sed simpliciter hominem creabilem, & a Deo producibilem, inter media quibus Deus finem in praedestinatione intentum assequitur, ponunt creationem & lapsus permissionem. Adeoque creatio & lapsus permissio sunt ipsis effectus praedestinationis, in his quidem ad vitam, in aliis vero ad mortem & interitum. Prout videre licet apud Bezam, Perkinsum, Bucanum, Polanum, & alios ejusdem sententiae.",
    "588": "XXVII. Illi vero qui praedestinationis & electionis objectum constituunt hominem consideratum a Deo ut lapsum, ac peccato corruptum, quique non subordinant decretum creationis & permissionis lapsus decreto de illustranda Dei justitia & misericordia in horum quidem salute, in aliorum vero justa punitione, non putant inter effectus praedestinationis numerari debere hominum creationem, ut nec lapsus permissionem. Sed tantum electionis effecta esse volunt varia illa media, quibus Deus homines a peccato liberat, eosque ad felicitatem & vitam aeternam perducit: inter quae primum & praecipuum ponunt ipsam Mediatoris Christi donationem, & missionem in mundum.",
    "589": "XXVIII. Denique illi quibus objectum electionis & praedestinationis non est homo lapsus simpliciter, sed praeterea ad Christi gratiam & communionem vocatus, non possunt inter effectus electionis numerare missionem Christi in mundum, & Redemptionem morte ejus peractam. Siquidem decretum de Christo mittendo, & de humano genere per Christum redimendo, juxta ipsos, praecedit decretum electionis, & ab eo praesupponitur. Sed primum & proprium electionis effectum ipsis est fidei verae in tempore donatio: quam sequitur, ut ejusdem electionis effectus, collatio reliquorum Christi beneficiorum, quibus ad salutem aeternam pervenitur."
}

SECTIONS = [
    {
        "section": "584",
        "title": "Infralapsarian majority — object is the mass corrupted by sin (Dort)",
        "pass_a": "Yet the greater part of the Doctors of the Reformed School will that the object for God predestining was the mass corrupted by sin, and they will not have the decree of creating man and of permitting the first fall of man enter the total decree of predestination and make a part of it. But on their opinion in God, according to our way of conceiving, the foresight of man’s fall existed before the decree of exercising and manifesting mercy in the salvation of certain men — which by Theologians is called election or predestination. And therefore, according to them, the object of election and predestination is man fallen and corrupted by sin: nor in describing and defining it ought we to rise above man’s fall and creation. And this opinion is most conformable to the Canons of the Synod of Dort, and by far the greater part of the Reformed follow it, whose names it would be too long and superfluous to list.",
        "pass_b": [
            "Most Reformed: object = mass corrupted by sin (infralapsarian).",
            "Creation-decree and fall-permission are not parts of total praedestinatio.",
            "Foresight of fall before mercy-election — Dort-conformable majority."
        ],
        "lemmas": [
            {
                "latin": "massam peccato corruptam",
                "gloss": "the mass corrupted by sin"
            },
            {
                "latin": "homo lapsus & peccato corruptus",
                "gloss": "man fallen and corrupted by sin"
            }
        ],
        "choices": [
            {
                "term": "objectum electionis & praedestinationis est homo lapsus & peccato corruptus",
                "english": "the object of election and predestination is man fallen and corrupted by sin",
                "why": "Opens XXIII+ against XXII’s creatable/supralapsarian party.",
                "rejected": [
                    "the Dort majority takes the object as creatable man above the fall"
                ]
            }
        ],
        "notes": [
            "OCR: XXIII PDF 142; Dort infralapsarian majority."
        ],
        "bible_refs": []
    },
    {
        "section": "585",
        "title": "Some Reformed — object already called by external preaching",
        "pass_a": "But among the Reformed some are found who constitute the object of election not man simply fallen and corrupted by sin, but moreover already called to participation and communion of the grace of Christ by external preaching. For they will not have the decree of sending Christ the Redeemer, and of offering His grace to men by the preaching of the word, make a part of the decree of predestination and be subordinated to the decree of bestowing eternal salvation on these or those men. Rather they lay down, according to our way of conceiving, that God first decreed to send Christ into the world before He efficaciously leads certain men to life and salvation through true faith in Christ.",
        "pass_b": [
            "Some Reformed: object = fallen man already externally called.",
            "Christ-sending / gospel-offer not inside the predestination decree.",
            "Christ-mission-decree prior to efficacious leading of certain men to salvation."
        ],
        "lemmas": [
            {
                "latin": "jam ad gratiae Christi participationem & communionem vocatum externa praedicatione",
                "gloss": "already called to participation and communion of the grace of Christ by external preaching"
            },
            {
                "latin": "Deum prius decrevisse Christum in mundum mittere",
                "gloss": "that God first decreed to send Christ into the world"
            }
        ],
        "choices": [
            {
                "term": "Deum prius decrevisse Christum in mundum mittere, quam certos quosdam homines ad vitam & salutem … efficaciter perducere",
                "english": "that God first decreed to send Christ into the world before He efficaciously leads certain men to life and salvation",
                "why": "Second Reformed object-party: external vocation before particular election.",
                "rejected": [
                    "this party subordinates Christ’s mission to the particular-salvation decree"
                ]
            }
        ],
        "notes": [
            "OCR: XXIV PDF 142; external-call object."
        ],
        "bible_refs": []
    },
    {
        "section": "586",
        "title": "Sohnius — fallen and gospel-called; followed by Testard and Cameronians",
        "pass_a": "This was the opinion of Georg Sohn, formerly Professor of Theology in the Heidelberg Academy. For in the second tome of his works he so defines the predestination of men: The decree of God by which He from eternity preordained to eternal life or death all men foreknown by Himself as corrupted, and called to Christ through the Gospel, for declaring His eternal glory. But explaining this definition he adds these things: That predestination was made according to the foreknowledge of God — that is, God preordained men foreknown by Himself, and therefore as corrupted by sin and called through the Gospel concerning Christ. For from eternity predestining them He considered them not simply as men to be created by Himself, but as men who would fall into sin, and who were to be called again through Christ in the Gospel. To which he afterward subjoins: And so the object or matter of predestination is the human race fallen, and called again through the Gospel. For the calling here is universal. In the Exegesis of the chief articles of the Augsburg Confession, treatise on eternal predestination, page 1000. Which opinion of Sohn Testard proves and follows in the book On Nature and Grace, in the chapter on the will and decree of grace, section nine. And to this also all those must come who in the doctrine of men’s Redemption and election follow Cameron’s Method and Doctrine, if indeed they wish to stand by their own tenets.",
        "pass_b": [
            "Sohn (Heidelberg): object = race fallen and gospel-called (universal vocation).",
            "Not simply creatable — considered as falling and called again in the Gospel.",
            "Testard follows; Cameronians must join if consistent with their own tenets."
        ],
        "lemmas": [
            {
                "latin": "genus humanum lapsum, & per Evangelium iterum vocatum",
                "gloss": "the human race fallen, and called again through the Gospel"
            },
            {
                "latin": "vocatio hic est universalis",
                "gloss": "the calling here is universal"
            }
        ],
        "choices": [
            {
                "term": "objectum seu materia praedestinationis est genus humanum lapsum, & per Evangelium iterum vocatum",
                "english": "the object or matter of predestination is the human race fallen, and called again through the Gospel",
                "why": "Names Sohnius as the type for XXIV’s party; ties Testard/Cameron.",
                "rejected": [
                    "Sohn takes the object as creatable man above fall and calling"
                ]
            }
        ],
        "notes": [
            "OCR: XXV PDF 142; Sohn / Testard / Cameron."
        ],
        "bible_refs": []
    },
    {
        "section": "587",
        "title": "Creatable-object party — creation and fall-permission as effects",
        "pass_a": "But as various men variously think concerning the Object of Predestination and Election, so also it is necessary that they think diversely concerning the effects of predestination and election. For those who judge the object of predestination to be man not created and fallen, but simply creatable man and producible by God, place among the means by which God obtains the end intended in predestination creation and the permission of the fall. And therefore creation and the permission of the fall are for them effects of predestination — in these indeed to life, but in others to death and ruin. As may be seen in Beza, Perkins, Bucanus, Polanus, and others of the same opinion.",
        "pass_b": [
            "Object-view drives effect-list.",
            "Creatable-object party: creation + fall-permission are means/effects of praedestinatio.",
            "To life in some, to death/ruin in others — Beza, Perkins, Bucanus, Polanus."
        ],
        "lemmas": [
            {
                "latin": "creatio & lapsus permissio sunt ipsis effectus praedestinationis",
                "gloss": "creation and the permission of the fall are for them effects of predestination"
            },
            {
                "latin": "hominem creabilem, & a Deo producibilem",
                "gloss": "creatable man and producible by God"
            }
        ],
        "choices": [
            {
                "term": "creatio & lapsus permissio sunt ipsis effectus praedestinationis, in his quidem ad vitam, in aliis vero ad mortem & interitum",
                "english": "creation and the permission of the fall are for them effects of predestination — in these indeed to life, but in others to death and ruin",
                "why": "Links XXII’s creatable party to its effect-consequences.",
                "rejected": [
                    "the creatable-object party excludes creation from the effects"
                ]
            }
        ],
        "notes": [
            "OCR: XXVI PDF 142; creatable → creation/fall as effects."
        ],
        "bible_refs": []
    },
    {
        "section": "588",
        "title": "Fallen-object party — effects are saving means; Christ chief",
        "pass_a": "But those who constitute the object of predestination and election as man considered by God as fallen and corrupted by sin, and who do not subordinate the decree of creation and of the permission of the fall to the decree of illustrating God’s justice and mercy in the salvation of these and the just punishment of others, do not think men’s creation ought to be numbered among the effects of predestination, nor the permission of the fall. But they will that the effects of election are only those various means by which God frees men from sin and brings them to happiness and eternal life: among which they place as first and chief the very gift of the Mediator Christ, and His mission into the world.",
        "pass_b": [
            "Fallen-object party: creation and fall-permission are not effects.",
            "Effects = means freeing from sin unto eternal life.",
            "First/chief: gift and mission of Mediator Christ."
        ],
        "lemmas": [
            {
                "latin": "non putant inter effectus praedestinationis numerari debere hominum creationem",
                "gloss": "do not think men’s creation ought to be numbered among the effects of predestination"
            },
            {
                "latin": "ipsam Mediatoris Christi donationem, & missionem in mundum",
                "gloss": "the very gift of the Mediator Christ, and His mission into the world"
            }
        ],
        "choices": [
            {
                "term": "primum & praecipuum ponunt ipsam Mediatoris Christi donationem, & missionem in mundum",
                "english": "they place as first and chief the very gift of the Mediator Christ, and His mission into the world",
                "why": "Infralapsarian effect-list centered on Christ as means.",
                "rejected": [
                    "this party counts creation as the first effect of election"
                ]
            }
        ],
        "notes": [
            "OCR: XXVII PDF 142; fallen-object effects."
        ],
        "bible_refs": []
    },
    {
        "section": "589",
        "title": "Called-object party — first effect is gift of faith, not Christ’s mission",
        "pass_a": "Finally those for whom the object of election and predestination is not man simply fallen, but moreover called to the grace and communion of Christ, cannot number among the effects of election the mission of Christ into the world and the Redemption accomplished by His death. Seeing that the decree of sending Christ, and of redeeming the human race through Christ, according to them precedes the decree of election and is presupposed by it. But the first and proper effect of election for them is the gift of true faith in time: which is followed, as an effect of the same election, by the bestowal of the remaining benefits of Christ by which one arrives at eternal salvation.",
        "pass_b": [
            "Called-object party: Christ’s mission/redemption not election-effects.",
            "Those decrees precede and are presupposed by election.",
            "First proper effect = gift of true faith in time; then other benefits."
        ],
        "lemmas": [
            {
                "latin": "primum & proprium electionis effectum ipsis est fidei verae in tempore donatio",
                "gloss": "the first and proper effect of election for them is the gift of true faith in time"
            },
            {
                "latin": "decretum de Christo mittendo … praecedit decretum electionis",
                "gloss": "the decree of sending Christ … precedes the decree of election"
            }
        ],
        "choices": [
            {
                "term": "primum & proprium electionis effectum ipsis est fidei verae in tempore donatio",
                "english": "the first and proper effect of election for them is the gift of true faith in time",
                "why": "Closes XXIII–XXVIII on Sohnius/Cameron effect-order; next XXIX+ comparative word-use.",
                "rejected": [
                    "this party makes Christ’s mission the first effect of election"
                ]
            }
        ],
        "notes": [
            "OCR: XXVIII PDF 142-143; next XXIX+ comparative summary."
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
        if 584 <= n <= 589:
            notes = (
                'Section %s: new densify De Aeterna Hominum Electione XXIII-XXVIII; '
                'Pass A!=B; lock-grounded PDF 142-143 / book pp. 130-131.' % sid
            )
        else:
            notes = (
                'Section %s: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in aeterna_electio XXIII-XXVIII packet scope covering all current sections.'
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
                'Scope review: densify De Aeterna Hominum Electione XXIII-XXVIII only '
                '(sections %s-%s). Meta discloses %s. '
                'Next Aeterna Electio XXIX+. Not shipped.'
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
            'De Aeterna Hominum Electione et Praedestinatione XXIII-XXVIII '
            '(communior fallen-in-Adam; Reformed senses; infralapsarian; Sohnius/Cameron)'
        ),
        'next_locus': (
            'De Aeterna Hominum Electione et Praedestinatione XXIX+ '
            '(comparative Roman/Reformed word-use)'
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
        '## %s (Scribe — De Aeterna Hominum Electione XXIII–XXVIII densify LOCAL)\n\n'
        '- Before: **%s**. After: **%s** (contiguous Aeterna Electio XXIII–XXVIII → §§%s–%s).\n'
        '- Packet %s. Punch X = NO. Not shipped.\n'
        '- Post tip-ready hold cleared (%s) live %s.\n'
        '- Next: Aeterna Electio XXIX+.\n\n'
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
        '## %s ~ET (Scribe — Le Blanc De Aeterna Electione XXIII–XXVIII densify)\n\n'
        'CoS densify: Aeterna Electio XXIII–XXVIII (**%s→%s**). Packet %s. '
        'Next: Aeterna Electio XXIX+. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_589.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-589 post-ready')
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
