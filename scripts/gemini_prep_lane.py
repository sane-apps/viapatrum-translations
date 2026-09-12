#!/usr/bin/env python3
"""Optional Gemini Flash-Lite prep / checker-C lane for Fathers.

Writes ONLY under outputs/gemini-prep/<stamp>/. Never touches live
jeremiah_english.json, never marks claims prepped/done, never calls
ai_promote. CF Workers AI + NVIDIA stay the primary overnight lanes.

  source ~/.config/nv/env   # GEMINI_API_KEY
  python3 scripts/gemini_prep_lane.py --sections 6.1,7.3
  python3 scripts/gemini_prep_lane.py --claim jer-h6
  python3 scripts/gemini_prep_lane.py --checker-c --sections 6.1
  python3 scripts/gemini_prep_lane.py --sections 6.1 --latin-sample

Enable for overnight (still artifact-only):
  FATHERS_GEMINI_PREP=1  or  --enable-gemini on overnight_quota.py
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
sys.path.insert(0, str(ROOT / "scripts"))

from ai_promote import parse_claim_row, sections_from_slice  # noqa: E402
from llm_bakeoff import PREP_SYS, extract_json, load_fixture, user_prompt  # noqa: E402
from llm_lane_config import (  # noqa: E402
    as_list,
    gemini_enabled,
    load_lane_config,
)

DEFAULT_OUT_ROOT = ROOT / "outputs" / "gemini-prep"
API = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)

PREP_LATIN = """You make a crib of early Christian Latin. You are NOT a literary translator.

You may use ONLY the locked Latin paragraphs given. Do not use ANF, NPNF, FOTC,
web English, or memory of modern translations.

Return ONLY valid JSON (no markdown fences):
{{
  "section": "{section}",
  "pass_a_gloss": "literal English gloss, clause by clause; ugly is fine",
  "lemmas": [{{"form": "form as printed", "lemma": "…", "gloss": "…"}}],
  "ocr_flags": ["garbled word, empty slot, or gap you see"],
  "scripture_guesses": [{{"latin_snip": "quoted Latin", "maybe": "Ezek 18:23"}}]
}}

Rules:
- Do NOT write reading English or Pass B.
- Do NOT invent missing Latin. If the print looks gapped, dotted, or junk, put it in ocr_flags.
- At most 8 lemmas, and only load-bearing nouns/verbs. Do not lemma articles, et, pronouns, or prepositions.
- Use the form as printed even if it looks wrong; note suspicion in ocr_flags.
- Keep pass_a_gloss under ~800 characters. Prefer complete clauses over covering every line.
- scripture_guesses are guesses from quotation shape. Quote the Latin snip. Skip if unsure. Max 4 guesses.
"""

CHECKER_C = """You are checker C: an independent QA pass on an early Christian translation draft.

You may use ONLY the locked source text given plus the draft Pass A / Pass B.
Do not consult ANF/NPNF/web memory as authority. Flag invention vs source.

