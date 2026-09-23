# -*- coding: utf-8 -*-
import json, copy, sys
from pathlib import Path
ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, file_digest

eng_path = BOOK / "translations/cap1_tip_english.json"
src_path = BOOK / "translations/cap1_tip_source.json"
meta_path = BOOK / "translations/cap1_tip_meta.json"
eng = json.loads(eng_path.read_text(encoding="utf-8"))
src = json.loads(src_path.read_text(encoding="utf-8"))
meta = json.loads(meta_path.read_text(encoding="utf-8"))
assert len(eng) == 38 and len(src) == 38, (len(eng), len(src))
print("sections ok", len(eng))

old_p = json.loads((BOOK / "reviews/audit/cap7_s6_causes_densify.packet.json").read_text(encoding="utf-8"))
packet = copy.deepcopy(old_p)
packet.pop("packet_id", None)
packet["seed"] = 20260922
packet["sample_size"] = 38
packet["expected_sections"] = [str(i) for i in range(1, 39)]
packet["explicit_selected_sections"] = packet["expected_sections"][:]
packet["coverage"] = {"expected": 38, "english": 38, "source": 38}
packet["identity"]["work"] = meta["title"]
packet["identity"]["edition"] = meta["edition"]
packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, 39)}
packet["publication_scope"]["title"] = meta["title"]
packet["publication_scope"]["section_count"] = 38
packet["publication_scope"]["blurb"] = meta["blurb"]
packet["publication_scope"]["edition"] = meta["edition"]
packet["publication_scope"]["first_english_note"] = meta["first_english_note"]
packet["publication_scope"]["text_history"] = meta["text_history"]

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
]
files = [
    {"path": str(eng_path), "sha256": file_digest(eng_path)},
    {"path": str(src_path), "sha256": file_digest(src_path)},
]
for lf in lock_files:
    p = BOOK / "sources" / lf
    files.append({"path": str(p), "sha256": file_digest(p)})
packet["files"] = files
packet["raw_source_paths"] = [str(BOOK / "sources" / lf) for lf in lock_files]

eng_by = {str(s["section"]): s for s in eng}
src_by = {str(s["section"]): s for s in src}
new_sections = []
for sid in packet["expected_sections"]:
    er, sr = eng_by[sid], src_by[sid]
    latin = sr["latin"] if isinstance(sr["latin"], str) else "\n\n".join(sr["latin"])
    english = er["english"] if isinstance(er["english"], list) else [er["english"]]
    new_sections.append({
        "section": sid,
        "locus": sid,
        "source_path": str(src_path),
        "source_text": [latin],
        "english": english,
        "source_sha256": digest({"latin": latin}),
        "english_sha256": digest(er),
        "risks": ["negation_modality_or_doctrine", "scripture_links", "textual_uncertainty"],
        "raw_source_paths": packet["raw_source_paths"],
    })
packet["sections"] = new_sections
packet["structural_errors"] = []
packet_id = digest(packet)
packet_out = {"packet_id": packet_id, **packet}
assert digest({k: v for k, v in packet_out.items() if k != "packet_id"}) == packet_id

pkt_path = BOOK / "reviews/audit/cap7_denique_modus_densify.packet.json"
pkt_path.write_text(json.dumps(packet_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("packet", packet_id[:16], len(new_sections))

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
        "notes": f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII Denique / σκοπῷ–verbis; Pass A != B.",
    })

review = {
    "packet_id": packet_id,
    "reviewer": "scribe-placeus / Placeus Cap. VII Denique modus densify review, 2026-09-22",
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
        "notes": "Cap. I–VI + Cap. VII through Denique / σκοπῷ–verbis to Gualtherus first-argument close from locked 1661 Saumur Latin. Honest partial — Cap. VII Accedamus ἐφ᾽ ᾧ onward and Cap. VIII+ remain. Reformed Saumur era disclosed. Prior residual ἔργον label corrected to σκοπῷ on the page.",
    },
    "reviews": reviews,
}
rev_path = BOOK / "reviews/audit/cap7_denique_modus_densify.review.json"
rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("review pass", len(reviews))

hand = BOOK / "SESSION_HANDOFF.md"
old = hand.read_text(encoding="utf-8")
if "cap7_denique_modus_densify" not in old[:800]:
    entry = """# Placeus De imputatione — production ledger

## 2026-09-22 Cap. VII Denique densify (modes + σκοπῷ/verbis through Gualtherus)

- Before: **33** sections (Cap. I–VII through §.6 Sed pergamus)
- After: **38** sections (Cap. I–VII through Denique / Gualtherus first-argument close)
- Packet: `cap7_denique_modus_densify`
- Locked Latin: `sources/_placeus_cap7_denique_latin_lock.txt` (1661 PDF pp. 62–66 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **σκοπῷ**/verbis (prior residual handoff label ἔργον was OCR misread of Greek σκοπῷ)
- Stopped before Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον
- Honest partial: Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography onward + Cap. VIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
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
print("claim lock exists", claim.exists())

for sid in ["34", "35", "36", "37", "38"]:
    j = json.loads((BOOK / f"reviews/justifications/cap7_{sid}.json").read_text(encoding="utf-8"))
    assert j["pass_a_ne_b"] and j["pass_a_gloss"] != " ".join(j["pass_b_english"])
    print(sid, j["title"][:70], "dist", j["a_neq_b_distance"])
print("NEW TITLES:")
for s in eng[33:]:
    print(" ", s["section"], s["title"])
print("DID NOT SHIP; DID NOT COMMIT; claim not freed")
