# Logos Personal Book — description stub

**Work:** Epiphanius of Salamis, *Panarion* (Haer. I Cap. V, tip)
**Slug:** `epiphanius-panarion`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/epiphanius-panarion/epiphanius-panarion.docx`

## Short description (paste into Logos Personal Books)

Epiphanius of Salamis, Panarion — a new English rendering for private study from the locked PG 41 Greek. This tip covers Heresy I Chapter V (no heresy yet: Adam as prophet of Father, Son, and Spirit); the remainder of the Panarion is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Epiphanius of Salamis", title "Epiphanius: Panarion".
- Edition: `build_book.py` FRONT_MATTER → "from locked PG 41 Greek", "Greek copy-text is PG 41 page-image OCR (tesseract grc+eng)"; lock `sources/_panarion_greek_lock.txt`.
- Contents: FRONT_MATTER "Scope: Epiphanius Panarion. Tip covers Haer. I Cap. V"; receipt 1 record from panarion_english.json ("Haer. I Cap. V: no heresy yet; Adam prophet of Father, Son, Spirit").
- Limit: FRONT_MATTER "remainder remains."
