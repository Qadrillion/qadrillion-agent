# Runtime portability and integration research

Official sources inspected on 2026-09-24. Runtime discovery, hooks and vendor
commands change: verify the installed version before relying on a documented
feature. This research did not activate native hooks, authenticate a company
integration or benchmark tokens. Local `codex --version` reported 0.154.0;
`twg` and `acli` were absent from PATH. Repository test results belong in the
[audit](../reviews/2026-09-24-framework-audit.md), separately from these findings.

## Instructions travel; discovery and enforcement differ

Codex builds an instruction chain from global and project AGENTS files, with
directory scope affected by where a session starts. Its skill discovery includes
project `.agents/skills`; metadata precedes full skill loading. Duplicate skill
names are not merged. This supports a compact bootstrap and on-demand content,
but does not prove the checked-in files loaded in a particular session.
[OpenAI AGENTS documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills).

Claude documents `.claude/skills` as its project skill root. Its newer native
AGENTS support has version and precedence conditions; a checked-in `CLAUDE.md`
with `@AGENTS.md` remains a documented compatibility path. Cloud project content
does not imply availability of someone's home-directory skills.
[Claude skills](https://code.claude.com/docs/en/skills),
[Claude memory](https://code.claude.com/docs/en/memory).

Cursor documents `.cursor/skills`, `.agents/skills` and compatibility roots
including `.claude/skills`. Its scoped `.mdc` rules are a separate instruction
mechanism. Installing copies in multiple discovered roots can create ambiguity;
this research did not establish deduplication or precedence for identical copies.
[Cursor skills](https://cursor.com/docs/skills),
[Cursor rules](https://cursor.com/docs/rules).

The repository keeps `.cursor` as its maintained source for existing adopters
and generates portable copies and runtime adapters. That is a compatibility
choice, not a claim that one directory works identically everywhere. Native
subagents are optional; another runtime can execute the roles sequentially.
Readonly metadata must survive generation: Codex supports a readonly sandbox
setting and Claude supports restricted tool lists.
[OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Claude subagents](https://code.claude.com/docs/en/sub-agents).

## Hooks need runtime-specific verification

Codex requires native trust for project hook definitions; changed definitions
can be skipped until trusted. Hosted tools and subsequent interactive
`write_stdin` input are outside its general PreToolUse coverage. Its documented
unsupported approval response must not be emitted as an effective approval gate.
The repository therefore translates a policy `ask` into a native denial for
Codex and preserves runtime permissions when policy allows an action.
[OpenAI hooks](https://learn.chatgpt.com/docs/hooks).

Claude distinguishes a valid denial or supported blocking exit from ordinary
hook errors; malformed output is not a reliable block. Cursor exposes
`failClosed` for failures/timeouts, while some cloud exploration paths omit
hooks. Shared policy logic consequently needs native event/response adapters,
valid JSON on errors and separate live registration tests.
[Claude hooks](https://code.claude.com/docs/en/hooks),
[Cursor hooks](https://cursor.com/docs/hooks).

The adopted policy is narrow by default: routine edits and authorized task work
proceed, while destructive operations, production execution and credential
disclosure retain targeted protection. Organizations can opt into stricter
gating. Neither policy can infer complete user intent from command text or a
tool name. Native credentials, server authorization and the agent's task scope
remain necessary. A denial never justifies switching transports to bypass it.
See [runtime support](../reference/runtime-support.md) for actual coverage gaps.

## Atlassian's CLI products are different surfaces

Teamwork Graph CLI (`twg`) is the relevant new agent-oriented Atlassian CLI. Its
overview, updated 2026-09-23, describes Teamwork Graph and multiple Atlassian
Cloud products. ACLI is a separate CLI with explicit Jira work-item commands;
Rovo Dev CLI is an agent host that can itself connect to MCP servers.
[TWG overview](https://developer.atlassian.com/cloud/twg-cli/),
[ACLI Jira search reference](https://developer.atlassian.com/cloud/acli/reference/commands/jira-workitem-search/),
[Rovo Dev MCP configuration](https://support.atlassian.com/rovo/docs/connect-to-an-mcp-server-in-rovo-dev-cli/).

Atlassian describes TWG and MCP as complementary. Shell and graph workflows may
favor the CLI, while simple MCP requests can require fewer turns. The guide
recommends one primary interface per session or explicitly choosing one per
operation; it does not support a universal token or speed winner.
[Atlassian decision guide](https://support.atlassian.com/atlassian-ai-gateway/docs/teamwork-graph-cli-and-atlassian-mcp-decision-guide/).

Authentication and policy are part of that choice. TWG documents OAuth for
product data and separate mechanisms for Bitbucket and administration. Rovo MCP
supports OAuth and, when administrators permit, API tokens. Its data-security
policy control applies to OAuth, not API-token authentication or custom MCP
servers. Changing transport/authentication is therefore not automatically
policy-equivalent.
[TWG authentication](https://developer.atlassian.com/platform/teamwork-graph/twg-cli/getting-started/how-authentication-works/),
[Rovo MCP authentication](https://support.atlassian.com/atlassian-ai-gateway/docs/authentication-and-authorization/),
[Atlassian policy scope](https://support.atlassian.com/security-and-access-policies/docs/prevent-atlassian-rovo-mcp-server-access/).

The developer FAQ says enriched TWG operations can consume Rovo credits; older
support material still describes beta free usage. Installation/update wording
also differs between pages. Do not advertise all operations as free or invent
command syntax: inspect installed `--help`, version and available commands.
[TWG FAQ](https://developer.atlassian.com/cloud/twg-cli/faq/),
[TWG setup](https://support.atlassian.com/organization-administration/docs/get-started-with-twg-cli/).

## Efficiency is a measured workflow property

Anthropic identifies tool definitions and intermediate results as significant
context costs and demonstrates filtering/code execution in a worked example.
That example is not this framework's benchmark or proof that every MCP setup is
expensive. Claude also documents deferred MCP tool loading where host/model
support permits it; deployment paths differ.
[Anthropic engineering article](https://www.anthropic.com/engineering/code-execution-with-mcp),
[Claude MCP documentation](https://code.claude.com/docs/en/mcp).

The framework's resulting recommendations are to load only relevant skills and
capabilities, choose a primary transport, bound queries and retain raw evidence
outside the prompt. Measure equivalent complete tasks across cold and warm
sessions: input/output tokens where exposed, tool calls, elapsed time, billed
operations, successful outcomes and authorization behavior. Record pagination
and truncation so a smaller response cannot masquerade as complete coverage.
No comparative token, latency or cost savings are claimed here.

`qa-config.json` is a declarative inventory, not an implementation of every
provider or an authorization broker. Offline doctor checks configuration and
local prerequisites; it does not prove login, tenant access, native discovery or
hook trust. Live identity checks and harmless native smoke tests remain separate
adoption steps. Public framework upgrades and private team evidence also need
separate handling, described in the [team workflow](../reference/team-workflow.md).
