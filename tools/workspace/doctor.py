#!/usr/bin/env python3
"""Offline setup checks. Configured files are not proof of live trust or access."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from config import load, validate


def inspect(root: Path) -> list[dict[str, str]]:
    results = []

    def report(status, check, detail):
        results.append({"status": status, "check": check, "detail": detail})

    report("ok" if sys.version_info >= (3, 11) else "error", "python", "Python 3.11+ required")
    for executable in ("git", "bash"):
        report("ok" if shutil.which(executable) else "error", executable,
               "available" if shutil.which(executable) else "missing executable")
    required = ["AGENTS.md", "CLAUDE.md", "docs/STATE.md", "docs/decisions/INDEX.md",
                "docs/reference/known-quirks.md", "docs/reference/runtime-support.md",
                "docs/reference/integrations.md", "docs/reference/team-workflow.md", ".cursor/hooks.json",
                ".claude/settings.json", ".codex/hooks.json"]
    for name in required:
        report("ok" if (root / name).is_file() else "error", name, "required workspace file")
    try:
        data = load(root / "qa-config.json")
        errors = validate(data)
    except (OSError, ValueError) as exc:
        data, errors = {}, [str(exc)]
    for error in errors:
        report("error", "qa-config", error)
    if not errors:
        report("ok", "qa-config", "valid declarations; authentication and target roles not verified")
        for group in ("integrations", "runners"):
            for row in data[group]:
                if not row["enabled"]:
                    continue
                executable = row.get("executable") if group == "integrations" else row["argv"][0]
                if executable:
                    # Local runner paths are resolved against their declared working directory.
                    local = root / row.get("cwd", ".") / executable
                    if "/" in executable or "\\" in executable:
                        present = local.is_file() and os.access(local, os.X_OK)
                    else:
                        present = shutil.which(executable)
                    report("ok" if present else "error", row["id"], "executable available" if present else "missing executable: " + executable)
                if group == "runners":
                    for key in ("cwd", "artifacts"):
                        path = (root / row[key]).resolve()
                        if not path.is_relative_to(root):
                            report("error", row["id"], key + " resolves outside workspace")
                        elif key == "cwd" and not path.is_dir():
                            report("error", row["id"], "runner cwd missing: " + row[key])
        if not data["runners"]:
            report("info", "execution", "no automated runner configured; manual/black-box QA remains available")
        for env in data["environments"]:
            report("unverified", env["id"], "declared role is not independent target identity evidence")
    try:
        from refresh import load_manifest
        load_manifest(root / "workspace-manifest.json", root)
        report("ok", "manifest", "schema valid; run refresh.py for repository status")
    except (ImportError, OSError, ValueError, TypeError) as exc:
        report("error", "manifest", str(exc))
    sync = root / "tools/agents/sync.py"
    if sync.is_file():
        try:
            result = subprocess.run([sys.executable, str(sync), "--check"], cwd=root,
                                    capture_output=True, text=True, encoding="utf-8", timeout=30)
            report("ok" if result.returncode == 0 else "error", "adapters", result.stdout.strip() or result.stderr.strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            report("error", "adapters", str(exc))
    else:
        report("error", "adapters", "committed sync.py missing")
    for runtime in ("Cursor", "Claude Code", "Codex"):
        report("unverified", runtime, "native discovery, permissions and live hook blocking require the runtime smoke in docs/reference/runtime-support.md")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = inspect(args.root.resolve())
    if args.json:
        print(json.dumps({"checks": results, "live_access_tested": False}, indent=2))
    else:
        for row in results:
            print(f"{row['status'].upper():10} {row['check']}: {row['detail']}")
    return int(any(row["status"] == "error" for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
