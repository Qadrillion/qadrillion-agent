# Specialist blind review

Base: `91e9bb0d4dcbfe812963fe6f04f4387c1b664497`.
The reviewer received only the complete diff and frozen acceptance spec, in a
fresh reviewer session. No implementer rationale or claimed test results were
supplied. The reviewer independently delegated a bounded harness inspection.

## Round 1 — BLOCKED

Snapshot: `677c95e`.
Code fingerprint: `26a55cf5373a97612f459b4e15c56671f2e4a469971daed4a813f85d26b37779`.
Full binary diff SHA-256: `474b19d89a80cd64d6a5a3f92ed693cf61655a31023248d93944651f915c0e45`.

| Scope | Severity | Finding | Disposition |
|---|---|---|---|
| IN-SCOPE | BLOCKER | Browser teardown at `tools/specialists/reference/web/tests/parcel.spec.js:36` performs diagnostics before cleanup. Closing the page leaves the owned order behind. | Fixed: independently attempt diagnostics, retain their failures, verify identity before mutations, attempt all owned deletions and baseline checks. Real Chromium closed-page injection fails on the original cleanup and passes its cleanup invariant after repair; the teardown error remains a test failure. |
| IN-SCOPE | SHOULD | `tools/specialists/measure.py:141` detects an existing output only after traffic, discarding samples. | Fixed: reserve output before identity parsing or HTTP. Real CLI regressions verify zero requests for existing/unusable paths, preserved original bytes, exit 2 and retained structured setup failures. |

The reviewer independently ran all 75 guard cases, 136 tooling tests, four mobile
ownership tests and six HTTP reference replays. All passed. The 261 then-shared
artifact hashes and nine usage events matched. These successful checks did not
prevent the two reproduced findings.

### Reviewer Not verified (verbatim)

- Checklist reviewed: A1 architecture ownership; A2 five execution procedures; A3 routing; A4 API/security detection; A5 browser execution/isolation; A6 bounded measurements; A7 mobile capabilities; A8 evidence/claims/usage; A9 adapters/offline/reference/native/CI; A10 adoption and completed review. A5 fails the reproduced cleanup case; A9/A10 still need final clean-clone, CI and PR evidence.
- Independently ran `python3 tools/verify.py`: **PASS**, including 75 hook cases, 136 tooling tests, four mobile ownership tests and adapter equality. All 261 shared artifact hashes matched; nine recorded usage events matched the reported totals.
- Historical mobile execution and native runtime discovery were not rerun. Retained records support their stated results, but do not establish fresh device/runtime behavior. Android literal-input skips, iOS/hybrid/hardware coverage and native deny enforcement remain unverified.
- Unreproduced historical inspection claims remain claims: “Sources inspected 2026-09-24”, “Inspected APIs”, “their installation was probed”, and “These are inspected sections/pages”. Reproducing them requires the relevant version probes and primary-source inspection.
- The retained original browser claims “First-failure diagnostics were inspected before continuing the matrix” and “extracted first-attempt trace evidence, inspected directly” remain unsupported; the later reports appropriately retain and correct them.
- The later statement “This evaluator independently viewed all three named images and corroborated their content” and handoff statements “Viewed with the image tool during this review” / “Viewed during this review” lack serialized reviewer action evidence. They cannot establish historical viewing from this diff.
- Findings refer to the frozen round-one diff; the parent’s subsequent cleanup repair was not reviewed here.

## Round 2 — PASS WITH SHOULDS

Snapshot: `b5e19e2`.
Code fingerprint: `2cacb0e980d76c40f33c1815fc9b3e3da46ae1c948cbfd43ac04507b55a58e7b`.
Full binary diff SHA-256: `5816330dc5814f65cfd9da735e52cb1e9a864fb8f3dfc11265d0f6f813e3a7f1`.

| Scope | Severity | Finding | Disposition |
|---|---|---|---|
| IN-SCOPE | SHOULD | `.cursor/skills/qa-mobile/references/appium.md:6` says execution selected Maestro, contradicting the retained ADB/UIAutomator execution. | Fixed the canonical reference to ADB/UIAutomator plus stdlib; Maestro is explicitly only probed. Regenerated both copies and the adapter manifest. |

### Reviewer Not verified (verbatim)

- Checklist reviewed: A1 ownership; A2 specialist procedures; A3 routing; A4 API/security; A5 browser isolation; A6 performance; A7 mobile; A8 evidence; A9 portability/runtime/CI; A10 adoption/handoff. This verdict concerns the frozen round-two diff; subsequent corrections are excluded.
- Independently passed `tools/verify.py`: 75 hook cases, 138 tooling tests, four mobile tests and adapter checks.
- All eight reference replays produced expected defective/corrected outcomes, including Chromium and Firefox. The closed-page fault injection retained diagnostic failures while removing owned orders. Evidence: `/tmp/qadrillion-review2-replay-20260924` and `/tmp/qadrillion-review2-cleanup-probe`.
- All 284 shared artifact hashes matched. Nine recorded completed-turn usage events matched reported totals. Historical Android and native-runtime execution were not rerun; iOS/hybrid/hardware coverage and native deny enforcement remain unverified.
- Final CI/PR status and independent clean-clone execution remain unverified. Retained clean-clone logs do not substitute for commands run during this review.
- Historical research claims remain unverified: “Inspected APIs:”, “Sources inspected 2026-09-24:”, “Inspected 2026-09-24.” and “These are inspected sections/pages”. Reproduction requires the primary-source inspection records.
- Unsupported historical browser claims remain: “First-failure diagnostics were inspected before continuing the matrix” and “extracted first-attempt trace evidence, inspected directly”. Later reports appropriately preserve and correct them.
- “This evaluator independently viewed all three named images and corroborated their content”, “Viewed with the image tool during this review” and “Viewed during this review” lack serialized reviewer-action evidence; historical viewing cannot be established from the diff.

