#!/bin/bash
# launchd com.saneapps.cf-batch-broker (KeepAlive): the Workers AI batch broker.
set -u
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
cd "$HOME/SaneApps/clients/translations/scripts" || exit 1
exec /usr/bin/nice -n 5 /opt/homebrew/bin/python3 cf_batch_broker.py
