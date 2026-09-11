#!/usr/bin/env python3
"""Fail justifications that are not a real two-pass (Pass A gloss vs Pass B English)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")


def join_b(b) -> str:
    if isinstance(b, list):
        return " ".join(str(x) for x in b).strip()
    return (b or "").strip()


def greek_ratio(s: str) -> float:
    if not s:
        return 0.0
    g = len(GREEK.findall(s))
    return g / max(len(s), 1)


def check_file(path: Path) -> list[str]:
    j = json.loads(path.read_text(encoding="utf-8"))
    errs = []
    a = (j.get("pass_a_gloss") or "").strip()
    b = join_b(j.get("pass_b_english"))
    src = (j.get("source_text") or "").strip()
    if not a:
        errs.append("empty pass_a_gloss")
    if not b or b.startswith("(see translations/"):
        errs.append("pass_b_english missing or still a pointer")
    if a and b and a == b:
        errs.append("Pass A copies Pass B")
    if a and greek_ratio(a) > 0.25:
        errs.append("Pass A looks like Greek, not an English gloss")
    if not (j.get("lemmas") or []):
        errs.append("empty lemmas")
    if not (j.get("choices") or []):
        errs.append("empty choices")
    if not src or src.startswith("[full cleaned"):
        errs.append("source_text missing or placeholder")
    return errs


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", type=Path, help="justification files or directories")
    args = p.parse_args(argv)
    files: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        else:
            files.append(path)
    n_fail = 0
    n_ok = 0
    for f in files:
        errs = check_file(f)
        if errs:
            n_fail += 1
            print(f"FAIL {f.name}: {'; '.join(errs)}")
        else:
            n_ok += 1
    print(f"ok={n_ok} fail={n_fail} total={len(files)}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
