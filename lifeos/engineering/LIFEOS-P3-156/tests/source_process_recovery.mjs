import {test} from 'node:test';import assert from 'node:assert/strict';import {spawn,execFileSync} from 'node:child_process';import {createInterface} from 'node:readline';import {once} from 'node:events';
const binary='/private/tmp/lifeos-p3-156-next-action-v1/target/debug/synthetic-driver';
function host(fixture){const p=spawn(binary,['--synthetic-fixture',fixture],{stdio:['pipe','pipe','pipe']});let n=0;const pending=new Map();createInterface({input:p.stdout}).on('line',l=>{const v=JSON.parse(l),h=pending.get(v.id);if(h){pending.delete(v.id);v.ok?h.resolve(v.result):h.reject(v.error)}});p.on('exit',()=>{for(const h of pending.values())h.reject(Error('synthetic host exited'))});return {pid:p.pid,call:(command,payload)=>new Promise((resolve,reject)=>{const id=++n;pending.set(id,{resolve,reject});p.stdin.write(JSON.stringify({id,command,request:{version:1,payload}})+'\n')}),close:async()=>{const wait=once(p,'exit');p.stdin.end();await wait}}}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
test('independent process restore is read-only until manual resume and request replay is idempotent', {timeout:30000},async()=>{const fixture='p156-source-'+crypto.randomUUID();let h=host(fixture);const pids=[h.pid];try{
 await h.call('connect_source_directory',{requestId:'initial-connect'});
 let s=(await h.call('get_source_status',{})).connectors[0];
 const request={requestId:'manual-pause',connectorId:'directory',expectedGeneration:s.grantGeneration,action:'pause'};
 const first=await h.call('control_source_job',request);assert.deepEqual(await h.call('control_source_job',request),first);
 const before=(await h.call('get_source_status',{})).connectors[0];await h.close();execFileSync('python3',['-c',"import sqlite3,sys; c=sqlite3.connect('file:'+sys.argv[1]+'?mode=rw',uri=True); c.execute(\"INSERT OR REPLACE INTO source_runtime_errors VALUES('directory','source_changed')\"); c.commit(); c.close()",'/private/tmp/lifeos-p3-156-next-action-v1/source-engine/'+fixture+'.sqlite']);h=host(fixture);pids.push(h.pid);assert.notEqual(pids[0],pids[1]);
 const restored=(await h.call('get_source_status',{})).connectors[0];assert.equal(restored.status,'paused');assert.equal(restored.error,'source_changed');assert.equal(restored.jobId,before.jobId);assert.equal(restored.processed,before.processed);
 await pause(100);assert.deepEqual((await h.call('get_source_status',{})).connectors[0],restored);
 await h.call('control_source_job',{requestId:'manual-resume',connectorId:'directory',expectedGeneration:restored.grantGeneration,action:'resume'});
 for(let i=0;i<200;i++){s=(await h.call('get_source_status',{})).connectors[0];if(s.scanComplete&&s.pending===0)break;await pause(50)}assert(s.scanComplete&&s.pending===0);assert(s.parsed>0);assert.equal(s.error,null);
 const versions=s.files.map(f=>[f.sourceRef,f.version]);await h.call('control_source_job',{requestId:'manual-refresh',connectorId:'directory',expectedGeneration:s.grantGeneration,action:'refresh'});
 for(let i=0;i<200;i++){s=(await h.call('get_source_status',{})).connectors[0];if(s.scanComplete&&s.pending===0)break;await pause(50)}assert.deepEqual(s.files.map(f=>[f.sourceRef,f.version]),versions);assert(s.updateCounts.unchanged>0);
}finally{await h.close()}});
