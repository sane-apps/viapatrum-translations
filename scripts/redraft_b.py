#!/usr/bin/env python3
"""Constrained Pass B redraft: rebuild reading English from certified Pass A.

Recovery path when revise fails structurally (hallucinated or abridged
Pass B). Pass A is the anchor: split it into numbered clauses (lossless,
mechanically verified), draft one numbered Pass B sentence per clause,
verify mechanically, strip numbers. Writes nothing unless every
mechanical check passes. Never promotes; the normal promote flow follows.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_promote import parse_claim_row, sections_from_slice  # noqa: E402
from book_adapter import JEREMIAH_SLUG, get_adapter  # noqa: E402
from draft_claim import (  # noqa: E402
    DRAFT_DEFAULT,
    justification_data,
    upsert_cyril_english,
    upsert_english,
    write_justification,
)
from llm_bakeoff import DEFAULT_ACCOUNT, is_nvidia_model, normalize_model, vendor_call  # noqa: E402
from pipeline_autonomy import parse_or_repair  # noqa: E402

REF_RE = re.compile(r"(\d+):(\d+(?:\s*[-\u2013]\s*\d+)?)")
WORD_RE = re.compile(r"[A-Za-z]+|\d+")
KNOWN_BOOKS = frozenset(
    "genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|"
    "1 samuel|2 samuel|1 kings|2 kings|1 chronicles|2 chronicles|ezra|nehemiah|esther|job|"
    "psalm|psalms|proverbs|ecclesiastes|song of solomon|isaiah|jeremiah|lamentations|ezekiel|daniel|"
    "hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|"
    "matthew|mark|luke|john|acts|romans|1 corinthians|2 corinthians|galatians|ephesians|"
    "philippians|colossians|1 thessalonians|2 thessalonians|1 timothy|2 timothy|titus|philemon|"
    "hebrews|james|1 peter|2 peter|1 john|2 john|3 john|jude|revelation|"
    "tobit|judith|wisdom|sirach|baruch|1 maccabees|2 maccabees".split("|"))
GREEK_RE = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")
BRACKET_TAG_RE = re.compile(r"\[[a-z]\d+\]")
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(.*\S)\s*$")


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def verify_lossless_split(clauses: list[str], source: str) -> bool:
    if not clauses or not all(isinstance(c, str) and c.strip() for c in clauses):
        return False
    return norm_space(" ".join(clauses)) == norm_space(source)


def verify_numbered_sequence(lines: list[str], n: int) -> tuple[bool, list[str]]:
    if len(lines) != n:
        return False, []
    stripped: list[str] = []
    for i, line in enumerate(lines, start=1):
        m = NUMBERED_RE.match(line.strip())
        if not m or int(m.group(1)) != i or not m.group(2).strip():
            return False, []
        stripped.append(m.group(2).strip())
    return True, stripped


def _norm_book(book: str) -> str:
    return norm_space(book).lower()


def _book_before(text: str, pos: int) -> str:
    """Walk left from a ch:v ref to find the book name.

    Takes capitalized words (plus 'of' and a leading 1/2/3); a lone
    lowercase word counts only when it is a known book ((john 3:5)).
    Returns "" when no book shape is present (meet 3:30).
    """
    toks = WORD_RE.findall(text[:pos])[-4:]
    if not toks:
        return ""
    words: list[str] = []
    for tok in reversed(toks):
        if tok.isdigit():
            if len(tok) == 1 and words and len(words) < 3:
                words.append(tok)
            break
        if tok[0].isupper():
            if len(words) >= 3:
                break
            words.append(tok)
            continue
        if tok.lower() == "of" and words:
            words.append(tok)
            continue
        break
    if words:
        return norm_space(" ".join(reversed(words)))
    lone = toks[-1]
    if lone[0].islower() and _norm_book(lone) in KNOWN_BOOKS:
        return lone
    return ""


def _parse_verses(verses: str) -> tuple[int, int]:
    nums = [int(x) for x in re.split(r"\s*[-\u2013]\s*", verses)]
    return (nums[0], nums[-1]) if len(nums) > 1 else (nums[0], nums[0])


def parse_citation(text: str) -> tuple[str, int, int, int] | None:
    cites = extract_citations(text)
    return cites[0] if cites else None


def extract_citations(text: str) -> list[tuple[str, int, int, int]]:
    out: list[tuple[str, int, int, int]] = []
    for m in REF_RE.finditer(text):
        book = _book_before(text, m.start())
        if not book:
            continue
        lo, hi = _parse_verses(m.group(2))
        out.append((_norm_book(book), int(m.group(1)), lo, hi))
    return out


def citation_allowed(cite: tuple[str, int, int, int],
                     allow: list[tuple[str, int, int, int]]) -> bool:
    book, ch, lo, hi = cite
    for abook, ach, alo, ahi in allow:
        if abook == book and ach == ch and alo <= lo and hi <= ahi:
            return True
    return False


def check_citations(paras: list[str], allow: list[tuple[str, int, int, int]]) -> list[str]:
    bad: list[str] = []
    for p in paras:
        for m in REF_RE.finditer(p):
            book = _book_before(p, m.start())
            if not book:
                continue
            lo, hi = _parse_verses(m.group(2))
            cite = (_norm_book(book), int(m.group(1)), lo, hi)
            if not citation_allowed(cite, allow):
                bad.append(f"{book} {m.group(1)}:{m.group(2)}")
    return bad


def has_greek(text: str) -> bool:
    return bool(GREEK_RE.search(text))


def has_bracket_tags(text: str) -> bool:
    return bool(BRACKET_TAG_RE.search(text))


def length_ratio_ok(draft: str, anchor: str, lo: float = 0.4, hi: float = 3.0) -> bool:
    if not anchor.strip():
        return False
    ratio = len(draft) / len(anchor)
    return lo <= ratio <= hi


SPLIT_SYS = (
    "Split the gloss into clauses. Return ONLY JSON {\"clauses\": [\"...\", ...]}. "
    "Do not alter, translate, reorder, or drop ANY characters apart from "
    "splitting: joining your clauses with single spaces must reproduce the "
    "gloss EXACTLY. Split on sentence and clause boundaries; keep every word."
)

DRAFT_SYS = (
    "You write reading English from a numbered gloss. Return ONLY JSON "
    "{\"sentences\": [\"1. ...\", \"2. ...\", ...]}. Rules: exactly one numbered "
    "sentence per gloss clause, same order, numbers 1..N with no gaps; every "
    "sentence a full sentence of natural literary prose in the author's voice; "
    "same claims as the gloss, different sentences. Never add claims, events, "
    "names, or quotes the gloss lacks. Never drop a clause. Never paste Greek "
    "words. Never emit bracketed tags like [n1]. Cite Scripture ONLY with the "
    "ALLOWED references below, beside the clause they belong to; never invent "
    "or adjust verse numbers."
)

SPLIT_SHAPE = '{"clauses": ["gloss clause 1", "..."]}'
DRAFT_SHAPE = '{"sentences": ["1. reading sentence", "..."]}'


def build_allowlist(pass_a: str, justification: dict) -> list[tuple[str, int, int, int]]:
    allow = extract_citations(pass_a)
    for ref in justification.get("bible_refs") or []:
        allow.extend(extract_citations(str(ref)))
    for note in justification.get("translator_notes") or []:
        allow.extend(extract_citations(str(note)))
    notes = justification.get("notes")
    if isinstance(notes, str):
        allow.extend(extract_citations(notes))
    return allow


def assemble_paragraphs(sentences: list[str], width: int = 600) -> list[str]:
    paras: list[str] = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) + 1 > width and cur:
            paras.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        paras.append(cur)
    return paras


def redraft_section(section: str, agent: str, model: str, cf_token: str,
                    nv_token: str, account: str, chain: list[str],
                    attempts: int, book: str) -> dict:
    adapter = get_adapter(book)
    jeremiah = book == JEREMIAH_SLUG
    try:
        fix = adapter.load_source_row(section)
    except (KeyError, SystemExit) as exc:
        return {"ok": False, "section": section, "error": "unknown_section",
                "detail": str(exc)[:200]}
    if jeremiah:
        from draft_claim import ENG, JUST_DIR
        rows = json.loads(ENG.read_text(encoding="utf-8"))
        matches = [r for r in rows if str(r.get("section")) == section]
        just_path = JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json"
    else:
        eng_path = adapter.english_path_for_section(section)
        rows = json.loads(eng_path.read_text(encoding="utf-8"))
        matches = [r for r in rows if str(r.get("section")) == section]
        just_path = adapter.justification_path(section)
    if not matches or not just_path.is_file():
        return {"ok": False, "section": section, "error": "missing_prior_draft"}
    row = matches[0]
    prior = json.loads(just_path.read_text(encoding="utf-8"))
    pass_a = str(prior.get("pass_a_gloss") or "")
    if not pass_a.strip() or not prior.get("lemmas"):
        return {"ok": False, "section": section,
                "error": "missing_evidence_for_redraft",
                "detail": "prior justification lacks pass_a_gloss/lemmas anchor"}
    allow = build_allowlist(pass_a, prior)

    def _call(call_model, call_messages, call_tokens):
        return vendor_call(call_model, call_messages, cf_token=cf_token,
                           nv_token=nv_token, account=account,
                           max_tokens=call_tokens)

    info: dict = {"ms": 0, "pt": 0, "ct": 0, "neurons": 0}
    clauses: list[str] = []
    used_model = chain[0]
    for attempt in range(2):
        used_model = chain[attempt % len(chain)]
        obj, meta = parse_or_repair(
            _call, used_model,
            [{"role": "system", "content": SPLIT_SYS},
             {"role": "user", "content": f"Section {section}. Gloss:\n{pass_a}"}],
            need=["clauses"], shape_desc=SPLIT_SHAPE, max_tokens=3000)
        for key in ("ms", "pt", "ct", "neurons"):
            info[key] += meta.get(key) or 0
        if obj and verify_lossless_split(obj.get("clauses") or [], pass_a):
            clauses = [c.strip() for c in obj["clauses"]]
            break
    if not clauses:
        return {"ok": False, "section": section, "error": "split_not_lossless",
                "ms": info["ms"]}
    n = len(clauses)
    numbered = "\n".join(f"{i}. {c}" for i, c in enumerate(clauses, 1))
    allowed_txt = "; ".join(sorted({f"{b} {c}:{l}" + (f"-{h}" if h != l else "")
                                    for b, c, l, h in allow})) or "(none: cite nothing)"
    sentences: list[str] = []
    violations: list[str] = []
    for attempt in range(max(1, attempts)):
        used_model = chain[attempt % len(chain)]
        feedback = ("\nPrevious attempt violated: " + "; ".join(violations)
                    if violations else "")
        obj, meta = parse_or_repair(
            _call, used_model,
            [{"role": "system", "content": DRAFT_SYS},
             {"role": "user", "content":
              f"Section {section}. Numbered gloss clauses:\n{numbered}\n\n"
              f"ALLOWED Scripture references (cite nothing else): {allowed_txt}\n"
              f"Lemmas: {json.dumps(prior.get('lemmas'), ensure_ascii=False)[:1500]}"
              f"{feedback}"}],
            need=["sentences"], shape_desc=DRAFT_SHAPE, max_tokens=4000)
        for key in ("ms", "pt", "ct", "neurons"):
            info[key] += meta.get(key) or 0
        if not obj or not isinstance(obj.get("sentences"), list):
            violations = ["unparseable sentences list"]
            continue
        raw_lines = [str(x) for x in obj["sentences"]]
        ok_seq, stripped = verify_numbered_sequence(raw_lines, n)
        if not ok_seq:
            violations = [f"need exactly sentences 1..{n} in order, got {len(raw_lines)} lines"]
            continue
        joined = " ".join(stripped)
        violations = []
        if not length_ratio_ok(joined, pass_a):
            violations.append(f"length {len(joined)} vs gloss {len(pass_a)} out of 0.4x-3x band")
        if has_greek(joined):
            violations.append("Greek characters in reading English")
        if has_bracket_tags(joined):
            violations.append("bracketed tags in reading English")
        bad = check_citations(stripped, allow)
        if bad:
            violations.append("unlisted citations: " + ", ".join(sorted(set(bad))))
        if not violations:
            sentences = stripped
            break
    if not sentences:
        return {"ok": False, "section": section, "error": "redraft_constraints_fail",
                "detail": "; ".join(violations)[:500], "ms": info["ms"],
                "clauses": n}
    english = assemble_paragraphs(sentences)
    notes = [str(x) for x in row.get("translator_notes") or []]
    notes.append(f"Pass B mechanically redrafted from {n} gloss clauses (redraft_b, no checker input).")
    obj_out = {
        "section": section,
        "title": str(row.get("title") or "").strip(),
        "pass_a_gloss": pass_a,
        "english": english,
        "lemmas": prior["lemmas"],
        "choices": prior.get("choices"),
        "translator_notes": notes,
    }
    prior_edition = prior.get("edition") or {}
    witnesses = [{"path": prior_edition.get("path") or "",
                  "sha256": prior_edition.get("sha256") or ""}] + [
        {"path": c.get("path"), "sha256": c.get("sha256")}
        for c in prior_edition.get("checks") or []]
    try:
        evidence = justification_data(section, obj_out, agent, used_model, fix,
                                      adapter=adapter if not jeremiah else None,
                                      witnesses=witnesses)
    except ValueError as exc:
        return {"ok": False, "section": section, "error": "missing_draft_evidence",
                "detail": str(exc)[:200]}
    for key in ("edition", "source_text", "source_normalizations", "anf_compare",
                "apparatus", "bible_refs", "variants"):
        if key in prior:
            evidence[key] = prior[key]
    prior_drafter = str(prior.get("draft_model") or "")
    evidence["draft_model"] = prior_drafter + f"+redraft:{used_model}" if prior_drafter else used_model
    evidence["revisions"] = list(prior.get("revisions") or []) + [{
        "model": used_model, "agent": agent,
        "at": datetime.now(timezone.utc).isoformat(),
        "from_receipt": "redraft_b:constrained", "notes_addressed": 0,
        "clauses": n,
    }]
    evidence["reviewer"] = f"pending-ai-crosscheck:{used_model}"
    write_justification(section, evidence, just_path)
    if jeremiah:
        upsert_english(section, obj_out["title"], english, notes, fix.get("homily"))
    else:
        upsert_cyril_english(section, obj_out["title"], english, notes, adapter)
    return {"ok": True, "section": section, "title": obj_out["title"],
            "clauses": n, "ms": info["ms"], "pt": info["pt"], "ct": info["ct"],
            "neurons": info.get("neurons", 0), "model": used_model,
            "justification": str(just_path)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Constrained Pass B redraft from Pass A.")
    ap.add_argument("--claim", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--model", default=DRAFT_DEFAULT)
    ap.add_argument("--section", action="append", default=[])
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--draft-fallbacks",
                    default="@cf/openai/gpt-oss-20b,@cf/meta/llama-3.3-70b-instruct-fp8-fast")
    args = ap.parse_args()
    model = normalize_model(args.model)
    chain = [model] + [normalize_model(x) for x in (args.draft_fallbacks or "").split(",")
                       if x.strip() and normalize_model(x) != model]
    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv_token = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    if is_nvidia_model(model):
        if not nv_token:
            raise SystemExit("Need NV_API_KEY for NVIDIA models")
    elif not cf_token:
        raise SystemExit("Need CF_TOKEN / CLOUDFLARE_API_TOKEN")
    row = parse_claim_row(args.claim)
    book = row.get("Book slug") or JEREMIAH_SLUG
    claimed = sections_from_slice(row.get("Slice (sections)") or "", book)
    if args.section and not set(args.section) <= set(claimed):
        raise SystemExit("Requested sections are outside the claim; refusing writes")
    sections = args.section or claimed
    from fathers_run_lock import install_wall_deadline  # noqa: WPS433
    install_wall_deadline(5400, label=f"redraft_b:{args.claim}", exit_code=4)
    results = [redraft_section(s, args.agent, model, cf_token, nv_token,
                               account, chain, args.attempts, book)
               for s in sections]
    print(json.dumps({"claim": args.claim, "sections": results}, indent=1,
                     ensure_ascii=False), flush=True)
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
