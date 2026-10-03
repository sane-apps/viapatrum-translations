#!/usr/bin/env python3
"""Bring a work in from First1KGreek (or Perseus canonical-greekLit) as a new
book the translation lanes can take (owner 2026-10-03, phase one: the early
Church, earliest first; see docs/early-inventory.json).

  python3 scripts/intake_first1k.py --urn tlg1443.tlg001 --slug ignatius-letters \
      --author "Ignatius of Antioch" --title "The Letters of Ignatius" [--dry-run]

Writes books/<slug>/: book.yml, sources/<urn>.xml (the raw TEI witness, kept
byte for byte), and per top-level unit translations/<stem>_source.json (one
section per chapter, editorial notes left out), an empty <stem>_english.json
for the lanes to fill, and <stem>_meta.json naming the edition and witness.
Then runs provenance_audit.py on the new book and refuses to leave a book
that fails it.

Latin (stoa*/phi* urns) comes from the Open Greek and Latin CSEL TEI
(csel-dev, public-domain CSEL volumes) and Perseus canonical-latinLit, both
CC BY-SA 4.0. Every Latin edition printed by 1929 is kept as a witness; the
CSEL text is the copy-text when it exists, later editions are refused.
Sections use the key "latin":

  python3 scripts/intake_first1k.py --urn stoa0104a.stoa001 --slug cyprian-to-donatus \
      --author "Cyprian of Carthage" --title "Cyprian: To Donatus" \
      --original-title "Ad Donatum" --year 258 [--dry-run]

Greek editions printed after 1929 are refused too. --edition picks a file
when a work has several (Eusebius' Church History: the Dindorf 1871 text,
tlg2018.tlg002.1st1K-grc2.xml, not the 1932 Loeb); --skip-units drops
front-matter divs by n or subtype (Hippolytus' Refutatio: MSS, the sigla).

Greek works with no TEI come from Migne PG with --pg-khazarzar/--pg-scan
(see "Patrologia Graeca mode" below).

Set GITHUB_TOKEN to lift the GitHub API listing limit (60 calls an hour).
"""
import argparse
import collections
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
try:  # refuse entity tricks in downloaded XML when defusedxml is installed
    from defusedxml.ElementTree import fromstring as xml_fromstring
except ImportError:  # stdlib expat does not fetch external entities
    xml_fromstring = ET.fromstring
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "books"
TEI = "{http://www.tei-c.org/ns/1.0}"
REPOS = {
    "1st1K": "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data",
    "perseus": "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data",
}
# Latin: (GitHub repo, label); CSEL first so the critical edition is copy-text.
LATIN_REPOS = {
    "csel": ("OpenGreekAndLatin/csel-dev", "OGL CSEL TEI"),
    "perseus-lat": ("PerseusDL/canonical-latinLit", "Perseus canonical-latinLit TEI"),
}
LAST_PD_YEAR = 1929  # later printed editions may still be in copyright
SKIP = {"note", "bibl", "ref", "head", "label", "del", "app", "rdg", "milestone", "figure"}


def gh_json(url: str):
    tok = os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"} if tok else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def edition_year(root) -> int:
    """Latest printing year named in sourceDesc (imprint dates first); 0 if none."""
    sd = root.find(f".//{TEI}sourceDesc")
    if sd is None:
        return 0
    dates = [" ".join(d.itertext()) for d in sd.iter(f"{TEI}date")] or [" ".join(sd.itertext())]
    years = [int(y) for d in dates for y in re.findall(r"\b(1[5-9]\d\d|20\d\d)\b", d)]
    return max(years) if years else 0


def fetch_latin(urn: str, prefer: str = "") -> tuple[list, list]:
    """([(file name, raw bytes, repo, year)] public-domain Latin editions,
    copy-text first; [(file name, repo, reason)] editions refused)."""
    group, work = urn.split(".")[:2]
    keep, refused = [], []
    for repo, (gh, _) in LATIN_REPOS.items():
        try:
            names = [x["name"] for x in gh_json(f"https://api.github.com/repos/{gh}/contents/data/{group}/{work}")]
        except Exception:  # noqa: BLE001
            continue
        for n in sorted(n for n in names if n.endswith(".xml") and "-lat" in n and not n.startswith("__")):
            with urllib.request.urlopen(f"https://raw.githubusercontent.com/{gh}/master/data/{group}/{work}/{n}",
                                        timeout=180) as r:
                raw = r.read()
            year = edition_year(xml_fromstring(raw))
            if not year or year > LAST_PD_YEAR:
                refused.append((n, repo, f"edition printed {year}, after {LAST_PD_YEAR}" if year
                                else "no printing year in sourceDesc"))
            else:
                keep.append((n, raw, repo, year))
    if prefer:
        keep.sort(key=lambda e: e[0] != prefer)
    if not keep:
        raise SystemExit(f"no public-domain Latin edition found for {urn}: {refused}")
    return keep, refused


