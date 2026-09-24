"""Black-box contract suite. Set QA_LAB_IDENTITY and QA_ARTIFACT_DIR to rerun."""
import ipaddress
import json
import os
from pathlib import Path
import time
import unittest
import uuid
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

OUT = Path(os.environ.get('QA_ARTIFACT_DIR', 'artifacts/parcel-api/run'))
IDENTITY = Path(os.environ.get('QA_LAB_IDENTITY', 'target.json'))

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None

class Client:
    def __init__(self):
        self.identity = json.loads(IDENTITY.read_text())
        self.origin = self.identity['url']
        url = urlsplit(self.origin)
        if url.scheme != 'http' or not ipaddress.ip_address(url.hostname).is_loopback or url.username or url.password or url.path not in ('', '/') or url.query or url.fragment:
            raise RuntimeError('Only literal local HTTP targets are supported')
        self.opener = build_opener(ProxyHandler({}), NoRedirect())
        OUT.mkdir(parents=True, exist_ok=False)
        status, live = self.call('GET', '/__identity', actor=None)
        if status != 200 or live != self.identity or live['role'] != 'test' or live['fixture'] != 'qadrillion-specialist-lab':
            raise RuntimeError('Live identity mismatch; mutations blocked')
        (OUT / 'identity.json').write_text(json.dumps(live, indent=2))

    def call(self, method, path, body=None, key=None, actor='alice', raw=None):
        headers = {}
        if actor is not None:
            headers['X-Lab-Actor'] = actor
        if key is not None:
            headers['Idempotency-Key'] = key
        payload = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        if payload is not None:
            headers['Content-Type'] = 'application/json'
        started = time.monotonic()
        try:
            response = self.opener.open(Request(self.origin + path, data=payload, headers=headers, method=method), timeout=1)
        except HTTPError as error:
            response = error
        with response:
            raw_response = response.read(65537)
            event = dict(method=method, path=path, actor=actor, key=key, request=payload.decode() if payload is not None else None, status=response.status, response=raw_response.decode(), content_type=response.headers.get('Content-Type'), elapsed=time.monotonic()-started)
            with (OUT / 'http.jsonl').open('a') as log:
                log.write(json.dumps(event) + '\n')
            if len(raw_response) > 65536:
                raise AssertionError('Response capture bound exceeded')
            if response.headers.get_content_type() != 'application/json':
                raise AssertionError('Expected JSON media type')
            return response.status, json.loads(raw_response)

CLIENT = None

def setUpModule():
    global CLIENT
    CLIENT = Client()

