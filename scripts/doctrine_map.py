#!/usr/bin/env python3
"""Where did this belief come from? Search the library for each disputed
question and judge every relevant passage blind (owner 2026-10-03).

  index   embed every English paragraph of every book (incremental)
  search  candidate passages per question (semantic search, then rerank)
  grade   blind judging by two checkers from different labs; a referee breaks splits
  report  write the site data file data/explore/doctrine_map.json
  audit-locus  stamp locus + audited text on audit rows (index and report do it too)

Questions come from data/explore/doctrine_questions.json: each lists the
competing precise positions, every one defined in the words of the tradition
that holds it, with the MARK that tells it from its neighbours and the
SHARED GROUND that counts for none of them. Spec: docs/BELIEFS_MAP_SPEC.md.

Bias guards: graders see positions only as shuffled letters, never names or
churches; a passage counts for a position only when it states that
position's mark or rules it out, never for sounding similar; silence is never
evidence; a split with no majority is shown as disputed.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = Path.home() / "SaneApps/websites/fathers.saneapps.com"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SITE / "scripts"))
import book_era  # noqa: E402
import llm_bakeoff as LB  # noqa: E402
import work_pipeline as W  # noqa: E402
from search_sync import embed_docs, _req, CF  # noqa: E402
# Passage ids hash the cleaned words, so the cleaner must not change under the
# grades: speak_text.read_text moved to the reader's words on 2026-10-06, which
# would make ~300 graded passages look new (re-embed, re-grade, and drop from the
# map meanwhile) with no English change. The legacy cleaner keeps the old ids;
# beliefs_page._on_page ignores the [brackets] it leaves in.
from speak_text import legacy_read_text as read_text  # noqa: E402

OUT = ROOT / "outputs" / "doctrine-map"
SITE_DATA = SITE / "data" / "explore" / "doctrine_map.json"
EMBED = "@cf/qwen/qwen3-embedding-0.6b"
RERANK = "@cf/baai/bge-reranker-base"
INSTRUCTION = "Given a statement of Christian doctrine, retrieve early Christian passages that affirm, approach or contradict it"
MIN_WORDS = 25
MAP_UNTIL = 800         # the map covers dated writers to AD 800; later works and undated ones are left out
CHUNK_CHARS = 1600
PER_QUERY = 60          # nearest paragraphs per search phrasing
KEEP_EARLY = 90         # graded candidates per doctrine from writers who died by 450
KEEP_LATER = 30         # writers dated 451-800, for the rest of the timeline
ATTRIBUTION = SITE / "data" / "explore" / "attribution.json"
def sha(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def token() -> str:
    if not W.TOKENS["cf"]:
        W.TOKENS["cf"], W.TOKENS["nv"] = W.secret("CLOUDFLARE_API_TOKEN"), W.secret("NV_API_KEY")
    if not W.TOKENS["cf"]:
        raise SystemExit("no CF token: source ~/.config/nv/env")
    return W.TOKENS["cf"]


# ---------------------------------------------------------------- index

def paragraphs():
    """(id, book, file, section, author, year, text) for every English paragraph."""
    for f in sorted((ROOT / "books").glob("*/translations/*_english.json")):
        book = f.parts[-3]
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        rows = rows if isinstance(rows, list) else rows.get("sections", [])
        author, year = book_era.author_of(book), book_era.book_year(book)
        for r in rows:
            if not isinstance(r, dict):
                continue
            paras = [read_text(p) for p in r.get("english") or [] if isinstance(p, str)]
            for k, text in enumerate(paras):
                text = re.sub(r"\s+", " ", text).strip()
                if len(text.split()) < MIN_WORDS:
                    continue
                for j in range(0, len(text), CHUNK_CHARS):
                    piece = text[max(0, j - 200):j + CHUNK_CHARS] if j else text[:CHUNK_CHARS]
                    yield {"id": sha(f"{f.name}|{r.get('section')}|{k}|{j}|{piece}"), "book": book, "file": f.stem,
                           "section": str(r.get("section")), "para": k, "author": author, "year": year, "text": piece}


def index() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    corpus_path, emb_path = OUT / "corpus.jsonl", OUT / "emb.npy"
    old = {}
    if corpus_path.exists() and emb_path.exists():
        rows = [json.loads(x) for x in corpus_path.read_text().splitlines()]
        audit_backfill(rows)    # locus + audited text, while the audited ids still resolve
        vecs = np.load(emb_path)
        old = {r["id"]: vecs[i] for i, r in enumerate(rows)}
    rows = list(paragraphs())
    todo = [r for r in rows if r["id"] not in old]
    print(f"index: {len(rows)} passages, {len(todo)} to embed", flush=True)
    tok = token()
    batches = [todo[i:i + 32] for i in range(0, len(todo), 32)]

    def one(batch):
        for attempt in range(4):
            try:
                v = embed_docs(tok, [r["text"] for r in batch])
                if len(v) == len(batch):
                    return v
            except Exception as e:  # noqa: BLE001
                print(f"  embed retry: {e}", flush=True)
            time.sleep(10 * (attempt + 1))
        raise RuntimeError("embedding failed after retries")

    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for batch, vecs in zip(batches, ex.map(one, batches)):
            for r, v in zip(batch, vecs):
                old[r["id"]] = np.asarray(v, dtype=np.float32)
            done += 1
            if done % 100 == 0:
                print(f"  embedded {done}/{len(batches)} batches", flush=True)
    mat = np.stack([old[r["id"]] for r in rows]).astype(np.float32)
    mat /= np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9
    np.save(emb_path, mat.astype(np.float16))
    corpus_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"index: wrote {len(rows)} passages", flush=True)
    return 0


# ---------------------------------------------------------------- search

def load_corpus():
    rows = [json.loads(x) for x in (OUT / "corpus.jsonl").read_text().splitlines()]
    return rows, np.load(OUT / "emb.npy").astype(np.float32)


def embed_queries(tok: str, qs: list[str]) -> np.ndarray:
    res = _req("POST", f"{CF}/ai/run/{EMBED}", tok, json.dumps({"queries": qs, "instruction": INSTRUCTION}).encode())
    v = np.asarray((res.get("result") or {}).get("data") or [], dtype=np.float32)
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)


def rerank(tok: str, query: str, texts: list[str]) -> list[float]:
    scores = [0.0] * len(texts)
    for i in range(0, len(texts), 50):
        res = _req("POST", f"{CF}/ai/run/{RERANK}", tok,
                   json.dumps({"query": query, "contexts": [{"text": t[:2000]} for t in texts[i:i + 50]]}).encode())
        for item in (res.get("result") or {}).get("response") or []:
            scores[i + int(item["id"])] = float(item["score"])
    return scores


# ---------------------------------------------------------------- questions
# Owner 2026-10-03: map exact meanings, not what "sounds similar". Each
# question lists competing precise positions; every passage is judged against
# all of them at once, so shared ground ("this is my body") counts for no one.

QUESTIONS = SITE / "data" / "explore" / "doctrine_questions.json"
VERDICTS = ("states", "compatible", "excludes")
# Graders from two labs: Kimi (also a lanes checker) and gpt-oss; GLM-5.2 is
# left to the lanes after it hit 429s when shared (2026-10-03). Nemotron
# (NVIDIA) referees. Both checkers are batch-capable: grading sends them
# through the batch broker only (DM_BATCH_ONLY, default on), so it never takes
# the lanes' direct per-model slots.
CHECKERS = os.environ.get("DM_CHECKERS", "@cf/moonshotai/kimi-k2.6,@cf/openai/gpt-oss-120b").split(",")
BATCH_ONLY = os.environ.get("DM_BATCH_ONLY", "1") != "0"

Q_SYS = """You read one passage from an early Christian writer and compare it with several competing positions on one question.
You do not know which church holds which position, and must not guess. Judge only what this passage says, in its own terms.

