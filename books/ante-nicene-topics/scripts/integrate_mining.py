#!/usr/bin/env python3
"""Integrate outputs/mining/*_candidates.json into translations/topics/."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINING = ROOT / "outputs" / "mining"
TOPICS = ROOT / "translations" / "topics"
AUTHORS_PATH = ROOT / "authors.json"

AUTHOR_ALIASES = {
    "Mathetes": "Mathetes (Epistle to Diognetus)",
    "Methodius": "Methodius of Olympus",
    "Barnabas (Epistle)": "Barnabas",
    "Cyprian of Carthage": "Cyprian",
    "Dionysius/Methodius misc": "Methodius of Olympus",  # ANF misc page — contested
    "Eusebius of Caesarea": "Eusebius of Caesarea",
    "Clement of Rome": "Clement of Rome",
    "Firmilian of Caesarea": "Firmilian of Caesarea",
    "Justin Martyr (attrib.)": "Justin Martyr",
    "Passion of Perpetua and Felicity": "Passion of Perpetua and Felicity",
}

CANDIDATES = [
    ("theology_christology_candidates.json", "theology_christology.json", "theology-proper+christology"),
    ("bibliology_pneumatology_candidates.json", "bibliology_pneumatology.json", "bibliology+pneumatology"),
    ("ecclesiology_sacraments_candidates.json", "ecclesiology_sacraments.json", "ecclesiology+sacraments"),
    ("eschatology_ethics_candidates.json", "eschatology_ethics.json", "eschatology+ethics"),
]

FREE_WILL_RE = re.compile(r"\bfree will\b", re.I)


def infer_source_language(e: dict) -> str:
    if e.get("source_language"):
        return e["source_language"]
    if e.get("greek"):
        return "grc"
    if e.get("latin"):
        return "lat"
    # Heuristic from known Latin authors
    latinish = {
        "Tertullian",
        "Cyprian",
        "Minucius Felix",
        "Arnobius",
        "Lactantius",
        "Novatian",
        "Commodian",
        "Victorinus of Pettau",
        "Firmilian of Caesarea",  # letter preserved in Cyprian Latin corpus
        "Clement of Rome",  # Latin/Greek debate — keep grc default below if unknown
    }
    author = AUTHOR_ALIASES.get(e.get("author") or "", e.get("author") or "")
    if author in latinish:
        return "lat"
    return "grc"


def scrub_english(paras: list[str]) -> list[str]:
    out = []
    for p in paras:
        # Glossary: no bare "free will" system slogan in customer English.
        p2 = FREE_WILL_RE.sub("free choice", p)
        out.append(p2)
    return out


def normalize(e: dict) -> dict:
    e = dict(e)
    raw_author = e.get("author") or ""
    e["author"] = AUTHOR_ALIASES.get(raw_author, raw_author)
    e["source_language"] = infer_source_language(e)
    if isinstance(e.get("english"), list):
        e["english"] = scrub_english(e["english"])
    if e.get("id", "").startswith("dionysius_methodius"):
        e["authenticity"] = "contested"
        notes = list(e.get("notes") or [])
        notes.append("ANF misc Dionysius/Methodius page — attribution contested; review before lock.")
        e["notes"] = notes
    if raw_author == "Justin Martyr (attrib.)":
        e["authenticity"] = "contested"
        notes = list(e.get("notes") or [])
        if not any("contested" in str(n).lower() for n in notes):
            notes.append("Attribution contested; keep until edition audit.")
            e["notes"] = notes
    if e.get("author") == "Eusebius of Caesarea":
        notes = list(e.get("notes") or [])
        notes.append("Eusebius is post-ante-Nicene witness / historian — keep as secondary citation.")
        e["notes"] = notes
    for k in ("english", "translator_notes", "notes", "added_allusions"):
        if k not in e:
            e[k] = []
    return e


def ensure_authors(needed: set[str]) -> None:
    data = json.loads(AUTHORS_PATH.read_text())
    authors = data["authors"]
    extras = {
        "Clement of Rome": {
            "dates_display": "fl. c. 96",
            "sort_year": 96,
            "kind": "person",
            "note": "1 Clement traditionally late 1st century.",
        },
        "Firmilian of Caesarea": {
            "dates_display": "d. c. 269",
            "sort_year": 269,
            "kind": "person",
            "note": "Letter to Cyprian preserved in Cyprian corpus.",
        },
        "Eusebius of Caesarea": {
            "dates_display": "c. 260–c. 339",
            "sort_year": 325,
            "kind": "person",
            "note": "Post-ante-Nicene historian; used only as secondary witness when mining.",
        },
        "Passion of Perpetua and Felicity": {
            "dates_display": "c. 203",
            "sort_year": 203,
            "kind": "anonymous_work",
            "note": "Martyr act; traditional date under Septimius Severus.",
        },
    }
    changed = False
    for name in sorted(needed):
        if name not in authors and name in extras:
            authors[name] = extras[name]
            changed = True
        elif name not in authors:
            raise SystemExit(f"Author missing from authors.json and no extra stub: {name!r}")
    if changed:
        AUTHORS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("updated authors.json")


def main() -> int:
    all_excerpts: list[dict] = []
    for src_name, dest_name, locus in CANDIDATES:
        src = MINING / src_name
        if not src.exists():
            print("SKIP missing", src)
            continue
        raw = json.loads(src.read_text())
        excerpts = [normalize(e) for e in raw.get("excerpts") or []]
        dest = {
            "topic_file": dest_name,
            "locus": locus,
            "integrated_from": src_name,
            "integrated_at": date.today().isoformat(),
            "confidence_policy": "seed_anf|seed_edition only — not Professional GTG",
            "excerpts": excerpts,
        }
        out = TOPICS / dest_name
        out.write_text(json.dumps(dest, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {out.relative_to(ROOT)} ({len(excerpts)} excerpts)")
        all_excerpts.extend(excerpts)

    needed = {e["author"] for e in all_excerpts}
    ensure_authors(needed)

    # Cross-file id uniqueness vs MVP
    mvp = json.loads((TOPICS / "soteriology_free_will.json").read_text())
    mvp_ids = {e["id"] for e in mvp}
    ids = [e["id"] for e in all_excerpts]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids inside mining integrate")
    overlap = sorted(set(ids) & mvp_ids)
    if overlap:
        raise SystemExit(f"id overlap with MVP: {overlap[:10]}")

    by_topic = defaultdict(int)
    by_conf = defaultdict(int)
    for e in all_excerpts:
        by_topic[e["topic"]] += 1
        by_conf[e["confidence"]] += 1
    print("total integrated", len(all_excerpts))
    print("by_conf", dict(by_conf))
    print("topics", len(by_topic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
