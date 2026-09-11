#!/bin/bash
# Close Ante panels, rebuild Ante-Nicene PBB, verify TN headword articles.
set +e
OUT=/tmp/ante-logos
mkdir -p "$OUT"
LOG="$OUT/close-build-log.txt"
exec >"$LOG" 2>&1
PID=$(pgrep -f '/Applications/Logos.app/Contents/MacOS/Logos' | head -1)
echo "START $(date) PID=$PID"

osascript -e 'tell application "Logos" to activate'
sleep 0.5

# Close floating panels + Cmd+W resource tabs
for _ in 1 2 3 4 5 6 7 8 9 10; do
  osascript <<'OSA'
tell application "System Events"
  tell process "Logos"
    set frontmost to true
    repeat with w in windows
      try
        set wname to name of w as text
        if wname is not "Logos Pro" then
          try
            click button 1 of w
          end try
        end if
      end try
    end repeat
  end tell
end tell
OSA
  osascript -e 'tell application "System Events" to tell process "Logos" to keystroke "w" using command down'
  sleep 0.3
done

osascript <<'OSA'
tell application "System Events"
  tell process "Logos"
    set frontmost to true
    try
      click menu item "Personal Books" of menu 1 of menu bar item "Tools" of menu bar 1
    end try
  end tell
end tell
OSA
sleep 1.0
screencapture -x "$OUT/pb-open.png"

# OCR
python3 - <<'PY'
from pathlib import Path
import Vision
# Use swift helper file instead if Vision py unavailable
print("use_swift")
PY

swift -e '
import Vision
import AppKit
import Foundation
let url = URL(fileURLWithPath: "/tmp/ante-logos/pb-open.png")
guard let img = NSImage(contentsOf: url) else { fatalError("img") }
let w = img.size.width, h = img.size.height
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
try! VNImageRequestHandler(url: url, options: [:]).perform([req])
var lines: [String] = []
for o in req.results ?? [] {
  let t = o.topCandidates(1).first!.string
  let b = o.boundingBox
  let x = Int((b.origin.x + b.size.width/2) * w)
  let y = Int((1 - b.origin.y - b.size.height/2) * h)
  let keys = ["Ante-Nicene", "Soteriology", "Build", "Finished", "docx", "succeeded", "failed", "errors", "close"]
  if keys.contains(where: { t.localizedCaseInsensitiveContains($0) }) {
    lines.append("\(t)|\(x),\(y)")
  }
}
try! lines.joined(separator: "\n").write(toFile: "/tmp/ante-logos/pb-ocr.txt", atomically: true, encoding: .utf8)
'
cat "$OUT/pb-ocr.txt"

FIN=$(grep -i '^Finished|' "$OUT/pb-ocr.txt" | head -1 | awk -F'|' '{print $2}')
[ -n "$FIN" ] && /opt/homebrew/bin/cliclick "c:$FIN" && sleep 0.4

ANTE=$(awk -F'|' 'BEGIN{IGNORECASE=1} $1~/Ante-Nicene|Soteriology/ && $2~/^[0-9]+,[0-9]+$/ {split($2,a,","); if(a[1]>700){print $2; exit}}' "$OUT/pb-ocr.txt")
echo "ANTE=$ANTE"
[ -n "$ANTE" ] && /opt/homebrew/bin/cliclick "c:$ANTE"
sleep 0.8

# Peekaboo Build button
peekaboo see --pid "$PID" --json > "$OUT/pb-see.json" 2>"$OUT/pb-see.err" || true
python3 - <<'PY'
import json
from pathlib import Path
p = Path("/tmp/ante-logos/pb-see.json")
if not p.exists() or p.stat().st_size < 20:
    raise SystemExit(0)
