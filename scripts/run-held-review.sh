#!/bin/bash
# Weekly Claude review of held sections (owner 2026-10-03). launchd:
# com.saneapps.fathers-held-review, Sundays 04:30. scripts/held_review.py
# exports sections held for confirmed problems, has headless Claude judge each
# finding against the source, and releases the sections whose findings are
# noise or whose real errors its fixes correct; lanes then re-read and certify.
# Exit 3 = Claude not logged in on the Mini (health_watch alerts on it).
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:$PATH"
ROOT="$HOME/SaneApps/clients/translations"
LOCK="/tmp/fathers-held-review.lock"
mkdir "$LOCK" 2>/dev/null || { echo "$(date '+%F %T') another review is running"; exit 0; }
trap 'rmdir "$LOCK"' EXIT
cd "$ROOT" || exit 1
# CLAUDE_CODE_OAUTH_TOKEN, when present in the sane-env loader, authenticates
# headless claude; otherwise the CLI's own login is used.
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
echo "$(date '+%F %T') held review start"
timeout 14400 nice -n 10 python3 scripts/held_review.py run
rc=$?
echo "$(date '+%F %T') held review exit $rc"
exit $rc
