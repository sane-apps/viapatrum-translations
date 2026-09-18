# Logos Personal Book — description stub

**Work:** Epiphanius of Salamis, *Anacephalaeosis* (tip)
**Slug:** `epiphanius-anacephalaeosis`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/epiphanius-anacephalaeosis/epiphanius-anacephalaeosis.docx`

## Short description (paste into Logos Personal Books)

Epiphanius of Salamis, Anacephalaeosis — a new English rendering for private study from the locked PG 41 Greek. This tip covers the recapitulation opening (eighty heresies by book and tome); the remainder is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Epiphanius of Salamis", title "Epiphanius: Anacephalaeosis".
- Edition: `build_book.py` FRONT_MATTER → "from locked PG 41 Greek", "Greek copy-text is PG 41 page-image OCR (tesseract grc+eng)"; lock `sources/_anacephalaeosis_greek_lock.txt`.
- Contents: FRONT_MATTER "Scope: Epiphanius Anacephalaeosis. Tip covers the recapitulation opening"; receipt 1 record from anacephalaeosis_english.json ("Recapitulation: eighty heresies by book and tome").
- Limit: FRONT_MATTER "remainder remains."
