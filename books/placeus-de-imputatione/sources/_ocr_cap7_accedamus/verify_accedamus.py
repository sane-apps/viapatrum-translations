# -*- coding: utf-8 -*-
import json
from pathlib import Path
import sys
ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import validate_audit_receipt

print("hostname done separately")
BOOK = ROOT / "books/placeus-de-imputatione"
eng = json.loads((BOOK / "translations/cap1_tip_english.json").read_text())
src = json.loads((BOOK / "translations/cap1_tip_source.json").read_text())
pkt = json.loads((BOOK / "reviews/audit/cap7_accedamus_densify.packet.json").read_text())
rev = json.loads((BOOK / "reviews/audit/cap7_accedamus_densify.review.json").read_text())
errs = validate_audit_receipt(pkt, rev)
print("sections eng/src/pkt/rev", len(eng), len(src), len(pkt["sections"]), len(rev["reviews"]))
print("validate errors", len(errs))
print("last title:", eng[-1]["title"])
print("new titles:")
for s in eng[38:]:
    print(" ", s["section"], s["title"])
for sid in ["39", "40", "41", "42", "43"]:
    j = json.loads((BOOK / f"reviews/justifications/cap7_{sid}.json").read_text())
    assert j["pass_a_ne_b"] and j["pass_a_gloss"] != " ".join(j["pass_b_english"])
    print(sid, "dist", j["a_neq_b_distance"], "ok")
old = json.loads((BOOK / "reviews/audit/cap7_denique_modus_densify.packet.json").read_text())
mismatch = 0
for s in pkt["sections"]:
    if int(s["section"]) <= 38:
        o = next(x for x in old["sections"] if str(x["section"]) == str(s["section"]))
        if s["english"] != o["english"]:
            mismatch += 1
            print("MUTATED", s["section"])
print("1-38 english mismatches vs denique packet:", mismatch)
lock = (BOOK / "sources/_placeus_cap7_accedamus_latin_lock.txt").read_text()
assert "Accedamus" in lock
assert "\u1f10\u03c6\u1fbd \u1fa7" in lock or "\u1f10\u03c6\u1fbd\u1fa7" in lock
assert "\u1f14\u03c1\u03b3\u03bf\u03bd" not in lock
print("lock greek ok; no ergon")
print("claim", (ROOT / "docs/claim-locks/placeus-de-imputatione-densify/agent.txt").read_text().strip())
print("DID NOT SHIP")
print((BOOK / "SESSION_HANDOFF.md").read_text()[:750])
assert len(errs) == 0
assert len(eng) == 43
assert mismatch == 0
