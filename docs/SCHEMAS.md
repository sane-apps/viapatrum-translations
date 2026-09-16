# Translation JSON schemas

Shapes used by Julian and expected for new books. Fields may be added; do not remove required ones without updating `build_book.py`.

## Numbered continuous work (e.g. To Florus)

`translations/ad_florum_N_english.json` — list of:

```json
{
  "book": 1,
  "section": 1,
  "english": ["Paragraph one.", "Paragraph two."],
  "notes_covered": [],
  "added_allusions": [
    {
      "reference": "Romans 5:12",
      "reason": "Explicit quotation of transmission of sin.",
      "certainty": "clear"
    }
  ],
  "translator_notes": ["Optional editorial note."]
}
```

- `english`: non-empty strings; no `TODO` / `YYYY` / raw `[n12]`.
- `added_allusions[].certainty`: `clear` | `possible`. Clear references belong inline beside the clause; possible allusions stay explicitly uncertain in translator notes as plain-text words, never as clickable Bible links. Mark an allusion `clear` only when the fixed source text quotes or echoes the verse; a thematic resemblance on its own is not an allusion. There is no `none` value: if there is no quotation, echo, or plausible connection, delete the entry instead (a translator note may record why it was considered and rejected). A leftover `none` entry would be rendered as a link by builders, which is exactly the padding this rule exists to prevent. Never emit repeated “Scripture connection” captions.
- Builder skips an allusion caption when the same reference already appears inline (unless certainty is `possible`).

## Origen Jeremiah (homily sections)

`books/origen-jeremiah-samuel/translations/jeremiah_english.json` — list of objects (Pass B only):

```json
{
  "section": "6.1",
  "homily": 6,
  "title": "Name of the thought (not a locus label)",
  "english": ["Paragraph one.", "Paragraph two."],
  "notes_covered": [],
  "added_allusions": [
    {
      "reference": "Jeremiah 1:1",
      "reason": "Why this allusion is clear or possible.",
      "certainty": "clear"
    }
  ],
  "translator_notes": ["OCR gap or lemma note."],
  "klostermann": "GCS Orig. III Hom. 6 §1"
}
```

- Pass A does **not** live here. Put it in `reviews/justifications/jeremiah_H_S.json` as `pass_a_gloss` (copy `jeremiah_1_1.json`).
- Locked Greek: `translations/jeremiah_source.json` (same `section` keys).
- Do not use the Julian `ad_florum_*` shape for this book.
- Optional `supplied_from`: one-line reader cue when this section is supplied from another witness (e.g. “This homily survives only in Jerome’s Latin.”). Omit when the section follows the copy-text.

Work-level `translations/<stem>_meta.json` may include `text_history` for the site’s “About this text”:

```json
{
  "method": "English follows the named copy-text. Other prints were checked.",
  "witnesses": [
    {
      "name": "Klostermann, Origenes Werke III (GCS, 1901)",
      "language": "Greek",
      "role": "copy-text",
      "coverage": "Homilies 1–2",
      "url": "https://archive.org/details/origeneswerke03orig"
    }
  ],
  "joins": [
    {"where": "Homily 1.1", "note": "TEI omits Ἑβραῖον; English follows the GCS page image."}
  ]
}
```

- `witnesses[].role`: `copy-text` | `check` | `version` | `fragments`.
- `joins`: only combinations actually made. Empty list if none.
- `publish_homilies` (optional): integers of homilies that may ship; drafts for later homilies in the same JSON stay off the site.

## Fragment / location-keyed work

```json
{
  "work": "Letter to Rome",
  "location": "1.2.4",
  "kind": "Letter attributed to Julian",
  "english": ["…"],
  "source": "https://…",
  "translator_notes": [],
  "also_preserved_at": ["1.3.7"]
}
```

- `location`: preserving-work citation (e.g. `3.20.41`).
- `kind`: caption above the English (quoted authority, report, etc.).
- `source`: URL or local witness pointer for the Source witness link.

