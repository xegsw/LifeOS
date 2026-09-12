//! A offline integration. No device, credential or network grant is created here.
use super::*;
use crate::voice::budget::{BudgetStore,Ledger};
const BUDGET:&str="voice:budget";
pub(crate) struct VoiceBudgetStore<'a>{pub store:&'a Store}
fn ledger(c:&Connection)->Result<Ledger,&'static str>{
 let v=get(c,"sources",BUDGET).map_err(|_|"voice_budget_storage")?.ok_or("voice_budget_missing")?;
 if v["kind"]!="voice_budget"||v.as_object().map_or(true,|o|o.len()!=2){return Err("voice_budget_corrupt")}
 let l:Ledger=serde_json::from_value(v["ledger"].clone()).map_err(|_|"voice_budget_corrupt")?;
 if serde_json::to_value(&l).map_err(|_|"voice_budget_corrupt")?!=v["ledger"]||l.revision!=l.reservations.len() as u64{return Err("voice_budget_corrupt")}
 let mut ids=std::collections::HashSet::new();let mut at=0;let mut day=0;
 for r in &l.reservations{if r.id.is_empty()||!ids.insert(&r.id)||r.at_ms<at||r.day<day||r.units==0{return Err("voice_budget_corrupt")}at=r.at_ms;day=r.day;}
 if at!=l.high_water_ms||day!=l.high_water_day{return Err("voice_budget_corrupt")}
 Ok(l)
}
impl BudgetStore for VoiceBudgetStore<'_>{
 fn load(&self)->Result<Ledger,&'static str>{ledger(&self.store.c)}
 fn compare_save(&mut self,previous:u64,next:Ledger)->Result<(),&'static str>{
  let proposed=serde_json::to_value(&next).map_err(|_|"voice_budget_corrupt")?;
  self.store.tx(&format!("voice:budget:{}:{}",previous,crate::conversation_store::uid("cas")),"voice_budget_reserve",&proposed,|c|{
   let old=ledger(c).map_err(error)?;
   if old.revision!=previous||next.revision!=previous+1||next.reservations.len()!=old.reservations.len()+1||next.high_water_ms<old.high_water_ms||next.high_water_day<old.high_water_day{return Err(error("voice_budget_conflict"))}
   for (a,b) in old.reservations.iter().zip(&next.reservations){if serde_json::to_value(a).unwrap()!=serde_json::to_value(b).unwrap(){return Err(error("voice_budget_conflict"))}}
   put(c,"sources",BUDGET,&json!({"kind":"voice_budget","ledger":proposed}))?;
   ledger(c).map_err(error)?;Ok(json!({"reserved":true}))
  }).map(|_|()).map_err(|_|"voice_budget_storage_or_conflict")
 }
}
impl Store{
 pub(super) fn voice_recover(c:&Connection)->R<()>{
  let count:i64=c.query_row("SELECT COUNT(*) FROM sources WHERE id LIKE 'voice:session:%' AND json_extract(body,'$.state')='active'",[],|r|r.get(0))?;if count==0{return Ok(())}if count>64{return Err(error("voice_session_corrupt"))}
  c.execute_batch("SAVEPOINT voice_recovery")?;
  let result=(||{c.execute("UPDATE sources SET body=json_set(body,'$.state','closed','$.generation',COALESCE(json_extract(body,'$.generation'),0)+1) WHERE id LIKE 'voice:session:%' AND json_extract(body,'$.state')='active'",[])?;c.execute("UPDATE meta SET revision=revision+1 WHERE id=1",[])?;Ok::<(),crate::repository::Error>(())})();
  match result{Ok(())=>{c.execute_batch("RELEASE voice_recovery")?;Ok(())},Err(e)=>{let _=c.execute_batch("ROLLBACK TO voice_recovery; RELEASE voice_recovery");Err(e)}}
 }
 pub(crate) fn voice_dispatch(&self,command:&str,v:Value)->R<Value>{
  #[derive(Deserialize)]#[serde(deny_unknown_fields)]struct Envelope{version:u8,payload:Value}
  #[derive(Deserialize)]#[serde(deny_unknown_fields)]struct Control{action:String}
  if !no_null(&v){return Err(error("voice_contract_rejected"))}let e:Envelope=decode(v)?;if e.version!=1{return Err(error("voice_contract_rejected"))}
  if command=="voice_control"{let d:Control=decode(e.payload)?;match d.action.as_str(){"status"|"disable"|"end_session"|"stop_playback"=>{},"enable"=>return Err(error("voice_offline_unavailable")),_=>return Err(error("voice_contract_rejected"))}}
  else if command!="voice_status"||e.payload!=json!({}){return Err(error("voice_contract_rejected"))}
  // Fixed unavailable state reflects the absence of an authorized native adapter.
  Ok(json!({"version":1,"status":{"state":"disabled","sessionId":null,"generation":0,"policyRevision":0},"settings":{"enabled":false,"asr":false,"tts":false,"sessionTurn":false,"wakeWord":"LifeOS","keyConfigured":false,"usageLabel":"真实调用 0 · 离线接线验证","available":false}}))
 }
}

