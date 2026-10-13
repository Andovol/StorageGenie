// Offline independent audit of immutable stored evidence. No browser or network.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const j = JSON.parse(fs.readFileSync('docs/worklogs/SG-183_measure.json'));
const controls = JSON.parse(fs.readFileSync('docs/worklogs/SG-183_controls.json')).controls;
assert.equal(controls.controls.length, 9);
assert(controls.controls.every(c => c.ok === true));
assert(controls.contrastKnown.some(c => c.ok === false));
const counts = {}, dispositions = {}, contrast = [];
for (const row of j.app.routes) {
  const m = row.measure;
  assert.equal(m.docOverflowX, m.docEl_scrollWidth - m.docEl_clientWidth);
  const c = counts[row.viewport] ||= { samples: 0, overflow: 0 };
  c.samples++; c.overflow += m.docOverflowX > 0;
  for (let i = 0; i < (m.targets || []).length; i++) {
    const r = m.targets[i].rect;
    const small = r.width < 24 || r.height < 24;
    let overlaps = false;
    const x = r.left + r.width/2, y = r.top + r.height/2;
    for (let k = 0; k < m.targets.length; k++) {
      if (k === i) continue;
      const o = m.targets[k].rect;
      const edge = Math.hypot(Math.max(o.left-x,0,x-o.right),Math.max(o.top-y,0,y-o.bottom));
      const centers = Math.hypot(x-(o.left+o.width/2),y-(o.top+o.height/2));
      overlaps ||= edge < 12 || ((o.width < 24 || o.height < 24) && centers < 24);
    }
    const expected = !small ? 'PASS-SIZE' : !overlaps ? 'PASS-SPACING' : 'FAIL';
    assert.equal(row.targetDispositions[i].disposition, expected);
    dispositions[expected] = (dispositions[expected] || 0) + 1;
  }
  for (const t of m.contrast || []) if (t.passesAA === false) contrast.push(t);
}
assert.equal(counts['390x844'].overflow, 10);
assert.equal(counts['834x1112'].overflow, 9);
assert.equal(counts['1440x900'].overflow, 0);
function luminance(rgb) {
  return rgb.map(c => c/255).map(c => c <= .04045 ? c/12.92 : ((c+.055)/1.055)**2.4)
    .reduce((sum,c,i) => sum+c*[.2126,.7152,.0722][i],0);
}
const ratio = (luminance([245,245,244])+.05)/(luminance([120,113,108])+.05);
assert(ratio < 4.5 && Math.abs(ratio-4.3977) < .0001);
assert(contrast.length > 0);
console.log(JSON.stringify({counts,dispositions,belowAASamples:contrast.length,independentRatio:ratio,
  limitations:['stored evidence only','focus probe prevents native scrolling','alpha control has tautological branch','sampled targets only']},null,2));
