import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import assert from 'node:assert/strict';
import {ControlledConversation,ControlledFlow} from '../../credential-save-fix/candidate/ui/controlled_conversation.js';
import {settingsView,settingView} from '../../credential-save-fix/candidate/ui/settings_view.js';
const p=spawn('/private/tmp/lifeos-p3-152-health-conversation-v1/real-target/debug/synthetic-driver',[],{stdio:['pipe','pipe','ignore']});
let seq=0;const pending=new Map(),results=[];
createInterface({input:p.stdout}).on('line',l=>{const v=JSON.parse(l),q=pending.get(v.id);if(!q)return;clearTimeout(q.timer);pending.delete(v.id);v.ok?q.resolve(v.result):q.reject(v.error);});
p.on('exit',()=>{for(const q of pending.values()){clearTimeout(q.timer);q.reject(Error('synthetic_driver_exited'));}});
const invoke=(command,request)=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>reject(Error('synthetic_deadline')),10000);pending.set(id,{resolve,reject,timer});p.stdin.write(JSON.stringify({id,command,request})+'\n');});
const app=new ControlledConversation({invoke});
try{
 const initial=await app.read();assert.equal(initial.mode,'synthetic');
 await app.saveCredential('fictional-audit-credential-9876',0);
 let s=await app.read();assert.equal(s.provider.credentialState,'stored');assert.equal(s.provider.maskedTail,'9876');
 settingView.section='模型设置';settingView.mode='cloud';settingView.drafts.cloud={provider:'DeepSeek',model:''};
 const html=settingsView(s,String,()=> '');assert.ok(!html.includes('9876'));assert.match(html,/input id="model" list=/);assert.match(html,/disabled>测试连接/);
 results.push({case:'stored_suffix_returned_but_not_rendered',reproduced:true},{case:'manual_model_input_and_disabled_test',reproduced:true});
 await app.selectModel('fictional-never-tested-model');s=await app.read();assert.equal(s.provider.modelId,'fictional-never-tested-model');assert.equal(s.provider.enabled,true);
 results.push({case:'untested_arbitrary_model_selection_enables_provider',reproduced:true});
 await app.saveCredential('fictional-replacement-credential-1234',1);s=await app.read();assert.equal(s.provider.enabled,true);assert.equal(s.provider.modelId,'fictional-never-tested-model');
 results.push({case:'credential_change_does_not_require_retest',reproduced:true});
 let code='';try{await app.call5('save_ai_provider_settings','test_connection',{requestId:crypto.randomUUID()});}catch(e){code=e.code;}
 assert.ok(code);results.push({case:'manual_test_unavailable_in_public_host',reproduced:true,errorCode:code});
 const flow=new ControlledFlow(app,()=>{});await flow.start();assert.equal(flow.snapshot.provider.credentialState,'stored');flow.dispose();
 results.push({case:'new_frontend_flow_keeps_saved_credential_metadata',reproduced:true,limit:'not an App or OS restart test'});
 console.log(JSON.stringify({scope:'synthetic-only defect reproduction, not product Pass',cases:results.length,results},null,2));
}finally{p.kill();}
