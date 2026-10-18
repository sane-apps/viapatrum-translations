#!/usr/bin/env python3
"""Daily Workers AI spending cap for every Via Patrum job (owner 2026-10-14:
"make sure theres no chance of credits burning. only useful work").

Spend is read from Cloudflare's GraphQL usage (aiInferenceAdaptiveGroups),
the same number the invoice uses, for the current UTC day (it resets at
8 PM ET). It counts the whole account, so lanes, narration and the beliefs
job share one cap. The read is free; it makes no inference call.

  spend_guard.py check       exit 0 under the cap, 10 over, 2 when usage is unknown
  spend_guard.py gate-lanes  for run-recert-lanes.sh: pauses lanes when over the
                             cap, lifts its own pause the next UTC day; exit 0 =
                             lanes may start, 1 = they may not
  spend_guard.py status      one line for people and fathers-watch
  spend_guard.py allow       the per-call gate (broker batches, review calls):
                             exit 0 = may spend, 10 = over the daily cap or the
                             hourly ceiling, 2 = usage unknown (refused)

Hourly ceiling (2026-10-14): spend in the current UTC hour may not pass
cap/12, so one night cannot use the whole day (the Oct 14 burn was $182 by
10 AM ET at up to $20/hour). allow() caches its answer for ALLOW_TTL_S so a
busy caller does not query GraphQL on every call.

Cap: outputs/spend/cap.json {"usd": N}, else FATHERS_DAILY_CAP_USD, else 150.
On 2026-10-14 the real burn was about $388/day and the grant had about
$5,500 left, enough for two weeks; at $150/day it lasts about five.
Unknown usage counts as over for starting new work (fail closed), but does
not pause lanes that are already running.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SPEND = ROOT / "outputs" / "spend"
TODAY = SPEND / "today.json"
CAP_FILE = SPEND / "cap.json"
LANES = ROOT / "outputs" / "work-pipeline"
PAUSED = LANES / "lanes.paused"
RESTART = LANES / "lanes.restart"
DEFAULT_CAP_USD = 150.0
FREE_NEURONS = 10_000  # per day, free
USD_PER_1K_NEURONS = 0.011
LANE_SHARE = 0.8  # lanes stop at 80% of the cap so narration and beliefs keep the rest
BUDGET_TAG = "budget:"  # first word of a pause this script wrote; an owner pause has none

HOURLY_FRACTION = 1 / 12  # hourly ceiling = cap * this
ALLOW_CACHE = SPEND / "allow.json"
ALLOW_TTL_S = 15
HOLD = SPEND / "hold"  # owner hold: while it exists every gated call refuses, whatever the spend
REFUSED_TAG = "spend guard refused"  # callers match this and must not fall back to a direct call
RESERVE_WINDOW_S = 300  # a reservation counts until Cloudflare's usage has caught up with it
# Conservative per-call estimates, USD (2026-10-16). Real spend 10-15..16 was
# about $0.005 per deepseek/glm/kimi call; these over-estimate on purpose so
# parallel workers cannot all start the call that crosses the line.
USD_PER_M_IN = 1.0
USD_PER_M_OUT = 4.0
USD_PER_1K_TTS_CHARS = 0.030  # Aura-2 (docs/GPU_RENDER_COSTS.md)
USD_EMBED_CALL = 0.001
_reserved: list = []  # (time, usd) reserved by this process


class SpendRefused(RuntimeError):
    """A gated Workers AI call was refused. Do not fall back to another paid path."""

OVER, UNKNOWN, OK = 10, 2, 0


def hourly_ceiling_usd(cap: float) -> float:
    return cap * HOURLY_FRACTION


def _token() -> str:
    return os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_TOKEN") or ""


def neurons_this_hour(token: str, account: str) -> int:
    from overnight_quota import gql
    end = datetime.now(timezone.utc)
    start = end.replace(minute=0, second=0, microsecond=0)
    q = ('query { viewer { accounts(filter: {accountTag: "%s"}) { aiInferenceAdaptiveGroups(limit: 1, '
         'filter: {datetime_geq: "%s", datetime_lt: "%s"}) { sum { totalNeurons } } } } }'
         % (account, start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")))
    data = gql(token, q)
    if data.get("errors"):
        raise SystemExit(f"GraphQL hourly neurons error: {data['errors']}")
    groups = (((data.get("data") or {}).get("viewer") or {}).get("accounts") or [{}])[0].get(
        "aiInferenceAdaptiveGroups") or []
    return int(((groups[0].get("sum") or {}).get("totalNeurons")) or 0) if groups else 0


# A usage read that fails is retried before it counts as unknown (2026-10-18:
# one GraphQL 502 at 05:44 refused a grade call and killed a 2 h beliefs grade
# run). Still fail closed when every attempt fails.
READ_RETRY_SLEEPS_S = (2, 6)


def _with_retries(read):
    import time
    for pause in READ_RETRY_SLEEPS_S:
        r = read()
        if "error" not in r or "no Cloudflare token" in r["error"]:
            return r
        time.sleep(pause)
    return read()


def read_hour_usage() -> dict:
    """Spend in the current UTC hour (no free-tier offset), or {'error': ...}. Never raises."""
    return _with_retries(_read_hour_usage_once)


def _read_hour_usage_once() -> dict:
    token = _token()
    if not token:
        return {"error": "no Cloudflare token in the environment"}
    try:
        from overnight_quota import DEFAULT_ACCOUNT
        n = neurons_this_hour(token, os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT)
    except (Exception, SystemExit) as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"[:300]}
    return {"neurons": n, "usd": round(n * USD_PER_1K_NEURONS / 1000, 2)}


def decide(day: dict, hour: dict, cap: float) -> tuple[bool, str]:
    """(may spend, why). Unknown usage refuses (fail closed)."""
    for name, u in (("daily", day), ("hourly", hour)):
        if "error" in u:
            return False, f"{name} usage unknown ({u['error']})"
    if day["usd"] >= cap:
        return False, f"over the daily cap: ${day['usd']:.2f} of ${cap:.0f} (UTC day)"
    ceiling = hourly_ceiling_usd(cap)
    if hour["usd"] >= ceiling:
        return False, f"over the hourly ceiling: ${hour['usd']:.2f} of ${ceiling:.2f} this UTC hour"
    return True, f"ok: ${day['usd']:.2f} of ${cap:.0f} today, ${hour['usd']:.2f} of ${ceiling:.2f} this hour"


def hold_reason() -> str:
    try:
        return "owner hold (outputs/spend/hold): " + (HOLD.read_text(errors="replace").strip()[:200] or "set")
    except OSError:
        return ""


def _status(caller: str = "") -> dict:
    """{ok, why, day, hour, cap}, cached ALLOW_TTL_S across processes; never raises."""
    import time
    try:
        c = json.loads(ALLOW_CACHE.read_text())
        if time.time() - float(c["t"]) < ALLOW_TTL_S and "day" in c:
            return c
    except (OSError, ValueError, KeyError, TypeError):
        pass
    day = hour = None
    try:
        du, hu = read_usage(), read_hour_usage()
        cap = cap_usd()
        ok, why = decide(du, hu, cap)
        day, hour = du.get("usd"), hu.get("usd")
    except Exception as e:  # noqa: BLE001  fail closed
        ok, why, cap = False, f"guard error {type(e).__name__}: {e}"[:300], DEFAULT_CAP_USD
    c = {"t": time.time(), "ok": ok, "why": why, "day": day, "hour": hour, "cap": cap, "caller": caller}
    try:
        SPEND.mkdir(parents=True, exist_ok=True)
        tmp = ALLOW_CACHE.with_suffix(".tmp.%d" % os.getpid())
        tmp.write_text(json.dumps(c))
        tmp.replace(ALLOW_CACHE)
    except OSError:
        pass
    return c


def allow(caller: str = "") -> tuple[bool, str]:
    """The per-call gate (no reservation). Owner hold first; never raises."""
    held = hold_reason()
    if held:
        return False, held
    c = _status(caller)
    return bool(c["ok"]), str(c["why"])


def estimate_usd(in_chars: int = 0, max_tokens: int = 0, tts_chars: int = 0, embed: bool = False) -> float:
    """Upper-bound guess of one call's cost."""
    usd = in_chars / 4 * USD_PER_M_IN / 1e6 + max_tokens * USD_PER_M_OUT / 1e6
    usd += tts_chars * USD_PER_1K_TTS_CHARS / 1000
    return usd + (USD_EMBED_CALL if embed else 0.0)


