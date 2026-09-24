# ADR-0006 — Portable evidence and explicit runtime boundaries
Status: accepted for the public-framework upgrade (2026-09-24)

## Context

Company-specific practices had become universal requirements: source-backed test
IDs, cloud-owned collections, staging-only names, fixed runners and tracker fields.
Public adopters need the same quality of evidence without the same stack. Hooks
also cover only supported runtime events and recognizable payloads, not all ways
an agent or subprocess can act.

## Decision

Keep shared contracts and runtime adapters. Select available capabilities and
test the exposed behavior when source or automation is unavailable. Use observed
semantic locators/test IDs with source provenance when available; do not invent
identifiers or confuse source with deployed-build proof. Configured commands and
connections are declarations, not evidence that an integration is installed.

Use runtime-native permissions, scoped accounts and verified target identity
alongside hooks. Publish only under applicable user authorization and native
permissions; never use a model-supplied approval marker. Carry authorization
through the task without repeated per-file or routine-report approvals. Default
hooks target recognizable destructive operations, production tests and credential
disclosure. Ordinary tool writes rely on task scope and native permissions;
organizations may opt into stricter hook gates. If an action still requires a
native approval unavailable in that runtime, retain its local draft. Production
execution remains out of scope under ADR-0003.

Failing criteria mean Fail. Missing required evidence/coverage means Partial.
Pass is scoped to the agreed executed checks. Preserve historical runs across
build changes and provide one owner/branch/next action for handoff.

## Supersedes

ADR-0001's claim that every boundary can be made deterministic by a command regex
is replaced by the explicit coverage/defense-in-depth contract. Its single-source
and payload-regression principles remain. ADR-0004's mandatory source registry
and prohibition on semantic/text locators are replaced by observed-interface
evidence. Its distinction between source and installed-build evidence remains.

## Consequences

More setups can complete useful QA with honest limitations. Native hook activation
and auth still need per-machine observation. Research-backed instructions and
synthetic behavior evaluations improve decision quality; they do not establish
universal product coverage or a measured automation percentage.
