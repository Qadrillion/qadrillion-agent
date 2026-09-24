#!/usr/bin/env bash
# beforeReadFile: credential paths are checked before template exemptions.
# This protects supported file-read events, not arbitrary shell programs.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

"$PY" -c '
import fnmatch
import json
import os
import re
import sys


def result(permission, reason=None):
    response = {"permission": permission}
    if reason:
        response.update(user_message="Blocked read: " + reason,
                        agent_message="The workspace file-read guard denied this request: " + reason +
                        ". Do not retry or expose secrets. Use a configured credential provider without returning its secret value.")
    print(json.dumps(response))
    sys.exit(0)


try:
    event = json.load(sys.stdin)
    if not isinstance(event, dict):
        raise ValueError()
    paths = [event[key] for key in ("file_path", "path") if key in event]
    if not paths or any(not isinstance(path, str) or not path.strip() or "\0" in path for path in paths):
        raise ValueError()
    if len(set(paths)) != 1:
        raise ValueError()
    path = paths[0]
except (ValueError, TypeError):
    result("deny", "invalid event; a nonempty file_path or path string is required")

protected, extra = sys.argv[1:]
candidates = {path, os.path.abspath(path), os.path.realpath(path)}
for candidate in candidates:
    # Normalization catches relative dotfiles and resolvable symlink targets.
    hard = (
        r"(^|/)(id_rsa|id_ed25519)[^/]*($|/)",
        r"\.(pem|p12|keystore|jks|pfx)$",
        r"(^|/)(\.ssh|\.aws)(/|$)",
        r"(^|/)(\.netrc|\.npmrc|\.pypirc)$",
        r"(^|/)mcp\.json$",
        r"(^|/)\.codex/auth\.json$",
        r"(^|/)\.claude/settings\.local\.json$",
        r"(^|/)Keychains(/|$)",
        r"credentials($|[./])",
    )
    if any(re.search(pattern, candidate) for pattern in hard):
        result("deny", path)
    try:
        if protected and re.search(protected, candidate):
            result("deny", path)
    except re.error:
        result("deny", "invalid protected-path configuration")
    if any(fnmatch.fnmatchcase(candidate, pattern) for pattern in extra.split()):
        result("deny", path)
    if candidate.endswith((".example", ".template", ".sample")):
        continue
    if re.search(r"\.env($|[./])", candidate):
        result("deny", path)
result("allow")
' "${PROTECTED_PATHS:-}" "${EXTRA_DENY_READ:-}"
