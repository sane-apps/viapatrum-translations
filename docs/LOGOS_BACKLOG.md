# Logos Personal Book backlog

Updated: 2026-09-15 16:57 UTC (Mini audit). Owner compiles on **Air** only (SOP §5). Agents do not ship site from this file.

Queue: tip-shipped / live works with a DOCX body that still need Air Personal Book steps (cover art, description, upload/compile).

Related:
- Markup rules: `docs/LOGOS_MARKUP.md`
- Process: `docs/SOP.md` §4–6
- Description template: `docs/LOGOS_DESCRIPTION_TEMPLATE.md`

## Awaiting Air Logos (pending)

| slug | title | docx path | site URL | Logos status | notes |
| --- | --- | --- | --- | --- | --- |
| `nemesius-de-natura-hominis` | Nemesius: De natura hominis | `books/nemesius-de-natura-hominis/nemesius-de-natura-hominis.docx` | https://fathers.saneapps.com/works/nemesius-de-natura-hominis/ | **pending** | Tip densify 1.1–3.1 live (HTTP 200). verify_docx OK 2026-09-15; inline Bible×2; TN 1–24 Headword; no footnotes.xml/logosres. Description stub: books/.../reviews/audit/logos_description.md. Cover art + Air upload/compile still needed. Site already live — no re-ship required for Logos markup (DOCX unchanged this audit). |
| `origen-heraclides-pascha` | Origen — Dialogue with Heraclides and On Pascha | `books/origen-heraclides-pascha/origen-heraclides-pascha.docx` | https://fathers.saneapps.com/works/origen-dialogue-heraclides/ (+ /works/origen-on-pascha/) | **pending** | Live tip pages present; DOCX exists; resource_id empty. Needs Logos description stub + cover + Air compile. Re-run verify_docx before Build. |
| `origen-jeremiah-samuel` | Origen: Homilies on Jeremiah and on 1 Samuel 28 | `books/origen-jeremiah-samuel/origen-jeremiah-samuel.docx` | https://fathers.saneapps.com/works/origen-homilies-jeremiah/ (+ /works/origen-homily-1samuel-28/) | **pending** | Live tip pages present; DOCX exists; resource_id empty. Needs description stub + cover + Air compile. |
| `cyril-alexandria-adoration-1` | Cyril of Alexandria: On Adoration (tip pack / live adoration pages) | `books/cyril-alexandria-adoration-1/cyril-alexandria-adoration-1.docx` | https://fathers.saneapps.com/works/cyril-adoration-1/ (… through cyril-adoration-17 on site) | **pending** | Live adoration tip pages on site; local DOCX is adoration-1 pack — confirm body coverage vs live slugs before PBB. Description + cover + Air compile pending. |

## Already compiled (reference)

| slug | docx | resource_id | notes |
| --- | --- | --- | --- |
| `julian-of-eclanum` | `books/julian-of-eclanum/Julian of Eclanum English.docx` | `PBB:49ea9d72e8d7414782017dd81625e605` | verified — SOP reference compile |
| `origen-prayer-martyrdom` | `books/origen-prayer-martyrdom/origen-prayer-martyrdom.docx` | `PBB:4f41cb276f014e1aa7ee22103e299a76` | done — already compiled |

## Excluded this pass

- **Macarius** (`macarius-spiritual-homilies`): another agent owns those files — do not edit; not listed as actionable here even if a DOCX exists.
- **OpenCode:** leave alone.
- Draft/series-closeout books with DOCX but **not** tip-live on fathers.saneapps.com are out of this tip backlog (add later if tip-shipped).

## Nemesius audit snapshot (2026-09-15)

- Read SOP §Logos + `LOGOS_MARKUP.md` fully.
- Live tip DOCX + english JSON audited: **pass** (no rebuild).
- English has parenthetical `(Genesis 2:2)` / `(John 5:17)`; builder emits `[[… >> Bible:…]]` in DOCX.
- Headword TN (not Word footnotes); headings OK; no `logosres:`.
- **Site re-ship:** not required for Logos markup (no DOCX change). Site already serves the work URL above.
- Description stub ready under `books/nemesius-de-natura-hominis/reviews/audit/logos_description.md`.

