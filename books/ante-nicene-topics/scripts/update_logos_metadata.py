#!/usr/bin/env python3
"""Update Logos Personal Book Id=4 metadata (title, description, cover, body path).

Run with Logos quit or after closing the PB editor if SQLite is locked.
Prefers the new Desktop body file AnteNicene-Dogmatics.docx.
"""
from __future__ import annotations

import sqlite3
import urllib.parse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
COVER = ROOT / "assets" / "cover.jpg"
BODY = Path.home() / "Desktop" / "AnteNicene-Dogmatics.docx"
BODY_LEGACY = Path.home() / "Desktop" / "AnteNicene-Soteriology.docx"
DB = Path.home() / "Library/Application Support/Logos4/Documents/adcocvnb.nzw/PersonalBooks/PersonalBookManager.db"

TITLE = "Ante-Nicene Dogmatics"
AUTHORS = "Ante-Nicene Fathers (topical library)"
DESCRIPTION = (
    "Modern English excerpts from the ante-Nicene fathers, arranged by the main "
    "topics of Christian teaching — God, Christ, Scripture, Spirit, church, "
    "sacraments, salvation, human will, last things, and the Christian life. "
    "One Logos encyclopedia for private study. Famous voices and lesser-known "
    "ones appear together under each topic, earliest to latest. Not a complete "
    "dogmatics and not a critical edition of the Greek or Latin."
)
COPYRIGHT = "Ancient texts; new English topical library prepared for private study, 2026."
BOOK_ID = 4


def main() -> int:
    if not DB.exists():
        raise SystemExit(f"missing Logos DB: {DB}")
    if not COVER.exists():
        raise SystemExit(f"missing cover: {COVER}")
    body = BODY if BODY.exists() else BODY_LEGACY
    if not body.exists():
        raise SystemExit(f"missing body DOCX: {BODY} or {BODY_LEGACY}")

    cover_blob = COVER.read_bytes()
    # Logos SourceFilePaths are URL-encoded absolute paths with %2f separators.
    encoded = urllib.parse.quote(str(body), safe="")
    now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")
    # insert colon in timezone offset: -0400 -> -04:00
    if len(now) >= 5 and now[-5] in "+-" and now[-3] != ":":
        now = now[:-2] + ":" + now[-2:]

    con = sqlite3.connect(DB)
    before = con.execute(
        "SELECT Title, length(CoverImage), SourceFilePaths FROM Books WHERE Id=?",
        (BOOK_ID,),
    ).fetchone()
    con.execute(
        """
        UPDATE Books SET
          Title = ?,
          Authors = ?,
          Description = ?,
          Copyright = ?,
          Language = 'en',
          ResourceType = 'text.monograph.encyclopedia',
          CoverImage = ?,
          SourceFilePaths = ?,
          ModifiedDate = ?
        WHERE Id = ?
        """,
        (TITLE, AUTHORS, DESCRIPTION, COPYRIGHT, cover_blob, encoded, now, BOOK_ID),
    )
    con.commit()
    after = con.execute(
        "SELECT Title, length(CoverImage), substr(Description,1,80), SourceFilePaths FROM Books WHERE Id=?",
        (BOOK_ID,),
    ).fetchone()
    con.close()
    print({"before": before, "after": after, "body": str(body), "cover_bytes": len(cover_blob)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
