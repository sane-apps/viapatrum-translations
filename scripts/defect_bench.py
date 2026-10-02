#!/usr/bin/env python3
"""Seeded-defect benchmark for the translation checks.

Takes clean base works, injects ONE known defect per section (deterministic,
seeded, ground truth recorded), runs the detectors, and scores recall per
defect type. The unmodified base is also run, to measure false positives and
to discard findings that already exist on the base ("novel" catches only).

  python3 scripts/defect_bench.py build
  python3 scripts/defect_bench.py run --detector lint|read|source|all [--models a,b] [--force]
  python3 scripts/defect_bench.py score

Everything is written under outputs/defect-bench/.

Detectors
  lint    pipeline/work_lint.py   lint_work(sections, brief=None) -> [{rule,severity,section,quote,why}]
  read    scripts/work_read.py    whole-work English-only reader (CF models, free)
  source  scripts/work_pipeline.py source_check(sections, brief, models) -> [{class,section,quote,why}]
          (skipped with a note when that function does not exist yet)

Catch rule (conservative). A finding catches defect D when ALL hold:
  1. finding.section equals one of D's sections (term_drift and boundary_cut
     list several);
  2. LOCALIZED: the normalised finding quote shares a run of >=3 consecutive
     words (>=2 if the injected span itself has <3 words) with an injected
     span or its anchor, or one contains the other; for term_drift, a variant
     text equal to an injected variant word also counts;
  3. NOVEL: the same (section, normalised quote) was not already reported on
     the unmodified base.
"typed" recall additionally requires the finding class/rule to be compatible
with the defect type (TYPE_COMPAT). For the source detector, whose quote may
cite the Greek/Latin, a finding of the exact class in the right section also
counts ("class_section" level).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "defect-bench"
BOOKS = ROOT / "books"
SEED = 20261002
BASES = ["origen-job-homilies", "origen-proverbs-fragments", "cyril-alexandria-fragmenta-acta-catholicas"]
VARIANTS_PER_BASE = 2
TYPES = ["term_drift", "ancient_title", "malapropism", "wrong_scripture", "speaker_strip", "garbled",
         "boundary_cut", "archaic", "negation_flip", "agency_swap", "omission", "addition"]
SOURCE_TYPES = {"negation_flip": "negation", "agency_swap": "agency", "omission": "omission", "addition": "addition"}
# which finding classes / lint-rule keywords count as "the right kind of finding"
TYPE_COMPAT = {
    "term_drift": ["term_drift", "drift", "inconsistent", "terminology"],
    "ancient_title": ["unexplained", "ancient", "title", "kingdoms", "book_name"],
    "malapropism": ["suspect_meaning", "garbled", "mistranslation", "malaprop"],
    "wrong_scripture": ["wrong_scripture", "scripture", "citation", "reference"],
    "speaker_strip": ["speaker", "attribution", "quote"],
    "garbled": ["garbled", "suspect_meaning", "gloss"],
    "boundary_cut": ["garbled", "boundary", "truncat", "lowercase", "unpunctuated", "fragment", "cut", "speaker"],
    "archaic": ["archaic", "kj", "thee", "thou"],
    "negation_flip": ["negation", "suspect_meaning", "garbled"],
    "agency_swap": ["agency", "suspect_meaning", "garbled"],
    "omission": ["omission"],
    "addition": ["addition", "unsupported"],
}

# ---------------------------------------------------------------- text utils

def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", norm(s))


def sentences(text: str) -> list[tuple[int, int]]:
    """(start, end) spans of sentences."""
    return [(m.start(), m.end()) for m in re.finditer(r"[^.!?\n]+[.!?]+['\")\]”’]*|[^.!?\n]+$", text)]


def cap_like(src: str, rep: str) -> str:
    return rep[:1].upper() + rep[1:] if src[:1].isupper() else rep


def rng_for(*parts) -> random.Random:
    h = hashlib.sha256(("|".join(map(str, parts)) + str(SEED)).encode()).hexdigest()
    return random.Random(int(h[:12], 16))

# ---------------------------------------------------------------- loading

def load_base(slug: str) -> list[dict]:
    """Ordered [{id,title,text,source}] with the locked Greek/Latin per section."""
    out, seen = [], set()
    for f in sorted(glob.glob(str(BOOKS / slug / "translations" / "*_english.json"))):
        src_file = f.replace("_english.json", "_source.json")
        src = {}
        try:
            for r in json.load(open(src_file)):
                body = r.get("greek") or r.get("latin") or r.get("source_text") or ""
                src[str(r.get("section"))] = "\n".join(body) if isinstance(body, list) else str(body)
        except (OSError, json.JSONDecodeError):
            pass
        for it in json.load(open(f)):
            eng = it.get("english", [])
            txt = "\n".join(eng) if isinstance(eng, list) else str(eng)
            if not txt.strip():
                continue
            sid = str(it.get("section"))
            if sid in seen:
                sid = Path(f).stem.replace("_english", "") + ":" + sid
            seen.add(sid)
            out.append({"id": sid, "title": it.get("title", ""), "text": txt,
                        "source": src.get(str(it.get("section")), "")})
    return out

# ---------------------------------------------------------------- injectors
# Each takes (sections, idx_list_candidates, rng) and tries to inject into the
# first suitable section among candidates. Returns (truth, {idx: new_text}) or None.
# New text of OTHER sections may change only for term_drift / boundary_cut.

SYN = {
    "Savior": ["Redeemer", "Deliverer", "Healer"], "soul": ["spirit", "psyche", "inner self"],
    "righteous": ["just", "upright", "honest"], "church": ["assembly", "congregation", "gathering"],
    "wisdom": ["cleverness", "sophia", "shrewdness"], "sin": ["offense", "misstep", "error"],
    "prophet": ["seer", "soothsayer", "diviner"], "faith": ["trust", "belief", "confidence"],
    "heaven": ["the sky", "the firmament", "the upper air"], "grace": ["favor", "kindness", "charity"],
    "truth": ["accuracy", "fact", "reality"], "kingdom": ["realm", "dominion", "empire"],
    "apostle": ["envoy", "emissary", "messenger"], "devil": ["adversary", "slanderer", "demon"],
    "law": ["rule", "statute", "custom"], "flesh": ["body", "meat", "frame"],
    "Spirit": ["Breath", "Ghost", "Wind"], "Jews": ["Hebrews", "Israelites", "Judeans"],
    "virtue": ["merit", "excellence", "goodness"], "mercy": ["pity", "compassion", "clemency"],
    "temptation": ["trial", "testing", "enticement"], "Scripture": ["the writings", "the text", "the book"],
    "angel": ["messenger", "envoy", "spirit"], "sacrifice": ["offering", "victim", "oblation"],
    "Word": ["Discourse", "Reason", "Speech"], "humility": ["lowliness", "modesty", "meekness"],
    "patience": ["endurance", "forbearance", "tolerance"], "enemy": ["foe", "adversary", "opponent"],
    "wicked": ["evil", "bad", "base"], "poor": ["needy", "destitute", "beggarly"],
}


def inj_term_drift(secs, cands, rng):
    cnt = {}
    for term in SYN:
        pat = re.compile(r"\b" + re.escape(term) + r"s?\b", re.I if term[0].islower() else 0)
        per = [len(pat.findall(secs[i]["text"])) for i in range(len(secs))]
        cnt[term] = (per, pat)
    best = []
    for term, (per, pat) in cnt.items():
        ok = [i for i in cands if per[i] >= 1]
        if len(ok) >= 3 and sum(per) >= 4:
            best.append((sum(per[i] for i in ok), term, ok))
    if not best:
        return None
    best.sort(reverse=True)
    _, term, ok = best[0]
    # pick the best-supported term that the rng prefers among the top 3
    _, term, ok = best[rng.randrange(min(3, len(best)))]
    pat = cnt[term][1]
    chosen = sorted(rng.sample(ok, 3)) if len(ok) > 3 else ok[:3]
    variants = SYN[term][:3]
    new, spans = {}, []
    for k, i in enumerate(chosen):
        var = variants[k]
        t = pat.sub(lambda m: cap_like(m.group(0), var) + ("s" if m.group(0).lower().endswith("s") and not var.startswith("the ") else ""), secs[i]["text"])
        new[i] = t
        spans.append({"section": secs[i]["id"], "original": term, "injected": var})
    return ({"type": "term_drift", "sections": [secs[i]["id"] for i in chosen], "term": term,
             "variants": variants, "spans": spans}, new)


TITLE_INS = ["as we read in the first of Kingdoms", "as Jesus son of Nave did", "as the volume of Kingdoms relates",
             "as the third of Kingdoms shows", "as the Book of the Reigns reports"]


def inj_ancient_title(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = [s for s in sentences(t) if 10 <= len(t[s[0]:s[1]].split()) <= 45]
        if not ss:
            continue
        a, b = ss[rng.randrange(len(ss))]
        sent = t[a:b]
        m = re.search(r"[.!?]+['\")\]”’]*\s*$", sent)
        if not m:
            continue
        ins = TITLE_INS[rng.randrange(len(TITLE_INS))]
        new_sent = sent[:m.start()].rstrip() + ", " + ins + sent[m.start():]
        return ({"type": "ancient_title", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": "", "injected": ins}]},
                {i: t[:a] + new_sent + t[b:]})
    return None


MALAP = {"prophet": "profit", "soul": "sole", "altar": "alter", "peace": "piece", "heart": "hart", "wisdom": "wizardry",
         "mercy": "mercenary", "sacrifice": "sacrilege-dancer", "temple": "temple-dancer", "spirit": "belly-dancer",
         "bread": "bred", "angel": "angle", "judgment": "judgment-cake", "virtue": "virtual", "priest": "priced",
         "prayer": "prayer-rug", "scripture": "scrapture",
         "voice": "vice", "body": "bawdy"}


def inj_malapropism(secs, cands, rng):
    keys = list(MALAP)
    rng.shuffle(keys)
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        for k in keys:
            ms = list(re.finditer(r"\b" + k + r"\b", t))
            ms = [m for m in ms if m.start() > 20]
            if ms:
                m = ms[len(ms) // 2]
                rep = MALAP[k]
                lo, hi = max(0, m.start() - 25), min(len(t), m.end() + 25)
                nt = t[:m.start()] + rep + t[m.end():]
                return ({"type": "malapropism", "sections": [secs[i]["id"]],
                         "spans": [{"section": secs[i]["id"], "original": k, "injected": rep,
                                    "context": nt[lo:hi + len(rep) - len(k)]}]}, {i: nt})
    return None


WRONG_SCRIP = [("Isaiah 40:8", "Hosea 2:16"), ("Psalm 23:1", "Psalm 91:13"), ("John 3:16", "Romans 1:26"),
               ("Matthew 5:3", "Exodus 12:4")]
KNOWN_QUOTES = [("\"The grass withers, the flower fades, but the word of our God stands forever\"", "Genesis 3:15"),
                ("\"Blessed are the poor in spirit, for theirs is the kingdom of heaven\"", "Leviticus 11:7"),
                ("\"The Lord is my shepherd; I shall not want\"", "Jeremiah 52:3")]
BOOKS_ALL = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Isaiah", "Jeremiah", "Psalm", "Proverbs", "Matthew",
             "Mark", "Luke", "John", "Acts", "Romans", "Hebrews", "Revelation", "Job", "Ezekiel", "Daniel"]
CITE = re.compile(r"\b((?:[1-3] )?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation))\.? (\d{1,3}):(\d{1,3})")


def inj_wrong_scripture(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ms = list(CITE.finditer(t))
        if ms:
            m = ms[rng.randrange(len(ms))]
            book, ch, vs = m.group(1), int(m.group(2)), int(m.group(3))
            if rng.random() < 0.5:
                other = rng.choice([b for b in BOOKS_ALL if b.lower() not in book.lower()])
                rep = f"{other} {ch}:{vs}"
            else:
                rep = f"{book} {ch + 7}:{vs + 11}"
            nt = t[:m.start()] + rep + t[m.end():]
            return ({"type": "wrong_scripture", "sections": [secs[i]["id"]],
                     "spans": [{"section": secs[i]["id"], "original": m.group(0), "injected": rep}], "mode": "altered_existing"},
                    {i: nt})
    # fallback: insert a famous quotation with a wrong reference
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = [s for s in sentences(t) if len(t[s[0]:s[1]].split()) >= 8]
        if not ss:
            continue
        a, b = ss[len(ss) // 2]
        q, ref = KNOWN_QUOTES[rng.randrange(len(KNOWN_QUOTES))]
        ins = f" As it is written: {q} ({ref})."
        return ({"type": "wrong_scripture", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": "", "injected": ins.strip()}], "mode": "inserted_miscited"},
                {i: t[:b] + ins + t[b:]})
    return None


ATTR = re.compile(r"\b((?:[A-Z][a-z]+|the (?:blessed |holy |apostle |prophet )?[A-Z]?[a-z]+|he|she|they) (?:says|said|saith|writes|wrote|declares|declared|teaches|taught|asks|asked|answers|answered|replies|replied|tells|told)(?: to (?:them|him|her|us))?)\s*(?::\s*|,\s*(?=['\"“‘]))")


def inj_speaker_strip(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ms = [m for m in ATTR.finditer(t)]
        if ms:
            m = ms[rng.randrange(len(ms))]
            nt = t[:m.start()] + t[m.end():]
            nt = re.sub(r"(^|[.!?]\s+)(['\"“‘])", lambda x: x.group(0), nt)
            lo, hi = max(0, m.start() - 30), min(len(nt), m.start() + 50)
            return ({"type": "speaker_strip", "sections": [secs[i]["id"]],
                     "spans": [{"section": secs[i]["id"], "original": m.group(0), "injected": "",
                                "context": nt[lo:hi]}]}, {i: nt})
    # fallback: strip "(Acts 1:7)"-style or "said to them:" lead-ins is not possible; rewrite "He said to them:"
    return None


def inj_garbled(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        cl = [m for m in re.finditer(r"[A-Za-z][A-Za-z' \-]{40,110}(?=[,;.])", t) if 7 <= len(m.group(0).split()) <= 16]
        if not cl:
            continue
        m = cl[rng.randrange(len(cl))]
        w = m.group(0).split()
        for _ in range(10):
            sh = w[:]
            rng.shuffle(sh)
            if sh != w and sh[0].lower() != w[0].lower():
                break
        new = " ".join(sh)
        return ({"type": "garbled", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": m.group(0), "injected": new}]},
                {i: t[:m.start()] + new + t[m.end():]})
    return None


def inj_boundary_cut(secs, cands, rng):
    # joint defect on section i (cut mid-sentence) and i+1 (tail restarts, lowercase)
    pairs = [i for i in cands if i + 1 < len(secs) and (i + 1) in cands]
    for i in rng.sample(pairs, len(pairs)):
        t = secs[i]["text"]
        ws = list(re.finditer(r"\S+", t))
        if len(ws) < 60:
            continue
        # cut inside a sentence, at least 12 words before the end
        k = None
        for _ in range(40):
            j = rng.randrange(int(len(ws) * 0.55), len(ws) - 12)
            if not re.search(r"[.!?:;]['\")]?$", ws[j - 1].group(0)) and not re.search(r"[.!?]['\")]?$", ws[j].group(0)):
                k = j
                break
        if k is None:
            continue
        cut = ws[k].start()
        head, tail = t[:cut].rstrip(), t[cut:].lstrip()
        nxt = secs[i + 1]["text"]
        new_nxt = tail[:1].lower() + tail[1:] + " " + nxt
        return ({"type": "boundary_cut", "sections": [secs[i]["id"], secs[i + 1]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": "", "injected": " ".join(head.split()[-8:]) + " [END]"},
                           {"section": secs[i + 1]["id"], "original": "", "injected": " ".join(tail.split()[:8])}]},
                {i: head, i + 1: new_nxt})
    return None


ARCH_SUBS = [(r"\byou have\b", "thou hast"), (r"\byou are\b", "thou art"), (r"\byou\b", "thee"), (r"\byour\b", "thy"),
             (r"\bhas\b", "hath"), (r"\bdoes\b", "doth"), (r"\bsays\b", "saith"), (r"\bdo not\b", "dost not"), (r"\bhe is\b", "he is")]


def inj_archaic(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = [s for s in sentences(t) if len(t[s[0]:s[1]].split()) >= 8]
        if not ss:
            continue
        a, b = ss[rng.randrange(len(ss))]
        sent = t[a:b]
        new = sent
        for pat, rep in ARCH_SUBS:
            new = re.sub(pat, rep, new, count=2)
        if new == sent:
            new = " Verily, thou hast heard that it hath been said, and thus it is. " + sent.lstrip()
            new = (" " if sent.startswith(" ") else "") + new.lstrip()
        if new == sent:
            continue
        return ({"type": "archaic", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": sent.strip(), "injected": new.strip()}]},
                {i: t[:a] + new + t[b:]})
    return None


AUX = r"(is|are|was|were|has|have|had|does|do|did|can|will|shall|should|must|may|might|could|would)"


def inj_negation_flip(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = [s for s in sentences(t) if len(t[s[0]:s[1]].split()) >= 8]
        rng.shuffle(ss)
        for a, b in ss:
            sent = t[a:b]
            m = re.search(r"\b" + AUX + r" not\b", sent)
            if m:
                new = sent[:m.start()] + m.group(1) + sent[m.end():]
            else:
                m = re.search(r"\b" + AUX + r"\b", sent)
                if not m:
                    continue
                new = sent[:m.end()] + " not" + sent[m.end():]
            return ({"type": "negation_flip", "sections": [secs[i]["id"]],
                     "spans": [{"section": secs[i]["id"], "original": sent.strip(), "injected": new.strip()}]},
                    {i: t[:a] + new + t[b:]})
    return None


VERBS = r"(loves|saves|teaches|sent|commands|made|created|called|taught|judges|forgives|gave|raised|wrote|asked|answered|punished|struck|leads|led|sees|saw|hates|loved|fears|feared|blessed|rebuked|heals|healed|forsook|comforts|warns|warned|instructs|instructed)"
AG = re.compile(r"\b((?:[A-Z][a-z]{2,}|the [a-z]{3,}|The [a-z]{3,}))\s+" + VERBS + r"\s+((?:[A-Z][a-z]{2,}|the [a-z]{3,}|his [a-z]{3,}|their [a-z]{3,}))\b")


def inj_agency_swap(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ms = [m for m in AG.finditer(t) if m.group(1).lower() not in ("the", "this", "that")]
        if not ms:
            continue
        m = ms[rng.randrange(len(ms))]
        subj, verb, obj = m.group(1), m.group(2), m.group(3)
        obj_s = re.sub(r"^(his|their)\s", "the ", obj)
        new = f"{cap_like(subj, obj_s) if subj[0].isupper() else obj_s} {verb} {subj[0].lower() + subj[1:] if subj.lower().startswith('the ') else subj}"
        nt = t[:m.start()] + new + t[m.end():]
        return ({"type": "agency_swap", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": m.group(0), "injected": new}]}, {i: nt})
    return None


def inj_omission(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = sentences(t)
        mid = [s for s in ss[1:-1] if 9 <= len(t[s[0]:s[1]].split()) <= 50]
        if not mid:
            continue
        a, b = mid[rng.randrange(len(mid))]
        before = t[:a].split()[-5:]
        after = t[b:].split()[:5]
        nt = (t[:a].rstrip() + " " + t[b:].lstrip())
        return ({"type": "omission", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": t[a:b].strip(), "injected": "",
                            "context": " ".join(before + after)}]}, {i: nt})
    return None


ADD_CLAIMS = ["As the bishops later decreed at Chalcedon, no one may hold otherwise.",
              "This is why the pagan philosophers of Alexandria were finally silenced.",
              "Origen himself confessed that he had received this teaching from an angel in a dream.",
              "For this reason the emperor Constantine ordered that this passage be read aloud every year in Rome."]


def inj_addition(secs, cands, rng):
    for i in rng.sample(cands, len(cands)):
        t = secs[i]["text"]
        ss = sentences(t)
        mid = [s for s in ss[1:-1] if len(t[s[0]:s[1]].split()) >= 6]
        if not mid:
            continue
        a, b = mid[rng.randrange(len(mid))]
        claim = ADD_CLAIMS[rng.randrange(len(ADD_CLAIMS))]
        return ({"type": "addition", "sections": [secs[i]["id"]],
                 "spans": [{"section": secs[i]["id"], "original": "", "injected": claim}]},
                {i: t[:b] + " " + claim + t[b:]})
    return None


INJECTORS = {"term_drift": inj_term_drift, "ancient_title": inj_ancient_title, "malapropism": inj_malapropism,
             "wrong_scripture": inj_wrong_scripture, "speaker_strip": inj_speaker_strip, "garbled": inj_garbled,
             "boundary_cut": inj_boundary_cut, "archaic": inj_archaic, "negation_flip": inj_negation_flip,
             "agency_swap": inj_agency_swap, "omission": inj_omission, "addition": inj_addition}

# ---------------------------------------------------------------- build

def core_of(orig: str, inj: str, pad: int = 2) -> str:
    """Changed words of a sentence-level edit plus `pad` neighbours each side
    (so a quote must touch the actual edit, not just the same sentence)."""
    import difflib
    a, b = orig.split(), inj.split()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    keep: set[int] = set()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if j2 > j1:
            keep.update(range(max(0, j1 - pad), min(len(b), j2 + pad)))
        else:  # pure deletion: anchor on the words around the join
            keep.update(range(max(0, j1 - pad - 1), min(len(b), j1 + pad + 1)))
    return " ".join(b[i] for i in sorted(keep))


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"seed": SEED, "variants": [], "skipped": [], "bases": {}}
    type_cycle = list(TYPES)
    for bi, slug in enumerate(BASES):
        base = load_base(slug)
        words_n = sum(len(s["text"].split()) for s in base)
        manifest["bases"][slug] = {"sections": len(base), "words": words_n}
        (OUT / f"base__{slug}.json").write_text(json.dumps(base, indent=1, ensure_ascii=False))
        for vi in range(VARIANTS_PER_BASE):
            vid = f"{slug}__v{vi + 1}"
            secs = [dict(s) for s in base]
            used: set[int] = set()
            truth = []
            budget = max(2, int(len(base) * 0.6))
            order = type_cycle[(bi * 4 + vi * 6) % len(TYPES):] + type_cycle[:(bi * 4 + vi * 6) % len(TYPES)]
            for ty in order:
                if len(used) >= budget:
                    break
                cands = [i for i in range(len(secs)) if i not in used]
                rng = rng_for(vid, ty)
                res = INJECTORS[ty](secs, cands, rng)
                if res is None:
                    manifest["skipped"].append({"variant": vid, "type": ty, "why": "no applicable site"})
                    continue
                tr, new = res
                touched = set(new)
                if touched & used:
                    manifest["skipped"].append({"variant": vid, "type": ty, "why": "section clash"})
                    continue
                if ty in ("negation_flip", "archaic"):
                    for sp_ in tr["spans"]:
                        sp_["core"] = core_of(sp_["original"], sp_["injected"])
                for k, v in new.items():
                    secs[k]["text"] = v
                used |= touched
                tr["variant"] = vid
                tr["id"] = f"{vid}:{len(truth) + 1}:{ty}"
                truth.append(tr)
            clean = [{k: v for k, v in s.items() if k != "source"} for s in secs]
            (OUT / f"variant__{vid}.json").write_text(json.dumps(clean, indent=1, ensure_ascii=False))
            (OUT / f"variant__{vid}.truth.json").write_text(json.dumps(truth, indent=1, ensure_ascii=False))
            manifest["variants"].append({"id": vid, "base": slug, "defects": len(truth),
                                         "types": [t["type"] for t in truth],
                                         "sections_touched": sorted({s for t in truth for s in t["sections"]})})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    from collections import Counter
    c = Counter(t for v in manifest["variants"] for t in v["types"])
    print("defects per type:", dict(c))
    print("variants:", [(v["id"].split("__")[0][:14] + v["id"][-3:], v["defects"]) for v in manifest["variants"]])
    print("skipped:", manifest["skipped"])
    return 0

# ---------------------------------------------------------------- detectors

def import_lint():
    sys.path.insert(0, str(ROOT))
    try:
        from pipeline.work_lint import lint_work  # type: ignore
        return lint_work
    except Exception as e:  # noqa: BLE001
        return None


def import_source():
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from work_pipeline import source_check  # type: ignore
        return source_check
    except Exception:  # noqa: BLE001
        return None


def sections_of(name: str):
    """name = 'base__slug' or 'variant__vid'."""
    return json.load(open(OUT / f"{name}.json"))


def all_names():
    names = [f"base__{b}" for b in BASES]
    names += [f"variant__{v['id']}" for v in json.load(open(OUT / "manifest.json"))["variants"]]
    return names


def run_lint(force=False):
    lint_work = import_lint()
    if lint_work is None:
        (OUT / "runs").mkdir(exist_ok=True)
        (OUT / "runs" / "lint.SKIPPED.txt").write_text(
            "pipeline/work_lint.py (lint_work) not importable when the bench ran. "
            "Adapter: lint_work(sections=[{id,title,text}], brief=None) -> [{rule,severity,section,quote,why}]; "
            "re-run `defect_bench.py run --detector lint` once it exists.\n")
        print("lint: SKIPPED (work_lint not available)")
        return
    (OUT / "runs").mkdir(exist_ok=True)
    (OUT / "runs" / "lint.SKIPPED.txt").unlink(missing_ok=True)
    for n in all_names():
        secs = sections_of(n)
        fs = lint_work(secs, None)
        (OUT / "runs" / f"lint__{n}.json").write_text(json.dumps(fs, indent=1, ensure_ascii=False))
        print(f"lint {n}: {len(fs)} findings")


def latest_receipt(model: str) -> str | None:
    key = model.replace("/", "_").replace("@", "_")
    fs = sorted(glob.glob(str(Path.home() / "SaneApps/infra/SaneProcess/outputs/llm-api-research" / f"*{key.split('_cf_')[-1].replace('/', '_')}*")))
    for f in reversed(fs):  # newest first; the gate requires purpose translation-qa
        try:
            if "translation-qa" in json.dumps(json.load(open(f)).get("purpose", "")):
                return f
        except (OSError, json.JSONDecodeError):
            continue
    return None


def run_read(models, force=False):
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(Path.home() / "SaneApps/infra/SaneProcess/scripts"))
    import work_read as wr  # noqa: E402
    from llm_vendor_gate import require_llm_receipt  # noqa: E402
    for m in models:
        require_llm_receipt([m], receipt_path=latest_receipt(m), purpose="translation-qa")
    tokens = {"cf": wr.secret("CLOUDFLARE_API_TOKEN"), "nv": wr.secret("NV_API_KEY")}
    (OUT / "runs").mkdir(exist_ok=True)
    jobs = []
    for n in all_names():
        for m in models:
            f = OUT / "runs" / f"read__{n}__{m.split('/')[-1]}.json"
            if f.exists() and not force:
                continue
            jobs.append((n, m, f))

    def one(job):
        n, m, f = job
        secs = sections_of(n)
        title = n.split("__", 1)[1].split("__")[0]
        obj = wr.read_with(m, title, secs, tokens)
        if "_error" in obj:
            print(f"read {n} {m}: ERROR {obj['_error'][:100]}")
            return
        kept, dropped = wr.verify(obj, secs, m)
        f.write_text(json.dumps({"model": m, "work": n, "findings": kept, "dropped": len(dropped),
                                 "followability": obj.get("followability"), "ms": obj.get("_ms")},
                                indent=1, ensure_ascii=False))
        print(f"read {n} {m.split('/')[-1]}: kept {len(kept)} dropped {len(dropped)} {obj.get('_ms')}ms", flush=True)

    # one worker per model so each model sees a modest request rate
    with ThreadPoolExecutor(max(1, len(models))) as ex:
        by_model = {m: [j for j in jobs if j[1] == m] for m in models}
        futs = [ex.submit(lambda js: [one(j) for j in js], js) for js in by_model.values()]
        for fu in futs:
            fu.result()


def run_source(models, force=False):
    sc = import_source()
    (OUT / "runs").mkdir(exist_ok=True)
    if sc is None:
        (OUT / "runs" / "source.SKIPPED.txt").write_text(
            "scripts/work_pipeline.py source_check not available when the bench ran. Contract: "
            "source_check(sections=[{id,source,english}], brief, models) -> [{class,section,quote,why}] "
            "with classes negation|agency|omission|addition|mistranslation|wrong_scripture|speaker. "
            "Re-run `defect_bench.py run --detector source` when it exists.\n")
        print("source: SKIPPED (source_check not available)")
        return
    (OUT / "runs" / "source.SKIPPED.txt").unlink(missing_ok=True)
    bases = {b: load_base(b) for b in BASES}
    for n in all_names():
        f = OUT / "runs" / f"source__{n}.json"
        if f.exists() and not force:
            continue
        slug = n.split("__", 1)[1].split("__")[0]
        src = {s["id"]: s["source"] for s in bases[slug]}
        secs = [{"id": s["id"], "source": src.get(s["id"], ""), "english": s["text"]} for s in sections_of(n)]
        fs = sc(secs, None, models)
        f.write_text(json.dumps(fs, indent=1, ensure_ascii=False))
        print(f"source {n}: {len(fs)} findings", flush=True)

# ---------------------------------------------------------------- scoring

def load_findings(det: str, name: str) -> list[dict]:
    """Normalised findings: {section, quote, kind, variants, detector_tag}."""
    out = []
    runs = OUT / "runs"
    if det == "lint":
        f = runs / f"lint__{name}.json"
        if f.exists():
            for x in json.load(open(f)):
                out.append({"section": str(x.get("section")), "quote": x.get("quote", "") or "",
                            "kind": str(x.get("rule", "")).lower(), "variants": [], "tag": "lint"})
    elif det == "read":
        for f in sorted(runs.glob(f"read__{name}__*.json")):
            d = json.load(open(f))
            for x in d["findings"]:
                out.append({"section": str(x.get("section")), "quote": x.get("quote", "") or "",
                            "kind": x.get("class", ""), "variants": [v.get("text", "") for v in x.get("variants") or []],
                            "variant_sections": [s for v in x.get("variants") or [] for s in v.get("sections", [])],
                            "tag": d["model"].split("/")[-1]})
    elif det == "source":
        f = runs / f"source__{name}.json"
        if f.exists():
            for x in json.load(open(f)):
                out.append({"section": str(x.get("section")), "quote": x.get("quote", "") or "",
                            "kind": x.get("class", ""), "variants": [], "tag": "source"})
    return out


def overlap(quote: str, span: str) -> bool:
    qw, sw = words(quote), words(span)
    if not qw or not sw:
        return False
    need = 3 if len(sw) >= 3 and len(qw) >= 3 else 2 if min(len(sw), len(qw)) >= 2 else 1
    if need == 1:
        return norm(quote) in norm(span) or norm(span) in norm(quote)
    sset = {tuple(sw[i:i + need]) for i in range(len(sw) - need + 1)}
    return any(tuple(qw[i:i + need]) in sset for i in range(len(qw) - need + 1))


def matches(f: dict, d: dict) -> bool:
    if f["section"] not in d["sections"]:
        # lint/readers may name the section by title or prefix; exact match only (conservative)
        if not (d["type"] == "term_drift" and any(s in d["sections"] for s in f.get("variant_sections", []))):
            return False
    for sp in d["spans"]:
        if sp.get("core"):
            targets = [sp["core"]]
        else:
            targets = [sp.get("injected", ""), sp.get("context", ""), sp.get("original", "") if d["type"] in ("term_drift",) else ""]
        if sp["section"] != f["section"] and d["type"] != "term_drift":
            continue
        for tg in targets:
            if tg and overlap(f["quote"], tg):
                return True
        if d["type"] == "term_drift":
            vv = {norm(v) for v in d["variants"]}
            if any(norm(x) in vv for x in f["variants"]) or norm(f["quote"]) in vv:
                return True
            for tg in (sp["injected"],):
                if tg and re.search(r"\b" + re.escape(norm(tg)) + r"\b", norm(f["quote"])):
                    return True
    return False


def typed(f: dict, d: dict) -> bool:
    k = f["kind"].lower()
    return any(c in k for c in TYPE_COMPAT[d["type"]])


def load_truth():
    out = []
    for f in sorted(OUT.glob("variant__*.truth.json")):
        out += json.load(open(f))
    return out


def score() -> int:
    truth = load_truth()
    man = json.load(open(OUT / "manifest.json"))
    base_findings = {}
    for b in BASES:
        for det in ("lint", "read", "source"):
            base_findings[(det, b)] = load_findings(det, f"base__{b}")
    base_keys = {(det, b): {(f["section"], norm(f["quote"])) for f in fs} for (det, b), fs in base_findings.items()}
    present = {det: any(list((OUT / "runs").glob(f"{det}__variant__{v['id']}*.json")) for v in man["variants"])
               for det in ("lint", "read", "source")}
    dets = [d for d in ("lint", "read", "source") if present[d]]
    rows = {}
    per_defect = []
    for d in truth:
        slug = d["variant"].split("__")[0]
        rec = {"id": d["id"], "type": d["type"]}
        for det in dets:
            fs = load_findings(det, f"variant__{d['variant']}")
            bk = base_keys[(det, slug)]
            novel = [f for f in fs if (f["section"], norm(f["quote"])) not in bk]
            hit = [f for f in novel if matches(f, d)]
            rec[det] = bool(hit)
            rec[det + "_typed"] = any(typed(f, d) for f in hit)
            if det == "source" and d["type"] in SOURCE_TYPES:
                rec["source_class_section"] = rec["source"] or any(
                    f["section"] in d["sections"] and SOURCE_TYPES[d["type"]] in f["kind"].lower() for f in novel)
            rec[det + "_by"] = sorted({f["tag"] for f in hit})
        per_defect.append(rec)
    # per-model read recall
    models = sorted({t for r in per_defect for t in r.get("read_by", [])})
    lines = []
    L = lines.append
    L("# Seeded-defect bench: report\n")
    L(f"Generated {time.strftime('%Y-%m-%d %H:%M')} | seed {SEED} | bases: {', '.join(BASES)}\n")
    L(f"Defects injected: {len(truth)} across {len(man['variants'])} variants "
      f"({sum(b['words'] for b in man['bases'].values())} base words, "
      f"{sum(b['sections'] for b in man['bases'].values())} base sections).\n")
    for d in ("lint", "read", "source"):
        if not present[d]:
            sk = OUT / "runs" / f"{d}.SKIPPED.txt"
            L(f"- detector `{d}`: NOT RUN" + (f" ({sk.read_text().strip()[:160]})" if sk.exists() else ""))
    L("")
    cols = dets + (["read_any"] if "read" in dets else []) + ["combined"]
    L("## Recall (localized + novel catch; strict typed catch in brackets)\n")
    L("| defect type | n | " + " | ".join(cols) + " |")
    L("|---|---|" + "---|" * len(cols))
    tot = {c: [0, 0, 0] for c in cols}  # hits, typed hits, n
    for ty in TYPES:
        rs = [r for r in per_defect if r["type"] == ty]
        if not rs:
            continue
        cells = []
        for c in cols:
            if c == "combined":
                h = sum(any(r.get(x) for x in dets) for r in rs)
                th = sum(any(r.get(x + "_typed") for x in dets) for r in rs)
            elif c == "read_any":
                h, th = sum(r["read"] for r in rs), sum(r["read_typed"] for r in rs)
            else:
                h, th = sum(r[c] for r in rs), sum(r[c + "_typed"] for r in rs)
            tot[c][0] += h; tot[c][1] += th; tot[c][2] += len(rs)
            cells.append(f"{h}/{len(rs)} [{th}]")
        L(f"| {ty} | {len(rs)} | " + " | ".join(cells) + " |")
    L("| **all** | " + str(len(per_defect)) + " | " + " | ".join(
        f"{tot[c][0]}/{tot[c][2]} [{tot[c][1]}]" for c in cols) + " |")
    L("")
    if "read" in dets and models:
        L("## Reader recall per model (localized)\n")
        L("| defect type | " + " | ".join(models) + " |")
        L("|---|" + "---|" * len(models))
        for ty in TYPES:
            rs = [r for r in per_defect if r["type"] == ty]
            if rs:
                L(f"| {ty} | " + " | ".join(f"{sum(m in r['read_by'] for r in rs)}/{len(rs)}" for m in models) + " |")
        L("")
    if "source" in dets:
        L("## Source detector, class-in-right-section level (lenient)\n")
        for ty in SOURCE_TYPES:
            rs = [r for r in per_defect if r["type"] == ty]
            if rs:
                L(f"- {ty}: {sum(r.get('source_class_section', False) for r in rs)}/{len(rs)}")
        L("")
    # precision / flood check: how many novel findings per variant, and what share hit a seeded defect
    L("## Finding volume vs hit rate (variants)\n")
    L("| detector | novel findings | that hit a seeded defect | hit share | novel findings per 1k words |")
    L("|---|---|---|---|---|")
    for det in dets:
        nov = hit = 0
        w = 0
        for v in man["variants"]:
            slug = v["id"].split("__")[0]
            bk = base_keys[(det, slug)]
            fs = [f for f in load_findings(det, f"variant__{v['id']}") if (f["section"], norm(f["quote"])) not in bk]
            ds = [d for d in truth if d["variant"] == v["id"]]
            nov += len(fs)
            hit += sum(any(matches(f, d) for d in ds) for f in fs)
            w += man["bases"][slug]["words"]
        L(f"| {det} | {nov} | {hit} | {hit / max(nov, 1):.0%} | {nov / w * 1000:.1f} |")
    L("")
    # false positives on the unmodified base
    L("## False-positive baseline (unmodified base works; raw findings, not adjudicated)\n")
    L("| detector | base words | findings | per 1k words |")
    L("|---|---|---|---|")
    samples = []
    for det in ("lint", "read", "source"):
        if not present[det]:
            continue
        n = sum(len(base_findings[(det, b)]) for b in BASES)
        w = sum(man["bases"][b]["words"] for b in BASES)
        L(f"| {det} | {w} | {n} | {n / w * 1000:.2f} |")
        for b in BASES:
            for f in base_findings[(det, b)]:
                samples.append({"detector": det, "tag": f["tag"], "work": b, **{k: f[k] for k in ("section", "quote", "kind")}})
    L("")
    random.Random(SEED).shuffle(samples)
    (OUT / "fp_sample.json").write_text(json.dumps(samples[:10], indent=1, ensure_ascii=False))
    (OUT / "fp_all.json").write_text(json.dumps(samples, indent=1, ensure_ascii=False))
    miss = [f"{b} ({m})" for b in BASES for m in models if not (OUT / "runs" / f"read__base__{b}__{m}.json").exists()]
    if miss:
        L("Missing reader base runs (model output unparseable after 3 tries): " + ", ".join(miss) +
          ". For those, 'novel' filtering has no baseline and base FP counts are understated.\n")
    L("10 random base findings for adjudication are in `fp_sample.json` (all in `fp_all.json`).\n")
    L("## How to read this\n")
    L("- Defects are synthetic and mechanical. Recall here is a floor on easy, clearly localized cases, not a field estimate.")
    L("- Base works are 'clean' only relative to check_pass_ab; findings on them may be true defects in the base, which is why catches must be novel against the base run.")
    L("- omission, agency_swap and negation_flip are mostly invisible to English-only detectors; low `lint`/`read` recall there is expected and is the case for the source-aware checker.")
    L("- Reader recall is bought with volume: it flags roughly 15 things per 1k words on CLEAN text, so a hit is cheap and the useful signal is the typed column plus the hit share above. Raw reader findings cannot gate publication without a triage step.")
    L("- Lint is near-silent on clean text (about 0.5 per 1k words) but only sees the shapes it has rules for; zero recall on term_drift here means its drift rule does not cover these ordinary words, not that drift is rare.")
    L("- Nothing English-only caught omission. Source-aware recall for negation/agency/omission/addition is unmeasured until `source_check` exists; re-run `run --detector source` then `score`.")
    L("- Reader runs are single samples per variant; model output varies. Treat differences under ~15 points as noise (n per type is 2-4).")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    (OUT / "per_defect.json").write_text(json.dumps(per_defect, indent=1))
    print("\n".join(lines))
    return 0

# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("build")
    r = sp.add_parser("run")
    r.add_argument("--detector", default="all", choices=["lint", "read", "source", "all"])
    r.add_argument("--models", default="@cf/deepseek-ai/deepseek-v4-pro-0813,@cf/moonshotai/kimi-k2.6")
    r.add_argument("--force", action="store_true")
    sp.add_parser("score")
    a = ap.parse_args()
    if a.cmd == "build":
        return build()
    if a.cmd == "score":
        return score()
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    if a.detector in ("lint", "all"):
        run_lint(a.force)
    if a.detector in ("source", "all"):
        run_source(models, a.force)
    if a.detector in ("read", "all"):
        run_read(models, a.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
