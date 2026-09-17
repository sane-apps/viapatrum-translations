#!/usr/bin/env python3
"""Sync Personal Books metadata from books/*/book.yml into Logos' PersonalBookManager.db.

FAST PATH (standard — replaces all GUI field-filling and file-picker work):
  1. Quit Logos completely (Cmd+Q; verify: pgrep -x Logos prints nothing).
  2. python3 scripts/pb_sync.py            # dry run, prints planned actions
     python3 scripts/pb_sync.py --apply    # backup DB, write changes
  3. Reopen Logos:  open -a Logos ; open 'logos4:PersonalBooks'
  4. In the Personal Books tool, open each book's Edit view and click
     "Build book". GUI is used ONLY for Build clicks — never for typing
     metadata (typing into Edit fields while another field has a selection
     destroys text; cursor-verified clicks only).

Proven mappings (Air, Logos 53.1, 2026-09-17):
  - Books.ResourceType "text.monograph.ancient.manuscript.translation"
    displays as Type "Ancient Manuscript Translation". The "text.monograph."
    prefix is REQUIRED — without it the raw dotted string shows in the UI.
  - "text.monograph.encyclopedia" = Encyclopedia. "text.monograph" = Monograph.
  - Edit fields map 1:1 to columns: Title, Authors, Copyright, Description,
    Language ('en'), CoverImage blob, SourceFilePaths (URL-encoded abs path).
  - Field edits in the GUI save to the DB immediately (no save button).
  - book.yml is the source of truth: title, author, docx, pb_type,
    description, copyright, resource_id, logos_book_id.
"""

import argparse
import datetime
import glob
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PB_DB = os.path.expanduser(
    "~/Library/Application Support/Logos4/Documents"
    "/adcocvnb.nzw/PersonalBooks/PersonalBookManager.db"
)
BACKUP_DIR = os.path.join(REPO, "outputs", "pb-db-backups")

LANG_MAP = {"English": "en"}
FALLBACK_TYPES = {
    "Monograph": "text.monograph",
    "Encyclopedia": "text.monograph.encyclopedia",
}


