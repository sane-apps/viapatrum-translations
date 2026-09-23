#!/usr/bin/env python3
"""Backfill book.yml edition: keys from identity.json / descriptions.

The corpus catalog (docs/corpus-catalog.json + CORPUS_CATALOG.md) reads
book.yml edition:/edition_lock: via scripts/build_corpus_catalog.py.
33 rows lack it; the data already exists in reviews/audit/identity.json
or the book.yml description ("prepared ... from ...").

Usage:
  python3 scripts/backfill_editions.py            # dry run, print proposals
  python3 scripts/backfill_editions.py --apply    # write book.yml keys
Then: python3 scripts/build_corpus_catalog.py
"""

import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATTERNS = [
    # from the Latin text of the Vossius 1684 edition
    (re.compile(r"from the (?:Greek|Latin|Syriac|Coptic|Armenian|Georgian|Ethiopic|Arabic|Slavonic) text of (?:the )?([A-Z][^.]*? edition(?: \([^)]*\))?)"), "desc-edition"),
    # from the Greek GCS Koetschau edition (1899) (no "text of")
    (re.compile(r"from the (?:Greek|Latin) ((?:GCS|CSEL|CCL|SC|TU|Sources Chretiennes)[^.]*? edition(?: \([^)]*\))?)"), "desc-series"),
    # from the GCS edition (Origenes Werke)
    (re.compile(r"from the ((?:GCS|CSEL|CCL|SC|TU) edition \([^)]*\))"), "desc-series-bare"),
    # from the locked Pusey 1877 Greek
    (re.compile(r"from the locked ([A-Z][a-z]+ \d{4})"), "desc-locked"),
    # from the Greek text (Migne PG 41)
    (re.compile(r"from the (?:Greek|Latin) text \(([^)]*(?:Migne|PG|PL|GCS|CSEL|CCL|SC|TU|BHG|CPG)[^)]*)\)"), "desc-paren"),
    # from the Greek text of Migne, Patrologia Graeca 34
    (re.compile(r"from the (?:Greek|Latin) text of ((?:Migne|Patrologia)[^.]*?\d[^.]*)"), "desc-migne"),
    # from the Greek text of Routh's Reliquiae Sacrae
    (re.compile(r"from the (?:Greek|Latin) text of ([^.]*?(?:Sacrae|Reliquiae|Corpus|Thesaurus)[^.]*)"), "desc-collection"),
    # from the Latin text (Cambridge: Roger Daniel, 1650)
    (re.compile(r"from the (?:Greek|Latin|English) text \(([^)]*\d{4}[^)]*)\)"), "desc-pub"),
    # checked against Migne, PG 86 ...
    (re.compile(r"\(checked against ([^)]*(?:Migne|PG|PL)[^)]*)\)"), "desc-checked"),
]

# Matches that are derivation notes, not editions -> force manual triage.
WEAK = re.compile(r"concordance|extract|witnesses\b", re.IGNORECASE)

NORMALIZE = {
    "Vossius edition, 1684": "Vossius 1684 edition",
}


def clean(ed):
    ed = ed.strip().rstrip(".")
    return NORMALIZE.get(ed, ed)


def propose(slug):
    bdir = os.path.join(REPO, "books", slug)
    ident = os.path.join(bdir, "reviews", "audit", "identity.json")
    if os.path.exists(ident):
        try:
            ed = (json.load(open(ident, encoding="utf-8")).get("edition") or "").strip()
        except (json.JSONDecodeError, OSError):
            ed = ""
        if ed and not WEAK.search(ed):
            return clean(ed), "identity.json"
    # translations/*_meta.json edition (irenaeus pattern)
    tdir = os.path.join(bdir, "translations")
    if os.path.isdir(tdir):
        for fn in sorted(os.listdir(tdir)):
            if fn.endswith("_meta.json"):
                try:
                    ed = (json.load(open(os.path.join(tdir, fn),
                                         encoding="utf-8")).get("edition") or "").strip()
                except (json.JSONDecodeError, OSError):
                    continue
                if ed and not WEAK.search(ed):
                    return clean(ed), "meta.json:" + fn
    # sources/manifest.json copy_text.edition or sources[0].source
    man = os.path.join(bdir, "sources", "manifest.json")
    if os.path.exists(man):
        try:
            m = json.load(open(man, encoding="utf-8"))
            ed = ((m.get("copy_text") or {}).get("edition") or "").strip()
            if not ed and m.get("sources"):
                ed = (m["sources"][0].get("source") or "").strip().split("\n")[0]
            if ed and not WEAK.search(ed) and len(ed) < 300:
                return clean(ed), "manifest.json"
        except (json.JSONDecodeError, OSError, IndexError, AttributeError):
            pass
    yml_path = os.path.join(bdir, "book.yml")
    if not os.path.exists(yml_path):
        return None, "no-book.yml"
    text = open(yml_path, encoding="utf-8").read()
    m = re.search(r"^description:\s*[\"']?(.*)$", text, re.M)
    desc = m.group(1) if m else ""
    for rx, src in PATTERNS:
        mm = rx.search(desc)
        if mm:
            ed = clean(mm.group(1))
            if WEAK.search(ed):
                return None, "weak-source:" + ed[:60]
            return ed, src
    return None, "manual-triage"


def main():
    apply = "--apply" in sys.argv
    catalog = json.load(open(os.path.join(REPO, "docs", "corpus-catalog.json"),
                             encoding="utf-8"))
    rows = catalog if isinstance(catalog, list) else catalog.get("works", catalog.get("rows", []))
    missing = [r["slug"] for r in rows
               if isinstance(r, dict) and not r.get("edition")]
    print("catalog rows missing edition: %d" % len(missing))
    proposals, manual = {}, []
    for slug in sorted(missing):
        ed, src = propose(slug)
        if ed:
            proposals[slug] = {"edition": ed, "src": src}
            print("PROPOSE %-55s [%s] %s" % (slug, src, ed[:90]))
        else:
            manual.append((slug, src))
            print("MANUAL  %-55s (%s)" % (slug, src))
    if not apply:
        print("dry run: no writes. Re-run with --apply.")
        return
    for slug, p in proposals.items():
        yml_path = os.path.join(REPO, "books", slug, "book.yml")
        with open(yml_path, encoding="utf-8") as f:
            lines = f.readlines()
        if any((l.startswith("edition:") or l.startswith("edition_lock:"))
                and not re.match(r"^edition(_lock)?:\s*(\"\"|'')?\s*$", l)
                for l in lines):
            print("SKIP (has value) %s" % slug)
            continue
        ed = p["edition"].replace('"', "'")
        ins = 'edition: "%s"\n' % ed
        # Replace an existing EMPTY key in place, else append at end
        # (never insert after description: it can be multiline).
        done = False
        for i, l in enumerate(lines):
            if re.match(r"^edition(_lock)?:\s*(\"\"|'')?\s*$", l):
                lines[i] = ins
                done = True
                break
        if not done:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(ins)
        with open(yml_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("WROTE %s" % slug)
    rec = os.path.join(REPO, "outputs", "edition-backfill-20260923.json")
    with open(rec, "w", encoding="utf-8") as f:
        json.dump({"proposals": proposals,
                   "manual": manual}, f, indent=1, sort_keys=True)
    print("receipt %s; manual-triage: %d" % (rec, len(manual)))


if __name__ == "__main__":
    main()
