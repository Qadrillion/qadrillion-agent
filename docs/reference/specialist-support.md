# Specialist support and execution boundaries

The [architecture audit](../reviews/2026-09-24-specialist-architecture.md) explains
ownership. The [acceptance spec](../specs/2026-09-24-qa-specialists.md) fixes the
completion bar. This matrix distinguishes procedures from measured reference
execution; no arbitrary company stack is certified by the fixture.

| Capability | Implemented | Reference execution | Adaptation paths and limits |
|---|---|---|---|
| API | Contracts/dialects, boundaries, actors, persistence, async, idempotency, diagnostics, cleanup | Fresh agent authored 34 real HTTP tests; 7 initial failures, 34/34 unchanged passes on correction | Existing language-native suites and CLI/collection runners; synthetic actors do not validate real authentication. |
| Web | Observed semantics, fixtures/auth, waits, business effects, engine variation, first-failure traces, maintenance | Playwright 1.63.0, Chromium 153.0.8010.12, Firefox 155.0: 6 price failures then 6/6 unchanged passes; original report overclaims retained/corrected | Playwright reference; existing Cypress/Selenium/browser tooling remains valid. No conformance claim. |
| Mobile | Android/iOS/native/hybrid, install/build, permissions, lifecycle, observed locators, waits, data, diagnostics | Real Android14 API34 arm64, ADB/UIAutomator: first 8 passed / 2 failed / 2 skipped; diagnostic confirms lost state; corrected 10 passed / 0 failed / 2 skipped (Partial) | Native Android/iOS, Appium, Maestro recipes. Full Xcode and iOS Simulator absent; no iOS/hardware/hybrid/BLE execution claim. |
| Security | Authorized risk slice, actor/object controls, protected state, impact/severity, cleanup, limits | 69 bounded HTTP requests: 4 of 86 assertions detect cross-owner disclosure; corrected 86/86 | OWASP-informed selected checks; optional tools. Not a whole-application security assessment. |
| Performance | Workload/model, warmup/baseline, thresholds, ceilings/stops, distributions, errors, investigation | 50 candidate + 50 baseline requests: unchanged 40 ms p95 threshold detects 95.00 ms candidate; baseline 8.64 ms passes | Bounded stdlib local probe; k6 adaptation. No production capacity or measured bottleneck claim without telemetry. |
| Accessibility/exploration/data/BLE | Focused procedures with observation and oracle requirements | Only checks named in retained evaluation count as executed | No pipeline-stack, radio, assistive-technology or conformance certification. |

Use `/qa` with the actual feature and oracle. It selects surfaces and justified
overlays; questions bypass the workflow. Missing optional tools/source block only
dependent claims. The [routing table](../../.cursor/skills/qa/references/routing.md)
is procedural guidance, not a keyword classifier or authorization engine.

## Runtime evidence categories

Canonical Cursor skills and generated `.agents`/`.claude` copies supply identical
procedures. Native discovery, body selection, tool execution and hook trust are
different checks. See [runtime support](runtime-support.md). Word/character
budgets from `verify.py` are proxies; runtime usage events measure tokens for
those runs, not universal efficiency gains.

## Customize without forking contracts

Keep runner declarations in `qa-config.json`, ownership in the manifest, and
product oracles/fixtures in private product/automation repositories. Adapt the
recipe for the observed runner/version. Add a focused reference for a recurring
stack constraint, link it from the skill and evaluate real work before expanding
discovery metadata. Edit `.cursor`, regenerate adapters and verify the diff.

Before adding a specialty, show why existing procedures plus a reference cannot
execute the work. Provide a discriminating description, author/run/debug/maintain
instructions, capability fallbacks, independent defect-sensitive fixtures and a
measured support boundary. A skill does not require a new agent; delegate only
independently useful work in an owned checkout.


[Evidence and retained failures](../evidence/qa-specialists/README.md) include
original outputs, unchanged test hashes, independent action review and native
usage events. [Replay instructions](../../tools/specialists/reference/README.md)
run the HTTP/browser suites without model access. This deterministic replay is
separate from original model work. Native mobile literal decimal/text inputs were
filtered by the OS input path; those cases remain skipped. Appium/Maestro were
probed, not feature-tested. k6, Cypress and Selenium are adaptation recipes only.

Codex CLI 0.154.0 metadata discovery and explicit QA execution were observed.
Claude Code 2.1.278 metadata/full-skill reads and benign Read/Stop hooks were
observed. Neither proves implicit trigger parity or native deny enforcement.
Cursor editor 3.21.18 is installed. Its `cursor agent` launcher installed the
initially missing CLI; the native smoke result is recorded separately below.
