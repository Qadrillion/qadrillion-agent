# Public GitHub page

Light path. The page is the product's front door. The agent layer itself is out of scope.

## Acceptance criteria

| # | Criterion | Failure it guards | Verification |
|---|---|---|---|
| 1 | `main` rejects force-push and deletion, a merge requires a pull request, and the `governance` check must pass. No bypass actor. Zero required approvals. | A rewritten history, or a push to the default branch that never ran CI. A review count of 1 would lock the only maintainer out. | `gh api repos/Qadrillion/qadrillion-agent/rulesets` |
| 2 | The About panel description names the QA agent, Cursor, and Claude Code; homepage is `https://qadrillion.com/repo`; topics cover QA and agentic testing. The repo is a template. Secret scanning and push protection are on. | An empty About box, so GitHub search and Google have nothing specific to index. A public repo that will accept a committed token. | `gh api repos/Qadrillion/qadrillion-agent` and `/topics` |
| 3 | The README opens with the Qadrillion header, the real clone URL, and the existing contract: hooks as boundaries, no Pass without evidence, not a test platform, a human signs the artifact. | A decorated page that drops the product or invents a claim. | Read `README.md`. Header file exists. |
| 4 | Code of conduct, contributing, security policy, and an issue form are present. Copy does not name a parent company, say "10x", call the agent a replacement, or say the paid app is for sale. | A half-finished public repo, or a claim the company cannot stand behind. | `gh api repos/Qadrillion/qadrillion-agent/community/profile` and a read of the diff. |
| 5 | `docs/STATE.md` stays a handover with the same headings an adopting team overwrites. | Replacing the skeleton's state file with a diary, so a clone has nothing to start from. | Read `docs/STATE.md`. |

## Assumptions

Admins are not exempt from the ruleset. A pull request needs zero approving reviews, so the maintainer merges after CI. Discussions stay off. No release tag in this change.
