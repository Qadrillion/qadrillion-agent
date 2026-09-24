# The maintained agent configuration

`.cursor/` owns shared skills, roles, rules and guard policy. Cursor uses these
directly; `python3 tools/agents/sync.py` generates the Claude/Codex bridges from
committed sources. Run `python3 tools/verify.py` after changing them. Never edit
a generated copy to create a second contract.

| Layer | Path | Load when |
|---|---|---|
| Identity and handoff | [AGENTS.md](../AGENTS.md) | Session startup |
| Minimal always-on behavior | [core](rules/core.mdc) | Every task |
| Ticket, source, test and reporting contracts | `rules/*.mdc` | Relevant work |
| QA and evaluation procedures | `skills/*/SKILL.md` | Matching task or command |
| Bounded specialist roles | `agents/*.md` | Independent work justifies delegation |
| Targeted hook checks | `hooks.json`, `hooks/` | Supported native runtime events |

`/qa` handles a ticket or supplied task. The `qa-workflow` skill is its internal
procedure. `/golden-tasks` evaluates behavior; policy payloads alone are not a
model evaluation. Without subagents, one agent performs the roles sequentially.

## Hook policy

The default `GUARD_PROFILE='targeted'` in `hooks/guard.conf` protects recognizable
destructive Git actions, production-targeted test runs, credentials and configured
protected paths. High-impact operations can still require approval. Ordinary
documentation edits, dependency installation and authorized CLI/MCP updates have
no blanket confirmation gate. Native permissions and task authorization still
apply. `GUARD_PROFILE='strict'` opts into broader mutation and unknown-tool gates.

The shell guard matches command text; the read guard checks paths; native edit
adapters check file destinations without executing documentation examples.
A command pasted inside a shell heredoc can still trigger text heuristics: use
native file editing for documentation. Project changes do not disable global
hooks. A rejected action is reported, not retried through another transport.

Lifecycle hooks provide a state-checkpoint reminder. They are advisory and do not
make state a distributed lock. Hooks are not a sandbox, and event coverage varies
by runtime. See [runtime support](../docs/reference/runtime-support.md) for trust,
known gaps and disposable native smoke checks.

## Connections and customization

Use [adoption](../docs/adopting.md), [capability configuration](../docs/reference/qa-config.md)
and [integrations](../docs/reference/integrations.md). Choose relevant connections
for the task and authenticate through native mechanisms. Keep credentials out of
the repository; example MCP files contain placeholders only. No fixed server count
or vendor is required. Read detailed guidance on demand.
