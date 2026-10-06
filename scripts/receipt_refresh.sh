# Smoked-receipt refresh shared by the Fathers runners (sourced, not run):
# run-recert-lanes.sh (lanes, every 30 min) and run-doctrine-map.sh (beliefs,
# 03:30). The vendor gate TTL is 4 h, so a receipt older than 3 h is re-smoked.
# Needs GATE (llm_api_research_gate.rb) and RECEIPTS (its output folder).
KW='{"chat_template_kwargs":{"enable_thinking":false}}'

fresh() {  # model purpose [provider]: receipt with that purpose younger than 3 h?
  local slug f
  slug=$(echo "$1" | tr '/@' '__')
  f=$(ls -t "$RECEIPTS"/*-"${3:-cf}"-"$slug".json 2>/dev/null | xargs grep -l "\"purpose\": *\"$2\"" 2>/dev/null | head -1)
  [ -n "$f" ] && [ $(( $(date +%s) - $(stat -f %m "$f") )) -lt 10800 ]
}
refresh() {  # model purpose [kwargs] [provider] [label]; returns 1 when the smoke fails
  fresh "$1" "$2" "${4:-cf}" && return 0
  if timeout 400 ruby "$GATE" --provider "${4:-cf}" --model "$1" --purpose "$2" \
    --notes "${NOTES:-work_pipeline via llm_bakeoff.vendor_call, thinking off}" --kwargs "${3:-$KW}" --smoke >/dev/null 2>&1; then
    echo "$(date +%T) receipt refreshed ${5:-$1}"
  else
    echo "$(date +%T) receipt FAILED ${5:-$1}"
    return 1
  fi
}
