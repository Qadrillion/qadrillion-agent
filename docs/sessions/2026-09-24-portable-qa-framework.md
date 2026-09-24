# Portable QA framework — checkpoint 2026-09-24

Scope: tooling. User requested an in-depth audit, QA-practice research and an
implementation improving portability, token efficiency, team handoff and all
skills/agents. Cursor was selected for the first work-laptop pilot.

Branch: `feat/portable-qa-framework`; committed checkpoint `78886db`.
Working tree also contains the authorized skill/rule/agent rewrites, regenerated
copies, config/doctor/verifier, examples, sample ticket and documentation changes.
No unrelated starting changes existed. Do not discard the current working tree.

## Implemented

- Repository refresh validates real Git roots, expected remotes and mutability;
  explicitly fetches the canonical ref and rechecks state before merging.
- Ticket parsing rejects ambiguous/malformed state, supports tracker-free tasks,
  more scopes and relative evidence; index validates and escapes content.
- Hook event parsing fails closed; unknown MCP effects ask; known CLI writes are
  checked; file-read JSON/path handling and session checkpoints are hardened.
- Runtime generation is repository-owned, preserves custom settings and native
  read-only roles, materializes skills without symlink requirements, detects drift
  and fixes nested-root/UTF-8 handling. No native trust was changed automatically.
- Skills/agents use capabilities, risk-directed techniques, independent oracles,
  observed locators, honest black-box limits, retained failures and explicit handoff.
- Added setup declarations/doctor, on-demand surface guidance, deterministic CI
  entry point, ten behavioral scenarios and a current audit/acceptance spec.

## Verification with output

Expanded Python suite:

```text
Ran 97 tests in 12.553s
OK
```

The final policy run initially caught a newly introduced quoting bug in an inline
Python comment. The comment was corrected; affected checks were executed again:

```text
passed: 71   failed: 0
TOTAL passed=12 failed=0
```

The 12 checks are malformed-event probes of three guards, not yet durable new
hook fixtures. Logs retained at `/tmp/qadrillion-latest-verify.log` (including the
failure) and `/tmp/qadrillion-read-guard-fixed.log` (fix validation). Python tests
were unchanged by this comment correction and were not rerun unnecessarily.

Ticket schema: 1 checked, 0 violations. Index current. Adapter drift check current.
Diff check clean. Ten fresh-agent synthetic scenarios passed; detailed observations
and limits are in `2026-09-24-golden-tasks.md`.

Always-loaded project prose: 850 → 634 words; 5,935 → 4,712 characters. These are
not model token or billing measurements. A standalone skill-authoring validator
could not run because its interpreter lacks PyYAML; committed metadata/drift
checks ran without that optional external dependency.

## Source review and disposition

Focused independent review found locale-dependent reads, incorrect nested-root
launcher discovery, post-fetch state changes and absolute artifact references.
All four received fixes and regressions. Checkpoint tests additionally exposed
untracked-edit detection, repeated prompts and malformed lifecycle-event issues.
The final blind acceptance review has not run: required documentation checks
remain blocked, so its prerequisite verification is not green.

## Blocker and exact next action

The active PreToolUse hook rejected a shell-based documentation write because
command examples were recognized as destructive commands; it separately rejected
writing simulated credential-read regression payloads. No such operations were
executed. The denied writes were not retried through another tool.

A user question is pending: permission to write those prepared documentation and
test-data examples through the file-edit tool, without executing the examples or
changing the active hook configuration. Resolve that request before those writes.

Pending files: `docs/reference/integrations.md`, `team-workflow.md`,
`runtime-support.md`; updates to `docs/adopting.md` and `.cursor/README.md`;
`docs/research/qa-practices.md` and `runtime-portability.md`; durable additional
hook regression payloads in `tools/tests/test_hooks.py` / the hook test runner.
Research source notes already exist at `/tmp/qadrillion-qa-research.md` and
`/tmp/qadrillion-portability-research.md`; they contain inspected sources and limits.

After resolving: finish those files, regenerate adapters if canonical inputs
change, run full verification and clean-export checks, perform the blind build
review against the spec, record its content fingerprint, then prepare the reviewed
branch for publication. Do not represent the current overall verification as Pass:
five broken documentation links and three required missing guides remain.

Tracker update: none applicable; no external post, push, PR or release performed.
Native runtime trust/discovery, Windows operation, company tools/product/device,
actual token savings and the work-laptop pilot remain unverified.

Verdict: **Partial — code tests pass; documentation/fixture gate and final review pending.**

## Resumed with user authorization — 2026-09-24

The user approved the previously blocked harmless documentation and fixture
writes and requested fewer approval gates. All pending guides/research and
durable hook tests are now committed. Default guards use a targeted profile;
strict organizational gates are opt-in. Ordinary local edits, dependencies and
authorized QA updates proceed; explicit reporting authority carries through the
task. No global hook or native permission configuration was changed.

Final verification caught a new doctor regression: temporary roots on macOS can
resolve under another prefix. Three subcases of one new executable-path test
failed because valid cwd/artifact paths appeared outside the unnormalized root.
`doctor.inspect()` now normalizes the root before comparing resolved paths. The
failed output is retained at `/tmp/qadrillion-final-verify.log`.

After that fix, the test-runner recorded at f6dbb93:

```text
Main: passed: 75  failed: 0
Ran 111 tests in 18.750s — OK
Offline verification: PASS (exit 0)
Git-free export sync check: exit 0
Git-free export: passed: 75  failed: 0
Ran 111 tests in 18.278s — OK
Offline verification: PASS (exit 0)
```

