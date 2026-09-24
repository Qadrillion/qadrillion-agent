#!/usr/bin/env python3
"""Disposable loopback QA target. Run --help; never use this as an application server."""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from socketserver import TCPServer
import threading
import time
from urllib.parse import urlsplit
import uuid

MODES = ("good", "api-defect", "web-defect", "security-defect", "perf-defect")
PAGE = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Parcel lab</title><main><h1>Parcel orders</h1>
<form id="order"><label for="quantity">Quantity</label>
<input id="quantity" name="quantity" type="number" min="1" max="100" value="1" required>
<button>Place order</button></form><p role="status" aria-live="polite">Ready</p>
<section aria-label="Receipt" hidden><h2>Receipt</h2><p id="receipt"></p></section>
</main><script>
const form = document.querySelector('form');
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  const status = document.querySelector('[role=status]');
  button.disabled = true; status.textContent = 'Submitting';
  try {
    const response = await fetch('/orders', {method:'POST', headers:{
      'Content-Type':'application/json', 'X-Lab-Actor':'alice',
      'Idempotency-Key':crypto.randomUUID()}, body:JSON.stringify({quantity:Number(form.quantity.value)})});
    const order = await response.json();
    if (!response.ok) throw new Error(order.error);
    document.querySelector('#receipt').textContent = `${order.quantity} parcels — $${(TOTAL / 100).toFixed(2)}`;
    document.querySelector('section').hidden = false;
    status.textContent = 'Order saved';
  } catch (error) { status.textContent = 'Order failed: ' + error.message; }
  finally { button.disabled = false; }
});
</script></html>"""


class Lab(ThreadingHTTPServer):
    daemon_threads = True

    def server_bind(self):
        # HTTPServer resolves a host name here; this loopback-only fixture has
        # no DNS identity and must start when the host resolver is unavailable.
        TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]

    def __init__(self, mode="good", run_id=None):
        super().__init__(("127.0.0.1", 0), Handler)
        self.mode = mode
        self.run_id = run_id or str(uuid.uuid4())
        self.build = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.orders = {}
        self.keys = {}
        self.jobs = {}
        self.lock = threading.RLock()
        self.work_count = 0

    def identity(self):
        return {"fixture": "qadrillion-specialist-lab", "role": "test", "run_id": self.run_id,
                "build": self.build,
                "mode": self.mode, "url": f"http://127.0.0.1:{self.server_port}"}


class Handler(BaseHTTPRequestHandler):
    server: Lab

    def log_message(self, *_):
        pass

    def reply(self, status, value, content_type="application/json"):
        payload = json.dumps(value).encode() if content_type == "application/json" else value.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_DELETE(self):
        self.dispatch("DELETE")

    def dispatch(self, method):
        path = urlsplit(self.path).path
        if method == "GET" and path == "/__identity":
            return self.reply(200, self.server.identity())
        if method == "GET" and path == "/":
            total = "order.quantity * 400" if self.server.mode == "web-defect" else "order.total_cents"
            return self.reply(200, PAGE.replace("TOTAL", total), "text/html; charset=utf-8")
        if method == "GET" and path == "/work":
            with self.server.lock:
                self.server.work_count += 1
                slow = self.server.mode == "perf-defect" and self.server.work_count % 5 == 0
            time.sleep(0.08 if slow else 0.002)
            return self.reply(200, {"ok": True})
        actor = self.headers.get("X-Lab-Actor")
        if actor not in {"alice", "bob"}:
            return self.reply(401, {"error": "actor required"})
        data = None
        if method == "POST":
            invalid_status = 422 if path == "/orders" else 400
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    return self.reply(invalid_status, {"error": "invalid body length"})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("object required")
            except (ValueError, UnicodeError):
                return self.reply(invalid_status, {"error": "JSON object required"})
        with self.server.lock:
            if path == "/orders" and method == "GET":
                return self.reply(200, [o for o in self.server.orders.values() if o["owner"] == actor])
            if path == "/orders" and method == "POST":
                quantity = data.get("quantity")
                if set(data) != {"quantity"} or type(quantity) is not int or not 1 <= quantity <= 100:
                    return self.reply(422, {"error": "quantity must be an integer from 1 to 100"})
                key = self.headers.get("Idempotency-Key")
                if not key or len(key) > 128:
                    return self.reply(400, {"error": "Idempotency-Key required (1..128 chars)"})
                previous = self.server.keys.get((actor, key))
                if previous:
                    if previous["quantity"] != quantity:
                        return self.reply(409, {"error": "idempotency key reused with different input"})
                    return self.reply(200, previous)
                order = {"id": str(uuid.uuid4()), "owner": actor, "quantity": quantity,
                         "total_cents": quantity * 500}
                self.server.orders[order["id"]] = order
                self.server.keys[(actor, key)] = order
                return self.reply(201, order)
            if path.startswith("/orders/"):
                ident = path.removeprefix("/orders/")
                order = self.server.orders.get(ident)
                if not order or (order["owner"] != actor and
                                 not (method == "GET" and self.server.mode == "security-defect")):
                    return self.reply(404, {"error": "order not found"})
                if method == "GET":
                    return self.reply(200, order)
                if method == "DELETE":
                    del self.server.orders[ident]
                    for key in [k for k, o in self.server.keys.items() if o["id"] == ident]:
                        del self.server.keys[key]
                    return self.reply(200, {"deleted": ident})
            if path == "/jobs" and method == "POST":
                order = self.server.orders.get(data.get("order_id")) if isinstance(data.get("order_id"), str) else None
                if set(data) != {"order_id"} or not order or order["owner"] != actor:
                    return self.reply(404, {"error": "order not found"})
                ident = str(uuid.uuid4())
                self.server.jobs[ident] = {"id": ident, "owner": actor, "order_id": order["id"],
                                           "ready": time.monotonic() + 0.05}
                return self.reply(202, {"id": ident, "state": "pending"})
            if path.startswith(("/jobs/", "/receipts/")):
                ident = path.rsplit("/", 1)[-1]
                job = self.server.jobs.get(ident)
                if not job or job["owner"] != actor:
                    return self.reply(404, {"error": "job not found"})
                if method == "DELETE" and path.startswith("/jobs/"):
                    del self.server.jobs[ident]
                    return self.reply(200, {"deleted": ident})
                if method == "GET":
                    ready = time.monotonic() >= job["ready"]
                    if path.startswith("/jobs/"):
                        return self.reply(200, {"id": ident, "state": "complete" if ready else "pending"})
                    if ready and self.server.mode != "api-defect":
                        return self.reply(200, {"job_id": ident, "order_id": job["order_id"], "delivered": True})
                    return self.reply(404, {"error": "receipt not found"})
        self.reply(404, {"error": "route not found"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="good")
    parser.add_argument("--ready-file", type=Path, required=True, help="new identity JSON path; removed on normal shutdown")
    args = parser.parse_args()
    server = Lab(args.mode)
    created = False
    try:
        with args.ready_file.open("x") as handle:
            created = True
            json.dump(server.identity(), handle)
        print(json.dumps(server.identity()), flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if created:
            args.ready_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
