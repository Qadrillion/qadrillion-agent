# Configuration contract

`qa-config.json` is a version-1 declarative inventory read by the QA orchestrator.
`tools/workspace/config.py` validates it; doctor calls the same validator. It is
not a runner, auth broker, automatic tool router or enforcement engine.

| Field | Meaning |
|---|---|
| `schema_version` | Integer 1 |
| `project.name`, `project.scopes` | Name and relevant QA surfaces; empty scopes valid before adoption |
| `integrations[]` | Unique id, provider, cli/api/mcp/manual transport, capabilities, tenant/project scope, explicit enabled boolean; CLI additionally names executable |
| `environments[]` | Unique id, declared role, description of required independent identity evidence |
| `runners[]` | Unique id, supported scopes, enabled boolean, reviewed argv list, workspace-relative cwd and artifact directory |
| `context` | Positive max_result_chars and max_search_results; guidance for bounded retrieval, not byte/token enforcement |
| `policy` | production_execution false; external_writes task-authorization |

Use `other` for a product outside the named surface categories. Capability names
describe the operation (for example tracker.read or observability.read) rather
than claiming a provider tool exists. Resolve actual commands/tool schemas in the
installed version before use. A disabled example does not establish access.

`task-authorization` carries the user's authorization through the requested work.
An instruction to publish a task's QA result authorizes routine reporting to that
destination without approving each generated sentence again. A testing request
alone does not authorize unrelated messages, deployment or destructive changes.
Ask only when the required external action lacks authorization or its destination
or scope materially changes. Native permissions still apply. This declaration
does not alter runtime permissions or hook policy: `.cursor/hooks/guard.conf`
defaults to a targeted profile; organizations can opt into its stricter gates.

Runner paths cannot contain parent traversal, absolute or home paths. Doctor also
checks enabled runner directories for resolved-path escape. Commands are argv
arrays for review; no tool in this inventory automatically executes them. The
agent selects the existing command and result format from the actual repository.
Shell pipelines should live in reviewed project scripts, not interpolated ticket
text. Runner environment/credentials are supplied through the team's native
execution/auth mechanism, never secret values in this file.

Environment roles are dev, test, staging, production or unknown. A role label is
not proof. Record provider/deployment/device identity in the ticket before a
mutation. Declaring production does not authorize test execution there.

Repository ownership remains in `workspace-manifest.json`, schema version 1.
Each entry names an id, workspace-relative path, role, expected origin remote,
ownership (owned/dependency), canonical branch, exact allowed_mutability values
and scopes. `refresh.py` validates and inspects this separately. Status is the
default; explicit update requires matching origin, the canonical clean branch,
successful fetch and declared fetch/fast-forward permissions. Worktrees are valid
repositories; ordinary nested folders are not. Remote URL spelling must match
the manifest (SSH and HTTPS are not silently treated as equivalent).

Private-team and runtime details belong in the corresponding on-demand guides.
Unknown fields may carry team metadata; they do not create automatic capabilities
or relax the required policy fields.
