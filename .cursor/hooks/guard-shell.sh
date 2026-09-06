#!/usr/bin/env bash
# beforeShellExecution hook — the deterministic boundary for shell commands.
# Reads the hook event JSON on stdin, prints {"permission": allow|ask|deny}.
#
# Boundaries live here, not in prose. If you find yourself writing "never ..."
# in AGENTS.md or a rule, add a line to this file (or guard.conf) instead.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=guard.conf
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

input="$(cat)"
command="$(printf '%s' "$input" | "$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("command") or "")
except Exception:
    print("")
')"

deny() {
  printf '{"permission":"deny","user_message":"Blocked by workspace hook: %s","agent_message":"Blocked by the workspace safety hook (.cursor/hooks/guard-shell.sh): %s. Do not retry or work around it. Tell the user what you wanted to run and why."}\n' "$1" "$1"
  exit 0
}
ask() {
  printf '{"permission":"ask","user_message":"Needs approval: %s","agent_message":"This action needs the user'"'"'s explicit approval: %s. Wait for the decision."}\n' "$1" "$1"
  exit 0
}
m() { printf '%s' "$command" | grep -qE -e "$1"; }
mi() { printf '%s' "$command" | grep -qiE -e "$1"; }

# ---------------------------------------------------------------- destructive
m 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s+("?(/|~|\$HOME)"?(\s|$)|~/(Documents|Desktop|Library|Downloads|Pictures)/?(\s|$))' \
  && deny "recursive force-delete of a home or system path"
# `git -C <dir> ...` is the same command aimed at a nested repo; match it too.
m 'git(\s+-C\s+\S+)?\s+push\b[^|;&]*(--force\b|--force-with-lease\b|[[:space:]]-f\b)' \
  && deny "git force-push"
m 'git(\s+-C\s+\S+)?\s+(reset\s+--hard|clean\s+-[a-zA-Z]*[fd]|checkout\s+\.|restore\s+\.|filter-branch|rebase\s+.*--root)' \
  && deny "discards uncommitted work or rewrites history"
m 'git(\s+-C\s+\S+)?\s+(branch\s+-D|push\b[^|;&]*--delete|tag\s+-d)' \
  && ask "deletes a branch or tag"
m '(mkfs|diskutil\s+(erase|reformat)|dd\s+.*of=/dev/)' \
  && deny "disk-level destructive operation"

# ---------------------------------------------------------------- isolation
if [ -n "${PROTECTED_PATHS:-}" ]; then
  m "$PROTECTED_PATHS" && deny "touches a protected path outside this workspace"
fi

# ---------------------------------------------------------------- credentials
SECRET_FILES='(\.env(\.[a-z]+)?\b|id_rsa|id_ed25519|\.pem\b|\.p12\b|\.keystore\b|credentials|\.netrc|\.aws/|\.ssh/|Keychains?|mcp\.json|accounts_pool)'
# Committed templates (*.example, *.template, *.sample) are safe to read: drop those
# tokens from the command before matching so `cat .env.example` is not a false deny.
scrubbed="$(printf '%s' "$command" | sed -E 's#[^[:space:]"'"'"'=]*\.(example|template|sample)[^[:space:]"'"'"']*##g')"
ms() { printf '%s' "$scrubbed" | grep -qE -e "$1"; }
# Reading secrets into context, or moving them off the machine — by a pager, a
# text tool, OR an interpreter (`python3 -c "open('.env')"` is still a read).
ms "(cat|less|more|head|tail|bat|xxd|strings|base64|scp|rsync|curl|wget|jq|yq|sed|awk|grep|rg|sqlite3|source)\\b[^|;&]*${SECRET_FILES}" \
  && deny "reads or copies credential material"
# interpreters take a quoted program that may itself contain ; & | — scan to end of line
ms "(python3?|node|ruby|perl|php|deno|bun)\\b.*${SECRET_FILES}" \
  && deny "interpreter reads credential material"
ms "(^|[;&|]\\s*)\\.\\s+[^|;&]*${SECRET_FILES}" \
  && deny "sources a credential file into the shell"
# local copy of a secret file: fine when the source is a committed template, otherwise ask
if m "(cp|mv)\\b[^|;&]*${SECRET_FILES}" && ! m '\.(example|template|sample)\b'; then
  ask "copies or moves a credential file"
fi
m '(\.env|secret|token|password|credential|PMAK|PAT)[^|;&]*\|[^|;&]*(curl|wget|nc)\b' \
  && deny "possible credential exfiltration"
m 'security\s+find-(generic|internet)-password' \
  && deny "dumps a keychain secret into the agent context"

# ---------------------------------------------------------------- production
# A test runner or mutation script pointed at production is denied outright.
# Release and production checks are human actions.
if [ -n "${TEST_RUNNERS:-}" ] && [ -n "${PROD_SELECTORS:-}" ]; then
  if m "$TEST_RUNNERS" && mi "$PROD_SELECTORS"; then
    deny "test or mutation run targets production"
  fi
fi
mi '(TEST_ENVIRONMENT|[A-Z_]*_ENV|ENVIRONMENT)=("?)(prod|production)\b' \
  && deny "environment variable selects production"

# ---------------------------------------------------------------- ask
if [ -n "${EXTRA_DENY:-}" ]; then m "$EXTRA_DENY" && deny "workspace-specific denied action"; fi
if [ -n "${EXTRA_ASK:-}" ];  then m "$EXTRA_ASK"  && ask  "workspace-specific gated action";  fi

m '((npm|pnpm|bun)\s+(i|install|add)|yarn\s+add|pip3?\s+install|uv\s+(add|pip\s+install)|brew\s+install|cargo\s+add|dotnet\s+add\s+package|gem\s+install|go\s+get)\s+[^-[:space:]]' \
  && ask "adds a new dependency"
m '(vercel\s+.*--prod|eas\s+(submit|build\s+.*--auto-submit)|npm\s+publish|supabase\s+db\s+push|gh\s+release\s+create|gh\s+pr\s+merge)' \
  && ask "deployment, release or merge action"
mi '(drop\s+(table|database|schema)|truncate\s+table|delete\s+from\s+[a-z_]+\s*(;|$)|update\s+[a-z_]+\s+set\b[^;]*$)' \
  && ask "destructive or unbounded database mutation"

printf '{"permission":"allow"}\n'
