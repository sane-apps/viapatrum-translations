#!/usr/bin/env bash
# Install the Mini LaunchAgent for the always-on Fathers lanes (CF + NVIDIA).
# Run ON the Mac Mini only.
# Does not kill a burn that was started outside launchd.

set -euo pipefail

host="$(hostname -s 2>/dev/null || hostname)"
case "$host" in
  *ini*|*Mini*|Stephans-Mac-mini) ;;
  *)
    echo "Refusing install on non-Mini host: $host (ssh mini and re-run)" >&2
    exit 2
    ;;
esac

LABEL="com.saneapps.fathers-overnight-quota"
ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
SCRIPT="$ROOT/scripts/run-overnight-quota.sh"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/SaneApps"
OUT="$HOME/SaneApps/outputs/fathers-overnight"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$OUT"
chmod +x "$SCRIPT"

python3 - "$PLIST" "$SCRIPT" "$LOG_DIR" "$LABEL" <<'PY'
import plistlib, pathlib, sys
plist, script, log_dir, label = sys.argv[1:5]
data = {
    "Label": label,
    "ProgramArguments": ["/bin/bash", script],
    "RunAtLoad": True,
    # Restart only after a crash. A clean stop stays down.
    # KeepAlive true (always) used to bootout mid-promote and stack a second run.
    "KeepAlive": {"SuccessfulExit": False},
    "Nice": 10,
    "ThrottleInterval": 300,
    "ProcessType": "Background",
    "WorkingDirectory": str(pathlib.Path(script).resolve().parents[1]),
    "EnvironmentVariables": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "HOME": str(pathlib.Path.home()),
        "SANE_TRANSLATIONS_ROOT": str(pathlib.Path(script).resolve().parents[1]),
        "SANE_FATHERS_FOREVER": "1",
    },
    "StandardOutPath": f"{log_dir}/fathers-overnight.out.log",
    "StandardErrorPath": f"{log_dir}/fathers-overnight.err.log",
}
path = pathlib.Path(plist)
with path.open("wb") as fh:
    plistlib.dump(data, fh)
print(path)
PY

uid="$(id -u)"
# Reloads the launchd job only. A nohup burn is a different process and keeps its flock.
launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$uid" "$PLIST"
launchctl enable "gui/$uid/$LABEL" 2>/dev/null || true
echo "installed $LABEL"
echo "  plist: $PLIST"
echo "  mode: always-on supervisor (SANE_FATHERS_FOREVER=1)"
echo "  restart: only after a crash (KeepAlive SuccessfulExit false)"
echo "  locks: ~/SaneApps/outputs/fathers-overnight/locks/"
echo "  One batch, then exit: $SCRIPT"
