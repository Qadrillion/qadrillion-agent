const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
async function verify(request) {
  const file = path.resolve(process.env.QA_IDENTITY || 'target.json');
  const expected = JSON.parse(fs.readFileSync(file, 'utf8'));
  const url = new URL(expected.url);
  assert.equal(url.hostname, '127.0.0.1');
  assert.equal(url.protocol, 'http:');
  assert.equal(expected.role, 'test');
  assert.equal(expected.fixture, 'qadrillion-specialist-lab');
  const response = await request.get(`${expected.url}/__identity`, { maxRedirects: 0 });
  assert.equal(response.status(), 200);
  assert.deepEqual(await response.json(), expected);
  return expected;
}
module.exports = { verify };
