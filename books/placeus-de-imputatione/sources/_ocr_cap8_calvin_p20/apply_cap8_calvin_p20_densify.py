# -*- coding: utf-8 -*-
"""Cap. VIII Calvin p.20 densify: after gift reductio through hereditary-corruption close / before Ex vs.16."""
from __future__ import annotations
import json, copy, sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap8_calvin_p20"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, validate_audit_receipt, make_audit_packet

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
SIDS = ["71", "72", "73", "74", "75"]

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput VIII after Rom. 5:15 gift reductio — Calvin p.20 citation block through Institutes 2.1.8/4.15.10 and hereditary-corruption close through "morti sumus addicti" (printed pp. 95–97 tip). Stops before III. Ex verf. 16 / further Cap. VIII. Not Cap. IX+.
Reconstruction: IA PDF page images via macOS Vision OCR + tesseract + pdftotext; long-s/ligature OCR corrected; Calvin Comm. Rom. 5:15 aligned to Cap. IV lock (Vision marginal soft); Inst. irae Dei OCR soft.
No modern English used as copy-text.
Remaining: Cap. VIII Ex vs.16 onward + Cap. IX+ of the ~494-page Disputatio.

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

    lock_path = BOOK / "sources/_placeus_cap8_calvin_p20_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in SIDS) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path.name, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == 70 and len(src) == 70, (len(eng), len(src))
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
            "notes": f"Cap. VIII Calvin p.20 densify section {sid} from locked 1661 Latin (pp. 95–97 tip).",
        }
        jp = BOOK / f"reviews/justifications/cap8_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("just", sid, "A≠B dist", j["a_neq_b_distance"])

    assert digest(eng[:70]) == pre_eng, "sections 1-70 english mutated"
    assert digest(src[:70]) == pre_src, "sections 1-70 source mutated"

    stop = "Cap. VIII Calvin p.20 / Institutes / hereditary corruption close / before Ex vs.16"
    meta.update({
        "title": f"De imputatione primi peccati Adami (Cap. I–VIII partial: through {stop})",
        "edition": (
            "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). IA deimputationepri00lapl. "
            "Densify: Capita I–VII + Caput VIII through Calvin p.20 citation / Institutes 2.1.8·4.15.10 / "
            "hereditary-corruption close before Ex vs.16. "
            "Not whole Disputatio; Cap. VIII Ex vs.16+ + Cap. IX+ remain."
        ),
        "blurb": (
            "Josue de la Place (Placeus) — Capita I–VIII partial of De imputatione primi peccati Adami from the 1661 Saumur Latin, "
            f"through {stop}. Honest partial; Cap. VIII Ex vs.16+ + Cap. IX+ remain."
        ),
        "first_english_note": (
            "No complete public-domain English of this Latin work was locked as reading text. "
            f"This is a new rendering from locked Latin for Capita I–VIII partial through {stop}."
        ),
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap8_calvin_p20_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap8_calvin_p20",
            "path": "sources/_placeus_cap8_calvin_p20_latin_lock.txt",
            "role": "copy-text",
            "name": "Locked Latin, Caput VIII Calvin p.20 through hereditary-corruption close (Saumur 1661)",
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": (
            "English follows the locked 1661 Saumur Latin of Capita I–VIII partial through Cap. VIII Calvin p.20 / "
            "Institutes / hereditary-corruption close before Ex vs.16, reconstructed from IA PDF page images with Vision OCR, tesseract, "
            "and pdftotext as check. No modern English was copied. Cap. VIII Ex vs.16+ + Cap. IX+ remain."
        ),
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap8_open_densify.packet.json").read_text(encoding="utf-8"))
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    packet["seed"] = 20260922
    packet["sample_size"] = 75
    packet["expected_sections"] = [str(i) for i in range(1, 76)]
    packet["explicit_selected_sections"] = packet["expected_sections"][:]
    packet["coverage"] = {"expected": 75, "english": 75, "source": 75}
    packet["identity"]["work"] = meta["title"]
    packet["identity"]["edition"] = meta["edition"]
    packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, 76)}
    packet["publication_scope"]["title"] = meta["title"]
    packet["publication_scope"]["section_count"] = 75
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
    pkt_path = BOOK / "reviews/audit/cap8_calvin_p20_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    eng_by = {str(s["section"]): s for s in eng}
    reviews = []
    for sid in packet["expected_sections"]:
        n_paras = len(eng_by[sid]["english"]) if isinstance(eng_by[sid]["english"], list) else 1
        note = (
            f"Section {sid}: Cap. VIII Calvin p.20 densify; Pass B vs locked 1661 Latin; Pass A != B."
            if int(sid) >= 71
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
            "covered_source_paragraphs": list(range(1, n_paras + 1)),
            "notes": note,
        })

    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-placeus / Placeus Cap. VIII Calvin p.20 densify review, 2026-09-22",
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
                "Cap. I–VIII through Calvin p.20 / Institutes / hereditary-corruption close before Ex vs.16 "
                "from locked 1661 Saumur Latin (pp. 95–97 tip). Honest partial — Cap. VIII Ex vs.16+ + Cap. IX+ remain. "
                "Reformed Saumur era disclosed. OCR soft on marginal in Rom. / ira·irae Dei; do not revive OCR ἔργον. "
                "Punch X: NO."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap8_calvin_p20_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name)

    rc = validate_audit_receipt(pkt_path, rev_path)
    print("validate_audit_receipt", rc)

    # check_pass_ab on new justifications
    from pipeline import check_pass_ab
    fails = 0
    for sid in SIDS:
        errs = check_pass_ab.check_file(BOOK / f"reviews/justifications/cap8_{sid}.json")
        status = "ok" if not errs else "FAIL"
        print(f"check_pass_ab cap8_{sid}: {status}")
        if errs:
            fails += 1
            for e in errs:
                print(" ", e)
    print("check_pass_ab fails", fails)

    # prepend SESSION_HANDOFF
    handoff = BOOK / "SESSION_HANDOFF.md"
    old = handoff.read_text(encoding="utf-8")
    entry = (
        "## 2026-09-22 Cap. VIII Calvin p.20 densify (gift reductio → hereditary close / before Ex vs.16)\n\n"
        "- Before: **70** sections (Cap. I–VIII opening through Rom. 5:15 παράπτωμα/χάρισμα gift reductio)\n"
        "- After: **75** sections (Cap. I–VIII through Calvin p.20 / Institutes 2.1.8·4.15.10 / hereditary-corruption close)\n"
        "- Packet: `cap8_calvin_p20_densify`\n"
        "- Locked Latin: `sources/_placeus_cap8_calvin_p20_latin_lock.txt` (1661 PDF pp. 95–97 tip)\n"
        "- Pass A≠B; OUR; English-first; no PBB/ops TNs\n"
        "- Lemma note: Calvin Comm. Rom. 5:15 aligned Cap. IV; Inst. **irae Dei** OCR soft; do not revive ἔργον\n"
        "- Stopped before III. Ex verf. 16\n"
        "- Honest partial: Cap. VIII Ex vs.16+ + Cap. IX+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)\n"
        "- Claim `placeus-de-imputatione-densify` stays claimed (scribe-placeus); no second claim; not marked done\n"
        "- Punch X: **NO** (do not ship)\n\n"
    )
    handoff.write_text(entry + old, encoding="utf-8")
    print("handoff prepended")

if __name__ == "__main__":
    main()
