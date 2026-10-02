#!/usr/bin/env python3
"""Write cross-checked justifications back into the topic excerpts.

Only a justification whose `crosscheck` passed AND whose current
source/Pass A/Pass B still hash to what the checkers judged is applied. The
excerpt gets the new reading English, the locked source paragraphs, the
edition id, a pointer to its justification, and confidence source_verified.
Everything else in the topic file is left as it is (other agents' edits
included). Dry run by default; --apply writes.

Re-attribution: an edition whose id names a different work than the excerpt
(Polycarp's Philippians filed under Ignatius) also corrects author/work/
citation, via ATTRIBUTION below.

  python3 books/ante-nicene-topics/scripts/integrate_verified_justifications.py [--apply] [--stage-from-head] [ID ...]

--stage-from-head (with --apply): the repo often holds other agents'
uncommitted edits in the same topic files. This stages HEAD's version of each
touched file plus only these excerpt changes, so a commit carries just this
work while the working tree keeps everyone's edits.
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
REPO = BOOK.parents[1]
JUST = BOOK / "reviews/justifications"

ATTRIBUTION = {
    "lake-1912-loeb-polycarp-philippians": {
        "author": "Polycarp of Smyrna",
        "work": "To the Philippians",
        "kind": "Letter",
        "period": "c. 110–135",
        "citation": "Polycarp — To the Philippians {locus}",
    },
}


# Mislabels found while locking sources (2026-10-02). Keyed by the chapters
# file the excerpt's source came from; fn(excerpt, unit) returns field fixes.
def _baptism_or_scorpiace(e, unit):
    if str(unit).startswith("Scorpiace"):
        n = str(unit).split()[-1]
        return {"work": "Scorpiace", "locus": n, "citation": f"Tertullian — Scorpiace {n}"}
    return {}


def _hermas_sim(e, unit):
    if str(unit).startswith("Sim.") and "Mand" in str(e.get("locus", "")):
        n = str(unit)[4:]
        return {"locus": f"Sim. {n}", "citation": f"Hermas — Shepherd, Similitude {n}"}
    return {}


CHAPTER_FIXES = {
    "tertullian-against-praxeas.json": lambda e, u: {
        "work": "On Baptism", "citation": f"Tertullian — On Baptism {e.get('locus', '')}".strip()},
    "tertullian-on-baptism.json": _baptism_or_scorpiace,
    "tertullian-on-the-soul.json": lambda e, u: {
        "work": "On the Flesh of Christ", "citation": f"Tertullian — On the Flesh of Christ {u}"},
    "origen-epistula-ad-africanum.json": lambda e, u: {
        "work": "Letter to Africanus", "citation": f"Origen — Letter to Africanus {u}"},
    "hermas-shepherd.json": _hermas_sim,
}
_units: dict | None = None


def chapter_unit(eid: str):
    global _units
    if _units is None:
        _units = {}
        for f in (BOOK / "sources/chapters").glob("*.json"):
            for k, v in (json.loads(f.read_text()).get("excerpt_map") or {}).items():
                _units[k] = (f.name, v)
    return _units.get(eid)


def current_hash(j: dict) -> str:
    return hashlib.sha256(json.dumps(
        {k: j.get(k) for k in ("source_text", "pass_a_gloss", "pass_b_english")},
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def paragraphs(source_text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\s*\[\d+\]\s*", source_text) if p.strip()]
    return parts or [source_text.strip()]


def main() -> int:
    apply = "--apply" in sys.argv
    only = {a for a in sys.argv[1:] if not a.startswith("--")}
    ready = {}
    for p in JUST.glob("*.json"):
        j = json.loads(p.read_text())
        cc = j.get("crosscheck") or {}
        if only and j.get("excerpt_id") not in only:
            continue
        if (j.get("confidence") == "source_verified" and cc.get("pass")
                and cc.get("content_sha256") == current_hash(j)):
            ready[j["excerpt_id"]] = j
    stage = "--stage-from-head" in sys.argv
    changed_files, applied = 0, []
    for f in sorted(glob.glob(str(BOOK / "translations/topics/*.json"))):
        d = json.loads(Path(f).read_text())
        if not isinstance(d, dict):
            continue
        ids = apply_to(d, ready)
        if not ids:
            continue
        applied += ids
        changed_files += 1
        if apply:
            Path(f).write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
            if stage:
                rel = str(Path(f).relative_to(REPO))
                head = json.loads(subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                                                 capture_output=True, text=True, check=True).stdout)
                apply_to(head, ready)
                blob = subprocess.run(["git", "-C", str(REPO), "hash-object", "-w", "--stdin"],
                                      input=json.dumps(head, ensure_ascii=False, indent=2) + "\n",
                                      capture_output=True, text=True, check=True).stdout.strip()
                subprocess.run(["git", "-C", str(REPO), "update-index", "--cacheinfo", f"100644,{blob},{rel}"], check=True)
    missing = sorted(set(ready) - set(applied))
    print(f"{'APPLIED' if apply else 'DRY RUN'}: {len(applied)} excerpts in {changed_files} topic files"
          + (" (staged from HEAD)" if apply and stage else ""))
    if missing:
        print("verified but not found in any topic file:", missing)
    return 0


def apply_to(d: dict, ready: dict) -> list:
    """Apply verified justifications to one parsed topic file; return ids."""
    applied = []
    for e in d.get("excerpts", []):
        j = ready.get(e.get("id"))
        if not j:
            continue
        ed = j["edition"]
        e["english"] = j["pass_b_english"]
        e["greek" if ed.get("language") == "grc" else "latin"] = paragraphs(j["source_text"])
        e["source_language"] = ed.get("language", e.get("source_language"))
        e["edition_id"] = ed["id"]
        e["source"] = ed.get("path", e.get("source"))
        e["confidence"] = "source_verified"
        e["justification"] = f"reviews/justifications/{j['excerpt_id']}.json"
        e["added_allusions"] = [r["display"] for r in j.get("bible_refs", [])]
        fix = ATTRIBUTION.get(ed["id"])
        if fix:
            locus = e.get("locus", "")
            e.update({k: v.format(locus=locus) for k, v in fix.items()})
        cu = chapter_unit(e["id"]) if "chapters/" in str(ed.get("path", "")) else None
        if cu and cu[0] in CHAPTER_FIXES:
            e.update(CHAPTER_FIXES[cu[0]](e, cu[1]))
        applied.append(e["id"])
    return applied


if __name__ == "__main__":
    sys.exit(main())
