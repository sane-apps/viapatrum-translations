#!/usr/bin/env python3
"""Model calls billed to subscription plans, not Workers AI credit (owner 2026-10-19:
"automate that ... make them self aware of usage limits in their various plans").

Three plans, called through their own CLIs so no per-token bill is involved:
  muse     Muse, through the Muse queue runner (scripts/muse_client.py). Model id "muse".
  claude   Claude Code headless (`claude -p`), no tools, no session. Model ids
           claude-sonnet-5-5, claude-haiku-5-5, claude-opus-5-5.
  grok     Grok Build headless (`grok --prompt-file`), no tools, the X subscription login:
           XAI_API_KEY is removed from its environment (per-use billing). Model ids
           grok-4.7-build-fast (low effort), grok-4.7.

llm_bakeoff.vendor_call routes these ids here, so every work_pipeline call (draft,
check, repair, referee, readers) can run on the plans with no other change.

Limits are handled, not fought:
- When a plan says its usage window is spent, the reset time it names is recorded in
  outputs/plan-limits/state.json and every process waits for it, then carries on.
  Nothing is marked failed and no retry is spent. Muse: "Subscription quota exhausted.
  Your usage window resets at <ISO>". Claude: "You've hit your weekly limit · resets
  Oct 12 at 9pm (America/New_York)".
- Each plan keeps a soft budget per hour and per rolling day (PLAN_<PLAN>_CALLS_PER_HOUR /
  _PER_DAY; Claude 60 / 500, Muse 120 / 600, Grok 30 / 200), because the owner's own Claude
  Code, Muse Spark and Cursor use share these limits (Grok's pool is shared with Cursor).
  At most 3 Claude, 4 Muse and 2 Grok calls run at once across every lane.
- A call waits at most PLAN_MAX_WAIT_S (default 6 h) for a window; past that it returns
  an error with "plan paused" in it and the caller decides.

  python3 scripts/plan_calls.py status          # pauses + budget, one JSON line
  python3 scripts/plan_calls.py smoke [model]   # one tiny call per plan
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get("PLAN_STATE", ROOT / "outputs" / "plan-limits" / "state.json"))
SLOTS = Path(os.environ.get("PLAN_SLOTS", "/tmp/plan-claude-slots"))
CLAUDE = os.environ.get("CLAUDE_BIN", str(Path.home() / ".local/bin/claude"))
NO_TOOLS = ["Bash", "Edit", "Write", "Read", "Glob", "Grep", "WebFetch", "WebSearch", "Agent", "NotebookEdit"]
CLAUDE_MODELS = {"claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"}
MUSE_MODEL = "muse"
# Grok on the owner's X subscription login, never XAI_API_KEY (per-use billing; owner
# 2026-10-19). build-fast at low effort: 62 s a section and the best recall in the checker
# bench (outputs/checker-bench-20261019: 4 real catches no other checker made).
GROK_MODELS = {"grok-4.7-build-fast", "grok-4.7"}
GROK = os.environ.get("GROK_BIN", str(Path.home() / ".grok/bin/grok"))
GROK_EFFORT = os.environ.get("PLAN_GROK_EFFORT", "low")
GROK_NO_TOOLS = "bash,edit,write,read,glob,grep,web_fetch,web_search,task"
# Grok loads project files (AGENTS.md and the like) from its cwd, so it runs in a private,
# empty, owner-only folder: a shared /tmp path could be pre-seeded with instructions.
GROK_CWD = Path(os.environ.get("PLAN_GROK_CWD") or Path.home() / ".cache" / "plan-grok-empty")
# Soft budgets per plan: the owner's own Claude Code and Muse Spark sessions share these
# plans' limits, so the lanes take a bounded slice, per hour and per rolling day.
BUDGETS = {
    "claude": (int(os.environ.get("PLAN_CLAUDE_CALLS_PER_HOUR", "50")),
               int(os.environ.get("PLAN_CLAUDE_CALLS_PER_DAY", "600"))),
    "muse": (int(os.environ.get("PLAN_MUSE_CALLS_PER_HOUR", "120")),
             int(os.environ.get("PLAN_MUSE_CALLS_PER_DAY", "600"))),
    # One weekly X-plan pool is shared with the owner's Cursor use: take a small slice.
    "grok": (int(os.environ.get("PLAN_GROK_CALLS_PER_HOUR", "30")),
             int(os.environ.get("PLAN_GROK_CALLS_PER_DAY", "200"))),
}
GROK_CONCURRENT = int(os.environ.get("PLAN_GROK_MAX_CONCURRENT", "2"))
PLANS = ("muse", "claude", "grok")
CLAUDE_CONCURRENT = int(os.environ.get("PLAN_CLAUDE_MAX_CONCURRENT", "3"))
# Muse jobs in flight across every lane; the runner itself works MUSE_WORKERS (2) at once,
# so this keeps its queue short and each call's wait bounded.
MUSE_CONCURRENT = int(os.environ.get("PLAN_MUSE_MAX_CONCURRENT", "4"))
MAX_WAIT_S = float(os.environ.get("PLAN_MAX_WAIT_S", str(6 * 3600)))
MUSE_EFFORT = os.environ.get("PLAN_MUSE_EFFORT", "medium")
CALL_TIMEOUT_S = int(os.environ.get("PLAN_CALL_TIMEOUT_S", "900"))
DEFAULT_PAUSE_S = 3600  # a limit message whose reset time cannot be read
PAUSED = "plan paused"


def is_plan_model(model: str) -> bool:
    return plan_of(model) is not None


def plan_of(model: str) -> str | None:
    m = (model or "").strip()
    if m == MUSE_MODEL:
        return "muse"
    if m in CLAUDE_MODELS:
        return "claude"
    if m in GROK_MODELS:
        return "grok"
    return None


# ---------------------------------------------------------------- limit messages

MUSE_LIMIT = re.compile(r"quota exhausted|usage window resets", re.I)
# Grok's wording was not seen yet: match the usual limit phrases and read any reset time.
GROK_LIMIT = re.compile(r"usage limit|rate limit|quota|limit reached|exceeded your|too many requests|\b429\b|balance exhausted|payment required|\b402\b", re.I)
ISO_TIME = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d))")
MUSE_RESET = re.compile(r"resets at (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)")
CLAUDE_LIMIT = re.compile(r"hit your (?:\w+ )?limit|usage limit reached|limit reached", re.I)
CLAUDE_RESET = re.compile(
    r"resets\s+(?:(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+at\s+)?"
    r"(?P<hour>\d{1,2})(?::(?P<min>\d\d))?\s*(?P<ampm>am|pm)"
    r"(?:\s*\((?P<tz>[A-Za-z_]+/[A-Za-z_]+)\))?", re.I)
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                                      "Nov", "Dec"), 1)}


def muse_reset(text: str, now: datetime) -> datetime | None:
    """Reset time from a Muse quota message, or None when it is not one."""
    if not MUSE_LIMIT.search(text or ""):
        return None
    m = MUSE_RESET.search(text)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return now + timedelta(seconds=DEFAULT_PAUSE_S)


def grok_reset(text: str, now: datetime) -> datetime | None:
    """Reset time from a Grok limit message, or None when it is not one."""
    if not GROK_LIMIT.search(text or ""):
        return None
    m = ISO_TIME.search(text)
    if m:
        return datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    return claude_reset("limit reached " + text, now)  # "resets 3pm (zone)" style, else +1 h


def claude_reset(text: str, now: datetime) -> datetime | None:
    """Reset time from a Claude limit message, or None when it is not one.

    "resets 3pm (America/New_York)" is the next 3 pm there; "resets Oct 12 at 9pm (...)"
    names the day. An epoch after "|" (older CLI wording) is used as is."""
    text = text or ""
    if not CLAUDE_LIMIT.search(text):
        return None
    epoch = re.search(r"\|(\d{10})\b", text)
    if epoch:
        return datetime.fromtimestamp(int(epoch.group(1)), timezone.utc)
    m = CLAUDE_RESET.search(text)
    if not m:
        return now + timedelta(seconds=DEFAULT_PAUSE_S)
    tz = ZoneInfo(m.group("tz") or "America/New_York")
    local_now = now.astimezone(tz)
    hour = int(m.group("hour")) % 12 + (12 if m.group("ampm").lower() == "pm" else 0)
    minute = int(m.group("min") or 0)
    if m.group("mon"):
        when = local_now.replace(month=MONTHS[m.group("mon").title()], day=int(m.group("day")),
                                 hour=hour, minute=minute, second=0, microsecond=0)
        if when < local_now - timedelta(days=1):  # "Jan 2" read in late December
            when = when.replace(year=when.year + 1)
    else:
        when = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if when <= local_now:
            when += timedelta(days=1)
    return when.astimezone(timezone.utc)


# ---------------------------------------------------------------- shared state

@contextmanager
def _state():
    """Read-modify-write the shared state under an exclusive lock."""
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE.with_suffix(".lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            data = json.loads(STATE.read_text()) if STATE.exists() else {}
        except ValueError:
            data = {}
        yield data
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1))
        tmp.replace(STATE)


def pause(plan: str, until: datetime, why: str) -> None:
    with _state() as s:
        cur = s.get(plan, {}).get("paused_until")
        if not cur or cur < until.isoformat():
            s.setdefault(plan, {}).update(paused_until=until.isoformat(timespec="seconds"),
                                          why=why[:300], since=_now().isoformat(timespec="seconds"))


def paused_until(plan: str, now: datetime | None = None) -> datetime | None:
    now = now or _now()
    with _state() as s:
        raw = s.get(plan, {}).get("paused_until")
    if not raw:
        return None
    until = datetime.fromisoformat(raw)
    return until if until > now else None


def _budget_wait(plan: str, now: datetime) -> float:
    """Seconds until the plan's soft hourly and daily budgets both have room (0 = go)."""
    per_hour, per_day = BUDGETS[plan]
    t = now.timestamp()
    with _state() as s:
        c = s.setdefault(plan, {})
        day = [x for x in c.get("calls", []) if x > t - 86400]
        hour = [x for x in day if x > t - 3600]
        c["calls"] = day
        if len(hour) >= per_hour:
            return max(1.0, hour[0] + 3600 - t)
        if len(day) >= per_day:
            return max(1.0, day[0] + 86400 - t)
        return 0.0


