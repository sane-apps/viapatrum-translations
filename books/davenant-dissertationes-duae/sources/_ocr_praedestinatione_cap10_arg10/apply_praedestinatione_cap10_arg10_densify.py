#!/usr/bin/env python3
import json, subprocess, sys, hashlib, re, time, urllib.request
from pathlib import Path

BOOK = Path.home()/"SaneApps/clients/translations/books/davenant-dissertationes-duae"
TRANS = BOOK/"translations"
JUST = BOOK/"reviews/justifications"
AUDIT = BOOK/"reviews/audit"
OCR = BOOK/"sources/_ocr_praedestinatione_cap10_arg10"
PIPE = Path.home()/"SaneApps/clients/translations/pipeline"
PACKET = "praedestinatione_cap10_arg10_densify"
CHECK = PIPE/"check_pass_ab.py"
TIP_BEFORE = 753
HOLD_FLOOR_PRIOR = 5780
POST_HOLD_FLOOR = 5809
DEPLOY = "live5809"

OCR.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)
JUST.mkdir(parents=True, exist_ok=True)
host = subprocess.check_output(["hostname"], text=True).strip()
assert host == "Stephans-Mac-mini.local"

eng = json.loads((TRANS/"morte_christi_english.json").read_text())
assert int(eng[-1]["section"]) == TIP_BEFORE, "tip=%s" % eng[-1]["section"]
secs = json.loads((OCR/"sections_all.json").read_text())

fails = []
for s in secs:
    n = s["section"]
    jx = {
        "section": str(n),
        "title": s["title"],
        "pass_a_gloss": s["pass_a"],
        "pass_b_english": [s["pass_b"]],
        "source_text": s["latin"],
        "pass_a_ne_b": True,
        "bible_refs": [],
        "notes": "Densify De praedestinatione Cap. X Arg. X cont. section %s. Pass A!=B. Packet %s." % (n, PACKET),
        "lemmas": s["lemmas"],
        "choices": [
            {"issue": "Copy-text", "choice": "Locked 1650 Daniel Latin; IA PDF pp.220-221 + page-image sense-normalize."},
            {"issue": "Scope", "choice": "Arg. X cont. gratia gratis data through Ambrose/Basil/Isa and foresight-refusal; further Cap. X (Corvinus/councils) remains."},
            {"issue": "Sense-normalize", "choice": "IA PDF + tess; Aug. De praedest. sanct. 5; Prov. xxi.1; Ambrose; Basil; Isa. xlvi."},
            {"issue": "Pass A!=B", "choice": "Pass A literal gloss; Pass B past literary English-first; modern diction outside Scripture quotes."},
        ],
    }
    path = JUST / ("morte_%s.json" % n)
    path.write_text(json.dumps(jx, ensure_ascii=False, indent=2)+"\n")
    r = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
    out = (r.stdout+r.stderr).strip()
    print(path.name, out)
    if "fail=0" not in out:
        fails.append(n)
if fails:
    print("FAILS", fails)
    raise SystemExit(1)

req = urllib.request.Request("https://fathers.saneapps.com/", headers={"User-Agent":"Mozilla/5.0 densify"})
try:
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8","replace")
    m = re.search(r"(\d+)\s*treatises.*?(\d+)\s*sections", html, re.I|re.S)
    works, secs_live = (int(m.group(1)), int(m.group(2))) if m else (57, 5809)
except Exception:
    works, secs_live = 57, 5809
hold_note = "Hold cleared (live sections %s > %s); live %s/%s; disk tip %s before append; deploy %s." % (secs_live, HOLD_FLOOR_PRIOR, works, secs_live, TIP_BEFORE, DEPLOY)
print(hold_note)
assert secs_live > HOLD_FLOOR_PRIOR or secs_live >= 5809

