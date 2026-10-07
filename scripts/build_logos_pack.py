#!/usr/bin/env python3
"""Zip the Logos books a person can upload themselves.

Each folder has the Word file, the series cover, and the description to paste
into Logos. A book stays out when it has no cover, no introduction, no Bible
links, or the Word file is much shorter than the page on the site. It also
stays out when the Word file fails verify_docx (worksheet notes such as
"True OET" or "Pass A"), leaves out its intro.md, or is older than its
English; rebuild it with build_pbb_docx.py --catchup. Only works
the site build published go in (--app-dir, required): the pack never carries
a withheld or retired work.

  python3 scripts/build_logos_pack.py --app-dir ~/SaneApps/websites/fathers.saneapps.com/dist/app/v1
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.book_meta import unquote_scalar  # noqa: E402
from pipeline.verify_docx import logos_file_problems  # noqa: E402
BOOKS = ROOT / "books"
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com/dist/works"
OUT = ROOT / "outputs" / "logos-share"
# Cloudflare Pages rejects a single file over 25 MB. Each part stays under this.
PART_LIMIT = 18 * 1024 * 1024
PART_HARD = 24 * 1024 * 1024

README = """These are Word files for Logos Bible Software.

Each folder is one book. To add it:

1. In Logos, open Tools, then Utilities, then Personal Books.
2. Add the Word file.
3. Attach cover.jpg.
4. Paste the text in description.txt into the description field.
5. Build the book.

The Word file is English. Scripture references are linked, so a click opens
the Bible in Logos. Translator notes are Headword articles.

New English translation, copyright 2026 SaneApps (CC BY 4.0). The source text
is public domain.

