# Update the Qadrillion Agent landing page

Copy the prompt below into a chat with access to the **Qadrillion website
repository**. It authorizes implementation and verification there, not deployment.
The live page was inspected on 2026-09-24 using public HTML and isolated Chromium
at desktop and mobile widths. Reinspect before editing because it may change.

---

Implement an update to **https://qadrillion.com/repo** in the Qadrillion website
repository. Do the actual source edits, visual checks and build verification;
do not stop at a proposal. The goal is a credible, appealing landing page that
helps engineers understand Qadrillion Agent, try it and contribute or star it.

## Start with the actual source

1. Locate the website checkout, read its AGENTS.md/instructions and current state,
   and inspect the `/repo` route, shared components, design tokens and metadata.
   Preserve existing work and use the project's branch/review workflow. If the
   website source is unavailable, identify that exact dependency; do not pretend
   to have changed the live page.
2. Inspect the current live `/repo` page at desktop and mobile sizes. Record its
   initial state so the final comparison is based on observation.
3. Read the current public framework repository below. The substantive specialist
   upgrade merged in PR #4 at `d593f73`; use current main and its measured support
   boundaries as the factual source of truth. Local framework source may be at
   `/Users/mb/Documents/Projects/qadrillion-agent`, but do not require that path.

Sources:

- Repository/README: https://github.com/Qadrillion/qadrillion-agent
- Entry point: https://github.com/Qadrillion/qadrillion-agent/blob/main/.cursor/skills/qa/SKILL.md
- Shared execution: https://github.com/Qadrillion/qadrillion-agent/blob/main/.cursor/skills/qa-workflow/SKILL.md
- Support matrix: https://github.com/Qadrillion/qadrillion-agent/blob/main/docs/reference/specialist-support.md
- Runtime support: https://github.com/Qadrillion/qadrillion-agent/blob/main/docs/reference/runtime-support.md
- Actual evaluation evidence: https://github.com/Qadrillion/qadrillion-agent/blob/main/docs/evidence/qa-specialists/README.md
- Adoption: https://github.com/Qadrillion/qadrillion-agent/blob/main/docs/adopting.md
- Contributions: https://github.com/Qadrillion/qadrillion-agent/blob/main/CONTRIBUTING.md

## Keep the brand; improve the story

Retain the existing Qadrillion identity: near-black surfaces, off-white type,
restrained warm orange, existing serif wordmark, DM Sans and monospace commands,
with the site's existing spacing, buttons and component conventions. Reuse its
actual tokens and assets. Do not introduce a new theme, font stack or dependency
merely to restyle this page. Keep technical background decoration subordinate to
text and respect reduced motion. Simplify excessive section repetition.

Direction: Persuade. The visitor should understand the outcome, recognize their
QA task, see credible evidence, and reach GitHub or setup instructions.
The first viewport should contain the project identity, a concise promise and a
clear GitHub action. Show the real format of a QA request nearby. Avoid fake
testimonials, invented popularity metrics, unsupported speed claims or terminal
output that looks like an actual run when it is only illustrative.

## Use this content hierarchy

### 1. Hero

Headline: **Give your coding agent a QA workflow.**

Supporting copy: **Investigate risk, write and run tests, diagnose failures, and
hand off evidence across API, web and mobile.**

Identify the project as **Qadrillion Agent**, free and open source under MIT.
Show Cursor, Claude Code, Codex and other capable coding agents as adaptation
targets, without implying identical native activation or enforcement.

Primary CTA: **Explore on GitHub** → repository URL.
Secondary CTA: **Start with /qa** → the task example/setup section.
Keep a copyable clone command if it fits the established design.

### 2. A task visitors recognize

Show this copyable request:

```text
/qa Test checkout across our web app and API.
Verify totals and whether another user can read the order.
Use our existing tools and prepare the results locally.
```

Explain the selection: **Web + API + security**. A mobile lifecycle issue uses
mobile guidance; a latency investigation adds performance; a quick question
bypasses the QA pipeline. A task can be free text or a tracker ticket.
Label any depicted output **Illustrative example** unless it is accurately
extracted and attributed to a specific retained public fixture run.

### 3. Five specialist capabilities

Use five readable entries with concrete outcomes, not a wall of feature labels:

- **API:** Test contracts and boundaries, authorization, persisted state,
  asynchronous completion, idempotency and cleanup.
- **Web:** Author browser tests with observed semantic locators, isolated
  fixtures, authentication setup, meaningful assertions and failure traces.
- **Mobile:** Work through Android/iOS and native/hybrid procedures covering
  build/device identity, permissions, synchronization, lifecycle and diagnostics.
- **Security:** Execute an authorized risk slice, reproduce actor/object access
  failures, reason about impact and state what a narrow check establishes.
- **Performance:** Define a bounded workload, compare a baseline, measure latency
  distributions and errors, enforce thresholds/stops and investigate regressions.

Each specialist covers authoring, execution, debugging and maintenance. Security
and performance are selected when relevant, not attached to every ticket.
Accessibility, exploration, data pipelines and connected-device/BLE work have
focused references; do not market them as fully validated standalone engines.

### 4. How work moves forward

Use a compact sequence: **Understand and identify → route and plan → author and
execute → investigate and retain evidence → report and resume**.

Explain that routine authorized work proceeds without repeated approvals, and
reporting authorization carries forward. Use **Pass | Partial | Fail** for QA:
a confirmed in-scope defect is Fail; missing required coverage is Partial.
The next engineer gets target/build identity, artifacts, limits and next action.

