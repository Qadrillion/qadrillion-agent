"""Validate declarative QA capabilities without executing commands or reading auth."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath, PureWindowsPath

SCOPES = {"api", "ui-web", "mobile", "backend", "desktop", "data", "device",
          "other", "multi-surface", "tooling"}


def relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return False
    posix, windows = PurePosixPath(value), PureWindowsPath(value)
    return not (posix.is_absolute() or windows.is_absolute() or windows.drive
                or ".." in posix.parts or ".." in windows.parts or value.startswith("~"))


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError("configuration must be an object")
    return value


def validate(data: dict) -> list[str]:
    errors = []

    def error(where, message):
        errors.append(f"{where}: {message}")

    def string(value):
        return isinstance(value, str) and bool(value.strip()) and "\x00" not in value

    def strings(value):
        return isinstance(value, list) and all(string(v) for v in value)

    def scopes(value, where):
        if not strings(value) or any(v not in SCOPES for v in value):
            error(where, "expected a list of supported scopes (use other for an unlisted product)")

    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        error("schema_version", "expected integer 1")
    project = data.get("project")
    if not isinstance(project, dict) or not string(project.get("name")):
        error("project", "name is required")
    else:
        scopes(project.get("scopes"), "project.scopes")
    policy = data.get("policy")
    if not isinstance(policy, dict) or policy.get("production_execution") is not False:
        error("policy.production_execution", "must be false; this framework excludes production execution")
    if not isinstance(policy, dict) or policy.get("external_writes") != "task-authorization":
        error("policy.external_writes", "must be task-authorization")
    context = data.get("context")
    if not isinstance(context, dict):
        error("context", "object required")
    else:
        for key in ("max_result_chars", "max_search_results"):
            if type(context.get(key)) is not int or context[key] <= 0:
                error(f"context.{key}", "positive integer required")
    for group in ("integrations", "environments", "runners"):
        rows = data.get(group)
        if not isinstance(rows, list):
            error(group, "list required")
            continue
        ids = set()
        for i, row in enumerate(rows):
            where = f"{group}[{i}]"
            if not isinstance(row, dict):
                error(where, "object required")
                continue
            ident = row.get("id")
            if not string(ident) or ident in ids:
                error(where, "unique nonempty id required")
            else:
                ids.add(ident)
            if group != "environments" and type(row.get("enabled")) is not bool:
                error(where, "enabled must be true or false")
            if group == "integrations":
                if not string(row.get("provider")) or not string(row.get("scope")):
                    error(where, "provider and tenant/project scope required")
                if not isinstance(row.get("transport"), str) or row["transport"] not in {"cli", "api", "mcp", "manual"}:
                    error(where, "transport must be cli, api, mcp or manual")
                if not strings(row.get("capabilities")) or not row.get("capabilities"):
                    error(where, "nonempty capability list required")
                if row.get("transport") == "cli" and not string(row.get("executable")):
                    error(where, "CLI executable required")
            elif group == "environments":
                if not isinstance(row.get("role"), str) or row["role"] not in {"dev", "test", "staging", "production", "unknown"}:
                    error(where, "role must be dev, test, staging, production or unknown")
                if not string(row.get("identity_evidence")):
                    error(where, "identity_evidence requirement must be described")
            else:
                scopes(row.get("scopes"), where + ".scopes")
                if not row.get("scopes"):
                    error(where, "runner must declare at least one scope")
                if not strings(row.get("argv")) or not row.get("argv"):
                    error(where, "argv must be a nonempty list of strings, never a shell string")
                for key in ("cwd", "artifacts"):
                    if not relative_path(row.get(key)):
                        error(where + "." + key, "workspace-relative path without parent traversal required")
    return errors
