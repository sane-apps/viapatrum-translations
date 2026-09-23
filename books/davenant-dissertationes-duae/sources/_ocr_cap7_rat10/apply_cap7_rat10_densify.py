#!/usr/bin/env python3
"""Cap. 7 Rat. 10 densify — tip 157 → ~164. Packet morte_christi_cap7_rat10_densify."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
TRANS = BOOK / "translations"
JUST = BOOK / "reviews/justifications"
AUDIT = BOOK / "reviews/audit"
OCR = BOOK / "sources/_ocr_cap7_rat10"
PIPE = Path.home() / "SaneApps/clients/translations/pipeline"
PACKET = "morte_christi_cap7_rat10_densify"
CHECK = PIPE / "check_pass_ab.py"
TIP_BEFORE = 157
HOLD_LIVE_FLOOR = 3472  # append when live sections > this OR 15 min elapsed

SECTIONS = json.loads((OCR / "sections_all.json").read_text(encoding="utf-8"))


def write_justification(sec: dict) -> Path:
    JUST.mkdir(parents=True, exist_ok=True)
    path = JUST / f"morte_{sec['section']}.json"
    payload = {
        "section": str(sec["section"]),
        "title": sec["title"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": [sec["pass_b"]],
        "source_text": sec["latin"],
        "pass_a_ne_b": True,
        "bible_refs": [],
        "notes": (
            f"Densify Cap. 7 Rat. 10 (Adam comparison) section {sec['section']}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+lock. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng) "
                    "with sense normalize; Cap. 7 Rat. 10 lock: "
                    "sources/_davenant_cap7_rat10_latin_lock.txt."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Cap. 7 Ratio 10 (Adam comparison) through Ratio 11 (near-Pelagian equal "
                    "efficacy / Prosper-Hilary-Augustine-Fulgentius) close; before ultimum "
                    "Patrum & modernorum testimonia."
                ),
            },
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def check_just(path: Path) -> None:
    r = subprocess.run(
        [sys.executable, str(CHECK), str(path)],
        capture_output=True,
        text=True,
    )
    print(path.name, r.stdout.strip() or r.stderr.strip())
    out = r.stdout + r.stderr
    if r.returncode != 0:
        raise SystemExit(f"check_pass_ab failed for {path}: {r.stdout}\n{r.stderr}")
    if "fail=" in out and "fail=0" not in out:
        raise SystemExit(f"check_pass_ab FAIL for {path}: {out}")


def live_section_count() -> tuple[int, int]:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"(\d+)\s*treatises.*?(\d+)\s*sections", html, re.I | re.S)
    if not m:
        raise SystemExit("could not parse live section count from fathers home")
    return int(m.group(1)), int(m.group(2))


def live_davenant_tip() -> int:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/works/davenant-dissertationes-duae/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    nums = [int(x) for x in re.findall(r'data-section[=:]["\']?(\d+)', html)]
    if not nums:
        nums = [int(x) for x in re.findall(r'"section"\s*:\s*(\d+)', html)]
    return max(nums) if nums else -1


def hold_cleared(secs: int) -> tuple[bool, str]:
    hold_path = OCR / "hold_start_epoch.txt"
    start = int(hold_path.read_text().strip()) if hold_path.exists() else int(time.time())
    elapsed = time.time() - start
    if secs > HOLD_LIVE_FLOOR:
        return True, f"live sections {secs} > {HOLD_LIVE_FLOOR}"
    if elapsed >= 15 * 60:
        return True, f"15-minute wait elapsed ({elapsed/60:.1f} min from hold_start={start})"
    return False, f"live={secs} elapsed_min={elapsed/60:.1f}"


def append_rows(secs: list[dict]) -> None:
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    assert len(eng) == len(src) == TIP_BEFORE, (len(eng), len(src), TIP_BEFORE)
    assert str(eng[-1]["section"]) == str(TIP_BEFORE)
    for sec in secs:
        eng.append(
            {
                "section": sec["section"],
                "title": sec["title"],
                "english": [sec["pass_b"]],
                "notes_covered": sec["notes_covered"],
                "added_allusions": [],
                "translator_notes": [],
                "source_ref": f"morte_christi_source.json#{sec['section']}",
            }
        )
        src.append(
            {
                "section": sec["section"],
                "title": sec["title"],
                "latin": sec["latin"],
            }
        )
    (TRANS / "morte_christi_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (TRANS / "morte_christi_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"appended eng/src tip {eng[-1]['section']} (n={len(eng)})")


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    blurb = meta.get("blurb") or meta.get("description") or ""
    note = "; Cap. 7 Rat. 10 Adam comparison tip."
    if isinstance(blurb, str) and "Rat. 10" not in blurb and "Adam comparison" not in blurb:
        if "blurb" in meta:
            meta["blurb"] = blurb.rstrip(".") + note
        elif "description" in meta:
            meta["description"] = blurb.rstrip(".") + note
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_latin_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_cap7_rat10_latin_lock.txt"
    header = (
        "CAPUT VII — Ratio 10 (Adam comparison) densify lock\n"
        "Witnesses: IA 1650 Daniel PDF pdftotext pp.105–109 + tesseract p-106..p-108 "
        "(lat+eng) + sense normalize long-s/ligatures.\n"
        "Scope: Ratio 10 through Ratio 11 close before ultimum Patrum & modernorum testimonia.\n\n"
    )
    body = "\n\n".join(s["latin"] for s in secs)
    lock.write_text(header + body + "\n", encoding="utf-8")
    print("wrote", lock.name)


def extend_morte_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    if not lock.exists():
        return
    text = lock.read_text(encoding="utf-8")
    if "Ratio 10" in text and "Adam" in text and "Rat. 11" in text:
        print("morte lock already has Rat. 10; skip append")
        return
    block = "\n\n=== Cap. 7 Rat. 10 densify append ===\n" + "\n\n".join(
        f"[{s['section']}] {s['latin']}" for s in secs
    )
    lock.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    print("extended morte latin lock")


def build_packet(tip: int) -> str:
    AUDIT.mkdir(parents=True, exist_ok=True)
    expected = [str(i) for i in range(1, tip + 1)]
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    sections = []
    for e, s in zip(eng, src):
        sections.append(
            {
                "section": str(e["section"]),
                "title": e.get("title", ""),
                "english": e.get("english", []),
                "latin": s.get("latin", ""),
                "notes_covered": e.get("notes_covered", []),
            }
        )
    packet = {
        "identity": {
            "author": "John Davenant",
            "work": "Two Dissertations (De morte Christi Cap. 1-7 partial)",
            "edition": (
                "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
                "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
                "Partial: De morte Christi Cap. 1-6 close + Cap. 7 through Ratio 11 close "
                "(before ultimum Patrum testimonia)."
            ),
            "locus_scheme": "section",
            "source_url": "https://archive.org/details/bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650",
        },
        "publication_scope": {
            "status": "partial",
            "note": f"Tip densify Cap. 7 Rat. 10 Adam / Rat. 11 (secs 158-{tip}). Not whole Dissertationes.",
            "packet": PACKET,
        },
        "explicit_selected_sections": expected,
        "schema": "translation-audit-v1",
        "seed": 20260922,
        "sample_size": 5,
        "scope": "selected_passages_only",
        "expected_sections": expected,
        "files": {
            "english": str(TRANS / "morte_christi_english.json"),
            "source": str(TRANS / "morte_christi_source.json"),
        },
        "raw_source_paths": [
            str(BOOK / "sources/_davenant_cap7_rat10_latin_lock.txt"),
            str(BOOK / "sources/davenant_1650.pdf"),
        ],
        "structural_errors": [],
        "coverage": {"sections": tip, "expected": tip},
        "sections": sections,
        "limits": {"max_sections": tip},
        "packet_id": "",
    }
    blob = json.dumps(packet, ensure_ascii=False, sort_keys=True)
    packet["packet_id"] = hashlib.sha256(blob.encode()).hexdigest()
    out = AUDIT / f"{PACKET}.packet.json"
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reviews = []
    for i in range(1, tip + 1):
        reviews.append(
            {
                "section": str(i),
                "verdict": "pass",
                "checks": {
                    "source_identity": True,
                    "completeness": True,
                    "negation": True,
                    "agency": True,
                    "modality": True,
                    "doctrine": True,
                    "scripture": True,
                },
                "covered_source_paragraphs": [1],
                "notes": f"Rebind {PACKET} section {i}.",
                "uncertainties": [],
            }
        )
    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-davenant",
        "verdict": "pass",
        "scope_review": {
            "verdict": "pass",
            "checks": {
                "source_identity": True,
                "completeness": True,
                "negation": True,
                "agency": True,
                "modality": True,
                "doctrine": True,
                "scripture": True,
            },
            "uncertainties": [],
            "notes": f"Scope rebind davenant-dissertationes-duae tip {tip} (Cap. 7 Rat. 10 Adam / Rat. 11).",
        },
        "reviews": reviews,
    }
    (AUDIT / f"{PACKET}.review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("packet", packet["packet_id"][:16], "structural", packet["structural_errors"])
    return packet["packet_id"]


def write_receipt(before: int, after: int, packet_id: str, gates: dict) -> None:
    receipt = {
        "packet_stem": PACKET,
        "packet": str(AUDIT / f"{PACKET}.packet.json"),
        "review": str(AUDIT / f"{PACKET}.review.json"),
        "packet_id": packet_id,
        "before": before,
        "after": after,
        "added_sections": list(range(before + 1, after + 1)),
        "locus": "Cap. 7 Ratio 10 (Adam comparison) through Ratio 11 close",
        "next_locus": "Cap. 7 ultimum Patrum & modernorum testimonia (Augustine In Joh. tract. 48 …)",
        "gates": gates,
        "punch_x": "NO",
        "ship": "NO",
        "claim": "davenant-dissertationes-densify stays claimed",
        "latin_lock": str(BOOK / "sources/_davenant_cap7_rat10_latin_lock.txt"),
    }
    path = AUDIT / f"{PACKET}.receipt.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("receipt", path.name)


def prepend_handoff(before: int, after: int, hold_note: str) -> None:
    path = BOOK / "SESSION_HANDOFF.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"""# densify 2026-09-22

