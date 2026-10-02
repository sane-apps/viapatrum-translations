#!/usr/bin/env python3
"""Build the Library edition EPUB + PDF for one Fathers site work.

One work in (site slug), EPUB 3 + PDF out. Reads the same English the site
reads, through the site builder's own loaders and helpers (read-only import of
~/SaneApps/websites/fathers.saneapps.com/scripts/build_site.py), and groups
sections into passages with the site's chunking rule so Contents match the
reader page.

EPUB: stdlib only (zipfile). PDF: typst (brew install typst).

Usage:
  python3 scripts/build_edition.py origen-on-prayer --out outputs/edition-sample/origen-on-prayer
  python3 scripts/build_edition.py origen-on-prayer --loader load_origen_works --out DIR
Exit 0 when both files build and the EPUB passes the structural check.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib.util
import inspect
import json
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from xml.dom import minidom

SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
PUBLISHER = "SaneApps · Via Patrum"
SITE_URL = "https://fathers.saneapps.com"
LICENSE = "New English translation © 2026 SaneApps (CC BY 4.0); source text public domain."


def load_site():
    path = SITE / "scripts/build_site.py"
    spec = importlib.util.spec_from_file_location("fathers_build_site", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


def find_work(b, slug: str, loader: str | None) -> dict:
    names = [loader] if loader else sorted(
        n for n, f in vars(b).items()
        if n.startswith("load_") and callable(f) and inspect.isfunction(f)
        and not any(p.default is p.empty for p in inspect.signature(f).parameters.values())
    )
    for name in names:
        try:
            works = getattr(b, name)()
        except Exception:
            continue
        if isinstance(works, list):
            for w in works:
                if isinstance(w, dict) and w.get("slug") == slug:
                    return w
    raise SystemExit(f"work {slug!r} not found (loaders tried: {len(names)})")


# --- passages: same grouping as the site reader (build_site.build → chunk_sections) ---

def display_head(b, w: dict, s: dict) -> str:
    sid = str(s["section"])
    head = str(s.get("head") or "").strip()
    if not head:
        return ""
    low = head.lower()
    sid_dot, sid_dash = sid.replace("-", "."), sid.replace(".", "-")
    echoes = {sid.lower(), sid_dot.lower(), sid_dash.lower(), f"chapter {sid}".lower(),
              f"§{sid}".lower(), f"section {sid}".lower(),
              f"{w['title']} {sid}".lower(), f"{w['title']} {sid_dot}".lower()}
    if low in echoes:
        return ""
    if re.fullmatch(r"(against julian|marriage|rome|collective letter|to florus)\s+[\d.]+", low):
        return ""
    if b._CPG_TITLE.match(head):
        return ""
    return head


def chunk_sections(b, w: dict, secs: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    cur: dict | None = None
    for s in secs:
        h = display_head(b, w, s)
        n = sum(len(p) for p in s["english"])
        bible_locus = bool(h and b._BIBLE_LOCUS_TITLE.match(h))
        same_title = cur is not None and h and cur["head"] == h and cur["chars"] < 9000 and not bible_locus
        untitled_run = (cur is not None and not h and not cur["head"]
                        and cur["chars"] < 3500 and len(cur["secs"]) < 8)
        if same_title or untitled_run:
            cur["secs"].append(s)
            cur["chars"] += n
        else:
            cur = {"head": h, "secs": [s], "chars": n}
            chunks.append(cur)
    return chunks


def curly(text: str) -> str:
    """Straight quotes in the English → typographic quotes (both formats)."""
    text = re.sub(r"(?<=\w)'(?=\w)", "\u2019", text)
    text = re.sub(r"(^|[\s(\[\u2014\u2013/-])'", "\\1\u2018", text)
    text = text.replace("'", "\u2019")
    text = re.sub(r'(^|[\s(\[\u2014\u2013/-])"', "\\1\u201c", text)
    return text.replace('"', "\u201d")


# Bible references. Logos keeps them inline as live links; in a PDF or EPUB they
# are dead text, and a run like "(Titus 3:5) (Psalm 104:24) …" buries the
# sentence. Each parenthesised run becomes one note: a popup footnote in the
# EPUB, a page footnote in the PDF. References inside a sentence stay inline.
_REF_RUN = re.compile(r"(?:\s*\((?:[^()]|\([^()]*\))+\))+")
_REF_ONE = re.compile(
    r"^\s*((?:[1-4]\s)?[A-Z][A-Za-z.]*(?:\s(?:of\s)?[A-Z][A-Za-z.]*)*)\s+\d+(?::\d+)?"
    r"(?:\s*[–-]\s*\d+(?::\d+)?)?(?:\s*,\s*\d+(?:[–-]\d+)?)*(?:\s*\([^()]*\))?\s*$"
)


def _is_ref(b, inner: str) -> bool:
    """True when a parenthesis holds only a Bible reference ("Psalm 33:4 (LXX)")."""
    m = _REF_ONE.match(strip_marks(b, inner))
    if not m:
        return False
    book = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(".").lower()
    return book in _BOOK_NAMES(b) or book in _EXTRA_BOOKS


_EXTRA_BOOKS = {
    "wisdom", "wisdom of solomon", "sirach", "ecclesiasticus", "tobit", "judith", "baruch",
    "1 maccabees", "2 maccabees", "3 maccabees", "4 maccabees", "susanna", "bel", "1 esdras", "2 esdras",
}
_BOOK_CACHE: set[str] = set()


def _BOOK_NAMES(b) -> set[str]:
    if not _BOOK_CACHE:
        _BOOK_CACHE.update(k for k in b._BIBLE_CANON)
        _BOOK_CACHE.update(c.lower() for _, c in b._BIBLE_BOOKS)
    return _BOOK_CACHE


def strip_marks(b, text: str) -> str:
    return b.strip_logos_markup(text)
_REF_GROUP = re.compile(r"\(((?:[^()]|\([^()]*\))*)\)")
NOTE_OPEN, NOTE_CLOSE = "\ue000", "\ue001"


def split_refs(b, raw: str, notes: list[str]) -> str:
    """Raw Logos-marked English → plain text with note placeholders."""
    def sub(m: "re.Match") -> str:
        plain = b.strip_logos_markup(m.group(0)).strip()
        refs = [g.strip() for g in _REF_GROUP.findall(plain) if g.strip()]
        # Every parenthesis in the run must be a Bible reference; asides stay.
        if not refs or not all(_is_ref(b, r) for r in refs):
            return m.group(0)
        notes.append("; ".join(refs))
        return f"{NOTE_OPEN}{len(notes)}{NOTE_CLOSE}"
    return b.strip_logos_markup(_REF_RUN.sub(sub, raw))


def note_parts(text: str) -> list[tuple[str, int | None]]:
    """[(text, None), ("", n), …] — text runs and note numbers in order."""
    out: list[tuple[str, int | None]] = []
    for i, part in enumerate(re.split(f"{NOTE_OPEN}(\\d+){NOTE_CLOSE}", text)):
        if i % 2:
            out.append(("", int(part)))
        elif part:
            out.append((part, None))
    return out


def build_passages(b, w: dict) -> list[dict]:
    ordinals = b.section_ordinals(w["sections"])
    out = []
    for ch in chunk_sections(b, w, w["sections"]):
        secs = ch["secs"]
        first = b.shown_section(secs[0]["section"], ordinals)
        last = b.shown_section(secs[-1]["section"], ordinals)
        title = ch["head"]
        if not title:
            snip = b.strip_logos_markup(" ".join(secs[0].get("english") or []))
            title = snip[:107].rsplit(" ", 1)[0] + "…" if len(snip) > 110 else snip
        notes: list[str] = []
        sections = [
            {"mark": b.shown_section(s["section"], ordinals),
             "supplied": (s.get("supplied_from") or "").strip(),
             "paras": [curly(t) for t in (split_refs(b, p, notes) for p in s["english"]) if t.strip()]}
            for s in secs
        ]
        out.append({
            "notes": notes,
            "range": f"§{first}" if len(secs) == 1 else f"§§{first}–{last}",
            "title": curly(b.clean_reader_notation(b.strip_logos_markup(title))) or f"§{first}",
            "multi": len(secs) > 1,
            "sections": sections,
        })
    return out


def edition_meta(b, w: dict) -> dict:
    th = w.get("text_history") or {}
    wits = [x for x in th.get("witnesses") or [] if isinstance(x, dict) and x.get("name")]
    copy = [x["name"] for x in wits if x.get("role") == "copy-text"]
    checks = [x["name"] for x in wits if x.get("role") != "copy-text"]
    has_greek = any(s.get("greek") for s in w["sections"])
    lang = "Greek" if has_greek else ("Latin" if any(s.get("latin") for s in w["sections"]) else "source")
    about = [
        f"This is an AI-assisted study translation from the {lang}, checked against the {lang} "
        "of the copy-text. Source fidelity and completeness have not been independently "
        "certified. It is not a critical edition.",
    ]
    if copy:
        about.append("Copy-text: " + "; ".join(copy) + ".")
    if checks:
        about.append("Checked against: " + "; ".join(checks) + ".")
    about.append("Section marks (§) follow the copy-text’s numbering. Passage headings are "
                 "plain-English editorial titles, not part of the ancient text.")
    about.append(LICENSE)
    about.append(f"Read free online and report errors at {SITE_URL}/works/{w['slug']}/.")
    return {
        "title": b.public_reader_title(w["title"], slug=w["slug"]),
        "subtitle": b.public_reader_latin_subtitle(w["title"], slug=w["slug"]),
        "author": w["author"],
        "period": b.format_bc_ad(w.get("period") or ""),
        "blurb": w.get("blurb") or "",
        "about": about,
        "slug": w["slug"],
    }


# --- EPUB 3 ---

CSS = """\
body { font-family: serif; line-height: 1.5; margin: 0 5%; }
h1, h2 { font-weight: normal; text-align: center; hyphens: none; }
h1.title { font-size: 2em; margin: 3em 0 0.3em; }
p.byline { text-align: center; font-variant: small-caps; letter-spacing: 0.05em; margin: 0; }
p.sub { text-align: center; font-style: italic; margin: 0.4em 0 2em; }
p.colophon { text-align: center; font-size: 0.85em; margin-top: 4em; }
h2 { font-size: 1.25em; font-style: italic; margin: 2em 0 1em; }
h2 .range { display: block; font-style: normal; font-size: 0.6em; letter-spacing: 0.1em; color: #555; margin-bottom: 0.4em; }
p { margin: 0; text-indent: 1.2em; text-align: justify; }
h2 + p, p.first, p.supplied + p { text-indent: 0; }
p.supplied { font-style: italic; font-size: 0.9em; text-indent: 0; margin: 0.6em 0; }
p.about { text-indent: 0; margin: 0 0 0.8em; text-align: left; }
span.sec { font-size: 0.7em; color: #666; vertical-align: 0.15em; margin-right: 0.25em; }
nav ol { list-style: none; padding-left: 0; }
nav li { margin: 0.35em 0; }
a.nref { font-size: 0.65em; vertical-align: super; line-height: 0; text-decoration: none; margin-left: 0.1em; }
aside.fnote p { font-size: 0.8em; text-indent: 0; margin: 0.2em 0; color: #444; }
aside.fnote a { text-decoration: none; }
"""


def xhtml(title: str, body: str, *, nav: bool = False) -> str:
    ns = ' xmlns:epub="http://www.idpf.org/2007/ops"' if nav else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml"{ns} xml:lang="en" lang="en">\n'
        f'<head><meta charset="UTF-8"/><title>{html.escape(title)}</title>'
        '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
        f"<body>\n{body}\n</body>\n</html>\n"
    )


def passage_xhtml(p: dict, pid: str = "p") -> str:
    e = html.escape

    def body(t: str) -> str:
        bits = []
        for text, n in note_parts(t):
            if n is None:
                bits.append(e(text))
            else:
                bits.append(f'<a epub:type="noteref" class="nref" id="{pid}-r{n}" href="#{pid}-n{n}">{n}</a>')
        return "".join(bits)

    out = [f'<section epub:type="chapter"><h2><span class="range">{e(p["range"])}</span>{e(p["title"])}</h2>']
    for s in p["sections"]:
        if s["supplied"]:
            out.append(f'<p class="supplied">{e(s["supplied"])}</p>')
        for i, t in enumerate(s["paras"]):
            mark = f'<span class="sec">§{e(s["mark"])}</span>' if i == 0 and p["multi"] else ""
            out.append(f"<p>{mark}{body(t)}</p>")
    for n, note in enumerate(p.get("notes") or [], 1):
        out.append(
            f'<aside epub:type="footnote" class="fnote" id="{pid}-n{n}">'
            f'<p><a href="#{pid}-r{n}">{n}</a> {e(note)}</p></aside>'
        )
    out.append("</section>")
    return "\n".join(out)


def build_epub(meta: dict, passages: list[dict], dest: Path) -> None:
    e = html.escape
    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, SITE_URL + '/works/' + meta['slug'] + '/edition')}"
    modified = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sub = f'<p class="sub">{e(meta["subtitle"])}</p>' if meta["subtitle"] else ""
    title_body = (
        f'<p class="byline">{e(meta["author"])}</p><h1 class="title">{e(meta["title"])}</h1>{sub}'
        f'<p class="sub">A new English translation for study</p>'
        f'<p class="colophon">{e(PUBLISHER)}<br/>{e(SITE_URL)}</p>'
    )
    about_body = '<section epub:type="preface"><h2>About this translation</h2>' + "".join(
        f'<p class="about">{e(t)}</p>' for t in ([meta["blurb"]] if meta["blurb"] else []) + meta["about"]
    ) + "</section>"
    files: dict[str, str] = {
        "title.xhtml": xhtml(meta["title"], title_body),
        "about.xhtml": xhtml("About this translation", about_body, nav=True),
    }
    pids = []
    for i, p in enumerate(passages, 1):
        pid = f"p{i:03d}"
        pids.append(pid)
        files[f"{pid}.xhtml"] = xhtml(p["title"], passage_xhtml(p, pid), nav=True)
    nav_items = "".join(
        f'<li><a href="{pid}.xhtml">{e(p["range"])} · {e(p["title"])}</a></li>'
        for pid, p in zip(pids, passages)
    )
    files["nav.xhtml"] = xhtml("Contents", (
        '<nav epub:type="toc" id="toc"><h2>Contents</h2><ol>'
        '<li><a href="about.xhtml">About this translation</a></li>'
        f"{nav_items}</ol></nav>"
        '<nav epub:type="landmarks" hidden="hidden"><ol>'
        '<li><a epub:type="titlepage" href="title.xhtml">Title page</a></li>'
        '<li><a epub:type="toc" href="nav.xhtml">Contents</a></li>'
        f'<li><a epub:type="bodymatter" href="{pids[0]}.xhtml">Text</a></li></ol></nav>'
    ), nav=True)
    ncx_points = "".join(
        f'<navPoint id="n{i}" playOrder="{i}"><navLabel><text>{e(label)}</text></navLabel>'
        f'<content src="{src}"/></navPoint>'
        for i, (label, src) in enumerate(
            [("About this translation", "about.xhtml")]
            + [(f'{p["range"]} · {p["title"]}', f"{pid}.xhtml") for pid, p in zip(pids, passages)], 1)
    )
    files["toc.ncx"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head>'
        f'<meta name="dtb:uid" content="{book_id}"/></head>'
        f"<docTitle><text>{e(meta['title'])}</text></docTitle><navMap>{ncx_points}</navMap></ncx>\n"
    )
    order = ["title.xhtml", "nav.xhtml", "about.xhtml"] + [f"{pid}.xhtml" for pid in pids]
    manifest = ['<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
    for name in order:
        props = ' properties="nav"' if name == "nav.xhtml" else ""
        manifest.append(f'<item id="{name[:-6]}" href="{name}" media-type="application/xhtml+xml"{props}/>')
    spine = "".join(f'<itemref idref="{n[:-6]}"/>' for n in order)
    opf = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="bookid">{book_id}</dc:identifier>'
        f"<dc:title>{e(meta['title'])}</dc:title><dc:creator>{e(meta['author'])}</dc:creator>"
        f"<dc:language>en</dc:language><dc:publisher>{e(PUBLISHER)}</dc:publisher>"
        f"<dc:rights>{e(LICENSE)}</dc:rights>"
        + (f"<dc:description>{e(meta['blurb'])}</dc:description>" if meta["blurb"] else "")
        + f'<meta property="dcterms:modified">{modified}</meta></metadata>\n'
        f'<manifest>{"".join(manifest)}</manifest>\n<spine toc="ncx">{spine}</spine>\n</package>\n'
    )
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        "</rootfiles></container>\n"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        for name, text in files.items():
            z.writestr(f"OEBPS/{name}", text, compress_type=zipfile.ZIP_DEFLATED)


def check_epub(path: Path) -> list[str]:
    """Structural self-check used when epubcheck (Java) is not installed."""
    problems: list[str] = []
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        first = infos[0]
        if first.filename != "mimetype" or first.compress_type != zipfile.ZIP_STORED or first.extra:
            problems.append("mimetype must be the first entry, stored, with no extra field")
        elif z.read("mimetype") != b"application/epub+zip":
            problems.append("bad mimetype content")
        names = set(z.namelist())
        try:
            cont = minidom.parseString(z.read("META-INF/container.xml"))
            opf_path = cont.getElementsByTagName("rootfile")[0].getAttribute("full-path")
        except Exception as exc:  # noqa: BLE001
            return problems + [f"container.xml: {exc}"]
        base = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
        opf = minidom.parseString(z.read(opf_path))
        items = {i.getAttribute("id"): i for i in opf.getElementsByTagName("item")}
        hrefs = {base + i.getAttribute("href") for i in items.values()}
        for h in hrefs - names:
            problems.append(f"manifest file missing: {h}")
        for n in names - hrefs - {"mimetype", "META-INF/container.xml", opf_path}:
            problems.append(f"file not in manifest: {n}")
        for ref in opf.getElementsByTagName("itemref"):
            if ref.getAttribute("idref") not in items:
                problems.append(f"spine idref not in manifest: {ref.getAttribute('idref')}")
        if not [i for i in items.values() if "nav" in i.getAttribute("properties").split()]:
            problems.append("no nav document")
        if not opf.getElementsByTagName("meta") or not any(
            m.getAttribute("property") == "dcterms:modified" for m in opf.getElementsByTagName("meta")
        ):
            problems.append("missing dcterms:modified")
        for n in sorted(names):
            if n.endswith((".xhtml", ".ncx", ".opf", ".xml")):
                try:
                    doc = minidom.parseString(z.read(n))
                except Exception as exc:  # noqa: BLE001
                    problems.append(f"{n} not well-formed: {exc}")
                    continue
                for a in doc.getElementsByTagName("a"):
                    target = a.getAttribute("href").split("#")[0]
                    if target and not target.startswith("http") and base + target not in names:
                        problems.append(f"{n}: broken link {target}")
    return problems


# --- PDF via typst ---

TYPST_TEMPLATE = r"""
#let book-title = __TITLE__
#let book-author = __AUTHOR__
#set document(title: book-title, author: book-author)
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt, lang: "en", hyphenate: true, number-type: "old-style")
#set par(justify: true, leading: 0.6em, spacing: 0.6em, first-line-indent: 1.2em)
#set page(width: 6in, height: 9in, margin: (inside: 0.85in, outside: 0.7in, top: 0.85in, bottom: 0.85in), numbering: none)

#let secmark(m) = [#text(size: 0.68em, fill: luma(95), baseline: -0.2em, number-type: "lining")[§#m]#h(0.3em)]
#let passage-title(it) = text(style: "italic", it)
#show heading.where(level: 1): it => block(width: 100%, above: 0pt, below: 1.1em, sticky: true, {
  set align(center)
  set par(justify: false, first-line-indent: 0pt)
  set text(size: 13pt, weight: "regular", hyphenate: false)
  passage-title(it.body)
})
#let passage(rng, title) = {
  v(1.9em, weak: true)
  block(width: 100%, below: 0.45em, sticky: true, align(center, text(size: 7.5pt, tracking: 0.12em, fill: luma(90), number-type: "lining", rng)))
  heading(level: 1, supplement: rng, title)
}
#let p(mark, body) = par({ if mark != none { secmark(mark) }; body })
#set footnote.entry(separator: line(length: 25%, stroke: 0.4pt + luma(140)), gap: 0.35em)
#show footnote.entry: set text(size: 8pt)
#show footnote.entry: set par(first-line-indent: 0pt, justify: false)
#let supplied(body) = block(above: 0.8em, below: 0.8em, par(first-line-indent: 0pt, text(style: "italic", size: 9.5pt, body)))

