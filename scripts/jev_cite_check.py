#!/usr/bin/env python3
"""Shadow citation-correctness check via Jev Choice judgments (TypeSafe).

For each scripture citation in a section's Pass B, asks Jev whether the
cited verse is the true source of the quoted words. Advisory only: prints
verdicts + confidence, never promotes or holds. Needs TYPESAFE_API_KEY.

Usage: python3 scripts/jev_cite_check.py --book SLUG --section ID [--max N] [--json]
Exit 0 with a CITES line; --json prints the full verdict object.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_review import jev  # noqa: E402
import ai_promote as promote  # noqa: E402

AUTO_ACCEPT = 0.8

ID_DISPLAY = {
    "gen": "Genesis", "exod": "Exodus", "lev": "Leviticus", "num": "Numbers",
    "deut": "Deuteronomy", "josh": "Joshua", "judg": "Judges", "ruth": "Ruth",
    "1sam": "1 Samuel", "2sam": "2 Samuel", "1kgs": "1 Kings", "2kgs": "2 Kings",
    "1chr": "1 Chronicles", "2chr": "2 Chronicles", "ezra": "Ezra", "neh": "Nehemiah",
    "esth": "Esther", "job": "Job", "ps": "Psalms", "prov": "Proverbs",
    "eccl": "Ecclesiastes", "song": "Song of Solomon", "isa": "Isaiah",
    "jer": "Jeremiah", "lam": "Lamentations", "ezek": "Ezekiel", "dan": "Daniel",
    "hos": "Hosea", "joel": "Joel", "amos": "Amos", "obad": "Obadiah",
    "jonah": "Jonah", "mic": "Micah", "nah": "Nahum", "hab": "Habakkuk",
    "zeph": "Zephaniah", "hag": "Haggai", "zech": "Zechariah", "mal": "Malachi",
    "wis": "Wisdom", "sir": "Sirach", "bar": "Baruch", "tob": "Tobit",
    "jdt": "Judith", "1macc": "1 Maccabees", "2macc": "2 Maccabees",
    "matt": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John",
    "acts": "Acts", "rom": "Romans", "1cor": "1 Corinthians",
    "2cor": "2 Corinthians", "gal": "Galatians", "eph": "Ephesians",
    "phil": "Philippians", "col": "Colossians", "1thess": "1 Thessalonians",
    "2thess": "2 Thessalonians", "1tim": "1 Timothy", "2tim": "2 Timothy",
    "titus": "Titus", "phlm": "Philemon", "heb": "Hebrews", "jas": "James",
    "1pet": "1 Peter", "2pet": "2 Peter", "1jn": "1 John", "2jn": "2 John",
    "3jn": "3 John", "jude": "Jude", "rev": "Revelation",
}

CRITERIA = {
    "supports": "The cited verse is the true source of the quoted words.",
    "contradicts": "The quoted words come from a different verse; the citation is wrong.",
    "says_nothing": "Cannot tell from the Greek and English given.",
}

VERDICT = {"supports": "verified", "contradicts": "contradicted", "says_nothing": "unsupported"}


def display_ref(ref) -> str:
    book, chapter, verse = ref
    name = ID_DISPLAY.get(book, book)
    return f"{name} {chapter}:{verse}" if verse else f"{name} {chapter}"


_CITE_PAREN_RE = re.compile(r"\([^()]*?\d+\s*[:.]\s*\d+[^()]*?\)")
_BIBLE_MACRO_RE = re.compile(r">>\s*Bible:[^\]\n]*")


def sanitize_clause(clause: str) -> str:
    """Strip the filed answer from the clause so Jev judges words, not strings.

    Removes citation parens ("(John 3:5)", "(Isa 5:4)"), Bible macro tails
    (">> Bible:Exodus 15:1"), and [[ ]] markers. Without this, Jev could
    match the visible citation instead of knowing the verse — and negatives
    carrying the true cite in-clause would be trivially easy.
    """
    text = _BIBLE_MACRO_RE.sub(" ", clause)
    text = _CITE_PAREN_RE.sub(" ", text)
    text = text.replace("[[", " ").replace("]]", " ")
    return re.sub(r"\s+", " ", text).strip()


def cite_pairs(english_paras, max_n=12):
    """(clause, ref, display) for each citation found in Pass B sentences.

    Citations sit at clause end, so the sentence containing "(Jn 3:5)" is
    usually the tail fragment after the quote. When the text before the
    citation is short, prepend the previous sentence so Jev judges the
    quoted clause, not the following one.
    """
    pairs = []
    seen = set()
    for para in english_paras:
        prev = ""
        for sent in promote.split_sentences(para):
            for ref in promote.extract_refs(sent):
                key = (sent[:200], ref)
                if key in seen:
                    continue
                seen.add(key)
                clause = sent.strip()
                head = clause.split("(")[0]
                if len(head) < 80 and prev:
                    clause = (prev.strip() + " " + clause).strip()
                cf = "cf." in clause.lower()
                pairs.append((sanitize_clause(clause), ref, display_ref(ref), cf))
                if len(pairs) >= max_n:
                    return pairs
            prev = sent
    return pairs


def build_questions(pairs):
    questions = {}
    for i, (sent, _ref, display, _cf) in enumerate(pairs):
        questions[f"cite{i}"] = {
            "type": "choice",
            "instructions": (
                f"The English translation renders the clause: {sent[:500]!r} "
                f"and cites it as {display}. The locked Greek source is in state. "
                f"Is {display} the verse these words come from?"
            ),
            "criteria": CRITERIA,
        }
    return questions


def load_section_texts(book, section):
    """Direct (greek, english_paras) load, no adapter: works for every book.

    The cite check needs only source + English text, never justifications
    or bindings, so it reads the book JSON straight instead of going
    through the two-book adapter registry.
    """
    tdir = promote.ROOT / "books" / book / "translations"
    paras: list = []
    for ef in sorted(tdir.glob("*_english.json")):
        try:
            data = json.loads(ef.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        for row in rows:
            if isinstance(row, dict) and str(row.get("section")) == section:
                eng = row.get("english") or []
                paras = eng if isinstance(eng, list) else [eng]
                break
        if paras:
            break
    if not paras:
        raise SystemExit(f"Missing english for section {section} in {book}")
    greek = ""
    for sf in sorted(tdir.glob("*_source.json")):
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        for row in rows:
            if isinstance(row, dict) and str(row.get("section")) == section:
                greek = str(row.get("latin") or row.get("greek") or "")
                break
        if greek:
            break
    return greek, paras


def check_section(book, section, max_n=12):
    greek, paras = load_section_texts(book, section)
    pairs = cite_pairs(paras, max_n)
    if not pairs:
        return {"section": section, "cites": [], "note": "no citations in Pass B"}
    state = {
        "greek": greek[:4000],
        "english": "\n".join(paras)[:4000],
    }
    body = jev(state, build_questions(pairs))
    cites = []
    for i, (sent, _ref, display, cf) in enumerate(pairs):
        ans = body["answers"][f"cite{i}"]
        choice = ans["choice"]
        conf = ans.get("confidence", 0.0)
        cites.append({
            "display": display,
            "sentence": sent[:200],
            "choice": choice,
            "verdict": VERDICT.get(choice, "unsupported"),
            "confidence": round(conf, 3),
            "auto": conf >= AUTO_ACCEPT,
            "cf": cf,
        })
    return {"section": section, "model": body.get("model"),
            "usage": body.get("usage"), "cites": cites}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--section", required=True)
    ap.add_argument("--max", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = check_section(args.book, args.section, args.max)
    if args.json:
        print(json.dumps(result, indent=1))
    else:
        for cite in result.get("cites", []):
            print(f"{cite['verdict']:12s} conf={cite['confidence']:.2f} "
                  f"auto={cite['auto']!s:5s} {cite['display']}")
        use = result.get("usage") or {}
        print(f"CITES: {len(result.get('cites', []))} checked "
              f"(in={use.get('input_tokens', 0)} out={use.get('output_tokens', 0)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
