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
