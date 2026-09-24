const { chromium, firefox, request } = require('@playwright/test');
const fs = require('node:fs');
const { verify } = require('./target.cjs');
(async () => {
 const api = await request.newContext();
 const identity = await verify(api);
 const evidence = { identity, playwright: require('@playwright/test/package.json').version, engines: {} };
 for (const [name, engine] of Object.entries({ chromium, firefox })) {
  let browser;
  try {
   browser = await engine.launch();
   const page = await browser.newPage();
   await page.goto(identity.url);
   evidence.engines[name] = { version: browser.version(), snapshot: await page.locator('body').ariaSnapshot(), controls: await page.locator('input, button, [role], section').evaluateAll(nodes => nodes.map(n => ({ tag:n.tagName, type:n.type, role:n.getAttribute('role'), label:n.getAttribute('aria-label'), min:n.min, max:n.max, required:n.required, text:n.textContent }))), counts: { quantity:await page.getByLabel('Quantity', {exact:true}).count(), button:await page.getByRole('button', {name:'Place order',exact:true}).count(), status:await page.getByRole('status').count(), receipt:await page.getByRole('region',{name:'Receipt',exact:true}).count() } };
  } catch(error) { evidence.engines[name] = { error:String(error) }; }
  finally { await browser?.close(); }
 }
 fs.writeFileSync('artifacts/parcel/observation.json', JSON.stringify(evidence,null,2));
 await api.dispose();
})();
