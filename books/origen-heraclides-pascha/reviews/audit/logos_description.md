# Logos Personal Book — description stub

**Work:** Origen, *Dialogue with Heraclides and On Pascha*
**Slug:** `origen-heraclides-pascha`
**Resource type:** Monograph · **Language:** English
**Site:** https://fathers.saneapps.com/works/origen-dialogue-heraclides/ (+ https://fathers.saneapps.com/works/origen-on-pascha/)
**Body DOCX:** `books/origen-heraclides-pascha/origen-heraclides-pascha.docx`

## Short description (paste into Logos Personal Books)

Origen, Dialogue with Heraclides and On Pascha — a new English rendering for private study from the locked Greek of two Toura-papyrus recoveries that lack a public-domain English version. Damaged papyrus is marked [lacuna], and editorial fillings are not treated as Origen's text. On Prayer and the Exhortation to Martyrdom belong to a separate volume, not this one. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

## Cover-art notes (Air)

- Series cover, mandatory: same layout, typography, and palette as every other book; author, English title, original-language subtitle.
- No logosres: assets. After Build: TN hover must open TN n, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest DOCX (`python3 -m pipeline.verify_docx` green).
4. Paste short description above; attach the series cover (required); confirm DOCX title/author properties match `book.yml`.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. Record `resource_id` in `book.yml`; update docs/LOGOS_BACKLOG.md.

## Evidence (repo sources — not pasted into Logos)

- Author/title: `book.yml` → author "Origen", title "Origen — Dialogue with Heraclides and On Pascha".
- Edition/contents: `build_book.py` FRONT_MATTER → "from locked Greek", "Scope: Dialogue with Heraclides and On Pascha — Toura-papyrus recoveries that lack a public-domain English version."; locks `sources/heraclides_greek.txt`, `sources/pascha_witte_greek_ocr.txt`.
- Build: `build_receipt.json` title "Origen: Dialogue with Heraclides and On Pascha (New English)", 177 records from heraclides_english.json and pascha_english.json.
- Limits: FRONT_MATTER "Prayer and Martyrdom are in a separate book. Contra Celsum and De Principiis are out of scope here."; "Damaged papyrus is marked [lacuna]. Editorial fillings are not treated as Origen's text."
- Site: docs/LOGOS_BACKLOG.md → /works/origen-dialogue-heraclides/ (+ /works/origen-on-pascha/).
