"""Structural translation checks and reproducible, hash-bound audit packets.

A sampled audit only reviews its selected passages. It does not certify a corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

from pipeline.check_pass_ab import check_record, content_errors, join_b, normalized

REQUIRED_EXCERPT = {"id", "topic", "citation", "author", "work", "locus", "english", "confidence"}
REQUIRED_JUSTIFICATION = {
    "excerpt_id", "edition", "source_text", "pass_a_gloss", "lemmas",
    "pass_b_english", "choices", "confidence",
}
SEMANTIC_CHECKS = ("source_identity", "completeness", "negation", "agency",
                   "modality", "doctrine", "scripture")


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROW_ID_KEYS = ("id", "fragment_id", "section", "location", "codex")


def load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "sections" in data or "excerpts" in data:
            data = data.get("sections", data.get("excerpts"))
        elif any(data.get(key) is not None for key in ROW_ID_KEYS):
            data = [data]  # Single-row file (e.g. one Photius codex per file).
        else:
            data = None
    if not isinstance(data, list) or not data or any(not isinstance(x, dict) for x in data):
        raise ValueError(f"{path}: expected a nonempty list of records")
    return data


def row_id(row: dict) -> str:
    for key in ROW_ID_KEYS:
        if row.get(key) is not None:
            return str(row[key])
    raise ValueError("record has no id, fragment_id, section, location or codex")


def source_paragraphs(row: dict) -> list[str]:
    for key in ("source_text", "greek", "latin", "julian", "text"):
        value = row.get(key)
        if value:
            paras = value if isinstance(value, list) else [value]
            if any(not isinstance(x, str) or not x.strip() for x in paras):
                raise ValueError("source paragraphs must be nonempty strings")
            return paras
    return []


def indexed(rows: list[dict], label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        key = row_id(row)
        if key in result:
            raise ValueError(f"{label}: duplicate section {key}; provide unique composite ids")
        result[key] = row
    return result


def check_excerpts(path: Path) -> list[str]:
    try:
        rows = load_rows(path)
        indexed(rows, "excerpts")
    except (OSError, ValueError) as exc:
        return [str(exc)]
    errors = []
    for row in rows:
        missing = REQUIRED_EXCERPT - row.keys()
        if missing:
            errors.append(f"{row_id(row)}: missing {sorted(missing)}")
        if not isinstance(row.get("english"), list) or any(
                not isinstance(p, str) or not p.strip() for p in row.get("english", [])):
            errors.append(f"{row_id(row)}: english must contain nonempty paragraphs")
        errors += [f"{row_id(row)}: {e}" for e in content_errors(row.get("english"))]
    return errors


def check_justifications(excerpts_path: Path, just_dir: Path) -> list[str]:
    try:
        rows = load_rows(excerpts_path)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    errors = []
    for row in rows:
        if row.get("confidence") != "source_verified":
            continue
        eid = row_id(row)
        jp = just_dir / f"{eid}.json"
        try:
            j = json.loads(jp.read_text())
            if not isinstance(j, dict):
                raise ValueError("justification must be an object")
        except (OSError, ValueError) as exc:
            errors.append(f"{eid}: missing/invalid justification: {exc}")
            continue
        missing = REQUIRED_JUSTIFICATION - j.keys()
        errors += [f"{eid}: {e}" for e in check_record(j)]
        if missing:
            errors.append(f"{eid}: justification missing {sorted(missing)}")
        if j.get("excerpt_id") != eid:
            errors.append(f"{eid}: excerpt_id mismatch")
        if j.get("pass_b_english") != row.get("english"):
            errors.append(f"{eid}: pass_b_english != current English snapshot")
        edition = j.get("edition") or {}
        if not isinstance(edition, dict):
            errors.append(f"{eid}: edition must be an object")
            continue
        source_path = Path(edition.get("path") or "")
        if not source_path.is_absolute():
            # Existing receipt paths are relative to the book containing reviews/.
            source_path = just_dir.parent.parent / source_path
        try:
            if not source_path.is_file() or edition.get("sha256") != file_digest(source_path):
                errors.append(f"{eid}: missing/stale raw source file hash")
        except OSError as exc:
            errors.append(f"{eid}: unreadable source: {exc}")
        if not edition.get("locus"):
            errors.append(f"{eid}: missing source locus")
    return errors


# Longer names first so "gpt-oss" is not also counted as "gpt".
_MODEL_FAMILIES = ("gpt-oss", "deepseek", "nemotron", "gemini", "gemma", "mistral",
                   "qwen", "llama", "claude", "kimi", "glm", "gpt")


def _flat_text(value) -> str:
    if isinstance(value, (list, tuple)):
        return " ".join(_flat_text(part) for part in value)
    return " ".join(str(value or "").split())


def _quotes_passage(note: str, passage, n: int = 25) -> bool:
    """True when the note copies a real span of the passage."""
    text = _flat_text(passage)
    if not text:
        return False
    if len(text) <= n:
        return text in note
    return any(text[i:i + n] in note for i in range(len(text) - n + 1))


def _quote_errors(notes, sources, englishes) -> list[str]:
    note = _flat_text(notes)
    errors = []
    if not any(_quotes_passage(note, passage) for passage in sources):
        errors.append("semantic review notes do not quote the source")
    if not any(_quotes_passage(note, passage) for passage in englishes):
        errors.append("semantic review notes do not quote the English")
    return errors


def reviewer_model_families(reviewer: str) -> list[str]:
    """Family names found in a reviewer string, each family once.

    Display/diagnostic only. validate_audit_receipt never trusts this; it
    reads provenance_family_errors (structured model ids + call metadata)."""
    name = str(reviewer or "").casefold()
    found = []
    for family in _MODEL_FAMILIES:
        if family in name:
            found.append(family)
            name = name.replace(family, " ")
    return found


# Reviewer family identity (2026-10-09). The two-family rule reads the
# structured provenance a review adapter records (scripts/dual_family_review.py):
# exact model ids plus per-call metadata, bound to the reviewed text hashes.
# The free-text "reviewer" string is a display field only; typing model names
# into it proves nothing. Every receipt needs provenance: no corpus receipt
# passed the free-text two-family rule either (0 of 738 on 2026-10-09), so no
# historical approval is withdrawn.
PROVENANCE_SCHEMA = "review-provenance-v1"

# Exact model id -> exactly ONE family. Unknown ids fail closed; add researched
# identities here, never substring guesses.
# mistralai/mistral-nemotron is ONE family, "nemotron" (NVIDIA Nemotron
# post-training on a Mistral base). MODEL_RELATED records the shared lineage
# so it can never pair with a nemotron OR a mistral lane to make two families.
MODEL_FAMILY = {
    "nvidia/nemotron-3-super-120b-a12b": "nemotron",
    "nvidia/nemotron-3-ultra-550b-a55b": "nemotron",
    "mistralai/mistral-nemotron": "nemotron",
    "gemini-3.5-flash-lite": "gemini",
    "gemini-3.1-flash-lite": "gemini",
    "gemini-flash-lite-latest": "gemini",
    "gemini-2.5-flash-lite": "gemini",
    "gemini-2.5-flash": "gemini",
    "@cf/google/gemma-4-26b-a4b-it": "gemma",
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast": "llama",
    "@cf/meta/llama-3.1-8b-instruct-fp8-fast": "llama",
    "@cf/qwen/qwen3-30b-a3b-fp8": "qwen",
    "@cf/qwen/qwen3.8-27b": "qwen",
    "@cf/deepseek-ai/deepseek-v4-pro-0813": "deepseek",
    "@cf/moonshotai/kimi-k2.6": "kimi",
    "@cf/zai-org/glm-5.2": "glm",
    "@cf/zai-org/glm-4.7-flash": "glm",
    "@cf/openai/gpt-oss-20b": "gpt-oss",
}
MODEL_RELATED = {"mistralai/mistral-nemotron": frozenset({"mistral"})}


def model_family(model_id) -> str | None:
    """Family for an exact model id (case-insensitive), else None."""
    key = str(model_id or "").strip().casefold()
    return next((fam for mid, fam in MODEL_FAMILY.items() if mid.casefold() == key), None)


def _response_family(response_model) -> str | None:
    """Family of the model id the API echoed. Exact id, or a known id plus a
    version suffix (e.g. gemini-3.5-flash-lite-001)."""
    name = str(response_model or "").strip().casefold()
    if name.startswith("models/"):
        name = name[len("models/"):]
    fam = model_family(name)
    if fam:
        return fam
    for mid in sorted(MODEL_FAMILY, key=len, reverse=True):
        if name.startswith(mid.casefold() + "-") or name.startswith(mid.casefold() + "@"):
            return MODEL_FAMILY[mid]
    return None


def independent_family_count(lanes) -> int:
    """Count independent families among (model_id, family) lanes.

    Lanes with the same family, or whose recorded lineage (MODEL_RELATED)
    touches the other lane's family, merge into one."""
    nodes = []
    for model_id, family in lanes:
        related = MODEL_RELATED.get(str(model_id or "").strip().casefold(), frozenset())
        nodes.append(({family}, set(related) | {family}))
    groups: list[set[str]] = []
    for fams, touch in nodes:
        merged = set(touch)
        keep = []
        for g in groups:
            if g & merged:
                merged |= g
            else:
                keep.append(g)
        groups = keep + [merged]
    return len(groups)


