# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus, *Metaphrasis in Ecclesiasten* (Cap. I opening, tip)
**Slug:** `gregory-thaumaturgus-ecclesiastes-metaphrase`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-ecclesiastes-metaphrase/gregory-thaumaturgus-ecclesiastes-metaphrase.docx`

## Short description (paste into Logos Personal Books)

Gregory Thaumaturgus, Paraphrase of Ecclesiastes — a new English rendering for private study from the locked MGR Greek. This tip covers the Chapter I opening (Solomon to the Church: human affairs empty, nothing new under the sun); the remainder is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: Ecclesiastes metaphrase".
- Edition: `build_book.py` FRONT_MATTER → "Greek copy-text is the MGR concordance extract (TLG 2063.006). Vossius 1684 Latin column DjVu OCR is retained as a check witness only."; lock `sources/_eccl_metaphrase_greek_lock.txt`; "Prior English (ANF 4 Crombie, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Metaphrasis in Ecclesiasten. Tip covers Cap. I opening … through Solomon as king in Jerusalem"; receipt 1 record from eccl_metaphrase_english.json ("Cap. I opening: Solomon to the Church — human affairs empty; nothing new under the sun").
- Limit: FRONT_MATTER "remainder remains."
