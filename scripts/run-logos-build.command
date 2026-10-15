#!/bin/bash
# Logos Personal Book build, opened in Terminal by launchd
# (com.saneapps.fathers-logos-build: /usr/bin/open -g -a Terminal <this file>).
#
# Why Terminal: a launchd job's osascript has no Accessibility grant, so every
# scheduled run since at least 2026-09-27 died "PB tool never became AX-ready"
# (proved 2026-10-14 with a one-shot launchd probe). Terminal already holds the
# grant, and a script it runs inherits it, so no new security setting is needed.
# launchd only sees `open` succeed, so the real exit code goes to
# outputs/logos_runs/last-exit for fathers_watch. The window closes itself.
set -u
# launchd's EnvironmentVariables do not reach a script Terminal runs.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
export SANE_TRANSLATIONS_ROOT="$HOME/SaneApps/clients/translations"
ROOT="$HOME/SaneApps/clients/translations"
SITE="$HOME/SaneApps/websites/fathers.saneapps.com"
LOG="$HOME/Library/Logs/SaneApps/fathers-logos-build.out.log"
STATUS="$ROOT/outputs/logos_runs/last-exit"
mkdir -p "$(dirname "$STATUS")"
exec >>"$LOG" 2>&1
close_window() {
  ( sleep 3; /usr/bin/osascript -e 'tell application "Terminal" to close (every window whose name contains "run-logos-build.command")' ) >/dev/null 2>&1 &
  disown
}
trap close_window EXIT
L="$SITE/outputs/build.lock"
d=$((SECONDS + 3600))
until o=$(python3 "$SITE/scripts/ship_lock.py" "$L" $$ 2>&1); do
  if [ $SECONDS -ge $d ]; then
    echo "$(date "+%F %T") BUSY: outputs/build.lock held 60 min ($o); Logos build skipped"
    echo "75 $(date -Iseconds)" > "$STATUS"
    exit 75
  fi
  sleep 30
done
echo "$(date "+%F %T") holding outputs/build.lock ($o)"
cd "$ROOT" || exit 1
# Hard backstop over logos_build.py's own 2 h limit (MAX_RUN_S): the lock is
# never held past 2 h 30 min even if the driver hangs inside one book.
# 124 = killed by this limit (2026-10-15: a stuck run held the lock 4.5 h).
/opt/homebrew/bin/timeout --kill-after=60 9000 /usr/bin/python3 "$ROOT/scripts/logos_build.py" "$@"
rc=$?
[ "$rc" -eq 124 ] && echo "$(date "+%F %T") LIMIT: logos_build.py killed at the wrapper's 2 h 30 min limit"
echo "$(date "+%F %T") logos build exit $rc"
echo "$rc $(date -Iseconds)" > "$STATUS"
exit $rc
