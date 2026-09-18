# Logos Personal Book — description stub

**Work:** Paulus Silentarius, *Descriptio Ambonis* (Ekphrasis of the Ambo)
**Slug:** `paulus-silentarius-ambonis`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/paulus-silentarius-ambonis/paulus-silentarius-ambonis English.docx`

## Short description (paste into Logos Personal Books)

Paulus Silentarius, Description of the Ambo of Hagia Sophia — a new English rendering for private study from the locked Greek (PG 86b / Friedländer 1912). The poem (275 hexameter verses with a 29-verse trimeter prologue) was recited separately after the main Hagia Sophia ekphrasis, likely at Epiphany 563. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Paulus Silentarius", title "Paulus Silentarius: Descriptio Ambonis".
- Edition/date: `build_book.py` FRONT_MATTER → "from locked Greek (PG 86b / Friedländer 1912)", "recited separately after the main ekphrasis, likely at Epiphany 563 AD"; lock `sources/paulus_silentarius_ambonis_greek_lock.txt`; "Lethaby & Swainson 1894 (Hakluyt Society) used as PD English reference only."
- Contents: FRONT_MATTER "Scope: Full work densify — 275 hexameter verses + 29 trimeter prologue."; receipt 8 records from ambon_body_english.json and ambon_prologue_english.json.
