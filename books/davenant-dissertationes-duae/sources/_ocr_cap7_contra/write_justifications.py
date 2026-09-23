from pathlib import Path
import json, subprocess, sys, re

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
JUST = BOOK / "reviews/justifications"
OCR = BOOK / "sources/_ocr_cap7_contra"
CHECK = Path.home() / "SaneApps/clients/translations/pipeline/check_pass_ab.py"
PACKET = "morte_christi_cap7_contra_densify"
secs = json.loads((OCR / "sections_all.json").read_text(encoding="utf-8"))
JUST.mkdir(parents=True, exist_ok=True)

def jx_ok(out: str, rc: int) -> bool:
    if rc != 0:
        return False
    m = re.search(r"fail=(\d+)", out)
    if m:
        return int(m.group(1)) == 0
    return True

for sec in secs:
    sid = sec["section"]
    path = JUST / f"morte_{sid}.json"
    payload = {
        "section": str(sid),
        "title": sec["title"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": [sec["pass_b"]],
        "source_text": sec["latin"],
        "pass_a_ne_b": True,
        "bible_refs": [],
        "notes": (
            f"Densify Cap. 7 Contra haec omnia section {sid}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+DjVu+lock. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng + DjVu) "
                    "with sense normalize; Cap. 7 Contra lock: "
                    "sources/_davenant_cap7_contra_latin_lock.txt."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Cap. 7 Contra haec omnia Obj. 1-4 through Cap. 7 close (Amen); "
                    "before De praedestinatione."
                ),
            },
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print(f"morte_{sid}: {out}")
    if not jx_ok(out, r.returncode):
        print(f"FAIL section {sid} — stop")
        sys.exit(1)

print("ALL_JX_OK", len(secs))