def provenance_family_errors(receipt: dict, sections) -> list[str]:
    """Two-family rule from structured provenance, bound to the reviewed text.

    sections: the packet's selected section items (section, source_sha256,
    english_sha256). Each call must name its section and those hashes, so a
    call made on other text cannot stand in for this review.
    """
    prov = receipt.get("review_provenance")
    if not isinstance(prov, dict) or prov.get("schema") != PROVENANCE_SCHEMA:
        return ["reviewer provenance missing: two model families must come from "
                "recorded model calls, not the free-text reviewer"]
    lanes = prov.get("lanes")
    if not isinstance(lanes, list) or not lanes or any(not isinstance(x, dict) for x in lanes):
        return ["reviewer provenance has no lanes: cannot establish two model families"]
    by_section = {s.get("section"): s for s in sections}
    reviews = {r.get("section"): r for r in receipt.get("reviews") or [] if isinstance(r, dict)}
    errors, lane_ids, per_section = [], [], {}
    for i, lane in enumerate(lanes):
        model = lane.get("model")
        family = model_family(model)
        if family is None:
            errors.append(f"provenance lane {i}: unknown model id {model!r} has no family")
            continue
        if lane.get("family") != family:
            errors.append(f"provenance lane {i}: declared family {lane.get('family')!r} "
                          f"is not {family!r} for {model}")
        calls = lane.get("calls")
        if not isinstance(calls, list) or not calls:
            errors.append(f"provenance lane {i} ({model}): no recorded calls")
            continue
        if lane.get("call_count") != len(calls):
            errors.append(f"provenance lane {i} ({model}): call_count does not match calls")
        good = 0
        for call in calls:
            if not isinstance(call, dict):
                errors.append(f"provenance lane {i}: call must be an object")
                continue
            sid = call.get("section")
            item = by_section.get(sid)
            if item is None:
                errors.append(f"provenance lane {i}: call for unselected section {sid!r}")
                continue
            if (call.get("source_sha256") != item.get("source_sha256") or
                    call.get("english_sha256") != item.get("english_sha256")):
                errors.append(f"{sid}: {model} call reviewed other text (hash mismatch)")
                continue
            if _response_family(call.get("response_model")) != family:
                errors.append(f"{sid}: {model} call response model "
                              f"{call.get('response_model')!r} is not family {family}")
                continue
            if not (call.get("response_id") or call.get("request_id")) or not call.get("finished_at"):
                errors.append(f"{sid}: {model} call lacks response/request id or timestamp")
                continue
            if call.get("verdict") not in ("pass", "fail"):
                errors.append(f"{sid}: {model} call has no recorded model verdict")
                continue
            if call["verdict"] != "pass" or call.get("uncertainties"):
                adj = [a for a in (reviews.get(sid, {}).get("adjudications") or [])
                       if isinstance(a, dict) and a.get("model") == model
                       and str(a.get("resolution") or "").strip()]
                if not adj:
                    errors.append(f"{sid}: {model} returned {call['verdict']}"
                                  f"{' with uncertainties' if call.get('uncertainties') else ''}"
                                  " and no adjudication is recorded")
                    continue
            good += 1
            per_section.setdefault(sid, []).append((model, family))
        if good:
            lane_ids.append((model, family))
    if independent_family_count(lane_ids) < 2:
        errors.append("reviewer provenance shows fewer than two model families with recorded calls")
    for sid in by_section:
        if independent_family_count(per_section.get(sid, [])) < 2:
            errors.append(f"{sid}: not reviewed by two model families in provenance")
    return errors