d = json.loads(p.read_text())
for e in d.get("data", {}).get("ui_elements", []):
    lab = e.get("label") or ""
    b = e.get("bounds") or {}
    if not b:
        continue
    xy = f"{int(b['x']+b['width']/2)},{int(b['y']+b['height']/2)}"
    if lab.startswith("Build") or lab == "Build book":
        Path("/tmp/ante-logos/buildxy.txt").write_text(xy)
        print("build", lab, xy)
    if lab.strip() == "Finished":
        Path("/tmp/ante-logos/finxy.txt").write_text(xy)
PY
[ -f /tmp/ante-logos/finxy.txt ] && /opt/homebrew/bin/cliclick "c:$(cat /tmp/ante-logos/finxy.txt)" && sleep 0.3

# Ensure panels closed once more before build
for _ in 1 2 3 4; do
  osascript -e 'tell application "System Events" to tell process "Logos" to keystroke "w" using command down'
  sleep 0.25
done
osascript <<'OSA'
tell application "System Events"
  tell process "Logos"
    set frontmost to true
    try
      click menu item "Personal Books" of menu 1 of menu bar item "Tools" of menu bar 1
    end try
  end tell
end tell
OSA
sleep 0.8
[ -n "$ANTE" ] && /opt/homebrew/bin/cliclick "c:$ANTE"
sleep 0.5

XY=$(cat /tmp/ante-logos/buildxy.txt 2>/dev/null || echo "1397,825")
echo "BUILD $XY"
/opt/homebrew/bin/cliclick "c:$XY"

ok=0
for i in $(seq 1 40); do
  sleep 2
  screencapture -x "$OUT/wait.png"
  swift -e '
import Vision
import AppKit
import Foundation
let url = URL(fileURLWithPath: "/tmp/ante-logos/wait.png")
let img = NSImage(contentsOf: url)!
let w = img.size.width, h = img.size.height
let req = VNRecognizeTextRequest()
req.recognitionLevel = .fast
try! VNImageRequestHandler(url: url, options: [:]).perform([req])
var lines: [String] = []
for o in req.results ?? [] {
  let t = o.topCandidates(1).first!.string
  let keys = ["Build succeeded", "Build failed", "Could not remove", "0 errors", "Compiling", "Converting", "close all", "warnings"]
  if keys.contains(where: { t.localizedCaseInsensitiveContains($0) }) { lines.append(t) }
}
try! lines.joined(separator: "\n").write(toFile: "/tmp/ante-logos/wait-ocr.txt", atomically: true, encoding: .utf8)
'
  echo "wait $i $(tr '\n' ' ' < "$OUT/wait-ocr.txt" 2>/dev/null | head -c 200)"
  if grep -qi 'Build succeeded' "$OUT/wait-ocr.txt" 2>/dev/null; then
    echo SUCCESS
    cat "$OUT/wait-ocr.txt"
    ok=1
    break
  fi
  if grep -qiE 'Build failed|Could not remove|close all' "$OUT/wait-ocr.txt" 2>/dev/null; then
    echo FAIL
    cat "$OUT/wait-ocr.txt"
    break
  fi
done

screencapture -x "$OUT/final.png"
python3 - <<'PY'
import sqlite3
from pathlib import Path
db = Path.home() / "Library/Application Support/Logos4/Documents/adcocvnb.nzw/PersonalBooks/PersonalBookManager.db"
con = sqlite3.connect(db)
print("LastCompiled", con.execute("SELECT LastCompiled FROM Books WHERE Id=4").fetchone())
rows = con.execute(
    "SELECT ArticleId, Context FROM ArticleCache WHERE BookId=4 AND Context LIKE 'TN %' ORDER BY Context"
).fetchall()
print("TN_count", len(rows))
for r in rows:
    print(r)
print("total", con.execute("SELECT COUNT(*) FROM ArticleCache WHERE BookId=4").fetchone()[0])
con.close()
logdir = Path.home() / "Library/Application Support/Logos4/Logging/PBB Logs"
logs = sorted(logdir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
print("log", logs[0])
print(logs[0].read_text(errors="ignore")[-1000:])
PY
echo "DONE ok=$ok $(date)" | tee "$OUT/close-build-done"
