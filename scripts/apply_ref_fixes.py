#!/usr/bin/env python3
"""Apply judged Bible-reference fixes to the English at source (Nov 8, 2026).

Input: a JSONL of decisions, one per printed reference, from the reference sweep
(~/SaneApps/outputs/viapatrum/references-20261108/):
  {"work", "section", "sentence", "printed", "action": "replace"|"remove", "new_ref": "Psalm 79:8"|null, "why"}
For each decision it finds the section's English file (books/<book>/translations/*_english.json), finds the sentence
and the printed reference in it, and swaps or removes that reference only. Every change is checked citation-only and
recorded in books/<book>/reviews/citation_amendments.jsonl (so certified works stay certified), mirrored in that
section's added_allusions, and logged to the per-work audit log.
Skips: a section under an active claim (docs/CLAIMS.md), a book a work_pipeline lane is running, a sentence or
reference it cannot find exactly once. Dry run unless --apply. Writes a receipt JSONL of every decision's outcome.

Usage: python3 scripts/apply_ref_fixes.py --decisions PATH --out RECEIPTS.jsonl [--apply] [--books a,b]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOKS = ROOT / "books"
sys.path.insert(0, str(HERE))
import citation_amendments as CA  # noqa: E402

SITE = Path.home() / "SaneApps/websites/viapatrum.org/scripts"
TOOL = "scripts/apply_ref_fixes.py (reference sweep 2026-11-08)"

ABBR = {"ps": "psalm", "pss": "psalm", "psalms": "psalm", "matt": "matthew", "mt": "matthew", "mk": "mark",
        "lk": "luke", "jn": "john", "gen": "genesis", "exod": "exodus", "ex": "exodus", "lev": "leviticus",
        "num": "numbers", "deut": "deuteronomy", "isa": "isaiah", "jer": "jeremiah", "ezek": "ezekiel",
        "dan": "daniel", "rom": "romans", "cor": "corinthians", "heb": "hebrews", "rev": "revelation",
        "prov": "proverbs", "eccl": "ecclesiastes", "sir": "sirach", "wis": "wisdom", "zech": "zechariah",
        "mal": "malachi", "hos": "hosea", "gal": "galatians", "eph": "ephesians", "phil": "philippians",
        "col": "colossians", "thess": "thessalonians", "tim": "timothy", "pet": "peter", "jas": "james",
        "josh": "joshua", "judg": "judges", "sam": "samuel", "kgs": "kings", "chr": "chronicles"}


def norm_ref(r: str) -> str:
    r = (r or "").strip().lower().replace("–", "-").replace(".", "")
    words = r.split()
    words = [ABBR.get(w, w) for w in words]
    return " ".join(words)


def work_book_dir(slug: str) -> Path | None:
    if (BOOKS / slug).is_dir():
        return BOOKS / slug
    try:
        sys.path.insert(0, str(SITE))
        import build_site as B  # noqa: E402
        name = B.work_book(slug)
    except Exception:
        name = None
    return BOOKS / name if name and (BOOKS / name).is_dir() else None


def active_claims() -> set[tuple[str, str]]:
    out = set()
    path = ROOT / "docs/CLAIMS.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.search(r"\| (claimed|checking|review|drafting) \|", line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4:
                out.add((cells[2], cells[3] if not cells[3].lower().startswith("full work") else "*"))
    return out


def running_books() -> set[str]:
    try:
        q = json.loads((ROOT / "outputs/work-pipeline/queue.json").read_text())
    except Exception:
        return set()
    rows = q.items() if isinstance(q, dict) else enumerate(q)
    return {str(k if isinstance(k, str) else r.get("book")) for k, r in rows
            if isinstance(r, dict) and r.get("result") == "running"}


def strip_markup(text: str) -> str:
    try:
        sys.path.insert(0, str(SITE))
        import build_site as B  # noqa: E402
        return B.strip_logos_markup(text)
    except Exception:
        return re.sub(r"\[\[(.*?)\s*>>\s*[^\]]*\]\]", r"\1", text)


def ship_running(lock: Path = Path.home() / "SaneApps/websites/viapatrum.org/outputs/ship.lock") -> bool:
    """True while a site ship holds its lock. Writing the English mid-ship made the ship's own reference ratchet
    read half-applied files and fail (2026-11-08 12:16 PM)."""
    import fcntl
    import os
    if not lock.exists():
        return False
    fd = os.open(lock, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    finally:
        os.close(fd)


def dump_like(orig: str, data) -> str:
    """Serialise data in the file's own JSON style (indent, ASCII escaping, final newline) so the diff is the change."""
    parsed = json.loads(orig)
    end = "\n" if orig.endswith("\n") else ""
    for indent in (1, 2, 4, None, 3):
        for asc in (False, True):
            if json.dumps(parsed, ensure_ascii=asc, indent=indent) + end == orig:
                return json.dumps(data, ensure_ascii=asc, indent=indent) + end
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def new_para(para: str, sentence: str, printed: str, action: str, new_ref: str | None, times: int = 1) -> str | None:
    """The paragraph with the reference changed, or None when it can't be placed exactly."""
    if para.count(sentence) != 1 and strip_markup(para).count(sentence) != 1:
        return None
    if para.count(sentence) == 1:
        s0 = para.index(sentence)
        seg = para[s0:s0 + len(sentence)]
    else:  # the sentence carries Logos markup in the file: place by the words just before the reference
        st = strip_markup(para)
        i0 = st.index(sentence)
        j = sentence.find(printed)
        if j < 0 or sentence.count(printed) != times:
            return None
        ctx = sentence[max(0, j - 30):j + len(printed)]
        if para.count(ctx) != 1:
            return None
        s0 = para.index(ctx)
        seg = ctx
    if seg.count(printed) != times:
        return None
    i = seg.rindex(printed)
    if action == "replace" and times > 1:  # every occurrence judged, all to the same reference
        seg2 = re.sub(re.escape(printed) + r"(?![\w:])", lambda _m: new_ref, seg)
        if seg2.count(new_ref) - seg.count(new_ref) != times:
            return None
    elif action == "replace":
        seg2 = seg[:i] + new_ref + seg[i + len(printed):]
    else:
        seg2 = seg[:i] + seg[i + len(printed):]
        seg2 = re.sub(r"\(\s*[;,]\s*", "(", seg2)
        seg2 = re.sub(r"\s*[;,]\s*\)", ")", seg2)
        seg2 = re.sub(r"\s*\(\s*\)", "", seg2)
        seg2 = re.sub(r" {2,}", " ", seg2)
    return para[:s0] + seg2 + para[s0 + len(seg):]


