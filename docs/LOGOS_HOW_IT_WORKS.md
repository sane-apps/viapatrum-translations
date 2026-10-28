# How bulk upload into Logos works — the plain-language version

*Read this first. The full operator detail lives in `LOGOS_PIPELINE.md`
(how the automation runs) and `LOGOS_MARKUP.md` (how a DOCX must be tagged).
This page is the story those two assume you already know.*

## The one-paragraph version

Logos has **no bulk-import API** for Personal Books. So this system does the
two things Logos *does* allow, automatically, for every book:

1. **It writes the book's row directly into Logos's own database**
   (`PersonalBookManager.db`) from the book's `book.yml` — title, author,
   type, description, and the path to its DOCX file. This is `pb_sync.py`.
   A timestamped backup of the database is taken first, every time.
2. **It drives the Logos app's UI** (accessibility clicks — the same clicks
   a human would make) to press **Build book** on each new or changed row,
   then **Upload** on each built book. This is `logos_build.py`.

**Build** compiles the DOCX into a Logos book on that one machine.
**Upload** is the step that matters: it puts the book on Faithlife's servers,
which is what makes it appear in the owner's library on *every* device
(Mini, Air, phone, web). A built-but-not-uploaded book exists only locally.

It runs by itself every Sunday at 04:00 on the Mini (LaunchAgent
`com.saneapps.fathers-logos-build`). Nobody clicks anything.

## What a new book needs before the pipeline will take it

All four, or the book is **held** (logged as `HOLD`, never silently dropped):

- **The DOCX**, built from the certified English by
  `python3 scripts/build_pbb_docx.py --catchup` and tagged per
  `LOGOS_MARKUP.md` (Bible references as real Logos datatype links, headword
  milestones, translator notes in their required place).
- **A clean DOCX**: no translator worksheet notes left in the text (things
  like `True OET` / `Pass A` — `verify_docx` checks), not older than its
  English source or `intro.md`, and an Introduction present when `intro.md`
  exists.
- **`book.yml`** that parses as YAML, with title, author, and `pb_type`
  carrying the full dotted prefix (e.g. `text.monograph.…`). After the first
  sync, the book's Logos `resource_id` is written back into `book.yml` —
  that ID, not the title, is the book's identity from then on.
- **A cover** (`assets/cover.jpg` or `cover.png`). No cover = no upload.
  This is deliberate: a coverless book in the library looks broken.

## Running it by hand

```
python3 scripts/logos_build.py --dry-run          # show the plan, change nothing
python3 scripts/logos_build.py --book <slug>      # one book, sync + build + upload
python3 scripts/logos_build.py --build-only       # builds only
python3 scripts/logos_build.py --upload-only      # uploads only
python3 scripts/logos_backlog.py                  # refresh the backlog, read-only
```

Exit 2 means *partial* failure: the run receipt
(`outputs/logos_runs/<stamp>.json`) names the failed books; fix them and
re-run with `--book`.

## How you know it worked (no screenshots needed)

| Step | Proof |
|------|-------|
| Sync | `verify: all synced rows read back OK.` in pb_sync's output |
| Build | the book's `LastCompiled` timestamp in the database flips, and the row reports `Build succeeded with N errors, M warnings.` |
| Upload | the edit view shows `Upload successful.`, and a receipt lands in `outputs/logos_uploads.json` |

## The hard-won rules (learned by trial and error — do not relearn them)

- **Never match a book by title alone.** 13 titles are shared by more than
  one book (*Fragments on John* has four authors). Match on `resource_id`,
  or on title **and** author, and confirm the row's body file is this book's
  DOCX before building.
- **Logos never builds on its own.** A row with no `LastCompiled` sits
  Pending forever until something clicks **Build book**.
- **A freshly built row can't be re-clicked in the same session** (it
  expands inline), which is why the pipeline restarts Logos between the
  build phase and the upload phase, and again after every couple of builds.
- **Row titles in the UI can contain line breaks** and long lists go
  click-dead as rows expand; the driver waits for the list to settle and
  clicks mid-row. If clicks stop landing, restart Logos — don't click harder.
- **Upload leaves no trace in the local database.** The upload ledger is
  `outputs/logos_uploads.json` in this repo. Trust it, not the DB.
- Control state lies: the UI's `enabled` property reads `missing value` on
  Logos's .NET controls. The driver verifies by *outcome* (database flip,
  result text), never by control state.

## Where things live

- Backlog (generated — do not hand-edit): `docs/LOGOS_BACKLOG.md`
- Upload receipts: `outputs/logos_uploads.json`
- Run receipts: `outputs/logos_runs/<stamp>.json`
- Database backups: `outputs/pb-db-backups/`
- Troubleshooting: the end of `LOGOS_PIPELINE.md`
