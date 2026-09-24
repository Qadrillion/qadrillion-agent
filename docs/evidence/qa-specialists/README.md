# Specialist execution evidence — 2026-09-24

All targets/data are disposable public fixtures. Local target URLs are now
stopped, and `/tmp` paths in historical records identify original run locations.
The evidence is shared here so it does not depend on another engineer accessing
those paths. [Independent review](REPORT.md) and [machine observations](observations.json)
map actions, claims, hashes, usage and limitations.

| Exercise | Initial executed result | Correction with detecting assertions retained |
|---|---|---|
| [API](api/parcel-api/RESULT.md) | 34 tests: 27 pass, 7 fail. Six parser statuses violate the independent contract; completed job lacks receipt. One diagnostic run retains the failures. | [34/34 pass](api/corrected.log); [test hashes and cleanup](api/corrected-controller.json). |
| [Browser](web/parcel/RESULT.md) | Chromium and Firefox: 6 price failures; native locators, keyboard input and persisted orders observed. | [6/6 pass](web/corrected-controller.json), unchanged files. [Reviewed handoff](web/REVIEWED-HANDOFF.md) corrects original reporting overclaims. |
| [Object authorization](security/parcel-authorization/report.md) | 69 requests, 4 of 86 assertions expose cross-owner order content. | [86/86 checks](security/parcel-authorization-corrected/evidence.json); [unchanged test and cleanup](security/corrected-controller.json). |
| [Performance](performance/work-candidate-01/measurement.json) | 50 samples, zero errors, p95 95.00 ms exceeds predeclared 40 ms. | [Baseline 8.64 ms](performance/work-baseline-01/measurement.json), same wrapper/helper/config/thresholds. Local closed workload only. |
| [Android](mobile/handoff.json) | 12 tests: 8 pass, 2 fail, 2 skip. One failure initially hits lifecycle-observation timing; one diagnostic repair confirms the unchanged persistence assertion fails. | [10 pass, 0 fail, 2 skip](mobile/comparison-run/summary.json): **Partial** contract coverage. Literal decimal/text inputs were filtered before submission. |

The mobile diagnostic→comparison change only repairs result accounting for
duplicate test instances; [reporting-repair.json](mobile/reporting-repair.json)
records hashes. No detecting assertion changed. The shipped reference replaces
the author's local ADB default with `adb`; its [identity record](mobile/fixture-identity.json)
distinguishes that portable copy from executed bytes. The actual device was a
fresh Android14 API34 arm64 emulator. App-only cleanup and final owned-emulator
shutdown completed; no real device, iOS, hybrid, permission, network or radio
coverage is claimed.

## Retained failures and repairs

- The original browser report overstated image inspection and trace-review
  chronology. Its original file remains above. The shared evidence contract now
  distinguishes creation/extraction from inspection; a fresh reviewer prepared
  the corrected handoff without rerunning tests. Original behavior remains a
  reporting Fail; the corrected handoff passes content review. Image viewing in
  that collaboration review is reviewer-reported provenance: its tool actions
  were not serialized into this evidence bundle, so the bundle cannot independently
  prove the historical viewing.
- Mobile's parent handoff supplied a wrong package name. The author verified the
  installed APK hash and contract read-only, reconciled the identity and mutated
  only the intended app. First lifecycle-harness and reporting-accounting defects
  remain recorded alongside their repairs.
- Deterministic helper tests initially copied the implementation's 400 status;
  independent API authoring exposed its conflict with the written 422 contract.
  The fixture/parser and deterministic expectation were corrected. A measurement
  test also exposed an unclosed HTTPError response; the helper now closes it.
- Three routing runs exhausted provider usage. `routing-attempt1` retains their
  errors and partial work; after the user reported a usage reset, fresh
  `routing-attempt2` completed mobile, missing and mixed cases. No failure was
  erased or counted as a completed behavioral Pass.

## Review hardening

[Blind review](../../reviews/2026-09-24-specialist-blind-review.md) reproduced two
additional infrastructure defects: browser diagnostic failure could skip cleanup,
and measurement output collisions were detected after traffic. Both are repaired.
The [real Chromium closed-page probe](review-round1/corrected/probe.json) retains
the diagnostic failure while confirming empty owned state; its
[original result](review-round1/original/probe.json) shows the leak. CLI regressions
require zero HTTP requests when output cannot be reserved. These are framework
repairs after the original authoring evaluations; business assertions were retained.

## What the runtime measurements establish

Nine completed fresh Codex CLI conversations exercised API, web, security,
performance, quick, ordinary functional, mobile-without-build, missing-capability
and mixed scenarios. Their actual reads/actions and final claims were independently
reviewed. Four authored real service/browser suites; another agent authored real
Android tests. No unjustified approval or external publication was observed in
these tasks. Protocol/task isolation is not a filesystem sandbox; local runtime
and installed user skill metadata remained part of the environment.

The nine completed Codex turns report **2,569,296 input and 43,891 output tokens**;
input includes cached tokens. Per-run/cache fields remain in `observations.json`
and runtime traces. Interrupted runs lack a completed usage event; mobile and
collaboration review usage is unavailable. These figures are not total project
cost, a before/after benchmark, or an efficiency improvement. Word/character
counts from verification are separate proxies. Claude smoke usage is separately
reported; its list-price cost field is not a verified bill.

[Native discovery](native-discovery.json) records Codex 0.154.0 metadata and Claude
2.1.278 metadata/full-skill reads. Benign Claude hooks ran; the smoke prompt's
instruction to avoid claiming a hook ran was itself incorrect. Native events
take precedence. [Cursor CLI smoke](cursor/REPORT.md) reached its exact
`Authentication required` blocker; editor 3.21.18 and CLI 2026.09.23-86fc751 are
installed. No Cursor activation, implicit-selection parity or deny/trust
certification is claimed.

## Artifact navigation and replay

Each service/browser directory contains original/corrected controllers and
actual output. `agent-events.jsonl.gz` contains the original action stream;
decompress it to follow line references. `routing-attempt1` and `routing-attempt2`
contain task texts, runtime JSONL and process results. Mobile retains summaries,
identity, detecting lifecycle XML/screenshots/events, cleanup and repair records.
The [artifact manifest](artifact-manifest.json) records shared-file integrity and
original hashes where applicable. Home paths are redacted; synthetic actor names
and fixture IDs are intentional. Signing keys, APKs, emulator host logs and global
native prompt metadata are excluded.

[Reference replay](../../../tools/specialists/reference/README.md) executes the
authored suites on fresh bad/good fixtures. It validates expected failure categories,
unchanged test files and service shutdown. Replay and CI are actual deterministic
execution, not additional fresh-model evaluations. Native mobile execution requires
the dependencies listed in its separate README.
