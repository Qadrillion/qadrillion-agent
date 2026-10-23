# Playwright recipe

Use when the project already uses Playwright or the selected disposable exercise
needs a real browser runner. Inspect `package.json`, its lockfile and installed
version before editing configuration:

```sh
npm ls @playwright/test --depth=0
npx --no-install playwright --version
npx --no-install playwright test --help
```

If absent, install a deliberately selected version in the task's disposable
project and retain its lockfile. Install only the engines needed for the selected
checks. A package being installed does not prove its browser executable works.
Use the repository's package manager and scripts for existing projects.

## Isolated reference project

Read `tools/specialists/CONTRACT.md`; start or use the evaluator's disposable lab
and verify `/__identity` before mutations. Set `QA_BASE_URL` to that pinned origin.
A minimal `playwright.config.ts` in the isolated exercise can use:

```typescript
import { defineConfig } from '@playwright/test';

const baseURL = process.env.QA_BASE_URL;
if (!baseURL) throw new Error('QA_BASE_URL must identify the verified lab');

export default defineConfig({
  testDir: './tests',
  retries: 0,
  workers: 1,
  outputDir: 'test-results',
  reporter: [['list'], ['json', { outputFile: 'test-results/results.json' }]],
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
```

The fixture has no real login: its browser uses a synthetic actor. Do not present
this exercise as validation of production authentication. Isolate the server
process per concurrent exercise; browser contexts alone cannot isolate its order
list. For a real app, follow its supported auth setup and give modifying tests
separate accounts or resources. Ignore saved auth state in Git and control access
to traces that may contain session data.

## Observe, author, run

Open the actual page in the browser before asserting locator provenance. Observe
the Quantity input, Place order button, status region and resulting Receipt
section, and record their roles/names plus unique-match counts. With the inspected
lab build, candidate locators are `getByLabel('Quantity')`,
`getByRole('button', { name: 'Place order', exact: true })`,
`getByRole('status')` and `getByRole('region', { name: 'Receipt' })`.
Verify them against the live page instead of treating this list as proof.

Author a test with `test` and `expect` from `@playwright/test`; use the provided
`page` fixture. Fill a nontrivial quantity, place the order, await the expected
receipt text and enabled button, and compare the result with persisted API data
under the same fixture identity. The independent contract is 500 cents per
parcel. A matching toast cannot substitute for this business assertion. Register
owned-record cleanup even if a later assertion fails.

```sh
npx --no-install playwright test --project=chromium --trace on
```

`--trace on` retains first-attempt evidence in a reference run. In normal projects,
`retain-on-failure` preserves a failed trace; `on-first-retry` misses the initial
failure and should not be the only diagnostic evidence. Find actual artifact
paths under `test-results`; open the selected ZIP with `playwright show-trace`.
Review action snapshots, locator matches, console and network before changing
the test. Retain the original failing output after any justified test repair.

For variation, add a named Firefox or WebKit project only when that engine is
installed and relevant; run it by its declared project name. Retain engine/version,
viewport and locale in the evidence. A missing engine remains not run.

After a fixture correction, rerun the same test and compare its file hash and
target identity. Do not change the expected price or intercept the API to make a
broken UI pass. Shut down the owned service and confirm cleanup afterward.

Official references: [writing tests](https://playwright.dev/docs/writing-tests),
[fixtures](https://playwright.dev/docs/test-fixtures),
[authentication](https://playwright.dev/docs/auth),
[trace viewer](https://playwright.dev/docs/trace-viewer-intro) and
[trace options](https://playwright.dev/docs/api/class-testoptions#test-options-trace).
