/** UI lifecycle only. Host remains the authority for persistence and confirmation. */
export class ConversationFlow {
 draft:any; preview:any=null; opened=false; busy=false; phase='restoring'; error:any=null;
 private serial=0; private starting:Promise<void>|null=null; private queue=Promise.resolve();
 private timer:ReturnType<typeof setTimeout>|undefined; private expiry:ReturnType<typeof setTimeout>|undefined;
 private committing:string|null=null;
 private previewContext:{turnId:string,excluded:string[]}|null=null;
 constructor(private app:any, private changed:()=>void, private reload:()=>Promise<void>){this.draft=this.newDraft()}
 private newDraft(){const id=crypto.randomUUID();return {requestId:id,draftId:'draft:'+id,conversationId:'source-chat',turnId:id,revision:1,text:''}}
 start(){
  if(this.opened)return Promise.resolve();if(this.starting)return this.starting;
  this.phase='restoring';this.error=null;this.changed();
  this.starting=(async()=>{try{const page=await this.app.open('source-chat');this.opened=true;
   // Any edit in this flow's lifetime wins, including edits between failed attempts.
   if(this.serial===0&&page.pendingDraft)this.draft=page.pendingDraft;
   await this.reload();this.phase='idle';if(this.serial>0)this.saveDraft();
  }catch(e){this.error=e;this.phase=this.opened?'idle':'open-failed'}finally{this.starting=null;this.changed()}})();return this.starting;
 }
 edit(text:string){if(this.committing===this.draft.draftId)this.draft=this.newDraft();
  this.draft={...this.draft,text,revision:this.draft.revision+1,requestId:crypto.randomUUID()};this.serial++;
  this.invalidate();clearTimeout(this.timer);this.timer=setTimeout(()=>this.saveDraft(),250);
 }
 private saveDraft(){if(!this.opened)return;const captured={...this.draft};
  this.queue=this.queue.then(()=>this.app.call('capture_record','draft_question',captured)).catch(e=>{this.error=e;this.changed()});
 }
 invalidate(){const prior=this.preview;this.preview=null;this.previewContext=null;clearTimeout(this.expiry);
  if(prior){void this.app.cancel(prior).catch(()=>{});this.changed()}
 }
 private accept(preview:any,serial:number,turnId:string,excluded:string[]=[]){if(serial!==this.serial){void this.app.cancel(preview).catch(()=>{});return}
  this.preview=preview;this.previewContext={turnId,excluded:[...excluded]};clearTimeout(this.expiry);
  if(preview.state==='ready')this.expiry=setTimeout(()=>{if(this.preview===preview){this.invalidate();this.error={code:'preview_expired'};this.changed()}},Math.max(0,preview.expiresAt-Date.now()));
 }
 async prepare(){if(this.busy||!this.opened||!this.draft.text.trim())return;
  const submitted={...this.draft},serial=this.serial;this.committing=submitted.draftId;
  this.busy=true;this.phase='preparing';this.error=null;this.invalidate();this.changed();clearTimeout(this.timer);
  try{await this.queue;await this.app.ask(submitted);
   if(this.draft.draftId===submitted.draftId&&this.draft.revision===submitted.revision)this.draft=this.newDraft();
   await this.reload();this.accept(await this.app.preview(submitted.turnId),serial,submitted.turnId);
  }catch(e){this.error=e}finally{this.committing=null;this.busy=false;this.phase='idle';this.changed()}
 }
 async prepareTurn(turnId:string,excluded:string[]=[]){if(this.busy||!this.opened)return;const serial=this.serial;
  this.busy=true;this.phase='preparing';this.error=null;this.invalidate();this.changed();
  try{this.accept(await this.app.preview(turnId,excluded),serial,turnId,excluded)}catch(e){this.error=e}finally{this.busy=false;this.phase='idle';this.changed()}
 }
 async remove(segmentId:string){if(this.busy)return;
  const prior=this.preview,context=this.previewContext,serial=this.serial;
  this.preview=null;this.previewContext=null;clearTimeout(this.expiry);
  this.busy=true;this.phase='preparing';this.error=null;this.changed();
  try{
   if(prior)await this.app.cancel(prior);
   if(!prior||!context||!prior.items?.some((i:any)=>i.source?.segmentId===segmentId))throw {code:'preview_stale'};
   const excluded=[...new Set([...context.excluded,segmentId])];
   this.accept(await this.app.preview(context.turnId,excluded),serial,context.turnId,excluded);
  }catch(e){this.error=e}finally{this.busy=false;this.phase='idle';this.changed()}
 }
 async confirm(){const preview=this.preview;if(this.busy||preview?.state!=='ready')return;
  this.busy=true;this.error=null;this.phase='checking';this.changed();
  try{const current=await this.app.call('get_context_disclosure_receipt','read_preview',{previewId:preview.previewId});
   if(this.preview!==preview||current.state!=='ready'||current.revision!==preview.revision||current.confirmationToken!==preview.confirmationToken)throw {code:'preview_stale'};
   this.preview=null;this.previewContext=null;clearTimeout(this.expiry);this.phase='sending';this.changed();
   const result=await this.app.send(current);if(result.state!=='succeeded')this.error={code:result.errorCode||'dispatch_outcome_unknown'};
   await this.reload();
  }catch(e){this.error=e;this.invalidate()}finally{this.busy=false;this.phase='idle';this.changed()}
 }
 async cancel(){const prior=this.preview;this.preview=null;this.previewContext=null;clearTimeout(this.expiry);this.changed();if(prior)try{await this.app.cancel(prior)}catch(e){this.error=e;this.changed()}}
 dispose(){clearTimeout(this.timer);clearTimeout(this.expiry)}
}
