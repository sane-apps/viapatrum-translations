# AI cross-check → done (no human review gate)

**Owner ruling 2026-09-11:** There is no standing human Greek/Latin reviewer. A human `review` queue would only backlog work. Independent model agreement is one review requirement. Publication also requires current source identity, complete declared scope, explicit semantic checks and receipts bound to exact content. A model agreement flag alone never authorizes publication.

Site readers can later **submit a correction** (see `/contribute/#corrections`). That is opt-in quality improvement, not a gate before publish.

## Status flow

`free` → `claimed` → **`done`**

- Optional transient status `checking` while `scripts/ai_promote.py` runs (tools may set this).
- Do **not** leave slices in `review` waiting for a human. Legacy `review` rows should be run through `ai_promote.py` (or re-claimed) until `done`.

## Pipeline (required for `done`)

For every section in the claim:

1. **Draft model** produces Pass A (`pass_a_gloss` + lemmas) + Pass B (`english[]`) + thought title from locked Greek/Latin only.
   Default: `@cf/qwen/qwen3-30b-a3b-fp8` (see `LLM_API_SETUP.md` / shared SOP).
2. **Structural gate** (local, deterministic): parse JSON, section id, thought title, Pass A ≠ Pass B, length floors, no ANF/archaic smell, no fence leak in fields. Same checks as `llm_bakeoff.py` scorer.
3. **Checker model A** (different family from draft): given locked Greek + Pass A + Pass B, returns a verdict JSON (`pass` / `fail` + reasons). Must not share the draft's model family.
   Selection follows configured fallback order, skipping the draft family. Every required semantic flag must explicitly pass with evidence and full source-paragraph coverage; missing, false or uncertain flags fail closed.
4. **Checker model B** (second independent check): same prompt shape; its family must differ from both draft and checker A.
   Default: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (oracle). NVIDIA `nvidia/nemotron-3-super-120b-a12b` is an alternate when CF is rate-limited (researched kwargs only).
5. **Promote** only if structural PASS and **both** checkers PASS. Write receipt under `outputs/ai-promote/<stamp>/` and set claim → `done`. Set justification `reviewer` to `ai-crosscheck:<modelA>+<modelB>`.

If either checker fails: keep `claimed` (or set `checking`→`claimed`), apply the checker’s concrete fixes, re-run. Do not “majority vote” a fail away.

## Content and provenance guard

The canonical draft writer records the actual source block, raw witness SHA256, genuine model-supplied lemmas/choices, Pass B snapshot, draft identity and any print-verified OCR corrections. Missing evidence leaves existing files unchanged. Never invent lexicon citations or decisions to satisfy a schema.

Promotion rejects unsupported book claims before mutation; the current automated bundle loader is Jeremiah-specific. Other books use the shared source-review packet/publication path until a real source adapter exists. All review stamps are tied to current source, English and justification content. Default overnight prep remains prep; it is not a translation approval.

The site additionally verifies current semantic/source receipts for each new or changed passage and its declared work scope. Manual claim-board changes cannot bypass that gate. Review uncertainty requires correction or withholding, not a softer checker or majority vote. The full review protocol is in `docs/SOP.md` §3.

## Checker config + fallbacks

Canonical file: `docs/LLM_LANE_CONFIG.json` (flag: `--config` / `--lane cf|nv`).

The CF checker-A chain starts with the existing Qwen model so each configured draft family has two distinct checker families available in the configuration; overnight prep remains the default.

