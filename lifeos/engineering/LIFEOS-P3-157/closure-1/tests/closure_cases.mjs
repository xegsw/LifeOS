import {test} from 'node:test';import assert from 'node:assert/strict';
import {classifyAction,actionCandidate} from '../candidate/ui/action_domain.js';
import {ActionApplication} from '../candidate/ui/action_application.js';
import {ControlledConversation,ControlledFlow} from '../candidate/ui/controlled_conversation.js';
const a={id:'a',version:1,confirmedContent:'我明天先买合成材料',status:'planned',sourceRefs:[]};
const packet=(raw,actions=[])=>({id:'p',raw,actions,suggestions:[],expiresAt:Date.now()+100000,revision:1});
const cases=[
['strong-frame-unlisted-verb','我明天先买合成材料。',[],'supported_action','create'],
['strong-frame-another-verb','我接下来先寄合成样品。',[],'supported_action','create'],
['word-internal-negation','我明天先买不锈钢合成材料。',[],'supported_action','create'],
['withdraw-unique','先不买合成材料了。',[a],'supported_action','cancel'],
['withdraw-no-target','先不买合成材料了。',[],'unsupported_action',undefined],
['withdraw-multiple','先不买合成材料了。',[a,{...a,id:'b',confirmedContent:'我今天先买合成材料'}],'ambiguous_action','clarify'],
['negative-new-intent','我不打算买合成材料。',[],'chat',undefined],
['negative-not-withdrawal','我不打算买合成材料。',[a],'chat',undefined],
['cancelled-target','先不买合成材料了。',[{...a,status:'cancelled'}],'unsupported_action',undefined],
['finished-target','先不买合成材料了。',[{...a,status:'completed'}],'unsupported_action',undefined],
['quoted-withdrawal','他说“先不买合成材料了”。',[a],'chat',undefined],
['hypothetical','如果先不买合成材料了，会怎样？',[a],'chat',undefined],
['question','我明天先买合成材料好吗？',[],'chat',undefined],
['uncertain','我明天可能先买合成材料。',[],'unsupported_action',undefined],
['conflicting-clauses','我明天先买合成材料，但还没决定。',[],'unsupported_action',undefined],
['unsupported-explicit','帮我把这件事安排一下。',[],'unsupported_action',undefined],
['ordinary-chat','今天聊天挺有意思。',[a],'chat',undefined],
['cloud-affirmation','好的，已经安排好了。',[],'chat',undefined]
];
for(const [id,raw,actions,kind,op] of cases)test(id,()=>{const r=classifyAction(packet(raw,actions));assert.equal(r.kind,kind);assert.equal(r.candidate?.operation,op)});
test('parse-none cannot fall into chat for explicit intent',async()=>{let commits=0;const app=new ActionApplication({prepare:async()=>packet('我明天先买合成材料。'),commit:async()=>commits++},{id:'OfflineA',parse:async()=>undefined});const r=await app.submit({turnId:'t',revision:1},()=>true);assert.equal(r.kind,'unsupported');assert.equal(commits,0)});
function mocked(raw){let cloud=0,writes=0;const repo={invoke:async(c,r)=>{if(r.operation==='draft_turn')return {};if(r.operation==='prepare_action_turn')return packet(raw);if(r.operation==='conversation_snapshot')return {mode:'real',revision:0,turns:[],questions:[],pendingDraft:null};if(r.operation==='action_snapshot')return {revision:0,actions:[],turns:[],focus:null};if(r.operation==='commit_action_turn'){writes++;return {status:'committed'}}cloud++;throw Error('ordinary pipeline invoked '+r.operation)}};return {app:new ControlledConversation(repo),counts:()=>({cloud,writes})}}
test('unsupported explicit input never prepares disclosure and keeps draft',async()=>{const {app,counts}=mocked('帮我把这件事安排一下。');const f=new ControlledFlow(app,()=>{});await f.start();f.edit('帮我把这件事安排一下。');await f.prepare();assert.equal(f.preview,null);assert.equal(f.draft.text,'帮我把这件事安排一下。');assert.match(f.notice,/没有记入/);assert.deepEqual(counts(),{cloud:0,writes:0});f.dispose()});
test('unsupported no matching cancellation is honest local no-change',async()=>{const {app,counts}=mocked('先不买合成材料了。');const r=await app.prepare({requestId:'d',turnId:'t',revision:1,text:'先不买合成材料了。'},()=>true);assert.equal(r.kind,'unsupported');assert.match(r.notice,/没有取消/);assert.deepEqual(counts(),{cloud:0,writes:0})});
test('unsupported read restoration does not parse or write',async()=>{const {app,counts}=mocked('帮我把这件事安排一下。');const f=new ControlledFlow(app,()=>{});await f.start();f.edit('帮我把这件事安排一下。');await f.prepare();await f.restore();assert.deepEqual(counts(),{cloud:0,writes:0});assert.equal(f.draft.text,'帮我把这件事安排一下。');f.dispose()});
test('late cancelled parsing cannot write',async()=>{let calls=0;const app=new ActionApplication({prepare:async()=>packet('我明天先买合成材料。'),commit:async()=>calls++});await assert.rejects(app.submit({turnId:'t',revision:1},()=>false));assert.equal(calls,0)});
test('legacy explicit negative new intent never becomes cancellation',()=>{const r=classifyAction(packet('我明天先不买合成材料。',[a]));assert.equal(r.kind,'unsupported_action');assert.equal(r.candidate,undefined)});
