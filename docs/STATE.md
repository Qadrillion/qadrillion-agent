# State — Qadrillion Agent

Updated: 2026-10-23. Branch: `chore/provider-neutral-setup-2026-10-23`.
Base: `d91545d` (verified remote `main`). Changes uncommitted pending review.

## Current task

- Publish only the provider-neutral source migration from a clean base.
  Earlier unfinished Cursor-import and checkpoint/handover refinements are
  excluded; the original checkout and its existing work remain separate.
- `.agent` owns rules, skills, roles and hook policy. Native skill entrypoints
  link to that source. Native role/hook formats remain generated. The optional
  `.cursor -> .agent` alias preserves old skill/role/hook paths; neutral Markdown
  rules do not claim historical native Cursor `.mdc` discovery.
- Ledger paths are normalized before adoption. Generated-copy migration stages
  output, renames originals to recoverable backups and commits its ledger last.
  Errors roll back; interrupted work recovers on the next normal invocation.
  Read-only checks report pending recovery without writing.

## Evidence and next action

- Full offline run before the publication-review correction: 154 framework +
  14 mobile tests, 75 guard payloads, schema/index, document links, drift and
  doctor PASS with the optional `.cursor` alias removed, then restored.
- Publication review found recovery backups were not Git-ignored. Added exact
  root ignore patterns for transaction, staging and retained-completion folders.
  Recovery artifacts are preserved. Updated generator/adapter suite: 51 PASS;
  new fixtures verify ignored pending/staging/retained backups, `git add --all`
  exclusion, preserved unrelated synthetic config and valid recovery/`--check`.
  `git diff --check` PASS. Fresh re-review is pending; live checks are separate.
- No authenticated runtime or connected-service execution is part of this change.
  Native discovery/trust/readiness and Codex–Claude continuation require separate
  observation in the exact task checkout with account access available.
- Main requires a pull request and the `governance` check. Do not commit or push
  this candidate before its fresh publication review and coordinator instruction.
- See [publication record](sessions/2026-10-23-provider-neutral-publication.md).
