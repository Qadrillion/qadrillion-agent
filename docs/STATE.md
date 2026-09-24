# State — Qadrillion Agent

Updated: 2026-09-24. Owner: framework maintainer session.
Branch: `docs/repository-presentation`. Base: `d593f73` (merged PR #4).
Implementation base/acceptance checkpoint: `34f817a`; presentation commit follows.

Task: refresh GitHub presentation and supply a separate website implementation
prompt before the private laptop pilot. Current main and existing work were
preserved. PR #4 is merged; this task changes documentation only.

Updated root README and two runnable-reference guides. All six tracked READMEs
were inspected; the canonical configuration guide and two historical evidence
READMEs remain unchanged. The website was inspected read-only; its source and
live deployment were not changed. The copyable handoff is
[the website prompt](prompts/update-repo-landing-page.md).

Checks: 153 Python tests, 75 guard payloads, local doctor, six HTTP and eight
HTTP/browser replay outcomes pass. Forty-four local links/anchors resolve.
Desktop light/dark and 320px/390px local GitHub-style renders have no page-width
overflow. Generated adapters are current. See
[verification](evidence/repository-presentation/verification.md) and
[acceptance/review record](specs/2026-09-24-repository-presentation.md).

Review: PASS after two documentation findings were corrected; zero unresolved or
deferred. The reviewer independently passed offline, replay and render checks.
Dirty paths: none after the presentation/completion commit; no unrelated work.
Next: maintainer reviews and merges the presentation PR, then uses the website
prompt in the website checkout and pilots the framework privately. The task's
final handoff links the published PR and exact hosted-check result.
No website deployment or popularity/conversion uplift is claimed. Existing
runtime/mobile execution limits remain in the support matrix. No company data
or accounts were used.
