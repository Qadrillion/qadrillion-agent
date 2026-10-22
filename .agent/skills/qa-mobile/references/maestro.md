# Maestro local recipe

Use when the project already uses Maestro or a local accessibility-driven smoke
slice is appropriate. Probe `maestro --version` and command usage first. The
reference machine has **1.36.0**, which accepts `--debug-output`, `--format JUNIT`
and `--output`; current documentation also shows newer flags absent here.
No cloud account is required for `maestro test` against a local emulator.

Set command-local `JAVA_HOME` to an installed compatible JDK when Java discovery
fails. On the reference Mac, Android Studio's `Contents/jbr/Contents/Home`
provides JDK 21. Avoid changing shell profiles or globally installing a second JDK
when an existing one works. Install the verified app build on an explicitly
selected disposable device before running Maestro.

Author a Flow with the actual package as `appId`. Start independent cases with
`launchApp: { clearState: true }` only when reset is the intended setup. Use
`tapOn` and `assertVisible` with inspected text or IDs; both are regex selectors,
so escape literal regex characters. For a persistence check use `stopApp` then
`launchApp` without `clearState`; do not conflate that with background/resume.
Use a separate Home/activate case for background behavior.

`assertVisible` waits for the condition. Use `extendedWaitUntil` with a justified
timeout for longer operations, then assert the completed business result. Do not
use the YAML `retry` command to erase failed attempts. Default permission grants
can mask denial behavior; set permissions deliberately when supported by the
installed version and inspect actual OS state.

For the inspected 1.36.0 CLI, with a real `flow.yaml`, unique `evidence` directory,
and `SERIAL` taken from the owned device manifest:

```sh
maestro --udid "$SERIAL" test --format JUNIT --output "$EVIDENCE/junit.xml" \
  --debug-output "$EVIDENCE/debug" flow.yaml
adb -s "$SERIAL" exec-out screencap -p > "$EVIDENCE/screen.png"
adb -s "$SERIAL" shell uiautomator dump /sdcard/qa-hierarchy.xml
adb -s "$SERIAL" pull /sdcard/qa-hierarchy.xml "$EVIDENCE/hierarchy.xml"
adb -s "$SERIAL" shell rm /sdcard/qa-hierarchy.xml
```

Use that fixed temporary hierarchy filename only on the dedicated disposable
device; on shared hardware choose a unique task filename. Add `takeScreenshot`
at meaningful checkpoints. Verify where this installed version writes it: newer
artifact bundle layouts and `--test-output-dir` are not a 1.36.0 contract. Preserve
stdout/stderr, exit status and nonzero executed count alongside report files.

Sources inspected 2026-09-24: [selectors](https://docs.maestro.dev/reference/selectors/core-selectors),
[launch state](https://docs.maestro.dev/reference/commands-available/launchapp),
[condition waits](https://docs.maestro.dev/reference/commands-available/extendedwaituntil),
[reports](https://docs.maestro.dev/maestro-flows/workspace-management/test-reports-and-artifacts),
[1.36.0 command source](https://github.com/mobile-dev-inc/maestro/blob/cli-1.36.0/maestro-cli/src/main/java/maestro/cli/command/TestCommand.kt).
