# Mobile specialist research and capability probe

Inspected 2026-09-24. This extends the evidence principles in
[QA practices](qa-practices.md) and [runtime portability](runtime-portability.md).
Commands below are probes, not a claim that feature tests executed.

| Local probe | Observed result | Consequence |
|---|---|---|
| `uname -m`; `sw_vers` | arm64; macOS 26.6.2 | Use an arm64 Android system image. |
| `adb version`; `adb devices -l` | ADB 36.0.0; no attached devices | No existing device was selected. The probe started ADB's local daemon. |
| `emulator -version`; `emulator -accel-check` | 36.2.12.0; Hypervisor.Framework check 0 | An isolated Android emulator is feasible. |
| Installed SDK metadata | Platforms 33/34/36; build-tools 34.0.0/35.0.0/36.1.0; Android 34 Google APIs arm64 image rev8 | Select API34 for the reference run; do not download a new SDK. |
| Default Java/Maestro invocation | Java runtime not found | A discoverability issue, not an absent compiler. |
| Bundled JDK `java -version`, `javac -version`; command-local `JAVA_HOME` Maestro probe | JDK/javac 21.0.8; Maestro 1.36.0 | Reuse Android Studio's JDK without changing global configuration. |
| `appium --version`; `appium driver list --installed` | 2.5.4; UiAutomator2 2.42.0 | Alternative installed; not selected for the reference feature run. |
| SDK build tools | AAPT2 2.19-10229193; D8 8.2.2-dev; apksigner 0.9 | Tiny native fixture can be built without dependency downloads. |
| `xcode-select -p`; `xcodebuild -version`; `xcrun simctl list runtimes` | Command Line Tools selected; full Xcode absent; simctl unavailable | iOS execution not run. Requires full Xcode plus a compatible iOS Simulator runtime or provisioned device. |

Two existing personal AVDs were enumerated but were not booted, reset or reused.
No account, paid service, existing app data, personal key or global configuration
was used. `qa-config.json` contained no configured mobile runner; the observed
machine capability does not change that inventory into a portable prerequisite.

## Choices and source mapping

The reference uses a fresh task-owned AVD plus a native Java Activity. The
capability probe proposed Maestro; the independent author selected stdlib tests
driving serial-pinned ADB and observed UIAutomator XML, including actual process
and activity lifecycle evidence. Maestro remained a CLI capability probe.
Appium provides richer WebView/context control but
adds a driver/client/server stack unnecessary for this native slice. Native
Espresso/XCUITest remains preferable when a product already has those harnesses.
None of these choices makes a runner mandatory for adopters.

- [Android AVD management](https://developer.android.com/tools/avdmanager) and
  [environment variables](https://developer.android.com/tools/variables) establish
  explicit image/device creation and per-run AVD/preferences locations. Current
  docs deprecate avdmanager in favor of the new Android CLI; the inspected
  installed avdmanager syntax is retained for this pinned reference. Its probe
  warned that newer SDK XML metadata exceeds its schema version. Keep the warning
  and assess the actual create/boot result; do not claim a clean probe.
- [Emulator CLI](https://developer.android.com/studio/run/emulator-commandline)
  distinguishes device userdata and images. Isolate userdata instead of wiping
  an existing personal AVD. Headless emulation still executes the Android OS.
- [AAPT2](https://developer.android.com/tools/aapt2),
  [D8](https://developer.android.com/tools/d8) and
  [apksigner](https://developer.android.com/tools/apksigner) define the build
  chain. AAPT2 resource output alone is unsigned and lacks DEX; build and signing
  must complete before installation.
- [ADB](https://developer.android.com/tools/adb) supports explicit serials,
  install, process lifecycle and screenshots. Record the live AVD name before a
  mutation and retain OS/app fingerprints rather than relying on a port alone.
- Maestro [selectors](https://docs.maestro.dev/reference/selectors/core-selectors),
  [launch state](https://docs.maestro.dev/reference/commands-available/launchapp),
  [condition waits](https://docs.maestro.dev/reference/commands-available/extendedwaituntil)
  and [artifact documentation](https://docs.maestro.dev/maestro-flows/workspace-management/test-reports-and-artifacts)
  informed observed IDs, explicit resets, lifecycle cases and bounded waits.
  The installed 1.36.0 CLI exposes `--debug-output` and JUnit `--output`; newer
  `--test-output-dir`/artifact manifest behavior was not assumed. Its
  [pinned source](https://github.com/mobile-dev-inc/maestro/blob/cli-1.36.0/maestro-cli/src/main/java/maestro/cli/command/TestCommand.kt)
  confirms the older output flags.
- Official Appium, Android native-testing and Apple test APIs are linked beside
  their conditional recipes. They inform adaptation procedures, not claims of
  local Appium, Espresso or iOS execution.

## Validation boundary

Source/build/lifecycle checks belong to helper verification. Independently
authored mobile tests, detecting assertions, initial failures, corrected-build
results and cleanup evidence belong to the specialist evaluation record. Do not
derive their verdict from this research or from a successful APK build. Physical
devices, hybrid contexts, iOS, BLE, camera, push and production-like networking
remain unexecuted unless the evaluation explicitly supplies that evidence.
