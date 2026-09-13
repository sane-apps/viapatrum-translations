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
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_promote import atomic_text, file_digest, parse_claim_row, require_supported_claim, sections_from_slice
from pipeline.check_pass_ab import check_record  # noqa: E402
from llm_bakeoff import (  # noqa: E402
    DEFAULT_ACCOUNT,
    PREP_SYS,
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
RAW_SOURCE = ROOT / "books/origen-jeremiah-samuel/sources/origeneswerke03orig.pdf"
XML_SOURCE = RAW_SOURCE.parent / "first1k/tlg2042.tlg009.opp-grc1.xml"
SOURCE_MANIFEST = RAW_SOURCE.parent / "manifest.json"
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
    atomic_text(ENG, json.dumps(rows, indent=2, ensure_ascii=False) + "\n")


def justification_data(section: str, obj: dict, agent: str, model: str, fix: dict) -> dict:
    """Preserve supplied evidence; never synthesize choices or claim a lexicon was checked."""
    h, s = section.split(".")
    data = {
        "anf_compare": {"status": "not_checked", "notes": "Machine draft from the supplied Greek; independent review pending."},
        "apparatus": [], "bible_refs": obj.get("bible_refs") or [],
        "checks": {"lemma_constraint": "pending", "placeholders": "pass"},
        "choices": obj.get("choices"), "confidence": "machine_draft",
        "edition": {"id": "gcs6-klostermann-1901", "language": "grc",
                    "locus": fix.get("klostermann") or f"Hom. {section}",
                    "path": fix["raw_source_path"],
                    "sha256": fix["raw_source_sha256"], "checks": fix["raw_checks"]},
        "excerpt_id": f"jeremiah_{h}_{s}", "lemmas": obj.get("lemmas"),
        "pass_a_gloss": obj.get("pass_a_gloss"), "pass_b_english": obj.get("english"),
        "source_text": " ".join(fix["greek"]), "variants": obj.get("variants") or [],
        "source_normalizations": fix.get("ocr_normalizations") or [],
        "reviewer": f"pending-ai-crosscheck:{model}", "draft_agent": agent,
        "draft_model": model, "drafted_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = check_record(data)
    for key, fields in (("choices", ("term", "english", "why")), ("lemmas", ("form", "lemma", "gloss"))):
        for item in data.get(key) or []:
            if not isinstance(item, dict) or any(not isinstance(item.get(f), str) or not item[f].strip() for f in fields):
                errors.append(f"{key}: model must supply real {', '.join(fields)}")
    if errors:
        raise ValueError("Missing draft evidence; retain prep and request a complete draft: " + "; ".join(errors))
    return data


def write_justification(section: str, data: dict) -> Path:
    path = JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json"
    atomic_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path


def write_prep_justification(section: str, obj: dict, agent: str, model: str, fix: dict) -> Path:
    h, s = section.split(".")
    path = JUST_DIR / f"jeremiah_{h}_{s}.json"
    src = fix
    lemmas_in = obj.get("lemmas") or []
    lemmas = []
    for item in lemmas_in:
        if not isinstance(item, dict):
            continue
        lemmas.append(
            {
                "form": item.get("form") or item.get("greek") or "",
                "lemma": item.get("lemma") or "",
                "gloss": item.get("gloss") or "",
                **({"lexica": item["lexica"]} if item.get("lexica") else {}),
            }
        )
    guesses = obj.get("scripture_guesses") if isinstance(obj.get("scripture_guesses"), list) else []
    flags = obj.get("ocr_flags") if isinstance(obj.get("ocr_flags"), list) else []
    greek = src.get("greek") or []
    data = {
        "anf_compare": {
            "notes": "Machine crib only. Not reading English. Not copied from modern English.",
            "status": "no_pd_reference",
        },
        "apparatus": [],
        "bible_refs": [
            {
                "display": str(g.get("maybe") or ""),
                "method": "guess",
                "note": str(g.get("greek_snip") or ""),
            }
            for g in guesses
            if isinstance(g, dict) and (g.get("maybe") or g.get("greek_snip"))
        ],
        "checks": {
            "anf_diverge": "pending",
            "lemma_constraint": "pending",
            "placeholders": "pass",
        },
        "choices": [],
        "confidence": "machine_prep",
        "edition": {
            "id": "gcs6-klostermann-1901",
            "language": "grc",
            "locus": src.get("klostermann") or f"Hom. {section}",
            "path": fix["raw_source_path"],
            "sha256": fix["raw_source_sha256"], "checks": fix["raw_checks"],
        },
        "excerpt_id": f"jeremiah_{h}_{s}",
        "lemmas": lemmas,
        "ocr_flags": [str(x) for x in flags],
        "pass_a_gloss": obj.get("pass_a_gloss") or "",
        "reviewer": f"prep:{model}",
        "draft_agent": agent,
        "draft_model": model,
        "drafted_at": datetime.now(timezone.utc).isoformat(),
        "source_text": " ".join(str(p) for p in greek),
        "source_normalizations": fix.get("ocr_normalizations") or [],
        "variants": [],
    }
    atomic_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path


def salvage_prep_obj(raw: str, section: str) -> dict | None:
    """Keep a truncated crib if at least pass_a_gloss is intact."""
    m = re.search(r'"pass_a_gloss"\s*:\s*"((?:\\.|[^"\\])*)"', raw or "")
    if not m:
        return None
    try:
        gloss = json.loads(f'"{m.group(1)}"')
    except json.JSONDecodeError:
        return None
    if not isinstance(gloss, str) or len(gloss.strip()) < 40:
        return None
    return {
        "section": section,
        "pass_a_gloss": gloss.strip(),
        "lemmas": [],
        "ocr_flags": ["json truncated; salvaged pass_a only"],
        "scripture_guesses": [],
    }


def score_prep(obj: dict | None) -> dict:
    checks = {
        "parse_json": isinstance(obj, dict),
        "has_pass_a": False,
        "has_lemmas": False,
        "ocr_flags_list": False,
    }
    if not isinstance(obj, dict):
        return {"ok": False, "checks": checks}
    a = str(obj.get("pass_a_gloss") or "").strip()
    checks["has_pass_a"] = len(a) >= 40
    # Lemmas help; a long gloss is enough. Truncated JSON often dies on lemmas.
    lemmas = obj.get("lemmas") if isinstance(obj.get("lemmas"), list) else []
    checks["has_lemmas"] = True if len(a) >= 80 else bool(lemmas)
    flags = obj.get("ocr_flags")
    if flags is None:
        obj["ocr_flags"] = []
        checks["ocr_flags_list"] = True
    else:
        checks["ocr_flags_list"] = isinstance(flags, list)
    return {"ok": all(checks.values()), "checks": checks}


def draft_section(
    section: str,
    model: str,
    cf_token: str,
    nv_token: str,
    account: str,
    agent: str,
    max_tokens: int | None = None,
    *,
    prep: bool = False,
) -> dict:
    model = normalize_model(model)
    fix = load_fixture(section)
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    witnesses = []
    for path in dict.fromkeys((RAW_SOURCE, XML_SOURCE)):
        sha = file_digest(path)
        manifest_key = path.relative_to(SOURCE_MANIFEST.parent).as_posix()
        if manifest.get("files", {}).get(manifest_key, {}).get("sha256") != sha:
            return {"ok": False, "section": section, "error": "raw_source_does_not_match_locked_manifest"}
        witnesses.append({"path": path.relative_to(JUST_DIR.parent.parent).as_posix(), "sha256": sha})
    fix["raw_source_path"], fix["raw_source_sha256"] = witnesses[0]["path"], witnesses[0]["sha256"]
    fix["raw_checks"] = witnesses[1:]
    prior = JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json"
    if prep and prior.is_file() and json.loads(prior.read_text()).get("pass_b_english"):
        return {"ok": False, "section": section, "error": "existing_translation_preserved; prep must not overwrite reading-text evidence"}
    sys_msg = PREP_SYS if prep else SYS_TMPL
    messages = [
        {"role": "system", "content": sys_msg.format(section=section)},
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
    if prep and not obj:
        obj = salvage_prep_obj(raw.get("content") or "", section)
    current = load_fixture(section)
    if (current["greek"] != fix["greek"] or current.get("ocr_normalizations") != fix.get("ocr_normalizations")
            or any(file_digest(JUST_DIR.parent.parent / w["path"]) != w["sha256"] for w in witnesses)):
        return {"ok": False, "section": section, "error": "source_changed_during_draft"}
    sc = score_prep(obj) if prep else score(obj, raw["content"], section, source=fix["greek"])
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
    if prep:
        jpath = write_prep_justification(section, obj, agent, model, fix)
        return {
            "ok": True,
            "section": section,
            "prep": True,
            "ms": raw.get("ms"),
            "pt": raw.get("pt"),
            "ct": raw.get("ct"),
            "justification": str(jpath),
            "ocr_flags": obj.get("ocr_flags") or [],
            "checks": sc.get("checks"),
            "max_tokens": max_tokens,
        }
    try:
        evidence = justification_data(section, obj, agent, model, fix)
    except ValueError as exc:
        return {"ok": False, "section": section, "error": "missing_draft_evidence", "detail": str(exc)}
    title = str(obj.get("title") or "").strip()
    english = obj.get("english") if isinstance(obj.get("english"), list) else []
    notes = obj.get("translator_notes") if isinstance(obj.get("translator_notes"), list) else []
    jpath = write_justification(section, evidence)
    upsert_english(section, title, english, notes, fix.get("homily"))
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
    ap.add_argument(
        "--prep",
        action="store_true",
        help="Crib only: Pass A, lemmas, OCR flags, scripture guesses. No reading English.",
    )
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
    require_supported_claim(row)
    claimed_sections = sections_from_slice(row.get("Slice (sections)") or "")
    if args.section and not set(args.section) <= set(claimed_sections):
        raise SystemExit("Requested sections are outside the claim; refusing writes")
    sections = args.section or claimed_sections
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        wall = int(cfg.get("claim_wall_s") or 5400)
    except Exception:  # noqa: BLE001
        wall = 5400
    from fathers_run_lock import install_wall_deadline  # noqa: WPS433

    install_wall_deadline(wall, label=f"draft_claim:{args.claim}", exit_code=4)
    print(
        f"{'Prep' if args.prep else 'Drafting'} {args.claim}: {sections} via {model}",
        flush=True,
    )
    hb = Path.home() / "SaneApps/outputs/fathers-overnight/heartbeat"
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text(f"{args.claim}\n", encoding="utf-8")

    failures = 0
    for section in sections:
        print(f"→ {section}", flush=True)
        try:
            hb.write_text(f"{args.claim} {section}\n", encoding="utf-8")
        except OSError:
            pass
        result = None
        attempts = max(1, args.retries + 1)
        override = args.max_tokens or None
        for attempt in range(1, attempts + 1):
            tok = override
            if attempt > 1 and not override:
                tok = 4096 + (attempt - 1) * 1024
            result = draft_section(
                section,
                model,
                cf_token,
                nv_token,
                account,
                args.agent,
                max_tokens=tok,
                prep=args.prep,
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
            extra = (
                f"ocr={result.get('ocr_flags')!r}"
                if result.get("prep")
                else f"title={result.get('title')!r}"
            )
            print(
                f"  PASS  {result.get('ms')}ms  {extra}  "
                f"pt={result.get('pt')} ct={result.get('ct')}",
                flush=True,
            )
        else:
            failures += 1
            print(f"  FAIL  {result}", flush=True)
        time.sleep(0.5)
    # Partial cribs are still useful. Fail the process only if every section failed.
    if args.prep and failures and failures < len(sections):
        print(f"partial prep: {len(sections) - failures}/{len(sections)} sections ok", flush=True)
        return 0
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
