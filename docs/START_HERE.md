# Start here

## Fathers public UX (standing)

If your claim touches fathers.saneapps.com presentation or a tip ship, read first the site repo AGENTS.md section **Standing UX rules**.

Acknowledge in working notes before editing: English-first titles everywhere public-facing; author dates on Authors index; no fake-link underlines; Author accordion bios; always-on mobile nav; tip-only closeout labeling when partial.

Copy this whole file into your AI.

You are helping finish public-domain Fathers texts in new English for https://fathers.saneapps.com.

Do not copy FOTC, ACW, ANF, NPNF, blogs, or other English. Translate from the locked Greek or Latin in https://github.com/sane-apps/translations

Clone that repo if you do not already have it. Then run:

```bash
python3 scripts/claims.py start --agent YourName
```

Replace YourName with a real name. That takes the next free slice and prints what to do. One slice only.

Then:

- Read the book’s `books/<slug>/SESSION_HANDOFF.md`.
- Translate only the sections on that claim.
- **Pass A:** literal gloss + lemmas in `reviews/justifications/<id>.json` (`pass_a_gloss`). Copy an existing file in that folder for the shape.
- **Pass B:** reading English in `translations/*_english.json` → `english[]`. Same meaning as A, in the author’s voice. Do not paste A as B. Clear Scripture quotes/allusions need **inline parenthetical refs** in that English (not only `added_allusions` / `bible_refs`).
- Title the thought, not the section number.
- Check exact author/work/source identity and full declared scope against the raw edition. Preserve all clauses; a tip slice must not replace a chapter. Produce genuine source/English-bound evidence under SOP §3. Missing evidence or uncertainty means fix or hold, never mark done.
- Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`
- Before SERIES CLOSEOUT / marking a tip done: `python3 scripts/assert_tip_ready.py <stem>_english.json <stem>_source.json` must exit 0 (refuses Lemma-led / Rem * scaffolds and tip ops in source).
- Stop. Do not take a second slice. Do not deploy the website. Do not run Logos.

If there is no free slice, stop and say so.

More detail: `docs/SOP.md`.
