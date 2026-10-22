# Native Android and iOS adaptation

Prefer the repository's existing harness for in-app state and synchronization;
retain cross-app/system tests where an instrumentation test cannot establish the
criterion. These recipes are conditional, not executed claims for this workspace.

## Android: Espresso, Compose and UI Automator

Inspect wrapper/plugin/dependency versions, the Android test source set,
instrumentation runner, build variant and `./gradlew tasks --all`. Use the actual
task (commonly `:app:connectedDebugAndroidTest`) and select the task-owned serial
through the project's runner/`ANDROID_SERIAL`. Capture Gradle output plus XML
results and any device logs. An APK build success is not an instrumented test run.

Use observed `R.id` with Espresso `onView(withId(...))`, actions, and
`check(matches(withText(...)))`. Compose tests use the observed semantics tree;
merged semantics can differ from the source composable tree. Prefer native
semantics matchers to forcing every UI into the same driver abstraction.

Espresso waits for its known idle resources; background jobs need registered
idling resources when they are relevant to completion. Register before the first
dependent action and release resources in teardown. Condition readiness and the
business assertion remain distinct. `ActivityScenario.recreate()` exercises
activity recreation, not whole-process death. Use an external driver/ADB process
termination and relaunch to test persisted state without resetting app data.
UI Automator is useful for system UI and cross-app transitions; treat granted
permissions, OS text and active window as explicit state.

Sources: [Espresso matching/assertions](https://developer.android.com/training/testing/espresso/basics),
[idling resources](https://developer.android.com/training/testing/espresso/idling-resource),
[ActivityScenario](https://developer.android.com/reference/androidx/test/core/app/ActivityScenario).

## iOS: XCTest/XCUITest

Probe `xcode-select -p`, `xcodebuild -version`, `xcrun simctl list runtimes` and
`xcrun simctl list devices available`. Read `xcodebuild -list` for the actual
workspace/project scheme, test plan and destination. Use a disposable simulator
UDID rather than `booted` on a shared machine. Set `DEVELOPER_DIR` for a single
command when selecting a known Xcode installation; do not alter global selection.

With the actual paths/scheme/UDID, the command pattern is:

```sh
xcodebuild test -workspace "$WORKSPACE" -scheme "$SCHEME" \
  -destination "platform=iOS Simulator,id=$UDID" \
  -resultBundlePath "$EVIDENCE/Run.xcresult"
```

In the existing UI test target, launch `XCUIApplication()`, query observed
accessibility identifiers, assert `waitForExistence(timeout:)` before interacting,
and assert the resulting text/value/state. Check `isHittable` when visibility or
occlusion matters; existence alone is insufficient. `terminate()` followed by
`launch()` tests relaunch; `activate()` supports bringing the application forward.
Configure launch arguments only for reset hooks actually implemented by the app.
Deleting/reinstalling an app does not promise keychain reset. Capture failure
attachments and the `.xcresult` bundle; record any unavailable crash/device logs.

On physical devices verify developer mode/trust, signing, provisioning and
entitlements using the team's existing setup. Do not substitute simulator
coverage for push delivery, camera hardware, biometric hardware or radio behavior.
If Xcode/runtime/device access is absent, preserve that exact blocker and do
source/test-authoring work honestly without claiming a native run.

Sources inspected 2026-09-24: [XCUIApplication lifecycle](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication),
[existence waits](https://developer.apple.com/documentation/xcuiautomation/xcuielement/waitforexistence(timeout:)),
[test results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results),
[CLI destination syntax](https://developer.apple.com/library/archive/technotes/tn2339/_index.html).
