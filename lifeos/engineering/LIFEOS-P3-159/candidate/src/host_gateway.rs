use crate::{repository::Error,health_conversation_host::{Store,Start},model_port::{ModelPort,ModelResponse}};
use serde_json::{Value,json};use std::sync::{Arc,Mutex,OnceLock};
type R<T>=Result<T,Error>;
pub struct SyntheticControlledModel;
static MODEL_SERIAL:Mutex<()>=Mutex::new(());
impl ModelPort for SyntheticControlledModel {
 fn generate(&mut self,body:&str,key:&[u8])->R<ModelResponse>{self.generate_with_receipt(body,key,&mut||{})}
 fn generate_with_receipt(&mut self,body:&str,_key:&[u8],received:&mut dyn FnMut())->R<ModelResponse>{
  if crate::runtime_root::network_enabled(){return Err(Error::new("real_capability_denied"));}let value:Value=serde_json::from_str(body).map_err(|_|Error::new("provider_protocol"))?;let user:Value=serde_json::from_str(value["messages"][1]["content"].as_str().unwrap_or("")).map_err(|_|Error::new("provider_protocol"))?;if user["purpose"]=="proactive_analysis.v1"||user["purpose"]=="proactive_response.v1"{
   received();let p=std::path::Path::new(crate::health_conversation_host::ROOT).join("proactive-responses.json");
   let purpose=user["purpose"].as_str().unwrap();let label=if purpose=="proactive_response.v1"{user["currentUser"]["text"].as_str()}else{user["context"][0]["text"].as_str()}.unwrap_or("");
   let v=offline_fixture_bytes(&p).and_then(|b|serde_json::from_slice::<Value>(&b).ok()).and_then(|v|v[purpose][label].as_object().map(|o|Value::Object(o.clone()))).ok_or_else(||Error::new("proactive_fixture_missing"))?;
   return Ok(ModelResponse{text:v.to_string(),usage:None});
  }if user.get("currentUser").is_some(){
   received();
   let path=std::path::Path::new(crate::health_conversation_host::ROOT).join("coordination-responses.json");
   let raw=user["currentUser"]["text"].as_str().unwrap_or("");let phase=if user["queryResults"].as_array().is_some_and(|a|!a.is_empty()){"second"}else{"first"};
   let mut response=offline_fixture_bytes(&path).and_then(|b|serde_json::from_slice::<Value>(&b).ok()).and_then(|v|v.get(raw).and_then(|v|v.get(phase)).cloned()).unwrap_or(json!({"schemaVersion":8,"answerText":"公开合成替身未配置本条回答，未更改安排。","candidate":{"operation":"none"}}));
   fn bind(v:&mut Value,u:&Value){match v{Value::String(s)=>{let replacement=match s.as_str(){"__target0__"=>u["targets"][0]["ref"].as_str(),"__fact0__"=>u["queryResults"][0]["facts"][0]["ref"].as_str(),"__note__"=>u["capabilities"].as_array().and_then(|a|a.iter().find(|c|c["id"]=="fixture.note.lookup.v1")).and_then(|c|c["targets"][0]["ref"].as_str()),"__schedule__"=>u["capabilities"].as_array().and_then(|a|a.iter().find(|c|c["id"]=="fixture.schedule.lookup.v1")).and_then(|c|c["targets"][0]["ref"].as_str()),"__forecast__"=>u["capabilities"].as_array().and_then(|a|a.iter().find(|c|c["id"]=="fixture.forecast.lookup.v1")).and_then(|c|c["targets"][0]["ref"].as_str()),_=>None};if let Some(r)=replacement{*s=r.into()}},Value::Array(a)=>for x in a{bind(x,u)},Value::Object(o)=>for x in o.values_mut(){bind(x,u)},_=>()}}
   bind(&mut response,&user);return Ok(ModelResponse{text:response.to_string(),usage:None});
  }
  if user.get("current_user").is_some(){
   received();
   let path=std::path::Path::new(crate::health_conversation_host::ROOT).join("operation-responses.json");
   let raw=user["current_user"]["text"].as_str().unwrap_or("");
   let fixture=offline_fixture_bytes(&path).and_then(|b|serde_json::from_slice::<Value>(&b).ok()).and_then(|v|v.get(raw).cloned());
   let text=fixture.unwrap_or(json!({"schemaVersion":1,"answerText":"合成离线替身：尚未配置本条响应，未执行安排。","candidate":{"operation":"none"}})).to_string();
   return Ok(ModelResponse{text,usage:None});
  }
  let question=user["question"].as_str().unwrap_or("");received();std::thread::sleep(std::time::Duration::from_millis(1200));
  for (marker,code) in [("[模拟超时]","provider_timeout"),("[模拟网络错误]","provider_network"),("[模拟认证错误]","provider_authentication"),("[模拟模型错误]","provider_model")]{if question.contains(marker){return Err(Error::new(code));}}
  static FAILED:OnceLock<Mutex<std::collections::HashSet<String>>>=OnceLock::new();if question.contains("[模拟失败一次]")&&FAILED.get_or_init(Default::default).lock().unwrap().insert(question.into()){return Err(Error::new("provider_unavailable"));}
  let text=if user["items"].as_array().is_none_or(|v|v.is_empty()){String::from("合成演练 · 本次没有披露健康依据。离线适配器不具备开放域推理能力。")}
  else{let items=user["items"].as_array().unwrap();format!("合成演练 · 受控发送测试\n本次仅使用你确认的 {} 条资料。\n{}\n这是验证披露与回答链路的离线示例，不代表真实 DeepSeek 回答。",items.len(),items.iter().map(|r|format!("{} [{}]",r["text"].as_str().unwrap_or(""),r["citationId"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"))};let text=if question.contains("工作")&&question.contains("建议"){format!("{text}\n建议：整理报告结论。") }else{text};Ok(ModelResponse{text,usage:None})
 }
}
pub fn dispatch(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8])->R<Value>{if crate::runtime_root::network_enabled(){dispatch_with_port(store,command,bytes,&mut crate::provider_transport::DeepSeekModel)}else{dispatch_with_port(store,command,bytes,&mut SyntheticControlledModel)}}
pub(crate) fn dispatch_with_port(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8],port:&mut dyn ModelPort)->R<Value>{
 if lifeos_source_engine::COMMANDS.contains(&command){
  if bytes.len()>4096{return Err(Error::new("source_request_limit"));}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("source_contract_rejected"))?;crate::strict_json::parse(raw)?;
  let s=store.lock().map_err(|_|Error::new("store_busy"))?;
  let result=lifeos_source_engine::dispatch(command,bytes,&s.fixture()).map_err(|e|Error::new(&e.code))?;
  if ["connect_source_directory","control_source_job","authorize_source_target"].contains(&command){s.invalidate_notes()?;}
  return Ok(result)
 }
 if ["voice_status","voice_control"].contains(&command){if bytes.len()>1024{return Err(Error::new("voice_contract_rejected"))}let text=std::str::from_utf8(bytes).map_err(|_|Error::new("voice_contract_rejected"))?;let v=crate::strict_json::parse(text).map_err(|_|Error::new("voice_contract_rejected"))?;return store.lock().map_err(|_|Error::new("store_busy"))?.voice_dispatch(command,v)}
 if bytes.len()<=16384 {if let Ok(raw)=std::str::from_utf8(bytes){if let Ok(v)=crate::strict_json::parse(raw){if v["version"]=="interaction-v1"{return store.lock().map_err(|_|Error::new("store_busy"))?.interaction_dispatch(command,v)}if v["version"]=="proactive-v1"{return store.lock().map_err(|_|Error::new("store_busy"))?.proactive_dispatch(command,v)}}}}
 if command=="get_today"{return store.lock().map_err(|_|Error::new("store_busy"))?.health_view(bytes)}
 if bytes.len()>16384{return Err(Error::new("dto_rejected"));}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("dto_rejected"))?;let value=crate::strict_json::parse(raw)?;
 if command=="resolve_request_context"{crate::health_conversation_host::v8_signal_cancel(&value);}
 let mut guard=Some(store.lock().map_err(|_|Error::new("store_busy"))?);
 if command!="send_source_ai_request" {return guard.as_ref().unwrap().dispatch(command,bytes)}
 let r:crate::repository::Request=serde_json::from_value(value).map_err(|_|Error::new("dto_rejected"))?;if r.version==8 {
 if r.operation!="confirm_coordination_model"{return Err(Error::new("operation_rejected"))}
 let wrap=|v|json!({"version":8,"operation":"confirm_coordination_model","result":v});
 match guard.as_ref().unwrap().v8_consume(r.payload)?{
 crate::health_conversation_host::V8Start::Replay(v)=>return Ok(wrap(v)),
 crate::health_conversation_host::V8Start::Send(plan)=>{
 let Ok(_serial)=MODEL_SERIAL.try_lock() else{return guard.as_ref().unwrap().v8_finish(&plan,Err(Error::new("model_busy"))).map(wrap)};
 let refs=plan.turn["packet"]["snapshot"]["records"].as_array().unwrap().iter().filter_map(|r|r.get("engineRef").cloned()).collect::<Vec<_>>();
 let mut fence=match lifeos_source_engine::send_fence(&guard.as_ref().unwrap().fixture(),&refs){Ok(v)=>v,Err(_)=>return guard.as_ref().unwrap().v8_finish(&plan,Err(Error::new("source_not_authorized"))).map(wrap)};
 if let Some(v)=guard.as_ref().unwrap().v8_preflight(&plan)?{return Ok(wrap(v))}
 let remaining=plan.turn["activityBudget"]["reservedMs"].as_u64().unwrap().saturating_sub(plan.started.elapsed().as_millis() as u64);
 let mut diagnostics=crate::model_port::ModelDiagnostics::default();
 let result=if remaining==0{Err(Error::new("provider_timeout"))}else{port.generate_diagnosed_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,remaining,&mut||{drop(fence.take());drop(guard.take());},&mut|d|diagnostics=d)};drop(fence.take());drop(guard.take());
 let s=store.lock().map_err(|_|Error::new("response_storage_failed"))?;s.v8_record_model_diagnostics(&plan,&diagnostics)?;return s.v8_finish(&plan,result).map(wrap);
 }}
 }
 if r.version==7&&r.operation=="confirm_operation_turn"{
 match guard.as_ref().unwrap().operation_consume(r.payload).map_err(|e|storage_stage(e,false))?{
 crate::health_conversation_host::OperationStart::Replay(v)=>return Ok(v),
 crate::health_conversation_host::OperationStart::Send(plan)=>{
 let Ok(_serial)=MODEL_SERIAL.try_lock() else{return guard.as_ref().unwrap().operation_finish(&plan,Err(Error::new("model_busy")))};
 let refs=plan.preview["packet"]["snapshot"]["records"].as_array().unwrap().iter().filter_map(|r|r.get("engineRef").cloned()).collect::<Vec<_>>();
 let mut fence=match lifeos_source_engine::send_fence(&guard.as_ref().unwrap().fixture(),&refs){Ok(f)=>f,Err(_)=>return guard.as_ref().unwrap().operation_finish(&plan,Err(Error::new("source_context_stale")))};
 // D-0667: validate again after the fence and immediately before transport.
 if let Some(result)=guard.as_ref().unwrap().operation_preflight(&plan)?{return Ok(result)}
 let result=port.generate_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,&mut||{drop(fence.take());drop(guard.take());});drop(fence.take());drop(guard.take());
 return store.lock().map_err(|_|Error::new("response_storage_failed"))?.operation_finish(&plan,result).map_err(|e|storage_stage(e,true));
 }}
 }
 if crate::runtime_root::network_enabled(){return Err(Error::new("operation_rejected"));}
 if r.version!=5||r.operation!="confirm_send"{return Err(Error::new("operation_rejected"));}
 match guard.as_ref().unwrap().consume(r.payload).map_err(|e|storage_stage(e,false))?{Start::Replay(v)=>Ok(v),Start::Send(plan)=>{
  let Ok(_serial)=MODEL_SERIAL.try_lock() else{return guard.as_ref().unwrap().finish(&plan,Err(Error::new("model_busy")))};
  let refs=plan.preview["packet"]["snapshot"]["records"].as_array().unwrap().iter().filter(|r|plan.preview["inputRefs"].as_array().unwrap().iter().any(|rf|rf["id"]==r["id"])).filter_map(|r|r.get("engineRef").cloned()).collect::<Vec<_>>();
  let mut fence=match lifeos_source_engine::send_fence(&guard.as_ref().unwrap().fixture(),&refs){Ok(v)=>v,Err(_)=>{let result=guard.as_ref().unwrap().finish(&plan,Err(Error::new("source_context_stale")));return result;}};
  let result=port.generate_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,&mut||{drop(fence.take());drop(guard.take());});drop(fence.take());drop(guard.take());
  store.lock().map_err(|_|Error::new("response_storage_failed"))?.finish(&plan,result).map_err(|e|storage_stage(e,true))
 }}
}

