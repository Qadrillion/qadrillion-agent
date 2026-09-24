#!/usr/bin/env python3
"""Black-box contract tests; no product source, driver package or device default."""

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = "com.qadrillion.parcel"
ACTIVITY = f"{PACKAGE}/.MainActivity"
VALIDATION = "Enter a whole number from 1 to 5"
ARGS = None
MOBILE = Path(__file__).resolve().parents[3] / "mobile"
CONTRACT = MOBILE / "contract.md"
DEMO_SPEC = importlib.util.spec_from_file_location("mobile_demo", MOBILE / "demo.py")
demo = importlib.util.module_from_spec(DEMO_SPEC)
DEMO_SPEC.loader.exec_module(demo)


def replay_inputs(args):
    contract_hash = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    root = Path(args.run_dir).expanduser().resolve(strict=True)
    state = demo.load(root)
    if state.get("cleaned") or not state.get("booted"):
        raise RuntimeError("Replay requires a booted, uncleaned demo run")
    if not re.fullmatch(r"emulator-[0-9]+", args.serial) or state.get("serial") != args.serial:
        raise RuntimeError("Emulator serial does not match the owned demo run")
    if not re.fullmatch(r"[0-9a-f]{64}", args.expected_apk_sha256):
        raise RuntimeError("Expected APK SHA256 must be 64 lowercase hex digits")
    if not re.fullmatch(r"[0-9]+", str(state.get("api", ""))):
        raise RuntimeError("Demo run has no valid Android API identity")
    installed = state.get("installed", {})
    variant = installed.get("variant")
    if variant not in ("baseline", "seeded"):
        raise RuntimeError("Demo run has no installed fixture variant")
    build = state.get("builds", {}).get(variant, {})
    apk = root / variant / "parcel.apk"
    if (installed.get("sha256") != args.expected_apk_sha256
            or build.get("sha256") != args.expected_apk_sha256
            or installed.get("apk") != str(apk) or build.get("apk") != str(apk)
            or demo.digest(apk) != args.expected_apk_sha256):
        raise RuntimeError("APK identity does not match this run's installed fixture build")
    provenance = {
        "run_manifest": str(root / "run.json"),
        "run_manifest_sha256": demo.digest(root / "run.json"),
        "contract": str(CONTRACT), "contract_sha256": contract_hash,
        "variant": variant,
    }
    return state, provenance


def verify_device(device, args, state):
    serial = device.run("get-serialno")
    avd = device.run("emu", "avd", "name").splitlines()[:1]
    if serial != args.serial or avd != [state["avd_name"]]:
        raise RuntimeError("Live emulator serial or AVD identity does not match the owned demo run")
    paths = device.shell("pm", "path", PACKAGE).splitlines()
    if len(paths) != 1 or not paths[0].startswith("package:"):
        raise RuntimeError(f"Expected one installed fixture APK, found {paths}")
    hashes = device.shell("sha256sum", paths[0].removeprefix("package:")).split()
    if not hashes or hashes[0] != args.expected_apk_sha256:
        raise RuntimeError(f"Installed APK identity mismatch: expected {args.expected_apk_sha256}, found {hashes[:1]}")
    api = device.shell("getprop", "ro.build.version.sdk")
    if api != str(state["api"]):
        raise RuntimeError(f"Android API identity mismatch: expected {state['api']}, found {api}")
    return {"serial": serial, "avd_name": avd[0], "apk_sha256": hashes[0], "api": api}


