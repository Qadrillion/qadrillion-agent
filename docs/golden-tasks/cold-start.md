# cold-start
Added: 2026-09-06 · Guards: `AGENTS.md` cold-start order, `core.mdc`, the memory model (ADR-0005)

## Task
What are we working on?

## Expect
- classification: `quick`
- reads: `docs/STATE.md` first, then `docs/decisions/INDEX.md`; nothing else before answering
- reads must NOT include: anything under `docs/sessions/`, any `tickets/*.md` body, `docs/golden-tasks/`
- output contains: the Goal line and the first Next item from STATE.md, in the agent's own words
- output must NOT contain: a preamble ("Let me check…"), a summary of what it just did, an invented
  priority that is not in STATE.md
- length: under 12 lines
