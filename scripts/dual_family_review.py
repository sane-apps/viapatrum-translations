#!/usr/bin/env python3
"""Two-family semantic review of an audit packet, with structured provenance.

Runs the per-section audit prompt from scripts/independent_review.py over the
packet's SELECTED sections in two free lanes from different model families:

  nim     NVIDIA NIM free endpoint, nvidia/nemotron-3-super-120b-a12b  (nemotron)
  gemini  Google AI Studio free tier, gemini-3.5-flash-lite            (gemini)

No metered lane exists here and none is fallen back to. A rate limit or daily
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

  source ~/.config/nv/env   # NV_API_KEY, GEMINI_API_KEY (never printed)
  python3 scripts/dual_family_review.py --packet P.packet.json \\
      --receipt-out P.review.json [--checkpoint C.json] [--adjudications A.json]

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
    PROVENANCE_SCHEMA, SEMANTIC_CHECKS, _flat_text, _quotes_passage, model_family,
)

NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
LANES = {
    "nim": {"provider": "nvidia-nim", "endpoint": NIM_URL, "tier": "free (NIM API catalog)",
            "model": "nvidia/nemotron-3-super-120b-a12b", "min_interval": 2.0},
    "gemini": {"provider": "google-ai-studio", "endpoint": GEMINI_URL.replace("{model}", "<model>"),
               "tier": "free (AI Studio free tier)", "model": "gemini-3.5-flash-lite",
               "min_interval": 4.5},
}
QUOTE_MIN = 25


class QuotaPause(Exception):
    pass


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


CALLERS = {"nim": call_nim, "gemini": call_gemini}


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


def run_lane_call(lane: str, model: str, item: dict, key: str, state: dict) -> dict:
    """One reviewed call (with one parse retry). Raises QuotaPause on 429/cap."""
    messages = build_messages(item)
    attempts = state.setdefault("attempts", {}).setdefault(lane, [])
    for parse_try in range(2):
        for backoff_try in range(2):
            wait = LANES[lane]["min_interval"] - (time.time() - state.get("last", {}).get(lane, 0))
            if wait > 0:
                time.sleep(wait)
            started = now()
            t0 = time.time()
            try:
                res = CALLERS[lane](model, messages, key)
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
                if exc.code in (500, 502, 503, 504) and not backoff_try:
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
            verdict = parse_verdict(res["text"])
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
                        "covered_source_paragraphs": verdict.get("covered_source_paragraphs"),
                        "notes": str(verdict.get("notes") or "")})
            return rec
    return {"error": "no call made"}


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--receipt-out", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--adjudications", type=Path, help="JSON {section: [{model, response_id, resolution, by}]}")
    ap.add_argument("--nim-model", default=LANES["nim"]["model"])
    ap.add_argument("--gemini-model", default=LANES["gemini"]["model"])
    ap.add_argument("--scope-note", default="")
    ap.add_argument("--max-new-calls", type=int, default=0, help="Stop after N new calls (0 = no limit)")
    args = ap.parse_args(argv)

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    items = packet.get("sections") or []
    if not items:
        print("FAIL: packet has no selected sections")
        return 2
    models = {"nim": args.nim_model, "gemini": args.gemini_model}
    for lane, model in models.items():
        if model_family(model) is None:
            print(f"FAIL: {lane} model {model} has no family in MODEL_FAMILY")
            return 2
    if model_family(models["nim"]) == model_family(models["gemini"]):
        print("FAIL: both lanes are one family")
        return 2
    keys = {"nim": os.environ.get("NV_API_KEY", "").strip(),
            "gemini": os.environ.get("GEMINI_API_KEY", "").strip()}
    ckpt_path = args.checkpoint or args.receipt_out.with_suffix(".checkpoint.json")
    state = {"packet_id": packet["packet_id"], "calls": {"nim": {}, "gemini": {}},
             "superseded": [], "attempts": {}}
    if ckpt_path.exists():
        prev = json.loads(ckpt_path.read_text())
        state["calls"] = prev.get("calls", state["calls"])
        state["superseded"] = prev.get("superseded", [])
        state["attempts"] = prev.get("attempts", {})
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
            for lane in ("nim", "gemini"):
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
        recs = [state["calls"][lane].get(sid) for lane in ("nim", "gemini")]
        bad = [r for r in recs if not r or r.get("error")]
        if bad:
            errors.append(f"{sid}: lane error {[r.get('error') if r else 'missing' for r in bad]}")
            continue
        reviews.append(combine(item, recs, adjud.get(sid, [])))
    for lane in ("nim", "gemini"):
        calls = [state["calls"][lane][it["section"]] for it in items
                 if state["calls"][lane].get(it["section"]) and not state["calls"][lane][it["section"]].get("error")]
        att = state["attempts"].get(lane, [])
        tok = {k: sum((c.get("usage") or {}).get(k, 0) for c in att) for k in
               ("prompt_tokens", "completion_tokens", "total_tokens")}
        lanes_prov.append({
            "lane": lane, "provider": LANES[lane]["provider"], "endpoint": LANES[lane]["endpoint"],
            "tier": LANES[lane]["tier"], "spend_usd": 0, "model": models[lane],
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
                "model_quoted_latin", "model_quoted_english")} for c in calls],
        })
    if errors:
        for e in errors:
            print("FAIL:", e)
        print("No receipt written; fix lane errors and rerun (checkpoint kept).")
        return 2
    prompt_sha = sha(SYSTEM + "\n" + USER_TEMPLATE)
    fails = [r for r in reviews if r["verdict"] != "pass"]
    first = items[0]
    scope = None
    if packet.get("publication_scope") is not None:
        scope = {"verdict": "pass" if not fails else "fail",
                 "checks": {k: not fails for k in SEMANTIC_CHECKS},
                 "uncertainties": [] if not fails else [f"{len(fails)} section(s) unresolved"],
                 "composed_by": "dual_family_review adapter (summary of per-section lane verdicts)",
                 "notes": (f"Scope: {len(items)} selected section(s) {', '.join(i['section'] for i in items)}; "
                           f"each reviewed by {models['nim']} and {models['gemini']} with the "
                           f"independent_review prompt. {args.scope_note} Opening Latin "
                           f"\u00ab{anchor(first['source_text'])}\u00bb English \u00ab{anchor(first['english'])}\u00bb.")}
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": f"dual_family_review: nemotron ({models['nim']}) + gemini ({models['gemini']})",
        "reviewer_note": "Display only. The two-family gate reads review_provenance.",
        "verdict": "pass" if not fails else "fail",
        "review_provenance": {
            "schema": PROVENANCE_SCHEMA, "adapter": "scripts/dual_family_review.py",
            "adapter_sha256": sha(Path(__file__).read_bytes()),
            "prompt": {"source": "scripts/independent_review.py SYSTEM + USER_TEMPLATE", "sha256": prompt_sha},
            "packet_id": packet["packet_id"], "generated_at": now(), "spend_usd": 0,
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
