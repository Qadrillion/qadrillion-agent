# Public framework audit

Audit baseline: `1ec30e1`. Scope: the public repository, its instructions, scripts,
agent/runtime adapters, tests and adoption model. Adjacent Qadrillion product
context confirmed the free bring-your-own-tools intent; private company material
was not copied into this repository. Cursor is the first work-laptop pilot.

## Assessment

The useful core is already here: durable ticket state, a short startup path,
separation of contracts from procedures, bounded specialist roles, retained
execution evidence and committed policy tests. The main gap was treating one
team's implementation choices as prerequisites for trustworthy QA. That prevents
the framework from serving source-limited work, semantic web automation, alternative
trackers and languages, manual exploration or teams sharing work over time.

The public product should be a portable QA method with executable support tools,
clear capability gaps and measured outcomes. It cannot honestly promise every
stack's integrations, equal enforcement in every agent, defect-free products or
99% autonomy. Those claims need representative company pilots and comparative
measurements, not larger prompts or more agents.

## Verified baseline findings

| Priority | Finding and failure | Evidence at baseline | Change |
|---|---|---|---|
| High | A nested folder can be treated as its parent Git repository; refresh proceeds on remote mismatch and after a failed fetch. | `refresh.sh` root test and unconditional merge path; reproduced placeholder reporting parent commit. | Validate actual root, contained paths, exact mutability, remote and successful fetch before update; isolated Git regressions. |
| High | Malformed hook events are allowed. | All three guards returned allow for an object lacking their required fields. | Explicit event validation and fail-closed decisions. |
| High | Codex approval convention can be supplied by the agent itself. | Adapter recognizes a command prefix instead of native consent. | Remove convention; supported runtime semantics only. |
| High | Hook/runtime claims exceed demonstrated coverage. | CI covered Cursor payloads and two Claude mappings, no native discovery/trust demonstration. | Shared adapter tests, explicit coverage table and per-machine smoke; no universal sandbox claim. |
| High | Mandatory source IDs, fixed runner conventions and cloud-canonical collections exclude valid testing setups. | QA skill and test contract unconditionally require them. | Capability discovery, black-box fallback, observed semantic locators and actual project ownership. |
| Medium | Ticket parser silently accepts duplicate keys and malformed delimiters; index emits malformed tables for pipe content. | Direct parser/index inspection and synthetic reproductions. | Typed restricted-YAML parsing, duplicate rejection, validation before index rendering and escaping. |
| Medium | Free-text tasks cannot satisfy required tracker URL; fixed scopes/environment labels exclude other products. | Validator schema. | Nullable tracker, local IDs, more surfaces and explicit unknown/other capability handling. |
| Medium | Required startup reference missing; public generation depends on a personal private path. | `known-quirks.md` absent; AGENTS names author-local installer. | Ship startup references and repository-owned synchronizer. |
| Medium | Always-on per-file approval contradicts task autonomy. | core rule versus user/project authorization. | Carry authorization through routine local implementation; ask only for material decisions/actions. |
| Medium | Full verbose output and unconditional worker routing waste context. | QA workflow and orchestrator. | Focused delegation, decisive excerpts, artifact paths, on-demand references and measured budgets. |
| Medium | Team adoption does not distinguish public upstream from company state or owner/build-aware handoff. | Adoption guide lacks a private-workspace upgrade procedure. | Private adoption, task ownership, separate checkouts, pinned identity and safe upgrade branch. |

Baseline verification: 71 hook payloads passed; one fictional ticket validated and
its index was current. That suite did not catch the findings above. A green suite
shows its assertions passed, not that the framework has complete coverage.

## Research translated into decisions

The [QA source register](../research/qa-practices.md) contains twelve inspected
primary works, not a popularity ranking or a claim to have read inaccessible
books. Each supplies a practical decision: risk-directed techniques; independent
oracles; exploratory charters; test isolation and reliable waits; lowest effective
layer; whole-team feedback; limits of accessibility scans; actor/object authorization;
observable business outcomes; build/config identity; and measured performance.

The [runtime/integration register](../research/runtime-portability.md) uses current
official documentation. It distinguishes TWG CLI, ACLI and Rovo MCP, including
authorization differences and cost caveats. Tool choice follows policy and task
coverage before efficiency. No live transport benchmark was run here.

## Prompt and behavior measurements

Always-loaded project prose (AGENTS plus the core rule body) changed from 850
words / 5,935 characters at baseline to 660 words / 4,898 characters. These are
word/character measurements, not actual model tokens or billing. Detailed research
and surface guidance load on demand. Generated skill aliases may still be exposed
more than once by particular runtime discovery versions; inspect the native list.

Ten fresh-context synthetic decisions met their expected outcomes in one run;
an additional authorization scenario passed after the user's autonomy amendment.
The [evaluation record](../sessions/2026-09-24-golden-tasks.md) retains observations
and limits. There is no claim of a broad success rate from this small sample.

## Limits and next evidence

1. Deterministic checks validate parsers, repository safety and selected policy/
   adapter payloads; behavior evaluations assess specific synthetic decisions.
2. Native runtime discovery/trust and approval must be observed per machine.
   User-level/global hooks can conflict with project hooks; regexes can also
   reject harmless documentation that contains command examples.
3. Config is a capability inventory, not a fleet of implemented vendor connectors.
   Authenticate and verify actual command/tool schemas in the company environment.
4. Pilot a representative Cursor task end to end on the work laptop, including
   pause/resume and another engineer reading evidence. Then repeat for Claude
   Code and Codex before claiming parity.
5. Measure actual tokens, latency, costs, interventions, task outcomes and escaped
   defects on comparable tasks. Prompt word counts are not token measurements.

## Autonomy adjustment requested by the user

The final default is `GUARD_PROFILE='targeted'`: ordinary edits, dependency
installation and authorized CLI/MCP work have no generic approval gate. Targeted
destructive operations, production tests, credential access and configured fences
remain checked. Organizations can opt into broader `strict` gates. This does not
grant external publication authority: an explicit reporting task carries its
authorization forward, with native permissions still active. Native file edits
check paths rather than treating documentation command examples as executable.
Global machine hooks are outside this repository and were not changed.

Implementation results and review evidence are recorded in the linked
[spec](../specs/2026-09-24-portable-qa-framework.md) and dated session records.
