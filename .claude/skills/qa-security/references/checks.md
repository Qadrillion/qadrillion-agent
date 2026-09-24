# Bounded security checks

Select rows from the identified trust boundary; this is not a mandatory whole-app
checklist. Match the product's actual rules and use only owned synthetic fixtures.

| Boundary | Author and observe | Limit |
|---|---|---|
| Object/tenant authorization | Owner A creates A's object; actor B can use B's own object but cannot read/change A's. Assert response data and owner read-back after denied mutation. Cover alternate methods and async operation/result URLs where relevant. | A tested route does not prove every route uses the same enforcement. |
| Property authorization | Submit a privileged/immutable property through a permitted create/update action; assert documented rejection or ignoring plus persisted value. | Derive protected properties from the contract, not guessed field names. |
| Session lifecycle | Use task-owned sessions to test expiry/logout/revocation and required reauthentication; verify protected actions after each transition. | Cookie flags or a login success alone do not establish session security. |
| Input/rendering | Send harmless boundary strings through the selected parser/template path; assert data stays data, validation is consistent and state remains valid. | Escaping one marker is a narrow test; actual exploitability needs an authorized reproducer. |
| Upload/download/redirect | Use tiny synthetic files and owned objects, verify permitted type/size/name handling, destination restrictions and access. Use only a controlled local destination for redirect/callback checks. | Do not expand into external fetches, huge files or destructive payloads without scope. |
| Exposure/dependency | Inspect relevant errors/logs/artifacts for synthetic sensitive markers; inspect the pinned dependency report and actual affected path. | A package advisory or pattern match is a lead, not proof of reachable exploitation. |

Stop if a negative check unexpectedly retrieves unrelated data; preserve the
minimum metadata needed to report exposure and redact the content. Proving more
damage is unnecessary for a reproducible finding.

## Executable local authorization exercise

Read `tools/specialists/CONTRACT.md` and use the API skill's Python HTTP recipe
or the team's actual test runner. Start a separate disposable lab or consume the
evaluator's pinned identity; verify it before fixture creation.

Author tests that create one order as `alice` and another as `bob`, using distinct
keys. First assert each can read their own order. Then use Bob's actor header to
GET Alice's known ID: the lab contract requires 404 with no order content.
Assert Bob cannot DELETE it, and Alice can still read the unchanged record.
Check list isolation separately; passing a list check does not prove ID access.
When jobs/receipts are in scope, apply the same owner/non-owner matrix to both
job status and delivered output. Missing/unknown actors must receive 401 on data
routes. These headers simulate actors; no real token authentication is exercised.

Retain the actor/object relationship and sanitized responses so a reviewer can
distinguish an authorization failure from invalid setup. Cleanup as each owner
even when an assertion fails. Run the authored tests against the supplied
corrected target with unchanged assertions and record their hash.

For a Python exercise with cases named `test_security_*.py` under `tests/`:

```sh
python3 -m unittest discover -s tests -p 'test_security_*.py' -v
```

Source mapping: [OWASP WSTG v4.2 object-reference testing](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References/)
supports paired users and owned identifiers. [NIST SP 800-115](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf),
sections 6.3, 6.5 and 7.1–7.2, informs objective, scope, data handling and stop
conditions. Its 2008 methodology is not current tool documentation; the shared
repository authorization and non-production contracts remain authoritative.
