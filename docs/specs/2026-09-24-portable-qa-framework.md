# Spec — Portable QA framework
Status: authorized 2026-09-24 by the request to audit, research and improve the public framework.

## Problem

The public template carries conventions from a small number of company setups.
It must support QA work across products, vendors and coding agents without
inventing integrations, overstating evidence, or requiring the author's machine.

## Decisions

- Keep the repository and existing rule/skill entry points; introduce capabilities
  and optional surface guidance instead of a new hosted service or test runner.
- Cursor is the first work-laptop pilot. Ship shared instructions and reproducible
  adapters for Cursor, Codex and Claude Code; other agents use explicit manual entry.
- Keep production execution excluded. Hooks are defense in depth, not a sandbox.
  Runtime permissions, least-privilege credentials and observed hook execution matter.
- A company adopts into a private workspace. Public upstream receives generic fixes;
  teammates hand off ticket evidence through their private repository and tracker.
- Research at least ten substantive primary works; link inspected material and
  translate it into operational decisions. Do not claim a popularity ranking,
  complete book review, guaranteed 99% autonomy, or unmeasured token savings.
- Read-only/reversible task work proceeds under the user's authorization. External
  writes need applicable consent; an unavailable approval UI must not silently allow them.

## Acceptance criteria

| # | Given / When / Then | Guards against | Verified by |
|---|---|---|---|
| AC1 | A clean public clone can validate and regenerate its agent configuration using committed tools, without personal absolute paths or external private repos. | Author-machine dependency and adapter drift | Generator tests and check in a clean exported tree |
| AC2 | QA can start from a ticket or free text with no tracker/source/mobile stack; it uses available capabilities, records gaps and can execute black-box checks. | Vendor lock-in and invented access | Behavioral golden tasks and ticket validation tests |
| AC3 | A test plan links risks/criteria to techniques, oracles, checks and evidence, and distinguishes failed, skipped, expected-failed, not-run and blocked outcomes. | False confidence and checklist-only testing | Skill evaluation and evidence contract review |
| AC4 | Setup reports missing prerequisites, malformed configuration and unverified runtime enforcement without reading secrets or making network calls. | Broken first-run experience | Doctor tests for valid/missing/invalid configurations |
| AC5 | CLI/API/MCP selection is capability-driven, scoped and measured; approvals survive a transport change and uncertain writes are reconciled before retry. | Token inflation and duplicate/unapproved writes | Integration guide, hook payload and behavior tests |
| AC6 | Team handoff records owner, branch, source/build/config identity, artifacts and concrete next action; the guide distinguishes private company data from public template updates. | Lost or conflicting team work | Ticket validation tests and resume golden task |
| AC7 | Refresh never updates a parent repo through a nested folder, a mismatched remote, an unsafe path or a failed fetch. | Wrong-repository mutation | Isolated Git regression tests |
| AC8 | Malformed hook events fail closed, supported adapters preserve verdicts, credential paths are encoded safely, and no model-supplied approval marker authorizes a write. | Silent policy bypass | Hook and adapter tests; live runtime activation explicitly separate |
| AC9 | The skills/agents use research from at least ten inspected primary works, with conditional surface guidance and no forced full-context research loading. | Unsourced instruction accumulation | Source register and independent review |
| AC10 | One committed verification command runs meaningful local checks also used by CI; golden outcomes and tool output are retained honestly. | Divergent verification and self-declared success | Full verification, independent behavior tests and blind review |
| AC11 | Default guards permit routine documentation, dependency and authorized QA tool work without blanket approval prompts; targeted destructive/production/credential checks remain, with stricter organizational gates opt-in. | Unnecessary interruption and documentation false positives | Targeted/strict hook payloads, native file-edit adapter tests and authorization behavior scenario |

## User amendment — 2026-09-24

The user explicitly authorized the previously blocked documentation and fixture
writes through file-edit tools and requested minimal approval gates. This settles
AC11: preserve task authorization, let ordinary work proceed, keep focused checks
for high-impact operations, and do not change global machine hooks or permissions.
The earlier pending-approval checkpoint below is historical, not an active blocker.

## Out of scope

Company integrations/authentication, customer product tests and paid services;
live production checks; claiming support for every runtime's enforcement layer;
a new testing platform; global machine configuration; deleting existing company data.

## Not verifiable here

Live Cursor, Claude Code and Codex hook activation on a fresh colleague's machine;
authenticated Jira/other vendor flows; the user's work-laptop product and device;
actual model token savings or autonomous completion rates in those environments.

## Decision-record candidates

Portable capability-based QA and observed evidence replace mandatory mobile-specific
conventions. Runtime hooks complement native permissions rather than defining a sandbox.

## Interim verification — 2026-09-24

Branch: feat/portable-qa-framework; committed checkpoint 78886db plus working changes.
97 Python tests pass. After fixing an introduced quoting regression, 71 existing
guard payloads and 12 malformed-event probes pass. Ten fresh-agent behavioral
scenarios met expectations in a single run. No live integration claim is made.

Overall verification remains blocked by missing documentation whose write was
denied by the active hook; user permission to write the harmless literal examples
through a file-edit tool is pending. Additional hook fixtures remain pending for
the same reason. Final blind acceptance review and publication have not occurred.
See the dated session checkpoint for exact resume steps and retained failure output.