def fetch(urn: str, prefer: str = "") -> tuple[str, bytes, str]:
    """(file name, raw bytes, repo) for the first edition file of a urn, or
    the file named by prefer (e.g. tlg2018.tlg002.1st1K-grc2.xml)."""
    group, work = urn.split(".")[:2]
    for repo, base in REPOS.items():
        api = ("https://api.github.com/repos/OpenGreekAndLatin/First1KGreek/contents/data" if repo == "1st1K"
               else "https://api.github.com/repos/PerseusDL/canonical-greekLit/contents/data")
        try:
            names = [x["name"] for x in gh_json(f"{api}/{group}/{work}")]
        except Exception:  # noqa: BLE001
            continue
        eds = sorted(n for n in names if n.endswith(".xml") and "grc" in n and not n.startswith("__"))
        if prefer:
            eds = [n for n in eds if n == prefer]
        if eds:
            with urllib.request.urlopen(f"{base}/{group}/{work}/{eds[0]}", timeout=120) as r:
                return eds[0], r.read(), repo
    raise SystemExit(f"no Greek edition {prefer or ''} found for {urn}".replace("  ", " "))


def top_divs(edition, skip=()):
    """Top-level textparts, leaving out any whose n or subtype is in skip
    (front matter such as an editor's sigla list)."""
    return [d for d in edition if d.tag == f"{TEI}div"
            and d.get("n") not in skip and d.get("subtype") not in skip]


def text_of(el) -> str:
    """Element text without editorial notes, apparatus or headings."""
    parts = [el.text or ""] if el.tag.replace(TEI, "") not in SKIP else []
    for ch in el:
        if ch.tag.replace(TEI, "") not in SKIP:
            parts.append(text_of(ch))
        parts.append(ch.tail or "")
    return "".join(parts)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def dehyphen(s: str) -> str:
    """Join words the printed page broke at a line end ("ple- num", "ple-num")."""
    return re.sub(r"(\w)- ?(?=[a-zæœ])", r"\1", s)


def chapters_only(root) -> bool:
    """True when the top-level textparts are chapters (one file, a section
    per chapter), not books or letters (a file each)."""
    edition = root.find(f".//{TEI}div[@type='edition']")
    tops = [d for d in (edition if edition is not None else []) if d.tag == f"{TEI}div"]
    return bool(tops) and (tops[0].get("subtype") in ("chapter", "section", "caput")
                           or not any(k.tag == f"{TEI}div" for t in tops for k in t))


def edition_label(root) -> str:
    for path in (f".//{TEI}sourceDesc//{TEI}bibl", f".//{TEI}sourceDesc//{TEI}biblStruct"):
        el = root.find(path)
        if el is not None:
            return clean("".join(el.itertext()))[:300]
    return ""


def flat_units(root, skip=()):
    """One file; each top-level textpart (a chapter) is one section."""
    edition = root.find(f".//{TEI}div[@type='edition']")
    if edition is None:
        edition = root.find(f".//{TEI}body")
    secs = []
    for k, top in enumerate(top_divs(edition, skip), 1):
        lines = [clean(text_of(p)) for p in top.iter() if p.tag in (f"{TEI}p", f"{TEI}l")]
        lines = [x for x in lines if x] or [clean(text_of(top))]
        if lines[0]:
            secs.append((top.get("n") or str(k), lines))
    return [("1", "", secs)] if secs else []


