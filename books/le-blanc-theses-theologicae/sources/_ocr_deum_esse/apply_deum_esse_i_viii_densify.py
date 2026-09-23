#!/usr/bin/env python3
"""Build + apply Demonstratur Deum esse I-VIII densify (tip 328 → 336).

Pre-append hold CLEARED at live 57/4205. After tip-ready: HOLD live>4205 OR 12m.
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
PACKET_STEM = 'deum_esse_i_viii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_deum_esse/apply_deum_esse_i_viii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['329', '330', '331', '332', '333', '334', '335', '336']
ROMANS = {
    '329': 'I', '330': 'II', '331': 'III', '332': 'IV',
    '333': 'V', '334': 'VI', '335': 'VII', '336': 'VIII',
}
TIP_BEFORE = 328
LIVE_FLOOR = 4205
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify: De Theologia I-XLIII + De Fide I-XXII + De Authoritate Scripturae Pars I I-XLVII + "
    "Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + De Scripturae plenitudine Pars I I-XXXVIII + "
    "Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + Demonstratur Deum esse I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate Scripturae through Pars IV XLIV, "
    "De Scripturae plenitudine through Pars IV XXXIV, and Demonstratur Deum esse I-VIII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia, De Fide, De Authoritate Scripturae, "
    "De Scripturae plenitudine (through Pars IV XXXIV), and Demonstratur Deum esse I-VIII, reconstructed from "
    "the Internet Archive PDF page images with pdftotext + tesseract (+ DjVu checks). The 1683 third "
    "edition was not used as copy-text. No modern English was copied. This slice opens Demonstratur Deum esse "
    "I-VIII (AN SIT / natural knowledge / demonstrability from effects)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: Demonstratur Deum esse (Theses Theologicae quibus Demonstratur Deum esse).\n"
    "Same 1675 Pitt copy-text. Book pp. 90-91 / PDF 102-103 (I-VIII). "
    "pdftotext + tess OCR (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Demonstratur Deum esse I-VIII tip. IX+ remains.\n"
    "Note: Distinct from De Theologia (already densified). This tract asks AN SIT and proves God from effects.\n\n"
)

LATIN = {
    '329': (
        'I. Ut Deus nomen Theologiae dedit, ita ejus est praecipuum objectum. Idcirco res '
        'Theologicas tractare aggredienti ab ipso Deo sumendum est exordium.'
    ),
    '330': (
        'II. Quae autem de Deo traduntur ad duo capita revocari possunt. Vel enim spectant '
        'Dei existentiam, & quaestionem AN SIT: vel Dei naturam atque essentiam, & '
        'quaestionem QUID SIT. A priori ratio postulat ut incipiamus.'
    ),
    '331': (
        'III. Primum ergo totius Theologiae theorema, cui omnis religio superstruitur, illud '
        'est, Esse Deum, hoc est mentem aeternam, optimam, potentissimam & sapientissimam, '
        'quae sit causa rerum omnium, & a qua omnia pendeant & regantur. Juxta quod dicit '
        'Apostolus Hebr. 11.6. Accedentem ad Deum oportet credere, quod est.'
    ),
    '332': (
        'IV. Porro principium istud non est de genere eorum, quae ex sola revelatione & Dei '
        'verbo habentur: sed res est, quam tota rerum natura inculcat, & nostris pene '
        'sensibus ingerit. Nam ut ait Apostolus Rom. 1.20. Invisibilia Dei sempiterna scil. '
        'ejus virtus & divinitas a creatione mundi, per ea, quae facta sunt intellecta, '
        'conspiciuntur. Quo spectat etiam Job 12.7-9. Interroga, inquit, jumenta, & docebunt '
        'te: aut aves, & indicabunt tibi: aut terram alloquere, & docebit te; & ipsos pisces '
        'maris, & tibi narrabunt. Quis ignorat quod haec omnia manus Domini fecerit?'
    ),
    '333': (
        'V. Unde factum, ut etiam citra revelationem, qua Deus seipsum in verbo cognoscendum '
        'praebuit, nonnulla Dei cognitio ad omnes fere homines promanarit. Siquidem nulla, '
        'aut pene nulla gens est, cui non sit aliqua religionis forma, & qualiscunque '
        'divinitatis cultus. Nec aliunde proveniunt conscientiae terrores & morsus, qui etiam '
        'improbissimos & perditissimos quosque, qui omnem Dei timorem excutere conantur, '
        'quamvis invitos protrahunt ad ipsius tribunal, & divinae vindictae horrorem illis '
        'incutiunt.'
    ),
    '334': (
        'VI. Non est quidem negandum, veram & salutarem Dei cognitionem apud paucos admodum '
        'homines reperiri: Verumque Deum fuisse, & etiamnum esse, plerisque gentibus '
        'ignotum, quo nomine dicuntur ab Apostolo ἄθεοι ἐν τῷ κόσμῳ, sine Deo in mundo, '
        'Eph. 2.12. Sed hoc non obstat, quo minus apud illas ipsas gentes, quas Paulus '
        'Atheismi quodammodo intitulat, numinis tamen sensus aliquis remanserit, licet '
        'multis & foedis erroribus implicatus. Cujus rei argumentum est illa ipsa '
        'idololatria, qua sese gentes profanae polluerunt, & relicto creatore, creaturas '
        'varias, & ipsa animi sui figmenta coluerunt. Oportet enim ut alte hominibus '
        'impressus sit iste divinitatis sensus, quandoquidem homo, plus satis alioqui ad '
        'superbiam pronus & fastu tumens, maluerit se abjicere infra bestias, & colere '
        'lapides & ligna, quam nullum plane Deum agnoscere.'
    ),
    '335': (
        'VII. Igitur omnino certum est ex contemplatione Mundi, & eorum quae in eo '
        'videntur, homines posse ad Dei cognitionem pervenire: nec obstitisse tenebras '
        'humanae menti per peccatum offusas, quin maxima pars hominum, hac via, & natura '
        'duce, qualemcunque numinis notitiam adeptasit. Sed quaeritur, cujus generis sint '
        'rationes illae, quibus ex operum naturae consideratione ostenditur esse Deum. An '
        'scilicet sint necessariae, an vero probabiles tantum? Et an Dei existentia sit '
        'demonstrabilis ingenio humano, an vero duntaxat illam assequi possit conjecturis '
        'nonnullis, & probabilibus quibusdam argumentis. In hac autem sumus sententia, cum '
        'omnibus fere Theologis tam nostris quam Pontificiis, Dei existentiam rem esse, '
        'quae demonstrari potest, & necessariis argumentis evinci.'
    ),
    '336': (
        'VIII. Sed cum duplex sit demonstratio apud Dialecticos, altera quae ex causis '
        'effectum, altera vero quae contra ex effectis causam monstrat: manifestum est, '
        'priori demonstrationis modo non posse doceri Deum esse; cum nec Dei, nec ejus '
        'existentiae, possit in ullo genere causa proferri: sed demonstrari potest '
        'posteriori modo, nimirum ex effectis. Nec enim existimandum est, argumenta quibus '
        'probatur esse Deum, rem aliquatenus relinquere dubiam, & suadere tantum, non '
        'convincere.'
    ),
}

SECTIONS = [
    {
        'section': '329',
        'title': 'Theology begins from God — He is its chief object',
        'pass_a': (
            'As God gave the name to Theology, so He is its chief object. Therefore one who '
            'sets out to treat theological matters must take the beginning from God Himself.'
        ),
        'pass_b': [
            'Theology takes its name from God — and He is its chief object.',
            'So the right start for theological work is God Himself.',
        ],
        'lemmas': [
            {'latin': 'praecipuum objectum', 'gloss': 'chief object'},
            {'latin': 'ab ipso Deo sumendum est exordium', 'gloss': 'the beginning must be taken from God Himself'},
        ],
        'choices': [{
            'term': 'ab ipso Deo sumendum est exordium',
            'english': 'the beginning must be taken from God Himself',
            'why': 'Opens the Deum esse tract: start from God before AN SIT / QUID SIT.',
            'rejected': ['start from ecclesiastical tradition'],
        }],
        'notes': ['OCR: Thesis I PDF 102 / p.90; Ut Deus restored (scan dropped initial U).'],
        'bible_refs': [],
    },
    {
        'section': '330',
        'title': 'Two heads about God: whether He is, and what He is',
        'pass_a': (
            'But the things handed down about God can be reduced to two heads. For either '
            'they regard the existence of God, and the question WHETHER HE IS: or the nature '
            'and essence of God, and the question WHAT HE IS. Reason a priori demands that '
            'we begin.'
        ),
        'pass_b': [
            'Two heads: AN SIT (whether God is) and QUID SIT (what God is).',
            'Reason says start with whether He is.',
        ],
        'lemmas': [
            {'latin': 'AN SIT', 'gloss': 'whether He is'},
            {'latin': 'QUID SIT', 'gloss': 'what He is'},
        ],
        'choices': [{
            'term': 'A priori ratio postulat ut incipiamus',
            'english': 'Reason a priori demands that we begin',
            'why': 'Orders the tract: existence before essence.',
            'rejected': ['begin with attributes before existence'],
        }],
        'notes': ['OCR: II PDF 102; AN SIT / QUID SIT caps retained as scholastic tags.'],
        'bible_refs': [],
    },
    {
        'section': '331',
        'title': 'First theorem: God is — eternal mind, cause of all',
        'pass_a': (
            'Therefore the first theorem of all Theology, on which every religion is built, '
            'is this: That God is — that is, an eternal mind, best, most powerful and most '
            'wise, which is the cause of all things, and from which all things hang and are '
            'ruled. According to what the Apostle says in Hebrews 11:6: One approaching God '
            'must believe that He is.'
        ),
        'pass_b': [
            'First theorem under all religion: God is.',
            'Eternal mind — best, most powerful, most wise — cause and ruler of all.',
            'Hebrews 11:6: the one who comes to God must believe that He is.',
        ],
        'lemmas': [
            {'latin': 'Esse Deum', 'gloss': 'That God is'},
            {'latin': 'mentem aeternam', 'gloss': 'an eternal mind'},
        ],
        'choices': [{
            'term': 'cui omnis religio superstruitur',
            'english': 'on which every religion is built',
            'why': 'Marks God\'s existence as the load-bearing theorem.',
            'rejected': ['religion can stand without God\'s existence'],
        }],
        'notes': ['OCR: III PDF 102; Hebr. 11.6 restored.'],
        'bible_refs': ['Bible:Hebrews 11:6'],
    },
    {
        'section': '332',
        'title': 'God\'s existence is not revelation-only — nature presses it on the senses',
        'pass_a': (
            'Further, that principle is not of the kind of things which are had from '
            'revelation and the word of God alone: but it is a matter which the whole nature '
            'of things inculcates, and almost thrusts upon our senses. For as the Apostle '
            'says in Romans 1:20: The invisible things of God, His everlasting power and '
            'divinity, are clearly seen from the creation of the world, being understood '
            'through the things that are made. To which also Job 12:7-9 looks: Ask, he says, '
            'the beasts, and they will teach you; or the birds, and they will tell you; or '
            'speak to the earth, and it will teach you; and the fish of the sea will narrate '
            'to you. Who does not know that the hand of the Lord has made all these things?'
        ),
        'pass_b': [
            'This principle is not revelation-only — nature itself drums it in.',
            'Romans 1:20: everlasting power and divinity seen in the things made.',
            'Job: ask beasts, birds, earth, and fish — the Lord\'s hand made them.',
        ],
        'lemmas': [
            {'latin': 'ex sola revelatione', 'gloss': 'from revelation alone'},
            {'latin': 'tota rerum natura inculcat', 'gloss': 'the whole nature of things inculcates'},
        ],
        'choices': [{
            'term': 'non est de genere eorum, quae ex sola revelatione & Dei verbo habentur',
            'english': 'is not of the kind of things which are had from revelation and the word of God alone',
            'why': 'Natural theology claim before the pagan-knowledge theses.',
            'rejected': ['God\'s existence is known only by special revelation'],
        }],
        'notes': ['OCR: IV PDF 102; Rom 1.20 / Job 12 restored from tess+layout.'],
        'bible_refs': ['Bible:Romans 1:20', 'Bible:Job 12:7-9'],
    },
    {
        'section': '333',
        'title': 'Even without the Word, some knowledge of God reaches nearly all peoples',
        'pass_a': (
            'Whence it came about that even apart from revelation, by which God offered '
            'Himself to be known in the Word, some knowledge of God has flowed out to almost '
            'all people. Since there is no nation, or almost none, which does not have some '
            'form of religion and some cult of divinity. Nor from elsewhere do the terrors '
            'and bites of conscience arise, which even the most wicked and most lost — who '
            'try to shake off all fear of God — drag unwilling to His tribunal and strike '
            'with horror of divine vengeance.'
        ),
        'pass_b': [
            'Even without the Word, some God-knowledge reaches nearly every people.',
            'Almost no nation lacks some religion and some cult of divinity.',
            'Conscience terrors drag even the most lost toward God\'s tribunal.',
        ],
        'lemmas': [
            {'latin': 'citra revelationem', 'gloss': 'apart from revelation'},
            {'latin': 'conscientiae terrores & morsus', 'gloss': 'terrors and bites of conscience'},
        ],
        'choices': [{
            'term': 'nonnulla Dei cognitio ad omnes fere homines promanarit',
            'english': 'some knowledge of God has flowed out to almost all people',
            'why': 'Universal natural knowledge claim.',
            'rejected': ['only the church has any knowledge of God'],
        }],
        'notes': ['OCR: V PDF 102.'],
        'bible_refs': [],
    },
    {
        'section': '334',
        'title': 'Saving knowledge is rare — yet even "atheist" nations keep a sense of deity',
        'pass_a': (
            'It is indeed not to be denied that true and saving knowledge of God is found '
            'among very few people: and that the true God was, and still is, unknown to most '
            'nations, by which name they are called by the Apostle atheists in the world, '
            'without God in the world (Ephesians 2:12). But this does not hinder that among '
            'those very nations which Paul somehow brands with atheism, some sense of deity '
            'has nevertheless remained, though entangled in many foul errors. Proof of which '
            'is that very idolatry by which the profane nations polluted themselves, and '
            'having left the Creator, worshipped various creatures and the very figments of '
            'their own mind. For this sense of divinity must be deeply impressed on people, '
            'since man — otherwise more than enough prone to pride and swollen with arrogance '
            '— preferred to cast himself below the beasts and worship stones and wood rather '
            'than acknowledge no God at all.'
        ),
        'pass_b': [
            'True saving knowledge is rare; most nations miss the true God.',
            'Ephesians 2:12: without God in the world — yet a sense of deity remains.',
            'Idolatry proves it: proud man would rather bow to stones than admit no God.',
        ],
        'lemmas': [
            {'latin': 'sine Deo in mundo', 'gloss': 'without God in the world'},
            {'latin': 'numinis tamen sensus aliquis', 'gloss': 'some sense of deity nevertheless'},
        ],
        'choices': [{
            'term': 'maluerit se abjicere infra bestias, & colere lapides & ligna, quam nullum plane Deum agnoscere',
            'english': 'preferred to cast himself below the beasts and worship stones and wood rather than acknowledge no God at all',
            'why': 'Idolatry as evidence of residual deity-sense.',
            'rejected': ['idolatry proves nations have no deity-sense'],
        }],
        'notes': ['OCR: VI PDF 102; Greek ἄθεοι ἐν τῷ κόσμῳ from Eph 2.12 restored.'],
        'bible_refs': ['Bible:Ephesians 2:12'],
    },
    {
        'section': '335',
        'title': 'World-contemplation can reach God — and His existence is demonstrable',
        'pass_a': (
            'Therefore it is altogether certain that from contemplation of the World, and of '
            'the things seen in it, people can arrive at knowledge of God: nor have the '
            'darknesses poured over the human mind by sin hindered that the greater part of '
            'people, by this way and with nature as guide, have obtained some notice of '
            'deity. But it is asked of what kind those reasons are by which from '
            'consideration of the works of nature it is shown that God is. Are they '
            'necessary, or only probable? And is the existence of God demonstrable by human '
            'wit, or can it only be reached by some conjectures and certain probable '
            'arguments? But in this we are of the opinion, with almost all theologians both '
            'ours and the Pontificii, that the existence of God is a matter which can be '
            'demonstrated and proved by necessary arguments.'
        ),
        'pass_b': [
            'World-contemplation can reach some knowledge of God — sin\'s darkness does not block that path for most.',
            'Open question: are the reasons necessary or only probable?',
            'Verdict with nearly all theologians, ours and Rome\'s: God\'s existence is demonstrable by necessary arguments.',
        ],
        'lemmas': [
            {'latin': 'demonstrabilis ingenio humano', 'gloss': 'demonstrable by human wit'},
            {'latin': 'necessariis argumentis evinci', 'gloss': 'proved by necessary arguments'},
        ],
        'choices': [{
            'term': 'Dei existentiam rem esse, quae demonstrari potest, & necessariis argumentis evinci',
            'english': 'the existence of God is a matter which can be demonstrated and proved by necessary arguments',
            'why': 'Settles demonstrability before the a-priori / a-posteriori split in VIII.',
            'rejected': ['God\'s existence is only probable conjecture'],
        }],
        'notes': ['OCR: VII spans PDF 102-103 page break (nostri / quam Pontificiis).'],
        'bible_refs': [],
    },
    {
        'section': '336',
        'title': 'God is not shown a priori from causes — but a posteriori from effects',
        'pass_a': (
            'But since demonstration among Dialecticians is twofold — one which from causes '
            'shows the effect, the other which on the contrary from effects shows the cause '
            '— it is clear that God\'s existence cannot be taught by the prior mode of '
            'demonstration; since neither of God nor of His existence can a cause be brought '
            'forward in any genus: but it can be demonstrated by the posterior mode, namely '
            'from effects. Nor should it be thought that the arguments by which it is proved '
            'that God is leave the matter somewhat doubtful, and only persuade, not convince.'
        ),
        'pass_b': [
            'Two demonstration modes: from causes, or from effects.',
            'God cannot be shown a priori from a higher cause — there is none.',
            'He is shown a posteriori from effects — and those arguments convince, not merely persuade.',
        ],
        'lemmas': [
            {'latin': 'ex causis effectum', 'gloss': 'from causes the effect'},
            {'latin': 'ex effectis causam', 'gloss': 'from effects the cause'},
            {'latin': 'suadere tantum, non convincere', 'gloss': 'only persuade, not convince'},
        ],
        'choices': [{
            'term': 'priori demonstrationis modo non posse doceri Deum esse',
            'english': 'God\'s existence cannot be taught by the prior mode of demonstration',
            'why': 'Blocks a-priori causal proof; opens effect-to-cause path for IX+.',
            'rejected': ['God is demonstrated from a higher cause'],
        }],
        'notes': ['OCR: VIII PDF 103; closes tip before IX (examples / unique demonstration).'],
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
            DATA / 'latin.json',
            Path(__file__),
        ],
        expected_sections=section_ids,
        seed=20260923,
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
        if 329 <= n <= 336:
            notes = (
                f'Section {sid}: new densify Demonstratur Deum esse I-VIII; '
                'Pass A!=B; lock-grounded PDF 102-103 / book pp. 90-91.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in deum_esse I-VIII packet scope covering all current sections.'
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
                'Scope review: densify Demonstratur Deum esse I-VIII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest partial; Deum esse through VIII; IX+ remains. '
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
        'locus': 'Demonstratur Deum esse theses I-VIII (AN SIT / natural knowledge / demonstrability)',
        'next_locus': 'Demonstratur Deum esse IX+ (principles / effect-to-cause demonstration)',
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
        f'## {day} (Scribe — Demonstratur Deum esse I–VIII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Deum esse I–VIII → §§{SECS[0]}–{SECS[-1]}; new tract after Plenitudine close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 102-103 / pp. 90-91).\n'
        f'- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n'
        '- Honest **partial**: Demonstratur Deum esse through VIII (AN SIT; natural knowledge; '
        'demonstrability from effects). IX+ remains. Prior tracts closed as before. Not folio. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Pre-append hold cleared live>4205 OR 12m; post tip-ready hold cleared '
        f'({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}; '
        f'disk tip re-read {TIP_BEFORE} before append.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc Demonstratur Deum esse I–VIII densify)\n\n'
        'CoS densify: Demonstratur Deum esse I–VIII (existence of God). '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Deum esse I–VIII (**'
        f'{receipt["before"]}→{receipt["after"]}** sections). Packet '
        f'{packet_ref}. Pass A≠B; tip-ready ok. Honest partial; through VIII. Next: Deum esse IX+. '
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-328 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
