#!/usr/bin/env python3
"""Translate native hook events to committed Cursor policies without running tool input."""
import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path


class PolicyError(Exception):
    pass


# Codex documents Bash as its shell hook name, including unified exec. The
# exec_command alias also accepts the actual local tool's documented cmd input.
SHELL_TOOLS = {"Bash", "exec_command"}
FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch"}
PATH_FIELDS = {"path", "file_path", "filename", "notebook_path", "source", "destination",
               "source_path", "destination_path", "old_path", "new_path"}
LIFECYCLE = {"SessionStart": "sessionStart", "Stop": "stop", "SessionEnd": "sessionEnd"}
POLICY_TIMEOUT = 8


def decision(permission, reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": permission, "permissionDecisionReason": reason}}


def verdict_output(verdicts, runtime):
    for permission in ("deny", "ask"):
        for verdict in verdicts:
            if verdict.get("permission") == permission:
                reason = verdict.get("user_message") or verdict.get("agent_message") or "Blocked by workspace policy"
                if permission == "ask" and runtime == "codex":
                    reason += (". This Codex hook cannot request native approval. "
                               "The action is blocked; prepare it for the user's manual execution. "
                               "A command prefix or tool argument cannot grant approval.")
                    permission = "deny"
                return decision(permission, reason)
    # An explicit native allow could skip the runtime's own permission checks.
    return {}


def require_string(value, label):
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise PolicyError("missing or invalid " + label)
    return value


def paths_in(value):
    paths = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PATH_FIELDS:
                if key in {"source", "destination"} and isinstance(item, (dict, list)):
                    paths.extend(paths_in(item))
                else:
                    paths.append(require_string(item, "path argument"))
            elif key == "paths":
                if not isinstance(item, list) or not item:
                    raise PolicyError("invalid paths argument")
                paths.extend(require_string(path, "path argument") for path in item)
            elif isinstance(item, (dict, list)):
                paths.extend(paths_in(item))
    elif isinstance(value, list):
        for item in value:
            paths.extend(paths_in(item))
    return paths


def patch_paths(value):
    patch = require_string(value.get("command"), "patch command")
    lines = patch.splitlines()
    if lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        raise PolicyError("invalid patch boundaries")
    paths = []
    actions = 0
    for line in lines[1:-1]:
        if not line.startswith("*** "):
            continue
        match = re.fullmatch(r"\*\*\* (Add File|Update File|Delete File|Move to): (.*)", line)
        if match:
            paths.append(require_string(match[2], "patch path"))
            actions += match[1] != "Move to"
        elif line != "*** End of File":
            raise PolicyError("unrecognized patch header")
    if not actions:
        raise PolicyError("patch has no recognized file actions")
    return paths


def tool_paths(tool, value, cwd):
    paths = paths_in(value)
    if tool == "apply_patch":
        paths.extend(patch_paths(value))
    if tool in FILE_TOOLS and not paths:
        raise PolicyError("file operation has no recognized path")
    if len(paths) > 128:
        raise PolicyError("too many paths to check in one hook event")
    result = []
    for path in paths:
        result.extend((path, str((cwd / Path(path).expanduser()).resolve())))
    return list(dict.fromkeys(result))


def run_policy(root, entry, payload, deadline, boundary):
    if not isinstance(entry, dict) or not isinstance(entry.get("command"), str):
        raise PolicyError("invalid project hook definition")
    try:
        argv = shlex.split(entry["command"])
        if not argv:
            raise ValueError()
        script = (root / argv[0]).resolve()
        if not script.is_relative_to((root / ".cursor/hooks").resolve()) or script.suffix != ".sh":
            raise PolicyError("policy command must reference a committed .cursor/hooks shell script")
        timeout = deadline - time.monotonic()
        if timeout <= 0:
            raise PolicyError("policy deadline exceeded")
        result = subprocess.run(["bash", str(script), *argv[1:]], input=json.dumps(payload),
                                capture_output=True, text=True, timeout=timeout, cwd=root)
        if result.returncode:
            raise PolicyError("policy process failed: " + script.name)
        verdict = json.loads(result.stdout)
        if not isinstance(verdict, dict):
            raise ValueError()
        if boundary and verdict.get("permission") not in {"allow", "ask", "deny"}:
            raise ValueError()
        for key in ("user_message", "agent_message", "followup_message"):
            if key in verdict and not isinstance(verdict[key], str):
                raise ValueError()
        return verdict
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise PolicyError("policy unavailable, timed out, or invalid") from exc


def project(data, root, runtime):
    if not isinstance(data, dict):
        raise PolicyError("invalid event object")
    event = data.get("hook_event_name", "PreToolUse")
    if event not in {"PreToolUse", *LIFECYCLE}:
        raise PolicyError("unsupported hook event")
    hooks = json.loads((root / ".cursor/hooks.json").read_text())["hooks"]
    if not isinstance(hooks, dict):
        raise PolicyError("invalid project hook manifest")
    cwd = Path(require_string(data.get("cwd", str(root)), "working directory"))
    if not cwd.is_absolute():
        raise PolicyError("hook working directory must be absolute")
    if event in LIFECYCLE:
        calls = [(LIFECYCLE[event], {"status": "completed", "workspace_roots": [str(root)],
                 "conversation_id": data.get("session_id", ""),
                 "loop_count": 1 if data.get("stop_hook_active") else 0})]
    else:
        tool = require_string(data.get("tool_name"), "tool name")
        value = data.get("tool_input")
        if not isinstance(value, dict):
            raise PolicyError("invalid tool arguments")
        calls = []
        if tool in SHELL_TOOLS:
            key = "cmd" if tool == "exec_command" else "command"
            command = require_string(value.get(key), "shell command")
            calls.append(("beforeShellExecution", {"command": command, "cwd": str(cwd)}))
        elif tool.startswith("mcp__"):
            parts = tool.split("__", 2)
            if len(parts) != 3 or not all(parts[1:]):
                raise PolicyError("invalid MCP tool name")
            calls.append(("beforeMCPExecution", {"server_name": parts[1], "tool_name": parts[2],
                                               "tool_input": value}))
        calls.extend(("beforeReadFile", {"file_path": path}) for path in tool_paths(tool, value, cwd))
    deadline = time.monotonic() + (2 if event == "SessionEnd" else POLICY_TIMEOUT)
    verdicts = []
    for cursor_event, payload in calls:
        entries = hooks.get(cursor_event)
        if not isinstance(entries, list) or (event == "PreToolUse" and not entries):
            raise PolicyError("missing or invalid policy handlers: " + cursor_event)
        verdicts.extend(run_policy(root, entry, payload, deadline, event == "PreToolUse")
                        for entry in entries)
    if event in LIFECYCLE:
        messages = [item["followup_message"] for item in verdicts if item.get("followup_message")]
        return {"decision": "block", "reason": "\n".join(messages)} if event == "Stop" and messages else {}
    return verdict_output(verdicts, runtime)


def main(runtime=None, root=None):
    if runtime is None:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--runtime", choices=("claude", "codex"), required=True)
        runtime = parser.parse_args().runtime
    root = root or Path(__file__).resolve().parents[2]
    data = None
    try:
        data = json.load(sys.stdin)
        output = project(data, root, runtime)
    except Exception as exc:
        # Native runtimes often ignore hook crashes; emit a valid denial instead.
        if isinstance(data, dict) and data.get("hook_event_name") in LIFECYCLE:
            output = {"systemMessage": "Workspace reminder failed: " + str(exc)}
        else:
            output = decision("deny", "Workspace policy failed closed: " + str(exc))
    print(json.dumps(output))


if __name__ == "__main__":
    main()
