# LLM API setup notes (read before calling models)

**Canonical SOP (all projects):** `~/SaneApps/infra/SaneProcess/docs/LLM_VENDOR_API_SOP.md`  
**Research gate:** `ruby ~/SaneApps/infra/SaneProcess/scripts/llm_api_research_gate.rb --provider cf|nvidia --model '<id>'`  
**Shell hook:** `sane_llm_api_guard.rb` blocks ad-hoc CF/NVIDIA inference without a receipt.

**Rule:** for every model family, read the vendor model card + live infer schema **before** baking. Blind defaults caused empty/`null`/hang failures on 2026-09-11. Prefer “our call shape is wrong” over “API is broken” — millions use these endpoints.

Sources checked 2026-09-11:

- Nemotron Super infer: https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b-infer  
- DeepSeek V4 Flash infer: https://docs.api.nvidia.com/nim/reference/deepseek-ai-deepseek-v4-flash-0731-infer  
- CF OpenAI-compat: https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/  
- CF Gemma / GLM / gpt-oss model pages + **live** `GET …/ai/models/schema?model=`  
- Community: [OpenCode #24264](https://github.com/anomalyco/opencode/issues/24264) (DeepSeek hang without correct kwargs); [NVIDIA forum hang/404](https://forums.developer.nvidia.com/t/newer-nim-models-kimi-k2-6-deepseek-v4-pro-hang-indefinitely-or-404-possible-missing-public-api-endpoints-permission/377777)

## Proven call-shape fixes (this account, 2026-09-11)

| Symptom we saw | Actual cause | Fix that worked |
|----------------|--------------|-----------------|
| CF GLM / Gemma `null` / reasoning prose / “empty” | Live schema: `chat_template_kwargs.enable_thinking` **defaults true** | Send `enable_thinking: false` for JSON drafts; Gemma prefer `max_completion_tokens` |
| CF gpt-oss “null” earlier | Wrong profile (invented thinking kwargs / low token budget / bad parse) | Plain `/ai/run` with `max_tokens≥2k`, `temperature: 0.6` (schema default). Smoke returns `{"ok":true}` |
| NVIDIA DeepSeek hang / client timeout | **Non-stream** chat completions hang; stream with `reasoning_effort: "none"` returns in ~0.3s | Always `stream: true` + `reasoning_effort: "none"`. Do **not** also send `chat_template_kwargs.enable_thinking: false` (that combo hung in probe) |
| NVIDIA Super empty / hang | Thinking left on / client timeout 60s / temp 0 | `reasoning_effort: "none"`, temp 1.0, top_p 0.95, client timeout ≥180s |
| mistral-nemotron “FAIL” | Markdown ``` fences around valid JSON; scorer treated wrapper as fail | Strip fences in `extract_json`; score fence leak on **parsed fields**, not raw wrapper |
| Catalog ID → HTTP 404 Function not found | Account entitlement (“Public API Endpoints”) — common free-tier pattern | Probe each ID; only bake models that smoke. Not a code bug once smoke is green |

## NVIDIA NIM (`NV_API_KEY` → `https://integrate.api.nvidia.com/v1/chat/completions`)

| Model | Required for structured JSON drafts | Do not |
|-------|--------------------------------------|--------|
| `nvidia/nemotron-3-super-120b-a12b` | `reasoning_effort: "none"`. Card: temp **1.0**, top_p **0.95**, large `max_tokens`. Fixture PASS with ≥180s timeout. | `temperature: 0` alone; 60s client timeout |
| `deepseek-ai/deepseek-v4-flash-0731` | Official: `reasoning_effort` defaults **high**; use **`none`**. **Must `stream: true`** on this free NIM path — non-stream hung 45–90s in every probe. | Non-stream; `chat_template_kwargs` false on top of `none` (hung); unbounded waits without stream |
| `mistralai/mistral-nemotron` | Standard chat; smoke OK; strip markdown fences | Assume every catalog ID is enabled |
| `nvidia/nemotron-3.5-lightning-*` | Still timing out here after probes | Unbounded waits |

## Cloudflare Workers AI

| Model | Setup | Failure mode we hit |
|-------|--------|---------------------|
| `@cf/meta/llama-3.*` | Plain `messages` + `max_tokens` | — |
| `@cf/qwen/qwen3-30b-a3b-fp8` | Plain messages; robust JSON extract | Malformed JSON until extractor fixed |
| `@cf/zai-org/glm-4.7-flash` | `chat_template_kwargs.enable_thinking: false` | `null` with thinking on → **PASS** once off |
| `@cf/google/gemma-4-26b-a4b-it` | Same: thinking **defaults true**. With thinking on, `response` is reasoning prose (looks “wrong”). With off + `max_completion_tokens`: smoke `{"ok":true}` | First bake “empty” / unusable JSON |
| `@cf/openai/gpt-oss-20b` | Schema default `max_tokens: 256`, `temperature: 0.6`. Prefer `/ai/run` or `/ai/v1/chat/completions`. Responses API returns reasoning objects — extract text carefully. | Invented `enable_thinking` / temp 0 |

JSON Mode (`response_format`) is **not** universal on CF. Do not assume Qwen/GLM/Gemma support it.

## Bake harness (`scripts/llm_bakeoff.py`)

Profiles wired in code:

- CF Gemma/GLM → thinking off  
- CF gpt-oss → temp 0.6, max_tokens 4096, no fake thinking kwargs  
- NV DeepSeek → **stream + reasoning_effort none**  
- NV Super → reasoning_effort none, long timeout  

**Gate:** never multi-model bake until each profile has a smoke `{"ok":true}` with hard client timeout.
