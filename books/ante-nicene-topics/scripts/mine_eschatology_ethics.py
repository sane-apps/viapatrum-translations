#!/usr/bin/env python3
"""Deep mine eschatology + ethics/apologetics candidates from local sources + ANF cache."""
from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "outputs/mining/anf_cache"
OUT = ROOT / "outputs/mining/eschatology_ethics_candidates.json"

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
    "dionysius_alexandria.html": ("Methodius", "Discourse on the Resurrection (ANF misc)", "c. 270–300", "Treatise", "contested", "grc"),
    "tertullian_resurrection_flesh.html": (
        "Tertullian",
        "On the Resurrection of the Flesh",
        "c. 208–212",
        "Treatise",
        "accepted",
        "lat",
    ),
    "melito_passover.html": ("(misfiled)", "skip", "", "", "", ""),
    "melito_apology.html": ("(misfiled)", "skip", "", "", "", ""),
}

CACHE_META_PREFIX = [
    (r"^0103", "Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    (r"^0126", "Justin Martyr", "First Apology", "c. 155", "Apology", "accepted", "grc"),
    (r"^0127", "Justin Martyr", "Second Apology", "c. 155", "Apology", "accepted", "grc"),
    (r"^0128", "Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc"),
    (r"^0130", "Justin Martyr (attrib.)", "On the Sole Government of God", "c. 2nd?", "Treatise", "contested", "grc"),
    (r"^0131", "Justin Martyr (attrib.)", "On the Resurrection", "c. 2nd?", "Treatise", "contested", "grc"),
    (r"^0202", "Tatian", "Address to the Greeks", "c. 165", "Apology", "accepted", "grc"),
    (r"^0204", "Theophilus of Antioch", "To Autolycus", "c. 180", "Apology", "accepted", "grc"),
    (r"^0205", "Athenagoras", "Plea for the Christians", "c. 177", "Apology", "accepted", "grc"),
    (r"^0206", "Athenagoras", "On the Resurrection of the Dead", "c. 177", "Treatise", "accepted", "grc"),
    (r"^0209", "Clement of Alexandria", "Paedagogus", "c. 200", "Treatise", "accepted", "grc"),
    (r"^0210", "Clement of Alexandria", "Stromata", "c. 200", "Treatise", "accepted", "grc"),
    (r"^0101", "Mathetes", "Epistle to Diognetus", "c. 150?", "Letter", "accepted", "grc"),
    (r"^0124", "Barnabas (Epistle)", "Epistle of Barnabas", "c. 100–130", "Letter", "contested", "grc"),
    (r"^0104", "Ignatius of Antioch", "To the Ephesians", "c. 110", "Letter", "accepted", "grc"),
    (r"^0109", "Ignatius of Antioch", "To the Smyrnaeans", "c. 110", "Letter", "accepted", "grc"),
    (r"^0301", "Tertullian", "Apology", "c. 197", "Apology", "accepted", "lat"),
    (r"^0302", "Tertullian", "On Idolatry", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0303", "Tertullian", "De Spectaculis", "c. 197–202", "Treatise", "accepted", "lat"),
    (r"^0304", "Tertullian", "De Corona", "c. 211", "Treatise", "accepted", "lat"),
    (r"^0305", "Tertullian", "To Scapula", "c. 212", "Letter", "accepted", "lat"),
    (r"^0306", "Tertullian", "Ad Nationes", "c. 197", "Apology", "accepted", "lat"),
    (r"^0308", "Tertullian", "An Answer to the Jews", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0309", "Tertullian", "The Soul's Testimony", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0310", "Tertullian", "A Treatise on the Soul", "c. 210", "Treatise", "accepted", "lat"),
    (r"^0311", "Tertullian", "Prescription against Heretics", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0312", "Tertullian", "Against Marcion", "c. 207", "Treatise", "accepted", "lat"),
    (r"^0313", "Tertullian", "Against Hermogenes", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0314", "Tertullian", "Against the Valentinians", "c. 207", "Treatise", "accepted", "lat"),
    (r"^0315", "Tertullian", "On the Flesh of Christ", "c. 208–212", "Treatise", "accepted", "lat"),
    (r"^0317", "Tertullian", "Against Praxeas", "c. 213", "Treatise", "accepted", "lat"),
    (r"^0318", "Tertullian", "Scorpiace", "c. 213", "Treatise", "accepted", "lat"),
    (r"^0319", "Tertullian", "Against All Heresies", "c. 200?", "Treatise", "contested", "lat"),
    (r"^0320", "Tertullian", "On Repentance", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0322", "Tertullian", "On Prayer", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0323", "Tertullian", "To the Martyrs", "c. 197", "Letter", "accepted", "lat"),
    (r"^0324", "Passion of Perpetua and Felicity", "Passion of Perpetua and Felicity", "c. 203", "Martyr act", "accepted", "lat"),
    (r"^0325", "Tertullian", "Of Patience", "c. 200", "Treatise", "accepted", "lat"),
    (r"^0402", "Tertullian", "On the Apparel of Women", "c. 202", "Treatise", "accepted", "lat"),
    (r"^0403", "Tertullian", "On the Veiling of Virgins", "c. 204", "Treatise", "accepted", "lat"),
    (r"^0404", "Tertullian", "To His Wife", "c. 200–206", "Treatise", "accepted", "lat"),
    (r"^0405", "Tertullian", "On Exhortation to Chastity", "c. 204–212", "Treatise", "accepted", "lat"),
    (r"^0406", "Tertullian", "On Monogamy", "c. 217", "Treatise", "accepted", "lat"),
    (r"^0407", "Tertullian", "On Modesty", "c. 217–222", "Treatise", "accepted", "lat"),
    (r"^0408", "Tertullian", "On Fasting", "c. 217–222", "Treatise", "accepted", "lat"),
    (r"^0409", "Tertullian", "De Fuga in Persecutione", "c. 208–212", "Treatise", "accepted", "lat"),
    (r"^0410", "Minucius Felix", "Octavius", "c. 200", "Dialogue", "accepted", "lat"),
    (r"^0411", "Commodian", "Instructions", "c. 250?", "Poem", "accepted", "lat"),
    (r"^0412", "Origen", "On First Principles", "c. 230", "Treatise", "accepted", "grc"),
    (r"^0416", "Origen", "Against Celsus", "c. 248", "Treatise", "accepted", "grc"),
    (r"^0501", "Hippolytus", "Refutation of All Heresies", "c. 220", "Treatise", "accepted", "grc"),
    (r"^0516", "Hippolytus", "On Christ and Antichrist", "c. 200–210", "Treatise", "accepted", "grc"),
    (r"^0507", "Cyprian of Carthage", "Treatises", "c. 250", "Treatise", "accepted", "lat"),
    (r"^0623", "Methodius", "Banquet of the Ten Virgins", "c. 270–300", "Dialogue", "accepted", "grc"),
    (r"^0701", "Lactantius", "Divine Institutes", "c. 304–310", "Treatise", "accepted", "lat"),
    (r"^0714", "Didache", "Didache", "c. 100", "Church order", "accepted", "grc"),
    (r"^2501", "Eusebius of Caesarea", "Church History", "c. 325", "History", "accepted", "grc"),
    (r"^0612", "Dionysius of Alexandria", "Fragments", "c. 250", "Fragment", "accepted", "grc"),
    (r"ccel_anf01\.viii", "Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc"),
    (r"ccel_anf01\.ix", "Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat"),
    (r"tertullian_resurrection", "Tertullian", "On the Resurrection of the Flesh", "c. 208–212", "Treatise", "accepted", "lat"),
]

CYPRIAN_TITLES = {
    "050701": "On the Unity of the Church",
    "050702": "On the Dress of Virgins",
    "050703": "On the Lapsed",
    "050704": "On the Lord's Prayer",
    "050705": "An Address to Demetrianus",
    "050706": "On the Vanity of Idols",
    "050707": "On the Mortality",
    "050708": "On Works and Alms",
    "050709": "On the Advantage of Patience",
    "050710": "On Jealousy and Envy",
    "050711": "Exhortation to Martyrdom",
}

TOPIC_RULES = {
    "resurrection-body": {
        "need_any": [
            r"resurrect",
            r"rise again",
            r"rising again",
            r"bodies? (shall |will )?(be )?(raised|rise)",
            r"flesh.*(rise|raised|immortal)",
            r"immortalit",
        ],
        "need_strong": [
            r"resurrection of the (flesh|body|dead)",
            r"bodies?.*(raised|rise|resurrection)",
            r"flesh.*(rise|raised|resurrection)",
            r"same body",
            r"this flesh",
            r"palpable flesh",
            r"immortality of the body",
        ],
        "ban": [r"^All hail, you sons"],
    },
    "judgment-second-coming": {
        "need_any": [
            r"judgment of God",
            r"last judgment",
            r"second coming",
            r"coming of (the )?Christ",
            r"advent of Christ",
            r"last (day|time|times)",
            r"day of (the )?Lord",
            r"eternal (fire|punishment)",
            r"Antichrist",
            r"future (and )?just judgment",
        ],
        "need_strong": [
            r"(last|final|future|just) judgment",
            r"judgment of God",
            r"second coming|coming of Christ|advent of Christ",
            r"eternal (fire|punishment)",
            r"Antichrist",
            r"day of (the )?Lord",
            r"reward.{0,40}(deed|work)|according to (their |his )?(deeds|works)",
        ],
        "ban": [],
    },
    "millennium-debate": {
        "need_any": [
            r"thousand years",
            r"millennium",
            r"chiliast",
            r"six thousand",
            r"new Jerusalem",
            r"reign.{0,40}(earth|Christ|saints)",
            r"Papias",
            r"Sabbath.{0,40}thousand|thousand.{0,40}Sabbath",
        ],
        "need_strong": [
            r"thousand years",
            r"six thousand years",
            r"millennium|chiliast",
            r"new Jerusalem",
            r"reign.{0,60}(thousand|earth)",
            r"Papias",
            r"eighth day",
        ],
        "ban": [],
    },
    "heaven-hell-intermediate": {
        "need_any": [
            r"\bHades\b",
            r"paradise",
            r"hell",
            r"gehenna",
            r"Abraham.?s bosom",
            r"lower regions",
            r"underworld",
            r"souls?.*(depart|wait|rest|torment)",
            r"intermediate",
            r"place of (the )?dead",
        ],
        "need_strong": [
            r"\bHades\b",
            r"paradise",
            r"Abraham.?s bosom",
            r"gehenna|eternal (fire|punishment)",
            r"souls?.{0,50}(body|flesh|resurrection|wait|depart)",
            r"lower regions",
            r"torment",
        ],
        "ban": [],
    },
    "love-neighbor-enemy": {
        "need_any": [
            r"love.{0,40}(enem|neighbor|neighbour)",
            r"pray for.{0,40}(persecut|enem)",
            r"two ways",
            r"do good to",
            r"bless.{0,20}(curse|them that)",
            r"enemy",
            r"neighbour|neighbor",
        ],
        "need_strong": [
            r"love.{0,30}(your |thy )?(enem|neighbor|neighbour)",
            r"pray for.{0,40}(them that|those who).{0,30}(persecut|hate|enem)",
            r"two ways",
            r"do good to.{0,30}(hate|enem)",
            r"bless those who curse",
        ],
        "ban": [],
    },
    "sexual-marriage": {
        "need_any": [
            r"marriage",
            r"fornicat",
            r"adulter",
            r"continence",
            r"chastit",
            r"virginit",
            r"\blust\b",
            r"wife",
            r"husband",
            r"monogamy",
            r"second marriage",
        ],
        "need_strong": [
            r"marriage",
            r"fornicat|adulter",
            r"continence|chastit|virginit",
            r"second marriage|monogamy",
            r"one wife|one husband",
            r"veil|apparel of women",
        ],
        "ban": [],
    },
    "wealth-alms": {
        "need_any": [
            r"\balms?\b",
            r"rich(es|est)?",
            r"wealth",
            r"possessions",
            r"\bpoor\b",
            r"money",
            r"mammon",
            r"liberality",
            r"give to",
            r"works and alms",
        ],
        "need_strong": [
            r"\balms?\b",
            r"rich.{0,40}(poor|camel|needle|hard)",
            r"give.{0,30}(poor|needy|alms)",
            r"possessions|mammon|wealth",
            r"liberality",
            r"works and alms",
        ],
        "ban": [],
    },
    "martyrdom-witness": {
        "need_any": [
            r"martyr",
            r"persecut",
            r"confess",
            r"suffer.{0,40}(Christ|death|name)",
            r"blood.{0,30}(witness|shed)",
            r"crown",
            r"torture",
        ],
        "need_strong": [
            r"martyr",
            r"persecut",
            r"confess.{0,40}(Christ|name|faith)",
            r"suffer.{0,40}(Christ|death|martyr)",
            r"exhortation to martyrdom",
            r"to the martyrs",
        ],
        "ban": [],
    },
    "civil-authority": {
        "need_any": [
            r"emperor",
            r"\bCaesar\b",
            r"magistrate",
            r"tribute",
            r"soldier",
            r"warfare|military|bearing arms",
            r"obey.{0,30}(ruler|king|magistrate|authority)",
            r"king to be honour",
            r"kingdoms? of (this )?world",
            r"\bempire\b",
            r"Scapula",
            r"chaplet|De Corona|military crown",
        ],
        "need_strong": [
            r"emperor|\bCaesar\b",
            r"tribute|tax",
            r"soldier|military|warfare|bearing arms|chaplet|corona",
            r"magistrate",
            r"obey.{0,40}(authority|ruler|king|emperor)",
            r"king to be honour",
            r"Scapula",
        ],
        "ban": [],
    },
    "apologetic-method": {
        "need_any": [
            r"prophe(t|cy|cies|sies).{0,60}(prove|fulfill|predict|foretold|demonstrate)",
            r"antiquit",
            r"by reason|reason.{0,40}(faith|truth|God)",
            r"philosoph.{0,50}(borrow|stole|truth|Moses|barbarian)",
            r"miracle|wonders?",
            r"Sibyl",
            r"testimony of (the )?(prophets|poets|philosophers)",
            r"prove.{0,40}(from|by).{0,30}(scripture|prophet|reason)",
        ],
        "need_strong": [
            r"prophe(t|cy|cies|sies).{0,50}(prove|fulfill|predict|foretold)",
            r"antiquit",
            r"by reason|reason.{0,40}(faith|truth|God)",
            r"philosoph.{0,50}(borrow|stole|truth|Moses|barbarian)",
            r"miracle|wonders?",
            r"Sibyl",
            r"testimony of (the )?(prophets|poets|philosophers)",
            r"prove.{0,40}(from|by).{0,30}(scripture|prophet|reason)",
        ],
        "ban": [],
    },
}

# Require at least one strong hit (score from strong patterns alone >= 4).
MIN = {k: 8 for k in TOPIC_RULES}
MIN.update(
    {
        "millennium-debate": 4,
        "heaven-hell-intermediate": 6,
        "love-neighbor-enemy": 6,
        "wealth-alms": 6,
        "apologetic-method": 8,
        "civil-authority": 8,
        "judgment-second-coming": 8,
        "resurrection-body": 8,
        "martyrdom-witness": 8,
        "sexual-marriage": 8,
    }
)
# Soft caps: dozens per topic; no ultra-thin 4–8, but curb keyword flood.
SOFT = {k: 48 for k in TOPIC_RULES}
SOFT.update(
    {
        "millennium-debate": 36,
        "heaven-hell-intermediate": 36,
        "love-neighbor-enemy": 36,
        "wealth-alms": 40,
        "civil-authority": 40,
        "apologetic-method": 42,
        "judgment-second-coming": 48,
        "resurrection-body": 48,
        "martyrdom-witness": 42,
        "sexual-marriage": 42,
    }
)

FORCE = [
    # Resurrection
    ("justin_apology1_43.html", r"Chapter 18", ["resurrection-body", "heaven-hell-intermediate"]),
    ("justin_apology1_43.html", r"Chapter 19", ["resurrection-body"]),
    ("justin_apology1_43.html", r"Chapter 52", ["judgment-second-coming", "resurrection-body"]),
    ("justin_apology1_43.html", r"Chapter 8", ["judgment-second-coming", "heaven-hell-intermediate"]),
    ("justin_2apology.html", r"Chapter 9", ["judgment-second-coming"]),
    ("01286", r"Chapter 80", ["millennium-debate"]),
    ("01286", r"Chapter 81", ["millennium-debate"]),
    ("0131", r"Chapter", ["resurrection-body"]),
    ("0206", r"Chapter", ["resurrection-body"]),
    ("athenagoras_plea.html", r"Chapter 31", ["sexual-marriage", "apologetic-method"]),
    ("athenagoras_plea.html", r"Chapter 32", ["sexual-marriage"]),
    ("athenagoras_plea.html", r"Chapter 33", ["love-neighbor-enemy"]),
    ("athenagoras_plea.html", r"Chapter 35", ["judgment-second-coming"]),
    ("athenagoras_plea.html", r"Chapter 36", ["resurrection-body"]),
    ("Tatian_address.html", r"Chapter 6", ["resurrection-body"]),
    ("theophilus_autolycus.html", r"Chapter 7", ["resurrection-body", "heaven-hell-intermediate"]),
    ("theophilus_autolycus.html", r"Chapter 13", ["resurrection-body"]),
    ("theophilus_autolycus.html", r"Chapter 11", ["civil-authority"]),
    ("minucius_octavius.html", r"Chapter 34", ["resurrection-body"]),
    ("minucius_octavius.html", r"Chapter 35", ["judgment-second-coming", "heaven-hell-intermediate"]),
    ("minucius_octavius.html", r"Chapter 37", ["martyrdom-witness"]),
    ("irenaeus_ah_5_28.html", r".", ["millennium-debate", "judgment-second-coming"]),
    ("0103530", r".", ["millennium-debate", "judgment-second-coming"]),
    ("0103531", r".", ["heaven-hell-intermediate", "resurrection-body"]),
    ("0103532", r".", ["millennium-debate", "resurrection-body"]),
    ("0103533", r".", ["millennium-debate"]),
    ("0103534", r".", ["millennium-debate"]),
    ("0103535", r".", ["millennium-debate", "heaven-hell-intermediate"]),
    ("0103536", r".", ["millennium-debate", "heaven-hell-intermediate"]),
    ("0103506", r".", ["resurrection-body"]),
    ("barnabas.html", r"Chapter 15", ["millennium-debate"]),
    ("barnabas.html", r"Chapter 19", ["love-neighbor-enemy", "wealth-alms", "sexual-marriage"]),
    ("barnabas.html", r"Chapter 21", ["judgment-second-coming"]),
    ("didache.html", r"Chapter 1", ["love-neighbor-enemy"]),
    ("didache.html", r"Chapter 2", ["sexual-marriage", "love-neighbor-enemy"]),
    ("didache.html", r"Chapter 3", ["sexual-marriage"]),
    ("didache.html", r"Chapter 4", ["wealth-alms", "civil-authority"]),
    ("didache.html", r"Chapter 16", ["judgment-second-coming"]),
    ("mathetes_diognetus.html", r"Chapter 5", ["love-neighbor-enemy", "civil-authority", "sexual-marriage"]),
    ("mathetes_diognetus.html", r"Chapter 6", ["civil-authority"]),
    ("hermas_mandates.html", r"Commandment 4", ["sexual-marriage"]),
    ("hermas_similitudes.html", r"Similitude 1", ["wealth-alms"]),
    ("hermas_similitudes.html", r"Similitude 2", ["wealth-alms"]),
    ("victorinus_creation.html", r".", ["millennium-debate"]),
    ("commodian_instructions.html", r".", ["millennium-debate", "judgment-second-coming"]),
    ("0411", r".", ["millennium-debate"]),
    # Lactantius Inst VII
    ("07017", r"Chapter 14", ["millennium-debate"]),
    ("07017", r"Chapter 19", ["judgment-second-coming"]),
    ("07017", r"Chapter 20", ["judgment-second-coming"]),
    ("07017", r"Chapter 21", ["heaven-hell-intermediate"]),
    ("07017", r"Chapter 23", ["resurrection-body"]),
    ("07017", r"Chapter 24", ["millennium-debate"]),
    ("07017", r"Chapter 26", ["judgment-second-coming", "millennium-debate"]),
    ("07016", r"Chapter 11", ["love-neighbor-enemy"]),
    ("07016", r"Chapter 12", ["wealth-alms"]),
    ("07016", r"Chapter 19", ["wealth-alms"]),
    ("07016", r"Chapter 23", ["sexual-marriage"]),
    ("07015", r"Chapter 8", ["civil-authority"]),
    ("07015", r"Chapter 17", ["apologetic-method"]),
    ("lactantius_institutes1.html", r"Chapter 5", ["apologetic-method"]),
    ("lactantius_institutes1.html", r"Chapter 6", ["apologetic-method"]),
    # Tertullian — specific chapters only
    ("tertullian_resurrection_flesh.html", r"Chapter I\b", ["resurrection-body"]),
    ("tertullian_resurrection_flesh.html", r"Chapter II\b", ["resurrection-body"]),
    ("tertullian_resurrection_flesh.html", r"Chapter XIV\b", ["resurrection-body"]),
    ("tertullian_resurrection_flesh.html", r"Chapter XV\b", ["resurrection-body"]),
    ("tertullian_resurrection_flesh.html", r"Chapter XXXV\b", ["resurrection-body"]),
    ("tertullian_resurrection_flesh.html", r"Chapter LXIII\b", ["resurrection-body"]),
    ("0301", r"Chapter 21", ["apologetic-method"]),
    ("0301", r"Chapter 39", ["love-neighbor-enemy", "wealth-alms", "sexual-marriage"]),
    ("0301", r"Chapter 42", ["civil-authority"]),
    ("0301", r"Chapter 48", ["resurrection-body"]),
    ("0301", r"Chapter 50", ["martyrdom-witness"]),
    ("0302", r"Chapter 15", ["civil-authority"]),
    ("0302", r"Chapter 17", ["civil-authority"]),
    ("0302", r"Chapter 19", ["civil-authority"]),
    ("0303", r"Chapter 1", ["civil-authority"]),
    ("0304", r"Chapter 1", ["civil-authority", "martyrdom-witness"]),
    ("0304", r"Chapter 11", ["civil-authority"]),
    ("0305", r".", ["civil-authority", "martyrdom-witness"]),
    ("0323", r".", ["martyrdom-witness"]),
    ("0318", r"Chapter 1", ["martyrdom-witness"]),
    ("0318", r"Chapter 4", ["martyrdom-witness"]),
    ("0404", r"Chapter 1", ["sexual-marriage"]),
    ("0404", r"Chapter 2", ["sexual-marriage"]),
    ("0405", r"Chapter 1", ["sexual-marriage"]),
    ("0406", r"Chapter 1", ["sexual-marriage"]),
    ("0402", r"Chapter 1", ["sexual-marriage"]),
    ("0403", r"Chapter 1", ["sexual-marriage"]),
    ("0310", r"Chapter 55", ["heaven-hell-intermediate"]),
    ("0310", r"Chapter 56", ["heaven-hell-intermediate"]),
    ("0310", r"Chapter 58", ["heaven-hell-intermediate"]),
    ("0315", r"Chapter 1", ["resurrection-body"]),
    ("0315", r"Chapter 5", ["resurrection-body"]),
    # Origen — pick high-signal chapters
    ("04122", r"Chapter 10", ["resurrection-body"]),
    ("04122", r"Chapter 11", ["heaven-hell-intermediate"]),
    ("04165", r"Chapter 18", ["resurrection-body"]),
    ("04165", r"Chapter 19", ["resurrection-body"]),
    ("04167", r"Chapter 9", ["apologetic-method"]),
    ("04167", r"Chapter 28", ["judgment-second-coming"]),
    ("04168", r"Chapter 65", ["civil-authority"]),
    ("04168", r"Chapter 68", ["civil-authority"]),
    ("04168", r"Chapter 72", ["judgment-second-coming"]),
    ("04162", r"Chapter 48", ["resurrection-body"]),
    ("origen_celsus.html", r"Chapter 9", ["apologetic-method"]),
    ("origen_celsus.html", r"Chapter 2", ["apologetic-method"]),
    # Methodius / Hippolytus / Cyprian
    ("dionysius_alexandria.html", r"Part 1", ["resurrection-body"]),
    ("dionysius_alexandria.html", r"Part 2", ["resurrection-body", "heaven-hell-intermediate"]),
    ("dionysius_alexandria.html", r"Part 3", ["heaven-hell-intermediate"]),
    ("062301", r".", ["sexual-marriage"]),
    ("062302", r".", ["sexual-marriage"]),
    ("062303", r".", ["sexual-marriage"]),
    ("062311", r".", ["sexual-marriage"]),
    ("0516", r"Chapter 1", ["judgment-second-coming"]),
    ("0516", r"Chapter 5", ["judgment-second-coming"]),
    ("0516", r"Chapter 43", ["millennium-debate", "judgment-second-coming"]),
    ("0516", r"Chapter 44", ["millennium-debate"]),
    ("050708", r".", ["wealth-alms"]),
    ("050711", r".", ["martyrdom-witness"]),
    ("050702", r".", ["sexual-marriage"]),
    ("050705", r".", ["civil-authority", "apologetic-method"]),
    ("050707", r".", ["martyrdom-witness", "heaven-hell-intermediate"]),
    ("050709", r".", ["martyrdom-witness"]),
    ("clement_instructor.html", r"Chapter 4", ["sexual-marriage"]),
    ("clement_instructor.html", r"Chapter 10", ["wealth-alms"]),
    ("clement_instructor.html", r"Chapter 11", ["wealth-alms"]),
    ("clement_instructor.html", r"Chapter 12", ["love-neighbor-enemy"]),
    ("02093", r"Chapter 1", ["sexual-marriage"]),
    ("02093", r"Chapter 2", ["sexual-marriage"]),
    ("ignatius_smyrnaeans.html", r"Chapter 3", ["resurrection-body"]),
    ("ignatius_smyrnaeans.html", r"Chapter 4", ["martyrdom-witness"]),
    ("0324", r".", ["martyrdom-witness"]),
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
    # Common New Advent chapter-page chrome
    s = re.sub(
        r"(?is)^(?:Home\s*>.*?|CHURCH FATHERS:.*?)(?=\d+\.\s|For |Now |But |And |When |It |The |We |This |These |Since |Moreover |Further )",
        "",
        s,
        count=1,
    )
    s = re.sub(r"(?is)Against Heresies \(Book [IVXLC]+,?\s*Chapter \d+\)\s*", "", s)
    s = re.sub(r"(?is)Ante-Nicene Fathers, Vol\.\s*[IVXLC0-9]+\s*:\s*", "", s)
    return s.strip()


def split_chapters(raw: str, fname: str):
    # Tertullian.org ANF On Resurrection: body chapters use <FONT SIZE=3>Chapter I.-...
    if "tertullian_resurrection" in fname:
        parts = re.split(
            r"(?i)(<FONT\s+SIZE=3>\s*Chapter\s+[IVXLC]+\.\-[^<]{0,220})",
            raw,
        )
        out = []
        if len(parts) > 3:
            i = 1
            while i + 1 < len(parts):
                head = strip_html(parts[i])
                body = clean_body(strip_html(parts[i + 1]))
                body = re.split(r"(?i)<FONT\s+SIZE=3>\s*Chapter\s+|Elucidations", body)[0].strip()
                m = re.search(r"Chapter\s+([IVXLC]+)", head, re.I)
                if m and len(body) > 160:
                    out.append((f"Chapter {m.group(1)}", body))
                i += 2
            if out:
                return out
    # Standard New Advent <h2>Chapter N. Title</h2>
    parts = re.split(r"(?i)(<h2[^>]*>\s*Chapter\s+[^<]+</h2>)", raw)
    out = []
    if len(parts) == 1:
        parts_rom = re.split(r"(?i)((?:<h2[^>]*>|<p[^>]*>|<b>)\s*Chapter\s+[IVXLC0-9]+\.?\s*[^<]{0,120}(?:</h2>|</b>|</p>))", raw)
        if len(parts_rom) > 3:
            parts = parts_rom
    if len(parts) == 1:
        parts2 = re.split(r"(?i)(<h2[^>]*>[^<]{3,160}</h2>)", raw)
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
        # Commodian / Arnobius: numbered poem sections
        parts_num = re.split(r"(?i)(<h[23][^>]*>\s*[IVXLC0-9]+\.?\s*[^<]{3,100}</h[23]>)", raw)
        if len(parts_num) > 3:
            i = 1
            while i + 1 < len(parts_num):
                head = strip_html(parts_num[i])
                body = clean_body(strip_html(parts_num[i + 1]))
                ab = re.search(r"About this page", body, re.I)
                if ab:
                    body = body[: ab.start()].strip()
                if len(body) > 180:
                    out.append((head, body))
                i += 2
            if out:
                return out
        title_m = re.search(r"<title>([^<]+)", raw, re.I) or re.search(r"<h1[^>]*>([^<]+)", raw, re.I)
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
            meta = list(rest)
            if stem[:6] in CYPRIAN_TITLES:
                meta[1] = f"Treatises — {CYPRIAN_TITLES[stem[:6]]}"
            if re.match(r"0623\d+", stem):
                meta[1] = "Banquet of the Ten Virgins"
            return tuple(meta)
    t = title.lower()
    if "irenaeus" in t or "heresies" in t:
        return ("Irenaeus", "Against Heresies", "c. 180", "Treatise", "accepted", "lat")
    if "justin" in t and "trypho" in t:
        return ("Justin Martyr", "Dialogue with Trypho", "c. 155", "Dialogue", "accepted", "grc")
    if "resurrection of the flesh" in t:
        return ("Tertullian", "On the Resurrection of the Flesh", "c. 208–212", "Treatise", "accepted", "lat")
    if "lactantius" in t or "institutes" in t:
        return ("Lactantius", "Divine Institutes", "c. 304–310", "Treatise", "accepted", "lat")
    if "athenagoras" in t and "resurrect" in t:
        return ("Athenagoras", "On the Resurrection of the Dead", "c. 177", "Treatise", "accepted", "grc")
    if "methodius" in t:
        return ("Methodius", "Banquet of the Ten Virgins", "c. 270–300", "Dialogue", "accepted", "grc")
    if "hippolytus" in t and "antichrist" in t:
        return ("Hippolytus", "On Christ and Antichrist", "c. 200–210", "Treatise", "accepted", "grc")
    if "cyprian" in t:
        return ("Cyprian of Carthage", "Treatises", "c. 250", "Treatise", "accepted", "lat")
    if "origen" in t or "celsum" in t or "celsus" in t:
        return ("Origen", "Against Celsus", "c. 248", "Treatise", "accepted", "grc")
    if "tertullian" in t:
        return ("Tertullian", "Treatise", "c. 200", "Treatise", "accepted", "lat")
    return None


def locus_of(title: str, work: str, path: str) -> str:
    m = re.search(r"Book\s+([IVXLC\d]+).*?Chapter\s+(\d+|[IVXLC]+)", title, re.I)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = re.search(r"0103(\d)(\d{2})", path)
    if m:
        return f"{m.group(1)}.{int(m.group(2))}"
    m = re.search(r"0701(\d)", path)
    if m:
        book = m.group(1)
        ch = re.search(r"Chapter\s+(\d+|[IVXLC]+)", title, re.I)
        return f"{book}.{ch.group(1)}" if ch else f"Book {book}"
    m = re.search(r"0416(\d)", path)
    if m:
        book = m.group(1)
        ch = re.search(r"Chapter\s+(\d+|[IVXLC]+)", title, re.I)
        return f"{book}.{ch.group(1)}" if ch else f"Book {book}"
    m = re.search(r"0623(\d+)", path)
    if m:
        return f"Discourse {int(m.group(1))}"
    m = re.search(r"0507(\d{2})", path)
    if m:
        return CYPRIAN_TITLES.get(f"0507{m.group(1)}", f"Treatise {int(m.group(1))}")
    m = re.search(r"Chapter\s+([IVXLC]+|\d+)", title, re.I)
    if m:
        return m.group(1)
    m = re.search(r"Commandment\s+(\d+)|Mandate\s+(\d+)|Similitude\s+(\d+)", title, re.I)
    if m:
        n = next(g for g in m.groups() if g)
        if "Similitude" in title:
            return f"Sim. {n}"
        return f"Mand. {n}"
    m = re.search(r"^([IVXLC0-9]+)\.\s+", title)
    if m:
        return m.group(1)
    return re.sub(r"\s+", " ", title)[:56]


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
    # Drop New Advent / CCEL chrome that sometimes survives strip.
    text = re.sub(
        r"(?is)^.*?(?:Against Heresies \(Book[^\)]*\)|Book [IVXLC]+, Chapter \d+\.?)\s*",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"(?is)Home\s*>.*?Chapter\s+\d+\.?\s*",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"(?is)CHURCH FATHERS:.*?(?=Chapter|\d+\.\s|[A-Z][a-z]{3,})",
        "",
        text,
        count=1,
    )
    text = re.sub(r"(?is)Ante-Nicene Fathers, Vol\.[^:]+:\s*", "", text)
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
        if re.search(r"Home\s*>|Fathers of the Church\s*>|Submit Search|CHURCH FATHERS:", b):
            continue
        if len(b) > max_chars:
            b = b[:max_chars].rsplit(" ", 1)[0] + "…"
        if len(b) > 100:
            out.append(b)
        if len(out) >= limit:
            break
    return out


def source_url(path: str) -> str:
    m = re.search(r"anf_cache/(0\d+|2501\d*)\.html$", path)
    if m:
        return f"https://www.newadvent.org/fathers/{m.group(1)}.htm"
    if "tertullian_resurrection" in path:
        return "https://www.tertullian.org/anf/anf03/anf03-41.htm"
    if "ccel_" in path:
        return "https://www.ccel.org/ccel/schaff/" + Path(path).name.replace("ccel_", "") + ".html"
    # local ANF HTML
    return path


def topic_notes(topic: str, ch: dict) -> list[str]:
    notes = []
    author = ch["author"]
    work = ch["work"]
    if topic == "millennium-debate":
        if any(x in author for x in ("Irenaeus", "Justin", "Commodian", "Lactantius", "Victorinus", "Barnabas", "Hippolytus")):
            notes.append(
                "Chiliastic / millenarian trajectory — mark as millennium-debate development, not later consensus."
            )
        if "Origen" in author or "Clement" in author:
            notes.append(
                "Often read as non-chiliast / spiritualizing stream over against Justin–Irenaeus chiliasm; label carefully."
            )
        if "Barnabas" in author:
            notes.append("Barnabas 15: six-thousand-year / eighth-day scheme — related to chiliast chronology, not identical to Rev 20 systems.")
    if topic == "heaven-hell-intermediate":
        notes.append("Interim / Hades–paradise language — seed only; do not dump later medieval systems.")
    if "Justin Martyr (attrib.)" in author and "Resurrection" in work:
        notes.append("Authenticity contested for On the Resurrection (Ps.-Justin often); keep contested flag.")
    if ch.get("authenticity") == "contested":
        notes.append("Authenticity contested — review before Professional lock.")
    if "Methodius" in author and "ANF misc" in work:
        notes.append("ANF misc Dionysius/Methodius resurrection page — attribution contested.")
    if topic == "apologetic-method":
        notes.append("Method passage (how they argue: reason / antiquity / prophecy / miracles), not only content.")
    if topic == "civil-authority" and "Tertullian" in author:
        notes.append("Civil-authority debate under pagan rule; Tertullian often sharp on military/idolatry boundaries.")
    if "Eusebius" in author:
        notes.append("SECONDARY WITNESS: Eusebius HE — historical report, not ante-Nicene dogmatic voice.")
    return notes


def main():
    chapters = []
    files_read = []
    paths = list((ROOT / "sources").glob("*.html")) + list(CACHE.glob("*.html"))
    # Prefer tertullian resurrection from cache; skip tiny stubs
    for path in sorted(set(paths)):
        if path.stat().st_size < 2000:
            continue
        # skip soft-404 leftovers and pure indices under ~8k with no chapters
        raw = path.read_text(errors="replace")
        if re.search(r"404 Not Found|page you requested could not", raw):
            continue
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
        base = f"{a}_{w}_{l}_{topic[:14]}"
        id_counts[base] += 1
        if id_counts[base] > 1:
            base = f"{base}_{id_counts[base]}"
        return base

    def add(topic, ch, sc, extra_notes=None):
        # Skip wrong-topic bleed from FORCE typo protection
        if topic not in TOPIC_RULES:
            return False
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
        notes = topic_notes(topic, ch)
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
            if title_re != r"." and not re.search(title_re, ch["title"] + " " + ch["body"][:120], re.I):
                continue
            for topic in topics:
                if topic not in TOPIC_RULES:
                    continue
                sc = score(topic, ch["body"])
                # Priority loci may be short; floor only if some topical signal exists.
                if sc < 2 and not re.search(
                    "|".join(TOPIC_RULES[topic]["need_any"]), ch["body"], re.I
                ):
                    continue
                sc = max(sc, 6)
                if counts[topic] >= SOFT[topic] + 12:
                    continue
                add(topic, ch, sc, extra_notes=["Forced priority locus for topic fill."])

    by_topic = defaultdict(list)
    for ch in chapters:
        for topic in TOPIC_RULES:
            sc = score(topic, ch["body"])
            if sc >= MIN[topic]:
                # Require a strong-pattern hit for noisy topics.
                strong = TOPIC_RULES[topic]["need_strong"]
                if not any(re.search(p, ch["body"], re.I) for p in strong):
                    continue
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
        "Justin Dialogue 80–81 + On the Resurrection (contested) from New Advent cache — not in local sources/ originally.",
        "Athenagoras On the Resurrection of the Dead fetched to anf_cache/0206.html.",
        "Irenaeus AH V.30–36 chiliastic chapters from New Advent cache; local English was only free-will/selected chapters + V.28.",
        "Lactantius Divine Institutes Books II–VII from New Advent cache; local HTML was Book I only (full Latin XML already in sources/latin/).",
        "Tertullian On the Resurrection of the Flesh from tertullian.org ANF (New Advent 0316 soft-404); Apology, De Corona, To Scapula, Ad Martyras, marriage treatises cached.",
        "Origen Contra Celsum Books II–VIII from New Advent; local English was Book I-centric (full Greek XML present).",
        "Methodius Banquet Discourses 1–11 cached; Discourse on the Resurrection English remains the contested ANF misc page (dionysius_alexandria.html).",
        "seed_edition Greek/Latin line-locks not attached in this pass (edition_id null) — next upgrade wave.",
        "millennium-debate: harvest includes chiliasts (Justin Dial 80–81, Irenaeus V.32–36, Barnabas 15, Commodian, Lactantius VII, Victorinus, Hippolytus Antichrist) and non-chiliast / spiritualizing notes where Origen/Clement scored — label development in notes.",
        "Cyprian On Works and Alms + Exhortation to Martyrdom from cache; local cyprian_treatises.html stub unused.",
    ]

    coverage_notes = {
        "resurrection-body": (
            "Strong: Justin 1 Apol 18–19/52, Athenagoras On Resurrection + Plea 36, Tatian 6, Theophilus 1.13, "
            "Minucius 34, Tertullian De Res. Carnis, Irenaeus V.6/31–32, Methodius resurrection misc, Lactantius VII.23, Origen Cels."
        ),
        "judgment-second-coming": (
            "Strong: Justin judgment chapters, Didache 16, Barnabas 21, Minucius 35, Lactantius VII.19–20/26, "
            "Hippolytus On Christ and Antichrist, Origen Cels VII–VIII, Irenaeus V.30."
        ),
        "millennium-debate": (
            "Both streams: chiliasts Justin Dial 80–81, Irenaeus V.28/32–36, Barnabas 15, Commodian, Lactantius VII, "
            "Victorinus, Hippolytus Antichrist; non-chiliast / spiritualizing notes for Origen/Clement hits. Mark debate."
        ),
        "heaven-hell-intermediate": (
            "Seed density: Tertullian De Anima Hades chapters, Irenaeus V.31/35–36, Minucius, Methodius resurrection misc, "
            "Lactantius VII.21, Justin interim language. Avoid later system dump."
        ),
        "love-neighbor-enemy": (
            "Didache 1–2, Barnabas 19, Diognetus 5, Athenagoras Plea 33, Tertullian Apology 39, Clement Paedagogus, Lactantius VI."
        ),
        "sexual-marriage": (
            "Strong: Justin/Athenagoras continence, Didache 2–3, Hermas Mand 4, Clement Paedagogus, Methodius Banquet, "
            "Tertullian Ad Uxorem / Exhortation to Chastity / Monogamy / Veiling, Cyprian Dress of Virgins."
        ),
        "wealth-alms": (
            "Didache 4, Hermas Sim 1–2, Barnabas 19, Cyprian On Works and Alms, Tertullian Apology 39, Clement Paedagogus, Lactantius VI."
        ),
        "martyrdom-witness": (
            "Tertullian Ad Martyras / Scorpiace / Apology 50, Passion of Perpetua, Cyprian Exhortation to Martyrdom / Mortality, "
            "Minucius 37, Ignatius Smyrnaeans."
        ),
        "civil-authority": (
            "Debate: Theophilus 1.11 honor the king, Diognetus 5–6, Tertullian De Corona / Idolatry / To Scapula / Apology 42, "
            "Origen Cels VIII, Cyprian Demetrianus, Lactantius V."
        ),
        "apologetic-method": (
            "Method loci: Justin prophecy proofs, Athenagoras reason, Tatian antiquity, Minucius, Lactantius Inst I.5–6 & V, "
            "Origen Cels preface/method chapters, Tertullian Apology, Arnobius, Cyprian Demetrianus."
        ),
        "general_gaps": gaps,
        "summary": (
            f"Deep seed harvest for eschatology+ethics: {len(excerpts)} excerpts across {len(counts)} topics "
            f"from {len(set(files_read))} files read ({len(files_used)} used). confidence=seed_anf; not Professional GTG."
        ),
    }

    payload = {
        "locus": "eschatology+ethics",
        "mined_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_note": "Candidates only. confidence is seed_anf|seed_edition. Do not claim source_verified or Professional GTG.",
        "counts_per_topic": dict(counts),
        "total_excerpts": len(excerpts),
        "files_opened": sorted(set(files_read)),
        "files_used": sorted(files_used),
        "coverage_notes": coverage_notes,
        "gaps": gaps,
        "excerpts": excerpts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("Wrote", OUT)
    print("counts", dict(counts))
    print("total", len(excerpts), "unique_ids", len({e["id"] for e in excerpts}))
    junk = sum(1 for e in excerpts if re.search(r"Submit Search|CHURCH FATHERS:", " ".join(e["english"])))
    print("junk", junk)
    for t in order:
        ex = [e for e in excerpts if e["topic"] == t]
        print(t, counts[t], "sample:", ex[0]["citation"] if ex else "-")


if __name__ == "__main__":
    main()
