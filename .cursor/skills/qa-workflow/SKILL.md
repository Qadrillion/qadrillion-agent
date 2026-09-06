---
name: qa-workflow
description: Internal five-step QA execution loop, loaded only by the qa orchestrator. Do not invoke directly for ticket IDs; enter through /qa.
disable-model-invocation: true
---

# QA workflow — the loop

`/qa` sequences this; this is the loop itself. Do not skip a step; execute
autonomously when the ticket is clear enough. Persist the ticket file at the
end of step 1, and update `status` / `next_action` / `blockers` at every step
boundary so a pause is recoverable.

## 1 · Understand
- Ticket: description, acceptance criteria as a numbered list, comments, links.
- Source: read the implementation. Produce `[SEVERITY]` risks (`code-review.mdc`).
- UI: extract real identifiers from source; produce the locator table.
  "In source?" is proven by the offline audit, "In build?" by the live smoke.
- Write `tickets/{ID}.md` → `status: analyzed`.

## 2 · Plan
- Scenarios: happy path, negative, edge, auth/validation, regression, plus one
  scenario per `[SEVERITY]` risk that maps to a test.
- Each scenario: `automated now` / `manual` / `blocked (reason)`.
- Present the plan and continue, unless it is ambiguous or the user asked to
  review first. → `status: planned`.

## 3 · Write tests
- Follow `test-automation.mdc`. Only identifiers from the table. Register
  locators, run the audit. Collections: edit in the tool, then sync.
- → `status: in_test`.

## 4 · Run and verify
- Verbose output, shown in full. No Pass without it.
- Assertion failure = finding. Locator error = back to step 1. Infra error =
  budgets in AGENTS.md. Never re-run to get green.
- For API work, confirm the request reached the service where a log or trace
  tool exists — a 2xx is not proof the work happened.

## 5 · Report
- `tracker-reporter` prepares the comment (and bugs) per `tracker-reporting.mdc`.
  The hook asks before any post. → `status: reporting`.
- `ticket-writer` closes the file: `status: done`, `verdict`, final
  `next_action`, evidence attached.
- Overwrite `docs/STATE.md`; append a `docs/sessions/` entry.
