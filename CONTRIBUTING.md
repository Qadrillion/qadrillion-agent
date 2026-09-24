# Contributing

Changes to `main` land through a pull request. The `governance` check has to pass. Force-push and branch deletion are blocked on `main`.

## Before you open the PR

- [ ] Edit maintained `.cursor` sources, then run `python3 tools/agents/sync.py`; do not hand-edit generated runtime copies
- [ ] `python3 tools/verify.py` passes (the same offline checks as CI)
- [ ] After behavioral instruction changes, run `/golden-tasks run` in fresh isolated agents and record actual outcomes; do not substitute keyword checks
- [ ] No secrets: `.env`, `.cursor/mcp.json`, keys, tokens, pools
- [ ] The pull request template is filled in, including real command output

Add regression evidence for the actual failure. Hooks are defense in depth:
document which events and payloads are covered, and do not present regex checks
as a sandbox. Native runtime smoke and connected-product tests are separate from
offline verification. Report unavailable checks explicitly.

Public contributions must contain only generic code, instructions and sanitized
fixtures. Company ticket state, target details and evidence stay in the team's
private workspace. See [team upgrades](docs/reference/team-workflow.md).

## Reporting

Bugs and questions: [open an issue](https://github.com/Qadrillion/qadrillion-agent/issues/new/choose).

A hook bypass, a credential leak, or anything that would let an agent act on production: see [SECURITY.md](SECURITY.md). Do not file that in public.

Behaviour toward other people: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report it to hello@qadrillion.com.
