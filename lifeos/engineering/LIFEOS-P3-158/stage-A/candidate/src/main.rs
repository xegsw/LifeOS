#![cfg_attr(not(debug_assertions),windows_subsystem="windows")]
mod host_support;pub use host_support::{repository,conversation_store};
mod strict_json;
mod health_conversation_host;
use tauri::Manager;
use std::{sync::{Mutex,Arc},io::Write,os::fd::FromRawFd};
struct State(Arc<Mutex<health_conversation_host::Store>>);
async fn route(command:&'static str,body:tauri::ipc::InvokeBody,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{let tauri::ipc::InvokeBody::Raw(bytes)=body else{return Err(repository::Error::new("raw_required"));};tauri::async_runtime::spawn_blocking(move||{let s=app.state::<State>();crate::host_gateway::dispatch(&s.0,command,&bytes)}).await.map_err(|_|repository::Error::new("store_operation_failed"))?}
#[tauri::command]async fn capture_record(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("capture_record",request.body().clone(),app).await}
#[tauri::command]async fn get_context_recovery(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("get_context_recovery",request.body().clone(),app).await}
#[tauri::command]async fn resolve_request_context(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("resolve_request_context",request.body().clone(),app).await}
#[tauri::command]async fn decide_understanding_feedback(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("decide_understanding_feedback",request.body().clone(),app).await}
#[tauri::command]async fn save_ai_provider_settings(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("save_ai_provider_settings",request.body().clone(),app).await}
#[tauri::command]async fn send_source_ai_request(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("send_source_ai_request",request.body().clone(),app).await}
#[tauri::command]async fn get_ai_provider_settings(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("get_ai_provider_settings",request.body().clone(),app).await}
#[tauri::command]async fn get_today(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("get_today",request.body().clone(),app).await}
#[tauri::command]async fn connect_source_directory(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("connect_source_directory",request.body().clone(),app).await}
#[tauri::command]async fn control_source_job(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("control_source_job",request.body().clone(),app).await}
#[tauri::command]async fn get_source_status(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("get_source_status",request.body().clone(),app).await}
#[tauri::command]async fn authorize_source_target(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("authorize_source_target",request.body().clone(),app).await}
#[tauri::command]async fn get_source_evidence(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("get_source_evidence",request.body().clone(),app).await}
#[tauri::command]async fn import_apple_health_file(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,repository::Error>{route("import_apple_health_file",request.body().clone(),app).await}
fn main(){std::panic::set_hook(Box::new(|_|{}));unsafe{libc::umask(0o077);let lim=libc::rlimit{rlim_cur:0,rlim_max:0};libc::setrlimit(libc::RLIMIT_CORE,&lim);}let out=unsafe{libc::fcntl(1,libc::F_DUPFD_CLOEXEC,3)};unsafe{let f=libc::open(c"/dev/null".as_ptr(),libc::O_RDWR);if f>=0{libc::dup2(f,0);libc::dup2(f,1);libc::dup2(f,2);if f>2{libc::close(f);}}}
 let store=match health_conversation_host::Store::open_fixed(){Ok(s)=>s,Err(e)=>{if out>=0{let mut f=unsafe{std::fs::File::from_raw_fd(out)};let _=writeln!(f,"{{\"status\":\"failed\",\"code\":\"{}\"}}",e.code);}return;}};
 let _=tauri::Builder::default().manage(State(Arc::new(Mutex::new(store)))).invoke_handler(tauri::generate_handler![connect_source_directory,control_source_job,get_source_status,authorize_source_target,get_source_evidence,import_apple_health_file,get_today,capture_record,get_context_recovery,resolve_request_context,decide_understanding_feedback,save_ai_provider_settings,send_source_ai_request,get_ai_provider_settings]).setup(move|app|{tauri::WebviewWindowBuilder::new(app,"main",tauri::WebviewUrl::App("index.html".into())).title(if crate::runtime_root::is_real(){"LifeOS P3-158 - Controlled Conversation"}else{"LifeOS P3-158 - Synthetic Conversation"}).inner_size(1280.0,949.0).min_inner_size(560.0,640.0).incognito(true).build()?;if out>=0{let mut f=unsafe{std::fs::File::from_raw_fd(out)};let _=writeln!(f,"{{\"status\":\"{}\"}}",if crate::runtime_root::is_real(){"controlled_conversation_started"}else{"synthetic_conversation_started"});}Ok(())}).run(tauri::generate_context!());}

mod conversation_contract;
mod runtime_root;
mod secure_credentials;
mod provider_store;
mod wire_encoding;
mod provider_transport;
mod model_port;

mod host_gateway;

mod health_reader;
mod health_source;

#[cfg(test)]
mod source_restoration_tests;

#[cfg(all(test,feature="synthetic-driver"))]mod integration_guards{
 #[test]fn source_existing_schema_rejects_missing_table_without_migration(){assert!(lifeos_source_engine::synthetic_existing_schema_check().unwrap());}
}
#[cfg(all(test,feature="synthetic-driver"))]mod update_contract_tests{
 #[test]fn source_update_unchanged_metadata_changed_missing_pause_restart_idempotency_and_revoke(){lifeos_source_engine::synthetic_update_lifecycle().unwrap();}
 #[test]fn import_status_missing_schema_is_not_migrated(){lifeos_source_engine::synthetic_status_schema_check().unwrap();}
}

#[cfg(all(test,feature="synthetic-driver"))]
#[test]fn source_restart_status_and_late_worker_error_are_owned(){lifeos_source_engine::synthetic_late_error_check().unwrap();}

#[cfg(all(test,feature="synthetic-driver"))]
#[test]fn failed_import_start_never_publishes_running(){lifeos_source_engine::synthetic_start_persistence_check().unwrap();}