def validate_semantic_review(review: dict, expected_source_paragraphs=None, *,
                             source_passages=None, english_passages=None) -> list[str]:
    """Validate review evidence. A supplied passage must be quoted in the note.

    Quoting a span still does not prove the reviewer understood the work.
    Callers that do not supply the passage keep the shape check only.
    """
    if not isinstance(review, dict):
        return ["semantic review must be an object"]
    errors = []
    if review.get("verdict") != "pass":
        errors.append("semantic verdict is not pass")
    checks = review.get("checks")
    if not isinstance(checks, dict):
        checks = {}
    for key in SEMANTIC_CHECKS:
        if checks.get(key) is not True:
            errors.append(f"semantic check {key} is not explicitly true")
    if review.get("uncertainties") != []:
        errors.append("semantic uncertainties missing or unresolved")
    if expected_source_paragraphs is not None:
        expected = list(range(1, expected_source_paragraphs + 1))
        if (review.get("covered_source_paragraphs") != expected or
                any(type(n) is not int for n in review.get("covered_source_paragraphs", []))):
            errors.append("semantic review does not cover every source paragraph")
    if not isinstance(review.get("notes"), str) or not review["notes"].strip():
        errors.append("semantic review needs evidence notes")
    elif source_passages is not None or english_passages is not None:
        errors.extend(_quote_errors(review.get("notes"), source_passages or [], english_passages or []))
    return errors


