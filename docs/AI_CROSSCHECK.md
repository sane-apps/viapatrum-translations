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
   Default: `@cf/meta/llama-3.1-8b-instruct-fp8-fast`.
4. **Checker model B** (second independent check): same prompt shape.  
   Default: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (oracle) **or**, if CF budget is tight, NVIDIA `nvidia/nemotron-3-super-120b-a12b` with researched kwargs.
5. **Promote** only if structural PASS and **both** checkers PASS. Write receipt under `outputs/ai-promote/<stamp>/` and set claim → `done`. Set justification `reviewer` to `ai-crosscheck:<modelA>+<modelB>`.

If either checker fails: keep `claimed` (or set `checking`→`claimed`), apply the checker’s concrete fixes, re-run. Do not “majority vote” a fail away.

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
