#!/usr/bin/env bash
# Install Mini LaunchAgent for Fathers dual-lane overnight (CF + NVIDIA).
# Run ON the Mac Mini only.

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

# Daily ~01:10 UTC ≈ after CF neuron reset (00:00 UTC). Local Mini TZ may be ET:
# 01:10 UTC = 21:10 ET previous calendar day — use UTC via StartCalendarInterval
# in *local* clock. Owner Mini is America/New_York → 21:10 local.
python3 - "$PLIST" "$SCRIPT" "$LOG_DIR" "$LABEL" <<'PY'
import plistlib, pathlib, sys
plist, script, log_dir, label = sys.argv[1:5]
data = {
    "Label": label,
    "ProgramArguments": ["/bin/bash", script],
    # After CF free-neuron reset (00:00 UTC): 21:10 America/New_York
    "StartCalendarInterval": {"Hour": 21, "Minute": 10},
    "RunAtLoad": False,
    "Nice": 10,
    # Retry when the burn exits nonzero (crash / API blip / promote fail mid-claim).
    # SuccessfulExit=false means exit 0 does NOT keep restarting.
    "KeepAlive": {"SuccessfulExit": False},
    "ThrottleInterval": 120,
    "ProcessType": "Background",
    "WorkingDirectory": str(pathlib.Path(script).resolve().parents[1]),
    "EnvironmentVariables": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "HOME": str(pathlib.Path.home()),
        "SANE_TRANSLATIONS_ROOT": str(pathlib.Path(script).resolve().parents[1]),
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
launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$uid" "$PLIST"
launchctl enable "gui/$uid/$LABEL" 2>/dev/null || true
echo "installed $LABEL"
echo "  plist: $PLIST"
echo "  schedule: daily 21:10 local (≈01:10 UTC)"
echo "  KeepAlive on failure; ThrottleInterval 120s"
echo "  kickstart now: launchctl kickstart -k gui/$uid/$LABEL"
