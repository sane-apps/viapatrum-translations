#!/usr/bin/env python3
"""Deep mine bibliology + pneumatology candidates from local + ANF cache."""
from __future__ import annotations

from pathlib import Path
import re
import html
import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "outputs/mining/anf_cache"
OUT = ROOT / "outputs/mining/bibliology_pneumatology_candidates.json"

NAV_JUNK = re.compile(
    r"(?:CHURCH FATHERS:|Search:\s*Submit Search|Home\s+Encyclopedia|Summa Fathers Bible Library|"
    r"Please help support.*?\$19\.99\.\.\.?|About this page.*|Source\. Translated by.*|"
    r"Contact information\..*|« Prev.*?Next »|Font Aa.*?Tags:|"
    r"Disable scripture popups.*?(?:World English Bible)?|Show footnotes.*?(?:On the side)|"
    r"Reader Width|Bible Version|Text Size A A|Contents\b|"
    r"A B C D E F G H I J K L M N O P Q R S T U V W X Y Z|"
    r"Encyclopedia Summa Fathers Bible Library\s*-->)",
    re.I | re.S,
)

FILE_META = {
    "justin_apology1_43.html": ("Justin Martyr", "First Apology", "c. 155", "Apology", "accepted", "grc"),
    "justin_2apology.html": ("Justin Martyr", "Second Apology", "c. 155", "Apology", "accepted", "grc"),
    "athenagoras_plea.html": ("Athenagoras", "Plea for the Christians", "c. 177", "Apology", "accepted", "grc"),
    "Tatian_address.html": ("Tatian", "Address to the Greeks", "c. 165", "Apology", "accepted", "grc"),
    "theophilus_autolycus.html": ("Theophilus of Antioch", "To Autolycus", "c. 180", "Apology", "accepted", "grc"),
    "barnabas.html": ("Barnabas (Epistle)", "Epistle of Barnabas", "c. 100–130", "Letter", "contested", "grc"),
    "didache.html": ("Didache", "Didache", "c. 100", "Church order", "accepted", "grc"),
    "hermas_mandates.html": ("Hermas", "Shepherd — Mandates", "c. 140", "Apocalypse", "contested", "grc"),
    "hermas_similitudes.html": ("Hermas", "Shepherd — Similitudes", "c. 140", "Apocalypse", "contested", "grc"),
    "hermas_shepherd.html": ("Hermas", "Shepherd of Hermas", "c. 140", "Apocalypse", "contested", "grc"),
    "ignatius_ephesians.html": ("Ignatius of Antioch", "To the Ephesians", "c. 110", "Letter", "accepted", "grc"),
    "ignatius_smyrnaeans.html": ("Ignatius of Antioch", "To the Smyrnaeans", "c. 110", "Letter", "accepted", "grc"),
    "irenaeus_ah_3_18.html": ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    "irenaeus_ah_4_37.html": ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    "irenaeus_ah_4_39.html": ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    "irenaeus_ah_5_21.html": ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    "irenaeus_ah_5_28.html": ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    "tertullian_marcion_2_5.html": ("Tertullian", "Against Marcion", "c. 207", "Treatise", "accepted", "lat"),
    "tertullian_repentance.html": ("Tertullian", "On Repentance", "c. 200", "Treatise", "accepted", "lat"),
    "clement_stromata1.html": ("Clement of Alexandria", "Stromata", "c. 200", "Treatise", "accepted", "grc"),
    "clement_instructor.html": ("Clement of Alexandria", "Paedagogus", "c. 200", "Treatise", "accepted", "grc"),
    "origen_celsus.html": ("Origen", "Against Celsus", "c. 248", "Treatise", "accepted", "grc"),
    "origen_princ_3_1.html": ("Origen", "On First Principles", "c. 230", "Treatise", "accepted", "grc"),
    "novatian_trinity.html": ("Novatian", "On the Trinity", "c. 250", "Treatise", "accepted", "lat"),
    "hippolytus_refutation1.html": ("Hippolytus", "Refutation of All Heresies", "c. 220", "Treatise", "accepted", "grc"),
    "lactantius_institutes1.html": ("Lactantius", "Divine Institutes", "c. 304–310", "Treatise", "accepted", "lat"),
    "mathetes_diognetus.html": ("Mathetes", "Epistle to Diognetus", "c. 150?", "Letter", "accepted", "grc"),
    "commodian_instructions.html": ("Commodian", "Instructions", "c. 250?", "Poem", "accepted", "lat"),
    "minucius_octavius.html": ("Minucius Felix", "Octavius", "c. 200", "Dialogue", "accepted", "lat"),
    "arnobius_nations1.html": ("Arnobius", "Against the Nations", "c. 300", "Apology", "accepted", "lat"),
    "cyprian_treatises.html": ("Cyprian of Carthage", "Treatises", "c. 250", "Treatise", "accepted", "lat"),
    "methodius_freewill.html": ("Methodius", "On Free Will / related", "c. 300", "Treatise", "accepted", "grc"),
    "victorinus_creation.html": ("Victorinus of Pettau", "On the Creation of the World", "c. 270", "Treatise", "accepted", "lat"),
    "gregory_thaumaturgus.html": ("Gregory Thaumaturgus", "Panegyric to Origen", "c. 240", "Oration", "accepted", "grc"),
    "dionysius_alexandria.html": ("Dionysius/Methodius misc", "Fragments", "c. 250–300", "Fragment", "contested", "grc"),
    "melito_passover.html": ("(misfiled)", "skip", "", "", "", ""),
    "melito_apology.html": ("(misfiled)", "skip", "", "", "", ""),
}

