#!/usr/bin/env python3
"""Draft Pass A/B for a claim's sections via Workers AI or NVIDIA NIM.

  source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/draft_claim.py --claim jer-h6 --agent overnight
  python3 scripts/draft_claim.py --claim jer-h8 --agent overnight-nv \
    --model nvidia/nemotron-3-super-120b-a12b

Then: python3 scripts/ai_promote.py --claim <id> --agent …
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_promote import parse_claim_row, sections_from_slice  # noqa: E402
from llm_bakeoff import (  # noqa: E402
    DEFAULT_ACCOUNT,
    SYS_TMPL,
    extract_json,
    is_nvidia_model,
    load_fixture,
    normalize_model,
    score,
    user_prompt,
    vendor_call,
)

ENG = ROOT / "books/origen-jeremiah-samuel/translations/jeremiah_english.json"
JUST_DIR = ROOT / "books/origen-jeremiah-samuel/reviews/justifications"
SOURCE = ROOT / "books/origen-jeremiah-samuel/translations/jeremiah_source.json"
DRAFT_DEFAULT = "@cf/qwen/qwen3-30b-a3b-fp8"


def section_sort_key(section: str):
    parts = str(section).split(".")
    return tuple(int(p) if p.isdigit() else p for p in parts)


def upsert_english(section: str, title: str, english: list, notes: list, homily: int | None) -> None:
    rows = json.loads(ENG.read_text(encoding="utf-8"))
    row = {
        "section": section,
        "homily": homily if homily is not None else int(section.split(".")[0]),
        "title": title,
        "english": english,
    }
    if notes:
        row["translator_notes"] = notes
    replaced = False
    for i, existing in enumerate(rows):
        if str(existing.get("section")) == section:
            rows[i] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)
    rows.sort(key=lambda r: section_sort_key(str(r.get("section"))))
    ENG.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_justification(section: str, obj: dict, agent: str, model: str) -> Path:
    h, s = section.split(".")
    path = JUST_DIR / f"jeremiah_{h}_{s}.json"
    src_rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    src = next((r for r in src_rows if str(r.get("section")) == section), {})
    lemmas_in = obj.get("lemmas") or []
    lemmas = []
    for item in lemmas_in:
        if not isinstance(item, dict):
            continue
        lemmas.append(
            {
                "form": item.get("greek") or item.get("form") or "",
                "lemma": item.get("lemma") or item.get("greek") or "",
                "gloss": item.get("gloss") or "",
                "lexica": item.get("lexica") or "LSJ",
            }
        )
    data = {
        "anf_compare": {
            "notes": "No public-domain English of the Greek Jeremiah homilies (FOTC 97 is copyrighted). Draft from locked GCS Greek only; not copied from modern English.",
            "status": "no_pd_reference",
        },
        "apparatus": [],
        "bible_refs": [],
        "checks": {
            "anf_diverge": "pending",
            "lemma_constraint": "pending",
            "placeholders": "pass",
        },
        "choices": [],
        "confidence": "machine_draft",
        "edition": {
            "id": "gcs6-klostermann-1901",
            "language": "grc",
            "locus": src.get("klostermann") or f"Hom. {section}",
            "path": "sources/first1k/tlg2042.tlg009.opp-grc1.xml",
        },
        "excerpt_id": f"jeremiah_{h}_{s}",
        "lemmas": lemmas,
        "pass_a_gloss": obj.get("pass_a_gloss") or "",
        "reviewer": f"pending-ai-crosscheck:{model}",
        "draft_agent": agent,
        "draft_model": model,
        "drafted_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def draft_section(
    section: str,
    model: str,
    cf_token: str,
    nv_token: str,
    account: str,
    agent: str,
    max_tokens: int | None = None,
) -> dict:
    model = normalize_model(model)
    fix = load_fixture(section)
    messages = [
        {"role": "system", "content": SYS_TMPL.format(section=section)},
        {"role": "user", "content": user_prompt(fix)},
    ]
    raw = vendor_call(
        model,
        messages,
        cf_token=cf_token,
        nv_token=nv_token,
        account=account,
        max_tokens=max_tokens,
    )
    if raw.get("error"):
        return {"ok": False, "section": section, "error": raw["error"], "ms": raw.get("ms")}
    obj = extract_json(raw["content"])
    sc = score(obj, raw["content"], section)
    if not sc.get("ok") or not obj:
        return {
            "ok": False,
            "section": section,
            "error": "structural_fail",
            "checks": sc.get("checks"),
            "raw": (raw.get("content") or "")[:2000],
            "ms": raw.get("ms"),
            "max_tokens": max_tokens,
        }
    title = str(obj.get("title") or "").strip()
    english = obj.get("english") if isinstance(obj.get("english"), list) else []
    notes = obj.get("translator_notes") if isinstance(obj.get("translator_notes"), list) else []
    upsert_english(section, title, [str(x) for x in english], [str(x) for x in notes], fix.get("homily"))
    jpath = write_justification(section, obj, agent, model)
    return {
        "ok": True,
        "section": section,
        "title": title,
        "ms": raw.get("ms"),
        "pt": raw.get("pt"),
        "ct": raw.get("ct"),
        "justification": str(jpath),
        "checks": sc.get("checks"),
        "max_tokens": max_tokens,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--model", default=DRAFT_DEFAULT)
    ap.add_argument("--section", action="append", default=[], help="Limit to these sections")
    ap.add_argument("--max-tokens", type=int, default=0, help="Override model profile max_tokens")
    ap.add_argument("--retries", type=int, default=2, help="Retries on structural_fail / API error")
    args = ap.parse_args()

    model = normalize_model(args.model)
    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv_token = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    if is_nvidia_model(model):
        if not nv_token:
            raise SystemExit("Need NV_API_KEY for NVIDIA draft models")
    elif not cf_token:
        raise SystemExit("Need CF_TOKEN / CLOUDFLARE_API_TOKEN")

    row = parse_claim_row(args.claim)
    sections = args.section or sections_from_slice(row.get("Slice (sections)") or "")
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        wall = int(cfg.get("claim_wall_s") or 5400)
    except Exception:  # noqa: BLE001
        wall = 5400
    from fathers_run_lock import install_wall_deadline  # noqa: WPS433

    install_wall_deadline(wall, label=f"draft_claim:{args.claim}", exit_code=4)
    print(f"Drafting {args.claim}: {sections} via {model}", flush=True)

    failures = 0
    for section in sections:
        print(f"→ {section}", flush=True)
        result = None
        attempts = max(1, args.retries + 1)
        override = args.max_tokens or None
        for attempt in range(1, attempts + 1):
            tok = override
            if attempt > 1 and not override:
                tok = 4096 + (attempt - 1) * 1024
            result = draft_section(
                section, model, cf_token, nv_token, account, args.agent, max_tokens=tok
            )
            if result.get("ok"):
                break
            if attempt < attempts:
                print(
                    f"  retry {attempt}/{attempts - 1} after {result.get('error')} "
                    f"(max_tokens={result.get('max_tokens')})",
                    flush=True,
                )
                time.sleep(1.0)
        if result and result.get("ok"):
            print(
                f"  PASS  {result.get('ms')}ms  title={result.get('title')!r}  "
                f"pt={result.get('pt')} ct={result.get('ct')}",
                flush=True,
            )
        else:
            failures += 1
            print(f"  FAIL  {result}", flush=True)
        time.sleep(0.5)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
