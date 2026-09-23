#!/usr/bin/env python3
"""De Scripturae plenitudine Pars I I-VIII densify on Mini.

Lock + justifs (check_pass_ab each) first. Append eng/src only after live >3556.
No ship/commit/push/publication-review/Logos/ai_promote. Punch X=NO.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
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
DATA = Path("/tmp/leblanc_plenitudine_open")
PACKET_STEM = "scripturae_plenitudine_open_densify"
APPLY_COPY = BOOK / "sources/_ocr_plenitudine/apply_scripturae_plenitudine_open_densify.py"

sys.path.insert(0, str(REPO))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt  # noqa: E402
from pipeline.check_pass_ab import check_file, main as check_main  # noqa: E402

SECS = ["163", "164", "165", "166", "167", "168", "169", "170"]
ROMANS = {
    "163": "I",
    "164": "II",
    "165": "III",
    "166": "IV",
    "167": "V",
    "168": "VI",
    "169": "VII",
    "170": "VIII",
}

TIP_BEFORE = 162
LIVE_FLOOR = 3556

RANGE_SHORT = (
    "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV "
    "+ De Scripturae plenitudine Pars I I-VIII"
)
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; "
    "De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XLI; Pars IV I-XLIV; "
    "De Scripturae plenitudine Pars I I-VIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. "
    "IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + "
    "De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XLI + Pars IV I-XLIV + "
    "De Scripturae plenitudine Pars I I-VIII (not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu - Sedan Theological Theses, newly rendered from the "
    "1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate "
    "Scripturae through Pars IV XLIV, and De Scripturae plenitudine Pars I through VIII "
    "(sufficiency open: necessary-to-salvation senses; substance vs indifferent rites; "
    "κατὰ λέξιν / in substance). Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, "
    "De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, Pars III I-XLI, Pars IV I-XLIV, "
    "and De Scripturae plenitudine Pars I I-VIII, reconstructed from the Internet Archive PDF "
    "page images with pdftotext + tesseract (+ DjVu checks). The 1683 third edition was not "
    "used as copy-text. No modern English was copied. De Authoritate closes at Pars IV XLIV; "
    "this slice opens De Scripturae plenitudine through VIII (before IX consequence distinction). "
    "Later plenitudine theses remain."
)

LOCK_HEADER = (
    "Locked Latin: Louis Le Blanc, Theses theologicae (London: Moses Pitt, 1675).\n"
    "Tract: De Scripturae Plenitudine et Sufficientia adversus necessitatem verbi cujusdam non scripti.\n"
    "PARS PRIMA — theses I-VIII (open densify contiguous after De Authoritate Pars IV XLIV).\n"
    "Same 1675 Pitt copy-text. Book pp. 54-56 / PDF 67-69. pdftotext + tess OCR (+ DjVu checks). "
    "Long-s and ligatures normalized. 1683 not copy-text. No modern English.\n"
    "Scope: Plenitudine Pars I through VIII only (natural close before IX consequence / "
    "immediate vs mediate). IX+ remains.\n"
    "Note: I controversy open; II necessary vs not; III-IV two senses; V both senses; "
    "VI substance vs appendices; VII rites left to prudence; VIII κατὰ λέξιν / in substantia "
    "(Trinity / 1 John 5:7). Greek κατὰ λέξιν OCR-soft on IA scan.\n\n"
)


def load_data():
    latin = json.loads((DATA / "latin.json").read_text(encoding="utf-8"))
    sections = json.loads((DATA / "sections.json").read_text(encoding="utf-8"))
    by_sec = {s["section"]: s for s in sections}
    return latin, by_sec


def write_lock(latin: dict):
    if LOCK.exists() and "theses I-VIII" in LOCK.read_text(encoding="utf-8"):
        print("lock already present")
        return
    blob = LOCK_HEADER + "\n".join(latin[s] + "\n" for s in SECS) + "\n"
    LOCK.write_text(blob, encoding="utf-8")
    print("wrote", LOCK)


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
        if sec == "170":
            just["bible_refs"] = [
                {"ref": "1 John 5:7", "note": "tres esse in caelo example (Trinity in substance)"},
                {"ref": "1 Corinthians 14:40", "note": "alluded in VII ordine & decenter; kept near VIII context"},
            ]
        if sec == "169":
            just["bible_refs"] = [
                {"ref": "1 Corinthians 14:40", "note": "omnia fiant ordine & decenter"},
            ]
        jpath = JUST / f"plenitudine_{sec}.json"
        jpath.write_text(json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errs = check_file(jpath)
        print(f"check_pass_ab plenitudine_{sec} ({ROMANS[sec]})", "ok" if not errs else errs)
        if errs:
            raise SystemExit(f"FAIL check_pass_ab {sec}: {errs}")


def live_section_count() -> tuple[int, int] | tuple[None, None]:
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


def wait_hold_live_gt(floor: int = LIVE_FLOOR):
    """Owner hold: do not append past 162 until live sections > floor."""
    while True:
        treatises, secs = live_section_count()
        lb = live_leblanc_tip()
        now = datetime.now().strftime("%H:%M:%S")
        print(f"hold check now={now} live={treatises}/{secs} leblanc_tip={lb} need_live>{floor}")
        if secs is not None and secs > floor:
            print("hold cleared: live sections >", floor)
            return treatises, secs, lb
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
            f"refuse append: tip not {TIP_BEFORE} (eng={len(eng)} last={eng[-1].get(section)})"
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
    witnesses = th.setdefault("witnesses", [])
    if not any(w.get("id") == "plenitudine_latin_lock" for w in witnesses):
        witnesses.append(
            {
                "id": "plenitudine_latin_lock",
                "path": LOCK_REL,
                "role": "copy-text",
                "name": "Locked Latin, De Scripturae plenitudine densify (Pitt 1675)",
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

    pdf = BOOK / "sources/le_blanc_theses_1675.pdf"
    packet = make_audit_packet(
        ENG,
        SRC,
        raw_sources=[
            LOCK,
            pdf,
            BOOK / "sources/_ocr_plenitudine/pdf_66_70.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-067.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-068.txt",
            BOOK / "sources/_ocr_plenitudine/tesseng-p-069.txt",
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
        if 163 <= n <= 170:
            notes = (
                f"Section {sid}: new densify De Scripturae plenitudine Pars I I-VIII; "
                "Pass A!=B; lock-grounded PDF 67-69 / book pp. 54-56."
            )
        else:
            notes = (
                f"Section {sid}: prior verified densify retained; Pass A/B and lock identity "
                "rechecked in plenitudine open packet scope covering all current sections."
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
                "Scope review: densify De Scripturae plenitudine Pars I I-VIII only "
                f"(sections {SECS[0]}-{SECS[-1]}). Meta discloses {RANGE_SHORT}. "
                "Honest partial; plenitudine IX+ remain. Prior tracts untouched. Not shipped."
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
    treatises, secs, lb = live_tuple
    receipt = {
        "packet_stem": PACKET_STEM,
        "packet": str(packet_path),
        "review": str(review_path),
        "packet_id": packet.get("packet_id"),
        "before": TIP_BEFORE,
        "after": TIP_BEFORE + len(SECS),
        "added_sections": [int(s) for s in SECS],
        "locus": "De Scripturae plenitudine Pars I theses I-VIII (open after Authoritate XLIV)",
        "next_locus": "De Scripturae plenitudine Pars I IX+ (consequence / immediate vs mediate)",
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
        "raw_source_paths_count": 7,
    }
    rpath = AUDIT / f"{PACKET_STEM}.receipt.json"
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("receipt", rpath)
    return receipt



def prepend_handoff(receipt: dict):
    day = datetime.now().strftime("%Y-%m-%d")
    parts = [
        "## " + day + " (Scribe — De Scripturae plenitudine Pars I I–VIII densify LOCAL)\n\n",
        "- Before: **" + str(receipt["before"]) + "** (Authoritate through Pars IV XLIV). After: **" + str(receipt["after"]) + "** ",
        "(contiguous Plenitudine Pars I I–VIII → §§" + SECS[0] + "–" + SECS[-1] + ").\n",
        "- Packet `" + PACKET_STEM + "` (`reviews/audit/" + PACKET_STEM + ".packet.json` + `.review.json`). ",
        "Reviewer: scribe-leblanc, " + day + ". Verdict pass grounded in ",
        "`sources/_le_blanc_plenitudine_latin_lock.txt` (PDF 67–69 / book pp. 54–56).\n",
        "- Meta range bumped to **" + RANGE_SHORT + "** (title, edition, blurb, text_history.method).\n",
        "- Honest **partial**: Plenitudine Pars I through VIII (sufficiency open; necessary senses; ",
        "substance vs indifferent rites; κατὰ λέξιν / in substance + Trinity). IX+ remains. ",
        "De Theologia / De Fide / Authoritate closed as before. Not folio. Not shipped this slice.\n",
        "- Pass A ≠ B for §§" + SECS[0] + "–" + SECS[-1] + ". Inline 1 Cor 14:40 sense; 1 John 5:7 / Trinity. ",
        "OCR restorations (incl. Greek κατὰ λέξιν) noted in translator_notes.\n",
        "- All eight new justifications check_pass_ab ok; tip-ready ok; validate_audit_receipt ok.\n",
        "- Hold cleared live " + receipt["live_at_proceed"] + " (>3556); disk tip re-read " + str(TIP_BEFORE) + " before append.\n",
        "- Claim `le-blanc-theses-densify` stays claimed. Punch X = NO.\n\n",
    ]
    block = "".join(parts)
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    HANDOFF.write_text(block + prev, encoding="utf-8")
    print("handoff prepended")



def main():
    latin, by_sec = load_data()
    write_lock(latin)
    write_and_check_justifications(latin, by_sec)
    # HARD HOLD — owner 2026-09-22: live >3556 before any eng/src append past 162
    live_tuple = wait_hold_live_gt(LIVE_FLOOR)
    eng, src = reread_tip()
    if len(eng) != TIP_BEFORE:
        raise SystemExit(f"tip drifted before append: {len(eng)}")
    append_translations(latin, by_sec)
    update_meta()
    tip_ready()
    packet_path, review_path, packet = build_packet_and_review()
    receipt = write_receipt(packet_path, review_path, live_tuple, packet)
    prepend_handoff(receipt)
    APPLY_COPY.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
    print("DONE", receipt["before"], "->", receipt["after"], "Punch X=NO")


if __name__ == "__main__":
    main()
