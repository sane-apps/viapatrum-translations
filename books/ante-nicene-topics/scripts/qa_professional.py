#!/usr/bin/env python3
"""Professional-track QA for ante-nicene-topics excerpts.

Checks glossary policy, required metadata, and source_verified invariants.
Exit 0 = pass; 1 = fail. Prints a short summary either way.

Use --strict-professional to fail on missing clear (owner or named second-model),
empty lemmas, or missing checks.source_lock for source_verified receipts
(Professional GTG gate).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = ROOT / "translations" / "topics"
JUST_DIR = ROOT / "reviews" / "justifications"
REGISTRY = ROOT / "works" / "registry.json"
VERSION = ROOT / "VERSION"

# Customer-facing English must not use bare "free will" (system slogan).
FREE_WILL_RE = re.compile(r"\bfree will\b", re.I)
PENDING_EDITION = re.compile(r"^pending|pending-", re.I)
OWNER_CLEAR_RE = re.compile(r"^owner-\d{4}-\d{2}-\d{2}$")
SECOND_MODEL_CLEAR_RE = re.compile(r"^second-model-\d{4}-\d{2}-\d{2}$")

# Glossary lemma → allowed English (from docs/GLOSSARY.md). Soft-check on MVP English.
GLOSSARY_LEMMA_EN = {
    "αὐτεξούσιον": ("self-determining power", "self-determining"),
    "liberum arbitrium": ("free decision", "free choice"),
    "εἱμαρμένη": ("fate", "destiny"),
    "ἐφʼ ἡμῖν": ("in our power", "what is in our power"),
    "προαίρεσις": ("deliberate choice", "choice"),
}


def clear_ok(just: dict) -> bool:
    """Professional GTG clear: human owner clear and/or named second-model clear."""
    reviewer = str(just.get("reviewer") or "")
    checks = just.get("checks") or {}
    if OWNER_CLEAR_RE.match(reviewer) and checks.get("human_clear") == "pass":
        return True
    if SECOND_MODEL_CLEAR_RE.match(reviewer) and checks.get("second_model_clear") == "pass":
        report = checks.get("second_model_report") or ""
        if report and (ROOT / report).exists():
            return True
    return False



def load_excerpts() -> list[dict]:
    items: list[dict] = []
    for path in sorted(TOPICS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            chunk = data.get("excerpts") or data.get("items") or []
        else:
            chunk = data
        items.extend(chunk)
    return items


def english_blob(x: dict) -> str:
    en = x.get("english")
    if isinstance(en, list):
        return "\n".join(en)
    return str(en or "")


def notes_blob(x: dict) -> str:
    notes = x.get("notes")
    if isinstance(notes, list):
        return "\n".join(str(n) for n in notes)
    return str(notes or "")


def main() -> int:
    strict = "--strict-professional" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []
    items = load_excerpts()
    registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}

    if not VERSION.exists():
        errors.append("missing VERSION file")
    else:
        ver = VERSION.read_text().strip()
        if not re.match(r"^\d+\.\d+\.\d+", ver):
            errors.append(f"VERSION not semver-ish: {ver!r}")

    conf = Counter(x.get("confidence") for x in items)
    just_files = {p.stem for p in JUST_DIR.glob("*.json")} if JUST_DIR.exists() else set()
    empty_lemmas = 0
    pending_reviewer = 0
    missing_source_lock = 0

    for x in items:
        eid = x.get("id") or "<no-id>"
        if not x.get("authenticity"):
            errors.append(f"{eid}: missing authenticity")
        if not x.get("source_language"):
            errors.append(f"{eid}: missing source_language")

        body = english_blob(x)
        if FREE_WILL_RE.search(body):
            errors.append(f"{eid}: glossary — 'free will' in English body")

        notes = notes_blob(x)
        if FREE_WILL_RE.search(notes) and "glossary" not in notes.lower() and "system" not in notes.lower():
            warnings.append(f"{eid}: 'free will' in notes (review)")

        # Soft glossary: if Greek/Latin blob names a tracked lemma, English should use an allowed gloss.
        if x.get("confidence") == "source_verified":
            src = " ".join(
                str(x.get(k) or "")
                for k in ("greek", "latin", "source_text", "original")
            )
            if isinstance(x.get("source"), dict):
                src += " " + " ".join(str(v) for v in x["source"].values())
            low_body = body.lower()
            for lemma, allowed in GLOSSARY_LEMMA_EN.items():
                if lemma in src or lemma.replace("ʼ", "'") in src:
                    if not any(a in low_body for a in allowed):
                        warnings.append(
                            f"{eid}: glossary soft — source has {lemma} but English lacks {allowed[0]!r}"
                        )

        if x.get("confidence") == "source_verified":
            if eid not in just_files:
                errors.append(f"{eid}: source_verified but no reviews/justifications/{eid}.json")
            else:
                just = json.loads((JUST_DIR / f"{eid}.json").read_text())
                ed = just.get("edition") or {}
                if not ed.get("id") or PENDING_EDITION.search(str(ed.get("id"))):
                    errors.append(f"{eid}: justification edition.id missing/pending")
                path = ed.get("path") or ""
                if path and not (ROOT / path).exists():
                    errors.append(f"{eid}: justification edition.path missing on disk: {path}")
                if just.get("confidence") != "source_verified":
                    errors.append(f"{eid}: justification confidence != source_verified")
                if not just.get("lemmas"):
                    empty_lemmas += 1
                    msg = f"{eid}: source_verified but empty lemmas[]"
                    (errors if strict else warnings).append(msg)
                if not clear_ok(just):
                    pending_reviewer += 1
                    msg = (
                        f"{eid}: source_verified lacks clear "
                        "(owner-YYYY-MM-DD + human_clear=pass, or "
                        "second-model-YYYY-MM-DD + second_model_clear=pass + report path)"
                    )
                    (errors if strict else warnings).append(msg)
                checks = just.get("checks") or {}
                if checks.get("source_lock") != "pass":
                    missing_source_lock += 1
                    msg = f"{eid}: source_verified but checks.source_lock != pass"
                    (errors if strict else warnings).append(msg)
            edition_id = x.get("edition_id") or ""
            if not edition_id or PENDING_EDITION.search(str(edition_id)):
                errors.append(f"{eid}: source_verified but excerpt edition_id missing/pending")

    covered: set[str] = set()
    for key, work in registry.items():
        for eid in work.get("excerpt_ids") or []:
            covered.add(eid)
        ed = (work.get("edition") or {}).get("id") or ""
        path = (work.get("edition") or {}).get("path") or ""
        if path and not PENDING_EDITION.search(ed) and not (ROOT / path).exists():
            errors.append(f"registry {key}: edition.path missing on disk: {path}")

    seed_unregistered = 0
    for x in items:
        eid = x.get("id")
        if eid and eid not in covered:
            if x.get("confidence") in ("seed_anf", "seed_edition"):
                seed_unregistered += 1
            else:
                errors.append(f"{eid}: not listed in works/registry.json excerpt_ids")

    print("=== ante-nicene professional QA ===")
    if strict:
        print("mode: --strict-professional")
    print(f"excerpts: {len(items)}")
    print(f"confidence: {dict(conf)}")
    print(f"justifications on disk: {len(just_files)}")
    print(f"registry works: {len(registry)}")
    verified = conf.get("source_verified", 0)
    print(f"source_verified: {verified}/{len(items)} ({100 * verified / max(len(items), 1):.0f}%)")
    print(
        f"professional_gaps: empty_lemmas={empty_lemmas} pending_reviewer={pending_reviewer} "
        f"missing_source_lock={missing_source_lock}"
    )
    if seed_unregistered:
        warnings.append(f"{seed_unregistered} seed excerpts not yet in works/registry.json excerpt_ids")
    if not strict:
        warnings = [
            w
            for w in warnings
            if "empty lemmas" not in w
            and "lacks clear" not in w
            and "pending-owner-golden-set" not in w
            and "source_lock !=" not in w
        ]
        if empty_lemmas:
            warnings.append(f"{empty_lemmas} source_verified receipts have empty lemmas[]")
        if pending_reviewer:
            warnings.append(
                f"{pending_reviewer} source_verified receipts still lack human/second-model clear "
                "(blocks Professional GTG)"
            )
        if missing_source_lock:
            warnings.append(f"{missing_source_lock} source_verified receipts lack checks.source_lock=pass")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if errors:
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)")
    if strict:
        print("NOTE: --strict-professional green ⇒ Professional GTG gate met (see docs/PROFESSIONAL_BAR.md).")
    else:
        print(
            "NOTE: PASS ≠ Professional GTG. Professional GTG needs "
            "--strict-professional green (owner clear and/or named second-model clear)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