def _record_call(plan: str, now: datetime) -> None:
    """Count a call against the budget only once the plan actually ran it: a call that
    never reached the plan (runner down, local timeout) must not spend budget
    (2026-10-19: 120 'runner not alive' failures used up Muse's hour)."""
    with _state() as s:
        c = s.setdefault(plan, {})
        c.setdefault("calls", []).append(now.timestamp())
        c["calls_total"] = int(c.get("calls_total", 0)) + 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


@contextmanager
def _slot(name: str, n: int):
    """At most n calls of this plan in flight across every lane (file-lock slots)."""
    SLOTS.mkdir(parents=True, exist_ok=True)
    while True:
        for i in range(n):
            fh = open(SLOTS / f"{name}-{i}.lock", "w")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                fh.close()
                continue
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
                fh.close()
            return
        _sleep(2)


# ---------------------------------------------------------------- calls

def _split(messages: list) -> tuple[str, str]:
    system = "\n\n".join(m["content"] for m in messages if m.get("role") == "system")
    user = "\n\n".join(m["content"] for m in messages if m.get("role") != "system")
    return system, user


def _run_claude(model: str, system: str, user: str) -> tuple[str, bool]:
    """(text, is_error) from one `claude -p` call."""
    cmd = [CLAUDE, "-p", "--model", model, "--output-format", "json", "--no-session-persistence",
           "--disallowedTools", *NO_TOOLS]
    if system:
        cmd += ["--system-prompt", system]
    try:
        r = subprocess.run(cmd, input=user, capture_output=True, text=True, timeout=CALL_TIMEOUT_S,
                           cwd=str(ROOT / "outputs"))
    except subprocess.TimeoutExpired:
        return f"claude timeout after {CALL_TIMEOUT_S}s", True
    out = r.stdout.strip()
    if out.startswith("{"):
        try:
            env = json.loads(out)
            return str(env.get("result") or ""), bool(env.get("is_error"))
        except ValueError:
            pass
    return (out or r.stderr.strip())[:2000], r.returncode != 0


