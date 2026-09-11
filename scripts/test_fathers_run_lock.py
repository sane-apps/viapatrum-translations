#!/usr/bin/env python3
"""Regression tests for Fathers overnight flock + promote exit mapping."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_flock_busy() -> None:
    lock_root = tempfile.mkdtemp(prefix="fathers-flock-")
    env = os.environ.copy()
    env["SANE_FATHERS_LOCK_ROOT"] = lock_root
    env["PYTHONUNBUFFERED"] = "1"
    p1 = subprocess.Popen(
        [sys.executable, "-u", str(SCRIPTS / "fathers_run_lock.py"), "try-global", "t1"],
        env=env,
        stdout=subprocess.PIPE,
        text=True,
    )
    line = ""
    deadline = time.time() + 5
    while time.time() < deadline:
        line = p1.stdout.readline() if p1.stdout else ""
        if line.startswith("HELD"):
            break
        time.sleep(0.05)
    assert line.startswith("HELD"), repr(line)
    p2 = subprocess.run(
        [sys.executable, "-u", str(SCRIPTS / "fathers_run_lock.py"), "try-global", "t2"],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert p2.returncode == 1 and "BUSY" in p2.stdout, (p2.returncode, p2.stdout)
    p1.send_signal(15)
    p1.wait(timeout=3)


def test_claim_lock_and_nested_global() -> None:
    from fathers_run_lock import acquire_claim, acquire_global, release_all

    lock_root = tempfile.mkdtemp(prefix="fathers-claim-")
    os.environ["SANE_FATHERS_LOCK_ROOT"] = lock_root
    # Re-import paths already loaded — mutate module LOCK_ROOT
    import fathers_run_lock as frl

    frl.LOCK_ROOT = Path(lock_root)
    g = acquire_global("outer")
    assert g is not None
    assert acquire_global("other") is None
    c1 = acquire_claim("jer-h8", "p1")
    assert c1 is not None
    assert acquire_claim("jer-h8", "p2") is None
    assert acquire_claim("jer-h9", "p3") is not None
    release_all()


def test_wall_exit_code() -> None:
    from fathers_run_lock import clear_wall_deadline, install_wall_deadline

    install_wall_deadline(1, label="test", exit_code=4)
    try:
        time.sleep(3)
        raise AssertionError("wall did not fire")
    except SystemExit as exc:
        assert exc.code == 4, exc.code
    finally:
        clear_wall_deadline()


def main() -> int:
    test_flock_busy()
    print("ok flock_busy")
    test_claim_lock_and_nested_global()
    print("ok claim_lock")
    test_wall_exit_code()
    print("ok wall_exit_4")
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
