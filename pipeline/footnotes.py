"""LEGACY — do not use for Logos Personal Books.

Verified 2026-09-10 (Origen PBB): even a well-formed Word `footnotes.xml` with
unique note text compiles with 0 errors while Logos ignores the marks. Hover
falls back to the resource description for every superscript.

Required path for translator notes: Headword TN marks
`[[ⁿ >> Headword:TN n]]` + a Translator notes section
(see `docs/LOGOS_MARKUP.md`). `pipeline.verify_docx` fails if footnotes.xml
is present.

This module remains only so old experiments can be read; book builders must
not call `FootnoteStore`.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FOOTNOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"
FOOTNOTES_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


class FootnoteStore:
    """Collect footnotes while building; finalize into a Word-native DOCX."""

    def __init__(self):
        self._notes: list[str] = []

    @property
    def count(self) -> int:
        return len(self._notes)

    def attach(self, paragraph, note_text: str) -> int:
        text = (note_text or "").strip()
        assert text, "empty footnote"
        fid = len(self._notes) + 1
        self._notes.append(text)

        run = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        style = OxmlElement("w:rStyle")
        style.set(qn("w:val"), "FootnoteReference")
        rpr.append(style)
        run.append(rpr)
        ref = OxmlElement("w:footnoteReference")
        ref.set(qn("w:id"), str(fid))
        run.append(ref)
        paragraph._p.append(run)
        return fid

    def finalize(self, docx_path: Path | str) -> None:
        if not self._notes:
            return
        path = Path(docx_path)
        tmp = path.with_suffix(path.suffix + ".fn.tmp")
        with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    data = _ensure_content_types(data)
                elif item.filename == "word/_rels/document.xml.rels":
                    data = _ensure_footnotes_rel(data)
                elif item.filename == "word/styles.xml":
                    data = _ensure_footnote_styles(data)
                if item.filename != "word/footnotes.xml":
                    zout.writestr(item, data)
            zout.writestr("word/footnotes.xml", _footnotes_xml(self._notes))
        tmp.replace(path)


def paragraph_with_note_anchors(doc, footnotes: FootnoteStore, linked_text: str, anchors: list[dict]):
    """Build a paragraph; attach footnotes after the first hit of each phrase."""
    p = doc.add_paragraph()
    if not linked_text:
        return p, 0, []

    events: list[tuple[int, str, str]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for raw in anchors or []:
        phrase = (raw.get("phrase") or "").strip()
        note = (raw.get("note") or "").strip()
        if not phrase or not note or phrase in seen:
            continue
        idx = linked_text.find(phrase)
        if idx < 0:
            missing.append(phrase)
            continue
        seen.add(phrase)
        events.append((idx + len(phrase), note, phrase))

    events.sort(key=lambda x: x[0])
    cursor = 0
    placed = 0
    used_ends: set[int] = set()
    for end, note, _phrase in events:
        if end in used_ends or end < cursor:
            continue
        chunk = linked_text[cursor:end]
        if chunk:
            p.add_run(chunk)
        footnotes.attach(p, note)
        placed += 1
        used_ends.add(end)
        cursor = end
    if cursor < len(linked_text):
        p.add_run(linked_text[cursor:])
    return p, placed, missing


def _ensure_content_types(data: bytes) -> bytes:
    root = ET.fromstring(data)
    for child in root:
        if child.tag.endswith("Override") and child.get("PartName") == "/word/footnotes.xml":
            return data
    override = ET.SubElement(root, f"{{{CT_NS}}}Override")
    override.set("PartName", "/word/footnotes.xml")
    override.set("ContentType", FOOTNOTES_CT)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _ensure_footnotes_rel(data: bytes) -> bytes:
    root = ET.fromstring(data)
    for child in root:
        if child.get("Target") == "footnotes.xml":
            return data
    max_id = 0
    for child in root:
        rid = child.get("Id") or ""
        if rid.startswith("rId"):
            try:
                max_id = max(max_id, int(rid[3:]))
            except ValueError:
                pass
    rel = ET.SubElement(root, f"{{{R_NS}}}Relationship")
    rel.set("Id", f"rId{max_id + 1}")
    rel.set("Type", FOOTNOTES_REL)
    rel.set("Target", "footnotes.xml")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _ensure_footnote_styles(data: bytes) -> bytes:
    """Inject Word footnote styles (required for Logos PBB hover)."""
    root = ET.fromstring(data)
    have = {
        (s.get(f"{{{W_NS}}}styleId") or "")
        for s in root.findall(f"{{{W_NS}}}style")
    }
    if "FootnoteText" not in have:
        s = ET.SubElement(root, _w("style"))
        s.set(f"{{{W_NS}}}type", "paragraph")
        s.set(f"{{{W_NS}}}styleId", "FootnoteText")
        n = ET.SubElement(s, _w("name"))
        n.set(f"{{{W_NS}}}val", "footnote text")
        b = ET.SubElement(s, _w("basedOn"))
        b.set(f"{{{W_NS}}}val", "Normal")
    if "FootnoteReference" not in have:
        s = ET.SubElement(root, _w("style"))
        s.set(f"{{{W_NS}}}type", "character")
        s.set(f"{{{W_NS}}}styleId", "FootnoteReference")
        n = ET.SubElement(s, _w("name"))
        n.set(f"{{{W_NS}}}val", "footnote reference")
        rpr = ET.SubElement(s, _w("rPr"))
        vert = ET.SubElement(rpr, _w("vertAlign"))
        vert.set(f"{{{W_NS}}}val", "superscript")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _footnotes_xml(notes: list[str]) -> bytes:
    root = ET.Element(_w("footnotes"))
    for fid, kind, child_tag in (
        ("-1", "separator", "separator"),
        ("0", "continuationSeparator", "continuationSeparator"),
    ):
        fn = ET.SubElement(root, _w("footnote"))
        fn.set(f"{{{W_NS}}}id", fid)
        fn.set(f"{{{W_NS}}}type", kind)
        p = ET.SubElement(fn, _w("p"))
        r = ET.SubElement(p, _w("r"))
        ET.SubElement(r, _w(child_tag))

    for i, text in enumerate(notes, start=1):
        fn = ET.SubElement(root, _w("footnote"))
        fn.set(f"{{{W_NS}}}id", str(i))
        p = ET.SubElement(fn, _w("p"))
        ppr = ET.SubElement(p, _w("pPr"))
        ps = ET.SubElement(ppr, _w("pStyle"))
        ps.set(f"{{{W_NS}}}val", "FootnoteText")
        r0 = ET.SubElement(p, _w("r"))
        rpr = ET.SubElement(r0, _w("rPr"))
        rs = ET.SubElement(rpr, _w("rStyle"))
        rs.set(f"{{{W_NS}}}val", "FootnoteReference")
        ET.SubElement(r0, _w("footnoteRef"))
        r1 = ET.SubElement(p, _w("r"))
        t = ET.SubElement(r1, _w("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = " " + text

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
