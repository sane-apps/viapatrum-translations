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
    cf_call,
    cf_profile,
    extract_json,
    load_fixture,
    score,
    user_prompt,
    SYS_TMPL,
)

CLAIMS = ROOT / "docs" / "CLAIMS.md"
OUT = ROOT / "outputs" / "ai-promote"
LOCKS = ROOT / "docs" / "claim-locks"

DRAFT_DEFAULT = "@cf/qwen/qwen3-30b-a3b-fp8"
CHECKER_A_DEFAULT = "@cf/meta/llama-3.1-8b-instruct-fp8-fast"
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

Fail if English invents sense absent from Greek, if Pass B adds ideas not in Pass A,
if title is only a locus label, or if the English smells like ANF/Victorian paste.
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


def run_checker(model: str, bundle: dict, token: str, account: str) -> dict:
    prof = cf_profile(model)
    raw = cf_call(
        model,
        checker_prompt(bundle),
        token,
        account,
        max_tokens=min(int(prof.get("max_tokens", 1200)), 1200),
        temperature=float(prof.get("temperature", 0.0)),
        enable_thinking=prof.get("enable_thinking"),
        use_max_completion_tokens=bool(prof.get("use_max_completion_tokens")),
        api=prof.get("api", "run"),
    )
    if raw.get("error"):
        return {"ok": False, "error": raw["error"], "model": model, "ms": raw.get("ms")}
    obj = extract_json(raw["content"]) or {}
    verdict = str(obj.get("verdict") or "").lower()
    ok = verdict == "pass" and obj.get("anf_or_archaic_smell") is not True
    # Prefer explicit grounding flags when present
    for key in ("grounded_in_greek", "pass_b_subset_of_pass_a", "title_is_thought"):
        if key in obj and obj[key] is False:
            ok = False
    return {
        "ok": ok,
        "model": model,
        "ms": raw.get("ms"),
        "parsed": obj,
        "raw": raw["content"][:4000],
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
    ap.add_argument("--draft-model", default=DRAFT_DEFAULT)
    ap.add_argument("--checker-a", default=CHECKER_A_DEFAULT)
    ap.add_argument("--checker-b", default=CHECKER_B_DEFAULT)
    ap.add_argument(
        "--structural-only",
        action="store_true",
        help="Skip model checkers (debug). Not enough for done.",
    )
    ap.add_argument(
        "--mark-done",
        action="store_true",
        default=True,
        help="Mark claim done when all checks pass (default true)",
    )
    ap.add_argument("--no-mark-done", action="store_true")
    args = ap.parse_args()
    mark_done = args.mark_done and not args.no_mark_done

    token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    if not args.structural_only and not token:
        raise SystemExit("Need CF_TOKEN / CLOUDFLARE_API_TOKEN")

    row = parse_claim_row(args.claim)
    status = row.get("Status", "")
    if status not in {"claimed", "checking", "review", "free"}:
        raise SystemExit(f"Claim status {status!r} cannot promote")
    sections = sections_from_slice(row.get("Slice (sections)") or "")
    print(f"Claim {args.claim}: {sections}", flush=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = OUT / f"{stamp}-{args.claim}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    all_ok = True
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
        for label, model in (("checker_a", args.checker_a), ("checker_b", args.checker_b)):
            if model == args.draft_model:
                raise SystemExit(f"{label} must differ from draft model")
            print(f"  {section} → {label} {model}", flush=True)
            chk = run_checker(model, bundle, token, account)
            entry[label] = {k: v for k, v in chk.items() if k != "raw"}
            (out_dir / f"{section}_{label}.raw.txt").write_text(
                chk.get("raw") or chk.get("error") or "", encoding="utf-8"
            )
            flag = "PASS" if chk.get("ok") else "FAIL"
            print(f"    {flag} {chk.get('error') or chk.get('parsed')}", flush=True)
            if not chk.get("ok"):
                all_ok = False
            time.sleep(0.4)
        results.append(entry)

    summary = {
        "claim": args.claim,
        "agent": args.agent,
        "sections": sections,
        "draft_model": args.draft_model,
        "checker_a": args.checker_a,
        "checker_b": args.checker_b,
        "ok": all_ok,
        "results": results,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nReceipt: {out_dir}", flush=True)

    if not all_ok:
        print("NOT done — fix fails and re-run.", flush=True)
        return 1
    if args.structural_only:
        print("Structural-only OK — not marking done.", flush=True)
        return 0
    if mark_done:
        reviewer = f"ai-crosscheck:{args.checker_a}+{args.checker_b}"
        stamp_justifications(sections, reviewer)
        mark_claim_done(
            args.claim,
            args.agent,
            f"{args.checker_a} + {args.checker_b}; receipt {out_dir.name}",
        )
        print(f"Claim {args.claim} → done ({reviewer})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
