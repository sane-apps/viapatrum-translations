#!/usr/bin/env python3
"""Build the corpus catalog: every book in books/, oldest first.

Reads books/*/book.yml plus the fathers site's author dates (with
docs/author-dates-backfill.json filling gaps) and the site's live/held sets.

Writes docs/CORPUS_CATALOG.md (human pick-from list) and
docs/corpus-catalog.json (machine-readable rows).

English-lineage flags are HEURISTIC, derived from book.yml notes/scope text:
  refresh         prior English used as base (densify lane, NOT OET, prior PD)
  prior-exists    prior English exists and was deliberately not copied (new rendering)
  first-english   notes explicitly claim no usable prior/PD English
  unstated        no signal in notes -- needs triage, do not assume
Correct lineage by editing the book's notes, then re-run this script.
"""
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books"
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
sys.path.insert(0, str(SITE / "scripts"))
try:
    import build_site as site
except ImportError as exc:
    sys.exit("fathers site repo not found at %s: %s" % (SITE, exc))

import yaml

BACKFILL = json.loads((ROOT / "docs/author-dates-backfill.json").read_text())


def ccel_by_repo_author():
    """repo author -> sorted CCEL volumes (cited prior English)."""
    ccel_path = ROOT / "docs/ccel-english.json"
    map_path = ROOT / "docs/ccel-author-map.json"
    if not (ccel_path.is_file() and map_path.is_file()):
        return {}
    ccel = json.loads(ccel_path.read_text())
    amap = json.loads(map_path.read_text())
    out = {}
    for key, entry in amap.items():
        if key.startswith("_") or not isinstance(entry, dict):
            continue
        repo_author = entry.get("repo_author")
        if not repo_author:
            continue
        if key in ccel.get("authors", {}):
            vols = sorted({v for e in ccel["authors"][key]["works"].values()
                           for v in e["volumes"]})
        else:
            vols = sorted(entry.get("ccel_volumes", []))
        out.setdefault(repo_author, set()).update(vols)
    return {a: sorted(v) for a, v in out.items()}

COMPLETE = {"series-closeout", "series-closed", "done", "verified"}

REFRESH_RES = [
    re.compile(r"\bnot OET\b", re.I),
    re.compile(r"prior PD", re.I),
    re.compile(r"densify-lane\s*[-\u2014]", re.I),
    re.compile(r"PD English tradition", re.I),
    re.compile(r"from [^.]{0,60} PD English", re.I),
]
PRIOR_NAMES = ("ANF|NPNF|FOTC|ACW|\\bSC\\b|Crombie|Chadwick|Butterworth|Heine|Scheck|"
               "Barkley|Bruce|O.Meara|Greer|Hill|Lewis|Trigg|Pusey|Greystone|Lunn|"
               "Robinson|Wilson|Allport|McCrindle|Freese|Durand|Migne")
PRIOR_RES = [
    re.compile(r"(no|without|never|n't|not|\u2260)\s+[^.\n]{0,50}(%s)" % PRIOR_NAMES, re.I),
    re.compile(r"\bskip(ped)?\b[^.\n]{0,40}(%s)" % PRIOR_NAMES, re.I),
]
FIRST_STRONG_RES = [
    re.compile(r"no (usable |public-domain |pd )*english", re.I),
    re.compile(r"never (been )?translated", re.I),
    re.compile(r"\buntranslated\b", re.I),
    re.compile(r"no prior english", re.I),
]
FIRST_WEAK_RES = [
    re.compile(r"first english", re.I),
]


def lineage(text):
    t = text or ""
    if any(r.search(t) for r in REFRESH_RES):
        return "refresh"
    if any(r.search(t) for r in FIRST_STRONG_RES):
        return "first-english"
    if any(r.search(t) for r in PRIOR_RES):
        return "prior-exists"
    if any(r.search(t) for r in FIRST_WEAK_RES):
        return "first-english"
    return "unstated"


# Site slugs whose book dir is not recoverable from review packets
# (provisional-legacy works). site slug -> books/<dir>.
SITE_SLUG_OVERRIDES = {
    "origen-song-homily-1": "origen-song",
    "origen-song-homily-2": "origen-song",
    "origen-homilies-jeremiah": "origen-jeremiah-samuel",
    "origen-homily-1samuel-28": "origen-jeremiah-samuel",
    "origen-lamentations-fragments": "origen-jeremiah-samuel",
    "origen-on-pascha": "origen-heraclides-pascha",
    "julian-collective-letter": "julian-of-eclanum",
    "julian-letter-to-rome": "julian-of-eclanum",
    "julian-marriage-extracts": "julian-of-eclanum",
    "julian-turbantius-fragments": "julian-of-eclanum",
}


