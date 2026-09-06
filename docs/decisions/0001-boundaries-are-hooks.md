# ADR-0001 — Boundaries are hooks, conventions are rules
Status: accepted (2026-09-06)

## Context
An instruction inside the context window is a suggestion the model weighs
against everything else. A hook is a program outside the loop that can refuse
the call. Setups that grow by accumulation end up with every safety-relevant
sentence in `AGENTS.md` ("always confirm before posting", "never run against
prod"), where it competes for attention with everything else and loses
exactly when the context is fullest. In field testing, a frontier model
refused a force-push on its own but ran `git reset --hard` on polite request
and attempted an `.env` read without hesitation — vendor safety training
tracks vendor-chosen harms, not yours.

## Options
1. Keep boundaries in prose, rely on the model — rejected: probabilistic by construction.
2. User-level hooks in `~/.cursor/hooks.json` — rejected as the only layer: they never reach cloud agents or other machines.
3. **Committed project hooks** in `.cursor/hooks/` with a payload test per fence — chosen.

## Decision
Anything that must always or never happen lives in `.cursor/hooks/` and is
committed. Rules and `AGENTS.md` describe conventions and point at the hook.
Every fence has a golden payload in `tests/run-tests.sh`; the tests run in CI.
The same scripts are registered for Claude Code through `.claude/settings.json`.

## Consequences
Prose gets shorter. A fence that cannot spawn (missing executable bit,
missing interpreter) locks the agent out under `failClosed` — that is correct,
and CI asserts the bit. Match the action, not one spelling of it: package
scripts, wrappers and aliases are the same action.

## Revisit triggers
The harness ships a native permission system with per-repo, committed,
testable rules. Until then, this stands.
