"""Encyclopedia builder: Ante-Nicene Dogmatics (one book, full systematic map)."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from pipeline.bible_links import REF, BibleLinker, sort_ref_key  # noqa: E402
from pipeline.docx_helpers import (  # noqa: E402
    BookmarkStore,
    assert_internal_links,
    hyperlink,
    logos_safe_headword,
    setup_document,
)

OUT = ROOT / "Ante-Nicene Dogmatics.docx"
# Logos PBB body file — keep the new name; leave a one-time copy under the old
# Desktop path only if a prior Personal Book still points there.
DESKTOP_OUT = Path.home() / "Desktop" / "AnteNicene-Dogmatics.docx"
DESKTOP_OUT_LEGACY = Path.home() / "Desktop" / "AnteNicene-Soteriology.docx"
BOOK_META = {
    "title": "Ante-Nicene Dogmatics",
    "subtitle": "The Fathers on the Full Counsel of God",
    "description": (
        "Modern English excerpts from the ante-Nicene fathers, arranged by the main "
        "topics of Christian teaching — God, Christ, Scripture, Spirit, church, "
        "sacraments, salvation, human will, last things, and the Christian life. "
        "One Logos encyclopedia for private study. Famous voices and lesser-known "
        "ones appear together under each topic, earliest to latest. Not a complete "
        "dogmatics and not a critical edition of the Greek or Latin."
    ),
    "copyright": "Ancient texts; new English topical library prepared for private study, 2026.",
    "authors": "Ante-Nicene Fathers (topical library)",
}
AUTHORS_PATH = ROOT / "authors.json"
TOPICS_YML = ROOT / "topics.yml"


def load_topics_order() -> list[tuple[str, str]]:
    """Topic id + title from topics.yml in locus order. One book TOC."""
    data = yaml.safe_load(TOPICS_YML.read_text())
    order: list[tuple[str, str]] = []
    for locus in data.get("loci") or []:
        for t in locus.get("topics") or []:
            tid = (t.get("id") or "").strip()
            title = (t.get("title") or tid).strip()
            if tid:
                order.append((tid, title))
    if not order:
        raise SystemExit("topics.yml produced empty topic order")
    return order


TOPICS_ORDER = load_topics_order()

# Logos-visible superscripts for TN headword links (not Word footnotes).
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_YEAR = re.compile(r"(\d{3,4})")


def tn_mark(n: int) -> str:
    return "".join(_SUP[int(ch)] for ch in str(n))


def load_excerpts():
    """Load all translations/topics/*.json (list or {excerpts:[]})."""
    folder = ROOT / "translations" / "topics"
    items: list = []
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            chunk = data.get("excerpts") or data.get("items") or []
        else:
            chunk = data
        items.extend(chunk)
    return items


def load_authors() -> dict:
    data = json.loads(AUTHORS_PATH.read_text())
    authors = data.get("authors") or {}
    assert isinstance(authors, dict) and authors, "authors.json missing authors map"
    return authors


def period_year(period: str | None) -> int:
    m = _YEAR.search(period or "")
    return int(m.group(1)) if m else 9999


def author_meta(authors: dict, name: str) -> dict:
    meta = authors.get(name)
    if not meta:
        raise KeyError(
            f"Author {name!r} missing from authors.json — add dates before rebuild."
        )
    return meta


def author_heading_label(name: str, meta: dict) -> str:
    dates = (meta.get("dates_display") or "").strip()
    return f"{name} ({dates})" if dates else name


def excerpt_sort_key(x: dict) -> tuple:
    return (
        period_year(x.get("period")),
        (x.get("work") or "").lower(),
        (x.get("locus") or "").lower(),
        x.get("id") or "",
    )


def authors_in_topic_order(items: list[dict], authors: dict) -> list[str]:
    """Unique authors in chronological order for one topic."""
    seen: set[str] = set()
    ordered: list[str] = []
    keyed = []
    for x in items:
        name = (x.get("author") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        meta = author_meta(authors, name)
        keyed.append((int(meta.get("sort_year") or 9999), name.lower(), name))
    keyed.sort()
    for _y, _low, name in keyed:
        ordered.append(name)
    return ordered


def attribution_line(x: dict) -> str:
    author = (x.get("author") or "").strip()
    work = (x.get("work") or "").strip()
    locus = (x.get("locus") or "").strip()
    if locus.lower().startswith("chapter") and "argument" in locus.lower():
        m = re.match(r"(Chapter\s+\d+)", locus, re.I)
        locus = m.group(1) if m else locus.split(".")[0].strip()
    if author and work and locus:
        return f"— {author}, {work} {locus}"
    if author and work:
        return f"— {author}, {work}"
    return f"— {x.get('citation', '').strip()}"


def excerpt_heading_label(x: dict) -> str:
    """Customer H3 + Headword: keep short; never ship ANF 'Argument:' titles into Logos Headwords."""
    author = (x.get("author") or "").strip()
    work = (x.get("work") or "").strip()
    locus = (x.get("locus") or "").strip()
    if locus.lower().startswith("chapter") and "argument" in locus.lower():
        m = re.match(r"(Chapter\s+\d+)", locus, re.I)
        locus = m.group(1) if m else locus.split(".")[0].strip()
    elif "argument:" in locus.lower():
        locus = locus.split(".", 1)[0].strip()
    if author and work and locus:
        return f"{author} — {work} ({locus})"
    return (x.get("citation") or "").strip() or work or author or x.get("id") or "excerpt"


def insert_tn_links(text: str, anchors: list[dict], start_n: int) -> tuple[str, list[dict], list[str]]:
    """
    After each anchor phrase, insert a Logos Headword link:
    [[¹ >> Headword:TN 1]]
    Returns (new_text, placed_records, missing_phrases).
    """
    remaining = list(anchors or [])
    placed: list[dict] = []
    missing: list[str] = []
    out = text
    # Place by first occurrence order in this paragraph; renumber globally via start_n.
    events: list[tuple[int, dict]] = []
    seen: set[str] = set()
    for a in remaining:
        phrase = (a.get("phrase") or "").strip()
        note = (a.get("note") or "").strip()
        if not phrase or not note or phrase in seen:
            continue
        idx = out.find(phrase)
        if idx < 0:
            missing.append(phrase)
            continue
        seen.add(phrase)
        events.append((idx + len(phrase), a))
    events.sort(key=lambda x: x[0])
    # Insert from the end so earlier indices stay stable.
    n = start_n + len(events) - 1
    for end, a in reversed(events):
        phrase = a["phrase"]
        hw = f"TN {n}"
        mark = tn_mark(n)
        link = f"[[{mark} >> Headword:{hw}]]"
        out = out[:end] + link + out[end:]
        placed.append(
            {
                "n": n,
                "headword": hw,
                "phrase": phrase,
                "note": a["note"].strip(),
                "citation": a.get("citation") or "",
                "excerpt_id": a.get("excerpt_id") or "",
            }
        )
        n -= 1
    placed.reverse()
    return out, placed, missing


def main():
    excerpts = load_excerpts()
    authors = load_authors()
    missing_authors = sorted({(x.get("author") or "").strip() for x in excerpts} - set(authors))
    missing_authors = [a for a in missing_authors if a]
    assert not missing_authors, f"authors.json missing: {missing_authors}"

    by_topic = defaultdict(list)
    for x in excerpts:
        by_topic[x["topic"]].append(x)

    doc = setup_document(
        title=BOOK_META["title"],
        author=BOOK_META["authors"],
        subject=BOOK_META["subtitle"],
        keywords="Ante-Nicene; dogmatics; theology; Christology; soteriology; Logos Encyclopedia",
        comments="Private study edition. One Logos encyclopedia. Not a critical edition.",
    )
    linker = BibleLinker()
    bookmarks = BookmarkStore()
    records = []
    tn_records: list[dict] = []
    anchor_missing: list[str] = []
    author_order_receipt: dict[str, list[str]] = {}

    def bible_text(text, key=None, label=None, note=False):
        return linker.bible_text(text, key=key, label=label, note=note)

    def para(text, style=None, key=None, label=None, note=False):
        p = doc.add_paragraph(style=style)
        p.add_run(bible_text(text, key, label, note))
        return p

    def heading(text, level, key, headword=None):
        p = doc.add_heading(text, level)
        bookmarks.add(p, key)
        hw = logos_safe_headword(headword if headword is not None else text)
        doc.add_paragraph(f"[[@Headword:{hw}]]")
        return p

    doc.add_paragraph(BOOK_META["title"], style="Title")
    para(BOOK_META["subtitle"], style="Subtitle")
    para("Private study edition · 2026")

    heading("About this edition", 1, "about", headword="About this edition")
    para(BOOK_META["description"])
    para(
        "Under each topic, authors appear from earliest to latest, grouped so one voice stays together. Lifespan or floruit dates sit beside each author name (approximate scholarly consensus — not exact civil records). The English aims for clear contemporary prose that keeps each author’s personality. Where a wording choice is marked, a numbered Headword note opens on hover or click. Editorial leads under each topic are ours; the excerpts are theirs."
    )
    para(
        "Use Logos Headwords to open a topic, an author-within-topic, a citation, or a TN note. Bible references use the Bible datatype. Each excerpt ends with a plain citation line for copy and paste. Corrections: hi@saneapps.com."
    )

    heading("How to read", 2, "how_to_read", headword="How to read")
    para(
        "Open a topic Headword (for example One God the Creator, or Free Will). Authors follow in chronological order, each headed with dates — for example Justin Martyr (c. 100–c. 165). Under that author, excerpts appear in work order. Numbered marks open short translation notes on hover."
    )

    heading("Contents", 1, "contents", headword="Contents")
    for tid, title in TOPICS_ORDER:
        if tid not in by_topic:
            continue
        p = doc.add_paragraph()
        hyperlink(p, title, f"topic_{tid}", internal=True)

    for tid, title in TOPICS_ORDER:
        items = by_topic.get(tid, [])
        if not items:
            continue
        heading(title, 1, f"topic_{tid}", headword=title)
        lead = next((x.get("topic_lead") for x in items if x.get("topic_lead")), None) or (
            f"Ante-Nicene witnesses on {title.lower()}, famous and lesser-known, authors earliest to latest."
        )
        para(lead, style="Caption")

        author_names = authors_in_topic_order(items, authors)
        author_order_receipt[tid] = [
            f"{n} ({author_meta(authors, n).get('dates_display', '')})" for n in author_names
        ]
        by_author: dict[str, list] = defaultdict(list)
        for x in items:
            by_author[(x.get("author") or "").strip()].append(x)

        for author_name in author_names:
            meta = author_meta(authors, author_name)
            label_author = author_heading_label(author_name, meta)
            author_key = f"author_{tid}_{re.sub(r'[^a-z0-9]+', '_', author_name.lower()).strip('_')}"
            # Topic-scoped Headword so ArticleCache Contexts stay unique across topics.
            heading(label_author, 2, author_key, headword=f"{author_name} — {title}")

            for x in sorted(by_author[author_name], key=excerpt_sort_key):
                assert x.get("english"), x.get("id")
                key = x["id"]
                label = excerpt_heading_label(x)
                citation = x.get("citation") or label
                heading(label, 3, key, headword=label)
                # confidence / authenticity / edition_id / notes / translator_notes
                # stay in translations JSON + QA — never in the customer DOCX.

                anchors = []
                for a in x.get("note_anchors") or []:
                    anchors.append(
                        {
                            **a,
                            "citation": citation,
                            "excerpt_id": key,
                        }
                    )
                remaining = list(anchors)
                for t in x["english"]:
                    here = [a for a in remaining if (a.get("phrase") or "") in t]
                    linked = bible_text(t, key=key, label=citation)
                    text2, placed, missing = insert_tn_links(linked, here, start_n=len(tn_records) + 1)
                    tn_records.extend(placed)
                    used = {p["phrase"] for p in placed}
                    remaining = [a for a in remaining if a.get("phrase") not in used]
                    p = doc.add_paragraph()
                    p.add_run(text2)

                for a in remaining:
                    phrase = (a.get("phrase") or "").strip()
                    if phrase:
                        anchor_missing.append(f"{key}:{phrase}")
                # Plain caption — never bible_text() attributions (e.g. “Ephesians 20” is a letter locus).
                attr = attribution_line(x)
                p_attr = doc.add_paragraph(style="Caption")
                p_attr.add_run(attr)

                for a in x.get("added_allusions", []):
                    certainty = "Possible allusion" if a.get("certainty") == "possible" else "Cf."
                    para(
                        f"{certainty} {a['reference']}" + (f" — {a['reason']}" if a.get("reason") else ""),
                        style="Caption",
                        key=key,
                        label=citation,
                        note=True,
                    )

                records.append(
                    dict(
                        key=key,
                        label=citation,
                        topic=tid,
                        author=author_name,
                        author_dates=meta.get("dates_display"),
                        paragraphs=len(x["english"]),
                        attribution=attr,
                        anchors=len(anchors),
                    )
                )

    if tn_records:
        heading("Translation notes", 1, "translation_notes", headword="Translation notes")
        para(
            "Short NET-style notes for wording choices. Hover or click a numbered mark in the excerpts to open the matching note."
        )
        for rec in tn_records:
            hw = rec["headword"]
            heading(hw, 3, f"tn_{rec['n']}", headword=hw)
            para(rec["note"])
            where = rec["citation"]
            if rec.get("phrase"):
                where = f"{where} — “{rec['phrase']}”"
            para(where, style="Caption")

    heading("Scripture index", 1, "scripture", headword="Scripture index")
    para("Select a reference to open Scripture; select a citation to return to its excerpt.")
    last = None
    for ref, entries in sorted(linker.index.items(), key=lambda x: sort_ref_key(x[0])):
        m = REF.fullmatch(ref)
        if not m:
            continue
        book = m["book"]
        if book != last:
            heading(book, 2, "idx_" + book.replace(" ", "_"), headword=book + " (index)")
            last = book
        p = doc.add_paragraph()
        p.add_run(bible_text(ref)).bold = True
        p.add_run(" — ")
        for i, (key, label) in enumerate(entries):
            if i:
                p.add_run("; ")
            hyperlink(p, label, key, internal=True)

    assert_internal_links(doc, bookmarks.ids)
    assert len(records) >= 20, len(records)
    doc.save(OUT)
    DESKTOP_OUT.write_bytes(OUT.read_bytes())
    # Keep legacy Desktop filename in sync so an unrepointed Logos body path still rebuilds.
    try:
        DESKTOP_OUT_LEGACY.write_bytes(OUT.read_bytes())
    except OSError:
        pass
    receipt = dict(
        section_count=len(records),
        bible_links=linker.link_receipts,
        scripture_index_entries=len(linker.index),
        bookmark_count=len(bookmarks.ids),
        tn_notes=len(tn_records),
        anchors_missing=anchor_missing,
        tn_records=tn_records,
        records=records,
        author_order_by_topic=author_order_receipt,
        authors=sorted({r["author"] for r in records}),
        desktop_copy=str(DESKTOP_OUT),
        title=BOOK_META["title"],
        subtitle=BOOK_META["subtitle"],
    )
    (ROOT / "build_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUT),
                "desktop": str(DESKTOP_OUT),
                "excerpts": len(records),
                "authors": len(receipt["authors"]),
                "bible_links": len(linker.link_receipts),
                "tn_notes": len(tn_records),
                "anchors_missing": len(anchor_missing),
                "free_will_authors": author_order_receipt.get("free-will"),
                "bytes": OUT.stat().st_size,
            }
        )
    )


if __name__ == "__main__":
    main()
