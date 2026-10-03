#!/usr/bin/env python3
"""Jev-verified citation correction + backfill loop (TypeSafe + CF proposer).

For each flagged citation (filed-but-wrong or missing): a CF model proposes
the verse, Jev Choice verifies the proposal against clause + Greek, and the
Pass B text is edited only when Jev supports at high confidence. Every edit
is atomic with a JSONL receipt. Sections under active claims are skipped.

Usage:
  jev_cite_correct.py --flags PATH [--mode correct|backfill] [--min-conf F]
    [--books a,b] [--limit N] [--apply] [--out PATH]
Without --apply, prints what would change and writes no files.
Needs CF_TOKEN (proposer) + TYPESAFE_API_KEY (verifier).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jev_review import jev  # noqa: E402
import jev_cite_check as cite  # noqa: E402
import ai_promote as promote  # noqa: E402
import kjv_lookup  # noqa: E402
from llm_bakeoff import vendor_call  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROPOSER = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
VERIFY_CONF = 0.85
BACKFILL_CONF = 0.9
OVERLAP_MIN_SHARED = 2

_OVERLAP_STOP = frozenset(
    "a about after all also among an and are as at be because been before "
    "being both but by came come could did do doth down even every for from "
    "had hath have having he her here him his how into is it its made make "
    "many may more most much must nor not now off on one only or other out "
    "over said same say says shall she should so some such than that the "
    "their them then there these they this those through thus under unto up "
    "upon was were what when where which while who whom will with within "
    "without would ye you your".split())
_OVERLAP_KEEP = frozenset(
    "god lord jesus christ paul peter john james sin son men man law soul "
    "king lamb word way life love faith hope rock door vine bread".split())


def _overlap_tokens(text: str) -> set:
    toks = set()
    for word in re.findall(r"[a-z]+", text.lower()):
        if word in _OVERLAP_STOP:
            continue
        stem = word
        if stem.endswith("eth") and len(stem) > 5:
            stem = stem[:-3]
        elif stem.endswith("ed") and len(stem) > 5:
            stem = stem[:-2]
        elif stem.endswith("s") and len(stem) > 4:
            stem = stem[:-1]
        if len(stem) < 4 and stem not in _OVERLAP_KEEP:
            continue
        toks.add(stem)
    return toks


def verse_overlap(clause: str, verse_text: str) -> int:
    """Shared distinctive tokens between clause and verse text."""
    return len(_overlap_tokens(clause) & _overlap_tokens(verse_text))


def overlap_with_kjv(clause: str, proposed) -> int:
    return verse_overlap(clause, kjv_lookup.verse_window(*proposed))


SITE_BIBLES = Path.home() / "SaneApps/websites/fathers.saneapps.com/data/bibles"
SEARCH_VERSIONS = ("web", "bsb")
SEARCH_TOP = 3
_search_index = None


def _version_rows():
    """(ref, text) for KJV plus the site's WEB/BSB (modern wording matches
    the new English better than KJV alone)."""
    for book_id, chapters in kjv_lookup._load().items():
        for c, verses in enumerate(chapters, 1):
            for v, text in enumerate(verses, 1):
                yield (book_id, c, v), text
    import gzip
    for name in SEARCH_VERSIONS:
        path = SITE_BIBLES / f"{name}.json.gz"
        if not path.is_file():
            continue
        books = json.loads(gzip.open(path).read())["books"]
        if len(books) != 66:
            continue
        for book_id, chapters in zip(kjv_lookup.CANONICAL_IDS, books.values()):
            for c, verses in chapters.items():
                for v, text in verses:
                    yield (book_id, int(c), int(v)), text


def _load_search():
    global _search_index
    if _search_index is None:
        import math
        docs, postings, by_ref = [], {}, {}
        for ref, text in _version_rows():
            toks = _overlap_tokens(text)
            docs.append((ref, toks))
            by_ref.setdefault(ref, []).append(toks)
            for t in toks:
                postings.setdefault(t, []).append(len(docs) - 1)
        idf = {t: math.log(len(docs) / len(ids)) for t, ids in postings.items()}
        _search_index = (docs, postings, idf, by_ref)
    return _search_index


_QUOTE_RE = re.compile(r"[‘“'\"]([^‘’“”'\"]{12,})[’”'\"]")


def search_verses(clause: str, top: int = SEARCH_TOP):
    """Best-matching verse refs for the words quoted in clause (IDF overlap
    over KJV/WEB/BSB, max per ref). Needs 2+ shared distinctive words."""
    quoted = " ".join(_QUOTE_RE.findall(clause))
    query = _overlap_tokens(quoted if len(_overlap_tokens(quoted)) >= 3 else clause)
    if not query:
        return []
    docs, postings, idf, _by_ref = _load_search()
    hits, scores = {}, {}
    for t in query:
        for i in postings.get(t, ()):
            hits[i] = hits.get(i, 0.0) + idf[t]
    for i, sc in hits.items():
        ref, toks = docs[i]
        if len(query & toks) < OVERLAP_MIN_SHARED:
            continue
        if sc > scores.get(ref, 0.0):
            scores[ref] = sc
    return sorted(scores, key=lambda r: -scores[r])[:top]


TEXT_MATCH_CONF = 0.6
TEXT_MATCH_SHARED = 4


def clause_before(sentence: str, filed) -> str:
    """Words the filed citation points at: from the previous citation (or the
    sentence start) up to the filed one. Whole sentence when that is too thin."""
    spans = ref_spans(sentence)
    for i, (b, c, v, s, _e) in enumerate(spans):
        if not same_ref((b, c, v), filed):
            continue
        prev_end = max([e for _b, _c, _v, _s, e in spans if e <= s] or [0])
        seg = sentence[prev_end:s]
        if len(_overlap_tokens(seg)) >= 3:
            return seg
        break
    return sentence


def text_match_strength(clause: str, proposed) -> float:
    """Share of the clause's distinctive words found in the verse."""
    want = _overlap_tokens(" ".join(_QUOTE_RE.findall(clause)) or clause)
    if not want:
        return 0.0
    return overlap_any(clause, proposed) / len(want)


