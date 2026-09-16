#!/usr/bin/env python3
"""Book identity, single source of truth.

Author and title live in each book's ``book.yml``. Builders must load them
from here instead of hardcoding strings: hardcoded copy-paste once shipped
five books all titled as another author's work.
"""
from __future__ import annotations

from pathlib import Path

REQUIRED = ("title", "author", "slug")


def load_book_meta(book_dir: str | Path) -> dict:
    """Read flat ``book.yml`` (no dependency beyond the standard library)."""
    meta: dict[str, str] = {}
    text = (Path(book_dir) / "book.yml").read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line or line[0] in (" ", "\t", "#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    missing = [k for k in REQUIRED if k not in meta]
    if missing:
        raise ValueError(f"{book_dir}/book.yml lacks: {', '.join(missing)}")
    return meta
