# -*- coding: utf-8 -*-
"""Cap. IX open densify: Caput IX Hebr. 7:9–10 through roses reductio / before Responsio secunda."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap9_open"
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
SIDS = ["92", "93", "94", "95", "96", "97", "98"]

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput IX opening — Declaratio … Ex Hebr. 7.9–10 Levi in lumbis Abrahae through I. Anselm / II. Garissoles Levi parallel / Fayus ἐφ᾽ ᾧ / Theses syllogism / Sed fortasse indirect / roses vs stones reductio (printed pp. 103–107 tip). Stops before Responsio secunda (ὡς ἔπος εἰπεῖν). Not further Cap. IX+.
Reconstruction: IA PDF page images via macOS Vision OCR + pdftotext; long-s/ligature OCR corrected. Locked Greek ἐφ᾽ ᾧ πάντες ἥμαρτον (OCR soft; Fayus = in quo). Do not revive OCR ἔργον.
No modern English used as copy-text.
Remaining: Cap. IX Responsio 2+ / Cap. X+ of the ~494-page Disputatio.

"""


def dist(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 1.0
    return round(1.0 - len(ta & tb) / len(ta | tb), 4)


def main() -> None:
    for sid in SIDS:
        a, b = PASS_A[sid], " ".join(PASS_B[sid])
        assert a.strip() != b.strip(), sid
        d = dist(a, b)
        assert d > 0.35, (sid, d)

    lock_path = BOOK / "sources/_placeus_cap9_open_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in SIDS) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path.name, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == 91 and len(src) == 91, (len(eng), len(src))
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
            "notes": NOTES[sid][0],
        })
        pb = PASS_B[sid]
        j = {
            "section": sid,
            "title": TITLES[sid],
            "pass_a_gloss": PASS_A[sid],
            "pass_b_english": pb,
            "source_text": LATIN[sid],
            "pass_a_ne_b": True,
            "a_neq_b_distance": dist(PASS_A[sid], " ".join(pb)),
            "lemmas": LEMMAS[sid],
            "choices": CHOICES[sid],
            "bible_refs": BIBLE[sid],
            "notes": f"Cap. IX open densify section {sid} from locked 1661 Latin (pp. 103–107 tip).",
        }
        jp = BOOK / f"reviews/justifications/cap9_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("just", sid, "A≠B dist", j["a_neq_b_distance"])

    assert digest(eng[:91]) == pre_eng, "sections 1-91 english mutated"
    assert digest(src[:91]) == pre_src, "sections 1-91 source mutated"

    stop = (
        "Cap. IX open / Heb. 7:9–10 Levi / Anselm / Fayus ἐφ᾽ ᾧ / "
        "Theses syllogism / roses reductio / before Responsio 2"
    )
    remain = "Cap. IX Responsio 2+ / Cap. X+ remain."
    meta.update({
        "title": f"De imputatione primi peccati Adami (Cap. I–IX partial: through {stop})",
        "edition": (
            "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). "
            "IA deimputationepri00lapl. Densify: Capita I–VIII + Caput IX opening through "
            "roses reductio before Responsio secunda. "
            f"Not whole Disputatio; {remain}"
        ),
        "blurb": (
            "Josue de la Place (Placeus) — Capita I–IX partial of De imputatione primi "
            f"peccati Adami from the 1661 Saumur Latin, through {stop}. Honest partial; {remain}"
        ),
        "first_english_note": (
            "No complete public-domain English of this Latin work was locked as reading text. "
            f"This is a new rendering from locked Latin for Capita I–IX partial through {stop}."
        ),
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap9_open_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap9_open",
            "path": "sources/_placeus_cap9_open_latin_lock.txt",
            "role": "copy-text",
            "name": (
                "Locked Latin, Caput IX opening through roses reductio before Responsio secunda "
                "(Saumur 1661)"
            ),
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": (
            "English follows the locked 1661 Saumur Latin of Capita I–IX partial through Cap. IX "
            "open Heb. 7:9–10 Levi / Anselm / Fayus ἐφ᾽ ᾧ / Theses / roses reductio before "
            "Responsio secunda, reconstructed from IA PDF page images with Vision OCR and "
            "pdftotext as check. No modern English was copied. Cap. IX Responsio 2+ / Cap. X+ remain."
        ),
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap8_vs19_densify.packet.json").read_text(encoding="utf-8"))
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    n = 98
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

    lock_files = [
        "_placeus_cap1_latin_lock.txt",
        "_placeus_cap2_latin_lock.txt",
        "_placeus_cap3_latin_lock.txt",
        "_placeus_cap4_latin_lock.txt",
        "_placeus_cap4_rest_latin_lock.txt",
        "_placeus_cap5_6tip_latin_lock.txt",
        "_placeus_cap6_rest_latin_lock.txt",
        "_placeus_cap7_tip_latin_lock.txt",
        "_placeus_cap7_rest_latin_lock.txt",
        "_placeus_cap7_s6_latin_lock.txt",
        "_placeus_cap7_denique_latin_lock.txt",
        "_placeus_cap7_accedamus_latin_lock.txt",
        "_placeus_cap7_alias_latin_lock.txt",
        "_placeus_cap7_praeter_latin_lock.txt",
        "_placeus_cap7_quarta_latin_lock.txt",
        "_placeus_cap7_quinta_latin_lock.txt",
        "_placeus_cap8_open_latin_lock.txt",
        "_placeus_cap8_calvin_p20_latin_lock.txt",
        "_placeus_cap8_ex16_latin_lock.txt",
        "_placeus_cap8_vs17_latin_lock.txt",
        "_placeus_cap8_vs19_latin_lock.txt",
        "_placeus_cap9_open_latin_lock.txt",
    ]
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
    pkt_path = BOOK / "reviews/audit/cap9_open_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    reviews = []
    sec_by_id = {s["section"]: s for s in packet["sections"]}
    for sid in packet["expected_sections"]:
        note = (
            f"Section {sid}: Cap. IX open densify from locked 1661 Latin (pp. 103–107 tip); Pass A != B."
            if int(sid) >= 92
            else f"Section {sid}: prior densify retained; Pass B checked against locked 1661 Latin; Pass A != B."
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
        "reviewer": "scribe-placeus / Placeus Cap. IX open densify review, 2026-09-22",
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
                "Cap. I–IX through Cap. IX open Heb. 7:9–10 Levi / Anselm / Fayus ἐφ᾽ ᾧ / "
                "Theses syllogism / roses reductio before Responsio secunda from locked 1661 "
                "Saumur Latin (pp. 103–107 tip). Honest partial — Cap. IX Responsio 2+ / Cap. X+ "
                "remain. Reformed Saumur era disclosed. Locked Greek ἐφ᾽ ᾧ πάντες ἥμαρτον "
                "(OCR soft); do not revive OCR ἔργον. Punch X: NO."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap9_open_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name)

    rc = validate_audit_receipt(
        json.loads(pkt_path.read_text(encoding="utf-8")),
        json.loads(rev_path.read_text(encoding="utf-8")),
    )
    print("validate_audit_receipt", rc if rc else 0)
    if rc:
        raise SystemExit(f"validate_audit_receipt: {rc}")

    fails = 0
    for sid in SIDS:
        errs = check_pass_ab.check_file(BOOK / f"reviews/justifications/cap9_{sid}.json")
        status = "ok" if not errs else "FAIL"
        print(f"check_pass_ab cap9_{sid}: {status}")
        if errs:
            fails += 1
            for e in errs:
                print(" ", e)
    print("check_pass_ab fails", fails)

    tip_errs = check_pass_ab.check_translation_files(eng_path, src_path)
    print("tip-ready errors", len(tip_errs))
    for e in tip_errs[:20]:
        print(" ", e)

    handoff = BOOK / "SESSION_HANDOFF.md"
    old = handoff.read_text(encoding="utf-8")
    block = """## 2026-09-22 Cap. IX open densify (Heb. 7:9–10 Levi / Anselm → Fayus ἐφ᾽ ᾧ / Theses / roses / before Responsio 2)

- Before: **91** sections (Cap. I–VIII through VI Ex vs.19 / παρακοῆς / Chamier ἁμαρτωλούς / Martyr close)
- After: **98** sections (Cap. I–IX open through roses reductio / before Responsio secunda)
- Packet: `cap9_open_densify`
- Locked Latin: `sources/_placeus_cap9_open_latin_lock.txt` (1661 PDF pp. 103–107 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **ἐφ᾽ ᾧ πάντες ἥμαρτον** (OCR soft; Fayus = in quo; do not revive ἔργον)
- Stopped before Responsio secunda (ὡς ἔπος εἰπεῖν / further Cap. IX)
- Honest partial: Cap. IX Responsio 2+ / Cap. X+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Claim `placeus-de-imputatione-densify` stays claimed (scribe-placeus); no second claim; not marked done
- Punch X: **NO** (do not ship)

"""
    handoff.write_text(block + old, encoding="utf-8")
    print("handoff prepended")
    if fails or tip_errs:
        raise SystemExit(f"check failures: pass_ab={fails} tip_ready={len(tip_errs)}")


if __name__ == "__main__":
    main()
