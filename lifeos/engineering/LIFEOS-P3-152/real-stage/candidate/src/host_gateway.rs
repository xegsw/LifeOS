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
  else{let items=user["items"].as_array().unwrap();format!("合成演练 · 受控发送测试\n本次仅使用你确认的 {} 条资料。\n{}\n这是验证披露与回答链路的离线示例，不代表真实 DeepSeek 回答。",items.len(),items.iter().map(|r|format!("{} [{}]",r["text"].as_str().unwrap_or(""),r["citationId"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"))};Ok(ModelResponse{text,usage:None})
 }
}
pub fn dispatch(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8])->R<Value>{if crate::runtime_root::is_real(){dispatch_with_port(store,command,bytes,&mut crate::provider_transport::DeepSeekModel)}else{dispatch_with_port(store,command,bytes,&mut SyntheticControlledModel)}}
pub(crate) fn dispatch_with_port(store:&Arc<Mutex<Store>>,command:&str,bytes:&[u8],port:&mut dyn ModelPort)->R<Value>{
 if bytes.len()>16384{return Err(Error::new("dto_rejected"));}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("dto_rejected"))?;let value=crate::strict_json::parse(raw)?;
 let mut guard=Some(store.lock().map_err(|_|Error::new("store_busy"))?);
 if command!="send_source_ai_request" {return guard.as_ref().unwrap().dispatch(command,bytes)}
 let r:crate::repository::Request=serde_json::from_value(value).map_err(|_|Error::new("dto_rejected"))?;if r.version!=5||r.operation!="confirm_send"{return Err(Error::new("operation_rejected"));}
 match guard.as_ref().unwrap().consume(r.payload)?{Start::Replay(v)=>Ok(v),Start::Send(plan)=>{
  let result=port.generate_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,&mut||drop(guard.take()));drop(guard.take());
  store.lock().map_err(|_|Error::new("store_busy"))?.finish(&plan,result)
 }}
}
