# Translation QA — anti-hallucination + justification stack

**Professional default:** every shipped excerpt aims at `source_verified` with a justification receipt. `anf_mediated` is a temporary bootstrap label only.

See also: `PROFESSIONAL_BAR.md`, `STYLE.md`, `GLOSSARY.md`.

## Pipeline

```text
edition-locked source
  → Pass A (literal + lemmas)
  → automated checks (ANF diverge, lexicon keys, optional consensus)
  → Pass B (literary, lemma-constrained, voice card)
  → re-diff + optional back-translation
  → justification JSON
  → human clear on flags/variants
  → source_verified
```

## Source lock

- Translate **only** the provided source block for the named edition.
- Unreadable → `[lacuna]`; never invent.
- Record: language (`grc`|`lat`|…), edition id, file path, CTS/URN if any.
- Irenaeus AH: prefer Latin witness; attach Greek fragments as notes when present.

## Pass A / Pass B

- **A:** sense gloss + key lemmas (every theologically loaded noun/verb at minimum).
- **B:** modern literary English; **may not** add concepts absent from A’s lemma/sense list.
- Voice card from `STYLE.md`.

## Justifications (required for source_verified)

File: `reviews/justifications/<excerpt_id>.json`

```json
{
  "excerpt_id": "justin_1apol_43",
  "edition": {"id": "first1k-justin-1apol", "language": "grc", "path": "sources/greek/justin_1apology.xml", "locus": "43"},
  "source_text": "…",
  "pass_a_gloss": "…",
  "lemmas": [{"form": "προαιρέσει", "lemma": "προαίρεσις", "gloss": "deliberate choice", "lexica": "LSJ: free choice / purpose"}],
  "pass_b_english": ["…"],
  "choices": [
    {
      "term": "προαίρεσις ἐλευθέρα",
      "english": "free deliberate choice",
      "why": "Justin’s anti-fate vocabulary; αὐτεξούσιον not in this sentence; contemporary apologetic usage against εἱμαρμένη",
      "rejected": ["free will (anachronistic system)", "autexousion (transliteration unused here)"]
    }
  ],
  "anf_compare": {"status": "same_sense", "notes": "ANF uglier; sense aligned"},
  "variants": [],
  "bible_refs": [{"display": "…", "method": "wording_or_map", "note": ""}],
  "checks": {"anf_diverge": "pass", "lemma_constraint": "pass"},
  "confidence": "source_verified",
  "reviewer": "pending-human"
}
```

## Cross-checks

| Check | Fail condition |
|-------|----------------|
| ANF diverge | Our English **contradicts** ANF sense |
| Lemma constraint | Pass B concept not grounded in Pass A |
| Lexicon | Key term outside LSJ/Lampe/Blaise range without note |
| Consensus | Two models disagree on agency/negation |
| Back-translation | Large drift vs source |
| Variant silence | Known MSS/edition conflict with no note |

## Bible refs

Verify by quotation wording / citation map, not model memory (Hosea 11:1 vs Exodus cases).

## Public label

Until Professional GTG: captions show real confidence.  
After: “Translated from named editions with justification receipts; corrections welcome.”
