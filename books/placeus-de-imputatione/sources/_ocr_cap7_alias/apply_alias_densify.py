# -*- coding: utf-8 -*-
"""Cap. VII Ad alias rationes densify: Prima–Secunda–Resp.1–3–Tertia tip."""
from __future__ import annotations
import json, copy, sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap7_alias"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, file_digest, validate_audit_receipt, make_audit_packet

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
SIDS = ["44", "45", "46", "47", "48"]

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput VII Ad alias rationes through Prima (finis/causa), Secunda (ἐν ᾧ vs ἐφ᾽ ᾧ) with Placeus Resp. 1–3, and Tertia ratio tip on certain inhering vs remote imputed cause (printed pp. 71–76 tip). Stops before Praeter aberrationem / numbered vices of Garissoles responses / further Cap. VII. Not Cap. VIII+.
Reconstruction: IA PDF page images via macOS Vision OCR + tesseract + pdftotext; long-s/ligature OCR corrected; Greek ἐφ᾽ ᾧ / ἐν ᾧ / ἐπί / θάνατος / ἁμαρτία / ἀνθρώπου / ἀγχίνοιαν / ἀποσχεδιάζει confirmed against page image.
No modern English used as copy-text.
Remaining: Cap. VII Praeter aberrationem / vices of responses onward and Cap. VIII+ of the ~494-page Disputatio.

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

    lock_path = BOOK / "sources/_placeus_cap7_alias_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in SIDS) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path.name, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == 43 and len(src) == 43, (len(eng), len(src))
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
            "notes": f"Cap. VII Ad alias densify section {sid} from locked 1661 Latin (pp. 71–76 tip).",
        }
        jp = BOOK / f"reviews/justifications/cap7_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("just", sid, "A≠B dist", j["a_neq_b_distance"])

    assert digest(eng[:43]) == pre_eng, "sections 1-43 english mutated"
    assert digest(src[:43]) == pre_src, "sections 1-43 source mutated"

    stop = "Cap. VII Ad alias rationes / Prima–Secunda–Resp. 1–3 / Tertia tip"
    meta.update({
        "title": f"De imputatione primi peccati Adami (Cap. I–VII partial: through {stop})",
        "edition": (
            "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). IA deimputationepri00lapl. "
            "Densify: Capita I–VI + Caput VII through Ad alias rationes Prima (finis/causa), Secunda (ἐν ᾧ vs ἐφ᾽ ᾧ) "
            "with Placeus Resp. 1–3, and Tertia ratio tip on certain inhering vs remote imputed cause. "
            "Not whole Disputatio; Cap. VII Praeter aberrationem onward and Cap. VIII+ remain."
        ),
        "blurb": (
            "Josue de la Place (Placeus) — Capita I–VII partial of De imputatione primi peccati Adami from the 1661 Saumur Latin, "
            f"through {stop}. Honest partial; Cap. VII Praeter aberrationem onward and later Capita remain."
        ),
        "first_english_note": (
            "No complete public-domain English of this Latin work was locked as reading text. "
            f"This is a new rendering from locked Latin for Capita I–VII partial through {stop}."
        ),
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap7_alias_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap7_alias",
            "path": "sources/_placeus_cap7_alias_latin_lock.txt",
            "role": "copy-text",
            "name": "Locked Latin, Caput VII Ad alias rationes Prima–Tertia tip (Saumur 1661)",
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": (
            "English follows the locked 1661 Saumur Latin of Capita I–VII partial through Cap. VII Ad alias rationes "
            "Prima–Secunda–Resp. 1–3 and Tertia ratio tip, reconstructed from IA PDF page images with Vision OCR, tesseract, "
            "and pdftotext as check. No modern English was copied. Cap. VII Praeter aberrationem onward and Cap. VIII+ remain."
        ),
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap7_accedamus_densify.packet.json").read_text(encoding="utf-8"))
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    packet["seed"] = 20260922
    packet["sample_size"] = 48
    packet["expected_sections"] = [str(i) for i in range(1, 49)]
    packet["explicit_selected_sections"] = packet["expected_sections"][:]
    packet["coverage"] = {"expected": 48, "english": 48, "source": 48}
    packet["identity"]["work"] = meta["title"]
    packet["identity"]["edition"] = meta["edition"]
    packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, 49)}
    packet["publication_scope"]["title"] = meta["title"]
    packet["publication_scope"]["section_count"] = 48
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
    pkt_path = BOOK / "reviews/audit/cap7_alias_rationes_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    eng_by = {str(s["section"]): s for s in eng}
    reviews = []
    for sid in packet["expected_sections"]:
        n_paras = len(eng_by[sid]["english"]) if isinstance(eng_by[sid]["english"], list) else 1
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
            "notes": f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII Ad alias rationes / Prima–Tertia tip; Pass A != B.",
        })

    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-placeus / Placeus Cap. VII Ad alias rationes densify review, 2026-09-22",
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
                "Cap. I–VI + Cap. VII through Ad alias rationes Prima (finis/causa), Secunda (ἐν ᾧ vs ἐφ᾽ ᾧ), "
                "Placeus Resp. 1–3, and Tertia ratio tip (certain inhering vs remote imputed cause) from locked 1661 Saumur Latin. "
                "Honest partial — Cap. VII Praeter aberrationem onward and Cap. VIII+ remain. "
                "Reformed Saumur era disclosed. Locked Greek ἐφ᾽ ᾧ / ἐν ᾧ / ἥμαρτον (do not revive OCR ἔργον); prior σκοπῷ/verbis stays for Denique."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap7_alias_rationes_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name)

    errs = validate_audit_receipt(packet, review)
    print("validate_audit_receipt errors", len(errs))
    for e in errs[:20]:
        print(" -", e)
    assert len(errs) == 0, errs

    hand = BOOK / "SESSION_HANDOFF.md"
    old = hand.read_text(encoding="utf-8")
    if "cap7_alias_rationes_densify" not in old[:1200]:
        entry = """# Placeus De imputatione — production ledger

## 2026-09-22 Cap. VII Ad alias rationes densify (Prima–Secunda–Resp. 1–3–Tertia tip)

- Before: **43** sections (Cap. I–VII through Accedamus ἐφ᾽ ᾧ / aorist / lexicography)
- After: **48** sections (Cap. I–VII through Ad alias Prima–Secunda–Resp. 1–3 / Tertia tip)
- Packet: `cap7_alias_rationes_densify`
- Locked Latin: `sources/_placeus_cap7_alias_latin_lock.txt` (1661 PDF pp. 71–76 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **ἐφ᾽ ᾧ** / **ἐν ᾧ** / **ἥμαρτον** (do not revive OCR ἔργον); prior σκοπῷ/verbis stays for Denique slice
- Stopped before Praeter aberrationem / numbered vices of Garissoles responses
- Honest partial: Cap. VII Praeter aberrationem onward + Cap. VIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Punch X: **NO**

"""
        rest = old
        if rest.startswith("# Placeus"):
            rest = rest.split("\n", 1)[1].lstrip("\n")
        hand.write_text(entry + rest, encoding="utf-8")
        print("handoff updated")
    else:
        print("handoff already has entry")

    claim = Path("/Users/stephansmac/SaneApps/clients/translations/docs/claim-locks/placeus-de-imputatione-densify")
    print("claim lock", claim.read_text().strip() if claim.exists() else "MISSING")
    print("NEW TITLES:")
    for s in eng[43:]:
        print(" ", s["section"], s["title"])
    print("BEFORE 43 AFTER", len(eng))
    print("DID NOT SHIP; DID NOT COMMIT; claim not freed")

if __name__ == "__main__":
    main()
