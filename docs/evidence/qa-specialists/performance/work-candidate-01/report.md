# Fail — local /work latency budget

Task LOCAL-1; owner: QA agent; classification: api with performance overlay. Tracker: null; no publication. Baseline pending; no relative-regression conclusion.

## Reproduce

From the workspace root:

```sh
python3 -B tests/check_work.py --identity target.json --out-dir artifacts/work-candidate-01
```

Recorded wrapper and helper exits: **1**. For another identity, change only `--identity` and use a fresh `--out-dir` under `artifacts/`. Existing run directories are refused to preserve evidence. The fixed workload and thresholds remain unchanged. No retries were run.

## Declared experiment and coverage

Before measurement: 50 measured GET /work requests, 1 worker, 3 separate warmups, 1-second blocking request timeout, 10-second measured dispatch ceiling, stop at 3 observed errors; p95 <= 40 ms and error_rate = 0. Outer helper process timeout: 20 seconds. The helper verifies live identity again before warmup. The first warmup checks the business result before measured work proceeds.

| Risk | Automated check / oracle | Impact / likelihood | Evidence |
|---|---|---|---|
| Wrong target | Literal loopback, exact live identity, test role and fixture | Unauthorized target / guarded | invocation.json and measurement.json |
| Incorrect work response | HTTP 200 and JSON {"ok": true}, supplied CONTRACT.md | Invalid operation / initially unknown | helper business checks and raw samples |
| Slow responses | Nearest-rank all-attempt p95 <= 40 ms | Local latency budget missed / observed | measurement.json and checks.json |
| Errors or incomplete workload | Zero errors, 50 completed attempts, no stop | Invalid characterization / guarded | checks.json |

Single closed worker sends the next request only after the previous one finishes, with no think time. No controlled arrival rate. Each helper request builds a urllib opener; connection establishment/client JSON read and parse are included, with no browser connection-pool simulation. Proxies and redirects are disabled. No business dataset or actors are required by /work. Cache state before warmup is unknown; three warmups do not prove steady state. Only identity verification and /work were accessed.

## Observed results

- Scheduled / attempted / completed / successful measured requests: **50 / 50 / 50 / 50**.
- Errors / timeouts / interrupted / not run / outstanding at return: **0 / 0 / 0 / 0 / 0**.
- Warmups: 3 successful HTTP 200 responses, 7.866, 7.853 and 8.640 ms; excluded from measured percentiles and elapsed time.
- Measured elapsed: **1.292350 s**; achieved throughput: **38.689 attempts/s**.
- All-sample p50 / p95 / p99: **9.278 / 94.998 / 98.386 ms**. Success-only p95: **94.998 ms**, identical population because all attempts succeeded.
- p95 fails by **54.998 ms** (2.375 times the budget); error rate passes at **0%**.
- 10/50 samples exceed 40 ms. Slow zero-based sequence numbers: **1, 6, 11, 16, 21, 26, 31, 36, 41, 46**, spanning **87.532–98.386 ms**. Other samples span **7.708–12.152 ms**.
- No emergency stop: `stop_reason: null`. The measured workload completed before the duration ceiling and without consuming the error budget. Threshold failure is separate from stopping traffic.

Nearest-rank quantiles sort all 50 measured timings: p50 is rank 25, p95 rank 48, p99 rank 50 (the maximum). These are small-sample indicators, especially p99. The periodic slow sample every fifth measured request supports a hypothesis of periodic operation-associated delay, but cannot identify a resource bottleneck or prove server causality without traces/utilization. No diagnostic rerun or fixture change was needed to establish the budget failure.

## Boundaries and stops

Maximum intended /work traffic: 53 calls including warmups; actual: 53. One in-flight measurement at a time. The error stop observes completed failed attempts; with one worker there is no concurrency overshoot. The 10-second ceiling gates dispatch and excludes warmups/identity checks; an in-flight call can extend elapsed time past it. The 1-second urllib timeout is a blocking timeout, not a strict total transaction deadline; the 20-second outer process timeout bounds helper execution. No stop behavior was deliberately induced. CPU, memory, socket utilization, saturation, and server traces were not collected; the workload limits bound traffic, not server resource use.

## Provenance, cleanup, and handoff

Live identity matched target.json before local authoring and again in the wrapper/helper: fixture qadrillion-specialist-lab, role test, run f0e77488-08af-4ec9-85b6-849e6d900a02, build a036766d21e2e67fec0b69432b01472b177cdc3b8131cc30e155a34c7f07f28a, URL http://127.0.0.1:61349. Mode is retained as identity metadata, not used as an oracle. Environment: macOS 26.6.2 arm64, local loopback client; exact Python, UTC times, argv, cwd and helper/contract/test/config SHA-256 hashes are in invocation.json.

Workspace branch: main; no commit exists, so no source revision can be pinned. The manifest has no repositories and scoped refresh exited 0 with no entries. Product implementation/lab.py is not supplied; source review is limited to the measurement helper and independent contract. This is black-box target evidence; reported build identity is not source verification. Initial workspace files were untracked. No dependencies installed. Tests authored only in tests/check_work.py; task records only in artifacts/work-candidate-01/. Instruction/config/identity files were not modified. State/handoff is recorded here rather than docs/tickets to honor the requested output boundary.

Cleanup: no task-owned service, fixture, business data or temporary fixture directory was created. The supplied target is left running under its existing ownership. Evidence is intentionally retained. No external publication.

Unexecuted: baseline comparison (awaiting separately supplied identity), corrected-target run, other routes, concurrent/open-arrival load, sustained load/soak, stop-injection scenarios, production capacity, resource profiling, browser/mobile behavior. This result establishes only failure of the agreed local absolute latency budget; it makes no production-capacity claim.

Next action: run the unchanged wrapper against the separately supplied baseline with a fresh artifact directory under equivalent environment/state, then compare both retained runs.

Artifacts: measurement.json (raw warmup/measured samples and helper summary), checks.json (independent wrapper assertions/counts), invocation.json (command/environment/identity/hashes/exits), stdout.txt, stderr.txt, report.md. No tracker post or draft is required.
