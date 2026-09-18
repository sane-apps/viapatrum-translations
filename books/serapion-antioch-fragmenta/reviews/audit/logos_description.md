# Logos Personal Book — description stub

**Work:** Serapion of Antioch, *Fragmenta* (Gospel of Peter, tip)
**Slug:** `serapion-antioch-fragmenta`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/serapion-antioch-fragmenta/serapion-antioch-fragmenta.docx`

## Short description (paste into Logos Personal Books)

Serapion of Antioch, Fragments — a new English rendering for private study from the locked Greek of Routh's Reliquiae Sacrae, cross-checked against Eusebius. This tip covers the fragment On the So-Called Gospel of Peter, addressed to the church at Rhossus; the other surviving Serapion scraps are not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Serapion of Antioch", title "Serapion of Antioch: Fragmenta".
- Edition: `build_book.py` FRONT_MATTER → "Greek copy-text is Reliquiae Sacrae (Routh 1846) Serapion extract, cross-checked against Eusebius HE 6.12 (Perseus/Lake TEI)."; lock `sources/_serapion_fragmenta_greek_lock.txt`; "Prior English (ANF, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Serapion Fragmenta. Tip covers On the so-called Gospel of Peter"; receipt 1 record from serapion_fragmenta_english.json ("Section 1 — On the so-called Gospel of Peter (to the church at Rhossus)").
- Limit: FRONT_MATTER "other Serapion scraps remain."
