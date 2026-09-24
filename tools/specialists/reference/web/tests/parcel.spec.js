const { test: base, expect } = require('@playwright/test');
const { verify } = require('./target.cjs');
const test = base.extend({
  journey: async ({ page, request, browser }, use, info) => {
    const identity = await verify(request);
    const owned = [];
    const pending = [];
    const diagnostics = { identity, browser: browser.version(), viewport: page.viewportSize(), locale: 'en-US', timezone: 'UTC', console: [], errors: [], network: [], cleanup: [] };
    const baselines = {};
    for (const actor of ['alice', 'bob']) {
      const r = await request.get(`${identity.url}/orders`, { headers: { 'X-Lab-Actor': actor } });
      expect(r.status()).toBe(200);
      baselines[actor] = await r.json();
    }
    page.on('console', msg => { if (msg.type() === 'error') diagnostics.console.push(msg.text()); });
    page.on('pageerror', error => diagnostics.errors.push(String(error)));
    page.on('response', response => {
      const req = response.request();
      diagnostics.network.push({ method: req.method(), url: response.url(), status: response.status() });
      if (req.method() === 'POST' && new URL(response.url()).pathname === '/orders' && response.ok()) {
        pending.push((async () => {
          const order = await response.json();
          const actor = req.headers()['x-lab-actor'];
          expect(['alice', 'bob']).toContain(actor);
          expect(baselines[actor].some(record => record.id === order.id)).toBe(false);
          owned.push({ id: order.id, actor });
        })());
      }
    });
    try {
      await page.goto(identity.url);
      await use({ identity, owned, pending, diagnostics });
    } finally {
      const teardownErrors = [];
      diagnostics.teardownErrors = [];
      const recordError = (phase, error) => {
        teardownErrors.push(error);
        diagnostics.teardownErrors.push({ phase, error: String(error), stack: error?.stack });
      };
      const attempt = async (phase, action) => {
        try { await action(); return true; }
        catch (error) { recordError(phase, error); return false; }
      };
      for (const result of await Promise.allSettled(pending)) {
        if (result.status === 'rejected') recordError('order observation', result.reason);
      }
      await attempt('snapshot', async () => { diagnostics.snapshot = await page.locator('body').ariaSnapshot(); });
      await attempt('screenshot', () => page.screenshot({ path: info.outputPath('final.png'), fullPage: true }));
      // Diagnostic failures must not strand owned data; failed identity still forbids mutations.
      if (await attempt('cleanup identity', () => verify(request))) {
        for (const order of owned) {
          await attempt(`delete ${order.id}`, async () => {
            const r = await request.delete(`${identity.url}/orders/${order.id}`, { headers: { 'X-Lab-Actor': order.actor } });
            diagnostics.cleanup.push({ ...order, status: r.status() });
            expect(r.status()).toBe(200);
          });
        }
        let restored = true;
        for (const actor of ['alice', 'bob']) {
          const actorRestored = await attempt(`baseline ${actor}`, async () => {
            const r = await request.get(`${identity.url}/orders`, { headers: { 'X-Lab-Actor': actor } });
            expect(r.status()).toBe(200);
            expect(await r.json()).toEqual(baselines[actor]);
          });
          restored = actorRestored && restored;
        }
        diagnostics.baselineRestored = restored;
      }
      await attempt('diagnostic attachment', () => info.attach('diagnostics', { body: JSON.stringify(diagnostics, null, 2), contentType: 'application/json' }));
      if (teardownErrors.length) throw new AggregateError(teardownErrors, 'Browser teardown failed; inspect diagnostics');
    }
  }
});
test.use({ locale: 'en-US', timezoneId: 'UTC', viewport: { width: 1280, height: 720 } });

async function assertOrder(page, request, journey, quantity, receiptText, responsePromise) {
  const response = await responsePromise;
  expect(response.status()).toBe(201);
  await Promise.all(journey.pending);
  expect(journey.owned).toHaveLength(1);
  const { id, actor } = journey.owned[0];
  const saved = await request.get(`${journey.identity.url}/orders/${id}`, { headers: { 'X-Lab-Actor': actor } });
  expect(saved.status()).toBe(200);
  const order = await saved.json();
  expect(order).toMatchObject({ id, owner: actor, quantity, total_cents: quantity * 500 });
  await expect.soft(page.getByRole('status')).toHaveText('Order saved');
  await expect.soft(page.getByRole('button', { name: 'Place order', exact: true })).toBeEnabled();
  const receipt = page.getByRole('region', { name: 'Receipt', exact: true });
  await expect(receipt).toHaveCount(1);
  journey.diagnostics.receipt = await receipt.innerText();
  journey.diagnostics.persisted = order;
  await expect.soft(receipt).toContainText(receiptText);
  await page.reload();
  const reloaded = await request.get(`${journey.identity.url}/orders/${id}`, { headers: { 'X-Lab-Actor': actor } });
  expect(await reloaded.json()).toEqual(order);
}
function orderResponse(page) {
  return page.waitForResponse(r => new URL(r.url()).pathname === '/orders' && r.request().method() === 'POST');
}

test('nontrivial order receipt agrees with the 500-cent contract and persisted state', async ({ page, request, journey }) => {
  await expect(page.getByLabel('Quantity', { exact: true })).toHaveCount(1);
  await page.getByLabel('Quantity', { exact: true }).fill('3');
  const response = orderResponse(page);
  await page.getByRole('button', { name: 'Place order', exact: true }).click();
  await assertOrder(page, request, journey, 3, '3 parcels — $15.00', response);
});

test('keyboard reaches controls, rejects invalid quantities and recovers at upper boundary', async ({ page, request, journey }, info) => {
  const quantity = page.getByLabel('Quantity', { exact: true });
  const button = page.getByRole('button', { name: 'Place order', exact: true });
  await page.keyboard.press('Tab');
  await expect(quantity).toBeFocused();
  journey.diagnostics.focus = await quantity.evaluate(el => ({ visible: el.matches(':focus-visible'), outline: getComputedStyle(el).outline }));
  expect(journey.diagnostics.focus.visible).toBe(true);
  await page.screenshot({ path: info.outputPath('keyboard-focus.png') });
  for (const value of ['0', '101', '1.5', '']) {
    await page.keyboard.press('ControlOrMeta+A');
    if (value) await page.keyboard.type(value); else await page.keyboard.press('Backspace');
    await page.keyboard.press('Tab');
    await expect(button).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(quantity).toBeFocused();
    expect(await quantity.evaluate(el => el.validity.valid)).toBe(false);
    await expect(page.getByRole('status')).toHaveText('Ready');
    expect(journey.diagnostics.network.filter(r => r.method === 'POST')).toHaveLength(0);
  }
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.type('100');
  await page.keyboard.press('Tab');
  await expect(button).toBeFocused();
  const response = orderResponse(page);
  await page.keyboard.press('Enter');
  await assertOrder(page, request, journey, 100, '100 parcels — $500.00', response);
});

test('minimum quantity renders the correct receipt', async ({ page, request, journey }) => {
  await page.getByLabel('Quantity', { exact: true }).fill('1');
  const response = orderResponse(page);
  await page.getByRole('button', { name: 'Place order', exact: true }).click();
  await assertOrder(page, request, journey, 1, '1 parcels — $5.00', response);
});
