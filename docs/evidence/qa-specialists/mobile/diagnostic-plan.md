# Single diagnostic rerun

First run finished normally (exit1) during the user's usage interruption; its complete output, 12 cases and source snapshot remain in `first-run/`. No incomplete command is retried.

Hypothesis: `am start -W --activity-clear-top` reports the replacement activity's readiness before the old activity's asynchronous onDestroy event. The first run read events immediately and failed that diagnostic despite final events showing destruction 684 ms later. A bounded condition wait for the same unchanged lifecycle evidence will distinguish the harness race from the underlying totals assertion. Only `test_activity_recreation` is rerun.

Repair: wait up to 10 seconds for the existing destruction and two-creation event conditions, retaining the final scoped event log. The original seed, action, PID/activity checks and exact `Parcels: 2` / `Units: 5` business assertions are unchanged. Also repair the independently reviewed summary edge case where failure plus cleanup error could subtract one test twice, and capture actual Android configuration when the optional locale property is empty. These reporting changes do not alter product assertions.

Original source SHA256: `88b5955d2e002a254c21c6a310809aa6c5fef84d592e09d7a21998a0da6751c6`, archived as `first-run/test_parcel.py`.

Command from `/tmp/qadrillion-mobile-author`:

```sh
python3 automation/mobile/test_parcel.py --serial emulator-5560 --expected-apk-sha256 1261bed953d12ad7db8cd5ae2c183d26af142dd43a60e5b9d24bc16a9bdf834a --evidence artifacts/LOCAL-1/diagnostic-recreation --test test_activity_recreation
```
