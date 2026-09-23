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
