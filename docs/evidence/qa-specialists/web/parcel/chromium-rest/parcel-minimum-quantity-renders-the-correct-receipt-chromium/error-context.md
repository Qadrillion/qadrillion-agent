# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: parcel.spec.js >> minimum quantity renders the correct receipt
- Location: tests/parcel.spec.js:119:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('region', { name: 'Receipt', exact: true })
Expected substring: "1 parcels — $5.00"
Received string:    "Receipt1 parcels — $4.00"
Timeout: 5000ms

Call log:
  - Expect "soft toContainText" getByRole('region', { name: 'Receipt', exact: true }) with timeout 5000ms
  - waiting for getByRole('region', { name: 'Receipt', exact: true })
    14 × locator resolved to <section aria-label="Receipt">…</section>
       - unexpected value "Receipt1 parcels — $4.00"

```

```yaml
- region "Receipt":
  - heading "Receipt" [level=2]
  - paragraph: 1 parcels — $4.00
```

# Test source

```ts
  1   | const { test: base, expect } = require('@playwright/test');
  2   | const { verify } = require('./target.cjs');
  3   | const test = base.extend({
  4   |   journey: async ({ page, request, browser }, use, info) => {
  5   |     const identity = await verify(request);
  6   |     const owned = [];
  7   |     const pending = [];
  8   |     const diagnostics = { identity, browser: browser.version(), viewport: page.viewportSize(), locale: 'en-US', timezone: 'UTC', console: [], errors: [], network: [], cleanup: [] };
  9   |     const baselines = {};
  10  |     for (const actor of ['alice', 'bob']) {
  11  |       const r = await request.get(`${identity.url}/orders`, { headers: { 'X-Lab-Actor': actor } });
  12  |       expect(r.status()).toBe(200);
  13  |       baselines[actor] = await r.json();
  14  |     }
  15  |     page.on('console', msg => { if (msg.type() === 'error') diagnostics.console.push(msg.text()); });
  16  |     page.on('pageerror', error => diagnostics.errors.push(String(error)));
  17  |     page.on('response', response => {
  18  |       const req = response.request();
  19  |       diagnostics.network.push({ method: req.method(), url: response.url(), status: response.status() });
  20  |       if (req.method() === 'POST' && new URL(response.url()).pathname === '/orders' && response.ok()) {
  21  |         pending.push((async () => {
  22  |           const order = await response.json();
  23  |           const actor = req.headers()['x-lab-actor'];
  24  |           expect(['alice', 'bob']).toContain(actor);
  25  |           expect(baselines[actor].some(record => record.id === order.id)).toBe(false);
  26  |           owned.push({ id: order.id, actor });
  27  |         })());
  28  |       }
  29  |     });
  30  |     try {
  31  |       await page.goto(identity.url);
  32  |       await use({ identity, owned, pending, diagnostics });
  33  |     } finally {
  34  |       try {
  35  |         await Promise.all(pending);
  36  |         diagnostics.snapshot = await page.locator('body').ariaSnapshot();
  37  |         await page.screenshot({ path: info.outputPath('final.png'), fullPage: true });
  38  |         await verify(request);
  39  |         for (const order of owned) {
  40  |           const r = await request.delete(`${identity.url}/orders/${order.id}`, { headers: { 'X-Lab-Actor': order.actor } });
  41  |           diagnostics.cleanup.push({ ...order, status: r.status() });
  42  |           expect(r.status()).toBe(200);
  43  |         }
  44  |         for (const actor of ['alice', 'bob']) {
  45  |           const r = await request.get(`${identity.url}/orders`, { headers: { 'X-Lab-Actor': actor } });
  46  |           expect(r.status()).toBe(200);
  47  |           expect(await r.json()).toEqual(baselines[actor]);
  48  |         }
  49  |         diagnostics.baselineRestored = true;
  50  |       } finally {
  51  |         await info.attach('diagnostics', { body: JSON.stringify(diagnostics, null, 2), contentType: 'application/json' });
  52  |       }
  53  |     }
  54  |   }
  55  | });
  56  | test.use({ locale: 'en-US', timezoneId: 'UTC', viewport: { width: 1280, height: 720 } });
  57  | 
  58  | async function assertOrder(page, request, journey, quantity, receiptText, responsePromise) {
  59  |   const response = await responsePromise;
  60  |   expect(response.status()).toBe(201);
  61  |   await Promise.all(journey.pending);
  62  |   expect(journey.owned).toHaveLength(1);
  63  |   const { id, actor } = journey.owned[0];
  64  |   const saved = await request.get(`${journey.identity.url}/orders/${id}`, { headers: { 'X-Lab-Actor': actor } });
  65  |   expect(saved.status()).toBe(200);
  66  |   const order = await saved.json();
  67  |   expect(order).toMatchObject({ id, owner: actor, quantity, total_cents: quantity * 500 });
  68  |   await expect.soft(page.getByRole('status')).toHaveText('Order saved');
  69  |   await expect.soft(page.getByRole('button', { name: 'Place order', exact: true })).toBeEnabled();
  70  |   const receipt = page.getByRole('region', { name: 'Receipt', exact: true });
  71  |   await expect(receipt).toHaveCount(1);
  72  |   journey.diagnostics.receipt = await receipt.innerText();
  73  |   journey.diagnostics.persisted = order;
> 74  |   await expect.soft(receipt).toContainText(receiptText);
      |                              ^ Error: expect(locator).toContainText(expected) failed
  75  |   await page.reload();
  76  |   const reloaded = await request.get(`${journey.identity.url}/orders/${id}`, { headers: { 'X-Lab-Actor': actor } });
  77  |   expect(await reloaded.json()).toEqual(order);
  78  | }
  79  | function orderResponse(page) {
  80  |   return page.waitForResponse(r => new URL(r.url()).pathname === '/orders' && r.request().method() === 'POST');
  81  | }
  82  | 
  83  | test('nontrivial order receipt agrees with the 500-cent contract and persisted state', async ({ page, request, journey }) => {
  84  |   await expect(page.getByLabel('Quantity', { exact: true })).toHaveCount(1);
  85  |   await page.getByLabel('Quantity', { exact: true }).fill('3');
  86  |   const response = orderResponse(page);
  87  |   await page.getByRole('button', { name: 'Place order', exact: true }).click();
  88  |   await assertOrder(page, request, journey, 3, '3 parcels — $15.00', response);
  89  | });
  90  | 
  91  | test('keyboard reaches controls, rejects invalid quantities and recovers at upper boundary', async ({ page, request, journey }, info) => {
  92  |   const quantity = page.getByLabel('Quantity', { exact: true });
  93  |   const button = page.getByRole('button', { name: 'Place order', exact: true });
  94  |   await page.keyboard.press('Tab');
  95  |   await expect(quantity).toBeFocused();
  96  |   journey.diagnostics.focus = await quantity.evaluate(el => ({ visible: el.matches(':focus-visible'), outline: getComputedStyle(el).outline }));
  97  |   expect(journey.diagnostics.focus.visible).toBe(true);
  98  |   await page.screenshot({ path: info.outputPath('keyboard-focus.png') });
  99  |   for (const value of ['0', '101', '1.5', '']) {
  100 |     await page.keyboard.press('ControlOrMeta+A');
  101 |     if (value) await page.keyboard.type(value); else await page.keyboard.press('Backspace');
  102 |     await page.keyboard.press('Tab');
  103 |     await expect(button).toBeFocused();
  104 |     await page.keyboard.press('Enter');
  105 |     await expect(quantity).toBeFocused();
  106 |     expect(await quantity.evaluate(el => el.validity.valid)).toBe(false);
  107 |     await expect(page.getByRole('status')).toHaveText('Ready');
  108 |     expect(journey.diagnostics.network.filter(r => r.method === 'POST')).toHaveLength(0);
  109 |   }
  110 |   await page.keyboard.press('ControlOrMeta+A');
  111 |   await page.keyboard.type('100');
  112 |   await page.keyboard.press('Tab');
  113 |   await expect(button).toBeFocused();
  114 |   const response = orderResponse(page);
  115 |   await page.keyboard.press('Enter');
  116 |   await assertOrder(page, request, journey, 100, '100 parcels — $500.00', response);
  117 | });
  118 | 
  119 | test('minimum quantity renders the correct receipt', async ({ page, request, journey }) => {
  120 |   await page.getByLabel('Quantity', { exact: true }).fill('1');
  121 |   const response = orderResponse(page);
  122 |   await page.getByRole('button', { name: 'Place order', exact: true }).click();
  123 |   await assertOrder(page, request, journey, 1, '1 parcels — $5.00', response);
  124 | });
  125 | 
```