## Round 3 — BLOCKED

Snapshot: `5dc46cf`.
Code fingerprint: `c26b735f4d74b728cbab05eca08a425c7a081db04c50be67d6b8ef48cc65d53a`.
Full binary diff SHA-256: `12c216a38da8ce78956a8f33bf94690dadc36147cc301a4e678e436ce19f987d`.

| Scope | Severity | Finding | Disposition |
|---|---|---|---|
| IN-SCOPE | BLOCKER | Shipped mobile replay resolves an absent author-only `CONTRACT.md` path before its tests. | Fixed: load/hash the shipped mobile contract before any ADB access. |
| IN-SCOPE | BLOCKER | Shipped mobile replay accepts only the historical emulator-5560, rejecting a fresh owned serial. | Fixed: caller-pinned owned manifest, live AVD/serial/API and installed APK checks. Fresh emulator-5562 replay detects both lifecycle defects, then passes 2/2 unchanged tests on correction; all owned device state removed. |

The build skill defaults to stopping after three review rounds. This task
explicitly requires fixing in-scope findings and forbids deferring missing generic
functionality to the work-laptop pilot. That task instruction takes precedence:
continue only the bounded mobile replay repair and its independent recheck;
retain the failed verdict and do not weaken the acceptance criteria.

### Reviewer Not verified (verbatim)

- Checklist: A1 ownership; A2 actionable recipes; A3 routing; A4 API/security; A5 browser; A6 performance; A7 mobile; A8 retained evidence; A9 portability/runtime/CI; A10 adoption and completed review. A2/A7/A9/A10 remain incomplete because of the findings.
- Independently passed `verify.py` and all eight defective/corrected HTTP/browser replay checks. Evidence: `/tmp/reviewer-round3-verify.log`, `/tmp/reviewer-round3-replay-installed/replay.json`.
- Nine routing conversations and recorded token totals were corroborated through delegated raw-evidence inspection.
- Native mobile replay was not executed independently. Fix the shipped replay, then execute against a fresh owned emulator. CI on the final revision remains unverified.
- Historical claims remain unreproduced: “Inspected APIs:”, “Sources inspected 2026-09-24:”, and “These are inspected sections/pages”. Reproduction requires the original inspection evidence.
- Retained browser claims “First-failure diagnostics were inspected before continuing the matrix” and “extracted first-attempt trace evidence, inspected directly” remain unsupported; later reports preserve and correct them.

## Final review — PASS

Initial fourth-review snapshot: `c9bdc32`.
Initial code fingerprint: `83ef0c7961555e84d0fcef13f46752d2ded0ca745bd9b4f75e7cc2a2aedb0681`.
Initial full binary diff SHA-256: `8ed58b276a5951e655ebecbc4f24c8c6f755f7747eb98eba5277bffd98579bc8`.

| Scope | Severity | Finding | Disposition |
|---|---|---|---|
| IN-SCOPE | SHOULD | Malformed measurement identity JSON (`[]`, `null`, numeric URL) escaped the setup-error handler, leaving reserved output empty. | Fixed: validate object/string shapes before access, including the live identity response. Actual CLI regression retains parseable blocked evidence with exit 2. Reviewer independently reproduced the correction. |

The reviewer inspected the supplemental complete diff and reran 23 specialist
tests before issuing PASS. Final reviewed code is committed as `b060801`.
Final code fingerprint: `16afb15b4a39970dedeaea8dd0bd79431e0e026aec6a3fb402cb6dc18c7147f7`.
Final full binary diff SHA-256: `fa8784e003d1401a5407e789a3248949b7307cc742dda3210f95cfea25013f4d`.
The final fingerprint/diff were captured before explicitly dispatching the
supplemental diff. No unresolved or deferred findings remain; six in-scope
findings were fixed across the retained review sequence.

### Reviewer Not verified (verbatim)

- Checklist reviewed: A1 ownership; A2 procedures; A3 routing; A4 API/security; A5 browser; A6 performance; A7 mobile; A8 evidence integrity; A9 portability/runtime/CI; A10 adoption/handoff.
- Independently passed offline verification, all eight defective/corrected HTTP/browser replay outcomes, and 23 specialist tests after the identity-schema repair. Malformed identities now retain blocked evidence and exit 2. Evidence: `/tmp/reviewer-round4-verify.log`, `/tmp/reviewer-round4-replay-installed/replay.json`, `/tmp/reviewer-round4-fixed-specialists.log`.
- All 373 shared artifact hashes matched. Nine recorded usage events reproduced reported totals and routing selections. Mobile artifacts match the current test hash; business/device methods remain unchanged. Native mobile execution was not independently rerun.
- Final CI, final clean-clone execution and PR completion remain unchecked. iOS, hybrid, physical hardware and native denial enforcement remain outside executed coverage.
- Historical claims remain unreproduced: “Inspected APIs:”, “Sources inspected 2026-09-24:”, “Inspected 2026-09-24.”, “These are inspected sections/pages”, “their installation was probed”, and “This evaluator independently viewed all three named images and corroborated their content”. Verification requires the corresponding inspection/probe/view records.
- Retained browser claims “First-failure diagnostics were inspected before continuing the matrix” and “extracted first-attempt trace evidence, inspected directly” remain unsupported. Later reports preserve and correct them.