fn storage_stage(e:Error,after_adapter:bool)->Error{if matches!(e.code.as_str(),"store_operation_failed"|"database_unavailable"|"store_busy"){Error::new(if after_adapter{"response_storage_failed"}else{"confirmation_storage_failed"})}else{e}}

fn offline_fixture_bytes(path:&std::path::Path)->Option<Vec<u8>>{
 use std::{io::Read,os::unix::fs::{OpenOptionsExt,MetadataExt}};
 if crate::runtime_root::network_enabled(){return None}
 let f=std::fs::OpenOptions::new().read(true).custom_flags(libc::O_NOFOLLOW|libc::O_CLOEXEC).open(path).ok()?;let m=f.metadata().ok()?;
 if !m.is_file()||m.nlink()!=1||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o600||m.len()>65536{return None}let mut b=vec![];f.take(65537).read_to_end(&mut b).ok()?;if b.len()>65536{return None}Some(b)
}

/// Called by the running native app, never by a read/projection IPC.
pub(crate) fn proactive_tick(store:&Arc<Mutex<Store>>,visible_unlocked:impl Fn()->bool,port:&mut dyn ModelPort)->R<Value>{
 let Ok(_serial)=MODEL_SERIAL.try_lock() else{return Ok(json!({"status":"busy"}))};
 let mut guard=Some(store.lock().map_err(|_|Error::new("store_busy"))?);
 if guard.as_ref().unwrap().proactive_policy_view()?["enabled"]!=true{return Ok(json!({"status":"disabled"}))}
 guard.as_ref().unwrap().proactive_sync_sources()?;
 guard.as_ref().unwrap().proactive_reconcile()?;
 if !visible_unlocked(){return Ok(json!({"status":"not_visible"}))}
 let plan=match guard.as_ref().unwrap().proactive_reserve_response(true)?{Some(p)=>Some(p),None=>guard.as_ref().unwrap().proactive_reserve(true)?};
 let Some(plan)=plan else{return Ok(json!({"status":"idle"}))};
 let expected_profile=guard.as_ref().unwrap().proactive_transport_profile(&plan);
 let fixture=guard.as_ref().unwrap().fixture();
 // Keychain IPC can stall independently of its authentication policy. Never
 // hold the repository or source fence while waiting, and never retry a timeout.
 drop(guard.take());
 let started=std::time::Instant::now();let mut usage=None;
 let (key,credential_diagnostic)=match expected_profile.as_ref(){Ok(_)=>proactive_credential_wait(move||crate::provider_store::proactive_credential(&fixture),std::time::Duration::from_secs(5)),Err(e)=>(Err(Error::new(&e.code)),crate::secure_credentials::ReadDiagnostic::new("configuration_binding",None))};
 guard=Some(store.lock().map_err(|_|Error::new("store_busy"))?);
 let mut held_fence=None;
 let transport=match (expected_profile,key){
  (Ok(profile),Ok(key))=>{
   let refs:Vec<Value>=plan["snapshot"].as_array().unwrap().iter().filter_map(|r|r.get("engineRef").filter(|v|!v.is_null()).cloned()).collect();
   match lifeos_source_engine::send_fence(&guard.as_ref().unwrap().fixture(),&refs){Ok(f)=>{held_fence=f;guard.as_ref().unwrap().proactive_transport(&plan,&profile,key)},Err(e)=>Err(Error::new(&e.code))}
  },(Err(e),_)|(_,Err(e))=>Err(e)
 };
 let result=match transport{
  Ok((body,key)) if visible_unlocked()=>port.generate_proactive(&body,&key,&mut||{drop(held_fence.take());drop(guard.take());}).map(|r|{usage=r.usage;r.text}),
  Ok(_)=>Err(Error::new("proactive_not_visible")),Err(e)=>Err(e)
 };drop(held_fence.take());drop(guard.take());
 let s=store.lock().map_err(|_|Error::new("store_busy"))?;
 let elapsed=started.elapsed().as_millis() as u64;s.proactive_usage(plan["id"].as_str().unwrap(),usage,elapsed,Some(credential_diagnostic))?;let result=if elapsed>60000{Err(Error::new("provider_timeout"))}else{result};
 if plan["purpose"]=="proactive_response.v1"{s.proactive_finish_response(&plan,result)}else{s.proactive_finish(&plan,result)}
}

