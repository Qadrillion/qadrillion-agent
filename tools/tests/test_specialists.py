"""Deterministic loopback contracts and evidence plumbing, never model evaluation."""
from contextlib import contextmanager
import gc
import importlib.util
import json
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import warnings
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import build_opener, ProxyHandler, Request


ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"tools/specialists/{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


lab, measure, evaluate = (module(name) for name in ("lab", "measure", "evaluate"))


@contextmanager
def running_lab(mode="good", handler=None):
    server = lab.Lab(mode)
    if handler:
        server.RequestHandlerClass = handler
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        if thread.is_alive():
            raise AssertionError("fixture server did not stop")
        with socket.socket() as connection:
            connection.settimeout(0.2)
            if connection.connect_ex(("127.0.0.1", server.server_port)) == 0:
                raise AssertionError("fixture port remains open after cleanup")


def request(server, method, path, *, actor="alice", body=None, key=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    headers = {"Content-Type": "application/json"}
    if actor is not None:
        headers["X-Lab-Actor"] = actor
    if key is not None:
        headers["Idempotency-Key"] = key
    query = Request(server.identity()["url"] + path, data=data, headers=headers, method=method)
    opener = build_opener(ProxyHandler({}), measure.NoRedirect())
    try:
        response = opener.open(query, timeout=1)
    except HTTPError as exc:
        response = exc
    with response:
        return response.status, json.loads(response.read())


def order(server, actor="alice", quantity=2, key="order-key"):
    status, value = request(server, "POST", "/orders", actor=actor, body={"quantity": quantity}, key=key)
    if status != 201:
        raise AssertionError((status, value))
    return value


def complete_job(server, order_id):
    status, job = request(server, "POST", "/jobs", body={"order_id": order_id})
    if status != 202 or job.get("state") != "pending":
        raise AssertionError((status, job))
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        status, state = request(server, "GET", "/jobs/" + job["id"])
        if status != 200:
            raise AssertionError((status, state))
        if state["state"] == "complete":
            return job["id"]
        threading.Event().wait(0.005)
    raise AssertionError("job never reached its contracted terminal state")


class LabContractTests(unittest.TestCase):
    def test_literal_loopback_startup_does_not_depend_on_dns(self):
        with patch("socket.getfqdn", side_effect=RuntimeError("resolver unavailable")):
            with running_lab() as server:
                self.assertEqual(measure.get(server.identity()["url"] + "/__identity", 1),
                                 (200, server.identity()))
                self.assertEqual(server.server_name, "127.0.0.1")

    def test_order_validation_and_idempotency_preserve_persisted_state(self):
        with running_lab() as server:
            for invalid in (0, 101, True, 1.5, "2", None):
                with self.subTest(quantity=invalid):
                    self.assertEqual(request(server, "POST", "/orders", body={"quantity": invalid}, key="invalid")[0], 422)
            self.assertEqual(request(server, "GET", "/orders")[1], [])
            original = order(server)
            self.assertEqual({k: original[k] for k in ("owner", "quantity", "total_cents")},
                             {"owner": "alice", "quantity": 2, "total_cents": 1000})
            self.assertEqual(request(server, "POST", "/orders", body={"quantity": 2}, key="order-key"), (200, original))
            self.assertEqual(request(server, "POST", "/orders", body={"quantity": 3}, key="order-key")[0], 409)
            self.assertEqual(request(server, "GET", "/orders"), (200, [original]))
            independent = order(server, actor="bob")
            self.assertNotEqual(independent["id"], original["id"])
            self.assertEqual(request(server, "GET", "/orders", actor="bob"), (200, [independent]))

    def test_body_key_and_actor_errors_do_not_create_data(self):
        with running_lab() as server:
            self.assertEqual(request(server, "POST", "/orders", actor=None, body={"quantity": 1}, key="key")[0], 401)
            for raw in (b"not-json", b"[]", b"x" * 4097):
                self.assertEqual(request(server, "POST", "/orders", raw=raw, key="key")[0], 422)
            for key in (None, "", "k" * 129):
                self.assertEqual(request(server, "POST", "/orders", body={"quantity": 1}, key=key)[0], 400)
            self.assertEqual(request(server, "POST", "/orders", body={"quantity": 1, "owner": "bob"}, key="key")[0], 422)
            self.assertEqual(request(server, "GET", "/orders"), (200, []))
            self.assertEqual(order(server, quantity=1, key="k" * 128)["total_cents"], 500)
            self.assertEqual(order(server, quantity=100, key="upper")["total_cents"], 50000)

    def test_same_receipt_oracle_detects_seeded_completion_defect(self):
        for mode, expected_receipt_status in (("good", 200), ("api-defect", 404)):
            with self.subTest(mode=mode), running_lab(mode) as server:
                original = order(server)
                ident = complete_job(server, original["id"])
                status, receipt = request(server, "GET", "/receipts/" + ident)
                self.assertEqual(status, expected_receipt_status)
                fulfilled = status == 200 and receipt == {"job_id": ident, "order_id": original["id"], "delivered": True}
                self.assertEqual(fulfilled, mode == "good")
                self.assertEqual(request(server, "GET", "/jobs/" + ident, actor="bob")[0], 404)
                self.assertEqual(request(server, "DELETE", "/jobs/" + ident), (200, {"deleted": ident}))
                self.assertEqual(request(server, "GET", "/receipts/" + ident)[0], 404)

    def test_paired_objects_detect_seeded_read_bypass_and_protect_deletion(self):
        for mode, denied in (("good", True), ("security-defect", False)):
            with self.subTest(mode=mode), running_lab(mode) as server:
                alice, bob = order(server), order(server, actor="bob")
                path = "/orders/" + alice["id"]
                self.assertEqual(request(server, "GET", path), (200, alice))
                status, body = request(server, "GET", path, actor="bob")
                self.assertEqual(status == 404, denied)
                if not denied:
                    self.assertEqual(body, alice)
                self.assertEqual(request(server, "DELETE", path, actor="bob")[0], 404)
                self.assertEqual(request(server, "GET", path), (200, alice))
                self.assertEqual(request(server, "GET", "/orders", actor="bob"), (200, [bob]))
                self.assertEqual(request(server, "DELETE", path), (200, {"deleted": alice["id"]}))
                self.assertEqual(request(server, "GET", path)[0], 404)
                self.assertEqual(request(server, "GET", "/orders/" + bob["id"], actor="bob"), (200, bob))
                self.assertNotEqual(order(server)["id"], alice["id"])

    def test_cli_shutdown_removes_only_its_ready_file_and_closes_port(self):
        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / "ready.json"
            process = subprocess.Popen([sys.executable, str(ROOT / "tools/specialists/lab.py"), "--ready-file", str(ready)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 3
                identity = None
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        identity = json.loads(ready.read_text())
                        break
                    except (FileNotFoundError, json.JSONDecodeError):
                        threading.Event().wait(0.01)
                self.assertIsNotNone(identity, "fixture did not become ready")
                self.assertEqual(measure.get(identity["url"] + "/__identity", 1), (200, identity))
                process.send_signal(signal.SIGINT)
                output, error = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 0, error)
                self.assertEqual(json.loads(output), identity)
                self.assertFalse(ready.exists())
                with socket.socket() as connection:
                    self.assertNotEqual(connection.connect_ex(("127.0.0.1", urlsplit(identity["url"]).port)), 0)
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=3)
            ready.write_text("existing user-owned marker")
            collision = subprocess.run([sys.executable, str(ROOT / "tools/specialists/lab.py"), "--ready-file", str(ready)],
                                       capture_output=True, text=True, timeout=3)
            self.assertNotEqual(collision.returncode, 0)
            self.assertEqual(ready.read_text(), "existing user-owned marker")


class FailureHandler(lab.Handler):
    def dispatch(self, method):
        if self.path == "/work":
            with self.server.lock:
                self.server.work_count += 1
            return self.reply(503, {"error": "synthetic failure"})
        return super().dispatch(method)


class WrongBodyHandler(FailureHandler):
    def reply(self, status, value, content_type="application/json"):
        if self.path == "/work":
            status, value = 200, {"ok": False}
        return super().reply(status, value, content_type)


class SlowHandler(lab.Handler):
    def dispatch(self, method):
        if self.path == "/work":
            time.sleep(0.08)
        return super().dispatch(method)


class MeasureTests(unittest.TestCase):
    def test_real_http_baseline_and_seeded_tail_use_unchanged_threshold(self):
        results = []
        for mode in ("good", "perf-defect"):
            with running_lab(mode) as server:
                result = measure.measure(server.identity(), requests=20, warmup=0, p95_ms=60)
                self.assertEqual(result["identity"], server.identity())
                self.assertEqual(result["summary"]["count"], 20)
                self.assertEqual(result["summary"]["errors"], 0)
                self.assertEqual([sample["sequence"] for sample in result["samples"]], list(range(20)))
                results.append(result)
        self.assertEqual([r["summary"]["verdict"] for r in results], ["pass", "fail"])
        self.assertEqual(results[0]["thresholds"], results[1]["thresholds"])
        self.assertGreaterEqual(results[1]["summary"]["p95_ms"], 70)

    def test_warmup_is_retained_but_excluded_from_measured_count(self):
        with running_lab() as server:
            result = measure.measure(server.identity(), requests=4, warmup=2, p95_ms=1000)
            self.assertEqual(len(result["warmup"]), 2)
            self.assertEqual(result["summary"]["count"], 4)
            self.assertEqual(server.work_count, 6)

    def test_identity_mismatch_blocks_work_before_warmup(self):
        with running_lab() as server:
            for key in ("run_id", "build", "mode", "url"):
                identity = server.identity()
                identity[key] = "different" if key != "url" else identity[key] + "/other"
                with self.subTest(key=key), self.assertRaises(ValueError):
                    measure.measure(identity)
            self.assertEqual(server.work_count, 0)

    def test_external_or_ambiguous_origins_are_rejected(self):
        for url in ("http://localhost:1234", "https://127.0.0.1:1234", "http://127.0.0.2:1234",
                    "http://user@127.0.0.1:1234", "http://127.0.0.1:1234?x=1", "http://127.0.0.1:1234#x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                measure.measure({"url": url})

    def test_limits_reject_invalid_values_before_any_requests(self):
        bad = {"requests": (0, 1001, True, 1.5), "concurrency": (0, 17, False, 1.5),
               "warmup": (-1, 21, True, 0.5), "max_errors": (0, 101, True, 1.5),
               "timeout": (0, 6, float("nan")), "duration": (0, 31, float("inf")),
               "p95_ms": (0, float("nan")), "error_rate": (-1, 2, float("nan"))}
        with running_lab() as server:
            for name, values in bad.items():
                for value in values:
                    with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                        measure.measure(server.identity(), **{name: value})
            self.assertEqual(server.work_count, 0)

    def test_error_budget_bounds_inflight_work_and_retains_http_failures(self):
        with running_lab(handler=FailureHandler) as server:
            result = measure.measure(server.identity(), requests=30, concurrency=3, warmup=0, max_errors=2)
            self.assertEqual(result["summary"]["verdict"], "fail")
            self.assertEqual(result["summary"]["stop_reason"], "error budget")
            self.assertLessEqual(result["summary"]["count"], 4)
            self.assertEqual(result["summary"]["errors"], result["summary"]["count"])
            self.assertIsNone(result["summary"]["success_p95_ms"])
            self.assertTrue(all(s["status"] == 503 and s["diagnostic"] == "HTTPError" for s in result["samples"]))

    def test_http_error_response_resources_are_closed(self):
        with running_lab(handler=FailureHandler) as server, warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ResourceWarning)
            measure.measure(server.identity(), requests=1, warmup=0)
            gc.collect()
            leaked = [str(w.message) for w in caught if issubclass(w.category, ResourceWarning)]
            self.assertEqual(leaked, [])

    def test_http_200_wrong_content_counts_as_failure(self):
        with running_lab(handler=WrongBodyHandler) as server:
            result = measure.measure(server.identity(), requests=2, warmup=0, max_errors=10)
            self.assertEqual(result["summary"]["errors"], 2)
            self.assertEqual(result["summary"]["verdict"], "fail")
            self.assertTrue(all(s["diagnostic"] == "business response mismatch" for s in result["samples"]))
            with self.assertRaisesRegex(ValueError, "warmup business check failed"):
                measure.measure(server.identity(), requests=2, warmup=1)

    def test_duration_and_request_timeout_fail_without_filling_workload(self):
        with running_lab(handler=SlowHandler) as server:
            result = measure.measure(server.identity(), requests=100, warmup=0, duration=0.05, timeout=0.01)
            self.assertEqual(result["summary"]["verdict"], "fail")
            self.assertLess(result["summary"]["count"], 100)
            self.assertTrue(result["summary"]["stop_reason"] in ("duration ceiling", "error budget"))
            self.assertTrue(all(not s["ok"] and s["status"] is None for s in result["samples"]))

    def test_cli_retains_threshold_failure_and_will_not_overwrite_artifact(self):
        with tempfile.TemporaryDirectory() as directory, running_lab() as server:
            identity, output = Path(directory) / "identity.json", Path(directory) / "result.json"
            identity.write_text(json.dumps(server.identity()))
            command = [sys.executable, str(ROOT / "tools/specialists/measure.py"), "--identity", str(identity),
                       "--out", str(output), "--requests", "2", "--warmup", "0", "--p95-ms", "0.0001"]
            first = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(first.returncode, 1, first.stderr)
            retained = output.read_bytes()
            self.assertEqual(json.loads(retained)["summary"]["verdict"], "fail")
            collision = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertNotEqual(collision.returncode, 0)
            self.assertEqual(output.read_bytes(), retained)

    def test_cli_reserves_output_before_any_target_http_requests(self):
        received = []

        class CountingHandler(lab.Handler):
            def dispatch(self, method):
                received.append((method, self.path))
                return super().dispatch(method)

        with tempfile.TemporaryDirectory() as directory, running_lab(handler=CountingHandler) as server:
            root = Path(directory)
            identity = root / "identity.json"
            identity.write_text(json.dumps(server.identity()))
            existing = root / "existing.json"
            existing.write_bytes(b"retained original evidence\n")
            for output in (existing, root / "missing" / "result.json", existing / "result.json"):
                with self.subTest(output=output):
                    run = subprocess.run(
                        [sys.executable, str(ROOT / "tools/specialists/measure.py"),
                         "--identity", str(identity), "--out", str(output),
                         "--requests", "1", "--warmup", "0"],
                        capture_output=True, text=True, timeout=5)
                    self.assertEqual(received, [], "output reservation failure must not contact the target")
                    self.assertEqual(run.returncode, 2, run.stderr)
                    self.assertIn("Measurement blocked:", run.stderr)
                    self.assertNotIn("Traceback", run.stderr)
                    self.assertEqual(existing.read_bytes(), b"retained original evidence\n")

    def test_cli_retains_setup_failure_in_reserved_output(self):
        with tempfile.TemporaryDirectory() as directory, running_lab() as server:
            root = Path(directory)
            identity = root / "identity.json"
            invalid = server.identity()
            invalid["run_id"] = "different"
            for name, content, diagnostic in (
                    ("invalid-json", "{", "JSONDecodeError"),
                    ("array", "[]", "ValueError"),
                    ("null", "null", "ValueError"),
                    ("numeric-url", '{"url":123}', "ValueError"),
                    ("null-url", '{"url":null}', "ValueError"),
                    ("identity-mismatch", json.dumps(invalid), "ValueError")):
                with self.subTest(name=name):
                    identity.write_text(content)
                    output = root / f"{name}.json"
                    run = subprocess.run(
                        [sys.executable, str(ROOT / "tools/specialists/measure.py"),
                         "--identity", str(identity), "--out", str(output)],
                        capture_output=True, text=True, timeout=5)
                    self.assertEqual(run.returncode, 2, run.stderr)
                    self.assertIn("Measurement blocked:", run.stderr)
                    self.assertNotIn("Traceback", run.stderr)
                    result = json.loads(output.read_text())
                    self.assertEqual(result["summary"]["verdict"], "blocked")
                    self.assertEqual(result["error"]["type"], diagnostic)
                    self.assertTrue(result["error"]["message"])
                    self.assertEqual(result["samples"], [])
                    self.assertEqual(server.work_count, 0)


class EvaluationPlumbingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        for name in evaluate.FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}" if path.suffix == ".json" else "Synthetic instruction input\n")
        for name in evaluate.TREES:
            directory = self.source / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "fixture.txt").write_text("permitted synthetic dependency")
        for name in evaluate.SKILLS:
            path = self.source / f".cursor/skills/{name}/SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(f"Synthetic {name} instruction\n")
        contract = self.source / "tools/specialists/CONTRACT.md"
        contract.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "tools/specialists/CONTRACT.md", contract)
        self.out = self.root / "run"

    def review(self, verdict="Fail"):
        return {"runtime": "synthetic-format-test", "model": "no-model-executed",
                "runtime_run_id": "format-test", "reviewer": "unit-test", "verdict": verdict,
                "observations": ["Synthetic format test; not a model run."],
                "findings": ["Synthetic failure preservation check."], "actual_tokens": None}

    def test_catalog_has_distinct_requested_route_cases(self):
        self.assertEqual(set(evaluate.scenarios()), {"api", "web", "mobile", "mixed", "security", "performance", "quick", "ordinary", "missing"})
        self.assertEqual(evaluate.scenarios()["quick"]["expect"]["specialties"], [])
        self.assertEqual(evaluate.scenarios()["ordinary"]["expect"]["specialties"], ["qa-web"])

    def test_materialization_excludes_history_and_answers_and_pins_copy(self):
        secret = self.source / "docs/sessions/history.md"
        secret.parent.mkdir(parents=True)
        secret.write_text("prior run answer key")
        (self.source / "scenarios.json").write_text("unpermitted source answer key")
        run = evaluate.materialize(self.source, "api", self.out, revision="known-source-commit")
        worker = self.out / "workspace"
        self.assertFalse((worker / "docs/sessions").exists())
        self.assertFalse((worker / "scenarios.json").exists())
        self.assertFalse((worker / "evaluation.json").exists())
        self.assertFalse((worker / "tools/specialists").exists())
        self.assertEqual((worker / "TASK.md").read_text().strip(), evaluate.scenarios()["api"]["task"])
        self.assertEqual(run["status"], "Not-run")
        self.assertIsNone(run["actual_tokens"])
        self.assertEqual(run["source_revision"], "known-source-commit")
        self.assertTrue(run["expect"])
        for name, sha in run["manifest"].items():
            self.assertEqual(evaluate.digest(worker / name), sha)
        original = (worker / "AGENTS.md").read_bytes()
        (self.source / "AGENTS.md").write_text("later source mutation")
        self.assertEqual((worker / "AGENTS.md").read_bytes(), original)

    def test_missing_inputs_and_duplicate_context_fail_before_destination_creation(self):
        missing = self.source / ".cursor/skills/qa-web/SKILL.md"
        saved = missing.read_bytes()
        missing.unlink()
        with self.assertRaisesRegex(ValueError, "required file missing"):
            evaluate.materialize(self.source, "web", self.out)
        self.assertFalse(self.out.exists())
        missing.write_bytes(saved)
        with self.assertRaisesRegex(ValueError, "duplicate fixture"):
            evaluate.materialize(self.source, "api", self.out, contexts=[ROOT / "tools/specialists/CONTRACT.md"])
        self.assertFalse(self.out.exists())

    def test_existing_run_and_symlinked_inputs_are_not_overwritten(self):
        evaluate.materialize(self.source, "quick", self.out)
        original = (self.out / "evaluation.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "must be new"):
            evaluate.materialize(self.source, "quick", self.out)
        self.assertEqual((self.out / "evaluation.json").read_bytes(), original)
        link = self.source / ".cursor/rules/linked.md"
        link.symlink_to(self.source / "AGENTS.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            evaluate.materialize(self.source, "quick", self.root / "another-run")

    def test_record_retains_failed_attempt_and_raw_jsonl_without_executing_commands(self):
        evaluate.materialize(self.source, "api", self.out)
        transcript = self.root / "runtime.jsonl"
        marker = self.root / "must-not-execute"
        raw = json.dumps({"type": "tool", "command": f"touch {marker}"}) + "\n"
        transcript.write_text(raw)
        first = evaluate.record(self.out, self.review(), transcript=transcript)
        first_bytes = first.read_bytes()
        second_review = self.review("Pass")
        second_review["findings"] = []
        second = evaluate.record(self.out, second_review, transcript=transcript)
        self.assertNotEqual(first.parent, second.parent)
        self.assertEqual(first.read_bytes(), first_bytes)
        self.assertEqual(json.loads(first_bytes)["review"]["verdict"], "Fail")
        self.assertEqual((first.parent / "transcript.jsonl").read_text(), raw)
        self.assertFalse(marker.exists())
        self.assertIsNone(evaluate.read_json(second)["review"]["actual_tokens"])

    def test_executed_record_requires_real_evidence_format_and_explicit_token_source(self):
        evaluate.materialize(self.source, "api", self.out)
        with self.assertRaisesRegex(ValueError, "requires the actual runtime transcript"):
            evaluate.record(self.out, self.review("Pass"))
        transcript = self.root / "runtime.jsonl"
        for text in ("", "[]\n", "not-json\n"):
            transcript.write_text(text)
            with self.assertRaises(ValueError):
                evaluate.record(self.out, self.review(), transcript=transcript)
        review = self.review()
        review["actual_tokens"] = 123
        with self.assertRaisesRegex(ValueError, "requires a runtime evidence source"):
            evaluate.validate_review(review)
        review["token_source"] = "turn.completed.usage"
        evaluate.validate_review(review)
        for tokens in (True, 1.5, -1):
            review["actual_tokens"] = tokens
            with self.assertRaises(ValueError):
                evaluate.validate_review(review)


if __name__ == "__main__":
    unittest.main()
