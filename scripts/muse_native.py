#!/usr/bin/env python3
"""Run a Muse model the way it is built to work: as a coding agent with its own tools, inside one workspace folder,
under the Muse program's own operating-system sandbox (19 Nov 2026, late).

Why this file: on 19 Nov I ran Muse models with their tools switched off (`--preset empty`) and made them answer in
my own one-action text format (sealed_run.py). They failed that format and I reported that "Muse cannot do code
work". The owner: "Sounds like user error. Muse ought to be able to code if needed ... It's sop to learn tools before
you tell me they're broken." He was right: the tool has a coding mode, and it has a sandbox.

What the Muse sandbox does on this Mac, measured with nine fixed commands (probe kept in
~/.cache/sealed-jobs/muse-native-probe-*/events.jsonl, 20 Nov 2026 12:13 AM), with --sandbox-network restricted:
  writes inside the workspace: allowed        writes outside it: "Operation not permitted"
  network (curl): blocked                     keychain (`security list-keychains`): fails
  opening an app (`open -a`): fails           a Python from a virtual environment outside the workspace: runs
  READS OUTSIDE THE WORKSPACE: ALLOWED (it read a canary file and listed ~/.ssh).
So: it cannot change, send or launch anything outside its folder, but it can read the home folder. Rules for callers:
give it only tasks whose text you control or have read; tell it which folders it may read; and run audit() on the
event log afterwards, which lists every command that names a path outside the allowed folders.

  run_native(model, task, workspace, effort="high", timeout_s=3600, allowed_roots=()) ->
      {"final": text, "rc": int, "commands": [...], "outside": [...], "events_path": str}
"""
import json, os, re, subprocess, time
from pathlib import Path

MUSE = os.path.expanduser("~/.local/bin/muse")
MODELS = {"muse-wonder-full-1.0", "muse-wonder-1.0", "muse-spark-1.3", "muse-ember-1.0"}
HOME = os.path.realpath(os.path.expanduser("~"))


def audit(events_path, workspace, allowed_roots=()):
    """Every shell command the run made, and those naming a path under the home folder or /Volumes that is outside
    the workspace and the allowed folders (a lexical check of the command text; it reports, it does not judge)."""
    ok = [os.path.realpath(os.fspath(workspace))] + [os.path.realpath(os.fspath(r)) for r in allowed_roots]
    ok += [os.path.expanduser(os.fspath(r)) for r in allowed_roots] + [os.fspath(workspace)]
    cmds, outside = [], []
    for line in open(events_path, errors="replace"):
        try:
            p = (json.loads(line).get("payload") or {})
        except ValueError:
            continue
        if p.get("kind") != "tool_result":
            continue
        try:
            t = json.loads(p.get("text") or "{}")
        except ValueError:
            t = {}
        c = t.get("command")
        if not c:
            continue
        cmds.append({"command": c, "exit_code": t.get("exit_code")})
        for path in re.findall(r"(?:~|\$HOME|/Users/[^\s\"';|&)]*|/Volumes/[^\s\"';|&)]*)[^\s\"';|&)]*", c):
            plain = os.path.expanduser(path.replace("$HOME", HOME))
            full = os.path.realpath(plain)     # a link (a virtual environment's python) is judged where it is named too
            if not any(x == r or x.startswith(r.rstrip("/") + "/") for r in ok for x in (plain, full)):
                outside.append({"command": c, "path": path})
    return cmds, outside


def run_native(model, task, workspace, effort="high", timeout_s=3600, allowed_roots=()):
    if model not in MODELS:
        raise ValueError(f"not a Muse model we call: {model}")
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import plan_calls
    why = plan_calls._screen("muse", "", task)
    if why:
        raise RuntimeError(f"{model}: screened: {why}; refusing")
    ws = Path(os.path.realpath(os.fspath(workspace)))
    if not ws.is_dir() or ws == Path(HOME) or str(Path(HOME)).startswith(str(ws) + "/"):
        raise ValueError("the workspace must be an existing folder that is not the home folder or above it")
    pf = ws / ".task.txt"
    pf.write_text(task)
    ev = ws / f".muse-events-{time.strftime('%H%M%S')}.jsonl"
    with open(ev, "w") as out, open(ws / ".muse-stderr.txt", "w") as err:
        try:
            p = subprocess.run([MUSE, "exec", "--json", "--workspace", str(ws), "--prompt-file", str(pf), "--model", model,
                                "--reasoning-effort", effort, "--disable-approval", "--sandbox-network", "restricted",
                                "--disable-web-tools"], stdout=out, stderr=err, timeout=timeout_s, cwd=str(ws),
                               stdin=subprocess.DEVNULL)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    final = None
    for line in open(ev, errors="replace"):
        try:
            pl = json.loads(line).get("payload") or {}
        except ValueError:
            continue
        if pl.get("kind") == "run_terminal" and pl.get("terminal") == "completed":
            final = pl.get("text") or ""
    cmds, outside = audit(ev, ws, allowed_roots)
    return {"final": final, "rc": rc, "commands": cmds, "outside": outside, "events_path": str(ev)}
