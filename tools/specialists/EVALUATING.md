# Specialist evaluation

`python3 tools/verify.py` runs deterministic policy and fixture tests. Those tests
exercise real local HTTP behavior and helper boundaries; they do not measure
model behavior. Run fresh model scenarios separately after deterministic checks
pass. The [golden-task procedure](../../.cursor/skills/golden-tasks/SKILL.md)
defines that distinction.

List the nine routing scenarios with:

```sh
python3 tools/specialists/evaluate.py list
python3 tools/specialists/evaluate.py materialize --scenario api --out /tmp/qa-api-evaluation
```

The destination must be new. Each call creates `workspace/` with the canonical
QA skills, roles, contracts, supporting tools and safe task fixtures. `TASK.md`
contains only the task. State starts fresh; sessions, `.git`, research, tests,
the evaluation helper, scenario catalog and answer keys are excluded. The
evaluator's `evaluation.json` stays outside the worker root and pins copied
content with SHA-256 hashes. `--revision` additionally records a known source
commit. `--context /path/to/file` copies an explicitly selected regular file to
`workspace/fixtures/`; filenames must be unique. Use synthetic non-secret
context only, and do not supply a variant answer key or prior failed attempt.

Start a fresh runtime yourself, with access restricted to `workspace/` plus the
permitted disposable target, and give it only `TASK.md` and the normal QA entry
point. The directory layout is **not a sandbox**: use native runtime controls
and ensure the evaluator directory is not exposed. Disable inherited chat
history. Do not give the worker `evaluation.json`, `scenarios.json`, expectations
or implementer reasoning. The helper does not start runtimes, register hooks,
execute transcript commands, authenticate to services or grade outputs.

Route evaluations inspect actual skill reads, actions, artifacts and claims.
Some routing scenarios intentionally have no live target: useful independent
authoring and accurate execution gaps are part of their expected behavior.
Missing capabilities do not automatically fail a correctly limited response.
For the execution exercises, supply the independent [parcel contract](CONTRACT.md)
and a fresh target identity. Keep evaluator-controlled defects outside worker
source access. Capture authored-test hashes before executing the same tests on
defective and corrected targets; preserve both outputs and cleanup evidence.

Review actual runtime actions against the evaluator-only expectations. Save a
review JSON document, for example:

```json
{
  "reviewer": "independent reviewer identifier",
  "runtime": "runtime and version",
  "model": "reported model identifier",
  "runtime_run_id": "actual session or agent identifier",
  "verdict": "Fail",
  "observations": ["transcript.jsonl line 12: initial request accepted; final receipt was never checked"],
  "findings": ["The final claim treated HTTP 202 as completed delivery."],
  "actual_tokens": null,
  "token_source": null
}
```

Record it with the unmodified runtime JSONL and relevant artifacts:

```sh
python3 tools/specialists/evaluate.py record --run /tmp/qa-api-evaluation --review /tmp/review.json --transcript /tmp/runtime.jsonl --artifact /tmp/test-output.txt
```

Each record has a new attempt ID and copies/hashes its evidence. Earlier failed
records cannot be replaced by a later Pass. `Pass`, `Fail`, `Blocked` and
`Not-run` are reviewer verdicts, not keyword scores. An executed verdict requires
a nonempty runtime JSONL and evidence observations; failed or blocked reviews
also require findings. JSONL format validation cannot establish authenticity or
prove correct reasoning. State provenance honestly and keep the original runtime
session evidence available.

`actual_tokens` is nullable. Use an integer only when the runtime exposes that
count and name its evidence in `token_source`; words, characters and estimates
are not actual tokens. Report each failed/unexecuted case and unnecessary
approval or inaccurate-claim findings separately. Preserve the first failure;
any one diagnostic rerun needs a stated hypothesis and both results. Native
discovery, trust and hook activation require separate observed runtime checks.
