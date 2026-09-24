"""Offline replay preflight checks; no feature suite or device is executed."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "reference/mobile/tests/test_parcel.py"
SPEC = importlib.util.spec_from_file_location("parcel_replay", SOURCE)
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


class ReadOnlyDevice:
    def __init__(self, state, overrides=None):
        self.calls = []
        self.responses = {
            ("get-serialno",): state["serial"],
            ("emu", "avd", "name"): state["avd_name"] + "\nOK",
            ("shell", "pm", "path", replay.PACKAGE): "package:/data/app/fixture/base.apk",
            ("shell", "sha256sum", "/data/app/fixture/base.apk"):
                state["installed"]["sha256"] + "  /data/app/fixture/base.apk",
            ("shell", "getprop", "ro.build.version.sdk"): state["api"],
        }
        self.responses.update(overrides or {})

    def run(self, *arguments):
        self.calls.append(arguments)
        if arguments not in self.responses:
            raise AssertionError(f"Preflight attempted an unexpected or mutating command: {arguments}")
        return self.responses[arguments]

    def shell(self, *arguments):
        return self.run("shell", *arguments)


class ReplayPreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        apk = self.root / "baseline/parcel.apk"
        apk.parent.mkdir()
        apk.write_bytes(b"offline synthetic fixture build")
        self.apk_hash = hashlib.sha256(apk.read_bytes()).hexdigest()
        build = {"apk": str(apk), "sha256": self.apk_hash}
        self.state = {
            "owner": replay.demo.MARKER, "root": str(self.root), "id": "test-owned",
            "avd_name": "qa-mobile-test-owned", "serial": "emulator-5562",
            "api": "34", "booted": True, "builds": {"baseline": build},
            "installed": {**build, "variant": "baseline"},
        }
        self.args = SimpleNamespace(run_dir=str(self.root), serial=self.state["serial"],
                                    expected_apk_sha256=self.apk_hash)
        self.save()

    def save(self):
        (self.root / "run.json").write_text(json.dumps(self.state))

    def test_current_contract_and_manifest_are_hashed_before_device_access(self):
        with patch.object(replay.subprocess, "run") as execute:
            state, provenance = replay.replay_inputs(self.args)
        execute.assert_not_called()
        contract = Path(__file__).with_name("contract.md").resolve()
        self.assertEqual(provenance["contract"], str(contract))
        self.assertEqual(provenance["contract_sha256"], hashlib.sha256(contract.read_bytes()).hexdigest())
        self.assertEqual(provenance["run_manifest_sha256"],
                         hashlib.sha256((self.root / "run.json").read_bytes()).hexdigest())
        self.assertEqual(state, self.state)

    def test_owned_emulators_can_use_different_serials_and_recorded_api(self):
        for serial, api in [("emulator-5562", "34"), ("emulator-5578", "35")]:
            with self.subTest(serial=serial, api=api):
                self.state.update(serial=serial, api=api)
                self.args.serial = serial
                self.save()
                state, _ = replay.replay_inputs(self.args)
                observed = replay.verify_device(ReadOnlyDevice(state), self.args, state)
                self.assertEqual(observed, {"serial": serial, "api": api,
                                           "avd_name": state["avd_name"], "apk_sha256": self.apk_hash})

    def test_missing_contract_stops_before_device_access(self):
        with patch.object(replay, "CONTRACT", self.root / "absent-contract.md"):
            with patch.object(replay.subprocess, "run") as execute:
                with self.assertRaises(FileNotFoundError):
                    replay.replay_inputs(self.args)
            execute.assert_not_called()

    def test_missing_manifest_stops_before_device_access(self):
        (self.root / "run.json").unlink()
        with patch.object(replay.subprocess, "run") as execute:
            with self.assertRaises(FileNotFoundError):
                replay.replay_inputs(self.args)
        execute.assert_not_called()

    def test_invalid_ownership_stops_before_device_access(self):
        original = copy.deepcopy(self.state)
        changes = [
            {"owner": None}, {"owner": "another-fixture"}, {"root": "/another/run"},
            {"avd_name": "personal-device"}, {"serial": "emulator-5560"},
            {"serial": None}, {"booted": False}, {"cleaned": True}, {"api": None},
            {"installed": {}},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.state = {**copy.deepcopy(original), **change}
                self.save()
                with patch.object(replay.subprocess, "run") as execute:
                    with self.assertRaises(RuntimeError):
                        replay.replay_inputs(self.args)
                execute.assert_not_called()

    def test_physical_serial_is_rejected_even_when_manifest_matches(self):
        self.args.serial = self.state["serial"] = "physical-123"
        self.save()
        with self.assertRaisesRegex(RuntimeError, "Emulator serial"):
            replay.replay_inputs(self.args)

    def test_expected_hash_must_match_manifest_build_and_local_apk(self):
        original = copy.deepcopy(self.state)
        for location in ("expected", "installed", "build", "local"):
            with self.subTest(location=location):
                self.state = copy.deepcopy(original)
                self.args.expected_apk_sha256 = self.apk_hash
                if location == "expected":
                    self.args.expected_apk_sha256 = "0" * 64
                elif location == "installed":
                    self.state["installed"]["sha256"] = "0" * 64
                elif location == "build":
                    self.state["builds"]["baseline"]["sha256"] = "0" * 64
                else:
                    Path(self.state["installed"]["apk"]).write_bytes(b"changed fixture build")
                self.save()
                with patch.object(replay.subprocess, "run") as execute:
                    with self.assertRaisesRegex(RuntimeError, "APK identity"):
                        replay.replay_inputs(self.args)
                execute.assert_not_called()

    def test_relocated_apk_is_not_authorized_by_a_copied_hash(self):
        for entry in (self.state["installed"], self.state["builds"]["baseline"]):
            entry["apk"] = "/another/run/baseline/parcel.apk"
        self.save()
        with self.assertRaisesRegex(RuntimeError, "APK identity"):
            replay.replay_inputs(self.args)

    def test_wrong_live_serial_or_avd_stops_before_package_access(self):
        for overrides in [{("get-serialno",): "emulator-5560"},
                          {("emu", "avd", "name"): "personal-device\nOK"},
                          {("emu", "avd", "name"): ""}]:
            with self.subTest(overrides=overrides):
                device = ReadOnlyDevice(self.state, overrides)
                with self.assertRaisesRegex(RuntimeError, "AVD identity"):
                    replay.verify_device(device, self.args, self.state)
                self.assertFalse(any(call[0] == "shell" for call in device.calls))

    def test_wrong_package_build_or_api_never_mutates_device(self):
        for overrides in [
            {("shell", "pm", "path", replay.PACKAGE): ""},
            {("shell", "pm", "path", replay.PACKAGE): "package:/one.apk\npackage:/two.apk"},
            {("shell", "sha256sum", "/data/app/fixture/base.apk"): "0" * 64 + " base.apk"},
            {("shell", "sha256sum", "/data/app/fixture/base.apk"): ""},
            {("shell", "getprop", "ro.build.version.sdk"): "35"},
        ]:
            with self.subTest(overrides=overrides):
                with self.assertRaises(RuntimeError):
                    replay.verify_device(ReadOnlyDevice(self.state, overrides), self.args, self.state)


if __name__ == "__main__":
    unittest.main()
