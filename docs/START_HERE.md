# START HERE — for any human or LLM contributing


**Repo:** https://github.com/sane-apps/translations  
**Default LLM draft model (Cloudflare):** `@cf/qwen/qwen3-30b-a3b-fp8` (see `docs/LLM_API_SETUP.md`; drafts stay in claim `review`, never auto-`done`).
**Paste this file into your AI first.** Then do only what it says.

You are helping translate early Christian (and later Reformer) texts into new English from locked public-domain Greek/Latin, for private study and for https://fathers.saneapps.com. You are not inventing a process.

Repo root: `~/SaneApps/clients/translations` (same path on every machine).

---

## Recommended draft engine (2026-09-11 bake)

After a controlled bake (`docs/LLM_BAKE_PROTOCOL.md` → `outputs/llm-bakeoff/VERDICT.md`):

- **Default (contributors / overnight drafts):** Cloudflare Workers AI `@cf/qwen/qwen3-30b-a3b-fp8`
- **Fallback:** `@cf/meta/llama-3.1-8b-instruct-fp8-fast`
- **Oracle (owner):** `@cf/meta/llama-3.3-70b-instruct-fp8-fast`
- Helper prompt/fixture: `python3 scripts/llm_bakeoff.py --section <H.S> --models '@cf/qwen/qwen3-30b-a3b-fp8'`
- Drafts still go to claim status **`review`** — never auto-publish.

NVIDIA free NIM is optional research only until it stops truncating/hanging on long JSON.

---

## Do this, in order

### 1. Read these three files (and nothing else yet)

1. This file (`docs/START_HERE.md`)
2. `docs/CLAIMS.md` — what is free / taken
3. `docs/SOP.md` — how a slice is finished

If the work ships to the public site, also skim:  
`~/SaneApps/websites/fathers.saneapps.com/AGENTS.md` → **Works reader SOP**.

### 2. Take one free claim (mandatory — before any translation file)

- Always take the **topmost** `free` row in `docs/CLAIMS.md` — not the row that “looks easiest” in Notes.
- Prefer the helper (avoids two agents grabbing the same row):

```bash
cd ~/SaneApps/clients/translations
python3 scripts/claims.py free
python3 scripts/claims.py take jer-h6 --agent YourName
```

- If you cannot run the script: re-open `CLAIMS.md` fresh, set that one row to `claimed`, fill Agent + Started (`YYYY-MM-DD`) + Branch, save **once**. If it is already `claimed`, take the next `free` row.
- **At most one row may be `claimed` by you at a time.** Never claim `jer-h5a`+`jer-h5b`+`jer-h5c` together.
- **Do not edit English (or source JSON) until the claim is saved as `claimed`.** Your first commit for the slice must include that `CLAIMS.md` (and lock) change.
- Branch name must be exactly `wip/<claim-id>` (example: `wip/jer-h6`).  
  If you do not know how to create that Git branch, **stop and ask a human** — do not translate on `main`.
- Never edit section IDs that are already `done`, or any ID not on your active `claimed` row.

### 3. Do only that slice

- Read `books/<slug>/SESSION_HANDOFF.md` for the book named in your claim row.
- There is **no** single “church fathers” file. English for Jeremiah lives only in:

  `books/origen-jeremiah-samuel/translations/jeremiah_english.json`

  Locked Greek for those sections:

  `books/origen-jeremiah-samuel/translations/jeremiah_source.json`

  (Other books: same pattern — `books/<slug>/translations/*_english.json` + `*_source.json`.)

- Translate **only** the section IDs in your claim’s Slice column (e.g. `jer-h5a` → §§5.1–5.6 only).
- **Two-pass** (required; detail in `docs/SOP.md`):
  - **Pass A** lives in each justification JSON as `pass_a_gloss` (+ lemmas) — **not** in `*_english.json` or `*_source.json`.
  - **Pass B** = reading English only in `*_english.json` `english[]` (may not add ideas missing from A).
