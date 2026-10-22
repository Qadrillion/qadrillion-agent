#!/usr/bin/env python3
"""Generate project runtime adapters from neutral .agent sources (Python 3.11+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import tomllib
import uuid


ROOT = Path(__file__).resolve().parents[2]
LEDGER = "tools/agents/generated.json"
OLD_LEDGER = ".codex/agent-core-managed.json"
CONFIGS = {"codex": ".codex/hooks.json", "claude": ".claude/settings.json"}
MATCHER = "^(Bash|exec_command|Read|Edit|Write|MultiEdit|NotebookEdit|apply_patch|mcp__.*)$"
GENERATOR_ID = "qadrillion-agent-runtime"
TRANSACTION = ".agent-runtime-transaction"
CODEX_LAUNCHER = '''import json
from pathlib import Path
import runpy

try:
    cwd = Path.cwd().resolve()
    roots = [path for path in (cwd, *cwd.parents)
             if (path / "tools/agents/generated.json").exists()]
    if len(roots) != 1:
        raise RuntimeError("Expected exactly one ancestor QA workspace; refusing missing or ambiguous policy root")
    root = roots[0]
    marker = root / "tools/agents/generated.json"
    if marker.resolve() != marker:
        raise RuntimeError("QA workspace marker must not be a symlink")
    state = json.loads(marker.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("generator") != "qadrillion-agent-runtime":
        raise RuntimeError("Unrecognized QA workspace marker")
    script = root / ".codex/hooks/adapter.py"
    if script.resolve() != script:
        raise RuntimeError("QA workspace adapter must not be a symlink")
    runpy.run_path(str(script), run_name="__main__")
except Exception as exc:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": "Workspace policy launcher failed closed: " + str(exc)}}))
'''


class SyncError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SyncError(f"Expected JSON object: {path}")
    return value


def metadata(path):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise SyncError(f"Missing frontmatter: {path}")
    fields = {}
    for line in parts[1].strip().splitlines():
        if not line or line.startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise SyncError(f"Use single-line scalar frontmatter in {path}")
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        if not value or value in {"|", ">"}:
            raise SyncError(f"Missing or unsupported {key} in {path}")
        fields[key] = value
    for key in ("name", "description"):
        if not fields.get(key):
            raise SyncError(f"Missing {key}: {path}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", fields["name"]):
        raise SyncError(f"Invalid agent/skill name: {path}")
    return fields, parts[2].lstrip()


def hook_groups(runtime):
    if runtime == "codex":
        # Hooks use session cwd, which may be a nested Git checkout. Git root
        # discovery could select that checkout's policy instead of ours.
        command = "python3 -c " + shlex.quote(CODEX_LAUNCHER)
    else:
        command = 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.sh"'
    groups = {}
    for event in ("PreToolUse", "SessionStart", "Stop", "SessionEnd"):
        group = {"hooks": [{"type": "command", "command": command,
                             "timeout": 3 if event == "SessionEnd" else 30}]}
        if event == "PreToolUse":
            group = {"matcher": MATCHER, **group}
        groups[event] = [group]
    return groups


def desired_files(root):
    root = root.resolve()
    canonical = root / ".agent"
    if not canonical.is_dir() or canonical.resolve() != canonical:
        raise SyncError("Canonical .agent must be a real workspace directory")
    for name in ("agents", "rules", "hooks", "skills"):
        directory = canonical / name
        if not directory.is_dir() or directory.resolve() != directory:
            raise SyncError(f"Canonical {name} must be a real workspace directory")
    files = {
        ".codex/hooks/adapter.py": (root / "tools/agents/templates/codex-adapter.py").read_bytes(),
        ".claude/hooks/pretooluse.sh": (root / "tools/agents/templates/claude-pretooluse.sh").read_bytes(),
    }
    modes = {".claude/hooks/pretooluse.sh": 0o755}
    for path in sorted((root / ".agent/agents").glob("*.md")):
        if path.is_symlink():
            raise SyncError(f"Canonical agent must not be a symlink: {path}")
        fields, body = metadata(path)
        name = fields["name"]
        if name != path.stem:
            raise SyncError(f"Agent name must match filename: {path}")
        readonly = fields.get("readonly", "false")
        if readonly not in {"true", "false"}:
            raise SyncError(f"readonly must be true or false: {path}")
        codex = '# Generated by tools/agents/sync.py; edit .agent/agents.\n'
        for key, value in (("name", name), ("description", fields["description"]),
                           ("developer_instructions", body)):
            codex += f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
        if readonly == "true":
            codex += 'sandbox_mode = "read-only"\n'
        tomllib.loads(codex)
        files[f".codex/agents/{name}.toml"] = codex.encode("utf-8")
        claude = "---\n" + "\n".join(f"{key}: {json.dumps(fields[key], ensure_ascii=False)}"
                                    for key in ("name", "description"))
        claude += "\nmodel: inherit\n"
        if readonly == "true":
            # A Write/Edit denylist still leaves shell, MCP, and delegation
            # paths able to mutate; these roles need only local source reads.
            claude += "tools: Read, Grep, Glob\n"
        claude += "---\n\n" + body
        files[f".claude/agents/{name}.md"] = claude.encode("utf-8")
    links = {}
    skill_root = root / ".agent/skills"
    if not skill_root.is_dir() or skill_root.resolve() != skill_root:
        raise SyncError("Canonical skills must be a real workspace directory")
    for skill in sorted(skill_root.iterdir()):
        if not skill.is_dir() or skill.is_symlink():
            raise SyncError(f"Expected a real canonical skill directory: {skill}")
        fields, _ = metadata(skill / "SKILL.md")
        if fields["name"] != skill.name:
            raise SyncError(f"Skill name must match directory: {skill}")
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise SyncError(f"Canonical skill must not contain symlinks: {path}")
        for directory in (".agents/skills", ".claude/skills"):
            links[f"{directory}/{skill.name}"] = f"../../.agent/skills/{skill.name}"
    return files, {relative: modes.get(relative, 0o644) for relative in files}, links


def safe_path(root, relative, replacements=()):
    if not isinstance(relative, str):
        raise SyncError(f"Invalid managed path: {relative}")
    path = Path(relative)
    if (path.is_absolute() or ".." in path.parts
            or str(path) == "." or path.as_posix() != relative):
        raise SyncError(f"Invalid managed path: {relative}")
    for parent in (path, *path.parents):
        candidate = root / parent
        if candidate.is_symlink() and parent.as_posix() not in replacements:
            raise SyncError(f"Refusing generated path through a symlink: {parent}")
    return root / path


def merge_hooks(root, runtime, previous, wanted):
    path = root / CONFIGS[runtime]
    config = read_json(path) if path.exists() else {}
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SyncError(f"Invalid hooks object: {path}")
    for event in sorted(set(previous) | set(wanted)):
        current = hooks.get(event, [])
        if not isinstance(current, list):
            raise SyncError(f"Invalid hook groups: {path}: {event}")
        current = current.copy()
        additions = list(wanted.get(event, []))
        for group in previous.get(event, []):
            if group not in current:
                raise SyncError(f"Managed hook changed locally: {path}: {event}; restore or move the custom hook first")
            index = current.index(group)
            current.pop(index)
            if additions:
                replacement = additions.pop(0)
                if replacement not in current:
                    current.insert(index, replacement)
        for group in additions:
            if group not in current:
                current.append(group)
        hooks[event] = current
    return encoded(config)


def load_state(root):
    path = safe_path(root, LEDGER)
    if path.exists():
        state = read_json(path)
        if (state.get("version") not in {1, 2} or not isinstance(state.get("files"), dict)
                or not isinstance(state.get("hooks"), dict) or not isinstance(state.get("links", {}), dict)):
            raise SyncError("Invalid generated-file ledger")
        validate_state_paths(root, state)
        return state, False
    legacy = read_json(root / "tools/agents/legacy.json")
    # Only known historical output is adopted; an untracked collision is never
    # assumed to be generated simply because it has a familiar filename.
    validate_state_paths(root, legacy)
    return legacy, True


def validate_state_paths(root, state):
    for relative in state["files"]:
        safe_path(root, relative)
    for relative in state.get("links", {}):
        safe_path(root, relative, (relative,))
    for relative in state.get("modes", {}):
        safe_path(root, relative)
        if relative not in state["files"]:
            raise SyncError(f"Mode without a managed file: {relative}")


def managed_skill_tree(root, relative, state):
    """Adopt only exact owned copies, before any generated path is changed."""
    path = safe_path(root, relative)
    expected = {name: checksum for name, checksum in state["files"].items()
                if name.startswith(relative + "/")}
    if not expected:
        raise SyncError(f"Unmanaged skill directory collision: {relative}")
    for name in expected:
        member = safe_path(root, name)
        if not member.is_relative_to(path) or member == path:
            raise SyncError(f"Invalid managed skill member: {name}")
    directories = {str(parent) for name in expected for parent in Path(name).parents
                   if str(parent).startswith(relative + "/")}
    for current in path.rglob("*"):
        name = current.relative_to(root).as_posix()
        if current.is_symlink():
            raise SyncError(f"Unexpected symlink in generated skill: {name}")
        if current.is_dir():
            if name not in directories:
                raise SyncError(f"Unmanaged directory in generated skill: {name}")
        elif (not current.is_file() or name not in expected
              or digest(current.read_bytes()) != expected[name]
              or (current.stat().st_mode & 0o777) != state.get("modes", {}).get(name, current.stat().st_mode & 0o777)):
            raise SyncError(f"Generated skill changed locally: {name}")
    for name in expected:
        if not (root / name).is_file():
            raise SyncError(f"Generated skill file missing: {name}")
    return sorted(expected)


def plan(root):
    files, modes, links = desired_files(root)
    state, migrating = load_state(root)
    replacements = {}
    link_updates = {}
    for relative, target in links.items():
        path = safe_path(root, relative, (relative,))
        if path.is_symlink():
            current = os.readlink(path)
            if current == target:
                continue
            old_target = target.replace(".agent/", ".cursor/")
            if state.get("links", {}).get(relative) != current and not (migrating and current == old_target):
                raise SyncError(f"Unexpected skill symlink: {relative}")
        elif path.is_dir():
            replacements[relative] = managed_skill_tree(root, relative, state)
        elif path.exists():
            old_target = target.replace(".agent/", ".cursor/")
            if not migrating or not path.is_file() or path.read_text(encoding="utf-8").strip() != old_target:
                raise SyncError(f"Unexpected skill file: {relative}")
        link_updates[relative] = target
    updates = {}
    for relative, content in files.items():
        path = safe_path(root, relative)
        if path.exists():
            if not path.is_file():
                raise SyncError(f"Generated file collides with directory: {relative}")
            old = path.read_bytes()
            old_mode = path.stat().st_mode & 0o777
            if old == content and old_mode == modes[relative]:
                continue
            if (digest(old) != state["files"].get(relative)
                    or old_mode != state.get("modes", {}).get(relative, old_mode)):
                raise SyncError(f"Generated file changed locally: {relative}; edit the canonical source or move the custom file")
        updates[relative] = content
    deletions = []
    for relative, previous_hash in state["files"].items():
        if relative in files or any(relative.startswith(item + "/") for item in replacements):
            continue
        path = safe_path(root, relative)
        if path.exists():
            if not path.is_file() or digest(path.read_bytes()) != previous_hash:
                raise SyncError(f"Obsolete generated file changed locally: {relative}")
            deletions.append(relative)
    for relative, previous_target in state.get("links", {}).items():
        if relative in links:
            continue
        path = safe_path(root, relative, (relative,))
        if path.is_symlink():
            if os.readlink(path) != previous_target:
                raise SyncError(f"Obsolete generated link changed locally: {relative}")
            deletions.append(relative)
        elif path.exists():
            raise SyncError(f"Obsolete generated link replaced locally: {relative}")
    groups = {runtime: hook_groups(runtime) for runtime in CONFIGS}
    for runtime, relative in CONFIGS.items():
        path = safe_path(root, relative)
        previous = state["hooks"].get(runtime, {})
        if migrating and not path.exists():
            previous = {}
        elif migrating and not (root / OLD_LEDGER).exists():
            present = read_json(path).get("hooks", {})
            if not isinstance(present, dict):
                raise SyncError(f"Invalid hooks object: {path}")
            adopted = {}
            for event, entries in present.items():
                if not isinstance(entries, list):
                    raise SyncError(f"Invalid hook groups: {path}: {event}")
                known = previous.get(event, []) + groups[runtime].get(event, [])
                for entry in entries:
                    if entry in known:
                        adopted.setdefault(event, []).append(entry)
                    elif any(marker in json.dumps(entry) for marker in
                             (".codex/hooks/adapter.py", ".claude/hooks/pretooluse.sh")):
                        raise SyncError(f"Unrecognized existing workspace hook: {path}: {event}")
            previous = adopted
        content = merge_hooks(root, runtime, previous, groups[runtime])
        if not path.exists() or path.read_bytes() != content:
            updates[relative] = content
    if migrating and (root / OLD_LEDGER).exists():
        path = safe_path(root, OLD_LEDGER)
        if digest(path.read_bytes()) != state["old_ledger_hash"]:
            raise SyncError("Legacy generated-file ledger changed locally; cannot safely migrate")
        deletions.append(OLD_LEDGER)
    ledger = encoded({"version": 2, "generator": GENERATOR_ID,
                      "files": {key: digest(value) for key, value in sorted(files.items())},
                      "modes": dict(sorted(modes.items())),
                      "links": dict(sorted(links.items())),
                      "hooks": groups})
    if not (root / LEDGER).exists() or (root / LEDGER).read_bytes() != ledger:
        updates[LEDGER] = ledger
    return updates, deletions, replacements, modes, link_updates


def path_state(path):
    if path.is_symlink():
        return {"type": "link", "target": os.readlink(path)}
    if not path.exists():
        return None
    mode = path.stat().st_mode & 0o777
    if path.is_file():
        return {"type": "file", "hash": digest(path.read_bytes()), "mode": mode}
    if path.is_dir():
        return {"type": "directory", "mode": mode,
                "children": {child.name: path_state(child) for child in sorted(path.iterdir())}}
    raise SyncError(f"Unsupported transaction path: {path}")


def transaction_journal(root):
    directory = safe_path(root, TRANSACTION)
    if not directory.exists():
        return None
    if not directory.is_dir():
        raise SyncError("Runtime transaction path is not a directory")
    marker = directory / "journal.json"
    if marker.is_symlink():
        raise SyncError("Runtime transaction journal must not be a symlink")
    journal = read_json(marker)
    if journal.get("generator") != GENERATOR_ID or journal.get("version") != 1:
        raise SyncError("Unrecognized runtime transaction journal")
    operations = journal.get("operations")
    if not isinstance(operations, list):
        raise SyncError("Invalid runtime transaction operations")
    paths = []
    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != {"path", "before", "after"}:
            raise SyncError("Invalid runtime transaction operation")
        relative = operation["path"]
        path = safe_path(root, relative, (relative,))
        if Path(relative).parts[0] == TRANSACTION:
            raise SyncError("Transaction cannot manage its own recovery directory")
        if any(path == previous or path.is_relative_to(previous) or previous.is_relative_to(path)
               for previous in paths):
            raise SyncError("Overlapping runtime transaction paths")
        paths.append(path)
    for name in ("staged", "backup", "discard"):
        path = directory / name
        if path.is_symlink() or not path.is_dir():
            raise SyncError("Invalid runtime transaction storage")
    return directory, operations


def recover_transaction(root, check=False):
    transaction = transaction_journal(root)
    if transaction is None:
        return
    if check:
        raise SyncError("Pending runtime transaction; run sync without --check to recover")
    directory, operations = transaction
    committed = directory / "committed"
    if committed.is_symlink():
        raise SyncError("Invalid runtime transaction commit marker")
    if not committed.exists():
        # Backups are renamed originals, never a reconstruction from the ledger.
        # Replaying rollback is safe even if rollback itself was interrupted.
        for index in reversed(range(len(operations))):
            operation = operations[index]
            path = safe_path(root, operation["path"], (operation["path"],))
            backup = directory / "backup" / str(index)
            discard = directory / "discard" / str(index)
            saved = path_state(backup)
            current = path_state(path)
            if saved is not None:
                if saved != operation["before"]:
                    raise SyncError(f"Runtime recovery backup changed: {operation['path']}")
                if current is not None:
                    if current != operation["after"] or discard.exists() or discard.is_symlink():
                        raise SyncError(f"Runtime recovery collision: {operation['path']}")
                    path.replace(discard)
                path.parent.mkdir(parents=True, exist_ok=True)
                backup.replace(path)
            elif operation["before"] is None:
                if current is not None:
                    if current != operation["after"] or discard.exists() or discard.is_symlink():
                        raise SyncError(f"Runtime recovery collision: {operation['path']}")
                    path.replace(discard)
            elif current != operation["before"]:
                raise SyncError(f"Runtime recovery original missing: {operation['path']}")
    retire_transaction(directory)


def retire_transaction(directory):
    # Retire the recovery entry atomically before cleanup, whose own partial
    # failure must not leave a broken journal blocking the next invocation.
    retired = directory.with_name(".agent-runtime-complete-" + uuid.uuid4().hex)
    directory.replace(retired)
    try:
        shutil.rmtree(retired)
    except OSError as exc:
        print(f"Runtime transaction cleanup retained {retired.name}: {exc}", file=sys.stderr)


def apply_transaction(root, updates, deletions, modes, links):
    directory = root / TRANSACTION
    provisional = root / (".agent-runtime-stage-" + uuid.uuid4().hex)
    provisional.mkdir()
    prepared = False
    try:
        for name in ("staged", "backup", "discard"):
            (provisional / name).mkdir()
        (provisional / "journal.json").write_bytes(encoded(
            {"generator": GENERATOR_ID, "version": 1, "operations": []}))
        provisional.replace(directory)
        operations = []
        # Persisting the ledger last makes it describe only installed outputs.
        targets = sorted(set(updates) | set(deletions) | set(links), key=lambda name: (name == LEDGER, name))
        for index, relative in enumerate(targets):
            path = safe_path(root, relative, (relative,))
            before = path_state(path)
            staged = directory / "staged" / str(index)
            if relative in links:
                staged.symlink_to(links[relative], target_is_directory=True)
            elif relative in updates:
                staged.write_bytes(updates[relative])
                staged.chmod(modes.get(relative, before["mode"] if before and before["type"] == "file" else 0o644))
            operations.append({"path": relative, "before": before, "after": path_state(staged)})
        journal = {"generator": GENERATOR_ID, "version": 1, "operations": operations}
        next_journal = directory / "journal.next"
        next_journal.write_bytes(encoded(journal))
        next_journal.replace(directory / "journal.json")
        # Validate the recovery plan before the first existing path is moved.
        transaction_journal(root)
        prepared = True
        for index, operation in enumerate(operations):
            path = safe_path(root, operation["path"], (operation["path"],))
            if path_state(path) != operation["before"]:
                raise SyncError(f"Generated path changed during sync: {operation['path']}")
            if operation["before"] is not None:
                path.replace(directory / "backup" / str(index))
            if operation["after"] is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                (directory / "staged" / str(index)).replace(path)
        (directory / "committed").write_text("committed\n", encoding="utf-8")
    except Exception:
        if prepared:
            recover_transaction(root)
        elif provisional.exists():
            retire_transaction(provisional)
        else:
            retire_transaction(directory)
        raise
    recover_transaction(root)


def sync(root, check=False):
    root = root.resolve()
    recover_transaction(root, check)
    updates, deletions, replacements, modes, links = plan(root)
    changed = sorted(set(updates) | set(deletions) | set(replacements) | set(links))
    if check:
        if changed:
            raise SyncError("Generated runtime drift:\n" + "\n".join(changed))
        return []
    if changed:
        apply_transaction(root, updates, deletions, modes, links)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without changing files")
    args = parser.parse_args()
    try:
        changed = sync(ROOT, args.check)
    except (SyncError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Agent sync failed: {exc}", file=sys.stderr)
        return 1
    print(f"Agent adapters {'updated (' + str(len(changed)) + ' paths)' if changed else 'are current'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
