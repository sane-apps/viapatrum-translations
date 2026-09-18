# Logos Personal Book — description stub

**Work:** Paulus Silentarius, *Descriptio Sanctae Sophiae* (Ekphrasis of Hagia Sophia)
**Slug:** `paulus-silentarius-sophia`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/paulus-silentarius-sophia/paulus-silentarius-sophia English.docx`

## Short description (paste into Logos Personal Books)

Paulus Silentarius, Description of Hagia Sophia — a new English rendering for private study from the locked Greek (PG 86b / Friedländer 1912). The 1,046 hexameter verses celebrate the church's rededication on 24 December 563 in three movements: the dome and nave, the exedras and piers, then the ambo and conclusion. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Paulus Silentarius", title "Paulus Silentarius: Descriptio Sanctae Sophiae".
- Edition/date: `build_book.py` FRONT_MATTER → "from locked Greek (PG 86b / Friedländer 1912)", "recited at the rededication of Hagia Sophia, 24 December 563 AD"; lock `sources/paulus_silentarius_greek_lock.txt`; "Lethaby & Swainson 1894 (Hakluyt Society) used as PD English reference only."
- Contents: FRONT_MATTER "Scope: Paul the Silentiary's Ekphrasis of Hagia Sophia (1046 hexameter verses) … Three parts: (1) The Dome and Nave, (2) The Exedras and Piers, (3) The Ambo and Conclusion."; receipt 8 records from sophia_part1/2/3_english.json.