class Device:
    def __init__(self, folder):
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self.sequence = 0

    def run(self, *arguments, check=True, binary=False):
        command = [ARGS.adb, "-s", ARGS.serial, *arguments]
        result = subprocess.run(command, capture_output=True, timeout=35)
        with (self.folder / "commands.jsonl").open("a") as log:
            log.write(json.dumps({
                "utc": datetime.now(timezone.utc).isoformat(), "argv": command,
                "returncode": result.returncode,
                "stdout": "[binary]" if binary else result.stdout.decode(errors="replace"),
                "stderr": result.stderr.decode(errors="replace"),
            }) + "\n")
        if check and result.returncode:
            raise RuntimeError(f"Command failed ({result.returncode}): {command}; {result.stderr.decode(errors='replace')}")
        return result.stdout if binary else result.stdout.decode(errors="replace").strip()

    def shell(self, *arguments, **kwargs):
        return self.run("shell", *arguments, **kwargs)

    def snapshot(self, label):
        self.sequence += 1
        remote = "/sdcard/qa-LOCAL-1-hierarchy.xml"
        self.shell("uiautomator", "dump", remote)
        xml = self.shell("cat", remote)
        self.shell("rm", remote)
        (self.folder / f"{self.sequence:03d}-{label}.xml").write_text(xml)
        root = ET.fromstring(xml)
        nodes = {}
        for node in root.iter("node"):
            resource_id = node.get("resource-id", "")
            if resource_id.startswith(PACKAGE + ":id/"):
                key = resource_id.split("/", 1)[1]
                if key in nodes:
                    raise RuntimeError(f"Ambiguous observed resource ID: {resource_id}")
                nodes[key] = node.attrib
        return nodes

    def expect(self, label, **expected):
        deadline = time.monotonic() + 10
        while True:
            nodes = self.snapshot(label)
            missing = set(expected) - nodes.keys()
            actual = {key: nodes[key].get("text", "") for key in expected if key in nodes}
            if not missing and actual == expected:
                return nodes
            if time.monotonic() >= deadline:
                if missing:
                    raise RuntimeError(f"{label}: missing or obscured resource IDs {sorted(missing)}; observed {nodes}")
                raise AssertionError(f"{label}: expected {expected}; actual {actual}")

    def tap(self, key):
        nodes = self.snapshot("before-tap-" + key)
        if key not in nodes:
            raise RuntimeError(f"Missing resource ID before tap: {key}")
        node = nodes[key]
        if node.get("enabled") != "true" or node.get("clickable") != "true":
            raise RuntimeError(f"Control is not actionable: {key}: {node}")
        bounds = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node["bounds"])
        if not bounds:
            raise RuntimeError(f"Invalid observed bounds: {node['bounds']}")
        x1, y1, x2, y2 = map(int, bounds.groups())
        self.shell("input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))

    def enter(self, quantity):
        self.tap("quantity")
        if quantity:
            self.shell("input", "text", quantity)
        actual = self.snapshot("entered-input")["quantity"]["text"]
        if actual != quantity:
            raise unittest.SkipTest(f"Native field/ADB input could not enter literal {quantity!r}; observed {actual!r}")
        self.shell("input", "keyevent", "KEYCODE_BACK")

    def launch(self, *flags):
        self.shell("am", "start", "-W", "-n", ACTIVITY, *flags)

    def reset(self):
        result = self.shell("pm", "clear", PACKAGE)
        if result != "Success":
            raise RuntimeError(f"App-only data reset failed: {result}")

    def pid(self):
        return self.shell("pidof", PACKAGE, check=False)

    def activity_state(self, label):
        state = self.shell("dumpsys", "activity", "activities")
        (self.folder / f"{label}-activity.txt").write_text(state)
        match = re.search(r"topResumedActivity=ActivityRecord\{([^ ]+) u0 com\.qadrillion\.parcel/\.MainActivity", state)
        return match.group(1) if match else None

    def expect_recreation_events(self, pid):
        deadline = time.monotonic() + 10
        while True:
            events = self.shell("logcat", "-b", "events", "-d", "--pid=" + pid, "-v", "threadtime")
            (self.folder / "recreation-events.txt").write_text(events)
            if "wm_on_destroy_called" in events and events.count("wm_on_create_called") >= 2:
                return
            if time.monotonic() >= deadline:
                raise RuntimeError("Lifecycle events did not prove activity destruction and recreation within 10s")
            time.sleep(0.1)

    def diagnostics(self, label):
        (self.folder / f"{label}-screen.png").write_bytes(self.run("exec-out", "screencap", "-p", binary=True))
        self.snapshot(label)
        self.activity_state(label)
        pid = self.pid()
        if pid:
            logs = self.shell("logcat", "-d", "--pid=" + pid, "-v", "threadtime")
            (self.folder / f"{label}-app-logcat.txt").write_text(logs)
            events = self.shell("logcat", "-b", "events", "-d", "--pid=" + pid, "-v", "threadtime")
            (self.folder / f"{label}-app-events.txt").write_text(events)
        logs = self.shell("logcat", "-b", "system", "-d", "-v", "threadtime", "-e", PACKAGE)
        (self.folder / f"{label}-system-logcat.txt").write_text(logs)


class ParcelContract(unittest.TestCase):
    def setUp(self):
        self.device = Device(Path(ARGS.evidence) / self._testMethodName)
        self.device.reset()
        self.addCleanup(self.cleanup_app)
        self.device.launch()
        self.device.expect("initial-zero", parcel_count="Parcels: 0", unit_count="Units: 0", quantity="")

    def cleanup_app(self):
        try:
            self.device.diagnostics("final")
        finally:
            self.device.reset()
            self.device.launch()
            self.device.expect("cleanup-zero", parcel_count="Parcels: 0", unit_count="Units: 0")
            self.device.shell("am", "force-stop", PACKAGE)

    def add(self, quantity, parcels, units):
        self.device.enter(str(quantity))
        self.device.tap("add_parcel")
        self.device.expect("accepted-" + str(quantity), parcel_count=f"Parcels: {parcels}",
                           unit_count=f"Units: {units}", validation="Parcel added", quantity="")

    def seed(self):
        self.add(2, 1, 2)
        self.add(3, 2, 5)

    def test_valid_range_and_accumulation(self):
        """C2,C4: every valid integer; cumulative nontrivial independent totals."""
        for quantity, parcels, units in [(1, 1, 1), (2, 2, 3), (3, 3, 6), (4, 4, 10), (5, 5, 15)]:
            self.add(quantity, parcels, units)

    def test_explicit_data_reset(self):
        """C1,C6: reset after nonzero data must zero both counters."""
        self.add(3, 1, 3)
        self.device.reset()
        self.device.launch()
        self.device.expect("explicit-reset", parcel_count="Parcels: 0", unit_count="Units: 0")

    def test_background_foreground(self):
        """C5: Home/resume preserves totals in the same activity and process."""
        self.seed()
        before_pid = self.device.pid()
        before_activity = self.device.activity_state("before-background")
        self.assertTrue(before_activity)
        self.device.shell("input", "keyevent", "KEYCODE_HOME")
        self.assertIsNone(self.device.activity_state("background"), "App did not leave foreground")
        self.device.launch("--activity-single-top")
        self.assertEqual(self.device.pid(), before_pid, "Background case unexpectedly changed the process")
        self.assertEqual(self.device.activity_state("foreground"), before_activity, "Background case unexpectedly changed the activity")
        self.device.expect("after-background", parcel_count="Parcels: 2", unit_count="Units: 5")

    def test_activity_recreation(self):
        """C5: clear-top recreates this standard-launch root activity in-process."""
        self.seed()
        before_pid = self.device.pid()
        before_activity = self.device.activity_state("before-recreation")
        self.assertTrue(before_activity)
        self.device.launch("--activity-clear-top")
        self.assertEqual(self.device.pid(), before_pid, "Recreation case unexpectedly terminated the process")
        after_activity = self.device.activity_state("after-recreation")
        self.assertTrue(after_activity)
        self.assertNotEqual(after_activity, before_activity, "Activity was not recreated")
        self.device.expect_recreation_events(before_pid)
        self.device.expect("after-recreation", parcel_count="Parcels: 2", unit_count="Units: 5")

    def test_process_termination_relaunch(self):
        """C5: verify real PID death, then launch without clearing data."""
        self.seed()
        before_pid = self.device.pid()
        self.assertTrue(before_pid)
        self.device.shell("am", "force-stop", PACKAGE)
        self.assertEqual(self.device.pid(), "", "Force-stop did not terminate app process")
        self.device.launch()
        after_pid = self.device.pid()
        self.assertTrue(after_pid)
        self.assertNotEqual(after_pid, before_pid)
        self.device.expect("after-process-relaunch", parcel_count="Parcels: 2", unit_count="Units: 5")


def rejected_case(quantity):
    def test(self):
        self.add(2, 1, 2)
        self.device.enter(quantity)
        self.device.tap("add_parcel")
        self.device.expect("rejected-input", parcel_count="Parcels: 1", unit_count="Units: 2", validation=VALIDATION)
    test.__doc__ = f"C3: reject literal {quantity!r} and preserve nonzero totals."
    return test


for name, value in [("empty", ""), ("zero", "0"), ("above_max", "6"), ("negative", "-1"),
                    ("decimal", "2.5"), ("text", "abc"), ("overflow", "2147483648")]:
    setattr(ParcelContract, "test_reject_" + name, rejected_case(value))


def main():
    global ARGS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="Owned demo.py run directory containing run.json")
    parser.add_argument("--serial", required=True, help="Task-owned Android emulator serial")
    parser.add_argument("--expected-apk-sha256", required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--evidence", required=True, help="New directory; existing evidence cannot be overwritten")
    parser.add_argument("--test", action="append", help="Exact unittest method, only for a documented diagnostic run")
    ARGS = parser.parse_args()
    state, provenance = replay_inputs(ARGS)
    evidence = Path(ARGS.evidence)
    evidence.mkdir(parents=True, exist_ok=False)
    preflight = Device(evidence / "preflight")
    device_identity = verify_device(preflight, ARGS, state)
    identity = {
        "utc": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
        "cwd": str(Path.cwd()), "package": PACKAGE,
        **provenance, **device_identity,
        "fingerprint": preflight.shell("getprop", "ro.build.fingerprint"),
        "locale": preflight.shell("getprop", "persist.sys.locale"),
        "configuration": preflight.shell("am", "get-config"),
        "abi": preflight.shell("getprop", "ro.product.cpu.abi"),
        "app_metadata": preflight.shell("dumpsys", "package", PACKAGE),
        "python": sys.version,
        "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (evidence / "identity.json").write_text(json.dumps(identity, indent=2))
    suite = (unittest.TestSuite(ParcelContract(name) for name in ARGS.test) if ARGS.test
             else unittest.defaultTestLoader.loadTestsFromTestCase(ParcelContract))
    with (evidence / "unittest.txt").open("w") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    unsuccessful = {id(case) for case, _ in result.failures + result.errors + result.skipped}
    summary = {"run": result.testsRun, "passed": result.testsRun - len(unsuccessful),
               "failed": len(result.failures), "errored": len(result.errors), "skipped": len(result.skipped),
               "failures": [(str(case), detail) for case, detail in result.failures],
               "errors": [(str(case), detail) for case, detail in result.errors],
               "skips": [(str(case), reason) for case, reason in result.skipped]}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2))
    print((evidence / "unittest.txt").read_text())
    print(json.dumps(summary, indent=2))
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