The same English is on https://viapatrum.org/works/
"""


def scalar(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return unquote_scalar(line.split(":", 1)[1])
    return ""


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text))


def site_words(slug: str) -> int:
    page = SITE / slug / "index.html"
    if not page.is_file():
        return 0
    html = page.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'<div class="reader">(.*)</div>', html, re.S)
    chunk = match.group(1) if match else ""
    return words(re.sub(r"<[^>]+>", " ", chunk))


def entry_cost(name: str, data: bytes) -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, data)
        info = archive.getinfo(name)
    name_n = len(name.encode("utf-8"))
    return info.compress_size + name_n * 2 + 160


def readme(part: int, total: int) -> str:
    return (
        "These are Word files for Logos Bible Software.\n"
        f"This is part {part} of {total}. Download every part.\n"
        "The list of parts is at https://viapatrum.org/logos/\n\n"
        + README.split("\n", 1)[1]
    )


def safe(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', " ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:80] or "book"


def word_file_problems(book: Path, docx: Path) -> list[str]:
    """Reasons this Word file must not go in the pack (empty when it may).

    The one shared rule (verify_docx.logos_file_problems) that the builder,
    the Sunday driver and pb_sync also apply: verify_docx (worksheet notes),
    plus a file older than its English or without its intro.md.
    """
    return logos_file_problems(book, docx)


def published_slugs(app_dir: Path) -> set[str]:
    """Slugs the site build published, from its app export catalogue."""
    try:
        works = json.loads((app_dir / "catalog.json").read_text(encoding="utf-8")).get("works") or []
    except (OSError, json.JSONDecodeError):
        works = []
    slugs = {w["slug"] for w in works if w.get("slug")}
    if not slugs:
        raise SystemExit(f"BLOCKED: no site catalogue at {app_dir}/catalog.json")
    return slugs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app-dir", required=True, type=Path,
                    help="the site build's app export (catalog.json lists the published works)")
    published = published_slugs(ap.parse_args().app_dir.expanduser())
    excluded = []
    used: set[str] = set()
    gathered: list[dict] = []

    for book in sorted(BOOKS.iterdir()):
        if not book.is_dir() or not (book / "book.yml").is_file():
            continue
        yml = (book / "book.yml").read_text(encoding="utf-8", errors="replace")
        slug = book.name
        if slug not in published:
            excluded.append({"slug": slug, "why": "not published on the site"})
            continue
        named = scalar(yml, "docx") or f"{slug}.docx"
        docx = book / named
        if not docx.is_file():
            continue
        cover = next((p for p in (book / "assets" / "cover.jpg", book / "assets" / "cover.png") if p.is_file()), None)
        intro = (book / "intro.md").is_file()
        try:
            xml = zipfile.ZipFile(docx).read("word/document.xml").decode("utf-8", "replace")
        except Exception as exc:
            excluded.append({"slug": slug, "why": f"unreadable: {exc}"})
            continue
        links = xml.count("&gt;&gt; Bible:") + xml.count(">> Bible:")
        docx_words = words(re.sub(r"<[^>]+>", " ", xml))
        live = site_words(slug)
        ratio = (docx_words / live) if live else 0
        why = []
        if cover is None:
            why.append("no cover")
        if not intro:
            why.append("no introduction")
        if links <= 0:
            why.append("no Bible links")
        if live and ratio < 0.6:
            why.append(f"shorter than the site ({ratio:.2f})")
        why.extend(word_file_problems(book, docx))
        if why:
            excluded.append({"slug": slug, "why": ", ".join(why)})
            continue
        author = scalar(yml, "author") or "Unknown"
        title = scalar(yml, "title") or slug
        edition = scalar(yml, "edition")
        desc = scalar(yml, "description")
        if not desc:
            desc = f"{author}, {title}. New English for private study."
            if edition:
                desc += f" Source: {edition}."
        extra = []
        if "Bible" not in desc:
            extra.append("Bible quotations in the Word file are linked and open in Logos.")
        site = f"https://viapatrum.org/works/{slug}/"
        if site not in desc:
            extra.append(f"The same English is on the site: {site}")
        if extra:
            desc = desc.rstrip() + " " + " ".join(extra)
        folder = safe(f"{author} - {title}")
        if folder in used:
            folder = safe(f"{folder} - {slug}")
        used.add(folder)
        files = [
            (f"{folder}/description.txt", desc.encode() + b"\n"),
            (f"{folder}/cover{cover.suffix}", cover.read_bytes()),
            (f"{folder}/{safe(title)}.docx", docx.read_bytes()),
        ]
        gathered.append({
            "slug": slug,
            "author": author,
            "title": title,
            "folder": folder,
            "bible_links": links,
            "site": site,
            "files": files,
        })

    # One folder must fit in a part. A book that cannot is held, not squeezed in.
    books = []
    for row in gathered:
        files = row["files"]
        cost = sum(entry_cost(name, data) for name, data in files)
        if cost + 12000 > PART_LIMIT:
            excluded.append({"slug": row["slug"], "why": "larger than one download part"})
            continue
        books.append({**row, "files": files, "cost": cost})
    books.sort(key=lambda row: (row["author"].lower(), row["title"].lower(), row["slug"]))

    parts: list[list[dict]] = []
    current: list[dict] = []
    current_cost = 0
    for book in books:
        if current and current_cost + book["cost"] + 12000 > PART_LIMIT:
            parts.append(current)
            current = []
            current_cost = 0
        current.append(book)
        current_cost += book["cost"]
    if current:
        parts.append(current)

    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for index, group in enumerate(parts, start=1):
        lines = [f"Books in part {index} of {len(parts)}", ""]
        blob: list[tuple[str, bytes]] = [
            ("README.txt", readme(index, len(parts)).encode()),
        ]
        for book in group:
            lines.append(f"{book['author']}: {book['title']}")
            lines.append(f"  {book['site']}")
            blob.extend(book["files"])
            book["part"] = index
        blob.append(("INDEX.txt", ("\n".join(lines) + "\n").encode()))
        name = f"fathers-personal-books-{index}.zip"
        dest = OUT / name
        tmp = dest.with_suffix(".zip.tmp")
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for arc, data in blob:
                archive.writestr(arc, data)
        size = tmp.stat().st_size
        if size > PART_HARD:
            tmp.unlink(missing_ok=True)
            raise SystemExit(f"{name} is {size} bytes, over the 24 MB cap")
        tmp.replace(dest)
        written.append({"file": name, "bytes": size, "books": len(group)})
        print(f"part {index}: {len(group)} books, {size} bytes", flush=True)

    included_out = []
    for book in books:
        included_out.append({k: v for k, v in book.items() if k not in ("files", "cost")})
    manifest = {
        "parts": written,
        "bytes": sum(part["bytes"] for part in written),
        "included": included_out,
        "excluded": excluded,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"included {len(included_out)} excluded {len(excluded)} "
        f"parts {len(written)} bytes {manifest['bytes']}"
    )
    for row in excluded:
        print(f"HOLD {row['slug']}: {row['why']}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
