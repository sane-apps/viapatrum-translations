#!/usr/bin/env python3
"""Muse queue runner: lets scripts call Muse Code without an interactive login.

Muse authenticates through the login Keychain, which is only unlocked inside
the logged-in GUI (Aqua) session. Calls made over SSH can't reach it. This runner
runs as the user LaunchAgent com.saneapps.muse-runner
(~/Library/LaunchAgents/com.saneapps.muse-runner.plist, LimitLoadToSessionType
Aqua), so `muse exec` inherits the Aqua session. It never reads, copies or
exports any credential; it only calls `muse exec`.

Queue (default outputs/muse-queue, override with MUSE_QUEUE):
  in/<id>.json    job written by a client: {"prompt": str, "effort": "medium", "timeout": 900}
                  (written as in/<id>.json.tmp, then renamed, so it is atomic)
  work/<id>.json  claimed job (rename from in/; requeued to in/ if the runner restarts)
  out/<id>.json   result: {"id", "rc", "answer", "stderr_tail", "seconds", "effort",
                  "started_at", "finished_at", "error"} (written to .tmp, then renamed)
  heartbeat       touched every poll; clients use its age to tell the runner is alive
  runner.log      launchd stdout/stderr

Client side: scripts/muse_client.py (ask(), or the CLI).
  python3 scripts/muse_runner.py            # loop forever (what launchd runs)
  python3 scripts/muse_runner.py --once     # process what is queued now, then exit
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_QUEUE = Path(__file__).resolve().parents[1] / "outputs" / "muse-queue"
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}


def queue_dir() -> Path:
    return Path(os.environ.get("MUSE_QUEUE") or DEFAULT_QUEUE)


def muse_bin() -> str:
    return os.environ.get("MUSE_BIN") or str(Path.home() / ".local/bin/muse")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dirs(q: Path) -> dict:
    d = {k: q / k for k in ("in", "work", "out", "ws")}
    for p in d.values():
        p.mkdir(parents=True, exist_ok=True)
    return d


def write_atomic(path: Path, obj) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def run_job(q: Path, claimed: Path) -> dict:
    d = dirs(q)
    jid = claimed.stem
    started, t0 = now(), time.time()
    res = {"id": jid, "rc": None, "answer": "", "stderr_tail": "", "effort": None,
           "started_at": started, "finished_at": None, "seconds": None, "error": None}
    try:
        job = json.loads(claimed.read_text(encoding="utf-8"))
        effort = str(job.get("effort") or "medium")
        if effort not in EFFORTS:
            raise ValueError(f"bad effort {effort!r}")
        res["effort"] = effort
        pf = d["work"] / f"{jid}.prompt.txt"
        pf.write_text(str(job["prompt"]), encoding="utf-8")
        p = subprocess.run([muse_bin(), "exec", "--prompt-file", str(pf), "--reasoning-effort", effort,
                            "--workspace", str(d["ws"])], capture_output=True, text=True,
                           timeout=int(job.get("timeout") or 900), cwd=str(d["ws"]))
        res.update(rc=p.returncode, answer=p.stdout, stderr_tail=p.stderr[-600:])
        if p.returncode != 0:
            res["error"] = f"muse exited {p.returncode}"
        pf.unlink(missing_ok=True)
    except subprocess.TimeoutExpired as exc:
        res["error"] = f"timeout after {exc.timeout}s"
    except Exception as exc:  # recorded, never raised: one bad job must not stop the queue
        res["error"] = f"{type(exc).__name__}: {exc}"
    res["finished_at"], res["seconds"] = now(), round(time.time() - t0, 1)
    write_atomic(d["out"] / f"{jid}.json", res)
    claimed.unlink(missing_ok=True)
    return res


def claim_all(q: Path) -> list[Path]:
    d = dirs(q)
    got = []
    for f in sorted(d["in"].glob("*.json")):
        dst = d["work"] / f.name
        try:
            os.rename(f, dst)  # atomic claim; a second runner loses the race cleanly
        except OSError:
            continue
        got.append(dst)
    return got


def requeue_stale(q: Path) -> None:
    d = dirs(q)
    for f in d["work"].glob("*.json"):
        os.replace(f, d["in"] / f.name)


def process_pending(q: Path | None = None, workers: int = 1) -> list[dict]:
    q = q or queue_dir()
    jobs = claim_all(q)
    if not jobs:
        return []
    with ThreadPoolExecutor(max(1, workers)) as ex:
        return list(ex.map(lambda j: run_job(q, j), jobs))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    q = queue_dir()
    workers = int(os.environ.get("MUSE_WORKERS", "2"))
    dirs(q)
    if "--once" in argv:
        for r in process_pending(q, workers):
            print(r["id"], r["rc"], r["error"] or "", r["seconds"], flush=True)
        return 0
    requeue_stale(q)
    print(f"{now()} muse-runner start pid {os.getpid()} queue {q} muse {muse_bin()} workers {workers}", flush=True)
    sem = threading.BoundedSemaphore(max(1, workers))
    live: set = set()
    lock = threading.Lock()

    def worker(job: Path):
        try:
            r = run_job(q, job)
            print(f"{now()} {r['id']} rc={r['rc']} {r['seconds']}s {r['error'] or ''}", flush=True)
        finally:
            with lock:
                live.discard(job.name)
            sem.release()

    while True:
        (q / "heartbeat").write_text(now() + "\n")
        for job in claim_all(q):
            sem.acquire()
            with lock:
                live.add(job.name)
            threading.Thread(target=worker, args=(job,), daemon=True).start()
        time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
