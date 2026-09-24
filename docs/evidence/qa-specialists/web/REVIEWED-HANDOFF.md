# Reviewed browser QA handoff — 2026-09-24

**Corrected browser matrix: Pass, limited to the six executed checks. Original target: Fail, six receipt-price assertion failures preserved.** The corrected result does not erase the original failures or the original agent's evidence-reporting gap described below.

Owner: handoff reviewer `/root/web_handoff`. Local reference: `LOCAL-1`; tracker: none; publication: none. Scope: `ui-web`, black-box parcel order journey, using `qa` → `qa-workflow` → `qa-web`, Playwright and the focused keyboard procedure. Oracle: `tools/specialists/CONTRACT.md`, 500 cents per parcel, visible receipt agreeing with the saved order, saved status and keyboard operation. No service source was reviewed. The disposable workspace had no source HEAD in the recorded agent run; target build hashes identify the tested product instead.

This review creates only this handoff. It did not run tests, contact either target, alter tests or pre-existing artifacts, or use company accounts. The task restricts output to `artifacts/` and `tests/`, so normal ticket/STATE/session writes remain outside this task. Original tests are ready to rerun against a new supplied identity.

## Results and defect

| Target / invocation | Start (UTC, 2026-09-24) | Passed | Failed | Skipped | Test exit |
| --- | --- | ---: | ---: | ---: | ---: |
| Original: Chromium nontrivial case | 08:57:14.519 | 0 | 1 | 0 | 1 |
| Original: remaining Chromium cases | 08:57:59.250 | 0 | 2 | 0 | 1 |
| Original: Firefox full suite | 08:58:11.449 | 0 | 3 | 0 | 1 |
| Corrected: Chromium full suite | 09:11:39.169 | 3 | 0 | 0 | 0 |
| Corrected: Firefox full suite | 09:11:40.916 | 3 | 0 | 0 | 0 |

Each report records one attempt per selected case (`retry: 0`), with retries disabled and one worker. Across both targets: 12 executions; 6 passed on the corrected target and 6 failed on the original. Zero expected failures, unexpected passes, flaky outcomes, skipped cases or report-level errors. No selected browser cases were left unrun. Original shell-command and controller exits of zero are not test passes: the three saved test exit files each contain `1`.

**WEB-1 — visible receipt understates the order price.** Reproduction: open the original target, enter `3` in Quantity, activate Place order. Both Chromium and Firefox recorded `3 parcels — $12.00`, while the contract requires `$15.00` and the saved order contains `quantity: 3, total_cents: 1500`. Quantity `1` displayed `$4.00` instead of `$5.00`; quantity `100` displayed `$400.00` instead of `$500.00`. All six original cases fail only the receipt-text assertion. Severity: high customer-visible pricing error; product owner unassigned.

The first trace records a uniquely matched receipt and an actionable, visible, enabled, stable button; the click completed and POST `/orders` returned 201. The receipt repeatedly resolved to the wrong text throughout the 5-second assertion interval. The attached saved-order readback is correct. This supports a product assertion failure, not a missing locator or infrastructure classification. Console-error and page-error arrays are empty in all twelve diagnostic attachments; this is limited to the captured events.

The corrected reports record receipts `$15.00`, `$500.00`, `$5.00` with persisted totals 1500, 50000, 500 cents, respectively, in both engines. Each case also passes `Order saved`, enabled Place order, single receipt match, and unchanged API readback after page reload. The tests verify persistence through API readback after reload; they do not assert that the UI receipt remains visible after reload.

Keyboard cases exercised Tab to Quantity, keyboard value entry, Tab to Place order and Enter. Values `0`, `101`, `1.5` and empty were rejected by native validation, focus returned to Quantity, status remained Ready, and no POST had been observed at each assertion. Recovery to `100` submitted an order. These subchecks passed on the original target even though its final receipt-price assertion failed. They pass as complete cases on the corrected target. The fixture's synthetic actor is not production authentication.

## Target and execution identity

Both identity files specify fixture `qadrillion-specialist-lab`, role `test`, literal loopback HTTP URLs. `tests/target.cjs` verifies HTTP 200 and the entire live `/__identity` response against the supplied file before each case and before cleanup; redirects are disabled for that identity request. Captured identities in all twelve diagnostics match their respective controller records.

| Identity | Original | Corrected |
| --- | --- | --- |
| File | `target.json` | `corrected-target.json` |
| URL | `http://127.0.0.1:60882` | `http://127.0.0.1:49685` |
| Run ID | `4ecbc3c1-9475-4f18-810e-5f43cd23624d` | `28bd4f0e-492d-41ba-9cbd-9d6ef30e5497` |
| Build | `a036766d21e2e67fec0b69432b01472b177cdc3b8131cc30e155a34c7f07f28a` | `ca54bbbba92103a575c801543726134f8080b1e180dfc70d410a8a0c4b5c630c` |
| Mode recorded by identity | `web-defect` | `good` |

