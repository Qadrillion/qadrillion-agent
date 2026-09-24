# Focused checks beyond the five specialties

These procedures extend a relevant task; they are not mandatory audits. Shared
test/evidence contracts still apply. Record which operations actually ran.

## Accessibility

Start with the changed journey and applicable requirement. Observe accessible
names/roles/states and the keyboard path: enter without a pointer, reach each
control, operate it, see focus, submit invalid input, recover, and reach the
result. For a dialog, test initial focus, containment where appropriate, Escape
and focus restoration. Check errors are associated with inputs and async status
is exposed without stealing focus. Check zoom/reflow and touch target concerns
when they affect the task. Use the project's scan tool for a pinned page/state;
keep rule IDs, affected nodes and manual reproduction for each finding.

On mobile inspect the platform accessibility tree, focus order and actions;
exercise TalkBack/VoiceOver on the actual supported device when available.
Record OS, assistive technology and version. DOM snapshots and automated scans
cannot establish screen-reader experience or conformance. If no assistive tool is
available, execute keyboard/semantic checks and list the remaining assessment.
Use W3C's [evaluation guidance](https://www.w3.org/WAI/test-evaluate/) and
[Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/) for selection.

## Exploratory sessions

Write a charter as an information question, boundaries, timebox and observation
tools. Example: “Can a user recover an interrupted order without duplicate
charges?” Prepare owned data and record the initial state. Vary one useful
dimension at a time: actor, sequence, input partition, network or lifecycle.
Keep a timestamped trail of actions, observations, evidence and new questions;
do not record only bugs. Follow surprising evidence within the authorized
boundary, then minimize reproduction against an independent oracle.

Debrief: question answered, paths explored, defects versus uncertainties,
blocked observations, cleanup and next charter. Turn stable regressions into
automation; leave discoveries that lack a deterministic oracle as investigation.
The existing [research](../research/qa-practices.md) supplies the session-based
method. A checklist with no observed actions is a plan, not exploration.

## Data and pipelines

Pin input snapshot/schema, transformation/config revision, clock/time zone and
sink. Use a small synthetic corpus with explicit independently calculated
expected rows/totals, including empty input, null/duplicate keys, boundaries,
precision, out-of-order and late data as relevant. Run the actual transformation,
compare schema plus row-level and aggregate invariants, and reconcile source →
accepted/rejected/quarantined → sink counts. Sampling cannot prove reconciliation.

Replay the same batch/event IDs and check the agreed duplicate semantics. Inject
one safe failure in an owned fixture, inspect checkpoint/offset/partial output,
resume and compare with a clean run. Test schema compatibility against the actual
consumer contract. Record watermarks, rejected records and transaction boundary;
do not infer exactly-once effects from an engine setting. Use private team
datasets/tools where configured; cleanup only owned namespaces. No pipeline
stack is certified by the public HTTP fixture.

## Connected devices and BLE

Before radio actions, identify owned hardware/firmware, mobile OS/app build,
adapter, protocol/service/characteristic contract, physical environment and
approved recovery procedure. Discover the actual device and services; do not
invent UUIDs or treat an advertisement name as unique identity. Limit connection
attempts and record permission/radio state and observed protocol errors.

Select transitions: fresh pairing/bonding, reconnect, radio off/on, foreground/
background, out-of-range recovery, stale bond and interrupted transfer. Verify
both app state and device acknowledgement/sequence where observable. A write
accepted by a host API is not necessarily applied by firmware; await the defined
response. Distinguish advertised, connected, discovered, subscribed and confirmed
states. Avoid firmware flashing, factory resets and unsafe actuator actions
without explicit scope and recovery; use a simulator for dangerous fault cases
and label its boundary. Preserve packet/log timestamps and personal-data limits.

Record what cannot run without hardware, radio conditions or a protocol oracle.
Continue API/parser/state-machine checks independently. Android's official
[BLE overview](https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview)
and Apple's [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
are conditional platform references; this framework has not validated physical
BLE execution. New repeated deep pipeline or BLE work may justify another skill;
current evidence justifies focused references, not an empty specialist shell.
