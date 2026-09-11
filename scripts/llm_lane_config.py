#!/usr/bin/env python3
"""Load Fathers dual-lane draft/checker config + API-error helpers."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "docs" / "LLM_LANE_CONFIG.json"

API_ERROR_RE = re.compile(
    r"(?i)(HTTP\s*410|end of life|HTTP\s*404|HTTP\s*5\d\d|timeout|timed out|"
    r"empty SSE|empty message|fetch failed|connection|503|429|rate)"
)


def load_lane_config(path: str | Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    if "lanes" not in data:
        raise SystemExit(f"Bad lane config (no lanes): {p}")
    return data


def is_api_error(err: str | None) -> bool:
    if not err:
        return False
    return bool(API_ERROR_RE.search(str(err)))


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(x) for x in value if x]
