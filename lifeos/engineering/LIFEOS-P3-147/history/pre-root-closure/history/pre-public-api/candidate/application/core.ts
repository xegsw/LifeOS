/** P3-146 Application/Ports. Lifecycle/resolver semantics trace to 139/140. */
export type Ref = {id:string,version:number,authorizationGeneration:number};
export interface RepositoryPort { invoke(ipc:string, request: {version:2,operation:string,payload:unknown}):Promise<any> }
export interface ModelPort { id:'OfflineA'|'OfflineB'; generate(packet:any):{text:string,inputRefs:Ref[],startedAt:number,finishedAt:number,usage:number}; }
export interface SourcePort { status:'synthetic_fixture'; discover():string[]; read(id:string):SourceItem; sync():never; }
export type SourceItem={sourceId:string,externalId:string,sourceType:'synthetic_markdown'|'synthetic_health',version:number,content:string,mimeType:string,title?:string,metadata?:Record<string,unknown>};
export type Snapshot={revision:number,now:number,records:any[],memories:any[],states:any[],sources:any[],questions:any[],packets:any[],derivations:any[],feedback:any[],drafts:any[]};
export class NoNetwork { calls=0; dispatch():never {this.calls++;throw new Error('offline_network_denied')} }
export class NoCredential { calls=0; read():never {this.calls++;throw new Error('offline_credential_denied')} }
export const boundary={network:new NoNetwork(),credential:new NoCredential()};
export const uid=()=>crypto.randomUUID();
export function validRows(s:Snapshot,now=Date.now()){return s.records.filter(r=>r.status==='active'&&(!r.validUntil||r.validUntil>now)&&s.sources.some(src=>src.id===r.sourceId&&src.authorized));}
export function currentStates(s:Snapshot,now=Date.now()) {
 const ids=new Set(validRows(s,now).map(r=>r.id));const sorted=s.states.filter(v=>v.status==='active'&&ids.has(v.rawId)&&v.validUntil>now).sort((a,b)=>b.observedAt-a.observedAt||b.generation-a.generation||b.id.localeCompare(a.id));
 return sorted.filter((v,i)=>sorted.findIndex(w=>w.stateKey===v.stateKey&&w.domain===v.domain)===i);
}
function stateFromText(text:string,domain:string) {
 const available=text.match(/(?:时间|有空|time)\D{0,5}(\d{1,3})\s*(?:分钟|min)/i);
 const sleep=text.match(/(?:睡眠|睡了|sleep)\D{0,5}(\d{1,2}(?:\.\d+)?)\s*(?:小时|h)/i);
 if(available) return {stateKey:'available_time',stateValue:Number(available[1]),domain:'work'};
 if(sleep) return {stateKey:'sleep_hours',stateValue:Number(sleep[1]),domain:'health'};
 if(domain==='work')return {stateKey:'work_load',stateValue:text,domain};
 return {domain};
}
/** Feedback is usable only when its entire original basis is still in this request. */
export function relevantFeedback(s:Snapshot,refs:Ref[],now=Date.now()) {
 const valid=validRows(s,now);
 return s.feedback.filter(f=>{
  const target=s.derivations.find(d=>d.id===f.targetId);
  if(!target || !(target.status===f.decision || (f.decision==='correct'&&target.status==='stale')) || !target.inputRefs?.length)return false;
  return target.inputRefs.every((r:Ref)=>{
   const raw=valid.find(v=>v.id===r.id), source=raw&&s.sources.find(v=>v.id===raw.sourceId);
   return raw&&raw.version===r.version&&source.generation===r.authorizationGeneration&&refs.some(v=>v.id===r.id&&v.version===r.version&&v.authorizationGeneration===r.authorizationGeneration);
  });
 }).map(f=>({targetId:f.targetId,decision:f.decision}));
}
/** L1 mandatory confirmed memory, L2 mandatory effective state, L3 relevant source Top-K.
 * Required entries reserve before optional retrieval; final packet checked again. */
