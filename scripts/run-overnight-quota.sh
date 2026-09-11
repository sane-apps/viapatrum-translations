#!/usr/bin/env bash
# Mini daily Fathers dual-lane burn (CF neurons + NVIDIA NIM).
# LaunchAgent: com.saneapps.fathers-overnight-quota
# Exit 0 for normal stop (cap / queue / content skips). Exit 2 only for infra
# worth KeepAlive — and a per-day fuse stops infinite loops.

set -euo pipefail

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
OUT="$HOME/SaneApps/outputs/fathers-overnight"
LOCK_DIR="$OUT/run.lock"
LOG_DIR="$HOME/Library/Logs/SaneApps"
DAY="$(date -u +%Y%m%d)"
FUSE="$OUT/keepalive-fuse-$DAY"
MAX_KEEPALIVE="${SANE_FATHERS_MAX_KEEPALIVE:-3}"

mkdir -p "$OUT" "$LOG_DIR"

if [[ ! -d "$ROOT" ]]; then
  echo "Missing translations root: $ROOT" >&2
  exit 0
fi

# Fuse: after N infra failures today, stop restarting
fails=0
if [[ -f "$FUSE" ]]; then
  fails="$(cat "$FUSE" 2>/dev/null || echo 0)"
fi
if [[ "${fails:-0}" -ge "$MAX_KEEPALIVE" ]]; then
  echo "Fuse tripped ($fails>=$MAX_KEEPALIVE) for $DAY — exit 0 (no KeepAlive loop)."
  exit 0
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
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

if [[ -f "$HOME/.config/nv/env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.config/nv/env"
  set +a
fi
export CF_TOKEN="${CF_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"

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

# Infra failure → bump fuse, nonzero for KeepAlive (until fuse trips)
echo $((fails + 1)) >"$FUSE"
exit 2
