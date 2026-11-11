#!/usr/bin/env python3
"""Model calls billed to subscription plans, not Workers AI credit (owner 2026-10-19:
"automate that ... make them self aware of usage limits in their various plans").

Four plans, called through their own CLIs so no per-token bill is involved:
  muse     Muse, through the Muse queue runner (scripts/muse_client.py). Model id "muse".
  claude   Claude Code headless (`claude -p`), no tools, no session. Model ids
           claude-sonnet-5-5, claude-haiku-5-5, claude-opus-5-5.
  grok     Grok Build headless (`grok --prompt-file`), no tools, the X subscription login:
           XAI_API_KEY is removed from its environment (per-use billing). Model ids
           grok-4.7-build-fast (low effort), grok-4.7.
  agy      Antigravity CLI headless (`agy -p`), the owner's Google sign-in (added 2026-10-24;
           Gemini CLI's Google login ended 18 Jun 2026). Model ids "agy/<model>" from
           `agy models`: agy/gemini-3.8-flash-{high,medium,low}, agy/claude-sonnet-4-6,
           agy/claude-opus-4-6-thinking, agy/gpt-oss-120b-medium. Paid AI-credit overages are
           off in the owner's account settings (confirmed 2026-10-24); agy drops unknown
           settings keys, so this is not checked from a file. `agy models` on 2026-11-11 also
           lists gemini-4-argon-{low,medium,high}, claude-sonnet-5-5-* and claude-opus-5-5-*.
  cursor   Cursor CLI headless (`cursor-agent -p --mode ask`), the owner's Cursor login (added
           2026-11-11, owner: "cursor also available"). Model ids "cursor/<model>". Only models
           the plan includes: on 2026-11-11 it refused GPT-5.5 and Claude Sonnet 5.5 ("not
           included in your weekly usage. Buy credits or switch to a Grok model") and answered on
           composer-2.5. Its Grok models draw on the X plan pool, so they stay out.

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
  At most 3 Claude, 4 Muse and 2 Grok calls run at once across every lane. Cursor: 20 / 200,
  2 at once.
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
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get("PLAN_STATE", ROOT / "outputs" / "plan-limits" / "state.json"))
SLOTS = Path(os.environ.get("PLAN_SLOTS", "/tmp/plan-claude-slots"))
_HEADLESS = Path.home() / ".local/bin/claude-headless"  # wrapper with a long-lived login, where a machine has one
CLAUDE = os.environ.get("CLAUDE_BIN", str(_HEADLESS if _HEADLESS.exists() else Path.home() / ".local/bin/claude"))
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
# Antigravity: the plan quota refreshes every 5 h (weekly cap); limits are not published.
AGY = os.environ.get("AGY_BIN", "/opt/homebrew/bin/agy")
AGY_PREFIX = "agy/"
AGY_MODELS = {"gemini-3.8-flash-high", "gemini-3.8-flash-medium", "gemini-3.8-flash-low",
              "claude-sonnet-4-6", "claude-opus-4-6-thinking", "gpt-oss-120b-medium",
              # `agy models`, 2026-11-11
              "gemini-4-argon-low", "gemini-4-argon-medium", "gemini-4-argon-high",
              "claude-sonnet-5-5-low", "claude-sonnet-5-5-medium", "claude-sonnet-5-5-high",
              "claude-opus-5-5-low", "claude-opus-5-5-medium", "claude-opus-5-5-high"}
AGY_CONCURRENT = int(os.environ.get("PLAN_AGY_MAX_CONCURRENT", "3"))
# Headless agy still runs shell commands and fetches URLs (tested 2026-10-24), so lane calls
# run under their own HOME, signed in separately, whose settings deny every tool, from an
# empty owner-only folder. The owner's own ~/.gemini settings are untouched.
AGY_HOME = Path(os.environ.get("PLAN_AGY_HOME") or Path.home() / ".cache" / "agy-lane-home")
AGY_CWD = AGY_HOME / "work"
AGY_DENY_ALL = {"command(*)", "read_file(*)", "write_file(*)", "mcp(*)", "read_url(*)", "execute_url(*)"}
BUDGETS["agy"] = (int(os.environ.get("PLAN_AGY_CALLS_PER_HOUR", "60")),
                  int(os.environ.get("PLAN_AGY_CALLS_PER_DAY", "600")))
# Cursor: the weekly allowance is not published, and the owner's own Cursor work shares it, so a
# small slice. No paid credits: a model the plan does not include is refused, never bought.
CURSOR = os.environ.get("CURSOR_BIN", str(Path.home() / ".local/bin/cursor-agent"))
CURSOR_PREFIX = "cursor/"
CURSOR_MODELS = {"composer-2.5"}
CURSOR_CONCURRENT = int(os.environ.get("PLAN_CURSOR_MAX_CONCURRENT", "2"))
BUDGETS["cursor"] = (int(os.environ.get("PLAN_CURSOR_CALLS_PER_HOUR", "20")),
                     int(os.environ.get("PLAN_CURSOR_CALLS_PER_DAY", "200")))
# Lane folder, tested 2026-11-11: a workspace under HOME made Cursor load ~/AGENTS.md from a parent
# folder, so it lives in the per-user temp folder. Ask mode refused shell and file writes but still
# read any file by path, and its WebFetch tool exists; the project .cursor/cli.json below denies
# reads, writes, shell, MCP and fetches ("Permission denied" / "User Rejected" in the same test).
CURSOR_DIR = Path(os.environ.get("PLAN_CURSOR_DIR") or Path(os.confstr(65537) or "/tmp") / "plan-cursor-lane")  # 65537: DARWIN_USER_TEMP_DIR
CURSOR_DENY_ALL = ["Read(**)", "Write(**)", "Shell(*)", "Mcp(*:*)", "WebFetch(*)"]
PLANS = ("muse", "claude", "grok", "agy", "cursor")
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
    if m.startswith(AGY_PREFIX) and m[len(AGY_PREFIX):] in AGY_MODELS:
        return "agy"
    if m.startswith(CURSOR_PREFIX) and m[len(CURSOR_PREFIX):] in CURSOR_MODELS:
        return "cursor"
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


def pause_key(model: str) -> str | None:
    """Where a spent window is recorded. Antigravity quotas are per model family: the 29 Oct and
    4 Nov "Individual quota reached" stops were gemini-3.8-flash-high alone (agy lane logs), so a
    spent Gemini referee must not stop an agy Claude checker, or the reverse (2026-11-11). Budgets
    stay per plan."""
    plan = plan_of(model)
    if plan == "agy":
        name = model[len(AGY_PREFIX):]
        return "agy/" + next((g for g in ("gemini", "claude", "gpt-oss") if g in name), name)
    return plan


def paused_until(plan: str, now: datetime | None = None) -> datetime | None:
    """Live pause for a plan, or for a pause_key ("agy/claude"), which a pause of its whole plan also covers."""
    now = now or _now()
    keys = [plan] + ([plan.split("/", 1)[0]] if "/" in plan else [])
    with _state() as s:
        raws = [s.get(k, {}).get("paused_until") for k in keys]
    live = [u for u in (datetime.fromisoformat(r) for r in raws if r) if u > now]
    return max(live) if live else None


def budgets(plan: str, now: datetime | None = None) -> tuple[int, int]:
    """(per hour, per day) for a plan. budgets.json, when present, is the one live setting every
    process reads on each call: per-process caps let a job with a higher cap starve the others
    (2026-10-19, twice). Without the file, the env/defaults in BUDGETS apply.

    A "night" block ({"hours": [22, 8], "claude": [100, 900]}) applies between those local hours,
    so background work takes most of a plan while the owner is not using it (owner 2026-10-19:
    "muse and grok do most of this work so claude is free to be my main on other projects")."""
    try:
        cfg = json.loads(STATE.with_name("budgets.json").read_text())
        night = cfg.get("night") or {}
        hours = night.get("hours")
        if isinstance(hours, list) and len(hours) == 2 and plan in night:
            h, (a, b) = (now or datetime.now(timezone.utc)).astimezone().hour, hours
            if (a <= h < b) if a < b else (h >= a or h < b):
                cfg = night
        v = cfg.get(plan)
        if isinstance(v, list) and len(v) == 2:
            return int(v[0]), int(v[1])
    except (OSError, ValueError, TypeError):
        pass
    return BUDGETS[plan]


def _budget_wait(plan: str, now: datetime) -> float:
    """Seconds until the plan's soft hourly and daily budgets both have room (0 = go)."""
    per_hour, per_day = budgets(plan, now)
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
# A login that failed never reached the plan: pause briefly, spend no budget (2026-11-07: about
# 25 "OAuth session expired and could not be refreshed" failures used up Claude's 15/h).
AUTH_FAIL = re.compile(r"failed to authenticate|oauth session expired|could not be refreshed|\bnot logged in\b", re.I)
AUTH_PAUSE_S = 300


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
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT_S, cwd=str(GROK_CWD), env=env)
    except subprocess.TimeoutExpired:
        return f"grok timeout after {CALL_TIMEOUT_S}s", True
    finally:
        pf.unlink(missing_ok=True)
    out = r.stdout.strip()
    env_out = {}
    if out.startswith("{"):
        try:
            env_out = json.loads(out)
        except ValueError:
            env_out = {}
    _GROK_USAGE.last = _grok_usage(env_out, t0)
    if env_out:
        text = str(env_out.get("text") or "")
        return (text or str(env_out)[:2000]), (r.returncode != 0 or not text)
    return (out or r.stderr.strip())[:2000], True