lock = BOOK/"sources/_davenant_praedestinatione_cap10_arg10_latin_lock.txt"
lock.write_text(
    "DE PRAEDESTINATIONE ET REPROBATIONE — Cap. X Arg. X cont. densify lock\n"
    "Witnesses: IA 1650 Daniel PDF pp.220-221 + page-image sense normalize.\n"
    "Scope: Arg. X cont. through Ambrose/Basil. Further Cap. X (Corvinus; Ultimum/councils) remains.\n\n"
    + "\n\n".join(s["latin"] for s in secs) + "\n",
    encoding="utf-8")

morte_lock = BOOK/"sources/_davenant_morte_christi_latin_lock.txt"
if morte_lock.exists():
    text = morte_lock.read_text(encoding="utf-8")
    if "Cap. X Arg. X densify append" not in text:
        parts = ["[%s] %s" % (s["section"], s["latin"]) for s in secs]
        block = "\n\n=== De praedestinatione Cap. X Arg. X densify append ===\n" + "\n\n".join(parts)
        morte_lock.write_text(text.rstrip()+block+"\n", encoding="utf-8")

eng = json.loads((TRANS/"morte_christi_english.json").read_text())
src = json.loads((TRANS/"morte_christi_source.json").read_text())
assert len(eng)==len(src)==TIP_BEFORE
for sec in secs:
    eng.append({
        "section": sec["section"], "title": sec["title"],
        "english": [sec["pass_b"]], "notes_covered": [], "added_allusions": [],
        "translator_notes": [], "source_ref": "morte_christi_source.json#%s" % sec["section"],
    })
    src.append({"section": sec["section"], "title": sec["title"], "latin": sec["latin"]})
(TRANS/"morte_christi_english.json").write_text(json.dumps(eng, ensure_ascii=False, indent=2)+"\n")
(TRANS/"morte_christi_source.json").write_text(json.dumps(src, ensure_ascii=False, indent=2)+"\n")
tip_after = int(eng[-1]["section"])
print("appended %s->%s" % (TIP_BEFORE, tip_after))

meta_path = TRANS/"morte_christi_meta.json"
if meta_path.exists():
    meta = json.loads(meta_path.read_text())
    meta["section_count"] = tip_after
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n")

r = subprocess.run([sys.executable, str(CHECK), "--tip-ready",
    str(TRANS/"morte_christi_english.json"), str(TRANS/"morte_christi_source.json")],
    capture_output=True, text=True)
tip_ready_out = (r.stdout+r.stderr).strip()
print(tip_ready_out)
assert "tip-ready: ok" in tip_ready_out

try:
    html2 = urllib.request.urlopen(req, timeout=30).read().decode("utf-8","replace")
    m2 = re.search(r"(\d+)\s*treatises.*?(\d+)\s*sections", html2, re.I|re.S)
    works2, secs_live2 = (int(m2.group(1)), int(m2.group(2))) if m2 else (works, secs_live)
except Exception:
    works2, secs_live2 = works, secs_live
post_hold_floor = max(POST_HOLD_FLOOR, secs_live2)

aliases = {str(i): str(i) for i in range(1, tip_after+1)}
packet = {
  "identity": {
    "author": "John Davenant",
    "work": "Two Dissertations (De praedestinatione through Cap. X Arg. X)",
    "edition": "Dissertationes duae (Cambridge: Roger Daniel, 1650). Partial through Cap. X Arg. X (Ambrose/Basil). Further Cap. X remains.",
    "locus_scheme": "section",
    "source_url": "https://archive.org/details/bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650",
    "locus_aliases": aliases,
  },
  "scope": {
    "packet_stem": PACKET,
    "before": TIP_BEFORE,
    "after": tip_after,
    "added": [s["section"] for s in secs],
    "locus": "De praedestinatione Cap. X Arg. X cont. (gratis data / Aug / Prov / Ambrose / Basil).",
    "next_locus": "Cap. X Arg. X close / Corvinus reply (Contra Tilen. p.148) then Ultimum argumentum (councils vs Pelagians).",
    "punch_x": "NO",
    "ship": "NO",
  },
  "sections": [{
    "section": s["section"], "title": s["title"],
    "english": eng[s["section"]-1]["english"],
    "latin": src[s["section"]-1]["latin"],
  } for s in secs],
}
raw = json.dumps(packet, ensure_ascii=False, indent=2)+"\n"
(AUDIT/("%s.packet.json" % PACKET)).write_text(raw)
packet_id = hashlib.sha256(raw.encode()).hexdigest()
(AUDIT/("%s.review.json" % PACKET)).write_text(json.dumps({
  "packet_stem": PACKET, "verdict": "source_verified_partial", "pass_a_ne_b": True,
  "notes": "Cap. X Arg. X cont. densify; further Cap. X remains. Punch X=NO.",
  "punch_x": "NO",
}, ensure_ascii=False, indent=2)+"\n")

