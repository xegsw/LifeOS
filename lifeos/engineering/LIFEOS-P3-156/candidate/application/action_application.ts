import {actionCandidate,validateCandidate,transition} from './action_domain.ts';
import type {ActionPacket,Candidate} from './action_domain.ts';
export interface ActionRepositoryPort {prepare(turnId:string,revision:number):Promise<ActionPacket>;commit(d:any,p:ActionPacket,c:Candidate,modelId:string):Promise<any>;snapshot(offset?:number):Promise<any>}
export interface ActionModelPort {id:'OfflineA'|'OfflineB';parse(p:ActionPacket):Promise<Candidate|undefined>}
export class OfflineActionModel implements ActionModelPort {constructor(public id:'OfflineA'|'OfflineB'){}async parse(p:ActionPacket){return actionCandidate(p)}}
export class ActionApplication {
 constructor(private repo:ActionRepositoryPort,public model:ActionModelPort=new OfflineActionModel('OfflineA')){}
 read(){return this.repo.snapshot()}
 async submit(d:any,current:()=>boolean){const p=await this.repo.prepare(d.turnId,d.revision);if(!current())throw {code:'turn_cancelled'};const c=await this.model.parse(p);if(!c)return false;validateCandidate(p,c);if(c.operation!=='clarify')transition(p.actions.find(a=>a.id===c.targetId),c,{id:'validation',rawId:d.turnId,at:Date.now()});if(!current())throw {code:'turn_cancelled'};await this.repo.commit(d,p,c,this.model.id);return true;}
}
export class IpcActionRepository implements ActionRepositoryPort {
 constructor(private call:(command:string,operation:string,payload:any)=>Promise<any>){}
 prepare(turnId:string,revision:number){return this.call('resolve_request_context','prepare_action_turn',{requestId:'action-prepare:'+turnId+':'+revision,turnId,expectedDraftRevision:revision})}
 commit(d:any,p:ActionPacket,c:Candidate,modelId:string){return this.call('resolve_request_context','commit_action_turn',{requestId:'action-commit:'+d.turnId,turnId:d.turnId,packetId:p.id,expectedDraftRevision:d.revision,candidate:c,modelId})}
 snapshot(offset=0){return this.call('get_context_recovery','action_snapshot',{offset})}
}
