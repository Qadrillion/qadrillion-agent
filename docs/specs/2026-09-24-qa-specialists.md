# QA specialist execution

Status: implementation authorized by the user's 2026-09-24 brief.
Base: `91e9bb0d4dcbfe812963fe6f04f4387c1b664497` (merged PR #3).
Branch: `feat/qa-specialists`. Owner: framework maintainer session.

## Scope and architecture

Keep `/qa` as the entry point and the existing rules as the single owners of
authorization, evidence, locators, failure retention and reporting. Add five
on-demand execution skills: `qa-api`, `qa-web`, `qa-mobile`, `qa-security`,
`qa-performance`. The first three describe test authoring, execution, diagnosis
and maintenance for an interface; the last two are risk-selected overlays.
Skills are procedures, not extra workers. Reuse bounded existing roles; authoring
belongs to the orchestrator or an explicitly assigned general worker, never the
execution-only test-runner. No specialty-specific agents are required.

Use conditional references for tool recipes and accessibility, exploratory,
data and BLE checks. Executable helpers supply disposable reference targets,
repeatable evaluation and bounded measurement, not a mandatory production runner.
No new tracker, language, vendor or account requirement. Routine authorized work
continues; production, unknown targets, denied actions and credential disclosure
remain protected. The task authorizes a public PR containing only synthetic data.

## Acceptance criteria (frozen before implementation)

| ID | Observable completion criterion | Failure guarded against | Verification |
|---|---|---|---|
| A1 | Audit maps orchestration, specialties, references, roles and helpers to existing owners, with justified choices for accessibility/exploration/data/BLE. | File proliferation and duplicated contracts. | Source audit and independent review. |
| A2 | Five skills supply actionable prepare/author/execute/debug/maintain procedures covering every specialty topic in the user brief; conditional stack recipes are runnable against inspected versions. | Superficial best-practice prose and universal tool requirements. | Real isolated authoring exercises, source mapping and review. |
| A3 | `/qa` routes API, web, mobile, mixed tasks and justified security/performance overlays; quick questions bypass ticket work; ordinary functional tasks do not load unrelated overlays. | Under-routing, keyword over-routing and loading all skills. | Fresh-agent route/action evaluations across at least eight distinct cases, including missing capabilities. |
| A4 | API and security exercises author real tests against a local disposable service, detect known contract/completion and object-authorization defects, and pass on corrected behavior with assertions unchanged. | Status-only tests, fake execution, diluted assertions. | Retained failing/passing outputs, test hashes, fixture identity and cleanup evidence. |
| A5 | Web exercise authors and debugs browser tests using observed semantic locators, isolated state and condition waits; detects defective business behavior then passes corrected behavior unchanged. | Source-only locators, mocks presented as browser tests, flaky sleeps. | Real browser output and traces/screenshots; reference version and test hashes. |
| A6 | Performance exercise defines workload, thresholds, limits/stops and baseline; measures distributions and errors on real local HTTP traffic, detects a seeded regression then passes correction unchanged. | Traffic generation or averages presented as useful load assessment. | Raw samples, summaries, threshold exits and bounded run identity. |
| A7 | Inspect actual mobile capabilities; execute a real native/device or emulator/simulator path when feasible, including authoring and defect detection. If impossible, retain exact dependency/capability evidence, implement all generic procedures and exercise independent authoring checks while marking device execution not run. | Mocked drivers or static code called verified mobile execution. | Device probe, real run artifacts or explicit dependency blocker; review of Android/iOS/hybrid adaptation. |
| A8 | Evaluation retains failed attempts, distinguishes static/simulated/actual/native evidence, records unnecessary approval or inaccurate-claim failures, and uses actual token usage when exposed; proxies are labelled. | Inflated success, autonomy or efficiency claims. | Inspect action traces and machine-readable evaluation results. |
| A9 | Runtime copies regenerate without drift; a clean clone runs required offline verification and deterministic reference execution; CI passes. Native discovery/activation is checked where installed and accessible, otherwise exact limits are documented. | Generated files confused with native support and laptop-dependent generic functionality. | sync --check, verify.py, clean clone, CI and runtime smoke evidence. |
| A10 | Adoption, customization, research, support matrix and team handoff explain using/extending specialties and evidence limits. Reviewed merge-ready PR; no unresolved in-scope review findings. | Unusable handoff or unfinished generic scope. | Blind review against this table, fixes and final run record. |

## Initial support matrix and claim boundaries

The final measured matrix lives in `docs/reference/specialist-support.md`.
Entries here define intended coverage, not completed validation.

| Capability | Implemented procedure required | Reference execution selected | Supported adaptation paths | Execution limit to report |
|---|---|---|---|---|
| API | Contracts, boundaries, actors, state, async, retries/idempotency, cleanup | Python stdlib HTTP service and isolated language-native tests | Existing test language, collection/CLI/API runner | No real company schema/provider verified |
| Web | Locators, auth, isolation, async, business assertions, browser variation, trace diagnosis | Playwright on a local demo, Chromium plus another available engine | Cypress, Selenium, native browser/manual tools | Only installed/exercised engines certified for fixture |
| Mobile | Install/build, devices, contexts, waits, permissions, lifecycle, data, diagnostics | Choose from measured local capability probe before execution | Appium, native Android/iOS tests, Maestro/manual | Simulator is not hardware; unexecuted OS/tool paths labelled |
| Security | Explicit scope, selected attack surface, paired fixtures, impact and limits | Local object authorization and safe negative controls | WSTG/MASVS checks through team's existing tools | Narrow test is not assessment/certification |
| Performance | Model, baseline, thresholds, ceilings, stop, distributions, investigation | Bounded local HTTP workload with seeded latency regression | Existing k6/JMeter/Locust/native tooling | Local demo is not capacity or production SLO evidence |
| Accessibility/exploration/data/BLE | Focused executable check procedures when relevant | Fixture keyboard/focus checks; other checks only if actually run | Team oracles, datasets and hardware/protocol harnesses | No conformance, pipeline or radio claim from unexecuted guidance |
| Runtimes | Maintained Cursor + generated Claude/Codex + manual fallback | Installed CLI smoke where access permits | Generic agent reads entrypoint/contracts sequentially | Native trust/discovery requires observed runtime evidence |

## Review and implementation record

To be appended after verification, with content fingerprint captured before blind
review, commands/results, review disposition, CI URL and remaining exact limits.
