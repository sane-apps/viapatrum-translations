#!/usr/bin/env bash
# Mini daily Fathers dual-lane burn (CF neurons + NVIDIA NIM).
# LaunchAgent: com.saneapps.fathers-overnight-quota
# Exit 0 when capped/exhausted; nonzero on interruptible failure so KeepAlive retries.

set -euo pipefail

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
OUT="$HOME/SaneApps/outputs/fathers-overnight"
LOCK_DIR="$OUT/run.lock"
LOG_DIR="$HOME/Library/Logs/SaneApps"
mkdir -p "$OUT" "$LOG_DIR"

if [[ ! -d "$ROOT" ]]; then
  echo "Missing translations root: $ROOT" >&2
  exit 2
fi

# Single-instance: LaunchAgent KeepAlive must not stack overlapping burns.
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  # Stale lock if holder is dead
  old_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  if [[ -n "${old_pid:-}" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "Another overnight run holds $LOCK_DIR (pid $old_pid); exit 0."
    exit 0
  fi
  rm -rf "$LOCK_DIR"
  mkdir "$LOCK_DIR"
fi
echo $$ >"$LOCK_DIR/pid"
cleanup() { rm -rf "$LOCK_DIR"; }
trap cleanup EXIT

# Load CF + NVIDIA keys (no prompt floods)
if [[ -f "$HOME/.config/nv/env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.config/nv/env"
  set +a
fi
export CF_TOKEN="${CF_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"

cd "$ROOT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
echo "[$STAMP] fathers overnight start host=$(hostname -s)" | tee -a "$OUT/runner.log"

# Soft git sync if this checkout has a remote (best-effort; never block burn)
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$ROOT" fetch --quiet origin 2>/dev/null || true
fi

set +e
nice -n 10 /usr/bin/python3 scripts/overnight_quota.py \
  --lanes both \
  --agent overnight-mini \
  --max-claims 12 \
  --reserve 800
RC=$?
set -e

echo "[$(date -u +%Y%m%dT%H%M%SZ)] fathers overnight end rc=$RC" | tee -a "$OUT/runner.log"

# Cap / empty queue / already done today → success (no KeepAlive loop)
if [[ "$RC" -eq 0 ]]; then
  exit 0
fi

# Transient failure → nonzero so LaunchAgent KeepAlive (SuccessfulExit=false) retries
exit "$RC"
