#!/usr/bin/env bash
# Mini weekly independent re-review (second-model sample + corrections snapshot).
# LaunchAgent: com.saneapps.fathers-independent-review (Sundays 03:00).
# Findings never fail the job. Exit codes: 0 ran; independent_review.py's own
# non-zero exit when it crashed; 75 another Fathers job holds the global lock.
# Network-bound: it does not take the site's outputs/build.lock.

set -euo pipefail

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
OUT="$HOME/SaneApps/outputs/fathers-independent-review"
LOG_DIR="$HOME/Library/Logs/SaneApps"

mkdir -p "$OUT" "$LOG_DIR"

if [[ ! -d "$ROOT" ]]; then
  echo "Missing translations root: $ROOT" >&2
  exit 0
fi

# Yield to ai_promote (and the retired overnight burn) via the same global
# flock. Its holder writes pid, owner and start time to global-burn.lock.meta.json.
HOLD_LOG="$OUT/lock.$$.log"
set +e
/usr/bin/python3 -u "$ROOT/scripts/fathers_run_lock.py" try-global "indreview:$$" \
  >"$HOLD_LOG" 2>&1 &
HOLD_PID=$!
set -e
held=0
for _ in $(seq 1 100); do  # up to 10 s for the lock helper to start
  if ! kill -0 "$HOLD_PID" 2>/dev/null; then
    break
  fi
  if grep -q '^HELD' "$HOLD_LOG" 2>/dev/null; then
    held=1
    break
  fi
  if grep -q '^BUSY' "$HOLD_LOG" 2>/dev/null; then
    break
  fi
  sleep 0.1
done
if [[ "$held" -ne 1 ]]; then
  META="${SANE_FATHERS_LOCK_ROOT:-$HOME/SaneApps/outputs/fathers-overnight/locks}/global-burn.lock.meta.json"
  WHO="$(/usr/bin/python3 - "$META" <<'PY' 2>/dev/null || echo "holder unknown"
import json, sys
from datetime import datetime, timezone
m = json.load(open(sys.argv[1]))
age = (datetime.now(timezone.utc) - datetime.fromisoformat(m["started"])).total_seconds() // 60
print(f"pid {m.get('pid')} ({m.get('owner')}) for {int(age)} min")
PY
)"
  echo "[$(date -u +%Y%m%dT%H%M%SZ)] BUSY: the global Fathers lock is held by $WHO; independent review skipped (exit 75)" | tee -a "$OUT/runner.log"
  kill "$HOLD_PID" 2>/dev/null || true
  wait "$HOLD_PID" 2>/dev/null || true
  rm -f "$HOLD_LOG"
  exit 75
fi
cleanup() {
  kill "$HOLD_PID" 2>/dev/null || true
  wait "$HOLD_PID" 2>/dev/null || true
  rm -f "$HOLD_LOG"
}
trap cleanup EXIT

if [[ -f "$HOME/.config/nv/env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.config/nv/env"
  set +a
fi
export CF_TOKEN="${CF_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
export SANE_FATHERS_WRAPPER=1
export SANE_FATHERS_NESTED=1

cd "$ROOT"
echo "[$(date -u +%Y%m%dT%H%M%SZ)] independent review start host=$(hostname -s)" | tee -a "$OUT/runner.log"

set +e
nice -n 10 /usr/bin/python3 scripts/independent_review.py --sample 5 2>&1 | tee -a "$OUT/runner.log"
RC=$?
nice -n 10 /usr/bin/python3 scripts/corrections.py 2>&1 | tee -a "$OUT/runner.log" || true
set -e

echo "[$(date -u +%Y%m%dT%H%M%SZ)] independent review end rc=$RC" | tee -a "$OUT/runner.log"
exit "$RC"