def reserve(caller: str, usd: float, now: float | None = None) -> tuple[bool, str]:
    """Pre-call reservation: refuse when today's or this hour's spend plus what
    this process reserved in the last RESERVE_WINDOW_S plus this call would
    reach the daily cap or the hourly ceiling. Never raises."""
    import threading
    import time
    held = hold_reason()
    if held:
        return False, held
    c = _status(caller)
    if not c.get("ok"):
        return False, str(c.get("why"))
    now = time.time() if now is None else now
    lock = globals().setdefault("_RES_LOCK", threading.Lock())
    with lock:
        _reserved[:] = [(t, u) for t, u in _reserved if now - t < RESERVE_WINDOW_S]
        pending = sum(u for _, u in _reserved)
        cap = float(c.get("cap") or DEFAULT_CAP_USD)
        day, hour = float(c.get("day") or 0), float(c.get("hour") or 0)
        if day + pending + usd >= cap:
            return False, (f"daily cap: ${day:.2f} spent + ${pending:.2f} reserved + ${usd:.3f} this call "
                           f"reaches ${cap:.0f}")
        ceiling = hourly_ceiling_usd(cap)
        if hour + pending + usd >= ceiling:
            return False, (f"hourly ceiling: ${hour:.2f} this hour + ${pending:.2f} reserved + ${usd:.3f} "
                           f"this call reaches ${ceiling:.2f}")
        _reserved.append((now, usd))
    return True, "reserved"


