#!/bin/bash
# launchd com.saneapps.cf-batch-broker (KeepAlive): the Workers AI batch broker.
set -u
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
cd "$HOME/SaneApps/clients/translations/scripts" || exit 1
# Daily cap + hourly ceiling (spend_guard.py, 2026-10-14). Over it or usage
# unknown: do not start; wait so KeepAlive does not spin. The broker also
# checks before every batch.
if ! timeout 120 /opt/homebrew/bin/python3 spend_guard.py allow; then
  sleep 300
  exit 0
fi
exec /usr/bin/nice -n 5 /opt/homebrew/bin/python3 cf_batch_broker.py
