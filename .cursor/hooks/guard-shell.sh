#!/usr/bin/env bash
# beforeShellExecution — defense-in-depth checks for recognizable commands.
# Reads the hook event JSON on stdin, prints {"permission": allow|ask|deny}.
#
# Regex checks are not a shell parser or a sandbox. Unknown programs, aliases,
# obfuscation and scripts can have effects these heuristics cannot establish.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=guard.conf
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

deny() {
  printf '{"permission":"deny","user_message":"Blocked by workspace hook: %s","agent_message":"Blocked by the workspace safety hook (.cursor/hooks/guard-shell.sh): %s. Do not retry or work around it. Tell the user what you wanted to run and why."}\n' "$1" "$1"
  exit 0
}
ask() {
  printf '{"permission":"ask","user_message":"Needs approval: %s","agent_message":"This action needs the user'"'"'s explicit approval: %s. Wait for the decision."}\n' "$1" "$1"
  exit 0
}
input="$(cat)"
if ! command="$(printf '%s' "$input" | "$PY" -c '
import json, sys
try:
    event = json.load(sys.stdin)
    command = event.get("command") if isinstance(event, dict) else None
    if not isinstance(command, str) or not command.strip() or "\0" in command:
        raise ValueError()
    print(command)
except (ValueError, TypeError):
    sys.exit(1)
')"; then
  deny "invalid hook event; command must be a nonempty string"
fi
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
SECRET_FILES='(\.env(\.[a-z]+)?\b|id_rsa|id_ed25519|\.pem\b|\.p12\b|\.keystore\b|credentials|\.netrc|\.npmrc|\.pypirc|\.codex/auth\.json|\.aws/|\.ssh/|Keychains?|mcp\.json|accounts_pool)'
# Committed templates (*.example, *.template, *.sample) are safe to read: drop those
# tokens from the command before matching so `cat .env.example` is not a false deny.
scrubbed="$(printf '%s' "$command" | "$PY" -c '
import re, shlex, sys
command = sys.stdin.read()
# Remove only negative globs in a standalone, narrowly recognized rg file-list
# command. Pipelines, substitutions, unknown options and positive paths remain.
if not any(char in command for char in "`$;|&<>\n\r"):
    try:
        words = shlex.split(command)
        if words and words[0] == "rg" and "--files" in words:
            clean, index = ["rg"], 1
            while index < len(words):
                word = words[index]
                if word in ("-g", "--glob") and index + 1 < len(words) and words[index + 1].startswith("!"):
                    index += 2
                    continue
                if word.startswith("--glob=!"):
                    index += 1
                    continue
                if word.startswith("-") and word not in ("--files", "--hidden", "--no-ignore", "--no-ignore-vcs"):
                    break
                clean.append(word)
                index += 1
            else:
                command = shlex.join(clean)
    except ValueError:
        pass
sys.stdout.write(command)
' | sed -E 's#[^[:space:]"'"'"'=;|&()]*\.(example|template|sample)([[:space:]"'"'"'=;|&()]|$)#\2#g')"
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
if m "(cp|mv)\\b[^|;&]*${SECRET_FILES}"; then
  if ! printf '%s' "$command" | "$PY" -c '
import shlex, sys
try:
    words = shlex.split(sys.stdin.read())
    safe = len(words) == 3 and words[0] in ("cp", "mv") and words[1].endswith((".example", ".template", ".sample"))
except ValueError:
    safe = False
sys.exit(0 if safe else 1)
'; then
    ask "copies or moves a credential file"
  fi
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
# These common CLI spellings are gated even when no MCP connector is involved.
# They intentionally do not claim to classify arbitrary programs or API effects.
m '(acli|twg)\b[^|;&]*\b(create|update|edit|delete|remove|transition|assign|post|send|publish|write|upload|add|set|close|reopen)\b' \
  && ask "tracker or workspace CLI mutation"
m 'gh\s+(issue|pr|release|repo|project|label|gist)\b[^|;&]*\b(create|edit|comment|close|reopen|merge|review|ready|lock|unlock|delete|archive|transfer|add|remove)\b' \
  && ask "GitHub CLI mutation"
mi '(gh\s+api|az\s+rest)\b[^|;&]*(-X[[:space:]]*|--method[=[:space:]]+)(POST|PUT|PATCH|DELETE)\b' \
  && ask "API mutation method"
m 'gh\s+api\b[^|;&]*([[:space:]]-[fF]([[:space:]]|[^-[:space:]])|--(raw-)?field([=[:space:]]))' \
  && ask "GitHub API fields can imply a POST request"
m 'az\b[^|;&]*\b(create|update|delete|set|start|stop|restart|deallocate|redeploy|assign|remove|add|upload|import|restore|swap)\b' \
  && ask "cloud CLI mutation"
mi '(curl\b[^|;&]*(-X[[:space:]]*|--request[=[:space:]]+)(POST|PUT|PATCH|DELETE)\b|curl\b[^|;&]*([[:space:]]-[dFT]([[:space:]]|[^-[:space:]])|--(data[^[:space:]]*|form|upload-file)([=[:space:]]))|wget\b[^|;&]*--(post-data|post-file|method[=[:space:]]+(POST|PUT|PATCH|DELETE)))' \
  && ask "HTTP request may mutate external state"
mi '(drop\s+(table|database|schema)|truncate\s+table|delete\s+from\s+[a-z_]+\s*(;|$)|update\s+[a-z_]+\s+set\b[^;]*$)' \
  && ask "destructive or unbounded database mutation"

printf '{"permission":"allow"}\n'
