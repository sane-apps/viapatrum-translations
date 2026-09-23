#!/usr/bin/env python3
"""Work-lane lookup: book slug -> lane, lane status/shares, book years.

Work lanes (translate direction: rank1/reformed/densify/topics/latin) are
distinct from compute lanes (model lanes cf/nv/gemini). Registry lives in
docs/work-lanes.json; per-book override via book.yml `lane:` field.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads((ROOT / "docs/work-lanes.json").read_text())


@lru_cache(maxsize=1)
def catalog_years() -> dict:
    """slug -> year from the generated catalog (9999-ish unknown handled by caller)."""
    path = ROOT / "docs/corpus-catalog.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return {}
    return {r.get("slug"): r.get("year", 9999) for r in data.get("rows", [])}


@lru_cache(maxsize=1)
def refresh_slugs() -> set:
    path = ROOT / "docs/corpus-catalog.json"
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return set()
    return {r.get("slug") for r in data.get("rows", []) if r.get("lineage") == "refresh"}


def book_lane(slug: str) -> str:
    reg = registry()
    lanes = reg.get("lanes", {})
    # 1. per-book override in book.yml
    meta = ROOT / "books" / slug / "book.yml"
    if meta.is_file():
        for line in meta.read_text(encoding="utf-8").splitlines():
            if line.startswith("lane:"):
                lane = line.split(":", 1)[1].strip().strip("\"'")
                if lane in lanes:
                    return lane
    # 2. explicit registry lists
    for name, cfg in lanes.items():
        if slug in (cfg.get("books") or []):
            return name
    # 3. dynamic: catalog refresh lineage -> densify
    if slug in refresh_slugs():
        return "densify"
    # 4. default (paused rank1: new books wait for conscious assignment)
    return reg.get("default_lane", "rank1")


def lane_status(lane: str) -> str:
    return (registry().get("lanes", {}).get(lane) or {}).get("status", "unknown")


def lane_share(lane: str) -> float:
    try:
        return float((registry().get("lanes", {}).get(lane) or {}).get("budget_share_pct", 0)) / 100.0
    except (TypeError, ValueError):
        return 0.0


def book_year(slug: str) -> int:
    try:
        return int(catalog_years().get(slug, 9999))
    except (TypeError, ValueError):
        return 9999


def is_active(lane: str) -> bool:
    return lane_status(lane) == "active"
