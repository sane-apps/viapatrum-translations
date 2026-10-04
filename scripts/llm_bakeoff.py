#!/usr/bin/env python3
"""Bake-off: Workers AI (+ optional Ollama) on one locked Greek section.

Fixture: Origen Jeremiah §6.1 → Pass A + Pass B JSON. Scores SOP shape, not vibes.

  source ~/.config/nv/env
  export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/llm_bakeoff.py
  python3 scripts/llm_bakeoff.py --models '@cf/qwen/qwen3-30b-a3b-fp8'
  python3 scripts/llm_bakeoff.py --ollama gemma3:4b   # only if ollama is up

Receipts: outputs/llm-bakeoff/<timestamp>/
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys as _sys
_sys.path.insert(0, str(ROOT))
_sys.path.insert(0, str(ROOT / "scripts"))
SOURCE = (
    ROOT
    / "books/origen-jeremiah-samuel/translations/jeremiah_source.json"
)
OUT_ROOT = ROOT / "outputs" / "llm-bakeoff"

# Account used by existing SaneCite Workers AI benches.
DEFAULT_ACCOUNT = "2c267ab06352ba2522114c3081a8c5fa"

TIER_A = [
    "@cf/qwen/qwen3-30b-a3b-fp8",
    "@cf/google/gemma-4-26b-a4b-it",
    "@cf/zai-org/glm-4.7-flash",
    "@cf/openai/gpt-oss-20b",
    "@cf/meta/llama-3.1-8b-instruct-fp8-fast",
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
]

PREP_SYS = """You make a crib of early Christian Greek. You are NOT a literary translator.

You may use ONLY the locked Greek paragraphs given. Do not use ANF, NPNF, FOTC,
web English, or memory of modern translations.

Return ONLY valid JSON (no markdown fences):
{{
  "section": "{section}",
  "pass_a_gloss": "literal English gloss, clause by clause; ugly is fine",
  "lemmas": [{{"form": "form as printed", "lemma": "…", "gloss": "…"}}],
  "ocr_flags": ["garbled word, empty slot, or gap you see"],
  "scripture_guesses": [{{"greek_snip": "quoted Greek", "maybe": "Jer 5:3"}}]
}}

Rules:
- Do NOT write reading English or Pass B.
- Do NOT invent missing Greek. If the print looks gapped, dotted, or junk, put it in ocr_flags.
- At most 8 lemmas, and only load-bearing nouns/verbs. Do not lemma articles, καί, pronouns, or prepositions.
- Use the form as printed even if it looks wrong; note suspicion in ocr_flags.
- Keep pass_a_gloss under ~800 characters. Prefer complete clauses over covering every line.
- scripture_guesses are guesses from quotation shape. Quote the Greek snip. Skip if unsure. Max 4 guesses.
"""


SYS_TMPL = """You translate early Christian Greek into new English for private study.
You may use ONLY the locked Greek paragraphs given. Do not use ANF, NPNF, FOTC,
web English, or memory of modern translations.

Return ONLY valid JSON (no markdown fences) with this shape:
{{
  "section": "{section}",
  "title": "short name of the thought (not a locus like Homily {section})",
  "pass_a_gloss": "literal sense gloss of the whole section",
  "lemmas": [{{"form": "source spelling", "lemma": "dictionary form", "gloss": "sense here"}}],
  "choices": [{{"term": "source expression", "english": "chosen rendering", "why": "specific grammatical or contextual reason", "rejected": ["alternative"]}}],
  "bible_refs": [{{"display": "Full Book chapter:verse", "method": "wording", "note": "quoted source words"}}],
  "variants": [],
  "english": ["Pass B paragraph 1", "Pass B paragraph 2"],
  "translator_notes": ["OCR or uncertainty notes, or empty list"]
}}

Rules:
- pass_a_gloss must NOT equal the joined english paragraphs.
- english is reading prose in the author's voice; no idea absent from pass_a_gloss.
- At most 12 lemmas — pick the load-bearing words only. Supply at least one real translation choice with source term, rendering, and reason; never invent lexicon citations.
- Put each clear Bible quotation/allusion reference beside its clause in english, not only bible_refs. Record uncertainty honestly; do not invent verse numbers.
- Finish every english paragraph with a full sentence (period). Never cut mid-clause.
- Translate every supplied clause and paragraph. Never summarize, omit repetitions, or shorten the source to fit a token budget; an incomplete translation fails review.
- If Greek is broken or gapped, say so in translator_notes; do not invent Greek.
- Skip edition headers (like ΤΟΜΟΣ Β΄ plus number), stray digits standing alone, and
  obvious OCR debris; never translate them as content. Record each skip in translator_notes.