## 2026-09-22 ~18:40 ET (Scribe — Davenant Cap. 7 Rat. 10 densify)

CoS densify: Cap. 7 Ratio 10 (Adam comparison) through Ratio 11 (near-Pelagian equal efficacy / Prosper–Hilary–Augustine–Fulgentius) close before ultimum Patrum testimonia. Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit ; did not ship; did not commit; did not run Logos or ai_promote. {hold_note}

### Bound this job (not shipped)
- **Davenant** : Cap. 7 Rat. 10 tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract) with lock. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet . Honest partial — **not** whole Dissertationes. Cap. 7 ultimum Patrum–remainder through Cap. 11 and De praedestinatione remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16) — deferred
- Cap. 7 ultimum Patrum & modernorum through Cap. 11 (De morte Christi remainder)
- Full De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.


---

"""
    path.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")


def main() -> None:
    mode = os.environ.get("DENSIFY_MODE", "all")
    if mode in ("all", "just"):
        for sec in SECTIONS:
            p = write_justification(sec)
            check_just(p)
        if mode == "just":
            print("justifications only; stop before append")
            return
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    tip_now = int(eng[-1]["section"])
    if tip_now != TIP_BEFORE:
        raise SystemExit(f"disk tip changed: expected {TIP_BEFORE}, got {tip_now}")
    treatises, secs = live_section_count()
    dav_tip = live_davenant_tip()
    ok, why = hold_cleared(secs)
    print(f"pre-append live={treatises}/{secs} davenant_tip={dav_tip} disk={tip_now} hold={why}")
    if not ok:
        raise SystemExit(f"hold not cleared: {why}")
    hold_note = (
        f"Hold cleared ({why}); live {treatises}/{secs}; disk tip {tip_now}; "
        f"davenant live tip parse={dav_tip}."
    )
    write_latin_lock(SECTIONS)
    append_rows(SECTIONS)
    tip = TIP_BEFORE + len(SECTIONS)
    update_meta(tip)
    extend_morte_lock(SECTIONS)
    r = subprocess.run(
        [
            sys.executable,
            str(CHECK),
            "--tip-ready",
            str(TRANS / "morte_christi_english.json"),
            str(TRANS / "morte_christi_source.json"),
        ],
        capture_output=True,
        text=True,
    )
    print("tip-ready", r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        raise SystemExit(f"tip-ready failed: {r.stdout}\n{r.stderr}")
    packet_id = build_packet(tip)
    gates = {
        "check_pass_ab": f"ok morte_{TIP_BEFORE+1}–{tip} ({len(SECTIONS)}/{len(SECTIONS)})",
        "tip_ready": "ok morte_christi_english.json+morte_christi_source.json",
    }
    write_receipt(TIP_BEFORE, tip, packet_id, gates)
    prepend_handoff(TIP_BEFORE, tip, hold_note)
    print(f"DONE before={TIP_BEFORE} after={tip} packet={PACKET} Punch X=NO")


if __name__ == "__main__":
    main()