def make_audit_packet(english_path: Path, source_path: Path, *, raw_sources=(),
                      expected_sections=None, seed=0, sample_size=5, identity=None,
                      selected_sections=None, publication_scope=None) -> dict:
    """Check all rows, then select first/last, one risk-ranked, and seeded samples.

    expected_sections names the explicitly declared scope; otherwise the supplied
    source JSON is the scope. A reviewer must still compare that scope to the print.
    """
    required_identity = ("author", "work", "edition", "locus_scheme", "source_url")
    if not isinstance(identity, dict) or any(
            not isinstance(identity.get(k), str) or not identity[k].strip()
            for k in required_identity):
        raise ValueError("identity requires author, work, edition, locus_scheme and source_url")
    aliases = identity.get("locus_aliases", {})
    if not isinstance(aliases, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) or not v.strip()
            for k, v in aliases.items()):
        raise ValueError("identity.locus_aliases must map native ids to nonempty public loci")
    if publication_scope is not None and not isinstance(publication_scope, dict):
        raise ValueError("publication_scope must be an object")
    if sample_size < 3:
        raise ValueError("sample_size must be at least 3 (small corpora select all)")
    english_path, source_path = Path(english_path).resolve(), Path(source_path).resolve()
    english = indexed(load_rows(english_path), "English")
    source = indexed(load_rows(source_path), "source")
    declared_scope = expected_sections is not None
    expected = list(source) if expected_sections is None else [str(x) for x in expected_sections]
    if not expected or len(expected) != len(set(expected)):
        raise ValueError("expected sections must be nonempty and unique")
    errors = []
    extra_english = sorted(set(english) - set(expected))
    extra_source = sorted(set(source) - set(expected))
    if declared_scope:
        # Declared scope freezes the reviewed set: rows added later in both
        # files are unreviewed tail (never published), not packet breakage.
        # English without any source row stays a structural error.
        unreviewed_extra = sorted((set(extra_english) & set(extra_source)) |
                                  (set(extra_source) - set(extra_english)))
        english_only = sorted(set(extra_english) - set(extra_source))
    else:
        unreviewed_extra = []
        english_only = extra_english
    for name, missing, extra in (("English", sorted(set(expected) - set(english)), english_only),
                                 ("source", sorted(set(expected) - set(source)),
                                  [] if declared_scope else extra_source)):
        if missing:
            errors.append(f"{name}: missing expected sections {missing}")
        if extra:
            errors.append(f"{name}: sections outside declared scope {extra}")
    all_items = []
    for key in expected:
        if key not in english or key not in source:
            continue
        en, src = english[key], source[key]
        paras = source_paragraphs(src)
        body, source_text = join_b(en.get("english")), join_b(paras)
        row_errors = content_errors(body) + content_errors(source_text, "source", source=True)
        if not isinstance(en.get("english"), list) or any(
                not isinstance(p, str) or not p.strip() for p in en.get("english", [])):
            row_errors.append("English must contain nonempty string paragraphs")
        if normalized(body) and normalized(body) == normalized(source_text):
            row_errors.append("English copies the source")
        errors.extend(f"{key}: {error}" for error in row_errors)
        risks = []
        if re.search(r"\b(?:not|never|unless|must|may|cannot|grace|sin|will)\b", body, re.I):
            risks.append("negation_modality_or_doctrine")
        if "[[" in body or en.get("added_allusions"):
            risks.append("scripture_links")
        if en.get("translator_notes") or re.search(r"\b(?:lacuna|gap|uncertain)\b", body, re.I):
            risks.append("textual_uncertainty")
        if source_text and len(body.split()) < 0.5 * len(source_text.split()):
            risks.append("possible_omission")  # Selection signal, never a fidelity verdict.
        locus = str(src.get("locus") or src.get("location") or en.get("locus") or aliases.get(key) or key)
        all_items.append({
            "section": key, "locus": locus, "source_path": str(source_path),
            "source_text": paras, "english": en.get("english"),
            "source_sha256": digest(paras), "english_sha256": digest(en),
            "risks": risks,
        })
    bindings = [{"path": str(path), "sha256": file_digest(path)}
                for path in dict.fromkeys([english_path, source_path] +
                                          [Path(p).resolve() for p in raw_sources])]
    raw = [str(Path(p).resolve()) for p in raw_sources]
    if not raw:
        errors.append("no raw witness files supplied; source transcription cannot verify itself")
    candidates = {item["section"]: item for item in all_items}
    selected = []
    if candidates:
        keys = list(candidates)
        selected = list(dict.fromkeys([keys[0], keys[-1]]))
        risk = sorted(keys, key=lambda k: (-len(candidates[k]["risks"]), digest([seed, k])))
        if risk:
            selected.append(next((k for k in risk if k not in selected), risk[0]))
        for key in sorted(keys, key=lambda k: digest([seed, k])):
            if len(set(selected)) >= min(sample_size, len(keys)):
                break
            selected.append(key)
        selected = list(dict.fromkeys(selected))
    if selected_sections is not None:
        selected = [str(k) for k in selected_sections]
        if not selected or len(set(selected)) != len(selected) or any(k not in candidates for k in selected):
            raise ValueError("explicit selected sections must be nonempty, unique and present")
    packet = {
        "identity": identity, "publication_scope": publication_scope,
        "explicit_selected_sections": selected_sections,
        "declared_scope": declared_scope, "unreviewed_extra": unreviewed_extra,
        "schema": "translation-audit-v1", "seed": seed, "sample_size": sample_size,
        "scope": "selected_passages_only", "expected_sections": expected,
        "files": bindings, "raw_source_paths": raw, "structural_errors": errors,
        "coverage": {"expected": len(expected), "english": len(english), "source": len(source),
                     "unreviewed_extra": len(unreviewed_extra)},
        "sections": [{**candidates[k], "raw_source_paths": raw} for k in selected],
        "limits": "Sampling and structural checks do not prove whole-work fidelity or completeness.",
    }
    packet["packet_id"] = digest(packet)
    return packet


