#!/usr/bin/env python3
"""Per-book adapters for draft/promote generalization.

Each supported book slug maps to an adapter that knows its claim-ID shape,
slice syntax, source layout, evidence paths, and witness files. Unknown
books and unknown sections refuse with SystemExit (fail closed, as before).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

JEREMIAH_SLUG = "origen-jeremiah-samuel"
CYRIL_ISAIAH_SLUG = "cyril-alexandria-isaiah"


class BookAdapter:
    slug = ""
    claim_re = r"(?!)"
    work_title = ""
    chunked_source = False

    def sections_from_slice(self, text: str) -> list[str]:
        raise NotImplementedError

    def load_source_row(self, section: str) -> dict:
        """Return fix dict: section, greek[list], ocr_normalizations, locus-ish."""
        raise NotImplementedError

    def justification_path(self, section: str) -> Path:
        raise NotImplementedError

    def excerpt_id(self, section: str) -> str:
        raise NotImplementedError

    def witness_files(self, section: str) -> list[Path]:
        """Absolute raw-source files to hash-lock for this section."""
        raise NotImplementedError

    def manifest_path(self) -> Path | None:
        """Committed manifest pinning witness hashes, or None if unpinned."""
        return None

    def manifest_rel(self, path: Path) -> str:
        parent = self.manifest_path()
        assert parent is not None
        return path.relative_to(parent.parent).as_posix()

    def edition_dict(self, fix: dict, witnesses: list[dict]) -> dict:
        raise NotImplementedError

    def checker_title(self, section: str) -> str:
        raise NotImplementedError

    def resolve_source_path(self, rel: str) -> Path:
        raise NotImplementedError


class JeremiahAdapter(BookAdapter):
    slug = JEREMIAH_SLUG
    claim_re = r"jer-h\d+(?:-[a-z0-9]+)*"
    work_title = "Origen, Homilies on Jeremiah"

    def __init__(self):
        self.book_dir = ROOT / "books/origen-jeremiah-samuel"
        self.eng = self.book_dir / "translations/jeremiah_english.json"
        self.just_dir = self.book_dir / "reviews/justifications"
        self.raw_source = self.book_dir / "sources/origeneswerke03orig.pdf"
        self.xml_source = self.book_dir / "sources/first1k/tlg2042.tlg009.opp-grc1.xml"
        self.manifest = self.book_dir / "sources/manifest.json"

    def sections_from_slice(self, slice_text: str) -> list[str]:
        """Parse Homily 6 sections 6.1-6.3 style slices into section ids."""
        m = re.search(r"§§?\s*([\d.]+)\s*[–-]\s*([\d.]+)", slice_text)
        if not m:
            raise SystemExit(f"Cannot parse slice sections from: {slice_text!r}")
        start, end = m.group(1), m.group(2)
        sh, ss = start.split(".")
        eh, es = end.split(".")
        if sh != eh or int(ss) < 1 or int(es) < int(ss):
            raise SystemExit(f"Cross-homily slice not supported yet: {slice_text}")
        return [f"{sh}.{i}" for i in range(int(ss), int(es) + 1)]

    def load_source_row(self, section: str) -> dict:
        from llm_bakeoff import load_fixture

        return load_fixture(section)

    def english_path(self) -> Path:
        return self.eng

    def justification_path(self, section: str) -> Path:
        flat = section.replace(".", "_")
        return self.just_dir / f"jeremiah_{flat}.json"

    def excerpt_id(self, section: str) -> str:
        h, s = section.split(".")
        return f"jeremiah_{h}_{s}"

    def witness_files(self, section: str) -> list[Path]:
        return [self.raw_source, self.xml_source]

    def manifest_path(self) -> Path | None:
        return self.manifest

    def edition_dict(self, fix: dict, witnesses: list[dict]) -> dict:
        return {
            "id": "gcs6-klostermann-1901", "language": "grc",
            "locus": fix.get("klostermann") or f"Hom. {fix["section"]}",
            "path": witnesses[0]["path"], "sha256": witnesses[0]["sha256"],
            "checks": witnesses[1:],
        }

    def checker_title(self, section: str) -> str:
        return f"Origen, Homilies on Jeremiah, section {section}"

    def resolve_source_path(self, rel: str) -> Path:
        path = Path(rel)
        if path.is_absolute():
            return path
        return self.book_dir / path


_LOCUS_WORDS = {"book": "Book", "tomos": "tome", "logos": "logos",
                "part": "part", "open": "opening", "rem": "remainder"}


def _pretty_locus(section: str) -> str:
    if section == "prologue":
        return "Prologue"
    words = []
    for tok in section.split("-"):
        m = re.fullmatch(r"([a-z]+)(\d+)", tok)
        if m:
            words.append(_LOCUS_WORDS.get(m.group(1), m.group(1)) + " " + m.group(2))
        else:
            words.append(_LOCUS_WORDS.get(tok, tok))
    text = " ".join(words)
    return text[0].upper() + text[1:] if text else section


class CyrilIsaiahAdapter(BookAdapter):
    slug = CYRIL_ISAIAH_SLUG
    claim_re = r"cyr-isa-[a-z0-9][a-z0-9-]*"
    work_title = "Cyril of Alexandria, Commentary on Isaiah"
    chunked_source = True

    def __init__(self):
        self.book_dir = ROOT / "books/cyril-alexandria-isaiah"
        self.trans_dir = self.book_dir / "translations"
        self.just_dir = self.book_dir / "reviews/justifications"
        self.pg70 = self.book_dir / "sources/isaiah_pg70.txt"
        self.manifest = self.book_dir / "sources/manifest.json"
        self._index = None

    def _source_index(self):
        if self._index is None:
            index = {}
            for path in sorted(self.trans_dir.glob("*_source.json")):
                rows = json.loads(path.read_text(encoding="utf-8"))
                for i, row in enumerate(rows if isinstance(rows, list) else [rows]):
                    section = str(row.get("section") or "")
                    if not section:
                        continue
                    if section in index:
                        raise SystemExit(f"Duplicate cyril-isaiah section {section}")
                    index[section] = (path, i, row)
            self._index = index
        return self._index

    def sections_from_slice(self, slice_text: str) -> list[str]:
        sections = [s for s in re.split(r"[,\s]+", slice_text.strip()) if s]
        if not sections:
            raise SystemExit(f"Cannot parse slice sections from: {slice_text!r}")
        index = self._source_index()
        for section in sections:
            if section not in index:
                raise SystemExit(f"Unknown cyril-isaiah section {section!r}")
        return sections

    def load_source_row(self, section: str) -> dict:
        index = self._source_index()
        if section not in index:
            raise SystemExit(f"Unknown cyril-isaiah section {section!r}")
        _path, _i, row = index[section]
        greek = row.get("greek") or ""
        paras = [greek] if isinstance(greek, str) else [str(g) for g in greek]
        return {
            "section": section, "homily": None, "klostermann": None,
            "locus": _pretty_locus(section), "greek": paras,
            "ocr_normalizations": row.get("ocr_normalizations") or [],
            "chunked_source": True,
        }

    def english_path_for_section(self, section: str) -> Path:
        path, _i, _row = self._source_index()[section]
        return path.with_name(path.name.replace("_source.json", "_english.json"))

    def english_row_index(self, section: str) -> int:
        _path, i, _row = self._source_index()[section]
        return i

    def justification_path(self, section: str) -> Path:
        path, _i, _row = self._source_index()[section]
        stem = path.name.replace("_source.json", "")
        if stem.startswith("isaiah_"):
            stem = stem[7:]
        if stem == "prol":
            stem = "prologue"
        rows = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(rows, list) and len(rows) > 1:
            stem += "_" + section.rsplit("-", 1)[-1]
        return self.just_dir / f"{stem}.json"

    def excerpt_id(self, section: str) -> str:
        return section

    def witness_files(self, section: str) -> list[Path]:
        path, _i, _row = self._source_index()[section]
        files = [path]
        if self.pg70.is_file():
            files.append(self.pg70)
        return files

    def edition_dict(self, fix: dict, witnesses: list[dict]) -> dict:
        return {
            "id": "pg70-cpg5203", "language": "grc",
            "locus": fix.get("locus") or fix["section"],
            "path": witnesses[0]["path"], "sha256": witnesses[0]["sha256"],
            "checks": witnesses[1:],
        }

    def checker_title(self, section: str) -> str:
        return f"Cyril of Alexandria, Commentary on Isaiah, {section}"

    def resolve_source_path(self, rel: str) -> Path:
        path = Path(rel)
        if path.is_absolute():
            return path
        return self.book_dir / path


_ADAPTERS = {
    JEREMIAH_SLUG: JeremiahAdapter(),
    CYRIL_ISAIAH_SLUG: CyrilIsaiahAdapter(),
}


def supported_slugs() -> list[str]:
    return sorted(_ADAPTERS)


def get_adapter(slug: str) -> BookAdapter:
    try:
        return _ADAPTERS[slug]
    except KeyError:
        raise SystemExit(
            f"Unsupported book {slug!r} (supported: " + ", ".join(supported_slugs()) + "); refusing"
        ) from None
