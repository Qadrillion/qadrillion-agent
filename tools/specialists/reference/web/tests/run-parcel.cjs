const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const identity = path.resolve(process.argv[2] || path.join(root, 'target.json'));
const out = path.join(root, 'artifacts', `parcel-${Date.now()}`);
fs.mkdirSync(out, { recursive: true });
const version = require('@playwright/test/package.json').version;
if (version !== '1.63.0') throw Error(`Expected Playwright 1.63.0, found ${version}`);
const evidence = { identityFile: identity, node: process.version, platform: os.platform(), release: os.release(), arch: os.arch(), playwright: version, cwd: root, testsHash: crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname, 'parcel.spec.js'))).digest('hex'), commands: [] };
let failed = false;
for (const browser of ['chromium', 'firefox']) {
 const args = [require.resolve('@playwright/test/cli'), 'test', '-c', 'tests', '--browser='+browser, '--workers=1', '--retries=0', '--trace=on', '--output='+path.join(out,browser), '--reporter=list,json'];
 const started = new Date().toISOString();
 const result = spawnSync(process.execPath, args, { cwd: root, env: { ...process.env, QA_IDENTITY: identity, PLAYWRIGHT_JSON_OUTPUT_NAME: path.join(out, browser+'.json') }, encoding:'utf8' });
 fs.writeFileSync(path.join(out,browser+'.log'), (result.stdout || '')+(result.stderr || ''));
 evidence.commands.push({ executable:process.execPath,args,started,finished:new Date().toISOString(),exit:result.status,error:result.error?.message });
 if (result.status !== 0) failed = true;
}
fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify(evidence,null,2));
console.log(out);
process.exitCode = failed ? 1 : 0;
