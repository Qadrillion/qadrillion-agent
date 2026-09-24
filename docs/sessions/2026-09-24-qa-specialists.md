# Specialist implementation and evaluation

Owner: framework maintainer. Branch: `feat/qa-specialists`.
Base: `91e9bb0d4dcbfe812963fe6f04f4387c1b664497`, merged portability PR #3.
Initial checkout clean; existing feature branch retained; main fast-forwarded.

The [frozen acceptance spec](../specs/2026-09-24-qa-specialists.md) precedes
implementation. [Architecture](../reviews/2026-09-24-specialist-architecture.md),
[research](../research/specialist-practices.md), [support matrix](../reference/specialist-support.md)
and [retained evidence](../evidence/qa-specialists/README.md) contain stable detail.

Implemented five progressive skills, risk-selected routing, conditional recipes,
focused accessibility/exploration/data/BLE guidance, optional HTTP/Android targets,
bounded measurement, task-only evaluation workspaces and agent-authored replay.
Existing generic roles and shared contracts retain ownership. No mandatory new
tool, language, cloud, tracker or specialty-agent fleet was added.

Actual work: four native Codex authoring sessions, one isolated Android author,
nine completed routing/action scenarios, independent evidence review and corrected
targets. Failures and provider-interrupted attempts are preserved. Android's two
input-protocol skips remain Partial; iOS/Xcode and Cursor-native dependencies are
explicit, not work deferred to a company laptop. HTTP/browser fixtures and owned
emulator were stopped; only evidence/build/dependency files remain in temporary
storage. No company accounts or data were used or published.

Verification: baseline and integrated offline suites passed; five bundled skill
validators passed after PyYAML was installed in a task-specific venv. Eight
bad/good API/security/performance/browser replays met expected outcomes, including
real Chromium/Firefox. Generated copies were refreshed. Clean-clone verification,
blind review and CI are recorded in the spec's final implementation record.

Native counts: nine completed Codex turns expose actual usage; root, mobile
collaboration and review usage is unavailable. No savings/autonomy percentage is
claimed. Native discovery observations are narrower than hook/permission support.
Tracker publication: no QA tracker posting. The requested public framework PR
is the sole external deliverable; merge remains with the user.

Final hardening: six in-scope blind-review findings were fixed. Browser diagnostics
can no longer skip owned-data cleanup; performance output is reserved before
traffic and malformed identity receives retained blocked evidence; the mobile
stack claim is corrected; shipped native replay resolves its contract and validates
a caller-pinned owned emulator rather than the author’s historical serial.

A fresh emulator-5562 native replay detects two lifecycle failures and passes both
on the corrected APK, with identical test bytes. App/device state was cleaned.
Business-method ASTs are unchanged. Offline coverage is now 152 Python tests plus
75 guard cases. Final blind review is PASS with zero deferred findings. See the
spec implementation record for final publication and CI.
