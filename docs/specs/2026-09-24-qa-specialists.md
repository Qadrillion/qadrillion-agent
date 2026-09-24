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

The implementation and independent review record follows. Acceptance criteria
above were frozen before implementation; limits are not converted into passes.

## Implementation record — 2026-09-24

Branch: feat/qa-specialists · Commits: 7dcc98a..6f77b8c (reviewed implementation; completion records follow)
Review-base: 91e9bb0d4dcbfe812963fe6f04f4387c1b664497
Review-fingerprint: ea0f4280f74b052b82a1d32c0ff3fdbc7e0556ad7ef3bb972abb8d656c7d4250
Full-diff-sha256: 141a5c8c98c3b23cf59c67573c87d908869e248aee6fc5600fe495cf70aa72c5
Verified: `python3 tools/verify.py` → PASS (139 tooling + 14 mobile tests; 75 guard payloads); `python3 tools/agents/sync.py --check` → current; five skill validators → PASS; clean-clone `npm ci` and `python3 tools/specialists/replay.py --web` → eight expected defective/corrected outcomes, unchanged test files and closed services. Hosted macOS/Linux offline, real reference execution and governance checks → PASS at `6f77b8c`.
Review: round 1 BLOCKED; round 2 PASS WITH SHOULDS; round 3 BLOCKED; round 4 PASS after supplemental repair review; CI startup correction PASS.
Deferred: 0 items. All six in-scope review findings were corrected; the subsequent CI startup failure was repaired and independently reviewed.

The fingerprint and full binary-diff hash were captured before dispatching each
blind reviewer. The code fingerprint excludes documentation; the full-diff hash
also pins the evidence and instructions in the reviewed snapshot. Review history,
findings, disposition and verbatim reviewer limits are in the
[blind-review record](../reviews/2026-09-24-specialist-blind-review.md).

| Criterion | Completion evidence |
|---|---|
| A1 | [Ownership audit](../reviews/2026-09-24-specialist-architecture.md): shared rules, five skills, focused references, existing bounded roles and optional executable helpers. |
| A2 | Five substantive author/run/debug/maintain procedures; [research decisions](../research/specialist-practices.md) and [measured support](../reference/specialist-support.md) separate recipes from executed stacks. |
| A3 | Nine completed isolated routing/action cases. Quick/ordinary tasks avoid unrelated specialists; missing-capability tasks retain useful authoring without inventing execution. Three provider-interrupted attempts remain recorded. |
| A4 | Real API suite: 34/34 corrected; authorization: 86/86 corrected. Original defect failures, unplanned contract mismatch, unchanged detecting assertions and cleanup remain inspectable. |
| A5 | Real Chromium/Firefox: six price failures then six corrected passes. Blind-review closed-page regression confirms cleanup despite retained diagnostic failure. Original reporting overclaims remain failures. |
| A6 | Fixed 40 ms p95 budget rejects 95.00 ms candidate and accepts 8.64 ms baseline, 50 samples each. Closed workload and environment limits are explicit; output reservation now precedes all HTTP. |
| A7 | Real owned Android14/API34 emulator path detects persistence failure. Corrected result is 10 pass, 0 fail, 2 skip: product coverage remains Partial. Full Xcode/iOS Simulator and unexecuted hardware/hybrid/BLE paths are named limits. Fresh owned emulator-5562 replay also detects both lifecycle failures and passes 2/2 after correction with identical test bytes. Both owned emulators/data cleanups completed. |
| A8 | Original action streams, outputs, hashes and independent observations are [committed](../evidence/qa-specialists/README.md). Nine completed Codex turns expose 2,569,296 input and 43,891 output tokens; other session usage is not inferred. |
| A9 | Generated copies current; clean-clone offline and real reference execution pass. Codex/Claude discovery/read observations remain narrower than native trust. Cursor installed CLI returns Authentication required with no native events; an authenticated Cursor session is the exact remaining dependency. Hosted CI is recorded below. |
| A10 | Adoption/customization/team handoff updated. Blind-review findings fixed; public PR and final check status recorded below. Merge remains with the user. |

Clean-clone HTTP/browser replay exercised `4ef5b3e`. After the mobile preflight
repair, a further clean clone at `21b4e0b` passed all 152 tests. Fresh emulator
replay exercised that repaired script. The subsequent malformed-identity guard
passed full offline and independent specialist checks; a release clone verifies
the resulting implementation. Hosted CI checks the final branch. Clean-clone
logs and original failures are under `docs/evidence/qa-specialists/verification`.
Neither synthetic fixtures nor this review certify an arbitrary company setup.

Reviewer limits at review time (verbatim): “Final CI, final clean-clone execution and PR completion remain unchecked. iOS, hybrid, physical hardware and native denial enforcement remain outside executed coverage.” Maintainer clean-clone/PR/CI completion is recorded afterward below. Full historical inspection limitations remain verbatim in the linked review record.

## Publication and hosted verification

[PR #4](https://github.com/Qadrillion/qadrillion-agent/pull/4) targets current main.
The [first hosted run](https://github.com/Qadrillion/qadrillion-agent/actions/runs/35984192362)
passed Linux and all eight real HTTP/browser replays, but failed macOS fixture
readiness. Its failure is retained in the verification evidence. The first server-based
contract test took about 35 seconds; the CLI fixture then missed its unchanged
three-second readiness ceiling.

Source inspection identified an unnecessary reverse-DNS dependency in Python’s
HTTPServer initialization. The lab binds literal loopback and now assigns its
server identity directly after TCP bind. A resolver-unavailable regression fails
on the original source and passes after repair; the cleanup test’s timeouts and
assertions are unchanged. Attributing the historical delay to DNS is an inference,
not a claim of captured resolver telemetry.

The inspected CI interpreter is CPython 3.11.9. Its
[HTTPServer bind](https://raw.githubusercontent.com/python/cpython/v3.11.9/Lib/http/server.py),
[TCPServer initialization](https://raw.githubusercontent.com/python/cpython/v3.11.9/Lib/socketserver.py)
and [socket name resolution](https://raw.githubusercontent.com/python/cpython/v3.11.9/Lib/socket.py)
establish this dependency. Lab has no CGI handler and its public identity already
uses literal loopback; the assigned ephemeral port and identity schema stay intact.

The [corrected hosted run](https://github.com/Qadrillion/qadrillion-agent/actions/runs/35984699651)
at `6f77b8cc90ba4f140c1d7ce561287a371a4e4645` passed all four jobs: Linux
offline, macOS offline, reference execution and governance. Fresh CI checkouts
run all 153 Python tests and 75 guard payloads; reference execution installs its
pinned dependencies and exercises all eight defective/corrected HTTP/browser
outcomes. The public run result is retained in
`docs/evidence/qa-specialists/verification/ci-repaired-result.json`.
The independent CI-repair review also returned PASS. Later completion-record
commits are documentation only; their current check state is visible on
[PR #4 checks](https://github.com/Qadrillion/qadrillion-agent/pull/4/checks).
No unresolved in-scope findings or generic implementation work remain. The
support matrix's native/runtime and Android input limits remain explicit.
