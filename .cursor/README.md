# .cursor — how the agent layer fits together

Open the workspace root in Cursor, start an Agent chat, type a ticket ID. That
is the whole interface. What loads, and when:

| Layer | Path | Loads | Owns |
|---|---|---|---|
| Boundaries | `hooks.json` + `hooks/*.sh` | outside the loop, every event | what may never happen, what needs approval |
| Identity | `../AGENTS.md` | every chat | who the agent is, cold-start order, budgets, output |
| Style | `rules/core.mdc` (always-on, <120 words) | every chat | behaviour when uncertain |
| Conventions | `rules/*.mdc` (glob or description) | when matching files or tasks are in context | one contract each |
| Procedures | `skills/*/SKILL.md` | on `/command` or description match | `/qa`, its loop, `/golden-tasks` |
| Workers | `agents/*.md` | when dispatched | isolated-context executors |

## Hooks (the only deterministic layer)

| Event | Script | Verdicts |
|---|---|---|
| `beforeShellExecution` | `guard-shell.sh` | deny destructive git, home-path deletes, credential reads, prod-targeted test runs, protected paths; ask on dependencies, deploys, DB mutations, `guard.conf` extras |
| `beforeMCPExecution` | `guard-mcp.sh` | deny listed servers and delete verbs; ask on write verbs (the confirm-gate) |
| `beforeReadFile` | `guard-read.sh` | deny keys, env files, credential files, protected paths (deny before exempt) |
| `sessionStart` / `stop` / `sessionEnd` | `checkpoint-state.sh` | one follow-up if files changed but `docs/STATE.md` did not; fail-open |

Per-workspace fences go in `hooks/guard.conf` (protected paths, production
hosts, extra deny/ask, MCP server deny list). Golden payloads:
`hooks/tests/run-tests.sh` — run after every edit; CI runs it on every push.

**Acceptance test, once per machine:** ask the agent to run `git reset --hard`
in a scratch repo. A live fence returns the hook's own message in the Hooks
output channel. Do not test with `git push --force` — the model refuses that on
its own and the refusal masquerades as a working fence.

Cloud agents see only committed project hooks; user-level hooks never load
there. `beforeReadFile` is not in every cloud hook set — the shell fence
covers `cat .env` independently.

## Claude Code

`.claude/settings.json` registers `.claude/hooks/pretooluse.sh`, an adapter
that feeds the same three guard scripts. `CLAUDE.md` is one line:
`@AGENTS.md`. Verify the deny once in Claude Code before delegating anything
unattended.

## Rules own the contracts

| Contract | Rule |
|---|---|
| Ticket frontmatter schema and state machine | `ticket-state.mdc` |
| Source-review checklist and `[SEVERITY]` output | `code-review.mdc` |
| Test hard rules | `test-automation.mdc` |
| Tracker comment and bug format | `tracker-reporting.mdc` |

Skills and subagents reference a rule; they never copy it. Subagents run in
isolated context, so they read the rule file explicitly.

## MCP

Credential-bearing servers go in the gitignored project `.cursor/mcp.json`,
never in `~/.cursor/mcp.json` (global servers load in every workspace,
including other clients'). Keep ≤3 servers; anything with a CLI gets a skill
that shells out instead. Commit `mcp.<name>.example.json` templates with
placeholders only.
