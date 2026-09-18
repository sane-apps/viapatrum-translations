# Logos Personal Book — description stub

**Work:** Epiphanius of Salamis, *Ancoratus* (Cap. II, tip)
**Slug:** `epiphanius-ancoratus`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/epiphanius-ancoratus/epiphanius-ancoratus.docx`

## Short description (paste into Logos Personal Books)

Epiphanius of Salamis, Ancoratus — a new English rendering for private study from the locked PG 43 Greek. This tip covers Chapter II (the Spirit given to seekers, Peter's confession, the Trinity in unity); the remainder of the Ancoratus is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Epiphanius of Salamis", title "Epiphanius: Ancoratus".
- Edition: `build_book.py` FRONT_MATTER → "from locked PG 43 Greek", "Greek copy-text is PG 43 Ancoratus Cap. II from page-image OCR (tesseract grc+eng)"; lock `sources/_ancoratus_greek_lock.txt`.
- Contents: FRONT_MATTER "Scope: Ancoratus. Tip covers Cap. II … (Spirit given to seekers; Peter confession; Trinity in unity)"; receipt 1 record from ancoratus_english.json with the same label.
- Limit: FRONT_MATTER "remainder remains."
