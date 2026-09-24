# Research behind the QA workflow

Inspected on 2026-09-24. This is a selected set of 12 primary works, not a
popularity ranking or a claim to have read ten complete books. The framework's
rules are adaptations of the practices below; none of these sources validates
an autonomous agent replacing a QA engineer or doing a guaranteed percentage of
their work.

The resulting workflow starts with a decision, its risks and an independent
expected-result oracle. It chooses the least costly useful test layer, changes
the investigation as evidence arrives, and preserves what remains unknown.
Read this research when changing those contracts; normal ticket execution needs
only the relevant [testing strategy](../reference/testing-strategy.md).

## Inspected sources and implementation mapping

| Primary work and inspected scope | Practice and limit | Repository application |
|---|---|---|
| [ISTQB CTFL syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), sections 4.1–4.2.4 and 5.2.1–5.2.4 | Risk likelihood and impact inform depth and priority. Boundaries, condition combinations and state sequences need different techniques. The syllabus does not establish a universal test count or risk score. | [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): criterion/risk → technique → oracle → layer → evidence. |
| [Jonathan Bach, Session-Based Test Management](https://www.satisfice.us/articles/sbtm.pdf), original article, especially pages 1–4 and 9 | Exploratory sessions have a mission, reviewable notes and a debrief; discoveries can change the investigation. The original team's 90-minute sessions and time accounting are contextual. | [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): charter, tested paths, observations, questions and unfinished scope; no universal session duration. |
| [Cem Kaner and James Bach, The Nature of Exploratory Testing](https://www.kaner.com/pdfs/NatureOfExploratoryTest.pdf), slides 4–17 | Exploration combines learning, design and execution. Information objectives, observation and oracle problems matter. These slides were inspected; the authors' books were not. | [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): identify an independent oracle; distinguish a discrepancy, uncertainty and a confirmed defect. |
| [Martin Fowler, Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html), full article | Isolation, clocks, asynchronous waits, dependencies and resource leaks can create intermittent results. Quarantine needs active repair. This guidance concerns regression reliability, not a ban on variable exploratory or performance inputs. | [Test automation contract](../../.cursor/rules/test-automation.mdc): preserve first failures, investigate causes, synchronize on conditions, identify quarantine owner and review date. The one-rerun limit is this repository's budget choice. |
| [Ham Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), pipeline placement, terminology and avoiding duplication | Prefer fast focused checks while retaining broader checks for the additional evidence they provide. A pyramid is a heuristic, not mandatory test percentages. | [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md) and [test automation contract](../../.cursor/rules/test-automation.mdc): use the lowest effective layer and declare what mocks cannot establish. |
| [DORA, Test automation capability](https://dora.dev/capabilities/test-automation/), implementation, pitfalls, improvement and measurement | Developers and testers collaborate on reliable suites, incremental coverage and continued exploratory/usability work. This is a synthesis, not an independent inspection of its datasets or causal estimates. | [Team workflow](../reference/team-workflow.md) and [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): clear ownership, evidence and next action; do not optimize raw test counts or create a separate QA approval silo. |
| [Janet Gregory and Lisa Crispin, Why we now say holistic testing vs. agile testing](https://agiletestingfellow.com/blog/post/why-we-now-say-holistic-testing-vs-agile-testing), original post | Testing supports continuous feedback across the whole team and product lifecycle. Practitioner framing does not prove agent effectiveness; the linked book was not read. | [Testing strategy](../reference/testing-strategy.md): consider relevant security, accessibility, reliability and operational risks; select a justified slice instead of requiring every audit on every ticket. |
| [W3C WAI, Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/), initial checks, tools and reporting | Automated tools alone cannot establish accessibility conformance. Knowledgeable human evaluation remains necessary. The overview is not a complete WCAG audit procedure. | [Surface guidance](../reference/surfaces.md) and [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): distinguish scan findings from keyboard, focus and assistive-technology checks actually performed; retain pending coverage. |
| [OWASP WSTG v4.2, Testing for Insecure Direct Object References](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References/), objectives and procedure | Test object references with users who own different objects and, where relevant, have different privileges. One security category cannot establish overall application security. | [Test automation contract](../../.cursor/rules/test-automation.mdc): paired permitted fixtures; actor × owner × action checks and resulting data. The matrix notation is a framework adaptation. |
| [Rob Ewaschuk, Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/), SRE chapter 6: symptoms, signals and latency distributions | Successful HTTP status can accompany wrong content; averages hide tails; internal telemetry can reveal failures hidden by retries. These are monitoring principles, not authorization to mutate production. | [QA workflow](../../.cursor/skills/qa-workflow/SKILL.md): observe business completion and correlate evidence; [testing strategy](../reference/testing-strategy.md): report workload, errors and latency distribution. |
| [Alex Perry and Max Luebbe, Testing for Reliability](https://sre.google/sre-book/testing-reliability/), SRE chapter 17: configuration differences, regressions, stress and canary limits | Results depend on build/configuration and execution context; canaries can miss faults. Large-system examples do not mandate stress testing for every change. Only this chapter was inspected. | [Ticket state contract](../../.cursor/rules/ticket-state.mdc) and [QA router](../../.cursor/skills/qa/SKILL.md): preserve target/build/source/configuration identity and reassess evidence when resuming on a changed target. |
| [Brendan Gregg, The USE Method](https://www.brendangregg.com/usemethod.html), metrics, unknowns, interpretation and tool selection | Investigate resource utilization, saturation and errors; long averages can obscure issues. Missing measurements remain unknown. This method addresses resource bottlenecks, not every performance issue. | [Testing strategy](../reference/testing-strategy.md): start with the performance question and workload; require measurements for a bottleneck or improvement claim. No informal effectiveness percentages were adopted. |

## What the synthesis changes

The [explorer](../../.cursor/agents/code-explorer.md) locates relevant code; the
[reviewer](../../.cursor/agents/code-reviewer.md) turns source observations into
testable risks. Source inspection cannot substitute for execution or prevent
useful black-box testing when source is unavailable. The
[test runner](../../.cursor/agents/test-runner.md) preserves execution identity
and failures. The [ticket writer](../../.cursor/agents/ticket-writer.md) and
[tracker reporter](../../.cursor/agents/tracker-reporter.md) preserve scope,
evidence, uncertainty and next actions across handoffs.

These are framework design decisions. So are `Pass | Partial | Fail`, bounded
retries and compact artifact references. They make the evidence contract
explicit; they do not certify the product or resolve ambiguous requirements.
Automation is useful when an observable result answers a relevant question,
not merely when a new test exits successfully.

## Evaluation and remaining gaps

The [golden-task skill](../../.cursor/skills/golden-tasks/SKILL.md) separates
deterministic configuration tests from actual fresh-model behavior. Fixtures
cover such mistakes as accepting HTTP 202 as completed work, treating an empty
test run as Pass, erasing a failed first attempt and reusing stale build evidence.
The [recorded evaluation](../sessions/2026-09-24-golden-tasks.md) states which
scenarios were actually executed; the research itself is not an evaluation run.

Further useful fixtures include invalid state transitions, cross-tenant object
access, requirement/implementation disagreement, mean-versus-tail latency and
tests that stay green when the intended behavior is deliberately broken. These
are proposals, not completed coverage. Grade actions, artifacts and final claims
together; keyword matching does not establish sound QA judgment.

Two attempted sources were excluded from the substantive count: Gerard
Meszaros's author-hosted Humble Object page could not be retrieved, and the
Google Testing Blog flaky-test page became inaccessible behind a challenge.
No unavailable commercial books or private company material were treated as
inspected sources. Detailed device/BLE testing, property testing, mutation
testing and model-evaluation methodology need further primary-source research
before adding specialized prescriptive rules.