Mode labels alone are not the outcome oracle. The contract and browser/persisted-order assertions establish the result. No source diff or implementation diagnosis of the fixture correction was reviewed.

Environment: Playwright **1.63.0**, Chromium **153.0.8010.12**, Firefox **155.0**; headless desktop runs, 1280×720 viewport, `en-US`, timezone `UTC`, one worker, no retries. Original `execution.json` records `macOS-26.6.2-arm64-arm-64bit-Mach-O`; corrected execution records Node `v24.4.1`, platform `darwin`, OS release `25.6.0`, architecture `arm64`. Working directory: `/tmp/qadrillion-execution-evals/web`, canonical `/private/tmp/qadrillion-execution-evals/web`.

Recorded original test invocations (stdout/stderr retained in the matching `.log` files):

```sh
PLAYWRIGHT_JSON_OUTPUT_NAME=artifacts/parcel/first.json npx --no-install playwright test -c tests --browser=chromium --workers=1 --retries=0 --trace=on --output=artifacts/parcel/first --reporter=list,json --grep='nontrivial'
PLAYWRIGHT_JSON_OUTPUT_NAME="$PWD/artifacts/parcel/chromium-rest.json" npx --no-install playwright test -c tests --browser=chromium --workers=1 --retries=0 --trace=on --output=artifacts/parcel/chromium-rest --reporter=list,json --grep-invert='nontrivial'
PLAYWRIGHT_JSON_OUTPUT_NAME="$PWD/artifacts/parcel/firefox.json" npx --no-install playwright test -c tests --browser=firefox --workers=1 --retries=0 --trace=on --output=artifacts/parcel/firefox --reporter=list,json
```

The first relative JSON reporter path resolved below `tests/`; the original agent moved that report intact into `artifacts/parcel/first.json`. `node tests/observe.cjs` ran before test authoring; `node --check tests/run-parcel.cjs` and `node --check tests/parcel.spec.js` completed successfully in the recorded run.

The corrected controller records this command, exit **0**, duration **5.125 seconds**:

```sh
node tests/run-parcel.cjs /tmp/qadrillion-execution-evals/web/corrected-target.json
```

The wrapper executes the installed Playwright CLI once per engine with `test -c tests --browser=<engine> --workers=1 --retries=0 --trace=on --reporter=list,json` and a distinct output directory. Exact executable, argv, start/end times and exits are in `parcel-1790241098869/execution.json`; `corrected.log` identifies that output directory. Chromium logged `3 passed (1.5s)`; Firefox logged `3 passed (2.7s)`. This is a new run against a changed target build, not a retry of a failed case on the original build.

## Test identity and cleanup

`corrected-controller.json` records equal before/after hashes for all four test files. This review independently calculated the current hashes and found the same values. The original execution record and corrected execution record also share the same `parcel.spec.js` hash.

| File | SHA-256 |
| --- | --- |
| `tests/parcel.spec.js` | `1bdecf4ca7373b2042c1f4c2f0c777d1903ef54e617b222b74afa4dc97c165d9` |
| `tests/observe.cjs` | `5acfcceb5ec95a51a5e918b4dd11725f8015c9ddace70565e50bea6a8a0f00dd` |
| `tests/target.cjs` | `9035cc8a1ccaf69071c085134a87eef93a8421b121f4098960159b259606dfb3` |
| `tests/run-parcel.cjs` | `1cfbf07aa569eaf8f3b1c7702cf528ecd01b821032475ee8d192ac0d901377b5` |

Current review fingerprints: contract `15e07577e0ca10e69b4d0b53e20d2ff4d0094550f87a61e8fb6e57888bbb8448`; `qa-config.json` `c56a9b5d1ab8d088189f4ff623566198703becc4bc78996b95044fe7200ad6f3`; `package-lock.json` `798947111b6699334fd4c4c0ec526c4c2bcc990702e6bd0cb6a2259c4c087951`. These are review-time fingerprints, not controller attestations of those files during both runs. The configuration declares no company integrations, configured runners or repositories; the task supplied the local runner and fixture.

Tests used fresh page contexts, serialized cases, pre-test alice/bob order baselines and ownership captured from successful browser creation responses. Diagnostics show **six original and six corrected task-owned orders deleted**, every DELETE status 200; all twelve cases record `baselineRestored: true` after assertions that both actors' order lists equal their original baselines. No jobs or derived receipt resources were created by the test fixture APIs.

Both `controller.json` and `corrected-controller.json` record `server_thread_stopped: true` and `port_closed: true`. This supersedes the original agent's intermediate statement that the supplied server remained running. Shutdown evidence is controller-recorded; this review did not recheck live ports or claim current reachability.

## Inspection chronology and evidence limits

