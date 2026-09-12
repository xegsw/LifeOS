//! User-only, read-only credential check. IPC can open a native menu, but only
//! its native selection can consume the private, short-lived check identity.
use crate::{health_conversation_host::Store,repository::Error};
use serde_json::{json,Value};
use std::{sync::{Arc,Mutex,OnceLock,atomic::{AtomicBool,Ordering}},time::{Duration,Instant}};
use tauri::Manager;
type R<T>=Result<T,Error>;
#[derive(Default)]
struct Check { token:String, binding:Value, started:Option<Instant>, state:&'static str, result:Option<Value> }
impl Check {
 fn arm(&mut self,binding:Value)->R<String>{
  if matches!(self.state,"awaiting_user"|"checking"){return Err(Error::new("credential_check_busy"))}
  self.token=crate::conversation_store::uid("credential-check");self.binding=binding;self.started=Some(Instant::now());self.state="awaiting_user";self.result=None;Ok(self.token.clone())
 }
 fn expired(&self)->bool{self.started.is_some_and(|t|t.elapsed()>Duration::from_secs(60))}
 fn consume(&mut self,token:&str,foreground:bool,binding:&Value)->bool{
  if self.state!="awaiting_user"||self.token!=token{return false}
  if self.expired()||!foreground||self.binding!=*binding{self.cancel("cancelled");return false}
  self.state="checking";self.started=Some(Instant::now());true
 }
 fn cancel(&mut self,state:&'static str){self.token.clear();self.state=state;self.result=None;}
 fn finish(&mut self,token:&str,binding:&Value,result:Value){
  if self.state!="checking"||self.token!=token{return}
  if self.expired(){self.cancel("timeout");return}
  if self.binding!=*binding{self.cancel("binding_changed");return}
  self.state="finished";self.token.clear();self.result=Some(result);
 }
 fn view(&mut self)->Value{if matches!(self.state,"awaiting_user"|"checking")&&self.expired(){self.cancel("timeout")};json!({"status":if self.state.is_empty(){"idle"}else{self.state},"diagnostic":self.result,"backgroundRestored":false,"readAttempts":READ_COUNT.load(Ordering::Acquire)})}
}
static CHECK:OnceLock<Mutex<Check>>=OnceLock::new();
static WORKER:AtomicBool=AtomicBool::new(false);
static READ_COUNT:std::sync::atomic::AtomicU64=std::sync::atomic::AtomicU64::new(0);
static MENU:OnceLock<Mutex<Option<tauri::menu::Menu<tauri::Wry>>>>=OnceLock::new();
fn check()->std::sync::MutexGuard<'static,Check>{CHECK.get_or_init(Default::default).lock().unwrap_or_else(|e|e.into_inner())}
pub(crate) fn binding(store:&Arc<Mutex<Store>>)->R<Value>{
 let s=store.lock().map_err(|_|Error::new("store_busy"))?;
 let policy=s.proactive_policy_view()?;
 if policy["enabled"]!=true{return Err(Error::new("credential_check_not_enabled"))}
 let p=s.provider_view()?;
 if p["enabled"]!=true||(crate::runtime_root::network_enabled()&&p["modelId"]!="deepseek-v4-pro")||p["credentialState"]!="stored"{return Err(Error::new("credential_check_configuration_binding"))}
 let raw=crate::provider_store::settings(&s.fixture())?;
 Ok(json!({"profile":p,"rawProfile":raw,"policy":policy}))
}
pub(crate) fn is_operation(v:&Value)->bool{v["version"]=="proactive-v1"&&matches!(v["operation"].as_str(),Some("request_credential_check"|"credential_check_status"|"cancel_credential_check"))}
fn validate<'a>(command:&str,v:&'a Value)->R<&'a str>{
 let Some(o)=v.as_object()else{return Err(Error::new("dto_rejected"))};
 let op=v["operation"].as_str().unwrap_or("");
 if o.len()!=3||v["version"]!="proactive-v1"||v["payload"]!=json!({})||!matches!((command,op),("save_ai_provider_settings","request_credential_check"|"cancel_credential_check")|("get_context_recovery","credential_check_status")){return Err(Error::new("dto_rejected"))}Ok(op)
}
pub(crate) fn dispatch(app:&tauri::AppHandle,command:&str,v:Value)->R<Value>{
 let op=validate(command,&v)?;
 let result=match op{
  "credential_check_status"=>check().view(),
  "cancel_credential_check"=>{check().cancel("cancelled");check().view()},
  "request_credential_check"=>{
   if !crate::proactive_runtime::foreground(app){return Err(Error::new("credential_check_not_visible"))}
   if WORKER.load(Ordering::Acquire){return Err(Error::new("credential_check_busy"))}
   let b=binding(&app.state::<crate::State>().0)?;
   let token=check().arm(b)?;
   let menu_result=(||{
    let item=tauri::menu::MenuItem::with_id(app,token,"检查一次（只读，不发送模型请求）",true,None::<&str>)?;
    let menu=tauri::menu::Menu::with_items(app,&[&item])?;
    let window=app.get_webview_window("main").ok_or(tauri::Error::WindowNotFound)?;
    *MENU.get_or_init(Default::default).lock().unwrap()=Some(menu.clone());
    window.popup_menu(&menu)
   })();
   if menu_result.is_err(){check().cancel("cancelled");return Err(Error::new("credential_check_native_unavailable"))}
   check().view()
  },_=>return Err(Error::new("operation_rejected"))
 };Ok(json!({"version":"proactive-v1","operation":op,"result":result}))
}
/// Called exclusively by Tauri's native menu event, never the IPC dispatcher.
pub(crate) fn native_select(app:&tauri::AppHandle,id:&str){
 if !id.starts_with("credential-check-"){return}
 let visible=crate::proactive_runtime::foreground(app);
 {let c=check();if c.token!=id||c.state!="awaiting_user"{return}}
 let store=Arc::clone(&app.state::<crate::State>().0);
 if WORKER.compare_exchange(false,true,Ordering::AcqRel,Ordering::Acquire).is_err(){check().cancel("busy");return}
 let id=id.to_string();
 if std::thread::Builder::new().name("user-credential-check".into()).spawn(move||{
  struct Done;impl Drop for Done{fn drop(&mut self){WORKER.store(false,Ordering::Release);}}
  let _done=Done;
  // Never wait for Store on the native event thread: the scheduler can be
  // waiting for a native foreground query while holding that repository lock.
  let Ok(b)=binding(&store)else{check().cancel("binding_changed");return};
  if !check().consume(&id,visible,&b){return}
  {let c=check();if c.token!=id||c.state!="checking"||c.expired(){return}}
  let fixture=match store.lock(){Ok(s)=>s.fixture(),Err(_)=>{check().cancel("cancelled");return}};
  // No Store or business lock during OS interaction; key is dropped here and
  // is never transferred to the UI, scheduler, model, or a later request.
  crate::secure_credentials::read_stage("configuration_binding",None);
  READ_COUNT.fetch_add(1,Ordering::AcqRel);
  let result=read_once(||crate::provider_store::check_selected_credential(&fixture,&b["rawProfile"]));
  let latest=binding(&store).unwrap_or(Value::Null);
  check().finish(&id,&latest,result);
 }).is_err(){WORKER.store(false,Ordering::Release);check().cancel("worker_unavailable");}
}
fn safe_error(code:&str)->&str{match code{"credential_missing"|"credential_reference_rejected"|"credential_authentication_failed"|"credential_interaction_required"=>code,_=>"credential_unavailable"}}
fn read_once(load:impl FnOnce()->R<zeroize::Zeroizing<Vec<u8>>>)->Value{
 match load(){Ok(key)=>{drop(key);json!({"ok":true,"stage":"complete","osStatus":null,"errorCode":null})},Err(e)=>{let (stage,status)=crate::secure_credentials::read_diagnostic();json!({"ok":false,"stage":stage,"osStatus":status,"errorCode":safe_error(&e.code)})}}
}
pub(crate) fn window_closed(){check().cancel("cancelled");}

