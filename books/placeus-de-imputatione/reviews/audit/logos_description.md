# Logos Personal Book — description stub

**Work:** Josué de la Place (Placeus), *De imputatione primi peccati Adami* (Caput Primum, tip)
**Slug:** `placeus-de-imputatione`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/placeus-de-imputatione/placeus-de-imputatione.docx`

## Short description (paste into Logos Personal Books)

Josué de la Place, On the Imputation of Adam's First Sin — a new English rendering for private study from the locked 1661 Saumur Latin. This tip covers the First Chapter (the Charenton National Synod decree on original sin and Placeus's framing reply, answering the rumor of his condemnation) in 2 sections; the remainder is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Josué de la Place (Placeus)", title "De imputatione primi peccati Adami (Caput Primum tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1661 Saumur Latin", "Salmurii: Apud Ioannem Lesnerium, 1661", "Public domain. Saumur faculty / Amyraldian circle; Amyraut French Brief traité not used."; lock `sources/_placeus_cap1_latin_lock.txt`.
- Contents: FRONT_MATTER "Scope: tip only — Caput Primum (Charenton National Synod decree + Placeus framing)"; receipt 2 records from cap1_tip_english.json ("The Charenton decree …", "Placeus was not condemned: rumor, silence, and the author's purpose").
- Limit: FRONT_MATTER "Remainder of De imputatione primi peccati Adami remains."