def overlap_any(clause: str, proposed) -> int:
    """Shared distinctive words with the verse in KJV, WEB or BSB."""
    want = _overlap_tokens(clause)
    _docs, _postings, _idf, by_ref = _load_search()
    best = overlap_with_kjv(clause, proposed)
    for toks in by_ref.get(tuple(proposed[:3]), ()):
        best = max(best, len(want & toks))
    return best


def section_claimed(section: str, active_text: str) -> bool:
    return bool(section) and bool(re.search(r"\b" + re.escape(section) + r"\b", active_text))


def parse_display(display: str):
    refs = promote.extract_refs(display)
    return refs[0] if refs else None


def ref_spans(sentence: str):
    """(book, chapter, verse, start, end) for each citation in text."""
    out = []
    for match in promote._REF_CH_VERSE_RE.finditer(sentence):
        book = promote._book_id(match.group(1) or "", match.group(2))
        if book:
            verse = int(re.split(r"\s*[-\u2013]\s*", match.group(4))[0])
            out.append((book, int(match.group(3)), verse, match.start(), match.end()))
    masked = promote._REF_CH_VERSE_RE.sub(lambda m: " " * len(m.group(0)), sentence)
    for match in promote._REF_CH_ONLY_RE.finditer(masked):
        book = promote._book_id(match.group(1) or "", match.group(2))
        if book:
            out.append((book, int(match.group(3)), None, match.start(), match.end()))
    return out


def span_covers(sentence: str, span, ref) -> bool:
    """True when span (book, ch, verse, s, e) is ref or a range holding it."""
    book, ch, verse, s, e = span
    if same_ref((book, ch, verse), ref):
        return True
    if book != ref[0] or ch != ref[1] or verse is None or ref[2] is None:
        return False
    tail = re.search(r"[-\u2013]\s*(\d+)\s*$", sentence[s:e])
    return bool(tail) and verse <= ref[2] <= int(tail.group(1))


def same_ref(a, b) -> bool:
    if a is None or b is None:
        return False
    if a[0] != b[0] or a[1] != b[1]:
        return False
    return a[2] is None or b[2] is None or a[2] == b[2]


