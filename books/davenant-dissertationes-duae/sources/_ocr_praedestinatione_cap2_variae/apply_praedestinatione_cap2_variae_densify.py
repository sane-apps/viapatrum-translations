#!/usr/bin/env python3
"""De praedestinatione Cap. II Variae densify — tip 221 → 228. Packet praedestinatione_cap2_variae_densify."""
from __future__ import annotations

import hashlib
import json
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
OCR = BOOK / "sources/_ocr_praedestinatione_cap2_variae"
PIPE = Path.home() / "SaneApps/clients/translations/pipeline"
ROOT = Path.home() / "SaneApps/clients/translations"
PACKET = "praedestinatione_cap2_variae_densify"
CHECK = PIPE / "check_pass_ab.py"
TIP_BEFORE = 221
HOLD_FLOOR = 3757
HOLD_START_PATH = OCR / "hold_start_epoch.txt"

SECTIONS = json.loads((OCR / "sections_all.json").read_text(encoding="utf-8"))


def live_section_count() -> tuple[int, int]:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"(\d+)\s*treatises.*?(\d+)\s*sections", html, re.I | re.S)
    if not m:
        raise SystemExit("could not parse live section count")
    return int(m.group(1)), int(m.group(2))


def wait_hold() -> str:
    hold_start = int(HOLD_START_PATH.read_text().strip().split("=")[-1])
    while True:
        works, secs = live_section_count()
        elapsed = time.time() - hold_start
        print(f"live {works}/{secs}; elapsed {elapsed/60:.1f} min; floor>{HOLD_FLOOR}", flush=True)
        if secs > HOLD_FLOOR or elapsed >= 12 * 60:
            eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
            tip = int(eng[-1]["section"])
            note = (
                f"Hold cleared ({'live sections ' + str(secs) + ' > ' + str(HOLD_FLOOR) if secs > HOLD_FLOOR else f'12-minute wait elapsed ({elapsed/60:.1f} min from hold_start={hold_start})'}); "
                f"live {works}/{secs}; disk tip {tip} before append."
            )
            if tip != TIP_BEFORE:
                raise SystemExit(f"disk tip {tip} != {TIP_BEFORE} after hold; abort")
            return note
        time.sleep(30)


def write_latin_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_praedestinatione_cap2_variae_latin_lock.txt"
    header = (
        "DE PRAEDESTINATIONE ET REPROBATIONE — Cap. II Variae densify lock\n"
        "Witnesses: IA 1650 Daniel PDF pdftotext pp.~132–134 + tesseract lat+eng + DjVu + sense normalize.\n"
        "Scope: Cap. II Variae illorum sententiae (election from foresight merits / Pelagian–Semipelagian opening); after Cap. 1 prol. IV; before Cap. II Scholastics.\n\n"
    )
    lock.write_text(header + "\n\n".join(s["latin"] for s in secs) + "\n", encoding="utf-8")
    print("wrote", lock.name)


def extend_morte_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    if not lock.exists():
        return
    text = lock.read_text(encoding="utf-8")
    if "Cap. II Variae densify append" in text or "Variæ illorum sententiæ referuntur" in text or "Variae illorum sententiae referuntur" in text:
        print("morte lock already has Cap II Variae; skip append")
        return
    block = "\n\n=== De praedestinatione Cap. II Variae densify append ===\n" + "\n\n".join(
        f"[{s['section']}] {s['latin']}" for s in secs
    )
    lock.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    print("extended morte latin lock")