def validate_audit_receipt(packet: dict, receipt: dict) -> list[str]:
    if not isinstance(packet, dict):
        return ["packet must be an object"]
    errors = []
    if packet.get("schema") != "translation-audit-v1" or not packet.get("raw_source_paths"):
        return ["packet requires translation-audit-v1 and raw witnesses"]
    # Recreate from current files so a self-consistent digest cannot detach the
    # selected text from the actual files it claims to bind.
    append_tolerant = False
    try:
        bindings = packet["files"]
        legacy = "declared_scope" not in packet
        current = make_audit_packet(Path(bindings[0]["path"]), Path(bindings[1]["path"]),
                                    raw_sources=packet["raw_source_paths"],
                                    expected_sections=(packet["expected_sections"]
                                                       if packet.get("declared_scope") else None),
                                    seed=packet["seed"], sample_size=packet["sample_size"],
                                    identity=packet["identity"],
                                    selected_sections=packet.get("explicit_selected_sections"),
                                    publication_scope=packet.get("publication_scope"))
        if legacy:
            # Packets made before declared scopes existed: compare old shape
            # to old shape so unchanged files still validate (migration-safe).
            current = {k: v for k, v in current.items()
                       if k not in {"declared_scope", "unreviewed_extra"}}
            current["coverage"] = {k: v for k, v in current["coverage"].items()
                                   if k != "unreviewed_extra"}
        # Append tolerance applies only to full-selection declared packets:
        # every declared section is individually hash-bound, so whole-file
        # drift can only be unreviewed tail. Sampling packets keep the legacy
        # whole-file binding (an unselected edit must still invalidate).
        append_tolerant = (packet.get("declared_scope") and
                           set(packet.get("expected_sections", [])) ==
                           {s["section"] for s in packet.get("sections", [])} and
                           bool(packet.get("expected_sections")))
        if append_tolerant:
            # Declared scope freezes the reviewed set: file-level bindings and
            # coverage legitimately move as unreviewed tail is appended. Compare
            # everything else (identity, scope, declared sections and hashes).
            # Packets without the flag keep the legacy whole-packet comparison.
            ignore = {"files", "coverage", "packet_id", "unreviewed_extra"}
            old = {k: v for k, v in packet.items() if k not in ignore}
            new = {k: v for k, v in current.items() if k not in ignore}
            if new != old:
                errors.append("packet does not match regenerated current source and English")
        elif legacy:
            # Legacy ids were computed without the newer keys: compare content
            # only (the packet_id self-integrity check below still applies).
            old = {k: v for k, v in packet.items() if k != "packet_id"}
            new = {k: v for k, v in current.items() if k != "packet_id"}
            if new != old:
                errors.append("packet does not match regenerated current source and English")
        elif current != packet:
            errors.append("packet does not match regenerated current source and English")
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        return errors + [f"packet cannot be regenerated: {exc}"]
    if packet.get("packet_id") != digest({k: v for k, v in packet.items() if k != "packet_id"}):
        errors.append("packet contents changed")
    for pos, binding in enumerate(packet.get("files", [])):
        try:
            if append_tolerant and pos < 2:
                # english/source files: declared sections are hash-bound
                # individually above; whole-file drift is the unreviewed tail.
                continue
            if file_digest(Path(binding["path"])) != binding["sha256"]:
                errors.append(f"stale snapshot: {binding['path']}")
        except (OSError, KeyError) as exc:
            errors.append(f"missing snapshot file: {exc}")
    if packet.get("structural_errors"):
        errors.append("packet has unresolved structural errors")
    if not isinstance(receipt, dict):
        return errors + ["receipt must be an object"]
    if receipt.get("packet_id") != packet.get("packet_id"):
        errors.append("receipt belongs to another packet")
    sections = packet.get("sections") or []
    if receipt.get("verdict") != "pass" or not str(receipt.get("reviewer") or "").strip():
        errors.append("missing passing verdict or reviewer")
    else:
        # Families come from structured provenance only (never the reviewer string).
        errors += provenance_family_errors(receipt, sections)
    if packet.get("publication_scope") is not None:
        errors += ["scope review: " + e for e in validate_semantic_review(
            receipt.get("scope_review"),
            source_passages=[s.get("source_text") for s in sections],
            english_passages=[s.get("english") for s in sections])]
    reviews = receipt.get("reviews")
    if not isinstance(reviews, list) or any(not isinstance(r, dict) for r in reviews):
        return errors + ["receipt reviews must be a list of objects"]
    if any(not isinstance(r.get("section"), str) for r in reviews):
        return errors + ["review section ids must be strings"]
    expected = {s["section"]: s for s in sections}
    if not expected or len(reviews) != len(expected) or {r.get("section") for r in reviews} != set(expected):
        errors.append("reviewed sections do not match the selected packet")
    for review in reviews:
        section = expected.get(review.get("section"))
        if section:
            errors += [f"{review['section']}: {e}" for e in validate_semantic_review(
                review, len(section["source_text"]),
                source_passages=[section.get("source_text")],
                english_passages=[section.get("english")])]
    return errors


