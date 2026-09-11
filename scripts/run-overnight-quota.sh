#!/usr/bin/env bash
# Mini daily Fathers dual-lane burn (CF neurons + NVIDIA NIM).
# LaunchAgent: com.saneapps.fathers-overnight-quota
# Exit 0 for normal stop (cap / queue / content skips / lock held / fuse / wall).
# Exit 2 only for infra — calendar agent has no KeepAlive; fuse kept for safety.

set -euo pipefail

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
OUT="$HOME/SaneApps/outputs/fathers-overnight"
LOG_DIR="$HOME/Library/Logs/SaneApps"
DAY="$(date -u +%Y%m%d)"
FUSE="$OUT/keepalive-fuse-$DAY"
MAX_KEEPALIVE="${SANE_FATHERS_MAX_KEEPALIVE:-3}"

mkdir -p "$OUT/locks" "$LOG_DIR"

if [[ ! -d "$ROOT" ]]; then
  echo "Missing translations root: $ROOT" >&2
  exit 0
fi

fails=0
if [[ -f "$FUSE" ]]; then
  fails="$(cat "$FUSE" 2>/dev/null || echo 0)"
fi
if [[ "${fails:-0}" -ge "$MAX_KEEPALIVE" ]]; then
  echo "Fuse tripped ($fails>=$MAX_KEEPALIVE) for $DAY — exit 0."
  exit 0
fi

# Kernel flock via helper process — cannot be stolen by stale-pid logic.
# Per-PID hold log so overlapping wrappers cannot truncate each other's HELD line.
HOLD_LOG="$OUT/locks/global-hold.$$.log"
set +e
/usr/bin/python3 -u "$ROOT/scripts/fathers_run_lock.py" try-global "wrapper:$$" \
  >"$HOLD_LOG" 2>&1 &
HOLD_PID=$!
set -e
held=0
for _ in $(seq 1 30); do
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
  echo "Another Fathers burn holds the global flock; exit 0."
  kill "$HOLD_PID" 2>/dev/null || true
  wait "$HOLD_PID" 2>/dev/null || true
  cat "$HOLD_LOG" 2>/dev/null || true
  rm -f "$HOLD_LOG"
  exit 0
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
# Overnight owns the burn; child promotes only take per-claim flocks.
export SANE_FATHERS_WRAPPER=1
export SANE_FATHERS_NESTED=1

cd "$ROOT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
echo "[$STAMP] fathers overnight start host=$(hostname -s) fuse=$fails/$MAX_KEEPALIVE" | tee -a "$OUT/runner.log"

set +e
nice -n 10 /usr/bin/python3 scripts/overnight_quota.py \
  --lanes both \
  --agent overnight-mini \
  --max-claims 12 \
  --reserve 800
RC=$?
set -e

echo "[$(date -u +%Y%m%dT%H%M%SZ)] fathers overnight end rc=$RC" | tee -a "$OUT/runner.log"

if [[ "$RC" -eq 0 ]]; then
  exit 0
fi

echo $((fails + 1)) >"$FUSE"
exit 2