def fail(msg):
    print(f"pb_sync: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def logos_running():
    try:
        out = subprocess.run(
            ["pgrep", "-x", "Logos"], capture_output=True, text=True
        )
        return out.returncode == 0
    except FileNotFoundError:
        return False


_SCALAR_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def _unquote(val):
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def load_yml(path):
    """Read flat scalar keys from book.yml (skips | blocks, lists, comments)."""
    data = {}
    with open(path, encoding="utf-8") as f:
        in_block = False
        for line in f:
            if in_block:
                if line.startswith((" ", "\t")) or line.strip() == "":
                    continue
                in_block = False
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = _SCALAR_RE.match(line)
            if not m:
                continue
            key, val = m.group(1), m.group(2)
            if val.strip() in ("|", ">"):
                in_block = True
                continue
            if val.strip().startswith(("- ", "[")):
                continue
            data[key] = _unquote(val)
    for k in ("logos_book_id",):
        if k in data and data[k] == "":
            del data[k]
    return data


def backfill_yml(path, resource_id, book_id):
    """Surgically set resource_id / logos_book_id, preserving everything else."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text, n = re.subn(
        r'(?m)^resource_id:\s*""\s*$',
        f'resource_id: "{resource_id}"',
        text,
        count=1,
    )
    if n == 0 and "resource_id" not in text:
        text = text.rstrip("\n") + f'\nresource_id: "{resource_id}"\n'
    if re.search(r"(?m)^logos_book_id:", text):
        text = re.sub(
            r"(?m)^logos_book_id:.*$",
            f"logos_book_id: {book_id}",
            text,
            count=1,
        )
    else:
        text = re.sub(
            r"(?m)^(resource_id:.*)$",
            f"\\1\nlogos_book_id: {book_id}",
            text,
            count=1,
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def book_row(slug, yml, yml_path):
    docx_name = yml.get("docx") or ""
    docx_path = os.path.join(REPO, "books", slug, docx_name)
    if not docx_name or not os.path.exists(docx_path):
        return None, f"missing docx: {docx_path}"
    cover = None
    for cand in ("cover.jpg", "cover.png"):
        p = os.path.join(REPO, "books", slug, "assets", cand)
        if os.path.exists(p):
            with open(p, "rb") as f:
                cover = f.read()
            break
    lang = LANG_MAP.get(yml.get("language", "English"), "en")
    pb_type = yml.get("pb_type") or FALLBACK_TYPES.get(
        yml.get("resource_type", "Monograph"), "text.monograph"
    )
    return (
        {
            "title": yml.get("title", ""),
            "authors": yml.get("author", ""),
            "description": yml.get("description", ""),
            "language": lang,
            "copyright": yml.get("copyright", ""),
            "resource_type": pb_type,
            "cover": cover,
            "src": urllib.parse.quote(os.path.abspath(docx_path), safe=""),
            "now": datetime.datetime.now()
            .astimezone()
            .isoformat(timespec="seconds"),
        },
        None,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="write changes (default: dry run)")
    ap.add_argument("--force", action="store_true",
                    help="run even if Logos is open (risks lost writes)")
    ap.add_argument("--delete-resource", action="append", default=[],
                    metavar="PBB:...",
                    help="delete a stale book row by ResourceId")
    args = ap.parse_args()

    if args.apply and logos_running() and not args.force:
        fail("Logos is running. Quit it first (Cmd+Q), then re-run.")

    con = sqlite3.connect(PB_DB, timeout=30)
    cur = con.cursor()
    existing = {
        r[0]: r
        for r in cur.execute(
            "SELECT ResourceId,Id,Title,Authors FROM Books WHERE IsDeleted=0"
        )
    }
    by_title = {}
    for rid, bid, title, authors in existing.values():
        by_title.setdefault((title, authors), []).append((rid, bid))

    plan = []
    for yml_path in sorted(glob.glob(os.path.join(REPO, "books", "*", "book.yml"))):
        slug = os.path.basename(os.path.dirname(yml_path))
        yml = load_yml(yml_path)
        row, err = book_row(slug, yml, yml_path)
        if err:
            plan.append((slug, f"SKIP ({err})", None))
            continue
        rid = yml.get("resource_id") or ""
        if rid and rid in existing:
            plan.append((slug, f"UPDATE Id={existing[rid][1]} {rid}", (row, existing[rid][1], yml_path, yml, False)))
        elif (row["title"], row["authors"]) in by_title:
            rid2, bid2 = by_title[(row["title"], row["authors"])][0]
            plan.append((slug, f"UPDATE Id={bid2} {rid2} (matched by title)", (row, bid2, yml_path, yml, True)))
        else:
            plan.append((slug, "INSERT new row", (row, None, yml_path, yml, False)))

    for slug, action, _ in plan:
        print(f"{slug}: {action}")
    for rid in args.delete_resource:
        print(f"DELETE ResourceId={rid}")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = os.path.join(BACKUP_DIR, f"PersonalBookManager-{stamp}.db")
    con.commit()
    con.close()
    shutil.copy2(PB_DB, backup)
    print(f"backup: {backup}")

    con = sqlite3.connect(PB_DB, timeout=30)
    cur = con.cursor()
    wrote = []  # (slug, Id, want_title, want_cover_len, want_type)
    for slug, action, item in plan:
        if item is None:
            continue
        row, bid, yml_path, yml, backfill_rid = item
        if bid is None:
            new_rid = "PBB:" + uuid.uuid4().hex
            cur.execute(
                "INSERT INTO Books (ResourceId,SourceFilePaths,Title,Authors,"
                "Description,Language,Copyright,ResourceType,LastCompiled,"
                "ModifiedDate,SyncRevision,SyncState,IsDeleted)"
                " VALUES (?,?,?,?,?,?,?,?,NULL,?,NULL,0,0)",
                (new_rid, row["src"], row["title"], row["authors"],
                 row["description"], row["language"], row["copyright"],
                 row["resource_type"], row["now"]),
            )
            bid = cur.lastrowid
            backfill_yml(yml_path, new_rid, bid)
            print(f"{slug}: INSERTED Id={bid} {new_rid} (book.yml backfilled)")
        else:
            cur.execute(
                "UPDATE Books SET SourceFilePaths=?,Title=?,Authors=?,"
                "Description=?,Language=?,Copyright=?,ResourceType=?,"
                "CoverImage=?,ModifiedDate=? WHERE Id=?",
                (row["src"], row["title"], row["authors"],
                 row["description"], row["language"], row["copyright"],
                 row["resource_type"], row["cover"], row["now"], bid),
            )
            if backfill_rid or not yml.get("resource_id"):
                rid = cur.execute(
                    "SELECT ResourceId FROM Books WHERE Id=?", (bid,)
                ).fetchone()[0]
                backfill_yml(yml_path, rid, bid)
            print(f"{slug}: UPDATED Id={bid}")
        wrote.append((slug, bid, row["title"],
                      len(row["cover"]) if row["cover"] else None,
                      row["resource_type"]))
    for rid in args.delete_resource:
        cur.execute("DELETE FROM Books WHERE ResourceId=?", (rid,))
        print(f"DELETED {rid} (rows: {cur.rowcount})")
    con.commit()
    # Verify pass: read back every synced row (covers once wrote NULL
    # transiently on 2026-09-17; never ship an unverified write).
    errors = 0
    for slug, bid, want_title, want_cover, want_type in wrote:
        got = cur.execute(
            "SELECT Title,length(CoverImage),ResourceType FROM Books WHERE Id=?",
            (bid,),
        ).fetchone()
        if got is None or got[0] != want_title or got[1] != want_cover \
                or got[2] != want_type:
            print(f"VERIFY FAIL {slug} Id={bid}: got {got!r}")
            errors += 1
    con.close()
    if errors:
        fail(f"{errors} row(s) failed verification — restore from {backup}")
    print("verify: all synced rows read back OK.")
    print("done. Reopen Logos and click Build book per book.")


if __name__ == "__main__":
    main()
