# Start here

You are helping finish public-domain Fathers texts in **new English** for https://fathers.saneapps.com.

Do **not** copy modern English (FOTC, ACW, ANF, NPNF, blogs, other sites). Translate from the locked Greek or Latin in this repo.

---

## Humans

Clone [this repo](https://github.com/sane-apps/translations). Point your AI at **this file**, then paste:

```bash
python3 scripts/claims.py start --agent YourName
```

The command takes the next free slice and prints what the AI should do. One slice at a time. Stop when it is done.

If you already keep the repo at `~/SaneApps/clients/translations`, `cd` there first.

Spot a bad English reading and you read Greek or Latin? [Submit a correction](https://github.com/sane-apps/translations/issues/new?template=correction.yml).

---

## AIs — do this

1. Run `python3 scripts/claims.py start --agent YourName` if a slice is not already assigned. Use a real name, not `YourName`.
2. Read the book’s `books/<slug>/SESSION_HANDOFF.md`.
3. Translate **only** the sections on that claim.
4. For each section:
   - **Pass A:** a literal gloss + key lemmas in `reviews/justifications/<id>.json` (`pass_a_gloss`). Copy an existing file in that folder for the shape.
   - **Pass B:** reading English in `translations/*_english.json` → `english[]`. Same meaning as A, in the author’s voice. Do not paste A as B.
   - Title the **thought**, not the section number.
5. Finish with:

```bash
python3 scripts/ai_promote.py --claim <id> --agent YourName
```

6. Stop. Do not take a second slice. Do not deploy the website. Do not run Logos.

If there is no free slice, stop and say so.

More detail if you need it: `docs/SOP.md`.
