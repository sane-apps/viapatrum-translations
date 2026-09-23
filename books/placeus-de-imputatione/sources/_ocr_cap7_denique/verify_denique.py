import json
from pathlib import Path
BOOK=Path("/Users/stephansmac/SaneApps/clients/translations/books/placeus-de-imputatione")
eng=json.load(open(BOOK/"translations/cap1_tip_english.json"))
src=json.load(open(BOOK/"translations/cap1_tip_source.json"))
rev=json.load(open(BOOK/"reviews/audit/cap7_denique_modus_densify.review.json"))
pkt=json.load(open(BOOK/"reviews/audit/cap7_denique_modus_densify.packet.json"))
print("hostname check via Path only")
print("eng", len(eng), "src", len(src), "reviews", len(rev["reviews"]), "pkt secs", len(pkt["sections"]))
print("verdict", rev["verdict"], "scope", rev["scope_review"]["verdict"])
old=json.load(open(BOOK/"reviews/audit/cap7_s6_causes_densify.packet.json"))
mismatch=0
for s in pkt["sections"]:
    if int(s["section"])<=33:
        o=next(x for x in old["sections"] if x["section"]==s["section"])
        if s["english"]!=o["english"]:
            mismatch+=1
            print("MUTATED", s["section"])
print("1-33 english mismatches vs prior packet:", mismatch)
for r in rev["reviews"][-5:]:
    er=next(s for s in eng if str(s["section"])==str(r["section"]))
    print("cov", r["section"], r["covered_source_paragraphs"], "n_eng", len(er["english"]))
# multi-para older section sample
for r in rev["reviews"]:
    if r["covered_source_paragraphs"] != [1]:
        print("multi covered example", r["section"], r["covered_source_paragraphs"])
        break
print("claim:", Path("/Users/stephansmac/SaneApps/clients/translations/docs/claim-locks/placeus-de-imputatione-densify").read_text()[:400])
print("lock exists", (BOOK/"sources/_placeus_cap7_denique_latin_lock.txt").exists())
print("--- handoff ---")
print((BOOK/"SESSION_HANDOFF.md").read_text()[:900])
print("DID NOT SHIP")
