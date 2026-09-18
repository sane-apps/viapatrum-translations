# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus, *On the Soul, to Tatian* (tip)
**Slug:** `gregory-thaumaturgus-ad-tatianum-de-anima`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-ad-tatianum-de-anima/gregory-thaumaturgus-ad-tatianum-de-anima.docx`

## Short description (paste into Logos Personal Books)

Gregory Thaumaturgus, Disputation on the Soul addressed to Tatian — a new English rendering for private study from the locked Vossius 1684 Latin, covering the preface and inquiry program. By the terms of the disputation itself no Scripture testimonies are argued here, so this tip carries no inline Bible quotations from Gregory. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: On the Soul, to Tatian".
- Edition: `build_book.py` FRONT_MATTER → "from locked Vossius 1684 Latin"; lock `sources/_anima_latin_lock.txt`; "Prior English (ANF 6 Salmond, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Disputatio de Anima ad Tatianum. Tip densify preface + inquiry program"; receipt 1 record from anima_tatianum_english.json ("Preface to Tatian: argue the soul without Scripture proofs").
- Limit/character: FRONT_MATTER "the commission itself forbids Scripture testimonies in this disputation, so the tip English has no inline Bible quotes from Gregory."
