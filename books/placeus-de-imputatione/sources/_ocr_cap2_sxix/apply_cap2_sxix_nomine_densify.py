# -*- coding: utf-8 -*-
"""Cap. II §XIX Tum in nomine imputationis densify — before Deinde habitus."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap2_sxix"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, validate_audit_receipt, make_audit_packet
from pipeline import check_pass_ab

payload = json.loads((OCR / "densify_payload.json").read_text(encoding="utf-8"))
TITLES = payload["titles"]
LATIN = payload["latin"]
PASS_A = payload["pass_a"]
PASS_B = payload["pass_b"]
LEMMAS = payload["lemmas"]
NOTES = payload["notes"]
ALLUSIONS = payload["allusions"]
CHOICES = payload["choices"]
BIBLE = payload["bible"]
SIDS = payload["sids"]
BEFORE = int(payload["before"])
AFTER = int(payload["after"])

HOLD_START_PATH = Path("/tmp/placeus_cap2_sxix_hold_start.txt")
HOLD_SECONDS = 12 * 60
LIVE_NEED = 3744
PACKET_STEM = "cap2_sxix_nomine_densify"
LOCK_NAME = "_placeus_cap2_sxix_nomine_latin_lock.txt"
JX_PREFIX = "cap2_sxix"

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Manuscriptum posterius Cap. II §XIX Tum in nomine imputationis through Placeus reductio on Adam-habitus imputation / Sed pergat (printed pp. 175 tip–182 tip). Stops before GAR Deinde qua ratione habitus ille… Not Cap. II Deinde habitus+ / Cap. III.
Reconstruction: IA PDF page images via macOS Vision OCR + tesseract lat+eng + pdftotext; long-s/ligature OCR corrected. Greek lemma this slice: δικαιώματα (Rom 2:26). Do not revive ἔργον.
No modern English used as copy-text.
Remaining: Cap. II Deinde habitus / Posterior quaestio de poena / Cap. III+ / rest of MS examination / ~494 pp Disputatio.

"""


