from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/workspace/refresh.py"
spec = importlib.util.spec_from_file_location("workspace_refresh", SCRIPT)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "workspace with spaces"
        self.root.mkdir()
        self.origin = self.base / "upstream"
        self.origin.mkdir()
        self.git(self.origin, "init", "--quiet", "--initial-branch=main")
        self.commit(self.origin, "first")
        self.repo = self.root / "client app"
        self.git(self.root, "clone", "--quiet", str(self.origin), str(self.repo))
        self.manifest = self.root / "workspace-manifest.json"
        self.entry = {
            "id": "client", "path": "client app", "canonical_branch": "main",
            "expected_remote": str(self.origin), "allowed_mutability": ["status", "fetch", "fast-forward"],
            "scopes": ["desktop"],
        }
        self.write_manifest()

    def git(self, directory, *args):
        environment = {
            **os.environ, "GIT_AUTHOR_NAME": "QA Fixture", "GIT_AUTHOR_EMAIL": "qa@example.invalid",
            "GIT_COMMITTER_NAME": "QA Fixture", "GIT_COMMITTER_EMAIL": "qa@example.invalid",
            "GIT_TERMINAL_PROMPT": "0",
        }
        result = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, text=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, directory, content):
        (directory / "fixture.txt").write_text(content, encoding="utf-8")
        self.git(directory, "add", "fixture.txt")
        self.git(directory, "commit", "--quiet", "-m", content)
        return self.git(directory, "rev-parse", "HEAD")

    def write_manifest(self, entries=None):
        self.manifest.write_text(json.dumps({"schema_version": 1, "repositories": entries or [self.entry]}), encoding="utf-8")

    def run_refresh(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(self.manifest), *args], capture_output=True, text=True)

    def test_status_does_not_fetch_or_refresh_index(self):
        self.commit(self.origin, "second")
        index = self.repo / ".git/index"
        before = (index.read_bytes(), index.stat().st_mtime_ns)
        head = self.git(self.repo, "rev-parse", "HEAD")
        result = self.run_refresh()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("client app", result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), head)
        self.assertEqual((index.read_bytes(), index.stat().st_mtime_ns), before)
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_update_fast_forwards_path_with_spaces(self):
        expected = self.commit(self.origin, "second")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), expected)
        self.assertIn("fast-forward complete", result.stdout)

    def test_nested_placeholder_is_not_parent_repository(self):
        (self.repo / "placeholder").mkdir()
        self.entry["path"] = "client app/placeholder"
        self.write_manifest()
        result = self.run_refresh()
        self.assertEqual(result.returncode, 0)
        self.assertIn("MISSING", result.stdout)
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_worktree_git_file_is_recognized(self):
        linked = self.root / "linked checkout"
        self.git(self.repo, "worktree", "add", "--quiet", "-b", "review", str(linked))
        self.entry["path"] = "linked checkout"
        self.entry["canonical_branch"] = "review"
        self.write_manifest()
        result = self.run_refresh()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("MISSING", result.stdout)
        self.assertIn("(review)", result.stdout)

    def test_resolved_paths_cannot_escape_workspace(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "escape").symlink_to(outside, target_is_directory=True)
        for value in ("../outside", str(outside), "escape"):
            with self.subTest(path=value):
                self.entry["path"] = value
                self.write_manifest()
                result = self.run_refresh("--update")
                self.assertEqual(result.returncode, 1)
                self.assertIn("inside the workspace", result.stderr)

    def test_remote_mismatch_refuses_fetch(self):
        self.entry["expected_remote"] = str(self.base / "different-upstream")
        self.write_manifest()
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("update refused", result.stdout)
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_failed_fetch_never_merges_stale_tracking_reference(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        advanced = self.commit(self.origin, "second")
        self.git(self.repo, "fetch", "--quiet", "origin")
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), advanced)
        self.origin.rename(self.base / "unavailable-upstream")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("fetch failed; no merge attempted", result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)

    def test_missing_canonical_branch_never_merges_stale_ref_after_other_fetch_succeeds(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        stale = self.commit(self.origin, "second")
        self.git(self.repo, "fetch", "--quiet", "origin")
        self.git(self.origin, "branch", "-m", "main", "other")
        other = self.commit(self.origin, "other branch advances")
        self.git(self.repo, "config", "remote.origin.fetch", "+refs/heads/other:refs/remotes/origin/other")
        self.git(self.repo, "fetch", "--quiet", "origin")
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/other"), other)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), stale)

        result = self.run_refresh("--update")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("fetch failed; no merge attempted", result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), stale)

    def test_canonical_branch_is_fetched_even_when_configured_refspec_excludes_it(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.origin, "branch", "other")
        expected = self.commit(self.origin, "canonical branch advances")
        self.git(self.repo, "config", "remote.origin.fetch", "+refs/heads/other:refs/remotes/origin/other")
        self.git(self.repo, "fetch", "--quiet", "origin")
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), original)

        result = self.run_refresh("--update")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), expected)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), expected)

    def test_fetch_only_preserves_configured_refspec_and_local_branch(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.commit(self.origin, "canonical branch advances")
        self.git(self.origin, "checkout", "--quiet", "-b", "other")
        expected = self.commit(self.origin, "other branch advances")
        self.git(self.repo, "config", "remote.origin.fetch", "+refs/heads/other:refs/remotes/origin/other")
        self.entry["allowed_mutability"] = ["fetch"]
        self.write_manifest()

        result = self.run_refresh("--update")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), original)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/other"), expected)

    def test_dirty_tree_is_preserved(self):
        self.commit(self.origin, "second")
        (self.repo / "fixture.txt").write_text("local edit", encoding="utf-8")
        head = self.git(self.repo, "rev-parse", "HEAD")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("dirty", result.stdout)
        self.assertEqual((self.repo / "fixture.txt").read_text(), "local edit")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), head)
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_branch_switch_during_fetch_preserves_feature_tip_without_merging(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.repo, "branch", "feature")
        self.commit(self.origin, "upstream advance")
        actual_git = refresh.git
        commands = []

        def switch_after_fetch(directory, *arguments):
            commands.append(arguments)
            result = actual_git(directory, *arguments)
            if arguments[0] == "fetch" and result.returncode == 0:
                self.git(self.repo, "checkout", "--quiet", "feature")
            return result

        with patch.object(refresh, "git", side_effect=switch_after_fetch):
            message, failed = refresh.inspect(self.entry, self.root, True)

        self.assertTrue(failed, message)
        self.assertIn("repository changed during fetch; no merge attempted", message)
        self.assertFalse(any(command[0] == "merge" for command in commands))
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "feature")
        self.assertEqual(self.git(self.repo, "rev-parse", "feature"), original)
        self.assertEqual(self.git(self.repo, "rev-parse", "main"), original)

    def test_new_local_work_during_fetch_is_preserved_without_merging(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.commit(self.origin, "upstream advance")
        actual_git = refresh.git
        commands = []
        artifact = self.repo / "local-work.txt"

        def edit_after_fetch(directory, *arguments):
            commands.append(arguments)
            result = actual_git(directory, *arguments)
            if arguments[0] == "fetch" and result.returncode == 0:
                artifact.write_text("another actor's local work\n")
            return result

        with patch.object(refresh, "git", side_effect=edit_after_fetch):
            message, failed = refresh.inspect(self.entry, self.root, True)

        self.assertTrue(failed, message)
        self.assertIn("repository changed during fetch; no merge attempted", message)
        self.assertFalse(any(command[0] == "merge" for command in commands))
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(artifact.read_text(), "another actor's local work\n")

    def test_remote_change_during_fetch_refuses_merge(self):
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.commit(self.origin, "upstream advance")
        actual_git = refresh.git
        changed_remote = str(self.base / "different-origin")

        def change_remote_after_fetch(directory, *arguments):
            result = actual_git(directory, *arguments)
            if arguments[0] == "fetch" and result.returncode == 0:
                self.git(self.repo, "remote", "set-url", "origin", changed_remote)
            return result

        with patch.object(refresh, "git", side_effect=change_remote_after_fetch):
            message, failed = refresh.inspect(self.entry, self.root, True)

        self.assertTrue(failed, message)
        self.assertIn("repository changed during fetch; no merge attempted", message)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(self.git(self.repo, "remote", "get-url", "origin"), changed_remote)

    def test_noncanonical_and_detached_branches_are_preserved(self):
        self.git(self.repo, "checkout", "--quiet", "-b", "feature")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "feature")
        self.git(self.repo, "checkout", "--quiet", "--detach")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "")

    def test_divergence_returns_failure_without_rewriting_local_commit(self):
        original = self.commit(self.repo, "local")
        self.commit(self.origin, "upstream")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("fast-forward failed", result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)

    def test_mutability_is_exact_and_fetch_only_does_not_merge(self):
        self.entry["allowed_mutability"] = ["no-fetch"]
        self.write_manifest()
        self.assertEqual(self.run_refresh("--update").returncode, 1)
        self.entry["allowed_mutability"] = ["fetch"]
        self.write_manifest()
        original = self.git(self.repo, "rev-parse", "HEAD")
        advanced = self.commit(self.origin, "second")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), advanced)

    def test_missing_scope_argument_is_usage_error(self):
        result = self.run_refresh("--scope")
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected one argument", result.stderr)

    def test_scope_filter_leaves_unselected_repository_untouched(self):
        self.commit(self.origin, "second")
        result = self.run_refresh("--scope", "api", "--update")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_invalid_manifest_is_rejected_before_any_update(self):
        for changed in ({"schema_version": True, "repositories": [self.entry]}, {"schema_version": 1, "repositories": [self.entry, self.entry]}):
            with self.subTest(manifest=changed):
                self.manifest.write_text(json.dumps(changed))
                self.assertEqual(self.run_refresh("--update").returncode, 1)
                self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_duplicate_manifest_keys_are_rejected_at_every_level(self):
        self.write_manifest()
        text = self.manifest.read_text()
        for duplicated in (
            text.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
            text.replace('"id": "client"', '"id": "other", "id": "client"'),
        ):
            with self.subTest(manifest=duplicated):
                self.manifest.write_text(duplicated)
                result = self.run_refresh("--update")
                self.assertEqual(result.returncode, 1)
                self.assertIn("duplicate manifest key", result.stderr)
                self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_ownership_is_validated_without_restricting_descriptive_role(self):
        self.entry["role"] = "Product dependency used for desktop compatibility investigations"
        for ownership in ("owned", "dependency"):
            with self.subTest(ownership=ownership):
                self.entry["ownership"] = ownership
                self.write_manifest()
                self.assertEqual(self.run_refresh().returncode, 0)
        for ownership in ("", "customer", None, False, [], {}):
            with self.subTest(ownership=ownership):
                self.entry["ownership"] = ownership
                self.write_manifest()
                result = self.run_refresh("--update")
                self.assertEqual(result.returncode, 1)
                self.assertIn("ownership must be owned or dependency", result.stderr)
                self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())

    def test_invalid_mutability_and_scope_types_are_diagnostic(self):
        for key, value in (("allowed_mutability", "fetch"), ("allowed_mutability", ["fetch", "fetch"]), ("allowed_mutability", ["fast-forward"]), ("allowed_mutability", [False]), ("scopes", "desktop"), ("scopes", [""])):
            with self.subTest(key=key, value=value):
                original = dict(self.entry)
                self.entry[key] = value
                self.write_manifest()
                result = self.run_refresh("--update")
                self.assertEqual(result.returncode, 1)
                self.assertIn("Invalid workspace manifest", result.stderr)
                self.entry = original

    def test_no_fetch_permission_leaves_every_ref_unchanged(self):
        self.entry["allowed_mutability"] = ["status"]
        self.write_manifest()
        original = self.git(self.repo, "rev-parse", "HEAD")
        self.commit(self.origin, "second")
        result = self.run_refresh("--update")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), original)
        self.assertFalse((self.repo / ".git/FETCH_HEAD").exists())


if __name__ == "__main__":
    unittest.main()
