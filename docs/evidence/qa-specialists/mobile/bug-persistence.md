# Android | Unit total resets to zero after activity recreation or process relaunch

Build: SHA256 `1261bed953d12ad7db8cd5ae2c183d26af142dd43a60e5b9d24bc16a9bdf834a`, package `com.qadrillion.parcel`, version 1.0 (1). Target: task-owned `emulator-5560`, Android14 API34 ARM64, en_US, portrait. Date: 2026-09-24. Local draft only; no tracker or external publication.

1. Clear only this disposable app's data and launch it.
2. Enter 2, submit; enter 3, submit. Observe `Parcels: 2` and `Units: 5`.
3. Force-stop `com.qadrillion.parcel` and verify its PID is absent.
4. Relaunch the same installed package without a reset.

Expected: `Parcels: 2` and `Units: 5`, per CONTRACT.md criterion 5.

Actual: `Parcels: 2` and `Units: 0`. Both input actions showed `Parcel added` and cleared the field before termination. The assertion's bounded wait retained five consecutive snapshots with zero units; the final screenshot agrees. This is visible data loss. Source was unavailable by task constraint, so no implementation cause is asserted.

Evidence: `first-run/test_process_termination_relaunch/009-accepted-3.xml`, `010-after-process-relaunch.xml` through `014-after-process-relaunch.xml`, `final-screen.png`, `commands.jsonl`, scoped logs and activity dump in the same directory. One original execution; no product rerun is needed for this deterministic retained observation. Background/foreground in the same activity passed on this build.

In-process recreation independently confirms the same loss: after the same 2+3 seed, launch the standard root activity with `am start -W -n com.qadrillion.parcel/.MainActivity --activity-clear-top`. PID remains unchanged, activity identity changes, and native events prove old destruction/new creation. Expected 2/5, actual 2/0. The first attempt stopped at a lifecycle-log timing assertion; after repairing that bounded wait, the single diagnostic rerun failed the unchanged totals assertion. Both attempts are retained. See `diagnostic-plan.md` and `diagnostic-recreation/test_activity_recreation/`, including `recreation-events.txt`, `010-after-recreation.xml` onward and `final-screen.png`.