def reviewed_section_errors(packet: dict, receipt: dict, section,
                            source_paragraphs, english, *, expected_identity=None,
                            expected_scope=None) -> list[str]:
    """Validate a current sampled review against a consumer's exact passage.

    This authorizes only a selected passage. The consumer must call it for every
    new/changed section and must establish the work's raw-source identity.
    """
    errors = validate_audit_receipt(packet, receipt)
    if errors:
        return errors
    if not isinstance(expected_identity, dict) or any(
            not expected_identity.get(k) for k in ("author", "work", "edition")):
        return ["consumer must supply author, work and edition identity"]
    if any(packet["identity"].get(k) != v for k, v in expected_identity.items()):
        return ["consumer author/work/edition identity differs from review"]
    if expected_scope is not None and packet.get("publication_scope") != expected_scope:
        return ["consumer publication scope differs from review"]
    selected = [item for item in packet["sections"] if item["section"] == str(section)]
    if len(selected) != 1:
        return ["section was not selected and reviewed"]
    item = selected[0]
    if source_paragraphs != item["source_text"]:
        errors.append("consumer source differs from reviewed source")
    if english != item["english"]:
        errors.append("consumer English differs from reviewed English")
    return errors


REFERENCE_NGRAM = 8
# Calibrated 2026-09-18 on Photius/Freese: 10 copied rows run 21-206 words,
# 7 independently rendered rows run 0-17 (top clean: one shared 17-word opener).
REFERENCE_MAX_VERBATIM_RUN = 20  # words; independent translations never sustain this
REFERENCE_MAX_COVERAGE = 0.50  # fraction of section 8-grams found in a reference


