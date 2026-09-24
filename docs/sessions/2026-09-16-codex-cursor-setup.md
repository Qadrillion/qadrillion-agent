# Cursor / Codex setup — 2026-09-16

Generated Codex skills, agents, rule bridge, hooks and public MCP registrations
from maintained Cursor sources. Shared source policy remains in .cursor.
Project policy payload checks pass; runtime configuration/discovery succeeds.
Native hook trust, runtime login and observed enforcement remain user steps.
No product code or account identity changed. No product build/release performed.

Setup branch: `fix/codex-cursor-parity`; base: `a1822b1568c0c6d376e3b41179a3dbeab943cd33`.
The original checkout and unrelated edits were preserved.

## Implementation record — 2026-09-16
Branch: fix/codex-cursor-parity · Commits: a1822b1568c0c6d376e3b41179a3dbeab943cd33..fix/codex-cursor-parity
Review-base: a1822b1568c0c6d376e3b41179a3dbeab943cd33
Review-fingerprint: 069d193c12722b1495ff9f1909dc24cc2ea010807a63176c4b32a34fd906123f
Verified: Shared hook suites: 30 Python tests + 56 shell + 23 read + 17 adapter + 13 reminder cases; 27 project payload/lifecycle checks; generator drift check; native runtime discovery; PASS.
Review: round 1 BLOCKED; round 2 BLOCKED; round 3 PASS
Deferred: 0
Not verified (reviewer, applicable excerpt): Native trust, live extension enforcement, OAuth and worktree discovery remain unverified.

No product feature was implemented. New hook trust and runtime authentication
remain native user steps. Review before integrating this setup branch.
