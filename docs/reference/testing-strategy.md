# Risk-directed testing

Read for planning; do not load the research register on every ticket.
The rationale and inspected sources are in [research](../research/qa-practices.md).

Choose the information needed for a decision before choosing a tool. Record the
criteria, plausible failure impact and exposure, test technique, expected-result
oracle, execution layer and evidence. Use boundaries and partitions for ranges,
condition tables for interacting rules, and state/event sequences for lifecycles.
Uncertainty about the expected result is a requirement question, not a reason to
copy implementation behavior into a test.

Use the lowest layer that exposes the risk. Retain integration/journey checks
where they provide distinct evidence. State mocked boundaries; a provider double
cannot establish the real provider's behavior. Prioritize critical flows and
historical defects before expanding coverage. Do not prescribe test percentages.

Exploration needs a charter (question/risk), bounded session, observations,
questions and a short debrief. Let discoveries change the next investigation;
record what the original charter left untested. Automation complements this work.

Reliability: isolate data, control time/randomness when relevant, wait on observable
conditions, and retain the original failing run. Quarantine has a linked defect,
owner and review date. A green retry does not erase intermittent failure.

Use only applicable surface guidance in [surfaces](surfaces.md). A small functional
change does not require a full load, security and accessibility audit. Name the
slice selected and why. No number of checks establishes absence of defects.
