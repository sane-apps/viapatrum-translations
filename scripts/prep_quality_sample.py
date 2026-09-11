#!/usr/bin/env python3
"""One-shot: crib Homily 6.1 (NVIDIA) and 7.3 (CF) into outputs/prep-quality/."""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from draft_claim import draft_section  # noqa: E402

OUT = ROOT / "outputs" / "prep-quality"
JUST = ROOT / "books/origen-jeremiah-samuel/reviews/justifications"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cf = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    from llm_bakeoff import DEFAULT_ACCOUNT  # noqa: E402

    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    print("tokens cf", bool(cf), "nv", bool(nv), flush=True)
    r1 = draft_section(
        "6.1",
        "nvidia/nemotron-3-super-120b-a12b",
        cf,
        nv,
        acct,
        "quality-nv",
        max_tokens=2048,
        prep=True,
    )
    print("6.1 nv", json.dumps({k: r1.get(k) for k in ("ok", "error", "ocr_flags", "ms")}, default=str), flush=True)
    r2 = draft_section(
        "7.3",
        "@cf/qwen/qwen3-30b-a3b-fp8",
        cf,
        nv,
        acct,
        "quality-cf",
        max_tokens=2048,
        prep=True,
    )
    print("7.3 cf", json.dumps({k: r2.get(k) for k in ("ok", "error", "ocr_flags", "ms")}, default=str), flush=True)
    shutil.copy(JUST / "jeremiah_6_1.json", OUT / "nv_6_1.json")
    shutil.copy(JUST / "jeremiah_7_3.json", OUT / "cf_7_3.json")
    print("saved", OUT, flush=True)
    return 0 if r1.get("ok") and r2.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
