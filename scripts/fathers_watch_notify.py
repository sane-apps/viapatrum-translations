#!/usr/bin/env python3
"""Air-side Fathers Watch notifier + status viewer.

Runs every 15 min on the Air via launchd (com.saneapps.fathers-watch-notify):
fetches the Mini watch status.json, compares alert ids against local
notified state, and posts a macOS notification ONLY on new problems and
recoveries. Silent when green and unchanged.

  fathers_watch_notify.py           # notify pass (launchd)
  fathers_watch_notify.py --status  # print one-line + detail summary

A status.json older than STALE_MIN means the Mini watch is unloaded or stuck
and cannot say so itself; that becomes the alert watch:stale (2026-10-06:
the watch was unloaded 06:15-12:20 and this notifier stayed silent).

Until 2026-10-06 this file lived only on the Air, untracked; the repo copy
is the source now.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MINI_STATUS = "SaneApps/clients/translations/outputs/fathers-watch/status.json"
STATE = Path.home() / ".local/state/fathers_watch_notified.json"
STALE_MIN = 30  # the Mini watch runs every 15 min


def stale_alert(status: dict, now: datetime | None = None) -> dict | None:
    """watch:stale when status.json was written more than STALE_MIN ago."""
    try:
        at = datetime.fromisoformat(str(status.get("checked_at")))
    except ValueError:
        return {"id": "watch:stale", "severity": "fail", "text": "Mini watch status.json has no checked_at"}
    age_min = int(((now or datetime.now(timezone.utc)) - at).total_seconds() // 60)
    if age_min <= STALE_MIN:
        return None
    return {"id": "watch:stale", "severity": "fail",
            "text": f"Mini fathers-watch last ran {age_min} min ago: it is unloaded or stuck, so nothing is being watched"}


def fetch_status() -> tuple[dict | None, str]:
    try:
        raw = subprocess.check_output(
            ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
             "mini", f"cat {MINI_STATUS}"],
            text=True, timeout=60)
        return json.loads(raw), ""
    except subprocess.TimeoutExpired:
        return None, "ssh to mini timed out"
    except subprocess.CalledProcessError as exc:
        return None, f"ssh failed rc={exc.returncode}"
    except (OSError, ValueError) as exc:
        return None, str(exc)


def notify(title: str, body: str) -> None:
    body = body.replace('"', "'")[:400]
    subprocess.run(["osascript", "-e",
                    f'display notification "{body}" with title "{title}" '
                    'sound name "Blow"'],
                   capture_output=True, timeout=30)


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"notified": {}, "link_down_notified": False}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def one_line(status: dict) -> str:
    alerts = status.get("alerts", []) or []
    if not alerts:
        return f"GREEN checked={status.get('checked_at', '?')}"
    return ("RED " if status.get("overall") == "fail" else "YELLOW ") + "; ".join(
        f"{a['id']}: {a['text'][:100]}" for a in alerts)


def main() -> int:
    status, err = fetch_status()
    state = load_state()
    if status is None:
        if not state.get("link_down_notified"):
            notify("Fathers Watch: Mini unreachable",
                   f"Cannot fetch Mini watch status ({err}). Lanes may be fine; the link is down.")
            state["link_down_notified"] = True
            save_state(state)
        print(f"link down: {err}")
        return 0
    if state.get("link_down_notified"):
        notify("Fathers Watch: Mini reachable again",
               "Watch link recovered.")
        state["link_down_notified"] = False
    stale = stale_alert(status)
    if stale:
        status["alerts"] = [stale] + list(status.get("alerts") or [])
        status["overall"] = "fail"
    if "--status" in sys.argv:
        print(one_line(status))
        for name, c in (status.get("checks") or {}).items():
            print(f"  {name:10s} {c.get('state', '?'):4s} {c.get('detail', '')[:110]}")
        save_state(state)
        return 0
    notified: dict = state.get("notified", {})
    current = {a["id"]: a for a in (status.get("alerts") or [])}
    for aid, a in current.items():
        if aid not in notified:
            sev = "FAIL" if a.get("severity") == "fail" else "WARN"
            notify(f"Fathers {sev}: {aid}", a.get("text", aid))
            notified[aid] = datetime.now(timezone.utc).isoformat()
    for aid in [k for k in notified if k not in current]:
        notify("Fathers recovered", f"{aid} is green again.")
        del notified[aid]
    state["notified"] = notified
    save_state(state)
    print(one_line(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
