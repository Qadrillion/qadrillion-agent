#!/usr/bin/env bash
# beforeMCPExecution hook — makes the "confirm before posting" rule deterministic.
# Reads the hook event JSON on stdin, prints {"permission": allow|ask|deny}.
#
# Verdicts, in order: denied server -> denied tool verb -> ask on write verbs
# -> allow. Reads are never gated. The verb lists live in guard.conf.
# Server patterns match the SERVER name only; verb patterns match the TOOL name
# only — a server called "postman" must not trip the "post" write verb.
#
# VERIFY THE PAYLOAD SHAPE ONCE: the field names below (tool_name, server_name,
# tool_input) are what the harness sends today; confirm in the Hooks output
# channel the first time this fires, then keep the golden test payloads in
# tests/run-tests.sh in sync.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=guard.conf
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

input="$(cat)"
read -r server tool < <(printf '%s' "$input" | "$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
    server = d.get("server_name") or d.get("server") or d.get("mcp_server") or ""
    tool = d.get("tool_name") or d.get("tool") or ""
    print((server or "-").replace(" ", "_"), (tool or "-").replace(" ", "_"))
except Exception:
    print("-", "-")
')
subject="$server $tool"

deny() {
  printf '{"permission":"deny","user_message":"Blocked MCP call: %s","agent_message":"Blocked by the workspace safety hook (.cursor/hooks/guard-mcp.sh): %s. Do not retry or use another server for the same effect. Tell the user what you wanted to do."}\n' "$1" "$1"
  exit 0
}
ask() {
  printf '{"permission":"ask","user_message":"Confirm MCP write: %s","agent_message":"This MCP call writes to an external system and needs the user'"'"'s explicit approval: %s. Show the exact payload, then wait."}\n' "$1" "$1"
  exit 0
}
srv()  { printf '%s' "$server" | grep -qiE -e "$1"; }
verb() { printf '%s' "$tool"   | grep -qiE -e "(^|[^a-z])(${1})"; }

[ -n "${MCP_DENY_SERVERS:-}" ] && srv  "$MCP_DENY_SERVERS" && deny "server is not permitted in this workspace ($subject)"
[ -n "${MCP_DENY_TOOLS:-}" ]   && verb "$MCP_DENY_TOOLS"   && deny "destructive tool ($subject)"
[ -n "${MCP_ASK_TOOLS:-}" ]    && verb "$MCP_ASK_TOOLS"    && ask  "$subject"

printf '{"permission":"allow"}\n'
