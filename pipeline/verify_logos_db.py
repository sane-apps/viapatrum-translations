"""Verify Logos PersonalBooks DB after a Build (Air)."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def default_db() -> Path:
    home = Path.home()
    # Logos4 Documents/<profile>/PersonalBooks/PersonalBookManager.db
    base = home / "Library/Application Support/Logos4/Documents"
    if not base.exists():
        raise SystemExit(f"Logos Documents folder missing: {base}")
    candidates = list(base.glob("*/PersonalBooks/PersonalBookManager.db"))
    if not candidates:
        raise SystemExit(f"No PersonalBookManager.db under {base}")
    # Prefer non-empty / newest mtime
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def verify(db: Path, title_substr: str) -> list[str]:
    errors: list[str] = []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT Id, Title, LastCompiled, ResourceId FROM Books WHERE IsDeleted=0 AND Title LIKE ?",
            (f"%{title_substr}%",),
        ).fetchall()
        if not rows:
            return [f"no book matching %{title_substr}% in {db}"]
        for book_id, title, last, rid in rows:
            print(f"book id={book_id} title={title!r} LastCompiled={last} ResourceId={rid}")
            if not last:
                errors.append(f"{title!r}: LastCompiled empty")
            polluted = con.execute(
                """
                SELECT count(*) FROM ArticleCache
                WHERE BookId=? AND (
                  Context LIKE '%[[@Headword:%' OR ArticleId LIKE '%[[@Headword:%'
                )
                """,
                (book_id,),
            ).fetchone()[0]
            sample = con.execute(
                "SELECT Context FROM ArticleCache WHERE BookId=? LIMIT 5",
                (book_id,),
            ).fetchall()
            print(f"  ArticleCache samples: {len(sample)}; polluted_context_hits={polluted}")
            if polluted:
                errors.append(f"{title!r}: {polluted} ArticleCache rows still contain [[@Headword:")
            total = con.execute(
                "SELECT count(*) FROM ArticleCache WHERE BookId=?",
                (book_id,),
            ).fetchone()[0]
            print(f"  ArticleCache count={total}")
            if total == 0:
                errors.append(f"{title!r}: ArticleCache empty (not compiled?)")
    finally:
        con.close()
    return errors


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--title-substr", required=True)
    p.add_argument("--db", type=Path, default=None)
    args = p.parse_args(argv)
    db = args.db or default_db()
    print(f"db={db}")
    errs = verify(db, args.title_substr)
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