If architecture is useful, distinguish shared contracts, on-demand skills,
bounded subagent roles and executable helpers. Do not make folder counts the
main selling point. Actual shared skills are `qa`, `qa-workflow`, `golden-tasks`;
specialties are `qa-api`, `qa-web`, `qa-mobile`, `qa-security`, `qa-performance`.
`golden-tasks` evaluates the framework's agent behavior, not a customer's
universal smoke suite. Actual bounded roles are `code-explorer`, `code-reviewer`,
`test-runner`, `ticket-writer`, `tracker-reporter`; skills are not separate agents.

### 5. Execution evidence

Describe the retained evaluation: isolated agents authored tests against real
HTTP services, Chromium/Firefox and a real Android emulator. Seeded defects were
detected; corrected fixtures passed the detecting assertions unchanged. Failed
attempts, diagnostics, cleanup and reporting corrections remain inspectable.

Link to **See the evaluation evidence** and **View the support matrix**.
Keep limits adjacent to relevant claims. The original corrected Android suite
was 10 passed, 2 skipped (Partial). iOS, physical devices, hybrid/BLE and
Appium/Maestro feature execution were not validated in this evaluation. Recipes
and available tools are not proof of execution. Actual CI and test counts may be
included as a dated snapshot if reverified; do not make them evergreen guarantees.

### 6. Get started and adapt

Use the repository's verified setup commands:

```bash
git clone https://github.com/Qadrillion/qadrillion-agent.git qa-workspace
cd qa-workspace
python3 tools/agents/sync.py
python3 tools/verify.py
python3 tools/workspace/doctor.py
```

Prerequisites: Python 3.11+, Git and Bash. Offline checks run on macOS/Linux;
Windows setups need local WSL/Git Bash verification. Coding agents and chosen
test tools are separate prerequisites for live execution. Existing test suites,
product source and a tracker help but are not universally required.

Explain private adoption before company data: establish a private workspace and
verify its remote/visibility, configure actual tools in `qa-config.json` and
repository ownership in `workspace-manifest.json`, then pilot a known
non-production task. Link the adoption guide. Do not imply cloning alone
authenticates providers, connects devices or installs Appium/Playwright.

### 7. Short FAQ and contribution invitation

Cover agent/tool compatibility, privacy, setup and limits concisely. There is no
framework telemetry or required Qadrillion account; coding agents and connected
providers have their own accounts, costs and data policies. Guards are defense
in depth, not a sandbox. Coverage depends on native registration, trust and
events; production execution is excluded. See runtime support for measured scope.

End with GitHub/contribution links and one restrained invitation to star the
project if it is useful. Keep any Qaido/service promotion secondary; do not assert
technical parity, integrations or commercial usage without independent evidence.

## Remove these observed stale claims everywhere on this route

Check visible copy, replay illustrations, FAQs, tooltips, metadata and structured
data. These were present on the public page inspected on 2026-09-24:

- Cursor/Claude-only positioning that omits Codex and the generic-agent path.
- Nonexistent skills: `acceptance-criteria→test-cases`, `defect-taxonomy`,
  `golden-task-regression`, `exploratory-charters`, `automate-in-your-framework`.
- Nonexistent role names: `test-designer`, `automation-engineer`, `blind-reviewer`.
- Nonexistent hook names: `deny-destructive-on-tracked-artifacts`, `no-done-without-run`.
- “Up to five” test attempts and “iteration 2/5”. The rule is at most one
  diagnostic rerun for a stated hypothesis; a repair gets a separately identified
  verification run, with original failures preserved.
- Mandatory human sign-off for every routine update. Ask for unresolved material
  decisions or unauthorized irreversible actions; preserve task authorization.
- Absolute claims that hooks cannot be bypassed or prevent all test edits/deletes.
- `SHIP` despite a reproduced in-scope defect, invented runs/videos/tickets
  presented as real evidence, or unlabelled simulated transcripts.
- “We use it daily on Playwright and Appium” unless separately substantiated.
- A requirement for an existing repository with tests and the unqualified
  “nothing is sent to us” privacy claim.

As additional writing constraints, do not introduce universal stack certification,
unmeasured 99% autonomy or token-saving promises. These are precautionary limits,
not claims observed on the inspected landing page.

## Metadata and verification

Update the page title, description, Open Graph and Twitter copy consistently.
Suggested title: **Qadrillion Agent | Open-source QA for coding agents**.
Suggested description: **An open-source QA framework for Cursor, Claude Code
and Codex. Author and run API, web and mobile tests with scoped security,
performance checks and evidence.**
Keep the canonical URL `/repo`. Reuse the site's social-image pipeline if one
exists; do not leave an old sign-off claim embedded in preview text or artwork.

Before finishing:

1. Run the website repository's required lint, type, test and build checks.
2. Render desktop and mobile, including 320px/390px widths and 200% zoom. Check
   hierarchy, wrapping, overflow, readable contrast, focus and reduced motion.
3. Exercise navigation anchors, GitHub/docs links, copy controls (including success
   and failure feedback) and any FAQ accordion with keyboard and pointer input.
4. Verify that examples are labelled, support limits match current source, and
   stale identifiers/sign-off/retry/absolute-enforcement claims are removed.
5. Capture actual before/after screenshots, retain test results and obtain the
   project's required independent review. Fix in-scope findings.
6. Deliver committed changes or a review-ready PR, a short account of the copy
   and layout improvements, checks and exact remaining limits. Do not deploy
   unless I explicitly authorize deployment.

Proceed with routine edits and verification under this task authorization.
Ask only for a material decision that the website source and this brief cannot
resolve. Do not modify the QA framework while implementing this website task.
