#!/usr/bin/env python3
"""Expand works/registry.json so every excerpt id is listed under a work.

Matches seeds onto existing MVP registry keys via author+work aliases.
Creates pending-edition stubs for unmatched works. Does not invent edition locks.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "translations" / "topics"
REGISTRY = ROOT / "works" / "registry.json"

# Normalized (author_slug, work_slug) → existing registry key
ALIASES: dict[tuple[str, str], str] = {
    ("athenagoras", "plea_for_the_christians"): "athenagoras.plea",
    ("athenagoras", "plea"): "athenagoras.plea",
    ("clement_of_alexandria", "instructor"): "clement.instructor",
    ("clement_of_alexandria", "paedagogus"): "clement.instructor",
    ("clement_of_alexandria", "stromata"): "clement.stromata",
    ("theophilus_of_antioch", "to_autolycus"): "theophilus.autolycus",
    ("theophilus", "to_autolycus"): "theophilus.autolycus",
    ("novatian", "on_the_trinity"): "novatian.trinity",
    ("novatian", "de_trinitate"): "novatian.trinity",
    ("lactantius", "divine_institutes"): "lactantius.divinae_institutiones",
    ("origen", "against_celsus"): "origen.contra_celsum",
    ("origen", "contra_celsum"): "origen.contra_celsum",
    ("origen", "on_first_principles"): "origen.de_principiis",
    ("origen", "de_principiis"): "origen.de_principiis",
    ("methodius_of_olympus", "concerning_free_will"): "methodius.de_libero_arbitrio",
    ("methodius", "concerning_free_will"): "methodius.de_libero_arbitrio",
    ("hermas", "shepherd"): "hermas.shepherd",
    ("hermas", "the_shepherd"): "hermas.shepherd",
    ("hermas", "shepherd_mandates_similitudes"): "hermas.shepherd",
    ("barnabas", "epistle_of_barnabas"): "barnabas.epistle",
    ("mathetes_epistle_to_diognetus", "to_diognetus"): "diognetus.epistle",
    ("mathetes", "to_diognetus"): "diognetus.epistle",
    ("melito_of_sardis", "on_pascha"): "melito.pascha",
    ("melito_of_sardis", "peri_pascha"): "melito.pascha",
    ("melito_of_sardis", "on_the_incarnation_fragments"): "melito.incarnation_fragment",
    ("cyprian", "de_catholicae_ecclesiae_unitate"): "cyprian.unity",
    ("cyprian", "on_the_unity_of_the_church"): "cyprian.unity",
    ("arnobius", "against_the_nations"): "arnobius.nations",
    ("arnobius", "adversus_nationes"): "arnobius.nations",
    ("victorinus_of_pettau", "on_the_creation_of_the_world"): "victorinus.creation",
    ("dionysius_of_alexandria", "on_nature_fragments"): "dionysius_alex.nature",
    ("dionysius_of_alexandria", "on_nature"): "dionysius_alex.nature",
    ("gregory_thaumaturgus", "declaration_of_faith"): "gregory_thaumaturgus.creed",
    ("tatian", "address_to_the_greeks"): "tatian.oratio",
    ("tatian", "oratio_ad_graecos"): "tatian.oratio",
    ("hippolytus", "refutation_of_all_heresies"): "hippolytus.refutation",
    ("didache", "teaching_of_the_twelve_apostles"): "didache.teaching",
    ("justin_martyr", "first_apology"): "justin_martyr.first_apology",
    ("justin_martyr", "second_apology"): "justin_martyr.second_apology",
    ("irenaeus", "against_heresies"): "irenaeus.against_heresies",
    ("tertullian", "against_marcion"): "tertullian.against_marcion",
    ("tertullian", "on_repentance"): "tertullian.on_repentance",
    ("ignatius_of_antioch", "to_the_ephesians"): "ignatius.ephesians",
    ("ignatius_of_antioch", "to_the_smyrnaeans"): "ignatius.smyrnaeans",
    ("commodian", "instructions"): "commodian.instructions",
    ("minucius_felix", "octavius"): "minucius.octavius",
}


def slug(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def load_excerpts() -> list[dict]:
    items: list[dict] = []
    for path in sorted(TOPICS.glob("*.json")):
        data = json.loads(path.read_text())
        chunk = data.get("excerpts") if isinstance(data, dict) else data
        items.extend(chunk or [])
    return items


def resolve_key(author: str, work: str, registry: dict) -> str | None:
    a, w = slug(author), slug(work)
    if (a, w) in ALIASES:
        return ALIASES[(a, w)]
    candidate = f"{a}.{w}"
    if candidate in registry:
        return candidate
    # Exact author+work string match against registry values
    for key, meta in registry.items():
        if meta.get("author") == author and meta.get("work") == work:
            return key
    # Soft: same author slug, work slug contained either way
    for key, meta in registry.items():
        if slug(meta.get("author", "")) != a:
            continue
        rw = slug(meta.get("work", ""))
        if not rw or not w:
            continue
        if rw == w or rw in w or w in rw:
            return key
    return None


def main() -> int:
    apply = "--apply" in sys.argv
    dry = not apply
    excerpts = load_excerpts()
    registry = json.loads(REGISTRY.read_text())
    before = len(registry)

    by_key: dict[str, list[dict]] = defaultdict(list)
    created = 0
    unmatched_auth = Counter()

    for ex in excerpts:
        author = ex.get("author") or "Unknown"
        work = ex.get("work") or "Unknown"
        key = resolve_key(author, work, registry)
        if key is None:
            key = f"{slug(author)}.{slug(work)}"
            if key not in registry:
                lang = ex.get("source_language") or "und"
                auth = ex.get("authenticity") or "accepted"
                registry[key] = {
                    "author": author,
                    "work": work,
                    "language": lang,
                    "authenticity": auth,
                    "edition": {
                        "id": "pending-seed-edition",
                        "path": "",
                        "license": "pending",
                    },
                    "excerpt_ids": [],
                    "note": "Seed coverage stub — edition lock pending; not Professional GTG.",
                }
                created += 1
            unmatched_auth[(author, work)] += 1
        by_key[key].append(ex)

    added_ids = 0
    for key, group in by_key.items():
        meta = registry[key]
        ids = list(meta.get("excerpt_ids") or [])
        seen = set(ids)
        # Prefer majority authenticity/language from group if stub
        auths = Counter(e.get("authenticity") for e in group if e.get("authenticity"))
        langs = Counter(e.get("source_language") for e in group if e.get("source_language"))
        if auths and meta.get("authenticity") != "contested":
            # keep contested if any excerpt contested
            if "contested" in auths:
                meta["authenticity"] = "contested"
            elif not meta.get("authenticity"):
                meta["authenticity"] = auths.most_common(1)[0][0]
        if langs and not meta.get("language"):
            meta["language"] = langs.most_common(1)[0][0]
        for e in group:
            eid = e.get("id")
            if eid and eid not in seen:
                ids.append(eid)
                seen.add(eid)
                added_ids += 1
        meta["excerpt_ids"] = ids

    # Coverage check
    covered = set()
    for meta in registry.values():
        covered |= set(meta.get("excerpt_ids") or [])
    all_ids = {e["id"] for e in excerpts if e.get("id")}
    missing = sorted(all_ids - covered)

    print(f"registry works before={before} after={len(registry)} created={created}")
    print(f"excerpt_ids added={added_ids} covered={len(covered)}/{len(all_ids)} missing={len(missing)}")
    if missing[:5]:
        print("missing sample:", missing[:5])

    if dry:
        print("DRY RUN (pass --apply to write).")
        return 0 if not missing else 1

    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {REGISTRY}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
