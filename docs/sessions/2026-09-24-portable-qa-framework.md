# Portable QA framework — checkpoint 2026-09-24

Scope: tooling. User requested an in-depth audit, QA-practice research and an
implementation improving portability, token efficiency, team handoff and all
skills/agents. Cursor was selected for the first work-laptop pilot.

Branch: `feat/portable-qa-framework`; committed checkpoint `78886db`.
Working tree also contains the authorized skill/rule/agent rewrites, regenerated
copies, config/doctor/verifier, examples, sample ticket and documentation changes.
No unrelated starting changes existed. Do not discard the current working tree.

## Implemented

- Repository refresh validates real Git roots, expected remotes and mutability;
  explicitly fetches the canonical ref and rechecks state before merging.
- Ticket parsing rejects ambiguous/malformed state, supports tracker-free tasks,
  more scopes and relative evidence; index validates and escapes content.
- Hook event parsing fails closed; unknown MCP effects ask; known CLI writes are
  checked; file-read JSON/path handling and session checkpoints are hardened.
- Runtime generation is repository-owned, preserves custom settings and native
  read-only roles, materializes skills without symlink requirements, detects drift
  and fixes nested-root/UTF-8 handling. No native trust was changed automatically.
- Skills/agents use capabilities, risk-directed techniques, independent oracles,
  observed locators, honest black-box limits, retained failures and explicit handoff.
- Added setup declarations/doctor, on-demand surface guidance, deterministic CI
  entry point, ten behavioral scenarios and a current audit/acceptance spec.

## Verification with output

Expanded Python suite:

```text
Ran 97 tests in 12.553s
OK
```

The final policy run initially caught a newly introduced quoting bug in an inline
Python comment. The comment was corrected; affected checks were executed again:

```text
passed: 71   failed: 0
TOTAL passed=12 failed=0
```

The 12 checks are malformed-event probes of three guards, not yet durable new
hook fixtures. Logs retained at `/tmp/qadrillion-latest-verify.log` (including the
failure) and `/tmp/qadrillion-read-guard-fixed.log` (fix validation). Python tests
were unchanged by this comment correction and were not rerun unnecessarily.

Ticket schema: 1 checked, 0 violations. Index current. Adapter drift check current.
Diff check clean. Ten fresh-agent synthetic scenarios passed; detailed observations
and limits are in `2026-09-24-golden-tasks.md`.

Always-loaded project prose: 850 → 634 words; 5,935 → 4,712 characters. These are
not model token or billing measurements. A standalone skill-authoring validator
could not run because its interpreter lacks PyYAML; committed metadata/drift
checks ran without that optional external dependency.

## Source review and disposition

Focused independent review found locale-dependent reads, incorrect nested-root
launcher discovery, post-fetch state changes and absolute artifact references.
All four received fixes and regressions. Checkpoint tests additionally exposed
untracked-edit detection, repeated prompts and malformed lifecycle-event issues.
The final blind acceptance review has not run: required documentation checks
remain blocked, so its prerequisite verification is not green.

## Blocker and exact next action

The active PreToolUse hook rejected a shell-based documentation write because
command examples were recognized as destructive commands; it separately rejected
writing simulated credential-read regression payloads. No such operations were
executed. The denied writes were not retried through another tool.

A user question is pending: permission to write those prepared documentation and
test-data examples through the file-edit tool, without executing the examples or
changing the active hook configuration. Resolve that request before those writes.

Pending files: `docs/reference/integrations.md`, `team-workflow.md`,
`runtime-support.md`; updates to `docs/adopting.md` and `.cursor/README.md`;
`docs/research/qa-practices.md` and `runtime-portability.md`; durable additional
hook regression payloads in `tools/tests/test_hooks.py` / the hook test runner.
Research source notes already exist at `/tmp/qadrillion-qa-research.md` and
`/tmp/qadrillion-portability-research.md`; they contain inspected sources and limits.

After resolving: finish those files, regenerate adapters if canonical inputs
change, run full verification and clean-export checks, perform the blind build
review against the spec, record its content fingerprint, then prepare the reviewed
branch for publication. Do not represent the current overall verification as Pass:
five broken documentation links and three required missing guides remain.

Tracker update: none applicable; no external post, push, PR or release performed.
Native runtime trust/discovery, Windows operation, company tools/product/device,
actual token savings and the work-laptop pilot remain unverified.

Verdict: **Partial — code tests pass; documentation/fixture gate and final review pending.**