CACHE_META_PREFIX = [
    (r"^0103", "Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    (r"^0126", "Justin Martyr", "First Apology", "c. 155", "Apology", "accepted", "grc"),
    (r"^0128", "Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc"),
    (r"^0204", "Theophilus of Antioch", "To Autolycus", "c. 180", "Apology", "accepted", "grc"),
    (r"^0210", "Clement of Alexandria", "Stromata", "c. 200", "Treatise", "accepted", "grc"),
    (r"^0311", "Tertullian", "Prescription against Heretics", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0312", "Tertullian", "Against Marcion", "c. 207", "Treatise", "accepted", "lat"),
    (r"^0315", "Tertullian", "On the Soul", "c. 210", "Treatise", "accepted", "lat"),
    (r"^0318", "Tertullian", "On Baptism", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0321", "Tertullian", "Against Praxeas", "c. 213", "Treatise", "accepted", "lat"),
    (r"^0324", "Tertullian", "On the Veiling of Virgins", "c. 210", "Treatise", "accepted", "lat"),
    (r"^0325", "Tertullian", "On Monogamy", "c. 210", "Treatise", "accepted", "lat"),
    (r"^0412", "Origen", "On First Principles", "c. 230", "Treatise", "accepted", "grc"),
    (r"^0416", "Origen", "Against Celsus", "c. 248", "Treatise", "accepted", "grc"),
    (r"^0501", "Hippolytus", "Refutation of All Heresies", "c. 220", "Treatise", "accepted", "grc"),
    (r"^0502", "Cyprian of Carthage", "Epistles", "c. 250", "Letter", "accepted", "lat"),
    (r"^0507", "Cyprian of Carthage", "Treatises", "c. 250", "Treatise", "accepted", "lat"),
    (r"^2501", "Eusebius of Caesarea", "Church History", "c. 325", "History", "accepted", "grc"),
    (r"ccel_anf01\.viii", "Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc"),
    (r"ccel_anf01\.ix", "Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
]

TOPIC_RULES = {
    "scripture-inspiration": {
        "need_any": [
            r"inspir",
            r"prophet",
            r"holy (scripture|writings|writ)",
            r"oracles",
            r"prophetic Spirit",
            r"Spirit.{0,40}(spoke|speaks|utter)",
            r"divine (scripture|writings)",
            r"writings of the prophets",
        ],
        "need_strong": [
            r"inspir",
            r"prophetic Spirit",
            r"Spirit.{0,30}(spoke|speaks).{0,40}prophet",
            r"oracles of God",
            r"divine scripture",
            r"God spoke.{0,30}prophet",
            r"holy scriptures?",
        ],
        "ban": [r"^All hail, you sons"],
    },
    "canon-rule-of-truth": {
        "need_any": [
            r"rule of (truth|faith)",
            r"apostolic tradition",
            r"tradition.{0,50}apostles",
            r"four Gospel",
            r"canon",
            r"succession",
            r"pillar and ground|ground and pillar",
            r"Scriptures belong",
        ],
        "need_strong": [
            r"rule of (truth|faith)",
            r"apostolic tradition",
            r"four Gospel",
            r"succession of (bishops|presbyters)",
            r"tradition derived from the apostles",
            r"handed down.{0,40}(scripture|gospel|apostles)",
        ],
        "ban": [r"Has the sun himself"],
    },
    "old-and-new": {
        "need_any": [
            r"Marcion",
            r"Old Testament",
            r"New Testament",
            r"both (testaments|covenants)",
            r"old and the new",
            r"law and the (gospel|prophets)",
            r"Creator.{0,40}(law|prophet|scripture)",
            r"one (and the same )?God.{0,80}(testament|covenant|law)",
        ],
        "need_strong": [
            r"Marcion",
            r"both (testaments|covenants)",
            r"Old Testament.{0,80}New Testament|New Testament.{0,80}Old Testament",
            r"one and the same God",
            r"two gods",
            r"Demiurge",
        ],
        "ban": [],
    },
    "hermeneutics-types": {
        "need_any": [
            r"allegor",
            r"\btyp(e|es|ical|ology)\b",
            r"figur(e|atively)",
            r"spiritual (sense|meaning|interpretation)",
            r"shadow",
            r"interpret",
        ],
        "need_strong": [
            r"allegor",
            r"\btyp(e|es|ical|ology)\b",
            r"spiritual (sense|meaning|interpretation)",
            r"was a type",
            r"figuratively",
        ],
        "ban": [r"These are your ideas, these are your sentiments"],
    },
    "lxx-and-form": {
        "need_any": [
            r"Septuagint",
            r"\bSeventy\b",
            r"\bLXX\b",
            r"Hebrew",
            r"Greek (version|translation|reading|copy)",
            r"translat",
        ],
        "need_strong": [
            r"Septuagint",
            r"\bSeventy\b",
            r"\bLXX\b",
            r"Hebrew.{0,50}(Greek|version|translation|reading)",
            r"translat(ors|ion).{0,40}(seventy|Hebrew|Greek)",
            r"Ptolem",
        ],
        "ban": [],
    },
    "spirit-prophecy": {
        "need_any": [
            r"Holy Spirit",
            r"Holy Ghost",
            r"Spirit of (God|prophecy|truth)",
            r"prophetic Spirit",
            r"prophes",
        ],
        "need_strong": [
            r"prophetic Spirit",
            r"Spirit.{0,40}prophet",
            r"Spirit of prophecy",
            r"Holy Spirit.{0,60}(spoke|speaks|prophet|inspir)",
            r"prophets?.{0,40}(Spirit|inspired)",
        ],
        "ban": [],
    },
    "spirit-and-baptism": {
        "need_any": [r"baptis", r"laver", r"regenerat", r"born again", r"water"],
        "need_strong": [
            r"baptis\w*.{0,80}(spirit|holy ghost)",
            r"(spirit|holy ghost).{0,80}baptis",
            r"water and.{0,30}spirit",
            r"laver",
            r"regenerat\w*.{0,60}(baptis|water|spirit)",
            r"baptiz\w*.{0,40}(Father|Son|Spirit)",
        ],
        "ban": [],
    },
    "gifts-and-order": {
        "need_any": [r"gift", r"charism", r"prophet", r"Montan", r"tongues", r"apostle", r"order"],
        "need_strong": [
            r"charism",
            r"gifts? of (the )?(Spirit|Holy)",
            r"Montan",
            r"false prophet",
            r"prophetess",
            r"apostles? and prophets",
            r"try the spirits",
            r"tongues",
            r"prophesy in the church",
            r"Commandment 11|false prophet|true prophet",
        ],
        "ban": [],
    },
    "spirit-sanctifies": {
        "need_any": [r"sanctif", r"holy", r"Spirit", r"temple", r"purif"],
        "need_strong": [
            r"sanctif",
            r"temple of.{0,30}(God|Spirit|Holy)",
            r"Spirit.{0,50}(dwell|indwell|abide|live in)",
            r"purif\w*.{0,40}spirit",
            r"grieve.{0,20}Spirit",
            r"fruit of the Spirit",
        ],
        "ban": [],
    },
}

MIN = {
    "scripture-inspiration": 5,
    "canon-rule-of-truth": 4,
    "old-and-new": 5,
    "hermeneutics-types": 5,
    "lxx-and-form": 4,
    "spirit-prophecy": 5,
    "spirit-and-baptism": 4,
    "gifts-and-order": 3,
    "spirit-sanctifies": 4,
}
SOFT = {k: 55 for k in MIN}
SOFT.update(
    {
        "lxx-and-form": 35,
        "gifts-and-order": 40,
        "spirit-and-baptism": 40,
        "canon-rule-of-truth": 45,
    }
)

FORCE = [
    ("0103110", r".", ["canon-rule-of-truth"]),
    ("0103301", r".", ["canon-rule-of-truth", "scripture-inspiration", "spirit-prophecy"]),
    ("0103302", r".", ["canon-rule-of-truth"]),
    ("0103303", r".", ["canon-rule-of-truth"]),
    ("0103304", r".", ["canon-rule-of-truth"]),
    ("0103311", r".", ["canon-rule-of-truth"]),
    ("0103409", r".", ["old-and-new"]),
    ("0103411", r".", ["old-and-new"]),
    ("0103420", r".", ["old-and-new", "scripture-inspiration"]),
    ("0103433", r".", ["spirit-prophecy", "gifts-and-order"]),
    ("0103506", r".", ["spirit-sanctifies"]),
    ("0103508", r".", ["spirit-and-baptism", "spirit-sanctifies"]),
    ("ccel_anf01.ix.vi.xx", r".", ["gifts-and-order", "spirit-prophecy"]),
    ("ccel_anf01.ix.vii.viii", r".", ["spirit-and-baptism", "spirit-sanctifies"]),
    ("ccel_anf01.ix.iv.xxxiii", r".", ["spirit-prophecy"]),
    ("04120", r".", ["canon-rule-of-truth", "scripture-inspiration"]),
    ("04124", r".", ["hermeneutics-types", "scripture-inspiration"]),
    ("0311", r"Chapter 13", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 15", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 19", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 21", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 28", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 36", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 37", ["canon-rule-of-truth"]),
    ("0311", r"Chapter 38", ["canon-rule-of-truth"]),
    ("03121", r".", ["old-and-new"]),
    ("03122", r".", ["old-and-new"]),
    ("03123", r".", ["old-and-new"]),
    ("03124", r".", ["old-and-new"]),
    ("03125", r".", ["old-and-new"]),
    ("0318", r"Chapter", ["spirit-and-baptism"]),
    ("ccel_anf01.viii.iv.lxxi", r".", ["lxx-and-form"]),
    ("ccel_anf01.viii.iv.lxxii", r".", ["lxx-and-form"]),
    ("ccel_anf01.viii.iv.lxxiii", r".", ["lxx-and-form"]),
    ("01281", r"Chapter 7", ["scripture-inspiration", "spirit-prophecy"]),
    ("didache.html", r"Chapter 7", ["spirit-and-baptism"]),
    ("didache.html", r"Chapter 11", ["gifts-and-order"]),
    ("didache.html", r"Chapter 15", ["gifts-and-order"]),
    ("justin_apology1_43.html", r"Chapter 61", ["spirit-and-baptism"]),
    ("justin_apology1_43.html", r"Chapter 65", ["spirit-and-baptism"]),
    ("justin_apology1_43.html", r"Chapter 31", ["scripture-inspiration", "lxx-and-form"]),
    ("justin_apology1_43.html", r"Chapter 36", ["spirit-prophecy"]),
    ("justin_apology1_43.html", r"Chapter 44", ["scripture-inspiration"]),
    ("athenagoras_plea.html", r"Chapter 7", ["spirit-prophecy", "scripture-inspiration"]),
    ("athenagoras_plea.html", r"Chapter 9", ["spirit-prophecy", "scripture-inspiration"]),
    ("hermas_mandates.html", r"Commandment 11", ["gifts-and-order", "spirit-prophecy"]),
    ("hermas_mandates.html", r"Commandment 10", ["spirit-sanctifies"]),
    ("hermas_mandates.html", r"Commandment 5", ["spirit-sanctifies"]),
    ("050108", r".", ["gifts-and-order"]),
    ("050109", r".", ["gifts-and-order"]),
    ("250104", r".", ["canon-rule-of-truth"]),
    ("barnabas.html", r"Chapter 7", ["hermeneutics-types"]),
    ("barnabas.html", r"Chapter 8", ["hermeneutics-types"]),
    ("barnabas.html", r"Chapter 9", ["hermeneutics-types", "lxx-and-form"]),
    ("barnabas.html", r"Chapter 10", ["hermeneutics-types"]),
    ("barnabas.html", r"Chapter 11", ["hermeneutics-types", "spirit-and-baptism"]),
    ("barnabas.html", r"Chapter 12", ["hermeneutics-types"]),
    ("barnabas.html", r"Chapter 13", ["old-and-new"]),
    ("barnabas.html", r"Chapter 14", ["old-and-new"]),
    ("novatian_trinity.html", r"Chapter 29", ["spirit-prophecy"]),
    ("050701", r".", ["canon-rule-of-truth"]),
    ("050703", r".", ["spirit-and-baptism"]),
    ("ignatius_ephesians.html", r"Chapter 9", ["spirit-sanctifies"]),
    ("ignatius_ephesians.html", r"Chapter 18", ["spirit-and-baptism"]),
    ("0321", r"Chapter", ["spirit-prophecy"]),
]


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<script.*?</script>", " ", s)
    s = re.sub(r"(?is)<style.*?</style>", " ", s)
    s = re.sub(r"(?is)<!--.*?-->", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = NAV_JUNK.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_body(s: str) -> str:
    s = NAV_JUNK.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for marker in [
        "Unity of the faith",
        "The Church , though",
        "The Church, though",
        "We have learned from none others",
        "When, however, they are confuted",
        "It is within the power of all",
        "Since therefore we have such proofs",
        "Preface.",
        "1. ",
    ]:
        i = s.find(marker)
        if 0 < i < 500:
            s = s[i:]
            break
    return s.strip()


def split_chapters(raw: str, fname: str):
    parts = re.split(r"(?i)(<h2[^>]*>\s*Chapter\s+[^<]+</h2>)", raw)
    out = []
    if len(parts) == 1:
        parts2 = re.split(r"(?i)(<h2[^>]*>[^<]{3,120}</h2>)", raw)
        if len(parts2) > 3:
            i = 1
            while i + 1 < len(parts2):
                head = strip_html(parts2[i])
                if re.search(r"About this page|Encyclopedia|Search", head, re.I):
                    i += 2
                    continue
                body = clean_body(strip_html(parts2[i + 1]))
                ab = re.search(r"About this page", body, re.I)
                if ab:
                    body = body[: ab.start()].strip()
                if len(body) > 200 and not re.search(r"CHURCH FATHERS:|Submit Search", body):
                    out.append((head, body))
                i += 2
            if out:
                return out
        title_m = re.search(r"<h1[^>]*>([^<]+)", raw, re.I)
        title = strip_html(title_m.group(1)) if title_m else fname
        body = clean_body(strip_html(raw))
        ab = re.search(r"About this page", body, re.I)
        if ab:
            body = body[: ab.start()].strip()
        if len(body) > 220:
            out.append((title, body))
        return out
    i = 1
    while i + 1 < len(parts):
        head = strip_html(parts[i])
        body = clean_body(strip_html(parts[i + 1]))
        ab = re.search(r"About this page", body, re.I)
        if ab:
            body = body[: ab.start()].strip()
        if len(body) > 180:
            out.append((head, body))
        i += 2
    return out


def meta_for(path: Path, title: str):
    name = path.name
    if name in FILE_META:
        return FILE_META[name]
    stem = name.replace(".html", "")
    for pat, *rest in CACHE_META_PREFIX:
        if re.search(pat, stem):
            return tuple(rest)
    t = title.lower()
    if "irenaeus" in t or "heresies" in t:
        return ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat")
    if "justin" in t and "trypho" in t:
        return ("Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc")
    if "tertullian" in t or "marcion" in t:
        return ("Tertullian", "Against Marcion", "c. 207", "Treatise", "accepted", "lat")
    if "origen" in t:
        return ("Origen", "Treatise", "c. 230", "Treatise", "accepted", "grc")
    if "clement" in t:
        return ("Clement of Alexandria", "Stromata", "c. 200", "Treatise", "accepted", "grc")
    if "cyprian" in t:
        return ("Cyprian of Carthage", "Treatises", "c. 250", "Treatise", "accepted", "lat")
    if "hippolytus" in t:
        return ("Hippolytus", "Refutation of All Heresies", "c. 220", "Treatise", "accepted", "grc")
    return None


def locus_of(title: str, work: str, path: str) -> str:
    m = re.search(r"Book\s+([IVXLC\d]+).*?Chapter\s+(\d+)", title, re.I)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = re.search(r"0103(\d)(\d{2})", path)
    if m:
        return f"{m.group(1)}.{int(m.group(2))}"
    m = re.search(r"Chapter\s+([IVXLC]+|\d+)", title, re.I)
    if m:
        return m.group(1)
    m = re.search(r"Commandment\s+(\d+)|Mandate\s+(\d+)|Similitude\s+(\d+)", title, re.I)
    if m:
        return "Mand." + next(g for g in m.groups() if g)
    m = re.search(r"0312(\d)", path)
    if m:
        return f"Book {m.group(1)}"
    m = re.search(r"0412(\d)", path)
    if m:
        return {0: "Preface", 1: "1", 2: "2", 3: "3", 4: "4"}.get(int(m.group(1)), m.group(1))
    return re.sub(r"\s+", " ", title)[:48]


def score(topic: str, text: str) -> int:
    rules = TOPIC_RULES[topic]
    if any(re.search(b, text, re.I) for b in rules["ban"]):
        return 0
    if not any(re.search(p, text, re.I) for p in rules["need_any"]):
        return 0
    sc = 0
    for p in rules["need_strong"]:
        sc += 4 * len(re.findall(p, text, re.I))
    for p in rules["need_any"]:
        sc += len(re.findall(p, text, re.I))
    return sc


def paragraphs(text: str, max_chars: int = 1500, limit: int = 4):
    bits = re.split(r"(?=\b\d+\.\s)", text)
    bits = [b.strip() for b in bits if len(b.strip()) > 90]
    if len(bits) < 2:
        sents = re.split(r"(?<=[.!?])\s+", text)
        bits, buf = [], ""
        for s in sents:
            if len(buf) + len(s) > 850 and buf:
                bits.append(buf.strip())
                buf = s
            else:
                buf = (buf + " " + s).strip()
        if buf:
            bits.append(buf.strip())
    out = []
    for b in bits:
        if len(b) > max_chars:
            b = b[:max_chars].rsplit(" ", 1)[0] + "…"
        if len(b) > 100:
            out.append(b)
        if len(out) >= limit:
            break
    return out


def source_url(path: str) -> str:
    m = re.search(r"anf_cache/(01\d+|02\d+|03\d+|04\d+|05\d+|2501\d*)\.html$", path)
    if m:
        return f"https://www.newadvent.org/fathers/{m.group(1)}.htm"
    if "ccel_" in path:
        return "https://www.ccel.org/ccel/schaff/" + Path(path).name.replace("ccel_", "") + ".html"
    return path


def main():
    chapters = []
    files_read = []
    paths = list((ROOT / "sources").glob("*.html")) + list(CACHE.glob("*.html"))
    for path in sorted(paths):
        if path.stat().st_size < 2000:
            continue
        raw = path.read_text(errors="replace")
        files_read.append(str(path.relative_to(ROOT)))
        for title, body in split_chapters(raw, path.name):
            meta = meta_for(path, title)
            if not meta or meta[1] == "skip":
                continue
            author, work, period, kind, authenticity, lang = meta
            if len(body) < 220:
                continue
            if re.search(r"Submit Search|Encyclopedia Summa", body):
                continue
            chapters.append(
                dict(
                    path=str(path.relative_to(ROOT)),
                    title=title,
                    body=body,
                    author=author,
                    work=work,
                    period=period,
                    kind=kind,
                    authenticity=authenticity,
                    lang=lang,
                )
            )

    print("chapters", len(chapters), "files", len(set(files_read)))

    excerpts = []
    seen_keys = set()
    seen_body = set()
    id_counts = Counter()
    files_used = set()
    counts = Counter()

    def make_id(author, work, locus, topic):
        a = re.sub(r"[^a-z0-9]+", "_", author.lower()).strip("_")[:20]
        w = re.sub(r"[^a-z0-9]+", "_", work.lower()).strip("_")[:24]
        l = re.sub(r"[^a-z0-9]+", "_", str(locus).lower()).strip("_")[:18]
        base = f"{a}_{w}_{l}_{topic[:12]}"
        id_counts[base] += 1
        if id_counts[base] > 1:
            base = f"{base}_{id_counts[base]}"
        return base

    def add(topic, ch, sc, extra_notes=None):
        locus = locus_of(ch["title"], ch["work"], ch["path"])
        key = (ch["author"], ch["work"], locus, topic)
        if key in seen_keys:
            return False
        sig = hashlib.md5((topic + ch["body"][:350]).encode()).hexdigest()
        if sig in seen_body:
            return False
        paras = paragraphs(ch["body"])
        if not paras:
            return False
        blob = " ".join(paras)
        if re.search(r"Submit Search|\$19\.99|Catholic Encyclopedia|CHURCH FATHERS:", blob):
            return False
        seen_keys.add(key)
        seen_body.add(sig)
        notes = []
        if ch["author"].startswith("Eusebius"):
            notes.append(
                "SECONDARY WITNESS: Eusebius HE — historical report of earlier material, not an ante-Nicene dogmatic voice."
            )
        if topic == "gifts-and-order" and "Tertullian" in ch["author"]:
            notes.append("Montanist-period context possible — label gifts-and-order as debate.")
        if topic == "hermeneutics-types" and "Origen" in ch["author"]:
            notes.append("Development: do not flatten Origen’s allegory into the only ante-Nicene method.")
        if topic == "lxx-and-form":
            notes.append("Keep the father’s cited LXX/Hebrew form; do not correct to NA28/ESV.")
        if extra_notes:
            notes.extend(extra_notes)
        notes.append(f"seed relevance score {sc}; ANF English cleaned; not source_verified.")
        excerpts.append(
            {
                "id": make_id(ch["author"], ch["work"], locus, topic),
                "topic": topic,
                "citation": f"{ch['author']} — {ch['work']} {locus}",
                "author": ch["author"],
                "work": ch["work"],
                "locus": str(locus),
                "period": ch["period"],
                "kind": ch["kind"],
                "confidence": "seed_anf",
                "source": source_url(ch["path"]),
                "english": paras,
                "translator_notes": [
                    "ANF/New Advent or local ANF HTML seed; lightly cleaned. Edition lock pending."
                ],
                "authenticity": ch["authenticity"],
                "notes": notes,
                "added_allusions": [],
                "edition_id": None,
                "source_language": ch["lang"],
            }
        )
        files_used.add(ch["path"])
        counts[topic] += 1
        return True

    for path_sub, title_re, topics in FORCE:
        for ch in chapters:
            if path_sub.lower() not in ch["path"].lower():
                continue
            if title_re != r"." and not re.search(title_re, ch["title"] + " " + ch["body"][:80], re.I):
                continue
            for topic in topics:
                sc = max(score(topic, ch["body"]), 8)
                add(topic, ch, sc, extra_notes=["Forced priority locus for topic fill."])

    by_topic = defaultdict(list)
    for ch in chapters:
        for topic in TOPIC_RULES:
            sc = score(topic, ch["body"])
            if sc >= MIN[topic]:
                by_topic[topic].append((sc, ch))

    for topic, items in by_topic.items():
        items.sort(key=lambda x: -x[0])
        for sc, ch in items:
            if counts[topic] >= SOFT[topic]:
                break
            add(topic, ch, sc)

    order = list(TOPIC_RULES)
    excerpts.sort(key=lambda e: (order.index(e["topic"]), e["period"], e["author"], e["locus"]))

    gaps = [
        "Local Irenaeus English was free-will chapters only; AH bibliology/pneumatology loci filled from New Advent/CCEL ANF cache.",
        "Local Tertullian Marcion HTML is Book II; Books I/III/IV/V + Prescription + On Baptism from anf_cache.",
        "Origen Princ Pref + Book 4 (inspiration/hermeneutics) from anf_cache; local Princ English is Book III-centric.",
        "Justin Dialogue (incl. LXX 71–73) not in local sources/; from New Advent/CCEL cache.",
        "Melito On Pascha Greek sources in-repo are empty/broken; Melito OT books via Eusebius HE only (secondary).",
        "seed_edition Greek/Latin line-locks not attached in this pass (edition_id null) — next upgrade wave.",
        "Muratorian Fragment absent from corpus.",
        "gifts-and-order thinner than inspiration topics: Didache 11–15, Hermas Mand.11, Irenaeus gifts, Hippolytus on Montanus, Tertullian On Baptism/related.",
    ]

    coverage = " ".join(
        [
            f"Deep seed harvest for bibliology+pneumatology: {len(excerpts)} excerpts across {len(counts)} topics from {len(set(files_read))} files read ({len(files_used)} used).",
            "English is ANF seed (seed_anf), cleaned of New Advent nav chrome; no source_verified claims.",
            "Eusebius HE flagged secondary. Tertullian Montanist-leaning gift texts flagged as debate.",
            f"Per-topic counts: {dict(counts)}.",
            "Thin relative to corpus reality: gifts-and-order and some spirit-and-baptism depend on Didache/Hermas/Hippolytus/Irenaeus/Tertullian On Baptism rather than universal density.",
        ]
    )

    payload = {
        "locus": "bibliology+pneumatology",
        "mined_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "coverage_notes": coverage,
        "counts_per_topic": dict(counts),
        "files_read": sorted(set(files_read)),
        "files_used": sorted(files_used),
        "gaps": gaps,
        "excerpts": excerpts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("Wrote", OUT)
    print("counts", dict(counts))
    print("total", len(excerpts), "unique_ids", len({e["id"] for e in excerpts}))
    unk = sum(1 for e in excerpts if e["author"] in ("Unknown", "(misfiled)"))
    junk = sum(1 for e in excerpts if re.search(r"Submit Search|CHURCH FATHERS:", " ".join(e["english"])))
    print("unknown", unk, "junk", junk)
    for t in order:
        ex = [e for e in excerpts if e["topic"] == t]
        print(t, counts[t], "sample:", ex[0]["citation"] if ex else "-")


if __name__ == "__main__":
    main()
