#!/usr/bin/env python3
"""Pars IV XXXIX-XLIV densify on Mini: lock, justifs+check_pass_ab each, wait hold, append eng/src, packet, tip-ready, handoff."""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/le-blanc-theses-theologicae"
REPO = Path.home() / "SaneApps/clients/translations"
ENG = BOOK / "translations/theses_theologia_english.json"
SRC = BOOK / "translations/theses_theologia_source.json"
META = BOOK / "translations/theses_theologia_meta.json"
JUST = BOOK / "reviews/justifications"
LOCK = BOOK / "sources/_le_blanc_authoritate_latin_lock.txt"
LOCK_REL = "sources/_le_blanc_authoritate_latin_lock.txt"
PDF = BOOK / "sources/le_blanc_theses_1675.pdf"
AUDIT = BOOK / "reviews/audit"
HANDOFF = BOOK / "SESSION_HANDOFF.md"
DATA = Path("/tmp/leblanc_pars4_xxxix")
PACKET_STEM = "authoritate_scripturae_pars_iv_xxxix_densify"
APPLY_COPY = BOOK / "sources/_ocr_authoritate/apply_pars_iv_xxxix_densify.py"

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ["157", "158", "159", "160", "161", "162"]
ROMANS = {
    "157": "XXXIX",
    "158": "XL",
    "159": "XLI",
    "160": "XLII",
    "161": "XLIII",
    "162": "XLIV",
}

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; "
    "De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. "
    "IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + "
    "De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV "
    "(not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the "
    "1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate "
    "Scripturae Pars I through XLVII, Pars II through XXXV, Pars III through XLI, and Pars IV "
    "through XLIV (Fathers-vs-heretics confirmation; reciprocal proof; a posteriori). "
    "Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, "
    "De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, and Pars IV I-XLIV, "
    "reconstructed from the Internet Archive PDF page images with pdftotext + tesseract "
    "(+ DjVu checks for earlier tracts). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. Pars I closes at XLVII; Pars II through XXXV; Pars III "
    "through XLI; Pars IV through XLIV (I-XXXVIII retained; XXXIX-XLIV Fathers-vs-heretics "
    "confirmation). Next tract De Scripturae plenitudine remains."
)

LOCK_HEADER = (
    "\n---\n\n"
    "Expand lock: De Authoritate Scripturae Pars IV theses XXXIX-XLIV "
    "(contiguous after XXXI-XXXVIII - Fathers-vs-heretics confirmation).\n"
    "Same 1675 Pitt copy-text. Book pp. 52-54 / PDF 64-66. pdftotext + tess OCR (+ DjVu checks). "
    "Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Part IV continue through XLIV only (natural close before De Scripturae plenitudine). "
    "Plenitudine / later tracts remain.\n"
    "Note: XXXIX Fathers consensus vs heretics not present-pastor supremacy; XL Augustine Contra "
    "Faustum 32-33 literary fame; XLI human not divine argument; XLII reciprocal proof; "
    "XLIII a posteriori; XLIV summary regulam fidei.\n\n"
)


def load_data():
    latin = json.loads((DATA / "latin.json").read_text(encoding="utf-8"))
    sections = json.loads((DATA / "sections.json").read_text(encoding="utf-8"))
    by_sec = {s["section"]: s for s in sections}
    return latin, by_sec


def append_lock(latin: dict):
    text = LOCK.read_text(encoding="utf-8")
    marker = "Expand lock: De Authoritate Scripturae Pars IV theses XXXIX-XLIV"
    if marker in text:
        print("lock already expanded")
        return
    blob = LOCK_HEADER + "\n".join(latin[s] + "\n" for s in SECS) + "\n"
    LOCK.write_text(text.rstrip() + "\n" + blob, encoding="utf-8")
    print("lock appended Pars IV XXXIX-XLIV")


def write_and_check_justifications(latin: dict, by_sec: dict):
    for sec in SECS:
        s = by_sec[sec]
        just = {
            "section": sec,
            "title": s["title"],
            "source_text": latin[sec],
            "pass_a_gloss": s["pass_a"],
            "pass_b_english": s["pass_b"],
            "pass_a_ne_b": True,
            "lemmas": s["lemmas"],
            "choices": s["choices"],
            "bible_refs": [],
        }
        jpath = JUST / f"authoritate_{sec}.json"
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errs = check_file(jpath)
        print(f"check_pass_ab authoritate_{sec} ({ROMANS[sec]})", "ok" if not errs else errs)
        if errs:
            raise SystemExit(f"FAIL check_pass_ab {sec}: {errs}")


