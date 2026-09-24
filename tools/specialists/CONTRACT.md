# Disposable parcel service

This is a public synthetic evaluation fixture, not a secure application or a
suggested architecture. `lab.py --help` starts a new memory-only service on a
random literal loopback port and writes its identity to a new JSON file.
Run one process per evaluation, send Ctrl-C on completion, verify it exited and
the port closed. Never point these helpers at company infrastructure.

`GET /__identity` returns fixture, role, run_id, build hash, mode and URL.
`X-Lab-Actor: alice` or `bob` represents two synthetic actors; it is intentionally
not real authentication. Missing/unknown actors receive 401 on data routes.
All responses are JSON except the HTML page at `/`.

| Operation | Required behavior |
|---|---|
| POST /orders | JSON object with only `quantity`, integer 1..100 (not bool); invalid input 422. `Idempotency-Key` 1..128 chars required (400 otherwise). New: 201 with id, owner, quantity, total_cents = quantity × 500. |
| Repeat POST /orders | Same actor/key/input: 200 with same object, one persisted order; changed input with same key: 409 and original state unchanged. Actors have independent keys. |
| GET /orders | 200 list of caller-owned orders only. |
| GET /orders/{id} | Own: 200 full object; absent or other actor: 404. |
| DELETE /orders/{id} | Own: 200 deleted ID; absent/other actor: 404; no other data changed. Removes associated idempotency entry. |
| POST /jobs | Body only `order_id` owned by caller; 202 with id and pending state, other/absent: 404. |
| GET /jobs/{id} | Owner sees pending then complete within 2 seconds. Other/absent: 404. |
| GET /receipts/{job-id} | Owner: 404 while pending; after complete, 200 with job_id, order_id, delivered true. Other/absent: 404. Completion promises this side effect. |
| DELETE /jobs/{id} | Own: 200 deleted ID, removing job and derived receipt; other/absent: 404. |
| GET / | Quantity-labelled input, Place order button. Successful action renders `N parcels — $X.XX`, Order saved status, enabled button. UI receipt must match persisted order. Keyboard must reach/operate controls. |
| GET /work | 200 with `{"ok": true}`; synthetic measurement operation, no business data. |

The evaluator controls target variants. Workers receive the contract and target
identity, not the evaluator's answer key. Test authoring must use the independent
contract. Correcting a fixture means running the same tests against a new pinned
target; do not edit assertions to match observed defects.

`measure.py --identity <ready.json> --out <new-result.json>` is a bounded
closed-workload reference helper. It verifies the exact lab identity, disables
proxies/redirects, retains warmup and raw samples, checks business responses and
returns 1 on thresholds/incomplete workload. Configure thresholds **before** the
comparison. Error stops can leave up to concurrency−1 already-started requests;
in-flight requests finish within timeout. A small local run does not estimate
production capacity. Other products use their existing load tools.