export function resolve(s:Snapshot,purpose:string,{budget=256,topK=3,removedRefs=[] as string[],now=Date.now()}={}) {
 if(budget<32||budget>1200||topK<1||topK>8)throw new Error('context_budget_rejected');
 const valid=validRows(s,now), removed=new Set(removedRefs);const included:any[]=[], excluded:any[]=[];let used=0;
 for(const r of s.records){if(!valid.some(v=>v.id===r.id))excluded.push({id:r.id,reason:'invalid_expired_or_revoked'});else if(removed.has(r.id))excluded.push({id:r.id,reason:'removed_for_request'});}
 const add=(r:any,layer:string,required:boolean)=>{if(removed.has(r.id)||included.some(v=>v.id===r.id))return;const cost=8+Math.ceil([...r.text].length/4);if(used+cost>budget){if(required)throw new Error('context_budget_rejected');excluded.push({id:r.id,reason:'budget_pruned'});return;}used+=cost;const source=s.sources.find(v=>v.id===r.sourceId);included.push({id:r.id,version:r.version,authorizationGeneration:source.generation,layer,text:r.text,domain:r.domain});};
 for(const m of s.memories.filter(m=>m.confirmed&&m.status==='active')) {const r=valid.find(v=>v.id===m.rawId);if(r)add(r,'L1',true);}
 for(const st of currentStates(s,now)){const r=valid.find(v=>v.id===st.rawId);if(r&&(purpose!=='work'||r.domain!=='health'))add(r,'L2',true);}
 let optional=0;
 for(const r of valid) {if(included.some(v=>v.id===r.id)||removed.has(r.id))continue;if(purpose==='work'&&r.domain==='health'){excluded.push({id:r.id,reason:'domain_not_necessary'});continue;}
 if(optional>=topK){excluded.push({id:r.id,reason:'top_k_pruned'});continue;}const n=included.length;add(r,'L3',false);if(included.length>n)optional++;}
 if(used>budget)throw new Error('context_budget_rejected');
 return {id:'packet:'+uid(),purpose,budget,usedBudget:used,topK,inputRefs:included.map(({id,version,authorizationGeneration})=>({id,version,authorizationGeneration})),included,excluded,states:currentStates(s,now).filter(st=>included.some(v=>v.id===st.rawId)),feedback:relevantFeedback(s,included,now),createdAt:now};
}
/** A missing available-time field matters only if there is actual Work to prioritize. */
export function nextQuestion(s:Snapshot,context='daily',now=Date.now()) {
 const rows=validRows(s,now);if(!rows.some(r=>r.domain==='work')||currentStates(s,now).some(v=>v.stateKey==='available_time'))return null;
 const prior=s.questions.filter(q=>q.context===context&&q.missingField==='available_time').sort((a,b)=>b.window.localeCompare(a.window));
 const latest=prior[0];
 if(latest&&['ignored','refused'].includes(latest.status)&&latest.window===String(Math.floor(now/86400000)))return null;
 if(latest?.status==='deferred'&&latest.resumeAt>now)return null;
 if(latest?.status==='answered'&&rows.some(r=>r.id===latest.answerRef))return null;
 let window=String(Math.floor(now/86400000));let suffix=latest?.status==='answered'&&!rows.some(r=>r.id===latest.answerRef)?':expired-'+latest.answerRef:'';
 const id='q:'+context+':available:'+window+suffix;
 return {id,purpose:'可用时间会改变下一步的大小',missingField:'available_time',context,window,text:'今天可以留给这件事多少分钟？',basisRefs:rows.filter(r=>r.domain==='work').map(r=>r.id),generation:1,status:'pending'};
}
export function makeModel(id:'OfflineA'|'OfflineB'):ModelPort {
 if(!['OfflineA','OfflineB'].includes(id))throw new Error('offline_model_rejected');
 return {id,generate(packet:any){const start=Date.now();const available=packet.states.find((s:any)=>s.stateKey==='available_time');const sleep=packet.states.find((s:any)=>s.stateKey==='sleep_hours');const minutes=available?Math.min(25,Math.max(1,Number(available.value))):25;
 const health=sleep&&Number(sleep.value)<7?'考虑你记录的睡眠较短，先降低今天的负荷。':'';
 const previous=packet.feedback.some((f:any)=>['reject','correct'].includes(f.decision))?'已考虑你对上一建议的纠正，重新选择受影响的下一步。':'';
 const hasWork=packet.included.some((r:any)=>r.domain==='work');const text=packet.inputRefs.length===0?'目前没有可用的获准记录；先保存一条想法。':!hasWork?'已保留当前来源，暂不生成缺少 Work 依据的行动。':`${id==='OfflineA'?'建议先做':'可以从'}一个 ${minutes} 分钟的工作起步。${health}${previous}`;
 return {text,inputRefs:packet.inputRefs,startedAt:start,finishedAt:Date.now(),usage:packet.usedBudget};}};
}
export class FixtureSource implements SourcePort {
 status='synthetic_fixture' as const;
 constructor(private items:SourceItem[]){}
 discover(){return this.items.map(v=>v.externalId)}
 read(id:string){const item=this.items.find(v=>v.externalId===id);if(!item)throw new Error('source_item_missing');return structuredClone(item)}
 sync():never{throw new Error('continuous_sync_unsupported')}
}
export class Application {
 constructor(public repo:RepositoryPort){}
 call(ipc:string,operation:string,payload:any={}){return this.repo.invoke(ipc,{version:2,operation,payload})}
 snapshot():Promise<Snapshot>{return this.call('get_today','snapshot')}
 draft(text:string,draftId:string,conversationId:string,turnId:string,revision:number,requestId="save:"+turnId,observedAt=Date.now()){return this.call('capture_record','draft',{draftId,conversationId,turnId,revision,text,requestId,observedAt})}
 async save(text:string,{intent='record',requestId=uid(),conversationId='daily',turnId=uid(),draftId,questionId,domain='work',now=Date.now()}:{intent?:string,requestId?:string,conversationId?:string,turnId?:string,draftId?:string,questionId?:string,domain?:string,now?:number}={}) {
  if(!text.trim()||[...text].length>200)throw new Error('text_rejected');
  const state=intent==='remember'?{domain}:stateFromText(text,domain);
  if(intent==='answer'&&state.stateKey!=='available_time')throw new Error('answer_needs_available_minutes');
  const p:any={requestId,conversationId,turnId,text,intent,observedAt:now,...state};
  if(intent==='remember')Object.assign(p,{statement:text,scope:'person',confirmation:'remember_this_statement'});
  else if(state.stateKey)p.validUntil=now+86400000;
  if(draftId)p.draftId=draftId;if(questionId)p.questionId=questionId;
  return this.call('capture_record','save',p);
 }
 async importSource(item:SourceItem,requestId=uid(),now=Date.now()){
  let state:any={domain:'work'},validUntil:number|undefined;
  if(item.sourceType==='synthetic_health'){
   if(item.sourceId!=='health-demo'||item.mimeType!=='application/json')throw new Error('source_type_rejected');
   let h:any;try{h=JSON.parse(item.content)}catch{throw new Error('health_payload_rejected')}
   if(Object.keys(h).some(k=>!['sleepHours','start','end','unit'].includes(k))||typeof h.sleepHours!=='number'||h.sleepHours<0||h.sleepHours>24||h.unit!=='hours'||!Number.isSafeInteger(h.start)||!Number.isSafeInteger(h.end)||h.end<=h.start||h.end>now)throw new Error('health_payload_rejected');
   state={domain:'health',stateKey:'sleep_hours',stateValue:h.sleepHours};validUntil=h.end+86400000;now=h.end;
  } else if(item.sourceType!=='synthetic_markdown'||item.sourceId!=='obsidian-demo'||item.mimeType!=='text/markdown')throw new Error('source_type_rejected');
  if(item.sourceType==='synthetic_markdown'){const parsed=stateFromText(item.content,'work');if(parsed.stateKey==='available_time'){state=parsed;validUntil=now+86400000;}}
  const p:any={requestId,item,authorizationRef:'local:'+item.sourceId,observedAt:now,...state};if(validUntil)p.validUntil=validUntil;else p.noExpiryReason='synthetic_reference_until_revised';
  return this.call('capture_record','ingest',p);
 }
 async prepare(purpose='person',options:any={}) {const s=await this.snapshot();const packet=resolve(s,purpose,options);return this.call('assemble_global_ai_context','local_prepare',{requestId:uid(),expectedGeneration:s.revision,packet});}
 async generate(packet:any,modelId:'OfflineA'|'OfflineB'='OfflineA') {const output=makeModel(modelId).generate(packet);return this.call('resolve_request_context','offline_generate',{requestId:uid(),modelId,contextPacketId:packet.id,output});}
 async question() {const s=await this.snapshot();const q=nextQuestion(s);if(!q)return null;return this.call('assemble_global_ai_context','surface_question',{requestId:uid(),question:q});}
 decide(q:any,decision:string,resumeAt?:number) {const p:any={requestId:uid(),questionId:q.id,expectedGeneration:q.generation,decision};if(resumeAt)p.resumeAt=resumeAt;return this.call('decide_understanding_feedback','question_decision',p);}
 async correct(record:any,text:string,now=Date.now(),draftId?:string) {const state=stateFromText(text,record.domain);const p:any={requestId:uid(),id:record.id,text,expectedGeneration:record.version,observedAt:now};if(draftId)p.draftId=draftId;if(record.intent==='remember')p.confirmation='remember_this_statement';else if(state.stateKey){p.validUntil=now+86400000;p.stateValue=state.stateValue;}return this.call(record.intent==='remember'?'upsert_durable_memory':'update_current_state','correct',p);}
 feedback(id:string,decision:string){return this.call('decide_understanding_feedback','feedback',{requestId:uid(),id,decision})}
 revoke(source:any){return this.call('get_context_disclosure_receipt','source_revoke',{requestId:uid(),sourceId:source.id,expectedGeneration:source.generation})}
}
