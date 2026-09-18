# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus, *Twelve Chapters on the Faith* (Capita I–II, tip)
**Slug:** `gregory-thaumaturgus-de-fide-xii`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-de-fide-xii/gregory-thaumaturgus-de-fide-xii.docx`

## Short description (paste into Logos Personal Books)

Gregory Thaumaturgus, Twelve Chapters on the Faith — a new English rendering for private study from the locked Vossius 1684 text. This tip covers Chapters 1–2 (the body of Christ as created flesh of the uncreated Word; the flesh not consubstantial with the Godhead); Chapters 3–12 are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: Twelve Chapters on the Faith".
- Edition: `build_book.py` FRONT_MATTER → "from locked Vossius 1684 Latin"; lock `sources/_fide12_latin_lock.txt`; "Prior English (ANF 6 Crombie, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Twelve Chapters on the Faith (Duodecim Capita). Tip covers Capita I–II"; receipt 2 records from fide_xii_english.json ("Chapter 1 — The body of Christ is created flesh of the uncreated Word", "Chapter 2 — The flesh is not consubstantial with the Godhead").
- Limit: Capita III–XII have no translation file in `translations/` (only fide_xii_english.json) and no receipt records.
