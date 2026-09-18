# Logos Personal Book — description stub

**Work:** John Davenant, *Dissertationes duae* (De morte Christi, tip)
**Slug:** `davenant-dissertationes-duae`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/davenant-dissertationes-duae/davenant-dissertationes-duae.docx`

## Short description (paste into Logos Personal Books)

John Davenant, Dissertationes duae — a new English rendering for private study from the locked 1650 Cambridge Latin. This tip covers De morte Christi Chapter 1 (the origin of the controversy and Thesis 1, on the death of Christ as a universal remedy) in 2 sections; the remainder of the Dissertationes is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "John Davenant", title "Dissertationes duae (De morte Christi tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1650 Cambridge Daniel Latin", "Cambridge: Roger Daniel, 1650", "Wing D317 / ESTC R5446"; lock `sources/_davenant_morte_christi_latin_lock.txt`.
- Contents: FRONT_MATTER "Scope: tip only — De morte Christi Cap. 1 (controversy origin + Thesis 1)"; receipt 2 records from morte_christi_english.json.
- Limit: FRONT_MATTER "Remainder of Dissertationes duae remains."; "Allport 1831 Colossians English was not used."
