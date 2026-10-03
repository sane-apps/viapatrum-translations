"""Deterministic whole-work linter for the patristic translation corpus.

No LLM, no network. Every existing check is per-section; this one reads a
whole work in order and reports defects a reader sees across sections.

Contract (imported by other code):
    load_work(slug) -> [{"id", "title", "text"}]
    lint_work(sections, brief=None) -> [{"rule", "severity", "section", "quote", "why"}]
Every quote is an exact substring of that section's text.

`brief` (optional): {"glossary": [{"source_term", "english", "banned": [...]}],
                     "names": {"first of Kingdoms": "1 Samuel"},
                     "language": "Latin"}   # language is an optional extra

CLI:
    python3 -m pipeline.work_lint --slug eustathius-engastrimytho
    python3 -m pipeline.work_lint --all --out outputs/work-lint/corpus-20261002.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:  # run as `python3 -m pipeline.work_lint` or as a script from pipeline/
    from pipeline import check_pass_ab as cpa
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from pipeline import check_pass_ab as cpa

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books"

# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def _as_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(p) for p in value if p is not None)
    return ""


def _sections_from(data, stem: str) -> list[dict]:
    out: list[dict] = []
    if isinstance(data, dict):
        if isinstance(data.get("sections"), list):
            return _sections_from(data["sections"], stem)
        if "english" in data or "text" in data:
            data = [data]
        else:
            return out
    if not isinstance(data, list):
        return out
    # a bare list of paragraph strings is one section
    if data and all(isinstance(x, str) for x in data):
        return [{"id": stem, "title": "", "text": "\n".join(data)}]
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            continue
        text = _as_text(row.get("english", row.get("text")))
        sid = row.get("section") or row.get("id") or (stem if len(data) == 1 else f"{stem}#{i + 1}")
        out.append({"id": str(sid), "title": str(row.get("title") or ""), "text": text})
    return out


def load_work(slug: str) -> list[dict]:
    """Ordered [{"id","title","text"}] from books/<slug>/translations/*_english.json."""
    folder = BOOKS / slug / "translations"
    sections: list[dict] = []
    for path in sorted(folder.glob("*_english.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        stem = path.name[: -len("_english.json")]
        sections.extend(_sections_from(data, stem))
    return sections


def _book_language(slug: str) -> str:
    try:
        for line in (BOOKS / slug / "book.yml").read_text(encoding="utf-8").splitlines():
            if line.startswith("language:"):
                return line.split(":", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return ""


# --------------------------------------------------------------------------
# Rule helpers
# --------------------------------------------------------------------------

Finding = dict


def _f(rule, severity, sec, quote, why) -> Finding:
    return {"rule": rule, "severity": severity, "section": sec["id"], "quote": quote, "why": why}


def _snip(text: str, start: int, end: int, pad: int = 0) -> str:
    return text[max(0, start - pad): min(len(text), end + pad)]


# ---- boundary -------------------------------------------------------------

_TERMINAL = set('.!?”’"\')]…')


def _is_stub(text: str) -> bool:
    """Scaffold stubs are reported by `scaffold`; do not pile boundary/script noise on them."""
    return bool(cpa.PLACEHOLDER.search(text) or cpa.CONTAMINATION.search(text))


def rule_boundary(sec, brief):
    text = sec["text"].strip()
    if not text or _is_stub(text):
        return []
    out = []
    first = text[0]
    if first.isalpha() and first.islower():
        m = re.match(r"\S+(?:\s+\S+){0,3}", text)
        out.append(_f("boundary", "error", sec, m.group(0),
                      "section starts with a lowercase letter (cut mid-sentence)"))
    last = text[-1]
    if last not in _TERMINAL:
        tail = text[-40:]
        out.append(_f("boundary", "error", sec, tail.lstrip() or text[-1:],
                      "section ends without terminal punctuation"))
    return out


# ---- bracket_filler ---------------------------------------------------------

_BRACKET = re.compile(r"\[([A-Za-z][A-Za-z'’-]*(?:\s+[A-Za-z][A-Za-z'’-]*){0,2})\]")
_BRACKET_OK = {"sic", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def rule_bracket_filler(sec, brief):
    out = []
    for m in _BRACKET.finditer(sec["text"]):
        if m.group(1).lower() in _BRACKET_OK:
            continue
        out.append(_f("bracket_filler", "warn", sec, m.group(0),
                      "editorial filler in square brackets in the reading text"))
    return out


# ---- citation_style -----------------------------------------------------------

_ABBR = (
    "Matt|Mt|Mk|Lk|Jn|Rom|Cor|Gal|Eph|Phil|Col|Thess|Tim|Heb|Jas|Pet|Rev|"
    "Gen|Exod|Ex|Lev|Num|Deut|Dt|Josh|Judg|Sam|Kgs|Chr|Neh|Ps|Pss|Prov|Eccl|Isa|Jer|"
    "Ezek|Dan|Hos|Obad|Mic|Nah|Hab|Zeph|Hag|Zech|Mal"
)
_CITE_ABBR = re.compile(
    r"[(\[]\s*(?:[123]\s?)?(?:" + _ABBR + r")\b\.?(?=\s*(?:\d|[)\]]|$|[;,]))(?:\s*\d[\d:.,\u2013-]*\d|\s*\d)?"
)
_CITE_OLD = re.compile(r"\b(?:Canticles|Apocalypse)\b")


def rule_citation_style(sec, brief):
    out = []
    text = sec["text"]
    for m in _CITE_ABBR.finditer(text):
        out.append(_f("citation_style", "error", sec, m.group(0).rstrip(),
                      "abbreviated book name in a reference; house style uses full names"))
    for m in re.finditer(
        r"\b(?:first|second|third|fourth|1st|2nd|3rd|4th)\s+(?:book\s+|volume\s+)?of\s+(?:the\s+)?kingdoms\b",
        text, re.I,
    ):
        out.append(_f("citation_style", "error", sec, m.group(0),
                      "Septuagint title 'Kingdoms'; use 1-2 Samuel / 1-2 Kings"))
    for m in _CITE_OLD.finditer(text):
        out.append(_f("citation_style", "warn", sec, m.group(0),
                      "old title; modern readers expect Song of Songs / Revelation"))
    return out


# ---- ancient_names -----------------------------------------------------------

# pattern -> modern name(s). The finding is dropped if the section also names
# the modern book/person (a gloss such as "Osee (Hosea)").
_ANCIENT = [
    (r"\b(?:book|books|volume)\s+of\s+(?:the\s+)?Kingdoms\b", "Samuel|Kings"),
    (r"\bParalipomen(?:on|a)\b", "Chronicles"),
    (r"\bJesus(?:,?\s+the)?\s+(?:son\s+of|of)\s+Nav[eé]\b|\bJesus\s+Nav[eé]\b|\bJesus\s+son\s+of\s+Nun\b", "Joshua"),
    (r"\bEsaias\b", "Isaiah"),
    (r"\bOsee\b", "Hosea"),
    (r"\bSophonias\b", "Zephaniah"),
    (r"\bAgg?aeus\b|\bAggeus\b", "Haggai"),
    (r"\bAbdias\b", "Obadiah"),
    (r"\bMicheas\b", "Micah"),
    (r"\bMalachias\b", "Malachi"),
    (r"\bEzechiel\b", "Ezekiel"),
    (r"\bEsdras\b", "Ezra"),
    (r"\bEliseus\b", "Elisha"),
]
_ANCIENT_RX = [(re.compile(p), mod) for p, mod in _ANCIENT]


def rule_ancient_names(sec, brief):
    out = []
    text = sec["text"]
    for rx, modern in _ANCIENT_RX:
        for m in rx.finditer(text):
            if re.search(r"\b(?:" + modern + r")\b", text):
                continue
            out.append(_f("ancient_names", "error", sec, m.group(0),
                          f"old name; a modern reader needs '{modern.replace('|', ' / ')}'"))
    return out


# ---- stray_script -----------------------------------------------------------

_SCRIPT = re.compile(
    r"[Ͱ-Ͽἀ-῿֐-׿Ⲁ-⳿܀-ݏ]+"
    r"(?:[\s,.;··'’-]+[Ͱ-Ͽἀ-῿֐-׿Ⲁ-⳿܀-ݏ]+)*"
)
_GLOSS_AFTER = re.compile(r"^[\s\"”’')\],;]{0,3}\(?\s*[A-Za-z]{2,}|^[\s\"”’')\]]*(?:,|—|-)?\s*"
                          r"(?:that is|i\.e\.|meaning|means|literally|or)\b", re.I)
_GLOSS_BEFORE = re.compile(r"(?:means?|meaning|word|term|called|literally|Greek|Hebrew|Syriac|Coptic|Latin|"
                           r"as|is|the)\W*$", re.I)


def rule_stray_script(sec, brief):
    out = []
    text = sec["text"]
    if _is_stub(text):
        return out
    for m in _SCRIPT.finditer(text):
        run = m.group(0).strip()
        # single letters (phi-shaped, sigla) and Greek numerals (alpha-prime) are not stray prose
        if len(re.sub(r"[^\w]", "", run)) < 2 or re.search(r"[\u02b9\u0374\u0384\u0375]", run):
            continue
        after = text[m.end(): m.end() + 40]
        before = text[max(0, m.start() - 40): m.start()]
        # gloss: an English gloss in parentheses/quotes right after, or a naming phrase right before
        if re.match(r"^\s*[,\u2014:]?\s*[(“\"‘']", after) and re.search(r"[A-Za-z]{3,}", after[:35]):
            continue
        if re.search(r"[(“\"‘']\s*$", before) and re.search(r"[A-Za-z]{3,}", before[:-1]):
            if re.search(r"[A-Za-z]{3,}", after[:30]):
                continue
        if re.match(r"^\s*[,—-]?\s*(?:that is|i\.e\.|meaning|means|literally)\b", after, re.I):
            continue
        if re.search(r"(?:means?|meaning|called|literally|word|term)\W{0,3}$", before, re.I):
            continue
        out.append(_f("stray_script", "warn", sec, m.group(0).strip(),
                      "Greek/Hebrew/Coptic/Syriac letters with no English gloss nearby"))
    return out


# ---- term_drift (work level) -------------------------------------------------

_HYPH = re.compile(r"\b([A-Za-z]{3,})-([A-Za-z]{3,})\b")
# Prefixes that form ordinary English compounds; never a coinage family.
_DRIFT_STOP = set("""
self well ill half all non pre pro anti post semi quasi over under out up down off
ever one two three four five six seven eight nine ten twelve hundred thousand first second third
many much more most least less very high low long short good bad old new great little big
ex vice co sub super ultra mid inter intra trans counter cross
father mother brother sister son daughter god lord christ holy heavenly
so by day night life soul body heart mind world earth sea sun moon star fire water
man men woman fellow free full open dead living only same other each every any no
light dark true false right left wise early late double single
twenty thirty forty fifty sixty seventy eighty ninety eleven thirteen fourteen fifteen sixteen seventeen eighteen nineteen
fourth fifth sixth seventh eighth ninth tenth not alone already once own best human
""".split())
# Stems that make a frequent, legitimate English family ("-minded", "-hearted", "-born").
_DRIFT_SUFFIX_STOP = set("minded hearted born like fold bearing giving making loving seeking".split())


def rule_term_drift(sections, brief):
    fam: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for sec in sections:
        for m in _HYPH.finditer(sec["text"]):
            head, tail = m.group(1), m.group(2)
            if head.lower() in _DRIFT_STOP:
                continue
            fam[head.lower()][m.group(0).lower()].append((sec, m.group(0)))
    out = []
    for head, variants in sorted(fam.items()):
        if len(variants) < 2:
            continue
        tails = {v.split("-", 1)[1] for v in variants}
        if tails <= _DRIFT_SUFFIX_STOP:
            continue
        # distinct renderings, not just plural/singular of one
        if len({t[:-1] if t.endswith("s") else t for t in tails}) < 3:
            continue
        # the defect we target: one person/agent term rendered several ways (belly-dancer, belly-talker...)
        agents = {t.rstrip("s") for t in tails if re.search(r"(?:er|ers|or|ors|ist|ists)$", t)}
        if len(agents) < 2:
            continue
        hits = [h for occ in variants.values() for h in occ]
        if len({h[0]["id"] for h in hits}) < 3:
            continue
        names = ", ".join(sorted(f"{v} x{len(o)}" for v, o in variants.items()))
        first_sec, first_quote = min(hits, key=lambda h: [s["id"] for s in sections].index(h[0]["id"]))
        out.append((len({t.rstrip("s") for t in tails}), _f(
            "term_drift", "warn", first_sec, first_quote,
            f"'{head}-' coinage rendered {len(variants)} ways across the work: {names}")))
    # A work full of compounds is style, not drift: report only the three widest families.
    out.sort(key=lambda p: -p[0])
    return [f for _, f in out[:3]]


# ---- glossary / names (brief-driven) ---------------------------------------

def rule_glossary(sec, brief):
    out = []
    text = sec["text"]
    # Owner rule 2026-10-03: cite the book as "Wisdom of Solomon", never bare "Wisdom".
    for m in re.finditer(r"\bWisdom(?! of Solomon)(?=\s+\d+[:.]\d+)", text):
        out.append(_f("glossary", "error", sec, m.group(0) + text[m.end():m.end() + 8],
                      "write the book as 'Wisdom of Solomon'"))
    if not brief:
        return out
    text = sec["text"]
    for entry in brief.get("glossary") or []:
        for bad in entry.get("banned") or []:
            if not bad:
                continue
            for m in re.finditer(r"(?<![\w-])" + re.escape(bad) + r"(?![\w-])", text, re.I):
                out.append(_f("glossary", "error", sec, m.group(0),
                              f"banned rendering of {entry.get('source_term', '?')}; use '{entry.get('english', '?')}'"))
    for old, modern in (brief.get("names") or {}).items():
        # Only a plain short name is a modern form; a note ("Christ (Christou)
        # appears once in section 9") is not something the text can say.
        if not modern or len(modern) > 40 or len(modern.split()) > 5 or re.search(r"[()\u2014\u2013:;]|\bappears\b", modern):
            continue
        # A short form of the modern name ("Wisdom" for Wisdom of Solomon) is the
        # library's own citation style (91 "Wisdom N:N" vs 1 long form, owner
        # 2026-10-03): only real renames (Sion -> Zion) are flagged, and only
        # capitalized, so "wisdom" the virtue is never taken for the book.
        if old.lower() in modern.lower():
            continue
        pat = r"(?<!\w)" + re.escape(old) + r"(?!\w)"
        for m in re.finditer(pat, text):
            if re.search(r"(?<!\w)" + re.escape(modern) + r"(?!\w)", text, re.I):
                continue
            out.append(_f("glossary", "error", sec, m.group(0),
                          f"use the modern name '{modern}'"))
    return out


# ---- scaffold / output guard -----------------------------------------------

def rule_scaffold(sec, brief):
    out = []
    text = sec["text"]
    for rx, what in ((cpa.PLACEHOLDER, "placeholder/scaffold text"), (cpa.CONTAMINATION, "process note leaked into text")):
        for m in rx.finditer(text):
            out.append(_f("scaffold", "error", sec, m.group(0), what))
    return out


def rule_output_guard(sec, brief):
    out = []
    text = sec["text"]
    paras = [p for p in text.split("\n") if p.strip()]
    for p in paras:
        for err in cpa.output_guard_errors(p):
            what = err.split(": ", 1)[1]
            quote = None
            for rx in (cpa._GLUED_STUTTER, cpa._WORD_RUN, cpa._DOUBLED):
                m = rx.search(p)
                if m and m.group(0)[:20] in err:
                    quote = m.group(0)
                    break
            if quote is None:
                quote = p[:60]
            out.append(_f("output_guard", "error", sec, quote, what))
    return out


# ---- archaic ------------------------------------------------------------------

_ARCHAIC = re.compile(r"\b(?:thee|thou|thy|thine|hath|hast|doth|saith|wherefore|unto|thereof|ye)\b", re.I)
_QUOTED = re.compile(r"[\"“][^\"“”]{0,600}[\"”]")


def rule_archaic(sec, brief):
    text = sec["text"]
    masked = _QUOTED.sub(lambda m: " " * len(m.group(0)), text)
    out = []
    for m in _ARCHAIC.finditer(masked):
        out.append(_f("archaic", "warn", sec, text[m.start():m.end()],
                      "archaic King James diction outside quotation marks"))
    return out


# ---- false_friend (Latin works only) ----------------------------------------
# Short, documented list. Each entry: pattern, Latin source, usual sense.
_FALSE_FRIENDS = [
    (r"\bconspir(?:acy|acies|ed|e|ing)\b", "conspiratio", "agreement/harmony, not plotting"),
    (r"\bdocuments\b", "documenta", "proofs/examples, not papers"),
    (r"\bpretend(?:s|ed|ing)?\b", "praetendere", "to put forward/allege, not to feign"),
]
_FF_RX = [(re.compile(p, re.I), src, sense) for p, src, sense in _FALSE_FRIENDS]


def rule_false_friend(sec, brief):
    if not brief or "latin" not in str(brief.get("language", "")).lower():
        return []
    out = []
    for rx, src, sense in _FF_RX:
        for m in rx.finditer(sec["text"]):
            out.append(_f("false_friend", "warn", sec, m.group(0),
                          f"Latin false friend: {src} usually means {sense}"))
    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

SECTION_RULES = (rule_boundary, rule_bracket_filler, rule_citation_style, rule_ancient_names,
                 rule_stray_script, rule_glossary, rule_scaffold, rule_output_guard,
                 rule_archaic, rule_false_friend)


def lint_work(sections: list[dict], brief: dict | None = None) -> list[dict]:
    findings: list[Finding] = []
    for sec in sections:
        sec = {"id": str(sec.get("id")), "title": sec.get("title", ""), "text": sec.get("text") or ""}
        for rule in SECTION_RULES:
            findings.extend(rule(sec, brief))
    clean = [{"id": str(s.get("id")), "title": s.get("title", ""), "text": s.get("text") or ""} for s in sections]
    findings.extend(rule_term_drift(clean, brief))
    seen, unique = set(), []
    by_id = {s["id"]: s["text"] for s in clean}
    for f in findings:
        key = (f["rule"], f["section"], f["quote"])
        if key in seen or not f["quote"] or f["quote"] not in by_id.get(f["section"], ""):
            continue
        seen.add(key)
        unique.append(f)
    return unique


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def lint_slug(slug: str, brief: dict | None = None) -> tuple[list[dict], list[dict]]:
    sections = load_work(slug)
    b = dict(brief or {})
    b.setdefault("language", _book_language(slug))
    brief_file = BOOKS / slug / "brief.json"
    if brief_file.exists():
        try:
            for k, v in json.loads(brief_file.read_text(encoding="utf-8")).items():
                b.setdefault(k, v)
        except ValueError:
            pass
    return sections, lint_work(sections, b)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--slug")
    ap.add_argument("--out")
    ap.add_argument("--sample", type=int, default=10, help="random findings per rule to save for hand-checking")
    args = ap.parse_args(argv)
    if not args.all and not args.slug:
        ap.error("pass --all or --slug")
    slugs = sorted(p.name for p in BOOKS.iterdir() if (p / "translations").is_dir()) if args.all else [args.slug]
    per_rule: Counter = Counter()
    per_rule_sev: Counter = Counter()
    works: dict[str, dict] = {}
    all_findings = []
    for slug in slugs:
        sections, found = lint_slug(slug)
        if not sections:
            continue
        words = sum(len(s["text"].split()) for s in sections)
        c = Counter(f["rule"] for f in found)
        err = sum(1 for f in found if f["severity"] == "error")
        works[slug] = {"sections": len(sections), "words": words, "errors": err,
                       "warns": len(found) - err, "by_rule": dict(c)}
        for f in found:
            per_rule[f["rule"]] += 1
            per_rule_sev[(f["rule"], f["severity"])] += 1
            all_findings.append({"slug": slug, **f})
    top = sorted(works.items(), key=lambda kv: (-kv[1]["errors"], -kv[1]["warns"]))[:30]
    rng = random.Random(20261002)
    samples = {}
    for rule in per_rule:
        pool = [f for f in all_findings if f["rule"] == rule]
        samples[rule] = rng.sample(pool, min(args.sample, len(pool)))
    report = {
        "works_linted": len(works),
        "findings_total": len(all_findings),
        "per_rule": {r: {"count": n, "severity": sorted({s for (rr, s) in per_rule_sev if rr == r})}
                     for r, n in per_rule.most_common()},
        "top_30_worst_works": [{"slug": s, **w} for s, w in top],
        "works": works,
    }
    if args.slug and not args.all:
        report["findings"] = all_findings
    print(f"works={len(works)} findings={len(all_findings)}")
    for r, n in per_rule.most_common():
        print(f"  {r:16s}{n}")
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
        out.with_name(out.stem + "-samples.json").write_text(
            json.dumps(samples, indent=1, ensure_ascii=False), encoding="utf-8")
        out.with_name(out.stem + "-findings.json").write_text(
            json.dumps(all_findings, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {out}")
    elif args.slug:
        for f in all_findings:
            print(f"{f['severity']:5s} {f['rule']:14s} {f['section']:18s} {f['quote'][:50]!r}  {f['why'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
