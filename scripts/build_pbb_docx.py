#!/usr/bin/env python3
"""Build one Logos Personal-Book DOCX from a book's english JSON.

Covers the per-slice layout (sorted translations/*_source.json with
*_english.json siblings, e.g. cyril-alexandria-isaiah). Other layouts
refuse; extend the reader when the next book needs it.

Markup follows docs/LOGOS_MARKUP.md:
  Title/Subtitle cover from book.yml (never hardcoded strings)
  Heading 1 per slice file, Heading 2 per section
  [[@Headword:...]] milestones as standalone paragraphs
  english paragraphs with [[... >> Bible:...]] via BibleLinker receipts
  translator notes as Headword TN marks + TN articles (no Word footnotes)

The verify_docx gate runs before the final path is written: a failing
build never lands. Zero Bible links is the honest hold, not an error
to pad around.

Usage:
  python3 scripts/build_pbb_docx.py --book cyril-alexandria-isaiah \\
      --out books/cyril-alexandria-isaiah/cyril-isaiah.docx [--sections a,b]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from pipeline.bible_links import BibleLinker  # noqa: E402
from pipeline.book_meta import load_book_meta  # noqa: E402
from pipeline.docx_helpers import setup_document  # noqa: E402
from pipeline.verify_docx import verify_docx  # noqa: E402

_SUPER = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

PENDING_ENGLISH = "[English pending.]"

_SCAFFOLD_LEADS = (
    re.compile(r"Rem (?:early|mid|CLOSEOUT):"),
    re.compile(r"Lemma-led\b"),
    re.compile(r"ZU [A-Z]{2,}"),
)


# Production notes travel with the English JSON. A Logos reader should not
# get "True OET", copy-text lines, or the stock "may be fragmented" remark.
_NOTE_BOILER = (
    "true oet",
    "pass a ≠",
    "pass a !=",
    "copy-text:",
    "mcenerney",
    "melito skipped",
    "earliest-forward",
    "condensed lemma-led",
    "the greek text may be fragmented",
    "the source text may be fragmented",
    "the text appears to be a fragment",
    "the translation aims to preserve",
    "the translation tries to follow",
    "the translation tries to provide",
    "some sentences may be cut off",
    "no obvious ocr",
    "no edition headers",
    "no untranslatable",
    "no invented text",
    "all supplied greek",
    "the chunked source may begin",
    "never cyril matthew",
    "skip pusey",
    "khazarzar research-footer",
    "real khazarzar file",
    "densify-lane",
    "corpus-wide rank-1",
    "series closeout",
    "machine draft",
    "tip-checked",
    "appears to be a fragment",
    "may be a fragment",
    "based on the editor's note",
    "ocr debris",
    "no preceding context",
    "no clear terminal punctuation",
)


def _reader_note(note: str) -> str:
    """Return a translator note worth printing, or empty when it is shop talk."""
    text = " ".join(str(note).split())
    if not text:
        return ""
    low = text.lower()
    if any(mark in low for mark in _NOTE_BOILER):
        return ""
    return text


def is_scaffold_english(paras) -> bool:
    """True when the row is untranslated scaffold, not content.

    Rem/Lemma/ZU scaffold rows carry working labels as their English text;
    shipping them paints labels as translation (cyril-isaiah.docx Sep 2026).
    """
    for para in paras or []:
        text = str(para).strip()
        if not text:
            continue
        return any(rx.match(text) for rx in _SCAFFOLD_LEADS)
    return False


def _slice_title(stem: str) -> str:
    short = stem[7:] if stem.startswith("isaiah_") else stem
    return short.replace("_", " ").replace("-", " ").strip().title() or stem


# Unit codes (u01, rem, open) are file names, not part titles. A Heading 1
# of "Ail U01 Open" would show up in the Logos contents as the work's name.
_CODE_SLICE = re.compile(
    r"(?:^|_)(?:u\d+|open|rem|early|mid|close)(?:_|$)", re.I)


def _slice_heading(stem: str) -> str | None:
    if stem.startswith("isaiah_"):
        return _slice_title(stem)
    if _CODE_SLICE.search(stem):
        return None
    return _slice_title(stem)


def _plain_heading(title: str) -> str:
    """A heading must not contain a nested Bible or Headword marker.

    A title once read "Virgin birth and [[God with us >> Bible:Matthew 1:23]]".
    Wrapping that string as a Headword made a marker inside a marker, and the
    build was refused.
    """
    text = re.sub(
        r"\[\[([^\[\]]+?)(?:\s*>>\s*[^\[\]]+)?\]\]",
        lambda match: match.group(1).strip(),
        str(title),
    )
    return re.sub(r"\s+", " ", text).strip()


def _part_already_in_whole(src: Path) -> bool:
    """Skip a ranged tip file when the whole homily beside it already has that English.

    The site ships exod_hom6 and skips exod_hom6_1_7 and exod_hom6_8_14.
    Those two files repeat the song. A Logos book should not print it twice.
    """
    stem = src.name[: -len("_source.json")]
    match = re.fullmatch(r"(.+)_\d+_\d+", stem)
    if not match:
        return False
    whole_path = src.with_name(match.group(1) + "_english.json")
    part_path = src.with_name(stem + "_english.json")
    if not whole_path.is_file() or not part_path.is_file():
        return False

    def paras(path: Path) -> set[str]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return set()
        rows = data if isinstance(data, list) else [data]
        out: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            for line in row.get("english") or []:
                text = str(line).strip()
                if text:
                    out.add(text)
        return out

    part_paras = paras(part_path)
    return bool(part_paras) and part_paras <= paras(whole_path)


def _wants_english_tail(book_dir: Path) -> bool:
    path = book_dir / "book.yml"
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("logos_english_tail:"):
            continue
        value = line.split(":", 1)[1].strip().strip('"').strip("'").lower()
        return value in ("true", "yes", "1")
    return False


def collect_sections(book_dir: Path, only: set[str] | None) -> list[dict]:
    trans = book_dir / "translations"
    sources = sorted(trans.glob("*_source.json"))
    if not sources:
        raise SystemExit(f"No per-slice source layout under {trans}; refusing")
    sections = []
    for src in sources:
        if _part_already_in_whole(src):
            continue
        eng_path = src.with_name(src.name.replace("_source.json", "_english.json"))
        if not eng_path.is_file():
            raise SystemExit(f"Missing english sibling for {src.name}; refusing")
        src_rows = json.loads(src.read_text(encoding="utf-8"))
        eng_rows = json.loads(eng_path.read_text(encoding="utf-8"))
        src_rows = src_rows if isinstance(src_rows, list) else [src_rows]
        eng_rows = eng_rows if isinstance(eng_rows, list) else [eng_rows]
        for i, srow in enumerate(src_rows):
            section = str(srow.get("section") or "")
            if only is not None and section not in only:
                continue
            erow = eng_rows[i] if i < len(eng_rows) else {}
            english = list(erow.get("english") or [])
            if is_scaffold_english(english):
                english = [PENDING_ENGLISH]
            sections.append({
                "slice": src.stem.replace("_source", ""),
                "section": section,
                "title": str(erow.get("title") or srow.get("head") or section),
                "english": english,
                "translator_notes": list(erow.get("translator_notes") or []),
            })
        # Some books lock a short source file and keep the rest of the English
        # beside it. The site already shows that English. Opt in with
        # logos_english_tail: true. Do not invent source rows.
        if _wants_english_tail(book_dir) and len(eng_rows) > len(src_rows):
            slice_name = src.stem.replace("_source", "")
            for erow in eng_rows[len(src_rows):]:
                if not isinstance(erow, dict):
                    continue
                section = str(erow.get("section") or "")
                if only is not None and section not in only:
                    continue
                english = list(erow.get("english") or [])
                if is_scaffold_english(english):
                    english = [PENDING_ENGLISH]
                sections.append({
                    "slice": slice_name,
                    "section": section,
                    "title": str(erow.get("title") or section),
                    "english": english,
                    "translator_notes": list(erow.get("translator_notes") or []),
                })
    if only:
        missing = only - {s["section"] for s in sections}
        if missing:
            raise SystemExit(f"Unknown sections: {sorted(missing)}")
    if not sections:
        raise SystemExit("No sections collected; refusing to build an empty book")
    return sections


def build_docx(book: str, out: Path, only: set[str] | None) -> dict:
    book_dir = ROOT / "books" / book
    meta = load_book_meta(book_dir)
    sections = collect_sections(book_dir, only)
    _drop_raw = str(meta.get("logos_drop_titles") or "").strip()
    # load_book_meta returns strings; accept ["a", "b"] or a bare title.
    if _drop_raw.startswith("["):
        _drop_raw = _drop_raw[1:]
    if _drop_raw.endswith("]"):
        _drop_raw = _drop_raw[:-1]
    drop = {t.strip().strip(chr(34)).strip(chr(39)) for t in _drop_raw.split(",") if t.strip()}
    if drop:
        sections = [s for s in sections if s["title"] not in drop]
    # Scaffold and "[English pending.]" stay out of the Logos book. The
    # website can still list a work; Logos gets only the reading text.
    readable = []
    for item in sections:
        paras = [str(p) for p in (item["english"] or []) if str(p).strip()
                 and str(p).strip() != PENDING_ENGLISH]
        if paras:
            readable.append({**item, "english": paras})
    if not readable:
        raise SystemExit("No translated sections; refusing to build a scaffold book")
    sections = readable
    linker = BibleLinker()
    doc = setup_document(
        title=meta["title"],
        author=meta["author"],
        subject=meta.get("edition", ""),
        keywords=meta.get("slug", book),
        # OOXML core properties cap at 255 chars; keep the full text on the cover page.
        comments=(lambda s: s if len(s) <= 252 else s[:252] + "…")(
            str(meta.get("logos_blurb") or meta.get("blurb") or meta.get("description", ""))),
    )
    doc.add_paragraph(meta["title"], style="Title")
    doc.add_paragraph(meta["author"], style="Subtitle")
    if meta.get("edition"):
        doc.add_paragraph(str(meta["edition"]), style="Subtitle")
    if meta.get("logos_intro") and (book_dir / "intro.md").is_file():
        doc.add_heading("Introduction", level=1)
        intro_text = (book_dir / "intro.md").read_text(encoding="utf-8").strip()
        for para in intro_text.split("\n\n"):
            if para.strip():
                doc.add_paragraph(para.strip())

    tn_counter = 0
    tn_articles: list[tuple[int, str]] = []
    last_heading = None
    for item in sections:
        heading = _slice_heading(item["slice"])
        if heading and heading != last_heading:
            doc.add_heading(heading, level=1)
            last_heading = heading
        title = _plain_heading(item["title"]) or str(item["section"])
        headword = f"{title} ({item['section']})"
        doc.add_heading(title, level=2)
        doc.add_paragraph(f"[[@Headword:{headword}]]")
        paras = item["english"] or ["[English pending.]"]
        for para in paras:
            linked = linker.bible_text(str(para), key=item["section"], label=item["title"])
            doc.add_paragraph(linked)
        for note in item["translator_notes"]:
            text = _reader_note(note)
            if not text:
                continue
            tn_counter += 1
            mark = str(tn_counter).translate(_SUPER)
            doc.add_paragraph(f"[[{mark} >> Headword:TN {tn_counter}]]")
            tn_articles.append((tn_counter, text))
    if tn_articles:
        doc.add_heading("Translator Notes", level=1)
        for num, text in tn_articles:
            doc.add_heading(f"TN {num}", level=3)
            doc.add_paragraph(f"[[@Headword:TN {num}]]")
            doc.add_paragraph(text)

    tmp = out.with_name(out.name + ".tmp")
    doc.save(str(tmp))
    errors = verify_docx(tmp)
    if errors:
        tmp.unlink(missing_ok=True)
        raise SystemExit("verify_docx refused the build:\n- " + "\n- ".join(errors))
    if out.is_file():
        old_n, new_n = _docx_chars(out), _docx_chars(tmp)
        # A certified slice must not replace a longer book already on the shelf.
        if old_n > 8000 and new_n < old_n * 0.5:
            tmp.unlink(missing_ok=True)
            raise SystemExit(
                f"refusing to shrink {out.name}: {old_n} chars -> {new_n}")
    tmp.replace(out)
    return {
        "out": str(out),
        "sections": len(sections),
        "bible_links": len(linker.link_receipts),
        "tn_notes": len(tn_articles),
    }


def _docx_chars(path: Path) -> int:
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    return sum(len("".join(node.text or "" for node in para.iter(ns + "t")))
               for para in root.iter(ns + "p"))


def _yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _set_scalar(text: str, key: str, value: str) -> str:
    """Set one top-level scalar, leaving block values and other keys alone."""
    line = f"{key}: {_yaml_quote(value)}"
    pattern = re.compile(rf"(?m)^{re.escape(key)}:.*$")
    if pattern.search(text):
        return pattern.sub(line, text, count=1)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def _has_resource_id(text: str) -> bool:
    return bool(re.search(r'(?m)^resource_id:\s*"?PBB:', text))


def _scalar(text: str, key: str) -> str:
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", text)
    if not m:
        return ""
    raw = m.group(1).strip()
    if raw in ("|", ">", ""):
        return ""
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    return raw


def prepare_book_yml(slug: str, title_en: str) -> list[str]:
    """Point a passing book at its DOCX and use the website's English title.

    Books already compiled (resource_id set) keep their Logos title so a
    rebuild updates the body without inserting a second library row.
    """
    path = ROOT / "books" / slug / "book.yml"
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []
    if title_en and not _has_resource_id(text):
        current = _scalar(text, "title")
        if current and current != title_en:
            if not _scalar(text, "original_title"):
                text = _set_scalar(text, "original_title", current)
            text = _set_scalar(text, "title", title_en)
            notes.append(f"title {current!r} -> {title_en!r}")
    if not _scalar(text, "docx"):
        text = _set_scalar(text, "docx", f"{slug}.docx")
        notes.append("docx")
    if not _scalar(text, "pb_type"):
        text = _set_scalar(text, "pb_type", "text.monograph.ancient.manuscript.translation")
        notes.append("pb_type")
    if not _scalar(text, "copyright"):
        text = _set_scalar(
            text, "copyright",
            "New English translation © 2026 SaneApps (CC BY 4.0); source text public domain.")
        notes.append("copyright")
    if (ROOT / "books" / slug / "intro.md").is_file() and not _scalar(text, "logos_intro"):
        text = _set_scalar(text, "logos_intro", "true")
        notes.append("logos_intro")
    if not _scalar(text, "description"):
        author = _scalar(text, "author") or title_en
        title = _scalar(text, "title") or title_en
        edition = _scalar(text, "edition")
        desc = f"{author}, {title}. New English for private study from the locked source."
        if edition:
            desc += f" Source: {edition}."
        text = _set_scalar(text, "description", desc[:500])
        notes.append("description")
    path.write_text(text, encoding="utf-8")
    return notes


def catchup() -> int:
    """Build Logos DOCX for certified works that already pass the research gate.

    A DOCX named in book.yml is checked by check_research.py before any
    Logos build or site ship. Books missing a sourced intro stay off the
    shelf rather than failing that gate.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "check_research", ROOT / "scripts" / "check_research.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    queue = json.loads((ROOT / "outputs/work-pipeline/queue.json").read_text())
    dates_path = Path.home() / "SaneApps/websites/fathers.saneapps.com/data/author-dates.json"
    dates = json.loads(dates_path.read_text(encoding="utf-8")) if dates_path.is_file() else {}
    built, skipped, failed = [], [], []
    for slug in sorted(k for k, v in queue.items() if v.get("result") == "certified"):
        cr.ERRORS.clear()
        yml_path = ROOT / "books" / slug / "book.yml"
        if not yml_path.is_file():
            skipped.append((slug, "no book.yml"))
            continue
        named = _scalar(yml_path.read_text(encoding="utf-8"), "docx")
        existing = ROOT / "books" / slug / (named or f"{slug}.docx")
        if existing.is_file():
            # Leave an existing file alone. A later catchup must not overwrite it.
            skipped.append((slug, "docx already present"))
            continue
        brief_path = ROOT / "books" / slug / "work_brief.json"
        title_en = ""
        if brief_path.is_file():
            try:
                title_en = str(json.loads(brief_path.read_text(encoding="utf-8")).get("title_en") or "").strip()
            except (OSError, ValueError):
                title_en = ""
        yml = cr.load_yml(str(yml_path))
        intro = cr.check_intro(slug)
        data = cr.check_research(slug)
        cr.check_years(slug, intro, data, yml, dates)
        cr.check_author_dates(slug, intro, yml, dates)
        if cr.ERRORS:
            skipped.append((slug, cr.ERRORS[0]))
            continue
        original = yml_path.read_text(encoding="utf-8")
        try:
            notes = prepare_book_yml(slug, title_en)
            cr.ERRORS.clear()
            yml = cr.load_yml(str(yml_path))
            cr.check_years(slug, intro, data, yml, dates)
            cr.check_author_dates(slug, intro, yml, dates)
            if cr.ERRORS:
                yml_path.write_text(original, encoding="utf-8")
                skipped.append((slug, cr.ERRORS[0]))
                continue
            out = ROOT / "books" / slug / f"{slug}.docx"
            # Honor an existing docx name if prepare left one in place.
            named = _scalar(yml_path.read_text(encoding="utf-8"), "docx")
            if named:
                out = ROOT / "books" / slug / named
            receipt = build_docx(slug, out, None)
        except (SystemExit, ValueError, OSError) as exc:
            yml_path.write_text(original, encoding="utf-8")
            failed.append((slug, str(exc)))
            print(f"FAIL {slug}: {exc}", flush=True)
            continue
        built.append({
            "slug": slug,
            "sections": receipt["sections"],
            "bible_links": receipt["bible_links"],
            "meta": notes,
        })
        print(f"BUILT {slug}: {receipt['sections']} sections, "
              f"{receipt['bible_links']} Bible links ({', '.join(notes) or 'body only'})",
              flush=True)
    stamp = ROOT / "outputs" / "logos-catchup"
    stamp.mkdir(parents=True, exist_ok=True)
    out_path = stamp / "latest.json"
    out_path.write_text(json.dumps({
        "built": built, "skipped": skipped, "failed": failed,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"catchup built={len(built)} skipped={len(skipped)} failed={len(failed)} -> {out_path}",
          flush=True)
    return 1 if failed else 0


def _site_words() -> dict[str, int]:
    """Reader-column word counts from the built site, when it is on disk."""
    import html as html_mod
    root = Path.home() / "SaneApps/websites/fathers.saneapps.com/dist/works"
    out: dict[str, int] = {}
    if not root.is_dir():
        return out
    for page in root.glob("*/index.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'<div class="reader">(.*)</main>', text, re.S)
        chunk = match.group(1) if match else ""
        chunk = re.sub(r"<script.*?</script>|<style>.*?</style>", " ", chunk, flags=re.S)
        chunk = re.sub(r"<[^>]+>", " ", chunk)
        chunk = html_mod.unescape(chunk)
        out[page.parent.name] = len(re.findall(r"[A-Za-z']+", chunk))
    return out


def _paint_cover(slug: str) -> None:
    """Series cover, when the Swift painter is already built."""
    painter = Path("/tmp/logos_cover")
    if not painter.is_file():
        return
    assets = ROOT / "books" / slug / "assets"
    if (assets / "cover.jpg").is_file() or (assets / "cover.png").is_file():
        return
    text = (ROOT / "books" / slug / "book.yml").read_text(encoding="utf-8")
    author = _scalar(text, "author")
    title = _scalar(text, "title")
    subtitle = _scalar(text, "original_title")
    if not subtitle or subtitle == title or len(subtitle) > 80 or title.lower() in subtitle.lower():
        subtitle = ""
    assets.mkdir(parents=True, exist_ok=True)
    job = assets / ".cover-job.json"
    job.write_text(json.dumps([{
        "out": str((assets / "cover.jpg").resolve()),
        "author": author,
        "title": title,
        "subtitle": subtitle,
    }]), encoding="utf-8")
    subprocess_run = __import__("subprocess").run
    subprocess_run([str(painter), str(job)], check=False)
    job.unlink(missing_ok=True)


def shelf(limit: int) -> int:
    """Source an introduction, then build a Logos DOCX, for works that already have English.

    Uses work_pipeline.py intro, which web-sources the background facts and
    checks every intro sentence. A book a lane is translating is left alone.
    An existing DOCX is left alone.
    """
    import subprocess

    queue = json.loads((ROOT / "outputs/work-pipeline/queue.json").read_text(encoding="utf-8"))
    running = {slug for slug, row in queue.items() if row.get("result") == "running"}
    words = _site_words()
    # verify_docx already refused these. The English cites no Scripture,
    # or the only English is a scaffold label. Leave them off the shelf.
    # Do not invent Bible links. A real abbreviation such as "1 Cor 1:10"
    # is linked, so it is not a reason to stay on this list.
    no_link = {
        "origen-proverbs-expositio",
        "minucius-felix-octavius",
        "clement-alexandria-newly-baptized",
        "cyril-alexandria-fragmentum-papyraceum",
        "cyril-alexandria-sermo-trium-puerorum",
        "epiphanius-testamentum-ad-cives",
        "eustathius-de-anima-contra-philosophos",
        "eustathius-oratio-psalmorum-graduum",
        "evagrius-capitula-xxxiii",
        "gregory-thaumaturgus-ad-tatianum-de-anima",
        "irenaeus-letter-victor",
        "tertullian-to-scapula",
        "severianus-in-job",
        "origen-lamentationes-fragments",
        "epiphanius-homilia-in-divini-corporis-sepulturam",
        "severianus-in-illud-quando",
        "epiphanius-de-prophetarum-vita-et-obitu",
        "epiphanius-homilia-in-laudes-mariae-deiparae",
        "epiphanius-liturgia-praesanctificatorum",
        "epiphanius-homilia-in-christi-resurrectionem",
        "epiphanius-de-prophetarum-vita-et-obitu-recensio-altera",

        "epiphanius-homilia-in-festo-palmarum",
        "photius-bibliotheca",
        "severianus-in-genesim",
        "epiphanius-homilia-in-assumptionem-christi",
        # Linker found no Bible datatype links in the English. Do not invent any.
        "epiphanius-de-xii-gemmis",
        "epiphanius-index-apostolorum",
        "epiphanius-notitiae-episcopatuum",
        "severianus-fragmenta-2thess",
        "epiphanius-index-discipulorum",
        "epiphanius-epistula-ad-eusebium",
        "acts-of-justin",
        "epiphanius-de-xii-gemmis-fragmenta",
        "epiphanius-apophthegmata",
        "evagrius-spiritales-sententiae",
        "dionysius-corinth-fragments",
        "epiphanius-appendices-ad-indices-apostolorum-discipulorumque",
        "epiphanius-epistula-ad-theodosium-imperatorem",
        "eustathius-allocutio-constantinum",
        "severianus-fragmentum-philemonem",
        "eustathius-in-proverbia",
        "epiphanius-enumeratio-lxxii-prophetarum-et-prophetissarum",
        "origen-hebrews-homily-scrap",
        "photius-fragmentum-philemonem",
        "photius-epigramma",
        "gregory-thaumaturgus-ouden-eidolon",
    }
    # Catalogue title and the English are different works. Do not ship the mismatch.
    # hesychius-homilia-i-lazarum: site title is Homily I on Saint Lazarus, but the
    # Greek incipit is the homily on James and David (Ἀνεγνώσθη … εἰς Ἰάκωβον … καὶ Δαυίδ).
    identity_hold = {
        "hesychius-homilia-i-lazarum",
        # Labeled Scholia in Apocalypsem. The English is the Pantainos and Heraclas
        # training notice and never mentions the Apocalypse.
        "origen-apocalypse-scholia-scrap",
    }
    dates_path = Path.home() / "SaneApps/websites/fathers.saneapps.com/data/author-dates.json"
    author_dates = json.loads(dates_path.read_text(encoding="utf-8"))

    def author_is_dated(author: str) -> bool:
        # Same match as check_research.check_author_dates. A miss there is a hard skip.
        want = re.sub(r"[^a-z0-9]", "", author.lower())
        if not want:
            return False
        for key in author_dates:
            key_n = re.sub(r"[^a-z0-9]", "", key.lower())
            if key_n == want or key_n.startswith(want) or want.startswith(key_n):
                return True
        return False

    def has_usable_english(book: Path) -> bool:
        pending = "[English pending.]"
        for path in (book / "translations").glob("*_english.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            rows = data if isinstance(data, list) else [data]
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for line in row.get("english") or []:
                    text = str(line).strip()
                    if text and text != pending:
                        return True
        return False

    linker = BibleLinker()

    def build_would_refuse(book: Path) -> bool:
        # The same checks verify_docx enforces: a scaffold label must not ship,
        # and a book with no Bible datatype link stays out. Do this before an intro.
        try:
            sections = collect_sections(book, None)
        except SystemExit:
            return True
        links = 0
        for item in sections:
            paras = [str(p) for p in (item["english"] or [])
                     if str(p).strip() and str(p).strip() != PENDING_ENGLISH]
            for para in paras:
                text = para.strip()
                if any(rx.match(text) for rx in _SCAFFOLD_LEADS):
                    return True
                linked = linker.bible_text(text, key=item["section"], label=str(item["title"]))
                if ">> Bible:" in linked:
                    links += 1
        return links == 0

    ranked: list[tuple[int, str]] = []
    undated = 0
    empty_english = 0
    refused = 0
    for book in sorted((ROOT / "books").iterdir()):
        if not book.is_dir() or not (book / "book.yml").is_file():
            continue
        slug = book.name
        if slug in running or slug in no_link or slug in identity_hold:
            continue
        if (book / f"{slug}.docx").is_file():
            continue
        if not list((book / "translations").glob("*_english.json")):
            continue
        try:
            meta = load_book_meta(book)
        except ValueError:
            continue
        named = (meta.get("docx") or "").strip()
        if named and (book / named).is_file():
            continue
        if not author_is_dated(meta.get("author") or ""):
            undated += 1
            continue
        if not has_usable_english(book):
            empty_english += 1
            continue
        if build_would_refuse(book):
            refused += 1
            continue
        ranked.append((words.get(slug, 0), slug))
    ranked.sort(reverse=True)
    chosen = [slug for _, slug in ranked[:limit]]
    print(f"shelf: {len(chosen)} of {len(ranked)} works ready for a Logos file "
          f"({undated} undated, {empty_english} empty English, {refused} no Bible link or scaffold)",
          flush=True)
    built = failed = 0
    for slug in chosen:
        print(f"INTRO {slug}", flush=True)
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "work_pipeline.py"), "intro", "--slug", slug],
            cwd=ROOT,
        )
        if proc.returncode != 0:
            failed += 1
            print(f"SKIP {slug}: intro exit {proc.returncode}", flush=True)
            continue
        yml_path = ROOT / "books" / slug / "book.yml"
        original = yml_path.read_text(encoding="utf-8")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "check_research", ROOT / "scripts" / "check_research.py")
            cr = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cr)
            dates_path = Path.home() / "SaneApps/websites/fathers.saneapps.com/data/author-dates.json"
            dates = json.loads(dates_path.read_text(encoding="utf-8"))
            brief_path = ROOT / "books" / slug / "work_brief.json"
            title_en = ""
            if brief_path.is_file():
                title_en = str(json.loads(brief_path.read_text(encoding="utf-8")).get("title_en") or "").strip()
            page = Path.home() / f"SaneApps/websites/fathers.saneapps.com/dist/works/{slug}/index.html"
            if page.is_file():
                import html as html_mod
                found = re.search(r"<h1>(.*?)</h1>", page.read_text(encoding="utf-8", errors="replace"))
                if found:
                    title_en = html_mod.unescape(found.group(1)).strip() or title_en
            cr.ERRORS.clear()
            notes = prepare_book_yml(slug, title_en)
            yml = cr.load_yml(str(yml_path))
            intro = cr.check_intro(slug)
            data = cr.check_research(slug)
            cr.check_years(slug, intro, data, yml, dates)
            cr.check_author_dates(slug, intro, yml, dates)
            if cr.ERRORS:
                yml_path.write_text(original, encoding="utf-8")
                failed += 1
                print(f"SKIP {slug}: {cr.ERRORS[0]}", flush=True)
                continue
            out = ROOT / "books" / slug / f"{slug}.docx"
            receipt = build_docx(slug, out, None)
        except (SystemExit, ValueError, OSError) as exc:
            yml_path.write_text(original, encoding="utf-8")
            failed += 1
            print(f"FAIL {slug}: {exc}", flush=True)
            continue
        built += 1
        _paint_cover(slug)
        print(f"BUILT {slug}: {receipt['sections']} sections, {receipt['bible_links']} links "
              f"({', '.join(notes)})", flush=True)
    print(f"shelf built={built} failed={failed}", flush=True)
    return 1 if built == 0 else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--sections", default="")
    ap.add_argument("--catchup", action="store_true",
                    help="build DOCX for certified works that pass the research gate")
    ap.add_argument("--shelf", action="store_true",
                    help="source intros and build DOCX for works that already have English")
    ap.add_argument("--limit", type=int, default=10, help="with --shelf, how many works")
    args = ap.parse_args()
    if args.catchup:
        return catchup()
    if args.shelf:
        return shelf(args.limit)
    if not args.book or not args.out:
        ap.error("--book and --out are required unless --catchup")
    only = {s.strip() for s in args.sections.split(",") if s.strip()} or None
    try:
        receipt = build_docx(args.book, Path(args.out), only)
    except (SystemExit, ValueError) as exc:
        print(f"build_pbb_docx: {exc}", flush=True)
        return 1
    print(f"Built {receipt['out']}: "
          f"{receipt['sections']} sections, "
          f"{receipt['bible_links']} Bible links, "
          f"{receipt['tn_notes']} TN notes", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
