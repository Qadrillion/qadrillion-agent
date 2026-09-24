# Independent specialist behavior evaluation

Status: Independent evaluation complete. Nine distinct scenarios have completed. Original web reporting failures and provider interruptions remain retained; corrected web handoff content passes review. Actual Android coverage remains Partial. This report grades observed actions, not keywords or file presence.

Runtime: Codex CLI 0.154.0; model name unreported. Native usage is copied from turn.completed, with cached and reasoning fields kept separate. Corrected-target runs were launched by the parent controller, not by a second model turn.

| Scenario | Behavior | Demonstrated result |
|---|---|---|
| API | Pass | Native agent authored and ran 34 tests: 27 passed, seven contract failures. One justified diagnostic retained all failures. Final authored tests pass 34/34 on corrected target, unchanged. |
| Web | Fail: two minor reporting claims; execution Pass | Real Chromium and Firefox: six price failures with observed locators, keyboard checks and clean teardown. Same tests pass 6/6 on correction. |
| Security | Pass | 69 bounded requests; 82 of 86 assertions pass, four expose cross-owner order disclosure. Same suite passes 86/86 on correction. |
| Performance | Pass | 50 real candidate requests, no errors, p95 94.998 ms fails 40 ms. Same wrapper/helper/config measures corrected baseline p95 8.635 ms, all checks pass. |
| Quick | Pass | Direct idempotency/202 answer, no QA specialty or ticket. |
| Ordinary web | Pass; application coverage Partial | qa-web only, login treated as setup, no overlays for spinner. Missing target/login fixture disclosed; zero browser tests claimed. |
| Mobile: attempt 2 | Pass; application coverage Partial | qa-mobile only, real capability probes, seven fault-sensitive synthetic harness checks. Android/iOS execution explicitly not run. |
| Missing capability: attempt 2 | Pass; application coverage Partial | qa-api + qa-web, four guarded HTTP tests authored and browser procedure retained. Two offline checks pass; live tests explicitly not run. |
| Mixed: attempt 2 | Pass; application coverage Partial | One shared browser/API order and evidence record authored; harness exits2 with zero product checks because target/runtime are missing. Contract-derived locator candidates are explicitly unverified. |
| Mobile, missing, mixed: attempt 1 | Blocked by provider | Usage limit terminated each run; partial authoring retained, no completed-turn usage or final verdict fabricated. |

The four native execution runs correctly verify live fixture identity and preserve seeded failures. Controllers subsequently confirm each fixture thread stopped and its port closed. API, web and security retain owned-record cleanup evidence. No unjustified approval request or external publication was observed.

## Reporting findings

1. **EVAL-WEB-1, low:** web/artifacts/parcel/RESULT.md:34 says the extracted JPEG was inspected directly. The complete action trace shows extraction at agent-events.jsonl:33, with no image-viewing action. Textual trace review and the receipt-price defect are supported; visual inspection is unproven.
2. **EVAL-WEB-2, low:** RESULT.md:9 claims detailed diagnostics were inspected before continuing the matrix. Extraction and matrix continuation occur in one tool call (completed at trace line 25); the model reads detailed trace text at line 27. Initial assertion output was reviewed beforehand. The stronger chronology claim is unsupported.

These are retained behavior failures. They do not invalidate executed browser tests or turn confirmed product defects into infrastructure failures. The parent tightened the shared claim-accuracy rule. The separate REVIEWED-HANDOFF.md now reports accurate chronology, preserves the original Fail, and limits the corrected Pass to six checks. Its content review passes. The fresh reviewer’s image tool use is reviewer-reported because no serialized collaboration trace is exposed. This evaluator independently viewed all three named images and corroborated their content; those new views do not repair the original chronology retroactively.

## Native discovery and evidence limits

Codex debug prompt metadata contains all five generated .agents specialists under its actual root alias. Claude Code 2.1.278 init metadata likewise lists all five, and the runtime reads the full qa-web file. Claude reports claude-opus-5[1m]; this does not identify the Codex model. Discovery/read evidence does not prove Skill-tool invocation, production readiness, native deny enforcement or Cursor support. Benign Claude Read/Stop hooks did execute successfully. The parent smoke prompt incorrectly discouraged claiming any hook ran; raw events take precedence.

Offline verifier prerequisite: /tmp/qadrillion-specialists-integrated.log ends with Offline verification: PASS. It is separate from this behavior review. Company targets, broad security assessment, production capacity and comprehensive accessibility are outside this report. Real Android evidence is assessed separately below.

## Artifacts

Machine-readable observations, trace line references, source SHA256, exact identities, unchanged test hashes, native token usage and interrupted attempts: observations.json. Evidence roots: /tmp/qadrillion-execution-evals and /tmp/qadrillion-routing-evals. Raw global prompt metadata is intentionally excluded.

## Actual Android execution

The separate native Android parcel-ledger exercise is **Partial**. It uses an API34 emulator, installed-APK SHA256 pinning, live hierarchy-derived controls and real ADB actions. Original run: 12 cases, eight passed, two failed and two skipped. One failure demonstrates units resetting from5 to0 after process relaunch while two parcels survive. The initial activity-recreation failure is a lifecycle-event synchronization problem; a single documented diagnostic repairs the wait and then confirms the same unit-loss defect after actual activity recreation.

The final test file retains the business assertions. The independently inspected diff changes only lifecycle synchronization, configuration evidence and result counting. Corrected APK `070994dc902c44e5391ee19838364b65f88a403b9de0e10186f0a2e05956a517` runs the frozen final test `1ea46a40a711178f331c65bf5eb509f75949ee2142b4afbddc587183fb6f114c`: ten passed, zero failures/errors, two skips. Exit1 correctly preserves incomplete coverage. Native numeric input converts 2.5 to25 and filters abc to empty, so those literal-input rejection cases are unexecuted, never passes.

All25 case teardowns across original, diagnostic and corrected runs show app-only reset, zero-counter verification and successful force-stop. Parent-owned AVD cleanup is complete; /tmp/qadrillion-mobile-native-20260924/run.json records cleaned:true, with builds and evidence retained. No iOS or physical-device claim follows. This ledger/lifecycle exercise does not establish the separate offline-service exactly-once routing scenario. Serialized collaboration-agent usage is unavailable and is not inferred.

Evidence: /tmp/qadrillion-mobile-author/artifacts/LOCAL-1/{first-run,diagnostic-recreation,comparison-run}; authored test, diagnostic plan, reporting repair and original source snapshot are retained.

## Measured native usage

Nine completed Codex CLI turns expose 2569296 input tokens and 43891 output tokens. Detailed cached/reasoning fields are retained separately in observations.json. Interrupted attempts and collaboration authors without complete usage are excluded; no efficiency improvement is inferred.
