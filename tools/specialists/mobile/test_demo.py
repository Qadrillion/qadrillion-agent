"""Offline ownership checks; these do not execute or simulate feature tests."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("mobile_demo", Path(__file__).with_name("demo.py"))
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)


class OwnershipTests(unittest.TestCase):
    def test_wrong_device_cannot_be_installed_or_stopped(self):
        state = {"avd_name": "qa-mobile-owned", "serial": "emulator-5560"}
        observed = subprocess.CompletedProcess([], 0, "personal-device\nOK\n", "")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "avd").mkdir()
            with patch.object(demo, "adb", return_value=observed) as adb:
                with self.assertRaisesRegex(RuntimeError, "identity"):
                    demo.install(root, state, "seeded")
                with self.assertRaisesRegex(RuntimeError, "identity"):
                    demo.cleanup(root, state)
                self.assertFalse(any(call.args[1:] == ("emu", "kill") for call in adb.call_args_list))
            self.assertTrue((root / "avd").is_dir())

    def test_empty_identity_is_not_a_matching_device(self):
        with patch.object(demo, "adb", return_value=subprocess.CompletedProcess([], 0, "", "")):
            with self.assertRaisesRegex(RuntimeError, "identity"):
                demo.assert_device({"avd_name": "qa-mobile-owned"})

    def test_cleanup_refuses_symlink_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            root.mkdir()
            unrelated = Path(directory) / "unrelated"
            unrelated.mkdir()
            (unrelated / "keep").write_text("existing data")
            (root / "avd").symlink_to(unrelated, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "symlink"):
                demo.cleanup(root, {})
            self.assertEqual((unrelated / "keep").read_text(), "existing data")
            (root / "avd").unlink()
            (root / "avd").mkdir()
            (root / "android-user").mkdir()
            (root / "evidence").mkdir()
            (root / "evidence/result.txt").write_text("first failure")
            demo.cleanup(root, {})
            self.assertFalse((root / "avd").exists())
            self.assertEqual((root / "evidence/result.txt").read_text(), "first failure")

    def test_copied_manifest_does_not_authorize_another_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            demo.save(root, {"owner": demo.MARKER, "root": "/another/run"})
            with self.assertRaisesRegex(RuntimeError, "identity"):
                demo.load(root)


if __name__ == "__main__":
    unittest.main()