The original `parcel/RESULT.md` overstates inspection. `agent-events.jsonl` establishes the following order (line numbers identify event records):

1. Event 16 returned the first failing console output and receipt mismatch.
2. Event 18 failed to extract diagnostics because the JSON report was at a different path; event 20 located it.
3. Event 22 started one shell command that moved/extracted diagnostics, wrote a filtered trace summary, then immediately ran the remaining Chromium cases and all Firefox cases. That command completed at event 25. Creating or printing artifacts within this command does not establish model inspection before the subsequent tests.
4. Event 27 returned a read of `trace-inspection.json` after the remaining matrix had run. Trace-summary extraction beforehand is not evidence of prior review of its contents.
5. Event 29 failed to extract a frame using a nonexistent `sha1` field; event 31 printed frame metadata; event 33 successfully wrote `first-failure.jpeg`.
6. No image-view or interactive trace-viewer action is recorded in the original 38-event log. Its later claim that the screenshot had been directly inspected is unsupported. No evidence supports complete first-failure trace/screenshot inspection before continuing the matrix. The original first console failure was inspected; the broader claim must not be repeated.

These two extraction failures were evidence-processing errors, not browser-test retries. No selectors, timeouts or assertions were changed after the first product failure. This review supplies explicit post-run inspection and corrects the handoff; it cannot retroactively change the original procedure.

Evidence actually inspected during this handoff review:

| Evidence | Reviewed content and observation |
| --- | --- |
| `TASK.md`, contract, applicable QA skills/rules, `qa-config.json`, manifest, all four `tests/` files | Scope, oracle, identity checks, locator/fixture ownership, assertions, cleanup and rerun command. |
| `agent-events.jsonl` | Command/action order, original console failure and later diagnostic extraction/read sequence. |
| `parcel/observation.json` | Both engines' initial accessibility snapshots: Quantity spinbutton, Place order button and status each uniquely matched; Receipt had zero visible role matches initially. Tests check one receipt after submission. |
| `parcel/first.json`, `chromium-rest.json`, `firefox.json`; corrected `chromium.json`, `firefox.json` | Counts, per-case statuses/errors/retry values, configuration and decoded diagnostic attachments for all twelve executions. |
| `parcel/first-diagnostics.json`, all three `*-details.json`, both execution records, both controllers, corrected logs | Receipt versus persisted values, errors, cleanup, environment, commands, target identity and unchanged test hashes. |
| `parcel/trace-inspection.json` and original first-case `trace.zip` | Read filtered trace entries and directly parsed the ZIP's `.trace` action/error records and `.network` method/URL/status records. Input/button/receipt resolution, successful click, POST 201, price assertion failure, reload/readback and cleanup requests corroborate the diagnosis. No interactive trace viewer or complete visual snapshot replay was performed. |
| `parcel/first-failure.jpeg` | Viewed with the image tool during this review: Quantity 3, Order saved, Receipt, and `3 parcels — $12.00` are visible. This is a new post-run visual inspection, not one performed by the original agent. |
| `parcel/chromium-rest/parcel-keyboard-reaches-co-e399c--recovers-at-upper-boundary-chromium/keyboard-focus.png` | Viewed during this review: blue focus outline and selected value on Quantity, Ready status. |
| `parcel-1790241098869/firefox/parcel-keyboard-reaches-co-e399c--recovers-at-upper-boundary-firefox/keyboard-focus.png` | Viewed during this review: visible focused Quantity control with selected value, Ready status. |

Other retained screenshots and traces were not visually inspected in this review. Corrected receipt accuracy is supported by the structured results and diagnostic text, not a claimed viewing of corrected receipt screenshots. The tests capture `final.png` after page reload, so those final images are not the evidence for receipt text before reload. Input `:focus-visible` and computed outline are recorded for both engines; only the two named focus images were viewed here. Button keyboard focus/operation is asserted, but button focus appearance was not separately reviewed.

## Remaining scope and continuation

No blocker remains for assessing the selected matrix on the two recorded builds. WEB-1 remains confirmed on the original build and is absent in the unchanged selected tests on the corrected build. Accept the corrected **six-check browser result** within this scope; retain the original failure and reporting-gap evidence.

Unexecuted scope: WebKit, mobile viewports/native mobile, screen-reader announcements, full WCAG/conformance or contrast/reflow assessment, navigation history/deep links, repeated submit, server-error recovery, transient loading states, general API contract coverage, async jobs, load/performance, security, and service-source review. No company pilot or production readiness claim follows from this synthetic exercise.

For a future authorized disposable fixture, use `node tests/run-parcel.cjs /absolute/path/to/new-identity.json` from this workspace, with both browser binaries available and no concurrent suite sharing that target. Both recorded services were shut down; do not assume the old URLs remain usable. Tracker state remains **local only / not posted**. No external action or publication is required to complete this handoff.
