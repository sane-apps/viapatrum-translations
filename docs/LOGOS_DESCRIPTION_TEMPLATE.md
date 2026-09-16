# Logos description template — densify tips

Copy this stub for each tip-shipped work before Air Personal Book upload.

```
# Logos Personal Book — description stub

**Work:** <Author>, *<Title>*
**Slug:** `<slug>`
**Resource type:** Monograph · **Language:** English
**Site:** https://fathers.saneapps.com/works/<slug>/
**Body DOCX:** `books/<slug>/<docx>`

## Short description (paste into Logos Personal Books)

<Author>, <Title> — new English for private study from locked <edition/witness>.
Tip densify covering <section range / topic>. Bible quotations and clear allusions
are tagged inline as [[display >> Bible:Book ch:v]]. Translator notes use Headword
TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted
English was copied. Disclose if a PD English already exists.

## Cover-art notes (Air, required)

- Series cover, mandatory: same layout, typography, and palette as every
  other book; author, English title, original-language subtitle.
- Master lives at `books/<slug>/assets/cover.*`; export the size Logos
  asks for at compile time. No cover, no upload.
- No logosres: assets. After Build: TN hover must open TN n, not this blurb.

## Compile checklist (owner on Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K).
3. Body = latest DOCX (`python3 -m pipeline.verify_docx` green).
4. Paste short description; attach the series cover (required); confirm
   DOCX title/author properties match `book.yml`.
5. Build → Finished; spot-check TOC, Bible click, TN hover.
6. Record resource_id in book.yml; update docs/LOGOS_BACKLOG.md.
```