def units(root, skip=()):
    """[(unit n, unit title, [(section n, [lines])])]: top-level textparts as
    files, their children as sections; deeper parts join into the section."""
    edition = root.find(f".//{TEI}div[@type='edition']")
    if edition is None:
        edition = root.find(f".//{TEI}body")
    tops = top_divs(edition, skip)
    if not tops:
        tops = [edition]
    out = []
    for top in tops:
        n = top.get("n") or str(len(out) + 1)
        head = top.find(f"{TEI}head")
        title = clean("".join(head.itertext())) if head is not None else ""
        kids = [d for d in top if d.tag == f"{TEI}div"]
        secs = []
        for k, kid in enumerate(kids or [top], 1):
            lines = [clean(text_of(p)) for p in kid.iter() if p.tag in (f"{TEI}p", f"{TEI}l")]
            lines = [x for x in lines if x]
            if not lines:
                lines = [clean(text_of(kid))]
            if lines and lines[0]:
                secs.append((kid.get("n") or str(k), lines))
        if secs:
            out.append((n, title, secs))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--urn", default="", help="e.g. tlg1443.tlg001 (TEI modes)")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--stem", default="", help="file stem prefix (default: slug initials)")
    ap.add_argument("--unit-names", default="", help="comma list naming each top-level unit for file stems")
    ap.add_argument("--flat", action="store_true", help="one file, one section per top-level chapter")
    ap.add_argument("--year", type=int, default=0, help="writer year from docs/early-inventory.json")
    ap.add_argument("--original-title", default="", help="Latin/Greek title for book.yml original_title")
    ap.add_argument("--edition", default="", help="edition file name to use as copy-text "
                    "(e.g. tlg2018.tlg002.1st1K-grc2.xml); default: the first one listed")
    ap.add_argument("--skip-units", default="", help="comma list of top-level div n or subtype values "
                    "to leave out (front matter, e.g. MSS for a sigla list)")
    ap.add_argument("--pg-khazarzar", default="", help="PG mode copy-text: path under Khazarzar PG_Migne/, "
                    "e.g. 'Athanasius the Great of Alexandria_ PG 25-28/Vita Antonii.pdf'")
    ap.add_argument("--pg-scan", default="", help="PG mode check witness: archive.org item(s) of the PG "
                    "volume, comma list (e.g. patrologiae_cursus_completus_gr_vol_026)")
    ap.add_argument("--pg-anchors", default="", help="PG mode without Khazarzar: 'first words|last words' "
                    "of the work in the scan OCR")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.pg_khazarzar or a.pg_anchors:
        return pg_main(a)
    if not a.urn:
        raise SystemExit("--urn is required (or --pg-khazarzar / --pg-anchors for PG mode)")

    dest = BOOKS / a.slug
    if dest.exists():
        raise SystemExit(f"already exists: {dest} (one book per work; extend it by hand)")
    latin = not a.urn.startswith(("tlg", "ogl"))  # ogl* urns in First1KGreek are Greek
    lang, key = ("Latin", "latin") if latin else ("Greek", "greek")
    if latin:
        eds, refused = fetch_latin(a.urn, a.edition)
        name, raw, repo, _ = eds[0]
    else:
        name, raw, repo = fetch(a.urn, a.edition)
        eds, refused = [(name, raw, repo, 0)], []
    root = xml_fromstring(raw)
    if not latin and edition_year(root) > LAST_PD_YEAR:
        raise SystemExit(f"{name}: edition printed {edition_year(root)}, after {LAST_PD_YEAR}; "
                         "choose a public-domain file with --edition")
    edition = edition_label(root)
    skip = tuple(x.strip() for x in a.skip_units.split(",") if x.strip())
    flat = a.flat or (latin and chapters_only(root))
    parts = flat_units(root, skip) if flat else units(root, skip)
    if latin:
        parts = [(n, t, [(sn, [dehyphen(x) for x in lines]) for sn, lines in secs]) for n, t, secs in parts]
    if not parts:
        raise SystemExit("no text parts parsed")
    names = [x.strip() for x in a.unit_names.split(",")] if a.unit_names else []
    stem0 = a.stem or "".join(w[0] for w in a.slug.split("-"))
    words = sum(len(" ".join(l).split()) for _, _, secs in parts for _, l in secs)
    print(f"{a.urn} ({repo}): {len(parts)} units, {sum(len(s) for _, _, s in parts)} sections, {words} {lang} words")
    print(f"edition: {edition}")
    for n, _, r, y in eds[1:]:
        print(f"  also witness: {n} ({r}, {y})")
    for n, r, why in refused:
        print(f"  refused: {n} ({r}): {why}")
    for i, (n, title, secs) in enumerate(parts):
        print(f"  unit {n} {names[i] if i < len(names) else title!r}: {len(secs)} sections; "
              f"first: {secs[0][1][0][:70]}")
    if a.dry_run:
        return 0

    # Build in a staging folder and audit it alone; lanes take any book with a
    # translations/ folder, so the book enters books/ only after it passes.
    final, stage_root = dest, ROOT / "outputs" / "intake-stage"
    dest = stage_root / a.slug
    if dest.exists():
        raise SystemExit(f"stale staging folder {dest}; inspect and remove it first")
    (dest / "sources").mkdir(parents=True)
    (dest / "translations").mkdir()
    witnesses = []  # every edition kept byte for byte; the first is copy-text
    for k, (n, r_bytes, r, _) in enumerate(eds):
        (dest / "sources" / n).write_bytes(r_bytes)
        g, w = a.urn.split(".")[:2]
        src_url = (f"{REPOS[r]}/{g}/{w}/{n}" if not latin
                   else f"https://raw.githubusercontent.com/{LATIN_REPOS[r][0]}/master/data/{g}/{w}/{n}")
        lab = edition if k == 0 else edition_label(xml_fromstring(r_bytes))
        witnesses.append({"name": lab or n, "language": lang,
                          "role": "copy-text" if k == 0 else "comparison witness (not aligned to the sections)",
                          "path": f"sources/{n}", "urn": f"urn:cts:{key}Lit:{a.urn}", "source": src_url})
    origin = (LATIN_REPOS[repo][1] if latin else ("First1KGreek" if repo == "1st1K" else "Perseus") + " TEI")
    (dest / "book.yml").write_text(
        f'title: "{a.title}"\nauthor: "{a.author}"\nslug: "{a.slug}"\nlanguage: {lang}\nstatus: available\n'
        + (f'original_title: "{a.original_title}"\n' if a.original_title else "")
        + f'edition: "{edition or name} ({origin}, urn:cts:{key}Lit:{a.urn})"\n'
        f'scope: "Complete as transmitted in the copy-text edition."\n'
        f'notes: "Phase-one intake 2026-10-03 by scripts/intake_first1k.py; new English from the {lang}."\n'
        + (f"year: {a.year}\n" if a.year else ""),
        encoding="utf-8")
    for i, (n, title, secs) in enumerate(parts):
        label = names[i] if i < len(names) else (title or f"u{n}")
        stem = stem0 if flat else f"{stem0}_{re.sub(r'[^a-z0-9]+', '', label.lower())[:16] or n}"
        sid = (lambda sn: str(sn)) if flat else (lambda sn: f"{n}.{sn}")
        src = [{"section": sid(sn), key: lines} for sn, lines in secs]
        eng = [{"section": sid(sn), "title": "", "english": []} for sn, _ in secs]
        meta = {"slug": a.slug, "title": a.title + (f": {label}" if len(parts) > 1 else ""),
                "author": a.author, "edition": edition, "status": "available", "first_english": False,
                "text_history": {
                    "method": f"New English from the {lang} copy-text; no published English used as wording.",
                    "witnesses": witnesses}}
        t = dest / "translations"
        (t / f"{stem}_source.json").write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding="utf-8")
        (t / f"{stem}_english.json").write_text(json.dumps(eng, ensure_ascii=False, indent=1), encoding="utf-8")
        (t / f"{stem}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return audit_and_move(a.slug, dest, final, f"{len(parts)} files")


def audit_and_move(slug: str, stage: Path, final: Path, what: str) -> int:
    """Source-identity gate: the staged book must pass the provenance audit
    before it enters books/."""
    rep = ROOT / "outputs" / f"provenance-{slug}.json"
    subprocess.run([sys.executable, str(ROOT / "scripts/provenance_audit.py"), "--books", str(stage.parent), "--out", str(rep)],
                   check=False, capture_output=True, timeout=600)
    flags = [f for f in (json.loads(rep.read_text()).get("flags") or []) if f.get("slug") == slug] if rep.exists() else []
    if flags:
        print("PROVENANCE FLAGS:", json.dumps(flags, ensure_ascii=False)[:600], f"(left in {stage})")
        return 1
    if not rep.exists():
        print(f"provenance audit did not run; left in {stage}")
        return 1
    stage.rename(final)
    print(f"intake ok: books/{slug} ({what}); provenance audit clean")
    return 0


# --- Patrologia Graeca mode (owner 2026-10-03) ------------------------------
# Greek works with no TEI. Copy-text is the Aegean "Digital Patrology" text on
# Khazarzar (born-digital PDFs keyed to Migne PG, the source the library's
# Didymus, Cyril, Severian and Agathias books already use), taken only when it
# prints like Migne; the check witness is the Greek OCR of the PG volume scan
# on archive.org, aligned and diffed word by word. With no Khazarzar text the
# copy-text is the PG scan OCR itself between two anchor phrases, checked
# against a second scan of the same volume (one print, so single-witness).
#
#   python3 scripts/intake_first1k.py --slug athanasius-vita-antonii \
#       --author "Athanasius of Alexandria" --title "Athanasius: Life of Antony" \
#       --original-title "Vita Antonii" --year 373 \
#       --pg-khazarzar "Athanasius the Great of Alexandria_ PG 25-28/Vita Antonii.pdf" \
#       --pg-scan patrologiae_cursus_completus_gr_vol_026 [--dry-run]
#
#   python3 scripts/intake_first1k.py --slug hippolytus-contra-noetum ... \
#       --pg-scan patrologiae_cursus_completus_gr_vol_010_1,patrologiae_cursus_completus_gr_vol_010_2 \
#       --pg-anchors "first words of the work|last words of the work"
KHAZ = "http://khazarzar.skeptik.net/pgm/PG_Migne"
PG_CACHE = ROOT / "outputs" / "pg-intake" / "cache"
KHAZ_FOOTER = re.compile(r"Ερευνητικό|Χρηματοδότηση|Επιτρέπεται η ελεύθερη|Πανεπιστήμιο Αιγαίου|"
                         r"Εργαστήριο ∆ιαχείρισης|ΨΗΦΙΑΚΗ ΠΑΤΡΟΛΟΓΙΑ|^\s*\d{1,3}\s*$")
SECTION_WORDS = 450  # lanes take sections of about 300-650 words


def fold(w: str) -> str:
    """Compare form: no accents or case, final sigma, and the letter pairs
    Greek OCR confuses most (κ/χ, β/δ) made one."""
    w = "".join(c for c in unicodedata.normalize("NFD", w.lower()) if not unicodedata.combining(c))
    w = w.replace("ς", "σ").replace("ϲ", "σ").replace("χ", "κ").replace("δ", "β")
    return re.sub(r"[^α-ω]", "", w)


_VOCAB: set = set()


def vocab() -> set:
    """Word forms of the born-digital Greek TEI already in the library."""
    if not _VOCAB:
        for f in sorted(BOOKS.glob("*/sources/*grc*.xml")):
            text = re.sub(r"<[^>]+>", " ", f.read_text(encoding="utf-8", errors="ignore"))
            _VOCAB.update(x for x in (fold(t) for t in text.split()) if x)
    return _VOCAB


def cached(url: str, name: str) -> bytes:
    PG_CACHE.mkdir(parents=True, exist_ok=True)
    path = PG_CACHE / name
    if not path.exists() or path.stat().st_size < 1000:
        with urllib.request.urlopen(url, timeout=600) as r:
            path.write_bytes(r.read())
    return path.read_bytes()


# The Khazarzar PDFs type some Greek capitals and mu with look-alike math signs.
LOOKALIKE = str.maketrans({"\u2206": "Δ", "\u00b5": "μ", "\u2126": "Ω"})


def khazarzar(rel: str) -> tuple[bytes, str, str]:
    """(pdf bytes, extracted text, url) for a path under PG_Migne/."""
    url = f"{KHAZ}/{urllib.parse.quote(rel)}"
    raw = cached(url, "khaz__" + re.sub(r"[^\w.-]+", "_", rel))
    tmp = PG_CACHE / "khaz_extract.pdf"
    tmp.write_bytes(raw)
    exe = shutil.which("pdftotext") or "/opt/homebrew/bin/pdftotext"
    text = subprocess.run([exe, str(tmp), "-"], capture_output=True, text=True, check=True).stdout
    return raw, text.translate(LOOKALIKE), url


def migne_print(text: str) -> tuple[bool, str]:
    """Migne keeps the grave on an oxytone before punctuation ("ὀρθὴν, καὶ");
    the later critical editions that also sit on Khazarzar print the acute
    (Opitz, Thomson, SC). PG column marks ("26.532") are the other sign."""
    g = a = 0
    for w in re.findall(r"(\w+)[,·.;]", text):
        d = unicodedata.normalize("NFD", w)
        tail = d[len(d.rstrip("̀́͂̓̔̈ͅ")):]
        g += "̀" in tail
        a += "́" in tail and "̀" not in tail
    cols = len(re.findall(r"\b\d{1,3}[AB]?\.\d{2,4}\b", text))
    ratio = g / max(1, g + a)
    ok = (g + a >= 8 and ratio >= 0.55) or (g + a < 8 and cols and ratio >= 0.5)
    return ok, f"grave before punctuation {g}/{g + a} ({ratio:.2f}), PG column marks {cols}"


def scan_lines(item: str) -> list[tuple[int, str]]:
    """Greek lines of a PG volume's archive.org OCR: (raw line no, text),
    end-of-line hyphens joined, Latin column and junk lines dropped."""
    raw = cached(f"https://archive.org/download/{item}/{item}_djvu.txt", f"{item}_djvu.txt").decode("utf-8", "replace")
    lines = raw.split("\n")
    out, voc, carry = [], vocab(), ""
    for i, line in enumerate(lines):
        line = carry + line.strip()
        carry = ""
        m = re.search(r"(\w+)[-‐¬]$", line)
        if m and i + 1 < len(lines):
            carry, line = m.group(1), line[:m.start()].rstrip()
        toks = [f for f in (fold(x) for x in line.split()) if f]
        if len(toks) >= 2 and sum(t in voc for t in toks) / len(toks) >= 0.4:
            out.append((i, line))
    return out


def scan_tokens(lines: list[tuple[int, str]]) -> tuple[list[str], list[str], list[int]]:
    """(folded tokens, raw words, line index of each) over kept scan lines."""
    folded, words, where = [], [], []
    for k, (_, line) in enumerate(lines):
        for w in line.split():
            f = fold(w)
            if f:
                folded.append(f); words.append(w); where.append(k)
    return folded, words, where


def locate(ct: list[str], ot: list[str], n: int = 4) -> tuple[int, int, int]:
    """Window of ot that best holds ct: (start, end, distinct 4-gram hits)."""
    idx = collections.defaultdict(list)
    for i in range(len(ot) - n):
        idx[tuple(ot[i:i + n])].append(i)
    hits = sorted((i, j) for j in range(len(ct) - n) for i in idx.get(tuple(ct[j:j + n]), ()))
    span, best, lo, cnt = int(len(ct) * 1.5) + 200, (0, 0, 0), 0, collections.Counter()
    for hi in range(len(hits)):
        cnt[hits[hi][1]] += 1
        while hits[hi][0] - hits[lo][0] > span:
            cnt[hits[lo][1]] -= 1
            if not cnt[hits[lo][1]]:
                del cnt[hits[lo][1]]
            lo += 1
        if len(cnt) > best[0]:
            best = (len(cnt), hits[lo][0], hits[hi][0])
    return max(0, best[1] - 80), best[2] + 80, best[0]


def collate(ct: list[str], win: list[str]) -> dict:
    """Word diff of copy-text against the scan: agreement, spacing-only and
    OCR-like differences, and the substantive ones (both readings real words)."""
    sm = difflib.SequenceMatcher(None, ct, win, autojunk=False)
    same = sum(b.size for b in sm.get_matching_blocks())
    counts, subst, voc = collections.Counter(), [], vocab()
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            continue
        A, B = ct[a1:a2], win[b1:b2]
        if "".join(A) == "".join(B):
            counts["spacing"] += 1
        elif len(A) > 8 or len(B) > 8:
            counts["gap"] += 1  # scan notes, Latin, lacuna or page furniture
        elif not B:
            counts["copy_text_only"] += 1  # mostly words the OCR lost
        elif not A:
            counts["scan_only"] += 1  # mostly OCR debris; real additions show here too
        elif (difflib.SequenceMatcher(None, "".join(A), "".join(B)).ratio() >= 0.6
              or not all(x in voc and len(x) >= 3 for x in A + B)):
            counts["ocr"] += 1
        else:
            counts["substantive"] += 1
            subst.append({"copy_text": " ".join(A), "scan": " ".join(B), "at_word": a1})
    return {"agreement": round(same / max(1, len(ct)), 3), "differences": dict(counts), "substantive": subst[:400]}


def join_splits(words: list[str], extra: set) -> list[str]:
    """Rejoin words the Khazarzar typesetting broke with a space ("κρα τοῦντες")
    when the joined form is a known word and a half is not."""
    voc, out, i = vocab() | extra, [], 0
    while i < len(words):
        a = words[i]
        if i + 1 < len(words) and re.fullmatch(r"[^\W\d_]+", a):
            b = words[i + 1]
            fa, fb, fab = fold(a), fold(b), fold(a + b)
            if fa and fb and fab in voc and (fa not in voc or fb not in voc):
                out.append(a + b); i += 2
                continue
        out.append(a); i += 1
    return out


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.;·])\s+(?=\S)", text) if s.strip()]