// ---- title page ----
#align(center + horizon, {
  text(size: 9pt, tracking: 0.18em, upper(book-author))
  v(1.4em)
  text(size: 30pt, book-title)
  __SUBTITLE__
  v(1.2em)
  text(style: "italic", size: 11pt)[A new English translation for study]
})
#align(center + bottom, text(size: 9pt, tracking: 0.08em)[__PUBLISHER__ \ __SITEURL__])
#pagebreak()

// ---- about (verso) ----
#set par(first-line-indent: 0pt, justify: false, spacing: 0.9em)
#v(1fr)
#text(size: 11pt, style: "italic")[About this translation]
#v(0.6em)
#set text(size: 9pt, hyphenate: false)
__ABOUT__
#set text(size: 10.5pt)
#set par(first-line-indent: 1.2em, justify: true, spacing: 0.6em)
#pagebreak(to: "odd")

// ---- contents ----
#show outline.entry.where(level: 1): it => {
  set text(size: 9.5pt)
  block(above: 0.55em, link(it.element.location(), grid(columns: (2.6em, 1fr), gutter: 0pt,
    text(size: 7.5pt, fill: luma(90), number-type: "lining", baseline: -0.1em, it.element.supplement),
    it.inner())))
}
#outline(title: text(size: 13pt, style: "italic", weight: "regular")[Contents], depth: 1)
#pagebreak(to: "odd")

