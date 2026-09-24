# Repository presentation and website prompt

Owner: framework maintainer. Branch: `docs/repository-presentation`.
Base: `d593f73a14606753ff5cbf937767d33f9a0b8a52` (merged specialty PR #4).
Started from clean current main; existing branches/work preserved.

The frozen presentation spec preceded edits. Inspected uv, Playwright and FastAPI
READMEs for structure, retained the existing Qadrillion mark, and rewrote the
root README around a concrete task, five specialist entry points, runnable demos,
reference evidence, private adoption and contributions. Improved the two
runnable-reference guides. All six tracked READMEs are accounted for; canonical
configuration and historical evidence guides are unchanged.

An isolated read-only website audit inspected current public HTML and desktop/
mobile renders of qadrillion.com/repo. The website implementation prompt supplies
replacement content, current capability limits, actual stale-claim corrections,
metadata and verification criteria for a separate website chat. No website source
or deployment changed. No popularity guarantees or company account access.

Verification: 153 Python tests, 75 guard payloads and local doctor pass; documented
HTTP and browser setup/replays produce six/eight expected defective/corrected
outcomes with unchanged test hashes and cleanup. Forty-four local links/anchors
resolve. GitHub API-rendered Markdown was checked with versioned preview CSS,
light/dark desktop and 320px/390px mobile layouts. This does not certify GitHub's
hosted shell, field performance or full accessibility conformance.

Independent review caught the omitted hidden `.cursor/README.md` in the inventory
and a sentence that grouped precautionary 99% autonomy/token-savings exclusions
with observed website claims. Both are corrected; acceptance criteria unchanged.
Final review, commit and PR status follow in the spec implementation record.

Independent review returned PASS on supplemental content snapshot 3, with no
unresolved findings or deferrals. The reviewer independently reran offline checks,
HTTP and Chromium/Firefox replays, links and responsive rendering. Final content
fingerprint: `b896e4ca0adce61ca7fe75967ad9a90712c939d57af80fae4da6a442b5db4724`;
full binary-diff SHA-256: `345362be0fc5117a3a2820186c0bbbc5e26f607979967b9ef7ebc1c6bc651171`.
Completion records follow the reviewed snapshot. All owned services, including
the README preview server, are stopped; temporary outputs remain inspectable.
Publish the reviewed branch, verify hosted CI and leave merge to the user.

Published PR #5 at `7cfa20e`; all four jobs in run 35990168203 passed. The stop
reminder did not recognize Markdown-wrapped record fields or the free-form PASS
sentence. Inspected its parser, confirmed the current fingerprint still matches
the reviewed content, and normalized only the record format to plain fields and
`Review: round 1 PASS`. The reminder then returned an empty result. No new product,
README or website-prompt change was made after review. Merge remains with the user.
