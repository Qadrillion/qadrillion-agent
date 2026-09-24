---
name: qa
description: Autonomous QA orchestrator. Use when given a ticket ID (e.g. `/qa PROJ-123`) or a feature or bug to test end-to-end. Classifies, routes to the right subagents, sequences the qa-workflow loop, resumes paused tickets from their frontmatter, and prepares the tracker report. Stops only at the gates the hooks enforce.
---

# QA orchestrator (`/qa <TICKET>`)

The single front door for ticket-driven QA. This skill decides *what runs and
in what order*; it does not restate contracts. The contracts are in the rules,
the loop is in `qa-workflow`, the boundaries are in the hooks.

## Inputs

A ticket ID, or a free-text bug report / task (skip the tracker fetch, infer scope).

## Pipeline

### 0. Resume, refresh, load
- If `tickets/{ID}.md` exists: read the frontmatter (`ticket-state.mdc`) and
  resume from `status` + `next_action`. Re-verify `build` and `source_refs`
  are still current before trusting prior findings.
- `./tools/workspace/refresh.sh --scope <relevant>` — fetches and fast-forwards
  clean canonical branches only; never switches branches.
- Read `.cursor/skills/qa-workflow/SKILL.md`. This orchestrator sequences it.

### 1. Understand
- Fetch the ticket (tracker MCP, read tools): description, acceptance
  criteria, comments, links. Pull wiki or design context when it matters.
- **Mandatory source review** for anything that changes behaviour:
  `code-explorer` to locate, `code-reviewer` for the `[SEVERITY]` pass.
- Mobile / web UI: build the locator table (identifier, in source?, in build?).
  Missing means missing. Never invent a substitute.

### 2. Classify and route
State the scope (`api` / `ui-web` / `mobile` / `backend` / `multi-surface` /
`tooling` / `quick`). Read the matching convention rule before writing
anything. **Persist now:** `ticket-writer` creates `tickets/{ID}.md` with
`status: analyzed` so a pause is recoverable.

| Scope | Author | Execute | Extra |
|---|---|---|---|
| `api` / `backend` | collection or API test | `test-runner` | confirm the request reached the service (logs/traces), not just 2xx |
| `ui-web` | Playwright test | `test-runner` | design checklist if a design link exists |
| `mobile` | framework test, registry entry | `test-runner` | run the live locator smoke first |
| `multi-surface` | both | both | API first, then UI |
| `tooling` / `quick` | direct edit | direct | — |

### 3. Write tests
Only identifiers from the step-1 table. Register locators; run the offline
audit. Never hand-edit a synced collection.

### 4. Run and verify
`test-runner` with verbose output. Show real output. A failure is a finding
(re-run once, then report). Locator error → back to step 1. Infra error →
AGENTS.md error budgets.

### 5. Report and close
- `tracker-reporter` prepares the QA comment (and any new bug) per
  `tracker-reporting.mdc`; the MCP hook asks before it posts.
- `ticket-writer` sets `status`, `verdict`, `next_action`, attaches evidence.
- Overwrite `docs/STATE.md`; append `docs/sessions/<date>-<ID>.md`.

## Gates (everything else is autonomous)

Stop and ask when requirements are ambiguous, a locator or fixture is
missing from the build, or a budget is spent. Every external write and every
production-shaped action is already gated by the hooks — you will be asked;
do not pre-empt it with prose.

## Output, always

Scope → what was done → files changed → source-review insights → tests
written → results with output → tracker comment (prepared / posted) →
blockers → verdict `Pass | Partial | Fail`.
