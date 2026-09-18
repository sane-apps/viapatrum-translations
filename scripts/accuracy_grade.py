#!/usr/bin/env python3
"""Grade accuracy_packet.json via the free Gemini prep/QA lane.

Artifact-only: reads outputs/accuracy_packet.json, writes
outputs/accuracy_grades.json. Never touches translations/, never promotes.

Rubric (charter fidelity standard):
  faithful    - English says what the source says; restructuring OK.
  minor-gloss - small added connective/interpretive gloss, claim unchanged.
  distorts    - meaning changed (wrong subject, negation/number error,
                omission that changes the claim).
  invented    - substantive claims with no basis in the source passage.
Brevity/condensation is not infidelity: judge what the English DOES say.

Usage:
  source ~/.config/nv/env   # GEMINI_API_KEY
  python3 scripts/accuracy_grade.py [--packet ...] [--out ...] [--batch 4]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gemini_prep_lane import call_with_failover, gemini_models_from_cfg  # noqa: E402
from llm_lane_config import load_lane_config  # noqa: E402

SYSTEM = """You grade English translation fidelity against a locked Greek/Latin source passage. Use ONLY the source text given; never appeal to published translations or memory. Brevity or condensation is NOT infidelity: judge only whether what the English DOES assert matches the source. Return ONLY valid JSON (no markdown fences): a list of {"tip_id": ..., "verdict": "faithful|minor-gloss|distorts|invented", "reason": "one line"} in the same order as the input items."""


def grade_user(items: list[dict]) -> str:
    blocks = []
    for e in items:
        blocks.append(
            f"--- tip_id: {e['tip_id']} | lang: {e['source_lang']} | {e['context']}\n"
            f"SOURCE:\n{e['source_text'][:2200]}\n"
            f"ENGLISH:\n{e['our_english'][:2200]}"
        )
    return "Grade each item:\n\n" + "\n\n".join(blocks)


def parse_grades(raw: str, want: list[str]) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, dict):
        for k in ("grades", "items", "results"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
    assert isinstance(data, list), f"expected list, got {type(data).__name__}"
    out = []
    for g, tip in zip(data, want):
        v = g.get("verdict", "").strip()
        assert v in ("faithful", "minor-gloss", "distorts", "invented"), f"bad verdict {v!r} for {tip}"
        out.append({"tip_id": tip, "verdict": v, "reason": str(g.get("reason", ""))[:300]})
    assert len(out) == len(want), f"got {len(out)} grades for {len(want)} items"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, default=ROOT / "outputs" / "accuracy_packet.json")
    ap.add_argument("--out", type=Path, default=ROOT / "outputs" / "accuracy_grades.json")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--sleep", type=float, default=4.0)
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        env = Path.home() / ".config" / "nv" / "env"
        for line in env.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key:
        print("no GEMINI_API_KEY", flush=True)
        return 2
    cfg = load_lane_config()
    models, _ = gemini_models_from_cfg(cfg)
    print(f"models: {models}", flush=True)

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    items = packet["items"]
    grades: list[dict] = []
    fails = 0
    for i in range(0, len(items), args.batch):
        chunk = items[i : i + args.batch]
        want = [e["tip_id"] for e in chunk]
        ok = False
        for attempt in range(3):
            r = call_with_failover(models, key, SYSTEM, grade_user(chunk))
            if not r.get("ok"):
                print(f"batch {i//args.batch+1} attempt {attempt+1}: {r.get('error')} {str(r.get('body',''))[:100]}", flush=True)
                time.sleep(5)
                continue
            try:
                grades.extend(parse_grades(r["raw"], want))
                ok = True
                print(f"batch {i//args.batch+1}/{((len(items)-1)//args.batch+1)} ok ({r.get('model')}, {r.get('ms')}ms)", flush=True)
                break
            except (ValueError, AssertionError) as ex:
                print(f"batch {i//args.batch+1} parse fail: {ex}", flush=True)
                time.sleep(3)
        if not ok:
            fails += 1
            for tip in want:
                grades.append({"tip_id": tip, "verdict": "UNRESOLVED", "reason": "lane failed after retries"})
        time.sleep(args.sleep)
    result = {
        "audit": "accuracy",
        "seed": packet.get("seed"),
        "packet_generated_utc": packet.get("generated_utc"),
        "model_lane": "gemini prep_qa_only",
        "count": len(grades),
        "grades": grades,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({len(grades)} grades, {fails} failed batches)", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
