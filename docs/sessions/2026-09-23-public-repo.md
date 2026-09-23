# 2026-09-23 — public repo page

The GitHub page is how someone finds the free agent. The agent layer itself was not changed.

## Files

README header and lede, `docs/brand/header.png`, `docs/brand/mark.svg`, contributing, security, code of conduct, issue forms, this spec's criteria in `docs/specs/2026-09-23-public-repo.md`.

## GitHub settings

Live on the repository, not in git:

- Description names the QA agent, Cursor, and Claude Code. Homepage `https://qadrillion.com/repo`. Template repository. Branches deleted on merge.
- Topics: `qa`, `quality-assurance`, `software-testing`, `test-automation`, `qa-automation`, `ai-agents`, `claude-code`, `cursor`, `agent-skills`, `qa-tools`.
- Secret scanning and push protection on. Private vulnerability reporting on.
- Ruleset `23899087` (`main`): block deletion, block force-push, require a pull request, require the `governance` check. Zero approving reviews. No bypass actor.

## Not in this change

- Social preview image. GitHub has no API for it. The file to upload under Settings → General → Social preview is `docs/brand/header.png`.
- No release tag. That waits until a later chat reviews the skills and subagents.
- Pull request #1 (`fix/codex-cursor-parity`) also edits `docs/STATE.md`. Merging both needs a resolution of that file.

## Checks

`./.cursor/hooks/tests/run-tests.sh` → `passed: 71  failed: 0`.
