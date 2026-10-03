#!/bin/bash
# Re-certification lanes for Via Patrum (owner 2026-10-02: re-check every work
# against the source; keep the site up; real progress overnight).
# launchd: com.saneapps.fathers-recert, every 30 min. Idempotent: refreshes
# smoked model receipts when older than 3 h (gate TTL is 4 h), then starts any
# lane that is not running. Each lane is one `work_pipeline.py queue` process.
set -u
# launchd PATH has no Node: npx (wrangler deploy of the status site) lives here.
export PATH="/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:$PATH"
ROOT="$HOME/SaneApps/clients/translations"
GATE="$HOME/SaneApps/infra/SaneProcess/scripts/llm_api_research_gate.rb"
RECEIPTS="$HOME/SaneApps/infra/SaneProcess/outputs/llm-api-research"
OUT="$ROOT/outputs/work-pipeline"
LOCK="/tmp/fathers-recert.lock"
mkdir -p "$OUT"
mkdir "$LOCK" 2>/dev/null || { echo "$(date +%T) another tick is running"; exit 0; }
trap 'rmdir "$LOCK"' EXIT
cd "$ROOT" || exit 1
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
[ -n "${CLOUDFLARE_API_TOKEN:-}" ] || { echo "$(date +%T) no Cloudflare token"; exit 2; }
KW='{"chat_template_kwargs":{"enable_thinking":false}}'

fresh() {  # receipt for model $1 younger than 3 h?
  local slug f
  slug=$(echo "$1" | tr '/@' '__')
  f=$(ls -t "$RECEIPTS"/*-cf-"$slug".json 2>/dev/null | head -1)
  [ -n "$f" ] && [ $(( $(date +%s) - $(stat -f %m "$f") )) -lt 10800 ]
}
refresh() {  # model purpose
  fresh "$1" && return 0
  timeout 400 ruby "$GATE" --provider cf --model "$1" --purpose "$2" \
    --notes "work_pipeline via llm_bakeoff.vendor_call, thinking off" --kwargs "$KW" --smoke >/dev/null 2>&1 \
    && echo "$(date +%T) receipt refreshed $1" || echo "$(date +%T) receipt FAILED $1"
}
refresh @cf/deepseek-ai/deepseek-v4-pro-0813 translate
for m in @cf/moonshotai/kimi-k2.6 @cf/zai-org/glm-5.2 @cf/qwen/qwen3.8-27b; do refresh "$m" translation-qa; done
# NVIDIA referee (third family): same 3 h freshness rule, NIM provider.
NVR=$(ls -t "$RECEIPTS"/*-nvidia-nvidia_nemotron-3-ultra-550b-a55b.json 2>/dev/null | head -1)
if [ -z "$NVR" ] || [ $(( $(date +%s) - $(stat -f %m "$NVR") )) -ge 10800 ]; then
  timeout 400 ruby "$GATE" --provider nvidia --model nvidia/nemotron-3-ultra-550b-a55b --purpose translation-qa \
    --notes "work_pipeline referee via llm_bakeoff.vendor_call" --kwargs '{"reasoning_effort":"none"}' --smoke >/dev/null 2>&1 \
    && echo "$(date +%T) receipt refreshed nemotron-3-ultra" || echo "$(date +%T) receipt FAILED nemotron-3-ultra"
fi

lane() {  # name args...
  local name="$1"; shift
  local pidf="$OUT/lane-$name.pid"
  if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then return 0; fi
  nohup nice -n 10 python3 scripts/work_pipeline.py queue "$@" >> "$OUT/lane$name.out" 2>&1 &
  echo $! > "$pidf"
  echo "$(date +%T) lane $name started pid $!"
}
# Cost is not a constraint (owner 2026-10-02, CF grant): run many lanes. Work is
# network-bound (Workers AI calls), so lanes cost little CPU. Lanes skip a book
# another lane holds (queue.json) and certified books.
for n in 1 2 3; do lane A$n --limit 500 --max-words 2000; done
for n in 1 2 3 4; do lane B$n --limit 500 --min-words 2000 --max-words 20000; done
for n in 1 2; do lane D$n --limit 500 --min-words 20000; done
for n in 1 2 3; do lane C$n --unpublished --limit 500 --max-words 20000; done

# Owner status site (private Pages project viapatrum-status behind Cloudflare
# Access, owner email only): rebuild from the audit log and deploy each tick.
if nice -n 10 timeout 600 python3 scripts/status_site.py >> "$OUT/status-site.log" 2>&1; then
  timeout 300 npx --yes wrangler@4 pages deploy outputs/status-site --project-name viapatrum-status \
    --branch main --commit-dirty=true >> "$OUT/status-site.log" 2>&1 \
    && echo "$(date +%T) status site deployed" || echo "$(date +%T) status site deploy FAILED"
fi
