# Style guide — Ante-Nicene topical library

## Goals

Modern literary English (CSB/ESV narrative level) that remains **accurate** to the Father’s sense and **recognizably his voice**.

## Chronology (book order)

Inside each topic, authors are grouped earliest → latest using `authors.json` (`dates_display` + `sort_year`). Anonymous works use floruit of the text. Dates are approximate scholarly consensus (`c.` / `fl.` / `d.`), not exact civil records. Excerpts under one author stay together, sorted by work period then locus.

## Shared clarity rules

- Short sentences where the Greek/Latin piles clauses.
- No *hath*, *wherefore*, *thereof*, *ye*.
- Keep technical terms in captions when needed: *Logos*, *ousia*, *substantia*, *regula fidei*, *autexousion* (self-determining power).
- Scripture: modern names/numbers; tag as `[[ref >> Bible:ref]]` in the DOCX build.

## Two lanes (never one pass)

1. Sense / fidelity draft  
2. Literary polish  
3. Re-diff vs sense — polish loses if meaning moved  

## Voice cards

| Author | Voice |
|--------|--------|
| Ignatius | Urgent, affectionate, almost liturgical intensity |
| Justin | Philosophical, patient, forensic against fate |
| Irenaeus | Pastoral-polemical, Scripture-woven, measured weight |
| Tertullian | Sharp, sarcastic, forensic — never pious-wash the bite |
| Clement of Alexandria | Cultured, teacherly |
| Origen | Exploratory, layered; preserve hedges |
| Hermas | Plain catechetical vision-speech |
| Methodius | Dialogical, anti-fatalist clarity |
| Lactantius | Rhetorical Latin cadence, public apologetic |
| Melito | Homiletic parallelism / poetic typology |
| Commodian | Rough, direct verse instruction |
| Tatian / Athenagoras / Theophilus | Compact apologetic philosophy |
| Minucius / Arnobius | Roman forensic satire against pagan fate |

Fail any excerpt that reads like generic “church father English.”

## Internal metadata (never in the customer DOCX / Logos book)

Keep these in `translations/topics/*.json`, `reviews/justifications/`, and QA only:

- `confidence` — `source_verified` | `anf_mediated` | `uncertain`
- `authenticity`, `edition_id`, `justification`
- `notes`, `translator_notes` — process / rematch / OCR honesty for agents

Customer-facing only: citation, English body, `note_anchors` (wording choices), attribution line, clear Scripture allusions, and the work’s `text_history` (copy-text, checked prints, supplied stretches) in collapsed About this text. Do not print Confidence captions, Pass A, or GTG / QA jargon in About.
