#!/usr/bin/env python3
"""Materialize isolated specialist tasks and preserve separately reviewed run evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name("scenarios.json")
SKILLS = ("qa", "qa-workflow", "qa-api", "qa-web", "qa-mobile", "qa-security", "qa-performance")
FILES = ("AGENTS.md", "qa-config.json", "workspace-manifest.json", "docs/decisions/INDEX.md",
         "docs/reference/known-quirks.md", "docs/reference/integrations.md",
         "docs/reference/surfaces.md", "docs/reference/testing-strategy.md",
         "docs/reference/focused-checks.md")
TREES = (".cursor/rules", ".cursor/agents", "tools/workspace", "tools/tickets")
VERDICTS = ("Pass", "Fail", "Blocked", "Not-run")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def scenarios(catalog=CATALOG):
    data = read_json(catalog)
    if data.get("schema_version") != 1 or not isinstance(data.get("scenarios"), list):
        raise ValueError("invalid scenario catalog")
    entries = {}
    for entry in data["scenarios"]:
        if (not isinstance(entry, dict) or not isinstance(entry.get("id"), str)
                or not entry["id"] or entry["id"] in entries
                or not isinstance(entry.get("task"), str) or not entry["task"].strip()
                or not isinstance(entry.get("expect"), dict)):
            raise ValueError("invalid or duplicate scenario")
        entries[entry["id"]] = entry
    return entries


def regular_file(path):
    path = Path(path).absolute()
    if path.is_symlink():
        raise ValueError(f"symlink input is not an isolated file: {path}")
    if not path.is_file():
        raise ValueError(f"required file missing: {path}")
    return path.resolve()


def input_files(source):
    files = {Path(name) for name in FILES}
    trees = [*TREES, *(f".cursor/skills/{name}" for name in SKILLS)]
    for name in SKILLS:
        regular_file(source / f".cursor/skills/{name}/SKILL.md")
    for name in trees:
        directory = source / name
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError(f"required directory missing or symlinked: {directory}")
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"symlink input is not isolated: {path}")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files.add(path.relative_to(source))
    return [(regular_file(source / relative), relative) for relative in sorted(files)]


def materialize(source, scenario_id, out, *, contexts=(), revision=None, catalog=CATALOG):
    source = Path(source).resolve()
    entry = scenarios(catalog).get(scenario_id)
    if entry is None:
        raise ValueError(f"unknown scenario: {scenario_id}")
    inputs = input_files(source)
    inputs.append((regular_file(source / "tools/specialists/CONTRACT.md"), Path("fixtures/CONTRACT.md")))
    for context in contexts:
        path = regular_file(context)
        inputs.append((path, Path("fixtures") / path.name))
    destinations = [relative for _, relative in inputs]
    if len(set(destinations)) != len(destinations):
        raise ValueError("duplicate fixture destination")
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise ValueError("evaluation destination must be new")
    out.parent.mkdir(parents=True, exist_ok=True)
    out = out.parent.resolve() / out.name
    out.mkdir()
    worker = out / "workspace"
    worker.mkdir()
    manifest = {}
    for original, relative in inputs:
        destination = worker / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)
        manifest[relative.as_posix()] = digest(destination)
    state = worker / "docs/STATE.md"
    state.write_text("# Isolated QA evaluation\n\nTask: TASK.md. Owner: fresh runtime session.\n"
                     "No previous session evidence. Use supplied fixtures only.\n", encoding="utf-8")
    (worker / "TASK.md").write_text(entry["task"] + "\n", encoding="utf-8")
    manifest["docs/STATE.md"] = digest(state)
    manifest["TASK.md"] = digest(worker / "TASK.md")
    run = {"schema_version": 1, "run_id": str(uuid.uuid4()), "created_at": now(),
           "scenario": scenario_id, "source_revision": revision,
           "catalog_sha256": digest(catalog), "worker_root": "workspace",
           "manifest": manifest, "expect": entry["expect"],
           "status": "Not-run", "actual_tokens": None}
    write_json(out / "evaluation.json", run)
    return run


def validate_review(review):
    if not isinstance(review, dict) or review.get("verdict") not in VERDICTS:
        raise ValueError("review must supply a recognized verdict")
    for name in ("reviewer", "runtime", "model", "runtime_run_id"):
        if not isinstance(review.get(name), str) or not review[name].strip():
            raise ValueError(f"review requires {name}")
    for name in ("observations", "findings"):
        values = review.get(name)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"review requires a list of {name}")
    if review["verdict"] != "Not-run" and not review["observations"]:
        raise ValueError("executed review requires evidence observations")
    if review["verdict"] in ("Fail", "Blocked") and not review["findings"]:
        raise ValueError("failed or blocked review requires findings")
    tokens = review.get("actual_tokens")
    if tokens is not None and (type(tokens) is not int or tokens < 0):
        raise ValueError("actual_tokens must be a nonnegative runtime count or null")
    if tokens is not None and (not isinstance(review.get("token_source"), str) or not review["token_source"].strip()):
        raise ValueError("actual token count requires a runtime evidence source")
    if review["verdict"] == "Not-run" and tokens is not None:
        raise ValueError("an unexecuted scenario cannot have actual token usage")


def record(run_dir, review, *, transcript=None, artifacts=()):
    run_dir = Path(run_dir).resolve()
    run = read_json(regular_file(run_dir / "evaluation.json"))
    validate_review(review)
    files = []
    if transcript is not None:
        transcript = regular_file(transcript)
        lines = transcript.read_text(encoding="utf-8").splitlines()
        if not lines or any(not isinstance(json.loads(line), dict) for line in lines):
            raise ValueError("transcript must be nonempty JSONL objects from the runtime")
        files.append((transcript, "transcript.jsonl"))
    elif review["verdict"] != "Not-run":
        raise ValueError("executed verdict requires the actual runtime transcript")
    for index, path in enumerate(artifacts):
        original = regular_file(path)
        files.append((original, f"artifact-{index}-{original.name}"))
    attempts = run_dir / "records"
    if attempts.is_symlink():
        raise ValueError("records directory must not be a symlink")
    attempts.mkdir(exist_ok=True)
    attempt_id = str(uuid.uuid4())
    destination = attempts / attempt_id
    destination.mkdir()
    evidence = {}
    for original, name in files:
        shutil.copy2(original, destination / name)
        evidence[name] = {"sha256": digest(destination / name), "bytes": (destination / name).stat().st_size}
    result = {"schema_version": 1, "run_id": run["run_id"], "scenario": run["scenario"],
              "attempt_id": attempt_id, "recorded_at": now(),
              "evaluation_sha256": digest(run_dir / "evaluation.json"),
              "review": {**review, "actual_tokens": review.get("actual_tokens")}, "evidence": evidence,
              "claim": "Recorded runtime evidence plus reviewer judgment; not automatic behavioral grading or native-runtime certification."}
    write_json(destination / "record.json", result)
    return destination / "record.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list task IDs without the evaluator answer key")
    make = sub.add_parser("materialize", help="prepare a fresh worker directory; never launches a runtime")
    make.add_argument("--source", type=Path, default=ROOT)
    make.add_argument("--scenario", required=True)
    make.add_argument("--out", type=Path, required=True)
    make.add_argument("--revision", help="source commit if known; copied file hashes are always retained")
    make.add_argument("--context", type=Path, action="append", default=[])
    save = sub.add_parser("record", help="retain actual JSONL, artifacts and an independent review")
    save.add_argument("--run", type=Path, required=True)
    save.add_argument("--review", type=Path, required=True)
    save.add_argument("--transcript", type=Path)
    save.add_argument("--artifact", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        if args.command == "list":
            print("\n".join(scenarios()))
        elif args.command == "materialize":
            run = materialize(args.source, args.scenario, args.out, contexts=args.context, revision=args.revision)
            print(json.dumps({"run_id": run["run_id"], "worker": str(args.out / "workspace"), "status": "Not-run"}))
        else:
            print(record(args.run, read_json(args.review), transcript=args.transcript, artifacts=args.artifact))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Evaluation blocked: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
