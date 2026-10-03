#!/usr/bin/env python3
"""Jev cross-check for filed Bible-allusion certainty (TypeSafe reviewer lane).

For each added_allusion in a book's English JSON, asks Jev whether the locked
source quotes, echoes, or merely resembles the verse, and reports agreement
with the filed certainty. Advisory only: mismatches go to a stronger reviewer,
never auto-decide.

Routing: Cloudflare Workers AI (`typesafe/jev`) first so Jev rides existing
CF usage instead of separate TypeSafe spend; direct api.typesafe.ai only as
fallback when TYPESAFE_API_KEY is set (one stderr note per process).
Needs CF_TOKEN/CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID for the CF path.

Usage: python3 scripts/jev_review.py <book-slug> [--all] [--max N]
Exit 0 with a MISMATCHES count line; prints one verdict line per allusion.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.typesafe.ai/v1/systemone"
# Override with JEV_MODEL=@cf/cloudflare/clef (Jev-compatible, 2026-10-01) to A/B.
CF_MODEL = os.environ.get("JEV_MODEL", "typesafe/jev")
DEFAULT_ACCOUNT = "2c267ab06352ba2522114c3081a8c5fa"
TIMEOUT = 25

_fallback_noted = False


def _post(url, payload, token):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _cf_jev(state, questions):
    token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", DEFAULT_ACCOUNT)
    if not token or not account:
        raise RuntimeError("CF Jev credentials missing")
    body = _post(
        "https://api.cloudflare.com/client/v4/accounts/%s/ai/run" % account,
        {"model": CF_MODEL, "input": {"state": state, "questions": questions}},
        token,
    )
    # Workers AI wraps once; the gateway wraps again
    # ({result: {state, result: {answers}}}). Unwrap until answers show.
    for _ in range(3):
        if (isinstance(body, dict) and "answers" not in body
                and isinstance(body.get("result"), dict)):
            body = body["result"]
        else:
            break
    if not isinstance(body, dict) or "answers" not in body:
        raise RuntimeError("CF Jev bad shape: %s" % str(body)[:160])
    return body


def _direct_jev(state, questions):
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        raise SystemExit("TYPESAFE_API_KEY not set")
    return _post(
        API,
        {"model": "jev-latest", "state": state, "questions": questions},
        key,
    )


def jev(state, questions):
    global _fallback_noted
    try:
        return _cf_jev(state, questions)
    except Exception as e:  # noqa: BLE001 - CF path may lack balance/scopes
        cf_err = e
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("CF Jev failed (%s); TYPESAFE_API_KEY not set" % cf_err)
    if not _fallback_noted:
        print("JEV-DIRECT-FALLBACK: %s" % cf_err, file=sys.stderr)
        _fallback_noted = True
    return _direct_jev(state, questions)


CERTAINTY_Q = {
    "type": "choice",
    "instructions": (
        "Does the source text quote or echo the candidate verse, "
        "or merely resemble it in theme?"
    ),
    "criteria": {
        "clear": "The source quotes the verse or unmistakably echoes its wording.",
        "possible": "No quotation or clear echo, but a plausible thematic connection.",
        "none": "Neither quotation, echo, nor meaningful connection.",
    },
}

WINDOW_FULL = 6000
WINDOW_EDGE = 3000
WINDOW_SNIP = "\n[... snip ...]\n"


def excerpt_window(text):
    """Full text up to WINDOW_FULL; head+tail with a snip marker beyond.

    A blind [:1500] head-clip once hid quoted verses living past the
    cut and produced confident false 'none' verdicts.
    """
    text = text or ""
    if len(text) <= WINDOW_FULL:
        return text
    return text[:WINDOW_EDGE] + WINDOW_SNIP + text[-WINDOW_EDGE:]


# Filed certainty vocab is wider than Jev's {clear, possible, none}.
# Normalize to bands for verdicts; receipts keep the raw filed value.
CERTAINTY_NORM = {
    "quotation": "clear",
    "clear": "clear",
    "probable": "possible",
    "allusion": "possible",
    "allusive": "possible",
    "possible": "possible",
    "none": "none",
}


def normalize_certainty(filed):
    """Map a filed certainty to Jev's band; unknown values pass through."""
    key = (filed or "").strip().lower()
    return CERTAINTY_NORM.get(key, key)


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        print("usage: jev_review.py <book-slug> [--all] [--max N]", file=sys.stderr)
        return 2
    slug = argv[1]
    check_all = "--all" in argv
    max_n = 5
    if "--max" in argv:
        max_n = int(argv[argv.index("--max") + 1])
    book = ROOT / "books" / slug
    eng_files = sorted((book / "translations").glob("*_english.json"))
    if not eng_files:
        print(f"no English JSON under {book}/translations")
        return 2
    mismatches = 0
    checked = 0
    for ef in eng_files:
        data = json.loads(ef.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("sections", [])
        src_path = ef.with_name(ef.name.replace("_english.json", "_source.json"))
        src_map = {}
        if src_path.exists():
            sdata = json.loads(src_path.read_text(encoding="utf-8"))
            srows = sdata if isinstance(sdata, list) else sdata.get("sections", [])
            src_map = {str(s.get("section")): s for s in srows if isinstance(s, dict)}
        for row in rows:
            if not isinstance(row, dict):
                continue
            for al in row.get("added_allusions") or []:
                if not isinstance(al, dict) or not al.get("reference"):
                    continue
                if checked >= max_n and not check_all:
                    print(f"cap reached ({max_n}); rerun with --all for the rest")
                    print(f"MISMATCHES: {mismatches} of {checked} checked")
                    return 0
                sec = str(row.get("section"))
                src = src_map.get(sec, {})
                full_en = " ".join(row.get("english") or [])
                english_excerpt = excerpt_window(full_en)
                state = {
                    "source_excerpt": str(src.get("latin") or src.get("greek") or "")[:3000],
                    "english_excerpt": english_excerpt,
                    "candidate_verse": al.get("reference"),
                    "filed_certainty": al.get("certainty"),
                    "filed_reason": al.get("reason"),
                }
                try:
                    body = jev(state, {"certainty": CERTAINTY_Q})
                except Exception as e:  # noqa: BLE001 - report lane failure plainly
                    print(f"LANE-ERROR sec {sec}: {type(e).__name__}: {e}")
                    return 3
                ans = body["answers"]["certainty"]
                filed = (al.get("certainty") or "").strip().lower()
                verdict = "AGREE" if ans["choice"] == normalize_certainty(filed) else "MISMATCH"
                if verdict == "MISMATCH":
                    mismatches += 1
                checked += 1
                print(
                    f"{verdict} sec {sec} {al.get('reference')}: filed={filed} "
                    f"jev={ans['choice']} conf={ans['confidence']:.2f}"
                )
    if checked == 0:
        print("no added_allusions filed in this book")
    print(f"MISMATCHES: {mismatches} of {checked} checked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