def site_slug_to_book(site_slug, packet_map):
    if site_slug in packet_map:
        return packet_map[site_slug]
    if site_slug in SITE_SLUG_OVERRIDES:
        return SITE_SLUG_OVERRIDES[site_slug]
    if site_slug.startswith("cyril-adoration-"):
        return "cyril-alexandria-adoration-1"
    return site_slug  # default: book dir matches site slug


def author_year(name):
    """(year, period_display, source). Year 9999 = undated."""
    try:
        y = site.author_sort_year(name)
    except Exception:
        y = 9999
    if y != 9999:
        return y, site.author_dates_raw(name, None) or "", "site"
    entry = BACKFILL.get(name)
    if isinstance(entry, str):
        period, note = entry, ""
    else:
        period, note = (entry or {}).get("period"), (entry or {}).get("note", "")
    if period:
        y = site.year_from_period(period, bound="end")
        if y is not None:
            return y, period, "backfill"
    return 9999, note or "undated", "missing"


def book_site_status():
    """Map books/<dir> -> (status, [site slugs]). Status: live > held > absent."""
    works = SITE / "dist/works"
    live = {p.name for p in works.iterdir() if p.is_dir()} if works.is_dir() else set()
    held = set()
    cq = SITE / "outputs/catalogue-quality.json"
    if cq.is_file():
        try:
            held = {h["slug"] for h in json.loads(cq.read_text()).get("held_works", [])}
        except (ValueError, KeyError):
            pass
    packet_map = {}
    conflicts = []
    manifest = SITE / "data/publication-review.json"
    if manifest.is_file():
        try:
            m = json.loads(manifest.read_text())
            for key, rev in (m.get("reviews") or {}).items():
                parts = key.split(":")
                if len(parts) == 3 and parts[0] == "work":
                    book = (rev.get("packet") or "").split("/")[1:2]
                    if book:
                        packet_map.setdefault(parts[1], book[0])
            for slug, rev in (m.get("scope_reviews") or {}).items():
                book = ((rev or {}).get("packet") or "").split("/")[1:2]
                if book:
                    if slug in packet_map and packet_map[slug] != book[0]:
                        conflicts.append((slug, packet_map[slug], book[0]))
                    packet_map.setdefault(slug, book[0])
        except ValueError:
            pass
    per_book = {}
    for slug in live:
        book = site_slug_to_book(slug, packet_map)
        st, slugs = per_book.get(book, ("absent", []))
        per_book[book] = ("live", slugs + [slug])
    for slug in held:
        book = site_slug_to_book(slug, packet_map)
        st, slugs = per_book.get(book, ("absent", []))
        if st != "live":
            per_book[book] = ("held", slugs + [slug])
    return per_book, len(live), len(held), conflicts


def cell(value, width):
    s = re.sub(r"\s+", " ", str(value or "")).strip().replace("|", "/")
    return (s[:width - 1] + "\u2026") if len(s) > width else s


