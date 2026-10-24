import json,glob,re,sys
NUM={w:i for i,w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE THIRTEEN FOURTEEN FIFTEEN SIXTEEN SEVENTEEN EIGHTEEN NINETEEN TWENTY".split())}
TENS={"TWENTY":20,"THIRTY":30,"FORTY":40}
def num(w):
    w=w.upper()
    if w in NUM: return NUM[w]
    if '-' in w:
        a,b=w.split('-',1); return TENS[a]+NUM[b]
    return TENS[w]
def roman(s):
    v={'I':1,'V':5,'X':10,'L':50,'C':100}; t=0
    for i,c in enumerate(s):
        t+= -v[c] if i+1<len(s) and v[c]<v[s[i+1]] else v[c]
    return t
def clean(t):
    o=t
    m=re.match(r"^CHAPTER ([A-Z\-]+)\. (.*)$",t)
    if m: t=f"Chapter {num(m.group(1))}: {m.group(2)}"
    t=re.sub(r"^Cap\.\s?\d+ close:\s*","",t)
    t=re.sub(r"\bGods\b","God's",t); t=t.replace("humans obligation","human's obligation")
    # trailing worksheet tails
    t=re.sub(r"\s*[;—–-]*\s*(?:—\s*)?Cap\.\s?\d+\s*(?:/\s*Liber [IVX]+\s*)?(?:close|COMPLETE|mid|next)\b.*$","",t)
    t=re.sub(r"\s*[;—–]\s*Cap\.\s?\d+\s+(?:close|next).*$","",t)
    t=re.sub(r"\s*[;,]\s*Cap\.\s?\d+\s+toward\s+Hexaemeron$","",t)
    t=re.sub(r"\s*[;—–]\s*Cap\.\s?\d+\s+(?:toward|before).*$","",t)
    t=re.sub(r"\s*;\s*Cap\.\s?\d+\s+next.*$","",t)
    t=re.sub(r"\s*toward Cap\.\s?\d+","",t)
    t=re.sub(r"\s*[;—–]\s*Liber [IVX]+ close.*$","",t)
    t=re.sub(r"\s*;\s*FINIS Liber IV / Syntagma$","",t)
    t=re.sub(r"^Cap\.\s?\d+ close:\s*","",t)
    t=re.sub(r"^Pastoral close of Cap\. \d+$","Pastoral close",t)
    t=re.sub(r"\s*—\s*Cap\. \d+ close of I$"," (end of part I)",t)
    t=re.sub(r"^Liber I corona:\s*","Close of Book 1: ",t)
    t=re.sub(r"Liber II corona","close of Book 2",t)
    t=re.sub(r"^Aph\. ([IVXL]+)(?:-([IVXL]+))?:",lambda m:"Aphorisms %d–%d:"%(roman(m.group(1)),roman(m.group(2))) if m.group(2) else "Aphorism %d:"%roman(m.group(1)),t)
    t=t.replace("Pentateuch, Triteuch, Octateuch","the books of Moses and the groups of three and eight books")
    t=t.replace("On the Hexaemeron, or the works of the six days","On the six days of creation")
    t=re.sub(r"\s*[;—–]\s*$","",t).strip()
    if t and t[0].islower(): t=t[0].upper()+t[1:]
    return t
changes=[]
for f in sorted(glob.glob('translations/*_english.json')):
    raw=open(f).read(); rows=json.loads(raw); ch=False
    for r in rows:
        n=clean(r.get('title',''))
        if n!=r.get('title',''): changes.append((f,r['section'],r['title'],n)); r['title']=n; ch=True
    if ch and '--write' in sys.argv:
        ind=2 if re.search(r'\n  [\[{"]',raw[:300]) else (1 if re.search(r'\n [\[{"]',raw[:300]) else None)
        open(f,'w').write(json.dumps(rows,ensure_ascii=False,indent=ind)+('\n' if raw.endswith('\n') else ''))
for c in changes: print(c[0].split('/')[-1][:-13],c[1],'|',c[2],'\n      ->',c[3])
print(len(changes))
