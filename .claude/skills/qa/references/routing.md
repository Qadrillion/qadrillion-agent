# Select only needed procedures

Route by the requested behavior and the interfaces that must be exercised,
not incidental words, repository language or the availability of a tool. Do
not scan the entire skill tree. Paths below are relative to the workspace root
and point to maintained content; runtime-generated counterparts are equivalent.

| Actual work | Load | Boundary |
|---|---|---|
| HTTP/API contract, service integration, async job or API automation | `.cursor/skills/qa-api/SKILL.md` | A backend/data task with no HTTP surface uses the shared workflow and its applicable reference. |
| Browser behavior or authoring/debugging browser automation | `.cursor/skills/qa-web/SKILL.md` | A ticket mentioning a URL or a documentation question is not browser execution. |
| Android/iOS app behavior, native/hybrid automation, device lifecycle | `.cursor/skills/qa-mobile/SKILL.md` | Desktop apps do not become mobile because they share a language. |
| Explicit security testing, or changed object access, roles/tenancy, untrusted input handling or sensitive-data boundaries that justify a security check | `.cursor/skills/qa-security/SKILL.md` plus relevant interface | Select a bounded risk slice. A normal login fixture or routine positive permission assertion does not require a full security procedure. |
| Explicit performance/load task or latency/throughput/resource regression with a measurable question | `.cursor/skills/qa-performance/SKILL.md` plus relevant interface if needed | Functional waits, a spinner, or the word “fast” are not reasons to generate load. |
| Multiple actual interfaces | Each needed surface skill, plus justified overlays | One plan, fixture ownership and report. Share a business oracle and correlation IDs; avoid redundant checks at every layer. |
| Keyboard/focus/semantics or accessibility requirement | `docs/reference/focused-checks.md` accessibility section, plus interface | Scanning is partial evidence, not WCAG conformance. |
| Exploratory mission, data transformation or hardware/BLE | Relevant `docs/reference/focused-checks.md` section | No generic “all specialties” fallback. Hardware limits stay explicit. |

Examples are decisions, not a keyword classifier: “explain API idempotency” is
a quick answer; “test retries on the API” loads API; “test cross-tenant invoice
access” loads API + security if the interface is HTTP; “test checkout receipt in
the browser and persisted API order” loads web + API; “measure API p95 under a
bounded workload” loads API + performance; “test mobile offline draft recovery”
loads mobile. Reassess only if new evidence changes the scope.

Identify the configured/installed runner before opening its tool recipe. Existing
project conventions win over an example stack. No source: execute black-box
checks with an independent oracle. No automation: use an available manual/control
path and retain its evidence. No live target: author reviewable runnable tests
against a supplied contract, run independent local checks, and mark target
execution not run. Missing source, IDs, optional plugins or telemetry do not
justify invented observations or blocking unrelated authorized work.