RUNNER_DOWN_S = 600  # heartbeat silent this long = runner really down, not just busy
RUNNER_DOWN = "muse runner down"


def _runner_heartbeat_age() -> float:
    from muse_runner import queue_dir
    hb = queue_dir() / "heartbeat"
    return time.time() - hb.stat().st_mtime if hb.exists() else float("inf")


def _run_grok(model: str, system: str, user: str) -> tuple[str, bool]:
    """(text, is_error) from one headless Grok call on the subscription login."""
    GROK_CWD.mkdir(mode=0o700, parents=True, exist_ok=True)
    st = GROK_CWD.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        return f"grok cwd {GROK_CWD} is not a private folder owned by this user; refusing", True
    env = {k: v for k, v in os.environ.items() if k != "XAI_API_KEY"}
    pf = GROK_CWD / f"prompt-{os.getpid()}-{time.time_ns()}.txt"
    fd = os.open(pf, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(user)
    cmd = [GROK, "--prompt-file", str(pf), "-m", model, "--output-format", "json", "--disable-web-search",
           "--disallowed-tools", GROK_NO_TOOLS, "--reasoning-effort", GROK_EFFORT]
    if system:
        cmd += ["--system-prompt-override", system]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT_S, cwd=str(GROK_CWD), env=env)
    except subprocess.TimeoutExpired:
        return f"grok timeout after {CALL_TIMEOUT_S}s", True
    finally:
        pf.unlink(missing_ok=True)
    out = r.stdout.strip()
    if out.startswith("{"):
        try:
            env_out = json.loads(out)
            text = str(env_out.get("text") or "")
            return (text or str(env_out)[:2000]), (r.returncode != 0 or not text)
        except ValueError:
            pass
    return (out or r.stderr.strip())[:2000], True


