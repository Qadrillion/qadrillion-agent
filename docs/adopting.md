# Adopt or upgrade the framework

Start in a private team repository before adding company information. The public
repository is a reusable template; it is not the place for your tickets, source
checkouts, credentials or test evidence. See the [team workflow](reference/team-workflow.md)
for shared ownership and upgrades.

## First setup

1. Clone the template and establish the private repository's visibility and remote.
   Install Python 3.11+, Git and Bash. Use macOS/Linux, or validate a WSL/Git Bash
   setup before relying on it.
2. Describe actual repositories in `workspace-manifest.json`: root, expected remote,
   canonical branch, ownership, scopes and allowed mutations. Do not leave fake
   nested repositories. Status checks do not fetch; updates are explicit.
3. Start with the closest [configuration example](../examples/config/). Configure
   `qa-config.json` with available capabilities, runner argv/cwd/artifacts and
   required non-production identity evidence. Examples are disabled declarations,
   not installed tools. [Configuration contract](reference/qa-config.md).
4. Connect the systems that supply requirements, test execution and useful evidence.
   Tracker, source, CI, logs and artifacts usually help; none is universally required.
   Use native authentication and scoped accounts. Never paste credentials into a
   prompt or commit them. Choose CLI/API/MCP by verified coverage, policy and measured
   cost; see [integrations](reference/integrations.md).
5. Review `.cursor/hooks/guard.conf`. Add actual production hosts and protected
   folders. The default `targeted` profile leaves ordinary edits and authorized
   tool work to task instructions and native permissions; use `strict` only when
   your organization needs the extra gates. Add payload tests for your changes.
6. Run the committed tools:

   ```bash
   python3 tools/agents/sync.py
   python3 tools/verify.py
   python3 tools/workspace/doctor.py
   ```

   Doctor is offline: it validates configuration and executable availability, not
   authentication, remote access or native hook activation.
7. Follow [runtime support](reference/runtime-support.md) to inspect discovered
   skills/agents and observe hook behavior in a disposable workspace. Cursor is
   the first pilot here. Repeat native checks after hook/runtime upgrades.
8. Replace `docs/STATE.md` with your current work and populate known quirks only
   from verified evidence. Keep long-lived conventions in scoped rules and
   on-demand references. Run a small non-production ticket through QA and handoff.

A free-text task with supplied requirements works without a tracker. A product
with no available source can be tested through its observable interface; record
that coverage boundary. Do not invent missing connections or evidence.

## Upgrade an existing work laptop

Create an upgrade branch or separate checkout and record the existing template
revision. Preserve company config, tickets, artifacts, runtime settings, auth and
local customizations. Compare a pinned public revision, then bring in framework
changes deliberately; do not replace the company repository with a fresh public
clone or run an installer that overwrites its settings.

Review conflicts in canonical `.cursor` files before running the synchronizer.
It refuses unexpected edits to managed output: reconcile those edits at their
source instead of forcing over them. Run verification, review native trust changes,
and pilot one ticket before making the upgrade the team's default. Coordinate
one writer per checkout; each engineer uses separate credentials and worktrees.

## The first Cursor pilot

Use one representative ticket on a known non-production build. Verify requirement
retrieval (or supplied text), source review where available, risk-based checks,
test execution, failure evidence, and an accurate report. Ask explicitly for
publication if it is part of the task; that authorization carries through routine
reporting without repeated approval questions. Then pause and resume from the
ticket state, ideally with another engineer, and confirm the artifacts are accessible.

Record runtime/model, source/build/config identity, elapsed time, actual usage or
cost where available, human interventions, verdict and remaining coverage. Retain
failures and missing integrations. Offline tests passing is not a live pilot.

## Measure before making claims

Compare the same representative task set and output quality before and after a
change. Track input/output tokens, latency, provider costs, intervention count,
useful checks completed and defects missed. Include tool pagination and retries.
Word counts are a prompt-size proxy, not token usage. MCP versus CLI has no
universal winner, and no 99% autonomy claim is established by this repository.
