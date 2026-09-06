# ADR-0002 — A failure is a finding: no automatic re-run
Status: accepted (2026-09-06)

## Context
Re-run plugins turn a red suite green by hiding the failures that were
intermittent. An agent under pressure to "finish" does the same by hand:
re-run until it passes, then report Pass. Both destroy the signal QA exists
to produce.

## Options
1. Auto-rerun plugin with a retry count — rejected: hides intermittency, the most expensive defect class.
2. Let the agent decide when to re-run — rejected: the agent's incentive is green.
3. **Exactly one re-run, then the result is a finding** — chosen.

## Decision
A failing test is re-run at most once. A second failure is reported as-is
with both outputs. No retry plugin is installed. An assertion failure is
never something to "make pass". The same budget logic applies to MCP calls
(two retries, then fall back and lower confidence) and to source reading
(~10 files, then ask).

## Consequences
More red reports, each one true. Flakiness becomes visible and gets fixed at
the cause (a wait, a fixture, an environment) rather than masked.

## Revisit triggers
None expected. A suite that "needs" retries has a fixture problem.
