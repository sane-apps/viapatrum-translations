# Logos Personal Book — SOP

Distilled from the Julian of Eclanum production run (Codex → Cursor, 2026-09-09). Follow this for every new book. Do not invent a parallel process.

## Audiobook voice rule (owner, 2026-10-09)

Owner's words: "each work should have one voice. It does NOT matter if each separate work has a different voice. internal consistency per book makes sense. Tying ourselves to one voice for the entire website makes no sense. whatever voice is best, fastest, cheapest etc."

- **One narrator voice per work.** Every section, chapter and part of a work (site read-along audio, downloadable audiobook, YouTube read-along) uses the same narrator voice from start to finish. Never mix narrators inside one work.
- **Different works may use different voices.** That is fine and expected.
- **Never require one site-wide voice.** Do not re-voice a finished, internally consistent work just to match other works or a newer default.
- **Choose per work, in this order:** best quality, then fastest, then cheapest. Candidates include Muse (prepaid through Nov 2, 2026; runs only in the Mini's logged-in GUI session), Cloudflare Workers AI Aura-2, and local Kokoro.
- **Record the choice.** The chosen voice is written into the work's audio metadata (`outputs/audio/<work>/manifest.json` → `"voice"`, and every passage's `"voice"`). Re-runs, fixes and new sections read that recorded voice and reuse it; they do not fall back to the current global default.
- If a fix needs a voice the work does not use (for example its engine is gone), re-voice that whole work in one new voice; never patch it in a second voice.
- The separate Scripture-quotation voice (`CF_TTS_QUOTE_VOICE`, decided 2026-10-07) predates this rule; Owner confirmed 2026-10-09: keep the separate Scripture-quotation voice; each work uses one narrator voice plus one quote voice, both consistent throughout that work.
- **Defaults for new works:** Cloudflare Aura-2 `arcas` narrates and Aura-2 `mars` reads the Scripture quotations (chosen by the owner 2026-10-09; Muse rejected as too manual). Recorded works keep their own voices; the defaults never re-voice anything.
- This supersedes any earlier "one voice for the whole site/corpus" or "re-voice every work into the current voice" wording (2026-10-07 VISION A.3, GPU_RENDER_COSTS "breaks corpus consistency").

## Phases

### 0. Charter

Write in `books/<slug>/SESSION_HANDOFF.md`:

- Title, author, resource type (usually Monograph), language (English).
- Scope: what survives, what is out of scope, what is lost.
- Legal: private study; new English from allowed source text; no modern copyrighted English copy; no public publish unless owner asks.
- Source URLs / editions and local paths.

### 1. Sources (many witnesses)

Lock the exact permitted copy-text and compare every additional witness actually used. Identify the work, author, printed page/locus and surviving scope against the raw print or document before translating. A second scan of the same edition checks OCR; it is not an independent textual witness. Record which comparisons were done and disagreements in `variants[]`. Do not invent missing witnesses or call generated source JSON a source lock.

**Reader disclosure:** the public work page’s collapsed “About this text” names the copy-text, the other prints checked, and every stretch supplied from another witness (`text_history` in `*_meta.json` or the site pack). The reading column stays clean. A one-line italic cue is used only when a whole stretch is supplied from another witness (for example a homily that survives only in Jerome’s Latin). Do not call the result a manuscript. Do not claim a combination that was not actually done. Agent receipts (`variants[]`, Pass A) stay off the page.

For each work, try in this order (skip what does not exist or is still in copyright):

1. Best PD critical edition (GCS, Pusey, Scherer/Witte, Klostermann).
2. A second scan or transcription of that same edition (PDF + OCR/TEI).
3. An earlier PD print (Migne PG/PL, Delarue, Huet, Ghislerius).
4. Ancient versions of the *same* work (Jerome/Rufinus Latin of Origen, Syriac, etc.).
5. Catena / fragment collections that preserve extra lines.
6. A second library scan when the first OCR is damaged.

Do **not** lock copyrighted critical editions or modern facing-page English as copy-text (SC, FOTC, Reuss 1957, etc.). Those may be edition-history notes only.

- Fetch and retain raw HTML/PDF/XML under `sources/`.
- `sources/manifest.json` lists every witness: edition, language, role (`copy-text` | `check` | `version` | `fragments`), URL, SHA256, local path.
- Speaker-split carefully (Julian vs Augustine vs quoted authorities). Prefer full-name speaker labels at paragraph start only when the site uses them that way.
- Keep raw HTML even when a parser cleans JSON — audits need the witness.
- Output structured Latin/source JSON that translation records can cite by location. Name which witness each section was read from. Declare expected section IDs from the edition and preserve every source paragraph. A matching chapter number does not authorize a short tip slice to replace the whole chapter.