"""


def load_fixture(section: str = "6.1") -> dict:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    matches = [r for r in rows if str(r.get("section")) == section]
    if len(matches) > 1:
        raise SystemExit(f"Duplicate source section {section} in {SOURCE}")
    for row in matches:
        if str(row.get("section")) == section:
            greek = row.get("greek") or []
            if isinstance(greek, str):
                greek = [greek]
            return {
                "section": section,
                "homily": row.get("homily"),
                "klostermann": row.get("klostermann"),
                "greek": greek,
                "ocr_normalizations": row.get("ocr_normalizations") or [],
            }
    raise SystemExit(f"Section {section} not found in {SOURCE}")


def user_prompt(fix: dict) -> str:
    paras = "\n\n".join(f"[p{i+1}]\n{p}" for i, p in enumerate(fix["greek"]))
    chunked = (
        "\nChunked source: the Greek may begin/end mid-sentence or mid-word "
        "(corpus slices, not authorial units). Translate edge fragments "
        "literally as fragments; mark a cut sentence end with a trailing …; "
        "omit untranslatable partial letters at an edge; never complete or "
        "invent the missing words; note each edge cut in translator_notes.\n"
        if fix.get("chunked_source") else ""
    )
    return (
        f"Section {fix['section']} ({fix.get('klostermann') or fix.get('locus') or 'no locus'}).\n"
        f"Locked Greek:\n{paras}\n\n"
        f"Source editor notes: {json.dumps(fix.get('ocr_normalizations') or [], ensure_ascii=False)}\n"
        f"{chunked}"
        "Produce the JSON now."
    )


def extract_json(text: str) -> dict | None:
    text = (text or "").strip()
    if not text or text == "null":
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # strip common reasoning wrappers
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.I).strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _end = dec.raw_decode(text, i)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and (
            "english" in obj or "pass_a_gloss" in obj or "section" in obj
        ):
            return obj
    return None


def score(obj: dict | None, raw: str, section: str = "6.1", source: list[str] | None = None) -> dict:
    checks: dict[str, bool] = {}
    notes: list[str] = []
    if not isinstance(obj, dict) or not obj:
        return {"ok": False, "checks": {"parse_json": False}, "notes": ["no JSON"]}
    checks["parse_json"] = True
    checks["has_section"] = str(obj.get("section", "")) == section
    title = str(obj.get("title") or "").strip()
    checks["thought_title"] = bool(title) and not re.search(
        rf"(?i)^(homily\s*)?§?\s*{re.escape(section)}$|^homily\s*\d+(\.\d+)?$",
        title,
    )
    pa = str(obj.get("pass_a_gloss") or "").strip()
    eng = obj.get("english")
    if not isinstance(eng, list):
        eng = []
    pb = " ".join(str(x) for x in eng).strip()
    checks["has_pass_a"] = len(pa) >= 40
    checks["has_pass_b"] = bool(eng) and all(isinstance(x, str) and x.strip() for x in eng) and len(pb) >= 40
    checks["pass_a_ne_pass_b"] = bool(pa and pb and re.sub(r"\W+", "", pa).casefold() != re.sub(r"\W+", "", pb).casefold())
    checks["lemmas"] = isinstance(obj.get("lemmas"), list) and bool(obj["lemmas"]) and all(
        isinstance(x, dict) and (x.get("form") or x.get("greek") or x.get("lemma")) and x.get("gloss") for x in obj["lemmas"])
    # Same scaffold/ops smells as pipeline.check_pass_ab / fathers catalogue gate.
    try:
        from pipeline.check_pass_ab import content_errors as _content_errors
    except ImportError:  # scripts/ cwd variants
        from check_pass_ab import content_errors as _content_errors  # type: ignore
    placeholder_notes = _content_errors(pa, "pass_a_gloss") + _content_errors(
        eng if eng else "", "english"
    )
    if source is not None:
        placeholder_notes += _content_errors(source, "source", source=True)
    checks["no_placeholders"] = not placeholder_notes
    if placeholder_notes:
        notes.extend(placeholder_notes)
    if source is not None:
        checks["source_present"] = isinstance(source, list) and bool(source) and all(isinstance(x, str) and x.strip() for x in source)
        # Only a gross-omission screen; semantic review must check every source clause.
        source_words = len(" ".join(source).split()) if checks["source_present"] else 0
        checks["not_grossly_abridged"] = source_words > 0 and len(pb.split()) >= source_words * 0.45
    smell = re.search(
        r"(?i)\b(thou|thee|thy|hast|doth|brethren,?\s+beloved|Ante-Nicene)\b",
        pb + " " + pa,
    )
    checks["no_archaic_anf_smell"] = smell is None
    if smell:
        notes.append(f"archaic/ANF smell: {smell.group(0)}")
    # Outer ```json wrappers are common; fail only if fences land inside fields.
    payload = json.dumps(obj, ensure_ascii=False)
    checks["no_fence_leak"] = "```" not in payload
    if "```" in (raw or "") and checks["no_fence_leak"]:
        notes.append("markdown fence wrapper stripped")
    # Truncation: each English para should end like a finished sentence.
    # Required inline citations trail the final period; judge the sentence.
    incomplete = False
    for para in eng:
        t = str(para).rstrip()
        if not t:
            continue
        t = re.sub(r"(\s*\([^()]*\))+$", "", t).rstrip()
        if not t:
            incomplete = True
            notes.append(f"citation-only paragraph: …{str(para)[-48:]}")
            break
        if not re.search(r'[.!?…]["\'»”’)\]]*$', t):
            incomplete = True
            notes.append(f"truncated english: …{t[-48:]}")
            break
    checks["english_complete"] = not incomplete
    ok = all(checks.values())
    return {"ok": ok, "checks": checks, "notes": notes}


TRUNCATED_REASONING = "truncated: reasoning only (thinking used the token budget; no answer)"


def _cf_reasoning_only(result: dict) -> bool:
    """True when the reply has reasoning text but no answer text: a thinking
    model ran out of tokens before it wrote the answer."""
    if not isinstance(result, dict) or result.get("response") or result.get("output_text"):
        return False
    if result.get("choices"):
        msg0 = (result["choices"][0] or {}).get("message") or {}
        return not msg0.get("content") and bool(msg0.get("reasoning_content") or msg0.get("reasoning"))
    if isinstance(result.get("output"), list):
        items = [i for i in result["output"] if isinstance(i, dict)]
        has_reason = any(i.get("type") == "reasoning" for i in items)
        has_answer = any(isinstance(b, dict) and b.get("text") for i in items if i.get("type") != "reasoning"
                         for b in i.get("content") or [])
        return has_reason and not has_answer
    return False


def _cf_pick_content(result: dict) -> str | None:
    """Normalize Workers AI result shapes (legacy response + chat choices).
    Answer text only: reasoning text is never returned as the answer (a
    truncated thinking reply gave half-thoughts that parsed as JSON,
    2026-10-03). None when there is no answer; see _cf_reasoning_only."""
    if not isinstance(result, dict):
        return None
    content = result.get("response")
    if content is None and result.get("choices"):
        msg0 = result["choices"][0].get("message") or {}
        content = msg0.get("content") or None
    if content is None and result.get("output_text"):
        content = result.get("output_text")
    if content is None and isinstance(result.get("output"), list):
        # Responses API-ish: join answer text chunks once each; skip reasoning items
        parts = []
        for item in result["output"]:
            if not isinstance(item, dict) or item.get("type") == "reasoning":
                continue
            for block in item.get("content") or []:
                if isinstance(block, dict) and block.get("text"):
                    parts.append(block["text"])
        content = "\n".join(parts) if parts else None
    if content is None:
        return None
    if not isinstance(content, str):
        return json.dumps(content)
    return content


# ---------------------------------------------------------------- batch route
# Batch-capable Workers AI models (catalog property async_queue, 2026-10-03)
# go through the local batch broker (scripts/cf_batch_broker.py), which turns
# many calls into a few ?queueRequest=true batches under the per-model caps.
# CF_BATCH=0 forces direct calls. If the broker is down, calls go direct.
BATCH_MODELS = ("kimi-k2.6", "gpt-oss-120b", "gpt-oss-20b", "qwen3.8-27b", "gemma-4-26b", "deepseek-v4-flash",
                "llama-3.3-70b", "qwen3-30b-a3b", "llama-4-scout")
BROKER = "http://127.0.0.1:" + os.environ.get("CF_BATCH_PORT", "8799")
import threading as _threading
_use_batch = _threading.local()  # per-thread flag: vendor_call sets it when the model is at its cap
_broker_seen = {"t": 0.0, "up": False, "stats": {}}
# A model whose oldest pending batch is older than this is stuck at Cloudflare
# (2026-10-04: Kimi K2.6 batches stopped completing; every overflow call waited
# the broker's full 25-min deadline, then failed). Its calls go direct instead.
BATCH_STUCK_S = float(os.environ.get("CF_BATCH_STUCK_S", "600"))


def _broker_up() -> bool:
    if time.time() - _broker_seen["t"] < 30:
        return _broker_seen["up"]
    try:
        with urllib.request.urlopen(BROKER + "/stats", timeout=2) as r:
            up = r.status == 200
            stats = json.loads(r.read() or b"{}") if up else {}
    except Exception:  # noqa: BLE001
        up, stats = False, {}
    _broker_seen.update(t=time.time(), up=up, stats=stats)
    return up


def _batch_stuck(model: str) -> bool:
    m = (_broker_seen.get("stats") or {}).get("models", {}).get(model) or {}
    return (m.get("oldest_pending_s") or 0) > BATCH_STUCK_S


def batch_route(model: str, api: str = "run") -> bool:
    return (api == "run" and os.environ.get("CF_BATCH", "1") != "0"
            and any(k in model for k in BATCH_MODELS) and _broker_up() and not _batch_stuck(model))


def _broker_run(model: str, payload: dict) -> dict:
    req = urllib.request.Request(BROKER + "/run", data=json.dumps({"model": model, "payload": payload}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=1700) as r:
        return json.loads(r.read() or b"{}")


def cf_call(
    model: str,
    messages: list,
    token: str,
    account: str,
    max_tokens: int = 1800,
    *,
    temperature: float = 0.0,
    enable_thinking: bool | None = None,
    use_max_completion_tokens: bool = False,
    api: str = "run",
    reasoning_effort: str | None = None,
    timeout: int = 120,
) -> dict:
    """Workers AI call. See docs/LLM_API_SETUP.md — Gemma/GLM thinking defaults ON."""
    if api == "chat":
        url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1/chat/completions"
        payload: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    else:
        url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"
        payload = {
            "messages": messages,
            "temperature": temperature,
        }
        if use_max_completion_tokens:
            payload["max_completion_tokens"] = max_tokens
        else:
            payload["max_tokens"] = max_tokens
    # Gemma/GLM: enable_thinking defaults true — burns budget into reasoning prose
    if enable_thinking is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    # Kimi K2.6 ignores enable_thinking=false; its switch is reasoning_effort "none".
    if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort
    if getattr(_use_batch, "on", False) and batch_route(model, api):
        _use_batch.on = False
        t0 = time.time()
        try:
            out = _broker_run(model, payload)
        except Exception as e:  # noqa: BLE001
            out = {"error": f"broker: {e}"}
        if out.get("result") is not None:
            result = out["result"]
            content = _cf_pick_content(result)
            if content is not None:
                usage = result.get("usage") or {}
                return {"content": content, "ms": int((time.time() - t0) * 1000), "batched": True,
                        "pt": usage.get("prompt_tokens") or 0, "ct": usage.get("completion_tokens") or 0,
                        "neurons": usage.get("neurons") or 0}
            if _cf_reasoning_only(result):
                return {"error": TRUNCATED_REASONING, "ms": int((time.time() - t0) * 1000), "batched": True}
        rate_acquire(model)  # broker failed: fall back to a paced direct call
    body = json.dumps(payload).encode()
    last_err = None
    for attempt in range(3):
        t0 = time.time()
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            ms = int((time.time() - t0) * 1000)
            # OpenAI-compat path returns choices at top level (no success wrapper)
            if api == "chat" and data.get("choices"):
                content = _cf_pick_content({"choices": data["choices"]})
                if not content:
                    if _cf_reasoning_only({"choices": data["choices"]}):
                        return {"error": TRUNCATED_REASONING, "ms": ms}
                    return {"error": f"empty chat result: {json.dumps(data)[:200]}", "ms": ms}
                usage = data.get("usage") or {}
                return {
                    "content": content,
                    "ms": ms,
                    "pt": usage.get("prompt_tokens") or 0,
                    "ct": usage.get("completion_tokens") or 0,
                    "neurons": usage.get("neurons") or 0,
                }
            if not data.get("success"):
                # Rate / capacity errors go straight back (no internal retry):
                # vendor_call lowers the model's allowance on a 429 and the
                # caller backs off (efficiency sweep 2026-10-03).
                msg = json.dumps(data.get("errors") or data)[:240]
                return {"error": msg, "ms": ms}
            result = data.get("result") or {}
            content = _cf_pick_content(result)
            if content is None:
                if _cf_reasoning_only(result):
                    return {"error": TRUNCATED_REASONING, "ms": ms}
                return {"error": f"empty result: {json.dumps(result)[:200]}", "ms": ms}
            usage = result.get("usage") or {}
            return {
                "content": content,
                "ms": ms,
                "pt": usage.get("prompt_tokens") or 0,
                "ct": usage.get("completion_tokens") or 0,
                "neurons": usage.get("neurons") or 0,
            }
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    detail = e.read().decode(errors="replace")[:200]
                except Exception:  # noqa: BLE001
                    detail = ""
                return {"error": f"HTTP 429 rate limited: {detail}", "ms": int((time.time() - t0) * 1000)}
            last_err = e
            time.sleep(1.0 * (attempt + 1))
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    return {"error": f"fetch failed: {last_err}", "ms": 0}


def _nvidia_read_sse(resp, deadline_s: float) -> tuple[str, dict]:
    """Accumulate SSE content (+ reasoning_content fallback). Returns (text, last_usage)."""
    chunks: list[str] = []
    reasoning: list[str] = []
    usage: dict = {}
    sock = None
    try:
        sock = resp.fp.raw._sock  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        sock = None
    while True:
        remain = deadline_s - time.time()
        if remain <= 0:
            break
        if sock is not None:
            try:
                sock.settimeout(max(1.0, remain))
            except OSError:
                pass
        try:
            line = resp.readline()
        except OSError:
            break
        if not line:
            break
        s = line.decode(errors="replace").strip()
        if not s or not s.startswith("data: "):
            continue
        data = s[6:]
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        if obj.get("usage"):
            usage = obj["usage"]
        choices = obj.get("choices") or []
        if not choices:
            continue
        delta = choices[0].get("delta") or {}
        if delta.get("content"):
            chunks.append(delta["content"])
        if delta.get("reasoning_content"):
            reasoning.append(delta["reasoning_content"])
        # some NIMs put full message on final chunk
        msg = choices[0].get("message") or {}
        if msg.get("content") and not chunks:
            chunks.append(msg["content"])
    text = "".join(chunks) or "".join(reasoning)
    return text, usage


def nvidia_call(
    model: str,
    messages: list,
    token: str,
    max_tokens: int = 4096,
    *,
    temperature: float = 1.0,
    top_p: float = 0.95,
    reasoning_effort: str | None = "none",
    chat_template_kwargs: dict | None = None,
    stream: bool | None = None,
) -> dict:
    """NIM OpenAI-compatible chat.

    DeepSeek V4 Flash: non-stream often hangs on free NIM; use stream=True +
    reasoning_effort='none' (proven 2026-09-11; see docs/LLM_API_SETUP.md).
    """
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    if stream is None:
        stream = "deepseek" in model.lower()
    payload: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": stream,
    }
    if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort
    if chat_template_kwargs is not None:
        payload["chat_template_kwargs"] = chat_template_kwargs
    body = json.dumps(payload).encode()
    accept = "text/event-stream" if stream else "application/json"
    last_err = None
    for attempt in range(2):
        t0 = time.time()
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": accept,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                if stream:
                    text, usage = _nvidia_read_sse(resp, time.time() + 170)
                    ms = int((time.time() - t0) * 1000)
                    if not text:
                        return {"error": "empty SSE stream", "ms": ms}
                    return {
                        "content": text,
                        "ms": ms,
                        "pt": usage.get("prompt_tokens") or 0,
                        "ct": usage.get("completion_tokens") or 0,
                        "stream": True,
                    }
                data = json.loads(resp.read().decode())
            ms = int((time.time() - t0) * 1000)
            if data.get("error"):
                err = data["error"]
                msg = json.dumps(err)[:240] if not isinstance(err, str) else err[:240]
                code = err.get("code") if isinstance(err, dict) else None
                if code in (503, "503") and attempt < 1:
                    time.sleep(3.0)
                    continue
                return {"error": msg, "ms": ms}
            if data.get("status") and data.get("detail"):
                return {"error": f"{data.get('status')}: {data.get('detail')}"[:240], "ms": ms}
            choices = data.get("choices") or []
            content = ""
            if choices:
                msg = choices[0].get("message") or {}
                content = msg.get("content") or ""
                if not content:
                    content = msg.get("reasoning_content") or ""
            if not content:
                return {"error": f"empty message: {json.dumps(data)[:200]}", "ms": ms}
            usage = data.get("usage") or {}
            return {
                "content": content,
                "ms": ms,
                "pt": usage.get("prompt_tokens") or 0,
                "ct": usage.get("completion_tokens") or 0,
            }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors="replace")[:240]
            ms = int((time.time() - t0) * 1000)
            if e.code == 503 and attempt < 1:
                time.sleep(3.0)
                last_err = f"HTTP {e.code}: {err_body}"
                continue
            return {"error": f"HTTP {e.code}: {err_body}", "ms": ms}
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < 1 and "timed out" in str(e).lower():
                time.sleep(2.0)
                continue
            time.sleep(1.0)
    return {"error": f"fetch failed: {last_err}", "ms": 0}


def ollama_call(model: str, messages: list, host: str = "http://127.0.0.1:11434") -> dict:
    url = f"{host}/api/chat"
    body = json.dumps(
        {"model": model, "messages": messages, "stream": False, "options": {"temperature": 0}}
    ).encode()
    t0 = time.time()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read().decode())
        ms = int((time.time() - t0) * 1000)
        content = (data.get("message") or {}).get("content") or ""
        return {"content": content, "ms": ms, "pt": 0, "ct": 0}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "ms": int((time.time() - t0) * 1000)}


def is_nvidia_model(model: str) -> bool:
    """True for NIM ids (not Workers AI @cf/…)."""
    m = (model or "").strip()
    if not m or m.startswith("@cf/"):
        return False
    if m.startswith("nvidia:"):
        return True
    # org/model NIM shape
    return "/" in m


def normalize_model(model: str) -> str:
    m = (model or "").strip()
    if m.startswith("nvidia:"):
        return m[len("nvidia:") :]
    return m


# ---------------------------------------------------------------- rate limits
# One slot ledger per model in /tmp/vendor-rate/<model>.json, shared by every
# process (lanes, grading, intake) through an flock. A call waits for a free
# slot instead of drawing a 429. Limits start from Cloudflare's published
# numbers and adapt: a 429 cuts that model's allowance by a quarter for 10
# minutes; a clean 10 minutes lets it climb back toward the ceiling.
RATE_DIR = Path("/tmp/vendor-rate")
RATE_CEILING = {  # requests per minute, per account, per model
    "default": 280,          # Workers AI text generation default is 300/min
    "paid": 18,              # paid-access models: 20/min (50 with prepaid AI Gateway credits)
    "nvidia": 35,            # NIM free-tier pacing
}
PAID_ACCESS = ("glm-5", "kimi-k2", "deepseek-v4", "qwen3.8")


def _rate_class(model: str) -> str:
    if is_nvidia_model(model):
        return "nvidia"
    return "paid" if any(k in model for k in PAID_ACCESS) else "default"


def _rate_file(model: str) -> Path:
    RATE_DIR.mkdir(exist_ok=True)
    return RATE_DIR / (re.sub(r"[^A-Za-z0-9._-]+", "_", model) + ".json")


def rate_try(model: str) -> bool:
    """Take a slot only if one is free now; never waits."""
    import fcntl
    ceiling = RATE_CEILING[_rate_class(model)]
    with open(_rate_file(model), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        try:
            st = json.loads(fh.read() or "{}")
        except ValueError:
            st = {}
        now = time.time()
        hits = [t for t in st.get("hits", []) if now - t < 60]
        if len(hits) >= st.get("limit", ceiling):
            return False
        hits.append(now)
        st["hits"] = hits
        st.setdefault("limit", ceiling)
        fh.seek(0); fh.truncate(); fh.write(json.dumps(st))
        return True


def rate_acquire(model: str, max_wait: float = 900.0) -> None:
    """Block until model has a free slot in the last 60 s."""
    import fcntl
    ceiling = RATE_CEILING[_rate_class(model)]
    path = _rate_file(model)
    deadline = time.time() + max_wait
    while True:
        with open(path, "a+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.seek(0)
            try:
                st = json.loads(fh.read() or "{}")
            except ValueError:
                st = {}
            now = time.time()
            hits = [t for t in st.get("hits", []) if now - t < 60]
            limit = st.get("limit", ceiling)
            if now - st.get("cut_at", 0) > 600 and limit < ceiling:
                limit = min(ceiling, limit + max(1, ceiling // 10))  # recover after a clean 10 min
                st["cut_at"] = now - 300
            if len(hits) < limit or now > deadline:
                hits.append(now)
                st.update(hits=hits, limit=limit)
                fh.seek(0); fh.truncate(); fh.write(json.dumps(st))
                return
            wait = 60 - (now - hits[0]) + 0.05
        time.sleep(min(max(wait, 0.2), 5.0))


def rate_throttled(model: str) -> None:
    """A 429 got through: lower this model's allowance for a while."""
    import fcntl
    path = _rate_file(model)
    with open(path, "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        try:
            st = json.loads(fh.read() or "{}")
        except ValueError:
            st = {}
        limit = st.get("limit", RATE_CEILING[_rate_class(model)])
        st["limit"] = max(2, int(limit * 0.75))
        st["cut_at"] = time.time()
        st["throttles"] = st.get("throttles", 0) + 1
        fh.seek(0); fh.truncate(); fh.write(json.dumps(st))


def rate_status() -> dict:
    """Per model: calls in the last minute, current allowance, 429s seen."""
    out = {}
    for f in sorted(RATE_DIR.glob("*.json")) if RATE_DIR.exists() else []:
        try:
            st = json.loads(f.read_text() or "{}")
        except ValueError:
            continue
        now = time.time()
        out[f.stem] = {"last_min": sum(1 for t in st.get("hits", []) if now - t < 60),
                       "limit": st.get("limit"), "throttles": st.get("throttles", 0)}
    return out


def vendor_call(
    model: str,
    messages: list,
    *,
    cf_token: str = "",
    nv_token: str = "",
    account: str = DEFAULT_ACCOUNT,
    max_tokens: int | None = None,
) -> dict:
    """Route to Workers AI or NIM using researched profiles, inside the
    shared per-model rate limit."""
    model = normalize_model(model)
    if batch_route(model) and not rate_try(model):
        _use_batch.on = True            # at the cap: overflow goes to the batch broker
    elif not batch_route(model):
        rate_acquire(model)             # direct-only model: wait for a slot
    r = _vendor_call_raw(model, messages, cf_token=cf_token, nv_token=nv_token, account=account,
                         max_tokens=max_tokens)
    if "429" in str(r.get("error", "")):
        rate_throttled(model)
    return r


def _vendor_call_raw(
    model: str,
    messages: list,
    *,
    cf_token: str = "",
    nv_token: str = "",
    account: str = DEFAULT_ACCOUNT,
    max_tokens: int | None = None,
) -> dict:
    if is_nvidia_model(model):
        if not nv_token:
            return {"error": "no NV_API_KEY", "ms": 0}
        prof = nv_profile(model)
        tok = int(max_tokens if max_tokens else prof.get("max_tokens", 4096))
        return nvidia_call(
            model,
            messages,
            nv_token,
            max_tokens=tok,
            temperature=float(prof.get("temperature", 0.2)),
            top_p=float(prof.get("top_p", 0.95)),
            reasoning_effort=prof.get("reasoning_effort"),
            chat_template_kwargs=prof.get("chat_template_kwargs"),
            stream=prof.get("stream"),
        )
    if not cf_token:
        return {"error": "no CF_TOKEN", "ms": 0}
    prof = cf_profile(model)
    tok = int(max_tokens if max_tokens else prof.get("max_tokens", 1800))
    if any(k in model.lower() for k in THINKING_ALWAYS_ON):
        # Thinking cannot be turned off here; a caller's answer-sized budget
        # gets eaten by reasoning and the reply comes back with no answer.
        tok = max(tok, int(prof.get("max_tokens", 0) or 0))
    return cf_call(
        model,
        messages,
        cf_token,
        account,
        max_tokens=tok,
        temperature=float(prof.get("temperature", 0.0)),
        enable_thinking=prof.get("enable_thinking"),
        use_max_completion_tokens=bool(prof.get("use_max_completion_tokens")),
        api=prof.get("api", "run"),
        reasoning_effort=prof.get("reasoning_effort"),
        timeout=int(prof.get("timeout", 120)),
    )


THINKING_ALWAYS_ON = ("glm-5.3", "gpt-oss-120b")  # never below the profile's max_tokens


def cf_profile(model: str) -> dict:
    """Per-model Workers AI kwargs from live schemas + docs/LLM_API_SETUP.md."""
    m = model.lower()
    if any(k in m for k in ("deepseek-v4", "kimi-k2", "glm-5.2", "qwen3.8", "nemotron-3-120b")):
        # Live schemas 2026-10-02: chat_template_kwargs.enable_thinking defaults
        # true on all five; false turns reasoning off. (glm-5.3 cannot disable
        # thinking and is excluded.) Long-context work-level reads need room.
        return {
            "enable_thinking": False,
            "reasoning_effort": "none" if ("kimi" in m or "deepseek" in m or "glm-5.2" in m) else None,
            "temperature": 0.2,
            "max_tokens": 8000,
            "use_max_completion_tokens": True,
            "timeout": 600,
        }
    if "glm-5.3" in m:
        # Thinking cannot be disabled on glm-5.3 (live schema 2026-10-02):
        # leave it on and give room so reasoning does not truncate the JSON.
        return {"temperature": 0.2, "max_tokens": 16000, "use_max_completion_tokens": True, "timeout": 900}
    if "glm" in m or "gemma" in m:
        # Live schema: chat_template_kwargs.enable_thinking default true
        return {
            "enable_thinking": False,
            "temperature": 0.0,
            "max_tokens": 2500,
            "use_max_completion_tokens": "gemma" in m,
        }
    if "gpt-oss" in m:
        # Schema default max_tokens=256 / temperature=0.6; do NOT invent thinking kwargs
        return {
            "temperature": 0.6,
            "max_tokens": 12000 if "120b" in m else 4096,   # checker JSON + reasoning
            "api": "run",
            "timeout": 600,
        }
    if "qwen" in m:
        # Full Pass A/B JSON (lemmas + multi-para english) truncates at 1800 on longer §§
        return {"temperature": 0.0, "max_tokens": 4096}
    return {"temperature": 0.0, "max_tokens": 1800}


def nv_profile(model: str) -> dict:
    """Per-model NIM kwargs from official infer docs + community hang fixes."""
    m = model.lower()
    if "deepseek" in m:
        # Non-stream hangs on free NIM; stream + reasoning_effort none is the fix
        return {
            "reasoning_effort": "none",
            "temperature": 1.0,
            "top_p": 0.95,
            "max_tokens": 4096,
            "stream": True,
            "chat_template_kwargs": None,  # extra ctk false can hang — do not send
        }
    if "nemotron-3-super" in m or "nemotron-3.5" in m or "nemotron-3-ultra" in m:
        # Ultra card (2026-10-02): reasoning_effort "none" = enable_thinking false;
        # without it Ultra thinks aloud and returns prose instead of JSON.
        return {
            "reasoning_effort": "none",
            "temperature": 1.0,
            "top_p": 0.95,
            "max_tokens": 4096,
            "stream": False,
        }
    return {
        "reasoning_effort": None,
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": 2500,
        "stream": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=TIER_A)
    ap.add_argument("--account", default=os.environ.get("CLOUDFLARE_ACCOUNT_ID", DEFAULT_ACCOUNT))
    ap.add_argument("--ollama", nargs="*", default=[], help="Local ollama model tags")
    ap.add_argument(
        "--nvidia",
        nargs="*",
        default=[],
        help="NVIDIA NIM model ids (e.g. nvidia/nemotron-3-nano-30b-a3b)",
    )
    ap.add_argument("--section", default="6.1")
    args = ap.parse_args()

    token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    # Owner env uses NV_API_KEY (also accept NVIDIA_API_KEY / NGC_API_KEY)
    nv_token = (
        os.environ.get("NV_API_KEY")
        or os.environ.get("NVIDIA_API_KEY")
        or os.environ.get("NGC_API_KEY")
        or ""
    )
    fix = load_fixture(args.section)
    messages = [
        {"role": "system", "content": SYS_TMPL.format(section=args.section)},
        {"role": "user", "content": user_prompt(fix)},
    ]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = OUT_ROOT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fixture.json").write_text(json.dumps(fix, indent=2), encoding="utf-8")

    results = []
    for model in args.models:
        print(f"→ {model}", flush=True)
        if not token:
            row = {"model": model, "error": "no CF_TOKEN/CLOUDFLARE_API_TOKEN", "ok": False}
        else:
            prof = cf_profile(model)
            raw = cf_call(
                model,
                messages,
                token,
                args.account,
                max_tokens=prof.get("max_tokens", 1800),
                temperature=prof.get("temperature", 0.0),
                enable_thinking=prof.get("enable_thinking"),
                use_max_completion_tokens=bool(prof.get("use_max_completion_tokens")),
                api=prof.get("api", "run"),
            )
            if raw.get("error"):
                row = {"model": model, **raw, "ok": False}
            else:
                obj = extract_json(raw["content"])
                sc = score(obj, raw["content"], args.section)
                row = {
                    "model": model,
                    "provider": "workers-ai",
                    "ms": raw["ms"],
                    "pt": raw["pt"],
                    "ct": raw["ct"],
                    **sc,
                    "parsed": obj,
                }
                (out_dir / (model.replace("/", "_") + ".raw.txt")).write_text(
                    raw["content"], encoding="utf-8"
                )
        results.append(row)
        flag = "PASS" if row.get("ok") else "FAIL"
        print(f"  {flag}  {row.get('ms', '?')}ms  {row.get('error') or row.get('checks')}", flush=True)
        time.sleep(0.4)

    for model in args.nvidia:
        print(f"→ nvidia:{model}", flush=True)
        if not nv_token:
            row = {
                "model": f"nvidia:{model}",
                "error": "no NV_API_KEY/NVIDIA_API_KEY",
                "ok": False,
            }
        else:
            prof = nv_profile(model)
            raw = nvidia_call(
                model,
                messages,
                nv_token,
                max_tokens=prof.get("max_tokens", 4096),
                temperature=prof.get("temperature", 1.0),
                top_p=prof.get("top_p", 0.95),
                reasoning_effort=prof.get("reasoning_effort"),
                chat_template_kwargs=prof.get("chat_template_kwargs"),
                stream=prof.get("stream"),
            )
            if raw.get("error"):
                row = {
                    "model": f"nvidia:{model}",
                    "provider": "nvidia-nim",
                    **raw,
                    "ok": False,
                }
            else:
                obj = extract_json(raw["content"])
                sc = score(obj, raw["content"], args.section)
                row = {
                    "model": f"nvidia:{model}",
                    "provider": "nvidia-nim",
                    "ms": raw["ms"],
                    "pt": raw["pt"],
                    "ct": raw["ct"],
                    **sc,
                    "parsed": obj,
                }
                safe = model.replace("/", "_")
                (out_dir / f"nvidia_{safe}.raw.txt").write_text(
                    raw["content"], encoding="utf-8"
                )
        results.append(row)
        flag = "PASS" if row.get("ok") else "FAIL"
        print(
            f"  {flag}  {row.get('ms', '?')}ms  {row.get('error') or row.get('checks')}",
            flush=True,
        )
        time.sleep(1.0)

    for tag in args.ollama:
        print(f"→ ollama:{tag}", flush=True)
        raw = ollama_call(tag, messages)
        if raw.get("error"):
            row = {"model": f"ollama:{tag}", "provider": "ollama", **raw, "ok": False}
        else:
            obj = extract_json(raw["content"])
            sc = score(obj, raw["content"], args.section)
            row = {
                "model": f"ollama:{tag}",
                "provider": "ollama",
                "ms": raw["ms"],
                **sc,
                "parsed": obj,
            }
            (out_dir / f"ollama_{tag.replace(':', '_')}.raw.txt").write_text(
                raw["content"], encoding="utf-8"
            )
        results.append(row)
        print(f"  {'PASS' if row.get('ok') else 'FAIL'}  {row.get('ms')}ms", flush=True)

    summary = {
        "stamp": stamp,
        "section": args.section,
        "passed": [r["model"] for r in results if r.get("ok")],
        "failed": [r["model"] for r in results if not r.get("ok")],
        "results": results,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nReceipt: {out_dir}")
    print(f"Passed ({len(summary['passed'])}): {', '.join(summary['passed']) or '—'}")
    print(f"Failed ({len(summary['failed'])}): {', '.join(summary['failed']) or '—'}")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
