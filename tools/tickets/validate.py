#!/usr/bin/env python3
"""Validate portable ticket state without third-party dependencies.

The supported YAML subset is one flat mapping with plain, JSON double-quoted
or YAML single-quoted scalars; null, booleans, numbers; and scalar lists written
inline or as indented dash items. Comments are supported. Nested mappings,
anchors, tags, block scalars and duplicate keys are rejected, never approximated.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
TICKETS = ROOT / "tickets"
REQUIRED = {
    "id", "title", "scope", "status", "verdict", "build", "environment", "tracker",
    "design", "source_refs", "started", "updated", "next_action", "blockers",
}
SCOPES = {"api", "ui-web", "mobile", "backend", "multi-surface", "tooling", "desktop", "data", "device", "other"}
STATUSES = {"analyzing", "analyzed", "planned", "in_test", "blocked", "reporting", "done"}
VERDICTS = {None, "pass", "partial", "fail"}
ENV_ROLES = {"dev", "test", "staging", "production", "unknown"}
VAGUE = re.compile(r"^(continue|carry on|keep going|tbd|todo|next|proceed)\b", re.I)


class FrontmatterError(ValueError):
    pass


def scalar(value: str):
    value = value.strip()
    if value.startswith('"'):
        try:
            result, end = json.JSONDecoder().raw_decode(value)
        except ValueError as exc:
            raise FrontmatterError("invalid double-quoted scalar") from exc
        if value[end:].strip() and not value[end:].lstrip().startswith("#"):
            raise FrontmatterError("unexpected text after quoted scalar")
        return result
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
        if not match:
            raise FrontmatterError("invalid single-quoted scalar")
        return match[1].replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not value or value.startswith("#") or value in {"null", "Null", "NULL", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)
    if re.fullmatch(r"[+-]?\d+\.\d+(?:[eE][+-]?\d+)?", value):
        return float(value)
    if value[0] in "[]{}&*!|>@`" or ": " in value or value.startswith("- "):
        raise FrontmatterError("unsupported YAML syntax; quote this scalar")
    return value


def inline_list(value: str) -> list:
    items, start, quote, index = [], 1, None, 1
    while index < len(value):
        char = value[index]
        if quote:
            if char == "\\" and quote == '"':
                index += 2
                continue
            if char == quote:
                if quote == "'" and index + 1 < len(value) and value[index + 1] == "'":
                    index += 2
                    continue
                quote = None
        elif char in "\"'" and not value[start:index].strip():
            quote = char
        elif char == "[" or char == "{":
            raise FrontmatterError("nested lists and mappings are unsupported")
        elif char in ",]":
            item = value[start:index].strip()
            if item:
                items.append(scalar(item))
            elif char == ",":
                raise FrontmatterError("empty list item")
            if char == "]":
                remainder = value[index + 1:].strip()
                if remainder and not remainder.startswith("#"):
                    raise FrontmatterError("unexpected text after list")
                return items
            start = index + 1
        index += 1
    raise FrontmatterError("unterminated list")


def parse_ticket(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError("no frontmatter block")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise FrontmatterError("missing exact frontmatter closing delimiter") from exc
    data, pending, indentation = {}, None, None
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            match = re.fullmatch(r" +-[ ]+(.*)| +-[ ]*", line)
            if not match or pending is None or "\t" in line[:len(line) - len(line.lstrip())]:
                raise FrontmatterError(f"line {number}: only indented list items are supported")
            width = len(line) - len(line.lstrip())
            if indentation is not None and width != indentation:
                raise FrontmatterError(f"line {number}: inconsistent list indentation")
            indentation = width
            if data[pending] is None:
                data[pending] = []
            data[pending].append(scalar(match[1] or ""))
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:[ ]+(.*)|[ ]*)", line)
        if not match:
            raise FrontmatterError(f"line {number}: invalid mapping entry")
        key, value = match[1], (match[2] or "").strip()
        if key in data:
            raise FrontmatterError(f"line {number}: duplicate key `{key}`")
        pending = key if not value or value.startswith("#") else None
        indentation = None
        data[key] = inline_list(value) if value.startswith("[") else scalar(value)
    return data, "\n".join(lines[end + 1:])


def frontmatter(text: str) -> dict | None:
    try:
        return parse_ticket(text)[0]
    except FrontmatterError:
        return None


def is_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value) -> bool:
    return isinstance(value, list) and all(is_text(item) for item in value)


def execution_evidence(path: Path, data: dict, body: str) -> bool:
    refs = data.get("evidence", [])
    if string_list(refs):
        for reference in refs:
            artifact = (path.parent / reference).resolve()
            try:
                if artifact.is_file() and artifact.stat().st_size > 0:
                    return True
            except OSError:
                continue
    section = re.search(r"^##\s+Execution\s*(?:&|and)\s*results\s*\n(.*?)(?=^##\s|\Z)", body, re.I | re.M | re.S)
    if not section:
        return False
    blocks = re.findall(r"^(`{3,}|~{3,})[^\n]*\n(.*?)^\1\s*$", section[1], re.M | re.S)
    return any(len(content.strip().splitlines()) >= 2 and not re.search(r"\b(TODO|TBD|placeholder)\b", content, re.I) for _, content in blocks)


def validate_data(path: Path, data: dict, body: str) -> list[str]:
    errors = [f"missing key `{key}`" for key in sorted(REQUIRED - data.keys())]
    if errors:
        return errors
    for key in ("id", "title", "next_action"):
        if not is_text(data[key]):
            errors.append(f"`{key}` must be a nonempty string")
    if data["id"] != path.stem:
        errors.append(f"id `{data['id']}` != filename `{path.stem}`")
    for key, allowed in (("scope", SCOPES), ("status", STATUSES), ("verdict", VERDICTS)):
        if not isinstance(data[key], (str, type(None))) or data[key] not in allowed:
            errors.append(f"invalid `{key}`: {data[key]!r}")
    for key in ("build", "environment", "design", "owner", "branch"):
        if data.get(key) is not None and not is_text(data[key]):
            errors.append(f"`{key}` must be a nonempty string or null")
    if "env_role" in data and (not isinstance(data["env_role"], str) or data["env_role"] not in ENV_ROLES):
        errors.append("`env_role` must be dev, test, staging, production or unknown")
    for key in ("source_refs", "blockers", "evidence"):
        if key in data and not string_list(data[key]):
            errors.append(f"`{key}` must be a list of nonempty strings")
    if data["status"] == "done" and data["verdict"] is None:
        errors.append("status done but verdict null")
    if data["verdict"] is not None and data["status"] != "done":
        errors.append(f"verdict set but status is `{data['status']}`")
    if data["status"] == "blocked" and not data["blockers"]:
        errors.append("blocked without a reason in `blockers`")
    dates = {}
    for key in ("started", "updated"):
        try:
            if not isinstance(data[key], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data[key]):
                raise ValueError()
            dates[key] = date.fromisoformat(data[key])
        except ValueError:
            errors.append(f"`{key}` is not an ISO date: {data[key]!r}")
    if len(dates) == 2 and dates["updated"] < dates["started"]:
        errors.append("`updated` must not precede `started`")
    action = data["next_action"]
    if isinstance(action, str) and (len(action.strip()) < 12 or VAGUE.match(action.strip())):
        errors.append(f"next_action too vague: {action!r}")
    tracker = data["tracker"]
    if tracker is not None:
        parsed = urlparse(tracker) if isinstance(tracker, str) else None
        if parsed is None or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("tracker must be an http(s) URL or null")
    if data["status"] == "done" and data["verdict"] == "pass" and not execution_evidence(path, data, body):
        errors.append("verdict pass requires execution output under `## Execution & results` or a nonempty local evidence artifact")
    return errors


def load_ticket(path: Path) -> dict:
    data, body = parse_ticket(path.read_text(encoding="utf-8"))
    errors = validate_data(path, data, body)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def check(path: Path) -> list[str]:
    try:
        load_ticket(path)
        return []
    except (OSError, ValueError) as exc:
        return [f"{path}: {exc}"]


def ticket_files(directory: Path = TICKETS) -> list[Path]:
    return sorted(path for path in directory.glob("*.md") if not path.name.startswith("_") and path.name != "INDEX.md")


def main(argv: list[str]) -> int:
    files = [Path(argument) for argument in argv] or ticket_files()
    errors = [error for path in files for error in check(path)]
    for error in errors:
        print(error)
    print(f"{len(files)} ticket(s) checked, {len(errors)} violation(s)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