def gate(caller: str, usd: float) -> None:
    """reserve() or raise SpendRefused (message starts with REFUSED_TAG)."""
    ok, why = reserve(caller, usd)
    if not ok:
        raise SpendRefused(f"{REFUSED_TAG} ({caller}): {why}")


def cap_usd() -> float:
    try:
        return float(json.loads(CAP_FILE.read_text())["usd"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    try:
        return float(os.environ.get("FATHERS_DAILY_CAP_USD") or DEFAULT_CAP_USD)
    except ValueError:
        return DEFAULT_CAP_USD


def usd_of(neurons: int) -> float:
    return max(0, neurons - FREE_NEURONS) * USD_PER_1K_NEURONS / 1000


def read_usage() -> dict:
    """Today's spend, or {'error': ...}. Never raises."""
    return _with_retries(_read_usage_once)


def _read_usage_once() -> dict:
    token = _token()
    if not token:
        return {"error": "no Cloudflare token in the environment"}
    try:
        from overnight_quota import DEFAULT_ACCOUNT, neurons_today
        neurons = neurons_today(token, os.environ.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT)
    except (Exception, SystemExit) as e:  # noqa: BLE001 - a failed read is data, not a crash
        return {"error": f"{type(e).__name__}: {e}"[:300]}
    return {"neurons": neurons, "usd": round(usd_of(neurons), 2)}


def evaluate(usage: dict, cap: float, day: str) -> dict:
    row = {"date": day, "cap_usd": cap, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **usage}
    row["state"] = "unknown" if "error" in usage else ("over" if usage["usd"] >= cap else "ok")
    return row


def record(row: dict) -> None:
    SPEND.mkdir(parents=True, exist_ok=True)
    tmp = TODAY.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, indent=1))
    tmp.replace(TODAY)


def gate_lanes(row: dict) -> int:
    """Pause or un-pause the lanes for this row. Returns 0 when lanes may start."""
    pause = PAUSED.read_text().strip() if PAUSED.exists() else ""
    ours = pause.startswith(BUDGET_TAG)
    if row["state"] == "ok" and row["usd"] >= row["cap_usd"] * LANE_SHARE:
        row = {**row, "state": "over"}
    if row["state"] == "over":
        if not pause:
            PAUSED.write_text(f"{BUDGET_TAG} ${row['usd']:.0f} spent on {row['date']} (UTC), past the lanes' "
                              f"{LANE_SHARE:.0%} share of the ${row['cap_usd']:.0f} daily cap; "
                              "lanes resume after 00:00 UTC (8 PM ET)\n")
            RESTART.touch()  # running lanes exit between works
            print(f"spend: ${row['usd']:.2f} is past the lanes' share of ${row['cap_usd']:.0f}; lanes paused")
        return 1
    if ours and row["state"] == "ok":
        PAUSED.unlink(missing_ok=True)
        print(f"spend: ${row['usd']:.2f} of ${row['cap_usd']:.0f} today; budget pause lifted")
    if row["state"] == "unknown":
        print(f"spend: usage unknown ({row['error']}); no new lanes this tick")
        return 1
    return 1 if PAUSED.exists() else 0


def line(row: dict) -> str:
    if row.get("state") == "unknown":
        return f"spend unknown at {row.get('at')}: {row.get('error')}"
    return f"spend {row.get('date')}: ${row.get('usd', 0):.2f} of ${row.get('cap_usd', 0):.0f} cap ({row.get('state')})"


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "status":
        try:
            print(line(json.loads(TODAY.read_text())))
        except (OSError, ValueError):
            print("spend: no reading yet")
        return 0
    if cmd in ("check", "allow", "gate-lanes") and hold_reason():
        print(f"refused: {hold_reason()}")
        if cmd == "gate-lanes":
            return 1
        return OVER
    if cmd == "allow":
        ok, why = allow("cli")
        print(("allowed: " if ok else "refused: ") + why)
        return OK if ok else (UNKNOWN if "unknown" in why or "error" in why else OVER)
    if cmd not in ("check", "gate-lanes"):
        print(__doc__)
        return 64
    row = evaluate(read_usage(), cap_usd(), datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    record(row)
    if cmd == "gate-lanes":
        return gate_lanes(row)
    print(line(row))
    rc = {"ok": OK, "over": OVER}.get(row["state"], UNKNOWN)
    if rc == OK:  # the hourly ceiling gates starts too (audio drain)
        hour = read_hour_usage()
        if "error" in hour:
            print(f"hourly usage unknown ({hour['error']})")
            return UNKNOWN
        if hour["usd"] >= hourly_ceiling_usd(row["cap_usd"]):
            print(f"over the hourly ceiling: ${hour['usd']:.2f} of ${hourly_ceiling_usd(row['cap_usd']):.2f}")
            return OVER
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
