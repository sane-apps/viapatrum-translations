#!/usr/bin/env python3
"""Apply the corrections that survived the skeptics in released-14-check.json
(owner-approved 'fix now + recheck', 2026-10-06), then send each touched
section back through the pipeline's source check: the staged section becomes
a hold whose notes are the verified errors, and the book is reopened so a lane
redrafts it with those notes, runs the blind two-model check, and re-certifies.

The corrected wording goes into books/*/translations now so the site never
shows the known error again; the lane's redraft replaces it on certification.
Books a live lane is running are skipped (its apply() would overwrite the edit).
Usage: apply_released_check.py [--apply]
"""
import json, os, re, shutil, sys
from collections import defaultdict
from pathlib import Path

T = Path.home() / "SaneApps/clients/translations"
sys.path.insert(0, str(T / "scripts"))
os.chdir(T)
import work_pipeline as W  # noqa: E402
import held_review as H  # noqa: E402

APPLY = "--apply" in sys.argv
OUT = Path(__file__).resolve().parent
data = json.loads((OUT / "released-14-check.json").read_text())
rows = json.loads(W.QUEUE_LOG.read_text())


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


running = {b for b, r in rows.items() if r.get("result") == "running" and alive(r.get("pid", 0))}
by_book = defaultdict(list)
for e in data["kept"]:
    by_book[e["slug"]].append(e)

receipt = {"apply": APPLY, "applied": [], "skipped": [], "books_reopened": []}
for book, errs in sorted(by_book.items()):
    if book in running:
        receipt["skipped"] += [{"book": book, "section": e["section"], "why": "lane running"} for e in errs]
        continue
    files = {}  # eng_file -> parsed json
    sec_rows = {}  # section id -> (eng_file, row)
    for f in sorted((T / "books" / book / "translations").glob("*_english.json")):
        d = json.loads(f.read_text())
        files[f] = d
        for r in (d if isinstance(d, list) else d.get("sections", [])):
            if isinstance(r, dict):
                sec_rows.setdefault(str(r.get("section")), (f, r))
    touched = defaultdict(list)  # section -> findings
    for e in errs:
        v = e.get("verdict") or {}
        new = (v.get("better_correction") or "").strip() if not v.get("correction_ok", True) else ""
        new = new or e["corrected_english"].strip()
        old = e["english_quote"].strip()
        hit = sec_rows.get(str(e["section"]))
        if not hit:
            receipt["skipped"].append({"book": book, "section": e["section"], "why": "section not found"})
            continue
        f, r = hit
        paras = r.get("english") or []
        where = [i for i, p in enumerate(paras) if old in p]
        if len(where) != 1 or paras[where[0]].count(old) != 1:
            receipt["skipped"].append({"book": book, "section": e["section"], "why": f"quote found {sum(p.count(old) for p in paras)}x; section re-held with the note, text left to the lane", "quote": old[:80]})
            touched[str(e["section"])].append({"class": e.get("kind", "error"), "quote": old, "source_quote": e.get("source_quote", ""),
                                               "why": e.get("why", "") + " Suggested: " + new})
            continue
        paras[where[0]] = paras[where[0]].replace(old, new)
        touched[str(e["section"])].append({"class": e.get("kind", "error"), "quote": old, "source_quote": e.get("source_quote", ""),
                                           "why": e.get("why", "")})
        receipt["applied"].append({"book": book, "section": e["section"], "severity": e["severity"], "old": old[:120], "new": new[:120]})
    if not touched:
        continue
    if APPLY:
        for f, d in files.items():
            raw = f.read_text()
            indent = 1 if raw.startswith("[\n {") or raw.startswith("{\n \"") else 2
            text = json.dumps(d, indent=indent, ensure_ascii=False) + ("\n" if raw.endswith("\n") else "")
            if text != raw:
                shutil.copy2(f, OUT / f"{book}__{f.name}.before-released-check")
                f.write_text(text)
    pairs = {str(p["id"]): p for p in W.load_pairs(book)}
    for sid, findings in touched.items():
        p = pairs.get(sid)
        if not p:
            continue
        sf = W.STAGE / book / "sections" / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', sid)}.json"
        j = json.loads(sf.read_text()) if sf.exists() else {"section": sid}
        prior = [x for x in (j.get("open_findings") or []) if isinstance(x, dict)] if j.get("_status") == "hold" else []
        new_j = {**j, "section": sid, "_status": "hold", "pass_b_english": p["english"],
                 "_why": "owner-approved correction (released-works check 2026-10-06): recheck this section against the source",
                 "open_findings": (prior + findings)[:13], "confidence": "held"}
        if APPLY:
            if sf.exists():
                shutil.copy2(sf, OUT / f"{book}__{sf.name}.before-released-check")
            sf.parent.mkdir(parents=True, exist_ok=True)
            sf.write_text(json.dumps(new_j, indent=1, ensure_ascii=False))
            tries = sf.with_suffix(".retries")
            if tries.exists():
                tries.unlink()
    receipt["books_reopened"].append(book)
if APPLY:
    H.reopen(receipt["books_reopened"])
(OUT / ("released-check-receipt.json" if APPLY else "released-check-dry.json")).write_text(json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"applied": len(receipt["applied"]), "skipped": len(receipt["skipped"]), "books": len(receipt["books_reopened"]),
                  "running": sorted(running & set(by_book))}))
for s in receipt["skipped"][:30]:
    print("  skip", s)
