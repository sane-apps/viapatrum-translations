# Logos Personal Book — description stub

**Work:** Nemesius of Emesa, *De natura hominis* (On Human Nature)
**Slug:** `nemesius-de-natura-hominis`
**Resource type:** Monograph · **Language:** English
**Site:** https://fathers.saneapps.com/works/nemesius-de-natura-hominis/
**Body DOCX:** `books/nemesius-de-natura-hominis/nemesius-de-natura-hominis.docx`

## Short description (paste into Logos Personal Books)

Nemesius of Emesa, On Human Nature — a new English rendering for private study from locked Wither 1636 Greek OCR (checked against PG 86 and BIUSante). This tip densify covers soul arguments in sections 1.1–3.1: the soul as living substance in act, not the body’s entelechy; refusals of soul-as-blood, breath, harmony, or number; and Moses on God’s rest with inline Scripture links (Genesis 2:2; John 5:17). Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied. Wither’s 1636 English exists (PD); this is a fresh densify from the Greek OCR, not a claim of first-ever English.

## Cover-art notes (Air)

- Prefer a simple monograph cover: title *Nemesius: De natura hominis*, subtitle *New English (tip densify)*, author line Nemesius of Emesa.
- Avoid library-specific logosres art assets; keep cover portable across libraries.
- After Build: hover a TN mark → must open `TN n`, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest `nemesius-de-natura-hominis.docx` (verify_docx green).
4. Paste short description above; add cover when ready.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. Record `resource_id` in `book.yml` and mark Logos status compiled in `docs/LOGOS_BACKLOG.md`.

## Markup audit (2026-09-15)

- `pipeline.verify_docx` OK; no `footnotes.xml`.
- Inline Bible: `[[Genesis 2:2 >> Bible:Genesis 2:2]]`, `[[John 5:17 >> Bible:John 5:17]]`.
- Headword TN 1–24 present; headings H1–H3 clean; no `logosres:`; no Scripture-connection dumps.
- No DOCX rebuild required this pass.
