# Logos Personal Book — description stub

**Work:** Robert Baron, *Philosophia theologiae ancillans* (Exercitatio Prima, tip)
**Slug:** `baron-philosophia-theologiae-ancillans`
**Resource type:** Monograph · **Language:** English
**Site:** (no live tip page confirmed in docs/LOGOS_BACKLOG.md — confirm before upload)
**Body DOCX:** `books/baron-philosophia-theologiae-ancillans/baron-philosophia-theologiae-ancillans.docx`

## Short description (paste into Logos Personal Books)

Robert Baron, Philosophia theologiae ancillans — a new English rendering for private study from the locked 1658 Oxford Latin (first edition St Andrews 1621). This tip covers Exercitatio Prima Art. I–III on being and essence (necessary being; being by essence; pure act) in 3 sections; the remainder of the work is not in this volume. Bible quotations and clear allusions are tagged inline for Logos KeyLinking. Translator notes use Headword TN marks (not Word footnotes). AI-assisted private study; no modern copyrighted English was copied.

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

- Author/title: `book.yml` → author "Robert Baron", title "Philosophia theologiae ancillans (Exercitatio Prima Art. I-III tip)".
- Edition/date: `build_book.py` FRONT_MATTER → "from the 1658 Oxford Latin", "Oxford: T. Robinson & R. Davis, 1658", "Wing B887", "First edition St Andrews 1621"; lock `sources/_baron_ente_art1_2_latin_lock.txt`.
- Contents: FRONT_MATTER "Scope: tip — Exercitatio Prima Art. I–III De Ente & Essentia (necessary being; being by essence; actus purus)"; receipt title "Robert Baron: Philosophia theologiae ancillans (New English tip)", 3 records from ente_art1_2_english.json ("Only God is necessary being", "being by essence", "pure act").
- Limit: FRONT_MATTER "Remainder of Philosophia theologiae ancillans remains."