#[cfg(test)]mod tests{
 use super::*;
 #[test]fn credential_check_native_grant_is_single_use_and_cannot_be_forged(){let mut c=Check::default();let b=json!({"profile":1,"grant":2});assert!(!c.consume("forged",true,&b));let t=c.arm(b.clone()).unwrap();assert!(!c.consume("forged",true,&b));assert!(c.consume(&t,true,&b));assert!(!c.consume(&t,true,&b));assert!(c.arm(b).is_err());}
 #[test]fn credential_check_cancel_timeout_and_changed_binding_discard_late_result(){for mode in 0..3{let mut c=Check::default();let b=json!({"profile":1});let t=c.arm(b.clone()).unwrap();assert!(c.consume(&t,true,&b));if mode==0{c.cancel("cancelled")}if mode==1{c.started=Some(Instant::now()-Duration::from_secs(61))}let latest=if mode==2{json!({"profile":2})}else{b};c.finish(&t,&latest,json!({"ok":true}));assert!(c.view()["diagnostic"].is_null());assert_eq!(c.view()["backgroundRestored"],false);}}
 #[test]fn credential_check_background_and_grant_change_reject_before_read(){for (visible,b) in [(false,json!(1)),(true,json!(2))]{let mut c=Check::default();let t=c.arm(json!(1)).unwrap();assert!(!c.consume(&t,visible,&b));}}
 #[test]fn credential_check_ipc_cannot_supply_authorization_key_reference_or_start(){for p in [json!({"authorized":true}),json!({"reference":"x"}),json!({"profile":1})]{assert!(validate("save_ai_provider_settings",&json!({"version":"proactive-v1","operation":"request_credential_check","payload":p})).is_err());}assert!(validate("save_ai_provider_settings",&json!({"version":"proactive-v1","operation":"start_credential_check","payload":{}})).is_err());}
 #[test]fn credential_check_status_is_inert_and_success_does_not_resume_background(){let mut c=Check::default();for _ in 0..5{assert_eq!(c.view()["status"],"idle");}let b=json!(1);let t=c.arm(b.clone()).unwrap();assert!(c.consume(&t,true,&b));c.finish(&t,&b,json!({"ok":true,"stage":"complete"}));assert_eq!(c.view()["diagnostic"]["ok"],true);assert_eq!(c.view()["backgroundRestored"],false);assert!(!c.consume(&t,true,&b));}
 #[test]fn credential_check_returns_only_fixed_diagnostic_and_never_key_or_error_description(){let mut calls=0;let r=read_once(||{calls+=1;Ok(zeroize::Zeroizing::new(b"fictional-secret-canary".to_vec()))});assert_eq!(calls,1);assert!(!r.to_string().contains("canary"));crate::secure_credentials::read_stage("default_keychain",Some(-25294));let r=read_once(||Err(Error::new("untrusted-account-path-canary")));assert_eq!(r["stage"],"default_keychain");assert_eq!(r["osStatus"],-25294);assert!(!r.to_string().contains("canary"));}
}
