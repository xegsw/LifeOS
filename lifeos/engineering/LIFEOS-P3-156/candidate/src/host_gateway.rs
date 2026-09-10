use crate::{repository::Error,health_conversation_host::{Store,Start},model_port::{ModelPort,ModelResponse}};
use serde_json::{Value,json};use std::sync::{Arc,Mutex,OnceLock};
type R<T>=Result<T,Error>;
pub struct SyntheticControlledModel;
impl ModelPort for SyntheticControlledModel {
 fn generate(&mut self,body:&str,key:&[u8])->R<ModelResponse>{self.generate_with_receipt(body,key,&mut||{})}
 fn generate_with_receipt(&mut self,body:&str,_key:&[u8],received:&mut dyn FnMut())->R<ModelResponse>{
  if crate::runtime_root::is_real(){return Err(Error::new("real_capability_denied"));}let value:Value=serde_json::from_str(body).map_err(|_|Error::new("provider_protocol"))?;let user:Value=serde_json::from_str(value["messages"][1]["content"].as_str().unwrap_or("")).map_err(|_|Error::new("provider_protocol"))?;let question=user["question"].as_str().unwrap_or("");received();std::thread::sleep(std::time::Duration::from_millis(1200));
  for (marker,code) in [("[模拟超时]","provider_timeout"),("[模拟网络错误]","provider_network"),("[模拟认证错误]","provider_authentication"),("[模拟模型错误]","provider_model")]{if question.contains(marker){return Err(Error::new(code));}}
  static FAILED:OnceLock<Mutex<std::collections::HashSet<String>>>=OnceLock::new();if question.contains("[模拟失败一次]")&&FAILED.get_or_init(Default::default).lock().unwrap().insert(question.into()){return Err(Error::new("provider_unavailable"));}
  let text=if user["items"].as_array().is_none_or(|v|v.is_empty()){String::from("合成演练 · 本次没有披露健康依据。离线适配器不具备开放域推理能力。")}
  else{let items=user["items"].as_array().unwrap();format!("合成演练 · 受控发送测试\n本次仅使用你确认的 {} 条资料。\n{}\n这是验证披露与回答链路的离线示例，不代表真实 DeepSeek 回答。",items.len(),items.iter().map(|r|format!("{} [{}]",r["text"].as_str().unwrap_or(""),r["citationId"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"))};let text=if question.contains("工作")&&question.contains("建议"){format!("{text}\n建议：整理报告结论。") }else{text};Ok(ModelResponse{text,usage:None})
 }
}
pub fn dispatch(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8])->R<Value>{if crate::runtime_root::is_real(){dispatch_with_port(store,command,bytes,&mut crate::provider_transport::DeepSeekModel)}else{dispatch_with_port(store,command,bytes,&mut SyntheticControlledModel)}}
pub(crate) fn dispatch_with_port(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8],port:&mut dyn ModelPort)->R<Value>{
 if lifeos_source_engine::COMMANDS.contains(&command){
  if bytes.len()>4096{return Err(Error::new("source_request_limit"));}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("source_contract_rejected"))?;crate::strict_json::parse(raw)?;
  let s=store.lock().map_err(|_|Error::new("store_busy"))?;
  let result=lifeos_source_engine::dispatch(command,bytes,&s.fixture()).map_err(|e|Error::new(&e.code))?;
  if ["connect_source_directory","control_source_job","authorize_source_target"].contains(&command){s.invalidate_notes()?;}
  return Ok(result)
 }
 if command=="get_today"{return store.lock().map_err(|_|Error::new("store_busy"))?.health_view(bytes)}
 if bytes.len()>16384{return Err(Error::new("dto_rejected"));}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("dto_rejected"))?;let value=crate::strict_json::parse(raw)?;
 let mut guard=Some(store.lock().map_err(|_|Error::new("store_busy"))?);
 if command!="send_source_ai_request" {return guard.as_ref().unwrap().dispatch(command,bytes)}
 let r:crate::repository::Request=serde_json::from_value(value).map_err(|_|Error::new("dto_rejected"))?;if r.version!=5||r.operation!="confirm_send"{return Err(Error::new("operation_rejected"));}
 match guard.as_ref().unwrap().consume(r.payload).map_err(|e|storage_stage(e,false))?{Start::Replay(v)=>Ok(v),Start::Send(plan)=>{
  let refs=plan.preview["packet"]["snapshot"]["records"].as_array().unwrap().iter().filter(|r|plan.preview["inputRefs"].as_array().unwrap().iter().any(|rf|rf["id"]==r["id"])).filter_map(|r|r.get("engineRef").cloned()).collect::<Vec<_>>();
  let mut fence=match lifeos_source_engine::send_fence(&guard.as_ref().unwrap().fixture(),&refs){Ok(v)=>v,Err(_)=>{let result=guard.as_ref().unwrap().finish(&plan,Err(Error::new("source_context_stale")));return result;}};
  let result=port.generate_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,&mut||{drop(fence.take());drop(guard.take());});drop(fence.take());drop(guard.take());
  store.lock().map_err(|_|Error::new("response_storage_failed"))?.finish(&plan,result).map_err(|e|storage_stage(e,true))
 }}
}

fn storage_stage(e:Error,after_adapter:bool)->Error{if matches!(e.code.as_str(),"store_operation_failed"|"database_unavailable"|"store_busy"){Error::new(if after_adapter{"response_storage_failed"}else{"confirmation_storage_failed"})}else{e}}
