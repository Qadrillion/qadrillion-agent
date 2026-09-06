#!/usr/bin/env python3
"""Validate ticket frontmatter against the schema in .cursor/rules/ticket-state.mdc.

    python3 tools/tickets/validate.py                 # every tickets/*.md (template excluded)
    python3 tools/tickets/validate.py tickets/X-1.md  # one file

Exit 1 on any violation. No YAML dependency: the frontmatter is flat enough
to parse by hand, and a dependency-free checker runs anywhere, including a
hook.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TICKETS = ROOT / "tickets"
REQUIRED = [
    "id", "title", "scope", "status", "verdict", "build", "environment", "tracker",
    "design", "source_refs", "started", "updated", "next_action", "blockers",
]
SCOPES = {"api", "ui-web", "mobile", "backend", "multi-surface", "tooling"}
STATUSES = {"analyzing", "analyzed", "planned", "in_test", "blocked", "reporting", "done"}
VERDICTS = {"null", "pass", "partial", "fail"}
ENVS = {"dev", "staging", "prod", "null"}
VAGUE = re.compile(r"^(continue|carry on|keep going|tbd|todo|next|proceed)\b", re.I)


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    out: dict[str, str] = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and key:
            out[key] = (out[key] + "\n" + line.strip()).strip()
            continue
        if ":" not in line:
            return None
        key, _, value = line.partition(":")
        key = key.strip()
        out[key] = value.strip()
    return out


def check(path: Path) -> list[str]:
    errors: list[str] = []
    fm = frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{path}: no frontmatter block"]
    for k in REQUIRED:
        if k not in fm:
            errors.append(f"{path}: missing key `{k}`")
    if errors:
        return errors
    stem = path.stem
    if fm["id"] != stem:
        errors.append(f"{path}: id `{fm['id']}` != filename `{stem}`")
    if fm["scope"] not in SCOPES:
        errors.append(f"{path}: scope `{fm['scope']}` not in {sorted(SCOPES)}")
    if fm["status"] not in STATUSES:
        errors.append(f"{path}: status `{fm['status']}` not in {sorted(STATUSES)}")
    if fm["verdict"] not in VERDICTS:
        errors.append(f"{path}: verdict `{fm['verdict']}` not in {sorted(VERDICTS)}")
    if fm["environment"] not in ENVS:
        errors.append(f"{path}: environment `{fm['environment']}` not in {sorted(ENVS)}")
    if fm["status"] == "done" and fm["verdict"] == "null":
        errors.append(f"{path}: status done but verdict null")
    if fm["verdict"] != "null" and fm["status"] != "done":
        errors.append(f"{path}: verdict set but status is `{fm['status']}`")
    if fm["status"] == "blocked" and fm["blockers"] in ("[]", ""):
        errors.append(f"{path}: blocked without a reason in `blockers`")
    for k in ("started", "updated"):
        try:
            date.fromisoformat(fm[k])
        except ValueError:
            errors.append(f"{path}: `{k}` is not an ISO date: {fm[k]!r}")
    na = fm["next_action"].strip('"')
    if len(na) < 12 or VAGUE.match(na):
        errors.append(f"{path}: next_action too vague: {na!r}")
    if not fm["tracker"].startswith(("http://", "https://")):
        errors.append(f"{path}: tracker is not a URL")
    return errors


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or sorted(
        p for p in TICKETS.glob("*.md") if not p.name.startswith("_") and p.name != "INDEX.md"
    )
    all_errors = [e for f in files for e in check(f)]
    for e in all_errors:
        print(e)
    print(f"{len(files)} ticket(s) checked, {len(all_errors)} violation(s)")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