static PROACTIVE_CREDENTIAL_ACTIVE:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);
type CredentialWait = (R<zeroize::Zeroizing<Vec<u8>>>,crate::secure_credentials::ReadDiagnostic);
fn credential_wait_failure(stage:&str)->CredentialWait {(Err(Error::new("credential_unavailable")),crate::secure_credentials::ReadDiagnostic::new(stage,None))}
pub(crate) fn proactive_credential_wait<F>(load:F,timeout:std::time::Duration)->CredentialWait where F:FnOnce()->R<zeroize::Zeroizing<Vec<u8>>>+Send+'static{
 use std::sync::atomic::Ordering;
 if PROACTIVE_CREDENTIAL_ACTIVE.compare_exchange(false,true,Ordering::AcqRel,Ordering::Acquire).is_err(){return credential_wait_failure("worker_busy")}
 struct Done;impl Drop for Done{fn drop(&mut self){PROACTIVE_CREDENTIAL_ACTIVE.store(false,Ordering::Release);}}
 let (tx,rx)=std::sync::mpsc::sync_channel(1);
 if std::thread::Builder::new().name("proactive-credential".into()).spawn(move||{
  let _done=Done;
  crate::secure_credentials::read_stage("configuration_binding",None);
  let result=load();
  // Capture on the worker. Parent TLS belongs to another operation/thread.
  if result.is_ok(){crate::secure_credentials::read_stage("complete",None);}
  let diagnostic=crate::secure_credentials::ReadDiagnostic::capture();
  // A dropped receiver drops both the result and its Zeroizing key; no late POST.
  drop(_done);
  let _=tx.send((result,diagnostic));
 }).is_err(){PROACTIVE_CREDENTIAL_ACTIVE.store(false,Ordering::Release);return credential_wait_failure("worker_unavailable")}
 match rx.recv_timeout(timeout){Ok(r)=>r,Err(std::sync::mpsc::RecvTimeoutError::Timeout)=>credential_wait_failure("worker_timeout"),Err(std::sync::mpsc::RecvTimeoutError::Disconnected)=>credential_wait_failure("worker_disconnected")}
}
#[cfg(test)]mod proactive_credential_wait_tests{
 use super::*;
 #[test]fn proactive_credential_timeout_is_bounded_and_no_second_worker_or_late_send(){let (release,wait)=std::sync::mpsc::channel();let (done,finished)=std::sync::mpsc::channel();let begin=std::time::Instant::now();let r=proactive_credential_wait(move||{wait.recv().unwrap();done.send(()).unwrap();Ok(zeroize::Zeroizing::new(b"fictional-only".to_vec()))},std::time::Duration::from_millis(10));assert_eq!(r.0.unwrap_err().code,"credential_unavailable");assert!(begin.elapsed()<std::time::Duration::from_secs(1));assert!(proactive_credential_wait(||panic!("second lookup forbidden"),std::time::Duration::from_millis(10)).0.is_err());release.send(()).unwrap();finished.recv_timeout(std::time::Duration::from_secs(1)).unwrap();for _ in 0..100{if !PROACTIVE_CREDENTIAL_ACTIVE.load(std::sync::atomic::Ordering::Acquire){break}std::thread::sleep(std::time::Duration::from_millis(1));}assert!(!PROACTIVE_CREDENTIAL_ACTIVE.load(std::sync::atomic::Ordering::Acquire));}
}

