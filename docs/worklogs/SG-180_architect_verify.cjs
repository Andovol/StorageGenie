// Independent offline raw-evidence audit; no application imports or network.
const fs = require('node:fs'), assert = require('node:assert/strict');
const data = {};
for (const g of ['g1','g2','g3']) {
  // Normalize log separators only for JSON framing; original evidence files unchanged.
  const raw = fs.readFileSync(`docs/worklogs/SG-180_${g}_run_2026-10-13.log`, 'utf8').replace(/\r\n/g,'\n');
  const start = raw.indexOf('{\n  "results"');
  const end = raw.lastIndexOf('\n}');
  assert(start >= 0 && end > start);
  const j = JSON.parse(raw.slice(start,end+2));
  assert(j.results.length > 0);
  assert(!j.results.some(r => r.result === 'FAIL'));
  data[g] = j;
}
function check(g,n) { const v = data[g].results.find(r => r.check === n); assert(v,n); return v; }
assert.equal(check('g1','cross_household_sha_dedup').b_get_status,403);
assert.equal(check('g1','cross_household_idempotency_replay').b_returned_a_row,true);
assert.equal(check('g1','counter_control_b_own_bytes_own_row').result,'PASS');
const corrupt = check('g1','same_size_corruption_served');
assert.equal(corrupt.status,200); assert.notEqual(corrupt.served_sha256,corrupt.db_sha256);
assert.equal(check('g1','missing_original_controls').file_status,404);
assert.equal(check('g3','wire_payload_envelope').result,'PASS');
assert.equal(check('g3','ledger_input_hash_is_redacted_sha').result,'PASS');
console.log(JSON.stringify(Object.fromEntries(Object.entries(data).map(([g,j])=>[g,{
  checks:j.results.length,dispositions:j.results.reduce((o,r)=>(o[r.result]=(o[r.result]||0)+1,o),{})
}])) ,null,2));
console.log('Stored evidence checks agree with named controls; not a local backend rerun or full-suite pass.');
