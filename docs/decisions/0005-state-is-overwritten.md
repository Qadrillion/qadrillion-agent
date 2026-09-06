# ADR-0005 — Live state is overwritten; history is appended and never read cold
Status: accepted (2026-09-06)

## Context
One workspace kept a "handoff" file that was loaded into every chat. It grew
to thousands of words: numbered next-actions with duplicates and
strike-throughs, done items kept for the record, message drafts to colleagues,
sent-message history. It cost roughly a fifth of the fixed context on every
turn and no longer answered "where am I" without reading all of it.

## Options
1. One file that is both state and log — rejected: that is the landfill above.
2. State + log, log read at startup "for context" — rejected: grows with project age.
3. **Three layers by growth behaviour** — chosen.

## Decision
`docs/STATE.md` holds what is true now and what is next; it is overwritten
every session and is the only state file read cold. `docs/sessions/` holds
what happened, appended, grep-only. `docs/decisions/` holds why, one file per
real decision, index read cold. Message drafts go to `docs/drafts/`; per-ticket
detail goes to `tickets/{ID}.md`. State is never `@`-imported into an
always-on rule — the agent reads it on cold start because AGENTS.md says so.

## Consequences
The stop hook asks once when a session changed files but not STATE.md. STATE
stays under ~60 lines; if it does not fit, the content belongs elsewhere.

## Revisit triggers
The harness ships durable per-repository memory with an explicit overwrite
semantic. Evaluate; keep the file regardless as the portable copy.
