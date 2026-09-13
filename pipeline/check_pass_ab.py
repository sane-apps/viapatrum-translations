#!/usr/bin/env python3
"""Deterministic two-pass checks. A clean result is not a fidelity verdict."""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys
import unicodedata

GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD|FIXME|YYYY)\b|\[n\d+\]|\blemma-led\s+open\b|"
    r"\brem\s+(?:early|mid|closeout)\s*:|\blemma and argument toward the thesis\b|"
    r"\b(?:see translations/|see working file|full cleaned source)\b", re.I
)
CONTAMINATION = re.compile(
    r"\bMelito skipped\b|\bnever Cyril Matthew densify\b|\bpro cibo temporary\b|"
    r"\b(?:SERIES CLOSEOUT|true OET|skip Pusey-PD)\b", re.I
)


def join_b(value) -> str:
    if isinstance(value, list):
        return " ".join(str(x) for x in value).strip()
    return str(value or "").strip()


def visible_text(text: str) -> str:
    text = re.sub(r"\[\[([^\[\]]+?)\s*>>\s*[^\]]+\]\]", r"\1", text)
    return re.sub(r"\[\[@[^\]]+\]\]", "", text)


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKC", visible_text(text)).casefold()
    return " ".join(re.findall(r"[^\W_]+", text, re.UNICODE))


def greek_ratio(text: str) -> float:
    return len(GREEK.findall(text)) / max(sum(c.isalpha() for c in text), 1)


def content_errors(value, label="english", *, source=False) -> list[str]:
    if not isinstance(value, (str, list)) or (isinstance(value, list) and any(
            not isinstance(p, str) or not p.strip() for p in value)):
        return [f"{label}: expected nonempty strings"]
    text = join_b(value)
    errors = []
    if not text:
        errors.append(f"{label}: empty text")
    # Numbered footnote markers belong in some raw-source transcriptions;
    # they remain invalid unresolved placeholders in the English reading text.
    check_text = re.sub(r"\[n\d+\]", "", text) if source else text
    if PLACEHOLDER.search(check_text) or CONTAMINATION.search(check_text):
        errors.append(f"{label}: placeholder or operational text")
    if not source and text and greek_ratio(visible_text(text)) > 0.25:
        errors.append(f"{label}: copied Greek needs review; expected English")
    return errors


def check_record(j: dict) -> list[str]:
    if not isinstance(j, dict):
        return ["justification must be an object"]
    a, b, src = (join_b(j.get(k)) for k in ("pass_a_gloss", "pass_b_english", "source_text"))
    errors = content_errors(j.get("pass_a_gloss"), "pass_a_gloss")
    errors += content_errors(j.get("pass_b_english"), "pass_b_english")
    errors += content_errors(j.get("source_text"), "source_text", source=True)
    na, nb = normalized(a), normalized(b)
    if na and nb:
        if na == nb:
            errors.append("Pass A copies Pass B (including formatting-only differences)")
        elif min(len(na.split()), len(nb.split())) >= 8:
            smaller, larger = sorted((na, nb), key=len)
            if smaller in larger or SequenceMatcher(None, na.split(), nb.split(), autojunk=False).ratio() >= 0.90:
                errors.append("Pass A and Pass B are near-copies; independent gloss needs review")
    if normalized(src) and normalized(src) == nb:
        errors.append("Pass B copies source text")
    for key in ("lemmas", "choices"):
        rows = j.get(key)
        if not isinstance(rows, list) or not rows or any(not isinstance(x, dict) or not x for x in rows):
            errors.append(f"{key}: expected nonempty objects")
    return errors


def check_file(path: Path) -> list[str]:
    try:
        return check_record(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        return [f"cannot read justification: {exc}"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="justification files or directories")
    args = parser.parse_args(argv)
    files = sorted({f for path in args.paths for f in
                    (path.glob("*.json") if path.is_dir() else [path])})
    if not files:
        print("FAIL: no justification files found")
        return 1
    failures = 0
    for path in files:
        errors = check_file(path)
        if errors:
            failures += 1
            print(f"FAIL {path.name}: {'; '.join(errors)}")
    print(f"ok={len(files) - failures} fail={failures} total={len(files)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
