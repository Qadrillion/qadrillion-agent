"""Regression checks for portable generation and native hook boundaries."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"tools/agents/{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


adapter = module("adapter")
sync = module("sync")


def ascii_locale():
    environment = dict(os.environ, LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0")
    result = subprocess.run([sys.executable, "-c", "import locale; print(locale.getpreferredencoding(False))"],
                            env=environment, capture_output=True, text=True, encoding="utf-8", check=True)
    if result.stdout.strip().lower() not in {"ascii", "us-ascii", "ansi_x3.4-1968"}:
        raise AssertionError(f"Expected an ASCII locale, got {result.stdout!r}")
    return environment


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qa runtime space ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.hooks = self.root / ".cursor/hooks"
        self.hooks.mkdir(parents=True)
        self.set_guard("printf '%s\\n' '{\"permission\":\"allow\"}'\n")

    def set_guard(self, script):
        (self.hooks / "guard with spaces.sh").write_text("#!/usr/bin/env bash\n" + script)
        entries = [{"command": "'.cursor/hooks/guard with spaces.sh' 'argument with spaces'"}]
        (self.root / ".cursor/hooks.json").write_text(json.dumps({"hooks": {
            "beforeShellExecution": entries, "beforeMCPExecution": entries,
            "beforeReadFile": entries, "sessionStart": entries, "stop": entries, "sessionEnd": entries}}))

    def call(self, tool="Bash", value=None, runtime="codex", raw=None, **fields):
        data = {"hook_event_name": "PreToolUse", "tool_name": tool,
                "tool_input": {"command": "echo safe"} if value is None else value,
                "cwd": str(self.root), **fields}
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(data) if raw is None else raw)), contextlib.redirect_stdout(output):
            adapter.main(runtime=runtime, root=self.root)
        return json.loads(output.getvalue())

    def permission(self, result):
        return result.get("hookSpecificOutput", {}).get("permissionDecision")

    def test_allow_does_not_override_native_permissions(self):
        self.assertEqual(self.call(), {})

    def test_approval_marker_never_authorizes(self):
        self.set_guard("printf '%s\\n' '{\"permission\":\"ask\",\"user_message\":\"publish\"}'\n")
        for command in ("publish", "APPROVED=1 publish", "APPROVED=1 APPROVED=1 publish"):
            with self.subTest(command=command):
                self.assertEqual(self.permission(self.call(value={"command": command})), "deny")
                self.assertEqual(self.permission(self.call(value={"command": command}, runtime="claude")), "ask")

    def test_mcp_name_and_arguments_preserved(self):
        capture = self.root / "payload.json"
        self.set_guard(f"cat > {shlex.quote(str(capture))}\nprintf '%s\\n' '{{\"permission\":\"allow\"}}'\n")
        self.assertEqual(self.call("mcp__postman__get_collection", {"id": "42"}), {})
        self.assertEqual(json.loads(capture.read_text()), {
            "server_name": "postman", "tool_name": "get_collection", "tool_input": {"id": "42"}})

    def test_mcp_metadata_is_not_interpreted_as_local_file_paths(self):
        capture = self.root / "payload.json"
        self.set_guard(f"cat > {shlex.quote(str(capture))}\nprintf '%s\\n' '{{\"permission\":\"allow\"}}'\n")
        for runtime in ("codex", "claude"):
            for metadata in ({"source": None}, {"paths": []}, {"path": {"node": "remote"}}):
                value = {"metadata": metadata}
                with self.subTest(runtime=runtime, metadata=metadata):
                    self.assertEqual(self.call("mcp__fixture__read_record", value, runtime=runtime), {})
                    self.assertEqual(json.loads(capture.read_text())["tool_input"], value)

    def test_shell_alias_and_command_are_data(self):
        capture = self.root / "payload.json"
        arg = self.root / "argument.txt"
        self.set_guard(f"cat > {shlex.quote(str(capture))}\nprintf '%s' \"$1\" > {shlex.quote(str(arg))}\nprintf '%s\\n' '{{\"permission\":\"allow\"}}'\n")
        command = f"echo $(touch {shlex.quote(str(self.root / 'executed'))})"
        self.assertEqual(self.call("exec_command", {"cmd": command}), {})
        self.assertEqual(json.loads(capture.read_text())["command"], command)
        self.assertEqual(arg.read_text(), "argument with spaces")
        self.assertFalse((self.root / "executed").exists())

    def test_malformed_events_fail_closed(self):
        for raw in ("{", "[]", "null", '{"tool_name":"Bash","tool_input":[]}',
                    '{"tool_name":"Bash","tool_input":{}}',
                    '{"tool_name":"Bash","tool_input":{"command":1}}'):
            for runtime in ("codex", "claude"):
                with self.subTest(raw=raw, runtime=runtime):
                    self.assertEqual(self.permission(self.call(raw=raw, runtime=runtime)), "deny")

    def test_guard_crashes_and_malformed_outputs_fail_closed(self):
        for script in ("exit 1", "exit 2", "printf not-json", "printf '[]'",
                       "printf '{}'", "printf '{\"permission\":\"maybe\"}'",
                       "printf '{\"permission\":\"deny\",\"user_message\":{}}'"):
            with self.subTest(script=script):
                self.set_guard(script)
                self.assertEqual(self.permission(self.call()), "deny")
                self.assertEqual(self.permission(self.call(runtime="claude")), "deny")

    def test_timeout_fails_closed(self):
        self.set_guard("exec sleep 10\n")
        with patch.object(adapter, "POLICY_TIMEOUT", 0.02):
            self.assertEqual(self.permission(self.call()), "deny")

    def test_missing_or_invalid_manifest_fails_closed(self):
        manifest = self.root / ".cursor/hooks.json"
        for value in ('{"hooks":{}}', '{"hooks":[]}', "[]", "invalid"):
            manifest.write_text(value)
            self.assertEqual(self.permission(self.call()), "deny")
        manifest.unlink()
        self.assertEqual(self.permission(self.call()), "deny")

    def test_utf8_event_manifest_and_guard_output_under_ascii_locale(self):
        script = self.root / "tools/agents/adapter.py"
        script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "tools/agents/adapter.py", script)
        manifest = self.root / ".cursor/hooks.json"
        value = json.loads(manifest.read_text(encoding="utf-8"))
        value["description"] = "Café policy"
        manifest.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        guard = self.hooks / "guard with spaces.sh"
        guard.write_text("printf '%s\\n' '{\"permission\":\"ask\",\"user_message\":\"Café review\"}'\n", encoding="utf-8")
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                 "tool_input": {"command": "printf café"}, "cwd": str(self.root)}
        result = subprocess.run([sys.executable, "-B", str(script), "--runtime", "claude"],
                                input=json.dumps(event, ensure_ascii=False), env=ascii_locale(),
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "ask")
        self.assertEqual(output["permissionDecisionReason"], "Café review")

    def test_file_tools_require_paths_including_notebooks(self):
        for tool in adapter.FILE_TOOLS:
            with self.subTest(tool=tool):
                self.assertEqual(self.permission(self.call(tool, {})), "deny")
        self.assertEqual(self.call("NotebookEdit", {"notebook_path": "notes.ipynb"}), {})

    def test_all_patch_headers_and_nested_paths_checked(self):
        capture = self.root / "paths.jsonl"
        self.set_guard(f"cat >> {shlex.quote(str(capture))}\nprintf '\\n' >> {shlex.quote(str(capture))}\nprintf '%s\\n' '{{\"permission\":\"allow\"}}'\n")
        patch_text = "*** Begin Patch\n*** Add File: new.txt\n+new\n*** Update File: old.txt\n*** Move to: moved.txt\n@@\n-old\n+new\n*** Delete File: delete.txt\n*** End Patch"
        self.assertEqual(self.call("apply_patch", {"command": patch_text}), {})
        paths = {json.loads(line)["file_path"] for line in capture.read_text().splitlines()}
        self.assertTrue({"new.txt", "old.txt", "moved.txt", "delete.txt"}.issubset(paths))
        self.assertEqual(self.call("MultiEdit", {"edits": [{"source": "one", "destination": "two"},
                                                         {"file_path": "three"}]}), {})
        paths = {json.loads(line)["file_path"] for line in capture.read_text().splitlines()}
        self.assertTrue({"one", "two", "three"}.issubset(paths))

    def test_symlink_resolved_target_is_checked(self):
        secret = self.root / ".env"
        secret.write_text("fixture")
        (self.root / "safe.txt").symlink_to(secret)
        paths = adapter.tool_paths("Read", {"file_path": "safe.txt"}, self.root)
        self.assertIn(str(secret.resolve()), paths)

    def test_invalid_patch_header_never_skips_a_path(self):
        for body in ("*** Update File: ", "*** Move to: target", "*** Unknown File: foo", "nothing"):
            with self.subTest(body=body):
                result = self.call("apply_patch", {"command": f"*** Begin Patch\n{body}\n*** End Patch"})
                self.assertEqual(self.permission(result), "deny")

    def test_lifecycle_failure_is_advisory(self):
        self.set_guard("exit 1")
        self.assertIn("systemMessage", self.call(hook_event_name="Stop"))

    def test_stop_followup_and_native_matchers(self):
        self.set_guard("printf '%s\\n' '{\"followup_message\":\"Update the handoff\"}'")
        self.assertEqual(self.call(hook_event_name="Stop"), {"decision": "block", "reason": "Update the handoff"})
        for tool in adapter.SHELL_TOOLS | adapter.FILE_TOOLS | {"mcp__jira__create_issue"}:
            self.assertTrue(re.fullmatch(sync.MATCHER, tool), tool)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qa sync space ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in (".cursor", "tools/agents"):
            shutil.copytree(ROOT / directory, self.root / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "generated.json"))

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.root / "tools/agents/sync.py"), *args],
                              cwd=self.root.parent, capture_output=True, text=True)

    def hook_command(self):
        config = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))
        return config["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    def invoke_hook(self, directory):
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                 "tool_input": {"command": "printf harmless-fixture"}, "cwd": str(directory)}
        result = subprocess.run(["bash", "-c", self.hook_command()], cwd=directory,
                                input=json.dumps(event), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        return output["permissionDecisionReason"]

    def root_guard(self):
        guard = self.root / ".cursor/hooks/launcher fixture.sh"
        guard.write_text("printf '%s\\n' '{\"permission\":\"deny\",\"user_message\":\"QA workspace policy reached\"}'\n",
                         encoding="utf-8")
        manifest = {"hooks": {"beforeShellExecution": [{"command": "'.cursor/hooks/launcher fixture.sh'"}]}}
        (self.root / ".cursor/hooks.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_clean_export_runs_without_private_installer_or_git(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cli("--check").returncode, 0)
        self.assertFalse((self.root / ".git").exists())
        self.assertTrue((self.root / ".claude/agents/test-runner.md").is_file())
        self.assertTrue((self.root / ".agents/skills/qa/SKILL.md").is_file())

    def test_generated_hook_uses_workspace_policy_from_nested_git_checkout(self):
        sync.sync(self.root)
        self.root_guard()
        nested = self.root / "source/product with spaces"
        nested.mkdir(parents=True)
        for directory in (self.root, nested):
            subprocess.run(["git", "init", "--quiet", str(directory)], check=True, capture_output=True)
        shadow = nested / ".codex/hooks/adapter.py"
        shadow.parent.mkdir(parents=True)
        shadow.write_text("raise RuntimeError('Wrong nested product adapter ran')\n", encoding="utf-8")
        self.assertEqual(self.invoke_hook(nested), "QA workspace policy reached")

    def test_generated_hook_runs_in_git_free_archive(self):
        sync.sync(self.root)
        self.root_guard()
        nested = self.root / "source/product with spaces"
        nested.mkdir(parents=True)
        self.assertFalse((self.root / ".git").exists())
        self.assertEqual(self.invoke_hook(nested), "QA workspace policy reached")

    def test_generated_hook_denies_missing_or_ambiguous_workspace(self):
        sync.sync(self.root)
        self.root_guard()
        with tempfile.TemporaryDirectory(prefix="unrelated cwd ") as directory:
            self.assertIn("exactly one ancestor QA workspace", self.invoke_hook(Path(directory)))
        nested = self.root / "source/product with spaces"
        marker = nested / sync.LEDGER
        marker.parent.mkdir(parents=True)
        marker.write_bytes((self.root / sync.LEDGER).read_bytes())
        self.assertIn("ambiguous policy root", self.invoke_hook(nested))

    def test_generated_hook_rejects_unrecognized_or_symlinked_workspace_marker(self):
        sync.sync(self.root)
        marker = self.root / sync.LEDGER
        original = marker.read_bytes()
        marker.write_text('{"generator":"another-framework"}', encoding="utf-8")
        self.assertIn("Unrecognized QA workspace marker", self.invoke_hook(self.root))
        real = self.root / "actual-marker.json"
        real.write_bytes(original)
        marker.unlink()
        marker.symlink_to(real)
        self.assertIn("marker must not be a symlink", self.invoke_hook(self.root))

    def test_generation_and_check_under_ascii_locale(self):
        environment = ascii_locale()
        source = self.root / ".cursor/agents/test-runner.md"
        source.write_text(source.read_text(encoding="utf-8") + "\nUnicode QA: café.\n", encoding="utf-8")
        for arguments in ([], ["--check"]):
            result = subprocess.run([sys.executable, "-B", str(self.root / "tools/agents/sync.py"), *arguments],
                                    cwd=self.root.parent, env=environment,
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
        generated = tomllib.loads((self.root / ".codex/agents/test-runner.toml").read_text(encoding="utf-8"))
        self.assertIn("Unicode QA: café.", generated["developer_instructions"])

    def test_idempotence_and_canonical_changes(self):
        sync.sync(self.root)
        self.assertEqual(sync.sync(self.root), [])
        source = self.root / ".cursor/agents/test-runner.md"
        source.write_text(source.read_text() + "\nA canonical change.\n")
        skill = self.root / ".cursor/skills/qa/SKILL.md"
        skill.write_text(skill.read_text() + "\nUpdated canonical skill.\n")
        with self.assertRaisesRegex(sync.SyncError, "drift"):
            sync.sync(self.root, check=True)
        sync.sync(self.root)
        self.assertIn("A canonical change.", (self.root / ".codex/agents/test-runner.toml").read_text())
        self.assertIn("Updated canonical skill.", (self.root / ".claude/skills/qa/SKILL.md").read_text())
        self.assertEqual(sync.sync(self.root, check=True), [])

    def test_readonly_roles_keep_native_restrictions(self):
        sync.sync(self.root)
        for name in ("code-explorer", "code-reviewer"):
            with self.subTest(name=name):
                codex = tomllib.loads((self.root / f".codex/agents/{name}.toml").read_text())
                self.assertEqual(codex["sandbox_mode"], "read-only")
                claude, _ = sync.metadata(self.root / f".claude/agents/{name}.md")
                self.assertEqual(set(claude["tools"].split(", ")), {"Read", "Grep", "Glob"})
        for name in ("test-runner", "ticket-writer", "tracker-reporter"):
            with self.subTest(name=name):
                codex = tomllib.loads((self.root / f".codex/agents/{name}.toml").read_text())
                self.assertNotIn("sandbox_mode", codex)
                claude, _ = sync.metadata(self.root / f".claude/agents/{name}.md")
                self.assertNotIn("tools", claude)

    def test_invalid_readonly_value_cannot_drop_restrictions(self):
        source = self.root / ".cursor/agents/code-explorer.md"
        source.write_text(source.read_text().replace("readonly: true", "readonly: yes"))
        with self.assertRaisesRegex(sync.SyncError, "readonly must be true or false"):
            sync.sync(self.root)
        self.assertFalse((self.root / ".codex/agents/code-explorer.toml").exists())

    def test_local_generated_modifications_rejected_before_other_writes(self):
        sync.sync(self.root)
        path = self.root / ".codex/agents/test-runner.toml"
        path.write_text("custom local content")
        before = (self.root / sync.LEDGER).read_bytes()
        source = self.root / ".cursor/skills/qa/SKILL.md"
        source.write_text(source.read_text() + "\nCanonical edit.\n")
        with self.assertRaisesRegex(sync.SyncError, "changed locally"):
            sync.sync(self.root)
        self.assertEqual(path.read_text(), "custom local content")
        self.assertEqual((self.root / sync.LEDGER).read_bytes(), before)

    def test_preserves_unrelated_settings_and_custom_skills(self):
        sync.sync(self.root)
        settings = self.root / ".claude/settings.json"
        value = json.loads(settings.read_text())
        value["permissions"] = {"deny": ["Bash(secret-command)"]}
        custom = {"matcher": "Read", "hooks": [{"type": "command", "command": "custom-audit"}]}
        value["hooks"]["PreToolUse"].append(custom)
        settings.write_text(json.dumps(value))
        local = self.root / ".agents/skills/private/SKILL.md"
        local.parent.mkdir()
        local.write_text("private skill")
        sync.sync(self.root)
        self.assertEqual(json.loads(settings.read_text()), value)
        self.assertEqual(local.read_text(), "private skill")

    def test_managed_hook_edits_are_rejected(self):
        sync.sync(self.root)
        path = self.root / ".codex/hooks.json"
        value = json.loads(path.read_text())
        value["hooks"]["PreToolUse"][0]["matcher"] = "never"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(sync.SyncError, "Managed hook changed locally"):
            sync.sync(self.root)

    def test_first_install_preserves_custom_runtime_settings(self):
        path = self.root / ".claude/settings.json"
        path.parent.mkdir()
        custom = {"matcher": "Read", "hooks": [{"type": "command", "command": "audit"}]}
        path.write_text(json.dumps({"model": "chosen-by-user", "hooks": {"PreToolUse": [custom]}}))
        sync.sync(self.root)
        settings = json.loads(path.read_text())
        self.assertEqual(settings["model"], "chosen-by-user")
        self.assertIn(custom, settings["hooks"]["PreToolUse"])

    def test_materializes_both_real_and_text_symlinks(self):
        directory = self.root / ".agents/skills"
        directory.mkdir(parents=True)
        (directory / "qa").symlink_to("../../.cursor/skills/qa")
        (directory / "qa-workflow").write_text("../../.cursor/skills/qa-workflow")
        with patch("os.symlink", side_effect=OSError("not supported")):
            sync.sync(self.root)
        self.assertFalse((directory / "qa").is_symlink())
        self.assertTrue((directory / "qa/SKILL.md").is_file())
        self.assertTrue((directory / "qa-workflow/SKILL.md").is_file())
        sync.sync(self.root, check=True)

    def test_unknown_collision_or_parent_symlink_not_overwritten(self):
        destination = self.root / ".codex/agents/test-runner.toml"
        destination.parent.mkdir(parents=True)
        destination.write_text("custom")
        with self.assertRaisesRegex(sync.SyncError, "changed locally"):
            sync.sync(self.root)
        self.assertEqual(destination.read_text(), "custom")
        destination.unlink()
        external = self.root / "external"
        external.mkdir()
        (self.root / ".agents").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(sync.SyncError, "symlink"):
            sync.sync(self.root)

    def test_deleted_canonical_agent_removes_only_owned_output(self):
        sync.sync(self.root)
        (self.root / ".cursor/agents/test-runner.md").unlink()
        custom = self.root / ".codex/agents/custom.toml"
        custom.write_text("custom")
        sync.sync(self.root)
        self.assertFalse((self.root / ".codex/agents/test-runner.toml").exists())
        self.assertFalse((self.root / ".claude/agents/test-runner.md").exists())
        self.assertEqual(custom.read_text(), "custom")

    def test_skill_script_executable_mode_is_preserved(self):
        source = self.root / ".cursor/skills/qa/run.sh"
        source.write_text("#!/bin/sh\nprintf verified\n")
        source.chmod(0o755)
        sync.sync(self.root)
        script = self.root / ".agents/skills/qa/run.sh"
        result = subprocess.run([str(script)], capture_output=True, text=True)
        self.assertEqual(result.stdout, "verified")
        script.chmod(0o644)
        with self.assertRaisesRegex(sync.SyncError, "changed locally"):
            sync.sync(self.root)

    def test_launchers_deny_malformed_input_and_missing_adapter(self):
        sync.sync(self.root)
        launchers = ([sys.executable, str(self.root / ".codex/hooks/adapter.py")],
                     ["bash", str(self.root / ".claude/hooks/pretooluse.sh")])
        for argv in launchers:
            with self.subTest(argv=argv):
                result = subprocess.run(argv, input="not-json", capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        (self.root / "tools/agents/adapter.py").unlink()
        for argv in launchers:
            with self.subTest(argv=argv):
                result = subprocess.run(argv, input="{}", capture_output=True, text=True)
                if argv[0] == "bash":
                    self.assertEqual(result.returncode, 2)
                else:
                    self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
