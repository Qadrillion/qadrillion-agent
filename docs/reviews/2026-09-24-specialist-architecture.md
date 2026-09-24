# Specialist architecture audit and rationale

Baseline: `91e9bb0d4dcbfe812963fe6f04f4387c1b664497`, merged portability PR #3.
The starting checkout was clean; its feature branch was preserved. Main was
fast-forwarded before creating `feat/qa-specialists`. The prior audit and both
research registers were inspected; no company account or source was used.

## What the portability upgrade solved and left open

The existing `qa` entrypoint already separates intake, identity, scope, resume,
workflow and reporting. The five rules own evidence/authorization contracts.
Generic agents have distinct navigation, review, execution, persistence and
publication responsibilities. `qa-config.json` is a capability inventory;
doctor deliberately does not execute its commands. Source, tracker, runner and
vendor choices are optional. Those boundaries remain useful.

The specialist gap is concrete: `surfaces.md` offers a paragraph for each
interface, with mobile sharing desktop. A capable agent must supply most of the
test design, synchronization, artifact and debugging procedure itself. Eleven
golden tasks assess small decisions and persistence; their evidence does not
demonstrate real specialist test authoring or defect sensitivity. The verifier
checks policy/config/adapter behavior, not browser/device automation quality.

## Smallest useful decomposition

| Layer | Owner | Reason |
|---|---|---|
| Intake, target/criteria, route, mixed-task coordination and handoff | `qa` and `qa-workflow` | These decisions need the whole task and should be made once. |
| Authorization, source review, evidence/locators, ticket schema and reporting | Existing `.cursor/rules/*.mdc` | One editable contract; specialties reference rather than fork it. |
| API, browser and mobile author/run/debug/maintain procedures | `qa-api`, `qa-web`, `qa-mobile` | Different state, observation and execution failure modes justify depth. |
| Bounded attack-surface checks and measured workload investigation | `qa-security`, `qa-performance` | Risk overlays that compose with interfaces, not new ticket scopes or mandatory audits. |
| Playwright, stdlib HTTP, Appium/Maestro/native tools and k6 adaptations | Conditional skill references | Team runner stays authoritative; detailed syntax should load only when relevant. |
| Accessibility, exploratory sessions, pipelines and BLE | Focused references | Accessibility shares UI state; exploration is already a workflow technique. Pipeline/radio procedures can guide useful checks, but no broad stack/hardware validation justifies additional skill shells. |
| Independent source location/review and execution | Existing agents or sequential roles | Skills provide instructions, agents provide isolation/ownership. Test authoring stays with the orchestrator or a general worker; the execution-only runner remains execution-only. |
| Reproducible local targets, measurement and evaluation records | `tools/specialists` and meaningful tooling tests | Repeated exact operations belong in code. Fixtures are optional examples, not a replacement for product runners. |

## Routing and runtime decisions

Quick questions leave before ticket creation or specialty loading. Actual
interfaces select surface procedures; explicit work or concrete changed risk
selects overlays. A normal login fixture does not trigger a security assessment;
a functional wait does not justify load. Mixed tasks share a business oracle,
fixture ownership and one evidence record. Missing optional capability limits
the affected execution claim while remaining work continues.

`tools/agents/sync.py` already recursively copies canonical skills and their
resources to `.agents/skills` and `.claude/skills`, preserving modes. Adding a
parallel skill installer or tool-specific agent fleet would create redundant
ownership. Root-relative shared-contract paths and skill-relative recipes work
across these copies. Generated equality is structural evidence; runtime metadata
discovery and hook trust require separate observations. Cursor can see multiple
roots, so deduplication cannot be inferred from identical files.

## Evaluation design and trade-offs

Disposable local services and Android app fixtures have independent written
contracts and known behavior variants. Fresh agents receive tasks and necessary
fixture context, author/debug real tests, and retain artifacts. The evaluator
then checks defect detection and the same assertions on corrected behavior.
This is stronger evidence than instruction linting; small synthetic targets
still cannot represent arbitrary company systems. The local latency workload
is deliberately capped and labelled, not advertised as capacity validation.

Retain diagnostic failures and implementation fixes separately. Check raw
actions against claims, cleanup and unnecessary permission requests. Model
execution, deterministic fixture tests, native discovery and physical execution
are distinct evidence categories. The frozen [acceptance criteria](../specs/2026-09-24-qa-specialists.md)
and measured [support matrix](../reference/specialist-support.md) define the bar;
the work-laptop pilot is adoption verification, not deferred generic implementation.
