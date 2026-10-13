#!/usr/bin/env python3
"""Fetch an original-language text that the library does not hold yet, for the
Timeline question dossiers (owner 2026-10-13: "as long as you can read the
original language I do not care the source").

Every file lands in outputs/question-dossiers/witnesses/ as plain text with a
first line naming where it came from, and corpus_search.py --raw searches it.

  python3 scripts/witness_fetch.py khaz "Gregory of Nyssa_PG 44-46" "Oratio catechetica magna"
  python3 scripts/witness_fetch.py khaz "Gregory of Nyssa_PG 44-46"          # list the folder
  python3 scripts/witness_fetch.py ia origenous-ta-heuriskomena-panta-t.-9-1839
  python3 scripts/witness_fetch.py url https://la.wikisource.org/wiki/... name

The text is a witness to read, not a lock: a dossier quote names the printed
edition, and a book still needs its own source intake before translation.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "question-dossiers" / "witnesses"
KHAZ = "http://khazarzar.skeptik.net/pgm/PG_Migne"
UA = {"User-Agent": "Mozilla/5.0 (ViaPatrum source research)"}


def get(url: str, timeout: int = 300) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()[:90]


def save(name: str, origin: str, text: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{slug(name)}.txt"
    p.write_text(f"SOURCE: {origin}\n\n{text}", encoding="utf-8")
    print(f"{p.relative_to(ROOT)}  ({len(text):,} chars)")
    return p


def khaz(folder: str, work: str | None) -> int:
    base = f"{KHAZ}/{urllib.parse.quote(folder)}/"
    if not work:
        page = get(base).decode("utf-8", "replace")
        for h in re.findall(r'href="([^"?/][^"]*)"', page):
            print(urllib.parse.unquote(html.unescape(h)))
        return 0
    name = work if work.endswith(".pdf") else work + ".pdf"
    pdf = get(base + urllib.parse.quote(name))
    tmp = OUT / "_tmp.pdf"
    OUT.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(pdf)
    text = subprocess.run(["pdftotext", "-layout", str(tmp), "-"], capture_output=True, text=True).stdout
    tmp.unlink()
    save(f"khaz {folder} {work}", base + name, text)
    return 0


def ia(ident: str) -> int:
    meta = json.loads(get(f"https://archive.org/metadata/{ident}/files", 60))
    names = [f["name"] for f in meta.get("result", []) if f["name"].endswith("_djvu.txt")]
    if not names:
        print(f"{ident}: no OCR text file")
        return 1
    url = f"https://archive.org/download/{ident}/{urllib.parse.quote(names[0])}"
    save(f"ia {ident}", url, get(url, 600).decode("utf-8", "replace"))
    return 0


def url(u: str, name: str) -> int:
    raw = get(u).decode("utf-8", "replace")
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    save(f"url {name}", u, re.sub(r"[ \t]+", " ", text))
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    kind = sys.argv[1]
    if kind == "khaz":
        return khaz(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    if kind == "ia":
        return ia(sys.argv[2])
    if kind == "url":
        return url(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else urllib.parse.urlparse(sys.argv[2]).path)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
