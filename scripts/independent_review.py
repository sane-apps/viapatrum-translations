#!/usr/bin/env python3
"""Weekly independent re-review: a different model blindly re-verdicts a sample.

Samples recent audit receipts (default: last 7 days), asks a second model for
fresh semantic verdicts, and diffs against the recorded checks. Mismatches are
reported for lane-owner rework; unresolved mismatches re-appear as ESCALATED
until the receipt is corrected or the section re-reviewed.

Writes outputs/independent-review/YYYY-Www.json. Reads tokens from the
environment (NV_API_KEY, CF_TOKEN/CLOUDFLARE_API_TOKEN). Bounded: --sample N
(default 5) sections, one primary call each plus one fallback on error.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from llm_bakeoff import vendor_call  # noqa: E402

CHECKS = ("source_identity", "completeness", "negation", "agency",
          "modality", "doctrine", "scripture")

SYSTEM = ("You are an independent translation auditor. Judge ONLY the given "
          "source paragraphs against the English. Reply with a single JSON "
          "object and no other text.")

USER_TEMPLATE = """Source (%s), %d paragraph(s):
%s

English, %d paragraph(s):
%s

Conventions (do not treat these as defects): parenthetical Scripture
identifications like (Psalm 7:5) are required apparatus, not invented
content; the source may contain OCR noise such as broken word spacing --
read through it; if source corruption makes a clause genuinely ambiguous,
record it in uncertainties instead of failing.

Verdict the English against the source on these checks (true only if fully satisfied):
- source_identity: renders THESE source paragraphs (not another passage/edition)
- completeness: no source clause dropped; no invented additions
- negation: negatives/affirmatives preserved (no flipped polarity)
- agency: subjects/agents preserved (who does what to whom)
- modality: necessity/possibility/commands preserved
- doctrine: no theologically loaded mistranslation
- scripture: Scripture citations rendered and cited correctly

