#!/bin/bash
# Weekly Claude review of held sections (owner 2026-10-03). launchd:
# com.saneapps.fathers-held-review, daily 04:30 since 2026-10-14: it runs when
# the last good review is 6+ days old, so a failed week retries the next
# morning instead of waiting seven days (the Oct 11 run hit Claude's weekly
# limit and nothing retried). scripts/held_review.py
# exports sections held for confirmed problems, has headless Claude judge each
# finding against the source, and releases the sections whose findings are
# noise or whose real errors its fixes correct; lanes then re-read and certify.
# Exit 3 = Claude unavailable: not logged in, or out of usage (fathers_watch.py
# alerts with the reason held_review.py logged).
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:$PATH"
ROOT="$HOME/SaneApps/clients/translations"
LOCK="/tmp/fathers-held-review.lock"
# One held review at a time. The lock directory holds "<pid> <start epoch>", so a
# lock left by a killed run is taken over, and a live one is reported (BUSY,
# exit 75) instead of passing as a quiet, healthy run. Network-bound: this job
# does not take the site's outputs/build.lock, so it keeps running during builds.
if ! mkdir "$LOCK" 2>/dev/null; then
  read -r opid ostart 2>/dev/null < "$LOCK/pid"
  if [ -n "${opid:-}" ] && kill -0 "$opid" 2>/dev/null; then
    echo "$(date '+%F %T') BUSY: held review pid $opid has run $(( ($(date +%s) - ${ostart:-$(date +%s)}) / 60 )) min; exit 75"
    exit 75
  fi
  echo "$(date '+%F %T') lock left by pid ${opid:-?}, which is not running; taking it"
  rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null
  mkdir "$LOCK" 2>/dev/null || { echo "$(date '+%F %T') BUSY: another held review took the lock first; exit 75"; exit 75; }
fi
echo "$$ $(date +%s)" > "$LOCK/pid"
trap 'rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null' EXIT
cd "$ROOT" || exit 1
# CLAUDE_CODE_OAUTH_TOKEN, when present in the sane-env loader, authenticates
# headless claude; otherwise the CLI's own login is used.
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
OK_STAMP="$ROOT/outputs/held-review/last-ok"
if [ -f "$OK_STAMP" ] && [ $(( $(date +%s) - $(stat -f %m "$OK_STAMP") )) -lt $(( 6 * 86400 )) ] && [ "${HELD_REVIEW_FORCE:-0}" != 1 ]; then
  echo "$(date '+%F %T') held review: last good run $(date -r "$(stat -f %m "$OK_STAMP")" '+%F'), under 6 days; nothing to do"
  exit 0
fi
echo "$(date '+%F %T') held review start"
# Opus through plan_calls (waits out spent usage windows), owner 2026-10-19. No cheap first judge:
# Muse's "real" calls matched Opus on the bench, but on the live backlog 3 of 10 of its fixes were
# wrong (one deleted a clause), so every verdict and fix comes from Opus.
export HELD_REVIEW_MODEL="${HELD_REVIEW_MODEL:-claude-opus-5-5}"
timeout 86400 nice -n 10 python3 scripts/held_review.py run
rc=$?
[ "$rc" = 0 ] && { mkdir -p "$(dirname "$OK_STAMP")"; touch "$OK_STAMP"; }
echo "$(date '+%F %T') held review exit $rc"
exit $rc
