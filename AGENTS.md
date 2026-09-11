# Translations — AGENTS

Private study corpora for **Logos Personal Books** (PBB). Not a SaneApps product.
English reading text only in the compiled book; Latin/source files stay in `sources/`.

## Canonical host

- **Corpus + pipeline:** `~/SaneApps/clients/translations` on Air and Mini (same relative path).
- **Logos GUI / compile / click-test:** **MacBook Air only** (owner’s Logos library). Explicit Mini-first exception.
- Screen Recording for remote agents on Air: run Peekaboo/`screencapture` via **Terminal.app `do script`** (direct SSH fails `CGPreflightScreenCaptureAccess`).

## Start here

**Contributors / other LLMs:** paste `docs/START_HERE.md` into the model. The model runs:

```bash
python3 scripts/claims.py start --agent YourName
```

Owner / deep work:

1. Read `docs/SOP.md` (full process — distilled from Julian of Eclanum / Codex).
2. Read `docs/LOGOS_MARKUP.md` before touching DOCX markup.
3. Read `docs/SCHEMAS.md` before writing translation JSON.
4. For an existing book, read `books/<slug>/SESSION_HANDOFF.md`.
5. Multi-agent coordination: `docs/CLAIMS.md` + `docs/START_HERE.md` (do not invent a second queue).
6. AI promote → `done` (no standing human review gate): `docs/AI_CROSSCHECK.md`. Overnight burn is **Mini only**, calendar 21:10 local, flock locks — do not start a second burn while global/claim locks are held (promote exit `3`).

## Layout

```
pipeline/          shared DOCX + Bible-link + verify tools
docs/              SOP, markup, schemas
templates/book/    scaffold for a new book
books/<slug>/      one corpus per book (sources, translations, build)
```

## Hard rules (from Julian production + Origen 2026-09-10)

- Do not copy modern copyrighted English translations. New English from Latin (or other allowed public-domain source text).
- Do not present a partial corpus as “complete works.” Disclose scope, losses, and AI-assisted private-study status in the front matter.
- English only in the Logos body. No Latin beside the reading text.
- Bible quotations and clear allusions must become Logos datatype links **inline**: `[[display >> Bible:Book ch:v]]`. Do not dump allusions as “Scripture connection:” captions under each section.
- Translator notes use **Headword TN marks** (`[[ⁿ >> Headword:TN n]]` + notes section). **Never Word footnotes** — Logos PBB does not compile them; hover falls back to the book blurb. `verify_docx` fails if `word/footnotes.xml` is present.
- `[[@Headword:…]]` must be its **own paragraph** after a clean heading — never glued into the heading text (pollutes ArticleCache TOC titles).
- **Fathers site reader (permanent):** when a book ships to `fathers.saneapps.com`, presentation follows `~/SaneApps/websites/fathers.saneapps.com/AGENTS.md` → *Works reader SOP*. Section `title` / `head` must name the **thought**, not the locus (`1.5.16`, `Against Julian 1.5.16`). Consecutive sections that share one thought title are one passage on the site; Contents lists each thought once. Do not invent a one-click-per-section browsing UX.
- **Two-pass translation (permanent):** `books/ante-nicene-topics/docs/TRANSLATION_QA.md`. Pass A is a literal gloss plus key lemmas from the locked source. Pass B is the reading English and may not add a concept absent from A. Do not copy B into A. A `source_verified` receipt with A==B is not a pass.
- **Many original-language witnesses (permanent):** for every work, lock as many PD Greek/Latin (and ancient versions) as exist — critical edition + second scan/TEI + earlier print (PG/PL) + catena/version. Diff them. Do not translate from a single OCR. Copyrighted editions are history notes, not copy-text. See `docs/SOP.md` §1. Reader-facing: name copy-text, checks, and supplied stretches in `text_history` (site “About this text”). Do not silently merge recensions or call the reading text a manuscript.
- Before Logos **Build**: close other open panels of that personal book. Rebuild fails with “Could not remove existing book / close all other open panels.”
- Open Personal Books via **Tools → Utilities → Personal Books** (or Tools toolbar search). Do **not** use Cmd+K (opens Study Assistant on this install).
- Never claim Bible-link success from click-return alone. Re-read live UI (screenshot/AX) or get owner confirmation; name what the surface shows.
- After Logos Build, hover a TN mark: it must open `TN n`, not the resource description.
- Do not purchase sources or publish publicly unless the owner asks.
- Public site for these corpora: `~/SaneApps/websites/fathers.saneapps.com` (Topics + Works). Extend books here, then rebuild/deploy the site.

## Commands

```bash
# From repo root
python3 -m pipeline.new_book --slug my-author --title "Title"
python3 books/<slug>/build_book.py
python3 -m pipeline.verify_docx books/<slug>/*.docx   # includes check_pbb_guards
python3 -m pipeline.check_pbb_guards                  # optional standalone
# On Air, after Logos Build:
python3 -m pipeline.verify_logos_db --title-substr "Julian"
# Public library (after English is ready):
cd ~/SaneApps/websites/fathers.saneapps.com && python3 scripts/build_site.py
```

## Done means

DOCX receipt green + Logos Build 0 errors/0 warnings + clean ArticleCache titles + TN hover opens `TN n` (not the book blurb) + owner- or screenshot-confirmed Bible-link navigation. When the corpus is public-ready, fathers.saneapps.com lists the work with topic cross-refs.
