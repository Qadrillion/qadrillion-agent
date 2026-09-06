#!/usr/bin/env bash
# refresh.sh — fetch and fast-forward the repositories in workspace-manifest.json.
#
#   ./tools/workspace/refresh.sh                 # status of every repo, no changes
#   ./tools/workspace/refresh.sh --scope mobile  # only repos whose scopes include "mobile"
#   ./tools/workspace/refresh.sh --update        # fetch, then fast-forward CLEAN repos on their canonical branch
#
# Never switches branches. A dirty tree or a non-canonical branch is reported
# and left alone. Missing repositories are reported, not cloned — cloning is a
# human step (credentials, org access).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$ROOT/workspace-manifest.json"
PY="$(command -v python3 || echo /usr/bin/python3)"
SCOPE=""; UPDATE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --scope)  SCOPE="$2"; shift 2 ;;
    --update) UPDATE=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

"$PY" - "$MANIFEST" "$SCOPE" <<'EOF' | while IFS=$'\t' read -r id path branch remote mut; do
import json, sys
m = json.load(open(sys.argv[1])); scope = sys.argv[2]
for r in m["repositories"]:
    if scope and scope not in r.get("scopes", []): continue
    print("\t".join([r["id"], r["path"], r["canonical_branch"], r["expected_remote"], ",".join(r["allowed_mutability"])]))
EOF
  dir="$ROOT/$path"
  if [ ! -d "$dir/.git" ] && ! git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '%-14s MISSING   %s\n' "$id" "$path"; continue
  fi
  actual_remote="$(git -C "$dir" remote get-url origin 2>/dev/null || echo none)"
  cur="$(git -C "$dir" branch --show-current 2>/dev/null || echo detached)"
  dirty="$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  note=""
  [ "$actual_remote" != "$remote" ] && note="remote differs from manifest ($actual_remote)"
  if [ "$UPDATE" -eq 1 ] && printf '%s' "$mut" | grep -q fetch; then
    git -C "$dir" fetch --quiet origin 2>/dev/null || note="${note:+$note; }fetch failed"
    if printf '%s' "$mut" | grep -q fast-forward && [ "$cur" = "$branch" ] && [ "$dirty" = "0" ]; then
      git -C "$dir" merge --ff-only --quiet "origin/$branch" 2>/dev/null && note="${note:+$note; }fast-forwarded" || note="${note:+$note; }not fast-forwardable"
    else
      [ "$cur" != "$branch" ] && note="${note:+$note; }on $cur, not $branch — left alone"
      [ "$dirty" != "0" ] && note="${note:+$note; }dirty ($dirty files) — left alone"
    fi
  fi
  printf '%-14s %-9s %s @ %s%s\n' "$id" "$cur" "$path" "$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)" "${note:+  [$note]}"
done
