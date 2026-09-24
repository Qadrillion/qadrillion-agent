# Bounded local HTTP measurement

Use `tools/specialists/measure.py` only with the disposable parcel lab. It accepts
a verified lab identity, not an arbitrary company URL. For another product use
its reviewed performance harness; do not weaken the helper's target guard.

Read `tools/specialists/CONTRACT.md` and inspect:

```sh
python3 tools/specialists/lab.py --help
python3 tools/specialists/measure.py --help
```

Start a new lab in a managed process, retaining its identity JSON path, or use
the evaluator's supplied identity. Declare the following example experiment
before running it: 50 measured requests, one worker, three warmup requests,
one-second blocking timeout, ten-second measured dispatch ceiling, stop after
three observed errors, p95 at most 40 ms and zero business/transport errors.
These are a local regression exercise's diagnostic thresholds, not product SLOs.

Set `QA_LAB_IDENTITY` to the supplied identity file and `QA_MEASUREMENT` to a new
result-file path in the task's artifact directory, then run:

```sh
python3 tools/specialists/measure.py \
  --identity "$QA_LAB_IDENTITY" --out "$QA_MEASUREMENT" \
  --requests 50 --concurrency 1 --timeout 1 --duration 10 \
  --max-errors 3 --p95-ms 40 --error-rate 0 --warmup 3
```

Capture stdout, stderr and exit status, including a nonzero result. The JSON
contains identity, workload, thresholds, warmup, raw timed samples and summary.
Exit 0 requires all requested samples and passing thresholds; exit 1 represents
failed thresholds/incomplete measured work; exit 2 indicates a blocked/invalid
measurement. An absent artifact after setup failure is not a completed run.

Inspect request count, error rate, stop reason, elapsed time, throughput and
p50/p95/p99. The helper reports all-sample quantiles and success-only p95; compare
their populations and inspect failures instead of dropping them. Quantiles use
nearest rank. With 50 requests, the upper tail is a small-sample local indicator.

Its model is closed: workers send their next request after completion with no
think time. `urllib` opens HTTP connections using its own connection behavior;
this is not a browser connection-pool simulation. Warmup is separate from the
measured dispatch ceiling. On a stop, already-started requests may complete;
the CLI's blocking timeout is not a strict whole-process deadline. Use an outer
process timeout if the evaluation requires one, and report an interrupted run as
incomplete. Resource telemetry is not collected by this helper.

Record a baseline and candidate with identical arguments, interpreter, generator
location and equivalent fixture state. Use new output paths and preserve both
identities; do not overwrite the failed sample or modify thresholds after seeing
it. A corrected target receives a new run with the same measurement parameters.
If unrelated local contention invalidates the comparison, state that evidence
and apply the shared diagnostic rerun budget instead of selecting the best run.

Finish by stopping each task-owned lab process, verifying process exit and closed
port, and removing task-owned fixture directories after retaining artifacts.
The result establishes only the specified local HTTP slice, not service capacity,
production reliability, browser experience or a resource bottleneck.
