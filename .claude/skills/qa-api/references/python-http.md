# Python stdlib HTTP recipe

Use this only for a Python stdlib project or the repository's synthetic lab.
Existing language-native suites and collection runners remain valid. Inspect
`python3 --version`, the project's test command and its supported Python version.

## Disposable reference target

Read `tools/specialists/CONTRACT.md`, then inspect the CLI:

```sh
python3 tools/specialists/lab.py --help
```

Start a new service in a managed terminal/process. Use a newly allocated directory
and retain its expanded identity-file path for the test process:

```sh
qa_lab_dir="$(mktemp -d)"
python3 tools/specialists/lab.py --mode good --ready-file "$qa_lab_dir/ready.json"
```

The foreground process prints its identity once ready. In an evaluation, use the
target identity supplied by the evaluator instead of choosing a variant. Load
the identity JSON, request its `url + '/__identity'`, and compare fixture, role,
run_id, build, mode and URL before mutations. The mode is identity, not an oracle.
Do not read the fixture's implementation to manufacture expected test results.

The lab's `X-Lab-Actor` header is deliberately synthetic, not authentication.
Use unique idempotency keys per case. Cleanup owned jobs before owned orders in
`addCleanup`/`finally`; never remove another case's data by clearing the service.
After the run, send Ctrl-C to the exact service process, confirm its exit and a
closed port, then remove the task-owned temporary directory. Shutdown erases the
memory-only dataset; preserve the run identity in the test artifact first.

## Small client seam

For this loopback fixture, a client like this retains non-2xx bodies and prevents
redirect/proxy surprises. Keep the verified origin fixed; do not pass arbitrary
URLs from responses into it.

```python
import json
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None


def request_json(origin, method, path, *, actor=None, body=None, key=None):
    headers = {}
    if actor is not None:
        headers["X-Lab-Actor"] = actor
    if key is not None:
        headers["Idempotency-Key"] = key
    payload = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(body).encode("utf-8")
    request = Request(origin + path, data=payload, headers=headers, method=method)
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        response = opener.open(request, timeout=1.0)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read(65537)
        if len(raw) > 65536:
            raise AssertionError("response exceeded fixture capture limit")
        return response.status, json.loads(raw)
```

Use assertions in the test, not inside the client, so an expected 422 or 404 is
observable. Catch transport errors only where the scenario expects them; do not
convert every exception into an empty successful response. The timeout bounds
blocking operations, not an entire polling loop: use a monotonic deadline for
the operation and the runner's process timeout for the suite.

## Author and execute against the contract

Create real `unittest.TestCase` cases in the disposable exercise's `tests/`.
Supply the pinned identity through an explicitly named argument/config or
`QA_LAB_IDENTITY` environment variable. Include the contract slice selected in
the plan, such as quantity partitions, exact totals and read-back, same-key retry
and conflict, and completed job plus delivered receipt. Assert cleanup and final
list state. For polling, repeatedly observe pending/complete until the two-second
contract deadline, using a bounded polling interval; retain the final response
when the deadline expires. Completion without the promised receipt is a failure.

```sh
python3 -m unittest discover -s tests -p 'test_api_*.py' -v
```

Record exit status and collected count. Run the same authored test file against
the corrected target when supplied; retain its hash and both identities/results.
The evaluator may inject independent defects; the procedure does not prescribe
an expected suite verdict.

Inspected APIs: [urllib.request](https://docs.python.org/3/library/urllib.request.html)
(`Request`, `build_opener`, `ProxyHandler`, `HTTPRedirectHandler`, timeouts) and
[urllib.error](https://docs.python.org/3/library/urllib.error.html)
(`HTTPError` response body). The client uses their Python 3.11-compatible subset;
verify the actual interpreter used by the team.
