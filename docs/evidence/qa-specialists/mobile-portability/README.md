# Mobile replay portability repair — real Android execution

The original shipped reference rejected a fresh owned `emulator-5562` with exit 2
before contacting it ([original output](old-shipped.log)). It also resolved an
absent author-only contract path. The historical author’s real execution remains
valid; packaging it exposed these additional portability defects.

The repair validates the actual shipped mobile contract before device access,
then checks the caller’s `demo.py` ownership manifest, exact live serial/AVD, API,
installed fixture package and pinned APK. Ten additional offline tests cover
these guards; they are not device execution evidence.

Root prepared a fresh API34 ARM64 AVD `qa-mobile-91a2e521c48b`, deliberately using
serial `emulator-5562`. Two selected lifecycle tests constitute this bounded
portability regression: activity recreation and process termination/relaunch.
They are a documented diagnostic subset, not a rerun of the whole 12-case suite.

| Variant | Actual result | Evidence |
|---|---|---|
| Seeded APK | 2 failures, 0 errors/skips; persisted unit total becomes 0 instead of 5 | [summary](seeded-execution/summary.json), [console](seeded-console.log), [identity](seeded-execution/identity.json) |
| Corrected baseline | 2 passes, 0 failures/errors/skips | [summary](baseline-execution/summary.json), [console](baseline-console.log), [identity](baseline-execution/identity.json) |

Both executions use exactly the same test file SHA-256:
`c3b19bddc8b3232a00b76d81cdc6c9fba9a2c947f98a3a85c16c2061f5e2f206`.
[AST comparison](assertion-integrity.json) also verifies the Device actions,
ParcelContract business methods and generated boundary cases are unchanged from
`5dc46cf`. Only portable preflight/provenance and CLI inputs changed.

Per-case commands, hierarchy XML, lifecycle events, screenshots and app-only
cleanup checks are retained. Images are captured artifacts; this report does not
claim manual visual inspection. Host logs, signing keys and APK files are excluded.
The final run state and cleanup output record owned-emulator shutdown and device
state removal. Original 12-case input-protocol skips remain Partial; no iOS,
hardware, hybrid, radio or newly validated Android-version coverage is implied.
