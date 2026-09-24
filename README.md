<p align="center">
  <img src="docs/brand/mark.svg" alt="Qadrillion" width="72" height="72">
</p>
<h1 align="center">Qadrillion Agent</h1>
<p align="center">
  <strong>Give your coding agent a QA workflow it can execute.</strong><br>
  Investigate risk. Write and run tests. Hand off evidence.
</p>
<p align="center">
  <a href="https://github.com/Qadrillion/qadrillion-agent/actions/workflows/governance.yml"><img src="https://github.com/Qadrillion/qadrillion-agent/actions/workflows/governance.yml/badge.svg?branch=main" alt="Framework checks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-FFA24A.svg" alt="MIT license"></a>
</p>
<p align="center">
  <a href="#quick-start">Quick&nbsp;start</a> ·
  <a href="#five-specialties-one-entry-point">Capabilities</a> ·
  <a href="#see-it-catch-a-defect">Try&nbsp;a&nbsp;demo</a> ·
  <a href="docs/adopting.md">Team&nbsp;setup</a> ·
  <a href="CONTRIBUTING.md">Contribute</a>
</p>

**A free, open-source AI-driven QA framework for engineers.** Take a ticket or
feature from investigation to test execution and evidence, using the tools your
team already has.

Designed for **Cursor, Claude Code, Codex and other capable coding agents**.
Your tracker, test runner, language and cloud remain your choices.
[Runtime setup and verified limits](docs/reference/runtime-support.md).

## Start with a real QA task

```text
/qa Test checkout across our web app and API.
Verify totals and whether another user can read the order.
Use our existing tools and prepare the results locally.
```

For this task, the agent loads **web + API + security** guidance, checks the
available capabilities, then authors and executes relevant tests. It preserves
failures and reports what was actually checked. Missing tools limit the affected
checks; they do not stop every useful action.

A mobile lifecycle bug loads mobile guidance. A latency regression adds
performance. A quick question stays a quick question.

## Five specialties, one entry point

Each specialty covers **prepare → author → execute → diagnose → maintain**.
`/qa` loads the relevant procedures and tool recipes as the task needs them.

| Specialty | Work it guides |
|---|---|
| [API](.cursor/skills/qa-api/SKILL.md) | Contracts and boundaries, actor permissions, persisted state, async completion, idempotency and cleanup |
| [Web](.cursor/skills/qa-web/SKILL.md) | Semantic locators, isolated fixtures, authentication, business assertions, browser variation and failure traces |
| [Mobile](.cursor/skills/qa-mobile/SKILL.md) | Android/iOS and native/hybrid procedures, build/device identity, observed locators, permissions, lifecycle and diagnostics |
| [Security](.cursor/skills/qa-security/SKILL.md) | Authorized checks selected by risk, actor/object controls, reproducible evidence and reasoned severity |
| [Performance](.cursor/skills/qa-performance/SKILL.md) | Workloads, baselines, thresholds, resource limits, stopping conditions, latency distributions and investigation |

Security and performance are selected when the task calls for them. Focused
references extend the workflow to accessibility, exploratory testing, data
pipelines and connected-device/BLE work. The [support matrix](docs/reference/specialist-support.md)
separates implemented procedures, executed reference stacks and adaptation paths.

## Quick start

**Prerequisites:** Python 3.11+, Git and Bash. Offline checks run on macOS and
Linux; validate your own WSL/Git Bash setup on Windows. Your agent and chosen
product-testing tools are separate prerequisites for live QA.

```bash
git clone https://github.com/Qadrillion/qadrillion-agent.git qa-workspace
cd qa-workspace
python3 tools/agents/sync.py
python3 tools/verify.py
python3 tools/workspace/doctor.py
```

Open the workspace root in your coding agent and give `/qa` a task, or use
`/qa PROJ-123` with a configured tracker. Without slash-command support, ask the
agent to read `AGENTS.md` and `.cursor/skills/qa/SKILL.md` and follow them.

Before adding company information, establish a **private team workspace** and
verify its remote and visibility. Configure the capabilities you actually have;
`doctor.py` checks local setup, not provider authentication or device access.
Follow the [adoption guide](docs/adopting.md) for your first real ticket.

## See it catch a defect

Try the bundled HTTP reference suites with **no model or company account**:

```bash
python3 tools/specialists/replay.py --out /tmp/qa-reference-first
```

Run from the workspace root and choose a new output directory each time. The
replay starts disposable local services, runs agent-authored API, authorization
and performance tests against defective and corrected behavior, and retains the
results in `replay.json` plus per-run artifacts.

