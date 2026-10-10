#!/usr/bin/env python3
"""Two-family semantic review of an audit packet, with structured provenance.

Reviews the packet's SELECTED sections in two lanes from different model
families. Two profiles (--profile):

  aligned (default since 2026-10-09)
    kimi    Cloudflare Workers AI @cf/moonshotai/kimi-k2.6   (kimi)
    glm     Cloudflare Workers AI @cf/zai-org/glm-5.2        (glm)
    Clause-aligned prompt: the source is cut into sentence chunks of <= 900
    characters; for each chunk the model writes its own literal gloss of the
    source FIRST, quotes the English that renders it, and lists only major
    meaning defects. One recorded call per chunk. Workers AI runs on the
    account's startup credits ($0 cash); credit use is recorded from the
    neurons the API reports.
  legacy (the default before 2026-10-09; old receipts stay valid)
    nim     NVIDIA NIM free endpoint, nvidia/nemotron-3-super-120b-a12b  (nemotron)
    gemini  Google AI Studio free tier, gemini-3.5-flash-lite            (gemini)
    The independent_review prompt, one call per whole section.

Why the default changed (bench outputs/review-bench-20261009, 20 known-bad
held sections with their fixed versions as controls): nemotron with the
independent_review prompt failed 19/20 fixed sections (no discrimination);
flash-lite was out of free quota; whole-section clause prompts on reasoning
models ran out of output budget on 3-4k character sections.

No paid fallback lane exists here and none is fallen back to. A rate limit or daily
cap writes the resumable checkpoint and exits 3 (QUOTA_PAUSE); rerun the same
command later to resume. Each call is recorded with the exact model id the API
echoed, its response/request ids, timestamps, token usage and the packet hashes
of the text it reviewed. pipeline/verify_translation_qa.py reads that
provenance (never the free-text reviewer string) for the two-family rule.

Section notes carry each model's verdict and notes plus Latin/English quotes of
25+ characters; a quote the model wrote is used when it is a verified span of
the text, otherwise an anchor span is copied from the packet text and labeled
so. A model fail or uncertainty is never hidden: the section stays fail until
the text is fixed (rerun re-reviews changed text) or an adjudication bound to
that exact call (response id) is supplied with --adjudications.

  source ~/.config/nv/env   # CLOUDFLARE_API_TOKEN (aligned); NV_API_KEY, GEMINI_API_KEY (legacy)
  python3 scripts/dual_family_review.py --packet P.packet.json \\
      --receipt-out P.review.json [--checkpoint C.json] [--adjudications A.json] \\
      [--profile aligned|legacy]

Optional Muse tiebreak (--muse-tiebreak; off by default, never a third family
in the gate): for each section that is still failing after adjudications, Muse
Code (via the GUI-session queue runner, scripts/muse_runner.py + muse_client.py)
is asked to judge each lane flag as a real error or a false positive. The answer
is stored as an advisory "muse_tiebreak" note on that review and cached in the
checkpoint. It never changes a verdict and never stands in for an adjudication;
it is input for the human/agent adjudicator. Muse is slow (~1 min per call).

Exit: 0 receipt written and passing; 1 receipt written with unresolved fails;
2 usage/parse error; 3 quota pause (checkpoint saved, no receipt).
"""
from __future__ import annotations

import argparse
import hashlib
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from independent_review import CHECKS, SYSTEM, USER_TEMPLATE, para_text  # noqa: E402
from pipeline.verify_translation_qa import (  # noqa: E402
    PROVENANCE_SCHEMA, SEMANTIC_CHECKS, _flat_text, _quotes_passage, independent_family_count,
    model_family,
)

NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CF_ACCOUNT = os.environ.get("CF_ACCOUNT_ID", "2c267ab06352ba2522114c3081a8c5fa")
CF_URL = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"
CF_USD_PER_1K_NEURONS = 0.011  # Workers AI list price; billed against startup credits
LANES = {
    "nim": {"provider": "nvidia-nim", "endpoint": NIM_URL, "tier": "free (NIM API catalog)",
            "model": "nvidia/nemotron-3-super-120b-a12b", "min_interval": 2.0},
    "gemini": {"provider": "google-ai-studio", "endpoint": GEMINI_URL.replace("{model}", "<model>"),
               "tier": "free (AI Studio free tier)", "model": "gemini-3.5-flash-lite",
               "min_interval": 4.5},
    "kimi": {"provider": "cloudflare-workers-ai", "endpoint": CF_URL.replace("{account}", "<account>").replace("{model}", "<model>"),
             "tier": "Workers AI on startup credits ($0 cash)", "model": "@cf/moonshotai/kimi-k2.6",
             "min_interval": 3.0, "key": "CLOUDFLARE_API_TOKEN", "caller": "cf"},
    "glm": {"provider": "cloudflare-workers-ai", "endpoint": CF_URL.replace("{account}", "<account>").replace("{model}", "<model>"),
            "tier": "Workers AI on startup credits ($0 cash)", "model": "@cf/zai-org/glm-5.2",
            "min_interval": 3.0, "key": "CLOUDFLARE_API_TOKEN", "caller": "cf"},
}
LANES["nim"].update({"key": "NV_API_KEY", "caller": "nim"})
LANES["gemini"].update({"key": "GEMINI_API_KEY", "caller": "gemini"})
PROFILES = {
    "aligned": {"lanes": ("kimi", "glm"), "prompt": "aligned"},
    "legacy": {"lanes": ("nim", "gemini"), "prompt": "independent"},
}
DEFAULT_PROFILE = "aligned"
CHUNK_CHARS = 900

