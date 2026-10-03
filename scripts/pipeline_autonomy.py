#!/usr/bin/env python3
"""Shared autonomy helpers: JSON repair, chunking, arbiter rule.

Offline-safe: callers inject the inference function, so unit tests never
touch the network. Used by draft_claim (draft path) and ai_promote (checker
path) to survive malformed model output without a human in the loop.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from llm_bakeoff import extract_json  # noqa: E402  (pure function, offline-safe)

import re as _re

_SENTENCE_END = _re.compile(r"(?<=[.!?;\u0387])\s+")


def split_sentences(para: str) -> list[str]:
    """Split a paragraph on sentence ends (Greek-aware)."""
    return [s for s in _SENTENCE_END.split(para) if s.strip()]

REPAIR_SYS = (
    "You repair broken JSON output. Return ONLY the corrected JSON object, "
    "no other text, no markdown fences."
)


def repair_messages(broken: str, shape_desc: str) -> list[dict]:
    return [
        {"role": "system", "content": REPAIR_SYS},
        {
            "role": "user",
            "content": (
                "This output failed to parse as JSON. Fix it so it parses as "
                f"{shape_desc}. Keep every word identical; change only quoting, "
                f"escaping, and structure:\n\n{broken}"
            ),
        },
    ]


def parse_or_repair(
    call_fn,
    model: str,
    messages: list[dict],
    *,
    need: list[str],
    shape_desc: str,
    max_tokens: int | None,
    attempts: int = 2,
    repairs: int = 1,
    raw_sink=None,
) -> tuple[dict | None, dict]:
    """Call, extract JSON, repair on failure. Returns (obj or None, info).

    call_fn(model, messages, max_tokens) -> dict with content/error/ms/pt/ct.
    need lists keys the parsed object must contain. raw_sink(tag, content)
    receives every raw model output for receipts. Never raises on model or
    network misbehavior; reports it in info["error"] instead.
    """
    info: dict = {
        "model": model, "attempts_used": 0, "repaired": False,
        "ms": 0, "pt": 0, "ct": 0, "neurons": 0, "error": None, "raw": "",
    }

    def bank(raw) -> str:
        if not isinstance(raw, dict):
            return ""
        for key in ("ms", "pt", "ct", "neurons"):
            try:
                info[key] += raw.get(key) or 0
            except TypeError:
                pass
        return raw.get("content") or ""

    def valid(content: str):
        obj = extract_json(content)
        if isinstance(obj, dict) and all(k in obj for k in need):
            return obj
        return None

    for attempt in range(max(1, attempts)):
        try:
            raw = call_fn(model, messages, max_tokens)
        except Exception as exc:  # noqa: BLE001 - flakiness must not kill autonomy
            info["error"] = f"call_exception: {exc}"[:200]
            continue
        info["attempts_used"] += 1
        content = bank(raw)
        info["raw"] = content
        if raw_sink:
            raw_sink(f"try{attempt}", content)
        if isinstance(raw, dict) and raw.get("error"):
            info["error"] = str(raw["error"])[:200]
            continue
        obj = valid(content)
        if obj is not None:
            info["error"] = None
            return obj, info
        for rep in range(max(0, repairs)):
            try:
                fixed = call_fn(
                    model, repair_messages(content[:7000], shape_desc), max_tokens
                )
            except Exception as exc:  # noqa: BLE001
                info["error"] = f"repair_exception: {exc}"[:200]
                continue
            info["attempts_used"] += 1
            fixed_content = bank(fixed)
            info["raw"] = fixed_content
            if raw_sink:
                raw_sink(f"try{attempt}_repair{rep}", fixed_content)
            if isinstance(fixed, dict) and fixed.get("error"):
                info["error"] = str(fixed["error"])[:200]
                continue
            obj = valid(fixed_content)
            if obj is not None:
                info["error"] = None
                info["repaired"] = True
                return obj, info
        info["error"] = "parse_fail"
    return None, info


class SplitRefused(Exception):
    """A section cannot be chunked; carries an actionable plan."""

    def __init__(self, reason: str, plan: str):
        super().__init__(reason)
        self.plan = plan


def chunk_paragraphs(paras: list[str], max_chars: int) -> list[list[str]]:
    """Greedy paragraph packing with a sentence fallback.

    Whole paragraphs pack first; a single paragraph over budget splits on
    sentence ends (Greek-aware) instead of refusing. SplitRefused fires only
    when one sentence alone exceeds the budget.
    """
    units: list[str] = []
    for i, para in enumerate(paras):
        if len(para) > max_chars:
            sents = split_sentences(para)
            if len(sents) <= 1 or any(len(s) > max_chars for s in sents):
                raise SplitRefused(
                    f"paragraph {i + 1} has {len(para)} chars, over {max_chars}",
                    f"shorten paragraph {i + 1} in source or raise the chunk budget",
                )
            units.extend(sents)
        else:
            units.append(para)
    chunks: list[list[str]] = []
    cur: list[str] = []
    cur_len = 0
    for unit in units:
        if cur and cur_len + 2 + len(unit) > max_chars:
            chunks.append(cur)
            cur, cur_len = [], 0
        cur.append(unit)
        cur_len += (2 if cur_len else 0) + len(unit)
    if cur:
        chunks.append(cur)
    return chunks


_LIST_KEYS = (
    "english", "lemmas", "choices", "scripture_guesses", "bible_refs",
    "variants", "translator_notes", "added_allusions", "ocr_flags",
)


def merge_chunk_drafts(objs: list[dict]) -> dict:
    """Merge per-chunk draft objects into one section result.

    Title stays empty: the caller fills it with one micro-call over the
    merged English, since no single chunk sees the whole thought.
    """
    merged: dict = {
        "section": objs[0].get("section"),
        "title": "",
        "pass_a_gloss": "\n\n".join(
            str(o.get("pass_a_gloss") or "").strip() for o in objs
        ).strip(),
    }
    for key in _LIST_KEYS:
        out: list = []
        for obj in objs:
            value = obj.get(key)
            if isinstance(value, list):
                out.extend(value)
        merged[key] = out
    return merged


def split_guard(
    source_chars: int, *, chunk_chars: int = 1500, hard_max_chars: int = 12000
) -> str:
    """Draft-time size decision: single call, chunked calls, or refuse."""
    if source_chars > hard_max_chars:
        return "refuse"
    if source_chars > chunk_chars:
        return "chunk"
    return "single"


def arbiter_needed(
    ok_a: bool, ok_b: bool, api_a: bool = False, api_b: bool = False
) -> bool:
    """True only for a content split: API failures never go to arbiter."""
    if api_a or api_b:
        return False
    return bool(ok_a) != bool(ok_b)


def arbiter_rule(arbiter_ok: bool) -> tuple[str, str]:
    if arbiter_ok:
        return ("PROMOTE", "arbiter breaks split toward pass; dissent recorded")
    return ("HOLD", "split decision stands; parked, never published")


def _fold_letters(text: str) -> str:
    """Accent-folded letters only, so a hyphenated source line still matches."""
    import unicodedata
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("ς", "σ").casefold()
    return "".join(ch for ch in text if ch.isalpha())


def _norm_words(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = _re.sub(r"[^0-9A-Za-z]+", " ", text.casefold())
    return " ".join(text.split())


_GREEK_RUN = _re.compile(
    r"[\u0370-\u03FF\u1F00-\u1FFF]+(?:[\s\-\u00AD\u2010]*[\u0370-\u03FF\u1F00-\u1FFF]+)*"
)
_QUOTED = _re.compile(r"['\u2018\u2019\"]([^'\u2018\u2019\"]{12,240})['\u2018\u2019\"]")
_OMIT_WORD = _re.compile(
    r"\b(omits?|omitted|omitting|omission|missing|misses|lacks?|lacking|absent|dropped)\b",
    _re.IGNORECASE,
)
_ADD_WORD = _re.compile(
    r"\b(adds?|added|adding|addition|not\s+present|not\s+in\s+the\s+source|invent\w*)\b",
    _re.IGNORECASE,
)
_OTHER_DEFECT = _re.compile(
    r"\b(mistranslat\w*|contradicts?|should\s+be|wrong\s+citation|paraphras\w*|summar(?:y|ise|ize)\w*)\b",
    _re.IGNORECASE,
)
_CONTENT_STOP = {
    "the", "and", "that", "this", "with", "from", "they", "will", "have",
    "been", "were", "was", "are", "not", "but", "about", "where", "which",
    "their", "into", "than", "then", "also", "only", "more", "most", "such",
    "upon", "your", "them", "when", "what", "there", "here", "those", "these",
}


def _greek_quotes(sentence: str) -> list[str]:
    found = []
    for match in _GREEK_RUN.finditer(sentence or ""):
        letters = _fold_letters(match.group(0))
        if len(letters) >= 8:
            found.append(letters)
    return found


def _english_quotes(sentence: str) -> list[str]:
    found = []
    for match in _QUOTED.finditer(sentence or ""):
        start = match.start()
        if start > 0 and (sentence or "")[start - 1].isalpha():
            continue
        frag = match.group(1)
        if _GREEK_RUN.search(frag):
            continue
        norm = _norm_words(frag)
        if "pass a" in norm or "pass b" in norm:
            continue
        if len(norm) >= 20:
            found.append(norm)
    return found


def _quote_covered(span: str, norm_text: str) -> bool:
    # Exact match, or the quote's content words sit together and at most
    # a few of them differ. Scattered hits in a long reading do not count.
    if span and span in (norm_text or ""):
        return True
    words = [w for w in (span or "").split() if len(w) >= 4]
    if len(words) < 6:
        return False
    tokens = (norm_text or "").split()
    if not tokens:
        return False
    need = max(6, (len(words) * 85 + 99) // 100)
    width = len((span or "").split()) + 8
    for i in range(len(tokens)):
        chunk = tokens[i:i + width]
        if sum(1 for w in words if w in chunk) >= need:
            return True
    return False


def _garbled_quotes(sentence: str) -> list[str]:
    """Beta-code or broken transliteration quoted as if it were a clause."""
    found = []
    for match in _QUOTED.finditer(sentence or ""):
        start = match.start()
        if start > 0 and (sentence or "")[start - 1].isalpha():
            continue
        frag = match.group(1)
        if _GREEK_RUN.search(frag):
            continue
        if _re.search(r"[A-Za-z][)/\\=]|[/\\=][A-Za-z]", frag):
            found.append(frag)
    return found


def _content_words(text: str) -> list[str]:
    out = []
    for word in _norm_words(text).split():
        if word in _CONTENT_STOP or len(word) < 4:
            continue
        for suffix in ("ness", "ing", "ed", "ly", "es", "s"):
            if len(word) > len(suffix) + 4 and word.endswith(suffix):
                word = word[: -len(suffix)]
                break
        if len(word) >= 4:
            out.append(word)
    return out


def _units(texts: list[str]) -> list[str]:
    units = []
    for text in texts:
        chunk = str(text or "").strip()
        if not chunk:
            continue
        if len(chunk) < 500:
            units.append(chunk)
        else:
            units.extend(split_sentences(chunk) or [chunk])
    return units


def unsupported_pass_b_quotes(texts: list[str], pass_a: str, pass_b: str) -> list[dict]:
    """English a failing judge quoted from Pass B that Pass A does not support.

    Pass B may paraphrase Pass A. A quoted sentence is unsupported when fewer
    than half of its content words appear in any one Pass A sentence. That is
    the 'as they ascend, they will experience the perfection...' class: the
    gloss says the Church is perfect and blameless, and Pass B gives that
    perfection to the nations on the way up.
    """
    pass_b_norm = _norm_words(pass_b)
    pass_a_sents = split_sentences(pass_a) or [pass_a]
    found = []
    seen = set()
    for unit in _units(texts):
        for match in _QUOTED.finditer(unit):
            frag = match.group(1)
            if _GREEK_RUN.search(frag):
                continue
            norm = _norm_words(frag)
            if len(norm) < 40 or norm in seen or norm not in pass_b_norm:
                continue
            seen.add(norm)
            quote_words = _content_words(frag)
            if not quote_words:
                continue
            best = 0.0
            for sent in pass_a_sents:
                support = set(_content_words(sent))
                if not support:
                    continue
                best = max(best, sum(1 for word in quote_words if word in support) / len(quote_words))
            if best < 0.45:
                found.append({"quote": frag[:240], "overlap": round(best, 2)})
    return found


def refute_confabulated_clauses(texts: list[str], source: str, pass_a: str, pass_b: str) -> dict:
    """Drop judge claims that the locked text already contradicts.

    override is true only when every concrete defect is refuted. actionable
    sentences are the defects a revise must still fix. A sentence with no
    quoted span is vague and is ignored, so boilerplate checker instructions
    cannot park a slice or force a rewrite.
    """
    source_letters = _fold_letters(source)
    passes = _norm_words(pass_a) + " \n " + _norm_words(pass_b)
    norm_b = _norm_words(pass_b)
    actionable: list[str] = []
    refuted: list[dict] = []
    saw_defect = False
    for sentence in _units(texts):
        greek = _greek_quotes(sentence)
        english = _english_quotes(sentence)
        # Quoted Pass B that Pass A does not support is a real defect, unless
        # this same sentence quotes the source Greek that the English renders.
        if unsupported_pass_b_quotes([sentence], pass_a, pass_b):
            in_source_greek = [span for span in greek if span in source_letters]
            if not in_source_greek:
                saw_defect = True
                actionable.append(sentence)
                continue
        omission = _OMIT_WORD.search(sentence) is not None
        addition = _ADD_WORD.search(sentence) is not None
        other = _OTHER_DEFECT.search(sentence) is not None
        if not greek and not english:
            continue
        if omission and addition:
            saw_defect = True
            actionable.append(sentence)
            continue
        if omission:
            saw_defect = True
            if _complaint_targets_pass_a(sentence):
                refuted.append({"sentence": sentence[:220], "basis": "complaint-targets-pass-a"})
                continue
            in_b = [span for span in english if _quote_covered(span, norm_b)]
            garbled = _garbled_quotes(sentence)
            if english and in_b and len(in_b) == len(english):
                refuted.append({"sentence": sentence[:220], "basis": "omission-already-in-draft"})
            elif garbled and all(frag not in (source or "") for frag in garbled):
                refuted.append({"sentence": sentence[:220], "basis": "garbled-not-in-source"})
            elif greek and all(span not in source_letters for span in greek):
                refuted.append({"sentence": sentence[:220], "basis": "greek-not-in-source"})
            else:
                actionable.append(sentence)
            continue
        if addition:
            saw_defect = True
            in_draft = [span for span in english if span in passes]
            in_source = [span for span in greek if span in source_letters]
            if english and not in_draft:
                refuted.append({"sentence": sentence[:220], "basis": "addition-not-in-draft"})
            elif in_source and in_draft:
                refuted.append({"sentence": sentence[:220], "basis": "addition-is-translated-source"})
            else:
                actionable.append(sentence)
            continue
        if other:
            saw_defect = True
            actionable.append(sentence)
    return {
        "override": bool(saw_defect and not actionable),
        "actionable": actionable,
        "refuted": refuted,
    }


def receipt_structural_only(data: dict) -> bool:
    """True when every result failed the structural gate and no checker ran.

    A revise needs checker notes. Re-promoting this receipt does not change
    the bundle, so the caller has to draft instead.
    """
    results = data.get("results") or []
    if not results:
        return False
    saw = False
    for entry in results:
        structural = entry.get("structural") or {}
        if not structural:
            return False
        if structural.get("ok"):
            return False
        saw = True
    return saw


def missing_lemma_senses(lemmas, english) -> list:
    """Multi-word lemma glosses whose content words are all absent from Pass B.

    A single surviving word means the sense was paraphrased, not dropped.
    Single-word glosses are ignored (too easy to paraphrase).
    """
    blob = " ".join(english) if isinstance(english, list) else str(english or "")
    low = blob.casefold()
    gaps = []
    for item in lemmas or []:
        if not isinstance(item, dict):
            continue
        gloss = str(item.get("gloss") or "").strip()
        words = _re.findall(r"[A-Za-z]{4,}", gloss)
        if len(words) < 2:
            continue
        if any(word.casefold() in low for word in words):
            continue
        form = str(item.get("form") or item.get("lemma") or "").strip()
        gaps.append(
            "Restore the sense of %s (%s). Put that sense in the sentence that dropped it. Do not add a second sentence that only repeats it."
            % (form, gloss)
        )
    return gaps


def source_is_betacode(text: str) -> bool:
    """True when the locked source is still TLG betacode, not Greek letters.

    A Latin title on a Greek paragraph is not betacode.
    """
    body = text or ""
    if _re.search(r"[A-Za-z][)/\\=]|[/\\=][A-Za-z]", body) is None:
        return False
    letters = [ch for ch in body if ch.isalpha()]
    if not letters:
        return True
    greek = 0
    for ch in letters:
        code = ord(ch)
        if 0x0370 <= code <= 0x03FF or 0x1F00 <= code <= 0x1FFF:
            greek += 1
    return greek * 2 < len(letters)

def arbiter_abstained(check) -> bool:
    if not isinstance(check, dict):
        return False
    if check.get("decision") == "ABSTAIN":
        return True
    return check.get("error") == "no_independent_checker_family"


def _complaint_targets_pass_a(sentence: str) -> bool:
    # "Pass A omits X (Pass B includes it)" is a gloss complaint.
    # It must not send Pass B back for a rewrite.
    low = (sentence or "").casefold()
    if not _re.search(r"\bpass\s*a\b", low):
        return False
    if not _re.search(r"\b(includes|include|contains|preserves)\b", low):
        return False
    if _re.search(
        r"\bpass\s*b\b.{0,80}\b(omits?|omitted|omitting|missing|misses|lacks?|dropped)\b",
        low,
    ):
        return False
    if _re.search(
        r"\b(omits?|omitted|missing|misses|lacks?|dropped)\b.{0,40}\bpass\s*b\b",
        low,
    ):
        return False
    return True


def unsatisfied_repair_notes(notes, english) -> list:
    blob = " ".join(english) if isinstance(english, list) else str(english or "")
    out = []
    for item in notes or []:
        if not isinstance(item, dict):
            continue
        word = str(item.get("until_absent") or "").strip()
        note = str(item.get("note") or "").strip()
        if len(word) < 5 or not note:
            continue
        still_there = _re.search(r"\b%s\b" % _re.escape(word), blob, _re.IGNORECASE) is not None
        missing_sense = False
        for piece in _re.findall(r"[A-Za-z]+", str(item.get("sentence_has") or "")):
            if len(piece) < 4:
                continue
            if not _re.search(r"\b%s\b" % _re.escape(piece), blob, _re.IGNORECASE):
                missing_sense = True
                break
        if still_there or missing_sense:
            out.append(note)
    return out


def concrete_omission_note(note: str) -> str:
    low = (note or "").casefold()
    if _re.search(r"\bpass\s*b\b", low) and _re.search(
        r"\b(includes|include|contains|preserves)\b", low
    ):
        return ""
    if not _OMIT_WORD.search(note or ""):
        return ""
    spans = []
    for match in _GREEK_RUN.finditer(note or ""):
        surface = " ".join(match.group(0).split())
        if len(_fold_letters(surface)) < 8 or surface in spans:
            continue
        spans.append(surface)
    if not spans:
        return ""
    return (
        "Add this missing clause to Pass B in the sentence it belongs to. "
        "Do not add a second sentence that only repeats it: "
        + spans[0]
    )


def stable_defect_key(texts) -> str:
    parts = []
    for text in texts or []:
        raw = str(text or "")
        if raw.startswith("Rewrite this sentence") or raw.startswith("Restore the sense of"):
            continue
        if raw.startswith("Add this missing clause"):
            continue
        for span in _greek_quotes(raw):
            parts.append("g:" + span)
        for span in _english_quotes(raw):
            parts.append("e:" + span[:80])
    if not parts:
        return ""
    return "|".join(sorted(set(parts))[:6])

