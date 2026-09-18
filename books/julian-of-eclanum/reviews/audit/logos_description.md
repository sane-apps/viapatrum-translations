# Logos Personal Book — description stub

**Work:** Julian of Eclanum, *Surviving Arguments Preserved by Augustine*
**Slug:** `julian-of-eclanum`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/julian-of-eclanum/Julian of Eclanum English.docx`

## Short description (paste into Logos Personal Books)

Julian of Eclanum, Surviving Arguments Preserved by Augustine — a new AI-assisted English translation from the Latin (2026) gathering what survives of Julian's case: his six books To Florus as quoted across Augustine's Unfinished Work, his books Against Julian and On Marriage and Concupiscence, together with the fragments To Turbantius, the Letter to Rome, and the Collective Letter to Thessalonica. Julian's own works are lost, so every passage here reaches us through Augustine's quotation. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes).

## Cover-art notes (Air)

- Series cover, mandatory: same layout, typography, and palette as every other book; author, English title, original-language subtitle.
- No logosres: assets. After Build: TN hover must open TN n, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest DOCX (`python3 -m pipeline.verify_docx` green).
4. Paste short description above; attach the series cover (required); confirm DOCX title/author properties match `book.yml`.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. `resource_id` already recorded in `book.yml` (PBB:49ea9d72e8d7414782017dd81625e605); update docs/LOGOS_BACKLOG.md.

## Evidence (repo sources — not pasted into Logos)

- Author/title: `book.yml` → author "Julian of Eclanum", title "Julian of Eclanum: Surviving Arguments Preserved by Augustine", resource_id "PBB:49ea9d72e8d7414782017dd81625e605".
- Edition/date: `build_book.py` FRONT_MATTER → "Private study edition. New AI-assisted translation from Latin, 2026."
- Contents: FRONT_MATTER "Scope: Julian's six books To Florus (preserved in Augustine's Unfinished Work Against Julian), fragments To Turbantius, extracts in On Marriage and Concupiscence, Letter to Rome, and Collective Letter to Thessalonica."; receipt 1164 records whose sources span augustinus.it incompiuta_giuliano (books 1–6), contro_giuliano (books 1–6), contro_pelagiani, and nozze_concupiscenza; `translations/` holds ad_florum_1–6 English JSON.
- Limit: Julian's works survive only as quoted by Augustine (title and source base); this volume adds no complete independent Julian text.
