# Logos Personal Book — description stub

**Work:** Samuel Strimesius, *Ingenua in Controversias Evangelicorum* (Prefatio, tip)
**Slug:** `strimesius-in-controversias-evangelicorum`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/strimesius-in-controversias-evangelicorum/strimesius-in-controversias-evangelicorum.docx`

## Short description (paste into Logos Personal Books)

Samuel Strimesius, A Candid Inquiry into the Controversies among Evangelicals — a new English rendering for private study from the locked 1708 Frankfurt-an-der-Oder Latin. This tip covers the Pacific-Apologetic Preface section I (the call for Protestant church peace, weighed by Scripture alone, undertaken at Frankfurt in 1679) in 2 sections; the remainder is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Samuel Strimesius", title "Ingenua in Controversias Evangelicorum (Prefatio tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1708 Frankfurt an der Oder Latin", "Francofurti ad Viadrum: Jer. Schrey & J. C. Hartmann, 1708", "Frankfurt (Oder) / Viadrina Reformed faculty"; lock `sources/_strimesius_prefatio_si_latin_lock.txt`; "No Colloquia Scholastica AI English used."
- Contents: FRONT_MATTER "Scope: tip only — Prefatio Pacifico-Apologetica section I (ad Lectorem Benevolum)"; receipt 2 records from prefatio_si_tip_english.json ("Nazianzen's cry for peace …", "Called at Frankfurt an der Oder in 1679 to weigh controversies only by Scripture …").
- Limit: FRONT_MATTER "Remainder of Ingenua in Controversias Evangelicorum remains."
