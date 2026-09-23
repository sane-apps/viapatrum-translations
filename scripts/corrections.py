#!/usr/bin/env python3
"""Snapshot open reader-correction issues for the digest (no tokens spent)."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "corrections-open.json"
REPO = "sane-apps/translations"


def issues(state: str, limit: int = 50) -> list:
    try:
        raw = subprocess.run(
            ["gh", "issue", "list", "-R", REPO, "--label", "correction",
             "--state", state, "--limit", str(limit),
             "--json", "number,title,createdAt,closedAt,labels"],
            capture_output=True, text=True, timeout=60, check=True).stdout
        return json.loads(raw or "[]")
    except (subprocess.SubprocessError, ValueError) as exc:
        print(f"corrections: gh failed ({exc})")
        return []


def main() -> int:
    open_issues = issues("open")
    OUT.write_text(json.dumps({"taken": datetime.now(timezone.utc).isoformat(),
                               "open": open_issues}, indent=1))
    print(f"corrections: {len(open_issues)} open")
    for issue in open_issues[:10]:
        labels = ",".join(label["name"] for label in issue.get("labels", []))
        print(f"  #{issue['number']} {issue['title'][:80]} [{labels}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
