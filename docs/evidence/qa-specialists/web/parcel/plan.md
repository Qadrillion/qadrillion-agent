Scope: ui-web; QA → qa-workflow → qa-web and keyboard slice. Black-box; no service source inspection, response interception, API suite, load/security testing, or publication. No source commit exists in this disposable workspace. User output restriction supersedes normal ticket/docs state writes; LOCAL-1 evidence resides here.

| Risk / impact | Automated check | Independent oracle |
| --- | --- | --- |
| Incorrect customer price / high | quantity 3 receipt + persisted order | 3 parcels cost $15.00 |
| Keyboard unusable or validation bypass / high | Tab, keyboard entry, Enter; 0, 101, fractional, empty; recovery to 100 | native constraint rejection, no order; 100 costs $500.00 |
| Boundary price / medium | minimum quantity 1 | $5.00 |
| State loss or contamination / high | readback after reload, tracked response IDs, teardown and baseline comparison | order persists; only owned orders deleted |

Owner: local QA agent. Both installed engines launch successfully. Observed locators and runtime identities: observation.json. Receipt is initially hidden; section accessible label observed in DOM, uniqueness checked after submission. Fresh context per test; one worker; no retries; supplied target dedicated to this task. API limited to identity, fixture readback and cleanup. First deterministic Chromium case precedes remaining matrix. Traces, screenshots, browser errors and network status retained. Tests parameterized by QA_IDENTITY; no target-specific expected defect.
