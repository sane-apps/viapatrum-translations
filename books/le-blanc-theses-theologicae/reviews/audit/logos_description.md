# Logos Personal Book — description stub

**Work:** Louis Le Blanc de Beaulieu, *Theological Theses* (De Theologia I–VII, tip)
**Slug:** `le-blanc-theses-theologicae`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/le-blanc-theses-theologicae/le-blanc-theses-theologicae.docx`

## Short description (paste into Logos Personal Books)

Louis Le Blanc de Beaulieu, Theological Theses — a new English rendering for private study from the locked 1675 London Latin. This tip covers the Theses on Theology I–VII (theology as speech about God; whether it is required for salvation and for the church) in 2 sections; the remainder of the collected Theses is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Louis Le Blanc de Beaulieu", title "Theological Theses (De Theologia tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1675 London Pitt folio", "London: Moses Pitt, 1675", "Public Domain Mark 1.0"; lock `sources/_le_blanc_theologia_latin_lock.txt`; "The 2024 AI English of the 1683 text was not used."
- Contents: FRONT_MATTER "Scope: tip only — Theses de Theologia I–VII"; receipt 2 records from theses_theologia_english.json ("speech about God", "not required of every person for salvation, yet the church cannot stand without it").
- Limit: FRONT_MATTER "Remainder of the collected Theses remains."
