import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {once} from 'node:events';
import {HealthConversation} from '../candidate/ui/health_conversation.js';
import {chooseContext,interpretation,sourceAvailability,minutes} from '../candidate/ui/health_context.js';
const binary='/private/tmp/lifeos-p3-155-source-update-v1/target/debug/synthetic-driver';
const results=[];let restartEvidence;
async function test(name,f){try{await f();results.push({name,pass:true})}catch(e){results.push({name,pass:false,error:e.stack||JSON.stringify(e)})}}
function host(fixture){const p=spawn(binary,['--synthetic-fixture',fixture],{stdio:['pipe','pipe','pipe']});let seq=0,errors='';const pending=new Map();p.stderr.on('data',b=>errors+=b);p.on('exit',()=>{for(const h of pending.values()){clearTimeout(h.timer);h.reject(Error('driver exited '+errors))}});createInterface({input:p.stdout}).on('line',l=>{const v=JSON.parse(l),h=pending.get(v.id);if(!h)return;pending.delete(v.id);clearTimeout(h.timer);v.ok?h.resolve(v.result):h.reject(v.error)});return {pid:p.pid,invoke:(command,request)=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('IPC timeout'));p.kill()},10000);pending.set(id,{resolve,reject,timer});p.stdin.write(JSON.stringify({id,command,request})+'\n')}),close:async()=>{const done=once(p,'exit');p.stdin.end();await done}}}
const draft=text=>({requestId:crypto.randomUUID(),turnId:crypto.randomUUID(),revision:1,text});
const fixture=()=>`p155-${crypto.randomUUID()}`;
async function send(a,text){const d=draft(text);await a.answer(d,()=>true);return d;}
// Any accidental model fetch is a test failure, not a silently mocked success.
let networkCalls=0;globalThis.fetch=()=>{networkCalls++;throw Error('network forbidden')};
await test('independent process reopen preserves answered state, raw refs and adapter continuity',async()=>{
 const name=fixture();let h=host(name),a=new HealthConversation(h);const pids=[h.pid];
 try{
  await send(a,'健康活动怎么安排');let s=await a.read();assert.equal(s.questions.length,1);const qid=s.questions[0].id;
  const reply=await send(a,'我有20分钟');s=await a.read();assert.equal(s.questions.find(q=>q.id===qid).status,'answered');assert.equal(s.states[0].value,20);
  const persisted=structuredClone(s);await h.close();h=host(name);pids.push(h.pid);a=new HealthConversation(h);s=await a.read();assert.deepEqual(s,persisted);assert.notEqual(...pids);
  const observations=[];for(const model of ['OfflineA','OfflineB']){await a.select(model);const adapter=a.models[model],generate=adapter.generate.bind(adapter);adapter.generate=async(p,c,d)=>{observations.push({model,refs:c.inputRefs,states:c.states.map(x=>({rawId:x.rawId,value:x.value})),decision:d});return generate(p,c,d)};await send(a,'请建议健康活动');}
  assert.deepEqual(observations[0].refs,observations[1].refs);assert.deepEqual(observations[0].states,observations[1].states);assert.equal(observations[1].decision.clarification,undefined);assert(observations[1].refs.some(r=>r.id==='raw:'+reply.turnId));
  const fix=await send(a,'纠正，改为5分钟');s=await a.read();assert.equal(s.states[0].value,5);assert(s.turns.some(t=>t.turnId===reply.turnId&&t.text==='我有20分钟'&&t.status==='stale'));assert(s.turns.some(t=>t.status==='stale'));
  await h.close();h=host(name);pids.push(h.pid);a=new HealthConversation(h);assert.equal((await a.read()).states[0].value,5);await send(a,'健康活动怎么安排');s=await a.read();assert.match(s.turns.at(-1).answer,/5 分钟/);assert(s.turns.at(-1).refs.some(r=>r.id==='raw:'+fix.turnId));assert(!s.turns.at(-1).refs.some(r=>r.id==='raw:'+reply.turnId));
  restartEvidence={pids,fixture:name};
 }finally{await h.close()}
});
await test('failure preserves raw draft and retry once commits once under concurrency',async()=>{const h=host(fixture()),a=new HealthConversation(h);try{const d=draft('我的睡眠记录 [模拟失败]');await assert.rejects(a.answer(d,()=>true));assert.equal((await a.read()).pendingDraft.text,d.text);await Promise.all([a.answer(d,()=>true),a.answer(d,()=>true)]);assert.equal((await a.read()).turns.length,1)}finally{await h.close()}});
await test('hypothetical time and observation duration never become user state',async()=>{const h=host(fixture()),a=new HealthConversation(h);try{await send(a,'如果我有20分钟运动会怎样');assert.equal((await a.read()).states.length,0);await send(a,'我的睡眠记录是什么');const s=await a.read();assert.equal(s.states.length,0);assert.equal(s.questions.length,0);assert.match(s.turns.at(-1).answer,/360/)}finally{await h.close()}});
await test('authorized selected source availability answers gap; denied, conflicting and irrelevant excluded',async()=>{
 const now=Date.now(),packet={domain:'work',question:'请建议工作安排',now,questions:[],snapshot:{records:[],states:[],memories:[],sources:[{id:'ok',authorized:true,generation:1},{id:'denied',authorized:false,generation:1}],feedback:[],derivations:[]}};
 const row=(id,text,sourceId='ok')=>({id,text,sourceId,domain:'work',kind:'source_projection',status:'active',version:1,observedAt:now,validUntil:now+60000});
 packet.snapshot.records=[row('known','工作安排：我有20分钟'),row('denied','工作安排：我有90分钟','denied')];let c=chooseContext(packet);assert.equal(sourceAvailability(c),20);assert.equal(interpretation(packet,c).clarification,undefined);assert(!c.inputRefs.some(r=>r.id==='denied'));
 packet.snapshot.records=[row('observe','工作安排：运动区间为20分钟')];c=chooseContext(packet);assert.equal(sourceAvailability(c),null);assert.equal(interpretation(packet,c).clarification.field,'available_time');
 packet.snapshot.records=[row('a','工作安排：我有20分钟'),row('b','工作安排：我有30分钟')];c=chooseContext(packet);assert.equal(sourceAvailability(c),null);assert.equal(interpretation(packet,c).clarification.field,'available_time');
 packet.question='解释是什么';c=chooseContext(packet);assert.equal(c.inputRefs.length,0);assert.equal(interpretation(packet,c).clarification,undefined);
});

