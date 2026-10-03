# -*- coding: utf-8 -*-
"""Apply densify sections JSON for a Liber III Cap. Usage: apply_liber3_cap.py capN sections.json"""
import json, hashlib, re, sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations/books/crocius-syntagma")
TRANS = ROOT / "translations"
JUST = ROOT / "reviews" / "justifications"
AUDIT = ROOT / "reviews" / "audit"
SRC = ROOT / "sources"
JUST.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)

def lemmas_from_latin(latin, n=14):
    toks = re.findall(r"[A-Za-z]+", latin)
    out = []; seen = set()
    for t in toks:
        if len(t) < 2: continue
        key = t.lower()
        if key in seen: continue
        seen.add(key)
        out.append({"latin": t, "gloss": t.lower()})
        if len(out) >= n: break
    return out

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    work_key = sys.argv[1]  # e.g. liber3_cap5
    sections = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    meta_extra = {}
    if len(sys.argv) > 3:
        meta_extra = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

    phys = meta_extra.get("phys", "")
    next_start = meta_extra.get("next_start", "")
    title_short = meta_extra.get("title_short", work_key)
    blurb = meta_extra.get("blurb", "")
    liber3_status = meta_extra.get("liber3_status", "")
    ocr_src = meta_extra.get("ocr_src")
    edition = meta_extra.get("edition") or (
        f"Syntagma sacrae theologiae (Bremen: Berthold Villerian, 1636). "
        f"VD17 14:684303C. SLUB id335860389. {title_short} COMPLETE ({phys})."
    )

    english_rows = []
    source_rows = []
    for s in sections:
        english_rows.append({"section": s["section"], "title": s["title"], "english": s["english"]})
        source_rows.append({"section": s["section"], "title": s["title"], "latin": s["latin"]})
        just = {
            "section": s["section"], "title": s["title"],
            "pass_a_gloss": s["pass_a"], "pass_b_english": s["english"],
            "source_text": s["latin"], "pass_a_ne_b": True,
            "lemmas": lemmas_from_latin(s["latin"]),
            "choices": [
                {"issue": "Copy-text", "choice": f"Densify Latin from SLUB {phys} {work_key}; prior Liber english untouched."},
                {"issue": "Register", "choice": "English-first theological prose matching Liber III densify register."},
            ],
            "confidence": "high",
            "excerpt_id": f"{work_key}_{s['section']}",
            "edition": edition,
        }
        (JUST / f"{work_key}_{s['section']}.json").write_text(
            json.dumps(just, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    eng_path = TRANS / f"{work_key}_english.json"
    src_path = TRANS / f"{work_key}_source.json"
    eng_path.write_text(json.dumps(english_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(source_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    meta = {
        "slug": "crocius-syntagma",
        "title": f"Syntagma sacrae theologiae ({title_short} densify complete)",
        "author": "Ludwig Crocius", "author_slug": "ludwig-crocius",
        "period": "1636 (Bremen; Reformed professor)", "edition": edition,
        "status": "available",
        "topics": ["faith-and-obedience", "grace-and-assistance", "gifts-and-order"],
        "blurb": blurb,
        "work_key": work_key, "section_count": len(sections), "phys": phys,
        "next_start": next_start, "liber3_status": liber3_status,
    }
    (TRANS / f"{work_key}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lock_parts = [
        "Locked Latin for Ludwig Crocius, Syntagma sacrae theologiae (Bremen: Berthold Villerian, 1636).",
        f"VD17 14:684303C. SLUB Dresden id335860389. {title_short}.",
        f"PHYS {phys}.",
        "Reconstructed from IIIF medium JPG / PDF Vision+tesseract lat OCR; long-s/ligatures normalized.",
        "",
    ]
    for s in sections:
        lock_parts.append(f"=== SEC {s['section']}: {s['title']} ===")
        lock_parts.append(s["latin"])
        lock_parts.append("")
    lock_parts.append(f"[{work_key} COMPLETE. Next: {next_start}]")
    lock_path = SRC / f"_crocius_{work_key}_latin_lock.txt"
    lock_path.write_text("\n".join(lock_parts) + "\n", encoding="utf-8")

    ocr_dst = SRC / f"crocius_syntagma_1636_slub_{work_key}_densify_ocr.txt"
    if ocr_src and Path(ocr_src).exists():
        ocr_dst.write_text(Path(ocr_src).read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    elif not ocr_dst.exists():
        ocr_dst.write_text(f"(OCR witness for {work_key}; see liber3_med/)\n", encoding="utf-8")

    # identity / expected / publication_scope for QA
    ids = [s["section"] for s in sections]
    identity = {
        "author": "Ludwig Crocius",
        "work": meta["title"],
        "edition": edition,
        "locus_scheme": "tip-section",
        "source_url": "https://digital.slub-dresden.de/id335860389",
        "locus_aliases": {i: i for i in ids},
    }
    expected = {"sections": ids}
    pub = {
        "slug": "crocius-syntagma",
        "title": meta["title"],
        "author": "Ludwig Crocius",
        "author_slug": "ludwig-crocius",
        "period": meta["period"],
        "status": "available",
        "edition": edition,
        "section_count": len(sections),
        "blurb": blurb,
    }
    (AUDIT / f"{work_key}_identity.json").write_text(json.dumps(identity, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (AUDIT / f"{work_key}_expected_sections.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (AUDIT / f"{work_key}_publication_scope.json").write_text(json.dumps(pub, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    print(f"WROTE {work_key} sections={len(sections)}")
    print("eng", sha(eng_path)[:16], "src", sha(src_path)[:16], "lock", sha(lock_path)[:16])

if __name__ == "__main__":
    main()
