# Repository presentation verification

Date: 2026-09-24. Scope: README presentation and a future website implementation
prompt. No framework behavior or live website changed.

## README inventory

| README | Disposition |
|---|---|
| Root `README.md` | Rebuilt introduction, task example, specialty navigation, quick start, executable demo, evidence, configuration and contribution path. Existing mark replaces the oversized banner in the layout. |
| `.cursor/README.md` | Inspected after independent review caught its omission from the initial non-hidden search. Current canonical-source, adapter and verification guidance remains unchanged. |
| `tools/specialists/reference/README.md` | Added prerequisites/expected outcomes, runnable browser subshell, result interpretation and artifact navigation. |
| `tools/specialists/mobile/README.md` | Added goal, prerequisite/setup/author/replay/cleanup sections and navigation; preserved identity controls and input skips. |
| `docs/evidence/qa-specialists/README.md` | Inspected; kept unchanged as a historical evaluation record. |
| `docs/evidence/qa-specialists/mobile-portability/README.md` | Inspected; kept unchanged with the historical artifacts and manifest. |

## Commands and outcomes

| Check | Result |
|---|---|
| `python3 tools/verify.py` | PASS: 139 tooling + 14 mobile helper tests, 75 guard payloads; generated adapters current. [Log](verify.log). |
| `python3 tools/workspace/doctor.py` | PASS for local prerequisites/configuration. No runner configured; native registration/authentication/target access remain separate checks. [Log](doctor.log). |
| Documented HTTP replay, fresh output directory | Six expected defective/corrected outcomes, unchanged tests, all services closed. [Records](http-replay.json). |
| Documented browser installation subshell | `npm ci` and Chromium/Firefox installation succeed; caller stays at workspace root. No dependency files changed. |
| Documented browser replay, fresh output directory | Eight expected defective/corrected outcomes including Chromium/Firefox, unchanged tests, all services closed. [Records](browser-replay.json), [output](browser-replay.log). |
| Local Markdown/image links and anchors | 44 resolve, zero missing. [Results](link-results.json). |
| Three README renders | GitHub Markdown API, `mode=markdown`, styled with `github-markdown-css` 5.9.0. All render; live badges and local brand image load. |
| Browser layout | Root at 1100px light/dark, 390px light, 320px dark; both subordinate guides at 390px. No page-width overflow; code blocks may scroll internally. [Results](render-results.json). |
| Local navigation | Quick-start link lands at its heading; keyboard focus visible; prose is 16px; a 200% CSS-zoom probe retains viewport width. [Results](interaction-results.json). |
| `git diff --check` | PASS. |

The rendering harness first failed because the optional local Playwright package
was absent. Installed the documented pinned browser dependencies, then rendered
successfully. This was a preview prerequisite failure, not a product test pass.

## Visual verification

The maintainer viewed desktop light/dark and 390px/320px first viewports, then the
complete desktop dark render. The introduction is compact; navigation labels
remain together, the task example follows the introduction, and the table/command
hierarchy stays readable. These are local GitHub-style previews, not screenshots
of the hosted GitHub page shell. The preview adds heading IDs for local navigation
and embeds the existing mark; repository Markdown controls the actual content.

[Desktop dark preview](root-1100-dark-top.png) ·
[Mobile light preview](root-390-light-top.png)

Frontend/design gate adapted to repository Markdown:

- Deterministic pre-pass: `npx impeccable@latest detect --json README.md tools/specialists/reference/README.md tools/specialists/mobile/README.md` returned **`[]`** (verbatim). Markdown findings alone do not establish DOM or accessibility coverage.
- Performance: SKIP field Core Web Vitals and GitHub shell payloads, which this repo does not control. No new runtime JavaScript, fonts or animation.
- Accessibility: PASS scoped local checks for image alt text, native links, visible keyboard focus and narrow/zoom reflow. Full WCAG conformance, screen readers and hosted GitHub behavior not checked.
- Typography: PASS GitHub-native prose/headings/code; measured body 16px. GitHub controls final theme/font sizes, including badges and code.
- Visual system: PASS existing mark, native GitHub surfaces and restrained badges; no new theme or invented product screenshot.
- Motion: PASS for repository content, which adds none.
- Design preflight: PASS for the frozen README direction; no fabricated adoption metrics, testimonials, autonomy or performance promises.

Disposition: independent review PASS after the inventory/website-wording fixes;
see the [review record](../../reviews/2026-09-24-repository-presentation.md).
This is not a website deployment or a claim of improved star/conversion metrics.

## Website audit and handoff

Inspected public [qadrillion.com/repo](https://qadrillion.com/repo) via HTTP200 HTML
and isolated Chromium at 1440×1000 and 390×844. The landing-page auditor inspected
full-page renders; the maintainer also viewed both first viewports. Existing brand
identity is retained in the handoff. The live page had stale skill/role/hook names,
Cursor/Claude-only positioning, five-run and mandatory-sign-off claims, absolute
hook-enforcement claims and unsupported Appium usage claims.

The [implementation prompt](../../prompts/update-repo-landing-page.md) provides
current content, source links, exact corrections, metadata, scope and acceptance
checks for the separate website checkout. A second read-only pass by the auditor
found no material factual or implementation gap. No website source or deployment
was changed in this task.

## Design sources

The frozen [direction/spec](../../specs/2026-09-24-repository-presentation.md)
records the inspected uv, Playwright and FastAPI READMEs and what was borrowed
from each structurally. No artwork, marketing claims or testimonials were copied.
The [GitHub Markdown endpoint documentation](https://docs.github.com/en/rest/markdown/markdown)
was inspected to select README-style rendering rather than comment-style GFM.
