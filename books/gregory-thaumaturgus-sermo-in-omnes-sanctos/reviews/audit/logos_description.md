# Logos Personal Book — description stub

**Work:** Gregory Thaumaturgus (?), *Sermo in omnes sanctos* (opening, tip)
**Slug:** `gregory-thaumaturgus-sermo-in-omnes-sanctos`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/gregory-thaumaturgus-sermo-in-omnes-sanctos/gregory-thaumaturgus-sermo-in-omnes-sanctos.docx`

## Short description (paste into Logos Personal Books)

The Sermon on All the Saints transmitted under the name of Gregory Thaumaturgus — a new English rendering for private study from the locked MGR Greek, covering the opening (silence preferred, yet the feast of the martyrs compels speech, through Christ despoiling Hades); the remainder is not in this volume. Attribution to Gregory is disputed in modern scholarship. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Gregory Thaumaturgus", title "Gregory Thaumaturgus: Sermo in omnes sanctos".
- Edition/attribution: `build_book.py` FRONT_MATTER → "Greek copy-text is the MGR extract (TLG 2063.010)."; "attribution to Gregory Thaumaturgus is disputed in modern scholarship and is disclosed."; lock `sources/_omnes_sanctos_greek_lock.txt`; "Prior English (ANF 6 Salmond, PD) consulted only as sense/style check."
- Contents: FRONT_MATTER "Scope: Sermo in omnes sanctos. Tip covers opening through Christ despoiling Hades / sting of death"; receipt 1 record from omnes_sanctos_english.json ("Opening: silence preferred, yet the feast of the martyrs compels speech").
- Limit: FRONT_MATTER "remainder remains."
