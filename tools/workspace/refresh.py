#!/usr/bin/env python3
"""Inspect manifest repositories; --update fetches and fast-forwards eligible repos."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUTABILITY = {"status", "fetch", "fast-forward", "content-edit", "ticket-scoped-content-edit"}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate manifest key {key!r}")
        result[key] = value
    return result


def load_manifest(path: Path, root: Path) -> list[dict]:
    root = root.resolve()
    manifest = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("manifest schema_version must be 1")
    repos = manifest.get("repositories")
    if not isinstance(repos, list):
        raise ValueError("manifest repositories must be a list")
    ids, paths = set(), set()
    for repo in repos:
        if not isinstance(repo, dict):
            raise ValueError("each repository must be an object")
        for key in ("id", "path", "canonical_branch", "expected_remote"):
            if not isinstance(repo.get(key), str) or not repo[key].strip() or any(c in repo[key] for c in "\n\r\0"):
                raise ValueError(f"repository {key} must be a nonempty single-line string")
        if "ownership" in repo and repo["ownership"] not in ("owned", "dependency"):
            raise ValueError(f"{repo['id']}: ownership must be owned or dependency")
        relative = Path(repo["path"])
        destination = (root / relative).resolve()
        if relative.is_absolute() or not destination.is_relative_to(root):
            raise ValueError(f"{repo['id']}: path must resolve inside the workspace")
        if repo["id"] in ids or destination in paths:
            raise ValueError("repository ids and resolved paths must be unique")
        ids.add(repo["id"])
        paths.add(destination)
        modes = repo.get("allowed_mutability")
        if not isinstance(modes, list) or any(not isinstance(mode, str) or mode not in MUTABILITY for mode in modes):
            raise ValueError(f"{repo['id']}: allowed_mutability contains an unknown mode")
        if len(modes) != len(set(modes)):
            raise ValueError(f"{repo['id']}: allowed_mutability contains duplicates")
        if "fast-forward" in modes and "fetch" not in modes:
            raise ValueError(f"{repo['id']}: fast-forward requires fetch permission")
        scopes = repo.get("scopes", [])
        if not isinstance(scopes, list) or any(not isinstance(scope, str) or not scope.strip() for scope in scopes):
            raise ValueError(f"{repo['id']}: scopes must be a list of nonempty strings")
    return repos


def git(directory: Path, *arguments: str) -> subprocess.CompletedProcess:
    # Status must not refresh the index, and unattended fetches cannot prompt.
    environment = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(
        ["git", "-C", str(directory), *arguments], text=True, capture_output=True,
        env=environment, timeout=120, check=False,
    )


def inspect(repo: dict, root: Path, update: bool) -> tuple[str, bool]:
    directory = (root / repo["path"]).resolve()
    prefix = f"{repo['id']:<16} {repo['path']}"
    top = git(directory, "rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.strip()).resolve() != directory:
        return f"{prefix}  MISSING (no repository rooted here)", update
    branch = git(directory, "branch", "--show-current")
    status = git(directory, "status", "--porcelain=v1", "--untracked-files=normal")
    head = git(directory, "rev-parse", "--short", "HEAD")
    remote = git(directory, "remote", "get-url", "origin")
    if any(result.returncode for result in (branch, status, head)):
        return f"{prefix}  ERROR (cannot inspect repository state)", True
    current = branch.stdout.strip()
    notes = []
    matches_remote = remote.returncode == 0 and remote.stdout.strip() == repo["expected_remote"]
    if not matches_remote:
        notes.append("origin remote differs from manifest")
    if status.stdout:
        notes.append("dirty working tree")
    modes = repo["allowed_mutability"]
    failed = False
    if update and "fetch" in modes:
        if not matches_remote:
            notes.append("update refused")
            failed = True
        elif "fast-forward" in modes and (status.stdout or current != repo["canonical_branch"]):
            notes.append(f"update refused: requires clean {repo['canonical_branch']} branch")
            failed = True
        else:
            tracking_ref = f"refs/remotes/origin/{repo['canonical_branch']}"
            if "fast-forward" in modes:
                # A successful default fetch may exclude a deleted or unconfigured
                # canonical branch, leaving an old tracking ref available to merge.
                refspec = f"refs/heads/{repo['canonical_branch']}:{tracking_ref}"
                fetched = git(directory, "fetch", "--quiet", "origin", refspec)
            else:
                fetched = git(directory, "fetch", "--quiet", "origin")
            if fetched.returncode:
                # Never merge a stale tracking ref after the requested fetch fails.
                notes.append("fetch failed; no merge attempted")
                failed = True
            elif "fast-forward" in modes:
                # Fetch can outlast another actor's branch switch or local edit.
                # This snapshot narrows that window; it is not an atomic lock.
                next_top = git(directory, "rev-parse", "--show-toplevel")
                next_remote = git(directory, "remote", "get-url", "origin")
                next_branch = git(directory, "branch", "--show-current")
                next_status = git(directory, "status", "--porcelain=v1", "--untracked-files=normal")
                next_head = git(directory, "rev-parse", "--short", "HEAD")
                changed = (
                    any(result.returncode for result in (next_top, next_remote, next_branch, next_status, next_head))
                    or (root / repo["path"]).resolve() != directory
                    or Path(next_top.stdout.strip()).resolve() != directory
                    or next_remote.stdout.strip() != repo["expected_remote"]
                    or next_branch.stdout.strip() != current
                    or bool(next_status.stdout)
                    or next_head.stdout.strip() != head.stdout.strip()
                )
                if changed:
                    notes.append("update refused: repository changed during fetch; no merge attempted")
                    failed = True
                else:
                    merged = git(directory, "merge", "--ff-only", "--quiet", tracking_ref)
                    if merged.returncode:
                        notes.append("fast-forward failed")
                        failed = True
                    else:
                        notes.append("fast-forward complete")
                        next_head = git(directory, "rev-parse", "--short", "HEAD")
                if not next_branch.returncode:
                    current = next_branch.stdout.strip()
                if not next_head.returncode:
                    head = next_head
            else:
                notes.append("fetched; fast-forward not permitted")
    elif update:
        notes.append("update skipped: fetch not permitted")
    suffix = f"  [{'; '.join(notes)}]" if notes else ""
    return f"{prefix} @ {head.stdout.strip()} ({current or 'detached HEAD'}){suffix}", failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", help="include repositories with this scope")
    parser.add_argument("--update", action="store_true", help="fetch and fast-forward clean canonical branches when permitted")
    parser.add_argument("--manifest", type=Path, default=ROOT / "workspace-manifest.json", help="manifest path; its parent is the workspace root")
    args = parser.parse_args(argv)
    path = args.manifest.resolve()
    root = path.parent
    try:
        repositories = load_manifest(path, root)
    except (OSError, ValueError) as exc:
        print(f"Invalid workspace manifest: {exc}", file=sys.stderr)
        return 1
    failed = False
    for repo in repositories:
        if args.scope and args.scope not in repo.get("scopes", []):
            continue
        try:
            message, repo_failed = inspect(repo, root, args.update)
        except (OSError, subprocess.TimeoutExpired) as exc:
            message, repo_failed = f"{repo['id']}: git operation failed ({type(exc).__name__})", True
        print(message)
        failed = failed or repo_failed
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
