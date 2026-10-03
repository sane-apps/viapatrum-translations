#!/bin/bash
# Catch-up for missed overnight burns. Safe by construction:
# - Burns ONLY if no dual-lane receipt in the last ~20h (env SANE_CATCHUP_MAX_AGE_S).
# - Execs the standard wrapper, whose global flock serializes vs a live burn.
# - SANE_CATCHUP_DRY_RUN=1 prints the decision without execing (for proof).
set -euo pipefail
ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
QDIR="$ROOT/outputs/overnight-quota"
LOG="$HOME/SaneApps/outputs/fathers-overnight/catchup.log"
MAX_AGE_S="${SANE_CATCHUP_MAX_AGE_S:-72000}"
mkdir -p "$(dirname "$LOG")"
now=$(date +%s)
newest=0
for f in "$QDIR"/*-dual.json; do
  [ -f "$f" ] || continue
  m=$(stat -f %m "$f" 2>/dev/null || echo 0)
  if [ "$m" -gt "$newest" ]; then newest=$m; fi
done
age=$((now - newest))
echo "[$(date -u +%Y%m%dT%H%M%SZ)] catchup check age=${age}s newest=${newest}" >>"$LOG"
if [ "$newest" -gt 0 ] && [ "$age" -lt "$MAX_AGE_S" ]; then
  echo "fresh burn ${age}s ago (< ${MAX_AGE_S}s); skip" >>"$LOG"
  exit 0
fi
if [ "${SANE_CATCHUP_DRY_RUN:-0}" = "1" ]; then
  echo "DRY_RUN: would exec wrapper (stale/missing receipts)" >>"$LOG"
  exit 0
fi
echo "stale receipts; exec wrapper" >>"$LOG"
exec /bin/bash "$ROOT/scripts/run-overnight-quota.sh"
