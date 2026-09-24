---
id: PROJ-101
title: Invoice export keeps stale currency after customer locale changes
scope: multi-surface
status: done
verdict: fail
build: "web 2.14.0 / api 2.14.1 — fictional preview build"
environment: preview-42
tracker: https://tracker.example/browse/PROJ-101
design: null
source_refs:
  - source/api/src/invoices/export/render.ts:57
  - source/api/src/customers/locale.ts:9
started: 2026-09-04
updated: 2026-09-24
next_action: "Retest the locale-change API and browser scenarios on an identified build containing the cache fix"
blockers: []
owner: example-qa
branch: qa/proj-101
env_role: test
evidence: []
---

# PROJ-101 — fictional worked example

**All product names, paths, build identifiers and output below are invented
illustrations. This is not an executed test result for Qadrillion or a company.**
The example shows a completed QA run with a failing criterion and a next action;
`done` does not mean the product passed.

## Analysis

Agreed criteria/oracle:

- AC1: Draft exports use the customer's currency selected at export time.
- AC2: A locale/currency change applies to the next export without another login.
- AC3: Issued invoices preserve their recorded issued currency.

`[HIGH]` — export reads a per-process cached customer locale that the update path
does not invalidate. Location: `render.ts:57` and `locale.ts:9` at fictional commit
9f3c1a2. Source suggests stale exports after a change; execute a sequence to prove it.
The implementation is supporting evidence, not the expected-result oracle.

Observed preview UI: one button named Export PDF. Use that observed role/name,
then the download event and downloaded PDF contents. A toast test ID is not
required to observe the agreed outcome. Source and runtime claims stay separate.

Target identity: the fixture's preview deployment is verified non-production.
Configuration: fictional c42. Source: fictional 9f3c1a2. No external payment or
customer records are involved; each test uses an isolated synthetic customer.

## Test plan

| Criterion / risk | Scenario and technique | Expected result | Layer | Status |
|---|---|---|---|---|
| AC1 | Export new EUR customer; representative partition | EUR totals | API | pass |
| AC1 | Export new GBP customer; alternate partition | GBP totals | API | pass |
| AC3 | Change locale after issuing invoice; state transition | Issued currency preserved | API | pass |
| AC2 / stale cache | Export EUR, change to GBP, export again; state sequence | Second export uses GBP | API | fail |
| AC2 / wiring | Same state sequence through observed browser controls | Downloaded PDF uses GBP | Browser | fail |

The API test is the narrow check; one browser journey adds wiring/download
coverage. Concurrent changes and localization formatting are outside this agreed
slice; neither is claimed tested. No defect is invented for missing test IDs.

## Execution & results

Illustrative commands and output, not executed in this repository:

```text
cwd: automation/api; target: preview-42; build: api 2.14.1; config: c42
$ pytest tests/invoices/test_export_currency.py -v
export_default_currency PASSED
export_alternate_currency PASSED
issued_currency_is_preserved PASSED
locale_change_updates_export FAILED
expected: GBP; actual: EUR
3 passed, 1 failed; exit 1

cwd: automation/web; target: preview-42; build: web 2.14.0; config: c42
$ npx playwright test invoices/export-currency.spec.ts
locale change followed by export FAILED
expected PDF total currency: GBP; actual: EUR
1 failed; exit 1
```

No diagnostic rerun was needed: the reproducible assertion already establishes
AC2 failure. Source supports a cache hypothesis; an observed wrong currency does
not independently prove every detail of the implementation's root cause.

## Handoff

Owner example-qa, branch qa/proj-101. The illustrative check files are ready for
review in the team's separate automation repository; no real files are supplied
here. AC1/AC3 covered, AC2 fails. Retest on a new identified build and preserve this
run as history. Verify the teammate can access actual artifacts in a real workspace.

## Tracker comment

Prepared draft; posted: no. Destination is fictional. No external write performed.

> QA — Fail. Tested preview-42, web 2.14.0 / api 2.14.1, configuration c42.
> New-customer and issued-currency checks pass. Changing locale then exporting
> retains the prior currency in both API output and the browser download (AC2).
> API: 3 passed / 1 failed. Browser: 1 failed. Concurrency and locale formatting
> were not tested in this slice. Retest the failed sequence on an identified fix build.

## Notes

Your team chooses its runner and tracker fields. This example uses pytest and
Playwright only to illustrate retained output; neither is a framework requirement.
