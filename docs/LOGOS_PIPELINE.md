# Logos Personal Books pipeline (Mini-automated)

Proven end-to-end 2026-09-23 on Logos 53.1 (Mini). No human clicks.
Air-only GUI steps are retired; SOP.md section 5 points here.

## What runs weekly

`scripts/logos_build.py` (LaunchAgent `com.saneapps.fathers-logos-build`,
Sundays 04:00 local, after the 03:00 independent-review job):

1. Quit Logos (SIGTERM; the app blocks graceful AppleScript quit with a
   dialog) and run `scripts/pb_sync.py --apply` (metadata from
   `books/*/book.yml` into `PersonalBookManager.db`, timestamped backup
   in `outputs/pb-db-backups/`).
2. Relaunch Logos, open `logos4:PersonalBooks`, wait for AX-ready.
3. **Build loop** for every DOCX book with `LastCompiled` NULL or older
   than the DOCX mtime: scroll-search the row by title, click it,
   verify the body file, AX-click **Build book**, poll `LastCompiled`
   until it flips (10 min timeout per book).
4. Restart Logos (a freshly built row expands inline and cannot be
   re-clicked in the same session).
5. **Upload loop** for every compiled book with no upload receipt (or
   rebuilt since its receipt): open the edit view, AX-click **Upload**,
   wait for the `Upload successful.` text (5 min timeout). Receipts in
   `outputs/logos_uploads.json` (`{slug: iso-timestamp}`).
6. Regenerate `docs/LOGOS_BACKLOG.md` and write a run receipt to
   `outputs/logos_runs/<stamp>.json`.

Verification signals (all machine-checked, no screenshots needed):

| Step   | Pass signal | Where |
|--------|-------------|-------|
| Sync   | `verify: all synced rows read back OK.` | pb_sync stdout |
| Build  | `LastCompiled` flips to a new timestamp | `PersonalBookManager.db` |
| Build  | `Build succeeded with N errors, M warnings.` | PB row text (receipt) |
| Upload | `Upload successful.` | PB edit-view text |

Upload is what puts the book on Faithlife servers, i.e. into **all**
owner libraries (Mini, Air, mobile, web). Build alone stays local.

## Manual operations

- Dry run (no changes): `python3 scripts/logos_build.py --dry-run`
- One book: `python3 scripts/logos_build.py --book <slug>`
- Builds only / uploads only: `--build-only` / `--upload-only`
- Backlog refresh (read-only, safe while Logos runs):
  `python3 scripts/logos_backlog.py`
- DB spot-check: `python3 -m pipeline.verify_logos_db --title-substr "<frag>"`

The script takes `outputs/logos_build.lock`; a second run refuses while
the lock exists. Exit 2 with per-book entries in the run receipt means
partial failure — fix the named books with `--book` and re-run.

## Known UI behaviors (encoded in the driver)

- Logos never auto-builds: NULL-`LastCompiled` rows sit Pending through
  restarts and tool reopens until **Build book** is clicked.
- After a build the view collapses to the list with an expanded result
  row; title clicks no longer reopen that row until relaunch (hence the
  phase-4 restart between builds and uploads).
- AX row titles can contain newlines mid-title; matching uses a
  contiguous first-5-words substring (unique across all 31 titles),
  then verifies the body filename before clicking anything.
- A row click either opens the edit view or only selects the row
  (revealing an `Edit` affordance at the right edge); the driver
  follows `Edit` when the first click merely selects.
- Clicks must land mid-row on a settled list: the driver waits for
  list quiescence, tries middle then near-left offsets, and restarts
  Logos after every 2 successes plus on click-dead retries, because
  each success expands its row and old sessions go click-dead.
- The AX `enabled` property reads `missing value` on Logos .NET
  controls; the driver verifies by outcome (DB flip / result text),
  never by control state.
- `Upload` writes no local-DB trace (`SyncState`/`SyncRevision` do not
  change); the repo-side `logos_uploads.json` is the upload ledger.

## Backlog state

`docs/LOGOS_BACKLOG.md` is generated. Two queues:

- **Build/upload queue**: DOCX exists (31 books as of 2026-09-23). Fully
  automatic once the DOCX lands.
- **DOCX queue** (406 books): Logos-blocked until a builder exists
  (`build_book.py` per book, or the per-slice DOCX builder). This is the
  real Logos backlog — not clicks.

## Troubleshooting

- `lock exists`: a run is active (`pgrep -f logos_build.py`) or a prior
  run died; if no process, delete the lock and re-run.
- `PB tool never became AX-ready`: Logos may be showing a modal (update
  prompt, sign-in). Resolve on screen, re-run with `--book`.
- `Upload failed` text: usually transient Faithlife errors; re-run
  `--upload-only --book <slug>`.
- Type shows raw dotted string: `pb_type` in `book.yml` missed the
  `text.monograph.` prefix (see `pb_sync.py` header); fix yml, re-run.
