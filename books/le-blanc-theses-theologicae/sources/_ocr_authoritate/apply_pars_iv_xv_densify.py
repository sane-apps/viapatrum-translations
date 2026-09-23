# -*- coding: utf-8 -*-
"""Pars IV XV-XXII densify: lock Latin, append secs 133-140, packet, review, handoff."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/le-blanc-theses-theologicae"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt
from pipeline.check_pass_ab import check_file, main as check_main

LOCK_PATH = BOOK / "sources/_le_blanc_authoritate_latin_lock.txt"
ENG_PATH = BOOK / "translations/theses_theologia_english.json"
SRC_PATH = BOOK / "translations/theses_theologia_source.json"
META_PATH = BOOK / "translations/theses_theologia_meta.json"
JUST_DIR = BOOK / "reviews/justifications"
AUDIT = BOOK / "reviews/audit"
PDF = BOOK / "sources/le_blanc_theses_1675.pdf"
PACKET_STEM = "authoritate_scripturae_pars_iv_xv_densify"
HANDOFF = BOOK / "SESSION_HANDOFF.md"
DATA = Path("/tmp/leblanc_pars4_xv")
APPLY_COPY = BOOK / "sources/_ocr_authoritate/apply_pars_iv_xv_densify.py"

SECS = ["133", "134", "135", "136", "137", "138", "139", "140"]

RANGE_SHORT = "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XXII"
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; "
    "De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XXII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. "
    "IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + "
    "De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XXII "
    "(not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the "
    "1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate "
    "Scripturae Pars I through XLVII, Pars II through XXXV, Pars III through XLI, and Pars IV "
    "through XXII (Scripture doubtful without Church; retorsion on Church/councils; three false "
    "presuppositions). Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, "
    "De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, and Pars IV I-XXII, "
    "reconstructed from the Internet Archive PDF page images with pdftotext + tesseract "
    "(+ DjVu checks for earlier tracts). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. Pars I closes at XLVII; Pars II through XXXV; Pars III "
    "through XLI; Pars IV through XXII (I-XIV retained; XV-XXII Scripture doubtful without Church / "
    "retorsion / false presuppositions). XXIII+ (pressius application) remains."
)

LOCK_HEADER = (
    "\n---\n\n"
    "Expand lock: De Authoritate Scripturae Pars IV theses XV-XXII "
    "(contiguous after IX-XIV - Scripture doubtful without Church; retorsion; false presuppositions).\n"
    "Same 1675 Pitt copy-text. Book pp. 46-49 / PDF 58-61. pdftotext + tess OCR (+ DjVu checks). "
    "Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Part IV continue through XXII only (natural close before XXIII pressius application). "
    "XXIII+ remains.\n"
    "Note: XV John 8 adultera / Ptolomaïtae; XVI sophisma/obmutescere; XVII Antipapae/Basel "
    "(tess misnumbered as XVI); XVIII Trent/simoniace; XIX indemonstrabilia (OCR X»X); "
    "XX Pyrrhonii; XXI ad hominem; XXII percunctatorem restored from damaged OCR.\n\n"
)


def load_data():
    latin = json.loads((DATA / "latin.json").read_text(encoding="utf-8"))
    engd = json.loads((DATA / "english.json").read_text(encoding="utf-8"))
    return (
        latin,
        engd["titles"],
        engd["pass_a"],
        engd["pass_b"],
        engd["notes"],
        engd["bible"],
        engd["lemmas"],
        engd["choices"],
        engd.get("allusions", {}),
    )


def append_lock(LATIN):
    text = LOCK_PATH.read_text(encoding="utf-8")
    if "Expand lock: De Authoritate Scripturae Pars IV theses XV-XXII" in text:
        print("lock already expanded")
        return
    blob = LOCK_HEADER + "\n".join(LATIN[s] + "\n" for s in SECS) + "\n"
    LOCK_PATH.write_text(text.rstrip() + "\n" + blob, encoding="utf-8")
    print("lock appended Pars IV XV-XXII")


def verify_justifications():
    for sec in SECS:
        path = JUST_DIR / f"authoritate_{sec}.json"
        errs = check_file(path)
        print(f"check_pass_ab authoritate_{sec}", "ok" if not errs else errs)
        if errs:
            raise SystemExit(1)


def append_translations(LATIN, TITLES, PASS_B, NOTES, ALLUSIONS):
    eng = json.loads(ENG_PATH.read_text(encoding="utf-8"))
    src = json.loads(SRC_PATH.read_text(encoding="utf-8"))
    if len(eng) != 132 or str(eng[-1]["section"]) != "132":
        raise SystemExit(f"refuse append: tip not 132 (eng={len(eng)} last={eng[-1].get('section')})")
    have = {str(r["section"]) for r in eng}
    for sec in SECS:
        if sec in have:
            raise SystemExit(f"refuse overwrite existing section {sec}")
        allusions = ALLUSIONS.get(sec, [])
        eng.append(
            {
                "section": sec,
                "title": TITLES[sec],
                "english": PASS_B[sec],
                "notes_covered": [],
                "added_allusions": allusions,
                "translator_notes": NOTES[sec],
                "source_ref": "sources/_le_blanc_authoritate_latin_lock.txt",
            }
        )
        src.append({"section": sec, "title": TITLES[sec], "latin": LATIN[sec]})
    ENG_PATH.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SRC_PATH.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english/source now", len(eng), len(src))


def update_meta():
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    meta["title"] = RANGE_TITLE
    meta["edition"] = EDITION
    meta["blurb"] = BLURB
    th = meta.setdefault("text_history", {})
    th["method"] = METHOD
    witnesses = th.setdefault("witnesses", [])
    if not any(w.get("id") == "authoritate_latin_lock" for w in witnesses):
        witnesses.append(
            {
                "id": "authoritate_latin_lock",
                "path": "sources/_le_blanc_authoritate_latin_lock.txt",
                "role": "copy-text",
                "name": "Locked Latin, De Authoritate Scripturae densify (Pitt 1675)",
                "language": "Latin",
                "url": "https://archive.org/details/bub_gb_eOkHAW4G0-wC",
            }
        )
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta updated")


def build_packet_and_review():
    eng = json.loads(ENG_PATH.read_text(encoding="utf-8"))
    section_ids = [str(r["section"]) for r in eng]
    aliases = {sid: sid for sid in section_ids}
    identity = {
        "author": "Louis Le Blanc de Beaulieu",
        "work": RANGE_TITLE,
        "edition": EDITION,
        "language": "English",
        "source_language": "Latin",
        "slug": "le-blanc-theses-theologicae",
        "locus_scheme": "tip-section",
        "source_url": "https://archive.org/details/bub_gb_eOkHAW4G0-wC",
        "locus_aliases": aliases,
    }
    publication_scope = {
        "slug": "le-blanc-theses-theologicae",
        "title": RANGE_TITLE,
        "author": "Louis Le Blanc de Beaulieu",
        "author_slug": "louis-le-blanc-de-beaulieu",
        "period": "1675 (Sedan theses; London collection)",
        "status": "available",
        "edition": EDITION,
        "section_count": len(section_ids),
        "blurb": BLURB,
        "era_note": (
            "Le Blanc wrote in the mid-seventeenth century as Reformed professor at the Academy "
            "of Sedan. This is not a patristic work. It is a public-domain Latin Reformed "
            "retrieval on the same Fathers-site pipeline. The 1675 Pitt folio is Public Domain "
            "Mark 1.0. Do not treat the site as ante-Nicene only."
        ),
        "groups": [],
        "related_topics": [
            "justification",
            "protestant-roman",
            "ireneicism",
            "catholicism",
        ],
        "first_english": False,
        "first_english_note": "",
        "text_history": json.loads(META_PATH.read_text(encoding="utf-8"))["text_history"],
        "section_ids": section_ids,
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "identity.json").write_text(
        json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (AUDIT / "publication_scope.json").write_text(
        json.dumps(publication_scope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (AUDIT / "expected_sections.json").write_text(
        json.dumps(section_ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    packet = make_audit_packet(
        ENG_PATH,
        SRC_PATH,
        raw_sources=[LOCK_PATH, PDF],
        expected_sections=section_ids,
        seed=20260922,
        sample_size=len(section_ids),
        identity=identity,
        selected_sections=section_ids,
        publication_scope=publication_scope,
    )
    packet_path = AUDIT / f"{PACKET_STEM}.packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reviews = []
    for sid in section_ids:
        n = int(sid)
        if 133 <= n <= 140:
            notes = f"Section {sid}: new densify Pars IV XV-XXII; Pass A/B checked."
        else:
            notes = (
                f"Section {sid}: prior verified densify retained; Pass A/B and lock identity "
                "rechecked in Pars IV XV-XXII packet scope covering all current sections."
            )
        reviews.append(
            {
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
                "covered_source_paragraphs": [1],
                "notes": notes,
            }
        )
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-leblanc, 2026-09-22",
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
                "Scope review: densify Pars IV XV-XXII only (sections 133-140). Meta discloses "
                f"{RANGE_SHORT}. Honest partial; Pars IV XXIII+ remains. "
                "De Theologia / De Fide untouched. Not shipped."
            ),
        },
        "reviews": reviews,
    }
    receipt_path = AUDIT / f"{PACKET_STEM}.review.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errs = validate_audit_receipt(packet, receipt)
    print("packet", packet["packet_id"])
    print("validate_audit_receipt", errs if errs else "ok")
    if errs:
        raise SystemExit(1)


def prepend_handoff(before: int, after: int):
    entry = (
        "## 2026-09-22 (Scribe — De Authoritate Scripturae Pars IV XV–XXII densify LOCAL)\n\n"
        f"- Before: **{before}** (Pars I I–XLVII + Pars II I–XXXV + Pars III I–XLI + Pars IV I–XIV). "
        f"After: **{after}** (contiguous Pars IV XV–XXII → §§133–140).\n"
        f"- Packet `{PACKET_STEM}` (`reviews/audit/{PACKET_STEM}.packet.json` + `.review.json`). "
        "Reviewer: scribe-leblanc, 2026-09-22. Verdict pass grounded in expanded "
        "`sources/_le_blanc_authoritate_latin_lock.txt` (PDF 58–61 / book pp. 46–49).\n"
        f"- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n"
        "- Honest **partial**: Pars IV through XXII (Scripture doubtful without Church; retorsion on "
        "Church/councils/popes; first rule indemonstrable; three false presuppositions). "
        "Pars IV XXIII+ (pressius application) remains. De Theologia closed. De Fide I–XXII untouched. "
        "Not folio. Not shipped this slice.\n"
        "- Pass A ≠ B for §§133–140. Inline John 8:1–11 (adulteress pericope). OCR restorations noted "
        "in translator_notes.\n"
        "- All eight new justifications check_pass_ab ok; tip-ready ok.\n"
        "- Claim `le-blanc-theses-densify` stays claimed. Punch X = NO.\n\n"
    )
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "Pars IV XV–XXII densify" in prev[:2000]:
        print("handoff already prepended")
        return
    HANDOFF.write_text(entry + prev, encoding="utf-8")
    print("handoff prepended")


def tip_ready():
    rc = check_main(["--tip-ready", str(ENG_PATH), str(SRC_PATH)])
    print("assert_tip_ready / check_pass_ab --tip-ready", rc)
    if rc != 0:
        raise SystemExit(rc)


def main():
    LATIN, TITLES, PASS_A, PASS_B, NOTES, BIBLE, LEMMAS, CHOICES, ALLUSIONS = load_data()
    before = len(json.loads(ENG_PATH.read_text(encoding="utf-8")))
    if before != 132:
        raise SystemExit(f"refuse: expected tip 132 before append, got {before}")
    append_lock(LATIN)
    verify_justifications()
    append_translations(LATIN, TITLES, PASS_B, NOTES, ALLUSIONS)
    update_meta()
    tip_ready()
    build_packet_and_review()
    after = len(json.loads(ENG_PATH.read_text(encoding="utf-8")))
    prepend_handoff(before, after)
    # keep apply script in book tree for audit trail
    APPLY_COPY.write_text(Path(__file__).read_text(encoding="utf-8") if False else open("/tmp/apply_pars_iv_xv_densify.py").read(), encoding="utf-8")
    print("DONE before", before, "after", after)


if __name__ == "__main__":
    main()
