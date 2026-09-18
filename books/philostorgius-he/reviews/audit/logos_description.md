# Logos Personal Book — description stub

**Work:** Philostorgius, *Ecclesiastical History* (Book 1 in this volume)
**Slug:** `philostorgius-he`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/philostorgius-he/philostorgius-he.docx`

## Short description (paste into Logos Personal Books)

Philostorgius, Ecclesiastical History — a new English rendering for private study from the locked Greek. This volume currently holds Book 1 only (the Maccabean judgments, Arius, and Constantine); the remaining books toward the full twelve are not in this volume yet. The source edition is still to be declared in the volume metadata. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Philostorgius", title "Philostorgius: Ecclesiastical History"; edition field is empty ("fill when source locked").
- Edition: `build_book.py` FRONT_MATTER → "Source edition to be declared in meta.json."; lock `sources/_phil1_greek_lock.txt`; "Prior English (Walford 1855) consulted only as sense/style check."
- Contents/limit: FRONT_MATTER "Scope: Philostorgius, Ecclesiastical History (Books 1–12 as preserved)."; but `build_receipt.json` holds exactly 1 record from ecclesiastical_history_english.json ("Book 1 — Book 1: Maccabees judgments, Arius, and Constantine"), so only Book 1 is in this DOCX.
