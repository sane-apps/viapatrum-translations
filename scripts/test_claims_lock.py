#!/usr/bin/env python3
"""Regression: releasing a claim drops its lock dir so re-take works.

Live 2026-09-23: mark-free left docs/claim-locks/<id>/ behind, so every
re-take failed with "lock already exists" and the overnight queue stalled.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import claims as C  # noqa: E402

ROW = "| cyr-isa-t1 | free | cyril-alexandria-isaiah | logos1-open |  |  |  | auto queue |"
HDR = "| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |"


def _board(tmp: Path) -> None:
    C.CLAIMS = tmp / "CLAIMS.md"
    C.LOCKS = tmp / "claim-locks"
    C.CLAIMS.write_text(
        "# Claims\n\n## Open / active claims\n\n" + HDR + "\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + ROW + "\n"
        + "\n## How to claim\n",
        encoding="utf-8",
    )


def test_release_drops_lock_and_retake() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="claims-lock-"))
    _board(tmp)
    assert C.cmd_take("cyr-isa-t1", "t-agent", quiet=True) == 0
    assert (C.LOCKS / "cyr-isa-t1").is_dir()
    assert C.cmd_mark("cyr-isa-t1", "free", "t-agent") == 0
    assert not (C.LOCKS / "cyr-isa-t1").exists()
    assert C.cmd_take("cyr-isa-t1", "t-agent2", quiet=True) == 0


def main() -> int:
    test_release_drops_lock_and_retake()
    print("ok release_drops_lock_and_retake")
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
