# Logos Personal Book — SOP

Distilled from the Julian of Eclanum production run (Codex → Cursor, 2026-09-09). Follow this for every new book. Do not invent a parallel process.

## Phases

### 0. Charter

Write in `books/<slug>/SESSION_HANDOFF.md`:

- Title, author, resource type (usually Monograph), language (English).
- Scope: what survives, what is out of scope, what is lost.
- Legal: private study; new English from allowed source text; no modern copyrighted English copy; no public publish unless owner asks.
- Source URLs / editions and local paths.

### 1. Sources (many witnesses)

Lock the exact permitted copy-text and compare every additional witness actually used. Identify the work, author, printed page/locus and surviving scope against the raw print or document before translating. A second scan of the same edition checks OCR; it is not an independent textual witness. Record which comparisons were done and disagreements in `variants[]`. Do not invent missing witnesses or call generated source JSON a source lock.

**Reader disclosure:** the public work page’s collapsed “About this text” names the copy-text, the other prints checked, and every stretch supplied from another witness (`text_history` in `*_meta.json` or the site pack). The reading column stays clean. A one-line italic cue is used only when a whole stretch is supplied from another witness (for example a homily that survives only in Jerome’s Latin). Do not call the result a manuscript. Do not claim a combination that was not actually done. Agent receipts (`variants[]`, Pass A) stay off the page.

For each work, try in this order (skip what does not exist or is still in copyright):

1. Best PD critical edition (GCS, Pusey, Scherer/Witte, Klostermann).
2. A second scan or transcription of that same edition (PDF + OCR/TEI).
3. An earlier PD print (Migne PG/PL, Delarue, Huet, Ghislerius).
4. Ancient versions of the *same* work (Jerome/Rufinus Latin of Origen, Syriac, etc.).
5. Catena / fragment collections that preserve extra lines.
6. A second library scan when the first OCR is damaged.

Do **not** lock copyrighted critical editions or modern facing-page English as copy-text (SC, FOTC, Reuss 1957, etc.). Those may be edition-history notes only.

- Fetch and retain raw HTML/PDF/XML under `sources/`.
- `sources/manifest.json` lists every witness: edition, language, role (`copy-text` | `check` | `version` | `fragments`), URL, SHA256, local path.
- Speaker-split carefully (Julian vs Augustine vs quoted authorities). Prefer full-name speaker labels at paragraph start only when the site uses them that way.
- Keep raw HTML even when a parser cleans JSON — audits need the witness.
- Output structured Latin/source JSON that translation records can cite by location. Name which witness each section was read from. Declare expected section IDs from the edition and preserve every source paragraph. A matching chapter number does not authorize a short tip slice to replace the whole chapter.

### 2. Translate (two passes)

Full bar: `books/ante-nicene-topics/docs/TRANSLATION_QA.md`.

- **Pass A:** literal sense gloss + key lemmas from the locked source block only.
- **Pass B:** reading English in the author’s voice; no concept that is not in A.
- One JSON file (or one per book/witness) under `translations/` matching `docs/SCHEMAS.md`.
- English paragraphs only in `english[]` (this is Pass B). No Latin in the reading text.
- Justification receipt required: `reviews/justifications/<id>.json` with `pass_a_gloss` ≠ joined Pass B.
- Use `kind` / `translator_notes` / `added_allusions` for editorial material.
- **Inline scripture refs (hard gate):** whenever the Father quotes or clearly alludes to Scripture, Pass B `english[]` must carry a parenthetical citation beside the clause (full book name + chapter:verse, Julian pattern). `added_allusions` / justification `bible_refs` alone do **not** pass — readers and Logos PBB both need the ref in the reading text. See `docs/LOGOS_MARKUP.md` and Project store `docs/scripture-refs-inline.md`.
- Forbid placeholders: no `TODO`, `YYYY`, or raw `[n12]` footnote junk in English.

### 3. Review