- Each lane has **draft** + **checker_a** + **checker_b** ordered lists.
- On **API** errors (410 EOL, 404, 5xx, timeout): try the next model in that chain.
- On **content** fail: stop that chain (do not shop for a softer model). Overnight leaves the claim `claimed` and moves on.
- Promote exit codes: `0` done, `1` content fail, `2` API fallbacks exhausted, `3` lock busy, `4` claim wall timeout (`claim_wall_s`; leave claimed — not success).
- Mini LaunchAgent is **always on**. `SANE_FATHERS_FOREVER=1` runs one supervisor: a batch, then the next batch. It waits 10 minutes only when a batch finds nothing to take. Cloudflare still stops at the daily neuron reserve; NVIDIA keeps taking other free slices in that same batch. A fail that only quotes wording already in the reading, or Greek that is not in the locked source, is thrown out and does not park the slice. A real miss gets one repair after the second fail. If that repair fails, the slice stays parked. A scaffold reading (Rem CLOSEOUT or other operational text) is not that kind of fail: it is drafted from the locked source, and a done row that is still a scaffold goes back in the queue four at a time. An arbiter pass does not publish a reading sentence that a dissent quoted when the gloss does not support it. An unreadable model reply (broken JSON or a cut-off chunk) is retried like an API failure and does not spend the repair. A quote already in the reading is not a new omission, and a complaint that changes does not spend the repair. A multi-word lemma gloss whose words are all missing from the reading blocks publish until a revise puts that sense back. A quiet wait updates the heartbeat so the watch does not treat it as a hang.
- Launchd restarts that supervisor only after a crash (`KeepAlive` SuccessfulExit false). KeepAlive-always is still forbidden: bootout used to orphan `ai_promote` and stack a second run. Optional fuse: `SANE_FATHERS_MAX_KEEPALIVE` (default 3) per UTC day, then the supervisor waits instead of exiting.
- **Concurrency:** kernel `fcntl.flock` on `outputs/fathers-overnight/locks/global-burn.lock` (one supervisor) + per-claim `claim-*.lock`. The supervisor holds the global flock for its whole life, including the wait. Overnight sets `SANE_FATHERS_NESTED=1` so CF+NV can promote different claims in parallel. A one-shot `run-overnight-quota.sh` exits 0 when that flock is held. Per-claim wall exits `4`; the batch wall (`overnight_wall_s`, 6h) exits `0` and the supervisor starts the next batch. In-flight promotes finish under their own `claim_wall_s`.
- Do not `bootout`/`kickstart` while a burn is live. The supervisor resumes its own `claimed` rows on the next batch.
- Child draft/promote is bounded by `claim_wall_s` (process-group kill → exit 4). Health: `python3 scripts/fathers_overnight_health.py` (optional `--kill` only if the log has gone silent).

**Cloudflare** free **10k neurons/day** (UTC) + **NVIDIA** free NIM (RPM/latency) run **in parallel** on different claims.

Canonical overnight host: **Mac Mini** (always on). Air orchestrates; Mini holds the live `CLAIMS.md` burn. After a Mini run, sync `docs/CLAIMS.md` + Jeremiah english/justifications back to Air before editing claims locally.

```bash
# On Mini the LaunchAgent supervisor does this continuously:
source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
python3 scripts/overnight_quota.py --lanes both --agent overnight-mini
```

Install / refresh agent: `bash scripts/install-mini-overnight-quota.sh`
Wrapper: `scripts/run-overnight-quota.sh` (kernel flock single-instance; calendar agent; resumes stuck `claimed` rows).

Stops CF lane near the free reserve. NVIDIA lane keeps going until max-claims / queue empty. Does not Logos-compile or deploy the site.

Overnight **default is `--mode prep`**: Pass A gloss, lemmas, OCR flags, scripture guesses. No reading English, no `ai_promote`, claim marked `prepped`. These models are not trusted for Pass B. `--mode translate` is the old draft+promote path and should not be the Mini calendar job.

## Optional Gemini prep / checker-C (never promote alone)

`gemini-3.5-flash-lite` (failover `gemini-3.1-flash-lite` / `gemini-flash-lite-latest`) is an **optional thin prep / checker-C** lane. It writes only under `outputs/gemini-prep/<stamp>/`. It does **not** mark claims, does **not** write live Pass B, and is **never** a sole promote gate.

Enable without changing the CF/NV calendar default:

```bash
source ~/.config/nv/env   # GEMINI_API_KEY
python3 scripts/gemini_prep_lane.py --sections 6.1,7.3
python3 scripts/gemini_prep_lane.py --checker-c --sections 6.1
# Beside overnight CF+NV (still primary):
FATHERS_GEMINI_PREP=1 python3 scripts/overnight_quota.py --lanes both --agent overnight-mini
# or:  … overnight_quota.py --lanes both --enable-gemini
```

Config: `docs/LLM_LANE_CONFIG.json` → `lanes.gemini` (`enabled` defaults **false**). Project note: store `docs/gemini-prep-lane.md`.

## What checkers must verify

- English is grounded in the locked Greek (no imported ANF/FOTC sense).
- Pass B does not add ideas absent from Pass A.
- Thought title names the idea, not a locus label.
- OCR/lacuna notes are honest where Greek is broken.

Checkers are still models — they can be wrong together. Corrections on the site are the long-term safety valve.

## Deterministic review layers

Two machine layers backstop the model judges; both record into the receipt.

- **Clause refutation** (`clause_override`, `unsupported_pass_b_quotes`): a quoted omission already in the reading is thrown out. Quoted Greek that is not in the locked source is thrown out. A garbled beta-code quote that is not in the source is thrown out. A Pass B sentence a dissent quoted, which the gloss does not support and which does not quote its own source Greek, blocks an arbiter pass. Vague notes with no quote are ignored.
- **Scripture grounding** (`grounding_override`): when every failing judgment
  fails only the scripture check, each concrete "missing citation" claim is
  verified by regex against Pass B. Claims naming citations that are present
  (or demanding citations inside the Pass A gloss, where they are not
  required) are refuted and the section promotes. Correctness disputes,
  vague fails, non-scripture fails, and API errors still hold.