### 2. Translate (two passes)

Full bar: `books/ante-nicene-topics/docs/TRANSLATION_QA.md`.

- **Pass A:** literal sense gloss + key lemmas from the locked source block only.
- **Pass B:** reading English in the author’s voice; no concept that is not in A.
- One JSON file (or one per book/witness) under `translations/` matching `docs/SCHEMAS.md`.
- English paragraphs only in `english[]` (this is Pass B). No Latin in the reading text.
- Justification receipt required: `reviews/justifications/<id>.json` with `pass_a_gloss` ≠ joined Pass B.
- Use `kind` / `translator_notes` / `added_allusions` for editorial material.
- **Inline scripture refs (hard gate):** whenever the Father quotes or clearly alludes to Scripture, Pass B `english[]` must carry a parenthetical citation beside the clause (full book name + chapter:verse, Julian pattern). `added_allusions` / justification `bible_refs` alone do **not** pass — readers and Logos PBB both need the ref in the reading text. See `docs/LOGOS_MARKUP.md` and Project store `docs/scripture-refs-inline.md`.
- Forbid placeholders: no `TODO`, `YYYY`, or raw `[n12]` footnote junk in English.

### 3. Review

- Check all records structurally: nonempty source/English, no scaffold or operational prose, distinct Pass A/Pass B, exact declared section coverage and current file hashes. These checks cannot certify meaning.
- Compare first/last plus seeded and risk-selected passages against actual raw source pages. Record the sampled scope. Prioritize negation, agency, modality, doctrinal terms, quotations, lacunae and suspiciously short output.
- Every new or changed published passage needs a source-backed semantic review of **every clause** in that passage. Approving five sampled passages does not approve the rest of a work.
- Review author/work/locus identity, completeness, negation, agency, modality, doctrine and Scripture explicitly. Each source paragraph needs a coverage entry and concrete evidence notes. Uncertainty or missing evidence blocks approval; never prefer pass when unsure.
- Scripture wording controls the target, not a shifted footnote list. Verify each explicit quotation and clear allusion. Distinguish Hebrew/modern and LXX/Vulgate Psalm numbering; label possible allusions as uncertain. Record corrections in the existing scripture review.
- Source audit for fragments must distinguish the author's words, the opponent's reply and indirect reports. Preserve lacunae and lost material; no invented connective argument.
- Bind review to exact author/work identity, source/English files, raw witnesses and scope. Any source, English, attribution or scope edit invalidates affected review. Do not copy old reviewer stamps forward.
- Use `pipeline.verify_translation_qa` to create and validate packets; `pipeline.check_pass_ab` checks justifications. `ai_promote.py` handles supported independent-model promotion. No standing human approval queue is required; the reviewing agent/model still must inspect the actual source.
- The website consumer independently checks evidence. A claim marked `done`, two model names, a nonempty file or `source_verified` alone is insufficient. The site's provisional legacy hash baseline is not certification and must never be refreshed to bypass review.
- Preserve held files. Repair one source/translation family at a time and review changes before release. Never expand the catalogue to meet a volume target.

Example packet generation (run on Mini; use actual paths):

```bash
python3 -m pipeline.verify_translation_qa --english <english.json> --source <source.json> \
  --raw-source <edition.pdf> --identity <identity.json> --expected-sections <section-ids.json> \
  --seed 20260913 --sample-size 5 --packet-out <packet.json>
```

Generation reports structural status only. A current passing receipt is a separate artifact from the review itself; consume it with `--receipt <receipt.json>` or the shared validation API.

### 4. Build DOCX

```bash
cd ~/SaneApps/clients/translations
python3 books/<slug>/build_book.py
python3 -m pipeline.verify_docx books/<slug>/*.docx
# verify_docx also runs pipeline.check_pbb_guards (bans FootnoteStore / Scripture-connection captions in build_book.py)
```

Required in the DOCX:

- Heading styles for TOC (Heading 1–3).
- Clean heading text + **separate** paragraph `[[@Headword:Label]]`.
- Bible links `[[display >> Bible:Book ch:v]]` **inline in the reading text** (see `docs/LOGOS_MARKUP.md`). Clear allusions go beside the clause; do not emit a “Scripture connection:” caption dump.
- Translator notes as **Headword TN marks** (`[[ⁿ >> Headword:TN n]]` + a Translator notes section). **Never Word footnotes** — Logos PBB ignores them and every hover becomes the book description. Do not import `pipeline.footnotes` / `FootnoteStore` in any `build_book.py`.
- Internal bookmarks for section navigation and Scripture index back-links.
- Front matter that discloses scope and AI-assisted private-study status.
- `build_receipt.json` with section counts and bible link receipts.
- `python3 -m pipeline.verify_docx` green (fails on `footnotes.xml`, Scripture-connection dumps, and PBB build-script guards).

