"""Validate excerpt JSON + optional justification receipts for professional bar."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_EXCERPT = {
    "id",
    "topic",
    "citation",
    "author",
    "work",
    "locus",
    "english",
    "confidence",
}
REQUIRED_JUSTIFICATION = {
    "excerpt_id",
    "edition",
    "source_text",
    "pass_a_gloss",
    "lemmas",
    "pass_b_english",
    "choices",
    "confidence",
}


def check_excerpts(path: Path) -> list[str]:
    errors = []
    data = json.loads(path.read_text())
    ids = set()
    for i, x in enumerate(data):
        missing = REQUIRED_EXCERPT - set(x)
        if missing:
            errors.append(f"[{i}] {x.get('id')}: missing {sorted(missing)}")
        eid = x.get("id")
        if eid in ids:
            errors.append(f"duplicate id {eid}")
        ids.add(eid)
        if not x.get("english"):
            errors.append(f"{eid}: empty english")
        if x.get("confidence") == "source_verified":
            # justification file required
            pass
    return errors


def check_justifications(excerpts_path: Path, just_dir: Path) -> list[str]:
    errors = []
    data = json.loads(excerpts_path.read_text())
    for x in data:
        if x.get("confidence") != "source_verified":
            continue
        jp = just_dir / f"{x['id']}.json"
        if not jp.exists():
            errors.append(f"{x['id']}: source_verified but missing {jp.name}")
            continue
        j = json.loads(jp.read_text())
        missing = REQUIRED_JUSTIFICATION - set(j)
        if missing:
            errors.append(f"{x['id']}: justification missing {sorted(missing)}")
        if j.get("excerpt_id") != x["id"]:
            errors.append(f"{x['id']}: excerpt_id mismatch")
        # Pass B must equal english paragraphs roughly
        pb = j.get("pass_b_english") or []
        if pb and pb != x.get("english"):
            errors.append(f"{x['id']}: pass_b_english != excerpt english (keep in sync)")
        if not j.get("source_text", "").strip():
            errors.append(f"{x['id']}: empty source_text")
        if not j.get("lemmas"):
            errors.append(f"{x['id']}: lemmas empty")
        if not j.get("choices"):
            errors.append(f"{x['id']}: choices empty — professional bar requires justifications")
    return errors


def anf_diverge_heuristic(ours: str, anf: str) -> str:
    """Very light opposite-sense detector; not a full NLI model."""
    ours_l, anf_l = ours.lower(), anf.lower()
    neg_pairs = [
        ("not free", "free"),
        ("no choice", "choice"),
        ("by fate", "not by fate"),
        ("necessity", "not necessity"),
    ]
    # if ANF affirms free choice language and ours denies
    anf_free = any(w in anf_l for w in ("free choice", "free will", "power of", "own power", "voluntarily"))
    ours_denies = any(w in ours_l for w in ("no free", "not free", "no choice", "by fate alone", "no power to"))
    if anf_free and ours_denies:
        return "fail"
    return "pass"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--excerpts", type=Path, required=True)
    p.add_argument("--justifications", type=Path, default=None)
    args = p.parse_args(argv)
    errs = check_excerpts(args.excerpts)
    just_dir = args.justifications
    if just_dir is None:
        just_dir = args.excerpts.parent.parent.parent / "reviews" / "justifications"
    if just_dir.exists():
        errs += check_justifications(args.excerpts, just_dir)
    else:
        # only error if any source_verified
        data = json.loads(args.excerpts.read_text())
        if any(x.get("confidence") == "source_verified" for x in data):
            errs.append(f"missing justifications dir: {just_dir}")
    if errs:
        print("FAIL")
        for e in errs:
            print(" -", e)
        return 1
    print("OK professional excerpt/justification checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