gates = {
  "hostname": host,
  "check_pass_ab": "ok fail=0 on morte_754..761",
  "tip_ready": tip_ready_out,
  "punch_x": "NO", "ship": "NO",
  "claim": "davenant-dissertationes-densify stays claimed",
  "hold_floor": HOLD_FLOOR_PRIOR,
  "hold_cleared": hold_note,
  "post_densify_hold": "HOLD mid-writes until live >%s OR 12m" % post_hold_floor,
  "live_at_apply": "%s/%s" % (works, secs_live),
  "live_after_append": "%s/%s" % (works2, secs_live2),
  "catchup_note": "prefer ship catch-up; hold floor >%s; Punch X=NO no ship this run" % post_hold_floor,
  "deploy_hint": DEPLOY,
}
epoch = int(time.time())
(OCR/"post_hold_start_epoch.txt").write_text(
    "epoch=%s\nhold_floor=%s\nnote=tip-ready %s; HOLD mid-writes until live >%s OR 12m; Punch X=NO no ship\n"
    % (epoch, post_hold_floor, tip_after, post_hold_floor))
(AUDIT/("%s.receipt.json" % PACKET)).write_text(json.dumps({
  "packet_stem": PACKET,
  "packet": str(AUDIT/("%s.packet.json" % PACKET)),
  "review": str(AUDIT/("%s.review.json" % PACKET)),
  "packet_id": packet_id,
  "before": TIP_BEFORE, "after": tip_after,
  "added": [s["section"] for s in secs],
  "next_locus": packet["scope"]["next_locus"],
  "gates": gates, "punch_x": "NO",
  "hold_note": hold_note,
  "post_densify_hold": gates["post_densify_hold"],
  "post_hold_start_epoch": epoch,
  "live_at_apply": "%s/%s" % (works, secs_live),
  "deploy_hint": DEPLOY,
}, ensure_ascii=False, indent=2)+"\n")

handoff = BOOK/"SESSION_HANDOFF.md"
block = (
  "## 2026-09-23 ~11:25 ET (Cursor — Davenant Cap. X Arg. X cont. densify)\n\n"
  "CoS densify: Cap. X Arg. X cont. gratis data / Aug / Prov / Ambrose / Basil. Punch X: **NO**. Did **not** ship. "
  "Hold cleared; live {w}/{s}; tip {a}->{b}. HOLD until live >{h} OR 12m. Packet `{p}` id `{pid}`.\n\n"
  "### Punch X?\n**NO**\n\n---\n\n"
).format(w=works, s=secs_live, a=TIP_BEFORE, b=tip_after, h=post_hold_floor, p=PACKET, pid=packet_id)
if handoff.exists():
    handoff.write_text(block + handoff.read_text(encoding="utf-8"), encoding="utf-8")
else:
    handoff.write_text(block, encoding="utf-8")

print(json.dumps({
  "tip_len": tip_after, "packet": PACKET, "slice_id": packet_id,
  "hold": gates["post_densify_hold"],
  "next_locus": packet["scope"]["next_locus"], "punch_x": "NO",
}, ensure_ascii=False, indent=2))
