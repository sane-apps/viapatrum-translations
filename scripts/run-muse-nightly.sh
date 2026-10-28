#!/bin/bash
# Muse-only translation lane, nightly (owner 2026-10-18). launchd:
# com.saneapps.fathers-muse-nightly, daily 05:10 (after held-review 04:30,
# clear of the 03:00 e2e build lock window; this job is network-bound and
# takes no build lock). Drafts + blind-gloss-critic reviews the head of
# outputs/muse-lane/queue.json through the Muse queue runner; never
# writes book files, never ships. Exit 3 = muse runner unavailable.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
ROOT="$HOME/SaneApps/clients/translations"
LOCK="/tmp/fathers-muse-nightly.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  read -r opid ostart 2>/dev/null < "$LOCK/pid"
  if [ -n "${opid:-}" ] && kill -0 "$opid" 2>/dev/null; then
    echo "$(date '+%F %T') BUSY: muse nightly pid $opid; exit 75"
    exit 75
  fi
  rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null
  mkdir "$LOCK" 2>/dev/null || { echo "$(date '+%F %T') BUSY: lock race; exit 75"; exit 75; }
fi
echo "$$ $(date +%s)" > "$LOCK/pid"
trap 'rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null' EXIT
cd "$ROOT" || exit 1
echo "$(date '+%F %T') muse nightly start"
timeout 7200 nice -n 10 python3 scripts/muse_nightly.py --max-sections 4
rc=$?
echo "$(date '+%F %T') muse nightly exit $rc"
exit $rc
