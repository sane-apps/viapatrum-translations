# Melito, Peri Pascha — transcription workspace

Project transcription from the papyrus witnesses, made from the institutions'
own served images. No modern edition's text is copied anywhere in this folder:
Hall (1979) and Perler (SC 123) are collation references only, consulted in a
later pass to catch transcription errors, with divergences logged in
`../reviews/`.

## Witnesses and image sets (provenance in `../sources/manifest.json`)

- **B** = P. Bodmer XIII, in the composite codex P. Bodmer C (Fondation Martin
  Bodmer, Cologny; Bodmer Lab, UNIGE). Barcode 1072205366. IIIF manifest:
  https://iiif.hedera.unige.ch/iiif/manifests/bodmerlab/IIIFManifest_1072205366.json
  (licence stated in the manifest: CC BY-NC 4.0). Melito occupies canvases
  056-095 of the codex sequence; images filed in `../sources/bodmer-xiii/`.
- **C** = P. Chester Beatty XII (Chester Beatty Library, Dublin; images via
  CSNTM). High-resolution viewer requires a free CSNTM account login; the
  anonymous IIIF endpoint serves only 100 px thumbnails (larger requests
  return HTTP 500, verified 2026-10-25). Thumbnails filed in
  `../sources/chester-beatty-xii/`; collation against C is blocked on the
  login, see `../sources/chester-beatty-xii/README.md`.

## Conventions

- One file per page (or opening), named by section range.
- Diplomatic transcript first: the scribe's letters in Greek capitals,
  scriptio continua, line breaks kept, nomina sacra as written (with the
  overline noted), the scribe's apostrophe-like word dividers marked ' .
- `[ ]` = lacuna / lost letters. `(?)` after a word = reading uncertain.
- Resolved reading second: word-divided, lower case, accents added by the
  transcriber, nomina sacra expanded in ( ). Only letters actually on the
  papyrus are resolved; nothing is imported from any edition.
- Section numbers follow the plate captions printed on the Bodmer scans
  themselves where they exist; other boundaries are marked "(inferred)".

## Canvas map for P. Bodmer XIII (canvases of PB C, barcode 1072205366)

| Canvas | Content | Sections |
|---|---|---|
| 055 | End of Jude (PB VII), explicit, codex p. ΞΗ | (previous work) |
| 056 | Melito title leaf: ΜΕΛΙΤΩΝΟC ΠΕΡΙ ΠΑCXΑ | title |
| 057 | Fragments, Melito p. Α | §§1-3 (plate caption) |
| 058 | Fragments, Melito p. Β | §§3-6 (plate caption) |
| 059 | Melito p. Γ, complete page | §§6-9 (inferred) |
| 060-062 | Duplicate angled photographs of the p. Γ page | (same as 059) |
| 063 | Opening, Melito pp. Δ-Ε | §§9-11 / §§11-13 (plate captions) |
| 064 | Opening | §§14-15 / §§15-17 (plate captions) |
| 066 | Opening | §§20-23 (plate captions) |
| 085 | Opening | §§74-78 (plate captions) |
| 090 | Opening | §§91-92 (plate captions) |
| 095 | Final Melito page, explicit ΑΜΗΝ ΜΕΛΙΤΩΝΟC ΠΕΡΙ ΠΑCXΑ | §§104-105 (plate caption) |
| 096-108 | PB XII (hymn) and photographic targets/covers | (next work) |

Canvases between the sampled points are Melito in sequence; their exact
section ranges are fixed as each page is transcribed.

## State (2026-10-25, Phase 1)

Transcribed: title leaf; pp. Α, Β (fragmentary, diplomatic only);
p. Γ (complete); pp. Δ-Ε (complete). Resolved reading text filed in
`../translations/mpp_source.json` for §§9-13 only; §§1-8 resolution waits on
the collation pass because the opening leaves are fragmentary and two word
shapes on p. Γ are not yet settled (see the notes in
`03-sections-006-009_pGamma.md`).
