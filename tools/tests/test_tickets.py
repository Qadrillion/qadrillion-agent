from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/tickets"))
import validate

spec = importlib.util.spec_from_file_location("ticket_index", ROOT / "tools/tickets/index.py")
index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(index)


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / "LOCAL-1.md"
        self.data = {
            "id": "LOCAL-1", "title": "Check a portable product", "scope": "desktop",
            "status": "analyzed", "verdict": None, "build": None,
            "environment": "customer-sandbox", "tracker": None, "design": None,
            "source_refs": [], "started": "2026-09-24", "updated": "2026-09-24",
            "next_action": "Execute the regression scenarios", "blockers": [],
        }

    def document(self, body=""):
        lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in self.data.items()]
        return "---\n" + "\n".join(lines) + "\n---\n" + body

    def write(self, body=""):
        self.path.write_text(self.document(body), encoding="utf-8")
        return validate.check(self.path)

    def test_existing_v1_example_remains_valid(self):
        self.assertEqual(validate.check(ROOT / "tickets/PROJ-101.md"), [])

    def test_tracker_free_text_environment_and_new_scopes(self):
        for scope in ("desktop", "data", "device", "other"):
            with self.subTest(scope=scope):
                self.data["scope"] = scope
                self.assertEqual(self.write(), [])
        self.data.update(env_role="test", owner="qa-engineer", branch="feature/desktop")
        self.assertEqual(self.write(), [])

    def test_empty_or_type_invalid_fields_fail(self):
        for key, value in (("environment", ""), ("environment", 42), ("env_role", "live"), ("owner", []), ("branch", ""), ("title", False), ("source_refs", "[]"), ("blockers", "reason"), ("source_refs", [1]), ("blockers", [""]), ("tracker", "https://")):
            with self.subTest(key=key, value=value):
                original = dict(self.data)
                self.data[key] = value
                self.assertTrue(self.write())
                self.data = original

    def test_duplicate_keys_and_malformed_delimiters_fail(self):
        for text in (
            self.document().replace("title:", 'id: "LOCAL-1"\ntitle:'),
            self.document().replace("\n---\n", "\n---not-a-delimiter\n"),
            self.document().replace('title: "Check a portable product"', 'title "missing colon"'),
        ):
            with self.subTest(text=text):
                self.path.write_text(text)
                self.assertTrue(validate.check(self.path))

    def test_yaml_subset_block_and_inline_lists_and_quotes(self):
        text = self.document().replace('source_refs: []', "source_refs:\n  - src/main.py:41\n  - 'src/customer''s.py:12'")
        text = text.replace('blockers: []', 'blockers: ["waiting, with comma", waiting-for-build] # comment')
        parsed, _ = validate.parse_ticket(text)
        self.assertEqual(parsed["source_refs"], ["src/main.py:41", "src/customer's.py:12"])
        self.assertEqual(parsed["blockers"], ["waiting, with comma", "waiting-for-build"])
        self.assertEqual(validate.validate_data(self.path, parsed, ""), [])

    def test_unsupported_yaml_is_rejected(self):
        for text in ("title: |\n  multi-line", "title: &alias value", "title: !custom value", "title: {nested: mapping}", "title: [nested, [list]]", 'title: "unterminated', "title: [unterminated", "title: [a,,b]", "title: value\n  continuation", "source_refs:\n  - first\n    - nested", "source_refs:\n  - - nested"):
            with self.subTest(text=text):
                with self.assertRaises(validate.FrontmatterError):
                    validate.parse_ticket("---\n" + text + "\n---\n")

    def test_crlf_and_comments_are_supported(self):
        text = self.document().replace("---\n", "---\n# useful context\n", 1).replace('"desktop"', 'desktop # scope')
        self.path.write_bytes(text.replace("\n", "\r\n").encode())
        self.assertEqual(validate.check(self.path), [])

    def test_date_order_and_iso_format(self):
        for updated in ("2026-09-23", "2026-02-30", "20260924", 20260924):
            with self.subTest(updated=updated):
                self.data["updated"] = updated
                self.assertTrue(self.write())

    def test_blocked_requires_reason_and_done_requires_verdict(self):
        self.data["status"] = "blocked"
        self.assertTrue(self.write())
        self.data["blockers"] = ["Await a staging deployment"]
        self.assertEqual(self.write(), [])
        self.data["status"] = "done"
        self.assertTrue(self.write())

    def test_pass_requires_execution_evidence_not_placeholder_prose(self):
        self.data.update(status="done", verdict="pass")
        for body in ("", "## Execution & results\n\nReal output. Command, then result.\n", "## Execution & results\n```\nTODO\nplaceholder\n```\n", "## Analysis\n```\n$ pytest\n2 passed\n```\n"):
            with self.subTest(body=body):
                self.assertTrue(self.write(body))
        body = "## Execution & results\n\n```text\n$ python3 -m unittest\nRan 2 tests: OK\n```\n\n## Handoff\nDone.\n"
        self.assertEqual(self.write(body), [])

    def test_pass_accepts_existing_nonempty_local_evidence(self):
        self.data.update(status="done", verdict="pass", evidence=["run.log"])
        self.assertTrue(self.write())
        (self.directory / "run.log").write_text("")
        self.assertTrue(self.write())
        (self.directory / "run.log").write_text("Ran 2 tests: OK\n")
        self.assertEqual(self.write(), [])

    def test_index_escapes_pipes_newlines_and_html(self):
        self.data["title"] = "A | B\n<script>bad</script>"
        self.data["next_action"] = "Execute scenario | two\nthen report"
        self.assertEqual(self.write(), [])
        rendered = index.render(self.directory)
        self.assertIn("A \\| B<br>&lt;script&gt;bad&lt;/script&gt;", rendered)
        self.assertIn("Execute scenario \\| two<br>then report", rendered)

    def test_index_sorts_by_date_not_table_delimiters(self):
        self.data["title"] = "A | B"
        self.write()
        self.data.update(id="LOCAL-2", updated="2026-09-25")
        (self.directory / "LOCAL-2.md").write_text(self.document())
        rendered = index.render(self.directory)
        self.assertLess(rendered.index("[LOCAL-2]"), rendered.index("[LOCAL-1]"))

    def test_invalid_ticket_stops_index_without_overwriting_existing_file(self):
        self.path.write_text("not frontmatter\n")
        destination = self.directory / "INDEX.md"
        destination.write_text("keep existing index\n")
        with self.assertRaises(ValueError):
            index.render(self.directory)
        real_render = index.render
        with patch.object(index, "INDEX", destination), patch.object(index, "render", side_effect=lambda: real_render(self.directory)):
            self.assertEqual(index.main([]), 1)
        self.assertEqual(destination.read_text(), "keep existing index\n")

    def test_missing_file_is_diagnostic_not_traceback(self):
        self.assertTrue(validate.check(self.directory / "missing.md"))


if __name__ == "__main__":
    unittest.main()
