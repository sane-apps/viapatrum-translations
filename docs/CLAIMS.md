# Claims — who is working on what

**Read `docs/START_HERE.md` first.**

Only one agent may hold a claim. Prefer:

```bash
python3 scripts/claims.py take <claim-id> --agent YourName
```

That uses a folder lock so two agents cannot take the same id. Manual edits of this table are allowed only if you re-read the file immediately before saving; if the row is already `claimed`, take the next `free` row.

Statuses: `free` → `claimed` → `done`  
(Optional tool status `checking` while `ai_promote.py` runs. Do not park work in human `review`.)  
Expiry: if `claimed` older than **48 hours** with no handoff update, anyone may set it back to `free` (and remove `docs/claim-locks/<id>/` if present).

**Always take the topmost `free` row** (table order). Do not skip ahead to a “easier” Notes line.  
**At most one `claimed` row per agent.**  
**Done gate:** `docs/AI_CROSSCHECK.md` — two independent models + structural checks; no human reviewer.

## Open / active claims

| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |
|----------|--------|-----------|------------------|-------|---------|--------|-------|
| jer-h6 | free | origen-jeremiah-samuel | Homily 6 §§6.1–6.3 | | | wip/jer-h6 | Short — best first claim |
| jer-h7 | free | origen-jeremiah-samuel | Homily 7 §§7.1–7.3 | | | wip/jer-h7 | Short |
| jer-h9 | free | origen-jeremiah-samuel | Homily 9 §§9.1–9.4 | | | wip/jer-h9 | Medium |
| jer-h10 | free | origen-jeremiah-samuel | Homily 10 §§10.1–10.8 | | | wip/jer-h10 | Medium |
| jer-h8 | free | origen-jeremiah-samuel | Homily 8 §§8.1–8.9 | | | wip/jer-h8 | Medium |
| jer-h5a | free | origen-jeremiah-samuel | Homily 5 §§5.1–5.6 | | | wip/jer-h5a | First third of Homily 5 only |
| jer-h5b | free | origen-jeremiah-samuel | Homily 5 §§5.7–5.12 | | | wip/jer-h5b | Middle third only |
| jer-h5c | free | origen-jeremiah-samuel | Homily 5 §§5.13–5.17 | | | wip/jer-h5c | Final third only |
| cyril-rf-lock | free | cyril-alexandria-recta-fide-court | Source lock only: slice Pusey CPG 5219–5220 into `*_source.json` | | | wip/cyril-rf-lock | **No English** — source lane |
| gifts-mine | free | ante-nicene-topics | Gifts-and-order: one new locked-source excerpt + stance | | | wip/gifts-mine | Topics lane |

## How to claim

```bash
python3 scripts/claims.py free
python3 scripts/claims.py take jer-h6 --agent YourName
```

Then create branch `wip/<claim-id>`, work only those section IDs, Pass A + Pass B, justifications, handoff → run `python3 scripts/ai_promote.py --claim <id> --agent YourName` → Status `done`.

## Done / closed

| Claim ID | Status | Slice | Closed | Notes |
|----------|--------|-------|--------|-------|
| jer-h1-4 | done | Homilies 1–4 (27 §§) | 2026-09-11 | Owner lane; on site |

## Do not claim these (owner / blocked)

- Website deploy / Cloudflare Pages / edits under `websites/fathers.saneapps.com`
- Logos Personal Book compile; `build_book.py` unless owner asked
- Inventing a new book slug without `docs/WORKS_QUEUE.md` + charter
- Any modern or ANF English as the reading text
- Changing Slice columns or merging/splitting claim rows (ask owner)
