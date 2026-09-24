"""Guard payload tests: commands are stdin data and are never executed."""
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("hook_test_adapter", ROOT / "tools/agents/adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qa guard fixtures ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.hooks = self.root / ".cursor/hooks"
        shutil.copytree(ROOT / ".cursor/hooks", self.hooks)
        shutil.copyfile(ROOT / ".cursor/hooks.json", self.root / ".cursor/hooks.json")
        self.config = (self.hooks / "guard.conf").read_text(encoding="utf-8")

    def configure(self, **values):
        overrides = "".join(f"\n{key}={shlex.quote(value)}\n" for key, value in values.items())
        (self.hooks / "guard.conf").write_text(self.config + overrides, encoding="utf-8")

    def call(self, guard, event=None, raw=None):
        result = subprocess.run(["bash", str(self.hooks / f"guard-{guard}.sh")],
                                input=json.dumps(event) if raw is None else raw,
                                cwd=self.root, capture_output=True, text=True,
                                encoding="utf-8", timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        verdict = json.loads(result.stdout)
        self.assertIn(verdict["permission"], {"allow", "ask", "deny"})
        return verdict

    def shell(self, command):
        return self.call("shell", {"command": command})["permission"]

    def mcp(self, tool, server="fixture"):
        return self.call("mcp", {"server_name": server, "tool_name": tool,
                                 "tool_input": {}})["permission"]

    def read(self, path):
        return self.call("read", {"file_path": path})["permission"]

    def test_malformed_json_and_required_types_fail_closed(self):
        for guard in ("shell", "mcp", "read"):
            for raw in ("{", "[]", "null", "false", "{}"):
                with self.subTest(guard=guard, raw=raw):
                    self.assertEqual(self.call(guard, raw=raw)["permission"], "deny")
        for value in (None, 1, True, [], {}, "", "  ", "bad\0value"):
            for guard, field in (("shell", "command"), ("read", "file_path")):
                with self.subTest(guard=guard, value=value):
                    self.assertEqual(self.call(guard, {field: value})["permission"], "deny")

    def test_mcp_identifiers_payload_and_aliases_are_validated(self):
        base = {"server_name": "fixture", "tool_name": "get_item", "tool_input": {}}
        for field in base:
            for value in (None, 5, [], "" if field != "tool_input" else "payload"):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.call("mcp", {**base, field: value})["permission"], "deny")
        for extra in ({"server": "other"}, {"tool": "other"}, {"tool_name": "get\nitem"}):
            self.assertEqual(self.call("mcp", {**base, **extra})["permission"], "deny")
        self.assertEqual(self.call("mcp", {**base, "server": "fixture"})["permission"], "allow")

    def test_targeted_profile_does_not_repeat_routine_approval(self):
        for command in ("pip install requests", "npm install @playwright/test", "pytest tests/",
                        "python3 tools/flags.py update --confirm-write", "gh pr create --body-file draft.md",
                        "acli jira workitem comment create --key DEMO-1 --body-file qa.md",
                        "curl --request PATCH https://example.invalid/fixture -d '{}'",
                        "python3 tools/tickets/index.py"):
            with self.subTest(command=command):
                self.assertEqual(self.shell(command), "allow")
        for tool in ("create_issue", "updatePage", "remove_label", "delete_fixture", "send_message",
                     "evaluate_script", "http_request", "performGesture"):
            with self.subTest(tool=tool):
                self.assertEqual(self.mcp(tool), "allow")

    def test_strict_profile_preserves_optional_broad_gates(self):
        self.configure(GUARD_PROFILE="strict")
        for command in ("pip install requests", "twg jira create", "gh issue comment 5 --body-file draft.md",
                        "curl -X POST https://example.invalid -d '{}'", "python3 flags.py --confirm-write"):
            with self.subTest(command=command):
                self.assertEqual(self.shell(command), "ask")
        for tool in ("create_issue", "updatePage", "send_message", "evaluate_script", "performGesture"):
            self.assertEqual(self.mcp(tool), "ask")
        for tool in ("delete_issue", "removeCollection"):
            self.assertEqual(self.mcp(tool), "deny")
        for tool in ("getCollection", "jira_get_transitions", "confluence_get_labels"):
            self.assertEqual(self.mcp(tool, server="postman"), "allow")

    def test_high_impact_shell_guards_remain_in_both_profiles(self):
        for profile in ("targeted", "strict"):
            self.configure(GUARD_PROFILE=profile)
            for command in ("git push --force origin main", "git -C source reset --hard",
                            "rm -rf ~/Documents", "pytest tests/ --env production",
                            "TEST_ENVIRONMENT=prod pytest tests/", "cat .env", "security find-generic-password -w"):
                with self.subTest(profile=profile, command=command):
                    self.assertEqual(self.shell(command), "deny")
            for command in ("gh pr merge 42 --squash", "npm publish", "git branch -D old", "DROP DATABASE fixture;"):
                self.assertEqual(self.shell(command), "ask")

    def test_high_impact_mcp_patterns_are_targeted(self):
        for tool in ("force_push", "git_forcePush", "dropDatabase", "delete_repository"):
            self.assertEqual(self.mcp(tool), "deny")
        for tool in ("deploy_production", "mergePullRequest", "publish_release"):
            self.assertEqual(self.mcp(tool), "ask")

    def test_policy_configuration_fails_closed_and_custom_gates_apply(self):
        for guard, event in (("shell", {"command": "echo fixture"}),
                             ("mcp", {"server": "fixture", "tool": "get", "tool_input": {}})):
            self.configure(GUARD_PROFILE="typo")
            self.assertEqual(self.call(guard, event)["permission"], "deny")
        for key, guard, event in (("EXTRA_DENY", "shell", {"command": "echo fixture"}),
                                  ("PROTECTED_PATHS", "read", {"file_path": "docs/note.md"}),
                                  ("MCP_ASK_TOOLS", "mcp", {"server": "fixture", "tool": "get", "tool_input": {}})):
            self.configure(**{key: "["})
            self.assertEqual(self.call(guard, event)["permission"], "deny")
        self.configure(EXTRA_ASK="fixture-operation", MCP_ASK_TOOLS="custom_write", MCP_DENY_SERVERS="forbidden")
        self.assertEqual(self.shell("fixture-operation"), "ask")
        self.assertEqual(self.mcp("custom_write"), "ask")
        self.assertEqual(self.mcp("get", server="forbidden"), "deny")

    def test_paths_json_escaping_and_alias_conflicts(self):
        for path in ('docs/quotes"and\\slashes.md', "docs/new\nline.md", "docs/café.md"):
            self.assertEqual(self.read(path), "allow")
        path = 'secrets/quotes"and\nnewline.env'
        verdict = self.call("read", {"file_path": path})
        self.assertEqual(verdict["permission"], "deny")
        self.assertIn(path, verdict["user_message"])
        self.assertEqual(self.call("read", {"file_path": "one", "path": "two"})["permission"], "deny")
        self.assertEqual(self.call("read", {"file_path": "one", "path": "one"})["permission"], "allow")

    def test_credential_patterns_and_terminal_template_exemptions(self):
        for path in (".env", ".env.local", ".aws/config", ".ssh/config", ".netrc", ".npmrc", ".pypirc",
                     ".cursor/mcp.json", ".codex/auth.json", "server.pem", "id_rsa.example",
                     "config.sample.env", "automation/accounts_pool.json", "secrets.env/ordinary.md"):
            with self.subTest(path=path):
                self.assertEqual(self.read(path), "deny")
        for path in (".env.example", "config.env.template", "accounts_pool.example.json", "docs/credentials-guide.md"):
            self.assertEqual(self.read(path), "allow")

    def test_symlinks_and_protected_paths_precede_template_exemptions(self):
        (self.root / ".env").write_text("fixture only", encoding="utf-8")
        (self.root / "safe.example").symlink_to(self.root / ".env")
        self.assertEqual(self.read("safe.example"), "deny")
        self.configure(PROTECTED_PATHS="(^|/)private[[:digit:]]+(/|$)")
        self.assertEqual(self.read("private42/.env.example"), "deny")
        self.assertEqual(self.read("private-other/.env.example"), "allow")
        (self.root / "alias").symlink_to(self.root / "private42", target_is_directory=True)
        self.assertEqual(self.read("alias/note.md"), "deny")

    def test_negative_rg_globs_and_template_copy_remain_usable(self):
        for command in ("rg --files --hidden -g '!.env' -g '!mcp.json'", "cp .env.example .env", "cat .env.example"):
            self.assertEqual(self.shell(command), "allow")
        for command in ("rg --files .env", "cat .env.example .env", "rg --files -g '!.env' | cat .env"):
            self.assertEqual(self.shell(command), "deny")
        self.assertEqual(self.shell("cp .env /tmp/fixture-backup.env"), "ask")

    def test_document_edit_content_is_not_executed_or_scanned_as_a_command(self):
        patch_text = ("*** Begin Patch\n*** Add File: docs/guard-examples.md\n"
                      "+Examples only: git push --force; cat .env; DROP DATABASE sample;\n*** End Patch")
        for runtime in ("claude", "codex"):
            for tool, value in (("apply_patch", {"command": patch_text}),
                                ("Write", {"file_path": "docs/guide.md", "content": patch_text})):
                event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": value,
                         "cwd": str(self.root)}
                self.assertEqual(adapter.project(event, self.root, runtime), {})
        self.assertFalse((self.root / "docs/guard-examples.md").exists())

    def test_native_relative_paths_use_event_cwd_without_losing_lexical_checks(self):
        child = self.root / "child"
        child.mkdir()
        (self.root / ".env").write_text("fixture only", encoding="utf-8")
        (self.root / "safe.txt").symlink_to(self.root / ".env")
        (child / "safe.txt").write_text("ordinary fixture", encoding="utf-8")
        (child / ".env").symlink_to(child / "safe.txt")
        for runtime in ("claude", "codex"):
            for tool in ("Read", "Write"):
                event = {"hook_event_name": "PreToolUse", "tool_name": tool,
                         "cwd": str(child), "tool_input": {"file_path": "safe.txt"}}
                with self.subTest(runtime=runtime, tool=tool):
                    self.assertEqual(adapter.project(event, self.root, runtime), {})
                    event["tool_input"]["file_path"] = str(child / "safe.txt")
                    self.assertEqual(adapter.project(event, self.root, runtime), {})
                    event["tool_input"]["file_path"] = ".env"
                    decision = adapter.project(event, self.root, runtime)
                    self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_native_permissions_are_preserved_and_prefix_does_not_authorize(self):
        for runtime in ("claude", "codex"):
            event = {"hook_event_name": "PreToolUse", "tool_name": "mcp__fixture__update_page",
                     "tool_input": {}, "cwd": str(self.root)}
            self.assertEqual(adapter.project(event, self.root, runtime), {})
            event.update(tool_name="Bash", tool_input={"command": "APPROVED=1 git push --force"})
            self.assertEqual(adapter.project(event, self.root, runtime)["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
