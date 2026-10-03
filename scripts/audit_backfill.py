#!/usr/bin/env python3
"""One-off: load 2026-10-02 receipts into the audit log (outputs/audit/events.jsonl).

Receipts without per-row times take the receipt file's modification time and
are marked approx=True. Safe to run once; refuses if backfill already ran.
"""
import json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_log as A  # noqa: E402

ROOT = A.ROOT
OUT = ROOT / "outputs"
marker = OUT / "audit" / ".backfill-20261002"
if marker.exists():
    sys.exit("backfill already done")
os.environ["AUDIT_BY"] = "backfill"


def mtime(p: Path) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(p.stat().st_mtime))


def load(p: Path):
    if not p.exists():
        return []
    if p.suffix == ".jsonl":
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    d = json.loads(p.read_text())
    return d if isinstance(d, list) else d


n = 0
# Bible references (jev_cite_correct pass 1)
p = OUT / "jev-correct-20261002-pass1.jsonl"
for r in load(p):
    if r.get("applied"):
        verb = "duplicate reference removed" if r.get("op") == "dedupe" else f"{r.get('display')} -> {r.get('proposed')}"
        A.record(r["book"], "citation", f"Bible reference corrected: {verb} (section {r['section']})",
                 ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r["section"],
                 old=r.get("display"), new=r.get("proposed"), basis=r.get("basis", "verifier"))
        n += 1
# Manual citation restore in Heraclides
A.record("origen-heraclides-pascha", "citation", "Restored Lamentations 4:20 the correction loop wrongly removed; removed a doubled Jeremiah 1:5 clause (section 27)",
         ref="session 2026-10-02", when="2026-10-02T19:40:00", approx=True, section="27"); n += 1

# Source-checked fused-word repairs
p = OUT / "fused-words-fix-20261002.json"
for r in load(p):
    if r.get("status") == "fixed":
        A.record(r["book"], "repair", f"Fused words repaired from the source: '{r['old'][:60]}' -> '{r['new'][:60]}'",
                 ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r.get("section")); n += 1
# Stutter collapse (first applied pass)
for name in ("stutter-fix-20261002-pass1.json",):
    p = OUT / name
    for r in load(p):
        A.record(A.book_of(r["file"]), "repair", f"Repeated-text damage collapsed in section {r.get('section')}",
                 ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r.get("section")); n += 1
# Agent garble repairs (source-checked)
p = OUT / "garble-applied-20261002.json"
for r in load(p):
    if str(r.get("status", "")).startswith("fixed"):
        A.record(A.book_of(r["file"]), "repair", f"Damaged word repaired from the source: '{r['old'][:50]}' -> '{r['new'][:50]}'",
                 ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r.get("section"),
                 confidence=r.get("confidence", "high")); n += 1
# Residual mechanical repairs
p = OUT / "residual-fix-20261002.json"
for r in load(p):
    A.record(A.book_of(r["file"]), "repair", f"Split possessive / doubled punctuation repaired in section {r.get('section')}",
             ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r.get("section")); n += 1
# Lost-text restore from pre-pass git copy
p = OUT / "span-repair-20261002.json"
for r in load(p):
    A.record(A.book_of(r["file"]), "repair", f"Lost words restored from the pre-damage text in section {r.get('section')}",
             ref=str(p.relative_to(ROOT)), when=mtime(p), approx=True, section=r.get("section")); n += 1
# Hand repairs this session
for book, summary in [
    ("hesychius-in-conceptionem-praecursoris", "Restored a lost sentence on Luke 1:13 from the Greek (section u01-rem-early)"),
    ("davenant-dissertationes-duae", "Restored 'from the mere good pleasure of his will, and not from foreknowledge of merits' from the Latin (Rat. 12)"),
    ("evagrius-capitula-xxxiii", "Meaning fixed: 'lacking virtues' -> 'supported by virtues' (Greek epereidomenos aretais, ch. 20)"),
    ("origen-job-homilies", "Restored the numbers of Job's years (78, 156, 14, 170, 248) from the Greek (u03-rem-close)"),
    ("didymus-commentarii-zacchariam", "Restored 'being men who watch for wonders, that I call my servant East' from the Greek (u06-rem-early)"),
]:
    A.record(book, "repair", summary, ref="session 2026-10-02", when="2026-10-02T19:20:00", approx=True); n += 1
A.record("eustathius-engastrimytho", "title", "Public title: 'On the Belly-Speaker against Origen' -> 'On the Witch of Endor, Against Origen' (Greer & Mitchell; New Advent)",
         ref="websites/fathers.saneapps.com scripts/build_site.py", when="2026-10-02T20:12:00", approx=True); n += 1
# Re-certification queue results so far
p = OUT / "work-pipeline" / "queue.json"
for book, r in (json.loads(p.read_text()) if p.exists() else {}).items():
    if r.get("result") in ("certified", "held"):
        st = r.get("status") or {}
        A.record(book, r["result"], f"Re-certification {r['result']}: sections {st.get('sections')}, readers {st.get('followability')}, intro ok {st.get('intro_ok')}",
                 ref="outputs/work-pipeline/queue.json", when=r.get("at", mtime(p)), minutes=r.get("minutes")); n += 1
marker.parent.mkdir(parents=True, exist_ok=True)
marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%S"))
print("backfilled", n, "events")
