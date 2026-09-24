# Fail — parcel API contract

Full suite: **34 tests, 27 passed, 7 failed, exit 1**. No errors, skips, expected failures or unexpected passes. Positive control: 1 passed, exit 0. Diagnostic after test-control-flow correction: 23 tests, 16 passed, the same 7 failed, exit 1. No product changes or source inspection. No external publication.

## Findings

1. **Completion has no promised receipt.** POST /jobs returns 202/pending. GET /jobs/{id} progresses from pending to complete within the two-second bound. GET /receipts/{id} still returns 404 `{"error":"receipt not found"}`. Expected 200 with matching job/order IDs and `delivered: true`. Reproduced in the single diagnostic run. This breaks the business completion promise. Full-run job: `5e3ec69a-eaa9-4420-93ae-33e2dbf1908f`; diagnostic job: `a3636c8c-d864-48ed-80ae-9488a2c04209`.
2. **Invalid body status contradicts the written contract.** Six forms—array, null, number, string, malformed JSON, empty body—return 400 rather than the specified invalid-input 422, with a valid idempotency key. Valid JSON objects with invalid quantity or extra fields correctly return 422. The status oracle follows the supplied contract literally; no undocumented exception for malformed/non-object input was assumed. Both runs preserve these failures.

## Coverage and diagnosis

Passed: quantities 1, 2, 99, 100 with exact totals and public read-back; integer/type/null/omission/extra-field partitions; key lengths 1 and 128 accepted, missing/empty/129 rejected; identical retry gives 200 and unchanged object/count; conflicting retry gives 409 without replacing state; fresh keys create distinct orders; actor key namespaces; order deletion, key reuse, preservation of another order; absent resources; pending receipt absence; job completion deadline; job deletion and post-deletion job/receipt absence.

Harness correction: initial assertions stopped the remainder of invalid-status and missing-receipt tests. Replaced those two assertions with subtests so independent state/deletion checks execute despite the primary failure. The diagnostic specifically established that invalid requests leave lists unchanged and job deletion preserves its order. Assertions and expected values were not relaxed. Original full output remains in `full.log`; diagnostic output in `diagnostic.log`. No further reruns performed.

The contract specifies no error object schema or invalid-job-body rejection status, so no invented schema/status assertions were used. Order responses are checked for exact fields, values and integer types. Job/receipt checks use documented fields. Delete response shape beyond a deleted ID is unspecified. Test review was performed sequentially; no agents needed.

## Environment and evidence

Python 3.14.6, standard library unittest/urllib, no dependency installation. Target `http://127.0.0.1:60868`, role test, run `a5483eb7-8dec-4240-a4cf-aad0e86fe13e`, build `a036766d21e2e67fec0b69432b01472b177cdc3b8131cc30e155a34c7f07f28a`. Every invocation compared all live identity fields with `target.json` before mutation; proxies and redirects disabled. Branch main has no commit. Identity, contract and final test hashes, commands, timestamps, cwd, platform, exits and counts: `execution.json`. Workspace refresh for api exited 0; no configured repositories/runners.

- `plan.md`: risk-to-check mapping and scope.
- `control.log`, `full.log`, `diagnostic.log`: decisive runner output and tracebacks.
- `{control,full,diagnostic}/http.jsonl`: exact HTTP requests/responses, statuses, media types and request durations.
- `{control,full,diagnostic}/identity.json`: verified live target identity.
- `{control,full,diagnostic}/cleanup.jsonl`: owned IDs, cleanup and baseline checks.
- `../../tests/test_api_parcel.py`: reusable suite.

## Cleanup, limits and handoff

All 58 test lifecycles across the three invocations completed cleanup with zero reported problems. Jobs were removed before orders, GET confirmed absence, receipt absence was checked, and both actor order lists matched their pre-test baselines. No synthetic records remain observable. The supplied target process was left running: this task did not create or own its process.

Unexecuted/excluded: browser/UI, security/access-control assessment, performance/workload measurement, product source review, restart/durable-storage behavior, concurrent retries, transport-loss injection, unspecified job failure/cancellation behavior. Persistence means independent HTTP read-back within the running service. Removal of an existing delivered receipt could not be demonstrated because the target never produced one; post-delete absence was demonstrated. No independent telemetry is supplied. There is no claim of whole-product coverage.

Owner: QA agent. Changed paths: `tests/test_api_parcel.py` and `artifacts/parcel-api/`. No instruction/config/identity files changed. No tracker post or external draft publication. State/session handoff is contained here under the explicit artifacts-only constraint. Next action: product owner resolves missing receipt and invalid-body status mismatch; rerun unchanged tests against a corrected identity. Tests are not quarantined.

Rerun from workspace root with a new, nonexistent output directory:

```sh
QA_LAB_IDENTITY=/path/to/another-identity.json QA_ARTIFACT_DIR=artifacts/parcel-api/new-run python3 -m unittest discover -s tests -p test_api_parcel.py -v
```

The identity must name the supplied local fixture with role test; tests refuse mismatches and non-loopback targets before mutation.
