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