def folded_words(text: str) -> list[str]:
    """Lowercased alphanumeric words with diacritics folded (copy detection)."""
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[^\W_]+", text, re.UNICODE)


def reference_ngrams(path: Path, n: int = REFERENCE_NGRAM) -> set[tuple[str, ...]]:
    words = folded_words(path.read_text(encoding="utf-8"))
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def verbatim_run_stats(words: list[str], ref: set[tuple[str, ...]],
                       n: int = REFERENCE_NGRAM) -> tuple[int, float]:
    """Longest verbatim word-run and 8-gram coverage of words against ref."""
    if len(words) < n or not ref:
        return 0, 0.0
    hits = [tuple(words[i:i + n]) in ref for i in range(len(words) - n + 1)]
    best = run = 0
    for hit in hits:
        run = run + 1 if hit else 0
        best = max(best, run)
    longest_words = best + n - 1 if best else 0
    return longest_words, sum(hits) / len(hits)


def reference_overlap_errors(english: dict[str, dict], reference_paths) -> list[str]:
    """Fail English sections copied from reference-only witnesses (Freese rule).

    A lock header marking a witness "reference only -- do not copy" is a
    project rule, not a suggestion; near-verbatim English fails here instead
    of reaching review. Short shared phrases pass; only sustained verbatim
    runs or majority coverage fail.
    """
    errors = []
    refs = []
    for raw in reference_paths or []:
        path = Path(raw)
        try:
            refs.append((str(path), reference_ngrams(path)))
        except OSError as exc:
            errors.append(f"unreadable reference {path}: {exc}")
    for key, row in english.items():
        body = join_b(row.get("english"))
        if not body.strip():
            continue
        words = folded_words(body)
        for name, ref in refs:
            longest, coverage = verbatim_run_stats(words, ref)
            if longest >= REFERENCE_MAX_VERBATIM_RUN:
                errors.append(
                    f"{key}: {longest}-word verbatim run from reference-only {name}")
            elif coverage >= REFERENCE_MAX_COVERAGE:
                errors.append(
                    f"{key}: {coverage:.0%} 8-gram coverage of reference-only {name}")
    return errors


