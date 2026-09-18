# Logos Personal Book — description stub

**Work:** Ludwig Crocius, *Syntagma sacrae theologiae* (Liber I Cap. 1, tip)
**Slug:** `crocius-syntagma`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/crocius-syntagma/crocius-syntagma.docx`

## Short description (paste into Logos Personal Books)

Ludwig Crocius, Syntagma sacrae theologiae — a new English rendering for private study from the locked 1636 Bremen Latin. This tip covers Liber Primus Caput Primum on the definition of theology (sacred over against profane, a practical habit ordered to faith and eternal life) in 2 sections; the remainder of the Syntagma is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Ludwig Crocius", title "Syntagma sacrae theologiae (Liber I Cap. 1 tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1636 Bremen Villerian Latin", "Bremen: Berthold Villerian, 1636", "SLUB id335860389 / VD17 14:684303C"; lock `sources/_crocius_liber1_cap1_latin_lock.txt`.
- Contents: FRONT_MATTER "Scope: tip only — Liber Primus Caput Primum De Theologiae definitione"; receipt 2 records from liber1_cap1_english.json ("practical habit", "sacred over against profane science").
- Limit: FRONT_MATTER "Remainder of the Syntagma remains."
