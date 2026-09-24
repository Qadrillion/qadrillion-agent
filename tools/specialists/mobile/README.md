# Disposable native Android reference

The [contract](contract.md) is the test author's oracle. This target is an actual
native Android Activity, built using installed SDK tools with no Gradle, network
dependency resolution, account or backend. It is an evaluation fixture, not the
recommended build system for a product. Python 3, a JDK, AAPT2, D8, zipalign,
apksigner, ADB, emulator, avdmanager, platform SDK and compatible system image
must already be available. `prepare` reports exact missing paths.

On the inspected Apple Silicon machine, SDK API 34/build-tools 34.0.0 and the
`system-images;android-34;google_apis;arm64-v8a` image are installed. Defaults use
those versions and Android Studio's bundled JDK. Other hosts pass `--sdk`,
`--java-home`, `--api`, `--build-tools` and `--image` at prepare time. Choose an
image matching the host architecture. No package is installed automatically.

Use a previously nonexistent run path. The following commands build both fixture
variants, start a fresh dedicated AVD, and install one APK:

```sh
python3 tools/specialists/mobile/demo.py prepare --run-dir /tmp/qa-mobile-RUN
python3 tools/specialists/mobile/demo.py start --run-dir /tmp/qa-mobile-RUN
python3 tools/specialists/mobile/demo.py install --run-dir /tmp/qa-mobile-RUN --variant seeded
python3 tools/specialists/mobile/demo.py status --run-dir /tmp/qa-mobile-RUN
```

`run.json` records app hashes, source hashes, image, unique AVD name, explicit
serial, process and observed OS fingerprint. API/build-tools and Java paths are
local runtime inputs; do not commit personal paths or signing keys as evaluation
evidence. The generated key signs only these synthetic fixtures and expires in
seven days. APK byte hashes differ between preparations because keys differ.
Build inputs and retained commands make the steps reproducible.

The supervisor supplies the author the contract, skill, selected APK hash,
owned serial and run directory; keep the mutation's implementation out of the authoring context.
The author inspects runtime locators and writes the tests. Preserve the first
failed result, then install `--variant baseline` and run the **unchanged** tests
with their declared independent setup. `install -r` retains app data; tests must
state when data is cleared and avoid clearing it within persistence checks.
Do not mistake YAML parsing or APK installation for feature verification.

Store stdout/stderr, test hashes, exit statuses, JUnit, screenshots, hierarchy and
scoped logs under `evidence/` or another explicitly supplied artifact path. Device
execution remains not run until a real runner executes assertions. Use the
installed Maestro version's options; see the mobile skill's conditional recipe.

The completed reference evaluation used independently authored Python tests
driving ADB/UIAutomator observations. Replay that suite with explicit device and
APK identity; supply the serial and installed APK hash from this run's `run.json`:

```sh
python3 tools/specialists/reference/mobile/tests/test_parcel.py --run-dir /tmp/qa-mobile-RUN --adb /path/to/sdk/platform-tools/adb --serial emulator-SERIAL --expected-apk-sha256 APK_HASH --evidence /tmp/qa-mobile-RUN/evidence/attempt-1
```

The run directory must be the original owned fixture directory created by
`demo.py`, with its current `run.json` and built APKs retained. Before contacting
ADB, replay reads and hashes the shipped `contract.md`, validates run ownership,
and checks the requested serial and APK hash against the installed manifest
variant and local build. Before any app reset, launch or input, it verifies the
live emulator serial, AVD name, fixture package, installed APK hash and recorded
Android API. Missing or mismatched identity stops the replay. The resulting
`identity.json` records the manifest, contract and test hashes with the observed
device identity. Physical devices are outside this fixture replay's scope.

This suite clears only the selected fixture app between independent cases. Its
in-test persistence transitions retain data. Literal decimal/text input cases
remain skipped if the OS input path filters those characters; skips produce a
nonzero exit and must not be called full coverage. The shipped copy replaces
the author's machine-specific default ADB path with `adb`; detecting assertions
are unchanged. Android is optional and is not executed by the standard CI job.

When finished:

```sh
python3 tools/specialists/mobile/demo.py cleanup --run-dir /tmp/qa-mobile-RUN
```

Cleanup checks the live AVD name before shutting down the recorded serial and
removes only this run's AVD/preferences directories. It retains build/log/evidence
files. It refuses to kill a different device or remove data while the recorded
process remains. Reconcile a failed cleanup explicitly; do not issue global ADB
kill commands, wipe existing AVDs or delete user device data. A failed start is
retained as one attempt; prepare a new run only after diagnosing it and cleaning
its owned state. Android emulator results do not establish physical or iOS
coverage.
