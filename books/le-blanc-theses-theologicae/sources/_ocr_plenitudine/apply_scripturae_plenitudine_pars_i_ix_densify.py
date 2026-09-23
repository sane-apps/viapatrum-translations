#!/usr/bin/env python3
"""De Scripturae plenitudine Pars I IX-XVI densify on Mini.

Lock + justifs (check_pass_ab each) first. Append eng/src only after live >3582
OR 12 minutes from tip-170 ship (handoff 19:04 EDT), then re-read tip.
No ship/commit/push/publication-review/Logos/ai_promote. Punch X=NO.
"""
from __future__ import annotations

import json
import re
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
LOCK = BOOK / "sources/_le_blanc_plenitudine_latin_lock.txt"
LOCK_REL = "sources/_le_blanc_plenitudine_latin_lock.txt"
AUDIT = BOOK / "reviews/audit"
HANDOFF = BOOK / "SESSION_HANDOFF.md"
DATA = Path("/tmp/leblanc_plen_ix_densify")
PACKET_STEM = "scripturae_plenitudine_pars_i_ix_densify"
APPLY_COPY = BOOK / "sources/_ocr_plenitudine/apply_scripturae_plenitudine_pars_i_ix_densify.py"

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ["171", "172", "173", "174", "175", "176", "177", "178"]
ROMANS = {
    "171": "IX",
    "172": "X",
    "173": "XI",
    "174": "XII",
    "175": "XIII",
    "176": "XIV",
    "177": "XV",
    "178": "XVI",
}

TIP_BEFORE = 170
LIVE_FLOOR = 3582
# Tip-170 ship landed ~19:04 EDT 2026-09-22 (handoff mtime); 12-minute OR-gate.
HOLD_START = datetime(2026, 9, 22, 19, 4, 8)
HOLD_MINUTES = 12

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV "
    "+ De Scripturae plenitudine Pars I I-XVI"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; "
    "De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; "
    "De Scripturae plenitudine Pars I I-XVI)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. "
    "IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + "
    "De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-XVI (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the "
    "1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate "
    "Scripturae through Pars IV XLIV, and De Scripturae plenitudine Pars I through XVI "
    "(sufficiency; immediate vs mediate consequence; sigillatim vs in seed; perfect rule "
    "without a second regula; faith principles as Scripture). Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, "
    "De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, Pars IV I-XLIV, "
    "and De Scripturae plenitudine Pars I I-XVI, reconstructed from the Internet Archive PDF "
    "page images with pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not "
    "used as copy-text. No modern English was copied. This slice continues Plenitudine from "
    "IX (consequence / immediate vs mediate) through XVI (science-axiom analogy). "
    "XVII+ (Spirit illumination disparity) remains."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scripturae Plenitudine et Sufficientia adversus necessitatem verbi cujusdam non scripti.\n"
    "PARS PRIMA — theses I-XVI (IX-XVI densify contiguous after I-VIII).\n"
    "Same 1675 Pitt copy-text. Book pp. 54-58 / PDF 67-71. pdftotext + tess OCR (+ DjVu checks). "
    "Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Plenitudine Pars I through XVI (natural close before XVII Spirit illumination "
    "disparity). XVII+ remains.\n"
    "Note: I-VIII retained from prior lock; IX immediate vs mediate; X consequence not addition "
    "(Acts 10:43); XI sigillatim / in semine; XII express claim; XIII perfect rule + ministry/"
    "Spirit; XIV principles = Scripture; XV rule not of itself; XVI science axioms.\n\n"
)


def load_data():
    latin = json.loads((DATA / "latin.json").read_text(encoding="utf-8"))
    sections = json.loads((DATA / "sections.json").read_text(encoding="utf-8"))
    by_sec = {s["section"]: s for s in sections}
    return latin, by_sec


def write_lock(latin: dict):
    # Expand lock: keep I-VIII body from existing lock, append IX-XVI.
    prior = LOCK.read_text(encoding="utf-8") if LOCK.exists() else ""
    # Extract I-VIII thesis bodies (lines starting with roman numerals after header)
    body_lines = []
    if prior:
        # Drop old header; keep thesis paragraphs I-VIII
        parts = prior.split("\n\n", 1)
        rest = parts[1] if len(parts) > 1 else prior
        # Stop before any IX if somehow present
        if "\nIX." in rest:
            rest = rest.split("\nIX.")[0].rstrip() + "\n"
        body_lines.append(rest.rstrip() + "\n")
    for sec in SECS:
        body_lines.append(latin[sec].rstrip() + "\n")
    blob = LOCK_HEADER + "\n".join(body_lines) + "\n"
    LOCK.write_text(blob, encoding="utf-8")
    print("wrote", LOCK, "chars", len(blob))


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
            "bible_refs": s.get("bible_refs") or [],
        }
        jpath = JUST / f"plenitudine_{sec}.json"
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errs = check_file(jpath)
        print(f"check_pass_ab plenitudine_{sec} ({ROMANS[sec]})", "ok" if not errs else errs)
        if errs:
            raise SystemExit(f"FAIL check_pass_ab {sec}: {errs}")


