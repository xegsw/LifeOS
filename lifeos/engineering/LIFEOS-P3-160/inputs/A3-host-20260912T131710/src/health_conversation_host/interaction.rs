//! Additive interaction envelope. Existing drafts, proactive response and v8 remain authoritative.
use super::*;
use crate::interaction_contract::{Origin,Ref,UserTurn,SpeechInterrupted};
use sha2::{Digest,Sha256};
fn hash(v:&Value)->String{format!("{:x}",Sha256::digest(v.to_string().as_bytes()))}
pub(super) fn iso(at:i64)->R<String>{unsafe{let seconds:libc::time_t=at/1000;let mut tm:libc::tm=std::mem::zeroed();if libc::gmtime_r(&seconds,&mut tm).is_null(){return Err(error("interaction_clock_unavailable"))}let mut bytes=[0i8;64];let size=libc::strftime(bytes.as_mut_ptr(),bytes.len(),c"%Y-%m-%dT%H:%M:%SZ".as_ptr(),&tm);if size==0{return Err(error("interaction_clock_unavailable"))}Ok(std::ffi::CStr::from_ptr(bytes.as_ptr()).to_string_lossy().into_owned())}}
fn allocation_key(turn:&str)->String{format!("interaction:turn:{turn}")}
#[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]
struct Allocate {correlation_id:String,conversation_ref:Ref,origin:Origin,#[serde(default)]reply_to:Option<Ref>,#[serde(default)]presented_proactive_ref:Option<Ref>}
#[derive(Deserialize)]#[serde(deny_unknown_fields)]struct Envelope {version:String,operation:String,payload:Value}
impl Store {
 pub(crate) fn interaction_dispatch(&self,command:&str,value:Value)->R<Value>{
  if !no_null(&value){return Err(error("interaction_contract_rejected"))}
  let e:Envelope=decode(value)?;if e.version!="interaction-v1"{return Err(error("interaction_contract_rejected"))}
  // D0676 currently authorizes this bridge only in offline integration.
  if crate::runtime_root::network_enabled(){return Err(error("interaction_offline_only"))}
  let result=match(command,e.operation.as_str()){
   ("resolve_request_context","allocate_user_turn")=>self.interaction_allocate(e.payload)?,
   ("capture_record","submit_user_turn")=>self.interaction_submit(e.payload)?,
   ("get_context_recovery","interaction_turn_status")=>{
    #[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Status{turn_id:String}
    let d:Status=decode(e.payload)?;self.interaction_status(&d.turn_id)?
   },
   ("get_context_recovery","interaction_outputs")=>{if e.payload!=json!({}){return Err(error("interaction_contract_rejected"))}self.interaction_outputs()?},
   ("decide_understanding_feedback","speech_interrupted")=>{
    let event:SpeechInterrupted=decode(e.payload)?;if event.schema_version!="interaction-v1"{return Err(error("interaction_contract_rejected"))}
    // No active host speech authorization exists in A yet. An untrusted interrupt cannot alter business state.
    return Err(error("speech_request_not_authorized"))
   },_=>return Err(error("operation_rejected"))};
  Ok(json!({"version":"interaction-v1","operation":e.operation,"result":result}))
 }
 pub(super) fn interaction_allocate(&self,payload:Value)->R<Value>{
  let d:Allocate=decode(payload.clone())?;
  id(&d.correlation_id)?;
  if d.conversation_ref.id!="source-chat"||d.conversation_ref.revision!=1{return Err(error("interaction_conversation_stale"))}
  if !matches!(d.origin,Origin::Keyboard){let segment=self.voice_validate_origin(&d.origin,None)?;if segment["segmentId"]!=d.correlation_id||d.reply_to.is_some()||d.presented_proactive_ref.is_some(){return Err(error("voice_segment_conflict"))}}
  if !enabled(&self.c,"conversation")?{return Err(error("source_not_authorized"))}
  let key=format!("interaction:correlation:{}",hash(&json!([d.conversation_ref,d.correlation_id])));
  self.tx(&key,"interaction_allocate",&payload,|c|{
   let canonical=crate::conversation_store::uid("user-turn");
   let row=json!({"kind":"interaction_allocation","schemaVersion":1,"turnId":canonical,"legacyTurnId":d.correlation_id,"conversationRef":d.conversation_ref,"origin":d.origin,"replyTo":d.reply_to,"presentedProactiveRef":d.presented_proactive_ref,"status":"allocated","allocatedAt":now()});
   put(c,"sources",&allocation_key(&canonical),&row)?;
   Ok(json!({"turnId":canonical,"conversationRef":d.conversation_ref,"allocatedAt":row["allocatedAt"]}))
  })
 }
 fn interaction_submit(&self,payload:Value)->R<Value>{
  let turn:UserTurn=decode(payload.clone())?;
  if turn.schema_version!="interaction-v1"||turn.text.trim().is_empty()||turn.text.len()>8192||turn.finalized_at.len()>40||turn.finalized_at.is_empty(){return Err(error("interaction_contract_rejected"))}
  let key=allocation_key(&turn.turn_id);let mut row=get(&self.c,"sources",&key)?.ok_or_else(||error("interaction_turn_unallocated"))?;
  if row["conversationRef"]!=json!(turn.conversation_ref)||row["origin"]!=json!(turn.origin)||row["replyTo"]!=json!(turn.reply_to)||row["presentedProactiveRef"]!=json!(turn.presented_proactive_ref){return Err(error("interaction_conversation_stale"))}
  if !matches!(turn.origin,Origin::Keyboard){self.voice_validate_origin(&turn.origin,Some(&turn.text))?;}
  if turn.interrupted_speech_request_id.is_some(){return Err(error("speech_request_not_authorized"))}
  let digest=hash(&payload);
  if row.get("submittedDigest").is_some_and(|h|h!=&json!(digest)){return Err(error("idempotency_conflict"))}
  if row["status"]=="linked"{let mut status=self.interaction_status(&turn.turn_id)?;if status["receipt"]["status"]=="accepted"{status["receipt"]["status"]=json!("duplicate")}return Ok(status)}
  // Reserve the immutable envelope before any downstream prepare. Replays resume the same legacy request.
  self.tx(&format!("interaction:submit:{}",turn.turn_id),"interaction_submit",&payload,|c|{row["submittedDigest"]=json!(digest);row["status"]=json!("pending");put(c,"sources",&key,&row)?;Ok(json!({"reserved":true}))})?;
  if let Some(target)=turn.reply_to.as_ref(){
   let out=self.proactive_dispatch("resolve_request_context",json!({"version":"proactive-v1","operation":"prepare_proactive_response","payload":{"requestId":format!("interaction:{}",turn.turn_id),"suggestionId":target.id,"expectedRevision":target.revision,"text":turn.text}}))?;
   row["proactiveRequestId"]=out["result"]["requestId"].clone();row["recordRef"]=json!({"id":out["result"]["rawRef"],"revision":1});
  }else{
   let legacy=row["legacyTurnId"].as_str().unwrap();let draft=get(&self.c,"drafts",&format!("draft:{legacy}"))?;
   if draft.as_ref().is_some_and(|d|d["text"]!=turn.text){return Err(error("interaction_draft_changed"))}
   if draft.is_none(){self.coordination_dispatch("capture_record","save_coordination_draft",json!({"requestId":format!("interaction:draft:{}",turn.turn_id),"turnId":legacy,"expectedDraftRevision":0,"text":turn.text}))?;}
  }
  row["status"]=json!("linked");
  self.tx(&format!("interaction:linked:{}",turn.turn_id),"interaction_linked",&json!({"turnId":turn.turn_id}),|c|{put(c,"sources",&key,&row)?;Ok(json!({"linked":true}))})?;
  self.interaction_status(&turn.turn_id)
 }
 fn interaction_outputs(&self)->R<Value>{
  let mut query=self.c.prepare("SELECT body FROM sources WHERE json_extract(body,'$.kind')='interaction_allocation' AND json_extract(body,'$.status')='linked' ORDER BY rowid DESC LIMIT 32")?;
  let rows=query.query_map([],|r|r.get::<_,String>(0))?.collect::<Result<Vec<_>,_>>()?;let mut turns=vec![];
  for raw in rows {
   let allocation:Value=serde_json::from_str(&raw).map_err(|_|error("store_contract_rejected"))?;
   let canonical=allocation["turnId"].as_str().unwrap();let legacy=allocation["legacyTurnId"].as_str().unwrap();
   let mut content=None;let mut origin="conversation";let mut at=allocation["allocatedAt"].as_i64().unwrap_or(0);
   if let Some(request_id)=allocation["proactiveRequestId"].as_str(){
    let result=self.proactive_dispatch("decide_understanding_feedback",json!({"version":"proactive-v1","operation":"proactive_response","payload":{"requestId":request_id}}))?;
    let r=&result["result"];let outcome=&r["outcome"];origin="proactive";
    if r["status"]=="committed" {if let Some(reply)=outcome["reply"].as_str(){content=Some(json!({"kind":"response","text":reply}));}}
    else if r["status"]=="failed" {content=Some(json!({"kind":"error","text":"回应未完成，原输入保留。","code":outcome["errorCode"]}));}
   }else if let Some(receipt)=get(&self.c,"packets",&format!("coord8:committed:{legacy}"))?{
    if receipt["state"]=="committed"{
     at=receipt["committedAt"].as_i64().unwrap_or(at);
     content=Some(if receipt["result"]["businessChanged"]==true {origin="transaction";json!({"kind":"receipt","text":receipt["reply"],"receiptRef":{"id":receipt["operationId"],"revision":1}})}else if receipt["result"]["kind"]=="clarify" {json!({"kind":"question","text":receipt["reply"]})}else{json!({"kind":"response","text":receipt["reply"]})});
    }
   }
   if let Some(content)=content{let mut output=json!({"schemaVersion":"interaction-v1","turnRef":{"id":format!("assistant:{canonical}"),"revision":1},"conversationRef":allocation["conversationRef"],"inReplyToTurnId":canonical,"origin":origin,"content":content,"finalizedAt":iso(at)?});if allocation["replyTo"].is_object(){output["proactiveRef"]=allocation["replyTo"].clone();}turns.push(output);}
  }
  // Only the current Host-approved projection crosses the proactive surface boundary.
  let view=self.proactive_dispatch("get_today",json!({"version":"proactive-v1","operation":"proactive_view","payload":{}}))?;
  for item in view["result"]["items"].as_array().unwrap_or(&vec![]){
   let d=&item["suggestion"];let candidate=&d["candidate"];let mut content=if candidate["kind"]=="question"{json!({"kind":"question","text":candidate["question"]})}else{json!({"kind":"suggestion","text":candidate["proposal"],"whyNow":candidate["whyNow"],"evidenceRefs":d["evidenceSnapshot"].as_array().unwrap().iter().map(|r|json!({"id":r["id"],"revision":r["version"]})).collect::<Vec<_>>(),"inferenceFlags":candidate["inferenceFlags"]})};
   if content["kind"]=="question" {content["text"]=json!(format!("{}\n{}",candidate["question"].as_str().unwrap_or(""),candidate["whyNow"].as_str().unwrap_or("")));}
   turns.push(json!({"schemaVersion":"interaction-v1","turnRef":{"id":format!("assistant:{}",d["id"].as_str().unwrap()),"revision":d["revision"]},"conversationRef":{"id":"source-chat","revision":1},"origin":"proactive","proactiveRef":{"id":d["id"],"revision":item["state"]["revision"]},"content":content,"finalizedAt":iso(d["createdAt"].as_i64().unwrap_or(0))?}));
  }
  for turn in &turns {let _:crate::interaction_contract::AssistantTurn=decode(turn.clone())?;}
  Ok(json!({"turns":turns,"speechRequests":[]}))
 }
 fn interaction_status(&self,turn_id:&str)->R<Value>{
  let row=get(&self.c,"sources",&allocation_key(turn_id))?.ok_or_else(||error("interaction_turn_unallocated"))?;
  let legacy=row["legacyTurnId"].as_str().unwrap();let raw=format!("coord8:raw:{legacy}");
  let record=if row.get("recordRef").is_some(){Some(row["recordRef"].clone())}else if get(&self.c,"records",&raw)?.is_some(){Some(json!({"id":raw,"revision":1}))}else{None};
  let receipt=if let Some(record)=record{json!({"turnId":turn_id,"status":"accepted","recordRef":record})}else{json!({"turnId":turn_id,"status":"pending_authorization","code":"existing_conversation_confirmation_required"})};
  Ok(json!({"receipt":receipt,"legacyTurnId":legacy,"proactiveRequestId":row.get("proactiveRequestId")}))
 }
}

#[cfg(test)]mod tests{
 use super::*;
 fn setup()->Store{super::super::controlled_tests::store()}
 fn allocation()->Value{json!({"correlationId":"legacy-keyboard-uuid","conversationRef":{"id":"source-chat","revision":1},"origin":{"kind":"keyboard"}})}
 fn turn(a:&Value)->Value{json!({"schemaVersion":"interaction-v1","turnId":a["turnId"],"conversationRef":a["conversationRef"],"origin":{"kind":"keyboard"},"text":"合成项目需要讨论","finalizedAt":"2026-09-12T10:00:00Z"})}
 #[test]fn interaction_host_allocates_canonical_and_keeps_legacy_ids(){let s=setup();let a=s.interaction_allocate(allocation()).unwrap();assert_ne!(a["turnId"],"legacy-keyboard-uuid");assert_eq!(s.interaction_allocate(allocation()).unwrap(),a);let t=turn(&a);let r=s.interaction_submit(t.clone()).unwrap();assert_eq!(r["receipt"]["status"],"pending_authorization");assert_eq!(r["legacyTurnId"],"legacy-keyboard-uuid");assert_eq!(s.interaction_submit(t).unwrap(),r);assert_eq!(get(&s.c,"drafts","draft:legacy-keyboard-uuid").unwrap().unwrap()["text"],"合成项目需要讨论");assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn interaction_changed_text_canonical_and_conversation_are_rejected(){let s=setup();let a=s.interaction_allocate(allocation()).unwrap();let t=turn(&a);s.interaction_submit(t.clone()).unwrap();let mut changed=t.clone();changed["text"]=json!("替换原文");assert_eq!(s.interaction_submit(changed).unwrap_err().code,"idempotency_conflict");let mut other=t.clone();other["turnId"]=json!("forged");assert!(s.interaction_submit(other).is_err());let mut other=t;other["conversationRef"]["revision"]=json!(2);assert!(s.interaction_submit(other).is_err());}
 #[test]fn interaction_partial_and_ungranted_voice_never_submit(){let s=setup();let a=s.interaction_allocate(allocation()).unwrap();let mut t=turn(&a);t["partial"]=json!(true);assert!(s.interaction_submit(t).is_err());let mut a=allocation();a["origin"]=json!({"kind":"voice","sessionId":"session","segmentId":"segment","asrRequestId":"asr","language":"zh-CN"});assert_eq!(s.interaction_allocate(a).unwrap_err().code,"voice_session_not_authorized");assert!(get(&s.c,"drafts","draft:legacy-keyboard-uuid").unwrap().is_none());}
 #[test]fn interaction_pending_mapping_recovers_after_downstream_fault(){let s=setup();let a=s.interaction_allocate(allocation()).unwrap();let t=turn(&a);s.c.execute_batch("CREATE TEMP TRIGGER interaction_fault BEFORE INSERT ON drafts BEGIN SELECT RAISE(ABORT,'synthetic downstream fault'); END;").unwrap();assert!(s.interaction_submit(t.clone()).is_err());assert!(get(&s.c,"drafts","draft:legacy-keyboard-uuid").unwrap().is_none());s.c.execute_batch("DROP TRIGGER interaction_fault").unwrap();assert_eq!(s.interaction_submit(t.clone()).unwrap()["receipt"]["status"],"pending_authorization");assert_eq!(s.interaction_submit(t).unwrap()["legacyTurnId"],"legacy-keyboard-uuid");}
 #[test]fn interaction_metadata_does_not_consume_old_pages(){let s=setup();let before=list(&s.c,"sources",16).unwrap();for n in 0..20{let mut a=allocation();a["correlationId"]=json!(format!("legacy-{n}"));s.interaction_allocate(a).unwrap();}assert_eq!(list(&s.c,"sources",16).unwrap(),before);}
 #[test]fn interaction_user_turn_mirror_roundtrips_without_business_fields(){let a=json!({"turnId":"host-turn","conversationRef":{"id":"source-chat","revision":1}});let v=turn(&a);let decoded:UserTurn=serde_json::from_value(v.clone()).unwrap();assert_eq!(serde_json::to_value(decoded).unwrap(),v);let mut bad=v;bad["authorized"]=json!(true);assert!(serde_json::from_value::<UserTurn>(bad).is_err());}
}
