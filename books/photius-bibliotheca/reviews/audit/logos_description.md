# Logos Personal Book — description stub

**Work:** Photius of Constantinople, *Bibliotheca* (Codices 1–15, tip)
**Slug:** `photius-bibliotheca`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/photius-bibliotheca/photius-bibliotheca English.docx`

## Short description (paste into Logos Personal Books)

Photius of Constantinople, Bibliotheca (the Myriobiblon) — a new English rendering for private study from the locked Bekker 1824 Greek. This tip holds the opening Codices 1–15, from Theodore on Dionysius through Gelasius on Nicaea, including the Eusebius and Origen entries; Codices 16–279 are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Photius of Constantinople", title "Photius: Bibliotheca (Myriobiblon)".
- Edition: `build_book.py` FRONT_MATTER → "from locked Greek (Bekker 1824). Freese 1920 (PD English, codices 1-165) used as reference only — not copied."; lock `sources/photius_bibliotheca_greek_lock.txt`.
- Contents: `build_book.py` CODEX_FILES lists bibl_codex_1–15 English JSON; `build_receipt.json` holds 15 records (Codex 1 Theodore on Dionysius; 2 Hadrian; 3 Nonnosus; 4 Theodore of Mopsuestia; 5 Sophronius; 6–7 Gregory of Nyssa; 8 Origen De Principiis; 9–13 Eusebius; 14 Apollinarius; 15 Gelasius on Nicaea).
- Limits/flags: Codices 16–279 have no receipt records, so they are not in this DOCX. NOTE: FRONT_MATTER line 44 and the receipt title still say "first 5 codices" / "Codices 1–5" — stale strings that understate the built 15-codex volume; builder/receipt owners should update them (out of scope for this description-only change).
