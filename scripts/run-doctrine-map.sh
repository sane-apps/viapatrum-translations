#!/bin/bash
# Daily beliefs-map refresh (owner 2026-10-03: the timeline grows as works
# arrive). launchd com.saneapps.fathers-beliefs, 03:30. Embeds new or changed
# paragraphs, re-searches every question, grades only passages not graded
# under the current definitions, and rewrites the site data; the next ship
# publishes it. New deciding verdicts wait for the Claude audit before they
# count (doctrine_map.py report applies outputs/doctrine-map/audit/*.json).
set -u
export PATH="/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOCK="/tmp/fathers-beliefs.lock"
mkdir "$LOCK" 2>/dev/null || { echo "$(date +%T) already running"; exit 0; }
trap 'rmdir "$LOCK"' EXIT
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
cd "$HOME/SaneApps/clients/translations" || exit 1
PY="$HOME/Models/kokoro/.venv/bin/python"
for step in index search grade report; do
  echo "$(date +%T) $step"
  nice -n 10 timeout 10800 "$PY" scripts/doctrine_map.py "$step" --workers 10 || echo "$(date +%T) $step FAILED"
done
