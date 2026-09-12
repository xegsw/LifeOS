use super::*;
const SLOT:&str="_settings_catalog";
const CLOUD:[&str;8]=["openai","anthropic","google_gemini","deepseek","kimi","openrouter","cloud_openai_compatible","cloud_custom"];
const LOCAL:[&str;4]=["ollama","lm_studio","local_openai_compatible","local_custom"];
#[derive(Deserialize,Serialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Primary{mode:String,provider_id:String,model_label:String,endpoint_url:Option<String>,local_runtime:Option<String>}
#[derive(Deserialize,Serialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Policy{prefer_local:bool,allow_cloud_supplement:bool,allow_automatic_failover:bool,prefer_fast_response:bool}
#[derive(Deserialize,Serialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Fallback{configured:bool,provider_id:Option<String>}
#[derive(Deserialize,Serialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Advanced{expanded:bool,capability_overrides:std::collections::BTreeMap<String,String>,temperature:u16,max_output_tokens:u16,timeout_seconds:u16,context_window:u16}
#[derive(Deserialize,Serialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Settings{version:u8,primary:Primary,routing_policy:Policy,fallback:Fallback,advanced:Advanced}
#[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]struct Save{request_id:String,expected_revision:u64,settings:Settings}
fn validate(s:&Settings)->R<()>{let p=&s.primary;let providers=if p.mode=="cloud"{&CLOUD[..]}else if p.mode=="local"{&LOCAL[..]}else{return Err(error("catalog_rejected"))};if s.version!=1||!providers.contains(&p.provider_id.as_str())||p.model_label.trim().is_empty()||p.model_label.len()>96{return Err(error("catalog_rejected"))}
 if p.mode=="cloud"{let expected=if p.provider_id=="deepseek"{"https://api.deepseek.com".into()}else{format!("offline://catalog/cloud/{}",p.provider_id)};if p.endpoint_url.as_deref()!=Some(&expected)||p.local_runtime.is_some(){return Err(error("catalog_rejected"))}}else if p.endpoint_url.is_some()||p.local_runtime.as_deref()!=Some("synthetic-local-runtime-v1"){return Err(error("catalog_rejected"))}
 if s.fallback.configured!=s.fallback.provider_id.is_some()||s.fallback.provider_id.as_ref().is_some_and(|id|id==&p.provider_id||!CLOUD.contains(&id.as_str())&&!LOCAL.contains(&id.as_str())){return Err(error("catalog_rejected"))}
 let a=&s.advanced;if a.temperature>200||!(128..=8192).contains(&a.max_output_tokens)||!(5..=120).contains(&a.timeout_seconds)||!(4..=128).contains(&a.context_window)||a.capability_overrides.len()!=6||["text","vision","speech_input","speech_output","tool_use","long_context"].iter().any(|k|a.capability_overrides.get(*k).map(String::as_str)!=Some("auto")){return Err(error("catalog_rejected"))}Ok(())}
impl Store{
 pub(crate) fn catalog(&self)->R<Value>{Ok(get(&self.c,"sources",SLOT)?.unwrap_or(json!({"revision":0,"settings":null})))}
 pub(crate) fn save_catalog(&self,p:Value)->R<Value>{let d:Save=decode(p.clone())?;validate(&d.settings)?;self.tx(&d.request_id,"save_local_catalog",&p,|c|{let current=get(c,"sources",SLOT)?.unwrap_or(json!({"revision":0}));if current["revision"]!=d.expected_revision{return Err(error("catalog_revision_conflict"))}let v=json!({"id":SLOT,"kind":"private_settings_metadata","authorized":false,"revision":d.expected_revision+1,"settings":d.settings});put(c,"sources",SLOT,&v)?;Ok(v)})}
 pub(crate) fn catalog_send_revision(&self,model:&str)->R<u64>{let c=self.catalog()?;if !c["settings"].is_null(){let p=&c["settings"]["primary"];if p["mode"]!="cloud"||p["providerId"]!="deepseek"{return Err(error("provider_not_enabled"))}if p["modelLabel"]!=model{return Err(error("catalog_model_conflict"))}}Ok(c["revision"].as_u64().unwrap_or(0))}
}
