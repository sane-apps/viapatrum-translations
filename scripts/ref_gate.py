#!/usr/bin/env python3
"""Reference gate: every Bible reference in new English is judged before a work is certified (Nov 8, 2026).

Why: a sweep of the 404 published works found 25.5% of printed Bible references wrong (400-reference random sample,
careful judges; outputs/../references-20261108). The Greek-numbered Psalm, the reference on the wrong clause, and the
wrong verse ("called Elijah by the Lord (Luke 1:17)", Larry Sanger's report) all passed the section checkers. The
September Jev sweep caught 7 of 36 at its bar. A strong model given the verse text caught 23 of 24 with no false alarms.

What it does, per work at work_pipeline.apply() time:
1. Finds every reference in parentheses in the passing sections' English.
2. Deterministic: a chapter or verse that does not exist in the English (KJV) Bible is always sent to the judge.
3. Judge: Claude Opus through plan_calls (plan budget and usage limits respected), with the KJV text of the cited
   verse and its neighbours, and for Psalms the English text at the Greek numbering. Same brief as the sweep
   (docs/REFERENCE_JUDGE_BRIEF.md).
4. Fixes the English, citation-only: a wrong, near or Greek-numbered reference with a confident correction is
   replaced; a confidently wrong one with no correction is removed. Anything else stays.
5. If the judge cannot run (plan paused, call failed, malformed answer) the work is NOT certified this time; the
   lane tries again later. The gate never passes silently.
The receipt then hashes the fixed English and records the gate's counts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import citation_amendments as CA  # noqa: E402

MODEL = "claude-opus-5-5"
FIX_CONF = 0.8
BATCH = 80
BRIEF = ROOT / "docs" / "REFERENCE_JUDGE_BRIEF.md"
KJV = json.loads((ROOT / "data" / "en_kjv.json").read_text(encoding="utf-8"))

NAMES = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel",
         "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
         "Psalm", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel",
         "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
         "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
         "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
         "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
         "1 John", "2 John", "3 John", "Jude", "Revelation"]
assert len(NAMES) == len(KJV) == 66
ALIASES = {"psalms": "Psalm", "ps": "Psalm", "pss": "Psalm", "song": "Song of Solomon", "song of songs": "Song of Solomon",
           "canticles": "Song of Solomon", "apocalypse": "Revelation", "rev": "Revelation", "gen": "Genesis",
           "exod": "Exodus", "ex": "Exodus", "lev": "Leviticus", "num": "Numbers", "deut": "Deuteronomy",
           "josh": "Joshua", "judg": "Judges", "neh": "Nehemiah", "esth": "Esther", "prov": "Proverbs",
           "eccl": "Ecclesiastes", "qoheleth": "Ecclesiastes", "isa": "Isaiah", "jer": "Jeremiah", "lam": "Lamentations",
           "ezek": "Ezekiel", "dan": "Daniel", "hos": "Hosea", "obad": "Obadiah", "mic": "Micah", "nah": "Nahum",
           "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai", "zech": "Zechariah", "mal": "Malachi",
           "matt": "Matthew", "mt": "Matthew", "mk": "Mark", "lk": "Luke", "jn": "John", "rom": "Romans",
           "gal": "Galatians", "eph": "Ephesians", "phil": "Philippians", "col": "Colossians", "tit": "Titus",
           "phlm": "Philemon", "heb": "Hebrews", "jas": "James"}
NUMBERED = {"sam": "Samuel", "samuel": "Samuel", "kgs": "Kings", "kings": "Kings", "chr": "Chronicles",
            "chronicles": "Chronicles", "cor": "Corinthians", "corinthians": "Corinthians", "thess": "Thessalonians",
            "thessalonians": "Thessalonians", "tim": "Timothy", "timothy": "Timothy", "pet": "Peter", "peter": "Peter",
            "john": "John", "jn": "John"}
INDEX = {n.lower(): i for i, n in enumerate(NAMES)}

_REF = re.compile(rf"(?P<book>{CA._BOOKS})\.?\s+(?P<ch>\d+)(?::(?P<v>\d+)(?:\s*[-–]\s*(?P<ve>\d+))?)?")


def canon(book: str) -> str | None:
    b = re.sub(r"\s+", " ", book.strip().rstrip(".")).lower()
    b = re.sub(r"^(i|first)\s", "1 ", re.sub(r"^(ii|second)\s", "2 ", re.sub(r"^iii\s", "3 ", b)))
    m = re.match(r"^([123])\s?(\w+)$", b)
    if m and m.group(2) in NUMBERED:
        b = f"{m.group(1)} {NUMBERED[m.group(2)].lower()}"
    name = ALIASES.get(b) or (NAMES[INDEX[b]] if b in INDEX else None)
    return name


def refs_in(paras: list[str]):
    """(para index, start, end, printed, book, ch, v, ve) for references inside reference-only parentheses."""
    out = []
    for pi, para in enumerate(paras):
        for pm in CA.REF_PAREN.finditer(para):
            inner_start = para.index("(", pm.start())
            inner = para[inner_start:pm.end()]
            for m in _REF.finditer(inner):
                book = canon(m.group("book"))
                if not book:
                    continue
                s = inner_start + m.start()
                ch, v = int(m.group("ch")), int(m.group("v")) if m.group("v") else None
                ve = int(m.group("ve")) if m.group("ve") else None
                if book in SINGLE_CHAPTER and v is None:  # "Jude 6" is verse 6 of the one chapter
                    ch, v = 1, ch
                rest = inner[m.end():m.end() + 8]
                labelled = bool(re.match(r"\s*(?:\(\s*)?(?:LXX|Greek|Vulg)", rest)) or inner[max(0, m.start() - 6):m.start()].rstrip().endswith("LXX")
                out.append((pi, s, inner_start + m.end(), m.group(0), book, ch, v, ve) + ((True,) if labelled else ()))
    return out


SINGLE_CHAPTER = {"Obadiah", "Philemon", "2 John", "3 John", "Jude"}


def labelled_greek(ref: tuple) -> bool:
    """True when refs_in found the reference marked LXX/Greek/Vulgate (its numbering is not the English one)."""
    return len(ref) > 8 and ref[8]


def exists(book: str, ch: int, v: int | None) -> bool:
    chs = KJV[INDEX[book.lower()]]["chapters"]
    return 1 <= ch <= len(chs) and (v is None or 1 <= v <= len(chs[ch - 1]))


def kjv(book: str, ch: int, lo: int, hi: int) -> list[str]:
    chs = KJV[INDEX[book.lower()]]["chapters"]
    if not 1 <= ch <= len(chs):
        return []
    vs = chs[ch - 1]
    return [f"{book} {ch}:{v} {vs[v - 1]}" for v in range(max(1, lo), min(len(vs), hi) + 1)]


def lxx_to_english(ch: int) -> list[int]:
    if ch <= 8 or ch >= 148:
        return [ch]
    if ch == 9:
        return [9, 10]
    if ch == 113:
        return [114, 115]
    if ch in (114, 115):
        return [116]
    if ch in (146, 147):
        return [147]
    return [ch + 1]


def items_for(sections: dict[str, list[str]]):
    """Judge items and an index back to (section, ref tuple)."""
    items, where = [], {}
    for sid, paras in sections.items():
        for r in refs_in(paras):
            pi, s, e, printed, book, ch, v, ve = r[:8]
            para = paras[pi]
            iid = f"G{len(items):05d}"
            item = {"id": iid, "printed": printed, "parsed_as": f"{book} {ch}" + (f":{v}" if v else "") + (f"-{ve}" if ve else ""),
                    "context": para[max(0, s - 700):e + 300],
                    "kjv_cited_and_neighbours": kjv(book, ch, (v or 1) - 2, (ve or v or 3) + 2),
                    "exists_in_english_numbering": exists(book, ch, v)}
            if labelled_greek(r):
                item["labelled_greek_numbering"] = True
            if book == "Psalm" and v:
                alt = [x for c2 in lxx_to_english(ch) if c2 != ch for x in kjv("Psalm", c2, v - 3, (ve or v) + 1)]
                if alt:
                    item["kjv_if_greek_numbering"] = alt
            items.append(item)
            where[iid] = (sid, r)
    return items, where


def judge(items: list[dict], chat=None) -> dict[str, dict] | None:
    """{id: verdict} for every item, or None when the judge could not run for all of them."""
    if chat is None:
        import plan_calls
        chat = plan_calls.chat
    brief = BRIEF.read_text(encoding="utf-8")
    out = {}
    for i in range(0, len(items), BATCH):
        part = items[i:i + BATCH]
        user = (f"Judge all {len(part)} items below. Output ONLY the JSON lines, one per item, in input order.\n\nITEMS:\n"
                + json.dumps(part, ensure_ascii=False))
        res = chat(MODEL, [{"role": "system", "content": brief}, {"role": "user", "content": user}])
        if "error" in res:
            return None
        got = {}
        for line in str(res.get("content", "")).splitlines():
            line = line.strip().strip("`")
            if line.startswith("{"):
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("verdict") in ("correct", "greek_numbering", "near", "wrong", "unclear"):
                    got[d.get("id")] = d
        if any(x["id"] not in got for x in part):
            return None
        out.update(got)
    return out


def decide(v: dict) -> tuple[str, str | None]:
    """('keep'|'replace'|'remove', new display)."""
    conf = float(v.get("confidence") or 0)
    if v["verdict"] in ("correct", "unclear") or conf < FIX_CONF:
        return "keep", None
    ref = (v.get("correct_ref") or "").strip()
    m = _REF.fullmatch(ref) if ref else None
    if m and canon(m.group("book")):
        book = canon(m.group("book"))
        tail = ref[m.end("book"):].lstrip(". ")
        return "replace", f"{book} {tail}"
    if v["verdict"] == "wrong" and not ref:
        return "remove", None
    return "keep", None


def fix_sections(sections: dict[str, list[str]], verdicts: dict[str, dict], where: dict) -> tuple[dict, dict]:
    """New English per section (citation-only) and counts."""
    plan: dict[str, list] = {}
    counts = {"references": len(where), "replaced": 0, "removed": 0, "kept_flagged": 0}
    for iid, (sid, r) in where.items():
        action, new = decide(verdicts[iid])
        if action == "keep":
            if verdicts[iid]["verdict"] not in ("correct",):
                counts["kept_flagged"] += 1
            continue
        plan.setdefault(sid, []).append((r, action, new))
    out = {}
    for sid, paras in sections.items():
        new_paras = list(paras)
        for (pi, s, e, printed, *_), action, new in sorted(plan.get(sid, []), key=lambda x: (x[0][0], -x[0][1])):
            p = new_paras[pi]
            if action == "replace":
                p = p[:s] + new + p[e:]
            else:
                p = p[:s] + p[e:]
                p = re.sub(r"\(\s*[;,]\s*", "(", p)
                p = re.sub(r"\s*[;,]\s*\)", ")", p)
                p = re.sub(r"\s*\(\s*\)", "", p)
            new_paras[pi] = p
        if new_paras != paras and CA.citation_only(paras, new_paras):
            for _r, action, _n in plan.get(sid, []):
                counts["replaced" if action == "replace" else "removed"] += 1
            out[sid] = new_paras
        else:
            out[sid] = paras
    return out, counts


def gate(sections: dict[str, list[str]], chat=None) -> tuple[dict | None, dict]:
    """Fixed sections and report, or (None, report) when the judge could not run."""
    items, where = items_for(sections)
    if not items:
        return dict(sections), {"references": 0}
    verdicts = judge(items, chat=chat)
    if verdicts is None:
        return None, {"references": len(items), "error": "reference judge did not answer for every reference"}
    fixed, counts = fix_sections(sections, verdicts, where)
    return fixed, counts
