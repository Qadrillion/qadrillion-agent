# Cursor native smoke — Partial (authentication blocked)

Cursor Agent CLI `2026.09.23-86fc751` is installed. Its status command returns `Not logged in` (exit 0). The explicit `/qa` read-only attempt returns exit 1 in 1.165 seconds:

```text
Error: Authentication required. Please run 'cursor agent login' first, or set CURSOR_API_KEY environment variable.
```

No login, supplied API key, account switch, integration connection, personal configuration edit, trust change or permission override was attempted. The parent session's earlier `cursor agent --help` automatically installed the missing CLI; this smoke did not run an installer. No personal or company identity is inferred.

## Environment and scope

- macOS 26.6.2 arm64.
- Cursor editor `3.21.18`, revision `c4730f7d93d787d9ab120af715999f0345ee5bc0`.
- Source HEAD `06d1dac7e6c9035ed63ce661849952f0032032f1`; files copied from the working tree, including its complete framework skill roots. This is not a clean-commit test; `skill-manifest.json` pins copied skill bytes.
- Disposable workspace: `/tmp/qadrillion-cursor-smoke/workspace`.
- All three framework roots are present: `.cursor/skills`, `.agents/skills`, `.claude/skills`. Each contains eight skill names. Each name has three identical bodies according to filesystem SHA-256 inventory. No `.codex/skills` exists in this framework.

## Evidence boundaries

| Check | Observation |
|---|---|
| Files and equal copies | Confirmed by local filesystem inventory only |
| Native metadata discovery | Unverified; no stream events emitted |
| Native duplicate handling | Unverified; identical copies do not establish deduplication |
| Explicit `/qa` invocation | Attempted; rejected for missing authentication |
| Full qa/workflow/web bodies | No native read observed |
| Browser-only web specialty routing | Unverified |
| Implicit selection | Not attempted after auth blocker |
| Read-tool operation | Unverified |
| Benign hook activation | Unverified |
| Hook denial enforcement | Not attempted |
| Editor skill list | Not inspected; this was a CLI smoke |

The stdout JSONL file is deliberately empty. There are no model responses, tool events, skill reads, hook events or usage records to extract. Tokens, model and cost were not reported; no zero-cost claim is made.

## Commands and artifacts

The version/status commands were `cursor --version`, `cursor agent --version`, `cursor agent --help`, and `cursor agent status`.

The execution argv and complete prompt are preserved in `request.json`:

```text
cursor agent --print --output-format stream-json --mode ask --workspace /tmp/qadrillion-cursor-smoke/workspace '<prompt in request.json beginning /qa>'
```

The prompt asks for native qa/qa-workflow/qa-web registrations and duplicates, complete body reads, and hypothetical web-only specialty selection. It prohibits edits, external integrations, authentication, installation and outside-workspace inspection. The CLI did not reach the prompt execution.

`native-evidence.json` contains the machine-readable classification. `raw/` retains editor/CLI versions and help, redacted auth status, empty native stdout and exact stderr. `metadata.json`, `skill-manifest.json`, and `static-skill-inventory.json` pin the copy.

[Cursor skills documentation](https://cursor.com/docs/skills) describes project `.agents`, `.cursor`, compatibility `.claude`/`.codex` roots and deferred body loading. Documentation is not evidence that this CLI discovered or deduplicated the copied files. CLI options were checked against its installed help.

Next prerequisite: an authorized authenticated Cursor CLI session. Run the preserved request once that external prerequisite is satisfied, then separately observe metadata, body reads, implicit selection, read tools and native hook behavior. No company account login is required by this report.
