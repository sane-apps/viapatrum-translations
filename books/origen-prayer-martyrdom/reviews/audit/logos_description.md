# Logos Personal Book — description stub

**Work:** Origen, *On Prayer and Exhortation to Martyrdom*
**Slug:** `origen-prayer-martyrdom`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/origen-prayer-martyrdom/origen-prayer-martyrdom.docx`

## Short description (paste into Logos Personal Books)

Origen, On Prayer and Exhortation to Martyrdom — a new English rendering for private study from the Greek text of the GCS Koetschau edition, both works lacking a public-domain English version. This volume holds the complete On Prayer (34 chapters) and the complete Exhortation to Martyrdom (proem and 51 chapters). Passages marked rough still await page-image verification against the GCS edition. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

## Cover-art notes (Air)

- Series cover, mandatory: same layout, typography, and palette as every other book; author, English title, original-language subtitle.
- No logosres: assets. After Build: TN hover must open TN n, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest DOCX (`python3 -m pipeline.verify_docx` green).
4. Paste short description above; attach the series cover (required); confirm DOCX title/author properties match `book.yml`.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. `resource_id` already recorded in `book.yml` (PBB:4f41cb276f014e1aa7ee22103e299a76); update docs/LOGOS_BACKLOG.md.

## Evidence (repo sources — not pasted into Logos)

- Author/title: `book.yml` → author "Origen", title "Origen: On Prayer and Exhortation to Martyrdom", resource_id "PBB:4f41cb276f014e1aa7ee22103e299a76".
- Edition/contents: `build_book.py` FRONT_MATTER → "from the Greek text of the GCS Koetschau edition", "Scope: the complete On Prayer (34 chapters) and the complete Exhortation to Martyrdom (proem and 51 chapters) — works of Origen lacking a public-domain English version."; locks `sources/gcs3_gebet_slice.txt`, `sources/gcs2_martyrium_slice.txt`.
- Build: `build_receipt.json` title "Origen: On Prayer and Exhortation to Martyrdom (New English)", 86 records from gebet_english.json and martyrium_english.json.
- Limit: FRONT_MATTER "Passages marked rough await page-image verification against the GCS edition."
