#!/usr/bin/env python3
"""Citation-only amendments to certified English (Nov 8, 2026).

Why: a reference sweep found wrong Bible references in published works (Larry Sanger's report: "(Luke 1:17)" for
Matthew 11:14; Psalms printed in Greek numbering). Fixing them changes the English, and a work_pipeline receipt
pins each section's English by SHA-256, so the build would withhold the whole work. Re-certifying 200 works for a
reference change is waste; silently rewriting receipt hashes would skip the gate.

So a reference fix is recorded in reviews/citation_amendments.jsonl, one row per change:
  {"section", "before_sha256", "after_sha256", "before": [paras], "after": [paras], "tool", "at", "why"}
certified() accepts a section whose English no longer matches its receipt only when a chain of rows leads from the
receipt's hash to the current English and EVERY row is proved citation-only: the before and after texts are identical
once Bible references inside parentheses are removed. Any other change in a row voids the chain, so the work goes
back to the normal re-check.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

FILE = "citation_amendments.jsonl"

_BOOKS = (
    r"Genesis|Gen|Exodus|Exod|Ex|Leviticus|Lev|Numbers|Num|Deuteronomy|Deut|Joshua|Josh|Judges|Judg|Ruth|"
    r"(?:1|2|I|II|First|Second) ?(?:Samuel|Sam|Kings|Kgs|Chronicles|Chr|Esdras|Maccabees|Macc)|Ezra|Nehemiah|Neh|"
    r"Tobit|Tob|Judith|Jdt|Esther|Esth|Job|Psalms?|Pss?|Proverbs|Prov|Ecclesiastes|Eccl|Qoheleth|"
    r"Song of (?:Songs|Solomon)|Song|Canticles|Wisdom(?: of Solomon)?|Wis|Sirach|Sir|Ecclesiasticus|Baruch|Bar|"
    r"Isaiah|Isa|Jeremiah|Jer|Lamentations|Lam|Ezekiel|Ezek|Daniel|Dan|Hosea|Hos|Joel|Amos|Obadiah|Obad|Jonah|"
    r"Micah|Mic|Nahum|Nah|Habakkuk|Hab|Zephaniah|Zeph|Haggai|Hag|Zechariah|Zech|Malachi|Mal|"
    r"Matthew|Matt|Mt|Mark|Mk|Luke|Lk|John|Jn|Acts|Romans|Rom|(?:1|2|I|II) ?(?:Corinthians|Cor|Thessalonians|Thess|"
    r"Timothy|Tim|Peter|Pet)|Galatians|Gal|Ephesians|Eph|Philippians|Phil|Colossians|Col|Titus|Tit|Philemon|Phlm|"
    r"Hebrews|Heb|James|Jas|(?:1|2|3|I|II|III) ?(?:John|Jn)|Jude|Revelation|Rev|Apocalypse"
)
_LOC = r"\d+(?::\d+[a-c]?(?:\s*[-–]\s*\d+(?::\d+)?[a-c]?)?(?:\s*,\s*\d+[a-c]?(?:\s*[-–]\s*\d+[a-c]?)?)*)?"
_ONE = rf"(?:(?:cf\.|see|compare|LXX|Greek|Vulgate)\s+)?(?:{_BOOKS})\.?\s+{_LOC}(?:\s+(?:LXX|Greek|Vulgate))?"
# A parenthesis that holds nothing but Bible references (one or more, ; or , separated).
REF_PAREN = re.compile(rf"\s*\(\s*{_ONE}(?:\s*[;,]\s*(?:{_ONE}|{_LOC}))*\s*\)")


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def strip_refs(paras: list[str]) -> str:
    """The English with every reference-only parenthesis removed, whitespace normalised."""
    text = "\n".join(paras)
    text = REF_PAREN.sub("", text)
    return re.sub(r"[ \t]+", " ", re.sub(r" +([,.;:!?])", r"\1", text)).strip()


def citation_only(before: list[str], after: list[str]) -> bool:
    return strip_refs(before) == strip_refs(after)


def load(book_dir: Path) -> list[dict]:
    path = book_dir / "reviews" / FILE
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def chain_ok(rows: list[dict], section: str, receipt_sha: str, current_sha: str) -> bool:
    """True when proved citation-only rows lead from the receipt's English hash to the current one."""
    if receipt_sha == current_sha:
        return True
    h = receipt_sha
    for r in rows:
        if str(r.get("section")) != str(section) or r.get("before_sha256") != h:
            continue
        before, after = r.get("before") or [], r.get("after") or []
        if sha("\n".join(before)) != h or sha("\n".join(after)) != r.get("after_sha256"):
            return False
        if not citation_only(before, after):
            return False
        h = r["after_sha256"]
        if h == current_sha:
            return True
    return False


def record(book_dir: Path, section: str, before: list[str], after: list[str], *, tool: str, why: str) -> dict:
    """Append a proved citation-only row. Raises ValueError if the change is not citation-only."""
    if not citation_only(before, after):
        raise ValueError(f"{book_dir.name} §{section}: change is not citation-only")
    row = {"section": str(section), "before_sha256": sha("\n".join(before)), "after_sha256": sha("\n".join(after)),
           "before": before, "after": after, "tool": tool, "why": why, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    path = book_dir / "reviews" / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
