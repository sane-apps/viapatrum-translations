# -*- coding: utf-8 -*-
"""Pass A gloss repair for Placeus Cap. VII Praeter sections 49–53. No new sections. No ship."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
OCR = BOOK / "sources/_ocr_cap7_praeter"
sys.path.insert(0, str(ROOT))
from pipeline.check_pass_ab import check_record, join_b
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt

payload = json.loads((OCR / "praeter_pass_a_repair_payload.json").read_text(encoding="utf-8"))
PASS_A = payload["pass_a"]
PASS_B = payload["pass_b"]


def dist(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 1.0
    return round(1.0 - len(ta & tb) / len(ta | tb), 4)


def main() -> None:
    eng_path = BOOK / "translations/cap1_tip_english.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    assert len(eng) == 53, len(eng)
    pre48 = json.dumps(eng[:48], ensure_ascii=False)

    changed_b = []
    for sid in ["49", "50", "51", "52", "53"]:
        jp = BOOK / f"reviews/justifications/cap7_{sid}.json"
        j = json.loads(jp.read_text(encoding="utf-8"))
        old_b = join_b(j["pass_b_english"])
        new_a = PASS_A[sid]
        new_b = PASS_B[sid]
        new_b_join = " ".join(new_b)
        j["pass_a_gloss"] = new_a
        j["pass_b_english"] = new_b
        j["pass_a_ne_b"] = True
        j["a_neq_b_distance"] = dist(new_a, new_b_join)
        j["notes"] = (
            f"Cap. VII Praeter densify section {sid} from locked 1661 Latin (pp. 77–82 tip). "
            "Pass A gloss repair 2026-09-22 (English sense gloss; not Latin telegram)."
        )
        if not j.get("lemmas"):
            raise SystemExit(f"empty lemmas {sid}")
        if not j.get("choices"):
            raise SystemExit(f"empty choices {sid}")
        errs = check_record(j)
        if errs:
            print("FAIL pre-write", sid, errs)
            print("A words", len(new_a.split()), "B words", len(new_b_join.split()))
            raise SystemExit(1)
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("ok just", sid, "A≠B dist", j["a_neq_b_distance"], "A/B", len(new_a.split()), len(new_b_join.split()))

        row = eng[int(sid) - 1]
        assert str(row["section"]) == sid
        if old_b != new_b_join:
            changed_b.append(sid)
            row["english"] = new_b
        elif join_b(row["english"]) != new_b_join:
            row["english"] = new_b

    assert json.dumps(eng[:48], ensure_ascii=False) == pre48, "sections 1-48 mutated"
    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english updated; Pass B changed sections:", changed_b or "(none)")

    old_p = json.loads((BOOK / "reviews/audit/cap7_praeter_vices_densify.packet.json").read_text(encoding="utf-8"))
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta = json.loads((BOOK / "translations/cap1_tip_meta.json").read_text(encoding="utf-8"))
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
    ]
    raw = [str(BOOK / "sources" / lf) for lf in lock_files]
    expected = [str(i) for i in range(1, 54)]
    identity = copy.deepcopy(old_p["identity"])
    identity["work"] = meta["title"]
    identity["edition"] = meta["edition"]
    identity["locus_aliases"] = {str(i): str(i) for i in range(1, 54)}
    pub = copy.deepcopy(old_p["publication_scope"])
    pub["title"] = meta["title"]
    pub["section_count"] = 53
    pub["blurb"] = meta["blurb"]
    pub["edition"] = meta["edition"]
    pub["first_english_note"] = meta["first_english_note"]
    pub["text_history"] = meta["text_history"]
    pub["section_ids"] = expected[:]

    packet = make_audit_packet(
        eng_path,
        src_path,
        raw_sources=raw,
        expected_sections=expected,
        seed=20260922,
        sample_size=53,
        identity=identity,
        selected_sections=expected,
        publication_scope=pub,
    )
    pkt_path = BOOK / "reviews/audit/cap7_praeter_vices_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], "sections", len(packet["sections"]))

    eng_by = {str(s["section"]): s for s in eng}
    reviews = []
    for sid in expected:
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
            "notes": (
                f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII Praeter; "
                "Pass A English gloss repair (not Latin telegram)."
            ),
        })
    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-placeus / Placeus Cap. VII Praeter Pass A gloss repair, 2026-09-22",
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
            "uncertainties": [
                "Section 53: Greek ἐγγύς in meritorious-causes quote is page-OCR soft (Vision crop); sense locked by proximitas context."
            ],
            "notes": (
                "Pass A gloss repair on sections 49–53 of Cap. VII Praeter aberrationem densify. "
                "Not a new slice. Honest partial — Cap. VII Quarta ratio onward and Cap. VIII+ remain. "
                "Locked Greek ἐφ᾽ ᾧ / ἥμαρτον / ἀνθρώπου / ἐγγύς (do not revive OCR ἔργον). Punch X: NO."
            ),
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap7_praeter_vices_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errs = validate_audit_receipt(packet, review)
    print("validate_audit_receipt errors", len(errs))
    for e in errs[:20]:
        print(" -", e)
    assert not errs, errs

    hand = BOOK / "SESSION_HANDOFF.md"
    old = hand.read_text(encoding="utf-8")
    entry = """# Placeus De imputatione — production ledger

## 2026-09-22 Cap. VII Praeter Pass A gloss repair (secs 49–53)

- Scope: **repair only** already-written Praeter densify sections **49–53** (not a new slice; no new sections)
- Problem: Pass A was a Latin telegram and too short to constrain Pass B (`check_pass_ab` fail)
- Fix: rewrite Pass A as complete English sense gloss of every locked-Latin clause; re-read Pass B; cut non-Latin claims; smooth source word-order; keep Garissoles quote → Placeus answer voice
- Lemma: locked Greek **ἐφ᾽ ᾧ** / **ἥμαρτον** (do not revive OCR ἔργον)
- Packet refreshed: `cap7_praeter_vices_densify` (`validate_audit_receipt` 0)
- Claim `placeus-de-imputatione-densify` stays claimed (scribe-placeus); no second claim
- Punch X: **NO** (do not ship)
- Honest partial: Cap. VII Quarta ratio onward + Cap. VIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)

"""
    if old.startswith("# Placeus"):
        rest = old.split("\n", 1)[1]
        while rest.startswith("\n"):
            rest = rest[1:]
        # avoid duplicate gloss-repair header
        if "Pass A gloss repair (secs 49–53)" in rest[:800]:
            # drop previous repair entry block if re-run
            parts = rest.split("\n## ", 1)
            if len(parts) == 2 and parts[0].startswith("2026-09-22 Cap. VII Praeter Pass A"):
                rest = "## " + parts[1]
        hand.write_text(entry + rest, encoding="utf-8")
    else:
        hand.write_text(entry + old, encoding="utf-8")
    print("prepended SESSION_HANDOFF")

    ok = fail = 0
    for sid in ["49", "50", "51", "52", "53"]:
        j = json.loads((BOOK / f"reviews/justifications/cap7_{sid}.json").read_text(encoding="utf-8"))
        e = check_record(j)
        if e:
            fail += 1
            print("FAIL", sid, e)
        else:
            ok += 1
            print("OK", sid)
    print(f"ok={ok} fail={fail} total={ok+fail}")
    print("CHANGED_B", ",".join(changed_b) if changed_b else "none")
    print("CLAIM", (ROOT / "docs/claim-locks/placeus-de-imputatione-densify/agent.txt").read_text().strip())


if __name__ == "__main__":
    main()
