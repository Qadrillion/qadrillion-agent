[Qadrillion Agent](../../../README.md) / Reference suites

# Run tests that detect known defects

Replay API, security, performance and optional browser tests against disposable
local targets. No model account, tracker or company system is needed.

| Path | Prerequisites | Expected coverage |
|---|---|---|
| HTTP reference | Python 3.11+; macOS/Linux workspace | Six defective/corrected outcomes across API, security and performance |
| Browser reference | HTTP prerequisites, Node.js/npm and installed Playwright browsers | Eight outcomes including real Chromium and Firefox |
| [Native Android](../mobile/README.md) | Android SDK, JDK and an owned emulator | Separate device replay; not part of the commands below |

## Run the HTTP suites

Run from the repository root. Choose a previously nonexistent output directory:

```sh
python3 tools/specialists/replay.py --out /tmp/qa-reference-new
```

## Include Chromium and Firefox

Install the optional pinned stack; the subshell keeps your working directory at
the repository root. Browser installation may also require OS dependencies on
Linux; use Playwright's reported dependency instructions for that machine.

```sh
(
  cd tools/specialists/reference/web
  npm ci
  npx --no-install playwright install chromium firefox
)
python3 tools/specialists/replay.py --web --out /tmp/qa-reference-browser-new
```

## Read the result

Open `replay.json` in your output directory. Every record must have
`verified_expected_outcome: true`, unchanged test hashes and completed cleanup.
Each run folder retains `run.json`, `output.log` and its test artifacts.
The replay exits zero only if all expected outcomes and cleanup checks pass.

**Defective variants should fail their test subprocess.** That retained failure
is the evidence of detection; it does not mean the product behavior passed.
Unexpected outcomes, infrastructure problems or incomplete work make the replay
exit nonzero. Diagnose them before starting a separately identified run.

## What this proves

These tests were authored/debugged by fresh agents using the specialist skills
against real local targets. Original failures and corrected execution are in the
[specialist evaluation record](../../../docs/evidence/qa-specialists/README.md).
The files retain their final authored business assertions; the replay controller
provides fresh identities and fixture variants. Blind review subsequently
hardened browser teardown so failed diagnostics cannot skip owned-data cleanup.
A closed-page regression retains its failure while proving cleanup; original
authored bytes/hashes remain in the evaluation evidence.

This replay executes already-authored tests. It is not a fresh model evaluation;
[the evaluation guide](../EVALUATING.md) covers that separate workflow.
Performance budgets characterize the local fixture, not production capacity.
CI contention can produce a recorded threshold failure requiring diagnosis.

## Artifacts and cleanup

The controller creates memory-only HTTP services, verifies the expected failure
category and cleanup, and retains stdout, artifacts and test hashes. All owned
services stop; output directories remain for your review. Browser traces contain
only synthetic fixture data here. Real project auth and traces need private
storage. See the [support matrix](../../../docs/reference/specialist-support.md)
for executed stacks and remaining limits.
