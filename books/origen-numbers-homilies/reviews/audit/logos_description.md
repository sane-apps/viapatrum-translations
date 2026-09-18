# Logos Personal Book — description stub

**Work:** Origen of Alexandria, *Homilies on Numbers* (Homilies I–II, IV–XXVIII)
**Slug:** `origen-numbers-homilies`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/origen-numbers-homilies/origen-numbers-homilies.docx`

## Short description (paste into Logos Personal Books)

Origen of Alexandria, Homilies on Numbers — a new English rendering for private study from the locked Baehrens Latin (GCS 30, 1921), Rufinus's Latin version of the homilies. This volume holds Homilies I–II and IV–XXVIII (83 sections); Homily III is absent through an unrecoverable title lacuna in the copy-text, so this volume is not presented as a complete 28-of-28 text. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title/edition: `book.yml` → author "Origen of Alexandria", title "Origen: Homilies on Numbers", edition_lock "Baehrens, Origenes Werke VII = GCS 30 (1921)", scope "28 Numbers homilies (Rufinus Latin) as in Baehrens GCS 30."
- Contents: `build_book.py` FRONT_MATTER → "Scope: Numbers Homiliae I–II and IV–XXVIII in Rufinus's Latin as printed in Baehrens GCS 30"; receipt 83 records from num_hom1/2/4–28 English JSON (no num_hom3 file in `translations/`).
- Limit: FRONT_MATTER "Homilia III is absent from this build: the Baehrens OCR/scan has an unrecoverable title lacuna … Do not present this Personal Book as 28/28 complete text."; "Scheck FOTC is not the reading text."