def paren_extra_text(sentence: str, start: int, end: int) -> str:
    """Non-reference text in the paren group holding span (start, end).

    Returns "" for clean spans like "(John 3:5)" or "(Lev 19:5-8)".
    Non-empty for annotator glosses ("(X (LXX) or Y - ...)"), either/or
    notes ("(Mark 1:1 or John 1:34)"), or other compound groups whose
    extra text a bare span swap would orphan (live 2026-09-25)."""
    open_i, depth = -1, 0
    for i in range(start - 1, -1, -1):
        if sentence[i] == ")":
            depth += 1
        elif sentence[i] == "(":
            if depth == 0:
                open_i = i
                break
            depth -= 1
    if open_i < 0:
        return ""
    depth = 0
    close_i = -1
    for i in range(open_i, len(sentence)):
        if sentence[i] == "(":
            depth += 1
        elif sentence[i] == ")":
            depth -= 1
            if depth == 0:
                close_i = i
                break
    if close_i < end:
        return ""
    group = sentence[open_i:close_i + 1]
    # Strip verse-like tokens (not ref_spans ranges: those can swallow
    # a preceding "or "), then whatever non-punctuation remains is gloss.
    extra = re.sub(r"\d?\s?[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)? \d+(?::\d+)?",
                   " ", group)
    extra = re.sub(r";\s*cf\.?", " ", extra)  # handled cf. pattern
    extra = re.sub(r"[-\u2013]\d+", "", extra)  # verse-range tail
    extra = re.sub(r"[()\[\];\s]", "", extra)
    return extra


def replace_citation(sentence: str, filed, new_display: str) -> str | None:
    """Swap the filed citation span for the verified display; None if absent."""
    for book, ch, verse, start, end in ref_spans(sentence):
        if same_ref((book, ch, verse), filed):
            out = sentence[:start] + new_display + sentence[end:]
            # Filed cites sometimes split a possessive: "Aaron’ (X)s rod".
            out = re.sub(r"([’']) \(" + re.escape(new_display) + r"\)s\b",
                         r"\1s (" + new_display + ")", out)
            return out
    return None


def remove_citation(sentence: str, filed) -> str | None:
    """Delete the filed citation span (dedupe fix); None if absent."""
    for book, ch, verse, start, end in ref_spans(sentence):
        if same_ref((book, ch, verse), filed):
            out = sentence[:start] + sentence[end:]
            out = re.sub(r"\(\s*;\s*", "(", out)
            out = re.sub(r"\s*;\s*\)", ")", out)
            out = re.sub(r"\(\s*\)", "", out)
            out = re.sub(r"(['’”]) ([,.;])", r"\1\2", out)
            # Rejoin possessives the filed cite had split: "man’ s" -> "man’s".
            out = re.sub(r"([’'])\s+s(\s)", r"\1s\2", out)
            return re.sub(r" {2,}", " ", out).strip()
    return None


def append_citation(sentence: str, new_display: str) -> str:
    return sentence.rstrip() + f" ({new_display})"


def insert_citation_at_quote(sentence: str, quote: str, new_display: str) -> str:
    """Cite at the quote's close (splitters cut long quotes mid-clause).

    Falls back to sentence-end append when the quote tail is not found."""
    tail = (quote or "").strip()[-40:]
    if tail:
        i = sentence.rfind(tail)
        if i >= 0:
            pos = i + len(tail)
            if sentence[pos:pos + 1] in "\u2019'\"\u201d":
                pos += 1
            return sentence[:pos] + f" ({new_display})" + sentence[pos:]
    return append_citation(sentence, new_display)


def active_claim_text() -> str:
    path = ROOT / "docs/CLAIMS.md"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.search(r"\| (claimed|checking|review|drafting) \|", line):
            rows.append(line)
    return "\n".join(rows)


def propose_verse(clause: str, greek: str, cf_token: str) -> tuple | None:
    messages = [
        {"role": "system", "content": (
            "Identify the Bible verse. Reply with ONLY the reference, "
            "like 'Matthew 13:30' or 'Psalms 23:1'. No other words.")},
        {"role": "user", "content": (
            f"English clause: {clause[:600]}\nGreek context: {greek[:800]}\n"
            "Which Bible verse are these words from?")},
    ]
    try:
        resp = vendor_call(PROPOSER, messages, cf_token=cf_token, max_tokens=60)
    except Exception:
        return None
    text = resp.get("content") or resp.get("text") or ""
    refs = promote.extract_refs(text)
    return refs[0] if refs else None


SECOND_VERIFIER = "@cf/cloudflare/clef"
AGREE_CONF = 0.5   # both verifiers say "supports" at least this sure


def second_opinion(clause: str, greek: str, display: str):
    """Clef's verdict on the same question; ("error", 0.0) when unavailable."""
    import jev_review as jr
    keep = jr.CF_MODEL
    try:
        jr.CF_MODEL = SECOND_VERIFIER
        return verify_proposal(clause, greek, display)[:2]
    except Exception:  # noqa: BLE001 - second opinion is optional
        return ("error", 0.0)
    finally:
        jr.CF_MODEL = keep