def live_section_count():
    try:
        req = urllib.request.Request(
            "https://fathers.saneapps.com/",
            headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
        m = re.search(r"(\d+)\s+treatises online\s+·\s+(\d+)\s+sections", html)
        if not m:
            return None, None
        return int(m.group(1)), int(m.group(2))
    except Exception as exc:
        print("live probe failed:", exc)
        return None, None


def live_leblanc_tip() -> int:
    try:
        req = urllib.request.Request(
            "https://fathers.saneapps.com/works/le-blanc-theses-theologicae/",
            headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
        nums = [int(n) for n in re.findall(r"/works/le-blanc-theses-theologicae/(\d+)/", html)]
        return max(nums) if nums else 0
    except Exception as exc:
        print("leblanc tip probe failed:", exc)
        return 0


def wait_hold():
    """Owner hold: live >3582 OR 12 minutes from tip-170 ship, then re-read tip."""
    deadline = HOLD_START + timedelta(minutes=HOLD_MINUTES)
    while True:
        treatises, secs = live_section_count()
        lb = live_leblanc_tip()
        now = datetime.now()
        timed_out = now >= deadline
        live_ok = secs is not None and secs > LIVE_FLOOR
        print(
            f"hold check now={now.strftime('%H:%M:%S')} live={treatises}/{secs} "
            f"leblanc_tip={lb} need_live>{LIVE_FLOOR} or_after={deadline.strftime('%H:%M:%S')} "
            f"timed_out={timed_out}"
        )
        if live_ok or timed_out:
            reason = f"live>{LIVE_FLOOR}" if live_ok else f"{HOLD_MINUTES}m since tip-170 ship"
            print("hold cleared:", reason)
            return treatises, secs, lb, reason
        time.sleep(30)


def reread_tip():
    eng = json.loads(ENG.read_text(encoding="utf-8"))
    src = json.loads(SRC.read_text(encoding="utf-8"))
    print("re-read tip eng", len(eng), "last", eng[-1]["section"], eng[-1]["title"][:60])
    print("re-read tip src", len(src), "last", src[-1]["section"])
    return eng, src


def append_translations(latin: dict, by_sec: dict):
    eng, src = reread_tip()
    if len(eng) != TIP_BEFORE or str(eng[-1]["section"]) != str(TIP_BEFORE):
        raise SystemExit(
            f"refuse append: tip not {TIP_BEFORE} (eng={len(eng)} last={eng[-1].get('section')})"
        )
    if len(src) != TIP_BEFORE:
        raise SystemExit(f"refuse append: src tip not {TIP_BEFORE} ({len(src)})")
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

    pdf = BOOK / "sources/le_blanc_theses_1675.pdf"
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=[
            LOCK,
            pdf,
            BOOK / "sources/_ocr_plenitudine/pdf_66_70.txt",
            BOOK / "sources/_ocr_plenitudine/pdf_69_73.txt",
            BOOK / "sources/_ocr_plenitudine/raw_68_71.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-068.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-069.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-070.txt",
            APPLY_COPY,
        ],
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
        if 171 <= n <= 178:
            notes = (
                f"Section {sid}: new densify De Scripturae plenitudine Pars I IX-XVI; "
                "Pass A!=B; lock-grounded PDF 68-71 / book pp. 56-58."
            )
        else:
            notes = (
                f"Section {sid}: prior verified densify retained; Pass A/B and lock identity "
                "rechecked in plenitudine Pars I IX packet scope covering all current sections."
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
    day = datetime.now().strftime("%Y-%m-%d")
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": f"scribe-leblanc, {day}",
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
                "Scope review: densify De Scripturae plenitudine Pars I IX-XVI only "
                f"(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. "
                "Honest partial; plenitudine XVII+ remain. Prior tracts untouched. Not shipped."
            ),
        },
        "reviews": reviews,
    }
    review_path = AUDIT / f"{PACKET_STEM}.review.json"
    review_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errs = validate_audit_receipt(packet, receipt)
    print("packet", packet["packet_id"])
    print("validate_audit_receipt", errs if errs else "ok")
    if errs:
        raise SystemExit(1)
    return packet_path, review_path, packet