def chunk(text: str, size: int = SECTION_WORDS) -> list[str]:
    """Cut at sentence ends into pieces of about size words."""
    out, cur = [], []
    for s in sentences(text):
        cur.append(s)
        if len(" ".join(cur).split()) >= size:
            out.append(" ".join(cur)); cur = []
    if cur:
        if out and len(" ".join(cur).split()) < size // 3:
            out[-1] += " " + " ".join(cur)
        else:
            out.append(" ".join(cur))
    return out


COL = re.compile(r"\b(\d{1,3}[AB]?)\.(\d{2,4})\b")


def pg_sections(text: str, vols: set) -> list[tuple[str, str, list]]:
    """[(unit n, title, [(section n, [paragraph], locus)])] from Khazarzar text.
    All-capital lines are headings and open a unit when the text has several;
    numbered lines ("2 Κατὰ πλεονεξίας") open chapters; PG column marks become
    each section's locus."""
    lines = [l.strip() for l in text.split("\n")[1:] if l.strip() and not KHAZ_FOOTER.search(l)]
    blocks = []  # [(heading, [lines])]
    for l in lines:
        letters = [c for c in l if c.isalpha()]
        if len(letters) >= 3 and all(not c.islower() for c in letters) and (
                len(l.split()) >= 2 or not blocks or not blocks[-1][1]):
            if blocks and not blocks[-1][1]:
                blocks[-1] = (blocks[-1][0] + " " + l, [])
            else:
                blocks.append((l, []))
        else:
            if not blocks:
                blocks.append(("", []))
            blocks[-1][1].append(l)
    blocks = [b for b in blocks if b[1]]
    if len(blocks) > 12:  # a heading per psalm or chapter: one file, a chapter each
        blocks = [("", [f"{k} {head} {l}" if j == 0 else l for j, l in enumerate(body)])
                  for k, (head, body) in enumerate(blocks, 1)]
        blocks = [("", [l for _, body in blocks for l in body])]
    units = []
    for u, (title, body) in enumerate(blocks, 1):
        chapters, cur, num = [], [], None
        for l in body:
            m = re.match(r"(\d{1,3})\s+(?=\D)", l)
            if m and not COL.match(l) and (num is None and m.group(1) in ("1", "2") or
                                           num is not None and int(m.group(1)) == int(num) + 1):
                if cur:
                    chapters.append((num, " ".join(cur)))
                num, cur = m.group(1), [l[m.end():]]
            else:
                cur.append(l)
        if cur:
            chapters.append((num, " ".join(cur)))
        marks = [f"{v}.{c}" for v, c in COL.findall(title) if v.rstrip("AB") in vols]
        title = re.sub(r"\s{2,}", " ", COL.sub("", title)).strip()
        secs, col = [], marks[-1] if marks else ""
        for num, ctext in chapters:
            pieces = chunk(ctext) if len(ctext.split()) > 700 or num is None else [ctext]
            for k, p in enumerate(pieces, 1):
                marks = [f"{v}.{c}" for v, c in COL.findall(p) if v.rstrip("AB") in vols]
                start = col or (marks[0] if marks else "")
                p = COL.sub(lambda m: "" if m.group(1).rstrip("AB") in vols else m.group(0), p)
                p = re.sub(r"\s{2,}", " ", p).strip()
                col = marks[-1] if marks else col
                locus = f"PG {start}" + (f"–{col.split('.')[-1]}" if col and col != start else "") if start else ""
                sn = (num if len(pieces) == 1 else f"{num}.{k}") if num else str(len(secs) + 1)
                if p:
                    secs.append((sn, [p], locus))
        if secs:
            units.append((str(u), title, secs))
    return units


