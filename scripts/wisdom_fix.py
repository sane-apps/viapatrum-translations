"""'Wisdom N:N' -> 'Wisdom of Solomon N:N' across the English texts (owner 2026-10-03).

Only the book used as a citation (followed by chapter:verse or chapter.verse);
wisdom the virtue and personified Wisdom are untouched. Inside [[display >> Bible:...]]
only the display part changes. Dry run unless --apply. Logs each work to the audit log.
"""
import glob, json, re, sys
from pathlib import Path

ROOT = Path.home() / "SaneApps/clients/translations"
sys.path.insert(0, str(ROOT / "scripts"))
APPLY = "--apply" in sys.argv
CITE = re.compile(r"\bWisdom(?! of Solomon)(?=\s+\d+[:.]\d+)")

changed = {}
samples = []
for f in sorted(glob.glob(str(ROOT / "books/*/translations/*_english.json"))):
    path = Path(f)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        continue
    rows = data if isinstance(data, list) else data.get("sections", [])
    n = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        paras = row.get("english") or []
        for i, para in enumerate(paras):
            if not isinstance(para, str) or "Wisdom" not in para:
                continue
            # leave link targets (after '>>') alone; fix display text and plain prose
            parts = re.split(r"(>>[^\]]*\]\])", para)
            new = "".join(p if p.startswith(">>") else CITE.sub("Wisdom of Solomon", p) for p in parts)
            if new != para:
                k = CITE.findall("".join(p for p in parts if not p.startswith(">>")))
                n += len(k)
                if len(samples) < 6:
                    m = re.search(r"Wisdom of Solomon\s+\d+[:.]\d+", new)
                    samples.append(new[max(0, m.start() - 40):m.end() + 10] if m else new[:80])
                paras[i] = new
    if n:
        changed[f] = n
        if APPLY:
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.rename(path)

print(f"{sum(changed.values())} citations in {len(changed)} files; apply={APPLY}")
for s in samples:
    print("  ", s)
if APPLY:
    import audit_log
    by_book = {}
    for f, n in changed.items():
        b = audit_log.book_of(f)
        by_book[b] = by_book.get(b, 0) + n
    for b, n in by_book.items():
        audit_log.record(b, "citation", f"Book name written in full: 'Wisdom' -> 'Wisdom of Solomon' in {n} citation(s)",
                         ref="owner rule 2026-10-03")
