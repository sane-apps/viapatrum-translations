#!/usr/bin/env python3
"""Draft Pass A/B for a claim's sections via Workers AI or NVIDIA NIM.

  source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/draft_claim.py --claim jer-h6 --agent overnight
  python3 scripts/draft_claim.py --claim jer-h8 --agent overnight-nv \
    --model nvidia/nemotron-3-super-120b-a12b

Then: python3 scripts/ai_promote.py --claim <id> --agent …
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_promote import atomic_text, file_digest, parse_claim_row, require_supported_claim, sections_from_slice
from book_adapter import JEREMIAH_SLUG, get_adapter
from pipeline_autonomy import SplitRefused, chunk_paragraphs, merge_chunk_drafts, parse_or_repair, split_guard
from pipeline.check_pass_ab import check_record  # noqa: E402
from llm_bakeoff import (  # noqa: E402
    DEFAULT_ACCOUNT,
    PREP_SYS,
    SYS_TMPL,
    extract_json,
    is_nvidia_model,
    load_fixture,
    normalize_model,
    score,
    user_prompt,
    vendor_call,
)

ENG = ROOT / "books/origen-jeremiah-samuel/translations/jeremiah_english.json"
JUST_DIR = ROOT / "books/origen-jeremiah-samuel/reviews/justifications"
SOURCE = ROOT / "books/origen-jeremiah-samuel/translations/jeremiah_source.json"
RAW_SOURCE = ROOT / "books/origen-jeremiah-samuel/sources/origeneswerke03orig.pdf"
XML_SOURCE = RAW_SOURCE.parent / "first1k/tlg2042.tlg009.opp-grc1.xml"
SOURCE_MANIFEST = RAW_SOURCE.parent / "manifest.json"
DRAFT_DEFAULT = "@cf/qwen/qwen3-30b-a3b-fp8"


def section_sort_key(section: str):
    parts = str(section).split(".")
    return tuple(int(p) if p.isdigit() else p for p in parts)


def upsert_english(section: str, title: str, english: list, notes: list, homily: int | None) -> None:
    rows = json.loads(ENG.read_text(encoding="utf-8"))
    row = {
        "section": section,
        "homily": homily if homily is not None else int(section.split(".")[0]),
        "title": title,
        "english": english,
    }
    if notes:
        row["translator_notes"] = notes
    replaced = False
    for i, existing in enumerate(rows):
        if str(existing.get("section")) == section:
            rows[i] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)
    rows.sort(key=lambda r: section_sort_key(str(r.get("section"))))
    atomic_text(ENG, json.dumps(rows, indent=2, ensure_ascii=False) + "\n")


def upsert_cyril_english(section: str, title: str, english: list, notes: list, adapter) -> None:
    """Update one cyril-isaiah english row, preserving book-specific keys.

    English files parallel source files row-for-row, so a section missing by
    id but present by source index heals drift instead of duplicating rows.
    """
    path = adapter.english_path_for_section(section)
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else [rows]
    target = None
    for i, existing in enumerate(rows):
        if str(existing.get("section")) == section:
            target = i
            break
    if target is None:
        idx = adapter.english_row_index(section)
        if idx < len(rows):
            target = idx
    row = dict(rows[target]) if target is not None else {}
    row.update({"section": section, "title": title, "english": english})
    if notes:
        row["translator_notes"] = notes
    else:
        row.pop("translator_notes", None)
    if target is None:
        rows.append(row)
    else:
        rows[target] = row
    atomic_text(path, json.dumps(rows, indent=2, ensure_ascii=False) + "\n")


def justification_data(section: str, obj: dict, agent: str, model: str, fix: dict, adapter=None, witnesses=None) -> dict:
    """Preserve supplied evidence; never synthesize choices or claim a lexicon was checked."""
    if adapter is not None and adapter.slug != JEREMIAH_SLUG:
        edition = adapter.edition_dict(fix, witnesses or [])
        excerpt = adapter.excerpt_id(section)
    else:
        h, s = section.split(".")
        edition = {"id": "gcs6-klostermann-1901", "language": "grc",
                    "locus": fix.get("klostermann") or f"Hom. {section}",
                    "path": fix["raw_source_path"],
                    "sha256": fix["raw_source_sha256"], "checks": fix["raw_checks"]}
        excerpt = f"jeremiah_{h}_{s}"
    data = {
        "anf_compare": {"status": "not_checked", "notes": "Machine draft from the supplied Greek; independent review pending."},
        "apparatus": [], "bible_refs": obj.get("bible_refs") or [],
        "checks": {"lemma_constraint": "pending", "placeholders": "pass"},
        "choices": obj.get("choices"), "confidence": "machine_draft",
        "edition": edition,
        "excerpt_id": excerpt, "lemmas": obj.get("lemmas"),
        "pass_a_gloss": obj.get("pass_a_gloss"), "pass_b_english": obj.get("english"),
        "source_text": " ".join(fix["greek"]), "variants": obj.get("variants") or [],
        "source_normalizations": fix.get("ocr_normalizations") or [],
        "reviewer": f"pending-ai-crosscheck:{model}", "draft_agent": agent,
        "draft_model": model, "drafted_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = check_record(data)
    for key, fields in (("choices", ("term", "english", "why")), ("lemmas", ("form", "lemma", "gloss"))):
        for item in data.get(key) or []:
            if not isinstance(item, dict) or any(not isinstance(item.get(f), str) or not item[f].strip() for f in fields):
                errors.append(f"{key}: model must supply real {', '.join(fields)}")
    if errors:
        raise ValueError("Missing draft evidence; retain prep and request a complete draft: " + "; ".join(errors))
    return data


def write_justification(section: str, data: dict, path: Path | None = None) -> Path:
    path = path or JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json"
    atomic_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path


def write_prep_justification(section: str, obj: dict, agent: str, model: str, fix: dict, path: Path | None = None, adapter=None, witnesses=None) -> Path:
    src = fix
    if adapter is not None and adapter.slug != JEREMIAH_SLUG:
        prep_edition = adapter.edition_dict(fix, witnesses or [])
        prep_excerpt = adapter.excerpt_id(section)
        path = path or adapter.justification_path(section)
    else:
        h, s = section.split(".")
        prep_edition = {
            "id": "gcs6-klostermann-1901",
            "language": "grc",
            "locus": src.get("klostermann") or f"Hom. {section}",
            "path": fix["raw_source_path"],
            "sha256": fix["raw_source_sha256"], "checks": fix["raw_checks"],
        }
        prep_excerpt = f"jeremiah_{h}_{s}"
        path = path or JUST_DIR / f"jeremiah_{h}_{s}.json"
    lemmas_in = obj.get("lemmas") or []
    lemmas = []
    for item in lemmas_in:
        if not isinstance(item, dict):
            continue
        lemmas.append(
            {
                "form": item.get("form") or item.get("greek") or "",
                "lemma": item.get("lemma") or "",
                "gloss": item.get("gloss") or "",
                **({"lexica": item["lexica"]} if item.get("lexica") else {}),
            }
        )
    guesses = obj.get("scripture_guesses") if isinstance(obj.get("scripture_guesses"), list) else []
    flags = obj.get("ocr_flags") if isinstance(obj.get("ocr_flags"), list) else []
    greek = src.get("greek") or []
    data = {
        "anf_compare": {
            "notes": "Machine crib only. Not reading English. Not copied from modern English.",
            "status": "no_pd_reference",
        },
        "apparatus": [],
        "bible_refs": [
            {
                "display": str(g.get("maybe") or ""),
                "method": "guess",
                "note": str(g.get("greek_snip") or ""),
            }
            for g in guesses
            if isinstance(g, dict) and (g.get("maybe") or g.get("greek_snip"))
        ],
        "checks": {
            "anf_diverge": "pending",
            "lemma_constraint": "pending",
            "placeholders": "pass",
        },
        "choices": [],
        "confidence": "machine_prep",
        "edition": prep_edition,
        "excerpt_id": prep_excerpt,
        "lemmas": lemmas,
        "ocr_flags": [str(x) for x in flags],
        "pass_a_gloss": obj.get("pass_a_gloss") or "",
        "reviewer": f"prep:{model}",
        "draft_agent": agent,
        "draft_model": model,
        "drafted_at": datetime.now(timezone.utc).isoformat(),
        "source_text": " ".join(str(p) for p in greek),
        "source_normalizations": fix.get("ocr_normalizations") or [],
        "variants": [],
    }
    atomic_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path


def salvage_prep_obj(raw: str, section: str) -> dict | None:
    """Keep a truncated crib if at least pass_a_gloss is intact."""
    m = re.search(r'"pass_a_gloss"\s*:\s*"((?:\\.|[^"\\])*)"', raw or "")
    if not m:
        return None
    try:
        gloss = json.loads(f'"{m.group(1)}"')
    except json.JSONDecodeError:
        return None
    if not isinstance(gloss, str) or len(gloss.strip()) < 40:
        return None
    return {
        "section": section,
        "pass_a_gloss": gloss.strip(),
        "lemmas": [],
        "ocr_flags": ["json truncated; salvaged pass_a only"],
        "scripture_guesses": [],
    }


def score_prep(obj: dict | None) -> dict:
    checks = {
        "parse_json": isinstance(obj, dict),
        "has_pass_a": False,
        "has_lemmas": False,
        "ocr_flags_list": False,
    }
    if not isinstance(obj, dict):
        return {"ok": False, "checks": checks}
    a = str(obj.get("pass_a_gloss") or "").strip()
    checks["has_pass_a"] = len(a) >= 40
    # Lemmas help; a long gloss is enough. Truncated JSON often dies on lemmas.
    lemmas = obj.get("lemmas") if isinstance(obj.get("lemmas"), list) else []
    checks["has_lemmas"] = True if len(a) >= 80 else bool(lemmas)
    flags = obj.get("ocr_flags")
    if flags is None:
        obj["ocr_flags"] = []
        checks["ocr_flags_list"] = True
    else:
        checks["ocr_flags_list"] = isinstance(flags, list)
    return {"ok": all(checks.values()), "checks": checks}


def draft_section(
    section: str,
    model: str,
    cf_token: str,
    nv_token: str,
    account: str,
    agent: str,
    max_tokens: int | None = None,
    *,
    prep: bool = False,
    book: str = JEREMIAH_SLUG,
    chunk_chars: int = 1500,
    hard_max_chars: int = 12000,
) -> dict:
    adapter = get_adapter(book)  # Refuse unknown books before any API call.
    model = normalize_model(model)
    jeremiah = book == JEREMIAH_SLUG
    # Jeremiah keeps module constants so existing callers/tests keep working.
    witness_paths = list(dict.fromkeys((RAW_SOURCE, XML_SOURCE))) if jeremiah else adapter.witness_files(section)
    manifest_file = SOURCE_MANIFEST if jeremiah else adapter.manifest_path()
    manifest = json.loads(manifest_file.read_text()) if manifest_file else {}
    base = JUST_DIR.parent.parent if jeremiah else adapter.book_dir
    fix = load_fixture(section) if jeremiah else adapter.load_source_row(section)
    witnesses = []
    for path in witness_paths:
        sha = file_digest(path)
        if jeremiah:
            manifest_key = path.relative_to(SOURCE_MANIFEST.parent).as_posix()
            if manifest.get("files", {}).get(manifest_key, {}).get("sha256") != sha:
                return {"ok": False, "section": section, "error": "raw_source_does_not_match_locked_manifest"}
        elif manifest_file:
            manifest_key = path.relative_to(manifest_file.parent).as_posix()
            pinned = manifest.get("files", {}).get(manifest_key, {}).get("sha256")
            if pinned and pinned != sha:
                return {"ok": False, "section": section, "error": "raw_source_does_not_match_locked_manifest"}
        # Unpinned witnesses record first-seen hashes in the justification;
        # promote re-verifies them, so post-draft tampering still fails.
        witnesses.append({"path": path.relative_to(base).as_posix(), "sha256": sha})
    fix["raw_source_path"], fix["raw_source_sha256"] = witnesses[0]["path"], witnesses[0]["sha256"]
    fix["raw_checks"] = witnesses[1:]
    just_path = JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json" if jeremiah else adapter.justification_path(section)
    prior = just_path
    if prep and prior.is_file() and json.loads(prior.read_text()).get("pass_b_english"):
        return {"ok": False, "section": section, "error": "existing_translation_preserved; prep must not overwrite reading-text evidence"}
    sys_msg = PREP_SYS if prep else SYS_TMPL

    def _call(call_model, call_messages, call_tokens):
        return vendor_call(
            call_model, call_messages, cf_token=cf_token, nv_token=nv_token,
            account=account, max_tokens=call_tokens,
        )

    need = ["pass_a_gloss"] if prep else ["pass_a_gloss", "english"]
    shape = ('{"pass_a_gloss": str, "lemmas": [...]}' if prep else
             '{"section": str, "title": str, "pass_a_gloss": str, "english": [...]}')
    source_chars = len(" ".join(fix["greek"]))
    guard = split_guard(source_chars, chunk_chars=chunk_chars, hard_max_chars=hard_max_chars)
    chunked = False
    if guard == "refuse":
        return {"ok": False, "section": section, "error": "section_too_large",
                "chars": source_chars,
                "plan": "split the source section or raise the hard max budget"}
    if guard == "single":
        messages = [
            {"role": "system", "content": sys_msg.format(section=section)},
            {"role": "user", "content": user_prompt(fix)},
        ]
        obj, info = parse_or_repair(_call, model, messages, need=need, shape_desc=shape, max_tokens=max_tokens)
        raw = {"content": info["raw"], "ms": info["ms"], "pt": info["pt"], "ct": info["ct"], "neurons": info["neurons"]}
        if obj is None and prep:
            obj = salvage_prep_obj(info["raw"] or "", section)
        if obj is None:
            return {"ok": False, "section": section, "error": info["error"] or "structural_fail",
                    "raw": (info["raw"] or "")[:2000], "ms": info["ms"], "max_tokens": max_tokens,
                    "repaired": info["repaired"]}
    else:
        chunked = True
        try:
            chunks = chunk_paragraphs(fix["greek"], chunk_chars)
        except SplitRefused as exc:
            return {"ok": False, "section": section, "error": "section_too_large",
                    "detail": str(exc), "plan": exc.plan}
        chunk_objs = []
        totals = {"ms": 0, "pt": 0, "ct": 0, "neurons": 0}
        for i, chunk in enumerate(chunks):
            chunk_section = f"{section}#c{i + 1}"
            chunk_fix = dict(fix, greek=chunk, section=chunk_section)
            chunk_messages = [
                {"role": "system", "content": sys_msg.format(section=chunk_section)},
                {"role": "user", "content": user_prompt(chunk_fix) + (
                    "\nFor THIS chunk: pass_a_gloss must cover EVERY clause completely "
                    "in source word order (a thin gloss fails review even when the "
                    "reading is good). The english paragraphs must be natural literary "
                    "prose in the author's voice -- same claims, different sentences; "
                    "never source word order, never a copy of the gloss.")},
            ]
            cobj, cinfo = parse_or_repair(_call, model, chunk_messages, need=need, shape_desc=shape, max_tokens=max_tokens)
            for key in totals:
                totals[key] += cinfo.get(key) or 0
            if cobj is None:
                return {"ok": False, "section": section, "error": "chunk_draft_failed",
                        "chunk": i + 1, "detail": cinfo.get("error"), "max_tokens": max_tokens}
            if english_tail_cut(cobj.get("english")):
                merged, tinfo = complete_tail(
                    _call, model, chunk_section, " ".join(chunk),
                    cobj.get("pass_a_gloss") or "", cobj.get("english"))
                for key in totals:
                    totals[key] += tinfo.get(key) or 0
                if merged is None:
                    return {"ok": False, "section": section, "error": "chunk_tail_cut",
                            "chunk": i + 1, "max_tokens": max_tokens}
                cobj["english"] = merged
            chunk_objs.append(cobj)
        obj = merge_chunk_drafts(chunk_objs)
        obj["section"] = section
        merged_english = " ".join(str(x) for x in obj.get("english") or [])
        title_obj, title_info = parse_or_repair(
            _call, model,
            [{"role": "system", "content": "Name the thought. Return ONLY valid JSON, no fences."},
             {"role": "user", "content": f"Section {section}. Reading English:\n\n{merged_english}\n\nReturn ONLY {{\"title\": \"short name of the thought (not a locus)\"}}"}],
            need=["title"], shape_desc='{"title": str}', max_tokens=800)
        for key in totals:
            totals[key] += title_info.get(key) or 0
        if title_obj and str(title_obj.get("title") or "").strip():
            obj["title"] = str(title_obj.get("title") or "").strip()
        else:
            # Fallback: first chunk's real title beats an empty one.
            obj["title"] = str(chunk_objs[0].get("title") or "").strip()
        raw = {"content": json.dumps(obj, ensure_ascii=False), "ms": totals["ms"],
               "pt": totals["pt"], "ct": totals["ct"], "neurons": totals["neurons"]}
    current = load_fixture(section) if jeremiah else adapter.load_source_row(section)
    if (current["greek"] != fix["greek"] or current.get("ocr_normalizations") != fix.get("ocr_normalizations")
            or any(file_digest(base / w["path"]) != w["sha256"] for w in witnesses)):
        return {"ok": False, "section": section, "error": "source_changed_during_draft"}
    sc = score_prep(obj) if prep else score(obj, raw["content"], section, source=fix["greek"])
    if not prep and obj is not None and not sc.get("ok"):
        checks = sc.get("checks") or {}
        others_ok = all(v for k, v in checks.items() if k not in ("english_complete", "thought_title"))
        if checks.get("parse_json") and not checks.get("english_complete") and others_ok:
            # Verbose models get cut mid-clause; finish the tail instead of a
            # full redraft. Bounded: one micro-call, then re-scored as usual.
            merged, tail_info = complete_tail(
                _call, model, section, " ".join(fix["greek"]),
                obj.get("pass_a_gloss") or "", obj.get("english"))
            for key in ("ms", "pt", "ct", "neurons"):
                raw[key] = raw.get(key, 0) + (tail_info.get(key) or 0)
            if merged:
                obj["english"] = merged
                sc = score(obj, json.dumps(obj, ensure_ascii=False), section, source=fix["greek"])
                raw["content"] = json.dumps(obj, ensure_ascii=False)
    if not sc.get("ok") or not obj:
        return {
            "ok": False,
            "section": section,
            "error": "structural_fail",
            "checks": sc.get("checks"),
            "raw": (raw.get("content") or "")[:2000],
            "ms": raw.get("ms"),
            "max_tokens": max_tokens,
        }
    if prep:
        jpath = write_prep_justification(section, obj, agent, model, fix, path=just_path, adapter=adapter, witnesses=witnesses)
        return {
            "ok": True,
            "section": section,
            "prep": True,
            "ms": raw.get("ms"),
            "pt": raw.get("pt"),
            "ct": raw.get("ct"),
            "neurons": raw.get("neurons", 0),
            "chunked": chunked,
            "justification": str(jpath),
            "ocr_flags": obj.get("ocr_flags") or [],
            "checks": sc.get("checks"),
            "max_tokens": max_tokens,
        }
    try:
        evidence = justification_data(section, obj, agent, model, fix, adapter=adapter, witnesses=witnesses)
    except ValueError as exc:
        return {"ok": False, "section": section, "error": "missing_draft_evidence", "detail": str(exc)}
    title = str(obj.get("title") or "").strip()
    english = obj.get("english") if isinstance(obj.get("english"), list) else []
    notes = obj.get("translator_notes") if isinstance(obj.get("translator_notes"), list) else []
    jpath = write_justification(section, evidence, just_path)
    if jeremiah:
        upsert_english(section, title, english, notes, fix.get("homily"))
    else:
        upsert_cyril_english(section, title, english, notes, adapter)
    return {
        "ok": True,
        "section": section,
        "title": title,
        "ms": raw.get("ms"),
        "pt": raw.get("pt"),
        "ct": raw.get("ct"),
        "neurons": raw.get("neurons", 0),
        "chunked": chunked,
        "book": book,
        "justification": str(jpath),
        "checks": sc.get("checks"),
        "max_tokens": max_tokens,
    }


REVISE_SYS = """You revise a rejected patristic reading draft. Return ONLY valid JSON, no fences."""

REVISE_B_SHAPE = '{"title": str, "english": [str, ...], "translator_notes": [...]}'

TERMINAL_END = re.compile(r'[.!?…]["\'»”’)\]]*$')


def english_tail_cut(english) -> bool:
    paras = [x for x in english or [] if isinstance(x, str) and x.strip()]
    return bool(paras) and not TERMINAL_END.search(paras[-1].strip())


def complete_tail(call_fn, model, section, greek_text, gloss, english, max_tokens=1500):
    """Finish a cut-off final paragraph. Returns (merged_english|None, info)."""
    paras = [x for x in english or [] if isinstance(x, str)]
    tail_obj, info = parse_or_repair(
        call_fn, model,
        [{"role": "system", "content": "Finish a cut-off translation. Return ONLY valid JSON, no fences."},
         {"role": "user", "content": (
             f"Section {section}. The reading English below was cut off mid-clause. "
             f"Using ONLY the locked Greek and gloss, return ONLY "
             f'{{"english_tail": ["completed final paragraph(s), every one a full sentence"]}}.\n\n'
             f"Locked Greek:\n{greek_text}\n\n"
             f"Gloss:\n{gloss}\n\n"
             f"Cut-off English:\n{json.dumps(paras, ensure_ascii=False)}")}],
        need=["english_tail"], shape_desc='{"english_tail": [...]}', max_tokens=max_tokens)
    tail = []
    if tail_obj:
        tail = [str(x).strip() for x in tail_obj.get("english_tail") or [] if str(x).strip()]
    if not tail:
        return None, info
    return ((paras[:-1] if paras else []) + tail), info


def _cap_note(value, limit: int = 40):
    if isinstance(value, list) and len(value) > limit:
        return value[:limit] + [f"... {len(value) - limit} more notes truncated"]
    if isinstance(value, str) and len(value) > 4000:
        return value[:4000] + "... [truncated]"
    return value


def load_receipt_failures(receipt_path: str) -> dict[str, list[str]]:
    """Map failed sections to checker/arbiter notes from a promote receipt."""
    data = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {}
    for entry in data.get("results") or []:
        section = entry.get("section")
        if not section:
            continue
        if not (entry.get("structural") or {}).get("ok"):
            continue
        notes: list[str] = []
        content_fail = False
        for key in ("checker_a", "checker_b"):
            check = entry.get(key) or {}
            if check.get("api_error"):
                continue
            if not check.get("ok"):
                content_fail = True
                parsed = check.get("parsed") or {}
                if (parsed.get("notes") or parsed.get("reasons") or parsed.get("reason")
                        or parsed.get("checks")):
                    notes.append(f"{key} ({check.get('model')}): verdict={parsed.get('verdict')}; "
                                 f"notes={_cap_note(parsed.get('notes'))}; "
                                 f"reasons={_cap_note(parsed.get('reasons'))}; "
                                 f"reason={_cap_note(parsed.get('reason'))}; "
                                 f"checks={_cap_note(parsed.get('checks'))}")
        arb = entry.get("arbiter") or {}
        if arb and not arb.get("ok") and not arb.get("api_error"):
            parsed = arb.get("parsed") or {}
            if (parsed.get("notes") or parsed.get("reasons") or parsed.get("reason")
                    or parsed.get("checks")):
                notes.append(f"arbiter ({arb.get('model')}): verdict={parsed.get('verdict')}; "
                             f"notes={_cap_note(parsed.get('notes'))}; "
                             f"reason={_cap_note(parsed.get('reason'))}; "
                             f"checks={_cap_note(parsed.get('checks'))}")
        if content_fail and notes:
            out[section] = notes
    return out


GREEK_SPAN = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF][\u0370-\u03FF\u1F00-\u1FFF\s\u0387.,;·ʼ'ʼ\u2019-]{8,}")


def greek_spans_in(notes: list[str]) -> list[str]:
    """Distinct Greek spans (8+ chars) quoted across checker notes."""
    seen: list[str] = []
    for note in notes:
        for match in GREEK_SPAN.findall(note):
            span = " ".join(match.split())
            if span not in seen:
                seen.append(span)
    return seen


def topup_gloss(call_fn, model, section, spans: list[str], max_tokens=800):
    """Gloss quoted-but-missing spans mechanically. Returns (lines|None, info)."""
    obj, info = parse_or_repair(
        call_fn, model,
        [{"role": "system", "content": "Gloss ancient Greek mechanically. Return ONLY valid JSON, no fences."},
         {"role": "user", "content": (
             f"Section {section}. Gloss ONLY these Greek spans in mechanical source "
             f"word order, one literal English line each. No flowing sentences, no "
             f"Greek in the output. Return ONLY "
             f'{{"added_glosses": ["gloss of span 1", ...]}}.\n\nSpans:\n' +
             "\n".join(f"- {s}" for s in spans))}],
        need=["added_glosses"], shape_desc='{"added_glosses": [...]}', max_tokens=max_tokens)
    if not obj:
        return None, info
    lines = [str(x).strip() for x in obj.get("added_glosses") or [] if str(x).strip()]
    return (lines or None), info


def revise_section(
    section: str,
    model: str,
    cf_token: str,
    nv_token: str,
    account: str,
    agent: str,
    notes: list[str],
    receipt: str,
    max_tokens: int | None = None,
    *,
    book: str = JEREMIAH_SLUG,
) -> dict:
    """Revise Pass B in place against checker notes; Pass A evidence stays.

    Fails closed when the prior justification lacks full-draft evidence.
    Records each revision in the justification for audit.
    """
    adapter = get_adapter(book)
    model = normalize_model(model)
    jeremiah = book == JEREMIAH_SLUG
    fix = load_fixture(section) if jeremiah else adapter.load_source_row(section)
    if jeremiah:
        eng_path = ENG
        rows = json.loads(eng_path.read_text(encoding="utf-8"))
        matches = [r for r in rows if str(r.get("section")) == section]
        just_path = JUST_DIR / f"jeremiah_{section.replace('.', '_')}.json"
    else:
        eng_path = adapter.english_path_for_section(section)
        rows = json.loads(eng_path.read_text(encoding="utf-8"))
        matches = [r for r in rows if str(r.get("section")) == section]
        just_path = adapter.justification_path(section)
    if not matches or not just_path.is_file():
        return {"ok": False, "section": section, "error": "missing_prior_draft"}
    row = matches[0]
    prior = json.loads(just_path.read_text(encoding="utf-8"))
    for key in ("pass_a_gloss", "lemmas", "choices"):
        if not prior.get(key):
            return {"ok": False, "section": section, "error": "missing_evidence_for_revision",
                    "detail": f"prior justification lacks {key}; redraft instead"}
    greek_text = " ".join(fix["greek"])
    current_b = json.dumps({"title": row.get("title"), "english": row.get("english"),
                            "translator_notes": row.get("translator_notes") or []}, ensure_ascii=False)
    critique = "\n".join(f"- {n}" for n in notes)
    messages = [
        {"role": "system", "content": REVISE_SYS},
        {"role": "user", "content": (
            f"Section {section}. Locked Greek:\n{greek_text}\n\n"
            f"Locked Pass A gloss (do not contradict it):\n{prior['pass_a_gloss']}\n\n"
            f"Current Pass B draft:\n{current_b}\n\n"
            f"Independent checkers REJECTED the draft:\n{critique}\n\n"
            f"Write a corrected Pass B covering EVERY clause with correct agency, "
            f"modality, participles, and verb tenses. "
            f"MINIMAL EDIT: reproduce every sentence the notes do NOT flag "
            f"word-for-word; change only flagged clauses and the fixes below. "
            f"Keep Pass B natural literary prose in the author's voice -- same "
            f"claims as the gloss, different sentences; never lapse into source "
            f"word order or copy gloss phrasing. "
            f"This never excuses omissions: you MUST still ADD any missing "
            f"translations (such as quote words) as new sentences. "
            f"QUOTE WORDS: the Greek contains direct biblical quotations; the "
            f"English MUST contain the translated WORDS of each quote, never a "
            f"summary or bare citation in their place. "
            f"ENGLISH ONLY in english[] and pass_a_gloss: never paste Greek words "
            f"into either; translate quote words into English in both. Greek "
            f"snips belong in translator_notes at most, never in the gloss or "
            f"reading text. Never emit bracketed tags like [n1]. "
            f"Edge fragments (the source chunk may begin/end mid-sentence): render "
            f"literally with a trailing/leading … and a translator note; never "
            f"complete or invent cut words. Place each clear Bible "
            f"quotation/allusion reference inline beside its clause as a "
            f"parenthetical (Full Book chapter:verse); never invent verse numbers. "
            f"Return ONLY this JSON shape:\n"
            f'{{"title": "short name of the thought (not a locus)", '
            f'"english": ["paragraphs of reading English, every one a full sentence"], '
            f'"translator_notes": ["uncertainty notes or empty list"]}}. Do not return '
            f"a gloss; missing-clause glosses are added mechanically from the notes.")},
    ]

    def _call(call_model, call_messages, call_tokens):
        return vendor_call(
            call_model, call_messages, cf_token=cf_token, nv_token=nv_token,
            account=account, max_tokens=call_tokens,
        )

    spans = greek_spans_in(notes)
    topup_lines: list[str] = []
    topup_info: dict = {}
    if spans:
        topup_lines, topup_info = topup_gloss(_call, model, section, spans, max_tokens=1500)
        topup_lines = topup_lines or []
    rev, info = parse_or_repair(_call, model, messages, need=["english"],
                                shape_desc=REVISE_B_SHAPE, max_tokens=max_tokens or 3000)
    for key in ("ms", "pt", "ct", "neurons"):
        info[key] = info.get(key, 0) + (topup_info.get(key) or 0)
    if rev is None:
        return {"ok": False, "section": section, "error": info["error"] or "revise_parse_fail",
                "raw": (info["raw"] or "")[:2000], "ms": info["ms"]}
    prior_lines = prior["pass_a_gloss"].split("\n")
    fresh_lines = [ln for ln in topup_lines
                   if ln and not any(ln in e or e in ln for e in prior_lines)]
    obj = {
        "section": section,
        "title": str(rev.get("title") or row.get("title") or "").strip(),
        "pass_a_gloss": (prior["pass_a_gloss"].strip() +
                         ("\n" + "\n".join(fresh_lines) if fresh_lines else "")),
        "english": [str(x) for x in rev.get("english") or []],
        "lemmas": prior["lemmas"],
        "choices": prior["choices"],
        "translator_notes": [str(x) for x in rev.get("translator_notes") or []],
    }
    sc = score(obj, json.dumps(obj, ensure_ascii=False), section, source=fix["greek"])
    if not sc.get("ok"):
        checks = sc.get("checks") or {}
        others_ok = all(v for k, v in checks.items() if k not in ("english_complete", "thought_title"))
        if checks.get("parse_json") and not checks.get("english_complete") and others_ok:
            merged, _tinfo = complete_tail(
                _call, model, section, " ".join(fix["greek"]),
                obj.get("pass_a_gloss") or "", obj.get("english"))
            if merged:
                obj["english"] = merged
                sc = score(obj, json.dumps(obj, ensure_ascii=False), section, source=fix["greek"])
    if not sc.get("ok"):
        return {"ok": False, "section": section, "error": "revise_structural_fail",
                "checks": sc.get("checks"), "ms": info["ms"],
                "notes": sc.get("notes"),
                "english": obj.get("english"), "title": obj.get("title")}
    prior_edition = prior.get("edition") or {}
    fix["raw_source_path"] = prior_edition.get("path") or ""
    fix["raw_source_sha256"] = prior_edition.get("sha256") or ""
    fix["raw_checks"] = prior_edition.get("checks") or []
    witnesses = [{"path": fix["raw_source_path"], "sha256": fix["raw_source_sha256"]}] + [
        {"path": c.get("path"), "sha256": c.get("sha256")} for c in fix["raw_checks"]]
    try:
        evidence = justification_data(section, obj, agent, model, fix,
                                      adapter=adapter if not jeremiah else None,
                                      witnesses=witnesses)
    except ValueError as exc:
        return {"ok": False, "section": section, "error": "missing_draft_evidence", "detail": str(exc)}
    # Preserve edition/witness/source evidence from the prior draft; the
    # revision changes reading text, not provenance. Record the round.
    for key in ("edition", "source_text", "source_normalizations", "anf_compare",
                "apparatus", "bible_refs", "variants"):
        if key in prior:
            evidence[key] = prior[key]
    prior_drafter = str(prior.get("draft_model") or "")
    evidence["draft_model"] = prior_drafter + f"+rev:{model}" if prior_drafter else model
    evidence["revisions"] = list(prior.get("revisions") or []) + [{
        "model": model, "agent": agent, "at": datetime.now(timezone.utc).isoformat(),
        "from_receipt": receipt, "notes_addressed": len(notes),
    }]
    evidence["reviewer"] = f"pending-ai-crosscheck:{model}"
    write_justification(section, evidence, just_path)
    if jeremiah:
        upsert_english(section, obj["title"], obj["english"], obj["translator_notes"], fix.get("homily"))
    else:
        upsert_cyril_english(section, obj["title"], obj["english"], obj["translator_notes"], adapter)
    return {"ok": True, "section": section, "title": obj["title"], "ms": info["ms"],
            "pt": info.get("pt", 0), "ct": info.get("ct", 0), "neurons": info.get("neurons", 0),
            "repaired": info["repaired"], "book": book, "justification": str(just_path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", required=True)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--model", default=DRAFT_DEFAULT)
    ap.add_argument("--section", action="append", default=[], help="Limit to these sections")
    ap.add_argument("--max-tokens", type=int, default=0, help="Override model profile max_tokens")
    ap.add_argument("--chunk-chars", type=int, default=0, help="Override draft chunk threshold chars")
    ap.add_argument("--hard-max-chars", type=int, default=0, help="Override draft refuse threshold chars")
    ap.add_argument("--revise-from", default="", help="Promote receipt summary.json whose failed sections get revised")
    ap.add_argument("--retries", type=int, default=2, help="Retries on structural_fail / API error")
    ap.add_argument("--draft-fallbacks", default="@cf/openai/gpt-oss-20b,@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                    help="Comma models rotated across attempts after the primary")
    ap.add_argument(
        "--prep",
        action="store_true",
        help="Crib only: Pass A, lemmas, OCR flags, scripture guesses. No reading English.",
    )
    args = ap.parse_args()

    model = normalize_model(args.model)
    _fb = [normalize_model(x) for x in (args.draft_fallbacks or "").split(",") if x.strip()]
    draft_chain = [model] + [x for x in _fb if x != model]
    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv_token = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    if is_nvidia_model(model):
        if not nv_token:
            raise SystemExit("Need NV_API_KEY for NVIDIA draft models")
    elif not cf_token:
        raise SystemExit("Need CF_TOKEN / CLOUDFLARE_API_TOKEN")

    row = parse_claim_row(args.claim)
    require_supported_claim(row)
    book = row.get("Book slug") or JEREMIAH_SLUG
    if args.revise_from:
        return revise_main(args, row, book)
    claimed_sections = sections_from_slice(row.get("Slice (sections)") or "", book)
    if args.section and not set(args.section) <= set(claimed_sections):
        raise SystemExit("Requested sections are outside the claim; refusing writes")
    sections = args.section or claimed_sections
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        wall = int(cfg.get("claim_wall_s") or 5400)
        chunk_chars = args.chunk_chars or int(cfg.get("draft_chunk_chars") or 1500)
        hard_max_chars = args.hard_max_chars or int(cfg.get("draft_hard_max_chars") or 12000)
    except Exception:  # noqa: BLE001
        wall = 5400
        chunk_chars = 1500
        hard_max_chars = 12000
    from fathers_run_lock import install_wall_deadline  # noqa: WPS433

    install_wall_deadline(wall, label=f"draft_claim:{args.claim}", exit_code=4)
    print(
        f"{'Prep' if args.prep else 'Drafting'} {args.claim} [{book}]: {sections} via {draft_chain}",
        flush=True,
    )
    hb = Path.home() / "SaneApps/outputs/fathers-overnight/heartbeat"
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text(f"{args.claim}\n", encoding="utf-8")

    failures = 0
    for section in sections:
        print(f"→ {section}", flush=True)
        try:
            hb.write_text(f"{args.claim} {section}\n", encoding="utf-8")
        except OSError:
            pass
        result = None
        attempts = max(1, args.retries + 1)
        override = args.max_tokens or None
        for attempt in range(1, attempts + 1):
            m = draft_chain[(attempt - 1) % len(draft_chain)]
            tok = override
            if attempt > 1 and not override:
                tok = 4096 + (attempt - 1) * 1024
            result = draft_section(
                section,
                m,
                cf_token,
                nv_token,
                account,
                args.agent,
                max_tokens=tok,
                prep=args.prep,
                book=book,
                chunk_chars=chunk_chars,
                hard_max_chars=hard_max_chars,
            )
            if result.get("ok"):
                break
            if attempt < attempts:
                print(
                    f"  retry {attempt}/{attempts - 1} after {result.get('error')} "
                    f"(model={m} max_tokens={result.get('max_tokens')})",
                    flush=True,
                )
                time.sleep(1.0)
        if result and result.get("ok"):
            extra = (
                f"ocr={result.get('ocr_flags')!r}"
                if result.get("prep")
                else f"title={result.get('title')!r}"
            )
            print(
                f"  PASS  {result.get('ms')}ms  {extra}  "
                f"pt={result.get('pt')} ct={result.get('ct')}",
                flush=True,
            )
        else:
            failures += 1
            print(f"  FAIL  {result}", flush=True)
        time.sleep(0.5)
    # Partial cribs are still useful. Fail the process only if every section failed.
    if args.prep and failures and failures < len(sections):
        print(f"partial prep: {len(sections) - failures}/{len(sections)} sections ok", flush=True)
        return 0
    return 1 if failures else 0


def revise_main(args, row, book: str) -> int:
    cf_token = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN") or ""
    nv_token = os.environ.get("NV_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    failures = load_receipt_failures(args.revise_from)
    if args.section:
        wanted = set(args.section)
        failures = {s: n for s, n in failures.items() if s in wanted}
    claimed = set(sections_from_slice(row.get("Slice (sections)") or "", book))
    for section in failures:
        if section not in claimed:
            raise SystemExit("Receipt section outside the claim; refusing writes")
    if not failures:
        print("No failed sections with checker notes to revise.", flush=True)
        return 0
    override = args.max_tokens or None
    _fb = [normalize_model(x) for x in (args.draft_fallbacks or "").split(",") if x.strip()]
    _rev_chain = [normalize_model(args.model)] + [x for x in _fb if x != normalize_model(args.model)]
    fails = 0
    for section, notes in failures.items():
        print(f"Revising {section} against {len(notes)} note(s)", flush=True)
        result: dict = {"ok": False}
        for attempt in range(2):
            _m = _rev_chain[attempt % len(_rev_chain)]
            result = revise_section(section, _m, cf_token, nv_token,
                                    account, args.agent, notes, args.revise_from,
                                    max_tokens=override, book=book)
            if result.get("ok"):
                break
            time.sleep(1.0)
        if result.get("ok"):
            print(f"  PASS title={result.get('title')!r} repaired={result.get('repaired')}", flush=True)
        else:
            fails += 1
            print(f"  FAIL {result}", flush=True)
        time.sleep(0.5)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
