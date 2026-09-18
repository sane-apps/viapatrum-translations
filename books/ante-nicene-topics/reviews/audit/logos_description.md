# Logos Personal Book — description stub

**Work:** Ante-Nicene Fathers, *Ante-Nicene Dogmatics* (topical library)
**Slug:** `ante-nicene-topics`
**Resource type:** Encyclopedia · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/ante-nicene-topics/Ante-Nicene Dogmatics Soteriology and Free Will.docx`

## Short description (paste into Logos Personal Books)

Modern English excerpts from the ante-Nicene fathers, arranged by the main topics of Christian teaching for private study, prepared as a new English topical library in 2026. This volume presents the Soteriology and Free Will locus. It is not a complete dogmatics and not a critical edition of the Greek or Latin. Bible quotations are linked inline for Logos KeyLinking. AI-assisted private study; no modern copyrighted English was copied.

## Cover-art notes (Air)

- Series cover, mandatory: same layout, typography, and palette as every other book; English title, original-language subtitle line.
- No logosres: assets. After Build: TN hover must open TN n, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest DOCX (`python3 -m pipeline.verify_docx` green).
4. Paste short description above; attach the series cover (required); confirm DOCX title/author properties match `book.yml`.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. Record `resource_id` in `book.yml`; update docs/LOGOS_BACKLOG.md.

## Evidence (repo sources — not pasted into Logos)

- Author/kind: `book.yml` → title "Ante-Nicene Dogmatics", author "Ante-Nicene Fathers (modern English topical library)", resource_type Encyclopedia; `build_book.py` BOOK_META "authors": "Ante-Nicene Fathers (topical library)", "copyright": "Ancient texts; new English topical library prepared for private study, 2026."
- Scope/limits: BOOK_META "description" ends "Not a complete dogmatics and not a critical edition of the Greek or Latin."; `book.yml` mvp_loci anthropology, soteriology; body file is the Soteriology and Free Will DOCX.
- Build: `build_receipt.json` section_count 1237 with inline Bible links; `translations/topics/` holds bibliology_pneumatology, ecclesiology_sacraments, eschatology_ethics, soteriology_free_will, theology_christology JSON.
