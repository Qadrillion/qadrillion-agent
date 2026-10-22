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
        self.hooks = self.root / ".agent/hooks"
        self.hooks.mkdir(parents=True)
        self.set_guard("printf '%s\\n' '{\"permission\":\"allow\"}'\n")


    def set_guard(self, script):
        (self.hooks / "guard with spaces.sh").write_text("#!/usr/bin/env bash\n" + script)
        entries = [{"command": "'.agent/hooks/guard with spaces.sh' 'argument with spaces'"}]
        (self.root / ".agent/hooks.json").write_text(json.dumps({"hooks": {
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
        manifest = self.root / ".agent/hooks.json"
        for value in ('{"hooks":{}}', '{"hooks":[]}', "[]", "invalid"):
            manifest.write_text(value)
            self.assertEqual(self.permission(self.call()), "deny")
        manifest.unlink()
        self.assertEqual(self.permission(self.call()), "deny")


    def test_utf8_event_manifest_and_guard_output_under_ascii_locale(self):
        script = self.root / "tools/agents/adapter.py"
        script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "tools/agents/adapter.py", script)
        manifest = self.root / ".agent/hooks.json"
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
        self.assertTrue({str(self.root / name) for name in
                         ("new.txt", "old.txt", "moved.txt", "delete.txt")}.issubset(paths))
        self.assertEqual(self.call("MultiEdit", {"edits": [{"source": "one", "destination": "two"},
                                                         {"file_path": "three"}]}), {})
        paths = {json.loads(line)["file_path"] for line in capture.read_text().splitlines()}
        self.assertTrue({str(self.root / name) for name in ("one", "two", "three")}.issubset(paths))


    def test_symlink_resolved_target_is_checked(self):
        secret = self.root / ".env"
        secret.write_text("fixture")
        (self.root / "safe.txt").symlink_to(secret)
        paths = adapter.tool_paths("Read", {"file_path": "safe.txt"}, self.root)
        self.assertIn(str(secret.resolve()), paths)


    def test_policy_cannot_escape_neutral_hook_directory(self):
        outside = self.root / "outside.sh"
        marker = self.root / "unexpected-execution"
        outside.write_text(f"touch {shlex.quote(str(marker))}\nprintf '%s\\n' '{{\"permission\":\"allow\"}}'\n")
        link = self.hooks / "outside.sh"
        link.symlink_to(outside)
        manifest = self.root / ".agent/hooks.json"
        for command in ("outside.sh", ".agent/hooks/outside.sh"):
            manifest.write_text(json.dumps({"hooks": {"beforeShellExecution": [{"command": command}]}}))
            self.assertEqual(self.permission(self.call()), "deny")
            self.assertFalse(marker.exists())


    def test_policy_rejects_symlinked_neutral_source_directory(self):
        canonical = self.root / ".agent"
        actual = self.root / "external-source"
        canonical.rename(actual)
        canonical.symlink_to(actual, target_is_directory=True)
        self.assertEqual(self.permission(self.call()), "deny")


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
        for directory in (".agent", "tools/agents"):
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
        guard = self.root / ".agent/hooks/launcher fixture.sh"
        guard.write_text("printf '%s\\n' '{\"permission\":\"deny\",\"user_message\":\"QA workspace policy reached\"}'\n",
                         encoding="utf-8")
        manifest = {"hooks": {"beforeShellExecution": [{"command": "'.agent/hooks/launcher fixture.sh'"}]}}
        (self.root / ".agent/hooks.json").write_text(json.dumps(manifest), encoding="utf-8")


    def test_clean_export_runs_without_private_installer_or_git(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cli("--check").returncode, 0)
        self.assertFalse((self.root / ".git").exists())
        self.assertTrue((self.root / ".claude/agents/test-runner.md").is_file())
        self.assertTrue((self.root / ".agents/skills/qa/SKILL.md").is_file())
        self.assertTrue((self.root / ".agents/skills/qa").is_symlink())
        self.assertFalse((self.root / ".cursor").exists())


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
        source = self.root / ".agent/agents/test-runner.md"
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
        source = self.root / ".agent/agents/test-runner.md"
        source.write_text(source.read_text() + "\nA canonical change.\n")
        skill = self.root / ".agent/skills/qa/SKILL.md"
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
        source = self.root / ".agent/agents/code-explorer.md"
        source.write_text(source.read_text().replace("readonly: true", "readonly: yes"))
        with self.assertRaisesRegex(sync.SyncError, "readonly must be true or false"):
            sync.sync(self.root)
        self.assertFalse((self.root / ".codex/agents/code-explorer.toml").exists())


    def test_local_generated_modifications_rejected_before_other_writes(self):
        sync.sync(self.root)
        path = self.root / ".codex/agents/test-runner.toml"
        path.write_text("custom local content")
        before = (self.root / sync.LEDGER).read_bytes()
        source = self.root / ".agent/skills/qa/SKILL.md"
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


    def test_migrates_legacy_real_and_text_symlinks_to_neutral_source(self):
        directory = self.root / ".agents/skills"
        directory.mkdir(parents=True)
        (directory / "qa").symlink_to("../../.cursor/skills/qa")
        (directory / "qa-workflow").write_text("../../.cursor/skills/qa-workflow")
        sync.sync(self.root)
        self.assertTrue((directory / "qa").is_symlink())
        self.assertEqual((directory / "qa").readlink().as_posix(), "../../.agent/skills/qa")
        self.assertTrue((directory / "qa/SKILL.md").is_file())
        self.assertTrue((directory / "qa-workflow/SKILL.md").is_file())
        sync.sync(self.root, check=True)


    def legacy_copies(self):
        sync.sync(self.root)
        state = json.loads((self.root / sync.LEDGER).read_text())
        for relative, target in state.pop("links").items():
            destination = self.root / relative
            source = destination.resolve()
            destination.unlink()
            shutil.copytree(source, destination)
            for path in destination.rglob("*"):
                if path.is_file():
                    name = path.relative_to(self.root).as_posix()
                    state["files"][name] = sync.digest(path.read_bytes())
                    state["modes"][name] = path.stat().st_mode & 0o777
        state["version"] = 1
        (self.root / sync.LEDGER).write_text(json.dumps(state))


    def test_owned_copies_migrate_to_one_source_without_cursor_alias(self):
        self.legacy_copies()
        sync.sync(self.root)
        for runtime in (".agents", ".claude"):
            path = self.root / runtime / "skills/qa"
            self.assertTrue(path.is_symlink())
            self.assertEqual(path.resolve(), (self.root / ".agent/skills/qa").resolve())
        self.assertFalse((self.root / ".cursor").exists())
        self.assertEqual(sync.sync(self.root), [])


    def test_modified_or_extra_copy_blocks_all_migration_writes(self):
        for kind in ("content", "extra", "symlink"):
            with self.subTest(kind=kind):
                self.legacy_copies()
                path = self.root / ".claude/skills/qa/SKILL.md"
                before = (self.root / sync.LEDGER).read_bytes()
                if kind == "content":
                    path.write_text("preserve local work")
                elif kind == "extra":
                    path = path.parent / "private.md"
                    path.write_text("preserve local work")
                else:
                    path = path.parent / "linked.md"
                    path.symlink_to(self.root / ".agent/skills/qa/SKILL.md")
                with self.assertRaises(sync.SyncError):
                    sync.sync(self.root)
                self.assertFalse((self.root / ".agents/skills/qa").is_symlink())
                self.assertEqual((self.root / sync.LEDGER).read_bytes(), before)
                if kind != "symlink":
                    self.assertEqual(path.read_text(), "preserve local work")
                if kind == "content":
                    shutil.copy2(self.root / ".agent/skills/qa/SKILL.md", path)
                else:
                    path.unlink()
                sync.sync(self.root)


    def test_unsupported_symlinks_preserve_old_copies(self):
        self.legacy_copies()
        before = (self.root / sync.LEDGER).read_bytes()
        with patch("os.symlink", side_effect=OSError("not supported")):
            with self.assertRaises(OSError):
                sync.sync(self.root)
        self.assertFalse((self.root / ".agents/skills/qa").is_symlink())
        self.assertTrue((self.root / ".agents/skills/qa/SKILL.md").is_file())
        self.assertEqual((self.root / sync.LEDGER).read_bytes(), before)


    def test_ledger_traversal_cannot_remove_files_outside_workspace(self):
        outer = self.root
        workspace = outer / "workspace"
        workspace.mkdir()
        for name in (".agent", "tools"):
            (outer / name).rename(workspace / name)
        self.root = workspace
        self.legacy_copies()
        victim = outer / "victim.txt"
        victim.write_text("preserve sibling fixture")
        ledger = self.root / sync.LEDGER
        state = json.loads(ledger.read_text())
        name = ".agents/skills/qa/../../../../victim.txt"
        state["files"][name] = sync.digest(victim.read_bytes())
        state["modes"][name] = victim.stat().st_mode & 0o777
        ledger.write_text(json.dumps(state))
        before = ledger.read_bytes()
        with self.assertRaisesRegex(sync.SyncError, "Invalid managed path"):
            sync.sync(self.root)
        self.assertEqual(victim.read_text(), "preserve sibling fixture")
        self.assertEqual(ledger.read_bytes(), before)
        self.assertFalse((self.root / ".agents/skills/qa").is_symlink())
        self.assertFalse((self.root / sync.TRANSACTION).exists())


    def test_ledger_noncanonical_descendant_is_rejected(self):
        self.legacy_copies()
        ledger = self.root / sync.LEDGER
        state = json.loads(ledger.read_text())
        state["files"][".agents/skills/qa/./SKILL.md"] = state["files"][".agents/skills/qa/SKILL.md"]
        ledger.write_text(json.dumps(state))
        with self.assertRaisesRegex(sync.SyncError, "Invalid managed path"):
            sync.sync(self.root)
        self.assertFalse((self.root / ".agents/skills/qa").is_symlink())


    def fail_replace(self, stage, error):
        original = Path.replace
        raised = []
        def replace(path, target):
            target = Path(target)
            matches = ((stage == "backup" and target.parent.name == "backup")
                       or (stage == "link" and path.parent.name == "staged" and path.is_symlink())
                       or (stage == "ledger" and path.parent.name == "staged" and target == (self.root / sync.LEDGER).resolve()))
            if matches and not raised:
                raised.append(True)
                raise error("injected " + stage + " failure")
            return original(path, target)
        return patch.object(Path, "replace", replace), raised


    def assert_copies_preserved(self, ledger):
        self.assertEqual((self.root / sync.LEDGER).read_bytes(), ledger)
        for runtime in (".agents", ".claude"):
            skill = self.root / runtime / "skills/qa"
            self.assertTrue(skill.is_dir())
            self.assertFalse(skill.is_symlink())
            self.assertEqual((skill / "SKILL.md").read_bytes(), (self.root / ".agent/skills/qa/SKILL.md").read_bytes())


    def test_migration_errors_restore_originals_before_retry(self):
        for stage in ("backup", "link", "ledger"):
            with self.subTest(stage=stage):
                self.legacy_copies()
                before = (self.root / sync.LEDGER).read_bytes()
                injection, raised = self.fail_replace(stage, OSError)
                with injection, self.assertRaisesRegex(OSError, "injected"):
                    sync.sync(self.root)
                self.assertTrue(raised)
                self.assert_copies_preserved(before)
                self.assertFalse((self.root / sync.TRANSACTION).exists())
                sync.sync(self.root)
                self.assertEqual(sync.sync(self.root, check=True), [])


    def test_interrupted_migration_recovers_on_next_invocation(self):
        for stage in ("backup", "link", "ledger"):
            with self.subTest(stage=stage):
                self.legacy_copies()
                injection, raised = self.fail_replace(stage, KeyboardInterrupt)
                with injection, self.assertRaises(KeyboardInterrupt):
                    sync.sync(self.root)
                self.assertTrue(raised)
                journal = self.root / sync.TRANSACTION / "journal.json"
                before = journal.read_bytes()
                with self.assertRaisesRegex(sync.SyncError, "Pending runtime transaction"):
                    sync.sync(self.root, check=True)
                self.assertEqual(journal.read_bytes(), before)
                sync.sync(self.root)
                self.assertEqual(sync.sync(self.root, check=True), [])
                self.assertFalse((self.root / sync.TRANSACTION).exists())


    def test_interrupted_staging_recovers_without_mutating_outputs(self):
        self.legacy_copies()
        before = (self.root / sync.LEDGER).read_bytes()
        original = Path.write_bytes
        def interrupt_stage(path, content):
            if path.parent.name == "staged":
                raise KeyboardInterrupt("interrupted staging")
            return original(path, content)
        with patch.object(Path, "write_bytes", interrupt_stage), self.assertRaises(KeyboardInterrupt):
            sync.sync(self.root)
        self.assert_copies_preserved(before)
        sync.sync(self.root)
        self.assertEqual(sync.sync(self.root, check=True), [])


    def test_rollback_itself_can_resume_after_interruption(self):
        self.legacy_copies()
        injection, _ = self.fail_replace("ledger", KeyboardInterrupt)
        with injection, self.assertRaises(KeyboardInterrupt):
            sync.sync(self.root)
        original = Path.replace
        def interrupt_restore(path, target):
            if path.parent.name == "backup" and "skills" in Path(target).parts:
                raise KeyboardInterrupt("interrupted recovery")
            return original(path, target)
        with patch.object(Path, "replace", interrupt_restore), self.assertRaises(KeyboardInterrupt):
            sync.sync(self.root)
        sync.sync(self.root)
        self.assertEqual(sync.sync(self.root, check=True), [])


    def test_cleanup_failure_keeps_committed_installation_usable(self):
        self.legacy_copies()
        with patch.object(sync.shutil, "rmtree", side_effect=OSError("injected cleanup failure")):
            sync.sync(self.root)
        self.assertTrue((self.root / ".agents/skills/qa").is_symlink())
        self.assertFalse((self.root / sync.TRANSACTION).exists())
        self.assertEqual(sync.sync(self.root, check=True), [])

    def initialize_git_ignore_fixture(self):
        shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)

    def assert_recovery_artifacts_ignored(self, paths):
        names = {path.relative_to(self.root).as_posix() for path in paths}
        result = subprocess.run(["git", "-C", str(self.root), "check-ignore", "--stdin"],
                                input="\n".join(sorted(names)) + "\n", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), names)
        subprocess.run(["git", "-C", str(self.root), "add", "--all"], check=True, capture_output=True)
        tracked = subprocess.run(["git", "-C", str(self.root), "ls-files", "-z"],
                                 check=True, capture_output=True, text=True).stdout.split("\0")
        self.assertTrue(names.isdisjoint(tracked))

    def test_pending_and_provisional_recovery_artifacts_are_git_ignored(self):
        self.initialize_git_ignore_fixture()
        self.legacy_copies()
        provisional = self.root / ".agent-runtime-stage-fixture" / "private.json"
        provisional.parent.mkdir()
        provisional.write_text('{"synthetic_private_field":"fixture-only"}')
        injection, _ = self.fail_replace("ledger", KeyboardInterrupt)
        with injection, self.assertRaises(KeyboardInterrupt):
            sync.sync(self.root)
        transaction = self.root / sync.TRANSACTION
        artifacts = [provisional, *(path for path in transaction.rglob("*")
                                    if path.is_file() or path.is_symlink())]
        self.assert_recovery_artifacts_ignored(artifacts)
        journal = transaction / "journal.json"
        before = journal.read_bytes()
        with self.assertRaisesRegex(sync.SyncError, "Pending runtime transaction"):
            sync.sync(self.root, check=True)
        self.assertEqual(journal.read_bytes(), before)
        sync.sync(self.root)
        self.assertEqual(sync.sync(self.root, check=True), [])
        self.assertTrue(provisional.is_file())

    def test_retained_recovery_config_backup_is_git_ignored(self):
        self.initialize_git_ignore_fixture()
        self.legacy_copies()
        settings = self.root / ".claude/settings.json"
        value = json.loads(settings.read_text())
        value["synthetic_private_field"] = "local-only-fixture"
        settings.write_text(json.dumps(value))
        original = settings.read_bytes()
        with patch.object(sync.shutil, "rmtree", side_effect=OSError("retain backup fixture")):
            sync.sync(self.root)
        retained = list(self.root.glob(".agent-runtime-complete-*"))
        self.assertEqual(len(retained), 1)
        journal = json.loads((retained[0] / "journal.json").read_text())
        index = next(index for index, operation in enumerate(journal["operations"])
                     if operation["path"] == ".claude/settings.json")
        backup = retained[0] / "backup" / str(index)
        self.assertEqual(backup.read_bytes(), original)
        artifacts = [path for path in retained[0].rglob("*") if path.is_file() or path.is_symlink()]
        self.assert_recovery_artifacts_ignored(artifacts)
        self.assertEqual(json.loads(settings.read_text()), value)
        self.assertEqual(sync.sync(self.root, check=True), [])
        self.assertTrue(backup.is_file())


    def test_retargeted_generated_symlink_is_not_overwritten(self):
        sync.sync(self.root)
        path = self.root / ".agents/skills/qa"
        path.unlink()
        path.symlink_to(self.root / ".agent/skills/qa-web")
        with self.assertRaisesRegex(sync.SyncError, "Unexpected skill symlink"):
            sync.sync(self.root)


    def test_deleted_canonical_skill_removes_only_managed_links(self):
        sync.sync(self.root)
        shutil.rmtree(self.root / ".agent/skills/qa-web")
        custom = self.root / ".agents/skills/custom/SKILL.md"
        custom.parent.mkdir()
        custom.write_text("custom")
        sync.sync(self.root)
        for runtime in (".agents", ".claude"):
            self.assertFalse((self.root / runtime / "skills/qa-web").is_symlink())
        self.assertEqual(custom.read_text(), "custom")


    def test_symlinked_canonical_source_is_rejected_before_writes(self):
        source = self.root / ".agent/agents"
        actual = self.root / "external-agents"
        source.rename(actual)
        source.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(sync.SyncError, "real workspace directory"):
            sync.sync(self.root)
        self.assertFalse((self.root / sync.LEDGER).exists())


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
        (self.root / ".agent/agents/test-runner.md").unlink()
        custom = self.root / ".codex/agents/custom.toml"
        custom.write_text("custom")
        sync.sync(self.root)
        self.assertFalse((self.root / ".codex/agents/test-runner.toml").exists())
        self.assertFalse((self.root / ".claude/agents/test-runner.md").exists())
        self.assertEqual(custom.read_text(), "custom")


    def test_skill_script_executable_mode_is_preserved(self):
        source = self.root / ".agent/skills/qa/run.sh"
        source.write_text("#!/bin/sh\nprintf verified\n")
        source.chmod(0o755)
        sync.sync(self.root)
        script = self.root / ".agents/skills/qa/run.sh"
        result = subprocess.run([str(script)], capture_output=True, text=True)
        self.assertEqual(result.stdout, "verified")
        self.assertEqual(script.resolve(), source.resolve())
        self.assertEqual(sync.sync(self.root), [])


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
