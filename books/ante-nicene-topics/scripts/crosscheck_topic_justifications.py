#!/usr/bin/env python3
"""Independent two-family cross-check for topic-excerpt justifications.

Topic excerpts are not claim slices, so scripts/ai_promote.py cannot load
them. This reuses its checker prompt (CHECK_SYS) and the shared
validate_semantic_review gate unchanged, with two checker families that both
differ from the drafter:

  checker A: xAI Grok        (XAI_API_KEY)
  checker B: NVIDIA Nemotron (NV_API_KEY, smoked receipt required)

Both must pass. A pass stamps the justification source_verified with
reviewer "ai-crosscheck:<A>+<B>" and writes a receipt; a fail records the
reasons in `crosscheck` for repair and leaves confidence alone.

Usage (from repo root):
  set -a; source ~/.config/nv/env; set +a
  SANE_LLM_API_RECEIPT=<nemotron receipt> \
    python3 books/ante-nicene-topics/scripts/crosscheck_topic_justifications.py ID [ID ...]
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "books/ante-nicene-topics"
JUST = BOOK / "reviews/justifications"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "SaneApps/infra/SaneProcess/scripts"))
from ai_promote import CHECK_SYS  # noqa: E402  same standard as claim promotion
from pipeline.verify_translation_qa import validate_semantic_review  # noqa: E402
from llm_vendor_gate import require_llm_receipt  # noqa: E402

GROK = "grok-4.7"


def secret(*names):
    """Env first, then the sane-env keychain (same lookup as the research gate)."""
    import subprocess
    for n in names:
        if os.environ.get(n):
            return os.environ[n]
    kc = os.path.expanduser("~/Library/Keychains/sane-env.keychain-db")
    for n in names:
        args = ["/usr/bin/security", "find-generic-password", "-s", "sane-env", "-a", n, "-w"]
        if os.path.isfile(kc):
            args.append(kc)
        out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
        if out:
            return out
    raise SystemExit(f"missing secret: {names[0]}")

NEMO = "nvidia/nemotron-3-super-120b-a12b"
XAI_KEY = NV_KEY = None


def post(url, key, body, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def parse_verdict(text: str):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def prompt(j: dict) -> list[dict]:
    user = (
        f"Ignatius topic excerpt {j['excerpt_id']}.\n"
        f"Named edition: {json.dumps(j.get('edition'), ensure_ascii=False)}\n\n"
        f"Locked Greek:\n[p1]\n{j['source_text']}\n\n"
        "Paragraph count: the Locked Greek above is exactly 1 numbered paragraph(s); "
        "after checking each, report covered_source_paragraphs as exactly [1].\n\n"
        f"Pass A gloss:\n{j.get('pass_a_gloss')}\n\n"
        f"Title: {j.get('thought_title')}\n\n"
        f"Pass B english:\n{json.dumps(j.get('pass_b_english') or [], ensure_ascii=False)}\n\n"
        f"Lemmas and choices: {json.dumps({k: j.get(k) for k in ('lemmas', 'choices')}, ensure_ascii=False)}\n"
        f"Notes and variants: {json.dumps({'notes': j.get('notes'), 'variants': j.get('variants'), 'bible_refs': j.get('bible_refs')}, ensure_ascii=False)}\n"
        "Judge now."
    )
    return [{"role": "system", "content": CHECK_SYS}, {"role": "user", "content": user}]


def check_grok(j):
    # Grok reasons before answering; long excerpts can take several minutes.
    # One retry on timeout so slowness never counts as a verdict.
    for attempt in (1, 2):
        try:
            d = post("https://api.x.ai/v1/chat/completions", XAI_KEY,
                     {"model": GROK, "messages": prompt(j), "max_tokens": 8000}, 600)
            return parse_verdict(d["choices"][0]["message"]["content"])
        except TimeoutError:
            if attempt == 2:
                raise


def check_nemo(j):
    # One retry when the reply is unparseable or skips the required checks
    # block: a malformed verdict is an API-shape miss, not a judgment.
    v = None
    for _ in (1, 2):
        d = post("https://integrate.api.nvidia.com/v1/chat/completions", NV_KEY,
                 {"model": NEMO, "messages": prompt(j), "reasoning_effort": "none",
                  "temperature": 1.0, "top_p": 0.95, "max_tokens": 2000}, 220)
        v = parse_verdict(d["choices"][0]["message"]["content"])
        if isinstance(v, dict) and isinstance(v.get("checks"), dict):
            return v
    return v


def run_one(eid: str, stamp: str, out_dir: Path) -> dict:
    path = JUST / f"{eid}.json"
    j = json.loads(path.read_text())
    content_hash = hashlib.sha256(json.dumps(
        {k: j.get(k) for k in ("source_text", "pass_a_gloss", "pass_b_english")},
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    verdicts = {}
    for name, fn in (("a", check_grok), ("b", check_nemo)):
        try:
            v = fn(j)
        except Exception as e:  # API failure: record, never count as pass
            v = {"verdict": "error", "notes": f"{type(e).__name__}: {e}"}
        errs = validate_semantic_review(v, expected_source_paragraphs=1) if isinstance(v, dict) else ["unparseable"]
        verdicts[name] = {"model": GROK if name == "a" else NEMO, "review": v, "gate_errors": errs}
    ok = all(not x["gate_errors"] for x in verdicts.values())
    j["crosscheck"] = {"at": stamp, "content_sha256": content_hash, "pass": ok,
                       "a": verdicts["a"], "b": verdicts["b"]}
    if ok:
        j["confidence"] = "source_verified"
        j["reviewer"] = f"ai-crosscheck:{GROK}+{NEMO.split('/')[-1]}"
        j.setdefault("checks", {})["semantic_review"] = "pass"
    path.write_text(json.dumps(j, ensure_ascii=False, indent=1) + "\n")
    (out_dir / f"{eid}.json").write_text(json.dumps(j["crosscheck"], ensure_ascii=False, indent=1))
    reasons = []
    for x in verdicts.values():
        r = x["review"] if isinstance(x["review"], dict) else {}
        reasons += [str(s)[:300] for s in (r.get("reasons") or [])] + x["gate_errors"][:2]
    return {"id": eid, "pass": ok, "reasons": reasons}


def main() -> int:
    ids = sys.argv[1:]
    if not ids:
        print(__doc__)
        return 2
    require_llm_receipt([NEMO], purpose="translation-qa")
    global XAI_KEY, NV_KEY
    XAI_KEY = secret("XAI_API_KEY")
    NV_KEY = secret("NV_API_KEY", "NVIDIA_API_KEY", "NGC_API_KEY")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "outputs/ai-promote" / f"topic-crosscheck-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda i: run_one(i, stamp, out_dir), ids))
    for r in results:
        print(("PASS " if r["pass"] else "FAIL ") + r["id"])
        for s in r["reasons"][:4]:
            print("    - " + s)
    print(f"{sum(r['pass'] for r in results)}/{len(results)} passed; receipts in {out_dir}")
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
