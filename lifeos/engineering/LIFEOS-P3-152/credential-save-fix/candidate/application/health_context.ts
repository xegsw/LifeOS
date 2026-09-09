/** P3-151 scoped extension of the existing Context Resolver; synthetic only. */
import {resolve,validRows,currentStates,type Snapshot,type Ref} from './core.ts';
export type Domain='health'|'work'|'source'|'ambiguous';
export const minutes=(text:string)=>{const m=text.match(/(?:(?:我有|只有|有空|可用|能拿出|可以留出)\s*)?(\d{1,3})\s*(?:分钟|min(?:utes)?)/i);return m&&Number(m[1])>=1&&Number(m[1])<=240?Number(m[1]):null};
export function intent(text:string){const h=/健康|睡眠|睡了|步数|散步|走路|运动|锻炼|精力|疲惫|活动|health|sleep|exercise|steps/i.test(text),w=/工作|项目|报告|会议|任务|编程|work|project|report/i.test(text);return h&&!w?'health':w&&!h?'work':'ambiguous'}
export function chooseContext(packet:any){
 const purpose:Domain=packet.domain,now=packet.now;
 if(purpose==='ambiguous'||/解释|证明|是什么|为什么/.test(packet.question)&&!/我的|记录|来源|最近|昨天/.test(packet.question))return {inputRefs:[],included:[],states:[],feedback:[],usedBudget:0,usedBytes:0,purpose};
 const scoped:Snapshot=structuredClone(packet.snapshot);
 scoped.records=scoped.records.filter((r:any)=>r.domain===purpose);
 const current=currentStates(scoped,now).filter((s:any)=>s.domain===purpose).slice(0,2);
 const memory=scoped.memories.filter((m:any)=>m.confirmed&&m.status==='active'&&scoped.records.some(r=>r.id===m.rawId)).slice(0,Math.max(0,2-current.length));
 const required=new Set([...current,...memory].map(v=>v.rawId));
 const metric=/睡|sleep/i.test(packet.question)?'sleep':/步数|steps/i.test(packet.question)?'steps':/运动|散步|走路|锻炼|exercise/i.test(packet.question)?'exercise':null;
 const words=[...new Set((packet.question.toLowerCase().match(/[a-z]{3,}|[\u4e00-\u9fff]+/g)||[]).flatMap((w:string)=>/^[a-z]/.test(w)?[w]:Array.from({length:Math.max(0,w.length-1)},(_,i)=>w.slice(i,i+2))))];
 const score=(r:any)=>metric&&r.metric===metric?100:words.reduce((n:number,t:string)=>n+(r.text.toLowerCase().includes(t)?1:0),0)+(purpose==='health'&&/安排|建议|计划|活动|走路|运动|散步|exercise/i.test(packet.question)&&['sleep','exercise'].includes(r.metric)?1:0);
 const source=validRows(scoped,now).filter((r:any)=>r.kind==='source_projection'&&score(r)>0).sort((a:any,b:any)=>score(b)-score(a)||b.observedAt-a.observedAt||a.id.localeCompare(b.id)).slice(0,3);
 scoped.records=scoped.records.filter(r=>required.has(r.id)||source.some(s=>s.id===r.id));scoped.states=current;scoped.memories=memory;
 const result=resolve(scoped,purpose,{budget:512,topK:3,now});
 const usedBytes=new TextEncoder().encode(JSON.stringify(result.included)).length;
 if(usedBytes>4096||result.included.filter((r:any)=>r.layer==='L3').length>3||result.included.filter((r:any)=>r.layer!=='L3').length>2)throw {code:'context_budget_rejected'};
 return {...result,usedBytes};
}
export function interpretation(packet:any,context:any){
 const text=packet.question,domain:Domain=packet.domain,qs=packet.questions||[],states=packet.snapshot.states||[];
 const pending=qs.find((q:any)=>q.status==='pending'&&(q.field==='domain'||q.domain===domain));
 if(domain==='source')return {};
 const time=minutes(text),selfSleep=text.match(/(?:我|自己).{0,6}(?:睡了|睡眠).{0,3}(\d{1,2}(?:\.\d+)?)\s*(?:小时|h)/i);
 const explicitTime=time!==null&&!/如果|假如|假设|分钟[吗?？]/.test(text)&&(/我有|只有|有空|可用|能拿出|可以留出/.test(text)||pending?.field==='available_time');
 let state:any,corrects:string|undefined,answerTo:string|undefined;
 if(domain!=='ambiguous'&&explicitTime)state={key:'available_time',value:time,domain};
 if(domain==='health'&&selfSleep&&!/如果|假如|假设|小时[吗?？]/.test(text)&&Number(selfSleep[1])<=24)state={key:'sleep_hours',value:Number(selfSleep[1]),domain};
 if(state&&/纠正|改为|不是|更正/.test(text)){const prior=states.find((s:any)=>s.stateKey===state.key&&s.domain===domain&&s.status==='active');if(prior)corrects=prior.id;}
 if(pending&&(state&&pending.field===state.key||pending.field==='domain'&&domain!=='ambiguous'))answerTo=pending.id;
 const hasTime=!!state&&state.key==='available_time'||states.some((s:any)=>s.stateKey==='available_time'&&s.domain===domain&&s.status==='active'&&s.validUntil>packet.now);
 const needs=domain==='ambiguous'?(/安排|计划|工作|健康|work|health|plan/i.test(text)?'domain':null):/安排|建议|怎么开始|如何开始|计划|plan|suggest|recommend/i.test(text)&&!hasTime&&context.included.length?'available_time':null;
 const already=needs&&qs.some((q:any)=>q.field===needs&&(q.domain===domain||needs==='domain')&&(['answered','ignored','pending'].includes(q.status)||q.status==='deferred'&&q.resumeAt>packet.now));
 return {state,corrects,answerTo,clarification:needs&&!already?{field:needs}:undefined};
}
export interface HealthModelPort {id:'OfflineA'|'OfflineB';generate(packet:any,context:any,decision:any):Promise<{text:string,inputRefs:Ref[]}>}
export class OfflineAdapter implements HealthModelPort{
 private failed=new Set<string>();
 constructor(public id:'OfflineA'|'OfflineB'){}
 async generate(packet:any,context:any,decision:any){
  if(Date.now()>packet.expiresAt||context.usedBytes>4096)throw {code:'context_stale'};
  if(context.inputRefs.some((r:any)=>!packet.snapshot.records.some((v:any)=>v.id===r.id&&v.version===r.version)))throw {code:'context_stale'};
  await new Promise(r=>setTimeout(r,this.id==='OfflineB'?1100:25));
  if(packet.question.includes('[模拟失败]')&&!this.failed.has(packet.id)){this.failed.add(packet.id);throw {code:'offline_test_failure'};}
  const prefix=`合成演练 · ${this.id==='OfflineA'?'离线测试 A':'离线测试 B'}\n`;
  let answer='';
  if(decision.clarification?.field==='domain')answer='你想讨论工作安排，还是健康活动？这会决定本次使用哪些来源。';
  else if(decision.clarification?.field==='available_time')answer='你这次大约有多少分钟？可用时间会影响建议的大小，也可以暂时不回答。';
  else if(!context.included.length)answer='没有找到与这个问题相关、有效且获准的合成来源。此离线测试不具备开放域推理能力，暂不能据此回答。';
  else {
   const metric=/睡|sleep/i.test(packet.question)?'sleep':/步数|steps/i.test(packet.question)?'steps':null;
   const available=decision.state?.key==='available_time'?decision.state.value:context.states.find((s:any)=>s.stateKey==='available_time')?.value;
   const source=context.included.filter((r:any)=>r.layer==='L3');
   const original=source.map((r:any)=>packet.snapshot.records.find((s:any)=>s.id===r.id));
   if(metric)answer=original.filter((r:any)=>r.metric===metric).map((r:any)=>`${r.text}（合成来源日期 ${new Date(r.observedAt).toISOString().slice(0,10)}）`).join('\n')||'这一指标暂无相关的有效观察；不会把缺失当作零。';
   else if(packet.domain==='health')answer=available?`按你明确提供的 ${available} 分钟，可以留 ${Math.min(10,available)} 分钟轻松走动，再决定是否继续。这是非医疗的合成示例。`:'可先选择轻松活动；目前缺少可用时间，不替你假定时长。';
   else answer=available?`按你提供的 ${available} 分钟，先处理一个能在 ${Math.min(25,available)} 分钟内推进的小步骤。`:'先从问题涉及的工作资料中确定一个小步骤；暂不假定你的可用时间。';
   if(decision.corrects)answer+=' 已按你的纠正更新本次短期依据，旧理解不会继续沿用。';
   if(original.length)answer+=`\n依据截至 ${new Date(Math.max(...original.map((r:any)=>r.observedAt))).toISOString().slice(0,10)}；仅代表已导入的合成观察。`;
  }
  return {text:prefix+answer,inputRefs:context.inputRefs};
 }
}