AGY_LIMIT = re.compile(r"quota|rate limit|usage limit|limit reached|exhausted|resource_exhausted|\b429\b|"
                       r"credits", re.I)


def agy_reset(text: str, now: datetime) -> datetime | None:
    """Reset time for a spent Antigravity quota: an ISO time when given, else +1 h."""
    if not AGY_LIMIT.search(text or ""):
        return None
    m = ISO_TIME.search(text)
    if m:
        try:
            return datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
        except ValueError:
            pass
    # "Resets in 0s" / "Resets in 5m30s" is a short per-model window, not a spent plan (2026-10-29: it was read as +1 h)
    rel = re.search(r"[Rr]esets in\s+(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", text)
    if rel and any(rel.groups()):
        h, mi, se = (int(x or 0) for x in rel.groups())
        return now + timedelta(seconds=max(30, h * 3600 + mi * 60 + se))
    return now + timedelta(seconds=DEFAULT_PAUSE_S)


def _run_agy(model: str, system: str, user: str) -> tuple[str, bool]:
    """(text, is_error) from one headless Antigravity call. Exit codes are not trusted:
    only status SUCCESS with a non-empty response counts."""
    AGY_CWD.mkdir(mode=0o700, parents=True, exist_ok=True)
    st = AGY_CWD.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077 or any(AGY_CWD.iterdir()):
        return f"agy cwd {AGY_CWD} is not a private, empty folder owned by this user; refusing", True
    try:
        cfg = json.loads((AGY_HOME / ".gemini" / "antigravity-cli" / "settings.json").read_text())
    except (OSError, ValueError):
        cfg = {}
    deny = set((cfg.get("permissions") or {}).get("deny") or [])
    if not AGY_DENY_ALL <= deny:
        return "agy lane settings must deny every tool; refusing", True
    # search_web cannot be denied by a permission rule (agy 1.4.7 rejects the action name);
    # it only sends a query to Google. Shell, files, URLs and MCP are denied in settings.
    rule = "Answer only from the text in this prompt. Do not use any tools, search, or browse."
    body = f"{system}\n\n---\n\n{user}" if system else user
    prompt = f"{rule}\n\n{body}"
    cmd = [AGY, "-p", prompt, "--model", model[len(AGY_PREFIX):], "--output-format", "json",
           "--print-timeout", f"{CALL_TIMEOUT_S}s"]
    try:
        env = {k: os.environ[k] for k in ("PATH", "USER", "LOGNAME", "LANG", "TMPDIR", "SHELL") if k in os.environ}
        env["HOME"] = str(AGY_HOME)
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=CALL_TIMEOUT_S + 60, cwd=str(AGY_CWD), env=env)
    except subprocess.TimeoutExpired:
        return f"agy timeout after {CALL_TIMEOUT_S}s", True
    out = r.stdout.strip()
    if out.startswith("{"):
        try:
            env = json.loads(out)
            text = str(env.get("response") or "")
            if env.get("status") == "SUCCESS" and text.strip():
                return text, False
            return (str(env.get("error") or env.get("status") or "") + " " + text)[:2000].strip() or out[:2000], True
        except ValueError:
            pass
    return (out or r.stderr.strip() or f"agy exit {r.returncode} with no output")[:2000], True


