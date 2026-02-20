#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/quality-guardrail-report.sh [LOG_FILE...]

Summarize fallback reasons from JSON logs. If no files are provided, reads stdin.
Requires: jq
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required." >&2
  exit 1
fi

read_input() {
  if [[ "$#" -gt 0 ]]; then
    cat "$@"
  else
    cat
  fi
}

read_input "$@" | jq -R '
  def parse:
    (try fromjson) //
    (try (capture("(?<json>\\{.*\\})").json | fromjson)) //
    empty;
  def reason:
    (.fallback_reason
     // .fallback?.reason
     // .error?.type
     // .error_type
     // .provider_error
     // .provider_error_type
     // .exception
     // "unknown") | tostring;
  def route:
    (.route // .path // .request?.path // .endpoint // "unknown") | tostring;
  def provider:
    (.provider // "unknown") | tostring;
  def ts:
    (.ts // .timestamp // .time // ."@timestamp" // "unknown") | tostring;
  def req:
    (.request_id // .trace_id // .span_id // .req_id // "unknown") | tostring;
  inputs
  | parse
  | select(.fallback_used == true)
  | {reason: reason, provider: provider, route: route, ts: ts, request_id: req}
' | jq -s '
  def count_by(f):
    map(f) | sort | group_by(.) | map({key:.[0], count:length}) | sort_by(-.count);
  if length == 0 then
    "No fallback_used=true events found."
  else
    "Total fallback events: \(length)\n" +
    "By reason:\n" +
    (count_by(.reason) | map("  - \(.count) \(.key)") | join("\n")) +
    "\n\nBy provider:\n" +
    (count_by(.provider) | map("  - \(.count) \(.key)") | join("\n")) +
    "\n\nBy route:\n" +
    (count_by(.route) | map("  - \(.count) \(.key)") | join("\n")) +
    "\n\nRecent examples (up to 5):\n" +
    (sort_by(.ts) | reverse | .[0:5]
     | map("  - [\(.ts)] \(.route) provider=\(.provider) reason=\(.reason) request_id=\(.request_id)")
     | join("\n"))
  end
'
