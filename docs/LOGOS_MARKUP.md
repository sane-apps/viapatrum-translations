# Logos Personal Book markup

Canonical tags for DOCX/Word body text compiled by Logos Personal Books. Prefer the Julian-proven forms below.

## Bible datatype links

Display text and target can differ:

```
[[Romans 5:12 >> Bible:Romans 5:12]]
[[John 8:44 >> Bible:John 8:44]]
[[Psalm 32:1-2 >> Bible:Psalm 32:1-2]]
```

Rules used in production:

- Use the `Bible` datatype with modern chapter/verse for KeyLinking.
- Prefer full book names in the target (`Romans`, not only `Ro`) for readability; Logos accepts standard abbreviations too.
- When retaining LXX/Vulgate numbering in the display, still link the modern equivalent the reader should open (Julian builder maps old-number labels to the preceding modern Psalm ref).
- Ranges keep an en-dash or hyphen consistently in the target after normalization to `-`.
- **Inline first.** Clear Bible quotations and allusions belong in the reading paragraphs as `[[… >> Bible:…]]` (often a short parenthetical after the clause). Do **not** dump every `added_allusion` as a separate “Scripture connection:” caption under the section — Logos readers see a useless chunk at the bottom, and most English prose never had verse numbers to auto-link.
- Short captions are allowed only for **possible / uncertain** allusions (e.g. lacuna guesses), labeled `Possible allusion:`.
- A Bible link tells the reader that the author is quoting or echoing that passage. A verse the passage merely resembles in theme is not an allusion to that verse.
- If the fixed source text (the Greek or Latin recorded in `translations/*_source.json` and `sources/manifest.json`) contains no quotation or echo of the verse, the most you may do is mention the resemblance in a translator note. You must never turn it into a `[[... >> Bible:...]]` link, not even inside a `Possible allusion:` caption. Writing `certainty: possible` and admitting there is no textual basis does not make it acceptable; that combination is padding.
- Caption lines are always plain text and do not count toward the requirement that a book contain at least one Bible link. When a passage genuinely cites no Scripture, the book honestly has zero Bible links: the website tip may still ship, but the Logos book build stays on hold. That is the tip exemption.

Auto-tagging (“Tag References as Hyperlinks” in Advanced) is optional; this pipeline emits explicit tags so receipts are auditable.

## Headword milestones

```
Heading paragraph: To Florus 1.1
Next paragraph:    [[@Headword:To Florus 1.1]]
```

**Critical:** Headword must be its **own paragraph**, not appended to the heading text. Gluing produces ArticleCache titles like `To Florus 1.1 [[@Headword:To Florus 1.1]]` and pollutes TOC/lookup.

## Translator notes (required path)

Logos Personal Books **do not compile Word footnotes**. `w:footnoteReference` + `footnotes.xml` can Build with 0 errors while every hover falls back to the book description.

Use **Headword TN marks** (Ante-Nicene / Origen 2026-09-10 proven):

```
In body:   [[⁴ >> Headword:TN 4]]
Later:     Heading 3  TN 4
           [[@Headword:TN 4]]
           Note text…
```

- Unicode superscripts `⁰¹²³⁴⁵⁶⁷⁸⁹` in the display mark.
- One Headword article per note (`TN 1`, `TN 2`, …).
- Do **not** ship Word-native footnotes in PBB DOCX. `pipeline.verify_docx` fails the build if `word/footnotes.xml` is present.

`pipeline/footnotes.py` is legacy research only — do not call `FootnoteStore` from book builders.

## Document structure

- Heading 1–3 styles drive the Logos Contents pane TOC.
- First Heading 1 can become the document title in some Liberonix-era docs; Julian uses Title/Subtitle styles for the cover and Heading 1 for major parts.
- Internal Word bookmarks + hyperlinks support TOC jumps and Scripture-index back-links inside the DOCX; Logos Headwords handle resource lookup after compile.

## Covers, descriptions, and document identity (all mandatory per book)

A book is not done until it has all three: cover art, a description, and
correct document identity. Missing any one of them holds the Logos upload.

- Covers follow one series design: same layout, typography, and palette on
  every book. Each cover shows the author name, the English title, and the
  original-language subtitle. Keep a high-resolution master at
  `books/<slug>/assets/cover.*`; export whatever size Logos asks for at
  compile time.
- Descriptions follow `docs/LOGOS_DESCRIPTION_TEMPLATE.md`: plain sentences
  saying what the work is, its scope, the locked source it was rendered
  from, and that the English is new. No hype, no jargon, no claims the
  review does not support.
- Document identity (DOCX properties, title page, receipt title) comes from
  `book.yml` through `pipeline.book_meta`. Never hardcode another book's
  strings into a builder; five books once shipped titled as another
  author's work, which is why this rule exists.
- The Air compile checklist in the template verifies all three before
  upload: DOCX properties match `book.yml`, description pasted, series
  cover attached.

## External links

Ordinary Word hyperlinks are fine for “Source witness” URLs to retained Latin pages. Prefer stable archive URLs when possible.
**Never** emit `logosres:` / cross-resource links in shared books — they hardcode one library and prompt other users to buy.

## Compile checklist (Air)

1. Close open panels of this personal book.
2. Tools → Utilities → Personal Books (never Cmd+K on this install).
3. Body file = latest DOCX.
4. `python3 -m pipeline.verify_docx books/<slug>/*.docx` must be green (runs `check_pbb_guards` too).
5. Cursor Write/Edit on `books/*/build_book.py` is blocked if it introduces `FootnoteStore` or `"Scripture connection"`.
5. Build → Finished; re-read UI for errors/warnings.
6. Open book → clean breadcrumb titles → Bible link click with Bible pane → re-read destination.
7. Hover a TN mark → must open `TN n`, not the book blurb.