- **Jev citation gate** (`jev_cites`, `scripts/jev_cite_check.py`): one TypeSafe
  Choice call per section asks, per Pass B citation, whether the cited verse
  is the true source of the quoted words (supports/contradicts/says_nothing).
  Verdicts are always recorded; only a high-confidence (≥0.9) contradicts on
  a direct (non-`cf.`) citation holds the section. Supports verdicts never
  override a hold, and a Jev hold blocks the grounding override. Missing key
  or API errors degrade to recorded-skipped, never block.
  Calibration 2026-09-25 (`scripts/jev_cite_eval.py --all`,
  `outputs/jev-cite-sweep-20260925.jsonl`): 59,406 judgments, $1.32.
  Swapped-verse negatives 99% contradicts (the 1 miss was a same-book swap
  collision — Jev was right). Filed positives 48% supports; adjudicated
  samples show high-confidence contradicts are ~95% genuine filed errors
  (near-miss pattern: right neighborhood, wrong chapter/verse) and
  high-confidence supports ~80-90% right. `cf.` cites stay advisory.

## Commands

```bash
# After English + justifications exist for the claim’s sections:
python3 scripts/ai_promote.py --claim jer-h6 --agent overnight

# Draft one section then check (optional combined path):
python3 scripts/ai_promote.py --claim jer-h6 --section 6.1 --draft --agent overnight
```

Vendor API calls must follow `~/SaneApps/infra/SaneProcess/docs/LLM_VENDOR_API_SOP.md` (or use this script / `llm_bakeoff.py`, which are allowlisted).

## Site

- Publish `done` slices on the next Mini site rebuild (owner or scheduled).
- `/contribute/` documents claims + this AI path + how to report a correction.

## 2026-09-25 red-team closeout (85 cyr-isa holds)

Stale-hold release: `python3 scripts/hold_reconcile.py [--apply]` clears HOLD
rows ONLY when the board says done AND the newest receipt is promoted+ok.
Keeps fail history plus clear audit fields. Run after batches; the nightly
path does not auto-clear yet (owner decision, see below).

Catch-up job: `com.saneapps.fathers-overnight-catchup` (RunAtLoad + daily
09:10) execs the standard wrapper ONLY if no dual-lane receipt in ~20h
(`scripts/overnight_catchup.sh`; dry-run via SANE_CATCHUP_DRY_RUN=1).
Install: `scripts/install-mini-overnight-catchup.sh`. Disable: bootout the label.

Env fixes landed: wrapper PATH includes node@24 dir (was: nightly site step
BLOCKED on missing node); publish PATH too. python-docx+lxml installed to
/usr/bin/python3 user site (was: ModuleNotFoundError in docx step). Wrapper
now fails loud (exit 2) on bad env load or bad SANE_TRANSLATIONS_ROOT, warns
when the env file is absent, and sanitizes the fuse counter.

Proven false alarms (no action): burn-then-hold ledger (spend is post-hoc
GraphQL delta; retry path exists), checker hold rates (fail-closed working),
keychain-locked silent empty (exits 2, loud), HELD-poll double burn
(impossible via kernel flock), book_adapter f-string SyntaxError (mixed
quotes, imports clean).

Owner decisions pending (touch gates, NOT implemented): per-night single
record_claim_fail per claim (cross-lane double-fail can latch 0 to held in
one night); lane_share normalization over lanes present in queue (rank1 40%
cap starves while 60% is unspendable); nightly auto-reconcile hook.

## 2026-09-25 batch closeout (81/85 cyr-isa done)

Root cause of the 85: owner-committed tip stubs the night lane skipped
(English present, so no draft) plus stale HOLD rows that never cleared
(5 initially, then ongoing via hold_reconcile). Resolution: draft lane +
promote per claim; verified-marker scripts/mark_verified_done.py replays
stamp+mark for promoted+ok receipts after review_is_current passes
(no model re-burn for unchanged inputs).

PARKED judge-side blocks (content passes, checker/validator does not):
cyr-isa-logos1-rem-early (both checkers pass 7/7 but enumerate paras
[1..9] on a 1-para block; validator demands [1]); book5-part2-rem-early,
rem-mid, rem-close (gemma-only false fails disproven by grep; glm passes).
Do NOT churn text on these; they need a judge-side decision: checker
prompt numbering tolerance, gemma calibration, or arbiter-promote rule.
Book5 trio will auto-retry on the next night run (not latched); the logos
claim is latched held and stays skipped until decided.

2026-09-28: the owner decided this. The judge side refutes a quote that is already in the reading or that is not in the source, and a real miss gets one repair. logos2-open had been marked done on an arbiter pass while a dissent quoted reading sentences the gloss does not support. That slice is reopened for one repair.
