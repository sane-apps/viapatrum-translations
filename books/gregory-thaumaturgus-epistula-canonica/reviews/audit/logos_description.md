# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus, *Epistula Canonica* (Canon I, tip)
**Slug:** `gregory-thaumaturgus-epistula-canonica`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-epistula-canonica/gregory-thaumaturgus-epistula-canonica.docx`

## Short description (paste into Logos Personal Books)

Gregory Thaumaturgus, Canonical Epistle — a new English rendering for private study from the locked Canones Greek. This tip covers Canon I (on captives eating food set before them by the barbarians, and on captive women under force); Canons II–XI are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: Epistula canonica".
- Edition: `build_book.py` FRONT_MATTER → "Greek copy-text is the Documenta Catholica Omnia Canones GR extract. Vossius 1684 DjVu retained as a check witness only."; lock `sources/_epistula_canonica_greek_lock.txt`; "Prior English (ANF, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Epistula Canonica. Tip covers Canon I … (captives eating food set by barbarians; captive women under force)"; receipt 1 record from epistula_canonica_english.json with the same label.
- Limit: FRONT_MATTER "Canons II–XI remain."