### 5. Logos compile + upload (Mini-automated; Air GUI retired 2026-09-23)

The weekly driver does the whole loop — metadata sync, build, upload to
all owner libraries. Full spec: `docs/LOGOS_PIPELINE.md`.

```bash
python3 scripts/logos_build.py --dry-run   # what would build/upload
python3 scripts/logos_build.py --book <slug>  # one book, build + upload
python3 -m pipeline.verify_logos_db --title-substr "<Title fragment>"
```

Manual fallback (only if the driver reports a per-book failure it cannot
clear): open `logos4:PersonalBooks` on the Mini, click the row, check the
body file, click **Build book**, wait for `LastCompiled` to flip, then
click **Upload** and wait for `Upload successful.` Never type metadata
into the GUI — `books/*/book.yml` is the source of truth and
`pb_sync.py --apply` writes it. After any manual fix, record the upload
in `outputs/logos_uploads.json` and re-run the driver.

### 6. Handoff

Update `books/<slug>/SESSION_HANDOFF.md` and repo `SESSION_HANDOFF.md` with LastCompiled, receipt counts, verification evidence, next moves.

## Mini GUI verification path

AX over SSH works on the Mini (proven 2026-09-23): System Events can
enumerate Logos windows and click by button description, and `cliclick`
handles row clicks. Screen capture is NOT needed — verify by outcome:
`LastCompiled` flips in `PersonalBookManager.db` for builds,
`Upload successful.` text for uploads. After every GUI mutation, poll
the AX tree or DB and name what the surface shows.

## Anti-patterns

- Gluing Headword onto the heading run.
- Claiming success from click-return alone.
- Using Cmd+K for Personal Books.
- Rebuilding while the book panel is open.
- Starting a second project folder under Documents.
- Shipping Word footnotes (`FootnoteStore` / `footnotes.xml`) in a Personal Book.
- Dumping `added_allusions` as repeated “Scripture connection:” captions instead of inline Bible links.
- Emitting `logosres:` links that prompt other users’ libraries.

## 2026-09-26 overnight stall fixes (4-critic review + live E2E proof)

Root causes of the daily stall, all proven against receipts before patching:

- Coverage validator flipped honest passes to fail: judges saw one
  [p1] block and invented [1..9]/[1,2]/[1..5]; exact-match then
  rejected the pass AND suppressed the arbiter (no split, no tiebreak).
  Fix: prompt states the exact paragraph count; a pass-shaped but
  malformed verdict gets a bounded same-model retry. Validator unchanged.
- Arbiter chain collapse: draft+revise history saturates qwen+llama, and
  excluding draft+checker families left glm as the sole eligible arbiter;
  one flake then held the claim. Fix: arbiter retries 2->3, a warning
  when fewer than 2 models stay eligible, SOP rule below. Independence
  semantics unchanged.
- gpt-oss-20b was banned from judging but still drafted text (default
  draft/revise fallback) and produced pure confabulation (receipt
  20260926T011739517488Z). Fix: banned from draft_claim + redraft_b
  defaults (DRAFT_FALLBACK_DEFAULTS constants, test-enforced).
- HOLD latch races + crash bug: record_claim_fail is now lock-guarded;
  hold_reconcile keep-path NameError fixed; wrapper auto-runs
  hold_reconcile --apply nightly (fail-closed, never trips the fuse).
- Lane shares normalize over lanes with queued work (fixed total still
  binds); receipts now embed the judged English+Greek snapshot;
  revise prompt verifies notes against the locked text first.

Rules going forward:

- Manual --arbiter chains must span at least 3 model families, or the
  family filter may leave zero eligible judges (silent hold).
- Never re-add gpt-oss-20b to any chain without a new bakeoff receipt.
- Held rows release only with written evidence (claim, receipt refs,
  fixed cause); the claim must still pass full promote. No blanket
  clears.
- After stashing another lane's work to ship, pop the stash before
  deploying (2026-09-26: a ship stash reverted the live Explore
  redesign until restored + reshipped).

## Fathers Watch (self-monitoring, 2026-09-28)

No human should have to poke the system to learn it is broken. Three
scheduled pieces replace the manual watch:

