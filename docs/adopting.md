# Adopting this in your team — the checklist

The skeleton is generic on purpose. A real team workspace built on it should end up with every row
below ticked. Rows marked **measure** produce a number; write the number down before and after — a
setup change without a measurement is an opinion.

## 1. Fill in (day one)

- [ ] `workspace-manifest.json`: your automation repo(s) and product checkouts, each with an
      `allowed_mutability` list. Product source is `ticket-scoped-content-edit` at most.
- [ ] `.cursor/hooks/guard.conf`: `PROD_SELECTORS` names your production hosts and environment ids,
      not just the word "prod"; `PROTECTED_PATHS` names any other client's folder on the machine;
      `MCP_DENY_SERVERS` names the cloud/marketplace variants you must never use here.
- [ ] `.cursor/hooks/tests/run-tests.sh`: add one payload per real fence you added (the prod host, the
      protected path, your tracker's write tools). Run it. Green.
- [ ] `.cursor/mcp.json` (gitignored) from the `mcp.*.example.json` templates; ≤3 servers; a
      credential-bearing server never goes in `~/.cursor/mcp.json`.
- [ ] `AGENTS.md`: the product name, the stack row, your classification signals. Stay under ~600 words;
      if you are writing "never …", stop and add a `guard.conf` line instead.
- [ ] Rules: one contract per file, glob- or description-matched. `core.mdc` is the only always-on rule
      and stays under 120 words (CI enforces).
- [ ] `docs/STATE.md` from the template; `docs/decisions/INDEX.md` with the decisions you already live
      by but never wrote down (staging-only, no auto-rerun, which tracker, which Postman/collection is
      canonical, Story vs Task validation).

## 2. Verify (once per machine, then after every hook edit)

- [ ] The acceptance test: ask the agent for a hard `git reset` in a scratch repo → the deny message
      appears in the Hooks output channel. Not the model refusing; the hook.
- [ ] A tracker write through MCP asks before posting; a denied server is denied.
- [ ] `claude -p` in the same folder: one deny observed in the transcript before any unattended run.
- [ ] `/golden-tasks run` — the three starters pass (`cold-start`, `bare-ticket-id`, `prod-request`).

## 3. Measure (the numbers that make it an engagement, not a vibe)

- [ ] **measure** Cursor Context Usage panel, fresh Agent chat at the workspace root: system / tools /
      rules / skills / MCP + dynamic / subagents. Before you change anything, and after.
- [ ] **measure** Always-on operator prose in words (`AGENTS.md` + every `alwaysApply: true` rule +
      anything they `@`-import). Target: under ~1,000 words.
- [ ] **measure** Tickets moved to `done` with a run artifact attached and zero human re-prompt, per
      month. This is the product's own number; publish it when it exists.
- [ ] **measure** Defect escape rate on the surfaces the agent covers, before and after.

## 4. Patterns a mature workspace has (harvested from real setups; rebuild, do not copy)

- [ ] **Locator contract with provenance.** Registry entries carry a `source_ref`; an offline audit proves
      the identifier is in source; a live smoke proves it is in the installed build and stamps a
      provenance file; misses are quarantined, never guessed. Two proofs for two claims.
- [ ] **Strict xfail as a spec-discrepancy instrument.** A test that captures a product-vs-AC disagreement
      is `xfail(strict=True)`, documented as "do not fix the test", and flips to XPASS when the product
      reconciles. Won't-fix items have a decision record so nobody re-files them.
- [ ] **No auto-rerun plugin.** Flaky = re-run once, then it is a finding with both outputs.
- [ ] **Evidence gates in five places, same sentence.** AGENTS, the test rule, the skill, the subagent,
      the PR template: "no Pass without execution evidence".
- [ ] **One rule owns each contract.** `[SEVERITY]` output, ticket schema, tracker comment format —
      subagents read the rule, never restate it.
- [ ] **Reviewer feedback is a convention change, not a file change.** Fix all occurrences, fix the
      convention that produced it, add a mechanical gate over a written reminder. Twice-repeated
      corrections become a golden task, then a hook or rule — never a third correction.
- [ ] **Ticket state machine** (`analyzing → analyzed → planned → in_test → reporting → done`, `blocked`
      from anywhere) with `next_action` + `blockers` as the resume payload; write early at `analyzed`.
- [ ] **Manifest-declared mutability** and a refresh script that never switches branches.
- [ ] **`verify.sh` = the exact script CI runs.** Local red predicts CI red.
- [ ] **Drift tests over the workspace itself.** The continuity hook, the ticket index, the baseline
      contracts, the repository state — all in CI. The setup tests its own setup.
- [ ] **Two-proof rule for MCP writes.** Write tools whitelisted and delete tools omitted at the server
      config, *and* every write verb asks at the hook.
- [ ] **State is overwritten; history is appended; drafts are neither.** A live-state file that grows
      past 60 lines is a smell: the detail belongs in a ticket file.

## 5. What to do with the numbers

Put the before/after pair in your own `docs/decisions/` record for the adoption, with the date. If a row
in §4 is not ticked after a month of use, either the pattern does not apply to your stack (write that
down) or the workspace is drifting (fix the gate, not the reminder).
