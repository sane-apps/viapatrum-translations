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
# Pause switch (owner 2026-10-05, quality audit): while outputs/work-pipeline/
# lanes.paused exists, no lane is started. Running lanes still finish their
# current work and exit on lanes.restart (never kill a lane).
if [ -f "$OUT/lanes.paused" ]; then echo "$(date +%T) lanes paused ($(head -1 "$OUT/lanes.paused"))"; exit 0; fi
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
[ -n "${CLOUDFLARE_API_TOKEN:-}" ] || { echo "$(date +%T) no Cloudflare token"; exit 2; }
# fresh()/refresh() and KW live in receipt_refresh.sh (shared with the beliefs job).
source "$ROOT/scripts/receipt_refresh.sh" || { echo "$(date +%T) receipt_refresh.sh missing"; exit 1; }
refresh @cf/deepseek-ai/deepseek-v4-pro-0813 translate
for m in @cf/moonshotai/kimi-k2.6 @cf/zai-org/glm-5.2 @cf/qwen/qwen3.8-27b; do refresh "$m" translation-qa; done
refresh @cf/openai/gpt-oss-120b translation-qa '{}'
# Checker pairs rotate across lanes (2026-10-03). Workers AI caps paid-access
# models (GLM-5.x, Kimi, DeepSeek) at about 20 requests/min per model, and
# open models such as GPT-OSS-120B at 300/min. GLM-5.2 shared by all lanes
# drew 516 failed-after-retries 429s. So GPT-OSS (bench: GLM-level recall,
# fewer false alarms) is in every pair and the paid checkers each take a
# third. llm_bakeoff.rate_acquire paces every call under the caps, so lanes
# wait for a slot instead of getting throttled.
# GLM-5.3 out (spend audit 2026-10-03): never benched as a checker, the defect
# bench rejected it, 27% of its billed calls returned nothing (~\$70/day), and a
# failed call fell back to an unbenched model or counted a finding as confirmed.
# GPT-OSS out (quality audit 2026-10-05, docs/QUALITY_AUDIT_20261005.md): it
# raised the false finding or voted down the true one in 13 of 24 traced errors.
# Kimi + GLM are the benched pair; rate_acquire paces lanes under their caps,
# so fewer lanes run at full speed.
PAIRS=("@cf/moonshotai/kimi-k2.6,@cf/zai-org/glm-5.2")
NLANE=0
# NVIDIA referee (third family): same 3 h rule, NIM provider. Purpose-aware
# since the beliefs job also smokes a doctrine-grade Nemotron receipt nightly.
NOTES="work_pipeline referee via llm_bakeoff.vendor_call" refresh nvidia/nemotron-3-ultra-550b-a55b \
  translation-qa '{"reasoning_effort":"none"}' nvidia nemotron-3-ultra

# Re-gate held sections offline each tick (no LLM): gate fixes release false
# holds once no lane is on the book (2026-10-03 stall fixes).
timeout 300 python3 scripts/regate_held.py >> "$OUT/regate.log" 2>&1 || true

lane() {  # name args...
  local name="$1"; shift
  local pidf="$OUT/lane-$name.pid"
  if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then return 0; fi
  local ck="${PAIRS[$((NLANE % ${#PAIRS[@]}))]}"; NLANE=$((NLANE + 1))
  WP_CHECKERS="$ck" WORK_PIPELINE_WORKERS=8 nohup nice -n 10 python3 scripts/work_pipeline.py queue "$@" >> "$OUT/lane$name.out" 2>&1 &
  echo $! > "$pidf"
  echo "$(date +%T) lane $name started pid $! checkers $ck"
}
# Cost is not a constraint (owner 2026-10-02, CF grant): run many lanes. Work is
# network-bound (Workers AI calls), so lanes cost little CPU. Lanes skip a book
# another lane holds (queue.json) and certified books.
# Phase one (owner 2026-10-03): untranslated early works first, then the
# translated ones. Untranslated get 8 lanes (E covers works over 20k words,
# which had no lane before); re-checks of live works get 7. Every lane takes
# the earliest writer first (work_pipeline.queue).
# Owner 2026-10-03 evening: spend cut from 15 lanes to 6 (~$600/day of credits
# bought 45 small certifications). One lane per size/state group, two for small
# unpublished works; reopened books go first (work_pipeline.queue).
for n in 1 2; do lane C$n --unpublished --limit 500 --max-words 20000; done
for n in 1; do lane E$n --unpublished --limit 500 --min-words 20000; done
for n in 1; do lane A$n --limit 500 --max-words 2000; done
for n in 1; do lane B$n --limit 500 --min-words 2000 --max-words 20000; done
for n in 1; do lane D$n --limit 500 --min-words 20000; done

# Owner status site (private Pages project viapatrum-status behind Cloudflare
# Access, owner email only): rebuild from the audit log each tick, deploy only
# when the content changed (2026-10-06: every tick re-uploaded ~430 files).
# The build time sits in index.html inside <span data-built>, left out of the hash.
if nice -n 10 timeout 600 python3 scripts/status_site.py >> "$OUT/status-site.log" 2>&1; then
  SITE_SHA=$(cd outputs/status-site && find . -type f | LC_ALL=C sort | while read -r f; do
    echo "$f"; sed 's/<span data-built>[^<]*<\/span>//' "$f"; done | shasum -a 256 | cut -d' ' -f1)
  if [ -n "$SITE_SHA" ] && [ "$SITE_SHA" = "$(cat "$OUT/status-site.deployed.sha256" 2>/dev/null)" ]; then
    echo "$(date +%T) status site unchanged, skip deploy"
  elif timeout 300 npx --yes wrangler@4 pages deploy outputs/status-site --project-name viapatrum-status \
    --branch main --commit-dirty=true >> "$OUT/status-site.log" 2>&1; then
    echo "$SITE_SHA" > "$OUT/status-site.deployed.sha256"
    echo "$(date +%T) status site deployed"
  else
    echo "$(date +%T) status site deploy FAILED"
  fi
fi
