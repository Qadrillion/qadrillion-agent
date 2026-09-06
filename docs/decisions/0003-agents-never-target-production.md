# ADR-0003 — Agents never target production; release is a human action
Status: accepted (2026-09-06)

## Context
Test runners, seeding scripts and repro scripts all take an environment
selector. A config file that names a remote target cannot tell you it points
at production: one project ran every "dev" push against the published
storefront for two months because two environment IDs were inverted, and the
file was internally consistent and wrong.

## Options
1. Trust the environment file — rejected: it was wrong for two months.
2. A rule "never run against prod" — rejected: prose (ADR-0001).
3. **Three fences**: hook denies prod selectors on any test verb; scripts call a staging guard before authenticating; targets are read from the provider's own API before an agent may act — chosen.

## Decision
`guard-shell.sh` denies any command that matches a test verb *and* a
production selector, and any environment variable set to `prod`. Every
mutation script calls the staging guard first. Any config that names a
remote target (theme, environment, database, project) is verified against
the provider's answer (`role`, `is_production`, hostname) before use.
Production checks and releases are done by a person.

## Consequences
Add your real production hostnames to `PROD_SELECTORS` in `guard.conf`; the
generic `prod|production` token catches config names but not a bare URL.

## Revisit triggers
A read-only production smoke that an agent may run appears as a requirement.
Then: a separate, explicitly named read-only path, still fenced by verb.
