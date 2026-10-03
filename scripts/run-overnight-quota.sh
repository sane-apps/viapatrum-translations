#!/usr/bin/env bash
# Fathers dual-lane burn (Cloudflare neurons + NVIDIA NIM).
# LaunchAgent: com.saneapps.fathers-overnight-quota
#
# SANE_FATHERS_FOREVER=1 (the LaunchAgent): one supervisor. It runs a batch,
# then another, and waits 10 minutes only when a batch finds nothing to take.
# The kernel flock stays held so a second copy cannot start a promote.
# Launchd restarts this process only after a crash, not after every batch.
# KeepAlive-always is still wrong: bootout used to orphan ai_promote and
# stack a second one.
#
# Without SANE_FATHERS_FOREVER: one batch, then exit. Catch-up and a manual
# run use that path and exit 0 when the supervisor already holds the flock.
#
# Exit 0: normal stop (cap, empty queue, content skip, lock busy, fuse, wall).
# Exit 2: infra. The daily fuse still caps those retries.

set -euo pipefail

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PATH="/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
OUT="$HOME/SaneApps/outputs/fathers-overnight"
LOG_DIR="$HOME/Library/Logs/SaneApps"
MAX_KEEPALIVE="${SANE_FATHERS_MAX_KEEPALIVE:-3}"
FOREVER="${SANE_FATHERS_FOREVER:-0}"
HEARTBEAT="$OUT/heartbeat"
HOLD_PID=""
HOLD_LOG=""

mkdir -p "$OUT/locks" "$LOG_DIR"

if [[ ! -f "$ROOT/scripts/overnight_quota.py" ]]; then
  echo "Bad translations root (no scripts/overnight_quota.py): $ROOT" >&2
  exit 2
fi

touch_hb() {
  date -u +%Y-%m-%dT%H:%M:%SZ >"$HEARTBEAT"
}

# Heartbeat at least every 60s. The watch treats a live lock helper with a
# silent log as a hang after 15 minutes.
paced_sleep() {
  local left="$1"
  while (( left > 0 )); do
    local step=60
    if (( left < step )); then
      step=$left
    fi
    sleep "$step"
    touch_hb
    left=$((left - step))
  done
}

note() {
  echo "[$(date -u +%Y%m%dT%H%M%SZ)] $*" | tee -a "$OUT/runner.log"
}

release_global() {
  if [[ -n "${HOLD_PID}" ]]; then
    kill "$HOLD_PID" 2>/dev/null || true
    wait "$HOLD_PID" 2>/dev/null || true
  fi
  HOLD_PID=""
  rm -f "${HOLD_LOG}"
  HOLD_LOG=""
}

acquire_global() {
  release_global
  HOLD_LOG="$OUT/locks/global-hold.$$.log"
  set +e
  /usr/bin/python3 -u "$ROOT/scripts/fathers_run_lock.py" try-global "wrapper:$$" \
    >"$HOLD_LOG" 2>&1 &
  HOLD_PID=$!
  set -e
  local held=0
  local _
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
    note "flock busy"
    cat "$HOLD_LOG" 2>/dev/null || true
    release_global
    return 1
  fi
  return 0
}

fuse_tripped() {
  local day fuse fails
  day="$(date -u +%Y%m%d)"
  fuse="$OUT/keepalive-fuse-$day"
  fails=0
  if [[ -f "$fuse" ]]; then
    fails="$(cat "$fuse" 2>/dev/null || echo 0)"
  fi
  [[ "$fails" =~ ^[0-9]+$ ]] || fails=0
  if (( fails >= MAX_KEEPALIVE )); then
    note "fuse tripped ($fails>=$MAX_KEEPALIVE) for $day"
    return 0
  fi
  return 1
}

# One batch. Lock must already be held. Returns the quota exit code.
run_one_batch() {
  local day fuse fails stamp rc
  day="$(date -u +%Y%m%d)"
  fuse="$OUT/keepalive-fuse-$day"
  fails=0
  if [[ -f "$fuse" ]]; then
    fails="$(cat "$fuse" 2>/dev/null || echo 0)"
  fi
  [[ "$fails" =~ ^[0-9]+$ ]] || fails=0
  if (( fails >= MAX_KEEPALIVE )); then
    note "fuse tripped ($fails>=$MAX_KEEPALIVE) for $day — skip batch"
    return 0
  fi

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  note "fathers batch start host=$(hostname -s) fuse=$fails/$MAX_KEEPALIVE forever=$FOREVER"
  touch_hb

  set +e
  nice -n 10 /usr/bin/python3 scripts/hold_reconcile.py --apply 2>&1 | tail -2 | tee -a "$OUT/runner.log" || true
  nice -n 10 /usr/bin/python3 scripts/overnight_quota.py \
    --lanes both \
    --agent overnight-mini \
    --max-claims 12 \
    --reserve 800 --mode auto 2>&1 | tee -a "$OUT/nightly-$day.log"
  rc=${PIPESTATUS[0]:-$?}
  set -e

  note "fathers batch end rc=$rc"
  touch_hb

  if [[ "$rc" -eq 0 ]]; then
    nice -n 10 /usr/bin/python3 scripts/nightly_publish.py 2>&1 | tee -a "$OUT/runner.log" || true
    return 0
  fi

  echo $((fails + 1)) >"$fuse"
  return 2
}

load_env() {
  if [[ -f "$HOME/.config/nv/env" ]]; then
    set -a
    # shellcheck disable=SC1090
    if ! source "$HOME/.config/nv/env"; then
      echo "env load failed: $HOME/.config/nv/env" >&2
      exit 2
    fi
    set +a
  else
    echo "env file missing: $HOME/.config/nv/env (lane keys unavailable)" >&2
  fi
  export CF_TOKEN="${CF_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
  export SANE_FATHERS_WRAPPER=1
  export SANE_FATHERS_NESTED=1
}

cd "$ROOT"
load_env
touch_hb

if [[ "$FOREVER" != "1" ]]; then
  if ! acquire_global; then
    echo "Another Fathers burn holds the global flock; exit 0."
    exit 0
  fi
  trap release_global EXIT
  run_one_batch
  exit $?
fi

note "forever supervisor start pid=$$"
trap 'release_global; note "forever supervisor stop"; exit 0' INT TERM

while true; do
  if fuse_tripped; then
    paced_sleep 1800
    continue
  fi
  if [[ -z "$HOLD_PID" ]] || ! kill -0 "$HOLD_PID" 2>/dev/null; then
    if ! acquire_global; then
      paced_sleep 60
      continue
    fi
  fi
  batch_start=$(date +%s)
  set +e
  run_one_batch
  rc=$?
  set -e
  elapsed=$(( $(date +%s) - batch_start ))
  if [[ "$rc" -ne 0 ]]; then
    note "infra rc=$rc; backoff 5 min"
    paced_sleep 300
  elif (( elapsed < 45 )); then
    note "nothing to take (${elapsed}s); wait 10 min"
    paced_sleep 600
  else
    note "batch ran ${elapsed}s; next batch shortly"
    paced_sleep 10
  fi
done