def main():
    per_book, n_live, n_held, conflicts = book_site_status()
    ccel_map = ccel_by_repo_author()
    rows = []
    for path in sorted(BOOKS.iterdir()):
        meta_path = path / "book.yml"
        if not meta_path.is_file():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        slug = str(meta.get("slug") or path.name)
        author = str(meta.get("author") or "Unknown")
        year, period, date_src = author_year(author)
        notes = " ".join(str(meta.get(k) or "") for k in ("notes", "scope", "notes_oet"))
        status = str(meta.get("status") or "unknown")
        site_st, site_slugs = per_book.get(path.name, ("absent", []))
        # also try the slug field (usually identical to the dir name)
        if site_st == "absent" and slug != path.name:
            site_st, site_slugs = per_book.get(slug, ("absent", []))
        rows.append({
            "slug": slug,
            "title": str(meta.get("title") or slug),
            "author": author,
            "year": year,
            "period": period,
            "date_src": date_src,
            "status": status,
            "complete": status in COMPLETE,
            "lineage": lineage(notes),
            "ccel": ccel_map.get(author, []),
            "site": site_st,
            "site_works": sorted(site_slugs),
            "logos": meta.get("logos_book_id") or "",
            "edition": str(meta.get("edition") or meta.get("edition_lock") or ""),
            "missing": [k for k in ("scope", "notes") if not meta.get(k)] + (
                [] if (meta.get("edition") or meta.get("edition_lock")) else ["edition"]),
        })
    rows.sort(key=lambda r: (r["year"], r["author"].lower(), r["title"].lower()))

    status_ct = Counter(r["status"] for r in rows)
    lineage_ct = Counter(r["lineage"] for r in rows)
    site_ct = Counter(r["site"] for r in rows)
    undated = sorted({r["author"] for r in rows if r["date_src"] == "missing"})
    unlisted_edition = [r["slug"] for r in rows if "edition" in r["missing"]]
    unstated = [r for r in rows if r["lineage"] == "unstated"]
    closeout_absent = [r for r in rows if r["complete"] and r["site"] == "absent"]
    next_up = [r for r in rows if not r["complete"]][:25]
    oldest_unstarted = [r for r in rows
                        if not r["complete"] and r["lineage"] in ("first-english", "unstated")][:10]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n_complete = sum(1 for r in rows if r["complete"])

    md = []
    md.append("# Corpus Catalog\n")
    md.append("Generated " + now + " by scripts/build_corpus_catalog.py -- re-run after any "
              "book.yml change. Do not hand-edit rows; fix the book.yml (or "
              "docs/author-dates-backfill.json) and regenerate.\n")
    md.append("## Progress\n")
    md.append("%d works tracked. %d translation-complete, %d in progress. "
              "Site: %d live, %d held, %d absent. Logos books attached: %d.\n"
              % (len(rows), n_complete, len(rows) - n_complete,
                 site_ct.get("live", 0), site_ct.get("held", 0), site_ct.get("absent", 0),
                 sum(1 for r in rows if r["logos"])))
    md.append("| Translation status | Works |")
    md.append("|---|---|")
    for k, v in status_ct.most_common():
        md.append("| %s | %d |" % (k, v))
    md.append("\n| English lineage (heuristic) | Works |")
    md.append("|---|---|")
    for k, v in lineage_ct.most_common():
        md.append("| %s | %d |" % (k, v))
    md.append("\n## Next up (oldest unfinished, joiners start here)\n")
    md.append("Oldest first per the charter. Claim a slice with "
              "`python3 scripts/claims.py start --agent YourName` (see `docs/START_HERE.md`).\n")
    md.append("| Year | Author | Work | Slug | Status | Lineage |")
    md.append("|---|---|---|---|---|---|")
    for r in next_up:
        y = "?" if r["year"] == 9999 else r["year"]
        md.append("| %s | %s | %s | `%s` | %s | %s |"
                  % (y, cell(r["author"], 32), cell(r["title"], 60),
                     r["slug"], r["status"], r["lineage"]))
    md.append("\n## Oldest works still without finished new English\n")
    for r in oldest_unstarted:
        y = "?" if r["year"] == 9999 else r["year"]
        md.append("- %s -- %s, *%s* (`%s`, %s, %s)"
                  % (y, r["author"], cell(r["title"], 70),
                     r["slug"], r["status"], r["lineage"]))
    md.append("\n## Full catalog (oldest first)\n")
    md.append("| # | Year | Author | Work | Slug | Transl | Lineage | CCEL | Site | Logos | Edition |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        y = "?" if r["year"] == 9999 else r["year"]
        t = "done" if r["complete"] else r["status"]
        s = r["site"] + ("(%d)" % len(r["site_works"]) if len(r["site_works"]) > 1 else "")
        c = ",".join(r["ccel"]) if r["ccel"] else "-"
        md.append("| %d | %s | %s | %s | `%s` | %s | %s | %s | %s | %s | %s |"
                  % (i, y, cell(r["author"], 28), cell(r["title"], 52), r["slug"],
                     t, r["lineage"], c, s, r["logos"], cell(r["edition"], 44)))
    md.append("\n## Data gaps\n")
    md.append("- Undated authors (%d): %s" % (len(undated), ", ".join(undated) if undated else "none"))
    if unlisted_edition:
        shown = ", ".join("`%s`" % s for s in unlisted_edition[:20])
        if len(unlisted_edition) > 20:
            shown += " ..."
        md.append("- Works missing edition lock (%d): %s" % (len(unlisted_edition), shown))
    else:
        md.append("- Works missing edition lock (0): none")
    md.append("- Works with unstated English lineage: %d (triage notes to shrink this)"
              % len(unstated))
    md.append("- Translation-complete but absent from site: %d (publishing backlog)"
              % len(closeout_absent))
    md.append("")
    (ROOT / "docs/CORPUS_CATALOG.md").write_text("\n".join(md), encoding="utf-8")
    (ROOT / "docs/corpus-catalog.json").write_text(
        json.dumps({"generated": now, "rows": rows}, indent=1), encoding="utf-8")
    print("works=%d complete=%d site_works_live=%d site_works_held=%d "
          "books_live=%d books_held=%d lineage=%s undated_authors=%d"
          % (len(rows), n_complete, n_live, n_held, site_ct.get("live", 0),
             site_ct.get("held", 0), dict(lineage_ct), len(undated)))
    for slug, a, b in conflicts:
        print("PACKET-CONFLICT %s reviews=%s scope=%s" % (slug, a, b))


if __name__ == "__main__":
    main()