- Check all records structurally: nonempty source/English, no scaffold or operational prose, distinct Pass A/Pass B, exact declared section coverage and current file hashes. These checks cannot certify meaning.
- Compare first/last plus seeded and risk-selected passages against actual raw source pages. Record the sampled scope. Prioritize negation, agency, modality, doctrinal terms, quotations, lacunae and suspiciously short output.
- Every new or changed published passage needs a source-backed semantic review of **every clause** in that passage. Approving five sampled passages does not approve the rest of a work.
- Review author/work/locus identity, completeness, negation, agency, modality, doctrine and Scripture explicitly. Each source paragraph needs a coverage entry and concrete evidence notes. Uncertainty or missing evidence blocks approval; never prefer pass when unsure.
- Scripture wording controls the target, not a shifted footnote list. Verify each explicit quotation and clear allusion. Distinguish Hebrew/modern and LXX/Vulgate Psalm numbering; label possible allusions as uncertain. Record corrections in the existing scripture review.
- Source audit for fragments must distinguish the author's words, the opponent's reply and indirect reports. Preserve lacunae and lost material; no invented connective argument.
- Bind review to exact author/work identity, source/English files, raw witnesses and scope. Any source, English, attribution or scope edit invalidates affected review. Do not copy old reviewer stamps forward.
- Use `pipeline.verify_translation_qa` to create and validate packets; `pipeline.check_pass_ab` checks justifications. `ai_promote.py` handles supported independent-model promotion. No standing human approval queue is required; the reviewing agent/model still must inspect the actual source.
- The website consumer independently checks evidence. A claim marked `done`, two model names, a nonempty file or `source_verified` alone is insufficient. The site's provisional legacy hash baseline is not certification and must never be refreshed to bypass review.
- Preserve held files. Repair one source/translation family at a time and review changes before release. Never expand the catalogue to meet a volume target.

Example packet generation (run on Mini; use actual paths):

```bash
python3 -m pipeline.verify_translation_qa --english <english.json> --source <source.json> \
  --raw-source <edition.pdf> --identity <identity.json> --expected-sections <section-ids.json> \
  --seed 20260913 --sample-size 5 --packet-out <packet.json>
```

Generation reports structural status only. A current passing receipt is a separate artifact from the review itself; consume it with `--receipt <receipt.json>` or the shared validation API.

### 4. Build DOCX

```bash
cd ~/SaneApps/clients/translations
python3 books/<slug>/build_book.py
python3 -m pipeline.verify_docx books/<slug>/*.docx
# verify_docx also runs pipeline.check_pbb_guards (bans FootnoteStore / Scripture-connection captions in build_book.py)
```

Required in the DOCX:

- Heading styles for TOC (Heading 1–3).
- Clean heading text + **separate** paragraph `[[@Headword:Label]]`.
- Bible links `[[display >> Bible:Book ch:v]]` **inline in the reading text** (see `docs/LOGOS_MARKUP.md`). Clear allusions go beside the clause; do not emit a “Scripture connection:” caption dump.
- Translator notes as **Headword TN marks** (`[[ⁿ >> Headword:TN n]]` + a Translator notes section). **Never Word footnotes** — Logos PBB ignores them and every hover becomes the book description. Do not import `pipeline.footnotes` / `FootnoteStore` in any `build_book.py`.
- Internal bookmarks for section navigation and Scripture index back-links.
- Front matter that discloses scope and AI-assisted private-study status.
- `build_receipt.json` with section counts and bible link receipts.
- `python3 -m pipeline.verify_docx` green (fails on `footnotes.xml`, Scripture-connection dumps, and PBB build-script guards).

### 5. Logos compile (Air only)

1. Close other open panels of this personal book (required or Build fails).
2. Open **Tools → Utilities → Personal Books** (not Cmd+K).
3. Create/edit the draft: title, author, type Monograph, English.
4. Add / replace the body file with the new DOCX.
5. **Build**. Wait for Finished. Re-read UI: “0 errors, 0 warnings” or name the blocker.
6. Open the book. Spot-check TOC titles (no raw `[[@Headword:`).
7. Click a Bible link with a Bible open; re-read the Bible panel location. Screenshot via Terminal-hosted capture if remote.

```bash
python3 -m pipeline.verify_logos_db --title-substr "<Title fragment>"
```

### 6. Handoff

Update `books/<slug>/SESSION_HANDOFF.md` and repo `SESSION_HANDOFF.md` with LastCompiled, receipt counts, verification evidence, next moves.

## Air GUI capture path

Direct SSH Peekaboo often lacks Screen Recording. Working route:

```bash
osascript -e 'tell application "Terminal" to do script "…peekaboo or screencapture…"'
```

Same idea as SaneMaster `--terminal-host`. After every GUI mutation, poll screenshot/AX and name what the surface shows.

## Anti-patterns

- Gluing Headword onto the heading run.
- Claiming success from click-return alone.
- Using Cmd+K for Personal Books.
- Rebuilding while the book panel is open.
- Starting a second project folder under Documents.
- Shipping Word footnotes (`FootnoteStore` / `footnotes.xml`) in a Personal Book.
- Dumping `added_allusions` as repeated “Scripture connection:” captions instead of inline Bible links.
- Emitting `logosres:` links that prompt other users’ libraries.
