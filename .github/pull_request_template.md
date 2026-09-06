## What and why

<!-- One or two sentences. Link the ticket. -->

Ticket:

## How to review this

<!-- Which file first? Which command runs just the tests you touched? -->

## Checks

- [ ] `./.cursor/hooks/tests/run-tests.sh` passes (if I touched a hook or `guard.conf`)
- [ ] `/golden-tasks run` passes (if I touched a rule, skill or subagent)
- [ ] `python3 tools/tickets/validate.py` passes (if I touched a ticket)
- [ ] No secrets committed (`.env`, `mcp.json`, pools, tokens)
- [ ] The convention that caused any reviewer correction was updated too (not just the file)

## Evidence

<!-- Real output. "It worked locally" is not evidence. -->

```
paste output here
```

## Anything you were unsure about
