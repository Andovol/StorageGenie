// Close verification. Run from repo root; output names immutable snapshot layers.
const fs=require('node:fs'), cp=require('node:child_process'), assert=require('node:assert/strict');
const git=(...a)=>cp.execFileSync('git',a,{maxBuffer:12*1024*1024});
const text=(b)=>new TextDecoder('utf-8',{fatal:true}).decode(b);
const controls=(b)=>[...text(b).matchAll(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g)].length;
const normal=fs.readFileSync('README.md'); assert.equal(controls(normal),0);
assert.equal(controls(Buffer.concat([normal,Buffer.from([0])])),1);
const old=git('show','9d2554c:STATE.md'), marker=Buffer.from('**Index (append-only retirement):**');
const cut=old.indexOf(marker); assert(cut>0);
const archived=git('show','HEAD:docs/history/2026-10-13-state-decisions-preserved.md');
assert.deepEqual(archived,old.subarray(cut));
const raw=fs.readFileSync('.git/session-transfer-state-before.bin');
assert.deepEqual(fs.readFileSync('docs/history/2026-10-13-state-decisions-preserved.md'),raw.subarray(3360));
const changed=text(git('diff','--name-only','3454e1c','HEAD')).trim().split('\n');
const checked=[], exceptions=[], preserved=[];
const ratingOld=git('show','3454e1c:docs/ratings.md');
const moji=/\u00e2\u20ac[\u201c\u201d\u2018\u2019]|\u00c3[\u0080-\u00bf]/g;
const sgr=/\x1b\[[0-9;]*m/g;
const styledControl=Buffer.concat([normal,Buffer.from([27]),Buffer.from('[31m')]);
assert.equal(controls(styledControl),1); assert.equal(controls(Buffer.from(text(styledControl).replace(sgr,''))),0);
for(const p of changed.filter(p=>/\.(md|py|tsx?|jsx?|mjs|cjs|json|log|ya?ml)$/.test(p))){
  const b=git('show',`HEAD:${p}`);
  try {
    const count=controls(b), s=text(b);
    if(count && p.endsWith('.log') && controls(Buffer.from(s.replace(sgr,'')))===0){
      const sequences=[...s.matchAll(sgr)].length; assert.equal(sequences,count);
      preserved.push({path:p,kind:'raw ANSI SGR terminal capture; original bytes preserved',sequences});
    } else assert.equal(count,0,p);
  }
  catch(e){exceptions.push({path:p,problem:String(e.message)}); continue;}
  const s=text(b);
  if([...s.matchAll(moji)].length){
    if(p==='docs/ratings.md' && b.subarray(0,ratingOld.length).equals(ratingOld)
      && [...s.matchAll(moji)].length===[...text(ratingOld).matchAll(moji)].length)
      preserved.push({path:p,kind:'inherited ratings mojibake; old Git prefix byte-identical; REC-ISS33',matches:[...s.matchAll(moji)].length});
    else exceptions.push({path:p,problem:'possible newly introduced mojibake; inspect stored bytes'});
  }
  checked.push(p);
}
assert.equal(exceptions.length,0,JSON.stringify(exceptions));
const head=text(git('rev-parse','HEAD')).trim(), previous='3454e1c';
const size=(ref,p)=>git('show',`${ref}:${p}`).length;
const rulesOld=cp.execFileSync('git',['-C','.rules-cache','show','contract-v0.46.0:RULES.md']);
const rulesNow=fs.readFileSync('C:/Users/popes/.codex/AGENTS.md');
const arch=fs.readFileSync('.rules-cache/ARCHITECT.md');
const entries=['AGENTS.md','CLAUDE.md','STATE.md'];
const table=Object.fromEntries(entries.map(p=>[p,{previous:size(previous,p),closingSnapshot:size(head,p),workingBytes:fs.statSync(p).size}]));
const oldBasis=rulesOld.length+arch.length+entries.reduce((n,p)=>n+table[p].previous,0);
const newBasis=rulesNow.length+arch.length+entries.reduce((n,p)=>n+table[p].closingSnapshot,0);
function totals(ref){const rows=text(git('ls-tree','-r','-l',ref)).trim().split('\n');
 const values=rows.map(l=>Number(l.match(/^\d+ blob [0-9a-f]+\s+(\d+)\t/)[1]));
 return {snapshot:ref,trackedBlobCount:values.length,trackedBlobBytes:values.reduce((a,b)=>a+b,0)};}
const refs=['docs/decisions/2026-10-13-fresh-session-transfer.md','docs/decisions/2026-10-13-contract-0.47-adoption-plan.md',
 'docs/reviews/2026-10-13-recovery-audit.md','docs/reviews/2026-10-13-user-scenarios.md','docs/reviews/2026-10-13-recovery-plan.md',
 'docs/packets/SG-181-api-domain-recovery-audit.md','docs/packets/SG-182-operations-test-trust-consolidation-audit.md',
 'docs/worklogs/SG-175_audit.md','docs/worklogs/SG-179_audit.md','docs/worklogs/SG-183_audit.md','docs/worklogs/SG-180_audit.md'];
assert(refs.every(p=>fs.existsSync(p)));
const ratings=text(git('show','HEAD:docs/ratings.md'));
for(const id of ['SG-175','SG-179','SG-183','SG-180']){const row=ratings.split('\n').find(l=>l.startsWith(`| ${id} |`));
 assert(row,id); const cells=row.split('|').slice(1,-1).map(s=>s.trim()); assert(cells.length>=11); assert(cells[9],`${id} remaining`);}
const out={measurement:'canonical immutable Git snapshots, installed rules raw bytes, working bytes separately; not tokens/ingestion',
 previous,closingRecordsSnapshot:head,entries:table,rulesPreviousBytes:rulesOld.length,rulesInstalledBytes:rulesNow.length,
 mandatoryArchitectBytes:arch.length,coldStartBasisPrevious:oldBasis,coldStartBasisClosing:newBasis,change:newBasis-oldBasis,
 largestGrowingEntry:[...Object.entries(table).map(([p,v])=>({path:p,change:v.closingSnapshot-v.previous})),{path:'installed Codex AGENTS rules',change:rulesNow.length-rulesOld.length}].sort((a,b)=>b.change-a.change)[0],
 repository:[totals(previous),totals(head)],preservedHistoryGitBytes:archived.length,preservedHistoryWorkingBytes:8449,
 rawConservation:'3360+8449=11809',textFilesChecked:checked.length,controlProbe:'untouched README clear; planted byte0 detected',
 textExceptions:exceptions,preservedExceptions:preserved,currentReferencesExist:true,ratingRemainingFields:true,
 contextTokens:'unavailable',platformCost:'unavailable'};
fs.writeFileSync('docs/worklogs/2026-10-13-transfer-verification.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({head,coldStart:oldBasis+' -> '+newBasis,change:out.change,archiveEquality:true,textFilesChecked:checked.length,exceptions:exceptions.length}));
