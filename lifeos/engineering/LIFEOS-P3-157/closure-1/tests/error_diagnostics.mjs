import {test} from 'node:test';import assert from 'node:assert/strict';
import {errorText,withFailureStage} from '../candidate/ui/health_errors.js';
import {ControlledConversation,ControlledFlow} from '../candidate/ui/controlled_conversation.js';
test('fixed codes distinguish storage, local commit and remote parser without raw error disclosure',()=>{
 for(const [stage,code] of [['prepare_turn','readonly_sidecar_required'],['prepare_turn','database_unavailable'],['commit_turn','clarification_rejected'],['confirm_send','provider_protocol'],['confirm_send','response_too_large'],['confirm_send','credential_unavailable'],['confirm_send','credential_reference_rejected'],['confirm_send','confirmation_rejected'],['confirm_send','confirmation_storage_failed'],['confirm_send','response_storage_failed']]){
 const text=errorText({code,stage,message:'PRIVATE_BODY_KEY_CANARY',body:'PRIVATE_BODY_KEY_CANARY'});assert(text.includes(code));assert(!text.includes('PRIVATE_BODY_KEY_CANARY'));
 }
});
test('unknown codes, inherited properties and arbitrary stages never render',()=>{
 for(const code of ['secret-text','constructor','toString','__proto__']){const text=errorText({code,stage:'PRIVATE_CANARY',message:'PRIVATE_CANARY'});assert(text.includes('operation_failed'));assert(!text.includes('PRIVATE_CANARY'));assert(!text.includes(code+'）'));}
});
test('actual application IPC wrapper preserves stage and excludes raw messages',async()=>{
 const a=new ControlledConversation({invoke:async()=>{throw {code:'clarification_rejected',message:'PRIVATE_CANARY'}}});
 await assert.rejects(a.call('resolve_request_context','commit_turn',{}),e=>e.code==='clarification_rejected'&&e.stage==='commit_turn'&&!('message' in e));
 await assert.rejects(a.call5('resolve_request_context','prepare_disclosure',{}),e=>e.stage==='prepare_disclosure');
});
test('prepare failure preserves draft and performs zero confirmation calls',async()=>{
 let sends=0;const a={read:async()=>({revision:0,pendingDraft:null}),prepare:async()=>{throw {code:'database_unavailable',stage:'prepare_turn'}},draft:async()=>{},confirm:async()=>{sends++}};
 const f=new ControlledFlow(a,()=>{});await f.start();f.edit('合成旧库问题');await f.prepare();assert.equal(f.phase,'failed');assert.equal(f.draft.text,'合成旧库问题');assert.equal(f.error.stage,'prepare_turn');assert.equal(sends,0);f.dispose();
});
test('remote protocol failure stays failed and does not automatically re-confirm',async()=>{
 let sends=0;const a={read:async()=>({revision:0,pendingDraft:null}),draft:async()=>{},prepare:async()=>({kind:'preview',preview:{previewId:'synthetic-preview'}}),confirm:async()=>{sends++;return {state:'failed',errorCode:'provider_protocol'}}};
 const f=new ControlledFlow(a,()=>{});await f.start();f.edit('合成响应问题');await f.prepare();await f.confirm();assert.equal(f.phase,'failed');assert.equal(f.error.stage,'confirm_send');assert.equal(f.draft.text,'合成响应问题');assert.equal(f.preview,null);await f.confirm();assert.equal(sends,1);f.dispose();
});

test('fixed code survives object or bounded string IPC envelope without raw fields',async()=>{
 for(const value of [{code:'source_identity_rejected',message:'PRIVATE_CANARY'},JSON.stringify({code:'source_identity_rejected',message:'PRIVATE_CANARY'}),'source_identity_rejected']){
 await assert.rejects(withFailureStage('prepare_turn',async()=>{throw value}),e=>e.code==='source_identity_rejected'&&e.stage==='prepare_turn'&&!JSON.stringify(e).includes('PRIVATE_CANARY'));
 }
 for(const value of [{code:'PRIVATE_CANARY'},'PRIVATE_CANARY',{message:'PRIVATE_CANARY'},JSON.stringify({message:'PRIVATE_CANARY'}),'x'.repeat(3000)]){
 await assert.rejects(withFailureStage('prepare_turn',async()=>{throw value}),e=>['unrecognized_host_error','ipc_error_envelope_invalid'].includes(e.code)&&!errorText(e).includes('PRIVATE_CANARY'));
 }
});
