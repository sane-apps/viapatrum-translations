#!/usr/bin/env python3
"""Research SOP gate: every published book's intro must be sourced.

Rules (see CONTRIBUTING.md "Research SOP"):
  1. Every book with a DOCX has intro.md (exactly 3 paragraphs:
     author / context / contents) AND research.json.
  2. research.json: matching slug, checked date, >=1 claim; every
     claim has kind + text + sources; kind=fact requires >=1
     http(s) source (kind=scope/repo may cite repo: paths).
  3. Every 3-4 digit year in intro.md appears in the book's claims,
     its book.yml, or author-dates.json (no unsourced dates).
  4. The intro's author-date line matches author-dates.json for that
     author (the two never drift). Multi-author volumes listed in
     SKIP_AUTHORS are exempt from rule 4 only.

Exit 0 when clean, 1 with messages otherwise. Wired into
websites/fathers.saneapps.com scripts/ship.sh and the Logos
driver preflight, so neither output ships unsourced words.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from pb_sync import load_yml  # noqa: E402

SITE_DATES = os.path.expanduser(
    "~/SaneApps/websites/fathers.saneapps.com/data/author-dates.json")
SKIP_AUTHORS = {"ante-nicene-topics"}  # multi-author volumes
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def norm_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def years(text: str) -> list[str]:
    return re.findall(r"\d{3,4}", text.replace(",", ""))


def docx_books() -> dict[str, dict]:
    books = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "books", "*", "book.yml"))):
        slug = os.path.basename(os.path.dirname(path))
        yml = load_yml(path)
        docx = yml.get("docx") or ""
        full = os.path.join(ROOT, "books", slug, docx)
        if docx and os.path.exists(full):
            books[slug] = yml
    return books


def check_intro(slug: str) -> str:
    path = os.path.join(ROOT, "books", slug, "intro.md")
    if not os.path.exists(path):
        err("%s: missing intro.md" % slug)
        return ""
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) != 3:
        err("%s: intro.md has %d paragraphs, want 3 "
            "(author/context/contents)" % (slug, len(paras)))
    return text


def check_research(slug: str) -> dict:
    path = os.path.join(ROOT, "books", slug, "research.json")
    if not os.path.exists(path):
        err("%s: missing research.json" % slug)
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as exc:
        err("%s: research.json is not valid JSON (%s)" % (slug, exc))
        return {}
    if data.get("slug") != slug:
        err("%s: research.json slug mismatch" % slug)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("checked") or "")):
        err("%s: research.json needs a checked YYYY-MM-DD date" % slug)
    claims = data.get("claims")
    if not claims:
        err("%s: research.json has no claims" % slug)
        return data
    for i, claim in enumerate(claims):
        where = "%s: claim %d" % (slug, i)
        kind = claim.get("kind")
        if kind not in ("fact", "scope", "repo"):
            err("%s: bad kind %r" % (where, kind))
        if not (claim.get("claim") or "").strip():
            err("%s: empty claim text" % where)
        sources = claim.get("sources") or []
        if not sources:
            err("%s: no sources" % where)
        for src in sources:
            if not (src.startswith("http://") or src.startswith("https://")
                    or src.startswith("repo:")):
                err("%s: bad source %r" % (where, src))
        if kind == "fact" and not any(
                s.startswith("http") for s in sources):
            err("%s: kind=fact needs an http(s) source" % where)
    return data


def check_years(slug: str, intro: str, data: dict, yml: dict,
                dates: dict) -> None:
    if not intro or not data:
        return
    allowed = " ".join(
        [c.get("claim", "") for c in data.get("claims", [])]
        + [" ".join("%s=%s" % kv for kv in yml.items())]
        + [" ".join("%s=%s" % kv for kv in dates.items())])
    for year in years(intro):
        if year not in years(allowed) and year not in allowed:
            err("%s: intro year %s has no basis in research.json, "
                "book.yml, or author-dates.json" % (slug, year))


def check_author_dates(slug: str, intro: str, yml: dict,
                       dates: dict) -> None:
    if slug in SKIP_AUTHORS or not intro:
        return
    if not dates:
        err("%s: author-dates.json unreadable, cannot cross-check" % slug)
        return
    author = yml.get("author") or ""
    want = norm_key(author)
    hit = None
    for key, val in dates.items():
        if norm_key(key) == want or norm_key(key).startswith(want) \
                or want.startswith(norm_key(key)):
            hit = val
            break
    if hit is None:
        err("%s: author %r has no author-dates.json entry" % (slug, author))
        return
    if not years(str(hit)):
        return  # vague entry (e.g. "fl. 4th/5th c.") cannot contradict
    first_para = re.split(r"\n\s*\n", intro.strip())[0]
    life = None
    for grp in re.findall(r"\([^()]*\)", first_para):
        if years(grp):
            life = grp
            break
    if life is None:
        err("%s: intro para 1 has no author-date line" % slug)
        return
    for year in years(life):
        if year not in years(str(hit)):
            err("%s: intro author year %s disagrees with "
                "author-dates.json (%s)" % (slug, year, hit))


def main() -> int:
    try:
        with open(SITE_DATES, encoding="utf-8") as f:
            dates = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dates = {}
    books = docx_books()
    if not books:
        err("no DOCX books found")
    for slug, yml in sorted(books.items()):
        intro = check_intro(slug)
        data = check_research(slug)
        check_years(slug, intro, data, yml, dates)
        check_author_dates(slug, intro, yml, dates)
    if ERRORS:
        print("research gate FAILED (%d books checked):" % len(books))
        for msg in ERRORS:
            print("  -", msg)
        return 1
    print("research gate OK (%d books, intros sourced + dates agree)"
          % len(books))
    return 0


if __name__ == "__main__":
    sys.exit(main())