fn voice_digest(text:&str)->String{use sha2::{Digest,Sha256};format!("{:x}",Sha256::digest(text.as_bytes()))}
impl Store{
 // Trusted audio worker entry only. Public voice_control cannot create a policy/session.
 fn voice_session(&self,id:&str,generation:u64,revision:u64)->R<Value>{
  let policy=get(&self.c,"sources","voice:policy")?.ok_or_else(||error("voice_session_not_authorized"))?;
  let session=get(&self.c,"sources",&format!("voice:session:{id}"))?.ok_or_else(||error("voice_session_not_authorized"))?;
  if crate::runtime_root::network_enabled()||policy["scope"]!="A_contract_fake"||policy["enabled"]!=true||policy["asr"]!=true||policy["sessionTurn"]!=true||policy["revision"]!=revision||session["state"]!="active"||session["generation"]!=generation||session["policyRevision"]!=revision||!enabled(&self.c,"conversation")?{return Err(error("voice_session_not_authorized"))}
  Ok(session)
 }
 pub(super) fn voice_validate_origin(&self,origin:&crate::interaction_contract::Origin,text:Option<&str>)->R<Value>{
  let crate::interaction_contract::Origin::Voice{session_id,segment_id,asr_request_id,language}=origin else{return Err(error("voice_session_not_authorized"))};
  let segment=get(&self.c,"sources",&format!("voice:asr:{asr_request_id}"))?.ok_or_else(||error("voice_session_not_authorized"))?;
  if segment["sessionId"]!=*session_id||segment["segmentId"]!=*segment_id||segment["status"]!="final"||language!="zh-CN"{return Err(error("voice_session_not_authorized"))}
  self.voice_session(session_id,segment["generation"].as_u64().ok_or_else(||error("voice_session_not_authorized"))?,segment["policyRevision"].as_u64().ok_or_else(||error("voice_session_not_authorized"))?)?;
  if text.is_some_and(|t|segment["textDigest"]!=voice_digest(t)){return Err(error("voice_segment_conflict"))}Ok(segment)
 }
 pub(super) fn voice_begin_segment(&self,session_id:&str,generation:u64,revision:u64)->R<Value>{
  self.voice_session(session_id,generation,revision)?;
  let request_id=crate::conversation_store::uid("voice-asr");let segment_id=crate::conversation_store::uid("voice-segment");
  self.tx(&format!("voice:segment:{request_id}"),"voice_segment",&json!({"sessionId":session_id,"generation":generation,"policyRevision":revision}),|c|{let r=json!({"kind":"voice_asr_binding","asrRequestId":request_id,"segmentId":segment_id,"sessionId":session_id,"generation":generation,"policyRevision":revision,"status":"pending"});put(c,"sources",&format!("voice:asr:{request_id}"),&r)?;Ok(r)})
 }
 // Called only for Gateway::Outcome::Final, never SSE partial/AudioEvent::Utterance.
 pub(super) fn voice_final_turn(&self,asr_request_id:&str,text:&str)->R<Value>{
  if text.trim().is_empty()||text.chars().count()>1000{return Err(error("voice_final_rejected"))}
  let key=format!("voice:asr:{asr_request_id}");let mut segment=get(&self.c,"sources",&key)?.ok_or_else(||error("voice_session_not_authorized"))?;
  let session_id=segment["sessionId"].as_str().ok_or_else(||error("voice_session_not_authorized"))?.to_owned();
  self.voice_session(&session_id,segment["generation"].as_u64().ok_or_else(||error("voice_session_not_authorized"))?,segment["policyRevision"].as_u64().ok_or_else(||error("voice_session_not_authorized"))?)?;
  let digest=voice_digest(text);
  if segment.get("textDigest").is_some_and(|v|v!=&json!(digest)){return Err(error("voice_segment_conflict"))}
  let finalized=self.tx(&format!("voice:final:{asr_request_id}"),"voice_final",&json!({"asrRequestId":asr_request_id,"textDigest":digest}),|c|{segment["status"]=json!("final");segment["textDigest"]=json!(digest);segment["finalizedAt"]=json!(now());put(c,"sources",&key,&segment)?;Ok(segment.clone())})?;
  let origin=json!({"kind":"voice","sessionId":session_id,"segmentId":finalized["segmentId"],"asrRequestId":asr_request_id,"language":"zh-CN"});
  let allocation=self.interaction_allocate(json!({"correlationId":finalized["segmentId"],"conversationRef":{"id":"source-chat","revision":1},"origin":origin}))?;
  Ok(json!({"schemaVersion":"interaction-v1","turnId":allocation["turnId"],"conversationRef":allocation["conversationRef"],"text":text,"origin":origin,"finalizedAt":super::interaction::iso(finalized["finalizedAt"].as_i64().unwrap())?}))
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::voice::budget::{reserve,Reservation,Purpose,Phase};
 fn store()->Store{super::super::controlled_tests::store()}
 fn r()->Reservation{Reservation{id:"a-only-reservation".into(),purpose:Purpose::Asr,phase:Phase::BDevelopment,at_ms:1000,day:1,units:1000}}
 #[test]fn voice_budget_missing_corrupt_and_cas_fail_closed(){let s=store();let mut b=VoiceBudgetStore{store:&s};assert!(reserve(&mut b,r()).is_err());put(&s.c,"sources",BUDGET,&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();reserve(&mut b,r()).unwrap();let saved=b.load().unwrap();assert_eq!(saved.revision,1);assert!(b.compare_save(0,saved.clone()).is_err());assert_eq!(b.load().unwrap().reservations.len(),1);assert!(reserve(&mut b,r()).is_err());put(&s.c,"sources",BUDGET,&json!({"kind":"voice_budget","ledger":{}})).unwrap();assert!(b.load().is_err());}
 #[test]fn voice_budget_reopen_retains_reservation_without_action_or_raw_write(){let s=store();put(&s.c,"sources",BUDGET,&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();reserve(&mut VoiceBudgetStore{store:&s},r()).unwrap();let path=PathBuf::from(s.c.path().unwrap());drop(s);let s=Store::open(&path).unwrap();assert_eq!(VoiceBudgetStore{store:&s}.load().unwrap().reservations.len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());assert!(list(&s.c,"sources",32).unwrap().iter().all(|r|r["kind"]!="voice_budget"));}
 #[test]fn voice_offline_controls_reject_permission_spoof_and_never_initialize_budget(){let s=store();let before:i64=s.c.query_row("SELECT revision FROM meta",[],|r|r.get(0)).unwrap();for action in ["status","disable","end_session","stop_playback"]{assert_eq!(s.voice_dispatch("voice_control",json!({"version":1,"payload":{"action":action}})).unwrap()["settings"]["available"],false);}assert!(s.voice_dispatch("voice_control",json!({"version":1,"payload":{"action":"enable","authorized":true}})).is_err());assert!(s.voice_dispatch("voice_control",json!({"version":1,"payload":{"action":"enable"}})).is_err());assert!(get(&s.c,"sources",BUDGET).unwrap().is_none());assert_eq!(s.c.query_row("SELECT revision FROM meta",[],|r|r.get::<_,i64>(0)).unwrap(),before);}
}

#[cfg(test)]mod final_tests{
 use super::*;
 fn store()->Store{let s=super::super::controlled_tests::store();put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"asr":true,"sessionTurn":true,"revision":1})).unwrap();put(&s.c,"sources","voice:session:fixture-session",&json!({"state":"active","generation":1,"policyRevision":1})).unwrap();s}
 fn submit(s:&Store,t:Value)->R<Value>{s.interaction_dispatch("capture_record",json!({"version":"interaction-v1","operation":"submit_user_turn","payload":t}))}
 #[test]fn voice_final_has_one_canonical_turn_and_recovers_across_reopen(){let s=store();let segment=s.voice_begin_segment("fixture-session",1,1).unwrap();let id=segment["asrRequestId"].as_str().unwrap();let turn=s.voice_final_turn(id,"讨论合成报告").unwrap();let result=submit(&s,turn.clone()).unwrap();assert_eq!(result["result"]["receipt"]["status"],"pending_authorization");let path=PathBuf::from(s.c.path().unwrap());drop(s);let s=Store::open(&path).unwrap();assert!(s.voice_final_turn(id,"讨论合成报告").is_err());let restored=s.interaction_dispatch("get_context_recovery",json!({"version":"interaction-v1","operation":"interaction_turn_status","payload":{"turnId":turn["turnId"]}})).unwrap();assert_eq!(restored["result"],result["result"]);assert!(submit(&s,turn).is_err());assert_eq!(list(&s.c,"drafts",32).unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn voice_partial_conflicting_text_and_arbitrary_correlation_cannot_duplicate(){let s=store();let segment=s.voice_begin_segment("fixture-session",1,1).unwrap();let id=segment["asrRequestId"].as_str().unwrap();let origin=json!({"kind":"voice","sessionId":"fixture-session","segmentId":segment["segmentId"],"asrRequestId":id,"language":"zh-CN"});assert!(s.interaction_allocate(json!({"correlationId":segment["segmentId"],"conversationRef":{"id":"source-chat","revision":1},"origin":origin})).is_err());let turn=s.voice_final_turn(id,"讨论合成报告").unwrap();assert!(s.voice_final_turn(id,"被替换的文本").is_err());assert!(s.interaction_allocate(json!({"correlationId":"forged-correlation","conversationRef":{"id":"source-chat","revision":1},"origin":origin})).is_err());let mut altered=turn.clone();altered["text"]=json!("改成另一个事项");assert!(submit(&s,altered).is_err());submit(&s,turn).unwrap();assert_eq!(list(&s.c,"drafts",32).unwrap().len(),1);}
 #[test]fn voice_late_final_and_unsubmitted_turn_fail_after_generation_or_policy_change(){for revoke in [false,true]{let s=store();let segment=s.voice_begin_segment("fixture-session",1,1).unwrap();let id=segment["asrRequestId"].as_str().unwrap();let turn=s.voice_final_turn(id,"讨论合成报告").unwrap();if revoke{put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":false,"asr":true,"sessionTurn":true,"revision":2})).unwrap();}else{put(&s.c,"sources","voice:session:fixture-session",&json!({"state":"active","generation":2,"policyRevision":1})).unwrap();}assert!(s.voice_final_turn(id,"讨论合成报告").is_err());assert!(submit(&s,turn).is_err());assert!(list(&s.c,"drafts",32).unwrap().is_empty());}}
}

