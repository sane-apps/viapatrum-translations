#!/usr/bin/env python3
"""Delete Logos FN Test Pandoc Footnotes personal book (Air)."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import time
from pathlib import Path

DB = Path.home() / "Library/Application Support/Logos4/Documents/adcocvnb.nzw/PersonalBooks/PersonalBookManager.db"
SEE = Path("/tmp/fn_cleanup_see.json")


def sh(*args: str) -> None:
    subprocess.run(args, check=False)


def pid() -> str:
    return subprocess.check_output(
        ["pgrep", "-f", "/Applications/Logos.app/Contents/MacOS/Logos"], text=True
    ).strip().split("\n")[0]


def see(p: str) -> list[dict]:
    subprocess.run(
        ["peekaboo", "see", "--pid", p, "--json"],
        stdout=SEE.open("w"),
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return json.loads(SEE.read_text()).get("data", {}).get("ui_elements", []) or []


def center(b: dict) -> str:
    return f"{int(b['x']+b['width']/2)},{int(b['y']+b['height']/2)}"


def main() -> int:
    before = sqlite3.connect(DB).execute("SELECT Id, Title FROM Books").fetchall()
    print("before", before)
    sh("osascript", "-e", 'tell application "Logos" to activate')
    time.sleep(0.4)
    sh("open", "logos4:PersonalBooks")
    time.sleep(2.2)
    p = pid()
    elems = see(p)
    fn = None
    for e in elems:
        lab = e.get("label") or ""
        b = e.get("bounds") or {}
        if "FN Test" in lab and b:
            fn = center(b)
            print("select", lab, fn)
            break
    if not fn:
        print("NO_FN_ROW")
        for e in elems:
            lab = e.get("label") or ""
            if lab and ("Test" in lab or "FN" in lab or "Foot" in lab):
                print("LAB", repr(lab)[:100])
        return 2
    sh("/opt/homebrew/bin/cliclick", f"c:{fn}")
    time.sleep(0.8)
    elems = see(p)
    delete = None
    for e in elems:
        lab = (e.get("label") or "").strip().lower()
        b = e.get("bounds") or {}
        if not b:
            continue
        if lab in ("delete", "delete book", "remove") or lab.startswith("delete"):
            delete = center(b)
            print("delete", lab, delete)
            break
    if delete:
        sh("/opt/homebrew/bin/cliclick", f"c:{delete}")
        time.sleep(0.8)
        elems = see(p)
        for e in elems:
            lab = (e.get("label") or "").strip().lower()
            b = e.get("bounds") or {}
            if lab in ("delete", "ok", "yes", "remove") and b:
                print("confirm", lab, center(b))
                sh("/opt/homebrew/bin/cliclick", f"c:{center(b)}")
                break
    else:
        print("NO_DELETE_BTN — trying keyboard Delete")
        sh(
            "osascript",
            "-e",
            'tell application "System Events" to tell process "Logos" to key code 51',
        )
    time.sleep(1.2)
    after = sqlite3.connect(DB).execute("SELECT Id, Title FROM Books").fetchall()
    print("after", after)
    doc = Path("/tmp/fn-test.docx")
    if doc.exists():
        sh("trash", str(doc))
        print("trashed", doc)
    still = [r for r in after if r[0] == 5 or (r[1] and "FN Test" in r[1])]
    print("still_fn", still)
    return 0 if not still else 3


if __name__ == "__main__":
    raise SystemExit(main())
