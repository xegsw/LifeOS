//! A-only Host-owned speech registry. No native permission or network route is enabled.
use super::*;
use crate::interaction_contract::{Ref,SpeechOutputRequest,SpeechInterrupted};
use crate::voice::{gateway::{Authority,Binding,Gateway,Transport,Frame,Outcome},budget::{Purpose,Phase}};
use super::voice_host::VoiceBudgetStore;
fn digest(v:&Value)->String{use sha2::{Digest,Sha256};format!("{:x}",Sha256::digest(v.to_string().as_bytes()))}
fn key(id:&str)->String{format!("voice:speech:{id}")}
struct SpeechAuthority<'a>{store:&'a Store,visible:&'a dyn Fn()->bool}
impl Authority for SpeechAuthority<'_>{
 fn check(&self,b:&Binding,p:Purpose)->Result<(),&'static str>{if p!=Purpose::Tts{return Err("voice_purpose_denied")}self.store.voice_speech_projection(b,(self.visible)()).map(|_|()).map_err(|_|"voice_output_invalidated")}
 fn projection(&self,b:&Binding)->Result<String,&'static str>{self.store.voice_speech_projection(b,(self.visible)()).map_err(|_|"voice_output_invalidated")}
 fn now(&self)->(u64,u64){let at=now().max(0) as u64;(at,at/86_400_000)}
}
impl Store{
 fn voice_output_session(&self,session:&str,generation:u64,revision:u64)->R<()>{
  let policy=get(&self.c,"sources","voice:policy")?.ok_or_else(||error("speech_request_not_authorized"))?;
  let state=get(&self.c,"sources",&format!("voice:session:{session}"))?.ok_or_else(||error("speech_request_not_authorized"))?;
  if crate::runtime_root::network_enabled()||policy["scope"]!="A_contract_fake"||policy["enabled"]!=true||policy["tts"]!=true||policy["revision"]!=revision||state["state"]!="active"||state["generation"]!=generation||state["policyRevision"]!=revision||!enabled(&self.c,"conversation")?{return Err(error("speech_request_not_authorized"))}Ok(())
 }
 fn voice_current_output(&self,reference:&Ref,visible_now:bool)->R<Value>{
  let outputs=self.interaction_outputs()?;
  let mut matches=outputs["turns"].as_array().ok_or_else(||error("speech_projection_stale"))?.iter().filter(|t|t["turnRef"]==json!(reference));
  let output=matches.next().ok_or_else(||error("speech_projection_stale"))?.clone();if matches.next().is_some(){return Err(error("speech_projection_stale"))}
  if output["origin"]=="proactive"{
   if !visible_now{return Err(error("speech_projection_stale"))}
   let visible=self.proactive_view()?;let target=&output["proactiveRef"];
   if !visible["items"].as_array().is_some_and(|items|items.iter().any(|i|i["suggestion"]["id"]==target["id"]&&i["state"]["revision"]==target["revision"]&&i["state"]["status"]=="surfaced")){return Err(error("speech_projection_stale"))}
  }Ok(output)
 }
 // Native host decides when to register a current output; no arbitrary text/IPC grant.
 pub(super) fn voice_register_speech(&self,session:&str,generation:u64,revision:u64,reference:&Ref,visible_now:bool)->R<SpeechOutputRequest>{
  self.voice_output_session(session,generation,revision)?;
  let output=self.voice_current_output(reference,visible_now)?;let hash=digest(&output);
  let projection=Ref{id:format!("voice-projection:{hash}"),revision:1};
  let identity=digest(&json!([session,generation,revision,reference,projection]));
  let result=self.tx(&format!("voice:speech-register:{identity}"),"voice_speech_register",&json!({"sessionId":session,"generation":generation,"policyRevision":revision,"assistantTurnRef":reference,"projectionRef":projection}),|c|{
   let request=SpeechOutputRequest{schema_version:"interaction-v1".into(),request_id:crate::conversation_store::uid("voice-tts"),session_id:session.into(),session_generation:generation,assistant_turn_ref:reference.clone(),proactive_decision_ref:if output["origin"]=="proactive"{Some(Ref{id:format!("voice-decision:{hash}"),revision:1})}else{None},projection_ref:projection,policy_revision:revision,voice:"mimo_default".into(),language:"zh-CN".into()};
   put(c,"sources",&key(&request.request_id),&json!({"kind":"voice_speech_binding","request":request,"outputDigest":hash,"state":"ready","decision":if let Some(d)=request.proactive_decision_ref.as_ref(){json!({"kind":"surface","schemaVersion":"interaction-v1","decisionRef":d,"proactiveRef":output["proactiveRef"],"assistantTurn":output})}else{Value::Null}}))?;Ok(json!(request))
  })?;decode(result)
 }
 fn voice_speech_projection(&self,b:&Binding,visible_now:bool)->R<String>{
  let row=get(&self.c,"sources",&key(&b.request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;
  let request:SpeechOutputRequest=decode(row["request"].clone())?;
  if row["kind"]!="voice_speech_binding"||!matches!(row["state"].as_str(),Some("ready"|"sending"|"draining"))||request.request_id!=b.request_id||request.session_id!=b.session_id||request.session_generation!=b.generation||request.policy_revision!=b.policy_revision{return Err(error("speech_request_not_authorized"))}
  self.voice_output_session(&b.session_id,b.generation,b.policy_revision)?;
  let output=self.voice_current_output(&request.assistant_turn_ref,visible_now)?;
  let hash=digest(&output);
  if row["outputDigest"]!=hash||request.projection_ref!= (Ref{id:format!("voice-projection:{hash}"),revision:1})||request.proactive_decision_ref!=(if output["origin"]=="proactive"{Some(Ref{id:format!("voice-decision:{hash}"),revision:1})}else{None}){return Err(error("speech_projection_stale"))}
  let content=&output["content"];let mut text=content["text"].as_str().ok_or_else(||error("speech_projection_stale"))?.to_owned();
  if content["kind"]=="suggestion"{text.push('\n');text.push_str(content["whyNow"].as_str().ok_or_else(||error("speech_projection_stale"))?);}
  if text.trim().is_empty()||text.chars().count()>4000{return Err(error("speech_projection_stale"))}Ok(text)
 }
 fn voice_speech_state(&self,id:&str,state:&str)->R<()>{
  self.tx(&format!("voice:speech-state:{id}:{state}"),"voice_speech_state",&json!({"requestId":id,"state":state}),|c|{let mut r=get(c,"sources",&key(id))?.ok_or_else(||error("speech_request_not_authorized"))?;if r["state"]=="interrupted"{return Ok(json!({"state":"interrupted"}))}if state=="sending"{let count:i64=c.query_row("SELECT COUNT(*) FROM sources WHERE json_extract(body,'$.kind')='voice_speech_binding' AND json_extract(body,'$.state') IN ('sending','draining')",[],|r|r.get(0))?;if count!=0{return Err(error("voice_concurrency"))}}r["state"]=json!(state);put(c,"sources",&key(id),&r)?;Ok(json!({"state":state}))})?;Ok(())
 }
 pub(super) fn voice_gateway_begin_tts(&self,g:&mut Gateway,request:&SpeechOutputRequest,visible:&dyn Fn()->bool,net:&mut dyn Transport)->R<Binding>{
  let row=get(&self.c,"sources",&key(&request.request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;
  if row["state"]!="ready"||row["request"]!=json!(request){return Err(error("speech_request_not_authorized"))}
  let b=Binding{request_id:request.request_id.clone(),session_id:request.session_id.clone(),generation:request.session_generation,policy_revision:request.policy_revision};self.voice_speech_projection(&b,visible())?;
  self.voice_speech_state(&b.request_id,"sending")?;
  if let Err(e)=g.begin_tts(b.clone(),Phase::BDevelopment,&SpeechAuthority{store:self,visible},&mut VoiceBudgetStore{store:self},net){self.voice_speech_state(&b.request_id,"failed")?;return Err(error(e))}Ok(b)
 }
 pub(super) fn voice_gateway_poll_tts(&self,g:&mut Gateway,id:&str,frame:Frame,visible:&dyn Fn()->bool,net:&mut dyn Transport)->R<Outcome>{
  let outcome=g.poll(Purpose::Tts,id,frame,&SpeechAuthority{store:self,visible},net);
  match outcome{Ok(Outcome::Complete)=>{self.voice_speech_state(id,"draining")?;Ok(Outcome::Complete)},Ok(v)=>Ok(v),Err(e)=>{self.voice_speech_state(id,"failed")?;Err(error(e))}}
 }
 // Called immediately before native enqueue AND each playback delivery boundary.
 // HTTP EOF only enters draining. Native completion is a separate acknowledgement.
 pub(super) fn voice_validate_playback(&self,request:&SpeechOutputRequest,visible_now:bool)->R<()>{
  let row=get(&self.c,"sources",&key(&request.request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;
  if row["request"]!=json!(request)||!matches!(row["state"].as_str(),Some("sending"|"draining")){return Err(error("speech_request_not_authorized"))}
  self.voice_speech_projection(&Binding{request_id:request.request_id.clone(),session_id:request.session_id.clone(),generation:request.session_generation,policy_revision:request.policy_revision},visible_now).map(|_|())
 }
 pub(super) fn voice_playback_completed(&self,request:&SpeechOutputRequest,visible_now:bool)->R<()>{
  self.voice_validate_playback(request,visible_now)?;
  let row=get(&self.c,"sources",&key(&request.request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;
  if row["state"]!="draining"{return Err(error("voice_playback_not_drained"))}self.voice_speech_state(&request.request_id,"complete")
 }
 pub(super) fn voice_speech_interrupted(&self,event:SpeechInterrupted)->R<Value>{
  let row=get(&self.c,"sources",&key(&event.speech_request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;let request:SpeechOutputRequest=decode(row["request"].clone())?;
  if crate::runtime_root::network_enabled()||event.schema_version!="interaction-v1"||event.event_id.is_empty()||event.event_id.len()>128||event.session_id!=request.session_id||event.session_generation!=request.session_generation||event.assistant_turn_ref!=request.assistant_turn_ref||!matches!(row["state"].as_str(),Some("ready"|"sending"|"draining"|"interrupted")){return Err(error("speech_request_not_authorized"))}
  self.tx(&format!("voice:interrupted:{}",event.event_id),"voice_speech_interrupted",&json!(event),|c|{let mut r=get(c,"sources",&key(&event.speech_request_id))?.ok_or_else(||error("speech_request_not_authorized"))?;r["state"]=json!("interrupted");put(c,"sources",&key(&event.speech_request_id),&r)?;Ok(json!({"status":"interrupted","speechRequestId":event.speech_request_id,"businessChanged":false}))})
 }
 // Native playback must stop immediately before reporting the event. This wrapper
 // cancels only this TTS request; it cannot cancel a concurrent ASR or business turn.
 pub(super) fn voice_gateway_interrupt_tts(&self,g:&mut Gateway,event:SpeechInterrupted,net:&mut dyn Transport)->R<Value>{
  let active=get(&self.c,"sources",&key(&event.speech_request_id))?.is_some_and(|r|r["state"]=="sending");
  let result=self.voice_speech_interrupted(event)?;if active{g.cancel(Purpose::Tts,net);}Ok(result)
 }
}

#[cfg(test)]pub(super) mod tests{
 use super::*;use crate::voice::{budget::Ledger,mimo::RequestBody};
 #[derive(Default)]struct Fake{starts:usize,cancels:usize,body:String}
 impl Transport for Fake{fn start(&mut self,_:&str,url:&str,body:RequestBody)->Result<(),&'static str>{assert_eq!(url,crate::voice::mimo::ENDPOINT);self.starts+=1;self.body=String::from_utf8(body.0.clone()).unwrap();Ok(())}fn cancel(&mut self,_:&str){self.cancels+=1;}}
 pub(crate) fn setup()->(Store,Ref){let s=super::super::controlled_tests::store();put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"tts":true,"revision":1})).unwrap();put(&s.c,"sources","voice:session:speech-fixture",&json!({"state":"active","generation":1,"policyRevision":1})).unwrap();put(&s.c,"sources","voice:budget",&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();let a=s.interaction_allocate(json!({"correlationId":"speech-fixture-turn","conversationRef":{"id":"source-chat","revision":1},"origin":{"kind":"keyboard"}})).unwrap();let canonical=a["turnId"].as_str().unwrap();let mut row=get(&s.c,"sources",&format!("interaction:turn:{canonical}")).unwrap().unwrap();row["status"]=json!("linked");put(&s.c,"sources",&format!("interaction:turn:{canonical}"),&row).unwrap();put(&s.c,"packets","coord8:committed:speech-fixture-turn",&json!({"state":"committed","committedAt":1800000000000i64,"result":{"businessChanged":false,"kind":"discuss"},"reply":"这是一条经过宿主投影的合成回复。"})).unwrap();let reference=Ref{id:format!("assistant:{canonical}"),revision:1};(s,reference)}
 fn event(r:&SpeechOutputRequest,id:&str)->SpeechInterrupted{serde_json::from_value(json!({"schemaVersion":"interaction-v1","eventId":id,"sessionId":r.session_id,"sessionGeneration":r.session_generation,"speechRequestId":r.request_id,"assistantTurnRef":r.assistant_turn_ref,"reason":"user_stop","occurredAt":"2026-09-12T13:00:00Z"})).unwrap()}
 #[test]fn voice_speech_registry_projects_host_text_and_rejects_forged_or_duplicate_request(){let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();assert_eq!(s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap(),request);let mut g=Gateway::new();let mut net=Fake::default();let mut forged=request.clone();forged.projection_ref.revision=99;assert!(s.voice_gateway_begin_tts(&mut g,&forged,&||true,&mut net).is_err());assert_eq!(net.starts,0);let b=s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();assert_eq!(net.starts,1);assert!(net.body.contains("经过宿主投影"));assert!(s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).is_err());assert!(s.voice_gateway_poll_tts(&mut g,&b.request_id,Frame::Headers(200),&||true,&mut net).is_ok());assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn voice_speech_changed_projection_or_permission_cancels_before_next_chunk(){for mode in ["text","conversation","policy","generation","output"]{let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut net=Fake::default();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();match mode{"text"=>{let mut p=get(&s.c,"packets","coord8:committed:speech-fixture-turn").unwrap().unwrap();p["reply"]=json!("新的回复");put(&s.c,"packets","coord8:committed:speech-fixture-turn",&p).unwrap();},"output"=>{s.c.execute("DELETE FROM packets WHERE id='coord8:committed:speech-fixture-turn'",[]).unwrap();},"conversation"=>{let mut p=get(&s.c,"sources","conversation").unwrap().unwrap();p["authorized"]=json!(false);put(&s.c,"sources","conversation",&p).unwrap();},"policy"=>{put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"tts":false,"revision":2})).unwrap();},_=>{put(&s.c,"sources","voice:session:speech-fixture",&json!({"state":"active","generation":2,"policyRevision":1})).unwrap();}}
 assert!(s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Headers(200),&||true,&mut net).is_err(),"{mode}");assert_eq!(net.cancels,1);assert_eq!(net.starts,1);assert_eq!(get(&s.c,"sources","voice:budget").unwrap().unwrap()["ledger"]["reservations"].as_array().unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());}}
 #[test]fn voice_speech_interrupt_is_bound_idempotent_and_never_business_feedback(){let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut net=Fake::default();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();let mut forged=event(&request,"forged");forged.session_generation=2;assert!(s.voice_gateway_interrupt_tts(&mut g,forged,&mut net).is_err());assert_eq!(net.cancels,0);let result=s.voice_gateway_interrupt_tts(&mut g,event(&request,"stop-1"),&mut net).unwrap();assert_eq!(result["businessChanged"],false);assert_eq!(net.cancels,1);assert_eq!(s.voice_gateway_interrupt_tts(&mut g,event(&request,"stop-1"),&mut net).unwrap(),result);assert_eq!(net.cancels,1);assert!(s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Eof,&||true,&mut net).is_err());assert!(s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).is_err());assert!(Store::actions(&s.c).unwrap().is_empty());assert_eq!(get(&s.c,"packets","coord8:committed:speech-fixture-turn").unwrap().unwrap()["reply"],"这是一条经过宿主投影的合成回复。");}
 #[test]fn voice_speech_restart_invalidates_registered_output(){let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let path=PathBuf::from(s.c.path().unwrap());drop(s);let s=Store::open(&path).unwrap();let mut net=Fake::default();assert!(s.voice_gateway_begin_tts(&mut Gateway::new(),&request,&||true,&mut net).is_err());assert_eq!(net.starts,0);}
 fn chunk(delta:Value,finish:Value)->Frame{Frame::Data(format!("data: {}\n\n",json!({"id":"tts-fixture","object":"chat.completion.chunk","model":"mimo-v2.5-tts","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes())}
 #[test]fn voice_speech_pcm_rechecked_at_sink_and_eof_is_not_playback_completion(){
  use crate::voice::{audio::Playback,mimo::Part};
  let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut net=Fake::default();let mut playback=Playback::new();let epoch=playback.begin();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Headers(200),&||true,&mut net).unwrap();
  let Outcome::Parts(parts)=s.voice_gateway_poll_tts(&mut g,&request.request_id,chunk(json!({"audio":{"id":"audio-fixture","data":"AAABAA=="}}),Value::Null),&||true,&mut net).unwrap() else{panic!()};let pcm=parts.into_iter().find_map(|p|if let Part::Pcm(v)=p{Some(v)}else{None}).unwrap();s.voice_validate_playback(&request,true).unwrap();playback.push(epoch,&pcm).unwrap();assert_eq!(playback.queued(),2);assert!(s.voice_playback_completed(&request,true).is_err());
  s.voice_gateway_poll_tts(&mut g,&request.request_id,chunk(json!({}),json!("stop")),&||true,&mut net).unwrap();s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Data(b"data: [DONE]\n\n".to_vec()),&||true,&mut net).unwrap();assert!(matches!(s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Eof,&||true,&mut net).unwrap(),Outcome::Complete));assert_eq!(get(&s.c,"sources",&key(&request.request_id)).unwrap().unwrap()["state"],"draining");assert_eq!(playback.queued(),2);s.voice_validate_playback(&request,true).unwrap();
  // Fake sink completion explicitly drains; HTTP EOF above did not claim playback.
  let consumed=playback.drain(2);assert_eq!(consumed.0.len(),2);drop(consumed);assert_eq!(playback.queued(),0);s.voice_playback_completed(&request,true).unwrap();assert!(s.voice_validate_playback(&request,true).is_err());assert_eq!(net.starts,1);
 }
 #[test]fn voice_speech_revocation_between_parser_and_enqueue_rejects_returned_pcm(){let(s,reference)=setup();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut net=Fake::default();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Headers(200),&||true,&mut net).unwrap();assert!(matches!(s.voice_gateway_poll_tts(&mut g,&request.request_id,chunk(json!({"audio":{"id":"audio-fixture","data":"AAABAA=="}}),Value::Null),&||true,&mut net).unwrap(),Outcome::Parts(_)));let mut p=get(&s.c,"sources","voice:policy").unwrap().unwrap();p["tts"]=json!(false);put(&s.c,"sources","voice:policy",&p).unwrap();assert!(s.voice_validate_playback(&request,true).is_err());assert!(s.voice_gateway_poll_tts(&mut g,&request.request_id,Frame::Connecting,&||true,&mut net).is_err());assert_eq!(net.cancels,1);}

 #[test]fn voice_speech_interrupt_preserves_concurrent_asr_and_stale_stop_cannot_cancel_new_output(){let(s,reference)=setup();let mut p=get(&s.c,"sources","voice:policy").unwrap().unwrap();p["asr"]=json!(true);p["sessionTurn"]=json!(true);put(&s.c,"sources","voice:policy",&p).unwrap();let request=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut net=Fake::default();let asr=s.voice_gateway_begin_asr(&mut g,"speech-fixture",1,1,crate::voice::audio::Audio(vec![0;1600]),&mut net).unwrap();s.voice_gateway_begin_tts(&mut g,&request,&||true,&mut net).unwrap();s.voice_gateway_interrupt_tts(&mut g,event(&request,"old-stop"),&mut net).unwrap();assert!(s.voice_gateway_poll_asr(&mut g,&asr.request_id,Frame::Headers(200),&mut net).is_ok());let mut output=get(&s.c,"packets","coord8:committed:speech-fixture-turn").unwrap().unwrap();output["reply"]=json!("新的合成回复");put(&s.c,"packets","coord8:committed:speech-fixture-turn",&output).unwrap();let new=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();s.voice_gateway_begin_tts(&mut g,&new,&||true,&mut net).unwrap();s.voice_gateway_interrupt_tts(&mut g,event(&request,"old-stop"),&mut net).unwrap();assert_eq!(net.cancels,1);assert!(s.voice_gateway_poll_tts(&mut g,&new.request_id,Frame::Headers(200),&||true,&mut net).is_ok());assert_eq!(net.starts,3);}

}