Logs: `/tmp/qadrillion-final-fixed-verify.log` and
`/tmp/qadrillion-clean-export-verify.log`. The disposable export came from
committed HEAD, ran under a path with spaces, had no `.git`, and was cleaned up.
Runtime: Python 3.14.6, Bash 3.2.57, Git 2.54.0 (Apple Git-157). No failed,
errored or skipped Python tests remained. CI will also exercise Python 3.11 on
Linux/macOS; the stable `governance` aggregate preserves the required check name.

Remote main had advanced to d7bb662 by squashing the earlier public-page branch.
Its tree exactly matched the original 1ec30e1 baseline. The feature branch merged
that main revision at 9a25704, resolving duplicate-history conflicts with the
current implementation. `git diff f6dbb93 HEAD --stat` was empty: the merge did
not change verified content.

The new authorization scenario also passed in a fresh agent; the behavioral
record now contains eleven distinct synthetic cases across two checkpoints.
Always-loaded prose is now 660 words / 4,898 characters versus baseline
850 / 5,935. These remain word/character proxies, not token measurements.

Blind review round 1 is in progress against d7bb662; the fingerprint was captured
before dispatch and recorded in the spec. Publication awaits that review.

## Blind review round 1 corrections

Verdict: PASS WITH SHOULDS. Three in-scope findings, zero deferred findings:

1. Enabled MCP inventory metadata named `executable` could crash doctor. Inspect
   executable availability only for CLI integrations; leave other transport
   metadata as data. Regression covers API, MCP and manual declarations.
2. Adapter path extraction treated nested MCP `source: null` and `paths: []` as
   malformed local file arguments. Restrict extraction to supported native file
   tools and preserve MCP payload data unchanged. Regression covers both adapters;
   filesystem MCP permission coverage is explicitly documented as a native/provider
   responsibility without an explicit schema mapping.
3. Doctor's mocked no-execution test was weaker than the claimed property. It now
   configures a real disposable executable which would write a marker, reports it
   available, and asserts the marker remains absent after inspection.

All three fixed in 5abb8ba. Full verification and clean export rerun requested;
the next reviewer gets a fresh context and complete updated diff. No prior review
fingerprint is reused for the changed code. Historical behavior runs remain
observations by the original evaluator, not a claim of independent reproduction.

## Blind review round 2 corrections

Round 1 fixes passed 75 guard cases and 113 Python tests in both the checkout
and a Git-free export at 5abb8ba. Logs: `/tmp/qadrillion-review-fixes-verify.log`
and `/tmp/qadrillion-review-fixes-export.log`. Round 2 independently reproduced
those counts; its verdict was PASS WITH SHOULDS for two new in-scope findings.

Doctor still consumed optional integration `cwd` metadata as if it were a
validated runner directory. Fixed by resolving CLI executable paths at the
workspace root and consuming cwd only for runners. Regression covers metadata
of multiple valid JSON shapes. Two refresh tests inspected private helper calls
despite already checking preserved repository state; those call-history checks
were removed while the concurrent-change fixtures and observable assertions stay.

Both findings fixed in b059df6. No deferred findings. Full verification and
clean-export checks precede fresh blind review round 3. The round 2 fingerprint
was a0963e81aec6835f132eeff962434e767b76d55a6d716acc2f1fb447404caf9d.

## Round 3 correction and final content check

The b059df6 tree passed 75 guard cases and 114 Python tests in checkout/export;
the third blind reviewer independently confirmed those results. Initial verdict:
PASS WITH SHOULDS for one reproduced false denial. An event running in a child
checkout supplied a relative file path; the adapter also passed that raw path
to a guard running at the workspace root. An unrelated root symlink could then
deny the safe child file.

Fixed in fffd465: root candidates are now event-cwd absolute lexical paths and
their resolved targets. Regression covers both runtimes and Read/Write, and
proves lexical credential-name checks still deny even when a symlink points to
an ordinary fixture. The round 3 reviewer will recheck replacement complete
content after full verification; no fourth broad review round is being started.
The initial round 3 fingerprint was
64fd5754d99f6e3f57e105516dbf8602dac50b981c3f323fc697986ecec12f72.

## Completed implementation and review

Final implementation: fffd465. Both checkout and Git-free committed export passed
75 guard cases and 115 Python tests, with zero failures/errors/skips. Output:

```text
Checkout: Ran 115 tests in 18.679s — OK
Export: Ran 115 tests in 18.968s — OK
passed: 75  failed: 0
Offline verification: PASS
Export sync check: exit 0
```

Logs: `/tmp/qadrillion-final-content-verify.log` and
`/tmp/qadrillion-final-content-export.log`. The final reviewer independently
confirmed 75/115 in checkout/export and checked the correction with independent
path probes; final verdict **PASS**, no remaining findings. The six SHOULD
findings across three review rounds are all fixed; zero findings deferred.
The final fingerprint was captured before the corrected-content recheck:
`ccebd55ec5259becb587c2c06b475e1544fa95c25b40c0307cdc242099547894`.
Base: `d7bb662f6aa09f4f9f2b3cdbcce60674104def41`.

The spec retains the final reviewer's Not verified section verbatim. Historical
behavior observations are attributed to their original fresh-agent evaluations;
the reviewer did not replay them. Native runtime and connected-company tests
remain for the Cursor pilot. The harmless native-canary instructions were made
concrete after review; they were not executed in a live runtime here.

All five task-owned implementation worktrees were clean and removed. Their
commits remain in Git. Main checkout contains only intended task changes;
publication/CI results will be appended after the reviewed branch is pushed.
