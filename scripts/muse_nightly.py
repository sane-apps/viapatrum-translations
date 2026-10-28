#!/usr/bin/env python3
"""Muse-only nightly lane: draft + blind-gloss critic + research + gate.

Reads outputs/muse-lane/queue.json (items prepared by the orchestrator):
  {"english": "books/<slug>/translations/<stem>_english.json",
   "source": "books/<slug>/translations/<stem>_source.json",
   "raw": "books/<slug>/sources/<witness>.pdf",
   "identity": {"author": ..., "work": ..., "edition": ...,
                "locus_scheme": ..., "source_url": ...},
   "section": "6.1",
   "research": [{"item": ..., "source": ..., "sense_relied_on": ...}]}

Per item (default one per run): drafts Pass A/B through the Muse queue
runner, scores it (llm_bakeoff scorer + check_pass_ab), builds an audit
packet on a sandbox copy, reviews it with scripts/muse_review.py, and
validates the receipt with pipeline.verify_translation_qa. A passing item
leaves the queue; anything else stays with its status recorded. This job
never writes book files and never ships: the orchestrator promotes a
passing draft into the book and its justification in session.

  python3 scripts/muse_nightly.py [--max-sections 1] [--queue PATH]

Exit: 0 done or queue empty; 1 an item failed its gate; 3 muse runner down.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from llm_bakeoff import SYS_TMPL, extract_json, score  # noqa: E402
from muse_review import build_receipt, normalize_research  # noqa: E402
from pipeline.check_pass_ab import check_record  # noqa: E402
from pipeline.verify_translation_qa import (  # noqa: E402
    make_audit_packet, source_paragraphs, validate_audit_receipt,
)

QUEUE_DEFAULT = ROOT / "outputs/muse-lane/queue.json"
OUT_ROOT = ROOT / "outputs/muse-lane"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rows(data) -> list[dict]:
    return [data] if isinstance(data, dict) else list(data)


def _key(row: dict) -> str:
    return str(row.get("section") or row.get("location") or row.get("codex") or row.get("id"))


def process_item(item: dict, ask, run_dir: Path) -> dict:
    """One queue item end to end. Returns a status record; writes run files."""
    sid = str(item["section"])
    eng_path, src_path = ROOT / item["english"], ROOT / item["source"]
    english_rows = _rows(_load(eng_path))
    source_rows = _rows(_load(src_path))
    src_row = next((r for r in source_rows if _key(r) == sid), None)
    if src_row is None:
        return {"section": sid, "status": "no-source-row"}
    paras = source_paragraphs(src_row)
    status: dict = {"section": sid, "started_at": now()}
    run_dir.mkdir(parents=True, exist_ok=True)
    # 1. Draft (unattended muse, locked source only).
    paras_text = "\n\n".join(f"[p{i + 1}]\n{p}" for i, p in enumerate(paras))
    prompt = SYS_TMPL.format(section=sid) + f"\n\nSection {sid}.\nLocked source:\n{paras_text}\n\nProduce the JSON now."
    res = ask(prompt, effort="medium", timeout=900, tag=f"nightly-draft-{sid}")
    if res.get("error"):
        return {**status, "status": "runner-error", "error": str(res["error"])[:300]}
    draft = extract_json(str(res.get("answer") or ""))
    if not draft or not draft.get("english"):
        return {**status, "status": "draft-unparsed"}
    (run_dir / "draft.json").write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scored = score(draft, str(res.get("answer") or ""), sid, paras)
    justification = {"excerpt_id": f"muse-nightly-{sid}", "source_text": " ".join(paras),
                     "pass_a_gloss": draft.get("pass_a_gloss"), "pass_b_english": draft.get("english"),
                     "lemmas": draft.get("lemmas") or [], "choices": draft.get("choices") or [],
                     "edition": {"id": "muse-nightly", "language": "grc-or-lat", "locus": sid,
                                 "path": item.get("raw", "")},
                     "confidence": "bench_unreviewed"}
    gate_errors = check_record(justification)
    status["draft_score_ok"] = bool(scored.get("ok"))
    status["pass_ab_errors"] = gate_errors
    if not scored.get("ok") or gate_errors:
        return {**status, "status": "draft-gate-failed"}
    # 2. Sandbox packet: draft English over a copy, never the book file.
    copied = []
    replaced = False
    for row in english_rows:
        row = dict(row)
        if _key(row) == sid:
            row["english"] = draft["english"]
            if draft.get("title"):
                row["title"] = draft["title"]
            replaced = True
        copied.append(row)
    if not replaced:
        copied.append({"section": sid, "english": draft["english"], "title": draft.get("title", "")})
    sandbox_eng = run_dir / "english.json"
    sandbox_eng.write_text(json.dumps(copied, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    packet = make_audit_packet(sandbox_eng, src_path, raw_sources=[ROOT / item["raw"]],
                               seed=20261018, sample_size=5, identity=item["identity"],
                               selected_sections=[sid])
    (run_dir / "packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if packet["structural_errors"]:
        return {**status, "status": "packet-structural-errors", "errors": packet["structural_errors"]}
    # 3. Critic + research + gate.
    research = normalize_research({sid: item.get("research") or []})
    if not research.get(sid):
        return {**status, "status": "needs-research"}
    receipt, hard = build_receipt(packet, research, ask)
    if hard:
        return {**status, "status": "review-error", "errors": hard}
    (run_dir / "review.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = validate_audit_receipt(packet, receipt)
    status["receipt_verdict"] = receipt.get("verdict")
    status["validate_errors"] = errors
    status["pass_b_sha256"] = hashlib.sha256("\n".join(draft["english"]).encode()).hexdigest()
    return {**status, "status": "pass" if receipt.get("verdict") == "pass" and not errors else "review-failed",
            "finished_at": now()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue", type=Path, default=QUEUE_DEFAULT)
    ap.add_argument("--max-sections", type=int, default=4)
    args = ap.parse_args(argv)
    if not args.queue.exists():
        print(f"nothing to do: no queue at {args.queue}")
        return 0
    queue = _load(args.queue)
    if not isinstance(queue, list):
        print("FAIL: queue must be a JSON list")
        return 2
    if not queue:
        print("nothing to do: muse-lane queue empty")
        return 0
    from muse_client import ask, runner_alive  # lazy: only when work exists
    if not runner_alive():
        print("FAIL: muse runner not alive (no heartbeat)")
        return 3
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results, remaining = [], []
    todo = queue[: args.max_sections]
    for item in todo:
        run_dir = OUT_ROOT / stamp / f"{item.get('section')}"
        rec = process_item(item, ask, run_dir)
        rec["run_dir"] = str(run_dir)
        results.append(rec)
        print(f"{rec['section']}: {rec['status']}", flush=True)
        if rec["status"] != "pass":
            remaining.append(item)
    remaining.extend(queue[args.max_sections:])
    args.queue.write_text(json.dumps(remaining, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "last-run.json").write_text(json.dumps(
        {"stamp": stamp, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["status"] == "pass" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
