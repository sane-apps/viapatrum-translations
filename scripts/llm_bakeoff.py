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

SYS_TMPL = """You translate early Christian Greek into new English for private study.
You may use ONLY the locked Greek paragraphs given. Do not use ANF, NPNF, FOTC,
web English, or memory of modern translations.

Return ONLY valid JSON (no markdown fences) with this shape:
{{
  "section": "{section}",
  "title": "short name of the thought (not a locus like Homily {section})",
  "pass_a_gloss": "literal sense gloss of the whole section",
  "lemmas": [{{"greek": "…", "gloss": "…"}}],
  "english": ["Pass B paragraph 1", "Pass B paragraph 2"],
  "translator_notes": ["OCR or uncertainty notes, or empty list"]
}}

Rules:
- pass_a_gloss must NOT equal the joined english paragraphs.
- english is reading prose in the author's voice; no idea absent from pass_a_gloss.
- If Greek is broken or gapped, say so in translator_notes; do not invent Greek.
"""


def load_fixture(section: str = "6.1") -> dict:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    for row in rows:
        if str(row.get("section")) == section:
            greek = row.get("greek") or []
            if isinstance(greek, str):
                greek = [greek]
            return {
                "section": section,
                "homily": row.get("homily"),
                "klostermann": row.get("klostermann"),
                "greek": greek,
            }
    raise SystemExit(f"Section {section} not found in {SOURCE}")


def user_prompt(fix: dict) -> str:
    paras = "\n\n".join(f"[p{i+1}]\n{p}" for i, p in enumerate(fix["greek"]))
    return (
        f"Section {fix['section']} ({fix.get('klostermann')}).\n"
        f"Locked Greek:\n{paras}\n\n"
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


def score(obj: dict | None, raw: str, section: str = "6.1") -> dict:
    checks: dict[str, bool] = {}
    notes: list[str] = []
    if not obj:
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
    checks["has_pass_b"] = len(eng) >= 1 and len(pb) >= 40
    checks["pass_a_ne_pass_b"] = bool(pa and pb and pa != pb)
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
    ok = all(checks.values())
    return {"ok": ok, "checks": checks, "notes": notes}


def _cf_pick_content(result: dict) -> str | None:
    """Normalize Workers AI result shapes (legacy response + chat choices)."""
    if not isinstance(result, dict):
        return None
    content = result.get("response")
    if content is None and result.get("choices"):
        msg0 = result["choices"][0].get("message") or {}
        content = (
            msg0.get("content")
            or msg0.get("reasoning_content")
            or msg0.get("reasoning")
        )
    if content is None and result.get("output_text"):
        content = result.get("output_text")
    if content is None and isinstance(result.get("output"), list):
        # Responses API-ish: join text chunks
        parts = []
        for item in result["output"]:
            if not isinstance(item, dict):
                continue
            for block in item.get("content") or []:
                if isinstance(block, dict) and block.get("text"):
                    parts.append(block["text"])
            if item.get("type") == "message":
                for block in item.get("content") or []:
                    if isinstance(block, dict) and block.get("text"):
                        parts.append(block["text"])
        content = "\n".join(parts) if parts else None
    if content is None:
        return None
    if not isinstance(content, str):
        return json.dumps(content)
    return content


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
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            ms = int((time.time() - t0) * 1000)
            # OpenAI-compat path returns choices at top level (no success wrapper)
            if api == "chat" and data.get("choices"):
                content = _cf_pick_content({"choices": data["choices"]})
                if not content:
                    return {"error": f"empty chat result: {json.dumps(data)[:200]}", "ms": ms}
                usage = data.get("usage") or {}
                return {
                    "content": content,
                    "ms": ms,
                    "pt": usage.get("prompt_tokens") or 0,
                    "ct": usage.get("completion_tokens") or 0,
                }
            if not data.get("success"):
                msg = json.dumps(data.get("errors") or data)[:240]
                if re.search(r"429|rate|capacity|9007|3040", msg, re.I) and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return {"error": msg, "ms": ms}
            result = data.get("result") or {}
            content = _cf_pick_content(result)
            if content is None:
                return {"error": f"empty result: {json.dumps(result)[:200]}", "ms": ms}
            usage = result.get("usage") or {}
            return {
                "content": content,
                "ms": ms,
                "pt": usage.get("prompt_tokens") or 0,
                "ct": usage.get("completion_tokens") or 0,
            }
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    return {"error": f"fetch failed: {last_err}", "ms": 0}


def _nvidia_read_sse(resp, deadline_s: float) -> tuple[str, dict]:
    """Accumulate SSE content (+ reasoning_content fallback). Returns (text, last_usage)."""
    chunks: list[str] = []
    reasoning: list[str] = []
    usage: dict = {}
    while True:
        if time.time() > deadline_s:
            break
        line = resp.readline()
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


def cf_profile(model: str) -> dict:
    """Per-model Workers AI kwargs from live schemas + docs/LLM_API_SETUP.md."""
    m = model.lower()
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
            "max_tokens": 4096,
            "api": "run",
        }
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
    if "nemotron-3-super" in m or "nemotron-3.5" in m:
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
