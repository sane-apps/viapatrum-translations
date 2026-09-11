#!/usr/bin/env python3
"""Promote a claim to done via structural + multi-model AI cross-check.

No human review gate (owner 2026-09-11). See docs/AI_CROSSCHECK.md.

  source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/ai_promote.py --claim jer-h6 --agent overnight
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from llm_bakeoff import (  # noqa: E402
    DEFAULT_ACCOUNT,
    extract_json,
    is_nvidia_model,
    load_fixture,
    normalize_model,
    score,
    vendor_call,
)
from llm_lane_config import (  # noqa: E402
    as_list,
    is_api_error,
    load_lane_config,
)
from fathers_run_lock import (  # noqa: E402
    acquire_claim,
    acquire_global,
    clear_wall_deadline,
    install_wall_deadline,
    release_all,
)

CLAIMS = ROOT / "docs" / "CLAIMS.md"
OUT = ROOT / "outputs" / "ai-promote"
LOCKS = ROOT / "docs" / "claim-locks"

DRAFT_DEFAULT = "@cf/qwen/qwen3-30b-a3b-fp8"
CHECKER_A_DEFAULT = "@cf/google/gemma-4-26b-a4b-it"
CHECKER_B_DEFAULT = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"

CHECK_SYS = """You are an independent checker for a Greek→English Fathers translation.
You do NOT rewrite the English. You only judge the draft against the locked Greek.

Return ONLY JSON:
{
  "verdict": "pass" | "fail",
  "reasons": ["short bullet", "..."],
  "grounded_in_greek": true/false,
  "pass_b_subset_of_pass_a": true/false,
  "title_is_thought": true/false,
  "anf_or_archaic_smell": true/false
}

Rules:
- Pass A is intentionally a short gloss/summary of the whole section. Do NOT fail
  merely because Pass A compresses or paraphrases. Fail Pass A only if it asserts
  a concrete claim with no support in the Greek.
- To claim Pass B invents sense, you MUST quote the exact Pass B wording from the
  English provided. Never invent English that is not in the draft.
- Fail only on material invention (ideas absent from Greek), ANF/Victorian paste
  (thou/thee/hast, "brethren beloved"), or a title that is only a locus label
  (e.g. "Homily 6.1", "§6.2"). Prefer pass when unsure.
- Small awkward phrasing or literal calque is not a fail if the sense is in the Greek.
- Origen’s own moral inference from the verse (e.g. “those who feel chastisement are
  blessed”) is allowed when the locked Greek argues that point. Do not fail merely
  because the Greek does not use the English word “blessed.”