def append_rows(secs: list[dict], tip_before: int) -> int:
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    assert len(eng) == len(src) == tip_before, (len(eng), len(src), tip_before)
    assert int(eng[-1]["section"]) == tip_before
    for sec in secs:
        eng.append(
            {
                "section": sec["section"],
                "title": sec["title"],
                "english": [sec["pass_b"]],
                "notes_covered": sec.get("notes_covered") or [],
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
    return len(eng)


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    blurb = meta.get("blurb") or meta.get("description") or ""
    note = "; De praedestinatione Cap. II Variae (Pelagian opening) tip."
    if isinstance(blurb, str) and "Cap. II Variae" not in blurb:
        if "blurb" in meta:
            meta["blurb"] = blurb.rstrip(".") + note
        elif "description" in meta:
            meta["description"] = blurb.rstrip(".") + note
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated meta section_count", tip)


def tip_ready() -> str:
    eng = TRANS / "morte_christi_english.json"
    src = TRANS / "morte_christi_source.json"
    r = subprocess.run(
        [sys.executable, str(CHECK), "--tip-ready", str(eng), str(src)],
        capture_output=True,
        text=True,
    )
    out = (r.stdout + r.stderr).strip()
    print("tip-ready:", out)
    if "tip-ready: ok" not in out:
        raise SystemExit(f"tip-ready failed: {out}")
    return out


def build_packet(tip: int) -> str:
    AUDIT.mkdir(parents=True, exist_ok=True)
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    aliases = {str(i): str(i) for i in range(1, tip + 1)}
    packet = {
        "identity": {
            "author": "John Davenant",
            "work": "Two Dissertations (De morte Christi Cap. 1-7 + De praedestinatione Prefatio/Cap.1–Cap.II Variae partial)",
            "edition": (
                "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
                "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
                "Partial: De morte Christi Cap. 1-7 close + De praedestinatione title, Prefatio, "
                "Cap. 1 Prolegomena I-IV + Cap. II Variae illorum sententiae (Pelagian–Semipelagian opening) "
                "(before Cap. II Scholastics / Vasquez)."
            ),
            "locus_scheme": "section",
            "source_url": "https://archive.org/details/bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650",
            "locus_aliases": aliases,
        },
        "scope": {
            "packet_stem": PACKET,
            "before": TIP_BEFORE,
            "after": tip,
            "added": [s["section"] for s in SECTIONS],
            "locus": "De praedestinatione Cap. II Variae illorum sententiae (election from foresight merits / Pelagian opening)",
            "next_locus": "Cap. II Scholastici (causes of election error; then Pontificii / Vasquez)",
            "punch_x": "NO",
            "ship": "NO",
        },
        "sections": [
            {
                "section": s["section"],
                "title": s["title"],
                "english": eng[s["section"] - 1]["english"],
                "latin": src[s["section"] - 1]["latin"],
            }
            for s in SECTIONS
        ],
    }
    path = AUDIT / f"{PACKET}.packet.json"
    raw = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"
    path.write_text(raw, encoding="utf-8")
    pid = hashlib.sha256(raw.encode()).hexdigest()
    review = {
        "packet_stem": PACKET,
        "verdict": "source_verified_partial",
        "pass_a_ne_b": True,
        "notes": "De praedestinatione Cap. II Variae densify; Cap. II Scholastics / Vasquez remain.",
        "punch_x": "NO",
    }
    (AUDIT / f"{PACKET}.review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote packet", path.name, "id", pid[:16])
    return pid


def write_receipt(before: int, after: int, packet_id: str, gates: dict, hold_note: str) -> None:
    receipt = {
        "packet_stem": PACKET,
        "packet": str(AUDIT / f"{PACKET}.packet.json"),
        "review": str(AUDIT / f"{PACKET}.review.json"),
        "packet_id": packet_id,
        "before": before,
        "after": after,
        "added_sections": [s["section"] for s in SECTIONS],
        "locus": "De praedestinatione Cap. II Variae illorum sententiae (election from foresight merits / Pelagian opening)",
        "next_locus": "Cap. II Scholastici (causes of election error; then Pontificii / Vasquez)",
        "gates": gates,
        "punch_x": "NO",
        "ship": "NO",
        "claim": "davenant-dissertationes-densify stays claimed",
        "latin_lock": str(BOOK / "sources/_davenant_praedestinatione_cap2_variae_latin_lock.txt"),
        "hold_note": hold_note,
    }
    path = AUDIT / f"{PACKET}.receipt.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote receipt", path.name)


def prepend_handoff(before: int, after: int, hold_note: str) -> None:
    book_h = BOOK / "SESSION_HANDOFF.md"
    root_h = ROOT / "SESSION_HANDOFF.md"
    ts = time.strftime("%Y-%m-%d ~%H:%M ET")
    block = f"""## {ts} (Cursor — Davenant De praedestinatione Cap. II Variae densify)

CoS densify: Cap. II Variæ illorum sententiæ (election from foresight merits / Pelagian opening). Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit `publication-review.json`; did not ship; did not commit; did not run Logos or ai_promote. {hold_note}

### Bound this job (not shipped)
- **Davenant** `davenant-dissertationes-duae`: Cap. II Variae tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract + DjVu) with lock. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet `{PACKET}`. Honest partial — **not** whole Dissertationes. Cap. II Scholastici / Vasquez remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16)
- Cap. II Scholastici through remainder of De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.

---

"""
    for path in (book_h, root_h):
        if path == book_h and not path.exists():
            continue
        prev = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(block + prev, encoding="utf-8")
        print("prepended", path)


def main() -> None:
    host = subprocess.check_output(["hostname"], text=True).strip()
    assert host == "Stephans-Mac-mini.local", host

    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    tip_now = int(eng[-1]["section"])
    print(f"disk tip before append: {tip_now} (n={len(eng)})")
    if tip_now != TIP_BEFORE:
        raise SystemExit(f"disk tip {tip_now} != expected start {TIP_BEFORE}; abort (do not rewrite)")

    for sec in SECTIONS:
        p = JUST / f"morte_{sec['section']}.json"
        if not p.exists():
            raise SystemExit(f"missing justification {p}")
        r = subprocess.run(
            [sys.executable, str(CHECK), str(p)],
            capture_output=True,
            text=True,
        )
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 or "fail=0" not in out:
            raise SystemExit(f"recheck FAIL {p.name}: {out}")

    write_latin_lock(SECTIONS)
    hold_note = wait_hold()
    before = TIP_BEFORE
    after = append_rows(SECTIONS, TIP_BEFORE)
    update_meta(after)
    extend_morte_lock(SECTIONS)
    tip_out = tip_ready()
    packet_id = build_packet(after)
    gates = {
        "hostname": "Stephans-Mac-mini.local",
        "check_pass_ab": "ok fail=0 on morte_222..228",
        "tip_ready": tip_out,
        "punch_x": "NO",
        "ship": "NO",
        "claim": "davenant-dissertationes-densify stays claimed",
    }
    write_receipt(before, after, packet_id, gates, hold_note)
    prepend_handoff(before, after, hold_note)
    print("DONE", before, "->", after, "Punch X=NO")


if __name__ == "__main__":
    main()
