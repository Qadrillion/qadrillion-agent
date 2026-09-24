# Security

This repository is an agent layer you run locally. It does not operate a service, and it does not send telemetry.

Hooks inspect selected runtime events and recognizable payload patterns. They are
not a sandbox, an authorization service or a guarantee that every tool is covered.
Use scoped credentials, runtime-native permissions, target identity verification
and appropriate environment/network restrictions. Trust and event coverage differ
by agent and version; see [runtime support](docs/reference/runtime-support.md).

## Report a vulnerability

Use [private vulnerability reporting](https://github.com/Qadrillion/qadrillion-agent/security/advisories/new) on GitHub, or email hello@qadrillion.com.

Do not open a public issue for any of these:

- a hook that should have denied a command and did not
- a path that reads credentials the guard is supposed to block
- anything that would let an agent target production or push a secret into the repo

Include a sanitized payload, runtime/version, hook output and expected decision.
Use disposable fixtures; do not reveal secrets or demonstrate impact against
production. A model refusing in prose does not prove a native hook executed.

## What happens next

We acknowledge the report, confirm whether the hook or the config is the gap, and ship the fix through a pull request with a golden payload that fails before the fix and passes after it. We do not ask you to prove impact against a real production system.
