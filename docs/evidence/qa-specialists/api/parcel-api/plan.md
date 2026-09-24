Scope: api. QA entry point qa; specialist qa-api; sequential author/executor/reviewer roles. Black-box only, no product source inspected. All tests automated using stdlib unittest. No external publication.

| Risk / impact | Scenario | Oracle | Evidence |
|---|---|---|---|
| Incorrect charges / high | Quantity limits, exact totals and read-back | CONTRACT.md integer 1..100, quantity × 500 | HTTP trace + unittest |
| Invalid state / high | Missing/null/type/extra-field/malformed inputs; key lengths | 422 or 400; unchanged list | HTTP trace + isolated cases |
| Duplicate effects / high | Identical retry, conflicting retry, fresh key, actor key namespaces | 200 same object, 409 unchanged, distinct new resource | HTTP trace |
| Data loss / high | Delete, key reuse, preserve another record | 200, absence, recreated key accepted | HTTP trace + cleanup |
| False completion / high | Poll pending to complete; inspect receipt and unchanged order | Complete within 2 seconds; delivered receipt | Timed HTTP trace |

Source/build: live identity must exactly equal supplied JSON before mutations. Mode is identity only. Baseline lists are retained; cleanup only IDs returned from this run's writes, jobs before orders, with final baseline comparison. Transport failure never retries a write. Test run evidence uses separate directories; existing evidence cannot be overwritten.

Contract does not specify error object schema, malformed job-input status, unknown method status, or extra job fields, so these are not invented assertions. Actor key namespaces are functional idempotency coverage, not security assessment. UI, security, performance and implementation review excluded. Workspace is main with no HEAD commit; Python 3.14.6; configured runners/repositories empty. User's artifacts-only instruction supersedes ticket/docs state writes.
