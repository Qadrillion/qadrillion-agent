<p align="center">
  <img src="docs/brand/header.png" alt="Qadrillion Agent — an open-source AI-driven QA framework" width="1280">
</p>

# qadrillion-agent

A free, open-source **AI-driven testing framework** for QA engineers. It connects
your coding agent to your existing QA work: understand a ticket, investigate risk,
plan checks, write and run tests, explore behavior, and hand off evidence.
Built from hands-on QA lead and senior QA engineering work; published by
[Qadrillion](https://qadrillion.com/repo) under the [MIT license](LICENSE).

Use Cursor, Claude Code, Codex, or another agent that can read repository
instructions and use your tools. Test web, API, backend, mobile, desktop, data or
connected products. Your tracker, language, cloud, observability and test runner
are choices, not prerequisites. Source and tracker access improve available
evidence; supplied requirements and black-box testing also work.

## Start locally

Requires Python 3.11+, Git and Bash (macOS/Linux; Windows via a verified WSL/Git
Bash setup). No application language or automation framework is imposed.

```bash
git clone https://github.com/Qadrillion/qadrillion-agent.git qa-workspace
cd qa-workspace
python3 tools/agents/sync.py
python3 tools/verify.py
python3 tools/workspace/doctor.py
```

Before entering company information, create a **private team workspace** and
verify its visibility/remote. Keep company tickets and evidence out of public
upstream. [Adoption and upgrade guide](docs/adopting.md).

Open the workspace root in your agent. Ask `/qa PROJ-123` when a tracker is
connected, or supply a task directly:

> Test our preview checkout. Quantities must be integers from 1 to 100. The API
> and web UI are available; product source is not. Plan the highest-risk checks,
> use our configured runner, and prepare the result locally.

For runtimes without slash commands, ask the agent to read `AGENTS.md` and
`.cursor/skills/qa/SKILL.md`. Roles can run sequentially without native subagents.

## Make it yours

| File | Configure |
|---|---|
| `workspace-manifest.json` | Repository roots, expected remotes, branches and permitted mutations |
| `qa-config.json` | Available integrations/capabilities, runner argv/cwd, artifacts and target identity requirements |
| `.cursor/hooks/guard.conf` | Known production selectors, protected paths and verified tool patterns |
| Runtime-native local settings | Authentication and permissions; never commit credentials |

[Examples](examples/config/) cover manual black-box QA, a web/CLI setup and a
mixed mobile/backend/device setup. They declare choices; they do not install or
authenticate tools. Connect relevant systems progressively, using
[the CLI/API/MCP guide](docs/reference/integrations.md). It distinguishes
Atlassian TWG CLI, ACLI and Rovo MCP and explains how to measure actual costs.

## What the workflow does

- Chooses tests by risk, with independent expected results and suitable test layers.
- Uses observed interfaces/locators and available source; records what cannot be checked.
- Preserves failing and diagnostic-rerun evidence, skips and incomplete coverage.
- Prepares tracker comments and bugs before authorized publication.
- Persists owner, branch, tested revision and next action for another engineer.
- Loads detailed guidance only when needed, retaining large outputs as artifacts.

The [QA research register](docs/research/qa-practices.md) documents 12 inspected
primary works and the resulting practices. [Team handoffs and upgrades](docs/reference/team-workflow.md)
keep company setup separate from public framework changes.

## What is verified

`python3 tools/verify.py` runs policy payloads, tooling/adapter regressions, ticket
validation, generated-config drift, setup checks and prompt-size budgets. CI runs
the same command. Behavioral scenarios live in `docs/golden-tasks/`; they require
actual agent runs and are distinct from deterministic tests.

Hooks are **defense in depth**, not a sandbox or a guarantee that every tool is
intercepted. Default guards target destructive operations, production tests and
credential exposure; ordinary edits and authorized QA updates proceed without
blanket approval prompts. Teams can opt into stricter gates. Native runtime
trust, permissions and observed blocking must be
checked on each machine. Read [runtime support and limits](docs/reference/runtime-support.md)
before unattended use. Production execution remains excluded.

There is no measured 99% autonomy or universal token-saving claim. Judge the
framework by verified outcomes, remaining risk, human interventions and measured
costs in your own environment. It orchestrates your existing tools; it is not a
hosted testing platform. No framework telemetry or account is required; connected
providers and coding agents have their own accounts, costs and policies.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Fictional worked ticket](tickets/PROJ-101.md)