ALIGNED_SYSTEM = ("You are a philologist auditing an English translation of Ancient Greek or Latin, "
                  "clause by clause. You read the source yourself; you never trust the English. "
                  "Reply with ONE JSON object only.")
ALIGNED_USER = """FULL ENGLISH TRANSLATION (for locating; it renders a longer source):
{english}

SOURCE PASSAGE TO CHECK ({lang}), part {part} of {parts}:
{chunk}

Task:
1. Write your own strict literal gloss of the SOURCE PASSAGE, word by word in order, from the {lang} only.
2. Quote the exact English sentences that render this passage.
3. Compare them clause by clause with your gloss. Report only MAJOR meaning errors: flipped negation or comparison, wrong subject/agent/speaker, changed tense/mood/command, wrong number, an invented clause or image not in the source, a dropped clause, a mistranslated key word, a Scripture reference that does not match the verse quoted (Psalms are usually cited in LXX numbering with the Hebrew/English number in brackets). NOT defects (never list them): style or word order; near-synonyms; an untranslated particle (καί, δέ, δή, γάρ, οὖν, τε, γε, μέν; et, autem, enim, vero); a participle rendered as a finite verb or clause; idiomatic tense or aspect; bracketed editorial notes or conjectures; parenthetical Scripture apparatus; OCR noise. Use "uncertain" only when source corruption leaves the meaning undecidable, never for something you judge acceptable.
Return ONE JSON object: {{"gloss": "...", "english": "...", "defects": [{{"check": "<one of: {checks}>", "english": "<exact English, 3-25 words>", "source": "<exact source words>", "problem": "<=25 words"}}], "uncertain": ["..."], "verdict": "pass" or "fail"}}"""
QUOTE_MIN = 25


class QuotaPause(Exception):
    pass


def _env_file(name: str) -> str:
    env = Path.home() / ".config/nv/env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(value) -> str:
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def build_messages(item: dict) -> list[dict]:
    """Exactly independent_review.second_verdict's prompt for one packet item."""
    src = para_text(item.get("source_text", []))
    eng = para_text(item.get("english", []))
    lang = "Latin" if re.search(r"\b(et|est|non|qui|quod|Deus)\b", " ".join(src)) else "Greek-or-Latin"
    user = USER_TEMPLATE % (lang, len(src), "\n".join(f"{i + 1}. {p}" for i, p in enumerate(src)),
                            len(eng), "\n".join(f"{i + 1}. {p}" for i, p in enumerate(eng)))
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def _post(url: str, body: dict, headers: dict, timeout: int):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", **headers},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        hdr = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status, hdr, json.loads(resp.read().decode())


def call_nim(model: str, messages: list[dict], key: str) -> dict:
    body = {"model": model, "messages": messages, "temperature": 1.0, "top_p": 0.95,
            "max_tokens": 2048, "stream": False, "reasoning_effort": "none"}
    status, hdr, data = _post(NIM_URL, body, {"Authorization": f"Bearer {key}",
                                              "Accept": "application/json"}, 180)
    msg = ((data.get("choices") or [{}])[0].get("message") or {})
    usage = data.get("usage") or {}
    return {"http_status": status, "text": msg.get("content") or msg.get("reasoning_content") or "",
            "response_model": data.get("model"), "response_id": data.get("id"),
            "request_id": hdr.get("nvcf-reqid") or hdr.get("x-request-id"),
            "finish_reason": (data.get("choices") or [{}])[0].get("finish_reason"),
            "usage": {"prompt_tokens": usage.get("prompt_tokens") or 0,
                      "completion_tokens": usage.get("completion_tokens") or 0,
                      "total_tokens": usage.get("total_tokens") or 0}}


