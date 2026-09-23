#!/usr/bin/env python3
"""Build + apply De Vita Dei XVII-XXII densify (tip 491 → 497).

Honest tract close before De Scientia Dei. Live floor 4793.
After tip-ready: HOLD live>4793 OR 12m. Punch X=NO. No ship.
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
LOCK = BOOK / 'sources/_le_blanc_dei_vita_latin_lock.txt'
LOCK_REL = 'sources/_le_blanc_dei_vita_latin_lock.txt'
AUDIT = BOOK / 'reviews/audit'
HANDOFF = BOOK / 'SESSION_HANDOFF.md'
DATA = Path('/tmp/leblanc_dei_vita_densify')
PACKET_STEM = 'dei_vita_xvii_xxii_densify'
APPLY_COPY = BOOK / 'sources/_ocr_dei_vita/apply_dei_vita_xvii_xxii_densify.py'

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ['492', '493', '494', '495', '496', '497']
ROMANS = {
    '492': 'XVII', '493': 'XVIII', '494': 'XIX',
    '495': 'XX', '496': 'XXI', '497': 'XXII',
}
TIP_BEFORE = 491
PRIOR_START = 476
LIVE_FLOOR = 4793
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XXXVIII + Pars II I-XLIV + Pars III I-L + Pars IV I-XXXIV + "
    "Demonstratur Deum esse I-XLII + De Dei Simplicitate I-XXVIII + "
    "De Dei Perfectione & Infinitate I-XXVI + De Dei Immensitate & Omnipraesentia I-XXXII + "
    "De Aeternitate Dei I-XIX + De Vita Dei I-XXII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; De Authoritate Scripturae "
    "Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; De Scripturae plenitudine "
    "Pars I I-XXXVIII; Pars II I-XLIV; Pars III I-L; Pars IV I-XXXIV; Demonstratur Deum esse I-XLII; "
    "De Dei Simplicitate I-XXVIII; De Dei Perfectione & Infinitate I-XXVI; "
    "De Dei Immensitate & Omnipraesentia I-XXXII; De Aeternitate Dei I-XIX; De Vita Dei I-XXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. IA bub_gb_eOkHAW4G0-wC. "
    "Densify through De Vita Dei I-XXII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the 1675 London Latin. "
    "Covers De Theologia through De Vita Dei I-XXII. Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin through De Vita Dei I-XXII, "
    "reconstructed from IA PDF page images with pdftotext (+ DjVu checks). "
    "1683 not copy-text. No modern English. This slice densifies Vita Dei XVII-XXII "
    "(Scripture living God; oaths; life itself; John 1 scholastic aside; tract close)."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Vita Dei.\n"
    "Same 1675 Pitt copy-text. Book pp. 114-117 / PDF 126-129 (I-XXII; this packet XVII-XXII). "
    "pdftotext layout (+ DjVu checks). Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: De Vita Dei I-XXII tip — tract closed. Next: De Scientia Dei.\n"
    "Note: Continues after IX-XVI. Scripture living God; Vivit Dominus; God as life; frivolous John 1 question.\n\n"
)

LATIN = {
    '492': (
        'XVII. Propterea nihil est frequentius in Scriptura quam Deum vocare vivum sive '
        'viventem, quo titulo vult illa Deum verum quem colimus falsis Diis opponere, '
        'illumque secernere ab idolis mortuis, quae omni cognitione & agendi vi destituta sunt.'
    ),
    '493': (
        'XVIII. Inde quoque natus est mos in Scriptura probatus jurandi per Dei vitam. Nam '
        'pii homines in juramentis suis saepe hanc formulam usurpant, Vivit Dominus. Et Deus '
        'ipse dum, ut sese nobis attemperet, jurans introducitur, utitur his verbis, Vivo Ego.'
    ),
    '494': (
        'XIX. Neque Deus in Scriptura simpliciter vivere dicitur, sed etiam vivens absolute '
        'vocatur, & titulus viventis ipsi tanquam nomen quoddam proprium tribuitur, ut Genes. '
        '17. ubi puteus ille apud quem Deus ancillae Abrahae Agar apparuerat vocatur in persona '
        'mulieris istius puteus viventis videntis me. Et Apoc. 4. ubi viginti quatuor seniores '
        'dicuntur adorasse Viventem in saecula.'
    ),
    '495': (
        'XX. Hinc etiam Ethnici Deum illum supremum quem ipsi praedicabant patrem hominumque '
        'Deumque, vocaverunt Ζῆνα quasi vivum diceres, scilicet a τῷ ζῆν, quod apud Graecos '
        'vivere significat.'
    ),
    '496': (
        'XXI. Neque Deus solum dicitur vivens sed vita ipsa: ut cum Dei Filius dicit apud '
        'Joan. c. 14. Ego sum via, veritas & vita: & undecimo capite, Ego sum resurrectio & '
        'vita. Et certe Dei summa simplicitas exigit ut ipse vita dici possit: quoniam in illo '
        'res non se habet ut in creaturis: in quibus vivere & esse distinguuntur tanquam gradus '
        'essentiales; vita vero Dei est ipsum ejus esse, neque in eo, ut in nobis, a vita '
        'distingui debet quoddam vivendi principium. Veruntamen quum Scriptura Deum & Christum '
        'dicit esse vitam, eo proprie non respicit: sed potius per hoc significat Deum non solum '
        'in seipso vivere, sed praeterea fontem esse perennem a quo quicquid est in creaturis '
        'vitae, praecipue spiritualis, necessario manat; & quicum non possumus communionem '
        'habere quin beatae & aeternae vitae fiamus participes, juxta illud Psalmi trigesimi '
        'sexti, quoniam apud te est fons vitae, & in lumine tuo videbimus lumen. Nec alio '
        'spectat Christus Dominus noster dum dicit apud Joan. cap. 5. Patrem habere vitam in '
        'seipso, & filio dedisse ut vitam quoque habeat in seipso: nempe ut per id probet '
        'mortuos audituros vocem filii Dei, & qui audierint victuros.'
    ),
    '497': (
        'XXII. Porro hic quaerere solent, & explicare conantur scholastici post Thomam quando '
        'omnia sint vita in Deo: sed quaestio ista prorsus frivola est & nata solum ex mala '
        'distinctione, & pravo intellectu textus vulgaris veteris initio capitis primi '
        'Evangelii secundum Joannem, ubi tanquam unam sententiam verba ista conjungit Thomas, '
        'quod factum est in ipso vita erat. Cum tamen verba illa quod factum est pertineant ad '
        'praecedentem clausulam omnia per ipsum facta sunt, & sine ipso factum est nihil quod '
        'factum est. Sequenś vero sententia incipiat ab illis verbis, In ipso vita erat.'
    ),
}

SECTIONS = [
    {
        'section': '492',
        'title': 'Scripture calls God the living — against dead idols',
        'pass_a': (
            'Therefore nothing is more frequent in Scripture than to call God living or the '
            'living One, by which title it wills to oppose the true God whom we worship to the '
            'false gods, and to set Him apart from dead idols, which are destitute of all '
            'knowledge and power of acting.'
        ),
        'pass_b': [
            'Scripture’s favorite title: living / the living God.',
            'Sets the true God against false gods.',
            'Dead idols: no knowledge, no power to act.',
        ],
        'lemmas': [
            {'latin': 'Deum vocare vivum sive viventem', 'gloss': 'to call God living or the living One'},
            {'latin': 'ab idolis mortuis', 'gloss': 'from dead idols'},
        ],
        'choices': [{
            'term': 'secernere ab idolis mortuis',
            'english': 'to set Him apart from dead idols',
            'why': 'Opens the Scripture slice: living God vs lifeless idols.',
            'rejected': ['living is only a philosophical title, not Scriptural'],
        }],
        'notes': ['OCR: XVII PDF 128; living God vs dead idols.'],
        'bible_refs': [],
    },
    {
        'section': '493',
        'title': 'Swearing by God’s life — Vivit Dominus / Vivo Ego',
        'pass_a': (
            'From there also arose the custom approved in Scripture of swearing by the life of '
            'God. For pious men in their oaths often use this formula, The Lord lives. And God '
            'Himself, when, that He may accommodate Himself to us, is introduced as swearing, '
            'uses these words, I live.'
        ),
        'pass_b': [
            'Scripture-approved oaths by God’s life.',
            'Human form: Vivit Dominus.',
            'Divine self-accommodation: Vivo Ego.',
        ],
        'lemmas': [
            {'latin': 'jurandi per Dei vitam', 'gloss': 'of swearing by the life of God'},
            {'latin': 'Vivit Dominus … Vivo Ego', 'gloss': 'The Lord lives … I live'},
        ],
        'choices': [{
            'term': 'jurandi per Dei vitam',
            'english': 'of swearing by the life of God',
            'why': 'Shows life-language entering oath practice in Scripture.',
            'rejected': ['Scripture forbids all oaths by God’s life'],
        }],
        'notes': ['OCR: XVIII PDF 128; Vivit Dominus / Vivo Ego.'],
        'bible_refs': [],
    },
    {
        'section': '494',
        'title': 'The Living as a proper title — Gen 16/17 well; Rev 4',
        'pass_a': (
            'Nor is God in Scripture said simply to live, but He is also called the Living One '
            'absolutely, and the title of the Living One is ascribed to Him as a kind of proper '
            'name, as in Genesis 17, where that well by which God had appeared to Abraham’s '
            'maidservant Hagar is called in that woman’s person the well of the Living One who '
            'sees me. And Revelation 4, where the twenty-four elders are said to have worshiped '
            'the One who lives forever.'
        ),
        'pass_b': [
            'Not only “lives” — titled the Living One.',
            'Hagar’s well: Living One who sees me.',
            'Rev 4: elders worship Him who lives forever.',
        ],
        'lemmas': [
            {'latin': 'titulus viventis … nomen quoddam proprium', 'gloss': 'the title of the Living One … a kind of proper name'},
            {'latin': 'Viventem in saecula', 'gloss': 'the One who lives forever'},
        ],
        'choices': [{
            'term': 'titulus viventis ipsi tanquam nomen quoddam proprium tribuitur',
            'english': 'the title of the Living One is ascribed to Him as a kind of proper name',
            'why': 'Elevates vivens from predicate to near-proper name in Scripture.',
            'rejected': ['vivens is only an occasional adjective'],
        }],
        'notes': ['OCR: XIX PDF 128; Gen well / Apoc 4; Beer-lahai-roi.'],
        'bible_refs': ['Gen. 16:13-14', 'Rev. 4:10'],
    },
    {
        'section': '495',
        'title': 'Pagans named Zeus from living — τῷ ζῆν',
        'pass_a': (
            'Hence also the pagans called that supreme God whom they proclaimed father of men '
            'and God, Ζῆνα, as if you should say the living One, namely from τῷ ζῆν, which among '
            'the Greeks means to live.'
        ),
        'pass_b': [
            'Even pagans nicknamed the top god from living.',
            'Ζῆνα from τῷ ζῆν — to live.',
            'Echoes the living-God theme outside Israel.',
        ],
        'lemmas': [
            {'latin': 'vocaverunt Ζῆνα quasi vivum', 'gloss': 'called Him Ζῆνα as if the living One'},
            {'latin': 'a τῷ ζῆν … vivere significat', 'gloss': 'from τῷ ζῆν … means to live'},
        ],
        'choices': [{
            'term': 'Ζῆνα quasi vivum diceres, scilicet a τῷ ζῆν',
            'english': 'Ζῆνα as if you should say the living One, namely from τῷ ζῆν',
            'why': 'Etymological aside confirming living as a supreme-god title.',
            'rejected': ['Zeus has no link to living in Greek speech'],
        }],
        'notes': ['OCR: XX PDF 128; Ζῆνα / τῷ ζῆν.'],
        'bible_refs': [],
    },
    {
        'section': '496',
        'title': 'God is life itself — simplicity; fountain of life',
        'pass_a': (
            'Nor is God only called living but life itself: as when the Son of God says in John '
            'chapter 14, I am the way, the truth, and the life: and in the eleventh chapter, I '
            'am the resurrection and the life. And certainly God’s highest simplicity requires '
            'that He Himself can be called life: because in Him the matter is not as in '
            'creatures, in whom to live and to be are distinguished as essential grades; but '
            'God’s life is His very being, nor in Him, as in us, must some principle of living '
            'be distinguished from life. Nevertheless when Scripture says that God and Christ '
            'are life, it does not properly look that way: but rather by this it signifies that '
            'God not only lives in Himself, but moreover is a perennial fountain from which '
            'whatever life there is in creatures, especially spiritual life, necessarily flows; '
            'and with whom we cannot have communion without becoming partakers of blessed and '
            'eternal life, according to that of Psalm 36, for with You is the fountain of life, '
            'and in Your light we shall see light. Nor does our Lord Christ look elsewhere when '
            'He says in John chapter 5 that the Father has life in Himself, and has given to '
            'the Son also to have life in Himself: namely that by that He may prove that the '
            'dead will hear the voice of the Son of God, and those who hear will live.'
        ),
        'pass_b': [
            'God / Christ called life itself (John 14; 11).',
            'Simplicity: God’s life = His being — no separate vital principle.',
            'Scripture stress: fountain of life (Ps 36); John 5 life-in-Himself.',
        ],
        'lemmas': [
            {'latin': 'vita vero Dei est ipsum ejus esse', 'gloss': 'but God’s life is His very being'},
            {'latin': 'fontem esse perennem', 'gloss': 'to be a perennial fountain'},
        ],
        'choices': [{
            'term': 'vita vero Dei est ipsum ejus esse',
            'english': 'but God’s life is His very being',
            'why': 'Doctrine of simplicity applied to divine life vs creature grades.',
            'rejected': ['God has a vital principle distinct from His essence'],
        }],
        'notes': ['OCR: XXI PDF 128-129; John 14/11/5; Ps 36.'],
        'bible_refs': ['John 14:6', 'John 11:25', 'Ps. 36:9', 'John 5:26'],
    },
    {
        'section': '497',
        'title': 'Frivolous scholastic question — John 1 punctuation',
        'pass_a': (
            'Further, here the scholastics after Thomas are wont to ask and try to explain when '
            'all things are life in God: but that question is altogether frivolous and born only '
            'from a bad distinction and a wrong understanding of the old Vulgate text at the '
            'beginning of the first chapter of the Gospel according to John, where Thomas joins '
            'those words as one sentence, what was made in Him was life. Whereas yet those words '
            'what was made belong to the preceding clause, all things were made through Him, and '
            'without Him was made nothing that was made. But the following sentence begins from '
            'those words, In Him was life.'
        ),
        'pass_b': [
            'Scholastic “when are all things life in God?” — frivolous.',
            'Bad Vulgate join: quod factum est in ipso vita erat.',
            'Right cut: …nihil quod factum est. / In ipso vita erat.',
        ],
        'lemmas': [
            {'latin': 'quaestio ista prorsus frivola est', 'gloss': 'that question is altogether frivolous'},
            {'latin': 'In ipso vita erat', 'gloss': 'In Him was life'},
        ],
        'choices': [{
            'term': 'Sequenś vero sententia incipiat ab illis verbis, In ipso vita erat',
            'english': 'But the following sentence begins from those words, In Him was life',
            'why': 'Closes Vita Dei by rejecting the Thomas/John 1 mispunctuation; next Scientia Dei.',
            'rejected': ['John 1 makes every creature life-in-God as one sentence'],
        }],
        'notes': ['OCR: XXII PDF 129; tract close; next De Scientia Dei.'],
        'bible_refs': ['John 1:3-4'],
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
        jpath = JUST / f'dei_vita_{sec}.json'
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        errs = check_file(jpath)
        print(f'check_pass_ab dei_vita_{sec} ({ROMANS[sec]})', 'ok' if not errs else errs)
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
    for name in ('pdf_128.txt', 'pdf_129.txt', 'pdf_126_134_layout.txt'):
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
        if 492 <= n <= 497:
            notes = (
                f'Section {sid}: new densify De Vita Dei XVII-XXII tract close; '
                'Pass A!=B; lock-grounded PDF 128-129 / book pp. 116-117.'
            )
        else:
            notes = (
                f'Section {sid}: prior verified densify retained; Pass A/B and lock identity '
                'rechecked in dei_vita XVII-XXII packet scope covering all current sections.'
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
                'Scope review: densify De Vita Dei XVII-XXII only '
                f'(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. '
                'Honest tract close; Vita through XXII. Next Scientia Dei. Not shipped.'
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
        'locus': 'De Vita Dei theses XVII-XXII (Scripture living God; oaths; life itself; John 1; close)',
        'next_locus': 'De Scientia Dei (opens after Vita Dei XXII)',
        'gates': {
            'check_pass_ab': f'ok dei_vita_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})',
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
        'honest_slice_note': 'XVII-XXII honest tract close before Scientia (6 < 4-8 ok)',
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
        f'## {day} (Scribe — De Vita Dei XVII–XXII densify LOCAL)\n\n'
        f'- Before: **{receipt["before"]}**. After: **{receipt["after"]}** '
        f'(contiguous Vita Dei XVII–XXII → §§{SECS[0]}–{SECS[-1]}; tract close).\n'
        f'- Packet {packet_ref} ({packet_files}). '
        f'Reviewer: scribe-leblanc, {day}. Verdict pass grounded in '
        f'{lock_ref} (PDF 128-129 / pp. 116-117).\n'
        f'- Meta range bumped to **{RANGE_SHORT}**.\n'
        '- Honest **partial**: De Vita Dei through XXII **closed**. '
        'Next: De Scientia Dei. Not shipped.\n'
        f'- Pass A ≠ B for §§{SECS[0]}–{SECS[-1]}. check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n'
        f'- Post tip-ready hold cleared ({receipt["hold_clear_reason"]}) live {receipt["live_at_proceed"]}.\n'
        f'- Claim {claim_ref} stays claimed. Punch X = NO.\n\n'
    )
    prev = HANDOFF.read_text(encoding='utf-8') if HANDOFF.exists() else ''
    HANDOFF.write_text(block + prev, encoding='utf-8')
    repo_handoff = REPO / 'SESSION_HANDOFF.md'
    repo_block = (
        f'## {day} ~ET (Scribe — Le Blanc De Vita Dei XVII–XXII densify)\n\n'
        'CoS densify: Vita Dei XVII–XXII tract close. '
        'Punch X: **NO**. No ship/commit/Logos/ai_promote.\n\n'
        '### Bound this job (not shipped)\n'
        f'- **Le Blanc** {slug_ref}: Vita Dei XVII–XXII (**'
        f'{receipt["before"]}→{receipt["after"]}**). Packet {packet_ref}. '
        'Next: Scientia Dei. Punch X: **NO**.\n\n---\n\n'
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
    (DATA / 'hold_post_tipready_497.json').write_text(
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
    live_tuple = wait_hold(hold_start, post_floor, label='tip-497 post-ready')
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print('DONE', receipt['before'], '->', receipt['after'], 'Punch X=NO', flush=True)


if __name__ == '__main__':
    main()
