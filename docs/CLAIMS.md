# Claims — who is working on what

Take the next free slice:

```bash
python3 scripts/claims.py start --agent YourName
```

That locks the top `free` row. One slice per person. Statuses: `free` → `claimed` → `prepped` (machine crib) or `done` (human Pass B).  
If a `claimed` row is older than 48 hours with no handoff, anyone may set it back to `free`.

## Open / active claims

| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |
|----------|--------|-----------|------------------|-------|---------|--------|-------|

| jer-h11 | prepped | origen-jeremiah-samuel | Homily 11 §§11.1–11.5 | overnight-mini-nv | 2026-09-11 | wip/jer-h11 | machine crib (Pass A/lemmas/OCR); not reading English |

| jer-h12a | prepped | origen-jeremiah-samuel | Homily 12 §§12.1–12.6 | overnight-mini-nv | 2026-09-11 | wip/jer-h12a | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h12b | prepped | origen-jeremiah-samuel | Homily 12 §§12.7–12.12 | overnight-mini-nv | 2026-09-11 | wip/jer-h12b | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h14a | prepped | origen-jeremiah-samuel | Homily 14 §§14.1–14.6 | overnight-mini-nv | 2026-09-11 | wip/jer-h14a | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h14b | prepped | origen-jeremiah-samuel | Homily 14 §§14.7–14.12 | overnight-mini-nv | 2026-09-11 | wip/jer-h14b | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h14c | prepped | origen-jeremiah-samuel | Homily 14 §§14.13–14.18 | overnight-mini-nv | 2026-09-11 | wip/jer-h14c | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h15 | prepped | origen-jeremiah-samuel | Homily 15 §§15.1–15.6 | overnight-mini-nv | 2026-09-11 | wip/jer-h15 | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h16a | prepped | origen-jeremiah-samuel | Homily 16 §§16.1–16.5 | overnight-mini-nv | 2026-09-11 | wip/jer-h16a | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h16b | prepped | origen-jeremiah-samuel | Homily 16 §§16.6–16.10 | overnight-mini-nv | 2026-09-11 | wip/jer-h16b | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h17 | prepped | origen-jeremiah-samuel | Homily 17 §§17.1–17.6 | overnight-mini-nv | 2026-09-11 | wip/jer-h17 | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h18a | prepped | origen-jeremiah-samuel | Homily 18 §§18.1–18.5 | overnight-mini-nv | 2026-09-11 | wip/jer-h18a | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h18b | prepped | origen-jeremiah-samuel | Homily 18 §§18.6–18.10 | overnight-mini-nv | 2026-09-11 | wip/jer-h18b | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h19 | prepped | origen-jeremiah-samuel | Homily 19 §§19.10–19.15 | overnight-mini-nv | 2026-09-11 | wip/jer-h19 | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h20a | prepped | origen-jeremiah-samuel | Homily 20 §§20.1–20.4 | overnight-mini-nv | 2026-09-11 | wip/jer-h20a | machine crib (Pass A/lemmas/OCR); not reading English |
| jer-h20b | prepped | origen-jeremiah-samuel | Homily 20 §§20.5–20.8 | overnight-mini-nv | 2026-09-11 | wip/jer-h20b | machine crib (Pass A/lemmas/OCR); not reading English |
| cyril-rf-lock | free | cyril-alexandria-recta-fide-court | Source lock only: slice Pusey CPG 5219–5220 into `*_source.json` | | | wip/cyril-rf-lock | **No English** — source lane |
| gifts-mine | free | ante-nicene-topics | Gifts-and-order: one new locked-source excerpt + stance | | | wip/gifts-mine | Topics lane |

## How to claim

```bash
python3 scripts/claims.py start --agent YourName
```

Then do only that slice. Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`.

## Done / closed

| Claim ID | Status | Slice | Closed | Notes |
|----------|--------|-------|--------|-------|
| jer-h13 | done | Homily 13 §§13.1–13.3 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T033948Z-jer-h13 |
| jer-h5c | done | Homily 5 §§5.13–5.17 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T033821Z-jer-h5c |
| jer-h5b | done | Homily 5 §§5.7–5.12 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T033544Z-jer-h5b |
| jer-h5a | done | Homily 5 §§5.1–5.6 | 2026-09-11 | AI cross-check (StephanMini); @cf/meta/llama-3.1-8b-instruct-fp8-fast+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T033224Z-jer-h5a |
| jer-h8 | done | Homily 8 §§8.1–8.9 | 2026-09-11 | NVIDIA promote on Mini; machine_draft, not shipped |
| jer-h10 | done | Homily 10 §§10.1–10.8 | 2026-09-11 | AI cross-check (overnight-cursor); @cf/google/gemma-4-26b-a4b-it + @cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260911T171847Z-jer-h10 |
| jer-h9 | done | Homily 9 §§9.1–9.4 | 2026-09-11 | AI cross-check (overnight-cursor); @cf/google/gemma-4-26b-a4b-it + @cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260911T171631Z-jer-h9 |
| jer-h7 | done | Homily 7 §§7.1–7.3 | 2026-09-11 | AI cross-check (overnight-cursor); @cf/meta/llama-3.1-8b-instruct-fp8-fast + @cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260911T171301Z-jer-h7 |
| jer-h6 | done | Homily 6 §§6.1–6.3 | 2026-09-11 | AI cross-check (overnight-cursor); @cf/meta/llama-3.1-8b-instruct-fp8-fast + @cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260911T171037Z-jer-h6 |
| jer-h1-4 | done | Homilies 1–4 (27 §§) | 2026-09-11 | Owner lane; Homilies 1–4 two-pass on site |

## Do not claim these (owner / blocked)

- Website deploy / Cloudflare Pages / edits under `websites/fathers.saneapps.com`
- Logos Personal Book compile; `build_book.py` unless owner asked
- Inventing a new book slug without `docs/WORKS_QUEUE.md` + charter
- Any modern or ANF English as the reading text
- Changing Slice columns or merging/splitting claim rows (ask owner)
