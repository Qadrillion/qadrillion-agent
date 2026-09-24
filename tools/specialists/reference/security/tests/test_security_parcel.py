"""Contract-based local regression: python3 tests/test_security_parcel.py --identity target.json --out artifacts/run"""
import argparse
import hashlib
import ipaddress
import json
import platform
import sys
import time
import unittest
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


class ParcelAuthorization(unittest.TestCase):
    def request(self, method, path, actor=None, body=None, key=None):
        if self.requests >= 100:
            raise RuntimeError('100-request ceiling reached')
        if method != 'GET' and not self.verified:
            raise RuntimeError('Mutation before verified identity')
        self.requests += 1
        headers = {'Content-Type': 'application/json'}
        if actor is not None:
            headers['X-Lab-Actor'] = actor
        if key:
            headers['Idempotency-Key'] = key
        req = Request(self.identity['url'] + path, method=method, headers=headers,
                      data=None if body is None else json.dumps(body).encode())
        entry = dict(number=self.requests, method=method, path=path, actor=actor, body=body)
        self.trace.append(entry)
        try:
            try:
                response = self.client.open(req, timeout=2)
            except HTTPError as error:
                response = error
            with response:
                raw = response.read(65537)
                if len(raw) > 65536:
                    raise RuntimeError('Response capture limit exceeded')
                value = json.loads(raw)
                entry.update(status=response.status, response=value)
                return response.status, value
        except Exception as error:
            entry['error'] = str(error)
            raise

    def check(self, name, actual, expected):
        ok = actual == expected
        self.checks.append(dict(name=name, passed=ok, actual=actual, expected=expected))
        with self.subTest(check=name):
            self.assertEqual(actual, expected)

    def path(self, kind, identifier):
        return '/' + kind + '/' + quote(str(identifier), safe='')

    def setUp(self):
        self.requests = 0
        self.verified = False
        self.trace, self.checks, self.owned, self.cleanup = [], [], [], []
        self.addCleanup(self.finish)
        self.identity = json.loads(Path(ARGS.identity).read_text())
        url = urlsplit(self.identity['url'])
        self.assertEqual(url.scheme, 'http')
        self.assertTrue(ipaddress.ip_address(url.hostname).is_loopback)
        self.assertFalse(url.username or url.password or url.query or url.fragment)
        self.assertIn(url.path, ('', '/'))
        self.assertEqual(self.identity['fixture'], 'qadrillion-specialist-lab')
        self.assertEqual(self.identity['role'], 'test')
        self.client = build_opener(ProxyHandler({}), NoRedirect())
        status, live = self.request('GET', '/__identity')
        self.assertEqual(status, 200)
        for field in ('fixture', 'role', 'run_id', 'build', 'mode', 'url'):
            self.assertEqual(live[field], self.identity[field], field)
        self.verified = True

    def test_actor_object_matrix(self):
        baseline = {}
        objects = {}
        for actor, quantity in [('alice', 3), ('bob', 7)]:
            status, baseline[actor] = self.request('GET', '/orders', actor)
            self.assertEqual(status, 200)
            status, order = self.request('POST', '/orders', actor, {'quantity': quantity}, str(uuid.uuid4()))
            if isinstance(order, dict) and 'id' in order:
                self.owned.append((actor, 'orders', order['id']))
            self.assertEqual(status, 201)
            expected = dict(id=order['id'], owner=actor, quantity=quantity, total_cents=quantity * 500)
            self.check(actor + ' create order content', order, expected)
            self.check(actor + ' own order read', self.request('GET', self.path('orders', order['id']), actor), (200, expected))
            started = time.monotonic()
            status, job = self.request('POST', '/jobs', actor, {'order_id': order['id']})
            if isinstance(job, dict) and 'id' in job:
                self.owned.append((actor, 'jobs', job['id']))
            self.assertEqual(status, 202)
            self.check(actor + ' job initially pending', job.get('state'), 'pending')
            for attempt in range(6):
                status, completed = self.request('GET', self.path('jobs', job['id']), actor)
                self.assertEqual(status, 200)
                if completed.get('state') == 'complete':
                    break
                if attempt < 5:
                    time.sleep(max(0, min(0.4, started + 2 - time.monotonic())))
            self.check(actor + ' job completes', completed.get('state'), 'complete')
            self.check(actor + ' completion deadline', time.monotonic() - started <= 2.1, True)
            receipt = dict(job_id=job['id'], order_id=order['id'], delivered=True)
            self.check(actor + ' own receipt', self.request('GET', self.path('receipts', job['id']), actor), (200, receipt))
            objects[actor] = (expected, completed, receipt)

        for owner, outsider in [('alice', 'bob'), ('bob', 'alice')]:
            order, job, receipt = objects[owner]
            status, listed = self.request('GET', '/orders', owner)
            self.check(owner + ' list isolation', (status, listed), (200, baseline[owner] + [order]))
            routes = [('orders', order['id'], order), ('jobs', job['id'], job), ('receipts', job['id'], receipt)]
            for kind, identifier, expected in routes:
                path = self.path(kind, identifier)
                methods = ['GET'] if kind == 'receipts' else ['GET', 'DELETE']
                for method in methods:
                    status, denied = self.request(method, path, outsider)
                    self.check(f'{outsider} {method} {owner} {kind} denial', status, 404)
                    protected_keys = set(expected)
                    self.check(f'{outsider} {method} {owner} {kind} no protected content',
                               isinstance(denied, dict) and not bool(protected_keys.intersection(denied)), True)
                    self.check(f'{owner} {kind} unchanged after {outsider} {method}',
                               self.request('GET', path, owner), (200, expected))
            status, denied = self.request('POST', '/jobs', outsider, {'order_id': order['id']})
            if status == 202 and isinstance(denied, dict) and 'id' in denied:
                self.owned.append((outsider, 'jobs', denied['id']))
            self.check(outsider + ' cannot create job for foreign order', status, 404)
            self.check(owner + ' order unchanged after foreign job attempt',
                       self.request('GET', self.path('orders', order['id']), owner), (200, order))

        order, job, _ = objects['alice']
        for actor in (None, 'unknown-synthetic-actor'):
            for kind, identifier in [('orders', order['id']), ('jobs', job['id']), ('receipts', job['id'])]:
                for method in (['GET'] if kind == 'receipts' else ['GET', 'DELETE']):
                    status, denied = self.request(method, self.path(kind, identifier), actor)
                    self.check(f'{actor} {method} {kind} unauthorized', status, 401)
                    self.check(f'{actor} {method} {kind} no object content',
                               isinstance(denied, dict) and not {'id', 'owner', 'quantity', 'job_id', 'order_id', 'delivered', 'state'}.intersection(denied), True)
        for owner, (order, job, receipt) in objects.items():
            for kind, obj, identifier in [('orders', order, order['id']), ('jobs', job, job['id']), ('receipts', receipt, job['id'])]:
                self.check(owner + ' final protected ' + kind, self.request('GET', self.path(kind, identifier), owner), (200, obj))
        self.baseline = baseline

    def finish(self):
        try:
            for actor, kind, identifier in sorted(self.owned, key=lambda item: item[1] != 'jobs'):
                path = self.path(kind, identifier)
                status, body = self.request('DELETE', path, actor)
                self.cleanup.append(dict(actor=actor, kind=kind, id=identifier, status=status, response=body))
                self.check(f'{actor} own DELETE {kind}', (status, body), (200, {'deleted': identifier}))
                self.check(f'{actor} deleted {kind} absent', self.request('GET', path, actor)[0], 404)
                if kind == 'jobs':
                    self.check(f'{actor} derived receipt removed', self.request('GET', self.path('receipts', identifier), actor)[0], 404)
            for actor, original in getattr(self, 'baseline', {}).items():
                self.check(actor + ' original list restored', self.request('GET', '/orders', actor), (200, original))
        finally:
            out = Path(ARGS.out)
            out.mkdir(parents=True, exist_ok=True)
            (out / 'evidence.json').write_text(json.dumps(dict(identity=getattr(self, 'identity', None),
                identity_verified=self.verified, requests=self.requests, ceiling=100, trace=self.trace,
                checks=self.checks, cleanup=self.cleanup, python=sys.version, platform=platform.platform(),
                test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--identity', required=True)
    parser.add_argument('--out', required=True)
    ARGS = parser.parse_args()
    unittest.main(argv=[sys.argv[0]], verbosity=2)
