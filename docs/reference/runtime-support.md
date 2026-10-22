# Runtime support and verification

Portable instructions do not guarantee native discovery, subagents or hooks.
This repository supplies content and adapters; validate them in the actual
runtime/version used by the team. Sources now live in provider-neutral `.agent`.
The portability baseline did not certify native activation. The later
[specialist evaluation](specialist-support.md) observes Codex 0.154.0 metadata
discovery and explicit skill execution, and Claude 2.1.278 discovery/full-skill
reads plus benign Read/Stop hooks. Cursor activation and native deny/trust coverage
remain unverified; these limited observations do not establish runtime parity.
Cursor editor 3.21.18/CLI 2026.09.23-86fc751 were probed: the explicit CLI
attempt stopped at `Authentication required`, with no native events.
[Retained evidence](../evidence/qa-specialists/cursor/REPORT.md) identifies the
required authenticated session without connecting a company account.

| Runtime | Maintained/generated entrypoints | What still needs live validation |
|---|---|---|
| Cursor / other editor | `AGENTS.md`; manually read `.agent` sources. Optional `.cursor -> .agent` alias preserves explicit paths | Native discovery/registration after migration is unverified; historical `.mdc` rule discovery is not preserved by the neutral `.md` source format |
| Claude Code | `CLAUDE.md` imports AGENTS; linked `.claude/skills`, generated agents and hook adapter | Implicit skill selection, import precedence, subagent activation, native tool permissions and deny/trust/event coverage beyond observed benign Read/Stop hooks |
| Codex | `AGENTS.md`; linked `.agents/skills`, generated `.codex/agents` and hooks | Implicit skill selection, subagent activation, trusted project layer and exact native hook definitions beyond observed metadata discovery/explicit execution |
| Other agent | Read AGENTS, then the named QA skill and applicable contracts manually | Its own discovery, tool access, permissions and execution support; perform roles sequentially without native subagents |

Edit `.agent` sources and run `python3 tools/agents/sync.py`. Use `--check` for
drift. Skills have one maintained body; runtime skill directories are relative
symlinks. The migration converts only copies matching their owned ledger hashes
and modes, rejecting extra or modified files before changing output. Symlink
support is required; if unavailable, the generator leaves existing output intact.
All ledger paths are normalized and workspace-contained before classification.
Changes use staged output and renamed originals in a recovery transaction; the
ledger is installed last and backups are retired only after commit. Failed writes
roll back, and an interrupted transaction recovers on the next normal invocation.
`--check` reports pending recovery without changing files. An unexpected edit
during recovery is preserved and reported as a collision. Failed backup cleanup
retains a named `.agent-runtime-complete-*` directory for inspection without
blocking the committed installation.
It preserves unrelated settings and rejects unexpected changes to managed output.
The optional `.cursor` alias is not required by generation, policy dispatch or
offline checks. No personal installer is required. Inspect the live skill list;
offline path checks do not certify a runtime's discovery behavior.

Python 3.11+, Git and Bash are the intended local prerequisites. The verification
workflow targets macOS and Linux. Windows users need a compatible Bash
environment, such as WSL or Git Bash, and must validate path/tool behavior;
native Windows behavior is not certified. A cloud runtime also needs the
required executables and approved credentials in that environment.

## Guard policy and its limits

`GUARD_PROFILE='targeted'` in `.agent/hooks/guard.conf` is the default. It permits
routine documentation/code edits and ordinary authorized
QA work. It retains targeted protection for destructive operations, production
execution and secret disclosure, with approval gates for high-impact operations
such as releases and deployment. Organizations can opt into `GUARD_PROFILE='strict'`
for broader approval gates, then regenerate adapters and validate native behavior.
Authorization still comes from the task and native runtime, not from a
hook returning allow. No command prefix or tool argument grants user consent.

The adapters translate supported shell, file and MCP events into the maintained
policy. Native file operations inspect paths, including patch source/destination
paths; their documentation content is data. Shell command pattern checks can
still match command examples embedded in shell text; use the runtime's file-edit
operation for documentation. Malformed supported events,
policy failures and invalid policy output produce a valid native denial. A
normal allow preserves the host's own permission checks. Codex cannot use this
adapter's approval request as native `ask`: gated actions become denials there.
That applies to remaining risky/strict gates, not every routine edit.

These hooks are defense in depth, not a shell parser, sandbox or universal tool
firewall. In particular:

- Name/command patterns cannot prove every operation's effects or authorization.
- Recursive `Grep`/`Glob` searches are not intercepted as individual file reads.
- MCP payload fields are provider data, not local paths. MCP guards inspect
  server/tool names; provider-native permissions must constrain file access by
  filesystem connectors. No MCP filesystem schema is mapped by this adapter.
- Wrappers, unrecognized tools, hosted execution and later interactive-shell
  input can lie outside the intercepted paths.
- Native trust, disabled hooks and runtime-specific cloud events affect whether
  any policy is invoked. Repository tests cannot establish that invocation.
- Readonly credentials, scoped service permissions and native sandbox settings
  remain the effective limits when hooks lack coverage.

The generated Codex launcher locates one ancestor workspace ledger, including
from nested checkouts and Git-free copies. Missing or ambiguous roots deny;
launching outside that ancestor tree is unsupported. It does not assume an
undocumented runtime project-root variable. New or changed native definitions
must undergo the runtime's trust process; generation cannot approve them.
See [official-source research](../research/runtime-portability.md).

## Offline checks versus native smoke tests

`python3 tools/verify.py` exercises repository contracts, fixtures, generator
drift and deterministic hook payloads. `python3 tools/workspace/doctor.py`
checks local configuration/prerequisites without authenticating providers.
Neither proves that a live agent loaded the skill, trusted a hook, selected the
right account or can reach a device. Record those as unverified until observed.

In a disposable private workspace, use this native smoke sequence:

1. Record runtime/version, operating system, framework commit and policy mode.
   Complete normal native registration/trust and inspect the active skills.
2. Start a free-text QA task; confirm the router and applicable contracts load.
   Create/edit a harmless documentation file under existing task authorization.
3. Test a harmless denial canary through a mocked operation or isolated empty
   fixture. Observe both native denial and absence of the effect. Never use a
   real force push, credential disclosure or production action as a canary.
   For example, in the disposable workspace set `EXTRA_DENY='qadrillion-hook-canary'`
   in its guard configuration, then ask the native agent to run
   `printf 'qadrillion-hook-canary\n'`. Expect the workspace-specific denial in
   the runtime's hook output; ordinary printed output or a prose refusal is not
   proof of interception. Restore that fixture's original configuration afterward.
4. Check applicable shell/file/MCP paths separately. If strict mode requests
   approval, verify the host's documented behavior, including Codex denial.
5. Connect one actual integration with approved credentials; read its identity
   and a bounded test item. Record auth/tenant/operation gaps separately.
6. Execute one small non-production check, retain actual output, interrupt and
   resume from ticket state. Confirm another engineer can access the evidence.

Preserve output and limitations in the private session record. Treat a missing
native boundary as a support gap; restrict that capability or use a separately
verified environment. Do not claim all runtimes passed from adapter fixtures.
