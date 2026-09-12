//! Fixed one-shot B Host diagnostic mode; no UI scheduler or model gateway starts.
use serde_json::{json,Value};
use std::{sync::{Arc,atomic::{AtomicBool,Ordering}},time::Duration};
fn wait_once(f:impl FnOnce()->Value+Send+'static,cancel:Arc<AtomicBool>,timeout:Duration)->Value{
 let (tx,rx)=std::sync::mpsc::sync_channel(1);
 let worker_cancel=cancel.clone();
 let worker=std::thread::Builder::new().name("single-item-metadata".into()).spawn(move||{let v=f();if !worker_cancel.load(Ordering::Acquire){let _=tx.send(v);}});
 if worker.is_err(){return json!({"stage":"worker_unavailable"})}
 match rx.recv_timeout(timeout){Ok(v)=>v,Err(_)=>{cancel.store(true,Ordering::Release);json!({"stage":"worker_timeout"})}}
}
pub(crate) fn run()->Value{
 if !crate::runtime_root::is_online(){return json!({"stage":"mode_rejected"})}
 let Ok(root)=crate::runtime_root::verify()else{return json!({"stage":"root_rejected"})};
 if !preflight(&root.join("conversation.sqlite")){return json!({"stage":"history_changed"})}
 // Durable single-use claim before any real DB/keychain operation. No retries.
 use std::os::unix::fs::OpenOptionsExt;
 if std::fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(root.join(".metadata-once-d912f5.claim")).is_err(){return json!({"stage":"already_consumed"})}
 wait_once(||match crate::provider_store::inspect_selected_metadata(){Ok(v)=>v,Err(e)=>configuration_error(&e.code)},Arc::new(AtomicBool::new(false)),Duration::from_secs(5))
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn metadata_timeout_and_cancel_discard_late_results_without_second_worker(){let count=Arc::new(std::sync::atomic::AtomicUsize::new(0));let n=count.clone();let r=wait_once(move||{n.fetch_add(1,Ordering::SeqCst);std::thread::sleep(Duration::from_millis(30));json!({"stage":"complete"})},Arc::new(AtomicBool::new(false)),Duration::from_millis(1));assert_eq!(r["stage"],"worker_timeout");std::thread::sleep(Duration::from_millis(50));assert_eq!(count.load(Ordering::SeqCst),1);let r=wait_once(||json!({"stage":"complete"}),Arc::new(AtomicBool::new(true)),Duration::from_millis(10));assert_eq!(r["stage"],"worker_timeout");}
 #[test]fn metadata_offline_mode_cannot_touch_real_configuration(){assert_eq!(run()["stage"],"mode_rejected");}
}

fn preflight(path:&std::path::Path)->bool{
 let Ok(c)=rusqlite::Connection::open_with_flags(path,rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY|rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW)else{return false};
 let result:rusqlite::Result<(i64,i64,i64,i64,i64)>=c.query_row("SELECT (SELECT json_extract(body,'$.analysis') FROM sources WHERE id='proactive:budget:production'),(SELECT json_extract(body,'$.response') FROM sources WHERE id='proactive:budget:production'),(SELECT json_extract(body,'$.generation') FROM sources WHERE id='proactive:policy'),(SELECT count(*) FROM sources WHERE id='proactive:budget:B'),(SELECT count(*) FROM sources r JOIN packets p ON p.id=json_extract(r.body,'$.packetId') WHERE json_extract(r.body,'$.kind')='proactive_request' AND json_extract(r.body,'$.grantGeneration')=5 AND json_extract(p.body,'$.payload.outcome.errorCode')='credential_unavailable')",[],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?)));
 matches!(result,Ok((5,0,5,0,n)) if n>0)
}

fn configuration_error(code:&str)->Value{
 let stage=match code{"metadata_query_failed"=>"query_failed","metadata_no_profile"=>"no_profile","metadata_invalid_revision"=>"invalid_revision","metadata_effective_binding"=>"effective_binding","metadata_multiple_profiles"=>"multiple_profiles","metadata_version_rejected"=>"version_rejected","metadata_reference_rejected"=>"reference_rejected","metadata_configuration_rows"=>"configuration_rows","metadata_provider_open"=>"provider_open","metadata_configuration_open"=>"configuration_open",_=>"configuration_binding"};json!({"stage":stage,"osStatus":null})
}

#[cfg(test)]#[test]fn metadata_configuration_errors_are_fixed_without_backend_details(){let v=configuration_error("secret-path-reference-canary");assert_eq!(v,json!({"stage":"configuration_binding","osStatus":null}));for code in ["metadata_query_failed","metadata_no_profile","metadata_invalid_revision","metadata_effective_binding","metadata_multiple_profiles","metadata_version_rejected","metadata_reference_rejected"]{assert_ne!(configuration_error(code)["stage"],"configuration_binding");}}
