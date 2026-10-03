#!/usr/bin/env python3
"""Local KJV verse lookup (public-domain text, data/en_kjv.json).

Source: thiagobodruk/bible json/en_kjv.json (English verse text; the book
*names* in that file are Portuguese, so books map by canonical index, never
by name). Deuterocanon is absent from KJV: lookups there return "".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

KJV_PATH = Path(__file__).resolve().parents[1] / "data" / "en_kjv.json"

CANONICAL_IDS = [
    "gen", "exod", "lev", "num", "deut", "josh", "judg", "ruth",
    "1sam", "2sam", "1kgs", "2kgs", "1chr", "2chr", "ezra", "neh",
    "esth", "job", "ps", "prov", "eccl", "song", "isa", "jer",
    "lam", "ezek", "dan", "hos", "joel", "amos", "obad", "jonah",
    "mic", "nah", "hab", "zeph", "hag", "zech", "mal",
    "matt", "mark", "luke", "john", "acts", "rom",
    "1cor", "2cor", "gal", "eph", "phil", "col",
    "1thess", "2thess", "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet", "1jn", "2jn", "3jn", "jude", "rev",
]

_cache: dict | None = None


def _load():
    global _cache
    if _cache is None:
        books = json.loads(KJV_PATH.read_text(encoding="utf-8"))
        assert len(books) == 66, f"KJV book count {len(books)}"
        _cache = {}
        for book_id, entry in zip(CANONICAL_IDS, books):
            _cache[book_id] = entry.get("chapters") or []
        probe = verse_text("john", 3, 16)
        assert "God so loved the world" in probe, f"KJV text check failed: {probe[:60]!r}"
    return _cache


def verse_text(book_id: str, chapter: int, verse: int | None = None) -> str:
    """Verse text ("" when unknown); verse None joins the whole chapter."""
    try:
        chapters = _load()[book_id]
        ch = chapters[int(chapter) - 1]
    except (KeyError, IndexError, ValueError, TypeError):
        return ""
    if verse is None:
        return " ".join(ch)
    try:
        return ch[int(verse) - 1]
    except (IndexError, ValueError, TypeError):
        return ""


def verse_window(book_id: str, chapter: int, verse: int | None) -> str:
    """Target verse plus neighbors (numbering drifts across traditions)."""
    if verse is None:
        return verse_text(book_id, chapter, None)
    parts = [verse_text(book_id, chapter, verse - 1),
             verse_text(book_id, chapter, verse),
             verse_text(book_id, chapter, verse + 1)]
    return " ".join(p for p in parts if p)
