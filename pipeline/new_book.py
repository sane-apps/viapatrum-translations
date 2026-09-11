"""Scaffold a new book under books/<slug>/."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "book"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slug", required=True, help="folder name under books/, e.g. julian-of-eclanum")
    p.add_argument("--title", required=True, help="Logos book title")
    p.add_argument("--author", default="", help="Author field")
    args = p.parse_args(argv)
    dest = ROOT / "books" / args.slug
    if dest.exists():
        print(f"already exists: {dest}", file=sys.stderr)
        return 1
    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 1
    shutil.copytree(TEMPLATE, dest)
    for name in ("book.yml", "SESSION_HANDOFF.md", "build_book.py"):
        path = dest / name
        text = path.read_text()
        text = (
            text.replace("{{TITLE}}", args.title)
            .replace("{{AUTHOR}}", args.author or args.title)
            .replace("{{SLUG}}", args.slug)
        )
        path.write_text(text)
    (dest / "sources").mkdir(exist_ok=True)
    (dest / "translations").mkdir(exist_ok=True)
    print(f"created {dest}")
    print("Next: fill sources/, translations/, then edit build_book.py — see docs/SOP.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