// ---- body ----
#counter(page).update(1)
#set page(numbering: "1", header: context {
  let pg = here().page()
  let here-heads = query(heading.where(level: 1)).filter(h => h.location().page() == pg)
  let before = query(heading.where(level: 1).before(here()))
  // A passage opening near the top already names itself: folio only.
  let opens-top = here-heads.any(h => h.location().position().y < 2.2in)
  let cur = if opens-top { none } else if here-heads.len() > 0 { here-heads.first().body } else if before.len() > 0 { before.last().body } else { none }
  let num = text(number-type: "lining", counter(page).display())
  set text(size: 8.5pt)
  if calc.even(pg) {
    grid(columns: (1fr, auto, 1fr), align(left, num), smallcaps(book-title), [])
  } else {
    grid(columns: (1fr, auto, 1fr), [], text(style: "italic", cur), align(right, num))
  }
}, footer: [])
__BODY__
"""


def tstr(s: str) -> str:
    s = re.sub(r"[\x00-\x08\x0b-\x1f]", " ", s)
    return json.dumps(s, ensure_ascii=False)


def build_pdf(meta: dict, passages: list[dict], dest: Path, typst: str) -> Path:
    body: list[str] = []
    for p in passages:
        body.append(f"#passage({tstr(p['range'])}, {tstr(p['title'])})")
        for s in p["sections"]:
            if s["supplied"]:
                body.append(f"#supplied({tstr(s['supplied'])})")
            for i, t in enumerate(s["paras"]):
                mark = tstr(s["mark"]) if i == 0 and p["multi"] else "none"
                notes = p.get("notes") or []
                content = "".join(
                    f"#{tstr(text)}" if n is None else f"#footnote({tstr(notes[n - 1])})"
                    for text, n in note_parts(t)
                )
                body.append(f"#p({mark}, [{content}])")
    about = [meta["blurb"]] if meta["blurb"] else []
    about += meta["about"]
    src = (TYPST_TEMPLATE
           .replace("__TITLE__", tstr(meta["title"]))
           .replace("__AUTHOR__", tstr(meta["author"]))
           .replace("__SUBTITLE__", f"v(0.5em); text(style: \"italic\", size: 12pt, {tstr(meta['subtitle'])})" if meta["subtitle"] else "")
           .replace("__PUBLISHER__", f"#{tstr(PUBLISHER)}")
           .replace("__SITEURL__", f"#{tstr(SITE_URL)}")
           .replace("__ABOUT__", "\n".join(f"#par({tstr(t)})" for t in about))
           .replace("__BODY__", "\n".join(body)))
    typ = dest.with_suffix(".typ")
    typ.write_text(src, encoding="utf-8")
    run = subprocess.run([typst, "compile", str(typ), str(dest)], capture_output=True, text=True)
    if run.returncode:
        raise SystemExit("typst failed:\n" + run.stderr[-3000:])
    if run.stderr.strip():
        print(run.stderr.strip()[-2000:], file=sys.stderr)
    return typ


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("slug", help="site work slug, e.g. origen-on-prayer")
    ap.add_argument("--out", required=True, type=Path, help="output dir (epub/ and pdf/ made inside)")
    ap.add_argument("--loader", help="build_site loader that returns the work (faster than scanning)")
    ap.add_argument("--typst", default=shutil.which("typst") or "/opt/homebrew/bin/typst")
    args = ap.parse_args()

    b = load_site()
    w = find_work(b, args.slug, args.loader)
    passages = build_passages(b, w)
    meta = edition_meta(b, w)
    print(f"{w['slug']}: {len(w['sections'])} sections -> {len(passages)} passages")

    epub = args.out / "epub" / f"{w['slug']}.epub"
    build_epub(meta, passages, epub)
    problems = check_epub(epub)
    print(f"EPUB {epub} ({epub.stat().st_size} bytes): " + ("structure OK" if not problems else "FAIL"))
    for prob in problems:
        print("  - " + prob)

    pdf = args.out / "pdf" / f"{w['slug']}.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(meta, passages, pdf, args.typst)
    print(f"PDF {pdf} ({pdf.stat().st_size} bytes)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
