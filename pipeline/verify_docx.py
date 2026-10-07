"""Verify a Logos PBB DOCX for common build failures."""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

# Captions labeled this way were the Origen failure mode: every clear allusion
# dumped under the chapter instead of linked inline in the prose.
_SCRIPTURE_DUMP = re.compile(r"Scripture connection\s*:", re.I)
# Soft limit: a few residual captions can be editorial; dozens means a dump.
_SCRIPTURE_DUMP_MAX = 8
# Scaffold rows must never ship: collect_sections maps them to pending, and
# this gate refuses any artifact that still contains them (cyril-isaiah 2026-09).
_SCAFFOLD_XML = re.compile(r"Rem (?:early|mid|CLOSEOUT):|Lemma-led|ZU [A-Z]{2,}")

# Translator worksheet notes. They travel with the English JSON and must never
# reach a reader: the 2026-10-06 red team found "True OET; Pass A ≠ Pass B.
# Melito skipped; never Cyril Matthew densify." printed as TN 1-12 in 169 of
# 225 Logos Word files. build_pbb_docx.py drops notes that match these marks,
# and this gate refuses any file that still carries one. Ordinary English such
# as "pass away" or "to pass a law" does not match ("Pass A" is case-sensitive).
WORKSHEET_MARKS = (
    "true oet",
    "pass a ≠",
    "pass a !=",
    "melito skipped",
    "never cyril matthew",
    "skip pusey",
    "machine draft",
    "tip-checked",
    "densify",
    "series closeout",
    "earliest-forward",
    "condensed lemma-led",
    "khazarzar research-footer",
    "real khazarzar file",
    "corpus-wide rank-1",
)
_WORKSHEET_CI = re.compile(
    "|".join(r"\s+".join(map(re.escape, mark.split())) for mark in WORKSHEET_MARKS),
    re.I)
_WORKSHEET_CS = re.compile(r"\bPass [AB]\b")


def worksheet_hits(text: str) -> list[str]:
    """Worksheet marks found in text, in order (empty when the text is clean)."""
    found = [(m.start(), -m.end(), m.group(0)) for m in _WORKSHEET_CI.finditer(text)]
    found += [(m.start(), -m.end(), m.group(0)) for m in _WORKSHEET_CS.finditer(text)]
    hits, reach = [], -1
    for start, neg_end, hit in sorted(found):
        if start < reach:
            continue  # "Pass A" inside "Pass A ≠" is one note, not two
        hits.append(" ".join(hit.split()))
        reach = -neg_end
    return hits


