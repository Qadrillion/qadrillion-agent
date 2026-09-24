# Surface guidance

Read only sections relevant to the risk. These are prompts for investigation,
not claims that a particular runner or connector is installed.

## API and backend

Check contract/status/error shape, boundary inputs, authorization by actor and
owned object, persistence, retries/idempotency, concurrency and rollback. For
async jobs inspect completion and business state, not just acceptance. Correlate
logs/traces when available; a 2xx with wrong content is still a failure. Existing
language-native tests, command clients and collection runners are all valid.

## Web

Inspect actual DOM and accessibility semantics. Prefer role/name and explicit
stable test IDs; control locale when visible text is the contract. Check routing,
keyboard/focus, errors/loading/recovery, browser/device variation relevant to users.
An automated accessibility scan is only the scanned-rule result; knowledgeable
manual/assistive-technology evaluation is needed for a conformance assessment.
Use the team's Playwright, Cypress, Selenium, browser or manual tooling.

## Mobile and desktop

Pin OS/device/app build, permissions, installation/update path, lifecycle,
background/foreground and network state. Inspect accessibility trees and native
identifiers where available. Check platform-specific navigation/input and storage.
Real devices, emulators/simulators, native harnesses, Appium, Maestro or manual
sessions supply different evidence; state which was exercised.

## Devices and connected products

Pin firmware/hardware/app/protocol versions and physical prerequisites. Consider
pairing, reconnect, stale state, interrupted updates, degraded radio/network and
recovery. Simulator results do not establish physical-device behavior. Do not
invent attached hardware; block only the hardware-dependent checks. Product
safety limits and recovery procedures must come from the team.

## Data and pipelines

Check schema evolution, nulls/duplicates, ordering, reconciliation, time zones,
precision, late events, replay/idempotency and failure recovery where relevant.
Use synthetic permitted data and independent totals/invariants; sampled rows do
not prove every record. Pin source snapshot and processing/config versions.

## Security, reliability and performance

Select explicit authorized scope. For object authorization use separate actors
and resources, including denied outcomes and resulting state. One security test
is not a security assessment. For performance define workload, threshold,
environment and baseline; examine tail latency, errors, utilization/saturation
and unknown measurements. An unmeasured optimization is not a verified improvement.
Stress/load and destructive recovery experiments require an isolated approved
non-production target and its cleanup plan.

## Unlisted products

Describe interfaces, state transitions, dependencies, highest-impact failures,
control/observation available and an oracle. Apply the shared workflow with
`scope: other`; extend this reference only when a repeatable need is established.