class ParcelContract(unittest.TestCase):
    def setUp(self):
        self.c = CLIENT
        self.orders = []
        self.jobs = []
        self.key = 'qa-' + uuid.uuid4().hex
        self.baselines = {}
        for actor in ('alice', 'bob'):
            status, orders = self.c.call('GET', '/orders', actor=actor)
            self.assertEqual(status, 200)
            self.assertIsInstance(orders, list)
            self.baselines[actor] = orders
        self.addCleanup(self.cleanup)

    def cleanup(self):
        problems = []
        for kind, records in (('jobs', self.jobs), ('orders', self.orders)):
            for actor, identifier in reversed(records):
                status, body = self.c.call('DELETE', '/' + kind + '/' + identifier, actor=actor)
                if status not in (200, 404):
                    problems.append([kind, identifier, status, body])
                status, body = self.c.call('GET', '/' + kind + '/' + identifier, actor=actor)
                if status != 404:
                    problems.append(['still present', kind, identifier, status, body])
                if kind == 'jobs':
                    status, body = self.c.call('GET', '/receipts/' + identifier, actor=actor)
                    if status != 404:
                        problems.append(['receipt remains', identifier, status, body])
        for actor, before in self.baselines.items():
            status, after = self.c.call('GET', '/orders', actor=actor)
            if status != 200 or sorted(after, key=lambda x: x['id']) != sorted(before, key=lambda x: x['id']):
                problems.append(['baseline mismatch', actor, before, after])
        with (OUT / 'cleanup.jsonl').open('a') as log:
            log.write(json.dumps(dict(test=self.id(), orders=self.orders, jobs=self.jobs, problems=problems)) + '\n')
        self.assertEqual(problems, [], 'Cleanup or unrelated-state invariant failed')

    def post_order(self, body, key, actor='alice', raw=None):
        status, obj = self.c.call('POST', '/orders', body, key, actor, raw)
        if isinstance(obj, dict) and isinstance(obj.get('id'), str):
            item = (actor, obj['id'])
            if item not in self.orders:
                self.orders.append(item)
        return status, obj

    def create(self, quantity=3, key=None, actor='alice'):
        status, obj = self.post_order({'quantity': quantity}, key or self.key, actor)
        self.assertEqual(status, 201)
        self.assertIsInstance(obj.get('id'), str)
        self.assertTrue(obj['id'])
        expected = dict(id=obj['id'], owner=actor, quantity=quantity, total_cents=quantity*500)
        self.assertEqual(obj, expected)
        self.assertIs(type(obj['quantity']), int)
        self.assertIs(type(obj['total_cents']), int)
        self.assertEqual(self.c.call('GET', '/orders/' + obj['id'], actor=actor), (200, expected))
        self.assertEqual(self.c.call('GET', '/orders', actor=actor), (200, self.baselines[actor] + [expected]))
        return obj

    def test_positive_control(self):
        self.create()

    def test_retry_and_conflict(self):
        original = self.create()
        self.assertEqual(self.post_order({'quantity': 3}, self.key), (200, original))
        self.assertEqual(self.post_order({'quantity': 4}, self.key)[0], 409)
        self.assertEqual(self.c.call('GET', '/orders/' + original['id']), (200, original))
        self.assertEqual(self.c.call('GET', '/orders'), (200, self.baselines['alice'] + [original]))
        status, fresh = self.post_order({'quantity': 3}, self.key + '-fresh')
        self.assertEqual(status, 201)
        self.assertNotEqual(fresh['id'], original['id'])
        self.assertEqual(self.c.call('GET', '/orders'), (200, self.baselines['alice'] + [original, fresh]))

    def test_actor_key_namespaces(self):
        alice = self.create(actor='alice')
        bob = self.create(actor='bob')
        self.assertNotEqual(alice['id'], bob['id'])
        for actor, obj in [('alice', alice), ('bob', bob)]:
            self.assertEqual(self.post_order({'quantity': 3}, self.key, actor), (200, obj))

    def test_delete_removes_key_and_preserves_other_order(self):
        first = self.create()
        status, other = self.post_order({'quantity': 2}, self.key + '-other')
        self.assertEqual(status, 201)
        status, deleted = self.c.call('DELETE', '/orders/' + first['id'])
        self.assertEqual(status, 200)
        self.assertIn(first['id'], json.dumps(deleted))
        self.assertEqual(self.c.call('GET', '/orders/' + first['id'])[0], 404)
        self.assertEqual(self.c.call('DELETE', '/orders/' + first['id'])[0], 404)
        self.assertEqual(self.c.call('GET', '/orders/' + other['id']), (200, other))
        status, replacement = self.post_order({'quantity': 4}, self.key)
        self.assertEqual(status, 201)
        self.assertNotEqual(first['id'], replacement['id'])
        self.assertEqual(replacement['total_cents'], 2000)

    def test_absent_resources(self):
        absent = 'qa-absent-' + uuid.uuid4().hex
        for route in ('orders', 'jobs', 'receipts'):
            self.assertEqual(self.c.call('GET', '/' + route + '/' + absent)[0], 404)
        for route in ('orders', 'jobs'):
            self.assertEqual(self.c.call('DELETE', '/' + route + '/' + absent)[0], 404)
        self.assertEqual(self.c.call('POST', '/jobs', {'order_id': absent})[0], 404)

    def test_job_completion_and_receipt(self):
        order = self.create()
        started = time.monotonic()
        status, job = self.c.call('POST', '/jobs', {'order_id': order['id']})
        if isinstance(job, dict) and isinstance(job.get('id'), str):
            self.jobs.append(('alice', job['id']))
        self.assertEqual(status, 202)
        self.assertEqual(job['state'], 'pending')
        job_id = job['id']
        while True:
            status, state = self.c.call('GET', '/jobs/' + job_id)
            self.assertEqual(status, 200)
            self.assertEqual(state['id'], job_id)
            self.assertIn(state['state'], ('pending', 'complete'))
            if state['state'] == 'complete':
                self.assertLessEqual(time.monotonic()-started, 2.0)
                break
            self.assertLess(time.monotonic()-started, 2.0, 'Job did not complete within 2 seconds')
            receipt_status, receipt = self.c.call('GET', '/receipts/' + job_id)
            # Completion can race the receipt read; re-observe state before rejecting it.
            if receipt_status != 404:
                self.assertEqual(self.c.call('GET', '/jobs/' + job_id)[1]['state'], 'complete')
            time.sleep(0.02)
        with self.subTest(criterion='completion delivers receipt'):
            self.assertEqual(self.c.call('GET', '/receipts/' + job_id), (200, dict(job_id=job_id, order_id=order['id'], delivered=True)))
        self.assertEqual(self.c.call('GET', '/orders/' + order['id']), (200, order))
        self.assertEqual(self.c.call('DELETE', '/jobs/' + job_id)[0], 200)
        self.assertEqual(self.c.call('GET', '/jobs/' + job_id)[0], 404)
        self.assertEqual(self.c.call('GET', '/receipts/' + job_id)[0], 404)
        self.assertEqual(self.c.call('GET', '/orders/' + order['id']), (200, order))

