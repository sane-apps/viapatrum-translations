# Logos Personal Book — description stub

**Work:** Cyril of Alexandria, *On the True Faith to the Imperial Women* (two court treatises)
**Slug:** `cyril-alexandria-recta-fide-court`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/cyril-alexandria-recta-fide-court/cyril-alexandria-recta-fide-court English.docx`

## Short description (paste into Logos Personal Books)

Cyril of Alexandria, On the True Faith to the Imperial Women — a first English rendering for private study of two court treatises from the locked Pusey 1877 Greek: To the Princesses Arcadia and Marina (100 sections) and To the Augustas Pulcheria and Eudocia (48 sections). The companion treatise To Theodosius is not in this volume, as it already has a modern English version. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Cyril of Alexandria", title "Cyril of Alexandria: On the True Faith to the Imperial Women".
- Edition: `build_book.py` FRONT_MATTER → "from locked Greek (Pusey 1877, PG 76)"; lock source `sources/pusey1877_de_recta_fide_djvu.txt`.
- Contents: FRONT_MATTER "Scope: two court treatises — De recta fide ad dominas (CPG 5219, §§1–100) and De recta fide ad augustas (CPG 5220, §§1–48)"; receipt 148 records (100x ad_arcadiam_marinamque_english.json, 48x ad_pulcheriam_eudociamque_english.json).
- Limits: FRONT_MATTER "The treatise ad Theodosium (CPG 5218) is excluded as it has a modern English in King FC 129"; "First English of these two court treatises from the locked Pusey 1877 Greek."
