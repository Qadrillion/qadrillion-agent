# Agent-authored reference suites

These tests were authored/debugged by fresh agents using the specialist skills
against real local targets. Original failures and corrected execution are in the
specialist evaluation record. The files retain their final authored business assertions;
the replay controller provides fresh identities and fixture variants. Blind review
subsequently hardened browser teardown so failed diagnostics cannot skip owned-data
cleanup. A closed-page regression retains its failure while proving cleanup;
original agent-authored bytes/hashes remain in the evaluation evidence.

Replay API, authorization and bounded performance checks without model access:

```sh
python3 tools/specialists/replay.py --out /tmp/qa-reference-new
```

For real Chromium and Firefox execution, install the optional pinned stack:

```sh
cd tools/specialists/reference/web
npm ci
npx --no-install playwright install chromium firefox
```

From the workspace root:

```sh
python3 tools/specialists/replay.py --web --out /tmp/qa-reference-browser-new
```

Use a new output directory. The controller creates disposable memory-only HTTP
services, runs the same tests on defective and corrected variants, verifies the
expected failure category and cleanup, and preserves stdout/artifacts/test hashes.
It returns nonzero for unexpected outcomes, infrastructure failures or incomplete
work. Defective variants should fail their test subprocess; that failure is
retained, never converted into a claim that the product behavior passed.

This replay is deterministic execution of already-authored tests, not a fresh
model evaluation. `evaluate.py` and `EVALUATING.md` cover fresh-agent evaluation.
Performance budgets characterize the local fixture, not production capacity;
CI contention can produce a real recorded threshold failure requiring diagnosis.
Browser traces contain only synthetic fixture data here. Real project auth and
traces need private storage. All local services stop; output directories remain
for review. The separate mobile README describes its optional SDK/device path.
