#!/bin/bash
# Daily beliefs-map refresh (owner 2026-10-03: the timeline grows as works
# arrive). launchd com.saneapps.fathers-beliefs, 03:30. Embeds new or changed
# paragraphs, re-searches every question, grades only passages not graded
# under the current definitions, and rewrites the site data; the next ship
# publishes it. New deciding verdicts wait for the Claude audit before they
# count (doctrine_map.py report applies outputs/doctrine-map/audit/*.json).
# Exits 1 when any step fails, so launchctl and fathers-watch see it.
set -u
export PATH="/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOCK="/tmp/fathers-beliefs.lock"
mkdir "$LOCK" 2>/dev/null || { echo "$(date +%T) already running"; exit 0; }
trap 'rmdir "$LOCK"' EXIT
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
ROOT="$HOME/SaneApps/clients/translations"
cd "$ROOT" || exit 1
PY="$HOME/Models/kokoro/.venv/bin/python"
GATE="$HOME/SaneApps/infra/SaneProcess/scripts/llm_api_research_gate.rb"
RECEIPTS="$HOME/SaneApps/infra/SaneProcess/outputs/llm-api-research"
source "$ROOT/scripts/receipt_refresh.sh" || { echo "$(date +%T) receipt_refresh.sh missing"; exit 1; }
# Grading needs doctrine-grade receipts for both graders and the Nemotron
# referee (doctrine_map.py receipts_ok). Nothing refreshed them, so the grade
# step was BLOCKED on 2026-10-04 and 10-05 while the job still exited 0.
grade_ok=1
NOTES="doctrine_map grade via llm_bakeoff.vendor_call, thinking off" refresh @cf/moonshotai/kimi-k2.6 doctrine-grade "$KW" || grade_ok=0
NOTES="doctrine_map grade via llm_bakeoff.vendor_call" refresh @cf/openai/gpt-oss-120b doctrine-grade '{}' || grade_ok=0
NOTES="doctrine_map referee via llm_bakeoff.vendor_call" refresh nvidia/nemotron-3-ultra-550b-a55b \
  doctrine-grade '{"reasoning_effort":"none"}' nvidia nemotron-3-ultra || grade_ok=0
rc=0
for step in index search grade report; do
  if [ "$step" = grade ] && [ "$grade_ok" = 0 ]; then
    echo "$(date +%T) grade FAILED: receipt refresh failed, grading skipped"; rc=1; continue
  fi
  args=(); [ "$step" = grade ] && args=(--workers 10)  # only grade runs calls in parallel
  echo "$(date +%T) $step"
  nice -n 10 timeout 10800 "$PY" scripts/doctrine_map.py "$step" ${args[@]+"${args[@]}"} || { echo "$(date +%T) $step FAILED"; rc=1; }
done
exit $rc
