#!/usr/bin/env python3
"""Select Ante-Nicene PBB and click Build book (Air Logos)."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import time
from pathlib import Path

OUT = Path("/Users/sj/SaneApps/clients/translations/books/ante-nicene-topics/outputs/logos-e2e-20260910-v050")
OUT.mkdir(parents=True, exist_ok=True)
DB = Path.home() / "Library/Application Support/Logos4/Documents/adcocvnb.nzw/PersonalBooks/PersonalBookManager.db"


def sh(*args: str) -> None:
    subprocess.run(args, check=False)


def pid_logos() -> str:
    r = subprocess.run(
        ["pgrep", "-f", "/Applications/Logos.app/Contents/MacOS/Logos"],
        capture_output=True,
        text=True,
    )
    return (r.stdout or "").strip().split("\n")[0]


def last_compiled() -> str:
    con = sqlite3.connect(DB)
    row = con.execute("SELECT LastCompiled FROM Books WHERE Id=4").fetchone()
    con.close()
    return row[0]


def peekaboo_see(pid: str, path: Path) -> list[dict]:
    err = path.with_suffix(".err")
    subprocess.run(
        ["peekaboo", "see", "--pid", pid, "--json"],
        stdout=path.open("w"),
        stderr=err.open("w"),
        check=False,
    )
    if not path.exists() or path.stat().st_size < 20:
        return []
    d = json.loads(path.read_text())
    return d.get("data", {}).get("ui_elements", []) or d.get("ui_elements", []) or []


def center(b: dict) -> str:
    x = int(b["x"] + b["width"] / 2)
    y = int(b["y"] + b["height"] / 2)
    return f"{x},{y}"


def find_xy(elems: list[dict], *needles: str) -> str | None:
    for e in elems:
        lab = (e.get("label") or "").lower()
        b = e.get("bounds") or {}
        if not b:
            continue
        if all(n in lab for n in needles):
            return center(b)
    return None


def find_build(elems: list[dict]) -> str | None:
    """Prefer exact Build book; never match status text / Add book / Upload."""
    skip = ("succeed", "error", "warning", "add", "upload")
    for e in elems:
        lab = (e.get("label") or "").strip().lower()
        b = e.get("bounds") or {}
        if not b:
            continue
        if lab in ("build book", "build"):
            return center(b)
    for e in elems:
        lab = (e.get("label") or "").strip().lower()
        b = e.get("bounds") or {}
        if not b:
            continue
        if lab.startswith("build") and not any(s in lab for s in skip):
            return center(b)
    return None


def main() -> int:
    before = last_compiled()
    print("before", before)
    pid = pid_logos()
    print("pid", pid)
    sh("osascript", "-e", 'tell application "Logos" to activate')
    time.sleep(0.5)
    # Tools menu often fails on Air; URL deep-link is enough.
    sh("open", "logos4:PersonalBooks")
    time.sleep(2.5)

    elems = peekaboo_see(pid, OUT / "see.json")
    finished = find_xy(elems, "finished")
    if finished:
        print("dismiss_finished", finished)
        sh("/opt/homebrew/bin/cliclick", f"c:{finished}")
        time.sleep(0.5)
        elems = peekaboo_see(pid, OUT / "see.json")

    ante = find_xy(elems, "ante-nicene", "dogmatics") or find_xy(elems, "ante-nicene")
    print("ante", ante)
    if not ante:
        print("NO_ANTE_ROW")
        sh("screencapture", "-x", str(OUT / "no-ante.png"))
        return 1
    sh("/opt/homebrew/bin/cliclick", f"c:{ante}")
    time.sleep(1.2)

    elems = peekaboo_see(pid, OUT / "see2.json")
    build = find_build(elems)
    print("build", build)
    if not build:
        print("NO_BUILD_BUTTON")
        for e in elems:
            lab = e.get("label") or ""
            if lab:
                print("LAB", repr(lab)[:80])
        sh("screencapture", "-x", str(OUT / "no-build.png"))
        return 1
    # Build is lower-right; refuse list-row / status clicks
    by = int(build.split(",")[1])
    if by < 400:
        print("BUILD_XY_TOO_HIGH", build, "— refusing (likely wrong control)")
        sh("screencapture", "-x", str(OUT / "bad-build-xy.png"))
        return 1
    sh("/opt/homebrew/bin/cliclick", f"c:{build}")

    ok = False
    for i in range(1, 36):
        time.sleep(2)
        now = last_compiled()
        print(f"wait {i} {now}")
        if now != before:
            ok = True
            break
    sh("screencapture", "-x", str(OUT / "final.png"))
    print("after", last_compiled(), "ok", ok)

    con = sqlite3.connect(DB)
    polluted = con.execute(
        "SELECT ArticleId, Context FROM ArticleCache WHERE BookId=4 AND "
        "(Context LIKE '%Confidence%' OR Context LIKE '%source_verified%' OR "
        "Context LIKE '%anf_mediated%' OR Context LIKE '%GTG%')"
    ).fetchall()
    print("polluted", len(polluted), polluted[:3])
    con.close()
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
