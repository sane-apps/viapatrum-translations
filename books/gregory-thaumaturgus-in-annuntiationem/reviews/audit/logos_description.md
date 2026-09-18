# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus, *On the Annunciation* (Sermo I opening, tip)
**Slug:** `gregory-thaumaturgus-in-annuntiationem`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-in-annuntiationem/gregory-thaumaturgus-in-annuntiationem.docx`

## Short description (paste into Logos Personal Books)

Gregory Thaumaturgus, On the Annunciation to the Holy Virgin Mary — a new English rendering for private study from the locked Vossius 1684 Latin. This tip covers the opening of the First Discourse (the joy of the day, David's oracle, Gabriel's hail through his reply); the rest of Sermo I and Sermones II–III are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: In annuntiationem".
- Edition: `build_book.py` FRONT_MATTER → "from locked Vossius 1684 Latin"; lock `sources/_annuntiationem_latin_lock.txt`; "Prior English (ANF 6 Salmond, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: In annuntiationem sanctissimae Dei genitricis Virginis Mariae, Sermo I. Tip covers opening through Gabriel reply"; receipt 1 record from annunciation_english.json ("Sermo I opening: today's joy, David's oracle, and Gabriel's hail").
- Limits: FRONT_MATTER "Sermones II–III and the rest of Sermo I remain."; "Vossius scholia … were stripped from the lock. Greek column OCR is damaged and is not copy-text."
