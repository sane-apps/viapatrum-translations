#!/usr/bin/env python3
"""Refuse tip / SERIES CLOSEOUT unless english+source files pass publication guards.

Root cause this closes: Rank-1 tips stamped done while english still had
Lemma-led / Rem early scaffolds (or source had tip ops language). The fathers
catalogue gate then held hundreds of works. Tip closeout must fail here first.

  python3 scripts/assert_tip_ready.py \\
    books/<book>/translations/<stem>_english.json \\
    books/<book>/translations/<stem>_source.json
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.check_pass_ab import check_translation_files, main as check_main


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print(
            "Usage: python3 scripts/assert_tip_ready.py <english.json> <source.json>",
            file=sys.stderr,
        )
        return 2
    eng, src = Path(args[0]), Path(args[1])
    if not eng.is_file() or not src.is_file():
        print(f"FAIL: missing file(s): {eng} {src}", file=sys.stderr)
        return 1
    # Reuse the shared CLI so one code path owns the message shape.
    return check_main(["--tip-ready", str(eng), str(src)])


if __name__ == "__main__":
    # Keep import of check_translation_files for tests; CLI delegates.
    _ = check_translation_files
    raise SystemExit(main())
