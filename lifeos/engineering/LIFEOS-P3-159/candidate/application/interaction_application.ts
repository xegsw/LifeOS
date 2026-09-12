import type {InteractionPort,UserTurn,UserTurnReceipt,AssistantTurn,SpeechOutputRequest,SpeechInterrupted,Ref} from './interaction_contract.ts';
/** One additive Host route. It never sends a model or invents execution permission. */
export class InteractionApplication implements InteractionPort {
 private delivered=new Set<string>();
 private assistants=new Set<(turn:AssistantTurn)=>void>();private speech=new Set<(r:SpeechOutputRequest)=>void>();
 constructor(private invoke:(command:string,request:any)=>Promise<any>){}
 private async call(command:string,operation:string,payload:any){const r=await this.invoke(command,{version:'interaction-v1',operation,payload});if(r?.version!=='interaction-v1'||r.operation!==operation||!r.result)throw {code:'interaction_contract_rejected'};return r.result;}
 async submitUserTurn(turn:UserTurn):Promise<UserTurnReceipt>{const r=await this.call('capture_record','submit_user_turn',turn);return r.receipt;}
 async submitKeyboard(text:string,correlationId:string,replyTo?:Ref){
  const hints=replyTo?{replyTo,presentedProactiveRef:replyTo}:{};
  const a=await this.call('resolve_request_context','allocate_user_turn',{correlationId,conversationRef:{id:'source-chat',revision:1},origin:{kind:'keyboard'},...hints});
  const turn:UserTurn={schemaVersion:'interaction-v1',turnId:a.turnId,conversationRef:a.conversationRef,text,origin:{kind:'keyboard'},finalizedAt:new Date(a.allocatedAt).toISOString(),...hints};
  const receipt=await this.submitUserTurn(turn);if(receipt.status==='rejected'||receipt.status==='unknown')throw {code:receipt.code};
  const status=await this.call('get_context_recovery','interaction_turn_status',{turnId:turn.turnId});return {turn,receipt,proactiveRequestId:status.proactiveRequestId};
 }
 onAssistantTurn(listener:(turn:AssistantTurn)=>void){this.assistants.add(listener);return ()=>this.assistants.delete(listener);}
 onSpeechOutputRequest(listener:(r:SpeechOutputRequest)=>void){this.speech.add(listener);return ()=>this.speech.delete(listener);}
 reportSpeechInterrupted(event:SpeechInterrupted){return this.call('decide_understanding_feedback','speech_interrupted',event).then(()=>{});}
 async refreshOutputs(){const output=await this.call('get_context_recovery','interaction_outputs',{});for(const turn of output.turns as AssistantTurn[]){const key=turn.turnRef.id+':'+turn.turnRef.revision;if(this.delivered.has(key))continue;this.delivered.add(key);for(const listener of this.assistants)listener(turn);}}
 // No SpeechOutputRequest is generated while voice-purpose authorization is absent.
}
