#!/usr/bin/env python3
"""Provenance audit v2: prove each book was translated from the right source.

The unit of trust is the WITNESS file recorded in _meta.json text_history.
Checks (SOP source-identity gate):
  1. witness: book.yml author/title vs witness-file head (transliterated).
     Missing witness file = flag.
  2. linkage: every _source.json unit head must occur in its book's witness
     text (else it was extracted from something else).
  3. dup-witness: same witness bytes claimed by 2+ books.
  4. no-meta: _source.json with no sibling/book meta (unverifiable input).
  5. ghost-english: english sections with no source section.
  6. topics: excerpt author vs cited sources/ filename.
Usage: python3 provenance_audit.py [--books DIR] [--out report.json]
"""
import argparse, glob, hashlib, json, os, re, sys, unicodedata

GREEK_LATIN = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e",
    "ζ": "z", "η": "e", "θ": "th", "ι": "i", "κ": "k", "λ": "l",
    "μ": "m", "ν": "n", "ξ": "x", "ο": "o", "π": "p", "ρ": "r",
    "σ": "s", "ς": "s", "τ": "t", "υ": "y", "φ": "ph", "χ": "ch",
    "ψ": "ps", "ω": "o",
}

def delatinize(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(GREEK_LATIN.get(c, c if c.isascii() else " ") for c in s.lower())

def norm(s):
    return re.sub(r"[^a-z]+", "", delatinize(s)).replace("c", "k")

def surname_stems(author):
    parts = re.findall(r"[A-Za-z]+", author or "")
    stems = set()
    for p in parts:
        p = p.lower().replace("c", "k")
        if len(p) >= 4:
            stems.add(p[:7])
            stems.add(p[:6])
            stems.add(p[:5])
    return [s for s in stems if len(s) >= 4]

def title_words(title):
    stop = {"the", "of", "on", "a", "an", "to", "and", "in", "de", "ad",
            "contra", "pro", "per", "liber", "books", "book", "saint", "st",
            "fragmenta", "fragment", "fragments", "selected", "homilies",
            "letters", "treatises", "works", "with", "from"}
    return [norm(w) for w in re.findall(r"[a-zA-Z]{5,}", title or "")
            if w.lower() not in stop][:8]

def load_yml(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"(\w+):\s*(.*)$", line.rstrip())
        if m:
            d[m.group(1)] = m.group(2).strip().strip("'\"")
    return d

def unit_head_text(row):
    for k in ("greek", "latin", "source", "text"):
        v = row.get(k)
        if isinstance(v, list) and v and isinstance(v[0], str):
            return v[0]
        if isinstance(v, str) and v.strip():
            return v
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", default=os.path.expanduser(
        "~/SaneApps/clients/translations/books"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    flags = []
    stats = {"books": 0, "witnesses": 0, "source_files": 0}
    seen_witness = {}

    def flag(check, slug, file, detail="", author="", title=""):
        flags.append({"check": check, "slug": slug, "file": file,
                      "author": author, "title": title, "detail": detail[:300]})

    for bookdir in sorted(glob.glob(os.path.join(a.books, "*"))):
        if not os.path.isdir(bookdir):
            continue
        slug = os.path.basename(bookdir)
        yml = os.path.join(bookdir, "book.yml")
        if not os.path.isfile(yml):
            continue
        meta = load_yml(yml)
        author, title = meta.get("author", ""), meta.get("title", "")
        srcs = sorted(glob.glob(os.path.join(bookdir, "translations", "*_source.json")))
        metas = sorted(glob.glob(os.path.join(bookdir, "translations", "*_meta.json")))
        if not srcs:
            continue
        stats["books"] += 1
        stems = surname_stems(author)
        twords = [w for w in title_words(title) if len(w) >= 5]
        witnesses = []  # (metafile, wpath, resolved, text|None)
        for mp in metas:
            try:
                m = json.load(open(mp, encoding="utf-8"))
            except Exception as e:
                flag("parse", slug, os.path.basename(mp), str(e)[:120], author, title)
                continue
            for w in (m.get("text_history", {}) or {}).get("witnesses", []) or []:
                wp = w.get("path") or ""
                res = None
                for cand in (os.path.join(bookdir, wp),
                             os.path.join(a.books, wp.lstrip("/")),
                             wp):
                    if cand and os.path.isfile(cand):
                        res = cand
                        break
                txt = None
                if res:
                    try:
                        txt = open(res, encoding="utf-8", errors="replace").read()
                    except Exception:
                        txt = None
                witnesses.append((mp, wp, res, txt))
        if not witnesses and metas:
            flag("no-witness", slug, os.path.basename(metas[0]),
                 "meta lists no witnesses", author, title)
        for mp, wp, res, txt in witnesses:
            stats["witnesses"] += 1
            if not res:
                flag("witness-missing", slug, f"{os.path.basename(mp)}:{wp}",
                     "witness file not found", author, title)
                continue
            h = hashlib.sha1(txt.encode("utf-8", "replace")).hexdigest()[:16]
            if h in seen_witness and seen_witness[h][0] != slug:
                flag("dup-witness", slug, wp,
                     f"same bytes as {seen_witness[h][0]}:{seen_witness[h][1]}",
                     author, title)
            else:
                seen_witness[h] = (slug, wp)
            head = norm(txt[:3000])
            if len(head) < 100:
                flag("witness-thin", slug, wp,
                     "witness head too short (%d)" % len(head), author, title)
                continue
            ok = any(st in head for st in stems) or \
                any(w in head for w in twords)
            if not ok:
                flag("witness-mismatch", slug, wp,
                     "head=" + txt[:180].replace("\n", " "), author, title)
        # linkage: unit heads must occur in witness text
        wnorm = " ".join(norm(t or "")[:60000] for _, _, _, t in witnesses if t)
        for sp in srcs:
            stats["source_files"] += 1
            base = os.path.basename(sp)
            if not os.path.isfile(sp.replace("_source.json", "_meta.json")) and not metas:
                flag("no-meta", slug, base, "no meta record", author, title)
            try:
                data = json.load(open(sp, encoding="utf-8"))
            except Exception as e:
                flag("parse", slug, base, str(e)[:120], author, title)
                continue
            rows = data if isinstance(data, list) else data.get("sections", [])
            if not rows:
                flag("empty-source", slug, base, "no sections", author, title)
                continue
            if wnorm:
                probe = norm(unit_head_text(rows[0]))[:120]
                if len(probe) >= 40 and probe not in wnorm:
                    # try second row before flagging (running headers shift)
                    probe2 = norm(unit_head_text(rows[1]))[:120] if len(rows) > 1 else ""
                    if len(probe2) < 40 or probe2 not in wnorm:
                        flag("unlinked", slug, base,
                             "unit head not in witness text: " +
                             unit_head_text(rows[0])[:120].replace("\n", " "),
                             author, title)
            eng = sp.replace("_source.json", "_english.json")
            if os.path.isfile(eng):
                try:
                    edata = json.load(open(eng, encoding="utf-8"))
                except Exception:
                    edata = []
                erows = edata if isinstance(edata, list) else edata.get("sections", [])
                ssecs = {str(r.get("section")) for r in rows if isinstance(r, dict)}
                esecs = {str(r.get("section")) for r in erows if isinstance(r, dict)}
                ghost = sorted(esecs - ssecs - {"None"})
                if ghost:
                    flag("ghost-english", slug, base,
                         "english w/o source: " + ",".join(ghost[:10]), author, title)
    # topics excerpts
    tdir = os.path.join(a.books, "ante-nicene-topics", "translations", "topics")
    tn = 0
    for f in sorted(glob.glob(os.path.join(tdir, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("excerpts", [])
        for x in rows:
            s = x.get("source") or ""
            if not s.startswith("sources/"):
                continue
            tn += 1
            stem = norm(os.path.basename(s).split(".")[0])
            words = [w for w in re.findall(r"[A-Za-z]+", x.get("author") or "")
                     if len(w) >= 5]
            if not any(norm(w)[:7] in stem or stem[:9] in norm(w) for w in words):
                flag("topics-mismatch", "ante-nicene-topics",
                     os.path.basename(f) + "#" + str(x.get("id")),
                     "cites " + s, x.get("author"), x.get("work"))
    stats["topics_checked"] = tn
    rep = {"stats": stats, "flags": flags}
    if a.out:
        json.dump(rep, open(a.out, "w", encoding="utf-8"), indent=1)
    by_check = {}
    for f in flags:
        by_check[f["check"]] = by_check.get(f["check"], 0) + 1
    print(f"books={stats['books']} witnesses={stats['witnesses']} "
          f"source_files={stats['source_files']} topics={tn} "
          f"flags={len(flags)} {by_check}")
    for f in flags[:50]:
        print(f"- [{f['check']}] {f['slug']} {f['file']} :: {f['detail'][:140]}")
    if len(flags) > 50:
        print(f"... {len(flags)-50} more (see report)")

if __name__ == "__main__":
    main()
