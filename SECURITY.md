# Security

This repository is an agent layer you run locally. It does not operate a service, and it does not send telemetry.

## Report a vulnerability

Use [private vulnerability reporting](https://github.com/Qadrillion/qadrillion-agent/security/advisories/new) on GitHub, or email hello@qadrillion.com.

Do not open a public issue for any of these:

- a hook that should have denied a command and did not
- a path that reads credentials the guard is supposed to block
- anything that would let an agent target production or push a secret into the repo

Include the command you ran, the hook's stdout, and the file you believe should have stopped it. A model refusing in prose is not evidence. The fence is the hook.

## What happens next

We acknowledge the report, confirm whether the hook or the config is the gap, and ship the fix through a pull request with a golden payload that fails before the fix and passes after it. We do not ask you to prove impact against a real production system.