def verify_proposal(clause: str, greek: str, display: str):
    state = {"greek": greek[:4000], "clause": clause[:600]}
    body = jev(state, {"v": {
        "type": "choice",
        "instructions": (
            f"The English clause is: {clause[:500]!r} Proposed citation: {display}. "
            f"Is {display} the verse these words come from?"),
        "criteria": cite.CRITERIA,
    }})
    ans = body["answers"]["v"]
    return ans["choice"], float(ans.get("confidence", 0.0)), body.get("usage") or {}


def english_candidates(book: str, section: str):
    """All (path, data, rows, idx) matching section: ids repeat across slices."""
    tdir = ROOT / "books" / book / "translations"
    out = []
    for ef in sorted(tdir.glob("*_english.json")):
        try:
            data = json.loads(ef.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        for i, row in enumerate(rows):
            if isinstance(row, dict) and str(row.get("section")) == section:
                out.append((ef, data, rows, i))
    return out


def greek_for_file(ef: Path, section: str) -> str:
    src = ef.with_name(ef.name.replace("_english.json", "_source.json"))
    if not src.is_file():
        return ""
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except Exception:
        return ""
    rows = data if isinstance(data, list) else data.get("sections", [])
    for row in rows:
        if isinstance(row, dict) and str(row.get("section")) == section:
            return str(row.get("latin") or row.get("greek") or "")
    return ""


def locate_target(paras_now, want: str, filed):
    """Best (score, sentence): filed-cite carriers by word overlap (correct
    mode), else 60-char overlap (backfill mode)."""
    best = None
    for para in paras_now:
        for sent in promote.split_sentences(para):
            if filed is not None:
                spans = [(b, c, v) for b, c, v, _s, _e in ref_spans(sent)]
                if not any(same_ref(s, filed) for s in spans):
                    continue
                clean = cite.sanitize_clause(sent)
                score = len(set(clean.split()) & set(want.split()))
            else:
                clean = cite.sanitize_clause(sent)
                if clean[:60] not in want and want[:60] not in clean:
                    continue
                score = len(set(clean.split()) & set(want.split()))
            if best is None or score > best[0]:
                best = (score, sent)
    return best


def justification_path(book: str, section: str):
    if book == "origen-jeremiah-samuel" and "." in section:
        h, s = section.split(".")
        cand = ROOT / f"books/{book}/reviews/justifications/jeremiah_{h}_{s}.json"
        return cand if cand.is_file() else None
    return None


def sync_justification(book: str, section: str, filed_display: str, new_display: str) -> bool:
    path = justification_path(book, section)
    if path is None:
        return False
    just = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for ref in just.get("bible_refs") or []:
        if not isinstance(ref, dict):
            continue
        if (ref.get("display") or "").strip().lower() == filed_display.strip().lower():
            ref["display"] = new_display
            changed = True
    if changed:
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(just, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.rename(path)
    return changed


def correct_item(item, cf_token: str, threshold: float):
    """Returns receipt dict; applied=False unless verified (apply flag gates writes)."""
    book, section = item["book"], item["section"]
    want = cite.sanitize_clause(item["sentence"])
    filed = parse_display(item.get("display", "")) if item.get("display") else None
    best = None  # (score, path, rows, idx, sentence, greek)
    for ef, _data, rows, idx in english_candidates(book, section):
        paras_now = rows[idx].get("english") or []
        hit = locate_target(paras_now, want, filed)
        if hit is None:
            continue
        score, target = hit
        if best is None or score > best[0]:
            greek = cite.load_section_texts(book, section)[0]
            best = (score, ef, rows, idx, target, greek)
    if best is None:
        if not english_candidates(book, section):
            return {"ok": False, "reason": "english-missing", **item}
        reason = "filed-cite-not-in-text" if filed is not None else "sentence-not-found"
        return {"ok": False, "reason": reason, **item}
    _score, ef, rows, idx, target, _greek_ignored = best
    greek = greek_for_file(ef, section)
    paras_now = rows[idx].get("english") or []
    flag_toks = _overlap_tokens(want)
    tgt_toks = _overlap_tokens(cite.sanitize_clause(target))
    shared_toks = flag_toks & tgt_toks
    ratio = len(shared_toks) / max(1, min(len(flag_toks), len(tgt_toks)))
    if len(shared_toks) < 3 or ratio < 0.4:
        return {"ok": False, "reason": "clause-mismatch", **item}
    focus = clause_before(target, filed) if filed is not None else target
    clean_target = cite.sanitize_clause(focus)
    candidates = [r for r in search_verses(focus)
                  if not (filed is not None and same_ref(r, filed))]
    guess = propose_verse(focus, greek, cf_token)
    if guess is not None and not (filed is not None and same_ref(guess, filed)) \
            and not any(same_ref(guess, r) for r in candidates):
        candidates.append(guess)
    if not candidates:
        reason = "proposer-agrees-with-filed" if guess is not None else "no-candidate"
        return {"ok": False, "reason": reason, **item}
    tried = []
    proposed = None
    basis = "verifier"
    top_hit = candidates[0] if candidates and candidates[0] != guess else None
    for cand in candidates:
        shared = overlap_any(clean_target, cand)
        cand_display = cite.display_ref(cand)
        if shared < OVERLAP_MIN_SHARED:
            tried.append(f"{cand_display}:overlap{shared}")
            continue
        try:
            choice, conf, _use = verify_proposal(clean_target, greek, cand_display)
        except Exception:  # noqa: BLE001 - verifier failure skips candidate
            tried.append(f"{cand_display}:error")
            continue
        tried.append(f"{cand_display}:{choice}@{conf:.2f}")
        if choice == "supports" and conf >= threshold:
            proposed, display = cand, cand_display
            break
        if choice == "supports" and conf >= AGREE_CONF:
            c2, conf2 = second_opinion(clean_target, greek, cand_display)
            tried.append(f"{cand_display}:clef {c2}@{conf2:.2f}")
            if c2 == "supports" and conf2 >= AGREE_CONF:
                proposed, display, basis = cand, cand_display, "jev+clef"
                break
        if (choice == "supports" and conf >= TEXT_MATCH_CONF and cand == top_hit
                and shared >= TEXT_MATCH_SHARED
                and text_match_strength(clean_target, cand) >= 0.5):
            proposed, display, basis = cand, cand_display, "verifier+text-match"
            break
    if proposed is None:
        low = all(":overlap" in t for t in tried)
        reason = "overlap-too-low:" + tried[0].split(":overlap")[-1] if low else "unverified"
        return {"ok": False, "reason": reason, "tried": tried, **item}
    if filed is not None:
        for _b, _c, _v, s, e in ref_spans(target):
            if same_ref((_b, _c, _v), filed) and paren_extra_text(target, s, e):
                return {"ok": False, "reason": "compound-span",
                        "proposed": display, **item}
        others = [s for s in ref_spans(target)
                  if not same_ref((s[0], s[1], s[2]), filed)]
        if any(span_covers(target, o, proposed) for o in others):
            new_sent = remove_citation(target, filed)
            op = "dedupe"
        else:
            new_sent = replace_citation(target, filed, display)
            op = "replace"
    else:
        if ref_spans(target):
            return {"ok": False, "reason": "already-cited", **item}
        para = next((p for p in paras_now if target in p), "")
        if any(same_ref((b, c, v), proposed)
               for b, c, v, _s, _e in ref_spans(para)):
            return {"ok": False, "reason": "already-cited", **item}
        new_sent = insert_citation_at_quote(target, item.get("quote", ""), display)
        op = "insert"
    if new_sent is None:
        return {"ok": False, "reason": "replace-failed", **item}
    # NB: **item spreads FIRST: item["sentence"] is the sanitized flag clause,
    # which must not clobber the located target (live corruption 2026-09-25).
    return {**item, "ok": True, "op": op, "applied": False, "proposed": display,
            "confidence": round(conf, 3), "overlap": shared, "tried": tried, "basis": basis,
            "old": target[:300], "new": new_sent[:300],
            "path": str(ef), "para_index": paras_now.index(
                next(p for p in paras_now if target in p)),
            "sentence": target, "new_sentence": new_sent}


def apply_correction(rec: dict, just_sync: bool = True) -> bool:
    path = Path(rec["path"])
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("sections", [])
    done = False
    for row in rows:
        if not isinstance(row, dict) or str(row.get("section")) != rec["section"]:
            continue
        paras = row.get("english") or []
        order = list(range(len(paras)))
        if isinstance(rec.get("para_index"), int) and 0 <= rec["para_index"] < len(paras):
            order.remove(rec["para_index"])
            order.insert(0, rec["para_index"])
        for i in order:
            para = paras[i]
            if rec["sentence"] in para:
                paras[i] = para.replace(rec["sentence"], rec["new_sentence"], 1)
                done = True
                break
    if not done:
        return False
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(path)
    if just_sync and rec.get("display"):
        sync_justification(rec["book"], rec["section"], rec["display"], rec["proposed"])
    try:  # every text change lands in the per-work audit log (status dashboard)
        if not (ROOT / "books" / rec["book"]).is_dir():
            raise LookupError("not a library book (tests)")
        import audit_log
        verb = "duplicate reference removed" if rec.get("op") == "dedupe" else f"{rec.get(display)} -> {rec.get(proposed)}"
        audit_log.record(rec["book"], "citation", f"Bible reference corrected ({rec.get(basis, verifier)}): {verb} (section {rec[section]})",
                         ref="scripts/jev_cite_correct.py", section=rec["section"])
    except Exception:
        pass
    return True


def main(argv=None) -> int:
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--flags", required=True)
    ap.add_argument("--mode", choices=["correct", "backfill"], default="correct")
    ap.add_argument("--min-conf", type=float, default=0.9)
    ap.add_argument("--verify-conf", type=float, default=0.0)
    ap.add_argument("--books", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    if not cf_token:
        print("need CF_TOKEN for proposer", flush=True)
        return 2
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("need TYPESAFE_API_KEY for verifier", flush=True)
        return 2
    flags = [json.loads(l) for l in open(args.flags, encoding="utf-8")]
    wanted = {b.strip() for b in args.books.split(",") if b.strip()}
    active = active_claim_text()
    threshold = args.verify_conf or (BACKFILL_CONF if args.mode == "backfill" else VERIFY_CONF)
    items = []
    for flag in flags:
        if args.mode == "correct":
            if flag.get("stratum") != "POS_DIRECT":
                continue
            if flag.get("choice") != "contradicts":
                continue
            if (flag.get("confidence") or 0) < args.min_conf:
                continue
            if flag.get("cf"):
                continue
            item = {"kind": "correct", "book": flag["book"], "section": flag["section"],
                    "display": flag["display"], "sentence": flag["clause"],
                    "flag_conf": flag["confidence"]}
        else:
            if (flag.get("noul") or 0) < args.min_conf:
                continue
            item = {"kind": "backfill", "book": flag["book"], "section": flag["section"],
                    "display": "", "sentence": flag["sentence"],
                    "quote": flag.get("quote", ""),
                    "flag_conf": flag["noul"]}
        if wanted and item["book"] not in wanted:
            continue
        if section_claimed(item["section"], active):
            item_skip = dict(item, ok=False, reason="active-claim")
            items.append(item_skip)
            continue
        items.append(item)
    if args.limit:
        items = sorted(items, key=lambda r: -(r.get("flag_conf") or 0))[:args.limit]
    receipts = []
    for n, item in enumerate(items, 1):
        if "ok" in item:
            receipts.append(item)
            print(f"[{n}/{len(items)}] {item['book']}/{item['section']} "
                  f"{item.get('display') or '(missing)'}: {item.get('reason', '?')}",
                  flush=True)
            continue
        try:
            rec = correct_item(item, cf_token, threshold)
        except Exception as e:  # noqa: BLE001 - one bad item never stops batch
            rec = dict(item, ok=False, reason=f"error: {e}"[:120])
        if rec.get("ok") and args.apply:
            rec["applied"] = apply_correction(rec)
            if not rec["applied"]:
                rec["reason"] = "write-missed"
        receipts.append(rec)
        if rec.get("ok") and args.apply and not rec.get("applied"):
            status = "OK-NOT-WRITTEN"
        else:
            status = "OK" if rec.get("ok") else rec.get("reason", "?")
        extra = f" -> {rec['proposed']}@{rec.get('confidence', 0)}" if rec.get("ok") else ""
        print(f"[{n}/{len(items)}] {item['book']}/{item['section']} "
              f"{item.get('display') or '(missing)'}: {status}{extra}", flush=True)
        time.sleep(0.2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for rec in receipts:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {args.out}", flush=True)
    ok = sum(1 for r in receipts if r.get("ok"))
    wrote = sum(1 for r in receipts if r.get("applied"))
    tail = f", {wrote} written" if args.apply else ", DRY RUN"
    print(f"done: {ok}/{len(receipts)} verified{tail}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
