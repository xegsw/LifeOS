import type {VoiceHostPort,VoiceStatus} from './voice/consumer.ts';
import {VoiceConsumer} from './voice/consumer.ts';
import {voiceSettings} from './voice/settings.ts';
import type {InteractionPort,UserTurn,UserTurnReceipt,SpeechInterrupted,SpeechOutputRequest} from './interaction_contract.ts';
// A-only adapter. There is no native final/audio producer or permission grant.
export class OfflineVoiceApplication implements VoiceHostPort {
 private snapshot:VoiceStatus={state:'disabled',sessionId:null,generation:0,policyRevision:0};
 private settings:any={enabled:false,asr:false,tts:false,sessionTurn:false,wakeWord:'LifeOS',keyConfigured:false,usageLabel:'离线接线验证',available:false};
 private consumer:VoiceConsumer;
 constructor(private call:(command:string,value:any)=>Promise<any>,interaction:InteractionPort){this.consumer=new VoiceConsumer(interaction,this);}
 status(){return this.snapshot;}
 async refresh(){const r=await this.call('voice_status',{version:1,payload:{}});if(r?.version!==1||r.settings?.available!==false||r.status?.state!=='disabled')throw new Error('voice_offline_contract');this.snapshot=r.status;this.settings=r.settings;}
 html(){return voiceSettings(this.settings,this.snapshot);}
 canSubmit(_turn:UserTurn){return false;}
 onFinal(_listener:(turn:UserTurn)=>void){return ()=>{};}
 onInterrupted(_listener:(event:SpeechInterrupted)=>void){return ()=>{};}
 async speak(_request:SpeechOutputRequest):Promise<void>{throw new Error('voice_offline_unavailable');}
 stopPlayback(){} // No playback device exists in this adapter.
 receipt(_receipt:UserTurnReceipt){}
 failure(_code:string){}
 dispose(){this.consumer.dispose();}
}
