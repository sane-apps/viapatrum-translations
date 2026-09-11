#!/usr/bin/env python3
"""Claim board helper: list free claims, take one atomically, print START_HERE."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "docs" / "CLAIMS.md"
START = ROOT / "docs" / "START_HERE.md"
LOCKS = ROOT / "docs" / "claim-locks"


def parse_open_table(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_open = False
    headers: list[str] = []
    for line in text.splitlines():
        if line.startswith("## Open / active claims"):
            in_open = True
            continue
        if in_open and line.startswith("## "):
            break
        if not in_open or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].startswith("---"):
            continue
        if cells[0] == "Claim ID":
            headers = cells
            continue
        if not headers:
            continue
        row = dict(zip(headers, cells))
        rows.append(row)
    return rows


def print_rows(rows: list[dict[str, str]]) -> None:
    for r in rows:
        print(
            f"{r.get('Claim ID'):12}  {r.get('Status'):8}  "
            f"{r.get('Book slug')}  ::  {r.get('Slice (sections)')}"
        )


def cmd_list(command: str) -> int:
    text = CLAIMS.read_text(encoding="utf-8")
    rows = parse_open_table(text)
    show = rows if command == "all" else [r for r in rows if r.get("Status") == "free"]
    if not show:
        print("No matching claims.", file=sys.stderr)
        return 1
    print_rows(show)
    print(
        f"\n{len(show)} row(s). Take one with:\n"
        f"  python3 scripts/claims.py take <claim-id> --agent YourName"
    )
    return 0


def cmd_start() -> int:
    print(START)
    print("---")
    print(START.read_text(encoding="utf-8")[:1200])
    print("\n…(open the full file)…")
    return 0


def claim_line_pattern(claim_id: str) -> re.Pattern[str]:
    # Match the whole markdown table row for this free claim.
    return re.compile(
        rf"^\| {re.escape(claim_id)} \| free \|.*\|$",
        re.MULTILINE,
    )


def agent_already_claimed(text: str, agent: str) -> str | None:
    for row in parse_open_table(text):
        if row.get("Status") == "claimed" and row.get("Agent", "").strip() == agent:
            return row.get("Claim ID")
    return None


def cmd_take(claim_id: str, agent: str) -> int:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", claim_id):
        print(f"Bad claim id: {claim_id}", file=sys.stderr)
        return 2
    if not agent.strip() or agent.strip().lower() in {"yourname", "me", "agent"}:
        print("Pass a real --agent name.", file=sys.stderr)
        return 2

    text = CLAIMS.read_text(encoding="utf-8")
    held = agent_already_claimed(text, agent.strip())
    if held:
        print(
            f"You already hold claimed row `{held}`. "
            f"Set it to review/done before taking another.",
            file=sys.stderr,
        )
        return 1

    rows = {r.get("Claim ID"): r for r in parse_open_table(text)}
    row = rows.get(claim_id)
    if not row:
        print(f"Unknown claim id: {claim_id}", file=sys.stderr)
        return 1
    if row.get("Status") != "free":
        print(f"`{claim_id}` is not free (status={row.get('Status')}).", file=sys.stderr)
        return 1

    LOCKS.mkdir(parents=True, exist_ok=True)
    lock_dir = LOCKS / claim_id
    try:
        lock_dir.mkdir()  # atomic; fails if exists
    except FileExistsError:
        print(
            f"`{claim_id}` lock already exists under docs/claim-locks/. "
            f"Take the next free claim.",
            file=sys.stderr,
        )
        return 1

    (lock_dir / "agent.txt").write_text(agent.strip() + "\n", encoding="utf-8")
    today = date.today().isoformat()
    branch = f"wip/{claim_id}"
    new_line = (
        f"| {claim_id} | claimed | {row.get('Book slug')} | "
        f"{row.get('Slice (sections)')} | {agent.strip()} | {today} | "
        f"{branch} | {row.get('Notes', '')} |"
    )
    pat = claim_line_pattern(claim_id)
    if not pat.search(text):
        # roll back lock
        (lock_dir / "agent.txt").unlink(missing_ok=True)
        lock_dir.rmdir()
        print(f"Could not find free row for `{claim_id}` in CLAIMS.md.", file=sys.stderr)
        return 1

    updated = pat.sub(new_line, text, count=1)
    CLAIMS.write_text(updated, encoding="utf-8")
    print(f"Claimed `{claim_id}` as {agent.strip()}.")
    print(f"Branch: {branch}")
    print(f"Lock:   {lock_dir.relative_to(ROOT)}")
    print("Next: create that branch, read START_HERE + SOP, translate only that slice.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Translations claim helper")
    ap.add_argument(
        "command",
        choices=["free", "start", "all", "take"],
        nargs="?",
        default="free",
    )
    ap.add_argument("claim_id", nargs="?", help="For take: claim id")
    ap.add_argument("--agent", default="", help="For take: your name")
    args = ap.parse_args()

    if args.command == "start":
        return cmd_start()
    if args.command == "take":
        if not args.claim_id or not args.agent:
            print("Usage: claims.py take <claim-id> --agent YourName", file=sys.stderr)
            return 2
        return cmd_take(args.claim_id, args.agent)
    return cmd_list(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
