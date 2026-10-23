# Provider-neutral source publication — 2026-10-23

Branch: `chore/provider-neutral-setup-2026-10-23`; base: verified remote `main`
at `d91545d8f593ddd934b69d7a2618e58c223830f2`. Work remains uncommitted pending
fresh publication review. This record describes this clean candidate only.

## Scope

Move maintained rules, skills, roles and hooks into `.agent`, independent of an
editor. Codex/Claude skill directories link to one maintained source; native
role/hook formats remain generated. An optional `.cursor -> .agent` alias keeps
old skill/role/hook paths. Update native consumers, offline tooling and active
guidance to use neutral paths and Markdown rule metadata.

Copied-skill adoption verifies normalized paths, exact prior hashes and modes,
rejecting unknown edits or collisions before mutation. Staged transactions
preserve renamed originals until the final ledger commit, support rollback and
resume after interruption, and retain failed cleanup evidence without blocking
the committed installation.

## Excluded work

The migration was reconstructed on committed source. It excludes earlier
unfinished Cursor-import event/matcher compatibility, checkpoint re-arm logic,
expanded automatic-handover prose, their test cases and their local session
records. Existing shared policy and checkpoint behavior come from the committed
base with path substitutions only. No dependency on that unfinished work is
required for the neutral-source migration.

## Verification

- `python3 -B -m unittest discover -s tools/tests -p test_agents.py`: 49 PASS.
- `python3 -B tools/verify.py`, with the optional `.cursor` alias removed:
  154 framework + 14 mobile tests, 75 guard payloads, ticket schema/index,
  document links, generator drift and offline doctor PASS. Alias restored.
- `git diff --check`: PASS. Prior-work exclusions checked against committed
  source, including checkpoint behavior, matcher, adapter, tests and guidance.
- Fresh independent publication review is pending. Earlier mixed-checkout
  test/review results are not evidence for this candidate.
Native discovery/trust/readiness, authenticated provider continuation, actual
power loss, disk exhaustion and other operating systems remain unverified.
No live provider, customer data or production execution belongs to this change.
