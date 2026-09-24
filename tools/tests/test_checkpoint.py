"""Exercise the advisory lifecycle in disposable, local Git repositories."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".cursor" / "hooks" / "checkpoint-state.sh"


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.hook = self.root / ".cursor" / "hooks" / HOOK.name
        self.hook.parent.mkdir(parents=True)
        shutil.copy(HOOK, self.hook)
        self.state = self.root / "docs" / "STATE.md"
        self.state.parent.mkdir()
        self.state.write_text("Initial handover.\n")
        (self.root / ".gitignore").write_text(".cursor-temp/\n")
        self.product = self.root / "product.txt"
        self.product.write_text("Initial product.\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Initial fixture")
        self.conversation = "checkpoint-fixture"
        self.key = hashlib.sha256(self.conversation.encode()).hexdigest()[:16]
        self.record = self.root / ".cursor-temp" / "checkpoint" / self.key

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True, timeout=10)

    def invoke(self, phase, *, event=None, raw=None):
        if event is None:
            event = {"conversation_id": self.conversation, "status": "completed", "loop_count": 0}
        result = subprocess.run(["bash", str(self.hook), phase],
                                input=raw if raw is not None else json.dumps(event),
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertIsInstance(output, dict)
        return output

    def test_unchanged_tree_has_no_advisory(self):
        self.assertEqual(self.invoke("start"), {})
        self.assertTrue(self.record.is_file())
        self.assertEqual(self.invoke("stop"), {})

    def test_changed_tree_prompts_only_once_even_without_loop_counter(self):
        self.invoke("start")
        self.product.write_text("Changed product.\n")
        self.assertIn("followup_message", self.invoke("stop"))
        self.assertEqual(self.invoke("stop"), {})
        self.product.write_text("Changed product again.\n")
        self.assertEqual(self.invoke("stop"), {})

    def test_updated_state_suppresses_advisory(self):
        self.invoke("start")
        self.product.write_text("Changed product.\n")
        self.state.write_text("Updated handover.\n")
        self.assertEqual(self.invoke("stop"), {})

    def test_end_removes_conversation_checkpoint(self):
        self.invoke("start")
        self.assertEqual(self.invoke("end"), {})
        self.assertFalse(self.record.exists())
        self.assertEqual(self.invoke("stop"), {})

    def test_existing_untracked_content_edit_is_detected(self):
        draft = self.root / "draft.txt"
        draft.write_text("Draft.\n")
        before = self.git("status", "--porcelain=v1", "--untracked-files=normal").stdout
        self.invoke("start")
        draft.write_text("Draft with a meaningful additional line.\n")
        self.assertEqual(before, self.git("status", "--porcelain=v1", "--untracked-files=normal").stdout)
        self.assertEqual(self.git("diff", "HEAD").stdout, "")
        self.assertIn("followup_message", self.invoke("stop"))

    def test_untracked_file_inside_existing_directory_is_detected(self):
        drafts = self.root / "drafts"
        drafts.mkdir()
        (drafts / "first.txt").write_text("First draft.\n")
        self.invoke("start")
        (drafts / "second.txt").write_text("Second draft.\n")
        self.assertIn("followup_message", self.invoke("stop"))

    def test_start_preserves_original_checkpoint(self):
        self.invoke("start")
        original = self.record.read_text()
        self.product.write_text("Changed product.\n")
        self.invoke("start")
        self.assertEqual(self.record.read_text(), original)
        self.assertIn("followup_message", self.invoke("stop"))

    def test_runtime_loop_count_suppresses_advisory(self):
        self.invoke("start")
        self.product.write_text("Changed product.\n")
        event = {"conversation_id": self.conversation, "status": "completed", "loop_count": 1}
        self.assertEqual(self.invoke("stop", event=event), {})

    def test_aborted_and_error_stops_are_advisory_free(self):
        self.invoke("start")
        self.product.write_text("Changed product.\n")
        for status in ("aborted", "error"):
            with self.subTest(status=status):
                event = {"conversation_id": self.conversation, "status": status, "loop_count": 0}
                self.assertEqual(self.invoke("stop", event=event), {})

    def test_malformed_events_fail_open_without_checkpoint(self):
        for raw in ("{", "[]", "null", "{}", '{"conversation_id": false}',
                    '{"conversation_id": "fixture", "status": "two words"}',
                    '{"conversation_id": "fixture", "loop_count": true}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.invoke("start", raw=raw), {})
        store = self.root / ".cursor-temp" / "checkpoint"
        self.assertFalse(store.exists() and list(store.iterdir()))

    def test_untracked_fifo_is_not_opened_for_content(self):
        os.mkfifo(self.root / "fixture.pipe")
        self.assertEqual(self.invoke("start"), {})
        self.assertEqual(self.invoke("stop"), {})

    def test_checkpoint_directory_is_excluded_without_ignore_rule(self):
        (self.root / ".gitignore").write_text("")
        self.git("add", ".gitignore")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Remove fixture ignore rule")
        self.invoke("start")
        self.assertEqual(self.invoke("stop"), {})

    def test_untracked_symlink_target_is_not_followed(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "notes.txt"
            target.write_text("Initial external fixture.\n")
            (self.root / "notes-link.txt").symlink_to(target)
            self.invoke("start")
            target.write_text("Changed external fixture with more text.\n")
            self.assertEqual(self.invoke("stop"), {})

    def test_missing_git_metadata_fails_open(self):
        shutil.move(self.root / ".git", self.root / "git-metadata-backup")
        self.assertEqual(self.invoke("start"), {})
        self.assertEqual(self.invoke("stop"), {})


if __name__ == "__main__":
    unittest.main()