def docx_text(xml: str) -> str:
    """Reader text of document.xml: runs joined inside a paragraph, one line each."""
    lines = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        line = "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", para))
        lines.append(line.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&"))
    return "\n".join(lines)


def _intro_opted_out(book_dir: Path) -> bool:
    """True when book.yml says logos_intro: false (the only opt-out)."""
    try:
        text = (book_dir / "book.yml").read_text(encoding="utf-8")
    except OSError:
        return False
    match = re.search(r"(?m)^logos_intro:\s*(.*)$", text)
    flag = match.group(1).strip().strip("'\"").lower() if match else ""
    return flag in ("false", "no", "0")


def stale_reasons(book_dir: Path, docx: Path) -> list[str]:
    """Why a book's Word file no longer matches its English (empty when current).

    One rule for the builder (catchup), the Logos pack, the Sunday driver
    and pb_sync: the Word file is older than an *_english.json or intro.md,
    or intro.md exists but the file has no Introduction. Worksheet notes are
    verify_docx's job; call both (logos_file_problems does).
    """
    book_dir, docx = Path(book_dir), Path(docx)
    try:
        built = docx.stat().st_mtime
    except OSError as exc:
        return [f"no Word file ({exc})"]
    intro = book_dir / "intro.md"
    inputs = list((book_dir / "translations").glob("*_english.json"))
    if intro.is_file():
        inputs.append(intro)
    reasons = []
    newer = sorted(p.name for p in inputs if p.stat().st_mtime > built)
    if newer:
        reasons.append("English newer than the Word file (" + ", ".join(newer[:3]) + ")")
    if intro.is_file() and not _intro_opted_out(book_dir):
        try:
            with zipfile.ZipFile(docx) as zf:
                xml = zf.read("word/document.xml").decode("utf-8", "replace")
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            return reasons + [f"unreadable Word file ({exc})"]
        if "\nIntroduction\n" not in f"\n{docx_text(xml)}\n":
            reasons.append("Word file leaves out intro.md")
    return reasons


def logos_file_problems(book_dir: Path, docx: Path) -> list[str]:
    """Every reason a Word file must not be built, uploaded or added to Logos.

    verify_docx (worksheet notes, Bible links, scaffold labels) plus
    stale_reasons (older than its English, or no Introduction). Short
    reasons, first sentence of each. Fix: build_pbb_docx.py --catchup.
    """
    errs = [e.split(". ")[0][:160] for e in verify_docx(Path(docx))]
    return errs + stale_reasons(book_dir, docx)


def verify_docx(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing file: {path}"]
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        # Logos Personal Books ignore Word footnotes; hover falls back to the
        # book description for every mark. Ban footnotes.xml entirely.
        if "word/footnotes.xml" in names:
            errors.append(
                "word/footnotes.xml present — Logos PBB does not compile Word "
                "footnotes (hover becomes the book blurb). Use Headword TN marks "
                "instead (see docs/LOGOS_MARKUP.md)."
            )
        if "footnoteReference" in xml or "w:footnoteReference" in xml:
            errors.append(
                "w:footnoteReference found in document.xml — do not use Word "
                "footnotes in Personal Books; use [[ⁿ >> Headword:TN n]]."
            )

    bad = []
    for m in re.finditer(r"<w:t[^>]*>([^<]*)</w:t>", xml):
        t = m.group(1)
        if "[[@Headword:" in t:
            # Standalone: entire text is the field (optional whitespace).
            if not re.fullmatch(r"\s*\[\[@Headword:[^\]]+\]\]\s*", t):
                bad.append(t[:120])
    if bad:
        errors.append(f"glued or dirty Headword runs ({len(bad)}): e.g. {bad[0]!r}")

    # Word stores >> as &gt;&gt; inside document.xml
    if not re.search(r"&gt;&gt;\s*Bible:|>>\s*Bible:", xml):
        errors.append(
            "no Bible datatype links found ([[… >> Bible:…]]). If the passage "
            "genuinely cites no Scripture, that is the honest result: leave the "
            "Logos book build on hold (this is the tip exemption). Do not invent "
            "possible or thematic links just to satisfy this check"
        )
    if "[[@Headword:" not in xml and "Headword:" not in xml:
        errors.append("no Headword milestones found")

    plain = re.sub(r"<[^>]+>", " ", xml)
    plain = plain.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    dump_hits = _SCRIPTURE_DUMP.findall(plain)
    if len(dump_hits) > _SCRIPTURE_DUMP_MAX:
        errors.append(
            f"{len(dump_hits)} 'Scripture connection:' captions (max {_SCRIPTURE_DUMP_MAX}) — "
            "put clear allusions inline in the English; captions only for possible/uncertain links."
        )
    scaffold_hits = _SCAFFOLD_XML.findall(plain)
    if scaffold_hits:
        errors.append(
            f"{len(scaffold_hits)} scaffold-text hit(s) (Rem/Lemma-led/ZU) — "
            "untranslated rows must render as [English pending.], never ship labels."
        )
    sheet = worksheet_hits(docx_text(xml))
    if sheet:
        shown = ", ".join(dict.fromkeys(sheet))[:120]
        errors.append(
            f"{len(sheet)} translator worksheet note(s) ({shown}). Lane notes such "
            "as True OET or Pass A must not ship; rebuild with build_pbb_docx.py, "
            "whose note filter drops them"
        )

    # Scope the caption check to a single <w:p> paragraph: matching over the
    # whole document lets a plain caption span forward into the next record's
    # legitimate inline cite (false positive; julian-of-eclanum 2026-09-16).
    padded = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        text = re.sub(r"<[^>]+>", " ", para)
        text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
        padded.extend(
            re.findall(r"Possible allusion:[^[]*\[\[[^]]*>>\s*Bible:", text, re.I)
        )
    if padded:
        errors.append(
            f"{len(padded)} 'Possible allusion' caption(s) written as clickable "
            "Bible links. Possible allusions must stay plain text because the "
            "author does not actually cite the passage; a truthful label does "
            "not turn padding into a real link. Render these captions as plain "
            "text instead"
        )

    if "logosres:" in plain.lower():
        errors.append("logosres: links found — do not emit cross-resource store prompts")

    return errors


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("docx", nargs="+", type=Path)
    args = p.parse_args(argv)
    # Fail closed on builder anti-patterns (FootnoteStore / Scripture-connection dumps).
    try:
        from pipeline.check_pbb_guards import check_build_scripts
    except ImportError:  # pragma: no cover
        from check_pbb_guards import check_build_scripts  # type: ignore

    guard_errs = check_build_scripts()
    if guard_errs:
        print("FAIL PBB guards (build scripts)")
        for e in guard_errs:
            print(f"  - {e}")
        return 1
    failed = 0
    for path in args.docx:
        errs = verify_docx(path)
        if errs:
            failed += 1
            print(f"FAIL {path}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