def anf_diverge_heuristic(ours: str, anf: str) -> str:
    """Legacy diagnostic only: no observed conflict is not semantic approval."""
    free = any(w in anf.lower() for w in ("free choice", "free will", "power of", "own power", "voluntarily"))
    denial = any(w in ours.lower() for w in ("no free", "not free", "no choice", "by fate alone", "no power to"))
    return "fail" if free and denial else "unreviewed"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excerpts", type=Path)
    parser.add_argument("--justifications", type=Path)
    parser.add_argument("--english", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--raw-source", action="append", type=Path, default=[])
    parser.add_argument("--reference-only", action="append", type=Path, default=[],
                        help="Reference-only witness English must not copy (repeatable)")
    parser.add_argument("--expected-sections", type=Path, help="JSON array declaring edition scope")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--sample-size", type=int, default=5)
    parser.add_argument("--identity", type=Path, help="JSON author/work/edition/locus/source identity")
    parser.add_argument("--section", action="append", help="Explicit targeted section instead of sample")
    parser.add_argument("--publication-scope", type=Path, help="JSON work metadata and ordered section ids")
    parser.add_argument("--packet-out", type=Path)
    parser.add_argument("--receipt", type=Path, help="Review against the freshly regenerated packet")
    args = parser.parse_args(argv)
    try:
        if args.excerpts:
            errors = check_excerpts(args.excerpts)
            just_dir = args.justifications or args.excerpts.parent.parent.parent / "reviews/justifications"
            errors += check_justifications(args.excerpts, just_dir)
        elif args.english and args.source:
            expected = json.loads(args.expected_sections.read_text()) if args.expected_sections else None
            packet = make_audit_packet(args.english, args.source, raw_sources=args.raw_source,
                                       expected_sections=expected, seed=args.seed, sample_size=args.sample_size,
                                       identity=json.loads(args.identity.read_text()) if args.identity else None,
                                       selected_sections=args.section,
                                       publication_scope=json.loads(args.publication_scope.read_text()) if args.publication_scope else None)
            if args.packet_out:
                args.packet_out.parent.mkdir(parents=True, exist_ok=True)
                args.packet_out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
            errors = list(packet["structural_errors"])
            if args.reference_only:
                english_rows = indexed(load_rows(args.english), "English")
                errors += reference_overlap_errors(english_rows, args.reference_only)
            if args.receipt:
                errors += validate_audit_receipt(packet, json.loads(args.receipt.read_text()))
            print(f"packet={packet['packet_id']} sampled={len(packet['sections'])} scope=selected_passages_only")
        else:
            parser.error("provide --excerpts, or --english and --source")
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"FAIL: {error}")
    if not errors:
        print("OK structural/current-snapshot checks; no automatic fidelity certification")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