// Offline joint adapter for the imported Gateway. The policy/session registry is
// re-read at each transport boundary; no IPC can construct this authority.
struct VoiceAsrAuthority<'a>{store:&'a Store}
impl crate::voice::gateway::Authority for VoiceAsrAuthority<'_>{
 fn check(&self,b:&crate::voice::gateway::Binding,p:crate::voice::budget::Purpose)->Result<(),&'static str>{
  if p!=crate::voice::budget::Purpose::Asr{return Err("voice_speech_registry_unavailable")}
  self.store.voice_session(&b.session_id,b.generation,b.policy_revision).map_err(|_|"voice_session_not_authorized")?;
  let r=get(&self.store.c,"sources",&format!("voice:asr:{}",b.request_id)).map_err(|_|"voice_registry_storage")?.ok_or("voice_registry_missing")?;
  if r["asrRequestId"]!=b.request_id||r["sessionId"]!=b.session_id||r["generation"]!=b.generation||r["policyRevision"]!=b.policy_revision||r["status"]!="pending"{return Err("voice_registry_stale")}Ok(())
 }
 fn projection(&self,_:&crate::voice::gateway::Binding)->Result<String,&'static str>{Err("voice_speech_registry_unavailable")}
 fn now(&self)->(u64,u64){let at=now().max(0) as u64;(at,at/86_400_000)}
}
impl Store{
 pub(super) fn voice_gateway_begin_asr(&self,g:&mut crate::voice::gateway::Gateway,session:&str,generation:u64,revision:u64,a:crate::voice::audio::Audio,net:&mut dyn crate::voice::gateway::Transport)->R<crate::voice::gateway::Binding>{
  let r=self.voice_begin_segment(session,generation,revision)?;
  let b=crate::voice::gateway::Binding{request_id:r["asrRequestId"].as_str().unwrap().into(),session_id:session.into(),generation,policy_revision:revision};
  g.begin_asr(b.clone(),a,crate::voice::budget::Phase::BDevelopment,&VoiceAsrAuthority{store:self},&mut VoiceBudgetStore{store:self},net).map_err(error)?;Ok(b)
 }
 pub(super) fn voice_gateway_poll_asr(&self,g:&mut crate::voice::gateway::Gateway,id:&str,frame:crate::voice::gateway::Frame,net:&mut dyn crate::voice::gateway::Transport)->R<Option<Value>>{
  let out=g.poll(crate::voice::budget::Purpose::Asr,id,frame,&VoiceAsrAuthority{store:self},net).map_err(error)?;
  match out{crate::voice::gateway::Outcome::Final(text)=>self.voice_final_turn(id,&text).map(Some),_=>Ok(None)}
 }
}
#[cfg(test)]mod gateway_joint_tests{
 use super::*;use crate::voice::{gateway::{Gateway,Transport,Frame},mimo::RequestBody,audio::Audio};
 #[derive(Default)]struct Fake{starts:usize,cancels:usize}
 impl Transport for Fake{fn start(&mut self,_:&str,url:&str,_:RequestBody)->Result<(),&'static str>{assert_eq!(url,crate::voice::mimo::ENDPOINT);self.starts+=1;Ok(())}fn cancel(&mut self,_:&str){self.cancels+=1;}}
 fn setup()->Store{let s=super::super::controlled_tests::store();put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"asr":true,"sessionTurn":true,"revision":1})).unwrap();put(&s.c,"sources","voice:session:joint",&json!({"state":"active","generation":1,"policyRevision":1})).unwrap();put(&s.c,"sources",BUDGET,&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();s}
 #[test]fn voice_joint_registry_rechecks_cancel_transport_and_retain_budget(){for changed in ["generation","policy","conversation"]{let s=setup();let mut g=Gateway::new();let mut net=Fake::default();let b=s.voice_gateway_begin_asr(&mut g,"joint",1,1,Audio(vec![1;1600]),&mut net).unwrap();assert_eq!(net.starts,1);assert_eq!(ledger(&s.c).unwrap().reservations.len(),1);if changed=="generation"{put(&s.c,"sources","voice:session:joint",&json!({"state":"active","generation":2,"policyRevision":1})).unwrap();}else if changed=="policy"{put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":false,"asr":true,"sessionTurn":true,"revision":2})).unwrap();}else{let mut source=get(&s.c,"sources","conversation").unwrap().unwrap();source["authorized"]=json!(false);put(&s.c,"sources","conversation",&source).unwrap();}assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Headers(200),&mut net).is_err());assert_eq!(net.cancels,1);assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Eof,&mut net).is_err());assert_eq!(net.starts,1);assert_eq!(ledger(&s.c).unwrap().reservations.len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());}}
 #[test]fn voice_joint_only_complete_gateway_final_enters_one_existing_preview(){
  let s=setup();let mut g=Gateway::new();let mut net=Fake::default();let b=s.voice_gateway_begin_asr(&mut g,"joint",1,1,Audio(vec![1;1600]),&mut net).unwrap();
  assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Headers(200),&mut net).unwrap().is_none());
  let event=|delta:Value,finish:Value|format!("data: {}\n\n",json!({"id":"joint-fixture","object":"chat.completion.chunk","model":"mimo-v2.5-asr","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes();
  assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Data(event(json!({"content":"讨论合成报告"}),Value::Null)),&mut net).unwrap().is_none());assert!(list(&s.c,"drafts",32).unwrap().is_empty());
  let mut stop=event(json!({}),json!("stop"));stop.extend(b"data: [DONE]\n\n");assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Data(stop),&mut net).unwrap().is_none());
  let turn=s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Eof,&mut net).unwrap().unwrap();assert_eq!(turn["text"],"讨论合成报告");assert_eq!(turn["origin"]["asrRequestId"],b.request_id);
  let out=s.interaction_dispatch("capture_record",json!({"version":"interaction-v1","operation":"submit_user_turn","payload":turn})).unwrap();assert_eq!(out["result"]["receipt"]["status"],"pending_authorization");assert_eq!(list(&s.c,"drafts",32).unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());assert!(s.voice_gateway_poll_asr(&mut g,&b.request_id,Frame::Eof,&mut net).is_err());assert_eq!(net.starts,1);
 }

}
