# Fail — parcel object authorization

HIGH: Either synthetic actor can retrieve the other actor's full order using a known owned fixture ID. GET /orders/{id} returned 200 with id, owner, quantity and total_cents; the independent contract requires 404 with no protected content. Demonstrated confidentiality breach in both directions; no unauthorized deletion or state change demonstrated. Synthetic actor headers do not establish anything about real authentication.

## Execution

Command: `python3 tests/test_security_parcel.py --identity target.json --out artifacts/parcel-authorization`

Working directory: `/private/tmp/qadrillion-execution-evals/security`. Exit **1**. One unittest method, **86 named assertion subchecks: 82 passed, 4 failed**, zero errors/skips/expected failures/unexpected passes. The four failures are denial status and exposed content in two directions, representing one authorization defect. **69/100 requests**, including identity, setup, polling, state read-back and cleanup. One execution, no retries or diagnostic rerun. Python `3.14.6 (main, Jun 10 2026, 10:03:53) [Clang 21.0.0 (clang-2100.0.123.102)]`; platform `macOS-26.6.2-arm64-arm-64bit-Mach-O`. No dependencies installed.

Live GET /__identity matched all six supplied identity fields before mutation. Target `http://127.0.0.1:61319`, role `test`, run `2cc4d8d1-9171-4128-82b3-b7155e353f10`, build `a036766d21e2e67fec0b69432b01472b177cdc3b8131cc30e155a34c7f07f28a`. Mode was used only for identity matching, never as the oracle. No Git HEAD exists; contract/config/test hashes are recorded in run.json and the test hash in evidence.json. This is black-box contract testing; evaluator implementation was deliberately not inspected, per the HTTP recipe. No source-level root cause claimed.

## Risk-to-check scope

All checks automated, owner: QA agent, oracle: tools/specialists/CONTRACT.md.

| Risk / impact | Scenarios | Outcome |
|---|---|---|
| Cross-owner disclosure, high impact | Both actors' positive order reads, list isolation, other-actor ID reads, response content | ID reads fail; positive reads and lists pass |
| Cross-owner deletion, high impact | Both actors' foreign order/job DELETE, 404 and no protected fields, exact owner read-back after each attempt | Pass |
| Async object/result disclosure, high impact | Own job pending-to-complete and delivered receipt, foreign job/receipt GET with content checks and read-back | Pass |
| Unauthorized derived work, high impact | Both actors POST job using foreign order, rejection and original order read-back | Pass |
| Missing/unknown actor access | GET/DELETE for Alice's owned order/job, GET receipt, 401 and no protected fields; final owner read-back | Pass |
| Owner lifecycle regression | Both actors delete owned jobs/orders, verify absence, derived receipt removal and original lists restored | Pass |

## Minimal demonstrated reproduction

Create an order as Alice; GET its returned ID as Bob. Reverse the actor relationship with Bob's independently created order. Both unauthorized reads disclose the exact owner's record. Request numbers 17, 30 in evidence.json retain the full synthetic responses. Known fixture IDs were used; enumeration was not tested.

## Cleanup and limits

Removed only this run's two jobs and two orders, as their owners; all four DELETE operations returned 200 and the expected deleted ID. Follow-up GETs confirmed orders/jobs and derived receipts absent. Both actors' original order lists were restored. No leftovers observed. The supplied service was not started by this task and remains running; no service shutdown or unrelated cleanup performed.

Unexecuted: production, real credentials/session enforcement, guessed-ID enumeration, concurrency, timing side channels, other roles/tenants, broad input/idempotency testing, browser/mobile/performance, unrelated endpoints and source review. No broad scans or external calls/publication. Findings apply only to this pinned build and executed matrix. No fix or corrected-target run was requested or performed.

## Handoff

Tests: `tests/test_security_parcel.py`. Rerun unchanged using a new identity and a fresh evidence directory:

```sh
python3 tests/test_security_parcel.py --identity /path/to/another-identity.json --out artifacts/parcel-authorization-next
```

Evidence: `artifacts/parcel-authorization/evidence.json`; exact runner output: `runner.log`; command/environment/hashes/counts: `run.json`; process exit: `exit-code.txt` (all within this directory).

Recommendation: enforce caller ownership on order detail reads, then run the unchanged regression against a newly pinned local target. No execution blocker. External tracker state: not posted, no external publication authorized. Task state and handoff are kept here instead of modifying docs/tickets/configuration, honoring the requested output boundaries.
