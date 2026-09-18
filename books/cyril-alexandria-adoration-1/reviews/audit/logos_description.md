# Logos Personal Book — description stub

**Work:** Cyril of Alexandria, *On Adoration and Worship in Spirit and Truth*, Book 1
**Slug:** `cyril-alexandria-adoration-1`
**Resource type:** Monograph · **Language:** English
**Site:** https://fathers.saneapps.com/works/cyril-adoration-1/
**Body DOCX:** `books/cyril-alexandria-adoration-1/cyril-alexandria-adoration-1.docx`

## Short description (paste into Logos Personal Books)

Cyril of Alexandria (patriarch 412–444), On Adoration and Worship in Spirit and Truth — a new English rendering for private study from the locked Migne PG 68 Greek. This volume holds Book 1 only (39 sections, on worship in spirit and truth through the types and shadows of the Law); Books 2–17 are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Cyril of Alexandria", title "Cyril of Alexandria: On Adoration and Worship in Spirit and Truth, Book 1".
- Date: `build_book.py` FRONT_MATTER → "Cyril wrote in the early fifth century (patriarch 412–444)."
- Edition/contents: FRONT_MATTER → "from locked Greek (Migne PG 68)", "Scope: Book 1 only … (CPG 5200). Books 2–17 are not in this volume. This is not Cyril of Jerusalem."; lock `sources/adoration_book1_greek_clean.txt`.
- Build: `build_receipt.json` title "Cyril of Alexandria: On Adoration and Worship in Spirit and Truth, Book 1", 39 records all from adoration1_english.json.
- Site: docs/LOGOS_BACKLOG.md → https://fathers.saneapps.com/works/cyril-adoration-1/.
