# ADR-0004 — Locators are source-grounded, with two proofs
Status: accepted (2026-09-06)

## Context
UI automation dies from locators: XPath copied from an inspector, text
matches that break on translation, identifiers that exist in a branch but
not in the installed build. Agents make this worse — they will invent a
locator rather than stop.

## Options
1. Inspector-derived XPath — rejected: brittle, unreviewable, invisible to the app team.
2. Text matching — rejected: breaks on every locale.
3. **A registry of identifiers, each with a `source_ref` into product source, and two proofs** — chosen.

## Decision
Every locator lives in one registry file with a `source_ref`. Two proofs,
two claims: an offline audit proves the identifier exists in *source*; a live
smoke against the installed build proves it exists in the *build* and stamps
a provenance file. Misses are quarantined, never guessed. A missing
identifier is a product PR, made in the same task, with the registry updated
in the same PR.

## Consequences
Coverage grows at the pace of the product team's identifier rollout. A
verdict stays `Partial` until the smoke resolves the identifiers on a build
that contains them. Content rendered in a separate window (dialog, sheet)
needs its own proof — semantics flags set on the root do not always reach it.

## Revisit triggers
The product ships a test-id convention enforced by its own lint. Then the
offline audit can be dropped; the live proof stays.