Reply exactly: {"verdict": "pass"|"fail", "checks": {all seven: bool}, "uncertainties": [], "covered_source_paragraphs": [ints], "notes": "concrete evidence quoting the exact English words at issue, 25+ chars"}"""


def para_text(paras) -> list[str]:
    if isinstance(paras, list):
        return [" ".join(p) if isinstance(p, list) else str(p) for p in paras]
    return [str(paras)]


def recent_receipts(since_days: int) -> list[Path]:
    cutoff = time.time() - since_days * 86400
    hits = []
    for path in sorted((ROOT / "books").glob("*/reviews/audit/*.review.json")):
        if path.stat().st_mtime >= cutoff:
            hits.append(path)
    return hits


def sample_sections(files: list[Path], n: int, seed: str):
    rng = random.Random(seed)
    per_book: dict[str, list[tuple]] = {}
    for rpath in files:
        try:
            receipt = json.loads(rpath.read_text())
            packet = json.loads(rpath.with_suffix("").with_name(
                rpath.name.replace(".review.json", ".packet.json")).read_text())
        except (OSError, ValueError):
            continue
        book = rpath.parts[rpath.parts.index("books") + 1]
        packet_reviews = {str(r.get("section")): r for r in receipt.get("reviews", [])}
        items = {s["section"]: s for s in packet.get("sections", [])}
        for sec, item in items.items():
            if str(sec) in packet_reviews:
                per_book.setdefault(book, []).append((sec, item, packet_reviews[str(sec)]))
    books = sorted(per_book)
    rng.shuffle(books)
    for b in books:
        rng.shuffle(per_book[b])
    out, i = [], 0
    while len(out) < n and any(per_book[b][i // len(books):] for b in books):
        for b in books:
            idx = i // len(books)
            if idx < len(per_book[b]) and len(out) < n:
                sec, item, recorded = per_book[b][idx]
                out.append({"book": b, "section": str(sec), "item": item, "recorded": recorded})
        i += 1
    return out


def second_verdict(sample: dict, model: str, fallback: str, env: dict) -> dict:
    item = sample["item"]
    src = para_text(item.get("source_text", []))
    eng = para_text(item.get("english", []))
    lang = "Latin" if re.search(r"\b(et|est|non|qui|quod|Deus)\b", " ".join(src)) else "Greek-or-Latin"
    user = USER_TEMPLATE % (lang, len(src), "\n".join(f"{i + 1}. {p}" for i, p in enumerate(src)),
                            len(eng), "\n".join(f"{i + 1}. {p}" for i, p in enumerate(eng)))
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    last_error = ""
    extra = {"account": env["CF_ACCOUNT"]} if env.get("CF_ACCOUNT") else {}
    for attempt, name in enumerate([model, fallback]):
        if not name or (attempt and name == model):
            continue
        res = vendor_call(name, messages, cf_token=env.get("CF_TOKEN", ""),
                          nv_token=env.get("NV_API_KEY", ""),
                          max_tokens=600, **extra)
        text = (res.get("content") or res.get("text") or res.get("response")
                or res.get("result") or "")
        if res.get("error") or not text:
            last_error = str(res.get("error") or "empty response")
            continue
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            last_error = "unparseable (no JSON object)"
            continue
        try:
            verdict = json.loads(match.group(0))
        except ValueError:
            last_error = "unparseable (bad JSON)"
            continue
        if not isinstance(verdict.get("checks"), dict):
            last_error = "unparseable (no checks)"
            continue
        verdict["_model"] = name
        verdict["_neurons"] = res.get("neurons", 0)
        return {"ok": True, "verdict": verdict}
    return {"ok": False, "error": last_error or "no model available"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly independent re-review sample.")
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--since-days", type=int, default=7)
    ap.add_argument("--seed", default="")
    ap.add_argument("--model", default="nvidia/nemotron-3-super-120b-a12b")
    ap.add_argument("--fallback-model", default="@cf/meta/llama-3.3-70b-instruct-fp8-fast")
    ap.add_argument("--confirm-model", default="@cf/meta/llama-3.3-70b-instruct-fp8-fast")
    args = ap.parse_args()
    week = datetime.now(timezone.utc).strftime("%Y-W%V")
    seed = args.seed or week
    out_dir = ROOT / "outputs" / "independent-review"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = recent_receipts(args.since_days)
    samples = sample_sections(files, args.sample, seed)
    env = {"CF_TOKEN": os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", ""),
           "NV_API_KEY": os.environ.get("NV_API_KEY", ""),
           "CF_ACCOUNT": os.environ.get("CF_ACCOUNT_ID", "")}
    report = {"week": week, "seed": seed, "model": args.model,
              "fallback": args.fallback_model, "confirm_model": args.confirm_model,
              "pool_receipts": len(files),
              "sampled": [], "mismatches": [], "unconfirmed": [], "errors": []}
    for sample in samples:
        entry = {"book": sample["book"], "section": sample["section"]}
        res = second_verdict(sample, args.model, args.fallback_model, env)
        if not res["ok"]:
            entry["outcome"] = "error"
            entry["error"] = res["error"]
            report["errors"].append(entry)
            report["sampled"].append(entry)
            continue
        second = res["verdict"]
        recorded = sample["recorded"]
        entry["model"] = second.pop("_model")
        entry["neurons"] = second.pop("_neurons", 0)
        entry["recorded_verdict"] = recorded.get("verdict")
        entry["second_verdict"] = second.get("verdict")
        diffs = [c for c in CHECKS
                 if bool((recorded.get("checks") or {}).get(c)) != bool(second.get("checks", {}).get(c))]
        entry["check_diffs"] = diffs
        entry["second_notes"] = str(second.get("notes", ""))[:300]
        entry["second_uncertainties"] = second.get("uncertainties", [])
        screen_hit = (second.get("verdict") != recorded.get("verdict") or diffs
                      or second.get("uncertainties"))
        if not screen_hit:
            entry["outcome"] = "agree"
            report["sampled"].append(entry)
            continue
        # Confirm with a different-vendor model before crying wolf.
        confirm = second_verdict(sample, args.confirm_model, "", env)
        if not confirm["ok"]:
            entry["outcome"] = "unconfirmed"
            entry["confirm_error"] = confirm["error"]
            report["unconfirmed"].append(entry)
            report["sampled"].append(entry)
            continue
        confirmer = confirm["verdict"]
        entry["confirm_model"] = confirmer.pop("_model")
        entry["confirm_verdict"] = confirmer.get("verdict")
        entry["confirm_notes"] = str(confirmer.get("notes", ""))[:300]
        c_diffs = [c for c in CHECKS
                   if bool((recorded.get("checks") or {}).get(c))
                   != bool(confirmer.get("checks", {}).get(c))]
        entry["confirm_diffs"] = c_diffs
        if confirmer.get("verdict") == "fail" and second.get("verdict") == "fail" \
                and (set(diffs) & set(c_diffs)):
            entry["outcome"] = "mismatch"
            report["mismatches"].append(entry)
        else:
            entry["outcome"] = "unconfirmed"
            report["unconfirmed"].append(entry)
        report["sampled"].append(entry)

    # Carry-forward: prior mismatches still present? A mismatch clears when any
    # receipt in its book is reworked (newer mtime than the previous report).
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    escalated = []
    prev_reports = sorted(out_dir.glob("*.json"))
    if prev_reports:
        try:
            prev = json.loads(prev_reports[-1].read_text())
        except ValueError:
            prev = {}
        if prev.get("week") != week and prev_reports[-1].name != f"{week}.json":
            try:
                prev_ts = datetime.fromisoformat(prev.get("generated_at", "")).timestamp()
            except ValueError:
                prev_ts = 0.0
            for old in prev.get("mismatches", []) + prev.get("escalated", []):
                key = (old.get("book"), old.get("section"))
                again = [m for m in report["mismatches"]
                         if (m.get("book"), m.get("section")) == key]
                if again:
                    continue
                rfiles = list((ROOT / "books" / (old.get("book") or "__none__")
                               / "reviews" / "audit").glob("*.review.json"))
                reworked = any(f.stat().st_mtime > prev_ts for f in rfiles)
                if not reworked:
                    escalated.append({**old, "outcome": "escalated",
                                      "since": old.get("since", prev.get("week"))})
    report["escalated"] = escalated

    out_path = out_dir / f"{week}.json"
    out_path.write_text(json.dumps(report, indent=1))
    print(f"week={week} pool={len(files)} sampled={len(report['sampled'])} "
          f"mismatches={len(report['mismatches'])} "
          f"unconfirmed={len(report['unconfirmed'])} errors={len(report['errors'])} "
          f"escalated={len(escalated)} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