**A defective fixture should fail its tests.** The replay succeeds only when the
expected defect is detected, the corrected fixture passes the same assertions,
and the owned services close. An unexpected failure remains a failure to diagnose.
This replays existing tests; it does not run a fresh AI evaluation.

[Add Chromium + Firefox](tools/specialists/reference/README.md) ·
[Run the native Android fixture](tools/specialists/mobile/README.md) ·
[Inspect the original evidence](docs/evidence/qa-specialists/README.md)

## How the work moves forward

1. **Understand the target.** Read requirements and available source; pin the
   build, environment and configuration. Black-box work is valid when source is absent.
2. **Choose the checks.** Route by surface and risk. Load only useful specialties;
   delegate bounded independent tasks when the runtime supports them.
3. **Write, run and investigate.** Use observed interfaces and meaningful
   assertions. Retain first failures; allow one diagnostic rerun for a stated hypothesis.
4. **Hand off a scoped result.** Record **Pass, Partial or Fail**, tested identity,
   evidence, remaining coverage and next action. Prepare tracker updates and
   publish when the task authorizes it and the runtime permits it.

Routine authorized QA, test authoring and local maintenance proceed without
repeated approvals. Shared contracts keep authorization and evidence consistent
across specialties and runtime adapters.

## Evidence you can inspect

The [specialist evaluation](docs/evidence/qa-specialists/README.md) records actual
test authoring and execution, including failed attempts and corrected claims:

- **API and security:** real HTTP suites detect contract/completion and cross-user
  access defects; corrected fixtures pass the detecting assertions unchanged.
- **Web:** Chromium and Firefox detect incorrect business totals, with retained
  traces and cleanup evidence.
- **Mobile:** a real Android emulator detects lost lifecycle state. Corrected
  coverage is **10 passed, 2 skipped (Partial)**; a fresh-emulator portability
  replay also detects and verifies correction of both lifecycle cases.
- **Performance:** a declared p95 budget detects a seeded latency regression,
  with raw samples, a baseline and bounded request counts.

[CI](https://github.com/Qadrillion/qadrillion-agent/actions/workflows/governance.yml)
runs offline verification on macOS/Linux and the HTTP/browser reference replays.
Nine completed isolated agent scenarios exercise routing and actual work;
[research mappings](docs/research/specialist-practices.md) explain the decisions.

These are reference-fixture results. iOS, physical devices, hybrid/BLE execution
and Appium/Maestro feature execution remain unverified here. Native agent
activation and hook enforcement also need checks in your own environment.
[Full support boundaries](docs/reference/specialist-support.md).

## Fit it to your team

| Configure | Where |
|---|---|
| Repository ownership, roots, branches and permitted mutations | [`workspace-manifest.json`](workspace-manifest.json) |
| Available integrations, runner commands, artifacts and target identity | [`qa-config.json`](qa-config.json) |
| Production selectors and protected paths | [`.cursor/hooks/guard.conf`](.cursor/hooks/guard.conf) |
| Authentication and permissions | Your runtime's local settings; keep credentials out of Git |

Start with a [configuration example](examples/config/), then use the
[integration guide](docs/reference/integrations.md) and
[team handoff/upgrade guide](docs/reference/team-workflow.md). Existing Playwright,
Appium, native or other test tooling can be adapted; no runner is mandatory.
Specialty skills supply expertise; subagents supply bounded independent work.
[Architecture and ownership](docs/reviews/2026-09-24-specialist-architecture.md).

Hooks provide defense in depth. Their coverage depends on runtime registration,
trust and events; they are not a sandbox. Production execution is excluded.
There is no framework telemetry or required Qadrillion account. Coding agents
and connected providers have their own costs, accounts and data policies.

## Help build it

Useful contributions include runner recipes, reproducible bugs, specialist
regression fixtures and clearer adoption docs. Bring a concrete task and evidence
of the behavior you want to improve. Start with [CONTRIBUTING.md](CONTRIBUTING.md),
[ask a question or report a bug](https://github.com/Qadrillion/qadrillion-agent/issues/new/choose),
or read the [fictional worked ticket](tickets/PROJ-101.md).

If this fits your workflow, **star the repository** to help other engineers find
it. Pilot reports with honest failures and limits are especially useful.

Built by [Qadrillion](https://qadrillion.com/repo). Free to use, adapt and
contribute under the [MIT license](LICENSE).
[Security policy](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)
