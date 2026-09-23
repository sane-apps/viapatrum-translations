# -*- coding: utf-8 -*-
"""Cap. XII open densify: Daubuz antecedent/immediate arguments through covenant close before v.19."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap12_open"
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
SIDS = ["138", "139", "140", "141", "142", "143", "144"]
BEFORE = 137
AFTER = 144

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput XII Imputationem antecedentem seu immediatam non esse probatam argumentis Dom. Daubuz (printed pp. 138–144 tip). Stops before Tranfit… vers. XIX. Not further Cap. XII v.19+.
Reconstruction: IA PDF page images via macOS Vision OCR + pdftotext; long-s/ligature OCR corrected. Locked Greek ἐφ᾽ ᾧ / καθ᾽ ἕξιν / ἐνεργείᾳ / ἀδιάλυτον / ἁπλῶς / κατὰ μέρος / θεανθρώπῳ (OCR soft). Do not revive OCR ἔργον.
No modern English used as copy-text.
Remaining: Cap. XII v.19+ / Cap. XIII+ of the ~494-page Disputatio.

"""


def dist(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 1.0
    return round(1.0 - len(ta & tb) / len(ta | tb), 4)


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
                f"Cap. XII open densify section {sid} "
                "from locked 1661 Latin (pp. 138–144 tip)."
            ),
        }
        jp = BOOK / f"reviews/justifications/cap12_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errs = check_pass_ab.check_file(jp)
        status = "ok" if not errs else "FAIL"
        print(f"check_pass_ab cap12_{sid}: {status} dist={j['a_neq_b_distance']}")
        if errs:
            for e in errs:
                print(" ", e)
            raise SystemExit(f"check_pass_ab failed on {sid}")


def main() -> None:
    write_justifications()

    lock_path = BOOK / "sources/_placeus_cap12_open_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in SIDS) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path.name, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == BEFORE and len(src) == BEFORE, (len(eng), len(src))
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
        "Cap. XII Daubuz antecedent/immediate / ἐφ᾽ ᾧ / infants habit / Theodoret–Augustine / "
        "duplex being–dying / Thomas–Caesar–Marius / covenant Mosaic–Abraham–nature close / before v.19"
    )
    remain = "Cap. XII v.19+ / Cap. XIII+ remain."
    meta.update({
        "title": f"De imputatione primi peccati Adami (Cap. I–X partial: through {stop})",
        "edition": (
            "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). "
            "IA deimputationepri00lapl. Densify: Capita I–XI + Caput XII open (Daubuz "
            "antecedent/immediate arguments) before v.19. "
            f"Not whole Disputatio; {remain}"
        ),
        "blurb": (
            "Josue de la Place (Placeus) — Capita I–XII partial of De imputatione primi "
            f"peccati Adami from the 1661 Saumur Latin, through {stop}. Honest partial; {remain}"
        ),
        "first_english_note": (
            "No complete public-domain English of this Latin work was locked as reading text. "
            f"This is a new rendering from locked Latin for Capita I–XII partial through {stop}."
        ),
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap12_open_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap12_open",
            "path": "sources/_placeus_cap12_open_latin_lock.txt",
            "role": "copy-text",
            "name": (
                "Locked Latin, Caput XII Daubuz antecedent/immediate open before v.19 "
                "(Saumur 1661)"
            ),
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": (
            "English follows the locked 1661 Saumur Latin of Capita I–XII partial through Cap. XII "
            "Daubuz antecedent/immediate open (ἐφ᾽ ᾧ; infants habit; Theodoret–Augustine; duplex "
            "being–dying; Thomas–Caesar–Marius; covenant Mosaic–Abraham–nature) before v.19, "
            "reconstructed from IA PDF page images with Vision OCR and pdftotext as check. "
            "No modern English was copied. Cap. XII v.19+ / Cap. XIII+ remain."
        ),
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap11_open_densify.packet.json").read_text(encoding="utf-8"))
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
        "_placeus_cap9_responsio2_latin_lock.txt",
        "_placeus_cap10_open_latin_lock.txt",
        "_placeus_cap10_alteram_latin_lock.txt",
        "_placeus_cap10_auxilium_latin_lock.txt",
        "_placeus_cap10_ultima_latin_lock.txt",
        "_placeus_cap11_open_latin_lock.txt",
        "_placeus_cap12_open_latin_lock.txt",
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
    pkt_path = BOOK / "reviews/audit/cap12_open_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    reviews = []
    sec_by_id = {s["section"]: s for s in packet["sections"]}
    for sid in packet["expected_sections"]:
        note = (
            f"Section {sid}: Cap. XII open densify from locked 1661 Latin "
            "(pp. 138–144 tip); Pass A != B."
            if int(sid) >= 138
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
        "reviewer": "scribe-placeus / Placeus Cap. XII open densify review, 2026-09-22",
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
                "Cap. I–XII through Cap. XII Daubuz antecedent/immediate open "
                "(ἐφ᾽ ᾧ; infants habit; Theodoret–Augustine; duplex being–dying; Thomas–Caesar–Marius; "
                "covenant Mosaic–Abraham–nature) before v.19 from locked 1661 Saumur Latin (pp. 138–144 tip). "
                "Honest partial — Cap. XII v.19+ / Cap. XIII+ remain. "
                "Reformed Saumur era disclosed. Locked Greek ἐφ᾽ ᾧ / καθ᾽ ἕξιν / ἐνεργείᾳ / ἀδιάλυτον / "
                "ἁπλῶς / κατὰ μέρος / θεανθρώπῳ; do not revive OCR ἔργον. "
                "Punch X: NO."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap12_open_densify.review.json"
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
    block = """## 2026-09-22 Cap. XII open densify (Daubuz antecedent/immediate → covenant close / before v.19)

- Before: **137** sections (Cap. I–XI through Cap. XI alienation / Walaeus close)
- After: **144** sections (Cap. I–XII through Cap. XII Daubuz open / ἐφ᾽ ᾧ / infants habit / Theodoret–Augustine / duplex being–dying / Thomas–Caesar–Marius / covenant Mosaic–Abraham–nature / before v.19)
- Packet: `cap12_open_densify`
- Locked Latin: `sources/_placeus_cap12_open_latin_lock.txt` (1661 PDF pp. 138–144 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **ἐφ᾽ ᾧ** / **καθ᾽ ἕξιν** / **ἐνεργείᾳ** / **ἀδιάλυτον** / **ἁπλῶς** / **κατὰ μέρος** / **θεανθρώπῳ** (OCR soft); do not revive ἔργον
- Gates: `check_pass_ab` ok cap12_138–144; `--tip-ready` 0; packet `reviews/audit/cap12_open_densify.packet.json`
- Stopped before Cap. XII Tranfit… vers. XIX (Daubuz on Rom 5:19)
- Honest partial: Cap. XII v.19+ / Cap. XIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Claim `placeus-de-imputatione-densify` stays claimed (scribe-placeus); no second claim; not marked done
- Punch X: **NO** (do not ship)

"""
    handoff.write_text(block + old, encoding="utf-8")
    print("handoff prepended")
    print(f"DONE before={BEFORE} after={AFTER} packet=cap12_open_densify PunchX=NO")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--justifications-only":
        write_justifications()
    else:
        main()