# "ActionRequiredError: GPT-5.5 is not included in your weekly usage Buy credits or switch to a Grok
# model to continue." (2026-11-11). Credits are never bought: the plan waits, then the caller decides.
CURSOR_LIMIT = re.compile(r"not included in your (?:weekly )?usage|usage limit|rate limit|limit reached|quota|"
                          r"too many requests|\b429\b|buy credits|out of (?:usage|credits)", re.I)


def cursor_reset(text: str, now: datetime) -> datetime | None:
    """Reset time for a spent Cursor allowance: an ISO time when given, else +1 h."""
    if not CURSOR_LIMIT.search(text or ""):
        return None
    m = ISO_TIME.search(text)
    if m:
        try:
            return datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
        except ValueError:
            pass
    return now + timedelta(seconds=DEFAULT_PAUSE_S)


def _cursor_lane() -> str:
    """Check (and on first use make) the Cursor lane folder; '' when it is safe to run in."""
    d = CURSOR_DIR
    if str(d.resolve()).startswith(str(Path.home().resolve()) + os.sep):
        return f"cursor lane folder {d} is under HOME (Cursor would load ~/AGENTS.md); refusing"
    d.parent.mkdir(parents=True, exist_ok=True)
    d.mkdir(mode=0o700, exist_ok=True)
    (d / ".cursor").mkdir(mode=0o700, exist_ok=True)
    for p in (d, d / ".cursor"):
        st = p.stat()
        if st.st_uid != os.getuid() or st.st_mode & 0o077:
            return f"cursor lane folder {p} is not private to this user; refusing"
    cfg_path = d / ".cursor" / "cli.json"
    if not cfg_path.exists():
        fd = os.open(cfg_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump({"permissions": {"allow": [], "deny": CURSOR_DENY_ALL}}, fh)
    try:
        perms = json.loads(cfg_path.read_text()).get("permissions") or {}
    except (OSError, ValueError):
        perms = {}
    if perms.get("allow") or not set(CURSOR_DENY_ALL) <= set(perms.get("deny") or []):
        return "cursor lane settings must deny every tool and allow none; refusing"
    if {p.name for p in d.iterdir()} != {".cursor"} or {p.name for p in (d / ".cursor").iterdir()} != {"cli.json"}:
        return f"cursor lane folder {d} must hold only .cursor/cli.json; refusing"
    return ""


def _run_cursor(model: str, system: str, user: str) -> tuple[str, bool]:
    """(text, is_error) from one headless Cursor call in ask mode, every tool denied, prompt on stdin."""
    why = _cursor_lane()
    if why:
        return why, True
    rule = "Answer only from the text in this prompt. Do not use any tools, search, or browse."
    body = f"{system}\n\n---\n\n{user}" if system else user
    cmd = [CURSOR, "-p", "--output-format", "json", "--mode", "ask", "--sandbox", "enabled", "--trust",
           "--model", model[len(CURSOR_PREFIX):], "--workspace", str(CURSOR_DIR)]
    try:
        r = subprocess.run(cmd, input=f"{rule}\n\n{body}", capture_output=True, text=True, timeout=CALL_TIMEOUT_S,
                           cwd=str(CURSOR_DIR))
    except subprocess.TimeoutExpired:
        return f"cursor timeout after {CALL_TIMEOUT_S}s", True
    out = r.stdout.strip()
    if out.startswith("{"):
        try:
            env = json.loads(out)
            text = str(env.get("result") or "")
            if not env.get("is_error") and text.strip():
                return text, False
            return (text or out)[:2000], True
        except ValueError:
            pass
    return (out or r.stderr.strip() or f"cursor exit {r.returncode} with no output")[:2000], True


_GROK_USAGE = threading.local()
GROK_SESSIONS = Path.home() / ".grok" / "sessions"


def _grok_usage(env_out: dict, t0: float) -> dict:
    """Tokens one Grok call used, from its session's usage.json: by the session id in the
    CLI's JSON when it gives one, else the newest session written in our cwd since t0."""
    folder = GROK_SESSIONS / str(GROK_CWD).replace("/", "%2F")
    sid = env_out.get("session_id") or env_out.get("sessionId") if isinstance(env_out, dict) else None
    paths = [folder / str(sid) / "usage.json"] if sid else sorted(
        (p for p in folder.glob("*/usage.json") if p.stat().st_mtime >= t0 - 1), key=lambda p: p.stat().st_mtime)[-1:]
    for p in paths:
        try:
            u = json.loads(p.read_text()).get("session") or {}
            return {"tokens": int(u.get("totalTokens") or 0),
                    "uncached": int(u.get("totalTokens") or 0) - int(u.get("cachedReadTokens") or 0)}
        except (OSError, ValueError):
            pass
    return {"tokens": None, "uncached": None}


def _ledger_path() -> Path:
    return STATE.with_name("grok-ledger.jsonl")


def _grok_ledger(ok: bool, limit: bool) -> None:
    u = getattr(_GROK_USAGE, "last", None) or {}
    row = {"at": _now().isoformat(timespec="seconds"), "ok": ok, "limit": limit,
           "tokens": u.get("tokens"), "uncached": u.get("uncached")}
    try:
        with _ledger_path().open("a") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


def grok_report() -> dict:
    """What the ledger says about the X plan's Grok Build pool (owner 2026-10-19: "figure out
    those limits and plan around them"): tokens spent in each window before a limit, when each
    limit lifted, and use since the last reset."""
    try:
        rows = [json.loads(l) for l in _ledger_path().read_text().splitlines() if l.strip()]
    except OSError:
        rows = []
    windows, cur, limited = [], {"start": rows[0]["at"] if rows else None, "tokens": 0, "uncached": 0, "calls": 0}, False
    for r in rows:
        if r.get("limit"):
            if not limited:
                windows.append({**cur, "limit_at": r["at"]})
                limited = True
            continue
        if r.get("ok"):
            if limited:
                windows[-1]["back_at"] = r["at"]
                cur = {"start": r["at"], "tokens": 0, "uncached": 0, "calls": 0}
                limited = False
            cur["tokens"] += r.get("tokens") or 0
            cur["uncached"] += r.get("uncached") or 0
            cur["calls"] += 1
    return {"windows": windows, "since_reset": None if limited else cur, "limited_now": limited}


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
    key = pause_key(model)
    t0 = time.time()
    deadline = t0 + MAX_WAIT_S
    while True:
        now = _now()
        until = paused_until(key, now)
        if until:
            wait = (until - now).total_seconds() + 30
            if time.time() + wait > deadline:
                return {"error": f"{PAUSED}: {key} until {until.isoformat()}", "ms": int((time.time() - t0) * 1000)}
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
            _grok_ledger(ok=not is_err, limit=bool(reset))
        elif plan == "agy":
            with _slot("agy", AGY_CONCURRENT):
                text, is_err = _run_agy(model, system, user)
            reset = agy_reset(text, _now()) if is_err and "refusing" not in text else None
        elif plan == "cursor":
            with _slot("cursor", CURSOR_CONCURRENT):
                text, is_err = _run_cursor(model, system, user)
            reset = cursor_reset(text, _now()) if is_err and "refusing" not in text else None
        else:
            prompt = f"{system}\n\n---\n\n{user}" if system else user
            text, is_err = _run_muse(prompt)
            reset = muse_reset(text, _now()) if is_err else None
            if is_err and text.startswith(RUNNER_DOWN):  # launchd restarts it; wait, don't fail
                reset = _now() + timedelta(minutes=10)
        auth = is_err and bool(AUTH_FAIL.search(text))
        if auth:
            reset = _now() + timedelta(seconds=AUTH_PAUSE_S)
        refused_locally = is_err and text.endswith("; refusing")  # lane folder check: the plan never ran it
        if not (is_err and text.startswith(RUNNER_DOWN)) and not auth and not refused_locally:
            _record_call(plan, _now())  # soft budget: concurrent callers may overshoot by a few
        if reset:
            pause(plan if auth else key, reset, text)  # a failed login stops the whole plan
            print(f"plan_calls: {plan if auth else key} {'login failed' if auth else 'usage window spent'}; waiting until "
                  f"{reset.isoformat()}", file=sys.stderr, flush=True)
            continue
        ms = int((time.time() - t0) * 1000)
        if is_err:
            return {"error": f"{plan} call failed: {text[:300]}", "ms": ms}
        return {"content": text, "ms": ms}


def probe(plan: str = "grok") -> str:
    """One tiny call, only while the ledger says the Grok pool is spent and its pause has run
    out, so the hour it comes back is recorded (fathers_watch runs this every 15 min). Never
    waits: a spent pool just re-pauses."""
    global MAX_WAIT_S
    if plan != "grok" or not grok_report()["limited_now"]:
        return "not limited"
    if paused_until(plan):
        return f"paused until {paused_until(plan).isoformat()}"
    old, MAX_WAIT_S = MAX_WAIT_S, 0
    try:
        r = chat("grok-4.7-build-fast", [{"role": "user", "content": 'Reply with exactly: {"ok": true}'}])
    finally:
        MAX_WAIT_S = old
    return "back" if r.get("content") else f"still limited: {str(r.get('error'))[:120]}"


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
                     "budget_hour_day": list(budgets(plan)), "calls_total": p.get("calls_total", 0)}
        groups = {k: v.get("paused_until") for k, v in snap.items() if k.startswith(plan + "/") and isinstance(v, dict)
                  and v.get("paused_until") and datetime.fromisoformat(v["paused_until"]) > now}
        if groups:
            out[plan]["model_pauses"] = groups  # e.g. agy/gemini spent while agy/claude still answers
    return out


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status()))
        return 0
    if cmd == "probe":
        print(probe(argv[2] if len(argv) > 2 else "grok"))
        return 0
    if cmd == "grok-report":
        print(json.dumps(grok_report(), indent=1))
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