def excerpt(text: str, anchors: str) -> str:
    """The stretch of text from the first words to the last words given as
    'first words|last words' (compared folded), keeping its line breaks."""
    first, last = ([fold(w) for w in part.split() if fold(w)] for part in anchors.split("|", 1))
    spans = [(m.start(), m.end(), fold(m.group())) for m in re.finditer(r"\S+", text)]
    spans = [x for x in spans if x[2]]
    seq = [x[2] for x in spans]

    def find(words, start=0):
        for i in range(start, len(seq) - len(words) + 1):
            if seq[i:i + len(words)] == words:
                return i
        raise SystemExit(f"anchor not found: {' '.join(words)}")
    i = find(first)
    j = find(last, i) + len(last) - 1
    return "[excerpt]\n" + text[spans[i][0]:spans[j][1]]


def pg_main(a) -> int:
    dest = BOOKS / a.slug
    if dest.exists():
        raise SystemExit(f"already exists: {dest} (one book per work; extend it by hand)")
    scans = [s.strip() for s in a.pg_scan.split(",") if s.strip()]
    if not scans:
        raise SystemExit("--pg-scan names the archive.org PG volume item(s) to check against")
    vols = {str(int(m.group(1))) for s in scans for m in [re.search(r"vol_0*(\d+)", s)] if m}
    files, witnesses, stem0 = {}, [], a.stem or "".join(w[0] for w in a.slug.split("-"))
    if a.pg_khazarzar:
        raw, text, url = khazarzar(a.pg_khazarzar)
        full = text
        if a.pg_anchors:  # one work transmitted inside another (a creed quoted in a Life)
            text = excerpt(text, a.pg_anchors)
        ok, why = migne_print(text)
        print(f"copy-text {a.pg_khazarzar}: {why}")
        if not ok:
            raise SystemExit(f"refused: {a.pg_khazarzar} prints like a later critical edition ({why}); "
                             "PG copy-text needs the scan OCR (--pg-anchors)")
        ct = [f for f in (fold(x) for x in join_splits(text.split(), set())) if f]
        best = None
        for item in scans:
            lines = scan_lines(item)
            ot, owords, where = scan_tokens(lines)
            s, e, h = locate(ct, ot)
            if h and (best is None or h > best[3]):
                best = (item, s, e, h, lines, ot, where)
        if not best:
            raise SystemExit("refused: the work was not found in the PG scan OCR")
        item, s, e, h, lines, ot, where = best
        # Spacing the scan confirms ("ἀλή θειαν" printed whole) rejoins the
        # copy-text; line breaks stay for the headings.
        text2 = "\n".join(" ".join(join_splits(l.split(), set(ot[s:e]))) for l in text.split("\n"))
        coll = collate([f for f in (fold(x) for x in text2.split()) if f], ot[s:e])
        print(f"check {item}: agreement {coll['agreement']}, differences {coll['differences']}")
        print("  substantive, copy-text | scan:", "; ".join(f"{d['copy_text']} | {d['scan']}"
                                                         for d in coll["substantive"][:25]))
        if coll["agreement"] < 0.55:
            raise SystemExit(f"refused: copy-text and PG scan agree on only {coll['agreement']} of words")
        parts = pg_sections(text2, vols)
        name = Path(a.pg_khazarzar).name
        stem_src = re.sub(r"[^a-z0-9]+", "_", Path(name).stem.lower()).strip("_")
        lo, hi = lines[where[s]][0], lines[where[min(e, len(where)) - 1]][0]
        raw_scan = cached(f"https://archive.org/download/{item}/{item}_djvu.txt", f"{item}_djvu.txt")
        excerpt = "\n".join(raw_scan.decode("utf-8", "replace").split("\n")[lo:hi + 1])
        files[f"{stem_src}_khazarzar.pdf"] = raw
        files[f"{stem_src}_khazarzar.txt"] = (f"[{a.author}: {a.original_title or a.title}; Khazarzar PG text, {url}"
                                             + (f"; this book is the stretch '{a.pg_anchors}'" if a.pg_anchors else "")
                                             + "]\n" + full).encode("utf-8")
        files[f"{stem_src}_pg_scan.txt"] = (f"[{a.author}: {a.original_title or a.title}; PG scan OCR, archive.org "
                                           f"{item}, djvu.txt lines {lo + 1}-{hi + 1}]\n" + excerpt).encode("utf-8")
        files[f"{stem_src}_collation.json"] = json.dumps(
            {"copy_text": f"sources/{stem_src}_khazarzar.txt", "check": f"sources/{stem_src}_pg_scan.txt",
             "method": "word diff after folding accents, case and OCR letter pairs (κ/χ, β/δ)",
             "print_check": why, **coll}, ensure_ascii=False, indent=1).encode("utf-8")
        witnesses = [
            {"name": "Migne PG text (Aegean University Digital Patrology, via Khazarzar)", "language": "Greek",
             "role": "copy-text", "path": f"sources/{stem_src}_khazarzar.txt", "source": url},
            {"name": f"Migne PG {'/'.join(sorted(vols, key=int))}, archive.org scan {item} (Greek OCR)",
             "language": "Greek", "role": "check (same print; OCR compared word by word)",
             "path": f"sources/{stem_src}_pg_scan.txt", "source": f"https://archive.org/details/{item}",
             "agreement": coll["agreement"], "collation": f"sources/{stem_src}_collation.json"}]
        edition = f"Migne PG {'/'.join(sorted(vols, key=int))}; Khazarzar Digital Patrology text, checked against the PG scan"
        method = ("New English from the Greek copy-text (Migne PG as typed by the Aegean Digital Patrology); "
                  f"the copy-text was diffed word by word against the OCR of the PG scan ({coll['agreement']:.0%} "
                  "word agreement, the rest OCR noise or listed in the collation). No published English used as wording.")
        single = False
    else:
        raise SystemExit("refused: no Khazarzar copy-text; scan-only PG intake (OCR copy-text from two scans) "
                         "is not built, because the PG scans interleave the Latin column and the notes")
    names = [x.strip() for x in a.unit_names.split(",")] if a.unit_names else []
    nsec = sum(len(s) for _, _, s in parts)
    words = sum(len(" ".join(p).split()) for _, _, secs in parts for _, p, _ in secs)
    print(f"{a.slug}: {len(parts)} units, {nsec} sections, {words} Greek words")
    for i, (n, title, secs) in enumerate(parts):
        print(f"  unit {n} {names[i] if i < len(names) else title[:60]!r}: {len(secs)} sections; "
              f"first: {secs[0][1][0][:60]} [{secs[0][2]}]")
    if a.dry_run:
        return 0
    stage_root = ROOT / "outputs" / "intake-stage"
    stage = stage_root / a.slug
    if stage.exists():
        raise SystemExit(f"stale staging folder {stage}; inspect and remove it first")
    (stage / "sources").mkdir(parents=True)
    (stage / "translations").mkdir()
    for n, b in files.items():
        (stage / "sources" / n).write_bytes(b)
    (stage / "sources" / "manifest.json").write_text(json.dumps(
        {"work": f"{a.author}, {a.original_title or a.title}", "edition": edition,
         "witnesses": [dict(w, sha256=hashlib.sha256((stage / w["path"]).read_bytes()).hexdigest()) for w in witnesses]
         + [{"path": f"sources/{n}", "role": "raw download", "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in files.items() if n.endswith(".pdf")]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    (stage / "book.yml").write_text(
        f'title: "{a.title}"\nauthor: "{a.author}"\nslug: "{a.slug}"\nlanguage: Greek\nstatus: available\n'
        + (f'original_title: "{a.original_title}"\n' if a.original_title else "")
        + f'edition: "{edition}"\n'
        f'scope: "Complete as transmitted in the copy-text."\n'
        f'notes: "Phase-one PG intake 2026-10-03 by scripts/intake_first1k.py --pg; new English from the Greek.'
        + (' Single witness: one print, two scans.' if single else '') + '"\n'
        + (f"year: {a.year}\n" if a.year else ""),
        encoding="utf-8")
    for i, (n, title, secs) in enumerate(parts):
        label = names[i] if i < len(names) else ""
        stem = stem0 if len(parts) == 1 else f"{stem0}_{re.sub(r'[^a-z0-9]+', '', label.lower())[:16] or 'u' + n}"
        src = [dict({"section": sn, "greek": p}, **({"locus": loc} if loc else {})) for sn, p, loc in secs]
        eng = [{"section": sn, "title": "", "english": []} for sn, _, _ in secs]
        meta = {"slug": a.slug, "title": a.title + (f": {label or title.title()}" if len(parts) > 1 else ""),
                "author": a.author, "edition": edition, "status": "available", "first_english": False,
                "text_history": {"method": method, "witnesses": witnesses,
                                 **({"single_witness": True} if single else {})}}
        if title:
            meta["source_heading"] = title
        t = stage / "translations"
        (t / f"{stem}_source.json").write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding="utf-8")
        (t / f"{stem}_english.json").write_text(json.dumps(eng, ensure_ascii=False, indent=1), encoding="utf-8")
        (t / f"{stem}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return audit_and_move(a.slug, stage, dest, f"{len(parts)} files")


if __name__ == "__main__":
    sys.exit(main())
