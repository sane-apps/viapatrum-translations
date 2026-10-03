#!/usr/bin/env bash
# Install Mini LaunchAgent: catch-up burn when the 21:10 overnight was missed
# (machine off/asleep). Fires at load + daily 09:10; the script itself burns
# ONLY if no dual-lane receipt in ~20h, else exits 0. Run ON the Mac Mini only.
set -euo pipefail
host="$(hostname -s 2>/dev/null || hostname)"
case "$host" in
  *ini*|*Mini*|Stephans-Mac-mini) ;;
  *) echo "Refusing install on non-Mini host: $host (ssh mini and re-run)" >&2; exit 2;;
esac
LABEL="com.saneapps.fathers-overnight-catchup"
ROOT="${SANE_TRANSLATIONS_ROOT:-$HOME/SaneApps/clients/translations}"
SCRIPT="$ROOT/scripts/overnight_catchup.sh"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/SaneApps"
mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"
chmod +x "$SCRIPT"
python3 - "$PLIST" "$SCRIPT" "$LOG_DIR" "$LABEL" <<'PY'
import plistlib, pathlib, sys
plist, script, log_dir, label = sys.argv[1:5]
data = {
    "Label": label,
    "ProgramArguments": ["/bin/bash", script],
    "RunAtLoad": True,
    "StartCalendarInterval": {"Hour": 9, "Minute": 10},
    "ThrottleInterval": 300,
    "Nice": 10,
    "ProcessType": "Background",
    "WorkingDirectory": str(pathlib.Path(script).resolve().parents[1]),
    "EnvironmentVariables": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "HOME": str(pathlib.Path.home()),
        "SANE_TRANSLATIONS_ROOT": str(pathlib.Path(script).resolve().parents[1]),
    },
    "StandardOutPath": f"{log_dir}/fathers-catchup.out.log",
    "StandardErrorPath": f"{log_dir}/fathers-catchup.err.log",
}
with pathlib.Path(plist).open("wb") as fh:
    plistlib.dump(data, fh)
print(plist)
PY
uid="$(id -u)"
launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$uid" "$PLIST"
launchctl enable "gui/$uid/$LABEL" 2>/dev/null || true
echo "installed $LABEL (RunAtLoad + daily 09:10; burns only if receipts stale ~20h)"