def call_gemini(model: str, messages: list[dict], key: str) -> dict:
    body = {"systemInstruction": {"parts": [{"text": messages[0]["content"]}]},
            "contents": [{"role": "user", "parts": [{"text": messages[1]["content"]}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096,
                                 "responseMimeType": "application/json"}}
    status, hdr, data = _post(GEMINI_URL.format(model=model), body, {"x-goog-api-key": key}, 120)
    cand = (data.get("candidates") or [{}])[0]
    parts = (cand.get("content") or {}).get("parts") or []
    usage = data.get("usageMetadata") or {}
    return {"http_status": status,
            "text": "".join(p.get("text", "") for p in parts if isinstance(p, dict) and not p.get("thought")),
            "response_model": data.get("modelVersion"), "response_id": data.get("responseId"),
            "request_id": hdr.get("x-request-id") or hdr.get("x-goog-request-id"),
            "finish_reason": cand.get("finishReason"),
            "usage": {"prompt_tokens": usage.get("promptTokenCount") or 0,
                      "completion_tokens": (usage.get("candidatesTokenCount") or 0)
                      + (usage.get("thoughtsTokenCount") or 0),
                      "total_tokens": usage.get("totalTokenCount") or 0}}


def call_cf(model: str, messages: list[dict], key: str) -> dict:
    # Thinking off, as scripts/llm_bakeoff.cf_profile sets for kimi-k2.6 / glm-5.2:
    # with thinking on, kimi spends the whole budget reasoning and returns no answer.
    body = {"messages": messages, "temperature": 0.2, "max_completion_tokens": 4000,
            "chat_template_kwargs": {"enable_thinking": False}, "reasoning_effort": "none"}
    status, hdr, data = _post(CF_URL.format(account=CF_ACCOUNT, model=model), body,
                              {"Authorization": f"Bearer {key}"}, 600)
    res = data.get("result") or {}
    choice = (res.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    usage = res.get("usage") or {}
    return {"http_status": status, "text": msg.get("content") or res.get("response") or "",
            "response_model": res.get("model"), "response_id": res.get("id"),
            "request_id": hdr.get("cf-ai-req-id") or hdr.get("cf-ray"),
            "finish_reason": choice.get("finish_reason"),
            "usage": {"prompt_tokens": usage.get("prompt_tokens") or 0,
                      "completion_tokens": usage.get("completion_tokens") or 0,
                      "total_tokens": usage.get("total_tokens") or 0,
                      "neurons": usage.get("neurons") or 0}}


CALLERS = {"nim": call_nim, "gemini": call_gemini, "cf": call_cf}


def source_chunks(paragraphs, size: int = CHUNK_CHARS) -> list[str]:
    """Sentence chunks of the source, each <= size chars where a sentence allows."""
    text = " ".join(" ".join(str(p).split()) for p in paragraphs)
    parts = re.split(r"(?<=[.;\u00b7\u0387:!?])\s+", text)
    out, cur = [], ""
    for part in parts:
        if cur and len(cur) + len(part) + 1 > size:
            out.append(cur)
            cur = ""
        cur = (cur + " " + part).strip()
    if cur:
        out.append(cur)
    return out or [text]


def build_aligned_messages(item: dict, chunk: str, part: int, parts: int) -> list[dict]:
    src = para_text(item.get("source_text", []))
    eng = para_text(item.get("english", []))
    lang = "Latin" if re.search(r"\b(et|est|non|qui|quod|Deus)\b", " ".join(src)) else "Greek"
    user = ALIGNED_USER.format(english="\n".join(eng), lang=lang, part=part, parts=parts, chunk=chunk,
                               checks=", ".join(CHECKS))
    return [{"role": "system", "content": ALIGNED_SYSTEM}, {"role": "user", "content": user}]


def parse_aligned(text: str) -> dict | None:
    """Aligned-prompt reply -> {verdict, checks, uncertainties, notes}. Any listed
    defect makes the verdict fail whatever the model's own verdict field says."""
    raw = text or ""
    start, obj = raw.find("{"), None
    while start != -1 and obj is None:
        try:
            obj, _ = json.JSONDecoder().raw_decode(raw[start:])
        except ValueError:
            start = raw.find("{", start + 1)
    if not isinstance(obj, dict) or obj.get("verdict") not in ("pass", "fail"):
        # Invalid JSON (often an unescaped quote inside the gloss). Read the verdict
        # and the defect list by pattern; anything unreadable counts as a fail.
        v = re.findall(r'"verdict"\s*:\s*"(pass|fail)"', raw)
        empty = re.search(r'"defects"\s*:\s*\[\s*\]', raw)
        if not v:
            return None
        if v[-1] == "pass" and empty:
            obj = {"verdict": "pass", "defects": [], "uncertain": []}
        else:
            m = re.search(r'"defects"\s*:\s*(\[.*?\])\s*,\s*"(?:uncertain|verdict)"', raw, re.S)
            obj = {"verdict": "fail", "uncertain": [],
                   "defects": [{"check": "completeness", "english": "", "source": "",
                                "problem": "unparsed defect list: " + (m.group(1) if m else raw[-600:])[:600]}]}
    defects = [d for d in obj.get("defects") or [] if isinstance(d, dict)]
    failed = {str(d.get("check")) for d in defects}
    checks = {k: k not in failed for k in CHECKS}
    if defects and all(checks.values()):
        checks["completeness"] = False  # a defect with no recognised check name
    notes = "; ".join(f"[{d.get('check')}] \"{d.get('english')}\" vs \"{d.get('source')}\": {d.get('problem')}"
                      for d in defects)
    return {"verdict": "fail" if defects else obj["verdict"], "checks": checks,
            "uncertainties": [str(u) for u in obj.get("uncertain") or [] if str(u).strip()],
            "notes": notes or ("no major defect; gloss: " + str(obj.get("gloss") or "")[:300])}


def parse_verdict(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
    except ValueError:
        return None
    if obj.get("verdict") not in ("pass", "fail") or not isinstance(obj.get("checks"), dict):
        return None
    return obj


def is_daily_cap(body: str) -> bool:
    return bool(re.search(r"per ?day|PerDay|daily", body, re.I))


def run_lane_call(lane: str, model: str, item: dict, key: str, state: dict,
                  messages: list[dict] | None = None, parser=None) -> dict:
    """One reviewed call (with one parse retry). Raises QuotaPause on 429/cap."""
    messages = messages or build_messages(item)
    parser = parser or parse_verdict
    attempts = state.setdefault("attempts", {}).setdefault(lane, [])
    for parse_try in range(2):
        for backoff_try in range(2):
            wait = LANES[lane]["min_interval"] - (time.time() - state.get("last", {}).get(lane, 0))
            if wait > 0:
                time.sleep(wait)
            started = now()
            t0 = time.time()
            try:
                res = CALLERS[LANES[lane]["caller"]](model, messages, key)
                state.setdefault("last", {})[lane] = time.time()
            except urllib.error.HTTPError as exc:
                state.setdefault("last", {})[lane] = time.time()
                body = exc.read().decode("utf-8", "replace")[:600]
                attempts.append({"section": item["section"], "started_at": started, "finished_at": now(),
                                 "http_status": exc.code, "error": body[:300]})
                if exc.code == 429:
                    if is_daily_cap(body) or backoff_try:
                        raise QuotaPause(f"{lane} HTTP 429 ({'daily cap' if is_daily_cap(body) else 'rate limit persisted after 60s backoff'}): {body[:200]}")
                    time.sleep(60)
                    continue
                if exc.code in (408, 500, 502, 503, 504) and not backoff_try:  # 408: Workers AI inference timeout
                    time.sleep(10)
                    continue
                return {"error": f"HTTP {exc.code}: {body[:200]}"}
            except Exception as exc:  # noqa: BLE001 - network timeouts etc.
                state.setdefault("last", {})[lane] = time.time()
                attempts.append({"section": item["section"], "started_at": started, "finished_at": now(),
                                 "error": f"{type(exc).__name__}: {exc}"[:300]})
                if not backoff_try:
                    time.sleep(10)
                    continue
                return {"error": f"{type(exc).__name__}: {exc}"[:200]}
            res["ms"] = int((time.time() - t0) * 1000)
            verdict = parser(res["text"])
            rec = {"section": item["section"], "source_sha256": item["source_sha256"],
                   "english_sha256": item["english_sha256"], "lane": lane, "model": model,
                   "response_model": res["response_model"], "response_id": res["response_id"],
                   "request_id": res["request_id"], "http_status": res["http_status"],
                   "finish_reason": res["finish_reason"], "started_at": started,
                   "finished_at": now(), "ms": res["ms"], "usage": res["usage"],
                   "raw_sha256": sha(res["text"] or "")}
            attempts.append({k: rec[k] for k in ("section", "started_at", "finished_at", "http_status",
                                                 "response_id", "usage")})
            if verdict is None:
                rec["error"] = "unparseable model output"
                rec["raw_head"] = (res["text"] or "")[:300]
                if parse_try == 0:
                    break  # retry once with a fresh call
                return rec
            checks = verdict.get("checks") or {}
            rec.update({"verdict": verdict["verdict"],
                        "checks": {k: checks.get(k) is True for k in CHECKS},
                        "uncertainties": [str(u) for u in (verdict.get("uncertainties") or [])],
                        "covered_source_paragraphs": verdict.get("covered_source_paragraphs")
                        or list(range(1, len(item.get("source_text") or []) + 1)),
                        "notes": str(verdict.get("notes") or "")})
            return rec
    return {"error": "no call made"}


def run_aligned_section(lane: str, model: str, item: dict, key: str, state: dict) -> dict:
    """Aligned profile: one recorded call per source chunk, folded into one
    section record. The section fails if any chunk fails; each chunk call keeps
    its own response id for provenance and adjudication."""
    chunks = source_chunks(item.get("source_text") or [])
    subs = []
    for i, chunk in enumerate(chunks, 1):
        rec = run_lane_call(lane, model, item, key, state,
                            messages=build_aligned_messages(item, chunk, i, len(chunks)), parser=parse_aligned)
        if rec.get("error"):
            return {**rec, "section": item["section"], "chunk": i}
        rec["chunk"], rec["chunk_sha256"] = i, sha(chunk)
        subs.append(rec)
    fails = [r for r in subs if r["verdict"] != "pass" or r["uncertainties"]]
    head = subs[0]
    agg = {k: head[k] for k in ("section", "source_sha256", "english_sha256", "lane", "model",
                                "response_model", "http_status", "started_at")}
    agg.update({
        "response_id": "+".join(str(r["response_id"]) for r in (fails or subs)),
        "request_id": "+".join(str(r.get("request_id")) for r in (fails or subs)),
        "finish_reason": ",".join(sorted({str(r["finish_reason"]) for r in subs})),
        "finished_at": subs[-1]["finished_at"], "ms": sum(r["ms"] for r in subs),
        "usage": {k: sum((r.get("usage") or {}).get(k, 0) for r in subs)
                  for k in ("prompt_tokens", "completion_tokens", "total_tokens", "neurons")},
        "raw_sha256": sha("".join(r["raw_sha256"] for r in subs)),
        "verdict": "fail" if any(r["verdict"] != "pass" for r in subs) else "pass",
        "checks": {k: all(r["checks"].get(k) for r in subs) for k in CHECKS},
        "uncertainties": [u for r in subs for u in r["uncertainties"]],
        "covered_source_paragraphs": list(range(1, len(item.get("source_text") or []) + 1)),
        "notes": " | ".join(f"part {r['chunk']}/{len(subs)}: {r['notes']}" for r in (fails or subs[:1])),
        "chunk_calls": [{k: r.get(k) for k in ("chunk", "chunk_sha256", "response_model", "response_id",
                                                 "request_id", "http_status", "finish_reason", "started_at",
                                                 "finished_at", "ms", "usage", "raw_sha256", "verdict",
                                                 "uncertainties", "notes")} for r in subs],
    })
    return agg


def quoted_spans(note: str, passage, n: int = QUOTE_MIN) -> list[str]:
    """Quoted strings in a model note that are verified spans of the passage."""
    text = _flat_text(passage)
    hits = []
    for q in re.findall(r"[\"\u201c\u2018']([^\"\u201d\u2019]{%d,400})[\"\u201d\u2019']" % n, note or ""):
        q = " ".join(q.split())
        if len(q) >= n and q in text:
            hits.append(q)
    return hits


def anchor(passage, n: int = 90) -> str:
    text = _flat_text(passage)
    if len(text) <= n:
        return text
    cut = text.rfind(" ", QUOTE_MIN + 5, n)
    return text[: cut if cut > 0 else n]


def combine(item: dict, recs: list[dict], adjudications: list[dict]) -> dict:
    src, eng = item.get("source_text"), item.get("english")
    lines, lane_summ, open_issues, applied = [], [], [], []
    latin_q = english_q = None
    for rec in recs:
        fam = model_family(rec["model"])
        failed = [k for k in CHECKS if not rec["checks"].get(k)]
        lines.append(f"[{fam} {rec['model']}] verdict={rec['verdict']}; failed checks: "
                     f"{', '.join(failed) or 'none'}; uncertainties: {len(rec['uncertainties'])}; "
                     f"model notes: {rec['notes']}")
        lq, eq = quoted_spans(rec["notes"], src), quoted_spans(rec["notes"], eng)
        latin_q = latin_q or (lq[0] if lq else None)
        english_q = english_q or (eq[0] if eq else None)
        rec["model_quoted_latin"], rec["model_quoted_english"] = bool(lq), bool(eq)
        lane_summ.append({"model": rec["model"], "family": fam, "verdict": rec["verdict"],
                          "failed_checks": failed, "uncertainties": rec["uncertainties"],
                          "response_id": rec["response_id"]})
        if rec["verdict"] != "pass" or rec["uncertainties"] or failed:
            adj = [a for a in adjudications if a.get("model") == rec["model"]
                   and a.get("response_id") == rec["response_id"] and str(a.get("resolution") or "").strip()]
            if adj:
                applied.extend(adj)
            else:
                open_issues.append(f"{rec['model']} {rec['verdict']}"
                                   f" (failed: {', '.join(failed) or 'none'}): {rec['notes'][:300]}"
                                   + (f" | uncertainties: {rec['uncertainties']}" if rec["uncertainties"] else ""))
    lines.append("Latin quote (%s): \u00ab%s\u00bb" % (
        "from model note, verified" if latin_q else "anchor copied from packet text", latin_q or anchor(src)))
    lines.append("English quote (%s): \u00ab%s\u00bb" % (
        "from model note, verified" if english_q else "anchor copied from packet text", english_q or anchor(eng)))
    for a in applied:
        lines.append(f"ADJUDICATED {a['model']} ({a.get('by', 'Densify')}): {a['resolution']}")
    ok = not open_issues
    checks = {k: (ok or all(r["checks"].get(k) for r in recs)) for k in SEMANTIC_CHECKS}
    if ok:
        checks = {k: True for k in SEMANTIC_CHECKS}
    review = {"section": item["section"], "verdict": "pass" if ok else "fail", "checks": checks,
              "uncertainties": [] if ok else open_issues,
              "covered_source_paragraphs": list(range(1, len(item["source_text"]) + 1)),
              "notes": "\n".join(lines), "lanes": lane_summ}
    if applied:
        review["adjudications"] = applied
    return review


MUSE_TIEBREAK_PROMPT = """You are adjudicating flags that two automated reviewers raised against an English
translation of an Ancient Greek or Latin passage. Read the SOURCE yourself; do not trust the English.
For each numbered flag decide whether it is a REAL meaning error in the English (flipped negation,
wrong subject/agent, wrong tense/mood with changed meaning, invented or dropped clause, mistranslated
key word, Scripture reference that does not match the verse quoted) or a FALSE POSITIVE (style, word
order, near-synonym, particle, participle-as-clause, parenthetical apparatus or headings, editorial
brackets, text actually present elsewhere in the passage).
Do not use any tools or files; answer from the text below only.

SOURCE ({section}):
{source}

ENGLISH:
{english}

FLAGS:
{flags}

Return ONE JSON object only: {{"flags": [{{"n": <number>, "real": true|false, "why": "<=30 words"}}],
"verdict": "pass" if no flag is real else "fail"}}"""


def _muse_flags(review: dict) -> list[str]:
    out = []
    for line in str(review.get("notes") or "").splitlines():
        if line.startswith("[") and "verdict=" in line and "verdict=pass" not in line.split(";")[0]:
            out.append(line[:3000])
    return out or [u[:3000] for u in review.get("uncertainties") or []]


def apply_muse_tiebreak(items: list[dict], reviews: list[dict], state: dict, ask, effort: str = "medium",
                        timeout: int = 1500, save=None) -> int:
    """Attach an advisory Muse judgement to every failing review. Never changes a verdict.
    `ask(prompt, effort=, timeout=, tag=)` returns a muse_client result dict. Returns new Muse calls made."""
    cache = state.setdefault("muse_tiebreak", {})
    by_sid = {it["section"]: it for it in items}
    calls = 0
    for r in reviews:
        if r.get("verdict") == "pass":
            continue
        it = by_sid[r["section"]]
        key = sha(json.dumps([it.get("source_sha256"), it.get("english_sha256"),
                             [l.get("response_id") for l in r.get("lanes", [])], effort]))
        rec = cache.get(r["section"])
        if not rec or rec.get("key") != key or rec.get("error"):
            flags = _muse_flags(r)
            prompt = MUSE_TIEBREAK_PROMPT.format(
                section=r["section"], source=_flat_text(it.get("source_text")), english=_flat_text(it.get("english")),
                flags="\n".join(f"{i}. {f}" for i, f in enumerate(flags, 1)))
            res = ask(prompt, effort=effort, timeout=timeout, tag="tiebreak")
            calls += 1
            answer = str(res.get("answer") or "")
            parsed = None
            m = re.search(r"\{.*\}", answer, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except ValueError:
                    parsed = None
            rec = {"key": key, "advisory": True, "model": "muse (Muse Code, Meta)", "effort": effort,
                   "queue_id": res.get("id"), "seconds": res.get("seconds"), "finished_at": res.get("finished_at"),
                   "answer_sha256": sha(answer), "verdict": (parsed or {}).get("verdict"),
                   "flags": (parsed or {}).get("flags"), "n_flags": len(flags),
                   "error": res.get("error") or (None if parsed else "unparsed Muse answer")}
            cache[r["section"]] = rec
            if save:
                save()
        r["muse_tiebreak"] = {k: v for k, v in rec.items() if k != "key"}
    return calls


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--receipt-out", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--adjudications", type=Path, help="JSON {section: [{model, response_id, resolution, by}]}")
    ap.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE,
                    help=f"lane pair and prompt (default {DEFAULT_PROFILE}; 'legacy' = nemotron + gemini, independent_review prompt)")
    ap.add_argument("--nim-model", default=LANES["nim"]["model"])
    ap.add_argument("--gemini-model", default=LANES["gemini"]["model"])
    ap.add_argument("--kimi-model", default=LANES["kimi"]["model"])
    ap.add_argument("--glm-model", default=LANES["glm"]["model"])
    ap.add_argument("--scope-note", default="")
    ap.add_argument("--max-new-calls", type=int, default=0, help="Stop after N new calls (0 = no limit)")
    ap.add_argument("--muse-tiebreak", action="store_true",
                    help="advisory Muse judgement on still-failing sections via the GUI-session queue runner "
                         "(slow; never changes a verdict; off by default)")
    ap.add_argument("--muse-effort", default="medium")
    ap.add_argument("--muse-timeout", type=int, default=1500)
    args = ap.parse_args(argv)

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    items = packet.get("sections") or []
    if not items:
        print("FAIL: packet has no selected sections")
        return 2
    profile = PROFILES[args.profile]
    lane_names = profile["lanes"]
    every = {"nim": args.nim_model, "gemini": args.gemini_model, "kimi": args.kimi_model, "glm": args.glm_model}
    models = {lane: every[lane] for lane in lane_names}
    for lane, model in models.items():
        if model_family(model) is None:
            print(f"FAIL: {lane} model {model} has no family in MODEL_FAMILY")
            return 2
    if independent_family_count([(m, model_family(m)) for m in models.values()]) < 2:
        print("FAIL: both lanes are one family")
        return 2
    keys = {lane: (os.environ.get(LANES[lane]["key"], "") or _env_file(LANES[lane]["key"])).strip()
            for lane in lane_names}
    ckpt_path = args.checkpoint or args.receipt_out.with_suffix(".checkpoint.json")
    state = {"packet_id": packet["packet_id"], "calls": {lane: {} for lane in lane_names},
             "superseded": [], "attempts": {}}
    if ckpt_path.exists():
        prev = json.loads(ckpt_path.read_text())
        for lane, calls in (prev.get("calls") or {}).items():
            if lane in state["calls"]:
                state["calls"][lane] = calls
        state["superseded"] = prev.get("superseded", [])
        state["attempts"] = prev.get("attempts", {})
        if prev.get("muse_tiebreak"):
            state["muse_tiebreak"] = prev["muse_tiebreak"]
        if prev.get("packet_id") != packet["packet_id"]:
            state["superseded"].append({"note": f"packet changed from {prev.get('packet_id')}"})
    adjud = json.loads(args.adjudications.read_text()) if args.adjudications else {}

    def save():
        ckpt_path.parent.mkdir(parents=True, exist_ok=True)
        ckpt_path.write_text(json.dumps({**state, "last": None, "saved_at": now()},
                                        ensure_ascii=False, indent=1) + "\n")

    new_calls, pause, errors = 0, None, []
    try:
        for item in items:
            sid = item["section"]
            for lane in lane_names:
                have = state["calls"][lane].get(sid)
                if have and (have.get("source_sha256"), have.get("english_sha256"), have.get("model")) == (
                        item["source_sha256"], item["english_sha256"], models[lane]) and not have.get("error"):
                    continue
                if have:
                    state["superseded"].append(have)
                if not keys[lane]:
                    raise QuotaPause(f"{lane} key missing in environment")
                if args.max_new_calls and new_calls >= args.max_new_calls:
                    raise QuotaPause(f"--max-new-calls {args.max_new_calls} reached")
                if profile["prompt"] == "aligned":
                    rec = run_aligned_section(lane, models[lane], item, keys[lane], state)
                else:
                    rec = run_lane_call(lane, models[lane], item, keys[lane], state)
                new_calls += 1
                state["calls"][lane][sid] = rec
                save()
                tag = rec.get("verdict") or ("ERROR " + str(rec.get("error"))[:120])
                print(f"{sid} {lane} {tag}", flush=True)
    except QuotaPause as exc:
        pause = str(exc)
    save()
    if pause:
        print(f"QUOTA_PAUSE: {pause}. Checkpoint {ckpt_path}; rerun the same command to resume.")
        return 3

    reviews, lanes_prov = [], []
    for item in items:
        sid = item["section"]
        recs = [state["calls"][lane].get(sid) for lane in lane_names]
        bad = [r for r in recs if not r or r.get("error")]
        if bad:
            errors.append(f"{sid}: lane error {[r.get('error') if r else 'missing' for r in bad]}")
            continue
        reviews.append(combine(item, recs, adjud.get(sid, [])))
    if args.muse_tiebreak and reviews:
        from muse_client import ask as muse_ask  # lazy: only when asked for
        n = apply_muse_tiebreak(items, reviews, state, muse_ask, args.muse_effort, args.muse_timeout, save)
        save()
        print(f"muse tiebreak: {n} new call(s); advisory only")
    for lane in lane_names:
        calls = [state["calls"][lane][it["section"]] for it in items
                 if state["calls"][lane].get(it["section"]) and not state["calls"][lane][it["section"]].get("error")]
        att = state["attempts"].get(lane, [])
        tok = {k: sum((c.get("usage") or {}).get(k, 0) for c in att) for k in
               ("prompt_tokens", "completion_tokens", "total_tokens", "neurons")}
        # Aligned sections fold one call per chunk; provenance lists every chunk call.
        flat = []
        for c in calls:
            for sub in c.get("chunk_calls") or [None]:
                flat.append(c if sub is None else {**c, **sub, "chunk_of": c["section"]})
        calls = flat
        lanes_prov.append({
            "lane": lane, "provider": LANES[lane]["provider"], "endpoint": LANES[lane]["endpoint"],
            "tier": LANES[lane]["tier"], "spend_usd": 0, "model": models[lane],
            "credit_usd": round(tok["neurons"] / 1000 * CF_USD_PER_1K_NEURONS, 4)
            if LANES[lane]["caller"] == "cf" else 0,
            "family": model_family(models[lane]), "call_count": len(calls),
            "http_attempts": len(att),
            "failed_attempts": [a for a in att if a.get("error")],
            "tokens_all_attempts": tok,
            "tokens_counted_calls": {k: sum((c.get("usage") or {}).get(k, 0) for c in calls)
                                     for k in ("prompt_tokens", "completion_tokens", "total_tokens")},
            "first_call_at": min((c["started_at"] for c in calls), default=None),
            "last_call_at": max((c["finished_at"] for c in calls), default=None),
            "calls": [{k: c.get(k) for k in (
                "section", "source_sha256", "english_sha256", "response_model", "response_id",
                "request_id", "http_status", "finish_reason", "started_at", "finished_at", "ms",
                "usage", "raw_sha256", "verdict", "checks", "uncertainties",
                "model_quoted_latin", "model_quoted_english", "chunk", "chunk_sha256")} for c in calls],
        })
    if errors:
        for e in errors:
            print("FAIL:", e)
        print("No receipt written; fix lane errors and rerun (checkpoint kept).")
        return 2
    prompt_text = (ALIGNED_SYSTEM + "\n" + ALIGNED_USER) if profile["prompt"] == "aligned" else (SYSTEM + "\n" + USER_TEMPLATE)
    prompt_sha = sha(prompt_text)
    fails = [r for r in reviews if r["verdict"] != "pass"]
    first = items[0]
    scope = None
    if packet.get("publication_scope") is not None:
        scope = {"verdict": "pass" if not fails else "fail",
                 "checks": {k: not fails for k in SEMANTIC_CHECKS},
                 "uncertainties": [] if not fails else [f"{len(fails)} section(s) unresolved"],
                 "composed_by": "dual_family_review adapter (summary of per-section lane verdicts)",
                 "notes": (f"Scope: {len(items)} selected section(s) {', '.join(i['section'] for i in items)}; "
                           f"each reviewed by {' and '.join(models.values())} with the "
                           f"{'clause-aligned chunk' if profile['prompt'] == 'aligned' else 'independent_review'} prompt. "
                           f"{args.scope_note} Opening Latin "
                           f"\u00ab{anchor(first['source_text'])}\u00bb English \u00ab{anchor(first['english'])}\u00bb.")}
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": "dual_family_review: " + " + ".join(f"{model_family(m)} ({m})" for m in models.values()),
        "reviewer_note": "Display only. The two-family gate reads review_provenance.",
        "verdict": "pass" if not fails else "fail",
        "review_provenance": {
            "schema": PROVENANCE_SCHEMA, "adapter": "scripts/dual_family_review.py",
            "adapter_sha256": sha(Path(__file__).read_bytes()),
            "profile": args.profile,
            "prompt": {"source": ("scripts/dual_family_review.py ALIGNED_SYSTEM + ALIGNED_USER (per source chunk)"
                                  if profile["prompt"] == "aligned" else
                                  "scripts/independent_review.py SYSTEM + USER_TEMPLATE"), "sha256": prompt_sha},
            "packet_id": packet["packet_id"], "generated_at": now(), "spend_usd": 0,
            "credit_usd": round(sum(lp.get("credit_usd", 0) for lp in lanes_prov), 4),
            "lanes": lanes_prov,
            "superseded_calls": [{k: s.get(k) for k in ("section", "model", "response_id", "verdict",
                                                         "english_sha256", "finished_at", "notes", "error")}
                                 for s in state["superseded"] if isinstance(s, dict) and s.get("section")],
        },
        "reviews": reviews,
    }
    if scope:
        receipt["scope_review"] = scope
    args.receipt_out.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for lp in lanes_prov:
        print(f"lane {lp['lane']} {lp['model']} calls={lp['call_count']} attempts={lp['http_attempts']} "
              f"tokens={lp['tokens_all_attempts']['total_tokens']}")
    for r in fails:
        print(f"UNRESOLVED {r['section']}: {r['uncertainties']}")
    print(f"receipt {args.receipt_out} verdict={receipt['verdict']} sections={len(reviews)} unresolved={len(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
