#!/usr/bin/env bash
# beforeReadFile hook — stops credential material entering the agent context.
# Reads the hook event JSON on stdin, prints {"permission": allow|deny}.
#
# ORDERING IS THE SECURITY PROPERTY. Deny first, exempt second.
# A version that ran the template allow-list first let `secrets.template.env`
# through because "template" appeared *somewhere* in the name. Now:
#   1. key / credential material is denied with no exemption at all;
#   2. the committed-template exemption applies only when the safe marker is
#      the FINAL extension (`.env.example`, not `example.env`);
#   3. the env family is denied unless (2) matched.
# Note: this event is not available to cloud agents in every harness — shell
# fences in guard-shell.sh cover the `cat .env` path independently.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=guard.conf
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

input="$(cat)"
path="$(printf '%s' "$input" | "$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("file_path") or d.get("path") or "")
except Exception:
    print("")
')"

deny() {
  printf '{"permission":"deny","user_message":"Blocked read: %s","agent_message":"Reading %s is blocked by the workspace safety hook (.cursor/hooks/guard-read.sh): it holds credential material. Ask the user for the value, or use a CLI that reads it from the keychain."}\n' "$1" "$1"
  exit 0
}

# 1 — hard deny, no exemption reaches this block
case "$path" in
  id_rsa*|*/id_rsa*|id_ed25519*|*/id_ed25519*)       deny "$path" ;;
  *.pem|*.p12|*.keystore|*.jks|*.pfx)                 deny "$path" ;;
  */.ssh/*|*/.aws/*|*/.netrc|*/.npmrc|*/.pypirc)      deny "$path" ;;
  mcp.json|*/mcp.json|.cursor/mcp.json|*/.codex/auth.json|.claude/settings.local.json|*/.claude/settings.local.json) deny "$path" ;;
  */Keychains/*|*/Library/Keychains/*)                deny "$path" ;;
  *credentials|*credentials.*|*/credentials/*)        deny "$path" ;;
esac
if [ -n "${PROTECTED_PATHS:-}" ] && printf '%s' "$path" | grep -qE -e "$PROTECTED_PATHS"; then
  deny "$path"
fi
for pat in ${EXTRA_DENY_READ:-}; do
  # shellcheck disable=SC2254
  case "$path" in $pat) deny "$path" ;; esac
done

# 2 — committed-template convention: safe marker must be the FINAL extension
case "$path" in
  *.example|*.template|*.sample) printf '{"permission":"allow"}\n'; exit 0 ;;
esac

# 3 — env family
case "$path" in
  *.env|*.env.*|*/.env|*/.env.*) deny "$path" ;;
esac

printf '{"permission":"allow"}\n'
