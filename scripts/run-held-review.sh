#!/bin/bash
# Weekly Claude review of held sections (owner 2026-10-03). launchd:
# com.saneapps.fathers-held-review, Sundays 04:30. scripts/held_review.py
# exports sections held for confirmed problems, has headless Claude judge each
# finding against the source, and releases the sections whose findings are
# noise or whose real errors its fixes correct; lanes then re-read and certify.
# Exit 3 = Claude not logged in on the Mini (fathers_watch.py alerts on it).
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
echo "$(date '+%F %T') held review start"
timeout 14400 nice -n 10 python3 scripts/held_review.py run
rc=$?
echo "$(date '+%F %T') held review exit $rc"
exit $rc
