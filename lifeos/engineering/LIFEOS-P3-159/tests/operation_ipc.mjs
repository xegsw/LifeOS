import {test} from 'node:test';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';import {createInterface} from 'node:readline';import {once} from 'node:events';import {writeFileSync} from 'node:fs';
import {V7ControlledConversation as ControlledConversation,ControlledFlow} from '../candidate/ui/controlled_conversation.js';
const root='/private/tmp/lifeos-p3-159-unified-proactive-v1/offline';
function host(fixture='p158-v7-'+crypto.randomUUID()){const p=spawn('/private/tmp/lifeos-p3-159-unified-proactive-v1/build/offline/debug/synthetic-driver',['--synthetic-fixture',fixture],{stdio:['pipe','pipe','pipe']});let next=0;const pending=new Map();createInterface({input:p.stdout}).on('line',line=>{const v=JSON.parse(line),x=pending.get(v.id);pending.delete(v.id);v.ok?x.resolve(v.result):x.reject(v.error)});p.on('exit',()=>{for(const x of pending.values())x.reject(Error('host exited'));pending.clear()});return {fixture,invoke(command,request){return new Promise((resolve,reject)=>{pending.set(++next,{resolve,reject});p.stdin.write(JSON.stringify({id:next,command,request})+'\n')})},async close(){p.stdin.end();await once(p,'exit')}};}
const expressions=['明天下午去健身房','挪到后天吧','先不去健身房了','聊一聊合成展览'];
const span=q=>[{messageRef:'current',start:0,end:Array.from(q).length}];
const response=candidate=>({schemaVersion:1,answerText:'模型声称已完成，这不具有事务权威。',candidate});
writeFileSync(root+'/operation-responses.json',JSON.stringify({
 [expressions[0]]:response({operation:'create',content:expressions[0],evidenceSpans:span(expressions[0]),sourceRefs:[]}),
 [expressions[1]]:response({operation:'adjust',targetRef:'T1',expectedVersion:1,content:'后天下午去健身房',evidenceSpans:span(expressions[1]),sourceRefs:[]}),
 [expressions[2]]:response({operation:'cancel',targetRef:'T1',expectedVersion:2,evidenceSpans:span(expressions[2])}),
 [expressions[3]]:response({operation:'none'})
}),{mode:0o600});
async function ready(app){await app.saveCredential('p158-offline-fictional-key',0);await app.testModels();await app.selectModel('user-synthetic-model');await app.setEnabled(true);}
test('historical v7 IPC and shared Flow create adjust cancel and independent process restart',async()=>{let h=host(),flow;try{let app=new ControlledConversation(h);await ready(app);flow=new ControlledFlow(app,()=>{});await flow.start();let id;
 for(let i=0;i<3;i++){flow.edit(expressions[i]);await flow.prepare();assert.equal(flow.phase,'awaiting-confirmation');assert.equal(flow.preview.version,7);assert.equal(flow.snapshot.actions.length,i?1:0);await flow.confirm();assert.equal(flow.phase,'idle',JSON.stringify(flow.error));assert.equal(flow.snapshot.actions.length,1);const a=flow.snapshot.actions[0];id??=a.id;assert.equal(a.id,id);assert.equal(a.version,i+1);assert.equal(a.status,i===2?'cancelled':'planned');assert(!flow.snapshot.turns.at(-1).answer.includes('模型声称'));}
 const before=flow.snapshot.actions;flow.dispose();const fixture=h.fixture;await h.close();h=host(fixture);app=new ControlledConversation(h);flow=new ControlledFlow(app,()=>{});await flow.start();assert.deepEqual(flow.snapshot.actions,before);assert.equal(flow.snapshot.turns.length,3);
 }finally{flow?.dispose();await h.close()}});
test('ordinary conversation uses same v7 and explicitly reports no operation',async()=>{const h=host();try{const app=new ControlledConversation(h);await ready(app);const flow=new ControlledFlow(app,()=>{});await flow.start();flow.edit(expressions[3]);await flow.prepare();await flow.confirm();assert.equal(flow.snapshot.actions.length,0);assert.match(flow.snapshot.turns.at(-1).answer,/本轮未更改安排/);flow.dispose();}finally{await h.close()}});