For EACH position give one verdict:
- states: the passage says that position's distinguishing mark (its MARK), in any wording. Saying only the SHARED GROUND is never enough.
- excludes: the passage says something that rules the position out (see EXCLUDED BY), or denies its mark.
- compatible: neither. The passage fits the position, or does not touch it, but does not decide it.

Rules: Most passages are compatible with most positions; say so. Never read later doctrine back into early words; similar-sounding language is not the mark. Never count silence. A bare quotation of Scripture decides nothing unless the writer interprets it. For states or excludes, quote the exact deciding words (under 40 words).

Also say whether the passage is on the question at all.

Reply with JSON only: {"on_question": true|false, "verdicts": {"A": {"verdict": "states|compatible|excludes", "quote": "...", "why": "one plain sentence"}, "B": {...}}}"""


def load_questions() -> list[dict]:
    return json.loads(QUESTIONS.read_text())


def q_prompt(q: dict, order: list[int], passage: str) -> str:
    lines = [f"QUESTION: {q['question']}", "", "SHARED GROUND (counts for no position):"]
    lines += [f"- {s}" for s in (q.get("shared_ground") or [])]
    for label, i in zip("ABCDEFGH", order):
        p = q["positions"][i]
        lines += ["", f"POSITION {label}: {p['statement']}", f"  MARK: {p['mark']}",
                  f"  EXCLUDED BY: {p.get('excluded_by') or '-'}"]
    lines += ["", "PASSAGE:", passage]
    return "\n".join(lines)


def load_attribution() -> dict:
    return json.loads(ATTRIBUTION.read_text()) if ATTRIBUTION.exists() else {}


def map_year(row: dict, attribution: dict) -> int | None:
    """The year the report will place this passage at, or None when the report
    leaves it out (spurious, undated, or after MAP_UNTIL)."""
    att = (attribution.get("passages") or {}).get(row["id"]) or (attribution.get("books") or {}).get(row["book"], {})
    if att.get("status") == "spurious":
        return None
    year = att.get("work_year") or row["year"]
    return year if year and year <= MAP_UNTIL else None


def split_candidates(best: list[int], rows: list[dict], attribution: dict) -> tuple[list[int], list[int]]:
    """Ranked pool -> (early, later). Slots go only to passages the map can show:
    up to 2*KEEP_EARLY by writers dated by EARLY_UNTIL, then up to KEEP_LATER
    dated EARLY_UNTIL+1..MAP_UNTIL. Undated and post-800 passages never take a slot."""
    years = {i: map_year(rows[i], attribution) for i in best}
    early = [i for i in best if years[i] and years[i] <= book_era.EARLY_UNTIL][:KEEP_EARLY * 2]
    later = [i for i in best if years[i] and years[i] > book_era.EARLY_UNTIL][:KEEP_LATER]
    return early, later


def q_search(only: set | None) -> int:
    tok = token()
    rows, mat = load_corpus()
    attribution = load_attribution()
    out = OUT / "q-candidates"
    out.mkdir(parents=True, exist_ok=True)
    for q in load_questions():
        if only and q["id"] not in only:
            continue
        qs = [q["question"]] + list(q.get("queries") or []) + list(q.get("shared_ground") or [])
        for p in q["positions"]:
            qs += [p["statement"], p["mark"]] + ([p["excluded_by"]] if p.get("excluded_by") else [])
        qv = np.concatenate([embed_queries(tok, qs[i:i + 32]) for i in range(0, len(qs), 32)])
        sims = mat @ qv.T
        pool = set()
        for j in range(sims.shape[1]):
            pool.update(np.argsort(-sims[:, j])[:PER_QUERY].tolist())
        pool = sorted(pool)
        scores = rerank(tok, q["question"] + " " + " ".join(q.get("queries") or [])[:400], [rows[i]["text"] for i in pool])
        best = sorted(zip(pool, scores), key=lambda x: -max(x[1], float(sims[x[0]].max())))
        early, later = split_candidates([i for i, _ in best], rows, attribution)
        (out / f"{q['id']}.json").write_text(json.dumps(
            [dict(rows[i], sim=round(float(sims[i].max()), 4)) for i in early + later], ensure_ascii=False, indent=1))
        print(f"search {q['id']}: {len(pool)} pooled -> {len(early)} early + {len(later)} later", flush=True)
    return 0


def _q_norm(obj, n: int) -> dict | None:
    """Labelled verdicts -> {position index: verdict}, or None when malformed."""
    if not isinstance(obj, dict) or not isinstance(obj.get("verdicts"), dict):
        return None
    out = {}
    for label, v in obj["verdicts"].items():
        k = "ABCDEFGH".find(str(label).strip()[:1].upper())
        if 0 <= k < n and isinstance(v, dict) and str(v.get("verdict", "")).lower() in VERDICTS:
            out[k] = {"verdict": str(v["verdict"]).lower(), "quote": str(v.get("quote") or "")[:400],
                      "why": str(v.get("why") or "")[:300]}
    return {"on": bool(obj.get("on_question", True)), "v": out} if len(out) == n else None


def broker_payload(model: str, system: str, user: str, max_tokens: int) -> dict | None:
    """The ai/run payload cf_call would send for this model, or None when the
    model cannot go through the broker (NIM, chat api, not batch-capable)."""
    model = LB.normalize_model(model)
    if LB.is_nvidia_model(model) or not any(k in model for k in LB.BATCH_MODELS):
        return None
    prof = LB.cf_profile(model)
    if prof.get("api", "run") != "run":
        return None
    payload = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
               "temperature": float(prof.get("temperature", 0.0))}
    payload["max_completion_tokens" if prof.get("use_max_completion_tokens") else "max_tokens"] = int(max_tokens)
    if prof.get("enable_thinking") is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": prof["enable_thinking"]}
    if prof.get("reasoning_effort") is not None:
        payload["reasoning_effort"] = prof["reasoning_effort"]
    return payload


def grade_call(model: str, system: str, user: str, max_tokens: int = 3000) -> dict | None:
    """W.call, but batch-capable models go through the batch broker only.
    Falls back to W.call (direct, paced by vendor_call) when the broker is down
    or keeps failing, so a dead broker never stops grading."""
    payload = broker_payload(model, system, user, max_tokens) if BATCH_ONLY else None
    if payload is None or not LB._broker_up():
        return W.call(model, system, user, max_tokens=max_tokens)
    last = ""
    for wait in (15, 60, 0):
        try:
            out = LB._broker_run(LB.normalize_model(model), payload)
        except Exception as e:  # noqa: BLE001
            out = {"error": f"broker: {e}"}
        content = LB._cf_pick_content(out["result"]) if out.get("result") is not None else None
        if content is not None:
            obj = W.work_read.parse_obj(content)
            if obj is not None:
                return obj
            last = "unparseable: " + content[:120]
        else:
            last = str(out.get("error") or "empty broker result")[:200]
        if wait:
            time.sleep(wait)
    print(f"grade_call {model} broker failed ({last}); going direct", file=sys.stderr, flush=True)
    return W.call(model, system, user, max_tokens=max_tokens)


def q_grade_one(q: dict, c: dict) -> dict:
    import random
    n = len(q["positions"])
    order = list(range(n))
    random.Random(c["id"]).shuffle(order)          # fixed per passage, different across passages
    user = q_prompt(q, order, c["text"])
    raw = {}

    def ask(m):
        r = _q_norm(grade_call(m, Q_SYS, user, max_tokens=3000), n)
        if not r:
            return None
        # labels -> real position ids
        return {"on": r["on"], "v": {q["positions"][order[k]]["id"]: v for k, v in r["v"].items()}}

    with ThreadPoolExecutor(max_workers=2) as ex:
        for m, r in zip(CHECKERS, ex.map(ask, CHECKERS)):
            if r:
                raw[m] = r
    pids = [p["id"] for p in q["positions"]]
    split = len(raw) < 2 or any(len({raw[m]["v"][pid]["verdict"] for m in raw}) > 1 for pid in pids)
    if split:
        r = ask(W.REFEREE)
        if r:
            raw[W.REFEREE] = r
    if len(raw) < 2:   # one vote or none is not a verdict; retry next run rather than store "disputed"
        raise RuntimeError(f"only {len(raw)} grader answered")
    final = {}
    for pid in pids:
        vs = [raw[m]["v"][pid]["verdict"] for m in raw]
        top = max(set(vs), key=vs.count) if vs else None
        verdict = top if top and vs.count(top) >= 2 else "disputed"
        quote = next((raw[m]["v"][pid]["quote"] for m in raw if raw[m]["v"][pid]["verdict"] == verdict
                      and raw[m]["v"][pid]["quote"]), "")
        final[pid] = {"verdict": verdict, "quote": quote, "agreement": f"{vs.count(top) if top else 0}/{len(vs)}"}
    on = [raw[m]["on"] for m in raw]
    return {"id": c["id"], "on_question": on.count(True) >= max(1, len(on) // 2 + (len(on) % 2)),
            "positions": final, "votes": raw}


def q_grade(only: set | None, workers: int) -> int:
    token()
    W.receipts_ok(CHECKERS + [W.REFEREE], "doctrine-grade")
    gdir = OUT / "q-grades"
    gdir.mkdir(parents=True, exist_ok=True)
    failed = 0
    for q in load_questions():
        if only and q["id"] not in only:
            continue
        cpath = OUT / "q-candidates" / f"{q['id']}.json"
        if not cpath.exists():
            continue
        cands = json.loads(cpath.read_text())
        gpath = gdir / f"{q['id']}.json"
        have = json.loads(gpath.read_text()) if gpath.exists() else {}
        key = sha(json.dumps([q.get("question"), q.get("shared_ground"),
                              [(p["id"], p["statement"], p["mark"], p.get("excluded_by")) for p in q["positions"]]]))
        todo = [c for c in cands if (have.get(c["id"]) or {}).get("key") != key]
        print(f"grade {q['id']}: {len(todo)} of {len(cands)} to grade", flush=True)

        # Hardening: one passage that fails (a vendor error, a broker timeout)
        # is logged and left ungraded for the next run, so the other passages
        # still save. (The 2026-10-06 beliefs log that ends mid-traceback was
        # cut off by the disk-full event, not by this; an ordinary exception
        # here already made run-doctrine-map.sh print "grade FAILED".)
        def run(c):
            try:
                r = q_grade_one(q, c)
            except Exception as e:  # noqa: BLE001
                print(f"  grade error {q['id']} {c['id']}: {type(e).__name__}: {str(e)[:200]}", flush=True)
                return c["id"], None
            r["key"] = key
            return c["id"], r

        with ThreadPoolExecutor(max_workers=workers) as ex:
            for k, (cid, r) in enumerate(ex.map(run, todo), 1):
                if r is None:
                    failed += 1
                else:
                    have[cid] = r
                if k % 10 == 0 or k == len(todo):
                    gpath.write_text(json.dumps(have, ensure_ascii=False, indent=1))
    if failed:
        print(f"grade: {failed} passages failed and wait for the next run", flush=True)
        return 1
    return 0


# ---------------------------------------------------------------- audit loci
# Audit rows are keyed by passage id, and the id hashes the text, so a recert
# edit would orphan them. Each row also carries a stable locus (book, file,
# section, para) and the text it audited. The report matches an orphaned row to
# the current passage at the same locus only when the text changed by at most a
# light edit (difflib ratio >= CARRY_RATIO), and marks it carried.
AUDIT = OUT / "audit"
CARRY_RATIO = 0.9


def locus(row: dict) -> str:
    return f"{row['book']}|{row['file']}|{row['section']}|{row['para']}"


def text_ratio(a: str, b: str) -> float:
    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return m.ratio() if m.real_quick_ratio() >= CARRY_RATIO and m.quick_ratio() >= CARRY_RATIO else 0.0


def audit_backfill(rows: list[dict] | None = None) -> int:
    """Stamp locus and audited text on audit rows that lack them, from the
    corpus the audit was made against. Run before index rewrites the corpus.
    A file changed by its writer while we worked is left for the next run."""
    if not AUDIT.exists() or not (OUT / "corpus.jsonl").exists():
        return 0
    if rows is None:
        rows = [json.loads(x) for x in (OUT / "corpus.jsonl").read_text().splitlines()]
    by_id = {r["id"]: r for r in rows}
    stamped = 0
    for f in sorted(AUDIT.glob("*.json")):
        mtime = f.stat().st_mtime
        try:
            data = json.loads(f.read_text())
        except ValueError:
            continue
        n = 0
        for row in data if isinstance(data, list) else []:
            c = by_id.get(row.get("passage"))
            if c and not (row.get("locus") and row.get("text")):
                row.setdefault("locus", locus(c))
                row.setdefault("text", c["text"])
                n += 1
        if n and f.stat().st_mtime == mtime:
            tmp = f.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1))
            os.replace(tmp, f)
            stamped += n
    if stamped:
        print(f"audit: stamped locus on {stamped} rows", flush=True)
    return stamped


def load_audit(by_id: dict) -> tuple[dict, dict]:
    """(exact, by_locus): exact[(passage, position)] -> audit; by_locus[locus]
    -> [(audited text, position, audit)] for rows whose passage id is gone."""
    exact, by_locus = {}, {}
    for f in sorted(AUDIT.glob("*.json")) if AUDIT.exists() else []:
        for row in json.loads(f.read_text()):
            a = {"verdict": row["verdict"], "audited": row.get("reason", "")}
            exact[(row["passage"], row["position"])] = a
            if row["passage"] not in by_id and row.get("locus") and row.get("text"):
                by_locus.setdefault(row["locus"], []).append((row["text"], row["position"], a))
    return exact, by_locus


def carried_audit(c: dict, pid: str, by_locus: dict, cache: dict) -> dict | None:
    """Best orphaned audit at this passage's locus for this position, when its
    audited text is within a light edit of the current text."""
    best, best_r = None, 0.0
    for text, pos, a in by_locus.get(locus(c), []):
        if pos != pid:
            continue
        key = (c["id"], text)
        if key not in cache:
            cache[key] = text_ratio(text, c["text"])
        if cache[key] >= CARRY_RATIO and cache[key] > best_r:
            best, best_r = a, cache[key]
    return dict(best, carried=True) if best else None


def q_report() -> int:
    """Site data: per question, per position, the passages that state its mark
    or exclude it, and per writer what their own words decide."""
    rows, _ = load_corpus()
    by_id = {r["id"]: r for r in rows}
    # The corpus is as of the last index. A passage id hashes its exact words, so
    # a graded passage whose id is not in today's English quotes words the work
    # page no longer says (Amphilochius "Fire was kindled", 2026-10-06). It is
    # left out until the next index and grade see the new words.
    current = {r["id"] for r in paragraphs()}
    stale = []
    searched = {}
    for r in rows:
        if r["year"]:
            searched.setdefault((r["year"] - 1) // 100 + 1, set()).add(r["author"])
    # Attribution (from the audit): spurious works leave the map; doubtful works
    # and catena fragments stay with a note but never set an earliest date;
    # work_year replaces the writer's death year when the work is dated.
    attribution = load_attribution()
    audit_backfill(rows)
    audit, by_locus = load_audit(by_id)
    ratio_cache = {}
    out = []
    for q in load_questions():
        gpath = OUT / "q-grades" / f"{q['id']}.json"
        g = json.loads(gpath.read_text()) if gpath.exists() else {}
        passages = []
        for cid, r in g.items():
            c = by_id.get(cid)
            # A passage entry (a quotation inside a work: Cyril quoting Apollinaris)
            # overrides its book's entry, and may name the real speaker.
            att = ((attribution.get("passages") or {}).get(cid) or (attribution.get("books") or {}).get(c["book"], {})) if c else {}
            if not c or not r.get("on_question") or att.get("status") == "spurious":
                continue
            if cid not in current:
                stale.append(f"{q['id']}: {c['book']}/{c['section']}")
                continue
            year = att.get("work_year") or c["year"]
            if not year or year > MAP_UNTIL:
                continue
            # Audit verdicts (Claude 4.5+, outputs/doctrine-map/audit/) override the graders.
            # An audit of this locus before a light text edit is carried (marked so),
            # but only when the graders of the current text reach the same verdict:
            # an audit of other words never overrides or certifies on its own.
            pos = {}
            for pid, v in r["positions"].items():
                a = audit.get((cid, pid))
                if a is None and by_locus:
                    a = carried_audit(c, pid, by_locus, ratio_cache)
                    if a and a["verdict"] != v["verdict"]:
                        a = None
                pos[pid] = dict(v, **(a or {}), reviewed=a is not None)
            decided = {pid: v for pid, v in pos.items() if v["verdict"] in ("states", "excludes", "disputed")}
            if not decided:
                continue  # on the question but decides nothing: shared ground only
            passages.append({"year": year, "author": att.get("author") or c["author"], "book": c["book"], "file": c["file"],
                             "section": c["section"], "text": c["text"][:900], "positions": decided,
                             "attribution": att.get("status"), "attribution_note": att.get("note")})
        passages.sort(key=lambda p: (p["year"] or 9999, p["author"]))
        positions = []
        for p in q["positions"]:
            st = [x for x in passages if (x["positions"].get(p["id"]) or {}).get("verdict") == "states"]
            # Only a reviewed verdict can set the earliest date (spec: audit step).
            st_rev = [x for x in st if (x["positions"][p["id"]] or {}).get("reviewed") and not x.get("attribution")]
            ex = [x for x in passages if (x["positions"].get(p["id"]) or {}).get("verdict") == "excludes"]
            positions.append({k: p.get(k) for k in ("id", "name", "traditions", "rejected_by", "defined",
                                                   "statement", "mark", "first_defined")}
                             | {"first_states": st_rev[0] if st_rev else None,
                                "first_uncertain": next((x for x in st if x["positions"][p["id"]].get("reviewed")), None)
                                if not st_rev else None,
                                "states": len(st), "excludes": len(ex)})
        out.append({"id": q["id"], "question": q["question"], "shared_ground": q.get("shared_ground"),
                    "positions": positions, "passages": passages,
                    "on_question": sum(1 for r in g.values() if r.get("on_question"))})
    data = {"generated": time.strftime("%Y-%m-%d"),
            "searched": {str(k): sorted(v) for k, v in sorted(searched.items())}, "questions": out}
    SITE_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"report: {len(out)} questions -> {SITE_DATA}", flush=True)
    if stale:
        print(f"report: left out {len(stale)} graded passages whose English has changed since the index:", flush=True)
        for s in sorted(set(stale)):
            print(f"  {s}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["index", "search", "grade", "report", "audit-locus"])
    ap.add_argument("--only", default="", help="comma-separated question ids")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    only = set(filter(None, a.only.split(","))) or None
    return {"index": index, "search": lambda: q_search(only), "grade": lambda: q_grade(only, a.workers),
            "report": q_report, "audit-locus": lambda: (audit_backfill(), 0)[1]}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
