#!/usr/bin/env python3
"""Owner status site for Via Patrum: what is certified, what was done to each
work and when (from outputs/audit/events.jsonl), and where audio is missing.

Builds outputs/status-site/ (index.html + works/<slug>.html). The 30-minute
recert tick (scripts/run-recert-lanes.sh) rebuilds and deploys it to the
private Pages project viapatrum-status (Cloudflare Access, owner only).
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
SITE = HOME / "SaneApps/websites/fathers.saneapps.com"
TR = HOME / "SaneApps/clients/translations"
OUT = TR / "outputs" / "status-site"
sys.path.insert(0, str(SITE / "scripts"))
sys.path.insert(0, str(TR / "scripts"))
from build_site import work_book, PUBLIC_ENGLISH_TITLES  # noqa: E402
import audit_log  # noqa: E402
import work_pipeline as wp  # noqa: E402

E = html.escape
KIND_LABEL = {"certified": "Certified", "held": "Held", "recheck": "Re-check", "translated": "New translation certified",
              "citation": "Bible reference", "repair": "Text repair", "title": "Title", "audio": "Audio",
              "shipped": "Shipped", "note": "Note"}
KIND_CLASS = {"certified": "good", "translated": "good", "held": "warn", "citation": "idle", "repair": "idle",
              "title": "idle", "audio": "idle", "shipped": "good", "recheck": "idle", "note": "idle"}

CSS = """
:root {
  --bg: #f6f7f9; --panel: #ffffff; --ink: #1c2330; --muted: #5b6577; --line: #dde1e8;
  --accent: #7a5c1e; --good: #2f7a4f; --good-bg: #e3f2e8; --warn: #9a6a12; --warn-bg: #fbf0d9;
  --bad: #a3392f; --bad-bg: #f8e3e0; --idle: #6b7486; --idle-bg: #eceff3;
  --display: "Literata", Georgia, serif; --body: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light;
}
@media (prefers-color-scheme: dark) { :root {
  --bg: #12161d; --panel: #1a2029; --ink: #e6e9ef; --muted: #9aa3b2; --line: #2b3340;
  --accent: #d9b56a; --good: #7fd09c; --good-bg: #1d3326; --warn: #e8bd63; --warn-bg: #3a2f19;
  --bad: #f0958b; --bad-bg: #3d2220; --idle: #a2abba; --idle-bg: #252c37; color-scheme: dark } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.5 var(--body); }
a { color: var(--ink); }
.wrap { max-width: 1080px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 48px; display: grid; gap: 22px; }
h1 { font: 650 30px/1.15 var(--display); margin: 0; text-wrap: balance; }
h2 { font: 650 20px/1.2 var(--display); margin: 0; }
.sub { color: var(--muted); margin: 4px 0 0; }
.sum { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.tile { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 6px; }
.tile b { font: 650 28px/1 var(--display); font-variant-numeric: tabular-nums; }
.tile span { color: var(--muted); font-size: 13px; }
.bar { height: 6px; border-radius: 3px; background: var(--idle-bg); overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--good); }
.key { color: var(--muted); font-size: 13px; display: flex; flex-wrap: wrap; gap: 10px 18px; }
.controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.controls input { flex: 1 1 220px; min-width: 0; font: inherit; padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); }
.seg { display: flex; flex-wrap: wrap; gap: 6px; }
.seg button { font: 500 13px var(--body); padding: 7px 11px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); cursor: pointer; }
.seg button[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
button:focus-visible, input:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.table { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 640px; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font: 600 12px var(--body); letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
tr:last-child td { border-bottom: 0; }
td small, .meta { display: block; color: var(--muted); font: 12px var(--mono); }
td.n { font: 13px var(--mono); font-variant-numeric: tabular-nums; color: var(--muted); white-space: nowrap; }
.chip { display: inline-block; font: 600 12px var(--body); padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.good { color: var(--good); background: var(--good-bg); } .warn { color: var(--warn); background: var(--warn-bg); }
.bad { color: var(--bad); background: var(--bad-bg); } .idle { color: var(--idle); background: var(--idle-bg); }
.feed { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; }
.ev { display: grid; grid-template-columns: 148px 1fr; gap: 4px 14px; padding: 10px 14px; border-bottom: 1px solid var(--line); }
.ev:last-child { border-bottom: 0; }
.ev time { font: 12px var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.ev p { margin: 0; min-width: 0; overflow-wrap: anywhere; }
@media (max-width: 560px) { .ev { grid-template-columns: 1fr; } }
footer { color: var(--muted); font-size: 13px; }
"""
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,650'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap">')


def page(title: str, body: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">'
            f'<title>{E(title)}</title>{FONTS}<style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>')


def event_html(ev: dict, show_book: bool) -> str:
    when = ev["at"].replace("T", " ")[:16] + (" ~" if (ev.get("detail") or {}).get("approx") else "")
    chip = f'<span class="chip {KIND_CLASS.get(ev["kind"], "idle")}">{E(KIND_LABEL.get(ev["kind"], ev["kind"]))}</span>'
    book = ""
    if show_book and ev["book"] and ev["book"] != "*":
        book = f' <a href="works/{E(ev["book"])}.html">{E(ev["book"])}</a>'
    ref = f'<span class="meta">{E(ev.get("ref", ""))}</span>' if ev.get("ref") else ""
    return f'<div class="ev"><time>{E(when)}</time><p>{chip}{book} {E(ev["summary"])}{ref}</p></div>'


def scout_section() -> str:
    """Cloudflare capability scout (SaneProcess outputs/cf-scout/latest.json)."""
    path = HOME / "SaneApps/infra/SaneProcess/outputs/cf-scout/latest.json"
    try:
        r = json.loads(path.read_text())
    except (OSError, ValueError):
        return ""
    rows = []
    for m in r.get("in_use_deprecating", []):
        rows.append(f'<div class="ev"><time>deprecating</time><p><span class="chip bad">We use it</span> '
                    f'<code>{E(m["name"])}</code> retires {E(str(m.get("deprecated")))}</p></div>')
    for n in r.get("in_use_missing", []):
        rows.append(f'<div class="ev"><time>missing</time><p><span class="chip bad">We use it</span> <code>{E(n)}</code> left the catalog</p></div>')
    for m in r.get("new_models", []):
        rows.append(f'<div class="ev"><time>new model</time><p><span class="chip good">New</span> <code>{E(m["name"])}</code> '
                    f'{E(m.get("task") or "")}: {E((m.get("description") or "")[:160])}</p></div>')
    for n in r.get("relevant_changelog", [])[:12]:
        rows.append(f'<div class="ev"><time>{E(n["date"])}</time><p><span class="chip idle">{E(n["products"][:40])}</span> '
                    f'<a href="{E(n["link"])}">{E(n["title"])}</a></p></div>')
    if not rows:
        rows.append('<div class="ev"><time>&nbsp;</time><p>Nothing new that touches our work since the last scan.</p></div>')
    untried = r.get("not_tried_text_models") or []
    extra = (f'<p class="sub">Text models available that we have not tried: {len(untried)} '
             f'(weekly list in SaneProcess outputs/cf-scout).</p>') if untried else ""
    return (f'<h2>Cloudflare: what\'s new</h2><p class="sub">Scanned {E(r.get("run", ""))}, nightly at 06:15.</p>'
            f'<div class="feed">{"".join(rows)}</div>{extra}')


def main() -> int:
    events = audit_log.events()
    by_book = defaultdict(list)
    for ev in events:
        by_book[ev["book"]].append(ev)
    queue = json.loads(wp.QUEUE_LOG.read_text()) if wp.QUEUE_LOG.exists() else {}
    # audio coverage from the latest ship log lines
    audio = {}
    logs = sorted([p for p in (SITE / "outputs").glob("ship-*.log")] + [HOME / "SaneApps/outputs/fathers-overnight/ship-auto.log"],
                  key=lambda p: p.stat().st_mtime if p.exists() else 0)
    for lg in logs:
        if lg.exists():
            for m in re.finditer(r"work (\S+): (\d+) tracked sentences, (\d+) reader passages, (\d+) unmatched",
                                 lg.read_text(errors="replace")):
                audio[m.group(1)] = int(m.group(4))
    rows = []
    for d in sorted((SITE / "dist/works").iterdir()):
        if not d.is_dir():
            continue
        slug = d.name
        book = slug if (wp.BOOKS / slug).is_dir() else (work_book(slug) or slug)
        try:
            cert = wp.certified(book)
        except Exception:
            cert = False
        q = queue.get(book, {})
        hist = by_book.get(book, [])
        rows.append({"slug": slug, "book": book, "title": PUBLIC_ENGLISH_TITLES.get(slug, slug), "certified": cert,
                     "queue": q.get("result", "waiting"), "followability": (q.get("status") or {}).get("followability"),
                     "words": q.get("words"), "audio_missing": audio.get(slug), "events": len(hist),
                     "last": hist[-1]["at"][:16].replace("T", " ") if hist else ""})
    live_books = {r["book"] for r in rows}
    new_books = sorted(b for b, v in queue.items() if b not in live_books)
    totals = {"live": len(rows), "certified": sum(r["certified"] for r in rows),
              "held": sum(1 for r in rows if r["queue"] == "held" and not r["certified"]),
              "audio_full": sum(1 for r in rows if r["audio_missing"] == 0),
              "new_certified": sum(1 for b in new_books if queue[b].get("result") == "certified"),
              "events": len(events)}
    generated = time.strftime("%Y-%m-%d %H:%M")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "works").mkdir(exist_ok=True)

    # per-work pages
    titles = {r["book"]: r for r in rows}
    for book in set(by_book) | live_books | set(new_books):
        if book in ("*", ""):
            continue
        r = titles.get(book, {"title": book, "slug": "", "certified": False, "queue": queue.get(book, {}).get("result", "waiting")})
        hist = list(reversed(by_book.get(book, [])))
        state = "Certified" if r.get("certified") else {"held": "Held", "running": "Checking now"}.get(r.get("queue"), "Waiting")
        cls = "good" if r.get("certified") else ("warn" if r.get("queue") in ("held", "running") else "idle")
        live = f'<a href="https://viapatrum.org/works/{E(r["slug"])}/">Open on viapatrum.org</a>' if r.get("slug") else "Not live yet"
        body = (f'<header><p class="sub"><a href="../index.html">All works</a></p><h1>{E(r["title"])}</h1>'
                f'<p class="sub"><span class="chip {cls}">{state}</span> &nbsp;{live} &nbsp;<span class="meta">{E(book)}</span></p></header>'
                f'<h2>History</h2><div class="feed">' + ("".join(event_html(ev, False) for ev in hist)
                                                         or '<p class="ev">Nothing recorded yet.</p>') + '</div>'
                f'<footer>Times are Mini local time; "~" marks a time taken from the receipt file. Updated {generated}.</footer>')
        (OUT / "works" / f"{book}.html").write_text(page(r["title"], body), encoding="utf-8")

    # index
    data = json.dumps({"works": rows}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pct = round(100 * totals["certified"] / max(1, totals["live"]))
    recent = "".join(event_html(ev, True) for ev in list(reversed(events))[:60])
    scout_html = scout_section()
    body = f"""
<header><h1>Via Patrum status</h1><p class="sub">Updated {generated} (Mini time), rebuilt every 30 minutes from the audit log.</p></header>
<section class="sum">
  <div class="tile"><b>{totals['certified']} / {totals['live']}</b><span>live works certified</span><div class="bar"><i style="width:{pct}%"></i></div></div>
  <div class="tile"><b>{totals['held']}</b><span>held for a second look</span></div>
  <div class="tile"><b>{totals['audio_full']}</b><span>works with full audio</span></div>
  <div class="tile"><b>{totals['new_certified']}</b><span>new translations certified</span></div>
  <div class="tile"><b>{totals['events']:,}</b><span>recorded changes</span></div>
</section>
<div class="key">
  <span><span class="chip good">Certified</span> every section checked against the Greek or Latin by two independent models, intro checked, readers passed</span>
  <span><span class="chip warn">Held</span> checked; part still disputed, current text stays live</span>
  <span><span class="chip idle">Waiting</span> not re-checked yet</span>
</div>
<div class="controls">
  <input id="q" type="search" placeholder="Find a work or Father" aria-label="Find a work">
  <div class="seg" id="seg">
    <button data-f="all" aria-pressed="true">All</button><button data-f="certified" aria-pressed="false">Certified</button>
    <button data-f="held" aria-pressed="false">Held</button><button data-f="waiting" aria-pressed="false">Waiting</button>
    <button data-f="audio" aria-pressed="false">Audio gaps</button>
  </div>
</div>
<div class="table"><table><thead><tr><th>Work</th><th>Source check</th><th>Audio</th><th>History</th></tr></thead><tbody id="rows"></tbody></table></div>
{scout_html}
<h2>Recent activity</h2><div class="feed">{recent}</div>
<h2>New translations</h2><p class="sub">{len(new_books)} started in the pipeline, {totals['new_certified']} certified:
{", ".join(f'<a href="works/{E(b)}.html">{E(b)}</a>' for b in new_books if queue[b].get("result") == "certified") or "none yet"}.</p>
<footer>Before 2026-10-02, 158 live works carried only a ticked-box receipt and 69 had no review at all.</footer>
<script id="data" type="application/json">{data}</script>
<script>
const W = JSON.parse(document.getElementById('data').textContent).works;
const st = w => w.certified ? 'certified' : (w.queue === 'held' ? 'held' : (w.queue === 'running' ? 'running' : 'waiting'));
let filter = 'all', query = '';
function render() {{
  const q = query.trim().toLowerCase();
  const list = W.filter(w => {{
    if (q && !(w.title + ' ' + w.slug).toLowerCase().includes(q)) return false;
    const s = st(w);
    if (filter === 'certified') return s === 'certified';
    if (filter === 'held') return s === 'held';
    if (filter === 'waiting') return s === 'waiting' || s === 'running';
    if (filter === 'audio') return w.audio_missing !== 0;
    return true;
  }}).sort((a, b) => (b.certified - a.certified) || a.title.localeCompare(b.title));
  document.getElementById('rows').innerHTML = list.length ? list.map(w => {{
    const s = st(w);
    const chip = s === 'certified' ? '<span class="chip good">Certified</span>' : s === 'held' ? '<span class="chip warn">Held</span>'
      : s === 'running' ? '<span class="chip warn">Checking now</span>' : '<span class="chip idle">Waiting</span>';
    const fol = (w.followability || []).length ? `<small>readers ${{w.followability.join(' / ')}} of 5</small>` : '';
    const au = w.audio_missing === 0 ? '<span class="chip good">Full</span>' : w.audio_missing == null ? '<span class="chip bad">None</span>'
      : `<span class="chip warn">${{w.audio_missing}} missing</span>`;
    const h = w.events ? `${{w.events}} changes<small>last ${{w.last}}</small>` : '<small>none yet</small>';
    return `<tr><td><a href="works/${{w.book}}.html">${{w.title}}</a><small>${{w.slug}}</small></td><td>${{chip}}${{fol}}</td><td>${{au}}</td><td class="n">${{h}}</td></tr>`;
  }}).join('') : '<tr><td colspan="4">No works match.</td></tr>';
}}
document.getElementById('q').addEventListener('input', e => {{ query = e.target.value; render(); }});
document.getElementById('seg').addEventListener('click', e => {{
  const b = e.target.closest('button'); if (!b) return; filter = b.dataset.f;
  document.querySelectorAll('#seg button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); render();
}});
render();
</script>"""
    (OUT / "index.html").write_text(page("Via Patrum Status", body), encoding="utf-8")
    (OUT / "status.json").write_text(json.dumps({"generated": generated, "totals": totals, "works": rows}, ensure_ascii=False))
    print(json.dumps(totals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
