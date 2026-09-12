# Cyril on Matthew — status

Updated: 2026-09-12 (Air)

## Identity

| Field | Value |
|-------|-------|
| Author | Cyril of Alexandria (not Origen) |
| Work | *Fragmenta in Matthaeum* (catena fragments) |
| **CPG** | **5206** |
| Book slug | `cyril-alexandria-matthew-fragments` |
| Closed | CPG 5219/5220 (*recta fide*) — do not reopen |

## Source lock

| Role | Witness | Usable? |
|------|---------|---------|
| **copy-text** | khazarzar / Aegean Digital Patrologia extract of Migne PG 72 (`Commentarii in Matthaeum.pdf` + `.txt`) | Yes — readable Greek |
| check | matia.gr mirror of same extract | Byte-identical to khazarzar (integrity only) |
| check only | IA `bim_…_1859_72` DjVu OCR | **Junk OCR — ignore as copy-text**; locus confirmation (~cols 365ff) |
| not locked | Reuss TU 61 (1957) | Copyrighted; edition-history note only |

- Manifest: `books/cyril-alexandria-matthew-fragments/sources/manifest.json`
- Source JSON: `translations/matthew_fragments_source.json` — **290** fragment heads parsed
- Diff before Pass A: khazarzar == matia; IA not merged

## Claims

| Claim ID | Status | Slice |
|----------|--------|-------|
| `cyril-matt-frag-lock` | done | Source lock |
| `cyril-matt-frag-a1` | done | fr.1–4 Pass A≠B |
| next | free | `cyril-matt-frag-a2` from fr.5 |

Tip SHA: `452e8f3` (`452e8f3800a2cd96f19ce4c5bd758b010ceac130`) on `cursor/cyril-matthew-fragments-1dff`.

## Guards

Pass A ≠ Pass B; CLAIMS helpers; jer-h20b intact; no CSS; Melito skipped; CPG 5219/5220 closed; no invented Greek.
