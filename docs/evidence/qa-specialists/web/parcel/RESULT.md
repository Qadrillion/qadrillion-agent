# Fail — parcel browser receipt price disagrees with saved order

LOCAL-1, 2026-09-24. Owner: local QA agent. Scope: black-box browser order journey against tools/specialists/CONTRACT.md. Local draft only; nothing published. No service source, instruction/config files or identity files changed. No source revision available (workspace has no HEAD); source review intentionally excluded. All task output is in artifacts/; automation is in tests/.

## Finding WEB-1

In Chromium and Firefox, enter 3 in Quantity and activate Place order. The receipt displays `3 parcels — $12.00`; the contract requires `3 parcels — $15.00`, and the persisted order contains `quantity: 3, total_cents: 1500`. Likewise, quantity 1 displays $4.00 instead of $5.00, and quantity 100 displays $400.00 instead of $500.00. Customer-visible totals are wrong; severity high. Product owner unassigned. Recommendation: correct receipt pricing, then run these unchanged tests against the corrected target identity.

First-failure diagnostics were inspected before continuing the matrix: exact live identity matched, POST returned 201, receipt matched uniquely, input/click were actionable, status was Order saved, button was enabled, persisted amount was correct, no browser console/page errors were captured. Trace and screenshot confirm the visible wrong price; this is a product assertion failure, not a locator or timeout problem. No assertion weakening, retries or diagnostic reruns occurred.

## Results and environment

| Invocation | Passed | Failed | Skipped | Exit |
| --- | ---: | ---: | ---: | ---: |
| Chromium first deterministic case | 0 | 1 | 0 | 1 |
| Chromium remaining cases | 0 | 2 | 0 | 1 |
| Firefox complete suite | 0 | 3 | 0 | 1 |

Total: 6 executed, 6 failed, 0 passed, 0 skipped, 0 expected-failed, 0 unexpected-passed, 0 infrastructure errors, 0 retries, 0 selected tests not run. Each failure is WEB-1. Successful subchecks do not turn failed cases into passes.

Playwright 1.63.0 from installed node_modules; Chromium 153.0.8010.12 and Firefox 155.0, headless on macOS 26.6.2 arm64, viewport 1280×720, locale en-US, timezone UTC. Identity: run 4ecbc3c1-9475-4f18-810e-5f43cd23624d; build a036766d21e2e67fec0b69432b01472b177cdc3b8131cc30e155a34c7f07f28a; http://127.0.0.1:60882. Exact live identity checked before each test and cleanup. No response mocking or service alterations.

Keyboard checks used Tab to Quantity, keyboard text entry, Tab to Place order, and Enter. Invalid 0, 101, 1.5 and empty values were rejected without POST; native validation returned focus to Quantity. Recovery to 100 submitted successfully. Focus-visible state, computed outline and focus screenshot retained. Success status and enabled button passed. No screen-reader announcement or comprehensive accessibility claim is made.

One fresh context per case, serialized against the supplied dedicated target. Ownership captured from successful browser order creation responses. All 6 owned orders deleted with HTTP 200; alice and bob order lists matched pre-test baselines after every case. Target process remains running because it was supplied, not created by this task. No jobs or receipts created through fixture APIs.

## Evidence

- observation.json: actual roles/names, locator counts, available engine versions and identity.
- first.log, chromium-rest.log, firefox.log: raw test output; matching .exit files preserve runner exits.
- first.json, chromium-rest.json, firefox.json: structured reports and attachment references.
- execution.json: timestamps, counts, environment, test hash and cleanup totals.
- first-diagnostics.json and *-details.json: persisted orders, receipts, network status, console and cleanup.
- trace-inspection.json and first-failure.jpeg: extracted first-attempt trace evidence, inspected directly.
- first/, chromium-rest/, firefox/: retained traces, screenshots and error contexts. Final screenshots are taken after the persistence reload; use trace frames / first-failure.jpeg for the failed receipt state.

## Commands actually run

Working directory: /tmp/qadrillion-execution-evals/web (canonical /private/tmp/qadrillion-execution-evals/web).

```sh
node tests/observe.cjs
PLAYWRIGHT_JSON_OUTPUT_NAME=artifacts/parcel/first.json npx --no-install playwright test -c tests --browser=chromium --workers=1 --retries=0 --trace=on --output=artifacts/parcel/first --reporter=list,json --grep='nontrivial'
PLAYWRIGHT_JSON_OUTPUT_NAME="$PWD/artifacts/parcel/chromium-rest.json" npx --no-install playwright test -c tests --browser=chromium --workers=1 --retries=0 --trace=on --output=artifacts/parcel/chromium-rest --reporter=list,json --grep-invert='nontrivial'
PLAYWRIGHT_JSON_OUTPUT_NAME="$PWD/artifacts/parcel/firefox.json" npx --no-install playwright test -c tests --browser=firefox --workers=1 --retries=0 --trace=on --output=artifacts/parcel/firefox --reporter=list,json
node --check tests/run-parcel.cjs
node --check tests/parcel.spec.js
```

Observation and syntax checks exited 0. Test commands exited 1 each; stdout/stderr redirected to their .log files. The first JSON reporter resolved its relative path under tests; it was moved intact to artifacts/parcel/first.json. Two artifact-extraction attempts encountered a path/trace-field mismatch; corrected by checking actual files and trace structure. These were evidence-processing errors, not test retries.

## Rerun unchanged

```sh
node tests/run-parcel.cjs /absolute/path/to/another-identity.json
```

The wrapper runs Chromium and Firefox sequentially with retries disabled and writes a new timestamped artifacts directory, command metadata and runner exits. It was syntax-checked; the constituent test commands were executed above. Browser binaries must be available. The supplied identity must identify the same disposable loopback fixture contract; each test compares its entire live identity before mutation. Do not run concurrent suites against one shared target.

Unexecuted/excluded scope: WebKit, mobile viewports, screen readers, full WCAG audit, back/forward/deep-link and repeated-submit behavior, server-error recovery, transient loading-state behavior, API contract suite, async jobs, performance, security and service-source review. No external publication. No blocker to completing the selected browser matrix; WEB-1 blocks a passing outcome.