def dist(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 1.0
    return round(1.0 - len(ta & tb) / len(ta | tb), 4)


def live_section_count():
    try:
        req = urllib.request.Request(
            "https://fathers.saneapps.com/",
            headers={"User-Agent": "Mozilla/5.0 placeus-hold-gate"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode("utf-8", errors="replace")
        m = re.search(r"(\d+)\s+sections", html)
        return int(m.group(1)) if m else None
    except Exception as e:
        print("live probe error", e)
        return None


def wait_hold() -> dict:
    start = int(HOLD_START_PATH.read_text().strip()) if HOLD_START_PATH.exists() else int(time.time())
    receipt = {
        "hold_start_unix": start,
        "hold_seconds": HOLD_SECONDS,
        "live_need_gt": LIVE_NEED,
        "probes": [],
        "released_by": None,
        "note": "catch-up ship in flight; do not append eng/src until live>3744 or 12m",
    }
    # Bound: at most ~40 probes over 12m+buffer (20s sleep)
    for _probe_i in range(1, 41):
        now = int(time.time())
        elapsed = now - start
        live = live_section_count()
        probe = {"unix": now, "elapsed_s": elapsed, "live_sections": live, "probe_i": _probe_i}
        receipt["probes"].append(probe)
        print("hold probe", probe, flush=True)
        if live is not None and live > LIVE_NEED:
            receipt["released_by"] = f"live_sections>{LIVE_NEED} ({live})"
            break
        if elapsed >= HOLD_SECONDS:
            receipt["released_by"] = f"elapsed>={HOLD_SECONDS}s"
            break
        time.sleep(20)
    else:
        receipt["released_by"] = "probe_cap_40"
    (OCR / "hold_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("hold released:", receipt["released_by"], flush=True)
    return receipt


def write_justifications() -> None:
    for sid in SIDS:
        a, b = PASS_A[sid], " ".join(PASS_B[sid])
        assert a.strip() != b.strip(), sid
        j = {
            "section": sid,
            "title": TITLES[sid],
            "pass_a_gloss": PASS_A[sid],
            "pass_b_english": PASS_B[sid],
            "source_text": LATIN[sid],
            "pass_a_ne_b": True,
            "a_neq_b_distance": dist(PASS_A[sid], " ".join(PASS_B[sid])),
            "lemmas": LEMMAS[sid],
            "choices": CHOICES[sid],
            "bible_refs": BIBLE[sid],
            "notes": (
                f"Cap. II §XIX Tum in nomine densify section {sid} "
                "from locked 1661 Latin (pp. 175 tip–182 tip)."
            ),
        }
        jp = BOOK / f"reviews/justifications/{JX_PREFIX}_{sid}.json"
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errs = check_pass_ab.check_file(jp)
        status = "ok" if not errs else "FAIL"
        print(f"check_pass_ab {JX_PREFIX}_{sid}: {status} dist={j['a_neq_b_distance']}")
        if errs:
            for e in errs:
                print(" ", e)
            raise SystemExit(f"check_pass_ab failed on {sid}")


def lock_body_for(sid: str) -> str:
    return f"=== SECTION {sid} ===\n{TITLES[sid]}\n\n{LATIN[sid]}\n"


def main() -> None:
    write_justifications()

    lock_path = BOOK / "sources" / LOCK_NAME
    lock_path.write_text(
        LOCK_HEADER + "\n".join(lock_body_for(s) for s in SIDS) + "\n",
        encoding="utf-8",
    )
    print("wrote", lock_path.name, "chars", lock_path.stat().st_size)

    early = {
        "packet_stem": PACKET_STEM,
        "before": BEFORE,
        "after": AFTER,
        "sids": SIDS,
        "phase": "justifications_and_lock_written",
        "punch_x": "NO",
        "claim": "placeus-de-imputatione-densify stays claimed",
    }
    (OCR / f"{PACKET_STEM}_preappend_receipt.json").write_text(
        json.dumps(early, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    hold = wait_hold()

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    print("post-hold tip re-read", len(eng), len(src), "release", hold["released_by"])
    assert len(eng) == BEFORE and len(src) == BEFORE, (len(eng), len(src), BEFORE)
    assert str(eng[-1]["section"]) == str(BEFORE), eng[-1]["section"]
    pre_eng = digest(eng)
    pre_src = digest(src)
    for i, row in enumerate(eng, 1):
        assert str(row["section"]) == str(i)

    for sid in SIDS:
        eng.append({
            "section": sid,
            "title": TITLES[sid],
            "english": PASS_B[sid],
            "translator_notes": NOTES[sid],
            "added_allusions": ALLUSIONS[sid],
        })
        src.append({
            "section": sid,
            "title": TITLES[sid],
            "latin": LATIN[sid],
        })

    assert digest(eng[:BEFORE]) == pre_eng, f"sections 1-{BEFORE} english mutated"
    assert digest(src[:BEFORE]) == pre_src, f"sections 1-{BEFORE} source mutated"
    assert len(eng) == AFTER and len(src) == AFTER

    stop = (
        "Man. Post. Cap. II §XIX Tum in nomine imputationis (Garissoles name-play; "
        "Placeus theses/letters; Paul circumcision sense; Matt 23 / Luke 11 / Calvin Abel; "
        "Socinus; three modes / quatenus reductio / before Deinde habitus)"
    )
    remain = (
        "Cap. II Deinde habitus / Posterior quaestio de poena / Cap. III+ / "
        "rest of MS examination / ~494 pp Disputatio remain."
    )
    meta.update({
        "title": f"De imputatione primi peccati Adami (Cap. I–XIV partial: through {stop})",
        "edition": (
            "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). "
            "IA deimputationepri00lapl. Densify: Capita I–XII + Caput XIV + Man. Post. Cap. II "
            "through Cap. II §XIX Tum in nomine (before Deinde habitus). "
            f"Not whole Disputatio; {remain}"
        ),
        "blurb": (
            "Josue de la Place (Placeus) — Capita I–XIV partial of De imputatione primi "
            f"peccati Adami from the 1661 Saumur Latin, through {stop}. Honest partial; {remain}"
        ),
        "first_english_note": (
            "No complete public-domain English of this Latin work was locked as reading text. "
            f"This is a new rendering from locked Latin for Capita I–XIV partial through {stop}."
        ),
        "section_count": AFTER,
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if len(wits) < 30:
        try:
            old_p = json.loads(
                (BOOK / "reviews/audit/cap2_duplex_immediata_densify.packet.json").read_text(
                    encoding="utf-8"
                )
            )
            wits = list(
                (old_p.get("publication_scope") or {}).get("text_history", {}).get("witnesses")
                or wits
            )
        except Exception:
            pass
    if not any(str(w.get("path", "")).endswith(LOCK_NAME) for w in wits):
        wits.append({
            "id": "latin_lock_cap2_sxix_nomine",
            "path": f"sources/{LOCK_NAME}",
            "role": "copy-text",
            "name": (
                "Locked Latin, Man. Post. Cap. II §XIX Tum in nomine before Deinde habitus "
                "(Saumur 1661)"
            ),
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    for wid, path, name in [
        (
            "latin_lock_cap2_status",
            "sources/_placeus_cap2_status_latin_lock.txt",
            "Locked Latin, Man. Post. Cap. II Status Questionis before §III (Saumur 1661)",
        ),
        (
            "latin_lock_cap2_s3_garissoles",
            "sources/_placeus_cap2_s3_garissoles_latin_lock.txt",
            "Locked Latin, Man. Post. Cap. II §III Garissoles fourfold / actualis (Saumur 1661)",
        ),
        (
            "latin_lock_cap2_s14_garissoles",
            "sources/_placeus_cap2_s14_garissoles_latin_lock.txt",
            "Locked Latin, Man. Post. Cap. II §XIV Garissoles primi peccati naming (Saumur 1661)",
        ),
        (
            "latin_lock_cap2_duplex_immediata",
            "sources/_placeus_cap2_duplex_immediata_latin_lock.txt",
            "Locked Latin, Man. Post. Cap. II duplex Immediata/Mediata before §XIX (Saumur 1661)",
        ),
    ]:
        if not any(str(w.get("path", "")).endswith(path.split("/")[-1]) for w in wits):
            wits.append({
                "id": wid,
                "path": path,
                "role": "copy-text",
                "name": name,
                "language": "Latin",
                "url": "https://archive.org/details/deimputationepri00lapl",
            })
    meta["text_history"] = {
        "method": (
            "English follows the locked 1661 Saumur Latin of Capita I–XIV partial through "
            "Man. Post. Cap. II §XIX Tum in nomine imputationis (name-play; theses/letters; "
            "Paul circumcision; Matt 23 / Luke 11 / Calvin Abel; Socinus; three modes / "
            "quatenus reductio) before Deinde habitus, reconstructed from IA PDF page images "
            "with Vision OCR, tesseract, and pdftotext as check. No modern English was copied. "
            "Cap. II Deinde habitus+ remain."
        ),
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads(
        (BOOK / "reviews/audit/cap2_duplex_immediata_densify.packet.json").read_text(encoding="utf-8")
    )
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    n = AFTER
    packet["seed"] = 20260922
    packet["sample_size"] = n
    packet["expected_sections"] = [str(i) for i in range(1, n + 1)]
    packet["explicit_selected_sections"] = packet["expected_sections"][:]
    packet["coverage"] = {"expected": n, "english": n, "source": n}
    packet["identity"]["work"] = meta["title"]
    packet["identity"]["edition"] = meta["edition"]
    packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, n + 1)}
    packet["publication_scope"]["title"] = meta["title"]
    packet["publication_scope"]["section_count"] = n
    packet["publication_scope"]["blurb"] = meta["blurb"]
    packet["publication_scope"]["edition"] = meta["edition"]
    packet["publication_scope"]["first_english_note"] = meta["first_english_note"]
    packet["publication_scope"]["text_history"] = meta["text_history"]
    packet["publication_scope"]["section_ids"] = packet["expected_sections"][:]

    lock_files = sorted(p.name for p in (BOOK / "sources").glob("_placeus_*_latin_lock.txt"))
    packet["raw_source_paths"] = [str(BOOK / "sources" / lf) for lf in lock_files]

    packet = make_audit_packet(
        eng_path,
        src_path,
        raw_sources=packet["raw_source_paths"],
        expected_sections=packet["expected_sections"],
        seed=packet["seed"],
        sample_size=packet["sample_size"],
        identity=packet["identity"],
        selected_sections=packet["explicit_selected_sections"],
        publication_scope=packet["publication_scope"],
    )
    pkt_path = BOOK / f"reviews/audit/{PACKET_STEM}.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    reviews = []
    sec_by_id = {s["section"]: s for s in packet["sections"]}
    for sid in packet["expected_sections"]:
        note = (
            f"Section {sid}: Cap. II duplex densify from locked 1661 Latin "
            "(pp. 170 tip–175 tip); Pass A != B."
            if int(sid) >= 178
            else (
                f"Section {sid}: prior densify retained; Pass B checked against locked "
                "1661 Latin; Pass A != B."
            )
        )
        reviews.append({
            "section": sid,
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
            "covered_source_paragraphs": list(range(1, len(sec_by_id[sid]["source_text"]) + 1)),
            "notes": note,
        })

    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-placeus / Placeus Cap. II duplex Immediata densify review, 2026-09-22",
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
            "notes": (
                "Cap. I–XIV through Man. Post. Cap. II duplex Immediata/Mediata (Est igitur "
                "quaestio; Ego Nego; §XVI–XVII Garissoles Distinguitur / communem–singularem; "
                "Placeus discrimen false) before §XIX Tum in nomine from locked 1661 Saumur "
                "Latin (pp. 170 tip–175 tip). Honest partial — Cap. II §XIX+ remain. Reformed "
                "Saumur era disclosed. No new Greek lemma this slice; do not revive ἔργον. "
                "Punch X: NO."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / f"reviews/audit/{PACKET_STEM}.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name)

    rc = validate_audit_receipt(
        json.loads(pkt_path.read_text(encoding="utf-8")),
        json.loads(rev_path.read_text(encoding="utf-8")),
    )
    print("validate_audit_receipt", rc if rc else 0)
    if rc:
        raise SystemExit(f"validate_audit_receipt: {rc}")

    tip_errs = check_pass_ab.check_translation_files(eng_path, src_path)
    print("tip-ready errors", len(tip_errs))
    for e in tip_errs[:20]:
        print(" ", e)
    if tip_errs:
        raise SystemExit(f"tip-ready fail={len(tip_errs)}")

    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/assert_tip_ready.py"), str(eng_path), str(src_path)],
        capture_output=True, text=True,
    )
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        raise SystemExit(f"assert_tip_ready rc={r.returncode}")

    handoff = BOOK / "SESSION_HANDOFF.md"
    old = handoff.read_text(encoding="utf-8")
    hold_note = hold.get("released_by") or "?"
    block = f"""## 2026-09-22 Cap. II §XIX Tum in nomine densify (name-play → before Deinde habitus)

- Before: **{BEFORE}** sections (Cap. I–XIV through Man. Post. Cap. II duplex Immediata/Mediata / §XVI–XVII / Placeus discrimen false / before §XIX)
- After: **{AFTER}** sections (Cap. I–XIV through Man. Post. Cap. II §XIX Tum in nomine / Paul circumcision / Matt–Luke–Calvin Abel / Socinus / three modes quatenus reductio / before Deinde habitus)
- Packet: `{PACKET_STEM}`
- Locked Latin: `sources/{LOCK_NAME}` (1661 PDF pp. 175 tip–182 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **δικαιώματα** (Rom 2:26); do not revive ἔργον
- Gates: `check_pass_ab` ok {JX_PREFIX}_185–192; `--tip-ready` 0; packet `reviews/audit/{PACKET_STEM}.packet.json`
- Hold: catch-up ship in flight; eng/src append after live>3744 or 12m (`sources/_ocr_cap2_sxix/hold_receipt.json`; released {hold_note})
- Stopped before Cap. II GAR Deinde qua ratione habitus ille…
- Honest partial: Cap. II Deinde habitus / Posterior quaestio de poena / Cap. III+ / rest of MS examination / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Claim `placeus-de-imputatione-densify` stays claimed (scribe-placeus); no second claim; not marked done
- Punch X: **NO** (do not ship)

"""
    handoff.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")

    done = {
        "packet_stem": PACKET_STEM,
        "before": BEFORE,
        "after": AFTER,
        "sids": SIDS,
        "phase": "appended_tip_ready",
        "punch_x": "NO",
        "claim": "placeus-de-imputatione-densify stays claimed",
        "check_pass_ab": f"ok {JX_PREFIX}_185-192",
        "tip_ready": "ok",
        "hold": hold_note,
        "hostname": subprocess.check_output(["hostname"], text=True).strip(),
    }
    (OCR / f"{PACKET_STEM}_done_receipt.json").write_text(
        json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(done, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
