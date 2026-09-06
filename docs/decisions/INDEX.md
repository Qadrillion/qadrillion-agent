# Decisions

The only file in this directory read at session start. Titles and one line
each; open a record only when it is relevant to the task at hand.

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-boundaries-are-hooks.md) | Boundaries are hooks, conventions are rules | accepted | 2026-09-06 |
| [0002](0002-no-auto-rerun.md) | A failure is a finding — no automatic re-run | accepted | 2026-09-06 |
| [0003](0003-agents-never-target-production.md) | Agents never target production; release is human | accepted | 2026-09-06 |
| [0004](0004-locators-are-source-grounded.md) | Locators are source-grounded, with two proofs | accepted | 2026-09-06 |
| [0005](0005-state-is-overwritten.md) | Live state is overwritten; history is appended and never read cold | accepted | 2026-09-06 |

## Anti-patterns established here

Named so they generalise to cases nobody has met yet:

- **Do not write "never …" in prose.** If it must always or never happen, it is a hook. (0001)
- **Do not re-run to get green.** A second failure is data, not noise. (0002)
- **Do not let a config file tell you it points at staging.** Read the target's role from the provider before an agent may act on it. (0003)
- **Do not invent a locator the app does not ship.** The fix is a product PR. (0004)
- **Do not read the log to find out where you are.** State is one overwritten file; if it is not enough, the file is wrong, not short. (0005)
- **Do not keep two editable copies of one contract.** Rules own contracts; skills and subagents reference them. (0001)
