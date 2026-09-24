# Repository presentation and website handoff

Status: authorized by the user's repository-presentation brief, 2026-09-24.
Base: `d593f73a14606753ff5cbf937767d33f9a0b8a52` (merged specialty PR #4).
Branch: `docs/repository-presentation`.

## Decisions

Improve first-time understanding and the path to trying/contributing to the
project. Stars are an aspiration, not a promised outcome. Preserve Qadrillion's
existing mark and warm accent. Use GitHub-native typography and Markdown rather
than a new visual identity, giant banner or bespoke website inside the README.
The user delegated reference selection and presentation decisions; no product or
brand decision requires a new interview. The design direction below resolves the
build/design skill's direction step within that authorization.

Audit all six READMEs. Update the root and two runnable-reference guides where
needed; preserve historical evaluation READMEs and their artifact hashes. Publish
a reviewed PR, leaving merge to the user. The website deliverable is a standalone
implementation prompt based on the live page; no website edits or deployment.

Inventory correction, 2026-09-24: the initial search omitted hidden
`.cursor/README.md`. The tracked-file inventory has six READMEs; that guide is
current and remains unchanged. P4 always requires all READMEs to be assessed;
the acceptance criteria are unchanged.

## Direction contract

Mode: Read, with a clear path to trying the project.

- THESIS: A QA workflow your coding agent can execute, with inspectable evidence.
- OWN-WORLD: Restrained GitHub light/dark surfaces, existing Qadrillion mark and
  orange accent; sparse live badges, readable tables and short command examples.
- TYPE: GitHub's native heading, prose and monospace fonts, ensuring Markdown
  portability and reader-selected themes without custom font dependencies.
- STORY: Understand the outcome, recognize your task, try it, inspect proof,
  adapt it privately, contribute.
- FIRST VIEWPORT: Compact mark/title, one-sentence promise, CI/license badges and
  section links; a concrete QA request follows immediately.
- NOT-DONE: A decorative banner that hides the first useful action, fabricated
  terminal output, a badge wall or unsupported adoption/performance claims.

## Design inputs

Inspected 2026-09-24:

| Reference | Take | Do not take |
|---|---|---|
| [uv README](https://github.com/astral-sh/uv/blob/main/README.md) | Direct positioning and prominent runnable usage | Its performance multipliers or benchmark styling without comparable evidence |
| [Playwright README](https://github.com/microsoft/playwright/blob/main/README.md) | Concrete testing examples and capability navigation | Its product/API scope or any implication this repo supplies a browser driver |
| [FastAPI README](https://github.com/fastapi/fastapi/blob/master/README.md) | Recognizable project identity and accessible getting-started path | Sponsor/testimonial walls or third-party adoption claims |

Hero object: existing `docs/brand/mark.svg`; current large `header.png` is removed
from the README layout, retained as a historical asset. Copy is authored from the
repository's actual skills, configuration and evaluation evidence before render.
Design variance: 2/10 (native GitHub conventions); motion: 0/10; density: 5/10
(short useful sections and progressive links). Website identity stays with the
existing site; the handoff supplies corrected content and a clear page hierarchy.

## Acceptance criteria (frozen before implementation)

| ID | Observable result | Failure guarded against | Verification |
|---|---|---|---|
| P1 | Root README immediately explains the framework, audience and agent/tool relationship, with a compact branded introduction and useful navigation. | Attractive but vague marketing or a giant banner hiding the entry point. | Inspect rendered desktop light/dark and narrow mobile views. |
| P2 | Five specialties, selective routing, example prompts, setup/adaptation and contributions are easy to find. Claims distinguish procedures from exercised stacks. | Stale three-skill positioning, tool lock-in or invented guarantees. | Content review against canonical skills, support matrix and actual scripts. |
| P3 | Setup and account-free replay commands are runnable; links/images/anchors resolve; subordinate runnable READMEs have clear prerequisites, outcomes and cleanup. | Broken first-use flow or a misleading successful replay of defective behavior. | Required verification, execute documented local commands and inspect results; check Markdown links and rendered assets. |
| P4 | All READMEs are assessed; retained historical evaluation evidence stays unchanged. | Documentation drift or rewriting failures for marketing. | Inventory/disposition and git diff inspection. |
| P5 | A copyable website implementation prompt identifies actual stale page claims, supplies current copy/structure/links, preserves brand, and asks for implementation plus verification in the website repo. | Generic redesign advice, false capabilities or accidental website changes here. | Compare to inspected public page and repository; independent review. |
| P6 | Required verification and independent review pass; changes are committed in a PR, with updated state/session and honest limits. | Unreviewed presentation or unverified popularity/runtime claims. | Build verification, blind diff review, PR/CI check. |

## Out of scope and verification limits

No new framework behavior, fresh specialty certification, company connections,
GitHub account campaigns, bought stars, website implementation or deployment.
No claim that README changes produce stars or conversion uplift. GitHub controls
its page shell, fonts and CSS; local GitHub-style renders verify this Markdown's
layout, not GitHub field Core Web Vitals or full site accessibility conformance.
Mobile hardware/iOS/Appium and runtime activation limits stay as documented.

## Implementation record — 2026-09-24

Branch: `docs/repository-presentation` · Acceptance checkpoint: `34f817a`; implementation/completion commit follows.
Review-base: `d593f73a14606753ff5cbf937767d33f9a0b8a52`.
Review-fingerprint: `b896e4ca0adce61ca7fe75967ad9a90712c939d57af80fae4da6a442b5db4724`.
Full-diff-sha256: `345362be0fc5117a3a2820186c0bbbc5e26f607979967b9ef7ebc1c6bc651171`.
Verified: `python3 tools/verify.py` → PASS (153 Python tests, 75 guard cases); doctor and adapter drift checks → PASS; documented HTTP/browser setup/replays → six/eight expected outcomes with unchanged tests and completed cleanup; 44 links/anchors and six responsive renders → PASS.
Review: one independent review, PASS after two supplemental documentation corrections.
Deferred: 0 items. Two in-scope findings fixed, zero unresolved.
Not verified: “Hosted GitHub layout, screen-reader behavior, fresh-machine setup and website implementation require separate execution. Local layout checks used the prepared GitHub-style HTML previews.” Full reviewer coverage and historical limits are retained verbatim in the [review record](../reviews/2026-09-24-repository-presentation.md).

The [verification record](../evidence/repository-presentation/verification.md)
accounts for all six READMEs, commands, rendering, prior evidence preservation
and the live-page inspection. The final reviewed content precedes these completion
records; no framework behavior changes. The owned preview server and all replay
services were stopped. Website implementation is intentionally handed to another
chat through the [copyable prompt](../prompts/update-repo-landing-page.md).

Publication: open the branch's PR after this record is committed, confirm its
hosted checks, and leave merge to the user. The final user handoff links the PR
and its current checks; publication is not part of the blind review's execution.
