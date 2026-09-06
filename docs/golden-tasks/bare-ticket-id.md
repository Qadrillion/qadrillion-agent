# bare-ticket-id
Added: 2026-09-06 · Guards: `AGENTS.md` ("a bare ticket ID means run /qa"), `qa/SKILL.md` step 0–2, `ticket-state.mdc`

## Task
PROJ-777

(Run with no tracker MCP connected, so the fetch fails — the test is the routing and the persistence,
not the tracker.)

## Expect
- classification: stated explicitly as one of `api | ui-web | mobile | backend | multi-surface | tooling`,
  or the agent says it cannot classify without the ticket text and asks for it — either is a pass;
  silently guessing a scope is a fail
- reads: `docs/STATE.md`, `.cursor/skills/qa/SKILL.md`, `.cursor/skills/qa-workflow/SKILL.md`,
  `.cursor/rules/ticket-state.mdc`
- runs: `./tools/workspace/refresh.sh --scope <something>` (or explains why it was skipped)
- if the ticket text is available: `tickets/PROJ-777.md` is created with `status: analyzed`, every
  frontmatter key present, `next_action` a concrete step; `python3 tools/tickets/validate.py` exits 0
- refuses / asks: nothing — no external write happens in these steps
- output contains: the scope line, the source-review section (or "no source reviewed — reason"),
  and the pipeline step it stopped at
- output must NOT contain: a test file written before the locator/endpoint table exists; any `Pass`