## Scripture review receipt

```json
{
  "book": 6,
  "review": "Independent full Latin/English Scripture and fidelity pass",
  "sections_read": [1, 2],
  "wording_corrections": [{"section": 24, "before": "…", "after": "…"}],
  "added_scripture_references": [],
  "remaining_textual_uncertainty": []
}
```

## Source audit receipt (include/exclude)

List of:

```json
{
  "location": "6.1.1",
  "decision": "included",
  "reason": "Final phrase Augustine quotes from Julian."
}
```

## Build receipt (`build_receipt.json`)

Produced by `build_book.py`:

```json
{
  "section_count": 1164,
  "bookmark_count": 1222,
  "scripture_index_entries": 580,
  "records": [{"key": "F1_1", "label": "To Florus 1.1", "source": "…", "paragraphs": 2}],
  "bible_links": [{"display": "Romans 5:12", "target": "Romans 5:12", "datatype": "Bible", "section": "F1_1", "editorial": false}]
}
```

## Explore stance layer (fathers.saneapps.com)

Editorial tags for the public **Explore** timeline (`/explore/`). Stored under
`websites/fathers.saneapps.com/data/explore/` and merged at site build into
`dist/data/explore-index.json`. These are **readings of the English/source**, not
infallible dogma scores. Do not invent numeric “orthodoxy” rankings.

### Claims (`claims.json`)

Closed set of claims per topic id (must match `topics.yml`):

```json
{
  "topic": "free-will",
  "title": "Free Will",
  "claims": [
    {"id": "will-capable", "label": "Will remains capable of choice"},
    {"id": "will-impaired", "label": "Will impaired so it cannot choose the good unaided"}
  ]
}
```

### Stances (`stances.json`)

One row per library point (excerpt or work section):

```json
{
  "ref": "excerpt:justin_1apol_43",
  "topic": "free-will",
  "claim_id": "will-capable",
  "stance": "affirms",
  "year": 155,
  "note": "Optional short editorial gloss."
}
```

- `ref`: `excerpt:{id}` or `work:{slug}/{section}`
- `stance`: `affirms` | `denies` | `qualified` | `unclear`
- `year`: approximate CE for the timeline (from `period` or contrast card)

### Contrast authors (`contrast.json`)

Thin cards for writers not yet fully in the topical corpus (e.g. Augustine):

```json
{
  "author": "Augustine of Hippo",
  "author_slug": "augustine",
  "period": "c. 400–430",
  "year": 412,
  "era_band": "Post-Nicene",
  "kind": "contrast",
  "points": [
    {
      "id": "augustine-free-will-contrast",
      "topic": "free-will",
      "claim_id": "will-impaired",
      "stance": "affirms",
      "summary": "After the fall, the will cannot turn to God without prior grace.",
      "citation": "Contrast summary — full Augustine works forthcoming"
    }
  ]
}
```

### Ruptures (`ruptures.json`)

Optional short captions for topics where Explore should teach a break:

```json
{
  "topic": "free-will",
  "title": "A later break",
  "body": "Earlier writers in this library generally treat the will as capable of choosing. Augustine’s late teaching on grace and the will sits notably apart from that earlier pattern."
}
```

## Current source review artifacts

`pipeline.verify_translation_qa` owns the `translation-audit-v1` packet and receipt schema.
Packets bind author/work identity, declared section scope, actual English/source files and raw witnesses.
Use the shared generator and validator rather than hand-writing packet hashes.
Each reviewed section needs explicit source identity, completeness, negation, agency, modality,
doctrine and Scripture checks, full source-paragraph coverage, no unresolved uncertainty and evidence notes.
A sample receipt approves only its selected passages.

The website stores references to current corpus packets/receipts in its publication review index.
That index cannot change a packet's author/work identity, expand its scope or substitute different text.
The provisional legacy baseline is an audit freeze, never a semantic approval.