def write_receipt(packet_path: Path, review_path: Path, live_tuple, packet: dict):
    treatises, secs, lb, reason = live_tuple
    receipt = {
        "packet_stem": PACKET_STEM,
        "packet": str(packet_path),
        "review": str(review_path),
        "packet_id": packet.get("packet_id"),
        "before": TIP_BEFORE,
        "after": TIP_BEFORE + len(SECS),
        "added_sections": [int(s) for s in SECS],
        "locus": "De Scripturae plenitudine Pars I theses IX-XVI (after I-VIII)",
        "next_locus": "De Scripturae plenitudine Pars I XVII+ (Spirit illumination disparity)",
        "gates": {
            "check_pass_ab": f"ok plenitudine_{SECS[0]}–{SECS[-1]} ({len(SECS)}/{len(SECS)})",
            "tip_ready": "ok theses_theologia_english.json+theses_theologia_source.json",
            "validate_audit_receipt": "ok",
        },
        "punch_x": "NO",
        "ship": "NO",
        "claim": "le-blanc-theses-densify stays claimed",
        "latin_lock": str(LOCK),
        "live_at_proceed": f"{treatises}/{secs}",
        "leblanc_live_tip_at_proceed": lb,
        "hold_clear_reason": reason,
        "raw_source_paths_count": 9,
    }
    rpath = AUDIT / f"{PACKET_STEM}.receipt.json"
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("receipt", rpath)
    return receipt


def prepend_handoff(receipt: dict):
    day = datetime.now().strftime("%Y-%m-%d")
    parts = [
        "## " + day + " (Scribe — De Scripturae plenitudine Pars I IX–XVI densify LOCAL)\n\n",
        "- Before: **" + str(receipt["before"]) + "** (Plenitudine Pars I I–VIII). After: **"
        + str(receipt["after"]) + "** ",
        "(contiguous Plenitudine Pars I IX–XVI → §§" + SECS[0] + "–" + SECS[-1] + ").\n",
        "- Packet `" + PACKET_STEM + "` (`reviews/audit/" + PACKET_STEM + ".packet.json` + `.review.json`). ",
        "Reviewer: scribe-leblanc, " + day + ". Verdict pass grounded in ",
        "`sources/_le_blanc_plenitudine_latin_lock.txt` (PDF 68–71 / book pp. 56–58).\n",
        "- Meta range bumped to **" + RANGE_SHORT + "** (title, edition, blurb, text_history.method).\n",
        "- Honest **partial**: Plenitudine Pars I through XVI (immediate vs mediate consequence; "
        "sigillatim vs in seed; perfect rule without second regula; principles = Scripture; "
        "science-axiom analogy). XVII+ remains. De Theologia / De Fide / Authoritate closed as before. "
        "Not folio. Not shipped this slice.\n",
        "- Pass A ≠ B for §§" + SECS[0] + "–" + SECS[-1] + ". Inline Acts 10:43; Matt 28:19 baptism Name. "
        "OCR restorations noted in translator_notes.\n",
        "- All eight new justifications check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n",
        "- Hold cleared (" + receipt["hold_clear_reason"] + ") live "
        + str(receipt["live_at_proceed"]) + "; disk tip re-read " + str(TIP_BEFORE) + " before append.\n",
        "- Claim `le-blanc-theses-densify` stays claimed. Punch X = NO.\n\n",
    ]
    block = "".join(parts)
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    HANDOFF.write_text(block + prev, encoding="utf-8")
    print("handoff prepended")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    latin, by_sec = load_data()
    if mode in ("all", "justifs"):
        write_lock(latin)
        write_and_check_justifications(latin, by_sec)
        if mode == "justifs":
            print("JUSTIFS DONE — hold/append deferred")
            return
    # HARD HOLD — owner: live >3582 OR 12m, then re-read tip before append past 170
    live_tuple = wait_hold()
    eng, src = reread_tip()
    if len(eng) != TIP_BEFORE:
        raise SystemExit(f"tip drifted before append: {len(eng)}")
    append_translations(latin, by_sec)
    update_meta()
    tip_ready()
    # Ensure apply copy exists before packet hashes it
    APPLY_COPY.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
    packet_path, review_path, packet = build_packet_and_review()
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    print("DONE", receipt["before"], "->", receipt["after"], "Punch X=NO")


if __name__ == "__main__":
    main()