"""


def parse_claim_row(claim_id: str) -> dict[str, str]:
    text = CLAIMS.read_text(encoding="utf-8")
    in_open = False
    headers: list[str] = []
    for line in text.splitlines():
        if line.startswith("## Open / active claims"):
            in_open = True
            continue
        if in_open and line.startswith("## "):
            break
        if not in_open or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0] == "Claim ID":
            headers = cells
            continue
        if not headers or cells[0].startswith("---"):
            continue
        row = dict(zip(headers, cells))
        if row.get("Claim ID") == claim_id:
            return row
    raise SystemExit(f"Claim {claim_id} not in open table")


def sections_from_slice(slice_text: str) -> list[str]:
    """Parse 'Homily 6 §§6.1–6.3' / '§§5.1–5.6' into section ids."""
    m = re.search(r"§§?\s*([\d.]+)\s*[–-]\s*([\d.]+)", slice_text)
    if not m:
        raise SystemExit(f"Cannot parse slice sections from: {slice_text!r}")
    start, end = m.group(1), m.group(2)
    # Expand only same-homily integer tails: 6.1–6.3 → 6.1,6.2,6.3
    sh, ss = start.split(".")
    eh, es = end.split(".")
    if sh != eh:
        raise SystemExit(f"Cross-homily slice not supported yet: {slice_text}")
    return [f"{sh}.{i}" for i in range(int(ss), int(es) + 1)]


def paths_for_section(section: str) -> tuple[Path, Path]:
    h, s = section.split(".")
    eng = (
        ROOT
        / "books/origen-jeremiah-samuel/translations/jeremiah_english.json"
    )
    just = (
        ROOT
        / "books/origen-jeremiah-samuel/reviews/justifications"
        / f"jeremiah_{h}_{s}.json"
    )
    return eng, just


def load_section_bundle(section: str) -> dict:
    eng_path, just_path = paths_for_section(section)
    rows = json.loads(eng_path.read_text(encoding="utf-8"))
    row = next((r for r in rows if str(r.get("section")) == section), None)
    if not row:
        raise SystemExit(f"Missing english for section {section} in {eng_path}")
    if not just_path.is_file():
        raise SystemExit(f"Missing justification {just_path}")
    just = json.loads(just_path.read_text(encoding="utf-8"))
    greek_fix = load_fixture(section)
    return {
        "section": section,
        "english_row": row,
        "justification": just,
        "greek": greek_fix["greek"],
        "paths": {"english": eng_path, "justification": just_path},
    }


def structural_ok(bundle: dict) -> dict:
    just = bundle["justification"]
    row = bundle["english_row"]
    obj = {
        "section": bundle["section"],
        "title": row.get("title") or row.get("head") or "",
        "pass_a_gloss": just.get("pass_a_gloss") or "",
        "english": row.get("english") or [],
        "lemmas": just.get("lemmas") or [],
        "translator_notes": row.get("translator_notes") or [],
    }
    raw = json.dumps(obj, ensure_ascii=False)
    return score(obj, raw, bundle["section"])


def checker_prompt(bundle: dict) -> list[dict]:
    just = bundle["justification"]
    row = bundle["english_row"]
    greek = "\n\n".join(f"[p{i+1}]\n{p}" for i, p in enumerate(bundle["greek"]))
    user = (
        f"Section {bundle['section']}.\n\nLocked Greek:\n{greek}\n\n"
        f"Pass A gloss:\n{just.get('pass_a_gloss')}\n\n"
        f"Title: {row.get('title') or row.get('head')}\n\n"
        f"Pass B english:\n{json.dumps(row.get('english') or [], ensure_ascii=False)}\n\n"
        "Judge now."
    )
    return [{"role": "system", "content": CHECK_SYS}, {"role": "user", "content": user}]


def run_checker(
    model: str,
    bundle: dict,
    *,
    cf_token: str = "",
    nv_token: str = "",
    account: str = DEFAULT_ACCOUNT,
    retries: int = 2,
) -> dict:
    model = normalize_model(model)
    last: dict = {}
    for attempt in range(1, max(1, retries) + 1):
        raw = vendor_call(
            model,
            checker_prompt(bundle),
            cf_token=cf_token,
            nv_token=nv_token,
            account=account,
            max_tokens=1200,
        )
        if raw.get("error"):
            err = str(raw["error"])
            last = {
                "ok": False,
                "error": err,
                "model": model,
                "ms": raw.get("ms"),
                "api_error": is_api_error(err),
            }
            if "410" in err or "end of life" in err.lower() or "404" in err:
                return last
            if attempt < retries and is_api_error(err):
                time.sleep(min(2.0 * attempt, 6.0))
                continue
            return last
        obj = extract_json(raw.get("content") or "") or {}
        verdict = str(obj.get("verdict") or "").lower()
        reasons = obj.get("reasons") or []
        if not isinstance(reasons, list):
            reasons = [str(reasons)]
        row = bundle.get("english_row") or {}
        just = bundle.get("justification") or {}
        text_blob = " ".join(
            [
                str(row.get("title") or ""),
                str(just.get("pass_a_gloss") or ""),
                " ".join(str(x) for x in (row.get("english") or [])),
            ]
        )
        local_anf = bool(
            re.search(
                r"(?i)\b(thou|thee|thy|hast|doth|brethren,?\s+beloved|Ante-Nicene)\b",
                text_blob,
            )
        )
        smell_fail = bool(obj.get("anf_or_archaic_smell") is True and local_anf)
        ok = verdict == "pass" and not smell_fail
        if obj.get("grounded_in_greek") is False and reasons:
            ok = False
        if obj.get("pass_b_subset_of_pass_a") is False and reasons:
            ok = False
        if obj.get("grounded_in_greek") is False and not reasons:
            ok = False
        title = str(row.get("title") or "")
        if obj.get("title_is_thought") is False:
            if re.search(r"(?i)^(homily\s*)?§?\s*[\d.]+$|^homily\s*\d+(\.\d+)?$", title.strip()):
                ok = False
        return {
            "ok": ok,
            "model": model,
            "ms": raw.get("ms"),
            "parsed": obj,
            "raw": (raw.get("content") or "")[:4000],
            "api_error": False,
        }
    return last or {"ok": False, "error": "checker_failed", "model": model, "api_error": True}


def run_checker_chain(
    models: list[str],
    bundle: dict,
    *,
    cf_token: str = "",
    nv_token: str = "",
    account: str = DEFAULT_ACCOUNT,
    retries_per_model: int = 2,
    draft_model: str = "",
) -> dict:
    """Try models in order. API errors → next model. Content fail stops the chain."""
    draft_model = normalize_model(draft_model)
    tried: list[dict] = []
    for model in models:
        model = normalize_model(model)
        if not model or model == draft_model:
            continue
        print(f"    try {model}", flush=True)
        chk = run_checker(
            model,
            bundle,
            cf_token=cf_token,
            nv_token=nv_token,
            account=account,
            retries=retries_per_model,
        )
        tried.append({k: v for k, v in chk.items() if k != "raw"})
        if chk.get("ok"):
            chk["tried"] = tried
            return chk
        if chk.get("api_error"):
            print(f"      API fail → fallback ({chk.get('error')})", flush=True)
            continue
        chk["tried"] = tried
        return chk
    return {
        "ok": False,
        "error": "all_checker_fallbacks_failed",
        "api_error": True,
        "model": models[-1] if models else "",
        "tried": tried,
        "raw": "",
    }


def mark_claim_done(claim_id: str, agent: str, notes: str) -> None:
    text = CLAIMS.read_text(encoding="utf-8")
    row_re = re.compile(
        rf"^\| {re.escape(claim_id)} \| (?:free|claimed|checking|review) \|.*\|$",
        re.MULTILINE,
    )
    m = row_re.search(text)
    if not m:
        raise SystemExit(f"Open row for {claim_id} not found to mark done")
    old = m.group(0)
    cells = [c.strip() for c in old.strip("|").split("|")]
    slice_txt = cells[3] if len(cells) > 3 else ""
    done_line = (
        f"| {claim_id} | done | {slice_txt} | {date.today().isoformat()} | "
        f"AI cross-check ({agent}); {notes} |"
    )
    text2 = row_re.sub("", text, count=1)
    text2 = re.sub(r"\n{3,}", "\n\n", text2)

    done_header = "## Done / closed"
    if done_header not in text2:
        text2 = (
            text2.rstrip()
            + f"\n\n{done_header}\n\n"
            + "| Claim ID | Status | Slice | Closed | Notes |\n"
            + "|----------|--------|-------|--------|-------|\n"
            + done_line
            + "\n"
        )
    else:
        # Insert after the separator line under Done / closed
        parts = text2.split(done_header, 1)
        head, tail = parts[0], parts[1]
        tlines = tail.splitlines(keepends=True)
        out_tail: list[str] = []
        inserted = False
        for line in tlines:
            out_tail.append(line)
            if not inserted and line.startswith("|---"):
                out_tail.append(done_line + "\n")
                inserted = True
        if not inserted:
            out_tail.append(done_line + "\n")
        text2 = head + done_header + "".join(out_tail)

    CLAIMS.write_text(text2, encoding="utf-8")
    lock = LOCKS / claim_id
    if lock.is_dir():
        for p in lock.iterdir():
            p.unlink()
        try:
            lock.rmdir()
        except OSError:
            pass


def stamp_justifications(sections: list[str], reviewer: str) -> None:
    for section in sections:
        _eng, just_path = paths_for_section(section)
        data = json.loads(just_path.read_text(encoding="utf-8"))
        data["reviewer"] = reviewer
        data["ai_crosscheck_at"] = datetime.now(timezone.utc).isoformat()
        just_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--draft-model", default="")
    ap.add_argument("--checker-a", default="", help="Override first checker (or comma-list)")
    ap.add_argument("--checker-b", default="", help="Override second checker (or comma-list)")
    ap.add_argument("--lane", default="", choices=["", "cf", "nv"])
    ap.add_argument("--config", default="")
    ap.add_argument("--structural-only", action="store_true")
    ap.add_argument("--mark-done", action="store_true", default=True)
    ap.add_argument("--no-mark-done", action="store_true")
    args = ap.parse_args()
    mark_done = args.mark_done and not args.no_mark_done

    # Concurrency: claim lock always; global lock only for standalone runs.
    # Overnight sets SANE_FATHERS_NESTED=1 so CF+NV lanes can promote in parallel.
    nested = os.environ.get("SANE_FATHERS_NESTED") == "1"
    if not nested:
        global_lock = acquire_global(f"ai_promote:{args.agent}:{args.claim}")
        if global_lock is None:
            print("Another Fathers burn/promote holds the global lock — exit 3.", flush=True)
            return 3
    claim_lock = acquire_claim(args.claim, f"ai_promote:{args.agent}")
    if claim_lock is None:
        print(f"Claim {args.claim} already has an active promote — exit 3.", flush=True)
        release_all()
        return 3
    cfg = load_lane_config(args.config or None)
    wall = int(cfg.get("claim_wall_s") or 5400)
    # Exit 4 ≠ done — overnight must not count wall timeout as success.
    install_wall_deadline(wall, label=f"ai_promote:{args.claim}", exit_code=4)
    retries = int(cfg.get("api_error_retries_per_model") or 2)
    lane = args.lane
    if not lane:
        dm = normalize_model(args.draft_model) if args.draft_model else ""
        lane = "nv" if dm and is_nvidia_model(dm) else "cf"
    lane_cfg = (cfg.get("lanes") or {}).get(lane) or {}

    drafts = as_list(lane_cfg.get("draft"))
    draft_model = normalize_model(args.draft_model) or normalize_model(
        drafts[0] if drafts else DRAFT_DEFAULT
    )
    if args.checker_a:
        chain_a = [normalize_model(x.strip()) for x in args.checker_a.split(",") if x.strip()]
    else:
        chain_a = [normalize_model(x) for x in as_list(lane_cfg.get("checker_a"))] or [CHECKER_A_DEFAULT]
    if args.checker_b:
        chain_b = [normalize_model(x.strip()) for x in args.checker_b.split(",") if x.strip()]
    else:
        chain_b = [normalize_model(x) for x in as_list(lane_cfg.get("checker_b"))] or [CHECKER_B_DEFAULT]

    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv_token = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    all_models = [draft_model] + chain_a + chain_b
    if not args.structural_only:
        needs_cf = any(not is_nvidia_model(m) for m in all_models if m)
        needs_nv = any(is_nvidia_model(m) for m in all_models if m)
        if needs_cf and not cf_token:
            raise SystemExit("Need CF_TOKEN / CLOUDFLARE_API_TOKEN")
        if needs_nv and not nv_token:
            raise SystemExit("Need NV_API_KEY for NVIDIA models")

    row = parse_claim_row(args.claim)
    status = row.get("Status", "")
    if status not in {"claimed", "checking", "review", "free"}:
        raise SystemExit(f"Claim status {status!r} cannot promote")
    sections = sections_from_slice(row.get("Slice (sections)") or "")
    print(f"Claim {args.claim}: {sections} lane={lane} draft={draft_model}", flush=True)
    print(f"  checker_a chain={chain_a}", flush=True)
    print(f"  checker_b chain={chain_b}", flush=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = OUT / f"{stamp}-{args.claim}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    all_ok = True
    any_api_fail = False
    used_a = used_b = ""
    for section in sections:
        bundle = load_section_bundle(section)
        st = structural_ok(bundle)
        entry = {"section": section, "structural": st}
        if not st.get("ok"):
            all_ok = False
            print(f"  {section} STRUCT FAIL {st}", flush=True)
            results.append(entry)
            continue
        print(f"  {section} structural PASS", flush=True)
        if args.structural_only:
            results.append(entry)
            continue
        for label, chain in (("checker_a", chain_a), ("checker_b", chain_b)):
            print(f"  {section} → {label}", flush=True)
            chk = run_checker_chain(
                chain,
                bundle,
                cf_token=cf_token,
                nv_token=nv_token,
                account=account,
                retries_per_model=retries,
                draft_model=draft_model,
            )
            entry[label] = {k: v for k, v in chk.items() if k != "raw"}
            (out_dir / f"{section}_{label}.raw.txt").write_text(
                chk.get("raw") or chk.get("error") or "", encoding="utf-8"
            )
            flag = "PASS" if chk.get("ok") else "FAIL"
            detail = chk.get("error") or chk.get("parsed")
            print(f"    {flag} model={chk.get('model')} {detail}", flush=True)
            if chk.get("ok"):
                if label == "checker_a":
                    used_a = chk.get("model") or used_a
                else:
                    used_b = chk.get("model") or used_b
            else:
                all_ok = False
                if chk.get("api_error"):
                    any_api_fail = True
            time.sleep(0.3)
        results.append(entry)

    summary = {
        "claim": args.claim,
        "agent": args.agent,
        "lane": lane,
        "sections": sections,
        "draft_model": draft_model,
        "checker_a_chain": chain_a,
        "checker_b_chain": chain_b,
        "checker_a_used": used_a,
        "checker_b_used": used_b,
        "ok": all_ok,
        "api_failure": any_api_fail,
        "results": results,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nReceipt: {out_dir}", flush=True)

    if not all_ok:
        code = 2 if any_api_fail else 1
        kind = "api" if any_api_fail else "content"
        print(f"NOT done — exit {code} ({kind}).", flush=True)
        clear_wall_deadline()
        release_all()
        return code
    if args.structural_only:
        print("Structural-only OK — not marking done.", flush=True)
        clear_wall_deadline()
        release_all()
        return 0
    if mark_done:
        reviewer = f"ai-crosscheck:{used_a or chain_a[0]}+{used_b or chain_b[0]}"
        stamp_justifications(sections, reviewer)
        mark_claim_done(
            args.claim,
            args.agent,
            f"{used_a}+{used_b}; receipt {out_dir.name}",
        )
        print(f"Claim {args.claim} → done ({reviewer})", flush=True)
    clear_wall_deadline()
    release_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
