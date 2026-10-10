#!/usr/bin/env python3
"""Client for the Muse queue runner (see scripts/muse_runner.py).

Submits a prompt to outputs/muse-queue/in atomically and waits for
outputs/muse-queue/out/<id>.json. Needs no Keychain or login: the runner,
running in the GUI session as LaunchAgent com.saneapps.muse-runner, makes
the call.

  python3 scripts/muse_client.py --prompt-file p.txt [--effort medium] [--timeout 1200] [--json]
  python3 scripts/muse_client.py --status

  from muse_client import ask
  res = ask("prompt text", effort="medium")   # dict: answer, rc, seconds, error, ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from muse_runner import dirs, queue_dir, write_atomic  # noqa: E402

HEARTBEAT_MAX_AGE = 30.0


def runner_alive(q: Path | None = None) -> bool:
    hb = (q or queue_dir()) / "heartbeat"
    return hb.exists() and (time.time() - hb.stat().st_mtime) < HEARTBEAT_MAX_AGE


def submit(prompt: str, effort: str = "medium", timeout: int = 900, q: Path | None = None,
           tag: str = "job") -> str:
    q = q or queue_dir()
    d = dirs(q)
    jid = f"{time.strftime('%Y%m%dT%H%M%S')}_{tag}_{uuid.uuid4().hex[:8]}"
    write_atomic(d["in"] / f"{jid}.json", {"prompt": prompt, "effort": effort, "timeout": timeout,
                                           "submitted_at": time.time()})
    return jid


def wait(jid: str, q: Path | None = None, timeout: float = 1200, poll: float = 2.0,
         require_runner: bool = True) -> dict:
    q = q or queue_dir()
    out = dirs(q)["out"] / f"{jid}.json"
    t0 = time.time()
    while time.time() - t0 < timeout:
        if out.exists():
            return json.loads(out.read_text(encoding="utf-8"))
        if require_runner and time.time() - t0 > HEARTBEAT_MAX_AGE and not runner_alive(q):
            return {"id": jid, "error": "muse runner not alive (no heartbeat); job left queued", "answer": ""}
        time.sleep(poll)
    return {"id": jid, "error": f"client timeout after {timeout}s; job may still finish", "answer": ""}


def ask(prompt: str, effort: str = "medium", timeout: int = 900, q: Path | None = None,
        tag: str = "job", wait_timeout: float | None = None) -> dict:
    jid = submit(prompt, effort, timeout, q, tag)
    return wait(jid, q, timeout=wait_timeout or timeout + 300)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt-file", type=Path)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--json", action="store_true", help="print the whole result record")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    q = queue_dir()
    if a.status:
        d = dirs(q)
        print(json.dumps({"queue": str(q), "runner_alive": runner_alive(q),
                          "queued": len(list(d["in"].glob("*.json"))),
                          "running": len(list(d["work"].glob("*.json"))),
                          "done": len(list(d["out"].glob("*.json")))}))
        return 0
    if not a.prompt_file:
        ap.error("--prompt-file is required")
    res = ask(a.prompt_file.read_text(encoding="utf-8"), a.effort, a.timeout, q, tag=a.prompt_file.stem[:24])
    print(json.dumps(res, ensure_ascii=False) if a.json else (res.get("answer") or ""))
    if res.get("error"):
        print("ERROR:", res["error"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
