"""Offline configuration validation, including malformed and partial setups."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workspace"))
import config
import doctor


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.data = config.load(ROOT / "qa-config.json")

    def test_default_and_examples_validate_without_integrations(self):
        for path in [ROOT / "qa-config.json", *ROOT.glob("examples/config/*.json")]:
            with self.subTest(path=path):
                self.assertEqual([], config.validate(config.load(path)))

    def test_malformed_types_are_errors_not_crashes(self):
        for key in ("project", "context", "policy", "integrations", "runners", "environments"):
            data = copy.deepcopy(self.data)
            data[key] = None
            with self.subTest(key=key):
                self.assertTrue(config.validate(data))
        data = copy.deepcopy(self.data)
        data["integrations"] = [{"id": [], "transport": [], "enabled": "yes"}]
        data["environments"] = [{"id": "x", "role": []}]
        self.assertTrue(config.validate(data))

    def test_config_cannot_enable_production_or_skip_write_consent(self):
        self.data["policy"] = {"production_execution": True, "external_writes": "auto"}
        self.assertEqual(2, len(config.validate(self.data)))

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text('{"schema_version":1,"schema_version":2}')
            with self.assertRaises(ValueError):
                config.load(path)

    def test_runner_requires_argv_and_safe_paths(self):
        self.data["runners"] = [{"id": "x", "enabled": False, "scopes": ["other"],
                                 "cwd": "../outside", "argv": "echo example", "artifacts": "C:\\outside"}]
        self.assertGreaterEqual(len(config.validate(self.data)), 3)

    def test_supported_relative_paths_and_rejected_traversals(self):
        for path in (".", "automation/test suite", "test-results/run-1"):
            self.assertTrue(config.relative_path(path))
        for path in ("../x", "/tmp/x", "C:\\x", "a/../../x", "a\\..\\x", "~user/x", "x\x00"):
            self.assertFalse(config.relative_path(path))

    def test_duplicate_ids_rejected(self):
        row = {"id": "preview", "role": "test", "identity_evidence": "verified separately"}
        self.data["environments"] = [row, row.copy()]
        self.assertTrue(config.validate(self.data))

    def test_empty_workspace_reports_errors_and_unverified_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            rows = doctor.inspect(Path(folder))
        self.assertTrue(any(row["status"] == "error" for row in rows))
        self.assertEqual(3, sum(row["status"] == "unverified" for row in rows))

    def test_doctor_does_not_execute_configured_commands(self):
        self.data["integrations"] = [{"id": "issue", "provider": "example", "transport": "cli",
                                      "executable": "not-installed-test-client", "enabled": True,
                                      "scope": "test-project", "capabilities": ["tracker.read"]}]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "qa-config.json").write_text(json.dumps(self.data))
            with mock.patch.object(doctor.subprocess, "run") as run:
                rows = doctor.inspect(root)
            run.assert_not_called()
        self.assertTrue(any(row["check"] == "issue" and row["status"] == "error" for row in rows))

    def test_runner_path_resolves_in_its_cwd_and_requires_executable_mode(self):
        self.data["runners"] = [{"id": "local-runner", "enabled": True,
                                 "scopes": ["other"], "cwd": "suite",
                                 "argv": ["./run.sh"], "artifacts": "test-results"}]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "suite").mkdir()
            (root / "qa-config.json").write_text(json.dumps(self.data), encoding="utf-8")
            runner = root / "suite/run.sh"
            for mode, expected in ((None, "error"), (0o644, "error"), (0o755, "ok")):
                with self.subTest(mode=mode):
                    if mode is not None:
                        runner.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                        runner.chmod(mode)
                    with mock.patch.object(doctor.shutil, "which", return_value="/wrong/cwd/run.sh"):
                        rows = doctor.inspect(root)
                    self.assertEqual([expected], [row["status"] for row in rows
                                                 if row["check"] == "local-runner"])


if __name__ == "__main__":
    unittest.main()
