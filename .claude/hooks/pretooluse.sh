#!/usr/bin/env bash
# Claude Code PreToolUse adapter — one fence, two harnesses.
# Translates Claude Code's hook input into the Cursor guard scripts' input and
# maps their {"permission": ...} verdict onto Claude Code's
# hookSpecificOutput.permissionDecision. The guard scripts stay the single
# source of truth; this file never carries a rule of its own.
#
# Registered in .claude/settings.json for Bash, Read and mcp__* tools.
# Verify once by asking Claude Code for `git reset --hard` in a scratch repo
# and reading the deny in its transcript — a hook you have not seen execute
# is not a hook.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$(command -v python3 || echo /usr/bin/python3)"
input="$(cat)"

read -r tool < <(printf '%s' "$input" | "$PY" -c 'import json,sys; print(json.load(sys.stdin).get("tool_name",""))')

case "$tool" in
  Bash)
    payload="$(printf '%s' "$input" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({"command": d.get("tool_input",{}).get("command","")}))')"
    verdict="$(printf '%s' "$payload" | bash "$ROOT/.cursor/hooks/guard-shell.sh")" ;;
  Read|Edit|Write|MultiEdit|NotebookEdit)
    payload="$(printf '%s' "$input" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({"file_path": d.get("tool_input",{}).get("file_path","")}))')"
    verdict="$(printf '%s' "$payload" | bash "$ROOT/.cursor/hooks/guard-read.sh")" ;;
  mcp__*)
    # Claude Code names MCP tools mcp__<server>__<tool>
    payload="$(printf '%s' "$input" | "$PY" -c '
import json,sys
d=json.load(sys.stdin); parts=d.get("tool_name","").split("__",2)
print(json.dumps({"server_name": parts[1] if len(parts)>1 else "", "tool_name": parts[2] if len(parts)>2 else d.get("tool_name",""), "tool_input": d.get("tool_input",{})}))')"
    verdict="$(printf '%s' "$payload" | bash "$ROOT/.cursor/hooks/guard-mcp.sh")" ;;
  *)
    exit 0 ;;
esac

printf '%s' "$verdict" | "$PY" -c '
import json,sys
v=json.load(sys.stdin)
p=v.get("permission","allow")
if p=="allow":
    sys.exit(0)
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":p,"permissionDecisionReason":v.get("agent_message") or v.get("user_message") or "blocked by workspace hook"}}))
'