Return ONLY valid JSON (no markdown fences):
{{
  "section": "{section}",
  "verdict": "ok" | "needs_fix" | "reject",
  "invention_flags": ["phrase that looks invented or unsupported"],
  "omission_flags": ["important source sense missing from Pass B"],
  "anf_smell_flags": ["archaic or ANF-like wording"],
  "ocr_or_source_flags": ["source print issues relevant to the draft"],
  "notes": "≤400 chars; concrete, not vibes"
}}
"""


def score_prep(obj, raw, section: str) -> dict:
    checks: dict[str, bool] = {}
    notes: list[str] = []
    if not obj:
        return {"ok": False, "checks": {"parse_json": False}, "notes": ["no JSON"]}
    checks["parse_json"] = True
    checks["has_section"] = str(obj.get("section", "")) == section
    pa = str(obj.get("pass_a_gloss") or "").strip()
    checks["has_pass_a"] = len(pa) >= 40
    lemmas = obj.get("lemmas") if isinstance(obj.get("lemmas"), list) else []
    checks["lemmas_list"] = isinstance(obj.get("lemmas"), list)
    checks["lemmas_max8"] = len(lemmas) <= 8
    eng = obj.get("english") or obj.get("pass_b_english")
    checks["no_pass_b_field"] = not eng
    smell = re.search(
        r"(?i)\b(thou|thee|thy|hast|doth|brethren,?\s+beloved|Ante-Nicene)\b",
        pa,
    )
    checks["no_archaic_anf_smell"] = smell is None
    if smell:
        notes.append(f"archaic/ANF smell: {smell.group(0)}")
    fence = "```"
    payload = json.dumps(obj, ensure_ascii=False)
    checks["no_fence_leak"] = fence not in payload
    if fence in (raw or "") and checks["no_fence_leak"]:
        notes.append("markdown fence wrapper stripped")
    checks["pass_a_bounded"] = len(pa) <= 1200
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "notes": notes,
        "lemma_count": len(lemmas),
        "pass_a_len": len(pa),
    }


def gemini_call(model: str, key: str, system: str, user: str, max_output: int = 2048) -> dict:
    url = API.format(model=model, key=key)
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_output,
            "responseMimeType": "application/json",
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
        ms = int((time.time() - t0) * 1000)
        parts = (
            ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts")
            or []
        )
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        return {
            "ok": True,
            "raw": text,
            "ms": ms,
            "model": model,
            "usage": data.get("usageMetadata"),
        }
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "replace")[:800]
        return {
            "ok": False,
            "error": f"HTTP {e.code}",
            "body": err,
            "ms": int((time.time() - t0) * 1000),
            "model": model,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "ms": int((time.time() - t0) * 1000),
            "model": model,
        }


def call_with_failover(models: list[str], key: str, system: str, user: str) -> dict:
    last: dict = {"ok": False, "error": "no_models"}
    for i, model in enumerate(models):
        r = gemini_call(model, key, system, user)
        if r.get("ok"):
            if i:
                r["failover_from"] = models[0]
            return r
        last = r
        blob = str(r.get("error", "")) + str(r.get("body", ""))
        if "429" in blob or "RESOURCE_EXHAUSTED" in blob:
            time.sleep(2)
            continue
        # Non-quota failures: still try failover once, then stop.
        if i + 1 < len(models):
            time.sleep(0.5)
            continue
        break
    return last


def load_latin_tertullian() -> dict:
    just = json.loads(
        (
            ROOT
            / "books/ante-nicene-topics/reviews/justifications/tertullian_paenitentia_4.json"
        ).read_text(encoding="utf-8")
    )
    latin = just.get("source_text") or ""
    return {
        "section": "tertullian_paenitentia_4",
        "language": "lat",
        "latin": [latin],
        "locus": (just.get("edition") or {}).get("locus"),
    }


def latin_user(fix: dict) -> str:
    return (
        f"Section {fix['section']} ({fix.get('locus')}).\n"
        f"Locked Latin:\n{fix['latin'][0]}\n\n"
        "Produce the JSON now."
    )


def resolve_sections(args: argparse.Namespace) -> list[str]:
    sections: list[str] = []
    if args.claim:
        row = parse_claim_row(args.claim)
        sections.extend(sections_from_slice(row.get("Slice (sections)") or ""))
    if args.sections:
        for part in args.sections.split(","):
            s = part.strip()
            if s and s not in sections:
                sections.append(s)
    if not sections and not args.latin_sample and not args.checker_c:
        sections = ["6.1"]
    return sections


def load_justification(section: str) -> dict | None:
    h, _, s = section.partition(".")
    if not s:
        return None
    path = ROOT / "books/origen-jeremiah-samuel/reviews/justifications" / f"jeremiah_{h}_{s}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_prep(
    section: str,
    *,
    models: list[str],
    key: str,
    out: Path,
    language: str = "grc",
) -> dict:
    if language == "lat":
        fix = load_latin_tertullian()
        section = fix["section"]
        sys_msg = PREP_LATIN.format(section=section)
        user = latin_user(fix)
    else:
        fix = load_fixture(section)
        sys_msg = PREP_SYS.format(section=section)
        user = user_prompt(fix)
    r = call_with_failover(models, key, sys_msg, user)
    obj = extract_json(r.get("raw") or "") if r.get("ok") else None
    sc = score_prep(obj, r.get("raw") or "", section)
    entry = {
        "section": section,
        "language": language,
        "lane": "gemini",
        "role": "prep",
        "promote": False,
        "call": {
            k: r.get(k)
            for k in ("ok", "error", "ms", "model", "failover_from", "usage")
        },
        "score": sc,
        "obj": obj,
        "raw_preview": (r.get("raw") or "")[:500],
        "error_body": r.get("body"),
    }
    safe = section.replace(".", "_")
    (out / f"prep_{safe}.json").write_text(
        json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return entry


def run_checker_c(
    section: str,
    *,
    models: list[str],
    key: str,
    out: Path,
) -> dict:
    just = load_justification(section)
    if not just:
        entry = {
            "section": section,
            "ok": False,
            "error": "justification_missing",
            "promote": False,
        }
        (out / f"checker_c_{section.replace('.', '_')}.json").write_text(
            json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return entry
    fix = load_fixture(section)
    paras = "\n\n".join(f"[p{i+1}]\n{p}" for i, p in enumerate(fix["greek"]))
    pb = just.get("pass_b_english") or []
    pb_txt = "\n".join(str(x) for x in pb) if isinstance(pb, list) else str(pb)
    user_c = (
        f"Section {section}.\nLocked Greek:\n{paras}\n\n"
        f"Draft Pass A:\n{just.get('pass_a_gloss')}\n\n"
        f"Draft Pass B:\n{pb_txt}\n\n"
        "Produce the checker JSON now."
    )
    rc = call_with_failover(models, key, CHECKER_C.format(section=section), user_c)
    obj_c = extract_json(rc.get("raw") or "") if rc.get("ok") else None
    entry = {
        "section": section,
        "lane": "gemini",
        "role": "checker_c",
        "promote": False,
        "confidence_of_draft": just.get("confidence"),
        "call": {
            k: rc.get(k)
            for k in ("ok", "error", "ms", "model", "failover_from", "usage")
        },
        "obj": obj_c,
        "raw_preview": (rc.get("raw") or "")[:600],
        "error_body": rc.get("body"),
    }
    (out / f"checker_c_{section.replace('.', '_')}.json").write_text(
        json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return entry


def gemini_models_from_cfg(cfg: dict) -> tuple[list[str], list[str]]:
    lane = (cfg.get("lanes") or {}).get("gemini") or {}
    prep = as_list(lane.get("prep")) or ["gemini-3.5-flash-lite"]
    failover = as_list(lane.get("prep_failover")) or [
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
    ]
    # Dedupe while preserving order: primary then failover.
    seen: set[str] = set()
    models: list[str] = []
    for m in prep + failover:
        if m not in seen:
            seen.add(m)
            models.append(m)
    checker = as_list(lane.get("checker_c")) or [models[0]]
    return models, checker


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Gemini Flash-Lite prep/QA — artifact-only, never promotes."
    )
    ap.add_argument("--sections", default="", help="Comma list, e.g. 6.1,7.3")
    ap.add_argument("--claim", default="", help="Claim id (Jeremiah slice → sections)")
    ap.add_argument(
        "--prep",
        action="store_true",
        help="Run prep cribs (default when --checker-c is omitted).",
    )
    ap.add_argument(
        "--checker-c",
        action="store_true",
        help="Run checker-C on already-drafted justifications (no promote).",
    )
    ap.add_argument(
        "--latin-sample",
        action="store_true",
        help="Also crib Tertullian De Paenitentia 4 (Latin sample).",
    )
    ap.add_argument("--config", default="")
    ap.add_argument(
        "--out-root",
        default="",
        help="Override artifact root (default outputs/gemini-prep).",
    )
    ap.add_argument(
        "--require-enabled",
        action="store_true",
        help="Exit 0 without work unless FATHERS_GEMINI_PREP / config / --force.",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Run even when lane config enabled=false (direct CLI default).",
    )
    ap.add_argument("--sleep", type=float, default=1.2, help="Pause between calls")
    args = ap.parse_args()

    cfg = load_lane_config(args.config or None)
    # Direct CLI is an explicit enable; overnight uses --require-enabled.
    if args.require_enabled and not gemini_enabled(cfg, force=args.force):
        print(
            "Gemini lane disabled (set FATHERS_GEMINI_PREP=1, "
            "lanes.gemini.enabled=true, or pass --force).",
            flush=True,
        )
        return 0

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    models, checker_models = gemini_models_from_cfg(cfg)
    lane = (cfg.get("lanes") or {}).get("gemini") or {}
    out_root = Path(args.out_root) if args.out_root else (
        ROOT / str(lane.get("artifact_root") or "outputs/gemini-prep")
    )
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_root / stamp
    out.mkdir(parents=True, exist_ok=True)

    receipt: dict = {
        "stamp": stamp,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lane": "gemini",
        "role": "prep_qa_only",
        "auto_promote": False,
        "models": models,
        "checker_c_models": checker_models,
        "key_present": bool(key),
        "sections": [],
        "checker_c": [],
        "note": "Artifacts only — never promote Gemini drafts to live Pass B / ship.",
    }

    if not key:
        receipt["error"] = "GEMINI_API_KEY missing"
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2), flush=True)
        return 2

    sections = resolve_sections(args)
    # Modes: prep (default), checker-c only, or both when --prep + --checker-c.
    want_checker = bool(args.checker_c)
    want_prep = bool(args.prep) or (not want_checker)
    if want_checker and not sections:
        sections = ["6.1"]

    if want_prep:
        for sec in sections:
            entry = run_prep(sec, models=models, key=key, out=out, language="grc")
            receipt["sections"].append(
                {k: entry[k] for k in ("section", "language", "call", "score")}
            )
            print(
                "PREP",
                sec,
                entry["call"].get("ok"),
                (entry.get("score") or {}).get("ok"),
                entry["call"].get("error"),
                flush=True,
            )
            time.sleep(args.sleep)
        if args.latin_sample:
            entry = run_prep(
                "tertullian_paenitentia_4",
                models=models,
                key=key,
                out=out,
                language="lat",
            )
            receipt["sections"].append(
                {k: entry[k] for k in ("section", "language", "call", "score")}
            )
            print(
                "PREP latin",
                entry["call"].get("ok"),
                (entry.get("score") or {}).get("ok"),
                entry["call"].get("error"),
                flush=True,
            )

    if want_checker:
        for sec in sections:
            entry = run_checker_c(sec, models=checker_models, key=key, out=out)
            receipt["checker_c"].append(
                {
                    "section": entry.get("section"),
                    "call": entry.get("call"),
                    "verdict": (entry.get("obj") or {}).get("verdict"),
                    "error": entry.get("error"),
                }
            )
            print(
                "CHECKER_C",
                sec,
                (entry.get("call") or {}).get("ok"),
                (entry.get("obj") or {}).get("verdict"),
                entry.get("error") or (entry.get("call") or {}).get("error"),
                flush=True,
            )
            time.sleep(args.sleep)

    receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
    ok_n = sum(1 for s in receipt["sections"] if (s.get("score") or {}).get("ok"))
    receipt["summary"] = {
        "prep_ok": ok_n,
        "prep_total": len(receipt["sections"]),
        "checker_c_n": len(receipt["checker_c"]),
        "out": str(out),
        "any_quota_error": any(
            "429" in str(s.get("call")) for s in receipt["sections"]
        )
        or any("429" in str(c.get("call")) for c in receipt["checker_c"]),
    }
    (out / "receipt.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("OUT", out, flush=True)
    print(json.dumps(receipt["summary"], indent=2), flush=True)
    if receipt["sections"]:
        return 0 if ok_n >= max(1, (len(receipt["sections"]) + 1) // 2) else 1
    if receipt["checker_c"]:
        return 0 if any((c.get("call") or {}).get("ok") for c in receipt["checker_c"]) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