# Each boundary has its own lifecycle and result, avoiding early-abort coverage gaps.
def valid_case(quantity=None, key_length=None):
    def test(self):
        self.create(quantity if quantity is not None else 3, ('k' * key_length) if key_length else None)
    return test

for name, quantity in [('minimum', 1), ('maximum', 100), ('near_minimum', 2), ('near_maximum', 99)]:
    setattr(ParcelContract, 'test_quantity_' + name, valid_case(quantity))
for length in (1, 128):
    setattr(ParcelContract, 'test_key_length_' + str(length), valid_case(key_length=length))

def invalid_case(body=None, raw=None, key_kind='valid', expected=422):
    def test(self):
        keys = {'valid': self.key, 'missing': None, 'empty': '', 'long': 'x'*129}
        status, response = self.post_order(body, keys[key_kind], raw=raw)
        with self.subTest(criterion='exact rejection status'):
            self.assertEqual(status, expected, response)
        self.assertEqual(self.c.call('GET', '/orders'), (200, self.baselines['alice']))
    return test

INVALID = {'missing_quantity': {}, 'null_quantity': {'quantity': None}, 'zero': {'quantity': 0}, 'negative': {'quantity': -1}, 'above_maximum': {'quantity': 101}, 'true': {'quantity': True}, 'false': {'quantity': False}, 'float': {'quantity': 1.5}, 'integral_float': {'quantity': 1.0}, 'string': {'quantity': '1'}, 'array_quantity': {'quantity': [1]}, 'object_quantity': {'quantity': {}}, 'unknown_field': {'quantity': 1, 'extra': 2}, 'array_body': [], 'string_body': 'value', 'number_body': 1}
for name, body in INVALID.items():
    setattr(ParcelContract, 'test_invalid_' + name, invalid_case(body))
for name, raw in [('null_body', b'null'), ('malformed', b'{'), ('empty_body', b'')]:
    setattr(ParcelContract, 'test_invalid_' + name, invalid_case(raw=raw))
for kind in ('missing', 'empty', 'long'):
    setattr(ParcelContract, 'test_invalid_key_' + kind, invalid_case({'quantity': 1}, key_kind=kind, expected=400))

if __name__ == '__main__':
    unittest.main()
