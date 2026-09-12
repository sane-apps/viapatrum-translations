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

## How to claim

```bash
python3 scripts/claims.py start --agent YourName
```

Then do only that slice. Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`.

## Done / closed

| Claim ID | Status | Slice | Closed | Notes |
|----------|--------|-------|--------|-------|
| cyril-rf-a12 | done | CPG 5219 Arcadia §§45–48 (Pusey pp.200–204) Pass A≠B | 2026-09-12 | StephanAir; greek_clean_a12 + rf_arcadia_45–48; A≠B; no site CSS |
| cyril-rf-a11 | done | CPG 5219 Arcadia §§41–44 (Pusey pp.196–199) Pass A≠B | 2026-09-12 | StephanAir; greek_clean_a11 + rf_arcadia_41–44; A≠B; no site CSS |
| cyril-rf-a10 | done | CPG 5219 Arcadia §§37–40 (Pusey pp.192–195) Pass A≠B | 2026-09-12 | StephanAir; greek_clean_a10 + rf_arcadia_37–40; A≠B; no site CSS |
| cyril-rf-a9 | done | CPG 5219 Arcadia §§33–36 (Pusey pp.187–191) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a9 + rf_arcadia_33–36; A≠B; no site CSS |
| cyril-rf-a8 | done | CPG 5219 Arcadia §§29–32 (Pusey pp.183–186) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a8 + rf_arcadia_29–32; A≠B; no site CSS |
| cyril-rf-a7 | done | CPG 5219 Arcadia §§25–28 (Pusey pp.179–182) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a7 + rf_arcadia_25–28; A≠B; no site CSS |
| cyril-rf-a6 | done | CPG 5219 Arcadia §§21–24 (Pusey pp.175–178) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a6 + rf_arcadia_21–24; A≠B; no site CSS |
| cyril-rf-a5 | done | CPG 5219 Arcadia §§17–20 (Pusey pp.171–174) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a5 + rf_arcadia_17–20; A≠B; no site CSS |
| cyril-rf-a4 | done | CPG 5219 Arcadia §§13–16 (Pusey pp.166–170) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a4 + rf_arcadia_13–16; A≠B; no site CSS |
| reward-judgment-mine | done | Reward-and-judgment: Didache 16 (`didache_16_judgment`) + stance final-judgment | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance explore/stances.json |
| image-likeness-mine3 | done | Image-likeness: Barnabas 6 (`barnabas_6_image`) + stance image-retained | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance explore/stances.json |
| cyril-rf-a3 | done | CPG 5219 Arcadia §§9–12 (Pusey pp.162–165) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a3 + rf_arcadia_09–12; A≠B; no site CSS |
| universal-call-mine2 | done | Universal-call: Justin 1 Apology 40 (`justin_1apol_40_call`) + stance call-and-refusal | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance explore/stances.json |
| baptism-birth-mine2 | done | Baptism-and-new-birth: Didache 7 (`didache_7_baptism`) + stance baptism-regenerates | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance explore/stances.json |
| atonement-mine | done | Atonement-recapitulation: Irenaeus AH 3.18.7 (`irenaeus_ah_3_18_7`) + stance recap-adam | 2026-09-12 | Topics lane (StephanMini); locked Latin Pass A≠B; stance in explore/stances.json; ai_promote N/A |
| cyril-rf-a2 | done | CPG 5219 Arcadia §§5–8 (Pusey pp.158–161) Pass A≠B | 2026-09-12 | StephanMini; greek_clean_a2 + rf_arcadia_05–08; A≠B; no site CSS |
| image-likeness-mine2 | done | Image-likeness: Diognetus 10 (`diognetus_10_image`) + stance image-retained | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance explore/stances.json |
| atonement-recapitulation-mine | done | Atonement-recapitulation: Irenaeus AH 1.10.1 (`irenaeus_ah_1_10_1_recap`) + stance recap-adam | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance in explore/stances.json; ai_promote N/A |
| cyril-rf-a1 | done | CPG 5219 Arcadia §§1–4 (Pusey pp.153–157) Pass A≠B | 2026-09-12 | StephanMini; greek_clean + rf_arcadia_01–04; A≠B; no site CSS |
| fate-foreknowledge-mine | done | Fate-and-foreknowledge: Tatian Oratio 9 (`tatian_oratio_9_fate`) + stance choice-not-fate | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| two-ways-mine | done | Two-ways: Barnabas 18.1-2 (`barnabas_18_two_ways`) + stance two-ways | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| grace-assist-mine | done | Grace-and-assistance: Clement Stromata 3.7.57 (`clement_strom_3_7_57_grace`) + stance grace-assists | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| image-likeness-mine | done | Image-likeness: Clement Stromata 2.19.97 (`clement_strom_2_19_image_likeness`) + stance image-retained | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| baptism-birth-mine | done | Baptism-and-new-birth: Barnabas 11 (`barnabas_11_baptism_new_birth`) + stance baptism-regenerates | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| universal-call-mine | done | Universal-call: Diognetus 10.2 (`diognetus_10_2_universal_call`) + stance call-and-refusal | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| baptism-birth-mine | done | Baptism-and-new-birth: Barnabas 11 (`barnabas_11_baptism_new_birth`) + stance baptism-regenerates | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| image-likeness-mine | done | Image-likeness: Clement Stromata 2.19.97 (`clement_strom_2_19_image_likeness`) + stance image-retained | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B |
| cyril-rf-lock | done | Source lock CPG 5219–5220 → `ad_arcadiam_marinamque_source.json` + `ad_pulcheriam_eudociamque_source.json` | 2026-09-12 | StephanMini; Pusey OCR slice; no English |
| gifts-mine | done | Gifts-and-order: Ignatius To Polycarp 2.2 (`ignatius_polycarp_2_gifts_order`) + stance gifts-with-office | 2026-09-12 | Topics lane (StephanMini); locked Greek Pass A≠B; stance in explore/stances.json; ai_promote N/A (Jeremiah-only paths) |
| jer-h20b | done | Homily 20 §§20.5–20.8 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T042127Z-jer-h20b |
| jer-h20a | done | Homily 20 §§20.1–20.4 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T041856Z-jer-h20a |
| jer-h19 | done | Homily 19 §§19.10–19.15 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T041635Z-jer-h19 |
| jer-h18b | done | Homily 18 §§18.6–18.10 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T041336Z-jer-h18b |
| jer-h18a | done | Homily 18 §§18.1–18.5 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T041056Z-jer-h18a |
| jer-h17 | done | Homily 17 §§17.1–17.6 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T040832Z-jer-h17 |
| jer-h16b | done | Homily 16 §§16.6–16.10 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T040531Z-jer-h16b |
| jer-h16a | done | Homily 16 §§16.1–16.5 | 2026-09-12 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T040247Z-jer-h16a |
| jer-h15 | done | Homily 15 §§15.1–15.6 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T035925Z-jer-h15 |
| jer-h14c | done | Homily 14 §§14.13–14.18 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T035515Z-jer-h14c |
| jer-h14b | done | Homily 14 §§14.7–14.12 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T035338Z-jer-h14b |
| jer-h14a | done | Homily 14 §§14.1–14.6 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T035054Z-jer-h14a |
| jer-h12b | done | Homily 12 §§12.7–12.12 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T034847Z-jer-h12b |
| jer-h12a | done | Homily 12 §§12.1–12.6 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T034641Z-jer-h12a |
| jer-h11 | done | Homily 11 §§11.1–11.5 | 2026-09-11 | AI cross-check (StephanMini); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260912T034450Z-jer-h11 |
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
