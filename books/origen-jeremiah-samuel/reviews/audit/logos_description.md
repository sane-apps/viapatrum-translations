# Logos Personal Book — description stub

**Work:** Origen of Alexandria, *Homilies on Jeremiah and on 1 Samuel 28*
**Slug:** `origen-jeremiah-samuel`
**Resource type:** Monograph · **Language:** English
**Site:** https://fathers.saneapps.com/works/origen-homilies-jeremiah/ (+ https://fathers.saneapps.com/works/origen-homily-1samuel-28/)
**Body DOCX:** `books/origen-jeremiah-samuel/origen-jeremiah-samuel.docx`

## Short description (paste into Logos Personal Books)

Origen of Alexandria, Homilies on Jeremiah and on 1 Samuel 28 — a new English rendering for private study from the locked Klostermann Greek (GCS, 1901). This volume holds the opening Jeremiah homilies (155 sections, from Jeremiah 1:2–10 forward) and the Homily on 1 Samuel 28 (10 sections); the two further Jeremiah homilies surviving only in Jerome's Latin, and the Lamentations fragments, are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Origen of Alexandria", title "Origen: Homilies on Jeremiah and on 1 Samuel 28".
- Edition: `build_book.py` FRONT_MATTER → "from locked Greek (Klostermann, GCS Orig. III, 1901)"; lock sources under `sources/` (origeneswerke03orig).
- Contents: `build_receipt.json` title "Origen: Homilies on Jeremiah and on 1 Samuel 28 (New English)", 165 records (155x jeremiah_english.json covering Homilies 1–3 material, 10x samuel_english.json).
- Limits: FRONT_MATTER "Two further Jeremiah homilies survive only in Jerome's Latin and are not here yet."; `translations/lamentations_english.json` exists but has no receipt records, so Lamentations is not in this DOCX.
- Site: docs/LOGOS_BACKLOG.md → /works/origen-homilies-jeremiah/ (+ /works/origen-homily-1samuel-28/).
