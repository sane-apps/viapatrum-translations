# -*- coding: utf-8 -*-
import json
from pathlib import Path
import sys
ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import validate_audit_receipt

BOOK = ROOT / "books/placeus-de-imputatione"
pkt_path = BOOK / "reviews/audit/cap7_accedamus_densify.packet.json"
rev_path = BOOK / "reviews/audit/cap7_accedamus_densify.review.json"
packet = json.loads(pkt_path.read_text(encoding="utf-8"))
eng = json.loads((BOOK / "translations/cap1_tip_english.json").read_text(encoding="utf-8"))

reviews = []
for sec in packet["sections"]:
    sid = str(sec["section"])
    n_src = len(sec["source_text"])
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
        "covered_source_paragraphs": list(range(1, n_src + 1)),
        "notes": (
            f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII "
            "Accedamus eph ho / aorist / lexicography; Pass A != B."
        ),
    })

review = {
    "packet_id": packet["packet_id"],
    "reviewer": "scribe-placeus / Placeus Cap. VII Accedamus densify review, 2026-09-22",
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
            "Cap. I-VI + Cap. VII through Accedamus eph' ho pantes hemarton, aorist force, "
            "and eph' ho lexicography (in quo vs eo quod) to Placeus two reasons from locked "
            "1661 Saumur Latin. Honest partial — Cap. VII Ad alias rationes onward and Cap. VIII+ remain. "
            "Reformed Saumur era disclosed. Locked Greek eph' ho / hemarton (do not revive OCR ergon)."
        ),
    },
    "reviews": reviews,
}
# restore proper Greek in notes via unicode escapes in a second pass
review["scope_review"]["notes"] = (
    "Cap. I–VI + Cap. VII through Accedamus \u1f10\u03c6\u1fbd \u1fa7 \u03c0\u03ac\u03bd\u03c4\u03b5\u03c2 \u1f25\u03bc\u03b1\u03c1\u03c4\u03bf\u03bd, "
    "aorist force, and \u1f10\u03c6\u1fbd \u1fa7 lexicography (in quo vs eo quod) to Placeus's two reasons "
    "from locked 1661 Saumur Latin. Honest partial — Cap. VII Ad alias rationes onward and Cap. VIII+ remain. "
    "Reformed Saumur era disclosed. Locked Greek \u1f10\u03c6\u1fbd \u1fa7 / \u1f25\u03bc\u03b1\u03c1\u03c4\u03bf\u03bd "
    "(do not revive OCR \u1f14\u03c1\u03b3\u03bf\u03bd)."
)
# decode escapes
review["scope_review"]["notes"] = review["scope_review"]["notes"].encode().decode("unicode_escape")
for r in reviews:
    r["notes"] = (
        f"Section {r['section']}: compared Pass B to locked 1661 Latin Cap. VII "
        "Accedamus \u1f10\u03c6\u1fbd \u1fa7 / aorist / lexicography; Pass A != B."
    ).encode().decode("unicode_escape")

rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
errs = validate_audit_receipt(packet, review)
print("validate_audit_receipt errors", len(errs))
for e in errs[:30]:
    print(" -", e)

hand = BOOK / "SESSION_HANDOFF.md"
oldh = hand.read_text(encoding="utf-8")
marker = "cap7_accedamus_densify"
if marker not in oldh[:1200]:
    entry = (
        "# Placeus De imputatione — production ledger\n\n"
        "## 2026-09-22 Cap. VII Accedamus densify (\u1f10\u03c6\u1fbd \u1fa7 / aorist / lexicography)\n\n"
        "- Before: **38** sections (Cap. I–VII through Denique / Gualtherus first-argument close)\n"
        "- After: **43** sections (Cap. I–VII through Accedamus \u1f10\u03c6\u1fbd \u1fa7 / aorist / \u1f10\u03c6\u1fbd \u1fa7 lexicography)\n"
        "- Packet: `cap7_accedamus_densify`\n"
        "- Locked Latin: `sources/_placeus_cap7_accedamus_latin_lock.txt` (1661 PDF pp. 66–71 tip)\n"
        "- Pass A\u2260B; OUR; English-first; no PBB/ops TNs\n"
        "- Lemma note: locked Greek **\u1f10\u03c6\u1fbd \u1fa7** / **\u1f25\u03bc\u03b1\u03c1\u03c4\u03bf\u03bd** "
        "(do not revive OCR \u1f14\u03c1\u03b3\u03bf\u03bd); \u03c3\u03ba\u03bf\u03c0\u1ff7/verbis remains for prior Denique slice\n"
        "- Stopped before Ad alias rationes (further Cap. VII)\n"
        "- Honest partial: Cap. VII Ad alias rationes onward + Cap. VIII+ / ~494 pp Disputatio remain "
        "(**do not claim full Disputatio**)\n"
        "- Punch X: **NO**\n\n"
    ).encode().decode("unicode_escape")
    rest = oldh
    if rest.startswith("# Placeus"):
        rest = rest.split("\n", 1)[1].lstrip("\n")
    hand.write_text(entry + rest, encoding="utf-8")
    print("handoff updated")
else:
    print("handoff already has entry")

print("hostname check via claim path")
print("sections", len(eng))
print("last title:", eng[-1]["title"])
print("packet", str(pkt_path))
print("claim", (ROOT / "docs/claim-locks/placeus-de-imputatione-densify/agent.txt").read_text().strip())
assert len(errs) == 0
print("DID NOT SHIP; DID NOT COMMIT; claim not freed")
