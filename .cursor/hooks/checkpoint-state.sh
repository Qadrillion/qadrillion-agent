#!/usr/bin/env bash
# sessionStart / stop / sessionEnd hook — the memory layer's seatbelt.
#
# At sessionStart it fingerprints the working tree and docs/STATE.md.
# At stop it compares: if the tree changed during this conversation but
# docs/STATE.md did not, it asks the agent once (loop_limit 1) to overwrite
# STATE.md before finishing. Fail-open by design: a broken hook must never
# lock the agent out of ending a session.
#
# Usage in hooks.json: checkpoint-state.sh start | stop | end
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE_FILE="$ROOT/docs/STATE.md"
STORE="$ROOT/.cursor-temp/checkpoint"
PY="$(command -v python3 || echo /usr/bin/python3)"

emit() { local out="${1:-}"; [ -z "$out" ] && out='{}'; printf '%s\n' "$out"; exit 0; }

input="$(cat)"
read -r conv status loop_count < <(printf '%s' "$input" | "$PY" -c '
import json, sys, hashlib
try:
    d = json.load(sys.stdin)
    c = d.get("conversation_id") or ""
    key = hashlib.sha256(c.encode()).hexdigest()[:16] if c else ""
    print(key, (d.get("status") or "").lower(), int(d.get("loop_count") or 0))
except Exception:
    print("", "", 0)
')
[ -z "$conv" ] && emit

fingerprint() {
  {
    git -C "$ROOT" status --porcelain=v1 --untracked-files=normal 2>/dev/null
    git -C "$ROOT" diff HEAD --no-ext-diff 2>/dev/null
  } | shasum -a 256 | cut -c1-16
}
state_hash() { [ -f "$STATE_FILE" ] && shasum -a 256 "$STATE_FILE" | cut -c1-16 || echo none; }

case "${1:-}" in
  start)
    mkdir -p "$STORE" 2>/dev/null || emit
    [ -f "$STORE/$conv" ] && emit
    printf '%s %s\n' "$(fingerprint)" "$(state_hash)" > "$STORE/$conv" 2>/dev/null
    emit ;;
  stop)
    [ "$status" = "aborted" ] || [ "$status" = "error" ] && emit
    [ -f "$STORE/$conv" ] || emit
    read -r fp0 st0 < "$STORE/$conv"
    fp1="$(fingerprint)"; st1="$(state_hash)"
    if [ "$fp1" != "$fp0" ] && [ "$st1" = "$st0" ] && [ "$loop_count" -lt 1 ]; then
      emit '{"followup_message":"The working tree changed in this conversation but docs/STATE.md did not. Overwrite docs/STATE.md now (handover note, not a diary: goal, done, in progress, next, rejected, open) and then stop."}'
    fi
    printf '%s %s\n' "$fp1" "$st1" > "$STORE/$conv" 2>/dev/null
    emit ;;
  end)
    rm -f "$STORE/$conv" 2>/dev/null
    emit ;;
  *) emit ;;
esac
