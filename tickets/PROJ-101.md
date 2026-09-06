---
id: PROJ-101
title: Invoice PDF export — amounts in the wrong currency after a customer changes their locale
scope: multi-surface
status: done
verdict: partial
build: web 2.14.0 (commit 9f3c1a2) · api 2.14.1 (staging deploy 2026-09-04)
environment: staging
tracker: https://tracker.example/browse/PROJ-101
design: null
source_refs:
  - source/web/src/features/invoices/export/InvoicePdf.tsx:41-88
  - source/web/src/lib/money/format.ts:12
  - source/api/src/invoices/export/render.ts:57-102
  - source/api/src/customers/locale.ts:9
started: 2026-09-04
updated: 2026-09-05
next_action: "Re-run scenario 4 (locale change mid-session) on the build that contains the api fix for the cached locale; expected: PDF totals in the customer's current currency"
blockers: []
---

# PROJ-101 — Invoice PDF export shows amounts in the wrong currency after a locale change

This is a **worked example against a fictional product** (an invoicing web app with a Node API). It
shows the shape of a finished ticket file: the frontmatter is the machine-readable state; the body is
the evidence. Names, numbers and output are invented but realistic.

## Analysis

**Requirements / acceptance criteria** (from the tracker, verbatim)

- AC1: The exported PDF shows every amount in the customer's currency as set at export time.
- AC2: Changing the customer's locale updates the currency used by subsequent exports without a re-login.
- AC3: Historical invoices keep the currency they were issued in.

**Source review** (`[SEVERITY]` blocks per `code-review.mdc`)

- `[HIGH]` `source/api/src/invoices/export/render.ts:57-102` — `renderInvoicePdf()` reads
  `customer.locale` from a per-process cache (`localeCache.get(customerId)`) that is populated on first
  request and never invalidated. A locale change via `PATCH /customers/:id` writes the DB but not the
  cache → AC2 fails until the process restarts. Testable: change locale, export, compare currency.
- `[MEDIUM]` `source/web/src/lib/money/format.ts:12` — `formatMoney(amount, currency = "EUR")` defaults
  to EUR when `currency` is `undefined`. If the API omits `currency` for legacy invoices the UI shows
  EUR silently. Testable: invoice without `currency` field → expect an explicit error, not EUR.
- `[LOW]` `source/web/src/features/invoices/export/InvoicePdf.tsx:41-88` — the export button has
  `data-testid="invoice-export-pdf"`; the resulting toast has no identifier. Cosmetic for testing; not a
  product defect.
- AC3 is implemented correctly: `render.ts:71` uses `invoice.issuedCurrency`, not the customer's
  current locale, for invoices with `status: issued`.

**Locator / endpoint table**

| Element or endpoint | Identifier | In source? | In build? | Notes |
|---|---|---|---|---|
| Export PDF button | `data-testid="invoice-export-pdf"` | yes (`InvoicePdf.tsx:52`) | yes (live smoke 2026-09-04) | |
| Export success toast | — | **no** | **no** | MISSING — assert on the download event instead; product ask filed as PROJ-104 |
| `PATCH /customers/:id` | route `customers/locale.ts:9` | yes | yes (200 on staging) | |
| `POST /invoices/:id/export` | route `export/render.ts:57` | yes | yes | returns `application/pdf` |

## Test plan

| # | Scenario | Type | Status | Notes |
|---|---|---|---|---|
| 1 | Export with default locale (de-DE) → amounts in EUR, formatted `1.234,56 €` | automated (API) | pass | |
| 2 | Export for a customer created with en-GB → GBP | automated (API) | pass | |
| 3 | Issued invoice keeps issued currency after locale change (AC3) | automated (API) | pass | |
| 4 | Change locale de-DE → en-GB, export a draft invoice → GBP (AC2) | automated (API) | **fail** | cache; see results |
| 5 | Same as 4 through the UI (button → download) | automated (Playwright) | **fail** | same root cause |
| 6 | Invoice payload without `currency` → UI shows an error, not EUR | automated (UI) | fail | `[MEDIUM]` confirmed |
| 7 | Export after API process restart → GBP | manual | pass | confirms the cache diagnosis |

## Execution & results

```
$ pytest tests/api/invoices/test_export_currency.py -v
tests/api/invoices/test_export_currency.py::test_export_default_locale_eur PASSED        [ 14%]
tests/api/invoices/test_export_currency.py::test_export_en_gb_customer_gbp PASSED        [ 28%]
tests/api/invoices/test_export_currency.py::test_issued_invoice_keeps_currency PASSED     [ 42%]
tests/api/invoices/test_export_currency.py::test_locale_change_updates_export FAILED     [ 57%]
tests/api/invoices/test_export_currency.py::test_missing_currency_is_error XFAIL (PROJ-101 [MEDIUM]; strict) [ 71%]
================================== FAILURES ===================================
____________________ test_locale_change_updates_export ________________________
AssertionError: PDF currency symbol
  expected: '£'   (customer locale en-GB after PATCH /customers/c_8f2 → 200)
  actual:   '€'   (PDF page 1, total line: "Gesamt 1.234,56 €")
============ 3 passed, 1 failed, 1 xfailed in 6.41s ============

$ npx playwright test invoices/export-currency.spec.ts
  ✘ 1 export after locale change shows customer currency (4.8s)
    Expected substring: "£"   Received: "€"   (pdf text, page 1)
  1 failed, 0 passed
```

Scenario 4 re-run once (ADR-0003): identical failure. Scenario 7 (manual, after `pm2 restart api` on
staging by the backend on-call): PDF shows `£1,234.56` — cache confirmed as the cause.

## Handoff

Mirrors `next_action`. Done: scenarios 1–3, 7 pass; 4–5 fail with a confirmed root cause; 6 encoded as
a strict xfail so it flips when the product reconciles. Open: re-run 4–5 on a build containing the
cache invalidation. Not verified: behaviour under concurrent locale changes for two customers sharing
a process (out of scope for this ticket; noted for the regression set).

## Tracker comment

Prepared per `tracker-reporting.mdc`. Posted: yes (comment 44812, after approval 2026-09-05).

> **QA — PROJ-101 — Partial.** AC1 ✅ AC3 ✅ AC2 ❌.
> Root cause: `render.ts` per-process locale cache is never invalidated after `PATCH /customers/:id`
> (confirmed by restart). Secondary: `formatMoney` defaults to EUR on a missing currency — filed as
> PROJ-103 (Medium). Missing toast identifier — PROJ-104 (Low, test-enablement).
> Evidence: 3 passed / 1 failed / 1 xfail (API), 1 failed (UI); output attached. Re-test on the build
> with the cache fix.

## Notes

- The two defects are separate tickets (PROJ-103, PROJ-104) so each can be closed on its own evidence.
- Automated tests live in the team's own automation repo (`automation/`), in the team's framework.
