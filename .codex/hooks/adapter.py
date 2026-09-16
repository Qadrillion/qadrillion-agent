#!/usr/bin/env python3
"""Translate Codex events to the existing Cursor policies; never execute tool input."""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path


class PolicyError(Exception):
    pass


def run_policy(script, payload, args=(), cwd=None, boundary=True):
    try:
        result = subprocess.run(
            ["bash", str(script), *args], input=json.dumps(payload), text=True,
            capture_output=True, timeout=8, cwd=cwd,
        )
        if result.returncode:
            raise PolicyError("policy process failed: " + script.name)
        verdict = json.loads(result.stdout)
        if not isinstance(verdict, dict):
            raise ValueError()
        if boundary and verdict.get("permission") not in ("allow", "ask", "deny"):
            raise ValueError()
        return verdict
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise PolicyError("policy unavailable or invalid: " + script.name) from exc


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}


def event_input(data):
    if not isinstance(data, dict) or not isinstance(data.get("tool_name"), str):
        raise PolicyError("invalid tool event")
    value = data.get("tool_input")
    if not isinstance(value, dict):
        raise PolicyError("invalid tool arguments")
    return data["tool_name"], value


def paths_in(value):
    """Collect every conventional path field, including nested arguments."""
    paths = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("source", "destination") and not isinstance(item, str):
                # These fields can also contain structured MCP objects.
                paths.extend(paths_in(item))
            elif key in ("path", "file_path", "filename", "source", "destination"):
                if not isinstance(item, str):
                    raise PolicyError("invalid path argument")
                if item:
                    paths.append(item)
            elif key == "paths":
                if not isinstance(item, list) or any(not isinstance(p, str) for p in item):
                    raise PolicyError("invalid paths argument")
                paths.extend(p for p in item if p)
            elif isinstance(item, (dict, list)):
                paths.extend(paths_in(item))
    elif isinstance(value, list):
        for item in value:
            paths.extend(paths_in(item))
    return paths


def tool_paths(tool, value, cwd):
    paths = paths_in(value)
    if tool in ("apply_patch", "Edit", "Write") and "command" in value:
        patch = value["command"]
        if not isinstance(patch, str) or not patch.startswith("*** Begin Patch"):
            raise PolicyError("invalid patch input")
        paths += re.findall(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", patch, re.M)
        if not paths:
            raise PolicyError("patch has no recognized file paths")
    # Check both spelling and resolved destination: relative and symlink paths
    # must not hide a credential directory from an existing path policy.
    result = []
    for path in paths:
        result.append(path)
        result.append(str((Path(cwd) / Path(path).expanduser()).resolve()))
    return list(dict.fromkeys(result))


def command_payload(tool, value):
    if tool == "Bash":
        command = value.get("command")
        if not isinstance(command, str) or not command.strip():
            raise PolicyError("missing shell command")
        approved = command.startswith("APPROVED=1 ")
        return {"command": command[len("APPROVED=1 "):] if approved else command}, approved
    # Preserve the server/tool split for QA tracker policy. Never pass the
    # server prefix as a verb (a server named 'postman' is not a write).
    parts = tool.split("__", 2)
    return {"tool_name": parts[2] if len(parts) == 3 else tool,
            "server_name": parts[1] if len(parts) == 3 else "",
            "tool_input": value}, False


def verdict_output(verdicts, approved=False):
    for permission in ("deny", "ask"):
        for verdict in verdicts:
            if verdict.get("permission") != permission:
                continue
            if permission == "ask" and approved:
                continue
            reason = verdict.get("user_message") or "blocked by policy"
            if permission == "ask":
                reason += (". Explicit user approval is required. For a shell command only, "
                           "after approval rerun the SAME command prefixed with APPROVED=1. "
                           "This marker records an approval convention; it does not verify consent.")
            return deny(reason)
    return {}


def lifecycle_payload(data):
    if not isinstance(data, dict):
        raise PolicyError("invalid lifecycle event")
    return {"status": "completed", "loop_count": 1 if data.get("stop_hook_active") else 0,
            "workspace_roots": [data["cwd"]] if data.get("cwd") else [],
            "conversation_id": data.get("session_id", "")}


def core(mode, data, script_dir):
    if mode == "require-review":
        verdict = run_policy(script_dir / "require-review.sh", lifecycle_payload(data), boundary=False)
        message = verdict.get("followup_message")
        return {"decision": "block", "reason": message} if message else {}
    tool, value = event_input(data)
    if mode == "block-catastrophic":
        payload, approved = command_payload(tool, value)
        return verdict_output([run_policy(script_dir / "block-catastrophic.sh", payload)], approved)
    if mode == "guard-read":
        verdicts = [run_policy(script_dir / "guard-read.sh", {"file_path": path})
                    for path in tool_paths(tool, value, data.get("cwd") or str(Path.cwd()))]
        return verdict_output(verdicts)
    raise PolicyError("unknown policy mode")


def project(data, root):
    try:
        hooks = json.loads((root / ".cursor/hooks.json").read_text())["hooks"]
        if not isinstance(hooks, dict):
            raise ValueError()
    except (OSError, ValueError, KeyError) as exc:
        raise PolicyError("project hook manifest unavailable or invalid") from exc
    event = data.get("hook_event_name", "PreToolUse")
    lifecycle = {"SessionStart": "sessionStart", "Stop": "stop", "SessionEnd": "sessionEnd"}
    if event in lifecycle:
        calls = [(lifecycle[event], lifecycle_payload(data))]
        approved = False
    else:
        tool, value = event_input(data)
        payload, approved = command_payload(tool, value)
        calls = []
        if tool == "Bash":
            calls.append(("beforeShellExecution", payload))
        elif tool.startswith("mcp__"):
            calls.append(("beforeMCPExecution", payload))
        calls.extend(("beforeReadFile", {"file_path": path})
                     for path in tool_paths(tool, value, data.get("cwd") or str(root)))
    verdicts = []
    messages = []
    for cursor_event, payload in calls:
        entries = hooks.get(cursor_event, [])
        if not isinstance(entries, list):
            raise PolicyError("invalid project event handlers")
        for entry in entries:
            command = shlex.split(entry["command"])
            script = (root / command[0]).resolve()
            # Generated projects intentionally reuse only their committed
            # Cursor shell scripts; do not interpret arbitrary shell strings.
            if not script.is_relative_to((root / ".cursor/hooks").resolve()) or script.suffix != ".sh":
                raise PolicyError("project policy command must be a .cursor/hooks shell script")
            verdict = run_policy(script, payload, command[1:], root, event not in lifecycle)
            verdicts.append(verdict)
            if verdict.get("followup_message"):
                messages.append(verdict["followup_message"])
    if event in lifecycle:
        return {"decision": "block", "reason": "\n".join(messages)} if event == "Stop" and messages else {}
    return verdict_output(verdicts, approved)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise PolicyError("invalid event object")
        here = Path(__file__).resolve()
        output = project(data, here.parents[2]) if mode == "project" else core(mode, data, here.parent.parent / "scripts")
    except (PolicyError, ValueError, KeyError, TypeError, IndexError, OSError) as exc:
        # Boundary failures deny; advisory lifecycle failures warn without
        # trapping the user in a repeated stop loop.
        if mode == "require-review" or ("data" in locals() and isinstance(data, dict)
                                         and data.get("hook_event_name") in ("SessionStart", "Stop", "SessionEnd")):
            output = {"systemMessage": "Agent policy reminder failed: " + str(exc)}
        else:
            output = deny("Agent policy failed closed: " + str(exc))
    print(json.dumps(output))


if __name__ == "__main__":
    main()
