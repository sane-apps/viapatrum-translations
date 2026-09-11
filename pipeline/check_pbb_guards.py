"""Fail closed on Personal Book builder anti-patterns (SOP 2026-09-10)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_build_scripts() -> list[str]:
    errs: list[str] = []
    for path in (ROOT / "books").glob("*/build_book.py"):
        text = path.read_text(encoding="utf-8")
        if "FootnoteStore" in text or "from pipeline.footnotes" in text:
            errs.append(f"{path.relative_to(ROOT)}: uses pipeline.footnotes / FootnoteStore — banned for PBB")
        # Caption dump label
        if re.search(r'["\']Scripture connection["\']', text):
            errs.append(
                f"{path.relative_to(ROOT)}: emits 'Scripture connection' captions — "
                "use inline Bible links; 'Possible allusion' / 'Cf.' only for leftovers"
            )
    return errs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.parse_args()
    errs = check_build_scripts()
    if errs:
        print("FAIL PBB guards")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("OK PBB guards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
