import {HealthConversation} from './health_conversation.ts';
import {chooseContext,interpretation} from './health_context.ts';
export class ControlledConversation extends HealthConversation {
 call5(command:string,operation:string,payload:any={}){return (this as any).repo.invoke(command,{version:5,operation,payload})}
 saveCatalog(settings:any,revision:number){return this.call5('save_ai_provider_settings','save_local_catalog',{requestId:crypto.randomUUID(),expectedRevision:revision,settings})}
 settings(){return this.call5('get_ai_provider_settings','read_local')}
 async lifecycle(operation:string,extra:any={}){const s=await this.read(),p=s.provider;return this.call5('save_ai_provider_settings',operation,{requestId:crypto.randomUUID(),expectedCredentialRevision:p.credentialRevision,expectedProfileRevision:p.profileRevision,expectedCatalogRevision:s.catalog.revision,expectedSettingsRevision:p.settingsRevision,...(operation==='test_models'?{}:{testReceiptId:p.testReceiptId||'missing'}),...extra})}
 testModels(){return this.lifecycle('test_models')}
 selectModel(modelId:string){return this.lifecycle('select_model',{modelId})}
 setEnabled(enabled:boolean){return this.lifecycle('set_enabled',{enabled})}
 saveCredential(apiKey:string,revision:number){return this.call5('save_ai_provider_settings','save_credential',{requestId:crypto.randomUUID(),expectedCredentialRevision:revision,apiKey})}
 deleteCredential(revision:number){return this.call5('save_ai_provider_settings','delete_credential',{requestId:crypto.randomUUID(),expectedCredentialRevision:revision})}
 cancelPreview(previewId:string){return this.call5('resolve_request_context','cancel_preview',{requestId:crypto.randomUUID(),previewId})}
 confirm(v:any){return this.call5('send_source_ai_request','confirm_send',{requestId:'send:'+v.previewId,previewId:v.previewId,expectedPreviewRevision:v.revision,confirmationToken:v.confirmationToken})}
 async prepare(d:any,current:()=>boolean){await this.draft(d);const packet=await this.call('resolve_request_context','prepare_turn',{requestId:crypto.randomUUID(),turnId:d.turnId,expectedDraftRevision:d.revision});const context=chooseContext(packet),decision=interpretation(packet,context);
  if(!current()){await this.cancel(d.turnId);throw {code:'turn_cancelled'}}
  if(decision.state||decision.answerTo||decision.clarification){await this.answer(d,current);return {kind:'local'}}
  const settings=await this.settings();if(settings.credentialState!=='stored'||!settings.modelId||!settings.enabled)throw {code:'credential_missing'};
  const preview=await this.call5('resolve_request_context','prepare_disclosure',{requestId:crypto.randomUUID(),turnId:d.turnId,packetId:packet.id,modelId:settings.modelId,inputRefs:context.inputRefs});
  if(!current()){await this.cancelPreview(preview.previewId);throw {code:'turn_cancelled'}}return {kind:'preview',preview};
 }
}
export class ControlledFlow {
 draft:any; snapshot:any=null;preview:any=null;opened=false;busy=false;phase='restoring';error:any=null;notice='';
 private serial=0;private queue=Promise.resolve();private timer:any;private token:string|null=null;private preparedTurn:string|null=null;private starting:Promise<void>|null=null;
 constructor(public app:ControlledConversation,private changed:()=>void){this.draft=this.newDraft()}
 private newDraft(text=''){return {requestId:crypto.randomUUID(),turnId:crypto.randomUUID(),revision:1,text}}
 async reload(){const s=await this.app.read();if(!this.snapshot||s.revision>=this.snapshot.revision)this.snapshot=s;this.changed()}
 start(){if(this.opened)return Promise.resolve();if(this.starting)return this.starting;this.starting=(async()=>{try{const s=await this.app.read();this.snapshot=s;this.opened=true;if(this.serial===0&&s.pendingDraft){const d=s.pendingDraft;this.draft=d.status==='cancelled'?this.newDraft(d.text):{requestId:crypto.randomUUID(),turnId:d.turnId,revision:d.revision,text:d.text};}this.phase='idle';if(this.serial)this.persist();}catch(e){this.error=e;this.phase='open-failed'}finally{this.starting=null;this.changed()}})();return this.starting}
 edit(text:string){if(this.preparedTurn===this.draft.turnId){if(this.preview)void this.app.cancelPreview(this.preview.previewId).catch(()=>{});void this.app.cancel(this.draft.turnId).catch(()=>{});this.preview=null;this.draft=this.newDraft(this.draft.text);this.preparedTurn=null;}
  this.draft={...this.draft,text,revision:this.draft.revision+1,requestId:crypto.randomUUID()};this.serial++;clearTimeout(this.timer);this.timer=setTimeout(()=>this.persist(),200);if(!this.busy){this.phase='idle';this.error=null;this.changed();}}
 private persist(){if(!this.opened)return;const d={...this.draft};this.queue=this.queue.then(()=>this.app.draft(d)).catch(e=>{this.error=e;this.changed()});}
 async prepare(){if(this.busy||!this.opened||!this.draft.text.trim())return;const d={...this.draft},serial=this.serial,token=crypto.randomUUID();this.token=token;this.preparedTurn=d.turnId;this.busy=true;this.phase='preparing';this.error=null;this.notice='';clearTimeout(this.timer);this.changed();const current=()=>this.token===token&&this.serial===serial;
  try{await this.queue;const out=await this.app.prepare(d,current);if(current()){if(out.kind==='local'){this.draft=this.newDraft();this.preparedTurn=null;this.preview=null;this.phase='idle';await this.reload();}else{this.preview=out.preview;this.phase='awaiting-confirmation';}}}
  catch(e){if(current()){this.error=e;this.phase='failed';}}
  finally{if(this.token===token){this.busy=false;this.token=null;if(this.phase==='preparing')this.phase='idle';this.changed();}}
 }
 async confirm(){if(this.busy||!this.preview)return;const v=this.preview,serial=this.serial,token=crypto.randomUUID();this.token=token;this.busy=true;this.phase='sending';this.error=null;this.changed();const current=()=>this.token===token&&this.serial===serial;
  try{const result=await this.app.confirm(v);if(current()){this.preview=null;if(result.state==='succeeded'){this.draft=this.newDraft();this.preparedTurn=null;this.phase='idle';}else if(result.state?.startsWith('cancel')){this.phase='cancelled';this.notice='已停止等待；已发出的内容无法保证撤回。';}else{this.error={code:result.errorCode||'dispatch_outcome_unknown'};this.phase='failed';}}await this.reload();}
  catch(e){if(current()){this.error=e;this.preview=null;this.phase='failed';}}
  finally{if(this.token===token){this.busy=false;this.token=null;this.changed();}}
 }
 async cancel(){const turn=this.preparedTurn,v=this.preview;this.token=null;this.serial++;this.busy=false;this.phase='cancelled';this.error=null;this.preview=null;this.preparedTurn=null;this.notice='已取消，草稿保留。';if(turn&&this.draft.turnId===turn)this.draft=this.newDraft(this.draft.text);this.changed();
  if(v){const r=await this.app.cancelPreview(v.previewId);if(r.state==='cancel_requested_after_dispatch'||r.state==='cancelled_after_dispatch')this.notice='已停止等待；已发出的内容无法保证撤回。';if(r.alreadyCompleted){this.notice='回答已完成。';this.draft=this.newDraft();}}
  if(turn)await this.app.cancel(turn);this.persist();await this.reload();
 }
 private async settingsMutation(operation:()=>Promise<void>){try{await operation();}catch(e){try{await this.reload();}catch{}throw e;}await this.reload();}
 async saveCatalog(settings:any,saved:()=>void=()=>{}){if(this.preparedTurn)await this.cancel();await this.settingsMutation(async()=>{await this.app.saveCatalog(settings,this.snapshot?.catalog?.revision||0);saved();});}
 async selectModel(modelId:string){if(this.preparedTurn)await this.cancel();let result:any;await this.settingsMutation(async()=>{result=await this.app.selectModel(modelId)});return result;}
 async testModels(){if(this.preparedTurn)await this.cancel();let result:any;await this.settingsMutation(async()=>{result=await this.app.testModels()});return result;}
 async setEnabled(enabled:boolean){if(this.preparedTurn)await this.cancel();await this.settingsMutation(async()=>{await this.app.setEnabled(enabled)});}
 async saveCredential(key:string,saved:()=>void=()=>{}){if(this.preparedTurn)await this.cancel();await this.settingsMutation(async()=>{await this.app.saveCredential(key,this.snapshot?.provider?.credentialRevision||0);saved();});}
 async deleteCredential(){if(this.preparedTurn)await this.cancel();await this.settingsMutation(async()=>{await this.app.deleteCredential(this.snapshot?.provider?.credentialRevision||0);});}
 async decide(id:string,d:'ignore'|'defer'|'reject'|'reopen'){await this.app.decision(id,d);await this.reload()}
 dispose(){clearTimeout(this.timer)}
}
