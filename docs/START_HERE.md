# Start here

Copy this whole file into your AI assistant (Claude, ChatGPT, Grok, Gemini, Cursor, anything that can use git). Many people work at once; the steps below keep you from colliding.

You are helping Via Patrum (https://viapatrum.org), a free library of the early Church Fathers in faithful, readable modern English, translated from the Greek and Latin sources in https://github.com/sane-apps/translations. Never copy an existing English translation (ANF, NPNF, FOTC, ACW, blogs or any other).

## 1. Pick one task and claim it (this is what prevents collisions)

1. Open https://github.com/sane-apps/translations/issues and choose ONE open issue labelled `help wanted` (or `held-section`) that does NOT have the `claimed` label.
2. Comment exactly `/claim` on it. Within a minute a bot replies "Claimed by @you" and adds the `claimed` label. If it says someone else already has it, pick another issue.
3. Work only on that issue. One issue per person at a time. If you stop, comment `/unclaim`. A claim with no pull request expires after 7 days.

## 2. Get only the files you need (the full repository is over 10 GB)

```bash
git clone --filter=blob:none --no-checkout https://github.com/sane-apps/translations.git
cd translations
git sparse-checkout init --cone
git sparse-checkout set docs held scripts
git checkout main
# if the issue names a book folder, add just that book:
git sparse-checkout add books/<book-slug>
```

This takes seconds and about 50 MB.

## 3. Do the work

- **`held-section` issues:** follow `held/README.md`. Edit only the `english` list of the one file the issue names. Keep every claim, negation and Scripture reference; add nothing. Where the source is corrupt, translate what is there and mark a guess in square brackets.
- **Retranslation issues (`[fidelity]`):** translate from the locked source in that book's folder: a literal gloss first (Pass A), then readable modern English (Pass B). The details are in "Maintainer slices" below and in `docs/SOP.md`.
- Explain your reading in the pull request and cite the Greek or Latin words.

## 4. Open one pull request

- Branch from `main`, change only the files your issue needs, and open a pull request whose description says `Fixes #<issue number>`.
- Then stop. Do not take a second issue until a maintainer reviews the first.
- A maintainer reviews every pull request. After merge the pipeline imports and checks the work and re-reads the whole book before anything is published.

Questions go in a comment on the issue.

---

## Maintainer slices (internal lanes and long-time contributors)

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

No free slice, or you would rather fix than translate? Take one GitHub issue labelled `held-section` and follow `held/README.md`: edit only the `english` of that one file, explain your reading in the pull request, and stop.

More detail: `docs/SOP.md`.
