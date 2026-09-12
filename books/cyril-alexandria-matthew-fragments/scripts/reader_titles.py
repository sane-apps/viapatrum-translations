"""Reader-facing titles for Cyril Matthew fragments (CPG 5206).

TOC / H1 labels are plain English (“Matthew 1:16”).
CPG / fragment / locus strings stay in scholar_label for apparatus.
"""

from __future__ import annotations

import re


def normalize_matthew_ref(matthew: str | None) -> str:
    """Turn stored matthew refs into a stable display form with en-dashes."""
    raw = (matthew or "").strip()
    if not raw:
        return ""
    # Prefer en-dash in ranges (11-12 → 11–12; 24:51-25:9 → 24:51–25:9)
    return re.sub(r"(?<=\d)-(?=\d)", "–", raw)


def reader_title(matthew: str | None) -> str:
    ref = normalize_matthew_ref(matthew)
    return f"Matthew {ref}" if ref else "Matthew fragment"


def fragment_from_title(title: str | None) -> int | None:
    m = re.search(r"\bfr\.(\d+)\b", title or "", re.I)
    return int(m.group(1)) if m else None


def scholar_label(
    *,
    cpg: int = 5206,
    fragment: int | None,
    matthew: str | None,
    existing: str | None = None,
) -> str:
    """Keep the edition-style label for About / apparatus."""
    existing = (existing or "").strip()
    if existing.startswith("CPG"):
        return existing
    ref = normalize_matthew_ref(matthew).replace(":", ", ")
    if fragment is None:
        return f"CPG {cpg}" + (f" on Mt {ref}" if ref else "")
    return f"CPG {cpg} fr.{fragment}" + (f" on Mt {ref}" if ref else "")


def matthew_sort_key(
    matthew: str | None,
    fragment: int | None,
    section: int | str | None,
) -> tuple[int, int, int, int]:
    nums = [int(x) for x in re.findall(r"\d+", str(matthew or ""))]
    ch = nums[0] if nums else 999
    vs = nums[1] if len(nums) > 1 else 0
    try:
        sec = int(section)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        sec = 0
    fr = int(fragment) if fragment is not None else sec
    return (ch, vs, fr, sec)