#[cfg(test)]mod diagnostic_worker_tests {
 use super::*;
 #[test]fn proactive_credential_worker_diagnostics_are_isolated_and_failure_modes_distinct(){
  use crate::secure_credentials::{read_stage,read_diagnostic};use std::time::Duration;
  let wait=|f:Box<dyn FnOnce()->R<zeroize::Zeroizing<Vec<u8>>>+Send>|proactive_credential_wait(f,Duration::from_secs(1));
  read_stage("default_keychain",Some(-999));
  for (stage,status) in [("single_item_read",-25308),("single_item_read",-25293),("default_keychain",-25294),("process_policy",-50)]{
   let (r,d)=wait(Box::new(move||{read_stage(stage,Some(status));Err(Error::new("credential_unavailable"))}));assert!(r.is_err());assert_eq!(d.value(),json!({"stage":stage,"osStatus":status}));assert_eq!(read_diagnostic(),("default_keychain",Some(-999)));
  }
  let (_,d)=wait(Box::new(||Err(Error::new("credential_unavailable"))));assert_eq!(d.value(),json!({"stage":"configuration_binding","osStatus":null}));
  let (r,d)=wait(Box::new(||{read_stage("single_item_read",Some(0));Ok(zeroize::Zeroizing::new(b"fictional-canary".to_vec()))}));drop(r);assert_eq!(d.value()["stage"],"complete");assert!(!d.value().to_string().contains("canary"));
  let (_,d)=wait(Box::new(||{panic!("synthetic disconnect")}));assert_eq!(d.value()["stage"],"worker_disconnected");
  let (release,rx)=std::sync::mpsc::channel();
  let (_,d)=proactive_credential_wait(move||{rx.recv().unwrap();read_stage("single_item_read",Some(-9999));Ok(zeroize::Zeroizing::new(b"late-canary".to_vec()))},Duration::from_millis(10));assert_eq!(d.value()["stage"],"worker_timeout");
  let (_,busy)=wait(Box::new(||panic!("concurrent lookup forbidden")));assert_eq!(busy.value()["stage"],"worker_busy");
  release.send(()).unwrap();for _ in 0..1000{if !PROACTIVE_CREDENTIAL_ACTIVE.load(std::sync::atomic::Ordering::Acquire){break}std::thread::sleep(Duration::from_millis(1));}
  let (_,fresh)=wait(Box::new(||Err(Error::new("credential_unavailable"))));assert_eq!(fresh.value()["stage"],"configuration_binding");assert_eq!(d.value()["stage"],"worker_timeout");
 }
}
