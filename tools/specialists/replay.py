#!/usr/bin/env python3
"""Replay independently authored reference tests on fresh bad/good local targets; no model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

from lab import Lab

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODES = {"api": "api-defect", "security": "security-defect", "web": "web-defect", "performance": "perf-defect"}


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def assess(surface, root, code, output, defective):
    if code != (1 if defective else 0):
        return False
    if surface == "api":
        cleanup = [json.loads(line) for line in (root / "artifacts/result/cleanup.jsonl").read_text().splitlines()]
        return (len(cleanup) == 34 and all(not row["problems"] for row in cleanup)
                and "Ran 34 tests" in output and
                (("FAILED (failures=1)" in output and "FAIL: test_job_completion_and_receipt" in output
                  and "receipt not found" in output) if defective else "\nOK\n" in output))
    if surface == "security":
        result = json.loads((root / "artifacts/result/evidence.json").read_text())
        failures = [c for c in result["checks"] if not c["passed"]]
        return (len(result["checks"]) == 86 and result["requests"] <= 100
                and len(failures) == (4 if defective else 0)
                and all("GET" in c["name"] and "orders" in c["name"] for c in failures)
                and all(c["passed"] for c in result["checks"] if "restored" in c["name"]))
    if surface == "performance":
        result = json.loads((root / "artifacts/result/measurement.json").read_text())
        summary = result["summary"]
        return (summary["count"] == 50 and summary["errors"] == 0
                and summary["stop_reason"] is None
                and (summary["p95_ms"] > 40 if defective else summary["p95_ms"] <= 40))
    folders = list((root / "artifacts").glob("parcel-*"))
    if len(folders) != 1:
        return False
    for browser in ("chromium", "firefox"):
        result = json.loads((folders[0] / f"{browser}.json").read_text())
        stats = result["stats"]
        if (stats["skipped"] or stats["flaky"] or result.get("errors")
                or stats["unexpected"] != (3 if defective else 0)
                or stats["expected"] != (0 if defective else 3)):
            return False
        if defective and "Receipt" not in json.dumps(result):
            return False
    return True


def run(surface, mode, out, node_modules):
    root = out / f"{surface}-{mode}"
    root.mkdir()
    shutil.copytree(HERE / "reference" / surface / "tests", root / "tests")
    before = hashes(root / "tests")
    (root / "artifacts").mkdir()
    (root / "tools/specialists").mkdir(parents=True)
    for name in ("CONTRACT.md", "measure.py"):
        shutil.copy2(HERE / name, root / "tools/specialists" / name)
    for name in ("qa-config.json", "workspace-manifest.json"):
        shutil.copy2(ROOT / name, root / name)
    if surface == "web":
        if not (node_modules / "@playwright/test/package.json").is_file():
            raise ValueError("Install reference/web dependencies and browser engines before --web")
        (root / "node_modules").symlink_to(node_modules, target_is_directory=True)
    server = Lab(mode)
    identity = root / "identity.json"
    identity.write_text(json.dumps(server.identity(), indent=2))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if surface == "api":
        env.update(QA_LAB_IDENTITY=str(identity), QA_ARTIFACT_DIR="artifacts/result")
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_api_parcel.py", "-v"]
    elif surface == "security":
        command = [sys.executable, "tests/test_security_parcel.py", "--identity", str(identity), "--out", "artifacts/result"]
    elif surface == "performance":
        command = [sys.executable, "tests/check_work.py", "--identity", str(identity), "--out-dir", "artifacts/result"]
    else:
        command = ["node", "tests/run-parcel.cjs", str(identity)]
    started = time.time()
    code, output, passed = None, "", False
    try:
        process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            # Browser workers share this task-owned process group; killing only
            # the CLI parent can otherwise leave them running after the ceiling.
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            output = stdout + stderr + "\nOuter 180-second deadline exceeded.\n"
            raise subprocess.TimeoutExpired(command, 180)
        code, output = process.returncode, stdout + stderr
        (root / "output.log").write_text(output)
        passed = assess(surface, root, code, output, mode != "good")
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        output += str(exc)
        (root / "output.log").write_text(output)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)
    with socket.socket() as probe:
        closed = probe.connect_ex(("127.0.0.1", server.server_port)) != 0
    after = hashes(root / "tests")
    record = {"surface": surface, "mode": mode, "identity": server.identity(), "command": command,
              "cwd": str(root), "exit": code, "elapsed_s": time.time() - started,
              "tests_before": before, "tests_after": after, "unchanged": before == after,
              "cleanup": {"port_closed": closed, "thread_stopped": not thread.is_alive()},
              "verified_expected_outcome": passed and before == after and closed and not thread.is_alive(),
              "kind": "deterministic replay of agent-authored tests; not a fresh model evaluation"}
    (root / "run.json").write_text(json.dumps(record, indent=2))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new artifact directory; retained for review")
    parser.add_argument("--web", action="store_true", help="also execute Chromium and Firefox")
    parser.add_argument("--node-modules", type=Path, default=HERE / "reference/web/node_modules")
    args = parser.parse_args()
    if args.web and not (args.node_modules / "@playwright/test/package.json").is_file():
        parser.error("Install reference/web dependencies and browser engines before --web")
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=False)
    results = []
    for surface in ("api", "security", "performance", *(("web",) if args.web else ())):
        for mode in (MODES[surface], "good"):
            result = run(surface, mode, out, args.node_modules.resolve())
            results.append(result)
            print(f"{surface} {mode}: exit={result['exit']} expected-outcome={result['verified_expected_outcome']}", flush=True)
    (out / "replay.json").write_text(json.dumps(results, indent=2))
    return 0 if all(r["verified_expected_outcome"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