- Mini `com.saneapps.fathers-watch` (every 15 min): runs
  `scripts/fathers_watch.py` — every live `com.saneapps.fathers-*` job's
  exit, lanes, queue progress, certifications, 429s, batch broker (a
  queue older than 30 min with no batch in flight = dead flusher), audio
  drain (`audio:drain`: its log silent over 30 min = two missed 15-min
  runs), narration drift (`audio:drift`, its own id so it never hides a
  stopped drain: sections waiting on sentence drift in drain-status.json
  and sections the last auto ship skipped with "audio does not match the
  page"; it stays open until someone re-reads them), ships (hand-run ship logs, running shelf steps) and the auto
  ship's `state.json` (last run exit, skip, paid shelf, a fresh
  fingerprint of what waits to ship), beliefs (a traceback with no
  FAILED line counts), recert ticks (BUSY lock lines do not count as
  ticks), held review (the newest exit in its log beats launchctl's
  0 or 3; any other launchctl exit, such as 75 busy or a kill, came from
  a newer run that wrote no exit line, so it wins),
  e2e receipt, logos lock, and disk against the one 15 GB floor (warn
  under 15 GB, when ships, builds and e2e skip; fail under 4 GB).
  `watch:gap` is raised once when the previous pass is over 30 min old
  or its lock was left by a dead pass. Writes
  `outputs/fathers-watch/status.json` (alerts carry stable ids +
  first_seen) and appends `alerts.log`. Bounded self-heal only: kill a
  twice-confirmed hung burn child (once per episode), remove a PID-dead
  logos lock older than 30 min. Never touches gates, books, or deploys.
- The watch cannot see its own unload. Two things can: the Air notifier
  below (alert `watch:stale` when status.json is over 30 min old) and
  the Mini nightly report (`infra/SaneProcess/scripts/mini/mini-nightly.sh`,
  08:45, one "Fathers watch" line: loaded, stale or NOT LOADED).
  `python3 scripts/status_site.py --now` prints the one pipeline block
  (live vs built vs waiting, paid shelf, last auto run and skip, git,
  disk, watch age, owner calls from the site handoff).
- Mini `com.saneapps.fathers-e2e` (daily 03:00, after the 02:44 disk
  clean): runs the site `scripts/fathers_e2e.sh` — full
  `ship.sh --dry-run` (build + gates + browser checks, never deploys).
  Holds `outputs/build.lock` (waits up to 60 min); a skip (lock busy,
  ship in flight, disk under 15 GB, another e2e live) exits 75 or 2 and
  never overwrites the last receipt. A red run exits with the dry-run's
  code. Receipt: site `outputs/e2e/LATEST.json` (names the failing gate
  line); full log `outputs/e2e/last-run.log`.
- Air `com.saneapps.fathers-watch-notify` (every 15 min): runs
  `scripts/fathers_watch_notify.py` — fetches Mini status.json over ssh, posts a macOS
  notification ONLY on new alert ids and on recovery. Silent when
  green. `... --status` prints the one-line summary any time. State:
  `~/.local/state/fathers_watch_notified.json`. Until 2026-10-06 the Air
  ran an untracked copy of this file (no `watch:stale`). The repo copy
  with `watch:stale` is the source but, as of 2026-10-06, is untracked on
  the Mini too: commit and push it from the Mini, then on the Air move
  the old untracked file aside and pull. No reload is needed (the Air
  plist already points at that path). Until then a stale watch shows
  only in the 08:45 nightly report and `status_site.py --now`.

Locks and exits (2026-10-06): heavy CPU and disk jobs (site build,
ship, auto ship + paid shelf, e2e, Logos compile, the 02:44 disk clean)
share the site's `outputs/build.lock` through `scripts/ship_lock.py`; a
caller that holds it passes `FATHERS_BUILD_LOCK_HELD=<pid>` so ship.sh
does not wait on it. Network-bound jobs (recert lanes, beliefs, held
review, independent review) do not take it, so lanes keep running
during builds. Every job's own single-instance lock records a pid and a
start time: a lock whose pid is dead is taken over; a live one prints
`BUSY:` and exits 75, so launchctl and the watch see it. The auto ship,
watch and e2e locks live under `outputs/` and survive a reboot, so their
holder also has to still run that script (`ps`) and be younger than the
job's hard limit (auto ship 27300 s, watch 30 min, e2e 7260 s); the lane,
beliefs and held-review locks live in /tmp, which a reboot clears. The auto ship
(`scripts/ship_if_changed.py`) exits 0 done / 1 ship not verified /
2 skipped / 3 paid shelf failed (the next run resumes it) / 75 busy /
143 killed. It refreshes the paid shelf only after a full ship of new
text; an `--audio-only` ship starts no shelf, so new narration reaches
the paid audiobooks with the next text change (open owner call). Nice 10; logs under each repo's `outputs/`. Unload:
`launchctl bootout gui/$(id -u)/<label>` on the owning machine.