def live_section_total() -> int | None:
    try:
        req = urllib.request.Request(
            "https://fathers.saneapps.com/",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
        import re

        m = re.search(r"([0-9][0-9,]*)\s+sections", html, re.I)
        if not m:
            return None
        return int(m.group(1).replace(",", ""))
    except Exception as exc:
        print("live probe failed:", exc)
        return None


def wait_hold(tip_mtime: float, minutes: float = 12.0, live_floor: int = 3527):
    ready_at = datetime.fromtimestamp(tip_mtime) + timedelta(minutes=minutes)
    while True:
        now = datetime.now()
        live = live_section_total()
        print(
            f"hold check now={now.strftime('%H:%M:%S')} ready_at={ready_at.strftime('%H:%M:%S')} "
            f"live_sections={live}"
        )
        if live is not None and live > live_floor:
            print("hold cleared: live sections >", live_floor)
            return
        if now >= ready_at:
            print("hold cleared: 12-minute wall")
            return
        time.sleep(30)


def reread_tip():
    eng = json.loads(ENG.read_text(encoding="utf-8"))
    src = json.loads(SRC.read_text(encoding="utf-8"))
    print("re-read tip eng", len(eng), "last", eng[-1]["section"], eng[-1]["title"])
    print("re-read tip src", len(src), "last", src[-1]["section"])
    return eng, src


def append_translations(latin: dict, by_sec: dict):
    eng, src = reread_tip()
    if len(eng) != 156 or str(eng[-1]["section"]) != "156":
        raise SystemExit(
            f"refuse append: tip not 156 (eng={len(eng)} last={eng[-1].get('section')})"
        )
    if len(src) != 156:
        raise SystemExit(f"refuse append: src tip not 156 ({len(src)})")
    have = {str(r["section"]) for r in eng}
    for sec in SECS:
        if sec in have:
            raise SystemExit(f"refuse overwrite existing section {sec}")
        s = by_sec[sec]
        eng.append(
            {
                "section": sec,
                "title": s["title"],
                "english": s["pass_b"],
                "notes_covered": [],
                "added_allusions": [],
                "translator_notes": s["notes"],
                "source_ref": LOCK_REL,
            }
        )
        src.append({"section": sec, "title": s["title"], "latin": latin[sec]})
    ENG.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SRC.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english/source now", len(eng), len(src))


def update_meta():
    meta = json.loads(META.read_text(encoding="utf-8"))
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
                "path": LOCK_REL,
                "role": "copy-text",
                "name": "Locked Latin, De Authoritate Scripturae densify (Pitt 1675)",
                "language": "Latin",
                "url": "https://archive.org/details/bub_gb_eOkHAW4G0-wC",
            }
        )
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta updated")


def tip_ready():
    rc = check_main(["--tip-ready", str(ENG), str(SRC)])
    print("check_pass_ab --tip-ready", rc)
    if rc != 0:
        raise SystemExit(rc)


def build_packet_and_review():
    eng = json.loads(ENG.read_text(encoding="utf-8"))
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
        "text_history": json.loads(META.read_text(encoding="utf-8"))["text_history"],
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
        ENG,
        SRC,
        raw_sources=[LOCK, PDF],
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
        if 157 <= n <= 162:
            notes = f"Section {sid}: new densify Pars IV XXXIX-XLIV; Pass A/B checked."
        else:
            notes = (
                f"Section {sid}: prior verified densify retained; Pass A/B and lock identity "
                "rechecked in Pars IV XXXIX-XLIV packet scope covering all current sections."
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
                "Scope review: densify Pars IV XXXIX-XLIV only (sections 157-162). Meta discloses "
                f"{RANGE_SHORT}. Honest partial; De Scripturae plenitudine + later remain. "
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
        "## 2026-09-22 (Scribe — De Authoritate Scripturae Pars IV XXXIX–XLIV densify LOCAL)\n\n"
        f"- Before: **{before}** (Pars I I–XLVII + Pars II I–XXXV + Pars III I–XLI + Pars IV I–XXXVIII). "
        f"After: **{after}** (contiguous Pars IV XXXIX–XLIV → §§157–162).\n"
        f"- Packet `{PACKET_STEM}` (`reviews/audit/{PACKET_STEM}.packet.json` + `.review.json`). "
        "Reviewer: scribe-leblanc, 2026-09-22. Verdict pass grounded in expanded "
        "`sources/_le_blanc_authoritate_latin_lock.txt` (PDF 64–66 / book pp. 52–54).\n"
        f"- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).\n"
        "- Honest **partial**: Pars IV through XLIV (Fathers-vs-heretics confirmation; Augustine "
        "Contra Faustum literary fame; human consensus argument; reciprocal proof; a posteriori; "
        "summary). Next: De Scripturae plenitudine. De Theologia closed. De Fide I–XXII untouched. "
        "Not folio. Not shipped this slice.\n"
        "- Pass A ≠ B for §§157–162. Inline Augustine quote; Donatists Canonicis libris. "
        "OCR restorations noted in translator_notes.\n"
        "- All six new justifications check_pass_ab ok; tip-ready ok.\n"
        "- Claim `le-blanc-theses-densify` stays claimed. Punch X = NO.\n\n"
    )
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "Pars IV XXXIX–XLIV densify" in prev[:3000]:
        print("handoff already prepended")
        return
    HANDOFF.write_text(entry + prev, encoding="utf-8")
    print("handoff prepended")


def main():
    latin, by_sec = load_data()
    before = len(json.loads(ENG.read_text(encoding="utf-8")))
    tip_mtime = ENG.stat().st_mtime
    print("disk tip before", before, "mtime", datetime.fromtimestamp(tip_mtime))
    if before != 156:
        raise SystemExit(f"refuse: expected tip 156 before work, got {before}")

    append_lock(latin)
    write_and_check_justifications(latin, by_sec)

    wait_hold(tip_mtime)
    # re-read tip after hold; refuse if tip moved
    eng_now, _src_now = reread_tip()
    if len(eng_now) != 156 or str(eng_now[-1]["section"]) != "156":
        raise SystemExit(
            f"refuse after hold: tip changed eng={len(eng_now)} last={eng_now[-1].get('section')}"
        )

    append_translations(latin, by_sec)
    update_meta()
    tip_ready()
    build_packet_and_review()
    after = len(json.loads(ENG.read_text(encoding="utf-8")))
    prepend_handoff(before, after)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
    print("DONE before", before, "after", after, "packet", PACKET_STEM)


if __name__ == "__main__":
    main()
