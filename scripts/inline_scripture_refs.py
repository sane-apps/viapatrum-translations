#!/usr/bin/env python3
"""Insert full-name parenthetical Bible refs into Pass B english[] from added_allusions / bible_refs."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ABBREV = {
 'Gen':'Genesis','Exod':'Exodus','Ex':'Exodus','Lev':'Leviticus','Num':'Numbers','Deut':'Deuteronomy',
 'Josh':'Joshua','Judg':'Judges','Ruth':'Ruth','1 Sam':'1 Samuel','2 Sam':'2 Samuel','1 Kgs':'1 Kings','2 Kgs':'2 Kings',
 '1 Chr':'1 Chronicles','2 Chr':'2 Chronicles','Ezra':'Ezra','Neh':'Nehemiah','Esth':'Esther','Job':'Job',
 'Ps':'Psalm','Psalm':'Psalm','Pss':'Psalms','Prov':'Proverbs','Eccl':'Ecclesiastes','Song':'Song of Songs',
 'Isa':'Isaiah','Jer':'Jeremiah','Lam':'Lamentations','Ezek':'Ezekiel','Dan':'Daniel',
 'Hos':'Hosea','Joel':'Joel','Amos':'Amos','Obad':'Obadiah','Jonah':'Jonah','Mic':'Micah','Nah':'Nahum',
 'Hab':'Habakkuk','Zeph':'Zephaniah','Hag':'Haggai','Zech':'Zechariah','Mal':'Malachi',
 'Matt':'Matthew','Mt':'Matthew','Mark':'Mark','Mk':'Mark','Luke':'Luke','Lk':'Luke','John':'John','Jn':'John',
 'Acts':'Acts','Rom':'Romans','1 Cor':'1 Corinthians','2 Cor':'2 Corinthians','Gal':'Galatians','Eph':'Ephesians',
 'Phil':'Philippians','Col':'Colossians','1 Thess':'1 Thessalonians','2 Thess':'2 Thessalonians',
 '1 Tim':'1 Timothy','2 Tim':'2 Timothy','Tit':'Titus','Titus':'Titus','Phlm':'Philemon','Heb':'Hebrews',
 'Jas':'James','James':'James','1 Pet':'1 Peter','2 Pet':'2 Peter','1 John':'1 John','2 John':'2 John','3 John':'3 John',
 'Jude':'Jude','Rev':'Revelation','Wis':'Wisdom','Sir':'Sirach','Bar':'Baruch','Tob':'Tobit',
}
FULL_NAMES = sorted(set(ABBREV.values()), key=len, reverse=True)

def expand_ref(raw: str) -> str | None:
    if not raw: return None
    raw = re.sub(r'\s+LXX.*$', '', raw.strip()).split('/')[0].strip()
    m = re.match(r'^([1-3]?\s*[A-Za-z][A-Za-z.]*(?:\s+[A-Za-z.]+)*)\s+(\d+[:.].*)$', raw)
    if not m: return None
    book, loc = m.group(1).strip(), m.group(2).strip().replace('-', '–')
    key = book.replace('.', '')
    book = ABBREV.get(key, ABBREV.get(book, book))
    if book == 'Psalms': book = 'Psalm'
    return f'{book} {loc}'


def _norm_open(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())[:90]


def build_justification_index(book_dir: Path) -> dict[str, Path]:
    """Map normalized Pass B opening line -> justification path."""
    jdir = book_dir / "reviews" / "justifications"
    idx: dict[str, Path] = {}
    if not jdir.exists():
        return idx
    for f in jdir.glob("*.json"):
        try:
            j = json.loads(f.read_text())
        except Exception:
            continue
        pb = j.get("pass_b_english") or []
        if not pb:
            continue
        opening = pb[0] if isinstance(pb, list) else pb
        idx[_norm_open(opening)] = f
    return idx


def justification_path(
    section: dict,
    book_dir: Path,
    stem: str | None = None,
    just_index: dict[str, Path] | None = None,
) -> Path | None:
    jp = section.get("justification")
    if jp:
        jpath = book_dir / jp if not Path(jp).is_absolute() else Path(jp)
        if not jpath.exists() and not str(jp).startswith("reviews/"):
            jpath = book_dir / "reviews" / "justifications" / Path(jp).name
        if jpath.exists():
            return jpath

    jdir = book_dir / "reviews" / "justifications"
    names: list[str] = []
    sec = section.get("section")

    # Explicit stem patterns
    if stem and sec is not None:
        s = str(sec)
        names += [f"{stem}_{s}.json", f"{stem}_{s.replace('.', '_')}.json"]
        if s.isdigit():
            n = int(s)
            names += [
                f"{stem}_{n:02d}.json",
                f"{stem}_{n:03d}.json",
                f"{stem}_{n}.json",
            ]
        if re.fullmatch(r"\d+\.\d+", s):
            a, b = s.split(".")
            names += [
                f"{stem}_{a}_{b}.json",
                f"{stem}_{int(a)}_{int(b)}.json",
                f"{stem}_{int(a)}_{int(b):02d}.json",
            ]

    # Julian Ad Florum: stem like florus_1 + section N -> florus_1_00N.json
    if stem and stem.startswith("florus_") and sec is not None and str(sec).isdigit():
        names.append(f"{stem}_{int(sec):03d}.json")

    # Matthew fragments: matt_frag_NN from section number
    if stem in {"matt_frag", "matthew_fragments", "matthew"} and sec is not None and str(sec).isdigit():
        names += [f"matt_frag_{int(sec):02d}.json", f"matt_frag_{int(sec)}.json"]

    # Sequential stems with 001 padding (collective/marriage/rome)
    if stem in {"collective", "marriage", "rome"} and sec is not None and str(sec).isdigit():
        names.append(f"{stem}_{int(sec):03d}.json")

    for name in names:
        cand = jdir / name
        if cand.exists():
            return cand

    # Fallback: match Pass B opening against justification index (Turbantius etc.)
    if just_index is not None:
        eng = section.get("english") or []
        if eng:
            hit = just_index.get(_norm_open(eng[0]))
            if hit is not None:
                return hit
    return None


def collect_refs(section: dict, book_dir: Path, stem: str | None = None, just_index: dict[str, Path] | None = None) -> list[str]:
    refs=[]
    for a in section.get('added_allusions') or []:
        if isinstance(a, str):
            r=expand_ref(a)
            if r: refs.append(r)
            continue
        cert = a.get('certainty') or a.get('certainty')
        if cert not in (None, 'clear'):
            continue
        r=expand_ref(a.get('reference') or a.get('display') or '')
        if r: refs.append(r)
    jpath = justification_path(section, book_dir, stem, just_index)
    if jpath is not None:
        j=json.loads(jpath.read_text())
        for br in j.get('bible_refs') or []:
            r=expand_ref(br if isinstance(br,str) else (br.get('display') or br.get('reference') or ''))
            if r: refs.append(r)
    out,seen=[],set()
    for r in refs:
        if r not in seen:
            seen.add(r); out.append(r)
    return out

def quote_spans(text: str):
    """Prefer curly double, then curly single, then straight double, then long straight-single spans."""
    spans=[]; i=0
    while i < len(text):
        if text[i]=='“':
            j=text.find('”', i+1)
            if j!=-1:
                spans.append((i,j+1,text[i+1:j])); i=j+1; continue
        i+=1
    if spans: return spans
    i=0
    while i < len(text):
        if text[i]=='‘':
            j=text.find('’', i+1)
            if j!=-1 and (j-i) >= 12:
                spans.append((i,j+1,text[i+1:j])); i=j+1; continue
        i+=1
    if spans: return spans
    pos=[m.start() for m in re.finditer(r'"', text)]
    for a,b in zip(pos[0::2], pos[1::2]):
        spans.append((a,b+1,text[a+1:b]))
    if spans: return spans
    # Apostrophe-quoted scripture common in Adorations: 'Do not think...'
    # Pair ' that look like quote delimiters (preceded by space/punct, length>=20)
    matches=list(re.finditer(r"(?<![A-Za-z])'([^']{20,})'(?![A-Za-z])", text))
    for m in matches:
        spans.append((m.start(), m.end(), m.group(1)))
    return spans

def append_ref(text, ref):
    if f'({ref})' in text: return text
    if text.endswith('…'): return text[:-1].rstrip()+f' ({ref})…'
    if text[-1:] in '.!?;:': return text[:-1]+f' ({ref})'+text[-1]
    return text.rstrip()+f' ({ref})'

def insert_at(text, index, refs):
    cluster=' '.join(f'({r})' for r in refs)
    after=text[index:]
    m=re.match(r'(?:\s*\((?:'+'|'.join(map(re.escape,FULL_NAMES))+r')[^)]*\))*', after)
    at=index+(m.end() if m else 0)
    need_space=not(at>0 and text[at-1:at]==' ')
    return text[:at]+((' ' if need_space else '')+cluster)+text[at:]

def place_refs(paragraphs, refs):
    paras=list(paragraphs)
    pending=[r for r in refs if not any(f'({r})' in p for p in paras)]
    if not pending: return paras
    all_spans=[]
    for pi,p in enumerate(paras):
        for start,end,interior in quote_spans(p):
            all_spans.append({'pi':pi,'end':end,'interior':interior,'len':len(interior),'used':False})
    assignments_span={}; assignments_para_end={}
    # sequential long quotes first (adorations are catena-heavy)
    for ref in list(pending):
        for si, sp in enumerate(all_spans):
            if sp['used'] or sp['len'] < 35: continue
            all_spans[si]['used']=True
            assignments_span.setdefault(si, []).append(ref)
            pending.remove(ref); break
    for ref in list(pending):
        for si, sp in enumerate(all_spans):
            if sp['used']: continue
            all_spans[si]['used']=True
            assignments_span.setdefault(si, []).append(ref)
            pending.remove(ref); break
    if pending:
        cands=[i for i,p in enumerate(paras) if len(p)>40]
        t=cands[-1] if cands else len(paras)-1
        assignments_para_end.setdefault(t, []).extend(pending)
    by_para={}
    for si, rs in assignments_span.items():
        sp=all_spans[si]
        by_para.setdefault(sp['pi'], []).append((sp['end'], rs))
    out=[]
    for i,p in enumerate(paras):
        new_p=p
        for end, rs in sorted(by_para.get(i, []), key=lambda x: -x[0]):
            new_p=insert_at(new_p, end, rs)
        for r in assignments_para_end.get(i, []):
            new_p=append_ref(new_p, r)
        out.append(re.sub(r' {2,}',' ', new_p))
    return out

def sync_justification(book_dir, section, new_english, stem: str | None = None, just_index: dict[str, Path] | None = None):
    jpath = justification_path(section, book_dir, stem, just_index)
    if jpath is None: return
    j=json.loads(jpath.read_text())
    j['pass_b_english']=new_english
    jpath.write_text(json.dumps(j, ensure_ascii=False, indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('english_json')
    ap.add_argument('--book-dir', default=None)
    args=ap.parse_args()
    eng_path=Path(args.english_json)
    book_dir=Path(args.book_dir) if args.book_dir else eng_path.parents[1]
    stem = eng_path.name
    for suf in ('_english.json', '.json'):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            break
    # Filename stem aliases for justification prefixes
    aliases = {
        'ad_florum_1': 'florus_1', 'ad_florum_2': 'florus_2', 'ad_florum_3': 'florus_3',
        'ad_florum_4': 'florus_4', 'ad_florum_5': 'florus_5', 'ad_florum_6': 'florus_6',
        'collective_letter': 'collective',
        'marriage2': 'marriage',
        'letter_to_rome': 'rome',
        'matthew_fragments': 'matt_frag',
        # contra_julianum relies on pass_b index match (turbantius_*)
        'contra_julianum_1': 'turbantius',
        'contra_julianum_2': 'turbantius',
        'contra_julianum_3': 'turbantius',
        'contra_julianum_4': 'turbantius',
        'contra_julianum_5': 'turbantius',
        'contra_julianum_6': 'turbantius',
    }
    stem = aliases.get(stem, stem)
    just_index = build_justification_index(book_dir)
    data=json.loads(eng_path.read_text())
    # For sequential works lacking numeric section, invent 1-based section for just lookup
    for i, s in enumerate(data, start=1):
        if s.get('section') is None:
            s['_seq'] = i
    changed=0
    for i, s in enumerate(data, start=1):
        if s.get('section') is None:
            s = dict(s)
            s['section'] = s.get('_seq', i)
        refs=collect_refs(s, book_dir, stem, just_index)
        if not refs: continue
        old=list(s.get('english') or [])
        new=place_refs(old, refs)
        if new!=old:
            data[i-1]['english']=new
            sync_justification(book_dir, s, new, stem, just_index)
            changed+=1
    eng_path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    FULL=re.compile(r'\((?:'+'|'.join(map(re.escape,FULL_NAMES))+r') [^)]*\d+:\d+')
    n_full=sum(1 for s in data if FULL.search('\n'.join(s.get('english') or [])))
    print(f'changed={changed} with_full={n_full}/{len(data)}')

if __name__=='__main__':
    main()