await test('reject survives more than eight new question instances and process restart, explicit reopen answers once',async()=>{
 const name=fixture();let h=host(name),a=new HealthConversation(h);
 try{
  await send(a,'健康活动怎么安排');const qid=(await a.read()).questions[0].id;await a.decision(qid,'reject');
  for(let i=0;i<12;i++){await send(a,`工作报告怎么安排 ${i}`);const q=(await a.read()).questions.find(q=>q.domain==='work');await a.decision(q.id,'ignore');}
  const before=await a.read();assert.equal(before.questions.find(q=>q.id===qid).status,'rejected');assert.equal(before.states.length,0);
  await h.close();h=host(name);a=new HealthConversation(h);assert.deepEqual(await a.read(),before);
  await send(a,'请建议健康活动');let state=await a.read();assert.equal(state.questions.find(q=>q.id===qid).status,'rejected');assert.equal(state.turns.at(-1).clarificationId,null);
  const request={requestId:crypto.randomUUID(),questionId:qid,decision:'reopen'};await Promise.all([a.call('decide_understanding_feedback','clarification_decision',request),a.call('decide_understanding_feedback','clarification_decision',request)]);
  await send(a,'15分钟');state=await a.read();assert.equal(state.states[0].value,15);assert.equal(state.questions.find(q=>q.id===qid).status,'answered');assert.equal(state.memories.length,2);
 }finally{await h.close()}
});
await test('defer survives independent restart without a prompt or state write',async()=>{const name=fixture();let h=host(name),a=new HealthConversation(h);try{await send(a,'健康活动怎么安排');const q=(await a.read()).questions[0];await a.decision(q.id,'defer');const before=await a.read();assert(before.questions[0].resumeAt>Date.now());await h.close();h=host(name);a=new HealthConversation(h);assert.deepEqual(await a.read(),before);await send(a,'请建议健康活动');const s=await a.read();assert.equal(s.questions[0].status,'deferred');assert.equal(s.turns.at(-1).clarificationId,null);assert.equal(s.states.length,0);await send(a,'20分钟');const answered=await a.read();assert.equal(answered.states[0].value,20);assert.equal(answered.questions[0].status,'answered')}finally{await h.close()}});
await test('ignore is only this occurrence; next request has a distinct question and preserves old turn',async()=>{const h=host(fixture()),a=new HealthConversation(h);try{await send(a,'健康活动怎么安排');const q=(await a.read()).questions[0];await a.decision(q.id,'ignore');const before=await a.read();assert.equal(before.states.length,0);assert.equal(before.questions[0].status,'ignored');await send(a,'健康活动怎么安排');const s=await a.read();assert.notEqual(s.questions[0].id,q.id);assert.equal(s.questions[0].status,'pending');assert.equal(s.turns[0].clarificationId,q.id);assert.equal(s.turns.length,2)}finally{await h.close()}});
await test('already answered, rejected, deferred and silence cannot be confused',async()=>{
 const now=Date.now(),packet={turnId:'new',question:'请建议工作安排',domain:'work',now,snapshot:{states:[]},questions:[]},context={included:[{layer:'L3',text:'工作项目：准备报告'}]};
 for(const status of ['rejected','pending','deferred']){packet.questions=[{id:'q',field:'available_time',domain:'work',status,resumeAt:now+1,basisTurn:'old'}];assert.equal(interpretation(packet,context).clarification,undefined);}
 packet.questions=[{id:'q',field:'available_time',domain:'work',status:'deferred',resumeAt:now-1}];assert.equal(interpretation(packet,context).clarification.field,'available_time');
 packet.questions=[{id:'q',field:'available_time',domain:'work',status:'ignored',basisTurn:'new'}];assert.equal(interpretation(packet,context).clarification,undefined);
 const before=structuredClone(packet);interpretation(packet,context);assert.deepEqual(packet,before);for(const text of ['我有-5分钟','我有2.5分钟','我有1020分钟'])assert.equal(minutes(text),null);
});
assert.equal(networkCalls,0);console.log(JSON.stringify({passed:results.filter(r=>r.pass).length,total:results.length,networkCalls,restartEvidence,results},null,2));if(results.some(r=>!r.pass))process.exitCode=1;
