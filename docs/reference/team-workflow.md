# A shared framework with private team evidence

Use public upstream for reusable skills, adapters, schemas, examples and
sanitized regression fixtures. Real tickets, internal source, environment
details and test artifacts belong in a separate private team workspace with
appropriate access. A public fork is not private storage.

Create the private workspace using your organization's approved repository
workflow, retain the framework's license and record the adopted upstream commit.
Before adding company data, inspect all remotes and repository visibility.
Do not push private workspace history or evidence to the public upstream.
Contribute generic fixes from a clean branch or separate checkout with sanitized
examples. Inspect diffs and artifact contents before publication.

## Each engineer's setup

Keep the team's common conventions and reviewed runner declarations in its
private repository. Each engineer uses their own permitted authentication and
local runtime configuration; credentials are never shared through Git. Use
[adoption](../adopting.md) and [runtime support](runtime-support.md) to validate
the actual machine. Generated files do not prove discovery or trust.

One writer works in a checkout at a time. Concurrent engineers or agents use
separate clones/worktrees and branches, then reconcile their changes. Ticket
`owner` and `branch` fields describe responsibility; they are not a distributed
lock. Agree ownership through the team's existing coordination mechanism.
Routine work proceeds under the task's authorization without per-file approval.

## Handoff contract

`tickets/{ID}.md` is the durable task record; its frontmatter carries status,
next action and blockers. `docs/STATE.md` is the current workspace handover, and
dated session entries retain history. Keep all three concise and consistent.

A useful handoff records:

- Task/criteria, current owner and next owner or explicit unassigned status.
- Branch, commit and dirty files, including uncommitted work that must travel.
- Source/deployed build, target identity and relevant configuration version.
- Commands/checks performed, actual outcomes and artifact locations.
- Known defects, failed attempts, untested scope, blockers and exact next action.
- Tracker draft/posted state and returned identifiers for completed writes.

Commit or explicitly transfer authorized local work before switching machines.
An ignored local log or a path on another engineer's laptop is not accessible
handoff evidence. Store redacted artifacts in approved shared storage with
retention/access suitable for the team; verify the recipient can access them.
The framework does not provide that storage or automatically upload artifacts.
Ticket frontmatter `evidence` accepts local paths relative to the ticket, not
remote URLs. Keep shared-storage links in the ticket body; retrieve referenced
artifacts into the declared local paths when needed, or retain decisive actual
execution output in the execution section. The validator checks structure and
file presence, not the truth of a result or a recipient's remote access.

Resume from ticket state, then inspect only the referenced evidence needed for
the next step. Recheck source/build/configuration identity. A previous Pass does
not cover a changed target, missing artifact or newly added criterion. Preserve
both engineers' observations when resolving conflicts; never silently replace a
failed run with another person's green run. Regenerate the ticket index after
reconciling state.

## Upgrade an existing work laptop

Record the current framework commit, runtime versions and local customizations.
Use a new branch or separate checkout to review the chosen upstream version.
Reconcile framework files with company overrides; do not overwrite private
configuration, ticket state, evidence or authentication.

Run `python3 tools/agents/sync.py --check` before deciding how to regenerate.
The generator tracks its own files and rejects unexpected edits; inspect those
conflicts and preserve intended local changes. Then regenerate with
`python3 tools/agents/sync.py` and run `python3 tools/verify.py` plus
`python3 tools/workspace/doctor.py`. Review changes to native hooks and complete
the runtime's trust/reload process on that machine.

Validate one representative task in the new branch, including interrupted-task
resume and artifact access from another engineer's checkout. Merge into the
private team's branch after its normal review. Record the adopted version and
new limitations. This is an explicit upgrade procedure; there is no automatic
private-state migration, background synchronization or cross-machine lock.
