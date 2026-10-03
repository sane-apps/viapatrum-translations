#!/usr/bin/env python3
"""Via Patrum health watch (owner 2026-10-03: monitor work, avoid previous
failure modes, watch for new ones). One snapshot per run; compares with the
last snapshot in outputs/health/state.json and prints ALERT lines for anything
wrong, EVENT lines for milestones. Exit 1 when there is an ALERT or EVENT.

Failure modes it watches (each seen on 2026-10-02/03):
- lanes dead or not progressing (crashed lanes, stale queue rows)
- 429 throttles rising (shared paid checker, no pacing)
- batch broker down or erroring
- narration stalled (paused by a long ship)
- a ship running for hours (slow upload) or failing (catalogue gate)
- disk low (ship staging filled the disk once), memory pressure
- status-site deploy failing (launchd PATH without npx)
- an orphan holding the ship lock after a stopped ship
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

H = Path.home()
T = H / "SaneApps/clients/translations"
SITE = H / "SaneApps/websites/fathers.saneapps.com"
STATE = T / "outputs/health/state.json"
now = time.time()
alerts, events, snap = [], [], {"t": now}


def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()


prev = json.loads(STATE.read_text()) if STATE.exists() else {}

# lanes
pids = list((T / "outputs/work-pipeline").glob("lane-*.pid"))
alive = 0
for f in pids:
    try:
        os.kill(int(f.read_text().strip()), 0)
        alive += 1
    except (OSError, ValueError):
        pass
snap["lanes_alive"] = alive
if alive < 12:
    alerts.append(f"only {alive}/15 lanes alive")
q = json.loads((T / "outputs/work-pipeline/queue.json").read_text())
done = sum(1 for v in q.values() if v.get("result") in ("certified", "held", "checked"))
snap["queue_done"] = done
snap["certified"] = sum(1 for v in q.values() if v.get("result") == "certified")
if prev and now - prev.get("progress_t", now) > 3 * 3600 and done <= prev.get("queue_done", 0):
    alerts.append("no lane finished a work in 3 hours")
snap["progress_t"] = now if done > prev.get("queue_done", -1) else prev.get("progress_t", now)

# throttles
thr = 0
for f in Path("/tmp/vendor-rate").glob("*.json"):
    try:
        thr += json.loads(f.read_text() or "{}").get("throttles", 0)
    except ValueError:
        pass
snap["throttles"] = thr
if prev and thr - prev.get("throttles", thr) > 25:
    alerts.append(f"429 throttles rose by {thr - prev['throttles']} since last check")

# broker
try:
    st = json.loads(urllib.request.urlopen("http://127.0.0.1:8799/stats", timeout=5).read())
    snap["broker_errors"] = st.get("errors", 0)
    if prev and st.get("errors", 0) - prev.get("broker_errors", 0) > 10:
        alerts.append(f"batch broker errors rose by {st['errors'] - prev['broker_errors']}")
except Exception:  # noqa: BLE001
    alerts.append("batch broker not answering on 127.0.0.1:8799")

# narration
log = H / "Library/Logs/SaneApps/fathers-audio-next.out.log"
rendered = sh(f"grep -c '^rendered' '{log}'")
snap["audio_rendered"] = int(rendered or 0)
if prev and snap["audio_rendered"] == prev.get("audio_rendered") and now - prev.get("audio_t", now) > 5400:
    alerts.append("narration rendered nothing for 90 minutes")
snap["audio_t"] = now if snap["audio_rendered"] != prev.get("audio_rendered") else prev.get("audio_t", now)

# ships
ship = sh("ps -Ao etime,command | grep 'scripts/ship.sh' | grep -v grep | head -1")
if ship:
    et = ship.split()[0]
    parts = [int(x) for x in re.split(r"[-:]", et)]
    secs = sum(v * m for v, m in zip(reversed(parts), (1, 60, 3600, 86400)))
    snap["ship_secs"] = secs
    if secs > 4 * 3600:
        alerts.append(f"a ship has run {secs // 3600} h (slow upload?)")
# A process left holding the ship lock with no ship running blocks every
# later ship (2026-10-03: an orphaned check_links.py from a stopped ship).
holders = sh(f"lsof -t '{SITE}/outputs/ship.lock' 2>/dev/null").split()
if holders and not ship:
    alerts.append("ship lock held with no ship running (orphan pid " + ",".join(holders) + ")")
for lg in (SITE / "outputs/ship-beliefs.log", H / "SaneApps/outputs/fathers-overnight/ship-auto.log"):
    if lg.exists() and now - lg.stat().st_mtime < 1800:
        tail = sh(f"tail -c 4000 '{lg}'")
        if re.search(r"BLOCKED|Traceback|AssertionError|FAILED", tail) and "SHIP OK" not in tail:
            alerts.append(f"ship problem in {lg.name}: " + re.findall(r"(BLOCKED[^\n]*|AssertionError[^\n]*|FAILED[^\n]*)", tail)[-1][:160])

# disk, memory
free_gb = int(sh("df -g / | awk 'NR==2{print $4}'") or 0)
snap["disk_free_gb"] = free_gb
if free_gb < 15:
    alerts.append(f"disk low: {free_gb} GB free")
mp = sh("memory_pressure | tail -1")
m = re.search(r"(\d+)%", mp)
if m and int(m.group(1)) < 8:
    alerts.append(f"memory free only {m.group(1)}%")

# status site deploy
sl = T / "outputs/work-pipeline/status-site.log"
if sl.exists() and "FAILED" in sh(f"tail -3 '{sl}'"):
    alerts.append("status site deploy failing")

# milestone: Beliefs live
try:
    # The zone's bot protection answers Python's default User-Agent with 403.
    req = urllib.request.Request("https://viapatrum.org/beliefs/", headers={"User-Agent": "viapatrum-health-watch"})
    with urllib.request.urlopen(req, timeout=15) as r:
        live = r.status == 200 and "Where did this belief come from" in r.read(200000).decode("utf-8", "replace")
except Exception:  # noqa: BLE001
    live = False
snap["beliefs_live"] = live
if live and not prev.get("beliefs_live"):
    events.append("Beliefs is live at https://viapatrum.org/beliefs/")

STATE.parent.mkdir(parents=True, exist_ok=True)
STATE.write_text(json.dumps(snap))
print(time.strftime("%H:%M"), json.dumps({k: v for k, v in snap.items() if k != "t"}))
for a in alerts:
    print("ALERT", a)
for e in events:
    print("EVENT", e)
sys.exit(1 if alerts or events else 0)
