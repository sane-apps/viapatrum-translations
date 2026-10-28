#!/usr/bin/env python3
"""Muse-only review adapter: blind-gloss critic receipts for the QA gate.

Writes a `review-provenance-muse-v1` receipt for a translation-audit-v1
packet (see pipeline/verify_translation_qa.py). Per selected section:

  1. blind-gloss call: a fresh Muse (via the GUI-session queue runner,
     scripts/muse_client.py) glosses the locked source alone.
  2. compare call: the same critic, given its gloss + source + English,
     returns the seven semantic checks, quoted evidence, and a verdict.
  3. research leg: --research JSON supplies the recorded lexicon/grammar
     lookup for every section; the gate refuses a receipt without it.

This lane replaces the two-family rule for Muse drafts only (owner
2026-10-18, docs/AI_CROSSCHECK.md). It never claims two model families.

  python3 scripts/muse_review.py --packet P.packet.json \
      --receipt-out P.review.json --research research.json [--effort medium]

Exit: 0 receipt written and passing; 1 receipt written with fails;
2 usage/parse error (no receipt); 3 muse runner unavailable (no receipt).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from pipeline.verify_translation_qa import (  # noqa: E402
    MUSE_MODEL_ID, MUSE_PROVENANCE_SCHEMA, SEMANTIC_CHECKS,
)

STAGE1_PROMPT = """You are a philologist. Gloss the locked source below clause by clause, from the source alone. You have not seen any translation; invent nothing. A missing or damaged stretch is missing: say so, never supply it.

Source ({lang}), {n} paragraph(s):
{source}

Return ONE JSON object only:
{{"gloss": "your clause-by-clause literal English gloss", "lemmas": [{{"form": "as printed", "lemma": "dictionary form", "gloss": "sense here"}}], "scripture": [{{"greek_or_latin": "quoted source words", "maybe": "Book ch:v"}}], "gaps": ["gap or damage you see"], "uncertainties": ["construction you are unsure of, or empty list"]}}"""

STAGE2_PROMPT = """You are a translation critic. Your own blind gloss of this source was:
{gloss}

Source ({lang}), {n} paragraph(s):
{source}

English, {m} paragraph(s):
{english}

Compare the English clause by clause against your gloss and the source. Judge only major meaning: added claim, dropped clause, flipped negation/agency/modality/doctrine, wrong Scripture target, filled lacuna, calque that breaks sense. Style alone is not a defect. Do not repeat these instructions or the schema; return only the one JSON object.

Return ONE JSON object only:
{{"verdict": "pass" or "fail", "checks": {{"source_identity": true, "completeness": true, "negation": true, "agency": true, "modality": true, "doctrine": true, "scripture": true}}, "uncertainties": [], "covered_source_paragraphs": [1], "flags": [{{"source": "exact source words", "english": "exact English words", "problem": "what is wrong"}}], "notes": "evidence: quote at least 25 characters of the source and at least 25 characters of the English, exactly as written"}}"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_answer(answer: str) -> dict | None:
    """Parse the model's JSON verdict/gloss. Models sometimes echo the
    prompt's schema example beside the real object; scan every '{' and
    prefer the object carrying the verdict/gloss key."""
    if not answer:
        return None
    decoder = json.JSONDecoder()
    candidates = []
    for i, ch in enumerate(answer):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(answer[i:])
        except ValueError:
            continue
        if isinstance(obj, dict):
            candidates.append(obj)
    for obj in reversed(candidates):
        if "verdict" in obj or "gloss" in obj:
            return obj
    return candidates[-1] if candidates else None


def _flat(value) -> str:
    if isinstance(value, (list, tuple)):
        return " ".join(_flat(v) for v in value)
    return " ".join(str(value or "").split())


def _anchor(value, n: int = 60) -> str:
    return _flat(value)[:n]


def normalize_research(raw) -> dict[str, list[dict]]:
    """Accept {section: [entries]} or a flat list of entries with section."""
    out: dict[str, list[dict]] = {}
    if isinstance(raw, dict):
        for sid, entries in raw.items():
            if isinstance(entries, list):
                out[str(sid)] = [e for e in entries if isinstance(e, dict)]
    elif isinstance(raw, list):
        for e in raw:
            if isinstance(e, dict) and e.get("section") is not None:
                out.setdefault(str(e["section"]), []).append(e)
    return out


