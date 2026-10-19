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
# One tick at a time. The lock directory holds "<pid> <start epoch>", so a
# lock left by a killed run is taken over, and a live one is reported (BUSY,
# exit 75) instead of passing as a quiet, healthy run. Network-bound: this job
# does not take the site's outputs/build.lock, so it keeps running during builds.
if ! mkdir "$LOCK" 2>/dev/null; then
  read -r opid ostart 2>/dev/null < "$LOCK/pid"
  if [ -n "${opid:-}" ] && kill -0 "$opid" 2>/dev/null; then
    echo "$(date +%T) BUSY: tick pid $opid has run $(( ($(date +%s) - ${ostart:-$(date +%s)}) / 60 )) min; exit 75"
    exit 75
  fi
  echo "$(date +%T) lock left by pid ${opid:-?}, which is not running; taking it"
  rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null
  mkdir "$LOCK" 2>/dev/null || { echo "$(date +%T) BUSY: another tick took the lock first; exit 75"; exit 75; }
fi
echo "$$ $(date +%s)" > "$LOCK/pid"
trap 'rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null' EXIT
cd "$ROOT" || exit 1
# Pause switch (owner 2026-10-05, quality audit): while outputs/work-pipeline/
# lanes.paused exists, no lane is started. Running lanes still finish their
# current work and exit on lanes.restart (never kill a lane).
set -a; source "$HOME/.config/nv/env" >/dev/null 2>&1; set +a
[ -n "${CLOUDFLARE_API_TOKEN:-}" ] || { echo "$(date +%T) no Cloudflare token"; exit 2; }
# Daily spending cap (owner 2026-10-14: "no chance of credits burning"). Over
# the cap it writes a "budget:" lanes.paused and touches lanes.restart; the next
# UTC day it lifts its own pause. An owner pause is never lifted here.
timeout 120 python3 scripts/spend_guard.py gate-lanes | sed "s/^/$(date +%T) /"
if [ -f "$OUT/lanes.paused" ]; then echo "$(date +%T) lanes paused ($(head -1 "$OUT/lanes.paused"))"; exit 0; fi
if [ "$(python3 -c 'import json;print(json.load(open("outputs/spend/today.json")).get("state"))' 2>/dev/null)" != ok ]; then
  echo "$(date +%T) spend unread; no lanes start this tick"; exit 0
fi
# fresh()/refresh() and KW live in receipt_refresh.sh (shared with the beliefs job).
source "$ROOT/scripts/receipt_refresh.sh" || { echo "$(date +%T) receipt_refresh.sh missing"; exit 1; }
# The scout writes promoted_drafter.json when a new model wins the bakeoff.
# A lane that is already running keeps the id it imported. This refresh is
# for the next start only.
DEFAULT_DRAFTER="@cf/deepseek-ai/deepseek-v4-pro-0813"
DRAFTER="$(python3 -c 'import sys; sys.path.insert(0, "'"$HOME"'/SaneApps/infra/SaneProcess/scripts/automation"); from cf_capability_scout import resolve_drafter; print(resolve_drafter())')" || DRAFTER=""
if [ -z "${DRAFTER:-}" ]; then
  DRAFTER="$DEFAULT_DRAFTER"
  echo "$(date +%T) drafter pointer unread; using $DRAFTER"
fi
# Lane profile (owner 2026-10-19: translation off Workers AI credit). "plans" (the default
# when $OUT/lane-profile is missing): Muse drafts and repairs, Claude Sonnet + Haiku check
# and read, no paid fallback. scripts/plan_calls.py waits out a spent usage window on
# either plan and paces Claude (hourly budget, 3 calls at once). Bench and reader
# calibration: outputs/checker-bench-20261019, outputs/plan-limits. Write "workers-ai"
# to $OUT/lane-profile to go back to the Workers AI drafter and checkers below.
PROFILE="$(head -1 "$OUT/lane-profile" 2>/dev/null | tr -d '[:space:]')"
PROFILE="${PROFILE:-plans}"
echo "$(date +%T) lane profile: $PROFILE ($(python3 scripts/plan_calls.py status 2>/dev/null))"
if [ "$PROFILE" = plans ]; then
  export WP_DRAFTER=muse WP_JUDGES=claude-sonnet-5-5,claude-haiku-5-5 WP_FALLBACK=""
  DRAFTER=muse
else
  refresh "$DRAFTER" translate
  for m in @cf/moonshotai/kimi-k2.6 @cf/zai-org/glm-5.2 @cf/qwen/qwen3.8-27b; do refresh "$m" translation-qa; done
  refresh @cf/openai/gpt-oss-120b translation-qa '{}'
fi
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
# Plans checkers: Sonnet (precise) + Grok build-fast on the X plan login (best recall in the
# 2026-10-19 bench, 62 s a section). A finding counts only when both agree or the other
# upholds it, so Grok's nitpicks are filtered and Sonnet's misses are covered. Haiku stays a
# reader (WP_JUDGES above): its scores are the calibrated pair.
[ "$PROFILE" = plans ] && PAIRS=("claude-sonnet-5-5,grok-4.7-build-fast")
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
# Cost was not a constraint (owner 2026-10-02, CF grant); since 2026-10-14 the
# daily cap in spend_guard.py bounds it (above). Work is
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