- One justification file **per section**. For Origen Jeremiah, section `H.S` →  
  `books/origen-jeremiah-samuel/reviews/justifications/jeremiah_H_S.json`  
  (example: §6.1 → `jeremiah_6_1.json`). **Copy** an existing receipt such as  
  `books/origen-jeremiah-samuel/reviews/justifications/jeremiah_1_1.json` and fill new fields; every new file must include `pass_a_gloss`.
- Update `books/<slug>/SESSION_HANDOFF.md` when the slice is done.
- Set your claim to `review` when finished. **`review` does not publish anything** — only the owner merges and rebuilds the site.

### 4. Stop when the slice is done

Do **not** start a second claim until the first is `review` or `done`.  
Do **not** deploy the website, edit `~/SaneApps/websites/fathers.saneapps.com`, run Cloudflare, run `build_book.py`, or compile Logos unless the owner explicitly asked in this thread.

---

## Hard rules (never break these)

| Do | Do not |
|----|--------|
| New English from the **locked** Greek/Latin in `books/<slug>/sources/` and `translations/*_source.json` | Copy or paraphrase **any** English edition or web page (FOTC, ACW, NPNF, ANF, Victorian PD, blogs, site English from other homilies as meaning-source, machine English) |
| Two passes: `pass_a_gloss` in justification JSON + Pass B in `*_english.json`. Pass B may not add ideas missing from A | One draft only; or Pass A == Pass B pasted |
| Section `title` / `head` = **name of the thought** | Titles that are only loci (“Homily 5.3”, “Against Julian 1.5.16”) |
| One claim at a time; JSON edits limited to that claim’s section IDs | “I’ll finish all of Homily 5 / all of Origen”; editing `done` slices |
| Mark OCR gaps in `translator_notes`; restore known Bible quotes from the biblical wording and say so | Invent Greek or fill lacunae silently from another English edition |
| Keep Latin/Greek in source fields / panels | “Scripture connection:” caption dumps |
| Ask before public publish / purchase / Logos Build | Deploy `fathers.saneapps.com`; touch `websites/`; run `build_book.py` / Logos; change Slice columns |

PRs must stay under `clients/translations` only (no website / Cloudflare / Logos paths). PRs without a matching `claimed`→`review` row and a section-ID-scoped diff will be rejected.

---

## Two-pass (short)

Full detail: `books/ante-nicene-topics/docs/TRANSLATION_QA.md` and `docs/SOP.md`.

1. **Pass A** — literal gloss + lemmas in `reviews/justifications/<id>.json` → field `pass_a_gloss` (from locked source only).  
2. **Pass B** — Reading English in `*_english.json` → `english[]`. Same meaning as A; better prose; author’s voice.  
3. **Receipt** — that same justification file also holds confidence (`source_verified`) and `reviewer: pending-human` until a human signs off. `pass_a_gloss` must not equal joined Pass B.

---

## Done for your claim means

- [ ] Claim row → `review` (and leave the lock under `docs/claim-locks/<id>/` until owner closes it)
- [ ] Pass B English in `*_english.json` for every section ID on the claim
- [ ] One justification JSON per section with `pass_a_gloss` (copy `jeremiah_1_1.json` shape for Jeremiah)
- [ ] Thought titles (not locus labels)
- [ ] `SESSION_HANDOFF.md` updated
- [ ] No website deploy / Logos / `build_book.py` from you

---

## If you are stuck

- No `free` claims → stop and say so; do not invent work.  
- Source Greek looks broken → note OCR gap; do not guess whole sentences.  
- Unsure of SOP → re-read `docs/SOP.md`; do not invent a parallel process.  
- `claims.py take` says already locked → take the next free claim.

---

## Human (non-technical) cheat sheet

Tell your AI exactly this:

> Open `~/SaneApps/clients/translations/docs/START_HERE.md` and follow it.  
> Run `python3 scripts/claims.py take <id> --agent YourName` for one free slice (see `python3 scripts/claims.py free`).  
> Do not deploy the site. Do not copy modern or ANF English.
