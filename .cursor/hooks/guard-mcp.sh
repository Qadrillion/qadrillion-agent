#!/usr/bin/env bash
# beforeMCPExecution: targeted high-impact names, or opt-in strict gates.
# Names do not prove effects or consent; native permissions still apply.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

"$PY" -c '
import json
import re
import sys


def result(permission, reason):
    response = {"permission": permission}
    if permission != "allow":
        response["user_message"] = reason
        response["agent_message"] = (
            "Blocked by the workspace MCP guard. Do not retry or route around it. " + reason
            if permission == "deny" else
            "This tool may change external state. Show the intended effect and a redacted payload, then obtain the required decision. " + reason
        )
    print(json.dumps(response))
    sys.exit(0)


def name(event, aliases):
    values = [event[key] for key in aliases if key in event]
    if not values or any(not isinstance(value, str) or not value.strip() or
                         any(char.isspace() or ord(char) < 32 for char in value) for value in values):
        raise ValueError()
    if len(set(values)) != 1:
        raise ValueError()
    return values[0]


try:
    event = json.load(sys.stdin)
    if not isinstance(event, dict) or not isinstance(event.get("tool_input"), dict):
        raise ValueError()
    server = name(event, ("server_name", "server", "mcp_server"))
    tool = name(event, ("tool_name", "tool"))
except (ValueError, TypeError):
    result("deny", "Invalid MCP event: server, tool name, and object tool_input are required.")

profile, deny_servers, deny_tools, ask_tools, read_tools = sys.argv[1:]
if profile not in ("targeted", "strict"):
    result("deny", "Invalid guard profile.")
subject = server + " " + tool
# Normalize camelCase so getCollection and get_collection share token rules.
normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", tool).lower()


def matches(pattern, value):
    return bool(pattern and re.search(pattern, value, re.IGNORECASE))


def verb(pattern):
    return matches(r"(^|[^a-z0-9])(" + pattern + r")", normalized) if pattern else False


try:
    # Validate the full policy before an early matching rule can hide an error.
    for pattern in (deny_servers, deny_tools, ask_tools, read_tools):
        re.compile(pattern)
    if matches(deny_servers, server):
        result("deny", "Server is not permitted: " + subject)
    if verb(deny_tools):
        result("deny", "Destructive tool: " + subject)
    if verb(ask_tools):
        result("ask", "Confirm tool effect: " + subject)
    if profile == "targeted":
        result("allow", "")
    if verb("delete|remove|destroy|purge|drop"):
        result("deny", "Destructive tool under strict profile: " + subject)
    if verb("create|update|add_comment|comment|transition_issue|assign|post|send|publish|patch|put|schedule|trigger|deploy|merge|resolve|upload|write|edit|add_label|set_|exec|execute|evaluate|run|request|http|api|invoke|call|sql|graphql"):
        result("ask", "Confirm tool effect under strict profile: " + subject)
    if matches(read_tools, normalized):
        result("allow", "")
except re.error:
    result("deny", "Invalid MCP guard configuration.")
result("ask", "Unknown tool effect: " + subject)
' "${GUARD_PROFILE:-targeted}" "${MCP_DENY_SERVERS:-}" "${MCP_DENY_TOOLS:-}" "${MCP_ASK_TOOLS:-}" "${MCP_READ_TOOLS:-}"
