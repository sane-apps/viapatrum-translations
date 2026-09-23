#!/usr/bin/env python3
"""Overnight publish epilogue: ship only when tonight's run promoted claims.

1. Read newest outputs/overnight-quota/*-dual.json.
2. If zero ok claims: print SKIP, exit 0.
3. For each promoted claim's book: rebuild the Logos source docx
   (build_pbb_docx.py --book slug --out books/slug/<docx from book.yml>).
4. Run websites/fathers.saneapps.com/scripts/ship.sh (its own gates decide;
   gate failure = no deploy, old site stays).

Always exits 0: publish trouble must not trip the burn fuse. The 10am
digest reports what shipped or why not.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"


def latest_summary() -> dict:
    files = sorted(glob.glob(str(ROOT / "outputs/overnight-quota/*-dual.json")))
    if not files:
        return {}
    return json.loads(Path(files[-1]).read_text(encoding="utf-8"))


def book_for_claim(claim_id: str) -> str | None:
    from book_adapter import get_adapter  # noqa: E402
    for slug in ("origen-jeremiah-samuel", "cyril-alexandria-isaiah"):
        try:
            adapter = get_adapter(slug)
        except SystemExit:
            continue
        if re.fullmatch(adapter.claim_re, claim_id):
            return slug
    return None


def docx_name(slug: str) -> str | None:
    yml = ROOT / "books" / slug / "book.yml"
    if not yml.is_file():
        return None
    m = re.search(r"^docx:\s*(\S+)", yml.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip("\"'") if m else None


def main() -> int:
    summary = latest_summary()
    ok_claims = [c["claim"] for lanes in [summary.get("lanes") or {}]
                 for lane in lanes.values() for c in (lane.get("claims") or [])
                 if c.get("ok") and c.get("claim")]
    if not ok_claims:
        print("[publish] SKIP: no promoted claims tonight", flush=True)
        return 0
    print(f"[publish] {len(ok_claims)} promoted: {ok_claims}", flush=True)
    slugs = sorted({s for c in ok_claims if (s := book_for_claim(c))})
    for slug in slugs:
        name = docx_name(slug)
        if not name:
            print(f"[publish] {slug}: no docx in book.yml; skip docx", flush=True)
            continue
        out = ROOT / "books" / slug / name
        cmd = [sys.executable, "scripts/build_pbb_docx.py",
               "--book", slug, "--out", str(out)]
        print(f"[publish] + {' '.join(cmd)}", flush=True)
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                  timeout=1200)
        except subprocess.TimeoutExpired:
            print(f"[publish] {slug}: docx TIMEOUT; continue to site", flush=True)
            continue
        tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
        print(f"[publish] {slug}: docx rc={proc.returncode}\n{tail}", flush=True)
    ship = SITE / "scripts/ship.sh"
    if not ship.is_file():
        print("[publish] ship.sh missing; site not shipped", flush=True)
        return 0
    print("[publish] + scripts/ship.sh", flush=True)
    try:
        proc = subprocess.run([str(ship)], cwd=SITE, capture_output=True,
                              text=True, timeout=1800,
                              env={**os.environ, "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + os.environ.get("PATH", "")})
    except subprocess.TimeoutExpired:
        print("[publish] ship.sh TIMEOUT; site unchanged", flush=True)
        return 0
    tail = ((proc.stdout or "") + (proc.stderr or ""))[-1500:]
    print(f"[publish] ship.sh rc={proc.returncode}\n{tail}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
