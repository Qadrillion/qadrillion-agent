#!/usr/bin/env python3
"""Run the same offline framework checks locally and in CI."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def instructions() -> bool:
    errors = []
    scripts = [*(ROOT / ".cursor/hooks").glob("*.sh"),
               ROOT / ".cursor/hooks/tests/run-tests.sh",
               *(ROOT / ".claude/hooks").glob("*.sh"),
               ROOT / "tools/workspace/refresh.sh"]
    for script in scripts:
        if not script.is_file() or not script.stat().st_mode & 0o111:
            errors.append(f"hook/entry script is not executable: {script.relative_to(ROOT)}")
    core_words = 0
    for path in (ROOT / ".cursor/rules").glob("*.mdc"):
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3:
            errors.append(f"invalid rule frontmatter: {path.name}")
            continue
        if re.search(r"^alwaysApply: true$", parts[1], re.M):
            if path.name != "core.mdc":
                errors.append(f"unexpected always-on rule: {path.name}")
            core_words = len(parts[2].split())
            if not 0 < core_words <= 120:
                errors.append(f"core word budget violated: {core_words}")
        if "@docs/STATE.md" in text:
            errors.append("STATE must not be imported on every turn")
    if not core_words:
        errors.append("core.mdc must be the always-on rule")
    identity = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if "@docs/STATE.md" in identity:
        errors.append("AGENTS must not import STATE on every turn")
    words = len(identity.split()) + core_words
    if words > 1000:
        errors.append(f"always-loaded project prose exceeds 1000 words: {words}")
    print(f"Project prompt proxy: {words} words; AGENTS {len(identity)} chars; core {core_words} words. Not token usage.", flush=True)
    for path in sorted((ROOT / ".cursor/skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        print(f"On-demand {path.parent.name}: {len(text.split())} words / {len(text)} chars", flush=True)
        parts = text.split("---", 2)
        if len(parts) != 3 or not re.search(r"^name: " + re.escape(path.parent.name) + "$", parts[1], re.M) or not re.search(r"^description: .+", parts[1], re.M):
            errors.append(f"invalid skill metadata: {path}")
    for error in errors:
        print("ERROR:", error, flush=True)
    return not errors


def document_links() -> bool:
    errors = []
    paths = [ROOT / "README.md", ROOT / "docs/adopting.md", ROOT / ".cursor/README.md",
             *(ROOT / "docs/reference").glob("*.md"),
             *(ROOT / ".cursor/skills").rglob("*.md")]
    for path in paths:
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = raw.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / unquote(target)).exists():
                errors.append(f"{path.relative_to(ROOT)}: missing linked file {target}")
    for error in errors:
        print("ERROR:", error, flush=True)
    return not errors


def main() -> int:
    if sys.version_info < (3, 11):
        print("Python 3.11+ required")
        return 1
    passed = instructions()
    passed = document_links() and passed
    commands = [
        ["bash", ".cursor/hooks/tests/run-tests.sh"],
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tools/tests", "-p", "test_*.py", "-v"],
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tools/specialists/mobile", "-p", "test_*.py", "-v"],
        [sys.executable, "tools/tickets/validate.py"],
        [sys.executable, "tools/tickets/index.py", "--check"],
        [sys.executable, "tools/agents/sync.py", "--check"],
        [sys.executable, "tools/workspace/doctor.py"],
    ]
    for command in commands:
        print("\nRUN " + " ".join(command), flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=180)
            passed = (result.returncode == 0) and passed
        except (OSError, subprocess.TimeoutExpired) as exc:
            print("ERROR:", exc, flush=True)
            passed = False
    print("\nOffline verification: " + ("PASS" if passed else "FAIL"), flush=True)
    print("Live runtime trust, connected tools and model behavioral evaluations are separate checks.", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
