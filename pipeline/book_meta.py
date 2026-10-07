#!/usr/bin/env python3
"""Book identity, single source of truth.

Author and title live in each book's ``book.yml``. Builders must load them
from here instead of hardcoding strings: hardcoded copy-paste once shipped
five books all titled as another author's work.
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED = ("title", "author", "slug")


def unquote_scalar(raw: str) -> str:
    """Return a flat YAML scalar's value, removing one pair of quotes only.

    Stripping every quote character from both ends once cut the closing
    quote off "Fragment on 'Rejoice in that day'". A single-quoted value
    doubles its inner single quotes; a double-quoted value uses backslash
    escapes, which JSON reads the same way for the cases book.yml uses.
    """
    val = raw.strip()
    if len(val) >= 2 and val[0] == val[-1] == "'":
        return val[1:-1].replace("''", "'")
    if len(val) >= 2 and val[0] == val[-1] == '"':
        try:
            out = json.loads(val)
        except ValueError:
            return val[1:-1]
        return out if isinstance(out, str) else val[1:-1]
    return val


def load_book_meta(book_dir: str | Path) -> dict:
    """Read flat ``book.yml`` (no dependency beyond the standard library)."""
    meta: dict[str, str] = {}
    text = (Path(book_dir) / "book.yml").read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line or line[0] in (" ", "\t", "#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = unquote_scalar(value)
    missing = [k for k in REQUIRED if k not in meta]
    if missing:
        raise ValueError(f"{book_dir}/book.yml lacks: {', '.join(missing)}")
    return meta