def _run_muse(prompt: str) -> tuple[str, bool]:
    """One Muse job through the runner queue. A busy runner is waited on, never failed:
    the call waits up to an hour for its queued job (MUSE_WORKERS run at once)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from muse_client import submit, wait
    if _runner_heartbeat_age() > RUNNER_DOWN_S:
        return f"{RUNNER_DOWN}: heartbeat silent over {RUNNER_DOWN_S}s", True
    with _slot("muse", MUSE_CONCURRENT):
        jid = submit(prompt, effort=MUSE_EFFORT, timeout=CALL_TIMEOUT_S, tag="plan")
        res = wait(jid, timeout=CALL_TIMEOUT_S + 3600, require_runner=False)
    err = str(res.get("error") or "")
    if err:
        return (err + " " + str(res.get("stderr_tail") or ""))[:2000], True
    return str(res.get("answer") or ""), False


def chat(model: str, messages: list, max_tokens: int | None = None) -> dict:
    """vendor_call-shaped result: {"content", "ms"} or {"error", "ms"}.

    Waits out a spent usage window (and the soft Claude budget) instead of failing."""
    plan = plan_of(model)
    if plan is None:
        return {"error": f"not a plan model: {model}", "ms": 0}
    system, user = _split(messages)
    t0 = time.time()
    deadline = t0 + MAX_WAIT_S
    while True:
        now = _now()
        until = paused_until(plan, now)
        if until:
            wait = (until - now).total_seconds() + 30
            if time.time() + wait > deadline:
                return {"error": f"{PAUSED}: {plan} until {until.isoformat()}", "ms": int((time.time() - t0) * 1000)}
            _sleep(wait)
            continue
        wait = _budget_wait(plan, now)
        if wait:
            if time.time() + wait > deadline:
                return {"error": f"{PAUSED}: {plan} budget", "ms": int((time.time() - t0) * 1000)}
            _sleep(wait)
            continue
        if plan == "claude":
            with _slot("claude", CLAUDE_CONCURRENT):
                text, is_err = _run_claude(model, system, user)
            reset = claude_reset(text, _now()) if is_err else None
        elif plan == "grok":
            with _slot("grok", GROK_CONCURRENT):
                text, is_err = _run_grok(model, system, user)
            reset = grok_reset(text, _now()) if is_err else None
        else:
            prompt = f"{system}\n\n---\n\n{user}" if system else user
            text, is_err = _run_muse(prompt)
            reset = muse_reset(text, _now()) if is_err else None
            if is_err and text.startswith(RUNNER_DOWN):  # launchd restarts it; wait, don't fail
                reset = _now() + timedelta(minutes=10)
        if not (is_err and text.startswith(RUNNER_DOWN)):
            _record_call(plan, _now())  # soft budget: concurrent callers may overshoot by a few
        if reset:
            pause(plan, reset, text)
            print(f"plan_calls: {plan} usage window spent; waiting until {reset.isoformat()}",
                  file=sys.stderr, flush=True)
            continue
        ms = int((time.time() - t0) * 1000)
        if is_err:
            return {"error": f"{plan} call failed: {text[:300]}", "ms": ms}
        return {"content": text, "ms": ms}


def status() -> dict:
    now = _now()
    with _state() as s:
        snap = json.loads(json.dumps(s))
    out = {"at": now.isoformat(timespec="seconds")}
    for plan in PLANS:
        p = snap.get(plan, {})
        raw = p.get("paused_until")
        live = bool(raw) and datetime.fromisoformat(raw) > now
        calls = p.get("calls", [])
        out[plan] = {"paused_until": raw if live else None, "why": p.get("why") if live else None,
                     "calls_last_hour": sum(t > now.timestamp() - 3600 for t in calls),
                     "calls_last_day": sum(t > now.timestamp() - 86400 for t in calls),
                     "budget_hour_day": list(BUDGETS[plan]), "calls_total": p.get("calls_total", 0)}
    return out


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status()))
        return 0
    if cmd == "smoke":
        models = argv[2:] or [MUSE_MODEL, "claude-haiku-5-5"]
        ok = True
        for m in models:
            r = chat(m, [{"role": "user", "content": 'Reply with exactly this JSON and nothing else: {"ok": true}'}])
            good = '"ok": true' in (r.get("content") or "").replace('"ok":true', '"ok": true')
            ok &= good
            print(f"{m}: {'ok' if good else 'FAIL'} {r.get('ms')} ms {r.get('error', '')[:200]}")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