def section_rows(book_dir: Path, sid: str):
    for ef in sorted((book_dir / "translations").glob("*_english.json")):
        try:
            data = json.loads(ef.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("sections", [])
        for row in rows:
            if isinstance(row, dict) and str(row.get("section")) == sid:
                yield ef, data, row


_INDEX: dict | None = None


def find_by_sentence(sentence: str):
    """(book dir, section id) of the one English row whose text holds this exact sentence, else None.
    For site works whose loader names them differently from their folder (Cyril, Julian, Origen batches)."""
    global _INDEX
    if _INDEX is None:
        _INDEX = []
        for ef in BOOKS.glob("*/translations/*_english.json"):
            try:
                data = json.loads(ef.read_text(encoding="utf-8"))
            except Exception:
                continue
            rows = data if isinstance(data, list) else data.get("sections", [])
            for row in rows:
                if isinstance(row, dict) and isinstance(row.get("english"), list):
                    _INDEX.append((ef.parents[1], str(row.get("section")), strip_markup("\n".join(map(str, row["english"])))))
    hits = {(b, s) for b, s, txt in _INDEX if sentence in txt}
    return hits.pop() if len(hits) == 1 else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--books", default="")
    a = ap.parse_args(argv)
    if a.apply and ship_running():
        print("refusing: a viapatrum.org ship is running (outputs/ship.lock held); its gates read these files. "
              "Wait for it to finish.")
        return 2
    only = set(filter(None, a.books.split(",")))
    decisions = [json.loads(l) for l in Path(a.decisions).read_text().splitlines() if l.strip()]
    claims, running = active_claims(), running_books()
    # Resolve each decision to its folder and section on its own: a site slug can name a folder differently
    # (cyril-adoration-6 lives in cyril-alexandria-adoration-1), and one section's decisions may not all share
    # the first one's sentence.
    by_sec = defaultdict(list)
    dir_cache: dict[str, Path | None] = {}
    for d in decisions:
        work, sid = d["work"], str(d["section"])
        if work not in dir_cache:
            dir_cache[work] = work_book_dir(work)
        bdir = dir_cache[work]
        if bdir is None or len(list(section_rows(bdir, sid))) != 1:
            alt = find_by_sentence(d["sentence"])
            if alt:
                bdir, sid = alt
        by_sec[(str(bdir) if bdir else "", sid, work)].append(d)
    outcome, receipts = Counter(), []
    for (bkey, sid, work), ds in by_sec.items():
        bdir = Path(bkey) if bkey else None
        def done(d, result, **kw):
            for x in [d] + list(d.get("_with", [])):
                outcome[result] += 1
                receipts.append({**{k: v for k, v in x.items() if not k.startswith("_")}, "result": result, **kw})
        if bdir is None:
            for d in ds:
                done(d, "skip-no-book-folder")
            continue
        if only and bdir.name not in only:
            continue
        if bdir.name in running or (bdir.name, sid) in claims or (bdir.name, "*") in claims:
            for d in ds:
                done(d, "skip-busy", book=bdir.name)
            continue
        found = list(section_rows(bdir, sid))
        if len(found) > 1:  # section ids repeat across slices: keep the row that holds the sentence
            found = [f for f in found if any(d["sentence"] in strip_markup("\n".join(map(str, f[2].get("english") or [])))
                                             for d in ds)]
        if len(found) != 1:
            for d in ds:
                done(d, f"skip-section-rows-{len(found)}", book=bdir.name)
            continue
        ef, data, row = found[0]
        before = list(row.get("english") or [])
        paras = list(before)
        applied = []
        # The same printed reference judged at every place it occurs in a sentence, all to one new reference:
        # apply them together (one decision carries them; the others are marked applied with it).
        same = defaultdict(list)
        for d in ds:
            same[(d["sentence"], d["printed"])].append(d)
        merged = []
        for (sent, pr), group in same.items():
            if (len(group) > 1 and sent.count(pr) == len(group) and len({g["action"] for g in group}) == 1
                    and group[0]["action"] == "replace" and len({g.get("new_ref") for g in group}) == 1):
                group[0]["_times"] = len(group)
                group[0]["_with"] = group[1:]
                merged.append(group[0])
            else:
                merged.extend(group)
        ds = merged
        for d in ds:
            t = d.get("_times", 1)
            hits = [k for k, p in enumerate(paras) if new_para(p, d["sentence"], d["printed"], d["action"], d.get("new_ref"), t)]
            if len(hits) != 1:
                done(d, "skip-not-placed", book=bdir.name, hits=len(hits))
                continue
            k = hits[0]
            cand = new_para(paras[k], d["sentence"], d["printed"], d["action"], d.get("new_ref"), t)
            if not CA.citation_only([paras[k]], [cand]):  # judge each fix alone; one bad fix must not block the rest
                done(d, "skip-not-citation-only", book=bdir.name)
                continue
            paras[k] = cand
            applied.append(d)
            # Later fixes in the same sentence must look for the sentence as it now reads.
            s_new = new_para(d["sentence"], d["sentence"], d["printed"], d["action"], d.get("new_ref"), t)
            if s_new:
                for d2 in ds:
                    if d2 is not d and d2 not in applied and d2["sentence"] == d["sentence"]:
                        d2["sentence"] = s_new
        if not applied:
            continue
        if not CA.citation_only(before, paras):
            for d in applied:
                done(d, "skip-not-citation-only", book=bdir.name)
            continue
        if a.apply:
            row["english"] = paras
            al = row.get("added_allusions")
            if isinstance(al, list):
                for d in applied:
                    old = norm_ref(d["printed"])
                    for x in list(al):
                        if isinstance(x, dict) and norm_ref(x.get("reference", "")) == old:
                            if d["action"] == "replace":
                                x["reference"] = d["new_ref"]
                            else:
                                al.remove(x)
            tmp = ef.with_suffix(".json.tmp")
            tmp.write_text(dump_like(ef.read_text(encoding="utf-8"), data), encoding="utf-8")
            tmp.rename(ef)
            why = "; ".join(f'{d["printed"]} -> {d.get("new_ref") or "removed"}' for d in applied)
            CA.record(bdir, sid, before, paras, tool=TOOL, why=why[:900])
            try:
                import audit_log
                audit_log.record(bdir.name, "citation", f"Bible references corrected (reference sweep 2026-11-08): {why}"[:400],
                                 ref="scripts/apply_ref_fixes.py", section=sid)
            except Exception:
                pass
        for d in applied:
            done(d, "applied" if a.apply else "would-apply", book=bdir.name, file=str(ef.relative_to(ROOT)))
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in receipts))
    print(("APPLIED" if a.apply else "DRY RUN"), dict(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
