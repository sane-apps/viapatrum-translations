"""Build the Julian of Eclanum Logos Personal Book DOCX."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.bible_links import BibleLinker, REF, _expand_comma_verses, sort_ref_key
from pipeline.docx_helpers import (
    BookmarkStore,
    add_heading_with_headword,
    assert_internal_links,
    hyperlink,
    setup_document,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Julian of Eclanum English.docx"
RECEIPT = ROOT / "build_receipt.json"

SEQUENCE = (141, 236, 216, 136, 64, 41)

FRONT_MATTER = [
    "Private study edition. New AI-assisted translation from Latin, 2026.",
    "Scope: Julian's six books To Florus (preserved in Augustine's Unfinished Work Against Julian), fragments To Turbantius, extracts in On Marriage and Concupiscence, Letter to Rome, and Collective Letter to Thessalonica.",
    "Bible quotations and clear allusions are linked inline in the reading text. Possible connections stay as short captions. Translator notes use numbered Headword marks — Logos Personal Books do not compile Word footnotes.",
]

# Logos-visible superscripts for TN headword links (not Word footnotes).
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_STOP = {
    "about", "after", "against", "almost", "already", "among", "because", "before",
    "being", "between", "chapter", "clear", "could", "echo", "echoes", "every",
    "first", "from", "further", "here", "into", "same", "saying", "shall", "should",
    "their", "there", "these", "those", "through", "under", "where", "which", "while",
    "with", "would", "julian", "augustine", "latin", "manichaean", "pelagian",
    "also", "than", "then", "that", "this", "they", "them", "have", "been", "were",
    "when", "what", "your", "unto",
}


def tn_mark(n: int) -> str:
    return "".join(_SUP[int(ch)] for ch in str(n))


def _allusion_ref(raw) -> tuple[str, str, str]:
    if isinstance(raw, dict):
        return (
            (raw.get("reference") or "").strip(),
            (raw.get("certainty") or "clear").strip(),
            (raw.get("reason") or "").strip(),
        )
    return (str(raw).strip(), "clear", "")


def _ref_already_in(text: str, reference: str) -> bool:
    for m in REF.finditer(reference):
        book = "Psalm" if m["book"] == "Psalms" else m["book"]
        for loc in _expand_comma_verses(book, m["loc"].replace("–", "-")):
            needle = f"{book} {loc}"
            if needle in text:
                return True
            if re.search(rf"\b{re.escape(book)}\s+{re.escape(loc.split(':')[0])}\b", text):
                return True
    return False


def _reason_words(reason: str) -> list[str]:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-z']{5,}", reason)
        if w.lower() not in _STOP
    ]
    for q in re.findall(r"'([^']{6,80})'|\"([^\"]{6,80})\"", reason):
        snippet = (q[0] or q[1]).lower()
        words.extend(w for w in re.findall(r"[A-Za-z']{5,}", snippet) if w not in _STOP)
    return words


def _insert_cite_before_punct(text: str, end: int, cite: str) -> str:
    return text[:end] + cite + text[end:]


def _word_hit(word: str, haystack: str) -> bool:
    if word in haystack:
        return True
    if len(word) >= 6 and word[:6] in haystack:
        return True
    return False


def _inject_cite_in_paragraph(paragraph: str, reference: str, reason: str) -> str:
    cite = f" ({reference})"
    if f"({reference})" in paragraph:
        return paragraph
    words = _reason_words(reason)
    score_base = re.sub(r"\s*\([^)]*\d[^)]*\)", "", paragraph)
    best_clause = None
    best_score = -1.0
    for m in re.finditer(r"[^.;!?]+[.;!]?", score_base):
        s = m.group()
        if len(s.strip()) < 12:
            continue
        sl = s.lower()
        score = float(sum(1 for w in words if _word_hit(w, sl)))
        if "'" in s or "‘" in s or "“" in s:
            score += 0.5
        score += min(len(s), 120) / 2000.0
        if score > best_score:
            best_score = score
            best_clause = s

    if best_clause is None or best_score < 1.0:
        end = len(paragraph)
        while end > 0 and paragraph[end - 1].isspace():
            end -= 1
        if end > 0 and paragraph[end - 1] in ".!?;:":
            return _insert_cite_before_punct(paragraph, end - 1, cite)
        return paragraph + cite

    core = re.sub(r"[.;!?]+$", "", best_clause.strip())
    core = re.sub(r"\s+", " ", core)
    needle = core[-50:] if len(core) > 50 else core
    pos = paragraph.find(needle)
    if pos < 0:
        pos = paragraph.lower().find(needle.lower())
    if pos < 0:
        end = len(paragraph)
        while end > 0 and paragraph[end - 1].isspace():
            end -= 1
        if end > 0 and paragraph[end - 1] in ".!?;:":
            return _insert_cite_before_punct(paragraph, end - 1, cite)
        return paragraph + cite

    end = pos + len(needle)
    while end < len(paragraph):
        ch = paragraph[end]
        if ch in ".!?;:":
            return _insert_cite_before_punct(paragraph, end, cite)
        if ch.isspace():
            end += 1
            continue
        if paragraph.startswith(" (", end):
            close = paragraph.find(")", end)
            if close < 0:
                break
            end = close + 1
            continue
        break
    return _insert_cite_before_punct(paragraph, end, cite)


def inject_refs_into_paragraphs(paragraphs: list[str], allusions: list) -> tuple[list[str], list[dict]]:
    original = list(paragraphs)
    paras = list(paragraphs)
    if not paras:
        return paras, []
    leftovers: list[dict] = []

    for raw in allusions or []:
        reference, certainty, reason = _allusion_ref(raw)
        if not reference:
            continue
        if certainty == "possible":
            leftovers.append({"reference": reference, "certainty": certainty, "reason": reason})
            continue
        body = "\n".join(paras)
        if _ref_already_in(body, reference):
            continue

        words = _reason_words(reason)
        best_i, best_score = len(paras) - 1, -1.0
        for i, p in enumerate(original):
            pl = p.lower()
            score = float(sum(1 for w in words if _word_hit(w, pl)))
            if "'" in p or "‘" in p or "“" in p:
                score += 0.5
            if score > best_score:
                best_score, best_i = score, i

        paras[best_i] = _inject_cite_in_paragraph(paras[best_i], reference, reason)

    return paras, leftovers


def load(name):
    return json.loads((ROOT / "translations" / name).read_text())


def main() -> None:
    doc = setup_document(
        title="Julian of Eclanum: Surviving Arguments Preserved by Augustine",
        author="Julian of Eclanum",
        subject="English translation with Scripture links and source references",
        keywords="Julian of Eclanum; Augustine; original sin; free will; grace; Logos Personal Book",
        comments="Private study edition. New AI-assisted translation from Latin, 2026.",
    )
    doc.add_paragraph("Julian of Eclanum", style="Title")
    doc.add_paragraph("Surviving Arguments Preserved by Augustine", style="Subtitle")
    doc.add_paragraph("An English study edition with Scripture links")
    doc.add_paragraph("New AI-assisted translation from the surviving Latin\nPrepared for private study in 2026")
    for para in FRONT_MATTER:
        doc.add_paragraph(para)

    linker = BibleLinker()
    bookmarks = BookmarkStore()
    tn_records: list[dict] = []
    records: list[dict] = []

    def heading(text, level, key):
        p = doc.add_heading(text, level)
        bookmarks.add(p, key)
        return p

    def para(text, style=None, key=None, label=None, note=False):
        p = doc.add_paragraph(style=style)
        p.add_run(linker.bible_text(text, key=key, label=label, note=note))
        return p

    def add_record(x, key, label, source, level=3):
        assert x["english"] and all(isinstance(t, str) and t.strip() for t in x["english"]), label
        assert not re.search(r"\[n\d|YYYY|TODO", " ".join(x["english"])), label
        if key not in bookmarks.ids:
            heading(label, level, key)
        if x.get("kind"):
            p = doc.add_paragraph(x["kind"].capitalize(), style="Caption")
            p.add_run(linker.bible_text("", key=key, label=label, note=True))

        enriched, possible = inject_refs_into_paragraphs(
            list(x.get("english") or []),
            x.get("added_allusions") or [],
        )
        n_paras = 0
        for p_text in enriched:
            linked = linker.bible_text(p_text, key=key, label=label)
            doc.add_paragraph(linked)
            n_paras += 1

        notes = [n.strip() for n in (x.get("translator_notes") or []) if (n or "").strip()]
        if notes and n_paras:
            marks = []
            for note in notes:
                n = len(tn_records) + 1
                hw = f"TN {n}"
                mark = tn_mark(n)
                marks.append(f"[[{mark} >> Headword:{hw}]]")
                tn_records.append(
                    {
                        "n": n,
                        "headword": hw,
                        "note": note,
                        "citation": label,
                        "excerpt_id": key,
                    }
                )
            doc.add_paragraph(" ".join(marks))

        for a in possible:
            reason = a.get("reason") or ""
            line = f"Possible allusion: {a['reference']}"
            if reason:
                line += f" — {reason}"
            doc.add_paragraph(
                linker.bible_text(line, key=key, label=label, note=True),
                style="Caption",
            )

        if x.get("also_preserved_at"):
            doc.add_paragraph(
                "Also preserved at " + ", ".join(x["also_preserved_at"]) + ".",
                style="Caption",
            )
        p = doc.add_paragraph(style="Caption")
        hyperlink(p, "Source witness", source)

        records.append(dict(key=key, label=label, source=source, paragraphs=n_paras))

    heading("About this edition", 1, "about")
    para(
        "This book lets you read Julian's surviving arguments in English and follow his biblical quotations and allusions in Logos. Its core is the six preserved books addressed to Florus, quoted section by section by Augustine. It also gathers earlier fragments addressed to Turbantius and material from letters preserved in Augustine's replies. Augustine's surrounding refutations are omitted. Where he only reports Julian's position, that report is identified rather than presented as Julian's continuous words."
    )
    para(
        "The six books To Florus are preserved in Augustine's Unfinished Work Against Julian. Augustine's work ends after Book Six; the last two of Julian's eight books do not survive there. The earlier four books To Turbantius survive as excerpts rather than an intact work. The fragments below follow the locations of the preserving works, not a conjectural reconstruction of Julian's lost original order. Repeated quotations within a witness are generally printed once; substantial or distinctive parallel witnesses are retained."
    )
    para(
        "This is an edition of the material gathered from the Augustinian witnesses listed below. It is not a complete collection of every work attributed to Julian: his separately transmitted biblical commentaries are outside its scope. Ancient transmission can leave gaps or uncertain attributions that no translation can repair. The working Latin sources are retained with the project files; the reading text is English only."
    )
    para(
        "The translation aims at clear contemporary English while keeping the argument, qualifications, and polemical force of the Latin. Long sentences are sometimes divided. Bible quotations follow Julian's wording rather than being replaced with a modern English Bible. Brackets and translation notes flag supplied wording, textual problems, and uncertain interpretations. This is a new AI-assisted private-study translation, checked against the available source texts; it has not received independent specialist publication review and should not be cited as an established critical edition."
    )
    heading("Reading and citing", 2, "reading")
    para(
        "Use the Logos table of contents to move between books and sections. Each section also has a named reference, such as To Florus 1.27. Cite Julian, To Florus, book and section, and identify this English study edition. For a fragment, cite the preserving work and its book, chapter, and section, for example Julian, fragment in Augustine, Against Julian 3.20.41. The Source witness link leads to the corresponding Latin passage. These locators are not invented page numbers."
    )
    para(
        "Bible references are links. Links use familiar modern chapter and verse numbers. Old reference labels, where retained, link to the corresponding modern passage rather than relying on a different numbering system. A quotation may differ from the Bible that opens because Julian often used an Old Latin form based on the Greek Scriptures. Clear quotations and allusions are linked in the English itself. 'Cf.' marks a recognizable echo kept as a short editorial caption; 'Possible allusion' marks an uncertain connection. These identifications are editorial, not words added to Julian's argument. Implicit echoes cannot always be identified with certainty."
    )
    para(
        "The Scripture index at the end lists reference ranges and links back to the sections using or discussing them. Entries marked 'note' occur in editorial notes, including comparisons and explanations of variant readings; they should not all be treated as quotations by Julian."
    )
    heading("Terms used in the debate", 2, "terms")
    for t in [
        "Original sin or original evil: the inherited condition and guilt Augustine defended and Julian rejected. When Julian says 'natural sin,' he is often attacking that doctrine rather than accepting that sin belongs to created nature.",
        "Desire and concupiscence: the Latin can mean desire broadly or, in this controversy, sexual desire in particular. The translation uses the more specific wording where the context requires it. 'Flesh' can mean the body, human mortality, or a sinful way of living; Julian's distinctions are retained.",
        "Nature and substance: what a thing is as created. A fault, vice, or defect can instead be something that happens to it. Much of the argument turns on the difference between a created capacity and its misuse.",
        "Justice and righteousness: different English uses of the same Latin word family. 'Merit,' 'deserving,' and 'what is due' concern the relationship between actions and judgment; they are not silently reduced to modern ideas of achievement.",
        '"You" normally addresses Augustine; "we" normally means Julian and those whose position he defends. Charges of Manichaeism, condemned marriage, or divine injustice are frequently Julian\'s accusations against his opponent, not beliefs he endorses.',
    ]:
        doc.add_paragraph(t)

    heading("Contents", 1, "contents")
    for text, key in (
        [("To Florus", "florus")]
        + [(f"Book {b}", f"florus_{b}") for b in range(1, 7)]
        + [
            ("To Turbantius fragments in Against Julian", "turbantius"),
            ("Extracts in On Marriage and Concupiscence", "marriage"),
            ("Letter to Rome", "rome"),
            ("Collective letter to Thessalonica", "collective"),
            ("Sources and editorial method", "sources"),
            ("Scripture index", "scripture"),
        ]
    ):
        p = doc.add_paragraph()
        hyperlink(p, text, key, internal=True)

    heading("To Florus", 1, "florus")
    para(
        "Julian's six preserved books, as quoted in Augustine's Unfinished Work Against Julian. The book and section numbers below follow that preserving work."
    )
    for b, total in enumerate(SEQUENCE, 1):
        a = load(f"ad_florum_{b}_english.json")
        assert [x["section"] for x in a] == list(range(1, total + 1)), f"Incomplete Book {b}"
        heading(f"Book {b}", 2, f"florus_{b}")
        for x in a:
            s = x["section"]
            add_record(
                x,
                f"F{b}_{s}",
                f"To Florus {b}.{s}",
                f"https://www.augustinus.it/latino/incompiuta_giuliano/incompiuta_giuliano_{b}_libro.htm#JL_{b:03}_{s:03}_{s:03}",
            )

    heading("To Turbantius fragments in Against Julian", 1, "turbantius")
    para(
        "These fragments come from Julian's earlier four-book work addressed to Turbantius. They are arranged by their locations in Augustine's six-book Against Julian. Quotations from other writers that Julian himself used are retained and identified. Separated fragments are printed as separate paragraphs; Augustine's intervening replies are not represented as part of Julian's text."
    )
    for b in range(1, 7):
        heading(f"Witness Book {b}", 2, f"turbantius_{b}")
        for x in load(f"contra_julianum_{b}_english.json"):
            add_record(x, "C" + x["location"].replace(".", "_"), "Against Julian " + x["location"], x["source"])

    heading("Extracts in On Marriage and Concupiscence", 1, "marriage")
    para(
        "Augustine received an intermediary document containing extracts from Julian's earlier reply and answered them in Book Two of On Marriage and Concupiscence. Augustine says that the compiler sometimes shortened, altered, or rearranged the quotations. This section therefore presents a distinct textual witness, including the compiler's framing and Augustine quotations when needed to preserve the argument. Such material is labeled; it is not silently treated as Julian's own new assertion."
    )
    for x in load("marriage2_english.json"):
        add_record(x, "M" + x["location"].replace(".", "_"), "Marriage " + x["location"], x["source"])

    heading("Letter to Rome", 1, "rome")
    para(
        "Fragments from the letter attributed to Julian in Book One of Augustine's Against Two Letters of the Pelagians. Much of the letter describes and attacks the opponents' teaching. Those descriptions must not be mistaken for Julian's own positive beliefs."
    )
    for x in load("letter_to_rome_english.json"):
        add_record(x, "R" + x["location"].replace(".", "_"), "Rome " + x["location"], x["source"])

    heading("Collective letter to Thessalonica", 1, "collective")
    para(
        "Material from the letter sent by Julian and fellow bishops to Thessalonica, preserved in Books Two through Four of Augustine's Against Two Letters of the Pelagians. This was a collective statement; individual authorship of every sentence cannot be established. Augustine says he has passed over part of it, so this is surviving material, not a recovered complete letter. Reported positions are distinguished from direct quotations."
    )
    for x in load("collective_letter_english.json"):
        add_record(x, "L" + x["location"].replace(".", "_"), "Collective letter " + x["location"], x["source"])

    heading("Sources and editorial method", 1, "sources")
    para(
        "Base witnesses: Augustine, Unfinished Work Against Julian, Books One through Six; Against Julian, Books One through Six; On Marriage and Concupiscence, Book Two; Against Two Letters of the Pelagians, Books One through Four. Latin texts and accompanying source notes were consulted in the Augustinus.it electronic edition and retained locally. References use that edition's divisions. The electronic site is not described here as an openly licensed publication; this compilation is prepared for private study."
    )
    p = doc.add_paragraph()
    hyperlink(p, "Augustinus.it Latin works of Augustine", "https://www.augustinus.it/latino/index.htm")
    para(
        "The nineteenth-century English context in Nicene and Post-Nicene Fathers, First Series, Volume Five, edited by Philip Schaff, was available through CCEL for the shorter Augustinian witnesses. The new reading text was translated from Latin; modern copyrighted English editions were not reproduced. Where the Latin electronic text had an obvious gap or mislabeled speaker, the surrounding reply and, where noted, the parallel Italian text were used to identify the problem. The missing clause at To Florus 6.23 and Greek terms at 3.145 were verified directly in the printed Latin of Patrologia Latina 45, columns 1555 and 1306 respectively. Uncertain restorations are marked."
    )
    p = doc.add_paragraph()
    hyperlink(
        p,
        "Printed Latin witness in Patrologia Latina 45",
        "https://www.documentacatholicaomnia.eu/02m/0354-0430%2C_Augustinus%2C_Contra_Secundam_Juliani_Responsionem%2C_MLT.pdf",
    )
    p = doc.add_paragraph()
    hyperlink(p, "CCEL Nicene and Post Nicene Fathers Volume Five", "https://ccel.org/ccel/schaff/npnf105")
    para(
        "The main text contains all 834 numbered Julian sections in the six-book To Florus witness. The supplements collect recoverable excerpts and identified reports from the stated witnesses. Scripture references were checked against quotation wording where source note numbers were missing or misaligned. The most substantial unresolved readings are identified at their locations. The absence of a separately printed repeated fragment does not imply that the parallel witness has been lost."
    )

    if tn_records:
        add_heading_with_headword(doc, bookmarks, "Translator notes", 1, "translation_notes")
        doc.add_paragraph(
            "Numbered marks in the chapters open these notes. They flag lacunae, "
            "wording choices, and rough passages — not Julian's text."
        )
        for rec in tn_records:
            hw = rec["headword"]
            add_heading_with_headword(doc, bookmarks, hw, 3, f"tn_{rec['n']}")
            doc.add_paragraph(rec["note"])
            doc.add_paragraph(rec["citation"], style="Caption")

    heading("Scripture index", 1, "scripture")
    para(
        "Select a Bible reference to open Scripture; select a section label to return to its discussion. Reference ranges are retained as ranges. 'Note' identifies editorial discussion, which may include comparison passages and corrected source citations."
    )
    from pipeline.bible_links import index_book_heading

    last = None
    for ref, entries in sorted(linker.index.items(), key=lambda x: sort_ref_key(x[0])):
        book = index_book_heading(ref)
        if book != last:
            heading(book, 2, "idx_" + book.replace(" ", "_"))
            last = book
        p = doc.add_paragraph()
        p.add_run(linker.bible_text(ref)).bold = True
        p.add_run(" — ")
        for i, (key, label) in enumerate(entries):
            if i:
                p.add_run("; ")
            hyperlink(p, label, key, internal=True)

    assert_internal_links(doc, bookmarks.ids)
    assert len([r for r in records if r["key"].startswith("F")]) == 834
    assert "[[Romans 5:12 >> Bible:Romans 5:12]]" in linker.bible_text("Romans 5:12")
    assert "Bible:Psalm 32:1-2" in linker.bible_text("Psalm 32:1–2; LXX Psalm 31:1–2")
    assert REF.findall("1 Corinthians 15:36, 38; 16:1")
    assert [m.group() for m in REF.finditer("Hebrews 12:22–23; 1 Corinthians 12:13")] == [
        "Hebrews 12:22–23",
        "1 Corinthians 12:13",
    ]
    assert [m.group() for m in REF.finditer("Genesis 1:27, 2 Corinthians 4:6")] == [
        "Genesis 1:27",
        "2 Corinthians 4:6",
    ]
    doc.save(OUT)

    receipt = {
        "title": "Julian of Eclanum: Surviving Arguments Preserved by Augustine",
        "section_count": len(records),
        "paragraph_count": sum(r["paragraphs"] for r in records),
        "bookmark_count": len(bookmarks.ids),
        "footnote_count": 0,
        "tn_note_count": len(tn_records),
        "bible_links": linker.link_receipts,
        "scripture_index_entries": sum(len(v) for v in linker.index.values()),
        "records": records,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                output=str(OUT),
                sections=len(records),
                bible_links=len(linker.link_receipts),
                index_entries=len(linker.index),
                bytes=OUT.stat().st_size,
            )
        )
    )


if __name__ == "__main__":
    main()