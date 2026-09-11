#!/usr/bin/env python3
"""Single-instance + per-claim locks for Fathers overnight/promote.

Uses fcntl.flock (kernel-held). mkdir+pid locks were stolen by a second
wrapper that treated a live lock as stale, then trap-cleanup deleted it.
"""
from __future__ import annotations

import atexit
import fcntl
import json
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_ROOT = Path(
    os.environ.get("SANE_FATHERS_LOCK_ROOT")
    or (Path.home() / "SaneApps/outputs/fathers-overnight/locks")
)


@dataclass
class HeldLock:
    path: Path
    kind: str
    key: str
    fd: int = -1
    meta_path: Path | None = None

    def release(self) -> None:
        try:
            if self.fd >= 0:
                try:
                    fcntl.flock(self.fd, fcntl.LOCK_UN)
                except OSError:
                    pass
                try:
                    os.close(self.fd)
                except OSError:
                    pass
                self.fd = -1
            if self.meta_path and self.meta_path.is_file():
                try:
                    self.meta_path.unlink()
                except OSError:
                    pass
        except OSError:
            pass


_HELD: list[HeldLock] = []


def _try_flock(lock_path: Path, meta: dict) -> HeldLock | None:
    LOCK_ROOT.mkdir(parents=True, exist_ok=True)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    payload = {
        **meta,
        "pid": os.getpid(),
        "started": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = lock_path.with_suffix(lock_path.suffix + ".meta.json")
    os.ftruncate(fd, 0)
    os.write(fd, (json.dumps(payload) + "\n").encode("utf-8"))
    os.fsync(fd)
    meta_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    held = HeldLock(
        path=lock_path,
        kind=str(meta.get("kind") or "lock"),
        key=str(meta.get("key") or ""),
        fd=fd,
        meta_path=meta_path,
    )
    _HELD.append(held)
    return held


def acquire_global(owner: str) -> HeldLock | None:
    """One Fathers overnight (or standalone promote) process at a time."""
    return _try_flock(
        LOCK_ROOT / "global-burn.lock",
        {"kind": "global", "key": "burn", "owner": owner},
    )


def acquire_claim(claim_id: str, owner: str) -> HeldLock | None:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in claim_id)
    return _try_flock(
        LOCK_ROOT / f"claim-{safe}.lock",
        {"kind": "claim", "key": claim_id, "owner": owner},
    )


def release_all() -> None:
    while _HELD:
        _HELD.pop().release()


atexit.register(release_all)


def install_wall_deadline(
    seconds: int,
    label: str = "fathers-job",
    exit_code: int = 0,
) -> None:
    """Hard stop so a hung NIM call cannot run forever (macOS has no GNU timeout).

    Promote walls must use exit_code=4 so overnight does not treat timeout as done.
    Overnight job walls may use 0 (wrapper/fuse: normal stop, not infra fail).
    """
    seconds = int(seconds)
    code = int(exit_code)
    if seconds <= 0:
        return

    def _boom(_signum=None, _frame=None) -> None:  # noqa: ANN001
        release_all()
        print(
            f"WALL_DEADLINE {label} after {seconds}s — exiting {code}",
            flush=True,
        )
        raise SystemExit(code)

    signal.signal(signal.SIGALRM, _boom)
    signal.alarm(seconds)


def run_bounded(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict,
    timeout_s: int,
    label: str = "child",
) -> int:
    """Run a child in its own session; kill the group if it outlives timeout_s.

    Returns the child's exit code, or 4 on wall timeout (same as claim_wall).
    """
    import subprocess

    timeout_s = max(1, int(timeout_s))
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, start_new_session=True)
    try:
        return int(proc.wait(timeout=timeout_s))
    except subprocess.TimeoutExpired:
        print(f"CHILD_WALL {label} after {timeout_s}s — SIGTERM", flush=True)
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            print(f"CHILD_WALL {label} SIGKILL", flush=True)
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=5)
        return 4


def clear_wall_deadline() -> None:
    try:
        signal.alarm(0)
    except Exception:  # noqa: BLE001
        pass


def main(argv: list[str] | None = None) -> int:
    """CLI for the bash wrapper: try-global | status."""
    args = list(argv or sys.argv[1:])
    if not args or args[0] in {"-h", "--help"}:
        print("usage: fathers_run_lock.py try-global|status [owner]", file=sys.stderr)
        return 2
    cmd = args[0]
    if cmd == "try-global":
        owner = args[1] if len(args) > 1 else f"cli:{os.getpid()}"
        held = acquire_global(owner)
        if held is None:
            print("BUSY", flush=True)
            return 1
        print(f"HELD pid={os.getpid()} path={held.path}", flush=True)
        # Hold until SIGTERM/SIGINT — wrapper keeps this child alive for the burn.
        def _stop(_s=None, _f=None) -> None:  # noqa: ANN001
            release_all()
            raise SystemExit(0)

        signal.signal(signal.SIGTERM, _stop)
        signal.signal(signal.SIGINT, _stop)
        while True:
            signal.pause()
    if cmd == "status":
        print(json.dumps({"lock_root": str(LOCK_ROOT), "held": len(_HELD)}, indent=2))
        return 0
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
