# AI cross-check → done (no human review gate)

**Owner ruling 2026-09-11:** There is no standing human Greek/Latin reviewer. A human `review` queue would only backlog work. Finished text ships when **independent models** agree, not when a person who cannot read the source rubber-stamps it.

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
3. **Checker model A** (different family from draft): given locked Greek + Pass A + Pass B, returns a verdict JSON (`pass` / `fail` + reasons). Must not be the same model id as the draft.  
   Default: `@cf/google/gemma-4-26b-a4b-it` (Llama 8B is too noisy as a hard gate — false fails and false ANF flags). Boolean flags alone are soft; unexplained `grounded_in_greek: false` still fails closed; ANF smell is verified locally.
4. **Checker model B** (second independent check): same prompt shape.  
   Default: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (oracle). NVIDIA `nvidia/nemotron-3-super-120b-a12b` is an alternate when CF is rate-limited (researched kwargs only).
5. **Promote** only if structural PASS and **both** checkers PASS. Write receipt under `outputs/ai-promote/<stamp>/` and set claim → `done`. Set justification `reviewer` to `ai-crosscheck:<modelA>+<modelB>`.

If either checker fails: keep `claimed` (or set `checking`→`claimed`), apply the checker’s concrete fixes, re-run. Do not “majority vote” a fail away.

## Checker config + fallbacks

Canonical file: `docs/LLM_LANE_CONFIG.json` (flag: `--config` / `--lane cf|nv`).

- Each lane has **draft** + **checker_a** + **checker_b** ordered lists.
- On **API** errors (410 EOL, 404, 5xx, timeout): try the next model in that chain.
- On **content** fail: stop that chain (do not shop for a softer model). Overnight leaves the claim `claimed` and moves on.
- Promote exit codes: `0` done, `1` content fail, `2` API fallbacks exhausted, `3` lock busy, `4` claim wall timeout (`claim_wall_s`; leave claimed — not success).
- Mini LaunchAgent is **calendar-only** (daily 21:10 local). No KeepAlive — reinstall/bootstrap used to restart mid-promote and stack duplicates. Optional wrapper fuse: `SANE_FATHERS_MAX_KEEPALIVE` (default 3) if KeepAlive is ever re-enabled.
- **Concurrency:** kernel `fcntl.flock` on `outputs/fathers-overnight/locks/global-burn.lock` (one burn session) + per-claim `claim-*.lock`. Wrapper holds the global flock via a helper process for the whole burn. Overnight sets `SANE_FATHERS_NESTED=1` so CF+NV can promote different claims in parallel; a second overnight/manual promote exits `3` (lock busy) / wrapper exits `0`. Per-claim wall exits `4`; overnight job wall (`overnight_wall_s`) exits `0` (soft stop on the main thread — in-flight promotes finish under their own `claim_wall_s`).
- Recover stuck `claimed` rows with `run-overnight-quota.sh` **only when idle** (no `ai_promote` / no held flock). Do not `bootout`/`kickstart` while a burn is live.

**Cloudflare** free **10k neurons/day** (UTC) + **NVIDIA** free NIM (RPM/latency) run **in parallel** on different claims.

Canonical overnight host: **Mac Mini** (always on). Air orchestrates; Mini holds the live `CLAIMS.md` burn. After a Mini run, sync `docs/CLAIMS.md` + Jeremiah english/justifications back to Air before editing claims locally.

```bash
# On Mini (LaunchAgent does this daily 21:10 local):
source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
python3 scripts/overnight_quota.py --lanes both --agent overnight-mini
```

Install / refresh agent: `bash scripts/install-mini-overnight-quota.sh`  
Wrapper: `scripts/run-overnight-quota.sh` (kernel flock single-instance; calendar agent; resumes stuck `claimed` rows).

Stops CF lane near the free reserve. NVIDIA lane keeps going until max-claims / queue empty. Does not Logos-compile or deploy the site.

## What checkers must verify

- English is grounded in the locked Greek (no imported ANF/FOTC sense).
- Pass B does not add ideas absent from Pass A.
- Thought title names the idea, not a locus label.
- OCR/lacuna notes are honest where Greek is broken.

Checkers are still models — they can be wrong together. Corrections on the site are the long-term safety valve.

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
