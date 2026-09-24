# Contributing

Changes to `main` land through a pull request. The `governance` check has to pass. Force-push and branch deletion are blocked on `main`.

## Before you open the PR

- [ ] `./.cursor/hooks/tests/run-tests.sh` passes if you touched a hook or `guard.conf`
- [ ] `python3 tools/tickets/validate.py` and `python3 tools/tickets/index.py --check` pass if you touched a ticket
- [ ] No secrets: `.env`, `.cursor/mcp.json`, keys, tokens, pools
- [ ] The pull request template is filled in, including real command output

A written "never …" is not a fix. If a behaviour must always or never happen, it belongs in `.cursor/hooks/guard.conf` or a hook test.

## Reporting

Bugs and questions: [open an issue](https://github.com/Qadrillion/qadrillion-agent/issues/new/choose).

A hook bypass, a credential leak, or anything that would let an agent act on production: see [SECURITY.md](SECURITY.md). Do not file that in public.

Behaviour toward other people: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report it to hello@qadrillion.com.
