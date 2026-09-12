import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ControlledConversation} from '../candidate/ui/controlled_conversation.js';
const applied={action:{id:'action:fixture',version:1},eventRef:'event:fixture',operation:'create'};
const condition={id:'condition:fixture',version:1};
const status=result=>({state:'committed',turnRequestId:'turn:fixture',turnId:'draft:fixture',businessChanged:result.businessChanged,receipt:{operationId:'operation:fixture',turnRequestId:'turn:fixture',turnId:'draft:fixture',state:'committed',committedAt:123,reply:'公开合成本地回执',result}});
const confirm=t=>new ControlledConversation({invoke:async()=>({version:8,operation:'confirm_coordination_model',result:t})}).confirm({requestId:'turn:fixture',previewId:'preview:fixture',revision:1});
const valid=[{kind:'none',businessChanged:false},{kind:'clarify',businessChanged:false,question:'是哪一项？'},{kind:'action',businessChanged:true,applied},{kind:'condition_only',businessChanged:true,condition,truth:'unknown',reason:'condition_unknown'},{kind:'condition_only',businessChanged:true,condition,truth:'false',reason:'condition_false'},{kind:'condition_only',businessChanged:true,condition,truth:'true',reason:'record_only'},{kind:'condition_and_action',businessChanged:true,condition,truth:'true',applied}];
for(const result of valid)test(`valid receipt ${result.kind}/${result.truth||''}/${result.reason||''}`,async()=>assert.equal((await confirm(status(result))).state,'succeeded'));
const mutations=[
 ['wrong-turn',t=>t.receipt.turnId='other'],
 ['wrong-operation-identity',t=>t.receipt.operationId=null],
 ['missing-event',t=>delete t.receipt.result.applied.eventRef],
 ['invalid-action-version',t=>t.receipt.result.applied.action.version=0],
 ['unexpected-permission',t=>t.receipt.result.permission='allow-all'],
 ['false-action-condition',t=>t.receipt.result.truth='false'],
 ['false-business-change',t=>t.receipt.result.businessChanged=false],
 ['inconsistent-status',t=>t.businessChanged=false],
 ['extra-receipt-field',t=>t.receipt.raw='untrusted-success'],
 ['oversized-reply',t=>t.receipt.reply='甲'.repeat(2001)],
];
for(const [name,mutate] of mutations)test(`production confirm rejects ${name} before success`,async()=>{const t=structuredClone(status(valid.at(-1)));mutate(t);await assert.rejects(confirm(t),e=>e.code==='dto_rejected')});
test('none cannot disguise an action event',async()=>{const t=status({kind:'none',businessChanged:false,applied});await assert.rejects(confirm(t),e=>e.code==='dto_rejected')});
test('condition-only reason must agree with truth',async()=>{const t=status({kind:'condition_only',businessChanged:true,condition,truth:'true',reason:'condition_unknown'});await assert.rejects(confirm(t),e=>e.code==='dto_rejected')});

test('retry preparation preserves terminal provider failure without another send',async()=>{
 const calls=[];const app=new ControlledConversation({invoke:async(command,r)=>{calls.push(r.operation);const result=r.operation==='save_coordination_draft'?{draftRevision:1}:r.operation==='prepare_coordination_turn'?{turn:{turnRequestId:'turn:failed'}}:{turnRequestId:'turn:failed',state:'failed',errorCode:'provider_response_truncated'};return {version:8,operation:r.operation,result};}});
 assert.deepEqual(await app.prepare({requestId:'draft:request',turnId:'draft:failed',text:'公开合成查询',revision:1},()=>true),{kind:'terminal',errorCode:'provider_response_truncated'});assert.equal(calls.includes('confirm_coordination_model'),false);
});
