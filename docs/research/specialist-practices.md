# Research translated into specialist execution

Inspected 2026-09-24. This extends [the existing register](qa-practices.md), rather
than restarting its source count. Related documentation pages are grouped as
source families, not presented as independent studies. These are inspected
sections/pages, not claims to have read books or validated every tool version.
The [mobile register](mobile-specialist.md) records that specialist's sources.

| Inspected primary material | Decision and trade-off | Implementation |
|---|---|---|
| [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html), §§9.2.1–9.2.2 and 15.3.3 | Idempotency concerns intended server effects; responses may differ. A 202 is nonterminal. Reconcile uncertain writes before retrying; bounded polling checks the promised effect. | API skill, jobs/receipts and actor-scoped idempotency fixture. |
| [OpenAPI specification](https://spec.openapis.org/oas/latest.html), inspected Operation/Responses/Response/Schema and dialect sections; page displayed 3.2.1 | Use the project's contract version and validator dialect. Shape checks need business/state oracles; a schema alone cannot prove authorization. Research version is not a forced upgrade. | API contract matrix and negative/boundary authoring procedure. |
| [OWASP WSTG v4.2 ATHZ-04](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References/), objectives and procedure, reused from prior research | Two controlled actors and their own objects support allowed and denied controls without probing strangers' data. Verify returned content and resulting state. The narrow check says nothing about other attack categories. | API/security composition and seeded unauthorized object read. |
| [NIST SP 800-115](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf), §§6.3, 6.5 and incident handling in 7.1–7.2 | Explicit targets, exclusions, permitted techniques, limits, data handling and stops before security execution. Carry existing authorization forward. This is 2008 methodology, not current tool guidance; the framework additionally excludes production. | Security scope record, bounded test selection, cleanup and incident stops. |
| [Python urllib.request](https://docs.python.org/3/library/urllib.request.html) Request/urlopen/handlers/examples and [urllib.error](https://docs.python.org/3/library/urllib.error.html) HTTPError | Stdlib is a useful dependency-free reference, not a language mandate. Negative responses have readable status/body. Timeout is a blocking-operation bound, not a whole-task deadline. Connection-close HTTP/1.1 affects latency comparison. | Conditional API recipe, loopback identity client and measurement limits. |
| Playwright [tests](https://playwright.dev/docs/writing-tests), [locators](https://playwright.dev/docs/locators), [fixtures](https://playwright.dev/docs/test-fixtures), [authentication](https://playwright.dev/docs/auth), [trace viewer](https://playwright.dev/docs/trace-viewer-intro) and [trace options](https://playwright.dev/docs/api/class-testoptions#test-options-trace) | Observe locators, await conditions and isolate server data as well as browser contexts. Stored auth state is sensitive. Use retries 0 and retain-on-failure tracing: common first-retry examples miss the first failure under our evidence policy. Trace value must be balanced with artifact sensitivity. | Web authoring/debugging recipe and real browser exercise. |
| Grafana k6 [API load testing](https://grafana.com/docs/k6/latest/testing-guides/api-load-testing/), [open/closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/), [thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/), [dropped iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/) and [graceful stop](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/graceful-stop/) | Model arrivals versus concurrency explicitly. Closed workloads slow their own arrivals; open workloads can drop scheduled iterations. Checks need thresholds for failing exit status. Abort timing must allow useful samples while bounding harm. No universal p95 or workload is inferred. | Performance skill and conditional k6 adaptation; local bounded helper reports a closed workload. |
| [Google SRE monitoring](https://sre.google/sre-book/monitoring-distributed-systems/), black/white-box signals, tails and measurement resolution; [USE Method](https://www.brendangregg.com/usemethod.html), both reused | Correlate errors, business outcomes, latency distribution and resource utilization/saturation/errors. Fast errors can improve average latency misleadingly. Unknown telemetry stays unknown. | Performance raw samples, successful/all-request distributions and investigation procedure. |
| W3C [Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/), keyboard/focus, forms, contrast/zoom, plus prior evaluation overview | Perform a relevant journey through keyboard and semantic checks; an automated scan or initial review is incomplete conformance evidence. | Focused accessibility reference and browser keyboard exercise. |
| Android [BLE overview](https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview), central/peripheral roles, discovery/services and connection; Apple Core Bluetooth landing page retrieval returned only a JavaScript shell | Pin roles and observed service/characteristic identity; distinguish host submission from device effect. Android docs support the conditional path; Apple content was not substantively retrieved here. | Focused BLE reference; no physical radio or iOS Bluetooth execution claim. |
| OpenAI [skill evals](https://developers.openai.com/blog/eval-skills), scenario definition, execution traces and deterministic graders; [skills](https://learn.chatgpt.com/docs/build-skills) and [developer commands](https://learn.chatgpt.com/docs/developer-commands) | Grade actions/artifacts, not plausible final prose. Separate native discovery from instruction copies. Use installed CLI help before relying on flags; blog examples can lag. Usage events are actual runtime measurements, word counts are proxies. | Isolated task materialization, retained events, explicit runtime support matrix. |

The attempted k6 average-load-testing page failed twice and was excluded. No
commercial book, inaccessible content or search snippet contributes substantive
evidence. Local sample thresholds are evaluator choices fixed before comparing
variants; they are not recommendations for arbitrary company services.

## Architecture consequences

The shared workflow keeps independent oracles, progressive retrieval and failure
retention. Surface skills hold specialist execution decisions. Tool-specific
recipes load only after observing the actual runner. Security/performance are
selected overlays rather than obligatory phases. Existing roles remain useful
work boundaries; multiplying agents would duplicate context without adding a
new capability. Accessibility/exploration/data/BLE remain focused procedures
until real repeated work justifies deeper independent execution packages.

Research informs design; [evaluation evidence](../reference/specialist-support.md)
determines what actually ran. Neither proves broad autonomous effectiveness,
company compatibility or universal token savings.