def build_receipt(packet: dict, research: dict[str, list[dict]], ask,
                  effort: str = "medium", timeout: int = 1500) -> tuple[dict, list[str]]:
    """Run the two critic calls per section. `ask` is muse_client.ask-shaped.
    Returns (receipt, hard_errors); hard errors mean no valid receipt."""
    items = packet.get("sections") or []
    if not items:
        return {}, ["packet has no selected sections"]
    lanes = {role: [] for role in ("blind-gloss", "compare")}
    reviews, hard = [], []
    for item in items:
        sid = str(item["section"])
        src = item.get("source_text") or []
        eng = item.get("english") or []
        lang = "Latin" if re.search(r"\b(et|est|non|qui|quod)\b", _flat(src)) else "Greek"
        base = {"section": sid, "source_sha256": item.get("source_sha256"),
                "english_sha256": item.get("english_sha256"),
                "response_model": MUSE_MODEL_ID}
        # Stage 1: blind gloss (source only).
        res1 = ask(STAGE1_PROMPT.format(lang=lang, n=len(src), source="\n".join(src)),
                   effort=effort, timeout=timeout, tag=f"muse-gloss-{sid}")
        if res1.get("error"):
            hard.append(f"{sid}: blind-gloss call failed: {res1['error']}")
            continue
        p1 = parse_answer(str(res1.get("answer") or ""))
        gloss = str((p1 or {}).get("gloss") or "")
        unc1 = list((p1 or {}).get("uncertainties") or [])
        if not gloss:
            unc1.append("blind gloss unparsed or empty")
        lanes["blind-gloss"].append({**base, "response_id": res1.get("id"),
                                     "started_at": res1.get("started_at"), "finished_at": res1.get("finished_at") or now(),
                                     "verdict": "pass" if gloss and not unc1 else "fail",
                                     "uncertainties": unc1,
                                     "usage": {"prompt_tokens": 0, "completion_tokens": 0}})
        # Stage 2: compare (gloss + source + English).
        res2 = ask(STAGE2_PROMPT.format(gloss=gloss or "(no gloss)", lang=lang, n=len(src),
                                        source="\n".join(src), m=len(eng), english="\n".join(eng)),
                   effort=effort, timeout=timeout, tag=f"muse-compare-{sid}")
        if res2.get("error"):
            hard.append(f"{sid}: compare call failed: {res2['error']}")
            continue
        p2 = parse_answer(str(res2.get("answer") or ""))
        checks_in = (p2 or {}).get("checks") or {}
        checks = {k: checks_in.get(k) is True for k in SEMANTIC_CHECKS}
        unc2 = list((p2 or {}).get("uncertainties") or [])
        verdict = "pass" if (p2 and p2.get("verdict") == "pass" and all(checks.values()) and not unc2) else "fail"
        if not p2:
            unc2.append("compare answer unparsed")
        lanes["compare"].append({**base, "response_id": res2.get("id"),
                                 "started_at": res2.get("started_at"), "finished_at": res2.get("finished_at") or now(),
                                 "verdict": verdict, "uncertainties": unc2,
                                 "usage": {"prompt_tokens": 0, "completion_tokens": 0}})
        entries = research.get(sid) or []
        adjudications = []
        if unc1 and entries:
            adjudications.append({"model": MUSE_MODEL_ID,
                                  "resolution": "Blind-gloss uncertainty covered by recorded research: "
                                                + "; ".join(str(e.get("item")) for e in entries)})
        notes = (f"[muse compare {MUSE_MODEL_ID}] verdict={verdict}; "
                 f"model notes: {str((p2 or {}).get('notes') or '')}\n"
                 f"Source quote (anchor from packet): \u00ab{_anchor(src)}\u00bb\n"
                 f"English quote (anchor from packet): \u00ab{_anchor(eng)}\u00bb")
        review = {"section": sid, "verdict": verdict, "checks": checks,
                  "uncertainties": [] if verdict == "pass" else (unc2 or ["compare verdict fail"]),
                  "covered_source_paragraphs": list(range(1, len(src) + 1)),
                  "notes": notes,
                  "lanes": [{"model": MUSE_MODEL_ID, "family": "muse", "verdict": verdict,
                             "response_id": res2.get("id")}]}
        if adjudications:
            review["adjudications"] = adjudications
        reviews.append(review)
    if hard:
        return {}, hard
    prov_lanes = [{"role": role, "provider": "muse-queue", "model": MUSE_MODEL_ID,
                   "family": "muse", "call_count": len(calls), "calls": calls}
                  for role, calls in lanes.items()]
    selected = {str(it["section"]) for it in items}
    flat_research = [{**e, "section": sid} for sid, entries in research.items()
                     if sid in selected for e in entries]
    receipt = {"packet_id": packet.get("packet_id"),
               "reviewer": "muse-only: drafter+blind-gloss-critic+research",
               "review_provenance": {"schema": MUSE_PROVENANCE_SCHEMA,
                                     "lanes": prov_lanes, "research": flat_research},
               "verdict": "pass" if reviews and all(r["verdict"] == "pass" for r in reviews) else "fail",
               "reviews": reviews}
    return receipt, []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--receipt-out", type=Path, required=True)
    ap.add_argument("--research", type=Path, required=True,
                    help="JSON {section: [{item, source, sense_relied_on}]} recorded before adjudication")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--timeout", type=int, default=1500)
    args = ap.parse_args(argv)
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    research = normalize_research(json.loads(args.research.read_text(encoding="utf-8")))
    missing = [str(s["section"]) for s in packet.get("sections") or [] if not research.get(str(s["section"]))]
    if missing:
        print(f"FAIL: research missing for sections {missing}; record the lookup before review")
        return 2
    from muse_client import ask, runner_alive  # lazy: queue runner only when reviewing
    if not runner_alive():
        print("FAIL: muse runner not alive (no heartbeat); receipt not written")
        return 3
    receipt, hard = build_receipt(packet, research, ask, args.effort, args.timeout)
    if hard:
        for e in hard:
            print("FAIL:", e)
        return 3
    args.receipt_out.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"receipt {args.receipt_out} verdict={receipt['verdict']} sections={len(receipt['reviews'])}")
    return 0 if receipt["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
