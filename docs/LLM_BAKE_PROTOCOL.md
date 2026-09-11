# Scientific bake protocol — Fathers LLM lane

**Goal:** Pick a default draft engine contributors can use without burning paid Cursor tokens. Prefer free/cheap cloud. Escalate to Air/Mini LoRA only if cloud fails.

**Date started:** 2026-09-11  
**Fixture:** Origen Jeremiah Homily 6 §6.1 locked Greek (`jeremiah_source.json`)  
**Null hypothesis H0:** No free/cheap cloud model produces SOP-shaped Pass A ≠ Pass B English from locked Greek alone.  
**Alt H1:** ≥1 Cloudflare Tier A (or NVIDIA Free Endpoint) model passes the structural SOP scorer on the fixture.  
**H2 (quality):** Passing models remain plausible on a second held-out section (§6.2) without ANF smell / locus-only titles.

## Controlled variables

- Same system + user prompt for every model (`scripts/llm_bakeoff.py`)
- Temperature 0
- Same max_tokens budget
- Automatic checks only (no human “vibes” in the pass/fail gate)

## Dependent measures (must all be true to PASS)

1. Valid JSON parse  
2. `section == "6.1"` (or target)  
3. Thought title (not locus-only)  
4. `pass_a_gloss` length ≥ 40  
5. `english[]` non-empty, joined length ≥ 40  
6. Pass A ≠ Pass B  
7. No crude ANF/archaic smell (`thou/thee/hast/…`)  
8. No markdown fence leak  

## Lanes

| Lane | Status |
|------|--------|
| Cloudflare Workers AI Tier A | Run with `CLOUDFLARE_API_TOKEN` |
| NVIDIA build.nvidia.com Free Endpoint | Requires `NVIDIA_API_KEY` (not present 2026-09-11 start) |
| Local Ollama | Optional `--ollama` if daemon up |

## Decision rule

1. If ≥1 cheap CF model PASSes on §6.1 **and** §6.2 → **default contributor draft engine** = that model (cheapest among passers). Document in START_HERE + contribute page.  
2. If only expensive CF (70B) passes → use it as **oracle checker** only; keep hunting cheaper / NVIDIA.  
3. If all CF fail → run NVIDIA when keyed; if still fail → Air LoRA plan.  
4. Never leave work in a human `review` queue; promote with `scripts/ai_promote.py` (two checkers) → `done`.

## Receipts

`outputs/llm-bakeoff/<stamp>/summary.json` + `VERDICT.md`
