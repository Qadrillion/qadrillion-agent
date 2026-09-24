#!/usr/bin/env bash
# sessionStart / stop / sessionEnd hook — the memory layer's seatbelt.
#
# At sessionStart it fingerprints the working tree and docs/STATE.md.
# At stop it compares: if the tree changed during this conversation but
# docs/STATE.md did not, it asks the agent once per conversation to overwrite
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
    c = d.get("conversation_id")
    status = d.get("status") or "-"
    loops = d.get("loop_count", 0)
    if not isinstance(c, str) or not c.strip() or not isinstance(status, str):
        raise ValueError()
    if any(char.isspace() for char in status):
        raise ValueError()
    if type(loops) is not int or loops < 0:
        raise ValueError()
    key = hashlib.sha256(c.encode()).hexdigest()[:16]
    print(key, status.lower(), loops)
except Exception:
    print("-", "-", 0)
')
[ -z "$conv" ] || [ "$conv" = "-" ] && emit

fingerprint() {
  {
    git -C "$ROOT" status --porcelain=v1 --untracked-files=normal -- . ':(exclude).cursor-temp' 2>/dev/null || return 1
    git -C "$ROOT" diff HEAD --no-ext-diff -- . ':(exclude).cursor-temp' 2>/dev/null || return 1
    # Git status names untracked paths but misses edits to an existing path.
    # Metadata avoids reading arbitrary untracked contents or following links.
    # Same-size edits preserving all timestamps can escape this advisory check.
    "$PY" - "$ROOT" <<'PY'
import hashlib
import os
import subprocess
import sys

try:
    root = os.fsencode(sys.argv[1])
    listing = subprocess.run(
        ["git", "-C", sys.argv[1], "ls-files", "--others", "--exclude-standard", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10,
    ).stdout
    digest = hashlib.sha256()
    for path in sorted(listing.split(b"\0")):
        if not path or path == b".cursor-temp" or path.startswith(b".cursor-temp/"):
            continue
        stat = os.lstat(os.path.join(root, path))
        metadata = (stat.st_mode, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        digest.update(path + b"\0" + repr(metadata).encode() + b"\0")
    print(digest.hexdigest())
except Exception:
    sys.exit(1)
PY
  } | shasum -a 256 | cut -c1-16
}
state_hash() { [ -f "$STATE_FILE" ] && shasum -a 256 "$STATE_FILE" | cut -c1-16 || echo none; }

case "${1:-}" in
  start)
    mkdir -p "$STORE" 2>/dev/null || emit
    [ -f "$STORE/$conv" ] && emit
    fp="$(fingerprint)" || emit
    st="$(state_hash)" || emit
    printf '%s %s 0\n' "$fp" "$st" > "$STORE/$conv" 2>/dev/null
    emit ;;
  stop)
    [ "$status" = "aborted" ] || [ "$status" = "error" ] && emit
    [ -f "$STORE/$conv" ] || emit
    read -r fp0 st0 prompted < "$STORE/$conv" || emit
    fp1="$(fingerprint)" || emit
    st1="$(state_hash)" || emit
    if [ "$fp1" != "$fp0" ] && [ "$st1" = "$st0" ] && [ "$loop_count" -lt 1 ] && [ "${prompted:-0}" != 1 ]; then
      # Persist before emitting: runtimes may omit or reset their loop counter.
      printf '%s %s 1\n' "$fp1" "$st1" > "$STORE/$conv" 2>/dev/null || emit
      emit '{"followup_message":"The working tree changed in this conversation but docs/STATE.md did not. Overwrite docs/STATE.md now (handover note, not a diary: goal, done, in progress, next, rejected, open) and then stop."}'
    fi
    printf '%s %s %s\n' "$fp1" "$st1" "${prompted:-0}" > "$STORE/$conv" 2>/dev/null
    emit ;;
  end)
    rm -f "$STORE/$conv" 2>/dev/null
    emit ;;
  *) emit ;;
esac
